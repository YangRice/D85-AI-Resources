---
name: edit-svg-canvas
description: Use when users want to edit a design themselves, change poster text, move a photo or logo, or adjust an existing layout visually, and an editable SVG source exists or can be located. Users need not know SVG, Method Draw, or the skill name.
---

# Edit a design visually

Let the user edit the current design visually, then continue from their exact
saved changes. This works independently of Toastmasters or any document task.

## Choose the canvas before launching

If the host has a built-in canvas that supports the requested edits, ask the
user to choose **Built-in canvas (recommended/default)** or **SVG editor
(Method Draw)**. Honor a choice already made in this conversation without asking
again. Default means the recommended option, not permission to skip the question
or infer an answer from silence. A static image or file preview is not an
editable canvas.

For the built-in canvas, load the latest editable design, let the user edit,
and capture their latest saved/exported state. Apply that exact state to the
editable source before continuing the task's rendering and review checks; never
rebuild an older layout over their changes. Do not launch Method Draw on this
route. If the built-in canvas cannot preserve the required edits, explain the
limitation and offer the SVG editor.

Use the Method Draw launch instructions below only when the user chooses it or
no suitable built-in canvas exists. Let the user edit text and move materials,
then click **Save and finish / 儲存並完成** to save a new SVG revision directly
into the task's output folder.

## Recognize the user's intent

Requests such as “let me change this myself”, “I want to edit the poster”,
“move the photo”, “我要自己改文字”, “我想手動編輯”, and “讓我調整位置” are enough.
Do not ask the user to name a file format or editor. Find the current task's
editable source first. If several plausible designs remain, ask which one.
For a plain instruction such as “change the title to X”, make the requested edit
directly unless the user wants a visual editing session.

If only a flattened image exists, explain that text and materials must first be
reconstructed as separate elements; do not promise that a PNG becomes editable
merely by putting it inside an SVG.

## Launch and return

Resolve `scripts/edit_svg.py` relative to this installed skill, not the task's
working directory. Read [runtime instructions](references/runtime.en.md) for
cache preparation, fonts, session lifecycle, and recovery.

```sh
python3 /absolute/path/to/edit-svg-canvas/scripts/edit_svg.py launch /absolute/path/to/design.svg --output-dir /absolute/path/to/task/output --open
```

Run this as a persistent process using the host's supported background/session
mechanism. Keep its process alive while the user edits. Open the printed
`editor_url` in an available browser and retain the printed `session_json` path
in the conversation. In Codex a browser panel can show this URL; a normal browser
is the baseline for WorkBuddy and other hosts. Explain: “Edit the text or drag
items. Click Save and finish, then return here and say continue.”

When the user returns, run:

```sh
python3 /absolute/path/to/edit-svg-canvas/scripts/edit_svg.py status /absolute/path/to/session.json
```

Only `state: complete` plus successful hash verification establishes a finished
handoff. Use `saved_path` as the new source; never regenerate from a stale build
script that would discard the user's edits. An editing state means no finish
has been saved yet. Stop only this session's server after handoff or cancellation.

Saving returns an SVG; the caller decides whether to render PNG/PDF or resume
another task. For posters, rerender the exact saved file and repeat the caller's
visual, protected-asset, QR, and independent review requirements. Saving does not
automatically message an agent, call an image model, or publish anything.

## Limits and truthfulness

The Method Draw launcher needs Python 3.10+, permission to bind a loopback port, and first-use
network access or the verified archive/cache. It preserves originals and writes
new revisions. Unsupported active/external SVG content is rejected explicitly.
Embedded raster artwork stays raster; outlined text cannot be edited as words.
Inspect the imported design and final saved rendering for font/layout changes.
If a host cannot launch a server, offer a manual handoff and identify the missing
capability. A text-only portable prompt does not contain the executable package.
Do not claim WorkBuddy discovery or successful editing without testing it there.
