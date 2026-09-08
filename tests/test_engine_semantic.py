from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import unittest

from fisher_engine._canonical import canonical_json_bytes, canonical_sha256
from fisher_engine._numeric import f64_bits_to_float, float_to_f64_bits
from fisher_engine.candidate import InternalCandidatePath
from fisher_engine.semantic import (
    FEATURE_TENSOR_MAX_BYTES,
    PAIR_PACKET_MAX_BYTES,
    OfflineRegistryResolver,
    SemanticValidationError,
    build_e0_feature_tensor,
    build_pair_packet,
    build_prediction_audit,
    build_synthetic_registry_artifact,
    build_semantic_artifacts,
    build_semantic_feature_plan,
    e0_vmp_category_grid,
    frozen_registry_from_artifact,
    marginalized_pair_prevalence,
    packet_state_prevalence,
    parse_e0_feature_tensor,
    parse_e0_feature_tensor_structural,
    parse_pair_packet,
    parse_pair_packet_structural,
    parse_prediction_audit,
    parse_prediction_audit_structural,
    parse_synthetic_registry_artifact,
    render_lookup_surface,
    replay_semantic_chain,
    validate_e0_feature_tensor,
    validate_pair_packet,
    validate_prediction_audit,
    validate_synthetic_registry_artifact,
)


VMP_HASH = sha256(b"synthetic-vmp").hexdigest()


def identity_path(text: str, *, q: float = 1.0, path_id: str = "candidate_path_01") -> InternalCandidatePath:
    alignment = tuple((index, index + 1) for index in range(len(text)))
    path_hash = canonical_sha256(
        {"text": text, "alignment": [list(value) for value in alignment]}
    )
    return InternalCandidatePath(
        path_id=path_id,
        path_sha256=path_hash,
        text=text,
        alignment=alignment,
        lineage={
            "lineage_version": "1.0.0",
            "contributors": [{"mode": "IDENTITY_BYPASS"}],
        },
        composition_score=0.0,
        q_numerator=1.0,
        q=q,
        effective_rewrite_spans=(),
    )


def rewritten_path(
    vmp_text: str,
    *,
    source_start: int,
    source_end: int,
    replacement: str,
) -> InternalCandidatePath:
    path_text = vmp_text[:source_start] + replacement + vmp_text[source_end:]
    alignment = (
        tuple((index, index + 1) for index in range(source_start))
        + tuple((source_start, source_end) for _ in replacement)
        + tuple((index, index + 1) for index in range(source_end, len(vmp_text)))
    )
    path_hash = canonical_sha256(
        {"text": path_text, "alignment": [list(value) for value in alignment]}
    )
    return InternalCandidatePath(
        path_id="candidate_path_01",
        path_sha256=path_hash,
        text=path_text,
        alignment=alignment,
        lineage={
            "lineage_version": "1.0.0",
            "contributors": [{"mode": "COMPOSED_SPAN", "units": []}],
        },
        composition_score=0.0,
        q_numerator=1.0,
        q=1.0,
        effective_rewrite_spans=(
            {
                "span_index": 0,
                "start": source_start,
                "end": source_end,
                "source_text": vmp_text[source_start:source_end],
            },
        ),
    )


def candidate(
    role: str,
    start: int,
    end: int,
    *,
    kind: str = "NONE",
    score: float = 1.0,
) -> dict:
    return {
        "role": role,
        "start": start,
        "end": end,
        "kind": kind,
        "score_f64_bits": float_to_f64_bits(score),
    }


def resolver(records: dict | None = None) -> OfflineRegistryResolver:
    return OfflineRegistryResolver(
        "registry_synthetic_e0",
        "resolver_1.0.0",
        records or {},
    )


def basic_artifacts(*, actor_score: float = 1.0, destination_score: float = 1.0):
    text = "SBI [DOMAIN]"
    path = identity_path(text)
    emitted = {
        path.path_id: [
            candidate("ACTOR", 0, 3, score=actor_score),
            candidate("DESTINATION", 4, 12, kind="DOMAIN", score=destination_score),
        ]
    }
    fixture = resolver(
        {
            ("SBI", "DOMAIN", "[DOMAIN]"): {
                "state": "MATCH",
                "registry_coverage": "COMPLETE",
                "evidence_ids": ["registry_evidence_sbi_domain"],
            }
        }
    )
    return text, path, emitted, fixture, build_semantic_artifacts(
        vmp_text=text,
        vmp_sha256=VMP_HASH,
        active_paths=[path],
        emitted_candidates_by_path=emitted,
        registry_resolver=fixture,
    )


