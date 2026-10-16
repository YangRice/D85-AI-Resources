"""Structural evidence check for skill-contribution PRs.

Reads the PR body from the PR_BODY environment variable and verifies that the
pull request template's walkthrough-evidence table is actually filled in:
both trial rows must carry expected/observed results, an explicit verdict,
and an evidence provenance label. Draft PRs get warnings instead of failures
(they are the documented draft-for-help route); missing sections fail.

Only checks structure, not truthfulness: contributor-reported results are
accepted as labeled, per the contribution rules.
"""

import os
import re
import sys

BODY = os.environ.get("PR_BODY") or ""
DRAFT = os.environ.get("PR_DRAFT") == "true"

VERDICT = re.compile(r"\b(PASS|FAIL|NOT\s*RUN)\b", re.IGNORECASE)

errors = []


def check(condition, message):
    if not condition:
        errors.append(message)


def trial_rows():
    """Map trial label -> (input, expected, observed, verdict, evidence)."""
    rows = {}
    for line in BODY.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if len(cells) >= 6 and ("Realistic task" in cells[0] or "Missing input" in cells[0]):
            rows[cells[0]] = cells[1:6]
    return rows


check(
    "Walkthrough evidence" in BODY or "使用测试证据" in BODY,
    "PR body must follow the pull request template (missing Walkthrough evidence section)",
)

rows = trial_rows()
for label in ("Realistic task", "Missing input"):
    if label not in rows:
        check(False, f"Missing trial row: '{label}'")
        continue
    _input, expected, observed, verdict, evidence = rows[label]
    check(bool(expected), f"'{label}' row: Expected column is empty")
    check(bool(observed), f"'{label}' row: Observed column is empty")
    check(
        bool(VERDICT.search(verdict)),
        f"'{label}' row: verdict must be PASS, FAIL, or NOT RUN (got '{verdict}')",
    )
    check(
        "contributor-reported" in evidence.lower() or "observed" in evidence.lower(),
        f"'{label}' row: evidence must say 'observed' or 'contributor-reported' (got '{evidence}')",
    )

check(
    "Public submission check" in BODY or "公开投稿检查" in BODY,
    "Missing 'Public submission check' section from the PR template",
)

if errors:
    if DRAFT:
        print("::warning::PR is a draft; evidence gaps are allowed for drafts:")
        for error in errors:
            print(f"::warning::{error}")
        sys.exit(0)
    for error in errors:
        print(f"::error::{error}")
    print(
        "Fill the walkthrough evidence table with expected/observed results, "
        "a verdict, and an evidence label for both trial rows. If checks are "
        "blocked, mark the PR as Draft and state the gaps."
    )
    sys.exit(1)

print("PR evidence structure OK: both trial rows filled with verdicts and provenance labels.")
