# Poster image checker

One offline checker measures selected logo, design-color and model-read copy
features of an actual PNG/JPEG poster. The model supplies observations; Python
validates and measures them. It never calls a model, OCR engine or network API.
It does not require renderer logs, layout source inventories or font files.

## Run

Use Python 3.10+ and install the pinned image dependencies. From this skill's
directory:

```sh
python -m pip install -r scripts/requirements.txt
python scripts/check_brand.py --template > observations.json
python scripts/check_brand.py --rules
```

Inspect the actual image and relevant crops, then fill the template. Obtain its
SHA-256 with `python -c "import hashlib; print(hashlib.sha256(open('poster.jpg', 'rb').read()).hexdigest())"`.
Run the completed observations against that same export:

```sh
python scripts/check_brand.py --candidate poster.jpg --observations observations.json
```

Exit codes: `0` PASS, `1` REVISE, `2` BLOCKED or invalid input. A template is
incomplete and cannot pass as exported. Missing local execution means NOT RUN.
Transparent artwork must first be flattened against its intended background.
Paths in observations resolve relative to the observation file's directory.

## One observation schema

The sole input format is `tm-poster-vision-check/v1`; its suffix identifies the
schema, not an alternate workflow. `rule_set` is `tm-poster-brand-2026-08-v1`,
the shared Brand Manual Version 2.0 Rev. 08/2026 baseline. The template supplies
these identifiers. `candidate_sha256` must identify the actual image bytes.
A hash establishes file identity, never visual correctness or source authenticity.

`producer` records the actual observation method and model ID when known. Do not
invent a model name. Fixtures must be labeled synthetic/source-derived rather
than presented as model extraction evidence. Coordinates refer to decoded-image
pixels, with origin at top left. Resize/crop observations must be mapped back to
that coordinate system before submission.

`requested_checks` must be nonempty, unique and select from:

| Check | Supplied evidence and measurement |
|---|---|
| `logo_detection` | Search regions and suitable references; SIFT/RANSAC or edge-template localization |
| `logo_geometry` | Original transform, before appearance rectification; distortion, skew, perspective and reflection |
| `logo_appearance` | Aligned spatial Lab residuals, local alterations and transparent interior checks |
| `logo_clear_space` | Per-reference wordmark X/width ratio; projected margin, canvas and foreground pixels |
| `logo_effects` | Extra ink around artwork on a corroborated uniform background |
| `logo_size` | Intended `target_width_px`; applicable 72px digital minimum |
| `design_palette` | Model-selected design polygons; measured color clusters and spatial outliers |
| `tagline` | Clearly transcribed and classified model-read wording |
| `marketing_phrases` | Clearly read/classified phrases; complete inventory for count PASS |

An unrequested check is unassessed. An empty logo observation list does not
establish that the image has no logo. Known defects remain REVISE even if another
requested check is BLOCKED.

## Logo observations and official references

Each `logos` entry has a unique nonempty `id`, the applicable asset `kind`, and
`references` containing all permitted variants of that asset family (maximum12).
A variant object has `path` and, when independently measured,
`wordmark_height_ratio`. For one reference, `reference` plus a logo-level ratio
is also supported. For multiple variants, use objects so each has its own ratio;
missing ratios leave clear space unmeasured. A ratio is the applicable manual X
height divided by the alpha-tight reference artwork width. Measure it from that
exact asset revision. Do not transfer a ratio between variants.

Obtain references through the shared asset guide. For the TI globe, include the
Color, 3Color, Grayscale and White PNGs from the official archive. For a standalone
wordmark, include Black, Color, Grayscale and White. Preserve inspectable source
filenames. The checker measures supplied files; it does not download missing
references or establish their authenticity.

Optional `roi` and `bounds` are integer `[x,y,width,height]` search hints, not
detection answers. `foreground_regions` lists nearby text/symbol/object boxes;
`foreground_inventory_complete` records whether the model inspected the full
relevant foreground. `background: "#RRGGBB"` supplies a uniform-background
hypothesis, which the checker corroborates for supported measurements.
`target_width_px` at the top level establishes the intended digital display
width; it must not be guessed from image metadata.

The checker retains every reference hypothesis, source filename/hash and selected
match. Detection and appearance status come first; distributed SIFT support then
precedes mean Lab residual. Appearance comparisons do not hide original geometry
by rectification. Coherent local edits are checked separately from average error.
Histograms and residual PCA remain diagnostics.

Enclosed transparent interiors are checked against sampled background. Conflicts
remain BLOCKED unless `background_uniform_across_logo: true` and the supplied
background corroborate uniform treatment; only supported strong conflicts REVISE.
A photo visible through transparent artwork is not itself a violation.

Clear space uses the projected source-space margin, including rotated corners.
Results disclose artwork edge gaps, expanded-margin edge gaps and localization
uncertainty. Foreground boxes need supporting visible ink; texture or photography
alone is not called an intrusion. Missing background evidence leaves an effects
check unresolved rather than granting an automatic PASS.

## Design-color observations

`colors` has `include` and `exclude` polygon lists. Each polygon needs a `reason`;
exclusions should also record their semantic `kind` (photo, official artwork,
QR, etc.). Points are finite original-image x/y pairs; continuous edge coordinates
may reach canvas width/height. The model's classifications remain model evidence.

Use the key `polygon` for point lists, for example on a 200×150 image:

```json
{
  "include": [
    {"polygon": [[0, 0], [200, 0], [200, 150], [0, 150]], "reason": "Observed design fill"}
  ],
  "exclude": []
}
```

This object fills the template's `colors` field. Use actual image coordinates
and classifications; exclude photos, QR codes and official artwork as needed.

Deterministic Lab k-means describes stable design fills; an independent spatial
bucket check prevents a coherent wrong-color patch from being averaged away.
`requested_k` is optional, 1–12, default6. The report counts measured, excluded,
unclassified, uncertain boundary and high-variation detail pixels. Empty masks
BLOCK. Moderate supported differences BLOCK; strong off-palette components REVISE.
Isolated outliers are disclosed without being certified compliant.

Primary-color fraction is a metric. No invented numerical dominance requirement
is enforced. Gradient/blend color membership does not prove a spatial gradient
recipe or exact opacity. A selected-mask PASS does not certify excluded pixels.

## Copy and results

For copy checks, `text_runs` have `text`, `role` (`tagline` or
`marketing-phrase`) and `readability` (`clear` or an uncertainty value).
`text_inventory_complete` is a model inspection assertion. Partial inventories
cannot establish a poster-wide phrase-count PASS. Never repair an uncertain
transcription to match approved wording. Copy results retain their model evidence
basis; they do not independently prove what was written or identify fonts.

The report contains findings, feature results, candidate/reference identity,
measurements and `scoped_verdict`. This verdict covers only `requested_checks`;
the script does not issue an overall visual or brand verdict.
See [measurement coverage](brand-requirements.md) for remaining manual work.
Missing dependencies or weak matches abstain. All numerical image thresholds are
engineering screening settings, not official brand exemptions.

## Tests

From the repository root:

```sh
python -m unittest discover -s tests -p 'test_poster_*.py'
```

Focused synthetic images exercise distortion, JPEG uncertainty, local edits,
reference variants, clear-space geometry, masks, copy, invalid input and missing
capabilities. They contain no official artwork. CI installs image dependencies
in the required package-check job. Tests skip measurements explicitly when those
dependencies are absent locally. Unit tests do not establish model extraction
accuracy, complete visual review, approval, rights or print readiness.
