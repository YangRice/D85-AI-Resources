# Installation re-check record — 2026-10-16, revision `6cfe32f`

Purpose: make the installation claims in [the verification record](skills-installation-verification-2026-10-16.md) checkable from inside the repository, at the revision that adds the installation guide. This record is an independent re-run, not a copy of the earlier working copy: every number below was observed in this run.

**Provenance.** Performed by Hermes Agent (Nous Research) on 2026-10-16 at the request of the repository maintainer, Git identity `yui.yi <yui.yi@alibaba-inc.com>`, revision `6cfe32f`. It is a repeat, by a different tool, of the packaging and lifecycle checks first reported in the verification record for baseline `1af81e05`.

**Status.** Executed. Limits are stated below; the checks it does not cover are named explicitly rather than implied.

## Environment

- Host: macOS; `node` v26.7.0, `npm` 11.19.0 (the host Node satisfied the CLI requirement; the earlier run had to supply a bundled runtime).
- Installer: released `skills@1.7.2`, fetched through `npx` and reported as `1.7.2`. Registry metadata confirmed independently at this revision: version `1.7.2` exists, is the `latest` dist-tag, and declares `engines.node = ">=22.20.0"`.
- Checks: Python 3.9.6 (the `3.10+` figure in the maintainer section describes a supported floor; the checker itself runs on 3.9).
- Source revision: `6cfe32f2cccea688c3922a6c4c6924c327c7cafa`, exported with `git archive` so only tracked files were installed.

## Isolation and limits

- All work happened in one disposable directory with `HOME`, the npm cache and `XDG_CONFIG_HOME`/`XDG_CACHE_HOME`/`XDG_DATA_HOME` redirected inside it. The directory listing after the run contained only `home/`, `npm-cache/` and the disposable test projects; the real user home was neither read for agent detection nor written.
- Network access was used to fetch the pinned CLI from the npm registry. The earlier run tested package commands with networking disabled; this run does not re-establish that condition.
- No global installation, update or removal was performed, and there is no claim about global behavior.
- No real client start-up was attempted. The earlier record's **BLOCKED/UNVERIFIED** client-discovery and harmless-first-task results therefore stand unchanged; nothing here supersedes them.
- Installer behavior depends on which agent directories exist in `HOME`; see the removal results below, where this run differs from the earlier one for that reason.

## Results

| Check | Observed in this run |
|---|---|
| Install all, project scope, `--skill '*' --agent codex --yes` | Exit 0. **24 expected IDs = 24 installed IDs**; `skills-lock.json` lists 24 entries. |
| Supporting file integrity | **101 tracked package files, 101 installed, 0 missing, 0 hash mismatches, 0 extra** — byte-identical by SHA-256. |
| Target-client isolation | The project contained only `.agents/` and `skills-lock.json`. No `.claude/`, `.hermes/` or `.codex/` directory appeared. |
| Selective installation `--skill toastmasters-poster-maker toastmasters-poster-reviewer edit-svg-canvas` | **Exactly those three IDs installed** in a second disposable project. |
| Named local-source update, `update --project toastmasters-poster-maker --yes` | Exit 0, printed `No installed skills found matching: toastmasters-poster-maker`. **Not evidence of an update**, matching the earlier record: a local directory source is not tracked for update. |
| Named removal with `--agent codex --yes` | Reported success, and in this environment the canonical directory and inventory entry were gone. The earlier run observed a **retained** canonical copy because another detected agent still used its path. The difference is environmental (other agent directories under `HOME`), so "removal always leaves a shared copy" is not a general rule — inspect the result after removal. |
| Removal with `--agent '*'` | **Rejected**: `Invalid agents: *`, followed by the valid agent list (`codex`, `claude-code`, `hermes-agent`, …). The published upstream example must not be documented as tested removal syntax. |
| Named removal without an agent filter | 23 of 24 skills remained, `toastmasters-poster-maker` was removed, and an unrelated user file in the project survived. This intentionally broadens client scope. |
| Global installation and lifecycle | **Not run** — unchanged from the earlier record: global removal routes remain documented, not verified. |

## Repository checks at this revision

| Command | Observed |
|---|---|
| `python3 scripts/validate_skill_packages.py` | Exit 0 — `Validated 24 skill packages (local static checks only).` |
| `python3 scripts/validate_portable_skills.py` | Exit 0 — `Validated 19 skills (7 journey, 12 atomic) and 9 optional actions.` |
| `python3 scripts/sync_poster_references.py --check` | Poster reference bundles match canonical sources. |
| `python3 -m unittest discover -s tests` | Live checkout: `Ran 36 tests`, OK, no skips. Clean export without `.git`: `Ran 36 tests`, OK, 1 skipped (the checkout-discovery test). The two contributor-prompt failures the verification record noted at its check time are resolved at this revision because that work is now committed. |
| `git diff --check` | Clean. |
| Documented clean-export flow (`docs/installation.md` → Maintainer checks) | Reproduced with a `git archive` export plus a `git ls-files` manifest: exit 0, `Validated 24 skill packages`. The same command without `--tracked-files` fails with a raw `git rev-parse` error instead of the intended "exports need `--tracked-files`" message. |
| Failure case | Removing a bundled package directory (`skills/translate-pdf/references`) produced two actionable errors — missing linked file and missing bundled file — and exit 1. |
| Local link and anchor check of `README.md`, `docs/installation.md` and the four installation records | Every relative target exists and is tracked, and every heading anchor resolves. |

## Not covered here

Client discovery, harmless first task, advanced workflows, global installation, and removal behavior with multiple agent directories present. The earlier record's `23` packages and `96` files are correct for its baseline `1af81e05` and are not restated as current; at this revision the corresponding figures are `24` packages and `101` files.

## Commands exercised

`S` is a `git archive` export of the tracked revision; each project command ran in a disposable project directory with the redirected environment described above.

```text
S="$BASE/src"; git archive HEAD | tar -x -C "$S"; git ls-files > "$BASE/tracked.txt"
npx --yes skills@1.7.2 --version
npx --yes skills@1.7.2 add "$S" --skill '*' --agent codex --yes
npx --yes skills@1.7.2 list --agent codex --json
npx --yes skills@1.7.2 add "$S" --skill toastmasters-poster-maker toastmasters-poster-reviewer edit-svg-canvas --agent codex --yes
npx --yes skills@1.7.2 update --project toastmasters-poster-maker --yes
npx --yes skills@1.7.2 remove toastmasters-poster-maker --agent codex --yes
npx --yes skills@1.7.2 remove toastmasters-poster-maker --agent '*' --yes
npx --yes skills@1.7.2 remove toastmasters-poster-maker --yes
python3 scripts/validate_skill_packages.py
python3 scripts/validate_portable_skills.py
python3 scripts/sync_poster_references.py --check
python3 -m unittest discover -s tests
git diff --check
```

Successful exit status is never the sole assertion: package IDs, file hashes, remaining names and a user-file sentinel were compared directly. To repeat, use a fresh disposable directory, redirect `HOME`, the npm cache and the XDG variables, export the revision with `git archive`, and compare names and SHA-256 hashes before testing client discovery separately.
