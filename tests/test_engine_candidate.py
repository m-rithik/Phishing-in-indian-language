from __future__ import annotations

from copy import deepcopy
from itertools import product
import json
import math
import unittest
from unittest.mock import patch

from fisher_engine._numeric import f64_bits_to_float, float_to_f64_bits
from fisher_engine.candidate import (
    CANDIDATE_PATH_ARTIFACT_FIELDS,
    CandidateReplayResult,
    CandidateValidationError,
    build_identity_manifest,
    candidate_diagnostics_bytes,
    candidate_path_artifact_bytes,
    candidate_path_artifact_sha256,
    parse_candidate_diagnostics,
    parse_candidate_path_artifact,
    parse_provider_execution,
    provider_execution_bytes,
    replay_candidate_run,
    run_candidate_provider,
    validate_rewrite_spans,
)


SHA_A = "a" * 64
SHA_B = "b" * 64
VMP_SHA = "c" * 64


def span(index: int, start: int, end: int, text: str) -> dict:
    return {
        "span_index": index,
        "start": start,
        "end": end,
        "source_text": text[start:end],
    }


def reading(rank: int, text: str, alignment: list[list[int]], score: float = 0.0) -> dict:
    return {
        "provider_rank": rank,
        "reading_text": text,
        "reading_alignment": alignment,
        "raw_logit_f64_bits": float_to_f64_bits(score),
    }


def composed_units(
    vmp_text: str,
    spans: list[dict],
    alternatives: list[list[tuple[str, float]]],
) -> list[dict]:
    return [
        {
            "unit_index": index,
            "unit_kind": "SPAN",
            "start": item["start"],
            "end": item["end"],
            "source_text": vmp_text[item["start"] : item["end"]],
            "readings": [
                reading(
                    rank,
                    replacement,
                    [[item["start"], item["end"]]] * len(replacement),
                    score,
                )
                for rank, (replacement, score) in enumerate(options, start=1)
            ],
        }
        for index, (item, options) in enumerate(zip(spans, alternatives))
    ]


def direct_unit(vmp_text: str, readings: list[dict]) -> list[dict]:
    return [
        {
            "unit_index": 0,
            "unit_kind": "FULL_PATH",
            "start": 0,
            "end": len(vmp_text),
            "source_text": vmp_text,
            "readings": readings,
        }
    ]


def base_kwargs(vmp_text: str, spans: list[dict], *, mode: str = "COMPOSED_SPAN") -> dict:
    return {
        "vmp_text": vmp_text,
        "vmp_sha256": VMP_SHA,
        "visible_artifacts": [],
        "configured_mode": mode,
        "provider_config_id": "provider_synthetic_e0",
        "provider_config_sha256": SHA_A,
        "normalizer_id": "normalizer_identity",
        "normalizer_sha256": SHA_B,
        "selector_output": spans,
        "temperature": 1.0,
    }


