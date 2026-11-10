"""Portable packaging contracts, not certification of coaching behavior."""

import importlib.util
import re
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SKILL_ID = "prepare-successful-club-presentation"
SPEC = importlib.util.spec_from_file_location(
    "scs_prompt_builder", ROOT / "scripts/build_portable_prompts.py"
)
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)
VALIDATOR_SPEC = importlib.util.spec_from_file_location(
    "portable_skill_validator", ROOT / "scripts/validate_portable_skills.py"
)
VALIDATOR = importlib.util.module_from_spec(VALIDATOR_SPEC)
VALIDATOR_SPEC.loader.exec_module(VALIDATOR)
ITEM = next(item for item in BUILDER.CATALOG["skills"] if item["id"] == SKILL_ID)

REGISTER_COLUMNS = (
    "topic_id",
    "official_title",
    "level",
    "item",
    "canonical_url",
    "supplied_lms_url",
    "duration",
    "research_date",
    "package_url",
    "printed_locators",
    "mutable_authorities",
    "conflict_or_uncertainty",
    "brief_summary",
)
REGISTER_FACT_COLUMNS = (
    "official_title",
    "level",
    "item",
    "canonical_url",
    "supplied_lms_url",
    "duration",
    "research_date",
    "package_url",
    "printed_locators",
    "mutable_authorities",
)
MODULE_CONTRACT_LABELS = {
    "en": (
        "Materials",
        "Accessibility",
        "Handoff and follow-through",
        "Rehearsal and live evaluation",
        "Reflection",
    ),
    "zh": (
        "材料",
        "无障碍与混合形式",
        "交接与后续",
        "排练与现场评估",
        "回顾",
    ),
}
MODULE_CONTRACT_MARKERS = {
    "en": {
        "club-climate": ("Model Club Checklist", "officer"),
        "meeting-roles": ("purpose-and-handoff map", "VPE"),
        "keeping-commitment": ("Toastmaster's Promise", "private reflection"),
        "going-beyond": ("verified public local example", "registration"),
        "finding-new-members": ("fictional guest-journey", "Vice President Membership"),
        "closing-the-sale": ("live-facts card", "treasurer"),
        "distinguished-club": ("299A/FAQ", "fictional Club Success Plan"),
        "education-program": ("goal-to-learning-choice", "Base Camp"),
        "moments-of-truth": ("six work areas", "notetaker", "60–90-minute"),
        "evaluate-to-motivate": ("fictional speech moment", "speaker's choice"),
        "mentoring": ("support-or-takeover", "four-stage relationship map", "VPE"),
    },
    "zh": {
        "club-climate": ("官方 Model Club Checklist", "俱乐部官员"),
        "meeting-roles": ("目的与交接图", "VPE"),
        "keeping-commitment": ("Toastmaster's Promise", "私下反思"),
        "going-beyond": ("已核实的公开本地例子", "报名"),
        "finding-new-members": ("虚构访客旅程", "VPM"),
        "closing-the-sale": ("即时事实卡", "财务长"),
        "distinguished-club": ("299A／FAQ", "虚构 Club Success Plan"),
        "education-program": ("目标到学习选择", "Base Camp"),
        "moments-of-truth": ("六个工作区", "记录员", "60–90 分钟"),
        "evaluate-to-motivate": ("虚构演讲时刻", "讲者自主决定"),
        "mentoring": ("支持还是代替", "四阶段关系图", "VPE"),
    },
}
REGISTER_FACTS = {
    "club-climate": (
        "Creating the Best Club Climate",
        "3",
        "294A",
        "https://www.toastmasters.org/resources/creating-the-best-club-climate",
        "NOT SUPPLIED",
        "10-15 minutes",
        "2026-11-10",
        "https://content.toastmasters.org/raw/upload/294-creating-best-club-climate.zip",
        "294A p. 5; 294A p. 6; 294A pp. 7-8",
        "https://www.toastmasters.org/EducationProgramFAQ; https://toastmasters.org/resources/1111-distinguished-club-program",
    ),
    "meeting-roles": (
        "Meeting Roles and Responsibilities",
        "3",
        "295A",
        "https://www.toastmasters.org/resources/meeting-roles-and-responsibilities",
        "NOT SUPPLIED",
        "10-15 minutes",
        "2026-11-10",
        "https://content.toastmasters.org/raw/upload/295-meeting-roles-and-responsibilities.zip",
        "295A p. 5; 295A p. 6; 295A p. 7",
        "https://www.toastmasters.org/EducationProgramFAQ; https://www.toastmasters.org/resources/club-leadership-handbook",
    ),
    "keeping-commitment": (
        "Keeping the Commitment",
        "3",
        "297A",
        "https://www.toastmasters.org/resources/keeping-the-commitment",
        "NOT SUPPLIED",
        "10-15 minutes",
        "2026-11-10",
        "https://content.toastmasters.org/raw/upload/297-keeping-the-commitment.zip",
        "297A p. 5; 297A p. 6",
        "https://www.toastmasters.org/EducationProgramFAQ; https://content.toastmasters.org/image/upload/1111-distinguished-club-program.pdf",
    ),
    "going-beyond": (
        "Going Beyond Our Club",
        "3",
        "298A",
        "https://www.toastmasters.org/resources/going-beyond-our-club",
        "NOT SUPPLIED",
        "10-15 minutes",
        "2026-11-10",
        "https://content.toastmasters.org/raw/upload/298-going-beyond-our-club.zip",
        "298A p. 5; 298A p. 6",
        "https://www.toastmasters.org/EducationProgramFAQ; https://www.toastmasters.org/resources/2026-2027-speech-contest-rulebook",
    ),
    "finding-new-members": (
        "Finding New Members for Your Club",
        "4",
        "291A",
        "https://www.toastmasters.org/resources/finding-new-members-for-your-club",
        "https://www.toastmasters.org/resources/finding-new-members-for-your-club?utm_source=lms&utm_medium=path&utm_campaign=pathways-enhancements",
        "10-15 minutes",
        "2026-11-10",
        "https://content.toastmasters.org/raw/upload/291-finding-new-members.zip",
        "291A p. 5; 291A p. 6",
        "https://www.toastmasters.org/EducationProgramFAQ; https://www.toastmasters.org/membership/leadership/club-officer-tools/membership-building",
    ),
    "closing-the-sale": (
        "Closing the Sale",
        "4",
        "293A",
        "https://www.toastmasters.org/resources/closing-the-sale",
        "https://www.toastmasters.org/resources/closing-the-sale?utm_source=lms&utm_medium=path&utm_campaign=pathways-enhancements",
        "10-15 minutes",
        "2026-11-10",
        "https://content.toastmasters.org/raw/upload/293-closing-the-sale.zip",
        "293A p. 5; 293A pp. 6-7; 293A p. 8; 293A pp. 9-10",
        "https://www.toastmasters.org/EducationProgramFAQ; https://www.toastmasters.org/footer/faq/Membership-Dues-and-Payments; https://www.toastmasters.org/resources/membership-application; https://www.toastmasters.org/membership/how-to-join.aspx",
    ),
    "distinguished-club": (
        "How to Be a Distinguished Club",
        "4",
        "299A",
        "https://www.toastmasters.org/resources/how-to-be-a-distinguished-club",
        "https://www.toastmasters.org/resources/how-to-be-a-distinguished-club?utm_source=lms&utm_medium=path&utm_campaign=pathways-enhancements",
        "10-15 minutes",
        "2026-11-10",
        "https://content.toastmasters.org/raw/upload/299-how-to-be-a-distinguished-club.zip",
        "299A p. 5; 299A p. 6; 299A p. 7",
        "https://www.toastmasters.org/EducationProgramFAQ; https://content.toastmasters.org/image/upload/1111-distinguished-club-program.pdf",
    ),
    "education-program": (
        "Toastmasters Educational Program",
        "4",
        "300A",
        "https://www.toastmasters.org/resources/toastmasters-educational-program",
        "https://toastmasters.org/resources/toastmasters-educational-program?utm_source=lms&utm_medium=path&utm_campaign=pathways-enhancements",
        "10-15 minutes",
        "2026-11-10",
        "https://content.toastmasters.org/raw/upload/300-toastmasters-education-program.zip",
        "300A pp. 5-6; 300A pp. 7-8; 300A p. 9; 300A p. 10",
        "https://www.toastmasters.org/EducationProgramFAQ",
    ),
    "moments-of-truth": (
        "Moments of Truth",
        "5",
        "290A",
        "https://www.toastmasters.org/resources/moments-of-truth",
        "https://www.toastmasters.org/resources/moments-of-truth?utm_source=lms&utm_medium=path&utm_campaign=pathways-enhancements",
        "60-90 minutes",
        "2026-11-10",
        "https://content.toastmasters.org/raw/upload/290-moments-of-truth.zip",
        "290A p. 5; 290A pp. 6-8; 290A pp. 8-9; 290A pp. 10-11",
        "https://www.toastmasters.org/EducationProgramFAQ; https://toastmasters.org/resources/1111-distinguished-club-program",
    ),
    "evaluate-to-motivate": (
        "Evaluate to Motivate",
        "5",
        "292A",
        "https://www.toastmasters.org/resources/evaluate-to-motivate",
        "https://www.toastmasters.org/resources/evaluate-to-motivate?utm_source=lms&utm_medium=path&utm_campaign=pathways-enhancements",
        "10-15 minutes",
        "2026-11-10",
        "https://content.toastmasters.org/raw/upload/292-evaluate-to-motivate.zip",
        "292A p. 5; 292A p. 6",
        "https://www.toastmasters.org/EducationProgramFAQ",
    ),
    "mentoring": (
        "Mentoring",
        "5",
        "296A",
        "https://www.toastmasters.org/resources/mentoring",
        "https://www.toastmasters.org/resources/mentoring?utm_source=lms&utm_medium=path&utm_campaign=pathways-enhancements",
        "10-15 minutes",
        "2026-11-10",
        "https://content.toastmasters.org/raw/upload/296-mentoring.zip",
        "296A p. 5; 296A p. 6; 296A p. 7; 296A p. 8; 296A p. 9",
        "https://www.toastmasters.org/EducationProgramFAQ; https://www.toastmasters.org/resources/club-leadership-handbook",
    ),
}
ALL_TOPIC_STEMS = {
    "club-climate",
    "meeting-roles",
    "keeping-commitment",
    "going-beyond",
    "finding-new-members",
    "closing-the-sale",
    "distinguished-club",
    "education-program",
    "moments-of-truth",
    "evaluate-to-motivate",
    "mentoring",
}


