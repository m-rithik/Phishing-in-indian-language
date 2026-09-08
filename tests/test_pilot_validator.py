from __future__ import annotations

from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
from pathlib import Path
import tempfile
import unittest

from fisher_pilot.cli import main
from fisher_pilot.validator import LANGUAGE_STRATA, validate_files


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in rows),
        encoding="utf-8",
    )


def _source(
    source_id: str = "src-001",
    *,
    consent_reference: str = "consent-001",
    collection_batch_id: str = "batch-001",
    provenance_class: str = "tester_authored_simulation",
) -> dict[str, object]:
    return {
        "schema_version": "0.1.0",
        "source_id": source_id,
        "provenance_class": provenance_class,
        "consent_status": "granted",
        "consent_reference": consent_reference,
        "collection_batch_id": collection_batch_id,
        "internal_research_permitted": True,
        "release_tier": "internal_only",
        "source_status": "active",
    }


def _item(
    item_id: str = "item-001",
    *,
    text: str = "Yeh ek surakshit synthetic sandesh hai.",
    label: str = "benign",
    stratum: str = "hindi",
    component: str = "component-001",
    resolution: str = "blind_agreement",
) -> dict[str, object]:
    return {
        "schema_version": "0.1.0",
        "item_id": item_id,
        "source_id": "src-001",
        "text": text,
        "content_sha256": sha256(text.encode("utf-8")).hexdigest(),
        "language_stratum": stratum,
        "final_label": label,
        "label_resolution": resolution,
        "leakage_component_id": component,
        "romanized_indic": stratum == "hindi",
        "romanization_ambiguous": False,
        "artifact_review": {"status": "passed", "representation": "none"},
        "privacy_review": True,
        "partition": "pilot",
    }


def _annotation(
    annotation_id: str,
    annotator_id: str,
    *,
    item_id: str = "item-001",
    label: str = "benign",
    stratum: str = "hindi",
    kind: str = "blind",
) -> dict[str, object]:
    return {
        "schema_version": "0.1.0",
        "annotation_id": annotation_id,
        "item_id": item_id,
        "annotator_id": annotator_id,
        "kind": kind,
        "primary_label": label,
        "language_stratum": stratum,
        "confidence": "high",
    }


class Fixture:
    def __enter__(self) -> "Fixture":
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.sources_path = self.root / "sources-private-name.jsonl"
        self.items_path = self.root / "items-private-name.jsonl"
        self.annotations_path = self.root / "annotations-private-name.jsonl"
        return self

    def write(
        self,
        sources: list[dict[str, object]],
        items: list[dict[str, object]],
        annotations: list[dict[str, object]],
    ) -> None:
        _write_jsonl(self.sources_path, sources)
        _write_jsonl(self.items_path, items)
        _write_jsonl(self.annotations_path, annotations)

    def __exit__(self, *args: object) -> None:
        self.temporary.cleanup()


def _valid_draft() -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    return (
        [_source()],
        [_item()],
        [_annotation("ann-001", "annotator-a"), _annotation("ann-002", "annotator-b")],
    )


