from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from hashlib import sha256
import json
from pathlib import Path
import re
import stat
from typing import Any, Iterable
import unicodedata

from fisher_baselines.data import (
    normalize_duplicate_key,
    scan_live_artifacts,
    scan_residual_candidates,
    template_group_id,
)


SCHEMA_VERSION = "0.1.0"
LANGUAGE_STRATA = ("hindi", "tamil", "telugu", "english_indic_code_mixed")
FINAL_LABELS = ("benign", "phishing")
ANNOTATION_LABELS = (*FINAL_LABELS, "uncertain")
ANNOTATION_STRATA = (*LANGUAGE_STRATA, "uncertain")
MODES = ("draft", "ready")
PILOT_CELLS = tuple(
    (stratum, label) for stratum in LANGUAGE_STRATA for label in FINAL_LABELS
)
MAX_FILE_BYTES = 8 * 1024 * 1024
MAX_LINE_BYTES = 64 * 1024
MAX_ROWS = {"source": 2_000, "item": 1_000, "annotation": 5_000}
MAX_TEXT_CHARACTERS = 4_000
ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,63}\Z")
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
OTP_RE = re.compile(
    r"(?i)\b(?:otp|one[ -]?time(?: password| code)?|pin|passcode|cvv)\b"
    r"[\s\S]{0,24}?(?<!\d)(?:\d[\s-]*){3,8}(?!\d)"
)
ACCOUNT_RE = re.compile(
    r"(?i)\b(?:account|a/c|acct|card|debit|credit)\b"
    r"[\s\S]{0,32}?(?<!\d)(?:\d[\s-]*){6,32}(?!\d)"
)
LONG_NUMBER_RE = re.compile(r"(?<!\d)(?:\d[\s-]*){12,32}(?!\d)")
SECRET_RE = re.compile(
    r"(?i)\b(?:password|passwd|secret|credential|api[ _-]?key|token)\b"
    r"\s*(?:is|:|=)\s*"
    r"(?!\[(?:PASSWORD|SECRET|TOKEN)\])\S+"
)
TYPED_PLACEHOLDER_RE = re.compile(
    r"\[(?:URL|DOMAIN|EMAIL|PHONE|UPI|IPV4|IPV6)\]"
)
BIDI_CONTROL_CODEPOINTS = frozenset(
    {0x061C, 0x200E, 0x200F, *range(0x202A, 0x202F), *range(0x2066, 0x206A)}
)
DEFAULT_IGNORABLE_RANGES = (
    (0x00AD, 0x00AD),
    (0x034F, 0x034F),
    (0x061C, 0x061C),
    (0x115F, 0x1160),
    (0x17B4, 0x17B5),
    (0x180B, 0x180F),
    (0x200B, 0x200F),
    (0x202A, 0x202E),
    (0x2060, 0x206F),
    (0x3164, 0x3164),
    (0xFE00, 0xFE0F),
    (0xFEFF, 0xFEFF),
    (0xFFA0, 0xFFA0),
    (0xFFF0, 0xFFF8),
    (0x1BCA0, 0x1BCA3),
    (0x1D173, 0x1D17A),
    (0xE0000, 0xE0FFF),
)

SOURCE_KEYS = frozenset(
    {
        "schema_version",
        "source_id",
        "provenance_class",
        "consent_status",
        "consent_reference",
        "collection_batch_id",
        "internal_research_permitted",
        "release_tier",
        "source_status",
    }
)
ITEM_KEYS = frozenset(
    {
        "schema_version",
        "item_id",
        "source_id",
        "text",
        "content_sha256",
        "language_stratum",
        "final_label",
        "label_resolution",
        "leakage_component_id",
        "romanized_indic",
        "romanization_ambiguous",
        "artifact_review",
        "privacy_review",
        "partition",
    }
)
ANNOTATION_KEYS = frozenset(
    {
        "schema_version",
        "annotation_id",
        "item_id",
        "annotator_id",
        "kind",
        "primary_label",
        "language_stratum",
        "confidence",
    }
)


