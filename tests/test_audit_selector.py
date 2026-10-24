from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from itertools import combinations
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from fisher_audit.selector import (
    ALGORITHM_VERSION,
    SCHEMA_VERSION,
    SCOPE,
    Attempt,
    _select_supplements_indexed,
    allocate_hamilton,
    format_json,
    format_text,
    hmac_rank_digest,
    rehearse_file,
)


ROOT = Path(__file__).resolve().parents[1]
SEED_HEX = "000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f"
LANGUAGES = (
    "hindi",
    "tamil",
    "telugu",
    "english_indic_code_mixed",
    "uncertain",
)
PRIMARY_STATES = ("benign", "phishing", "uncertain")
PROVENANCE_CLASSES = (
    "tester_donated_authentic",
    "tester_authored_simulation",
    "public_authentic",
    "llm_drafted_human_edited",
)


def attempt_record(
    index: int,
    *,
    language: str = "hindi",
    primary: str = "benign",
    provenance: str = "tester_authored_simulation",
    blind: tuple[str, str] = ("annotator_alpha", "annotator_beta"),
    final: str = "annotator_final",
) -> dict:
    item_id = f"item_rehearsal_{index:06d}"
    partition = "excluded" if language == "uncertain" or primary == "uncertain" else "pilot"
    return {
        "schema_version": "1.0.0",
        "scope": SCOPE,
        "item_id": item_id,
        "simulated_partition": partition,
        "simulated_final_language_state": language,
        "simulated_final_primary_state": primary,
        "simulated_provenance_class": provenance,
        "blind_annotator_ids": sorted(blind, key=lambda value: value.encode("utf-8")),
        "final_annotator_id": final,
        "synthetic_bundle_sha256": sha256(
            f"synthetic-bundle-{index}".encode("ascii")
        ).hexdigest(),
    }


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.write_text(
        "".join(
            json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n"
            for record in records
        ),
        encoding="utf-8",
    )


def diagnostic_codes(report) -> set[str]:
    return {value.code for value in report.diagnostics}


def canonical_hash(value: object) -> str:
    rendered = json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return sha256(rendered).hexdigest()


def make_attempt(index: int, annotators: tuple[str, str, str]) -> Attempt:
    return Attempt(
        source_line=index,
        item_id=f"item_equivalence_{index:06d}",
        partition="pilot",
        language_state="hindi",
        primary_state="benign",
        provenance_class="tester_authored_simulation",
        blind_annotator_ids=(annotators[0], annotators[1]),
        final_annotator_id=annotators[2],
        bundle_sha256=sha256(f"equivalence-{index}".encode("ascii")).hexdigest(),
    )


def slow_supplement_reference(
    ordered_attempts: list[Attempt], main_attempts: list[Attempt], seed: bytes
) -> tuple[list[tuple[str, str, tuple[str, ...]]], list[tuple[str, str | None, str]]]:
    """Independent quadratic oracle retained only in tests."""

    all_annotators = {
        annotator for attempt in ordered_attempts for annotator in attempt.annotator_ids
    }
    covered = {
        annotator for attempt in main_attempts for annotator in attempt.annotator_ids
    }
    initially_missing = sorted(all_annotators - covered, key=lambda value: value.encode())
    selected = {attempt.item_id for attempt in main_attempts}
    supplements: list[tuple[str, str, tuple[str, ...]]] = []
    processing: list[tuple[str, str | None, str]] = []
    for annotator_id in initially_missing:
        if annotator_id in covered:
            processing.append((annotator_id, None, "skipped_already_covered"))
            continue
        candidates = [
            attempt
            for attempt in ordered_attempts
            if attempt.item_id not in selected
            and annotator_id in attempt.annotator_ids
        ]
        chosen = min(
            candidates,
            key=lambda attempt: (
                hmac_rank_digest(seed, attempt.cell_key, attempt.item_id),
                attempt.item_id.encode(),
            ),
        )
        newly_covered = tuple(
            sorted(set(chosen.annotator_ids) - covered, key=lambda value: value.encode())
        )
        supplements.append((annotator_id, chosen.item_id, newly_covered))
        processing.append((annotator_id, chosen.item_id, "selected_supplement"))
        selected.add(chosen.item_id)
        covered.update(chosen.annotator_ids)
    return supplements, processing


