from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unicodedata
import unittest
from unittest.mock import patch

from fisher_data.validator import (
    BLINDING_ATTESTATION,
    SCHEMA_VERSION,
    _endpoint_pair_structures,
    _set_f1,
    format_json,
    format_text,
    validate_files,
)


STUDY_STRATA = ("hindi", "tamil", "telugu", "english_indic_code_mixed")
FACETS = (
    "claimed_actor",
    "claim_or_problem",
    "destination_artifact",
    "pressure_tactic",
    "requested_action",
    "sensitive_item_or_asset",
)


def visible_artifact(
    text: str,
    value: str = "[DOMAIN]",
    *,
    kind: str = "DOMAIN",
    kind_reason: str = "",
    representation: str = "TYPED_PLACEHOLDER",
) -> dict:
    start = text.index(value)
    return {
        "kind": kind,
        "kind_reason": kind_reason,
        "representation": representation,
        "start": start,
        "end": start + len(value),
        "text": value,
    }


def source_record(
    source_id: str = "src_test",
    *,
    provenance_class: str = "tester_authored_simulation",
    eligible_partitions: list[str] | None = None,
) -> dict:
    if eligible_partitions is None:
        eligible_partitions = (
            ["development", "external_test"]
            if provenance_class == "public_authentic"
            else [
                "pilot", "unassigned", "development", "probability_calibration",
                "safety_threshold", "primary_test", "external_test", "excluded",
            ]
        )
    participant = provenance_class in {"tester_authored_simulation", "tester_donated_authentic"}
    return {
        "schema_version": SCHEMA_VERSION,
        "source_id": source_id,
        "artifact_sha256": sha256(source_id.encode()).hexdigest(),
        "provenance": {
            "provenance_class": provenance_class,
            "origin_name": "reserved-synthetic-test",
            "collected_by": "reserved-test-author",
            "collected_date": "2026-08-19",
        },
        "rights": {
            "basis": "consent" if participant else "contract",
            "license_id": "reserved-test-only",
            "research_use_permitted": True,
        },
        "consent": {
            "status": "granted" if participant else "not_applicable",
            "scope": "reserved-synthetic-test",
            "withdrawal_process": "reserved-test-process",
        },
        "privacy": {"contains_personal_data": False, "deidentified": True, "reviewed": True},
        "eligible_partitions": eligible_partitions,
    }


def item_record(
    item_id: str = "item_test",
    *,
    text: str = "Actor claim action asset [DOMAIN] pressure evidence token",
    source_id: str = "src_test",
    partition: str = "pilot",
    language_stratum: str = "hindi",
    component_id: str | None = None,
    exclusion_reasons: list[str] | None = None,
) -> dict:
    language = {
        "hindi": "hi", "tamil": "ta", "telugu": "te",
        "english_indic_code_mixed": "mixed", "uncertain": "unknown",
    }[language_stratum]
    placeholder_kinds = ("URL", "DOMAIN", "PHONE", "UPI", "BANK", "EMAIL", "APP")
    visible_artifacts = [
        visible_artifact(text, f"[{kind}]", kind=kind)
        for kind in placeholder_kinds
        if f"[{kind}]" in text
    ]
    if "[ARTIFACT]" in text:
        visible_artifacts.append(
            visible_artifact(
                text,
                "[ARTIFACT]",
                kind="OTHER",
                kind_reason="Synthetic typed artifact with no more specific controlled kind.",
            )
        )
    visible_artifacts.sort(
        key=lambda artifact: (
            artifact["start"], artifact["end"], artifact["kind"].encode("utf-8"),
            artifact["representation"].encode("utf-8"), artifact["text"].encode("utf-8"),
        )
    )
    canonical_vmp = json.dumps(
        {"text": text, "visible_artifacts": visible_artifacts},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "item_id": item_id,
        "source_id": source_id,
        "text": text,
        "content_sha256": sha256(text.encode()).hexdigest(),
        "vmp_sha256": sha256(canonical_vmp.encode("utf-8")).hexdigest(),
        "language": language,
        "language_stratum": language_stratum,
        "partition": partition,
        "exclusion_reasons": exclusion_reasons or [],
        "visible_artifacts": visible_artifacts,
        "privacy": {"synthetic": True, "pii_reviewed": True, "contains_pii": False},
        "generation": {"method": "human", "model_id": "none"},
        "leakage_component_id": component_id or f"component_{item_id.removeprefix('item_')}",
        "lineage": {"parent_item_ids": [], "operation": "original"},
    }


def registry_record(snapshot_id: str = "registry_reserved_v1", approval: str = "approved") -> dict:
    return {
        "schema_version": SCHEMA_VERSION,
        "registry_snapshot_id": snapshot_id,
        "artifact_sha256": sha256(snapshot_id.encode()).hexdigest(),
        "version": "1.0.0",
        "snapshot_date": "2026-08-19",
        "approval_state": approval,
    }


def refresh_vmp_hash(item: dict) -> None:
    canonical = json.dumps(
        {"text": item["text"], "visible_artifacts": item["visible_artifacts"]},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )
    item["vmp_sha256"] = sha256(canonical.encode("utf-8")).hexdigest()


def lexical_ranges(text: str) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    start: int | None = None
    for index, character in enumerate(text):
        lexical = unicodedata.category(character)[0] in {"L", "M"}
        if lexical and start is None:
            start = index
        elif not lexical and start is not None:
            ranges.append((start, index))
            start = None
    if start is not None:
        ranges.append((start, len(text)))
    return ranges


