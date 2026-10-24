"""Tests for scripts/import_public.py."""

from pathlib import Path
import pytest

from eval.load import load_messages
from scripts.import_public import import_dakshina_sentences, import_uci


def test_import_uci(tmp_path: Path):
    fixture_path = Path("tests/fixtures/uci_sample.txt")
    out_path = tmp_path / "public_uci.jsonl"

    # Test with max_per_class=1
    records = import_uci(fixture_path, out_path, max_per_class=1)

    assert len(records) == 2
    benign_recs = [r for r in records if r["label"] == "benign"]
    scam_recs = [r for r in records if r["label"] == "scam"]
    assert len(benign_recs) == 1
    assert len(scam_recs) == 1

    # Verify fields
    for r in records:
        assert r["id"].startswith("pub-uci-")
        assert r["language"] == "english"
        assert r["script"] == "latin_english"
        assert r["source"] == "public:UCI SMS Spam Collection"
        assert "\n" not in r["text"]

    # Validate output with load_messages
    loaded = load_messages(out_path)
    assert len(loaded) == 2


def test_import_dakshina_sentences(tmp_path: Path):
    fixture_path = Path("tests/fixtures/dakshina_sample_hi.txt")
    out_path = tmp_path / "public_dakshina_hi.jsonl"

    # In fixture: 4 lines. Line 2 has 3 words ("Iska ulat hai."), so it should be skipped (<4 words).
    # The other 3 lines have >= 4 words.
    records = import_dakshina_sentences(fixture_path, out_path, lang_key="hi", max_sentences=2)

    assert len(records) == 2
    for r in records:
        assert r["id"].startswith("pub-dakshina-hi-")
        assert r["label"] == "benign"
        assert r["language"] == "hindi"
        assert r["script"] == "romanized"
        assert r["source"] == "public:Dakshina (Wikipedia, formal text)"
        assert len(r["text"].split()) >= 4

    # Validate with load_messages
    loaded = load_messages(out_path)
    assert len(loaded) == 2
