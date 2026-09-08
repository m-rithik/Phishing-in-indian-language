from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from hashlib import sha256
import json
import math
from numbers import Real
import os
from pathlib import Path
import secrets
from typing import Mapping

import numpy as np
import pandas as pd

from fisher_baselines.data import DEFAULT_SHEET, audit_workbook, prepare_dataframe
from fisher_baselines.evaluation import (
    EvaluationError,
    _metric_bundle,
    _model,
    _model_metadata,
    _runtime_versions,
    _sha256_json,
    assign_folds,
)


@dataclass(frozen=True)
class Candidate:
    model: str
    c: float

    @property
    def key(self) -> str:
        return f"{self.model}:C={self.c:.1f}"

    def as_dict(self) -> dict[str, object]:
        return {"model": self.model, "C": self.c}


# This order is also the final deterministic tie-break after metric equality.
CANDIDATES = (
    Candidate("char_logreg", 1.0),
    Candidate("char_linear_svc", 1.0),
    Candidate("word_char_linear_svc", 1.0),
    Candidate("char_logreg", 0.5),
    Candidate("char_linear_svc", 0.5),
    Candidate("word_char_linear_svc", 0.5),
    Candidate("char_logreg", 2.0),
    Candidate("word_char_linear_svc", 2.0),
)

_FROZEN_BASELINES = (
    Candidate("char_logreg", 1.0),
    Candidate("word_char_linear_svc", 1.0),
)
_SUMMARY_METRICS = (
    "spam_precision",
    "spam_recall",
    "spam_f1",
    "macro_f1",
    "balanced_accuracy",
    "average_precision",
)
_COMPARISON_TOLERANCE = 1e-12


@dataclass(frozen=True)
class SelectionResult:
    audit: dict[str, object]
    manifest: dict[str, object]
    metrics: dict[str, object]


def _derived_seed(seed: int, *parts: object) -> int:
    material = "\0".join([str(seed), *(str(part) for part in parts)])
    return int.from_bytes(sha256(material.encode("utf-8")).digest()[:4], "big")


def _fit_and_score(
    model_name: str,
    c: float,
    seed: int,
    train_texts: list[str],
    train_y: np.ndarray,
    validation_texts: list[str],
    validation_y: np.ndarray,
) -> dict[str, object]:
    """Fit all learned preprocessing on train_texts, then score validation_texts."""
    try:
        model = _model(model_name, seed, c=c)
        model.fit(train_texts, train_y)
        prediction = model.predict(validation_texts).astype(np.int8)
        if model_name == "char_logreg":
            score = model.predict_proba(validation_texts)[:, 1]
        else:
            score = model.decision_function(validation_texts)
    except (KeyError, TypeError, ValueError) as exc:
        raise EvaluationError("model training or scoring failed") from exc
    return _metric_bundle(validation_y, prediction, score)


def select_candidate(scores: Mapping[str, Mapping[str, float]]) -> Candidate:
    missing = [candidate.key for candidate in CANDIDATES if candidate.key not in scores]
    if missing:
        raise EvaluationError("candidate selection scores are incomplete")

    def rank(candidate: Candidate) -> tuple[float, float, float, int]:
        metrics = scores[candidate.key]
        try:
            values = tuple(metrics[name] for name in ("spam_f1", "macro_f1", "spam_precision"))
        except (KeyError, TypeError) as exc:
            raise EvaluationError("candidate selection scores are invalid") from exc
        if any(
            isinstance(value, bool)
            or not isinstance(value, Real)
            or not math.isfinite(float(value))
            or not 0.0 <= float(value) <= 1.0
            for value in values
        ):
            raise EvaluationError("candidate selection scores are invalid")
        return (
            float(values[0]),
            float(values[1]),
            float(values[2]),
            -CANDIDATES.index(candidate),
        )

    return max(CANDIDATES, key=rank)


def _aggregate_inner(fold_metrics: list[dict[str, object]]) -> dict[str, float]:
    return {
        metric: float(np.mean([float(fold[metric]) for fold in fold_metrics]))
        for metric in ("spam_f1", "macro_f1", "spam_precision")
    }


