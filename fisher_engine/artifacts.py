"""Canonical synthetic E0 system, provider, seed, and run artifacts."""

from __future__ import annotations

from dataclasses import dataclass, field
from hashlib import sha256
import math
import platform
import re
from types import MappingProxyType
import unicodedata
from typing import Any, Mapping, Sequence

from ._canonical import (
    CanonicalError,
    canonical_json_bytes,
    canonical_sha256,
    exact_keys,
    is_nonboolean_int,
    is_sha256,
    strict_json_loads,
)
from ._numeric import f64_bits_to_float, float_to_f64_bits, sequential_mean
from .source_closure import validate_source_closure


SYSTEM_MANIFEST_FIELDS = (
    "schema_version",
    "system_id",
    "condition",
    "system_variant",
    "executed_source_closure",
    "registry_binding",
    "provider_binding",
    "model_binding",
    "resource_binding",
    "environment_binding",
    "analysis_binding",
)
ENGINE_ENVELOPE_FIELDS = (
    "schema_version",
    "run_id",
    "condition",
    "system_id",
    "system_variant",
    "system_artifact_manifest_sha256",
    "runtime",
    "vmp",
    "provider_execution",
    "failure_stage",
    "failure_counts",
    "candidate_diagnostics",
    "candidate_paths",
    "active_path_ids",
    "five_seed_logit_artifact_sha256",
    "prediction_audit_sha256",
    "sep_packet_hashes",
    "feature_plan_id",
    "feature_tensor_hashes",
    "registry_snapshot_id",
    "registry_artifact_sha256",
    "resolver_version",
    "execution_status",
    "invalid_codes",
)
PROVIDER_EXECUTION_FIELDS = (
    "configured_mode",
    "provider_config_id",
    "provider_config_sha256",
    "normalizer_id",
    "normalizer_sha256",
    "eligible_spans",
    "invocation_attempted",
    "outcome",
    "output_accepted",
    "bypass_reason",
    "failure_code",
    "provider_manifest_sha256",
)
FAILURE_COUNT_FIELDS = (
    "total",
    "configured_span_entries_capped",
    "eligible_spans_capped",
    "provider",
    "normalizer",
    "candidate",
    "alignment",
    "prediction",
    "sep",
    "feature",
    "binding",
    "envelope",
)
RUNTIME_FIELDS = (
    "runtime_tag",
    "python_implementation",
    "python_version",
    "unicode_version",
    "platform_tag",
    "architecture",
    "math_backend_id",
    "math_backend_sha256",
    "float_contract",
)

ALLOWED_SYSTEMS = {
    ("C00", "BASE"),
    ("C10", "BASE"),
    ("C01", "BASE"),
    ("C11", "BASE"),
    ("C00", "CAPACITY_CONTROL"),
    ("C10", "CAPACITY_CONTROL"),
    ("C01", "SUPERVISION_CONTROL"),
    ("C11", "SUPERVISION_CONTROL"),
}
SEMANTIC_MASKS = {("C01", "BASE"), ("C11", "BASE")}
ALL_PATH_CONDITIONS = {"C10", "C11"}
_SAFE_IDENTITY = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")
_SYSTEM_ID = re.compile(r"system_[a-z0-9][a-z0-9_-]{0,62}\Z")
_RUN_ID = re.compile(r"engine_run_[a-z0-9][a-z0-9_-]{0,62}\Z")
_PATH_ID = re.compile(r"candidate_path_[a-z0-9][a-z0-9_-]{0,55}\Z")
_PROVIDER_ID = re.compile(r"provider_[a-z0-9][a-z0-9_-]{0,62}\Z")
_NORMALIZER_ID = re.compile(r"normalizer_[a-z0-9][a-z0-9_-]{0,62}\Z")
_VERSION = re.compile(r"[0-9]+(?:\.[0-9]+){1,3}\Z")
_CANDIDATE_DIAGNOSTIC_FIELDS = (
    "mode",
    "temperature_f64_bits",
    "search_mode",
    "input_count",
    "span_merge_reduction_count",
    "partial_merge_reduction_count",
    "full_merge_reduction_count",
    "total_merge_reduction_count",
    "postmerge_count",
    "returned_count",
    "preK_scope",
    "L_returned_f64_bits",
    "L_preK_f64_bits",
    "retained_preK_composition_mass_f64_bits",
    "q_normalizer_f64_bits",
    "q_max_f64_bits",
)
_INVALID_STAGE_CODES = {
    "PROVIDER_EXECUTION": {
        "engine_invalid_eligibility",
        "engine_provider_not_invoked",
        "engine_provider_invalid_output",
        "engine_normalizer_invalid_output",
    },
    "CANDIDATE": {
        "engine_candidate_invalid_arithmetic",
        "engine_candidate_nonfinite",
        "engine_candidate_invalid_alignment",
    },
    "PREDICTION": {"engine_prediction_invalid_audit", "engine_prediction_nonfinite"},
    "SEP": {"engine_sep_invalid_packet"},
    "FEATURE": {"engine_feature_invalid_tensor", "engine_feature_nonfinite"},
    "BINDING": {
        "engine_binding_invalid_system",
        "engine_binding_invalid_environment",
        "engine_binding_invalid_registry",
        "engine_binding_invalid_condition_mask",
        "engine_binding_invalid_path",
    },
    "ENVELOPE": {"engine_envelope_invalid_payload"},
}


class ArtifactValidationError(CanonicalError):
    """A controlled artifact validation failure."""


@dataclass(frozen=True)
class EngineValidationContext:
    """Exact stored artifact bytes required to validate one envelope."""

    preflight: Any
    provider_manifest_bytes: bytes | None
    provider_execution_bytes: bytes
    candidate_diagnostics_bytes: bytes | None
    candidate_path_artifact_bytes: Mapping[str, bytes]
    five_seed_artifact_bytes: bytes | None = None
    prediction_audit_bytes: bytes | None = None
    registry_artifact_bytes: bytes | None = None
    pair_packet_bytes_by_path: Mapping[str, bytes] = field(default_factory=dict)
    semantic_feature_plan_bytes_by_path: Mapping[str, bytes] = field(default_factory=dict)
    feature_tensor_bytes_by_path: Mapping[str, bytes] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for field in (
            "candidate_path_artifact_bytes",
            "pair_packet_bytes_by_path",
            "semantic_feature_plan_bytes_by_path",
            "feature_tensor_bytes_by_path",
        ):
            value = getattr(self, field)
            if not isinstance(value, Mapping) or any(
                not isinstance(key, str) or not isinstance(raw, bytes)
                for key, raw in value.items()
            ):
                raise ArtifactValidationError("engine_envelope_invalid_payload")
            object.__setattr__(self, field, MappingProxyType(dict(value)))
        for field in (
            "provider_manifest_bytes",
            "provider_execution_bytes",
            "candidate_diagnostics_bytes",
            "five_seed_artifact_bytes",
            "prediction_audit_bytes",
            "registry_artifact_bytes",
        ):
            value = getattr(self, field)
            if value is not None and not isinstance(value, bytes):
                raise ArtifactValidationError("engine_envelope_invalid_payload")


@dataclass(frozen=True)
class ValidatedEngineEnvelope:
    """Frozen output of complete exact-byte envelope replay."""

    canonical_bytes: bytes
    active_paths: tuple[Any, ...]
    candidate_replay: Any | None
    semantic_replay: Any | None

    @property
    def value(self) -> dict[str, Any]:
        parsed = strict_json_loads(self.canonical_bytes, prefix="engine_envelope")
        assert isinstance(parsed, dict)
        return parsed

    @property
    def sha256(self) -> str:
        return sha256(self.canonical_bytes).hexdigest()


def synthetic_hash(label: str) -> str:
    """Hash a synthetic fixture label; never a claim about an external file."""

    return sha256(f"fisher-e0-synthetic:{label}".encode("utf-8")).hexdigest()


def semantic_enabled(condition: str, variant: str) -> bool:
    if (condition, variant) not in ALLOWED_SYSTEMS:
        raise ArtifactValidationError("engine_binding_invalid_condition_mask")
    return (condition, variant) in SEMANTIC_MASKS


def all_paths_active(condition: str, variant: str) -> bool:
    if (condition, variant) not in ALLOWED_SYSTEMS:
        raise ArtifactValidationError("engine_binding_invalid_condition_mask")
    return condition in ALL_PATH_CONDITIONS


def build_environment_binding() -> dict[str, Any]:
    implementation = platform.python_implementation()
    version = platform.python_version()
    platform_tag = platform.system() + "-" + platform.release()
    platform_tag = re.sub(r"[^A-Za-z0-9._-]", "_", platform_tag)[:128]
    architecture = re.sub(r"[^A-Za-z0-9._-]", "_", platform.machine() or "unknown")[:128]
    math_backend_id = f"python_math_{version}"[:128]
    math_identity = "|".join((implementation, version, platform_tag, architecture, math_backend_id))
    return {
        "runtime_tag": f"cpython_{version}",
        "python_implementation": implementation,
        "python_version": version,
        "unicode_version": unicodedata.unidata_version,
        "platform_tag": platform_tag,
        "architecture": architecture,
        "math_backend_id": math_backend_id,
        "math_backend_sha256": sha256(math_identity.encode("utf-8")).hexdigest(),
        "float_contract": "IEEE754_BINARY64_RNE",
        "container_image_digest": None,
    }


def runtime_from_environment(environment: dict[str, Any]) -> dict[str, Any]:
    return {field: environment[field] for field in RUNTIME_FIELDS}