class PredictionAuditTests(unittest.TestCase):
    def test_dedup_highest_score_equal_tie_lowest_index_and_score_independent_cap_order(self) -> None:
        text = "ABCDEFGHIJK [DOMAIN]"
        path = identity_path(text)
        rows = [
            candidate("ACTOR", 0, 1, score=1.0),
            candidate("ACTOR", 0, 1, score=1.0),
            candidate("ACTOR", 0, 1, score=30.0),
        ]
        rows.extend(
            candidate("ACTOR", index, index + 1, score=float(20 - index))
            for index in range(1, 10)
        )
        rows.append(candidate("DESTINATION", 12, 20, kind="DOMAIN", score=0.5))
        audit, digest = build_prediction_audit(
            vmp_text=text,
            vmp_sha256=VMP_HASH,
            active_paths=[path],
            emitted_candidates_by_path={path.path_id: rows},
        )
        prediction = audit["path_predictions"][0]
        self.assertEqual(prediction["actor_pre_cap_count"], 10)
        self.assertTrue(prediction["actor_cap_hit"])
        self.assertIn(2, prediction["selected_actor_candidate_indices"])
        self.assertNotIn(0, prediction["selected_actor_candidate_indices"])
        self.assertNotIn(1, prediction["selected_actor_candidate_indices"])
        selected_starts = [
            prediction["endpoint_candidates"][index]["start"]
            for index in prediction["selected_actor_candidate_indices"]
        ]
        self.assertEqual(selected_starts, sorted(selected_starts))
        self.assertEqual(digest, canonical_sha256(audit, max_bytes=4 * 1024 * 1024))

    def test_equal_score_duplicate_keeps_first_emission(self) -> None:
        text = "AB"
        path = identity_path(text)
        audit, _ = build_prediction_audit(
            vmp_text=text,
            vmp_sha256=VMP_HASH,
            active_paths=[path],
            emitted_candidates_by_path={
                path.path_id: [
                    candidate("ACTOR", 0, 1),
                    candidate("ACTOR", 0, 1),
                ]
            },
        )
        self.assertEqual(
            audit["path_predictions"][0]["selected_actor_candidate_indices"], [0]
        )

    def test_binary64_scores_that_would_tie_in_binary32_remain_distinct(self) -> None:
        text = "A"
        path = identity_path(text)
        audit, _ = build_prediction_audit(
            vmp_text=text,
            vmp_sha256=VMP_HASH,
            active_paths=[path],
            emitted_candidates_by_path={
                path.path_id: [
                    candidate("ACTOR", 0, 1, score=1.00000003),
                    candidate("ACTOR", 0, 1, score=1.00000004),
                ]
            },
        )
        self.assertEqual(
            audit["path_predictions"][0]["selected_actor_candidate_indices"], [1]
        )

    def test_per_role_256_candidate_bound_is_fail_closed(self) -> None:
        text = "A" * 257
        path = identity_path(text)
        rows = [candidate("ACTOR", index, index + 1) for index in range(257)]
        with self.assertRaisesRegex(SemanticValidationError, "semantic_prediction_bound"):
            build_prediction_audit(
                vmp_text=text,
                vmp_sha256=VMP_HASH,
                active_paths=[path],
                emitted_candidates_by_path={path.path_id: rows},
            )

    def test_boolean_coordinate_and_negative_zero_are_rejected(self) -> None:
        text = "AB"
        path = identity_path(text)
        boolean_row = candidate("ACTOR", 0, 1)
        boolean_row["start"] = False
        with self.assertRaises(SemanticValidationError):
            build_prediction_audit(
                vmp_text=text,
                vmp_sha256=VMP_HASH,
                active_paths=[path],
                emitted_candidates_by_path={path.path_id: [boolean_row]},
            )
        negative_zero = candidate("ACTOR", 0, 1)
        negative_zero["score_f64_bits"] = "8000000000000000"
        with self.assertRaisesRegex(SemanticValidationError, "semantic_prediction_nonfinite"):
            build_prediction_audit(
                vmp_text=text,
                vmp_sha256=VMP_HASH,
                active_paths=[path],
                emitted_candidates_by_path={path.path_id: [negative_zero]},
            )

    def test_strict_parser_rejects_noncanonical_and_extra_fields(self) -> None:
        text, _, _, _, artifacts = basic_artifacts()
        audit = artifacts["prediction_audit"]
        raw = canonical_json_bytes(audit)
        self.assertEqual(parse_prediction_audit(raw, vmp_text=text), audit)
        with self.assertRaises(SemanticValidationError):
            parse_prediction_audit(raw + b"\n", vmp_text=text)
        extra = deepcopy(audit)
        extra["extra"] = None
        with self.assertRaises(SemanticValidationError):
            validate_prediction_audit(extra, vmp_text=text)


