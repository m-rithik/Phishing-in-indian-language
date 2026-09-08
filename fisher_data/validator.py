"""Strict cross-file validator for the Fisher Phase-0 v1.2 JSONL contract."""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from dataclasses import asdict, dataclass
from datetime import date
from hashlib import sha256
import io
import ipaddress
import json
import os
from pathlib import Path
import re
import stat
import unicodedata
from typing import Any, Callable, Iterable


SCHEMA_VERSION = "1.2.0"
PARTITIONS = {
    "pilot",
    "unassigned",
    "development",
    "probability_calibration",
    "safety_threshold",
    "primary_test",
    "external_test",
    "excluded",
}
PROTECTED_PARTITIONS = {
    "probability_calibration",
    "safety_threshold",
    "primary_test",
}
LANGUAGE_STRATA = {
    "hindi": "hi",
    "tamil": "ta",
    "telugu": "te",
    "english_indic_code_mixed": "mixed",
}
ANNOTATION_LANGUAGE_STRATA = set(LANGUAGE_STRATA) | {"uncertain"}
ITEM_LANGUAGES = {"hi", "ta", "te", "mixed", "unknown"}
BINARY_LABELS = {"phishing", "benign"}
LABELS = BINARY_LABELS | {"uncertain"}
SUBTYPES = {
    "personal",
    "transactional",
    "promotional",
    "informational",
    "other",
    "not_applicable",
}
FACETS = {
    "claimed_actor",
    "claim_or_problem",
    "requested_action",
    "sensitive_item_or_asset",
    "destination_artifact",
    "pressure_tactic",
}
SPAN_FACETS = FACETS | {"supporting_evidence"}
FACET_STATES = {"explicit", "not_explicit", "not_applicable"}
DESTINATION_QUALIFIERS = {
    "URL",
    "DOMAIN",
    "PHONE",
    "UPI",
    "BANK",
    "EMAIL",
    "APP",
    "OTHER",
}
VISIBLE_ARTIFACT_KINDS = DESTINATION_QUALIFIERS
VISIBLE_ARTIFACT_REPRESENTATIONS = {
    "DEFANGED",
    "RESERVED",
    "TYPED_PLACEHOLDER",
}
TYPED_PLACEHOLDERS = {
    "URL": "[URL]",
    "DOMAIN": "[DOMAIN]",
    "PHONE": "[PHONE]",
    "UPI": "[UPI]",
    "BANK": "[BANK]",
    "EMAIL": "[EMAIL]",
    "APP": "[APP]",
    "OTHER": "[ARTIFACT]",
}
DEFANGING_MARKERS = ("[.]", "(.)", "[at]", "[redacted]", "hxxp:", "hxxps:", "XXXX")
PRESSURE_QUALIFIERS = {
    "URGENCY",
    "THREAT",
    "AUTHORITY",
    "SCARCITY",
    "REWARD",
    "FEAR",
    "TRUST",
    "SOCIAL_PROOF",
    "OTHER",
}
REGISTRY_REFERENCE_LABELS = {"MATCH", "MISMATCH", "UNKNOWN"}
REGISTRY_COVERAGE = {"complete", "partial", "missing"}
BLINDING_ATTESTATION = "primary_label_provenance_and_protected_outcomes_hidden"
AMBIGUITY_TAGS = {
    "language",
    "intent",
    "actor",
    "action",
    "destination",
    "romanization",
    "missing_context",
    "other",
}
TOKEN_LANGUAGES = {"hi", "ta", "te", "en", "other"}
SCRIPTS = {"devanagari", "tamil", "telugu", "latin", "other"}
CODE_MIX_PAIRS = {"none", "en_hi", "en_ta", "en_te"}
AFFECTED_DECISIONS = {"primary_label"} | FACETS
LINEAGE_OPERATIONS = {
    "original",
    "translation",
    "transliteration",
    "paraphrase",
    "counterfactual",
    "augmentation",
}
ID_PATTERNS = {
    "source_id": re.compile(r"src_[a-z0-9][a-z0-9_-]{0,62}\Z"),
    "item_id": re.compile(r"item_[a-z0-9][a-z0-9_-]{0,62}\Z"),
    "leakage_component_id": re.compile(r"component_[a-z0-9][a-z0-9_-]{0,62}\Z"),
    "annotation_id": re.compile(r"annotation_[a-z0-9][a-z0-9_-]{0,62}\Z"),
    "annotator_id": re.compile(r"annotator_[a-z0-9][a-z0-9_-]{0,62}\Z"),
    "registry_snapshot_id": re.compile(r"registry_[a-z0-9][a-z0-9_-]{0,62}\Z"),
    "registry_reference_id": re.compile(r"registry_reference_[a-z0-9][a-z0-9_-]{0,44}\Z"),
    "registry_reviewer_id": re.compile(r"annotator_[a-z0-9][a-z0-9_-]{0,62}\Z"),
    "registry_evidence_id": re.compile(r"registry_evidence_[a-z0-9][a-z0-9_-]{0,45}\Z"),
    "resolver_version": re.compile(r"resolver_[0-9]{1,6}\.[0-9]{1,6}\.[0-9]{1,6}(?:-[a-z0-9][a-z0-9.-]{0,31})?\Z"),
}
HASH_PATTERN = re.compile(r"[0-9a-f]{64}\Z")
VERSION_PATTERN = re.compile(r"[0-9]+\.[0-9]+\.[0-9]+(?:-[a-z0-9][a-z0-9.-]{0,31})?\Z")
RESERVED_ARTIFACT_PATTERN = re.compile(
    r"(?i)(?:https?://|www\.)?"
    r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
    r"(?:example|invalid)(?:/[A-Za-z0-9._~!$&'()*+,;=:@%/-]*)?\Z"
)
SAFE_METADATA_PATTERN = re.compile(r"[A-Za-z0-9_.\[\]-]{1,160}\Z")
EMAIL_PATTERN = re.compile(r"(?iu)(?<![\w.])[^\s@<>]+@(?:[^\W_](?:[\w-]{0,61}[^\W_])?\.)+[^\W\d_]{2,63}\b")
PHONE_PATTERN = re.compile(r"(?<!\w)(?:\+\d{1,3}[ .()-]*)?(?:\d[ .()-]*){10,15}(?!\w)")
URL_PATTERN = re.compile(r"(?i)\b(?:https?://|ftp://|www\.)[^\s<>]+")
MAILTO_PATTERN = re.compile(r"(?i)\bmailto:[^\s<>]+")
DOMAIN_PATTERN = re.compile(r"(?iu)(?<![@\w.-])(?:[^\W_](?:[\w-]{0,61}[^\W_])?\.)+[^\W\d_]{2,63}\b")
IPV4_PATTERN = re.compile(r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])")
IPV6_CANDIDATE_PATTERN = re.compile(
    r"(?<![\w:.])\[?([0-9A-Fa-f:.]*:[0-9A-Fa-f:.]*:[0-9A-Fa-f:.]*)\]?(?![\w:.])"
)
UPI_HANDLE_PATTERN = re.compile(
    r"(?i)(?<![A-Za-z0-9._-])"
    r"[A-Za-z0-9][A-Za-z0-9._-]{0,255}@[A-Za-z][A-Za-z0-9_-]{0,63}"
    r"(?=$|[^A-Za-z0-9._-]|\.+(?=$|[^A-Za-z0-9_-]))"
)
SECRET_VALUE_PATTERN = re.compile(
    r"(?i)(?<![A-Za-z0-9])(?:otp|pin|password|passcode|credential|recovery[ _-]?code)"
    r"\s*[:=]\s*[A-Za-z0-9!@$^*._-]{4,}(?![A-Za-z0-9])"
)
RESERVED_TLDS = {"example", "invalid", "test"}
BIDI_CONTROL_CODEPOINTS = {
    0x061C,
    0x200E,
    0x200F,
    0x202A,
    0x202B,
    0x202C,
    0x202D,
    0x202E,
    0x2066,
    0x2067,
    0x2068,
    0x2069,
}
EXCLUSION_REASONS = {
    "unresolved_primary_label",
    "unresolved_language_stratum",
    "governance_ineligible",
    "safety_ineligible",
    "privacy_ineligible",
    "out_of_scope",
    "duplicate_or_leakage",
}
PILOT_EXCLUSION_REASONS = {"unresolved_primary_label", "unresolved_language_stratum"}
PUBLIC_PARTITIONS = {"development", "external_test"}
APPROVAL_STATES = {"approved", "pending", "blocked"}

# Operational, not statistical, safety limits. They intentionally exceed the later 6k design.
MAX_FILE_BYTES = 512 * 1024 * 1024
MAX_LINE_CHARS = 1_000_000
MAX_RECORDS = {
    "sources": 10_000,
    "items": 10_000,
    "annotations": 40_000,
    "registry_manifest": 10_000,
    "registry_references": 100_000,
}
MAX_NESTING_DEPTH = 32
MAX_LIST_ITEMS = 10_000
MAX_ITEM_TEXT_CHARS = 10_000
MAX_RATIONALE_CHARS = 500
MAX_VISIBLE_ARTIFACTS = 64


@dataclass(frozen=True)
class Diagnostic:
    severity: str
    code: str
    dataset: str
    message: str
    line: int | None = None
    record_id: str | None = None
    field: str | None = None
    related_record_id: str | None = None


@dataclass(frozen=True)
class Agreement:
    paired_items: int
    agreements: int
    raw_agreement: float | None
    cohen_kappa: float | None
    krippendorff_alpha: float | None


@dataclass(frozen=True)
class LanguageAgreement:
    paired_items: int
    agreements: int
    raw_agreement: float | None
    krippendorff_alpha: float | None


@dataclass(frozen=True)
class Reliability:
    binary_pair_coverage: float | None
    language_agreement: LanguageAgreement
    facet_alpha_overall: dict[str, float | None]
    per_stratum_alpha: dict[str, dict[str, float | None]]
    facet_span_exact_f1: dict[str, float | None]
    facet_span_character_overlap_f1: dict[str, float | None]
    endpoint_pair_structure_exact_f1: float | None
    supporting_evidence_exact_f1: float | None
    supporting_evidence_character_overlap_f1: float | None
    completeness: float | None


@dataclass(frozen=True)
class RegistryReferenceInventory:
    applicable_endpoint_pairs: int
    reference_records: int
    complete: int
    partial: int
    missing: int
    match: int
    mismatch: int
    unknown: int
    zero_applicable_pairs: bool


@dataclass(frozen=True)
class ValidationReport:
    mode: str
    valid: bool
    counts: dict[str, int]
    errors: int
    warnings: int
    llm_development_share: float | None
    llm_pilot_share: float | None
    unresolved_final_items: int
    unresolved_final_rate: float | None
    agreement: Agreement
    reliability: Reliability
    registry_reference_inventory: RegistryReferenceInventory
    diagnostics: tuple[Diagnostic, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "agreement": asdict(self.agreement),
            "counts": self.counts,
            "diagnostics": [asdict(diagnostic) for diagnostic in self.diagnostics],
            "errors": self.errors,
            "llm_development_share": self.llm_development_share,
            "llm_pilot_share": self.llm_pilot_share,
            "mode": self.mode,
            "reliability": asdict(self.reliability),
            "registry_reference_inventory": asdict(self.registry_reference_inventory),
            "unresolved_final_items": self.unresolved_final_items,
            "unresolved_final_rate": self.unresolved_final_rate,
            "valid": self.valid,
            "warnings": self.warnings,
        }


class _DuplicateKeyError(ValueError):
    pass


