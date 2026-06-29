#!/usr/bin/env python3
# designer: When you ask for git freshness status, I compare local branches
#   against their upstreams for the relevant repositories and report ahead/
#   behind counts without pulling changes. I am advisory-only and best-effort.
"""check_git_freshness.py -- Best-effort git upstream freshness report.

Invocation: skill-invoked, user-cli
Lifecycle: active

Usage:
    python .claude/skills/critique/check_git_freshness.py
    python .claude/skills/critique/check_git_freshness.py --json
    python .claude/skills/critique/check_git_freshness.py --repos C:/repo1,C:/repo2

Behavior:
- Resolves repos from harness root + CODEBASE_DIR in conventions (when available)
- Supports explicit repo override via --repos
- Compares HEAD with @{u} and reports ahead/behind counts
- Never performs git pull
- Never fails the caller: exits 0 in all cases
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

# Keep script robust when imported/executed in unusual contexts.
try:
    import project_config as _project_config
except ImportError:
    _project_config = None

DEFAULT_TIMEOUT_SECONDS = 5.0
PRIV_MARKERS = (
    "seja-public",
    "tools/sync_to_public.py",
    ".claude/skills/scripts/priv",
)


def _stderr(msg: str) -> None:
    print(msg, file=sys.stderr)


def _normalize_repo_path(path_text: str) -> Path:
    p = Path(path_text)
    if not p.is_absolute():
        p = (Path.cwd() / p).resolve()
    return p.resolve()


def _dedupe_paths(paths: list[Path]) -> list[Path]:
    seen: set[str] = set()
    unique: list[Path] = []
    for p in paths:
        key = str(p)
        if key in seen:
            continue
        seen.add(key)
        unique.append(p)
    return unique


def _has_priv_markers(repo_root: Path) -> bool:
    return any((repo_root / marker).exists() for marker in PRIV_MARKERS)


def _project_conventions_exists(repo_root: Path) -> bool:
    return (
        (repo_root / "product-design/conventions.md").is_file()
        or (repo_root / "_references/project/conventions.md").is_file()
    )


def _split_upstream(upstream: str) -> tuple[str, str]:
    if "/" not in upstream:
        return (upstream, "")
    remote, branch = upstream.split("/", 1)
    return (remote, branch)


def _run_git(repo: Path, args: list[str], timeout: float) -> tuple[str, str]:
    argv = ["git", "-C", str(repo)] + args
    try:
        cp = subprocess.run(
            argv,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return ("timeout", "")
    except FileNotFoundError:
        return ("missing", "")

    if cp.returncode != 0:
        return ("error", cp.stderr.strip() or cp.stdout.strip())
    return ("ok", cp.stdout.strip())


def _parse_count(raw: str) -> int | None:
    text = raw.strip()
    if text.isdigit():
        return int(text)
    return None


def _repo_result_template(repo: Path) -> dict[str, Any]:
    return {
        "repo": str(repo),
        "status": "ok",
        "branch": None,
        "upstream": None,
        "ahead": None,
        "behind": None,
        "fetch": "skipped",
        "warnings": [],
    }


def _inspect_repo(repo: Path, timeout: float) -> dict[str, Any]:
    result = _repo_result_template(repo)

    in_git_status, _ = _run_git(repo, ["rev-parse", "--is-inside-work-tree"], timeout)
    if in_git_status != "ok":
        result["status"] = "not-a-git-repo"
        return result

    branch_status, branch_out = _run_git(repo, ["rev-parse", "--abbrev-ref", "HEAD"], timeout)
    if branch_status != "ok":
        result["status"] = "failed"
        result["warnings"].append("could not resolve current branch")
        return result
    result["branch"] = branch_out

    upstream_status, upstream_out = _run_git(
        repo,
        ["rev-parse", "--abbrev-ref", "@{u}"],
        timeout,
    )
    if upstream_status != "ok":
        result["status"] = "no-upstream"
        return result
    result["upstream"] = upstream_out

    remote, remote_branch = _split_upstream(upstream_out)
    if remote and remote_branch:
        fetch_status, _ = _run_git(
            repo,
            ["fetch", "--quiet", remote, remote_branch],
            timeout,
        )
        result["fetch"] = "ok" if fetch_status == "ok" else "failed"
        if fetch_status not in ("ok", "error"):
            result["warnings"].append("fetch timed out or git unavailable")
    else:
        result["fetch"] = "skipped"

    behind_status, behind_out = _run_git(repo, ["rev-list", "--count", "HEAD..@{u}"], timeout)
    ahead_status, ahead_out = _run_git(repo, ["rev-list", "--count", "@{u}..HEAD"], timeout)

    if behind_status == "ok":
        behind_count = _parse_count(behind_out)
        result["behind"] = behind_count
        if behind_count is None:
            _stderr(
                f"warning: non-integer behind count for {repo}: {behind_out!r}"
            )
            result["warnings"].append("behind-count-unparseable")
    else:
        result["warnings"].append("behind-count-unavailable")

    if ahead_status == "ok":
        ahead_count = _parse_count(ahead_out)
        result["ahead"] = ahead_count
        if ahead_count is None:
            _stderr(
                f"warning: non-integer ahead count for {repo}: {ahead_out!r}"
            )
            result["warnings"].append("ahead-count-unparseable")
    else:
        result["warnings"].append("ahead-count-unavailable")

    return result


def _resolve_repositories(repos_override: str | None) -> tuple[list[Path], str | None]:
    if repos_override:
        paths = [
            _normalize_repo_path(part.strip())
            for part in repos_override.split(",")
            if part.strip()
        ]
        return (_dedupe_paths(paths), None)

    if _project_config is None:
        return ([], "SKIP: project_config unavailable; use --repos to provide targets")

    repo_root = Path(_project_config.REPO_ROOT).resolve()

    if _has_priv_markers(repo_root):
        return (
            [],
            "SKIP: harness-dev repo (seja-priv markers present); freshness-check does not apply",
        )

    if not _project_conventions_exists(repo_root):
        return (
            [],
            "INFO: product-design/conventions.md not found; freshness-check skipped",
        )

    paths = [repo_root]
    codebase_dir = _project_config.get("CODEBASE_DIR")
    if codebase_dir:
        codebase_path = Path(codebase_dir)
        if codebase_path.is_absolute():
            resolved = codebase_path.resolve()
            if resolved != repo_root:
                paths.append(resolved)

    return (_dedupe_paths(paths), None)


def _summary_line(results: list[dict[str, Any]], timeout: float) -> str:
    behind_repos = 0
    for item in results:
        behind = item.get("behind")
        if isinstance(behind, int) and behind > 0:
            behind_repos += 1

    suffix = ""
    if abs(timeout - DEFAULT_TIMEOUT_SECONDS) > 1e-9:
        suffix = f" (timeout={timeout}s)"

    return (
        "Summary: "
        f"{behind_repos} repo(s) behind upstream; run `git pull --ff-only` "
        f"where appropriate.{suffix}"
    )


def _render_text(results: list[dict[str, Any]], timeout: float) -> str:
    lines: list[str] = []
    for item in results:
        lines.append(f"Repo: {item['repo']}")
        status = item.get("status")
        if status == "ok":
            ahead = item["ahead"] if item["ahead"] is not None else "unknown"
            behind = item["behind"] if item["behind"] is not None else "unknown"
            lines.append(f"  branch: {item['branch']}")
            lines.append(f"  upstream: {item['upstream']}")
            lines.append(
                f"  ahead: {ahead} | behind: {behind} | fetch: {item['fetch']}"
            )
        elif status == "no-upstream":
            lines.append("  status: no-upstream (skipped)")
        elif status == "not-a-git-repo":
            lines.append("  status: not-a-git-repo (skipped)")
        else:
            lines.append(f"  status: {status} (skipped)")
        lines.append("")

    lines.append(_summary_line(results, timeout))
    return "\n".join(lines)


def build_report(repos_override: str | None, timeout: float) -> dict[str, Any]:
    repos, early_message = _resolve_repositories(repos_override)
    if early_message is not None:
        return {
            "status": "skipped",
            "message": early_message,
            "timeout_seconds": timeout,
            "repos": [],
            "behind_repos": 0,
            "summary": "Summary: 0 repo(s) behind upstream; run `git pull --ff-only` where appropriate.",
        }

    results = [_inspect_repo(repo, timeout) for repo in repos]
    behind_repos = sum(
        1
        for item in results
        if isinstance(item.get("behind"), int) and int(item["behind"]) > 0
    )
    return {
        "status": "ok",
        "message": None,
        "timeout_seconds": timeout,
        "repos": results,
        "behind_repos": behind_repos,
        "summary": _summary_line(results, timeout),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Check git upstream freshness")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit machine-readable JSON output",
    )
    parser.add_argument(
        "--repos",
        default=None,
        help="Comma-separated repo paths to check (overrides auto-detection)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT_SECONDS,
        help=(
            "Per-git-call timeout in seconds. Increase on slow VPN/proxy links; "
            "values above 30 are not recommended."
        ),
    )

    args = parser.parse_args(argv)
    timeout = args.timeout if args.timeout > 0 else DEFAULT_TIMEOUT_SECONDS

    report = build_report(args.repos, timeout)

    if report["status"] == "skipped":
        print(report["message"])
        return 0

    if args.json:
        print(json.dumps(report, sort_keys=True))
    else:
        print(_render_text(report["repos"], timeout))
    return 0


if __name__ == "__main__":
    sys.exit(main())
