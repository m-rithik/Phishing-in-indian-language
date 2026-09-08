from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from importlib import metadata
import json
import os
from pathlib import Path
import platform
import tempfile
import warnings

import numpy as np
import openpyxl
import pandas as pd
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_fscore_support,
)
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.svm import LinearSVC

from fisher_baselines import __version__
from fisher_baselines.data import DEFAULT_SHEET, audit_workbook, prepare_dataframe


class EvaluationError(ValueError):
    """Raised when development evaluation cannot satisfy its split contract."""


@dataclass(frozen=True)
class EvaluationResult:
    audit: dict[str, object]
    run_manifest: dict[str, object]
    metrics: dict[str, object]


def _canonical_json_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
        "utf-8"
    )


def _sha256_json(value: object) -> str:
    return sha256(_canonical_json_bytes(value)).hexdigest()


def assign_folds(frame: pd.DataFrame, *, folds: int, seed: int) -> np.ndarray:
    if not isinstance(folds, int) or isinstance(folds, bool) or folds < 2:
        raise EvaluationError("fold count must be an integer of at least two")
    if not isinstance(seed, int) or isinstance(seed, bool):
        raise EvaluationError("seed must be an integer")
    if frame.empty or set(frame["label"].unique()) != {"ham", "spam"}:
        raise EvaluationError("evaluation requires retained ham and spam rows")
    if frame["group_id"].nunique() < folds:
        raise EvaluationError("evaluation has too few template groups")
    group_counts_by_label = frame.groupby("label")["group_id"].nunique()
    if (group_counts_by_label < folds).any():
        raise EvaluationError("evaluation has too few groups for one label")

    strata = frame["label"].astype(str) + "|" + frame["script"].astype(str)
    splitter = StratifiedGroupKFold(n_splits=folds, shuffle=True, random_state=seed)
    assignment = np.full(len(frame), -1, dtype=np.int32)
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message=r"The least populated class in y has only .*",
                category=UserWarning,
            )
            for fold, (_, validation_indexes) in enumerate(
                splitter.split(np.zeros(len(frame)), strata, groups=frame["group_id"])
            ):
                assignment[validation_indexes] = fold
    except ValueError as exc:
        raise EvaluationError("grouped stratification failed") from exc
    if (assignment < 0).any():
        raise EvaluationError("grouped stratification was incomplete")

    group_fold_counts = frame.assign(fold=assignment).groupby("group_id")["fold"].nunique()
    if not (group_fold_counts == 1).all():
        raise EvaluationError("template-group leakage was detected")
    for fold in range(folds):
        training_labels = set(frame.loc[assignment != fold, "label"])
        validation_labels = set(frame.loc[assignment == fold, "label"])
        if training_labels != {"ham", "spam"} or validation_labels != {"ham", "spam"}:
            raise EvaluationError("a fold does not contain both labels")
    return assignment


def _char_tfidf() -> TfidfVectorizer:
    return TfidfVectorizer(
        analyzer="char",
        ngram_range=(3, 5),
        min_df=2,
        max_features=100_000,
        sublinear_tf=True,
        dtype=np.float32,
    )


def _model(model_name: str, seed: int, *, c: float = 1.0) -> Pipeline:
    if model_name == "char_logreg":
        return Pipeline(
            [
                ("tfidf", _char_tfidf()),
                (
                    "classifier",
                    LogisticRegression(
                        C=c,
                        class_weight="balanced",
                        max_iter=1_000,
                        random_state=seed,
                        solver="liblinear",
                    ),
                ),
            ]
        )
    if model_name == "char_linear_svc":
        return Pipeline(
            [
                ("tfidf", _char_tfidf()),
                (
                    "classifier",
                    LinearSVC(C=c, class_weight="balanced", random_state=seed, dual="auto"),
                ),
            ]
        )
    if model_name == "word_char_linear_svc":
        return Pipeline(
            [
                (
                    "features",
                    FeatureUnion(
                        [
                            (
                                "word",
                                TfidfVectorizer(
                                    analyzer="word",
                                    ngram_range=(1, 2),
                                    min_df=2,
                                    max_features=50_000,
                                    sublinear_tf=True,
                                    dtype=np.float32,
                                ),
                            ),
                            ("char", _char_tfidf()),
                        ]
                    ),
                ),
                (
                    "classifier",
                    LinearSVC(C=c, class_weight="balanced", random_state=seed, dual="auto"),
                ),
            ]
        )
    raise KeyError(model_name)


