from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import io
import json
import math
import os
from pathlib import Path
import tempfile
import sys
import unittest
from unittest.mock import patch

import numpy as np
import pandas as pd

from fisher_baselines.cli import main
from fisher_baselines.evaluation import EvaluationError
from fisher_baselines.selection import (
    CANDIDATES,
    _acceptance_decision,
    nested_evaluate_dataframe,
    select_candidate,
    write_selection_output,
)


def selection_frame() -> pd.DataFrame:
    ham = [
        "family meeting schedule alpha",
        "family meeting schedule bravo",
        "family meeting schedule charlie",
        "family meeting schedule delta",
        "office agenda review echo",
        "office agenda review foxtrot",
        "office agenda review golf",
        "office agenda review hotel",
        "lunch plan reminder india",
        "lunch plan reminder juliet",
        "lunch plan reminder kilo",
        "lunch plan reminder lima",
    ]
    spam = [
        "urgent prize claim mango",
        "urgent prize claim nectar",
        "urgent prize claim olive",
        "urgent prize claim pearl",
        "limited reward collect quartz",
        "limited reward collect raven",
        "limited reward collect solar",
        "limited reward collect tiger",
        "verify account immediately umber",
        "verify account immediately vivid",
        "verify account immediately whale",
        "verify account immediately xenon",
    ]
    return pd.DataFrame({"Message": ham + spam, "Type": ["Ham"] * 12 + ["Spam"] * 12})


def _all_floats(value: object):
    if isinstance(value, float):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from _all_floats(child)
    elif isinstance(value, list):
        for child in value:
            yield from _all_floats(child)


