from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import io
import json
import math
from pathlib import Path
import runpy
import sys
import tempfile
import threading
import types
import unittest

from fisher_engine._canonical import (
    CanonicalError,
    MAX_JSON_NESTING,
    canonical_json_bytes,
    read_cap_plus_one,
    strict_json_loads,
)
from fisher_engine._numeric import (
    f64_bits_to_float,
    float_to_f64_bits,
    ordered_logsumexp,
    ordered_softmax,
    sequential_mean,
    sequential_sum,
)
from fisher_engine.artifacts import (
    ALLOWED_SYSTEMS,
    ArtifactValidationError,
    EngineValidationContext,
    build_engine_run_envelope,
    build_five_seed_logit_artifact,
    build_system_artifact_manifest,
    five_seed_logit_artifact_bytes,
    five_seed_logit_artifact_sha256,
    semantic_enabled,
    system_artifact_manifest_bytes,
    system_artifact_manifest_sha256,
    validate_engine_envelope,
    validate_five_seed_logit_artifact,
    validate_system_artifact_manifest,
    validate_system_manifest_bundle,
)
from fisher_engine.candidate import (
    candidate_diagnostics_bytes,
    provider_execution_bytes,
    run_candidate_provider,
)
from fisher_engine.preflight import (
    EngineInputDescriptor,
    SuppliedVMPArtifact,
    preflight_engine_input,
    preflight_receipt_bytes,
    validate_pass_preflight_context,
)
from fisher_engine.semantic import build_synthetic_registry_artifact
from fisher_engine.source_closure import SourceClosureRecorder, source_manifest, validate_source_closure


ROOT = Path(__file__).resolve().parents[1]


class TrackingStream(io.BytesIO):
    def __init__(self, value: bytes) -> None:
        super().__init__(value)
        self.requests: list[int] = []

    def read(self, size: int = -1) -> bytes:
        self.requests.append(size)
        return super().read(size)


class HostileOverReturningStream:
    def __init__(self, value: bytes) -> None:
        self.value = value
        self.requests: list[int] = []

    def read(self, size: int = -1) -> bytes:
        self.requests.append(size)
        return self.value


