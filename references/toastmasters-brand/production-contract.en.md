# Poster production and review contract

## Required meeting and featured-speaker brief

These are user-required production checks, not additional official brand rules. For meeting/event posters, before event-specific design establish meeting identity/theme or purpose, organizer/audience, date/year, start/end/timezone, format/location or online access, and attendance instructions when applicable. Read existing materials first and ask only for required details that are missing or conflicting. Event-only fields are not applicable to evergreen posters without a meeting/event; do not invent a date or speaker.

Establish whether a keynote speaker or sharing master/featured presenter is included. For each featured person obtain their name, approved short introduction and exact talk/sharing topic; ask when any is missing. Do not infer credentials or invent a topic. A portrait is conditional on the chosen treatment; confirmed text-only treatment is valid. Explicitly no featured speaker makes this check not applicable. Keep unresolved required facts in the brief and ask for answers before event-specific layout/rendering; asset organization may continue.

The reviewer checks these facts against the supplied brief. Missing required brief evidence prevents final content approval and needs clarification; information established in the brief but incorrectly omitted from the candidate is a revision finding. Do not give PASS while required meeting/speaker/topic facts remain unresolved.

## Intermediate and composite files

Use one coordinate system: top-left origin, x/y/width/height in final-canvas pixels. Manifest format `tm-poster-layout/v1`:

```json
{
  "format": "tm-poster-layout/v1",
  "rule_set": "tm-poster-brand-2026-08-v1",
  "canvas": {"width_px": 1080, "height_px": 1440, "print_width_in": null, "print_height_in": null},
  "context": "ordinary-club",
  "brief": {"audience": "guests", "language": "en", "event_date": "2026-11-01", "timezone": "Europe/Berlin", "approved_copy": ["Open House"]},
  "layers": [
    {"id": "headline", "kind": "text", "x": 80, "y": 100, "width": 920, "height": 150, "text": "Open House", "font_family": "Montserrat", "font_size_px": 64, "font_weight": 700, "color": "#004165", "align": "left", "line_height_px": 76},
    {"id": "portrait", "kind": "photo", "x": 80, "y": 340, "width": 500, "height": 600, "source_path": "/absolute/source.png", "source_sha256": "record-actual-hash", "protected": true, "fit": "contain", "alteration_authorized": false, "permission_evidence": "user supplied confirmation"},
    {"id": "registration", "kind": "qr", "x": 760, "y": 1120, "width": 240, "height": 240, "source_path": "/absolute/qr.png", "source_sha256": "record-actual-hash", "expected_payload": "https://example.org/register", "protected": true, "fit": "contain"}
  ],
  "artwork": {"path": null, "sha256": null},
  "candidate": {"path": null, "sha256": null}
}
```

Use contexts `ordinary-club`, `area`, `division`, `district`, `corporate-club`, `gavel-club`, `annual-district-conference`. Include official logo/badge layers of kind `logo`/`badge` with provenance, bounding box, clear-space measurement and source checksum. Include known clip/crop or transform instructions and explicit user permission where applicable. Fill actual values, not example hashes. Never include secrets in the manifest.

Output: `layout.svg`, `layout-annotated.png`, `layout-clean.png`, `layout.json`, `rendering-instructions.md`, versioned `artwork-rNN.png`, `poster-rNN.svg`, `poster-rNN.png`, and `review-rNN.md`. Use a separate task output directory; never overwrite supplied sources. The guides are production artifacts, not finished posters.

Establish composition through a loose art-direction guide or a complete one-shot proof from authorized raw materials before locking coordinates. Finished benchmark posters are quality evidence, not default generation inputs; do not copy their spatial skeleton. Document the selected design with the layout artifacts afterward. A complete composition proof may render typography to evaluate hierarchy; follow the creative-quality guide for full-composition and material-plus-matte routes. The clean guide shows composition and usable overlay space, without explanatory borders or placeholder text. The annotated preview may show supplied material. If the user authorizes references/subject integration, send only the authorized references needed for art direction; otherwise mask private regions and use position-only guides. QR codes and official graphics remain exact final overlays. Do not upload private supplied material to an external renderer without user authorization for that transmission. Exact overlay copy is authoritative, not model-produced text.

Rendering brief: canvas/aspect ratio; placement hierarchy; B05/B06 palette; B09 imagery restrictions; overlay regions to leave unobstructed; no symbols pretending to be official logos or QR-like patterns. Model lettering may appear in a composition proof; a clean plate for editable text excludes it. Preserve original speaker identity through authorized direct photo integration/matting rather than generative replacement. Inspect actual returned artwork before compositing. Sample exposed background/accent colors against the official palette: image-model prompts do not guarantee exact RGB values. Correct drift using explicit brand-fill overlays following the generated geometry, before text/protected layers; keep the original generated bitmap and its checksum for provenance. Do not apply palette correction to supplied photographs or official logo/QR pixels. Verify complete exposed-background coverage, including seams and strips between corrected regions and opaque panels; a few correct interior samples do not establish whole-background compliance. Record the full correction bounds, align panel boundaries to them, and inspect/measure every remaining exposed generated strip. Never omit a transition gap from the palette review. Do not cover stray lettering with transparent overlays: remove it or rerender the affected artwork. Preserve accepted artwork hash across overlay-only revisions.