def build_system_artifact_manifest(
    *,
    system_id: str,
    condition: str,
    system_variant: str,
    executed_source_closure: dict[str, Any],
    matched_system_id: str | None = None,
    matched_system_artifact_manifest_sha256: str | None = None,
    environment_binding: dict[str, Any] | None = None,
    synthetic_fixture_manifest_sha256: str | None = None,
    registry_artifact_sha256: str | None = None,
) -> dict[str, Any]:
    """Build a deterministic, explicitly synthetic E0 system manifest."""

    semantic = semantic_enabled(condition, system_variant)
    source_manifest_hash = canonical_sha256(
        {
            "schema_version": "1.0.0",
            "files": executed_source_closure["files"],
        },
        max_bytes=4 * 1024 * 1024,
    )
    provider_config_id = "provider_synthetic_e0"
    normalizer_id = "normalizer_identity"
    provider_config_hash = canonical_sha256(
        {
            "schema_version": "1.0.0",
            "provider_config_id": provider_config_id,
            "provider_mode": "COMPOSED_SPAN",
            "maximum_readings": 8,
        }
    )
    normalizer_hash = canonical_sha256(
        {
            "schema_version": "1.0.0",
            "normalizer_id": normalizer_id,
            "mode": "E0_IDENTITY_ONLY",
        }
    )
    candidate_configuration_hash = canonical_sha256(
        {
            "schema_version": "1.0.0",
            "provider_config_sha256": provider_config_hash,
            "normalizer_sha256": normalizer_hash,
            "return_limit": 8,
            "beam_width": 64,
            "temperature_f64_bits": "3ff0000000000000",
        }
    )
    if synthetic_fixture_manifest_sha256 is None:
        synthetic_fixture_manifest_sha256 = synthetic_hash("fixture_manifest")
    if not is_sha256(synthetic_fixture_manifest_sha256):
        raise ArtifactValidationError("engine_binding_invalid_system")
    if registry_artifact_sha256 is None:
        registry_artifact_sha256 = synthetic_hash("registry_artifact")
    if not is_sha256(registry_artifact_sha256):
        raise ArtifactValidationError("engine_binding_invalid_registry")
    registry_binding = (
        {
            "registry_snapshot_id": "registry_synthetic_e0",
            "registry_artifact_sha256": registry_artifact_sha256,
            "resolver_version": "resolver_0.0.0-synthetic",
            "resolver_source_manifest_sha256": source_manifest_hash,
        }
        if semantic
        else {
            "registry_snapshot_id": None,
            "registry_artifact_sha256": None,
            "resolver_version": None,
            "resolver_source_manifest_sha256": None,
        }
    )
    if system_variant == "BASE":
        model_binding = None
    else:
        if matched_system_id is None or matched_system_artifact_manifest_sha256 is None:
            raise ArtifactValidationError("engine_binding_invalid_system")
        model_binding = {
            "binding_stage": "E0",
            "model_id": f"model_{system_id.removeprefix('system_')}",
            "checkpoint_sha256": None,
            "model_config_sha256": None,
            "matched_system_id": matched_system_id,
            "matched_system_artifact_manifest_sha256": matched_system_artifact_manifest_sha256,
            "capacity_adapter_sha256": None,
            "auxiliary_supervision": system_variant == "SUPERVISION_CONTROL",
        }
    manifest = {
        "schema_version": "1.0.0",
        "system_id": system_id,
        "condition": condition,
        "system_variant": system_variant,
        "executed_source_closure": executed_source_closure,
        "registry_binding": registry_binding,
        "provider_binding": {
            "provider_config_id": provider_config_id,
            "provider_config_sha256": provider_config_hash,
            "normalizer_id": normalizer_id,
            "normalizer_sha256": normalizer_hash,
            "candidate_configuration_sha256": candidate_configuration_hash,
            "provider_source_manifest_sha256": source_manifest_hash,
        },
        "model_binding": model_binding,
        "resource_binding": {
            "binding_stage": "E0",
            "resource_manifest_sha256": None,
            "synthetic_fixture_manifest_sha256": synthetic_fixture_manifest_sha256,
        },
        "environment_binding": environment_binding or build_environment_binding(),
        "analysis_binding": {
            "analysis_source_manifest_sha256": source_manifest_hash,
            "analysis_config_sha256": canonical_sha256(
                {
                    "schema_version": "1.0.0",
                    "analysis_scope": "SYNTHETIC_E0_ONLY",
                    "metric_conditions": ["C01", "C11"],
                }
            ),
        },
    }
    validate_system_artifact_manifest(manifest)
    return manifest


def _valid_identity_string(value: object) -> bool:
    return isinstance(value, str) and _SAFE_IDENTITY.fullmatch(value) is not None


def validate_system_artifact_manifest(value: object) -> None:
    if not exact_keys(value, SYSTEM_MANIFEST_FIELDS):
        raise ArtifactValidationError("engine_binding_invalid_system")
    assert isinstance(value, dict)
    if (
        value["schema_version"] != "1.0.0"
        or not isinstance(value["system_id"], str)
        or _SYSTEM_ID.fullmatch(value["system_id"]) is None
        or (value["condition"], value["system_variant"]) not in ALLOWED_SYSTEMS
    ):
        raise ArtifactValidationError("engine_binding_invalid_system")
    try:
        validate_source_closure(value["executed_source_closure"])
    except CanonicalError as error:
        raise ArtifactValidationError("engine_binding_invalid_system") from error
    semantic = semantic_enabled(value["condition"], value["system_variant"])
    registry = value["registry_binding"]
    if not exact_keys(
        registry,
        ("registry_snapshot_id", "registry_artifact_sha256", "resolver_version", "resolver_source_manifest_sha256"),
    ):
        raise ArtifactValidationError("engine_binding_invalid_registry")
    registry_values = tuple(registry.values())
    if semantic:
        if not all(_valid_identity_string(item) for item in (registry["registry_snapshot_id"], registry["resolver_version"])):
            raise ArtifactValidationError("engine_binding_invalid_registry")
        if not all(is_sha256(item) for item in (registry["registry_artifact_sha256"], registry["resolver_source_manifest_sha256"])):
            raise ArtifactValidationError("engine_binding_invalid_registry")
    elif any(item is not None for item in registry_values):
        raise ArtifactValidationError("engine_binding_invalid_registry")
    provider = value["provider_binding"]
    if not exact_keys(
        provider,
        (
            "provider_config_id",
            "provider_config_sha256",
            "normalizer_id",
            "normalizer_sha256",
            "candidate_configuration_sha256",
            "provider_source_manifest_sha256",
        ),
    ):
        raise ArtifactValidationError("engine_binding_invalid_system")
    if not isinstance(provider["provider_config_id"], str) or _PROVIDER_ID.fullmatch(provider["provider_config_id"]) is None:
        raise ArtifactValidationError("engine_binding_invalid_system")
    if not isinstance(provider["normalizer_id"], str) or _NORMALIZER_ID.fullmatch(provider["normalizer_id"]) is None:
        raise ArtifactValidationError("engine_binding_invalid_system")
    if not all(is_sha256(provider[field]) for field in tuple(provider)[1:] if field != "normalizer_id"):
        raise ArtifactValidationError("engine_binding_invalid_system")
    source_manifest_hash = canonical_sha256(
        {"schema_version": "1.0.0", "files": value["executed_source_closure"]["files"]},
        max_bytes=4 * 1024 * 1024,
    )
    expected_provider_hash = canonical_sha256(
        {
            "schema_version": "1.0.0",
            "provider_config_id": "provider_synthetic_e0",
            "provider_mode": "COMPOSED_SPAN",
            "maximum_readings": 8,
        }
    )
    expected_normalizer_hash = canonical_sha256(
        {
            "schema_version": "1.0.0",
            "normalizer_id": "normalizer_identity",
            "mode": "E0_IDENTITY_ONLY",
        }
    )
    expected_candidate_hash = canonical_sha256(
        {
            "schema_version": "1.0.0",
            "provider_config_sha256": expected_provider_hash,
            "normalizer_sha256": expected_normalizer_hash,
            "return_limit": 8,
            "beam_width": 64,
            "temperature_f64_bits": "3ff0000000000000",
        }
    )
    if provider != {
        "provider_config_id": "provider_synthetic_e0",
        "provider_config_sha256": expected_provider_hash,
        "normalizer_id": "normalizer_identity",
        "normalizer_sha256": expected_normalizer_hash,
        "candidate_configuration_sha256": expected_candidate_hash,
        "provider_source_manifest_sha256": source_manifest_hash,
    }:
        raise ArtifactValidationError("engine_binding_invalid_system")
    model = value["model_binding"]
    if value["system_variant"] == "BASE":
        if model is not None:
            raise ArtifactValidationError("engine_binding_invalid_system")
    else:
        model_fields = (
            "binding_stage",
            "model_id",
            "checkpoint_sha256",
            "model_config_sha256",
            "matched_system_id",
            "matched_system_artifact_manifest_sha256",
            "capacity_adapter_sha256",
            "auxiliary_supervision",
        )
        if not exact_keys(model, model_fields) or model["binding_stage"] != "E0":
            raise ArtifactValidationError("engine_binding_invalid_system")
        if not _valid_identity_string(model["model_id"]) or not isinstance(model["matched_system_id"], str) or _SYSTEM_ID.fullmatch(model["matched_system_id"]) is None:
            raise ArtifactValidationError("engine_binding_invalid_system")
        if not is_sha256(model["matched_system_artifact_manifest_sha256"]):
            raise ArtifactValidationError("engine_binding_invalid_system")
        if any(model[field] is not None for field in ("checkpoint_sha256", "model_config_sha256", "capacity_adapter_sha256")):
            raise ArtifactValidationError("engine_binding_invalid_system")
        if model["auxiliary_supervision"] is not (value["system_variant"] == "SUPERVISION_CONTROL"):
            raise ArtifactValidationError("engine_binding_invalid_system")
    resource = value["resource_binding"]
    if not exact_keys(resource, ("binding_stage", "resource_manifest_sha256", "synthetic_fixture_manifest_sha256")):
        raise ArtifactValidationError("engine_binding_invalid_system")
    if resource["binding_stage"] != "E0" or resource["resource_manifest_sha256"] is not None or not is_sha256(resource["synthetic_fixture_manifest_sha256"]):
        raise ArtifactValidationError("engine_binding_invalid_system")
    _validate_environment(value["environment_binding"])
    if value["environment_binding"] != build_environment_binding():
        raise ArtifactValidationError("engine_binding_invalid_environment")
    analysis = value["analysis_binding"]
    if not exact_keys(analysis, ("analysis_source_manifest_sha256", "analysis_config_sha256")) or not all(is_sha256(item) for item in analysis.values()):
        raise ArtifactValidationError("engine_binding_invalid_system")
    if analysis["analysis_source_manifest_sha256"] != source_manifest_hash:
        raise ArtifactValidationError("engine_binding_invalid_system")
    if analysis["analysis_config_sha256"] != canonical_sha256(
        {
            "schema_version": "1.0.0",
            "analysis_scope": "SYNTHETIC_E0_ONLY",
            "metric_conditions": ["C01", "C11"],
        }
    ):
        raise ArtifactValidationError("engine_binding_invalid_system")
    if semantic and registry["resolver_source_manifest_sha256"] != source_manifest_hash:
        raise ArtifactValidationError("engine_binding_invalid_registry")
    canonical_json_bytes(value, max_bytes=4 * 1024 * 1024)


