"""Held-out comparison of the shipped rule engine with calibrated lexical models.

Development folds choose each model's Platt calibration, its operating threshold,
and the selected model. The group-disjoint test partition is scored once. Only
aggregate metrics are returned; no text, prediction, model, or vocabulary is kept.
"""

from __future__ import annotations

import json
from pathlib import Path
import pickle
import subprocess
import time
import unicodedata

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score

from fisher_baselines.data import DEFAULT_SHEET, audit_workbook
from fisher_baselines.evaluation import (
    EvaluationError,
    _metric_bundle,
    _model,
    _runtime_versions,
    _sha256_json,
    assign_folds,
    write_json_file,
)

TEST_FOLDS = 5  # one of five template-grouped folds (~20%) is the held-out test
ML_MODELS = ("char_logreg", "word_char_linear_svc")
ABLATION = "word_char_linear_svc_unnormalized"
RULE_SCORES = {"no_match": 0, "cannot_analyze": 0, "review": 1, "high": 2}
BOOTSTRAP_RESAMPLES = 1_000
_ANALYZER = Path(__file__).resolve().parents[1] / "browser_extension" / "analyzer.mjs"
_NODE_SCRIPT = """
import { analyzeContent } from %s;
let input = "";
for await (const chunk of process.stdin) input += chunk;
process.stdout.write(JSON.stringify(JSON.parse(input).map((text) => analyzeContent(text).risk)));
"""
_HOMOGLYPHS = str.maketrans("aceopx", "асеорх")  # Latin -> Cyrillic look-alikes
PERTURBATIONS = {
    "uppercase": str.upper,
    "cyrillic_homoglyphs": lambda text: text.translate(_HOMOGLYPHS),
    "zero_width_joiners": lambda text: "‍".join(text),
    "truncate_64": lambda text: text[:64],
}


def normalize_model_input(text: str) -> str:
    """NFKC and removal of Unicode format controls (Cf), matching the duplicate key."""
    return "".join(c for c in unicodedata.normalize("NFKC", text) if unicodedata.category(c) != "Cf")


def rule_engine_scores(texts: list[str]) -> np.ndarray:
    """Score texts with the shipped v0.6 engine: 0 no match, 1 review, 2 high."""
    if not _ANALYZER.is_file():
        raise EvaluationError("the browser-extension rule engine is not available")
    script = _NODE_SCRIPT % json.dumps(_ANALYZER.as_uri())
    try:
        completed = subprocess.run(
            ["node", "--input-type=module", "-e", script],
            input=json.dumps(texts, ensure_ascii=False),
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
            timeout=600,
        )
        risks = json.loads(completed.stdout)
    except (OSError, subprocess.SubprocessError, json.JSONDecodeError) as exc:
        raise EvaluationError("rule engine scoring failed") from exc
    if len(risks) != len(texts) or not set(risks) <= set(RULE_SCORES):
        raise EvaluationError("rule engine returned an unexpected result")
    return np.array([RULE_SCORES[risk] for risk in risks], dtype=np.float64)


def _raw_scores(model, texts: list[str]) -> np.ndarray:
    if hasattr(model, "decision_function"):
        return model.decision_function(texts)
    return model.predict_proba(texts)[:, 1]


def _platt(scores: np.ndarray, y: np.ndarray) -> LogisticRegression:
    return LogisticRegression(C=1e6, max_iter=1_000).fit(scores.reshape(-1, 1), y)


def threshold_for_fpr(y: np.ndarray, probability: np.ndarray, max_fpr: float) -> float:
    """Lowest probability threshold whose ham false-positive rate stays within max_fpr."""
    ham = np.sort(probability[y == 0])[::-1]
    allowed = int(np.floor(max_fpr * len(ham)))
    if allowed >= len(ham):
        return 0.0
    # Hams tied with the boundary score fall below the threshold, so ties only make it stricter.
    return float(np.nextafter(ham[allowed], np.inf))


