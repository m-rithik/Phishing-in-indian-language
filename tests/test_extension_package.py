from __future__ import annotations

from contextlib import contextmanager
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import shutil
import stat
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import zipfile

try:
    import fisher_extension_package as package
except ModuleNotFoundError:
    package = None


ROOT = Path(__file__).resolve().parents[1]
EXTENSION = ROOT / "browser_extension"
EXPECTED_FILES = {
    "README.md",
    "analyzer.mjs",
    "detector.mjs",
    "icon-128.png",
    "icon-16.png",
    "icon-32.png",
    "icon-48.png",
    "icon.svg",
    "links.mjs",
    "manifest.json",
    "popup.html",
    "popup.js",
    "selection.mjs",
    "styles.css",
    "tests/analyzer.test.mjs",
    "tests/detector.test.mjs",
    "tests/realistic_messages.test.mjs",
    "tests/selection.test.mjs",
}
RUNTIME_FILES = {
    "analyzer.mjs",
    "detector.mjs",
    "icon-128.png",
    "icon-16.png",
    "icon-32.png",
    "icon-48.png",
    "links.mjs",
    "manifest.json",
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
EXPECTED_ORDER = tuple(sorted(EXPECTED_FILES))


class RepositoryFixture:
    def __init__(self, *, reverse_order: bool = False) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "repository"
        extension = self.root / "browser_extension"
        (extension / "tests").mkdir(parents=True)
        order = list(EXPECTED_ORDER)
        if reverse_order:
            order.reverse()
        for relative in order:
            target = extension / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((EXTENSION / relative).read_bytes())
            target.chmod(0o644)

    @property
    def extension(self) -> Path:
        return self.root / "browser_extension"

    @property
    def output_base(self) -> Path:
        return self.root / "outputs" / "browser_extension"

    @property
    def destination(self) -> Path:
        assert package is not None
        return self.output_base / package.ARCHIVE_FILENAME

    def close(self) -> None:
        self.temporary.cleanup()


@contextmanager
def temporary_umask(value: int):
    previous = os.umask(value)
    try:
        yield
    finally:
        os.umask(previous)


class ExtensionPackageTests(unittest.TestCase):
    def test_packaging_module_is_present(self) -> None:
        self.assertTrue((ROOT / "fisher_extension_package.py").is_file())

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

    def test_manifest_has_exact_temporary_permissions_and_no_standing_page_access(self) -> None:
        manifest = json.loads((EXTENSION / "manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["manifest_version"], 3)
        self.assertEqual(manifest["version"], "0.6.0")
        self.assertEqual(manifest["permissions"], ["activeTab", "scripting"])
        self.assertNotIn("host_permissions", manifest)
        self.assertNotIn("optional_host_permissions", manifest)
        self.assertNotIn("content_scripts", manifest)
        self.assertNotIn("background", manifest)
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
        self.assertEqual(package.EXPECTED_MANIFEST["version"], expected)
        self.assertEqual(package.DISTRIBUTION_NAME, f"fisher-scam-signal-prototype-v{expected}")

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
        combined = "\n".join(
            (EXTENSION / relative).read_text(encoding="utf-8")
            for relative in sorted(TEXT_RUNTIME_FILES)
        )
        for label, pattern in prohibited.items():
            with self.subTest(label=label):
                self.assertIsNone(pattern.search(combined))

    def test_icon_assets_are_local_rgba_pngs_at_manifest_sizes(self) -> None:
        for filename, expected_size in ICON_FILES.items():
            with self.subTest(filename=filename):
                data = (EXTENSION / filename).read_bytes()
                self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
                self.assertEqual(struct.unpack(">II", data[16:24]), (expected_size, expected_size))
                self.assertEqual(data[25], 6)

    def test_popup_is_explicit_action_only_and_labels_non_claims(self) -> None:
        html = (EXTENSION / "popup.html").read_text(encoding="utf-8")
        javascript = (EXTENSION / "popup.js").read_text(encoding="utf-8")
        stylesheet = (EXTENSION / "styles.css").read_text(encoding="utf-8")
        self.assertIn("Pattern checks can miss scams", html)
        self.assertIn('type="module"', html)
        self.assertIn('id="analyze"', html)
        self.assertIn('id="selection"', html)
        self.assertIn("Analyze selected text", html)
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


@unittest.skipIf(package is None, "packaging module not implemented")
class DeterministicDistributionTests(unittest.TestCase):
    def test_exact_archive_bytes_metadata_and_runtime_only_members(self) -> None:
        fixture = RepositoryFixture()
        self.addCleanup(fixture.close)
        distribution = package.build_distribution(
            repository_root=fixture.root,
            output_base=fixture.output_base,
        )

        archive_bytes = distribution.archive_path.read_bytes()
        digest = sha256(archive_bytes).hexdigest()
        self.assertEqual(distribution.sha256, digest)
        self.assertEqual(distribution.member_count, len(RUNTIME_FILES))
        self.assertEqual(distribution.byte_count, len(archive_bytes))
        self.assertEqual(
            {path.name for path in fixture.output_base.iterdir()},
            {package.ARCHIVE_FILENAME},
        )
        self.assertEqual(stat.S_IMODE(distribution.archive_path.stat().st_mode), 0o644)
        self.assertFalse(hasattr(distribution, "checksum_path"))

        with zipfile.ZipFile(distribution.archive_path) as archive:
            self.assertEqual(archive.namelist(), sorted(RUNTIME_FILES))
            self.assertEqual(archive.comment, b"")
            self.assertIsNone(archive.testzip())
            for info in archive.infolist():
                self.assertEqual(info.date_time, (1980, 1, 1, 0, 0, 0))
                self.assertEqual(info.compress_type, zipfile.ZIP_STORED)
                self.assertEqual(info.create_system, 3)
                self.assertEqual(info.external_attr >> 16, stat.S_IFREG | 0o644)
                self.assertEqual(info.extra, b"")
                self.assertEqual(info.comment, b"")
                self.assertEqual(archive.read(info), (fixture.extension / info.filename).read_bytes())

    def test_separate_builds_are_identical_despite_mtime_umask_and_entry_order(self) -> None:
        first = RepositoryFixture()
        second = RepositoryFixture(reverse_order=True)
        self.addCleanup(first.close)
        self.addCleanup(second.close)
        for index, relative in enumerate(EXPECTED_ORDER):
            os.utime(first.extension / relative, ns=(1_700_000_000_000_000_000 + index,)*2)
            os.utime(second.extension / relative, ns=(1_800_000_000_000_000_000 - index,)*2)
        with temporary_umask(0o077):
            first_distribution = package.build_distribution(
                repository_root=first.root,
                output_base=first.output_base,
            )
        with temporary_umask(0o002):
            second_distribution = package.build_distribution(
                repository_root=second.root,
                output_base=second.output_base,
            )
        self.assertEqual(
            first_distribution.archive_path.read_bytes(),
            second_distribution.archive_path.read_bytes(),
        )

    def test_source_shape_and_output_safety_rejections_leave_no_final_destination(self) -> None:
        def expect_rejection(
            mutator,
            *,
            output_outside: bool = False,
            destination_preexists: bool = False,
        ) -> None:
            fixture = RepositoryFixture()
            try:
                mutator(fixture)
                output_base = fixture.root / "elsewhere" if output_outside else fixture.output_base
                with self.assertRaises(package.PackagingError):
                    package.build_distribution(
                        repository_root=fixture.root,
                        output_base=output_base,
                    )
                if destination_preexists:
                    self.assertTrue(fixture.destination.is_dir())
                    self.assertEqual(list(fixture.destination.iterdir()), [])
                else:
                    self.assertFalse(fixture.destination.exists())
            finally:
                fixture.close()

        cases = {
            "symlink": lambda fixture: (
                (fixture.extension / "manifest.json").unlink(),
                (fixture.extension / "manifest.json").symlink_to("README.md"),
            ),
            "fifo": lambda fixture: (
                (fixture.extension / "popup.js").unlink(),
                os.mkfifo(fixture.extension / "popup.js"),
            ),
            "hardlink": lambda fixture: (
                (fixture.extension / "styles.css").unlink(),
                os.link(fixture.extension / "README.md", fixture.extension / "styles.css"),
            ),
            "unsafe_mode": lambda fixture: (fixture.extension / "README.md").chmod(0o664),
            "missing": lambda fixture: (fixture.extension / "popup.html").unlink(),
            "extra": lambda fixture: (fixture.extension / "extra.js").write_text(
                "extra", encoding="utf-8"
            ),
            "outside_output": lambda fixture: None,
            "existing_destination": lambda fixture: fixture.destination.mkdir(parents=True),
        }
        for name, mutator in cases.items():
            with self.subTest(name=name):
                expect_rejection(
                    mutator,
                    output_outside=name == "outside_output",
                    destination_preexists=name == "existing_destination",
                )

        existing_file = RepositoryFixture()
        self.addCleanup(existing_file.close)
        existing_file.destination.parent.mkdir(parents=True)
        existing_file.destination.write_bytes(b"do-not-overwrite")
        with self.assertRaises(package.PackagingError):
            package.build_distribution(
                repository_root=existing_file.root,
                output_base=existing_file.output_base,
            )
        self.assertEqual(existing_file.destination.read_bytes(), b"do-not-overwrite")

    def test_member_and_total_size_bounds_are_enforced(self) -> None:
        fixture = RepositoryFixture()
        self.addCleanup(fixture.close)
        (fixture.extension / "README.md").write_bytes(b"x" * (1024 * 1024 + 1))
        with self.assertRaises(package.PackagingError):
            package.build_distribution(
                repository_root=fixture.root,
                output_base=fixture.output_base,
            )
        self.assertFalse(fixture.destination.exists())

        total_fixture = RepositoryFixture()
        self.addCleanup(total_fixture.close)
        for relative in EXPECTED_ORDER[:6]:
            (total_fixture.extension / relative).write_bytes(b"x" * 900_000)
        with self.assertRaises(package.PackagingError):
            package.build_distribution(
                repository_root=total_fixture.root,
                output_base=total_fixture.output_base,
            )
        self.assertFalse(total_fixture.destination.exists())

    def test_manifest_contract_mutations_are_rejected(self) -> None:
        mutations = {
            "version": lambda manifest: manifest.update(version="0.2.1"),
            "manifest_float": lambda manifest: manifest.update(manifest_version=3.0),
            "manifest_bool": lambda manifest: manifest.update(manifest_version=True),
            "name": lambda manifest: manifest.update(name="Other"),
            "description": lambda manifest: manifest.update(description="Other"),
            "permissions": lambda manifest: manifest.update(permissions=[]),
            "permissions_reordered": lambda manifest: manifest.update(
                permissions=["scripting", "activeTab"]
            ),
            "icons": lambda manifest: manifest.pop("icons"),
            "tabs_permission": lambda manifest: manifest.update(
                permissions=["activeTab", "scripting", "tabs"]
            ),
            "host_permissions": lambda manifest: manifest.update(
                host_permissions=["<all_urls>"]
            ),
            "optional_host_permissions": lambda manifest: manifest.update(
                optional_host_permissions=["<all_urls>"]
            ),
            "background": lambda manifest: manifest.update(background={}),
            "content_scripts": lambda manifest: manifest.update(content_scripts=[]),
            "web_accessible_resources": lambda manifest: manifest.update(
                web_accessible_resources=[]
            ),
            "externally_connectable": lambda manifest: manifest.update(
                externally_connectable={}
            ),
            "sandbox": lambda manifest: manifest.update(sandbox={}),
            "update_url": lambda manifest: manifest.update(update_url="local"),
            "csp": lambda manifest: manifest.update(content_security_policy={}),
            "popup": lambda manifest: manifest["action"].update(default_popup="other.html"),
            "action_icon": lambda manifest: manifest["action"].pop("default_icon"),
            "action_extra": lambda manifest: manifest["action"].update(extra="value"),
            "title": lambda manifest: manifest["action"].update(default_title="Other"),
        }
        for name, mutation in mutations.items():
            with self.subTest(name=name):
                fixture = RepositoryFixture()
                try:
                    manifest_path = fixture.extension / "manifest.json"
                    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                    mutation(manifest)
                    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
                    with self.assertRaises(package.PackagingError):
                        package.build_distribution(
                            repository_root=fixture.root,
                            output_base=fixture.output_base,
                        )
                    self.assertFalse(fixture.destination.exists())
                finally:
                    fixture.close()

        for invalid_constant in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(constant=invalid_constant):
                fixture = RepositoryFixture()
                try:
                    manifest_path = fixture.extension / "manifest.json"
                    manifest_path.write_text(invalid_constant, encoding="utf-8")
                    with self.assertRaises(package.PackagingError):
                        package.build_distribution(
                            repository_root=fixture.root,
                            output_base=fixture.output_base,
                        )
                finally:
                    fixture.close()

    def test_source_directories_are_safe_and_rechecked(self) -> None:
        for relative in (".", "browser_extension", "browser_extension/tests"):
            with self.subTest(relative=relative):
                fixture = RepositoryFixture()
                try:
                    (fixture.root / relative).chmod(0o775)
                    with self.assertRaises(package.PackagingError):
                        package.build_distribution(
                            repository_root=fixture.root,
                            output_base=fixture.output_base,
                        )
                finally:
                    fixture.close()

        for relative in ("outputs", "outputs/browser_extension"):
            with self.subTest(relative=relative):
                fixture = RepositoryFixture()
                try:
                    fixture.output_base.mkdir(parents=True)
                    (fixture.root / relative).chmod(0o775)
                    with self.assertRaises(package.PackagingError):
                        package.build_distribution(
                            repository_root=fixture.root,
                            output_base=fixture.output_base,
                        )
                    self.assertFalse(fixture.destination.exists())
                finally:
                    fixture.close()

        directory_shape_mutations = {
            "root_symlink": lambda fixture: (
                fixture.extension.rename(fixture.root / "extension-real"),
                fixture.extension.symlink_to(
                    fixture.root / "extension-real", target_is_directory=True
                ),
            ),
            "root_non_directory": lambda fixture: (
                shutil.rmtree(fixture.extension),
                fixture.extension.write_text("not a directory", encoding="utf-8"),
            ),
            "tests_symlink": lambda fixture: (
                shutil.rmtree(fixture.extension / "tests"),
                (fixture.extension / "tests").symlink_to(".", target_is_directory=True),
            ),
            "tests_non_directory": lambda fixture: (
                shutil.rmtree(fixture.extension / "tests"),
                (fixture.extension / "tests").write_text("not a directory", encoding="utf-8"),
            ),
        }
        for name, mutation in directory_shape_mutations.items():
            with self.subTest(name=name):
                fixture = RepositoryFixture()
                try:
                    mutation(fixture)
                    with self.assertRaises(package.PackagingError):
                        package.build_distribution(
                            repository_root=fixture.root,
                            output_base=fixture.output_base,
                        )
                finally:
                    fixture.close()

        fixture = RepositoryFixture()
        self.addCleanup(fixture.close)
        original_builder = package._build_archive_bytes

        def mutate_directory_after_capture(captured):
            archive = original_builder(captured)
            directory = fixture.extension / "tests"
            metadata = directory.stat()
            os.utime(
                directory,
                ns=(metadata.st_atime_ns, metadata.st_mtime_ns + 1_000_000_000),
            )
            return archive

        with mock.patch.object(
            package, "_build_archive_bytes", side_effect=mutate_directory_after_capture
        ):
            with self.assertRaises(package.PackagingError):
                package.build_distribution(
                    repository_root=fixture.root,
                    output_base=fixture.output_base,
                )

    def test_prepublication_mutation_and_corruption_are_detected(self) -> None:
        fixture = RepositoryFixture()
        self.addCleanup(fixture.close)
        original_builder = package._build_archive_bytes

        def mutate_after_capture(captured):
            archive = original_builder(captured)
            (fixture.extension / "popup.js").write_bytes(b"changed after capture")
            return archive

        with mock.patch.object(package, "_build_archive_bytes", side_effect=mutate_after_capture):
            with self.assertRaises(package.PackagingError):
                package.build_distribution(
                    repository_root=fixture.root,
                    output_base=fixture.output_base,
                )
        self.assertFalse(fixture.destination.exists())
        self.assertTrue(
            not fixture.output_base.exists() or list(fixture.output_base.iterdir()) == []
        )

        clean = RepositoryFixture()
        self.addCleanup(clean.close)
        root_fd = package._open_directory(clean.root, message="test")
        source_fd = package._open_directory(
            "browser_extension", dir_fd=root_fd, message="test"
        )
        tests_fd = package._open_directory("tests", dir_fd=source_fd, message="test")
        try:
            captured, _ = package._capture_sources(source_fd, tests_fd)
        finally:
            os.close(tests_fd)
            os.close(source_fd)
            os.close(root_fd)
        archive_bytes = package._build_archive_bytes(captured)
        corrupted = bytearray(archive_bytes)
        corrupted[len(corrupted) // 2] ^= 1
        with self.assertRaises(package.PackagingError):
            package._validate_distribution_bytes(
                bytes(corrupted),
                archive_bytes,
                captured,
            )
        with self.assertRaises(package.PackagingError):
            package._validate_distribution_bytes(b"prefix" + archive_bytes, archive_bytes, captured)
        with self.assertRaises(package.PackagingError):
            package._validate_distribution_bytes(archive_bytes + b"suffix", archive_bytes, captured)

    def test_output_fd_anchor_rejects_symlink_swap_without_touching_outside(self) -> None:
        fixture = RepositoryFixture()
        self.addCleanup(fixture.close)
        fixture.output_base.mkdir(parents=True)
        outside = fixture.root / "outside"
        outside.mkdir()
        moved = fixture.root / "moved-output"
        original_recheck = package._recheck_sources

        def swap_after_recheck(*args, **kwargs):
            original_recheck(*args, **kwargs)
            fixture.output_base.rename(moved)
            fixture.output_base.symlink_to(outside, target_is_directory=True)

        with mock.patch.object(package, "_recheck_sources", side_effect=swap_after_recheck):
            with self.assertRaises(package.PackagingError):
                package.build_distribution(
                    repository_root=fixture.root,
                    output_base=fixture.output_base,
                )
        self.assertEqual(list(outside.iterdir()), [])
        self.assertFalse((moved / package.ARCHIVE_FILENAME).exists())
        self.assertEqual(list(moved.iterdir()), [])

    def test_concurrent_destination_and_injected_publish_failure_never_overwrite(self) -> None:
        concurrent = RepositoryFixture()
        self.addCleanup(concurrent.close)
        original_recheck = package._recheck_sources

        def claim_concurrently(*args, **kwargs):
            original_recheck(*args, **kwargs)
            concurrent.destination.mkdir(parents=True)

        with mock.patch.object(package, "_recheck_sources", side_effect=claim_concurrently):
            with self.assertRaises(package.PackagingError):
                package.build_distribution(
                    repository_root=concurrent.root,
                    output_base=concurrent.output_base,
                )
        self.assertTrue(concurrent.destination.is_dir())
        self.assertEqual(list(concurrent.destination.iterdir()), [])

        injected = RepositoryFixture()
        self.addCleanup(injected.close)
        with mock.patch.object(package.os, "link", side_effect=OSError("injected")):
            with self.assertRaises(package.PackagingError):
                package.build_distribution(
                    repository_root=injected.root,
                    output_base=injected.output_base,
                )
        self.assertFalse(injected.destination.exists())
        self.assertTrue(
            not injected.output_base.exists() or list(injected.output_base.iterdir()) == []
        )

    def test_staged_archive_symlink_swap_is_rejected_after_atomic_link(self) -> None:
        fixture = RepositoryFixture()
        self.addCleanup(fixture.close)
        outside = fixture.root / "outside.zip"
        outside.write_bytes(b"outside-must-not-be-read-or-changed")
        original_recheck = package._recheck_sources
        original_link = os.link
        link_calls = 0

        def swap_staged_archive(*args, **kwargs):
            original_recheck(*args, **kwargs)
            staging = next(
                path
                for path in fixture.output_base.iterdir()
                if path.name.startswith(".fisher-extension-")
            )
            self.assertEqual(stat.S_IMODE(staging.stat().st_mode), 0o700)
            staged_archive = staging / package.ARCHIVE_FILENAME
            staged_archive.unlink()
            staged_archive.symlink_to(outside)

        def count_link(*args, **kwargs):
            nonlocal link_calls
            link_calls += 1
            return original_link(*args, **kwargs)

        with (
            mock.patch.object(
                package,
                "_recheck_sources",
                side_effect=swap_staged_archive,
            ),
            mock.patch.object(package.os, "link", side_effect=count_link),
        ):
            with self.assertRaises(package.PackagingError):
                package.build_distribution(
                    repository_root=fixture.root,
                    output_base=fixture.output_base,
                )
        self.assertEqual(link_calls, 0)
        self.assertEqual(outside.read_bytes(), b"outside-must-not-be-read-or-changed")
        self.assertFalse(fixture.destination.exists())
        self.assertTrue(
            not fixture.output_base.exists() or list(fixture.output_base.iterdir()) == []
        )

    def test_output_replacement_after_link_preserves_anchored_public_archive(self) -> None:
        fixture = RepositoryFixture()
        self.addCleanup(fixture.close)
        fixture.output_base.mkdir(parents=True)
        moved = fixture.root / "moved-output"
        original_link = os.link

        def replace_after_link(*args, **kwargs):
            result = original_link(*args, **kwargs)
            fixture.output_base.rename(moved)
            fixture.output_base.mkdir()
            return result

        with mock.patch.object(package.os, "link", side_effect=replace_after_link):
            with self.assertRaises(package.PackagingError):
                package.build_distribution(
                    repository_root=fixture.root,
                    output_base=fixture.output_base,
                )
        moved_archive = moved / package.ARCHIVE_FILENAME
        self.assertTrue(moved_archive.read_bytes().startswith(b"PK"))
        self.assertEqual(moved_archive.stat().st_nlink, 1)
        self.assertEqual({path.name for path in moved.iterdir()}, {package.ARCHIVE_FILENAME})
        self.assertEqual(list(fixture.output_base.iterdir()), [])

    def test_cleanup_preserves_replacement_of_owned_public_archive(self) -> None:
        fixture = RepositoryFixture()
        self.addCleanup(fixture.close)
        replacement = b"concurrent-owner-replacement"
        original_check = package._check_archive
        checks = 0

        def replace_before_post_link_check(*args, **kwargs):
            nonlocal checks
            checks += 1
            if checks == 3:
                fixture.destination.unlink()
                fixture.destination.write_bytes(replacement)
            return original_check(*args, **kwargs)

        with mock.patch.object(
            package,
            "_check_archive",
            side_effect=replace_before_post_link_check,
        ):
            with self.assertRaises(package.PackagingError):
                package.build_distribution(
                    repository_root=fixture.root,
                    output_base=fixture.output_base,
                )
        self.assertGreaterEqual(checks, 3)
        self.assertEqual(fixture.destination.read_bytes(), replacement)
        self.assertEqual(
            {path.name for path in fixture.output_base.iterdir()},
            {package.ARCHIVE_FILENAME},
        )
        self.assertEqual(fixture.destination.stat().st_nlink, 1)

    def test_post_publication_failure_preserves_public_name_and_moved_archive(self) -> None:
        fixture = RepositoryFixture()
        self.addCleanup(fixture.close)
        moved_owned = fixture.root / "moved-owned.zip"
        replacement = b"replacement-after-cleanup-check"
        original_check = package._check_archive
        checks = 0
        interposed = False

        def fail_post_link_check(*args, **kwargs):
            nonlocal checks, interposed
            checks += 1
            if checks == 3:
                fixture.destination.rename(moved_owned)
                fixture.destination.write_bytes(replacement)
                interposed = True
                raise package.PackagingError("injected post-link failure")
            return original_check(*args, **kwargs)

        with mock.patch.object(
            package,
            "_check_archive",
            side_effect=fail_post_link_check,
        ):
            with self.assertRaises(package.PackagingError):
                package.build_distribution(
                    repository_root=fixture.root,
                    output_base=fixture.output_base,
                )
        self.assertTrue(interposed)
        self.assertEqual(fixture.destination.read_bytes(), replacement)
        self.assertTrue(moved_owned.read_bytes().startswith(b"PK"))
        self.assertEqual(moved_owned.stat().st_nlink, 1)

    def test_staging_cleanup_failures_preserve_public_archive(self) -> None:
        for operation in ("unlink", "rmdir"):
            with self.subTest(operation=operation):
                fixture = RepositoryFixture()
                try:
                    if operation == "unlink":
                        original = os.unlink
                        injected = False

                        def fail_staged_unlink(path, *args, **kwargs):
                            nonlocal injected
                            if path == package.ARCHIVE_FILENAME and not injected:
                                injected = True
                                raise OSError("injected cleanup failure")
                            return original(path, *args, **kwargs)

                        patcher = mock.patch.object(
                            package.os,
                            "unlink",
                            side_effect=fail_staged_unlink,
                        )
                    else:
                        original = os.rmdir
                        injected = False

                        def fail_staging_rmdir(path, *args, **kwargs):
                            nonlocal injected
                            if str(path).startswith(".fisher-extension-") and not injected:
                                injected = True
                                raise OSError("injected cleanup failure")
                            return original(path, *args, **kwargs)

                        patcher = mock.patch.object(
                            package.os,
                            "rmdir",
                            side_effect=fail_staging_rmdir,
                        )
                    with patcher:
                        with self.assertRaises(package.PackagingError):
                            package.build_distribution(
                                repository_root=fixture.root,
                                output_base=fixture.output_base,
                            )
                    self.assertTrue(injected)
                    self.assertTrue(fixture.destination.read_bytes().startswith(b"PK"))
                    self.assertEqual(
                        {path.name for path in fixture.output_base.iterdir()},
                        {package.ARCHIVE_FILENAME},
                    )
                finally:
                    fixture.close()

    def test_created_output_components_are_immediately_parent_synced(self) -> None:
        fixture = RepositoryFixture()
        self.addCleanup(fixture.close)
        original_mkdir = os.mkdir
        original_fsync = os.fsync
        events: list[tuple[str, str | int]] = []

        def record_mkdir(path, *args, **kwargs):
            result = original_mkdir(path, *args, **kwargs)
            events.append(("mkdir", str(path)))
            return result

        def record_fsync(descriptor):
            events.append(("fsync", descriptor))
            return original_fsync(descriptor)

        with (
            mock.patch.object(package.os, "mkdir", side_effect=record_mkdir),
            mock.patch.object(package.os, "fsync", side_effect=record_fsync),
        ):
            package.build_distribution(
                repository_root=fixture.root,
                output_base=fixture.output_base,
            )
        mkdir_indices = [index for index, event in enumerate(events) if event[0] == "mkdir"]
        self.assertEqual(len(mkdir_indices), 3)
        for index in mkdir_indices:
            self.assertLess(index + 1, len(events))
            self.assertEqual(events[index + 1][0], "fsync")

    def test_packager_never_uses_destination_replacing_rename(self) -> None:
        fixture = RepositoryFixture()
        self.addCleanup(fixture.close)
        original_link = os.link
        link_calls = 0

        def count_link(*args, **kwargs):
            nonlocal link_calls
            link_calls += 1
            return original_link(*args, **kwargs)

        with (
            mock.patch.object(package.os, "rename", side_effect=AssertionError("rename used")),
            mock.patch.object(package.os, "link", side_effect=count_link),
        ):
            distribution = package.build_distribution(
                repository_root=fixture.root,
                output_base=fixture.output_base,
            )
        self.assertTrue(distribution.archive_path.is_file())
        self.assertEqual(link_calls, 1)

    def test_cli_success_and_errors_do_not_echo_absolute_or_source_data(self) -> None:
        fixture = RepositoryFixture()
        self.addCleanup(fixture.close)
        shutil.copy2(ROOT / "fisher_extension_package.py", fixture.root)
        command = [sys.executable, "-m", "fisher_extension_package"]
        success = subprocess.run(
            command,
            cwd=fixture.root,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(success.returncode, 0, success.stderr)
        self.assertEqual(success.stderr, "")
        self.assertNotIn(str(fixture.root), success.stdout)
        self.assertRegex(
            success.stdout,
            rf"^archive=outputs/browser_extension/{re.escape(package.ARCHIVE_FILENAME)} "
            rf"members={len(RUNTIME_FILES)} bytes=\d+ sha256=[0-9a-f]{{64}}\n$",
        )
        self.assertEqual(
            {path.name for path in fixture.output_base.iterdir()},
            {package.ARCHIVE_FILENAME},
        )

        second = RepositoryFixture(reverse_order=True)
        self.addCleanup(second.close)
        shutil.copy2(ROOT / "fisher_extension_package.py", second.root)
        second_success = subprocess.run(
            command,
            cwd=second.root,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(second_success.returncode, 0, second_success.stderr)
        self.assertEqual(success.stdout, second_success.stdout)
        self.assertEqual(
            fixture.destination.read_bytes(),
            second.destination.read_bytes(),
        )

        failure = subprocess.run(
            [*command, "unexpected"],
            cwd=fixture.root,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(failure.returncode, 0)
        self.assertEqual(failure.stdout, "")
        self.assertNotIn(str(fixture.root), failure.stderr)
        self.assertNotIn("Fisher Scam Signal Prototype", failure.stderr)

        invalid = RepositoryFixture()
        self.addCleanup(invalid.close)
        shutil.copy2(ROOT / "fisher_extension_package.py", invalid.root)
        secret = "SOURCE-CONTENT-MUST-NOT-ECHO"
        (invalid.extension / "extra.js").write_text(secret, encoding="utf-8")
        invalid_result = subprocess.run(
            command,
            cwd=invalid.root,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(invalid_result.returncode, 0)
        self.assertEqual(invalid_result.stdout, "")
        self.assertNotIn(str(invalid.root), invalid_result.stderr)
        self.assertNotIn(secret, invalid_result.stderr)
        self.assertFalse(invalid.destination.exists())


if __name__ == "__main__":
    unittest.main()
