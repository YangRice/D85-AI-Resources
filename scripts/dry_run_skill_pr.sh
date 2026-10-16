#!/usr/bin/env bash
# Dry-run harness for PRs produced by the d85-skill-contributor skill.
#
# Replays the deterministic part of a contribution in a throwaway sandbox:
#   - rebuilds a fake upstream from the PR's base revision (no real history)
#   - applies the candidate commits on top in an isolated worktree
#   - runs the six repository checks and verifies generated-prompt parity
#   - reports the changed-file scope and any paths needing human review
#   - emits a task spec (dryrun-task.md) for the behavioral trial agent
#
# The behavioral trials (two fresh conversations: realistic task + missing
# input) require an AI agent and are dispatched separately using the emitted
# spec. This script performs no writes outside its own scratch directory,
# never changes global git config, and never pushes anywhere.
#
# Usage:
#   scripts/dry_run_skill_pr.sh --pr N                     # real PR via gh (needs auth + network)
#   scripts/dry_run_skill_pr.sh --source REPO --ref REF    # local mode, base = merge-base(REF, HEAD)
#   scripts/dry_run_skill_pr.sh --source REPO --ref REF --base BASE
set -euo pipefail

UPSTREAM_URL="https://github.com/YangRice/D85-AI-Resources.git"
WORKROOT="${TMPDIR:-/tmp}/d85-skill-pr-dryrun"

mode=""
pr_num=""
source_repo=""
ref=""
base=""

usage() {
    echo "usage: $0 --pr N | --source REPO --ref REF [--base BASE]" >&2
    exit 1
}

while [ $# -gt 0 ]; do
    case "$1" in
        --pr) mode="pr"; pr_num="$2"; shift 2 ;;
        --source) mode="${mode:-local}"; source_repo="$2"; shift 2 ;;
        --ref) mode="${mode:-local}"; ref="$2"; shift 2 ;;
        --base) base="$2"; shift 2 ;;
        *) usage ;;
    esac
done

[ -n "$mode" ] || usage
if [ "$mode" = "pr" ]; then
    command -v gh >/dev/null 2>&1 || { echo "error: --pr mode needs the gh CLI" >&2; exit 1; }
    [ -n "$pr_num" ] || usage
fi
if [ "$mode" = "local" ]; then
    [ -n "$source_repo" ] && [ -n "$ref" ] || usage
fi

workdir=$(mktemp -d "$WORKROOT.XXXXXX")
echo "Sandbox: $workdir"

# 1. Obtain base and candidate from the source.
if [ "$mode" = "pr" ]; then
    read -r base head_oid < <(gh pr view "$pr_num" --json baseRefOid,headRefOid \
        -q '[.baseRefOid, .headRefOid] | join(" ")')
    git clone -q "$UPSTREAM_URL" "$workdir/seed"
    git -C "$workdir/seed" fetch -q origin "pull/$pr_num/head"
    git -C "$workdir/seed" branch --force pr-candidate "$head_oid"
    archive_source="$workdir/seed"
    candidate_source="$workdir/seed"
    candidate_ref="pr-candidate"
else
    if [ -z "$base" ]; then
        base=$(git -C "$source_repo" merge-base "$ref" HEAD 2>/dev/null) || true
        [ -n "$base" ] || { echo "error: could not determine base; pass --base" >&2; exit 1; }
    fi
    archive_source="$source_repo"
    candidate_source="$source_repo"
    candidate_ref="$ref"
fi
echo "Base: $base"

# 2. Build a fake upstream (single squashed commit) from the base tree.
mkdir "$workdir/tree"
git -C "$archive_source" archive "$base" | tar -x -C "$workdir/tree"
if [ -z "$(ls -A "$workdir/tree")" ]; then
    echo "error: base revision $base could not be archived" >&2
    exit 1
fi
git -C "$workdir/tree" init -q
git -C "$workdir/tree" add -A
git -C "$workdir/tree" -c user.name="FakeUpstream" -c user.email="upstream@test.local" \
    commit -qm "fake upstream snapshot: simulated base for dry-run"