class AlignmentAndPacketTests(unittest.TestCase):
    def test_full_span_substitution_and_cut_through_guard(self) -> None:
        vmp = "Pay bankname via [DOMAIN]"
        path = rewritten_path(vmp, source_start=4, source_end=12, replacement="benkname")
        full = render_lookup_surface(
            vmp_text=vmp,
            path_text=path.text,
            path_alignment=path.alignment,
            effective_rewrite_spans=path.effective_rewrite_spans,
            start=4,
            end=12,
        )
        cut = render_lookup_surface(
            vmp_text=vmp,
            path_text=path.text,
            path_alignment=path.alignment,
            effective_rewrite_spans=path.effective_rewrite_spans,
            start=4,
            end=8,
        )
        self.assertEqual(full, ("benkname", "ALIGNED"))
        self.assertEqual(cut, ("", "UNALIGNED"))

    def test_mixed_aligned_and_unaligned_pairs_make_only_aligned_calls(self) -> None:
        vmp = "Pay bankname via [DOMAIN]"
        path = rewritten_path(vmp, source_start=4, source_end=12, replacement="benkname")
        destination_start = vmp.index("[DOMAIN]")
        emitted = {
            path.path_id: [
                candidate("ACTOR", 4, 12, score=2.0),
                candidate("ACTOR", 4, 8, score=1.0),
                candidate(
                    "DESTINATION",
                    destination_start,
                    destination_start + 8,
                    kind="DOMAIN",
                ),
            ]
        }
        fixture = resolver(
            {
                ("benkname", "DOMAIN", "[DOMAIN]"): {
                    "state": "MISMATCH",
                    "registry_coverage": "COMPLETE",
                    "evidence_ids": ["registry_evidence_benkname"],
                }
            }
        )
        artifacts = build_semantic_artifacts(
            vmp_text=vmp,
            vmp_sha256=VMP_HASH,
            active_paths=[path],
            emitted_candidates_by_path=emitted,
            registry_resolver=fixture,
        )
        packet = artifacts["paths"][0]["pair_packet"]
        self.assertEqual(len(packet["pairs"]), 2)
        self.assertEqual(packet["registry_call_count"], 1)
        states = {
            pair["resolution"]["resolution_source"]: pair["resolution"]["state"]
            for pair in packet["pairs"]
        }
        self.assertEqual(states, {"ALIGNMENT_GUARD": "UNKNOWN", "REGISTRY": "MISMATCH"})
        guarded = next(
            pair for pair in packet["pairs"]
            if pair["resolution"]["resolution_source"] == "ALIGNMENT_GUARD"
        )
        self.assertEqual(
            guarded["resolution"],
            {
                "state": "UNKNOWN",
                "registry_coverage": "NOT_EVALUATED",
                "resolution_source": "ALIGNMENT_GUARD",
                "evidence_ids": [],
            },
        )

    def test_empty_endpoint_product_makes_zero_calls_and_na_prevalence(self) -> None:
        text = "SBI only"
        path = identity_path(text)
        audit, _ = build_prediction_audit(
            vmp_text=text,
            vmp_sha256=VMP_HASH,
            active_paths=[path],
            emitted_candidates_by_path={
                path.path_id: [candidate("ACTOR", 0, 3)]
            },
        )
        packet, _ = build_pair_packet(
            vmp_sha256=VMP_HASH,
            vmp_length=len(text),
            path_prediction=audit["path_predictions"][0],
            resolver=resolver(),
        )
        self.assertEqual(packet["pairs"], [])
        self.assertTrue(packet["no_explicit_pair"])
        self.assertEqual(packet["registry_call_count"], 0)
        self.assertEqual(
            packet_state_prevalence(packet),
            {"MATCH": 0.0, "MISMATCH": 0.0, "UNKNOWN": 0.0, "N/A": 1.0},
        )

    def test_packet_equals_exact_selected_audit_cartesian_product(self) -> None:
        text, _, _, _, artifacts = basic_artifacts()
        packet = artifacts["paths"][0]["pair_packet"]
        prediction = artifacts["prediction_audit"]["path_predictions"][0]
        self.assertEqual(
            validate_pair_packet(
                packet,
                vmp_length=len(text),
                expected_path_prediction=prediction,
            ),
            artifacts["paths"][0]["pair_packet_sha256"],
        )
        changed = deepcopy(packet)
        changed["pairs"][0]["actor"]["start"] = 1
        with self.assertRaises(SemanticValidationError):
            validate_pair_packet(
                changed,
                vmp_length=len(text),
                expected_path_prediction=prediction,
            )

    def test_64_pair_and_16_evidence_bounds(self) -> None:
        actors = "ABCDEFGH"
        destinations = "ijklmnop"
        text = actors + destinations
        path = identity_path(text)
        rows = [candidate("ACTOR", index, index + 1, score=20 - index) for index in range(8)]
        rows += [
            candidate("DESTINATION", 8 + index, 9 + index, kind="OTHER", score=20 - index)
            for index in range(8)
        ]
        evidence = [f"registry_evidence_bound_{index:02d}" for index in range(16)]
        records = {
            (actor, "OTHER", destination): {
                "state": "MATCH",
                "registry_coverage": "COMPLETE",
                "evidence_ids": evidence,
            }
            for actor in actors
            for destination in destinations
        }
        audit, _ = build_prediction_audit(
            vmp_text=text,
            vmp_sha256=VMP_HASH,
            active_paths=[path],
            emitted_candidates_by_path={path.path_id: rows},
        )
        packet, _ = build_pair_packet(
            vmp_sha256=VMP_HASH,
            vmp_length=len(text),
            path_prediction=audit["path_predictions"][0],
            resolver=resolver(records),
        )
        self.assertEqual(len(packet["pairs"]), 64)
        self.assertEqual(packet["registry_call_count"], 64)
        self.assertTrue(all(len(pair["resolution"]["evidence_ids"]) == 16 for pair in packet["pairs"]))
        self.assertLessEqual(len(canonical_json_bytes(packet)), PAIR_PACKET_MAX_BYTES)
        invalid = {
            ("A", "OTHER", "i"): {
                "state": "MATCH",
                "registry_coverage": "COMPLETE",
                "evidence_ids": evidence + ["registry_evidence_bound_16"],
            }
        }
        with self.assertRaises(SemanticValidationError):
            resolver(invalid)

    def test_packet_parser_rejects_reordered_cartesian_rows(self) -> None:
        text = "AB [DOMAIN]"
        path = identity_path(text)
        audit, _ = build_prediction_audit(
            vmp_text=text,
            vmp_sha256=VMP_HASH,
            active_paths=[path],
            emitted_candidates_by_path={
                path.path_id: [
                    candidate("ACTOR", 0, 1),
                    candidate("ACTOR", 1, 2),
                    candidate("DESTINATION", 3, 11, kind="DOMAIN"),
                ]
            },
        )
        packet, _ = build_pair_packet(
            vmp_sha256=VMP_HASH,
            vmp_length=len(text),
            path_prediction=audit["path_predictions"][0],
            resolver=resolver(),
        )
        self.assertEqual(parse_pair_packet(canonical_json_bytes(packet)), packet)
        reordered = deepcopy(packet)
        reordered["pairs"].reverse()
        with self.assertRaises(SemanticValidationError):
            parse_pair_packet(canonical_json_bytes(reordered))
        with self.assertRaises(SemanticValidationError):
            parse_pair_packet(canonical_json_bytes(packet) + b" ")


