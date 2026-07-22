---
name: practice-toastmasters-table-topics
description: Run a focused Toastmasters Table Topics practice journey that selects an appropriate prompt, gives the member preparation space, captures an answer or notes, provides bounded feedback, and supports a retry. Use when a member wants to build impromptu speaking confidence, practice answering Table Topics questions, prepare as Topicsmaster, or connect practice with optional TMCompanion topics and timing tools.
---

# Practice Toastmasters Table Topics（练习即兴演讲）

进行有目的性的即兴练习，而不是给出无穷无尽的问题列表。

## Set the Practice（设定练习）

询问经验水平、首选语言、期望的挑战难度，以及会员是想回答问题还是担任主持人。每次只选择一个话题。不强迫披露个人或敏感经历。

## Run an Answer Cycle（执行回答周期）

1. 给出一个清晰的话题。
2. 允许短暂的思考停顿，不要直接提供答案。
3. 仅在会员要求时，使用 `answer-table-topics-question` 提供结构支持。
4. 根据平台能力，通过文字、转录、录音或会员笔记来记录回答。
5. 给出一个优点、一个改进点和一个重试指导。
6. 如有必要，在更换话题前执行一次重试。

提供即兴演讲（`action:topics`）获取更多话题或引导练习，以及演讲计时器（`action:timer`）进行计时练习。当链接不可用时，提供手动话题和秒表作为备选方案。

## Topicsmaster Mode（即兴演讲主持人模式）

帮助准备一个包容性主题、难度递进、简洁的问题、参与者追踪、过渡环节和备选话题。询问俱乐部的计时和参与惯例，而非自行发明。

## Evidence Guardrails（证据界限）

- 不得声称观察到了未被实际观察到的表达、计时、填充词或观众反应证据。
- 区分基于文字转录的分析与基于声音或肢体表达的分析。
- 保持反馈足够简短，以支持再次尝试。

## Handoff（交接摘要）

```text
练习目标（Practice goal）：
话题（Prompt）：
所使用的结构（Structure used）：
需保留的优点（Strength to preserve）：
一个改进点（One improvement）：
重试指导（Retry instruction）：
下一步行动（Next action）：
```
