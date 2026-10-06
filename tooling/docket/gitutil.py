from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path


class GitError(RuntimeError):
    pass


DEFAULT_FINGERPRINT_EXCLUDES = (".docket/",)


def run_git(repo: Path, *args: str, check: bool = True) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
    )
    if check and proc.returncode != 0:
        msg = (proc.stderr or proc.stdout or "git failed").strip()
        raise GitError(msg)
    return proc.stdout


def rev_parse(repo: Path, ref: str = "HEAD") -> str:
    return run_git(repo, "rev-parse", ref).strip()


def is_git_repo(repo: Path) -> bool:
    try:
        run_git(repo, "rev-parse", "--is-inside-work-tree")
        return True
    except GitError:
        return False


def changed_paths_since(repo: Path, baseline: str) -> list[str]:
    """Paths changed from baseline to the current working tree, plus untracked.

    Includes adds, deletes, modifies, and both sides of renames.
    Baseline must be an explicit git ref/sha — never inferred silently.
    """
    rev_parse(repo, baseline)

    paths: set[str] = set()

    status = run_git(repo, "diff", "--name-status", "-M", baseline)
    for line in status.splitlines():
        if not line.strip():
            continue
        parts = line.split("\t")
        code = parts[0]
        if code.startswith("R") or code.startswith("C"):
            if len(parts) >= 3:
                paths.add(parts[1])
                paths.add(parts[2])
            elif len(parts) == 2:
                paths.add(parts[1])
        elif len(parts) >= 2:
            paths.add(parts[1])

    untracked = run_git(repo, "ls-files", "--others", "--exclude-standard")
    for line in untracked.splitlines():
        if line.strip():
            paths.add(line)

    return sorted(normalize_repo_path(p) for p in paths if p.strip())


def normalize_repo_path(path: str) -> str:
    p = path.strip().replace("\\", "/")
    while p.startswith("./"):
        p = p[2:]
    return p


def _excluded(path: str, exclude_prefixes: tuple[str, ...], exclude_paths: set[str]) -> bool:
    norm = normalize_repo_path(path)
    if norm in exclude_paths:
        return True
    for prefix in exclude_prefixes:
        p = normalize_repo_path(prefix)
        if not p.endswith("/"):
            p = p + "/"
        if norm == p.rstrip("/") or norm.startswith(p):
            return True
    return False


def tree_fingerprint(
    repo: Path,
    *,
    exclude_prefixes: tuple[str, ...] = DEFAULT_FINGERPRINT_EXCLUDES,
    exclude_paths: set[str] | None = None,
) -> str:
    """Fingerprint HEAD + dirty worktree so implementation edits invalidate attestation.

    A commit SHA alone is insufficient when Docket operates on an uncommitted
    worktree. Excludes `.docket/` (verify logs/attestations) and optional paths
    such as the Ticket file, so filling Evidence does not false-stale the run.
    """
    exclude_paths = {normalize_repo_path(p) for p in (exclude_paths or set())}
    head = rev_parse(repo, "HEAD")
    porcelain = run_git(repo, "status", "--porcelain=v1", "-uall")
    # Diff vs HEAD, then drop excluded paths from the textual mix by filtering
    # name-only and hashing file contents for included paths only.
    h = hashlib.sha256()
    h.update(b"head:")
    h.update(head.encode())
    h.update(b"\nstatus:")
    for line in porcelain.splitlines():
        path = _porcelain_path(line)
        if path and _excluded(path, exclude_prefixes, exclude_paths):
            continue
        h.update(line.encode())
        h.update(b"\n")
    h.update(b"\ntracked-diff:")
    name_only = run_git(repo, "diff", "--name-only", "HEAD")
    for path in name_only.splitlines():
        if not path or _excluded(path, exclude_prefixes, exclude_paths):
            continue
        h.update(path.encode())
        h.update(b"\n")
        h.update(run_git(repo, "diff", "HEAD", "--", path).encode())
    h.update(b"\nuntracked:")
    for line in porcelain.splitlines():
        if not line.startswith("?? "):
            continue
        rel = line[3:]
        if _excluded(rel, exclude_prefixes, exclude_paths):
            continue
        fp = repo / rel
        h.update(rel.encode())
        h.update(b"\0")
        if fp.is_file():
            h.update(_file_digest(fp))
        h.update(b"\n")
    return h.hexdigest()


def _porcelain_path(line: str) -> str | None:
    if len(line) < 4:
        return None
    # XY PATH or XY ORIG -> PATH
    body = line[3:]
    if " -> " in body:
        body = body.split(" -> ", 1)[1]
    return body.strip()


def _file_digest(path: Path) -> bytes:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            chunk = f.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.digest()
