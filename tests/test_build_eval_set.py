"""Tests for scripts/build_eval_set.py."""

import json
from pathlib import Path
import pytest

from eval.load import load_messages
from scripts.build_eval_set import build_evaluation_set


def test_build_eval_set(tmp_path: Path):
    template_path = tmp_path / "template.jsonl"
    handwritten_path = tmp_path / "handwritten.jsonl"
    public_file_hi = tmp_path / "public_dakshina_hi.jsonl"
    public_file_uci = tmp_path / "public_uci.jsonl"
    out_path = tmp_path / "messages.jsonl"

    # Template with 1 scam and 1 benign in Hindi, 1 scam and 1 benign in English
    hw_data = [
        {"id": "hw-hi-01", "text": "Aapka account block hoga turant OTP bhejo", "label": "scam", "language": "hindi", "script": "romanized", "source": "synthetic"},
        {"id": "hw-hi-02", "text": "Kal milte hain chai pe", "label": "benign", "language": "hindi", "script": "romanized", "source": "synthetic"},
        {"id": "hw-en-01", "text": "Your card is blocked call now", "label": "scam", "language": "english", "script": "latin_english", "source": "synthetic"},
        {"id": "hw-en-02", "text": "Team meeting at 3pm", "label": "benign", "language": "english", "script": "latin_english", "source": "synthetic"},
    ]
    with open(template_path, "w", encoding="utf-8") as f:
        for r in hw_data:
            f.write(json.dumps(r) + "\n")

    # Public Hindi file with 5 benign messages (should be capped at 1 * 3 = 3 benign)
    pub_hi_data = [
        {"id": f"pub-dakshina-hi-{i:04d}", "text": f"Kumbh rashi sentence number {i} with long text", "label": "benign", "language": "hindi", "script": "romanized", "source": "public:Dakshina"}
        for i in range(1, 6)
    ]
    with open(public_file_hi, "w", encoding="utf-8") as f:
        for r in pub_hi_data:
            f.write(json.dumps(r) + "\n")

    # Public UCI file with 2 scam and 4 benign messages (benign should be capped at 1 * 3 = 3)
    pub_uci_data = [
        {"id": "pub-uci-0001", "text": "Urgent claim your prize now winner", "label": "scam", "language": "english", "script": "latin_english", "source": "public:UCI"},
        {"id": "pub-uci-0002", "text": "Lottery prize won call helpline", "label": "scam", "language": "english", "script": "latin_english", "source": "public:UCI"},
        {"id": "pub-uci-0003", "text": "See you at the cinema tonight", "label": "benign", "language": "english", "script": "latin_english", "source": "public:UCI"},
        {"id": "pub-uci-0004", "text": "Dinner is ready come downstairs", "label": "benign", "language": "english", "script": "latin_english", "source": "public:UCI"},
        {"id": "pub-uci-0005", "text": "Are you coming to the match tomorrow", "label": "benign", "language": "english", "script": "latin_english", "source": "public:UCI"},
        {"id": "pub-uci-0006", "text": "Please bring the car keys when you leave", "label": "benign", "language": "english", "script": "latin_english", "source": "public:UCI"},
    ]
    with open(public_file_uci, "w", encoding="utf-8") as f:
        for r in pub_uci_data:
            f.write(json.dumps(r) + "\n")

    # Run builder
    records = build_evaluation_set(
        handwritten_path=handwritten_path,
        template_path=template_path,
        public_glob_pattern=str(tmp_path / "public_*.jsonl"),
        output_path=out_path,
        public_benign_cap_ratio=3.0,
    )

    # 1. Handwritten was created from template
    assert handwritten_path.is_file()

    # 2. Hindi: 1 hw scam, 1 hw benign + 3 public benign (capped from 5) = 5 total
    hi_recs = [r for r in records if r["language"] == "hindi"]
    hi_benign = [r for r in hi_recs if r["label"] == "benign"]
    hi_scam = [r for r in hi_recs if r["label"] == "scam"]
    assert len(hi_scam) == 1
    assert len(hi_benign) == 4  # 1 hw + 3 pub

    # 3. English: 1 hw scam, 1 hw benign + 2 pub scam + 3 pub benign (capped from 4) = 7 total
    en_recs = [r for r in records if r["language"] == "english"]
    en_scam = [r for r in en_recs if r["label"] == "scam"]
    en_benign = [r for r in en_recs if r["label"] == "benign"]
    assert len(en_scam) == 3  # 1 hw + 2 pub
    assert len(en_benign) == 4  # 1 hw + 3 pub

    # 4. Validated with load_messages
    loaded = load_messages(out_path)
    assert len(loaded) == len(records)