class PilotSchemaAndWorkflowTests(unittest.TestCase):
    def test_small_draft_is_valid_with_readiness_warnings(self) -> None:
        with Fixture() as fixture:
            fixture.write(*_valid_draft())
            result = validate_files(
                fixture.sources_path, fixture.items_path, fixture.annotations_path, mode="draft"
            )
        self.assertTrue(result.valid)
        self.assertGreater(result.report["counts"]["warnings"], 0)

    def test_exact_schema_and_source_authorization_are_required(self) -> None:
        sources, items, annotations = _valid_draft()
        sources[0]["person_name"] = "must-not-be-here"
        with Fixture() as fixture:
            fixture.write(sources, items, annotations)
            result = validate_files(
                fixture.sources_path, fixture.items_path, fixture.annotations_path
            )
        codes = {diagnostic.code for diagnostic in result.diagnostics}
        self.assertIn("schema_keys", codes)
        self.assertIn("unknown_foreign_key", codes)

        sources, items, annotations = _valid_draft()
        sources[0]["consent_status"] = "pending"
        with Fixture() as fixture:
            fixture.write(sources, items, annotations)
            result = validate_files(
                fixture.sources_path, fixture.items_path, fixture.annotations_path
            )
        self.assertIn("source_authorization", {d.code for d in result.diagnostics})

    def test_duplicate_json_keys_and_nonfinite_numbers_are_rejected(self) -> None:
        sources, items, annotations = _valid_draft()
        with Fixture() as fixture:
            fixture.write(sources, items, annotations)
            fixture.sources_path.write_text(
                '{"schema_version":"0.1.0","schema_version":"0.1.0"}\n',
                encoding="utf-8",
            )
            duplicate = validate_files(
                fixture.sources_path, fixture.items_path, fixture.annotations_path
            )
        self.assertIn("invalid_json", {d.code for d in duplicate.diagnostics})

        sources, items, annotations = _valid_draft()
        with Fixture() as fixture:
            fixture.write(sources, items, annotations)
            fixture.annotations_path.write_text(
                json.dumps(annotations[0], separators=(",", ":")).replace(
                    '"confidence":"high"', '"confidence":NaN'
                )
                + "\n",
                encoding="utf-8",
            )
            nonfinite = validate_files(
                fixture.sources_path, fixture.items_path, fixture.annotations_path
            )
        self.assertIn("invalid_json", {d.code for d in nonfinite.diagnostics})

    def test_json_numbers_physical_record_bound_crlf_and_raw_line_separator(self) -> None:
        sources, items, annotations = _valid_draft()
        with Fixture() as fixture:
            fixture.write(sources, items, annotations)
            fixture.sources_path.write_text(
                '{"schema_version":"0.1.0","numeric":' + "9" * 5_000 + "}\n",
                encoding="utf-8",
            )
            numeric = validate_files(
                fixture.sources_path, fixture.items_path, fixture.annotations_path
            )
        self.assertIn("invalid_json", {d.code for d in numeric.diagnostics})

        with Fixture() as fixture:
            fixture.write(sources, items, annotations)
            fixture.sources_path.write_bytes(b"\n" * 3_000)
            bounded = validate_files(
                fixture.sources_path, fixture.items_path, fixture.annotations_path
            )
        self.assertIn("row_bound", {d.code for d in bounded.diagnostics})
        self.assertNotIn("blank_line", {d.code for d in bounded.diagnostics})

        sources, items, annotations = _valid_draft()
        items[0]["text"] = "Safe raw line separator\u2028inside text"
        items[0]["content_sha256"] = sha256(items[0]["text"].encode()).hexdigest()
        with Fixture() as fixture:
            fixture.write(sources, items, annotations)
            fixture.sources_path.write_bytes(fixture.sources_path.read_bytes().replace(b"\n", b"\r\n"))
            fixture.items_path.write_bytes(fixture.items_path.read_bytes().replace(b"\n", b"\r\n"))
            fixture.annotations_path.write_bytes(
                fixture.annotations_path.read_bytes().replace(b"\n", b"\r\n")
            )
            crlf = validate_files(
                fixture.sources_path, fixture.items_path, fixture.annotations_path
            )
        self.assertTrue(crlf.valid, crlf.report["diagnostics"])

    def test_symlink_input_is_rejected(self) -> None:
        with Fixture() as fixture:
            fixture.write(*_valid_draft())
            link = fixture.root / "sources-link.jsonl"
            link.symlink_to(fixture.sources_path)
            result = validate_files(link, fixture.items_path, fixture.annotations_path)
        self.assertIn("file_not_regular", {d.code for d in result.diagnostics})

    def test_hash_and_romanization_invariant_are_enforced(self) -> None:
        sources, items, annotations = _valid_draft()
        items[0]["content_sha256"] = "0" * 64
        items[0]["romanized_indic"] = False
        items[0]["romanization_ambiguous"] = True
        with Fixture() as fixture:
            fixture.write(sources, items, annotations)
            result = validate_files(
                fixture.sources_path, fixture.items_path, fixture.annotations_path
            )
        self.assertTrue(
            {"content_hash_mismatch", "romanization_invariant"}
            <= {diagnostic.code for diagnostic in result.diagnostics}
        )

    def test_schema_version_is_exact(self) -> None:
        sources, items, annotations = _valid_draft()
        sources[0]["schema_version"] = "0.1"
        with Fixture() as fixture:
            fixture.write(sources, items, annotations)
            result = validate_files(
                fixture.sources_path, fixture.items_path, fixture.annotations_path
            )
        self.assertIn("schema_version", {d.code for d in result.diagnostics})

    def test_disagreement_requires_distinct_adjudication_and_matching_outcome(self) -> None:
        sources, items, annotations = _valid_draft()
        items[0]["label_resolution"] = "adjudicated"
        items[0]["final_label"] = "phishing"
        annotations[1]["primary_label"] = "uncertain"
        annotations.append(
            _annotation(
                "ann-003", "annotator-c", label="phishing", stratum="hindi", kind="adjudication"
            )
        )
        with Fixture() as fixture:
            fixture.write(sources, items, annotations)
            valid = validate_files(
                fixture.sources_path, fixture.items_path, fixture.annotations_path
            )
        self.assertTrue(valid.valid)
        self.assertEqual(valid.report["readiness"]["uncertainty_items"], 1)

        annotations[-1]["annotator_id"] = "annotator-a"
        with Fixture() as fixture:
            fixture.write(sources, items, annotations)
            invalid = validate_files(
                fixture.sources_path, fixture.items_path, fixture.annotations_path
            )
        self.assertIn("adjudicator_not_distinct", {d.code for d in invalid.diagnostics})

    def test_agreement_forbids_adjudication(self) -> None:
        sources, items, annotations = _valid_draft()
        annotations.append(_annotation("ann-003", "annotator-c", kind="adjudication"))
        with Fixture() as fixture:
            fixture.write(sources, items, annotations)
            result = validate_files(
                fixture.sources_path, fixture.items_path, fixture.annotations_path
            )
        self.assertIn("unexpected_adjudication", {d.code for d in result.diagnostics})


