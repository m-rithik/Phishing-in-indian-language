from __future__ import annotations

from copy import deepcopy
from dataclasses import replace
from hashlib import sha256
import io
import math
from pathlib import Path
import unittest

from fisher_engine._canonical import canonical_json_bytes, strict_json_loads
from fisher_engine.evaluation import (
    _EnvelopeEvidence,
    EvaluationBindingError,
    EvaluationError,
    MAX_SUBMISSION_ROWS,
    MAX_UNIVERSE_ENTRIES,
    MetricArtifactBytes,
    MetricEnvelopeArtifactBytes,
    PathPairPrediction,
    UNIVERSE_MAX_BYTES,
    UniverseSemanticContext,
    classify_submission_rows,
    compute_pair_metrics,
    evaluate_boundary,
    evaluate_metric_run,
    _evaluate_metric_run_with_inspector,
    five_seed_mean_logits,
    gold_inventory_artifact,
    _make_engine_envelope_inspector,
    parse_metric_input,
    parse_metric_universe_input,
    supplied_temperature_summary,
    validate_universe_semantics,
)


ZERO_HASH = "0" * 64
ONE_HASH = "1" * 64
TWO_HASH = "2" * 64
SYSTEM_ID = "system_test"
SYSTEM_HASH = "a" * 64
ROOT = Path(__file__).resolve().parents[1]


def bundle() -> dict:
    return {
        "schema_version": "1.0.0",
        "registry_snapshot_id": "registry_test",
        "resolver_version": "resolver_1.0.0",
        "registry_manifest_sha256": ZERO_HASH,
        "registry_references_sha256": ONE_HASH,
    }


def dataset_hashes() -> dict:
    return {
        "items_jsonl_sha256": TWO_HASH,
        "annotations_jsonl_sha256": "3" * 64,
        "registry_manifest_jsonl_sha256": ZERO_HASH,
        "registry_references_jsonl_sha256": ONE_HASH,
    }


def empty_gold(item_id: str, vmp_hash: str, annotation_id: str) -> dict:
    return {
        "inventory_version": "1.0.0",
        "item_id": item_id,
        "vmp_sha256": vmp_hash,
        "final_annotation_id": annotation_id,
        "actors": [],
        "destinations": [],
        "registry_references": [],
    }


def nonempty_gold(item_id: str, vmp_hash: str, annotation_id: str, text: str = "A D") -> dict:
    return {
        "inventory_version": "1.0.0",
        "item_id": item_id,
        "vmp_sha256": vmp_hash,
        "final_annotation_id": annotation_id,
        "actors": [{"span_index": 0, "start": 0, "end": 1, "text": "A"}],
        "destinations": [
            {"span_index": 1, "start": 2, "end": 3, "text": "D", "kind": "DOMAIN"}
        ],
        "registry_references": [
            {
                "registry_reference_id": f"registry_reference_{item_id.removeprefix('item_')}",
                "actor_span_index": 0,
                "destination_span_index": 1,
                "label": "MATCH",
                "registry_coverage": "complete",
                "registry_evidence_ids": ["registry_evidence_test"],
                "registry_snapshot_id": "registry_test",
                "resolver_version": "resolver_1.0.0",
            }
        ],
    }


def entry_for(inventory: dict, partition: str = "development") -> tuple[dict, bytes]:
    artifact = gold_inventory_artifact(inventory)
    entry = {
        "item_id": inventory["item_id"],
        "partition": partition,
        "vmp_sha256": inventory["vmp_sha256"],
        "final_annotation_id": inventory["final_annotation_id"],
        "gold_inventory_size_bytes": len(artifact.data),
        "gold_inventory_sha256": artifact.sha256,
        "gold_pair_count": len(inventory["registry_references"]),
        "gold_empty": not inventory["registry_references"],
    }
    return entry, artifact.data


def universe(entries: list[dict], *, partition: str = "development") -> dict:
    bundle_hash = sha256(canonical_json_bytes(bundle())).hexdigest()
    return {
        "schema_version": "1.0.0",
        "universe_id": "evaluation_universe_test",
        "partition": partition,
        "dataset_artifact_hashes": dataset_hashes(),
        "registry_reference_bundle_sha256": bundle_hash,
        "entries": entries,
    }


def submission(universe_hash: str, rows: list[dict]) -> dict:
    return {
        "schema_version": "1.0.0",
        "evaluation_universe_sha256": universe_hash,
        "system_artifact_manifest_sha256": SYSTEM_HASH,
        "entries": rows,
    }


def context(entries: list[dict], inventories: dict[str, bytes], texts: dict[str, str]) -> UniverseSemanticContext:
    return UniverseSemanticContext(
        expected_entries=tuple(entries),
        dataset_artifact_hashes=dataset_hashes(),
        registry_reference_bundle=bundle(),
        gold_inventory_bytes=inventories,
        vmp_text_by_item_id=texts,
    )


def parse_universe(value: dict):
    return parse_metric_universe_input(
        canonical_json_bytes(value), receipt_id="metric_universe_input_test"
    )


def parse_submission(value: dict, universe_hash: str):
    return parse_metric_input(
        canonical_json_bytes(value),
        receipt_id="metric_input_test",
        evaluation_universe_sha256=universe_hash,
    )


def evidence(
    item_id: str,
    vmp_hash: str,
    *,
    condition: str = "C01",
    status: str = "VALID",
    paths: tuple[PathPairPrediction, ...] | None = None,
) -> _EnvelopeEvidence:
    if paths is None:
        paths = (PathPairPrediction("path_test", 1.0, frozenset()),)
    return _EnvelopeEvidence(
        execution_status=status,
        item_id=item_id,
        vmp_sha256=vmp_hash,
        condition=condition,
        system_id=SYSTEM_ID,
        system_variant="BASE",
        system_artifact_manifest_sha256=SYSTEM_HASH,
        registry_snapshot_id="registry_test",
        registry_artifact_sha256=ZERO_HASH,
        resolver_version="resolver_1.0.0",
        paths=paths,
    )


