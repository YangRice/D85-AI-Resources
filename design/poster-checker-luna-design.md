# Poster brand checker: model observations and deterministic rules

Design date: 2026-10-25 (Asia/Shanghai).
Visual-review policy revision: 2026-10-26 (Asia/Shanghai), following three
user-accepted real poster references. Section 11 supersedes the earlier policy
where missing production evidence would block an ordinary visual review.
Implementation update, 2026-10-26: section 12 records the implemented optional
vision route. Earlier proposed-interface/status statements describe the preceding
design revision; the new route implements a limited measurement subset.

This document describes the checker and the requested model-fed workflow.
Sections 1–10 retain the original proposed interface; section 12 documents the
implemented `tm-poster-vision-check/v1` subset. **GPT-5.6 Luna end-to-end execution
has not been tested.**
The exact requested model was unavailable in this session. Its image-input and
tool capabilities must be established before running this workflow.

## 1. Purpose

Given a poster image, identify applicable Toastmasters brand requirements,
measure what the image and available sources support, and explain each result.
Luna supplies visual observations. Python applies the versioned brand rules,
performs pixel/geometry calculations, and preserves the evidence basis.

No separate OCR engine is required in the requested workflow. Text comes from
the image-capable model. Model reading can still make errors; deterministic rule
evaluation does not make the input observations infallible.

## 2. Responsibility boundary

| Work | Model | Script / controller |
|---|---|---|
| Read visible Chinese/English copy | Transcribe, locate and mark unreadable spans | Validate structure; compare supplied strings with rules |
| Identify logo, text, photo, illustration and QR regions | Propose regions and classifications | Validate bounds; crop actual pixels; measure geometry |
| Identify a tagline versus event topic | Supply classification and visual reason | Apply the correct string rule conditionally on that classification |
| Identify logo variant | Propose an official asset candidate | Compare against an independently obtained official reference |
| Determine colors | Identify design-fill regions versus photos | Sample actual pixels; compare permitted palette/gradient recipes |
| Determine exact font family | Report unknown unless source evidence exists | Verify supplied font file and glyph rendering when available |
| Decide organizational/event context | Extract visible clues; retain uncertainty | Use supplied context facts and apply eligibility rules |
| Calculate dimensions, hashes and output status | Do not guess tool results | Compute from actual files and actual execution |
| Establish inventory completeness | Inspect full image and crops; disclose uncertain areas | Check geometric coverage and omissions that can be detected; cannot prove semantic completeness |

The model must not fill in a favorable source palette, official-logo provenance,
font family or approval merely because it resembles an expected value.

## 3. Data flow

```mermaid
flowchart TD
    A[Actual poster and available brief/source assets] --> B[Controller: decode image, record dimensions and file identity]
    B --> C[Luna: inspect image and crops; supply text and region observations]
    C --> D[Observation adapter: validate schema, bounds, uncertainty and provenance]
    D --> E[Python rule engine: copy, colors, logo geometry and source comparisons]
    E --> F[Report: findings, measurements, evidence basis and unresolved checks]
    F --> G{Specific unreadable or conflicting region?}
    G -->|Yes, bounded retry| C
    G -->|No or still unresolved| H[Final report with demonstrated defects and review gaps]
```

The controller handles file identity and tool execution; it can be an application
or the tool-enabled assistant environment. Python does not currently call a model
API. If Luna cannot inspect images, this workflow is unavailable for that model.
If Luna cannot run tools, a host application can execute Python on its behalf and
return the actual result.

## 4. Existing implementation

Paths below are relative to the repository root.

| File | Implemented responsibility |
|---|---|
| `skills/toastmasters-poster-reviewer/scripts/check_brand.py` | CLI, PNG/JPEG loading, candidate identity, v1/v2 routing, aggregate output |
| `skills/toastmasters-poster-reviewer/scripts/brand_rules.json` | Manual version, page references, palette, font roles, tagline and phrase rules |
| `skills/toastmasters-poster-reviewer/scripts/brand_extended.py` | V2 region/source/layout checks and context rules |
| `skills/toastmasters-poster-reviewer/scripts/logo_compare.py` | Compression-aware visual consistency comparison against a supplied reference |
| `skills/toastmasters-poster-reviewer/scripts/text_evidence.py` | Supplied font/glyph reproduction; optional local Tesseract fallback |
| `scripts/benchmark_poster_brand.py` | Run supplied specimens; score saved predictions against a separately frozen reference |