class PilotSafetyTests(unittest.TestCase):
    def _validate_text(self, text: str) -> set[str]:
        sources, items, annotations = _valid_draft()
        items[0]["text"] = text
        items[0]["content_sha256"] = sha256(text.encode("utf-8")).hexdigest()
        with Fixture() as fixture:
            fixture.write(sources, items, annotations)
            result = validate_files(
                fixture.sources_path, fixture.items_path, fixture.annotations_path
            )
        return {diagnostic.code for diagnostic in result.diagnostics}

    def test_live_residual_and_credentials_are_rejected(self) -> None:
        cases = {
            "Open https://bank.example/path": "recognized_live_artifact",
            "Open bank . example now": "residual_artifact_candidate",
            "Your OTP is 482913": "credential_candidate",
            "Account number 123456789012": "financial_identifier_candidate",
            "password: realSecret42": "credential_candidate",
        }
        for text, code in cases.items():
            with self.subTest(code=code):
                self.assertIn(code, self._validate_text(text))

    def test_safety_normalization_controls_and_cross_line_credentials(self) -> None:
        cases = {
            "Open h\u200bttps://bank.example/path": "recognized_live_artifact",
            "Write user@\u200bexample.com": "recognized_live_artifact",
            "abc\u202edef": "bidi_control",
            "OTP\n123456": "credential_candidate",
            "OTP 1 2 3 4 5 6": "credential_candidate",
            "CVV\r\n123": "credential_candidate",
            "Account\n12345678": "financial_identifier_candidate",
            "O\u200bTP\n1\u200b2\u200b3\u200b4": "credential_candidate",
            " \u200b\t ": "effectively_empty_text",
            "safe\x01text": "disallowed_control",
        }
        for text, code in cases.items():
            with self.subTest(code=code, text=repr(text)):
                self.assertIn(code, self._validate_text(text))

        codes = self._validate_text("Ｆｕｌｌｗｉｄｔｈ Ａ is ordinary text")
        self.assertNotIn("recognized_live_artifact", codes)
        self.assertNotIn("invalid_text", codes)

    def test_default_ignorables_cannot_hide_empty_artifact_or_credential_text(self) -> None:
        cases = {
            "\u034f": "effectively_empty_text",
            "O\u034fTP is 123456": "credential_candidate",
            "Call 98765\u034f43210": "recognized_live_artifact",
            "pass\ufe0fword: test-only-secret": "credential_candidate",
            "O\U00013430TP is 123456": "credential_candidate",
            "\u180b\U000e0100": "effectively_empty_text",
        }
        for text, code in cases.items():
            with self.subTest(code=code, text=repr(text)):
                self.assertIn(code, self._validate_text(text))

        fullwidth_codes = self._validate_text("Ｆｕｌｌｗｉｄｔｈ Ａ remains visible")
        self.assertNotIn("recognized_live_artifact", fullwidth_codes)
        self.assertNotIn("effectively_empty_text", fullwidth_codes)

    def test_typed_placeholder_representation_is_coherent(self) -> None:
        sources, items, annotations = _valid_draft()
        items[0]["text"] = "Open [URL] only after review"
        items[0]["content_sha256"] = sha256(items[0]["text"].encode()).hexdigest()
        items[0]["artifact_review"] = {"status": "passed", "representation": "none"}
        with Fixture() as fixture:
            fixture.write(sources, items, annotations)
            none_result = validate_files(
                fixture.sources_path, fixture.items_path, fixture.annotations_path
            )
        self.assertIn("artifact_representation_mismatch", {d.code for d in none_result.diagnostics})

        items[0]["text"] = "No typed artifact appears"
        items[0]["content_sha256"] = sha256(items[0]["text"].encode()).hexdigest()
        items[0]["artifact_review"] = {
            "status": "passed",
            "representation": "typed_placeholders",
        }
        with Fixture() as fixture:
            fixture.write(sources, items, annotations)
            typed_result = validate_files(
                fixture.sources_path, fixture.items_path, fixture.annotations_path
            )
        self.assertIn(
            "artifact_representation_mismatch", {d.code for d in typed_result.diagnostics}
        )

    def test_source_consent_and_batch_are_component_contained(self) -> None:
        sources, items, annotations = _valid_draft()
        items.append(_item("item-002", text="Second synthetic text", component="component-002"))
        annotations.extend(
            [
                _annotation("ann-003", "annotator-a", item_id="item-002"),
                _annotation("ann-004", "annotator-b", item_id="item-002"),
            ]
        )
        with Fixture() as fixture:
            fixture.write(sources, items, annotations)
            source_result = validate_files(
                fixture.sources_path, fixture.items_path, fixture.annotations_path
            )
        self.assertIn("source_component_conflict", {d.code for d in source_result.diagnostics})

        sources.append(
            _source(
                "src-002",
                consent_reference="consent-001",
                collection_batch_id="batch-001",
            )
        )
        items[1]["source_id"] = "src-002"
        with Fixture() as fixture:
            fixture.write(sources, items, annotations)
            mapping_result = validate_files(
                fixture.sources_path, fixture.items_path, fixture.annotations_path
            )
        codes = {d.code for d in mapping_result.diagnostics}
        self.assertIn("consent_component_conflict", codes)
        self.assertIn("batch_component_conflict", codes)

    def test_normalized_unicode_duplicate_requires_one_component(self) -> None:
        sources, items, annotations = _valid_draft()
        first = items[0]
        first["text"] = "PAY\u200b NOW"
        first["content_sha256"] = sha256(first["text"].encode()).hexdigest()
        second = _item(
            "item-002", text="pay now", component="component-002", label="benign", stratum="hindi"
        )
        items.append(second)
        annotations.extend(
            [
                _annotation("ann-003", "annotator-a", item_id="item-002"),
                _annotation("ann-004", "annotator-b", item_id="item-002"),
            ]
        )
        with Fixture() as fixture:
            fixture.write(sources, items, annotations)
            result = validate_files(
                fixture.sources_path, fixture.items_path, fixture.annotations_path
            )
        self.assertIn("duplicate_component_conflict", {d.code for d in result.diagnostics})

    def test_malformed_json_value_fails_without_exception(self) -> None:
        sources, items, annotations = _valid_draft()
        items[0]["source_id"] = ["not", "an", "id"]
        with Fixture() as fixture:
            fixture.write(sources, items, annotations)
            result = validate_files(
                fixture.sources_path, fixture.items_path, fixture.annotations_path
            )
        self.assertFalse(result.valid)
        self.assertIn("invalid_opaque_id", {d.code for d in result.diagnostics})

    def test_adversarial_container_types_fail_without_exception(self) -> None:
        sources, items, annotations = _valid_draft()
        sources[0]["provenance_class"] = ["invalid"]
        items[0]["final_label"] = ["benign"]
        items[0]["language_stratum"] = {"hindi": True}
        items[0]["leakage_component_id"] = ["component-001"]
        items[0]["artifact_review"] = {
            "status": "passed",
            "representation": ["none"],
        }
        annotations[0]["item_id"] = ["item-001"]
        annotations[1]["annotator_id"] = {"annotator": "b"}
        with Fixture() as fixture:
            fixture.write(sources, items, annotations)
            result = validate_files(
                fixture.sources_path, fixture.items_path, fixture.annotations_path
            )
        self.assertFalse(result.valid)
        self.assertIn("invalid_choice", {d.code for d in result.diagnostics})
        self.assertIn("invalid_opaque_id", {d.code for d in result.diagnostics})

    def test_number_normalized_template_variants_require_one_component(self) -> None:
        sources, items, annotations = _valid_draft()
        first_text = "Reserved route 123 expires soon"
        items[0]["text"] = first_text
        items[0]["content_sha256"] = sha256(first_text.encode()).hexdigest()
        items.append(
            _item(
                "item-002",
                text="Reserved route 987 expires soon",
                component="component-002",
            )
        )
        annotations.extend(
            [
                _annotation("ann-003", "annotator-a", item_id="item-002"),
                _annotation("ann-004", "annotator-b", item_id="item-002"),
            ]
        )
        with Fixture() as fixture:
            fixture.write(sources, items, annotations)
            result = validate_files(
                fixture.sources_path, fixture.items_path, fixture.annotations_path
            )
        self.assertIn("template_component_conflict", {d.code for d in result.diagnostics})