class CanonicalAndNumericTests(unittest.TestCase):
    def test_declared_order_unicode_and_no_terminal_lf(self) -> None:
        value = {"z": "தமிழ்", "a": [1, True, None]}
        encoded = canonical_json_bytes(value)
        self.assertEqual(encoded, '{"z":"தமிழ்","a":[1,true,null]}'.encode())
        self.assertFalse(encoded.endswith(b"\n"))

    def test_nonnfc_and_nonfinite_are_rejected(self) -> None:
        with self.assertRaisesRegex(CanonicalError, "canonical_non_nfc"):
            canonical_json_bytes({"value": "e\u0301"})
        with self.assertRaisesRegex(CanonicalError, "canonical_nonfinite"):
            canonical_json_bytes({"value": math.inf})

    def test_strict_scanner_duplicate_wins_over_nonfinite_and_later_syntax(self) -> None:
        raw = b'{"x":1,"x":NaN,'
        with self.assertRaises(CanonicalError) as caught:
            strict_json_loads(raw, prefix="probe")
        self.assertEqual(caught.exception.code, "probe_duplicate_key")

    def test_strict_scanner_nonfinite_wins_over_later_syntax(self) -> None:
        with self.assertRaises(CanonicalError) as caught:
            strict_json_loads(b'{"x":NaN,', prefix="probe")
        self.assertEqual(caught.exception.code, "probe_nonfinite")

    def test_strict_scanner_rejects_whitespace_as_noncanonical(self) -> None:
        with self.assertRaises(CanonicalError) as caught:
            strict_json_loads(b'{"x": 1}', prefix="probe")
        self.assertEqual(caught.exception.code, "probe_noncanonical_bytes")

    def test_cap_plus_one_reader_never_requests_more(self) -> None:
        stream = TrackingStream(b"abcdef")
        result = read_cap_plus_one(stream, 4)
        self.assertEqual(result.data, b"abcde")
        self.assertTrue(result.exceeded)
        self.assertEqual(stream.requests, [5])

    def test_cap_plus_one_clips_a_hostile_over_returning_reader(self) -> None:
        stream = HostileOverReturningStream(b"hostile-over-return")
        result = read_cap_plus_one(stream, 4)
        self.assertEqual(result.data, b"hosti")
        self.assertTrue(result.exceeded)
        self.assertEqual(stream.requests, [5])

    def test_json_nesting_limit_is_total_and_controlled(self) -> None:
        accepted = (b"[" * MAX_JSON_NESTING) + b"0" + (b"]" * MAX_JSON_NESTING)
        self.assertIsNotNone(strict_json_loads(accepted, prefix="probe"))
        rejected = b"[" + accepted + b"]"
        with self.assertRaises(CanonicalError) as caught:
            strict_json_loads(rejected, prefix="probe")
        self.assertEqual(caught.exception.code, "probe_invalid_json")

        value: object = 0
        for _ in range(MAX_JSON_NESTING + 1):
            value = [value]
        with self.assertRaises(CanonicalError) as caught:
            canonical_json_bytes(value)
        self.assertEqual(caught.exception.code, "canonical_nesting_too_deep")

    def test_binary64_known_answers_and_signed_zero(self) -> None:
        self.assertEqual(float_to_f64_bits(-0.0), "0000000000000000")
        self.assertEqual(float_to_f64_bits(1.0), "3ff0000000000000")
        with self.assertRaisesRegex(CanonicalError, "numeric_negative_zero"):
            f64_bits_to_float("8000000000000000")
        self.assertEqual(float_to_f64_bits(ordered_logsumexp([0.0, 0.0])), "3fe62e42fefa39ef")

    def test_sequential_arithmetic_is_not_reassociated(self) -> None:
        values = [1e16, 1.0, -1e16]
        self.assertEqual(sequential_sum(values), 0.0)
        self.assertEqual(sequential_mean(values), 0.0)

    def test_softmax_has_separate_accumulation_order(self) -> None:
        numerators, denominator, maximum, weights = ordered_softmax(
            [0.0, 0.0], 1.0, accumulation_order=[1, 0]
        )
        self.assertEqual([float_to_f64_bits(value) for value in numerators], ["3ff0000000000000"] * 2)
        self.assertEqual(float_to_f64_bits(denominator), "4000000000000000")
        self.assertEqual(float_to_f64_bits(maximum), "0000000000000000")
        self.assertEqual([float_to_f64_bits(value) for value in weights], ["3fe0000000000000"] * 2)


class SourceAndArtifactTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.closure = SourceClosureRecorder(ROOT, ["fisher_engine/artifacts.py"]).finalize()
        cls.item = json.loads((ROOT / "examples/pilot/items.jsonl").read_text().splitlines()[0])
        cls.vmp = {"text": cls.item["text"], "visible_artifacts": cls.item["visible_artifacts"]}
        cls.vmp_bytes = canonical_json_bytes(cls.vmp)
        cls.vmp_hash = sha256(cls.vmp_bytes).hexdigest()
        _, cls.registry_bytes, cls.registry_hash = build_synthetic_registry_artifact(
            registry_snapshot_id="registry_synthetic_e0",
            resolver_version="resolver_0.0.0-synthetic",
            records={
                ("synthetic_actor", "DOMAIN", "synthetic_destination"): {
                    "state": "MATCH",
                    "registry_coverage": "COMPLETE",
                    "evidence_ids": ["registry_evidence_synthetic"],
                }
            },
        )

    def system(self, condition: str, variant: str, **kwargs: object) -> dict:
        return build_system_artifact_manifest(
            system_id=f"system_e0_{condition.lower()}_{variant.lower()}",
            condition=condition,
            system_variant=variant,
            executed_source_closure=self.closure,
            registry_artifact_sha256=self.registry_hash,
            **kwargs,
        )

    def system_bundle(self) -> dict[str, bytes]:
        manifests: dict[tuple[str, str], dict] = {}
        for condition in ("C00", "C10", "C01", "C11"):
            manifests[(condition, "BASE")] = self.system(condition, "BASE")
        matched = {
            ("C00", "CAPACITY_CONTROL"): ("C01", "BASE"),
            ("C10", "CAPACITY_CONTROL"): ("C11", "BASE"),
            ("C01", "SUPERVISION_CONTROL"): ("C01", "BASE"),
            ("C11", "SUPERVISION_CONTROL"): ("C11", "BASE"),
        }
        for key, base_key in matched.items():
            base = manifests[base_key]
            manifests[key] = self.system(
                *key,
                matched_system_id=base["system_id"],
                matched_system_artifact_manifest_sha256=system_artifact_manifest_sha256(base),
            )
        return {
            manifest["system_id"]: system_artifact_manifest_bytes(manifest)
            for manifest in manifests.values()
        }

    def pass_evidence(self, manifest: dict) -> tuple[dict, object]:
        descriptor = EngineInputDescriptor(
            run_id="engine_run_core_fixture",
            condition=manifest["condition"],
            system_id=manifest["system_id"],
            system_variant=manifest["system_variant"],
            system_artifact_manifest_sha256=system_artifact_manifest_sha256(manifest),
            item_id=self.item["item_id"],
            vmp_sha256=self.vmp_hash,
        )
        descriptor_bytes = descriptor.to_bytes()
        bundle = self.system_bundle()
        receipt = preflight_engine_input(
            descriptor_bytes,
            preflight_id="engine_preflight_core_fixture",
            system_artifact_bytes=system_artifact_manifest_bytes(manifest),
            vmp_artifact=SuppliedVMPArtifact(self.item["item_id"], self.vmp_bytes),
            project_root=ROOT,
            system_manifest_bundle=bundle,
        )
        context = validate_pass_preflight_context(
            descriptor_bytes=descriptor_bytes,
            receipt_bytes=preflight_receipt_bytes(receipt),
            system_manifest_bytes=system_artifact_manifest_bytes(manifest),
            supplied_vmp=SuppliedVMPArtifact(self.item["item_id"], self.vmp_bytes),
            project_root=ROOT,
            system_manifest_bundle=bundle,
        )
        return receipt, context

    def test_source_manifest_and_closure_are_canonical(self) -> None:
        manifest = source_manifest(ROOT, ["fisher_engine/_numeric.py", "fisher_engine/_canonical.py"])
        self.assertEqual([row["path"] for row in manifest["files"]], ["fisher_engine/_canonical.py", "fisher_engine/_numeric.py"])
        validate_source_closure(self.closure)

    def test_source_closure_records_runpy_execution_not_process_history(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            script = Path(directory) / "executed_probe.py"
            script.write_text("RESULT = 1\n", encoding="utf-8")
            relative = script.relative_to(ROOT).as_posix()
            recorder = SourceClosureRecorder(ROOT, ["fisher_engine/source_closure.py"])
            with recorder:
                runpy.run_path(str(script))
            closure = recorder.finalize()
            self.assertIn(relative, [row["path"] for row in closure["files"]])

        stale_name = "fisher_engine.stale_history_probe"
        stale = types.ModuleType(stale_name)
        stale.__file__ = str(ROOT / "fisher_engine/candidate.py")
        before = SourceClosureRecorder(ROOT, ["fisher_engine/source_closure.py"]).finalize()
        sys.modules[stale_name] = stale
        try:
            after = SourceClosureRecorder(ROOT, ["fisher_engine/source_closure.py"]).finalize()
        finally:
            sys.modules.pop(stale_name, None)
        self.assertEqual(before, after)

    def test_nested_source_recorders_are_reentrant_and_root_scoped(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            script = Path(directory) / "nested_probe.py"
            script.write_text("RESULT = 1\n", encoding="utf-8")
            relative = script.relative_to(ROOT).as_posix()
            outer = SourceClosureRecorder(ROOT, ["fisher_engine/source_closure.py"])
            inner = SourceClosureRecorder(ROOT, ["fisher_engine/source_closure.py"])
            with outer:
                with inner:
                    runpy.run_path(str(script))
            self.assertIn(relative, [row["path"] for row in outer.finalize()["files"]])
            self.assertIn(relative, [row["path"] for row in inner.finalize()["files"]])

        with tempfile.TemporaryDirectory() as directory:
            outside = Path(directory) / "outside_probe.py"
            outside.write_text("RESULT = 1\n", encoding="utf-8")
            recorder = SourceClosureRecorder(ROOT, ["fisher_engine/source_closure.py"])
            with recorder:
                runpy.run_path(str(outside))
            self.assertNotIn(
                "outside_probe.py", [row["path"] for row in recorder.finalize()["files"]]
            )

    def test_unreconciled_project_exec_invalidates_source_closure(self) -> None:
        recorder = SourceClosureRecorder(ROOT, ["fisher_engine/source_closure.py"])
        missing = ROOT / "fisher_engine/nonexistent_dynamic_probe.py"
        with recorder:
            code = compile("RESULT = 1", str(missing), "exec")
            exec(code, {})
        with self.assertRaisesRegex(CanonicalError, "source_instrumentation_failed"):
            recorder.finalize()

    def test_source_recorder_observes_project_exec_in_worker_thread(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            script = Path(directory) / "thread_probe.py"
            script.write_text("RESULT = 1\n", encoding="utf-8")
            relative = script.relative_to(ROOT).as_posix()
            recorder = SourceClosureRecorder(ROOT, ["fisher_engine/source_closure.py"])
            with recorder:
                worker = threading.Thread(target=runpy.run_path, args=(str(script),))
                worker.start()
                worker.join()
            self.assertIn(relative, [row["path"] for row in recorder.finalize()["files"]])

    def test_all_eight_system_masks_validate(self) -> None:
        bases: dict[str, tuple[str, str]] = {}
        for condition in ("C00", "C10", "C01", "C11"):
            manifest = self.system(condition, "BASE")
            validate_system_artifact_manifest(manifest)
            bases[condition] = (manifest["system_id"], system_artifact_manifest_sha256(manifest))
            registry = manifest["registry_binding"]
            self.assertEqual(registry["registry_snapshot_id"] is not None, semantic_enabled(condition, "BASE"))
        for condition, variant in (("C00", "CAPACITY_CONTROL"), ("C10", "CAPACITY_CONTROL"), ("C01", "SUPERVISION_CONTROL"), ("C11", "SUPERVISION_CONTROL")):
            matched = "C01" if condition == "C00" else "C11" if condition == "C10" else condition
            manifest = self.system(
                condition,
                variant,
                matched_system_id=bases[matched][0],
                matched_system_artifact_manifest_sha256=bases[matched][1],
            )
            validate_system_artifact_manifest(manifest)
            self.assertIsNone(manifest["registry_binding"]["registry_snapshot_id"])
        self.assertEqual(len(ALLOWED_SYSTEMS), 8)

    def test_system_bundle_rejects_wrong_control_match_and_source_hash(self) -> None:
        bundle = self.system_bundle()
        validate_system_manifest_bundle(bundle)

        control_id = "system_e0_c00_capacity_control"
        wrong_match = json.loads(bundle[control_id])
        wrong_match["model_binding"]["matched_system_id"] = "system_e0_c00_base"
        mutated = dict(bundle)
        mutated[control_id] = canonical_json_bytes(wrong_match)
        with self.assertRaises(ArtifactValidationError):
            validate_system_manifest_bundle(mutated)

        source_mutation = json.loads(bundle["system_e0_c00_base"])
        source_mutation["provider_binding"]["provider_source_manifest_sha256"] = "a" * 64
        with self.assertRaises(ArtifactValidationError):
            validate_system_artifact_manifest(source_mutation)

    def test_system_manifest_declared_order_and_hash(self) -> None:
        manifest = self.system("C00", "BASE")
        encoded = system_artifact_manifest_bytes(manifest)
        self.assertEqual(sha256(encoded).hexdigest(), system_artifact_manifest_sha256(manifest))
        self.assertFalse(encoded.endswith(b"\n"))
        mutated = deepcopy(manifest)
        mutated["environment_binding"]["float_contract"] = "not-a-contract"
        with self.assertRaises(ArtifactValidationError):
            validate_system_artifact_manifest(mutated)

    def test_five_seed_mean_uses_exact_seed_order(self) -> None:
        artifact = build_five_seed_logit_artifact(
            system_artifact_manifest_sha256="a" * 64,
            vmp_sha256="b" * 64,
            active_path_ids=["candidate_path_one", "candidate_path_two"],
            seed_logits=[[1e16, 1.0], [1.0, 2.0], [-1e16, 3.0], [4.0, 4.0], [5.0, 5.0]],
        )
        validate_five_seed_logit_artifact(artifact)
        self.assertEqual(artifact["mean_logits_f64_bits"], [float_to_f64_bits(1.8), float_to_f64_bits(3.0)])
        self.assertEqual(five_seed_logit_artifact_sha256(artifact), sha256(canonical_json_bytes(artifact)).hexdigest())

    def test_valid_identity_envelope_and_static_nonsemantic_mask(self) -> None:
        manifest = self.system("C00", "BASE")
        receipt, preflight_context = self.pass_evidence(manifest)
        binding = manifest["provider_binding"]
        candidate = run_candidate_provider(
            vmp_text=self.vmp["text"], vmp_sha256=self.vmp_hash,
            visible_artifacts=self.vmp["visible_artifacts"],
            configured_mode="COMPOSED_SPAN",
            provider_config_id=binding["provider_config_id"],
            provider_config_sha256=binding["provider_config_sha256"],
            normalizer_id=binding["normalizer_id"],
            normalizer_sha256=binding["normalizer_sha256"],
            selector_output=[],
        )
        path_id = candidate.internal_paths[0].path_id
        seed = build_five_seed_logit_artifact(
            system_artifact_manifest_sha256=system_artifact_manifest_sha256(manifest),
            vmp_sha256=self.vmp_hash,
            active_path_ids=[path_id],
            seed_logits=[[0.0], [0.0], [0.0], [0.0], [0.0]],
        )
        counts = {
            "total": 33 + len(self.vmp["text"]), "configured_span_entries_capped": 0, "eligible_spans_capped": 0,
            "provider": 0, "normalizer": 0, "candidate": 1, "alignment": len(self.vmp["text"]),
            "prediction": 0, "sep": 0, "feature": 0, "binding": 8, "envelope": 24,
        }
        validation_context = EngineValidationContext(
            preflight=preflight_context,
            provider_manifest_bytes=candidate.provider_manifest_bytes,
            provider_execution_bytes=provider_execution_bytes(candidate.provider_execution),
            candidate_diagnostics_bytes=candidate_diagnostics_bytes(candidate.candidate_diagnostics),
            candidate_path_artifact_bytes={
                path.path_id: raw
                for path, raw in zip(candidate.internal_paths, candidate.candidate_path_artifact_bytes)
            },
            five_seed_artifact_bytes=five_seed_logit_artifact_bytes(seed),
        )
        envelope = build_engine_run_envelope(
            preflight_context=preflight_context,
            validation_context=validation_context,
            provider_execution=candidate.provider_execution,
            failure_stage="NONE",
            failure_counts=counts,
            candidate_diagnostics=candidate.candidate_diagnostics,
            candidate_paths=list(candidate.candidate_paths),
            active_path_ids=[path_id],
            five_seed_logit_artifact_sha256=five_seed_logit_artifact_sha256(seed),
        )
        validate_engine_envelope(envelope, context=validation_context)
        self.assertIsNone(envelope["prediction_audit_sha256"])
        self.assertEqual(envelope["sep_packet_hashes"], [])

    def test_degraded_union_stops_before_seed_and_semantics(self) -> None:
        manifest = self.system("C01", "BASE")
        receipt, preflight_context = self.pass_evidence(manifest)
        span = {"span_index": 0, "start": 0, "end": 5, "source_text": self.vmp["text"][:5]}
        binding = manifest["provider_binding"]
        candidate = run_candidate_provider(
            vmp_text=self.vmp["text"], vmp_sha256=self.vmp_hash,
            visible_artifacts=self.vmp["visible_artifacts"], configured_mode="COMPOSED_SPAN",
            provider_config_id=binding["provider_config_id"], provider_config_sha256=binding["provider_config_sha256"],
            normalizer_id=binding["normalizer_id"], normalizer_sha256=binding["normalizer_sha256"],
            selector_output=[span], dispatch_outcome="UNAVAILABLE_FALLBACK",
            failure_code="PROVIDER_UNAVAILABLE",
        )
        counts = {
            "total": 37 + len(self.vmp["text"]), "configured_span_entries_capped": 1,
            "eligible_spans_capped": 1, "provider": 0, "normalizer": 0, "candidate": 1,
            "alignment": len(self.vmp["text"]), "prediction": 0, "sep": 0, "feature": 0,
            "binding": 10, "envelope": 24,
        }
        validation_context = EngineValidationContext(
            preflight=preflight_context, provider_manifest_bytes=candidate.provider_manifest_bytes,
            provider_execution_bytes=provider_execution_bytes(candidate.provider_execution),
            candidate_diagnostics_bytes=candidate_diagnostics_bytes(candidate.candidate_diagnostics),
            candidate_path_artifact_bytes={path.path_id: raw for path, raw in zip(candidate.internal_paths, candidate.candidate_path_artifact_bytes)},
            registry_artifact_bytes=self.registry_bytes,
        )
        envelope = build_engine_run_envelope(
            preflight_context=preflight_context, validation_context=validation_context,
            provider_execution=candidate.provider_execution,
            failure_stage="PROVIDER_EXECUTION",
            failure_counts=counts,
            candidate_diagnostics=candidate.candidate_diagnostics,
            candidate_paths=list(candidate.candidate_paths),
            active_path_ids=[candidate.internal_paths[0].path_id],
            five_seed_logit_artifact_sha256=None,
            execution_status="DEGRADED_STOP_AFTER_IDENTITY",
        )
        self.assertIsNone(envelope["prediction_audit_sha256"])
        self.assertEqual(envelope["registry_snapshot_id"], "registry_synthetic_e0")

    def test_invalid_provider_union_retains_no_downstream_artifact(self) -> None:
        manifest = self.system("C01", "BASE")
        receipt, preflight_context = self.pass_evidence(manifest)
        binding = manifest["provider_binding"]
        candidate = run_candidate_provider(
            vmp_text=self.vmp["text"], vmp_sha256=self.vmp_hash,
            visible_artifacts=self.vmp["visible_artifacts"], configured_mode="COMPOSED_SPAN",
            provider_config_id=binding["provider_config_id"], provider_config_sha256=binding["provider_config_sha256"],
            normalizer_id=binding["normalizer_id"], normalizer_sha256=binding["normalizer_sha256"],
            selector_output={"not": "an array"},
        )
        counts = {
            "total": 33, "configured_span_entries_capped": 0, "eligible_spans_capped": 0,
            "provider": 0, "normalizer": 0, "candidate": 0, "alignment": 0,
            "prediction": 0, "sep": 0, "feature": 0, "binding": 9, "envelope": 24,
        }
        validation_context = EngineValidationContext(
            preflight=preflight_context, provider_manifest_bytes=None,
            provider_execution_bytes=provider_execution_bytes(candidate.provider_execution),
            candidate_diagnostics_bytes=None, candidate_path_artifact_bytes={},
            registry_artifact_bytes=self.registry_bytes,
        )
        envelope = build_engine_run_envelope(
            preflight_context=preflight_context, validation_context=validation_context,
            provider_execution=candidate.provider_execution,
            failure_stage="PROVIDER_EXECUTION",
            failure_counts=counts,
            candidate_diagnostics=None,
            candidate_paths=[],
            active_path_ids=[],
            five_seed_logit_artifact_sha256=None,
            execution_status="INVALID",
            invalid_codes=["engine_invalid_eligibility"],
        )
        self.assertEqual(envelope["execution_status"], "INVALID")
        self.assertEqual(envelope["candidate_paths"], [])
        self.assertEqual(envelope["sep_packet_hashes"], [])
        self.assertEqual(envelope["registry_snapshot_id"], "registry_synthetic_e0")


if __name__ == "__main__":
    unittest.main()
