# Successful Club Series Levels 3-5 Coach Design

**Date:** 2026-11-09

**Status:** Proposed for user review

**Current package:** `skills/prepare-successful-club-presentation/`

**Current revision reviewed:** `64fd305`

## Problem

The current `prepare-successful-club-presentation` skill has a broad Successful Club Series name but supports only the four presentations assigned to the applicable Pathways Level 3 enhancement. This causes two routing failures:

1. A member whose actual learning need is mentoring can be pushed toward `Keeping the Commitment`, even though Toastmasters publishes a dedicated `Mentoring` presentation.
2. A member working on a Level 4 or Level 5 requirement cannot use the same coaching journey for the Successful Club Series presentation assigned to that level.

The package also assumes that all supported presentations take 10-15 minutes. That is not true for `Moments of Truth`, which is a 60-90-minute facilitated club evaluation. Several modules contain changeable program, dues, application, or Distinguished Club Program information that must not be treated as timeless.

## Intended outcome

Expand the existing skill into one bilingual coach for all eleven Successful Club Series presentations assigned across the current Pathways Levels 3-5 enhancements. Preserve one continuous preparation journey while routing to only the selected topic's detailed notes. Make Pathways level relevant when the member is completing a level requirement, without making level history a prerequisite for ordinary club education use.

Success means that the skill:

- selects only from the member's current level when the member identifies a Pathways level or credit-bearing requirement;
- selects across all eleven topics by club need when no level constraint applies;
- explains cross-level preparation without claiming that a presentation satisfies the wrong level;
- keeps official source URLs, research dates, brief summaries, item/page locators, and changeable-authority links available;
- handles each topic's actual duration, activity, materials, and follow-through;
- remains useful in a text-only portable prompt without bundling eleven full detailed modules;
- preserves privacy, copyright, human review, and truthful completion-state boundaries;
- passes static repository checks and independent behavioral validation.

## Scope

### Level 3

1. `Creating the Best Club Climate` (294A)
2. `Meeting Roles and Responsibilities` (295A)
3. `Keeping the Commitment` (297A)
4. `Going Beyond Our Club` (298A)

### Level 4

5. `Finding New Members for Your Club` (291A)
6. `Closing the Sale` (293A)
7. `How to Be a Distinguished Club` (299A)
8. `Toastmasters Educational Program` (300A)

### Level 5

9. `Moments of Truth` (290A)
10. `Evaluate to Motivate` (292A)
11. `Mentoring` (296A)

The current official Education Programs FAQ governs this level mapping for credit decisions. The presentation manuals govern the content baseline. If a manual's credit statement conflicts with the current FAQ, the skill must disclose the conflict and use the current FAQ plus VPE confirmation for the credit decision.

## Non-goals

- Do not coach the Better Speaker Series or Leadership Excellence Series in this package.
- Do not copy official PDFs, PowerPoint files, logos, forms, charts, or completed club/member records into the repository.
- Do not translate and republish official manuals as if the translation were approved.
- Do not submit, approve, or record Pathways completion for the member.
- Do not promise that a presentation completed outside its assigned level will automatically count later.
- Do not store private member rosters, mentor/mentee matching details, completed evaluation forms, guest data, or internal club assessments.
- Do not make user-provided third-party articles part of the public skill package merely because they were used in one coaching conversation.

## Routing behavior

### 1. Determine whether level constrains the choice

Ask about Pathways level only when the request concerns a current Pathways requirement, credit, approval, or an explicitly named level.

- **Known credit-bearing Level 3, 4, or 5:** restrict recommendations to that level's official list, then choose by the club's learning need.
- **No level or ordinary club education:** choose across all eleven topics by the club's learning need.
- **Member requests a topic from a different level:** explain that members may work on individual projects in an order they choose, but level completions must be submitted in chronological order. Label the cross-level presentation as voluntary or future-level preparation unless current official instructions and the VPE support a stronger conclusion. Never claim it satisfies the current level.
- **Translated, legacy, vintage, completed, or otherwise uncertain path:** run the conditional applicability check. Presentation language alone does not establish course language or eligibility.

The skill should prefer one question at a time when the member asks for guided coaching. It should not demand Pathways history when the member only wants an education session.

### 2. Select by learning need within the allowed set

The entrypoint contains a concise level-grouped routing table. Each row maps a club learning need to one official English topic title and a detailed reference file. Mentoring needs must route to `Mentoring` when Level 5 or no level constraint applies; they must not be silently reframed as `Keeping the Commitment`.

### 3. Read only the selected detailed module

In a native skill session, load the shared source/boundary rules and only the chosen topic module. The member should not have to manage internal files. If the topic changes, stop using the old module and load the new one.

## Shared coaching journey

Keep the existing stages, generalized for all eleven modules:

1. understand the official purpose and choose one audience takeaway;
2. build a topic-appropriate timed outline;
3. prepare a factual host introduction and speaker/slide cues;
4. plan the official or optional activity, materials, accessibility, and follow-through;
5. rehearse against observed evidence;
6. prepare live delivery and the correct human evaluation material;
7. reflect and document only what the member reports or what is verified.

Duration comes from the selected module. Do not apply a global 10-15-minute assumption.

## Topic-module contract

Each of the eleven English and Chinese module pairs follows the same compact structure:

- official landing page, downloadable package URL, item number, research date, and printed-page locators;
- a brief original summary of purpose and required coverage;
- page-indexed coaching notes for source-specific corrections;
- distinctive activity, materials, accessibility, handoff, and follow-through;
- current-sensitive claims and the authoritative link used to recheck them;
- safe personalization guidance and likely misreadings;
- expected output for outline, notes, rehearsal, delivery, and reflection.

New reference pairs:

- `finding-new-members.{lang}.md`
- `closing-the-sale.{lang}.md`
- `distinguished-club.{lang}.md`
- `education-program.{lang}.md`
- `moments-of-truth.{lang}.md`
- `evaluate-to-motivate.{lang}.md`
- `mentoring.{lang}.md`

Existing Level 3 references remain and are revised only where the expanded routing or shared source rules require it.

## Source register and anti-hallucination rules

Add a bilingual source register that preserves, for every topic:

- official English title and item number;
- assigned enhancement level;
- canonical resource landing URL;
- original LMS URL when one was supplied;
- direct official package URL when verified;
- official shop/series URL for duration when relevant;
- concise English and Chinese original summaries;
- research date and last observed file metadata where useful;
- printed pages used by the coaching notes;
- current authorities for program rules, fees, applications, DCP, Pathways, or other changing claims;
- known conflict or uncertainty notes.

The skill must use the register as a locator, not as proof that a live page is unchanged. Current-sensitive answers require a fresh official check when browsing is available. Without browsing, use the dated summary and disclose the limitation.

For user-provided external sources, maintain a conversation-level source ledger with URL, title, access status, provenance, brief summary, and verification status. If an article cannot be opened, record `NOT VERIFIED` and ask for accessible text or the member's summary; never invent a brief. Do not automatically commit those sources to the public package.

## Topic-specific safeguards

### Moments of Truth

- Treat it as a 60-90-minute facilitated club evaluation, not a short speech.
- Preserve the six Moments of Truth, team discussion, ratings, recommendations, secretary/notetaker handoff, and later distribution step.
- Point members to the official handout/chart. Do not create an AI form labeled official.
- Keep completed ratings and club-specific findings outside AI unless they are explicitly shareable, anonymized aggregate observations.

### Mentoring

- Cover mentoring definition, benefits to mentees/mentors/clubs, mentor qualities, mentoring steps, mentee responsibilities, and the finite nature of the relationship.
- Treat the Club Mentor Program forms as member-operated materials. Do not collect or match identifiable mentor/mentee data.
- Allow mentoring to be a main topic rather than forcing it under member commitment.

### Finding New Members for Your Club

- Preserve member involvement, practical ways to find prospective members, and respectful guest treatment.
- Recheck current membership-building programs before naming them as active.
- Do not request prospect lists or identifiable guest data.

### Closing the Sale

- Preserve ethical, member-centered persuasion and the official presentation's closing techniques.
- Do not repeat stored dues, fees, application versions, payment methods, or processing instructions as current. Link to the current official application and membership authorities.
- Do not turn the session into pressure tactics or process an application.

### Evaluate to Motivate

- Preserve the official evaluation principles and supportive, actionable feedback focus.
- Use fictional or member-owned non-sensitive examples. Do not ingest identifiable evaluations without permission and sanitization.

### How to Be a Distinguished Club

- Use the current DCP manual and program-year rules for goals, qualifying requirements, deadlines, and recognition.
- Disclose the observed conflict between the 299A manual's credit language and the current Education Programs FAQ; current FAQ and VPE confirmation govern credit.
- Do not claim a club is Distinguished from unverified or incomplete data.

### Toastmasters Educational Program

- Recheck current paths, Base Camp behavior, education-series enhancements, DTM requirements, and recognition processes before presenting them as current.
- Avoid requesting Base Camp screenshots or nonpublic course material.

## Portable prompt design

Keep one portable prompt per language and one native skill. Do not create three competing public skills.

Native sessions retain eleven detailed topic references and load one at a time. Portable prompts bundle:

- the shared coaching journey;
- the level-aware selection rules;
- a compact eleven-topic routing/source summary;
- shared safety, credit, source, and capability boundaries.

