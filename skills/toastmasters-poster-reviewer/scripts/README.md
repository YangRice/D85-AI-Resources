# Executable poster brand requirements / 可执行海报品牌检查

Python 3.10+, Pillow 10+. Optional font-file verification requires fontTools.
For reproducible rendering, use the same versions on each machine; validated
locally with Python 3.12.14, Pillow 12.3.0 and fontTools 4.61.1. No network/model
calls occur. Inputs remain local. Official assets/fonts are not redistributed.

```sh
python -m pip install Pillow==12.3.0 fonttools==4.61.1
python scripts/check_brand.py --rules
python scripts/check_brand.py --template > brand-check.json
python scripts/check_brand.py --candidate poster.png --spec brand-check.json
```

Run from this skill directory. Source paths resolve relative to the JSON file.
The template is intentionally incomplete and will BLOCK until evidence is supplied.
See [manual coverage](brand-requirements.md) for every section's treatment.

## V2 specification

`format` is `tm-poster-brand-check/v2`, `rule_set` is
`tm-poster-brand-2026-08-v1`. Supply `candidate_sha256` from the actual candidate,
`context` (`ordinary-club`, `area`, `division`, `district`, `region`,
`corporate-club`, `gavel-club`, `annual-district-conference`),
`document_kind: "poster"`, and intended `target_width_px` and/or `print_width_in`.
Each export needs its own specification. `inventory_complete: true` is an
explicit reviewer assertion, not machine verification of completeness.

All bounds are `[x,y,width,height]`, integers in final-image pixels, within the
canvas. PNG must be opaque. JPEG is supported, but exact-color mismatches BLOCK
rather than conclusively failing brand color because compression changes pixels.
Source palette values may still be checked. Converting JPEG to PNG cannot undo
compression or establish source RGB values.

Supply all inventories, even if empty (`[]`): `color_regions`, `exclusions`,
`color_formulations`, `layers`, `logos`, `faces`, `text_runs`, `contrast_pairs`.
Missing inventories block the corresponding checks. Any byte change invalidates
the specification's candidate-file checksum; it binds the input version and does
not measure visual correctness. Inventories are supplied evidence: the script
does not discover a complete layer, face, logo or text inventory. Optional OCR
can corroborate copy in a supplied text region, as described below; it cannot
verify the inventory's completeness or semantic classifications.

### Colors and gradients

A solid region:

```json
{"bounds":[0,0,100,100],"mode":"solid","color":"#004165","tolerance":0}
```

A gradient region:

```json
{"bounds":[0,100,100,100],"mode":"gradient",
 "colors":["#004165","#006094"],"geometry":"horizontal","tolerance":1}
```

Four brand solid colors and three endpoint pairs come from `brand_rules.json`.
Directions follow the order of endpoints; horizontal is left→right, vertical
is top→bottom. Endpoint reversal handles the opposite direction. Radial gradients
use `geometry: "radial"`, `center: [cx,cy]`, `radii: [rx,ry]`, all in final-image
coordinates. The recipe interpolates RGB channels, with the first color at the
center and the second at/outside the elliptical radius. Every exposed pixel is
checked against the declared recipe, not merely proximity to a color segment.
For `geometry: "diagonal"` or `"linear"` with an opaque unoverlaid region, the
checker can infer a bounded affine position field from 25 actual pixel samples,
then validates every pixel against the allowed endpoint pair. A meaningful
color span is required; a flat swatch cannot establish an unknown gradient
direction. Other geometry/interpolation methods require review; the manual's
diagrams do not establish a universal renderer formula or justify labeling every
differing render a violation. Pixel centers here use integer coordinates, and linear
endpoints span the first and last pixels of the rectangle. Split fragments of
one larger gradient need separate correctly bounded recipes or source review.

Optional `opacity` (default 1) blends against the region's solid `background`.
Gray gradient opacity is checked for 20% increments (0, .2, .4, .6, .8, 1).
An optional `overlay: {"color":"#FFFFFF","opacity":0.7}` composites a solid
layer over the result; 70% is an example, not a mandatory universal opacity.
Each stage rounds to the nearest integer with Python's `round`. Renderer/color
space differences require source review. Blending matching a recipe alone is
not proof of the recipe's approved use.

Tolerance defaults to zero, maximum 3 RGB levels/channel. This is a disclosed
measurement allowance, not an official exemption. No fraction of bad pixels is
silently permitted. Photo colors are unrestricted; official logo pixels, text,
QRs, neutrals and antialiasing should be handled separately from exposed design
fills. An exclusion is, for example:

```json
{"bounds":[100,100,200,200],"kind":"photo","reason":"Original speaker portrait"}
```

