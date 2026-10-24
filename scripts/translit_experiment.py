"""Transliteration multi-candidate experiment for Romanized Indic text."""

import argparse
import json
import math
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Dict, List, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from eval.load import load_messages
from fisher_transliteration.candidates import CandidateConfig, generate_candidates

TOKEN_PATTERN = re.compile(r"([a-zA-Z]+)")
MAX_BATCH_SIZE = 500


def exact_mcnemar(first_only: int, second_only: int) -> float:
    """Exact two-sided McNemar test using standard library binomial."""
    n = first_only + second_only
    if n == 0:
        return 1.0
    k = min(first_only, second_only)
    prob = sum(math.comb(n, i) for i in range(k + 1)) * (0.5 ** n)
    return min(1.0, 2.0 * prob)


def flatten_text(text: str) -> str:
    """Flatten newlines and carriage returns inside messages to single spaces."""
    return re.sub(r"[\r\n]+", " ", text).strip()


def transliterate_word_candidates(
    word: str, language: str, k: int = 5
) -> List[Tuple[str, float]]:
    """Generate k candidate transliterations and confidences for a single word."""
    config = CandidateConfig(language=language, max_candidates=k, include_romanized=False)
    cands = generate_candidates(word, config)
    if not cands:
        # Fallback to include_romanized if no script candidates found
        cands = generate_candidates(word, CandidateConfig(language=language, max_candidates=k))
    if not cands:
        return [(word, 1.0)]

    return [(c.text, float(c.confidence)) for c in cands]


def build_variants(
    text: str, language: str, k: int = 5
) -> Tuple[List[str], List[float]]:
    """Build k variant strings and their raw joint weights for the message."""
    pieces = TOKEN_PATTERN.split(text)
    # pieces alternate between non-tokens and tokens
    # Collect candidate lists for token pieces
    word_candidates: List[List[Tuple[str, float]]] = []
    token_indices: List[int] = []

    for idx, piece in enumerate(pieces):
        if TOKEN_PATTERN.fullmatch(piece):
            lower_word = piece.lower()
            cands = transliterate_word_candidates(lower_word, language, k)
            word_candidates.append(cands)
            token_indices.append(idx)

    variant_texts: List[str] = []
    variant_raw_weights: List[float] = []

    for i in range(k):
        variant_pieces = list(pieces)
        joint_weight = 1.0
        for w_idx, p_idx in enumerate(token_indices):
            cands = word_candidates[w_idx]
            chosen_text, conf = cands[i] if i < len(cands) else cands[-1]
            variant_pieces[p_idx] = chosen_text
            joint_weight *= max(conf, 1e-6)

        variant_texts.append("".join(variant_pieces))
        variant_raw_weights.append(joint_weight)

    sum_weights = sum(variant_raw_weights)
    if sum_weights > 0:
        normalized_weights = [w / sum_weights for w in variant_raw_weights]
    else:
        normalized_weights = [1.0 / k for _ in range(k)]

    return variant_texts, normalized_weights


