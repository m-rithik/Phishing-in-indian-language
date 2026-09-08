"""Path-free engine descriptor parsing and one-code preflight receipts."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import re
from typing import Any, BinaryIO, Mapping

from fisher_data.validator import (
    DEFANGING_MARKERS,
    RESERVED_ARTIFACT_PATTERN,
    TYPED_PLACEHOLDERS,
    VISIBLE_ARTIFACT_KINDS,
    VISIBLE_ARTIFACT_REPRESENTATIONS,
    _object_contains_live_artifact,
    _object_contains_sensitive_artifact,
)

from ._canonical import (
    CanonicalError,
    canonical_json_bytes,
    exact_keys,
    is_nonboolean_int,
    is_sha256,
    read_cap_plus_one,
    strict_json_loads,
)
from .artifacts import (
    ALLOWED_SYSTEMS,
    ArtifactValidationError,
    system_artifact_manifest_sha256,
    validate_system_artifact_manifest,
    validate_system_manifest_bundle,
)
from .source_closure import verify_source_closure_files


DESCRIPTOR_CAP = 1024 * 1024
RECEIPT_CAP = 64 * 1024
DESCRIPTOR_FIELDS = (
    "schema_version",
    "run_id",
    "condition",
    "system_id",
    "system_variant",
    "system_artifact_manifest_sha256",
    "item_id",
    "vmp_sha256",
)
RECEIPT_FIELDS = (
    "schema_version",
    "preflight_id",
    "submitted_descriptor_sha256",
    "submitted_prefix_sha256",
    "prefix_bytes_hashed",
    "observed_bytes",
    "run_id",
    "condition",
    "system_id",
    "system_variant",
    "system_artifact_manifest_sha256",
    "item_id",
    "vmp_sha256",
    "decoded_descriptor_count",
    "validated_system_manifest_count",
    "validated_vmp_count",
    "failure_stage",
    "invalid_codes",
    "status",
)
_PREFLIGHT_ID = re.compile(r"engine_preflight_[a-z0-9][a-z0-9_-]{0,55}\Z")
_RUN_ID = re.compile(r"engine_run_[a-z0-9][a-z0-9_-]{0,62}\Z")
_SYSTEM_ID = re.compile(r"system_[a-z0-9][a-z0-9_-]{0,62}\Z")
_ITEM_ID = re.compile(r"item_[a-z0-9][a-z0-9_-]{0,62}\Z")
_PREFLIGHT_CODES = (
    "preflight_descriptor_too_large",
    "preflight_descriptor_bom",
    "preflight_descriptor_invalid_utf8",
    "preflight_descriptor_duplicate_key",
    "preflight_descriptor_nonfinite",
    "preflight_descriptor_invalid_json",
    "preflight_descriptor_non_nfc",
    "preflight_descriptor_noncanonical_bytes",
    "preflight_descriptor_schema_or_enum",
    "preflight_missing_referenced_artifact",
    "preflight_artifact_hash_mismatch",
    "preflight_invalid_system_manifest",
    "preflight_invalid_vmp",
)


@dataclass(frozen=True)
class EngineInputDescriptor:
    run_id: str
    condition: str
    system_id: str
    system_variant: str
    system_artifact_manifest_sha256: str
    item_id: str
    vmp_sha256: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "1.0.0",
            "run_id": self.run_id,
            "condition": self.condition,
            "system_id": self.system_id,
            "system_variant": self.system_variant,
            "system_artifact_manifest_sha256": self.system_artifact_manifest_sha256,
            "item_id": self.item_id,
            "vmp_sha256": self.vmp_sha256,
        }

    def to_bytes(self) -> bytes:
        value = self.to_dict()
        _validate_descriptor(value)
        return canonical_json_bytes(value, max_bytes=DESCRIPTOR_CAP)


@dataclass(frozen=True)
class SuppliedVMPArtifact:
    """The separately supplied item identity and exact canonical VMP bytes."""

    item_id: str
    data: bytes


_CONTEXT_SEAL = object()


@dataclass(frozen=True)
class ValidatedPreflightContext:
    """Opaque exact-byte evidence for a fully recomputed PASS preflight."""

    descriptor: EngineInputDescriptor
    descriptor_bytes: bytes
    receipt_bytes: bytes
    system_manifest_bytes: bytes
    vmp_item_id: str
    vmp_bytes: bytes
    system_manifest_bundle: tuple[tuple[str, bytes], ...]
    _seal: object

    def __post_init__(self) -> None:
        if self._seal is not _CONTEXT_SEAL:
            raise CanonicalError("preflight_invalid_context")

    @property
    def receipt(self) -> dict[str, Any]:
        value = strict_json_loads(self.receipt_bytes, prefix="preflight_receipt")
        assert isinstance(value, dict)
        return value

    @property
    def system_manifest(self) -> dict[str, Any]:
        value = strict_json_loads(self.system_manifest_bytes, prefix="system_manifest")
        assert isinstance(value, dict)
        return value


def _validate_descriptor(value: object) -> None:
    if not exact_keys(value, DESCRIPTOR_FIELDS):
        raise CanonicalError("preflight_descriptor_schema_or_enum")
    assert isinstance(value, dict)
    if (
        value["schema_version"] != "1.0.0"
        or not isinstance(value["run_id"], str)
        or _RUN_ID.fullmatch(value["run_id"]) is None
        or not isinstance(value["system_id"], str)
        or _SYSTEM_ID.fullmatch(value["system_id"]) is None
        or (value["condition"], value["system_variant"]) not in ALLOWED_SYSTEMS
        or not is_sha256(value["system_artifact_manifest_sha256"])
        or not isinstance(value["item_id"], str)
        or _ITEM_ID.fullmatch(value["item_id"]) is None
        or not is_sha256(value["vmp_sha256"])
    ):
        raise CanonicalError("preflight_descriptor_schema_or_enum")


def descriptor_from_value(value: object) -> EngineInputDescriptor:
    _validate_descriptor(value)
    assert isinstance(value, dict)
    return EngineInputDescriptor(**{field: value[field] for field in DESCRIPTOR_FIELDS[1:]})


def _safe_preflight_id(value: str) -> None:
    if _PREFLIGHT_ID.fullmatch(value) is None:
        raise ValueError("invalid preflight ID")


def _receipt(
    *,
    preflight_id: str,
    submitted_descriptor_sha256: str | None,
    submitted_prefix_sha256: str | None,
    prefix_bytes_hashed: int,
    observed_bytes: int | str,
    descriptor: EngineInputDescriptor | None,
    decoded_descriptor_count: int,
    validated_system_manifest_count: int,
    validated_vmp_count: int,
    code: str | None,
) -> dict[str, Any]:
    passed = code is None
    values = descriptor.to_dict() if passed and descriptor is not None else None
    receipt = {
        "schema_version": "1.0.0",
        "preflight_id": preflight_id,
        "submitted_descriptor_sha256": submitted_descriptor_sha256,
        "submitted_prefix_sha256": submitted_prefix_sha256,
        "prefix_bytes_hashed": prefix_bytes_hashed,
        "observed_bytes": observed_bytes,
        "run_id": values["run_id"] if values else None,
        "condition": values["condition"] if values else None,
        "system_id": values["system_id"] if values else None,
        "system_variant": values["system_variant"] if values else None,
        "system_artifact_manifest_sha256": values["system_artifact_manifest_sha256"] if values else None,
        "item_id": values["item_id"] if values else None,
        "vmp_sha256": values["vmp_sha256"] if values else None,
        "decoded_descriptor_count": decoded_descriptor_count,
        "validated_system_manifest_count": validated_system_manifest_count,
        "validated_vmp_count": validated_vmp_count,
        "failure_stage": "NONE" if passed else "VMP" if code == "preflight_invalid_vmp" else "SOURCE_OR_CONFIG",
        "invalid_codes": [] if passed else [code],
        "status": "PASS" if passed else "FAIL",
    }
    validate_preflight_receipt(receipt)
    return receipt


def _validate_vmp(value: object) -> None:
    if not exact_keys(value, ("text", "visible_artifacts")):
        raise CanonicalError("preflight_invalid_vmp")
    assert isinstance(value, dict)
    text = value["text"]
    artifacts = value["visible_artifacts"]
    if not isinstance(text, str) or not 1 <= len(text) <= 10_000 or not isinstance(artifacts, list) or len(artifacts) > 64:
        raise CanonicalError("preflight_invalid_vmp")
    ranges: list[tuple[int, int]] = []
    order: list[tuple[int, int, bytes, bytes, bytes]] = []
    for artifact in artifacts:
        if not exact_keys(artifact, ("kind", "kind_reason", "representation", "start", "end", "text")):
            raise CanonicalError("preflight_invalid_vmp")
        kind = artifact["kind"]
        reason = artifact["kind_reason"]
        representation = artifact["representation"]
        start, end, surface = artifact["start"], artifact["end"], artifact["text"]
        if kind not in VISIBLE_ARTIFACT_KINDS or representation not in VISIBLE_ARTIFACT_REPRESENTATIONS:
            raise CanonicalError("preflight_invalid_vmp")
        if not isinstance(reason, str) or len(reason) > 500 or (kind == "OTHER") != bool(reason):
            raise CanonicalError("preflight_invalid_vmp")
        if not is_nonboolean_int(start, minimum=0) or not is_nonboolean_int(end, minimum=1, maximum=len(text)) or start >= end or not isinstance(surface, str) or text[start:end] != surface:
            raise CanonicalError("preflight_invalid_vmp")
        coherent = (
            surface == TYPED_PLACEHOLDERS[kind]
            if representation == "TYPED_PLACEHOLDER"
            else RESERVED_ARTIFACT_PATTERN.fullmatch(surface) is not None
            if representation == "RESERVED"
            else any(marker in surface for marker in DEFANGING_MARKERS)
        )
        if not coherent:
            raise CanonicalError("preflight_invalid_vmp")
        ranges.append((start, end))
        order.append((start, end, kind.encode("utf-8"), representation.encode("utf-8"), surface.encode("utf-8")))
    if order != sorted(set(order)) or any(current[0] < prior[1] for prior, current in zip(sorted(ranges), sorted(ranges)[1:])):
        raise CanonicalError("preflight_invalid_vmp")
    if _object_contains_live_artifact(value) or _object_contains_sensitive_artifact(value):
        raise CanonicalError("preflight_invalid_vmp")


def preflight_engine_input(
    descriptor_source: bytes | BinaryIO,
    *,
    preflight_id: str,
    system_artifact_bytes: bytes | None,
    vmp_artifact: SuppliedVMPArtifact | None,
    project_root: Path | None = None,
    system_manifest_bundle: Mapping[str, bytes] | None = None,
) -> dict[str, Any]:
    """Apply the frozen total precedence and return one sanitized receipt."""

    _safe_preflight_id(preflight_id)
    try:
        bounded = read_cap_plus_one(descriptor_source, DESCRIPTOR_CAP)
    except (CanonicalError, MemoryError, RecursionError):
        return _receipt(
            preflight_id=preflight_id,
            submitted_descriptor_sha256=sha256(b"").hexdigest(),
            submitted_prefix_sha256=None,
            prefix_bytes_hashed=0,
            observed_bytes=0,
            descriptor=None,
            decoded_descriptor_count=0,
            validated_system_manifest_count=0,
            validated_vmp_count=0,
            code="preflight_descriptor_invalid_json",
        )
    if bounded.exceeded:
        return _receipt(
            preflight_id=preflight_id,
            submitted_descriptor_sha256=None,
            submitted_prefix_sha256=sha256(bounded.data).hexdigest(),
            prefix_bytes_hashed=DESCRIPTOR_CAP + 1,
            observed_bytes=f"GE_{DESCRIPTOR_CAP + 1}",
            descriptor=None,
            decoded_descriptor_count=0,
            validated_system_manifest_count=0,
            validated_vmp_count=0,
            code="preflight_descriptor_too_large",
        )
    descriptor_hash = sha256(bounded.data).hexdigest()
    receipt_metadata = {
        "preflight_id": preflight_id,
        "submitted_descriptor_sha256": descriptor_hash,
        "submitted_prefix_sha256": None,
        "prefix_bytes_hashed": 0,
        "observed_bytes": len(bounded.data),
    }

    try:
        raw_value = strict_json_loads(bounded.data, prefix="preflight_descriptor")
        descriptor = descriptor_from_value(raw_value)
    except CanonicalError as error:
        return _receipt(
            **receipt_metadata,
            descriptor=None,
            decoded_descriptor_count=0,
            validated_system_manifest_count=0,
            validated_vmp_count=0,
            code=error.code,
        )

    if system_artifact_bytes is None or vmp_artifact is None:
        return _receipt(
            **receipt_metadata,
            descriptor=None,
            decoded_descriptor_count=1,
            validated_system_manifest_count=0,
            validated_vmp_count=0,
            code="preflight_missing_referenced_artifact",
        )

    # Both direct byte hashes are checked before either artifact's semantics.
    system_hash_matches = sha256(system_artifact_bytes).hexdigest() == descriptor.system_artifact_manifest_sha256
    vmp_hash_matches = sha256(vmp_artifact.data).hexdigest() == descriptor.vmp_sha256
    if not system_hash_matches or not vmp_hash_matches:
        return _receipt(
            **receipt_metadata,
            descriptor=None,
            decoded_descriptor_count=1,
            validated_system_manifest_count=0,
            validated_vmp_count=0,
            code="preflight_artifact_hash_mismatch",
        )

    try:
        if len(system_artifact_bytes) > 4 * 1024 * 1024:
            raise ArtifactValidationError("engine_binding_invalid_system")
        system_value = strict_json_loads(system_artifact_bytes, prefix="system_manifest")
        validate_system_artifact_manifest(system_value)
        if system_manifest_bundle is None:
            raise ArtifactValidationError("engine_binding_invalid_system")
        bundle = validate_system_manifest_bundle(system_manifest_bundle)
        bundled = bundle[(descriptor.condition, descriptor.system_variant)]
        if canonical_json_bytes(bundled) != system_artifact_bytes:
            raise ArtifactValidationError("engine_binding_invalid_system")
        resolved_project_root = project_root or Path(__file__).resolve().parents[1]
        if not isinstance(resolved_project_root, Path):
            raise ArtifactValidationError("engine_binding_invalid_system")
        verify_source_closure_files(
            system_value["executed_source_closure"],
            resolved_project_root,
        )
        if (
            system_value["system_id"] != descriptor.system_id
            or system_value["condition"] != descriptor.condition
            or system_value["system_variant"] != descriptor.system_variant
            or system_artifact_manifest_sha256(system_value) != descriptor.system_artifact_manifest_sha256
        ):
            raise ArtifactValidationError("engine_binding_invalid_system")
    except (CanonicalError, ArtifactValidationError):
        return _receipt(
            **receipt_metadata,
            descriptor=None,
            decoded_descriptor_count=1,
            validated_system_manifest_count=0,
            validated_vmp_count=0,
            code="preflight_invalid_system_manifest",
        )

    try:
        if len(vmp_artifact.data) > 4 * 1024 * 1024:
            raise CanonicalError("preflight_invalid_vmp")
        vmp_value = strict_json_loads(vmp_artifact.data, prefix="vmp")
        _validate_vmp(vmp_value)
        if vmp_artifact.item_id != descriptor.item_id:
            raise CanonicalError("preflight_invalid_vmp")
    except CanonicalError:
        return _receipt(
            **receipt_metadata,
            descriptor=None,
            decoded_descriptor_count=1,
            validated_system_manifest_count=1,
            validated_vmp_count=0,
            code="preflight_invalid_vmp",
        )

    return _receipt(
        **receipt_metadata,
        descriptor=descriptor,
        decoded_descriptor_count=1,
        validated_system_manifest_count=1,
        validated_vmp_count=1,
        code=None,
    )


def validate_preflight_receipt(value: object) -> None:
    if not exact_keys(value, RECEIPT_FIELDS):
        raise CanonicalError("preflight_invalid_receipt")
    assert isinstance(value, dict)
    if value["schema_version"] != "1.0.0" or not isinstance(value["preflight_id"], str) or _PREFLIGHT_ID.fullmatch(value["preflight_id"]) is None:
        raise CanonicalError("preflight_invalid_receipt")
    for field in ("decoded_descriptor_count", "validated_system_manifest_count", "validated_vmp_count"):
        if not is_nonboolean_int(value[field], minimum=0, maximum=1):
            raise CanonicalError("preflight_invalid_receipt")
    if value["status"] == "PASS":
        if value["failure_stage"] != "NONE" or value["invalid_codes"]:
            raise CanonicalError("preflight_invalid_receipt")
        descriptor_value = {"schema_version": "1.0.0", **{field: value[field] for field in DESCRIPTOR_FIELDS[1:]}}
        _validate_descriptor(descriptor_value)
        if (value["decoded_descriptor_count"], value["validated_system_manifest_count"], value["validated_vmp_count"]) != (1, 1, 1):
            raise CanonicalError("preflight_invalid_receipt")
        if (
            not is_sha256(value["submitted_descriptor_sha256"])
            or value["submitted_prefix_sha256"] is not None
            or value["prefix_bytes_hashed"] != 0
            or not is_nonboolean_int(value["observed_bytes"], minimum=0, maximum=DESCRIPTOR_CAP)
        ):
            raise CanonicalError("preflight_invalid_receipt")
    elif value["status"] == "FAIL":
        if any(value[field] is not None for field in DESCRIPTOR_FIELDS[1:]) or not isinstance(value["invalid_codes"], list) or len(value["invalid_codes"]) != 1 or value["failure_stage"] not in {"SOURCE_OR_CONFIG", "VMP"}:
            raise CanonicalError("preflight_invalid_receipt")
        code = value["invalid_codes"][0]
        if code not in _PREFLIGHT_CODES or value["failure_stage"] != ("VMP" if code == "preflight_invalid_vmp" else "SOURCE_OR_CONFIG"):
            raise CanonicalError("preflight_invalid_receipt")
        code_index = _PREFLIGHT_CODES.index(code) + 1
        expected_counts = (0, 0, 0) if code_index <= 9 else (1, 0, 0) if code_index <= 12 else (1, 1, 0)
        actual_counts = (value["decoded_descriptor_count"], value["validated_system_manifest_count"], value["validated_vmp_count"])
        if actual_counts != expected_counts:
            raise CanonicalError("preflight_invalid_receipt")
        if code == "preflight_descriptor_too_large":
            if (
                value["submitted_descriptor_sha256"] is not None
                or not is_sha256(value["submitted_prefix_sha256"])
                or value["prefix_bytes_hashed"] != DESCRIPTOR_CAP + 1
                or value["observed_bytes"] != f"GE_{DESCRIPTOR_CAP + 1}"
            ):
                raise CanonicalError("preflight_invalid_receipt")
        elif (
            not is_sha256(value["submitted_descriptor_sha256"])
            or value["submitted_prefix_sha256"] is not None
            or value["prefix_bytes_hashed"] != 0
            or not is_nonboolean_int(value["observed_bytes"], minimum=0, maximum=DESCRIPTOR_CAP)
        ):
            raise CanonicalError("preflight_invalid_receipt")
    else:
        raise CanonicalError("preflight_invalid_receipt")
    canonical_json_bytes(value, max_bytes=RECEIPT_CAP)


def preflight_receipt_bytes(value: object) -> bytes:
    validate_preflight_receipt(value)
    return canonical_json_bytes(value, max_bytes=RECEIPT_CAP)


def engine_preflight_receipt_sha256(value: object) -> str:
    return sha256(preflight_receipt_bytes(value)).hexdigest()


def validate_pass_preflight_context(
    *,
    descriptor_bytes: bytes,
    receipt_bytes: bytes,
    system_manifest_bytes: bytes,
    supplied_vmp: SuppliedVMPArtifact,
    project_root: Path,
    system_manifest_bundle: Mapping[str, bytes],
) -> ValidatedPreflightContext:
    """Recompute all PASS evidence and return a frozen exact-byte token."""

    if (
        not all(isinstance(raw, bytes) for raw in (descriptor_bytes, receipt_bytes, system_manifest_bytes))
        or not isinstance(supplied_vmp, SuppliedVMPArtifact)
        or not isinstance(project_root, Path)
        or not isinstance(system_manifest_bundle, Mapping)
    ):
        raise CanonicalError("preflight_invalid_context")
    if len(descriptor_bytes) > DESCRIPTOR_CAP or len(receipt_bytes) > RECEIPT_CAP:
        raise CanonicalError("preflight_invalid_context")
    descriptor_value = strict_json_loads(descriptor_bytes, prefix="preflight_descriptor")
    descriptor = descriptor_from_value(descriptor_value)
    receipt_value = strict_json_loads(receipt_bytes, prefix="preflight_receipt")
    validate_preflight_receipt(receipt_value)
    assert isinstance(receipt_value, dict)
    if receipt_value["status"] != "PASS":
        raise CanonicalError("preflight_invalid_context")
    bundle = validate_system_manifest_bundle(system_manifest_bundle)
    target = bundle.get((descriptor.condition, descriptor.system_variant))
    if target is None or target["system_id"] != descriptor.system_id:
        raise CanonicalError("preflight_invalid_context")
    if system_manifest_bundle.get(descriptor.system_id) != system_manifest_bytes:
        raise CanonicalError("preflight_invalid_context")
    recomputed = preflight_engine_input(
        descriptor_bytes,
        preflight_id=receipt_value["preflight_id"],
        system_artifact_bytes=system_manifest_bytes,
        vmp_artifact=supplied_vmp,
        project_root=project_root,
        system_manifest_bundle=system_manifest_bundle,
    )
    if preflight_receipt_bytes(recomputed) != receipt_bytes or recomputed["status"] != "PASS":
        raise CanonicalError("preflight_invalid_context")
    return ValidatedPreflightContext(
        descriptor=descriptor,
        descriptor_bytes=descriptor_bytes,
        receipt_bytes=receipt_bytes,
        system_manifest_bytes=system_manifest_bytes,
        vmp_item_id=supplied_vmp.item_id,
        vmp_bytes=supplied_vmp.data,
        system_manifest_bundle=tuple(sorted(system_manifest_bundle.items())),
        _seal=_CONTEXT_SEAL,
    )


__all__ = [
    "DESCRIPTOR_CAP",
    "EngineInputDescriptor",
    "SuppliedVMPArtifact",
    "ValidatedPreflightContext",
    "descriptor_from_value",
    "engine_preflight_receipt_sha256",
    "preflight_engine_input",
    "preflight_receipt_bytes",
    "validate_preflight_receipt",
    "validate_pass_preflight_context",
]
