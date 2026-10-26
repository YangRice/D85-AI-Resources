# Image-based poster measurements: implementation and validation

Updated: 2026-10-27, Asia/Shanghai. Candidate for the existing draft PR #10,
covering SIFT/homography, clear-space crops, masked colors and reference selection.

## Implemented behavior

The optional `tm-poster-vision-check/v1` route accepts model-provided observations
through `check_brand.py --observations`. It performs no OCR, model API request
or network request. Strict v1/v2 audits retain their existing contract.

- SIFT descriptors, ratio matching and RANSAC homography localize a reference
  inside a supplied search region. Distributed matches/reprojection error gate
  acceptance. Sparse wordmarks have a bounded multiscale edge-template fallback.
- Original homography geometry is measured before rectification, retaining
  anisotropy, skew, reflection and perspective evidence.
- Source wordmark-height ratio determines the clear-space ring. Actual bounds,
  foreground regions, pixel evidence and localization uncertainty are reported.
  Photography/texture alone is not called an intrusion. Diagnostic crops include
  the requested ring, clipped only at the actual canvas edge.
- Aligned spatial Lab residuals screen logo appearance. Histograms and residual
  PCA are diagnostics. A local connected-component guard detects material edits
  that whole-logo averages can miss. Uniform-background exterior-ink screening
  reports possible effects/intrusions without claiming their authoring cause.
- Real globe-logo observations receive all four permitted PNG references from
  the official archive, including `ToastmastersLogo3Color.png`; standalone
  wordmarks receive their four variants. Source filenames, hashes, all competing
  hypotheses and the selected variant remain visible. Each reference has its
  own measured X/width ratio. Known globe measurements are bound to exact source
  revisions; unfamiliar downloads cannot inherit stale values.
- Equally passing variants are ranked by distributed SIFT support before mean
  residual, so a sparse white outline cannot win merely by comparing less ink.
  Enclosed transparent interiors are checked against independently sampled
  background. Conflicting interior content with no uniform-backdrop assertion
  BLOCKS rather than passes. Strong conflicts can REVISE only with the explicit
  `background_uniform_across_logo` assertion and corroborated background color.
  A photo confined to transparent interiors is not itself declared a violation.
- Model include/exclude polygons select design fills. Deterministic Lab k-means
  reports main colors and areas; an independent spatial color-bucket analysis
  prevents averaging away small coherent off-palette patches. Boundary and
  high-variation detail pixels are counted as unmeasured. Isolated quantization
  outliers are disclosed rather than treated as separate fill swatches. Supported
  moderate differences remain BLOCKED; strong differences REVISE.
- Optional tagline/marketing checks consume clearly identified model-read text
  directly, retaining its evidence basis. Partial text inventories cannot
  establish phrase-count PASS. No exact font identity is inferred.

Numeric vision tolerances are engineering settings, not manual exemptions.
Color membership in gradient/blend ranges does not certify spatial geometry or
opacity. Model masks/classification and official-reference authenticity still
need judgment. These selected checks do not establish all 26 brand requirements;
whole-visual/whole-brand verdicts remain NOT_ASSESSED.

## Tests and independent review

The complete repository suite passed **171 tests**, including **36 vision
tests** (18 logo, 13 mask/adapter/copy/dependency and 5 reference-preparation tests). Existing SVG-editor
tests used loopback permission. Runtime: Python 3.12.14, OpenCV headless
4.13.0, numpy 2.3.5, Pillow 12.3.0 in a private virtual environment.

New regressions cover actual-image JPEG, affine/projective distortion, recoloring,
local alterations, removed artwork, shadows, foreground ink versus whitespace,
missing scale/source/masks/dependency, model copy versus font evidence, wrong
candidate identity, duplicate entities, gradients/neutrals and small wrong-color
patches even with one k-means cluster. Empty masks/scopes cannot pass.
Variant regressions cover wrong-first/correct-second references, reversed input
order, retained local-edit rejection, sparse-outline negative space, true white
controls, uncertain photographic backdrops, complete archive preparation,
missing archive entries and per-source ratio isolation. No comparison tolerance
was relaxed to make the three calibration posters pass.

A controller-selected `gpt-6.1-sol` high-reasoning reviewer independently found
an initial false PASS: a magenta patch covering only about 5% of logo core passed
the mean-residual gate. That initial failure is retained as development evidence.
A general local residual component guard fixed it, with regressions for three
patch positions and erased artwork. Independent retest confirmed the patch now
REVISE while JPEG quality65 still PASS. Separate 12×12 and 8×8 off-palette color
patches REVISE even with `requested_k:1`. The bounded review found no further
high-impact issue; this is not an exhaustive correctness guarantee.

## Existing-case execution

`tests/build_poster_vision_cases.py` creates neutral inputs from the private
existing fixture manifests plus the three available real designs. Source-derived
fixture regions are explicitly distinguished from visually supplied model masks.
No images, official artwork or fonts are distributed in the repository.

