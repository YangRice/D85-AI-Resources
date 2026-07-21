# Poster Image Translation and Correction Prompt

> Upload the original poster image and copy the prompt below into an AI assistant that can inspect and edit images.

---

## Prompt

Translate or correct all applicable text in the poster image into Simplified Chinese.

Follow these two requirements strictly:

### 1. Preserve the original visual design

Only replace the text that requires translation or correction. Preserve the original poster exactly, including:

- canvas dimensions, aspect ratio, resolution, and orientation;
- typography, including font appearance, size, weight, style, color, spacing, and alignment;
- photographs, illustrations, icons, logos, QR codes, and other visual assets;
- backgrounds, colors, gradients, textures, shadows, borders, and effects;
- composition, hierarchy, object positions, margins, and spacing.

Do not redesign, restyle, crop, stretch, replace, add, or remove any visual element. Do not alter faces, bodies, logos, QR codes, photographs, illustrations, or background details. Remove only the original text being translated, reconstruct the area behind it cleanly, and place the translated text in the same location while matching the original typography and visual treatment as closely as possible.

The visible length and line wrapping may naturally differ between English and Chinese, but the original design settings must remain unchanged. Translation accuracy takes priority over forcing text to fit. Never shorten, omit, or alter the meaning merely to fit the available space.

If an accurate translation cannot fit without changing the original design, do not change the design or meaning. Identify the affected text area for manual review. Do not allow text to overlap, overflow, become clipped, cover important artwork, or extend outside the canvas without reporting it.

### 2. Use the approved Toastmasters terminology

Use the following translations consistently. When alternatives are provided with `/`, use the first translation as the default. Use the alternative only when the context clearly requires it, and keep that choice consistent throughout the poster.

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

Translate complete phrases and sentences naturally and accurately rather than translating isolated words without context. Keep acronyms such as TI, VPE, VPM, VPPR, SAA, TMoD, TTM, GE, and DTM when they appear in the original.

Before delivery, compare the edited poster with the original and check for:

- incorrect terminology, untranslated text, missing text, or duplicated text;
- misspellings, garbled Chinese characters, or factual changes;
- mismatched typography, alignment, color, spacing, or text effects;
- visible traces of removed text or damaged background reconstruction;
- clipping, overflow, overlap, or text covering important visual content;
- unintended changes to images, logos, QR codes, backgrounds, or dimensions.

Correct any translation or image-editing problem without changing the original design or meaning. Flag any issue that cannot be resolved under these requirements for manual review.

Return the completed poster at the original dimensions and highest available quality, preferably as a PNG. Do not overwrite the original image. Briefly identify:

- any text area where an accurate translation does not fit without a design change;
- any text that could not be read or edited reliably; and
- whether the final poster was visually compared with the original.

---

## Example request

```text
Please translate or correct the attached poster image in Simplified Chinese. Follow the visual-preservation rules and approved Toastmasters terminology in this prompt. Return a high-quality PNG at the original dimensions.
```
