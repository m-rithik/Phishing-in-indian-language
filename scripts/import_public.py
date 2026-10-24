"""Import public datasets into standardized Fisher evaluation JSONL format."""

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Dict, List, Optional, Set

from eval.load import load_messages


LANG_MAP = {
    "hi": "hindi",
    "hindi": "hindi",
    "ta": "tamil",
    "tamil": "tamil",
    "te": "telugu",
    "telugu": "telugu",
}

LANG_CODE_MAP = {
    "hindi": "hi",
    "tamil": "ta",
    "telugu": "te",
}


def _normalize_text_for_dedup(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def _flatten_newlines(text: str) -> str:
    return " ".join(text.replace("\r\n", " ").replace("\n", " ").replace("\r", " ").split())


def import_uci(
    input_path: Path,
    output_path: Path,
    max_per_class: int,
) -> List[Dict[str, str]]:
    """Import UCI SMS Spam Collection file into JSONL format.

    - Splits on first tab.
    - Maps 'ham' -> 'benign', 'spam' -> 'scam'.
    - Language: 'english', Script: 'latin_english'.
    - Source: 'public:UCI SMS Spam Collection'.
    - Flattens newlines.
    - Deduplicates by normalized text.
    - Caps counts per class.
    - ID format: pub-uci-0001.
    """
    if not input_path.is_file():
        raise FileNotFoundError(f"UCI input file not found: {input_path}")

    records = []
    seen_texts: Set[str] = set()
    class_counts = {"benign": 0, "scam": 0}

    with open(input_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split("\t", 1)
            if len(parts) != 2:
                continue
            raw_label, raw_text = parts
            raw_label = raw_label.strip().lower()
            if raw_label == "ham":
                label = "benign"
            elif raw_label == "spam":
                label = "scam"
            else:
                continue

            if class_counts[label] >= max_per_class:
                continue

            clean_text = _flatten_newlines(raw_text)
            if not clean_text:
                continue

            norm_text = _normalize_text_for_dedup(clean_text)
            if norm_text in seen_texts:
                continue
            seen_texts.add(norm_text)

            class_counts[label] += 1
            idx = len(records) + 1
            rec_id = f"pub-uci-{idx:04d}"

            records.append(
                {
                    "id": rec_id,
                    "text": clean_text,
                    "label": label,
                    "language": "english",
                    "script": "latin_english",
                    "source": "public:UCI SMS Spam Collection",
                }
            )

            if class_counts["benign"] >= max_per_class and class_counts["scam"] >= max_per_class:
                break

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="\n") as out_f:
        for rec in records:
            out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # Validate output
    load_messages(output_path)
    return records


def import_dakshina_sentences(
    input_path: Path,
    output_path: Path,
    lang_key: str,
    max_sentences: int,
    split: str = "test",
) -> List[Dict[str, str]]:
    """Import Dakshina romanized sentence file into JSONL format.

    - All rows: label 'benign', script 'romanized'.
    - Language: 'hindi', 'tamil', or 'telugu'.
    - Source: 'public:Dakshina (Wikipedia, formal text)'.
    - Skips sentences shorter than 4 words.
    - Flattens newlines.
    - Deduplicates by normalized text.
    - Caps count at max_sentences.
    - ID format: pub-dakshina-<lang_code>-0001.
    """
    if not input_path.is_file():
        raise FileNotFoundError(f"Dakshina sentence file not found: {input_path}")

    norm_lang = LANG_MAP.get(lang_key.lower())
    if not norm_lang:
        raise ValueError(f"Unsupported language: {lang_key}. Must be one of {list(LANG_MAP.keys())}")

    lang_code = LANG_CODE_MAP.get(norm_lang, lang_key.lower())
    records = []
    seen_texts: Set[str] = set()

    with open(input_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            clean_text = _flatten_newlines(line)
            if not clean_text:
                continue

            words = clean_text.split()
            if len(words) < 4:
                continue

            norm_text = _normalize_text_for_dedup(clean_text)
            if norm_text in seen_texts:
                continue
            seen_texts.add(norm_text)

            idx = len(records) + 1
            rec_id = f"pub-dakshina-{lang_code}-{idx:04d}"

            records.append(
                {
                    "id": rec_id,
                    "text": clean_text,
                    "label": "benign",
                    "language": norm_lang,
                    "script": "romanized",
                    "source": "public:Dakshina (Wikipedia, formal text)",
                }
            )

            if len(records) >= max_sentences:
                break

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="\n") as out_f:
        for rec in records:
            out_f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # Validate output
    load_messages(output_path)
    return records


def main():
    parser = argparse.ArgumentParser(description="Import public datasets into Fisher evaluation format")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # UCI subcommand
    uci_parser = subparsers.add_parser("uci", help="Import UCI SMS Spam Collection")
    uci_parser.add_argument("--input", "-i", type=Path, required=True, help="Path to SMSSpamCollection file")
    uci_parser.add_argument("--max-per-class", type=int, default=100, help="Max items per class (benign/scam)")
    uci_parser.add_argument("--out", "-o", type=Path, default=Path("eval/public_uci.jsonl"), help="Output JSONL path")

    # Dakshina sentences subcommand
    dakshina_parser = subparsers.add_parser("dakshina-sentences", help="Import Dakshina romanized sentences")
    dakshina_parser.add_argument("--lang", required=True, choices=["hi", "ta", "te", "hindi", "tamil", "telugu"], help="Language code")
    dakshina_parser.add_argument("--split", default="test", help="Dataset split (default: test)")
    dakshina_parser.add_argument("--input", "-i", type=Path, required=True, help="Path to romanized sentences file")
    dakshina_parser.add_argument("--max", type=int, default=150, help="Maximum number of sentences")
    dakshina_parser.add_argument("--out", "-o", type=Path, required=False, help="Output JSONL path")

    args = parser.parse_args()

    if args.command == "uci":
        records = import_uci(args.input, args.out, args.max_per_class)
        print(f"Imported {len(records)} UCI records to {args.out}")
    elif args.command == "dakshina-sentences":
        norm_lang = LANG_MAP[args.lang.lower()]
        lang_code = LANG_CODE_MAP[norm_lang]
        out_path = args.out or Path(f"eval/public_dakshina_{lang_code}.jsonl")
        records = import_dakshina_sentences(args.input, out_path, args.lang, args.max, args.split)
        print(f"Imported {len(records)} Dakshina records to {out_path}")


if __name__ == "__main__":
    main()
