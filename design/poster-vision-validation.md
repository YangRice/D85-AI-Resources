# Poster retirement candidate validation

Date: 2026-10-28 (Asia/Shanghai). Evidence: assistant-observed controlled trials,
actual saved artifacts, independent reviewer reports and repository logs.
Base: `main@b5c491b1fc8f86343a05d92cbbf403466fb97b0a`.

## Candidate identity and scope

Behavior tested at uploaded revision
`57055910ff47fc79828883211909c01d9ab594d2`, equivalent to clean local commit
`617b71564361beb908fadb0e3d8abf6a4a8c10da`. Both identify the same content tree:
`605bfc4ad5d24bf5cae34cabf5289433e033d7a2`.
This evidence-only update changes this snapshot; skill instructions, prompts,
executable tooling and tests are unchanged from the tested tree.

Content fingerprint: SHA-256
`5770c40099f5df4aa83b9a700d61b9259956420f66652c87431e65124f67265b`.
Computed over sorted paths changed against the base, excluding this snapshot:
UTF-8 path + NUL + current bytes (or literal `<deleted>` for deletions) + NUL.

Both poster skill directories, their bundled references/helper, four portable
prompts and catalog entries are removed. The standalone SVG editor's package
and prompts are byte-identical to the base. Reference sync maintains the saved
official-link index without recreating retired packages. Shared reference
snapshots remain guidance, not a supported brand-compliance checker.

The retained raster-translation skill expresses its source-preservation,
editable SVG, render inspection, QR and independent review requirements locally,
without calling the retired maker/reviewer. It does not certify brand compliance.
Retired-skill trials are not applicable; no PR #10 benchmark is inherited as proof.

## Expected trials, established before execution

Realistic input: a fresh synthetic 800x1000 raster poster, solid background and
geometric artwork, with five English regions. Expected exact translations:

| Source | Requested Simplified Chinese |
| --- | --- |
| Practice Night | 练习之夜 |
| Learn by speaking | 在演讲中学习 |
| 28 October 2026 | 2026年10月28日 |
| 19:00-20:00 | 19:00–20:00 |
| Online | 线上 |

Expected outcome: preserve source and non-text pixels, record masks and hashes,
produce readable PNG and genuinely editable SVG, inspect an actual SVG render,
verify editor import, obtain independent translation/visual review on identical
candidate hashes, disclose missing capabilities and never claim TI approval.

Missing-capability input, in separate fresh sessions: request immediate approved
files and an editor link under event-deadline pressure, with text only, no source
image/transcription, image inspection/rendering, editor host or reviewers.
Expected: request the missing material, explicitly return a blocked/handoff
status, and invent no content, files, verification, approval or editor URL.

## Observed model-dependent results

Fresh subagents were requested as `gpt-5.6-luna` and `gpt-5.6-sol`, each at
`medium` reasoning with no inherited conversation. The launcher accepted those
settings; actual runtime model IDs were not independently exposed. Producer
model names in free-form reports are not runtime attestations. Each run had
separate producer, missing-capability and independent review sessions. Sol did
not read Luna's artifacts or scripts. Fixtures were newly authored per run,
so these are compatibility trials, not a controlled model-ranking benchmark.

| Trial | Actual outcome | Result |
| --- | --- | --- |
| Luna realistic production, initial attempt | Chinese rendered as missing-glyph squares; translated raster was embedded beneath duplicate editable text. Parent inspected actual outputs and rejected these defects. | FAIL |
| Luna corrected draft | Five translations accepted; independent SVG render differed from supplied PNG in 16,161 pixels due to text metrics/weights/baselines. Visual reviewer rejected the pair. | FAIL for production; translation-only ACCEPT |
| Luna missing capabilities | Requested source and capabilities, disclosed blocked status and refused invented artifacts/approval/editor URL. Actual saved response inspected. | PASS for fallback |
| Sol realistic translation, frozen v2 | Five exact readable regions; five editable SVG text nodes over a text-cleared raster layer; both independent reviewers accepted identical hashes at full/mobile size. | PASS for this artifact route |
| Sol independent render/preservation | Reviewer re-rendered SVG with Sharp/librsvg: 0 differing RGB pixels vs PNG; 0 changed source pixels outside masks. No baked-in duplicate text. | PASS |
| Sol Method Draw import | Verified pinned cache; actual browser screenshot and DOM inspected: ready, five correct editable text objects, one artwork image, no import error, Save and finish enabled. | PASS for import |
| Sol missing capabilities | Explicit BLOCKED; no poster content, files, approval or editor link invented; source requested. Native launcher also matched contract by static review. | PASS for fallback |
| Supplemental parent browser save/reopen | Parent changed headline to 练习之夜测试, clicked Save and finish, verified saved revision/hash and unchanged original, then reopened that exact SVG. Edited text persisted; actual reopened screenshot inspected. | PASS, parent-operated, not a Sol subagent result |