git -C "$workdir/tree" branch -M main
git clone -q --bare "$workdir/tree" "$workdir/fake-upstream.git"

# 3. Isolated worktree; canonical URL is insteadOf-mapped to the fake remote.
git -c url."$workdir/fake-upstream.git".insteadOf="$UPSTREAM_URL" \
    clone -q "$UPSTREAM_URL" "$workdir/worktree"
git -C "$workdir/worktree" config url."$workdir/fake-upstream.git".insteadOf "$UPSTREAM_URL"
git -C "$workdir/worktree" fetch -q "$candidate_source" "$candidate_ref"
git -C "$workdir/worktree" checkout -q -b candidate FETCH_HEAD

# 4. Scope report.
echo "=== Changed files (main vs candidate) ==="
changed=$(git -C "$workdir/worktree" diff --name-only main candidate)
echo "$changed" | sed 's/^/  /'
echo "=== Scope warning (human review) ==="
outside=$(echo "$changed" | grep -vE '^(skills/|prompts/|catalog/|\.github/|docs/|design/)' || true)
if [ -n "$outside" ]; then
    echo "  WARNING: paths outside the usual skill-package dirs:"
    echo "$outside" | sed 's/^/    /'
else
    echo "  none"
fi

# 5. The six checks from the skill's section 4, run with base-revision tooling.
cd "$workdir/worktree"
set +e
failures=0
run_check() {
    echo "=== $* ==="
    if "$@"; then
        echo "PASS"
    else
        echo "FAIL"
        failures=$((failures + 1))
    fi
}
run_check python3 scripts/build_portable_prompts.py
echo "=== regeneration parity (git status must be empty) ==="
if [ -n "$(git status --porcelain)" ]; then
    echo "FAIL - generated prompts are out of date:"
    git status --porcelain
    failures=$((failures + 1))
else
    echo "PASS"
fi
run_check python3 scripts/validate_skill_packages.py
run_check python3 scripts/validate_portable_skills.py
run_check python3 scripts/sync_poster_references.py --check
run_check python3 -m unittest discover -s tests
run_check git diff --check main candidate
run_check env BASE_SHA=main python3 scripts/scan_skill_safety.py
set -e

# 6. Identify contributed skill packages for the behavioral spec.
skill_ids=$(echo "$changed" | sed -nE 's|^skills/([^/]+)/.*|\1|p' | sort -u | tr '\n' ' ')
echo "Contributed skill ids: ${skill_ids:-none (no skill package changed)}"

if [ -n "$skill_ids" ]; then
    cat > "$workdir/dryrun-task.md" <<EOF
# Behavioral dry-run task spec (generated by dry_run_skill_pr.sh)

Deterministic checks: see terminal output above (failures: $failures).
Sandbox workdir: $workdir
Candidate branch in worktree: candidate
Fake upstream (bare): $workdir/fake-upstream.git
Contributed skill id(s): $skill_ids
Portable prompt(s) to load for the trial agent: $workdir/worktree/prompts/<id>.en.md
 (copy from 'Instructions for the AI' through 'End of instructions')

Dispatch a fresh agent conversation with ONLY the portable prompt plus:
- HARNESS: upstream base URL is insteadOf-mapped to $workdir/fake-upstream.git
  (same mapping as used to build this sandbox). Hard boundaries: no 'gh', no
  network, nothing outside $workdir, global git config untouched.
- SCENARIO: derive a realistic-task and a missing-input scenario from the
  skill's own description; script the member's replies; set expected behavior
  before each run; label all trial evidence contributor-reported.
- GATE: the agent must push its branch to the mapped remote and then stop at
  the authorization/PR boundary honestly (no PR created, no PR claimed).
Then verify independently: bare-repo branches, diff scope, checks re-run in a
fresh clone, real repo and real GitHub untouched, transcript free of gh/network.
EOF
    echo "Behavioral task spec: $workdir/dryrun-task.md"
else
    echo "No skill package changed - behavioral trials not required for this PR."
fi

echo "Deterministic check failures: $failures"
exit "$failures"
