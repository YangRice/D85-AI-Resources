# Local Method Draw runtime

Run Python 3.10+ with `scripts/edit_svg.py --help`. No Node dependency or editor
build is needed. The source lives in the skill package; Method Draw is downloaded
from its official repository to `~/.cache/d85-method-draw/<pinned-commit>/` by
default. Use `--cache-dir` for a writable alternative. The launcher checks the
archive checksum and then cached file hashes, retains the MIT license, and
does not install software globally. Use the host's normal network permission
mechanism when needed; do not replace the pinned archive with an unverified one.

For an offline/pre-downloaded setup, supply `--archive /path/to/archive.tar.gz`.
The pinned URL and SHA-256 are constants in the launcher. Failed or modified
caches must be replaced in a fresh cache directory. Initial download requires
GitHub access; once cached, the editor disables the upstream remote font catalog
and blocks external browser resource loading. Document images/fonts must be
embedded or already installed locally. The launcher rejects relative/remote
image references; embed authorized local assets into a working SVG copy first.

The launch command stays running and prints one JSON record containing
`editor_url`, `pid`, and `session_json`. Keep it running using the host's normal
terminal session or background process; do not leave the user an expired URL.
Each new session uses a fresh unpredictable URL and writes a `.svg-edit-*`
directory under the explicit output directory. Share that local URL with the
user only in their task. A browser reload starts from the input again until
finish, so use Finish before leaving. The editor warns about unsaved changes.

`status` returns `editing` until a valid SVG is saved. A complete record contains
`source_path`, `source_sha256`, `saved_path`, `saved_sha256`, and `completed_at`.
The command verifies saved bytes and exits with an error on hash mismatch. The
saved file is `<source-stem>-edited-001.svg`, increasing without overwriting an
existing revision. Original and generated build scripts remain untouched.
Double-click a grouped item to enter it, click its text, and use the Content
field to change wording. Press Escape to leave a group before selecting another
material. Background decorations baked into an image cannot move independently.
Failed saves keep the session editable; retry Finish. After a successful finish,
the canvas is disabled to avoid editing an already submitted revision. Start a
new session on the saved SVG for further changes.

Method Draw is a third-party SVG editor with partial SVG support. The adapter
rejects unsupported attributes and inline CSS properties before import, while
normalizing numeric, unitless/px `letter-spacing` into editable per-character
`tspan dx` values. Stylesheet rules other than embedded @font-face are explicitly
rejected; their cascade is not flattened. Save stays disabled on incompatibility.
Common text attributes outside Method Draw's whitelist, such as
`text-decoration`, are also rejected rather than silently dropped.
Text/image content is checked after import; this is not a full visual equivalence
proof. Check font faces, clipping, masks, transforms, and multiline text in the
actual render. The source and output remain available even if a feature is
unsupported. The generated portable text prompt needs this installed package to
execute; it must not invent a launcher in text-only chat.

The adapter preserves embedded font declarations, chained transforms, and image
rendering settings. It preserves explicit inherited presentation overrides by disabling upstream
default-value cleanup before canvas construction. It applies small served
compatibility patches to the
pinned upstream source (empty-selection guard and disabling large-document
localStorage autosave); cached originals remain unchanged. Finish is the durable
save action. The server uses an expanded connection backlog for reliable first
loads of the editor's many local assets.
