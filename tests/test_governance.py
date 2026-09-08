from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from fisher_governance.validator import _Validator, format_json, format_text, validate_ledger


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "data" / "source_ledger.example.jsonl"
FIXED_TIME = "2026-08-19T13:00:00+05:30"


def blocked_record(source_id: str = "src_synthetic_example_001") -> dict:
    record = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    record["source_id"] = source_id
    return record


def authorized_record(
    source_id: str = "src_authorized_synthetic",
    provenance: str = "TESTER_AUTHORED_SIMULATION",
) -> dict:
    record = blocked_record(source_id)
    record["provenance_class"] = provenance
    record["authenticity"] = {
        "TESTER_DONATED_AUTHENTIC": "AUTHENTIC",
        "TESTER_AUTHORED_SIMULATION": "SIMULATED",
        "PUBLIC_AUTHENTIC_AUXILIARY": "AUTHENTIC",
        "LLM_DRAFTED_HUMAN_EDITED": "LLM_ASSISTED",
    }[provenance]
    record["lifecycle_status"] = "AUTHORIZED"
    record["blockers"] = []
    record["origin"].update({"artifact_version": "synthetic-v1", "accessed_at": FIXED_TIME})
    record["artifact_hash"] = {"algorithm": "SHA-256", "value": "a" * 64}
    record["audited_record_count"] = 1
    record["authorization"] = {
        "status": "APPROVED",
        "reviewer": "reviewer-role",
        "reviewed_at": FIXED_TIME,
        "basis": "Synthetic unit-test approval shape only.",
    }
    participant = provenance in {"TESTER_DONATED_AUTHENTIC", "TESTER_AUTHORED_SIMULATION"}
    record["consent"] = {
        "required": participant,
        "status": "APPROVED" if participant else "NOT_APPLICABLE",
        "document_version": "consent-v1" if participant else None,
        "consent_reference_policy": "consent-policy-v1" if participant else None,
    }
    record["ethics"] = {
        "status": "EXEMPT",
        "authority": "Synthetic review authority",
        "identifier": "ethics-ref-v1",
        "effective_date": "2026-08-19",
    }
    record["license"].update({"reviewer": "license-reviewer", "reviewed_at": FIXED_TIME})
    record["release_tier"] = "NO_RELEASE"
    for review_name in ("privacy_review", "safety_review"):
        for key in record[review_name]:
            if key == "reviewer":
                record[review_name][key] = f"{review_name}-reviewer"
            elif key == "reviewed_at":
                record[review_name][key] = FIXED_TIME
            else:
                record[review_name][key] = "PASSED"
    for key in record["quality_audits"]:
        record["quality_audits"][key] = "PASSED"
    record["equivalence_policy"].update({
        "opaque_token_policy_version": "opaque-v1",
        "component_policy_version": "component-v1",
        "key_custodian": "custodian-role",
        "key_rotation_policy": "rotation-v1",
    })
    for key in record["partition_eligibility"]:
        if key != "rationale":
            record["partition_eligibility"][key] = False
    record["partition_eligibility"]["development"] = True
    record["partition_eligibility"]["rationale"] = "Synthetic unit-test eligibility only."
    record["steward"] = "steward-role"
    record["updated_at"] = "2026-08-19T14:00:00+05:30"
    record["lineage"].update({
        "source_family_id": f"family-{source_id}",
        "collection_batch_id": f"batch-{source_id}",
        "scenario_or_prompt_family_id": "scenario-synthetic-v1" if provenance in {
            "TESTER_AUTHORED_SIMULATION", "LLM_DRAFTED_HUMAN_EDITED"
        } else None,
        "model_id": "model-synthetic-v1" if provenance == "LLM_DRAFTED_HUMAN_EDITED" else None,
        "generation_batch_id": "generation-synthetic-v1" if provenance == "LLM_DRAFTED_HUMAN_EDITED" else None,
        "author_or_donor_batch_id": "human-batch-synthetic-v1" if provenance != "PUBLIC_AUTHENTIC_AUXILIARY" else None,
        "parent_source_ids": [],
        "has_public_ancestor": False,
        "has_llm_ancestor": False,
    })
    record["llm_fraction_scope"] = (
        "COUNTS_TOWARD_DEVELOPMENT_AND_PILOT_CAPS"
        if provenance == "LLM_DRAFTED_HUMAN_EDITED"
        else "NOT_APPLICABLE"
    )
    if provenance == "PUBLIC_AUTHENTIC_AUXILIARY":
        record["origin"]["landing_page"] = "https://official.example/source"
        record["license"].update({
            "status": "VERIFIED",
            "name_or_spdx": "Synthetic-Test-License",
            "text_url": "https://official.example/license",
            "version": "1.0",
            "research_use": True,
            "modification": True,
            "redistribution": True,
            "commercial_use": False,
        })
    return record


