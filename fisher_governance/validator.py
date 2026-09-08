"""Strict, deterministic validator for Fisher's governance source ledger.

The module validates the executable projection frozen in SOURCE_LEDGER.md.  It
does not authenticate human evidence and therefore never grants collection
authorization by itself.
"""

from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass
from datetime import date, datetime
import ipaddress
import json
import os
from pathlib import Path
import re
import stat
from typing import Any
from urllib.parse import urlsplit


SCHEMA_VERSION = "1.0.0"
MAX_FILE_BYTES = 512 * 1024 * 1024
MAX_LINE_CHARS = 1_000_000
MAX_RECORDS = 10_000
MAX_CONTAINER_ITEMS = 10_000
MAX_NESTING_DEPTH = 32
MAX_SHORT_TEXT = 500
MAX_LONG_TEXT = 2_000

SOURCE_ID_PATTERN = re.compile(r"src_[a-z0-9][a-z0-9_-]{0,62}\Z")
OPAQUE_ID_PATTERN = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}\Z")
HASH_PATTERN = re.compile(r"[0-9a-f]{64}\Z")
EVIDENCE_NOTE_PATTERN = re.compile(r"(?:OBSERVED|DERIVED|ASSUMED|UNKNOWN): .+\Z", re.DOTALL)
SAFE_METADATA_PATTERN = re.compile(r"[A-Za-z0-9_.\[\]-]{1,200}\Z")
RFC3339_PATTERN = re.compile(
    r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})\Z"
)
URL_PATTERN = re.compile(r"(?i)(?:https?://|ftp://|www\.)[^\s<>]+")
MAILTO_PATTERN = re.compile(r"(?i)mailto:[^\s<>]+")
EMAIL_PATTERN = re.compile(
    r"(?iu)(?<![A-Za-z0-9.])[^\s@<>]+@(?:[^\W_](?:[\w-]{0,61}[^\W_])?\.)+[^\W\d_]{2,63}\b"
)
PHONE_PATTERN = re.compile(r"(?<![A-Za-z0-9])(?:\+\d{1,3}[ .()-]*)?(?:\d[ .()-]*){10,15}(?![A-Za-z0-9])")
DOMAIN_PATTERN = re.compile(
    r"(?iu)(?<![@A-Za-z0-9.-])(?:[^\W_](?:[\w-]{0,61}[^\W_])?\.)+[^\W\d_]{2,63}\b"
)
IPV4_PATTERN = re.compile(r"(?<![A-Za-z0-9.])(?:\d{1,3}\.){3}\d{1,3}(?![A-Za-z0-9.])")
SECRET_VALUE_PATTERN = re.compile(
    r"(?i)(?<![A-Za-z0-9])(?:otp|pin|password|passcode|credential|recovery[ _-]?code)"
    r"\s*[:=]\s*[A-Za-z0-9!@$^*._-]{4,}(?![A-Za-z0-9])"
)
DNS_LABEL_PATTERN = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\Z")
URL_PATH_PATTERN = re.compile(r"/[A-Za-z0-9._~/-]*\Z")
RESERVED_TLDS = {"example", "invalid", "test"}
OFFICIAL_URL_PATHS = {("origin", "landing_page"), ("license", "text_url")}
BIDI_CONTROL_CODEPOINTS = {
    0x061C, 0x200E, 0x200F, 0x202A, 0x202B, 0x202C, 0x202D, 0x202E,
    0x2066, 0x2067, 0x2068, 0x2069,
}

PROVENANCE_CLASSES = {
    "TESTER_DONATED_AUTHENTIC",
    "TESTER_AUTHORED_SIMULATION",
    "PUBLIC_AUTHENTIC_AUXILIARY",
    "LLM_DRAFTED_HUMAN_EDITED",
}
AUTHENTICITY = {"AUTHENTIC", "SIMULATED", "LLM_ASSISTED"}
EXPECTED_AUTHENTICITY = {
    "TESTER_DONATED_AUTHENTIC": "AUTHENTIC",
    "TESTER_AUTHORED_SIMULATION": "SIMULATED",
    "PUBLIC_AUTHENTIC_AUXILIARY": "AUTHENTIC",
    "LLM_DRAFTED_HUMAN_EDITED": "LLM_ASSISTED",
}
LIFECYCLE_STATES = {
    "PROPOSED", "BLOCKED", "AUTHORIZED", "INGESTED", "REJECTED", "WITHDRAWN"
}
ACTIVE_LIFECYCLE_STATES = {"AUTHORIZED", "INGESTED"}
AUTHORIZATION_STATES = {"BLOCKED", "APPROVED", "REJECTED"}
CONSENT_STATES = {"NOT_STARTED", "APPROVED", "NOT_APPLICABLE", "WITHDRAWN"}
ETHICS_STATES = {"UNKNOWN", "PENDING", "APPROVED", "EXEMPT", "REJECTED"}
LICENSE_STATES = {"UNKNOWN", "PENDING", "VERIFIED", "INCOMPATIBLE", "NOT_APPLICABLE"}
RELEASE_TIERS = {
    "NO_RELEASE", "AGGREGATES_ONLY", "DERIVED_ONLY", "DEIDENTIFIED_TEXT",
    "PUBLIC_TEXT", "UNKNOWN",
}
AUDIT_STATES = {"NOT_STARTED", "PENDING", "PASSED", "FAILED", "NOT_APPLICABLE"}
FINAL_AUDIT_STATES = {"PASSED", "NOT_APPLICABLE"}
LANGUAGE_SCOPES = {
    "HINDI_DOMINANT", "TAMIL_DOMINANT", "TELUGU_DOMINANT", "EN_INDIC_CODE_MIXED"
}
CONTENT_SCOPES = {"MESSAGE_TEXT", "URL", "DOMAIN", "PHONE", "UPI", "BANK", "EMAIL", "APP", "OTHER"}
PARTITIONS = (
    "pilot", "unassigned", "development", "probability_calibration",
    "safety_threshold", "primary_test", "external_test", "excluded",
)
PUBLIC_PARTITIONS = {"development", "external_test"}
PROTECTED_PARTITIONS = {"probability_calibration", "safety_threshold", "primary_test"}
LLM_FRACTION_SCOPES = {"COUNTS_TOWARD_DEVELOPMENT_AND_PILOT_CAPS", "NOT_APPLICABLE"}

TOP_FIELDS = {
    "schema_version", "source_id", "source_name", "description", "provenance_class",
    "authenticity", "lifecycle_status", "blockers", "origin", "artifact_hash",
    "expected_record_count", "audited_record_count", "language_scope", "content_scope",
    "authorization", "consent", "ethics", "license", "release_tier", "privacy_review",
    "safety_review", "quality_audits", "lineage", "equivalence_policy",
    "partition_eligibility", "llm_fraction_scope", "steward", "created_at", "updated_at",
    "decision_notes",
}


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
class HumanGate:
    code: str
    state: str
    representation: str
    reason: str


@dataclass(frozen=True)
class SourceReadiness:
    source_id: str
    lifecycle_status: str
    machine_authorization_ready: bool
    readiness_state: str


@dataclass(frozen=True)
class ValidationReport:
    schema_version: str
    schema_valid: bool
    collection_ready: bool
    readiness_state: str
    counts: dict[str, int]
    errors: int
    warnings: int
    source_readiness: tuple[SourceReadiness, ...]
    not_machine_verifiable: tuple[HumanGate, ...]
    diagnostics: tuple[Diagnostic, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "collection_ready": self.collection_ready,
            "counts": self.counts,
            "diagnostics": [asdict(value) for value in self.diagnostics],
            "errors": self.errors,
            "not_machine_verifiable": [asdict(value) for value in self.not_machine_verifiable],
            "readiness_state": self.readiness_state,
            "schema_valid": self.schema_valid,
            "schema_version": self.schema_version,
            "source_readiness": [asdict(value) for value in self.source_readiness],
            "warnings": self.warnings,
        }


class _DuplicateKeyError(ValueError):
    pass