@dataclass(frozen=True, order=True)
class Diagnostic:
    severity: str
    code: str
    record_kind: str
    line: int | None = None
    field: str | None = None

    def as_dict(self) -> dict[str, object]:
        result: dict[str, object] = {
            "severity": self.severity,
            "code": self.code,
            "record_kind": self.record_kind,
        }
        if self.line is not None:
            result["line"] = self.line
        if self.field is not None:
            result["field"] = self.field
        return result


@dataclass(frozen=True)
class ValidationResult:
    mode: str
    report: dict[str, object]
    diagnostics: tuple[Diagnostic, ...]

    @property
    def valid(self) -> bool:
        return not any(diagnostic.severity == "error" for diagnostic in self.diagnostics)


class _StrictJsonError(ValueError):
    pass


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _StrictJsonError("duplicate key")
        result[key] = value
    return result


def _reject_number(_: str) -> None:
    raise _StrictJsonError("numbers are not allowed")


def _diagnostic(
    diagnostics: list[Diagnostic],
    code: str,
    kind: str,
    line: int | None = None,
    field: str | None = None,
    *,
    severity: str = "error",
) -> None:
    diagnostics.append(Diagnostic(severity, code, kind, line, field))


def _load_jsonl(
    path: str | Path,
    kind: str,
    exact_keys: frozenset[str],
    diagnostics: list[Diagnostic],
) -> list[tuple[int, dict[str, Any]]]:
    path = Path(path)
    try:
        metadata = path.lstat()
        if not stat.S_ISREG(metadata.st_mode):
            _diagnostic(diagnostics, "file_not_regular", kind)
            return []
        if metadata.st_size <= 0 or metadata.st_size > MAX_FILE_BYTES:
            _diagnostic(diagnostics, "file_bound", kind)
            return []
        raw = path.read_bytes()
    except OSError:
        _diagnostic(diagnostics, "file_unreadable_or_not_utf8", kind)
        return []
    if len(raw) <= 0 or len(raw) > MAX_FILE_BYTES:
        _diagnostic(diagnostics, "file_bound", kind)
        return []

    physical_lines = raw.split(b"\n")
    if physical_lines and physical_lines[-1] == b"":
        physical_lines.pop()
    if len(physical_lines) > MAX_ROWS[kind]:
        _diagnostic(diagnostics, "row_bound", kind)
        return []

    rows: list[tuple[int, dict[str, Any]]] = []
    for line_number, physical_line in enumerate(physical_lines, start=1):
        if len(physical_line) > MAX_LINE_BYTES:
            _diagnostic(diagnostics, "line_bound", kind, line_number)
            continue
        if physical_line.endswith(b"\r"):
            physical_line = physical_line[:-1]
        try:
            raw_line = physical_line.decode("utf-8", errors="strict")
        except UnicodeDecodeError:
            _diagnostic(diagnostics, "file_unreadable_or_not_utf8", kind, line_number)
            continue
        if not raw_line.strip():
            _diagnostic(diagnostics, "blank_line", kind, line_number)
            continue
        try:
            value = json.loads(
                raw_line,
                object_pairs_hook=_strict_object,
                parse_int=_reject_number,
                parse_float=_reject_number,
                parse_constant=_reject_number,
            )
        except (ValueError, OverflowError, RecursionError):
            _diagnostic(diagnostics, "invalid_json", kind, line_number)
            continue
        if not isinstance(value, dict):
            _diagnostic(diagnostics, "row_not_object", kind, line_number)
            continue
        if frozenset(value) != exact_keys:
            _diagnostic(diagnostics, "schema_keys", kind, line_number)
            continue
        rows.append((line_number, value))
    return rows


def _is_id(value: Any) -> bool:
    return isinstance(value, str) and ID_RE.fullmatch(value) is not None


def _require_id(
    row: dict[str, Any], field: str, diagnostics: list[Diagnostic], kind: str, line: int
) -> bool:
    if not _is_id(row[field]):
        _diagnostic(diagnostics, "invalid_opaque_id", kind, line, field)
        return False
    return True


