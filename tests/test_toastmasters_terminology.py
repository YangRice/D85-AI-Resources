import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import sync_toastmasters_terminology as terminology


ROOT = Path(__file__).resolve().parents[1]
SOURCE = Path("references/toastmasters-terminology.md")
POSTER = "skills/poster-image-translation-redesign/references/toastmasters-terminology.md"
POWERPOINT = "skills/powerpoint-translation-redesign/references/toastmasters-terminology.md"
MENTOR = "skills/egg-toastmasters-speech-mentor/references/d85-toastmasters-terminology.md"
PDF = "skills/translate-pdf/references/toastmasters-terminology.md"
PDF_PATHWAYS = "skills/translate-pdf/references/pathways-terminology.md"
SUCCESSFUL_CLUB = "skills/prepare-successful-club-presentation/references/toastmasters-terminology.md"
COACHING = "skills/toastmasters-speech-coaching-team/references/toastmasters-terminology.md"
CONSUMERS = (POSTER, POWERPOINT, MENTOR, PDF, SUCCESSFUL_CLUB, COACHING)
TRANSLATION_PROMPTS = ("translate-pdf", "powerpoint-translation-redesign")
SAMPLE = "# Glossary\n\n| Club Officer | 俱乐部官员 |\n"


class ToastmastersTerminology(unittest.TestCase):
    def make_repo(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        root = Path(directory.name)
        (root / SOURCE).parent.mkdir()
        (root / SOURCE).write_text(SAMPLE, encoding="utf-8")
        return root

    def assert_mirror(self, root, mirror, canonical):
        path = root / mirror
        self.assertTrue(path.is_file(), mirror)
        notice, body = path.read_bytes().split(b"\n\n", 1)
        self.assertIn(SOURCE.as_posix().encode(), notice)
        self.assertIn(b"do not edit", notice.lower())
        self.assertEqual(body, canonical)

    def test_checked_in_mirrors_match_canonical(self):
        self.assertEqual(terminology.sync(ROOT, check=True), [])
        canonical = (ROOT / SOURCE).read_bytes()
        for mirror in CONSUMERS:
            with self.subTest(mirror=mirror):
                self.assert_mirror(ROOT, mirror, canonical)

    def test_every_core_glossary_consumer_is_synchronized(self):
        self.assertCountEqual(terminology.MIRRORS, map(Path, CONSUMERS))

    def test_translation_glossary_links_work_in_independent_packages(self):
        glossary = "references/toastmasters-terminology.md"
        for mirror in (POSTER, POWERPOINT, PDF):
            source = ROOT / Path(mirror).parents[1]
            with self.subTest(skill=source.name), tempfile.TemporaryDirectory() as temp:
                package = Path(temp) / source.name
                shutil.copytree(source, package, symlinks=True)
                instruction = (package / "SKILL.md").read_text(encoding="utf-8")
                expected = [glossary]
                if mirror == PDF:
                    expected.append("references/pathways-terminology.md")
                targets = re.findall(r"\]\(([^)]*terminology\.md)\)", instruction)
                self.assertCountEqual(targets, expected)
                for target in targets:
                    file = (package / target).resolve()
                    self.assertTrue(file.is_relative_to(package.resolve()))
                    self.assertTrue(file.is_file(), target)
                self.assert_mirror(Path(temp), f"{source.name}/{glossary}", (ROOT / SOURCE).read_bytes())

    def test_pdf_pathways_aliases_are_separate_from_core_glossary(self):
        supplement = ROOT / PDF_PATHWAYS
        self.assertTrue(supplement.is_file(), PDF_PATHWAYS)
        pathways = supplement.read_text(encoding="utf-8")
        core = (ROOT / PDF).read_text(encoding="utf-8")
        for alias in (
            "必修 = Required",
            "掌握基础 = Mastering Fundamentals",
            "动态领导 = Dynamic Leadership",
            "初试啼声 = Ice Breaker",
            "反思你的学习路径 = Reflect on Your Path",
            "杰出会员 = Distinguished Toastmaster (DTM)",
        ):
            with self.subTest(alias=alias):
                self.assertIn(alias, pathways)
                self.assertNotIn(alias, core)

    def make_prompt_repo(self):
        root = self.make_repo()
        (root / SOURCE).write_bytes((ROOT / SOURCE).read_bytes())
        (root / "scripts").mkdir()
        for filename in ("build_portable_prompts.py", "sync_toastmasters_terminology.py"):
            shutil.copy2(ROOT / "scripts" / filename, root / "scripts" / filename)
        shutil.copytree(ROOT / "catalog", root / "catalog")
        catalog_path = root / "catalog/skills.json"
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        catalog["skills"] = []
        catalog_path.write_text(json.dumps(catalog), encoding="utf-8")
        for skill_id in (*TRANSLATION_PROMPTS, "toastmasters-speech-coaching-team"):
            shutil.copytree(ROOT / "skills" / skill_id, root / "skills" / skill_id)
        return root

    def generate_translation_prompts(self, root):
        result = subprocess.run(
            [sys.executable, "scripts/build_portable_prompts.py"],
            cwd=root, capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        paths = {skill_id: root / "prompts" / f"{skill_id}.md" for skill_id in TRANSLATION_PROMPTS}
        self.assertEqual([skill_id for skill_id, path in paths.items() if path.is_file()], list(paths))
        return {skill_id: path.read_text(encoding="utf-8") for skill_id, path in paths.items()}

    def test_standalone_translation_prompts_match_generated_offline_content(self):
        outputs = self.generate_translation_prompts(self.make_prompt_repo())
        core = (ROOT / SOURCE).read_text(encoding="utf-8").strip()
        supplement = (ROOT / PDF_PATHWAYS).read_text(encoding="utf-8").strip()
        for skill_id, output in outputs.items():
            with self.subTest(skill=skill_id):
                checked_in = (ROOT / "prompts" / f"{skill_id}.md").read_text(encoding="utf-8")
                self.assertEqual(checked_in, output)
                self.assertEqual(output.count(core), 1)
                self.assertNotRegex(output, r"\]\([^)]*terminology\.md\)")
        self.assertEqual(outputs["translate-pdf"].count(supplement), 1)
        self.assertIn("初试啼声 = Ice Breaker", outputs["translate-pdf"])
        self.assertNotIn(supplement, outputs["powerpoint-translation-redesign"])

    def test_native_coaching_guides_load_the_package_glossary_for_chinese_output(self):
        for mirror, editions in (
            (SUCCESSFUL_CLUB, ("SKILL.md", "SKILL.zh.md")),
            (COACHING, ("SKILL.md",)),
        ):
            for edition in editions:
                with self.subTest(package=mirror, edition=edition):
                    skill = ROOT / Path(mirror).parents[1] / edition
                    self.assertIn("](references/toastmasters-terminology.md)", skill.read_text(encoding="utf-8"))
                    self.assertTrue((ROOT / mirror).is_file())

    def test_standalone_speech_coaching_is_generated_and_keeps_its_text_fallback(self):
        root = self.make_prompt_repo()
        self.generate_translation_prompts(root)
        path = Path("prompts/toastmasters-speech-coaching-team.md")
        self.assertTrue((root / path).is_file(), "The build must own the legacy prompt path")
        generated = (root / path).read_text(encoding="utf-8")
        self.assertEqual(generated, (ROOT / path).read_text(encoding="utf-8"))
        instructions = generated.split("## Instructions for the AI", 1)[1]
        core = (ROOT / SOURCE).read_text(encoding="utf-8").strip()
        self.assertEqual(instructions.count(core), 1)
        self.assertNotRegex(instructions, r"\]\(references/[^)]+\)")
        self.assertIn("If it does not, evaluate the roles sequentially", instructions)
        self.assertIn("Never claim that independent agents were used unless they actually were.", instructions)
        self.assertIn("five separate role reports", instructions)
        native = (ROOT / Path(COACHING).parents[1] / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("If sub-agents are unavailable, stop", native)

    def test_build_refreshes_stale_mirrors_before_embedding(self):
        root = self.make_prompt_repo()
        new_term = "| Fixture Term | 测试术语 |"
        glossary = (root / SOURCE).read_text(encoding="utf-8") + new_term + "\n"
        (root / SOURCE).write_text(glossary, encoding="utf-8")
        self.assertNotIn(new_term, (root / PDF).read_text(encoding="utf-8"))
        self.assertNotIn(new_term, (root / POWERPOINT).read_text(encoding="utf-8"))

        outputs = self.generate_translation_prompts(root)

        for mirror in CONSUMERS:
            self.assert_mirror(root, mirror, glossary.encode())
        for output in outputs.values():
            self.assertEqual(output.count(new_term), 1)

    def test_sync_repairs_drift(self):
        root = self.make_repo()
        poster = root / POSTER
        poster.parent.mkdir(parents=True)
        poster.write_text("stale", encoding="utf-8")

        self.assertEqual(terminology.sync(root, check=False), [])

        self.assertEqual((root / SOURCE).read_bytes(), SAMPLE.encode())
        for mirror in CONSUMERS:
            with self.subTest(mirror=mirror):
                self.assert_mirror(root, mirror, SAMPLE.encode())

    def test_check_reports_missing_and_drifted_mirrors(self):
        root = self.make_repo()
        poster = root / POSTER
        poster.parent.mkdir(parents=True)
        poster.write_text("stale", encoding="utf-8")
        modified = poster.stat().st_mtime_ns

        self.assertCountEqual(terminology.sync(root, check=True), CONSUMERS)

        self.assertEqual(poster.read_bytes(), b"stale")
        self.assertEqual(poster.stat().st_mtime_ns, modified)
        for mirror in CONSUMERS[1:]:
            self.assertFalse((root / mirror).parent.exists())
        self.assertEqual((root / SOURCE).read_bytes(), SAMPLE.encode())

    def test_sync_rejects_symlink_destination(self):
        root = self.make_repo()
        target = root / "untouched.md"
        target.write_text("untouched", encoding="utf-8")
        link = root / POWERPOINT
        link.parent.mkdir(parents=True)
        link.symlink_to(target)

        for check in (True, False):
            with self.subTest(check=check):
                with self.assertRaises(ValueError) as error:
                    terminology.sync(root, check=check)
                self.assertEqual(str(error.exception), f"Symlink destination: {POWERPOINT}")
                self.assertEqual(target.read_bytes(), b"untouched")
                self.assertTrue(link.is_symlink())
                self.assertFalse((root / POSTER).parent.exists())

    def test_mirror_destinations_stay_under_skill_reference_directories(self):
        root = self.make_repo()
        for path in (
            Path("references/not-a-mirror.md"),
            Path("skills/example/references/../not-a-mirror.md"),
            root / "skills/example/references/absolute.md",
        ):
            with self.subTest(path=path), patch.object(terminology, "MIRRORS", (path,)):
                with self.assertRaises(ValueError) as error:
                    terminology.sync(root, check=False)
                self.assertEqual(str(error.exception), f"Invalid mirror destination: {path.as_posix()}")
        self.assertFalse((root / "skills").exists())

        redirect = root / "redirect"
        redirect.mkdir()
        parent = (root / POSTER).parent
        parent.parent.mkdir(parents=True)
        parent.symlink_to(redirect, target_is_directory=True)
        with self.assertRaises(ValueError) as error:
            terminology.sync(root, check=False)
        self.assertEqual(str(error.exception), f"Symlink destination: {POSTER}")
        self.assertEqual(list(redirect.iterdir()), [])

    def test_missing_canonical_names_source_and_does_not_write(self):
        root = self.make_repo()
        (root / SOURCE).unlink()

        with self.assertRaises(FileNotFoundError) as error:
            terminology.sync(root, check=False)

        self.assertEqual(str(error.exception), f"Missing canonical glossary: {SOURCE.as_posix()}")
        self.assertFalse((root / "skills").exists())


class ChineseTerminologyContracts(unittest.TestCase):
    """Regressions for named concepts, not bans on words used in other contexts."""

    def assert_phrases(self, directory, cases):
        for concept, path, phrase in cases:
            with self.subTest(concept=concept, path=path, phrase=phrase):
                self.assertTrue(
                    any(phrase in line for line in (ROOT / directory / path).read_text(encoding="utf-8").splitlines()),
                    f"{path}: expected {phrase!r} for {concept}",
                )

    def test_pathways_and_speech_feedback_use_distinct_terms(self):
        self.assert_phrases("skills", (
            ("C01 Pathways Level", "build-speech-outline/SKILL.zh.md", "Pathways 阶段或项目"),
            ("C01 Pathways completion", "serve-club-vpe/SKILL.zh.md", "项目／阶段认证完成"),
            ("C02 formal Evaluation criteria", "build-speech-outline/SKILL.zh.md", "项目简介或点评标准"),
            ("C13 Speaker ownership", "prepare-speech-evaluation/SKILL.zh.md", "演讲者内容所有权"),
            ("C15 TI judgment", "prepare-speech-evaluation/SKILL.zh.md", "国际头马的官方判断"),
            ("C16 feedback publication", "prepare-speech-evaluation/SKILL.zh.md", "发布反馈"),
            ("C16 feedback learning objective", "understand-pathways-project/SKILL.zh.md", "领导力、研究、辅导、反馈"),
            ("N25 formal evaluation form", "understand-pathways-project/SKILL.zh.md", "点评表"),
        ))

    def test_meeting_roles_name_people_in_the_dispatch_rows(self):
        for edition in ("SKILL.md", "SKILL.zh.md"):
            with self.subTest(edition=edition):
                self.assert_phrases("skills", tuple(
                    (concept, f"perform-toastmasters-meeting-role/{edition}", f"| {label} | `{target}` |")
                    for concept, label, target in (
                        ("C03 Table Topics Evaluator", "Table Topics Evaluator / 即兴演讲点评人 TTE", "prepare-table-topics-evaluation"),
                        ("C04 Speech Evaluator", "Individual Speech Evaluator / 演讲点评人", "prepare-speech-evaluation"),
                        ("C06 Topicsmaster", "Topicsmaster / 即兴演讲主持人 TTM", "prepare-topicsmaster-role"),
                        ("C07 Timer", "Timer / 时间官", "prepare-timer-role"),
                        ("C10 Toastmaster", "Toastmaster of the Day / 会议主持人", "prepare-toastmaster-role"),
                    )
                ))

    def test_table_topics_labels_the_segment_role_and_contest_in_context(self):
        self.assert_phrases("skills", (
            *(("C03 optional segment route", f"{skill}/SKILL.zh.md", "#topics 是即兴演讲，不是导师入口")
              for skill in ("coach-mentee-practice", "establish-mentoring-agreement",
                            "practice-mentoring-conversation", "review-mentoring-relationship")),
            ("C03 evaluation activity", "prepare-table-topics-evaluation/SKILL.zh.md", "# 准备即兴演讲点评"),
            ("C03 assigned evaluator", "prepare-topicsmaster-role/references/role-guide.zh.md", "是否安排即兴演讲点评人"),
            ("C20 contest disqualification", "prepare-topicsmaster-role/SKILL.zh.md", "普通会议不套用演讲比赛取消资格规则"),
        ))

    def test_egg_evaluation_uses_canonical_role_names_without_changing_user_triggers(self):
        playbook = "egg-toastmasters-speech-mentor/references/evaluation-playbook.md"
        router = "egg-toastmasters-speech-mentor/SKILL.zh.md"
        self.assert_phrases("skills", (
            ("C02 activity", playbook, "即兴演讲点评（Table Topics Evaluation）"),
            ("C03 assigned TT evaluator", playbook, "即兴演讲点评人**（TT Evaluator）"),
            ("C04 Individual Evaluator", playbook, "个人点评人**（Individual Evaluator）"),
            ("C05 assigned Evaluator", playbook, "**感谢点评人**"),
            ("C07/C08/C10/C11 meeting-role roster", playbook, "各会议角色履职情况（时间官、语言官、哼哈官、会议主持人）"),
            ("C09 Grammarian's word", playbook, "**语言官** | 每日一词"),
            ("C12 contest timebox", "egg-toastmasters-speech-mentor/references/delivery-craft.md", "| 国际演讲比赛（5-7 分钟） |"),
            ("N06 participant's activity shorthand", playbook, '用户说"我要做个评"'),
            ("N06 recognition alias", router, "担任即兴主持"),
            ("N07 ASR speaker diarization", router, "说话人识别错误"),
        ))

    def test_officer_names_are_distinct_from_task_scopes(self):
        self.assert_phrases("skills", (
            ("C14 elected SAA in coordination", "serve-club-president/SKILL.md", "SAA (接待官) handles venue"),
            ("C14 SAA handoff", "serve-club-vpm/SKILL.zh.md", "与接待官准备到场欢迎流程"),
            ("N20 recurring logistics", "serve-club-saa/SKILL.zh.md", "可重复使用的运营标准与任期会务"),
            ("C18 Treasurer handoff", "prepare-successful-club-presentation/references/closing-the-sale.zh.md", "VPM 或财务官交接"),
            ("C19 Secretary roster", "serve-toastmasters-club-officer/SKILL.md", "| Secretary / 秘书长 | `serve-club-secretary` |"),
            ("C19 Secretary roster", "serve-toastmasters-club-officer/SKILL.zh.md", "| Secretary / 秘书长 | `serve-club-secretary` |"),
            ("C19 Secretary title", "serve-club-secretary/SKILL.zh.md", "# 担任俱乐部秘书长"),
        ))

    def test_successful_club_distinguishes_speech_evaluation_from_club_assessment(self):
        folder = "prepare-successful-club-presentation/references"
        self.assert_phrases("skills", (
            ("C02 speech assessment form", f"{folder}/meeting-roles.zh.md", "项目点评表"),
            ("C02 evaluation segment", f"{folder}/meeting-roles.zh.md", "总评协调点评环节并评估整场会议"),
            ("C05 assigned evaluator", f"{folder}/evaluate-to-motivate.zh.md", "请点评人检查"),
            ("C17 meeting Guest and act of visiting", f"{folder}/topic-register.zh.md", "来宾接待、再次来访与加入邀请"),
            ("C17 / Q05 mixed scope", f"{folder}/moments-of-truth.zh.md", "部分来宾与评估问题"),
            ("N18 club assessment", f"{folder}/moments-of-truth.zh.md", "各组只评估分配到的俱乐部体验"),
            ("N18 separate privacy categories", f"{folder}/sources-and-boundaries.zh.md", "已填俱乐部评估、可识别演讲点评"),
            ("N18 checklist assessment", f"{folder}/topic-register.zh.md", "Model Club Checklist 开展评估"),
        ))

    def test_updated_mappings_reach_the_portable_aggregates(self):
        self.assert_phrases("prompts", (
            ("C01/C02 speech preparation", "prepare-toastmasters-speech.zh.md", "Pathways 阶段或项目"),
            ("C02 project Evaluation", "prepare-toastmasters-speech.zh.md", "项目简介或点评标准"),
            ("C03 mentoring route", "mentor-toastmasters-member.zh.md", "#topics 是即兴演讲，不是导师入口"),
            ("C10/C14 officer handoff", "serve-toastmasters-club-officer.zh.md", "与 VPM、VPE 和会议主持人的本会交接方式"),
            ("C13/C16 speech ownership", "give-and-apply-toastmasters-feedback.zh.md", "发布反馈，尊重演讲者内容所有权"),
            ("C16 Pathways navigation", "navigate-pathways-learning.zh.md", "领导力、研究、辅导、反馈"),
        ))

    def test_egg_formal_evaluation_and_scored_diagnostics_keep_distinct_labels(self):
        egg = "egg-toastmasters-speech-mentor"
        router = f"{egg}/SKILL.zh.md"
        playbook = f"{egg}/references/evaluation-playbook.md"
        cases = f"{egg}/references/case-study-and-peer-eval.md"
        nvc = f"{egg}/references/nonviolent-communication.md"
        persuasion = f"{egg}/references/guiguzi-persuasion.md"
        self.assert_phrases("skills", (
            ("weekly formal evaluation capability", router, "点评技巧排最后但频次最高"),
            ("weekly formal evaluation practice", router, "会员每周例会都在做点评"),
            ("evaluation workshop route", router, "**点评工坊**（独立支线）"),
            ("speaking feedback example", playbook, "这本身就是最好的点评"),
            ("formal evaluation red lines", playbook, "## 8. 点评的禁忌与红线"),
            ("formal evaluation structure", nvc, "点评的结构、时间分配与角色流程"),
            ("timed General Evaluator structure", nvc, "不能替代点评结构（总评仍按 2.5 分钟"),
            ("assigned evaluation role", f"{egg}/references/jobs-presentation-secrets.md", "点评角色比演讲者低调半档"),
            ("individual evaluator's opening", persuasion, "个评怎么开口 | 点评 | `evaluation-playbook.md`"),
            ("numeric diagnostic library index", router, "三明治法、真实评估定级案例库"),
            ("numeric diagnostic library cross-reference", playbook, "**真实评估定级案例库**（《旧木箱》78 分"),
            ("numeric diagnostic library contents", cases, "③真实评估定级案例库"),
            ("numeric diagnostic library section", cases, "## 三、真实评估定级案例库"),
            ("Mode B prepared-speech rubric", playbook, "模式 B 的备稿演讲七维诊断表"),
            ("formal individual evaluation technique", cases, "点评三明治法（用户担任个人点评人时使用）"),
            ("NVC concept", nvc, "评论（Evaluations）"),
        ))

    def test_egg_names_assigned_people_in_meeting_reports_and_speech_guidance(self):
        egg = "egg-toastmasters-speech-mentor"
        router = f"{egg}/SKILL.zh.md"
        playbook = f"{egg}/references/evaluation-playbook.md"
        persuasion = f"{egg}/references/guiguzi-persuasion.md"
        self.assert_phrases("skills", (
            ("assigned individual evaluators", playbook, "个人点评人是否都守时、结构是否完整？"),
            ("whole-meeting host transitions", playbook, "会议主持人串场是否流畅"),
            ("whole-meeting host index", router, "会议角色（总评/语言官/哼哈官/会议主持人等）"),
            ("speaker guiding delivery", router, "鬼谷子留给演讲者的东西"),
            ("speaker practice section", persuasion, "本经阴符七术：演讲者的内功"),
            ("speaker practice abilities", persuasion, "| 演讲者的什么能力 |"),
        ))

    def test_official_pathways_authority_is_named_in_tool_finder(self):
        phrase = "Pathways 项目要求和完成认定以国际头马的官方资料及俱乐部指导为准"
        self.assert_phrases("skills", (
            ("official Toastmasters authority", "find-tmcompanion-tool/SKILL.zh.md", phrase),
        ))
        self.assert_phrases("prompts", (
            ("official Toastmasters authority", "find-tmcompanion-tool.zh.md", phrase),
        ))

    def test_meeting_role_guides_name_the_people_receiving_evaluation_or_handoff(self):
        handoff = "结束时按议程交接给时间官、即兴演讲点评人或会议主持人"
        self.assert_phrases("skills", (
            ("speaker receiving official evaluation", "prepare-successful-club-presentation/references/meeting-roles.zh.md",
             "适用于演讲者的正确官方点评资料"),
            ("Topicsmaster's handoff recipients", "prepare-topicsmaster-role/references/role-guide.zh.md", handoff),
        ))
        self.assert_phrases("prompts", (
            ("Topicsmaster's handoff recipients", "prepare-topicsmaster-role.zh.md", handoff),
            ("aggregate handoff recipients", "perform-toastmasters-meeting-role.zh.md", handoff),
        ))

    def test_egg_formal_playbook_labels_do_not_rename_diagnostic_workflows(self):
        egg = "egg-toastmasters-speech-mentor"
        router = f"{egg}/SKILL.zh.md"
        persuasion = f"{egg}/references/guiguzi-persuasion.md"
        debate = f"{egg}/references/debate-and-qa.md"
        self.assert_phrases("skills", (
            ("eight-dimension evaluation capability", router, "听众分析、辩论与应答、点评技巧。"),
            ("formal role methods in metadata", router, "点评侧方法：五角色（"),
            ("formal playbook in changelog", router, "**P2 点评手册**（`references/evaluation-playbook.md`）"),
            ("formal Table Topics playbook", router, "完整点评操作手册见 `references/evaluation-playbook.md` §3"),
            ("formal evaluation in persuasion index", persuasion, "表达/点评 | `delivery-craft.md`、`evaluation-playbook.md`"),
            ("suggested response after formal evaluation", debate, "不合适就丢掉——点评不是标准答案。"),
            ("numeric contest assessment", router, "比赛级评估定级（大区评委视角"),
            ("numeric Table Topics dimensions", router, "即兴演讲（Table Topics）评估维度"),
            ("diagnostic report workflow", router, "评估报告（大区评委·蛋导）"),
            ("evaluation activity alias", debate, "用户做完个评被追问"),
            ("Table Topics practice aliases", router, "要做个评/总评/评即兴/自评"),
        ))

    def test_egg_evaluator_rosters_and_feedback_attribution_name_assigned_people(self):
        egg = "egg-toastmasters-speech-mentor"
        router = f"{egg}/SKILL.zh.md"
        roster = "五角色（个人点评人/总评/即兴演讲点评人/比赛评委/自评）"
        self.assert_phrases("skills", (
            ("assigned evaluators in metadata", router, f"点评侧方法：{roster}"),
            ("assigned evaluators in the playbook changelog", router, f"`references/evaluation-playbook.md`）：{roster}"),
            ("assigned evaluator attribution", f"{egg}/references/audience-analysis.md",
             '个人点评人说"看不懂标题和内容的关系"'),
            ("individual evaluation example", router, "**完整逐字个评范例**"),
        ))

    def test_egg_crc_attribution_names_toastmasters_international(self):
        self.assert_phrases("skills", (
            ("institution named in CRC attribution", "egg-toastmasters-speech-mentor/references/evaluation-playbook.md",
             "**CRC**（Commend-Recommend-Commend） | 表扬 → 建议 → 表扬 | 国际头马官方体系，英文俱乐部常用"),
        ))
