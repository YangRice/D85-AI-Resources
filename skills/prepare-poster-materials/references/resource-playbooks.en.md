# Resource playbooks

Snapshot: 2026-10-28/29 session. Sources were inspected statically, not executed. These are original integration notes, not redistributed packages. Licenses do not automatically cover fonts, assets, model weights or hosted usage. Recheck the installed revision. All resources are optional; use routing (`visual-recipes.en.md`) and its evidence states.

## Composition

**Need/input:** static art direction or a stronger poster composition; purpose, priority, dimensions, fixed copy, protected assets and editability.

**Discover/use:** find installed `canvas-design`, read its current instructions/resources and load it via the host interface with that brief. Keep the user's required content authoritative despite its art-first orientation. Request a rendered concept, not adjectives. If absent, an existing SVG/layout renderer can make two labeled layout studies using identical copy; do not claim the missing skill was used. If no renderer exists, deliver a composition specification and label the preview unavailable.

**Output/setup/check:** upstream declares Markdown rationale and PNG/PDF artwork; this does not establish editable text/layers. Editable delivery requires a separate suitable editor/source and verification. Installation is optional; first check rendering libraries, fonts and file output. Inspect the actual concept for required information, reading order, spacing and target-size legibility. On failure, retain brief/concept for manual handoff.