def _summary(per_fold: list[dict[str, object]]) -> dict[str, object]:
    summary: dict[str, object] = {}
    for metric in _SUMMARY_METRICS:
        values = np.asarray([float(fold[metric]) for fold in per_fold], dtype=np.float64)
        summary[metric] = {
            "mean": float(np.mean(values)),
            "std": float(np.std(values)),
            "min": float(np.min(values)),
            "max": float(np.max(values)),
        }
    summary["summed_confusion_matrix"] = {
        key: int(sum(int(fold["confusion_matrix"][key]) for fold in per_fold))
        for key in ("tn", "fp", "fn", "tp")
    }
    return summary


def _acceptance_decision(
    *,
    selected_spam_f1_mean: float,
    selected_macro_f1_mean: float,
    comparator_spam_f1_mean: float,
    comparator_macro_f1_mean: float,
    selected_folds: list[dict[str, object]],
    comparator_folds: list[dict[str, object]],
) -> dict[str, object]:
    spam_f1_delta = selected_spam_f1_mean - comparator_spam_f1_mean
    macro_f1_decline = comparator_macro_f1_mean - selected_macro_f1_mean
    worse_fold_count = sum(
        float(selected["spam_f1"]) + _COMPARISON_TOLERANCE < float(reference["spam_f1"])
        for selected, reference in zip(selected_folds, comparator_folds, strict=True)
    )
    return {
        "comparator": {"model": "word_char_linear_svc", "C": 1.0},
        "required_spam_f1_mean_improvement": 0.01,
        "observed_spam_f1_mean_improvement": float(spam_f1_delta),
        "maximum_macro_f1_mean_decline": 0.005,
        "observed_macro_f1_mean_decline": float(macro_f1_decline),
        "maximum_outer_folds_with_worse_spam_f1": 1,
        "observed_outer_folds_with_worse_spam_f1": int(worse_fold_count),
        "floating_point_comparison_tolerance": _COMPARISON_TOLERANCE,
        "accepted": bool(
            spam_f1_delta + _COMPARISON_TOLERANCE >= 0.01
            and macro_f1_decline <= 0.005 + _COMPARISON_TOLERANCE
            and worse_fold_count <= 1
        ),
    }


def _split_digest(frame: pd.DataFrame, assignment: np.ndarray) -> str:
    rows = [
        {
            "record": row.record_id,
            "group": row.group_id,
            "fold": int(fold),
            "label": row.label,
            "script": row.script,
        }
        for row, fold in zip(frame.itertuples(index=False), assignment, strict=True)
    ]
    rows.sort(key=lambda row: str(row["record"]))
    return _sha256_json(rows)


def _group_crossings(frame: pd.DataFrame, assignment: np.ndarray) -> int:
    return int(
        (frame.assign(_fold=assignment).groupby("group_id")["_fold"].nunique() > 1).sum()
    )


