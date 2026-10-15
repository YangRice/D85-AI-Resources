"""Behavioral tests for the standalone loopback SVG editing bridge."""
import hashlib
import http.client
import importlib.util
import json
from pathlib import Path
import tempfile
import threading
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'skills/edit-svg-canvas/scripts/edit_svg.py'
SVG = b'<svg xmlns="http://www.w3.org/2000/svg" width="300" height="200"><text x="10" y="30">Hello</text></svg>'


class EditorTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue(SCRIPT.is_file(), 'The standalone SVG editor launcher is missing')
        spec = importlib.util.spec_from_file_location('edit_svg', SCRIPT)
        self.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.mod)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / 'drawing.svg'
        self.source.write_bytes(SVG)
        self.editor = self.root / 'cache/src'
        self.editor.mkdir(parents=True)
        (self.editor / 'index.html').write_text('<body></body>')
        self.session = self.mod.Session(self.source, self.root / 'out')
        self.server = self.mod.make_server(self.session, self.editor, port=0)
        thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(self.server.shutdown)
        self.origin = f'http://127.0.0.1:{self.server.server_port}'

    def request(self, method, path, body=None, origin=None, headers=None):
        conn = http.client.HTTPConnection('127.0.0.1', self.server.server_port)
        h = dict(headers or {})
        if origin is not None:
            h['Origin'] = origin
        conn.request(method, path, body, h)
        response = conn.getresponse()
        result = response.status, response.read()
        conn.close()
        return result

    def test_save_returns_exact_revision_and_hash_without_changing_source(self):
        changed = SVG.replace(b'Hello', '你好 World'.encode())
        code, payload = self.request('POST', f'/{self.session.token}/finish', changed, self.origin)
        self.assertEqual(code, 200, payload)
        result = json.loads(payload)
        saved = Path(result['saved_path'])
        self.assertEqual(saved.read_bytes(), changed)
        self.assertEqual(result['saved_sha256'], hashlib.sha256(changed).hexdigest())
        self.assertEqual(self.source.read_bytes(), SVG)
        self.assertEqual(self.mod.read_status(self.session.status_path)['state'], 'complete')
        code, _ = self.request('POST', f'/{self.session.token}/finish', SVG, self.origin)
        self.assertEqual(code, 409)
        self.assertEqual(saved.read_bytes(), changed)

    def test_rejects_cross_origin_unknown_host_bad_token_and_paths(self):
        path = f'/{self.session.token}/finish'
        for origin in ('https://example.com', 'null', None):
            code, _ = self.request('POST', path, SVG, origin)
            self.assertEqual(code, 403)
        code, _ = self.request('POST', '/wrong/finish', SVG, self.origin)
        self.assertEqual(code, 404)
        code, _ = self.request('GET', f'/{self.session.token}/../drawing.svg')
        self.assertEqual(code, 404)
        code, _ = self.request('GET', f'/{self.session.token}/input.svg', headers={'Host': 'evil.example'})
        self.assertEqual(code, 403)
        self.assertFalse(list((self.root / 'out').glob('*edited*.svg')))

    def test_invalid_svg_does_not_finish_and_retry_succeeds(self):
        path = f'/{self.session.token}/finish'
        code, _ = self.request('POST', path, b'<svg><script/></svg>', self.origin)
        self.assertEqual(code, 400)
        self.assertEqual(self.mod.read_status(self.session.status_path)['state'], 'editing')
        code, _ = self.request('POST', path, SVG, self.origin)
        self.assertEqual(code, 200)

    def test_status_detects_saved_file_tampering(self):
        self.request('POST', f'/{self.session.token}/finish', SVG, self.origin)
        result = self.mod.read_status(self.session.status_path)
        Path(result['saved_path']).write_bytes(b'changed')
        with self.assertRaisesRegex(ValueError, 'hash|checksum'):
            self.mod.read_status(self.session.status_path)

    def test_embedded_image_pixels_preserved_and_href_normalized(self):
        raw = b'<svg xmlns="http://www.w3.org/2000/svg"><image href="data:image/png;base64,YWJj" width="1" height="1"/></svg>'
        prepared = self.mod.prepare_svg(raw)
        self.assertIn(b'data:image/png;base64,YWJj', prepared)
        self.assertIn(b'xlink:href', prepared)

    def test_blocks_active_external_and_unsupported_content(self):
        for content in ('<script/>', '<foreignObject/>', '<animate/>', '<filter><feOffset/></filter>',
                        '<image href="https://example.com/a.png"/>',
                        '<image href="../private.png"/>',
                        '<rect onclick="alert(1)"/>',
                        '<style>@import "https://example.com";</style>',
                        '<rect style="fill:url(https://example.com/p)"/>'):
            with self.subTest(content=content), self.assertRaises(ValueError):
                self.mod.prepare_svg(('<svg xmlns="http://www.w3.org/2000/svg">' + content + '</svg>').encode())

    def test_another_session_never_overwrites_a_previous_revision(self):
        a = self.session.finish(SVG)
        b = self.mod.Session(self.source, self.root / 'out').finish(SVG.replace(b'Hello', b'Other'))
        self.assertNotEqual(a['saved_path'], b['saved_path'])
        self.assertEqual(Path(a['saved_path']).read_bytes(), SVG)


if __name__ == '__main__':
    unittest.main()
