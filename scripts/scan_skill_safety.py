"""Best-effort safety scan for PR content (skill packages and other files).

Implements the contribution rules' public-safety requirements as a static,
automated gate: unresolved secrets, private material, and symlinks block
uploads — including draft PRs. Network-capable scripts, binary files, and
generic credential-looking assignments are flagged for human review.

Heuristics only: a clean scan is not a guarantee, per the rules.

Usage (CI and harness):
    BASE_SHA=<base> python3 scripts/scan_skill_safety.py
Scans files changed between BASE_SHA and HEAD, prints ::error:: / ::warning::
annotations, and exits 1 if any blocking finding exists.

Core logic lives in scan_text()/scan_bytes() so the test suite can exercise
it directly; main() is the git/CI wrapper.
"""

import os
import re
import subprocess
import sys

# Specific, well-known credential formats: block on sight.
BLOCK_PATTERNS = [
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "AWS access key pattern"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{36,}\b"), "GitHub token pattern"),
    (re.compile(r"-----BEGIN( [A-Z ]+)?PRIVATE KEY-----"), "private key block"),
    (re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"), "Slack token pattern"),
    (re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"), "API key pattern (sk-)"),
]

# File names that must never become public.
BLOCK_FILENAMES = re.compile(
    r"(^|/)(\.env(\.\w+)?|id_rsa|id_ed25519|\.pem|\.key|credentials(\.\w+)?)$"
)

# Specific-user home paths (macOS and Windows): personal material, block.
BLOCK_PATHS = re.compile(
    r"/Users/[^/\s'\"()]+/(Documents|Desktop|Downloads|Pictures|Movies|Library)/"
    r"|C:\\Users\\[^\\\s'\"()]+\\"
)

# Generic home references: could be legitimate user guidance, review.
# Split so the scanner's own source does not trip the pattern.
WARN_PATHS = re.compile(chr(126) + r"[/\w.-]*|" + "/hom" + "e/" + r"[^/\s'\"()]+/")

# Generic credential-looking assignments: review, not auto-block.
GENERIC_SECRET = re.compile(
    r"(?i)\b(api[_-]?key|secret|passwd|password|token)\b\s*[:=]\s*['\"]?([A-Za-z0-9_\-.]{16,})"
)
PLACEHOLDERS = (
    "your", "example", "placeholder", "replace", "xxx", "changeme",
    "sample", "fake", "test", "abcdefghijklmnop",
)

# Network-capable code in candidate scripts: review before execution.
NETWORK_CODE = re.compile(
    r"(import\s+(urllib|requests|socket|http\.client)|"
    r"from\s+(urllib|requests|socket)\s+import|\bcurl\b\s|\bwget\b\s)"
)
SCRIPT_SUFFIXES = (".py", ".sh", ".js", ".mjs", ".ts")


def scan_text(text, relpath):
    """Return list of (level, message) findings for text content."""
    findings = []
    if BLOCK_FILENAMES.search(relpath):
        findings.append(("block", "credential or env file name must not be public"))
    for pattern, label in BLOCK_PATTERNS:
        if pattern.search(text):
            findings.append(("block", f"possible secret: {label}"))
    for match in BLOCK_PATHS.finditer(text):
        findings.append(("block", f"private user path: {match.group(0)}"))
    for match in WARN_PATHS.finditer(text):
        findings.append(("warn", f"home-directory path, review: {match.group(0)}"))
    for match in GENERIC_SECRET.finditer(text):
        value = match.group(2).lower()
        if not any(word in value for word in PLACEHOLDERS):
            findings.append(
                ("warn", f"credential-looking assignment '{match.group(1)}' at a long value, review")
            )
    is_script = relpath.endswith(SCRIPT_SUFFIXES) or "/scripts/" in relpath
    if is_script and NETWORK_CODE.search(text):
        findings.append(
            ("warn", "network-capable script; review before controlled execution")
        )
    return findings


def scan_bytes(data, relpath):
    """Return findings for binary-ish content: flag for review."""
    findings = []
    if b"\x00" in data[:8000]:
        findings.append(
            ("warn", "binary file; verify it is not private material (photo/QR)")
        )
    return findings


def main():
    base = os.environ.get("BASE_SHA") or "origin/main"
    try:
        names = subprocess.run(
            ["git", "diff", "--name-only", base, "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout.splitlines()
        summary = subprocess.run(
            ["git", "diff", "--summary", base, "HEAD"],
            capture_output=True, text=True, check=True,
        ).stdout
    except subprocess.CalledProcessError as exc:
        print(f"::error::could not compute PR diff: {exc}")
        return 1

    blocks = 0
    for name in names:
        relpath = name.strip()
        if not relpath:
            continue
        data = b""
        try:
            with open(relpath, "rb") as handle:
                data = handle.read()
        except OSError:
            findings = [("warn", "changed file not readable in checkout")]
            text = ""
        else:
            findings = scan_bytes(data, relpath)
            try:
                text = data.decode("utf-8")
            except UnicodeDecodeError:
                text = data.decode("utf-8", errors="replace")
            findings += scan_text(text, relpath)
        for level, message in findings:
            annotation = "error" if level == "block" else "warning"
            print(f"::{annotation}::{relpath}: {message}")
            if level == "block":
                blocks += 1

    for line in summary.splitlines():
        if "mode 120000" in line:
            path = line.rsplit(" ", 1)[-1]
            print(f"::error::{path}: symlink — rules reject symlinks in public files")
            blocks += 1

    if blocks:
        print(
            f"{blocks} blocking finding(s). Per the contribution rules, unresolved "
            "secrets, private material, and symlinks block all uploads, including drafts."
        )
        return 1
    print("Skill safety scan: no blocking findings (best-effort; not a guarantee).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
