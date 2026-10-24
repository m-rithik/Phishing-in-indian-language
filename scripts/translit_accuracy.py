"""Evaluate transliteration candidate accuracy on a Dakshina lexicon file."""

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Dict, List, Tuple

from fisher_transliteration.candidates import CandidateConfig, generate_candidates

LIMITATION_TEXT = "rule-based; Wikipedia vocabulary, not SMS vocabulary"


def evaluate_lexicon_accuracy(
    lexicon_path: Path,
    language: str,
    max_pairs: int = 2000,
) -> Dict[str, Any]:
    """Evaluate transliteration accuracy against a Dakshina lexicon TSV file.

    Format per line: native_word <tab> romanization <tab> count
    """
    if not lexicon_path.is_file():
        raise FileNotFoundError(f"Lexicon file not found: {lexicon_path}")

    pairs: List[Tuple[str, str, int]] = []
    with open(lexicon_path, "r", encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split("\t")
            if len(parts) < 3:
                continue
            native_word = parts[0].strip()
            romanization = parts[1].strip()
            try:
                count = int(parts[2].strip())
            except ValueError:
                count = 1

            pairs.append((native_word, romanization, count))
            if len(pairs) >= max_pairs:
                break

    config = CandidateConfig(language=language)

    results_all: List[Dict[str, Any]] = []
    for native_word, romanization, count in pairs:
        cands = generate_candidates(romanization, config)
        cand_texts = [c.text for c in cands]

        is_top1 = bool(cand_texts and cand_texts[0] == native_word)
        is_top5 = bool(native_word in cand_texts[:5])
        is_anywhere = bool(native_word in cand_texts)

        results_all.append(
            {
                "native": native_word,
                "roman": romanization,
                "count": count,
                "length": len(romanization),
                "top1": is_top1,
                "top5": is_top5,
                "anywhere": is_anywhere,
            }
        )

    def _calc_stats(subset: List[Dict[str, Any]]) -> Dict[str, Any]:
        n = len(subset)
        if n == 0:
            return {
                "n_pairs": 0,
                "total_count": 0,
                "top1_unweighted": 0.0,
                "top5_unweighted": 0.0,
                "anywhere_unweighted": 0.0,
                "top1_weighted": 0.0,
                "top5_weighted": 0.0,
                "anywhere_weighted": 0.0,
            }

        total_count = sum(item["count"] for item in subset)
        top1_cnt = sum(1 for item in subset if item["top1"])
        top5_cnt = sum(1 for item in subset if item["top5"])
        anyw_cnt = sum(1 for item in subset if item["anywhere"])

        top1_w = sum(item["count"] for item in subset if item["top1"])
        top5_w = sum(item["count"] for item in subset if item["top5"])
        anyw_w = sum(item["count"] for item in subset if item["anywhere"])

        return {
            "n_pairs": n,
            "total_count": total_count,
            "top1_unweighted": round(top1_cnt / n, 4),
            "top5_unweighted": round(top5_cnt / n, 4),
            "anywhere_unweighted": round(anyw_cnt / n, 4),
            "top1_weighted": round(top1_w / total_count, 4) if total_count > 0 else 0.0,
            "top5_weighted": round(top5_w / total_count, 4) if total_count > 0 else 0.0,
            "anywhere_weighted": round(anyw_w / total_count, 4) if total_count > 0 else 0.0,
        }

    subset_lt5 = [item for item in results_all if item["length"] < 5]
    subset_ge5 = [item for item in results_all if item["length"] >= 5]

    output: Dict[str, Any] = {
        "language": language,
        "lexicon_path": str(lexicon_path),
        "max_pairs_requested": max_pairs,
        "n_pairs_evaluated": len(pairs),
        "overall": _calc_stats(results_all),
        "shorter_than_5_letters": _calc_stats(subset_lt5),
        "5_letters_or_more": _calc_stats(subset_ge5),
        "limitations": [LIMITATION_TEXT],
    }

    return output


def main():
    parser = argparse.ArgumentParser(description="Evaluate transliteration candidate accuracy on Dakshina lexicon")
    parser.add_argument("lexicon_file", nargs="?", type=Path, help="Path to Dakshina lexicon TSV file")
    parser.add_argument("--input", "-i", type=Path, help="Path to Dakshina lexicon TSV file (alternative)")
    parser.add_argument("--language", "-l", required=True, choices=["hindi", "tamil", "telugu"], help="Target language")
    parser.add_argument("--max-pairs", "-n", type=int, default=2000, help="Maximum word pairs to evaluate (default: 2000)")
    parser.add_argument("--out", "-o", type=Path, help="Output JSON path")

    args = parser.parse_args()

    lexicon_path = args.lexicon_file or args.input
    if not lexicon_path:
        parser.error("A lexicon input file must be specified either as a positional argument or via --input")

    output_path = args.out or Path(f"eval/results/translit_accuracy_{args.language}.json")
    results = evaluate_lexicon_accuracy(lexicon_path, args.language, args.max_pairs)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"Wrote transliteration accuracy results to {output_path}")
    print(f"Overall: Top-1: {results['overall']['top1_unweighted']} (w: {results['overall']['top1_weighted']}), "
          f"Top-5: {results['overall']['top5_unweighted']} (w: {results['overall']['top5_weighted']}), "
          f"Anywhere: {results['overall']['anywhere_unweighted']} (w: {results['overall']['anywhere_weighted']})")


if __name__ == "__main__":
    main()