The v2 spec is `tm-poster-brand-check/v2`. It accepts `text_runs`, `logos`,
`layers`, `faces`, `color_regions`, `exclusions`, context and output-size facts.
Bounds are integer `[x, y, width, height]` in decoded-image coordinates.

Current execution from the repository root:

```sh
python3 skills/toastmasters-poster-reviewer/scripts/check_brand.py \
  --candidate poster.jpg --spec brand-check.json
```

The current `--evidence` option supplies renderer/source evidence and optional
OCR settings. It is not a model-observation interface. Supplying a model-read
string in `text_runs` alone currently does not corroborate that copy: the text
verifier attempts rendering/OCR and may return BLOCKED.

## 5. Proposed model-observation contract

Add an explicit model-observation input and adapter. Do not reinterpret the
existing renderer log as proof of a model observation, or fabricate a renderer
recipe for text that the model read.

Illustrative **proposed**, unimplemented payload:

```json
{
  "format": "tm-poster-observations/v1",
  "candidate_sha256": "<computed by controller>",
  "coordinate_space": "decoded-image-pixels",
  "producer": {
    "model_id": "<actual provider model ID>",
    "method": "model-image-observation"
  },
  "text_runs": [
    {
      "id": "text-1",
      "bounds": [40, 100, 500, 55],
      "text": "WHERE LEADERS ARE MADE",
      "readability": "clear",
      "role": "tagline",
      "role_reason": "Presented as a separate brand line",
      "font_family": null
    }
  ],
  "unresolved_regions": [],
  "inventory_claim": "partial"
}
```

This is a schema example, not an observation of one of the uploaded posters.
The controller records the actual model identity. The model supplies text,
bounds, roles, ambiguity and visual reasons. Unknown values remain null.
Ambiguous text includes alternatives or an unreadable span; it must not be
silently completed to an official phrase. Model confidence is not a calibrated
probability of correctness and cannot authorize a PASS by itself.

The adapter must:

1. Bind observations to the actual candidate identity and decoded dimensions.
2. Reject invalid/outside coordinates, malformed fields and duplicate IDs.
3. Keep full-image and crop coordinates consistent. Resized crop observations
   need a controller-recorded mapping back to original pixels.
4. Preserve model observations separately from source-backed facts and direct
   pixel measurements.
5. Treat missing inventory fields as unknown, not an empty successful check.
6. Keep rule outcomes tied to their inputs. A successful exact-string comparison
   is conditional on a correctly read and classified string.

## 6. What each check can establish

| Check | Required inputs | Result and limit |
|---|---|---|
| Tagline | Model-read text and tagline classification | Compare exact wording/case with permitted versions; mark basis as model observation |
| Marketing phrases | Relevant text runs and inventory coverage | Apply permitted phrases/count rules; partial inventory cannot establish a poster-wide count PASS |
| Digital logo minimum | Located logo bounds and intended output width | Measure scaled width against applicable minimum; report localization uncertainty |
| Print logo minimum | Logo bounds plus actual physical output width | Calculate inches; JPEG DPI alone does not establish intended print size |
| Logo proportions | Official reference and reliable logo bounds | Compare aspect ratio allowing disclosed raster rounding; uncertain localization is not proof of distortion |
| Logo consistency | Actual crop and trusted official reference | Compression-aware similarity; a mismatch alone is not proof of prohibited alteration |
| Clear space | Logo bounds, applicable source X measurement, nearby foreground regions | Measure boundary/foreground gaps; uncertain ink/boxes need review |
| Palette/gradients | Model-selected design regions and actual image | Measure actual pixels; JPEG drift/source-recipe uncertainty must be disclosed; photo colors are excluded by classification |
| Exact font family/effects | Actual font/source rendering evidence | Verify when supplied; model resemblance alone cannot prove family or absence of effects |
| Photograph/illustration relevance | Model classification and context | Retain as model judgment; Python cannot independently prove the semantic classification |