class CandidateEnumerationTests(unittest.TestCase):
    @staticmethod
    def _max_span_beam_run(replacement_length: int):
        text = "x" * 64
        spans = [span(index, index, index + 1, text) for index in range(64)]
        alternatives = [
            [
                (character + "z" * (replacement_length - 1), float(-rank))
                for rank, character in enumerate("abcdefgh")
            ]
            for _ in spans
        ]
        return run_candidate_provider(
            **base_kwargs(text, spans),
            provider_units=composed_units(text, spans, alternatives),
        )

    def test_8_by_8_is_exact_and_returns_top_eight(self) -> None:
        text = "a b"
        spans = [span(0, 0, 1, text), span(1, 2, 3, text)]
        alternatives = [
            [(character, float(-index)) for index, character in enumerate("abcdefgh")],
            [(character, float(-index)) for index, character in enumerate("ijklmnop")],
        ]
        result = run_candidate_provider(
            **base_kwargs(text, spans),
            provider_units=composed_units(text, spans, alternatives),
        )
        self.assertEqual(result.execution_status, "VALID")
        self.assertEqual(result.candidate_diagnostics["search_mode"], "EXACT")
        self.assertEqual(result.candidate_diagnostics["postmerge_count"], 64)
        self.assertEqual(result.candidate_diagnostics["returned_count"], 8)
        self.assertEqual(len(result.internal_paths), 8)
        self.assertEqual(result.internal_paths[0].text, "a i")

    def test_8_by_8_by_2_uses_width_64_beam(self) -> None:
        text = "a b c"
        spans = [
            span(0, 0, 1, text),
            span(1, 2, 3, text),
            span(2, 4, 5, text),
        ]
        alternatives = [
            [(character, float(-index)) for index, character in enumerate("abcdefgh")],
            [(character, float(-index)) for index, character in enumerate("ijklmnop")],
            [(character, float(-index)) for index, character in enumerate("qr")],
        ]
        result = run_candidate_provider(
            **base_kwargs(text, spans),
            provider_units=composed_units(text, spans, alternatives),
        )
        self.assertEqual(result.execution_status, "VALID")
        self.assertEqual(result.candidate_diagnostics["search_mode"], "BEAM")
        self.assertEqual(result.candidate_diagnostics["preK_scope"], "FINAL_BEAM")
        self.assertEqual(result.candidate_diagnostics["postmerge_count"], 64)
        self.assertEqual(len(result.internal_paths), 8)
        def stable_lse(scores: list[float]) -> float:
            maximum = max(scores)
            total = 0.0
            for score in scores:
                total = total + math.exp(score - maximum)
            return maximum + math.log(total)

        normalized_options = []
        for options in alternatives:
            denominator = stable_lse([score for _, score in options])
            normalized_options.append(
                [(replacement, score - denominator) for replacement, score in options]
            )
        exhaustive = []
        for combination in product(*normalized_options):
            path_text = f"{combination[0][0]} {combination[1][0]} {combination[2][0]}"
            composition_score = 0.0
            for value in combination:
                composition_score = composition_score + value[1]
            exhaustive.append((composition_score, path_text))
        expected = [
            path_text
            for _, path_text in sorted(
                exhaustive,
                key=lambda value: (-value[0], value[1].encode("utf-8")),
            )[:8]
        ]
        self.assertEqual([path.text for path in result.internal_paths], expected)

    def test_equal_scores_break_ties_by_utf8_text_bytes(self) -> None:
        text = "x"
        spans = [span(0, 0, 1, text)]
        alternatives = [[("β", 0.0), ("a", 0.0), ("A", 0.0)]]
        result = run_candidate_provider(
            **base_kwargs(text, spans),
            provider_units=composed_units(text, spans, alternatives),
        )
        self.assertEqual([path.text for path in result.internal_paths], ["A", "a", "β"])

    def test_text_equal_alignment_bytes_are_identity_and_tie_breaker(self) -> None:
        text = "xy"
        spans = [span(0, 0, 2, text)]
        units = [
            {
                "unit_index": 0,
                "unit_kind": "SPAN",
                "start": 0,
                "end": 2,
                "source_text": text,
                "readings": [
                    reading(1, "zz", [[0, 2], [0, 2]], 0.0),
                    reading(2, "zz", [[0, 1], [1, 2]], 0.0),
                ],
            }
        ]
        result = run_candidate_provider(
            **base_kwargs(text, spans),
            provider_units=units,
        )
        self.assertEqual(result.candidate_diagnostics["postmerge_count"], 2)
        self.assertNotEqual(result.internal_paths[0].path_sha256, result.internal_paths[1].path_sha256)
        self.assertEqual(result.internal_paths[0].alignment, ((0, 1), (1, 2)))
        self.assertEqual(result.internal_paths[1].alignment, ((0, 2), (0, 2)))

    def test_beam_alignment_byte_order_matches_exhaustive_oracle(self) -> None:
        text = "ab cd ef"
        spans = [
            span(0, 0, 2, text),
            span(1, 3, 5, text),
            span(2, 6, 8, text),
        ]

        def variants(start: int, triples: bool) -> list[list[list[int]]]:
            a = [start, start + 1]
            b = [start, start + 2]
            c = [start + 1, start + 2]
            if triples:
                return [[a, a, b], [a, a, c], [a, b, b], [a, b, c], [a, c, c], [b, b, b], [b, b, c], [b, c, c]]
            return [[a, c], [a, b], [b, b], [b, c]]

        alignments = [variants(0, False), variants(3, False), variants(6, True)]
        units = []
        for index, (item, options) in enumerate(zip(spans, alignments)):
            units.append(
                {
                    "unit_index": index,
                    "unit_kind": "SPAN",
                    "start": item["start"],
                    "end": item["end"],
                    "source_text": item["source_text"],
                    "readings": [
                        reading(rank, "zzz" if index == 2 else "zz", value, 0.0)
                        for rank, value in enumerate(options, start=1)
                    ],
                }
            )
        result = run_candidate_provider(
            **base_kwargs(text, spans),
            provider_units=units,
        )
        self.assertEqual(result.candidate_diagnostics["search_mode"], "BEAM")
        exhaustive = []
        for first, second, third in product(*alignments):
            full = tuple(tuple(pair) for pair in first)
            full += ((2, 3),)
            full += tuple(tuple(pair) for pair in second)
            full += ((5, 6),)
            full += tuple(tuple(pair) for pair in third)
            encoded = json.dumps(
                [[start, end] for start, end in full], separators=(",", ":")
            ).encode()
            exhaustive.append((encoded, full))
        expected = [value for _, value in sorted(exhaustive)[:8]]
        self.assertEqual([path.alignment for path in result.internal_paths], expected)

    def test_duplicate_ranks_remain_compact_without_cartesian_lineage(self) -> None:
        text = "x" * 64
        spans = [span(index, index, index + 1, text) for index in range(64)]
        alternatives = [[("z", float(rank)) for rank in range(8)] for _ in spans]
        result = run_candidate_provider(
            **base_kwargs(text, spans),
            provider_units=composed_units(text, spans, alternatives),
        )
        self.assertEqual(result.execution_status, "VALID")
        self.assertEqual(result.candidate_diagnostics["search_mode"], "EXACT")
        self.assertEqual(result.candidate_diagnostics["input_count"], 512)
        self.assertEqual(result.candidate_diagnostics["span_merge_reduction_count"], 448)
        self.assertEqual(result.candidate_diagnostics["postmerge_count"], 1)
        contributors = result.internal_paths[0].lineage["contributors"]
        self.assertEqual(len(contributors), 1)
        self.assertEqual(len(contributors[0]["units"]), 64)
        self.assertTrue(all(unit["ranks"] == list(range(1, 9)) for unit in contributors[0]["units"]))

    def test_log_domain_retained_mass_is_finite_for_extreme_scores(self) -> None:
        text = "a b"
        spans = [span(0, 0, 1, text), span(1, 2, 3, text)]
        alternatives = [
            [(character, -1_000.0 * index) for index, character in enumerate("abcdefgh")],
            [(character, -1_000.0 * index) for index, character in enumerate("ijklmnop")],
        ]
        result = run_candidate_provider(
            **base_kwargs(text, spans),
            provider_units=composed_units(text, spans, alternatives),
        )
        mass = f64_bits_to_float(
            result.candidate_diagnostics["retained_preK_composition_mass_f64_bits"]
        )
        self.assertTrue(math.isfinite(mass))
        self.assertGreater(mass, 0.0)
        self.assertLessEqual(mass, 1.0)
        self.assertTrue(
            math.isfinite(f64_bits_to_float(result.candidate_diagnostics["L_preK_f64_bits"]))
        )

    def test_q_records_exact_numerators_denominator_and_display_weights(self) -> None:
        text = "x"
        spans = [span(0, 0, 1, text)]
        alternatives = [[("a", 0.0), ("b", -1.0), ("c", -2.0)]]
        result = run_candidate_provider(
            **base_kwargs(text, spans),
            provider_units=composed_units(text, spans, alternatives),
        )
        numerators = [path.q_numerator for path in result.internal_paths]
        denominator = f64_bits_to_float(result.candidate_diagnostics["q_normalizer_f64_bits"])
        self.assertEqual(sum(numerators), denominator)
        self.assertEqual([path.q for path in result.internal_paths], [value / denominator for value in numerators])

    def test_persistent_beam_is_bounded_and_deterministic_at_64_by_8_by_1(self) -> None:
        first = self._max_span_beam_run(1)
        second = self._max_span_beam_run(1)
        self.assertEqual(first.execution_status, "VALID")
        self.assertEqual(first.work_units, 262_411)
        self.assertEqual(second.work_units, first.work_units)
        self.assertEqual(second.candidate_paths, first.candidate_paths)

    def test_persistent_beam_accepts_64_by_8_by_300_within_frozen_budget(self) -> None:
        result = self._max_span_beam_run(300)
        self.assertEqual(result.execution_status, "VALID")
        self.assertEqual(result.candidate_diagnostics["search_mode"], "BEAM")
        self.assertEqual(result.work_units, 1_487_115)
        self.assertLess(result.work_units, 2_000_000)
        self.assertTrue(all(len(path.text) == 19_200 for path in result.internal_paths))

    def test_internal_work_budget_aborts_with_controlled_non_echo_error(self) -> None:
        with patch("fisher_engine.candidate.CANDIDATE_WORK_BUDGET", 100):
            result = self._max_span_beam_run(1)
        self.assertEqual(result.execution_status, "INVALID")
        self.assertEqual(result.failure_stage, "CANDIDATE")
        self.assertEqual(result.invalid_codes, ("engine_candidate_invalid_arithmetic",))