def _ready_fixture() -> tuple[list[dict[str, object]], list[dict[str, object]], list[dict[str, object]]]:
    sources = [
        _source(
            f"src-{component_index:03d}",
            consent_reference=f"consent-{component_index:03d}",
            collection_batch_id=f"batch-{component_index:03d}",
        )
        for component_index in range(15)
    ]
    items: list[dict[str, object]] = []
    annotations: list[dict[str, object]] = []
    component_markers = (
        "amber", "cedar", "lotus", "river", "solar", "maple", "coral", "birch",
        "pearl", "flint", "mango", "olive", "quartz", "raven", "tiger",
    )
    index = 0
    for stratum in LANGUAGE_STRATA:
        for label in ("benign", "phishing"):
            for position in range(30):
                index += 1
                item_id = f"item-{index:03d}"
                component_index = position % 15
                component = f"component-{component_index:03d}"
                marker = component_markers[component_index]
                text = (
                    f"Reserved synthetic {stratum} {label} {marker} example "
                    f"number {position} variant {index}."
                )
                items.append(
                    _item(
                        item_id,
                        text=text,
                        label=label,
                        stratum=stratum,
                        component=component,
                    )
                )
                items[-1]["source_id"] = f"src-{component_index:03d}"
                annotations.extend(
                    [
                        _annotation(
                            f"ann-{index:03d}-a",
                            "annotator-a",
                            item_id=item_id,
                            label=label,
                            stratum=stratum,
                        ),
                        _annotation(
                            f"ann-{index:03d}-b",
                            "annotator-b",
                            item_id=item_id,
                            label=label,
                            stratum=stratum,
                        ),
                    ]
                )
    return sources, items, annotations


