# Club service skills: atomic capabilities and aggregate journeys

## Design decision

Follow the repository's existing atomic + journey composition. Three aggregate entry points select the user's role/stage and coordinate handoffs. Independently usable atomic skills own detailed workflows, source references and optional tools. This replaces the first draft's role-reference-only design after the user requested finer-grained skills.

### Meeting roles
`perform-toastmasters-meeting-role` selects nine atomics: SAA, Topicsmaster, TTE, Ah-Counter, Grammarian/Word Master, meeting host, General Evaluator, and the already-existing Timer and individual speech evaluator. Reuse those last two IDs rather than creating duplicate Timer/evaluation skills. Meeting SAA is distinct from term-level officer SAA.

### Club officers
`serve-toastmasters-club-officer` coordinates seven independent officer skills: President, VPE, VPM, VPPR, Secretary, Treasurer and SAA. It manages shared owners/dependencies, not seven repeated job descriptions. Immediate Past President remains advisory context, not an eighth elected office.

### Mentoring
`mentor-toastmasters-member` coordinates four focused capabilities: establish an agreement, coach actual practice, rehearse a mentoring conversation, and review a mentoring relationship. A single requested role-play turn stops for the user; planning and feedback do not take over their response.

## User and maintenance perspectives

- New member: use a natural-language goal or the aggregate journey without choosing filenames.
- Experienced member: invoke one atomic such as Timer directly, with its own useful output and sources.
- Native agent: load the selected atomic/reference only; if unavailable, disclose and give bounded text help, never pretend it loaded.
- Plain chat: generated aggregate prompts embed their declared atomics and references, so no local-file lookup is needed. They are larger than a selected atomic prompt; use the atomic edition when the role is known.
- Maintainer: role behavior has one canonical atomic source, not a copied parent playbook plus child instructions. EN/ZH must remain equivalent and generated editions must match regeneration.
- Reliability: explicit evidence, format, role and tool boundaries reduce failure opportunities; no model is guaranteed to comply. Optional feedback must not force invented praise.

## Sources and D85 adaptation

Use current TI requirements for governance, education and numerical rules; distinguish local choices and suggested workflows. Each atomic links relevant sources using original summaries, not redistributed official manuals. D85 practical options include Chinese/bilingual cards, WeChat-ready drafts, hybrid participation and offline fallback, without claiming universal club customs or official endorsement.

## Validation boundary

The earlier 500-answer batch tested candidate 1d08bc3, before this refactor. Its 495 PASS, 4 PARTIAL and 1 HARD_FAIL are baseline findings, not validation of the new atomic architecture. Re-run final package, dependency, language, generation and safety checks; independently test standalone atomic use, journey routing/composition, missing inputs/tools, and the discovered evidence/role/language/format failures. Report actual scenarios and outputs, not predictions or a stronger model pretending to be a smaller one.

No authorization is inferred to push, create PR, merge, publish a website, send member messages or alter records while the current publication pause is in effect. Catalog resource slugs reserve intended pages; they do not create live pages.
