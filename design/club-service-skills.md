# Club service skills: atomic capabilities and aggregate journeys

- Status: Implemented by [PR #14](https://github.com/YangRice/D85-AI-Resources/pull/14)
- Merged revision: `22df5e354ada294e6a09ecc021c034de08db03a3`
- Final PR head: `080a4507bda9731916b1c9f8fbba7940aaec7233`

This record preserves the durable architecture of the merged club-service skill
families. Candidate-specific test history and superseded results remain in PR
#14 and its commit history.

## Design decision

Follow the repository's atomic-capability plus aggregate-journey composition.
Three aggregate entry points select the user's role or stage and coordinate
handoffs. Independently usable atomic skills own detailed workflows, source
references, optional tools, and no-tool fallback. This replaced the first
draft's role-reference-only design after finer-grained skills were requested.

### Meeting roles

`perform-toastmasters-meeting-role` selects nine atomics: meeting SAA,
Topicsmaster, Table Topics Evaluator, Ah-Counter, Grammarian or Word Master,
Toastmaster of the Day, General Evaluator, Timer, and individual speech
evaluator. It reuses the existing Timer and speech-evaluation IDs instead of
creating duplicates. Meeting SAA execution is distinct from term-level officer
SAA service.

### Club officers

`serve-toastmasters-club-officer` coordinates seven independent officer skills:
President, VPE, VPM, VPPR, Secretary, Treasurer, and SAA. It assigns shared
owners and dependencies rather than repeating seven job descriptions. Immediate
Past President remains advisory context, not an eighth elected office.

One identified meeting's SAA execution routes to the meeting-role atomic even
when the user is the elected SAA. Reusable standards and term continuity remain
with the officer SAA atomic. When both scopes are needed, the officer atomic
defines the reusable standard and the meeting atomic executes the instance.

### Mentoring

`mentor-toastmasters-member` coordinates four focused capabilities: establish
an agreement, coach actual practice, rehearse a mentoring conversation, and
review a mentoring relationship. A requested single role-play turn stops for
the user. Planning and feedback do not take over the member's response.

User utterances, AI-simulated utterances, and real-world actions remain distinct.
An AI character's reply is not evidence that the user's wording was effective
or caused an outcome.

## User and maintenance perspectives

- A new member can state a natural-language goal or use an aggregate journey
  without choosing filenames.
- An experienced member can invoke one atomic directly and receive a useful
  role-specific result.
- A native agent loads only the selected atomic and relevant references. If the
  package is unavailable, it discloses that fact and provides bounded text help.
- A generated aggregate prompt embeds its declared atomics and references, so
  plain chat does not require local-file lookup. The atomic edition is preferred
  when the role is already known.
- Each role behavior has one canonical atomic source rather than copied parent
  and child playbooks. English and Simplified Chinese sources remain equivalent,
  and generated prompts match regeneration.
- Evidence, format, role, and capability boundaries reduce failure modes but do
  not guarantee model compliance. Feedback never invents praise or observation.

## Sources and D85 adaptation

Current Toastmasters International requirements govern official, educational,
governance, and numerical rules. Local choices and AI-proposed workflows remain
labelled as such. Atomic skills link relevant sources through original summaries
instead of redistributing official manuals.

D85-oriented practical outputs may include Chinese or bilingual cards,
WeChat-ready drafts, hybrid participation, and offline fallback when requested.
They do not imply that one club's custom is universal or officially endorsed.

## Maintainer contract

The architecture remains sound when:

- every aggregate routes to independently usable atomics;
- journey prompts embed declared atomics and relevant references completely;
- meeting SAA and officer SAA cross-route according to task scope;
- missing packages and tools produce explicit, useful fallback rather than
  fabricated loading or execution;
- evidence provenance and role boundaries survive native and portable use;
- English and Simplified Chinese canonical sources remain aligned; and
- generated prompts, catalog dependencies, package structure, safety checks,
  and behavioral regressions are validated against the exact candidate.

The behavioral batches, repair rounds, limitations, and exact merged results are
recorded in PR #14. This document describes the merged architecture; it is not a
replacement test report.
