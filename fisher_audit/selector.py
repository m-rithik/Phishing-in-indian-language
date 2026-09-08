"""Deterministic synthetic rehearsal of Fisher's canonical pilot-audit selector.

This module deliberately accepts no message text, source evidence, or real audit
mode.  It validates only the minimal synthetic metadata required to exercise the
frozen cell allocation, HMAC ranking, and annotator-supplement procedure.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import hmac
import json
import os
from pathlib import Path
import re
import stat
from typing import Any, Iterable, Mapping


INPUT_SCHEMA_VERSION = "1.0.0"
SCHEMA_VERSION = "1.1.0"
ALGORITHM_VERSION = "fisher-audit-rehearsal-1.1.0"
SCOPE = "SYNTHETIC_REHEARSAL_ONLY"

LANGUAGE_STATES = {
    "hindi",
    "tamil",
    "telugu",
    "english_indic_code_mixed",
    "uncertain",
}
PRIMARY_STATES = {"benign", "phishing", "uncertain"}
PROVENANCE_CLASSES = {
    "tester_donated_authentic",
    "tester_authored_simulation",
    "public_authentic",
    "llm_drafted_human_edited",
}
PARTITIONS = {"pilot", "excluded"}

_ITEM_ID = re.compile(r"item_[a-z0-9][a-z0-9_-]{0,62}\Z")
_ANNOTATOR_ID = re.compile(r"annotator_[a-z0-9][a-z0-9_-]{0,62}\Z")
_LOWER_HEX_64 = re.compile(r"[0-9a-f]{64}\Z")
_EXPECTED_FIELDS = {
    "schema_version",
    "scope",
    "item_id",
    "simulated_partition",
    "simulated_final_language_state",
    "simulated_final_primary_state",
    "simulated_provenance_class",
    "blind_annotator_ids",
    "final_annotator_id",
    "synthetic_bundle_sha256",
}

MAX_FILE_BYTES = 128 * 1024 * 1024
MAX_LINE_BYTES = 32 * 1024
MAX_RECORDS = 100_000

LIMITATIONS = (
    "CANNOT_CERTIFY_HUMAN_AUDIT",
    "CANNOT_CERTIFY_CSPRNG_WITNESSING",
    "CANNOT_CERTIFY_FROZEN_HASHES",
    "CANNOT_CERTIFY_ATTEMPTED_UNIVERSE_COMPLETENESS",
    "CANNOT_CERTIFY_GOVERNANCE_APPROVAL",
    "CANNOT_CERTIFY_ZERO_PROHIBITED_FINDINGS",
)


@dataclass(frozen=True)
class Diagnostic:
    severity: str
    code: str
    line: int | None = None
    field: str | None = None


@dataclass(frozen=True)
class Attempt:
    source_line: int
    item_id: str
    partition: str
    language_state: str
    primary_state: str
    provenance_class: str
    blind_annotator_ids: tuple[str, str]
    final_annotator_id: str
    bundle_sha256: str

    @property
    def cell_key(self) -> str:
        return f"{self.language_state}|{self.primary_state}|{self.provenance_class}"

    @property
    def annotator_ids(self) -> tuple[str, str, str]:
        return (*self.blind_annotator_ids, self.final_annotator_id)

    def canonical_record(self) -> dict[str, Any]:
        return {
            "blind_annotator_ids": list(self.blind_annotator_ids),
            "final_annotator_id": self.final_annotator_id,
            "item_id": self.item_id,
            "schema_version": INPUT_SCHEMA_VERSION,
            "scope": SCOPE,
            "simulated_final_language_state": self.language_state,
            "simulated_final_primary_state": self.primary_state,
            "simulated_partition": self.partition,
            "simulated_provenance_class": self.provenance_class,
            "synthetic_bundle_sha256": self.bundle_sha256,
        }


@dataclass(frozen=True)
class RehearsalReport:
    structurally_valid: bool
    diagnostics: tuple[Diagnostic, ...]
    attempted_items: int
    nonempty_cells: int
    prescribed_ten_percent_n: int | None
    main_selected_count: int
    supplement_selected_count: int
    fallback_entire_universe: bool
    revised_sampling_rule_required: bool
    input_file_sha256: str | None
    canonical_universe_sha256: str | None
    main_manifest_sha256: str | None
    supplement_manifest_sha256: str | None
    selection_manifest_sha256: str | None
    seed_hex: str | None
    cell_allocations: dict[str, dict[str, int]]
    main_sample: tuple[dict[str, Any], ...]
    supplements: tuple[dict[str, Any], ...]
    supplement_processing: tuple[dict[str, Any], ...]
    initially_missing_annotator_ids: tuple[str, ...]
    final_covered_annotator_ids: tuple[str, ...]
    final_uncovered_annotator_ids: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "algorithm_version": ALGORITHM_VERSION,
            "attempted_items": self.attempted_items,
            "canonical_universe_sha256": self.canonical_universe_sha256,
            "cell_allocations": self.cell_allocations,
            "diagnostics": [asdict(value) for value in self.diagnostics],
            "fallback_entire_universe": self.fallback_entire_universe,
            "final_covered_annotator_ids": list(self.final_covered_annotator_ids),
            "final_uncovered_annotator_ids": list(self.final_uncovered_annotator_ids),
            "initially_missing_annotator_ids": list(
                self.initially_missing_annotator_ids
            ),
            "input_file_sha256": self.input_file_sha256,
            "limitations": list(LIMITATIONS),
            "main_manifest_sha256": self.main_manifest_sha256,
            "main_sample": list(self.main_sample),
            "main_selected_count": self.main_selected_count,
            "nonempty_cells": self.nonempty_cells,
            "prescribed_ten_percent_n": self.prescribed_ten_percent_n,
            "release_blocked": True,
            "revised_sampling_rule_required": self.revised_sampling_rule_required,
            "schema_version": SCHEMA_VERSION,
            "scope": SCOPE,
            "seed_hex": self.seed_hex,
            "selection_manifest_sha256": self.selection_manifest_sha256,
            "structurally_valid": self.structurally_valid,
            "supplement_manifest_sha256": self.supplement_manifest_sha256,
            "supplement_processing": list(self.supplement_processing),
            "supplement_selected_count": self.supplement_selected_count,
            "supplements": list(self.supplements),
        }


class _DuplicateKeyError(ValueError):
    pass


class _NonFiniteNumberError(ValueError):
    pass


def _utf8_key(value: str) -> bytes:
    return value.encode("utf-8")


def _canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        allow_nan=False,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")


def _json_sha256(value: Any) -> str:
    return sha256(_canonical_json_bytes(value)).hexdigest()


def _object_pairs_no_duplicates(pairs: Iterable[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise _DuplicateKeyError("duplicate JSON key")
        result[key] = value
    return result


def _reject_nonfinite_number(value: str) -> None:
    del value
    raise _NonFiniteNumberError("non-finite JSON number")


def allocate_hamilton(capacities: Mapping[str, int], sample_size: int) -> dict[str, int]:
    """Allocate one per cell, then Hamilton quotas over remaining capacities."""

    if type(sample_size) is not int:
        raise ValueError("sample size must be an integer")
    if not capacities or any(
        not isinstance(key, str) or not key.isascii() for key in capacities
    ):
        raise ValueError("cell keys must be ASCII strings")
    if any(type(value) is not int or value <= 0 for value in capacities.values()):
        raise ValueError("capacities must be positive integers")
    cell_keys = sorted(capacities, key=_utf8_key)
    total = sum(capacities.values())
    if sample_size < len(cell_keys) or sample_size > total:
        raise ValueError("sample size cannot cover the requested cells")

    allocation = {key: 1 for key in cell_keys}
    remaining_slots = sample_size - len(cell_keys)
    if remaining_slots == 0:
        return allocation

    remaining_capacities = {key: capacities[key] - 1 for key in cell_keys}
    denominator = sum(remaining_capacities.values())
    if denominator == 0:
        raise ValueError("no remaining capacity")

    remainders: dict[str, int] = {}
    for key in cell_keys:
        numerator = remaining_slots * remaining_capacities[key]
        floor_quota, remainder = divmod(numerator, denominator)
        allocation[key] += floor_quota
        remainders[key] = remainder

    unfilled = sample_size - sum(allocation.values())
    remainder_order = sorted(
        cell_keys,
        key=lambda key: (-remainders[key], _utf8_key(key)),
    )
    for key in remainder_order[:unfilled]:
        allocation[key] += 1

    if sum(allocation.values()) != sample_size:
        raise AssertionError("Hamilton allocation arithmetic failed")
    if any(allocation[key] > capacities[key] for key in cell_keys):
        raise AssertionError("Hamilton allocation exceeded capacity")
    return allocation


def hmac_rank_digest(seed: bytes, cell_key: str, item_id: str) -> bytes:
    """Return the protocol's raw HMAC-SHA256 item-ranking digest."""

    if len(seed) != 32:
        raise ValueError("seed must contain exactly 32 bytes")
    message = (cell_key + "\0" + item_id).encode("utf-8")
    return hmac.digest(seed, message, "sha256")