class ProviderModeTests(unittest.TestCase):
    def test_direct_full_path_preserves_nonspan_text_and_alignment(self) -> None:
        text = "Pay a now"
        spans = [span(0, 4, 5, text)]
        alignment = [[index, index + 1] for index in range(len(text))]
        units = direct_unit(
            text,
            [
                reading(1, "Pay α now", alignment, 2.0),
                reading(2, "Pay a now", alignment, 1.0),
            ],
        )
        result = run_candidate_provider(
            **base_kwargs(text, spans, mode="DIRECT_FULL_PATH"),
            provider_units=units,
        )
        self.assertEqual(result.execution_status, "VALID")
        self.assertEqual(result.candidate_diagnostics["search_mode"], "DIRECT_FULL_PATH")
        self.assertEqual(result.internal_paths[0].text, "Pay α now")
        self.assertEqual(result.internal_paths[0].effective_rewrite_spans, tuple(spans))

    def test_direct_full_path_rejects_change_outside_rewrite_span(self) -> None:
        text = "Pay a now"
        spans = [span(0, 4, 5, text)]
        alignment = [[index, index + 1] for index in range(len(text))]
        units = direct_unit(text, [reading(1, "Bay α now", alignment)])
        result = run_candidate_provider(
            **base_kwargs(text, spans, mode="DIRECT_FULL_PATH"),
            provider_units=units,
        )
        self.assertEqual(result.execution_status, "INVALID")
        self.assertEqual(result.provider_execution["outcome"], "PROVIDER_INVALID_OUTPUT")

    def test_direct_duplicate_merge_has_compact_rank_set(self) -> None:
        text = "x"
        spans = [span(0, 0, 1, text)]
        units = direct_unit(
            text,
            [
                reading(2, "y", [[0, 1]], 1.0),
                reading(1, "y", [[0, 1]], 0.0),
                reading(3, "z", [[0, 1]], -1.0),
            ],
        )
        result = run_candidate_provider(
            **base_kwargs(text, spans, mode="DIRECT_FULL_PATH"),
            provider_units=units,
        )
        self.assertEqual(result.candidate_diagnostics["input_count"], 3)
        self.assertEqual(result.candidate_diagnostics["full_merge_reduction_count"], 1)
        merged = next(path for path in result.internal_paths if path.text == "y")
        self.assertEqual(merged.lineage["contributors"][0]["ranks"], [1, 2])

    def test_no_eligible_returns_valid_identity(self) -> None:
        result = run_candidate_provider(**base_kwargs("plain", []))
        self.assertEqual(result.execution_status, "VALID")
        self.assertEqual(result.provider_execution["outcome"], "NO_ELIGIBLE")
        self.assertEqual(result.provider_execution["eligible_spans"], [])
        self.assertEqual(result.candidate_diagnostics["mode"], "IDENTITY_BYPASS")
        self.assertEqual(result.internal_paths[0].text, "plain")
        self.assertEqual(result.internal_paths[0].q, 1.0)
        self.assertEqual(result.internal_paths[0].effective_rewrite_spans, ())

    def test_identity_manifest_hash_is_cause_independent_but_execution_is_not(self) -> None:
        text = "x"
        no_eligible = run_candidate_provider(**base_kwargs(text, []))
        spans = [span(0, 0, 1, text)]
        unavailable = run_candidate_provider(
            **base_kwargs(text, spans),
            dispatch_outcome="UNAVAILABLE_FALLBACK",
            failure_code="PROVIDER_UNAVAILABLE",
        )
        timeout = run_candidate_provider(
            **base_kwargs(text, spans),
            dispatch_outcome="TIMEOUT_FALLBACK",
            failure_code="NORMALIZER_TIMEOUT",
        )
        self.assertEqual(
            {no_eligible.provider_manifest_sha256, unavailable.provider_manifest_sha256, timeout.provider_manifest_sha256},
            {no_eligible.provider_manifest_sha256},
        )
        self.assertEqual(unavailable.execution_status, "DEGRADED_STOP_AFTER_IDENTITY")
        self.assertEqual(timeout.execution_status, "DEGRADED_STOP_AFTER_IDENTITY")
        self.assertNotEqual(no_eligible.provider_execution, unavailable.provider_execution)
        self.assertEqual(unavailable.provider_execution["eligible_spans"], spans)
        self.assertEqual(unavailable.internal_paths[0].effective_rewrite_spans, ())

    def test_identity_manifest_has_exact_declared_order_and_no_newline(self) -> None:
        manifest, encoded, digest = build_identity_manifest(vmp_sha256=VMP_SHA)
        self.assertEqual(
            tuple(manifest),
            (
                "manifest_version",
                "vmp_sha256",
                "provider_config_id",
                "provider_mode",
                "normalizer_id",
                "rewrite_spans",
                "units",
            ),
        )
        self.assertFalse(encoded.endswith(b"\n"))
        self.assertEqual(json.loads(encoded), manifest)
        self.assertEqual(len(digest), 64)


class ProviderOutcomeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.text = "x"
        self.spans = [span(0, 0, 1, self.text)]

    def test_not_invoked_is_fail_closed(self) -> None:
        result = run_candidate_provider(
            **base_kwargs(self.text, self.spans),
            dispatch_outcome="NOT_INVOKED",
            failure_code="PROVIDER_NOT_INVOKED",
        )
        self.assertEqual(result.execution_status, "INVALID")
        self.assertEqual(result.failure_stage, "PROVIDER_EXECUTION")
        self.assertEqual(result.invalid_codes, ("engine_provider_not_invoked",))
        self.assertFalse(result.provider_execution["output_accepted"])

    def test_explicit_invalid_provider_and_normalizer_outputs(self) -> None:
        provider = run_candidate_provider(
            **base_kwargs(self.text, self.spans),
            dispatch_outcome="PROVIDER_INVALID_OUTPUT",
            failure_code="PROVIDER_INVALID_OUTPUT",
        )
        normalizer = run_candidate_provider(
            **base_kwargs(self.text, self.spans),
            dispatch_outcome="NORMALIZER_INVALID_OUTPUT",
            failure_code="NORMALIZER_INVALID_OUTPUT",
        )
        self.assertEqual(provider.invalid_codes, ("engine_provider_invalid_output",))
        self.assertEqual(normalizer.invalid_codes, ("engine_normalizer_invalid_output",))
        self.assertIsNone(provider.provider_manifest_sha256)
        self.assertIsNone(normalizer.provider_manifest_sha256)

    def test_structurally_invalid_units_become_provider_invalid_output(self) -> None:
        result = run_candidate_provider(
            **base_kwargs(self.text, self.spans),
            provider_units=[],
        )
        self.assertEqual(result.provider_execution["outcome"], "PROVIDER_INVALID_OUTPUT")
        self.assertEqual(result.invalid_codes, ("engine_provider_invalid_output",))

    def test_invalid_provider_output_retains_only_validated_safe_prefix_count(self) -> None:
        units = composed_units(self.text, self.spans, [[("a", 0.0), ("b", 0.0)]])
        units[0]["readings"][1]["reading_alignment"] = [[False, 1]]
        result = run_candidate_provider(
            **base_kwargs(self.text, self.spans),
            provider_units=units,
        )
        self.assertEqual(result.execution_status, "INVALID")
        self.assertEqual(result.provider_count, 1)
        self.assertEqual(result.normalizer_count, 0)

    def test_manifest_byte_overflow_rejects_without_losing_safe_count(self) -> None:
        units = composed_units(self.text, self.spans, [[("a", 0.0)]])
        with patch("fisher_engine.candidate.PROVIDER_MANIFEST_MAX_BYTES", 1):
            result = run_candidate_provider(
                **base_kwargs(self.text, self.spans),
                provider_units=units,
            )
        self.assertEqual(result.invalid_codes, ("engine_provider_invalid_output",))
        self.assertEqual(result.provider_count, 1)

    def test_negative_zero_and_nonfinite_raw_logits_are_rejected(self) -> None:
        units = composed_units(self.text, self.spans, [[("a", 0.0)]])
        for bits in ("8000000000000000", "7ff8000000000000", "7ff0000000000000"):
            with self.subTest(bits=bits):
                invalid = deepcopy(units)
                invalid[0]["readings"][0]["raw_logit_f64_bits"] = bits
                result = run_candidate_provider(
                    **base_kwargs(self.text, self.spans),
                    provider_units=invalid,
                )
                self.assertEqual(result.invalid_codes, ("engine_provider_invalid_output",))

    def test_negative_zero_temperature_fails_candidate_after_manifest_acceptance(self) -> None:
        units = composed_units(self.text, self.spans, [[("a", 0.0)]])
        kwargs = base_kwargs(self.text, self.spans)
        kwargs["temperature"] = -0.0
        result = run_candidate_provider(**kwargs, provider_units=units)
        self.assertEqual(result.execution_status, "INVALID")
        self.assertEqual(result.failure_stage, "CANDIDATE")
        self.assertEqual(result.invalid_codes, ("engine_candidate_invalid_arithmetic",))
        self.assertIsNotNone(result.provider_manifest_sha256)

    def test_finite_logits_that_overflow_normalization_fail_at_candidate_stage(self) -> None:
        units = composed_units(self.text, self.spans, [[("a", 0.0), ("b", 0.0)]])
        units[0]["readings"][0]["raw_logit_f64_bits"] = "7fefffffffffffff"
        units[0]["readings"][1]["raw_logit_f64_bits"] = "ffefffffffffffff"
        result = run_candidate_provider(
            **base_kwargs(self.text, self.spans),
            provider_units=units,
        )
        self.assertEqual(result.execution_status, "INVALID")
        self.assertEqual(result.failure_stage, "CANDIDATE")
        self.assertEqual(result.invalid_codes, ("engine_candidate_nonfinite",))
        self.assertEqual(result.provider_execution["outcome"], "SUCCEEDED")
        self.assertIsNotNone(result.provider_manifest_sha256)

    def test_malformed_dispatch_combination_raises_only_safe_code(self) -> None:
        with self.assertRaisesRegex(CandidateValidationError, r"^candidate_invalid_dispatch_outcome$"):
            run_candidate_provider(
                **base_kwargs(self.text, self.spans),
                dispatch_outcome="TIMEOUT_FALLBACK",
                failure_code="PROVIDER_UNAVAILABLE",
            )


