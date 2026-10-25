# Three-role poster checker validation

The requested team consists of separate Tester, Reviewer and Programmer agents.
The Tester starts with two rounds and adds further rounds while meaningful
improvements remain. Every scored round has five intended positive and five
intended negative specimens. Positives are defined against their stated target
features, not as official approval of the entire poster.

## Evaluation protocol

1. Tester supplies neutral specimen IDs, actual images, reference assets,
   source evidence and the feature scope. Intended labels stay separate.
2. Reviewer inspects the actual specimens and manual independently, without
   intended labels or checker results, and freezes page-cited per-feature
   judgments. Reviewer disagreements with intended labels are retained.
3. Programmer uses round one for diagnosis and general implementation changes.
   Code must not use specimen IDs, filenames or hashes as verdict shortcuts.
4. Programmer freezes code identity and new-round predictions before receiving
   that round's reviewer judgments. Record any intent leakage or reused samples;
   a prediction freeze alone does not establish a fully blind holdout.
5. Compare individual feature decisions, including demonstrated defects and
   missing evidence. A global BLOCKED verdict cannot conceal a missed defect.
   Record false acceptance, false rejection, abstentions and uncovered features.
6. If changes follow a held-out failure, record the previous result; a rerun of
   the same cases is regression evidence rather than a new held-out trial.

Official downloaded assets and derived specimens remain private local test
artifacts. Only original/shareable generator code, synthetic regression tests
and nonprivate evidence summaries belong in repository changes. Source hashes
identify files; visual consistency is measured separately. Neither model
agreement nor automated tests establishes official TI approval or guarantees
correctness for every future poster.

## Recorded development and initial evaluation

The first authoritative dataset is versioned `cases-v3`. Earlier versions are
retained: two purported negatives originally had contradictory metadata or
missing evidence rather than visibly incorrect posters. The independent
Reviewer rejected those intended labels. Two actual-defect replacements made
the authoritative first two rounds five scoped positives/five actual negatives
each. Sample intent was partly disclosed during coordination; neither round is
claimed as an untouched blind holdout.

The Reviewer froze judgments before opening the Tester's intended-label file.
All 20 authoritative sample-level labels agreed with the independent review.
There are 68 individual feature judgments across all 26 registry keys; this does
not imply both positive and negative branch coverage for every key.

Round-one agreement progressed from 31/40 to 35/40 and then 40/40. This is
development-set agreement after using that round's reviewer feedback.

Round-two predictions were saved before its reviewer oracle was released.
Initial agreement was 20/28: eight mismatches, zero false accepts, zero false
rejects and six abstentions under the runner's explicit categories. The two
other mismatches were INFO versus PASS and REVISE versus BLOCKED. Scope-level
verdicts agreed for 8/10 cases. These results remain recorded even after fixes.

Further evaluation results, revised-scope scores and remaining gaps are recorded
below as execution completes. Matching an abstention caused by inadequate
checker input is distinguished from reproducing the reviewer's observed result.

## Requested model identities

The user subsequently specified GPT-6.1 Sol as the reference and GPT-5.6 Luna
plus the script as the proposed budget pipeline. The earlier reviewer is kept
as a development reference and is not relabeled as GPT-6.1 Sol.

A new independent agent was explicitly launched with `gpt-6.1-sol` and high
reasoning, without conversation history. It inspected the same actual images,
manual and neutral evidence, and froze fresh judgments before seeing intended
labels, previous oracles or checker results. The first five rounds have 135
individual reference feature decisions across 50 scoped cases. Round three's
duplicate means these are 49 unique images. The explicit reference retains one
literal BLOCKED scoped decision where known defects coexist with unresolved
measurement coverage; it is not silently converted to REVISE for scoring.

The benchmark scorer now reports literal reference scoped decisions separately
from defect-first summaries and per-feature agreement. It rejects missing or
duplicate cases/targets and changed candidate identities. Prediction runs check
code, manifest and evidence identities before/after execution and create fresh
output artifacts rather than overwriting frozen ones.

GPT-5.6 Luna has not been selectable in this session. GPT-6 Luna is available,
but is a different model and has not been substituted without user selection.
Direct Python execution tests the checker; it is not evidence of a GPT-5.6 Luna
model trial. The reproducible budget execution prompt and controller checks
are in `tests/poster_executor_prompt.md`. Exact requested model-pair parity
remains NOT RUN until that model is accessible or an alternative is agreed.

## Final checker regression against GPT-6.1 Sol

The final Python checker revision reproduced the following independent Sol
judgments. These are scoped feature results with supplied image/source evidence,
not whole-poster approvals or a budget-model execution trial.

| Round | Feature agreement | Literal scoped decisions |
|---|---:|---:|
| 1 | 40/40 | 10/10 |
| 2 | 27/28 | 9/10 |
| 3 | 23/23 | 10/10 |
| 4 | 24/24 | 10/10 |
| 5 | 20/20 | 10/10 |
| 6, frozen before review; no subsequent code change | 20/20 | 10/10 |
| Total | 154/155 | 59/60 |