def indexed_supplement_summary(
    ordered_attempts: list[Attempt], main_attempts: list[Attempt], seed: bytes
) -> tuple[list[tuple[str, str, tuple[str, ...]]], list[tuple[str, str | None, str]]]:
    supplements, processing, _, _, uncovered = _select_supplements_indexed(
        ordered_attempts, main_attempts, seed
    )
    if uncovered:
        raise AssertionError("indexed selector left an annotator uncovered")
    supplement_summary = [
        (
            entry["selected_for_annotator_id"],
            entry["item_id"],
            tuple(entry["newly_covered_annotator_ids"]),
        )
        for entry in supplements
    ]
    processing_summary = [
        (entry["annotator_id"], entry["selected_item_id"], entry["status"])
        for entry in processing
    ]
    return supplement_summary, processing_summary


class HamiltonTests(unittest.TestCase):
    def test_largest_remainder_tie_uses_utf8_cell_order(self) -> None:
        capacities = {"cell_b": 3, "cell_a": 3, "cell_c": 2}
        self.assertEqual(
            allocate_hamilton(capacities, 5),
            {"cell_a": 2, "cell_b": 2, "cell_c": 1},
        )

    def test_capacity_constraints_and_full_allocation(self) -> None:
        capacities = {"cell_a": 1, "cell_b": 7, "cell_c": 2}
        allocation = allocate_hamilton(capacities, 9)
        self.assertEqual(sum(allocation.values()), 9)
        self.assertEqual(allocation["cell_a"], 1)
        self.assertTrue(all(allocation[key] <= capacities[key] for key in capacities))
        self.assertEqual(allocate_hamilton(capacities, 10), capacities)

    def test_invalid_hamilton_inputs_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            allocate_hamilton({}, 0)
        with self.assertRaises(ValueError):
            allocate_hamilton({"cell": 0}, 1)
        with self.assertRaises(ValueError):
            allocate_hamilton({"cell": 1}, 0)
        with self.assertRaises(ValueError):
            allocate_hamilton({"céll": 1}, 1)
        with self.assertRaises(ValueError):
            allocate_hamilton({"cell": 1}, True)


class HmacTests(unittest.TestCase):
    def test_known_answer_matches_independent_openssl_vector(self) -> None:
        digest = hmac_rank_digest(
            bytes.fromhex(SEED_HEX),
            "hindi|phishing|tester_authored_simulation",
            "item_known_answer",
        )
        self.assertEqual(
            digest.hex(),
            "0319fd229051239edb19c0d07f2fd004685a2a452adbc6a90f3752cc19bcf808",
        )

    def test_hmac_rejects_non_32_byte_key(self) -> None:
        with self.assertRaises(ValueError):
            hmac_rank_digest(b"short", "cell", "item_test")


class SupplementIndexEquivalenceTests(unittest.TestCase):
    def test_exhaustive_main_subsets_match_slow_reference(self) -> None:
        seed = bytes.fromhex(SEED_HEX)
        attempts = [
            make_attempt(
                1,
                ("annotator_a", "annotator_b", "annotator_c"),
            ),
            make_attempt(
                2,
                ("annotator_a", "annotator_d", "annotator_e"),
            ),
            make_attempt(
                3,
                ("annotator_b", "annotator_d", "annotator_f"),
            ),
            make_attempt(
                4,
                ("annotator_c", "annotator_e", "annotator_g"),
            ),
            make_attempt(
                5,
                ("annotator_f", "annotator_g", "annotator_h"),
            ),
        ]
        for main_size in range(len(attempts) + 1):
            for main_tuple in combinations(attempts, main_size):
                with self.subTest(
                    main_item_ids=tuple(value.item_id for value in main_tuple)
                ):
                    expected = slow_supplement_reference(
                        attempts, list(main_tuple), seed
                    )
                    actual = indexed_supplement_summary(
                        attempts, list(main_tuple), seed
                    )
                    self.assertEqual(actual, expected)

    def test_randomized_annotation_graphs_match_slow_reference(self) -> None:
        seed = bytes.fromhex(SEED_HEX)
        generator = random.Random(20260819)
        annotators = [f"annotator_{letter}" for letter in "abcdefghijklmno"]
        for case in range(100):
            attempts: list[Attempt] = []
            for index in range(1, generator.randint(4, 25)):
                chosen = generator.sample(annotators, 3)
                blind = sorted(chosen[:2], key=lambda value: value.encode())
                attempts.append(
                    make_attempt(
                        case * 100 + index,
                        (blind[0], blind[1], chosen[2]),
                    )
                )
            main_attempts = [
                attempt for attempt in attempts if generator.random() < 0.35
            ]
            with self.subTest(case=case, attempted=len(attempts)):
                self.assertEqual(
                    indexed_supplement_summary(attempts, main_attempts, seed),
                    slow_supplement_reference(attempts, main_attempts, seed),
                )


