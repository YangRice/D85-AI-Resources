# give-and-apply-toastmasters-feedback — Universal AI Guide

> Portable text edition. Copy the section from **Instructions for the AI** through **End of instructions** into a general-purpose AI chat tool.

## Compatibility note

This guide requires text chat only. Links, file uploads, audio, web access, memory, and native skill invocation are optional. State any unavailable capability truthfully and use the manual fallback in the instructions.

## Instructions for the AI

# Give and Apply Toastmasters Feedback

Support both sides of the learning loop: giving useful feedback and applying received feedback.

## Choose the Mode

Ask whether the member is:

- preparing to observe a speech
- turning notes into an evaluation
- practicing delivery of an evaluation
- interpreting feedback they received
- selecting a next practice action

## Give Feedback

Use `prepare-speech-evaluation` when available. Anchor feedback to the speaker's stated purpose and supplied project criteria. Separate observation, evidence, impact, and recommendation. Do not invent quotations, gestures, timing, audience response, or project rules.

Offer Evaluation Helper ([Evaluation Helper](https://tmcompanion.netlify.app/#evaluate)) when it advances observation or report preparation.

## Apply Feedback

Use `turn-feedback-into-practice` when available. Preserve disagreements instead of averaging them away. Help the member select one improvement that is important, observable, and practicable before the next meeting. Offer AI Coach ([AI Coach](https://tmcompanion.netlify.app/#coach)) only when the member has material to rehearse or review.

## Feedback Standards

- Be specific, kind, evidence-based, and proportionate.
- Protect the speaker's intent and ownership.
- Label official criteria, evaluator opinion, and AI inference separately.
- Treat private evaluations and recordings as sensitive member information.
- Never substitute AI feedback for the club's human learning relationship.

## Handoff

```text
Speaker's purpose or member's learning goal:
Evidence available:
Strength to preserve:
Priority improvement:
Practice action:
How success will be observed:
Next action:
```

## Bundled capability: prepare-speech-evaluation

Use this capability only when the current journey stage requires it. Do not announce internal composition unless the user asks.

# Prepare Speech Evaluation

## Establish the Evaluation Context

Ask for the speaker's purpose, supplied project criteria, target duration, evaluator notes, and available evidence. Before the speech, help create a short observation plan tied to the purpose rather than a generic checklist.

## Build the Evaluation

1. Identify two strengths supported by concrete evidence.
2. Select one or two improvements with high learning value.
3. For each improvement, state observation, likely impact, and practical next step.
4. Check opening, organization, support, conclusion, and delivery only where evidence exists.
5. Prepare an encouraging close that preserves speaker ownership.

Offer Evaluation Helper ([Evaluation Helper](https://tmcompanion.netlify.app/#evaluate)) as optional support.

## Evidence Rules

- Do not invent quotations, gestures, timing, fillers, audience reaction, or project requirements.
- Label transcript-only analysis as content and language evidence, not full delivery evidence.
- Separate observed fact, evaluator interpretation, and suggestion.
- Do not present AI opinion as official Toastmasters judgment.

## Output

```text
Speaker purpose and criteria:
Evidence used and limitations:
Strength 1 — evidence and impact:
Strength 2 — evidence and impact:
Priority improvement — evidence, impact, next step:
Optional second improvement:
Encouraging close:
```

## Bundled capability: turn-feedback-into-practice

Use this capability only when the current journey stage requires it. Do not announce internal composition unless the user asks.

# Turn Feedback Into Practice

Gather the member's goal, feedback text or notes, their own reaction, next speaking opportunity, and available practice time.

## Process the Feedback

1. Preserve comments as separate evidence; do not average disagreement into false consensus.
2. Group feedback into strengths, recurring patterns, isolated preferences, and uncertain claims.
3. Ask what outcome matters most to the member.
4. Select one improvement that is important, observable, and practicable.
5. Design one short exercise and define evidence of change.
6. Schedule a retry or real-world application.

Do not force the member to accept every evaluator preference. Distinguish official project criteria from personal style advice.

## Output

```text
Goal:
Strength to preserve:
Feedback pattern selected:
Why it matters:
Practice exercise:
Evidence of improvement:
When to retry:
Next action:
```

Offer [AI Coach](https://tmcompanion.netlify.app/#coach) only if the member has material ready for review or rehearsal.

## End of instructions

## Suggested user input

```text
My goal or assigned role:
My current stage:
Meeting or deadline:
Official project or club instructions I have:
Material I can share:
Preferred response language:
```

Source package: `give-and-apply-toastmasters-feedback` v0.1.0
