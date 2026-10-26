# Poster reviewer: current validation

Updated: 2026-10-27, Asia/Shanghai. This document is the current candidate
snapshot, not a development log. Refresh its fingerprint and affected evidence
whenever reviewer code, instructions, shared references or prompts change.
Previous-run results must not be carried forward as current results.

## Current contract

The only executable input is `tm-poster-vision-check/v1`, supplied with
`check_brand.py --observations`; `--template` produces its incomplete template.
The script returns requested feature results and a scoped verdict only. It does
not emit overall visual/brand verdict fields or certify rights or approval.
Nine supported measurements cover logo detection, geometry, appearance, clear
space, effects and digital size, design colors, tagline and marketing phrases.
The model supplies observations; the script calls no OCR, model API or network.

Only Brand compliance can hard-block the overall AI review's design verdict.
Missing brief, original portraits, permissions, preservation evidence or QR
verification prompts focused user questions first. Those categories remain
PENDING_USER, UNVERIFIED or NOT_RUN while the available brand review continues.
Unknown non-brand evidence does not become a presumed defect or overall BLOCKED.
Known defects still receive correction advice; a scoped/design PASS is not proof
that every category has been verified or that publication is authorized.

## Candidate and execution

Candidate content based on `6e074b412fcd335156175e76c410d6b6c20aea1c`.
Content fingerprint SHA-256:
`17a0b7b862cde458425349d9a2c97c451c551e8d2ea03c9c907072022956d0b3`.
This hashes sorted relative-path/tab/file-SHA-256/newline records for the 198-file
intended candidate manifest, excluding this report to avoid a self-reference.
The manifest includes current tracked files that exist plus the new pinned
requirements file; removed files and unrelated untracked artifacts are excluded.
The source fingerprint was recomputed after execution and remained unchanged.
Final on-disk verification also compared all 24 changed/relevant runtime, test,
instruction, shared-reference, generated-prompt and workflow files with the tested
candidate: identical. Their focused fingerprint is
`dbc83ad9c58fecf9b5621ce49904ee9fb036db084c2f3c1f40fa580be58524a7`.

Run date: 2026-10-27, Asia/Shanghai. Environment: macOS arm64, Python 3.12.14,
Pillow 12.3.0, OpenCV headless 4.13.0, numpy 2.3.5. Checks ran in a clean candidate
copy with local loopback access for the existing SVG-editor tests. The original
checkout was not reset or cleaned. Clean-candidate validation uses the intended
current file manifest; the local commit records the removed modules as deletions
and excludes unrelated untracked artifacts.

| Current check | Observed result |
|---|---|
| Portable prompt regeneration and exact parity | PASS; no generated differences in the candidate copy |
| Skill package validation | PASS; 24 packages |
| Portable catalog validation | PASS; 19 skills |
| Canonical poster-reference synchronization | PASS |
| Complete repository unittest suite | PASS; 91 tests, no skips |
| Scoped-output regression and actual poster JSON execution | PASS; removed overall-verdict fields absent; requested feature/scoped results retained |
| Changed-file whitespace check | PASS |

Evidence source: actual local commands and inspected JSON outputs for this
candidate. The local commit records this fingerprinted candidate. Remote CI and upload
are not claimed; the commit identity is recorded by Git to avoid self-reference.

## Current behavior checks

Executed after the current English/Chinese policy and synchronized references
were saved. Tool: Codex subagents, each in a new conversation context; exact
model ID unavailable. Expected behavior was defined before dispatch. These
bounded trials exercise question-first handling, not official brand approval.

| Scenario/input | Expected behavior | Observed behavior | Result/evidence |
|---|---|---|---|
| Supplied District85 training PNG; no approved brief or portrait originals | Inspect image, ask for missing content/asset confirmations, keep non-brand gaps pending; assess brand separately | Actual image inspected; bilingual course mismatch raised as a question; brief/portrait/permission gaps PENDING_USER or UNVERIFIED; QR NOT_RUN/PENDING_USER. A visible title effect was reported separately as a B08 REVISE finding, not a non-brand blocker | PASS; actual response and local trial record inspected |
| No image, approved brief, originals or QR source; no Python; user can answer questions | Ask for evidence; reserve overall BLOCKED for inability to inspect brand compliance; no invented findings | Overall BLOCKED explicitly because the image is unavailable for brand inspection; content/material/QR gaps remain pending/unverified/not run with questions and no fabricated PASS | PASS; actual response and local trial record inspected |

Input identity for the supplied poster:
`79a86cb06f3d42c11fbca76e6f39eaf76d736ae704095d6d968db9bddfe6337e`.
Trial evidence is the current local `existing-poster.md` and `missing-image.md`
responses, not contributor-reported results. The real-image trial used visual
inspection and checksum verification; no source-layer comparison, QR decoding,
mobile render or exact pixel brand measurement was claimed in that trial. Its
B08 finding is model visual judgment, not an independently proven source effect.
No user answers were supplied during the trials, so pending categories remained
pending. The separately executed JSON example measures selected palette regions
only and cannot establish a complete design or brand approval.

## Limits

Remote CI, other operating systems/Python versions and Luna end-to-end accuracy
are NOT RUN. Local synthetic tests and bounded model trials do not establish
universal reliability, official acceptance, rights or print readiness.