class _Validator:
    def __init__(
        self, mode: str, *, registry_manifest_supplied: bool, registry_references_supplied: bool
    ) -> None:
        if mode not in {"draft", "pilot-final"}:
            raise ValueError("mode must be 'draft' or 'pilot-final'")
        self.mode = mode
        self.registry_manifest_supplied = registry_manifest_supplied
        self.registry_references_supplied = registry_references_supplied
        self.diagnostics: list[Diagnostic] = []
        self.sources: dict[str, tuple[int, dict[str, Any]]] = {}
        self.items: dict[str, tuple[int, dict[str, Any]]] = {}
        self.annotations: dict[str, tuple[int, dict[str, Any]]] = {}
        self.registry_manifest: dict[str, tuple[int, dict[str, Any]]] = {}
        self.registry_references: dict[str, tuple[int, dict[str, Any]]] = {}
        self.invalid_annotations: set[str] = set()

    def add(
        self,
        severity: str,
        code: str,
        dataset: str,
        message: str,
        *,
        line: int | None = None,
        record_id: str | None = None,
        field: str | None = None,
        related_record_id: str | None = None,
    ) -> None:
        safe_code = code if SAFE_METADATA_PATTERN.fullmatch(code) else "validation_error"
        safe_dataset = dataset if dataset in {"sources", "items", "annotations", "registry_manifest", "registry_references", "global"} else "global"
        safe_field = field if field is not None and SAFE_METADATA_PATTERN.fullmatch(field) else None
        safe_record_id = record_id if _is_safe_record_id(record_id) else None
        safe_related_id = related_record_id if _is_safe_record_id(related_record_id) else None
        safe_message = message if not _has_forbidden_control(message) else "Validation failed."
        self.diagnostics.append(
            Diagnostic(
                severity=severity if severity in {"error", "warning"} else "error",
                code=safe_code,
                dataset=safe_dataset,
                message=safe_message,
                line=line if type(line) is int and line > 0 else None,
                record_id=safe_record_id,
                field=safe_field,
                related_record_id=safe_related_id,
            )
        )
        if severity == "error" and safe_dataset == "annotations" and safe_record_id is not None:
            self.invalid_annotations.add(safe_record_id)

    def load(
        self,
        path: Path,
        dataset: str,
        record_id_field: str,
        validate_record: Callable[[dict[str, Any], str, int, str | None], bool],
    ) -> dict[str, tuple[int, dict[str, Any]]]:
        records: dict[str, tuple[int, dict[str, Any]]] = {}
        file_descriptor: int | None = None
        try:
            flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NONBLOCK", 0)
            nofollow_flag = getattr(os, "O_NOFOLLOW", 0)
            before_open = path.lstat()
            if not stat.S_ISREG(before_open.st_mode):
                self.add("error", "not_regular_file", dataset, "The JSONL input must be a regular file.")
                return records
            file_descriptor = os.open(path, flags | nofollow_flag)
            path_metadata = os.fstat(file_descriptor)
            if (
                before_open.st_dev != path_metadata.st_dev
                or before_open.st_ino != path_metadata.st_ino
            ):
                self.add("error", "file_changed_during_open", dataset, "The JSONL input changed while it was opened.")
                return records
            if not stat.S_ISREG(path_metadata.st_mode):
                self.add("error", "not_regular_file", dataset, "The JSONL input must be a regular file.")
                return records
            if path_metadata.st_size > MAX_FILE_BYTES:
                self.add("error", "file_size_limit", dataset, "The JSONL file exceeds the operational size limit.")
                return records
            captured_bytes = bytearray()
            with os.fdopen(file_descriptor, "rb") as binary_stream:
                file_descriptor = None
                while len(captured_bytes) <= MAX_FILE_BYTES:
                    remaining = MAX_FILE_BYTES + 1 - len(captured_bytes)
                    chunk = binary_stream.read(min(1024 * 1024, remaining))
                    if not chunk:
                        break
                    captured_bytes.extend(chunk)
            if len(captured_bytes) > MAX_FILE_BYTES:
                self.add("error", "file_size_limit", dataset, "The JSONL file exceeds the operational size limit.")
                return records
            raw_content = bytes(captured_bytes)
            decoded_content = raw_content.decode("utf-8")
            raw_lines: list[tuple[int, str]] = []
            with io.StringIO(decoded_content, newline=None) as stream:
                line_number = 0
                while True:
                    physical_line = stream.readline(MAX_LINE_CHARS + 3)
                    if not physical_line:
                        break
                    line_number += 1
                    if line_number > MAX_RECORDS[dataset]:
                        self.add("error", "record_count_limit", dataset, "The JSONL file exceeds the operational record-count limit.")
                        return {}
                    has_newline = physical_line.endswith("\n")
                    raw_line = physical_line[:-1] if has_newline else physical_line
                    if len(raw_line) > MAX_LINE_CHARS:
                        if not has_newline:
                            while physical_line and not physical_line.endswith("\n"):
                                physical_line = stream.readline(MAX_LINE_CHARS + 3)
                        self.add("error", "line_length_limit", dataset, "A JSONL line exceeds the operational length limit.", line=line_number)
                        continue
                    raw_lines.append((line_number, raw_line))
        except FileNotFoundError:
            self.add("error", "file_not_found", dataset, "The required JSONL file was not found.")
            return records
        except UnicodeDecodeError:
            self.add("error", "invalid_utf8", dataset, "The file is not valid UTF-8.")
            return records
        except OSError:
            self.add("error", "file_read_error", dataset, "The required JSONL file could not be read.")
            return records
        finally:
            if file_descriptor is not None:
                os.close(file_descriptor)

        for line_number, raw_line in raw_lines:
            if not raw_line.strip():
                self.add("error", "blank_line", dataset, "Blank lines are not permitted.", line=line_number)
                continue
            try:
                value = json.loads(
                    raw_line,
                    object_pairs_hook=_reject_duplicate_keys,
                    parse_constant=_reject_nonfinite_number,
                )
            except _DuplicateKeyError:
                self.add("error", "duplicate_json_key", dataset, "A JSON object contains a duplicate key.", line=line_number)
                continue
            except (json.JSONDecodeError, ValueError, RecursionError):
                self.add("error", "invalid_json", dataset, "The line is not strict JSON.", line=line_number)
                continue
            hazards = _string_hazards(value)
            if "surrogate" in hazards:
                self.add("error", "forbidden_surrogate", dataset, "Escaped surrogate code points are prohibited.", line=line_number)
            if "control" in hazards:
                self.add("error", "forbidden_control", dataset, "Prohibited C0 control characters are present.", line=line_number)
            if "bidi" in hazards:
                self.add("error", "forbidden_bidi_control", dataset, "Bidirectional formatting controls are prohibited.", line=line_number)
            if hazards:
                continue
            structure_error = _structure_limit_error(value)
            if structure_error is not None:
                self.add("error", structure_error, dataset, "The record exceeds an operational structure limit.", line=line_number)
                continue
            if type(value) is not dict:
                self.add("error", "record_not_object", dataset, "Each line must contain one JSON object.", line=line_number)
                continue
            if _object_contains_live_artifact(value):
                self.add("error", "live_artifact", dataset, "A live route or contact artifact is prohibited.", line=line_number)
                continue
            if _object_contains_sensitive_artifact(value):
                self.add("error", "sensitive_artifact", dataset, "A secret-like value is prohibited.", line=line_number)
                continue

            raw_record_id = value.get(record_id_field)
            safe_record_id = (
                raw_record_id
                if type(raw_record_id) is str and _valid_id(record_id_field, raw_record_id)
                else None
            )
            shape_valid = validate_record(value, dataset, line_number, safe_record_id)
            if not shape_valid or safe_record_id is None:
                continue
            if safe_record_id in records:
                self.add(
                    "error",
                    "duplicate_record_id",
                    dataset,
                    "The record identifier is duplicated.",
                    line=line_number,
                    record_id=safe_record_id,
                    field=record_id_field,
                )
                continue
            records[safe_record_id] = (line_number, value)
        return records

    def object_shape(
        self,
        value: Any,
        fields: set[str],
        dataset: str,
        line: int,
        record_id: str | None,
        field: str,
    ) -> bool:
        if type(value) is not dict:
            self.add("error", "wrong_type", dataset, "The field has the wrong JSON type.", line=line, record_id=record_id, field=field)
            return False
        valid = True
        for missing in sorted(fields - value.keys()):
            safe_missing = f"{field}.{missing}" if field else missing
            self.add("error", "missing_field", dataset, "A required field is missing.", line=line, record_id=record_id, field=safe_missing)
            valid = False
        if value.keys() - fields:
            self.add("error", "unknown_field", dataset, "One or more unknown fields are not permitted.", line=line, record_id=record_id, field=field or "record")
            valid = False
        return valid

    def exact_type(
        self,
        value: Any,
        expected: type,
        dataset: str,
        line: int,
        record_id: str | None,
        field: str,
    ) -> bool:
        if type(value) is expected:
            return True
        self.add("error", "wrong_type", dataset, "The field has the wrong JSON type.", line=line, record_id=record_id, field=field)
        return False

    def enum(
        self,
        value: Any,
        allowed: set[str],
        dataset: str,
        line: int,
        record_id: str | None,
        field: str,
    ) -> bool:
        if not self.exact_type(value, str, dataset, line, record_id, field):
            return False
        if value in allowed:
            return True
        self.add("error", "invalid_value", dataset, "The field value is outside the contract vocabulary.", line=line, record_id=record_id, field=field)
        return False

    def identifier(
        self,
        value: Any,
        kind: str,
        dataset: str,
        line: int,
        record_id: str | None,
        field: str,
    ) -> bool:
        if not self.exact_type(value, str, dataset, line, record_id, field):
            return False
        if _valid_id(kind, value):
            return True
        self.add("error", "invalid_id", dataset, "The identifier does not match the required syntax.", line=line, record_id=record_id, field=field)
        return False

    def nonempty_string(
        self,
        value: Any,
        dataset: str,
        line: int,
        record_id: str | None,
        field: str,
    ) -> bool:
        if not self.exact_type(value, str, dataset, line, record_id, field):
            return False
        if value:
            return True
        self.add("error", "empty_string", dataset, "The field must not be empty.", line=line, record_id=record_id, field=field)
        return False

    def bounded_string(
        self,
        value: Any,
        maximum: int,
        dataset: str,
        line: int,
        record_id: str | None,
        field: str,
        *,
        nonempty: bool = False,
    ) -> bool:
        if not self.exact_type(value, str, dataset, line, record_id, field):
            return False
        if nonempty and not value:
            self.add("error", "empty_string", dataset, "The field must not be empty.", line=line, record_id=record_id, field=field)
            return False
        if len(value) <= maximum:
            return True
        self.add("error", "string_length_limit", dataset, "The string exceeds the field length limit.", line=line, record_id=record_id, field=field)
        return False

    def sha256_value(self, value: Any, dataset: str, line: int, record_id: str | None, field: str) -> bool:
        if not self.exact_type(value, str, dataset, line, record_id, field):
            return False
        if HASH_PATTERN.fullmatch(value):
            return True
        self.add("error", "invalid_sha256", dataset, "The field must be a lowercase SHA-256 digest.", line=line, record_id=record_id, field=field)
        return False

    def date_value(self, value: Any, dataset: str, line: int, record_id: str | None, field: str) -> bool:
        if not self.exact_type(value, str, dataset, line, record_id, field):
            return False
        try:
            parsed = date.fromisoformat(value)
        except ValueError:
            parsed = None
        if parsed is not None and parsed.isoformat() == value:
            return True
        self.add("error", "invalid_date", dataset, "The field must be a real YYYY-MM-DD date.", line=line, record_id=record_id, field=field)
        return False

    def schema_version(self, value: Any, dataset: str, line: int, record_id: str | None) -> bool:
        if not self.exact_type(value, str, dataset, line, record_id, "schema_version"):
            return False
        if value == SCHEMA_VERSION:
            return True
        self.add("error", "schema_version", dataset, "The record schema version is unsupported.", line=line, record_id=record_id, field="schema_version")
        return False

    def validate_registry_manifest(
        self, record: dict[str, Any], dataset: str, line: int, record_id: str | None
    ) -> bool:
        fields = {
            "schema_version",
            "registry_snapshot_id",
            "artifact_sha256",
            "version",
            "snapshot_date",
            "approval_state",
        }
        valid = self.object_shape(record, fields, dataset, line, record_id, "")
        valid &= self.schema_version(record.get("schema_version"), dataset, line, record_id)
        valid &= self.identifier(record.get("registry_snapshot_id"), "registry_snapshot_id", dataset, line, record_id, "registry_snapshot_id")
        valid &= self.sha256_value(record.get("artifact_sha256"), dataset, line, record_id, "artifact_sha256")
        version = record.get("version")
        if self.exact_type(version, str, dataset, line, record_id, "version"):
            if VERSION_PATTERN.fullmatch(version) is None:
                self.add("error", "invalid_version", dataset, "The version must use canonical semantic-version syntax.", line=line, record_id=record_id, field="version")
                valid = False
        else:
            valid = False
        valid &= self.date_value(record.get("snapshot_date"), dataset, line, record_id, "snapshot_date")
        valid &= self.enum(record.get("approval_state"), APPROVAL_STATES, dataset, line, record_id, "approval_state")
        return bool(valid)

    def validate_registry_reference(
        self, record: dict[str, Any], dataset: str, line: int, record_id: str | None
    ) -> bool:
        fields = {
            "schema_version",
            "registry_reference_id",
            "item_id",
            "final_annotation_id",
            "registry_reviewer_id",
            "registry_snapshot_id",
            "actor_span_index",
            "destination_span_index",
            "label",
            "registry_coverage",
            "registry_evidence_ids",
            "resolver_version",
            "blinding_attestation",
            "created_date",
        }
        valid = self.object_shape(record, fields, dataset, line, record_id, "")
        valid &= self.schema_version(record.get("schema_version"), dataset, line, record_id)
        valid &= self.identifier(record.get("registry_reference_id"), "registry_reference_id", dataset, line, record_id, "registry_reference_id")
        valid &= self.identifier(record.get("item_id"), "item_id", dataset, line, record_id, "item_id")
        valid &= self.identifier(record.get("final_annotation_id"), "annotation_id", dataset, line, record_id, "final_annotation_id")
        valid &= self.identifier(record.get("registry_reviewer_id"), "registry_reviewer_id", dataset, line, record_id, "registry_reviewer_id")
        valid &= self.identifier(record.get("registry_snapshot_id"), "registry_snapshot_id", dataset, line, record_id, "registry_snapshot_id")
        valid &= self.exact_type(record.get("actor_span_index"), int, dataset, line, record_id, "actor_span_index")
        valid &= self.exact_type(record.get("destination_span_index"), int, dataset, line, record_id, "destination_span_index")
        valid &= self.enum(record.get("label"), REGISTRY_REFERENCE_LABELS, dataset, line, record_id, "label")
        valid &= self.enum(record.get("registry_coverage"), REGISTRY_COVERAGE, dataset, line, record_id, "registry_coverage")
        valid &= self.identifier(record.get("resolver_version"), "resolver_version", dataset, line, record_id, "resolver_version")
        valid &= self.date_value(record.get("created_date"), dataset, line, record_id, "created_date")
        if self.exact_type(record.get("blinding_attestation"), str, dataset, line, record_id, "blinding_attestation"):
            if record["blinding_attestation"] != BLINDING_ATTESTATION:
                self.add("error", "invalid_blinding_attestation", dataset, "The blinding attestation must equal the controlled contract statement.", line=line, record_id=record_id, field="blinding_attestation")
                valid = False
        else:
            valid = False

        evidence_ids = record.get("registry_evidence_ids")
        if self.exact_type(evidence_ids, list, dataset, line, record_id, "registry_evidence_ids"):
            if len(evidence_ids) > MAX_LIST_ITEMS:
                self.add("error", "list_size_limit", dataset, "The registry evidence list exceeds the operational limit.", line=line, record_id=record_id, field="registry_evidence_ids")
                valid = False
            for index, evidence_id in enumerate(evidence_ids):
                valid &= self.identifier(evidence_id, "registry_evidence_id", dataset, line, record_id, f"registry_evidence_ids[{index}]")
            if all(type(value) is str for value in evidence_ids):
                if evidence_ids != sorted(evidence_ids) or len(evidence_ids) != len(set(evidence_ids)):
                    self.add("error", "registry_evidence_order", dataset, "Registry evidence IDs must be sorted and unique.", line=line, record_id=record_id, field="registry_evidence_ids")
                    valid = False
        else:
            valid = False
        return bool(valid)

    def validate_source(
        self, record: dict[str, Any], dataset: str, line: int, record_id: str | None
    ) -> bool:
        fields = {
            "schema_version",
            "source_id",
            "artifact_sha256",
            "provenance",
            "rights",
            "consent",
            "privacy",
            "eligible_partitions",
        }
        valid = self.object_shape(record, fields, dataset, line, record_id, "")
        valid &= self.schema_version(record.get("schema_version"), dataset, line, record_id)
        valid &= self.identifier(record.get("source_id"), "source_id", dataset, line, record_id, "source_id")
        valid &= self.sha256_value(record.get("artifact_sha256"), dataset, line, record_id, "artifact_sha256")

        provenance = record.get("provenance")
        provenance_valid = self.object_shape(
            provenance,
            {"provenance_class", "origin_name", "collected_by", "collected_date"},
            dataset,
            line,
            record_id,
            "provenance",
        )
        if provenance_valid:
            valid &= self.enum(
                provenance["provenance_class"],
                {
                    "tester_donated_authentic",
                    "tester_authored_simulation",
                    "public_authentic",
                    "llm_drafted_human_edited",
                },
                dataset,
                line,
                record_id,
                "provenance.provenance_class",
            )
            valid &= self.nonempty_string(provenance["origin_name"], dataset, line, record_id, "provenance.origin_name")
            valid &= self.nonempty_string(provenance["collected_by"], dataset, line, record_id, "provenance.collected_by")
            valid &= self.date_value(provenance["collected_date"], dataset, line, record_id, "provenance.collected_date")
        else:
            valid = False

        rights = record.get("rights")
        rights_valid = self.object_shape(
            rights,
            {"basis", "license_id", "research_use_permitted"},
            dataset,
            line,
            record_id,
            "rights",
        )
        if rights_valid:
            valid &= self.enum(rights["basis"], {"consent", "contract", "license", "public_domain"}, dataset, line, record_id, "rights.basis")
            valid &= self.nonempty_string(rights["license_id"], dataset, line, record_id, "rights.license_id")
            valid &= self.exact_type(rights["research_use_permitted"], bool, dataset, line, record_id, "rights.research_use_permitted")
        else:
            valid = False

        consent = record.get("consent")
        consent_valid = self.object_shape(
            consent,
            {"status", "scope", "withdrawal_process"},
            dataset,
            line,
            record_id,
            "consent",
        )
        if consent_valid:
            valid &= self.enum(consent["status"], {"granted", "not_applicable", "withdrawn"}, dataset, line, record_id, "consent.status")
            valid &= self.nonempty_string(consent["scope"], dataset, line, record_id, "consent.scope")
            valid &= self.nonempty_string(consent["withdrawal_process"], dataset, line, record_id, "consent.withdrawal_process")
        else:
            valid = False

        privacy = record.get("privacy")
        privacy_valid = self.object_shape(
            privacy,
            {"contains_personal_data", "deidentified", "reviewed"},
            dataset,
            line,
            record_id,
            "privacy",
        )
        if privacy_valid:
            for name in ("contains_personal_data", "deidentified", "reviewed"):
                valid &= self.exact_type(privacy[name], bool, dataset, line, record_id, f"privacy.{name}")
        else:
            valid = False

        partitions = record.get("eligible_partitions")
        if self.exact_type(partitions, list, dataset, line, record_id, "eligible_partitions"):
            if not partitions:
                self.add("error", "empty_list", dataset, "At least one eligible partition is required.", line=line, record_id=record_id, field="eligible_partitions")
                valid = False
            for index, partition in enumerate(partitions):
                valid &= self.enum(partition, PARTITIONS, dataset, line, record_id, f"eligible_partitions[{index}]")
            if all(type(value) is str for value in partitions) and len(partitions) != len(set(partitions)):
                self.add("error", "duplicate_list_value", dataset, "List values must be unique.", line=line, record_id=record_id, field="eligible_partitions")
                valid = False
        else:
            valid = False
        return bool(valid)

    def validate_item(
        self, record: dict[str, Any], dataset: str, line: int, record_id: str | None
    ) -> bool:
        fields = {
            "schema_version",
            "item_id",
            "source_id",
            "text",
            "content_sha256",
            "vmp_sha256",
            "language",
            "language_stratum",
            "partition",
            "exclusion_reasons",
            "visible_artifacts",
            "privacy",
            "generation",
            "leakage_component_id",
            "lineage",
        }
        valid = self.object_shape(record, fields, dataset, line, record_id, "")
        valid &= self.schema_version(record.get("schema_version"), dataset, line, record_id)
        valid &= self.identifier(record.get("item_id"), "item_id", dataset, line, record_id, "item_id")
        valid &= self.identifier(record.get("source_id"), "source_id", dataset, line, record_id, "source_id")
        valid &= self.bounded_string(record.get("text"), MAX_ITEM_TEXT_CHARS, dataset, line, record_id, "text", nonempty=True)
        valid &= self.sha256_value(record.get("content_sha256"), dataset, line, record_id, "content_sha256")
        valid &= self.sha256_value(record.get("vmp_sha256"), dataset, line, record_id, "vmp_sha256")
        valid &= self.enum(record.get("language"), ITEM_LANGUAGES, dataset, line, record_id, "language")
        valid &= self.enum(record.get("language_stratum"), ANNOTATION_LANGUAGE_STRATA, dataset, line, record_id, "language_stratum")
        valid &= self.enum(record.get("partition"), PARTITIONS, dataset, line, record_id, "partition")
        valid &= self.identifier(record.get("leakage_component_id"), "leakage_component_id", dataset, line, record_id, "leakage_component_id")

        exclusion_reasons = record.get("exclusion_reasons")
        if self.exact_type(exclusion_reasons, list, dataset, line, record_id, "exclusion_reasons"):
            for index, reason in enumerate(exclusion_reasons):
                valid &= self.enum(reason, EXCLUSION_REASONS, dataset, line, record_id, f"exclusion_reasons[{index}]")
            if all(type(value) is str for value in exclusion_reasons):
                if exclusion_reasons != sorted(exclusion_reasons) or len(exclusion_reasons) != len(set(exclusion_reasons)):
                    self.add("error", "exclusion_reason_order", dataset, "Exclusion reasons must be sorted and unique.", line=line, record_id=record_id, field="exclusion_reasons")
                    valid = False
        else:
            valid = False

        visible_artifacts = record.get("visible_artifacts")
        text = record.get("text")
        if self.exact_type(visible_artifacts, list, dataset, line, record_id, "visible_artifacts"):
            if len(visible_artifacts) > MAX_VISIBLE_ARTIFACTS:
                self.add("error", "visible_artifact_count", dataset, "The visible-artifact inventory exceeds 64 entries.", line=line, record_id=record_id, field="visible_artifacts")
                valid = False
            order_keys: list[tuple[int, int, bytes, bytes, bytes]] = []
            ranges: list[tuple[int, int]] = []
            for index, artifact in enumerate(visible_artifacts):
                prefix = f"visible_artifacts[{index}]"
                if not self.object_shape(
                    artifact,
                    {"kind", "kind_reason", "representation", "start", "end", "text"},
                    dataset,
                    line,
                    record_id,
                    prefix,
                ):
                    valid = False
                    continue
                kind_valid = self.enum(artifact["kind"], VISIBLE_ARTIFACT_KINDS, dataset, line, record_id, f"{prefix}.kind")
                representation_valid = self.enum(
                    artifact["representation"],
                    VISIBLE_ARTIFACT_REPRESENTATIONS,
                    dataset,
                    line,
                    record_id,
                    f"{prefix}.representation",
                )
                reason_valid = self.bounded_string(
                    artifact["kind_reason"],
                    MAX_RATIONALE_CHARS,
                    dataset,
                    line,
                    record_id,
                    f"{prefix}.kind_reason",
                    nonempty=artifact["kind"] == "OTHER",
                )
                if reason_valid and artifact["kind"] != "OTHER" and artifact["kind_reason"]:
                    self.add("error", "visible_artifact_kind_reason", dataset, "Only OTHER visible artifacts may have a kind reason.", line=line, record_id=record_id, field=f"{prefix}.kind_reason")
                    valid = False
                start_valid = self.exact_type(artifact["start"], int, dataset, line, record_id, f"{prefix}.start")
                end_valid = self.exact_type(artifact["end"], int, dataset, line, record_id, f"{prefix}.end")
                artifact_text_valid = self.exact_type(artifact["text"], str, dataset, line, record_id, f"{prefix}.text")
                valid &= kind_valid and representation_valid and reason_valid and start_valid and end_valid and artifact_text_valid
                if start_valid and end_valid and type(text) is str:
                    start = artifact["start"]
                    end = artifact["end"]
                    if not (0 <= start < end <= len(text)):
                        self.add("error", "visible_artifact_out_of_bounds", dataset, "A visible-artifact range is empty or outside item text.", line=line, record_id=record_id, field=prefix)
                        valid = False
                    elif artifact_text_valid and text[start:end] != artifact["text"]:
                        self.add("error", "visible_artifact_text_mismatch", dataset, "Visible-artifact text does not equal the exact item-text substring.", line=line, record_id=record_id, field=f"{prefix}.text")
                        valid = False
                if kind_valid and representation_valid and artifact_text_valid:
                    representation = artifact["representation"]
                    artifact_text = artifact["text"]
                    coherent = (
                        artifact_text == TYPED_PLACEHOLDERS[artifact["kind"]]
                        if representation == "TYPED_PLACEHOLDER"
                        else RESERVED_ARTIFACT_PATTERN.fullmatch(artifact_text) is not None
                        if representation == "RESERVED"
                        else any(marker in artifact_text for marker in DEFANGING_MARKERS)
                    )
                    if not coherent:
                        self.add("error", "visible_artifact_representation_coherence", dataset, "The visible-artifact surface does not match its declared representation.", line=line, record_id=record_id, field=f"{prefix}.representation")
                        valid = False
                if kind_valid and representation_valid and start_valid and end_valid and artifact_text_valid:
                    order_keys.append(
                        (
                            artifact["start"],
                            artifact["end"],
                            artifact["kind"].encode("utf-8"),
                            artifact["representation"].encode("utf-8"),
                            artifact["text"].encode("utf-8"),
                        )
                    )
                    ranges.append((artifact["start"], artifact["end"]))
            if len(order_keys) == len(visible_artifacts):
                if order_keys != sorted(order_keys):
                    self.add("error", "visible_artifact_order", dataset, "Visible artifacts are not in canonical order.", line=line, record_id=record_id, field="visible_artifacts")
                    valid = False
                if len(order_keys) != len(set(order_keys)):
                    self.add("error", "visible_artifact_duplicate", dataset, "Duplicate visible artifacts are prohibited.", line=line, record_id=record_id, field="visible_artifacts")
                    valid = False
                sorted_ranges = sorted(ranges)
                for prior, current in zip(sorted_ranges, sorted_ranges[1:]):
                    if current[0] < prior[1]:
                        self.add("error", "visible_artifact_overlap", dataset, "Visible artifacts must be pairwise nonoverlapping.", line=line, record_id=record_id, field="visible_artifacts")
                        valid = False
                        break
        else:
            valid = False

        privacy = record.get("privacy")
        privacy_valid = self.object_shape(privacy, {"synthetic", "pii_reviewed", "contains_pii"}, dataset, line, record_id, "privacy")
        if privacy_valid:
            for name in ("synthetic", "pii_reviewed", "contains_pii"):
                valid &= self.exact_type(privacy[name], bool, dataset, line, record_id, f"privacy.{name}")
        else:
            valid = False

        generation = record.get("generation")
        generation_valid = self.object_shape(generation, {"method", "model_id"}, dataset, line, record_id, "generation")
        if generation_valid:
            valid &= self.enum(generation["method"], {"human", "llm", "template", "augmentation"}, dataset, line, record_id, "generation.method")
            valid &= self.nonempty_string(generation["model_id"], dataset, line, record_id, "generation.model_id")
        else:
            valid = False

        lineage = record.get("lineage")
        lineage_valid = self.object_shape(lineage, {"parent_item_ids", "operation"}, dataset, line, record_id, "lineage")
        if lineage_valid:
            valid &= self.enum(lineage["operation"], LINEAGE_OPERATIONS, dataset, line, record_id, "lineage.operation")
            parents = lineage["parent_item_ids"]
            if self.exact_type(parents, list, dataset, line, record_id, "lineage.parent_item_ids"):
                for index, parent in enumerate(parents):
                    valid &= self.identifier(parent, "item_id", dataset, line, record_id, f"lineage.parent_item_ids[{index}]")
                if all(type(value) is str for value in parents) and len(parents) != len(set(parents)):
                    self.add("error", "duplicate_list_value", dataset, "List values must be unique.", line=line, record_id=record_id, field="lineage.parent_item_ids")
                    valid = False
            else:
                valid = False
        else:
            valid = False
        return bool(valid)

    def validate_annotation(
        self, record: dict[str, Any], dataset: str, line: int, record_id: str | None
    ) -> bool:
        fields = {
            "schema_version",
            "annotation_id",
            "item_id",
            "annotator_id",
            "kind",
            "independent",
            "primary_label",
            "subtype",
            "subtype_other_reason",
            "language_stratum",
            "resolution_method",
            "confidence",
            "ambiguity_tags",
            "token_language_spans",
            "code_mix_pair",
            "facets",
            "spans",
            "evidence_span_indices",
            "romanization_ambiguities",
            "created_date",
        }
        valid = self.object_shape(record, fields, dataset, line, record_id, "")
        valid &= self.schema_version(record.get("schema_version"), dataset, line, record_id)
        valid &= self.identifier(record.get("annotation_id"), "annotation_id", dataset, line, record_id, "annotation_id")
        valid &= self.identifier(record.get("item_id"), "item_id", dataset, line, record_id, "item_id")
        valid &= self.identifier(record.get("annotator_id"), "annotator_id", dataset, line, record_id, "annotator_id")
        valid &= self.enum(record.get("kind"), {"blind", "final"}, dataset, line, record_id, "kind")
        valid &= self.exact_type(record.get("independent"), bool, dataset, line, record_id, "independent")
        valid &= self.enum(record.get("primary_label"), LABELS, dataset, line, record_id, "primary_label")
        valid &= self.enum(record.get("subtype"), SUBTYPES, dataset, line, record_id, "subtype")
        valid &= self.bounded_string(record.get("subtype_other_reason"), MAX_RATIONALE_CHARS, dataset, line, record_id, "subtype_other_reason")
        valid &= self.enum(record.get("language_stratum"), ANNOTATION_LANGUAGE_STRATA, dataset, line, record_id, "language_stratum")
        valid &= self.enum(record.get("resolution_method"), {"not_applicable", "adjudicated", "unresolved"}, dataset, line, record_id, "resolution_method")
        valid &= self.enum(record.get("confidence"), {"high", "medium", "low"}, dataset, line, record_id, "confidence")
        valid &= self.enum(record.get("code_mix_pair"), CODE_MIX_PAIRS, dataset, line, record_id, "code_mix_pair")
        valid &= self.date_value(record.get("created_date"), dataset, line, record_id, "created_date")

        ambiguity_tags = record.get("ambiguity_tags")
        if self.exact_type(ambiguity_tags, list, dataset, line, record_id, "ambiguity_tags"):
            for index, tag in enumerate(ambiguity_tags):
                valid &= self.enum(tag, AMBIGUITY_TAGS, dataset, line, record_id, f"ambiguity_tags[{index}]")
            if all(type(value) is str for value in ambiguity_tags) and len(ambiguity_tags) != len(set(ambiguity_tags)):
                self.add("error", "duplicate_list_value", dataset, "List values must be unique.", line=line, record_id=record_id, field="ambiguity_tags")
                valid = False
        else:
            valid = False

        token_spans = record.get("token_language_spans")
        if self.exact_type(token_spans, list, dataset, line, record_id, "token_language_spans"):
            if not token_spans:
                self.add("error", "token_language_required", dataset, "At least one token-language span is required.", line=line, record_id=record_id, field="token_language_spans")
                valid = False
            for index, token_span in enumerate(token_spans):
                prefix = f"token_language_spans[{index}]"
                if not self.object_shape(token_span, {"start", "end", "text", "language", "script"}, dataset, line, record_id, prefix):
                    valid = False
                    continue
                valid &= self.exact_type(token_span["start"], int, dataset, line, record_id, f"{prefix}.start")
                valid &= self.exact_type(token_span["end"], int, dataset, line, record_id, f"{prefix}.end")
                valid &= self.exact_type(token_span["text"], str, dataset, line, record_id, f"{prefix}.text")
                valid &= self.enum(token_span["language"], TOKEN_LANGUAGES, dataset, line, record_id, f"{prefix}.language")
                valid &= self.enum(token_span["script"], SCRIPTS, dataset, line, record_id, f"{prefix}.script")
        else:
            valid = False

        spans = record.get("spans")
        if self.exact_type(spans, list, dataset, line, record_id, "spans"):
            for index, span in enumerate(spans):
                prefix = f"spans[{index}]"
                if not self.object_shape(span, {"start", "end", "text", "facet", "qualifier", "qualifier_reason"}, dataset, line, record_id, prefix):
                    valid = False
                    continue
                valid &= self.exact_type(span["start"], int, dataset, line, record_id, f"{prefix}.start")
                valid &= self.exact_type(span["end"], int, dataset, line, record_id, f"{prefix}.end")
                valid &= self.exact_type(span["text"], str, dataset, line, record_id, f"{prefix}.text")
                valid &= self.enum(span["facet"], SPAN_FACETS, dataset, line, record_id, f"{prefix}.facet")
                valid &= self.exact_type(span["qualifier"], str, dataset, line, record_id, f"{prefix}.qualifier")
                valid &= self.bounded_string(span["qualifier_reason"], MAX_RATIONALE_CHARS, dataset, line, record_id, f"{prefix}.qualifier_reason")
        else:
            valid = False

        facets = record.get("facets")
        if self.exact_type(facets, list, dataset, line, record_id, "facets"):
            for index, facet in enumerate(facets):
                prefix = f"facets[{index}]"
                if not self.object_shape(facet, {"facet", "state", "span_indices"}, dataset, line, record_id, prefix):
                    valid = False
                    continue
                valid &= self.enum(facet["facet"], FACETS, dataset, line, record_id, f"{prefix}.facet")
                valid &= self.enum(facet["state"], FACET_STATES, dataset, line, record_id, f"{prefix}.state")
                indices = facet["span_indices"]
                if self.exact_type(indices, list, dataset, line, record_id, f"{prefix}.span_indices"):
                    for child_index, span_index in enumerate(indices):
                        valid &= self.exact_type(span_index, int, dataset, line, record_id, f"{prefix}.span_indices[{child_index}]")
                else:
                    valid = False
        else:
            valid = False

        evidence = record.get("evidence_span_indices")
        if self.exact_type(evidence, list, dataset, line, record_id, "evidence_span_indices"):
            for index, span_index in enumerate(evidence):
                valid &= self.exact_type(span_index, int, dataset, line, record_id, f"evidence_span_indices[{index}]")
        else:
            valid = False

        ambiguities = record.get("romanization_ambiguities")
        if self.exact_type(ambiguities, list, dataset, line, record_id, "romanization_ambiguities"):
            for index, ambiguity in enumerate(ambiguities):
                prefix = f"romanization_ambiguities[{index}]"
                if not self.object_shape(ambiguity, {"start", "end", "text", "language", "acceptable_forms", "affected_decisions"}, dataset, line, record_id, prefix):
                    valid = False
                    continue
                valid &= self.exact_type(ambiguity["start"], int, dataset, line, record_id, f"{prefix}.start")
                valid &= self.exact_type(ambiguity["end"], int, dataset, line, record_id, f"{prefix}.end")
                valid &= self.exact_type(ambiguity["text"], str, dataset, line, record_id, f"{prefix}.text")
                valid &= self.enum(ambiguity["language"], {"hi", "ta", "te"}, dataset, line, record_id, f"{prefix}.language")
                forms = ambiguity["acceptable_forms"]
                if self.exact_type(forms, list, dataset, line, record_id, f"{prefix}.acceptable_forms"):
                    for form_index, form in enumerate(forms):
                        form_prefix = f"{prefix}.acceptable_forms[{form_index}]"
                        if not self.object_shape(form, {"form", "script", "gloss"}, dataset, line, record_id, form_prefix):
                            valid = False
                            continue
                        valid &= self.nonempty_string(form["form"], dataset, line, record_id, f"{form_prefix}.form")
                        valid &= self.enum(form["script"], SCRIPTS, dataset, line, record_id, f"{form_prefix}.script")
                        valid &= self.nonempty_string(form["gloss"], dataset, line, record_id, f"{form_prefix}.gloss")
                else:
                    valid = False
                decisions = ambiguity["affected_decisions"]
                if self.exact_type(decisions, list, dataset, line, record_id, f"{prefix}.affected_decisions"):
                    for decision_index, decision in enumerate(decisions):
                        valid &= self.enum(decision, AFFECTED_DECISIONS, dataset, line, record_id, f"{prefix}.affected_decisions[{decision_index}]")
                else:
                    valid = False
        else:
            valid = False

        return bool(valid)

    def validate_cross_file(
        self,
    ) -> tuple[
        float | None,
        float | None,
        Agreement,
        Reliability,
        RegistryReferenceInventory,
        int,
        float | None,
    ]:
        self._validate_sources_semantics()
        llm_development_share, llm_pilot_share = self._validate_items_semantics()
        self._validate_annotations_semantics()
        registry_inventory = self._validate_registry_references_semantics()
        agreement, reliability, unresolved_items, unresolved_rate = self._validate_pilot_mechanism()
        return (
            llm_development_share,
            llm_pilot_share,
            agreement,
            reliability,
            registry_inventory,
            unresolved_items,
            unresolved_rate,
        )

    def _validate_sources_semantics(self) -> None:
        for source_id, (line, source) in sorted(self.sources.items()):
            provenance_class = source["provenance"]["provenance_class"]
            rights = source["rights"]
            consent = source["consent"]
            privacy = source["privacy"]
            if not rights["research_use_permitted"]:
                self.add("error", "source_rights_ineligible", "sources", "The source is not permitted for research use.", line=line, record_id=source_id, field="rights.research_use_permitted")
            if consent["status"] == "withdrawn":
                self.add("error", "source_consent_withdrawn", "sources", "The source consent has been withdrawn.", line=line, record_id=source_id, field="consent.status")
            if provenance_class in {"tester_donated_authentic", "tester_authored_simulation"} and consent["status"] != "granted":
                self.add("error", "participant_consent_required", "sources", "Tester-origin data requires granted consent.", line=line, record_id=source_id, field="consent.status")
            if not privacy["reviewed"]:
                self.add("error", "source_privacy_unreviewed", "sources", "The source privacy review is incomplete.", line=line, record_id=source_id, field="privacy.reviewed")
            if privacy["contains_personal_data"] and not privacy["deidentified"]:
                self.add("error", "source_not_deidentified", "sources", "Personal source data must be deidentified.", line=line, record_id=source_id, field="privacy.deidentified")
            eligible = set(source["eligible_partitions"])
            if provenance_class == "public_authentic" and not eligible <= PUBLIC_PARTITIONS:
                self.add("error", "public_source_partition_policy", "sources", "Public sources may declare only development or external-test eligibility.", line=line, record_id=source_id, field="eligible_partitions")
            elif provenance_class == "llm_drafted_human_edited" and eligible & PROTECTED_PARTITIONS:
                self.add("error", "source_protected_eligibility", "sources", "LLM sources cannot declare protected-partition eligibility.", line=line, record_id=source_id, field="eligible_partitions")

    def _validate_items_semantics(self) -> tuple[float | None, float | None]:
        exact_seen: dict[str, str] = {}
        canonical_seen: dict[str, str] = {}
        components: dict[str, list[str]] = defaultdict(list)

        for item_id, (line, item) in sorted(self.items.items()):
            text = item["text"]
            expected_hash = sha256(text.encode("utf-8")).hexdigest()
            if item["content_sha256"] != expected_hash:
                self.add("error", "content_hash_mismatch", "items", "The content hash does not match the exact UTF-8 text.", line=line, record_id=item_id, field="content_sha256")
            expected_vmp_hash = _vmp_sha256(text, item["visible_artifacts"])
            if item["vmp_sha256"] != expected_vmp_hash:
                self.add("error", "vmp_hash_mismatch", "items", "The VMP hash does not match canonical item text and visible artifacts.", line=line, record_id=item_id, field="vmp_sha256")
            expected_language = LANGUAGE_STRATA.get(item["language_stratum"], "unknown")
            if expected_language != item["language"]:
                self.add("error", "language_stratum_mismatch", "items", "The language and language stratum are inconsistent.", line=line, record_id=item_id, field="language_stratum")
            reasons = item["exclusion_reasons"]
            if item["partition"] == "excluded" and not reasons:
                self.add("error", "excluded_reason_required", "items", "Excluded items require at least one exclusion reason.", line=line, record_id=item_id, field="exclusion_reasons")
            if item["partition"] != "excluded" and reasons:
                self.add("error", "unexpected_exclusion_reason", "items", "Non-excluded items require an empty exclusion-reasons list.", line=line, record_id=item_id, field="exclusion_reasons")
            if item["language_stratum"] == "uncertain" and item["partition"] != "excluded":
                self.add("error", "uncertain_language_not_excluded", "items", "An uncertain item language stratum requires partition excluded.", line=line, record_id=item_id, field="language_stratum")
            if not item["privacy"]["pii_reviewed"]:
                self.add("error", "item_privacy_unreviewed", "items", "The item PII review is incomplete.", line=line, record_id=item_id, field="privacy.pii_reviewed")
            if item["privacy"]["contains_pii"]:
                self.add("error", "item_contains_pii", "items", "Items containing PII are prohibited from the dataset snapshot.", line=line, record_id=item_id, field="privacy.contains_pii")

            generation = item["generation"]
            if generation["method"] == "llm" and generation["model_id"] == "none":
                self.add("error", "llm_model_required", "items", "LLM-generated items require a model identifier.", line=line, record_id=item_id, field="generation.model_id")
            if generation["method"] != "llm" and generation["model_id"] != "none":
                self.add("error", "unexpected_model_id", "items", "Non-LLM items must use model identifier 'none'.", line=line, record_id=item_id, field="generation.model_id")

            source_entry = self.sources.get(item["source_id"])
            if source_entry is None:
                self.add("error", "unknown_source", "items", "The referenced source does not exist.", line=line, record_id=item_id, field="source_id")
            else:
                source = source_entry[1]
                if item["partition"] not in source["eligible_partitions"]:
                    self.add("error", "source_partition_ineligible", "items", "The source is not eligible for the assigned partition.", line=line, record_id=item_id, field="partition")
                source_is_llm = source["provenance"]["provenance_class"] == "llm_drafted_human_edited"
                item_is_llm = generation["method"] == "llm"
                if source_is_llm != item_is_llm:
                    self.add("error", "generation_provenance_mismatch", "items", "Item generation and source provenance are inconsistent.", line=line, record_id=item_id, field="generation.method")

            parents = item["lineage"]["parent_item_ids"]
            operation = item["lineage"]["operation"]
            if operation == "original" and parents:
                self.add("error", "original_has_parent", "items", "Original items must not declare parents.", line=line, record_id=item_id, field="lineage.parent_item_ids")
            if operation != "original" and not parents:
                self.add("error", "derived_missing_parent", "items", "Derived items must declare a parent.", line=line, record_id=item_id, field="lineage.parent_item_ids")
            if item_id in parents:
                self.add("error", "self_lineage", "items", "An item cannot be its own parent.", line=line, record_id=item_id, field="lineage.parent_item_ids")
            for parent_id in parents:
                parent_entry = self.items.get(parent_id)
                if parent_entry is None:
                    self.add("error", "unknown_parent_item", "items", "A lineage parent does not exist.", line=line, record_id=item_id, field="lineage.parent_item_ids")
                elif parent_entry[1]["leakage_component_id"] != item["leakage_component_id"]:
                    self.add("error", "lineage_component_mismatch", "items", "Lineage relatives must share the final leakage component identifier.", line=line, record_id=item_id, related_record_id=parent_id, field="leakage_component_id")

            exact_other = exact_seen.get(text)
            if exact_other is not None:
                self.add("error", "exact_duplicate", "items", "The message exactly duplicates another item.", line=line, record_id=item_id, related_record_id=exact_other, field="text")
            else:
                exact_seen[text] = item_id
            canonical = _canonical_text(text)
            canonical_other = canonical_seen.get(canonical)
            if canonical_other is not None and canonical_other != exact_other:
                self.add("error", "canonical_duplicate", "items", "The canonical message duplicates another item.", line=line, record_id=item_id, related_record_id=canonical_other, field="text")
            elif canonical_other is None:
                canonical_seen[canonical] = item_id
            components[item["leakage_component_id"]].append(item_id)

        cycle_items = _lineage_cycle_items(self.items)
        for item_id in sorted(cycle_items):
            self.add("error", "lineage_cycle", "items", "Directed item lineage contains a cycle.", line=self.items[item_id][0], record_id=item_id, field="lineage.parent_item_ids")

        llm_ancestry, public_ancestry = self._ancestry_flags()
        for item_id, (line, item) in sorted(self.items.items()):
            if item["partition"] in PROTECTED_PARTITIONS and llm_ancestry[item_id]:
                self.add("error", "llm_protected_partition", "items", "LLM-assisted ancestry is prohibited from protected partitions.", line=line, record_id=item_id, field="partition")
            if public_ancestry[item_id] and item["partition"] not in PUBLIC_PARTITIONS:
                self.add("error", "public_partition_policy", "items", "Public-source ancestry is permitted only in development or external test.", line=line, record_id=item_id, field="partition")

        for component_id, component_items in sorted(components.items()):
            active_partitions = {
                self.items[item_id][1]["partition"]
                for item_id in component_items
                if self.items[item_id][1]["partition"] != "excluded"
            }
            first_item = sorted(component_items)[0]
            if len(active_partitions) > 1:
                self.add("error", "partition_component_leakage", "items", "A leakage component crosses non-excluded partitions.", line=self.items[first_item][0], record_id=first_item, field="partition")
            if active_partitions & PROTECTED_PARTITIONS and len(component_items) != 1:
                self.add("error", "protected_component_not_singleton", "items", "Protected partitions require globally singleton leakage components.", line=self.items[first_item][0], record_id=first_item, field="leakage_component_id")

        development_ids = [item_id for item_id, (_, item) in self.items.items() if item["partition"] == "development"]
        pilot_ids = [item_id for item_id, (_, item) in self.items.items() if item["partition"] == "pilot"]
        development_share = _share(development_ids, llm_ancestry)
        pilot_share = _share(pilot_ids, llm_ancestry)
        if development_share is not None and development_share > 0.30:
            self.add("error", "llm_development_share", "items", "LLM-assisted ancestry exceeds 30% of development.", field="partition")
        if pilot_share is not None and pilot_share > 0.30:
            self.add("error", "llm_pilot_share", "items", "LLM-assisted ancestry exceeds 30% of retained pilot items.", field="partition")
        return development_share, pilot_share

    def _ancestry_flags(self) -> tuple[dict[str, bool], dict[str, bool]]:
        llm: dict[str, bool] = {}
        public: dict[str, bool] = {}
        for item_id, (_, item) in self.items.items():
            source_entry = self.sources.get(item["source_id"])
            provenance_class = source_entry[1]["provenance"]["provenance_class"] if source_entry else None
            llm[item_id] = item["generation"]["method"] == "llm" or provenance_class == "llm_drafted_human_edited"
            public[item_id] = provenance_class == "public_authentic"
        children: dict[str, list[str]] = defaultdict(list)
        for child_id, (_, item) in self.items.items():
            for parent_id in item["lineage"]["parent_item_ids"]:
                if parent_id in self.items:
                    children[parent_id].append(child_id)

        def propagate(flags: dict[str, bool]) -> None:
            pending = deque(sorted(item_id for item_id, flagged in flags.items() if flagged))
            while pending:
                parent_id = pending.popleft()
                for child_id in children.get(parent_id, ()):
                    if not flags[child_id]:
                        flags[child_id] = True
                        pending.append(child_id)

        propagate(llm)
        propagate(public)
        return llm, public

    def _validate_annotations_semantics(self) -> None:
        for annotation_id, (line, annotation) in sorted(self.annotations.items()):
            self._validate_one_annotation(annotation_id, line, annotation)

    def _validate_registry_references_semantics(self) -> RegistryReferenceInventory:
        if self.registry_references and not self.registry_manifest_supplied:
            self.add(
                "error",
                "registry_manifest_required",
                "registry_references",
                "Registry references require a supplied registry manifest.",
            )
        if self.mode == "pilot-final":
            if not self.registry_manifest_supplied:
                self.add("error", "pilot_registry_manifest_required", "registry_manifest", "Pilot-final requires a supplied registry manifest.")
            if not self.registry_references_supplied:
                self.add("error", "pilot_registry_references_required", "registry_references", "Pilot-final requires a supplied registry-reference artifact, which may be empty only when no endpoint pairs exist.")
            if not any(record[1]["approval_state"] == "approved" for record in self.registry_manifest.values()):
                self.add("error", "pilot_approved_registry_required", "registry_manifest", "Pilot-final requires at least one approved registry snapshot.", field="approval_state")

        final_annotations = {
            annotation_id: annotation
            for annotation_id, (_, annotation) in self.annotations.items()
            if annotation["kind"] == "final"
        }
        annotators_by_item: dict[str, set[str]] = defaultdict(set)
        for _, annotation in self.annotations.values():
            annotators_by_item[annotation["item_id"]].add(annotation["annotator_id"])

        expected_pairs: set[tuple[str, str, int, int]] = set()
        for annotation_id, annotation in final_annotations.items():
            actor_indices = _facet_span_indices(annotation, "claimed_actor")
            destination_indices = _facet_span_indices(annotation, "destination_artifact")
            for actor_index in actor_indices:
                for destination_index in destination_indices:
                    expected_pairs.add((annotation["item_id"], annotation_id, actor_index, destination_index))

        reference_rows = [record for _, record in self.registry_references.values()]
        order_keys = [
            (
                record["item_id"],
                record["final_annotation_id"],
                record["actor_span_index"],
                record["destination_span_index"],
                record["registry_reference_id"],
            )
            for record in reference_rows
        ]
        if order_keys != sorted(order_keys):
            self.add("error", "registry_reference_order", "registry_references", "Registry references must use deterministic item, final-annotation, actor, destination, and reference-ID order.")

        actual_pairs: set[tuple[str, str, int, int]] = set()
        for reference_id, (line, reference) in self.registry_references.items():
            final_annotation = final_annotations.get(reference["final_annotation_id"])
            if final_annotation is None:
                self.add("error", "registry_final_annotation_unknown", "registry_references", "The named annotation is not a final annotation.", line=line, record_id=reference_id, field="final_annotation_id")
            elif final_annotation["item_id"] != reference["item_id"]:
                self.add("error", "registry_item_annotation_mismatch", "registry_references", "The item and final annotation do not match.", line=line, record_id=reference_id, field="item_id", related_record_id=reference["final_annotation_id"])

            if reference["registry_reviewer_id"] in annotators_by_item.get(reference["item_id"], set()):
                self.add("error", "registry_reviewer_not_separate", "registry_references", "The registry reviewer must differ from both blind annotators and the final annotator.", line=line, record_id=reference_id, field="registry_reviewer_id")

            key = (
                reference["item_id"],
                reference["final_annotation_id"],
                reference["actor_span_index"],
                reference["destination_span_index"],
            )
            if key in actual_pairs:
                self.add("error", "duplicate_registry_endpoint_pair", "registry_references", "Each final actor-destination endpoint pair requires exactly one registry reference.", line=line, record_id=reference_id)
            actual_pairs.add(key)

            if final_annotation is not None:
                actor_indices = _facet_span_indices(final_annotation, "claimed_actor")
                destination_indices = _facet_span_indices(final_annotation, "destination_artifact")
                if reference["actor_span_index"] not in actor_indices:
                    self.add("error", "registry_actor_endpoint", "registry_references", "The actor endpoint is not an explicit claimed_actor span in the named final annotation.", line=line, record_id=reference_id, field="actor_span_index")
                if reference["destination_span_index"] not in destination_indices:
                    self.add("error", "registry_destination_endpoint", "registry_references", "The destination endpoint is not an explicit destination_artifact span in the named final annotation.", line=line, record_id=reference_id, field="destination_span_index")

            manifest = self.registry_manifest.get(reference["registry_snapshot_id"])
            if manifest is None:
                self.add("error", "registry_snapshot_unbound", "registry_references", "The registry snapshot is not declared in the supplied manifest.", line=line, record_id=reference_id, field="registry_snapshot_id")
            elif self.mode == "pilot-final" and manifest[1]["approval_state"] != "approved":
                self.add("error", "pilot_registry_snapshot_not_approved", "registry_references", "Every pilot-final registry reference must bind an approved registry snapshot.", line=line, record_id=reference_id, field="registry_snapshot_id")

            label = reference["label"]
            coverage = reference["registry_coverage"]
            evidence_ids = reference["registry_evidence_ids"]
            if label in {"MATCH", "MISMATCH"}:
                if coverage != "complete" or not evidence_ids:
                    self.add("error", "registry_decisive_reference_incomplete", "registry_references", "MATCH and MISMATCH require complete coverage and at least one registry evidence ID.", line=line, record_id=reference_id)
                if manifest is None or manifest[1]["approval_state"] != "approved":
                    self.add("error", "registry_snapshot_not_approved", "registry_references", "MATCH and MISMATCH require an approved bound registry snapshot.", line=line, record_id=reference_id, field="registry_snapshot_id")
            elif coverage not in {"partial", "missing"}:
                self.add("error", "registry_unknown_coverage", "registry_references", "UNKNOWN requires partial or missing registry coverage.", line=line, record_id=reference_id, field="registry_coverage")

        if self.registry_references_supplied:
            missing_pairs = expected_pairs - actual_pairs
            extra_pairs = actual_pairs - expected_pairs
            if missing_pairs:
                self.add("error", "registry_reference_missing", "registry_references", "One or more final actor-destination endpoint pairs have no registry reference.")
            if extra_pairs:
                self.add("error", "registry_reference_extra", "registry_references", "One or more registry references do not match a final actor-destination endpoint pair.")

        coverage_counts = Counter(record["registry_coverage"] for record in reference_rows)
        label_counts = Counter(record["label"] for record in reference_rows)
        return RegistryReferenceInventory(
            applicable_endpoint_pairs=len(expected_pairs),
            reference_records=len(reference_rows),
            complete=coverage_counts["complete"],
            partial=coverage_counts["partial"],
            missing=coverage_counts["missing"],
            match=label_counts["MATCH"],
            mismatch=label_counts["MISMATCH"],
            unknown=label_counts["UNKNOWN"],
            zero_applicable_pairs=not expected_pairs,
        )

    def _validate_one_annotation(
        self, annotation_id: str, line: int, annotation: dict[str, Any]
    ) -> None:
        item_entry = self.items.get(annotation["item_id"])
        if item_entry is None:
            self.add("error", "unknown_item", "annotations", "The referenced item does not exist.", line=line, record_id=annotation_id, field="item_id")
            return
        item = item_entry[1]
        text = item["text"]

        if annotation["kind"] == "blind" and not annotation["independent"]:
            self.add("error", "blind_not_independent", "annotations", "Blind annotations must be independent.", line=line, record_id=annotation_id, field="independent")
        if annotation["kind"] == "final" and annotation["independent"]:
            self.add("error", "final_marked_independent", "annotations", "Final annotations must not be marked independent.", line=line, record_id=annotation_id, field="independent")
        if annotation["kind"] == "blind" and annotation["resolution_method"] != "not_applicable":
            self.add("error", "blind_resolution_method", "annotations", "Blind annotations use resolution_method not_applicable.", line=line, record_id=annotation_id, field="resolution_method")
        if annotation["kind"] == "final" and annotation["primary_label"] == "uncertain" and annotation["resolution_method"] != "unresolved":
            self.add("error", "uncertain_resolution_method", "annotations", "Uncertain final annotations use resolution_method unresolved.", line=line, record_id=annotation_id, field="resolution_method")
        if annotation["kind"] == "final" and annotation["primary_label"] in BINARY_LABELS and annotation["resolution_method"] != "adjudicated":
            self.add("error", "final_resolution_method", "annotations", "Binary final annotations use resolution_method adjudicated.", line=line, record_id=annotation_id, field="resolution_method")
        if annotation["primary_label"] == "benign" and annotation["subtype"] == "not_applicable":
            self.add("error", "benign_subtype", "annotations", "Benign annotations require a benign subtype.", line=line, record_id=annotation_id, field="subtype")
        if annotation["primary_label"] != "benign" and annotation["subtype"] != "not_applicable":
            self.add("error", "nonbenign_subtype", "annotations", "Non-benign annotations use subtype not_applicable.", line=line, record_id=annotation_id, field="subtype")
        requires_subtype_reason = annotation["primary_label"] == "benign" and annotation["subtype"] == "other"
        if requires_subtype_reason != bool(annotation["subtype_other_reason"]):
            self.add("error", "subtype_other_reason", "annotations", "A subtype OTHER rationale is required exactly when benign subtype is other.", line=line, record_id=annotation_id, field="subtype_other_reason")
        if annotation["primary_label"] == "uncertain" and not annotation["ambiguity_tags"]:
            self.add("error", "uncertain_ambiguity_required", "annotations", "Uncertain annotations require an ambiguity tag.", line=line, record_id=annotation_id, field="ambiguity_tags")
        if annotation["language_stratum"] == "uncertain" and "language" not in annotation["ambiguity_tags"]:
            self.add("error", "uncertain_language_ambiguity", "annotations", "An uncertain language stratum requires the language ambiguity tag.", line=line, record_id=annotation_id, field="ambiguity_tags")

        token_keys: list[tuple[int, int, str, str]] = []
        declared_inventory: list[tuple[int, int]] = []
        for index, token_span in enumerate(annotation["token_language_spans"]):
            start = token_span["start"]
            end = token_span["end"]
            key = (start, end, token_span["language"], token_span["script"])
            token_keys.append(key)
            declared_inventory.append((start, end))
            if start < 0 or end <= start or end > len(text):
                self.add("error", "token_span_out_of_bounds", "annotations", "A token-language span is empty or out of bounds.", line=line, record_id=annotation_id, field=f"token_language_spans[{index}]")
            elif text[start:end] != token_span["text"]:
                self.add("error", "token_span_text_mismatch", "annotations", "Token span text does not equal the exact raw substring.", line=line, record_id=annotation_id, field=f"token_language_spans[{index}].text")
            if 0 <= start < end <= len(text) and token_span["script"] != _observed_script(text[start:end]):
                self.add("error", "token_script_mismatch", "annotations", "The declared token script does not match the observed Unicode script.", line=line, record_id=annotation_id, field=f"token_language_spans[{index}].script")
        if token_keys != sorted(token_keys) or len(token_keys) != len(set(token_keys)):
            self.add("error", "token_spans_order", "annotations", "Token-language spans must be sorted and unique.", line=line, record_id=annotation_id, field="token_language_spans")
        machine_inventory = _letter_mark_inventory(text)
        if declared_inventory != machine_inventory:
            self.add("error", "token_inventory_mismatch", "annotations", "Token-language spans must exactly cover the machine lexical-token inventory once.", line=line, record_id=annotation_id, field="token_language_spans")

        derived_stratum, derived_pair = _derive_language_stratum(annotation["token_language_spans"])
        if annotation["language_stratum"] != derived_stratum:
            self.add("error", "derived_language_stratum_mismatch", "annotations", "The annotation language stratum does not match all lexical-token counts.", line=line, record_id=annotation_id, field="language_stratum")
        if annotation["code_mix_pair"] != derived_pair:
            self.add("error", "code_mix_pair", "annotations", "The code-mix pair does not match all lexical-token counts.", line=line, record_id=annotation_id, field="code_mix_pair")
        if annotation["kind"] == "final" and annotation["language_stratum"] != "uncertain":
            if annotation["language_stratum"] != item["language_stratum"]:
                self.add("error", "final_language_item_mismatch", "annotations", "The final language stratum must match item metadata.", line=line, record_id=annotation_id, field="language_stratum")

        spans = annotation["spans"]
        visible_artifacts = {
            (artifact["start"], artifact["end"], artifact["text"]): artifact["kind"]
            for artifact in item["visible_artifacts"]
        }
        span_keys: list[tuple[int, int, str, str]] = []
        for index, span in enumerate(spans):
            start = span["start"]
            end = span["end"]
            facet = span["facet"]
            qualifier = span["qualifier"]
            span_keys.append((start, end, facet, qualifier))
            if start < 0 or end <= start or end > len(text):
                self.add("error", "span_out_of_bounds", "annotations", "A facet span is empty or out of bounds.", line=line, record_id=annotation_id, field=f"spans[{index}]")
            elif text[start:end] != span["text"]:
                self.add("error", "span_text_mismatch", "annotations", "Span text does not equal the exact raw substring.", line=line, record_id=annotation_id, field=f"spans[{index}].text")
            if facet == "destination_artifact":
                if qualifier not in DESTINATION_QUALIFIERS:
                    self.add("error", "destination_qualifier", "annotations", "Destination spans require a destination qualifier.", line=line, record_id=annotation_id, field=f"spans[{index}].qualifier")
                artifact_kind = visible_artifacts.get((start, end, span["text"]))
                if artifact_kind is None:
                    self.add("error", "destination_visible_artifact_mismatch", "annotations", "An explicit destination span must exactly match one item visible artifact.", line=line, record_id=annotation_id, field=f"spans[{index}]")
                elif qualifier != artifact_kind:
                    self.add("error", "destination_artifact_kind_mismatch", "annotations", "A destination qualifier must equal the matched visible-artifact kind.", line=line, record_id=annotation_id, field=f"spans[{index}].qualifier")
            elif facet == "pressure_tactic" and qualifier not in PRESSURE_QUALIFIERS:
                self.add("error", "pressure_qualifier", "annotations", "Pressure spans require a pressure qualifier.", line=line, record_id=annotation_id, field=f"spans[{index}].qualifier")
            elif facet not in {"destination_artifact", "pressure_tactic"} and qualifier != "N/A":
                self.add("error", "unexpected_span_qualifier", "annotations", "This facet span must use qualifier N/A.", line=line, record_id=annotation_id, field=f"spans[{index}].qualifier")
            if (qualifier == "OTHER") != bool(span["qualifier_reason"]):
                self.add("error", "qualifier_reason", "annotations", "A qualifier OTHER rationale is required exactly when qualifier is OTHER.", line=line, record_id=annotation_id, field=f"spans[{index}].qualifier_reason")
        if span_keys != sorted(span_keys) or len(span_keys) != len(set(span_keys)):
            self.add("error", "spans_order", "annotations", "Facet spans must be sorted and unique.", line=line, record_id=annotation_id, field="spans")

        facet_by_name: dict[str, dict[str, Any]] = {}
        referenced_facet_spans: set[int] = set()
        for index, facet in enumerate(annotation["facets"]):
            facet_name = facet["facet"]
            if facet_name in facet_by_name:
                self.add("error", "duplicate_facet", "annotations", "Each structured facet must occur exactly once.", line=line, record_id=annotation_id, field="facets")
            facet_by_name[facet_name] = facet
            indices = facet["span_indices"]
            if indices != sorted(indices) or len(indices) != len(set(indices)):
                self.add("error", "facet_span_order", "annotations", "Facet span indices must be sorted and unique.", line=line, record_id=annotation_id, field=f"facets[{index}].span_indices")
            if facet["state"] == "explicit" and not indices:
                self.add("error", "explicit_facet_missing_span", "annotations", "Explicit facets require at least one span.", line=line, record_id=annotation_id, field=f"facets[{index}].span_indices")
            if facet["state"] != "explicit" and indices:
                self.add("error", "inapplicable_facet_has_span", "annotations", "Non-explicit facets cannot reference spans.", line=line, record_id=annotation_id, field=f"facets[{index}].span_indices")
            for span_index in indices:
                if span_index < 0 or span_index >= len(spans):
                    self.add("error", "invalid_facet_span_reference", "annotations", "A facet references a missing span.", line=line, record_id=annotation_id, field=f"facets[{index}].span_indices")
                elif spans[span_index]["facet"] != facet_name:
                    self.add("error", "facet_span_mismatch", "annotations", "A facet span reference has the wrong facet type.", line=line, record_id=annotation_id, field=f"facets[{index}].span_indices")
                else:
                    referenced_facet_spans.add(span_index)
        if set(facet_by_name) != FACETS:
            self.add("error", "facet_inventory", "annotations", "The annotation must contain every structured facet exactly once.", line=line, record_id=annotation_id, field="facets")
        declared_facet_spans = {index for index, span in enumerate(spans) if span["facet"] in FACETS}
        if declared_facet_spans != referenced_facet_spans:
            self.add("error", "orphan_facet_span", "annotations", "Every structured facet span must be referenced exactly once.", line=line, record_id=annotation_id, field="spans")

        if annotation["primary_label"] == "phishing" and set(facet_by_name) == FACETS:
            if facet_by_name["requested_action"]["state"] == "not_applicable":
                self.add("error", "phishing_action_applicability", "annotations", "Phishing annotations require requested-action applicability.", line=line, record_id=annotation_id, field="facets.requested_action")
            if facet_by_name["sensitive_item_or_asset"]["state"] == "not_applicable":
                self.add("error", "phishing_asset_applicability", "annotations", "Phishing annotations require sensitive-item applicability.", line=line, record_id=annotation_id, field="facets.sensitive_item_or_asset")
            coherent_facets = {
                "requested_action",
                "sensitive_item_or_asset",
                "destination_artifact",
                "claimed_actor",
                "claim_or_problem",
            }
            if not any(facet_by_name[name]["state"] == "explicit" for name in coherent_facets):
                self.add("error", "phishing_semantically_empty", "annotations", "A phishing annotation requires at least one explicit coherence facet.", line=line, record_id=annotation_id, field="facets")

        evidence = annotation["evidence_span_indices"]
        self._validate_evidence_indices(annotation_id, line, evidence, spans, "evidence_span_indices")
        if annotation["primary_label"] in BINARY_LABELS and not evidence:
            self.add("error", "binary_evidence_required", "annotations", "Binary annotations require supporting evidence.", line=line, record_id=annotation_id, field="evidence_span_indices")

        ambiguity_keys: list[tuple[int, int, str]] = []
        for index, ambiguity in enumerate(annotation["romanization_ambiguities"]):
            start = ambiguity["start"]
            end = ambiguity["end"]
            ambiguity_keys.append((start, end, ambiguity["language"]))
            if start < 0 or end <= start or end > len(text):
                self.add("error", "romanization_span_out_of_bounds", "annotations", "A Romanization ambiguity span is invalid.", line=line, record_id=annotation_id, field=f"romanization_ambiguities[{index}]")
            elif text[start:end] != ambiguity["text"]:
                self.add("error", "romanization_text_mismatch", "annotations", "Romanization text does not equal the exact raw substring.", line=line, record_id=annotation_id, field=f"romanization_ambiguities[{index}].text")
            elif _observed_script(text[start:end]) != "latin":
                self.add("error", "romanization_source_script", "annotations", "A Romanization ambiguity source span must use observed Latin script.", line=line, record_id=annotation_id, field=f"romanization_ambiguities[{index}].text")
            forms = ambiguity["acceptable_forms"]
            form_keys = [(_canonical_text(form["form"]), form["script"]) for form in forms]
            if len(forms) < 2 or len(form_keys) != len(set(form_keys)):
                self.add("error", "romanization_forms", "annotations", "Romanization ambiguity requires at least two unique acceptable forms.", line=line, record_id=annotation_id, field=f"romanization_ambiguities[{index}].acceptable_forms")
            for form_index, form in enumerate(forms):
                if _observed_script(form["form"]) != form["script"]:
                    self.add("error", "romanization_form_script", "annotations", "An acceptable form's declared script must match its observed Unicode script.", line=line, record_id=annotation_id, field=f"romanization_ambiguities[{index}].acceptable_forms[{form_index}].script")
            decisions = ambiguity["affected_decisions"]
            if not decisions or decisions != sorted(decisions) or len(decisions) != len(set(decisions)):
                self.add("error", "romanization_decisions", "annotations", "Affected decisions must be nonempty, sorted, and unique.", line=line, record_id=annotation_id, field=f"romanization_ambiguities[{index}].affected_decisions")
        if ambiguity_keys != sorted(ambiguity_keys) or len(ambiguity_keys) != len(set(ambiguity_keys)):
            self.add("error", "romanization_order", "annotations", "Romanization ambiguity spans must be sorted and unique.", line=line, record_id=annotation_id, field="romanization_ambiguities")
        has_romanization_tag = "romanization" in annotation["ambiguity_tags"]
        if bool(annotation["romanization_ambiguities"]) != has_romanization_tag:
            self.add("error", "romanization_tag", "annotations", "Romanization records and the romanization ambiguity tag must agree.", line=line, record_id=annotation_id, field="ambiguity_tags")

    def _validate_evidence_indices(
        self,
        annotation_id: str,
        line: int,
        indices: list[int],
        spans: list[dict[str, Any]],
        field: str,
    ) -> None:
        if indices != sorted(indices) or len(indices) != len(set(indices)):
            self.add("error", "evidence_order", "annotations", "Evidence indices must be sorted and unique.", line=line, record_id=annotation_id, field=field)
        for span_index in indices:
            if span_index < 0 or span_index >= len(spans):
                self.add("error", "invalid_evidence_reference", "annotations", "Evidence references a missing span.", line=line, record_id=annotation_id, field=field)
            elif spans[span_index]["facet"] != "supporting_evidence":
                self.add("error", "evidence_facet_required", "annotations", "Evidence must reference supporting_evidence spans.", line=line, record_id=annotation_id, field=field)

    def _validate_pilot_mechanism(
        self,
    ) -> tuple[Agreement, Reliability, int, float | None]:
        by_item: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for annotation_id, (_, annotation) in self.annotations.items():
            annotation_copy = dict(annotation)
            annotation_copy["_annotation_id"] = annotation_id
            by_item[annotation["item_id"]].append(annotation_copy)

        completeness_severity = "error" if self.mode == "pilot-final" else "warning"
        retained_ids = sorted(item_id for item_id, (_, item) in self.items.items() if item["partition"] == "pilot")
        excluded_ids = sorted(item_id for item_id, (_, item) in self.items.items() if item["partition"] == "excluded")
        attempted_ids = retained_ids + excluded_ids
        attempted_set = set(attempted_ids)
        if self.mode == "pilot-final" and set(self.items) - attempted_set:
            self.add("error", "pilot_final_partition", "items", "Pilot-final permits only pilot and excluded partitions.", field="partition")

        blind_pairs: dict[str, tuple[dict[str, Any], dict[str, Any]]] = {}
        final_by_item: dict[str, dict[str, Any]] = {}
        valid_final_items: set[str] = set()
        complete_items = 0
        for item_id in sorted(self.items):
            annotations = by_item.get(item_id, [])
            blind = sorted((record for record in annotations if record["kind"] == "blind"), key=lambda record: (record["annotator_id"], record["_annotation_id"]))
            finals = sorted((record for record in annotations if record["kind"] == "final"), key=lambda record: record["_annotation_id"])
            if len(blind) != 2:
                self.add(completeness_severity, "blind_annotation_count", "annotations", "Each item requires exactly two blind annotations.", record_id=item_id, field="kind")
            if len(finals) != 1:
                self.add(completeness_severity, "final_annotation_count", "annotations", "Each item requires exactly one final annotation.", record_id=item_id, field="kind")
            valid_blind = False
            if len(blind) == 2:
                if len({record["annotator_id"] for record in blind}) != 2:
                    self.add("error", "blind_annotator_not_distinct", "annotations", "Blind annotations require distinct annotators.", record_id=item_id, field="annotator_id")
                elif all(record["independent"] for record in blind) and all(record["_annotation_id"] not in self.invalid_annotations for record in blind):
                    blind_pairs[item_id] = (blind[0], blind[1])
                    valid_blind = True
            if len(finals) == 1:
                final = finals[0]
                final_by_item[item_id] = final
                final_state_valid = True
                third_annotator = not any(record["annotator_id"] == final["annotator_id"] for record in blind)
                if not third_annotator:
                    self.add("error", "final_annotator_not_third", "annotations", "The final annotator must differ from both blind annotators.", record_id=item_id, field="annotator_id")
                item = self.items[item_id][1]
                reasons = set(item["exclusion_reasons"])
                if final["primary_label"] == "uncertain" and item["partition"] != "excluded":
                    self.add("error", "unresolved_not_excluded", "annotations", "An unresolved final primary label requires partition excluded.", record_id=item_id, field="primary_label")
                    final_state_valid = False
                if final["language_stratum"] == "uncertain" and item["partition"] != "excluded":
                    self.add("error", "unresolved_language_not_excluded", "annotations", "An unresolved final language stratum requires partition excluded.", record_id=item_id, field="language_stratum")
                    final_state_valid = False
                if item["partition"] == "excluded" and self.mode == "pilot-final":
                    expected: set[str] = set()
                    if final["primary_label"] == "uncertain":
                        expected.add("unresolved_primary_label")
                    if final["language_stratum"] == "uncertain":
                        expected.add("unresolved_language_stratum")
                    if reasons != expected or not expected:
                        self.add("error", "excluded_resolution_mismatch", "annotations", "Pilot-final exclusion reasons must exactly match unresolved final decisions.", record_id=item_id, field="exclusion_reasons")
                        final_state_valid = False
                if third_annotator and final_state_valid and final["_annotation_id"] not in self.invalid_annotations:
                    valid_final_items.add(item_id)
                if item_id in attempted_set and valid_blind and item_id in valid_final_items:
                    complete_items += 1

        if self.mode == "pilot-final":
            for item_id in excluded_ids:
                reasons = set(self.items[item_id][1]["exclusion_reasons"])
                if not reasons <= PILOT_EXCLUSION_REASONS:
                    self.add("error", "pilot_exclusion_reason", "items", "Pilot-final exclusions permit only unresolved decision reasons.", record_id=item_id, field="exclusion_reasons")

        if len(retained_ids) != 1200:
            self.add(completeness_severity, "pilot_item_count", "items", "Pilot-final requires exactly 1,200 retained pilot items.", field="partition")
        stratum_counts = Counter(self.items[item_id][1]["language_stratum"] for item_id in retained_ids)
        if any(stratum_counts[stratum] != 300 for stratum in LANGUAGE_STRATA) or sum(stratum_counts.values()) != sum(stratum_counts[stratum] for stratum in LANGUAGE_STRATA):
            self.add(completeness_severity, "pilot_stratum_balance", "items", "Retained pilot items require exactly 300 items per study language stratum.", field="language_stratum")

        final_balance: Counter[tuple[str, str]] = Counter()
        for item_id in retained_ids:
            final = final_by_item.get(item_id)
            if item_id in valid_final_items and final is not None and final["primary_label"] in BINARY_LABELS and final["language_stratum"] in LANGUAGE_STRATA:
                final_balance[(final["language_stratum"], final["primary_label"])] += 1
        if any(final_balance[(stratum, label)] != 150 for stratum in LANGUAGE_STRATA for label in BINARY_LABELS):
            self.add(completeness_severity, "pilot_label_balance", "annotations", "Final pilot decisions require 150 benign and 150 phishing items per study stratum.", field="primary_label")

        unresolved_items = len(excluded_ids)
        unresolved_rate = unresolved_items / len(attempted_ids) if attempted_ids else None
        if self.mode == "pilot-final" and (unresolved_rate is None or unresolved_rate > 0.05):
            self.add("error", "unresolved_rate_gate", "annotations", "The excluded attempted-item rate exceeds 5% or is undefined.", field="exclusion_reasons")

        valid_attempted_pairs = {item_id: pair for item_id, pair in blind_pairs.items() if item_id in attempted_set}
        binary_pairs = {item_id: pair for item_id, pair in valid_attempted_pairs.items() if all(record["primary_label"] in BINARY_LABELS for record in pair)}
        coverage = len(binary_pairs) / len(attempted_ids) if attempted_ids else None
        label_units = [[pair[0]["primary_label"], pair[1]["primary_label"]] for _, pair in sorted(binary_pairs.items())]
        agreements = sum(left == right for left, right in label_units)
        agreement = Agreement(len(label_units), agreements, agreements / len(label_units) if label_units else None, _cohen_kappa(label_units), _nominal_alpha(label_units))

        language_units = [[pair[0]["language_stratum"], pair[1]["language_stratum"]] for _, pair in sorted(valid_attempted_pairs.items())]
        language_agreements = sum(left == right for left, right in language_units)
        language_agreement = LanguageAgreement(len(language_units), language_agreements, language_agreements / len(language_units) if language_units else None, _nominal_alpha(language_units))

        facet_alpha_overall = {
            facet: _nominal_alpha([[_facet_state(pair[0], facet), _facet_state(pair[1], facet)] for _, pair in sorted(valid_attempted_pairs.items())])
            for facet in sorted(FACETS)
        }
        named_metrics = {
            "claimed_actor": lambda record: _facet_signature(record, "claimed_actor"),
            "requested_action": lambda record: _facet_signature(record, "requested_action"),
            "destination_artifact": lambda record: _facet_signature(record, "destination_artifact"),
        }
        per_stratum_alpha: dict[str, dict[str, float | None]] = {}
        for stratum in sorted(LANGUAGE_STRATA):
            pairs = [
                pair
                for item_id, pair in sorted(valid_attempted_pairs.items())
                if item_id in valid_final_items
                and final_by_item[item_id]["language_stratum"] == stratum
            ]
            per_stratum_alpha[stratum] = {name: _nominal_alpha([[rating(pair[0]), rating(pair[1])] for pair in pairs]) for name, rating in named_metrics.items()}

        facet_exact: dict[str, float | None] = {}
        facet_overlap: dict[str, float | None] = {}
        for facet in sorted(FACETS):
            relevant = [(pair, _facet_ranges(pair[0], facet), _facet_ranges(pair[1], facet)) for pair in valid_attempted_pairs.values()]
            relevant = [(pair, left, right) for pair, left, right in relevant if left or right]
            facet_exact[facet] = _mean(_set_f1(left, right) for _, left, right in relevant)
            facet_overlap[facet] = _mean(_set_f1(_covered_characters(left), _covered_characters(right)) for _, left, right in relevant)

        evidence_pairs = [(pair, _evidence_ranges(pair[0]), _evidence_ranges(pair[1])) for pair in binary_pairs.values()]
        evidence_pairs = [(pair, left, right) for pair, left, right in evidence_pairs if left or right]
        evidence_exact = _mean(_set_f1(left, right) for _, left, right in evidence_pairs)
        evidence_overlap = _mean(_set_f1(_covered_characters(left), _covered_characters(right)) for _, left, right in evidence_pairs)
        endpoint_pairs = [
            (_endpoint_pair_structures(pair[0]), _endpoint_pair_structures(pair[1]))
            for pair in valid_attempted_pairs.values()
        ]
        endpoint_pairs = [(left, right) for left, right in endpoint_pairs if left or right]
        endpoint_pair_exact = _mean(_set_f1(left, right) for left, right in endpoint_pairs)
        completeness = complete_items / len(attempted_ids) if attempted_ids else None
        reliability = Reliability(
            binary_pair_coverage=coverage,
            language_agreement=language_agreement,
            facet_alpha_overall=facet_alpha_overall,
            per_stratum_alpha=per_stratum_alpha,
            facet_span_exact_f1=facet_exact,
            facet_span_character_overlap_f1=facet_overlap,
            endpoint_pair_structure_exact_f1=endpoint_pair_exact,
            supporting_evidence_exact_f1=evidence_exact,
            supporting_evidence_character_overlap_f1=evidence_overlap,
            completeness=completeness,
        )

        if self.mode == "pilot-final":
            self._enforce_pilot_reliability(agreement, reliability)
        return agreement, reliability, unresolved_items, unresolved_rate

    def _enforce_pilot_reliability(
        self, agreement: Agreement, reliability: Reliability
    ) -> None:
        self._metric_gate("binary_pair_coverage_gate", reliability.binary_pair_coverage, 0.95, "Binary blind-pair coverage must be at least 95%.")
        self._metric_gate("raw_agreement_gate", agreement.raw_agreement, 0.90, "Raw binary agreement must be at least 90%.")
        self._metric_gate("label_alpha_gate", agreement.krippendorff_alpha, 0.80, "Binary nominal Krippendorff alpha must be at least 0.80.")
        self._metric_gate("language_alpha_gate", reliability.language_agreement.krippendorff_alpha, 0.80, "Five-state language-stratum nominal alpha must be at least 0.80.", field="reliability.language_agreement")
        for facet_name, value in sorted(reliability.facet_alpha_overall.items()):
            self._metric_gate("facet_alpha_gate", value, 0.67, "Every overall facet nominal alpha must be at least 0.67.", field=f"facets.{facet_name}")
        for stratum, values in sorted(reliability.per_stratum_alpha.items()):
            for metric, value in sorted(values.items()):
                self._metric_gate("stratum_alpha_gate", value, 0.60, "Named per-stratum nominal alpha must be at least 0.60.", field=f"reliability.{stratum}.{metric}")
        for facet, value in sorted(reliability.facet_span_exact_f1.items()):
            self._metric_gate("facet_span_exact_f1_gate", value, 0.60, "Every structured-facet exact-span F1 must be at least 0.60.", field=f"reliability.facet_span_exact_f1.{facet}")
        for facet, value in sorted(reliability.facet_span_character_overlap_f1.items()):
            self._metric_gate("facet_span_overlap_f1_gate", value, 0.75, "Every structured-facet character-overlap F1 must be at least 0.75.", field=f"reliability.facet_span_character_overlap_f1.{facet}")
        self._metric_gate("endpoint_pair_structure_exact_f1_gate", reliability.endpoint_pair_structure_exact_f1, 0.60, "Endpoint-pair structure exact F1 must be at least 0.60.", field="reliability.endpoint_pair_structure_exact_f1")
        self._metric_gate("supporting_evidence_overlap_f1_gate", reliability.supporting_evidence_character_overlap_f1, 0.75, "Supporting-evidence character-overlap F1 must be at least 0.75.")
        self._metric_gate("supporting_evidence_exact_f1_gate", reliability.supporting_evidence_exact_f1, 0.60, "Supporting-evidence exact-span F1 must be at least 0.60.")
        self._metric_gate("completeness_gate", reliability.completeness, 0.95, "Attempted-item annotation-bundle completeness must be at least 95%.")

    def _metric_gate(
        self,
        code: str,
        value: float | None,
        minimum: float,
        message: str,
        *,
        field: str = "reliability",
    ) -> None:
        if value is None or value < minimum:
            self.add("error", code, "annotations", message, field=field)

    def report(
        self,
        llm_development_share: float | None,
        llm_pilot_share: float | None,
        agreement: Agreement,
        reliability: Reliability,
        registry_reference_inventory: RegistryReferenceInventory,
        unresolved_items: int,
        unresolved_rate: float | None,
    ) -> ValidationReport:
        severity_order = {"error": 0, "warning": 1}
        diagnostics = tuple(
            sorted(
                self.diagnostics,
                key=lambda diagnostic: (
                    severity_order[diagnostic.severity],
                    diagnostic.dataset,
                    diagnostic.line if diagnostic.line is not None else -1,
                    diagnostic.code,
                    diagnostic.record_id or "",
                    diagnostic.field or "",
                    diagnostic.related_record_id or "",
                ),
            )
        )
        errors = sum(diagnostic.severity == "error" for diagnostic in diagnostics)
        warnings = sum(diagnostic.severity == "warning" for diagnostic in diagnostics)
        return ValidationReport(
            mode=self.mode,
            valid=errors == 0,
            counts={
                "sources": len(self.sources),
                "items": len(self.items),
                "annotations": len(self.annotations),
                "registry_manifest": len(self.registry_manifest),
                "registry_references": len(self.registry_references),
            },
            errors=errors,
            warnings=warnings,
            llm_development_share=llm_development_share,
            llm_pilot_share=llm_pilot_share,
            unresolved_final_items=unresolved_items,
            unresolved_final_rate=unresolved_rate,
            agreement=agreement,
            reliability=reliability,
            registry_reference_inventory=registry_reference_inventory,
            diagnostics=diagnostics,
        )


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKeyError
        result[key] = value
    return result