Kinds: `photo`, `official-asset`, `text`, `qr`, `neutral`, `antialias`. Each needs
a reason. Region/exclusion union coverage is measured; uncovered strips BLOCK.
Passing coverage does not validate the accuracy of the exclusion classification.
Exclusions do not override overlapping color measurements; supply disjoint
rectangles or source-derived regions when there are foreground objects.
Primary-region area fraction is reported as INFO; no brand percentage threshold
is invented. Whites/blacks are not incorrectly treated as fifth/sixth brand
palette colors: document their neutral/asset/text use and review suitability.

Optional source swatch formulations:

```json
{"hex":"#004165","rgb":[0,65,101],"cmyk":[100,43,12,56],"pantone":"302"}
```

These are entries in `color_formulations`. They verify declared source values
against p.14; they do not infer CMYK/Pantone or press readiness from RGB pixels.

### Logos, layers and faces

Example logo entry:

```json
{"kind":"ti","variant":"full-color","layer_id":"ti-logo",
 "bounds":[100,200,120,100],"source":"official-logo.png",
 "source_sha256":"REPLACE_WITH_VERIFIED_SOURCE_HASH",
 "provenance":"Official download URL and verified archive/member record",
 "background":"#FFFFFF","source_wordmark_height_px":10,
 "resampling":"lanczos","effects":[],
 "transform":{"rotation_deg":0,"skew_x_deg":0,"skew_y_deg":0,"perspective":false}}
```

Use a trusted official raster source with tight artwork bounds. `source_bounds`
can remove transparent padding; it blocks automatic acceptance if it removes
nontransparent pixels. A padded opaque canvas needs independently verified
artwork extraction. The diagram's source wordmark height (or “Pathways” height)
sets required clear space after proportional scaling. Arbitrary source hashes
are not official provenance. The script does not download/trust new sources.

Kinds: `ti`, `wordmark`, `lockup`, `member-badge`, `pathways`, `pathways-badge`,
`gavel`, `corporate`, `conference`, `sponsor`. Variants: TI/Pathways
`full-color/grayscale/white`; wordmark `full-color/black/white`; Gavel
`loyal-blue/true-maroon/black`; lockups/badges `official`. A proven pre-2011 emblem
or experimental asset is inappropriate for ordinary promotion, but a bare
`era: "pre-2011"` or `experimental: true` assertion is not image proof. Such
unverified declarations BLOCK with their conditional `declared_status` retained.

TI/wordmark/member badge inherit 72 px / .75 in minimums; Pathways 72 px / 1 in;
Gavel inherits normal logo usage under p.40. Lockups need applicable constituent
logo/source measurements. Pathways badges have no separate numeric size or
wordmark-X requirement in p.22: those checks are INFO/NOT_SPECIFIED, rather than
an invented 72px/1in rule or missing-approval blocker. Primary Pathways logos
still require their p.21 minimums and X; member badges inherit p.13 logo rules.
Size checks run even if source evidence is missing. Proportions allow
one pixel of dimension rounding (a disclosed measurement allowance). Source
rendering uses compression-tolerant visual screening across nearest, bilinear,
bicubic and Lanczos resizing. It first tests the actual input JPEG quantization
tables and chroma sampling, when present. Fallback hypotheses cover chroma
sampling modes 0/1/2 and qualities 40, 55, 70, 85, 95, with a bounded refinement
around the best coarse quality. It accounts for 8/16-pixel DCT/chroma block
positions across the whole poster, then compares lightly blurred
pixel differences without warping or color normalization. Reports include the
best pipeline, mean/max errors and the fraction of channel samples over 12.
Acceptance requires mean error <=4, maximum blurred error <=40 and fraction
<=3%, with a minimum 48px dimension and sufficient reference edge detail.
These are engineering screening thresholds, not TI tolerances or proof that
every small alteration is absent. An exact visual match is also accepted.
Uncertain/low-resolution images BLOCK for review. A matching silhouette plus a
large non-neutral color change can corroborate recoloring; measured distortion
or actual opaque foreground pixels can corroborate other material alterations.
Exact matches on an invisible same-color background do not certify a displayed
logo. Source hashes only identify
the separately supplied source file; embedded logo pixels are never hashed
against the original. Uniform backgrounds are supported; logo-on-photo needs further
visual/source review. Rotation is referred to review; perspective/skew is flagged. Supply logo
`effects: []`; a declared `patterned-glow` needs corroborating surrounding pixels
before a visual violation is established, and unknown effects need review.