def validate_system_manifest_bundle(
    manifest_bytes_by_system_id: Mapping[str, bytes],
) -> dict[tuple[str, str], dict[str, Any]]:
    """Validate the exact eight-system E0 set and every matched-control link."""

    if not isinstance(manifest_bytes_by_system_id, Mapping) or len(manifest_bytes_by_system_id) != 8:
        raise ArtifactValidationError("engine_binding_invalid_system")
    manifests: dict[tuple[str, str], dict[str, Any]] = {}
    system_ids: set[str] = set()
    for supplied_system_id, raw in manifest_bytes_by_system_id.items():
        if not isinstance(supplied_system_id, str) or not isinstance(raw, bytes) or len(raw) > 4 * 1024 * 1024:
            raise ArtifactValidationError("engine_binding_invalid_system")
        try:
            value = strict_json_loads(raw, prefix="system_manifest")
        except CanonicalError as error:
            raise ArtifactValidationError("engine_binding_invalid_system") from error
        validate_system_artifact_manifest(value)
        assert isinstance(value, dict)
        if supplied_system_id != value["system_id"] or value["system_id"] in system_ids:
            raise ArtifactValidationError("engine_binding_invalid_system")
        key = (value["condition"], value["system_variant"])
        if key in manifests:
            raise ArtifactValidationError("engine_binding_invalid_system")
        manifests[key] = value
        system_ids.add(value["system_id"])
    if set(manifests) != ALLOWED_SYSTEMS:
        raise ArtifactValidationError("engine_binding_invalid_system")

    reference = manifests[("C00", "BASE")]
    stable_fields = (
        "executed_source_closure",
        "provider_binding",
        "resource_binding",
        "environment_binding",
        "analysis_binding",
    )
    for manifest in manifests.values():
        if any(manifest[field] != reference[field] for field in stable_fields):
            raise ArtifactValidationError("engine_binding_invalid_system")

    matched_bases = {
        ("C00", "CAPACITY_CONTROL"): ("C01", "BASE"),
        ("C10", "CAPACITY_CONTROL"): ("C11", "BASE"),
        ("C01", "SUPERVISION_CONTROL"): ("C01", "BASE"),
        ("C11", "SUPERVISION_CONTROL"): ("C11", "BASE"),
    }
    for control_key, base_key in matched_bases.items():
        control = manifests[control_key]
        base = manifests[base_key]
        model = control["model_binding"]
        if (
            model["matched_system_id"] != base["system_id"]
            or model["matched_system_artifact_manifest_sha256"]
            != system_artifact_manifest_sha256(base)
        ):
            raise ArtifactValidationError("engine_binding_invalid_system")
    return manifests


def _validate_environment(value: object) -> None:
    fields = (*RUNTIME_FIELDS, "container_image_digest")
    if not exact_keys(value, fields):
        raise ArtifactValidationError("engine_binding_invalid_environment")
    assert isinstance(value, dict)
    for field in (
        "runtime_tag",
        "python_implementation",
        "platform_tag",
        "architecture",
        "math_backend_id",
    ):
        if not _valid_identity_string(value[field]):
            raise ArtifactValidationError("engine_binding_invalid_environment")
    if not isinstance(value["python_version"], str) or _VERSION.fullmatch(value["python_version"]) is None:
        raise ArtifactValidationError("engine_binding_invalid_environment")
    if not isinstance(value["unicode_version"], str) or _VERSION.fullmatch(value["unicode_version"]) is None:
        raise ArtifactValidationError("engine_binding_invalid_environment")
    if not is_sha256(value["math_backend_sha256"]) or value["float_contract"] != "IEEE754_BINARY64_RNE" or value["container_image_digest"] is not None:
        raise ArtifactValidationError("engine_binding_invalid_environment")


def system_artifact_manifest_bytes(value: object) -> bytes:
    validate_system_artifact_manifest(value)
    return canonical_json_bytes(value, max_bytes=4 * 1024 * 1024)


def system_artifact_manifest_sha256(value: object) -> str:
    return sha256(system_artifact_manifest_bytes(value)).hexdigest()


def identity_provider_manifest(vmp_sha256: str) -> dict[str, Any]:
    if not is_sha256(vmp_sha256):
        raise ArtifactValidationError("engine_provider_invalid_output")
    return {
        "manifest_version": "1.0.0",
        "vmp_sha256": vmp_sha256,
        "provider_config_id": "provider_identity_bypass",
        "provider_mode": "IDENTITY_BYPASS",
        "normalizer_id": "normalizer_identity",
        "rewrite_spans": [],
        "units": [],
    }


def identity_provider_manifest_sha256(vmp_sha256: str) -> str:
    return canonical_sha256(identity_provider_manifest(vmp_sha256), max_bytes=4 * 1024 * 1024)


def validate_eligible_spans(spans: object, *, text: str, visible_artifacts: Sequence[dict[str, Any]]) -> None:
    if not isinstance(spans, list) or len(spans) > 64:
        raise ArtifactValidationError("engine_invalid_eligibility")
    previous_end = -1
    artifact_ranges = [(row.get("start"), row.get("end")) for row in visible_artifacts]
    for index, span in enumerate(spans):
        if not exact_keys(span, ("span_index", "start", "end", "source_text")):
            raise ArtifactValidationError("engine_invalid_eligibility")
        start, end = span["start"], span["end"]
        if (
            span["span_index"] != index
            or not is_nonboolean_int(start, minimum=0)
            or not is_nonboolean_int(end, minimum=1, maximum=len(text))
            or start >= end
            or start < previous_end
            or span["source_text"] != text[start:end]
        ):
            raise ArtifactValidationError("engine_invalid_eligibility")
        if any(isinstance(a, int) and isinstance(b, int) and start < b and a < end for a, b in artifact_ranges):
            raise ArtifactValidationError("engine_invalid_eligibility")
        previous_end = end


_PROVIDER_OUTCOMES = {
    "NOT_INVOKED",
    "ELIGIBILITY_INVALID",
    "NO_ELIGIBLE",
    "SUCCEEDED",
    "UNAVAILABLE_FALLBACK",
    "TIMEOUT_FALLBACK",
    "PROVIDER_INVALID_OUTPUT",
    "NORMALIZER_INVALID_OUTPUT",
}


def build_provider_execution(
    *,
    system_manifest: dict[str, Any],
    eligible_spans: list[dict[str, Any]],
    outcome: str,
    provider_manifest_sha256: str | None,
    failure_code: str = "NONE",
    configured_mode: str = "COMPOSED_SPAN",
) -> dict[str, Any]:
    provider = system_manifest["provider_binding"]
    attempted = outcome in {
        "SUCCEEDED",
        "UNAVAILABLE_FALLBACK",
        "TIMEOUT_FALLBACK",
        "PROVIDER_INVALID_OUTPUT",
        "NORMALIZER_INVALID_OUTPUT",
    }
    accepted = outcome in {"NO_ELIGIBLE", "SUCCEEDED", "UNAVAILABLE_FALLBACK", "TIMEOUT_FALLBACK"}
    bypass = (
        "NO_ELIGIBLE_ROMANIZED_SPAN"
        if outcome == "NO_ELIGIBLE"
        else "PROVIDER_FAILURE_RAW_FALLBACK"
        if outcome in {"UNAVAILABLE_FALLBACK", "TIMEOUT_FALLBACK"}
        else "NONE"
    )
    value = {
        "configured_mode": configured_mode,
        "provider_config_id": provider["provider_config_id"],
        "provider_config_sha256": provider["provider_config_sha256"],
        "normalizer_id": provider["normalizer_id"],
        "normalizer_sha256": provider["normalizer_sha256"],
        "eligible_spans": eligible_spans,
        "invocation_attempted": attempted,
        "outcome": outcome,
        "output_accepted": accepted,
        "bypass_reason": bypass,
        "failure_code": failure_code,
        "provider_manifest_sha256": provider_manifest_sha256,
    }
    validate_provider_execution(value)
    return value


