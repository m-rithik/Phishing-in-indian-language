"""Canonical synthetic-E0 evaluation boundary for Fisher.

This module deliberately separates three trust boundaries:

1. raw evaluation-universe parsing;
2. raw submitted-inference parsing and universe-hash binding; and
3. semantic closure, envelope accounting, and metric calculation.

A failure at either raw boundary emits only its receipt.  Pair metrics are
available only after a complete, ordered, discrepancy-free metric run.
"""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import math
from pathlib import Path
import re
from types import MappingProxyType
from typing import Any, BinaryIO, Callable, Mapping, Sequence

from ._canonical import (
    CanonicalError,
    canonical_json_bytes,
    exact_keys,
    is_nonboolean_int,
    is_sha256,
    read_cap_plus_one,
    strict_json_loads,
)
from ._numeric import sequential_mean, sequential_sum


UNIVERSE_SCHEMA_VERSION = "1.0.0"
GOLD_INVENTORY_VERSION = "1.0.0"
METRIC_UNIVERSE_RECEIPT_VERSION = "1.0.0"
METRIC_INPUT_VERSION = "1.0.0"
METRIC_RUN_VERSION = "1.1.0"

UNIVERSE_MAX_BYTES = 32 * 1024 * 1024
UNIVERSE_READ_BYTES = UNIVERSE_MAX_BYTES + 1
GOLD_INVENTORY_MAX_BYTES = 2 * 1024 * 1024
RECEIPT_MAX_BYTES = 64 * 1024
MAX_UNIVERSE_ENTRIES = 10_000
MAX_SUBMISSION_ROWS = 20_000
MAX_GOLD_REFERENCE_EVIDENCE_IDS = 10_000

_ITEM_ID = re.compile(r"item_[a-z0-9][a-z0-9_-]{0,62}\Z")
_ANNOTATION_ID = re.compile(r"annotation_[a-z0-9][a-z0-9_-]{0,62}\Z")
_REFERENCE_ID = re.compile(r"registry_reference_[a-z0-9][a-z0-9_-]{0,44}\Z")
_EVIDENCE_ID = re.compile(r"registry_evidence_[a-z0-9][a-z0-9_-]{0,45}\Z")
_SNAPSHOT_ID = re.compile(r"registry_[a-z0-9][a-z0-9_-]{0,62}\Z")
_RESOLVER_VERSION = re.compile(
    r"resolver_[0-9]{1,6}\.[0-9]{1,6}\.[0-9]{1,6}"
    r"(?:-[a-z0-9][a-z0-9.-]{0,31})?\Z"
)
_UNIVERSE_ID = re.compile(r"evaluation_universe_[a-z0-9][a-z0-9_-]{0,55}\Z")
_UNIVERSE_RECEIPT_ID = re.compile(
    r"metric_universe_input_[a-z0-9][a-z0-9_-]{0,50}\Z"
)
_METRIC_INPUT_RECEIPT_ID = re.compile(r"metric_input_[a-z0-9][a-z0-9_-]{0,59}\Z")
_METRIC_RUN_ID = re.compile(r"metric_run_[a-z0-9][a-z0-9_-]{0,62}\Z")
_SYSTEM_ID = re.compile(r"system_[a-z0-9][a-z0-9_-]{0,62}\Z")

_PARTITIONS = {"development", "primary_test", "external_test"}
_CONDITIONS = {"C01", "C11"}
_VARIANTS = {"BASE"}
_DESTINATION_KINDS = {"URL", "DOMAIN", "PHONE", "UPI", "BANK", "EMAIL", "APP", "OTHER"}
_REFERENCE_LABELS = {"MATCH", "MISMATCH", "UNKNOWN"}
_REFERENCE_COVERAGE = {"complete", "partial", "missing"}

_UNIVERSE_FIELDS = (
    "schema_version",
    "universe_id",
    "partition",
    "dataset_artifact_hashes",
    "registry_reference_bundle_sha256",
    "entries",
)
_DATASET_HASH_FIELDS = (
    "items_jsonl_sha256",
    "annotations_jsonl_sha256",
    "registry_manifest_jsonl_sha256",
    "registry_references_jsonl_sha256",
)
_UNIVERSE_ENTRY_FIELDS = (
    "item_id",
    "partition",
    "vmp_sha256",
    "final_annotation_id",
    "gold_inventory_size_bytes",
    "gold_inventory_sha256",
    "gold_pair_count",
    "gold_empty",
)
_GOLD_FIELDS = (
    "inventory_version",
    "item_id",
    "vmp_sha256",
    "final_annotation_id",
    "actors",
    "destinations",
    "registry_references",
)
_GOLD_ACTOR_FIELDS = ("span_index", "start", "end", "text")
_GOLD_DESTINATION_FIELDS = ("span_index", "start", "end", "text", "kind")
_GOLD_REFERENCE_FIELDS = (
    "registry_reference_id",
    "actor_span_index",
    "destination_span_index",
    "label",
    "registry_coverage",
    "registry_evidence_ids",
    "registry_snapshot_id",
    "resolver_version",
)
_SUBMISSION_FIELDS = (
    "schema_version",
    "evaluation_universe_sha256",
    "system_artifact_manifest_sha256",
    "entries",
)
_SUBMISSION_ENTRY_FIELDS = ("item_id", "envelope_sha256")
_REGISTRY_BUNDLE_FIELDS = (
    "schema_version",
    "registry_snapshot_id",
    "resolver_version",
    "registry_manifest_sha256",
    "registry_references_sha256",
)
_METRIC_RUN_FIELDS = (
    "schema_version",
    "metric_run_id",
    "condition",
    "system_id",
    "system_variant",
    "system_artifact_manifest_sha256",
    "evaluation_universe_sha256",
    "registry_reference_bundle_sha256",
    "submitted_inference_manifest_sha256",
    "inference_envelopes",
    "N_all",
    "N_gold_empty",
    "N_gold_nonempty",
    "universe_error_count",
    "denominator_error_count",
    "submitted_count",
    "missing_count",
    "extra_count",
    "duplicate_count",
    "reordered_count",
    "degraded_count",
    "invalid_count",
    "mismatch_count",
    "status",
    "invalid_codes",
)

