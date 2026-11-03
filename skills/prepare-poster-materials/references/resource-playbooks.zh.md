# 资源操作指引

核实快照：2026-10-28/29 本轮会话。来源仅静态阅读，未执行。这是原创接入说明，不重新分发上游包。代码或指令许可不自动覆盖字体、素材、模型权重和在线服务使用。使用前核对已安装版本。所有资源均可选；结合能力路线 (`visual-recipes.zh.md`)及证据状态使用。

## 构图

**需要／输入：** 静态视觉方向或更好的海报构图；目的、优先级、尺寸、固定文案、受保护素材、可编辑要求。

**发现／使用：** 查找已装 `canvas-design`，阅读当前指令和资源，再通过平台入口加载并传入简报。它偏艺术表现，会员必要内容仍优先。要求实际渲染概念稿，不只形容词。缺失时可用已有 SVG 或版式渲染器，用相同文案制作两个注明用途的构图研究；不声称用了缺失技能。无渲染器时交付构图规格，注明预览不可用。

**输出／设置／检查：** 上游声明 Markdown 设计说明及 PNG/PDF 艺术图，不保证可编辑文字与图层。可编辑交付需另用合适编辑器、源文件并验证。安装可选；先检查渲染库、字体和文件输出。查看实际概念稿中的必要信息、阅读顺序、间距及目标尺寸可读性。失败时保留简报和概念稿用于手动交接。

