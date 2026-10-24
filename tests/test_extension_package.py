from __future__ import annotations

import json
from pathlib import Path
import re
import struct
import unittest


ROOT = Path(__file__).resolve().parents[1]
EXTENSION = ROOT / "browser_extension"
EXPECTED_FILES = {
    "README.md",
    "analyzer.mjs",
    "background.js",
    "content.js",
    "detector.mjs",
    "icon-128.png",
    "icon-16.png",
    "icon-32.png",
    "icon-48.png",
    "icon.svg",
    "links.mjs",
    "manifest.json",
    "nlp_report.html",
    "nlp_report.js",
    "popup.html",
    "popup.js",
    "selection.mjs",
    "styles.css",
    "tests/analyzer.test.mjs",
    "tests/detector.test.mjs",
    "tests/selection.test.mjs",
}
RUNTIME_FILES = {
    "analyzer.mjs",
    "background.js",
    "content.js",
    "detector.mjs",
    "icon-128.png",
    "icon-16.png",
    "icon-32.png",
    "icon-48.png",
    "links.mjs",
    "manifest.json",
    "nlp_report.html",
    "nlp_report.js",
    "popup.html",
    "popup.js",
    "selection.mjs",
    "styles.css",
}
ICON_FILES = {
    "icon-16.png": 16,
    "icon-32.png": 32,
    "icon-48.png": 48,
    "icon-128.png": 128,
}
TEXT_RUNTIME_FILES = RUNTIME_FILES - set(ICON_FILES)
# Known innerHTML user, excluded from the unsafe-HTML check only: background.js builds its
# in-page banner from fixed pattern strings, not page-derived text.
UNSAFE_HTML_EXCEPTIONS = {"background.js"}


