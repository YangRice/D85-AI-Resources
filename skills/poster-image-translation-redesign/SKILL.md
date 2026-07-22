---
name: poster-image-translation-redesign
description: Translate or repair text in existing poster images into Simplified Chinese while preserving the source canvas, typography, composition, photographs, illustrations, logos, QR codes, backgrounds, and visual identity. Use when Codex must localize a PNG, JPEG, WebP, or other raster poster; correct a flawed translated poster; apply approved Toastmasters terminology; or produce a reviewer-gated poster through separate Poster Designer, Translation Reviewer, and Visual Reviewer subagents.
---

# Poster Image Translation Redesign

Translate the poster through three independent subagents. Keep the main agent as coordinator; never let the designer approve its own work or combine the reviewer roles.

## Require Independent Subagents

Assign three distinct subagents:

1. **Poster Designer** — translate and edit a copy of the source poster, then return the edited image and a text-change map.
2. **Translation Reviewer** — compare every source and translated text region for accuracy, completeness, spelling, context, and approved terminology.
3. **Visual Reviewer** — compare the source and output images for design fidelity, legibility, clean reconstruction, and unintended visual changes.

Use the platform's equivalent of independent agents, workers, sessions, or delegated tasks. Run both reviews independently and in parallel when possible. Do not reveal one reviewer's verdict to the other before both respond.

If three independent subagents are unavailable, stop and explain that the required review independence cannot be met. Do not simulate missing subagents or approval in the coordinator.

## Establish the Source Baseline

Inspect the source before delegation. Record:

- absolute source and output paths;
- source file type, pixel dimensions, orientation, color mode, and file size;
- target language and locale;
- all visible source text, grouped by region and reading order;
- immutable pixel masks covering only the source text regions authorized for editing, plus a checksum of the mask data;
- logos, QR codes, faces, photographs, illustrations, and other protected regions;
- illegible text, existing damage, clipping, or layout defects;
- a source checksum.

Never overwrite the source. Work from a copy and preserve the original dimensions and highest practical image quality. Use PNG for the final output unless the user requests another format.

For Toastmasters content, read [references/toastmasters-terminology.md](references/toastmasters-terminology.md) completely and include it in the shared brief. Use the first listed translation as the default; use an alternative only when context clearly requires it, then apply that choice consistently.

## Create the Shared Production Brief

Give all subagents the same source image and requirements:

```text
Source path:
Output path:
Source properties:
Target locale:
Text regions and reading order:
Immutable text-mask coordinates and checksum:
Protected visual regions:
Approved terminology:
Known source defects:
User-specific instructions:
```

Treat these as hard constraints:

- Change only text that requires translation or correction.
- Preserve canvas size, aspect ratio, resolution, orientation, composition, hierarchy, object positions, margins, and spacing.
- Preserve the appearance, size, weight, style, color, spacing, alignment, and effects of the original typography as closely as the source permits.
- Preserve photographs, faces, bodies, illustrations, icons, logos, QR codes, backgrounds, colors, gradients, textures, shadows, borders, and effects.
- Never shorten, omit, or alter meaning merely to fit. Translation accuracy takes priority.
- If accurate text cannot fit without changing the design, record the exact region for manual review instead of changing the design or meaning.
- Retain TI, VPE, VPM, VPPR, SAA, TMoD, TTM, GE, and DTM whenever the acronym appears in the source.
- Permit edits only inside the coordinator-defined text masks. Treat any required mask expansion or change as `BLOCKED` unless the user explicitly approves a revised scope.

## Dispatch the Poster Designer

Require the Poster Designer to use an image-editing workflow capable of inspecting the original at full resolution. When using Codex, follow the installed `imagegen` skill for image edits.

The Poster Designer must:

1. Translate complete phrases and sentences in context, not isolated OCR fragments.
2. Retain TI, VPE, VPM, VPPR, SAA, TMoD, TTM, GE, and DTM whenever they appear in the source.
3. Remove only the source text being replaced and reconstruct its immediate background cleanly.
4. Place the translation in the same region while matching the original typography and treatment as closely as possible.
5. Constrain generative or inpainting edits to the immutable coordinator-defined text masks. Composite edited regions onto the decoded source image so pixels outside those masks remain unchanged.
6. Avoid altering any protected or non-text region.
7. Export each attempt to a new versioned path such as `poster-zh-r01.png`; never overwrite a candidate revision.
8. Return the candidate path, SHA-256 checksum, echoed text-mask checksum, and a text-change map containing region, source text, translation, and any fit concern.

