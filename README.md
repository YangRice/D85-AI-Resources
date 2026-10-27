# D85 AI Resources

> District 85 Toastmasters — AI Empowerment OKR Skills Repository  
> 国际演讲会 85 大区 — AI 赋能 OKR 技能资源库

---

## 📖 Overview | 概述

This repository contains reusable skill definitions designed for **AI coding agents** (Hermes Agent, Claude Code, Codex, etc.) used in the **D85 AI Empowerment OKR** initiative. These skills encode structured workflows, quality gates, and domain-specific knowledge — enabling AI agents to reliably perform Toastmasters-related tasks.

本仓库包含为 **D85 AI 赋能 OKR** 项目设计的、供 AI 编程助手（Hermes Agent、Claude Code、Codex 等）使用的可复用技能定义。每个技能都编码了结构化的工作流程、质量标准与领域知识，使 AI 能够可靠地完成头马相关任务。

---

## 📦 Skills | 技能清单

### Visual editing | 手动编辑设计

- [`edit-svg-canvas`](skills/edit-svg-canvas/SKILL.md): say “let me edit this design myself” or “我要自己改文字／調整位置” to choose a suitable built-in canvas or the local Method Draw editor. Method Draw uses **Save and finish** to return a new SVG revision and requires Python 3.10+ and local browser/server access. This standalone package works independently of poster production or brand review.

- 独立通用技能，不限于海报。完整复制 `skills/edit-svg-canvas/`（包括 `scripts/`），仅复制提示词无法运行；安装后可通过自然语言调用，无需用户知道 SVG 或编辑器名称。


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

### Poster skills retired | 海报技能退役

`toastmasters-poster-maker` and `toastmasters-poster-reviewer` are retired from this collection, including their generated prompts. D85 cannot consistently substantiate the brand-compliance assurance implied by these workflows. Use [official resources and templates](materials/toastmasters-brand/README.md) for brand guidance; saved references are historical guidance snapshots, not official approval or a maintained compliance service. Previous implementations remain in Git history.

本集合已移除海报制作与评审技能及其生成提示词：D85 无法持续为这些流程所暗示的品牌合规保证提供充分依据。品牌指导请使用[官方资源与模板](materials/toastmasters-brand/README.md)；保存资料为历史指导快照，不代表官方批准或持续维护的合规服务。旧实现保留在 Git 历史中。

The independent [SVG editor](skills/edit-svg-canvas/SKILL.md) remains available. Retirement does not uninstall existing local copies; remove retired IDs deliberately at their recorded installation scope if desired.

独立的 [SVG 编辑器](skills/edit-svg-canvas/SKILL.md)继续保留。退役不会自动卸载本地旧副本；如需移除，请按记录的安装位置与范围操作。

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

**Translate existing posters and text-bearing slide images**
翻译现有海报及幻灯片中的含文字图片

- **Path:** `skills/poster-image-translation-redesign/`
- **Agent config:** `agents/openai.yaml`
- **Terminology reference:** `references/toastmasters-terminology.md`

Translate an existing poster into the requested language (default Simplified Chinese), preserving its design. Also supports raster assets extracted by the PowerPoint workflow. Uses its own source-preservation and editable-output instructions, the independent `edit-svg-canvas` package, and installed `gpt-taste` static visual guidance. It does not assess or certify Toastmasters brand compliance; `gpt-taste` is an external prerequisite. One independent translation/visual review round; failed checks return a draft and findings without automatic iteration. Deliver PNG, editable SVG and a tested **Edit this poster** link together; disclose unavailable capabilities.

