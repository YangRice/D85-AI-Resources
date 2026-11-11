---
name: serve-toastmasters-club-officer
description: Help Toastmasters club officers plan a term, carry out responsibilities and hand over, covering President, VPE, VPM, VPPR, Secretary, Treasurer and SAA with current-rule verification.
---

# 俱乐部官员聚合技能

本入口按职责调用原子技能，协调共同工作，不一次倾倒七份岗位说明。

中文交付中，首次出现及标题、表头、行动卡中的角色标签必须使用中文规范名称，可在其后保留英文或缩写，不得只用英文或缩写：接待官（SAA）、教育副主席（VPE）、秘书长（Secretary）；涉及会议计时角色时用时间官（Timer），不用计时员。计时、实测用时等动作与证据描述仍按其本义表达，不改成角色名。

## 选择职责
沿用用户当前职位、任期阶段和实际问题，识别 Precident／Secretary／Sacretory 等拼写。只问会改变下一步的信息。SAA 按任务范围而非职位名称或紧急程度路由：某一场明确会议的执行交当次会务原子，即使用户正是任期接待官；可重复使用的标准与任期持续运营留在官员 SAA。

| 职位 | 原子技能 |
|---|---|
| President / 主席 | `serve-club-president` |
| VPE / 教育副主席 | `serve-club-vpe` |
| VPM / 会员副主席 | `serve-club-vpm` |
| VPPR / 公关副主席 | `serve-club-vppr` |
| Secretary / 秘书长 | `serve-club-secretary` |
| Treasurer / 财务官 | `serve-club-treasurer` |
| 接待官（SAA）：可重复运营与任期持续工作 | `serve-club-saa` |
| 接待官（SAA）：某一场明确会议的执行 | `prepare-saa-meeting-role` |

原生环境加载所选原子及相关参考；纯文字版使用对应内置能力。跨职位工作先确定一个主责和明确依赖，再分别准备必要角色行动，不把任务交回用户已经承担的职位。两种 SAA 范围都需要时，官员 SAA 定义可重复标准，当次 SAA 执行本场实例；不能仅因用户担任任期官员就撤回已限定范围的交接。若当次会务原子缺失，应说明限制，只依据已确认事实给最低限度行动卡，把未知的出入、权限、出口和应急细节留给负责真人确认。

## 协调任期
选择入职、日常执行、困难决策或交接，具体职位指导交给原子。共同计划保持简短：行动／负责人／已确认或建议日期／完成证据／依赖或审批。新官员先做第一周，不擅自铺全年。分清提议、决定、提交与批准。

规则、日期、会费、DCP、法定人数、权限需查现行正式来源；AI 计划不等于批准。本会选择明确标注。财务、会员、教育和对外沟通决策仍由真人负责。只用必要匿名数据，不收秘密、导入名单、擅自发送或改记录。

前任主席是传承建议角色，不是第八个选举职位或自动否决者；委员会职责需核实。按用户需要给中文／双语／离线输出，不自行假设。以有负责人的下一步和一个未决事项结束。

用户缩小职责或停用某项任务后，后续交接只保留当前范围。旧任务可明确标为已移出范围，但不得重新列为待办，除非用户恢复它。