class CandidateArtifactReplayTests(unittest.TestCase):
    def setUp(self) -> None:
        self.text = "pay jaldi"
        self.spans = [span(0, 4, 9, self.text)]
        self.run = run_candidate_provider(
            **base_kwargs(self.text, self.spans),
            provider_units=composed_units(
                self.text,
                self.spans,
                [[("जल्दी", 1.0), ("jaldi", 0.0)]],
            ),
        )

    def test_canonical_path_artifact_round_trip_binds_full_replay_context(self) -> None:
        artifact = self.run.candidate_path_artifacts[0]
        raw = self.run.candidate_path_artifact_bytes[0]
        self.assertEqual(tuple(artifact), CANDIDATE_PATH_ARTIFACT_FIELDS)
        self.assertNotIn("candidate_path_artifact_sha256", artifact)
        self.assertEqual(candidate_path_artifact_bytes(artifact), raw)
        self.assertEqual(
            candidate_path_artifact_sha256(artifact),
            self.run.candidate_path_artifact_sha256s[0],
        )
        self.assertEqual(
            parse_candidate_path_artifact(
                raw,
                expected_vmp_sha256=VMP_SHA,
                expected_provider_manifest_sha256=self.run.provider_manifest_sha256,
            ),
            artifact,
        )

    def test_replay_recomputes_diagnostics_paths_lineage_and_q(self) -> None:
        replay = replay_candidate_run(
            vmp_text=self.text,
            vmp_sha256=VMP_SHA,
            visible_artifacts=[],
            provider_manifest_bytes=self.run.provider_manifest_bytes,
            provider_execution_bytes=provider_execution_bytes(self.run.provider_execution),
            candidate_diagnostics_bytes=candidate_diagnostics_bytes(
                self.run.candidate_diagnostics
            ),
            candidate_path_artifact_bytes=self.run.candidate_path_artifact_bytes,
        )
        self.assertIsInstance(replay, CandidateReplayResult)
        self.assertEqual(replay.candidate_diagnostics, self.run.candidate_diagnostics)
        self.assertEqual(replay.candidate_paths, self.run.candidate_paths)
        self.assertEqual(replay.internal_paths, self.run.internal_paths)

    def test_path_parser_rejects_boolean_coordinate_negative_zero_and_nonfinite(self) -> None:
        artifact = self.run.candidate_path_artifacts[0]
        mutations = []
        boolean = deepcopy(artifact)
        boolean["alignment"][0][0] = False
        mutations.append(boolean)
        negative_zero = deepcopy(artifact)
        negative_zero["q_f64_bits"] = "8000000000000000"
        mutations.append(negative_zero)
        nonfinite = deepcopy(artifact)
        nonfinite["composition_score_f64_bits"] = "7ff8000000000000"
        mutations.append(nonfinite)
        for value in mutations:
            with self.subTest(value=value):
                raw = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode()
                with self.assertRaises(CandidateValidationError):
                    parse_candidate_path_artifact(raw)

    def test_replay_rejects_tampered_q_without_echoing_path_text(self) -> None:
        tampered = list(self.run.candidate_path_artifact_bytes)
        value = json.loads(tampered[0])
        value["q_f64_bits"] = float_to_f64_bits(0.125)
        tampered[0] = json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode()
        with self.assertRaises(CandidateValidationError) as caught:
            replay_candidate_run(
                vmp_text=self.text,
                vmp_sha256=VMP_SHA,
                visible_artifacts=[],
                provider_manifest_bytes=self.run.provider_manifest_bytes,
                provider_execution_bytes=provider_execution_bytes(
                    self.run.provider_execution
                ),
                candidate_diagnostics_bytes=candidate_diagnostics_bytes(
                    self.run.candidate_diagnostics
                ),
                candidate_path_artifact_bytes=tampered,
            )
        self.assertNotIn(self.run.internal_paths[0].text, str(caught.exception))

    def test_identity_and_degraded_identity_replay_keep_distinct_execution_cause(self) -> None:
        no_eligible = run_candidate_provider(**base_kwargs("plain", []))
        attempted_spans = [span(0, 0, 1, "plain")]
        degraded = run_candidate_provider(
            **base_kwargs("plain", attempted_spans),
            dispatch_outcome="UNAVAILABLE_FALLBACK",
            failure_code="PROVIDER_UNAVAILABLE",
        )
        replays = []
        for result in (no_eligible, degraded):
            replays.append(
                replay_candidate_run(
                    vmp_text="plain",
                    vmp_sha256=VMP_SHA,
                    visible_artifacts=[],
                    provider_manifest_bytes=result.provider_manifest_bytes,
                    provider_execution_bytes=result.provider_execution_bytes,
                    candidate_diagnostics_bytes=result.candidate_diagnostics_bytes,
                    candidate_path_artifact_bytes=result.candidate_path_artifact_bytes,
                )
            )
        self.assertEqual(
            replays[0].provider_manifest_sha256,
            replays[1].provider_manifest_sha256,
        )
        self.assertEqual(replays[0].provider_execution["outcome"], "NO_ELIGIBLE")
        self.assertEqual(
            replays[1].provider_execution["outcome"], "UNAVAILABLE_FALLBACK"
        )

    def test_strict_artifact_parsers_reject_duplicate_noncanonical_and_oversize(self) -> None:
        raw = self.run.candidate_path_artifact_bytes[0]
        duplicate = raw.replace(b'{"artifact_version":', b'{"artifact_version":"1.0.0","artifact_version":', 1)
        with self.assertRaisesRegex(CandidateValidationError, "duplicate_key"):
            parse_candidate_path_artifact(duplicate)
        with self.assertRaisesRegex(CandidateValidationError, "noncanonical_bytes"):
            parse_candidate_path_artifact(raw + b"\n")
        with patch("fisher_engine.candidate.CANDIDATE_PATH_ARTIFACT_MAX_BYTES", 1):
            with self.assertRaisesRegex(CandidateValidationError, "too_large"):
                parse_candidate_path_artifact(raw)

    def test_execution_and_diagnostics_bytes_reject_bool_and_negative_zero(self) -> None:
        execution = deepcopy(self.run.provider_execution)
        execution["invocation_attempted"] = 1
        raw_execution = json.dumps(
            execution, ensure_ascii=False, separators=(",", ":")
        ).encode()
        with self.assertRaises(CandidateValidationError):
            parse_provider_execution(raw_execution)
        diagnostics = deepcopy(self.run.candidate_diagnostics)
        diagnostics["temperature_f64_bits"] = "8000000000000000"
        raw_diagnostics = json.dumps(
            diagnostics, ensure_ascii=False, separators=(",", ":")
        ).encode()
        with self.assertRaises(CandidateValidationError):
            parse_candidate_diagnostics(raw_diagnostics)

    def test_multilingual_mechanics_preserve_scripts_without_quality_claim(self) -> None:
        cases = (
            ("otp bhejo", "ओटीपी भेजो"),
            ("otp anuppu", "ஓடிபி அனுப்பு"),
            ("otp pampu", "ఓటీపీ పంపు"),
            ("KYC jaldi verify", "KYC जल्दी verify"),
        )
        for source, replacement in cases:
            with self.subTest(source=source):
                spans = [span(0, 0, len(source), source)]
                result = run_candidate_provider(
                    **base_kwargs(source, spans),
                    provider_units=composed_units(
                        source,
                        spans,
                        [[(replacement, 0.0)]],
                    ),
                )
                self.assertEqual(result.execution_status, "VALID")
                self.assertEqual(result.internal_paths[0].text, replacement)
                self.assertEqual(
                    parse_candidate_path_artifact(
                        result.candidate_path_artifact_bytes[0]
                    )["text"],
                    replacement,
                )


