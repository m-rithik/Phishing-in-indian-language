from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from io import BytesIO
import json
import os
from pathlib import Path
import secrets
import stat
import sys
import zipfile

DISTRIBUTION_NAME = "fisher-scam-signal-prototype-v0.5.0"
ARCHIVE_FILENAME = f"{DISTRIBUTION_NAME}.zip"
OUTPUT_RELATIVE = Path("outputs/browser_extension")
SOURCE_FILES = (
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
    "tests/selection.test.mjs",
)
RUNTIME_FILES = (
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
)
ROOT_ENTRIES = frozenset({name for name in SOURCE_FILES if "/" not in name} | {"tests"})
EXPECTED_CSP = (
    "default-src 'none'; script-src 'self'; style-src 'self'; connect-src 'none'; "
    "object-src 'none'; base-uri 'none'; form-action 'none'"
)
EXPECTED_MANIFEST = {
    "manifest_version": 3,
    "name": "Fisher Scam Signal Prototype",
    "version": "0.5.0",
    "description": "Locally checks pasted messages, links, and explicitly selected text for scam signals.",
    "permissions": ["activeTab", "scripting"],
    "icons": {
        "16": "icon-16.png",
        "32": "icon-32.png",
        "48": "icon-48.png",
        "128": "icon-128.png",
    },
    "action": {
        "default_title": "Analyze text with Fisher",
        "default_popup": "popup.html",
        "default_icon": {
            "16": "icon-16.png",
            "32": "icon-32.png",
        },
    },
    "content_security_policy": {"extension_pages": EXPECTED_CSP},
}
MAX_MEMBER_BYTES = 1024 * 1024
MAX_TOTAL_BYTES = 5 * 1024 * 1024
UNSAFE_FILE_MODE = (
    stat.S_IXUSR
    | stat.S_IXGRP
    | stat.S_IXOTH
    | stat.S_ISUID
    | stat.S_ISGID
    | stat.S_IWGRP
    | stat.S_IWOTH
)
UNSAFE_DIRECTORY_MODE = stat.S_IWGRP | stat.S_IWOTH
DIRECTORY_FLAGS = (
    os.O_RDONLY
    | getattr(os, "O_DIRECTORY", 0)
    | getattr(os, "O_NOFOLLOW", 0)
    | getattr(os, "O_CLOEXEC", 0)
)
READ_FLAGS = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0)


class PackagingError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class Distribution:
    archive_path: Path
    member_count: int
    byte_count: int
    sha256: str


@dataclass(frozen=True, slots=True)
class _CapturedSource:
    data: bytes
    signature: tuple[int, ...]


def _signature(metadata: os.stat_result) -> tuple[int, ...]:
    return (
        metadata.st_dev,
        metadata.st_ino,
        metadata.st_mode,
        metadata.st_nlink,
        metadata.st_size,
        metadata.st_mtime_ns,
        metadata.st_ctime_ns,
    )


def _safe_directory(metadata: os.stat_result, message: str) -> None:
    if not stat.S_ISDIR(metadata.st_mode) or metadata.st_mode & UNSAFE_DIRECTORY_MODE:
        raise PackagingError(message)


def _open_directory(
    path: str | Path,
    *,
    message: str,
    dir_fd: int | None = None,
) -> int:
    descriptor = None
    try:
        descriptor = os.open(path, DIRECTORY_FLAGS, dir_fd=dir_fd)
        _safe_directory(os.fstat(descriptor), message)
        return descriptor
    except PackagingError:
        if descriptor is not None:
            os.close(descriptor)
        raise
    except OSError:
        if descriptor is not None:
            os.close(descriptor)
        raise PackagingError(message) from None


def _bind_directory(
    descriptor: int,
    message: str,
    *,
    path: Path | None = None,
    parent_fd: int | None = None,
    name: str | None = None,
) -> None:
    try:
        opened = os.fstat(descriptor)
        _safe_directory(opened, message)
        named = path.lstat() if path is not None else os.stat(
            name, dir_fd=parent_fd, follow_symlinks=False
        )
    except OSError:
        raise PackagingError(message) from None
    unsafe = (
        stat.S_ISLNK(named.st_mode)
        or not stat.S_ISDIR(named.st_mode)
        or named.st_mode & UNSAFE_DIRECTORY_MODE
        or (named.st_dev, named.st_ino) != (opened.st_dev, opened.st_ino)
    )
    if unsafe:
        raise PackagingError(message)