class FeatureTensorTests(unittest.TestCase):
    def test_five_unicode_categories_and_exact_bits(self) -> None:
        text = "Aा१ 😀"
        grid = e0_vmp_category_grid(text)
        self.assertEqual(
            grid,
            (
                (1.0, 0.0, 0.0, 0.0, 0.0),
                (0.0, 1.0, 0.0, 0.0, 0.0),
                (0.0, 0.0, 1.0, 0.0, 0.0),
                (0.0, 0.0, 0.0, 1.0, 0.0),
                (0.0, 0.0, 0.0, 0.0, 1.0),
            ),
        )
        path = identity_path(text)
        audit, _ = build_prediction_audit(
            vmp_text=text,
            vmp_sha256=VMP_HASH,
            active_paths=[path],
            emitted_candidates_by_path={
                path.path_id: [
                    candidate("ACTOR", 0, 2),
                    candidate("DESTINATION", 2, 5, kind="OTHER"),
                ]
            },
        )
        packet, _ = build_pair_packet(
            vmp_sha256=VMP_HASH,
            vmp_length=len(text),
            path_prediction=audit["path_predictions"][0],
            resolver=resolver(),
        )
        plan, plan_hash = build_semantic_feature_plan(packet)
        tensor, tensor_hash = build_e0_feature_tensor(
            vmp_text=text,
            vmp_sha256=VMP_HASH,
            path_sha256=path.path_sha256,
            semantic_feature_plan=plan,
            semantic_feature_plan_sha256=plan_hash,
        )
        self.assertEqual(tensor["pair_mask"], [True] + [False] * 63)
        self.assertEqual(len(tensor["vmp_hidden_grid_f64_bits"]), 80 * len(text))
        self.assertEqual(len(tensor["pair_rows_f64_bits"]), 16 * 64 * 31)
        first_row = [
            f64_bits_to_float(tensor["pair_rows_f64_bits"][offset : offset + 16])
            for offset in range(0, 16 * 31, 16)
        ]
        self.assertEqual(first_row[:5], [0.5, 0.5, 0.0, 0.0, 0.0])
        self.assertEqual(first_row[5:10], [0.0, 0.0, 1 / 3, 1 / 3, 1 / 3])
        padding = tensor["pair_rows_f64_bits"][16 * 31 :]
        self.assertEqual(set(padding), {"0"})
        self.assertEqual(
            validate_e0_feature_tensor(tensor, vmp_text=text, semantic_feature_plan=plan),
            tensor_hash,
        )
        self.assertLessEqual(len(canonical_json_bytes(tensor)), FEATURE_TENSOR_MAX_BYTES)
        self.assertEqual(
            parse_e0_feature_tensor(
                canonical_json_bytes(tensor),
                vmp_text=text,
                semantic_feature_plan=plan,
            ),
            tensor,
        )

    def test_empty_product_has_all_false_mask_and_positive_zero_padding(self) -> None:
        text = "SBI"
        path = identity_path(text)
        audit, _ = build_prediction_audit(
            vmp_text=text,
            vmp_sha256=VMP_HASH,
            active_paths=[path],
            emitted_candidates_by_path={path.path_id: [candidate("ACTOR", 0, 3)]},
        )
        packet, _ = build_pair_packet(
            vmp_sha256=VMP_HASH,
            vmp_length=len(text),
            path_prediction=audit["path_predictions"][0],
            resolver=resolver(),
        )
        plan, plan_hash = build_semantic_feature_plan(packet)
        tensor, _ = build_e0_feature_tensor(
            vmp_text=text,
            vmp_sha256=VMP_HASH,
            path_sha256=path.path_sha256,
            semantic_feature_plan=plan,
            semantic_feature_plan_sha256=plan_hash,
        )
        self.assertTrue(tensor["no_explicit_pair"])
        self.assertEqual(tensor["pair_mask"], [False] * 64)
        self.assertEqual(set(tensor["pair_rows_f64_bits"]), {"0"})

    def test_audit_only_score_surface_evidence_ids_q_ranks_hashes_do_not_change_rows(self) -> None:
        text, path, _, _, first = basic_artifacts(actor_score=1.0, destination_score=2.0)
        _, _, _, _, second = basic_artifacts(actor_score=99.0, destination_score=-3.0)
        first_packet = deepcopy(first["paths"][0]["pair_packet"])
        second_packet = deepcopy(second["paths"][0]["pair_packet"])
        second_packet["pairs"][0]["actor"]["lookup_surface"] = "BANK-ALIAS"
        second_packet["pairs"][0]["destination"]["lookup_surface"] = "domain-alias"
        second_packet["pairs"][0]["resolution"]["evidence_ids"] = [
            "registry_evidence_changed"
        ]
        second_packet["registry_snapshot_id"] = "registry_changed_e0"
        second_packet["resolver_version"] = "resolver_9.9.9"
        first_plan, first_plan_hash = build_semantic_feature_plan(first_packet)
        second_plan, second_plan_hash = build_semantic_feature_plan(second_packet)
        self.assertEqual(first_plan, second_plan)
        self.assertEqual(first_plan_hash, second_plan_hash)
        first_tensor, _ = build_e0_feature_tensor(
            vmp_text=text,
            vmp_sha256=VMP_HASH,
            path_sha256=path.path_sha256,
            semantic_feature_plan=first_plan,
        )
        second_tensor, _ = build_e0_feature_tensor(
            vmp_text=text,
            vmp_sha256="f" * 64,
            path_sha256="e" * 64,
            semantic_feature_plan=second_plan,
        )
        self.assertEqual(
            first_tensor["pair_rows_f64_bits"], second_tensor["pair_rows_f64_bits"]
        )
        self.assertNotEqual(first_tensor["vmp_sha256"], second_tensor["vmp_sha256"])
        plan_text = canonical_json_bytes(first_plan).decode("utf-8")
        for prohibited in ("score", "candidate_path", "provider_rank", "q_f64_bits"):
            self.assertNotIn(prohibited, plan_text)

    def test_tensor_validation_rejects_changed_mask_and_negative_zero(self) -> None:
        text, _, _, _, artifacts = basic_artifacts()
        plan = artifacts["paths"][0]["semantic_feature_plan"]
        tensor = deepcopy(artifacts["paths"][0]["semantic_feature_tensor"])
        tensor["pair_mask"][1] = True
        with self.assertRaises(SemanticValidationError):
            validate_e0_feature_tensor(tensor, vmp_text=text, semantic_feature_plan=plan)
        tensor = deepcopy(artifacts["paths"][0]["semantic_feature_tensor"])
        tensor["pair_rows_f64_bits"] = "8000000000000000" + tensor["pair_rows_f64_bits"][16:]
        with self.assertRaises(SemanticValidationError):
            validate_e0_feature_tensor(tensor, vmp_text=text, semantic_feature_plan=plan)


