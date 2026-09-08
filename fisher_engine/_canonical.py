"""Canonical JSON and bounded-input helpers for the synthetic Fisher engine.

The engine's artifacts use schema-declared object order.  Consequently this
module deliberately preserves insertion order instead of sorting object keys.
Callers must construct dictionaries in the order declared by the relevant
schema and validators must check that order with :func:`exact_keys`.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import math
import re
import unicodedata
from typing import Any, BinaryIO, Sequence


class CanonicalError(ValueError):
    """A fail-closed error carrying one safe, controlled diagnostic code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


@dataclass(frozen=True)
class BoundedRead:
    """The observable result of a cap-plus-one byte read."""

    data: bytes
    exceeded: bool

    @property
    def observed_bytes(self) -> int | str:
        return f"GE_{len(self.data)}" if self.exceeded else len(self.data)


_JSON_NUMBER = re.compile(
    r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?"
)
_NONFINITE = ("-Infinity", "Infinity", "NaN")
MAX_JSON_NESTING = 64


def exact_keys(value: object, fields: Sequence[str]) -> bool:
    """Return whether *value* is a dict with exactly the declared key order."""

    return isinstance(value, dict) and tuple(value) == tuple(fields)


def _validate_json_value(value: Any) -> None:
    try:
        pending: list[tuple[Any, int]] = [(value, 0)]
        while pending:
            current, depth = pending.pop()
            if current is None or isinstance(current, bool) or isinstance(current, int):
                continue
            if isinstance(current, float):
                if not math.isfinite(current):
                    raise CanonicalError("canonical_nonfinite")
                continue
            if isinstance(current, str):
                if unicodedata.normalize("NFC", current) != current:
                    raise CanonicalError("canonical_non_nfc")
                continue
            if isinstance(current, (list, dict)):
                child_depth = depth + 1
                if child_depth > MAX_JSON_NESTING:
                    raise CanonicalError("canonical_nesting_too_deep")
                if isinstance(current, list):
                    pending.extend((item, child_depth) for item in reversed(current))
                else:
                    for key, item in reversed(tuple(current.items())):
                        if not isinstance(key, str):
                            raise CanonicalError("canonical_non_string_key")
                        if unicodedata.normalize("NFC", key) != key:
                            raise CanonicalError("canonical_non_nfc")
                        pending.append((item, child_depth))
                continue
            raise CanonicalError("canonical_unsupported_type")
    except (MemoryError, RecursionError) as error:
        raise CanonicalError("canonical_resource_limit") from error


def canonical_json_bytes(value: Any, *, max_bytes: int | None = None) -> bytes:
    """Serialize JSON using compact UTF-8 and schema-declared field order."""

    _validate_json_value(value)
    try:
        encoded = json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError, MemoryError, RecursionError) as error:
        raise CanonicalError("canonical_invalid_value") from error
    if max_bytes is not None and len(encoded) > max_bytes:
        raise CanonicalError("canonical_too_large")
    return encoded


def canonical_sha256(value: Any, *, max_bytes: int | None = None) -> str:
    return sha256(canonical_json_bytes(value, max_bytes=max_bytes)).hexdigest()


def read_cap_plus_one(source: bytes | bytearray | memoryview | BinaryIO, cap: int) -> BoundedRead:
    """Read no more than ``cap + 1`` bytes from bytes or a binary stream."""

    if isinstance(cap, bool) or not isinstance(cap, int) or cap < 0:
        raise ValueError("cap must be a nonnegative integer")
    limit = cap + 1
    try:
        if isinstance(source, (bytes, bytearray, memoryview)):
            data = bytes(source[:limit])
        else:
            data = source.read(limit)
            if not isinstance(data, bytes):
                raise TypeError("binary input required")
            data = data[:limit]
    except (MemoryError, RecursionError) as error:
        raise CanonicalError("bounded_read_resource_limit") from error
    return BoundedRead(data=data, exceeded=len(data) > cap)


class _ScanFailure(ValueError):
    pass