HUMAN_GATES = (
    HumanGate(
        "ethics_authority_truth", "UNKNOWN", "REFERENCE_ONLY",
        "Machine checks can require ethics references but cannot authenticate the authority or determination.",
    ),
    HumanGate(
        "data_controller_accountability", "UNKNOWN", "NOT_REPRESENTED",
        "The full ledger has no structured data-controller or accountable-institution field.",
    ),
    HumanGate(
        "secure_storage_jurisdiction", "UNKNOWN", "NOT_REPRESENTED",
        "Storage location, jurisdiction, access controls, backup behavior, and vendor controls are not structured fields.",
    ),
    HumanGate(
        "consent_material_quality", "UNKNOWN", "REFERENCE_ONLY",
        "A document reference cannot prove understandable, voluntary, activity-specific consent or adult eligibility.",
    ),
    HumanGate(
        "retention_deletion_policy", "UNKNOWN", "NOT_REPRESENTED",
        "Raw/deidentified retention, backup expiry, deletion evidence, and model implications are not structured fields.",
    ),
    HumanGate(
        "withdrawal_cutoff_controls", "UNKNOWN", "REFERENCE_ONLY",
        "A policy reference cannot prove the approved cutoff, controlled mapping, or operational withdrawal process.",
    ),
    HumanGate(
        "incident_contact_drill", "UNKNOWN", "NOT_REPRESENTED",
        "The monitored incident contact, secure escalation channel, procedure, and synthetic drill evidence are not structured fields.",
    ),
    HumanGate(
        "native_reviewer_signoff", "UNKNOWN", "NOT_REPRESENTED",
        "Native-language reviewer identity, qualification, workload, coverage-cell audit, and sign-off are external.",
    ),
    HumanGate(
        "annotator_welfare", "UNKNOWN", "NOT_REPRESENTED",
        "Compensation, exposure limits, breaks, support, and conflicts are not structured fields.",
    ),
    HumanGate(
        "equivalence_secret_management", "UNKNOWN", "REFERENCE_ONLY",
        "Opaque policy references cannot prove key custody, secret storage, rotation, destruction, or access logging.",
    ),
    HumanGate(
        "license_and_official_source_truth", "UNKNOWN", "REFERENCE_ONLY",
        "URL, reviewer, and decision fields cannot prove officialness, completeness, license rights, or legal compatibility.",
    ),
    HumanGate(
        "privacy_safety_review_truth", "UNKNOWN", "REFERENCE_ONLY",
        "Status fields cannot prove PII absence, correct defanging, residual risk, or two-person review quality.",
    ),
    HumanGate(
        "append_only_history_and_hash_immutability", "UNKNOWN", "NOT_REPRESENTED",
        "One ledger snapshot cannot prove append-only corrections or that earlier artifact hashes were never changed.",
    ),
    HumanGate(
        "structured_coverage_manifest", "UNKNOWN", "NOT_REPRESENTED",
        "The separate component-aware coverage manifest and native audit are intentionally outside this schema.",
    ),
    HumanGate(
        "provenance_and_lineage_truth", "UNKNOWN", "REFERENCE_ONLY",
        "Source classes, parent links, family IDs, and ancestry flags cannot prove real-world provenance or complete lineage.",
    ),
    HumanGate(
        "artifact_hash_version_binding", "UNKNOWN", "REFERENCE_ONLY",
        "Hash syntax cannot prove that the digest was computed from the claimed artifact and version.",
    ),
    HumanGate(
        "source_count_and_acquisition_time_truth", "UNKNOWN", "REFERENCE_ONLY",
        "Count and timestamp syntax cannot prove measured counts or the actual acquisition time.",
    ),
    HumanGate(
        "reviewer_steward_identity_authority", "UNKNOWN", "REFERENCE_ONLY",
        "Names or role references cannot authenticate reviewer/steward identity, qualification, independence, or authority.",
    ),
    HumanGate(
        "opaque_id_nonidentifiability", "UNKNOWN", "REFERENCE_ONLY",
        "Safe identifier syntax cannot prove that an opaque value is random, nonidentifying, or unlinkable outside scope.",
    ),
    HumanGate(
        "llm_material_human_editing", "UNKNOWN", "NOT_REPRESENTED",
        "The ledger has no structured evidence that every LLM draft received material human editing before retention.",
    ),
)