def _reject_nonfinite_number(value: str) -> None:
    raise ValueError(value)


def _has_forbidden_control(value: str) -> bool:
    return any(ord(character) < 32 and character not in "\t\n\r" for character in value)


def _string_hazards(value: Any) -> set[str]:
    hazards: set[str] = set()
    stack = [value]
    while stack:
        current = stack.pop()
        if type(current) is str:
            if any(0xD800 <= ord(character) <= 0xDFFF for character in current):
                hazards.add("surrogate")
            if _has_forbidden_control(current):
                hazards.add("control")
            if any(ord(character) in BIDI_CONTROL_CODEPOINTS for character in current):
                hazards.add("bidi")
        elif type(current) is dict:
            stack.extend(current.keys())
            stack.extend(current.values())
        elif type(current) is list:
            stack.extend(current)
    return hazards


def _structure_limit_error(value: Any) -> str | None:
    stack: list[tuple[Any, int]] = [(value, 1)]
    while stack:
        current, depth = stack.pop()
        if type(current) is dict:
            if depth > MAX_NESTING_DEPTH:
                return "nesting_depth_limit"
            if len(current) > MAX_LIST_ITEMS:
                return "container_size_limit"
            stack.extend((child, depth + 1) for child in current.values())
        elif type(current) is list:
            if depth > MAX_NESTING_DEPTH:
                return "nesting_depth_limit"
            if len(current) > MAX_LIST_ITEMS:
                return "container_size_limit"
            stack.extend((child, depth + 1) for child in current)
    return None