Do not accept a newly generated approximation of the poster. The source image remains the visual authority.

## Run Independent Reviews

Give both reviewers the source, immutable candidate path, candidate SHA-256, shared brief, coordinator-defined text masks and checksum, and designer's text-change map. Each reviewer must inspect the actual images rather than approving from the designer's summary.

Use these verdicts consistently:

- `ACCEPT` — no required or unresolved defect remains.
- `REJECT` — a correctable defect remains and another designer revision is required.
- `BLOCKED` — accurate translation and required visual preservation cannot both be achieved, source text is illegible, or the available tools cannot perform or verify a required edit.

### Translation Reviewer Contract

Require the Translation Reviewer to inspect every visible text region and return:

```text
ROLE: Translation Reviewer
REVISION: [versioned filename]
SHA256: [candidate checksum]
VERDICT: ACCEPT | REJECT | BLOCKED
CHECKS PASSED:
- ...
REQUIRED FIXES:
1. [region] defect; expected result
BLOCKING ITEMS:
- ...
EVIDENCE:
- ...
```

Return `REJECT` for a correctable mistranslation, changed meaning, inconsistent or unapproved terminology, missing or duplicated text, residual source text that should be translated, misspelling, garbled characters, omitted source acronym, or inaccurate text-change map. Return `BLOCKED` when the source cannot be read reliably or an accurate translation cannot fit under the hard design constraints. Return `ACCEPT` only when neither a required fix nor blocking item remains.

### Visual Reviewer Contract

Require the Visual Reviewer to compare the source and output at full readable resolution and return:

```text
ROLE: Visual Reviewer
REVISION: [versioned filename]
SHA256: [candidate checksum]
VERDICT: ACCEPT | REJECT | BLOCKED
CHECKS PASSED:
- ...
REQUIRED FIXES:
1. [region] visible defect; expected result
BLOCKING ITEMS:
- ...
EVIDENCE:
- ...
```

Compare decoded source and output pixels outside the approved text masks. Require zero unexplained differences outside those masks. Decode every QR code in both images and require identical payloads; also compare protected QR regions visually.

Return `REJECT` for a correctable change to dimensions, crop, composition, typography hierarchy, colors, spacing, alignment, background reconstruction, clipping, overflow, overlap, covered artwork, or any unexplained pixel difference outside approved text masks. Return `BLOCKED` when the required edit cannot be made without changing a protected region or when QR integrity cannot be verified. Return `ACCEPT` only when neither a required fix nor blocking item remains.

## Enforce the Rejection Loop

Deliver only after both reviewers accept the same immutable output revision and echo its identical filename and SHA-256.

If either reviewer returns `BLOCKED`, stop immediately and produce the blocked handoff below. Do not send a blocked candidate through further revisions unless the blocker can be resolved without relaxing the user's constraints.

If either reviewer returns `REJECT`:

1. Consolidate every required fix without weakening or omitting a defect.
2. Return the current image, evidence, and complete fix list to the Poster Designer.
3. Require a new versioned output path, checksum, echoed unchanged text-mask checksum, and updated text-change map.
4. Send the new revision to both reviewers for fresh independent reviews.
5. Repeat until both reviewers return `ACCEPT` on that exact revision.

Invalidate all earlier approvals whenever the output changes. Do not patch an approved image after review. If a subagent fails its contract, replace that role with a fresh subagent and repeat the affected stage.

If the same required defect remains after three consecutive candidate revisions, classify the workflow as `BLOCKED` and stop without claiming completion.

## Blocked Handoff

When blocked, return no final or approved poster. Report:

- the latest candidate path, revision, and SHA-256;
- each unresolved region and constraint conflict;
- both reviewers' latest verdicts and evidence;
- the specific manual edit or missing capability required to continue.

## Deliver

Before handoff, recompute the accepted candidate SHA-256 and confirm that it matches the checksum echoed by both reviewers. Confirm that its dimensions match the source, the source checksum is unchanged, no unexplained pixel differences exist outside approved text masks, and every QR payload matches.

Return:

- the final poster path and format;
- source and output pixel dimensions;
- the number of design-review cycles;
- both reviewers' final `ACCEPT` verdicts;
- any source text intentionally left unchanged and the approved reason.

Do not deliver or describe the poster as complete when either reviewer rejected or blocked the final revision, the reviewer checksums differ, or any required or unresolved edit remains.