def parse_topic_register(path: Path) -> tuple[list[str], dict[str, dict[str, str]]]:
    text = path.read_text(encoding="utf-8")
    table_lines = [line for line in text.splitlines() if line.startswith("|")]
    if len(table_lines) < 3:
        raise AssertionError(f"{path}: missing register table")
    columns = [cell.strip() for cell in table_lines[0].strip("|").split("|")]
    if tuple(columns) != REGISTER_COLUMNS:
        raise AssertionError(f"{path}: unexpected columns {columns!r}")
    rows = {}
    for line in table_lines[2:]:
        if line.count("|") != len(REGISTER_COLUMNS) + 1:
            raise AssertionError(f"{path}: unescaped pipe or missing cell in {line!r}")
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != len(REGISTER_COLUMNS) or any("\n" in cell or not cell for cell in cells):
            raise AssertionError(f"{path}: invalid row {line!r}")
        row = dict(zip(REGISTER_COLUMNS, cells))
        if row["topic_id"] in rows:
            raise AssertionError(f"{path}: duplicate topic ID {row['topic_id']}")
        rows[row["topic_id"]] = row
    return table_lines, rows


def parse_module_contract(text: str, lang: str) -> dict[str, str]:
    marker = {
        "en": "## Topic-specific preparation contract",
        "zh": "## 主题专属准备约定",
    }[lang]
    if marker not in text:
        return {}
    section = text.split(marker, 1)[1].split("\n## ", 1)[0]
    rows = {}
    for label in MODULE_CONTRACT_LABELS[lang]:
        match = re.search(rf"^- \*\*{re.escape(label)}[：:]?\*\*\s+(.+)$", section, re.MULTILINE)
        if match:
            rows[label] = match.group(1).strip()
    return rows