def _entries(descriptor: int) -> dict[str, os.stat_result]:
    try:
        with os.scandir(descriptor) as entries:
            return {entry.name: entry.stat(follow_symlinks=False) for entry in entries}
    except OSError:
        raise PackagingError("Extension source inventory is invalid.") from None


def _inventory(
    source_fd: int,
    tests_fd: int,
) -> tuple[tuple[int, ...], tuple[int, ...]]:
    source_meta, tests_meta = (
        os.fstat(source_fd),
        os.fstat(tests_fd),
    )
    message = "Extension source inventory is invalid."
    _safe_directory(source_meta, message)
    _safe_directory(tests_meta, message)
    root, tests = (
        _entries(source_fd),
        _entries(tests_fd),
    )
    if set(root) != ROOT_ENTRIES or set(tests) != {
        "analyzer.test.mjs",
        "detector.test.mjs",
        "selection.test.mjs",
    }:
        raise PackagingError(message)
    test_dir = root["tests"]
    unsafe_test_dir = (
        stat.S_ISLNK(test_dir.st_mode)
        or not stat.S_ISDIR(test_dir.st_mode)
        or test_dir.st_mode & UNSAFE_DIRECTORY_MODE
        or (test_dir.st_dev, test_dir.st_ino) != (tests_meta.st_dev, tests_meta.st_ino)
    )
    file_meta = [value for key, value in root.items() if key != "tests"] + list(
        tests.values()
    )
    if unsafe_test_dir or any(not stat.S_ISREG(item.st_mode) for item in file_meta):
        raise PackagingError(message)
    return _signature(source_meta), _signature(tests_meta)


def _safe_source(metadata: os.stat_result) -> None:
    if (
        not stat.S_ISREG(metadata.st_mode)
        or metadata.st_nlink != 1
        or metadata.st_mode & UNSAFE_FILE_MODE
    ):
        raise PackagingError("Extension source file mode is unsafe.")
    if metadata.st_size < 0 or metadata.st_size > MAX_MEMBER_BYTES:
        raise PackagingError("Extension source size limit exceeded.")


def _read_all(descriptor: int, maximum: int, message: str) -> bytes:
    chunks, total = (
        [],
        0,
    )
    try:
        os.lseek(descriptor, 0, os.SEEK_SET)
        while True:
            chunk = os.read(descriptor, min(64 * 1024, maximum + 1 - total))
            if not chunk:
                return b"".join(chunks)
            chunks.append(chunk)
            total += len(chunk)
            if total > maximum:
                raise PackagingError(message)
    except OSError:
        raise PackagingError(message) from None


def _source_slot(relative: str, source_fd: int, tests_fd: int) -> tuple[int, str]:
    return (
        (tests_fd, relative.removeprefix("tests/"))
        if relative.startswith("tests/")
        else (source_fd, relative)
    )


def _capture_file(directory_fd: int, name: str) -> _CapturedSource:
    descriptor = None
    try:
        named = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
        _safe_source(named)
        descriptor = os.open(name, READ_FLAGS, dir_fd=directory_fd)
        before = os.fstat(descriptor)
        _safe_source(before)
        if _signature(named) != _signature(before):
            raise PackagingError("Extension source changed during capture.")
        data = _read_all(
            descriptor,
            MAX_MEMBER_BYTES,
            "Extension source size limit exceeded.",
        )
        if (
            _signature(before) != _signature(os.fstat(descriptor))
            or len(data) != before.st_size
        ):
            raise PackagingError("Extension source changed during capture.")
        return _CapturedSource(data, _signature(before))
    except OSError:
        raise PackagingError("Extension source could not be opened safely.") from None
    finally:
        if descriptor is not None:
            os.close(descriptor)


def _capture_sources(
    source_fd: int,
    tests_fd: int,
) -> tuple[dict[str, _CapturedSource], tuple[tuple[int, ...], tuple[int, ...]]]:
    directory_signatures = _inventory(source_fd, tests_fd)
    captured, total = (
        {},
        0,
    )
    for relative in SOURCE_FILES:
        captured[relative] = _capture_file(*_source_slot(relative, source_fd, tests_fd))
        total += len(captured[relative].data)
        if total > MAX_TOTAL_BYTES:
            raise PackagingError("Extension source total size limit exceeded.")
    return captured, directory_signatures


