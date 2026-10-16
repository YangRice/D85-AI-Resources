# Installation update: three-role team review

Date: 2026-10-16. Question: What does D85 AI Resources actually need to update about installation?

Three independent native Codex subagents reviewed the local repository, then received opposing arguments for cross-examination. The coordinator synthesized their recommendations. This document records a review decision, not an implemented change or client certification.

**Provenance.** Coordinated, reviewed and committed by the repository maintainer, Git identity `yui.yi <yui.yi@alibaba-inc.com>`. The review ran as three independent native Codex CLI subagents (`codex-cli 0.162.0-alpha.17.2`); their individual session identifiers were not recorded here, so cite the Git identity and the commit revision to locate the authors.

**Status.** Pre-implementation review decision, written before any installation guidance changed. The implementation it recommends landed afterwards in commit `6cfe32f` "Improve skill installation guidance and package validation", so every count or line reference below describes revision `1af81e05` at review time, not the revision that ships this file.

## Roles and rounds

| Role | Responsibility | Strongest contribution |
|---|---|---|
| Preacher | Defend the member mission, portability, handover and workflow quality requirements | Preserve the simple repository-URL entrance and every existing independent-review gate. Reduce documentation surface before sacrificing bilingual parity. |
| Politician | Represent members and maintainers; negotiate a feasible release | Verify one practical route first; label other routes documented but untested. Keep technical details behind the short member entrance. |
| Prosecutor | Challenge claims and demand evidence | The 23/18 difference does not prove five skills were lost. No diagnostic can infer client activation or advanced workflow success from file presence alone. |

Round 1 produced independent findings with source locations. Round 2 challenged the proposed diagnostic framework, breadth of supported clients, and mandatory whole-repository checkout. The Prosecutor explicitly accepted the final distinctions, with no remaining blocking objection to this review scope.

## Agreed updates

### 1. Correct and clarify the bilingual installation contract

Update [README.md](../README.md), preserving its repository-URL request and install-all default. A longer linked installation guide is reasonable if needed; a separate file is a documentation choice, not an additional product requirement.

The installing agent should report selected skill IDs, active installation location, source revision where available, discovery evidence or an explicit unverified status, unmet workflow requirements, and any required client reload. File presence, client loading and workflow readiness must remain separate statements.

Evidence: README lines 184–204 already request names, location and missing requirements, but offer no concrete acceptance procedure; lines 240–249 show Hermes-specific viewing calls without a cross-client verification contract.

Acceptance: the English and Chinese requests mean the same thing, an ordinary member still has one clear first action, and no route claims activation without observed client evidence.

### 2. Correct prerequisites and expose conditional requirements

Fix the claim at README lines 258 and 315–320 that the PPTX audit needs `python-pptx`: the tracked helper uses Python standard-library ZIP/XML tools. Basic text skills should not inherit a universal Python prerequisite.

Present a concise requirements table: text guidance; file editing/rendering; independent agents; image generation/inspection; local browser/server; external skill or upstream implementation. The table should summarize existing contracts, not invent replacement fallbacks.

Examples requiring explicit visibility:

- PPTX translation requires an installed `presentations` skill and distinct independent agents ([skill](../skills/powerpoint-translation-redesign/SKILL.md), lines 8–20).
- Agenda production stops if three independent agents are unavailable ([skill](../skills/toastmasters-meeting-agenda-team/SKILL.md), lines 10–20).
- Speech coaching uses five distinct role identities, with waves allowed ([skill](../skills/toastmasters-speech-coaching-team/SKILL.md), lines 16–26).
- Poster production has image/rendering/inspection requirements and independent review; unavailable review permits an unreviewed draft, not final approval ([maker](../skills/toastmasters-poster-maker/SKILL.md)).
- PDF translation is a companion to separately acquired, inspected upstream code and uses PyMuPDF ([skill](../skills/translate-pdf/SKILL.md), lines 8–14).

Acceptance: users can understand why a skill can be installed but unable to complete their chosen task. Existing hard stops and draft labels remain intact.

### 3. Add collection-wide package validation

Discover packages from tracked `skills/*/SKILL.md` rather than creating a second manually maintained list. Check identities, necessary bundled files, local links and declared/conditional companions. Keep the current portable-catalog validator's purpose intact.

