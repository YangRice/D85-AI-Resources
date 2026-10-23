# Agenda Requirements

Use this contract for every design and review cycle.

## Required Inputs

Confirm, when applicable:

- club name and number, meeting date, language, theme, start and end time
- meeting rules and ordered sessions with times or durations
- role holders and speaker/evaluator assignments
- speech titles, projects or levels, and timing ranges
- venue or online link, website or contact details, officers, and club mission when displayed
- special business, awards, announcements, breaks, contests, inductions, and guest activities
- A4 or US Letter paper size and Burgundy or Navy color only when selecting a packaged fallback
- source file type and required output file type
- one-page/slide requirement or permission to continue onto more output units
- every brace-wrapped template placeholder and its matching input value
- the required number and pairing of speaker and evaluator rows
- every optional missing field that would be displayed, resolved by the user as either omitted or marked `TBD`

Do not invent names, dates, times, roles, speech details, rules, club facts, venues, or URLs. Calculate and report any meeting-window overrun before production and ask the user what to change.

## Mandatory Sequence Rules

Preserve the user's sequence unless the user approves a change. Apply these hard rules even when a template differs:

1. The meeting-role introduction block must contain **General Evaluator Introduction**, **Timer Introduction**, **Ah-Counter Introduction**, and **Grammarian Introduction**.
2. That block must not contain an **Individual Evaluator Introduction** or **TTE Introduction**.
3. Place a separate **Individual Evaluator Introduction — 1 minute** immediately before **Prepared Speeches**. Do not merge it into the meeting-role introduction block.
4. The evaluation session must contain **Individual Evaluator Report**, **Ah-Counter Report**, **Grammarian Report**, **Timer Report**, and **General Evaluator Report**.
5. **Timer Report** must be second-to-last and **General Evaluator Report** must be last in the evaluation-report sequence.

Calculate missing start times from preceding durations. Keep times chronological and inside the approved meeting window. Preserve supplied timing ranges unless they conflict with the total schedule. Use **Topicsmaster** unless the club specifies another title.

## File-Format and Production Rules

- For a non-PDF template or sample, duplicate and edit that file and return the same file type; do not rebuild it in another format.
- For a PDF template or sample, use it as the visual authority and create an editable `.docx`.
- When no source is supplied, use the selected packaged DOCX fallback and return `.docx`.
- Preserve the source's native structure, dimensions, orientation, branding, logo, colors, typography, headers, information panels, dividers, hierarchy, functional hyperlinks, and continuation design unless the user asks otherwise.
- Show major blocks clearly with time, activity, and responsible person; distinguish sub-activities and align assignees consistently.
- Preserve format-specific styles, images, tab stops, sections, masters/themes, headers, footers, and page or slide furniture as applicable.
- Treat brace-wrapped text such as `{Club Name}`, `{Meeting Date}`, and `{Speaker #1}` as template placeholders. Replace every occurrence with matching user input while preserving its formatting and position. Ask for missing required values; remove optional placeholders or use `TBD` only with user approval. Leave no unresolved brace-wrapped placeholder in the final file.
- Treat speaker and evaluator rows as sample capacity, not a limit. Create one editable row for every supplied speaker and corresponding evaluator; never omit, merge, or overwrite participants to fit the template.
- Clone the nearest matching row's columns, borders, fills, typography, alignment, spacing, and row-height pattern. Keep numbering, participant details, timing, and speaker/evaluator pairings consistent throughout the file.
- Move later content down cleanly. If additional rows cannot fit legibly, use the closest continuation page, slide, or output unit, repeat required headers, and continue there. Never shrink text, clip content, or extend beyond the canvas to force a fit.
- Remove unused sample placeholders and facts, including `John Doe`, `Jane Doe`, `Club Name`, `Club Number`, sample dates, sample times, and sample URLs.
- Do not reuse sample facts without confirmation or use `TBD` without approval.
- Keep headings with their first related line. Use the source's continuation design when content exceeds the available space; never delete required content merely to force an output-unit count.
- Keep wording concise and correct obvious language inconsistencies without changing meaning.

## Content Review Gate

Reject if any item fails:

- all user-supplied facts, rules, sessions, assignments, and club information reconcile with the source material
- all start times, durations, timing ranges, and the end time are arithmetically consistent and chronological
- the four required role introductions appear and the two forbidden introductions are absent from that block
- the separate one-minute Individual Evaluator Introduction is immediately before Prepared Speeches
- all five required evaluation reports appear, with Timer second-to-last and General Evaluator last
- every other required session appears exactly once in the approved order
- names and roles are assigned consistently
- every supplied speaker and evaluator appears exactly once in the correct section; row counts, numbering, details, and speaker/evaluator pairings agree throughout the file
- every brace-wrapped placeholder is replaced with the matching approved input, and no unresolved placeholder remains
- no invented detail, reused sample fact, unapproved `TBD`, or leftover placeholder remains
- the filename follows the required convention
- the output format matches the format contract: same as a non-PDF source, or `.docx` for PDF input or a packaged fallback

## Visual Review Gate

Render and inspect every page, slide, or equivalent output unit at 100%. Reject if any item fails:

- dimensions and orientation match the selected source or fallback
- branding, logo, colors, typography, header, information rail, dividers, and continuation design remain faithful
- the time, activity, and assignee hierarchy is clear and aligned
- added speaker/evaluator rows faithfully match the source row design, and continuation units repeat the required headers consistently
- no text, image, border, or table is clipped, overlapping, truncated, or outside margins
- no unreadably small text, broken glyph, unexpected font substitution, or visibly crowded line appears
- page/slide breaks are intentional; headings stay with their related content
- headers, footers, panels, spacing, and margins are consistent across output units
- hyperlinks and visible link labels remain sensible
- the agenda is balanced, professional, and print-ready rather than merely technically readable
- the source checksum is unchanged from the value recorded before production

## Final Acceptance

Both the Content Reviewer and Visual Reviewer must return `ACCEPT` for the exact same output-file revision and its full rendering. The coordinator must also verify that the original source checksum is unchanged. Any edit invalidates both approvals and requires both reviews again.