class SelectorTests(unittest.TestCase):
    def test_all_sixty_cells_are_covered_with_exact_ten_percent(self) -> None:
        records: list[dict] = []
        index = 0
        for language in LANGUAGES:
            for primary in PRIMARY_STATES:
                for provenance in PROVENANCE_CLASSES:
                    for _ in range(20):
                        index += 1
                        records.append(
                            attempt_record(
                                index,
                                language=language,
                                primary=primary,
                                provenance=provenance,
                            )
                        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "attempts.jsonl"
            write_jsonl(path, records)
            report = rehearse_file(path, SEED_HEX)

        self.assertTrue(report.structurally_valid)
        self.assertEqual(report.attempted_items, 1_200)
        self.assertEqual(report.prescribed_ten_percent_n, 120)
        self.assertEqual(report.nonempty_cells, 60)
        self.assertEqual(report.main_selected_count, 120)
        self.assertFalse(report.fallback_entire_universe)
        self.assertEqual(
            {value["main_selected"] for value in report.cell_allocations.values()},
            {2},
        )
        self.assertEqual(len({value["cell_key"] for value in report.main_sample}), 60)

    def test_realistic_1203_attempt_universe_uses_ceil(self) -> None:
        records: list[dict] = []
        index = 0
        for language in LANGUAGES[:4]:
            for primary in PRIMARY_STATES[:2]:
                for cell_index in range(150):
                    index += 1
                    if cell_index % 5 == 0:
                        provenance = "llm_drafted_human_edited"
                    elif cell_index % 2 == 0:
                        provenance = "tester_donated_authentic"
                    else:
                        provenance = "tester_authored_simulation"
                    records.append(
                        attempt_record(
                            index,
                            language=language,
                            primary=primary,
                            provenance=provenance,
                        )
                    )
        records.extend(
            [
                attempt_record(1_201, language="uncertain", primary="benign"),
                attempt_record(1_202, language="hindi", primary="uncertain"),
                attempt_record(1_203, language="uncertain", primary="uncertain"),
            ]
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "attempts.jsonl"
            write_jsonl(path, records)
            report = rehearse_file(path, SEED_HEX)

        self.assertTrue(report.structurally_valid)
        self.assertEqual(report.attempted_items, 1_203)
        self.assertEqual(report.prescribed_ten_percent_n, 121)
        self.assertEqual(report.main_selected_count, 121)
        self.assertFalse(report.fallback_entire_universe)
        self.assertEqual(len({entry["item_id"] for entry in report.main_sample}), 121)

    def test_small_universe_selects_every_item_and_blocks_rule(self) -> None:
        report = rehearse_file(
            ROOT / "examples/audit/attempts.synthetic.jsonl", SEED_HEX
        )
        self.assertTrue(report.structurally_valid)
        self.assertEqual(report.attempted_items, 12)
        self.assertEqual(report.prescribed_ten_percent_n, 2)
        self.assertEqual(report.main_selected_count, 12)
        self.assertTrue(report.fallback_entire_universe)
        self.assertTrue(report.revised_sampling_rule_required)
        self.assertIn("protocol_bound_fallback", diagnostic_codes(report))

    def test_one_supplement_can_cover_three_missing_annotators(self) -> None:
        seed = bytes.fromhex(SEED_HEX)
        records = [attempt_record(index) for index in range(1, 1_201)]
        cell_key = "hindi|benign|tester_authored_simulation"
        rare_record = max(
            records,
            key=lambda value: hmac_rank_digest(seed, cell_key, value["item_id"]),
        )
        rare_record["blind_annotator_ids"] = ["annotator_rare_a", "annotator_rare_b"]
        rare_record["final_annotator_id"] = "annotator_rare_c"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "attempts.jsonl"
            write_jsonl(path, records)
            report = rehearse_file(path, SEED_HEX)

        self.assertTrue(report.structurally_valid)
        self.assertEqual(report.main_selected_count, 120)
        self.assertEqual(report.supplement_selected_count, 1)
        self.assertEqual(len(report.initially_missing_annotator_ids), 3)
        self.assertEqual(len(report.supplement_processing), 3)
        self.assertEqual(
            [value["status"] for value in report.supplement_processing],
            [
                "selected_supplement",
                "skipped_already_covered",
                "skipped_already_covered",
            ],
        )
        self.assertEqual(
            [value["selected_item_id"] for value in report.supplement_processing],
            [rare_record["item_id"], None, None],
        )
        self.assertEqual(
            set(report.final_covered_annotator_ids),
            {
                "annotator_alpha",
                "annotator_beta",
                "annotator_final",
                "annotator_rare_a",
                "annotator_rare_b",
                "annotator_rare_c",
            },
        )
        self.assertEqual(report.final_uncovered_annotator_ids, ())
        rendered = format_text(report)
        self.assertIn("annotator_rare_a:selected_supplement", rendered)
        self.assertIn("annotator_rare_b:skipped_already_covered:none", rendered)
        self.assertIn("final_covered_annotator_ids:", rendered)
        self.assertEqual(
            report.supplements[0]["newly_covered_annotator_ids"],
            ["annotator_rare_a", "annotator_rare_b", "annotator_rare_c"],
        )
        self.assertNotIn(
            report.supplements[0]["item_id"],
            {value["item_id"] for value in report.main_sample},
        )

    def test_supplement_uses_lowest_digest_among_unselected_candidates(self) -> None:
        seed = bytes.fromhex(SEED_HEX)
        records = [attempt_record(index) for index in range(1, 1_201)]
        cell_key = "hindi|benign|tester_authored_simulation"
        ranked_high_to_low = sorted(
            records,
            key=lambda value: hmac_rank_digest(seed, cell_key, value["item_id"]),
            reverse=True,
        )
        candidates = ranked_high_to_low[:2]
        for record in candidates:
            record["blind_annotator_ids"] = ["annotator_alpha", "annotator_rare"]
        expected = min(
            candidates,
            key=lambda value: hmac_rank_digest(seed, cell_key, value["item_id"]),
        )["item_id"]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "attempts.jsonl"
            write_jsonl(path, records)
            report = rehearse_file(path, SEED_HEX)

        self.assertTrue(report.structurally_valid)
        self.assertEqual(report.supplement_selected_count, 1)
        self.assertEqual(report.supplements[0]["item_id"], expected)

    def test_canonical_selection_is_invariant_to_row_order(self) -> None:
        records = [attempt_record(index) for index in range(1, 1_201)]
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first.jsonl"
            second = Path(directory) / "second.jsonl"
            write_jsonl(first, records)
            write_jsonl(second, list(reversed(records)))
            report_a = rehearse_file(first, SEED_HEX)
            report_b = rehearse_file(second, SEED_HEX)

        self.assertNotEqual(report_a.input_file_sha256, report_b.input_file_sha256)
        self.assertEqual(
            report_a.canonical_universe_sha256, report_b.canonical_universe_sha256
        )
        self.assertEqual(report_a.main_manifest_sha256, report_b.main_manifest_sha256)
        self.assertEqual(
            report_a.selection_manifest_sha256, report_b.selection_manifest_sha256
        )

    def test_json_format_is_byte_deterministic_and_explicitly_limited(self) -> None:
        path = ROOT / "examples/audit/attempts.synthetic.jsonl"
        report_a = rehearse_file(path, SEED_HEX)
        report_b = rehearse_file(path, SEED_HEX)
        output_a = format_json(report_a).encode("utf-8")
        output_b = format_json(report_b).encode("utf-8")
        self.assertEqual(output_a, output_b)
        parsed = json.loads(output_a)
        self.assertEqual(parsed["schema_version"], SCHEMA_VERSION)
        self.assertEqual(parsed["scope"], SCOPE)
        self.assertTrue(parsed["release_blocked"])
        for entry in parsed["main_sample"] + parsed["supplements"]:
            self.assertEqual(entry["scope"], SCOPE)
            self.assertTrue(entry["release_blocked"])
        main_envelope = {
            "algorithm_version": ALGORITHM_VERSION,
            "entries": parsed["main_sample"],
            "manifest_kind": "main_sample",
            "release_blocked": True,
            "schema_version": SCHEMA_VERSION,
            "scope": SCOPE,
        }
        supplement_envelope = {
            "algorithm_version": ALGORITHM_VERSION,
            "entries": parsed["supplements"],
            "manifest_kind": "annotator_supplements",
            "release_blocked": True,
            "schema_version": SCHEMA_VERSION,
            "scope": SCOPE,
        }
        self.assertEqual(parsed["main_manifest_sha256"], canonical_hash(main_envelope))
        self.assertEqual(
            parsed["supplement_manifest_sha256"],
            canonical_hash(supplement_envelope),
        )
        selection_envelope = {
            "algorithm_version": ALGORITHM_VERSION,
            "canonical_universe_sha256": parsed["canonical_universe_sha256"],
            "cell_allocations": parsed["cell_allocations"],
            "fallback_entire_universe": parsed["fallback_entire_universe"],
            "final_covered_annotator_ids": parsed["final_covered_annotator_ids"],
            "final_uncovered_annotator_ids": parsed["final_uncovered_annotator_ids"],
            "initially_missing_annotator_ids": parsed[
                "initially_missing_annotator_ids"
            ],
            "main_sample": parsed["main_sample"],
            "prescribed_ten_percent_n": parsed["prescribed_ten_percent_n"],
            "release_blocked": True,
            "schema_version": SCHEMA_VERSION,
            "scope": SCOPE,
            "seed_hex": parsed["seed_hex"],
            "supplement_processing": parsed["supplement_processing"],
            "supplements": parsed["supplements"],
        }
        self.assertEqual(
            parsed["selection_manifest_sha256"], canonical_hash(selection_envelope)
        )
        self.assertEqual(
            set(parsed["limitations"]),
            {
                "CANNOT_CERTIFY_HUMAN_AUDIT",
                "CANNOT_CERTIFY_CSPRNG_WITNESSING",
                "CANNOT_CERTIFY_FROZEN_HASHES",
                "CANNOT_CERTIFY_ATTEMPTED_UNIVERSE_COMPLETENESS",
                "CANNOT_CERTIFY_GOVERNANCE_APPROVAL",
                "CANNOT_CERTIFY_ZERO_PROHIBITED_FINDINGS",
            },
        )


class ValidationSafetyTests(unittest.TestCase):
    def _report_for_raw(self, raw: bytes, seed: str = SEED_HEX):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "attempts.jsonl"
            path.write_bytes(raw)
            return rehearse_file(path, seed)

    def test_duplicate_json_key_is_rejected_without_value_echo(self) -> None:
        raw = (
            b'{"schema_version":"1.0.0","schema_version":"unsafe.example"}\n'
        )
        report = self._report_for_raw(raw)
        rendered = format_text(report)
        self.assertIn("duplicate_json_key", diagnostic_codes(report))
        self.assertNotIn("unsafe.example", rendered)

    @unittest.skipIf(sys.platform == "win32", "POSIX-only filesystem feature")
    def test_non_regular_inputs_are_rejected_before_reading(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            regular = root / "regular.jsonl"
            write_jsonl(regular, [attempt_record(1)])
            symlink = root / "linked.jsonl"
            symlink.symlink_to(regular)
            fifo = root / "attempts.fifo"
            os.mkfifo(fifo)
            for path in (root, symlink, fifo):
                with self.subTest(kind=path.name):
                    report = rehearse_file(path, SEED_HEX)
                    self.assertFalse(report.structurally_valid)
                    self.assertEqual(
                        diagnostic_codes(report), {"input_not_regular_file"}
                    )
                    rendered = format_text(report)
                    self.assertNotIn(str(path), rendered)

    def test_nonfinite_json_bom_blank_and_operational_bounds_are_rejected(self) -> None:
        record_bytes = (json.dumps(attempt_record(1)) + "\n").encode("utf-8")
        self.assertIn(
            "nonfinite_json",
            diagnostic_codes(self._report_for_raw(b'{"value":NaN}\n')),
        )
        bom_report = self._report_for_raw(b"\xef\xbb\xbf" + record_bytes)
        self.assertIn("utf8_bom", diagnostic_codes(bom_report))
        self.assertIn("blank_line", diagnostic_codes(self._report_for_raw(b"\n" + record_bytes)))
        with patch("fisher_audit.selector.MAX_FILE_BYTES", len(record_bytes) - 1):
            self.assertIn("file_too_large", diagnostic_codes(self._report_for_raw(record_bytes)))
        with patch("fisher_audit.selector.MAX_LINE_BYTES", 8):
            self.assertIn("line_too_large", diagnostic_codes(self._report_for_raw(record_bytes)))
        two_records = record_bytes + (
            json.dumps(attempt_record(2)) + "\n"
        ).encode("utf-8")
        with patch("fisher_audit.selector.MAX_RECORDS", 1):
            self.assertIn("record_limit", diagnostic_codes(self._report_for_raw(two_records)))

    def test_unknown_message_and_live_route_are_rejected_without_echo(self) -> None:
        record = attempt_record(1)
        record["message_text"] = "visit https://unsafe.example and send OTP 123456"
        report = self._report_for_raw(
            (json.dumps(record, separators=(",", ":")) + "\n").encode("utf-8")
        )
        rendered = format_text(report)
        self.assertIn("record_fields", diagnostic_codes(report))
        self.assertNotIn("unsafe.example", rendered)
        self.assertNotIn("123456", rendered)

    def test_non_synthetic_record_scope_is_rejected(self) -> None:
        record = attempt_record(1)
        record["scope"] = "REAL_AUTHENTIC_AUDIT"
        report = self._report_for_raw(
            (json.dumps(record, separators=(",", ":")) + "\n").encode("utf-8")
        )
        self.assertIn("non_synthetic_scope", diagnostic_codes(report))
        self.assertNotIn("REAL_AUTHENTIC_AUDIT", format_text(report))

    def test_unicode_identifier_and_malformed_utf8_are_rejected(self) -> None:
        record = attempt_record(1)
        record["item_id"] = "item_हिंदी"
        unicode_report = self._report_for_raw(
            (json.dumps(record, ensure_ascii=False) + "\n").encode("utf-8")
        )
        malformed_report = self._report_for_raw(b'{"item_id":"\xff"}\n')
        self.assertIn("item_id", diagnostic_codes(unicode_report))
        self.assertIn("invalid_utf8", diagnostic_codes(malformed_report))

    def test_seed_must_be_exact_lowercase_32_byte_hex(self) -> None:
        raw = (json.dumps(attempt_record(1)) + "\n").encode("utf-8")
        for seed in ("00" * 31, "00" * 33, SEED_HEX.upper(), "g0" * 32):
            with self.subTest(seed_length=len(seed)):
                report = self._report_for_raw(raw, seed)
                self.assertIn("seed_hex", diagnostic_codes(report))
                self.assertIsNone(report.seed_hex)

    def test_annotation_cardinality_order_and_distinctness_are_enforced(self) -> None:
        base = attempt_record(1)
        cases = []
        wrong_count = deepcopy(base)
        wrong_count["blind_annotator_ids"] = ["annotator_alpha"]
        cases.append((wrong_count, "blind_annotator_ids"))
        wrong_order = deepcopy(base)
        wrong_order["blind_annotator_ids"] = ["annotator_beta", "annotator_alpha"]
        cases.append((wrong_order, "blind_annotator_ids_order_or_uniqueness"))
        repeated_final = deepcopy(base)
        repeated_final["final_annotator_id"] = "annotator_alpha"
        cases.append((repeated_final, "annotators_not_distinct"))
        for record, code in cases:
            with self.subTest(code=code):
                report = self._report_for_raw(
                    (json.dumps(record, separators=(",", ":")) + "\n").encode()
                )
                self.assertIn(code, diagnostic_codes(report))

    def test_partition_and_final_state_coherence_is_enforced(self) -> None:
        pilot_uncertain = attempt_record(1, language="uncertain")
        pilot_uncertain["simulated_partition"] = "pilot"
        excluded_resolved = attempt_record(2)
        excluded_resolved["simulated_partition"] = "excluded"
        for record, code in (
            (pilot_uncertain, "pilot_final_state"),
            (excluded_resolved, "excluded_final_state"),
        ):
            with self.subTest(code=code):
                report = self._report_for_raw(
                    (json.dumps(record, separators=(",", ":")) + "\n").encode()
                )
                self.assertIn(code, diagnostic_codes(report))

    def test_duplicate_item_and_bundle_hashes_are_rejected(self) -> None:
        first = attempt_record(1)
        duplicate_item = attempt_record(2)
        duplicate_item["item_id"] = first["item_id"]
        duplicate_bundle = attempt_record(3)
        duplicate_bundle["synthetic_bundle_sha256"] = first["synthetic_bundle_sha256"]
        report = self._report_for_raw(
            "".join(
                json.dumps(value, separators=(",", ":")) + "\n"
                for value in (first, duplicate_item, duplicate_bundle)
            ).encode()
        )
        self.assertIn("duplicate_item_id", diagnostic_codes(report))
        self.assertIn("duplicate_bundle_sha256", diagnostic_codes(report))

    def test_non_string_enums_do_not_crash_validator(self) -> None:
        record = attempt_record(1)
        record["simulated_provenance_class"] = ["not", "a", "string"]
        report = self._report_for_raw(
            (json.dumps(record, separators=(",", ":")) + "\n").encode()
        )
        self.assertFalse(report.structurally_valid)
        self.assertIn("provenance_class", diagnostic_codes(report))


class CliTests(unittest.TestCase):
    def _run(self, *arguments: str) -> subprocess.CompletedProcess[bytes]:
        environment = dict(os.environ)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [sys.executable, "-m", "fisher_audit", *arguments],
            cwd=ROOT,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def test_cli_json_output_is_identical_across_runs(self) -> None:
        arguments = (
            "rehearse",
            "--attempts",
            "examples/audit/attempts.synthetic.jsonl",
            "--seed-hex",
            SEED_HEX,
            "--scope",
            SCOPE,
            "--format",
            "json",
        )
        first = self._run(*arguments)
        second = self._run(*arguments)
        self.assertEqual(first.returncode, 0)
        self.assertEqual(second.returncode, 0)
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(first.stderr, b"")
        parsed = json.loads(first.stdout)
        self.assertEqual(parsed["scope"], SCOPE)
        self.assertTrue(parsed["release_blocked"])

    def test_cli_refuses_real_scope_without_echoing_it(self) -> None:
        unsafe_scope = "REAL_AUDIT_https://unsafe.example/123456"
        result = self._run(
            "rehearse",
            "--attempts",
            "examples/audit/attempts.synthetic.jsonl",
            "--seed-hex",
            SEED_HEX,
            "--scope",
            unsafe_scope,
            "--format",
            "text",
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn(SCOPE.encode(), result.stdout)
        self.assertIn(b"non_synthetic_scope", result.stdout)
        self.assertNotIn(unsafe_scope.encode(), result.stdout + result.stderr)

    def test_cli_sanitizes_malformed_argument_errors(self) -> None:
        unsafe_argument = "--unsafe=https://unsafe.example/123456"
        result = self._run("rehearse", unsafe_argument)
        self.assertEqual(result.returncode, 2)
        self.assertIn(b"cli_usage", result.stdout)
        self.assertNotIn(unsafe_argument.encode(), result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
