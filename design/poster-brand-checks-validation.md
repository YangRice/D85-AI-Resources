# Executable poster brand checks

Working candidate based on `b5c491b`; validated 2026-10-24 on Linux,
Python 3.12.14 / Pillow 12.3.0 / fontTools 4.61.1.
Evidence source: actual local command output and inspected artifacts.

## Manual verification

Downloaded the user-linked official 44-page manual and read the page text;
inspected rendered logo clear-space and gradient/transparency diagrams.
Version 2.0 Rev.08/2026, SHA-256
`929dec65bdfbb43e27c306e5d3c9ab6bd955d0c0b55256960d51f64509cedbe4`,
matching the existing canonical source inventory. PDF and official source assets
were not added to public files. The manual coverage matrix is in
`skills/toastmasters-poster-reviewer/scripts/brand-requirements.md`; machine facts
and page-cited rule registry are in `scripts/brand_rules.json` in that skill.

## Executed checks

- PASS: 44 dedicated measurement tests, including the original v1 cases and v2
  cases for coverage gaps, RGB/CMYK/Pantone formulations, actual spatial linear
  and radial gradients, opacity/blending, source proportions/variants/cropping,
  patterned glow, logo size without source evidence, bounding intersections,
  font family/role/effects and actual internal font-file name mismatch, tagline
  casing, phrase counts, translations needing evidence, corporate/Gavel rules,
  conference date/expiry/identifiers/sponsor placement, contrast/area metrics,
  checksum binding, JPEG uncertainty and CLI template/rule exports.
- PASS: complete repository suite, 100 tests. Existing SVG-editor tests initially
  required access to loopback sockets; reran the complete suite with that access
  and all passed. No SVG-editor code changed.
- PASS: package validation (24), portable catalog validation (19), reference
  synchronization, generated-prompt parity and diff whitespace check.
- PASS: controlled real-input missing-evidence trial on the supplied JPEG.
  Expected BLOCKED for incomplete source/inventories, with known size defects
  preserved and compressed-pixel color drift treated as uncertainty. Observed
  BLOCKED, 60px versus 72px logo finding at the declared 853px display width,
  and gradient mismatch BLOCKED rather than a definitive color violation.
  All original/image/spec/result artifacts stayed private outside the repository.

Tests use synthetic source art and font data, not redistributed official assets.
The supplied JPEG trial is a script execution, not independent visual approval
or a fresh-conversation skill trial.

## Limits and not-run checks

- NOT RUN: Windows/macOS or Python 3.10 execution locally. Six CI combinations
  cover Windows/macOS/Ubuntu and Python 3.10/3.12, pinning Pillow 12.3.0 and
  fontTools 4.61.1. No CI execution/cross-platform success is claimed.
- NOT RUN: fresh-conversation realistic-poster and missing-capability model trials.
  No model-adherence claim is made from unit tests or script trials.
- Source authenticity, true inventory completeness, legal rights/approval,
  semantic brand requirements and renderer evidence still need review.
  Measurements do not issue a whole-brand PASS or external release authorization.
- Scope is the manual's objective poster requirements. Website/video/physical
  merchandise-specific requirements are explicitly mapped as other-media scope,
  not claimed implemented in a static poster checker.

Canonical bilingual reviewer instructions and logo-variant references were
updated and their generated prompts regenerated, including maker prompts that
bundle the reviewer. V1 remains supported; v2 expands the source/layout schema.
No commit, push or publication was performed.

## Compression-aware logo correction

Replaced exact-render rejection in both v1 and v2 with shared local visual
screening (`logo_compare.py`). Reference identity hashes are kept separate from
visual comparison. Screening reports numerical metrics, explicit engineering
thresholds and uncertainty; it cannot certify provenance or absence of every
small alteration. No global color normalization, warping or geometric search is
used. Logo source bounds and uniform background evidence remain required.

Controlled synthetic tests accept resize/antialiasing differences and JPEG
qualities 40–95, including an unlisted quality and a logo cropped from a
whole-poster JPEG at a non-block-aligned position. Tests with recoloring,
stretching, removed elements and insufficient resolution withhold acceptance.
The full suite passed 106 tests before the final additional block-phase test;
the dedicated suite was rerun afterward. Cross-platform execution remains NOT RUN.

## Subsequent team refinement

The later Tester/Reviewer/Programmer iterations, explicit GPT-6.1 Sol reference
reviews, final test counts and remaining budget-model limitations are recorded
in [the team validation report](poster-reviewer-team-validation.md). Earlier test
counts above describe their historical revisions, not the final candidate.