def run_detector_batch(texts: List[str]) -> Dict[str, str]:
    """Run `node fisher.mjs batch-detail` on unique texts in chunks of at most 500 lines."""
    unique_texts = list(dict.fromkeys(texts))
    risk_map: Dict[str, str] = {}

    for i in range(0, len(unique_texts), MAX_BATCH_SIZE):
        chunk = unique_texts[i : i + MAX_BATCH_SIZE]
        stdin_data = "\n".join(chunk) + "\n"

        proc = subprocess.run(
            ["node", "fisher.mjs", "batch-detail"],
            input=stdin_data,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        lines = [line.strip() for line in proc.stdout.splitlines() if line.strip()]
        if len(lines) != len(chunk):
            raise RuntimeError(
                f"batch-detail returned {len(lines)} lines for {len(chunk)} inputs. "
                f"Stderr: {proc.stderr}"
            )

        for text_in, line_out in zip(chunk, lines):
            parsed = json.loads(line_out)
            risk_map[text_in] = parsed["risk"]

    return risk_map


def compute_condition_metrics(items: List[Dict[str, Any]], pred_key: str) -> Dict[str, Any]:
    tp = fp = tn = fn = 0
    for item in items:
        is_scam = item["label"] == "scam"
        pred = item["predictions"][pred_key]
        if is_scam and pred:
            tp += 1
        elif not is_scam and pred:
            fp += 1
        elif not is_scam and not pred:
            tn += 1
        elif is_scam and not pred:
            fn += 1

    n = len(items)
    precision = tp / (tp + fp) if tp + fp > 0 else (1.0 if tp == 0 and fp == 0 else 0.0)
    recall = tp / (tp + fn) if tp + fn > 0 else (1.0 if tp == 0 and fn == 0 else 0.0)
    f1 = (
        (2 * precision * recall) / (precision + recall)
        if precision + recall > 0
        else 0.0
    )

    return {
        "n": n,
        "TP": tp,
        "FP": fp,
        "TN": tn,
        "FN": fn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
    }


def run_experiment(
    messages_path: Path,
    positive_mode: str = "high_or_review",
    k: int = 5,
) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    raw_messages = load_messages(messages_path)
    romanized_items = [m for m in raw_messages if m["script"] == "romanized"]

    if not romanized_items:
        raise ValueError("No messages with script=='romanized' found in evaluation dataset.")

    is_positive = (
        (lambda risk: risk == "high")
        if positive_mode == "high"
        else (lambda risk: risk in ("high", "review"))
    )

    positive_risks = ["high"] if positive_mode == "high" else ["high", "review"]

    # Pre-generate text variants for each item
    item_variants = []
    all_needed_texts: List[str] = []

    for item in romanized_items:
        original = flatten_text(item["text"])
        variants, norm_weights = build_variants(item["text"], item["language"], k)
        flattened_variants = [flatten_text(v) for v in variants]

        # Condition A: original text
        text_a = original
        # Condition B: original + " " + top-1 candidate
        text_b = f"{original} {flattened_variants[0]}"
        # Condition C: 5 variants original + " " + variant_i
        texts_c = [f"{original} {v}" for v in flattened_variants]
        # Condition D: 5 variants for each of hindi, tamil, telugu (15 total)
        texts_d = []
        for d_lang in ("hindi", "tamil", "telugu"):
            d_variants, _ = build_variants(item["text"], d_lang, k)
            texts_d.extend(f"{original} {flatten_text(v)}" for v in d_variants)

        all_needed_texts.append(text_a)
        all_needed_texts.append(text_b)
        all_needed_texts.extend(texts_c)
        all_needed_texts.extend(texts_d)

        item_variants.append(
            {
                "item": item,
                "text_a": text_a,
                "text_b": text_b,
                "texts_c": texts_c,
                "texts_d": texts_d,
                "weights_c": norm_weights,
                "variants_raw": variants,
            }
        )

    # Batch execute detector on all unique texts
    risk_cache = run_detector_batch(all_needed_texts)

    # Evaluate predictions for each condition
    evaluated_items = []
    disagreeing_items = []

    for data in item_variants:
        item = data["item"]
        pred_a = is_positive(risk_cache[data["text_a"]])
        pred_b = is_positive(risk_cache[data["text_b"]])

        preds_c = [is_positive(risk_cache[t]) for t in data["texts_c"]]
        pred_c_max = any(preds_c)

        weighted_pos_sum = sum(
            w for p, w in zip(preds_c, data["weights_c"]) if p
        )
        pred_c_weighted = weighted_pos_sum >= 0.5

        preds_d = [is_positive(risk_cache[t]) for t in data["texts_d"]]
        pred_d = any(preds_d)

        predictions = {
            "A": bool(pred_a),
            "B": bool(pred_b),
            "C-max": bool(pred_c_max),
            "C-weighted": bool(pred_c_weighted),
            "D": bool(pred_d),
        }

        evaluated_entry = {
            "id": item["id"],
            "language": item["language"],
            "label": item["label"],
            "predictions": predictions,
            "variants": data["variants_raw"],
        }
        evaluated_items.append(evaluated_entry)

        # Check disagreement
        if len(set(predictions.values())) > 1:
            disagreeing_items.append(
                {
                    "id": item["id"],
                    "language": item["language"],
                    "label": item["label"],
                    "original_text": item["text"],
                    "predictions": predictions,
                    "variants": data["variants_raw"],
                }
            )

    # Compute metrics per condition
    conditions_summary = {}
    languages = sorted(list(set(m["language"] for m in evaluated_items)))

    for cond in ["A", "B", "C-max", "C-weighted", "D"]:
        overall = compute_condition_metrics(evaluated_items, cond)
        per_lang = {}
        for lang in languages:
            lang_items = [m for m in evaluated_items if m["language"] == lang]
            per_lang[lang] = compute_condition_metrics(lang_items, cond)
        conditions_summary[cond] = {
            "overall": overall,
            "per_language": per_lang,
        }

    # McNemar tests
    def compute_pair_mcnemar(c1: str, c2: str) -> Dict[str, Any]:
        first_only = second_only = 0
        for entry in evaluated_items:
            is_scam = entry["label"] == "scam"
            c1_corr = entry["predictions"][c1] == is_scam
            c2_corr = entry["predictions"][c2] == is_scam
            if c1_corr and not c2_corr:
                first_only += 1
            elif c2_corr and not c1_corr:
                second_only += 1
        p_val = exact_mcnemar(first_only, second_only)
        return {
            "n_items": len(evaluated_items),
            "first_only_correct": first_only,
            "second_only_correct": second_only,
            "p_value": round(p_val, 6),
        }

    mcnemar_results = {
        "A_vs_B": compute_pair_mcnemar("A", "B"),
        "B_vs_C-max": compute_pair_mcnemar("B", "C-max"),
        "B_vs_C-weighted": compute_pair_mcnemar("B", "C-weighted"),
        "B_vs_D": compute_pair_mcnemar("B", "D"),
        "C-max_vs_D": compute_pair_mcnemar("C-max", "D"),
    }

    metrics_output = {
        "n_items": len(evaluated_items),
        "k": k,
        "positive_risks": positive_risks,
        "limitations": [
            "Rule-based detector; no learned model.",
            "Oracle language ID: the item's language field selects the transliteration script.",
            "D removes the oracle: no language label is used.",
            "Small or synthetic evaluation data; no claim of real-world accuracy.",
            "Messages are flattened to one line for the batch CLI.",
        ],
        "conditions": conditions_summary,
        "mcnemar_exact": mcnemar_results,
    }

    return metrics_output, disagreeing_items[:20]


def main():
    parser = argparse.ArgumentParser(description="Fisher transliteration experiment.")
    parser.add_argument(
        "--messages",
        type=Path,
        default=Path("eval/messages.jsonl"),
        help="Path to evaluation .jsonl dataset.",
    )
    parser.add_argument(
        "--positive",
        choices=["high", "review"],
        default="review",
        help="Whether positive means 'high' only or 'high' or 'review' (default).",
    )
    parser.add_argument(
        "--k",
        type=int,
        default=5,
        help="Number of variants for condition C (default: 5).",
    )
    args = parser.parse_args()

    pos_mode = "high" if args.positive == "high" else "high_or_review"
    metrics, examples = run_experiment(args.messages, positive_mode=pos_mode, k=args.k)

    results_dir = Path("eval/results")
    results_dir.mkdir(parents=True, exist_ok=True)

    metrics_path = results_dir / "translit_metrics.json"
    examples_path = results_dir / "translit_examples.jsonl"

    metrics_path.write_text(json.dumps(metrics, indent=2) + "\n", encoding="utf-8", newline="\n")
    with examples_path.open("w", encoding="utf-8", newline="\n") as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")

    print(f"Transliteration experiment complete ({metrics['n_items']} romanized items).")
    print(f"Metrics written to: {metrics_path}")
    print(f"Disagreement examples ({len(examples)}) written to: {examples_path}")


if __name__ == "__main__":
    main()