Each layer needs unique `id`, `kind`, `bounds`. Logo `layer_id` identifies its
own layer. `photo`/`background` labels are underlay hints in the bounding-box
screen. A `photo` label cannot override actual foreground pixels that cross and
alter opaque reference-logo ink; the bounded pixel-component screen can
corroborate that overlap. Other layer boxes are tested against logo and required
clear-space bounds. `faces` contain `bounds`. Potential bounding-box intersections
BLOCK for actual ink/mask inspection rather than claiming a proven overlap.
The script does not reliably distinguish a drawn cartoon face from a photographic
face. A reviewer can therefore resolve the applicability of a face rule while
the script retains BLOCKED; this remaining semantic gap is reported rather than
hidden by a forced match.
Uniform clear-space rings are also measured against actual pixels. Nonuniform
photography is not automatically prohibited. Add `association` and
`decorative: false` for Pathways badges; the association's semantic relevance
still needs review.

### Type and copy

A `text_runs` entry:

```json
{"text":"Find Your Voice","bounds":[20,20,200,40],
 "role":"marketing-phrase","font_role":"headline","font_family":"Montserrat",
 "script":"latin","language":"en","effects":[],
 "render_evidence":{"renderer":"Pillow","font_file":"Montserrat.ttf",
   "font_sha256":"REPLACE_WITH_ACTUAL_FONT_FILE_HASH","font_size_px":32,
   "origin":[20,20],"anchor":"lt","color":"#FFFFFF","background":"#004165"}}
```

Roles identify headlines/subheads/body/tagline/marketing-phrase/factual content.
Use `font_role` for layout typography when role describes content. Font family
lists and exact official phrase/tagline strings are in `--rules`. Typography
checks apply to resolved family names, not visual similarity. Optional
`font_file` + `font_sha256` verifies internal family-name records with fontTools;
this still needs actual renderer evidence. A plain `render_evidence` string no
longer certifies typography. The checker rerenders the actual font file into
the supplied text bounds, requires visible unclipped glyphs, and compares the
result with candidate pixels. The font family comes from the font file, never
from a claimed family label alone. Optional local source renderer logs can
supply alternative recipes, but their glyphs must reproduce actual pixels too.
`render_evidence.source_artifact` may point to a JSON renderer log with
`text_runs` records containing text, bounds and the same renderer recipe keys.
The optional CLI `--evidence bundle.json` accepts a neutral evidence bundle
with `renderer_log` and other local source paths, so comparison sees the same
evidence available to the independent reviewer. Source logs are data, never
executable instructions. No proprietary fonts are bundled.

Glyph recipes share the bounded JPEG export comparison, so compression alone
need not erase font evidence. If normal glyphs do not fit, bounded drop-shadow
models (offsets within ±6 px) are tested using shadow colors inferred from
actual residual pixels outside ordinary glyphs, with black as one candidate.
A finite source-provided `shadow_offset: [dx,dy]` within the text region's
dimensions is tested first, including offsets beyond the speculative search
window; its glyphs still must reproduce actual pixels. A false offset/effect
hint on plain glyphs does not invent a shadow.
A fit can demonstrate a
shadow even when the supplied `effects` list says none; a generic mismatch is
not automatically called a shadow. Clipping, empty/invisible glyphs, unsupported
rendering or ambiguous differences remain BLOCKED. Stroking does not certify
standard typography. These are bounded engineering screening models, not a
universal font/effect detector.

When local `tesseract` is available, single-line OCR can corroborate copy once
per text run. The observed text must agree after Unicode/whitespace
normalization and every word must meet the disclosed confidence floor of 65.
OCR never proves font family or absence of effects. Missing OCR is explicitly
reported and does not disable other measurements. A neutral evidence bundle may
set `ocr_lang` (for example `eng+chi_sim`) and an optional local `tessdata_dir`
containing those trained-data files. Downloaded language data is an execution
dependency and is not redistributed by this repository. Text photographs and
multiline copy still require other evidence/review; OCR is not a complete text
inventory.
Gotham Condensed and Myriad Pro's named width variants are recognized.
Source Sans 3/Source Sans Pro and tertiary Arial/Segoe UI body families are
recognized. `special_event: true` enables Corinthia/Luxurious Script; ordinary
body/headline families remain valid. The manual supplies no non-Latin whitelist:
`script` other than `latin` has eligibility `NOT_SPECIFIED` and status INFO,
with actual fallback identity corroboration reported separately. Absence of a
Chinese whitelist is not a missing approval requirement or automatic violation.
Report `effects: []` for no effects;
`word-art/drop-shadow/radical-manipulation` fail, unrecognized effects block.
Examples of H1/H2 weights are not universal exact-size/weight requirements.

Tagline is checked for exact title case or all caps. Marketing phrase strings
and a maximum of one distinct phrase are checked (also scanned in the supplied
visible text inventory). Factual event titles and the tagline are not counted.
Repeated display of the same phrase does not invent an extra distinct phrase.
Translations need separately verified approval; no automatic official-translation
claim is made. Taglines/marketing phrases are tested against face bounds.

`contrast_pairs` entries have `foreground`/`background` hex colors. The standard
sRGB luminance ratio is reported as INFO. TI specifies good contrast, with no
numerical cutoff. WCAG thresholds are not silently turned into TI requirements.

