from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from fisher_engine.harness import (
    HarnessError,
    load_synthetic_fixture,
    run_synthetic_e0,
    run_synthetic_e0_bytes,
)
from fisher_engine.artifacts import ArtifactValidationError, validate_engine_envelope


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "examples/engine/synthetic_e0.json"


class SyntheticE0IntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.raw = FIXTURE.read_bytes()
        cls.result = run_synthetic_e0_bytes(cls.raw, project_root=ROOT)

    def test_all_eight_systems_and_two_metric_runs_pass(self) -> None:
        report = self.result.report
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["scope"], "SYNTHETIC_E0_ONLY")
        self.assertEqual(report["preflight_pass_count"], 8)
        self.assertEqual(report["valid_envelope_count"], 8)
        self.assertEqual(report["valid_metric_run_count"], 2)
        self.assertEqual(len(report["systems"]), 8)

    def test_provider_output_is_identical_across_factorial_and_controls(self) -> None:
        hashes = {run.provider_manifest_sha256 for run in self.result.candidate_runs.values()}
        self.assertEqual(len(hashes), 1)
        self.assertNotIn(None, hashes)
        bindings = {
            json.dumps(manifest["provider_binding"], separators=(",", ":"))
            for manifest in self.result.system_manifests.values()
        }
        self.assertEqual(len(bindings), 1)

    def test_rank_one_and_all_path_cells_are_factorially_distinct(self) -> None:
        candidate = self.result.candidate_runs["C00_BASE"]
        self.assertGreaterEqual(len(candidate.internal_paths), 2)
        q_values = [path.q for path in candidate.internal_paths]
        self.assertGreater(max(q_values), min(q_values))
        self.assertEqual(
            len(self.result.five_seed_artifacts["C00_BASE"]["active_path_ids"]), 1
        )
        self.assertEqual(
            len(self.result.five_seed_artifacts["C10_BASE"]["active_path_ids"]),
            len(candidate.internal_paths),
        )
        self.assertNotEqual(
            self.result.five_seed_artifacts["C00_BASE"],
            self.result.five_seed_artifacts["C10_BASE"],
        )
        self.assertEqual(len(self.result.semantic_artifacts["C01_BASE"]["paths"]), 1)
        self.assertEqual(
            len(self.result.semantic_artifacts["C11_BASE"]["paths"]),
            len(candidate.internal_paths),
        )

    def test_semantic_artifacts_exist_only_for_base_c01_and_c11(self) -> None:
        self.assertEqual(set(self.result.semantic_artifacts), {"C01_BASE", "C11_BASE"})
        for key, envelope in self.result.envelopes.items():
            semantic = key in self.result.semantic_artifacts
            self.assertEqual(envelope["prediction_audit_sha256"] is not None, semantic)
            self.assertEqual(bool(envelope["sep_packet_hashes"]), semantic)
            self.assertEqual(bool(envelope["feature_tensor_hashes"]), semantic)

    def test_synthetic_pair_known_answer_is_not_reported_as_performance(self) -> None:
        c01 = self.result.evaluation_results["C01_BASE"].metric_run
        c11 = self.result.evaluation_results["C11_BASE"].metric_run
        self.assertEqual(c01.manifest["status"], "VALID")
        self.assertEqual(c11.manifest["status"], "VALID")
        self.assertEqual(c01.pair_metrics["rank1"]["F1_pair"], 1.0)
        self.assertEqual(c11.pair_metrics["q_weighted"]["F1_pair"], 1.0)
        self.assertIn("NO_PERFORMANCE_CLAIM", self.result.report["claims"])
        self.assertIn("G5_G6_REMAIN_BLOCKED", self.result.report["claims"])

    def test_expected_nonhash_summary_is_frozen(self) -> None:
        expected = json.loads((ROOT / "examples/engine/expected_summary.json").read_text())
        projection = {
            "report_version": self.result.report["report_version"],
            "scope": self.result.report["scope"],
            "preflight_pass_count": self.result.report["preflight_pass_count"],
            "valid_envelope_count": self.result.report["valid_envelope_count"],
            "valid_metric_run_count": self.result.report["valid_metric_run_count"],
            "claims": self.result.report["claims"],
            "invalid_codes": self.result.report["invalid_codes"],
            "status": self.result.report["status"],
        }
        self.assertEqual(projection, expected)

    def test_same_process_replay_is_bit_identical(self) -> None:
        replay = run_synthetic_e0_bytes(self.raw, project_root=ROOT)
        self.assertEqual(replay.report, self.result.report)

    def test_envelope_validator_rejects_reviewer_mutations(self) -> None:
        key = "C10_BASE"
        context = self.result.validation_contexts[key]
        original = self.result.envelopes[key]
        mutations = []

        q_mutation = deepcopy(original)
        q_mutation["candidate_paths"][0]["q_f64_bits"] = "3fe0000000000000"
        mutations.append(q_mutation)

        span_mutation = deepcopy(original)
        span_mutation["candidate_paths"][0]["effective_rewrite_spans"][0]["source_text"] = "wrong"
        mutations.append(span_mutation)

        count_mutation = deepcopy(original)
        count_mutation["candidate_diagnostics"]["returned_count"] = 1
        mutations.append(count_mutation)

        failure_count_mutation = deepcopy(original)
        failure_count_mutation["failure_counts"] = {
            field: 0 for field in failure_count_mutation["failure_counts"]
        }
        mutations.append(failure_count_mutation)

        provider_mutation = deepcopy(original)
        provider_mutation["provider_execution"]["provider_manifest_sha256"] = "a" * 64
        mutations.append(provider_mutation)

        runtime_mutation = deepcopy(original)
        runtime_mutation["runtime"]["python_version"] = "9.9.9"
        mutations.append(runtime_mutation)

        for mutation in mutations:
            with self.subTest(field=next(k for k in mutation if mutation[k] != original[k])):
                with self.assertRaises(ArtifactValidationError):
                    validate_engine_envelope(mutation, context=context)

        with self.assertRaises(TypeError):
            validate_engine_envelope(original)  # type: ignore[call-arg]

    def test_invalid_fixture_fails_closed(self) -> None:
        value = json.loads(self.raw)
        value["scope"] = "AUTHENTIC"
        with self.assertRaisesRegex(HarnessError, "engine_fixture_scope"):
            run_synthetic_e0(value, project_root=ROOT)

    def test_excessively_nested_fixture_is_a_controlled_failure(self) -> None:
        raw = (b"[" * 65) + b"0" + (b"]" * 65)
        with self.assertRaises(HarnessError) as caught:
            load_synthetic_fixture(raw)
        self.assertEqual(caught.exception.code, "engine_fixture_invalid_json")