class EligibilityAndAlignmentTests(unittest.TestCase):
    def test_boolean_range_overlap_artifact_and_65_spans_are_invalid(self) -> None:
        text = "x" * 65
        valid_one = [span(0, 0, 1, text)]
        boolean = deepcopy(valid_one)
        boolean[0]["start"] = False
        overlap = [span(0, 0, 2, text), span(1, 1, 3, text)]
        out_of_range = [span(0, 0, 66, text)]
        sixty_five = [span(index, index, index + 1, text) for index in range(65)]
        cases = (
            (boolean, []),
            (overlap, []),
            (out_of_range, []),
            (valid_one, [{"start": 0, "end": 1}]),
            (sixty_five, []),
        )
        for selector, artifacts in cases:
            with self.subTest(selector_length=len(selector), artifacts=artifacts):
                kwargs = base_kwargs(text, selector)
                kwargs["visible_artifacts"] = artifacts
                result = run_candidate_provider(**kwargs)
                self.assertEqual(result.provider_execution["outcome"], "ELIGIBILITY_INVALID")
                self.assertEqual(result.provider_execution["eligible_spans"], [])
                self.assertEqual(result.invalid_codes, ("engine_invalid_eligibility",))

    def test_64_spans_is_valid_boundary_and_not_truncated(self) -> None:
        text = "x" * 64
        spans = [span(index, index, index + 1, text) for index in range(64)]
        result = run_candidate_provider(
            **base_kwargs(text, spans),
            dispatch_outcome="NOT_INVOKED",
            failure_code="PROVIDER_NOT_INVOKED",
        )
        self.assertEqual(result.provider_execution["outcome"], "NOT_INVOKED")
        self.assertEqual(len(result.provider_execution["eligible_spans"]), 64)
        self.assertEqual(result.configured_span_entries_capped, 64)
        self.assertEqual(result.eligible_spans_capped, 64)

    def test_artifact_adjacency_is_allowed_but_contact_is_not(self) -> None:
        text = "abcd"
        artifacts = [{"start": 2, "end": 4}]
        accepted = validate_rewrite_spans(
            [span(0, 0, 2, text)],
            vmp_text=text,
            visible_artifacts=artifacts,
        )
        self.assertEqual(len(accepted), 1)
        with self.assertRaisesRegex(CandidateValidationError, r"^candidate_invalid_eligibility$"):
            validate_rewrite_spans(
                [span(0, 1, 3, text)],
                vmp_text=text,
                visible_artifacts=artifacts,
            )

    def test_span_reading_codepoint_and_utf8_boundary(self) -> None:
        text = "x"
        spans = [span(0, 0, 1, text)]
        boundary = "😀" * 512
        valid = run_candidate_provider(
            **base_kwargs(text, spans),
            provider_units=composed_units(text, spans, [[(boundary, 0.0)]]),
        )
        self.assertEqual(valid.execution_status, "VALID")
        self.assertEqual(len(valid.internal_paths[0].text), 512)
        over = "a" * 513
        invalid = run_candidate_provider(
            **base_kwargs(text, spans),
            provider_units=composed_units(text, spans, [[(over, 0.0)]]),
        )
        self.assertEqual(invalid.invalid_codes, ("engine_provider_invalid_output",))

    def test_non_array_selector_has_zero_configured_count(self) -> None:
        result = run_candidate_provider(**base_kwargs("x", {"unsafe": "ignored"}))
        self.assertEqual(result.configured_span_entries_capped, 0)
        self.assertEqual(result.provider_execution["eligible_spans"], [])

    def test_wrong_source_slice_and_noncanonical_order_are_invalid(self) -> None:
        text = "abc"
        wrong_slice = [span(0, 0, 1, text)]
        wrong_slice[0]["source_text"] = "secret-not-echoed"
        wrong_order = [span(1, 0, 1, text)]
        for selector in (wrong_slice, wrong_order):
            with self.assertRaisesRegex(CandidateValidationError, r"^candidate_invalid_eligibility$"):
                validate_rewrite_spans(selector, vmp_text=text, visible_artifacts=[])

    def test_boolean_and_uncovered_alignments_are_invalid_provider_output(self) -> None:
        text = "xy"
        spans = [span(0, 0, 2, text)]
        base = composed_units(text, spans, [[("z", 0.0)]])
        variants = []
        boolean = deepcopy(base)
        boolean[0]["readings"][0]["reading_alignment"] = [[False, 2]]
        variants.append(boolean)
        uncovered = deepcopy(base)
        uncovered[0]["readings"][0]["reading_alignment"] = [[0, 1]]
        variants.append(uncovered)
        outside = deepcopy(base)
        outside[0]["readings"][0]["reading_alignment"] = [[0, 3]]
        variants.append(outside)
        for units in variants:
            with self.subTest(alignment=units[0]["readings"][0]["reading_alignment"]):
                result = run_candidate_provider(
                    **base_kwargs(text, spans),
                    provider_units=units,
                )
                self.assertEqual(result.invalid_codes, ("engine_provider_invalid_output",))


if __name__ == "__main__":
    unittest.main()
