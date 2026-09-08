"""Deterministic source-manifest and executed-source-closure recording."""

from __future__ import annotations

from hashlib import sha256
from pathlib import Path
import sys
from threading import local, RLock
from typing import Iterable

from ._canonical import (
    CanonicalError,
    canonical_json_bytes,
    canonical_sha256,
    read_cap_plus_one,
    safe_repo_path,
)


COLLECTION_METHOD = "INSTRUMENTED_IMPORT_AND_EXECUTED_FILE_ACCESS_V1"
MAX_SOURCE_FILES = 4_096
MAX_DECLARED_ENTRYPOINTS = 64
MAX_SOURCE_FILE_BYTES = 4 * 1024 * 1024
_BOOTSTRAP_PATHS = (
    "fisher_engine/_canonical.py",
    "fisher_engine/source_closure.py",
)
_ACTIVE_RECORDERS: list["SourceClosureRecorder"] = []
_ACTIVE_LOCK = RLock()
_AUDIT_LOCAL = local()


def _utf8_key(value: str) -> bytes:
    return value.encode("utf-8")


def _resolve_project_file(project_root: Path, relative_path: str) -> Path:
    if not safe_repo_path(relative_path):
        raise CanonicalError("source_invalid_path")
    root = project_root.resolve()
    path = (root / relative_path).resolve()
    try:
        path.relative_to(root)
    except ValueError as error:
        raise CanonicalError("source_path_escape") from error
    if not path.is_file():
        raise CanonicalError("source_missing_file")
    return path


def _hash_project_file(project_root: Path, relative_path: str) -> dict[str, str]:
    path = _resolve_project_file(project_root, relative_path)
    with path.open("rb") as stream:
        bounded = read_cap_plus_one(stream, MAX_SOURCE_FILE_BYTES)
    if bounded.exceeded:
        raise CanonicalError("source_file_too_large")
    return {"path": relative_path, "sha256": sha256(bounded.data).hexdigest()}


def source_manifest(project_root: Path, relative_paths: Iterable[str]) -> dict:
    paths = sorted(set(relative_paths), key=_utf8_key)
    if not paths or len(paths) > MAX_SOURCE_FILES:
        raise CanonicalError("source_invalid_file_count")
    manifest = {
        "schema_version": "1.0.0",
        "files": [_hash_project_file(project_root, path) for path in paths],
    }
    canonical_json_bytes(manifest, max_bytes=4 * 1024 * 1024)
    return manifest


def source_manifest_sha256(project_root: Path, relative_paths: Iterable[str]) -> str:
    return canonical_sha256(
        source_manifest(project_root, relative_paths), max_bytes=4 * 1024 * 1024
    )


class SourceClosureRecorder:
    """Record declared entrypoints and project Python executed while active."""

    def __init__(
        self,
        project_root: Path,
        declared_entrypoints: Iterable[str],
    ) -> None:
        self.project_root = project_root.resolve()
        self.declared_entrypoints = sorted(set(declared_entrypoints), key=_utf8_key)
        if not 1 <= len(self.declared_entrypoints) <= MAX_DECLARED_ENTRYPOINTS:
            raise CanonicalError("source_invalid_entrypoint_count")
        for path in self.declared_entrypoints:
            _resolve_project_file(self.project_root, path)
        self._observed: set[str] = set(self.declared_entrypoints)
        for relative in _BOOTSTRAP_PATHS:
            _resolve_project_file(self.project_root, relative)
            self._observed.add(relative)
        self._active = False
        self._audit_failure = False

    def __enter__(self) -> "SourceClosureRecorder":
        with _ACTIVE_LOCK:
            if self._active:
                raise CanonicalError("source_recorder_already_active")
            self._active = True
            _ACTIVE_RECORDERS.append(self)
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        del exc_type, exc, traceback
        with _ACTIVE_LOCK:
            if not self._active:
                raise CanonicalError("source_recorder_not_active")
            self._active = False
            _ACTIVE_RECORDERS.remove(self)

    def _observe_audit_path(self, candidate: object, *, require_file: bool) -> None:
        if isinstance(candidate, bytes):
            try:
                candidate = candidate.decode(sys.getfilesystemencoding(), errors="strict")
            except UnicodeError:
                return
        if not isinstance(candidate, str) or not candidate or candidate.startswith("<"):
            return
        path = Path(candidate)
        if path.suffix != ".py":
            return
        try:
            resolved = path.resolve()
            relative = resolved.relative_to(self.project_root).as_posix()
        except (OSError, RuntimeError, ValueError):
            return
        if not safe_repo_path(relative):
            return
        if resolved.is_file():
            self._observed.add(relative)
        elif require_file:
            self._audit_failure = True

    def record_executed_file(self, path: str | Path) -> None:
        candidate = Path(path)
        if candidate.is_absolute():
            resolved = candidate.resolve()
            try:
                relative = resolved.relative_to(self.project_root).as_posix()
            except ValueError as error:
                raise CanonicalError("source_path_escape") from error
        else:
            relative = candidate.as_posix()
        _resolve_project_file(self.project_root, relative)
        with _ACTIVE_LOCK:
            self._observed.add(relative)

    def finalize(self) -> dict:
        with _ACTIVE_LOCK:
            if self._active:
                raise CanonicalError("source_recorder_still_active")
            if self._audit_failure:
                raise CanonicalError("source_instrumentation_failed")
            paths = sorted(self._observed, key=_utf8_key)
        if not paths or len(paths) > MAX_SOURCE_FILES:
            raise CanonicalError("source_invalid_file_count")
        files = [_hash_project_file(self.project_root, path) for path in paths]
        unhashed = {
            "closure_version": "1.0.0",
            "collection_method": COLLECTION_METHOD,
            "declared_entrypoints": self.declared_entrypoints,
            "files": files,
        }
        return {**unhashed, "closure_sha256": canonical_sha256(unhashed)}


