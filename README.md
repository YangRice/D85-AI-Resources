# D85 AI Resources

> District 85 Toastmasters — AI Empowerment OKR Skills Repository  
> 国际演讲会 85 大区 — AI 赋能 OKR 技能资源库

---

## 📖 Overview | 概述

This repository contains reusable skill definitions designed for **AI coding agents** (Hermes Agent, Claude Code, Codex, etc.) used in the **D85 AI Empowerment OKR** initiative. These skills encode structured workflows, quality gates, and domain-specific knowledge — enabling AI agents to reliably perform Toastmasters-related tasks.

本仓库包含为 **D85 AI 赋能 OKR** 项目设计的、供 AI 编程助手（Hermes Agent、Claude Code、Codex 等）使用的可复用技能定义。每个技能都编码了结构化的工作流程、质量标准与领域知识，使 AI 能够可靠地完成头马相关任务。

---

## 📦 Skills | 技能清单

### 1. PowerPoint Translation Redesign

**Translate PPTX decks while preserving their visual design**  
翻译 PPTX 演示文稿，同时保留其视觉设计

- **Path:** `skills/powerpoint-translation-redesign/`
- **Agent config:** `agents/openai.yaml`
- **Audit script:** `scripts/audit_pptx_text.py`

Translate and localize existing PowerPoint PPTX decks while preserving slide dimensions, layouts, editable shapes, images, charts, typography, brand cues, and design intent. Includes an audit script to detect remaining source-language text, repeated paragraphs, and missing fragments.

在保持幻灯片尺寸、布局、可编辑形状、图片、图表、版式、品牌元素和设计意图不变的前提下，对现有 PPTX 文件进行翻译和本地化。附带审核脚本，可检测残留源语言文本、重复段落及缺失片段。

---

### 2. Toastmasters Speech Coaching Team

**Holistic speech feedback from five AI roles**  
来自五个 AI 角色的全方位演讲反馈

- **Path:** `skills/toastmasters-speech-coaching-team/`
- **Agent config:** `agents/openai.yaml`

Create a virtual Toastmasters evaluation team for one prepared speech. Five distinct sub-agents take on the roles of **Coach**, **Individual Evaluator**, **Timer**, **Grammarian**, and **Ah-Counter**, each producing an independent report. The main agent then synthesizes their findings into holistic, prioritized feedback.

为一场备稿演讲组建虚拟头马点评团队。五个独立的子 AI 分别扮演**教练**、**个评**、**计时员**、**语法官**和**哼哈官**，各自生成独立报告，再由主 AI 综合得出具有优先级的全方位反馈。

---

## 🚀 Usage | 使用方式

These skills are designed for use with AI coding agents that support the **Hermes Agent skill system** (SKILL.md format):

```bash
# Enable a skill in your Hermes Agent session
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

---

## 📁 Repository Structure | 目录结构

```
D85 AI SKILLs resource/
└── skills/
    ├── powerpoint-translation-redesign/
    │   ├── SKILL.md               # Skill definition & workflow
    │   ├── agents/openai.yaml     # Agent interface config
    │   └── scripts/
    │       └── audit_pptx_text.py # Translation audit script
    └── toastmasters-speech-coaching-team/
        ├── SKILL.md               # Skill definition & workflow
        └── agents/openai.yaml     # Agent interface config
```

---

## 🛠️ Requirements | 环境要求

- Python 3.10+
- `python-pptx` (for the audit script)
- An AI coding agent that supports SKILL.md (Hermes Agent, etc.)

---

## 🤝 Contributing | 如何贡献

This is part of the **D85 AI Empowerment OKR** initiative. As a public resource, it is designed to be **handover-proof** — knowledge and workflows live here rather than in any one person's head.

Feel free to open issues or PRs for improvements, new skills, or bug fixes.

本仓库是 **D85 AI 赋能 OKR** 项目的一部分。作为公开资源，其设计目标是**换屆免疫**——知识与工作流程沉淀于此，而非任何个人脑中。

欢迎提交 Issue 或 PR 来改进、添加新技能或修复问题。

---

## 📄 License | 许可

MIT