class GoldInventoryTests(unittest.TestCase):
    def test_canonical_gold_inventory_hash_size_and_cartesian_closure(self) -> None:
        inventory = nonempty_gold("item_a", ZERO_HASH, "annotation_a")
        artifact = gold_inventory_artifact(inventory, vmp_text="A D")
        entry, _ = entry_for(inventory)
        self.assertEqual(len(artifact.data), entry["gold_inventory_size_bytes"])
        self.assertEqual(artifact.sha256, entry["gold_inventory_sha256"])
        self.assertEqual(artifact, gold_inventory_artifact(inventory, vmp_text="A D", expected_entry=entry))

    def test_gold_rejects_boolean_coordinate_slice_and_incomplete_product(self) -> None:
        inventory = nonempty_gold("item_a", ZERO_HASH, "annotation_a")
        inventory["actors"][0]["start"] = False
        with self.assertRaisesRegex(EvaluationError, "gold_inventory_actor"):
            gold_inventory_artifact(inventory, vmp_text="A D")
        inventory = nonempty_gold("item_a", ZERO_HASH, "annotation_a")
        inventory["registry_references"] = []
        with self.assertRaisesRegex(EvaluationError, "gold_inventory_cartesian_closure"):
            gold_inventory_artifact(inventory, vmp_text="A D")


class UniverseParserTests(unittest.TestCase):
    def assert_code(self, raw: bytes, code: str) -> dict:
        result = parse_metric_universe_input(raw, receipt_id="metric_universe_input_test")
        self.assertEqual(result.receipt["status"], "FAIL")
        self.assertEqual(result.receipt["invalid_codes"], [code])
        self.assertIsNone(result.universe)
        return result.receipt

    def test_all_ten_codes_and_hash_states(self) -> None:
        stream = io.BytesIO(b"x" * (UNIVERSE_MAX_BYTES + 9))
        too_large = parse_metric_universe_input(
            stream, receipt_id="metric_universe_input_test"
        ).receipt
        self.assertEqual(too_large["invalid_codes"], ["metric_universe_too_large"])
        self.assertEqual(stream.tell(), UNIVERSE_MAX_BYTES + 1)
        self.assertEqual(too_large["prefix_bytes_hashed"], UNIVERSE_MAX_BYTES + 1)
        self.assertEqual(too_large["submitted_prefix_sha256"], sha256(b"x" * (UNIVERSE_MAX_BYTES + 1)).hexdigest())
        self.assertIsNone(too_large["evaluation_universe_sha256"])

        cases = (
            (b"\xef\xbb\xbf{}", "metric_universe_bom"),
            (b'\xff', "metric_universe_invalid_utf8"),
            (b'{"a":NaN,"a":1', "metric_universe_duplicate_key"),
            (b'{"a":NaN}', "metric_universe_nonfinite"),
            (b'{', "metric_universe_invalid_json_syntax"),
            ('{"x":"e\u0301"}'.encode(), "metric_universe_non_nfc"),
            (b'{ "x":1}', "metric_universe_noncanonical_bytes"),
            (b'{}', "metric_universe_schema_or_enum"),
        )
        for raw, code in cases:
            with self.subTest(code=code):
                receipt = self.assert_code(raw, code)
                if code == "metric_universe_schema_or_enum":
                    self.assertEqual(receipt["evaluation_universe_sha256"], sha256(raw).hexdigest())
                else:
                    self.assertIsNone(receipt["evaluation_universe_sha256"])

        template, _ = entry_for(empty_gold("item_a", ZERO_HASH, "annotation_a"))
        entries = []
        for index in range(MAX_UNIVERSE_ENTRIES + 1):
            row = dict(template)
            row["item_id"] = f"item_{index:05d}"
            row["final_annotation_id"] = f"annotation_{index:05d}"
            entries.append(row)
        raw = canonical_json_bytes(universe(entries))
        receipt = self.assert_code(raw, "metric_universe_too_many_entries")
        self.assertEqual(receipt["decoded_entry_count"], 10001)
        self.assertEqual(receipt["validated_entry_count"], 0)
        self.assertEqual(receipt["evaluation_universe_sha256"], sha256(raw).hexdigest())

    def test_schema_precedes_entry_bound_and_counts_complete_array_only(self) -> None:
        row, _ = entry_for(empty_gold("item_a", ZERO_HASH, "annotation_a"))
        rows = [deepcopy(row) for _ in range(MAX_UNIVERSE_ENTRIES + 1)]
        rows[-1]["gold_pair_count"] = True
        raw = canonical_json_bytes(universe(rows))
        receipt = self.assert_code(raw, "metric_universe_schema_or_enum")
        self.assertEqual(receipt["decoded_entry_count"], 10001)
        self.assertEqual(receipt["validated_entry_count"], 0)

        truncated = self.assert_code(b'{"entries":[', "metric_universe_invalid_json_syntax")
        self.assertEqual(truncated["decoded_entry_count"], 0)

    def test_structural_empty_passes_but_semantic_closure_requires_nonempty(self) -> None:
        result = parse_universe(universe([]))
        self.assertEqual(result.receipt["status"], "PASS")
        self.assertEqual(result.receipt["decoded_entry_count"], 0)
        empty_context = context([], {}, {})
        self.assertFalse(validate_universe_semantics(result.universe, empty_context))

    def test_complete_semantic_closure_and_gold_binding(self) -> None:
        inventory = nonempty_gold("item_a", ZERO_HASH, "annotation_a")
        entry, raw_gold = entry_for(inventory)
        result = parse_universe(universe([entry]))
        semantic = context([entry], {entry["gold_inventory_sha256"]: raw_gold}, {"item_a": "A D"})
        self.assertTrue(validate_universe_semantics(result.universe, semantic))
        wrong = deepcopy(semantic.expected_entries[0])
        wrong["item_id"] = "item_b"
        self.assertFalse(
            validate_universe_semantics(
                result.universe,
                UniverseSemanticContext(
                    (wrong,), semantic.dataset_artifact_hashes, semantic.registry_reference_bundle,
                    semantic.gold_inventory_bytes, semantic.vmp_text_by_item_id,
                ),
            )
        )