class CandidateSelectionTests(unittest.TestCase):
    def test_candidate_grid_and_tie_break_are_exact(self) -> None:
        self.assertEqual(
            [(candidate.model, candidate.c) for candidate in CANDIDATES],
            [
                ("char_logreg", 1.0),
                ("char_linear_svc", 1.0),
                ("word_char_linear_svc", 1.0),
                ("char_logreg", 0.5),
                ("char_linear_svc", 0.5),
                ("word_char_linear_svc", 0.5),
                ("char_logreg", 2.0),
                ("word_char_linear_svc", 2.0),
            ],
        )
        tied = {
            candidate.key: {
                "spam_f1": 0.7,
                "macro_f1": 0.8,
                "spam_precision": 0.9,
            }
            for candidate in CANDIDATES
        }
        self.assertEqual(select_candidate(tied), CANDIDATES[0])

        tied[CANDIDATES[2].key]["spam_f1"] = 0.71
        self.assertEqual(select_candidate(tied), CANDIDATES[2])

    def test_candidate_scores_reject_nonfinite_nonreal_and_out_of_range_values(self) -> None:
        valid = {
            candidate.key: {
                "spam_f1": 0.7,
                "macro_f1": 0.8,
                "spam_precision": 0.9,
            }
            for candidate in CANDIDATES
        }
        for invalid in (True, False, "0.7", float("nan"), float("inf"), -float("inf"), -0.1, 1.1):
            with self.subTest(invalid=repr(invalid)):
                scores = {key: dict(value) for key, value in valid.items()}
                scores[CANDIDATES[0].key]["spam_f1"] = invalid
                with self.assertRaises(EvaluationError):
                    select_candidate(scores)

    def test_acceptance_boundaries_are_inclusive_with_frozen_tolerance(self) -> None:
        selected = [
            {"spam_f1": 0.91},
            {"spam_f1": 0.90},
            {"spam_f1": 0.89},
        ]
        comparator = [
            {"spam_f1": 0.90},
            {"spam_f1": 0.90},
            {"spam_f1": 0.89 + 5e-13},
        ]
        decision = _acceptance_decision(
            selected_spam_f1_mean=0.91,
            selected_macro_f1_mean=0.895,
            comparator_spam_f1_mean=0.90,
            comparator_macro_f1_mean=0.90,
            selected_folds=selected,
            comparator_folds=comparator,
        )
        self.assertTrue(decision["accepted"])
        self.assertEqual(decision["observed_outer_folds_with_worse_spam_f1"], 0)
        self.assertEqual(decision["floating_point_comparison_tolerance"], 1e-12)

    def test_nested_splits_are_deterministic_group_disjoint_and_partition_fitted(self) -> None:
        fit_partitions: list[tuple[set[str], set[str]]] = []

        def fake_fit_and_score(
            model_name: str,
            c: float,
            seed: int,
            train_texts: list[str],
            train_y: np.ndarray,
            validation_texts: list[str],
            validation_y: np.ndarray,
        ) -> dict[str, object]:
            del model_name, c, seed, train_y
            training = set(train_texts)
            validation = set(validation_texts)
            self.assertTrue(training)
            self.assertTrue(validation)
            self.assertTrue(training.isdisjoint(validation))
            fit_partitions.append((training, validation))
            return {
                "support": int(len(validation_y)),
                "spam_support": int(np.count_nonzero(validation_y == 1)),
                "ham_support": int(np.count_nonzero(validation_y == 0)),
                "confusion_matrix": {
                    "tn": int(np.count_nonzero(validation_y == 0)),
                    "fp": 0,
                    "fn": int(np.count_nonzero(validation_y == 1)),
                    "tp": 0,
                },
                "spam_precision": 0.0,
                "spam_recall": 0.0,
                "spam_f1": 0.0,
                "macro_f1": 1.0 / 3.0,
                "balanced_accuracy": 0.5,
                "average_precision": float(np.mean(validation_y)),
            }

        with patch("fisher_baselines.selection._fit_and_score", side_effect=fake_fit_and_score):
            first = nested_evaluate_dataframe(selection_frame(), outer_folds=3, inner_folds=3)
            second = nested_evaluate_dataframe(selection_frame(), outer_folds=3, inner_folds=3)

        self.assertEqual(first.manifest, second.manifest)
        self.assertEqual(first.metrics, second.metrics)
        self.assertEqual(len(fit_partitions), 162)  # 81 fits per complete nested run.
        self.assertEqual(first.manifest["split"]["outer_group_crossing_count"], 0)
        self.assertTrue(
            all(
                split["group_crossing_count"] == 0
                for split in first.manifest["split"]["inner_splits"]
            )
        )

    @unittest.skipIf(sys.platform == "win32", "Windows file locking differs from POSIX")
    def test_output_is_single_aggregate_only_byte_deterministic_and_sheet_private(self) -> None:
        secret = "raw-secret-never-persist"
        frame = selection_frame()
        frame.loc[0, "Message"] += f" {secret}"
        result = nested_evaluate_dataframe(
            frame,
            outer_folds=3,
            inner_folds=3,
            workbook_sha256="a" * 64,
            sheet=f"sensitive-{secret}",
        )

        with tempfile.TemporaryDirectory() as directory:
            safe_directory = Path(directory).resolve()
            first = safe_directory / "first.json"
            second = safe_directory / "second.json"
            write_selection_output(result, first)
            write_selection_output(result, second)

            first_bytes = first.read_bytes()
            self.assertEqual(first_bytes, second.read_bytes())
            text = first_bytes.decode("utf-8")
            for prohibited in (
                secret,
                "record_id",
                "group_id",
                "predictions",
                "model_text",
                "vocabulary",
                "coefficient",
            ):
                self.assertNotIn(prohibited, text)
            document = json.loads(text)
            self.assertEqual(set(document), {"audit", "selection_manifest", "selection_metrics"})
            manifest = document["selection_manifest"]
            self.assertEqual(manifest["evaluation_scope"], "development_only")
            self.assertFalse(manifest["source"]["source_path_recorded"])
            self.assertEqual(len(manifest["candidates"]), 8)
            self.assertFalse(document["audit"]["source"]["selected_sheet_recorded"])
            metrics = document["selection_metrics"]
            self.assertIn("acceptance_decision", metrics)
            self.assertFalse(any(not math.isfinite(value) for value in _all_floats(document)))

    def test_occupied_and_symlink_output_destinations_fail_safely(self) -> None:
        result = nested_evaluate_dataframe(selection_frame(), outer_folds=3, inner_folds=3)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            occupied = root / "occupied.json"
            occupied.write_text("keep", encoding="utf-8")
            with self.assertRaises(EvaluationError):
                write_selection_output(result, occupied)
            self.assertEqual(occupied.read_text(encoding="utf-8"), "keep")

            target = root / "target.json"
            target.write_text("target", encoding="utf-8")
            symlink = root / "symlink.json"
            symlink.symlink_to(target)
            with self.assertRaises(EvaluationError):
                write_selection_output(result, symlink)
            self.assertEqual(target.read_text(encoding="utf-8"), "target")

            real_parent = root / "real-parent"
            real_parent.mkdir()
            linked_parent = root / "linked-parent"
            linked_parent.symlink_to(real_parent, target_is_directory=True)
            with self.assertRaises(EvaluationError):
                write_selection_output(result, linked_parent / "selection.json")
            self.assertEqual(list(real_parent.iterdir()), [])

            nested = real_parent / "nested"
            nested.mkdir()
            with self.assertRaises(EvaluationError):
                write_selection_output(result, linked_parent / "nested" / "selection.json")
            self.assertEqual(list(nested.iterdir()), [])

            traversal = root / "traversal"
            (traversal / "safe").mkdir(parents=True)
            (traversal / "other").mkdir()
            with self.assertRaises(EvaluationError):
                write_selection_output(
                    result,
                    traversal / "safe" / ".." / "other" / "selection.json",
                )
            self.assertEqual(list((traversal / "other").iterdir()), [])

    @unittest.skipIf(sys.platform == "win32", "Windows file locking differs from POSIX")
    def test_write_failure_and_parent_symlink_swap_publish_nothing(self) -> None:
        result = nested_evaluate_dataframe(selection_frame(), outer_folds=3, inner_folds=3)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            destination = root / "selection.json"
            with patch("fisher_baselines.selection._write_all", side_effect=OSError("injected")):
                with self.assertRaises(EvaluationError):
                    write_selection_output(result, destination)
            self.assertFalse(destination.exists())
            self.assertEqual(list(root.iterdir()), [])

            result.metrics["nonfinite_injection"] = float("nan")
            with self.assertRaises(EvaluationError):
                write_selection_output(result, destination)
            self.assertFalse(destination.exists())
            result.metrics.pop("nonfinite_injection")

            parent = root / "parent"
            moved = root / "moved"
            attacker = root / "attacker"
            parent.mkdir()
            attacker.mkdir()
            destination = parent / "selection.json"
            original = os.stat(parent, follow_symlinks=False)

            def swapped_binding(parent_fd: int, parent_path: Path) -> bool:
                del parent_fd, parent_path
                parent.rename(moved)
                parent.symlink_to(attacker, target_is_directory=True)
                return False

            with patch("fisher_baselines.selection._parent_binding_matches", side_effect=swapped_binding):
                with self.assertRaises(EvaluationError):
                    write_selection_output(result, destination)
            self.assertTrue(original.st_ino > 0)
            self.assertFalse((moved / "selection.json").exists())
            self.assertFalse((attacker / "selection.json").exists())
            self.assertEqual(list(moved.iterdir()), [])
            self.assertEqual(list(attacker.iterdir()), [])

    @unittest.skipIf(sys.platform == "win32", "Windows file locking differs from POSIX")
    def test_post_link_failure_never_deletes_a_replacement_filename(self) -> None:
        result = nested_evaluate_dataframe(selection_frame(), outer_folds=3, inner_folds=3)
        with tempfile.TemporaryDirectory() as directory:
            safe_directory = Path(directory).resolve()
            destination = safe_directory / "selection.json"
            owned = safe_directory / "owned-output.json"
            binding_checks = 0

            def interposed_binding(parent_fd: int, parent_path: Path) -> bool:
                nonlocal binding_checks
                del parent_fd, parent_path
                binding_checks += 1
                if binding_checks == 1:
                    return True
                destination.rename(owned)
                destination.write_text("replacement", encoding="utf-8")
                return False

            with patch(
                "fisher_baselines.selection._parent_binding_matches",
                side_effect=interposed_binding,
            ):
                with self.assertRaisesRegex(EvaluationError, "manual inspection"):
                    write_selection_output(result, destination)

            self.assertEqual(destination.read_text(encoding="utf-8"), "replacement")
            self.assertTrue(owned.read_bytes().endswith(b"\n"))


class NestedSelectionCliTests(unittest.TestCase):
    def test_invalid_fold_count_is_sanitized(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with patch(
            "fisher_baselines.cli.nested_evaluate_workbook",
            side_effect=EvaluationError("private split detail"),
        ), redirect_stdout(stdout), redirect_stderr(stderr):
            with self.assertRaises(SystemExit) as raised:
                main(
                    [
                        "nested-evaluate",
                        "--workbook",
                        "/private/input.xlsx",
                        "--output",
                        "out.json",
                        "--outer-folds",
                        "1",
                    ]
                )
        self.assertEqual(raised.exception.code, 2)
        combined = stdout.getvalue() + stderr.getvalue()
        self.assertNotIn("private split detail", combined)
        self.assertNotIn("/private/input.xlsx", combined)


if __name__ == "__main__":
    unittest.main()