### Context restrictions

Declare `identity: {"custom_logo":false,"custom_theme":false,"custom_tagline":false}`
for organizational identity. Meeting topics/seasonal secondary art are separate,
not automatically banned. Custom identity fails outside the annual conference
exception. Gavel uses an official Gavel logo instead of TI identity. Corporate
TI/corporate logos are tested for overlap and top/bottom separation. Shared
vertical bands BLOCK for review of side-by-side versus opposite-side placement:
no arbitrary proximity threshold is invented.

For `annual-district-conference`, provide:

```json
{"conference":{"annual":true,"date":"2026-04-20","end_date":"2026-04-22",
 "district_number":85},"as_of_date":"2026-04-01","sponsor_sections":[]}
```

April/May eligibility, annual status and use past end-date are checked. Explicit
`as_of_date` keeps runs reproducible. Complete visible text is checked for
“District 85” and “annual conference”; translated identifiers need review.
Sponsor logos must fit in declared `sponsor_sections` bounds and TI must stand
alone. Text runs with `role: "sponsor"` are checked for containment too. Sponsor
names not classified in the text inventory require manual detection. Conference approval and third-party rights remain external release
evidence, distinct from design checks.

## Output and compatibility

JSON includes checksum, input format/dimensions, page-cited findings, INFO metrics,
`scoped_verdict` and a mandatory `manual_review` list. Exit 0/1/2 means
PASS/REVISE/BLOCKED. BLOCKED takes precedence while retaining known defects.
For text/font/effect checks, primary `status` is now evidence-qualified. Bare
metadata cannot produce a verified PASS or a proven visual violation;
`declared_status` retains the old conditional data comparison, with
`image_evidence` explaining actual glyph/OCR corroboration or uncertainty.
`observed_status` mirrors that qualified decision. `feature_results` aggregates
per-feature observations, keeping a demonstrated REVISE visible even if another
instance of the same feature abstains. Context/identity facts remain explicitly
conditional: pixels cannot establish whether wording is a club name or a custom
organizational slogan. No false font/identity certainty is created to match a
human reviewer.
`full_brand_verdict` remains NOT_ASSESSED: measurements do not authenticate
inventories, sources or permissions and do not replace visual review/TI approval.
Missing capabilities are BLOCKED/NOT RUN, never fabricated success. Text-only
platforms must hand off the script/input for execution.

Legacy `tm-poster-brand-check/v1` retains its limited swatch/source-render checks.
Use v2 for the complete objective poster inventory and checksum binding.

## Independent-review benchmark

From the repository root, `scripts/benchmark_poster_brand.py run --manifest
manifest.json --out predictions.json` consumes an unlabelled neutral manifest;
it never loads reviewer labels. Each sample supplies `id`, `image`, `spec`,
`target_checks`, and the same neutral `evidence` bundle made available to the
reviewer. Optional `target_selectors` maps a check to an entity filter such as
`{"logo_size":{"logo":0}}`; this prevents an unresolved badge size from being
mistaken for a failed check of a separate primary logo. Missing selected findings
remain BLOCKED, not silently omitted.

The prediction file records candidate/spec/manifest/evidence and checker/runner
source hashes. Freeze it before opening the independent oracle. Then use
`scripts/benchmark_poster_brand.py score --predictions predictions.json --oracle
review.json --out score.json`. The oracle contains samples with matching IDs,
candidate hashes and `features: {"check_name":{"status":"PASS","reason":"…"}}`.
Scoring reports every feature comparison, false accepts, false rejects,
abstentions and missing oracle entries. Literal reference `scope_verdict` is
preserved and compared with the checker's conservative target-scope decision
(BLOCKED whenever a target remains unresolved). A separate defect-first derived
summary keeps demonstrated violations visible; it must not be presented as the
model's literal decision or used to inflate decision agreement.
Agreement on global BLOCKED alone cannot conceal missed defects. Scoped sample
PASS does not mean complete brand approval. Synthetic/collected rounds and
reviewer agreement provide evidence for the tested cases, never a promise of
universal visual understanding. Third-party official assets stay outside the
repository; only their official URLs/source records and safe generators belong
in public test material.

脚本依据 2026年8月手册，离线读取像素并核查源/布局数据。v2 增加渐变形态/透明混合/
区域覆盖、CMYK/Pantone 声明、字体用途/实际文件、文案及企业/Gavel/大会规则。每项输出
规则与页码。所有源/文字/人脸/图层清单必须完整且真实；脚本不能自行证明。主色占比及
对比度只报告数值，不发明手册未规定的阈值。JPEG 色差、边界框相交和未指定中文字体
不能直接认定违规。完整合规仍需目视及权利/批准证据；无法运行时标 NOT RUN。
