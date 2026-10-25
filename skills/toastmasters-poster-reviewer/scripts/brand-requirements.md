# Manual audit and executable coverage

Original PDF fetched and examined 2026-10-24, 44 pages, Version 2.0 Rev.08/2026.
URL and SHA-256 are recorded in `brand_rules.json`; `--rules` exports both and
all machine rule data. Printed page numbers equal PDF page numbers in this copy.
Reviewed text and diagrams, including clear-space figures and transparency
examples. The original PDF/assets remain private; only rule paraphrases and
measurement code are distributed. This table distinguishes objective poster
checks from subjective judgments and other media's rules.

| Manual pages | Requirement | Executable treatment / limits |
|---|---|---|
| 1–3 | Cover, contents, contacts | Provenance/version/hash; no design check |
| 4–6 | Values, promise, voice/tone | Semantic judgment, always retained in manual review |
| 7 | Section divider | No requirement |
| 8–9 | TI logo/wordmark variants, 72 px / .75 in, wordmark-height clear space | Source variant; actual pixel recipe; intended-size dimensions; source wordmark measurement; clear-space ring and layer bounds |
| 10 | Official lockups | Source matching/provenance; no invented independent lockup minimum |
| 11 | No custom organizational identity; rules still apply without logo | Context/identity flags checked; semantic classification of meeting topic remains manual |
| 12 | No perspective, distortion, altered elements/colors, busy pattern, overlaps, glow | Transform/aspect/source comparison, layer/clear-space intersections and pixels. Authenticity, visual context and patterned glow beyond regions remain manual |
| 13 | Member badges use logo standards | Official source, inherited dimensions and clear-space checks |
| 14 | Four solid colors; RGB, CMYK and Pantone values | Actual designated RGB regions; exact source formulation checks; no RGB→CMYK inference |
| 15 | Primary dominance and secondary support | Coverage and primary-region area metrics. No published percentage cutoff; semantic prominence remains manual |
| 16–18,20 | Three endpoint pairs, linear/radial gradients; gray opacity 20% increments | Pair validation, per-pixel horizontal/vertical/radial recipe comparison, alpha blending, gray step validation. Other rendering functions need review, not invented bans |
| 19–20 | Transparency treatments, good contrast | Blend recipes; contrast ratio measurement. 70% is an example, no universal opacity/contrast threshold invented |
| 21 | Pathways variants, 72 px / 1 in, “Pathways” height clear space | Source/size/clear-space checks |
| 22 | Badge association, not decoration | Required association and decorative-use flag; actual relevance is semantic, so manual |
| 23–25 | Font families and roles, standard styles, no word art/shadows | Source family/role/effect metadata; optional font-file name/hash verification; actual renderer evidence needed. No unsupported Chinese whitelist or mandatory H1/H2 weights |
| 26 | Section divider | No requirement |
| 27 | TM photography, illustrations secondary, image permission | Exclusions and layout inventories available for measurement; semantic subjects/prominence and legal permission remain manual/external |
| 28 | Logo/photo contrast, faces, clear space, preferred corners | Face/layer-box intersection and ring/ratio measurements; verify ink/masks. Contrast/legibility/competition manual; no corner mandate |
| 29 | Exact tagline case; one marketing phrase; phrases not over faces | Exact strings, distinct-phrase count, full supplied copy scan, face-box intersections. Translations/classification and contrast/competition manual |
| 30 | Section divider | No requirement |
| 31 | Brand portal, approval procedures | External evidence; not something image code can verify |
| 32–33 | Email signature/stationery template resources | Other media, no new numerical poster requirement |
| 34 | Section divider | No requirement |
| 35–36 | Certificate/product authorization, vendor/order rules | Other media/procedural evidence; not automatically applied to an ordinary poster |
| 37 | Website disclaimer/footer; no rehosting/restricted materials | Website/distribution scope, not a poster rule. Website audits need actual site content and rights evidence; not claimed implemented here |
| 38 | Video logo/credits, permissions, disclaimer ≥15 seconds, approval | Video scope, not a static poster rule. Requires timeline/media inspection; not claimed implemented here |
| 39 | Corporate placement and TM branding | Logo overlap/top-bottom geometry, ambiguous side-by-side referred to review; normal TM color/font checks still run |
| 40 | Official Gavel replacement, no alteration/custom tagline | Context/logo/variant/source/identity and inherited normal-usage checks. Gavel banner template production is outside poster scope |
| 41 | Annual April/May conference exception; district+annual-conference wording; identity expiry; sponsor section; standalone TI | Date/annual/as-of/end checks, supplied visible identifiers, logo/section geometry. Third-party rights and Brand Team approval remain external, not inferred |
| 42 | FAQ divider | No requirement |
| 43 | Old emblem restricted; both primary colors permitted for club/District; physical badge/ribbon/pin/banner rules | Pre-2011 asset metadata flagged; no club/District color restriction. Manufacturing/template rules outside poster scope |
| 44 | WHQ tests not replicable; TI IP | Experimental asset flag checked; approval/rights evidence manual/external |

“Objective” does not mean inferable from a flattened image. Exact font family,
print inches, logo source authenticity and event eligibility need actual source
or contextual evidence. Source declarations can be checked for consistency but
can still be wrong. Findings preserve that distinction. No whole-brand PASS is
issued by this script. No source-free object detection, legal authorization or
AI judgment is disguised as a deterministic test.

Both versions now use compression-tolerant visual logo screening rather than
requiring exact source-render pixels. Source-file hashes remain provenance
bookkeeping only, with trusted reference checksums required. Screening matches
are conditional visual consistency, not proof of authenticity or unchanged bytes.

V1 was a narrow swatch checker. V2 adds page-cited source/layout checks and
coverage, and keeps v1 compatibility. JPEG pixel drift is treated as incomplete
verification, addressing the earlier sample poster's yellow-color ambiguity.