class ExtensionPackageTests(unittest.TestCase):
    def test_package_allowlist_is_exact(self) -> None:
        for path in EXTENSION.rglob("*"):
            self.assertFalse(path.is_symlink(), path)
            self.assertTrue(path.is_file() or path.is_dir(), path)
        actual = {
            path.relative_to(EXTENSION).as_posix()
            for path in EXTENSION.rglob("*")
            if path.is_file()
        }
        self.assertEqual(actual, EXPECTED_FILES)

    def test_manifest_permissions_and_page_access_are_exact(self) -> None:
        manifest = json.loads((EXTENSION / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["manifest_version"], 3)
        self.assertEqual(manifest["permissions"], ["activeTab", "scripting", "tabs", "notifications"])
        self.assertEqual(manifest["host_permissions"], ["http://*/*", "https://*/*"])
        self.assertEqual(
            manifest["content_scripts"],
            [{"matches": ["<all_urls>"], "js": ["content.js"], "run_at": "document_end"}],
        )
        self.assertEqual(manifest["background"], {"service_worker": "background.js"})
        self.assertNotIn("optional_host_permissions", manifest)
        self.assertNotIn("externally_connectable", manifest)
        self.assertNotIn("web_accessible_resources", manifest)
        self.assertIn("selected", manifest["description"].lower())
        self.assertEqual(
            manifest["icons"],
            {
                "16": "icon-16.png",
                "32": "icon-32.png",
                "48": "icon-48.png",
                "128": "icon-128.png",
            },
        )
        self.assertEqual(manifest["action"]["default_popup"], "popup.html")
        self.assertEqual(
            manifest["action"]["default_icon"],
            {"16": "icon-16.png", "32": "icon-32.png"},
        )
        self.assertEqual(
            manifest["content_security_policy"]["extension_pages"],
            "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'none'; "
            "object-src 'none'; base-uri 'none'; form-action 'none'",
        )

    def test_runtime_references_are_local_and_present(self) -> None:
        html = (EXTENSION / "popup.html").read_text(encoding="utf-8")
        references = re.findall(r'(?:href|src)="([^"]+)"', html)
        self.assertEqual(set(references), {"styles.css", "popup.js", "popup.html?view=workspace"})
        for reference in references:
            self.assertFalse(reference.startswith(("http:", "https:", "//")))
            self.assertTrue((EXTENSION / reference.split("?", 1)[0]).is_file())

        javascript = (EXTENSION / "popup.js").read_text(encoding="utf-8")
        imports = re.findall(r'from\s+"\.\/([^"?]+)"', javascript)
        self.assertEqual(
            imports,
            ["analyzer.mjs", "detector.mjs", "links.mjs", "selection.mjs"],
        )
        for reference in imports:
            self.assertTrue((EXTENSION / reference).is_file())

    def test_product_version_identity_is_coordinated(self) -> None:
        manifest = json.loads((EXTENSION / "manifest.json").read_text(encoding="utf-8"))
        package_json = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
        analyzer = (EXTENSION / "analyzer.mjs").read_text(encoding="utf-8")
        engine_version = re.search(
            r'^export const ENGINE_VERSION = "([^"]+)";$',
            analyzer,
            re.MULTILINE,
        )

        self.assertIsNotNone(engine_version)
        assert engine_version is not None
        expected = manifest["version"]
        self.assertEqual(package_json["version"], expected)
        self.assertEqual(engine_version.group(1), expected)

    def test_runtime_has_no_remote_code_network_storage_or_unsafe_html(self) -> None:
        prohibited = {
            "remote module import": re.compile(r'''(?:from\s*|import\s*\()["']https?://''', re.IGNORECASE),
            "dynamic evaluation": re.compile(r"\beval\s*\(|\bnew\s+Function\b"),
            "unsafe HTML": re.compile(
                r"\.innerHTML\b|\binsertAdjacentHTML\b|\bdocument\.write\b"
            ),
            "network API": re.compile(
                r"\bfetch\s*\(|\bXMLHttpRequest\b|\bWebSocket\b|\bsendBeacon\b"
            ),
            "storage API": re.compile(
                r"\bchrome\.storage\b|\blocalStorage\b|\bsessionStorage\b|\bindexedDB\b"
            ),
        }
        for relative in sorted(TEXT_RUNTIME_FILES):
            text = (EXTENSION / relative).read_text(encoding="utf-8")
            for label, pattern in prohibited.items():
                if label == "unsafe HTML" and relative in UNSAFE_HTML_EXCEPTIONS:
                    continue
                with self.subTest(file=relative, label=label):
                    self.assertIsNone(pattern.search(text))

    def test_extension_pages_have_no_inline_script_or_handlers(self) -> None:
        # The extension CSP (script-src 'self') silently blocks inline code.
        for page in ("popup.html", "nlp_report.html"):
            with self.subTest(page=page):
                html = (EXTENSION / page).read_text(encoding="utf-8")
                for match in re.finditer(r"<script\b([^>]*)>(.*?)</script>", html, re.DOTALL):
                    self.assertIn("src=", match.group(1))
                    self.assertEqual(match.group(2).strip(), "")
                self.assertIsNone(re.search(r"\son[a-z]+\s*=", html))
        report = (EXTENSION / "nlp_report.html").read_text(encoding="utf-8")
        self.assertIn('<script src="nlp_report.js"></script>', report)

    def test_no_match_is_never_presented_as_safe(self) -> None:
        background = (EXTENSION / "background.js").read_text(encoding="utf-8")
        report = (EXTENSION / "nlp_report.js").read_text(encoding="utf-8")
        for source in (background, report):
            self.assertNotRegex(source, r"\bSAFE\b|APPEARS SAFE")
        self.assertIn("not a safety result", background)
        self.assertIn("not a safety result", report)

    def test_icon_assets_are_local_rgba_pngs_at_manifest_sizes(self) -> None:
        for filename, expected_size in ICON_FILES.items():
            with self.subTest(filename=filename):
                data = (EXTENSION / filename).read_bytes()
                self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
                self.assertEqual(struct.unpack(">II", data[16:24]), (expected_size, expected_size))
                self.assertEqual(data[25], 6)

    def test_popup_labels_actions_and_non_claims(self) -> None:
        html = (EXTENSION / "popup.html").read_text(encoding="utf-8")
        javascript = (EXTENSION / "popup.js").read_text(encoding="utf-8")
        stylesheet = (EXTENSION / "styles.css").read_text(encoding="utf-8")
        self.assertIn("Pattern checks can miss scams", html)
        self.assertIn('type="module"', html)
        self.assertIn('id="analyze"', html)
        self.assertIn('id="selection"', html)
        self.assertIn("Selection mode", html)
        self.assertIn('id="page-content"', html)
        self.assertIn('id="nlp-report"', html)
        self.assertIn('role="region"', html)
        self.assertIn('aria-labelledby="risk"', html)
        self.assertIn('aria-atomic="true"', html)
        self.assertIn('tabindex="-1"', html)
        self.assertIn("textContent", javascript)
        for heading in (
            "High-risk patterns found",
            "Worth a closer look",
            "No clear pattern match",
            "Could not analyze",
        ):
            self.assertIn(heading, javascript)
        self.assertNotIn("risk-low", stylesheet)
        self.assertNotIn("risk-medium", stylesheet)
        self.assertIn(":focus-visible", stylesheet)
        self.assertNotIn("maxlength=", html)
        self.assertNotIn('addEventListener("paste"', javascript)
        self.assertIn('id="mode-link"', html)
        self.assertIn('id="next-steps"', html)

    def test_selection_access_is_explicit_bounded_and_top_frame_only(self) -> None:
        popup = (EXTENSION / "popup.js").read_text(encoding="utf-8")
        selection = (EXTENSION / "selection.mjs").read_text(encoding="utf-8")
        self.assertIn('addEventListener("click"', popup)
        self.assertIn("requestSelectedPageText", popup)
        self.assertNotIn("message.value = selected", popup)
        self.assertNotIn("console.", popup + selection)
        self.assertIn("MAX_SELECTION_CODE_POINTS = 20_000", selection)
        self.assertIn("MAX_VISITED_TEXT_NODES = 10_000", selection)
        self.assertIn("{ active: true, currentWindow: true }", selection)
        self.assertIn("target: { tabId: tabs[0].id, frameIds: [0] }", selection)
        self.assertIn('world: "ISOLATED"', selection)
        self.assertNotIn("allFrames", selection)
        self.assertNotIn("tab.url", selection)
        self.assertNotIn("document.title", selection)
        self.assertNotIn("document.documentElement", selection)
        self.assertNotIn("querySelector", selection)


if __name__ == "__main__":
    unittest.main()
