# D85 AI Resources

> District 85 Toastmasters — AI Empowerment OKR Skills Repository  
> 国际演讲会 85 大区 — AI 赋能 OKR 技能资源库

---

## 📖 Overview | 概述

This repository contains reusable skill definitions designed for **AI coding agents** (Hermes Agent, Claude Code, Codex, etc.) used in the **D85 AI Empowerment OKR** initiative. These skills encode structured workflows, quality gates, and domain-specific knowledge — enabling AI agents to reliably perform Toastmasters-related tasks.

本仓库包含为 **D85 AI 赋能 OKR** 项目设计的、供 AI 编程助手（Hermes Agent、Claude Code、Codex 等）使用的可复用技能定义。每个技能都编码了结构化的工作流程、质量标准与领域知识，使 AI 能够可靠地完成头马相关任务。

---

## 📦 Skills | 技能清单

### 🧑‍🎓 Member Learning | 会员学习

#### Portable Toastmasters Learning Skills MVP

**Five member journeys, nine learning atomics, and one TM Companion routing skill**

**五条会员学习旅程、九个学习原子技能，以及一个 TM Companion 工具引导技能**

The MVP defines five journey skills:

- `navigate-pathways-learning`
- `prepare-toastmasters-speech`
- `perform-toastmasters-meeting-role`
- `give-and-apply-toastmasters-feedback`
- `practice-toastmasters-table-topics`

These journeys compose atomic skills for project interpretation, topic selection, outlining, draft review, rehearsal, Timer preparation, speech evaluation, feedback-to-practice planning, and Table Topics responses. Every skill also has a generated universal prompt for text-only use across general AI assistants.

本 MVP 定义五条会员学习旅程，并组合项目理解、主题选择、演讲提纲、讲稿评审、排练、计时员准备、个评、反馈转训练以及即兴演讲等原子技能。每个技能同时生成适用于多种通用 AI 助手的纯文本提示词。

- **Architecture:** [`design/portable-toastmasters-skills-mvp.md`](design/portable-toastmasters-skills-mvp.md)
- **Skill catalog:** [`catalog/skills.json`](catalog/skills.json)
- **TMCompanion action registry:** [`catalog/integrations.json`](catalog/integrations.json)
- **TM Companion tool finder:** [`skills/find-tmcompanion-tool/SKILL.md`](skills/find-tmcompanion-tool/SKILL.md) — a standalone, text-only route to one of the nine optional tools
- **Portable prompts:** [`prompts/`](prompts/)
- **Build/validate:** [`scripts/build_portable_prompts.py`](scripts/build_portable_prompts.py), [`scripts/validate_portable_skills.py`](scripts/validate_portable_skills.py)

Resource Center pages are deliberately not implemented in this MVP. Their future page IDs are reserved in the catalog so the website can consume the same canonical packages later.

**Generated prompts (15):**  `prompts/` 中每個技能都有 `.en.md`（英文）和可選的 `.zh.md`（中文）
```
answer-table-topics-question.en.md
build-speech-outline.en.md
choose-speech-topic.en.md
find-tmcompanion-tool.en.md
give-and-apply-toastmasters-feedback.en.md
navigate-pathways-learning.en.md
perform-toastmasters-meeting-role.en.md
practice-toastmasters-table-topics.en.md
prepare-speech-evaluation.en.md
prepare-timer-role.en.md
prepare-toastmasters-speech.en.md
rehearse-toastmasters-speech.en.md
review-speech-draft.en.md
turn-feedback-into-practice.en.md
understand-pathways-project.en.md
```

**Canonical skills (15):**
```
skills/{answer-table-topics-question, build-speech-outline, …}/SKILL.md + agents/openai.yaml
```

---

### Toastmasters Poster Production | 头马海报制作与评审

