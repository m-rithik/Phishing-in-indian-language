from __future__ import annotations

from contextlib import redirect_stderr
import io
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np
import pandas as pd

from fisher_baselines.cli import main
from fisher_baselines.data import prepare_dataframe
from fisher_baselines.evaluation import EvaluationError
from fisher_baselines.holdout import (
    ABLATION,
    expected_calibration_error,
    holdout_evaluate_prepared,
    normalize_model_input,
    rule_engine_scores,
    threshold_for_fpr,
    write_holdout_output,
)

WORDS = "alpha bravo charlie delta echo foxtrot golf hotel india juliet kilo lima mike nova oscar papa".split()


def holdout_frame() -> pd.DataFrame:
    ham = [f"family meeting schedule {w} {v}" for w in WORDS[:8] for v in ("tea", "rain", "bus")]
    spam = [f"urgent prize claim reward {w} {v}" for w in WORDS[8:] for v in ("now", "today", "fast")]
    return pd.DataFrame({"Message": ham + spam, "Type": ["Ham"] * len(ham) + ["Spam"] * len(spam)})


class HoldoutUnitTests(unittest.TestCase):
    def test_threshold_respects_fpr_budget(self) -> None:
        y = np.array([0] * 100 + [1] * 10)
        probability = np.concatenate([np.linspace(0, 0.9, 100), np.full(10, 0.95)])
        threshold = threshold_for_fpr(y, probability, 0.05)
        self.assertLessEqual(np.mean(probability[y == 0] >= threshold), 0.05)
        self.assertTrue((probability[y == 1] >= threshold).all())

    def test_calibration_error_is_zero_for_perfect_bins(self) -> None:
        self.assertEqual(expected_calibration_error(np.array([0, 1]), np.array([0.0, 1.0])), 0.0)

    def test_normalization_removes_format_controls_and_folds_compatibility(self) -> None:
        self.assertEqual(normalize_model_input("o‍t​p ｆｒｅｅ"), "otp free")
        self.assertEqual(normalize_model_input("ಕನ್ನಡ"), "ಕನ್ನಡ")

    def test_rule_engine_scores_are_ordinal(self) -> None:
        scores = rule_engine_scores(["see you at lunch", "Urgent: share your OTP now to verify account"])
        self.assertEqual(scores[0], 0)
        self.assertGreaterEqual(scores[1], 1)


class HoldoutEvaluationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.prepared, cls.audit = prepare_dataframe(holdout_frame())
        cls.result = holdout_evaluate_prepared(cls.prepared, cls.audit, seed=7, max_ham_fpr=0.1)

    def test_split_is_group_disjoint_and_complete(self) -> None:
        split = self.result["split"]
        self.assertEqual(split["development_test_group_crossings"], 0)
        self.assertEqual(split["development_rows"] + split["test_rows"], len(self.prepared))

    def test_reports_all_approaches_and_excludes_ablation_from_selection(self) -> None:
        self.assertEqual(
            set(self.result["approaches"]),
            {"rules_v0_6", "char_logreg", "word_char_linear_svc", ABLATION},
        )
        self.assertIn(self.result["selected_model"], {"char_logreg", "word_char_linear_svc"})
        self.assertTrue(all(ABLATION not in key for key in self.result["paired_bootstrap"]))

    def test_output_is_aggregate_only_and_deterministic(self) -> None:
        serialized = json.dumps(self.result, ensure_ascii=False)
        for message in holdout_frame()["Message"]:
            self.assertNotIn(message, serialized)
        again = holdout_evaluate_prepared(self.prepared, self.audit, seed=7, max_ham_fpr=0.1)
        strip = lambda r: {k: {n: {f: v for f, v in a.items() if f != "cost"} for n, a in r["approaches"].items()} if k == "approaches" else v for k, v in r.items()}
        self.assertEqual(strip(self.result), strip(again))

    def test_invalid_fpr_is_rejected(self) -> None:
        with self.assertRaises(EvaluationError):
            holdout_evaluate_prepared(self.prepared, self.audit, max_ham_fpr=0)

    def test_output_refuses_existing_destination(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "holdout.json"
            write_holdout_output({"ok": True}, target)
            with self.assertRaises(EvaluationError):
                write_holdout_output({"ok": True}, target)
            with self.assertRaises(EvaluationError):
                write_holdout_output({"ok": True}, Path(directory) / "missing" / "x.json")

    def test_cli_fails_safely_on_missing_workbook(self) -> None:
        with tempfile.TemporaryDirectory() as directory, redirect_stderr(io.StringIO()) as stderr:
            with self.assertRaises(SystemExit) as raised:
                main(["holdout-evaluate", "--workbook", f"{directory}/none.xlsx", "--output", f"{directory}/o.json"])
        self.assertEqual(raised.exception.code, 2)
        self.assertIn("failed safely", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
