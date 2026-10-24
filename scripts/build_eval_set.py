"""Build evaluation dataset by merging handwritten and public dataset files."""

import argparse
from collections import Counter
import glob
import json
from pathlib import Path
import re
import shutil
import sys
from typing import Any, Dict, List, Optional, Set

from eval.load import load_messages


def _normalize_text_for_dedup(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def build_evaluation_set(
    handwritten_path: Path = Path("eval/handwritten.jsonl"),
    template_path: Path = Path("eval/messages.template.jsonl"),
    public_glob_pattern: str = "eval/public_*.jsonl",
    output_path: Path = Path("eval/messages.jsonl"),
    public_benign_cap_ratio: Optional[float] = None,
) -> List[Dict[str, Any]]:
    """Merge handwritten messages and public datasets into eval/messages.jsonl.

    - Creates handwritten_path from template_path if missing.
    - Default: includes all imported public benign messages (no 3:1 cap unless specified).
    - Deduplicates by normalized text and ensures unique IDs.
    - Validates output with eval.load.load_messages.
    - Prints summary breakdown per language, script, label, and source.
    """
    # 1. Load handwritten file if present and non-empty, or fallback to template
    handwritten_records: List[Dict[str, Any]] = []
    if handwritten_path and Path(handwritten_path).is_file():
        p = Path(handwritten_path)
        if p.stat().st_size > 0:
            lines = [line.strip() for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]
            if lines:
                handwritten_records = load_messages(p)
    elif template_path and Path(template_path).is_file():
        if handwritten_path:
            shutil.copyfile(template_path, handwritten_path)
            print(f"Created {handwritten_path} from {template_path}")
            handwritten_records = load_messages(handwritten_path)
        else:
            handwritten_records = load_messages(template_path)

    # 2. Count handwritten scam messages per language
    hw_scam_counts: Dict[str, int] = Counter()
    for rec in handwritten_records:
        if rec["label"] == "scam":
            hw_scam_counts[rec["language"]] += 1

    # 3. Deduplication trackers
    merged_records: List[Dict[str, Any]] = []
    seen_ids: Set[str] = set()
    seen_texts: Set[str] = set()

    # Add all handwritten messages first
    for rec in handwritten_records:
        norm_text = _normalize_text_for_dedup(rec["text"])
        seen_texts.add(norm_text)
        seen_ids.add(rec["id"])
        merged_records.append(rec)

    # 4. Ingest public files
    public_files = sorted(glob.glob(public_glob_pattern))
    public_benign_counts: Dict[str, int] = Counter()

    for p_file in public_files:
        try:
            records = load_messages(p_file)
        except Exception as exc:
            print(f"Warning: Failed to load {p_file}: {exc}", file=sys.stderr)
            continue

        for rec in records:
            norm_text = _normalize_text_for_dedup(rec["text"])
            if norm_text in seen_texts:
                continue

            lang = rec["language"]
            label = rec["label"]

            # Cap public benign messages per language only if public_benign_cap_ratio is specified
            if label == "benign" and public_benign_cap_ratio is not None:
                scam_count = hw_scam_counts.get(lang, 0)
                max_allowed_benign = int(scam_count * public_benign_cap_ratio)
                if public_benign_counts[lang] >= max_allowed_benign:
                    continue
                public_benign_counts[lang] += 1

            # Ensure ID uniqueness
            rec_id = rec["id"]
            if rec_id in seen_ids:
                suffix = 1
                new_id = f"{rec_id}_{suffix}"
                while new_id in seen_ids:
                    suffix += 1
                    new_id = f"{rec_id}_{suffix}"
                rec = dict(rec)
                rec["id"] = new_id
                rec_id = new_id

            seen_ids.add(rec_id)
            seen_texts.add(norm_text)
            merged_records.append(rec)

    # 5. Write to output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="\n") as f:
        for rec in merged_records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # 6. Validate with load_messages
    validated = load_messages(output_path)

    # 7. Print summary breakdown
    print_counts(validated)
    return validated


def print_counts(records: List[Dict[str, Any]]) -> None:
    """Print counts per language, script, label, and source."""
    lang_counter = Counter(r["language"] for r in records)
    script_counter = Counter(r["script"] for r in records)
    label_counter = Counter(r["label"] for r in records)
    source_counter = Counter(r["source"] for r in records)

    print(f"\n--- Evaluation Dataset Summary (Total: {len(records)}) ---")
    print("By Language:")
    for lang, count in sorted(lang_counter.items()):
        print(f"  {lang}: {count}")

    print("\nBy Script:")
    for script, count in sorted(script_counter.items()):
        print(f"  {script}: {count}")

    print("\nBy Label:")
    for label, count in sorted(label_counter.items()):
        print(f"  {label}: {count}")

    print("\nBy Source:")
    for src, count in sorted(source_counter.items()):
        print(f"  {src}: {count}")
    print("--------------------------------------------------\n")


def main():
    parser = argparse.ArgumentParser(description="Build Fisher evaluation dataset")
    parser.add_argument("--handwritten", type=Path, default=Path("eval/handwritten.jsonl"), help="Path to handwritten messages")
    parser.add_argument("--template", type=Path, default=Path("eval/messages.template.jsonl"), help="Path to template messages")
    parser.add_argument("--public-glob", type=str, default="eval/public_*.jsonl", help="Glob pattern for public files")
    parser.add_argument("--out", "-o", type=Path, default=Path("eval/messages.jsonl"), help="Output path for eval set")
    parser.add_argument("--public-benign-cap", type=float, default=None, help="Optional max ratio of public benign to handwritten scam per language (default: None, no cap)")

    args = parser.parse_args()

    build_evaluation_set(
        handwritten_path=args.handwritten,
        template_path=args.template,
        public_glob_pattern=args.public_glob,
        output_path=args.out,
        public_benign_cap_ratio=args.public_benign_cap,
    )


if __name__ == "__main__":
    main()