def _nested_evaluate_prepared(
    prepared: pd.DataFrame,
    audit: dict[str, object],
    *,
    outer_folds: int,
    inner_folds: int,
    seed: int,
) -> SelectionResult:
    original_source = audit.get("source", {})
    safe_source = dict(original_source) if isinstance(original_source, dict) else {}
    safe_source.pop("selected_sheet", None)
    safe_source["selected_sheet_recorded"] = False
    safe_source["source_path_recorded"] = False
    audit["source"] = safe_source
    outer_assignment = assign_folds(prepared, folds=outer_folds, seed=seed)
    labels = (prepared["label"].to_numpy() == "spam").astype(np.int8)
    selected_fold_metrics: list[dict[str, object]] = []
    frozen_fold_metrics = {candidate.key: [] for candidate in _FROZEN_BASELINES}
    selected_configs: list[dict[str, object]] = []
    inner_results: list[dict[str, object]] = []
    inner_splits: list[dict[str, object]] = []
    outer_model_seeds: list[dict[str, int]] = []

    for outer_fold in range(outer_folds):
        outer_train_indexes = np.flatnonzero(outer_assignment != outer_fold)
        outer_validation_indexes = np.flatnonzero(outer_assignment == outer_fold)
        outer_train = prepared.iloc[outer_train_indexes].reset_index(drop=True)
        outer_validation = prepared.iloc[outer_validation_indexes].reset_index(drop=True)
        outer_train_y = (outer_train["label"].to_numpy() == "spam").astype(np.int8)
        outer_validation_y = labels[outer_validation_indexes]

        inner_seed = _derived_seed(seed, "inner", outer_fold)
        inner_assignment = assign_folds(outer_train, folds=inner_folds, seed=inner_seed)
        inner_splits.append(
            {
                "outer_fold": outer_fold,
                "seed": inner_seed,
                "split_sha256": _split_digest(outer_train, inner_assignment),
                "group_crossing_count": _group_crossings(outer_train, inner_assignment),
            }
        )

        candidate_aggregates: dict[str, dict[str, float]] = {}
        for candidate in CANDIDATES:
            candidate_fold_metrics: list[dict[str, object]] = []
            for inner_fold in range(inner_folds):
                inner_train_indexes = np.flatnonzero(inner_assignment != inner_fold)
                inner_validation_indexes = np.flatnonzero(inner_assignment == inner_fold)
                outcome = _fit_and_score(
                    candidate.model,
                    candidate.c,
                    inner_seed,
                    outer_train.loc[inner_train_indexes, "model_text"].tolist(),
                    outer_train_y[inner_train_indexes],
                    outer_train.loc[inner_validation_indexes, "model_text"].tolist(),
                    outer_train_y[inner_validation_indexes],
                )
                candidate_fold_metrics.append(outcome)
            candidate_aggregates[candidate.key] = _aggregate_inner(candidate_fold_metrics)

        selected = select_candidate(candidate_aggregates)
        selected_configs.append({"outer_fold": outer_fold, **selected.as_dict()})
        inner_results.append(
            {
                "outer_fold": outer_fold,
                "candidate_mean_scores": candidate_aggregates,
            }
        )

        outer_seed = _derived_seed(seed, "outer-model", outer_fold)
        outer_model_seeds.append({"outer_fold": outer_fold, "seed": outer_seed})
        outer_train_texts = outer_train["model_text"].tolist()
        outer_validation_texts = outer_validation["model_text"].tolist()
        selected_outcome = _fit_and_score(
            selected.model,
            selected.c,
            outer_seed,
            outer_train_texts,
            outer_train_y,
            outer_validation_texts,
            outer_validation_y,
        )
        selected_fold_metrics.append(
            {"outer_fold": outer_fold, **selected.as_dict(), **selected_outcome}
        )

        for baseline in _FROZEN_BASELINES:
            baseline_outcome = _fit_and_score(
                baseline.model,
                baseline.c,
                outer_seed,
                outer_train_texts,
                outer_train_y,
                outer_validation_texts,
                outer_validation_y,
            )
            frozen_fold_metrics[baseline.key].append(
                {"outer_fold": outer_fold, **baseline_outcome}
            )

    selected_summary = _summary(selected_fold_metrics)
    frozen_summaries = {
        key: _summary(per_fold) for key, per_fold in frozen_fold_metrics.items()
    }
    comparator_key = Candidate("word_char_linear_svc", 1.0).key
    comparator_folds = frozen_fold_metrics[comparator_key]
    acceptance = _acceptance_decision(
        selected_spam_f1_mean=float(selected_summary["spam_f1"]["mean"]),
        selected_macro_f1_mean=float(selected_summary["macro_f1"]["mean"]),
        comparator_spam_f1_mean=float(
            frozen_summaries[comparator_key]["spam_f1"]["mean"]
        ),
        comparator_macro_f1_mean=float(
            frozen_summaries[comparator_key]["macro_f1"]["mean"]
        ),
        selected_folds=selected_fold_metrics,
        comparator_folds=comparator_folds,
    )

    source = audit.get("source", {})
    workbook_hash = source.get("workbook_sha256") if isinstance(source, dict) else None
    selection_counts = Counter(
        Candidate(str(config["model"]), float(config["C"])).key
        for config in selected_configs
    )
    audit["evaluation_scope"] = "development_only"
    audit["development_only"] = True
    baseline_model_metadata = _model_metadata()
    candidate_features = {
        "char_logreg": baseline_model_metadata["char_logreg"],
        "char_linear_svc": {
            "features": "character TF-IDF",
            "ngram_range": [3, 5],
            "min_df": 2,
            "max_features": 100_000,
            "classifier": "class-balanced LinearSVC",
        },
        "word_char_linear_svc": baseline_model_metadata["word_char_linear_svc"],
    }
    manifest: dict[str, object] = {
        "schema_version": "1.0.0",
        "task": "auxiliary_spam_ham",
        "evaluation_scope": "development_only",
        "development_only": True,
        "prohibited_evidence_uses": [
            "phishing detection",
            "campaign generalization",
            "language performance",
            "score calibration",
            "deployment readiness",
        ],
        "source": {
            "workbook_sha256": workbook_hash,
            "selected_sheet_recorded": False,
            "source_path_recorded": False,
        },
        "parameters": {
            "seed": seed,
            "outer_folds": outer_folds,
            "inner_folds": inner_folds,
            "threshold_policy": "classifier default only; no threshold tuning",
            "floating_point_comparison_tolerance": _COMPARISON_TOLERANCE,
        },
        "candidates": [candidate.as_dict() for candidate in CANDIDATES],
        "candidate_features": candidate_features,
        "learned_preprocessing_policy": "TF-IDF is fitted inside each training partition only",
        "selection_rule": (
            "mean inner spam F1, then macro F1, then spam precision, then C priority "
            "1.0/0.5/2.0, then char_logreg/char_linear_svc/word_char_linear_svc"
        ),
        "runtime_versions": _runtime_versions(),
        "split": {
            "strategy": "nested StratifiedGroupKFold over label+mechanical-script strata",
            "grouping": "template-derived groups",
            "outer_split_sha256": _split_digest(prepared, outer_assignment),
            "outer_group_crossing_count": _group_crossings(prepared, outer_assignment),
            "inner_splits": inner_splits,
            "outer_model_seeds": outer_model_seeds,
        },
        "selected_config_per_fold": selected_configs,
        "selection_frequency": {
            candidate.key: int(selection_counts[candidate.key]) for candidate in CANDIDATES
        },
        "audit_sha256": _sha256_json(audit),
    }
    metrics: dict[str, object] = {
        "schema_version": "1.0.0",
        "task": "auxiliary_spam_ham",
        "evaluation_scope": "development_only",
        "average_precision_policy": (
            "computed and summarized per outer fold only; fold-specific scores are not pooled"
        ),
        "inner_selection": inner_results,
        "selected_policy": {
            "per_outer_fold": selected_fold_metrics,
            "summary": selected_summary,
        },
        "frozen_baselines": {
            key: {"per_outer_fold": frozen_fold_metrics[key], "summary": frozen_summaries[key]}
            for key in frozen_fold_metrics
        },
        "acceptance_decision": acceptance,
    }
    return SelectionResult(audit=audit, manifest=manifest, metrics=metrics)