def expected_calibration_error(y: np.ndarray, probability: np.ndarray, bins: int = 10) -> float:
    index = np.minimum((probability * bins).astype(int), bins - 1)
    error = 0.0
    for b in range(bins):
        mask = index == b
        if mask.any():
            error += mask.mean() * abs(probability[mask].mean() - y[mask].mean())
    return float(error)


def _operating_metrics(y: np.ndarray, prediction: np.ndarray, score: np.ndarray) -> dict:
    bundle = _metric_bundle(y, prediction, score)
    matrix = bundle["confusion_matrix"]
    bundle["ham_false_positive_rate"] = matrix["fp"] / max(matrix["fp"] + matrix["tn"], 1)
    return bundle


def _slice_metrics(frame: pd.DataFrame, y: np.ndarray, prediction: np.ndarray) -> dict:
    lengths = frame["model_text"].str.len().to_numpy()
    slices = {f"script:{script}": frame["script"].to_numpy() == script for script in sorted(frame["script"].unique())}
    slices.update(
        {
            "length:<=40": lengths <= 40,
            "length:41-100": (lengths > 40) & (lengths <= 100),
            "length:>100": lengths > 100,
        }
    )
    result = {}
    for name, mask in slices.items():
        spam, ham = mask & (y == 1), mask & (y == 0)
        result[name] = {
            "support": int(mask.sum()),
            "spam_support": int(spam.sum()),
            "spam_recall": float(prediction[spam].mean()) if spam.any() else None,
            "ham_false_positive_rate": float(prediction[ham].mean()) if ham.any() else None,
        }
    return result


def _f1(y: np.ndarray, prediction: np.ndarray) -> float:
    tp = np.sum((prediction == 1) & (y == 1))
    denominator = np.sum(prediction == 1) + np.sum(y == 1)
    return float(2 * tp / denominator) if denominator else 0.0


def paired_bootstrap(
    y: np.ndarray, groups: np.ndarray, first: np.ndarray, second: np.ndarray, seed: int
) -> dict:
    """Template-group bootstrap 95% intervals for first-minus-second F1 and recall."""
    unique, inverse = np.unique(groups, return_inverse=True)
    members = [np.flatnonzero(inverse == g) for g in range(len(unique))]
    rng = np.random.default_rng(seed)
    f1_deltas, recall_deltas = [], []
    for _ in range(BOOTSTRAP_RESAMPLES):
        rows = np.concatenate([members[g] for g in rng.integers(0, len(unique), len(unique))])
        yy, a, b = y[rows], first[rows], second[rows]
        f1_deltas.append(_f1(yy, a) - _f1(yy, b))
        spam = yy == 1
        recall_deltas.append(float(a[spam].mean() - b[spam].mean()) if spam.any() else 0.0)
    interval = lambda values: [float(np.percentile(values, 2.5)), float(np.percentile(values, 97.5))]
    return {
        "resamples": BOOTSTRAP_RESAMPLES,
        "spam_f1_delta": {"point": _f1(y, first) - _f1(y, second), "ci95": interval(f1_deltas)},
        "spam_recall_delta": {
            "point": float(first[y == 1].mean() - second[y == 1].mean()),
            "ci95": interval(recall_deltas),
        },
    }