def _require_choice(
    row: dict[str, Any],
    field: str,
    choices: Iterable[str],
    diagnostics: list[Diagnostic],
    kind: str,
    line: int,
) -> bool:
    if not isinstance(row[field], str) or row[field] not in choices:
        _diagnostic(diagnostics, "invalid_choice", kind, line, field)
        return False
    return True


def _validate_source_rows(
    rows: list[tuple[int, dict[str, Any]]], diagnostics: list[Diagnostic]
) -> dict[str, tuple[int, dict[str, Any]]]:
    sources: dict[str, tuple[int, dict[str, Any]]] = {}
    for line, row in rows:
        row_valid = True
        if row["schema_version"] != SCHEMA_VERSION:
            _diagnostic(diagnostics, "schema_version", "source", line, "schema_version")
            row_valid = False
        source_id_valid = _require_id(row, "source_id", diagnostics, "source", line)
        consent_id_valid = _require_id(
            row, "consent_reference", diagnostics, "source", line
        )
        batch_id_valid = _require_id(
            row, "collection_batch_id", diagnostics, "source", line
        )
        provenance_valid = _require_choice(
            row,
            "provenance_class",
            ("tester_donated_authentic", "tester_authored_simulation"),
            diagnostics,
            "source",
            line,
        )
        row_valid = row_valid and all(
            (source_id_valid, consent_id_valid, batch_id_valid, provenance_valid)
        )
        required_values = {
            "consent_status": "granted",
            "release_tier": "internal_only",
            "source_status": "active",
        }
        for field, expected in required_values.items():
            if row[field] != expected:
                _diagnostic(diagnostics, "source_authorization", "source", line, field)
                row_valid = False
        if row["internal_research_permitted"] is not True:
            _diagnostic(
                diagnostics,
                "source_authorization",
                "source",
                line,
                "internal_research_permitted",
            )
            row_valid = False
        if source_id_valid:
            source_id = row["source_id"]
            if source_id in sources:
                _diagnostic(diagnostics, "duplicate_id", "source", line, "source_id")
            elif row_valid:
                sources[source_id] = (line, row)
    return sources


def _in_frozen_default_ignorable_ranges(character: str) -> bool:
    codepoint = ord(character)
    return any(start <= codepoint <= end for start, end in DEFAULT_IGNORABLE_RANGES)


def _safety_view(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text)
    return "".join(
        character
        for character in normalized
        if unicodedata.category(character) != "Cf"
        and not _in_frozen_default_ignorable_ranges(character)
    )


def _unsafe_text_codes(text: str) -> tuple[str, ...]:
    codes: list[str] = []
    if any(ord(character) in BIDI_CONTROL_CODEPOINTS for character in text):
        codes.append("bidi_control")
    if any(
        unicodedata.category(character) == "Cc" and character not in "\t\n\r"
        for character in text
    ):
        codes.append("disallowed_control")

    safety_text = _safety_view(text)
    if not any(not character.isspace() for character in safety_text):
        codes.append("effectively_empty_text")
    if OTP_RE.search(safety_text) or SECRET_RE.search(safety_text):
        codes.append("credential_candidate")
    if ACCOUNT_RE.search(safety_text) or LONG_NUMBER_RE.search(safety_text):
        codes.append("financial_identifier_candidate")
    if any(scan_live_artifacts(safety_text).values()):
        codes.append("recognized_live_artifact")
    if any(scan_residual_candidates(safety_text).values()):
        codes.append("residual_artifact_candidate")
    return tuple(dict.fromkeys(codes))


