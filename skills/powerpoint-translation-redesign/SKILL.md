---
name: powerpoint-translation-redesign
description: Translate and localize existing PowerPoint PPTX decks while preserving slide dimensions, layouts, editable shapes, images, charts, typography, brand cues, and design intent. Use when Codex needs to translate a presentation into another language, repair a flawed translated deck, replace editable slide text without redesigning the source, handle text split across PowerPoint runs, or render and compare a translated deck for clipping, wrapping, overlap, and newly introduced overflow.
---

# PowerPoint Translation Redesign

## Core Rule

Treat the source deck as the visual reference. Keep slide size, slide order, masters, layouts, shapes, images, charts, colors, animations, and brand chrome unchanged unless the user explicitly requests a redesign.

Translate editable text at the shape, paragraph, or logical-label level. Do not blindly replace individual text runs: PowerPoint frequently splits one sentence across runs, and run-level replacement can duplicate, merge, or misassign text.

Use the installed `presentations` skill for PPTX inspection, editing, rendering, and visual QA. Follow its template-following rules because the source deck supplies the design.

## Workflow

1. Record the absolute source path, target language and locale, output path, slide count, slide dimensions, and any terminology that must remain untranslated.
2. Inspect the original deck before editing:
   - render every slide and create a contact sheet;
   - extract editable text by slide, shape, and paragraph;
   - distinguish editable text from text embedded in raster images;
   - record baseline overflow warnings from the original deck.
3. Build a translation map whose keys retain source context. Prefer stable identifiers such as slide number plus shape/paragraph position over a global source-string dictionary when repeated English labels require different translations.
4. Translate complete logical units. Preserve section numbers, hierarchy, bullets, hyperlinks, speaker-facing labels, acronyms, product names, and Toastmasters-specific terminology as appropriate.
5. Apply translations conservatively:
   - keep existing objects and formatting;
   - when a paragraph spans several runs, place the translated paragraph in the first suitable run and clear only the remaining text runs in that paragraph;
   - preserve intentional mixed formatting when it carries meaning;
   - do not inherit content from a known-bad translated deck. Use it only as a candidate translation source, then apply translations to a clean copy of the original.
6. Handle non-editable image text separately. Use the `image-translation-redesign` skill only for the affected raster asset, then replace that asset without changing its frame or crop.
7. Audit the exported PPTX:

   ```bash
   python3 <skill-dir>/scripts/audit_pptx_text.py <translated.pptx> --language en
   ```

   Review remaining source-language fragments, repeated paragraphs, missing text, and expected acronyms. The audit is a triage aid, not a substitute for visual inspection.
8. Render the translated deck and inspect every slide at readable size. Compare against the original for unexpected wrapping, clipped titles, overlaps, moved objects, altered hierarchy, and garbled characters.
9. Run the presentation overflow check on both source and output. Fix every warning introduced by translation. Do not claim success merely because the final deck has warnings that also existed in the source; inspect the rendered slides and document inherited warnings separately.
10. Prefer shortening a translation before shrinking type. Keep one-line banners and titles on one line. If a font change is unavoidable, use a compatible CJK font and preserve the original hierarchy.
11. Save a new output file. Do not overwrite the source or a prior translated version unless the user explicitly asks.

## Repairing an Existing Translation

Start again from the original deck whenever possible. Compare the flawed translation by slide and paragraph, reuse only trustworthy translations, and avoid copying its modified object structure. Check especially for:

- distinct source objects collapsed to the same translation;
- duplicated text caused by multiple runs;
- punctuation or hyphenation fragments missed by exact matching;
- merged mission statements or multi-line labels;
- long translated lines pushing later content below the canvas.

## Quality Bar

The result should look as though the original presentation designer produced the localized edition. The translated deck must introduce no new clipping or overflow, retain the source visual identity, contain no unexpected source-language text, and remain editable where the source was editable.

## Final Handoff

Tell the user the final PPTX path, target locale, slide count, terminology intentionally left untranslated, render/overflow QA result, and any remaining need for subject-matter proofreading. Link only the final deck unless previews or audit files were requested.
