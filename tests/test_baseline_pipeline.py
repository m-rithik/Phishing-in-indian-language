from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import pandas as pd

from fisher_baselines.cli import main
from fisher_baselines.data import (
    DataValidationError,
    defang_text,
    prepare_dataframe,
    script_category,
    template_group_id,
)
from fisher_baselines.evaluation import (
    EvaluationError,
    assign_folds,
    evaluate_dataframe,
    write_evaluation_outputs,
)


class DataPreparationTests(unittest.TestCase):
    def test_conservative_contamination_and_deduplication(self) -> None:
        frame = pd.DataFrame(
            {
                " Message ": [
                    "Pay NOW",
                    " pay   now ",
                    "Hello",
                    " hello ",
                    "Offer",
                    "offer",
                    123,
                    "",
                    "Okay",
                    "Maybe",
                    "Unique spam",
                ],
                "Type ": [
                    "Spam",
                    "Spa,",
                    "Ham",
                    " ham ",
                    "Spam",
                    "Ham",
                    "Ham",
                    "Spam",
                    "",
                    "Promotion",
                    "Spam",
                ],
            }
        )

        prepared, audit = prepare_dataframe(frame)

        self.assertEqual(list(prepared["label"]), ["ham", "spam"])
        self.assertEqual(audit["dispositions"]["contaminated_duplicate_groups"], 2)
        self.assertEqual(audit["dispositions"]["quarantined_contaminated_binary_rows"], 3)
        self.assertEqual(audit["dispositions"]["deduplicated_binary_rows_removed"], 1)
        self.assertEqual(audit["dispositions"]["quarantined_invalid_text_rows"], 2)
        self.assertEqual(audit["dispositions"]["quarantined_blank_label_rows"], 1)
        self.assertEqual(audit["dispositions"]["quarantined_unknown_label_rows"], 2)
        self.assertEqual(audit["dispositions"]["retained_rows"], 2)

    def test_schema_is_exact_after_header_trimming(self) -> None:
        valid = pd.DataFrame({" Message ": ["hello"], " Type ": ["Ham"]})
        prepared, _ = prepare_dataframe(valid)
        self.assertEqual(len(prepared), 1)

        extra = valid.assign(Source="tester")
        with self.assertRaises(DataValidationError):
            prepare_dataframe(extra)

    def test_record_and_group_ids_are_deterministic(self) -> None:
        frame = pd.DataFrame(
            {
                "Message": ["ordinary alpha", "urgent beta", "meeting gamma", "claim delta"],
                "Type": ["Ham", "Spam", "Ham", "Spam"],
            }
        )
        first, _ = prepare_dataframe(frame)
        second, _ = prepare_dataframe(frame.copy(deep=True))
        self.assertEqual(
            first[["record_id", "group_id"]].to_dict("records"),
            second[["record_id", "group_id"]].to_dict("records"),
        )

    def test_format_controls_cannot_split_duplicate_groups(self) -> None:
        frame = pd.DataFrame(
            {
                "Message": ["pay\u200bnow", "paynow"],
                "Type": ["Spam", "Ham"],
            }
        )
        prepared, audit = prepare_dataframe(frame)
        self.assertTrue(prepared.empty)
        self.assertEqual(audit["dispositions"]["contaminated_duplicate_groups"], 1)
        self.assertEqual(audit["dispositions"]["quarantined_contaminated_binary_rows"], 2)


class TextSafetyTests(unittest.TestCase):
    def test_defangs_supported_live_artifacts(self) -> None:
        cases = {
            "Visit https://secure.example.com/path?q=1": "[URL]",
            "Write to user@example.com": "[EMAIL]",
            "Pay alice@okaxis": "[UPI]",
            "Call +91 98765 43210": "[PHONE]",
            "Server 192.0.2.1": "[IPV4]",
            "Server 2001:db8::1": "[IPV6]",
            "Open bank\u3002example": "[DOMAIN]",
            "Open \u0909\u0926\u093e\u0939\u0930\u0923.\u092d\u093e\u0930\u0924": "[DOMAIN]",
        }
        for raw, placeholder in cases.items():
            with self.subTest(placeholder=placeholder):
                safe = defang_text(raw)
                self.assertIn(placeholder, safe)
                self.assertNotEqual(raw, safe)
                self.assertEqual(defang_text(safe), safe)

    def test_script_categories_are_mechanical(self) -> None:
        self.assertEqual(script_category("hello"), "latin")
        self.assertEqual(script_category("\u0bb5\u0ba3\u0b95\u0bcd\u0b95\u0bae\u0bcd"), "tamil")
        self.assertEqual(script_category("\u0c28\u0bae\u0c38\u0c4d\u0c15\u0c3e\u0c30\u0c02"), "telugu")
        self.assertEqual(script_category("\u0ca8\u0cae\u0cb8\u0ccd\u0c95\u0cbe\u0cb0"), "kannada")
        self.assertEqual(script_category("\u0d28\u0d2e\u0d38\u0d4d\u0d15\u0d3e\u0d30\u0d02"), "malayalam")
        self.assertEqual(script_category("ab\u0b85\u0b86"), "mixed")
        self.assertEqual(script_category("abcdefg\u0b85\u0b86\u0b87"), "latin")
        self.assertEqual(script_category("abcdef\u0b85\u0b86\u0b87\u0b88"), "mixed")
        self.assertEqual(script_category("123 !!!"), "no_letters")

    def test_template_group_ignores_artifact_and_number_variants(self) -> None:
        first = defang_text("Your code 123 is at https://a.example/path")
        second = defang_text("Your code 999 is at https://b.example/other")
        self.assertEqual(template_group_id(first), template_group_id(second))
        self.assertEqual(template_group_id("pay\u200bnow"), template_group_id("paynow"))

    def test_raw_scanner_counts_are_separate_from_residual_quarantine(self) -> None:
        frame = pd.DataFrame(
            {
                "Message": ["Visit https://one.example/path", "ordinary note"],
                "Type": ["Spam", "Ham"],
            }
        )
        _, audit = prepare_dataframe(frame)
        self.assertEqual(audit["raw_pre_defang_artifact_counts"]["url"], 1)
        self.assertEqual(audit["dispositions"]["quarantined_residual_artifact_rows"], 0)

    def test_independent_residual_candidates_are_quarantined_by_category(self) -> None:
        frame = pd.DataFrame(
            {
                "Message": [
                    "Open https : / / secure portal",
                    "Open bank . example",
                    "Pay alice@bank",
                    "Call +91 98765\u200b43210",
                    "ordinary note",
                ],
                "Type": ["Spam", "Spam", "Spam", "Spam", "Ham"],
            }
        )
        prepared, audit = prepare_dataframe(frame)
        self.assertEqual(list(prepared["label"]), ["ham"])
        self.assertEqual(audit["dispositions"]["quarantined_residual_artifact_rows"], 4)
        self.assertEqual(
            audit["post_defang_residual_candidate_counts"],
            {"spaced_http": 1, "spaced_domain": 1, "undotted_handle": 1, "broad_phone": 1},
        )
        self.assertEqual(audit["post_defang_residual_candidate_rows"], 4)


