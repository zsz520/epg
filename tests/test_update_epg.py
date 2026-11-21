import gzip
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts import update_epg


XML = b'<?xml version="1.0"?><tv><channel id="c"><display-name>Test</display-name></channel><programme channel="c" start="20261122000000 +0800" stop="20261122010000 +0800"><title>Test</title></programme></tv>'


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def do_GET(self):
        if self.path == "/redirect":
            self.send_response(302)
            self.send_header("Location", "/xml")
            self.end_headers()
            return
        responses = {
            "/xml": (200, XML),
            "/gzip": (200, gzip.compress(XML)),
            "/html": (200, b"<html><body>Just a moment...</body></html>"),
            "/forbidden": (403, XML),
            "/empty": (200, b"<tv/>"),
            "/truncated": (200, XML[:-5]),
            "/bad-gzip": (200, gzip.compress(XML)[:-8]),
        }
        code, body = responses[self.path]
        self.send_response(code)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class UpdateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.base = f"http://127.0.0.1:{cls.server.server_port}"

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.thread.join()
        cls.server.server_close()

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.output = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)

    def update(self, path):
        return update_epg.update_one("test.xml", self.base + path, self.output)

    def test_redirect_and_gzip_output(self):
        self.assertEqual(self.update("/redirect")[1], "updated")
        self.assertEqual((self.output / "test.xml").read_bytes(), XML)
        self.assertEqual(gzip.decompress((self.output / "test.xml.gz").read_bytes()), XML)

    def test_compressed_source_and_stable_output(self):
        self.assertEqual(self.update("/gzip")[1], "updated")
        before = (self.output / "test.xml.gz").read_bytes()
        self.assertEqual(self.update("/xml")[1], "unchanged")
        self.assertEqual((self.output / "test.xml.gz").read_bytes(), before)

    def test_bad_responses_preserve_valid_cache(self):
        self.update("/xml")
        for path in ("/html", "/forbidden", "/empty", "/truncated", "/bad-gzip"):
            with self.subTest(path=path):
                self.assertEqual(self.update(path)[1], "failed")
                self.assertEqual((self.output / "test.xml").read_bytes(), XML)
                self.assertEqual(gzip.decompress((self.output / "test.xml.gz").read_bytes()), XML)
        self.assertFalse(list(self.output.glob(".download-*")))

    def test_missing_archive_is_rebuilt(self):
        (self.output / "test.xml").write_bytes(XML)
        self.assertEqual(self.update("/xml")[1], "updated")
        self.assertEqual(gzip.decompress((self.output / "test.xml.gz").read_bytes()), XML)

    def test_existing_error_page_is_removed(self):
        (self.output / "test.xml").write_bytes(b"<html>error</html>")
        (self.output / "test.xml.gz").write_bytes(gzip.compress(b"error"))
        result = self.update("/forbidden")
        self.assertEqual(result[1], "failed")
        self.assertIn("removed invalid", result[2])
        self.assertFalse((self.output / "test.xml").exists())
        self.assertFalse((self.output / "test.xml.gz").exists())

    def test_network_failure_is_isolated(self):
        with patch.object(update_epg, "fetch", side_effect=ValueError("DNS failed")):
            self.assertEqual(self.update("/xml")[1], "failed")
        self.assertEqual(self.update("/xml")[1], "updated")

    def test_proxy_only_for_livednow(self):
        def fake_fetch(url, destination, proxy):
            destination.write_bytes(XML)
        with patch.object(update_epg, "fetch", side_effect=fake_fetch) as fetch:
            update_epg.update_one("test.xml", update_epg.LIVEDNOW_URL, self.output, "proxy")
            self.assertEqual(fetch.call_args.args[2], "proxy")
            update_epg.update_one("test.xml", self.base + "/xml", self.output, "proxy")
            self.assertEqual(fetch.call_args.args[2], "")

    def test_main_publishes_healthy_sources_after_failure(self):
        self.run_main({"bad.xml": self.base + "/forbidden", "good.xml": self.base + "/xml"}, 0)
        self.assertEqual((self.output / "good.xml").read_bytes(), XML)
        self.assertFalse((self.output / "bad.xml").exists())

    def test_main_fails_if_all_sources_fail(self):
        self.run_main({"bad.xml": self.base + "/forbidden"}, 1)

    def run_main(self, sources, expected):
        config = self.output / "files.json"
        config.write_text(json.dumps(sources))
        result = subprocess.run([sys.executable, update_epg.__file__, "--config", str(config),
                                 "--output", str(self.output)], capture_output=True, text=True)
        self.assertEqual(result.returncode, expected, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