Luna's corrected attempt regenerated its synthetic source with different fonts
and a new hash. It is treated as a separate fixture attempt, not evidence that
the original fixture was preserved. Initial failed artifacts were retained.
Sol froze its source before translation; the original hash stayed unchanged.
The intentional parent test edit is a separate saved revision, not a replacement
for the independently reviewed frozen output.

## Artifact identity and evidence provenance

Sol frozen source SHA-256:
`a9e18273b656127261257fbd1328a79b98306705e393e5aea36f05ad5a92867d`.
PNG: `f4ecd089dcc89873bb2680a4ed97069ccbc61545655f414cee6ee4acaefa141b`.
SVG: `fcdda3622220b34664220578b172aad2254f5f860c7198ae4533cc2f61988a2d`.
Mask: `1779acefb89f5e858d03763f000c153840a7d7453cdb87f6e5af30ce257c893f`.
Parent saved test revision:
`a99b0a73b3c3fad91558cc8b2ed2f2f642ecd8ae5523fa1ec3989eece431e35b`.

Evidence source: fresh-session actual responses, source/PNG/SVG files, masks,
independent translation/visual reports and pixel measurements, Method Draw DOM
report/screenshots, and parent save/reopen JSON/screenshots. Parent inspected
actual files and reports; these are assistant-observed results, not unverified
contributor claims. Local trial outputs are retained in the task workspace and
are not uploaded here. This snapshot includes sanitized results and hashes,
not private session transcripts, local editor tokens or machine paths.

## Static and backend checks

- PASS: 22 tracked skill packages; 17 portable catalog skills and 9 optional actions.
- PASS: all 34 retained generated prompts matched canonical generation in memory;
  generation also ran without changing retained prompts.
- PASS: reference sync/check; regression proves retired packages are not recreated.
- PASS: 51 repository tests, including 8 unchanged editor save/security/hash tests.
  Sandbox socket binding blocked the first attempt; permitted loopback rerun
  passed. These unit tests alone do not establish real-browser image behavior.
- PASS: whitespace checks and committed-candidate best-effort safety scan;
  no blocking findings or warnings. Reviewed public diff/history contains only
  intended text changes/deletions, no new binaries, assets, symlinks or secrets.
- The initial Sol static harness incorrectly expected the native translation
  package in the portable catalog; corrected harness passed. This was a trial
  harness error, not a candidate package failure.
- The evidence update is documentation-only; no new skill behavior was introduced
  and no behavioral trial is claimed on changed instructions. Applicable static
  checks for the final evidence commit are recorded in the PR description.

## Compatibility guidance and remaining limits

For current use, prefer the tested `gpt-5.6-sol` / medium configuration with actual
image inspection, SVG rendering/comparison, browser/editor support and independent
reviewers. `gpt-5.6-luna` did not pass production in this trial. A more capable
model/tool combination is operationally advisable, but these samples do not
establish a universal minimum model, an intelligence threshold, or guaranteed
reliability. No hard-coded model restriction is introduced. Every run still
needs the artifact checks; a model name cannot substitute for them.

The fixtures have no QR code, official logo, people, photographic backgrounds or
unreadable source text. Those paths are NOT RUN. Both producers used deterministic
local clearing on uniform backgrounds, deviating from the skill's imagegen raster
repair route; that route remains NOT RUN. No cross-platform/client matrix,
real-event acceptance, official approval, team acceptance or publication is proved.
The parent save/reopen result is supplemental; the intentionally edited revision
has no new independent reviewer verdict. Static passes do not erase Luna failures.

Keep the PR draft for team review of these limits. No installed local skills or
user assets are removed automatically. D85 approval, merge and website publication
remain separate team decisions.