class DiagnosticsTests(unittest.TestCase):
    def test_pair_prevalence_and_q_marginalization(self) -> None:
        _, _, _, _, match_artifacts = basic_artifacts()
        match_packet = match_artifacts["paths"][0]["pair_packet"]
        empty = deepcopy(match_packet)
        empty["pairs"] = []
        empty["no_explicit_pair"] = True
        empty["registry_call_count"] = 0
        result = marginalized_pair_prevalence(
            [
                (float_to_f64_bits(0.25), match_packet),
                (float_to_f64_bits(0.75), empty),
            ]
        )
        self.assertEqual(
            result,
            {"MATCH": 0.25, "MISMATCH": 0.0, "UNKNOWN": 0.0, "N/A": 0.75},
        )


class RegistryTrustBoundaryTests(unittest.TestCase):
    def test_registry_artifact_is_canonical_sorted_hashed_and_reconstructible(self) -> None:
        records = {
            ("Zed", "URL", "z.example"): {
                "state": "UNKNOWN",
                "registry_coverage": "PARTIAL",
                "evidence_ids": ["registry_evidence_zed"],
            },
            ("SBI", "DOMAIN", "[DOMAIN]"): {
                "state": "MATCH",
                "registry_coverage": "COMPLETE",
                "evidence_ids": ["registry_evidence_sbi_domain"],
            },
        }
        artifact, raw, digest = build_synthetic_registry_artifact(
            registry_snapshot_id="registry_synthetic_truth",
            resolver_version="resolver_1.0.0",
            records=records,
        )
        self.assertEqual(parse_synthetic_registry_artifact(raw), artifact)
        self.assertEqual(validate_synthetic_registry_artifact(artifact), digest)
        self.assertEqual(
            [entry["actor_lookup_surface"] for entry in artifact["entries"]],
            ["SBI", "Zed"],
        )
        frozen = frozen_registry_from_artifact(raw, expected_sha256=digest)
        result = frozen.resolve(
            {
                "role": "ACTOR", "start": 0, "end": 3, "kind": "NONE",
                "lookup_surface": "SBI", "lookup_status": "ALIGNED",
            },
            {
                "role": "DESTINATION", "start": 4, "end": 12,
                "kind": "DOMAIN", "lookup_surface": "[DOMAIN]",
                "lookup_status": "ALIGNED",
            },
        )
        self.assertEqual(result["state"], "MATCH")
        self.assertEqual(frozen.artifact_sha256, digest)
        with self.assertRaises(SemanticValidationError):
            frozen_registry_from_artifact(raw, expected_sha256="f" * 64)

    def test_registry_parser_rejects_unsorted_duplicate_and_deep_artifacts(self) -> None:
        artifact, _, _ = build_synthetic_registry_artifact(
            registry_snapshot_id="registry_synthetic_truth",
            resolver_version="resolver_1.0.0",
            records={
                ("A", "DOMAIN", "a.example"): {
                    "state": "MATCH",
                    "registry_coverage": "COMPLETE",
                    "evidence_ids": ["registry_evidence_a"],
                },
                ("B", "DOMAIN", "b.example"): {
                    "state": "MATCH",
                    "registry_coverage": "COMPLETE",
                    "evidence_ids": ["registry_evidence_b"],
                },
            },
        )
        unsorted = deepcopy(artifact)
        unsorted["entries"].reverse()
        with self.assertRaises(SemanticValidationError):
            validate_synthetic_registry_artifact(unsorted)
        duplicate = deepcopy(artifact)
        duplicate["entries"][1] = deepcopy(duplicate["entries"][0])
        with self.assertRaises(SemanticValidationError):
            validate_synthetic_registry_artifact(duplicate)
        over_count = deepcopy(artifact)
        over_count["entries"] = [deepcopy(artifact["entries"][0])] * 4_097
        with self.assertRaises(SemanticValidationError):
            validate_synthetic_registry_artifact(over_count)
        deep = b"[" * 80 + b"]" * 80
        with self.assertRaises(SemanticValidationError):
            parse_synthetic_registry_artifact(deep)

    def test_complete_replay_rejects_forged_lookup_surface(self) -> None:
        text, path, _, _, artifacts = basic_artifacts()
        audit = deepcopy(artifacts["prediction_audit"])
        audit["path_predictions"][0]["endpoint_candidates"][0][
            "lookup_surface"
        ] = "FORGED"
        packet = deepcopy(artifacts["paths"][0]["pair_packet"])
        packet["pairs"][0]["actor"]["lookup_surface"] = "FORGED"
        plan, plan_hash = build_semantic_feature_plan(packet)
        tensor, _ = build_e0_feature_tensor(
            vmp_text=text,
            vmp_sha256=VMP_HASH,
            path_sha256=path.path_sha256,
            semantic_feature_plan=plan,
            semantic_feature_plan_sha256=plan_hash,
        )
        _, registry_raw, _ = build_synthetic_registry_artifact(
            registry_snapshot_id="registry_synthetic_e0",
            resolver_version="resolver_1.0.0",
            records={
                ("FORGED", "DOMAIN", "[DOMAIN]"): {
                    "state": "MATCH",
                    "registry_coverage": "COMPLETE",
                    "evidence_ids": ["registry_evidence_sbi_domain"],
                }
            },
        )
        self.assertEqual(
            parse_prediction_audit_structural(
                canonical_json_bytes(audit), vmp_text=text
            ),
            audit,
        )
        with self.assertRaisesRegex(SemanticValidationError, "semantic_invalid_lookup_render"):
            replay_semantic_chain(
                vmp_text=text,
                vmp_sha256=VMP_HASH,
                active_paths=[path],
                prediction_audit_bytes=canonical_json_bytes(audit),
                registry_artifact_bytes=registry_raw,
                pair_packet_bytes_by_path={path.path_id: canonical_json_bytes(packet)},
                semantic_feature_plan_bytes_by_path={path.path_id: canonical_json_bytes(plan)},
                feature_tensor_bytes_by_path={path.path_id: canonical_json_bytes(tensor)},
            )

    def test_complete_replay_rejects_forged_path_alignment(self) -> None:
        text, path, _, fixture, artifacts = basic_artifacts()
        forged_alignment = ((0, 2),) + path.alignment[1:]
        forged_hash = canonical_sha256(
            {
                "text": text,
                "alignment": [list(value) for value in forged_alignment],
            }
        )
        forged_path = InternalCandidatePath(
            path_id=path.path_id,
            path_sha256=forged_hash,
            text=text,
            alignment=forged_alignment,
            lineage=path.lineage,
            composition_score=path.composition_score,
            q_numerator=path.q_numerator,
            q=path.q,
            effective_rewrite_spans=path.effective_rewrite_spans,
        )
        audit = deepcopy(artifacts["prediction_audit"])
        audit["path_predictions"][0]["path_sha256"] = forged_hash
        packet = deepcopy(artifacts["paths"][0]["pair_packet"])
        packet["path_sha256"] = forged_hash
        plan = artifacts["paths"][0]["semantic_feature_plan"]
        tensor = deepcopy(artifacts["paths"][0]["semantic_feature_tensor"])
        tensor["path_sha256"] = forged_hash
        _, registry_raw, _ = build_synthetic_registry_artifact(
            registry_snapshot_id=fixture.registry_snapshot_id,
            resolver_version=fixture.resolver_version,
            records={
                ("SBI", "DOMAIN", "[DOMAIN]"): {
                    "state": "MATCH",
                    "registry_coverage": "COMPLETE",
                    "evidence_ids": ["registry_evidence_sbi_domain"],
                }
            },
        )
        self.assertEqual(
            parse_pair_packet_structural(canonical_json_bytes(packet)), packet
        )
        with self.assertRaisesRegex(SemanticValidationError, "semantic_invalid_alignment"):
            replay_semantic_chain(
                vmp_text=text,
                vmp_sha256=VMP_HASH,
                active_paths=[forged_path],
                prediction_audit_bytes=canonical_json_bytes(audit),
                registry_artifact_bytes=registry_raw,
                pair_packet_bytes_by_path={path.path_id: canonical_json_bytes(packet)},
                semantic_feature_plan_bytes_by_path={path.path_id: canonical_json_bytes(plan)},
                feature_tensor_bytes_by_path={path.path_id: canonical_json_bytes(tensor)},
            )

    def test_complete_replay_rejects_structurally_valid_forged_registry_result(self) -> None:
        vmp = "SBI [DOMAIN]"
        path = rewritten_path(vmp, source_start=0, source_end=3, replacement="FORGED")
        audit, _ = build_prediction_audit(
            vmp_text=vmp,
            vmp_sha256=VMP_HASH,
            active_paths=[path],
            emitted_candidates_by_path={
                path.path_id: [
                    candidate("ACTOR", 0, 3),
                    candidate("DESTINATION", 4, 12, kind="DOMAIN"),
                ]
            },
        )
        forged_resolver = resolver(
            {
                ("FORGED", "DOMAIN", "[DOMAIN]"): {
                    "state": "MISMATCH",
                    "registry_coverage": "COMPLETE",
                    "evidence_ids": ["registry_evidence_forged"],
                }
            }
        )
        forged_packet, _ = build_pair_packet(
            vmp_sha256=VMP_HASH,
            vmp_length=len(vmp),
            path_prediction=audit["path_predictions"][0],
            resolver=forged_resolver,
        )
        forged_plan, forged_plan_hash = build_semantic_feature_plan(forged_packet)
        forged_tensor, _ = build_e0_feature_tensor(
            vmp_text=vmp,
            vmp_sha256=VMP_HASH,
            path_sha256=path.path_sha256,
            semantic_feature_plan=forged_plan,
            semantic_feature_plan_sha256=forged_plan_hash,
        )
        _, registry_raw, registry_hash = build_synthetic_registry_artifact(
            registry_snapshot_id="registry_synthetic_e0",
            resolver_version="resolver_1.0.0",
            records={
                ("FORGED", "DOMAIN", "[DOMAIN]"): {
                    "state": "MATCH",
                    "registry_coverage": "COMPLETE",
                    "evidence_ids": ["registry_evidence_registry_truth"],
                }
            },
        )
        # Every standalone parser is structural and therefore accepts this
        # internally coherent forged chain. Only authoritative replay may decide truth.
        self.assertEqual(
            parse_pair_packet_structural(canonical_json_bytes(forged_packet)),
            forged_packet,
        )
        with self.assertRaisesRegex(SemanticValidationError, "semantic_replay_packet_mismatch"):
            replay_semantic_chain(
                vmp_text=vmp,
                vmp_sha256=VMP_HASH,
                active_paths=[path],
                prediction_audit_bytes=canonical_json_bytes(audit),
                registry_artifact_bytes=registry_raw,
                pair_packet_bytes_by_path={path.path_id: canonical_json_bytes(forged_packet)},
                semantic_feature_plan_bytes_by_path={
                    path.path_id: canonical_json_bytes(forged_plan)
                },
                feature_tensor_bytes_by_path={
                    path.path_id: canonical_json_bytes(forged_tensor)
                },
                expected_registry_artifact_sha256=registry_hash,
            )

    def test_complete_replay_accepts_truth_bound_chain_and_returns_hashes(self) -> None:
        text, path, _, fixture, artifacts = basic_artifacts()
        _, registry_raw, registry_hash = build_synthetic_registry_artifact(
            registry_snapshot_id=fixture.registry_snapshot_id,
            resolver_version=fixture.resolver_version,
            records={
                ("SBI", "DOMAIN", "[DOMAIN]"): {
                    "state": "MATCH",
                    "registry_coverage": "COMPLETE",
                    "evidence_ids": ["registry_evidence_sbi_domain"],
                }
            },
        )
        path_artifact = artifacts["paths"][0]
        replay = replay_semantic_chain(
            vmp_text=text,
            vmp_sha256=VMP_HASH,
            active_paths=[path],
            prediction_audit_bytes=canonical_json_bytes(artifacts["prediction_audit"]),
            registry_artifact_bytes=registry_raw,
            pair_packet_bytes_by_path={
                path.path_id: canonical_json_bytes(path_artifact["pair_packet"])
            },
            semantic_feature_plan_bytes_by_path={
                path.path_id: canonical_json_bytes(path_artifact["semantic_feature_plan"])
            },
            feature_tensor_bytes_by_path={
                path.path_id: canonical_json_bytes(path_artifact["semantic_feature_tensor"])
            },
            expected_prediction_audit_sha256=artifacts["prediction_audit_sha256"],
            expected_registry_artifact_sha256=registry_hash,
            expected_pair_packet_sha256_by_path={
                path.path_id: path_artifact["pair_packet_sha256"]
            },
            expected_feature_tensor_sha256_by_path={
                path.path_id: path_artifact["semantic_feature_tensor_sha256"]
            },
        )
        self.assertEqual(replay.registry_artifact_sha256, registry_hash)
        self.assertEqual(dict(replay.P_pair), artifacts["P_pair"])
        self.assertEqual(
            replay.paths[0].pair_packet_sha256,
            path_artifact["pair_packet_sha256"],
        )