class PilotReadinessTests(unittest.TestCase):
    def test_ready_arithmetic_components_metrics_and_grouped_folds(self) -> None:
        with Fixture() as fixture:
            fixture.write(*_ready_fixture())
            first = validate_files(
                fixture.sources_path, fixture.items_path, fixture.annotations_path, mode="ready"
            )
            second = validate_files(
                fixture.sources_path, fixture.items_path, fixture.annotations_path, mode="ready"
            )
        self.assertTrue(first.valid, first.report["diagnostics"])
        self.assertEqual(first.report, second.report)
        self.assertEqual(first.report["readiness"]["blind_label_raw_agreement"], 1.0)
        self.assertEqual(
            first.report["provenance"]["items"]["tester_authored_simulation"], 240
        )
        for cell in first.report["readiness"]["cells"]:
            self.assertEqual(cell["items"], 30)
            self.assertEqual(cell["leakage_components"], 15)
            self.assertEqual(cell["largest_component_items"], 2)
        for fold in first.report["readiness"]["folds"]:
            self.assertGreater(fold["labels"]["benign"], 0)
            self.assertGreater(fold["labels"]["phishing"], 0)
            self.assertGreaterEqual(fold["components"], 5)
            self.assertTrue(all(cell["items"] > 0 for cell in fold["cells"]))

    def test_ready_fails_undefined_metrics_and_incomplete_cells(self) -> None:
        with Fixture() as fixture:
            fixture.write(*_valid_draft())
            result = validate_files(
                fixture.sources_path, fixture.items_path, fixture.annotations_path, mode="ready"
            )
        codes = {diagnostic.code for diagnostic in result.diagnostics}
        self.assertFalse(result.valid)
        self.assertIn("ready_item_count", codes)
        self.assertIn("ready_label_alpha", codes)

    def test_uncertain_blind_ratings_cannot_inflate_raw_agreement_gate(self) -> None:
        sources, items, annotations = _ready_fixture()
        for index in range(1, 31):
            item_id = f"item-{index:03d}"
            matching = [row for row in annotations if row["item_id"] == item_id]
            for row in matching:
                row["primary_label"] = "uncertain"
            item = next(row for row in items if row["item_id"] == item_id)
            item["label_resolution"] = "adjudicated"
            annotations.append(
                _annotation(
                    f"ann-{index:03d}-c",
                    "annotator-c",
                    item_id=item_id,
                    label=item["final_label"],
                    stratum=item["language_stratum"],
                    kind="adjudication",
                )
            )
        with Fixture() as fixture:
            fixture.write(sources, items, annotations)
            result = validate_files(
                fixture.sources_path, fixture.items_path, fixture.annotations_path, mode="ready"
            )
        self.assertFalse(result.valid)
        self.assertEqual(result.report["readiness"]["blind_label_raw_agreement"], 0.875)
        self.assertIn("ready_label_agreement", {d.code for d in result.diagnostics})

    def test_239_of_240_uncertain_language_pairs_cannot_bypass_gate(self) -> None:
        sources, items, annotations = _ready_fixture()
        for index in range(1, 240):
            item_id = f"item-{index:03d}"
            for row in annotations:
                if row["item_id"] == item_id:
                    row["language_stratum"] = "uncertain"
            item = next(row for row in items if row["item_id"] == item_id)
            item["label_resolution"] = "adjudicated"
            annotations.append(
                _annotation(
                    f"ann-{index:03d}-c",
                    "annotator-c",
                    item_id=item_id,
                    label=item["final_label"],
                    stratum=item["language_stratum"],
                    kind="adjudication",
                )
            )
        with Fixture() as fixture:
            fixture.write(sources, items, annotations)
            result = validate_files(
                fixture.sources_path, fixture.items_path, fixture.annotations_path, mode="ready"
            )
        self.assertFalse(result.valid)
        self.assertEqual(
            result.report["readiness"]["blind_language_known_raw_agreement"], 1 / 240
        )
        self.assertEqual(result.report["readiness"]["uncertainty_items"], 239)
        self.assertEqual(result.report["readiness"]["uncertain_ratings"], 478)
        self.assertEqual(result.report["readiness"]["uncertain_item_rate"], 239 / 240)
        self.assertEqual(result.report["readiness"]["uncertain_rating_rate"], 478 / 480)
        self.assertIn("ready_language_agreement", {d.code for d in result.diagnostics})

    def test_five_global_components_fail_fold_component_gate(self) -> None:
        sources, items, annotations = _ready_fixture()
        for item in items:
            old_index = int(item["leakage_component_id"].rsplit("-", 1)[1])
            new_index = old_index % 5
            item["leakage_component_id"] = f"component-{new_index:03d}"
            item["source_id"] = f"src-{new_index:03d}"
        sources = sources[:5]
        with Fixture() as fixture:
            fixture.write(sources, items, annotations)
            result = validate_files(
                fixture.sources_path, fixture.items_path, fixture.annotations_path, mode="ready"
            )
        self.assertFalse(result.valid)
        self.assertIn("ready_fold_components", {d.code for d in result.diagnostics})

    def test_cell_component_dominance_over_ten_fails_ready(self) -> None:
        sources, items, annotations = _ready_fixture()
        target = [
            item
            for item in items
            if item["language_stratum"] == "hindi" and item["final_label"] == "benign"
        ]
        for item in target[:26]:
            item["leakage_component_id"] = "component-000"
            item["source_id"] = "src-000"
        with Fixture() as fixture:
            fixture.write(sources, items, annotations)
            result = validate_files(
                fixture.sources_path, fixture.items_path, fixture.annotations_path, mode="ready"
            )
        self.assertFalse(result.valid)
        self.assertIn("ready_cell_component_dominance", {d.code for d in result.diagnostics})

    def test_exact_duplicates_cannot_fill_ready_quota(self) -> None:
        sources, items, annotations = _ready_fixture()
        items[1]["text"] = items[0]["text"]
        items[1]["content_sha256"] = items[0]["content_sha256"]
        items[1]["leakage_component_id"] = items[0]["leakage_component_id"]
        items[1]["source_id"] = items[0]["source_id"]
        with Fixture() as fixture:
            fixture.write(sources, items, annotations)
            result = validate_files(
                fixture.sources_path, fixture.items_path, fixture.annotations_path, mode="ready"
            )
        self.assertFalse(result.valid)
        self.assertIn("duplicate_text_retained", {d.code for d in result.diagnostics})


