# Prepare Poster Materials — capability integration validation

Historical local validation record (before the later authorized commit and PR update). Commit/upload statements below describe that validation session, not the current publication state.

Local candidate: catalog version **0.2.0**, checked during the 2026-10-28/29 session (Asia/Shanghai). Working checkout base: `b5c491b1fc8f86343a05d92cbbf403466fb97b0a`. No commits, push, PR edits, dependency installation, model downloads or account/permission changes were performed for this update. The existing working checkout was not reset/rebased; unrelated untracked files were preserved.

## Scope and files

- Reworked English/Chinese `skills/prepare-poster-materials/SKILL*.md`: goal/context, consequential ambiguity, explicit capability discovery and four evidence states; 653 English words.
- Reworked `references/visual-recipes.en.md` / `.zh.md`: everyday intent → resource selection → actual dispatch and checks.
- Added `references/resource-playbooks.en.md` / `.zh.md`: per-resource inputs, outputs, discovery/invocation, setup, checks and fallback; source/license citations.
- Added `references/platform-setup.en.md` / `.zh.md`: conditional host/provider/runtime choices and manual cutout handoff.
- Added the local catalog entry with empty required/recommended dependencies and three declared bilingual portable references; generated `prompts/prepare-poster-materials.en.md` and `.zh.md` from canonical sources. UI YAML was preserved unchanged.
- This report and synthetic validation artifacts under `output/prepare-poster-materials-validation-2026-10-29/` record evidence; they are not runtime prerequisites.

## Resource evaluation and static intake

External instructions were read as untrusted source material, not invoked. No third-party executable code was copied, installed or run. These are original integration notes rather than vendored skills. License statements distinguish code/instructions from fonts/assets/weights/service usage; actual selected versions need review before future use.

