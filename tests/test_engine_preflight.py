from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import io
import json
from pathlib import Path
import unittest

from fisher_engine._canonical import canonical_json_bytes
from fisher_engine.artifacts import (
    ArtifactValidationError,
    EngineValidationContext,
    build_engine_run_envelope,
    build_system_artifact_manifest,
    system_artifact_manifest_bytes,
    system_artifact_manifest_sha256,
)
from fisher_engine.preflight import (
    DESCRIPTOR_CAP,
    EngineInputDescriptor,
    SuppliedVMPArtifact,
    engine_preflight_receipt_sha256,
    preflight_engine_input,
)
from fisher_engine.source_closure import SourceClosureRecorder


ROOT = Path(__file__).resolve().parents[1]


class EnginePreflightTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        item = json.loads((ROOT / "examples/pilot/items.jsonl").read_text().splitlines()[0])
        cls.item_id = item["item_id"]
        cls.vmp_bytes = canonical_json_bytes({"text": item["text"], "visible_artifacts": item["visible_artifacts"]})
        cls.vmp = SuppliedVMPArtifact(cls.item_id, cls.vmp_bytes)
        closure = SourceClosureRecorder(ROOT, ["fisher_engine/preflight.py"]).finalize()
        cls.manifest = build_system_artifact_manifest(
            system_id="system_e0_preflight",
            condition="C00",
            system_variant="BASE",
            executed_source_closure=closure,
        )
        manifests: dict[tuple[str, str], dict] = {("C00", "BASE"): cls.manifest}
        for condition in ("C10", "C01", "C11"):
            manifests[(condition, "BASE")] = build_system_artifact_manifest(
                system_id=f"system_e0_preflight_{condition.lower()}_base",
                condition=condition,
                system_variant="BASE",
                executed_source_closure=closure,
            )
        matches = {
            ("C00", "CAPACITY_CONTROL"): ("C01", "BASE"),
            ("C10", "CAPACITY_CONTROL"): ("C11", "BASE"),
            ("C01", "SUPERVISION_CONTROL"): ("C01", "BASE"),
            ("C11", "SUPERVISION_CONTROL"): ("C11", "BASE"),
        }
        for key, base_key in matches.items():
            base = manifests[base_key]
            manifests[key] = build_system_artifact_manifest(
                system_id=f"system_e0_preflight_{key[0].lower()}_{key[1].lower()}",
                condition=key[0],
                system_variant=key[1],
                executed_source_closure=closure,
                matched_system_id=base["system_id"],
                matched_system_artifact_manifest_sha256=system_artifact_manifest_sha256(base),
            )
        cls.bundle = {
            manifest["system_id"]: system_artifact_manifest_bytes(manifest)
            for manifest in manifests.values()
        }
        cls.manifest_bytes = system_artifact_manifest_bytes(cls.manifest)
        cls.descriptor = EngineInputDescriptor(
            run_id="engine_run_preflight",
            condition="C00",
            system_id="system_e0_preflight",
            system_variant="BASE",
            system_artifact_manifest_sha256=system_artifact_manifest_sha256(cls.manifest),
            item_id=cls.item_id,
            vmp_sha256=sha256(cls.vmp_bytes).hexdigest(),
        )

    def run_preflight(self, raw: bytes, *, system: bytes | None = None, vmp: SuppliedVMPArtifact | None = None) -> dict:
        return preflight_engine_input(
            raw,
            preflight_id="engine_preflight_test",
            system_artifact_bytes=self.manifest_bytes if system is None else system,
            vmp_artifact=self.vmp if vmp is None else vmp,
            system_manifest_bundle=self.bundle,
        )

    def test_pass_binds_every_reference_and_hashes_receipt(self) -> None:
        receipt = self.run_preflight(self.descriptor.to_bytes())
        self.assertEqual(receipt["status"], "PASS")
        self.assertEqual((receipt["decoded_descriptor_count"], receipt["validated_system_manifest_count"], receipt["validated_vmp_count"]), (1, 1, 1))
        self.assertEqual(receipt["item_id"], self.item_id)
        self.assertEqual(len(engine_preflight_receipt_sha256(receipt)), 64)

    def test_too_large_reads_and_hashes_exact_cap_plus_one(self) -> None:
        raw = b"x" * (DESCRIPTOR_CAP + 50)
        stream = io.BytesIO(raw)
        receipt = self.run_preflight(stream)
        self.assertEqual(receipt["invalid_codes"], ["preflight_descriptor_too_large"])
        self.assertEqual(receipt["prefix_bytes_hashed"], DESCRIPTOR_CAP + 1)
        self.assertEqual(receipt["submitted_prefix_sha256"], sha256(raw[: DESCRIPTOR_CAP + 1]).hexdigest())
        self.assertEqual(stream.tell(), DESCRIPTOR_CAP + 1)

    def test_reader_memory_failure_returns_a_controlled_receipt(self) -> None:
        class MemoryFailingReader:
            def read(self, size: int) -> bytes:
                del size
                raise MemoryError

        receipt = self.run_preflight(MemoryFailingReader())
        self.assertEqual(
            receipt["invalid_codes"], ["preflight_descriptor_invalid_json"]
        )
        self.assertEqual(receipt["status"], "FAIL")

    def test_raw_parser_code_precedence(self) -> None:
        cases = [
            (b"\xef\xbb\xbf{}", "preflight_descriptor_bom"),
            (b'\xff', "preflight_descriptor_invalid_utf8"),
            (b'{"x":1,"x":NaN,', "preflight_descriptor_duplicate_key"),
            (b'{"x":NaN,', "preflight_descriptor_nonfinite"),
            (b'{"x":', "preflight_descriptor_invalid_json"),
            ('{"x":"e\u0301"}'.encode(), "preflight_descriptor_non_nfc"),
            (b'{"x": 1}', "preflight_descriptor_noncanonical_bytes"),
            (b'{}', "preflight_descriptor_schema_or_enum"),
        ]
        for raw, expected in cases:
            with self.subTest(expected=expected):
                receipt = self.run_preflight(raw)
                self.assertEqual(receipt["invalid_codes"], [expected])
                self.assertEqual(receipt["decoded_descriptor_count"], 0)

    def test_missing_precedes_hash_and_validation(self) -> None:
        receipt = preflight_engine_input(
            self.descriptor.to_bytes(),
            preflight_id="engine_preflight_test",
            system_artifact_bytes=None,
            vmp_artifact=self.vmp,
            system_manifest_bundle=self.bundle,
        )
        self.assertEqual(receipt["invalid_codes"], ["preflight_missing_referenced_artifact"])
        self.assertEqual(receipt["decoded_descriptor_count"], 1)

    def test_both_hashes_precede_both_artifact_validations(self) -> None:
        receipt = self.run_preflight(self.descriptor.to_bytes(), system=b"{}")
        self.assertEqual(receipt["invalid_codes"], ["preflight_artifact_hash_mismatch"])
        self.assertEqual((receipt["validated_system_manifest_count"], receipt["validated_vmp_count"]), (0, 0))

    def test_system_validation_precedes_vmp_validation(self) -> None:
        malformed = deepcopy(self.manifest)
        malformed["environment_binding"]["float_contract"] = "BAD"
        malformed_bytes = canonical_json_bytes(malformed)
        descriptor = EngineInputDescriptor(
            run_id=self.descriptor.run_id,
            condition=self.descriptor.condition,
            system_id=self.descriptor.system_id,
            system_variant=self.descriptor.system_variant,
            system_artifact_manifest_sha256=sha256(malformed_bytes).hexdigest(),
            item_id=self.descriptor.item_id,
            vmp_sha256=self.descriptor.vmp_sha256,
        )
        bad_vmp = SuppliedVMPArtifact(self.item_id, b"{}")
        descriptor = EngineInputDescriptor(
            run_id=descriptor.run_id,
            condition=descriptor.condition,
            system_id=descriptor.system_id,
            system_variant=descriptor.system_variant,
            system_artifact_manifest_sha256=descriptor.system_artifact_manifest_sha256,
            item_id=descriptor.item_id,
            vmp_sha256=sha256(bad_vmp.data).hexdigest(),
        )
        receipt = preflight_engine_input(
            descriptor.to_bytes(), preflight_id="engine_preflight_test",
            system_artifact_bytes=malformed_bytes, vmp_artifact=bad_vmp,
            system_manifest_bundle=self.bundle,
        )
        self.assertEqual(receipt["invalid_codes"], ["preflight_invalid_system_manifest"])
        self.assertEqual((receipt["validated_system_manifest_count"], receipt["validated_vmp_count"]), (0, 0))

    def test_forged_runtime_identity_is_rejected(self) -> None:
        forged = deepcopy(self.manifest)
        forged["environment_binding"]["python_version"] = "9.9.9"
        forged_bytes = canonical_json_bytes(forged)
        descriptor = EngineInputDescriptor(
            run_id=self.descriptor.run_id,
            condition=self.descriptor.condition,
            system_id=self.descriptor.system_id,
            system_variant=self.descriptor.system_variant,
            system_artifact_manifest_sha256=sha256(forged_bytes).hexdigest(),
            item_id=self.descriptor.item_id,
            vmp_sha256=self.descriptor.vmp_sha256,
        )
        receipt = preflight_engine_input(
            descriptor.to_bytes(), preflight_id="engine_preflight_test",
            system_artifact_bytes=forged_bytes, vmp_artifact=self.vmp,
            system_manifest_bundle={
                **self.bundle,
                self.manifest["system_id"]: forged_bytes,
            },
        )
        self.assertEqual(receipt["invalid_codes"], ["preflight_invalid_system_manifest"])

    def test_referenced_artifact_bounds_fail_without_unbounded_parsing(self) -> None:
        oversized_system = b"x" * (4 * 1024 * 1024 + 1)
        descriptor = EngineInputDescriptor(
            run_id=self.descriptor.run_id, condition=self.descriptor.condition,
            system_id=self.descriptor.system_id, system_variant=self.descriptor.system_variant,
            system_artifact_manifest_sha256=sha256(oversized_system).hexdigest(),
            item_id=self.item_id, vmp_sha256=self.descriptor.vmp_sha256,
        )
        receipt = preflight_engine_input(
            descriptor.to_bytes(), preflight_id="engine_preflight_test",
            system_artifact_bytes=oversized_system, vmp_artifact=self.vmp,
            system_manifest_bundle=self.bundle,
        )
        self.assertEqual(receipt["invalid_codes"], ["preflight_invalid_system_manifest"])

        oversized_vmp = b"x" * (4 * 1024 * 1024 + 1)
        descriptor = EngineInputDescriptor(
            run_id=self.descriptor.run_id, condition=self.descriptor.condition,
            system_id=self.descriptor.system_id, system_variant=self.descriptor.system_variant,
            system_artifact_manifest_sha256=self.descriptor.system_artifact_manifest_sha256,
            item_id=self.item_id, vmp_sha256=sha256(oversized_vmp).hexdigest(),
        )
        receipt = preflight_engine_input(
            descriptor.to_bytes(), preflight_id="engine_preflight_test",
            system_artifact_bytes=self.manifest_bytes,
            vmp_artifact=SuppliedVMPArtifact(self.item_id, oversized_vmp),
            system_manifest_bundle=self.bundle,
        )
        self.assertEqual(receipt["invalid_codes"], ["preflight_invalid_vmp"])
        self.assertEqual((receipt["validated_system_manifest_count"], receipt["validated_vmp_count"]), (1, 0))

    def test_invalid_vmp_retains_only_system_validation_count(self) -> None:
        bad_vmp = SuppliedVMPArtifact(self.item_id, b"{}")
        descriptor = EngineInputDescriptor(
            run_id=self.descriptor.run_id, condition=self.descriptor.condition,
            system_id=self.descriptor.system_id, system_variant=self.descriptor.system_variant,
            system_artifact_manifest_sha256=self.descriptor.system_artifact_manifest_sha256,
            item_id=self.item_id, vmp_sha256=sha256(bad_vmp.data).hexdigest(),
        )
        receipt = preflight_engine_input(
            descriptor.to_bytes(), preflight_id="engine_preflight_test",
            system_artifact_bytes=self.manifest_bytes, vmp_artifact=bad_vmp,
            system_manifest_bundle=self.bundle,
        )
        self.assertEqual(receipt["invalid_codes"], ["preflight_invalid_vmp"])
        self.assertEqual((receipt["validated_system_manifest_count"], receipt["validated_vmp_count"]), (1, 0))
        self.assertTrue(all(receipt[field] is None for field in ("run_id", "condition", "system_id", "system_variant", "item_id", "vmp_sha256")))

    def test_fail_receipt_cannot_construct_an_envelope(self) -> None:
        failed = self.run_preflight(b"{}")
        context = EngineValidationContext(
            preflight=failed,
            provider_manifest_bytes=None,
            provider_execution_bytes=b"{}",
            candidate_diagnostics_bytes=None,
            candidate_path_artifact_bytes={},
        )
        with self.assertRaises(ArtifactValidationError):
            build_engine_run_envelope(
                preflight_context=failed,
                validation_context=context,
                provider_execution={}, failure_stage="NONE", failure_counts={},
                candidate_diagnostics=None, candidate_paths=[], active_path_ids=[],
                five_seed_logit_artifact_sha256=None,
            )


if __name__ == "__main__":
    unittest.main()
