# Installation verification record — 2026-10-16

This record separates observed packaging behavior from native client loading and workflow results. It covers the 23 tracked packages at baseline commit `1af81e05acacde766f51e4aeeeb7a6134faa4198`, not concurrent uncommitted contributor work or future repository revisions.

**Provenance.** Coordinated, reviewed and committed by the repository maintainer, Git identity `yui.yi <yui.yi@alibaba-inc.com>`. The repository inspection, the three-role review and the implementation were carried out with native Codex CLI subagents (`codex-cli 0.162.0-alpha.17.2`, the same client inspected for discovery below). Agent session identifiers were not recorded in these documents; cite the Git identity and the commit revision to locate the authors.

**Status.** Verification run for baseline revision `1af81e05`, written before the change landed. The implementation it informed landed in commit `6cfe32f` "Improve skill installation guidance and package validation". The revision-anchored, independently reproduced re-check of these claims is [skills-installation-recheck-2026-10-16.md](skills-installation-recheck-2026-10-16.md); read the two together, since the figures here describe revision `1af81e05` only.

## Environment and isolation

- Released npm package: `skills@1.7.2`. Registry metadata requires Node `>=22.20.0`. The downloaded tarball's SHA-512 matched npm registry integrity metadata.
- Test runtime: bundled Node `v24.19.0`; npm `10.9.2`. The terminal's existing Node `v22.13.1` did not meet this package's requirement and was not changed.
- Local client inspected/attempted: `codex-cli 0.162.0-alpha.17.2`.
- Installer source: a temporary export of tracked `skills/` files only. No user outputs, private ignored downloads, local test artifacts, or Git metadata were copied.
- Installation targets: two temporary projects, one for the complete collection and one for selected poster companions. Installer state/cache/config were redirected with XDG variables. `HOME` and `CODEX_HOME` were not overridden.
- An OS sandbox blocked writes under the real user home. Package installation commands additionally ran with networking disabled. Dependencies for the installer were provisioned beforehand into a fresh temporary consumer project, using pinned `skills@1.7.2`, lifecycle scripts disabled, a temporary npm cache and separate empty npm config files.
- Existing home-directory agent presence could still affect agent detection. This was project isolation with protected home writes, not a fresh OS user or hermetic virtual machine. No actual global skill install/update/removal was performed.

The released package executable was invoked directly through the selected Node runtime. This tests the released CLI's behavior; it does not test every user's `npx` bootstrap, GitHub download path, proxy, authentication, operating system or global installation.

## Observed results

| Check | Observed result |
|---|---|
| Preview local exported collection | Exit 0; skills discovered. |
| Install all, project scope, `--skill '*' --agent codex --yes` | **PASS: 23 expected IDs matched 23 installed IDs.** |
| Supporting file integrity | **PASS: all 96 tracked package files present and byte-identical by SHA-256.** |
| Target-client isolation | No `.claude/`, `.hermes/` or `.codex/` project directories appeared. Codex used `.agents/skills/`. |
| Selective installation | **PASS:** maker, reviewer and SVG editor installed together with exactly those three inventory IDs. |
| Named local-source update | Exit 0 but printed `No installed skills found matching`. **Not evidence of an update.** Use an inspected scoped reinstall for unsupported local-source tracking. |
| Named Codex-only removal | Printed success/exit 0, but maker's canonical directory and inventory entry remained. **Removal was not established.** The released implementation retains a canonical copy when another detected agent still uses its path. |
| Removal with `--agent '*'` | **Rejected** by the released CLI as `Invalid agents: *`, despite an upstream README example. Do not publish that form as tested removal syntax. |
| Named removal without agent filter, current test project | **PASS:** removed maker across project-agent aliases; reviewer, SVG editor and a user-file sentinel survived. This intentionally broadens client scope and is not an automatic fallback for client-specific removal. |
| Global installation/lifecycle | **UNVERIFIED:** no global mutations tested. |
| Fresh Codex discovery/loading | **BLOCKED / UNVERIFIED:** isolated app-server startup returned `Operation not permitted` before responding to `initialize`, including after SQLite/log directories were redirected to temporary storage. |
| Harmless fresh-session task | **BLOCKED / UNVERIFIED:** ephemeral read-only execution failed to initialize its in-process app-server client under the home-write restrictions; no model/task events were emitted. |
| Advanced workflows | **UNVERIFIED:** no poster, agenda, translation or presentation output was produced by this installation test. |

