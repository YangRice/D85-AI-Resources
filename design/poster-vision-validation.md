# Poster retirement candidate validation

Date: 2026-10-28 (Asia/Shanghai). Tool: Codex; runtime model ID not recorded.
Base: `main@b5c491b1fc8f86343a05d92cbbf403466fb97b0a`.

## Candidate fingerprint and scope

SHA-256: `5770c40099f5df4aa83b9a700d61b9259956420f66652c87431e65124f67265b`.
Computed over the lexically sorted paths changed against the base, excluding this
snapshot, each encoded as UTF-8 path + NUL + current file bytes (or literal
`<deleted>` for deletions) + NUL. The PR commit identifies the exact candidate.

Both poster skill directories, their bundled references/helper, their four
portable prompts and their catalog entries are removed. SVG editor sources,
metadata, runtime references and prompts are byte-identical to the base.
Reference synchronization maintains the official-link index without recreating
retired packages. Shared reference snapshots remain as guidance, not a supported
compliance checker. Historical design records refer to their original revisions.

The dependent raster-translation skill now states its own SVG/render checks and
uses only the standalone editor. It no longer invokes or certifies brand review.
Its source-preservation, masks, QR checks and independent translation/visual
review requirements remain. The native launcher is updated consistently.

## Actual checks

- PASS: portable prompt regeneration; no retained prompt changed.
- PASS: 22 tracked package checks; 17 portable catalog entries.
- PASS: reference synchronization and check; regression confirms it creates no
  retired skill directories.
- PASS: 51 repository tests with loopback access, including 8 unchanged editor
  tests. The sandbox-only attempt failed at socket binding; the unrestricted
  rerun passed. No browser interaction or live model/image trial is implied.
- PASS: whitespace check and inspection of changed text files for unsafe public
  content; no added binaries, symlinks, private assets or credential material.
- Committed-candidate safety scan and whitespace result are reported in the PR.

## Behavioral evidence and remaining gaps

Retired maker/reviewer trials are not applicable: neither is distributed or
executable in this candidate. No result from PR #10 is inherited as current proof.

| Scenario | Expected | Observed | Result |
| --- | --- | --- | --- |
| Fresh realistic translation: synthetic poster to translated PNG, editable SVG and editor entrance | Preserve source/masks/QR, render and inspect, independent translation/visual review, no brand verdict | No fresh conversation or deliverable executed for this candidate | NOT RUN |
| Fresh missing-capability translation: no image inspection/editor runtime | Explicit draft/handoff, no fabricated inspection, approval or editor link | No fresh conversation executed for this candidate | NOT RUN |

Those trials remain required before treating the adjusted translation workflow as
validated. This candidate is submitted as a draft for team review. The checks
above establish retirement/package consistency, not translation quality, brand
compliance, official approval, client activation or publication. No installed
local skills or user assets are automatically deleted.
