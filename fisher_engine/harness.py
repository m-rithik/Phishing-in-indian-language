"""End-to-end, deterministic, synthetic-only Fisher E0 rehearsal."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping, TYPE_CHECKING

from ._canonical import CanonicalError, canonical_json_bytes, exact_keys, strict_json_loads
from .source_closure import SourceClosureRecorder

if TYPE_CHECKING:
    from .candidate import CandidateRun
    from .evaluation import EvaluationBoundaryResult


FIXTURE_MAX_BYTES = 4 * 1024 * 1024
FIXTURE_FIELDS = (
    "fixture_version",
    "scope",
    "fixture_id",
    "item_id",
    "text",
    "visible_artifacts",
    "selector_output",
    "provider_units",
    "endpoint_candidates",
    "registry_resolution",
    "seed_logits_f64_bits",
)
SYSTEM_COMBINATIONS = (
    ("C00", "BASE"),
    ("C10", "BASE"),
    ("C01", "BASE"),
    ("C11", "BASE"),
    ("C00", "CAPACITY_CONTROL"),
    ("C10", "CAPACITY_CONTROL"),
    ("C01", "SUPERVISION_CONTROL"),
    ("C11", "SUPERVISION_CONTROL"),
)


class HarnessError(ValueError):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


@dataclass(frozen=True)
class SyntheticE0Result:
    report: dict[str, Any]
    system_manifests: Mapping[str, dict[str, Any]]
    preflight_receipts: Mapping[str, dict[str, Any]]
    candidate_runs: Mapping[str, CandidateRun]
    semantic_artifacts: Mapping[str, dict[str, Any]]
    five_seed_artifacts: Mapping[str, dict[str, Any]]
    envelopes: Mapping[str, dict[str, Any]]
    evaluation_results: Mapping[str, EvaluationBoundaryResult]
    validation_contexts: Mapping[str, Any]
    descriptor_bytes: Mapping[str, bytes]
    registry_artifact_bytes: bytes

    @property
    def valid(self) -> bool:
        return self.report["status"] == "PASS"


def _system_key(condition: str, variant: str) -> str:
    return f"{condition}_{variant}"


def _system_id(condition: str, variant: str) -> str:
    return f"system_e0_{condition.lower()}_{variant.lower()}"


def _validate_fixture(value: object) -> dict[str, Any]:
    from ._numeric import f64_bits_to_float

    if not exact_keys(value, FIXTURE_FIELDS):
        raise HarnessError("engine_fixture_schema")
    assert isinstance(value, dict)
    if value["fixture_version"] != "1.0.0" or value["scope"] != "SYNTHETIC_E0_ONLY":
        raise HarnessError("engine_fixture_scope")
    if not isinstance(value["fixture_id"], str) or not value["fixture_id"].startswith("synthetic_"):
        raise HarnessError("engine_fixture_schema")
    if not isinstance(value["item_id"], str) or not value["item_id"].startswith("item_") or not isinstance(value["text"], str):
        raise HarnessError("engine_fixture_schema")
    for field in ("visible_artifacts", "selector_output", "provider_units", "endpoint_candidates"):
        if not isinstance(value[field], list):
            raise HarnessError("engine_fixture_schema")
    endpoints = value["endpoint_candidates"]
    endpoint_fields = ("role", "start", "end", "kind", "score_f64_bits")
    if (
        len(endpoints) != 2
        or not all(exact_keys(endpoint, endpoint_fields) for endpoint in endpoints)
        or endpoints[0]["role"] != "ACTOR"
        or endpoints[0]["kind"] != "NONE"
        or endpoints[1]["role"] != "DESTINATION"
    ):
        raise HarnessError("engine_fixture_schema")
    if not exact_keys(value["registry_resolution"], ("state", "registry_coverage", "evidence_ids")):
        raise HarnessError("engine_fixture_schema")
    resolution = value["registry_resolution"]
    if (
        resolution["state"] not in {"MATCH", "MISMATCH"}
        or resolution["registry_coverage"] != "COMPLETE"
        or not isinstance(resolution["evidence_ids"], list)
        or not resolution["evidence_ids"]
    ):
        raise HarnessError("engine_fixture_schema")
    logits = value["seed_logits_f64_bits"]
    if (
        not isinstance(logits, list)
        or len(logits) != 5
        or any(not isinstance(row, list) or len(row) < 2 for row in logits)
        or len({len(row) for row in logits}) != 1
    ):
        raise HarnessError("engine_fixture_schema")
    try:
        for endpoint in endpoints:
            f64_bits_to_float(endpoint["score_f64_bits"])
        for row in logits:
            for bits in row:
                f64_bits_to_float(bits)
    except CanonicalError as error:
        raise HarnessError("engine_fixture_numeric") from error
    return value


def load_synthetic_fixture(raw: bytes) -> dict[str, Any]:
    if len(raw) > FIXTURE_MAX_BYTES:
        raise HarnessError("engine_fixture_too_large")
    # Repository text fixtures use one POSIX record terminator.  It is not part
    # of the canonical artifact or its hash.
    if raw.endswith(b"\n") and not raw.endswith(b"\r\n"):
        raw = raw[:-1]
    try:
        value = strict_json_loads(raw, prefix="engine_fixture")
    except CanonicalError as error:
        raise HarnessError(error.code) from error
    return _validate_fixture(value)


def _build_systems(
    closure: dict[str, Any],
    *,
    fixture_hash: str,
    registry_artifact_hash: str,
) -> dict[str, dict[str, Any]]:
    from .artifacts import (
        build_system_artifact_manifest,
        system_artifact_manifest_sha256,
    )

    manifests: dict[str, dict[str, Any]] = {}
    for condition in ("C00", "C10", "C01", "C11"):
        key = _system_key(condition, "BASE")
        manifests[key] = build_system_artifact_manifest(
            system_id=_system_id(condition, "BASE"),
            condition=condition,
            system_variant="BASE",
            executed_source_closure=closure,
            synthetic_fixture_manifest_sha256=fixture_hash,
            registry_artifact_sha256=registry_artifact_hash,
        )
    for condition, variant in SYSTEM_COMBINATIONS[4:]:
        matched_condition = "C01" if condition == "C00" else "C11" if condition == "C10" else condition
        matched = manifests[_system_key(matched_condition, "BASE")]
        key = _system_key(condition, variant)
        manifests[key] = build_system_artifact_manifest(
            system_id=_system_id(condition, variant),
            condition=condition,
            system_variant=variant,
            executed_source_closure=closure,
            matched_system_id=matched["system_id"],
            matched_system_artifact_manifest_sha256=system_artifact_manifest_sha256(matched),
            synthetic_fixture_manifest_sha256=fixture_hash,
            registry_artifact_sha256=registry_artifact_hash,
        )
    return manifests


def _candidate_for_system(fixture: Mapping[str, Any], vmp_hash: str, manifest: Mapping[str, Any]) -> CandidateRun:
    from .candidate import run_candidate_provider

    binding = manifest["provider_binding"]
    return run_candidate_provider(
        vmp_text=fixture["text"],
        vmp_sha256=vmp_hash,
        visible_artifacts=fixture["visible_artifacts"],
        configured_mode="COMPOSED_SPAN",
        provider_config_id=binding["provider_config_id"],
        provider_config_sha256=binding["provider_config_sha256"],
        normalizer_id=binding["normalizer_id"],
        normalizer_sha256=binding["normalizer_sha256"],
        selector_output=fixture["selector_output"],
        provider_units=fixture["provider_units"],
        dispatch_outcome="SUCCEEDED",
        failure_code="NONE",
        temperature=1.0,
    )


def _failure_counts(
    candidate: CandidateRun,
    semantic: Mapping[str, Any] | None,
    *,
    active_count: int,
) -> dict[str, int]:
    from .artifacts import build_failure_counts

    prediction = 0
    sep = 0
    feature = 0
    if semantic is not None:
        prediction = sum(len(row["endpoint_candidates"]) for row in semantic["prediction_audit"]["path_predictions"])
        sep = sum(len(row["pair_packet"]["pairs"]) for row in semantic["paths"])
        feature = sum(sum(row["semantic_feature_tensor"]["pair_mask"]) for row in semantic["paths"])
    binding = 7 + active_count + (3 + 2 * active_count if semantic is not None else 0)
    counts = {
        "configured_span_entries_capped": candidate.configured_span_entries_capped,
        "eligible_spans_capped": candidate.eligible_spans_capped,
        "provider": candidate.provider_count,
        "normalizer": candidate.normalizer_count,
        "candidate": candidate.candidate_count,
        "alignment": candidate.alignment_count,
        "prediction": prediction,
        "sep": sep,
        "feature": feature,
        "binding": binding,
        "envelope": 24,
    }
    return build_failure_counts(total=sum(counts.values()), **counts)  # type: ignore[return-value]


def _build_evaluation(
    *,
    fixture: Mapping[str, Any],
    vmp_bytes: bytes,
    vmp_hash: str,
    manifests: Mapping[str, dict[str, Any]],
    receipts: Mapping[str, dict[str, Any]],
    descriptor_bytes: Mapping[str, bytes],
    candidates: Mapping[str, CandidateRun],
    semantic: Mapping[str, dict[str, Any]],
    seeds: Mapping[str, dict[str, Any]],
    envelopes: Mapping[str, dict[str, Any]],
    validation_contexts: Mapping[str, Any],
    registry_artifact_bytes: bytes,
) -> dict[str, EvaluationBoundaryResult]:
    from .artifacts import (
        engine_envelope_bytes,
        five_seed_logit_artifact_bytes,
        system_artifact_manifest_bytes,
        system_artifact_manifest_sha256,
    )
    from .candidate import candidate_diagnostics_bytes, provider_execution_bytes
    from .evaluation import (
        EvaluationBoundaryResult,
        MetricArtifactBytes,
        MetricEnvelopeArtifactBytes,
        UniverseSemanticContext,
        evaluate_boundary,
        gold_inventory_artifact,
        registry_reference_bundle_artifact,
    )
    from .preflight import preflight_receipt_bytes

    registry_manifest_hash = manifests["C01_BASE"]["registry_binding"]["registry_artifact_sha256"]
    registry_references_hash = sha256(b"fisher-e0-synthetic-registry-references").hexdigest()
    bundle_value = {
        "schema_version": "1.0.0",
        "registry_snapshot_id": "registry_synthetic_e0",
        "resolver_version": "resolver_0.0.0-synthetic",
        "registry_manifest_sha256": registry_manifest_hash,
        "registry_references_sha256": registry_references_hash,
    }
    bundle = registry_reference_bundle_artifact(bundle_value)
    actor = fixture["endpoint_candidates"][0]
    destination = fixture["endpoint_candidates"][1]
    resolution = fixture["registry_resolution"]
    inventory = {
        "inventory_version": "1.0.0",
        "item_id": fixture["item_id"],
        "vmp_sha256": vmp_hash,
        "final_annotation_id": "annotation_synthetic_e0",
        "actors": [{"span_index": 0, "start": actor["start"], "end": actor["end"], "text": fixture["text"][actor["start"]:actor["end"]]}],
        "destinations": [{"span_index": 0, "start": destination["start"], "end": destination["end"], "text": fixture["text"][destination["start"]:destination["end"]], "kind": destination["kind"]}],
        "registry_references": [{
            "registry_reference_id": "registry_reference_synthetic_e0",
            "actor_span_index": 0,
            "destination_span_index": 0,
            "label": resolution["state"],
            "registry_coverage": resolution["registry_coverage"].lower(),
            "registry_evidence_ids": resolution["evidence_ids"],
            "registry_snapshot_id": "registry_synthetic_e0",
            "resolver_version": "resolver_0.0.0-synthetic",
        }],
    }
    gold = gold_inventory_artifact(inventory, vmp_text=fixture["text"])
    entry = {
        "item_id": fixture["item_id"],
        "partition": "development",
        "vmp_sha256": vmp_hash,
        "final_annotation_id": "annotation_synthetic_e0",
        "gold_inventory_size_bytes": len(gold.data),
        "gold_inventory_sha256": gold.sha256,
        "gold_pair_count": 1,
        "gold_empty": False,
    }
    dataset_hashes = {
        "items_jsonl_sha256": sha256(b"fisher-e0-synthetic-items").hexdigest(),
        "annotations_jsonl_sha256": sha256(b"fisher-e0-synthetic-annotations").hexdigest(),
        "registry_manifest_jsonl_sha256": registry_manifest_hash,
        "registry_references_jsonl_sha256": registry_references_hash,
    }
    universe = {
        "schema_version": "1.0.0",
        "universe_id": "evaluation_universe_synthetic_e0",
        "partition": "development",
        "dataset_artifact_hashes": dataset_hashes,
        "registry_reference_bundle_sha256": bundle.sha256,
        "entries": [entry],
    }
    universe_bytes = canonical_json_bytes(universe)
    context = UniverseSemanticContext(
        expected_entries=(entry,),
        dataset_artifact_hashes=dataset_hashes,
        registry_reference_bundle=bundle_value,
        gold_inventory_bytes={gold.sha256: gold.data},
        vmp_text_by_item_id={fixture["item_id"]: fixture["text"]},
    )
    results: dict[str, EvaluationBoundaryResult] = {}
    for condition in ("C01", "C11"):
        key = _system_key(condition, "BASE")
        manifest = manifests[key]
        envelope = envelopes[key]
        envelope_raw = engine_envelope_bytes(
            envelope, context=validation_contexts[key]
        )
        envelope_hash = sha256(envelope_raw).hexdigest()
        submission = {
            "schema_version": "1.0.0",
            "evaluation_universe_sha256": sha256(universe_bytes).hexdigest(),
            "system_artifact_manifest_sha256": system_artifact_manifest_sha256(manifest),
            "entries": [{"item_id": fixture["item_id"], "envelope_sha256": envelope_hash}],
        }

        candidate = candidates[key]
        semantic_result = semantic[key]
        semantic_by_id = {row["path_id"]: row for row in semantic_result["paths"]}
        path_artifact_bytes = {
            path.path_id: raw
            for path, raw in zip(
                candidate.internal_paths, candidate.candidate_path_artifact_bytes
            )
        }
        artifact_bundle = MetricEnvelopeArtifactBytes(
            engine_envelope_bytes=envelope_raw,
            engine_input_descriptor_bytes=descriptor_bytes[key],
            preflight_receipt_bytes=preflight_receipt_bytes(receipts[key]),
            vmp_artifact_bytes=vmp_bytes,
            system_manifest_bytes=system_artifact_manifest_bytes(manifest),
            provider_manifest_bytes=candidate.provider_manifest_bytes,
            provider_execution_bytes=provider_execution_bytes(candidate.provider_execution),
            candidate_diagnostics_bytes=candidate_diagnostics_bytes(candidate.candidate_diagnostics),
            candidate_path_artifact_bytes=path_artifact_bytes,
            registry_artifact_bytes=registry_artifact_bytes,
            prediction_audit_bytes=canonical_json_bytes(semantic_result["prediction_audit"]),
            pair_packet_bytes_by_path={
                path_id: canonical_json_bytes(row["pair_packet"])
                for path_id, row in semantic_by_id.items()
            },
            semantic_feature_plan_bytes_by_path={
                path_id: canonical_json_bytes(row["semantic_feature_plan"])
                for path_id, row in semantic_by_id.items()
            },
            feature_tensor_bytes_by_path={
                path_id: canonical_json_bytes(row["semantic_feature_tensor"])
                for path_id, row in semantic_by_id.items()
            },
            five_seed_artifact_bytes=five_seed_logit_artifact_bytes(seeds[key]),
        )
        metric_artifacts = MetricArtifactBytes(
            project_root=Path(__file__).resolve().parents[1],
            system_manifest_bundle={
                system["system_id"]: system_artifact_manifest_bytes(system)
                for system in manifests.values()
            },
            envelopes={envelope_hash: artifact_bundle},
        )
        result = evaluate_boundary(
            universe_bytes,
            canonical_json_bytes(submission),
            universe_receipt_id=f"metric_universe_input_{condition.lower()}",
            input_receipt_id=f"metric_input_{condition.lower()}",
            metric_run_id=f"metric_run_synthetic_{condition.lower()}",
            condition=condition,
            system_id=manifest["system_id"],
            system_variant="BASE",
            semantic_context=context,
            metric_artifacts=metric_artifacts,
            declared_n_all=1,
            declared_n_gold_empty=0,
            declared_n_gold_nonempty=1,
        )
        if result.metric_run is None or result.metric_run.manifest["status"] != "VALID":
            raise HarnessError("engine_evaluation_invalid")
        results[key] = result
    return results


def run_synthetic_e0(fixture: Mapping[str, Any], *, project_root: Path) -> SyntheticE0Result:
    recorder = SourceClosureRecorder(
        project_root,
        (
            "fisher_engine/__init__.py",
            "fisher_engine/__main__.py",
            "fisher_engine/harness.py",
        ),
    )
    with recorder:
        import fisher_data as data_package_module
        from fisher_data import validator as data_validator_module
        from . import artifacts as artifacts_module
        from . import candidate as candidate_module
        from . import evaluation as evaluation_module
        from . import preflight as preflight_module
        from . import semantic as semantic_module
        from . import _numeric as numeric_module

        for module in (
            data_package_module,
            data_validator_module,
            artifacts_module,
            candidate_module,
            evaluation_module,
            preflight_module,
            semantic_module,
            numeric_module,
        ):
            recorder.record_executed_file(module.__file__)
        value = _validate_fixture(dict(fixture))
    closure = recorder.finalize()

    from ._numeric import f64_bits_to_float
    from .artifacts import (
        EngineValidationContext,
        build_engine_run_envelope,
        build_five_seed_logit_artifact,
        engine_run_envelope_sha256,
        five_seed_logit_artifact_bytes,
        five_seed_logit_artifact_sha256,
        semantic_enabled,
        system_artifact_manifest_bytes,
        system_artifact_manifest_sha256,
        validate_system_manifest_bundle,
    )
    from .candidate import candidate_diagnostics_bytes, provider_execution_bytes
    from .preflight import (
        EngineInputDescriptor,
        SuppliedVMPArtifact,
        engine_preflight_receipt_sha256,
        preflight_engine_input,
        preflight_receipt_bytes,
        validate_pass_preflight_context,
    )
    from .semantic import (
        build_semantic_artifacts,
        build_synthetic_registry_artifact,
        frozen_registry_from_artifact,
    )

    fixture_hash = sha256(canonical_json_bytes(value)).hexdigest()
    vmp = {"text": value["text"], "visible_artifacts": value["visible_artifacts"]}
    vmp_bytes = canonical_json_bytes(vmp)
    vmp_hash = sha256(vmp_bytes).hexdigest()
    actor_row = value["endpoint_candidates"][0]
    destination_row = value["endpoint_candidates"][1]
    _, registry_artifact_bytes, registry_artifact_hash = build_synthetic_registry_artifact(
        registry_snapshot_id="registry_synthetic_e0",
        resolver_version="resolver_0.0.0-synthetic",
        records={
            (
                value["text"][actor_row["start"]:actor_row["end"]],
                destination_row["kind"],
                value["text"][destination_row["start"]:destination_row["end"]],
            ): value["registry_resolution"]
        },
    )
    manifests = _build_systems(
        closure,
        fixture_hash=fixture_hash,
        registry_artifact_hash=registry_artifact_hash,
    )
    system_bundle = {
        manifest["system_id"]: system_artifact_manifest_bytes(manifest)
        for manifest in manifests.values()
    }
    validate_system_manifest_bundle(system_bundle)
    receipts: dict[str, dict[str, Any]] = {}
    descriptors: dict[str, bytes] = {}
    candidates: dict[str, CandidateRun] = {}
    semantics: dict[str, dict[str, Any]] = {}
    seeds: dict[str, dict[str, Any]] = {}
    envelopes: dict[str, dict[str, Any]] = {}
    validation_contexts: dict[str, EngineValidationContext] = {}

    registry = frozen_registry_from_artifact(
        registry_artifact_bytes, expected_sha256=registry_artifact_hash
    )
    for condition, variant in SYSTEM_COMBINATIONS:
        key = _system_key(condition, variant)
        manifest = manifests[key]
        manifest_hash = system_artifact_manifest_sha256(manifest)
        descriptor = EngineInputDescriptor(
            run_id=f"engine_run_{condition.lower()}_{variant.lower()}",
            condition=condition,
            system_id=manifest["system_id"],
            system_variant=variant,
            system_artifact_manifest_sha256=manifest_hash,
            item_id=value["item_id"],
            vmp_sha256=vmp_hash,
        )
        descriptor_bytes = descriptor.to_bytes()
        descriptors[key] = descriptor_bytes
        receipt = preflight_engine_input(
            descriptor_bytes,
            preflight_id=f"engine_preflight_{condition.lower()}_{variant.lower()}",
            system_artifact_bytes=system_artifact_manifest_bytes(manifest),
            vmp_artifact=SuppliedVMPArtifact(value["item_id"], vmp_bytes),
            project_root=project_root,
            system_manifest_bundle=system_bundle,
        )
        if receipt["status"] != "PASS":
            raise HarnessError("engine_preflight_failed")
        receipts[key] = receipt
        preflight_context = validate_pass_preflight_context(
            descriptor_bytes=descriptor_bytes,
            receipt_bytes=preflight_receipt_bytes(receipt),
            system_manifest_bytes=system_artifact_manifest_bytes(manifest),
            supplied_vmp=SuppliedVMPArtifact(value["item_id"], vmp_bytes),
            project_root=project_root,
            system_manifest_bundle=system_bundle,
        )
        candidate = _candidate_for_system(value, vmp_hash, manifest)
        if candidate.execution_status != "VALID":
            raise HarnessError("engine_candidate_failed")
        candidates[key] = candidate
        active_paths = candidate.internal_paths if condition in {"C10", "C11"} else candidate.internal_paths[:1]
        active_ids = [path.path_id for path in active_paths]
        semantic_result: dict[str, Any] | None = None
        if semantic_enabled(condition, variant):
            emitted = {path.path_id: value["endpoint_candidates"] for path in active_paths}
            semantic_result = build_semantic_artifacts(
                vmp_text=value["text"],
                vmp_sha256=vmp_hash,
                active_paths=active_paths,
                emitted_candidates_by_path=emitted,
                registry_resolver=registry,
            )
            semantics[key] = semantic_result
        raw_seed_rows = value["seed_logits_f64_bits"]
        if any(len(row) != len(candidate.internal_paths) for row in raw_seed_rows):
            raise HarnessError("engine_fixture_seed_width")
        active_seed_rows = [row[: len(active_ids)] for row in raw_seed_rows]
        seed = build_five_seed_logit_artifact(
            system_artifact_manifest_sha256=manifest_hash,
            vmp_sha256=vmp_hash,
            active_path_ids=active_ids,
            seed_logits=[[f64_bits_to_float(bits) for bits in row] for row in active_seed_rows],
        )
        seeds[key] = seed
        sep_hashes = [] if semantic_result is None else [{"path_id": row["path_id"], "sha256": row["pair_packet_sha256"]} for row in semantic_result["paths"]]
        feature_hashes = [] if semantic_result is None else [{"path_id": row["path_id"], "sha256": row["semantic_feature_tensor_sha256"]} for row in semantic_result["paths"]]
        path_artifact_bytes = {
            path.path_id: raw
            for path, raw in zip(
                candidate.internal_paths, candidate.candidate_path_artifact_bytes
            )
        }
        semantic_by_id = (
            {}
            if semantic_result is None
            else {row["path_id"]: row for row in semantic_result["paths"]}
        )
        validation_context = EngineValidationContext(
            preflight=preflight_context,
            provider_manifest_bytes=candidate.provider_manifest_bytes,
            provider_execution_bytes=provider_execution_bytes(candidate.provider_execution),
            candidate_diagnostics_bytes=candidate_diagnostics_bytes(candidate.candidate_diagnostics),
            candidate_path_artifact_bytes=path_artifact_bytes,
            five_seed_artifact_bytes=five_seed_logit_artifact_bytes(seed),
            prediction_audit_bytes=(
                None
                if semantic_result is None
                else canonical_json_bytes(semantic_result["prediction_audit"])
            ),
            registry_artifact_bytes=(
                registry_artifact_bytes if semantic_result is not None else None
            ),
            pair_packet_bytes_by_path={
                path_id: canonical_json_bytes(row["pair_packet"])
                for path_id, row in semantic_by_id.items()
            },
            semantic_feature_plan_bytes_by_path={
                path_id: canonical_json_bytes(row["semantic_feature_plan"])
                for path_id, row in semantic_by_id.items()
            },
            feature_tensor_bytes_by_path={
                path_id: canonical_json_bytes(row["semantic_feature_tensor"])
                for path_id, row in semantic_by_id.items()
            },
        )
        validation_contexts[key] = validation_context
        envelope = build_engine_run_envelope(
            preflight_context=preflight_context,
            validation_context=validation_context,
            provider_execution=candidate.provider_execution,
            failure_stage="NONE",
            failure_counts=_failure_counts(
                candidate, semantic_result, active_count=len(active_ids)
            ),
            candidate_diagnostics=candidate.candidate_diagnostics,
            candidate_paths=list(candidate.candidate_paths),
            active_path_ids=active_ids,
            five_seed_logit_artifact_sha256=five_seed_logit_artifact_sha256(seed),
            prediction_audit_sha256=None if semantic_result is None else semantic_result["prediction_audit_sha256"],
            sep_packet_hashes=sep_hashes,
            feature_plan_id=None if semantic_result is None else "E0_VMP_CATEGORY_MEAN_V1",
            feature_tensor_hashes=feature_hashes,
        )
        envelopes[key] = envelope

    evaluations = _build_evaluation(
        fixture=value,
        vmp_bytes=vmp_bytes,
        vmp_hash=vmp_hash,
        manifests=manifests,
        receipts=receipts,
        descriptor_bytes=descriptors,
        candidates=candidates,
        semantic=semantics,
        seeds=seeds,
        envelopes=envelopes,
        validation_contexts=validation_contexts,
        registry_artifact_bytes=registry_artifact_bytes,
    )
    rows = []
    for condition, variant in SYSTEM_COMBINATIONS:
        key = _system_key(condition, variant)
        candidate = candidates[key]
        semantic_result = semantics.get(key)
        evaluation = evaluations.get(key)
        rows.append({
            "condition": condition,
            "system_variant": variant,
            "system_artifact_manifest_sha256": system_artifact_manifest_sha256(manifests[key]),
            "engine_preflight_receipt_sha256": engine_preflight_receipt_sha256(receipts[key]),
            "provider_reading_manifest_sha256": candidate.provider_manifest_sha256,
            "candidate_count": candidate.candidate_count,
            "prediction_audit_sha256": None if semantic_result is None else semantic_result["prediction_audit_sha256"],
            "semantic_path_count": 0 if semantic_result is None else len(semantic_result["paths"]),
            "five_seed_logit_artifact_sha256": five_seed_logit_artifact_sha256(seeds[key]),
            "engine_run_envelope_sha256": engine_run_envelope_sha256(
                envelopes[key], context=validation_contexts[key]
            ),
            "metric_run_manifest_sha256": None if evaluation is None else evaluation.metric_run.manifest_sha256,
        })
    report = {
        "report_version": "1.0.0",
        "scope": "SYNTHETIC_E0_ONLY",
        "fixture_sha256": fixture_hash,
        "preflight_pass_count": len(receipts),
        "valid_envelope_count": len(envelopes),
        "valid_metric_run_count": len(evaluations),
        "systems": rows,
        "claims": [
            "INTERFACE_REHEARSAL_ONLY",
            "NO_TRAINED_MODEL",
            "NO_AUTHENTIC_DATA",
            "NO_PERFORMANCE_CLAIM",
            "G5_G6_REMAIN_BLOCKED",
        ],
        "invalid_codes": [],
        "status": "PASS",
    }
    canonical_json_bytes(report)
    return SyntheticE0Result(
        report,
        manifests,
        receipts,
        candidates,
        semantics,
        seeds,
        envelopes,
        evaluations,
        validation_contexts,
        descriptors,
        registry_artifact_bytes,
    )


def run_synthetic_e0_bytes(raw: bytes, *, project_root: Path) -> SyntheticE0Result:
    return run_synthetic_e0(load_synthetic_fixture(raw), project_root=project_root)


def format_report_json(result: SyntheticE0Result) -> str:
    return canonical_json_bytes(result.report).decode("utf-8")


def format_report_text(result: SyntheticE0Result) -> str:
    report = result.report
    return "\n".join(
        (
            "Fisher synthetic E0: PASS",
            f"preflights: {report['preflight_pass_count']}/8",
            f"valid envelopes: {report['valid_envelope_count']}/8",
            f"valid synthetic metric runs: {report['valid_metric_run_count']}/2",
            "claims: interface rehearsal only; no trained model, authentic data, or performance claim",
            "gates: G5/G6 remain blocked",
        )
    )


__all__ = [
    "HarnessError",
    "SyntheticE0Result",
    "format_report_json",
    "format_report_text",
    "load_synthetic_fixture",
    "run_synthetic_e0",
    "run_synthetic_e0_bytes",
]
