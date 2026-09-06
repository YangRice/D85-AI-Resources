# Translate PDF — Preserve the Original Design

Attach your PDF, paste the prompt below, and add `Translate to English` (or another target language). No skill installation is required.

---

Translate the attached PDF into the language I request, following this repository's extract → translate → replace-in-place workflow:
https://github.com/wshuyi/translate-pdf-skill

Read `skills/translate-pdf/SKILL.md` and its referenced Python scripts. Use the workflow with the tools available in this session; you do not need to install Claude Code. If Git cloning is unavailable, try reading the individual repository files through browsing and applying the inspected workflow with an available PyMuPDF installation. State whether you ran the original scripts or adapted them. If the needed code or library cannot be accessed, explain the limitation; do not claim the repository ran.

The PDF is the visual authority. Translate it, do not redesign it.

## Common Toastmasters terminology

For Toastmasters material translated into English, use these established terms consistently. Apply them only where the corresponding source content occurs; do not add absent projects or change the source program version. For other target languages, use the appropriate established terminology rather than forcing English.

- 必修 = Required; 选修 = Elective; 学习路径 = path; 项目 = project.
- 掌握基础 = Mastering Fundamentals; 了解风格 = Learning Your Style; 增长知识 = Increasing Knowledge; 培养技能 = Building Skills; 展示专业 = Demonstrating Expertise.
- 动态领导 = Dynamic Leadership; 愿景沟通 = Visionary Communication; 激励策略 = Motivational Strategies; 有说服力的影响 = Persuasive Influence; 精通演讲 = Presentation Mastery; 运用幽默 = Engaging Humor.
- 初试啼声 = Ice Breaker; 撰写带有目的性的演讲稿 = Writing a Speech with Purpose; 声音与肢体语言 = Introduction to Vocal Variety and Body Language; 评估与反馈 = Evaluation and Feedback.
- 了解你的领导风格 = Understanding Your Leadership Style; 了解你的沟通风格 = Understanding Your Communication Style; Toastmasters 导师计划 = Introduction to Toastmasters Mentoring; 反思你的学习路径 = Reflect on Your Path; 杰出会员 = Distinguished Toastmaster (DTM).

Preserve source acronyms such as TI, VPE, VPM, VPPR, SAA, TMoD, TTM, GE, DTM, and path codes. For unlisted projects, use the official target-language title when reliably established; otherwise translate consistently and flag unverified terminology in the delivery note. Never use terminology lookup to silently update source requirements.

Guardrails:

- Keep the original page count, page sizes, orientation, table geometry, positions, backgrounds, colors, rules, badges, logos, illustrations, and QR codes. Do not create a new overview, extra pages, or a reflowed guide. Never overwrite the source.
- Inspect the rendered PDF as well as extracted text. Translate complete phrases in context, joining extraction fragments where necessary. Track replacements by page and text region, not only by unique string. Preserve every number, duration, ID, name, contact detail, symbol, blank field, and table state. A blank cell must remain blank; never infer an elective or requirement. Preserve conflicting source values and flag the conflict separately.
- For specialized terminology, use established target-language names without updating the source's facts or program version. Preserve proper names unless an established translated form is known. Do not omit or summarize content to make it fit.
- Remove only the text being replaced. Inspect PyMuPDF's installed redaction API and explicitly preserve images and vector graphics; default redaction can damage intersecting table borders. Transparent fill alone is not sufficient protection. Never cover colored cells with white rectangles.
- Match the original font style, weight, color, alignment, baseline, rotation, and hierarchy as closely as possible. Measure the target-language text against its actual cell or text region. Preserve font size where it fits; otherwise adjust wrapping and spacing within that region, then use a modest, consistent size adjustment only if still readable. Do not blindly insert a longer translation at the original point or shrink individual labels unpredictably. If accurate, readable text cannot fit, report the specific conflict instead of changing the layout.
- Render every output page and compare it with the source at matching scale, both full-page and close-up. Check translation coverage, cell associations, readable typography, clipping, overlap, missing glyphs, stray text such as `Q&A;`, damaged rules, and changes outside the replaced text regions. Fix defects and render again after the last edit. Keep text searchable where the source permits.

Return the translated PDF with a brief note about checks actually performed, necessary font adjustments, source ambiguities, and any remaining limitations. Do not claim independent review unless a separate reviewer really inspected the output. If subagents are available, have an independent reviewer inspect the source and final PDF for both content and visual fidelity; fix rejections and obtain a fresh review. Otherwise perform an explicit self-check and label it as such. Do not describe an unresolved draft as finished.

---

Example request: `Translate to English.`