def _fit_calibrated(
    model_name: str,
    texts: np.ndarray,
    y: np.ndarray,
    dev_folds: np.ndarray,
    seed: int,
    max_fpr: float,
    normalize: bool,
):
    """Grouped dev out-of-fold scores -> Platt map and threshold; then refit on all dev."""
    prepare = (lambda batch: [normalize_model_input(t) for t in batch]) if normalize else list
    texts = np.array(prepare(texts), dtype=object)
    oof = np.full(len(y), np.nan)
    for fold in np.unique(dev_folds):
        train, valid = dev_folds != fold, dev_folds == fold
        model = _model(model_name, seed).fit(texts[train].tolist(), y[train])
        oof[valid] = _raw_scores(model, texts[valid].tolist())
    platt = _platt(oof, y)
    oof_probability = platt.predict_proba(oof.reshape(-1, 1))[:, 1]
    threshold = threshold_for_fpr(y, oof_probability, max_fpr)
    oof_prediction = (oof_probability >= threshold).astype(np.int8)
    started = time.perf_counter()
    final = _model(model_name, seed).fit(texts.tolist(), y)
    fit_seconds = time.perf_counter() - started
    dev = {
        "oof_at_operating_threshold": _operating_metrics(y, oof_prediction, oof_probability),
        "oof_brier": float(brier_score_loss(y, oof_probability)),
        "operating_threshold": threshold,
    }
    predict = lambda batch: platt.predict_proba(_raw_scores(final, prepare(batch)).reshape(-1, 1))[:, 1]
    return predict, threshold, dev, final, fit_seconds


def _selection_key(dev: dict) -> tuple[float, float]:
    metrics = dev["oof_at_operating_threshold"]
    return (metrics["spam_recall"], metrics["average_precision"])


