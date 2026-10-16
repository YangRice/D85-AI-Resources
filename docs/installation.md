# Installation and first use | 安装与首次使用

Start with the bilingual repository-URL request in the [README](../README.md#install-all-skills-once--一次安装全部技能). It asks for every skill for your client. A retained full checkout is optional for ordinary installation; if you request the complete tracked resource collection, the installer must also retain a checkout and report its archive location separately from the active skill location. Git-ignored private downloads are excluded from both routes.

先使用 [README](../README.md#install-all-skills-once--一次安装全部技能) 的双语仓库链接请求，为当前客户端安装全部技能。普通安装可选择是否保留完整仓库；若要求完整的 Git 跟踪资源库，安装者须另行保留仓库副本，并将资源副本位置与实际技能安装位置分开报告。两种路线都不包含被 Git 忽略的私有下载文件。

## What was verified? | 验证到了哪一层？

| Evidence level / 证据层级 | Required evidence / 所需证据 |
| --- | --- |
| Package presence / 文件存在 | Selected versus installed IDs, complete folders, active location and scope, source revision when available. / 所选与实际安装 ID、完整目录、实际位置和范围、可取得的来源版本。 |
| Client discovery/loading / 客户端发现与加载 | Client-provided skill listing/loading evidence in a fresh session. Files or a plausible answer alone are insufficient. / 新对话中的客户端技能清单／加载证据；文件存在或回答看似合理都不够。 |
| Harmless first task / 无害的首次任务 | Explicit skill request, supplied fictional inputs, observed result and limitations. / 明确调用技能、提供虚构输入、记录结果与限制。 |
| Advanced workflow readiness / 进阶工作流就绪 | Required tools and companions, real artifacts, rendering/inspection and independent review under that skill's contract. / 所需工具及配套技能、真实产物、渲染／查看以及该技能要求的独立评审。 |

Report each level separately as observed, failed, blocked or unverified. Unknown and untested never mean PASS. A successful text task does not certify poster, agenda, PDF or presentation production. Static validators below do not establish any client/runtime result.

逐层报告已观察到的证据、失败、受阻或未验证；未知、未测试不能写成通过。文字任务成功不证明海报、议程、PDF 或演示文稿制作就绪。下方静态检查器不证明客户端或运行能力。

**Route status:** The AI-assisted route and the Codex, Claude Code and Hermes CLI examples are documented routes, not blanket client certifications. CLI syntax is based on released `skills@1.7.2`, inspected on 2026-10-16; its published Node requirement is `>=22.20.0`. Record the actual installer and client versions, date, scope and evidence before calling a route verified. Upstream `main` may differ from the release. A sandbox file-install check alone does not verify client loading.

**路线状态：** AI 协助安装路线及 Codex、Claude Code、Hermes 的 CLI 示例是已记录的路线，不代表所有客户端均已认证。命令语法依据 2026-10-16 检查的已发布 `skills@1.7.2`，其 Node 要求为 `>=22.20.0`。声称某路线已验证前，须记录实际安装器和客户端版本、日期、范围与证据；上游 `main` 可能不同于发布版。沙盒文件安装检查不等于客户端加载验证。

See the dated [verification record](../design/skills-installation-verification-2026-10-16.md) for the actual sandbox/client observations and their limits. / 实际沙盒／客户端观察及其边界见注明日期的[验证记录](../design/skills-installation-verification-2026-10-16.md)。

## Workflow requirements | 工作流要求

The linked skill contracts are authoritative. Check the capabilities needed for the chosen task, rather than installing every possible dependency. / 以所链接的技能契约为准，按所选任务检查能力，不要求统一安装所有可能的依赖。

| Workflow / 工作流 | Capabilities and limits / 能力与边界 |
| --- | --- |
| [Learning guidance](../skills/prepare-toastmasters-speech/SKILL.md), outlines, feedback and portable prompts / 学习指导、提纲、反馈及便携提示词 | Capable text chat and member-supplied evidence; no universal Python prerequisite. Optional TM Companion links are not required accounts/services. Native calls require a skill-aware client. / 有相应能力的文字聊天及会员提供的证据，无统一 Python 要求。可选 TM Companion 链接不是必需服务或账号；原生调用须客户端支持技能。 |
| [Speech coaching team](../skills/toastmasters-speech-coaching-team/SKILL.md) / 演讲教练团队 | Five distinct role subagents; waves allowed, identities remain separate. Without subagents, stop; do not simulate the team. Audio/video feedback requires access to the actual media and suitable inspection tools. / 五个不同角色的独立子代理，可分批运行但身份不能合并。无子代理须停止，不可模拟团队。音视频反馈还须能读取并检查真实媒体。 |
| [Meeting agenda team](../skills/toastmasters-meeting-agenda-team/SKILL.md) / 议程团队 | Three independent agents, source-format editing, text/native-structure extraction, full rendering and visual inspection. Stop if three agents are unavailable. Preserve a non-PDF source type; PDF source produces DOCX; packaged DOCX fallback only when no source is supplied. / 三个独立代理、源格式编辑、文字及原生结构提取、完整渲染和视觉检查。无三个独立代理须停止。非 PDF 保留源格式，PDF 转 DOCX，仅无源文件时用内置 DOCX。 |
| [PPTX translation](../skills/powerpoint-translation-redesign/SKILL.md) / PPTX 翻译 | Separately installed external `presentations` skill plus compatible inspection/editing/rendering tools and three independent agents. Stop without required independence or when fidelity/verification cannot be met. Bundled audit uses Python stdlib ZIP/XML, **not `python-pptx`**; passing audit is only triage. / 须另装外部 `presentations` 技能，具备检查／编辑／渲染工具和三个独立代理。独立性或设计保真／验证不满足时须停止。内置审计仅用 Python 标准库 ZIP/XML，无须 `python-pptx`；审计通过只是初筛。 |
| [Raster poster translation](../skills/poster-image-translation-redesign/SKILL.md) / 栅格海报翻译 | Three independent agents, pixel-mask editing/comparison, actual-image inspection and QR decoding when present. Missing required capability or reviewer acceptance blocks final delivery. / 三个独立代理、像素蒙版编辑／比对、实际图片查看，以及有二维码时的解码。缺必需能力或评审未接受会阻止最终交付。 |
| [Poster maker](../skills/toastmasters-poster-maker/SKILL.md) and [reviewer](../skills/toastmasters-poster-reviewer/SKILL.md) / 海报制作与评审 | Image generation, layout/compositing, rendering, actual-image inspection, exact protected-asset overlays and QR decoding when present. Maker needs a separate reviewer agent/session; without independent review return only an explicitly unreviewed draft. No image inspection means BLOCKED image review, preliminary findings only. / 须图像生成、布局合成、渲染、实际图像查看、受保护素材的精确叠加及有二维码时的解码。制作须独立评审代理／会话；缺独立评审只能交明确标注的未经评审草稿。无法查看图片时，图像评审为 BLOCKED，仅提供初步发现。 |
| [Visual editing](../skills/edit-svg-canvas/SKILL.md) / 可视化编辑 | Suitable built-in canvas when available and chosen. Method Draw route needs complete package, Python 3.10+, loopback server/browser and verified cache or first-use network access; no Node runtime needed by the editor. Text-only chat can prepare a manual handoff, not launch it. / 可用且用户选择时用合适的内置画布。Method Draw 须完整技能包、Python 3.10+、本地服务／浏览器及已验证缓存或首次联网；编辑器无需 Node。纯文字聊天只能准备手动交接，不能启动编辑器。 |
| [PDF translation](../skills/translate-pdf/SKILL.md) / PDF 翻译 | Python/PyMuPDF, document/font inspection, rendering and every-page visual review. D85 provides companion guardrails, **not the upstream implementation**: separately acquire and inspect [upstream code](https://github.com/wshuyi/translate-pdf-skill) before using it. Use an independent reviewer when available; otherwise explicit self-review with the same content/visual checks and correction loop. Missing inspection is BLOCKED, not approval. / 须 Python/PyMuPDF、文档／字体检查、渲染及逐页视觉审核。D85 仅提供配套约束，并未内置上游代码；使用前须另行获取并检查[上游实现](https://github.com/wshuyi/translate-pdf-skill)。可用时用独立评审，否则明确标注自审，仍须同等内容／视觉检查及修正循环。无法检查是 BLOCKED，不是通过。 |

Native packages preserve instructions and bundled files; they do not automatically install Python libraries, renderers, browser tooling, image models, external skills or upstream PDF code. Choose tools compatible with the host and the skill contract. No blanket self-review fallback applies to the agenda, PPTX, raster-translation or speech-team hard stops.

原生技能包保留指令和内置文件，不会自动安装 Python 库、渲染器、浏览器工具、图像模型、外部技能或 PDF 上游代码。须按宿主能力和技能契约选择工具。议程、PPTX、栅格翻译及演讲团队的停止条件不能统一降级为自审。

## Selective installs and materials | 选择安装与素材

Install-all remains the default. For a selective install, read `requires`/`recommends` in the [portable catalog](../catalog/skills.json) and the native skill's own contract. Do not assume the external CLI resolves D85 catalog dependencies.

默认仍为全部安装。选择安装时，请阅读[便携目录](../catalog/skills.json)的 `requires`／`recommends` 和原生技能契约；不要假定外部 CLI 会自动解析 D85 的依赖关系。

- Poster maker needs `toastmasters-poster-reviewer`; add `edit-svg-canvas` if Method Draw is chosen or a suitable built-in canvas is unavailable. / 制作须配套 `toastmasters-poster-reviewer`；选择 Method Draw 或无合适内置画布时加装 `edit-svg-canvas`。
- PPTX translation needs the external `presentations` skill; also install `poster-image-translation-redesign` when embedded raster text needs translation. Finish its independent reviews before the PPTX team runs. / PPTX 翻译须外部 `presentations`；若内嵌栅格文字须翻译，还须 `poster-image-translation-redesign`，先完成其独立评审再运行 PPTX 团队。
- PDF's local shared glossary is in the raster-translation package; its bundled terminology note also links to the same online glossary. Either accessible copy is sufficient. The implementation remains external. / PDF 的本地共享术语表位于栅格翻译包；内置术语说明也链接同一在线表，任选可访问的一份即可。实现代码仍须另取。

The CLI preserves each selected skill folder's supporting files. Root-level `materials/`, `catalog/` and shared `references/` require the optional retained checkout. Private originals under `materials/toastmasters-brand/local/` are never in a fresh clone or CLI install. Reuse authorized originals or the [saved official URLs](../materials/toastmasters-brand/README.md), keeping source URL, filename and checksum provenance. Access does not establish permission, and the repository license does not grant rights to official assets.

CLI 保留所选技能目录内的配套文件；顶层 `materials/`、`catalog/` 和共享 `references/` 需另行保留仓库。`materials/toastmasters-brand/local/` 私有原件不会出现在新克隆或 CLI 安装中。复用有权使用的原件或[已保存的官方链接](../materials/toastmasters-brand/README.md)，保留来源 URL、文件名和校验值；技术上可获取不等于已获许可，仓库许可不授予官方素材权利。

## First-use record | 首次使用记录

Reload or start a new conversation only as the client requires. Ask explicitly for `build-speech-outline`: “My fictional topic is learning to cook; my message is that small experiments build confidence; audience: new club members; time: three minutes. Help me make an outline.” Provide project criteria if claiming a specific Pathways project; do not invent them.

按客户端要求重新加载或新建对话。明确调用 `build-speech-outline`：“虚构主题：学做饭；主旨：小实验建立信心；听众：新会员；时长三分钟。请帮我拟提纲。”若指定某个 Pathways 项目，须提供其真实标准，不能编造。

Record: date; client/version; installer/version/method; selected and installed IDs; project/global scope and active paths; source revision or unknown; retained checkout path or none; observed discovery/loading evidence or unverified; harmless task result; missing capabilities/companions; required reload; advanced workflows still untested. A client loading event or native skill listing is stronger evidence than the model saying it read the skill. For Codex, an explicit `$build-speech-outline` request can select the skill; confirm actual client evidence rather than relying on that syntax alone. See [Codex skill documentation](https://learn.chatgpt.com/docs/build-skills).

记录：日期、客户端／版本、安装器／版本／方式、所选和实际安装 ID、项目／全局范围及路径、来源版本或未知、仓库副本路径或未保留、发现／加载证据或未验证、首次任务结果、缺失能力／配套技能、是否须重载，以及仍未测试的进阶流程。客户端加载事件或原生技能清单比模型自称已读技能更可靠。Codex 可用 `$build-speech-outline` 显式选择技能，但仍须核实客户端证据；见 [Codex 技能文档](https://learn.chatgpt.com/docs/build-skills)。

## Maintenance and troubleshooting | 维护与排错

For **AI-assisted/manual installation**, ask the installing agent to update or remove only the named D85 IDs at the recorded active location and scope. Preserve other skills and user assets, inspect links before deleting targets, then reload if needed and repeat the loading/first-task checks. Pulling a retained checkout does not automatically refresh installed copies. A linked installation may follow its target; report that relationship before changing it.

**AI 协助／手动安装：** 请安装者仅在已记录的实际位置和范围内更新或移除指定 D85 ID。保留其他技能及用户素材，删除前确认链接与目标；按需重载并重做加载／首次任务检查。拉取资源仓库不自动更新已安装副本；链接安装可能随目标更新，修改前须说明关系。

For **Skills CLI 1.7.2**, run project commands from the intended project root. These examples target one installed D85 skill and Codex; replace the ID/client deliberately. For Claude Code use `--agent claude-code`; for Hermes use `--agent hermes-agent`. Node/npm and registry/source access are needed unless cached. Inventory is not activation evidence.

**Skills CLI 1.7.2：** 项目命令须在目标项目根目录运行。以下只针对一个已安装 D85 技能和 Codex；请明确替换 ID／客户端。Claude Code 用 `--agent claude-code`，Hermes 用 `--agent hermes-agent`。除缓存可用外，须 Node/npm 及注册表／来源网络访问。安装清单不等于激活证据。

```bash
# Project: list / 项目：查看
npx skills@1.7.2 list --agent codex --json
# Project: update only this ID / 项目：仅更新此 ID
npx skills@1.7.2 update --project build-speech-outline --yes
# Project: request removal for Codex / 项目：请求移除 Codex 对应安装
npx skills@1.7.2 remove build-speech-outline --agent codex --yes

# Global: list, update this ID, remove this ID / 全局：查看、更新此 ID、移除此 ID
npx skills@1.7.2 list --global --agent codex --json
npx skills@1.7.2 update --global build-speech-outline --yes
npx skills@1.7.2 remove build-speech-outline --global --agent codex --yes
```

`update` has no agent filter: review its targets when the same ID is installed for multiple clients. Omitting names can update unrelated tracked skills. Use it only for sources supported by the installer's tracking; a local-directory source may require repeating its scoped `add`. `skills check` shares the release's update handler; do not use it as a read-only diagnostic. After **every update/removal**, rerun the matching scoped `list`, inspect active files/link targets and check fresh-session client visibility. A successful exit alone does not prove an update or removal: shared canonical copies may remain available after agent-specific removal. If tracking cannot update a source, preview it and repeat the original scoped `add` with the intended IDs/client, then inspect the result. Keep installer inventory separate from client loading. See the [released CLI package documentation](https://www.npmjs.com/package/skills/v/1.7.2).

`update` 无客户端过滤参数：同一 ID 装于多个客户端时，须确认其目标。不指定名称可能更新其他已跟踪技能；仅用于安装器跟踪支持的来源，本地目录来源可能须按原范围重跑 `add`。此版本 `skills check` 共用更新处理器，不可作为只读诊断。**每次更新／移除后**须重跑相应范围的 `list`，检查实际文件／链接目标，并在新对话确认客户端可见性。成功退出不证明已更新或移除：按客户端移除后，共用的规范副本可能仍可访问。跟踪无法更新时，先预览来源，再按原范围、指定 ID／客户端重跑 `add` 并检查结果。安装器清单与客户端加载仍须分开；见 [CLI 发布包文档](https://www.npmjs.com/package/skills/v/1.7.2)。

If you intentionally want to remove one named skill from **all clients in the current project**, omit the agent filter: `npx skills@1.7.2 remove toastmasters-poster-maker --yes`. This broadens the client scope, so use it only for that intent and repeat the postchecks. Do not use `--agent '*'`: the tested release rejects it. To remove across all global clients, the analogous scope is `--global`; that global removal route is documented, not sandbox-verified here.

若明确要从**当前项目的所有客户端**移除同一个指定技能，可省略客户端过滤：`npx skills@1.7.2 remove toastmasters-poster-maker --yes`。这会扩大客户端范围，只能在意图相符时使用，并须重做后验检查。不要使用 `--agent '*'`，受测发布版会拒绝该值。跨所有全局客户端移除时，相应范围参数为 `--global`；此全局移除路线仅有文档说明，本次未在沙盒验证。

If the **client cannot discover/load** a package, compare the chosen client and scope with the reported active path; check complete folder/frontmatter, permissions and link targets, then follow that client's reload guidance. If it **loads but cannot complete a task**, identify the missing tool, companion or review role in the requirements table and exact skill contract. Report blocked/unverified checks; use only that skill's permitted draft or handoff mode. Do not “fix” loading by installing every runtime dependency or claim a failed workflow passed.

**客户端找不到／加载不了：** 对照目标客户端和范围检查实际路径、目录完整性、frontmatter、权限及链接目标，再按客户端说明重载。**已加载但任务无法完成：** 按能力表和准确技能契约定位缺少的工具、配套技能或评审角色，明确报告受阻／未验证检查，仅使用该技能允许的草稿或交接模式。不要靠安装所有运行依赖来“修复”加载，也不能将失败流程标为通过。

## Maintainer checks | 维护检查

From the repository root, Python 3.10+ and Git are sufficient for collection static checks; no workflow libraries are needed. The package inventory comes from tracked `skills/*/SKILL.md`, including every distributed package while ignoring untracked local artifacts. Every tracked file inside each package must exist; canonical identity/frontmatter, local Markdown file targets, catalog companions and the native PPTX conditional companion are checked. External tools/skills and remote links are not probed. This is deliberately a small package check, not a dependency installer or runtime diagnostic.

在仓库根目录运行集合静态检查只须 Python 3.10+ 和 Git，无须工作流库。清单来自 Git 跟踪的 `skills/*/SKILL.md`，覆盖全部分发包并忽略本地未跟踪文件。检查各包内所有跟踪文件是否存在、规范身份／frontmatter、本地 Markdown 文件链接、便携目录配套关系和原生 PPTX 的条件配套包。不探测外部工具／技能或远程链接；这是小型包检查器，不是依赖安装器或运行诊断。

```bash
python3 scripts/validate_skill_packages.py
python3 scripts/validate_portable_skills.py
python3 scripts/sync_poster_references.py --check
python3 -m unittest discover -s tests
git diff --check
```

The portable validator remains separate: the reviewed baseline `1af81e05` had 18 catalog entries with a different scope from its 23 tracked packages, and at the revision that adds this guide there are 19 catalog entries and 24 tracked packages. The same five officer/translation packages remain outside that catalog and remain installable; this difference does not mean the installer lost them or that prompts must be generated for them. Observed counts and command output for this revision are in the [re-check record](../design/skills-installation-recheck-2026-10-16.md).

便携检查器保持独立：受审基线 `1af81e05` 有 18 个便携条目，与当时 23 个跟踪包的范围不同；加入本指南的版本为 19 个便携条目与 24 个跟踪包。目录外仍是同样的五个干部／翻译包，仍可安装；数量差异不代表安装器漏装，也不要求为其生成新便携提示词。本版本的计数与命令输出见[复查记录](../design/skills-installation-recheck-2026-10-16.md)。

For a clean export without `.git`, first capture a source manifest using `git ls-files > /tmp/d85-tracked-files.txt`, export the same tracked revision, then run the current checker against the export:

无 `.git` 的干净导出可先在源仓库用 `git ls-files > /tmp/d85-tracked-files.txt` 保存清单，导出同一跟踪版本，再用当前检查器检查导出目录：

```bash
python3 scripts/validate_skill_packages.py --root /absolute/path/to/export --tracked-files /tmp/d85-tracked-files.txt
```

The manifest is an explicit input from the source checkout; a filesystem scan cannot recover an omitted tracked file. Review source changes and validation failures before release. Neither a static pass nor `--help` success can establish advanced-workflow readiness.

清单须明确来自源仓库；扫描导出文件系统无法知道哪些跟踪文件被漏掉。发布前须检查源改动及验证失败。静态通过或 `--help` 成功均不能证明进阶工作流就绪。
