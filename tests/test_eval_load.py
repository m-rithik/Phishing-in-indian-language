"""Unit tests for eval/load.py validation rules."""

import json
from pathlib import Path
import pytest

from eval.load import load_messages

VALID_RECORD = {
    "id": "hi-001",
    "text": "Aapka khata band ho jayega, turant OTP bhejo",
    "label": "scam",
    "language": "hindi",
    "script": "romanized",
    "source": "synthetic",
}


def _write_jsonl(tmp_path: Path, records: list) -> Path:
    file_path = tmp_path / "test.jsonl"
    with file_path.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r) + "\n")
    return file_path


def test_load_valid_file(tmp_path: Path):
    path = _write_jsonl(tmp_path, [VALID_RECORD])
    loaded = load_messages(path)
    assert len(loaded) == 1
    assert loaded[0]["id"] == "hi-001"


def test_load_rejects_empty_file(tmp_path: Path):
    empty_file = tmp_path / "empty.jsonl"
    empty_file.write_text("", encoding="utf-8")
    with pytest.raises(ValueError, match="empty"):
        load_messages(empty_file)


def test_load_rejects_missing_field(tmp_path: Path):
    rec = dict(VALID_RECORD)
    del rec["source"]
    path = _write_jsonl(tmp_path, [rec])
    with pytest.raises(ValueError, match="missing"):
        load_messages(path)


def test_load_rejects_unknown_field(tmp_path: Path):
    rec = dict(VALID_RECORD)
    rec["extra_field"] = "unexpected"
    path = _write_jsonl(tmp_path, [rec])
    with pytest.raises(ValueError, match="unknown"):
        load_messages(path)


def test_load_rejects_invalid_label(tmp_path: Path):
    rec = dict(VALID_RECORD, label="phishing")
    path = _write_jsonl(tmp_path, [rec])
    with pytest.raises(ValueError, match="invalid label"):
        load_messages(path)


def test_load_rejects_invalid_language(tmp_path: Path):
    rec = dict(VALID_RECORD, language="klingon")
    path = _write_jsonl(tmp_path, [rec])
    with pytest.raises(ValueError, match="invalid language"):
        load_messages(path)


def test_load_rejects_invalid_script(tmp_path: Path):
    rec = dict(VALID_RECORD, script="cyrillic")
    path = _write_jsonl(tmp_path, [rec])
    with pytest.raises(ValueError, match="invalid script"):
        load_messages(path)


def test_load_rejects_script_latin_english_with_non_english(tmp_path: Path):
    rec = dict(VALID_RECORD, language="hindi", script="latin_english")
    path = _write_jsonl(tmp_path, [rec])
    with pytest.raises(ValueError, match="mismatch"):
        load_messages(path)


def test_load_rejects_english_without_latin_english(tmp_path: Path):
    rec = dict(VALID_RECORD, language="english", script="romanized")
    path = _write_jsonl(tmp_path, [rec])
    with pytest.raises(ValueError, match="mismatch"):
        load_messages(path)


def test_load_rejects_invalid_source(tmp_path: Path):
    rec = dict(VALID_RECORD, source="internet")
    path = _write_jsonl(tmp_path, [rec])
    with pytest.raises(ValueError, match="invalid source"):
        load_messages(path)


def test_load_rejects_duplicate_id(tmp_path: Path):
    rec1 = dict(VALID_RECORD, id="dup-1", text="First unique message text")
    rec2 = dict(VALID_RECORD, id="dup-1", text="Second unique message text")
    path = _write_jsonl(tmp_path, [rec1, rec2])
    with pytest.raises(ValueError, match="duplicate id"):
        load_messages(path)


def test_load_rejects_duplicate_text_collapsed(tmp_path: Path):
    rec1 = dict(VALID_RECORD, id="id-1", text="  Aapka khata   band ho jayega  ")
    rec2 = dict(VALID_RECORD, id="id-2", text="aapka khata band ho jayega")
    path = _write_jsonl(tmp_path, [rec1, rec2])
    with pytest.raises(ValueError, match="duplicate text"):
        load_messages(path)