def nested_evaluate_dataframe(
    frame: pd.DataFrame,
    *,
    outer_folds: int = 3,
    inner_folds: int = 3,
    seed: int = 1729,
    workbook_sha256: str | None = None,
    sheet: str = DEFAULT_SHEET,
) -> SelectionResult:
    prepared, audit = prepare_dataframe(frame)
    audit["source"] = {
        "workbook_sha256": workbook_sha256,
        "selected_sheet_recorded": False,
        "source_path_recorded": False,
    }
    return _nested_evaluate_prepared(
        prepared,
        audit,
        outer_folds=outer_folds,
        inner_folds=inner_folds,
        seed=seed,
    )


def nested_evaluate_workbook(
    workbook: str | Path,
    *,
    sheet: str = DEFAULT_SHEET,
    outer_folds: int = 3,
    inner_folds: int = 3,
    seed: int = 1729,
) -> SelectionResult:
    prepared, audit = audit_workbook(workbook, sheet=sheet)
    return _nested_evaluate_prepared(
        prepared,
        audit,
        outer_folds=outer_folds,
        inner_folds=inner_folds,
        seed=seed,
    )


def _canonical_output_bytes(result: SelectionResult) -> bytes:
    document = {
        "audit": result.audit,
        "selection_manifest": result.manifest,
        "selection_metrics": result.metrics,
    }
    try:
        return (
            json.dumps(
                document,
                allow_nan=False,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ).encode("utf-8")
            + b"\n"
        )
    except (TypeError, ValueError) as exc:
        raise EvaluationError("selection output is not finite canonical JSON") from exc


