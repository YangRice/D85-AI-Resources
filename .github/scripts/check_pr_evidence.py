"""Structural evidence check for skill-contribution PRs.

Reads the PR body from the PR_BODY environment variable and verifies that the
pull request template's walkthrough-evidence table is actually filled in:
both trial rows must carry expected/observed results, an explicit verdict,
and an evidence provenance label. Draft PRs get warnings instead of failures
(they are the documented draft-for-help route); missing sections fail.

Only checks structure, not truthfulness: contributor-reported results are
accepted as labeled, per the contribution rules.

Core logic lives in validate() so the test suite can exercise it directly;
main() is the CLI wrapper the workflow calls.
"""

import os
import re
import sys

VERDICT = re.compile(r"\b(PASS|FAIL|NOT\s*RUN)\b", re.IGNORECASE)
TRIAL_LABELS = ("Realistic task", "Missing input")


def validate(body, draft=False):
    """Return a list of error strings (empty list = pass)."""
    errors = []

    def check(condition, message):
        if not condition:
            errors.append(message)

    check(
        "Walkthrough evidence" in body or "使用测试证据" in body,
        "PR body must follow the pull request template (missing Walkthrough evidence section)",
    )

    rows = {}
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if len(cells) < 6:
            continue
        for label in TRIAL_LABELS:
            if label in cells[0] and label not in rows:
                rows[label] = cells[1:6]

    for label in TRIAL_LABELS:
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
        "Public submission check" in body or "公开投稿检查" in body,
        "Missing 'Public submission check' section from the PR template",
    )
    return errors


def main():
    body = os.environ.get("PR_BODY") or ""
    draft = os.environ.get("PR_DRAFT") == "true"
    errors = validate(body, draft=draft)
    if errors:
        if draft:
            print("::warning::PR is a draft; evidence gaps are allowed for drafts:")
            for error in errors:
                print(f"::warning::{error}")
            return 0
        for error in errors:
            print(f"::error::{error}")
        print(
            "Fill the walkthrough evidence table with expected/observed results, "
            "a verdict, and an evidence label for both trial rows. If checks are "
            "blocked, mark the PR as Draft and state the gaps."
        )
        return 1
    print("PR evidence structure OK: both trial rows filled with verdicts and provenance labels.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