def write_ledger(directory: Path, records: list[dict], *, name: str = "ledger.jsonl") -> Path:
    path = directory / name
    path.write_text(
        "".join(json.dumps(record, ensure_ascii=True, separators=(",", ":")) + "\n" for record in records),
        encoding="utf-8",
    )
    return path


def diagnostic_codes(report) -> set[str]:
    return {diagnostic.code for diagnostic in report.diagnostics}


class GovernanceValidatorTests(unittest.TestCase):
    def run_records(self, records: list[dict]):
        with tempfile.TemporaryDirectory() as directory:
            return validate_ledger(write_ledger(Path(directory), records))

    def test_current_example_is_structurally_valid_but_collection_blocked(self) -> None:
        report = validate_ledger(EXAMPLE)
        self.assertTrue(report.schema_valid)
        self.assertFalse(report.collection_ready)
        self.assertEqual(report.readiness_state, "BLOCKED")
        self.assertEqual(report.counts["machine_authorization_ready"], 0)
        self.assertEqual(report.errors, 0)

    def test_authorized_shape_is_only_machine_ready_not_collection_ready(self) -> None:
        report = self.run_records([authorized_record()])
        self.assertTrue(report.schema_valid)
        self.assertEqual(report.counts["machine_authorization_ready"], 1)
        self.assertEqual(report.source_readiness[0].readiness_state, "HUMAN_REVIEW_REQUIRED")
        self.assertFalse(report.collection_ready)

    def test_human_unknowns_explicitly_cover_unstructured_governance(self) -> None:
        report = validate_ledger(EXAMPLE)
        gates = {gate.code: gate for gate in report.not_machine_verifiable}
        for code in (
            "data_controller_accountability", "secure_storage_jurisdiction",
            "retention_deletion_policy", "withdrawal_cutoff_controls",
            "incident_contact_drill", "native_reviewer_signoff",
            "provenance_and_lineage_truth", "artifact_hash_version_binding",
            "source_count_and_acquisition_time_truth", "reviewer_steward_identity_authority",
            "opaque_id_nonidentifiability", "llm_material_human_editing",
        ):
            self.assertEqual(gates[code].state, "UNKNOWN")
        self.assertEqual(gates["secure_storage_jurisdiction"].representation, "NOT_REPRESENTED")
        self.assertEqual(report.counts["human_unknown_gates"], 20)

    def test_unknown_top_level_field_rejected_without_echoing_key(self) -> None:
        record = blocked_record()
        record["https://secret.example.net/path"] = "value"
        report = self.run_records([record])
        output = format_text(report)
        self.assertIn("live_or_sensitive_artifact", diagnostic_codes(report))
        self.assertNotIn("secret.example.net", output)

        record = blocked_record()
        record["unexpected_private_field"] = "bounded value"
        report = self.run_records([record])
        self.assertIn("unknown_field", diagnostic_codes(report))
        self.assertNotIn("unexpected_private_field", format_text(report))

    def test_duplicate_nested_json_key_rejected(self) -> None:
        raw = EXAMPLE.read_text(encoding="utf-8").replace(
            '"required":true,"status"', '"required":true,"required":false,"status"', 1
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "ledger.jsonl"
            path.write_text(raw, encoding="utf-8")
            report = validate_ledger(path)
        self.assertIn("duplicate_json_key", diagnostic_codes(report))

    def test_non_object_blank_and_empty_ledgers_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            nonobject = base / "nonobject.jsonl"
            nonobject.write_text("[]\n\n", encoding="utf-8")
            report = validate_ledger(nonobject)
            self.assertIn("record_not_object", diagnostic_codes(report))
            self.assertIn("blank_line", diagnostic_codes(report))
            empty = base / "empty.jsonl"
            empty.write_text("", encoding="utf-8")
            self.assertFalse(validate_ledger(empty).schema_valid)

    def test_surrogate_control_and_malformed_utf8_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            surrogate = base / "surrogate.jsonl"
            surrogate.write_text('{"value":"\\ud800"}\n', encoding="utf-8")
            self.assertIn("forbidden_surrogate", diagnostic_codes(validate_ledger(surrogate)))
            control = base / "control.jsonl"
            control.write_text('{"value":"\\u0001"}\n', encoding="utf-8")
            self.assertIn("forbidden_control", diagnostic_codes(validate_ledger(control)))
            invalid = base / "invalid.jsonl"
            invalid.write_bytes(b"\xff\n")
            self.assertIn("invalid_utf8", diagnostic_codes(validate_ledger(invalid)))
            bidi = base / "bidi.jsonl"
            bidi.write_text('{"value":"safe\\u202etext"}\n', encoding="utf-8")
            self.assertIn("forbidden_bidi_control", diagnostic_codes(validate_ledger(bidi)))

    def test_live_routes_contacts_and_secret_values_rejected_in_general_strings(self) -> None:
        values = (
            "https://live.example.net/path", "user@live.example.net", "www.live.example.net",
            "203.0.113.25", "+91 98765 43210", "OTP: 482910",
            "x_password=Secret1234", "x_otp:482910", "x_9876543210", "x_8.8.8.8",
        )
        for index, value in enumerate(values):
            with self.subTest(index=index):
                record = blocked_record()
                record["description"] = value
                report = self.run_records([record])
                self.assertIn("live_or_sensitive_artifact", diagnostic_codes(report))
                self.assertNotIn(value, format_json(report))

    def test_reserved_and_defanged_artifacts_are_allowed(self) -> None:
        record = blocked_record()
        record["description"] = "Synthetic refs verify.example and verify[.]example are inert."
        report = self.run_records([record])
        self.assertTrue(report.schema_valid)

    def test_https_official_evidence_urls_are_allowlisted_but_never_fetched(self) -> None:
        for value in ("https://official.example/source", "https://official.example:443/source-v1"):
            with self.subTest(value=value):
                record = authorized_record(provenance="PUBLIC_AUTHENTIC_AUXILIARY")
                record["origin"]["landing_page"] = value
                report = self.run_records([record])
                self.assertTrue(report.schema_valid)
                self.assertEqual(report.counts["machine_authorization_ready"], 1)
                self.assertNotIn("official.example", format_text(report))

    def test_unsafe_official_evidence_urls_rejected(self) -> None:
        values = (
            "http://official.example/source",
            "https://user:secret@official.example/source",
            "https://127.0.0.1/source",
            "https://official.example/source?x_password=Secret1234",
            "https://official.example/source#fragment",
            "https://official.example\\@attacker.example/source",
            "https://official.example/%2e%2e/source",
            "https://official.example/\u202eevil",
            "https://-invalid.example/source",
            "https://invalid-.example/source",
            "https://under_score.example/source",
            "https://official.example:444/source",
            "https://official.example/../source",
            "https://xn--abc.example/source",
            "https://official.123/source",
        )
        for value in values:
            with self.subTest(value=value):
                record = authorized_record(provenance="PUBLIC_AUTHENTIC_AUXILIARY")
                record["origin"]["landing_page"] = value
                report = self.run_records([record])
                self.assertFalse(report.schema_valid)
                self.assertEqual(report.counts["machine_authorization_ready"], 0)
                self.assertNotIn(value, format_text(report))
                self.assertNotIn(value, format_json(report))

    def test_unsafe_source_and_opaque_identifiers_rejected(self) -> None:
        record = blocked_record("unsafe source id")
        report = self.run_records([record])
        self.assertIn("invalid_id", diagnostic_codes(report))
        record = blocked_record()
        record["lineage"]["source_family_id"] = "unsafe identifier with spaces"
        report = self.run_records([record])
        self.assertIn("unsafe_opaque_id", diagnostic_codes(report))

    def test_invalid_hash_date_timestamp_and_enum_rejected(self) -> None:
        mutations = (
            ("artifact_hash", lambda r: r.update(artifact_hash={"algorithm": "SHA-256", "value": "A" * 64}), "invalid_sha256"),
            ("ethics_date", lambda r: r["ethics"].update(status="APPROVED", authority="role", identifier="ref-v1", effective_date="2026-02-30"), "invalid_date"),
            ("timestamp", lambda r: r.update(updated_at="2026-08-19T14:00:00"), "invalid_timestamp"),
            ("enum", lambda r: r.update(lifecycle_status="READY"), "invalid_value"),
        )
        for name, mutation, code in mutations:
            with self.subTest(name=name):
                record = blocked_record()
                mutation(record)
                self.assertIn(code, diagnostic_codes(self.run_records([record])))

    def test_contradictory_approval_states_rejected(self) -> None:
        record = authorized_record()
        record["blockers"] = ["Still blocked"]
        self.assertIn("authorized_with_blockers", diagnostic_codes(self.run_records([record])))
        record = authorized_record()
        record["authorization"]["reviewer"] = None
        self.assertIn("missing_review_evidence", diagnostic_codes(self.run_records([record])))
        record = authorized_record()
        record["privacy_review"]["pii_scan"] = "PENDING"
        self.assertIn("contradictory_audit", diagnostic_codes(self.run_records([record])))

        record = blocked_record()
        record["equivalence_policy"]["raw_values_or_keys_in_ledger"] = True
        self.assertIn("raw_secret_material", diagnostic_codes(self.run_records([record])))

    def test_missing_owner_consent_and_core_reviews_block_authorization(self) -> None:
        mutations = (
            (lambda r: r.update(steward=None), "missing_steward"),
            (lambda r: r["consent"].update(status="NOT_STARTED", document_version=None, consent_reference_policy=None), "missing_consent_approval"),
            (lambda r: r["privacy_review"].update(status="PENDING", reviewer=None, reviewed_at=None), "privacy_review_incomplete"),
            (lambda r: r["safety_review"].update(status="PENDING", reviewer=None, reviewed_at=None), "safety_review_incomplete"),
            (lambda r: r["ethics"].update(status="PENDING"), "missing_ethics_approval"),
        )
        for mutation, code in mutations:
            with self.subTest(code=code):
                record = authorized_record()
                mutation(record)
                self.assertIn(code, diagnostic_codes(self.run_records([record])))

    def test_public_source_and_descendant_partition_restrictions(self) -> None:
        public = authorized_record("src_public", "PUBLIC_AUTHENTIC_AUXILIARY")
        public["partition_eligibility"]["primary_test"] = True
        report = self.run_records([public])
        self.assertIn("public_partition_violation", diagnostic_codes(report))

        public = authorized_record("src_public", "PUBLIC_AUTHENTIC_AUXILIARY")
        child = authorized_record("src_child")
        child["lineage"]["parent_source_ids"] = ["src_public"]
        child["lineage"]["has_public_ancestor"] = True
        child["partition_eligibility"]["development"] = False
        child["partition_eligibility"]["primary_test"] = True
        report = self.run_records([public, child])
        self.assertIn("public_partition_violation", diagnostic_codes(report))
        self.assertIn("primary_test_provenance", diagnostic_codes(report))

    def test_llm_direct_and_descendant_protected_restrictions(self) -> None:
        llm = authorized_record("src_llm", "LLM_DRAFTED_HUMAN_EDITED")
        llm["partition_eligibility"]["development"] = False
        llm["partition_eligibility"]["safety_threshold"] = True
        report = self.run_records([llm])
        self.assertIn("llm_protected_partition", diagnostic_codes(report))

        llm = authorized_record("src_llm", "LLM_DRAFTED_HUMAN_EDITED")
        child = authorized_record("src_child")
        child["lineage"]["parent_source_ids"] = ["src_llm"]
        child["lineage"]["has_llm_ancestor"] = True
        child["llm_fraction_scope"] = "COUNTS_TOWARD_DEVELOPMENT_AND_PILOT_CAPS"
        child["partition_eligibility"]["development"] = False
        child["partition_eligibility"]["probability_calibration"] = True
        report = self.run_records([llm, child])
        self.assertIn("llm_protected_partition", diagnostic_codes(report))

    def test_transitive_ancestry_flags_must_match_graph(self) -> None:
        public = authorized_record("src_public", "PUBLIC_AUTHENTIC_AUXILIARY")
        child = authorized_record("src_child")
        child["lineage"]["parent_source_ids"] = ["src_public"]
        report = self.run_records([public, child])
        self.assertIn("public_ancestry_mismatch", diagnostic_codes(report))

        llm = authorized_record("src_llm", "LLM_DRAFTED_HUMAN_EDITED")
        llm["llm_fraction_scope"] = "NOT_APPLICABLE"
        self.assertIn("llm_fraction_scope_mismatch", diagnostic_codes(self.run_records([llm])))

    def test_missing_parent_self_parent_and_cycle_rejected(self) -> None:
        child = authorized_record("src_child")
        child["lineage"]["parent_source_ids"] = ["src_missing"]
        self.assertIn("missing_parent_source", diagnostic_codes(self.run_records([child])))

        child = authorized_record("src_child")
        child["lineage"]["parent_source_ids"] = ["src_child"]
        self.assertIn("self_parent", diagnostic_codes(self.run_records([child])))

        left = authorized_record("src_left")
        right = authorized_record("src_right")
        left["lineage"]["parent_source_ids"] = ["src_right"]
        right["lineage"]["parent_source_ids"] = ["src_left"]
        report = self.run_records([left, right])
        self.assertIn("source_lineage_cycle", diagnostic_codes(report))

    def test_release_tier_cannot_exceed_verified_rights(self) -> None:
        record = authorized_record(provenance="PUBLIC_AUTHENTIC_AUXILIARY")
        record["release_tier"] = "PUBLIC_TEXT"
        record["license"]["redistribution"] = False
        self.assertIn("release_exceeds_rights", diagnostic_codes(self.run_records([record])))

        record = authorized_record(provenance="PUBLIC_AUTHENTIC_AUXILIARY")
        record["release_tier"] = "DEIDENTIFIED_TEXT"
        record["license"]["modification"] = False
        report = self.run_records([record])
        self.assertIn("release_exceeds_rights", diagnostic_codes(report))
        self.assertEqual(report.counts["machine_authorization_ready"], 0)

        record = authorized_record(provenance="PUBLIC_AUTHENTIC_AUXILIARY")
        record["release_tier"] = "DERIVED_ONLY"
        record["license"]["modification"] = False
        self.assertIn("release_exceeds_rights", diagnostic_codes(self.run_records([record])))

        record = authorized_record(provenance="PUBLIC_AUTHENTIC_AUXILIARY")
        record["release_tier"] = "PUBLIC_TEXT"
        record["license"]["modification"] = False
        report = self.run_records([record])
        self.assertTrue(report.schema_valid)
        self.assertEqual(report.counts["machine_authorization_ready"], 1)

    def test_active_verified_license_requires_affirmative_research_use(self) -> None:
        record = authorized_record(provenance="PUBLIC_AUTHENTIC_AUXILIARY")
        record["license"]["research_use"] = False
        report = self.run_records([record])
        self.assertIn("research_use_not_permitted", diagnostic_codes(report))
        self.assertFalse(report.schema_valid)
        self.assertEqual(report.counts["machine_authorization_ready"], 0)

    def test_long_chain_and_every_cycle_dependent_are_iteratively_rejected(self) -> None:
        records = [authorized_record(f"src_chain_{index:04d}") for index in range(1_200)]
        for index in range(1, len(records)):
            records[index]["lineage"]["parent_source_ids"] = [records[index - 1]["source_id"]]
        report = self.run_records(records)
        self.assertTrue(report.schema_valid)
        self.assertEqual(report.counts["machine_authorization_ready"], 1_200)

        cycle = [authorized_record(f"src_cycle_{index}") for index in range(3)]
        cycle[0]["lineage"]["parent_source_ids"] = [cycle[2]["source_id"]]
        cycle[1]["lineage"]["parent_source_ids"] = [cycle[0]["source_id"]]
        cycle[2]["lineage"]["parent_source_ids"] = [cycle[1]["source_id"]]
        dependent = authorized_record("src_cycle_dependent")
        dependent["lineage"]["parent_source_ids"] = [cycle[2]["source_id"]]
        report = self.run_records([*cycle, dependent])
        unresolved = {
            diagnostic.record_id
            for diagnostic in report.diagnostics
            if diagnostic.code == "source_lineage_cycle"
        }
        self.assertEqual(unresolved, {record["source_id"] for record in [*cycle, dependent]})
        self.assertEqual(report.counts["machine_authorization_ready"], 0)

    def test_active_descendants_require_active_machine_ready_ancestry(self) -> None:
        for lifecycle in ("PROPOSED", "BLOCKED", "REJECTED", "WITHDRAWN"):
            with self.subTest(lifecycle=lifecycle):
                parent = blocked_record(f"src_{lifecycle.casefold()}_parent")
                parent["lifecycle_status"] = lifecycle
                if lifecycle == "REJECTED":
                    parent["authorization"].update({
                        "status": "REJECTED", "reviewer": "reviewer-role", "reviewed_at": FIXED_TIME,
                    })
                if lifecycle == "WITHDRAWN":
                    parent["consent"]["status"] = "WITHDRAWN"
                child = authorized_record(f"src_{lifecycle.casefold()}_child")
                child["lineage"]["parent_source_ids"] = [parent["source_id"]]
                grandchild = authorized_record(f"src_{lifecycle.casefold()}_grandchild")
                grandchild["lineage"]["parent_source_ids"] = [child["source_id"]]
                report = self.run_records([parent, child, grandchild])
                ancestry_errors = {
                    diagnostic.record_id
                    for diagnostic in report.diagnostics
                    if diagnostic.code == "ancestor_not_machine_authorized"
                }
                self.assertEqual(ancestry_errors, {child["source_id"], grandchild["source_id"]})
                self.assertEqual(report.counts["machine_authorization_ready"], 0)

        invalid_parent = authorized_record("src_invalid_parent")
        invalid_parent["safety_review"]["status"] = "PENDING"
        invalid_parent["safety_review"]["reviewer"] = None
        invalid_parent["safety_review"]["reviewed_at"] = None
        child = authorized_record("src_child_of_invalid")
        child["lineage"]["parent_source_ids"] = [invalid_parent["source_id"]]
        report = self.run_records([invalid_parent, child])
        self.assertIn("ancestor_not_machine_authorized", diagnostic_codes(report))
        self.assertEqual(report.counts["machine_authorization_ready"], 0)

    def test_llm_shape_remains_explicitly_human_gated(self) -> None:
        report = self.run_records([authorized_record(provenance="LLM_DRAFTED_HUMAN_EDITED")])
        self.assertTrue(report.schema_valid)
        self.assertEqual(report.counts["machine_authorization_ready"], 1)
        self.assertFalse(report.collection_ready)
        gates = {gate.code: gate for gate in report.not_machine_verifiable}
        self.assertEqual(gates["llm_material_human_editing"].state, "UNKNOWN")
        self.assertEqual(report.source_readiness[0].readiness_state, "HUMAN_REVIEW_REQUIRED")

    def test_ten_thousand_node_worst_order_graph_sanity(self) -> None:
        validator = _Validator()
        for index in reversed(range(10_000)):
            source_id = f"src_perf_{index:05d}"
            parent_ids = [f"src_perf_{index - 1:05d}"] if index else []
            record = {
                "provenance_class": "TESTER_AUTHORED_SIMULATION",
                "lineage": {
                    "parent_source_ids": parent_ids,
                    "has_public_ancestor": False,
                    "has_llm_ancestor": False,
                },
                "partition_eligibility": {
                    **{partition: False for partition in (
                        "pilot", "unassigned", "development", "probability_calibration",
                        "safety_threshold", "primary_test", "external_test", "excluded",
                    )},
                    "rationale": "Synthetic graph-only performance fixture.",
                },
                "llm_fraction_scope": "NOT_APPLICABLE",
            }
            validator.records[source_id] = (index + 1, record)
        started = time.monotonic()
        validator.validate_graph_and_partitions()
        elapsed = time.monotonic() - started
        self.assertEqual(validator.diagnostics, [])
        self.assertLess(elapsed, 5.0)

    def test_cli_argument_errors_are_fixed_and_never_echo_values(self) -> None:
        malicious = "x_password=Secret1234\nSECOND-LINE"
        command = [
            sys.executable, "-m", "fisher_governance", "validate", "--ledger", str(EXAMPLE),
            "--format", malicious,
        ]
        environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        result = subprocess.run(command, cwd=ROOT, env=environment, capture_output=True, check=False)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, b"")
        self.assertNotIn(malicious.encode(), result.stderr)
        self.assertNotIn(b"Secret1234", result.stderr)
        self.assertNotIn(b"SECOND-LINE", result.stderr)
        self.assertIn(b"invalid command-line arguments", result.stderr)

    def test_input_must_be_a_regular_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            fifo = base / "ledger.fifo"
            os.mkfifo(fifo)
            self.assertIn("not_regular_file", diagnostic_codes(validate_ledger(fifo)))

            fifo_link = base / "ledger-link"
            fifo_link.symlink_to(fifo)
            self.assertIn("not_regular_file", diagnostic_codes(validate_ledger(fifo_link)))

            self.assertIn("not_regular_file", diagnostic_codes(validate_ledger(base)))
            self.assertIn("not_regular_file", diagnostic_codes(validate_ledger(Path("/dev/null"))))

            regular_link = base / "regular-link"
            regular_link.symlink_to(EXAMPLE)
            self.assertTrue(validate_ledger(regular_link).schema_valid)

    def test_post_fstat_growth_hits_cumulative_byte_limit_before_parsing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            path = write_ledger(base, [blocked_record("src_initial")])
            initial_size = path.stat().st_size
            extra = (
                json.dumps(blocked_record("src_appended"), ensure_ascii=True, separators=(",", ":"))
                + "\n"
            ).encode("utf-8")
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
                started = time.monotonic()
                with (
                    patch("fisher_governance.validator.MAX_FILE_BYTES", initial_size + 1),
                    patch("fisher_governance.validator.os.fstat", side_effect=fstat_then_grow),
                ):
                    report = validate_ledger(path)
                elapsed = time.monotonic() - started
            finally:
                os.close(append_descriptor)

        self.assertTrue(grown)
        self.assertIn("file_size_limit", diagnostic_codes(report))
        self.assertNotIn("invalid_utf8", diagnostic_codes(report))
        self.assertEqual(report.counts["sources"], 0)
        self.assertEqual(report.source_readiness, ())
        self.assertLess(elapsed, 1.0)

    def test_line_and_nesting_resource_limits(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            line_path = base / "line.jsonl"
            line_path.write_text("{" + "x" * 80 + "}\n", encoding="utf-8")
            with patch("fisher_governance.validator.MAX_LINE_CHARS", 40):
                self.assertIn("line_length_limit", diagnostic_codes(validate_ledger(line_path)))

            nested: object = "value"
            for _ in range(35):
                nested = [nested]
            nested_path = base / "nested.jsonl"
            nested_path.write_text(json.dumps(nested) + "\n", encoding="utf-8")
            self.assertIn("nesting_depth_limit", diagnostic_codes(validate_ledger(nested_path)))

            count_path = write_ledger(base, [blocked_record("src_one"), blocked_record("src_two")], name="count.jsonl")
            with patch("fisher_governance.validator.MAX_RECORDS", 1):
                self.assertIn("record_count_limit", diagnostic_codes(validate_ledger(count_path)))

    def test_duplicate_source_id_and_provenance_authenticity_mismatch(self) -> None:
        report = self.run_records([blocked_record(), blocked_record()])
        self.assertIn("duplicate_record_id", diagnostic_codes(report))
        record = blocked_record()
        record["authenticity"] = "AUTHENTIC"
        self.assertIn("authenticity_mismatch", diagnostic_codes(self.run_records([record])))

    def test_output_is_byte_deterministic_and_sanitized(self) -> None:
        report = validate_ledger(EXAMPLE)
        self.assertEqual(format_json(report), format_json(validate_ledger(EXAMPLE)))
        self.assertEqual(format_text(report), format_text(validate_ledger(EXAMPLE)))
        command = [
            sys.executable, "-m", "fisher_governance", "validate", "--ledger", str(EXAMPLE),
            "--format", "json",
        ]
        environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
        first = subprocess.run(command, cwd=ROOT, env=environment, capture_output=True, check=False)
        second = subprocess.run(command, cwd=ROOT, env=environment, capture_output=True, check=False)
        self.assertEqual(first.returncode, 1)
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(first.stderr, b"")
        self.assertNotIn(b"verify.example", first.stdout)


if __name__ == "__main__":
    unittest.main()
