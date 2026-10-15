#!/usr/bin/env python3
"""Open an SVG in a local Method Draw session; save a new revision on finish."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import json
import mimetypes
import os
from pathlib import Path, PurePosixPath
import re
import secrets
import tarfile
import tempfile
import threading
from urllib.parse import unquote, urlsplit
from urllib.request import urlopen
import webbrowser
import xml.etree.ElementTree as ET

COMMIT = 'c01c2f72b4497027eecb2a27e066c9bc5bf754c0'
ARCHIVE_SHA256 = '93cd9d7b92f6ea5d214364fa43ab50ef4cc4048b937b8fc6be72ee3cc4c21628'
ARCHIVE_URL = f'https://codeload.github.com/methodofaction/Method-Draw/tar.gz/{COMMIT}'
MAX_SVG = 48 * 1024 * 1024
SVG_NS = 'http://www.w3.org/2000/svg'
XLINK = 'http://www.w3.org/1999/xlink'
ET.register_namespace('', SVG_NS)
ET.register_namespace('xlink', XLINK)
ALLOWED = set(('svg g defs title desc metadata style image text tspan textPath '
               'rect circle ellipse line polyline polygon path clipPath mask '
               'linearGradient radialGradient stop pattern use symbol marker '
               'filter feGaussianBlur').split())


def sha(data):
    return hashlib.sha256(data).hexdigest()


def validate_svg(data):
    """Reject executable/external content and features Method Draw cannot edit."""
    if len(data) > MAX_SVG:
        raise ValueError('SVG exceeds the 48 MiB session limit')
    if re.search(br'<!\s*(?:DOCTYPE|ENTITY)', data, re.I):
        raise ValueError('SVG document types and entities are unsupported')
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        raise ValueError(f'Invalid SVG XML: {exc}') from exc
    if root.tag != f'{{{SVG_NS}}}svg':
        raise ValueError('Expected an SVG root in the SVG namespace')
    for node in root.iter():
        tag = node.tag.rsplit('}', 1)[-1]
        if tag not in ALLOWED or not node.tag.startswith('{' + SVG_NS + '}'):
            raise ValueError(f'Unsupported SVG element: {tag}')
        for name, value in node.attrib.items():
            local = name.rsplit('}', 1)[-1]
            if local.lower().startswith('on'):
                raise ValueError('SVG event handlers are unsupported')
            if local == 'href':
                if value.startswith('#'):
                    pass
                elif tag == 'image' and re.match(r'^data:image/(png|jpeg|jpg|webp);base64,[a-zA-Z0-9+/=\s]+$', value):
                    pass
                else:
                    raise ValueError('Embed raster images first; external/relative SVG references are unsupported')
        css = '\n'.join(node.attrib.values())
        if tag == 'style':
            css += node.text or ''
        if re.search(r'@import|expression\s*\(|javascript\s*:|\\', css, re.I):
            raise ValueError('Unsupported active or escaped SVG CSS')
        for url in re.findall(r'url\s*\(\s*([^)]+)\)', css, re.I):
            url = url.strip().strip('\'"')
            if not (url.startswith('#') or re.match(r'^data:(?:font/|application/(?:x-font|font-|vnd\.ms-fontobject))', url)):
                raise ValueError('External SVG/CSS resources are unsupported; embed them first')
    return root


def prepare_svg(data):
    root = validate_svg(data)
    for node in root.iter():
        if 'href' in node.attrib:
            node.set(f'{{{XLINK}}}href', node.attrib.pop('href'))
    return ET.tostring(root, encoding='utf-8', xml_declaration=True)


def atomic_json(path, value):
    fd, name = tempfile.mkstemp(dir=path.parent, prefix='.status-')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(value, stream, indent=2, ensure_ascii=False)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def read_status(path):
    result = json.loads(Path(path).read_text(encoding='utf-8'))
    if result['state'] == 'complete':
        saved = Path(result['saved_path'])
        if not saved.is_file() or sha(saved.read_bytes()) != result['saved_sha256']:
            raise ValueError('Saved SVG hash verification failed')
    return result


class Session:
    def __init__(self, source, output):
        self.source = Path(source).resolve(strict=True)
        original = self.source.read_bytes()
        self.prepared = prepare_svg(original)
        self.output = Path(output).resolve()
        self.output.mkdir(parents=True, exist_ok=True)
        self.token = secrets.token_urlsafe(24)
        self.directory = self.output / ('.svg-edit-' + secrets.token_hex(8))
        self.directory.mkdir()
        self.status_path = self.directory / 'session.json'
        self.lock = threading.Lock()
        self.result = {'version': 1, 'state': 'editing', 'source_path': str(self.source),
                       'source_sha256': sha(original), 'method_draw_commit': COMMIT}
        self.record()

    def record(self):
        atomic_json(self.status_path, self.result)

    def finish(self, data):
        validate_svg(data)
        with self.lock:
            if self.result['state'] == 'complete':
                raise FileExistsError('This editing session is already finished')
            # Write a complete temporary file, then publish using an exclusive
            # hard link so even concurrent sessions cannot overwrite a revision.
            fd, temporary = tempfile.mkstemp(dir=self.output, prefix='.svg-save-')
            saved = None
            try:
                with os.fdopen(fd, 'wb') as stream:
                    stream.write(data)
                    stream.flush()
                    os.fsync(stream.fileno())
                for revision in range(1, 10000):
                    candidate = self.output / f'{self.source.stem}-edited-{revision:03d}.svg'
                    try:
                        os.link(temporary, candidate)
                        saved = candidate
                        break
                    except FileExistsError:
                        continue
                if saved is None:
                    raise OSError('No available revision filename')
                updated = dict(self.result, state='complete', saved_path=str(saved),
                               saved_sha256=sha(data),
                               completed_at=datetime.now(timezone.utc).isoformat())
                try:
                    atomic_json(self.status_path, updated)
                except OSError:
                    saved.unlink()
                    raise
                self.result = updated
                return updated
            finally:
                Path(temporary).unlink(missing_ok=True)


def ensure_editor(cache, archive=None):
    """Check every cached file against the pinned upstream archive inventory."""
    cache = Path(cache).expanduser().resolve()
    target = cache / COMMIT
    inventory = target / '.verified-files.json'
    if inventory.is_file():
        files = json.loads(inventory.read_text())
        if files and all((target / name).is_file() and not (target / name).is_symlink()
                         and sha((target / name).read_bytes()) == digest
                         for name, digest in files.items()):
            return target / 'src'
        raise ValueError('Method Draw cache verification failed; use a fresh cache directory')
    if archive:
        data = Path(archive).read_bytes()
    else:
        with urlopen(ARCHIVE_URL, timeout=45) as response:
            data = response.read(16 * 1024 * 1024 + 1)
    if sha(data) != ARCHIVE_SHA256:
        raise ValueError('Method Draw archive checksum does not match the pinned revision')
    cache.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=cache, prefix='.install-') as tmp:
        staging = Path(tmp)
        files = {}
        with tarfile.open(fileobj=io.BytesIO(data), mode='r:gz') as bundle:
            for member in bundle.getmembers():
                path = PurePosixPath(member.name)
                relative = PurePosixPath(*path.parts[1:])
                if path.is_absolute() or '..' in path.parts or member.issym() or member.islnk():
                    raise ValueError('Unsafe path in Method Draw archive')
                if not member.isfile() or not relative.parts:
                    continue
                if relative.parts[0] != 'src' and str(relative) != 'LICENSE':
                    continue
                content = bundle.extractfile(member).read()
                destination = staging / str(relative)
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(content)
                files[str(relative)] = sha(content)
        if not (staging / 'src/index.html').is_file():
            raise ValueError('Archive is missing Method Draw')
        (staging / '.verified-files.json').write_text(json.dumps(files))
        if target.exists():
            raise ValueError('Incomplete Method Draw cache; use a fresh cache directory')
        staging.rename(target)
    return target / 'src'


def make_server(session, editor_root, port=0):
    editor_root = Path(editor_root).resolve()
    adapter = Path(__file__).with_name('bridge.js').read_bytes()

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass  # Do not log session tokens or SVG contents.

        def reply(self, code, data, mime='application/json; charset=utf-8'):
            self.send_response(code)
            self.send_header('Content-Type', mime)
            self.send_header('Content-Length', str(len(data)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('Referrer-Policy', 'no-referrer')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: blob:; font-src 'self' data:; connect-src 'self'; object-src 'none'; frame-ancestors 'none'; base-uri 'none'")
            self.end_headers()
            self.wfile.write(data)

        def route(self, write=False):
            origin = f'http://127.0.0.1:{self.server.server_port}'
            if self.headers.get('Host') != origin.removeprefix('http://'):
                self.reply(403, b'{"error":"Invalid Host"}')
                return None
            request_origin = self.headers.get('Origin')
            if (write and request_origin != origin) or (request_origin is not None and request_origin != origin):
                self.reply(403, b'{"error":"Invalid Origin"}')
                return None
            path = unquote(urlsplit(self.path).path)
            prefix = '/' + session.token + '/'
            if not path.startswith(prefix) or any(x in path.split('/') for x in ('..', '.')) or '\\' in path:
                self.reply(404, b'{}')
                return None
            return path[len(prefix):]

        def do_GET(self):
            route = self.route()
            if route is None:
                return
            if route == 'input.svg':
                self.reply(200, session.prepared, 'image/svg+xml')
            elif route == 'session':
                self.reply(200, json.dumps(session.result).encode())
            elif route == 'bridge.js':
                self.reply(200, adapter, 'application/javascript')
            elif route in ('js/loading.js', 'js/fonts.js'):
                # No cross-session preview or hundreds of external Google Fonts
                # requests; document fonts are retained inside the SVG instead.
                self.reply(200, b'/* Local editing session: no remote font catalog. */', 'application/javascript')
            else:
                file = (editor_root / (route or 'index.html')).resolve()
                if not file.is_relative_to(editor_root) or not file.is_file() or file.name.startswith('.'):
                    self.reply(404, b'{}')
                    return
                data = file.read_bytes()
                if route == 'js/svgcanvas.js':
                    # Upstream loops forever when text selection is empty.
                    data = data.replace(
                        b'while(selectedElements[0] == null) selectedElements.shift(0);',
                        b'while(selectedElements.length && selectedElements[0] == null) selectedElements.shift();')
                if route == 'js/svgutils.js':
                    # SvgCanvas captures this helper during construction. Patch
                    # the served definition before that binding: removing default
                    # values loses child overrides of inherited presentation.
                    data = data.replace(
                        b'svgedit.utilities.cleanupElement = function(element) {',
                        b'svgedit.utilities.cleanupElement = function(element) { return;')
                if route == 'js/state.js':
                    # Large embedded posters exceed localStorage quota. The
                    # explicit Finish endpoint is the sole durable handoff.
                    data = data.replace(b'function _save(key, val) {',
                                        b'function _save(key, val) { if (key === "canvasContent") return;')
                    data = data.replace(b'function _getValue(key, def) {',
                                        b'function _getValue(key, def) { if (key === "canvasContent") return def;')
                if file == editor_root / 'index.html':
                    data = data.replace(b'</body>', b'<script src="bridge.js"></script></body>')
                self.reply(200, data, mimetypes.guess_type(file.name)[0] or 'application/octet-stream')

        def do_POST(self):
            route = self.route(write=True)
            if route is None:
                return
            if route != 'finish':
                self.reply(404, b'{}')
                return
            try:
                length = int(self.headers.get('Content-Length', '-1'))
                if length < 1 or length > MAX_SVG:
                    self.reply(413, b'{"error":"SVG body must be between 1 byte and 48 MiB"}')
                    return
                self.connection.settimeout(15)
                data = self.rfile.read(length)
                if len(data) != length:
                    raise ValueError('Incomplete SVG request body')
                result = session.finish(data)
                self.reply(200, json.dumps(result, ensure_ascii=False).encode())
            except FileExistsError as exc:
                self.reply(409, json.dumps({'error': str(exc)}).encode())
            except (ValueError, OSError) as exc:
                self.reply(400, json.dumps({'error': str(exc)}).encode())

    class EditorServer(ThreadingHTTPServer):
        # Method Draw loads dozens of scripts/styles concurrently. macOS can
        # reset connections with HTTPServer's default five-request backlog.
        request_queue_size = 128

    return EditorServer(('127.0.0.1', port), Handler)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    launch = sub.add_parser('launch', help='Run until stopped; open the printed local URL')
    launch.add_argument('svg', type=Path)
    launch.add_argument('--output-dir', type=Path)
    launch.add_argument('--cache-dir', type=Path, default=Path.home() / '.cache/d85-method-draw')
    launch.add_argument('--archive', type=Path, help='Pre-downloaded official pinned archive')
    launch.add_argument('--port', type=int, default=0)
    launch.add_argument('--open', action='store_true')
    status = sub.add_parser('status', help='Read completion and verify saved SVG hash')
    status.add_argument('session_json', type=Path)
    args = parser.parse_args()
    if args.command == 'status':
        print(json.dumps(read_status(args.session_json), ensure_ascii=False, indent=2))
        return
    session = Session(args.svg, args.output_dir or args.svg.resolve().parent)
    editor_root = ensure_editor(args.cache_dir, args.archive)
    server = make_server(session, editor_root, args.port)
    url = f'http://127.0.0.1:{server.server_port}/{session.token}/index.html'
    session.result.update(editor_url=url, pid=os.getpid())
    session.record()
    print(json.dumps(dict(session.result, session_json=str(session.status_path)), ensure_ascii=False), flush=True)
    if args.open:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError) as error:
        raise SystemExit(str(error))
