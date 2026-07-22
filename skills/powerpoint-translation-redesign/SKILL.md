---
name: powerpoint-translation-redesign
description: Translate or repair existing PowerPoint PPTX decks into Simplified Chinese while preserving slide dimensions, masters, layouts, editable shapes, images, charts, typography, branding, and visual identity. Use when Codex must localize a presentation, repair a flawed translation, apply approved Toastmasters terminology, handle text split across PowerPoint runs, or produce a reviewer-gated translated deck through separate Presentation Designer, Translation Reviewer, and Visual Reviewer subagents.
---

# PowerPoint Translation Redesign

Translate the deck through three independent subagents. Keep the main agent as coordinator; never let the designer approve its own work or combine the reviewer roles.

## Require Independent Subagents

Assign three distinct subagents:

1. **Presentation Designer** — translate and edit a clean copy of the source PPTX, render every slide, and return the deck plus a text-change map.
2. **Translation Reviewer** — inspect extracted source and output text for accuracy, completeness, spelling, context, acronyms, and approved terminology.
3. **Visual Reviewer** — compare every rendered source and output slide for design fidelity, legibility, clipping, overflow, overlap, and unintended changes.

Run both reviews independently and in parallel when possible. Do not reveal one reviewer's verdict to the other before both respond. If three independent subagents are unavailable, stop and explain that the required review independence cannot be met; do not simulate approval in the coordinator.

Use the installed `presentations` skill for PPTX inspection, editing, rendering, and visual QA. Treat the source deck as the visual authority.

## Establish the Source Baseline

Before delegation, record:

- absolute source and output paths, target locale, and source SHA-256;
- slide count, dimensions, order, masters, layouts, and theme;
- editable text by slide, shape, paragraph, and logical unit;
- text embedded in raster images, with each extracted asset's SHA-256, slide location, frame, crop, position, and dimensions;
- hyperlinks, speaker notes, acronyms, mixed formatting, and protected brand terms;
- rendered source slides and a contact sheet;
- baseline clipping, overflow, overlap, missing-glyph, or rendering warnings.

Never overwrite the source or a prior candidate. Start repairs from the original deck whenever possible; use a flawed translated deck only as a candidate text source, never as the object-structure authority.

For Toastmasters content, read [references/toastmasters-terminology.md](references/toastmasters-terminology.md) completely and include it in the shared brief. Use the first listed translation as the default; use an alternative only when context clearly requires it, then apply that choice consistently.

## Preprocess Embedded Image Text

Complete this stage before dispatching the three PowerPoint subagents so the poster team and PowerPoint team do not compete for agent slots.

For each raster asset containing text that must change:

1. Extract the original asset without resampling and record its SHA-256 plus slide frame, crop, position, and dimensions.
2. Run the `poster-image-translation-redesign` skill as a separate coordinator-led workflow.
3. Continue only when both poster reviewers accept the same immutable asset revision and SHA-256.
4. Record the accepted asset path and SHA-256, immutable text-mask checksum, both poster reviewer `ACCEPT` verdicts, pixel-difference result, and QR verification result.
5. Finish and release the poster subagents before dispatching the PowerPoint team.

If any required raster asset is `REJECTED` or `BLOCKED`, stop the PowerPoint workflow and return that poster workflow's blocked evidence. Do not insert an unapproved or manually patched raster asset.

## Create the Shared Production Brief

Give all three subagents the same source artifacts and constraints:

```text
Source path and SHA-256:
Target locale:
Slide properties:
Extracted text inventory:
Embedded-image text:
Accepted raster assets and SHA-256 values:
Raster mask checksums and poster-review evidence:
Protected terms and acronyms:
Approved terminology:
Baseline render and warnings:
Output naming and path:
User-specific instructions:
```

Treat these as hard constraints:

- Change only text that requires translation or correction.
- Preserve slide size, order, masters, layouts, shapes, positions, spacing, alignment, images, charts, logos, colors, backgrounds, themes, branding, effects, animations, and transitions.
- Preserve font family, size, weight, style, color, alignment, and hierarchy. Do not change fonts to accommodate Chinese.
- Translate complete logical units, not isolated PowerPoint runs.
- Never shorten, omit, or alter meaning merely to fit. Translation accuracy takes priority.
- Retain TI, VPE, VPM, VPPR, SAA, TMoD, TTM, GE, and DTM whenever the acronym appears in the source.
- Treat an accurate translation that cannot fit, render, or display without changing design settings as `BLOCKED`.

## Dispatch the Presentation Designer

Require the Presentation Designer to:

1. Duplicate the original PPTX and edit only the duplicate.
2. Build a contextual translation map keyed by slide plus shape/paragraph position, not only source strings.
3. Replace text at the paragraph or logical-label level. When one paragraph spans several runs, place the translation in the first suitable run and clear only the remaining text runs in that paragraph.
4. Preserve intentional mixed formatting, bullets, hierarchy, section numbers, hyperlinks, speaker notes, acronyms, and brand terms.
5. Keep all original objects and design settings unchanged.
6. Replace each affected raster asset only with the exact coordinator-supplied, dual-approved asset bytes. Preserve its frame, crop, position, and dimensions; never regenerate, resample, or patch it inside the deck workflow.
7. Export each attempt to a new versioned path such as `deck-zh-r01.pptx`; never overwrite a candidate revision.
8. Compute the candidate SHA-256, run the audit script, render every output slide, and run source/output overflow checks.
9. Return the candidate path and checksum, render paths, audit results, overflow results, text-change map keyed by slide and shape, and extracted embedded-asset hashes proving that every inserted raster matches its accepted asset SHA-256.

Run the text audit as a triage aid, not a substitute for review:

```bash
python3 <skill-dir>/scripts/audit_pptx_text.py <candidate.pptx> --language en
```

## Run Independent Reviews

Give both reviewers the source, immutable candidate path and SHA-256, extracted text inventories, source and output renders, audit results, overflow results, shared brief, text-change map, accepted raster evidence, and candidate embedded-asset hashes. Require each reviewer to inspect the actual artifacts.

Use these verdicts:

- `ACCEPT` — no required or unresolved defect remains.
- `REJECT` — a correctable defect remains and another designer revision is required.
- `BLOCKED` — accurate translation and required design preservation cannot both be achieved, source content is unreadable, or available tools cannot perform or verify a required edit.

### Translation Reviewer Contract

Require this response:

```text
ROLE: Translation Reviewer
REVISION: [versioned filename]
SHA256: [candidate checksum]
VERDICT: ACCEPT | REJECT | BLOCKED
CHECKS PASSED:
- ...
REQUIRED FIXES:
1. [slide and shape] defect; expected result
BLOCKING ITEMS:
- ...
EVIDENCE:
- ...
```

Return `REJECT` for correctable mistranslation, changed meaning, inconsistent or unapproved terminology, missing or duplicated content, untranslated source text, garbled characters, omitted acronyms, incorrect notes or hyperlinks, inaccurate text-change maps, missing poster approval evidence, or a candidate embedded-asset hash that differs from the accepted raster SHA-256. Return `BLOCKED` when the source cannot be read reliably or accurate text cannot fit or render under the hard design constraints. Return `ACCEPT` only when neither a required fix nor blocking item remains.

### Visual Reviewer Contract

Require this response:

```text
ROLE: Visual Reviewer
REVISION: [versioned filename]
SHA256: [candidate checksum]
VERDICT: ACCEPT | REJECT | BLOCKED
CHECKS PASSED:
- ...
REQUIRED FIXES:
1. [slide and region] visible defect; expected result
BLOCKING ITEMS:
- ...
EVIDENCE:
- ...
```

Require the Visual Reviewer to compare every source and output slide at readable size and inspect slide dimensions, object positions, fonts, hierarchy, wrapping, clipping, overflow, overlap, missing glyphs, charts, images, logos, backgrounds, and visual balance. For every translated raster asset, verify the candidate PPTX embeds bytes matching the accepted asset SHA-256 and preserves the source frame, crop, position, and dimensions; confirm the carried poster evidence includes both `ACCEPT` verdicts, unchanged mask checksum, clean outside-mask pixel comparison, and matching QR payloads. Distinguish inherited source defects from newly introduced defects. Return `REJECT` for any correctable regression and `BLOCKED` for an unavoidable conflict with the hard constraints. Return `ACCEPT` only when neither a required fix nor blocking item remains.

## Enforce the Rejection Loop

Deliver only after both reviewers accept the same immutable candidate filename and SHA-256.

If either reviewer returns `BLOCKED`, stop immediately and produce the blocked handoff below.

If either reviewer returns `REJECT`:

1. Consolidate all required fixes without weakening or omitting a defect.
2. Return the candidate, evidence, and full fix list to the Presentation Designer.
3. Require a new versioned PPTX, SHA-256, full rendering, audit results, overflow results, and updated text-change map.
4. Send the new revision to both reviewers for fresh independent reviews.
5. Repeat until both return `ACCEPT` on that exact revision.

Invalidate all earlier approvals whenever the PPTX changes. Do not patch an approved deck after review. If the same required defect remains after three consecutive candidate revisions, classify the workflow as `BLOCKED` and stop without claiming completion.

## Blocked Handoff

When blocked, return no final or approved deck. Report:

- the latest candidate path, revision, and SHA-256;
- each unresolved slide, shape, and constraint conflict;
- both reviewers' latest verdicts and evidence;
- the specific manual edit or missing capability required to continue.

## Deliver

Recompute the accepted candidate SHA-256 and confirm that it matches both reviewer reports. Confirm the source checksum is unchanged and the delivered PPTX is the exact accepted revision.

Return:

- final PPTX path, target locale, slide count, and candidate SHA-256;
- audit and overflow results;
- the number of design-review cycles;
- both reviewers' final `ACCEPT` verdicts;
- any source text intentionally left unchanged and the approved reason.

Do not deliver or describe the deck as complete when either reviewer rejected or blocked the final revision, the reviewer checksums differ, or any required or unresolved edit remains.