Bounding boxes from model inspection are estimates. Borderline spacing/size
decisions need refined localization or source geometry. A repeatable calculation
on an inaccurate box is still inaccurate.

File SHA-256 binds observations/results to one file version. It never compares
an embedded logo with an original or establishes visual correctness. Compression
changes the file identity, so a newly compressed export needs new observations
and measurements.

## 7. Result policy

Keep three evidence categories visible: `model observation`, `pixel measurement`
and `source verified`. A rule may be evaluated using a model observation, but
the result must not be described as independent machine confirmation of what
the model saw. Conditional findings still help the user act on a legible poster.

PASS means that a specific applicable rule is satisfied on the supplied evidence;
REVISE means a demonstrated defect; BLOCKED means required evidence is unresolved;
INFO means a metric, preference or requirement not numerically specified.

List demonstrated defects and unresolved checks independently. For example, a
clearly read altered tagline can produce a model-observed REVISE while font
identity remains BLOCKED. An empty/partial text inventory must not produce a
poster-wide marketing-phrase PASS. This is a required correction to the current
v2 empty-list count behavior.

Current v2 aggregates BLOCKED before REVISE at the scoped-verdict level and
REVISE before BLOCKED within each feature. The proposed adapter/report must
preserve known defects visibly; matching two overall BLOCKED results is not
successful validation. A full brand verdict remains separate from these checks.

## 8. Luna operating instructions

The production extraction prompt should give Luna the following bounded task:

> Inspect the actual poster and provided crops. Transcribe visible text and
> locate text, logos, photos, illustrations and QR regions in original-image
> coordinates. Record uncertainty and unknown font/source/context facts. Do not
> repair text, infer official provenance, invent measurements, classify every
> slogan as an official tagline, or apply brand-rule verdicts during extraction.
> Return the observation schema. After the controller runs the checker, report
> its exact findings with the evidence basis, defects and unresolved checks.

Use one full-image extraction followed by targeted crops where necessary. Bound
retries, preserve earlier observations and record corrections. Never keep
re-reading until a failing string happens to match an approved phrase. The model
must not alter rules, measurements or statuses while summarizing a report.

## 9. Validation needed for the requested goal

The target is **Luna image interpretation plus script**, compared with an
independent Sol review of the same actual poster and available source facts.
The old executor-only protocol in `tests/poster_executor_prompt.md` tests a
different task: running a checker on already prepared inventories.

For each fresh round, Tester supplies five positive and five negative specimens.
Withhold inventories generated from fixture source, generator labels and Sol
answers from Luna. Source assets genuinely available in the intended user flow
may be provided equally to both reviewers. Freeze Luna observations, code and
predictions before revealing Sol's judgments. Record extraction errors, missing
regions, incorrect roles, rule-engine errors and reporting changes separately.

Score per-feature agreement, case verdicts, demonstrated-defect detection,
false acceptance/rejection and abstention. Report completed coverage as well as
accuracy: an all-BLOCKED pipeline cannot meet the goal. Run JPEG compression,
Chinese text, wordmarks, absent logos, ambiguous text and missing-source cases.
Retesting development cases after a fix is regression evidence.

Previously reported 154/155 feature agreement and 59/60 scoped decisions came
from supplied-inventory Python runs against Sol references. They do not establish
Luna's extraction accuracy or end-to-end parity. Subsequent OCR changes also
changed the code revision; those earlier scores belong to their frozen revision.

## 10. Implementation status and remaining work

| Component | Status |
|---|---|
| Versioned rules, image measurements and source comparisons | Implemented, with documented limits |
| Optional Tesseract branch | Exists in current code; excluded from this requested model-fed design |
| Explicit model-observation schema/adapter | Proposed here; not implemented |
| Model-read copy results with retained evidence basis | Requires adapter/report change |
| OCR-free execution mode for this workflow | Requires implementation; omitting OCR settings does not disable current fallback |
| Partial/empty inventory phrase-count guard | Requires implementation |
| Luna extraction prompt and tool orchestration | Specified here; not validated with the requested model |
| GPT-5.6 Luna + script versus GPT-6.1 Sol | NOT RUN |