def _validate_item_rows(
    rows: list[tuple[int, dict[str, Any]]],
    sources: dict[str, tuple[int, dict[str, Any]]],
    diagnostics: list[Diagnostic],
) -> dict[str, tuple[int, dict[str, Any]]]:
    items: dict[str, tuple[int, dict[str, Any]]] = {}
    duplicate_groups: dict[str, list[tuple[int, dict[str, Any]]]] = defaultdict(list)
    template_groups: dict[str, list[tuple[int, dict[str, Any]]]] = defaultdict(list)
    for line, row in rows:
        row_valid = True
        if row["schema_version"] != SCHEMA_VERSION:
            _diagnostic(diagnostics, "schema_version", "item", line, "schema_version")
            row_valid = False
        item_id_valid = _require_id(row, "item_id", diagnostics, "item", line)
        source_id_valid = _require_id(row, "source_id", diagnostics, "item", line)
        component_valid = _require_id(
            row, "leakage_component_id", diagnostics, "item", line
        )
        stratum_valid = _require_choice(
            row, "language_stratum", LANGUAGE_STRATA, diagnostics, "item", line
        )
        label_valid = _require_choice(
            row, "final_label", FINAL_LABELS, diagnostics, "item", line
        )
        resolution_valid = _require_choice(
            row,
            "label_resolution",
            ("blind_agreement", "adjudicated"),
            diagnostics,
            "item",
            line,
        )
        row_valid = row_valid and all(
            (
                item_id_valid,
                source_id_valid,
                component_valid,
                stratum_valid,
                label_valid,
                resolution_valid,
            )
        )
        if row["partition"] != "pilot":
            _diagnostic(diagnostics, "partition", "item", line, "partition")
            row_valid = False
        for field in ("romanized_indic", "romanization_ambiguous", "privacy_review"):
            if not isinstance(row[field], bool):
                _diagnostic(diagnostics, "invalid_boolean", "item", line, field)
                row_valid = False
        if row["privacy_review"] is not True:
            _diagnostic(diagnostics, "privacy_review", "item", line, "privacy_review")
            row_valid = False
        if row["romanization_ambiguous"] is True and row["romanized_indic"] is not True:
            _diagnostic(
                diagnostics, "romanization_invariant", "item", line, "romanization_ambiguous"
            )
            row_valid = False
        artifact_review = row["artifact_review"]
        artifact_review_valid = True
        if not isinstance(artifact_review, dict) or frozenset(artifact_review) != {
            "status",
            "representation",
        }:
            _diagnostic(diagnostics, "artifact_review_schema", "item", line, "artifact_review")
            row_valid = False
            artifact_review_valid = False
        elif (
            artifact_review["status"] != "passed"
            or not isinstance(artifact_review["representation"], str)
            or artifact_review["representation"]
            not in {"none", "typed_placeholders", "defanged"}
        ):
            _diagnostic(diagnostics, "artifact_review", "item", line, "artifact_review")
            row_valid = False
            artifact_review_valid = False

        text = row["text"]
        text_bytes: bytes | None = None
        try:
            if isinstance(text, str):
                text_bytes = text.encode("utf-8", errors="strict")
        except UnicodeEncodeError:
            text_bytes = None
        if not isinstance(text, str) or text_bytes is None or (
            not text.strip()
            or len(text) > MAX_TEXT_CHARACTERS
            or len(text_bytes) > MAX_LINE_BYTES // 2
            or "\x00" in text
        ):
            _diagnostic(diagnostics, "invalid_text", "item", line, "text")
            row_valid = False
        else:
            unsafe_codes = _unsafe_text_codes(text)
            for unsafe_code in unsafe_codes:
                _diagnostic(diagnostics, unsafe_code, "item", line, "text")
            if unsafe_codes:
                row_valid = False
            if artifact_review_valid:
                has_typed_placeholder = TYPED_PLACEHOLDER_RE.search(text) is not None
                representation = artifact_review["representation"]
                if (representation == "none" and has_typed_placeholder) or (
                    representation == "typed_placeholders" and not has_typed_placeholder
                ):
                    _diagnostic(
                        diagnostics,
                        "artifact_representation_mismatch",
                        "item",
                        line,
                        "artifact_review",
                    )
                    row_valid = False
            expected_hash = sha256(text_bytes).hexdigest()
            if not isinstance(row["content_sha256"], str) or not SHA256_RE.fullmatch(
                row["content_sha256"]
            ):
                _diagnostic(diagnostics, "content_hash_format", "item", line, "content_sha256")
                row_valid = False
            elif row["content_sha256"] != expected_hash:
                _diagnostic(diagnostics, "content_hash_mismatch", "item", line, "content_sha256")
                row_valid = False
            if component_valid and label_valid and stratum_valid:
                duplicate_groups[normalize_duplicate_key(text)].append((line, row))
                template_groups[template_group_id(text)].append((line, row))

        if not source_id_valid or row["source_id"] not in sources:
            _diagnostic(diagnostics, "unknown_foreign_key", "item", line, "source_id")
            row_valid = False
        if item_id_valid:
            item_id = row["item_id"]
            if item_id in items:
                _diagnostic(diagnostics, "duplicate_id", "item", line, "item_id")
                row_valid = False
            elif row_valid:
                items[item_id] = (line, row)

    for group in duplicate_groups.values():
        components = {row["leakage_component_id"] for _, row in group}
        outcomes = {(row["final_label"], row["language_stratum"]) for _, row in group}
        if len(group) > 1:
            for line, _ in group:
                _diagnostic(diagnostics, "duplicate_text_retained", "item", line, "text")
        if len(components) > 1:
            for line, _ in group:
                _diagnostic(
                    diagnostics, "duplicate_component_conflict", "item", line, "leakage_component_id"
                )
        if len(outcomes) > 1:
            for line, _ in group:
                _diagnostic(diagnostics, "duplicate_outcome_conflict", "item", line)
    for group in template_groups.values():
        components = {row["leakage_component_id"] for _, row in group}
        if len(components) > 1:
            for line, _ in group:
                _diagnostic(
                    diagnostics,
                    "template_component_conflict",
                    "item",
                    line,
                    "leakage_component_id",
                )

    containment: dict[str, dict[str, list[tuple[int, str]]]] = {
        "source_component_conflict": defaultdict(list),
        "consent_component_conflict": defaultdict(list),
        "batch_component_conflict": defaultdict(list),
    }
    for line, row in items.values():
        source = sources[row["source_id"]][1]
        component = row["leakage_component_id"]
        containment["source_component_conflict"][row["source_id"]].append((line, component))
        containment["consent_component_conflict"][source["consent_reference"]].append(
            (line, component)
        )
        containment["batch_component_conflict"][source["collection_batch_id"]].append(
            (line, component)
        )
    for code, mappings in containment.items():
        for records in mappings.values():
            if len({component for _, component in records}) > 1:
                for line, _ in records:
                    _diagnostic(diagnostics, code, "item", line, "leakage_component_id")
    return items