def _validate_record(value: Any, line: int) -> tuple[Attempt | None, list[Diagnostic]]:
    diagnostics: list[Diagnostic] = []
    if not isinstance(value, dict):
        return None, [Diagnostic("error", "record_not_object", line)]
    if set(value) != _EXPECTED_FIELDS:
        return None, [Diagnostic("error", "record_fields", line)]

    checks = (
        (
            isinstance(value["schema_version"], str)
            and value["schema_version"] == INPUT_SCHEMA_VERSION,
            "schema_version",
            "schema_version",
        ),
        (
            isinstance(value["scope"], str) and value["scope"] == SCOPE,
            "non_synthetic_scope",
            "scope",
        ),
        (
            isinstance(value["item_id"], str)
            and _ITEM_ID.fullmatch(value["item_id"]) is not None,
            "item_id",
            "item_id",
        ),
        (
            isinstance(value["simulated_partition"], str)
            and value["simulated_partition"] in PARTITIONS,
            "partition",
            "simulated_partition",
        ),
        (
            isinstance(value["simulated_final_language_state"], str)
            and value["simulated_final_language_state"] in LANGUAGE_STATES,
            "language_state",
            "simulated_final_language_state",
        ),
        (
            isinstance(value["simulated_final_primary_state"], str)
            and value["simulated_final_primary_state"] in PRIMARY_STATES,
            "primary_state",
            "simulated_final_primary_state",
        ),
        (
            isinstance(value["simulated_provenance_class"], str)
            and value["simulated_provenance_class"] in PROVENANCE_CLASSES,
            "provenance_class",
            "simulated_provenance_class",
        ),
        (
            isinstance(value["final_annotator_id"], str)
            and _ANNOTATOR_ID.fullmatch(value["final_annotator_id"]) is not None,
            "final_annotator_id",
            "final_annotator_id",
        ),
        (
            isinstance(value["synthetic_bundle_sha256"], str)
            and _LOWER_HEX_64.fullmatch(value["synthetic_bundle_sha256"]) is not None,
            "bundle_sha256",
            "synthetic_bundle_sha256",
        ),
    )
    for passed, code, field in checks:
        if not passed:
            diagnostics.append(Diagnostic("error", code, line, field))

    blind = value["blind_annotator_ids"]
    if (
        not isinstance(blind, list)
        or len(blind) != 2
        or any(
            not isinstance(identifier, str)
            or _ANNOTATOR_ID.fullmatch(identifier) is None
            for identifier in blind
        )
    ):
        diagnostics.append(
            Diagnostic("error", "blind_annotator_ids", line, "blind_annotator_ids")
        )
    elif blind != sorted(blind, key=_utf8_key) or len(set(blind)) != 2:
        diagnostics.append(
            Diagnostic(
                "error", "blind_annotator_ids_order_or_uniqueness", line,
                "blind_annotator_ids"
            )
        )
    elif (
        isinstance(value["final_annotator_id"], str)
        and value["final_annotator_id"] in blind
    ):
        diagnostics.append(
            Diagnostic("error", "annotators_not_distinct", line, "final_annotator_id")
        )

    partition = value["simulated_partition"]
    language = value["simulated_final_language_state"]
    primary = value["simulated_final_primary_state"]
    if partition == "pilot" and (language == "uncertain" or primary == "uncertain"):
        diagnostics.append(Diagnostic("error", "pilot_final_state", line))
    if partition == "excluded" and language != "uncertain" and primary != "uncertain":
        diagnostics.append(Diagnostic("error", "excluded_final_state", line))

    if diagnostics:
        return None, diagnostics
    return Attempt(
        source_line=line,
        item_id=value["item_id"],
        partition=partition,
        language_state=language,
        primary_state=primary,
        provenance_class=value["simulated_provenance_class"],
        blind_annotator_ids=(blind[0], blind[1]),
        final_annotator_id=value["final_annotator_id"],
        bundle_sha256=value["synthetic_bundle_sha256"],
    ), []


