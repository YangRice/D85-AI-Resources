# Budget-model execution protocol

This protocol tests whether a budget model can execute the checker and preserve
its decisions. It does not ask that model to replace an independent reference
review. Record the actual provider model ID and reasoning setting; do not label
a different model as GPT-5.6 Luna. That exact model has not been selectable in
this session. A direct Python run tests the checker, not model adherence.

Give the executor only this prompt, a neutral manifest path, repository path and
a fresh prediction-output path. Withhold reviewer oracles, intended labels,
fixture generators and previous model answers.

## Prompt

You are the execution operator for a poster checker. Use the provided manifest
and local evidence exactly as supplied. Do not modify the poster, specification,
evidence, checker, manifest or target feature selection. Do not invent missing
fonts, coordinates, source identity, permissions or image observations.

From the provided repository directory, execute:

```sh
python3 scripts/benchmark_poster_brand.py run --manifest MANIFEST_PATH --out FRESH_OUTPUT_PATH
```

Use tool arguments for paths; preserve spaces and non-ASCII characters. Read the
saved JSON result. For every sample, return its `id`, `candidate_sha256` and the
exact statuses in `features`. Preserve PASS, REVISE, BLOCKED and INFO without
reinterpretation. Report all samples; do not omit failures or uncertainty.
Include the prediction file path and reported checker revision. Report a failed
command or unavailable tool truthfully. Never manufacture a completed run.

Do not inspect or guess independent reviewer answers, use fixture names as
verdict hints, or change the output to make it look compliant. If asked for a
human summary, keep it separate from the exact machine decisions.

## Controller checks

1. Verify actual model identity, exact prompt and unchanged neutral inputs.
2. Verify that a prediction artifact exists and its IDs, candidate hashes and
   feature statuses exactly match the executor's returned rows.
3. Score the saved predictions against the separately frozen GPT-6.1 Sol oracle
   using `scripts/benchmark_poster_brand.py score`. Report feature agreement,
   literal scoped decisions, known-defect detection and abstentions separately.
4. Count missing cases, changed targets, fabricated artifacts or changed statuses
   as executor failures, even if a shortened summary appears to agree.
5. Report both executor fidelity and checker/reference agreement. Success at one
   does not establish the other. Repeated direct Python execution can establish
   deterministic outputs for tested inputs but cannot stand in for this model
   trial.