按指定语言翻译现有海报（默认简体中文），保留原设计；也可处理 PowerPoint 流程提取的栅格图片。需安装独立 `edit-svg-canvas` 及外部 `gpt-taste`；本流程不评定或保证头马品牌合规，仅采用其静态视觉原则。独立翻译和视觉评审各一次，未通过则交付草稿及问题，不自动循环。PNG、可编辑 SVG 与已测试的编辑入口须一起提供；能力缺失须如实说明。

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
and client compatibility. Report selected and installed skill IDs, active
installation location and scope, source revision when available, observed
client discovery/loading evidence (or explicitly unverified), missing
workflow requirements, and any required restart or new conversation.
A retained repository checkout is optional for ordinary installation.
If I request the complete tracked resource collection, also retain a checkout
with materials, catalog, and shared references; report its location separately.
Private Git-ignored downloads are excluded. Reuse authorized local assets or
obtain them from the bundled official links as needed. Distinguish file
presence, client loading, a harmless first task, and advanced workflow readiness;
never mark an untested step as passed.
```

```text
请为当前 AI 客户端安装 https://github.com/YangRice/D85-AI-Resources
中的全部技能。保留每个技能的完整目录，包括脚本、参考资料、素材和
智能体配置。检查依赖和客户端兼容性，报告所选及已安装技能 ID、实际
安装位置和范围、可取得的来源版本、已观察到的客户端发现／加载证据
（或明确标为未验证）、缺少的工作流条件，以及是否需要重启或新建对话。
普通安装可选择是否保留仓库副本；若我要求完整的 Git 跟踪资源库，
则须另行保留包含 materials、catalog 和共享参考资料的仓库副本，
并单独报告其位置。私有且被 Git 忽略的下载文件不包含在内。
按需复用有权使用的本地素材，或通过内置官方链接获取。
请区分文件存在、客户端加载、无害的首次任务成功和进阶工作流就绪；
未测试的步骤不得标为通过。
```

**Optional terminal installation / 可选终端安装:** With a compatible Node.js/npm toolchain, use the external [Skills CLI](https://github.com/vercel-labs/skills). Examples below pin released version `1.7.2` (Node `>=22.20.0`). This repository does not contain a dedicated bulk installer. These are documented routes; installation alone does not verify client loading or task readiness. See the [installation guide](docs/installation.md) for evidence levels, capability requirements, selective installs and maintenance.

有兼容的 Node.js/npm 环境时，也可使用外部 Skills CLI；以下示例固定为已发布的 `1.7.2`（Node `>=22.20.0`）。本仓库不包含专用批量安装器。这些是已记录的路线；安装本身不等于已验证客户端加载或任务就绪。[安装指南](docs/installation.md)说明证据层级、能力要求、选择安装和维护方式。

```bash
# Preview available skills without installing / 仅预览，不安装
npx skills@1.7.2 add YangRice/D85-AI-Resources --list

# Install all skills; choose the target client interactively
# 安装全部技能，交互选择目标客户端
npx skills@1.7.2 add YangRice/D85-AI-Resources --skill '*'

# Example: install globally for Hermes, across projects
# 示例：为 Hermes 全局安装，供所有项目使用
npx skills@1.7.2 add YangRice/D85-AI-Resources --skill '*' --agent hermes-agent --global
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

**First use:** In a fresh session, explicitly ask for `build-speech-outline` using a harmless fictional topic, a three-minute limit and a supplied message. Ask the agent to show client-provided loading evidence or state that loading is unverified. Record the result separately from package presence. Successful text guidance does not verify poster, agenda, PDF or PPTX production. The [guide](docs/installation.md) includes update/removal and troubleshooting.

**首次使用：** 在新对话中明确调用 `build-speech-outline`，提供无害的虚构主题、三分钟时限和主旨。请助手展示客户端提供的加载证据，或明确说明加载未验证；将任务结果与文件存在分开记录。文字指导成功不代表海报、议程、PDF 或 PPTX 制作已验证。[指南](docs/installation.md)包含更新、移除和故障排查。

### For PowerPoint Translation

```bash
# Run the audit script on a translated deck
python3 skills/powerpoint-translation-redesign/scripts/audit_pptx_text.py translated.pptx --language en
```