class EngineCliTests(unittest.TestCase):
    def command(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        environment = dict(os.environ)
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [sys.executable, "-m", "fisher_engine", *arguments],
            cwd=ROOT,
            env=environment,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_json_cli_is_deterministic_and_canonical(self) -> None:
        arguments = ("rehearse", "--fixture", str(FIXTURE), "--format", "json")
        first = self.command(*arguments)
        second = self.command(*arguments)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(second.returncode, 0, second.stderr)
        self.assertEqual(first.stdout, second.stdout)
        report = json.loads(first.stdout)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(first.stderr, "")

    def test_text_cli_is_explicitly_synthetic(self) -> None:
        completed = self.command("rehearse", "--fixture", str(FIXTURE), "--format", "text")
        self.assertEqual(completed.returncode, 0)
        self.assertIn("Fisher synthetic E0: PASS", completed.stdout)
        self.assertIn("no trained model, authentic data, or performance claim", completed.stdout)
        self.assertIn("G5/G6 remain blocked", completed.stdout)

    def test_invalid_usage_is_sanitized_exit_two(self) -> None:
        secret = "do-not-echo-this-value"
        completed = self.command("rehearse", "--fixture", secret, "--format", "unsafe")
        self.assertEqual(completed.returncode, 2)
        self.assertEqual(completed.stdout, "Fisher synthetic E0: INVALID_USAGE\n")
        self.assertNotIn(secret, completed.stdout + completed.stderr)

    def test_help_is_help_only_and_exits_zero(self) -> None:
        for arguments in (("--help",), ("rehearse", "--help")):
            with self.subTest(arguments=arguments):
                completed = self.command(*arguments)
                self.assertEqual(completed.returncode, 0)
                self.assertIn("usage:", completed.stdout)
                self.assertNotIn("INVALID_USAGE", completed.stdout + completed.stderr)
                self.assertEqual(completed.stderr, "")

    def test_nonregular_fixture_inputs_are_rejected_without_echo(self) -> None:
        with tempfile.TemporaryDirectory(dir=ROOT) as directory:
            temp_root = Path(directory)
            symlink = temp_root / "secret-symlink.json"
            symlink.symlink_to(FIXTURE)
            fifo = temp_root / "secret-fifo.json"
            os.mkfifo(fifo)
            for path in (symlink, fifo, temp_root):
                with self.subTest(kind=path.name):
                    completed = self.command(
                        "rehearse", "--fixture", str(path), "--format", "json"
                    )
                    self.assertEqual(completed.returncode, 1)
                    self.assertNotIn(str(path), completed.stdout + completed.stderr)
                    self.assertEqual(
                        json.loads(completed.stdout)["invalid_codes"],
                        ["engine_fixture_invalid_input"],
                    )

    def test_missing_fixture_is_sanitized_exit_one(self) -> None:
        secret_path = "/missing/do-not-echo-secret-fixture.json"
        completed = self.command("rehearse", "--fixture", secret_path, "--format", "json")
        self.assertEqual(completed.returncode, 1)
        self.assertNotIn(secret_path, completed.stdout + completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual(report["invalid_codes"], ["engine_internal_failure"])


if __name__ == "__main__":
    unittest.main()