Evidence: there were 23 tracked packages at review time (revision `1af81e05`); [the validator](../scripts/validate_portable_skills.py) explicitly describes portable-catalog validation at line 2 and iterates its catalog at lines 74–78. That catalog then had 18 entries. Five packages are outside its scope; this is not evidence that an installer misses them.

A separate small script or an extension to the existing validation entry point are both acceptable. No general diagnostic framework or mandatory member-run command is required.

Acceptance: every distributed package is accounted for, missing required bundled files produce an actionable failure, and the existing portable checks retain their scope and pass criteria. Verify a meaningful failure case such as a removed reference/template in an isolated fixture.

### 4. Align retained-checkout, companion and lifecycle guidance

Make a full retained checkout optional for ordinary skill installation, consistently across both entrances. It remains required when the user explicitly requests the complete tracked resource collection, or where a task actually needs repository-level resources. Report the archive and active installation locations separately. Private Git-ignored originals remain excluded.

Evidence: the AI request mandates a checkout at README lines 189–191; the CLI route presents it as a way to retain the resource collection at lines 228–238. Standalone packages already bundle many supporting resources.

Explain companion requirements for selective installs. Poster maker uses the reviewer and conditionally the sibling SVG editor; PPTX translation conditionally invokes raster-poster translation. Do not imply that the external installer resolves D85's custom catalog dependencies automatically.

Add concise update/removal instructions for each installation method actually documented. Explain that pulling a retained checkout does not automatically refresh active copies. Keep troubleshooting focused on two cases: the client cannot load the package, or the package loaded but the workflow lacks capabilities.

Acceptance: both installation entrances promise the same default result; explicit complete-resource requests are honored; single-skill users can identify companions; lifecycle instructions target the intended scope and copies.

## Evidence needed before calling a client verified

The Politician challenged the Preacher's initial suggestion to verify every documented route before release. They agreed on this distinction, which the Prosecutor accepted:

- Corrected documentation may ship with clearly labeled **documented but untested** routes.
- **Verified** requires a real scoped install with recorded released installer/client versions and date, expected-versus-installed package comparison, fresh-session skill-loading evidence and a harmless representative task.
- A plausible response alone is insufficient loading evidence. A static file diagnostic or helper's `--help` success is insufficient workflow evidence.
- A successful text task does not certify poster, agenda, PDF or presentation production.

Suggested first verification target: Codex, because this team already works in that environment. Hermes is a next candidate given its existing README guidance. This is a work order, not a current support certification. Published CLI behavior must be checked directly; upstream `main` alone cannot establish the npm release's behavior.

## Defer

- Custom installer or general diagnostic engine.
- Marketplace/plugin distribution.
- Automatic Python/system/tool dependency installation.
- Exhaustive client/version certification.
- Full advanced-workflow output tests as a prerequisite for a documentation-only correction.

CI for the collection checks is a useful next step once those checks exist. Absence of CI or plugin manifests is not itself proof of broken installation. The [MVP design](portable-toastmasters-skills-mvp.md), lines 59–64, already excludes platform installers and automatic runtime dependency injection.

## Changes to the earlier audit's interpretation

1. Replace any suggestion of five missing installations with “five packages outside the portable validator's scope.”
2. Requirements are already stated in many skills; the problem is their visibility and inconsistent summary, not universal absence.
3. A deterministic acceptance contract is needed; a new end-user diagnostic command is not established as necessary.
4. Retaining a full repository is a resource/archive choice, not a demonstrated universal runtime prerequisite.
5. Clean installation, activation and lifecycle failures remain unproven until exercised with actual released clients/installers.

## Implementation order

1. Correct README prerequisites, completion report, checkout policy and requirements presentation in EN/ZH.
2. Add minimal collection-wide package checks, preserving the portable catalog.
3. Exercise the Codex route in an isolated location and record what was actually observed; fix discovered defects before marking that route verified.
4. Add CI and other verified routes as maintenance capacity permits.

This review added only this decision record; the changes it recommends were implemented afterwards, in commit `6cfe32f` "Improve skill installation guidance and package validation", not by the review itself. It did not modify skill behavior, runtime dependencies or global/client installations. Existing unrelated work remains outside this review's edits.
