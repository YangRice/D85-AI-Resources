---
name: toastmasters-poster-reviewer
description: Use when independently reviewing an existing Toastmasters poster or a maker candidate for documented brand rules, accurate content, visual quality, protected assets and QR integrity.
---

# Toastmasters Poster Reviewer

Review a supplied Toastmasters poster independently or serve as the maker's separate quality gate. This skill reviews; it does not alter the poster, produce a replacement, submit approval requests or publish. Read [brand rules](references/brand-rules.en.md) and [review contract](references/production-contract.en.md), both included in portable editions. Baseline: `tm-poster-brand-2026-08-v1`, Brand Manual Version 2.0 Rev. 08/2026.

## Establish evidence and context

Obtain the actual candidate, SHA-256/revision, approved brief/copy, context, target display/print size, and available manifest, original protected assets, source/font provenance and permissions/approval evidence. A standalone poster may lack a manifest: inspect what exists and request only evidence necessary for a required check. A description or maker's assurances do not substitute for inspecting the actual image.

For a maker quality gate, use a different agent/session from the designer. In portable tools start a fresh conversation with these instructions/rules and attach the candidate/brief only after authorization for any external transmission. Never simulate independent approval in the maker conversation. If the image cannot be inspected, return BLOCKED for image-level review with preliminary findings only.

Classify ordinary club/Area/Division/District, corporate, Gavel or annual District conference before applying rules. Check conference eligibility, not just its title. Never apply the conference custom-brand exception to an October/fall event. Distinguish meeting-topic copy/secondary seasonal illustrations from custom organizational identity.

## Inspect five categories

1. **Brand compliance:** assess each applicable B01–B15 rule with page evidence: official logo variant/proportions/provenance; final-size minimum and clear space; palette/allowed gradients; hierarchy/standard font styles; photography and secondary artwork; approved phrase/tagline; Pathways relevance; corporate/Gavel/conference rules. Photo colors need not match palette. Preferred corner placement is not compulsory. Do not invent a Chinese-font approval list or apply certificates/merchandise authorization to every ordinary poster.
2. **Content accuracy:** for meeting/event posters verify the required meeting brief and, when a keynote speaker or sharing master is featured, their name, approved introduction and exact topic. Ask for missing required evidence; do not approve unresolved facts. Compare all visible regions against approved text, date/time/timezone, names, venue, meeting IDs, links/contact, spelling, translations and completeness. OCR helps but never replaces readable visual inspection. If the brief conflicts with itself, flag the specific unresolved fact.
3. **Visual quality:** inspect at full resolution and intended mobile/display size for contrast, clipping, overlap, hierarchy, glyphs, stray model lettering/fake logos, and safe reserved regions. Compare SVG rendering with PNG when source exists. Editable means text/assets/positions; raster background is not fully editable vector art. For standalone review without an editable-source requirement, absent SVG alone is not a defect.
4. **Protected-material integrity:** compare portraits/documentary photos and official graphics to originals and provenance; no unapproved retouching, cropping, recreated people or distortion. Verify manifest/source hashes when supplied; do not infer preservation merely from visual similarity. Keep exact supplied QR source separate from generated artwork.
5. **QR integrity:** decode every QR on the actual final poster and each QR region; match original decoded payload and confirmed destination, retain modules/quiet zone and proportions. A plausible-looking QR cannot pass. Unavailable decoder or unreadable/wrong payload prevents QR PASS. Report online reachability separately from payload correctness; no unauthorized navigation to private invites. No QR is not applicable.

## Evidence-based verdict

Use the review-contract report. Cite rule ID/manual page for official findings; label practical recommendations separately. Do not invent measurements for flattened images: exact fonts, physical scale, hashes and permissions may be unverified. Font similarity is an observation, not proof; obtain font/source evidence when needed for typography PASS. Missing physical scale prevents print-size verification, not digital-only review. Unknown permissions are not proof of absent permission; report them as unresolved release evidence, separately from visual design.

PASS requires actual-image inspection and no unresolved required design checks. REVISE indicates demonstrated correctable defects. BLOCKED indicates missing required verification or conflicting constraints; list any known correctable defects as well. Tie verdict to candidate checksum and record each category, region, evidence, rule/page or recommendation, required fix and unverified check.

Report external authorization independently: not applicable, evidenced, required/pending or unknown. A conference design may visually pass while its required Brand Team approval is pending; it cannot be called release-authorized. Local PASS is never official TI approval. Preserve missing-approval evidence rather than automatically emailing anyone.

Recommend overlay corrections for copy, spacing, official assets and QR issues before artwork regeneration. Any candidate change invalidates the old verdict and requires full-category review on its new checksum. The default is to stop after three unsuccessful maker review cycles with the latest draft/hash and unresolved issues; honor explicit user authorization to refine beyond that default, keeping changed candidates versioned and independently re-reviewed. The maker must recompute the accepted checksum at delivery.