class PilotCliTests(unittest.TestCase):
    def test_cli_is_deterministic_sanitized_and_example_is_valid(self) -> None:
        root = Path(__file__).resolve().parents[1]
        arguments = [
            "validate",
            "--sources",
            str(root / "examples/pilot_v01/sources.jsonl"),
            "--items",
            str(root / "examples/pilot_v01/items.jsonl"),
            "--annotations",
            str(root / "examples/pilot_v01/annotations.jsonl"),
            "--mode",
            "draft",
            "--format",
            "json",
        ]
        outputs = []
        for _ in range(2):
            stream = io.StringIO()
            with redirect_stdout(stream):
                code = main(arguments)
            self.assertEqual(code, 0)
            outputs.append(stream.getvalue())
        self.assertEqual(outputs[0], outputs[1])
        self.assertNotIn(str(root), outputs[0])
        self.assertNotIn("Yeh synthetic", outputs[0])
        self.assertEqual(json.loads(outputs[0])["status"], "VALID")

    def test_cli_validation_failure_returns_one_without_echoing_values_or_paths(self) -> None:
        sources, items, annotations = _valid_draft()
        secret = "private-value-never-echo"
        items[0]["text"] = f"password: {secret}"
        items[0]["content_sha256"] = sha256(items[0]["text"].encode()).hexdigest()
        with Fixture() as fixture:
            fixture.write(sources, items, annotations)
            stream = io.StringIO()
            with redirect_stdout(stream):
                code = main(
                    [
                        "validate",
                        "--sources",
                        str(fixture.sources_path),
                        "--items",
                        str(fixture.items_path),
                        "--annotations",
                        str(fixture.annotations_path),
                        "--mode",
                        "draft",
                        "--format",
                        "text",
                    ]
                )
            output = stream.getvalue()
        self.assertEqual(code, 1)
        self.assertNotIn(secret, output)
        self.assertNotIn("private-name", output)


if __name__ == "__main__":
    unittest.main()
