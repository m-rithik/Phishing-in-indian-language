"""Tests for transliteration experiment pipeline."""

from pathlib import Path
import pytest

from scripts.translit_experiment import run_experiment


def test_translit_experiment_on_fixture():
    fixture_path = Path("tests/fixtures/eval_messages.fixture.jsonl")
    assert fixture_path.is_file(), "Fixture file must exist"

    metrics, examples = run_experiment(fixture_path, positive_mode="high_or_review", k=5)

    # Check structure
    assert metrics["n_items"] == 4  # 4 romanized items out of 6 in fixture
    assert metrics["k"] == 5
    assert "conditions" in metrics
    for cond in ["A", "B", "C-max", "C-weighted"]:
        assert cond in metrics["conditions"]
        assert "overall" in metrics["conditions"][cond]
        assert "per_language" in metrics["conditions"][cond]

    # Check Condition A counts
    cond_a_overall = metrics["conditions"]["A"]["overall"]
    assert cond_a_overall["n"] == 4
    assert cond_a_overall["TP"] == 3
    assert cond_a_overall["FP"] == 0
    assert cond_a_overall["TN"] == 1
    assert cond_a_overall["FN"] == 0
    assert cond_a_overall["precision"] == 1.0
    assert cond_a_overall["recall"] == 1.0
    assert cond_a_overall["f1"] == 1.0

    # Check McNemar tests exist and p-values are within [0, 1]
    mcnemar = metrics["mcnemar_exact"]
    assert "A_vs_B" in mcnemar
    assert "B_vs_C-max" in mcnemar
    assert "B_vs_C-weighted" in mcnemar

    for pair_name, result in mcnemar.items():
        assert result["n_items"] == 4
        assert 0.0 <= result["p_value"] <= 1.0, f"{pair_name} p_value out of bounds: {result['p_value']}"