def _read_attempts(path: Path) -> tuple[list[Attempt], list[Diagnostic], str | None]:
    try:
        metadata = path.lstat()
    except OSError:
        return [], [Diagnostic("error", "file_unavailable")], None
    if not stat.S_ISREG(metadata.st_mode):
        return [], [Diagnostic("error", "input_not_regular_file")], None
    if metadata.st_size > MAX_FILE_BYTES:
        return [], [Diagnostic("error", "file_too_large")], None
    try:
        flags = os.O_RDONLY
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        descriptor = os.open(path, flags)
    except OSError:
        return [], [Diagnostic("error", "file_unavailable")], None
    try:
        opened_metadata = os.fstat(descriptor)
        if not stat.S_ISREG(opened_metadata.st_mode):
            return [], [Diagnostic("error", "input_not_regular_file")], None
        if opened_metadata.st_size > MAX_FILE_BYTES:
            return [], [Diagnostic("error", "file_too_large")], None
        chunks: list[bytes] = []
        remaining = MAX_FILE_BYTES + 1
        while remaining:
            chunk = os.read(descriptor, min(1024 * 1024, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        raw = b"".join(chunks)
    except OSError:
        return [], [Diagnostic("error", "file_unavailable")], None
    finally:
        os.close(descriptor)
    if len(raw) > MAX_FILE_BYTES:
        return [], [Diagnostic("error", "file_too_large")], None
    input_hash = sha256(raw).hexdigest()
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        return [], [Diagnostic("error", "invalid_utf8")], input_hash
    if text.startswith("\ufeff"):
        return [], [Diagnostic("error", "utf8_bom")], input_hash

    physical_lines = text.split("\n")
    if physical_lines and physical_lines[-1] == "":
        physical_lines.pop()
    if not physical_lines:
        return [], [Diagnostic("error", "empty_file")], input_hash
    if len(physical_lines) > MAX_RECORDS:
        return [], [Diagnostic("error", "record_limit")], input_hash

    attempts: list[Attempt] = []
    diagnostics: list[Diagnostic] = []
    for line_number, physical_line in enumerate(physical_lines, start=1):
        line = physical_line[:-1] if physical_line.endswith("\r") else physical_line
        if not line:
            diagnostics.append(Diagnostic("error", "blank_line", line_number))
            continue
        if len(line.encode("utf-8")) > MAX_LINE_BYTES:
            diagnostics.append(Diagnostic("error", "line_too_large", line_number))
            continue
        try:
            value = json.loads(
                line,
                object_pairs_hook=_object_pairs_no_duplicates,
                parse_constant=_reject_nonfinite_number,
            )
        except _DuplicateKeyError:
            diagnostics.append(Diagnostic("error", "duplicate_json_key", line_number))
            continue
        except _NonFiniteNumberError:
            diagnostics.append(Diagnostic("error", "nonfinite_json", line_number))
            continue
        except (json.JSONDecodeError, RecursionError):
            diagnostics.append(Diagnostic("error", "invalid_json", line_number))
            continue
        attempt, record_diagnostics = _validate_record(value, line_number)
        diagnostics.extend(record_diagnostics)
        if attempt is not None:
            attempts.append(attempt)

    item_ids: dict[str, int] = {}
    bundle_hashes: dict[str, int] = {}
    for attempt in attempts:
        if attempt.item_id in item_ids:
            diagnostics.append(
                Diagnostic("error", "duplicate_item_id", attempt.source_line)
            )
        else:
            item_ids[attempt.item_id] = attempt.source_line
        if attempt.bundle_sha256 in bundle_hashes:
            diagnostics.append(
                Diagnostic("error", "duplicate_bundle_sha256", attempt.source_line)
            )
        else:
            bundle_hashes[attempt.bundle_sha256] = attempt.source_line
    return attempts, diagnostics, input_hash


def _selection_entry(attempt: Attempt, digest: bytes) -> dict[str, Any]:
    return {
        "annotator_ids": list(attempt.annotator_ids),
        "cell_key": attempt.cell_key,
        "hmac_sha256": digest.hex(),
        "item_id": attempt.item_id,
        "release_blocked": True,
        "scope": SCOPE,
        "synthetic_bundle_sha256": attempt.bundle_sha256,
    }


def _manifest_envelope(
    manifest_kind: str, entries: Iterable[Mapping[str, Any]]
) -> dict[str, Any]:
    """Bind every independently hashed submanifest to the safety boundary."""

    return {
        "algorithm_version": ALGORITHM_VERSION,
        "entries": list(entries),
        "manifest_kind": manifest_kind,
        "release_blocked": True,
        "schema_version": SCHEMA_VERSION,
        "scope": SCOPE,
    }


def _select_supplements_indexed(
    ordered_attempts: list[Attempt],
    main_attempts: list[Attempt],
    seed: bytes,
) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
    list[str],
    list[str],
    list[str],
]:
    """Select supplements from per-annotator ranked indices.

    Each attempt's digest is computed once. Candidate memberships total exactly
    three per attempt, so construction is bounded by the declared universe plus
    sorting of those membership lists. Pointers only advance past items already
    selected by the main sample or an earlier supplement.
    """

    digest_by_item_id = {
        attempt.item_id: hmac_rank_digest(seed, attempt.cell_key, attempt.item_id)
        for attempt in ordered_attempts
    }
    candidates_by_annotator: dict[str, list[Attempt]] = {}
    for attempt in ordered_attempts:
        for annotator_id in attempt.annotator_ids:
            candidates_by_annotator.setdefault(annotator_id, []).append(attempt)
    for candidates in candidates_by_annotator.values():
        candidates.sort(
            key=lambda attempt: (
                digest_by_item_id[attempt.item_id],
                _utf8_key(attempt.item_id),
            )
        )

    all_annotators = set(candidates_by_annotator)
    covered_annotators = {
        annotator for attempt in main_attempts for annotator in attempt.annotator_ids
    }
    initially_missing = sorted(all_annotators - covered_annotators, key=_utf8_key)
    selected_item_ids = {attempt.item_id for attempt in main_attempts}
    next_candidate = {annotator_id: 0 for annotator_id in initially_missing}
    supplements: list[dict[str, Any]] = []
    processing: list[dict[str, Any]] = []

    for annotator_id in initially_missing:
        if annotator_id in covered_annotators:
            processing.append(
                {
                    "annotator_id": annotator_id,
                    "selected_item_id": None,
                    "status": "skipped_already_covered",
                }
            )
            continue
        candidates = candidates_by_annotator[annotator_id]
        pointer = next_candidate[annotator_id]
        while (
            pointer < len(candidates)
            and candidates[pointer].item_id in selected_item_ids
        ):
            pointer += 1
        next_candidate[annotator_id] = pointer
        if pointer == len(candidates):
            raise RuntimeError("supplement candidate unavailable")

        chosen = candidates[pointer]
        entry = _selection_entry(chosen, digest_by_item_id[chosen.item_id])
        newly_covered = sorted(
            set(chosen.annotator_ids) - covered_annotators, key=_utf8_key
        )
        entry["selected_for_annotator_id"] = annotator_id
        entry["newly_covered_annotator_ids"] = newly_covered
        supplements.append(entry)
        processing.append(
            {
                "annotator_id": annotator_id,
                "selected_item_id": chosen.item_id,
                "status": "selected_supplement",
            }
        )
        selected_item_ids.add(chosen.item_id)
        covered_annotators.update(chosen.annotator_ids)

    final_covered = sorted(covered_annotators, key=_utf8_key)
    final_uncovered = sorted(all_annotators - covered_annotators, key=_utf8_key)
    return supplements, processing, initially_missing, final_covered, final_uncovered


def _empty_report(
    diagnostics: Iterable[Diagnostic], input_hash: str | None = None
) -> RehearsalReport:
    return RehearsalReport(
        structurally_valid=False,
        diagnostics=tuple(diagnostics),
        attempted_items=0,
        nonempty_cells=0,
        prescribed_ten_percent_n=None,
        main_selected_count=0,
        supplement_selected_count=0,
        fallback_entire_universe=False,
        revised_sampling_rule_required=False,
        input_file_sha256=input_hash,
        canonical_universe_sha256=None,
        main_manifest_sha256=None,
        supplement_manifest_sha256=None,
        selection_manifest_sha256=None,
        seed_hex=None,
        cell_allocations={},
        main_sample=(),
        supplements=(),
        supplement_processing=(),
        initially_missing_annotator_ids=(),
        final_covered_annotator_ids=(),
        final_uncovered_annotator_ids=(),
    )


def invalid_usage_report(code: str = "cli_usage") -> RehearsalReport:
    return _empty_report((Diagnostic("error", code),))


def rehearse_file(path: Path, seed_hex: str) -> RehearsalReport:
    """Validate a synthetic universe and deterministically rehearse selection."""

    attempts, diagnostics, input_hash = _read_attempts(path)
    if not isinstance(seed_hex, str) or _LOWER_HEX_64.fullmatch(seed_hex) is None:
        diagnostics.append(Diagnostic("error", "seed_hex"))
    if diagnostics:
        return _empty_report(diagnostics, input_hash)
    if not attempts:
        return _empty_report((Diagnostic("error", "empty_universe"),), input_hash)

    seed = bytes.fromhex(seed_hex)
    ordered_attempts = sorted(attempts, key=lambda value: _utf8_key(value.item_id))
    canonical_records = [value.canonical_record() for value in ordered_attempts]
    universe_hash = _json_sha256(canonical_records)

    cells: dict[str, list[Attempt]] = {}
    for attempt in ordered_attempts:
        cells.setdefault(attempt.cell_key, []).append(attempt)
    capacities = {key: len(value) for key, value in cells.items()}
    attempted_n = len(ordered_attempts)
    prescribed_n = (attempted_n + 9) // 10
    fallback = attempted_n < 1_200 or len(cells) > 60
    main_target = attempted_n if fallback else prescribed_n
    allocation = (
        dict(sorted(capacities.items(), key=lambda value: _utf8_key(value[0])))
        if fallback
        else allocate_hamilton(capacities, main_target)
    )

    main_entries: list[dict[str, Any]] = []
    main_attempts: list[Attempt] = []
    for cell_key in sorted(cells, key=_utf8_key):
        ranked = sorted(
            cells[cell_key],
            key=lambda attempt: (
                hmac_rank_digest(seed, cell_key, attempt.item_id),
                _utf8_key(attempt.item_id),
            ),
        )
        for attempt in ranked[: allocation[cell_key]]:
            digest = hmac_rank_digest(seed, cell_key, attempt.item_id)
            main_entries.append(_selection_entry(attempt, digest))
            main_attempts.append(attempt)

    try:
        (
            supplements,
            supplement_processing,
            initially_missing,
            final_covered,
            final_uncovered,
        ) = _select_supplements_indexed(ordered_attempts, main_attempts, seed)
    except RuntimeError:
        return _empty_report(
            (Diagnostic("error", "supplement_candidate_unavailable"),), input_hash
        )
    if final_uncovered:
        return _empty_report(
            (Diagnostic("error", "annotator_coverage_incomplete"),), input_hash
        )

    cell_allocations = {
        key: {"capacity": capacities[key], "main_selected": allocation[key]}
        for key in sorted(cells, key=_utf8_key)
    }
    main_manifest_hash = _json_sha256(
        _manifest_envelope("main_sample", main_entries)
    )
    supplement_manifest_hash = _json_sha256(
        _manifest_envelope("annotator_supplements", supplements)
    )
    selection_core = {
        "algorithm_version": ALGORITHM_VERSION,
        "canonical_universe_sha256": universe_hash,
        "cell_allocations": cell_allocations,
        "fallback_entire_universe": fallback,
        "final_covered_annotator_ids": final_covered,
        "final_uncovered_annotator_ids": final_uncovered,
        "initially_missing_annotator_ids": initially_missing,
        "main_sample": main_entries,
        "prescribed_ten_percent_n": prescribed_n,
        "release_blocked": True,
        "schema_version": SCHEMA_VERSION,
        "scope": SCOPE,
        "seed_hex": seed_hex,
        "supplement_processing": supplement_processing,
        "supplements": supplements,
    }
    selection_hash = _json_sha256(selection_core)
    report_diagnostics = (
        (Diagnostic("warning", "protocol_bound_fallback"),) if fallback else ()
    )
    return RehearsalReport(
        structurally_valid=True,
        diagnostics=report_diagnostics,
        attempted_items=attempted_n,
        nonempty_cells=len(cells),
        prescribed_ten_percent_n=prescribed_n,
        main_selected_count=len(main_entries),
        supplement_selected_count=len(supplements),
        fallback_entire_universe=fallback,
        revised_sampling_rule_required=fallback,
        input_file_sha256=input_hash,
        canonical_universe_sha256=universe_hash,
        main_manifest_sha256=main_manifest_hash,
        supplement_manifest_sha256=supplement_manifest_hash,
        selection_manifest_sha256=selection_hash,
        seed_hex=seed_hex,
        cell_allocations=cell_allocations,
        main_sample=tuple(main_entries),
        supplements=tuple(supplements),
        supplement_processing=tuple(supplement_processing),
        initially_missing_annotator_ids=tuple(initially_missing),
        final_covered_annotator_ids=tuple(final_covered),
        final_uncovered_annotator_ids=tuple(final_uncovered),
    )


def format_json(report: RehearsalReport) -> str:
    return _canonical_json_bytes(report.to_dict()).decode("utf-8")


def format_text(report: RehearsalReport) -> str:
    lines = [
        SCOPE,
        "STRUCTURALLY_VALID" if report.structurally_valid else "INVALID",
        "release_blocked: true",
        f"attempted_items: {report.attempted_items}",
        f"nonempty_cells: {report.nonempty_cells}",
        f"prescribed_ten_percent_n: {report.prescribed_ten_percent_n}",
        f"main_selected_count: {report.main_selected_count}",
        f"supplement_selected_count: {report.supplement_selected_count}",
        f"fallback_entire_universe: {str(report.fallback_entire_universe).lower()}",
        f"revised_sampling_rule_required: {str(report.revised_sampling_rule_required).lower()}",
        f"canonical_universe_sha256: {report.canonical_universe_sha256}",
        f"main_manifest_sha256: {report.main_manifest_sha256}",
        f"supplement_manifest_sha256: {report.supplement_manifest_sha256}",
        f"selection_manifest_sha256: {report.selection_manifest_sha256}",
        "initially_missing_annotator_ids: "
        + ",".join(report.initially_missing_annotator_ids),
        "final_covered_annotator_ids: "
        + ",".join(report.final_covered_annotator_ids),
        "final_uncovered_annotator_ids: "
        + ",".join(report.final_uncovered_annotator_ids),
    ]
    lines.extend(
        "supplement_processing: "
        + value["annotator_id"]
        + ":"
        + value["status"]
        + ":"
        + (value["selected_item_id"] or "none")
        for value in report.supplement_processing
    )
    lines.extend(f"limitation: {value}" for value in LIMITATIONS)
    lines.extend(
        "diagnostic: "
        + ":".join(
            part
            for part in (
                diagnostic.severity,
                diagnostic.code,
                str(diagnostic.line) if diagnostic.line is not None else None,
                diagnostic.field,
            )
            if part is not None
        )
        for diagnostic in report.diagnostics
    )
    return "\n".join(lines)
