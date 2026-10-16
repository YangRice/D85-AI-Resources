# D85 skills installation: gap audit

Audit date: 2026-10-16. Scope: current local repository, tracked skill packages, and a selected sample of popular upstream repositories. This is an assessment and proposed work order; it does not change the public installation guide or install anything into an AI client.

See the [upstream comparison](skills-installation-upstream-research-2026-10-16.md) for primary-source evidence and the sample's popularity indicators.

## Assessment

The existing bulk-install approach is reasonable. The largest gap is the absence of a reproducible contract for what success means: files present, discovered by the client, and capable of completing the chosen workflow are three different states.

Keep the current simple member-facing request to install from the repository URL. Back it with a maintained installation guide, a complete package inventory, explicit capability checks, and a short verification procedure. A new custom installer or marketplace plugin is not a prerequisite for these improvements.

## What already works

- The [README](../README.md) provides bilingual install requests, a discovery command, a quoted all-skills selector, project/global scope explanations, and an agent-specific example.
- It distinguishes skill-local supporting files from top-level repository materials and private, ignored downloads.
- The poster packages include synchronized references and official asset URLs. The standalone TM Companion router embeds its destinations; it does not need the top-level integration registry at runtime.
- The agenda skill tracks four DOCX fallback templates and its supporting requirements.
- The SVG editor documents its pinned archive, checksums, cache, offline archive option, and local browser/server needs.

## Prioritized gaps

| Priority | Finding and evidence | Recommended improvement |
|---|---|---|
| High | There is no collection-wide installation acceptance check. The README asks the installing AI to check dependencies but does not give it a deterministic inventory or pass criteria. | Publish an `INSTALL.md` with a success checklist and a read-only diagnostic command. Report source revision, selected scope/client, expected and installed IDs, package files, discovery status, and unmet capabilities. |
| High | There are **23 tracked `skills/*/SKILL.md` packages**, while `catalog/skills.json` and `validate_portable_skills.py` cover **18**. Five packages sit outside this catalog: `poster-image-translation-redesign`, `powerpoint-translation-redesign`, `toastmasters-meeting-agenda-team`, `toastmasters-speech-coaching-team`, and `translate-pdf`. The validator iterates catalog entries; it does not compare them with all discoverable packages. | Add a collection-wide inventory/validator. Keep the portable prompt catalog scoped if intentional; do not add unrelated workflows to prompt generation merely to make counts match. Derive displayed counts from the appropriate inventory. |
| High | Installation does not establish workflow readiness. The [PPTX workflow](../skills/powerpoint-translation-redesign/SKILL.md) requires an installed `presentations` skill and three independent agents; the [agenda workflow](../skills/toastmasters-meeting-agenda-team/SKILL.md) requires three independent agents; [speech coaching](../skills/toastmasters-speech-coaching-team/SKILL.md) requires five distinct agent identities, with waves permitted. Poster production needs image generation, rendering/compositing, inspection, fonts, QR decoding where relevant, and independent review. | Provide a per-skill requirements/capability matrix, separating instructions installed from workflow ready. Identify external skills separately from Python libraries and host capabilities. Show a precise limitation/fallback where the workflow allows one. |
| High | [PDF translation](../skills/translate-pdf/SKILL.md) is explicitly a companion to another repository: its executable translation/extraction code is not bundled. | Make this visible in installation and first-use guidance. Document how inspected upstream code is obtained, record the revision used, and verify PyMuPDF and rendering/fonts when needed. Do not promise that bulk installation includes this external implementation. |
| Medium | A retained full checkout and installed skill folders are separate copies. The README explains both but does not specify which copy runs, how updates stay consistent, or whether single-skill installs include companion skills. The maker links to sibling `edit-svg-canvas`; maker review also needs the reviewer. | Explain source versus active installation. Define single-skill companion selection, preserve the complete-collection default, and verify companion discovery. Do not assume the external installer reads D85's custom `requires`/`recommends` catalog. |
| Medium | Post-install guidance says to reload/start a chat when required and shows Hermes tool calls, but lacks a small activation example and expected outcome for each supported client. | Use a short matrix with documented install route, discovery method, reload behavior, tested version/date, and known limits. Verify with a harmless request such as asking `find-tmcompanion-tool` which tool can time a speech; expect its bundled Speech Timer URL. A plausible answer alone is insufficient proof of skill activation: inspect the client's skill-loading indication too. |
| Medium | There is no update/removal/troubleshooting section or tracked CI workflow. README counts and requirements have drifted. | Add lifecycle instructions tied to the chosen installation method; distinguish updating the repository checkout from updating active skills. Add CI for all-package discovery, tracked supporting files, links, required companions, and isolated installation checks. Document network, symlink/copy, duplicate-name, and unsupported-host failures. |
| Medium | README says the PPTX audit requires `python-pptx`, but its tracked script imports only standard-library modules and reads ZIP/XML directly. Python is listed globally even though basic text skills need no Python. | Correct the audit prerequisite; list installer prerequisites separately from per-workflow runtimes. Avoid requiring every tool for every skill. State tested runtime versions rather than an unverified universal minimum. |