class StructuralParserAndIndicMechanicsTests(unittest.TestCase):
    def test_structural_parsers_fail_closed_on_excessive_nesting(self) -> None:
        deep = b"[" * 80 + b"]" * 80
        for parser, kwargs in (
            (parse_prediction_audit_structural, {"vmp_text": "A"}),
            (parse_pair_packet_structural, {}),
            (
                parse_e0_feature_tensor_structural,
                {
                    "vmp_text": "A",
                    "semantic_feature_plan": {
                        "feature_version": "1.0.0",
                        "no_explicit_pair": True,
                        "pairs": [],
                    },
                },
            ),
        ):
            with self.subTest(parser=parser.__name__):
                with self.assertRaises(SemanticValidationError):
                    parser(deep, **kwargs)

    def test_indic_combining_marks_and_code_mix_are_mechanical_only(self) -> None:
        # These checks exercise Unicode categories and VMP cut-through only.
        # They make no transliteration-quality or language-understanding claim.
        cases = {
            "hindi": "का KYC [DOMAIN]",
            "tamil": "கா KYC [DOMAIN]",
            "telugu": "కా KYC [DOMAIN]",
            "english_indic_code_mix": "KYC का [DOMAIN]",
        }
        for language, vmp in cases.items():
            with self.subTest(language=language):
                grid = e0_vmp_category_grid(vmp)
                categories = [row.index(1.0) for row in grid]
                self.assertIn(0, categories)  # LETTER
                self.assertIn(1, categories)  # MARK
                self.assertIn(3, categories)  # WHITESPACE
                word_end = vmp.index(" ")
                path = rewritten_path(
                    vmp,
                    source_start=0,
                    source_end=word_end,
                    replacement="romanized",
                )
                full = render_lookup_surface(
                    vmp_text=vmp,
                    path_text=path.text,
                    path_alignment=path.alignment,
                    effective_rewrite_spans=path.effective_rewrite_spans,
                    start=0,
                    end=word_end,
                )
                cut = render_lookup_surface(
                    vmp_text=vmp,
                    path_text=path.text,
                    path_alignment=path.alignment,
                    effective_rewrite_spans=path.effective_rewrite_spans,
                    start=0,
                    end=max(1, word_end - 1),
                )
                self.assertEqual(full, ("romanized", "ALIGNED"))
                self.assertEqual(cut, ("", "UNALIGNED"))


if __name__ == "__main__":
    unittest.main()