def _metric_bundle(y_true: np.ndarray, prediction: np.ndarray, score: np.ndarray) -> dict[str, object]:
    matrix = confusion_matrix(y_true, prediction, labels=[0, 1])
    tn, fp, fn, tp = (int(value) for value in matrix.ravel())
    precision, recall, spam_f1, _ = precision_recall_fscore_support(
        y_true,
        prediction,
        labels=[1],
        average="binary",
        zero_division=0,
    )
    both_labels = len(np.unique(y_true)) == 2
    return {
        "support": int(len(y_true)),
        "spam_support": int(np.count_nonzero(y_true == 1)),
        "ham_support": int(np.count_nonzero(y_true == 0)),
        "confusion_matrix": {"tn": tn, "fp": fp, "fn": fn, "tp": tp},
        "spam_precision": float(precision),
        "spam_recall": float(recall),
        "spam_f1": float(spam_f1),
        "macro_f1": float(f1_score(y_true, prediction, average="macro", zero_division=0)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, prediction))
        if both_labels
        else None,
        "average_precision": float(average_precision_score(y_true, score))
        if both_labels
        else None,
    }


def _model_metadata() -> dict[str, object]:
    return {
        "char_logreg": {
            "features": "character TF-IDF",
            "ngram_range": [3, 5],
            "min_df": 2,
            "max_features": 100_000,
            "classifier": "class-balanced LogisticRegression",
        },
        "word_char_linear_svc": {
            "features": "FeatureUnion(word TF-IDF, character TF-IDF)",
            "word_ngram_range": [1, 2],
            "char_ngram_range": [3, 5],
            "min_df": 2,
            "word_max_features": 50_000,
            "char_max_features": 100_000,
            "classifier": "class-balanced LinearSVC",
        },
    }


def _runtime_versions() -> dict[str, str]:
    try:
        package_version = metadata.version("fisher-baselines")
    except metadata.PackageNotFoundError:
        package_version = __version__
    return {
        "python": platform.python_version(),
        "fisher_baselines": package_version,
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "openpyxl": openpyxl.__version__,
        "scikit_learn": sklearn.__version__,
    }


def _evaluate_prepared(
    prepared: pd.DataFrame,
    audit: dict[str, object],
    *,
    folds: int,
    seed: int,
) -> EvaluationResult:
    fold_assignment = assign_folds(prepared, folds=folds, seed=seed)
    y = (prepared["label"].to_numpy() == "spam").astype(np.int8)
    texts = prepared["model_text"].to_numpy(dtype=object)
    metrics_models: dict[str, object] = {}

    for model_name in _model_metadata():
        predictions = np.full(len(prepared), -1, dtype=np.int8)
        scores = np.full(len(prepared), np.nan, dtype=np.float64)
        fold_metrics: list[dict[str, object]] = []
        for fold in range(folds):
            train_indexes = np.flatnonzero(fold_assignment != fold)
            validation_indexes = np.flatnonzero(fold_assignment == fold)
            model = _model(model_name, seed)
            try:
                model.fit(texts[train_indexes].tolist(), y[train_indexes])
                fold_predictions = model.predict(texts[validation_indexes].tolist()).astype(np.int8)
                if model_name == "char_logreg":
                    fold_scores = model.predict_proba(texts[validation_indexes].tolist())[:, 1]
                else:
                    fold_scores = model.decision_function(texts[validation_indexes].tolist())
            except (TypeError, ValueError) as exc:
                raise EvaluationError("model training or scoring failed") from exc
            predictions[validation_indexes] = fold_predictions
            scores[validation_indexes] = fold_scores
            fold_metrics.append(
                {
                    "fold": fold,
                    **_metric_bundle(y[validation_indexes], fold_predictions, fold_scores),
                }
            )
        if (predictions < 0).any() or not np.isfinite(scores).all():
            raise EvaluationError("out-of-fold prediction generation was incomplete")

        per_script: dict[str, object] = {}
        for script in sorted(prepared["script"].unique()):
            mask = prepared["script"].to_numpy() == script
            per_script[script] = _metric_bundle(y[mask], predictions[mask], scores[mask])
        metrics_models[model_name] = {
            "pooled_oof": _metric_bundle(y, predictions, scores),
            "per_fold": fold_metrics,
            "mean_per_fold_average_precision": float(
                np.mean(
                    [fold_metric["average_precision"] for fold_metric in fold_metrics]
                )
            ),
            "per_script_pooled": per_script,
        }

    split_rows = [
        {
            "record_id": row.record_id,
            "group_id": row.group_id,
            "fold": int(fold),
            "label": row.label,
            "script": row.script,
        }
        for row, fold in zip(prepared.itertuples(index=False), fold_assignment, strict=True)
    ]
    split_rows.sort(key=lambda row: row["record_id"])
    group_violations = int(
        (prepared.assign(fold=fold_assignment).groupby("group_id")["fold"].nunique() > 1).sum()
    )

    source = audit.get("source", {})
    workbook_hash = source.get("workbook_sha256") if isinstance(source, dict) else None
    stratum_counts = (
        (prepared["label"].astype(str) + "|" + prepared["script"].astype(str))
        .value_counts()
        .sort_index()
    )
    manifest: dict[str, object] = {
        "schema_version": "1.0.0",
        "task": "auxiliary_spam_ham",
        "evaluation_scope": "development_only",
        "split_description": "StratifiedGroupKFold over label+mechanical-script strata, grouped by template ID",
        "prohibited_claims": ["protected test", "campaign-disjoint", "phishing benchmark"],
        "parameters": {"seed": seed, "folds": folds},
        "source": {
            "workbook_sha256": workbook_hash,
            "source_path_recorded": False,
        },
        "runtime_versions": _runtime_versions(),
        "models": _model_metadata(),
        "metric_interpretation": {
            "pooled_oof_average_precision": (
                "Descriptive only: it ranks fold-specific out-of-fold scores together even though "
                "separately fitted folds are not calibrated to a common score scale."
            ),
            "mean_per_fold_average_precision": (
                "Arithmetic mean of independently computed fold average-precision values."
            ),
        },
        "split": {
            "stratification": "label+script",
            "grouping": "template_group_id",
            "split_manifest_sha256": _sha256_json(split_rows),
            "group_cross_fold_violations": group_violations,
            "stratum_support": {stratum: int(count) for stratum, count in stratum_counts.items()},
            "strata_below_fold_count": [
                stratum for stratum, count in stratum_counts.items() if count < folds
            ],
            "stratification_is_approximate": bool((stratum_counts < folds).any()),
        },
        "audit_sha256": _sha256_json(audit),
    }
    metrics: dict[str, object] = {
        "schema_version": "1.0.0",
        "evaluation_scope": "development_only",
        "metric_interpretation": manifest["metric_interpretation"],
        "models": metrics_models,
    }
    return EvaluationResult(audit=audit, run_manifest=manifest, metrics=metrics)