def _validate_annotation_rows(
    rows: list[tuple[int, dict[str, Any]]],
    items: dict[str, tuple[int, dict[str, Any]]],
    diagnostics: list[Diagnostic],
) -> dict[str, list[tuple[int, dict[str, Any]]]]:
    by_item: dict[str, list[tuple[int, dict[str, Any]]]] = defaultdict(list)
    annotation_ids: set[str] = set()
    for line, row in rows:
        row_valid = True
        if row["schema_version"] != SCHEMA_VERSION:
            _diagnostic(diagnostics, "schema_version", "annotation", line, "schema_version")
            row_valid = False
        annotation_id_ok = _require_id(row, "annotation_id", diagnostics, "annotation", line)
        item_id_ok = _require_id(row, "item_id", diagnostics, "annotation", line)
        annotator_id_ok = _require_id(row, "annotator_id", diagnostics, "annotation", line)
        kind_ok = _require_choice(
            row, "kind", ("blind", "adjudication"), diagnostics, "annotation", line
        )
        label_ok = _require_choice(
            row, "primary_label", ANNOTATION_LABELS, diagnostics, "annotation", line
        )
        stratum_ok = _require_choice(
            row, "language_stratum", ANNOTATION_STRATA, diagnostics, "annotation", line
        )
        confidence_ok = _require_choice(
            row, "confidence", ("high", "medium", "low"), diagnostics, "annotation", line
        )
        row_valid = row_valid and all(
            (
                annotation_id_ok,
                item_id_ok,
                annotator_id_ok,
                kind_ok,
                label_ok,
                stratum_ok,
                confidence_ok,
            )
        )
        if annotation_id_ok:
            if row["annotation_id"] in annotation_ids:
                _diagnostic(
                    diagnostics, "duplicate_id", "annotation", line, "annotation_id"
                )
                row_valid = False
            annotation_ids.add(row["annotation_id"])
        if not item_id_ok or row["item_id"] not in items:
            _diagnostic(diagnostics, "unknown_foreign_key", "annotation", line, "item_id")
            row_valid = False
        if row_valid:
            by_item[row["item_id"]].append((line, row))

    for item_id, (item_line, item) in items.items():
        annotations = by_item.get(item_id, [])
        blind = [(line, row) for line, row in annotations if row["kind"] == "blind"]
        adjudication = [
            (line, row) for line, row in annotations if row["kind"] == "adjudication"
        ]
        if len(blind) != 2 or len({row["annotator_id"] for _, row in blind}) != 2:
            _diagnostic(diagnostics, "blind_annotation_pair", "item", item_line)
            continue
        blind_agrees = (
            blind[0][1]["primary_label"] == blind[1][1]["primary_label"]
            and blind[0][1]["language_stratum"] == blind[1][1]["language_stratum"]
            and blind[0][1]["primary_label"] in FINAL_LABELS
            and blind[0][1]["language_stratum"] in LANGUAGE_STRATA
        )
        if blind_agrees:
            if adjudication:
                _diagnostic(diagnostics, "unexpected_adjudication", "item", item_line)
            expected_label = blind[0][1]["primary_label"]
            expected_stratum = blind[0][1]["language_stratum"]
            if (
                item["label_resolution"] != "blind_agreement"
                or item["final_label"] != expected_label
                or item["language_stratum"] != expected_stratum
            ):
                _diagnostic(diagnostics, "blind_resolution_mismatch", "item", item_line)
        else:
            if len(adjudication) != 1:
                _diagnostic(diagnostics, "adjudication_required", "item", item_line)
                continue
            adjudicator = adjudication[0][1]
            if adjudicator["annotator_id"] in {row["annotator_id"] for _, row in blind}:
                _diagnostic(diagnostics, "adjudicator_not_distinct", "item", item_line)
            if (
                adjudicator["primary_label"] not in FINAL_LABELS
                or adjudicator["language_stratum"] not in LANGUAGE_STRATA
            ):
                _diagnostic(diagnostics, "invalid_adjudication_outcome", "item", item_line)
            elif (
                item["label_resolution"] != "adjudicated"
                or item["final_label"] != adjudicator["primary_label"]
                or item["language_stratum"] != adjudicator["language_stratum"]
            ):
                _diagnostic(diagnostics, "adjudication_resolution_mismatch", "item", item_line)
    return by_item