def _recheck_sources(
    root_fd: int,
    source_fd: int,
    tests_fd: int,
    captured: dict[str, _CapturedSource],
    directory_signatures: tuple[tuple[int, ...], tuple[int, ...]],
) -> None:
    message = "Extension source changed before publication."
    _bind_directory(source_fd, message, parent_fd=root_fd, name="browser_extension")
    _bind_directory(tests_fd, message, parent_fd=source_fd, name="tests")
    if _inventory(source_fd, tests_fd) != directory_signatures:
        raise PackagingError(message)
    for relative, source in captured.items():
        directory_fd, name = _source_slot(relative, source_fd, tests_fd)
        try:
            metadata = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
            _safe_source(metadata)
        except OSError:
            raise PackagingError(message) from None
        if _signature(metadata) != source.signature:
            raise PackagingError(message)


def _unique_keys(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result = {}
    for key, value in pairs:
        if key in result:
            raise PackagingError("Extension manifest is invalid.")
        result[key] = value
    return result


def _validate_manifest(data: bytes) -> None:
    def reject_constant(_value: str) -> None:
        raise PackagingError("Extension manifest is invalid.")

    try:
        manifest = json.loads(
            data.decode("utf-8"),
            object_pairs_hook=_unique_keys,
            parse_constant=reject_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError, PackagingError):
        raise PackagingError("Extension manifest is invalid.") from None
    invalid = (
        type(manifest) is not dict
        or type(manifest.get("manifest_version")) is not int
        or manifest != EXPECTED_MANIFEST
    )
    if invalid:
        raise PackagingError("Extension manifest contract is invalid.")


def _build_archive_bytes(captured: dict[str, _CapturedSource]) -> bytes:
    output = BytesIO()
    with zipfile.ZipFile(
        output,
        "w",
        compression=zipfile.ZIP_STORED,
        allowZip64=False,
    ) as archive:
        for relative in sorted(RUNTIME_FILES):
            info = zipfile.ZipInfo(relative, date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type, info.create_system = zipfile.ZIP_STORED, 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            info.extra = info.comment = b""
            archive.writestr(info, captured[relative].data)
    return output.getvalue()


def _validate_distribution_bytes(
    candidate: bytes,
    expected: bytes,
    captured: dict[str, _CapturedSource],
) -> None:
    message = "Extension archive validation failed."
    if candidate != expected:
        raise PackagingError(message)
    try:
        with zipfile.ZipFile(BytesIO(candidate)) as archive:
            infos = archive.infolist()
            if archive.comment or [item.filename for item in infos] != sorted(
                RUNTIME_FILES
            ):
                raise PackagingError(message)
            if archive.testzip() is not None:
                raise PackagingError(message)
            for item in infos:
                invalid = (
                    item.date_time != (1980, 1, 1, 0, 0, 0)
                    or item.compress_type != zipfile.ZIP_STORED
                    or item.create_system != 3
                    or item.external_attr >> 16 != stat.S_IFREG | 0o644
                    or item.extra
                    or item.comment
                    or archive.read(item) != captured[item.filename].data
                )
                if invalid:
                    raise PackagingError(message)
    except (OSError, KeyError, RuntimeError, zipfile.BadZipFile):
        raise PackagingError(message) from None


def _close_output_chain(
    chain: list[tuple[int, str, int, bool]],
    *,
    remove_created: bool,
) -> None:
    for parent, name, child, created in reversed(chain):
        os.close(child)
        if remove_created and created:
            try:
                os.rmdir(name, dir_fd=parent)
                os.fsync(parent)
            except OSError:
                pass
    if chain:
        os.close(chain[0][0])


def _open_output_chain(root_fd: int) -> tuple[int, list[tuple[int, str, int, bool]]]:
    current, chain = (
        os.dup(root_fd),
        [],
    )
    try:
        for name in OUTPUT_RELATIVE.parts:
            created = False
            try:
                child = _open_directory(
                    name,
                    dir_fd=current,
                    message="Extension output is unsafe.",
                )
            except PackagingError:
                try:
                    os.stat(name, dir_fd=current, follow_symlinks=False)
                except FileNotFoundError:
                    try:
                        os.mkdir(name, 0o755, dir_fd=current)
                        created = True
                        os.fsync(current)
                        child = _open_directory(
                            name, dir_fd=current, message="Extension output is unsafe."
                        )
                    except (OSError, PackagingError):
                        if created:
                            try:
                                os.rmdir(name, dir_fd=current)
                                os.fsync(current)
                            except OSError:
                                pass
                        raise PackagingError(
                            "Extension output is unavailable."
                        ) from None
                except OSError:
                    raise PackagingError("Extension output is unsafe.") from None
                else:
                    raise
            chain.append((current, name, child, created))
            current = child
        return current, chain
    except Exception:
        _close_output_chain(chain, remove_created=True)
        if not chain:
            os.close(current)
        raise


def _check_output(
    path: Path,
    output_fd: int,
    chain: list[tuple[int, str, int, bool]],
) -> None:
    message = "Extension output changed during packaging."
    _safe_directory(os.fstat(chain[0][0]), message)
    for _parent, _name, child, _created in chain:
        _safe_directory(os.fstat(child), message)
    _bind_directory(output_fd, message, path=path)


def _create_staging(output_fd: int) -> tuple[str, int]:
    for _ in range(20):
        name = f".fisher-extension-{secrets.token_hex(8)}"
        try:
            os.mkdir(name, 0o700, dir_fd=output_fd)
            os.fsync(output_fd)
            descriptor = _open_directory(
                name,
                dir_fd=output_fd,
                message="Extension staging failed.",
            )
            if stat.S_IMODE(os.fstat(descriptor).st_mode) != 0o700:
                os.close(descriptor)
                raise PackagingError("Extension staging failed.")
            return name, descriptor
        except FileExistsError:
            continue
        except (OSError, PackagingError):
            try:
                os.rmdir(name, dir_fd=output_fd)
                os.fsync(output_fd)
            except OSError:
                pass
            raise PackagingError("Extension staging failed.") from None
    raise PackagingError("Extension staging failed.")


def _write_staged(staging_fd: int, data: bytes) -> int:
    descriptor = None
    flags = os.O_RDWR | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        descriptor = os.open(ARCHIVE_FILENAME, flags, 0o600, dir_fd=staging_fd)
        offset = 0
        while offset < len(data):
            written = os.write(descriptor, data[offset:])
            if written <= 0:
                raise PackagingError("Extension staging failed.")
            offset += written
        os.fchmod(descriptor, 0o644)
        os.fsync(descriptor)
        metadata = os.fstat(descriptor)
        valid = (
            stat.S_ISREG(metadata.st_mode)
            and stat.S_IMODE(metadata.st_mode) == 0o644
            and metadata.st_nlink == 1
            and metadata.st_size == len(data)
        )
        if not valid:
            raise PackagingError("Extension staging failed.")
        return descriptor
    except PackagingError:
        if descriptor is not None:
            os.close(descriptor)
        raise
    except OSError:
        if descriptor is not None:
            os.close(descriptor)
        raise PackagingError("Extension staging failed.") from None


def _check_archive(
    directory_fd: int,
    archive_bytes: bytes,
    captured: dict[str, _CapturedSource],
    identity: tuple[int, int],
    links: int,
) -> None:
    descriptor = None
    message = "Extension archive validation failed."
    try:
        descriptor = os.open(ARCHIVE_FILENAME, READ_FLAGS, dir_fd=directory_fd)
        before = os.fstat(descriptor)
        valid = (
            stat.S_ISREG(before.st_mode)
            and stat.S_IMODE(before.st_mode) == 0o644
            and (before.st_dev, before.st_ino) == identity
            and before.st_nlink == links
            and before.st_size == len(archive_bytes)
        )
        if not valid:
            raise PackagingError(message)
        candidate = _read_all(descriptor, len(archive_bytes), message)
        if _signature(before) != _signature(os.fstat(descriptor)):
            raise PackagingError(message)
        _validate_distribution_bytes(candidate, archive_bytes, captured)
    except OSError:
        raise PackagingError(message) from None
    finally:
        if descriptor is not None:
            os.close(descriptor)


def _build_distribution(*, repository_root: Path, output_base: Path) -> Distribution:
    root = Path(os.path.abspath(repository_root))
    output = Path(
        os.path.abspath(
            output_base if output_base.is_absolute() else root / output_base
        )
    )
    if output != root / OUTPUT_RELATIVE:
        raise PackagingError("Extension output location is invalid.")
    root_fd = _open_directory(root, message="Repository root is invalid.")
    source_fd = tests_fd = output_fd = staging_fd = staged_fd = None
    chain: list[tuple[int, str, int, bool]] = []
    staging_name = None
    stage_present = staged_present = final_linked = success = False
    failure = None
    archive_bytes = b""
    try:
        _bind_directory(root_fd, "Repository root is invalid.", path=root)
        source_fd = _open_directory(
            "browser_extension",
            dir_fd=root_fd,
            message="Extension source inventory is invalid.",
        )
        tests_fd = _open_directory(
            "tests",
            dir_fd=source_fd,
            message="Extension source inventory is invalid.",
        )
        captured, directory_signatures = _capture_sources(source_fd, tests_fd)
        _validate_manifest(captured["manifest.json"].data)
        archive_bytes = _build_archive_bytes(captured)
        output_fd, chain = _open_output_chain(root_fd)
        _check_output(output, output_fd, chain)
        staging_name, staging_fd = _create_staging(output_fd)
        stage_present = staged_present = True
        staged_fd = _write_staged(staging_fd, archive_bytes)
        staged_meta = os.fstat(staged_fd)
        identity = staged_meta.st_dev, staged_meta.st_ino
        _check_archive(staging_fd, archive_bytes, captured, identity, 1)
        os.fsync(staging_fd)
        _recheck_sources(root_fd, source_fd, tests_fd, captured, directory_signatures)
        _bind_directory(root_fd, "Repository root changed during packaging.", path=root)
        _check_output(output, output_fd, chain)
        _check_archive(staging_fd, archive_bytes, captured, identity, 1)
        try:
            os.link(
                ARCHIVE_FILENAME,
                ARCHIVE_FILENAME,
                src_dir_fd=staging_fd,
                dst_dir_fd=output_fd,
                follow_symlinks=False,
            )
            final_linked = True
        except FileExistsError:
            raise PackagingError(
                "Extension distribution destination already exists."
            ) from None
        except OSError:
            raise PackagingError("Extension distribution publication failed.") from None
        os.fsync(output_fd)
        _check_output(output, output_fd, chain)
        if os.fstat(staged_fd).st_nlink != 2:
            raise PackagingError(
                "Extension distribution publication validation failed."
            )
        _check_archive(output_fd, archive_bytes, captured, identity, 2)
        _check_archive(staging_fd, archive_bytes, captured, identity, 2)
        try:
            os.unlink(ARCHIVE_FILENAME, dir_fd=staging_fd)
            staged_present = False
            if os.fstat(staged_fd).st_nlink != 1:
                raise PackagingError("Extension staging cleanup failed.")
            os.fsync(staging_fd)
            _bind_directory(
                staging_fd,
                "Extension staging cleanup failed.",
                parent_fd=output_fd,
                name=staging_name,
            )
            os.close(staged_fd)
            staged_fd = None
            os.close(staging_fd)
            staging_fd = None
            os.rmdir(staging_name, dir_fd=output_fd)
            stage_present = False
            os.fsync(output_fd)
        except PackagingError:
            raise
        except OSError:
            raise PackagingError("Extension staging cleanup failed.") from None
        _check_archive(output_fd, archive_bytes, captured, identity, 1)
        _check_output(output, output_fd, chain)
        success = True
    except Exception as error:
        failure = error
    finally:
        if final_linked and not success:
            failure = PackagingError(
                "Extension post-publication failure; archive preserved."
            )
        if staged_present and staging_fd is not None:
            try:
                os.unlink(ARCHIVE_FILENAME, dir_fd=staging_fd)
            except OSError:
                failure = failure or PackagingError("Extension staging cleanup failed.")
        if staged_fd is not None:
            os.close(staged_fd)
        if staging_fd is not None:
            os.close(staging_fd)
        if stage_present and staging_name is not None and output_fd is not None:
            try:
                os.rmdir(staging_name, dir_fd=output_fd)
                os.fsync(output_fd)
            except OSError:
                failure = failure or PackagingError("Extension staging cleanup failed.")
        _close_output_chain(chain, remove_created=not success)
        if tests_fd is not None:
            os.close(tests_fd)
        if source_fd is not None:
            os.close(source_fd)
        os.close(root_fd)
    if failure is not None:
        if isinstance(failure, PackagingError):
            raise failure
        raise PackagingError("Extension packaging failed.") from None
    return Distribution(
        output / ARCHIVE_FILENAME,
        len(RUNTIME_FILES),
        len(archive_bytes),
        sha256(archive_bytes).hexdigest(),
    )


def build_distribution(*, repository_root: Path, output_base: Path) -> Distribution:
    """Build the deterministic, runtime-only extension distribution."""
    try:
        return _build_distribution(
            repository_root=Path(repository_root),
            output_base=Path(output_base),
        )
    except PackagingError:
        raise
    except Exception:
        raise PackagingError("Extension packaging failed.") from None


def main(arguments: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if arguments is None else arguments
    if arguments:
        print("error: this command takes no arguments", file=sys.stderr)
        return 2
    root = Path(__file__).resolve().parent
    try:
        distribution = build_distribution(
            repository_root=root,
            output_base=root / OUTPUT_RELATIVE,
        )
    except PackagingError as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    relative = distribution.archive_path.relative_to(root).as_posix()
    print(
        f"archive={relative} members={distribution.member_count} "
        f"bytes={distribution.byte_count} sha256={distribution.sha256}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
