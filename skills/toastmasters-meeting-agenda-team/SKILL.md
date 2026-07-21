---
name: toastmasters-meeting-agenda-team
description: "Create, revise, and quality-gate a Toastmasters club meeting agenda using three distinct sub-agents: a Visual Designer, a Content Reviewer, and a Visual Reviewer. Use when a user supplies meeting rules, a session sequence, club details, and optionally an agenda template or sample. Preserve a non-PDF source's native format, convert a PDF source to editable DOCX, or use the packaged DOCX fallback; require independent content and visual approval before delivery."
---

# Toastmasters Meeting Agenda Team

Create the agenda through independent design and review roles. Keep the main agent as coordinator; do not let it impersonate any required role.

## Require Independent Agents

Assign three distinct sub-agents:

1. **Visual Designer** — edit the source-derived agenda format and render every page, slide, or equivalent output unit.
2. **Content Reviewer** — audit facts, meeting rules, timing, assignments, and required sequence.
3. **Visual Reviewer** — inspect every rendered output unit for fidelity, hierarchy, readability, and print quality.

Use the platform's equivalent of independent agents, workers, sessions, or delegated tasks. Keep these roles separate on Codex, Claude Code, Magnus, Hermes, OpenClaw, or another agent platform. Never allow the designer to approve its own work or combine the two reviewer roles.

If three independent sub-agents are unavailable, stop and explain that the skill's review-independence requirement cannot be met. Do not simulate approval in the coordinator.

## Gather and Normalize Inputs

Inspect all supplied instructions and files before asking questions. Read [references/agenda-requirements.md](references/agenda-requirements.md) completely and treat it as the content and file-production contract.

Ask one concise, grouped set of questions for missing or conflicting information. For every missing optional field that the design would display, require the user to choose between omission and an approved `TBD`; never decide silently. Do not invent details. Before delegation, create a shared production brief containing:

```text
Club and meeting facts:
Meeting window:
Ordered sessions and timing:
Role and speaker assignments:
Speech and evaluation details:
Special activities:
Template or sample selected:
Source file type:
Required output file type:
Fallback paper size and color, if applicable:
Output-unit count preference:
Approved TBD fields:
User-specific rules:
Output path and filename:
```

Resolve timing infeasibility with the user before document production. Treat user-supplied meeting rules as hard constraints.

## Select the Source and Output Format

Use this order:

1. User-provided agenda template.
2. User-provided sample, edited directly on a duplicate while replacing meeting-specific content.
3. The matching skill-packaged fallback template:
   - A4 + Burgundy: [assets/toastmasters-645B-meeting-agenda-burgundy-A4.docx](assets/toastmasters-645B-meeting-agenda-burgundy-A4.docx)
   - US Letter + Burgundy: [assets/toastmasters-645B-meeting-agenda-burgundy-letter-size.docx](assets/toastmasters-645B-meeting-agenda-burgundy-letter-size.docx)
   - A4 + Navy: [assets/toastmasters-645N-meeting-agenda-navy-A4.docx](assets/toastmasters-645N-meeting-agenda-navy-A4.docx)
   - US Letter + Navy: [assets/toastmasters-645N-meeting-agenda-navy-letter-size.docx](assets/toastmasters-645N-meeting-agenda-navy-letter-size.docx)

Set the format contract before delegation:

- **Non-PDF template or sample:** duplicate and edit it; return the same file type. Never rebuild a PPTX as DOCX or otherwise change the native format.
- **PDF template or sample:** treat it as the visual authority and create an editable `.docx` that follows it closely.
- **No supplied source:** use the matching packaged DOCX fallback and return `.docx`.

Ask for paper size or color only when needed to choose a fallback. Record the source checksum, work from a copy, and never overwrite the source.

## Dispatch the Visual Designer

Give the Visual Designer the shared production brief, selected source copy, and the complete agenda requirements. Require the designer to:

- produce the required source-derived file type, not Markdown, PDF-only output, or a flattened substitute
- for a non-PDF source, edit its duplicate directly and preserve its native structure, dimensions, orientation, branding, styles, images, masters/themes, headers, footers, alignment system, and continuation design
- for a PDF source or packaged fallback, produce an editable `.docx`
- implement all content and sequence rules exactly
- calculate and verify chronological times and the meeting end time
- remove unused sample data and unapproved placeholders
- render every page, slide, or equivalent output unit for inspection at 100%
- return the output path and format, render paths, source path, calculated timeline, and a concise change summary

The designer must use format-appropriate editing and rendering tools.

## Run Both Reviews Independently

After each designer submission, send the same production brief plus the output artifacts to both reviewers. Run the reviews in parallel when possible. Do not reveal one reviewer's verdict to the other before both have responded.

### Content Reviewer Contract

Require the Content Reviewer to inspect the output file's extracted text and native structure with format-appropriate tools, not only the designer's summary. Check every item in the content gate in [references/agenda-requirements.md](references/agenda-requirements.md), including calculations and mandatory Toastmasters role order.

Require this response:

```text
ROLE: Content Reviewer
VERDICT: ACCEPT | REJECT
CHECKS PASSED:
- ...
REQUIRED FIXES:
1. [location] defect; expected result
EVIDENCE:
- ...
```

Return `ACCEPT` only when no required fix remains. Preferences and optional refinements must not be mislabeled as rejection defects.

### Visual Reviewer Contract

Require the Visual Reviewer to inspect every rendered page, slide, or equivalent output unit at 100% and compare it with the selected template or sample. Check the visual gate in [references/agenda-requirements.md](references/agenda-requirements.md). Do not approve from native file structure, text extraction, or a designer description alone.

Require this response:

```text
ROLE: Visual Reviewer
VERDICT: ACCEPT | REJECT
CHECKS PASSED:
- ...
REQUIRED FIXES:
1. [page/slide/output unit and location] visible defect; expected result
EVIDENCE:
- ...
```

Return `ACCEPT` only when every output unit is print-ready and no visible defect remains.

## Enforce the Rejection Loop

Deliver only after both reviewers accept the same revision.

If either reviewer returns `REJECT`:

1. Consolidate both reviewers' required fixes without weakening or omitting any defect.
2. Send the defect list, evidence, and current artifacts back to the Visual Designer.
3. Require a revised file in the same required output format and a fresh full rendering of every output unit.
4. Give the new revision to both reviewers for fresh, independent reviews.
5. Repeat until both return `ACCEPT` on that exact revision.

Invalidate all earlier approvals whenever the output file changes. Do not patch the final file after approval. If an agent fails to follow its contract, replace that role with a fresh sub-agent and rerun it. If repeated attempts cannot achieve dual acceptance, report the unresolved defects and stop without claiming completion.

## Deliver

Verify that the accepted output file and accepted render share the same revision. Return:

- the final agenda file in the required source-derived format
- the selected template or sample name
- the source and output file types
- meeting start and end time
- approved `TBD` fields, if any
- both reviewers' final `ACCEPT` verdicts
- the number of design-review cycles

Recompute the source checksum and confirm that it matches the value recorded before production. Use `[Club-Name]_[YYYY-MM-DD]_Meeting-Agenda_[size-or-orientation].[same-extension]`; for PDF input or a packaged fallback, use `.docx`. Do not deliver reviewer notes as a substitute for fixing rejected output.
