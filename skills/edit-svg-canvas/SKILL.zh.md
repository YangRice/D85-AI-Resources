---
name: edit-svg-canvas
description: 当用户想亲自编辑设计、修改海报文字、移动照片或标志、手动调整现有布局，且可找到可编辑 SVG 源文件时使用。用户无需知道 SVG、Method Draw 或技能名称。
---

# 手动编辑设计

用本地 Method Draw 打开当前设计，让用户修改文字、拖动素材，然后点击
**Save and finish / 儲存並完成**，将新的 SVG 修订直接保存到任务输出文件夹。
此技能独立于头马品牌、Codex 面板或具体文档任务。

## 识别自然语言意图

“我要自己改文字”“我想手動編輯”“让我调整位置”“让我自己改海报”“move the
photo”“let me edit this myself”都足够。先找当前任务的可编辑源文件，不要求用户
知道格式或编辑器名称；仅在存在多个候选设计时问是哪一张。如果用户只是要求
“把标题改成 X”，直接完成修改；用户希望亲自操作时才开启编辑会话。

只有 PNG/JPEG 时，说明需要先重建独立文字及素材。把整张图片放进 SVG 不会使
图片里的文字变成可编辑文本。

## 启动与交接

脚本路径相对于本技能的安装目录解析，不依赖任务工作目录。缓存、字体、会话
生命周期与恢复方式见[运行说明](references/runtime.zh.md)。

```sh
python3 /absolute/path/to/edit-svg-canvas/scripts/edit_svg.py launch /absolute/path/to/design.svg --output-dir /absolute/path/to/task/output --open
```

使用宿主支持的持久进程／后台会话方式运行，用户编辑时保持服务存活。用浏览器
打开输出中的 `editor_url`，在对话中保留 `session_json` 路径。Codex 可用浏览器
面板，WorkBuddy 等宿主可用普通浏览器。告诉用户：“可以改文字、拖动素材；完成后
点击 Save and finish，再回到这里说『继续』。”

用户返回后运行：

```sh
python3 /absolute/path/to/edit-svg-canvas/scripts/edit_svg.py status /absolute/path/to/session.json
```

只有 `state: complete` 且哈希校验成功才算完成。用 `saved_path` 作为新源文件；
不要运行会覆盖用户修改的旧构建脚本。`editing` 表示尚未保存完成。交接或取消后
仅停止本会话服务。

保存只交回 SVG；调用任务决定是否导出 PNG/PDF 或继续其他流程。海报任务须从
该文件重新渲染，并重复视觉、受保护素材、二维码及独立评审检查。保存不会自动
给代理发消息、调用图像模型或发布作品。

## 能力与限制

需要 Python 3.10+、本地端口权限，首次使用需要联网或已验证的缓存／归档。
保留原文件，另存修订。明确拒绝不支持的活动内容和外部资源，不静默删除。
位图背景仍是位图，转曲文字不能按文字编辑。检查导入及保存后的实际渲染与字体。
宿主无法启动服务时，说明缺失能力并提供手动交接。纯文字便携提示词不包含可执行
技能包。未在 WorkBuddy 内实测，不得称已验证其自动发现或编辑流程。