This document is a design handoff. No executable behavior was changed in the
documentation turn. The next implementation must add the observation adapter,
explicitly disable external OCR for this route, retain evidence distinctions,
and test the complete image-to-report path with the actual requested model.

## 11. Revision: practical visual review versus source audit

### Problem exposed by real posters

The supplied-inventory benchmark assumed rich source evidence. Ordinary users
upload flattened posters. The prior ten-poster runs largely reported that an
inventory was missing; they did not complete a useful visual brand assessment.
Missing evidence is not a demonstrated design defect. A checker can be strict
about documented requirements without requiring every poster author to supply
font files, renderer logs and a complete editable-layer manifest.

The product should default to **visual brand review**. A separate **source
audit** can be requested when exact font identity, production colors, asset
provenance or source preservation must be verified. This is a proposed change
to workflow and result policy; the existing CLI still implements its v2 behavior.

| Question | Default visual review | Optional source audit |
|---|---|---|
| Is an appropriate logo/wordmark visible, legible and apparently undistorted? | Model inspection with image/crop measurements when supported | Compare trusted original artwork and source transforms |
| Does the design use the brand palette? | Inspect design fills, text and accents; measure suitable actual regions; account for JPEG/export uncertainty | Verify source swatches, formulations and gradient recipes |
| Does typography have an apparent brand conflict? | Inspect hierarchy, visible styles and effects; qualify exact family as unverified | Verify font files and actual glyph rendering |
| Is clear space sufficient? | Inspect nearby ink and canvas edges; measure where localization supports it | Verify source geometry and applicable X measurement |
| Is the picture permitted and appropriate? | Assess visible relevance and prominence | Verify permissions separately from visual compliance |
| Are all production layers available? | Not required for image review; model must inspect the full image and relevant crops | Required only where the requested audit depends on them |

Visual review does not report an exact font PASS merely because a typeface looks
similar. It can report overall visual PASS with a note that exact font identity
was not verified. Missing evidence for a source-only property does not veto that
separate visual verdict. Conversely, a readable visible defect remains REVISE
even if sources were never supplied.

### Verdict contract

Proposed output separates `visual_brand_verdict` from `source_audit_verdict`.
The source audit defaults to NOT_REQUESTED. Source-only facts may be recorded as
NOT_VERIFIED without creating a visual defect. Keep `full_brand_verdict` separate;
visual review is not official approval or release authorization.

For the visual verdict:

1. REVISE when an applicable mandatory visual requirement has a supported
   violation. Preserve this result even when other items need review.
2. BLOCKED when no demonstrated violation is available but a necessary visual
   decision cannot be made: image unavailable, logo unreadable, relevant text
   ambiguous, material region uninspected, or contextual ambiguity that changes
   a mandatory rule. List the specific unresolved question.
3. PASS when applicable visual checks were actually inspected with adequate
   evidence and no supported violation or blocking visual uncertainty remains.
   State the review scope and source-only facts not verified.

PASS cannot be inferred solely from an empty defect list. Record an explicit
inspection result for each applicable visual category, including applicability
and the regions supporting it. An empty/partial text inventory cannot establish
absence of prohibited phrases. Model observations are accepted as model evidence,
not mislabeled as independently verified pixels or source facts. The report must
make clear which decisions depend on them.

Recommended user-facing wording: “PASS — visual brand review. Exact font identity
and original-asset provenance were not verified.” Reserve blocking questions for
facts necessary to decide the visible requirement; do not ask for every source
file as a default intake checklist.

### Calibration from the three user-accepted examples

These are user-provided acceptance references, not independently established
officially approved examples. Retain the expected positive label and any actual
rule disagreement separately. Do not hard-code image hashes, club names, labels
or special exceptions to make these specific images pass. Uploaded images stay
private; this document records only general design characteristics.