def _audit_hook(event: str, args: tuple[object, ...]) -> None:
    if getattr(_AUDIT_LOCAL, "busy", False):
        return
    with _ACTIVE_LOCK:
        if not _ACTIVE_RECORDERS:
            return
    candidate: object | None = None
    if event == "open" and args:
        candidate = args[0]
    elif event == "compile" and len(args) >= 2:
        candidate = args[1]
    elif event == "exec" and args:
        candidate = getattr(args[0], "co_filename", None)
    elif event == "import" and len(args) >= 2:
        candidate = args[1]
    if candidate is None:
        return
    _AUDIT_LOCAL.busy = True
    try:
        with _ACTIVE_LOCK:
            for recorder in _ACTIVE_RECORDERS:
                try:
                    recorder._observe_audit_path(
                        candidate, require_file=event in {"compile", "exec", "import"}
                    )
                except (MemoryError, RecursionError):
                    recorder._audit_failure = True
    finally:
        _AUDIT_LOCAL.busy = False


sys.addaudithook(_audit_hook)


def validate_source_closure(value: object) -> None:
    from ._canonical import exact_keys, is_sha256

    fields = (
        "closure_version",
        "collection_method",
        "declared_entrypoints",
        "files",
        "closure_sha256",
    )
    if not exact_keys(value, fields):
        raise CanonicalError("source_invalid_closure_schema")
    assert isinstance(value, dict)
    if value["closure_version"] != "1.0.0" or value["collection_method"] != COLLECTION_METHOD:
        raise CanonicalError("source_invalid_closure_schema")
    entrypoints = value["declared_entrypoints"]
    files = value["files"]
    if not isinstance(entrypoints, list) or not 1 <= len(entrypoints) <= MAX_DECLARED_ENTRYPOINTS:
        raise CanonicalError("source_invalid_entrypoint_count")
    if entrypoints != sorted(set(entrypoints), key=_utf8_key) or not all(safe_repo_path(path) for path in entrypoints):
        raise CanonicalError("source_invalid_entrypoints")
    if not isinstance(files, list) or not 1 <= len(files) <= MAX_SOURCE_FILES:
        raise CanonicalError("source_invalid_file_count")
    paths: list[str] = []
    for row in files:
        if not exact_keys(row, ("path", "sha256")) or not safe_repo_path(row["path"]) or not is_sha256(row["sha256"]):
            raise CanonicalError("source_invalid_file")
        paths.append(row["path"])
    if (
        paths != sorted(set(paths), key=_utf8_key)
        or not set(entrypoints).issubset(paths)
        or not set(_BOOTSTRAP_PATHS).issubset(paths)
    ):
        raise CanonicalError("source_invalid_files")
    unhashed = {field: value[field] for field in fields[:-1]}
    if not is_sha256(value["closure_sha256"]) or canonical_sha256(unhashed) != value["closure_sha256"]:
        raise CanonicalError("source_closure_hash_mismatch")


def verify_source_closure_files(value: object, project_root: Path) -> None:
    """Validate the closure and bind every row to the current exact file bytes."""

    validate_source_closure(value)
    assert isinstance(value, dict)
    for row in value["files"]:
        observed = _hash_project_file(project_root, row["path"])
        if observed != row:
            raise CanonicalError("source_closure_file_hash_mismatch")


__all__ = [
    "COLLECTION_METHOD",
    "SourceClosureRecorder",
    "source_manifest",
    "source_manifest_sha256",
    "validate_source_closure",
    "verify_source_closure_files",
]