def evaluation_frame() -> pd.DataFrame:
    ham_suffixes = [
        "alpha", "bravo", "charlie", "delta", "echo", "foxtrot",
        "golf", "hotel", "india", "juliet", "kilo", "lima",
    ]
    spam_suffixes = [
        "mango", "nectar", "olive", "pearl", "quartz", "raven",
        "solar", "tiger", "umber", "vivid", "whale", "xenon",
    ]
    return pd.DataFrame(
        {
            "Message": [f"family meeting schedule {word}" for word in ham_suffixes]
            + [f"urgent prize claim {word}" for word in spam_suffixes],
            "Type": ["Ham"] * len(ham_suffixes) + ["Spam"] * len(spam_suffixes),
        }
    )


class EvaluationTests(unittest.TestCase):
    def test_fold_assignment_is_deterministic_and_group_disjoint(self) -> None:
        prepared, _ = prepare_dataframe(evaluation_frame())
        first = assign_folds(prepared, folds=3, seed=1729)
        second = assign_folds(prepared, folds=3, seed=1729)
        self.assertEqual(first.tolist(), second.tolist())
        fold_sets = prepared.assign(fold=first).groupby("group_id")["fold"].nunique()
        self.assertTrue((fold_sets == 1).all())

    def test_outputs_are_aggregate_only_and_message_free(self) -> None:
        secret = "raw-secret-phrase-never-write"
        frame = evaluation_frame()
        frame.loc[0, "Message"] = f"family meeting schedule alpha {secret}"
        result = evaluate_dataframe(frame, folds=3, seed=1729, workbook_sha256="a" * 64)

        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory)
            write_evaluation_outputs(result, output_dir)

            self.assertEqual(
                {path.name for path in output_dir.iterdir()},
                {"audit.json", "run_manifest.json", "metrics.json"},
            )
            for path in output_dir.iterdir():
                self.assertNotIn(secret, path.read_text(encoding="utf-8"))
                self.assertNotIn("model_text", path.read_text(encoding="utf-8"))

            manifest = json.loads((output_dir / "run_manifest.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["evaluation_scope"], "development_only")
            self.assertEqual(manifest["split"]["group_cross_fold_violations"], 0)
            self.assertIn("split_manifest_sha256", manifest["split"])
            self.assertNotIn("predictions_model", manifest)
            self.assertIn("not calibrated", manifest["metric_interpretation"]["pooled_oof_average_precision"])

            metrics = json.loads((output_dir / "metrics.json").read_text(encoding="utf-8"))
            for model_metrics in metrics["models"].values():
                self.assertIn("mean_per_fold_average_precision", model_metrics)

    def test_occupied_output_directory_fails_without_deleting_legacy_file(self) -> None:
        result = evaluate_dataframe(
            evaluation_frame(), folds=3, seed=1729, workbook_sha256="a" * 64
        )
        with tempfile.TemporaryDirectory() as directory:
            output_dir = Path(directory) / "occupied"
            output_dir.mkdir()
            legacy = output_dir / "predictions.csv"
            legacy.write_text("sentinel", encoding="utf-8")

            with self.assertRaises(EvaluationError):
                write_evaluation_outputs(result, output_dir)

            self.assertEqual(legacy.read_text(encoding="utf-8"), "sentinel")
            self.assertEqual({path.name for path in output_dir.iterdir()}, {"predictions.csv"})


class CliSafetyTests(unittest.TestCase):
    def test_validation_error_does_not_echo_path_or_secret(self) -> None:
        hidden = "private-path-secret"
        stdout = io.StringIO()
        stderr = io.StringIO()
        with patch(
            "fisher_baselines.cli.audit_workbook",
            side_effect=DataValidationError("do not propagate details"),
        ), redirect_stdout(stdout), redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as raised:
                main(["audit", "--workbook", f"/{hidden}.xlsx", "--output", "audit.json"])
        self.assertEqual(raised.exception.code, 2)
        combined = stdout.getvalue() + stderr.getvalue()
        self.assertNotIn(hidden, combined)
        self.assertNotIn("do not propagate details", combined)


if __name__ == "__main__":
    unittest.main()
