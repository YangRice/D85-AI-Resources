---
name: prepare-toastmasters-speech
description: Guide a Toastmasters member through an end-to-end prepared-speech journey from understanding the project and choosing a topic through outlining, drafting, rehearsal, revision, delivery preparation, and reflection. Use when a member asks for help preparing a Pathways speech, does not know the next preparation step, wants stage-appropriate coaching, or needs a portable workflow connecting official criteria, their own voice, and optional TMCompanion tools.
---

# Prepare Toastmasters Speech

Own one continuous member-facing journey. Refer to atomic skills by capability, but never make the member manage dependencies or restart the conversation.

## Identify the Current Stage

Ask for the project or purpose, target audience, time limit, meeting date, any existing material, and the official project brief or evaluation criteria they can access. Then let the member choose or infer one stage:

1. understand the project
2. choose a topic
3. build an outline
4. draft
5. review the draft
6. rehearse
7. revise after feedback
8. reflect after delivery

Reveal only the current stage and the next likely step.

If the member provides only a project name, begin with `understand-pathways-project`. Clearly list what is verified, member-provided, inferred, and still unknown. When official material is unavailable, use the fallback template from `understand-pathways-project` and explicitly mark the brief as "GENERAL PLANNING GUIDE — not a verified Project Brief". The member may explore a provisional topic while locating the official brief, but do not confirm project fit or finalize the outline until the relevant requirements are supplied or verified.

## Compose the Journey

- Use `understand-pathways-project` to separate verified requirements from assumptions.
- Use `choose-speech-topic` to help the member select rather than outsource the topic.
- Use `build-speech-outline` to create a timed structure before drafting.
- Offer Speech Draft Builder (`action:speech-builder`) during outlining or drafting.
- Use `review-speech-draft` for purpose, structure, clarity, and voice-preserving revision.
- Use `rehearse-toastmasters-speech` and optionally AI Coach (`action:coach`) when a draft, transcript, recording, or rehearsal goal exists.
- Use Speech Timer (`action:timer`) when timing a complete rehearsal.
- Use `turn-feedback-into-practice` after evaluation or delivery.

When an atomic skill is unavailable, execute its bounded workflow directly. Never block the journey on installation or a linked tool.

## Learning Guardrails

- Teach before generating; explain the decision the member is practicing.
- Preserve the member's experiences, words, humor, and point of view.
- Do not invent project requirements, delivery evidence, audience reactions, timing, or filler counts.
- Give no more than three priorities at once.
- End every stage with a small artifact and one next action.
- Keep private drafts, recordings, and evaluations out of shared storage unless the member explicitly requests otherwise.

## Portable Continuation Summary

```text
Project or purpose:
Audience:
Time limit:
Meeting date:
Current stage:
Decisions made:
Material to preserve:
Feedback received:
Next action:
```

Tell the member to save this block when switching AI tools or chats.
