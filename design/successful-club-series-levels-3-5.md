# Successful Club Series Levels 3–5 coach

- Status: Implemented by [PR #13](https://github.com/YangRice/D85-AI-Resources/pull/13)
- Merged revision: `981e03ee94438c9ce4ddf753600714311c2e0488`
- Final PR head: `4daab71b1f9717a4384feac25d3420e83cf4de29`

This record preserves the durable architecture of the merged
`prepare-successful-club-presentation` v0.3.0 package. Candidate-specific
validation results and superseded implementation details remain in PR #13 and
its history rather than in this design record.

## Problem and outcome

Members need one coaching journey for the eleven Successful Club Series topics
assigned across Pathways Levels 3–5. The journey must choose topics accurately,
respect level-specific credit boundaries, retain enough source provenance for
verification, and remain useful in both native and portable text-only use.

The implemented package:

- limits credit-bearing recommendations to the member's current level;
- chooses across all eleven topics by club need when credit does not constrain
  the choice;
- separates voluntary or future-level preparation from current-level credit;
- preserves topic-specific duration, activity, materials, accessibility,
  handoff, and follow-through;
- distinguishes official material, confirmed local context, unverified facts,
  and AI suggestions;
- supports useful text fallback without claiming unavailable browsing, file,
  media, or slide capabilities; and
- keeps preparation, rehearsal, delivery, recording, and approval as distinct
  evidence states.

## Topic and routing model

The coach routes by credit first and club learning need second.

### Level 3

- `Creating the Best Club Climate`
- `Meeting Roles and Responsibilities`
- `Keeping the Commitment`
- `Going Beyond Our Club`

### Level 4

- `Finding New Members for Your Club`
- `Closing the Sale`
- `How to Be a Distinguished Club`
- `Toastmasters Educational Program`

### Level 5

- `Moments of Truth`
- `Evaluate to Motivate`
- `Mentoring`

When the member requests current credit, the coach establishes the applicable
level before recommending a topic. With no level or credit constraint, it may
select any topic by learning need. A different-level topic may be prepared as
voluntary or future-level education, but the coach does not promise present or
future credit. A Level 3 member asking for mentoring receives the Level 3 credit
choices and the Level 5 `Mentoring` option separately, followed by one priority
question.

`Moments of Truth` remains a 60–90-minute facilitated club assessment. A
10–15-minute request can produce only a clearly labelled overview or practice
plan and requires organizer or VPE confirmation; it is not silently converted
into the full module.

## Native and portable composition

The canonical bilingual skill files own the shared coaching journey and routing
rules. The catalog declares three portable references:

- shared sources and boundaries;
- the compact topic register; and
- the canonical Toastmasters terminology reference.

Eleven bilingual detailed topic modules are native-only references. A native
session reads the shared references and only the selected detailed module. This
keeps the active context focused while retaining page-indexed coaching notes,
topic-specific activities, safeguards, and output expectations.

The generated portable prompt intentionally omits the full detailed modules. It
contains the compact verified register and must disclose that limit in user
language. It still provides a provisional outline and activity, the relevant
official URL and printed locator, and the exact details that remain to be
checked. It never invents unseen manual content or exposes repository filenames
as a user requirement.

Canonical sources are edited first and portable prompts are regenerated; the
generated prompts are not hand-edited.

## Coaching journey

One conversation advances through the member's actual incomplete stages:

1. understand the official topic and choose one audience takeaway;
2. build a topic-appropriate timed outline;
3. prepare a factual host introduction and member-owned cues;
4. plan the activity, materials, accessibility, handoff, and follow-through;
5. rehearse using only reported or inspectable evidence;
6. prepare live delivery and human evaluation; and
7. reflect and document only reported or verified outcomes.

The coach reuses the member's topic, draft, evidence, and prior decisions. It
asks one question at a time only when the answer changes the next step. A
shorter practice version is labelled and does not replace an official format.

## Source, safety, and authority boundaries

- Official URLs, item numbers, research dates, brief original summaries, and
  printed-page locators remain available through the shared register and topic
  modules.
- Current official authorities govern credit and changing program rules. Club
  practice governs local logistics. Conflicts are stated with a precise
  official-source or VPE question.
- Official PDFs, decks, logos, forms, charts, and completed member or club
  records are not redistributed by the package.
- User-provided external sources remain conversation-level material unless
  separately reviewed for public inclusion. Inaccessible sources are marked
  `NOT VERIFIED`; their titles or contents are not fabricated.
- Completed `Moments of Truth` findings, identifiable evaluations, prospect
  lists, mentor matching data, and other private member information remain
  outside AI unless explicitly shareable and appropriately minimized.
- The coach does not submit, approve, pay, contact prospects, match mentors,
  record a level, or mark completion for the member.

## Maintainer contract

The package remains correct when:

- the catalog maps exactly eleven topics to the intended Levels 3–5;
- every topic has equivalent English and Simplified Chinese native references;
- portable and native routing preserve the same credit boundaries;
- Chinese output uses the synchronized canonical terminology source;
- detailed modules remain native-only while the compact register is portable;
- `Moments of Truth` retains its duration and facilitation exception;
- generated prompts match canonical regeneration; and
- tests cover routing, reference composition, malformed configuration,
  missing-capability behavior, and terminology-sensitive output.

Behavioral evidence, exact-head check results, limitations, and the reviewed
public history are recorded in PR #13. This document describes the merged
architecture; it is not a replacement validation report.