| Reference | What a practical visual review should recognize | What it must not infer |
|---|---|---|
| Blue/maroon AI project-management poster | Recognizable globe logo, primary-color layout, yellow accents, a relevant speaker portrait and clear information hierarchy | Missing font files do not prove a typeface violation; photographic colors do not constitute off-palette design colors; the three-line benefits copy is not automatically three official marketing phrases |
| Blue District poster-design training poster | Official wordmark is a valid alternative to the globe; white/gray/yellow support the primary blue; speaker photography is relevant | Do not require a globe in addition to the wordmark. Classify “EVERYONE CAN GLOW” before deciding whether it is an event slogan or prohibited custom District identity; an unresolved material classification must be disclosed |
| Blue coaching case-discussion poster | Recognizable globe logo, restrained brand colors, readable Chinese copy and a topic illustration inside the case panel | The manual supplies no Chinese-font whitelist. Architecture/family illustrations should be assessed in their supporting meeting-topic role, not treated automatically as prohibited photography subjects |

These observations explain why missing sources alone should not reject the
examples. They are not final pixel-measured verdicts for the new uploads. For
example, logo clear space near a canvas edge still needs inspection against the
applicable rule; a user-accepted label cannot override a demonstrated shortfall.

### Guardrails against making the checker indiscriminately permissive

Pair each accepted reference with negative controls: an obviously distorted or
recolored logo, an obscured wordmark, a measured insufficient margin, a large
off-palette design fill, a genuinely altered official tagline, or an unreadable
critical region. Keep correct photographs, allowed wordmarks, secondary
illustrations and unspecified Chinese fonts as positive controls. Changed logo
appearance and topic-versus-identity classification require their own evidence.

Evaluate both false rejection of acceptable designs and false acceptance of
actual violations. Unresolved disagreements with the user's labels must remain
visible. Three accepted references are development cases; use new unseen posters
to assess generalization. Do not loosen a numeric brand requirement or invent
a blanket color tolerance simply to improve this small set's score.

### Implementation consequences

The next code change should add the model-observation adapter and explicit
visual/source review scope together. The model supplies transcriptions and region
classifications; the script validates the schema, applies rules and performs
supported measurements. External OCR is not required for that route. Keep the
existing strict v2 source/layout path available as an audit, rather than silently
changing what its old PASS results meant.

This revision changes the local design document only. It does not implement the
adapter, rerun the new uploads, certify Luna 5.6 behavior or update the existing PR.

## 12. Implemented optional image-measurement route (2026-10-26)

`check_brand.py --observations` now accepts `tm-poster-vision-check/v1` inputs.
The actual format and commands are documented in the script README. New modules
are `vision_review.py` (model-input adapter/result policy), `logo_vision.py`
(SIFT/RANSAC, template fallback, transform/clear-space/appearance measurements),
and `color_vision.py` (polygon masks, deterministic Lab k-means and spatial
color-residual analysis). OpenCV is optional; legacy v1/v2 behavior is retained.

The new route uses model-supplied search regions, masks and readable copy,
without external OCR or model API calls. Logo matching needs a suitable reference
asset, not proof of the poster's original authoring file. It preserves original
geometry before rectification, evaluates localized alterations separately from
average residuals, and reports histograms/PCA as diagnostics. Coarse masks have
explicit unclassified/boundary/detail accounting. Small isolated color outliers
are disclosed without pretending they are independent design swatches; coherent
wrong-color regions remain defects. Gradient/blend membership is not recipe proof.

The route supports nine selected measurement names for existing requirements:
logo detection, geometry, appearance, clear space, effects and size, design
palette, tagline and marketing phrases. It does not cover all 26 registered
requirements or all model-semantic questions. Consequently `scoped_verdict` is
the operative output, while whole-brand and whole-visual verdicts remain
NOT_ASSESSED. An optional source audit remains separate. This implements a
useful subset of section 11, not its entire future product workflow.

`tests/build_poster_vision_cases.py` adapts existing private fixtures; their source
regions are explicitly not model-extraction evidence. Actual available exports
of the three real designs use visually prepared model observations. Their newer
high-resolution chat versions were unavailable as local files. Frozen-run results,
test counts, false-pass correction and remaining gaps belong in
`design/poster-vision-validation.md`. Exact Luna 5.6 execution remains NOT RUN.
