# Upstream skill installation research

**Provenance.** Coordinated, reviewed and committed by the repository maintainer, Git identity `yui.yi <yui.yi@alibaba-inc.com>`, working with native Codex CLI subagents (`codex-cli 0.162.0-alpha.17.2`). Agent session identifiers were not recorded; cite the Git identity and the commit revision to locate the authors.

**Status.** Pre-implementation source research. The commands below were taken from upstream documentation and source and were not executed in this repository; the released-package behavior D85 actually documents was measured separately and recorded in [the verification record](skills-installation-verification-2026-10-16.md) and [its re-check](skills-installation-recheck-2026-10-16.md).

Accessed: 2026-10-16. Scope: primary GitHub repository READMEs and source, read only; no package or skill was installed. This is a selected popular sample, not an exhaustive ranking. Stars are rounded figures displayed by GitHub during this inspection and can change. Commands below document upstream behavior; they have not been executed here. Source on `main` can differ from the currently published npm package.

## Popularity and distinct distribution models

| Repository | Observed stars | Role |
| --- | ---: | --- |
| [obra/superpowers](https://github.com/obra/superpowers) | 300.5k | Workflow framework distributed through client plugins/extensions |
| [anthropics/skills](https://github.com/anthropics/skills) | 181.6k | Claude examples and document skills |
| [vercel-labs/skills](https://github.com/vercel-labs/skills) | 35.2k | Cross-client installer CLI |
| [vercel-labs/agent-skills](https://github.com/vercel-labs/agent-skills) | 32.5k | Skill collection using that CLI |

The two Vercel repositories serve different purposes; a collection need not reproduce its installer's entire manual.

## Anthropic collection

The README leads Claude Code users through registering `anthropics/skills` as a plugin marketplace, then choosing `document-skills` or `example-skills`. It also gives direct plugin-install commands. Its first-use example explicitly names the PDF skill and a file to process. Claude.ai and API users are sent to separate platform documentation. Skills are folders containing instructions, scripts, and resources; document skills have different licensing from many examples. The inspected README does not provide a unified dependency bootstrap, update/remove walkthrough, or diagnostic checklist. [README](https://github.com/anthropics/skills#try-in-claude-code-claudeai-and-the-api)

Dependency requirements also live inside individual skills: the PDF skill demonstrates Python libraries and command-line utilities, gives an OCR package-install example, and links additional reference/form instructions. Copying only `SKILL.md` would omit referenced material. This establishes task-level setup guidance, not evidence that installing the collection automatically installs those tools. [PDF skill](https://github.com/anthropics/skills/blob/main/skills/pdf/SKILL.md)

## Vercel collection

First install is `npx skills add vercel-labs/agent-skills`. The collection says relevant tasks activate installed skills automatically and supplies concrete performance-review/deployment prompts. Its package description includes optional `scripts/` and `references/`, rather than treating a skill as a lone Markdown file. It publishes immutable discovery releases with an artifact per skill. The README does not itself give a runtime prerequisite checklist, client path table, update/remove steps, or troubleshooting section; those belong principally to the linked installer. The `npm ci --ignore-scripts` example builds discovery artifacts and should not be mistaken for an ordinary end-user installation prerequisite. [README](https://github.com/vercel-labs/agent-skills#installation)

## Vercel installer: user-facing lifecycle

The CLI separates project installation (default) from global (`-g`), supports client selection (`--agent`), skill selection (`--skill`), preview (`add SOURCE --list`), and copying (`--copy`). Symlinks to a canonical copy are recommended. Its client table includes Codex, Claude Code, and Hermes. It provides installed inventory (`list`), update and remove commands, including named skills and scope options. Troubleshooting covers wrong target paths, invalid YAML, missing name/description, and directory permissions. The compatibility table warns that hooks and other advanced features vary between clients. [README](https://github.com/vercel-labs/skills#readme)

```sh
npx skills add vercel-labs/agent-skills --list
npx skills add vercel-labs/agent-skills --skill '*' --agent codex -g
npx skills list -g -a codex
npx skills update -g
npx skills remove -g web-design-guidelines
```

These examples illustrate upstream syntax; they are not a proposed D85 install list. Inventory proves files were registered, while a real task is needed to assess activation and execution.

### Prerequisites and version boundary

At access time, repository `package.json` declares version `1.7.2` and Node `>=22.20.0`. The `npx` route requires an available Node/npm toolchain and network access unless cached; the published npm version was not independently fetched. Repository access also requires suitable credentials for private sources. Avoid documenting a historical Node minimum without checking the version being recommended. [Package manifest](https://github.com/vercel-labs/skills/blob/main/package.json)

### Important command semantics verified in source

`--all` sets skill wildcard, agent wildcard, and automatic yes together. It is broader than “all skills for my chosen client.” `--skill '*' --agent codex` expresses that narrower intent; replace the agent with `claude-code` or `hermes-agent` as appropriate. Quoting prevents the shell expanding `*`. Internal skills remain hidden from wildcard bulk requests unless the internal-skills environment flag is enabled; explicit named requests can include them. Running inside a detected AI agent also changes interactive defaults. [Add implementation](https://github.com/vercel-labs/skills/blob/main/src/add.ts)

The current dispatcher sends `check`, `update`, and `upgrade` to the same `runUpdate` handler. Do not describe `skills check` as a read-only health check or activation test. [CLI dispatcher](https://github.com/vercel-labs/skills/blob/main/src/cli.ts)

The update implementation reads tracking information and can invoke installation and removal operations. Named filters and explicit `-g`/`-p` scopes reduce ambiguity. Some sources or incomplete tracking entries cannot be checked automatically and receive reinstall guidance. This lifecycle is source/version management, not verification of runtime dependencies or task quality. [Update implementation](https://github.com/vercel-labs/skills/blob/main/src/update.ts)

### Client paths

| Agent argument | Project path | Default global path |
| --- | --- | --- |
| `codex` | `.agents/skills/` | `~/.agents/skills/` |
| `claude-code` | `.claude/skills/` | `~/.claude/skills/` |
| `hermes-agent` | `.hermes/skills/` | `~/.hermes/skills/` |

Hermes global paths can follow its configured home. Paths describe the installer, not a guarantee every agent version implements identical discovery behavior. [Agent definitions](https://github.com/vercel-labs/skills/blob/main/src/agents.ts)

### Supporting files and dependency boundary

The installer recursively copies a selected skill directory, excluding `metadata.json`, `.git`, `__pycache__`, and `__pypackages__`. It preserves file permissions, dereferences working symlinks, skips broken symlinks, and can fall back to copying if linking fails. Thus files inside a selected directory normally travel with it; unrelated repository-root assets do not automatically become part of every skill. The inspected directory installer performs file placement rather than a general Python/npm/system dependency bootstrap. [Installer implementation](https://github.com/vercel-labs/skills/blob/main/src/installer.ts)

Discovery parses `SKILL.md` name/description, metadata and standard directories, with plugin groupings and bounded traversal. It does not consult D85's `catalog/skills.json` in the inspected discovery code. Combined with add/installer inspection, there is no evidence that D85 catalog dependency declarations are automatically resolved. Treat that as an architectural inference from the reviewed paths, not an exhaustive proof over every possible provider. D85 should test discovered names against its intended catalog explicitly. [Discovery implementation](https://github.com/vercel-labs/skills/blob/main/src/skills.ts)

## Superpowers framework

Installation is explicitly client-specific and should be repeated for each harness. Current README routes Claude Code through plugin marketplaces, Codex App through sidebar Plugins, and Codex CLI through `/plugins`; it also documents many other clients. This differs from older clone/symlink Codex instructions. Hermes requires restarting active sessions and may lose bootstrap behavior after compaction; a fresh session is suggested if triggering stops. Muse has a concrete first-task check: a fresh-session React todo request should trigger brainstorming before coding. Updates depend on the client, with explicit examples for several clients; there is no single removal walkthrough. A diagnosing skill is the documented response to workflow failures. The framework needs its startup bootstrap and client integration as well as individual skill files. [README](https://github.com/obra/superpowers#installation)

The historical `.codex/INSTALL.md` endpoint did not return usable content during this inspection. Its failure alone does not prove deletion; the current README is the stronger source for present installation guidance.

## Implications for D85's installation design

These are recommendations drawn from the comparison, not claims of already-tested D85 behavior:

1. Lead with one novice path, explicit prerequisites, a client choice, and project/global scope. Keep selective installation available.
2. State the exact catalog/bundle installed and its exclusions. A filesystem-wide wildcard is not a curated catalog contract.
3. Package each skill's necessary references, scripts, templates, and assets together, or provide a tested mechanism for shared root dependencies.
4. Separate three checks: installed inventory, skill activation in a fresh session, and successful representative output with required runtimes/tools.
5. Publish dependency requirements and manual/automatic setup truthfully; installing instructions does not prove Python, office tools, browser tools, credentials, or external services are ready.
6. Add scoped update/removal and short troubleshooting routes. Version-pin examples when reproducibility matters, and verify compatibility against the actual released CLI before publishing.

## Limits

No installers, client activation checks, or generated-output tests were run. No exhaustive GitHub popularity survey or npm-release comparison was performed. Microsoft's collection was not needed to establish the four requested distribution patterns. “Not documented” refers to inspected pages, not the entire project or host platform. All mutable source links reflect material retrieved on the access date.