> **Note / 注意：** This text-audit helper uses Python's standard-library ZIP/XML tools; it does **not** require `python-pptx`. Full translation requires the separately installed `presentations` skill, editing/rendering tools and three independent subagents. 此文字审计脚本仅用 Python 标准库，无须 `python-pptx`；完整翻译须另装 `presentations` 技能，并具备编辑／渲染工具及三个独立子代理。

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
│   ├── validate_skill_packages.py # All tracked packages; static checks only
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

Text guidance and universal prompts need a capable text-chat AI; they do not universally require Python. Native `SKILL.md` invocation needs a compatible client. File production, independent reviewers, image tools, rendering and local editing have workflow-specific requirements; see the bilingual [capability table](docs/installation.md#workflow-requirements--工作流要求). Installing packages does not install those tools.

文字指导及通用提示词需要有相应能力的文字 AI，不统一要求 Python；原生调用 `SKILL.md` 需要兼容客户端。文件制作、独立评审、图像工具、渲染和本地编辑的条件因工作流而异，详见双语[能力表](docs/installation.md#workflow-requirements--工作流要求)。安装技能包不会自动安装这些工具。

Maintainers / 维护者：`python3 scripts/validate_skill_packages.py` checks every tracked package; `python3 scripts/validate_portable_skills.py` separately checks the portable catalog. The reviewed baseline `1af81e05` had 23 packages with 18 portable entries; this revision has 24 packages and 19 entries, and the same five packages remain outside the catalog as distributed skills. Both commands are local static validation, not client or workflow certification. See the [guide](docs/installation.md#maintainer-checks--维护检查) for clean-export checks and the [re-check record](design/skills-installation-recheck-2026-10-16.md) for the counts and outputs observed at this revision.

前者覆盖所有 Git 跟踪技能包，后者单独检查便携目录。受审基线 `1af81e05` 有 23 个包、18 个便携条目；退役后为 22 个包、17 个便携条目，目录外的仍是同样五个技能，仍会分发。两者均为本地静态检查，不证明客户端加载或完整工作流成功。干净导出的检查方式见[指南](docs/installation.md#maintainer-checks--维护检查)，本版本的计数与输出见[复查记录](design/skills-installation-recheck-2026-10-16.md)。

---

## 🤝 Contributing | 如何贡献

This is part of the **D85 AI Empowerment OKR** initiative. As a public resource, it is designed to be **handover-proof** — knowledge and workflows live here rather than in any one person's head.

Feel free to open issues or PRs for improvements, new skills, or bug fixes.

**No coding or Git knowledge required:** use [D85 Skill Contributor](skills/d85-skill-contributor/SKILL.md) to prepare a local skill or prompt, walk through two small tests, and submit a GitHub PR when tools and authentication allow. Text-only assistants provide an explicitly unsubmitted handoff. See the [contribution guide](CONTRIBUTING.md) and [portable English prompt](prompts/d85-skill-contributor.en.md).

The skill explains the full journey but ends at PR submission. Submission is only the first step toward acceptance; the D85 team handles review, approval, merge, and any website publication.

本仓库是 **D85 AI 赋能 OKR** 项目的一部分。作为公开资源，其设计目标是**换屆免疫**——知识与工作流程沉淀于此，而非任何个人脑中。

欢迎提交 Issue 或 PR 来改进、添加新技能或修复问题。

**不懂编程或 Git 也可以贡献：**使用 [D85 技能贡献者](skills/d85-skill-contributor/SKILL.zh.md)，整理本地技能或提示词、完成两个小测试，并在工具与登录条件允许时提交 GitHub PR。纯文字助手提供明确标注为尚未提交的交接材料。参阅[贡献指南](CONTRIBUTING.md)与[中文便携提示词](prompts/d85-skill-contributor.zh.md)。

该技能说明完整流程，但以提交 PR 为终点。投稿只是接纳流程的第一步，后续审核、批准、合并及网站发布由 D85 团队处理。

---

## 📄 License | 许可

MIT