def evaluate_dataframe(
    frame: pd.DataFrame,
    *,
    folds: int = 3,
    seed: int = 1729,
    workbook_sha256: str | None = None,
    sheet: str = DEFAULT_SHEET,
) -> EvaluationResult:
    prepared, audit = prepare_dataframe(frame)
    audit["source"] = {
        "workbook_sha256": workbook_sha256,
        "selected_sheet": sheet,
        "source_path_recorded": False,
    }
    return _evaluate_prepared(prepared, audit, folds=folds, seed=seed)


def evaluate_workbook(
    workbook: str | Path,
    *,
    sheet: str = DEFAULT_SHEET,
    folds: int = 3,
    seed: int = 1729,
) -> EvaluationResult:
    prepared, audit = audit_workbook(workbook, sheet=sheet)
    return _evaluate_prepared(prepared, audit, folds=folds, seed=seed)


def _atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
            temporary_name = handle.name
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_name, path)
    finally:
        if temporary_name is not None:
            try:
                Path(temporary_name).unlink(missing_ok=True)
            except OSError:
                pass


def write_json_file(value: object, path: str | Path) -> None:
    data = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2).encode("utf-8") + b"\n"
    _atomic_write(Path(path), data)


def write_evaluation_outputs(result: EvaluationResult, output_dir: str | Path) -> None:
    destination = Path(output_dir)
    if destination.exists():
        if destination.is_symlink() or not destination.is_dir():
            raise EvaluationError("evaluation output destination is not a regular directory")
        try:
            occupied = next(destination.iterdir(), None) is not None
        except OSError as exc:
            raise EvaluationError("evaluation output destination is not readable") from exc
        if occupied:
            raise EvaluationError("evaluation output destination is not empty")
    else:
        try:
            destination.mkdir(parents=True, exist_ok=False)
        except OSError as exc:
            raise EvaluationError("evaluation output destination cannot be created") from exc
    write_json_file(result.audit, destination / "audit.json")
    write_json_file(result.run_manifest, destination / "run_manifest.json")
    write_json_file(result.metrics, destination / "metrics.json")
