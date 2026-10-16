# Contributing to D85 AI Resources | 贡献 D85 AI 技能

You can contribute a useful prompt or local skill without knowing coding or Git. Start with its purpose, intended users, source files or text, and one realistic example. Chinese or English drafts are welcome; the assistant helps with packaging and translation.

无需懂编程或 Git，也能贡献有用的提示词或本地技能。先提供用途、适用对象、来源文件或文字，以及一个真实使用场景。可以先交中文或英文草稿；AI 助手协助整理格式与翻译。

## Start | 开始

Use [D85 Skill Contributor](skills/d85-skill-contributor/SKILL.md) or its [中文版本](skills/d85-skill-contributor/SKILL.zh.md). For text-only assistants, copy the reusable instructions from the generated [English prompt](prompts/d85-skill-contributor.en.md) or [中文提示词](prompts/d85-skill-contributor.zh.md).

Example request / 请求示例：

> Help me contribute this meeting-agenda prompt to D85. I do not know GitHub. Guide me through preparation and testing, then help me submit a PR if this platform supports it.
>
> 我想把这个会议议程提示词贡献给 D85，但我不懂 GitHub。请带我整理并测试；如果当前平台支持，再帮我提交 PR。

Read the canonical [contribution rules](skills/d85-skill-contributor/references/contribution-rules.en.md) / [贡献规则](skills/d85-skill-contributor/references/contribution-rules.zh.md). These files are bundled with the skill and generated prompts; update them there rather than maintaining a second policy copy here.

## What happens next | 后续流程

Prepare and test → Submit a GitHub PR → D85 team reviews and may request changes → Team approves and merges if accepted → Team considers website integration and verifies publication.

整理与测试 → 提交 GitHub PR → D85 团队审核，可能要求修改 → 接受后由团队批准并合并 → 团队决定网站收录并验证发布。

**Submission is only the first step toward acceptance.** The contributor skill ends with a verified PR link and an explanation to wait for team review. It does not approve, merge, manage review follow-ups, or publish a website page. Neither acceptance nor publication is guaranteed.

**投稿只是进入接纳流程的第一步。** 贡献者技能以提供已验证的 PR 链接并说明等待团队审核为终点，不负责批准、合并、后续审核管理或网站发布，也不保证收录或上线。

With file/Git/GitHub tools and the contributor's authenticated account, an assistant can prepare a fork-based PR. Without those capabilities, it can prepare copyable submission material and manual next steps. A prepared handoff is not a submitted PR. No maintainer password or token in chat is needed.

具备文件、Git、GitHub 工具且已登录贡献者账号时，助手可以通过个人 fork 提交 PR。缺少这些能力时，助手可整理可复制的投稿材料与手动步骤；材料准备好不等于已投稿。无需提供维护者密码，也不要把令牌发到聊天中。

## Before requesting review | 请求审核前

Walk through one realistic task and one missing-input or missing-capability case, guided one at a time. Include expected and observed results in the PR template. The assistant checks applicable package structure and the exact public file list. If behavioral or tooling checks are blocked or failing, a clearly labeled draft PR can request help; private material and unresolved sharing rights must be resolved before any upload. See the canonical rules for the full evidence and safety requirements.

在 AI 逐项引导下，完成一个正常使用场景和一个缺少输入或能力的场景，将预期与实际结果填写到 PR 模板中。助手检查适用的包结构和将公开的准确文件清单。若行为测试或工具检查受阻、失败，可以明确标注为草稿 PR 求助；隐私材料和未解决的分享权限问题必须在任何上传前处理。完整证据与安全要求以贡献规则为准。

## Repository tooling | 仓库工具

Contributors do not need to run terminal commands themselves. A capable assistant uses reviewed repository tooling against a scoped candidate checkout, after static inspection. It does not execute incoming skill scripts during intake.

贡献者不必自己运行终端命令。具备能力的助手在静态检查后，在限定范围的候选副本中使用已审核的仓库工具；接收材料时不执行投稿技能自带的脚本。

The collection-wide package check reads the Git-tracked package list, or an explicit `git ls-files` manifest for a clean export; the portable-catalog check covers only the catalog subset, so run both. See the [installation guide](docs/installation.md#maintainer-checks--维护检查) for the observed output and the clean-export route.

前者覆盖 Git 跟踪的全部技能包（干净导出须另给 `git ls-files` 清单），后者只覆盖便携目录子集，两者都要运行。实际输出与干净导出方式见[安装指南](docs/installation.md#maintainer-checks--维护检查)。

```sh
python3 scripts/build_portable_prompts.py
python3 scripts/validate_skill_packages.py
python3 scripts/validate_portable_skills.py
python3 scripts/sync_poster_references.py --check
git diff --check
```

Maintainers run relevant controlled tests, including `python3 -m unittest discover -s tests`, after reviewing executable changes. Structural checks alone do not demonstrate that a skill works.

维护者先审核可执行变更，再运行适当的受控测试，包括 `python3 -m unittest discover -s tests`。结构检查通过不能单独证明技能有效。

## Licensing clarification | 许可说明

The README currently declares MIT, but this checkout has no tracked full repository license file. Maintainers need to clarify that text and attribution terms; this guide does not create a CLA or new license terms. Share only original or authorized material, disclose sources and existing licenses, and preserve third-party notices. If rights for submitted material are uncertain, resolve them with the team before uploading that material.

README 当前声明 MIT，但本仓库尚未跟踪完整的仓库许可证文件，需由维护者明确许可文本与署名约定；本指南不建立 CLA 或新许可条款。只分享原创或已获授权的材料，说明来源与既有许可，并保留第三方声明。投稿材料的权利若不明确，应先与团队确认，再上传相关材料。