def validate_provider_execution(value: object) -> None:
    if not exact_keys(value, PROVIDER_EXECUTION_FIELDS):
        raise ArtifactValidationError("engine_provider_invalid_output")
    assert isinstance(value, dict)
    if value["configured_mode"] not in {"COMPOSED_SPAN", "DIRECT_FULL_PATH"}:
        raise ArtifactValidationError("engine_provider_invalid_output")
    if not isinstance(value["provider_config_id"], str) or _PROVIDER_ID.fullmatch(value["provider_config_id"]) is None:
        raise ArtifactValidationError("engine_provider_invalid_output")
    if not isinstance(value["normalizer_id"], str) or _NORMALIZER_ID.fullmatch(value["normalizer_id"]) is None:
        raise ArtifactValidationError("engine_provider_invalid_output")
    if not is_sha256(value["provider_config_sha256"]) or not is_sha256(value["normalizer_sha256"]):
        raise ArtifactValidationError("engine_provider_invalid_output")
    if value["outcome"] not in _PROVIDER_OUTCOMES or not isinstance(value["eligible_spans"], list):
        raise ArtifactValidationError("engine_provider_invalid_output")
    previous_end = 0
    for index, span in enumerate(value["eligible_spans"]):
        if not exact_keys(span, ("span_index", "start", "end", "source_text")):
            raise ArtifactValidationError("engine_provider_invalid_output")
        start, end = span["start"], span["end"]
        if (
            span["span_index"] != index
            or not is_nonboolean_int(start, minimum=0)
            or not is_nonboolean_int(end, minimum=1)
            or start >= end
            or start < previous_end
            or not isinstance(span["source_text"], str)
            or len(span["source_text"]) != end - start
        ):
            raise ArtifactValidationError("engine_provider_invalid_output")
        previous_end = end
    if not isinstance(value["invocation_attempted"], bool) or not isinstance(value["output_accepted"], bool):
        raise ArtifactValidationError("engine_provider_invalid_output")
    outcome = value["outcome"]
    spans = value["eligible_spans"]
    expected = {
        "NOT_INVOKED": (False, False, "NONE", "PROVIDER_NOT_INVOKED", False),
        "ELIGIBILITY_INVALID": (False, False, "NONE", "ELIGIBILITY_INVALID", False),
        "NO_ELIGIBLE": (False, True, "NO_ELIGIBLE_ROMANIZED_SPAN", "NONE", True),
        "SUCCEEDED": (True, True, "NONE", "NONE", True),
        "PROVIDER_INVALID_OUTPUT": (True, False, "NONE", "PROVIDER_INVALID_OUTPUT", False),
        "NORMALIZER_INVALID_OUTPUT": (True, False, "NONE", "NORMALIZER_INVALID_OUTPUT", False),
    }
    if outcome in expected:
        attempted, accepted, bypass, failure, has_hash = expected[outcome]
        if (value["invocation_attempted"], value["output_accepted"], value["bypass_reason"], value["failure_code"], is_sha256(value["provider_manifest_sha256"])) != (attempted, accepted, bypass, failure, has_hash):
            raise ArtifactValidationError("engine_provider_invalid_output")
        if outcome in {"ELIGIBILITY_INVALID", "NO_ELIGIBLE"} and spans:
            raise ArtifactValidationError("engine_provider_invalid_output")
        if outcome in {"NOT_INVOKED", "SUCCEEDED", "PROVIDER_INVALID_OUTPUT", "NORMALIZER_INVALID_OUTPUT"} and not 1 <= len(spans) <= 64:
            raise ArtifactValidationError("engine_provider_invalid_output")
    else:
        allowed_failures = {
            "UNAVAILABLE_FALLBACK": {"PROVIDER_UNAVAILABLE", "NORMALIZER_UNAVAILABLE"},
            "TIMEOUT_FALLBACK": {"PROVIDER_TIMEOUT", "NORMALIZER_TIMEOUT"},
        }[outcome]
        if (
            not value["invocation_attempted"]
            or not value["output_accepted"]
            or value["bypass_reason"] != "PROVIDER_FAILURE_RAW_FALLBACK"
            or value["failure_code"] not in allowed_failures
            or not is_sha256(value["provider_manifest_sha256"])
            or not 1 <= len(spans) <= 64
        ):
            raise ArtifactValidationError("engine_provider_invalid_output")