class SuccessfulClubPortablePackage(unittest.TestCase):
    def test_catalog_declares_eleven_native_topic_modules_and_two_portable_references(self):
        self.assertEqual(ITEM["version"], "0.3.0")
        self.assertEqual(
            ITEM["portable_references"],
            ["sources-and-boundaries.{lang}.md", "topic-register.{lang}.md"],
        )
        self.assertEqual(
            set(ITEM["native_only_references"]),
            {f"{stem}.{{lang}}.md" for stem in ALL_TOPIC_STEMS},
        )
        self.assertEqual(len(ITEM["native_only_references"]), 11)
        self.assertIn("eleven", ITEM["compatibility"]["en"].lower())
        self.assertIn("11 个主题", ITEM["compatibility"]["zh"])

        agent = (ROOT / "skills" / SKILL_ID / "agents/openai.yaml").read_text(encoding="utf-8")
        self.assertRegex(agent, r'short_description: "[^"]*(11|Levels 3-5)[^"]*"')
        self.assertIn("$prepare-successful-club-presentation", agent)

        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        section = readme.split("### Successful Club Series presentation coach", 1)[1].split(
            "\n---\n", 1
        )[0]
        self.assertIn("Mentoring", section)
        self.assertIn("no Pathways level", section)
        self.assertIn("Moments of Truth", section)
        self.assertIn("60-90 minutes", section)

    def test_all_eleven_modules_match_register_metadata_and_locator_sets(self):
        folder = ROOT / "skills" / SKILL_ID / "references"
        _, register = parse_topic_register(folder / "topic-register.en.md")
        self.assertEqual(set(register), ALL_TOPIC_STEMS)
        for stem in sorted(ALL_TOPIC_STEMS):
            facts = register[stem]
            locators = {}
            urls = {}
            for lang in ("en", "zh"):
                with self.subTest(topic=stem, lang=lang):
                    text = (folder / f"{stem}.{lang}.md").read_text(encoding="utf-8")
                    self.assertIn(f"Official item: **{facts['item']}**", text)
                    self.assertIn(
                        f"Pathways enhancement level: **{facts['level']}**", text
                    )
                    self.assertIn(facts["canonical_url"], text)
                    if facts["supplied_lms_url"] == "NOT SUPPLIED":
                        self.assertIn("Supplied LMS URL: **NOT SUPPLIED**", text)
                    else:
                        self.assertIn(facts["supplied_lms_url"], text)
                    self.assertIn(f"Duration: **{facts['duration']}**", text)
                    self.assertIn(f"Research date: **{facts['research_date']}**", text)
                    self.assertIn(facts["package_url"], text)
                    self.assertIn(f"Printed core outline: **{facts['printed_locators']}**", text)
                    locators[lang] = re.findall(
                        rf"^\| ({facts['item']} p\. \d+) \|", text, re.MULTILINE
                    )
                    self.assertGreaterEqual(len(locators[lang]), 2)
                    urls[lang] = set(re.findall(r"https://[^\s)\]|]+", text))
            self.assertEqual(locators["en"], locators["zh"])
            self.assertEqual(urls["en"], urls["zh"])

    def test_portable_prompt_bundles_register_not_detailed_modules(self):
        folder = ROOT / "skills" / SKILL_ID / "references"
        body_markers = {
            "en": ("## Knowledge notes and printed-page index", "## Source-specific facilitation"),
            "zh": ("## 知识笔记与印刷页码", "## 主题专属引导"),
        }
        for lang in ("en", "zh"):
            with self.subTest(lang=lang):
                output = BUILDER.build_prompt(ITEM, lang)
                register = (folder / f"topic-register.{lang}.md").read_text(encoding="utf-8").strip()
                self.assertEqual(output.count(register), 1)
                for marker in body_markers[lang]:
                    self.assertNotIn(marker, output)
                for stem in ALL_TOPIC_STEMS:
                    detailed = (folder / f"{stem}.{lang}.md").read_text(encoding="utf-8").strip()
                    self.assertNotIn(detailed, output)
                self.assertNotRegex(output, r"\]\(references/[^)]+\)")

    def test_portable_prompts_have_no_local_links_or_maintainer_paths(self):
        for lang in ("en", "zh"):
            with self.subTest(lang=lang):
                output = BUILDER.build_prompt(ITEM, lang)
                markdown_targets = re.findall(r"\[[^\]]*\]\(([^)]+)\)", output)
                local_targets = [
                    target
                    for target in markdown_targets
                    if not target.startswith(("https://", "http://", "#", "mailto:"))
                ]
                self.assertEqual(local_targets, [])
                self.assertNotIn("design/successful-club-presentation-validation.md", output)
                self.assertNotIn(".superpowers/", output)
                maintainer_phrases = {
                    "en": (
                        "Repository maintainers own source refresh",
                        "regenerate portable prompts",
                    ),
                    "zh": (
                        "仓库维护者负责来源更新",
                        "重新生成便携提示词",
                    ),
                }
                for phrase in maintainer_phrases[lang]:
                    self.assertNotIn(phrase, output)

    def test_readme_builds_before_validation_and_routes_behavioral_evidence(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        section = readme.split("### Universal Chat Prompts", 1)[1].split("### Agent Skills", 1)[0]
        commands = (
            "python3 scripts/build_portable_prompts.py",
            "python3 scripts/validate_skill_packages.py",
            "python3 scripts/validate_portable_skills.py",
            "python3 scripts/sync_poster_references.py --check",
            "python3 -m unittest discover -s tests",
            "git diff --check",
        )
        positions = [section.index(command) for command in commands]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("fresh realistic and missing-input or missing-capability trials", section)
        self.assertIn("[CONTRIBUTING.md](CONTRIBUTING.md)", section)

    def test_instruction_contract_covers_level_and_mentoring_decisions(self):
        contracts = {
            "en": (
                "No level constraint",
                "one question at a time",
                "voluntary or future-level",
                "Which goal is the priority: current Level 3 credit or the mentoring need?",
                "does not guarantee current or later credit",
                "topic-specific duration",
            ),
            "zh": (
                "没有等级限制",
                "一次只问一个问题",
                "自愿或未来等级",
                "你现在更优先的是 Level 3 学分，还是 mentoring 学习需求？",
                "不能保证当前或以后获得学分",
                "按主题查找时长",
            ),
        }
        for lang, phrases in contracts.items():
            skill_file = "SKILL.md" if lang == "en" else "SKILL.zh.md"
            text = (ROOT / "skills" / SKILL_ID / skill_file).read_text(encoding="utf-8")
            portable = BUILDER.build_prompt(ITEM, lang)
            for phrase in phrases:
                with self.subTest(lang=lang, phrase=phrase):
                    self.assertIn(phrase, text)
                    self.assertIn(phrase, portable)
            for level in ("Level 3", "Level 4", "Level 5"):
                self.assertIn(level, text)
            self.assertIn("Mentoring", text)
            self.assertIn("Keeping the Commitment", text)

    def test_instruction_contract_covers_moments_of_truth_duration_exception(self):
        phrases = {
            "en": (
                "60-90-minute facilitated",
                "10-15-minute request",
                "adapted overview",
                "organizer or VPE confirmation",
            ),
            "zh": (
                "60-90 分钟引导式",
                "10-15 分钟请求",
                "改编概览",
                "组织者或 VPE 确认",
            ),
        }
        for lang, required in phrases.items():
            skill_file = "SKILL.md" if lang == "en" else "SKILL.zh.md"
            text = (ROOT / "skills" / SKILL_ID / skill_file).read_text(encoding="utf-8")
            portable = BUILDER.build_prompt(ITEM, lang)
            for phrase in required:
                with self.subTest(lang=lang, phrase=phrase):
                    self.assertIn(phrase, text)
                    self.assertIn(phrase, portable)

    def test_portable_prompts_respect_compact_size_budget(self):
        limits = {"en": 30000, "zh": 18000}
        for lang, limit in limits.items():
            with self.subTest(lang=lang):
                output = BUILDER.build_prompt(ITEM, lang)
                tracked = (ROOT / "prompts" / f"{SKILL_ID}.{lang}.md").read_text(
                    encoding="utf-8"
                )
                self.assertEqual(output, tracked)
                self.assertLessEqual(len(output), limit)

    def test_level5_modules_have_matching_bilingual_metadata_and_locator_sets(self):
        folder = ROOT / "skills" / SKILL_ID / "references"
        topics = {
            "moments-of-truth": [
                "290A p. 5",
                "290A p. 6",
                "290A p. 7",
                "290A p. 8",
                "290A p. 9",
                "290A p. 10",
                "290A p. 11",
            ],
            "evaluate-to-motivate": ["292A p. 5", "292A p. 6"],
            "mentoring": [
                "296A p. 5",
                "296A p. 6",
                "296A p. 7",
                "296A p. 8",
                "296A p. 9",
            ],
        }
        _, register = parse_topic_register(folder / "topic-register.en.md")
        for stem, expected_locators in topics.items():
            facts = register[stem]
            self.assertEqual(facts["level"], "5")
            pair_locators = {}
            for lang in ("en", "zh"):
                with self.subTest(topic=stem, lang=lang):
                    path = folder / f"{stem}.{lang}.md"
                    text = path.read_text(encoding="utf-8")
                    self.assertIn(f"Official item: **{facts['item']}**", text)
                    self.assertIn("Pathways enhancement level: **5**", text)
                    self.assertIn(facts["canonical_url"], text)
                    self.assertIn(facts["supplied_lms_url"], text)
                    self.assertIn(f"Duration: **{facts['duration']}**", text)
                    self.assertIn(f"Printed core outline: **{facts['printed_locators']}**", text)
                    pair_locators[lang] = re.findall(
                        r"^\| (\d{3}A p\. \d+) \|", text, re.MULTILINE
                    )
                    self.assertEqual(pair_locators[lang], expected_locators)
                    if lang == "zh":
                        self.assertTrue(text.startswith(f"# {facts['official_title']}｜辅助说明："))
                    if stem == "moments-of-truth":
                        self.assertIn("Duration: **60-90 minutes**", text)
                        self.assertIn(
                            "Facilitated assessment structure: **six moments; team work; ratings; recommendations; notetaker handoff; follow-through**",
                            text,
                        )
                        self.assertIn(
                            "Official-handout boundary: **retrieve the official handout and chart; do not reconstruct or label an AI form official**",
                            text,
                        )
            self.assertEqual(pair_locators["en"], pair_locators["zh"])

    def test_all_eleven_bilingual_modules_define_topic_specific_preparation_contracts(self):
        folder = ROOT / "skills" / SKILL_ID / "references"
        contract_bodies = {"en": [], "zh": []}
        for stem in sorted(ALL_TOPIC_STEMS):
            for lang in ("en", "zh"):
                with self.subTest(topic=stem, lang=lang):
                    text = (folder / f"{stem}.{lang}.md").read_text(encoding="utf-8")
                    contract = parse_module_contract(text, lang)
                    self.assertEqual(tuple(contract), MODULE_CONTRACT_LABELS[lang])
                    self.assertTrue(all(len(value) >= 40 for value in contract.values()))
                    body = "\n".join(contract.values())
                    contract_bodies[lang].append(body)
                    for marker in MODULE_CONTRACT_MARKERS[lang][stem]:
                        self.assertIn(marker, body)
        for lang, bodies in contract_bodies.items():
            with self.subTest(lang=lang, check="distinct contracts"):
                self.assertEqual(len(bodies), len(set(bodies)))

    def test_level4_modules_have_matching_bilingual_metadata_and_locator_sets(self):
        folder = ROOT / "skills" / SKILL_ID / "references"
        topics = {
            "finding-new-members": ("finding-new-members", ["291A p. 5", "291A p. 6"]),
            "closing-the-sale": (
                "closing-the-sale",
                [
                    "293A p. 5",
                    "293A p. 6",
                    "293A p. 7",
                    "293A p. 8",
                    "293A p. 9",
                    "293A p. 10",
                ],
            ),
            "distinguished-club": (
                "distinguished-club",
                ["299A p. 5", "299A p. 6", "299A p. 7"],
            ),
            "education-program": (
                "education-program",
                [
                    "300A p. 5",
                    "300A p. 6",
                    "300A p. 7",
                    "300A p. 8",
                    "300A p. 9",
                    "300A p. 10",
                ],
            ),
        }
        _, register = parse_topic_register(folder / "topic-register.en.md")
        for stem, (topic_id, expected_locators) in topics.items():
            facts = register[topic_id]
            self.assertEqual(facts["level"], "4")
            pair_locators = {}
            for lang in ("en", "zh"):
                with self.subTest(topic=stem, lang=lang):
                    path = folder / f"{stem}.{lang}.md"
                    text = path.read_text(encoding="utf-8")
                    self.assertIn(f"Official item: **{facts['item']}**", text)
                    self.assertIn("Pathways enhancement level: **4**", text)
                    self.assertIn(facts["canonical_url"], text)
                    self.assertIn(facts["supplied_lms_url"], text)
                    self.assertIn(f"Printed core outline: **{facts['printed_locators']}**", text)
                    pair_locators[lang] = re.findall(
                        r"^\| (\d{3}A p\. \d+) \|", text, re.MULTILINE
                    )
                    self.assertEqual(pair_locators[lang], expected_locators)
                    if lang == "zh":
                        self.assertTrue(text.startswith(f"# {facts['official_title']}｜辅助说明："))
            self.assertEqual(pair_locators["en"], pair_locators["zh"])

        official_asset_suffixes = {".pdf", ".ppt", ".pptx"}
        self.assertEqual(
            [path for path in (ROOT / "skills" / SKILL_ID).rglob("*") if path.suffix.lower() in official_asset_suffixes],
            [],
        )

    def test_topic_register_has_exact_schema_and_level_item_url_duration_mapping(self):
        folder = ROOT / "skills" / SKILL_ID / "references"
        for lang in ("en", "zh"):
            with self.subTest(lang=lang):
                _, rows = parse_topic_register(folder / f"topic-register.{lang}.md")
                self.assertEqual(set(rows), set(REGISTER_FACTS))
                for topic_id, expected in REGISTER_FACTS.items():
                    actual = tuple(rows[topic_id][column] for column in REGISTER_FACT_COLUMNS)
                    self.assertEqual(actual, expected)
                    self.assertTrue(rows[topic_id]["brief_summary"])
                    self.assertTrue(rows[topic_id]["conflict_or_uncertainty"])
                self.assertEqual(rows["moments-of-truth"]["duration"], "60-90 minutes")
                self.assertEqual(
                    {row["duration"] for topic_id, row in rows.items() if topic_id != "moments-of-truth"},
                    {"10-15 minutes"},
                )

    def test_register_preserves_known_distinguished_club_credit_conflict(self):
        folder = ROOT / "skills" / SKILL_ID / "references"
        required = {
            "en": ("does not count", "lists it at Level 4", "VPE"),
            "zh": ("不计入", "列为 Level 4", "VPE"),
        }
        for lang in ("en", "zh"):
            with self.subTest(lang=lang):
                _, rows = parse_topic_register(folder / f"topic-register.{lang}.md")
                note = rows["distinguished-club"]["conflict_or_uncertainty"]
                for marker in ("299A", "FAQ", *required[lang]):
                    self.assertIn(marker, note)

    def test_topic_register_language_pairs_preserve_authorities_and_provenance(self):
        folder = ROOT / "skills" / SKILL_ID / "references"
        texts = {}
        rows = {}
        for lang in ("en", "zh"):
            path = folder / f"topic-register.{lang}.md"
            texts[lang] = path.read_text(encoding="utf-8")
            _, rows[lang] = parse_topic_register(path)

        for topic_id in REGISTER_FACTS:
            with self.subTest(topic=topic_id):
                for column in REGISTER_FACT_COLUMNS:
                    self.assertEqual(rows["en"][topic_id][column], rows["zh"][topic_id][column])
                self.assertNotEqual(
                    rows["en"][topic_id]["brief_summary"],
                    rows["zh"][topic_id]["brief_summary"],
                )
        supplied_urls = {facts[4] for facts in REGISTER_FACTS.values()} - {"NOT SUPPLIED"}
        self.assertEqual(len(supplied_urls), 7)
        for url in supplied_urls:
            with self.subTest(url=url):
                self.assertIn(url, texts["en"])
                self.assertIn(url, texts["zh"])

    def test_chinese_sources_use_canonical_club_officer_term(self):
        folder = ROOT / "skills" / SKILL_ID
        paths = (
            "SKILL.zh.md",
            "references/topic-register.zh.md",
            *(f"references/{stem}.zh.md" for stem in (
                "club-climate", "closing-the-sale", "distinguished-club", "education-program",
                "going-beyond", "keeping-commitment", "meeting-roles", "mentoring", "moments-of-truth",
            )),
        )
        for path in paths:
            with self.subTest(source=path):
                contents = (folder / path).read_text(encoding="utf-8")
                self.assertIn("俱乐部官员", contents)
                self.assertNotRegex(contents, r"干部|干事")

    def test_chinese_portable_prompt_supplies_club_officer_term_offline(self):
        output = (ROOT / "prompts" / f"{SKILL_ID}.zh.md").read_text(encoding="utf-8")
        self.assertRegex(output, r"Club Officer\s+译为[“\"]俱乐部官员[”\"]")
        self.assertNotRegex(output, r"干部|干事")

    def test_native_only_reference_paths_are_validated_and_rewritten(self):
        with tempfile.TemporaryDirectory() as temp:
            isolated = Path(temp)
            skill = isolated / "skills" / "fixture"
            references = skill / "references"
            references.mkdir(parents=True)
            item = {
                "id": "fixture",
                "portable_references": ["bundle.{lang}.md"],
                "native_only_references": ["detail.{lang}.md"],
            }
            labels = {
                "en": "detailed notes are not bundled here; use the verified topic summary and official source below",
                "zh": "此处不内嵌详细笔记；请使用下方已核实的主题摘要与官方来源",
            }
            for lang, skill_file in (("en", "SKILL.md"), ("zh", "SKILL.zh.md")):
                (skill / skill_file).write_text(
                    "---\nname: fixture\ndescription: fixture\n---\n\n"
                    f"[Body detail](references/detail.{lang}.md)",
                    encoding="utf-8",
                )
                (references / f"bundle.{lang}.md").write_text(
                    f"# Bundle\n\n[Bundled detail](references/detail.{lang}.md)",
                    encoding="utf-8",
                )
                (references / f"detail.{lang}.md").write_text(
                    "NATIVE DETAIL BODY MUST NOT BE EMBEDDED",
                    encoding="utf-8",
                )

            with patch.object(BUILDER, "ROOT", isolated):
                for lang, expected_label in labels.items():
                    with self.subTest(lang=lang):
                        output = BUILDER.portable_body(item, lang)
                        self.assertEqual(output.count(expected_label), 2)
                        self.assertNotIn("NATIVE DETAIL BODY MUST NOT BE EMBEDDED", output)
                        self.assertNotRegex(output, r"\]\(references/[^)]+\)")

                for template in ("missing.{lang}.md", "../escape.{lang}.md"):
                    with self.subTest(template=template):
                        invalid = {**item, "native_only_references": [template]}
                        with self.assertRaisesRegex(ValueError, rf"fixture.*{re.escape(template)}"):
                            BUILDER.portable_body(invalid, "en")

    def test_skill_without_native_only_references_keeps_existing_output(self):
        for item in BUILDER.CATALOG["skills"]:
            if "native_only_references" in item:
                continue
            for lang in ("en", "zh"):
                path = ROOT / "prompts" / f"{item['id']}.{lang}.md"
                if not path.exists():
                    continue
                with self.subTest(skill=item["id"], lang=lang):
                    self.assertEqual(BUILDER.build_prompt(item, lang), path.read_text(encoding="utf-8"))

    def test_reference_template_validator_rejects_invalid_contracts(self):
        with tempfile.TemporaryDirectory() as temp:
            skill = Path(temp) / "fixture"
            references = skill / "references"
            references.mkdir(parents=True)
            for name in ("bundle.en.md", "bundle.zh.md", "detail.en.md", "detail.zh.md"):
                (references / name).write_text(name, encoding="utf-8")

            cases = {
                "not-list": {
                    "id": "fixture",
                    "portable_references": ["bundle.{lang}.md"],
                    "native_only_references": "detail.{lang}.md",
                },
                "duplicate": {
                    "id": "fixture",
                    "portable_references": ["bundle.{lang}.md"],
                    "native_only_references": ["detail.{lang}.md", "detail.{lang}.md"],
                },
                "overlap": {
                    "id": "fixture",
                    "portable_references": ["bundle.{lang}.md"],
                    "native_only_references": ["bundle.{lang}.md"],
                },
                "missing-language": {
                    "id": "fixture",
                    "portable_references": ["missing.{lang}.md"],
                    "native_only_references": [],
                },
                "escape": {
                    "id": "fixture",
                    "portable_references": ["bundle.{lang}.md"],
                    "native_only_references": ["../escape.{lang}.md"],
                },
            }
            for label, item in cases.items():
                with self.subTest(case=label):
                    errors = VALIDATOR.validate_reference_templates(item, skill)
                    self.assertTrue(errors)
                    self.assertTrue(all("fixture" in error for error in errors))

    def test_reference_template_validator_reports_malformed_values_without_crashing(self):
        with tempfile.TemporaryDirectory() as temp:
            skill = Path(temp) / "fixture"
            references = skill / "references"
            references.mkdir(parents=True)
            for name in ("shared.en.md", "shared.zh.md"):
                (references / name).write_text(name, encoding="utf-8")

            cases = {
                "unhashable": (
                    {
                        "id": "fixture",
                        "portable_references": [{"path": "rules.md"}],
                        "native_only_references": [],
                    },
                    ("invalid portable_references template",),
                ),
                "mixed-overlap": (
                    {
                        "id": "fixture",
                        "portable_references": [1, "shared.{lang}.md"],
                        "native_only_references": [1, "shared.{lang}.md"],
                    },
                    (
                        "invalid portable_references template 1",
                        "invalid native_only_references template 1",
                        "appears in both manifests",
                    ),
                ),
            }
            for label, (item, expected) in cases.items():
                with self.subTest(case=label):
                    try:
                        errors = VALIDATOR.validate_reference_templates(item, skill)
                    except Exception as exc:
                        self.fail(f"validator crashed instead of returning diagnostics: {exc}")
                    diagnostics = "\n".join(errors)
                    for marker in expected:
                        self.assertIn(marker, diagnostics)

    def test_each_language_bundles_every_declared_reference_once(self):
        for lang in ("en", "zh"):
            with self.subTest(lang=lang):
                output = BUILDER.build_prompt(ITEM, lang)
                for template in ITEM["portable_references"]:
                    ref = ROOT / "skills" / SKILL_ID / "references" / template.format(lang=lang)
                    self.assertEqual(output.count(ref.read_text(encoding="utf-8").strip()), 1)
                self.assertNotRegex(output, r"\]\(references/[^)]+\)")
                self.assertNotIn("`action:", output)

    def test_generated_editions_equal_canonical_build(self):
        for lang in ("en", "zh"):
            with self.subTest(lang=lang):
                self.assertEqual(
                    BUILDER.build_prompt(ITEM, lang),
                    (ROOT / "prompts" / f"{SKILL_ID}.{lang}.md").read_text(encoding="utf-8"),
                )

    def test_package_works_without_repository_shared_files_or_other_skills(self):
        with tempfile.TemporaryDirectory() as temp:
            isolated = Path(temp)
            shutil.copytree(ROOT / "skills" / SKILL_ID, isolated / "skills" / SKILL_ID)
            self.assertEqual(ITEM["requires"], [])
            self.assertEqual(ITEM["recommends"], [])
            self.assertEqual(ITEM["actions"], [])
            for lang in ("en", "zh"):
                expected = BUILDER.build_prompt(ITEM, lang)
                with patch.object(BUILDER, "ROOT", isolated), patch.object(BUILDER, "CATALOG", {"skills": [ITEM]}):
                    self.assertEqual(BUILDER.build_prompt(ITEM, lang), expected)

    def test_language_pairs_reference_same_public_authorities(self):
        urls = lambda text: set(re.findall(r"https://[^\s)\]|]+", text))
        for template in ITEM["portable_references"]:
            with self.subTest(reference=template):
                folder = ROOT / "skills" / SKILL_ID / "references"
                self.assertEqual(
                    urls((folder / template.format(lang="en")).read_text(encoding="utf-8")),
                    urls((folder / template.format(lang="zh")).read_text(encoding="utf-8")),
                )

    def test_duration_authority_uses_current_shop_url(self):
        current_url = (
            "https://shop.toastmasters.org/shop/education/programs-and-modules/"
            "the-successful-club-series"
        )
        retired_url = (
            "https://www.toastmasters.org/shop/members/manuals-and-programs/"
            "the-successful-club-series"
        )
        folder = ROOT / "skills" / SKILL_ID / "references"
        for lang in ("en", "zh"):
            with self.subTest(lang=lang):
                boundary = (folder / f"sources-and-boundaries.{lang}.md").read_text(
                    encoding="utf-8"
                )
                portable = BUILDER.build_prompt(ITEM, lang)
                self.assertIn(current_url, boundary)
                self.assertIn(current_url, portable)
                self.assertNotIn(retired_url, boundary)
                self.assertNotIn(retired_url, portable)


    def test_simplified_chinese_content_does_not_reintroduce_converted_variants(self):
        # Scoped regression guard for the variants removed from this package.
        # This is not a general Chinese-language detector; no runtime dependency.
        traditional_variants = set(
            "並佈來倉個們倫備傳傾價優儲內兩冊別則剛創劃動務勢勵勸區協參員問啟單國圍圖團執報場夠學實審寫將專對導層師帶幫幹庫廣張強彙後"
            "徑從復態慣憑憶應採換損擇擋擔據攜攝敘數斷於時晉暢暫曆書會條構樂標樣機檔檢檻欄權歡歷決沒況減測準溝滿潔潛瀏為無熱營狀獎獨獲"
            "獻現環產畫異當發眾確碼礎礙禮種稱穫筆節範簡簽籌籤紀約納級細紹組結絡給經維綱網線編練縮總織繳繼續罰義習聯聲職聽與興舉舊蓋薦"
            "處虛號衝補裝製複見規視親覺覽觀觸訂計訊討訓記訪設許診註評詞詢試話該誌認語誤說誰課誼調請諒論諾講證識譯議護讀變讓財貢責買費"
            "貼資賓質賴購賽贅踐躍較載輔輸轉辦這連週進運過達遠適遲選邊釋釐錄錯鐘長門開間閱關隊階際隱雖難響頁項順須預領頭題額願類顧餘饋"
            "馬驗驟體麼點"
        )
        folder = ROOT / "skills" / SKILL_ID
        texts = {
            "canonical skill": (folder / "SKILL.zh.md").read_text(encoding="utf-8"),
            "generated prompt": (ROOT / "prompts" / f"{SKILL_ID}.zh.md").read_text(encoding="utf-8"),
            "catalog compatibility": ITEM["compatibility"]["zh"],
            "catalog input fields": "\n".join(ITEM["input_fields"]["zh"]),
        }
        for path in (folder / "references").glob("*.zh.md"):
            texts[path.name] = path.read_text(encoding="utf-8")
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        texts["README section"] = readme.split(
            "### Successful Club Series presentation coach", 1
        )[1].split("\n---\n", 1)[0]
        for name, text in texts.items():
            with self.subTest(source=name):
                self.assertEqual(sorted(set(text) & traditional_variants), [])

    def test_topic_knowledge_rows_keep_matching_printed_page_locators(self):
        folder = ROOT / "skills" / SKILL_ID / "references"
        for topic in ("club-climate", "meeting-roles", "keeping-commitment", "going-beyond"):
            with self.subTest(topic=topic):
                locators = {}
                for lang in ("en", "zh"):
                    text = (folder / f"{topic}.{lang}.md").read_text(encoding="utf-8")
                    locators[lang] = re.findall(r"^\| (\d{3}A pp?\. [^|]+) \|", text, re.MULTILINE)
                    self.assertEqual(len(locators[lang]), 7)
                self.assertEqual(locators["en"], locators["zh"])

if __name__ == "__main__":
    unittest.main()