- [Poster Maker / 海报制作](skills/toastmasters-poster-maker/SKILL.md) · [中文](skills/toastmasters-poster-maker/SKILL.zh.md): intermediate layout → image-model rendering → exact overlays → independent review. Supplied portraits, documentary photos and QR codes are placed directly, outside generative rendering.
- [Poster Reviewer / 海报评审](skills/toastmasters-poster-reviewer/SKILL.md) · [中文](skills/toastmasters-poster-reviewer/SKILL.zh.md): standalone or maker quality gate; checks brand, copy, visual quality, protected materials and QR payloads. Design compliance and external authorization are separate.
- [Maker EN](prompts/toastmasters-poster-maker.en.md) · [制作中文](prompts/toastmasters-poster-maker.zh.md) · [Reviewer EN](prompts/toastmasters-poster-reviewer.en.md) · [评审中文](prompts/toastmasters-poster-reviewer.zh.md). Text-only tools provide briefs/handoffs; production and visual approval require the stated tools and a separate review session.
- **[Poster materials / 海报素材](materials/toastmasters-brand/README.md)**: direct official links and a saved [URL catalog](materials/toastmasters-brand/sources.json), so users never need to re-extract links from the PDF. Reuse existing local downloads first; browser downloads and supplied assets are supported. The fetch script is optional.
- [Canonical brand references](references/toastmasters-brand/) use the August 2026 manual. Original files can be reused from the private, Git-ignored `materials/toastmasters-brand/local/` folder; official rights are not covered by the repository MIT license.

素材保持私有，不重托管官方文件；两技能支持普通俱乐部/区域/中区/大区、企业俱乐部、Gavel及年度大会。可编辑SVG中的文字、素材及位置可调整，生成背景仍是栅格层。没有独立评审时仅交未经评审草稿，不自动申请批准或发布。

Maintain canonical references, then run `python3 scripts/sync_poster_references.py`, `python3 scripts/build_portable_prompts.py`, `python3 scripts/validate_portable_skills.py`, `python3 scripts/sync_poster_references.py --check`, and `python3 -m unittest discover -s tests`. Do not hand-edit generated prompt/reference copies.

---

### 🛠️ Officer Tools | 幹部工具

#### 1. PowerPoint Translation Redesign

**Translate PPTX decks while preserving their visual design**  
翻译 PPTX 演示文稿，同时保留其视觉设计

- **Path:** `skills/powerpoint-translation-redesign/`
- **Agent config:** `agents/openai.yaml`
- **Audit script:** `scripts/audit_pptx_text.py`

Translate and localize existing PowerPoint PPTX decks while preserving slide dimensions, layouts, editable shapes, images, charts, typography, brand cues, and design intent. Includes an audit script to detect remaining source-language text, repeated paragraphs, and missing fragments.

在保持幻灯片尺寸、布局、可编辑形状、图片、图表、版式、品牌元素和设计意图不变的前提下，对现有 PPTX 文件进行翻译和本地化。附带审核脚本，可检测残留源语言文本、重复段落及缺失片段。

---

#### 2. Poster Image Translation Redesign

**Edit raster images embedded in PPTX slides — translate and replace inline text**
编辑 PPTX 幻灯片中的栅格图片——翻译并替换内嵌文字

- **Path:** `skills/poster-image-translation-redesign/`
- **Agent config:** `agents/openai.yaml`
- **Terminology reference:** `references/toastmasters-terminology.md`

Extract, translate, and reinsert images containing text within PowerPoint slides. Preserve the asset frame, crop, position, and dimensions exactly. Supports mask-based text isolation and pixel-level QA. Referenced as a preprocessing step by the PowerPoint Translation Redesign skill.

提取、翻译并重新插入 PPTX 幻灯片中包含文字的栅格图片。精确保留图片的框架、裁切、位置和尺寸。支持基于遮罩的文字隔离与像素级质量校验。此技能作为 PowerPoint 翻译重设计流程的预处理环节被引用。

---

#### 3. Toastmasters Speech Coaching Team

**Holistic speech feedback from five AI roles**  
来自五个 AI 角色的全方位演讲反馈