def _nominal_alpha(pairs: list[tuple[str, str]]) -> float | None:
    if not pairs:
        return None
    observed_disagreement = sum(left != right for left, right in pairs) / len(pairs)
    counts = Counter(value for pair in pairs for value in pair)
    total = sum(counts.values())
    expected_agreement = sum(count * (count - 1) for count in counts.values()) / (
        total * (total - 1)
    )
    expected_disagreement = 1.0 - expected_agreement
    if expected_disagreement == 0:
        return None
    return 1.0 - observed_disagreement / expected_disagreement


def _assign_folds(items: Iterable[dict[str, Any]]) -> tuple[dict[str, int], list[dict[str, Any]]]:
    component_counts: dict[str, Counter[tuple[str, str]]] = defaultdict(Counter)
    for item in items:
        cell = (item["language_stratum"], item["final_label"])
        component_counts[item["leakage_component_id"]][cell] += 1

    folds: list[Counter[tuple[str, str]]] = [Counter() for _ in range(3)]
    fold_components: list[set[str]] = [set() for _ in range(3)]
    assignments: dict[str, int] = {}
    ordered = sorted(
        component_counts.items(),
        key=lambda pair: (
            -sum(pair[1].values()),
            sha256(pair[0].encode("ascii", errors="ignore")).hexdigest(),
            pair[0],
        ),
    )
    for component_id, counts in ordered:
        chosen = min(
            range(3),
            key=lambda fold: (
                sum(
                    (folds[fold][cell] + counts[cell]) ** 2
                    for cell in PILOT_CELLS
                ),
                sum(folds[fold].values()),
                len(fold_components[fold]),
                fold,
            ),
        )
        assignments[component_id] = chosen
        folds[chosen].update(counts)
        fold_components[chosen].add(component_id)
    aggregates = [
        {
            "fold": fold,
            "items": int(sum(counts.values())),
            "components": len(fold_components[fold]),
            "labels": {
                label: int(
                    sum(counts[(stratum, label)] for stratum in LANGUAGE_STRATA)
                )
                for label in FINAL_LABELS
            },
            "cells": [
                {
                    "language_stratum": stratum,
                    "final_label": label,
                    "items": int(counts[(stratum, label)]),
                }
                for stratum, label in PILOT_CELLS
            ],
        }
        for fold, counts in enumerate(folds)
    ]
    return assignments, aggregates


