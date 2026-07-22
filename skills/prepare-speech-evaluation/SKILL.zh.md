---
name: prepare-speech-evaluation
description: Turn supported observations, notes, a transcript, recording, speaker purpose, and supplied project criteria into a kind specific Toastmasters speech evaluation. Use when a member is preparing to serve as Speech Evaluator, organizing evaluation notes, practicing an oral evaluation, or checking that feedback is evidence-based and actionable.
---

# Prepare Speech Evaluation（准备演讲点评）

## Establish the Evaluation Context（建立点评背景）

询问演讲者的目的、提供的项目标准、目标时长、点评人的笔记以及可用的证据。在演讲前，帮助制定一个紧扣演讲目的的简短观察计划，而不是使用通用清单。

## Build the Evaluation（构建点评内容）

1. 找出两个有具体证据支持的优点。
2. 选择一到两个学习价值高的改进点。
3. 针对每个改进点，陈述观察结果、可能的影响以及可行的下一步。
4. 仅在存在证据的情况下，检查开场、组织、支撑、结论和表达方面。
5. 准备一个鼓励性的结尾，保留演讲者的主动权。

提供点评助手（`action:evaluate`）作为可选支持。

## Evidence Rules（证据规则）

- 不得虚构引用语、手势、时间、填充词、观众反应或项目要求。
- 将仅基于文字转录的分析标注为内容和语言证据，而非完整的表达证据。
- 区分观察到的事实、点评人的解读以及建议。
- 不得将 AI 观点呈现为头马官方判断。

## Output（输出格式）

```text
演讲者目的与标准（Speaker purpose and criteria）：
所用证据及其局限性（Evidence used and limitations）：
优点 1 —— 证据与影响（Strength 1 — evidence and impact）：
优点 2 —— 证据与影响（Strength 2 — evidence and impact）：
优先改进项 —— 证据、影响、下一步（Priority improvement — evidence, impact, next step）：
可选的第二个改进点（Optional second improvement）：
鼓励性结尾（Encouraging close）：
```
