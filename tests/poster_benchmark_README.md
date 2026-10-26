# Poster benchmark fixture generation

## Vision-measurement adapter

`build_poster_vision_cases.py` adapts the existing private manifests to
`tm-poster-vision-check/v1` observations without importing the production checker
or reading predictions/reviewer judgments. It supplies loose logo search ROIs,
alpha-trimmed local reference images, foreground regions and actual prepared
design-region polygons. These inputs are explicitly `fixture-source-derived`;
their results test computer-vision measurements, not a model's ability to
discover regions from a new poster.

Run it with repeated `--manifest` arguments, `--assets` for the already prepared
private asset directory, and a fresh `--output` directory. Optional
`--real-images FIRST SECOND THIRD` adds three visually inspected calibration
layouts in this order: AI project-management, District poster-design training,
coaching case discussion. Those rough model masks are layout-specific; they must
not be applied to arbitrary posters. Their provenance and uncertainties are
recorded separately. The adapter does not download, publish or alter the input
posters. Derived official references stay inside private output.

The six historical manifests plus these three inputs produce 63 cases. Only 42
have targets that map to the new logo/color scope; 21 have original typography,
context or other targets that this pipeline does not assess. Empty target sets
must be reported as untested rather than successes. The original five-positive /
five-negative balance of each historical round does not imply the same balance
for the reduced vision scope. Original labels cannot be reused as new ground
truth without independent per-feature review.

Vision adapter versions v1/v2 used pixel-center rectangle corners, which
collapsed one-pixel-wide source partitions into zero-area polygons. Version v3
uses continuous pixel-edge corners (`x+w`, `y+h`); rasterization and uncertain
boundary handling belong to the measurement layer. Earlier inputs stay frozen.
This is an adapter-coordinate repair on the same images, not a new holdout.
Version v4 additionally preserves the actual source `background` as an engine-
verified hypothesis, maps artwork overlap to appearance as well as clear space,
and retains an explicit effects target for old effects cases. Real-image
observations do not invent a background value. This target-scope repair is
reported separately from the earlier version's results and is not a new holdout.

The reference-selection repair prepares all four permitted TI globe PNGs from
`logo.zip` for each real globe-logo observation, preserving their official
filenames. It includes `ToastmastersLogo3Color.png`, which earlier real inputs
omitted by supplying only `ti.png` (`ToastmastersLogoColor.png`). Source-derived
synthetic fixtures retain their known source references. This is a correction
on reused images, not a new holdout. Missing required archive variants fail
preparation instead of silently narrowing coverage. Extra ZIP entries are ignored.
The training poster similarly receives all four standalone wordmark variants
from `wordmark.zip`; its X/width is measured directly from each source's tight
alpha bounds.
Precomputed X/width ratios are attached to individual reference entries and
bound to the exact source-file hashes. Changed downloads need new measurements;
they cannot inherit a different variant's ratio. Hashes identify local source
assets, not visual matches to a compressed poster.

The available prior three real-poster files were 720×1280, 719×1280 and 720×1280.
The later higher-resolution versions shown in chat were not present in the local
attachment directory during this adaptation; results on the available bytes
must not be represented as tests of those later exports. User acceptance is a
calibration label, not a waiver of actual logo size/clear-space requirements or
an independently confirmed whole-brand approval.

`build_poster_benchmark.py` creates two rounds of ten actual poster images,
each with five intended positive and five intended negative samples for the
declared objective feature scope. Independent review must verify those intended
labels; they do not establish whole-brand approval. The accompanying neutral
manifests give actual image paths, source/checker specifications, true text
rendering logs and target feature keys. All 26 current rule-registry keys are
targeted across the two rounds; this is not exhaustive branch coverage.

The samples are created from official website assets and actual fonts, not
third-party posters claimed to be approved. No official assets/fonts or derived
posters are distributed in this repository. Obtain the following files in a
private local assets directory, preserving their original usage/license terms:

| Local filename | Source |
|---|---|
| `manual.pdf` | https://content.toastmasters.org/image/upload/02330-001-0001-brand-manual.pdf |
| `logo.zip` | https://ccdn.toastmasters.org/content/toastmasters-logo.zip |
| `gavel.zip` | https://ccdn.toastmasters.org/content/gavel-club-logo.zip |
| `pathways.zip` | https://ccdn.toastmasters.org/content/pathways-logo.zip |
| `badges.zip` | https://ccdn.toastmasters.org/content/pathways-badge.zip |
| `wordmark.zip` | https://ccdn.toastmasters.org/content/toastmasters-wordmark.zip |
| `Montserrat.ttf` | https://raw.githubusercontent.com/google/fonts/main/ofl/montserrat/Montserrat%5Bwght%5D.ttf |
| `SourceSans3.ttf` | https://raw.githubusercontent.com/google/fonts/main/ofl/sourcesans3/SourceSans3%5Bwght%5D.ttf |
| `Corinthia.ttf` | https://raw.githubusercontent.com/google/fonts/main/ofl/corinthia/Corinthia-Regular.ttf |
| `DejaVuSerif.ttf` | Local DejaVu Serif font for an intentionally different-family test; retained privately |

Requires Pillow. Run with a fresh output directory:

```sh
python tests/build_poster_benchmark.py --assets /path/to/private-assets --output /path/to/new-private-cases --revision 3
```