class MetricInputTests(unittest.TestCase):
    def parse_failure(self, raw: bytes, universe_hash: str = ZERO_HASH) -> dict:
        result = parse_metric_input(
            raw,
            receipt_id="metric_input_test",
            evaluation_universe_sha256=universe_hash,
        )
        self.assertIsNotNone(result.receipt)
        self.assertIsNone(result.manifest)
        return result.receipt

    def test_input_failure_stages_hash_and_binding(self) -> None:
        receipt = self.parse_failure(b"x" * (UNIVERSE_MAX_BYTES + 1))
        self.assertEqual(receipt["failure_stage"], "BYTES")
        self.assertEqual(receipt["invalid_codes"], ["metric_input_oversized"])

        for raw, stage, code in (
            (b"\xff", "UTF8", "metric_input_invalid_utf8"),
            (b'{', "JSON", "metric_input_invalid_json"),
            (b'{}', "JSON", "metric_input_invalid_shape"),
            (b'{ "schema_version":"1.0.0"}', "CANONICAL", "metric_input_noncanonical"),
        ):
            with self.subTest(code=code):
                receipt = self.parse_failure(raw)
                self.assertEqual(receipt["failure_stage"], stage)
                self.assertEqual(receipt["invalid_codes"], [code])
                self.assertEqual(receipt["submitted_prefix_sha256"], sha256(raw).hexdigest())
                self.assertEqual(receipt["prefix_bytes_hashed"], len(raw))

        wrong = submission(ONE_HASH, [])
        raw = canonical_json_bytes(wrong)
        receipt = self.parse_failure(raw)
        self.assertEqual(receipt["failure_stage"], "BINDING")
        self.assertEqual(receipt["invalid_codes"], ["metric_input_universe_hash_mismatch"])

    def test_input_row_bound_and_success(self) -> None:
        rows = [
            {"item_id": f"item_{index:05d}", "envelope_sha256": ZERO_HASH}
            for index in range(MAX_SUBMISSION_ROWS + 1)
        ]
        raw = canonical_json_bytes(submission(ZERO_HASH, rows))
        receipt = self.parse_failure(raw)
        self.assertEqual(receipt["failure_stage"], "ROW_BOUND")
        self.assertEqual(receipt["decoded_row_count"], "GE_20001")
        self.assertEqual(receipt["validated_row_count"], "GE_20001")

        valid = submission(ZERO_HASH, [{"item_id": "item_a", "envelope_sha256": ONE_HASH}])
        result = parse_submission(valid, ZERO_HASH)
        self.assertIsNone(result.receipt)
        self.assertEqual(result.manifest, valid)
        self.assertEqual(result.manifest_sha256, sha256(canonical_json_bytes(valid)).hexdigest())

    def test_malformed_shape_precedes_binding(self) -> None:
        malformed = submission(ONE_HASH, [{"item_id": "item_a", "envelope_sha256": True}])
        receipt = self.parse_failure(canonical_json_bytes(malformed), ZERO_HASH)
        self.assertEqual(receipt["failure_stage"], "JSON")
        self.assertEqual(receipt["invalid_codes"], ["metric_input_invalid_shape"])


class AccountingAndBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.inventory_a = empty_gold("item_a", ZERO_HASH, "annotation_a")
        self.inventory_b = empty_gold("item_b", ONE_HASH, "annotation_b")
        self.entry_a, self.raw_a = entry_for(self.inventory_a)
        self.entry_b, self.raw_b = entry_for(self.inventory_b)
        self.entries = [self.entry_a, self.entry_b]
        self.universe_result = parse_universe(universe(self.entries))
        self.universe_hash = self.universe_result.receipt["evaluation_universe_sha256"]
        self.semantic = context(
            self.entries,
            {
                self.entry_a["gold_inventory_sha256"]: self.raw_a,
                self.entry_b["gold_inventory_sha256"]: self.raw_b,
            },
            {"item_a": "x", "item_b": "y"},
        )

    def test_fixed_row_classification(self) -> None:
        rows = [
            {"item_id": item_id, "envelope_sha256": ZERO_HASH}
            for item_id in ("item_b", "item_a", "item_a", "item_c", "item_c")
        ]
        result = classify_submission_rows(["item_a", "item_b"], rows)
        self.assertEqual(
            {
                key: result[key]
                for key in (
                    "submitted_count",
                    "missing_count",
                    "extra_count",
                    "duplicate_count",
                    "reordered_count",
                )
            },
            {"submitted_count": 5, "missing_count": 0, "extra_count": 1, "duplicate_count": 2, "reordered_count": 2},
        )

    def test_diagnostic_counts_saturate_without_retaining_unsafe_ids(self) -> None:
        rows = [
            {"item_id": f"item_extra_{index}", "envelope_sha256": ZERO_HASH}
            for index in range(MAX_SUBMISSION_ROWS + 1)
        ]
        result = classify_submission_rows([], rows)
        self.assertEqual(result["submitted_count"], "GE_20001")
        self.assertEqual(result["extra_count"], "GE_20001")
        self.assertEqual(result["unique_expected_rows"], [])

    def test_all_discrepancy_classes_and_no_deletion(self) -> None:
        payloads = {name: name.encode() for name in ("a", "b", "c", "d")}
        hashes = {name: sha256(raw).hexdigest() for name, raw in payloads.items()}
        rows = [
            {"item_id": "item_b", "envelope_sha256": hashes["b"]},
            {"item_id": "item_a", "envelope_sha256": hashes["a"]},
            {"item_id": "item_a", "envelope_sha256": hashes["c"]},
            {"item_id": "item_c", "envelope_sha256": hashes["d"]},
            {"item_id": "item_c", "envelope_sha256": hashes["d"]},
        ]
        input_result = parse_submission(submission(self.universe_hash, rows), self.universe_hash)
        opened: list[bytes] = []

        def inspector(raw: bytes) -> _EnvelopeEvidence:
            opened.append(raw)
            item_id = "item_a" if raw == b"a" else "item_b"
            vmp = ZERO_HASH if item_id == "item_a" else ONE_HASH
            return evidence(item_id, vmp)

        run = _evaluate_metric_run_with_inspector(
            metric_run_id="metric_run_test",
            condition="C01",
            system_id=SYSTEM_ID,
            system_variant="BASE",
            universe_result=self.universe_result,
            input_result=input_result,
            semantic_context=self.semantic,
            envelope_bytes={hashes[name]: payloads[name] for name in payloads},
            envelope_inspector=inspector,
            declared_n_all=2,
            declared_n_gold_empty=2,
            declared_n_gold_nonempty=0,
        )
        manifest = run.manifest
        self.assertEqual(manifest["status"], "INVALID")
        self.assertEqual(manifest["submitted_count"], 5)
        self.assertEqual(manifest["missing_count"], 0)
        self.assertEqual(manifest["extra_count"], 1)
        self.assertEqual(manifest["duplicate_count"], 2)
        self.assertEqual(manifest["reordered_count"], 2)
        self.assertEqual(manifest["inference_envelopes"], [])
        self.assertEqual(opened, [b"b", b"a"])

    def test_exclusive_envelope_outcomes_denominator_and_codes(self) -> None:
        rows = []
        raw_by_hash = {}
        for item_id, raw in (("item_a", b"a"), ("item_b", b"b")):
            digest = sha256(raw).hexdigest()
            rows.append({"item_id": item_id, "envelope_sha256": digest})
            raw_by_hash[digest] = raw
        input_result = parse_submission(submission(self.universe_hash, rows), self.universe_hash)

        def inspector(raw: bytes) -> _EnvelopeEvidence:
            if raw == b"a":
                return evidence("item_a", ZERO_HASH, status="DEGRADED_STOP_AFTER_IDENTITY")
            return evidence("item_b", TWO_HASH)

        run = _evaluate_metric_run_with_inspector(
            metric_run_id="metric_run_test",
            condition="C01",
            system_id=SYSTEM_ID,
            system_variant="BASE",
            universe_result=self.universe_result,
            input_result=input_result,
            semantic_context=self.semantic,
            envelope_bytes=raw_by_hash,
            envelope_inspector=inspector,
            declared_n_all=True,
            declared_n_gold_empty=2,
            declared_n_gold_nonempty=0,
        )
        self.assertEqual(run.manifest["degraded_count"], 1)
        self.assertEqual(run.manifest["mismatch_count"], 1)
        self.assertEqual(run.manifest["denominator_error_count"], 1)
        self.assertEqual(
            run.manifest["invalid_codes"],
            ["metric_binding_mismatch", "metric_degraded", "metric_invalid_denominator"],
        )

    def test_missing_and_unreadable_envelope_are_disjoint(self) -> None:
        raw = b"unreadable"
        digest = sha256(raw).hexdigest()
        rows = [{"item_id": "item_a", "envelope_sha256": digest}]
        input_result = parse_submission(
            submission(self.universe_hash, rows), self.universe_hash
        )
        run = _evaluate_metric_run_with_inspector(
            metric_run_id="metric_run_missing_invalid",
            condition="C01",
            system_id=SYSTEM_ID,
            system_variant="BASE",
            universe_result=self.universe_result,
            input_result=input_result,
            semantic_context=self.semantic,
            envelope_bytes={digest: raw},
            envelope_inspector=lambda _raw: (_ for _ in ()).throw(
                EvaluationError("unreadable")
            ),
            declared_n_all=2,
            declared_n_gold_empty=2,
            declared_n_gold_nonempty=0,
        )
        self.assertEqual(run.manifest["missing_count"], 1)
        self.assertEqual(run.manifest["invalid_count"], 1)
        self.assertEqual(
            run.manifest["invalid_codes"],
            ["metric_invalid_envelope", "metric_missing"],
        )

    def test_structural_submission_failure_precedes_empty_semantic_universe(self) -> None:
        empty_result = parse_universe(universe([]))
        result = evaluate_boundary(
            canonical_json_bytes(universe([])),
            b'{',
            universe_receipt_id="metric_universe_input_order",
            input_receipt_id="metric_input_order",
            metric_run_id="metric_run_order",
            condition="C01",
            system_id=SYSTEM_ID,
            system_variant="BASE",
            semantic_context=context([], {}, {}),
            metric_artifacts=MetricArtifactBytes(ROOT, {}, {}),
            declared_n_all=0,
            declared_n_gold_empty=0,
            declared_n_gold_nonempty=0,
        )
        self.assertEqual(result.universe_result.receipt["status"], "PASS")
        self.assertEqual(result.input_result.receipt["invalid_codes"], ["metric_input_invalid_json"])
        self.assertIsNone(result.metric_run)
        self.assertEqual(empty_result.receipt["status"], "PASS")

    def test_empty_semantic_universe_short_circuits_without_opening(self) -> None:
        empty_universe = universe([])
        parsed_universe = parse_universe(empty_universe)
        universe_hash = parsed_universe.receipt["evaluation_universe_sha256"]
        parsed_input = parse_submission(submission(universe_hash, []), universe_hash)
        run = evaluate_metric_run(
            metric_run_id="metric_run_empty",
            condition="C01",
            system_id=SYSTEM_ID,
            system_variant="BASE",
            universe_result=parsed_universe,
            input_result=parsed_input,
            semantic_context=context([], {}, {}),
            metric_artifacts=MetricArtifactBytes(ROOT, {}, {}),
            declared_n_all=0,
            declared_n_gold_empty=0,
            declared_n_gold_nonempty=0,
        )
        self.assertEqual(run.manifest["universe_error_count"], 1)
        self.assertEqual(run.manifest["submitted_count"], 0)
        self.assertEqual(run.manifest["invalid_codes"], ["metric_invalid_universe"])
        self.assertIsNone(run.pair_metrics)

    def test_valid_manifest_complete_order_metrics_and_determinism(self) -> None:
        inventory = nonempty_gold("item_a", ZERO_HASH, "annotation_a")
        entry, raw_gold = entry_for(inventory)
        parsed_universe = parse_universe(universe([entry]))
        universe_hash = parsed_universe.receipt["evaluation_universe_sha256"]
        envelope_raw = b"validated-engine-envelope-a"
        envelope_hash = sha256(envelope_raw).hexdigest()
        rows = [{"item_id": "item_a", "envelope_sha256": envelope_hash}]
        parsed_input = parse_submission(submission(universe_hash, rows), universe_hash)
        semantic = context(
            [entry], {entry["gold_inventory_sha256"]: raw_gold}, {"item_a": "A D"}
        )
        predicted = frozenset({(0, 1, 2, 3, "MATCH")})

        def inspector(raw: bytes) -> _EnvelopeEvidence:
            self.assertEqual(raw, envelope_raw)
            return evidence(
                "item_a",
                ZERO_HASH,
                paths=(PathPairPrediction("path_test", 1.0, predicted),),
            )

        arguments = dict(
            metric_run_id="metric_run_valid",
            condition="C01",
            system_id=SYSTEM_ID,
            system_variant="BASE",
            universe_result=parsed_universe,
            input_result=parsed_input,
            semantic_context=semantic,
            envelope_bytes={envelope_hash: envelope_raw},
            envelope_inspector=inspector,
            declared_n_all=1,
            declared_n_gold_empty=0,
            declared_n_gold_nonempty=1,
        )
        first = _evaluate_metric_run_with_inspector(**arguments)
        second = _evaluate_metric_run_with_inspector(**arguments)
        self.assertEqual(first.manifest["status"], "VALID")
        self.assertEqual(first.manifest["inference_envelopes"], rows)
        self.assertEqual(first.manifest["invalid_codes"], [])
        self.assertEqual(first.pair_metrics["rank1"]["F1_pair"], 1.0)
        self.assertEqual(first.manifest_bytes, second.manifest_bytes)
        self.assertEqual(first.manifest_sha256, second.manifest_sha256)


