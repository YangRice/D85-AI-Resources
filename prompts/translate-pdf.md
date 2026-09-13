# Translate PDF — Preserve the Original Design

Attach your PDF, paste the prompt below, and add `Translate to English` (or another target language). No skill installation is required.

---

Translate the attached PDF into the language I request, following this repository's extract → translate → replace-in-place workflow:
https://github.com/wshuyi/translate-pdf-skill

Read `skills/translate-pdf/SKILL.md` and its referenced Python scripts. Use the workflow with the tools available in this session; you do not need to install Claude Code. If Git cloning is unavailable, try reading the individual repository files through browsing and applying the inspected workflow with an available PyMuPDF installation. State whether you ran the original scripts or adapted them. If the needed code or library cannot be accessed, explain the limitation; do not claim the repository ran.

The PDF is the visual authority. Translate it, do not redesign it.

## Toastmasters terminology reference

For Toastmasters content, read the [shared terminology reference](https://github.com/YangRice/D85-AI-Resources/blob/main/skills/poster-image-translation-redesign/references/toastmasters-terminology.md) before translating. For Pathways project and path names, also read the [PDF translation terminology supplement](https://github.com/YangRice/D85-AI-Resources/blob/main/skills/translate-pdf/references/toastmasters-terminology.md). Use the target-language side of the relevant entries; do not force English terms into another target language. Apply only terms corresponding to source content, preserve acronyms, and do not update source requirements or program versions. If a reference cannot be accessed, disclose it and flag unverified terminology instead of claiming glossary compliance.

Guardrails:

- Keep the original page count, page sizes, orientation, table geometry, positions, backgrounds, colors, rules, badges, logos, illustrations, and QR codes. Do not create a new overview, extra pages, or a reflowed guide. Never overwrite the source.
- Inspect the rendered PDF as well as extracted text. Translate complete phrases in context, joining extraction fragments where necessary. Track replacements by page and text region, not only by unique string. Preserve every number, duration, ID, name, contact detail, symbol, blank field, and table state. A blank cell must remain blank; never infer an elective or requirement. Preserve conflicting source values and flag the conflict separately.
- For specialized terminology, use established target-language names without updating the source's facts or program version. Preserve proper names unless an established translated form is known. Do not omit or summarize content to make it fit.
- Remove only the text being replaced. Inspect PyMuPDF's installed redaction API and explicitly preserve images and vector graphics; default redaction can damage intersecting table borders. Transparent fill alone is not sufficient protection. Never cover colored cells with white rectangles.
- Match the original font style, weight, color, alignment, baseline, rotation, and hierarchy as closely as possible. Measure the target-language text against its actual cell or text region. Preserve font size where it fits; otherwise adjust wrapping and spacing within that region, then use a modest, consistent size adjustment only if still readable. Do not blindly insert a longer translation at the original point or shrink individual labels unpredictably. If accurate, readable text cannot fit, report the specific conflict instead of changing the layout.
- Render every output page and compare it with the source at matching scale, both full-page and close-up. Check translation coverage, cell associations, readable typography, clipping, overlap, missing glyphs, stray text such as `Q&A;`, damaged rules, and changes outside the replaced text regions. Fix defects and render again after the last edit. Keep text searchable where the source permits.

## Post-generation visual review and correction loop

After generating each candidate PDF, create an independent reviewer subagent if the environment supports it. Give it the original PDF, the exact candidate file, the target language, terminology references, and the preservation requirements above. The reviewer must inspect the actual rendered pages, not just the translation text or your summary. If subagents are unavailable, perform the same review yourself and explicitly label it as self-review; never simulate independent approval.

Review every page at matching full-page scale and readable close-up scale. Check both translation completeness and visual design: original page geometry, table layout, graphics, colors, borders, typography hierarchy, font-size consistency, alignment, line wrapping, and absence of clipping, overlap, missing glyphs, or unintended changes outside text regions. Record the candidate filename, pages inspected, `PASS` or `FAIL`, and each defect's page/region.

If the review fails, correct the defects without redesigning the PDF, generate a new candidate, rerender every page, and repeat the review. Any edit invalidates the previous pass. Deliver only the exact revision that passes both content and visual checks. If a required check is impossible, or the same defect remains after three revisions, stop and report the unresolved issue and required user decision or capability; do not call that a pass.

Return the translated PDF with a brief note about the final review result, whether it was independent or self-review, checks actually performed, necessary font adjustments, and source ambiguities. Do not describe an unresolved draft as finished.

---

Example request: `Translate to English.`