- **Path:** `skills/toastmasters-speech-coaching-team/`
- **Agent config:** `agents/openai.yaml`

Create a virtual Toastmasters evaluation team for one prepared speech. Five distinct sub-agents take on the roles of **Coach**, **Individual Evaluator**, **Timer**, **Grammarian**, and **Ah-Counter**, each producing an independent report. The main agent then synthesizes their findings into holistic, prioritized feedback.

为一场备稿演讲组建虚拟头马点评团队。五个独立的子 AI 分别扮演**教练**、**个评**、**计时员**、**语法官**和**哼哈官**，各自生成独立报告，再由主 AI 综合得出具有优先级的全方位反馈。

---

#### 4. Toastmasters Meeting Agenda Team

**Reviewer-gated agenda creation in the source format**
经独立审核把关、保留源文件格式的会议议程生成

- **Path:** `skills/toastmasters-meeting-agenda-team/`
- **Agent config:** `agents/openai.yaml`
- **Agenda rules:** `references/agenda-requirements.md`

Create a print-ready Toastmasters meeting agenda through three distinct sub-agents: a **Visual Designer**, a **Content Reviewer**, and a **Visual Reviewer**. A non-PDF template or sample is duplicated, edited directly, and returned in the same file type; a PDF template or sample produces an editable DOCX; only when no source is supplied is the packaged DOCX fallback used. Any rejection returns the file for revision and full re-review; delivery is allowed only when both reviewers accept the same revision.

由三个独立子 AI 创建可打印的头马会议议程：**视觉设计师**、**内容审核员**与**视觉审核员**。非 PDF 模板或样例会先复制、再直接编辑，并以相同文件类型交付；PDF 模板或样例输出可编辑的 DOCX；只有未提供源文件时才使用内置 DOCX 模板。任一审核员拒绝时，文件必须返回设计师修订并重新完整审核；只有同一版本获得双重通过后才能交付。

---

## 🚀 Usage | 使用方式

### Universal Chat Prompts

The [`prompts/`](prompts/) folder contains copy-and-paste versions for general AI assistants such as Kimi, Claude, Gemini, DeepSeek, and ChatGPT. Unlike the agent skills, these prompts check the current platform's actual file, media, code, and editing capabilities before choosing a workflow. When a platform cannot create the requested artifact, the prompt defines a truthful text-based fallback.

`prompts/` 文件夹提供可直接复制到 Kimi、Claude、Gemini、DeepSeek、ChatGPT 等通用 AI 助手中的版本。与智能体技能不同，这些提示词会先确认当前平台实际具备的文件、媒体、代码和编辑能力，再选择工作流程；如果平台无法生成目标文件，则使用明确的文本交付方案。

For best results, paste only the reusable instruction section identified in each file, then add your own input using its example format.

为获得更稳定的效果，请仅复制每个文件中标明的可复用指令部分，再按照示例格式添加自己的材料。

Portable Toastmasters prompts under [`prompts/`](prompts/) are generated from the canonical skill catalog. Portability is a repository-wide promise, so generated and manually authored prompts share this folder. Generated files identify themselves in their headers and should not be edited manually. Regenerate and validate them with:

```bash
python3 scripts/validate_portable_skills.py
python3 scripts/build_portable_prompts.py
```

### Agent Skills

The `SKILL.md` packages can be used by compatible AI agents. The portable learning skills do not depend on native skill invocation; their generated prompts provide the text-only compatibility baseline.

#### Install all skills once | 一次安装全部技能

Copy this request into your skill-aware AI agent. If you already installed the complete collection in that client, skip installation and use the skills directly.

将以下请求复制到支持 Skills 安装的 AI 助手中。如果已在该客户端安装过完整技能库，可直接使用，无需重复安装。

