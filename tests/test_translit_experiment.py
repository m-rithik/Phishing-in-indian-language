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
    for cond in ["A", "B", "C-max", "C-weighted", "D"]:
        assert cond in metrics["conditions"]
        assert "overall" in metrics["conditions"][cond]
        assert "per_language" in metrics["conditions"][cond]

    # Check Condition A and D counts
    cond_a_overall = metrics["conditions"]["A"]["overall"]
    assert cond_a_overall["n"] == 4
    assert cond_a_overall["TP"] == 3
    assert cond_a_overall["FP"] == 0
    assert cond_a_overall["TN"] == 1
    assert cond_a_overall["FN"] == 0
    assert cond_a_overall["precision"] == 1.0
    assert cond_a_overall["recall"] == 1.0
    assert cond_a_overall["f1"] == 1.0

    cond_d_overall = metrics["conditions"]["D"]["overall"]
    assert cond_d_overall["n"] == 4
    assert cond_d_overall["TP"] >= 3

    # Check McNemar tests exist and p-values are within [0, 1]
    mcnemar = metrics["mcnemar_exact"]
    assert "A_vs_B" in mcnemar
    assert "B_vs_C-max" in mcnemar
    assert "B_vs_C-weighted" in mcnemar
    assert "B_vs_D" in mcnemar
    assert "C-max_vs_D" in mcnemar

    for pair_name, result in mcnemar.items():
        assert result["n_items"] == 4
        assert 0.0 <= result["p_value"] <= 1.0, f"{pair_name} p_value out of bounds: {result['p_value']}"

    # Check limitations
    assert any("D removes the oracle: no language label is used" in lim for lim in metrics["limitations"])