def language_tokens(item: dict, *, stratum: str | None = None) -> tuple[list[dict], str]:
    chosen = stratum or item["language_stratum"]
    ranges = lexical_ranges(item["text"])
    if chosen == "english_indic_code_mixed":
        languages = ["en" if index < len(ranges) // 2 else "hi" for index in range(len(ranges))]
        pair = "en_hi"
    else:
        language = {"hindi": "hi", "tamil": "ta", "telugu": "te"}.get(chosen, "other")
        languages = [language] * len(ranges)
        pair = "none"
    return ([
        {
            "start": start,
            "end": end,
            "text": item["text"][start:end],
            "language": languages[index],
            "script": "latin",
        }
        for index, (start, end) in enumerate(ranges)
    ], pair)


def span(text: str, value: str, facet: str, qualifier: str = "N/A") -> dict:
    start = text.index(value)
    return {
        "start": start,
        "end": start + len(value),
        "text": value,
        "facet": facet,
        "qualifier": qualifier,
        "qualifier_reason": "",
    }


def annotation_record(
    item: dict,
    suffix: str,
    *,
    kind: str = "blind",
    annotator: str = "annotator_a",
    label: str = "benign",
    structured: bool = False,
    offset_variant: bool = False,
) -> dict:
    text = item["text"]
    if structured:
        values = {
            "claimed_actor": "claim" if offset_variant else "Actor",
            "claim_or_problem": "Actor" if offset_variant else "claim",
            "requested_action": "pressure" if offset_variant else "action",
            "sensitive_item_or_asset": "[DOMAIN]" if offset_variant else "asset",
            "destination_artifact": "[DOMAIN]",
            "pressure_tactic": "action" if offset_variant else "pressure",
        }
        spans = [span(text, text, "supporting_evidence")]
        for facet in FACETS:
            qualifier = "DOMAIN" if facet == "destination_artifact" else "URGENCY" if facet == "pressure_tactic" else "N/A"
            spans.append(span(text, values[facet], facet, qualifier))
        spans.sort(key=lambda value: (value["start"], value["end"], value["facet"], value["qualifier"]))
        indices = {value["facet"]: index for index, value in enumerate(spans)}
        facets = [{"facet": facet, "state": "explicit", "span_indices": [indices[facet]]} for facet in FACETS]
    else:
        spans = [span(text, text, "supporting_evidence")]
        facets = [{"facet": facet, "state": "not_applicable", "span_indices": []} for facet in FACETS]
        if label == "phishing":
            spans.append(span(text, "Actor", "claimed_actor"))
            spans.sort(key=lambda value: (value["start"], value["end"], value["facet"], value["qualifier"]))
            actor_index = next(index for index, value in enumerate(spans) if value["facet"] == "claimed_actor")
            facets = [
                {
                    "facet": facet,
                    "state": "explicit" if facet == "claimed_actor" else "not_explicit" if facet in {"requested_action", "sensitive_item_or_asset"} else "not_applicable",
                    "span_indices": [actor_index] if facet == "claimed_actor" else [],
                }
                for facet in FACETS
            ]
        indices = {value["facet"]: index for index, value in enumerate(spans)}

    token_spans, pair = language_tokens(item)
    return {
        "schema_version": SCHEMA_VERSION,
        "annotation_id": f"annotation_{suffix}",
        "item_id": item["item_id"],
        "annotator_id": annotator,
        "kind": kind,
        "independent": kind == "blind",
        "primary_label": label,
        "subtype": "informational" if label == "benign" else "not_applicable",
        "subtype_other_reason": "",
        "language_stratum": item["language_stratum"],
        "resolution_method": "not_applicable" if kind == "blind" else "adjudicated",
        "confidence": "high",
        "ambiguity_tags": [],
        "token_language_spans": token_spans,
        "code_mix_pair": pair,
        "facets": facets,
        "spans": spans,
        "evidence_span_indices": [indices["supporting_evidence"]],
        "romanization_ambiguities": [],
        "created_date": "2026-08-19",
    }


def registry_reference(
    annotation: dict,
    suffix: str,
    *,
    actor_span_index: int | None = None,
    destination_span_index: int | None = None,
    label: str = "UNKNOWN",
    coverage: str = "missing",
    reviewer: str = "annotator_registry",
    snapshot_id: str = "registry_reserved_v1",
    evidence_ids: list[str] | None = None,
) -> dict:
    facets = {facet["facet"]: facet for facet in annotation["facets"]}
    if actor_span_index is None:
        actor_span_index = facets["claimed_actor"]["span_indices"][0]
    if destination_span_index is None:
        destination_span_index = facets["destination_artifact"]["span_indices"][0]
    return {
        "schema_version": SCHEMA_VERSION,
        "registry_reference_id": f"registry_reference_{suffix}",
        "item_id": annotation["item_id"],
        "final_annotation_id": annotation["annotation_id"],
        "registry_reviewer_id": reviewer,
        "registry_snapshot_id": snapshot_id,
        "actor_span_index": actor_span_index,
        "destination_span_index": destination_span_index,
        "label": label,
        "registry_coverage": coverage,
        "registry_evidence_ids": evidence_ids or [],
        "resolver_version": "resolver_1.0.0",
        "blinding_attestation": BLINDING_ATTESTATION,
        "created_date": "2026-08-19",
    }


def complete_annotations(item: dict, base: str, label: str, structured: bool) -> list[dict]:
    return [
        annotation_record(item, f"{base}_a", annotator="annotator_a", label=label, structured=structured),
        annotation_record(item, f"{base}_b", annotator="annotator_b", label=label, structured=structured),
        annotation_record(item, f"{base}_final", kind="final", annotator="annotator_final", label=label, structured=structured),
    ]


def change_primary(annotation: dict, label: str) -> None:
    annotation["primary_label"] = label
    annotation["subtype"] = "informational" if label == "benign" else "not_applicable"
    annotation["subtype_other_reason"] = ""
    if label == "uncertain":
        annotation["ambiguity_tags"] = sorted(set(annotation["ambiguity_tags"]) | {"intent"})


def change_language(annotation: dict, item: dict, stratum: str) -> None:
    annotation["language_stratum"] = stratum
    annotation["token_language_spans"], annotation["code_mix_pair"] = language_tokens(item, stratum=stratum)
    if stratum == "uncertain":
        annotation["ambiguity_tags"] = sorted(set(annotation["ambiguity_tags"]) | {"language"})


def pilot_dataset(
    *, below_coverage: bool = False
) -> tuple[list[dict], list[dict], list[dict], list[dict], list[dict]]:
    sources = [source_record()]
    items: list[dict] = []
    annotations: list[dict] = []
    by_item: dict[str, list[dict]] = {}
    structured_by_label: dict[str, list[str]] = {"benign": [], "phishing": []}
    by_label: dict[str, list[str]] = {"benign": [], "phishing": []}
    index = 0
    for stratum in STUDY_STRATA:
        for local_index in range(300):
            label = "benign" if local_index < 150 else "phishing"
            item_id = f"item_pilot_{index:04d}"
            text = f"Actor claim action asset [DOMAIN] pressure evidence token {index:04d}"
            item = item_record(item_id, text=text, language_stratum=stratum)
            structured = local_index % 2 == 0
            records = complete_annotations(item, f"pilot_{index:04d}", label, structured)
            items.append(item)
            annotations.extend(records)
            by_item[item_id] = records
            by_label[label].append(item_id)
            if structured:
                structured_by_label[label].append(item_id)
            index += 1
    uncertain_count = 61 if below_coverage else 60
    uncertain_ids = by_label["benign"][: (uncertain_count + 1) // 2] + by_label["phishing"][: uncertain_count // 2]
    for item_id in uncertain_ids:
        change_primary(by_item[item_id][0], "uncertain")
    if not below_coverage:
        for item_id in [value for value in structured_by_label["benign"] if value not in uncertain_ids][:57]:
            change_primary(by_item[item_id][1], "phishing")
        for item_id in [value for value in structured_by_label["phishing"] if value not in uncertain_ids][:57]:
            change_primary(by_item[item_id][1], "benign")
    references = [
        registry_reference(records[2], f"pilot_{item_id.removeprefix('item_pilot_')}")
        for item_id, records in sorted(by_item.items())
        if any(facet["facet"] == "claimed_actor" and facet["state"] == "explicit" for facet in records[2]["facets"])
        and any(facet["facet"] == "destination_artifact" and facet["state"] == "explicit" for facet in records[2]["facets"])
    ]
    return sources, items, annotations, [registry_record()], references


class ValidatorTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp.name)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def write_records(self, name: str, records: list[dict]) -> Path:
        path = self.directory / name
        path.write_text("".join(json.dumps(record, ensure_ascii=True) + "\n" for record in records), encoding="utf-8")
        return path

    def validate(
        self,
        sources: list[dict],
        items: list[dict],
        annotations: list[dict],
        registry: list[dict] | None = None,
        references: list[dict] | None = None,
        *,
        mode: str = "draft",
    ):
        registry_path = self.write_records("registry_manifest.jsonl", registry) if registry is not None else None
        references_path = self.write_records("registry_references.jsonl", references) if references is not None else None
        return validate_files(
            self.write_records("sources.jsonl", sources),
            self.write_records("items.jsonl", items),
            self.write_records("annotations.jsonl", annotations),
            mode,
            registry_path,
            references_path,
        )

    @staticmethod
    def codes(report) -> set[str]:
        return {diagnostic.code for diagnostic in report.diagnostics}

    def test_pilot_final_accepts_frozen_boundaries_and_reports_metrics(self) -> None:
        report = self.validate(*pilot_dataset(), mode="pilot-final")
        self.assertTrue(report.valid, format_text(report))
        self.assertEqual(report.counts, {"sources": 1, "items": 1200, "annotations": 3600, "registry_manifest": 1, "registry_references": 600})
        self.assertEqual(report.reliability.binary_pair_coverage, 0.95)
        self.assertEqual(report.agreement.raw_agreement, 0.90)
        self.assertGreaterEqual(report.agreement.krippendorff_alpha, 0.80)
        self.assertEqual(report.reliability.language_agreement.raw_agreement, 1.0)
        self.assertGreaterEqual(report.reliability.language_agreement.krippendorff_alpha, 0.80)
        self.assertTrue(all(value == 1.0 for value in report.reliability.facet_span_exact_f1.values()))
        self.assertEqual(report.registry_reference_inventory.applicable_endpoint_pairs, 600)
        self.assertEqual(report.registry_reference_inventory.reference_records, 600)
        self.assertEqual(report.reliability.endpoint_pair_structure_exact_f1, 1.0)
        self.assertNotIn("relation_structure_exact_f1", report.to_dict()["reliability"])
        self.assertEqual(report.reliability.supporting_evidence_exact_f1, 1.0)
        self.assertEqual(report.reliability.completeness, 1.0)

    def test_pilot_gates_fail_below_coverage_and_language_alpha(self) -> None:
        report = self.validate(*pilot_dataset(below_coverage=True), mode="pilot-final")
        self.assertLess(report.reliability.binary_pair_coverage, 0.95)
        self.assertIn("binary_pair_coverage_gate", self.codes(report))
        sources, items, annotations, registry, references = pilot_dataset()
        items_by_id = {item["item_id"]: item for item in items}
        changed = 0
        for annotation in annotations:
            if annotation["kind"] == "blind" and annotation["annotator_id"] == "annotator_b" and annotation["language_stratum"] == "hindi" and changed < 180:
                change_language(annotation, items_by_id[annotation["item_id"]], "tamil")
                changed += 1
        language_report = self.validate(sources, items, annotations, registry, references, mode="pilot-final")
        self.assertLess(language_report.reliability.language_agreement.krippendorff_alpha, 0.80)
        self.assertIn("language_alpha_gate", self.codes(language_report))

    def test_pilot_raw_agreement_and_balance_fail_below_boundaries(self) -> None:
        sources, items, annotations, registry, references = pilot_dataset()
        blind_labels: dict[str, list[str]] = {}
        for record in annotations:
            if record["kind"] == "blind":
                blind_labels.setdefault(record["item_id"], []).append(record["primary_label"])
        for annotation in annotations:
            if (
                annotation["kind"] == "blind"
                and annotation["annotator_id"] == "annotator_b"
                and annotation["primary_label"] == "benign"
                and blind_labels[annotation["item_id"]] == ["benign", "benign"]
                and any(facet["state"] == "explicit" for facet in annotation["facets"])
            ):
                change_primary(annotation, "phishing")
                break
        agreement = self.validate(sources, items, annotations, registry, references, mode="pilot-final")
        self.assertLess(agreement.agreement.raw_agreement, 0.90)
        self.assertIn("raw_agreement_gate", self.codes(agreement))

        sources, items, annotations, registry, references = pilot_dataset()
        changed_item = items[0]
        changed_item["language_stratum"] = "tamil"
        changed_item["language"] = "ta"
        for annotation in annotations[:3]:
            change_language(annotation, changed_item, "tamil")
        balance = self.validate(sources, items, annotations, registry, references, mode="pilot-final")
        self.assertTrue({"pilot_stratum_balance", "pilot_label_balance"} <= self.codes(balance))

    def test_unknown_key_and_newline_never_leak(self) -> None:
        source = source_record()
        source["attacker\nSECRET"] = "hidden"
        report = self.validate([source], [], [])
        for output in (format_text(report), format_json(report)):
            self.assertNotIn("attacker", output)
            self.assertNotIn("SECRET", output)
        self.assertIn("unknown_field", self.codes(report))

    def test_strict_jsonl_duplicate_keys_blank_nonfinite_and_nonobject(self) -> None:
        sources_path = self.directory / "strict_sources.jsonl"
        sources_path.write_text(
            '{"source_id":"src_x","source_id":"src_y"}\n\n[]\n{"x":NaN}\n',
            encoding="utf-8",
        )
        report = validate_files(
            sources_path,
            self.write_records("strict_items.jsonl", []),
            self.write_records("strict_annotations.jsonl", []),
            "draft",
        )
        self.assertTrue(
            {"duplicate_json_key", "blank_line", "record_not_object", "invalid_json"}
            <= self.codes(report)
        )

    def test_schema_version_and_safe_identifiers_are_required_everywhere(self) -> None:
        source = source_record()
        item = item_record()
        annotation = annotation_record(item, "schema")
        registry = registry_record()
        structured_final = annotation_record(item, "schema_final", kind="final", annotator="annotator_final", label="phishing", structured=True)
        reference = registry_reference(structured_final, "schema")
        del source["schema_version"]
        del item["schema_version"]
        del annotation["schema_version"]
        del registry["schema_version"]
        del reference["schema_version"]
        report = self.validate([source], [item], [annotation, structured_final], [registry], [reference])
        self.assertIn("missing_field", self.codes(report))
        old = source_record()
        old["schema_version"] = "1.0.0"
        self.assertIn("schema_version", self.codes(self.validate([old], [], [])))
        old_records = {
            "sources": source_record(),
            "items": item_record(),
            "annotations": annotation_record(item_record(), "old_schema"),
            "registry_manifest": registry_record(),
            "registry_references": registry_reference(structured_final, "old_schema"),
        }
        for dataset, old_record in old_records.items():
            with self.subTest(dataset=dataset):
                old_record["schema_version"] = "1.1.0"
                if dataset == "sources":
                    old_report = self.validate([old_record], [], [])
                elif dataset == "items":
                    old_report = self.validate([source_record()], [old_record], [])
                elif dataset == "annotations":
                    old_report = self.validate([source_record()], [item_record()], [old_record])
                elif dataset == "registry_manifest":
                    old_report = self.validate([], [], [], [old_record], [])
                else:
                    old_report = self.validate(
                        [source_record()],
                        [item],
                        [structured_final],
                        [registry_record()],
                        [old_record],
                    )
                self.assertTrue(
                    any(
                        diagnostic.code == "schema_version"
                        and diagnostic.dataset == dataset
                        for diagnostic in old_report.diagnostics
                    ),
                    format_text(old_report),
                )
        bad_source = source_record()
        bad_source["source_id"] = "unsafe/source"
        self.assertIn("invalid_id", self.codes(self.validate([bad_source], [], [])))

    def test_visible_artifact_inventory_accepts_empty_and_stays_out_of_human_gold(self) -> None:
        item = item_record()
        annotation = annotation_record(item, "visible_boundary")
        report = self.validate([source_record()], [item], [annotation])
        self.assertNotIn("unknown_field", self.codes(report), format_text(report))
        self.assertNotIn("visible_artifacts", annotation)

        empty = item_record("item_empty_inventory")
        empty["visible_artifacts"] = []
        refresh_vmp_hash(empty)
        empty_report = self.validate([source_record()], [empty], [])
        self.assertNotIn("visible_artifact_count", self.codes(empty_report), format_text(empty_report))

        sixty_four_text = " ".join("[DOMAIN]" for _ in range(64))
        sixty_four = item_record("item_sixty_four_artifacts", text=sixty_four_text)
        sixty_four["visible_artifacts"] = []
        cursor = 0
        for _ in range(64):
            start = sixty_four_text.index("[DOMAIN]", cursor)
            sixty_four["visible_artifacts"].append({
                "kind": "DOMAIN", "kind_reason": "",
                "representation": "TYPED_PLACEHOLDER",
                "start": start, "end": start + len("[DOMAIN]"), "text": "[DOMAIN]",
            })
            cursor = start + len("[DOMAIN]")
        refresh_vmp_hash(sixty_four)
        boundary_report = self.validate([source_record()], [sixty_four], [])
        self.assertFalse(
            {"visible_artifact_count", "visible_artifact_order", "visible_artifact_overlap", "visible_artifact_duplicate"}
            & self.codes(boundary_report),
            format_text(boundary_report),
        )

        leaked = deepcopy(annotation)
        leaked["annotation_id"] = "annotation_visible_leak"
        leaked["visible_artifacts"] = deepcopy(item["visible_artifacts"])
        self.assertIn(
            "unknown_field",
            self.codes(self.validate([source_record()], [item], [leaked])),
        )

    def test_visible_artifact_inventory_rejects_shape_type_and_vocabulary_errors(self) -> None:
        missing = item_record("item_missing_inventory")
        del missing["visible_artifacts"]
        self.assertIn("missing_field", self.codes(self.validate([source_record()], [missing], [])))

        wrong_inventory = item_record("item_wrong_inventory")
        wrong_inventory["visible_artifacts"] = {}
        self.assertIn("wrong_type", self.codes(self.validate([source_record()], [wrong_inventory], [])))

        too_many = item_record("item_too_many_inventory")
        too_many["visible_artifacts"] = [deepcopy(too_many["visible_artifacts"][0]) for _ in range(65)]
        self.assertIn("visible_artifact_count", self.codes(self.validate([source_record()], [too_many], [])))

        unknown = item_record("item_unknown_artifact_field")
        unknown["visible_artifacts"][0]["label"] = "phishing"
        self.assertIn("unknown_field", self.codes(self.validate([source_record()], [unknown], [])))

        field_values = {
            "kind": 1,
            "kind_reason": 1,
            "representation": 1,
            "start": True,
            "end": False,
            "text": 1,
        }
        for field, value in field_values.items():
            with self.subTest(field=field):
                wrong = item_record(f"item_wrong_{field}")
                wrong["visible_artifacts"][0][field] = value
                self.assertIn("wrong_type", self.codes(self.validate([source_record()], [wrong], [])))

        for field, value in (("kind", "NOT_A_KIND"), ("representation", "RAW")):
            with self.subTest(field=field, value=value):
                invalid = item_record(f"item_invalid_{field}")
                invalid["visible_artifacts"][0][field] = value
                self.assertIn("invalid_value", self.codes(self.validate([source_record()], [invalid], [])))

        empty_reason = item_record("item_empty_other_reason")
        empty_reason["visible_artifacts"][0]["kind"] = "OTHER"
        empty_reason["visible_artifacts"][0]["kind_reason"] = ""
        self.assertIn("empty_string", self.codes(self.validate([source_record()], [empty_reason], [])))
        unexpected_reason = item_record("item_unexpected_kind_reason")
        unexpected_reason["visible_artifacts"][0]["kind_reason"] = "not permitted"
        self.assertIn("visible_artifact_kind_reason", self.codes(self.validate([source_record()], [unexpected_reason], [])))
        long_reason = item_record("item_long_kind_reason")
        long_reason["visible_artifacts"][0]["kind_reason"] = "x" * 501
        self.assertIn("string_length_limit", self.codes(self.validate([source_record()], [long_reason], [])))

    def test_visible_artifact_inventory_rejects_offsets_text_order_and_overlap(self) -> None:
        base = item_record()
        invalid_ranges = {
            "negative": (-1, 3),
            "empty": (25, 25),
            "reversed": (30, 25),
            "past_end": (25, len(base["text"]) + 1),
        }
        for suffix, (start, end) in invalid_ranges.items():
            with self.subTest(range=suffix):
                invalid = item_record(f"item_{suffix}_artifact")
                invalid["visible_artifacts"][0]["start"] = start
                invalid["visible_artifacts"][0]["end"] = end
                self.assertIn("visible_artifact_out_of_bounds", self.codes(self.validate([source_record()], [invalid], [])))

        mismatch = item_record("item_artifact_mismatch")
        mismatch["visible_artifacts"][0]["text"] = "wrong"
        self.assertIn("visible_artifact_text_mismatch", self.codes(self.validate([source_record()], [mismatch], [])))

        ordered_text = "[URL] middle [DOMAIN] last"
        ordered = item_record("item_artifact_order", text=ordered_text)
        first = visible_artifact(ordered_text, "[URL]", kind="URL")
        destination = visible_artifact(ordered_text)
        ordered["visible_artifacts"] = [destination, first]
        self.assertIn("visible_artifact_order", self.codes(self.validate([source_record()], [ordered], [])))

        overlapping = item_record("item_artifact_overlap")
        nested = deepcopy(overlapping["visible_artifacts"][0])
        nested["start"] += 1
        nested["text"] = overlapping["text"][nested["start"]:nested["end"]]
        overlapping["visible_artifacts"].append(nested)
        overlapping["visible_artifacts"].sort(
            key=lambda artifact: (
                artifact["start"], artifact["end"],
                artifact["kind"].encode("utf-8"),
                artifact["representation"].encode("utf-8"),
                artifact["text"].encode("utf-8"),
            )
        )
        self.assertIn("visible_artifact_overlap", self.codes(self.validate([source_record()], [overlapping], [])))

        partial_text = "[DOMAIN][ARTIFACT]"
        partial = item_record("item_artifact_partial_overlap", text=partial_text)
        partial["visible_artifacts"] = [
            visible_artifact(partial_text),
            {
                "kind": "OTHER",
                "kind_reason": "Synthetic partially overlapping artifact used only for validation.",
                "representation": "DEFANGED",
                "start": 7,
                "end": len(partial_text),
                "text": partial_text[7:],
            },
        ]
        self.assertIn("visible_artifact_overlap", self.codes(self.validate([source_record()], [partial], [])))

        duplicate = item_record("item_artifact_duplicate")
        duplicate["visible_artifacts"].append(deepcopy(duplicate["visible_artifacts"][0]))
        duplicate_codes = self.codes(self.validate([source_record()], [duplicate], []))
        self.assertTrue({"visible_artifact_duplicate", "visible_artifact_overlap"} <= duplicate_codes)

    def test_visible_artifact_strings_use_global_safety_scanners(self) -> None:
        unsafe_cases = {
            "surrogate": ("kind_reason", "synthetic \ud800 marker", "forbidden_surrogate"),
            "control": ("kind_reason", "synthetic \u0000 marker", "forbidden_control"),
            "bidi": ("kind_reason", "synthetic \u202e marker", "forbidden_bidi_control"),
            "live": ("kind_reason", "synthetic https://example.com marker", "live_artifact"),
            "sensitive": ("kind_reason", "synthetic OTP=123456 marker", "sensitive_artifact"),
        }
        for suffix, (field, value, expected_code) in unsafe_cases.items():
            with self.subTest(case=suffix):
                item = item_record(f"item_unsafe_{suffix}")
                item["visible_artifacts"][0][field] = value
                report = self.validate([source_record()], [item], [])
                self.assertIn(expected_code, self.codes(report), format_text(report))
                self.assertNotIn("123456", format_json(report))

    def test_defanged_artifacts_cannot_hide_ipv6_upi_or_nfkc_dot_routes(self) -> None:
        unsafe_surfaces = {
            "ipv6": ("[redacted] 2606:4700:4700::1111", "OTHER"),
            "ipv6_terminal_dot": ("[redacted] 2606:4700:4700::1111.", "OTHER"),
            "ipv6_loopback_terminal_dot": ("[redacted] ::1.", "OTHER"),
            "ipv6_mapped_terminal_dot": ("[redacted] ::ffff:192.0.2.1.", "OTHER"),
            "ipv6_bracketed": ("[redacted] [2606:4700:4700::1111]", "OTHER"),
            "ipv6_bracketed_port": ("[redacted] [::1]:443", "OTHER"),
            "ipv6_full": ("[redacted] 2606:4700:4700:0000:0000:0000:0000:1111", "OTHER"),
            "ipv6_zone": ("[redacted] fe80::1%eth0", "OTHER"),
            "upi": ("[redacted] recipient@oksbi", "UPI"),
            "upi_terminal_dot": ("[redacted] recipient@oksbi.", "UPI"),
            "upi_two_terminal_dots": ("[redacted] recipient@oksbi..", "UPI"),
            "upi_mapped_terminal_dot": ("[redacted] recipient@oksbi\u2024", "UPI"),
            "upi_terminal_comma": ("[redacted] recipient@oksbi,", "UPI"),
            "upi_terminal_colon": ("[redacted] recipient@oksbi:", "UPI"),
            "upi_terminal_bracket": ("[redacted] recipient@oksbi]", "UPI"),
            "one_dot_leader": ("[redacted] live\u2024domain\u2024com", "DOMAIN"),
            "small_full_stop": ("[redacted] live\ufe52domain\ufe52com", "DOMAIN"),
        }
        for suffix, (surface, kind) in unsafe_surfaces.items():
            with self.subTest(case=suffix):
                text = f"Actor {surface}"
                item = item_record(f"item_hidden_route_{suffix}", text=text)
                item["visible_artifacts"] = [visible_artifact(
                    text,
                    surface,
                    kind=kind,
                    kind_reason=(
                        "Synthetic IPv6 artifact used only for a scanner regression."
                        if kind == "OTHER" else ""
                    ),
                    representation="DEFANGED",
                )]
                refresh_vmp_hash(item)
                report = self.validate([source_record()], [item], [])
                self.assertIn("live_artifact", self.codes(report), format_text(report))
                for output in (format_text(report), format_json(report)):
                    self.assertNotIn(surface, output)

        safe_text = "Actor recipient[at]oksbi person@sample.invalid. ratio 12:30:45 @mention"
        safe = item_record("item_safe_route_lookalikes", text=safe_text)
        safe["visible_artifacts"] = [visible_artifact(
            safe_text,
            "recipient[at]oksbi",
            kind="UPI",
            representation="DEFANGED",
        )]
        refresh_vmp_hash(safe)
        safe_report = self.validate([source_record()], [safe], [])
        self.assertNotIn("live_artifact", self.codes(safe_report), format_text(safe_report))

    def test_vmp_hash_is_canonical_deterministic_and_binding(self) -> None:
        item = item_record(
            "item_vmp_hash",
            text="Actor [URL] claim [DOMAIN] pressure evidence token",
        )
        report = self.validate([source_record()], [item], [])
        self.assertNotIn("vmp_hash_mismatch", self.codes(report), format_text(report))

        reordered_objects = deepcopy(item)
        reordered_objects["visible_artifacts"] = [
            dict(reversed(list(artifact.items())))
            for artifact in reordered_objects["visible_artifacts"]
        ]
        self.assertNotIn(
            "vmp_hash_mismatch",
            self.codes(self.validate([source_record()], [reordered_objects], [])),
        )

        mismatched = deepcopy(item)
        mismatched["vmp_sha256"] = "0" * 64
        self.assertIn("vmp_hash_mismatch", self.codes(self.validate([source_record()], [mismatched], [])))
        missing = deepcopy(item)
        del missing["vmp_sha256"]
        self.assertIn("missing_field", self.codes(self.validate([source_record()], [missing], [])))
        wrong_type = deepcopy(item)
        wrong_type["vmp_sha256"] = True
        self.assertIn("wrong_type", self.codes(self.validate([source_record()], [wrong_type], [])))
        malformed = deepcopy(item)
        malformed["vmp_sha256"] = "A" * 64
        self.assertIn("invalid_sha256", self.codes(self.validate([source_record()], [malformed], [])))

    def test_visible_artifact_representation_coherence_is_fail_closed(self) -> None:
        typed_placeholders = {
            "URL": "[URL]", "DOMAIN": "[DOMAIN]", "PHONE": "[PHONE]",
            "UPI": "[UPI]", "BANK": "[BANK]", "EMAIL": "[EMAIL]",
            "APP": "[APP]", "OTHER": "[ARTIFACT]",
        }
        for kind, placeholder in typed_placeholders.items():
            with self.subTest(kind=kind):
                item = item_record(f"item_typed_{kind.casefold()}", text=f"Actor {placeholder} token")
                if kind == "OTHER":
                    self.assertEqual(item["visible_artifacts"][0]["kind_reason"], "Synthetic typed artifact with no more specific controlled kind.")
                self.assertNotIn(
                    "visible_artifact_representation_coherence",
                    self.codes(self.validate([source_record()], [item], [])),
                )

        false_typed = item_record("item_false_typed")
        false_typed["visible_artifacts"][0]["kind"] = "URL"
        self.assertIn(
            "visible_artifact_representation_coherence",
            self.codes(self.validate([source_record()], [false_typed], [])),
        )

        for suffix, surface in (("domain", "Portal.Example"), ("url", "https://portal.invalid/path")):
            with self.subTest(reserved=surface):
                item = item_record(f"item_reserved_{suffix}", text=f"Actor {surface} token")
                item["visible_artifacts"] = [visible_artifact(item["text"], surface, representation="RESERVED")]
                refresh_vmp_hash(item)
                self.assertNotIn(
                    "visible_artifact_representation_coherence",
                    self.codes(self.validate([source_record()], [item], [])),
                )
        for suffix, surface in (("test", "portal.test"), ("word", "reserved"), ("surrounding", "see portal.example now")):
            with self.subTest(rejected_reserved=surface):
                item = item_record(f"item_false_reserved_{suffix}", text=f"Actor {surface} token")
                item["visible_artifacts"] = [visible_artifact(item["text"], surface, representation="RESERVED")]
                refresh_vmp_hash(item)
                self.assertIn(
                    "visible_artifact_representation_coherence",
                    self.codes(self.validate([source_record()], [item], [])),
                )

        defanged_surfaces = (
            "safe[.]invalid", "safe(.)invalid", "name[at]reserved",
            "[redacted]", "hxxp:reserved", "hxxps:reserved", "XXXX",
        )
        for index, surface in enumerate(defanged_surfaces):
            with self.subTest(defanged=surface):
                item = item_record(f"item_defanged_{index}", text=f"Actor {surface} token")
                item["visible_artifacts"] = [visible_artifact(item["text"], surface, representation="DEFANGED")]
                refresh_vmp_hash(item)
                self.assertNotIn(
                    "visible_artifact_representation_coherence",
                    self.codes(self.validate([source_record()], [item], [])),
                )
        false_defanged = item_record("item_false_defanged", text="Actor defanged token")
        false_defanged["visible_artifacts"] = [visible_artifact(false_defanged["text"], "defanged", representation="DEFANGED")]
        refresh_vmp_hash(false_defanged)
        self.assertIn(
            "visible_artifact_representation_coherence",
            self.codes(self.validate([source_record()], [false_defanged], [])),
        )
        wrong_case_defanged = item_record("item_wrong_case_defanged", text="Actor [REDACTED] token")
        wrong_case_defanged["visible_artifacts"] = [visible_artifact(wrong_case_defanged["text"], "[REDACTED]", representation="DEFANGED")]
        refresh_vmp_hash(wrong_case_defanged)
        self.assertIn(
            "visible_artifact_representation_coherence",
            self.codes(self.validate([source_record()], [wrong_case_defanged], [])),
        )

    def test_destination_spans_are_bound_to_visible_artifact_kind(self) -> None:
        item = item_record()
        annotation = annotation_record(item, "destination_binding", label="phishing", structured=True)
        valid = self.validate([source_record()], [item], [annotation])
        self.assertFalse(
            {"destination_visible_artifact_mismatch", "destination_artifact_kind_mismatch"}
            & self.codes(valid),
            format_text(valid),
        )

        absent = deepcopy(item)
        absent["visible_artifacts"] = []
        refresh_vmp_hash(absent)
        self.assertIn(
            "destination_visible_artifact_mismatch",
            self.codes(self.validate([source_record()], [absent], [annotation])),
        )

        wrong_kind = deepcopy(annotation)
        wrong_kind["annotation_id"] = "annotation_destination_wrong_kind"
        destination = next(
            span_record for span_record in wrong_kind["spans"]
            if span_record["facet"] == "destination_artifact"
        )
        destination["qualifier"] = "URL"
        self.assertIn(
            "destination_artifact_kind_mismatch",
            self.codes(self.validate([source_record()], [item], [wrong_kind])),
        )

        no_converse = annotation_record(item, "destination_no_converse", structured=False)
        no_converse_report = self.validate([source_record()], [item], [no_converse])
        self.assertNotIn("destination_visible_artifact_mismatch", self.codes(no_converse_report))

    def test_surrogate_and_control_are_fixed_diagnostics(self) -> None:
        source_path = self.write_records("sources.jsonl", [source_record()])
        raw = json.dumps(item_record())
        item_path = self.directory / "items.jsonl"
        item_path.write_text(raw.replace("Actor", r"\ud800Actor", 1) + "\n" + raw.replace("Actor", r"\u0000Actor", 1) + "\n", encoding="utf-8")
        report = validate_files(source_path, item_path, self.write_records("annotations.jsonl", []), "draft")
        self.assertTrue({"forbidden_surrogate", "forbidden_control"} <= self.codes(report))
        self.assertNotIn("Actor", format_json(report))

    def test_live_routes_in_any_string_value_are_rejected_without_echo(self) -> None:
        values = [
            "person@example.com", "person@example\u3002com", "person@उदाहरण.भारत",
            "+91 98765 43210", "example.com", "https://example.com/path", "203.0.113.9",
        ]
        for index, value in enumerate(values):
            with self.subTest(index=index):
                source = source_record()
                source["provenance"]["origin_name"] = value
                report = self.validate([source], [], [])
                self.assertIn("live_artifact", self.codes(report))
                self.assertNotIn(value, format_json(report))
        source = source_record()
        source["provenance"]["origin_name"] = "person@sample.invalid portal.example safe[.]com"
        self.assertNotIn("live_artifact", self.codes(self.validate([source], [], [])))

    def test_schema_hash_date_duplicate_and_input_bounds(self) -> None:
        source = source_record()
        source["provenance"]["collected_date"] = "2026-02-30"
        source["artifact_sha256"] = "A" * 64
        first = item_record("item_first", text="ＡＢＣ reserved")
        second = item_record("item_second", text="abc   RESERVED")
        third = item_record("item_third", text="ＡＢＣ reserved")
        fourth = item_record("item_fourth", text="abc reserved")
        first["content_sha256"] = "0" * 64
        second["privacy"]["pii_reviewed"] = 1
        report = self.validate([source], [first, second, third, fourth], [])
        self.assertTrue({"invalid_date", "invalid_sha256", "content_hash_mismatch", "wrong_type", "exact_duplicate", "canonical_duplicate"} <= self.codes(report))
        long_item = item_record(text="a" * 10_001)
        self.assertIn("string_length_limit", self.codes(self.validate([source_record()], [long_item], [])))
        line_path = self.directory / "too_long.jsonl"
        line_path.write_text(" " * 1_000_001 + "\n", encoding="utf-8")
        bounded = validate_files(line_path, self.write_records("bounded_items.jsonl", []), self.write_records("bounded_annotations.jsonl", []), "draft")
        self.assertIn("line_length_limit", self.codes(bounded))

    def test_nesting_container_record_and_file_bounds(self) -> None:
        nested: object = "x"
        for _ in range(33):
            nested = [nested]
        path = self.directory / "nested.jsonl"
        path.write_text(json.dumps(nested) + "\n", encoding="utf-8")
        report = validate_files(path, self.write_records("items.jsonl", []), self.write_records("annotations.jsonl", []), "draft")
        self.assertIn("nesting_depth_limit", self.codes(report))
        source = source_record()
        source["eligible_partitions"] = ["pilot"] * 10_001
        self.assertIn("container_size_limit", self.codes(self.validate([source], [], [])))
        many = self.directory / "many.jsonl"
        many.write_text("{}\n" * 10_001, encoding="utf-8")
        many_report = validate_files(many, self.write_records("few_items.jsonl", []), self.write_records("few_annotations.jsonl", []), "draft")
        self.assertIn("record_count_limit", self.codes(many_report))
        oversized = self.directory / "oversized.jsonl"
        with oversized.open("wb") as stream:
            stream.truncate(512 * 1024 * 1024 + 1)
        size_report = validate_files(oversized, self.write_records("size_items.jsonl", []), self.write_records("size_annotations.jsonl", []), "draft")
        self.assertIn("file_size_limit", self.codes(size_report))

    @unittest.skipIf(sys.platform == "win32", "POSIX-only filesystem feature")
    def test_only_regular_files_are_opened_without_path_echo(self) -> None:
        items_path = self.write_records("safe_items.jsonl", [])
        annotations_path = self.write_records("safe_annotations.jsonl", [])
        regular = self.write_records("regular_sources.jsonl", [source_record()])
        directory = self.directory / "secret_directory"
        directory.mkdir()
        symlink = self.directory / "secret_symlink"
        symlink.symlink_to(regular)
        fifo = self.directory / "secret_fifo"
        os.mkfifo(fifo)
        cases = [directory, symlink, fifo]
        if Path("/dev/null").exists():
            cases.append(Path("/dev/null"))
        for path in cases:
            with self.subTest(kind=path.name):
                report = validate_files(path, items_path, annotations_path, "draft")
                self.assertIn("not_regular_file", self.codes(report))
                output = format_json(report)
                self.assertNotIn("secret_", output)
                self.assertNotIn(str(path), output)

    def test_post_fstat_file_growth_hits_cumulative_byte_bound(self) -> None:
        path = self.write_records("growing_sources.jsonl", [source_record("src_initial")])
        initial_size = path.stat().st_size
        extra = (json.dumps(source_record("src_appended"), separators=(",", ":")) + "\n").encode("utf-8")
        real_fstat = os.fstat
        append_descriptor = os.open(path, os.O_WRONLY | os.O_APPEND)
        grown = False

        def fstat_then_grow(descriptor: int):
            nonlocal grown
            metadata = real_fstat(descriptor)
            if not grown:
                os.write(append_descriptor, extra)
                os.fsync(append_descriptor)
                grown = True
            return metadata

        try:
            with (
                patch("fisher_data.validator.MAX_FILE_BYTES", initial_size + 1),
                patch("fisher_data.validator.os.fstat", side_effect=fstat_then_grow),
            ):
                report = validate_files(
                    path,
                    self.write_records("growing_items.jsonl", []),
                    self.write_records("growing_annotations.jsonl", []),
                    "draft",
                )
        finally:
            os.close(append_descriptor)
        self.assertTrue(grown)
        self.assertIn("file_size_limit", self.codes(report))
        self.assertEqual(report.counts["sources"], 0)

    def test_oversized_line_drain_cannot_bypass_post_fstat_byte_bound(self) -> None:
        path = self.write_records("growing_oversized_sources.jsonl", [source_record("src_initial")])
        initial_size = path.stat().st_size
        oversized_tail = b'{"' + (b"x" * 100) + b'"}\n'
        real_fstat = os.fstat
        append_descriptor = os.open(path, os.O_WRONLY | os.O_APPEND)
        grown = False

        def fstat_then_grow(descriptor: int):
            nonlocal grown
            metadata = real_fstat(descriptor)
            if not grown:
                os.write(append_descriptor, oversized_tail)
                os.fsync(append_descriptor)
                grown = True
            return metadata

        try:
            with (
                patch("fisher_data.validator.MAX_FILE_BYTES", initial_size + 20),
                patch("fisher_data.validator.MAX_LINE_CHARS", 8),
                patch("fisher_data.validator.os.fstat", side_effect=fstat_then_grow),
            ):
                report = validate_files(
                    path,
                    self.write_records("growing_oversized_items.jsonl", []),
                    self.write_records("growing_oversized_annotations.jsonl", []),
                    "draft",
                )
        finally:
            os.close(append_descriptor)
        self.assertTrue(grown)
        self.assertIn("file_size_limit", self.codes(report))
        self.assertNotIn("line_length_limit", self.codes(report))
        self.assertEqual(report.counts["sources"], 0)

    def test_crlf_raw_bytes_cross_bound_before_universal_newline_normalization(self) -> None:
        path = self.write_records("growing_crlf_sources.jsonl", [source_record("src_initial")])
        initial_size = path.stat().st_size
        crlf_record = b"{}\r\n"
        real_fstat = os.fstat
        append_descriptor = os.open(path, os.O_WRONLY | os.O_APPEND)
        grown = False

        def fstat_then_grow(descriptor: int):
            nonlocal grown
            metadata = real_fstat(descriptor)
            if not grown:
                os.write(append_descriptor, crlf_record)
                os.fsync(append_descriptor)
                grown = True
            return metadata

        try:
            with (
                patch("fisher_data.validator.MAX_FILE_BYTES", initial_size + 3),
                patch("fisher_data.validator.os.fstat", side_effect=fstat_then_grow),
            ):
                report = validate_files(
                    path,
                    self.write_records("growing_crlf_items.jsonl", []),
                    self.write_records("growing_crlf_annotations.jsonl", []),
                    "draft",
                )
        finally:
            os.close(append_descriptor)
        self.assertTrue(grown)
        self.assertEqual(len(crlf_record), 4)
        self.assertEqual(len(crlf_record.decode("utf-8").replace("\r\n", "\n")), 3)
        self.assertIn("file_size_limit", self.codes(report))
        self.assertEqual(report.counts["sources"], 0)

    def test_exclusion_contract_and_unresolved_denominator(self) -> None:
        item = item_record(partition="excluded")
        self.assertIn("excluded_reason_required", self.codes(self.validate([source_record()], [item], [])))
        item["exclusion_reasons"] = ["unresolved_primary_label", "duplicate_or_leakage"]
        self.assertIn("exclusion_reason_order", self.codes(self.validate([source_record()], [item], [])))
        retained = [item_record(f"item_r_{index}", text=f"Actor claim action asset [DOMAIN] pressure evidence token r {index}") for index in range(19)]
        excluded = item_record("item_u", text="Actor claim action asset [DOMAIN] pressure evidence token u", partition="excluded", exclusion_reasons=["unresolved_primary_label"])
        annotations: list[dict] = []
        for index, row in enumerate(retained):
            annotations.extend(complete_annotations(row, f"r_{index}", "benign", index % 2 == 0))
        unresolved = complete_annotations(excluded, "u", "benign", True)
        change_primary(unresolved[2], "uncertain")
        unresolved[2]["resolution_method"] = "unresolved"
        annotations.extend(unresolved)
        report = self.validate([source_record()], retained + [excluded], annotations)
        self.assertEqual(report.unresolved_final_items, 1)
        self.assertEqual(report.unresolved_final_rate, 0.05)

    def test_public_source_and_transitive_descendants_only_dev_or_external(self) -> None:
        public = source_record("src_public", provenance_class="public_authentic", eligible_partitions=["pilot", "development"])
        self.assertIn("public_source_partition_policy", self.codes(self.validate([public], [], [])))
        public = source_record("src_public", provenance_class="public_authentic")
        human = source_record()
        parent = item_record("item_public_parent", source_id="src_public", partition="development", component_id="component_public")
        middle = item_record("item_public_middle", text="Reserved middle lineage text", partition="development", component_id="component_public")
        middle["lineage"] = {"parent_item_ids": [parent["item_id"]], "operation": "translation"}
        child = item_record("item_public_child", text="Reserved child lineage text", partition="pilot", component_id="component_public")
        child["lineage"] = {"parent_item_ids": [middle["item_id"]], "operation": "paraphrase"}
        report = self.validate([public, human], [child, middle, parent], [])
        self.assertIn("public_partition_policy", self.codes(report))

    def test_linear_ancestry_propagation_and_cycles(self) -> None:
        llm_source = source_record("src_llm", provenance_class="llm_drafted_human_edited")
        human = source_record()
        parent = item_record("item_llm_parent", source_id="src_llm", partition="development", component_id="component_chain")
        parent["generation"] = {"method": "llm", "model_id": "reserved-model"}
        middle = item_record("item_llm_middle", text="Reserved chain middle", partition="development", component_id="component_chain")
        middle["lineage"] = {"parent_item_ids": [parent["item_id"]], "operation": "paraphrase"}
        child = item_record("item_llm_child", text="Reserved chain child", partition="primary_test", component_id="component_chain")
        child["lineage"] = {"parent_item_ids": [middle["item_id"]], "operation": "paraphrase"}
        report = self.validate([llm_source, human], [child, middle, parent], [])
        self.assertIn("llm_protected_partition", self.codes(report))
        first = item_record("item_cycle_a", component_id="component_cycle")
        second = item_record("item_cycle_b", text="Reserved cycle second", component_id="component_cycle")
        first["lineage"] = {"parent_item_ids": [second["item_id"]], "operation": "paraphrase"}
        second["lineage"] = {"parent_item_ids": [first["item_id"]], "operation": "translation"}
        cycle = self.validate([human], [first, second], [])
        self.assertEqual(sum(d.code == "lineage_cycle" for d in cycle.diagnostics), 2)

    def test_llm_ancestry_caps_development_and_pilot_separately(self) -> None:
        human = source_record()
        llm = source_record("src_llm", provenance_class="llm_drafted_human_edited")
        items: list[dict] = []
        for partition in ("development", "pilot"):
            for index in range(10):
                source_id = "src_llm" if index < 4 else "src_test"
                item = item_record(
                    f"item_{partition}_{index}",
                    text=f"Reserved {partition} message token {index}",
                    source_id=source_id,
                    partition=partition,
                )
                if source_id == "src_llm":
                    item["generation"] = {"method": "llm", "model_id": "reserved-model"}
                items.append(item)
        report = self.validate([human, llm], items, [])
        self.assertEqual(report.llm_development_share, 0.4)
        self.assertEqual(report.llm_pilot_share, 0.4)
        self.assertTrue({"llm_development_share", "llm_pilot_share"} <= self.codes(report))

    def test_partition_component_and_protected_singleton(self) -> None:
        first = item_record("item_a", partition="development", component_id="component_shared")
        second = item_record("item_b", text="Reserved different row", partition="external_test", component_id="component_shared")
        self.assertIn("partition_component_leakage", self.codes(self.validate([source_record()], [first, second], [])))
        first["partition"] = "probability_calibration"
        second["partition"] = "excluded"
        second["exclusion_reasons"] = ["duplicate_or_leakage"]
        self.assertIn("protected_component_not_singleton", self.codes(self.validate([source_record()], [first, second], [])))

    def test_token_inventory_script_and_derived_stratum_regressions(self) -> None:
        item = item_record()
        annotation = annotation_record(item, "tokens")
        annotation["token_language_spans"].pop()
        self.assertIn("token_inventory_mismatch", self.codes(self.validate([source_record()], [item], [annotation])))
        annotation = annotation_record(item, "script")
        annotation["token_language_spans"][0]["script"] = "devanagari"
        self.assertIn("token_script_mismatch", self.codes(self.validate([source_record()], [item], [annotation])))
        annotation = annotation_record(item, "derived")
        annotation["language_stratum"] = "tamil"
        self.assertIn("derived_language_stratum_mismatch", self.codes(self.validate([source_record()], [item], [annotation])))

    def test_all_tokens_count_and_removed_eligibility_field_rejects_old_exploit(self) -> None:
        words = [f"word{index}" for index in range(100)]
        item = item_record(text=" ".join(words))
        annotation = annotation_record(item, "ratio")
        for index, token in enumerate(annotation["token_language_spans"]):
            token["language"] = "en" if index < 99 else "hi"
        annotation["language_stratum"] = "hindi"
        annotation["code_mix_pair"] = "none"
        ratio = self.validate([source_record()], [item], [annotation])
        self.assertIn("derived_language_stratum_mismatch", self.codes(ratio))

        old_exploit = deepcopy(annotation)
        old_exploit["annotation_id"] = "annotation_removed_eligibility"
        for token in old_exploit["token_language_spans"][:99]:
            token["stratum_eligible"] = False
        exploit_report = self.validate([source_record()], [item], [old_exploit])
        self.assertIn("unknown_field", self.codes(exploit_report))

    def test_three_language_token_mix_is_not_a_two_language_code_mix(self) -> None:
        item = item_record(text="one two three")
        annotation = annotation_record(item, "three")
        for token, language in zip(annotation["token_language_spans"], ("en", "hi", "ta"), strict=True):
            token["language"] = language
        annotation["language_stratum"] = "english_indic_code_mixed"
        annotation["code_mix_pair"] = "en_hi"
        three = self.validate([source_record()], [item], [annotation])
        self.assertTrue({"derived_language_stratum_mismatch", "code_mix_pair"} <= self.codes(three))

    def test_final_language_consistency_and_third_annotator(self) -> None:
        item = item_record()
        annotations = complete_annotations(item, "final", "benign", True)
        change_language(annotations[2], item, "tamil")
        annotations[2]["annotator_id"] = "annotator_a"
        report = self.validate([source_record()], [item], annotations)
        self.assertTrue({"final_language_item_mismatch", "final_annotator_not_third"} <= self.codes(report))
        self.assertEqual(report.reliability.completeness, 0.0)
        uncertain_retained = item_record(language_stratum="uncertain")
        self.assertIn("uncertain_language_not_excluded", self.codes(self.validate([source_record()], [uncertain_retained], [])))
        excluded = item_record(partition="excluded", language_stratum="uncertain", exclusion_reasons=["unresolved_language_stratum"])
        unresolved = annotation_record(excluded, "lang_u", kind="final", annotator="annotator_final")
        change_language(unresolved, excluded, "uncertain")
        unresolved["resolution_method"] = "adjudicated"
        self.assertNotIn("uncertain_language_ambiguity", self.codes(self.validate([source_record()], [excluded], [unresolved])))

    def test_phishing_coherence_and_other_rationales(self) -> None:
        item = item_record()
        phishing = annotation_record(item, "empty", label="phishing")
        for facet in phishing["facets"]:
            facet["state"] = "not_applicable"
            facet["span_indices"] = []
        phishing["spans"] = [value for value in phishing["spans"] if value["facet"] == "supporting_evidence"]
        phishing["evidence_span_indices"] = [0]
        empty = self.validate([source_record()], [item], [phishing])
        self.assertTrue({"phishing_action_applicability", "phishing_asset_applicability", "phishing_semantically_empty"} <= self.codes(empty))
        benign = annotation_record(item, "other")
        benign["subtype"] = "other"
        self.assertIn("subtype_other_reason", self.codes(self.validate([source_record()], [item], [benign])))
        rich = annotation_record(item, "qualifier", label="phishing", structured=True)
        destination = next(value for value in rich["spans"] if value["facet"] == "destination_artifact")
        destination["qualifier"] = "OTHER"
        self.assertIn("qualifier_reason", self.codes(self.validate([source_record()], [item], [rich])))

    def test_romanization_integrity_and_adversarial_forms(self) -> None:
        item = item_record()
        annotation = annotation_record(item, "roman", label="phishing", structured=True)
        start = item["text"].index("claim")
        ambiguity = {
            "start": start, "end": start + 5, "text": "claim", "language": "hi",
            "acceptable_forms": [
                {"form": "daava", "script": "latin", "gloss": "reserved one"},
                {"form": "\u0926\u093e\u0935\u093e", "script": "devanagari", "gloss": "reserved two"},
            ],
            "affected_decisions": ["claim_or_problem", "primary_label"],
        }
        annotation["ambiguity_tags"] = ["romanization"]
        annotation["romanization_ambiguities"] = [ambiguity]
        accepted = self.validate([source_record()], [item], [annotation])
        self.assertFalse({"romanization_source_script", "romanization_forms", "romanization_form_script"} & self.codes(accepted), format_text(accepted))
        native_item = item_record(text="\u0926\u093e\u0935\u093e Actor claim action asset [DOMAIN] pressure evidence")
        native = annotation_record(native_item, "native", label="phishing", structured=True)
        native_ambiguity = deepcopy(ambiguity)
        native_ambiguity.update({"start": 0, "end": 4, "text": "\u0926\u093e\u0935\u093e"})
        native["ambiguity_tags"] = ["romanization"]
        native["romanization_ambiguities"] = [native_ambiguity]
        self.assertIn("romanization_source_script", self.codes(self.validate([source_record()], [native_item], [native])))
        duplicate = deepcopy(annotation)
        duplicate["annotation_id"] = "annotation_duplicate_forms"
        duplicate["romanization_ambiguities"][0]["acceptable_forms"] = [
            {"form": "daava", "script": "latin", "gloss": "one"},
            {"form": "daava", "script": "latin", "gloss": "different gloss"},
        ]
        self.assertIn("romanization_forms", self.codes(self.validate([source_record()], [item], [duplicate])))
        canonical_duplicates = {
            "case": ("daava", "DAAVA"),
            "compatibility": ("daava", "ｄａａｖａ"),
            "unicode_whitespace": ("daava", "\u2003\u2003daava\u00a0\t"),
        }
        for case_name, (first_form, second_form) in canonical_duplicates.items():
            with self.subTest(case_name=case_name):
                canonical_duplicate = deepcopy(annotation)
                canonical_duplicate["annotation_id"] = f"annotation_{case_name}_forms"
                canonical_duplicate["romanization_ambiguities"][0]["acceptable_forms"] = [
                    {"form": first_form, "script": "latin", "gloss": "one"},
                    {"form": second_form, "script": "latin", "gloss": "two"},
                ]
                result = self.validate([source_record()], [item], [canonical_duplicate])
                self.assertIn("romanization_forms", self.codes(result), format_text(result))
        lied = deepcopy(annotation)
        lied["annotation_id"] = "annotation_form_script_lie"
        lied["romanization_ambiguities"][0]["acceptable_forms"][0]["script"] = "devanagari"
        self.assertIn("romanization_form_script", self.codes(self.validate([source_record()], [item], [lied])))

    def test_annotation_relation_field_and_relation_ambiguity_decision_are_rejected(self) -> None:
        item = item_record()
        annotation = annotation_record(item, "registry", label="phishing", structured=True)
        annotation["actor_destination_relations"] = []
        self.assertIn("unknown_field", self.codes(self.validate([source_record()], [item], [annotation])))
        clean = annotation_record(item, "ambiguity", label="phishing", structured=True)
        start = item["text"].index("claim")
        clean["ambiguity_tags"] = ["romanization"]
        clean["romanization_ambiguities"] = [{
            "start": start,
            "end": start + 5,
            "text": "claim",
            "language": "hi",
            "acceptable_forms": [
                {"form": "daava", "script": "latin", "gloss": "one"},
                {"form": "\u0926\u093e\u0935\u093e", "script": "devanagari", "gloss": "two"},
            ],
            "affected_decisions": ["actor_destination_relation"],
        }]
        self.assertIn("invalid_value", self.codes(self.validate([source_record()], [item], [clean])))

    def test_blind_and_final_annotations_reject_registry_inputs(self) -> None:
        item = item_record()
        for kind, annotator in (("blind", "annotator_a"), ("final", "annotator_final")):
            with self.subTest(kind=kind):
                annotation = annotation_record(
                    item,
                    f"registry_input_{kind}",
                    kind=kind,
                    annotator=annotator,
                    label="phishing",
                    structured=True,
                )
                annotation["registry_snapshot_id"] = "registry_reserved_v1"
                annotation["registry_coverage"] = "complete"
                self.assertIn("unknown_field", self.codes(self.validate([source_record()], [item], [annotation])))

    def test_registry_reference_binding_coherence_and_reviewer_separation(self) -> None:
        item = item_record()
        annotations = complete_annotations(item, "registry", "phishing", True)
        final = annotations[2]
        reference = registry_reference(final, "valid")
        missing_manifest = self.validate([source_record()], [item], annotations, None, [reference])
        self.assertTrue({"registry_manifest_required", "registry_snapshot_unbound"} <= self.codes(missing_manifest))
        blocked = self.validate([source_record()], [item], annotations, [registry_record(approval="blocked")], [reference])
        self.assertNotIn("registry_snapshot_not_approved", self.codes(blocked))
        decisive = registry_reference(
            final,
            "decisive",
            label="MATCH",
            coverage="complete",
            evidence_ids=["registry_evidence_reserved"],
        )
        blocked_decisive = self.validate([source_record()], [item], annotations, [registry_record(approval="blocked")], [decisive])
        self.assertIn("registry_snapshot_not_approved", self.codes(blocked_decisive))
        approved = self.validate([source_record()], [item], annotations, [registry_record()], [decisive])
        self.assertFalse({"registry_snapshot_unbound", "registry_snapshot_not_approved", "registry_decisive_reference_incomplete"} & self.codes(approved), format_text(approved))
        decisive["registry_evidence_ids"] = []
        self.assertIn("registry_decisive_reference_incomplete", self.codes(self.validate([source_record()], [item], annotations, [registry_record()], [decisive])))
        decisive["registry_evidence_ids"] = ["registry_evidence_z", "registry_evidence_a", "registry_evidence_a"]
        self.assertIn("registry_evidence_order", self.codes(self.validate([source_record()], [item], annotations, [registry_record()], [decisive])))
        unknown_complete = registry_reference(final, "unknown_complete", coverage="complete")
        self.assertIn("registry_unknown_coverage", self.codes(self.validate([source_record()], [item], annotations, [registry_record()], [unknown_complete])))
        same_reviewer = registry_reference(final, "same_reviewer", reviewer="annotator_a")
        self.assertIn("registry_reviewer_not_separate", self.codes(self.validate([source_record()], [item], annotations, [registry_record()], [same_reviewer])))
        final_reviewer = registry_reference(final, "final_reviewer", reviewer="annotator_final")
        self.assertIn("registry_reviewer_not_separate", self.codes(self.validate([source_record()], [item], annotations, [registry_record()], [final_reviewer])))
        invalid_attestation = registry_reference(final, "attestation")
        invalid_attestation["blinding_attestation"] = "not_verified"
        self.assertIn("invalid_blinding_attestation", self.codes(self.validate([source_record()], [item], annotations, [registry_record()], [invalid_attestation])))
        blind_target = registry_reference(final, "blind_target")
        blind_target["final_annotation_id"] = annotations[0]["annotation_id"]
        self.assertIn("registry_final_annotation_unknown", self.codes(self.validate([source_record()], [item], annotations, [registry_record()], [blind_target])))
        unsafe_id = registry_reference(final, "unsafe")
        unsafe_id["registry_reference_id"] = "registry_reference_unsafe/value"
        self.assertIn("invalid_id", self.codes(self.validate([source_record()], [item], annotations, [registry_record()], [unsafe_id])))
        message_evidence = registry_reference(final, "message_evidence")
        del message_evidence["registry_evidence_ids"]
        message_evidence["evidence_span_indices"] = final["evidence_span_indices"]
        self.assertIn("unknown_field", self.codes(self.validate([source_record()], [item], annotations, [registry_record()], [message_evidence])))

    def test_registry_reference_cartesian_inventory_order_and_endpoints(self) -> None:
        item = item_record(
            text="Actor claim action asset [DOMAIN] pressure evidence token [BANK]"
        )
        annotations = complete_annotations(item, "cartesian", "phishing", True)
        final = annotations[2]
        final["spans"].extend([
            span(item["text"], "claim", "claimed_actor"),
            span(item["text"], "[BANK]", "destination_artifact", "BANK"),
        ])
        final["spans"].sort(key=lambda value: (value["start"], value["end"], value["facet"], value["qualifier"]))
        for facet in final["facets"]:
            facet["span_indices"] = [
                index for index, value in enumerate(final["spans"])
                if value["facet"] == facet["facet"]
            ]
        final["evidence_span_indices"] = [
            index for index, value in enumerate(final["spans"])
            if value["facet"] == "supporting_evidence"
        ]
        actors = next(facet["span_indices"] for facet in final["facets"] if facet["facet"] == "claimed_actor")
        destinations = next(facet["span_indices"] for facet in final["facets"] if facet["facet"] == "destination_artifact")
        references = [
            registry_reference(final, f"pair_{actor}_{destination}", actor_span_index=actor, destination_span_index=destination)
            for actor in actors for destination in destinations
        ]
        references.sort(key=lambda row: (row["item_id"], row["final_annotation_id"], row["actor_span_index"], row["destination_span_index"], row["registry_reference_id"]))
        report = self.validate([source_record()], [item], annotations, [registry_record()], references)
        self.assertEqual(report.registry_reference_inventory.applicable_endpoint_pairs, 4)
        self.assertFalse({"registry_reference_missing", "registry_reference_extra"} & self.codes(report), format_text(report))
        self.assertIn("registry_reference_missing", self.codes(self.validate([source_record()], [item], annotations, [registry_record()], references[:-1])))
        extra = deepcopy(references)
        duplicate = deepcopy(extra[0])
        duplicate["registry_reference_id"] = "registry_reference_duplicate"
        extra.append(duplicate)
        duplicate_report = self.validate([source_record()], [item], annotations, [registry_record()], extra)
        self.assertIn("duplicate_registry_endpoint_pair", self.codes(duplicate_report))
        duplicate_id_report = self.validate(
            [source_record()], [item], annotations, [registry_record()], [*references, deepcopy(references[0])]
        )
        self.assertIn("duplicate_record_id", self.codes(duplicate_id_report))
        reversed_report = self.validate([source_record()], [item], annotations, [registry_record()], list(reversed(references)))
        self.assertIn("registry_reference_order", self.codes(reversed_report))
        wrong_endpoint = deepcopy(references)
        wrong_endpoint[0]["actor_span_index"] = final["evidence_span_indices"][0]
        wrong_report = self.validate([source_record()], [item], annotations, [registry_record()], wrong_endpoint)
        self.assertTrue({"registry_actor_endpoint", "registry_reference_missing", "registry_reference_extra"} <= self.codes(wrong_report))

    def test_endpoint_reliability_remains_without_relation_metrics(self) -> None:
        sources, items, annotations, registry, references = pilot_dataset()
        items_by_id = {item["item_id"]: item for item in items}
        replaced = 0
        for index, annotation in enumerate(annotations):
            if annotation["kind"] == "blind" and annotation["annotator_id"] == "annotator_b" and any(facet["state"] == "explicit" for facet in annotation["facets"]) and replaced < 400:
                annotations[index] = annotation_record(
                    items_by_id[annotation["item_id"]], annotation["annotation_id"].removeprefix("annotation_"),
                    annotator="annotator_b", label=annotation["primary_label"], structured=True, offset_variant=True,
                )
                replaced += 1
        report = self.validate(sources, items, annotations, registry, references, mode="pilot-final")
        self.assertIn("facet_span_exact_f1_gate", self.codes(report))
        self.assertIn("endpoint_pair_structure_exact_f1_gate", self.codes(report))
        self.assertNotIn("relation_structure_exact_f1_gate", self.codes(report))
        self.assertEqual(set(report.reliability.per_stratum_alpha["hindi"]), {"claimed_actor", "destination_artifact", "requested_action"})

        left = annotation_record(item_record(), "endpoint_left", label="phishing", structured=True)
        swapped = deepcopy(left)
        actor_index = next(facet["span_indices"][0] for facet in swapped["facets"] if facet["facet"] == "claimed_actor")
        destination_index = next(facet["span_indices"][0] for facet in swapped["facets"] if facet["facet"] == "destination_artifact")
        actor_span = swapped["spans"][actor_index]
        destination_span = swapped["spans"][destination_index]
        actor_coordinates = (actor_span["start"], actor_span["end"], actor_span["text"])
        actor_span["start"], actor_span["end"], actor_span["text"] = destination_span["start"], destination_span["end"], destination_span["text"]
        destination_span["start"], destination_span["end"], destination_span["text"] = actor_coordinates
        self.assertEqual(_set_f1(_endpoint_pair_structures(left), _endpoint_pair_structures(swapped)), 0.0)

    def test_pilot_final_requires_registry_artifacts_and_zero_pair_state_is_explicit(self) -> None:
        sources, items, annotations, _, _ = pilot_dataset()
        missing = self.validate(sources, items, annotations, mode="pilot-final")
        self.assertTrue({"pilot_registry_manifest_required", "pilot_registry_references_required", "pilot_approved_registry_required"} <= self.codes(missing))
        items_by_id = {item["item_id"]: item for item in items}
        for index, annotation in enumerate(annotations):
            if annotation["kind"] == "final":
                annotations[index] = annotation_record(
                    items_by_id[annotation["item_id"]],
                    annotation["annotation_id"].removeprefix("annotation_"),
                    kind="final",
                    annotator=annotation["annotator_id"],
                    label=annotation["primary_label"],
                    structured=False,
                )
        zero_pairs = self.validate(sources, items, annotations, [registry_record()], [], mode="pilot-final")
        self.assertTrue(zero_pairs.valid, format_text(zero_pairs))
        self.assertTrue(zero_pairs.registry_reference_inventory.zero_applicable_pairs)
        self.assertEqual(zero_pairs.registry_reference_inventory.reference_records, 0)

    def test_unicode_code_point_offsets(self) -> None:
        text = "Actor 👍🏽 e\u0301 claim action asset [DOMAIN] pressure evidence token"
        item = item_record(text=text)
        annotation = annotation_record(item, "unicode", label="phishing", structured=True)
        annotation["spans"] = [span(text, "👍🏽", "supporting_evidence")]
        annotation["facets"] = [{"facet": facet, "state": "not_explicit" if facet in {"requested_action", "sensitive_item_or_asset"} else "not_applicable", "span_indices": []} for facet in FACETS]
        annotation["evidence_span_indices"] = [0]
        report = self.validate([source_record()], [item], [annotation])
        self.assertNotIn("span_text_mismatch", self.codes(report))
        self.assertNotIn("token_script_mismatch", self.codes(report))
        annotation["spans"][0]["text"] = "wrong"
        self.assertIn("span_text_mismatch", self.codes(self.validate([source_record()], [item], [annotation])))

    def test_nfc_and_nfd_latin_tokens_share_valid_observed_script(self) -> None:
        for suffix, form in (("nfc", "é"), ("nfd", "e\u0301")):
            with self.subTest(form=suffix):
                text = f"Actor claim action asset [DOMAIN] pressure evidence token {form}"
                item = item_record(f"item_{suffix}", text=text)
                annotation = annotation_record(item, suffix, label="phishing", structured=True)
                report = self.validate([source_record()], [item], [annotation])
                self.assertNotIn("token_script_mismatch", self.codes(report), format_text(report))
                lexical = annotation["token_language_spans"][-1]
                self.assertEqual(lexical["text"], form)
                self.assertEqual(lexical["script"], "latin")

    def test_cli_modes_help_and_deterministic_json(self) -> None:
        source_path = self.write_records("sources.jsonl", [source_record()])
        item = item_record()
        item_path = self.write_records("items.jsonl", [item])
        annotation_path = self.write_records("annotations.jsonl", complete_annotations(item, "cli", "benign", True))
        root = Path(__file__).resolve().parents[1]
        base = [sys.executable, "-m", "fisher_data", "validate", "--sources", str(source_path), "--items", str(item_path), "--annotations", str(annotation_path), "--format", "json"]
        draft = subprocess.run([*base, "--mode", "draft"], cwd=root, capture_output=True, check=False)
        repeated_draft = subprocess.run([*base, "--mode", "draft"], cwd=root, capture_output=True, check=False)
        final = subprocess.run([*base, "--mode", "pilot-final"], cwd=root, capture_output=True, text=True, check=False)
        corpus = subprocess.run([*base, "--mode", "corpus-final"], cwd=root, capture_output=True, text=True, check=False)
        malicious = subprocess.run([*base, "--mode", "SECRET-invalid-mode"], cwd=root, capture_output=True, text=True, check=False)
        help_result = subprocess.run([sys.executable, "-m", "fisher_data", "validate", "--help"], cwd=root, capture_output=True, text=True, check=False)
        self.assertEqual(draft.returncode, 0, draft.stderr)
        self.assertEqual(repeated_draft.returncode, 0, repeated_draft.stderr)
        self.assertEqual(draft.stdout, repeated_draft.stdout)
        self.assertEqual(draft.stderr, repeated_draft.stderr)
        self.assertTrue(json.loads(draft.stdout)["valid"])
        self.assertEqual(final.returncode, 1)
        self.assertEqual(corpus.returncode, 2)
        self.assertEqual(malicious.returncode, 2)
        self.assertNotIn("SECRET", malicious.stderr)
        self.assertEqual(help_result.returncode, 0)
        self.assertIn("--registry-manifest", help_result.stdout)
        self.assertIn("--registry-references", help_result.stdout)


if __name__ == "__main__":
    unittest.main()