def _readiness(
    mode: str,
    items: dict[str, tuple[int, dict[str, Any]]],
    annotations: dict[str, list[tuple[int, dict[str, Any]]]],
    diagnostics: list[Diagnostic],
) -> dict[str, object]:
    item_values = [row for _, row in items.values()]
    cells: Counter[tuple[str, str]] = Counter(
        (row["language_stratum"], row["final_label"]) for row in item_values
    )
    cell_component_counts: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
    for row in item_values:
        cell = (row["language_stratum"], row["final_label"])
        cell_component_counts[cell][row["leakage_component_id"]] += 1

    label_pairs: list[tuple[str, str]] = []
    language_pairs: list[tuple[str, str]] = []
    disagreements = 0
    uncertainty_items = 0
    uncertain_ratings = 0
    for item_id in sorted(items):
        blind = [
            row
            for _, row in annotations.get(item_id, [])
            if row.get("kind") == "blind"
        ]
        if len(blind) != 2:
            continue
        label_pair = (blind[0]["primary_label"], blind[1]["primary_label"])
        language_pair = (blind[0]["language_stratum"], blind[1]["language_stratum"])
        label_pairs.append(label_pair)
        language_pairs.append(language_pair)
        if label_pair[0] != label_pair[1] or language_pair[0] != language_pair[1]:
            disagreements += 1
        if "uncertain" in label_pair or "uncertain" in language_pair:
            uncertainty_items += 1
        uncertain_ratings += sum(
            blind_rating["primary_label"] == "uncertain"
            or blind_rating["language_stratum"] == "uncertain"
            for blind_rating in blind
        )

    label_agreement = (
        sum(left == right and left in FINAL_LABELS for left, right in label_pairs)
        / len(label_pairs)
        if label_pairs
        else None
    )
    label_alpha = _nominal_alpha(label_pairs)
    language_agreement = (
        sum(
            left == right and left in LANGUAGE_STRATA
            for left, right in language_pairs
        )
        / len(language_pairs)
        if language_pairs
        else None
    )
    language_alpha = _nominal_alpha(language_pairs)
    _, folds = _assign_folds(item_values)

    readiness_gaps: list[tuple[str, str]] = []
    if len(item_values) != 240:
        readiness_gaps.append(("ready_item_count", "item"))
    for stratum in LANGUAGE_STRATA:
        for label in FINAL_LABELS:
            cell = (stratum, label)
            if cells[cell] != 30:
                readiness_gaps.append(("ready_cell_count", "item"))
            if len(cell_component_counts[cell]) < 5:
                readiness_gaps.append(("ready_cell_components", "item"))
            if cell_component_counts[cell] and max(cell_component_counts[cell].values()) > 10:
                readiness_gaps.append(("ready_cell_component_dominance", "item"))
    metric_requirements = (
        ("ready_label_agreement", label_agreement, 0.90),
        ("ready_language_agreement", language_agreement, 0.90),
        ("ready_label_alpha", label_alpha, 0.80),
        ("ready_language_alpha", language_alpha, 0.80),
    )
    for code, value, threshold in metric_requirements:
        if value is None or value < threshold:
            readiness_gaps.append((code, "annotation"))
    if any(
        fold["labels"]["benign"] == 0 or fold["labels"]["phishing"] == 0 for fold in folds
    ):
        readiness_gaps.append(("ready_fold_label_coverage", "item"))
    if any(fold["components"] < 5 for fold in folds):
        readiness_gaps.append(("ready_fold_components", "item"))
    if any(any(cell["items"] == 0 for cell in fold["cells"]) for fold in folds):
        readiness_gaps.append(("ready_fold_cell_coverage", "item"))

    severity = "error" if mode == "ready" else "warning"
    for code, kind in readiness_gaps:
        _diagnostic(diagnostics, code, kind, severity=severity)

    return {
        "cells": [
            {
                "language_stratum": stratum,
                "final_label": label,
                "items": int(cells[(stratum, label)]),
                "leakage_components": len(cell_component_counts[(stratum, label)]),
                "largest_component_items": max(
                    cell_component_counts[(stratum, label)].values(), default=0
                ),
            }
            for stratum, label in PILOT_CELLS
        ],
        "blind_label_raw_agreement": label_agreement,
        "blind_label_nominal_alpha": label_alpha,
        "blind_language_known_raw_agreement": language_agreement,
        "blind_language_nominal_alpha": language_alpha,
        "disagreement_items": disagreements,
        "uncertainty_items": uncertainty_items,
        "uncertain_ratings": uncertain_ratings,
        "uncertain_item_rate": (
            uncertainty_items / len(label_pairs) if label_pairs else None
        ),
        "uncertain_rating_rate": (
            uncertain_ratings / (2 * len(label_pairs)) if label_pairs else None
        ),
        "component_cross_fold_violations": 0,
        "folds": folds,
    }


