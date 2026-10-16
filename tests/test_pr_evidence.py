"""Tests for the PR evidence structure checker (.github/scripts/check_pr_evidence.py)."""

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "check_pr_evidence", ROOT / ".github/scripts/check_pr_evidence.py"
)
CHECKER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER)


def filled_body(label1="Realistic task / 正常使用", label2="Missing input or capability / 缺少输入或能力"):
    return (
        "## Walkthrough evidence | 使用测试证据\n"
        "| Case / 场景 | Input / 输入 | Expected / 预期 | Observed / 实际 | "
        "PASS / FAIL / NOT RUN | Evidence: observed or contributor-reported / 证据：亲自查看或贡献者反馈 |\n"
        "|---|---|---|---|---|---|\n"
        f"| {label1} | sample input | structured output | produced output | PASS | observed |\n"
        f"| {label2} | notes without attendees | ask instead of inventing | asked for attendees "
        "| PASS | contributor-reported |\n"
        "## Public submission check | 公开投稿检查\n"
        "- [x] intended files only.\n"
    )


class EvidenceChecker(unittest.TestCase):
    def test_bilingual_template_labels_pass(self):
        self.assertEqual(CHECKER.validate(filled_body()), [])

    def test_english_only_labels_pass(self):
        self.assertEqual(
            CHECKER.validate(filled_body("Realistic task", "Missing input")), []
        )

    def test_empty_body_reports_all_gaps(self):
        errors = CHECKER.validate("")
        self.assertEqual(len(errors), 4)
        joined = "\n".join(errors)
        for token in ("Walkthrough evidence", "Realistic task", "Missing input", "Public submission check"):
            self.assertIn(token, joined)

    def test_empty_observed_cell_fails(self):
        body = (
            "## Walkthrough evidence\n"
            "| Realistic task | in | expected |  | PASS | observed |\n"
            "| Missing input | in | expected | observed | PASS | observed |\n"
            "## Public submission check\n"
        )
        errors = CHECKER.validate(body)
        self.assertTrue(any("Observed column is empty" in e for e in errors), errors)

    def test_invalid_verdict_and_provenance_fail(self):
        body = (
            "## Walkthrough evidence\n"
            "| Realistic task | in | expected | observed | maybe | contributor-reported |\n"
            "| Missing input | in | expected | observed | PASS | third-party |\n"
            "## Public submission check\n"
        )
        errors = CHECKER.validate(body)
        joined = "\n".join(errors)
        self.assertIn("verdict must be", joined)
        self.assertIn("evidence must say", joined)

    def test_separator_and_header_rows_are_ignored(self):
        self.assertEqual(CHECKER.validate(filled_body()), [])


if __name__ == "__main__":
    unittest.main()
