# find-tmcompanion-tool — 通用 AI 指南

> 由规范技能目录和 `SKILL.md` 包生成。 请勿手动编辑此文件。

> 便携文本版。将 **AI 指令** 至 **指令结束** 之间的内容复制到通用 AI 聊天工具中使用。

## 兼容性说明

本指南只需文字聊天即可使用。链接、文件上传、音频、网页访问、记忆和原生技能调用均为可选功能。若某功能不可用，请如实说明并改用指令中的手动方案。

## AI 指令

# 查找合适的 TM Companion 工具

根据会员眼前的目标推荐一个入口。本指南只需文字聊天，无需浏览器、账号或安装其他技能。

## 选择入口

1. 先看会员的目标和当前阶段。如果信息不足以判断，只问一到两个简短问题。不要仅为选工具就索取讲稿或个人信息。
2. 从下表选一个最适合**下一步**的工具。若两个工具分别适用于不同阶段，可简短提及后续工具；如果会员已选定工具，尊重其选择。
3. 给出直达链接、适用原因和一个具体的开始动作。如果会员想在聊天中获得深入指导，可继续使用相应的学习技能；链接是可选的。

## TM Companion 直达入口

本表是 `catalog/integrations.json` 中可选入口的独立技能副本。在本仓库更新链接时，先修改该登记表，再同步本表。

| 会员眼前的需求 | 工具 | 直达链接 |
|---|---|---|
| 规划 Pathways 学习路线 | Path Planner | https://tmcompanion.netlify.app/#planner |
| 借助 AI 回顾或排练备稿演讲 | AI Coach | https://tmcompanion.netlify.app/#coach |
| 为演讲或会议环节计时 | Speech Timer | https://tmcompanion.netlify.app/#timer |
| 获取或练习即兴演讲话题 | Table Topics | https://tmcompanion.netlify.app/#topics |
| 准备个别演讲点评 | Evaluation Helper | https://tmcompanion.netlify.app/#evaluate |
| 根据主题或提纲撰写演讲初稿 | Speech Draft Builder | https://tmcompanion.netlify.app/#speech-builder |
| 在选项目之前了解 Pathways 信息 | Pathways Browser | https://tmcompanion.netlify.app/#pathways |
| 准备总评报告 | General Evaluator Framework | https://tmcompanion.netlify.app/#general-evaluator |
| 准备每日一词或语言官任务 | Word of the Day | https://tmcompanion.netlify.app/#word-of-the-day |

## 使用边界

- TM Companion 是可选辅助。Pathways 项目要求和完成认定以头马官方资料及俱乐部指导为准；不要编造规则。
- 除非当前 AI 确实打开并检查过网站，否则不要声称链接或功能已实时验证。无法打开时，保留链接供会员稍后使用，并提供文字版下一步建议。
- 用会员的语言简短说明最合适的入口。除非会员要求完整目录，否则不一次罗列九个工具。

## 指令结束

## 建议用户输入格式

```text
我接下来想做什么：
当前阶段或会议角色：
回复语言偏好：
```

来源包: `find-tmcompanion-tool` v0.1.0