def holdout_evaluate_prepared(
    prepared: pd.DataFrame,
    audit: dict[str, object],
    *,
    seed: int = 1729,
    max_ham_fpr: float = 0.01,
) -> dict[str, object]:
    if not 0 < max_ham_fpr < 1:
        raise EvaluationError("max ham false-positive rate must be between zero and one")
    folds = assign_folds(prepared, folds=TEST_FOLDS, seed=seed)
    test_mask = folds == 0
    dev_frame, test_frame = prepared[~test_mask], prepared[test_mask]
    dev_folds = folds[~test_mask]
    y_dev = (dev_frame["label"].to_numpy() == "spam").astype(np.int8)
    y_test = (test_frame["label"].to_numpy() == "spam").astype(np.int8)
    dev_texts = dev_frame["model_text"].to_numpy(dtype=object)
    test_texts = test_frame["model_text"].tolist()
    groups = test_frame["group_id"].to_numpy()
    crossings = len(set(dev_frame["group_id"]) & set(groups))
    if crossings:
        raise EvaluationError("template-group leakage between development and test")

    approaches: dict[str, dict] = {}
    test_predictions: dict[str, np.ndarray] = {}
    predictors: dict[str, tuple] = {}

    rule_test = rule_engine_scores(test_texts)
    rule_prediction = (rule_test >= 1).astype(np.int8)
    approaches["rules_v0_6"] = {
        "role": "baseline: shipped transparent rule engine, untrained",
        "operating_point": "risk in {review, high}",
        "test_at_operating_point": _operating_metrics(y_test, rule_prediction, rule_test),
        "test_high_only": _operating_metrics(y_test, (rule_test >= 2).astype(np.int8), rule_test),
        "test_roc_auc": float(roc_auc_score(y_test, rule_test)),
        "test_slices": _slice_metrics(test_frame, y_test, rule_prediction),
    }
    test_predictions["rules_v0_6"] = rule_prediction
    predictors["rules_v0_6"] = (lambda batch: rule_engine_scores(list(batch)), 1.0)

    for name in (*ML_MODELS, ABLATION):
        model_name = "word_char_linear_svc" if name == ABLATION else name
        try:
            predict, threshold, dev, final, fit_seconds = _fit_calibrated(
                model_name, dev_texts, y_dev, dev_folds, seed, max_ham_fpr, normalize=name != ABLATION
            )
            started = time.perf_counter()
            probability = predict(test_texts)
            predict_seconds = time.perf_counter() - started
        except (TypeError, ValueError) as exc:
            raise EvaluationError("model training or scoring failed") from exc
        prediction = (probability >= threshold).astype(np.int8)
        approaches[name] = {
            "role": {"char_logreg": "intermediate", ABLATION: "ablation: no input normalization"}.get(
                name, "advanced"
            ),
            "input_normalization": "none" if name == ABLATION else "NFKC + Unicode Cf removal",
            "calibration": "Platt sigmoid fitted on grouped development out-of-fold scores",
            "development": dev,
            "test_at_operating_threshold": _operating_metrics(y_test, prediction, probability),
            "test_at_probability_0_5": _operating_metrics(
                y_test, (probability >= 0.5).astype(np.int8), probability
            ),
            "test_roc_auc": float(roc_auc_score(y_test, probability)),
            "test_brier": float(brier_score_loss(y_test, probability)),
            "test_expected_calibration_error_10_bins": expected_calibration_error(y_test, probability),
            "test_slices": _slice_metrics(test_frame, y_test, prediction),
            "cost": {
                "fit_seconds_on_development": round(fit_seconds, 3),
                "predict_milliseconds_per_message": round(1000 * predict_seconds / len(test_texts), 4),
                "serialized_model_bytes_in_memory": len(pickle.dumps(final)),
            },
        }
        test_predictions[name] = prediction
        predictors[name] = (predict, threshold)

    selected = max(ML_MODELS, key=lambda name: _selection_key(approaches[name]["development"]))

    robustness = {}
    for perturbation, transform in PERTURBATIONS.items():
        perturbed = [transform(text) for text in test_texts]
        robustness[perturbation] = {}
        for name, (predict, threshold) in predictors.items():
            prediction = (predict(perturbed) >= threshold).astype(np.int8)
            robustness[perturbation][name] = {
                "spam_recall": float(prediction[y_test == 1].mean()),
                "ham_false_positive_rate": float(prediction[y_test == 0].mean()),
            }

    comparisons = {
        f"{selected}_minus_{other}": paired_bootstrap(
            y_test, groups, test_predictions[selected], test_predictions[other], seed
        )
        for other in test_predictions
        if other not in (selected, ABLATION)
    }

    return {
        "schema_version": "1.0.0",
        "task": "auxiliary_spam_ham",
        "evaluation_scope": "development_corpus_held_out_partition",
        "prohibited_claims": ["phishing benchmark", "campaign-disjoint", "deployment readiness"],
        "parameters": {"seed": seed, "test_fold_of": TEST_FOLDS, "max_ham_fpr": max_ham_fpr},
        "split": {
            "method": "StratifiedGroupKFold(label+script, template groups); fold 0 is test",
            "development_rows": int(len(dev_frame)),
            "test_rows": int(len(test_frame)),
            "test_spam": int(y_test.sum()),
            "development_test_group_crossings": crossings,
            "split_sha256": _sha256_json(
                sorted(zip(prepared["record_id"].tolist(), test_mask.astype(int).tolist()))
            ),
        },
        "selection_rule": "highest development out-of-fold spam recall at the ham-FPR threshold, then AP",
        "selected_model": selected,
        "approaches": approaches,
        "robustness_at_operating_threshold": robustness,
        "paired_bootstrap": comparisons,
        "audit_sha256": _sha256_json(audit),
        "source": {"workbook_sha256": audit.get("source", {}).get("workbook_sha256")},
        "runtime_versions": _runtime_versions(),
    }


def holdout_evaluate_workbook(
    workbook: str | Path,
    *,
    sheet: str = DEFAULT_SHEET,
    seed: int = 1729,
    max_ham_fpr: float = 0.01,
) -> dict[str, object]:
    prepared, audit = audit_workbook(workbook, sheet=sheet)
    return holdout_evaluate_prepared(prepared, audit, seed=seed, max_ham_fpr=max_ham_fpr)


def write_holdout_output(result: dict[str, object], output: str | Path) -> None:
    path = Path(output)
    if path.exists() or path.is_symlink():
        raise EvaluationError("holdout output destination already exists")
    if not path.parent.is_dir():
        raise EvaluationError("holdout output parent directory does not exist")
    write_json_file(result, path)
