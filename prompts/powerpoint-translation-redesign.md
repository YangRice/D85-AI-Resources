# PowerPoint Translation and Correction Prompt

> Upload the PowerPoint file and copy the prompt below into an AI assistant that can edit PPTX files.

---

## Prompt

Translate or correct the PowerPoint presentation in Simplified Chinese.

Follow these two requirements strictly:

### 1. Preserve all visual-design settings

Only translate or correct the text. Preserve the original presentation exactly, including:

- fonts, font sizes, font styles, and font colors;
- pictures, icons, logos, charts, and other visual assets;
- backgrounds, colors, themes, and branding;
- slide size, slide order, layouts, positions, spacing, and alignment;
- shapes, borders, effects, animations, and transitions.

Do not redesign, restyle, replace, add, or remove any visual element. Do not change the font or other design settings to accommodate the translation. Do not overwrite the original file; save the result as a new PPTX file.

The visible length and line wrapping of the text may naturally differ between English and Chinese, but the original design settings must remain unchanged. Translation accuracy takes priority over forcing text to fit. Never shorten, omit, or alter the meaning merely to fit a text box.

If an accurate translation cannot fit without changing the original design settings, do not change the design or meaning. Identify the affected slide and text box for manual review. Do not allow text to overlap, overflow, or become clipped without reporting it.

### 2. Use the approved Toastmasters terminology

Use the following translations consistently. When alternatives are provided with `/`, use the first translation as the default. Use the alternative only when the context clearly requires it, and keep that choice consistent throughout the presentation.

| English | Approved Chinese translation |
|---|---|
| Toastmasters International (TI) | 国际头马 / Toastmasters 国际演讲会 |
| Toastmasters Club | 演讲俱乐部 / 头马俱乐部（“头马”是会员圈常用简称） |
| Club Meeting | 俱乐部会议 |
| Meeting Role | 会议角色 |
| Club Officer | 俱乐部官员 |
| Club President | 主席 |
| Vice President Education (VPE) | 教育副主席 |
| Vice President Membership (VPM) | 会员副主席 |
| Vice President Public Relations (VPPR) | 公关副主席 |
| Secretary | 秘书长 |
| Treasurer | 财务 / 财务官 |
| Sergeant at Arms (SAA) | 接待官 |
| Toastmaster of the Day (TMoD / Toastmaster) | 会议主持人 / 当日主持 |
| General Evaluator (GE) | 总评 |
| Evaluator | 点评人 |
| Individual Evaluator | 个人点评人 |
| Speech Evaluator | 演讲点评人 / 个人点评人 |
| Prepared Speech | 备稿演讲 |
| Speaker | 演讲者 / 演讲人 |
| Table Topics | 即兴演讲 |
| Table Topics Master (TTM) | 即兴演讲主持人 |
| Timer | 时间官 |
| Grammarian | 语言官（中文俱乐部常用译法） |
| Ah-Counter | 哼哈官 |
| Word of the Day | 每日一词 |
| Guest | 来宾 |
| New Member | 新会员 |
| Induction | 入会仪式 |
| Ice Breaker Speech | 破冰演讲 |
| Pathways | 学习路径 |
| Project | 项目 |
| Level | 阶段 |
| Evaluation | 点评 |
| Feedback | 反馈 |
| Contest | 演讲比赛 |
| International Speech Contest | 国际演讲比赛 |
| Humorous Speech Contest | 幽默演讲比赛 |
| Table Topics Contest | 即兴演讲比赛 |
| Distinguished Toastmaster (DTM) | 杰出演讲会会员（DTM） |

Translate complete sentences naturally and accurately rather than translating isolated fragments. Keep acronyms such as TI, VPE, VPM, VPPR, SAA, TMoD, TTM, GE, and DTM when they appear in the source.

Before delivery, check every slide for incorrect terminology, untranslated text, missing or duplicated text, garbled characters, clipping, overflow, and overlap. Correct any translation problems without changing the visual design or meaning. Flag any fit problem that cannot be resolved under these requirements for manual review.

Return the corrected presentation as a new, editable PPTX file. Briefly identify:

- any slide or text box where an accurate translation does not fit without a design change; and
- any text that could not be edited because it is embedded inside an image.

---

## Example request

```text
Please translate or correct the attached PowerPoint in Simplified Chinese. Follow the visual-preservation rules and approved Toastmasters terminology in this prompt. Return a new, editable PPTX file.
```