class EvaluationError(ValueError):
    """A fail-closed evaluation error with a controlled diagnostic code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


class EvaluationBindingError(EvaluationError):
    """A canonical artifact exists but does not match its declared binding."""


@dataclass(frozen=True)
class CanonicalArtifact:
    value: dict[str, Any]
    data: bytes
    sha256: str


@dataclass(frozen=True)
class MetricUniverseParseResult:
    receipt: dict[str, Any]
    receipt_bytes: bytes
    receipt_sha256: str
    universe: dict[str, Any] | None


@dataclass(frozen=True)
class MetricInputParseResult:
    receipt: dict[str, Any] | None
    receipt_bytes: bytes | None
    receipt_sha256: str | None
    manifest: dict[str, Any] | None
    manifest_bytes: bytes | None
    manifest_sha256: str | None


@dataclass(frozen=True)
class UniverseSemanticContext:
    """Evidence needed to prove that a universe is the complete frozen closure.

    ``expected_entries`` is derived from the four validated dataset artifacts,
    not from model output.  Supplying it explicitly keeps dataset validation and
    metric execution separate while still requiring byte-for-byte closure.
    """

    expected_entries: tuple[dict[str, Any], ...]
    dataset_artifact_hashes: dict[str, str]
    registry_reference_bundle: dict[str, Any]
    gold_inventory_bytes: Mapping[str, bytes]
    vmp_text_by_item_id: Mapping[str, str]


PairKey = tuple[int, int, int, int, str]


@dataclass(frozen=True)
class PathPairPrediction:
    path_id: str
    q: float
    pairs: frozenset[PairKey]


@dataclass(frozen=True)
class _EnvelopeEvidence:
    """Metric-safe view returned by the engine-artifact integration layer.

    The inspector producing this object must first validate the complete engine
    envelope and its referenced SEP artifacts.  Evaluation then checks every
    cross-artifact identity and binding before accepting the row.
    """

    execution_status: str
    item_id: str
    vmp_sha256: str
    condition: str
    system_id: str
    system_variant: str
    system_artifact_manifest_sha256: str
    registry_snapshot_id: str | None
    registry_artifact_sha256: str | None
    resolver_version: str | None
    paths: tuple[PathPairPrediction, ...] = ()


_EnvelopeInspector = Callable[[bytes], _EnvelopeEvidence]


@dataclass(frozen=True)
class MetricArtifactBytes:
    """Complete exact-byte evidence for all submitted engine envelopes.

    The envelope hash is the key of ``envelopes``.  Each value retains every
    independently persisted artifact needed to replay preflight, candidate,
    registry, semantic, seed, and envelope construction.  Evaluation never
    manufactures missing evidence by serializing an object embedded elsewhere.
    """

    project_root: Path
    system_manifest_bundle: Mapping[str, bytes]
    envelopes: Mapping[str, "MetricEnvelopeArtifactBytes"]

    def __post_init__(self) -> None:
        if not isinstance(self.project_root, Path):
            raise EvaluationError("metric_invalid_artifact_store")
        if not isinstance(self.system_manifest_bundle, Mapping) or any(
            not isinstance(key, str) or not isinstance(raw, bytes)
            for key, raw in self.system_manifest_bundle.items()
        ):
            raise EvaluationError("metric_invalid_artifact_store")
        if not isinstance(self.envelopes, Mapping) or any(
            not is_sha256(key) or not isinstance(value, MetricEnvelopeArtifactBytes)
            for key, value in self.envelopes.items()
        ):
            raise EvaluationError("metric_invalid_artifact_store")
        object.__setattr__(
            self,
            "system_manifest_bundle",
            MappingProxyType(dict(self.system_manifest_bundle)),
        )
        object.__setattr__(self, "envelopes", MappingProxyType(dict(self.envelopes)))


@dataclass(frozen=True)
class MetricEnvelopeArtifactBytes:
    engine_envelope_bytes: bytes
    engine_input_descriptor_bytes: bytes
    preflight_receipt_bytes: bytes
    vmp_artifact_bytes: bytes
    system_manifest_bytes: bytes
    provider_manifest_bytes: bytes | None
    provider_execution_bytes: bytes
    candidate_diagnostics_bytes: bytes | None
    candidate_path_artifact_bytes: Mapping[str, bytes]
    registry_artifact_bytes: bytes | None
    prediction_audit_bytes: bytes | None
    pair_packet_bytes_by_path: Mapping[str, bytes]
    semantic_feature_plan_bytes_by_path: Mapping[str, bytes]
    feature_tensor_bytes_by_path: Mapping[str, bytes]
    five_seed_artifact_bytes: bytes | None

    def __post_init__(self) -> None:
        required_bytes = (
            "engine_envelope_bytes",
            "engine_input_descriptor_bytes",
            "preflight_receipt_bytes",
            "vmp_artifact_bytes",
            "system_manifest_bytes",
            "provider_execution_bytes",
        )
        optional_bytes = (
            "provider_manifest_bytes",
            "candidate_diagnostics_bytes",
            "registry_artifact_bytes",
            "prediction_audit_bytes",
            "five_seed_artifact_bytes",
        )
        if any(not isinstance(getattr(self, field), bytes) for field in required_bytes):
            raise EvaluationError("metric_invalid_artifact_store")
        if any(
            value is not None and not isinstance(value, bytes)
            for value in (getattr(self, field) for field in optional_bytes)
        ):
            raise EvaluationError("metric_invalid_artifact_store")
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
                raise EvaluationError("metric_invalid_artifact_store")
            object.__setattr__(self, field, MappingProxyType(dict(value)))


@dataclass(frozen=True)
class MetricRunResult:
    manifest: dict[str, Any]
    manifest_bytes: bytes
    manifest_sha256: str
    pair_metrics: dict[str, Any] | None


@dataclass(frozen=True)
class EvaluationBoundaryResult:
    universe_result: MetricUniverseParseResult
    input_result: MetricInputParseResult | None
    metric_run: MetricRunResult | None


def _fullmatch(pattern: re.Pattern[str], value: object) -> bool:
    return isinstance(value, str) and pattern.fullmatch(value) is not None


def _ordered_unique_strings(values: object, pattern: re.Pattern[str], maximum: int) -> bool:
    return (
        isinstance(values, list)
        and len(values) <= maximum
        and all(_fullmatch(pattern, value) for value in values)
        and values == sorted(values, key=lambda value: value.encode("utf-8"))
        and len(values) == len(set(values))
    )


def _artifact(value: dict[str, Any], *, max_bytes: int) -> CanonicalArtifact:
    data = canonical_json_bytes(value, max_bytes=max_bytes)
    return CanonicalArtifact(value=value, data=data, sha256=sha256(data).hexdigest())


def _validation_failure(error: Exception) -> EvaluationError:
    """Translate validator failures without conflating unreadable and tampered data."""

    code = getattr(error, "code", "")
    if isinstance(code, str) and any(
        marker in code for marker in ("binding", "mismatch", "hash_mismatch", "tamper")
    ):
        return EvaluationBindingError("metric_artifact_binding_mismatch")
    return EvaluationError("metric_invalid_referenced_artifact")


def _make_engine_envelope_inspector(
    artifacts: MetricArtifactBytes,
) -> _EnvelopeInspector:
    """Create the private authoritative exact-artifact inspector.

    This is deliberately not a public extension point.  Public metric entry
    points always construct it from ``MetricArtifactBytes`` so callers cannot
    replace validation with an accepting callback.
    """

    from ._numeric import f64_bits_to_float
    from .artifacts import EngineValidationContext, validate_engine_envelope_bytes
    from .preflight import SuppliedVMPArtifact, validate_pass_preflight_context
    from .semantic import replay_semantic_chain

    def inspect(raw: bytes) -> _EnvelopeEvidence:
        envelope_hash = sha256(raw).hexdigest()
        bundle = artifacts.envelopes.get(envelope_hash)
        if bundle is None:
            raise EvaluationError("metric_missing_referenced_artifact")
        if not isinstance(bundle, MetricEnvelopeArtifactBytes):
            raise EvaluationError("metric_invalid_referenced_artifact")
        if bundle.engine_envelope_bytes != raw:
            raise EvaluationBindingError("metric_referenced_artifact_hash_mismatch")

        try:
            descriptor = strict_json_loads(
                bundle.engine_input_descriptor_bytes,
                prefix="metric_engine_input_descriptor",
            )
            vmp = strict_json_loads(bundle.vmp_artifact_bytes, prefix="metric_vmp")
            if not isinstance(descriptor, dict) or not isinstance(vmp, dict):
                raise CanonicalError("metric_invalid_referenced_artifact")
            item_id = descriptor.get("item_id")
            if not isinstance(item_id, str):
                raise CanonicalError("metric_invalid_referenced_artifact")
            supplied_vmp = SuppliedVMPArtifact(item_id, bundle.vmp_artifact_bytes)
            preflight = validate_pass_preflight_context(
                descriptor_bytes=bundle.engine_input_descriptor_bytes,
                receipt_bytes=bundle.preflight_receipt_bytes,
                system_manifest_bytes=bundle.system_manifest_bytes,
                supplied_vmp=supplied_vmp,
                project_root=artifacts.project_root,
                system_manifest_bundle=artifacts.system_manifest_bundle,
            )
            validation_context = EngineValidationContext(
                preflight=preflight,
                provider_manifest_bytes=bundle.provider_manifest_bytes,
                provider_execution_bytes=bundle.provider_execution_bytes,
                candidate_diagnostics_bytes=bundle.candidate_diagnostics_bytes,
                candidate_path_artifact_bytes=bundle.candidate_path_artifact_bytes,
                five_seed_artifact_bytes=bundle.five_seed_artifact_bytes,
                prediction_audit_bytes=bundle.prediction_audit_bytes,
                registry_artifact_bytes=bundle.registry_artifact_bytes,
                pair_packet_bytes_by_path=bundle.pair_packet_bytes_by_path,
                semantic_feature_plan_bytes_by_path=(
                    bundle.semantic_feature_plan_bytes_by_path
                ),
                feature_tensor_bytes_by_path=bundle.feature_tensor_bytes_by_path,
            )
            validated = validate_engine_envelope_bytes(raw, context=validation_context)
        except (CanonicalError, ValueError, TypeError, KeyError) as error:
            raise _validation_failure(error) from error

        envelope = validated.value
        status = envelope["execution_status"]
        common = {
            "execution_status": status,
            "item_id": envelope["vmp"]["item_id"],
            "vmp_sha256": envelope["vmp"]["vmp_sha256"],
            "condition": envelope["condition"],
            "system_id": envelope["system_id"],
            "system_variant": envelope["system_variant"],
            "system_artifact_manifest_sha256": envelope[
                "system_artifact_manifest_sha256"
            ],
            "registry_snapshot_id": envelope["registry_snapshot_id"],
            "registry_artifact_sha256": envelope["registry_artifact_sha256"],
            "resolver_version": envelope["resolver_version"],
        }
        if status != "VALID":
            return _EnvelopeEvidence(**common)
        if (
            bundle.registry_artifact_bytes is None
            or bundle.prediction_audit_bytes is None
            or not isinstance(vmp.get("text"), str)
        ):
            raise EvaluationError("metric_missing_referenced_artifact")

        expected_packets = {
            row["path_id"]: row["sha256"] for row in envelope["sep_packet_hashes"]
        }
        expected_tensors = {
            row["path_id"]: row["sha256"]
            for row in envelope["feature_tensor_hashes"]
        }
        try:
            replay = replay_semantic_chain(
                vmp_text=vmp["text"],
                vmp_sha256=envelope["vmp"]["vmp_sha256"],
                prediction_audit_bytes=bundle.prediction_audit_bytes,
                registry_artifact_bytes=bundle.registry_artifact_bytes,
                pair_packet_bytes_by_path=bundle.pair_packet_bytes_by_path,
                semantic_feature_plan_bytes_by_path=(
                    bundle.semantic_feature_plan_bytes_by_path
                ),
                feature_tensor_bytes_by_path=bundle.feature_tensor_bytes_by_path,
                active_paths=validated.active_paths,
                expected_prediction_audit_sha256=envelope[
                    "prediction_audit_sha256"
                ],
                expected_registry_artifact_sha256=envelope[
                    "registry_artifact_sha256"
                ],
                expected_pair_packet_sha256_by_path=expected_packets,
                expected_feature_tensor_sha256_by_path=expected_tensors,
            )
        except (CanonicalError, ValueError, TypeError, KeyError) as error:
            raise _validation_failure(error) from error

        paths: list[PathPairPrediction] = []
        for path in replay.paths:
            try:
                q = f64_bits_to_float(path.q_f64_bits)
            except CanonicalError as error:
                raise EvaluationError("metric_invalid_path_weight") from error
            pairs = frozenset(row[:5] for row in path.registry_pair_tuples)
            if len(pairs) != len(path.registry_pair_tuples):
                raise EvaluationError("metric_duplicate_pair")
            paths.append(PathPairPrediction(path.path_id, q, pairs))
        return _EnvelopeEvidence(**common, paths=tuple(paths))

    return inspect


def _valid_span_endpoint(value: object, fields: Sequence[str], *, vmp_text: str | None) -> bool:
    if not exact_keys(value, fields):
        return False
    assert isinstance(value, dict)
    if not is_nonboolean_int(value["span_index"], minimum=0):
        return False
    if not is_nonboolean_int(value["start"], minimum=0):
        return False
    if not is_nonboolean_int(value["end"], minimum=1) or value["start"] >= value["end"]:
        return False
    if not isinstance(value["text"], str):
        return False
    if vmp_text is not None:
        if value["end"] > len(vmp_text) or vmp_text[value["start"] : value["end"]] != value["text"]:
            return False
    if fields == _GOLD_DESTINATION_FIELDS and value["kind"] not in _DESTINATION_KINDS:
        return False
    return True


def _valid_gold_reference(value: object) -> bool:
    if not exact_keys(value, _GOLD_REFERENCE_FIELDS):
        return False
    assert isinstance(value, dict)
    if not _fullmatch(_REFERENCE_ID, value["registry_reference_id"]):
        return False
    if not is_nonboolean_int(value["actor_span_index"], minimum=0):
        return False
    if not is_nonboolean_int(value["destination_span_index"], minimum=0):
        return False
    if value["label"] not in _REFERENCE_LABELS or value["registry_coverage"] not in _REFERENCE_COVERAGE:
        return False
    if not _ordered_unique_strings(
        value["registry_evidence_ids"], _EVIDENCE_ID, MAX_GOLD_REFERENCE_EVIDENCE_IDS
    ):
        return False
    if not _fullmatch(_SNAPSHOT_ID, value["registry_snapshot_id"]):
        return False
    if not _fullmatch(_RESOLVER_VERSION, value["resolver_version"]):
        return False
    evidence = value["registry_evidence_ids"]
    if value["label"] in {"MATCH", "MISMATCH"}:
        return value["registry_coverage"] == "complete" and bool(evidence)
    return value["registry_coverage"] in {"partial", "missing"}


def gold_inventory_artifact(
    inventory: dict[str, Any],
    *,
    vmp_text: str | None = None,
    expected_entry: Mapping[str, Any] | None = None,
) -> CanonicalArtifact:
    """Validate and serialize one complete canonical gold inventory."""

    if not exact_keys(inventory, _GOLD_FIELDS):
        raise EvaluationError("gold_inventory_schema")
    if inventory["inventory_version"] != GOLD_INVENTORY_VERSION:
        raise EvaluationError("gold_inventory_schema")
    if not _fullmatch(_ITEM_ID, inventory["item_id"]):
        raise EvaluationError("gold_inventory_schema")
    if not is_sha256(inventory["vmp_sha256"]):
        raise EvaluationError("gold_inventory_schema")
    if not _fullmatch(_ANNOTATION_ID, inventory["final_annotation_id"]):
        raise EvaluationError("gold_inventory_schema")

    actors = inventory["actors"]
    destinations = inventory["destinations"]
    references = inventory["registry_references"]
    if not isinstance(actors, list) or not isinstance(destinations, list) or not isinstance(references, list):
        raise EvaluationError("gold_inventory_schema")
    if not all(_valid_span_endpoint(value, _GOLD_ACTOR_FIELDS, vmp_text=vmp_text) for value in actors):
        raise EvaluationError("gold_inventory_actor")
    if not all(
        _valid_span_endpoint(value, _GOLD_DESTINATION_FIELDS, vmp_text=vmp_text)
        for value in destinations
    ):
        raise EvaluationError("gold_inventory_destination")
    actor_indices = [value["span_index"] for value in actors]
    destination_indices = [value["span_index"] for value in destinations]
    if actor_indices != sorted(actor_indices) or len(actor_indices) != len(set(actor_indices)):
        raise EvaluationError("gold_inventory_actor_order")
    if destination_indices != sorted(destination_indices) or len(destination_indices) != len(set(destination_indices)):
        raise EvaluationError("gold_inventory_destination_order")
    if not all(_valid_gold_reference(value) for value in references):
        raise EvaluationError("gold_inventory_reference")
    reference_order = [
        (
            value["actor_span_index"],
            value["destination_span_index"],
            value["registry_reference_id"].encode("utf-8"),
        )
        for value in references
    ]
    if reference_order != sorted(reference_order):
        raise EvaluationError("gold_inventory_reference_order")
    if len({value["registry_reference_id"] for value in references}) != len(references):
        raise EvaluationError("gold_inventory_reference_order")
    expected_pairs = {(actor, destination) for actor in actor_indices for destination in destination_indices}
    actual_pairs = {
        (value["actor_span_index"], value["destination_span_index"])
        for value in references
    }
    if actual_pairs != expected_pairs or len(references) != len(expected_pairs):
        raise EvaluationError("gold_inventory_cartesian_closure")

    actor_set = set(actor_indices)
    destination_set = set(destination_indices)
    if any(
        value["actor_span_index"] not in actor_set
        or value["destination_span_index"] not in destination_set
        for value in references
    ):
        raise EvaluationError("gold_inventory_reference_endpoint")

    if expected_entry is not None:
        identities = (
            ("item_id", "item_id"),
            ("vmp_sha256", "vmp_sha256"),
            ("final_annotation_id", "final_annotation_id"),
        )
        if any(inventory[left] != expected_entry[right] for left, right in identities):
            raise EvaluationError("gold_inventory_entry_binding")

    artifact = _artifact(inventory, max_bytes=GOLD_INVENTORY_MAX_BYTES)
    if expected_entry is not None:
        if expected_entry.get("gold_inventory_size_bytes") != len(artifact.data):
            raise EvaluationError("gold_inventory_size_mismatch")
        if expected_entry.get("gold_inventory_sha256") != artifact.sha256:
            raise EvaluationError("gold_inventory_hash_mismatch")
        if expected_entry.get("gold_pair_count") != len(references):
            raise EvaluationError("gold_inventory_pair_count_mismatch")
        if expected_entry.get("gold_empty") is not (len(references) == 0):
            raise EvaluationError("gold_inventory_empty_mismatch")
    return artifact


def parse_gold_inventory(
    raw: bytes,
    *,
    vmp_text: str | None = None,
    expected_entry: Mapping[str, Any] | None = None,
) -> CanonicalArtifact:
    if len(raw) > GOLD_INVENTORY_MAX_BYTES:
        raise EvaluationError("gold_inventory_too_large")
    try:
        value = strict_json_loads(raw, prefix="gold_inventory")
    except CanonicalError as error:
        raise EvaluationError(error.code) from error
    if not isinstance(value, dict):
        raise EvaluationError("gold_inventory_schema")
    artifact = gold_inventory_artifact(value, vmp_text=vmp_text, expected_entry=expected_entry)
    if artifact.data != raw:
        raise EvaluationError("gold_inventory_noncanonical")
    return artifact


def _valid_dataset_hashes(value: object) -> bool:
    return exact_keys(value, _DATASET_HASH_FIELDS) and all(
        is_sha256(value[field]) for field in _DATASET_HASH_FIELDS  # type: ignore[index]
    )


def _valid_universe_entry(value: object, *, partition: str | None = None) -> bool:
    if not exact_keys(value, _UNIVERSE_ENTRY_FIELDS):
        return False
    assert isinstance(value, dict)
    if not _fullmatch(_ITEM_ID, value["item_id"]):
        return False
    if value["partition"] not in _PARTITIONS:
        return False
    if partition is not None and value["partition"] != partition:
        return False
    return (
        is_sha256(value["vmp_sha256"])
        and _fullmatch(_ANNOTATION_ID, value["final_annotation_id"])
        and is_nonboolean_int(
            value["gold_inventory_size_bytes"], minimum=1, maximum=GOLD_INVENTORY_MAX_BYTES
        )
        and is_sha256(value["gold_inventory_sha256"])
        and is_nonboolean_int(value["gold_pair_count"], minimum=0)
        and isinstance(value["gold_empty"], bool)
        and value["gold_empty"] is (value["gold_pair_count"] == 0)
    )


def _universe_schema_counts(value: object) -> tuple[bool, int, int, bool]:
    """Return schema-valid, decoded count, validated count, and too-many."""

    if not isinstance(value, dict) or "entries" not in value or not isinstance(value["entries"], list):
        return False, 0, 0, False
    entries = value["entries"]
    decoded = min(len(entries), MAX_UNIVERSE_ENTRIES + 1)
    partition = value.get("partition") if value.get("partition") in _PARTITIONS else None
    entries_valid = all(_valid_universe_entry(entry, partition=partition) for entry in entries)
    validated = len(entries) if entries_valid and len(entries) <= MAX_UNIVERSE_ENTRIES else 0
    top_valid = (
        exact_keys(value, _UNIVERSE_FIELDS)
        and value["schema_version"] == UNIVERSE_SCHEMA_VERSION
        and _fullmatch(_UNIVERSE_ID, value["universe_id"])
        and value["partition"] in _PARTITIONS
        and _valid_dataset_hashes(value["dataset_artifact_hashes"])
        and is_sha256(value["registry_reference_bundle_sha256"])
    )
    schema_valid = top_valid and entries_valid
    too_many = schema_valid and len(entries) > MAX_UNIVERSE_ENTRIES
    return schema_valid, decoded, validated, too_many


def _universe_receipt(
    *,
    receipt_id: str,
    universe_hash: str | None,
    prefix_hash: str | None,
    prefix_bytes: int,
    observed_bytes: int | str,
    decoded: int,
    validated: int,
    code: str | None,
) -> tuple[dict[str, Any], bytes, str]:
    if not _fullmatch(_UNIVERSE_RECEIPT_ID, receipt_id):
        raise EvaluationError("metric_universe_invalid_receipt_id")
    receipt = {
        "schema_version": METRIC_UNIVERSE_RECEIPT_VERSION,
        "receipt_id": receipt_id,
        "evaluation_universe_sha256": universe_hash,
        "submitted_prefix_sha256": prefix_hash,
        "prefix_bytes_hashed": prefix_bytes,
        "observed_bytes": observed_bytes,
        "decoded_entry_count": decoded,
        "validated_entry_count": validated,
        "invalid_codes": [] if code is None else [code],
        "status": "PASS" if code is None else "FAIL",
    }
    artifact = _artifact(receipt, max_bytes=RECEIPT_MAX_BYTES)
    return receipt, artifact.data, artifact.sha256


def parse_metric_universe_input(
    source: bytes | bytearray | memoryview | BinaryIO,
    *,
    receipt_id: str,
) -> MetricUniverseParseResult:
    """Consume cap+1 bytes and emit the exact one-code universe receipt."""

    bounded = read_cap_plus_one(source, UNIVERSE_MAX_BYTES)
    if bounded.exceeded:
        receipt, data, digest = _universe_receipt(
            receipt_id=receipt_id,
            universe_hash=None,
            prefix_hash=sha256(bounded.data).hexdigest(),
            prefix_bytes=UNIVERSE_READ_BYTES,
            observed_bytes=f"GE_{UNIVERSE_READ_BYTES}",
            decoded=0,
            validated=0,
            code="metric_universe_too_large",
        )
        return MetricUniverseParseResult(receipt, data, digest, None)

    raw = bounded.data
    try:
        value = strict_json_loads(raw, prefix="metric_universe")
    except CanonicalError as error:
        mapping = {
            "metric_universe_bom": "metric_universe_bom",
            "metric_universe_invalid_utf8": "metric_universe_invalid_utf8",
            "metric_universe_duplicate_key": "metric_universe_duplicate_key",
            "metric_universe_nonfinite": "metric_universe_nonfinite",
            "metric_universe_invalid_json": "metric_universe_invalid_json_syntax",
            "metric_universe_non_nfc": "metric_universe_non_nfc",
            "metric_universe_noncanonical_bytes": "metric_universe_noncanonical_bytes",
        }
        code = mapping.get(error.code)
        if code is None:
            raise
        receipt, data, digest = _universe_receipt(
            receipt_id=receipt_id,
            universe_hash=None,
            prefix_hash=None,
            prefix_bytes=0,
            observed_bytes=len(raw),
            decoded=0,
            validated=0,
            code=code,
        )
        return MetricUniverseParseResult(receipt, data, digest, None)

    canonical_hash = sha256(raw).hexdigest()
    schema_valid, decoded, validated, too_many = _universe_schema_counts(value)
    if not schema_valid:
        code = "metric_universe_schema_or_enum"
        universe = None
    elif too_many:
        code = "metric_universe_too_many_entries"
        decoded = MAX_UNIVERSE_ENTRIES + 1
        validated = 0
        universe = None
    else:
        code = None
        universe = value
    receipt, data, digest = _universe_receipt(
        receipt_id=receipt_id,
        universe_hash=canonical_hash,
        prefix_hash=None,
        prefix_bytes=0,
        observed_bytes=len(raw),
        decoded=decoded,
        validated=validated,
        code=code,
    )
    return MetricUniverseParseResult(receipt, data, digest, universe)


def registry_reference_bundle_artifact(bundle: dict[str, Any]) -> CanonicalArtifact:
    if not exact_keys(bundle, _REGISTRY_BUNDLE_FIELDS):
        raise EvaluationError("registry_reference_bundle_schema")
    if bundle["schema_version"] != "1.0.0":
        raise EvaluationError("registry_reference_bundle_schema")
    if not _fullmatch(_SNAPSHOT_ID, bundle["registry_snapshot_id"]):
        raise EvaluationError("registry_reference_bundle_schema")
    if not _fullmatch(_RESOLVER_VERSION, bundle["resolver_version"]):
        raise EvaluationError("registry_reference_bundle_schema")
    if not is_sha256(bundle["registry_manifest_sha256"]) or not is_sha256(
        bundle["registry_references_sha256"]
    ):
        raise EvaluationError("registry_reference_bundle_schema")
    return _artifact(bundle, max_bytes=RECEIPT_MAX_BYTES)


def validate_universe_semantics(
    universe: dict[str, Any],
    context: UniverseSemanticContext,
) -> bool:
    """Prove nonempty, complete, byte-identical closure and gold bindings."""

    schema_valid, _decoded, _validated, too_many = _universe_schema_counts(universe)
    if not schema_valid or too_many:
        return False
    entries = universe["entries"]
    if not 1 <= len(entries) <= MAX_UNIVERSE_ENTRIES:
        return False
    item_ids = [entry["item_id"] for entry in entries]
    if item_ids != sorted(item_ids, key=lambda value: value.encode("utf-8")):
        return False
    if len(item_ids) != len(set(item_ids)):
        return False
    if tuple(entries) != context.expected_entries:
        return False
    if universe["dataset_artifact_hashes"] != context.dataset_artifact_hashes:
        return False
    try:
        bundle = registry_reference_bundle_artifact(context.registry_reference_bundle)
    except EvaluationError:
        return False
    if universe["registry_reference_bundle_sha256"] != bundle.sha256:
        return False
    dataset_hashes = universe["dataset_artifact_hashes"]
    if (
        context.registry_reference_bundle["registry_manifest_sha256"]
        != dataset_hashes["registry_manifest_jsonl_sha256"]
    ):
        return False
    if (
        context.registry_reference_bundle["registry_references_sha256"]
        != dataset_hashes["registry_references_jsonl_sha256"]
    ):
        return False

    for entry in entries:
        raw = context.gold_inventory_bytes.get(entry["gold_inventory_sha256"])
        text = context.vmp_text_by_item_id.get(entry["item_id"])
        if raw is None or text is None:
            return False
        try:
            inventory = parse_gold_inventory(raw, vmp_text=text, expected_entry=entry).value
        except EvaluationError:
            return False
        for reference in inventory["registry_references"]:
            if reference["registry_snapshot_id"] != context.registry_reference_bundle["registry_snapshot_id"]:
                return False
            if reference["resolver_version"] != context.registry_reference_bundle["resolver_version"]:
                return False
    return True


def _input_receipt(
    *,
    receipt_id: str,
    universe_hash: str,
    prefix_hash: str | None,
    prefix_bytes: int,
    observed_bytes: int | str,
    decoded: int | str,
    validated: int | str,
    stage: str,
    codes: Sequence[str],
) -> MetricInputParseResult:
    if not _fullmatch(_METRIC_INPUT_RECEIPT_ID, receipt_id):
        raise EvaluationError("metric_input_invalid_receipt_id")
    receipt = {
        "schema_version": METRIC_INPUT_VERSION,
        "receipt_id": receipt_id,
        "evaluation_universe_sha256": universe_hash,
        "submitted_prefix_sha256": prefix_hash,
        "prefix_bytes_hashed": prefix_bytes,
        "observed_bytes": observed_bytes,
        "decoded_row_count": decoded,
        "validated_row_count": validated,
        "failure_stage": stage,
        "invalid_codes": sorted(set(codes)),
        "status": "FAILED",
    }
    artifact = _artifact(receipt, max_bytes=RECEIPT_MAX_BYTES)
    return MetricInputParseResult(receipt, artifact.data, artifact.sha256, None, None, None)


def _submission_counts(value: object) -> tuple[int | str, int | str]:
    if not isinstance(value, dict) or not isinstance(value.get("entries"), list):
        return 0, 0
    entries = value["entries"]
    if len(entries) > MAX_SUBMISSION_ROWS:
        validated: int | str = (
            "GE_20001"
            if all(_valid_submission_entry(row) for row in entries[: MAX_SUBMISSION_ROWS + 1])
            else 0
        )
        return "GE_20001", validated
    decoded = sum(isinstance(row, dict) for row in entries)
    validated = sum(_valid_submission_entry(row) for row in entries)
    return decoded, validated


def _valid_submission_entry(value: object) -> bool:
    return (
        exact_keys(value, _SUBMISSION_ENTRY_FIELDS)
        and _fullmatch(_ITEM_ID, value["item_id"])  # type: ignore[index]
        and is_sha256(value["envelope_sha256"])  # type: ignore[index]
    )


def parse_metric_input(
    source: bytes | bytearray | memoryview | BinaryIO,
    *,
    receipt_id: str,
    evaluation_universe_sha256: str,
) -> MetricInputParseResult:
    """Preflight a raw inference submission against a passed universe hash."""

    if not is_sha256(evaluation_universe_sha256):
        raise EvaluationError("metric_input_expected_universe_hash")
    bounded = read_cap_plus_one(source, UNIVERSE_MAX_BYTES)
    if bounded.exceeded:
        return _input_receipt(
            receipt_id=receipt_id,
            universe_hash=evaluation_universe_sha256,
            prefix_hash=sha256(bounded.data).hexdigest(),
            prefix_bytes=UNIVERSE_READ_BYTES,
            observed_bytes=f"GE_{UNIVERSE_READ_BYTES}",
            decoded=0,
            validated=0,
            stage="BYTES",
            codes=["metric_input_oversized"],
        )
    raw = bounded.data
    try:
        value = strict_json_loads(raw, prefix="metric_input")
    except CanonicalError as error:
        if error.code in {"metric_input_bom", "metric_input_invalid_utf8"}:
            stage = "UTF8"
            code = "metric_input_invalid_utf8"
        elif error.code in {"metric_input_non_nfc", "metric_input_noncanonical_bytes"}:
            stage = "CANONICAL"
            code = "metric_input_noncanonical"
        else:
            stage = "JSON"
            code = "metric_input_invalid_json"
        return _input_receipt(
            receipt_id=receipt_id,
            universe_hash=evaluation_universe_sha256,
            prefix_hash=sha256(raw).hexdigest(),
            prefix_bytes=len(raw),
            observed_bytes=len(raw),
            decoded=0,
            validated=0,
            stage=stage,
            codes=[code],
        )

    decoded, validated = _submission_counts(value)
    if not exact_keys(value, _SUBMISSION_FIELDS):
        return _input_receipt(
            receipt_id=receipt_id,
            universe_hash=evaluation_universe_sha256,
            prefix_hash=sha256(raw).hexdigest(),
            prefix_bytes=len(raw),
            observed_bytes=len(raw),
            decoded=decoded,
            validated=validated,
            stage="JSON",
            codes=["metric_input_invalid_shape"],
        )
    assert isinstance(value, dict)
    entries = value["entries"]
    shape_valid = (
        value["schema_version"] == METRIC_INPUT_VERSION
        and is_sha256(value["evaluation_universe_sha256"])
        and is_sha256(value["system_artifact_manifest_sha256"])
        and isinstance(entries, list)
        and all(_valid_submission_entry(row) for row in entries)
    )
    if not shape_valid:
        return _input_receipt(
            receipt_id=receipt_id,
            universe_hash=evaluation_universe_sha256,
            prefix_hash=sha256(raw).hexdigest(),
            prefix_bytes=len(raw),
            observed_bytes=len(raw),
            decoded=decoded,
            validated=validated,
            stage="JSON",
            codes=["metric_input_invalid_shape"],
        )
    if len(entries) > MAX_SUBMISSION_ROWS:
        return _input_receipt(
            receipt_id=receipt_id,
            universe_hash=evaluation_universe_sha256,
            prefix_hash=sha256(raw).hexdigest(),
            prefix_bytes=len(raw),
            observed_bytes=len(raw),
            decoded="GE_20001",
            validated="GE_20001",
            stage="ROW_BOUND",
            codes=["metric_input_too_many_rows"],
        )
    if value["evaluation_universe_sha256"] != evaluation_universe_sha256:
        return _input_receipt(
            receipt_id=receipt_id,
            universe_hash=evaluation_universe_sha256,
            prefix_hash=sha256(raw).hexdigest(),
            prefix_bytes=len(raw),
            observed_bytes=len(raw),
            decoded=len(entries),
            validated=len(entries),
            stage="BINDING",
            codes=["metric_input_universe_hash_mismatch"],
        )
    artifact = CanonicalArtifact(value, raw, sha256(raw).hexdigest())
    return MetricInputParseResult(None, None, None, value, raw, artifact.sha256)


def classify_submission_rows(
    expected_item_ids: Sequence[str],
    submitted_rows: Sequence[Mapping[str, str]],
) -> dict[str, Any]:
    """Classify rows once, then compute missing and positional mismatches."""

    expected_set = set(expected_item_ids)
    seen: set[str] = set()
    unique_expected: list[Mapping[str, str]] = []
    duplicate = 0
    extra = 0
    for row in submitted_rows:
        item_id = row["item_id"]
        if item_id in seen:
            duplicate += 1
            continue
        seen.add(item_id)
        if item_id not in expected_set:
            extra += 1
        else:
            unique_expected.append(row)
    present = {row["item_id"] for row in unique_expected}
    restricted_expected = [item_id for item_id in expected_item_ids if item_id in present]
    submitted_expected = [row["item_id"] for row in unique_expected]
    reordered = sum(left != right for left, right in zip(restricted_expected, submitted_expected))
    def capped(value: int) -> int | str:
        return value if value <= MAX_SUBMISSION_ROWS else "GE_20001"

    return {
        "submitted_count": capped(len(submitted_rows)),
        "missing_count": capped(len(expected_item_ids) - len(present)),
        "extra_count": capped(extra),
        "duplicate_count": capped(duplicate),
        "reordered_count": capped(reordered),
        "unique_expected_rows": unique_expected,
    }


def _metric_run_artifact(manifest: dict[str, Any]) -> CanonicalArtifact:
    if not exact_keys(manifest, _METRIC_RUN_FIELDS):
        raise EvaluationError("metric_run_schema")
    return _artifact(manifest, max_bytes=UNIVERSE_MAX_BYTES)


def _invalid_codes(counts: Mapping[str, int | str], *, universe_error: int, denominator_error: int) -> list[str]:
    codes: list[str] = []
    if universe_error:
        codes.append("metric_invalid_universe")
    mapping = (
        ("missing_count", "metric_missing"),
        ("extra_count", "metric_extra"),
        ("duplicate_count", "metric_duplicate"),
        ("reordered_count", "metric_reordered"),
        ("degraded_count", "metric_degraded"),
        ("invalid_count", "metric_invalid_envelope"),
        ("mismatch_count", "metric_binding_mismatch"),
    )
    for field, code in mapping:
        if counts[field] != 0:
            codes.append(code)
    if denominator_error:
        codes.append("metric_invalid_denominator")
    return sorted(codes)


def _gold_pairs(inventory: Mapping[str, Any]) -> frozenset[PairKey]:
    actors = {value["span_index"]: value for value in inventory["actors"]}
    destinations = {value["span_index"]: value for value in inventory["destinations"]}
    return frozenset(
        (
            actors[value["actor_span_index"]]["start"],
            actors[value["actor_span_index"]]["end"],
            destinations[value["destination_span_index"]]["start"],
            destinations[value["destination_span_index"]]["end"],
            value["label"],
        )
        for value in inventory["registry_references"]
    )


def _safe_ratio(numerator: float, denominator: float) -> float:
    if denominator == 0.0:
        return 0.0
    result = numerator / denominator
    if not math.isfinite(result):
        raise EvaluationError("metric_nonfinite")
    return 0.0 if result == 0.0 else result


def _one_pair_metric_view(
    gold: Mapping[str, frozenset[PairKey]],
    predictions: Mapping[str, Sequence[PathPairPrediction]],
    *,
    rank_one: bool,
) -> dict[str, float | None]:
    tp = 0.0
    fp = 0.0
    fn = 0.0
    emptiness_correct = 0.0
    empty_correct = 0.0
    nonempty_correct = 0.0
    empty_count = sum(not values for values in gold.values())
    nonempty_count = len(gold) - empty_count
    for item_id, gold_pairs in gold.items():
        paths = predictions[item_id]
        selected = paths[:1] if rank_one else paths
        for path in selected:
            weight = 1.0 if rank_one else path.q
            predicted = path.pairs
            tp += weight * len(predicted & gold_pairs)
            fp += weight * len(predicted - gold_pairs)
            fn += weight * len(gold_pairs - predicted)
            same_empty = (not predicted) == (not gold_pairs)
            emptiness_correct += weight * int(same_empty)
            if not gold_pairs:
                empty_correct += weight * int(not predicted)
            else:
                nonempty_correct += weight * int(bool(predicted))
    precision = _safe_ratio(tp, tp + fp)
    recall = _safe_ratio(tp, tp + fn)
    f1 = _safe_ratio(2.0 * tp, 2.0 * tp + fp + fn)
    return {
        "TP": 0.0 if tp == 0.0 else tp,
        "FP": 0.0 if fp == 0.0 else fp,
        "FN": 0.0 if fn == 0.0 else fn,
        "precision_pair": precision,
        "recall_pair": recall,
        "F1_pair": f1,
        "pair_emptiness_accuracy": _safe_ratio(emptiness_correct, float(len(gold))),
        "gold_empty_recall": None if empty_count == 0 else _safe_ratio(empty_correct, float(empty_count)),
        "gold_nonempty_recall": None
        if nonempty_count == 0
        else _safe_ratio(nonempty_correct, float(nonempty_count)),
    }


def _validate_path_predictions(
    condition: str, paths: Sequence[PathPairPrediction]
) -> None:
    if not 1 <= len(paths) <= 8:
        raise EvaluationError("metric_missing_path")
    if condition == "C01" and len(paths) != 1:
        raise EvaluationError("metric_rank_one_path_count")
    seen: set[str] = set()
    for path in paths:
        if (
            not isinstance(path, PathPairPrediction)
            or not isinstance(path.path_id, str)
            or not path.path_id
            or path.path_id in seen
            or isinstance(path.q, bool)
            or not isinstance(path.q, (int, float))
            or not math.isfinite(path.q)
            or path.q < 0.0
            or not isinstance(path.pairs, frozenset)
        ):
            raise EvaluationError("metric_invalid_path_weight")
        seen.add(path.path_id)
        for pair in path.pairs:
            if (
                not isinstance(pair, tuple)
                or len(pair) != 5
                or any(not is_nonboolean_int(value, minimum=0) for value in pair[:4])
                or pair[0] >= pair[1]
                or pair[2] >= pair[3]
                or pair[4] not in _REFERENCE_LABELS
            ):
                raise EvaluationError("metric_invalid_pair")
    if condition == "C11" and not math.isclose(
        sequential_sum(path.q for path in paths),
        1.0,
        rel_tol=1e-12,
        abs_tol=1e-15,
    ):
        raise EvaluationError("metric_invalid_path_weight")


def compute_pair_metrics(
    condition: str,
    gold: Mapping[str, frozenset[PairKey]],
    predictions: Mapping[str, Sequence[PathPairPrediction]],
) -> dict[str, Any]:
    """Compute complete-universe rank-one and optional q-weighted metrics."""

    if condition not in _CONDITIONS:
        raise EvaluationError("metric_condition_not_applicable")
    if not gold or set(gold) != set(predictions):
        raise EvaluationError("metric_incomplete_universe")
    for paths in predictions.values():
        _validate_path_predictions(condition, paths)
    result: dict[str, Any] = {
        "N_all": len(gold),
        "N_gold_empty": sum(not pairs for pairs in gold.values()),
        "N_gold_nonempty": sum(bool(pairs) for pairs in gold.values()),
        "rank1": _one_pair_metric_view(gold, predictions, rank_one=True),
    }
    result["q_weighted"] = (
        _one_pair_metric_view(gold, predictions, rank_one=False) if condition == "C11" else None
    )
    return result


def supplied_temperature_summary(
    mean_logits: Sequence[float],
    weights: Sequence[float],
    *,
    temperature: float,
    rank_one: bool = False,
) -> dict[str, Any]:
    """Apply the supplied-temperature Fisher p/v/u formulas.

    This function does not fit a temperature; optimizer behavior remains outside
    E0.  Rank-one forces the specified disagreement value to exact ``+0.0``.
    """

    if not math.isfinite(temperature) or temperature <= 0.0:
        raise EvaluationError("temperature_invalid")
    if not mean_logits or len(mean_logits) != len(weights):
        raise EvaluationError("temperature_shape")
    if any(not math.isfinite(value) for value in mean_logits):
        raise EvaluationError("temperature_nonfinite_logit")
    if any(not math.isfinite(value) or value < 0.0 for value in weights):
        raise EvaluationError("temperature_invalid_weight")
    if rank_one:
        if len(mean_logits) != 1:
            raise EvaluationError("temperature_rank_one_shape")
        effective_weights = [1.0]
    else:
        if not math.isclose(sum(weights), 1.0, rel_tol=1e-12, abs_tol=1e-15):
            raise EvaluationError("temperature_invalid_weight")
        effective_weights = list(weights)

    probabilities: list[float] = []
    for logit in mean_logits:
        scaled = logit / temperature
        if scaled >= 0.0:
            probability = 1.0 / (1.0 + math.exp(-scaled))
        else:
            exp_value = math.exp(scaled)
            probability = exp_value / (1.0 + exp_value)
        probabilities.append(probability)
    p = sequential_sum(
        weight * probability for weight, probability in zip(effective_weights, probabilities)
    )
    v = 0.0 if rank_one else 4.0 * sequential_sum(
        weight * (probability - p) ** 2
        for weight, probability in zip(effective_weights, probabilities)
    )
    if p in {0.0, 1.0}:
        entropy = 0.0
    else:
        entropy = -p * math.log(p) - (1.0 - p) * math.log(1.0 - p)
    u = 0.5 * entropy / math.log(2.0) + 0.5 * v
    if not all(math.isfinite(value) for value in (p, v, u)):
        raise EvaluationError("temperature_nonfinite_result")
    return {
        "path_probabilities": tuple(probabilities),
        "p": 0.0 if p == 0.0 else p,
        "v": 0.0 if v == 0.0 else v,
        "u": 0.0 if u == 0.0 else u,
    }


def five_seed_mean_logits(seed_logits: Sequence[Sequence[float]]) -> tuple[float, ...]:
    """Average five finite seed rows in fixed row order using binary64 adds."""

    if len(seed_logits) != 5 or not seed_logits:
        raise EvaluationError("five_seed_shape")
    width = len(seed_logits[0])
    if width == 0 or any(len(row) != width for row in seed_logits):
        raise EvaluationError("five_seed_shape")
    if any(not math.isfinite(value) for row in seed_logits for value in row):
        raise EvaluationError("five_seed_nonfinite")
    means: list[float] = []
    for column in range(width):
        try:
            mean = sequential_mean(row[column] for row in seed_logits)
        except CanonicalError as error:
            raise EvaluationError("five_seed_nonfinite") from error
        if not math.isfinite(mean):
            raise EvaluationError("five_seed_nonfinite")
        means.append(0.0 if mean == 0.0 else mean)
    return tuple(means)


def _make_metric_manifest(
    *,
    metric_run_id: str,
    condition: str,
    system_id: str,
    system_variant: str,
    system_manifest_hash: str,
    universe_hash: str,
    bundle_hash: str,
    submission_hash: str,
    inference_envelopes: list[dict[str, str]],
    n_all: int,
    n_empty: int,
    n_nonempty: int,
    universe_error: int,
    denominator_error: int,
    counts: Mapping[str, int | str],
    status: str,
) -> MetricRunResult:
    if not _fullmatch(_METRIC_RUN_ID, metric_run_id):
        raise EvaluationError("metric_run_id")
    if condition not in _CONDITIONS or not _fullmatch(_SYSTEM_ID, system_id) or system_variant not in _VARIANTS:
        raise EvaluationError("metric_run_identity")
    invalid_codes = _invalid_codes(
        counts, universe_error=universe_error, denominator_error=denominator_error
    )
    manifest = {
        "schema_version": METRIC_RUN_VERSION,
        "metric_run_id": metric_run_id,
        "condition": condition,
        "system_id": system_id,
        "system_variant": system_variant,
        "system_artifact_manifest_sha256": system_manifest_hash,
        "evaluation_universe_sha256": universe_hash,
        "registry_reference_bundle_sha256": bundle_hash,
        "submitted_inference_manifest_sha256": submission_hash,
        "inference_envelopes": inference_envelopes,
        "N_all": n_all,
        "N_gold_empty": n_empty,
        "N_gold_nonempty": n_nonempty,
        "universe_error_count": universe_error,
        "denominator_error_count": denominator_error,
        "submitted_count": counts["submitted_count"],
        "missing_count": counts["missing_count"],
        "extra_count": counts["extra_count"],
        "duplicate_count": counts["duplicate_count"],
        "reordered_count": counts["reordered_count"],
        "degraded_count": counts["degraded_count"],
        "invalid_count": counts["invalid_count"],
        "mismatch_count": counts["mismatch_count"],
        "status": status,
        "invalid_codes": invalid_codes,
    }
    artifact = _metric_run_artifact(manifest)
    return MetricRunResult(manifest, artifact.data, artifact.sha256, None)


def _evaluate_metric_run_with_inspector(
    *,
    metric_run_id: str,
    condition: str,
    system_id: str,
    system_variant: str,
    universe_result: MetricUniverseParseResult,
    input_result: MetricInputParseResult,
    semantic_context: UniverseSemanticContext,
    envelope_bytes: Mapping[str, bytes],
    envelope_inspector: _EnvelopeInspector,
    declared_n_all: int,
    declared_n_gold_empty: int,
    declared_n_gold_nonempty: int,
) -> MetricRunResult:
    """Produce the valid/invalid metric-run union after both receipts pass."""

    universe = universe_result.universe
    submission = input_result.manifest
    if universe is None or universe_result.receipt["status"] != "PASS":
        raise EvaluationError("metric_universe_receipt_not_passed")
    if submission is None or input_result.receipt is not None or input_result.manifest_sha256 is None:
        raise EvaluationError("metric_input_receipt_not_passed")
    universe_hash = universe_result.receipt["evaluation_universe_sha256"]
    assert isinstance(universe_hash, str)
    bundle_hash = universe["registry_reference_bundle_sha256"]
    system_manifest_hash = submission["system_artifact_manifest_sha256"]

    base_counts: dict[str, int | str] = {
        "submitted_count": len(submission["entries"]),
        "missing_count": 0,
        "extra_count": 0,
        "duplicate_count": 0,
        "reordered_count": 0,
        "degraded_count": 0,
        "invalid_count": 0,
        "mismatch_count": 0,
    }
    if not validate_universe_semantics(universe, semantic_context):
        return _make_metric_manifest(
            metric_run_id=metric_run_id,
            condition=condition,
            system_id=system_id,
            system_variant=system_variant,
            system_manifest_hash=system_manifest_hash,
            universe_hash=universe_hash,
            bundle_hash=bundle_hash,
            submission_hash=input_result.manifest_sha256,
            inference_envelopes=[],
            n_all=0,
            n_empty=0,
            n_nonempty=0,
            universe_error=1,
            denominator_error=0,
            counts=base_counts,
            status="INVALID",
        )

    entries = universe["entries"]
    expected_ids = [entry["item_id"] for entry in entries]
    classification = classify_submission_rows(expected_ids, submission["entries"])
    for field in ("submitted_count", "missing_count", "extra_count", "duplicate_count", "reordered_count"):
        base_counts[field] = classification[field]
    derived_n_all = len(entries)
    derived_n_empty = sum(entry["gold_empty"] for entry in entries)
    derived_n_nonempty = derived_n_all - derived_n_empty
    denominator_error = sum(
        not is_nonboolean_int(declared, minimum=0, maximum=MAX_UNIVERSE_ENTRIES)
        or declared != derived
        for declared, derived in (
            (declared_n_all, derived_n_all),
            (declared_n_gold_empty, derived_n_empty),
            (declared_n_gold_nonempty, derived_n_nonempty),
        )
    )

    expected_by_id = {entry["item_id"]: entry for entry in entries}
    bundle = semantic_context.registry_reference_bundle
    predictions: dict[str, Sequence[PathPairPrediction]] = {}
    for row in classification["unique_expected_rows"]:
        raw = envelope_bytes.get(row["envelope_sha256"])
        if raw is None:
            base_counts["invalid_count"] = int(base_counts["invalid_count"]) + 1
            continue
        if sha256(raw).hexdigest() != row["envelope_sha256"]:
            base_counts["mismatch_count"] = int(base_counts["mismatch_count"]) + 1
            continue
        try:
            evidence = envelope_inspector(raw)
        except EvaluationBindingError:
            base_counts["mismatch_count"] = int(base_counts["mismatch_count"]) + 1
            continue
        except (CanonicalError, EvaluationError, ValueError, TypeError, KeyError):
            base_counts["invalid_count"] = int(base_counts["invalid_count"]) + 1
            continue
        if evidence.execution_status == "INVALID":
            base_counts["invalid_count"] = int(base_counts["invalid_count"]) + 1
            continue
        if evidence.execution_status == "DEGRADED_STOP_AFTER_IDENTITY":
            base_counts["degraded_count"] = int(base_counts["degraded_count"]) + 1
            continue
        entry = expected_by_id[row["item_id"]]
        binding_valid = (
            evidence.execution_status == "VALID"
            and evidence.item_id == row["item_id"]
            and evidence.vmp_sha256 == entry["vmp_sha256"]
            and evidence.condition == condition
            and evidence.system_id == system_id
            and evidence.system_variant == system_variant
            and evidence.system_artifact_manifest_sha256 == system_manifest_hash
            and evidence.registry_snapshot_id == bundle["registry_snapshot_id"]
            and evidence.registry_artifact_sha256 == bundle["registry_manifest_sha256"]
            and evidence.resolver_version == bundle["resolver_version"]
        )
        if not binding_valid:
            base_counts["mismatch_count"] = int(base_counts["mismatch_count"]) + 1
            continue
        if not evidence.paths or (condition == "C01" and len(evidence.paths) != 1):
            base_counts["mismatch_count"] = int(base_counts["mismatch_count"]) + 1
            continue
        try:
            _validate_path_predictions(condition, evidence.paths)
        except EvaluationError:
            base_counts["invalid_count"] = int(base_counts["invalid_count"]) + 1
            continue
        predictions[row["item_id"]] = evidence.paths

    has_error = denominator_error or any(
        base_counts[field] != 0
        for field in (
            "missing_count",
            "extra_count",
            "duplicate_count",
            "reordered_count",
            "degraded_count",
            "invalid_count",
            "mismatch_count",
        )
    )
    if has_error:
        return _make_metric_manifest(
            metric_run_id=metric_run_id,
            condition=condition,
            system_id=system_id,
            system_variant=system_variant,
            system_manifest_hash=system_manifest_hash,
            universe_hash=universe_hash,
            bundle_hash=bundle_hash,
            submission_hash=input_result.manifest_sha256,
            inference_envelopes=[],
            n_all=derived_n_all,
            n_empty=derived_n_empty,
            n_nonempty=derived_n_nonempty,
            universe_error=0,
            denominator_error=denominator_error,
            counts=base_counts,
            status="INVALID",
        )

    gold: dict[str, frozenset[PairKey]] = {}
    for entry in entries:
        raw = semantic_context.gold_inventory_bytes[entry["gold_inventory_sha256"]]
        inventory = parse_gold_inventory(
            raw,
            vmp_text=semantic_context.vmp_text_by_item_id[entry["item_id"]],
            expected_entry=entry,
        ).value
        gold[entry["item_id"]] = _gold_pairs(inventory)
    pair_metrics = compute_pair_metrics(condition, gold, predictions)
    run = _make_metric_manifest(
        metric_run_id=metric_run_id,
        condition=condition,
        system_id=system_id,
        system_variant=system_variant,
        system_manifest_hash=system_manifest_hash,
        universe_hash=universe_hash,
        bundle_hash=bundle_hash,
        submission_hash=input_result.manifest_sha256,
        inference_envelopes=[dict(row) for row in submission["entries"]],
        n_all=derived_n_all,
        n_empty=derived_n_empty,
        n_nonempty=derived_n_nonempty,
        universe_error=0,
        denominator_error=0,
        counts=base_counts,
        status="VALID",
    )
    return MetricRunResult(run.manifest, run.manifest_bytes, run.manifest_sha256, pair_metrics)


def evaluate_metric_run(
    *,
    metric_run_id: str,
    condition: str,
    system_id: str,
    system_variant: str,
    universe_result: MetricUniverseParseResult,
    input_result: MetricInputParseResult,
    semantic_context: UniverseSemanticContext,
    metric_artifacts: MetricArtifactBytes,
    declared_n_all: int,
    declared_n_gold_empty: int,
    declared_n_gold_nonempty: int,
) -> MetricRunResult:
    """Evaluate a run using only the mandatory authoritative artifact store."""

    if not isinstance(metric_artifacts, MetricArtifactBytes):
        raise EvaluationError("metric_invalid_artifact_store")
    envelope_bytes = {
        digest: bundle.engine_envelope_bytes
        for digest, bundle in metric_artifacts.envelopes.items()
        if isinstance(digest, str)
        and isinstance(bundle, MetricEnvelopeArtifactBytes)
        and isinstance(bundle.engine_envelope_bytes, bytes)
    }
    return _evaluate_metric_run_with_inspector(
        metric_run_id=metric_run_id,
        condition=condition,
        system_id=system_id,
        system_variant=system_variant,
        universe_result=universe_result,
        input_result=input_result,
        semantic_context=semantic_context,
        envelope_bytes=envelope_bytes,
        envelope_inspector=_make_engine_envelope_inspector(metric_artifacts),
        declared_n_all=declared_n_all,
        declared_n_gold_empty=declared_n_gold_empty,
        declared_n_gold_nonempty=declared_n_gold_nonempty,
    )


def evaluate_boundary(
    universe_source: bytes | bytearray | memoryview | BinaryIO,
    submission_source: bytes | bytearray | memoryview | BinaryIO,
    *,
    universe_receipt_id: str,
    input_receipt_id: str,
    metric_run_id: str,
    condition: str,
    system_id: str,
    system_variant: str,
    semantic_context: UniverseSemanticContext,
    metric_artifacts: MetricArtifactBytes,
    declared_n_all: int,
    declared_n_gold_empty: int,
    declared_n_gold_nonempty: int,
) -> EvaluationBoundaryResult:
    """Apply structural-universe -> submission -> authoritative replay order."""

    universe_result = parse_metric_universe_input(
        universe_source, receipt_id=universe_receipt_id
    )
    if universe_result.universe is None:
        return EvaluationBoundaryResult(universe_result, None, None)
    universe_hash = universe_result.receipt["evaluation_universe_sha256"]
    assert isinstance(universe_hash, str)
    input_result = parse_metric_input(
        submission_source,
        receipt_id=input_receipt_id,
        evaluation_universe_sha256=universe_hash,
    )
    if input_result.manifest is None:
        return EvaluationBoundaryResult(universe_result, input_result, None)
    metric_run = evaluate_metric_run(
        metric_run_id=metric_run_id,
        condition=condition,
        system_id=system_id,
        system_variant=system_variant,
        universe_result=universe_result,
        input_result=input_result,
        semantic_context=semantic_context,
        metric_artifacts=metric_artifacts,
        declared_n_all=declared_n_all,
        declared_n_gold_empty=declared_n_gold_empty,
        declared_n_gold_nonempty=declared_n_gold_nonempty,
    )
    return EvaluationBoundaryResult(universe_result, input_result, metric_run)


__all__ = [
    "CanonicalArtifact",
    "EvaluationBoundaryResult",
    "EvaluationBindingError",
    "EvaluationError",
    "GOLD_INVENTORY_MAX_BYTES",
    "MAX_SUBMISSION_ROWS",
    "MAX_UNIVERSE_ENTRIES",
    "MetricInputParseResult",
    "MetricArtifactBytes",
    "MetricEnvelopeArtifactBytes",
    "MetricRunResult",
    "MetricUniverseParseResult",
    "PathPairPrediction",
    "UniverseSemanticContext",
    "UNIVERSE_MAX_BYTES",
    "classify_submission_rows",
    "compute_pair_metrics",
    "evaluate_boundary",
    "evaluate_metric_run",
    "five_seed_mean_logits",
    "gold_inventory_artifact",
    "parse_gold_inventory",
    "parse_metric_input",
    "parse_metric_universe_input",
    "registry_reference_bundle_artifact",
    "supplied_temperature_summary",
    "validate_universe_semantics",
]