def identity_candidate_artifacts(text: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    alignment = [[index, index + 1] for index in range(len(text))]
    path_hash = canonical_sha256({"text": text, "alignment": alignment})
    path = {
        "path_id": "candidate_path_identity",
        "path_sha256": path_hash,
        "lineage": {
            "lineage_version": "1.0.0",
            "contributors": [{"mode": "IDENTITY_BYPASS"}],
        },
        "composition_score_f64_bits": float_to_f64_bits(0.0),
        "q_numerator_f64_bits": float_to_f64_bits(1.0),
        "q_f64_bits": float_to_f64_bits(1.0),
        "effective_rewrite_spans": [],
    }
    diagnostics = {
        "mode": "IDENTITY_BYPASS",
        "temperature_f64_bits": float_to_f64_bits(1.0),
        "search_mode": "IDENTITY_BYPASS",
        "input_count": 1,
        "span_merge_reduction_count": 0,
        "partial_merge_reduction_count": 0,
        "full_merge_reduction_count": 0,
        "total_merge_reduction_count": 0,
        "postmerge_count": 1,
        "returned_count": 1,
        "preK_scope": "EXACT_FULL",
        "L_returned_f64_bits": float_to_f64_bits(0.0),
        "L_preK_f64_bits": float_to_f64_bits(0.0),
        "retained_preK_composition_mass_f64_bits": float_to_f64_bits(1.0),
        "q_normalizer_f64_bits": float_to_f64_bits(1.0),
        "q_max_f64_bits": float_to_f64_bits(0.0),
    }
    return diagnostics, [path]


def build_five_seed_logit_artifact(
    *,
    system_artifact_manifest_sha256: str,
    vmp_sha256: str,
    active_path_ids: Sequence[str],
    seed_logits: Sequence[Sequence[float]],
) -> dict[str, Any]:
    if len(seed_logits) != 5 or not active_path_ids or any(len(row) != len(active_path_ids) for row in seed_logits):
        raise ArtifactValidationError("engine_binding_invalid_path")
    means = [sequential_mean([seed_logits[row][column] for row in range(5)]) for column in range(len(active_path_ids))]
    artifact = {
        "schema_version": "1.0.0",
        "system_artifact_manifest_sha256": system_artifact_manifest_sha256,
        "vmp_sha256": vmp_sha256,
        "active_path_ids": list(active_path_ids),
        "seeds": [11, 23, 37, 53, 71],
        "seed_logits_f64_bits": [[float_to_f64_bits(value) for value in row] for row in seed_logits],
        "mean_logits_f64_bits": [float_to_f64_bits(value) for value in means],
    }
    validate_five_seed_logit_artifact(artifact)
    return artifact


def validate_five_seed_logit_artifact(value: object) -> None:
    fields = (
        "schema_version",
        "system_artifact_manifest_sha256",
        "vmp_sha256",
        "active_path_ids",
        "seeds",
        "seed_logits_f64_bits",
        "mean_logits_f64_bits",
    )
    if not exact_keys(value, fields):
        raise ArtifactValidationError("engine_binding_invalid_path")
    assert isinstance(value, dict)
    ids = value["active_path_ids"]
    rows = value["seed_logits_f64_bits"]
    if value["schema_version"] != "1.0.0" or not is_sha256(value["system_artifact_manifest_sha256"]) or not is_sha256(value["vmp_sha256"]):
        raise ArtifactValidationError("engine_binding_invalid_path")
    if not isinstance(ids, list) or not ids or not all(isinstance(item, str) and _PATH_ID.fullmatch(item) for item in ids) or len(set(ids)) != len(ids):
        raise ArtifactValidationError("engine_binding_invalid_path")
    if value["seeds"] != [11, 23, 37, 53, 71] or not isinstance(rows, list) or len(rows) != 5 or any(not isinstance(row, list) or len(row) != len(ids) for row in rows):
        raise ArtifactValidationError("engine_binding_invalid_path")
    if not isinstance(value["mean_logits_f64_bits"], list) or len(value["mean_logits_f64_bits"]) != len(ids):
        raise ArtifactValidationError("engine_binding_invalid_path")
    try:
        decoded = [[f64_bits_to_float(bits) for bits in row] for row in rows]
        decoded_means = [f64_bits_to_float(bits) for bits in value["mean_logits_f64_bits"]]
    except CanonicalError as error:
        raise ArtifactValidationError("engine_candidate_nonfinite") from error
    expected = [sequential_mean([decoded[row][column] for row in range(5)]) for column in range(len(ids))]
    if [float_to_f64_bits(item) for item in expected] != [float_to_f64_bits(item) for item in decoded_means]:
        raise ArtifactValidationError("engine_binding_invalid_path")
    canonical_json_bytes(value, max_bytes=1024 * 1024)


def five_seed_logit_artifact_bytes(value: object) -> bytes:
    validate_five_seed_logit_artifact(value)
    return canonical_json_bytes(value, max_bytes=1024 * 1024)


def five_seed_logit_artifact_sha256(value: object) -> str:
    return sha256(five_seed_logit_artifact_bytes(value)).hexdigest()


def build_failure_counts(**counts: int | str) -> dict[str, int | str]:
    missing = set(FAILURE_COUNT_FIELDS) - set(counts)
    extra = set(counts) - set(FAILURE_COUNT_FIELDS)
    if missing or extra:
        raise ArtifactValidationError("engine_envelope_invalid_payload")
    value = {field: counts[field] for field in FAILURE_COUNT_FIELDS}
    _validate_failure_counts(value)
    return value


def zero_failure_counts() -> dict[str, int]:
    return {field: 0 for field in FAILURE_COUNT_FIELDS}


def _validate_failure_counts(value: object) -> None:
    if not exact_keys(value, FAILURE_COUNT_FIELDS):
        raise ArtifactValidationError("engine_envelope_invalid_payload")
    assert isinstance(value, dict)
    for field, item in value.items():
        maximum = 65 if field == "configured_span_entries_capped" else 64 if field == "eligible_spans_capped" else 65_534
        if item == "GE_65535" and field not in {"configured_span_entries_capped", "eligible_spans_capped"}:
            continue
        if not is_nonboolean_int(item, minimum=0, maximum=maximum):
            raise ArtifactValidationError("engine_envelope_invalid_payload")
    if all(isinstance(value[field], int) and not isinstance(value[field], bool) for field in FAILURE_COUNT_FIELDS):
        if value["total"] != sum(value[field] for field in FAILURE_COUNT_FIELDS[1:]):
            raise ArtifactValidationError("engine_envelope_invalid_payload")


def _validate_candidate_diagnostics(value: object) -> None:
    if not exact_keys(value, _CANDIDATE_DIAGNOSTIC_FIELDS):
        raise ArtifactValidationError("engine_candidate_invalid_arithmetic")
    assert isinstance(value, dict)
    allowed_pairs = {
        ("COMPOSED_SPAN", "EXACT"),
        ("COMPOSED_SPAN", "BEAM"),
        ("DIRECT_FULL_PATH", "DIRECT_FULL_PATH"),
        ("IDENTITY_BYPASS", "IDENTITY_BYPASS"),
    }
    if (value["mode"], value["search_mode"]) not in allowed_pairs:
        raise ArtifactValidationError("engine_candidate_invalid_arithmetic")
    try:
        temperature = f64_bits_to_float(value["temperature_f64_bits"])
        l_returned = f64_bits_to_float(value["L_returned_f64_bits"])
        l_pre_k = f64_bits_to_float(value["L_preK_f64_bits"])
        retained_mass = f64_bits_to_float(value["retained_preK_composition_mass_f64_bits"])
        q_normalizer = f64_bits_to_float(value["q_normalizer_f64_bits"])
        for field in (
            "q_max_f64_bits",
        ):
            f64_bits_to_float(value[field])
    except CanonicalError as error:
        raise ArtifactValidationError("engine_candidate_nonfinite") from error
    delta = l_returned - l_pre_k
    if (
        temperature <= 0.0
        or q_normalizer <= 0.0
        or delta > 0.0
        or float_to_f64_bits(math.exp(delta)) != float_to_f64_bits(retained_mass)
        or value["preK_scope"] not in {"EXACT_FULL", "FINAL_BEAM"}
        or (value["search_mode"] == "BEAM") is not (value["preK_scope"] == "FINAL_BEAM")
    ):
        raise ArtifactValidationError("engine_candidate_invalid_arithmetic")
    count_fields = (
        "input_count", "span_merge_reduction_count", "partial_merge_reduction_count",
        "full_merge_reduction_count", "total_merge_reduction_count", "postmerge_count", "returned_count",
    )
    if not all(is_nonboolean_int(value[field], minimum=0, maximum=65_535) for field in count_fields):
        raise ArtifactValidationError("engine_candidate_invalid_arithmetic")
    if not 1 <= value["input_count"] <= 512 or not 1 <= value["postmerge_count"] <= 64 or not 1 <= value["returned_count"] <= min(8, value["postmerge_count"]):
        raise ArtifactValidationError("engine_candidate_invalid_arithmetic")
    if value["total_merge_reduction_count"] != sum(value[field] for field in ("span_merge_reduction_count", "partial_merge_reduction_count", "full_merge_reduction_count")):
        raise ArtifactValidationError("engine_candidate_invalid_arithmetic")
    if value["mode"] == "IDENTITY_BYPASS" and any(value[field] != 0 for field in ("span_merge_reduction_count", "partial_merge_reduction_count", "full_merge_reduction_count", "total_merge_reduction_count")):
        raise ArtifactValidationError("engine_candidate_invalid_arithmetic")
    if value["mode"] == "IDENTITY_BYPASS" and (
        (value["input_count"], value["postmerge_count"], value["returned_count"]) != (1, 1, 1)
        or any(
            value[field] != expected
            for field, expected in (
                ("L_returned_f64_bits", float_to_f64_bits(0.0)),
                ("L_preK_f64_bits", float_to_f64_bits(0.0)),
                ("retained_preK_composition_mass_f64_bits", float_to_f64_bits(1.0)),
                ("q_normalizer_f64_bits", float_to_f64_bits(1.0)),
                ("q_max_f64_bits", float_to_f64_bits(0.0)),
            )
        )
    ):
        raise ArtifactValidationError("engine_candidate_invalid_arithmetic")


def _valid_path_rows(paths: object) -> bool:
    if not isinstance(paths, list) or not 1 <= len(paths) <= 8:
        return False
    ids: list[str] = []
    for path in paths:
        fields = (
            "path_id",
            "path_sha256",
            "lineage",
            "composition_score_f64_bits",
            "q_numerator_f64_bits",
            "q_f64_bits",
            "effective_rewrite_spans",
        )
        if not exact_keys(path, fields) or not isinstance(path["path_id"], str) or _PATH_ID.fullmatch(path["path_id"]) is None or not is_sha256(path["path_sha256"]):
            return False
        try:
            for field in ("composition_score_f64_bits", "q_numerator_f64_bits", "q_f64_bits"):
                f64_bits_to_float(path[field])
        except CanonicalError:
            return False
        if not _valid_lineage(path["lineage"]) or not isinstance(path["effective_rewrite_spans"], list):
            return False
        ids.append(path["path_id"])
    return len(set(ids)) == len(ids)


def _valid_lineage(value: object) -> bool:
    if not exact_keys(value, ("lineage_version", "contributors")):
        return False
    assert isinstance(value, dict)
    contributors = value["contributors"]
    if value["lineage_version"] != "1.0.0" or not isinstance(contributors, list) or not contributors:
        return False
    try:
        encoded = [canonical_json_bytes(contributor) for contributor in contributors]
    except CanonicalError:
        return False
    if encoded != sorted(encoded) or len(encoded) != len(set(encoded)):
        return False
    for contributor in contributors:
        if not isinstance(contributor, dict):
            return False
        mode = contributor.get("mode")
        if mode == "IDENTITY_BYPASS":
            if not exact_keys(contributor, ("mode",)):
                return False
        elif mode == "DIRECT_FULL_PATH":
            if not exact_keys(contributor, ("mode", "unit_index", "ranks")) or contributor["unit_index"] != 0 or not _valid_rank_list(contributor["ranks"]):
                return False
        elif mode == "COMPOSED_SPAN":
            if not exact_keys(contributor, ("mode", "units")) or not isinstance(contributor["units"], list) or not contributor["units"]:
                return False
            for index, unit in enumerate(contributor["units"]):
                if not exact_keys(unit, ("unit_index", "ranks")) or unit["unit_index"] != index or not _valid_rank_list(unit["ranks"]):
                    return False
        else:
            return False
    return True


def _valid_rank_list(value: object) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and value == sorted(set(value))
        and all(is_nonboolean_int(rank, minimum=1, maximum=8) for rank in value)
    )


def _validate_path_numeric(paths: list[dict[str, Any]], diagnostics: Mapping[str, Any]) -> None:
    try:
        temperature = f64_bits_to_float(diagnostics["temperature_f64_bits"])
        maximum = f64_bits_to_float(diagnostics["q_max_f64_bits"])
        denominator = f64_bits_to_float(diagnostics["q_normalizer_f64_bits"])
        for path in paths:
            score = f64_bits_to_float(path["composition_score_f64_bits"])
            numerator = f64_bits_to_float(path["q_numerator_f64_bits"])
            q = f64_bits_to_float(path["q_f64_bits"])
            expected_numerator = math.exp(score / temperature - maximum)
            if (
                numerator <= 0.0
                or not 0.0 <= q <= 1.0
                or float_to_f64_bits(numerator) != float_to_f64_bits(expected_numerator)
                or float_to_f64_bits(q) != float_to_f64_bits(numerator / denominator)
            ):
                raise ArtifactValidationError("engine_candidate_invalid_arithmetic")
    except (CanonicalError, KeyError, ZeroDivisionError, OverflowError) as error:
        raise ArtifactValidationError("engine_candidate_invalid_arithmetic") from error


def build_engine_run_envelope(
    *,
    preflight_context: Any,
    validation_context: EngineValidationContext,
    provider_execution: dict[str, Any],
    failure_stage: str,
    failure_counts: dict[str, Any],
    candidate_diagnostics: dict[str, Any] | None,
    candidate_paths: list[dict[str, Any]],
    active_path_ids: list[str],
    five_seed_logit_artifact_sha256: str | None,
    prediction_audit_sha256: str | None = None,
    sep_packet_hashes: list[dict[str, str]] | None = None,
    feature_plan_id: str | None = None,
    feature_tensor_hashes: list[dict[str, str]] | None = None,
    execution_status: str = "VALID",
    invalid_codes: list[str] | None = None,
) -> dict[str, Any]:
    from .preflight import ValidatedPreflightContext

    if (
        not isinstance(preflight_context, ValidatedPreflightContext)
        or validation_context.preflight is not preflight_context
    ):
        raise ArtifactValidationError("engine_binding_invalid_system")
    preflight_receipt = preflight_context.receipt
    system_manifest = preflight_context.system_manifest
    registry = system_manifest["registry_binding"]
    value = {
        "schema_version": "1.1.0",
        "run_id": preflight_receipt["run_id"],
        "condition": preflight_receipt["condition"],
        "system_id": preflight_receipt["system_id"],
        "system_variant": preflight_receipt["system_variant"],
        "system_artifact_manifest_sha256": preflight_receipt["system_artifact_manifest_sha256"],
        "runtime": runtime_from_environment(system_manifest["environment_binding"]),
        "vmp": {"item_id": preflight_receipt["item_id"], "vmp_sha256": preflight_receipt["vmp_sha256"]},
        "provider_execution": provider_execution,
        "failure_stage": failure_stage,
        "failure_counts": failure_counts,
        "candidate_diagnostics": candidate_diagnostics,
        "candidate_paths": candidate_paths,
        "active_path_ids": active_path_ids,
        "five_seed_logit_artifact_sha256": five_seed_logit_artifact_sha256,
        "prediction_audit_sha256": prediction_audit_sha256,
        "sep_packet_hashes": sep_packet_hashes or [],
        "feature_plan_id": feature_plan_id,
        "feature_tensor_hashes": feature_tensor_hashes or [],
        "registry_snapshot_id": registry["registry_snapshot_id"],
        "registry_artifact_sha256": registry["registry_artifact_sha256"],
        "resolver_version": registry["resolver_version"],
        "execution_status": execution_status,
        "invalid_codes": invalid_codes or [],
    }
    validate_engine_envelope(value, context=validation_context)
    return value


