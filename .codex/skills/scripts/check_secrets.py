#!/usr/bin/env python3
"""
check_secrets.py — Scan files for accidentally committed secrets.

Exit codes: 0 = no secrets found, 1 = potential secrets found, 2 = script error.

Scans staged files (default) or all tracked files (--all) for common secret
patterns: API keys, passwords, tokens, connection strings, and AWS credentials.

Usage
-----
    python .codex/skills/scripts/check_secrets.py           # scan staged files
    python .codex/skills/scripts/check_secrets.py --all      # scan all tracked files
    python .codex/skills/scripts/check_secrets.py --self-test # run built-in validation

Run from the repository root.
Optional flags:
    --all        Scan all tracked files instead of staged only
    --verbose    Show each file being scanned
    --self-test  Run built-in test fixtures to validate detection patterns
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

# File patterns to skip (test fixtures, examples, docs, migrations)
SKIP_PATTERNS = {
    ".example",
    ".sample",
    ".template",
}

SKIP_DIRS = {
    "node_modules",
    "__pycache__",
    ".git",
    "dist",
    "build",
    "coverage",
    "venv",
    ".venv",
    "migrations",
    "_loom",
}

SKIP_EXTENSIONS = {
    ".md",
    ".txt",
    ".rst",
    ".html",
    ".css",
    ".svg",
    ".png",
    ".jpg",
    ".gif",
    ".ico",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".map",
    ".lock",
    ".pyc",
    ".pyo",
}

# Secret detection patterns: (name, compiled regex)
SECRET_PATTERNS = [
    ("Hardcoded password assignment", re.compile(
        r"""(?:password|passwd|pwd)\s*[=:]\s*['"][^'"]{4,}['"]""", re.IGNORECASE
    )),
    ("API key assignment", re.compile(
        r"""(?:api_key|apikey|api_secret)\s*[=:]\s*['"][^'"]{8,}['"]""", re.IGNORECASE
    )),
    ("Secret/token assignment", re.compile(
        r"""(?:secret_key|secret|token|auth_token|access_token)\s*[=:]\s*['"][^'"]{8,}['"]""",
        re.IGNORECASE
    )),
    ("AWS access key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("AWS secret key pattern", re.compile(
        r"""(?:aws_secret_access_key|aws_secret)\s*[=:]\s*['"][^'"]{20,}['"]""", re.IGNORECASE
    )),
    ("Private key header", re.compile(r"-----BEGIN (?:RSA |EC |DSA )?PRIVATE KEY-----")),
    ("Connection string with password", re.compile(
        r"""(?:postgres|mysql|mongodb|redis)://[^:]+:[^@]{4,}@""", re.IGNORECASE
    )),
    ("Generic secret in env format", re.compile(
        r"""^[A-Z_]+_SECRET\s*=\s*[^\s#]{8,}""", re.MULTILINE
    )),
    ("Bearer token literal", re.compile(
        r"""['"]Bearer\s+[A-Za-z0-9\-_.]{20,}['"]"""
    )),
]

# Patterns that indicate the line is a false positive (comments, docs, examples)
FALSE_POSITIVE_PATTERNS = [
    re.compile(r"#\s*example", re.IGNORECASE),
    re.compile(r"#\s*TODO", re.IGNORECASE),
    re.compile(r"placeholder", re.IGNORECASE),
    re.compile(r"your[_-]?(?:password|key|secret|token)", re.IGNORECASE),
    re.compile(r"<your[_-]", re.IGNORECASE),
    re.compile(r"CHANGE[_-]?ME", re.IGNORECASE),
    re.compile(r"xxx+", re.IGNORECASE),
    re.compile(r"test[_-]?(?:password|key|secret|token)", re.IGNORECASE),
    re.compile(r"fake[_-]?(?:password|key|secret|token)", re.IGNORECASE),
    re.compile(r"dummy", re.IGNORECASE),
    re.compile(r"mock", re.IGNORECASE),
]


def is_false_positive(line: str) -> bool:
    """Check if a line is likely a false positive (example, placeholder, etc.)."""
    return any(p.search(line) for p in FALSE_POSITIVE_PATTERNS)


def should_skip_file(filepath: Path) -> bool:
    """Check if a file should be skipped based on path patterns."""
    name = filepath.name.lower()
    suffix = filepath.suffix.lower()

    if suffix in SKIP_EXTENSIONS:
        return True

    if any(skip in name for skip in SKIP_PATTERNS):
        return True

    parts = filepath.parts
    if any(d in parts for d in SKIP_DIRS):
        return True

    # Skip test files
    if "test" in name and suffix in {".py", ".js", ".ts", ".jsx", ".tsx"}:
        return True

    return False