class _Validator:
    def __init__(self) -> None:
        self.diagnostics: list[Diagnostic] = []
        self.records: dict[str, tuple[int, dict[str, Any]]] = {}
        self.invalid_ids: set[str] = set()
        self.machine_ready: set[str] = set()

    def add(
        self,
        severity: str,
        code: str,
        message: str,
        *,
        line: int | None = None,
        record_id: str | None = None,
        field: str | None = None,
        related_record_id: str | None = None,
    ) -> None:
        safe_code = code if SAFE_METADATA_PATTERN.fullmatch(code) else "validation_error"
        safe_field = field if field is not None and SAFE_METADATA_PATTERN.fullmatch(field) else None
        safe_record_id = record_id if _safe_source_id(record_id) else None
        safe_related_id = related_record_id if _safe_source_id(related_record_id) else None
        self.diagnostics.append(
            Diagnostic(
                severity=severity if severity in {"error", "warning"} else "error",
                code=safe_code,
                dataset="ledger",
                message=message if not _forbidden_control(message) else "Validation failed.",
                line=line if type(line) is int and line > 0 else None,
                record_id=safe_record_id,
                field=safe_field,
                related_record_id=safe_related_id,
            )
        )
        if severity == "error" and safe_record_id is not None:
            self.invalid_ids.add(safe_record_id)

    def load(self, path: Path) -> None:
        captured: bytes
        try:
            metadata = path.stat()
            if not stat.S_ISREG(metadata.st_mode):
                self.add("error", "not_regular_file", "The ledger input must be a regular file.")
                return
            if metadata.st_size > MAX_FILE_BYTES:
                self.add("error", "file_size_limit", "The JSONL file exceeds the operational size limit.")
                return
            flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NONBLOCK", 0)
            descriptor = os.open(path, flags)
            try:
                opened_metadata = os.fstat(descriptor)
                if not stat.S_ISREG(opened_metadata.st_mode):
                    self.add("error", "not_regular_file", "The ledger input must be a regular file.")
                    return
                if opened_metadata.st_size > MAX_FILE_BYTES:
                    self.add("error", "file_size_limit", "The JSONL file exceeds the operational size limit.")
                    return
                chunks: list[bytes] = []
                captured_bytes = 0
                while True:
                    read_limit = min(64 * 1024, MAX_FILE_BYTES + 1 - captured_bytes)
                    chunk = os.read(descriptor, read_limit)
                    if not chunk:
                        break
                    chunks.append(chunk)
                    captured_bytes += len(chunk)
                    if captured_bytes > MAX_FILE_BYTES:
                        self.add("error", "file_size_limit", "The JSONL file exceeds the operational size limit.")
                        return
                captured = b"".join(chunks)
            finally:
                os.close(descriptor)
        except FileNotFoundError:
            self.add("error", "file_not_found", "The required JSONL file was not found.")
            return
        except OSError:
            self.add("error", "file_read_error", "The required JSONL file could not be read.")
            return

        try:
            decoded = captured.decode("utf-8")
        except UnicodeDecodeError:
            self.add("error", "invalid_utf8", "The file is not valid UTF-8.")
            return

        physical_lines = decoded.split("\n") if decoded else []
        if decoded.endswith("\n"):
            physical_lines.pop()
        for line_number, raw_line in enumerate(physical_lines, start=1):
            if line_number > MAX_RECORDS:
                self.add("error", "record_count_limit", "The JSONL file exceeds the operational record-count limit.")
                break
            if len(raw_line) > MAX_LINE_CHARS:
                self.add("error", "line_length_limit", "A JSONL line exceeds the operational length limit.", line=line_number)
                continue
            self._load_line(raw_line, line_number)

    def _load_line(self, raw_line: str, line: int) -> None:
        if not raw_line.strip():
            self.add("error", "blank_line", "Blank lines are not permitted.", line=line)
            return
        try:
            value = json.loads(
                raw_line,
                object_pairs_hook=_reject_duplicate_keys,
                parse_constant=_reject_nonfinite_number,
            )
        except _DuplicateKeyError:
            self.add("error", "duplicate_json_key", "A JSON object contains a duplicate key.", line=line)
            return
        except (json.JSONDecodeError, ValueError, RecursionError):
            self.add("error", "invalid_json", "The line is not strict JSON.", line=line)
            return
        hazards = _string_hazards(value)
        if "surrogate" in hazards:
            self.add("error", "forbidden_surrogate", "Escaped surrogate code points are prohibited.", line=line)
        if "control" in hazards:
            self.add("error", "forbidden_control", "Prohibited C0 control characters are present.", line=line)
        if "bidi" in hazards:
            self.add("error", "forbidden_bidi_control", "Bidirectional formatting controls are prohibited.", line=line)
        if hazards:
            return
        structure_error = _structure_limit_error(value)
        if structure_error is not None:
            self.add("error", structure_error, "The record exceeds an operational structure limit.", line=line)
            return
        if type(value) is not dict:
            self.add("error", "record_not_object", "Each line must contain one JSON object.", line=line)
            return
        if _object_contains_unsafe_artifact(value):
            self.add("error", "live_or_sensitive_artifact", "A live route, contact route, or secret-like value is prohibited.", line=line)
            return

        raw_id = value.get("source_id")
        record_id = raw_id if type(raw_id) is str and SOURCE_ID_PATTERN.fullmatch(raw_id) else None
        shape_valid = self.validate_record(value, line, record_id)
        if not shape_valid or record_id is None:
            return
        if record_id in self.records:
            self.add("error", "duplicate_record_id", "The source identifier is duplicated.", line=line, record_id=record_id, field="source_id")
            return
        self.records[record_id] = (line, value)

    def object_shape(
        self, value: Any, fields: set[str], line: int, record_id: str | None, field: str
    ) -> bool:
        if type(value) is not dict:
            self.add("error", "wrong_type", "The field has the wrong JSON type.", line=line, record_id=record_id, field=field)
            return False
        valid = True
        for missing in sorted(fields - value.keys()):
            path = f"{field}.{missing}" if field else missing
            self.add("error", "missing_field", "A required field is missing.", line=line, record_id=record_id, field=path)
            valid = False
        if value.keys() - fields:
            self.add("error", "unknown_field", "One or more unknown fields are not permitted.", line=line, record_id=record_id, field=field or "record")
            valid = False
        return valid

    def exact_type(self, value: Any, expected: type, line: int, record_id: str | None, field: str) -> bool:
        if type(value) is expected:
            return True
        self.add("error", "wrong_type", "The field has the wrong JSON type.", line=line, record_id=record_id, field=field)
        return False

    def enum(self, value: Any, allowed: set[str], line: int, record_id: str | None, field: str) -> bool:
        if not self.exact_type(value, str, line, record_id, field):
            return False
        if value in allowed:
            return True
        self.add("error", "invalid_value", "The field value is outside the contract vocabulary.", line=line, record_id=record_id, field=field)
        return False

    def optional_string(
        self, value: Any, maximum: int, line: int, record_id: str | None, field: str,
        *, nonempty: bool = True, opaque: bool = False,
    ) -> bool:
        if value is None:
            return True
        if not self.exact_type(value, str, line, record_id, field):
            return False
        if nonempty and not value:
            self.add("error", "empty_string", "The field must not be empty.", line=line, record_id=record_id, field=field)
            return False
        if len(value) > maximum:
            self.add("error", "string_length_limit", "The string exceeds the field length limit.", line=line, record_id=record_id, field=field)
            return False
        if opaque and value and OPAQUE_ID_PATTERN.fullmatch(value) is None:
            self.add("error", "unsafe_opaque_id", "The opaque identifier does not match the safe syntax.", line=line, record_id=record_id, field=field)
            return False
        return True

    def required_string(
        self, value: Any, maximum: int, line: int, record_id: str | None, field: str,
        *, opaque: bool = False,
    ) -> bool:
        if value is None:
            self.add("error", "wrong_type", "The field has the wrong JSON type.", line=line, record_id=record_id, field=field)
            return False
        return self.optional_string(value, maximum, line, record_id, field, opaque=opaque)

    def optional_bool(self, value: Any, line: int, record_id: str | None, field: str) -> bool:
        return value is None or self.exact_type(value, bool, line, record_id, field)

    def date_value(self, value: Any, line: int, record_id: str | None, field: str, *, optional: bool = False) -> bool:
        if optional and value is None:
            return True
        if not self.exact_type(value, str, line, record_id, field):
            return False
        try:
            parsed = date.fromisoformat(value)
        except ValueError:
            parsed = None
        if parsed is not None and parsed.isoformat() == value:
            return True
        self.add("error", "invalid_date", "The field must be a real canonical YYYY-MM-DD date.", line=line, record_id=record_id, field=field)
        return False

    def timestamp_value(self, value: Any, line: int, record_id: str | None, field: str, *, optional: bool = False) -> bool:
        if optional and value is None:
            return True
        if not self.exact_type(value, str, line, record_id, field):
            return False
        parsed: datetime | None = None
        if RFC3339_PATTERN.fullmatch(value):
            try:
                parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
            except ValueError:
                parsed = None
        if parsed is not None and parsed.tzinfo is not None:
            return True
        self.add("error", "invalid_timestamp", "The field must be a timezone-aware RFC 3339 timestamp.", line=line, record_id=record_id, field=field)
        return False

    def list_of_strings(
        self, value: Any, line: int, record_id: str | None, field: str, *,
        allowed: set[str] | None = None, nonempty: bool = False, opaque: bool = False,
    ) -> bool:
        if not self.exact_type(value, list, line, record_id, field):
            return False
        valid = True
        if nonempty and not value:
            self.add("error", "empty_list", "The list must not be empty.", line=line, record_id=record_id, field=field)
            valid = False
        if len(value) != len({entry for entry in value if type(entry) is str}) or any(type(entry) is not str for entry in value):
            self.add("error", "invalid_string_list", "The field must be a unique list of strings.", line=line, record_id=record_id, field=field)
            return False
        for entry in value:
            if not entry or len(entry) > MAX_SHORT_TEXT:
                self.add("error", "invalid_string_list", "The field must be a unique list of bounded nonempty strings.", line=line, record_id=record_id, field=field)
                valid = False
                break
            if allowed is not None and entry not in allowed:
                self.add("error", "invalid_value", "A list value is outside the contract vocabulary.", line=line, record_id=record_id, field=field)
                valid = False
                break
            if opaque and OPAQUE_ID_PATTERN.fullmatch(entry) is None:
                self.add("error", "unsafe_opaque_id", "An opaque identifier does not match the safe syntax.", line=line, record_id=record_id, field=field)
                valid = False
                break
        return valid

    def validate_record(self, record: dict[str, Any], line: int, record_id: str | None) -> bool:
        valid = self.object_shape(record, TOP_FIELDS, line, record_id, "")
        valid &= self.enum(record.get("schema_version"), {SCHEMA_VERSION}, line, record_id, "schema_version")
        source_id = record.get("source_id")
        if not self.exact_type(source_id, str, line, record_id, "source_id"):
            valid = False
        elif SOURCE_ID_PATTERN.fullmatch(source_id) is None:
            self.add("error", "invalid_id", "The identifier does not match the required syntax.", line=line, field="source_id")
            valid = False
        valid &= self.required_string(record.get("source_name"), MAX_SHORT_TEXT, line, record_id, "source_name")
        valid &= self.required_string(record.get("description"), MAX_LONG_TEXT, line, record_id, "description")
        valid &= self.enum(record.get("provenance_class"), PROVENANCE_CLASSES, line, record_id, "provenance_class")
        valid &= self.enum(record.get("authenticity"), AUTHENTICITY, line, record_id, "authenticity")
        valid &= self.enum(record.get("lifecycle_status"), LIFECYCLE_STATES, line, record_id, "lifecycle_status")
        valid &= self.list_of_strings(record.get("blockers"), line, record_id, "blockers")
        valid &= self._validate_origin(record.get("origin"), line, record_id)
        valid &= self._validate_artifact_hash(record.get("artifact_hash"), line, record_id)
        valid &= self._optional_count(record.get("expected_record_count"), line, record_id, "expected_record_count")
        valid &= self._optional_count(record.get("audited_record_count"), line, record_id, "audited_record_count")
        valid &= self.list_of_strings(record.get("language_scope"), line, record_id, "language_scope", allowed=LANGUAGE_SCOPES, nonempty=True)
        valid &= self.list_of_strings(record.get("content_scope"), line, record_id, "content_scope", allowed=CONTENT_SCOPES, nonempty=True)
        valid &= self._validate_authorization(record.get("authorization"), line, record_id)
        valid &= self._validate_consent(record.get("consent"), line, record_id)
        valid &= self._validate_ethics(record.get("ethics"), line, record_id)
        valid &= self._validate_license(record.get("license"), line, record_id)
        valid &= self.enum(record.get("release_tier"), RELEASE_TIERS, line, record_id, "release_tier")
        valid &= self._validate_review(record.get("privacy_review"), "privacy_review", (
            "deidentification", "pii_scan", "residual_risk_review", "raw_storage_approval"
        ), line, record_id)
        valid &= self._validate_review(record.get("safety_review"), "safety_review", (
            "active_artifact_scan", "defanging", "credential_otp_scan", "prohibited_identifier_scan"
        ), line, record_id)
        valid &= self._validate_quality(record.get("quality_audits"), line, record_id)
        valid &= self._validate_lineage(record.get("lineage"), line, record_id)
        valid &= self._validate_equivalence(record.get("equivalence_policy"), line, record_id)
        valid &= self._validate_partitions(record.get("partition_eligibility"), line, record_id)
        valid &= self.enum(record.get("llm_fraction_scope"), LLM_FRACTION_SCOPES, line, record_id, "llm_fraction_scope")
        valid &= self.optional_string(record.get("steward"), MAX_SHORT_TEXT, line, record_id, "steward")
        valid &= self.timestamp_value(record.get("created_at"), line, record_id, "created_at")
        valid &= self.timestamp_value(record.get("updated_at"), line, record_id, "updated_at")
        valid &= self._validate_decision_notes(record.get("decision_notes"), line, record_id)
        if valid:
            self._record_cross_fields(record, line, record_id)
        return bool(valid)

    def _validate_origin(self, value: Any, line: int, record_id: str | None) -> bool:
        fields = {"publisher_or_creator", "landing_page", "artifact_version", "accessed_at"}
        valid = self.object_shape(value, fields, line, record_id, "origin")
        if not valid:
            return False
        valid &= self.required_string(value["publisher_or_creator"], MAX_SHORT_TEXT, line, record_id, "origin.publisher_or_creator")
        valid &= self.optional_string(value["landing_page"], 2_048, line, record_id, "origin.landing_page")
        if type(value["landing_page"]) is str and not _valid_official_https_url(value["landing_page"]):
            self.add("error", "invalid_evidence_url", "The evidence locator must be a syntactically safe HTTPS URL.", line=line, record_id=record_id, field="origin.landing_page")
            valid = False
        valid &= self.optional_string(value["artifact_version"], MAX_SHORT_TEXT, line, record_id, "origin.artifact_version")
        valid &= self.timestamp_value(value["accessed_at"], line, record_id, "origin.accessed_at", optional=True)
        return bool(valid)

    def _validate_artifact_hash(self, value: Any, line: int, record_id: str | None) -> bool:
        fields = {"algorithm", "value"}
        valid = self.object_shape(value, fields, line, record_id, "artifact_hash")
        if not valid:
            return False
        algorithm, digest = value["algorithm"], value["value"]
        if (algorithm is None) != (digest is None):
            self.add("error", "partial_artifact_hash", "Artifact hash algorithm and value must both be present or both be null.", line=line, record_id=record_id, field="artifact_hash")
            valid = False
        if algorithm is not None and algorithm != "SHA-256":
            self.add("error", "invalid_hash_algorithm", "The executable projection supports only SHA-256.", line=line, record_id=record_id, field="artifact_hash.algorithm")
            valid = False
        if digest is not None and (type(digest) is not str or HASH_PATTERN.fullmatch(digest) is None):
            self.add("error", "invalid_sha256", "The artifact value must be a lowercase SHA-256 digest.", line=line, record_id=record_id, field="artifact_hash.value")
            valid = False
        return bool(valid)

    def _optional_count(self, value: Any, line: int, record_id: str | None, field: str) -> bool:
        if value is None:
            return True
        if type(value) is int and 0 <= value <= 10_000_000:
            return True
        self.add("error", "invalid_count", "The count must be null or an integer within the operational bound.", line=line, record_id=record_id, field=field)
        return False

    def _validate_authorization(self, value: Any, line: int, record_id: str | None) -> bool:
        fields = {"status", "reviewer", "reviewed_at", "basis"}
        valid = self.object_shape(value, fields, line, record_id, "authorization")
        if not valid:
            return False
        valid &= self.enum(value["status"], AUTHORIZATION_STATES, line, record_id, "authorization.status")
        valid &= self.optional_string(value["reviewer"], MAX_SHORT_TEXT, line, record_id, "authorization.reviewer")
        valid &= self.timestamp_value(value["reviewed_at"], line, record_id, "authorization.reviewed_at", optional=True)
        valid &= self.required_string(value["basis"], MAX_LONG_TEXT, line, record_id, "authorization.basis")
        if value["status"] in {"APPROVED", "REJECTED"} and (value["reviewer"] is None or value["reviewed_at"] is None):
            self.add("error", "missing_review_evidence", "A completed authorization decision requires reviewer and review time.", line=line, record_id=record_id, field="authorization")
            valid = False
        return bool(valid)

    def _validate_consent(self, value: Any, line: int, record_id: str | None) -> bool:
        fields = {"required", "status", "document_version", "consent_reference_policy"}
        valid = self.object_shape(value, fields, line, record_id, "consent")
        if not valid:
            return False
        valid &= self.exact_type(value["required"], bool, line, record_id, "consent.required")
        valid &= self.enum(value["status"], CONSENT_STATES, line, record_id, "consent.status")
        valid &= self.optional_string(value["document_version"], 128, line, record_id, "consent.document_version", opaque=True)
        valid &= self.optional_string(value["consent_reference_policy"], 128, line, record_id, "consent.consent_reference_policy", opaque=True)
        if value["status"] == "APPROVED" and (value["document_version"] is None or value["consent_reference_policy"] is None):
            self.add("error", "missing_consent_evidence", "Approved consent requires versioned opaque policy references.", line=line, record_id=record_id, field="consent")
            valid = False
        if value["required"] and value["status"] == "NOT_APPLICABLE":
            self.add("error", "contradictory_consent", "Required consent cannot be marked not applicable.", line=line, record_id=record_id, field="consent")
            valid = False
        return bool(valid)

    def _validate_ethics(self, value: Any, line: int, record_id: str | None) -> bool:
        fields = {"status", "authority", "identifier", "effective_date"}
        valid = self.object_shape(value, fields, line, record_id, "ethics")
        if not valid:
            return False
        valid &= self.enum(value["status"], ETHICS_STATES, line, record_id, "ethics.status")
        valid &= self.optional_string(value["authority"], MAX_SHORT_TEXT, line, record_id, "ethics.authority")
        valid &= self.optional_string(value["identifier"], 128, line, record_id, "ethics.identifier", opaque=True)
        valid &= self.date_value(value["effective_date"], line, record_id, "ethics.effective_date", optional=True)
        complete = value["status"] in {"APPROVED", "EXEMPT", "REJECTED"}
        if complete and any(value[name] is None for name in ("authority", "identifier", "effective_date")):
            self.add("error", "missing_ethics_evidence", "A completed ethics decision requires authority, identifier, and effective date.", line=line, record_id=record_id, field="ethics")
            valid = False
        if value["status"] == "UNKNOWN" and any(value[name] is not None for name in ("authority", "identifier", "effective_date")):
            self.add("error", "contradictory_ethics", "Unknown ethics status cannot carry completed-decision evidence.", line=line, record_id=record_id, field="ethics")
            valid = False
        return bool(valid)

    def _validate_license(self, value: Any, line: int, record_id: str | None) -> bool:
        fields = {
            "status", "name_or_spdx", "text_url", "version", "reviewer", "reviewed_at",
            "research_use", "modification", "redistribution", "commercial_use",
            "attribution_text", "conflict_notes",
        }
        valid = self.object_shape(value, fields, line, record_id, "license")
        if not valid:
            return False
        valid &= self.enum(value["status"], LICENSE_STATES, line, record_id, "license.status")
        for name, maximum in (("name_or_spdx", 200), ("version", 128), ("reviewer", 200), ("attribution_text", 1_000), ("conflict_notes", 1_000)):
            valid &= self.optional_string(value[name], maximum, line, record_id, f"license.{name}")
        valid &= self.optional_string(value["text_url"], 2_048, line, record_id, "license.text_url")
        if type(value["text_url"]) is str and not _valid_official_https_url(value["text_url"]):
            self.add("error", "invalid_evidence_url", "The evidence locator must be a syntactically safe HTTPS URL.", line=line, record_id=record_id, field="license.text_url")
            valid = False
        valid &= self.timestamp_value(value["reviewed_at"], line, record_id, "license.reviewed_at", optional=True)
        for name in ("research_use", "modification", "redistribution", "commercial_use"):
            valid &= self.optional_bool(value[name], line, record_id, f"license.{name}")
        if value["status"] in {"VERIFIED", "INCOMPATIBLE"} and (value["reviewer"] is None or value["reviewed_at"] is None):
            self.add("error", "missing_review_evidence", "A completed license decision requires reviewer and review time.", line=line, record_id=record_id, field="license")
            valid = False
        if (value["reviewer"] is None) != (value["reviewed_at"] is None):
            self.add("error", "partial_review_evidence", "License reviewer and review time must both be present or both be null.", line=line, record_id=record_id, field="license")
            valid = False
        if value["status"] == "VERIFIED":
            required = ("name_or_spdx", "text_url", "version", "research_use", "modification", "redistribution", "commercial_use")
            if any(value[name] is None or value[name] == "" for name in required):
                self.add("error", "missing_license_evidence", "Verified license status requires complete identity, locator, version, and permission flags.", line=line, record_id=record_id, field="license")
                valid = False
        if value["status"] == "NOT_APPLICABLE" and not value["conflict_notes"]:
            self.add("error", "missing_license_basis", "Not-applicable license status requires a recorded consent or contract basis.", line=line, record_id=record_id, field="license.conflict_notes")
            valid = False
        return bool(valid)

    def _validate_review(
        self, value: Any, prefix: str, checks: tuple[str, ...], line: int, record_id: str | None
    ) -> bool:
        fields = {"status", *checks, "reviewer", "reviewed_at"}
        valid = self.object_shape(value, fields, line, record_id, prefix)
        if not valid:
            return False
        for name in ("status", *checks):
            valid &= self.enum(value[name], AUDIT_STATES, line, record_id, f"{prefix}.{name}")
        valid &= self.optional_string(value["reviewer"], MAX_SHORT_TEXT, line, record_id, f"{prefix}.reviewer")
        valid &= self.timestamp_value(value["reviewed_at"], line, record_id, f"{prefix}.reviewed_at", optional=True)
        if value["status"] in {"PASSED", "FAILED"} and (value["reviewer"] is None or value["reviewed_at"] is None):
            self.add("error", "missing_review_evidence", "A completed audit requires reviewer and review time.", line=line, record_id=record_id, field=prefix)
            valid = False
        if value["status"] == "PASSED" and any(value[name] not in FINAL_AUDIT_STATES for name in checks):
            self.add("error", "contradictory_audit", "A passed review cannot contain an incomplete or failed subcheck.", line=line, record_id=record_id, field=prefix)
            valid = False
        return bool(valid)

    def _validate_quality(self, value: Any, line: int, record_id: str | None) -> bool:
        fields = {
            "unicode_encoding", "language_script", "source_label", "duplicate_near_duplicate",
            "template_campaign", "fisher_independent_reannotation",
        }
        valid = self.object_shape(value, fields, line, record_id, "quality_audits")
        if not valid:
            return False
        for name in sorted(fields):
            valid &= self.enum(value[name], AUDIT_STATES, line, record_id, f"quality_audits.{name}")
        return bool(valid)

    def _validate_lineage(self, value: Any, line: int, record_id: str | None) -> bool:
        fields = {
            "source_family_id", "collection_batch_id", "scenario_or_prompt_family_id", "model_id",
            "generation_batch_id", "author_or_donor_batch_id", "parent_source_ids",
            "has_public_ancestor", "has_llm_ancestor",
        }
        valid = self.object_shape(value, fields, line, record_id, "lineage")
        if not valid:
            return False
        for name in (
            "source_family_id", "collection_batch_id", "scenario_or_prompt_family_id", "model_id",
            "generation_batch_id", "author_or_donor_batch_id",
        ):
            valid &= self.optional_string(value[name], 128, line, record_id, f"lineage.{name}", opaque=True)
        parents = value["parent_source_ids"]
        valid &= self.list_of_strings(parents, line, record_id, "lineage.parent_source_ids")
        if type(parents) is list:
            for parent in parents:
                if type(parent) is str and SOURCE_ID_PATTERN.fullmatch(parent) is None:
                    self.add("error", "invalid_id", "A parent source identifier does not match the required syntax.", line=line, record_id=record_id, field="lineage.parent_source_ids")
                    valid = False
                    break
        valid &= self.exact_type(value["has_public_ancestor"], bool, line, record_id, "lineage.has_public_ancestor")
        valid &= self.exact_type(value["has_llm_ancestor"], bool, line, record_id, "lineage.has_llm_ancestor")
        return bool(valid)

    def _validate_equivalence(self, value: Any, line: int, record_id: str | None) -> bool:
        fields = {
            "required", "opaque_token_policy_version", "final_component_assignment_required",
            "component_policy_version", "key_custodian", "key_rotation_policy",
            "raw_values_or_keys_in_ledger",
        }
        valid = self.object_shape(value, fields, line, record_id, "equivalence_policy")
        if not valid:
            return False
        valid &= self.exact_type(value["required"], bool, line, record_id, "equivalence_policy.required")
        valid &= self.optional_string(value["opaque_token_policy_version"], 128, line, record_id, "equivalence_policy.opaque_token_policy_version", opaque=True)
        valid &= self.exact_type(value["final_component_assignment_required"], bool, line, record_id, "equivalence_policy.final_component_assignment_required")
        valid &= self.optional_string(value["component_policy_version"], 128, line, record_id, "equivalence_policy.component_policy_version", opaque=True)
        valid &= self.optional_string(value["key_custodian"], MAX_SHORT_TEXT, line, record_id, "equivalence_policy.key_custodian")
        valid &= self.optional_string(value["key_rotation_policy"], 128, line, record_id, "equivalence_policy.key_rotation_policy", opaque=True)
        valid &= self.exact_type(value["raw_values_or_keys_in_ledger"], bool, line, record_id, "equivalence_policy.raw_values_or_keys_in_ledger")
        if value["raw_values_or_keys_in_ledger"] is True:
            self.add("error", "raw_secret_material", "Raw values, reversible mappings, and keys are prohibited in the ledger.", line=line, record_id=record_id, field="equivalence_policy.raw_values_or_keys_in_ledger")
            valid = False
        return bool(valid)

    def _validate_partitions(self, value: Any, line: int, record_id: str | None) -> bool:
        fields = {*PARTITIONS, "rationale"}
        valid = self.object_shape(value, fields, line, record_id, "partition_eligibility")
        if not valid:
            return False
        for name in PARTITIONS:
            valid &= self.exact_type(value[name], bool, line, record_id, f"partition_eligibility.{name}")
        valid &= self.required_string(value["rationale"], MAX_LONG_TEXT, line, record_id, "partition_eligibility.rationale")
        return bool(valid)

    def _validate_decision_notes(self, value: Any, line: int, record_id: str | None) -> bool:
        if not self.list_of_strings(value, line, record_id, "decision_notes", nonempty=True):
            return False
        valid = True
        for note in value:
            if EVIDENCE_NOTE_PATTERN.fullmatch(note) is None:
                self.add("error", "invalid_evidence_note", "Decision notes must begin with an evidence classification.", line=line, record_id=record_id, field="decision_notes")
                valid = False
                break
        return valid

    def _record_cross_fields(self, record: dict[str, Any], line: int, record_id: str | None) -> None:
        provenance = record["provenance_class"]
        lifecycle = record["lifecycle_status"]
        if record["authenticity"] != EXPECTED_AUTHENTICITY[provenance]:
            self.add("error", "authenticity_mismatch", "Authenticity contradicts the provenance class.", line=line, record_id=record_id, field="authenticity")

        created = _parse_timestamp(record["created_at"])
        updated = _parse_timestamp(record["updated_at"])
        if created is not None and updated is not None and updated < created:
            self.add("error", "timestamp_order", "The update time precedes the creation time.", line=line, record_id=record_id, field="updated_at")
        if record["audited_record_count"] is not None and record["artifact_hash"]["value"] is None:
            self.add("error", "audit_without_artifact", "An audited count requires an acquired hashed artifact.", line=line, record_id=record_id, field="audited_record_count")
        if "MESSAGE_TEXT" not in record["content_scope"]:
            self.add("error", "missing_message_scope", "The Paper 1 source must include message text scope.", line=line, record_id=record_id, field="content_scope")

        consent = record["consent"]
        tester = provenance in {"TESTER_DONATED_AUTHENTIC", "TESTER_AUTHORED_SIMULATION"}
        if tester and not consent["required"]:
            self.add("error", "tester_consent_not_required", "Tester provenance requires consent.", line=line, record_id=record_id, field="consent.required")
        if provenance == "PUBLIC_AUTHENTIC_AUXILIARY" and consent["required"] and consent["status"] == "NOT_APPLICABLE":
            self.add("error", "contradictory_consent", "Required consent cannot be not applicable.", line=line, record_id=record_id, field="consent")

        lineage = record["lineage"]
        if provenance != "LLM_DRAFTED_HUMAN_EDITED" and (lineage["model_id"] is not None or lineage["generation_batch_id"] is not None):
            self.add("error", "unexpected_llm_metadata", "Non-LLM provenance cannot declare direct model-generation metadata.", line=line, record_id=record_id, field="lineage")
        if record_id is not None and record_id in lineage["parent_source_ids"]:
            self.add("error", "self_parent", "A source cannot name itself as a parent.", line=line, record_id=record_id, field="lineage.parent_source_ids")

        partitions = {name for name in PARTITIONS if record["partition_eligibility"][name]}
        if lifecycle not in ACTIVE_LIFECYCLE_STATES and partitions:
            self.add("error", "inactive_partition_projection", "A non-authorized source cannot project partition eligibility.", line=line, record_id=record_id, field="partition_eligibility")
        if lifecycle in ACTIVE_LIFECYCLE_STATES and not partitions:
            self.add("error", "empty_partition_projection", "An authorized or ingested source requires at least one eligible partition.", line=line, record_id=record_id, field="partition_eligibility")
        if lifecycle in ACTIVE_LIFECYCLE_STATES and record["blockers"]:
            self.add("error", "authorized_with_blockers", "An authorized or ingested source cannot retain blockers.", line=line, record_id=record_id, field="blockers")
        if lifecycle not in ACTIVE_LIFECYCLE_STATES and not record["blockers"]:
            self.add("error", "missing_lifecycle_reason", "A non-authorized lifecycle state requires a blocker or terminal reason.", line=line, record_id=record_id, field="blockers")
        if lifecycle == "REJECTED" and record["authorization"]["status"] != "REJECTED":
            self.add("error", "lifecycle_authorization_mismatch", "Rejected lifecycle requires a rejected authorization decision.", line=line, record_id=record_id, field="authorization.status")
        if lifecycle == "WITHDRAWN" and tester and consent["status"] != "WITHDRAWN":
            self.add("error", "lifecycle_consent_mismatch", "Withdrawn tester lifecycle requires withdrawn consent.", line=line, record_id=record_id, field="consent.status")

        if lifecycle in ACTIVE_LIFECYCLE_STATES:
            self._authorized_cross_fields(record, line, record_id)

    def _authorized_cross_fields(self, record: dict[str, Any], line: int, record_id: str | None) -> None:
        before = len(self.diagnostics)
        provenance = record["provenance_class"]
        required_pairs = (
            (record["authorization"]["status"] == "APPROVED", "authorization.status", "missing_authorization_approval"),
            (record["ethics"]["status"] in {"APPROVED", "EXEMPT"}, "ethics.status", "missing_ethics_approval"),
            (record["license"]["status"] in {"VERIFIED", "NOT_APPLICABLE"}, "license.status", "missing_license_approval"),
            (record["release_tier"] != "UNKNOWN", "release_tier", "unknown_release_tier"),
            (record["privacy_review"]["status"] == "PASSED", "privacy_review.status", "privacy_review_incomplete"),
            (record["safety_review"]["status"] == "PASSED", "safety_review.status", "safety_review_incomplete"),
            (record["steward"] is not None, "steward", "missing_steward"),
            (record["artifact_hash"]["value"] is not None, "artifact_hash", "missing_artifact_hash"),
            (record["origin"]["artifact_version"] is not None, "origin.artifact_version", "missing_artifact_version"),
            (record["origin"]["accessed_at"] is not None, "origin.accessed_at", "missing_access_time"),
        )
        for condition, field, code in required_pairs:
            if not condition:
                self.add("error", code, "Authorized or ingested lifecycle is missing a mandatory completed gate.", line=line, record_id=record_id, field=field)
        if record["license"]["status"] == "NOT_APPLICABLE" and (
            record["license"]["reviewer"] is None or record["license"]["reviewed_at"] is None
        ):
            self.add("error", "missing_review_evidence", "Authorized not-applicable license decision requires reviewer and review time.", line=line, record_id=record_id, field="license")
        if provenance in {"TESTER_DONATED_AUTHENTIC", "TESTER_AUTHORED_SIMULATION"} and record["consent"]["status"] != "APPROVED":
            self.add("error", "missing_consent_approval", "Authorized tester provenance requires approved consent.", line=line, record_id=record_id, field="consent.status")
        if any(value not in FINAL_AUDIT_STATES for value in record["quality_audits"].values()):
            self.add("error", "quality_audit_incomplete", "Authorized or ingested lifecycle requires every quality audit to pass or be not applicable.", line=line, record_id=record_id, field="quality_audits")

        eq = record["equivalence_policy"]
        if eq["required"] and any(eq[name] is None for name in (
            "opaque_token_policy_version", "component_policy_version", "key_custodian", "key_rotation_policy"
        )):
            self.add("error", "equivalence_policy_incomplete", "Required equivalence linkage lacks a complete approved policy reference set.", line=line, record_id=record_id, field="equivalence_policy")
        if eq["final_component_assignment_required"] and eq["component_policy_version"] is None:
            self.add("error", "component_policy_incomplete", "Required final component assignment lacks a policy version.", line=line, record_id=record_id, field="equivalence_policy.component_policy_version")

        lineage = record["lineage"]
        common_lineage = ("source_family_id", "collection_batch_id")
        if any(lineage[name] is None for name in common_lineage):
            self.add("error", "lineage_incomplete", "Authorized source lineage requires source-family and collection-batch identifiers.", line=line, record_id=record_id, field="lineage")
        if provenance == "TESTER_DONATED_AUTHENTIC" and lineage["author_or_donor_batch_id"] is None:
            self.add("error", "donor_lineage_incomplete", "Authorized authentic donation requires an opaque donor-batch identifier.", line=line, record_id=record_id, field="lineage.author_or_donor_batch_id")
        if provenance == "TESTER_AUTHORED_SIMULATION" and (lineage["author_or_donor_batch_id"] is None or lineage["scenario_or_prompt_family_id"] is None):
            self.add("error", "simulation_lineage_incomplete", "Authorized simulation requires opaque author-batch and scenario-family identifiers.", line=line, record_id=record_id, field="lineage")
        if provenance == "LLM_DRAFTED_HUMAN_EDITED" and any(lineage[name] is None for name in (
            "scenario_or_prompt_family_id", "model_id", "generation_batch_id", "author_or_donor_batch_id"
        )):
            self.add("error", "llm_lineage_incomplete", "Authorized LLM-assisted source requires model, generation, prompt-family, and human-editor batch references.", line=line, record_id=record_id, field="lineage")
        if provenance == "PUBLIC_AUTHENTIC_AUXILIARY":
            if record["origin"]["landing_page"] is None or record["license"]["status"] != "VERIFIED":
                self.add("error", "public_evidence_incomplete", "Authorized public source requires an official HTTPS landing-page reference and verified license evidence.", line=line, record_id=record_id, field="origin.landing_page")
            if record["quality_audits"]["fisher_independent_reannotation"] != "PASSED":
                self.add("error", "public_reannotation_incomplete", "Authorized public source requires passed independent Fisher reannotation audit.", line=line, record_id=record_id, field="quality_audits.fisher_independent_reannotation")

        license_record = record["license"]
        if license_record["status"] == "VERIFIED" and license_record["research_use"] is not True:
            self.add("error", "research_use_not_permitted", "An active source governed by a verified license requires affirmative research-use permission.", line=line, record_id=record_id, field="license.research_use")
        if record["release_tier"] in {"DERIVED_ONLY", "DEIDENTIFIED_TEXT", "PUBLIC_TEXT"}:
            if license_record["status"] == "VERIFIED" and license_record["redistribution"] is not True:
                self.add("error", "release_exceeds_rights", "The release tier requires affirmative redistribution permission.", line=line, record_id=record_id, field="release_tier")
        if record["release_tier"] in {"DERIVED_ONLY", "DEIDENTIFIED_TEXT"} and license_record["status"] == "VERIFIED" and license_record["modification"] is not True:
            self.add("error", "release_exceeds_rights", "Derived or deidentified release requires affirmative modification permission.", line=line, record_id=record_id, field="release_tier")

        if record_id is not None and not any(
            diagnostic.severity == "error" and diagnostic.record_id == record_id
            for diagnostic in self.diagnostics[before:]
        ):
            self.machine_ready.add(record_id)

    def validate_graph_and_partitions(self) -> None:
        parents: dict[str, list[str]] = {}
        children: dict[str, list[str]] = {source_id: [] for source_id in self.records}
        indegree: dict[str, int] = {source_id: 0 for source_id in self.records}
        ancestry_unresolved: dict[str, bool] = {source_id: False for source_id in self.records}
        for source_id, (line, record) in self.records.items():
            parents[source_id] = record["lineage"]["parent_source_ids"]
            for parent in parents[source_id]:
                if parent not in self.records:
                    self.add("error", "missing_parent_source", "A parent source reference does not resolve in this ledger.", line=line, record_id=source_id, field="lineage.parent_source_ids", related_record_id=parent)
                    ancestry_unresolved[source_id] = True
                    continue
                children[parent].append(source_id)
                indegree[source_id] += 1

        actual_public = {source_id: False for source_id in self.records}
        actual_llm = {source_id: False for source_id in self.records}
        queue = deque(source_id for source_id in self.records if indegree[source_id] == 0)
        processed: set[str] = set()
        topological_order: list[str] = []
        while queue:
            source_id = queue.popleft()
            processed.add(source_id)
            topological_order.append(source_id)
            record = self.records[source_id][1]
            effective_public = (
                record["provenance_class"] == "PUBLIC_AUTHENTIC_AUXILIARY"
                or actual_public[source_id]
            )
            effective_llm = (
                record["provenance_class"] == "LLM_DRAFTED_HUMAN_EDITED"
                or actual_llm[source_id]
            )
            for child in children[source_id]:
                actual_public[child] = actual_public[child] or effective_public
                actual_llm[child] = actual_llm[child] or effective_llm
                ancestry_unresolved[child] = ancestry_unresolved[child] or ancestry_unresolved[source_id]
                indegree[child] -= 1
                if indegree[child] == 0:
                    queue.append(child)

        cycle_or_dependent = set(self.records) - processed
        for source_id in self.records:
            if source_id in cycle_or_dependent:
                line = self.records[source_id][0]
                self.add(
                    "error",
                    "source_lineage_cycle",
                    "The source belongs to or depends on a directed lineage cycle, so ancestry is unresolved.",
                    line=line,
                    record_id=source_id,
                    field="lineage.parent_source_ids",
                )
            elif ancestry_unresolved[source_id]:
                line = self.records[source_id][0]
                self.add(
                    "error",
                    "source_ancestry_unresolved",
                    "The source ancestry cannot be resolved because an upstream parent is missing.",
                    line=line,
                    record_id=source_id,
                    field="lineage.parent_source_ids",
                )

        for source_id in self.records:
            line, record = self.records[source_id]
            declared_public = record["lineage"]["has_public_ancestor"]
            declared_llm = record["lineage"]["has_llm_ancestor"]
            lineage_resolved = source_id in processed and not ancestry_unresolved[source_id]
            if lineage_resolved and declared_public != actual_public[source_id]:
                self.add("error", "public_ancestry_mismatch", "The declared public-ancestry flag does not match the transitive source graph.", line=line, record_id=source_id, field="lineage.has_public_ancestor")
            if lineage_resolved and declared_llm != actual_llm[source_id]:
                self.add("error", "llm_ancestry_mismatch", "The declared LLM-ancestry flag does not match the transitive source graph.", line=line, record_id=source_id, field="lineage.has_llm_ancestor")

            direct_public = record["provenance_class"] == "PUBLIC_AUTHENTIC_AUXILIARY"
            direct_llm = record["provenance_class"] == "LLM_DRAFTED_HUMAN_EDITED"
            effective_public = direct_public or (lineage_resolved and actual_public[source_id])
            effective_llm = direct_llm or (lineage_resolved and actual_llm[source_id])
            eligible = {name for name in PARTITIONS if record["partition_eligibility"][name]}
            if effective_public and not eligible <= PUBLIC_PARTITIONS:
                self.add("error", "public_partition_violation", "Public direct or derived lineage is restricted to development and external_test.", line=line, record_id=source_id, field="partition_eligibility")
            if effective_llm and eligible & PROTECTED_PARTITIONS:
                self.add("error", "llm_protected_partition", "LLM direct or derived lineage is forbidden from protected partitions.", line=line, record_id=source_id, field="partition_eligibility")
            if lineage_resolved:
                expected_scope = "COUNTS_TOWARD_DEVELOPMENT_AND_PILOT_CAPS" if effective_llm else "NOT_APPLICABLE"
                if record["llm_fraction_scope"] != expected_scope:
                    self.add("error", "llm_fraction_scope_mismatch", "The LLM cap-scope value contradicts direct or transitive lineage.", line=line, record_id=source_id, field="llm_fraction_scope")
            if "primary_test" in eligible and (
                record["provenance_class"] not in {"TESTER_DONATED_AUTHENTIC", "TESTER_AUTHORED_SIMULATION"}
                or effective_public or effective_llm or not lineage_resolved
            ):
                self.add("error", "primary_test_provenance", "Primary-test eligibility requires tester-originated provenance without public or LLM ancestry.", line=line, record_id=source_id, field="partition_eligibility.primary_test")

        chain_ready: dict[str, bool] = {}
        for source_id in topological_order:
            line = self.records[source_id][0]
            local_ready = source_id in self.machine_ready and source_id not in self.invalid_ids
            blocking_parent = next(
                (parent for parent in parents[source_id] if not chain_ready.get(parent, False)),
                None,
            )
            if local_ready and blocking_parent is not None:
                self.add(
                    "error",
                    "ancestor_not_machine_authorized",
                    "An active source has an ancestor that is not active and mechanically authorization-ready.",
                    line=line,
                    record_id=source_id,
                    field="lineage.parent_source_ids",
                    related_record_id=blocking_parent,
                )
                local_ready = False
            chain_ready[source_id] = local_ready

        self.machine_ready.difference_update(self.invalid_ids)

    def report(self) -> ValidationReport:
        diagnostics = tuple(sorted(
            self.diagnostics,
            key=lambda value: (
                value.dataset, value.line if value.line is not None else -1, value.severity,
                value.code, value.record_id or "", value.field or "", value.related_record_id or "",
            ),
        ))
        errors = sum(value.severity == "error" for value in diagnostics)
        warnings = sum(value.severity == "warning" for value in diagnostics)
        source_readiness: list[SourceReadiness] = []
        for source_id in sorted(self.records):
            lifecycle = self.records[source_id][1]["lifecycle_status"]
            machine = source_id in self.machine_ready and source_id not in self.invalid_ids
            if lifecycle in {"REJECTED", "WITHDRAWN"}:
                state = "NOT_APPLICABLE"
            elif machine:
                state = "HUMAN_REVIEW_REQUIRED"
            else:
                state = "BLOCKED"
            source_readiness.append(SourceReadiness(source_id, lifecycle, machine, state))
        schema_valid = errors == 0 and bool(self.records)
        active_unready = sum(
            record["lifecycle_status"] in {"PROPOSED", "BLOCKED"}
            for _, record in self.records.values()
        )
        collection_ready = False
        counts = {
            "sources": len(self.records),
            "machine_authorization_ready": len(self.machine_ready - self.invalid_ids),
            "declared_blocked_or_proposed": active_unready,
            "human_unknown_gates": len(HUMAN_GATES),
        }
        return ValidationReport(
            schema_version=SCHEMA_VERSION,
            schema_valid=schema_valid,
            collection_ready=collection_ready,
            readiness_state="BLOCKED",
            counts=counts,
            errors=errors,
            warnings=warnings,
            source_readiness=tuple(source_readiness),
            not_machine_verifiable=HUMAN_GATES,
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


def _forbidden_control(value: str) -> bool:
    return any(ord(character) < 32 and character not in "\t\n\r" for character in value)


def _string_hazards(value: Any) -> set[str]:
    hazards: set[str] = set()
    stack = [value]
    while stack:
        current = stack.pop()
        if type(current) is str:
            if any(0xD800 <= ord(character) <= 0xDFFF for character in current):
                hazards.add("surrogate")
            if _forbidden_control(current):
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
            if len(current) > MAX_CONTAINER_ITEMS:
                return "container_size_limit"
            stack.extend((child, depth + 1) for child in current.values())
        elif type(current) is list:
            if depth > MAX_NESTING_DEPTH:
                return "nesting_depth_limit"
            if len(current) > MAX_CONTAINER_ITEMS:
                return "container_size_limit"
            stack.extend((child, depth + 1) for child in current)
    return None


def _safe_source_id(value: str | None) -> bool:
    return type(value) is str and SOURCE_ID_PATTERN.fullmatch(value) is not None


def _reserved_host(value: str) -> bool:
    candidate = value.casefold().rstrip(".,;:!?)]}\"")
    if "://" in candidate:
        candidate = candidate.split("://", 1)[1]
    if candidate.startswith("www."):
        candidate = candidate[4:]
    candidate = candidate.split("/", 1)[0].split(":", 1)[0]
    return "." in candidate and candidate.rsplit(".", 1)[-1] in RESERVED_TLDS


def _valid_ipv4(value: str) -> bool:
    try:
        ipaddress.IPv4Address(value)
    except ipaddress.AddressValueError:
        return False
    return True


def _contains_route_or_secret(value: str) -> bool:
    if SECRET_VALUE_PATTERN.search(value):
        return True
    if MAILTO_PATTERN.search(value):
        return True
    if EMAIL_PATTERN.search(value):
        for match in EMAIL_PATTERN.finditer(value):
            if not _reserved_host(match.group(0).split("@", 1)[1]):
                return True
    if URL_PATTERN.search(value):
        for match in URL_PATTERN.finditer(value):
            if not _reserved_host(match.group(0)):
                return True
    normalized_dots = value.translate({0x3002: ord("."), 0xFF0E: ord("."), 0xFF61: ord(".")})
    for match in IPV4_PATTERN.finditer(normalized_dots):
        if _valid_ipv4(match.group(0)):
            return True
    for match in DOMAIN_PATTERN.finditer(normalized_dots):
        if not _reserved_host(match.group(0)):
            return True
    return PHONE_PATTERN.search(value) is not None


def _object_contains_unsafe_artifact(value: dict[str, Any]) -> bool:
    stack: list[tuple[Any, tuple[str, ...]]] = [(value, ())]
    while stack:
        current, path = stack.pop()
        if type(current) is dict:
            for key, child in current.items():
                if _contains_route_or_secret(key):
                    return True
                stack.append((child, (*path, key)))
        elif type(current) is list:
            stack.extend((child, path) for child in current)
        elif type(current) is str:
            if path in OFFICIAL_URL_PATHS:
                if SECRET_VALUE_PATTERN.search(current) or PHONE_PATTERN.search(current):
                    return True
                normalized_dots = current.translate(
                    {0x3002: ord("."), 0xFF0E: ord("."), 0xFF61: ord(".")}
                )
                if any(_valid_ipv4(match.group(0)) for match in IPV4_PATTERN.finditer(normalized_dots)):
                    return True
                continue
            if _contains_route_or_secret(current):
                return True
    return False


def _valid_official_https_url(value: str) -> bool:
    if (
        not value.startswith("https://")
        or any(ord(character) > 0x7F for character in value)
        or any(character in value for character in ("\\", "%", "?", "#"))
    ):
        return False
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError:
        return False
    if (
        parsed.scheme != "https"
        or not parsed.netloc
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
    ):
        return False
    hostname = parsed.hostname
    if hostname is None or len(hostname) > 253 or hostname.endswith("."):
        return False
    if port not in {None, 443}:
        return False
    try:
        ipaddress.ip_address(hostname)
    except ValueError:
        pass
    else:
        return False
    labels = hostname.split(".")
    if len(labels) < 2 or any(DNS_LABEL_PATTERN.fullmatch(label) is None for label in labels):
        return False
    if not any(character.isalpha() for character in labels[-1]):
        return False
    for label in labels:
        if label.casefold().startswith("xn--"):
            try:
                decoded = label.encode("ascii").decode("idna")
                round_trip = decoded.encode("idna").decode("ascii")
            except (UnicodeError, ValueError):
                return False
            if round_trip.casefold() != label.casefold():
                return False
    if parsed.path and URL_PATH_PATTERN.fullmatch(parsed.path) is None:
        return False
    if any(segment in {".", ".."} for segment in parsed.path.split("/")):
        return False
    expected_netloc = hostname if port is None else f"{hostname}:{port}"
    return parsed.netloc.casefold() == expected_netloc.casefold()


def _parse_timestamp(value: str) -> datetime | None:
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def validate_ledger(ledger_path: str | Path) -> ValidationReport:
    """Validate one strict Fisher governance-ledger JSONL file."""

    validator = _Validator()
    validator.load(Path(ledger_path))
    if not validator.records and not validator.diagnostics:
        validator.add("error", "empty_ledger", "The governance ledger must contain at least one source record.")
    validator.validate_graph_and_partitions()
    return validator.report()


def format_json(report: ValidationReport) -> str:
    """Return deterministic ASCII JSON without source contents."""

    return json.dumps(report.to_dict(), ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def format_text(report: ValidationReport) -> str:
    """Return deterministic text without echoing untrusted source contents."""

    lines = [
        (
            f"{report.readiness_state} schema_valid={str(report.schema_valid).lower()} "
            f"collection_ready={str(report.collection_ready).lower()} "
            f"sources={report.counts['sources']} "
            f"machine_authorization_ready={report.counts['machine_authorization_ready']} "
            f"declared_blocked_or_proposed={report.counts['declared_blocked_or_proposed']} "
            f"human_unknown_gates={report.counts['human_unknown_gates']} "
            f"errors={report.errors} warnings={report.warnings}"
        )
    ]
    for source in report.source_readiness:
        lines.append(
            f"SOURCE record={source.source_id} lifecycle={source.lifecycle_status} "
            f"machine_authorization_ready={str(source.machine_authorization_ready).lower()} "
            f"readiness={source.readiness_state}"
        )
    for gate in report.not_machine_verifiable:
        lines.append(
            f"HUMAN code={gate.code} state={gate.state} representation={gate.representation}: {gate.reason}"
        )
    for diagnostic in report.diagnostics:
        context = ["dataset=ledger"]
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