def validate_files(
    sources_path: str | Path,
    items_path: str | Path,
    annotations_path: str | Path,
    *,
    mode: str = "draft",
) -> ValidationResult:
    if mode not in MODES:
        raise ValueError("mode must be draft or ready")
    diagnostics: list[Diagnostic] = []
    source_rows = _load_jsonl(sources_path, "source", SOURCE_KEYS, diagnostics)
    item_rows = _load_jsonl(items_path, "item", ITEM_KEYS, diagnostics)
    annotation_rows = _load_jsonl(
        annotations_path, "annotation", ANNOTATION_KEYS, diagnostics
    )
    sources = _validate_source_rows(source_rows, diagnostics)
    items = _validate_item_rows(item_rows, sources, diagnostics)
    annotations = _validate_annotation_rows(annotation_rows, items, diagnostics)
    readiness = _readiness(mode, items, annotations, diagnostics)

    source_provenance_counts = Counter(
        row["provenance_class"]
        for _, row in sources.values()
        if row.get("provenance_class")
        in {"tester_donated_authentic", "tester_authored_simulation"}
    )
    item_values = [row for _, row in items.values()]
    item_provenance_counts = Counter(
        sources[row["source_id"]][1]["provenance_class"] for row in item_values
    )
    diagnostics.sort(
        key=lambda diagnostic: (
            diagnostic.severity,
            diagnostic.code,
            diagnostic.record_kind,
            diagnostic.line if diagnostic.line is not None else -1,
            diagnostic.field or "",
        )
    )
    error_count = sum(diagnostic.severity == "error" for diagnostic in diagnostics)
    warning_count = sum(diagnostic.severity == "warning" for diagnostic in diagnostics)
    report: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "mode": mode,
        "status": "VALID" if error_count == 0 else "INVALID",
        "counts": {
            "sources": len(sources),
            "items": len(items),
            "annotations": sum(len(value) for value in annotations.values()),
            "errors": error_count,
            "warnings": warning_count,
        },
        "provenance": {
            record_kind: {
                key: int(counts[key])
                for key in ("tester_donated_authentic", "tester_authored_simulation")
            }
            for record_kind, counts in (
                ("sources", source_provenance_counts),
                ("items", item_provenance_counts),
            )
        },
        "romanization": {
            "romanized_indic_items": sum(row.get("romanized_indic") is True for row in item_values),
            "ambiguous_items": sum(
                row.get("romanization_ambiguous") is True for row in item_values
            ),
        },
        "readiness": readiness,
        "diagnostics": [diagnostic.as_dict() for diagnostic in diagnostics],
    }
    return ValidationResult(mode, report, tuple(diagnostics))