来源：[canvas-design 指令](https://github.com/anthropics/skills/blob/main/skills/canvas-design/SKILL.md)、[目录 Apache-2.0 许可](https://github.com/anthropics/skills/blob/main/skills/canvas-design/LICENSE.txt)。此处未审核或复制字体。

## Baoyu

按任务挑选单个已装技能，不安装整套。[仓库许可 MIT](https://github.com/JimLiu/baoyu-skills/blob/main/LICENSE)。

| 能力 | 需要及输入 | 调用、输出与检查 |
|---|---|---|
| [baoyu-cover-image](https://github.com/JimLiu/baoyu-skills/blob/main/skills/baoyu-cover-image/SKILL.md) | 封面或背景；主体、画幅、配色、渲染、情绪、文字策略、参考图。 | 阅读已装接口，通过加载入口传入选择 → 封面图及保存的提示词。封面假设不等于通用活动版式。检查裁切、参考和文字；要精确可编辑文案时选择无标题素材。 |
| [baoyu-infographic](https://github.com/JimLiu/baoyu-skills/blob/main/skills/baoyu-infographic/SKILL.md) | 议程、比较、流程或密集摘要；确认的结构化内容和优先级。 | 让已装技能选择布局、风格，并使用支持的后端渲染 → 信息图。检查每项事实、字形；不作为所有海报的装饰默认。 |
| [baoyu-image-gen](https://github.com/JimLiu/baoyu-skills/blob/main/skills/baoyu-image-gen/SKILL.md) | 原生工具不适合时的位图生成或参考素材；提示词、参考图、画幅、路径、选定后端。 | 加载已装技能，检查实际支持参数 → 位图文件，不是可编辑版式。选择 CLI 路线时，先阅读当前用法及相关可执行代码。 |

**设置／降级：** 前端技能可使用原生图像后端，不一律需要 API Key。可选后端声明 Bun/npx、偏好及服务商设置要求；API 路线需要已授权凭据和额度，Codex CLI 路线使用已有登录。核对参考图支持及真实账号访问。发现资源不授权执行 npx、写偏好、下载或安装。选择设置前解释收益，见按需设置 (`platform-setup.zh.md`)。

检查返回图片，不只看作业成功。生成文字错误可能需要重生成或另做可编辑版式；不声称覆盖修改会更新原始源文件。不进行失控的付费重试。无可用后端时，提供工具可用提示词或商定替代版式产物；准备提示词不等于生图。[后端指引](https://github.com/JimLiu/baoyu-skills/blob/main/docs/image-generation.md)。平台特定调用示例需适配，不能原样套用。

## SVG

**需要／输入：** 编辑文字、形状或移动素材；最新 SVG、精确修改和保留约束。轮廓文字与嵌入位图各有边界。

**发现／使用：** 加载可用的 `edit-svg-canvas`。明确的助手文字修改可直接保存为新源文件版本。会员手动编辑遵循该包已有的画布选择与运行说明，尊重已经做出的选择。复用其 Method Draw 启动、状态及保存处理，不造新编辑器，不运行上游构建或安装步骤。

**输出／设置／检查：** SVG 新版本及可选渲染导出。现有集成需要 Python 3.10+、本地回环及浏览器服务权限、已验证缓存或首次网络。缺环境是配置缺口；纯文字只能手动指导。交互时保留 `editor_url` 和 `session_json`，说明 Save and finish，核实完成状态和哈希，按返回的保存源文件继续。检查导入导出字体、位置及位图素材。失败时提供文件供现有编辑器打开，说明没有可用链接；不承诺 PNG 自动分层。

来源：[Method Draw，MIT](https://github.com/methodofaction/Method-Draw)。以本地集成的当前说明为操作依据。

## 抠图

**需要／输入／输出：** 原照片及明确前景 → 透明 PNG。身份关键素材优先提取；生成式重建可能改变人物，必须说明。

**发现／使用：** 先检查真正的分割、去背景工具或已有编辑器。检查 rembg 可用性时，用清单、`command -v rembg` 或包元数据，不导入候选代码。首次执行前读已装帮助和相关源码。CLI 已审查、模型条款及缓存合适且已明确选择时，命令形式为 `rembg i -m MODEL input.png cutout.png`（需替换 MODEL）。不悄悄使用变化的默认模型，也不为探测可用性而触发模型下载。

**设置：** README 写 Python 3.11–3.13，pyproject 声明 ^3.11；需验证具体发行版与 ONNX 组合。可选 CPU，GPU 另有运行库及硬件约束。首次推理可能下载权重。MIT 代码不代表所有模型都同许可；文档中的 BRIA 默认模型有商业使用限制。提出设置前检查所选权重来源与条款、缓存、下载体积和网络、硬件。本指引不授权下载或安装。

**检查／降级：** 在浅深背景查看实际 alpha 和主体、发丝眼镜衣物边缘、孔洞、裁切及分辨率。PNG 后缀不证明透明。所有工具缺失且不想安装时，给手动抠图步骤 (`platform-setup.zh.md#manual-cutout`)，不虚构 PNG。无须 Canva MCP。

来源：[README 及模型](https://github.com/danielgatis/rembg)、[环境声明](https://github.com/danielgatis/rembg/blob/main/pyproject.toml)、[MIT 许可](https://github.com/danielgatis/rembg/blob/main/LICENSE.txt)、[用法](https://github.com/danielgatis/rembg/blob/main/USAGE.md)。

## 局部重绘选择

[IOPaint](https://github.com/Sanster/IOPaint) 仍显示于 2025-08-13 归档。[Apache-2.0](https://github.com/Sanster/IOPaint/blob/main/LICENSE) 不能解决维护或模型要求。排除其作为新手新装默认；不假设存在受维护分支。已有安装需评估适用性，不自动移除。

先检查已有平台或编辑器的蒙版支持。原图、蒙版或选区、修改及保留简报 → 修改图片。检查周围像素、脸部和受保护内容，不只检查选区。无工具时提供已有编辑器中的手动修图路线。

进阶候选：[ComfyUI](https://github.com/Comfy-Org/ComfyUI) 在本轮[元数据](https://api.github.com/repos/Comfy-Org/ComfyUI)核实中未归档且近期有推送；[README](https://github.com/Comfy-Org/ComfyUI#readme)描述局部重绘。核心 [GPL-3.0](https://github.com/Comfy-Org/ComfyUI/blob/master/LICENSE)、节点与权重需分别审查。仅考虑已有且已审查的工作流，或会员主动选择的进阶设置。检查工作流输入、模型及硬件兼容、本地还是 API 执行；传入原图、蒙版和提示词，检查返回图片的漂移。此处未安装或运行，不是已验证的 D85 替代方案。不可用时保留编辑简报和蒙版用于手动交接。不为一次小改把新手带入节点或模型安装。

[BRIA 模型卡与独立模型许可](https://huggingface.co/briaai/RMBG-2.0)。