def _validate_hash_rows(rows: object, *, active_ids: list[str]) -> bool:
    if not isinstance(rows, list) or len(rows) != len(active_ids):
        return False
    return all(
        exact_keys(row, ("path_id", "sha256"))
        and row["path_id"] == active_ids[index]
        and is_sha256(row["sha256"])
        for index, row in enumerate(rows)
    )


def _validate_engine_envelope_shape(
    value: object,
    *,
    system_manifest: dict[str, Any] | None = None,
    preflight_receipt: dict[str, Any] | None = None,
) -> None:
    if not exact_keys(value, ENGINE_ENVELOPE_FIELDS):
        raise ArtifactValidationError("engine_envelope_invalid_payload")
    assert isinstance(value, dict)
    if value["schema_version"] != "1.1.0" or not isinstance(value["run_id"], str) or _RUN_ID.fullmatch(value["run_id"]) is None:
        raise ArtifactValidationError("engine_envelope_invalid_payload")
    if (value["condition"], value["system_variant"]) not in ALLOWED_SYSTEMS or not isinstance(value["system_id"], str) or _SYSTEM_ID.fullmatch(value["system_id"]) is None or not is_sha256(value["system_artifact_manifest_sha256"]):
        raise ArtifactValidationError("engine_binding_invalid_system")
    if not exact_keys(value["runtime"], RUNTIME_FIELDS) or not exact_keys(value["vmp"], ("item_id", "vmp_sha256")) or not is_sha256(value["vmp"]["vmp_sha256"]):
        raise ArtifactValidationError("engine_envelope_invalid_payload")
    validate_provider_execution(value["provider_execution"])
    _validate_failure_counts(value["failure_counts"])
    semantic = semantic_enabled(value["condition"], value["system_variant"])
    registry_values = (value["registry_snapshot_id"], value["registry_artifact_sha256"], value["resolver_version"])
    if semantic:
        if not (_valid_identity_string(registry_values[0]) and is_sha256(registry_values[1]) and _valid_identity_string(registry_values[2])):
            raise ArtifactValidationError("engine_binding_invalid_registry")
    elif any(item is not None for item in registry_values):
        raise ArtifactValidationError("engine_binding_invalid_registry")
    status = value["execution_status"]
    if status not in {"VALID", "DEGRADED_STOP_AFTER_IDENTITY", "INVALID"}:
        raise ArtifactValidationError("engine_envelope_invalid_payload")
    if not isinstance(value["invalid_codes"], list) or value["invalid_codes"] != sorted(set(value["invalid_codes"])):
        raise ArtifactValidationError("engine_envelope_invalid_payload")
    if status == "VALID":
        if value["failure_stage"] != "NONE" or value["invalid_codes"] or not _valid_path_rows(value["candidate_paths"]):
            raise ArtifactValidationError("engine_envelope_invalid_payload")
        if value["provider_execution"]["outcome"] not in {"SUCCEEDED", "NO_ELIGIBLE"}:
            raise ArtifactValidationError("engine_envelope_invalid_payload")
        _validate_candidate_diagnostics(value["candidate_diagnostics"])
        _validate_path_numeric(value["candidate_paths"], value["candidate_diagnostics"])
        if value["provider_execution"]["outcome"] == "NO_ELIGIBLE":
            if value["candidate_diagnostics"]["mode"] != "IDENTITY_BYPASS" or any(path["effective_rewrite_spans"] for path in value["candidate_paths"]):
                raise ArtifactValidationError("engine_envelope_invalid_payload")
        elif value["candidate_diagnostics"]["mode"] != value["provider_execution"]["configured_mode"]:
            raise ArtifactValidationError("engine_envelope_invalid_payload")
        expected_active = [value["candidate_paths"][0]["path_id"]] if not all_paths_active(value["condition"], value["system_variant"]) else [row["path_id"] for row in value["candidate_paths"]]
        if value["active_path_ids"] != expected_active or value["candidate_diagnostics"] is None or not is_sha256(value["five_seed_logit_artifact_sha256"]):
            raise ArtifactValidationError("engine_binding_invalid_path")
        if semantic:
            if not is_sha256(value["prediction_audit_sha256"]) or value["feature_plan_id"] != "E0_VMP_CATEGORY_MEAN_V1" or not _validate_hash_rows(value["sep_packet_hashes"], active_ids=expected_active) or not _validate_hash_rows(value["feature_tensor_hashes"], active_ids=expected_active):
                raise ArtifactValidationError("engine_binding_invalid_condition_mask")
        elif value["prediction_audit_sha256"] is not None or value["sep_packet_hashes"] or value["feature_plan_id"] is not None or value["feature_tensor_hashes"]:
            raise ArtifactValidationError("engine_binding_invalid_condition_mask")
    elif status == "DEGRADED_STOP_AFTER_IDENTITY":
        provider_outcome = value["provider_execution"]["outcome"]
        if value["failure_stage"] != "PROVIDER_EXECUTION" or value["invalid_codes"] or provider_outcome not in {"UNAVAILABLE_FALLBACK", "TIMEOUT_FALLBACK"}:
            raise ArtifactValidationError("engine_envelope_invalid_payload")
        if not _valid_path_rows(value["candidate_paths"]) or len(value["candidate_paths"]) != 1 or value["active_path_ids"] != [value["candidate_paths"][0]["path_id"]]:
            raise ArtifactValidationError("engine_envelope_invalid_payload")
        _validate_candidate_diagnostics(value["candidate_diagnostics"])
        _validate_path_numeric(value["candidate_paths"], value["candidate_diagnostics"])
        if value["candidate_diagnostics"]["mode"] != "IDENTITY_BYPASS" or value["candidate_paths"][0]["effective_rewrite_spans"]:
            raise ArtifactValidationError("engine_envelope_invalid_payload")
        if value["five_seed_logit_artifact_sha256"] is not None or value["prediction_audit_sha256"] is not None or value["sep_packet_hashes"] or value["feature_plan_id"] is not None or value["feature_tensor_hashes"]:
            raise ArtifactValidationError("engine_binding_invalid_condition_mask")
    else:
        stage = value["failure_stage"]
        if stage not in _INVALID_STAGE_CODES or not value["invalid_codes"] or not set(value["invalid_codes"]).issubset(_INVALID_STAGE_CODES[stage]):
            raise ArtifactValidationError("engine_envelope_invalid_payload")
        has_candidates = stage in {"PREDICTION", "SEP", "FEATURE", "BINDING", "ENVELOPE"}
        if has_candidates:
            if not _valid_path_rows(value["candidate_paths"]) or value["candidate_diagnostics"] is None:
                raise ArtifactValidationError("engine_envelope_invalid_payload")
            _validate_candidate_diagnostics(value["candidate_diagnostics"])
            _validate_path_numeric(value["candidate_paths"], value["candidate_diagnostics"])
            expected_active = [value["candidate_paths"][0]["path_id"]] if not all_paths_active(value["condition"], value["system_variant"]) else [row["path_id"] for row in value["candidate_paths"]]
            if value["active_path_ids"] != expected_active:
                raise ArtifactValidationError("engine_binding_invalid_path")
        elif value["candidate_diagnostics"] is not None or value["candidate_paths"] or value["active_path_ids"]:
            raise ArtifactValidationError("engine_envelope_invalid_payload")
        if stage == "PROVIDER_EXECUTION":
            if value["provider_execution"]["outcome"] not in {"ELIGIBILITY_INVALID", "NOT_INVOKED", "PROVIDER_INVALID_OUTPUT", "NORMALIZER_INVALID_OUTPUT"}:
                raise ArtifactValidationError("engine_envelope_invalid_payload")
        elif value["provider_execution"]["outcome"] not in {"SUCCEEDED", "NO_ELIGIBLE"}:
            raise ArtifactValidationError("engine_envelope_invalid_payload")
        if stage in {"PROVIDER_EXECUTION", "CANDIDATE", "PREDICTION"}:
            if value["five_seed_logit_artifact_sha256"] is not None or value["prediction_audit_sha256"] is not None or value["sep_packet_hashes"] or value["feature_plan_id"] is not None or value["feature_tensor_hashes"]:
                raise ArtifactValidationError("engine_envelope_invalid_payload")
        elif stage == "SEP":
            if not is_sha256(value["five_seed_logit_artifact_sha256"]):
                raise ArtifactValidationError("engine_envelope_invalid_payload")
            if semantic and not is_sha256(value["prediction_audit_sha256"]):
                raise ArtifactValidationError("engine_envelope_invalid_payload")
            if value["sep_packet_hashes"] or value["feature_plan_id"] is not None or value["feature_tensor_hashes"]:
                raise ArtifactValidationError("engine_envelope_invalid_payload")
        elif stage == "FEATURE":
            if not semantic or not is_sha256(value["five_seed_logit_artifact_sha256"]) or not is_sha256(value["prediction_audit_sha256"]):
                raise ArtifactValidationError("engine_envelope_invalid_payload")
            if not _validate_hash_rows(value["sep_packet_hashes"], active_ids=value["active_path_ids"]):
                raise ArtifactValidationError("engine_envelope_invalid_payload")
            if value["feature_plan_id"] is not None or value["feature_tensor_hashes"]:
                raise ArtifactValidationError("engine_envelope_invalid_payload")
        elif stage in {"BINDING", "ENVELOPE"}:
            if not is_sha256(value["five_seed_logit_artifact_sha256"]):
                raise ArtifactValidationError("engine_envelope_invalid_payload")
            if semantic:
                if not is_sha256(value["prediction_audit_sha256"]) or value["feature_plan_id"] != "E0_VMP_CATEGORY_MEAN_V1" or not _validate_hash_rows(value["sep_packet_hashes"], active_ids=value["active_path_ids"]) or not _validate_hash_rows(value["feature_tensor_hashes"], active_ids=value["active_path_ids"]):
                    raise ArtifactValidationError("engine_envelope_invalid_payload")
            elif value["prediction_audit_sha256"] is not None or value["sep_packet_hashes"] or value["feature_plan_id"] is not None or value["feature_tensor_hashes"]:
                raise ArtifactValidationError("engine_envelope_invalid_payload")
    if system_manifest is not None:
        validate_system_artifact_manifest(system_manifest)
        if system_artifact_manifest_sha256(system_manifest) != value["system_artifact_manifest_sha256"]:
            raise ArtifactValidationError("engine_binding_invalid_system")
        if (system_manifest["condition"], system_manifest["system_id"], system_manifest["system_variant"]) != (value["condition"], value["system_id"], value["system_variant"]):
            raise ArtifactValidationError("engine_binding_invalid_system")
        if runtime_from_environment(system_manifest["environment_binding"]) != value["runtime"]:
            raise ArtifactValidationError("engine_binding_invalid_environment")
        provider = system_manifest["provider_binding"]
        execution = value["provider_execution"]
        if (execution["provider_config_id"], execution["provider_config_sha256"], execution["normalizer_id"], execution["normalizer_sha256"]) != (provider["provider_config_id"], provider["provider_config_sha256"], provider["normalizer_id"], provider["normalizer_sha256"]):
            raise ArtifactValidationError("engine_binding_invalid_system")
        registry = system_manifest["registry_binding"]
        if registry_values != (registry["registry_snapshot_id"], registry["registry_artifact_sha256"], registry["resolver_version"]):
            raise ArtifactValidationError("engine_binding_invalid_registry")
    if preflight_receipt is not None:
        expected = (
            preflight_receipt.get("run_id"),
            preflight_receipt.get("condition"),
            preflight_receipt.get("system_id"),
            preflight_receipt.get("system_variant"),
            preflight_receipt.get("system_artifact_manifest_sha256"),
            preflight_receipt.get("item_id"),
            preflight_receipt.get("vmp_sha256"),
        )
        actual = (
            value["run_id"], value["condition"], value["system_id"], value["system_variant"],
            value["system_artifact_manifest_sha256"], value["vmp"]["item_id"], value["vmp"]["vmp_sha256"],
        )
        if preflight_receipt.get("status") != "PASS" or expected != actual:
            raise ArtifactValidationError("engine_binding_invalid_system")
    canonical_json_bytes(value, max_bytes=1024 * 1024)


