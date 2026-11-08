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
ITEM = next(item for item in BUILDER.CATALOG["skills"] if item["id"] == SKILL_ID)


class SuccessfulClubPortablePackage(unittest.TestCase):
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