def _write_all(file_descriptor: int, data: bytes) -> None:
    view = memoryview(data)
    while view:
        written = os.write(file_descriptor, view)
        if written <= 0:
            raise OSError("selection output write failed")
        view = view[written:]


def _open_parent_directory(parent_path: Path) -> int:
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
        raise EvaluationError("selection output requires safe directory-open support")
    flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    parts = parent_path.parts
    if parent_path.is_absolute():
        current_fd = os.open(parent_path.anchor, flags)
        components = parts[1:]
    else:
        current_fd = os.open(".", flags)
        components = parts
    try:
        for component in components:
            if component in {"", "."}:
                continue
            if component == "..":
                raise EvaluationError("selection output parent traversal is not allowed")
            next_fd = os.open(component, flags, dir_fd=current_fd)
            os.close(current_fd)
            current_fd = next_fd
        return current_fd
    except Exception:
        os.close(current_fd)
        raise


def _parent_binding_matches(parent_fd: int, parent_path: Path) -> bool:
    descriptor_stat = os.fstat(parent_fd)
    verification_fd: int | None = None
    try:
        verification_fd = _open_parent_directory(parent_path)
        path_stat = os.fstat(verification_fd)
    except (EvaluationError, OSError):
        return False
    finally:
        if verification_fd is not None:
            os.close(verification_fd)
    return path_stat.st_dev == descriptor_stat.st_dev and path_stat.st_ino == descriptor_stat.st_ino


def write_selection_output(result: SelectionResult, output: str | Path) -> None:
    """Publish one complete aggregate JSON file without following or overwriting a target."""
    data = _canonical_output_bytes(result)
    destination = Path(output)
    parent = destination.parent
    filename = destination.name
    if not filename or filename in {".", ".."}:
        raise EvaluationError("selection output path is invalid")

    parent_fd: int | None = None
    stage_fd: int | None = None
    stage_name: str | None = None
    published = False
    try:
        parent_fd = _open_parent_directory(parent)
        stage_name = f".{filename}.stage-{secrets.token_hex(12)}"
        stage_fd = os.open(
            stage_name,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
            0o600,
            dir_fd=parent_fd,
        )
        _write_all(stage_fd, data)
        os.fsync(stage_fd)
        os.close(stage_fd)
        stage_fd = None

        if not _parent_binding_matches(parent_fd, parent):
            raise EvaluationError("selection output parent changed during publication")
        os.link(
            stage_name,
            filename,
            src_dir_fd=parent_fd,
            dst_dir_fd=parent_fd,
            follow_symlinks=False,
        )
        published = True
        if not _parent_binding_matches(parent_fd, parent):
            raise EvaluationError("selection output parent changed during publication")
        os.unlink(stage_name, dir_fd=parent_fd)
        stage_name = None
        os.fsync(parent_fd)
    except EvaluationError as exc:
        if published:
            raise EvaluationError(
                "selection output post-publication state requires manual inspection"
            ) from exc
        raise
    except OSError as exc:
        if published:
            raise EvaluationError(
                "selection output post-publication state requires manual inspection"
            ) from exc
        raise EvaluationError("selection output could not be published safely") from exc
    finally:
        if stage_fd is not None:
            try:
                os.close(stage_fd)
            except OSError:
                pass
        if parent_fd is not None:
            if stage_name is not None:
                try:
                    os.unlink(stage_name, dir_fd=parent_fd)
                except OSError:
                    pass
            try:
                os.close(parent_fd)
            except OSError:
                pass