class PairMetricAndTemperatureTests(unittest.TestCase):
    P = (0, 1, 2, 3, "MATCH")
    X = (0, 1, 4, 5, "MISMATCH")

    def test_all_empty_algebra_has_positive_emptiness_denominator(self) -> None:
        result = compute_pair_metrics(
            "C01",
            {"item_a": frozenset(), "item_b": frozenset()},
            {
                "item_a": (PathPairPrediction("path_a", 1.0, frozenset()),),
                "item_b": (PathPairPrediction("path_b", 1.0, frozenset()),),
            },
        )
        rank = result["rank1"]
        self.assertEqual((rank["TP"], rank["FP"], rank["FN"]), (0.0, 0.0, 0.0))
        self.assertEqual((rank["precision_pair"], rank["recall_pair"], rank["F1_pair"]), (0.0, 0.0, 0.0))
        self.assertEqual(rank["pair_emptiness_accuracy"], 1.0)
        self.assertEqual(rank["gold_empty_recall"], 1.0)
        self.assertIsNone(rank["gold_nonempty_recall"])
        self.assertGreater(math.copysign(1.0, rank["F1_pair"]), 0.0)

    def test_known_q_weighted_and_rank1_vectors_include_gold_empty_fp(self) -> None:
        gold = {"item_a": frozenset({self.P}), "item_b": frozenset()}
        predictions = {
            "item_a": (
                PathPairPrediction("path_1", 0.25, frozenset({self.P})),
                PathPairPrediction("path_2", 0.75, frozenset({self.X})),
            ),
            "item_b": (
                PathPairPrediction("path_1", 0.25, frozenset()),
                PathPairPrediction("path_2", 0.75, frozenset({self.X})),
            ),
        }
        result = compute_pair_metrics("C11", gold, predictions)
        rank = result["rank1"]
        weighted = result["q_weighted"]
        self.assertEqual((rank["TP"], rank["FP"], rank["FN"]), (1.0, 0.0, 0.0))
        self.assertEqual(rank["pair_emptiness_accuracy"], 1.0)
        self.assertAlmostEqual(weighted["TP"], 0.25)
        self.assertAlmostEqual(weighted["FP"], 1.5)
        self.assertAlmostEqual(weighted["FN"], 0.75)
        self.assertAlmostEqual(weighted["pair_emptiness_accuracy"], 0.625)
        self.assertAlmostEqual(weighted["gold_empty_recall"], 0.25)
        self.assertEqual(weighted["gold_nonempty_recall"], 1.0)

    def test_five_seed_mean_temperature_and_rank_one_v(self) -> None:
        means = five_seed_mean_logits([[1.0], [2.0], [3.0], [4.0], [5.0]])
        self.assertEqual(means, (3.0,))
        rank = supplied_temperature_summary(means, [1.0], temperature=2.0, rank_one=True)
        self.assertEqual(rank["v"], 0.0)
        self.assertGreater(math.copysign(1.0, rank["v"]), 0.0)
        ensemble = supplied_temperature_summary([0.0, 2.0], [0.5, 0.5], temperature=1.0)
        self.assertGreater(ensemble["v"], 0.0)
        with self.assertRaisesRegex(EvaluationError, "temperature_invalid"):
            supplied_temperature_summary([0.0], [1.0], temperature=0.0, rank_one=True)