## Installation routes to preserve

1. **Member-facing default:** paste one repository installation request into a skill-aware agent. Include a link to the maintained installation contract so the agent has specific acceptance criteria.
2. **Terminal alternative:** continue using the external Skills CLI with an explicit all-skills selector and chosen client/scope. Its current documented options support this pattern; see [Vercel's installer](https://github.com/vercel-labs/skills#options).
3. **General chat:** retain portable prompts where the host cannot load native skill packages. Label media/file outputs according to actual capability.
4. **Manual fallback:** document copying complete package directories into a host's documented discovery location, with companion requirements. Do not assume a GitHub link alone causes installation.

The [original MVP design](portable-toastmasters-skills-mvp.md) explicitly excludes custom platform installers and automatic runtime dependency injection. Documentation, diagnostic checks, and collection-wide validation can improve confidence within that boundary. Marketplace packaging can be evaluated later if usage justifies maintaining it.

## Checks performed

- Counted 23 tracked canonical skill entry points with `git ls-files`, versus 18 catalog entries.
- `python3 scripts/validate_portable_skills.py` passed: **18 skills (6 journey, 12 atomic), 9 optional actions**. This is evidence for the catalog subset, not all 23 packages or any client's activation.
- `python3 scripts/sync_poster_references.py --check` passed: poster bundles match canonical sources.
- Scanned relative Markdown file links in tracked skill Markdown: **28 resolved**, with no missing/untracked file targets. This checks the complete collection, not every possible single-skill installation.
- Copied only tracked `skills/` files into a temporary directory. All three tracked Python helpers returned exit code 0 for `python3 -I <helper> --help`: PPTX text audit, poster asset fetcher, SVG editor launcher. Temporary files were removed afterward. This proves startup, not a completed translation, asset download, or editor session.
- Checked for tracked CI/plugin/dependency manifests: no `.github/` or `.claude-plugin/` files, `requirements.txt`, `pyproject.toml`, or `package.json` were found in the tracked inventory inspected.
- Preserved existing unrelated modifications and untracked work. No native client installation, package-manager install, global write, update, uninstall, commit, push, or deployment was performed.

## Suggested work order

1. Create the complete inventory and read-only acceptance check.
2. Add bilingual installation documentation with a capability matrix, activation example, and lifecycle/troubleshooting guidance; link it from the existing simple installation request.
3. Exercise clean installs in temporary homes/projects for the clients actually supported, including all-package and selected-package cases. Record exact versions and outcomes.
4. Add CI for repeatable packaging checks. Consider marketplace packaging after the basic contract is demonstrated.

Acceptance target: a new user can identify where the skills were installed, confirm that all selected packages and companions are discoverable, know which workflows are ready, and update/remove them using the documented method.
