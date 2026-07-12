---
name: toastmasters-speech-coaching-team
description: Evaluate a Toastmasters prepared speech through a virtual coaching team made of separate Coach, Individual Evaluator, Timer, Grammarian, and Ah-Counter sub-agents, then synthesize their independent reports into holistic, prioritized feedback. Use when a user provides a speech transcript, audio, video, delivery notes, timing data, speech project, or evaluation goals and asks for Toastmasters-style speech evaluation, rehearsal coaching, meeting-role feedback, or a multi-perspective prepared-speech review.
---

# Toastmasters Speech Coaching Team

## Purpose

Create a virtual Toastmasters evaluation team for one prepared speech. Assign every meeting role to a different sub-agent, preserve each role's distinct report, and then provide one cross-role synthesis.

The main agent coordinates evidence and synthesizes. It must not replace, merge, or impersonate any required role.

## Required Architecture

Assign exactly one distinct sub-agent as the active owner of each required role:

1. Coach
2. Individual Evaluator
3. Timer
4. Grammarian
5. Ah-Counter

Run the five role agents in parallel when the environment permits. Never assign two required roles to the same sub-agent. Never ask one role agent to produce another role's report. The main agent is not one of the five role agents.

If fewer than five sub-agent slots are available, run roles in waves while keeping a distinct sub-agent identity for every role. If sub-agents are unavailable, stop and explain that this skill's core independence requirement cannot be satisfied; do not simulate all roles in the main agent.

## Gather the Evaluation Packet

Use whatever the user supplies:

- speech transcript, outline, audio, or video
- speech title and purpose
- Toastmasters project or evaluation criteria
- target time range
- audience and occasion
- speaker's goals or concerns
- timestamps, delivery notes, or prior feedback

Proceed with partial inputs when useful. State the evidence limits once and pass the same evaluation packet to every role. Ask a blocking question only when there is no speech content or observation evidence to evaluate.

Do not invent delivery, timing, filler-word, gesture, vocal-variety, or audience-response evidence. A transcript alone supports content and language analysis, but not reliable delivery or elapsed-time judgments. If timestamps are absent, the Timer may provide a clearly labeled estimate from word count, never an observed time. If audio is absent, the Ah-Counter may count written filler tokens in the transcript but must not call them spoken counts.

## Build the Shared Brief

Give each role agent the same shared brief:

```text
Speech title:
Speech project or criteria:
Speaker's purpose:
Target duration:
Audience and occasion:
Speaker's goals or concerns:
Available evidence:
Speech transcript or artifact:
Evidence limitations:
```

Add the role-specific assignment below. Tell every role to distinguish observed evidence, inference, and unavailable evidence.

## Dispatch Role Agents

### Coach

Ask the Coach sub-agent to consider the speaker's longer-term development across content, delivery, confidence, audience connection, and practice strategy. Require:

- two strengths to preserve
- two high-leverage growth areas
- a rehearsal plan with concrete exercises
- one encouraging coaching message
- evidence and limitations

The Coach should be developmental and future-facing, not duplicate the speech evaluator's line-by-line assessment.

### Individual Evaluator

Ask the Individual Evaluator sub-agent to assess how well this specific speech achieves its purpose and any supplied project criteria. Require:

- purpose and likely audience impact
- strengths with specific evidence
- improvement opportunities with specific evidence
- organization, support, transitions, opening, and conclusion
- delivery observations only when supported
- one priority recommendation using a behavior-impact-next-step structure
- evidence and limitations

### Timer

Ask the Timer sub-agent to report only defensible timing evidence. Require:

- observed duration and qualification against the target when timestamps or recording duration exist
- time spent by major section when timestamps support it
- pacing observations supported by timing data
- otherwise, transcript word count and a labeled estimated duration range using disclosed words-per-minute assumptions
- recommended section-level time budget
- evidence and limitations

Never let an estimate masquerade as an official Timer report.

### Grammarian

Ask the Grammarian sub-agent to examine language choices and clarity. Require:

- effective phrases and rhetorical devices
- unclear, awkward, repetitive, or grammatically weak wording
- concise suggested rewrites that preserve the speaker's voice
- vocabulary variety, register, imagery, and sentence rhythm
- optional word-of-the-day observation only if a word was supplied
- evidence and limitations

Do not turn the report into a full rewritten speech unless the user asks.

### Ah-Counter

Ask the Ah-Counter sub-agent to identify fillers and disruptive verbal habits only from supported evidence. Require:

- counts by filler or habit category when audio, video, or a verbatim transcript supports them
- locations or representative examples
- distinction between rhetorical repetition and accidental repetition
- patterns such as false starts, repeated connectors, or long pauses only when observable
- one targeted reduction exercise
- evidence and limitations

Treat a polished script as planned text, not proof of what the speaker actually said.

## Role-Agent Output Contract

Require each role agent to return only:

```text
ROLE: {role name}
EVIDENCE USED: {artifacts actually examined}
CONFIDENCE: High | Medium | Low

STRENGTHS
- ...

FINDINGS
- Observation: ...
  Evidence: ...
  Impact: ...

RECOMMENDATIONS
1. ...

LIMITATIONS
- ...
```

Allow the Timer and Ah-Counter to add compact count tables when useful. Require concise, specific, kind, and actionable feedback. Ban invented quotations and unsupported numeric scores.

## Synthesize Without Flattening

After all five reports return:

1. Present each role's report under its own heading. Do not silently rewrite away disagreements.
2. Identify converging findings supported by two or more roles.
3. Identify meaningful differences or tensions between roles.
4. Prioritize no more than three actions by likely impact and practicality.
5. Create a rehearsal plan for the next practice session.
6. End with one concise overall assessment that balances encouragement and candor.

Keep synthesis claims traceable to named roles. Do not introduce new speech findings during synthesis. If reports conflict, explain the conflict and the evidence behind it rather than choosing a side without justification.

## Final Response Format

```markdown
# Prepared Speech Evaluation

## Evaluation context and evidence limits

## Coach report

## Individual Evaluator report

## Timer report

## Grammarian report

## Ah-Counter report

## Holistic team synthesis

### What the team agrees is working

### Top three improvements

### Role differences or uncertainties

### Next-practice plan

### Overall assessment
```

Preserve useful quantitative details, examples, and attribution. Adapt length to the speech and user's request.

## Quality Gate

Before delivering, verify:

- five distinct sub-agents produced the five required reports
- every report is separately labeled and included
- all agents received the same speech and project context
- observed facts, estimates, and unavailable evidence are clearly separated
- no timing, delivery, filler, or audience-response claim was fabricated
- recommendations cite concrete evidence where possible
- the synthesis attributes its conclusions to roles
- the final plan is prioritized and practical

If any role fails, replace that role's agent with a fresh sub-agent and retry. Keep only the successful agent as that role's active owner. If it still fails, label the missing report and limitation explicitly; never fabricate it.
