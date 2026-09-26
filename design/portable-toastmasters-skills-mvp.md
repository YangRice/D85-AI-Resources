# Portable Toastmasters Skills MVP

## Product model

Use two complementary entrances into one versioned learning system:

- **Resource Center:** a member deliberately searches for a learning resource.
- **Reusable AI Guide:** an AI conversation detects the member's context and guides the next learning step.

Resource Center pages are not implemented in this MVP. The catalog reserves one page slug for every publishable skill so a later site build can render or author the matching pages without changing skill identity.

## Layers

1. **Journey skills** own a recognizable member outcome and a continuous conversation.
2. **Atomic skills** complete one bounded, independently useful learning job.
3. **Integration actions** resolve optional TMCompanion destinations from stable IDs.
4. **Universal prompts** are generated self-contained text artifacts for several AI tools.

`find-tmcompanion-tool` is a standalone routing skill for members who know their immediate need but do not know which TM Companion destination fits. Its portable prompt and bilingual skill package contain all nine links; `catalog/integrations.json` remains the canonical link registry.

Composition happens at publication time. A journey prompt bundles its required and available recommended atomic instructions. It does not depend on nested skill invocation, persistent memory, web access, file upload, or a custom runtime.

## MVP journey skills

| Journey skill | Outcome | First atomic coverage |
|---|---|---|
| `navigate-pathways-learning` | Choose and plan a verified next learning step | project understanding |
| `prepare-toastmasters-speech` | Move from project context to rehearsal and reflection | topic, outline, draft review, rehearsal, feedback practice |
| `perform-toastmasters-meeting-role` | Prepare, perform, report, and reflect | Timer, Speech Evaluator, Table Topics response |
| `give-and-apply-toastmasters-feedback` | Give useful evaluation and apply received feedback | evaluation, feedback-to-practice |
| `practice-toastmasters-table-topics` | Practice and retry an impromptu response | Table Topics response |

The role journey maps General Evaluator, Topicsmaster, Grammarian or Word Master, Ah-Counter, and Toastmaster of the Day at a high level. Only Timer and Speech Evaluator have dedicated atomic MVP skills. Add other role atomics after usage demonstrates independent demand.

## Portable compatibility promise

Promise that the core text workflow can be copied into general-purpose AI chat tools. Do not promise identical behavior, link access, attachment support, memory, native skill invocation, or output quality.

Every guide must:

- ask for goal, stage, deadline, and available evidence;
- ask no more than three questions at once;
- teach the learning decision before generating content;
- recommend one primary next action;
- separate official requirements, member-provided context, observation, inference, and AI suggestion;
- provide a manual fallback for optional tools;
- protect member ownership and sensitive information;
- finish with a copyable continuation summary when the journey spans chats.

## Publishing contract

- GitHub is the canonical source.
- `catalog/skills.json` defines type, version, composition, future page slug, and action IDs.
- `catalog/integrations.json` maps action IDs to optional destinations.
- Each skill remains a valid standalone `SKILL.md` package.
- Generated universal prompts include the core skill and one level of atomic composition.
- Resource Center implementation later consumes the same IDs and versions; it must not become a second canonical copy.

## MVP exclusions

- Resource Center HTML or CMS integration
- platform-specific installers beyond current `agents/openai.yaml`
- automatic runtime dependency injection
- user accounts, analytics collection, or remote state
- official project-content replication
- contest, mentoring, officer-operation, and education-series skills

## Validation targets

1. Catalog and skill structure are internally consistent.
2. Every action ID resolves to a valid HTTPS URL.
3. Journey dependencies exist and contain no cycles.
4. Universal prompts contain no unresolved action IDs.
5. A text-only AI can run the workflow without opening links.
6. Missing attachments or tool access produces a truthful fallback.
7. Project rules, timing, delivery, counts, and audience reactions are never fabricated.