Each round contains ten scoped cases, with five intended positive and five
negative specimens. Round three has nine unique images across ten different
target scopes; the other first-five rounds have ten unique images each. Earlier
results, rejected sample versions and uncertainty controls remain preserved.
Final reruns after development fixes are regression evidence, not new untouched
holdout trials. All 26 feature registry keys are targeted across the first two
rounds, without a claim of exhaustive branch coverage.

Before the corresponding fixes, frozen predictions scored against the explicit
Sol reference were 21/28 in round two, 20/23 in round three, 21/24 in round four
and 19/20 in round five. In particular, round five exposed a genuine missed
drop shadow: a supplied offset hint was not tried by the pixel verifier. The
general correction tries bounded hints and accepts them only when the rendered
effect matches actual pixels; a false-hint negative regression guards against
trusting that metadata. Its later 20/20 is a regression result. Initial-round
scores using the earlier development reviewer are retained separately above.

The remaining round-two difference is `face_overlap`: Sol identifies an
overlapping drawing as nonphotographic and returns INFO; supplied metadata calls
it a photo, while the checker cannot establish that semantic distinction and
returns BLOCKED. The actual logo overlap/clear-space defects are still detected.
There were no false accepts or false rejects under the scorer's defined
categories in these six final runs. That does not imply universal correctness.

Round six contained ten unique 1200×1600 posters, with 119 inventoried artifacts
verified unchanged. Independent Sol review confirmed five scoped positives and
five negatives (clear space, tagline, body font role, logo size and shadow).
The reference was frozen without seeing predictions or intended labels. The
already-frozen checker predictions matched all 20 features and all ten literal
scoped verdicts on the first comparison; no code changes followed that review.
The body-font result depends on supplied body-copy classification: the same
family is allowed for subheadings. Input semantics still need independent review.
The full six-round set contains 60 scoped cases and 59 unique images.

Refinement stops at this point: the fresh sixth round exposed no additional
objective discrepancy, while the unresolved face-category distinction requires
semantic evidence. Neither a fixture-specific exception nor changing the oracle
would constitute a general improvement. The exact requested model-pair goal
remains unverified until GPT-5.6 Luna can execute the fixed operator protocol.

Improvements driven by actual discrepancies include JPEG quantization,
subsampling and block-phase handling; source-verified foreground overlap;
font-file identity plus observed glyph reproduction; independently corroborated
copy and shadow effects; and logo-family-specific applicability. Supplied hints
only guide candidate measurements and must reproduce actual pixels. Hashes
record input/code identity, never visual brand correctness. Unsupported source,
inventory completeness and semantic claims remain explicit review gaps.

Final production validation: 87 focused poster tests and 134 complete repository
tests passed locally. The full suite required loopback socket access for existing
SVG-editor tests. Candidate-manifest validation includes new script/test files:
24 packages, 19 portable skills, reference synchronization and whitespace checks
passed. Six platform/Python CI combinations are configured; execution on other
platforms and CI remain NOT RUN. Exact GPT-5.6 Luna operator fidelity also remains
NOT RUN. No commit, push, PR or publication was performed.

Private per-round predictions and scores are retained outside the repository as
`final-rN-predictions.json` (rounds 1–5),
`round6-v1-frozen-predictions.json`, and `final-rN-61sol-score.json`; source identities and
candidate/evidence hashes are recorded inside each prediction artifact. Round
six predictions were frozen separately before its independent Sol review.
An independent repeated Python execution of all ten round-six cases produced
byte-identical JSON to that freeze, including all findings and source identities.
This demonstrates deterministic execution for those inputs in this environment;
it does not substitute for the unavailable budget-model trial.

Round-six prediction SHA-256:
`9e6e6875fdc47db542fb3cf2f3b6574e5451d6e760e1ee5973af36b0773ee123`.
Independent reference SHA-256:
`3f8679e021c4986551936d3d55df960f7779e48424021e1b8797b7d82e636f63`.
Score SHA-256:
`e42909c2abbcda73d6fe8246690f81aec1f568abccf4e188c73d61568cbb5b39`.

## Uploaded ten-poster OCR retry

The ten uploaded JPEGs were copied only to private temporary storage. A local
`chi_sim` Tesseract trained-data file was downloaded to `/tmp` and supplied via
the neutral evidence bundle as `eng+chi_sim`; it is not part of the repository.
The checker now accepts the OCR language and tessdata directory from that bundle
and requests TSV explicitly, so a minimal Tesseract installation does not rely
on an optional `tsv` config file. A dedicated regression test covers this path.

OCR-derived text runs were generated for the ten actual images and rerun through
the checker. Per-image copy corroboration covered 5/8, 1/7, 1/3, 0/3, 2/8,
3/8, 1/1, 1/6, 2/5 and 3/8 selected runs respectively. These are copy
observations only, not complete inventories; Chinese OCR, small text, stylized
text and QR contents remain fallible. Every poster's scoped verdict stayed
BLOCKED because official logo source/layout evidence and complete color/layer
inventories were still absent. The retry therefore did not claim brand PASS or
REVISE from OCR alone.

The poster-focused suite passed 88 tests and the complete repository suite
passed 135 tests after this OCR change.