def _provider_reading_count(manifest: Mapping[str, Any] | None) -> int:
    if manifest is None:
        return 0
    units = manifest.get("units")
    if not isinstance(units, list):
        return 0
    return sum(
        len(unit["readings"])
        for unit in units
        if isinstance(unit, dict) and isinstance(unit.get("readings"), list)
    )


def _exact_failure_counts(
    value: Mapping[str, Any],
    *,
    provider_manifest: Mapping[str, Any] | None,
    candidate_replay: Any | None,
    semantic_replay: Any | None,
    retained_prediction_count: int = 0,
    retained_pair_count: int = 0,
) -> dict[str, int]:
    execution = value["provider_execution"]
    spans = execution["eligible_spans"]
    configured = 0 if execution["outcome"] == "NO_ELIGIBLE" else len(spans)
    eligible = 0 if execution["outcome"] in {"NO_ELIGIBLE", "ELIGIBILITY_INVALID"} else len(spans)
    provider_count = _provider_reading_count(provider_manifest)
    normalizer_count = provider_count if candidate_replay is not None else 0
    candidate_count = 0 if candidate_replay is None else len(candidate_replay.internal_paths)
    alignment_count = (
        0
        if candidate_replay is None
        else sum(len(path.alignment) for path in candidate_replay.internal_paths)
    )
    prediction_count = 0 if semantic_replay is not None else retained_prediction_count
    pair_count = 0 if semantic_replay is not None else retained_pair_count
    feature_count = 0
    if semantic_replay is not None:
        audit = strict_json_loads(
            semantic_replay.prediction_audit_bytes, prefix="prediction_audit"
        )
        prediction_count = sum(
            len(path["endpoint_candidates"])
            for path in audit["path_predictions"]
        )
        for path in semantic_replay.paths:
            packet = strict_json_loads(path.pair_packet_bytes, prefix="pair_packet")
            tensor = strict_json_loads(path.feature_tensor_bytes, prefix="feature_tensor")
            pair_count += len(packet["pairs"])
            feature_count += sum(tensor["pair_mask"])
    binding = 6 + len(value["active_path_ids"])
    if value["five_seed_logit_artifact_sha256"] is not None:
        binding += 1
    if value["registry_snapshot_id"] is not None:
        binding += 3
    binding += len(value["sep_packet_hashes"]) + len(value["feature_tensor_hashes"])
    counts = {
        "configured_span_entries_capped": configured,
        "eligible_spans_capped": eligible,
        "provider": provider_count,
        "normalizer": normalizer_count,
        "candidate": candidate_count,
        "alignment": alignment_count,
        "prediction": prediction_count,
        "sep": pair_count,
        "feature": feature_count,
        "binding": binding,
        "envelope": len(ENGINE_ENVELOPE_FIELDS),
    }
    return {"total": sum(counts.values()), **counts}