Sources: [canvas-design instructions](https://github.com/anthropics/skills/blob/main/skills/canvas-design/SKILL.md), [Apache-2.0 folder license](https://github.com/anthropics/skills/blob/main/skills/canvas-design/LICENSE.txt). No fonts audited/copied here.

## Baoyu

Select individual installed skills; do not install the collection. [Repository license: MIT](https://github.com/JimLiu/baoyu-skills/blob/main/LICENSE).

| Capability | Need and input | Invocation/output/check |
|---|---|---|
| [baoyu-cover-image](https://github.com/JimLiu/baoyu-skills/blob/main/skills/baoyu-cover-image/SKILL.md) | Cover/background; subject, aspect, palette, rendering, mood, text policy, references. | Read installed interface; dispatch those choices through the loader → cover image and saved prompt. Its cover assumptions are not a universal event layout. Check crop, reference fidelity and lettering; choose a no-title asset when editable exact copy is needed. |
| [baoyu-infographic](https://github.com/JimLiu/baoyu-skills/blob/main/skills/baoyu-infographic/SKILL.md) | Agenda, comparison, process or dense summary; approved structured content and priorities. | Ask installed skill to choose layout and style, then render using a supported backend → infographic. Check every fact and glyph; not a decorative default for all posters. |
| [baoyu-image-gen](https://github.com/JimLiu/baoyu-skills/blob/main/skills/baoyu-image-gen/SKILL.md) | Raster generation/reference assets when native tools are unsuitable; prompt, references, aspect, path, selected backend. | Load installed skill and inspect supported parameters → raster file, not editable composition. A selected CLI route needs current usage and relevant executable review before running. |

**Setup/fallback:** front-end skills can use native image backends; API keys are not universal prerequisites. The optional backend declares Bun/npx and preferences/provider requirements; API routes need authorized credentials/credits, while its Codex CLI route uses existing login. Check actual reference support and account access. Discovery does not authorize npx, preference writes, downloads or installs. Explain benefit before a setup choice. Follow platform setup (`platform-setup.en.md`).

Inspect returned images, not just successful job status. Bad generated lettering may require regeneration or a separately editable layout; do not claim an overlay changes the original source. Stop uncontrolled paid retries. If no backend is usable, supply a tool-ready prompt or agree an alternative layout artifact; prompt preparation is not image generation. [Backend guidance](https://github.com/JimLiu/baoyu-skills/blob/main/docs/image-generation.md). Host-specific invocation examples require adaptation, not literal copying.

## SVG

**Need/input:** editable text/shapes or moving supplied assets; latest SVG, exact edit and preserved constraints. Outlined text and embedded bitmaps have different limits.

**Discover/use:** load available `edit-svg-canvas`. Exact agent text edits can directly save a new source revision. User visual editing follows that package's existing canvas choice/runtime instructions, honoring a choice already made. Reuse its Method Draw launch/status/save handling; do not build another editor or run upstream build/install instructions.

**Output/setup/check:** SVG revision and optional rendered export. Existing integration needs Python 3.10+, loopback/browser/server access and verified cache or first-use network. Missing runtime is a setup gap; text-only use is manual guidance. Interactive use retains `editor_url`/`session_json`, explains Save and finish, checks complete state/hash, and resumes from saved source. Check import/export fonts, positions and raster assets. On failure, provide files for an existing editor and disclose no working link; do not promise PNG-to-layer conversion.

Source: [Method Draw, MIT](https://github.com/methodofaction/Method-Draw). The current local integration governs operation.

## Cutouts

**Need/input/output:** original photo and clear foreground → transparent PNG. Prefer extraction for identity-critical material; generative reconstruction can change the subject and must be disclosed.

**Discover/use:** check genuine segmentation/removal tools or existing editors first. For rembg, use inventory, `command -v rembg` or package metadata without importing candidate code. Read installed help/relevant source before first execution. With reviewed CLI and an explicit model whose terms/cache are suitable, the command shape is `rembg i -m MODEL input.png cutout.png` (replace MODEL). Never silently rely on a changing default or trigger a model download to test availability.

**Setup:** README says Python 3.11–3.13, while pyproject declares ^3.11: verify the chosen release/ONNX combination. CPU is possible; GPU adds runtime/hardware constraints. First inference may download weights. MIT code does not license every model: the documented BRIA default has commercial-use restrictions. Check selected weights' source/terms, cache, download size/network and hardware before proposing setup; this guide does not authorize downloads or installation.

**Check/fallback:** inspect actual alpha and subject against light/dark backgrounds, hair/glasses/clothing edges, holes, crop and resolution. PNG extension alone does not prove transparency. Missing tools plus no-install preference → manual cutout steps (`platform-setup.en.md#manual-cutout`), no fictitious PNG. No Canva MCP required.

Sources: [README/models](https://github.com/danielgatis/rembg), [runtime declaration](https://github.com/danielgatis/rembg/blob/main/pyproject.toml), [MIT license](https://github.com/danielgatis/rembg/blob/main/LICENSE.txt), [usage](https://github.com/danielgatis/rembg/blob/main/USAGE.md).

## Inpainting choices

[IOPaint](https://github.com/Sanster/IOPaint) still shows archival on 2025-08-13. [Apache-2.0](https://github.com/Sanster/IOPaint/blob/main/LICENSE) does not solve maintenance/model requirements. Exclude from new novice setup; do not assume a maintained fork. Existing installations require suitability review, not automatic removal.

First inspect existing host/editor mask support. Original + mask/selection + change/preserve brief → edited image. Check surrounding pixels, face and protected content, not just the selected area. Without a working tool, offer manual retouching in an existing editor.

Advanced candidate: [ComfyUI](https://github.com/Comfy-Org/ComfyUI) was unarchived and recently pushed in [metadata](https://api.github.com/repos/Comfy-Org/ComfyUI) checked this session; [README](https://github.com/Comfy-Org/ComfyUI#readme) documents inpainting. Core [GPL-3.0](https://github.com/Comfy-Org/ComfyUI/blob/master/LICENSE), nodes and weights need separate review. Consider only an already configured reviewed workflow or user-requested advanced setup. Inspect workflow inputs, model/hardware compatibility and local versus API execution; supply source/mask/prompt and check the returned image for drift. This is not an installed/validated D85 replacement; no execution was performed here. If unavailable, retain an edit brief/mask for manual handoff. Do not send novices into node/model installation for one small edit.

[BRIA model card and separate model license](https://huggingface.co/briaai/RMBG-2.0).