```text
Please install all skills from https://github.com/YangRice/D85-AI-Resources
for this AI client. Preserve each complete skill folder, including its
scripts, references, assets, and agent configuration. Check dependencies
and client compatibility, then report the installed skills, installation
location, and any missing requirements. Keep a persistent checkout of the
complete repository, including its tracked materials, catalog, and shared
references, and report that location too. Private Git-ignored downloads
are not included; reuse existing authorized local assets or obtain them
from the bundled official links as needed. Tell me whether I need to restart
the client or open a new conversation before using them.
```

```text
请为当前 AI 客户端安装 https://github.com/YangRice/D85-AI-Resources
中的全部技能。保留每个技能的完整目录，包括脚本、参考资料、素材和
智能体配置。检查依赖和客户端兼容性，完成后报告已安装技能、安装位置
以及尚未满足的要求。同时保留完整仓库的持久本地副本，包括 Git 跟踪的
materials、catalog 和共享参考资料，并报告该副本的位置。私有且被 Git
忽略的下载文件不在仓库中；按需复用已有且有权使用的本地素材，或通过
内置官方链接获取。请说明使用前是否需要重启客户端或新建对话。
```

**Optional terminal installation / 可选终端安装:** With Node.js and npm available, use the external [Skills CLI](https://github.com/vercel-labs/skills). This repository does not contain a dedicated bulk installer.

安装了 Node.js 和 npm 后，也可使用外部 Skills CLI；本仓库不包含专用的批量安装脚本。

```bash
# Preview available skills without installing / 仅预览，不安装
npx skills add YangRice/D85-AI-Resources --list

# Install all skills; choose the target client interactively
# 安装全部技能，交互选择目标客户端
npx skills add YangRice/D85-AI-Resources --skill '*'

# Example: install globally for Hermes, across projects
# 示例：为 Hermes 全局安装，供所有项目使用
npx skills add YangRice/D85-AI-Resources --skill '*' --agent hermes-agent --global
```

Without `--global`, installation is scoped to the current project. Use `--agent` to select a supported client (for example, `hermes-agent`, `claude-code`, or `codex`). Keep `'*'` quoted so the shell does not expand it. The CLI's `--all` option installs to all supported agents as well as selecting all skills; use `--skill '*'` when you want to choose the client. Installation copies skill instructions and supporting files; workflow dependencies and tools still need to be available.

省略 `--global` 时，仅安装到当前项目。可用 `--agent` 指定受支持的客户端（如 `hermes-agent`、`claude-code` 或 `codex`）。请保留 `'*'` 的引号，避免被终端展开。CLI 的 `--all` 同时选择全部技能和全部受支持的客户端；如需选择客户端，请使用 `--skill '*'`。技能安装包含指令与配套文件，实际工作流所需的依赖和工具仍须另行满足。

**Materials coverage / 素材范围:** The CLI installs individual skill folders, not a persistent copy of the entire repository. Files inside each skill's `assets/`, `references/`, and `scripts/` are included; top-level `materials/`, `catalog/`, and shared `references/` are not. The poster skills bundle the brand rules, material guides, and official asset URL inventory needed for standalone use. To retain the complete tracked resource collection, keep a separate repository checkout:

CLI 安装的是各个技能目录，不会保留完整仓库副本。技能内部的 `assets/`、`references/` 和 `scripts/` 会包含在内；顶层的 `materials/`、`catalog/` 和共享 `references/` 不会。海报技能已内置独立使用所需的品牌规则、素材指南及官方链接目录。若需保留完整的 Git 跟踪资源，请另行保留仓库副本：

```bash
git clone https://github.com/YangRice/D85-AI-Resources.git
```

Actual downloaded logos, photos, fonts, and other originals under `materials/toastmasters-brand/local/` are private and Git-ignored. Neither the CLI nor a fresh clone includes these files. Reuse authorized local originals or download needed assets from the [saved official links](materials/toastmasters-brand/README.md).

`materials/toastmasters-brand/local/` 中已下载的标志、照片、字体等原件保持私有并被 Git 忽略；CLI 安装和新克隆均不包含这些文件。请复用已有且有权使用的本地原件，或从[已保存的官方链接](materials/toastmasters-brand/README.md)按需下载。

After installation, start a new conversation or reload the client if required. In Hermes, you can then view a skill with:

安装后，根据客户端要求新建对话或重新加载。在 Hermes 中，可通过以下方式查看技能：

```python
skill_manage(action='view', name='powerpoint-translation-redesign')

# Or load it from source
skill_view(name='powerpoint-translation-redesign')
```

### For PowerPoint Translation

```bash
# Run the audit script on a translated deck
python3 skills/powerpoint-translation-redesign/scripts/audit_pptx_text.py translated.pptx --language en
```

> **Note:** The audit script requires `python-pptx` (`pip install python-pptx`).

### For Speech Coaching

Provide the speech transcript, audio/video, project criteria, or any evaluation packet to the AI agent. The agent will dispatch five role sub-agents and return a structured evaluation report.

### For Meeting Agendas

Provide meeting rules, session order and timing, club information, and an agenda template or sample. The agent will dispatch the three agenda-team sub-agents and return the approved agenda in the source-derived format: the same file type as a non-PDF template or sample, DOCX for a PDF template or sample, or the packaged DOCX fallback only when no source is supplied.

---

## 📁 Repository Structure | 目录结构

```
D85 AI SKILLs resource/
├── catalog/
│   ├── skills.json                # Skill type, composition, version, page ID
│   └── integrations.json          # Optional TMCompanion action URLs
├── design/
│   └── portable-toastmasters-skills-mvp.md
├── prompts/                       # Portable prompts: <skill>.en.md + optional <skill>.zh.md
│   ├── <catalog-skill>.en.md      # Generated from canonical skill packages
│   ├── poster-image-translation-redesign.md
│   ├── powerpoint-translation-redesign.md
│   ├── toastmasters-speech-coaching-team.md
│   └── toastmasters-club-meeting-agenda-generator.md
├── scripts/
│   ├── build_portable_prompts.py
│   └── validate_portable_skills.py
└── skills/
    ├── <portable-learning-skill>/
    │   ├── SKILL.md
    │   └── agents/openai.yaml
    ├── poster-image-translation-redesign/
    │   ├── SKILL.md
    │   ├── agents/openai.yaml
    │   └── references/
    │       └── toastmasters-terminology.md
    ├── powerpoint-translation-redesign/
    │   ├── SKILL.md               # Skill definition & workflow
    │   ├── agents/openai.yaml     # Agent interface config
    │   └── scripts/
    │       └── audit_pptx_text.py # Translation audit script
    ├── toastmasters-speech-coaching-team/
    │   ├── SKILL.md               # Skill definition & workflow
    │   └── agents/openai.yaml     # Agent interface config
    └── toastmasters-meeting-agenda-team/
        ├── SKILL.md               # Multi-agent agenda workflow
        ├── agents/openai.yaml     # Agent interface config
        ├── assets/                  # Four fallback DOCX templates
        └── references/
            └── agenda-requirements.md
```

---

## 🛠️ Requirements | 环境要求

- Python 3.10+
- `python-pptx` (for the audit script)
- Any capable text-chat AI for universal prompts
- A compatible skill-aware AI agent only for native `SKILL.md` invocation

---

## 🤝 Contributing | 如何贡献

This is part of the **D85 AI Empowerment OKR** initiative. As a public resource, it is designed to be **handover-proof** — knowledge and workflows live here rather than in any one person's head.

Feel free to open issues or PRs for improvements, new skills, or bug fixes.

本仓库是 **D85 AI 赋能 OKR** 项目的一部分。作为公开资源，其设计目标是**换屆免疫**——知识与工作流程沉淀于此，而非任何个人脑中。

欢迎提交 Issue 或 PR 来改进、添加新技能或修复问题。

---

## 📄 License | 许可

MIT