class DefaultInspectorIntegrationTests(unittest.TestCase):

    def build_fixture(self):
        from fisher_engine._numeric import float_to_f64_bits
        from fisher_engine.artifacts import (
            EngineValidationContext,
            build_engine_run_envelope,
            build_five_seed_logit_artifact,
            five_seed_logit_artifact_bytes,
            five_seed_logit_artifact_sha256,
            system_artifact_manifest_bytes,
            system_artifact_manifest_sha256,
        )
        from fisher_engine.candidate import (
            candidate_diagnostics_bytes,
            provider_execution_bytes,
            run_candidate_provider,
        )
        from fisher_engine.harness import _build_systems, _failure_counts
        from fisher_engine.preflight import (
            EngineInputDescriptor,
            SuppliedVMPArtifact,
            preflight_engine_input,
            preflight_receipt_bytes,
            validate_pass_preflight_context,
        )
        from fisher_engine.semantic import (
            OfflineRegistryResolver,
            build_semantic_artifacts,
            build_synthetic_registry_artifact,
        )
        from fisher_engine.source_closure import SourceClosureRecorder

        text = "A D"
        vmp_raw = canonical_json_bytes({"text": text, "visible_artifacts": []})
        vmp_hash = sha256(vmp_raw).hexdigest()
        records = {
            ("A", "DOMAIN", "D"): {
                "state": "MATCH",
                "registry_coverage": "COMPLETE",
                "evidence_ids": ["registry_evidence_test"],
            }
        }
        _, registry_raw, registry_hash = build_synthetic_registry_artifact(
            registry_snapshot_id="registry_synthetic_e0",
            resolver_version="resolver_0.0.0-synthetic",
            records=records,
        )
        closure = SourceClosureRecorder(
            ROOT, ("fisher_engine/__main__.py", "fisher_engine/harness.py")
        ).finalize()
        manifests = _build_systems(
            closure,
            fixture_hash=sha256(b"evaluation-trust-fixture").hexdigest(),
            registry_artifact_hash=registry_hash,
        )
        manifest = manifests["C01_BASE"]
        manifest_hash = system_artifact_manifest_sha256(manifest)
        system_bundle = {
            value["system_id"]: system_artifact_manifest_bytes(value)
            for value in manifests.values()
        }
        descriptor = EngineInputDescriptor(
            run_id="engine_run_inspector",
            condition="C01",
            system_id=manifest["system_id"],
            system_variant="BASE",
            system_artifact_manifest_sha256=manifest_hash,
            item_id="item_inspector",
            vmp_sha256=vmp_hash,
        )
        descriptor_raw = descriptor.to_bytes()
        receipt = preflight_engine_input(
            descriptor_raw,
            preflight_id="engine_preflight_inspector",
            system_artifact_bytes=system_bundle[manifest["system_id"]],
            vmp_artifact=SuppliedVMPArtifact("item_inspector", vmp_raw),
            project_root=ROOT,
            system_manifest_bundle=system_bundle,
        )
        self.assertEqual(receipt["status"], "PASS")
        receipt_raw = preflight_receipt_bytes(receipt)
        preflight = validate_pass_preflight_context(
            descriptor_bytes=descriptor_raw,
            receipt_bytes=receipt_raw,
            system_manifest_bytes=system_bundle[manifest["system_id"]],
            supplied_vmp=SuppliedVMPArtifact("item_inspector", vmp_raw),
            project_root=ROOT,
            system_manifest_bundle=system_bundle,
        )
        binding = manifest["provider_binding"]
        candidate_run = run_candidate_provider(
            vmp_text=text,
            vmp_sha256=vmp_hash,
            visible_artifacts=[],
            configured_mode="COMPOSED_SPAN",
            provider_config_id=binding["provider_config_id"],
            provider_config_sha256=binding["provider_config_sha256"],
            normalizer_id=binding["normalizer_id"],
            normalizer_sha256=binding["normalizer_sha256"],
            selector_output=[],
        )
        active_paths = candidate_run.internal_paths[:1]
        semantic = build_semantic_artifacts(
            vmp_text=text,
            vmp_sha256=vmp_hash,
            active_paths=active_paths,
            emitted_candidates_by_path={
                active_paths[0].path_id: [
                    {
                        "role": "ACTOR",
                        "start": 0,
                        "end": 1,
                        "kind": "NONE",
                        "score_f64_bits": float_to_f64_bits(1.0),
                    },
                    {
                        "role": "DESTINATION",
                        "start": 2,
                        "end": 3,
                        "kind": "DOMAIN",
                        "score_f64_bits": float_to_f64_bits(1.0),
                    },
                ]
            },
            registry_resolver=OfflineRegistryResolver(
                "registry_synthetic_e0", "resolver_0.0.0-synthetic", records
            ),
        )
        semantic_path = semantic["paths"][0]
        active_ids = [active_paths[0].path_id]
        seed = build_five_seed_logit_artifact(
            system_artifact_manifest_sha256=manifest_hash,
            vmp_sha256=vmp_hash,
            active_path_ids=active_ids,
            seed_logits=[[0.0]] * 5,
        )
        path_bytes = {
            path.path_id: raw
            for path, raw in zip(
                candidate_run.internal_paths,
                candidate_run.candidate_path_artifact_bytes,
            )
        }
        pair_bytes = {
            active_ids[0]: canonical_json_bytes(semantic_path["pair_packet"])
        }
        plan_bytes = {
            active_ids[0]: canonical_json_bytes(
                semantic_path["semantic_feature_plan"]
            )
        }
        tensor_bytes = {
            active_ids[0]: canonical_json_bytes(
                semantic_path["semantic_feature_tensor"]
            )
        }
        audit_raw = canonical_json_bytes(semantic["prediction_audit"])
        execution_raw = provider_execution_bytes(candidate_run.provider_execution)
        diagnostics_raw = candidate_diagnostics_bytes(
            candidate_run.candidate_diagnostics
        )
        seed_raw = five_seed_logit_artifact_bytes(seed)
        validation_context = EngineValidationContext(
            preflight=preflight,
            provider_manifest_bytes=candidate_run.provider_manifest_bytes,
            provider_execution_bytes=execution_raw,
            candidate_diagnostics_bytes=diagnostics_raw,
            candidate_path_artifact_bytes=path_bytes,
            five_seed_artifact_bytes=seed_raw,
            prediction_audit_bytes=audit_raw,
            registry_artifact_bytes=registry_raw,
            pair_packet_bytes_by_path=pair_bytes,
            semantic_feature_plan_bytes_by_path=plan_bytes,
            feature_tensor_bytes_by_path=tensor_bytes,
        )
        envelope = build_engine_run_envelope(
            preflight_context=preflight,
            validation_context=validation_context,
            provider_execution=candidate_run.provider_execution,
            failure_stage="NONE",
            failure_counts=_failure_counts(candidate_run, semantic, active_count=1),
            candidate_diagnostics=candidate_run.candidate_diagnostics,
            candidate_paths=list(candidate_run.candidate_paths),
            active_path_ids=active_ids,
            five_seed_logit_artifact_sha256=five_seed_logit_artifact_sha256(seed),
            prediction_audit_sha256=semantic["prediction_audit_sha256"],
            sep_packet_hashes=[
                {"path_id": active_ids[0], "sha256": semantic_path["pair_packet_sha256"]}
            ],
            feature_plan_id="E0_VMP_CATEGORY_MEAN_V1",
            feature_tensor_hashes=[
                {
                    "path_id": active_ids[0],
                    "sha256": semantic_path["semantic_feature_tensor_sha256"],
                }
            ],
        )
        envelope_raw = canonical_json_bytes(envelope)
        bundle = MetricEnvelopeArtifactBytes(
            engine_envelope_bytes=envelope_raw,
            engine_input_descriptor_bytes=descriptor_raw,
            preflight_receipt_bytes=receipt_raw,
            vmp_artifact_bytes=vmp_raw,
            system_manifest_bytes=system_bundle[manifest["system_id"]],
            provider_manifest_bytes=candidate_run.provider_manifest_bytes,
            provider_execution_bytes=execution_raw,
            candidate_diagnostics_bytes=diagnostics_raw,
            candidate_path_artifact_bytes=path_bytes,
            registry_artifact_bytes=registry_raw,
            prediction_audit_bytes=audit_raw,
            pair_packet_bytes_by_path=pair_bytes,
            semantic_feature_plan_bytes_by_path=plan_bytes,
            feature_tensor_bytes_by_path=tensor_bytes,
            five_seed_artifact_bytes=seed_raw,
        )
        envelope_hash = sha256(envelope_raw).hexdigest()
        store = MetricArtifactBytes(
            ROOT, system_bundle, {envelope_hash: bundle}
        )
        return envelope_raw, bundle, store, manifest, vmp_hash

    def test_default_inspector_validates_complete_artifact_chain(self) -> None:
        envelope_raw, _bundle, store, _manifest, _vmp_hash = self.build_fixture()
        inspector = _make_engine_envelope_inspector(store)
        result = inspector(envelope_raw)
        self.assertEqual(result.execution_status, "VALID")
        self.assertEqual(result.item_id, "item_inspector")
        self.assertEqual(result.paths[0].q, 1.0)
        self.assertEqual(result.paths[0].pairs, frozenset({(0, 1, 2, 3, "MATCH")}))

    def test_default_inspector_separates_missing_from_hash_mismatch(self) -> None:
        envelope_raw, bundle, store, _manifest, _vmp_hash = self.build_fixture()
        missing = MetricArtifactBytes(ROOT, store.system_manifest_bundle, {})
        with self.assertRaisesRegex(EvaluationError, "metric_missing_referenced_artifact"):
            _make_engine_envelope_inspector(missing)(envelope_raw)

        envelope_hash = sha256(envelope_raw).hexdigest()
        corrupt = MetricArtifactBytes(
            ROOT,
            store.system_manifest_bundle,
            {envelope_hash: replace(bundle, engine_envelope_bytes=b"corrupt")},
        )
        with self.assertRaisesRegex(
            EvaluationBindingError, "metric_referenced_artifact_hash_mismatch"
        ):
            _make_engine_envelope_inspector(corrupt)(envelope_raw)

        unreadable_raw = b"{"
        unreadable = MetricArtifactBytes(
            ROOT,
            store.system_manifest_bundle,
            {
                sha256(unreadable_raw).hexdigest(): replace(
                    bundle, engine_envelope_bytes=unreadable_raw
                )
            },
        )
        with self.assertRaises(EvaluationError) as raised:
            _make_engine_envelope_inspector(unreadable)(unreadable_raw)
        self.assertNotIsInstance(raised.exception, EvaluationBindingError)

    def test_exact_artifact_store_snapshots_input_mappings(self) -> None:
        envelope_raw, bundle, store, _manifest, _vmp_hash = self.build_fixture()
        envelope_hash = sha256(envelope_raw).hexdigest()
        mutable_envelopes = {envelope_hash: bundle}
        mutable_systems = dict(store.system_manifest_bundle)
        frozen = MetricArtifactBytes(ROOT, mutable_systems, mutable_envelopes)
        mutable_envelopes.clear()
        mutable_systems.clear()
        self.assertEqual(
            _make_engine_envelope_inspector(frozen)(envelope_raw).execution_status,
            "VALID",
        )

        mutable_packets = dict(bundle.pair_packet_bytes_by_path)
        frozen_bundle = replace(bundle, pair_packet_bytes_by_path=mutable_packets)
        mutable_packets.clear()
        frozen_store = MetricArtifactBytes(
            ROOT, store.system_manifest_bundle, {envelope_hash: frozen_bundle}
        )
        self.assertEqual(
            _make_engine_envelope_inspector(frozen_store)(
                envelope_raw
            ).execution_status,
            "VALID",
        )

    def test_rejects_forged_exact_artifact_categories(self) -> None:
        envelope_raw, bundle, store, _manifest, _vmp_hash = self.build_fixture()
        path_id = next(iter(bundle.candidate_path_artifact_bytes))
        envelope = strict_json_loads(envelope_raw, prefix="test_envelope")
        runtime_forge = deepcopy(envelope)
        runtime_forge["runtime"]["runtime_tag"] = "cpython_0.0.0"
        runtime_raw = canonical_json_bytes(runtime_forge)
        cases = {
            "registry": replace(bundle, registry_artifact_bytes=b"{}"),
            "prediction": replace(bundle, prediction_audit_bytes=b"{}"),
            "packet": replace(bundle, pair_packet_bytes_by_path={path_id: b"{}"}),
            "feature_plan": replace(
                bundle, semantic_feature_plan_bytes_by_path={path_id: b"{}"}
            ),
            "tensor": replace(bundle, feature_tensor_bytes_by_path={path_id: b"{}"}),
            "provider_manifest": replace(bundle, provider_manifest_bytes=b"{}"),
            "provider_execution": replace(bundle, provider_execution_bytes=b"{}"),
            "candidate_path": replace(
                bundle, candidate_path_artifact_bytes={path_id: b"{}"}
            ),
            "preflight": replace(bundle, preflight_receipt_bytes=b"{}"),
            "descriptor": replace(bundle, engine_input_descriptor_bytes=b"{}"),
            "five_seed": replace(bundle, five_seed_artifact_bytes=b"{}"),
            "runtime": replace(bundle, engine_envelope_bytes=runtime_raw),
        }
        for name, forged_bundle in cases.items():
            with self.subTest(name=name):
                forged_raw = forged_bundle.engine_envelope_bytes
                forged_store = MetricArtifactBytes(
                    ROOT,
                    store.system_manifest_bundle,
                    {sha256(forged_raw).hexdigest(): forged_bundle},
                )
                with self.assertRaises(EvaluationError):
                    _make_engine_envelope_inspector(forged_store)(forged_raw)

    def test_default_inspector_rejects_rehashed_forged_semantic_chain(self) -> None:
        from fisher_engine.semantic import (
            OfflineRegistryResolver,
            build_e0_feature_tensor,
            build_pair_packet,
            build_semantic_feature_plan,
        )

        envelope_raw, bundle, store, _manifest, _vmp_hash = self.build_fixture()
        text = "A D"
        envelope = strict_json_loads(envelope_raw, prefix="test_envelope")
        forged_audit = deepcopy(
            strict_json_loads(
                bundle.prediction_audit_bytes, prefix="test_prediction_audit"
            )
        )
        candidates = forged_audit["path_predictions"][0]["endpoint_candidates"]
        candidates[0]["lookup_surface"] = "FORGED_ACTOR"
        candidates[1]["lookup_surface"] = "FORGED_DESTINATION"
        forged_audit_raw = canonical_json_bytes(forged_audit)
        forged_audit_hash = sha256(forged_audit_raw).hexdigest()

        resolver = OfflineRegistryResolver(
            "registry_synthetic_e0",
            "resolver_0.0.0-synthetic",
            {
                ("FORGED_ACTOR", "DOMAIN", "FORGED_DESTINATION"): {
                    "state": "MISMATCH",
                    "registry_coverage": "COMPLETE",
                    "evidence_ids": ["registry_evidence_forged"],
                }
            },
        )
        prediction = forged_audit["path_predictions"][0]
        forged_packet, forged_packet_hash = build_pair_packet(
            vmp_sha256=envelope["vmp"]["vmp_sha256"],
            vmp_length=len(text),
            path_prediction=prediction,
            resolver=resolver,
        )
        forged_plan, forged_plan_hash = build_semantic_feature_plan(forged_packet)
        forged_tensor, forged_tensor_hash = build_e0_feature_tensor(
            vmp_text=text,
            vmp_sha256=envelope["vmp"]["vmp_sha256"],
            path_sha256=prediction["path_sha256"],
            semantic_feature_plan=forged_plan,
            semantic_feature_plan_sha256=forged_plan_hash,
        )
        envelope["prediction_audit_sha256"] = forged_audit_hash
        envelope["sep_packet_hashes"][0]["sha256"] = forged_packet_hash
        envelope["feature_tensor_hashes"][0]["sha256"] = forged_tensor_hash
        forged_envelope_raw = canonical_json_bytes(envelope)
        path_id = prediction["path_id"]
        forged_bundle = replace(
            bundle,
            engine_envelope_bytes=forged_envelope_raw,
            prediction_audit_bytes=forged_audit_raw,
            pair_packet_bytes_by_path={path_id: canonical_json_bytes(forged_packet)},
            semantic_feature_plan_bytes_by_path={
                path_id: canonical_json_bytes(forged_plan)
            },
            feature_tensor_bytes_by_path={path_id: canonical_json_bytes(forged_tensor)},
        )
        forged_store = MetricArtifactBytes(
            ROOT,
            store.system_manifest_bundle,
            {sha256(forged_envelope_raw).hexdigest(): forged_bundle},
        )
        with self.assertRaises(EvaluationBindingError):
            _make_engine_envelope_inspector(forged_store)(forged_envelope_raw)

    def test_public_boundary_uses_authoritative_artifacts(self) -> None:
        envelope_raw, _bundle, store, manifest, vmp_hash = self.build_fixture()
        registry_hash = manifest["registry_binding"]["registry_artifact_sha256"]
        references_hash = sha256(b"evaluation-registry-references").hexdigest()
        registry_bundle = {
            "schema_version": "1.0.0",
            "registry_snapshot_id": "registry_synthetic_e0",
            "resolver_version": "resolver_0.0.0-synthetic",
            "registry_manifest_sha256": registry_hash,
            "registry_references_sha256": references_hash,
        }
        inventory = nonempty_gold(
            "item_inspector", vmp_hash, "annotation_inspector"
        )
        inventory["registry_references"][0].update(
            {
                "registry_reference_id": "registry_reference_inspector",
                "registry_snapshot_id": "registry_synthetic_e0",
                "resolver_version": "resolver_0.0.0-synthetic",
            }
        )
        gold = gold_inventory_artifact(inventory, vmp_text="A D")
        entry = {
            "item_id": "item_inspector",
            "partition": "development",
            "vmp_sha256": vmp_hash,
            "final_annotation_id": "annotation_inspector",
            "gold_inventory_size_bytes": len(gold.data),
            "gold_inventory_sha256": gold.sha256,
            "gold_pair_count": 1,
            "gold_empty": False,
        }
        hashes = {
            "items_jsonl_sha256": sha256(b"evaluation-items").hexdigest(),
            "annotations_jsonl_sha256": sha256(b"evaluation-annotations").hexdigest(),
            "registry_manifest_jsonl_sha256": registry_hash,
            "registry_references_jsonl_sha256": references_hash,
        }
        universe_value = {
            "schema_version": "1.0.0",
            "universe_id": "evaluation_universe_inspector",
            "partition": "development",
            "dataset_artifact_hashes": hashes,
            "registry_reference_bundle_sha256": sha256(
                canonical_json_bytes(registry_bundle)
            ).hexdigest(),
            "entries": [entry],
        }
        universe_raw = canonical_json_bytes(universe_value)
        envelope_hash = sha256(envelope_raw).hexdigest()
        submission_raw = canonical_json_bytes(
            {
                "schema_version": "1.0.0",
                "evaluation_universe_sha256": sha256(universe_raw).hexdigest(),
                "system_artifact_manifest_sha256": sha256(
                    store.system_manifest_bundle[manifest["system_id"]]
                ).hexdigest(),
                "entries": [
                    {"item_id": "item_inspector", "envelope_sha256": envelope_hash}
                ],
            }
        )
        semantic_context = UniverseSemanticContext(
            expected_entries=(entry,),
            dataset_artifact_hashes=hashes,
            registry_reference_bundle=registry_bundle,
            gold_inventory_bytes={gold.sha256: gold.data},
            vmp_text_by_item_id={"item_inspector": "A D"},
        )
        result = evaluate_boundary(
            universe_raw,
            submission_raw,
            universe_receipt_id="metric_universe_input_inspector",
            input_receipt_id="metric_input_inspector",
            metric_run_id="metric_run_inspector",
            condition="C01",
            system_id=manifest["system_id"],
            system_variant="BASE",
            semantic_context=semantic_context,
            metric_artifacts=store,
            declared_n_all=1,
            declared_n_gold_empty=0,
            declared_n_gold_nonempty=1,
        )
        self.assertEqual(result.metric_run.manifest["status"], "VALID")
        self.assertEqual(result.metric_run.pair_metrics["rank1"]["F1_pair"], 1.0)


if __name__ == "__main__":
    unittest.main()