The generator refuses to overwrite an existing nonempty benchmark directory.
Each round has `manifest.json` and a contact sheet. `intended-labels-private.json`
must be withheld from the independent reviewer. Withhold reviewer judgments
from the programmer until predictions and checker source hashes are frozen.
`sha256-inventory.json` identifies immutable generated artifacts; hashes are not
visual similarity tests. Revision 2 retains earlier contradictory/missing-evidence
cases as supplementary uncertainty tests. Revision 3 replaces those two cases
with demonstrable image defects. A revised set reusing eight samples must not
be described as an untouched holdout.

Measured source wordmark evidence is recorded in specifications. TI bar height
comes from inspected official fullwidth-alpha rows551–955 (405px), Pathways main
word from its isolated alpha component rows295–520 (226px), and standalone black
wordmark from its tight129px alpha height. Gavel/badge X is left unknown rather
than guessed. Verify these measurements again when official downloads change.

The first two rounds leave branch gaps, including some transformed/cropped-source
negative cases, gray/white variants, non-Latin fallback and unsupported geometry.
Subsequent rounds and separate unit regressions exercise several of these gaps;
the original twenty samples alone cannot prove universal parity with an
intelligent reviewer. Rights, authentic context and subjective visual judgment
remain outside deterministic image-only proof.

## Fresh subsequent round and uncertainty controls

`build_poster_round3.py` constructs a fresh ten-image round with new layout,
additional official grayscale/white variants, real source crops, actual geometry
and context defects, source-backed typography and applicable-entity selectors.
It does not import production checker code or read previous predictions.
The frozen historical round3-v2 has ten scoped cases but nine unique images:
its grayscale and padding-crop positives share identical image bytes and differ
in target features. This limitation is retained, not silently corrected after
the holdout handoff. Subsequent generator runs use a distinct crop-case layout
and reject duplicate image hashes before freezing a manifest.

```sh
python tests/build_poster_round3.py --assets /path/to/private-assets --output /path/to/new-private-round3
```

Run the initial generator and then round3 with the same private assets directory
before rounds4–6. The initial generator extracts `ti.png` and other working PNGs
from the downloaded archives; round3 additionally extracts `gray.png` and
`white.png`, which later generators consume. These extracted assets remain
private local files.

Neutral `target_checks` remain a list of rule keys. `target_selectors` maps a
check key to an applicable entity, such as `{"logo":0}`, so uncertainty about a
different logo cannot silently determine the scoped decision.

`build_poster_uncertainty_controls.py` creates two separate, unscored capability
controls from actual Han text and an actual diagonal gradient. A local Noto Sans
CJK Regular collection file must be supplied; collection face2 is the SC family.
These controls are explicitly excluded from the five-positive/five-negative
sample balance and must not be relabeled incorrect simply because a capability
or an official non-Latin whitelist is absent.

```sh
python tests/build_poster_uncertainty_controls.py --assets /path/to/private-assets --output /path/to/new-private-controls --cjk-font /path/to/NotoSansCJK-Regular.ttc
```

`build_poster_round4.py` adds a further ten-unique-image generalization/boundary
round. It uses fresh text and rendering parameters plus actual standard-weight
font instances generated with fontTools from the privately downloaded variable
fonts. Actual instance files and renderer evidence stay in the private output.
The script rejects duplicate image hashes and refuses nonempty output folders.
No checker code or predictions are imported to build these samples.

```sh
python tests/build_poster_round4.py --assets /path/to/private-assets --output /path/to/new-private-round4
```

The first frozen round4-v1 clear-space negative used a50px top gap against a
continuous50.345px source-derived requirement. Independent review treated this
as a subpixel/rounding uncertainty rather than a strong defect. Preserve that
specimen as a supplemental control. Round4-v2 changes only that specimen's
actual image to a36px top gap; the other nine image hashes remain identical.
The measured official wordmark-height evidence and scaling stay unchanged.
The generator now defaults to `--clear-space-inset 15`; use
`--clear-space-inset 1` only to reproduce the historical uncertainty control.
This is a versioned dataset repair, not an untouched fresh holdout or a new
brand threshold. Reviewer judgments and Programmer predictions for each
version must remain separately identified.

`build_poster_round5.py` creates a further fresh final-validation batch with ten
unique images. It changes the overall layout, source font weights, copy and
rendering/export parameters. As with other rounds, creation does not import
production checker code, consume predictions or expose intended labels in the
neutral manifest. Source font instances and official derived artwork remain
private. Requires Pillow and fontTools.

```sh
python tests/build_poster_round5.py --assets /path/to/private-assets --output /path/to/new-private-round5
```

The same source renderer supports a distinct final round6 using `--round 6`.
Round6 has different canvas/layout, text, standard font weights and resize/export
parameters, while staying within already measured feature families. It retains
five intended positives and five robust actual defects, with no subpixel-only
negative geometry. Prior output directories remain immutable. As with all
rounds, intended labels must be independently verified before claiming balance
or parity.

```sh
python tests/build_poster_round5.py --assets /path/to/private-assets --output /path/to/new-private-round6 --round 6
```

Use the specifically requested reference model when claiming model comparisons.
Earlier reviewers' frozen judgments remain development references; they must not
be relabeled as judgments from a different model. If a requested model is not
available, preserve the actual model/tool identity and report that limitation.