class _JsonEventScanner:
    """Small JSON scanner used to freeze duplicate/nonfinite precedence."""

    def __init__(self, text: str) -> None:
        self.text = text
        self.length = len(text)
        self.duplicates = False
        self.nonfinite = False

    def scan(self) -> None:
        index = self._skip_ws(0)
        index = self._value(index, 0)
        index = self._skip_ws(index)
        if index != self.length:
            raise _ScanFailure

    def _skip_ws(self, index: int) -> int:
        while index < self.length and self.text[index] in " \t\r\n":
            index += 1
        return index

    def _string(self, index: int) -> tuple[str, int]:
        if index >= self.length or self.text[index] != '"':
            raise _ScanFailure
        try:
            value, end = json.decoder.scanstring(self.text, index + 1, True)
        except (ValueError, json.JSONDecodeError) as error:
            raise _ScanFailure from error
        return value, end

    def _value(self, index: int, depth: int) -> int:
        index = self._skip_ws(index)
        if index >= self.length:
            raise _ScanFailure
        character = self.text[index]
        if character == "{":
            if depth >= MAX_JSON_NESTING:
                raise _ScanFailure
            return self._object(index, depth + 1)
        if character == "[":
            if depth >= MAX_JSON_NESTING:
                raise _ScanFailure
            return self._array(index, depth + 1)
        if character == '"':
            return self._string(index)[1]
        for literal in ("true", "false", "null"):
            if self.text.startswith(literal, index):
                return index + len(literal)
        for literal in _NONFINITE:
            if self.text.startswith(literal, index):
                self.nonfinite = True
                return index + len(literal)
        match = _JSON_NUMBER.match(self.text, index)
        if match is not None:
            return match.end()
        raise _ScanFailure

    def _object(self, index: int, depth: int) -> int:
        index = self._skip_ws(index + 1)
        if index < self.length and self.text[index] == "}":
            return index + 1
        keys: set[str] = set()
        while True:
            key, index = self._string(index)
            if key in keys:
                self.duplicates = True
            keys.add(key)
            index = self._skip_ws(index)
            if index >= self.length or self.text[index] != ":":
                raise _ScanFailure
            index = self._value(index + 1, depth)
            index = self._skip_ws(index)
            if index >= self.length:
                raise _ScanFailure
            if self.text[index] == "}":
                return index + 1
            if self.text[index] != ",":
                raise _ScanFailure
            index = self._skip_ws(index + 1)

    def _array(self, index: int, depth: int) -> int:
        index = self._skip_ws(index + 1)
        if index < self.length and self.text[index] == "]":
            return index + 1
        while True:
            index = self._value(index, depth)
            index = self._skip_ws(index)
            if index >= self.length:
                raise _ScanFailure
            if self.text[index] == "]":
                return index + 1
            if self.text[index] != ",":
                raise _ScanFailure
            index = self._skip_ws(index + 1)


def _all_strings_nfc(value: Any) -> bool:
    try:
        pending = [value]
        while pending:
            current = pending.pop()
            if isinstance(current, str):
                if unicodedata.normalize("NFC", current) != current:
                    return False
            elif isinstance(current, list):
                pending.extend(current)
            elif isinstance(current, dict):
                pending.extend(current.keys())
                pending.extend(current.values())
        return True
    except (MemoryError, RecursionError) as error:
        raise CanonicalError("canonical_resource_limit") from error


def strict_json_loads(raw: bytes, *, prefix: str) -> Any:
    """Parse canonical JSON and raise one controlled, precedence-ordered code.

    Size limits and schema checks belong to the caller.  The parser implements
    the shared BOM, UTF-8, duplicate, nonfinite, syntax, NFC, and canonical-byte
    boundary used by engine and metric preflight.
    """

    if raw.startswith(b"\xef\xbb\xbf"):
        raise CanonicalError(f"{prefix}_bom")
    try:
        decoded = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as error:
        raise CanonicalError(f"{prefix}_invalid_utf8") from error
    except (MemoryError, RecursionError) as error:
        raise CanonicalError(f"{prefix}_invalid_json") from error

    scanner = _JsonEventScanner(decoded)
    syntax_failed = False
    try:
        scanner.scan()
    except (_ScanFailure, MemoryError, RecursionError):
        syntax_failed = True
    if scanner.duplicates:
        raise CanonicalError(f"{prefix}_duplicate_key")
    if scanner.nonfinite:
        raise CanonicalError(f"{prefix}_nonfinite")
    if syntax_failed:
        raise CanonicalError(f"{prefix}_invalid_json")

    try:
        value = json.loads(decoded)
    except (json.JSONDecodeError, ValueError, MemoryError, RecursionError) as error:
        raise CanonicalError(f"{prefix}_invalid_json") from error
    try:
        if not _all_strings_nfc(value):
            raise CanonicalError(f"{prefix}_non_nfc")
    except CanonicalError as error:
        if error.code == f"{prefix}_non_nfc":
            raise
        raise CanonicalError(f"{prefix}_invalid_json") from error
    try:
        reencoded = canonical_json_bytes(value)
    except CanonicalError as error:
        raise CanonicalError(f"{prefix}_noncanonical_bytes") from error
    if reencoded != raw:
        raise CanonicalError(f"{prefix}_noncanonical_bytes")
    return value


def is_sha256(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def is_nonboolean_int(value: object, *, minimum: int | None = None, maximum: int | None = None) -> bool:
    if isinstance(value, bool) or not isinstance(value, int):
        return False
    if minimum is not None and value < minimum:
        return False
    if maximum is not None and value > maximum:
        return False
    return True


def safe_repo_path(value: object) -> bool:
    if not isinstance(value, str) or not value or "\\" in value or value.startswith("/") or value.endswith("/"):
        return False
    components = value.split("/")
    component_pattern = re.compile(r"[A-Za-z0-9_][A-Za-z0-9_.-]*\Z")
    return all(component not in {"", ".", ".."} and component_pattern.fullmatch(component) for component in components)


__all__ = [
    "BoundedRead",
    "CanonicalError",
    "MAX_JSON_NESTING",
    "canonical_json_bytes",
    "canonical_sha256",
    "exact_keys",
    "is_nonboolean_int",
    "is_sha256",
    "read_cap_plus_one",
    "safe_repo_path",
    "strict_json_loads",
]