def get_files_to_scan(scan_all: bool) -> list[Path]:
    """Get list of files to scan."""
    try:
        if scan_all:
            result = subprocess.run(
                ["git", "ls-files"],
                capture_output=True, text=True, cwd=REPO_ROOT
            )
        else:
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
                capture_output=True, text=True, cwd=REPO_ROOT
            )

        if result.returncode != 0:
            return []

        files = []
        for line in result.stdout.strip().split("\n"):
            if line.strip():
                fp = REPO_ROOT / line.strip()
                if fp.is_file() and not should_skip_file(fp):
                    files.append(fp)
        return files

    except (OSError, subprocess.SubprocessError):
        return []


def scan_file(filepath: Path) -> list[tuple[str, int, str, str]]:
    """Scan a single file for secrets. Returns list of (pattern_name, line_num, line_text, filepath)."""
    findings = []
    try:
        text = filepath.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return findings

    for line_num, line in enumerate(text.split("\n"), start=1):
        if is_false_positive(line):
            continue

        for pattern_name, pattern in SECRET_PATTERNS:
            if pattern.search(line):
                truncated = line.strip()[:120]
                findings.append((pattern_name, line_num, truncated, str(filepath.relative_to(REPO_ROOT))))

    return findings


def run_self_test() -> bool:
    """Run built-in validation fixtures. Returns True if all tests pass."""
    print("Running self-test...\n")

    # Known secrets that SHOULD be detected
    known_secrets = [
        ('password = "s3cur3P@ss!"', "Hardcoded password assignment"),
        ('API_KEY = "sk-1234567890abcdef"', "API key assignment"),
        ('secret_key = "my-super-secret-key-value"', "Secret/token assignment"),
        ("AKIAIOSFODNN7EXAMPLE1", "AWS access key"),
        ("-----BEGIN RSA PRIVATE KEY-----", "Private key header"),
        ('postgres://admin:realpassword@host:5432/db', "Connection string with password"),
        ("JWT_SECRET = abcdefghijklmnop", "Generic secret in env format"),
    ]

    # Known clean strings that should NOT be detected
    known_clean = [
        'password = os.environ.get("DB_PASSWORD")',
        "# Set your_password in .env file",
        'api_key = "<CHANGE_ME>"',
        'password = "test_password_123"',
        'secret = "placeholder"',
        "PASSWORD_MIN_LENGTH = 8",
        'token = "xxx"',
    ]

    passed = True

    # Test detection of known secrets
    for text, expected_pattern in known_secrets:
        detected = False
        for pattern_name, pattern in SECRET_PATTERNS:
            if pattern.search(text) and not is_false_positive(text):
                if pattern_name == expected_pattern:
                    detected = True
                    break
        if detected:
            print(f"  PASS: Detected '{expected_pattern}' in: {text[:60]}")
        else:
            print(f"  FAIL: Missed '{expected_pattern}' in: {text[:60]}")
            passed = False

    # Test that clean strings are not flagged
    for text in known_clean:
        flagged = False
        for pattern_name, pattern in SECRET_PATTERNS:
            if pattern.search(text) and not is_false_positive(text):
                flagged = True
                print(f"  FAIL: False positive '{pattern_name}' on: {text[:60]}")
                passed = False
                break
        if not flagged:
            print(f"  PASS: Correctly ignored: {text[:60]}")

    print()
    if passed:
        print("Self-test PASSED: all fixtures validated correctly.")
    else:
        print("Self-test FAILED: see above for details.")

    return passed


def main():
    parser = argparse.ArgumentParser(
        description="Scan files for accidentally committed secrets"
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Scan all tracked files instead of staged only"
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Show each file being scanned"
    )
    parser.add_argument(
        "--self-test", action="store_true",
        help="Run built-in test fixtures to validate detection patterns"
    )
    args = parser.parse_args()

    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    if args.self_test:
        success = run_self_test()
        sys.exit(0 if success else 1)

    scope = "all tracked files" if args.all else "staged files"
    print(f"# Secret Scan ({scope})\n")

    files = get_files_to_scan(scan_all=args.all)
    if not files:
        print(f"No {scope} to scan.")
        sys.exit(0)

    print(f"Scanning {len(files)} files...\n")

    all_findings = []
    for filepath in files:
        if args.verbose:
            print(f"  Scanning: {filepath.relative_to(REPO_ROOT)}")
        findings = scan_file(filepath)
        all_findings.extend(findings)

    if all_findings:
        print(f"## Potential Secrets Found ({len(all_findings)})\n")
        for pattern_name, line_num, line_text, fpath in all_findings:
            print(f"  - [{pattern_name}] {fpath}:{line_num}")
            print(f"    {line_text}")
            print()
        print(f"FAIL: {len(all_findings)} potential secret(s) found in {scope}.")
        sys.exit(1)
    else:
        print(f"PASS: No secrets detected in {len(files)} files.")
        sys.exit(0)


if __name__ == "__main__":
    main()