Adapter v1/v2 used pixel-center rectangles; a one-pixel-wide source region became
a degenerate polygon. V3 corrected these to continuous pixel-edge coordinates.
V4 also preserves actual source background hypotheses and maps inside-artwork
overlaps/effects to the relevant additional checks. These are versioned adapter
repairs on reused cases, not new blind holdouts. Earlier inputs/results remain
private and preserved.

The current v7 input execution evaluated **42 scoped cases** from the 63-case manifest.
The other **21** original target sets were not adapted to this measurement scope
and are explicitly untested, not successes. The 42 cases yield **127 feature
findings: 97 PASS, 17 REVISE, 13 BLOCKED**. Case-level scoped verdicts are
23 PASS, 14 REVISE, 5 BLOCKED. These counts describe execution outcomes, not
accuracy against a new independent oracle. Historical Sol scores from the older
checker revision must not be applied to this new pipeline.

Frozen private report: `tm-poster-vision-variants-verified-v7.json`, SHA-256
`1d55b7216d10f6b61e22626a3b9f93a354ee504e37524a2a0db80296e385aecb`.
It records every selected result, omitted target scope, candidate/observation
identity, reference-file identity, code identity and diagnostic crop identity.
The actual three logo-plus-ring crops were opened and inspected.

## Three real reference designs

Only earlier uploaded exports of these same designs were available as files:
720×1280, 719×1280 and 720×1280. The newer high-resolution chat images were
not locally available; no claim of executing their exact bytes is made. User
expected-positive labels remain separate from measured results.

| Design | Detection / geometry / digital size | Logo appearance | Selected design colors | Clear space |
|---|---|---|---|---|
| AI project management | PASS / PASS / PASS | PASS | BLOCKED: mild yellow/detail differences, no material off-palette component | REVISE: top gap about42.69px versus48.83px required, localization allowance1.75px |
| District poster training | PASS / PASS / PASS | PASS | PASS under selected masks | BLOCKED: top gap39.24px versus39.25px required, allowance2.01px |
| Coaching case discussion | PASS / PASS / PASS | PASS: `ToastmastersLogo3Color.png`, mean deltaE76 9.43 | PASS under selected masks | BLOCKED: top gap24.19px versus24.26px required, allowance1.5px |

The first is a measured apparent shortfall, not a missing-font/source rejection.
The other margins are within localization uncertainty; the script does not turn
subpixel differences into definitive violations. The first color result is an
uncertainty, not a demonstrated prohibited main-color choice. These do not
constitute blanket whole-brand verdicts, and the expected positive labels were
not hard-coded into the implementation.

The earlier v4 setup supplied only `ti.png`, the other full-color variant. Its
12.31 residual caused an unnecessary appearance BLOCKED on the coaching poster.
This was a reference-selection bug, not evidence that its logo was altered.
All earlier frozen reports are retained as historical evidence; the corrected
score is a rerun on reused images, not a new blind accuracy benchmark.

## Controlled workflow checks and remaining limits

Current source revision also passed two sequential fresh-session trials on
2026-10-27 (Codex agents, model ID not exposed), after source review. Expected
outcomes were recorded before execution; actual CLI outputs were saved and
inspected. A synthetic JPEG with a wrong first reference and correct second
reference returned exit0, all three requested logo checks PASS and explicit
second-reference selection; the wrong variant remained REVISE. A separate
synthetic case omitted all reference paths and returned exit2 with detection
and appearance BLOCKED and no invented match. Whole-brand stayed NOT_ASSESSED
in both. Source-file hashes identify the tested working files rather than
misrepresenting the original worktree's base HEAD as the candidate version.
Private evidence: `trial-report.json` in the realistic trial bundle and
`report.json` in the missing-input bundle. These are source-derived behavioral
checks, not blind model extraction accuracy or exact Luna tests.

A fresh-session realistic trial selected logo detection, geometry, appearance
and design palette on the actual available training poster. Expected-before-run
four scoped PASS results were observed in saved JSON (CLI exit0); whole-visual
and whole-brand remained NOT_ASSESSED. Full six-check clear-space BLOCKED was
retained separately. This is an explicitly scoped execution trial using supplied
observations/expectations, not blind extraction accuracy. Exact runtime model
identity was not exposed; no Luna execution claim is made.

The missing-dependency path is covered by a dedicated regression and a separate
fresh-session CLI trial. The new route must disclose unavailable OpenCV and
withhold fabricated measurements; it must never silently switch to OCR.
The actual missing-dependency trial returned exit2 with a BLOCKED JSON identifying
the missing `cv2` module and no measurements. A final aggregation regression also
ensures an INFO diagnostic for unmeasurable effects cannot produce a requested
effects-only PASS. This aggregation change does not alter either fresh trial's
selected measurements; the final existing-case run retains the same counts.

Package/catalog validation, reference synchronization, prompt regeneration and
whitespace checks passed. CI now installs the optional vision dependency in its
six OS/Python poster-test combinations; remote CI and Windows/macOS execution
remain NOT RUN. GPT-5.6 Luna end-to-end extraction remains NOT RUN. Remaining
gaps include weak-feature/small-logo matches, subtle alterations below screening,
ambiguous clear space, semantic mask correctness and unimplemented brand-context
judgments. Exact requested-model parity is not established by this candidate.
