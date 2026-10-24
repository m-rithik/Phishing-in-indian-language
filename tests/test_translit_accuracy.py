"""Tests for scripts/translit_accuracy.py."""

import json
from pathlib import Path
import pytest

from scripts.translit_accuracy import LIMITATION_TEXT, evaluate_lexicon_accuracy


def test_evaluate_lexicon_accuracy_on_fixture(tmp_path: Path):
    fixture_path = Path("tests/fixtures/dakshina_lexicon_sample.tsv")
    results = evaluate_lexicon_accuracy(fixture_path, language="hindi", max_pairs=5)

    assert results["language"] == "hindi"
    assert results["n_pairs_evaluated"] == 5
    assert LIMITATION_TEXT in results["limitations"]

    overall = results["overall"]
    assert overall["n_pairs"] == 5
    assert overall["total_count"] == 11  # 5 + 1 + 3 + 1 + 1

    # Checks that metrics are properly bounded between 0.0 and 1.0
    for key in [
        "top1_unweighted", "top5_unweighted", "anywhere_unweighted",
        "top1_weighted", "top5_weighted", "anywhere_weighted"
    ]:
        assert 0.0 <= overall[key] <= 1.0

    # Shorter than 5 letters: ank (len 3, count 5), anka (len 4, count 1) -> 2 pairs, count 6
    lt5 = results["shorter_than_5_letters"]
    assert lt5["n_pairs"] == 2
    assert lt5["total_count"] == 6

    # 5 letters or more: ankit (len 5, count 3), anakon (len 6, count 1), ankhon (len 6, count 1) -> 3 pairs, count 5
    ge5 = results["5_letters_or_more"]
    assert ge5["n_pairs"] == 3
    assert ge5["total_count"] == 5

    # Test file writing with newline="\n"
    out_file = tmp_path / "translit_accuracy_hindi.json"
    with open(out_file, "w", encoding="utf-8", newline="\n") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        f.write("\n")

    assert out_file.is_file()
    raw_content = out_file.read_bytes()
    # Ensure LF is used, no CRLF inside when written with newline="\n"
    assert b"\r\n" not in raw_content
    loaded = json.loads(raw_content.decode("utf-8"))
    assert loaded["language"] == "hindi"
    assert LIMITATION_TEXT in loaded["limitations"]