def _valid_id(kind: str, value: str) -> bool:
    return ID_PATTERNS[kind].fullmatch(value) is not None


def _is_safe_record_id(value: str | None) -> bool:
    if value is None or type(value) is not str:
        return False
    return any(pattern.fullmatch(value) is not None for pattern in ID_PATTERNS.values())


def _canonical_text(text: str) -> str:
    return " ".join(unicodedata.normalize("NFKC", text).casefold().split())


def _vmp_sha256(text: str, visible_artifacts: list[dict[str, Any]]) -> str:
    canonical = json.dumps(
        {"text": text, "visible_artifacts": visible_artifacts},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return sha256(canonical.encode("utf-8")).hexdigest()


def _letter_mark_inventory(text: str) -> list[tuple[int, int]]:
    inventory: list[tuple[int, int]] = []
    start: int | None = None
    for index, character in enumerate(text):
        lexical = unicodedata.category(character)[0] in {"L", "M"}
        if lexical and start is None:
            start = index
        elif not lexical and start is not None:
            inventory.append((start, index))
            start = None
    if start is not None:
        inventory.append((start, len(text)))
    return inventory


def _observed_script(text: str) -> str:
    scripts: set[str] = set()
    unsupported_letter = False
    for character in text:
        category = unicodedata.category(character)[0]
        if category not in {"L", "M"}:
            continue
        name = unicodedata.name(character, "")
        if "DEVANAGARI" in name:
            scripts.add("devanagari")
        elif "TAMIL" in name:
            scripts.add("tamil")
        elif "TELUGU" in name:
            scripts.add("telugu")
        elif "LATIN" in name:
            scripts.add("latin")
        elif category == "L":
            unsupported_letter = True
    return next(iter(scripts)) if not unsupported_letter and len(scripts) == 1 else "other"


def _derive_language_stratum(token_spans: list[dict[str, Any]]) -> tuple[str, str]:
    counts: Counter[str] = Counter(span["language"] for span in token_spans)
    total = sum(counts.values())
    if not total:
        return "uncertain", "none"
    proportions = {language: counts[language] / total for language in TOKEN_LANGUAGES}
    present_indic = [language for language in ("hi", "ta", "te") if counts[language] > 0]
    if len(present_indic) == 1:
        indic = present_indic[0]
        if (
            proportions["en"] >= 0.20
            and proportions[indic] >= 0.20
            and proportions["en"] < 0.70
            and proportions[indic] < 0.70
        ):
            return "english_indic_code_mixed", f"en_{indic}"
    for language, stratum in (("hi", "hindi"), ("ta", "tamil"), ("te", "telugu")):
        if proportions[language] >= 0.70:
            return stratum, "none"
    return "uncertain", "none"


def _reserved_host(value: str) -> bool:
    candidate = value.casefold().rstrip(".,;:!?)]}\"")
    if "://" in candidate:
        candidate = candidate.split("://", 1)[1]
    if candidate.startswith("www."):
        candidate = candidate[4:]
    candidate = candidate.split("/", 1)[0].split(":", 1)[0]
    return candidate.rsplit(".", 1)[-1] in RESERVED_TLDS if "." in candidate else False


def _reserved_email(value: str) -> bool:
    address = value.casefold().removeprefix("mailto:").rstrip(".,;:!?)]}\"")
    domain = address.rsplit("@", 1)[-1]
    return domain.rsplit(".", 1)[-1] in RESERVED_TLDS if "." in domain else False


def _contains_live_artifact(text: str) -> bool:
    text = text.translate(
        {0x2024: ord("."), 0x3002: ord("."), 0xFE52: ord("."), 0xFF0E: ord("."), 0xFF61: ord(".")}
    )
    if PHONE_PATTERN.search(text):
        return True
    if UPI_HANDLE_PATTERN.search(text):
        return True
    for match in IPV6_CANDIDATE_PATTERN.finditer(text):
        candidate = match.group(1).rstrip(".")
        try:
            ipaddress.IPv6Address(candidate)
        except ipaddress.AddressValueError:
            continue
        return True
    for match in IPV4_PATTERN.finditer(text):
        if all(0 <= int(part) <= 255 for part in match.group(0).split(".")):
            return True
    if any(not _reserved_email(match.group(0)) for match in EMAIL_PATTERN.finditer(text)):
        return True
    if any(not _reserved_email(match.group(0)) for match in MAILTO_PATTERN.finditer(text)):
        return True
    if any(not _reserved_host(match.group(0)) for match in URL_PATTERN.finditer(text)):
        return True
    if any(not _reserved_host(match.group(0)) for match in DOMAIN_PATTERN.finditer(text)):
        return True
    for token in re.findall(r"[^\s<>]+", text):
        candidate = token.strip("\"'(),;:!?{}")
        if "[.]" in candidate:
            continue
        if candidate.count("@") == 1:
            local, host = candidate.rsplit("@", 1)
            if local and _idna_host_is_live(host):
                return True
        elif "://" not in candidate and "/" not in candidate and _idna_host_is_live(candidate):
            return True
    return False


def _idna_host_is_live(value: str) -> bool:
    host = value.casefold().rstrip(".")
    labels = host.split(".")
    if len(labels) < 2 or any(not label for label in labels):
        return False
    try:
        ascii_labels = [label.encode("idna").decode("ascii") for label in labels]
    except UnicodeError:
        return False
    if any(re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", label) is None for label in ascii_labels):
        return False
    tld = ascii_labels[-1]
    if tld in RESERVED_TLDS:
        return False
    return tld.startswith("xn--") or (len(tld) >= 2 and any(character.isalpha() for character in tld))


def _object_contains_live_artifact(value: Any) -> bool:
    stack = [value]
    while stack:
        current = stack.pop()
        if type(current) is str and _contains_live_artifact(current):
            return True
        if type(current) is dict:
            stack.extend(current.values())
        elif type(current) is list:
            stack.extend(current)
    return False


def _object_contains_sensitive_artifact(value: Any) -> bool:
    stack = [value]
    while stack:
        current = stack.pop()
        if type(current) is str and SECRET_VALUE_PATTERN.search(current):
            return True
        if type(current) is dict:
            stack.extend(current.keys())
            stack.extend(current.values())
        elif type(current) is list:
            stack.extend(current)
    return False


def _lineage_cycle_items(
    items: dict[str, tuple[int, dict[str, Any]]]
) -> set[str]:
    state: dict[str, int] = {item_id: 0 for item_id in items}
    cycle_items: set[str] = set()
    for start_id in sorted(items):
        if state[start_id] != 0:
            continue
        path = [start_id]
        path_index = {start_id: 0}
        state[start_id] = 1
        frames: list[tuple[str, Any]] = [
            (start_id, iter(items[start_id][1]["lineage"]["parent_item_ids"]))
        ]
        while frames:
            item_id, parents = frames[-1]
            try:
                parent_id = next(parents)
            except StopIteration:
                frames.pop()
                state[item_id] = 2
                path_index.pop(item_id, None)
                path.pop()
                continue
            if parent_id not in items:
                continue
            if state[parent_id] == 0:
                state[parent_id] = 1
                path_index[parent_id] = len(path)
                path.append(parent_id)
                frames.append(
                    (parent_id, iter(items[parent_id][1]["lineage"]["parent_item_ids"]))
                )
            elif state[parent_id] == 1:
                cycle_items.update(path[path_index[parent_id] :])
    return cycle_items


def _share(item_ids: list[str], flags: dict[str, bool]) -> float | None:
    if not item_ids:
        return None
    return sum(flags[item_id] for item_id in item_ids) / len(item_ids)


def _facet_state(annotation: dict[str, Any], facet_name: str) -> str:
    for facet in annotation["facets"]:
        if facet["facet"] == facet_name:
            return facet["state"]
    return "missing"


def _facet_ranges(annotation: dict[str, Any], facet_name: str) -> set[tuple[int, int]]:
    for facet in annotation["facets"]:
        if facet["facet"] == facet_name and facet["state"] == "explicit":
            return {(annotation["spans"][index]["start"], annotation["spans"][index]["end"]) for index in facet["span_indices"]}
    return set()


def _facet_span_indices(annotation: dict[str, Any], facet_name: str) -> set[int]:
    for facet in annotation["facets"]:
        if facet["facet"] == facet_name and facet["state"] == "explicit":
            return set(facet["span_indices"])
    return set()


def _facet_signature(annotation: dict[str, Any], facet_name: str) -> str:
    ranges = sorted(_facet_ranges(annotation, facet_name))
    return json.dumps([_facet_state(annotation, facet_name), ranges], separators=(",", ":"))


def _endpoint_pair_structures(
    annotation: dict[str, Any],
) -> set[tuple[int, int, int, int]]:
    actor_ranges = _facet_ranges(annotation, "claimed_actor")
    destination_ranges = _facet_ranges(annotation, "destination_artifact")
    return {
        (actor_start, actor_end, destination_start, destination_end)
        for actor_start, actor_end in actor_ranges
        for destination_start, destination_end in destination_ranges
    }


def _nominal_alpha(units: list[list[str]]) -> float | None:
    usable = [unit for unit in units if len(unit) >= 2]
    if not usable:
        return None
    observed_pairs = 0
    observed_disagreements = 0
    pooled: Counter[str] = Counter()
    for unit in usable:
        for left_index in range(len(unit)):
            for right_index in range(left_index + 1, len(unit)):
                observed_pairs += 1
                observed_disagreements += unit[left_index] != unit[right_index]
        pooled.update(unit)
    if observed_pairs == 0:
        return None
    total = sum(pooled.values())
    if total < 2:
        return None
    observed = observed_disagreements / observed_pairs
    expected_agreement = sum(count * (count - 1) for count in pooled.values()) / (total * (total - 1))
    expected_disagreement = 1.0 - expected_agreement
    if expected_disagreement == 0.0:
        return None
    return 1.0 - observed / expected_disagreement


def _cohen_kappa(units: list[list[str]]) -> float | None:
    if not units:
        return None
    observed = sum(unit[0] == unit[1] for unit in units) / len(units)
    left = Counter(unit[0] for unit in units)
    right = Counter(unit[1] for unit in units)
    expected = sum((left[label] / len(units)) * (right[label] / len(units)) for label in BINARY_LABELS)
    return None if expected == 1.0 else (observed - expected) / (1.0 - expected)


def _evidence_ranges(annotation: dict[str, Any]) -> set[tuple[int, int]]:
    return {
        (annotation["spans"][index]["start"], annotation["spans"][index]["end"])
        for index in annotation["evidence_span_indices"]
        if 0 <= index < len(annotation["spans"])
    }


def _covered_characters(ranges: set[tuple[int, int]]) -> set[int]:
    return {position for start, end in ranges for position in range(start, end)}


def _set_f1(left: set[Any], right: set[Any]) -> float:
    if not left and not right:
        return 1.0
    if not left or not right:
        return 0.0
    return 2.0 * len(left & right) / (len(left) + len(right))


def _mean(values: Iterable[float]) -> float | None:
    collected = list(values)
    return sum(collected) / len(collected) if collected else None


def validate_files(
    sources_path: str | Path,
    items_path: str | Path,
    annotations_path: str | Path,
    mode: str,
    registry_manifest_path: str | Path | None = None,
    registry_references_path: str | Path | None = None,
) -> ValidationReport:
    """Validate a Fisher v1.2 JSONL file set and optional registry artifacts."""

    validator = _Validator(
        mode,
        registry_manifest_supplied=registry_manifest_path is not None,
        registry_references_supplied=registry_references_path is not None,
    )
    if registry_manifest_path is not None:
        validator.registry_manifest = validator.load(
            Path(registry_manifest_path),
            "registry_manifest",
            "registry_snapshot_id",
            validator.validate_registry_manifest,
        )
    if registry_references_path is not None:
        validator.registry_references = validator.load(
            Path(registry_references_path),
            "registry_references",
            "registry_reference_id",
            validator.validate_registry_reference,
        )
    validator.sources = validator.load(Path(sources_path), "sources", "source_id", validator.validate_source)
    validator.items = validator.load(Path(items_path), "items", "item_id", validator.validate_item)
    validator.annotations = validator.load(Path(annotations_path), "annotations", "annotation_id", validator.validate_annotation)
    (
        llm_development_share,
        llm_pilot_share,
        agreement,
        reliability,
        registry_reference_inventory,
        unresolved_items,
        unresolved_rate,
    ) = validator.validate_cross_file()
    return validator.report(
        llm_development_share,
        llm_pilot_share,
        agreement,
        reliability,
        registry_reference_inventory,
        unresolved_items,
        unresolved_rate,
    )


def format_json(report: ValidationReport) -> str:
    """Return deterministic machine-readable report JSON."""

    return json.dumps(report.to_dict(), ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def format_text(report: ValidationReport) -> str:
    """Return a deterministic text report that never quotes message content."""

    status = "VALID" if report.valid else "INVALID"
    lines = [
        (
            f"{status} mode={report.mode} sources={report.counts['sources']} "
            f"items={report.counts['items']} annotations={report.counts['annotations']} "
            f"registry_manifest={report.counts['registry_manifest']} "
            f"registry_references={report.counts['registry_references']} "
            f"errors={report.errors} warnings={report.warnings}"
        ),
        (
            "AGREEMENT "
            f"paired_items={report.agreement.paired_items} "
            f"raw={_metric_text(report.agreement.raw_agreement)} "
            f"kappa={_metric_text(report.agreement.cohen_kappa)} "
            f"alpha={_metric_text(report.agreement.krippendorff_alpha)} "
            f"coverage={_metric_text(report.reliability.binary_pair_coverage)}"
        ),
        (
            "LANGUAGE "
            f"paired_items={report.reliability.language_agreement.paired_items} "
            f"raw={_metric_text(report.reliability.language_agreement.raw_agreement)} "
            f"alpha={_metric_text(report.reliability.language_agreement.krippendorff_alpha)}"
        ),
        (
            "PILOT "
            f"unresolved_items={report.unresolved_final_items} "
            f"unresolved_rate={_metric_text(report.unresolved_final_rate)} "
            f"completeness={_metric_text(report.reliability.completeness)} "
            f"endpoint_pair_exact_f1={_metric_text(report.reliability.endpoint_pair_structure_exact_f1)} "
            f"evidence_exact_f1={_metric_text(report.reliability.supporting_evidence_exact_f1)} "
            f"evidence_overlap_f1={_metric_text(report.reliability.supporting_evidence_character_overlap_f1)}"
        ),
        (
            "REGISTRY_REFERENCES "
            f"applicable_pairs={report.registry_reference_inventory.applicable_endpoint_pairs} "
            f"records={report.registry_reference_inventory.reference_records} "
            f"complete={report.registry_reference_inventory.complete} "
            f"partial={report.registry_reference_inventory.partial} "
            f"missing={report.registry_reference_inventory.missing} "
            f"match={report.registry_reference_inventory.match} "
            f"mismatch={report.registry_reference_inventory.mismatch} "
            f"unknown={report.registry_reference_inventory.unknown} "
            f"zero_applicable_pairs={str(report.registry_reference_inventory.zero_applicable_pairs).lower()}"
        ),
    ]
    for diagnostic in report.diagnostics:
        context = [f"dataset={diagnostic.dataset}"]
        if diagnostic.line is not None:
            context.append(f"line={diagnostic.line}")
        if diagnostic.record_id is not None:
            context.append(f"record={diagnostic.record_id}")
        if diagnostic.related_record_id is not None:
            context.append(f"related={diagnostic.related_record_id}")
        if diagnostic.field is not None:
            context.append(f"field={diagnostic.field}")
        lines.append(f"{diagnostic.severity.upper()} {diagnostic.code} {' '.join(context)}: {diagnostic.message}")
    return "\n".join(lines)


def _metric_text(value: float | None) -> str:
    return "undefined" if value is None else f"{value:.6f}"
