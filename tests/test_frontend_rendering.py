"""Exercise saved-text rendering in installed Chrome, with no server or database."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from html.parser import HTMLParser


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class ResultParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_results = False
        self.result = ""

    def handle_starttag(self, tag, attrs):
        if tag == "pre" and dict(attrs).get("id") == "results":
            self.in_results = True

    def handle_data(self, data):
        if self.in_results:
            self.result += data

    def handle_endtag(self, tag):
        if tag == "pre":
            self.in_results = False


class FrontendRenderingTests(unittest.TestCase):
    def test_saved_text_stays_literal_and_controls_still_work(self):
        chrome = (
            os.environ.get("PULSEPOINT_TEST_CHROME")
            or shutil.which("google-chrome")
            or shutil.which("chromium")
            or "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        )
        if not Path(chrome).is_file():
            self.skipTest("Install Chrome/Chromium or set PULSEPOINT_TEST_CHROME to run DOM checks.")
        template = (PROJECT_ROOT / "tests/frontend/record-renderers.html").read_text()
        renderer = (PROJECT_ROOT / "frontend/js/record-renderers.js").read_text()
        with tempfile.TemporaryDirectory(prefix="pulsepoint-rendering-tests-") as directory:
            page = Path(directory) / "regression.html"
            page.write_text(template.replace("<!-- RENDERERS -->", f"<script>{renderer}</script>"))
            process = subprocess.run([
                chrome, "--headless=new", "--disable-gpu", "--disable-extensions",
                "--disable-background-networking", "--disable-component-update",
                "--no-first-run", "--no-default-browser-check", "--no-proxy-server",
                "--host-resolver-rules=MAP * ~NOTFOUND",
                f"--user-data-dir={directory}/chrome-profile", "--dump-dom",
                "--virtual-time-budget=1000", page.as_uri(),
            ], capture_output=True, text=True, timeout=45)
            self.assertEqual(process.returncode, 0, "Headless Chrome failed; no database was accessed.")
            parser = ResultParser()
            parser.feed(process.stdout)
            self.assertNotEqual(parser.result, "pending", "The rendering fixture did not finish.")
            self.assertTrue(parser.result, "Headless Chrome returned no rendering results.")
            results = json.loads(parser.result)
            self.assertGreaterEqual(len(results), 25)
            for result in results:
                with self.subTest(check=result["name"]):
                    self.assertTrue(result["passed"])


if __name__ == "__main__":
    unittest.main()