The portable build must strip unresolved local reference links and must not embed all eleven detailed page indexes. Add or generalize catalog/builder support only as needed to express this cleanly; avoid a skill-specific copy of the entire shared workflow.

## UI and catalog updates

- Broaden English and Chinese frontmatter descriptions from four Level 3 topics to eleven Level 3-5 presentations.
- Update `agents/openai.yaml` short description while preserving its existing invocation policy and unrelated fields.
- Bump the catalog package version because routing and supported behavior materially expand.
- Update catalog compatibility text, portable references, and README description/example.
- Regenerate portable prompts; never edit them directly.

## Error and conflict handling

- Missing level when credit matters: ask one focused question before recommending a topic.
- Missing level when credit does not matter: choose by club need; do not force Pathways intake.
- Cross-level request: distinguish preparation/delivery from current-level credit and sequential level recognition.
- Inaccessible source: preserve URL and access status, use no invented summary.
- Manual/FAQ conflict: state both claims and the exact authority/VPE question; do not silently choose a favorable interpretation.
- Missing browser: use the dated source summary and label mutable claims unverified.
- Requested time shorter than the selected module: offer a clearly labeled preview/practice version and require confirmation for any credit-bearing arrangement.
- Private or copyrighted input: sanitize, use public official locators, or stop the unsafe intake.

## Validation strategy

### Deterministic checks

Extend repository tests to require:

- exactly eleven topic IDs and the correct Level 3/4/5 mapping;
- English/Chinese reference pairs for every topic;
- identical official URL sets across language pairs;
- source-register entries with URL, brief summary, research date, item, and level;
- a 60-90-minute `Moments of Truth` exception;
- no unresolved `references/...` links in generated portable prompts;
- generated prompt equality with canonical regeneration;
- package independence from other installed skills;
- no bundled official PDF/PPT/logo/form assets.

Run the repository checks required by `AGENTS.md` after reviewing executable changes.

### Behavioral trials

Run fresh, synthetic conversations and record expected/observed results:

1. **Level 5 mentoring:** should select `Mentoring`, explain official purpose, and ask one next-step question.
2. **Level 3 mentoring need:** should keep selection within Level 3 for current credit, explain that `Mentoring` is Level 5, and avoid claiming cross-level credit.
3. **No level, mentoring need:** should select `Mentoring` directly.
4. **Cross-level planning:** should say individual projects may be done out of order but level completions are recognized sequentially; it must not guarantee future credit for an early presentation.
5. **Moments of Truth:** should plan a 60-90-minute facilitated assessment rather than a 10-15-minute speech.
6. **Missing web capability:** should use dated summaries, preserve URLs, and leave current DCP/fees/Pathways facts unverified.
7. **Inaccessible external article:** should record `NOT VERIFIED` and request accessible content rather than fabricate a brief.

### Independent subagent validation

After implementation and local checks pass, use multiple independent subagents with different responsibilities:

- **routing and credit evaluator:** test Level-aware, no-level, and cross-level decisions without seeing the intended response wording;
- **source and safety reviewer:** inspect official URLs, brief summaries, mutable-claim guards, privacy/copyright boundaries, and the exact public diff;
- **bilingual and portable reviewer:** compare English/Chinese meaning, verify the compact portable prompt, and test missing-capability behavior.

Each subagent reports PASS/FAIL/NOT RUN with evidence. The primary agent reviews their actual outputs, fixes supported issues, reruns affected checks, and reports only after all required checks pass or any remaining gap is explicitly disclosed. Different roles are preferred over maintaining multiple divergent skill versions.

## Expected files changed

- `skills/prepare-successful-club-presentation/SKILL.md`
- `skills/prepare-successful-club-presentation/SKILL.zh.md`
- `skills/prepare-successful-club-presentation/agents/openai.yaml`
- shared source/boundary references
- seven new English topic references
- seven new Chinese topic references
- bilingual compact source/topic register files
- `catalog/skills.json`
- `scripts/build_portable_prompts.py` only if generic portable-reference support is required
- `tests/test_successful_club_prompt.py`
- generated English and Chinese portable prompts
- the relevant README section

## Acceptance criteria

The change is complete only when:

- all eleven topics are source-grounded and reachable through one skill;
- known Pathways Level requests are filtered by level before club need;
- no-level requests can select any topic by club need;
- cross-level guidance is accurate and does not promise current-level credit;
- all official URLs and brief summaries are preserved with dated provenance;
- topic-specific duration, materials, privacy, and mutable-source rules are enforced;
- English, Chinese, native, and portable variants are consistent;
- realistic and missing-capability behavioral trials pass;
- independent subagent reviewers pass their assigned checks;
- all applicable repository checks pass with no unexpected generated changes;
- no upload or PR occurs without a separate public-safety review and authorization.