The client failures were local isolation/runtime failures, not evidence that a skill failed to load. No client activation or end-to-end support certification is claimed. A follow-up in a disposable OS user, VM/container that supports the actual client, or another supported isolated client environment should complete the loading and harmless-task checks.

## Commands exercised

Below, `skills` represents the provisioned released package executable; `SOURCE` is the tracked-file export, and each command runs in its intended temporary project. These are a record of test operations, not a request to execute them on a user's installed collection.

```text
skills --version
skills add SOURCE --list
skills add SOURCE --skill '*' --agent codex --yes
skills list --agent codex --json
skills add SOURCE --skill toastmasters-poster-maker toastmasters-poster-reviewer edit-svg-canvas --agent codex --yes
skills update --project toastmasters-poster-maker --yes
skills remove toastmasters-poster-maker --agent codex --yes
skills list --agent codex --json
skills remove toastmasters-poster-maker --yes
skills list --agent codex --json
```

Successful exit status is never the sole assertion. Tests compared actual package names, files and hashes, checked remaining names after removal, and preserved an unrelated user-file sentinel. The unsafe assumption that Codex-only removal must make a shared skill disappear caused the initial lifecycle assertion to fail; that finding informed the documented postchecks.

## Repository code checks

Before implementation, the original 17 unit tests passed with localhost binding allowed. The default command sandbox blocked eight editor tests at server bind; granting local loopback access resolved those environmental failures.

The engineer added 13 focused package-check tests and reported a clean baseline export with only the four owned implementation paths overlaid: **30 tests OK, one Git-only test skipped**. That checkout-discovery test passed separately in the live checkout. The clean export also passed the 23-package static check, the 18-entry portable validator and poster reference synchronization. The engineer and reviewer working reports were not retained in the repository and are not reachable from a clone; the reproducible replacement for that pointer is [skills-installation-recheck-2026-10-16.md](skills-installation-recheck-2026-10-16.md), which re-runs these checks at revision `6cfe32f`.

Concurrent contributor changes arrived during implementation in the shared working directory. At the engineer's check, the whole live suite had two missing-reference subtest errors in `test_contributor_prompts`, and portable validation referenced a missing contributor entry point. These are recorded separately from installation-change results; the concurrent work was preserved. A clean isolated pass must not be described as a whole-live-checkout pass.

## Durable evidence and reproduction

The sanitized CLI summary, command harness, released package metadata, installation inventory and stdout/stderr logs were kept in a Git-ignored working directory for the duration of this run; they are not part of the repository, a clone, or a pull request, so no reader of this file can open them. Disposable test paths were under `/private/tmp/d85-install-verification-raowkb__/`; they are evidence from that run, not a required installation location. For checks that can be reproduced from inside the repository, use [skills-installation-recheck-2026-10-16.md](skills-installation-recheck-2026-10-16.md) instead of relying on that working directory.

For a repeat test, use a fresh temporary project and matching tracked-file export, provision the pinned CLI with a compatible Node runtime, redirect its state/cache, block writes to the real user installation, and compare names and file hashes. Then test actual client discovery and a harmless task separately. Use a disposable OS user or VM when stronger isolation is required; a temporary folder by itself is not an OS sandbox.

Primary references: [released Skills CLI package](https://www.npmjs.com/package/skills/v/1.7.2), [npm release metadata](https://registry.npmjs.org/skills/1.7.2), [official Codex skill discovery and invocation](https://learn.chatgpt.com/docs/build-skills), and [Codex configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference).
