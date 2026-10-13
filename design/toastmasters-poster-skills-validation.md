# Toastmasters poster skills validation

Validated locally on 2026-10-13. Scope: maker/reviewer skill packages, canonical bilingual references, official source inventory, local asset helper, catalog integration and generated prompts. No publication, global skill installation, approval submission, commit or push was performed.

## Automated checks

- Nine stdlib unit tests pass: portable reference embedding and capability notes; generated EN/ZH poster prompts match canonical generator output and contain no unresolved local reference links or duplicated shared rule bundle; standalone reference copies and unique source IDs; changed downloads preserve the baseline; fresh caches detect changes against bundled snapshots; ZIP inventory excludes metadata and rejects unsafe paths; selective ZIP reading fetches only the requested member; aggregate range-byte limits are enforced.
- Official skill-creator quick validation passes for both packages (PyYAML supplied from a temporary validation directory).
- Repository portable-skill validation passes: 17 skills (6 journey, 11 atomic) and 9 optional actions.
- Reference synchronization check passes. Scoped tracked diff whitespace check passes. Official asset cache is ignored by Git.

## Behavioral evaluation

A read-only baseline agent, before the new skills existed, identified the described brand/date/QR defects against the supplied manual. It already knew these content rules; no claim is made that the new skill was necessary to detect every defect. The new skills add the reproducible production, evidence and independent-review contracts.

A separate forward reviewer inspected an actual 1000×1300 PNG, source logo, original QR and approved brief. It independently computed the checksum and decoded the whole image and QR region. It detected the planted wrong date, wrong QR payload, distorted/undersized logo, insufficient spacing, unsupported purple/orange gradient, decorative Pathways badges, dominant mountain illustration and ineligible October annual-conference naming. It returned BLOCKED with correctable defects and unresolved exact-font evidence, separately reporting external authorization as unknown. It did not invent official approval.

A maker forward evaluation exercised ordinary club recruitment/open house, corporate club, Gavel Club, qualifying April annual District conference, ordinary District training, and bilingual open house in a text-only environment. All six resulted in incomplete layout/rendering/review handoffs, preserving portrait/QR placement and refusing a false finished-poster/PASS claim.

Independent reviews found and prompted repairs to maker-only helper wording in the reviewer bundle, Chinese opacity/color pairings, external-review transmission authorization, busy-background/logo-overlap restrictions, and selective-download aggregate time/byte budgets.

## Rendered compositing smoke check

A deterministic synthetic fixture (not image-model output and not a certified poster) produced an annotated SVG/PNG guide, clean SVG/PNG guide and composite SVG/PNG using Sharp. Chinese/English text rendered visibly. The clean protected regions remained blank. Final photo-fixture and QR regions matched the original decoded pixels exactly. ZXing decoded both the whole final image and QR region to the original approved payload.

An initial smoke assertion correctly caught an incorrectly assumed QR dimension (330 rather than the supplied 370 pixels). The fixture was corrected to use source dimensions rather than resampling; the preservation checks then passed. This validates why the production contract requires checking source dimensions/modules.

Actual image-model rendering was not exercised in this initial synthetic smoke check. A subsequent real-material test on 2026-10-13 exercises the image model, local overlays and independent review; its private artifacts and report are under `test-poster/test-run-2026-10-13/`. The initial tests validate instructions, failure handling, resource integrity and deterministic overlay feasibility; they do not prove every image model will follow a layout or create a compliant poster. Every real poster still requires the stated image inspection and independent review.

## Official material inspection

The supplied 44-page Version 2.0 August 2026 manual contains 24 unique external URI hyperlink targets. All are inventoried, plus the current official online manual. The online cover still matches August 2026. Seven logo/wordmark/lockup/member/Pathways/Gavel ZIP archives were fully downloaded and inventoried privately with SHA-256 and formats. Official font pages and relevant supporting/permissions pages were inspected; HTML font-source access is not treated as a font installation or license verification.

The official photograph ZIP is 502,863,180 bytes. Its 37 JPEG members were inventoried with HTTP ranges; one 5,039,476-byte photograph was selectively downloaded, decoded and visually inspected (3952×2305). The full archive was neither downloaded nor hashed. Inventory and selected-member checksums are explicitly distinct from a full archive checksum. The helper supports selecting further photographs without bulk downloading.

The Brand Portal redirects to sign-in; no authentication boundary was bypassed. Unrelated shop/email/stationery/video links were inventoried and marked outside poster scope rather than fetched. Source statuses, timestamps, hashes, filenames and documented usage boundaries are in the canonical asset-source inventory. Original files remain in the ignored private cache; official rights are not subsumed by the repository MIT license.

## Reproduce package checks

```sh
python3 scripts/sync_poster_references.py --check
python3 scripts/validate_portable_skills.py
python3 -m unittest discover -s tests
```

For generation, edit canonical skill/reference sources first, synchronize reference copies, then run `python3 scripts/build_portable_prompts.py`. Native package validation uses the official skill-creator `quick_validate.py` with a Python environment containing PyYAML. Behavioral and rendered fixtures were isolated under `/tmp/tm-poster-skill-evaluation`; official asset files are deliberately not committed with the test report.

## Original creative benchmark and final production acceptance

The first generated design was rejected by the user for reproducing the benchmark's spatial skeleton. The maker was refined to derive a new visual premise from the event and to use finished examples as quality criteria, not default generation inputs. A fresh ImageGen proof used only the authorized original speaker photo, establishing a distinct zero-to-speech editorial composition. Its aesthetic acceptance did not complete production: serif raster text, dominant decorative art and uncontrolled palette required reconstruction. The first editable reconstruction passed the Toastmasters review but met only the aesthetic floor. A further full raw-material ImageGen proof and exact editable translation restored expressive hierarchy, original portrait integration and comparable QR footprints.

Final production candidate `test-poster/production-test-2026-10-13/poster-r03.png` (private, ignored) is 4800×8000; the separately composited mobile preview is 720×1200. SHA-256: `9c86f8c862534ff2897e100979de6fdcaf0f7ac0d69bbe6453734dde192b81c6`. Two separate reviewers inspected this same immutable candidate:

- Independent aesthetic reviewer: **MEETS_TARGET; ORIGINALITY PASS**, compared with the original target and minimum examples, not merely with the previous revision.
- Independent Toastmasters reviewer: **PASS for the local historical test**, across brand, complete content, visual quality, protected materials and QR integrity.

The source photograph's RGB is preserved through documented proportional derivation; only authorized alpha/crop/fade changes integrate the person. Official wordmark bytes match the independently inspected original archive. The master meeting/group codes equal exact 3×/2× nearest-neighbor source replications; both original payloads decode from whole master, master regions and whole/region mobile exports. No invitation URL was visited. All six supplied originals remain unchanged. Thirty-seven SVG text nodes remain editable, actual licensed Latin fonts resolve, and independently reopening the embedded SVG yields a byte-identical master PNG. Full intermediate layout, clean/annotated guides, manifest, rendering handoff and both checksum-bound reports are saved privately beside the poster.

Public photo rights, live invitation validity, physical print dimensions and press readiness remain unverified and are outside this local historical test. Expiry/history disclosures remain visible. The acceptance proves this tested execution, not a guarantee that every future model or brief passes. Every subsequent candidate still requires both applicable final gates.