| Resource | Primary evidence checked | Integration / boundary |
|---|---|---|
| Anthropic canvas-design | [SKILL.md](https://github.com/anthropics/skills/blob/main/skills/canvas-design/SKILL.md), [folder Apache-2.0](https://github.com/anthropics/skills/blob/main/skills/canvas-design/LICENSE.txt) | Static art-direction choice; Markdown rationale, PNG/PDF concepts. Does not establish editable layers. Discover installed skill first; native labeled SVG layout fallback can meet an editable-composition goal. No fonts audited/copied. |
| Baoyu selected skills | [cover-image](https://github.com/JimLiu/baoyu-skills/blob/main/skills/baoyu-cover-image/SKILL.md), [infographic](https://github.com/JimLiu/baoyu-skills/blob/main/skills/baoyu-infographic/SKILL.md), [image-gen](https://github.com/JimLiu/baoyu-skills/blob/main/skills/baoyu-image-gen/SKILL.md), [MIT](https://github.com/JimLiu/baoyu-skills/blob/main/LICENSE), [backend rules](https://github.com/JimLiu/baoyu-skills/blob/main/docs/image-generation.md) | Specific front-end choices and optional backend, not whole-repository installation. Native backend reuse; preferences/runtime/provider conditions only when relevant. Actual reference/model support is version-specific. |
| Method Draw | [repository and MIT](https://github.com/methodofaction/Method-Draw), existing local edit-svg-canvas instructions/runtime | Reuse installed SVG integration and its launch/save/hash lifecycle. No new editor or build procedure. SVG text, outlined text and embedded raster have distinct editability. |
| rembg | [README](https://github.com/danielgatis/rembg), [MIT code](https://github.com/danielgatis/rembg/blob/main/LICENSE.txt), [runtime](https://github.com/danielgatis/rembg/blob/main/pyproject.toml), [usage](https://github.com/danielgatis/rembg/blob/main/USAGE.md), [BRIA model card](https://huggingface.co/briaai/RMBG-2.0) | Optional local cutout route after checking existing removal tools. README 3.11–3.13 versus broader pyproject declaration is disclosed; actual ONNX compatibility must be checked. Model download/cache/terms differ from MIT code. Explicit model selection; no silent default. |
| IOPaint | [owner archive notice](https://github.com/Sanster/IOPaint), [Apache-2.0](https://github.com/Sanster/IOPaint/blob/main/LICENSE) | Still archived since 2025-08-13. Excluded from new novice default; existing installation is not automatically removed. |
| Advanced alternative | [ComfyUI metadata](https://api.github.com/repos/Comfy-Org/ComfyUI), [README](https://github.com/Comfy-Org/ComfyUI#readme), [GPL-3.0](https://github.com/Comfy-Org/ComfyUI/blob/master/LICENSE) | Unarchived and recently pushed at check time. Conditional advanced masked-edit candidate, not a tested replacement; requires reviewed workflow/models/nodes and runtime. Existing native masked tools/manual editors remain lower-setup choices. |

Official [WorkBuddy design guidance](https://www.workbuddy.cn/docs/workbuddy/From-Beginner-to-Expert-Guide/Function-Description/Design-Idea), [Canva connector guidance](https://www.canva.com/help/mcp-agent-setup/) and [regional account distinction](https://www.canva.cn/help/i-cant-login-cn/) were also checked. Documentation is not a live account/capability test.

## Behavioral validation

Expectations below were set in dispatch before each trial. Fresh Codex subagents had no parent conversation; exact inherited service model identity was not exposed. Candidate instructions/references were statically reviewed before application. Inputs were synthetic; no private member photos or QR codes were supplied. Final outputs were independently inspected by the parent.

Evaluated entry-point SHA-256:

- English: `846a84f4f373d3d4e2d9667fa63cd49fd1ce686cd842d765e530adcfee8c27d8`.
- Chinese: `1695d2726a6d3e0796af4beee7937188cdf05238dac46bc16a1827991b59df78`.

Reference-only source citations were appended during the run; they changed no operational instructions. Generated prompts include the final cited text. No behavior-changing edit followed these trials.

| Requested scenario | Expected | Observed / evidence | Verdict and limits |
|---|---|---|---|
| Transparent speaker asset for Canva | Ask only for missing photo/subject, inspect cutout capability; no connector/account demand or fake output | `routing_capability_trials` A requested original photo and selected subject if needed, described segmentation-first discovery and alpha/edge checks; explicitly no cutout produced | PASS routing; image extraction, transparency/identity checks and import **NOT RUN** because this text-only trial had no photo or processing capability |
| Explore better composition | Choose a feasible design capability and produce real alternatives with editable text, not just advice | `composition_capability_trial` used native SVG fallback under explicitly unavailable third-party/image-backend conditions; created two different 600×800 SVGs, rendered both with existing Sharp; parent opened both PNGs and inspected hierarchy, copy and clipping | PASS actual local file/render task. canvas-design/Baoyu execution **NOT RUN**; no claim of invoking them |
| Modify existing SVG | Exact date edit without platform migration; subsequent user visual edit reuses existing route | `svg_capability_trial` wrote new SVG. Parent confirmed exact byte replacement only, parsed XML, rendered via Sharp and opened PNG. Separate manual-edit request selected existing edit-svg-canvas, disclosed unavailable session and actual source having a portrait placeholder rather than photo | PASS exact file edit and route selection. Interactive Method Draw/browser/save lifecycle **NOT RUN**, not represented as completed |
| Missing cutout capability | Concrete manual options and optional local setup conditions; no automatic install or success claim | `routing_capability_trials` B gave conditional existing Canva removal/export, selection/mask steps, asked existing editor/device for precise UI, and explained rembg Python/ONNX/cache/model-license/CPU conditions | PASS guidance; actual editor/account operation, rembg install/inference/batch **NOT RUN** |
| Ambiguous “highlight time” | Resolve date versus hours versus grouping before hierarchy changes | `routing_capability_trials` C asked whether date, 18:30–21:30, or their grouping should be prominent; did not change layout | PASS clarification response; actual design change **NOT RUN**, appropriately pending answer |

The pre-edit baseline already supplied reasonable SVG ideas and a manual cutout route. It did not establish a measured improvement baseline; this update is not claimed to outperform ordinary chat or prove novice usefulness. Prior WorkBuddy field failure remains unresolved in that host; these controlled cases are not its reproduction.

### Actual artifacts

These artifact links refer to Git-ignored local validation outputs. They are not included in the public PR and will not resolve in a fresh clone; no public artifact reproduction is claimed.

- [Editorial SVG](../output/prepare-poster-materials-validation-2026-10-29/composition/01-editorial.svg), [actual PNG](../output/prepare-poster-materials-validation-2026-10-29/composition/01-editorial.png).
- [Centered SVG](../output/prepare-poster-materials-validation-2026-10-29/composition/02-centered.svg), [actual PNG](../output/prepare-poster-materials-validation-2026-10-29/composition/02-centered.png).
- [Source SVG](../output/prepare-poster-materials-validation-2026-10-29/svg/source.svg), [revised SVG](../output/prepare-poster-materials-validation-2026-10-29/svg/revised.svg), [parent-rendered PNG](../output/prepare-poster-materials-validation-2026-10-29/svg/revised.png).
- Child logs retained alongside those artifacts. The child's SVG log says rendering NOT RUN at its finish; the parent subsequently rendered and inspected the actual revised source as recorded above.

Source SVG SHA-256: `156e80d53678e838dfbf107a97f145e91c319c4aaed239b9ef65921463476a90`.
Revised SVG SHA-256: `07c6274ae2a0d5224f6686c742b3f577750b1deb063fb44b100c02624b7cd1d4`.

Independent static review: `resource_integration_review` inspected all nine package files, the catalog entry and both generated editions; no actionable findings or EN/ZH drift. Static review only, not runtime proof.

## Repository checks

- PASS: reviewed `scripts/build_portable_prompts.py`; generated outputs match canonical final sources. All three references are bundled in each language; no new local-file dependency in copied prompt bodies.
- PASS: `scripts/validate_skill_packages.py` with an explicit manifest of tracked files plus only candidate files — 25 packages. Default tracked-only validation would omit this still-untracked local package.
- PASS: `scripts/validate_portable_skills.py` — 20 skills, 9 optional actions.
- PASS: `scripts/sync_poster_references.py --check`.
- PASS: existing `python3 -m unittest discover -s tests` — 56 tests, with loopback access enabled. No new executable tests/scripts/dependencies added.
- PASS: tracked diff and explicit candidate-file whitespace checks; reviewed safety scanner functions found no candidate text/binary/symlink findings. This is scoped file inspection, not a clean committed base-to-HEAD scan.
- No commit was created, so committed-revision base-to-HEAD scanning is NOT APPLICABLE. No public-readiness claim.

## Remaining NOT RUN

Actual third-party canvas-design/Baoyu operations, all rembg/model/runtime setup and inference, BRIA/other model use, ComfyUI workflows, real portrait extraction, live WorkBuddy/Canva authentication or object edits, interactive SVG editing, QR validation, print/color checks, cross-editor font fidelity and novice learning/usefulness. Current resource documentation and licenses do not establish these outcomes. No tools were installed or accounts/permissions changed.