def _validate_engine_envelope_complete(
    raw: bytes,
    value: dict[str, Any],
    context: EngineValidationContext,
) -> ValidatedEngineEnvelope:
    from .candidate import (
        CandidateValidationError,
        _parse_provider_manifest_for_replay,
        parse_provider_execution,
        replay_candidate_run,
    )
    from .preflight import ValidatedPreflightContext
    from .semantic import (
        SemanticValidationError,
        build_pair_packet,
        frozen_registry_from_artifact,
        parse_prediction_audit_structural,
        replay_semantic_chain,
        validate_prediction_audit,
    )

    if not isinstance(context, EngineValidationContext) or not isinstance(
        context.preflight, ValidatedPreflightContext
    ):
        raise ArtifactValidationError("engine_envelope_invalid_payload")
    preflight = context.preflight
    receipt = preflight.receipt
    system_manifest = preflight.system_manifest
    _validate_engine_envelope_shape(
        value,
        system_manifest=system_manifest,
        preflight_receipt=receipt,
    )
    vmp = strict_json_loads(preflight.vmp_bytes, prefix="vmp")
    if (
        not isinstance(vmp, dict)
        or sha256(preflight.vmp_bytes).hexdigest() != value["vmp"]["vmp_sha256"]
        or preflight.vmp_item_id != value["vmp"]["item_id"]
    ):
        raise ArtifactValidationError("engine_binding_invalid_path")

    try:
        execution = parse_provider_execution(context.provider_execution_bytes)
        if execution != value["provider_execution"]:
            raise ArtifactValidationError("engine_envelope_invalid_payload")
        provider_binding = system_manifest["provider_binding"]
        if (
            execution["provider_config_id"],
            execution["provider_config_sha256"],
            execution["normalizer_id"],
            execution["normalizer_sha256"],
        ) != (
            provider_binding["provider_config_id"],
            provider_binding["provider_config_sha256"],
            provider_binding["normalizer_id"],
            provider_binding["normalizer_sha256"],
        ):
            raise ArtifactValidationError("engine_binding_invalid_system")

        candidate_replay = None
        provider_manifest = None
        retained_candidates = value["candidate_diagnostics"] is not None
        if retained_candidates:
            if context.provider_manifest_bytes is None or context.candidate_diagnostics_bytes is None:
                raise ArtifactValidationError("engine_envelope_invalid_payload")
            path_ids = [row["path_id"] for row in value["candidate_paths"]]
            if set(context.candidate_path_artifact_bytes) != set(path_ids):
                raise ArtifactValidationError("engine_binding_invalid_path")
            candidate_replay = replay_candidate_run(
                vmp_text=vmp["text"],
                vmp_sha256=value["vmp"]["vmp_sha256"],
                visible_artifacts=vmp["visible_artifacts"],
                provider_manifest_bytes=context.provider_manifest_bytes,
                provider_execution_bytes=context.provider_execution_bytes,
                candidate_diagnostics_bytes=context.candidate_diagnostics_bytes,
                candidate_path_artifact_bytes=[
                    context.candidate_path_artifact_bytes[path_id]
                    for path_id in path_ids
                ],
            )
            provider_manifest = candidate_replay.provider_manifest
            if (
                candidate_replay.provider_execution != value["provider_execution"]
                or candidate_replay.candidate_diagnostics != value["candidate_diagnostics"]
                or list(candidate_replay.candidate_paths) != value["candidate_paths"]
            ):
                raise ArtifactValidationError("engine_envelope_invalid_payload")
        else:
            if context.candidate_diagnostics_bytes is not None or context.candidate_path_artifact_bytes:
                raise ArtifactValidationError("engine_envelope_invalid_payload")
            if context.provider_manifest_bytes is not None:
                provider_manifest, _ = _parse_provider_manifest_for_replay(
                    context.provider_manifest_bytes,
                    vmp_text=vmp["text"],
                    vmp_sha256=value["vmp"]["vmp_sha256"],
                    visible_artifacts=vmp["visible_artifacts"],
                    execution=execution,
                )
            elif execution["provider_manifest_sha256"] is not None:
                raise ArtifactValidationError("engine_envelope_invalid_payload")

        active_paths: tuple[Any, ...] = ()
        if candidate_replay is not None:
            paths_by_id = {path.path_id: path for path in candidate_replay.internal_paths}
            if any(path_id not in paths_by_id for path_id in value["active_path_ids"]):
                raise ArtifactValidationError("engine_binding_invalid_path")
            active_paths = tuple(paths_by_id[path_id] for path_id in value["active_path_ids"])

        if value["five_seed_logit_artifact_sha256"] is None:
            if context.five_seed_artifact_bytes is not None:
                raise ArtifactValidationError("engine_binding_invalid_path")
        else:
            if context.five_seed_artifact_bytes is None:
                raise ArtifactValidationError("engine_binding_invalid_path")
            seed = strict_json_loads(
                context.five_seed_artifact_bytes, prefix="five_seed_artifact"
            )
            validate_five_seed_logit_artifact(seed)
            if (
                sha256(context.five_seed_artifact_bytes).hexdigest()
                != value["five_seed_logit_artifact_sha256"]
                or seed["system_artifact_manifest_sha256"]
                != value["system_artifact_manifest_sha256"]
                or seed["vmp_sha256"] != value["vmp"]["vmp_sha256"]
                or seed["active_path_ids"] != value["active_path_ids"]
            ):
                raise ArtifactValidationError("engine_binding_invalid_path")

        semantic_mask = semantic_enabled(value["condition"], value["system_variant"])
        semantic_replay = None
        retained_prediction_count = 0
        retained_pair_count = 0
        if semantic_mask:
            if context.registry_artifact_bytes is None:
                raise ArtifactValidationError("engine_binding_invalid_registry")
            registry = frozen_registry_from_artifact(
                context.registry_artifact_bytes,
                expected_sha256=value["registry_artifact_sha256"],
            )
            if (
                registry.registry_snapshot_id != value["registry_snapshot_id"]
                or registry.resolver_version != value["resolver_version"]
            ):
                raise ArtifactValidationError("engine_binding_invalid_registry")
            if value["prediction_audit_sha256"] is not None:
                if context.prediction_audit_bytes is None:
                    raise ArtifactValidationError("engine_binding_invalid_condition_mask")
                audit = parse_prediction_audit_structural(
                    context.prediction_audit_bytes, vmp_text=vmp["text"]
                )
                audit_hash = validate_prediction_audit(
                    audit, vmp_text=vmp["text"], expected_paths=active_paths
                )
                if (
                    audit_hash != value["prediction_audit_sha256"]
                    or audit["vmp_sha256"] != value["vmp"]["vmp_sha256"]
                    or sha256(context.prediction_audit_bytes).hexdigest() != audit_hash
                ):
                    raise ArtifactValidationError("engine_binding_invalid_path")
                retained_prediction_count = sum(
                    len(path["endpoint_candidates"])
                    for path in audit["path_predictions"]
                )
                if value["feature_plan_id"] == "E0_VMP_CATEGORY_MEAN_V1":
                    packet_hashes = {row["path_id"]: row["sha256"] for row in value["sep_packet_hashes"]}
                    tensor_hashes = {row["path_id"]: row["sha256"] for row in value["feature_tensor_hashes"]}
                    semantic_replay = replay_semantic_chain(
                        vmp_text=vmp["text"],
                        vmp_sha256=value["vmp"]["vmp_sha256"],
                        prediction_audit_bytes=context.prediction_audit_bytes,
                        registry_artifact_bytes=context.registry_artifact_bytes,
                        pair_packet_bytes_by_path=context.pair_packet_bytes_by_path,
                        semantic_feature_plan_bytes_by_path=context.semantic_feature_plan_bytes_by_path,
                        feature_tensor_bytes_by_path=context.feature_tensor_bytes_by_path,
                        active_paths=active_paths,
                        expected_prediction_audit_sha256=value["prediction_audit_sha256"],
                        expected_registry_artifact_sha256=value["registry_artifact_sha256"],
                        expected_pair_packet_sha256_by_path=packet_hashes,
                        expected_feature_tensor_sha256_by_path=tensor_hashes,
                    )
                else:
                    if context.semantic_feature_plan_bytes_by_path or context.feature_tensor_bytes_by_path:
                        raise ArtifactValidationError("engine_binding_invalid_condition_mask")
                    packet_hashes = {
                        row["path_id"]: row["sha256"]
                        for row in value["sep_packet_hashes"]
                    }
                    if set(context.pair_packet_bytes_by_path) != set(packet_hashes):
                        raise ArtifactValidationError("engine_binding_invalid_path")
                    predictions = {
                        row["path_id"]: row for row in audit["path_predictions"]
                    }
                    for path_id, expected_hash in packet_hashes.items():
                        packet, packet_hash = build_pair_packet(
                            vmp_sha256=value["vmp"]["vmp_sha256"],
                            vmp_length=len(vmp["text"]),
                            path_prediction=predictions[path_id],
                            resolver=registry,
                        )
                        expected_raw = canonical_json_bytes(packet)
                        if (
                            packet_hash != expected_hash
                            or context.pair_packet_bytes_by_path[path_id] != expected_raw
                            or sha256(expected_raw).hexdigest() != expected_hash
                        ):
                            raise ArtifactValidationError("engine_binding_invalid_path")
                        retained_pair_count += len(packet["pairs"])
            elif (
                context.prediction_audit_bytes is not None
                or context.pair_packet_bytes_by_path
                or context.semantic_feature_plan_bytes_by_path
                or context.feature_tensor_bytes_by_path
            ):
                raise ArtifactValidationError("engine_binding_invalid_condition_mask")
        elif any(
            item is not None
            for item in (
                context.prediction_audit_bytes,
                context.registry_artifact_bytes,
            )
        ) or any(
            (
                context.pair_packet_bytes_by_path,
                context.semantic_feature_plan_bytes_by_path,
                context.feature_tensor_bytes_by_path,
            )
        ):
            raise ArtifactValidationError("engine_binding_invalid_condition_mask")

        expected_counts = _exact_failure_counts(
            value,
            provider_manifest=provider_manifest,
            candidate_replay=candidate_replay,
            semantic_replay=semantic_replay,
            retained_prediction_count=retained_prediction_count,
            retained_pair_count=retained_pair_count,
        )
        if value["failure_counts"] != expected_counts:
            raise ArtifactValidationError("engine_envelope_invalid_payload")
    except CandidateValidationError as error:
        if "mismatch" in error.code:
            raise ArtifactValidationError("engine_binding_invalid_path") from error
        raise ArtifactValidationError("engine_envelope_invalid_payload") from error
    except SemanticValidationError as error:
        if "registry" in error.code and "mismatch" in error.code:
            raise ArtifactValidationError("engine_binding_invalid_registry") from error
        if (
            "mismatch" in error.code
            or "candidate" in error.code
            or error.code == "semantic_invalid_lookup_render"
        ):
            raise ArtifactValidationError("engine_binding_invalid_path") from error
        raise ArtifactValidationError("engine_envelope_invalid_payload") from error
    except (KeyError, TypeError) as error:
        raise ArtifactValidationError("engine_envelope_invalid_payload") from error
    return ValidatedEngineEnvelope(
        canonical_bytes=raw,
        active_paths=active_paths,
        candidate_replay=candidate_replay,
        semantic_replay=semantic_replay,
    )


def validate_engine_envelope(
    value: object, *, context: EngineValidationContext
) -> ValidatedEngineEnvelope:
    try:
        raw = canonical_json_bytes(value, max_bytes=1024 * 1024)
    except (CanonicalError, MemoryError, RecursionError) as error:
        raise ArtifactValidationError("engine_envelope_invalid_payload") from error
    if not isinstance(value, dict):
        raise ArtifactValidationError("engine_envelope_invalid_payload")
    return _validate_engine_envelope_complete(raw, value, context)


def validate_engine_envelope_bytes(
    raw: bytes, *, context: EngineValidationContext
) -> ValidatedEngineEnvelope:
    if not isinstance(raw, bytes) or len(raw) > 1024 * 1024:
        raise ArtifactValidationError("engine_envelope_invalid_payload")
    try:
        value = strict_json_loads(raw, prefix="engine_envelope")
    except (CanonicalError, MemoryError, RecursionError) as error:
        raise ArtifactValidationError("engine_envelope_invalid_payload") from error
    if not isinstance(value, dict):
        raise ArtifactValidationError("engine_envelope_invalid_payload")
    return _validate_engine_envelope_complete(raw, value, context)


def engine_envelope_bytes(
    value: object, *, context: EngineValidationContext
) -> bytes:
    return validate_engine_envelope(value, context=context).canonical_bytes


def engine_run_envelope_sha256(
    value: object, *, context: EngineValidationContext
) -> str:
    return validate_engine_envelope(value, context=context).sha256


__all__ = [
    "ALLOWED_SYSTEMS",
    "ArtifactValidationError",
    "EngineValidationContext",
    "ValidatedEngineEnvelope",
    "build_engine_run_envelope",
    "build_environment_binding",
    "build_failure_counts",
    "build_five_seed_logit_artifact",
    "build_provider_execution",
    "build_system_artifact_manifest",
    "engine_envelope_bytes",
    "engine_run_envelope_sha256",
    "five_seed_logit_artifact_bytes",
    "five_seed_logit_artifact_sha256",
    "identity_candidate_artifacts",
    "identity_provider_manifest",
    "identity_provider_manifest_sha256",
    "runtime_from_environment",
    "semantic_enabled",
    "synthetic_hash",
    "system_artifact_manifest_bytes",
    "system_artifact_manifest_sha256",
    "validate_eligible_spans",
    "validate_engine_envelope",
    "validate_engine_envelope_bytes",
    "validate_five_seed_logit_artifact",
    "validate_provider_execution",
    "validate_system_artifact_manifest",
    "validate_system_manifest_bundle",
    "zero_failure_counts",
]