Composite text stays SVG text (with explicit wrapped lines); generated artwork is an embedded raster layer, not editable vector art. Embed official graphics/photos/QR assets in the local SVG to avoid broken links; include font requirements and any substitution disclosure. Use licensed fonts; do not redistribute proprietary font files. In SVG/CSS quote family names containing numeric tokens, for example `font-family="'Source Sans 3'"`; an unquoted numeric family token can silently fall back to a serif font. Confirm the rendered glyphs and actual local font resolution, not only the manifest declaration. Large embedded source photographs may exceed a renderer’s XML/data-URI limits: use a renderer that supports the known local SVG size or a proportional derived display asset with recorded original/derived hashes; never weaken source preservation or crop to bypass a limit. Reopen/render the composite SVG, compare the exported PNG, check clipping and glyphs, and confirm overlays appear above artwork. When a QR is supplied inside a screenshot, a direct extraction may remove surrounding screenshot chrome only: preserve the entire QR card and quiet zone, record source/extraction bounds and hashes, and verify the extracted payload against the whole original. Do not crop modules or quiet zones, and retain visible expiry information in the brief and poster disclosures. Exact source bytes and decoded QR modules/payloads remain protected; scaling QR codes uses integer module scaling/nearest-neighbor with quiet zone retained, never cropping, recoloring, stretching or lossy export. Photos retain their original source checksum. Authorized crop/matting may alter the displayed silhouette; record source, mask and transformation and preserve face/body appearance. Otherwise maintain the full original aspect ratio. Official logos retain proportions and approved colors.

For a requested print PDF, confirm dimensions, final logo widths, and print requirements; do not label an RGB export as CMYK/press-ready without verification. Physical inch requirements cannot be checked from a raster poster without scale information.

## Review contract

Give a separate reviewer the brief, actual immutable candidate, its SHA-256, manifest, original protected files, official asset sources, rule-set version, and available permission/approval evidence. Do not give the expected verdict. The maker cannot certify its own candidate. A dependency bundled into a prompt is guidance, not evidence of an independent review. In a portable chat, open a new conversation, paste the reviewer instructions and bundled rules, and attach the actual candidate and brief. Without a separate agent/session, hand off an **unreviewed draft**, not PASS. A local reviewer can inspect authorized local evidence; sending private candidate images or originals to an external review chat/service requires authorization for that transmission, just as external rendering does.

```text
Candidate/revision:
SHA256:
Rule-set version:
Evidence inspected:
Design verdict: PASS | REVISE | BLOCKED
Brand compliance:
Content accuracy:
Visual quality:
Protected-material integrity:
QR integrity:
Findings: region; observation; rule ID/manual page OR practical recommendation; required fix; evidence
Unverified checks: what is missing; impact; how to verify
External authorization: not applicable | evidenced | required/pending | unknown
```

PASS requires actual-image inspection and no unresolved required check. REVISE means a demonstrated correctable defect; BLOCKED means a necessary check cannot be completed or a constraint cannot be met. If both exist, use BLOCKED and list all correctable defects too. External approval is separate: a design can pass visual checks with approval pending, but it is not release-authorized. Unknown photo-use permission is reported separately from visual compliance and cannot be invented. Unknown exact fonts in a flattened image: report visual similarity as an observation, exact identity unverified; request editable/font evidence before PASS on typography. Missing physical scale blocks print-size verification, not an otherwise inspectable digital-only review. A described-only candidate is a preliminary assessment, not an image-level PASS.

Compare every text region with approved copy: dates/timezone, names, venue, meeting ID, links, contact, language, spelling and completeness. Do not infer correctness from OCR alone. Check every QR in the full final image and its region, compare with original decoded payload and expected destination. Distinguish payload correctness from online URL reachability; do not navigate private invite destinations without authorization. Missing decoder, unreadable QR or wrong payload prevents QR PASS. No QR means not applicable, not blocked.

Invalidate approval on any pixel/file change. Prefer overlay fixes for copy, spacing and protected assets; rerender only defective artwork. Review all categories again on the new checksum. The default production stop is three unsuccessful review cycles, unless the user explicitly authorizes further refinement, such as reaching a visual benchmark. Honor that scope, version outputs and continue independent review; never claim success on a failed candidate. External requests or publication are never automatic.

For each output size, place QR assets directly from the preserved source rather than resizing an already scaled composite QR again. Decode every intended export, including mobile derivatives. Inspect authorized matte edges against the actual background; remove stage/lectern remnants and abrupt alpha boundaries without reconstructing faces or bodies.

## Image reconstruction evidence

For the maker's image-input route, extend `tm-poster-layout/v1` without changing its existing required fields. Add `input_image` with `path`, `sha256`, `width_px`, `height_px` and `mode: "reconstruction"`. For each decomposed layer record its existing ID/kind/bounds plus `z_index`, `group_id`, `representation` (`text`, `vector`, or `raster`), `editable_properties`, `source_bounds`, `confidence`, and `limitations`. Use null for unknown evidence, not guessed provenance. Record any OCR uncertainty, font substitution, asset extraction/repair and original/derived hashes. Document source-to-SVG differences and the temporary edit/export/reopen test in `reconstruction-report.md`.

Reconstruction may use the source artwork instead of image-model rendering; record generation as not applicable when none was needed. Existing layout/guide, final PNG/SVG, source-integrity, editor-delivery and review requirements still apply. The reviewer checks both visual fidelity and editable structure: visible copy must be real text, reconstructable shapes must be independent vector objects, and retained raster artwork must not duplicate replaced text or foreground components. Distinguish movable raster assets from editable vector content. Missing original assets or unreadable text remain explicit evidence gaps; source fidelity cannot override brand rules or justify a false PASS.
