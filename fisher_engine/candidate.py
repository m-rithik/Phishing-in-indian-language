"""Deterministic synthetic E0 provider and candidate mechanics for Fisher.

This module implements only the candidate stage of the engine contract.  It
accepts an already validated VMP text/hash and static provider binding, validates
the selector/provider boundary, and returns canonical records for the integration
layer.  Errors carry controlled codes and never echo provider or message data.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from functools import cached_property
from hashlib import sha256
from itertools import product
import math
import re
from typing import Any, Iterable, Sequence

from ._canonical import (
    CanonicalError,
    canonical_json_bytes,
    exact_keys,
    is_nonboolean_int,
    is_sha256,
    strict_json_loads,
)
from ._numeric import (
    f64_bits_to_float,
    float_to_f64_bits,
    ordered_logsumexp,
    ordered_softmax,
    sequential_sum,
)


PROVIDER_MANIFEST_MAX_BYTES = 4 * 1024 * 1024
MAX_REWRITE_SPANS = 64
MAX_READINGS_PER_UNIT = 8
MAX_SPAN_CODEPOINTS = 512
MAX_SPAN_UTF8_BYTES = 2_048
MAX_PATH_CODEPOINTS = 20_000
MAX_PATH_UTF8_BYTES = 80_000
BEAM_WIDTH = 64
RETURNED_PATH_LIMIT = 8
CANDIDATE_PATH_ARTIFACT_MAX_BYTES = 1 * 1024 * 1024
PROVIDER_EXECUTION_MAX_BYTES = 1 * 1024 * 1024
CANDIDATE_DIAGNOSTICS_MAX_BYTES = 64 * 1024
CANDIDATE_WORK_BUDGET = 2_000_000
CANDIDATE_PATH_ARTIFACT_FIELDS = (
    "artifact_version",
    "path_id",
    "path_sha256",
    "vmp_sha256",
    "vmp_length",
    "provider_reading_manifest_sha256",
    "text",
    "alignment",
    "lineage",
    "composition_score_f64_bits",
    "q_numerator_f64_bits",
    "q_f64_bits",
    "effective_rewrite_spans",
)

_PROVIDER_ID = re.compile(r"provider_[a-z0-9][a-z0-9_-]{0,62}\Z")
_NORMALIZER_ID = re.compile(r"normalizer_[a-z0-9][a-z0-9_-]{0,62}\Z")
_PATH_ID = re.compile(r"candidate_path_[a-z0-9][a-z0-9_-]{0,55}\Z")
_SPAN_FIELDS = ("span_index", "start", "end", "source_text")
_UNIT_FIELDS = ("unit_index", "unit_kind", "start", "end", "source_text", "readings")
_READING_FIELDS = (
    "provider_rank",
    "reading_text",
    "reading_alignment",
    "raw_logit_f64_bits",
)
_CONFIGURED_MODES = {"COMPOSED_SPAN", "DIRECT_FULL_PATH"}
_DISPATCH_OUTCOMES = {
    "SUCCEEDED",
    "NOT_INVOKED",
    "UNAVAILABLE_FALLBACK",
    "TIMEOUT_FALLBACK",
    "PROVIDER_INVALID_OUTPUT",
    "NORMALIZER_INVALID_OUTPUT",
}
_UNAVAILABLE_CODES = {"PROVIDER_UNAVAILABLE", "NORMALIZER_UNAVAILABLE"}
_TIMEOUT_CODES = {"PROVIDER_TIMEOUT", "NORMALIZER_TIMEOUT"}
_PROVIDER_EXECUTION_FIELDS = (
    "configured_mode",
    "provider_config_id",
    "provider_config_sha256",
    "normalizer_id",
    "normalizer_sha256",
    "eligible_spans",
    "invocation_attempted",
    "outcome",
    "output_accepted",
    "bypass_reason",
    "failure_code",
    "provider_manifest_sha256",
)
_CANDIDATE_DIAGNOSTIC_FIELDS = (
    "mode",
    "temperature_f64_bits",
    "search_mode",
    "input_count",
    "span_merge_reduction_count",
    "partial_merge_reduction_count",
    "full_merge_reduction_count",
    "total_merge_reduction_count",
    "postmerge_count",
    "returned_count",
    "preK_scope",
    "L_returned_f64_bits",
    "L_preK_f64_bits",
    "retained_preK_composition_mass_f64_bits",
    "q_normalizer_f64_bits",
    "q_max_f64_bits",
)


class CandidateValidationError(ValueError):
    """A candidate failure containing one controlled, non-sensitive code."""

    def __init__(self, code: str, *, safe_count: int = 0) -> None:
        super().__init__(code)
        self.code = code
        self.safe_count = safe_count


@dataclass(frozen=True)
class InternalCandidatePath:
    """A validated path plus its canonical envelope record."""

    path_id: str
    path_sha256: str
    text: str
    alignment: tuple[tuple[int, int], ...]
    lineage: dict[str, Any]
    composition_score: float
    q_numerator: float
    q: float
    effective_rewrite_spans: tuple[dict[str, Any], ...]

    @property
    def record(self) -> dict[str, Any]:
        return {
            "path_id": self.path_id,
            "path_sha256": self.path_sha256,
            "lineage": self.lineage,
            "composition_score_f64_bits": float_to_f64_bits(self.composition_score),
            "q_numerator_f64_bits": float_to_f64_bits(self.q_numerator),
            "q_f64_bits": float_to_f64_bits(self.q),
            "effective_rewrite_spans": [dict(span) for span in self.effective_rewrite_spans],
        }


@dataclass(frozen=True)
class CandidateRun:
    """Candidate-stage result consumed by the engine-envelope assembler."""

    provider_execution: dict[str, Any]
    provider_manifest: dict[str, Any] | None
    provider_manifest_bytes: bytes | None
    provider_manifest_sha256: str | None
    candidate_diagnostics: dict[str, Any] | None
    internal_paths: tuple[InternalCandidatePath, ...]
    execution_status: str
    failure_stage: str
    invalid_codes: tuple[str, ...]
    configured_span_entries_capped: int
    eligible_spans_capped: int
    provider_count: int
    normalizer_count: int
    candidate_count: int
    alignment_count: int
    vmp_sha256: str = ""
    vmp_length: int = 0
    work_units: int = 0

    @property
    def candidate_paths(self) -> tuple[dict[str, Any], ...]:
        return tuple(path.record for path in self.internal_paths)

    @property
    def provider_execution_bytes(self) -> bytes:
        return _provider_execution_bytes(self.provider_execution)

    @property
    def candidate_diagnostics_bytes(self) -> bytes | None:
        if self.candidate_diagnostics is None:
            return None
        return _candidate_diagnostics_bytes(self.candidate_diagnostics)

    @property
    def candidate_path_artifacts(self) -> tuple[dict[str, Any], ...]:
        if self.provider_manifest_sha256 is None:
            return ()
        return tuple(
            build_candidate_path_artifact(
                path,
                vmp_sha256=self.vmp_sha256,
                provider_manifest_sha256=self.provider_manifest_sha256,
                vmp_length=self.vmp_length,
            )
            for path in self.internal_paths
        )

    @property
    def candidate_path_artifact_bytes(self) -> tuple[bytes, ...]:
        return tuple(
            candidate_path_artifact_bytes(value)
            for value in self.candidate_path_artifacts
        )

    @property
    def candidate_path_artifact_sha256s(self) -> tuple[str, ...]:
        return tuple(
            sha256(value).hexdigest() for value in self.candidate_path_artifact_bytes
        )


@dataclass(frozen=True)
class CandidateReplayResult:
    """Authoritative reconstruction from canonical candidate artifacts."""

    provider_execution: dict[str, Any]
    provider_manifest: dict[str, Any]
    provider_manifest_sha256: str
    candidate_diagnostics: dict[str, Any]
    internal_paths: tuple[InternalCandidatePath, ...]
    candidate_path_artifacts: tuple[dict[str, Any], ...]
    candidate_path_artifact_bytes: tuple[bytes, ...]
    candidate_path_artifact_sha256s: tuple[str, ...]
    work_units: int

    @property
    def candidate_paths(self) -> tuple[dict[str, Any], ...]:
        return tuple(path.record for path in self.internal_paths)


@dataclass(frozen=True)
class _SpanCandidate:
    text: str
    alignment: tuple[tuple[int, int], ...]
    ranks: tuple[int, ...]
    score: float


@dataclass(frozen=True)
class _Contribution:
    contributor: dict[str, Any]
    score: float

    @cached_property
    def key(self) -> bytes:
        return canonical_json_bytes(self.contributor)


@dataclass(frozen=True)
class _WorkCandidate:
    text: str
    alignment: tuple[tuple[int, int], ...]
    contributions: tuple[_Contribution, ...]

    @cached_property
    def score(self) -> float:
        if len(self.contributions) == 1:
            return self.contributions[0].score
        ordered = sorted(self.contributions, key=lambda value: value.key)
        return _safe_logsumexp([value.score for value in ordered])

    @cached_property
    def lineage(self) -> dict[str, Any]:
        ordered = sorted(self.contributions, key=lambda value: value.key)
        return {
            "lineage_version": "1.0.0",
            "contributors": [value.contributor for value in ordered],
        }

    @cached_property
    def lineage_bytes(self) -> bytes:
        return canonical_json_bytes(self.lineage)


@dataclass
class _CandidateWorkCounter:
    """Budget expanded nodes, ordering comparisons, and materialized code points."""

    used: int = 0
    limit: int = field(default_factory=lambda: CANDIDATE_WORK_BUDGET)

    def consume(self, amount: int) -> None:
        if type(amount) is not int or amount < 0:
            raise _fail("candidate_invalid_work_accounting")
        if amount > self.limit - self.used:
            raise _fail("candidate_work_budget_exceeded")
        self.used += amount


@dataclass(frozen=True)
class _BeamNode:
    parent: _BeamNode | None
    span_candidate: _SpanCandidate | None
    span_index: int
    contributions: tuple[_Contribution, ...]

    @cached_property
    def score(self) -> float:
        if len(self.contributions) == 1:
            return self.contributions[0].score
        ordered = sorted(self.contributions, key=lambda value: value.key)
        return _safe_logsumexp([value.score for value in ordered])

    @cached_property
    def lineage_bytes(self) -> bytes:
        ordered = sorted(self.contributions, key=lambda value: value.key)
        lineage = {
            "lineage_version": "1.0.0",
            "contributors": [value.contributor for value in ordered],
        }
        return canonical_json_bytes(lineage)


def _fail(code: str, *, safe_count: int = 0) -> CandidateValidationError:
    return CandidateValidationError(code, safe_count=safe_count)


def _is_int(value: object) -> bool:
    return type(value) is int


def _utf8(value: str) -> bytes:
    return value.encode("utf-8")


def _alignment_json(alignment: Sequence[tuple[int, int]]) -> list[list[int]]:
    return [[start, end] for start, end in alignment]


def _alignment_bytes(alignment: Sequence[tuple[int, int]]) -> bytes:
    return canonical_json_bytes(_alignment_json(alignment))


def _identity_alignment(start: int, end: int) -> tuple[tuple[int, int], ...]:
    return tuple((index, index + 1) for index in range(start, end))


def _validate_text_bound(text: object, *, span: bool) -> str:
    if not isinstance(text, str):
        raise _fail("candidate_invalid_text")
    max_codepoints = MAX_SPAN_CODEPOINTS if span else MAX_PATH_CODEPOINTS
    max_bytes = MAX_SPAN_UTF8_BYTES if span else MAX_PATH_UTF8_BYTES
    if len(text) > max_codepoints or len(_utf8(text)) > max_bytes:
        raise _fail("candidate_text_too_large")
    try:
        canonical_json_bytes(text)
    except CanonicalError as error:
        raise _fail("candidate_invalid_text") from error
    return text


def _artifact_ranges(visible_artifacts: object, text_length: int) -> tuple[tuple[int, int], ...]:
    if type(visible_artifacts) is not list:
        raise _fail("candidate_invalid_artifact_inventory")
    ranges: list[tuple[int, int]] = []
    previous_end = 0
    for artifact in visible_artifacts:
        if not isinstance(artifact, dict):
            raise _fail("candidate_invalid_artifact_inventory")
        start = artifact.get("start")
        end = artifact.get("end")
        if (
            not _is_int(start)
            or not _is_int(end)
            or not 0 <= start < end <= text_length
            or start < previous_end
        ):
            raise _fail("candidate_invalid_artifact_inventory")
        ranges.append((start, end))
        previous_end = end
    return tuple(ranges)


def validate_rewrite_spans(
    selector_output: object,
    *,
    vmp_text: str,
    visible_artifacts: object,
) -> tuple[dict[str, Any], ...]:
    """Validate the complete selector result without retaining unsafe members."""

    if type(selector_output) is not list or len(selector_output) > MAX_REWRITE_SPANS:
        raise _fail("candidate_invalid_eligibility")
    artifact_ranges = _artifact_ranges(visible_artifacts, len(vmp_text))
    accepted: list[dict[str, Any]] = []
    previous_end = 0
    for expected_index, value in enumerate(selector_output):
        if not exact_keys(value, _SPAN_FIELDS):
            raise _fail("candidate_invalid_eligibility")
        span_index = value["span_index"]
        start = value["start"]
        end = value["end"]
        source_text = value["source_text"]
        if (
            not _is_int(span_index)
            or not _is_int(start)
            or not _is_int(end)
            or span_index != expected_index
            or not 0 <= start < end <= len(vmp_text)
            or start < previous_end
            or not isinstance(source_text, str)
            or source_text != vmp_text[start:end]
        ):
            raise _fail("candidate_invalid_eligibility")
        if any(start < artifact_end and artifact_start < end for artifact_start, artifact_end in artifact_ranges):
            raise _fail("candidate_invalid_eligibility")
        accepted.append(
            {
                "span_index": span_index,
                "start": start,
                "end": end,
                "source_text": source_text,
            }
        )
        previous_end = end
    return tuple(accepted)


def _decode_alignment(value: object) -> tuple[tuple[int, int], ...]:
    if type(value) is not list:
        raise _fail("candidate_invalid_alignment")
    decoded: list[tuple[int, int]] = []
    for pair in value:
        if type(pair) is not list or len(pair) != 2:
            raise _fail("candidate_invalid_alignment")
        start, end = pair
        if not _is_int(start) or not _is_int(end):
            raise _fail("candidate_invalid_alignment")
        decoded.append((start, end))
    return tuple(decoded)


def _validate_monotonic_alignment(
    text: str,
    alignment: tuple[tuple[int, int], ...],
    *,
    vmp_length: int,
) -> None:
    if len(text) != len(alignment):
        raise _fail("candidate_invalid_alignment")
    previous_start = -1
    previous_end = -1
    for start, end in alignment:
        if (
            not 0 <= start < end <= vmp_length
            or start < previous_start
            or end < previous_end
        ):
            raise _fail("candidate_invalid_alignment")
        previous_start = start
        previous_end = end


def _validate_span_alignment(
    text: str,
    alignment: tuple[tuple[int, int], ...],
    *,
    span_start: int,
    span_end: int,
    vmp_length: int,
) -> None:
    _validate_monotonic_alignment(text, alignment, vmp_length=vmp_length)
    covered_through = span_start
    for start, end in alignment:
        if start < span_start or end > span_end:
            raise _fail("candidate_invalid_alignment")
        if start > covered_through:
            raise _fail("candidate_invalid_alignment")
        covered_through = max(covered_through, end)
    if covered_through != span_end:
        raise _fail("candidate_invalid_alignment")


def _containing_span(
    start: int,
    end: int,
    spans: Sequence[dict[str, Any]],
) -> dict[str, Any] | None:
    for span in spans:
        if span["start"] <= start and end <= span["end"]:
            return span
    return None


def _validate_direct_alignment(
    reading_text: str,
    alignment: tuple[tuple[int, int], ...],
    *,
    vmp_text: str,
    spans: Sequence[dict[str, Any]],
) -> None:
    _validate_monotonic_alignment(reading_text, alignment, vmp_length=len(vmp_text))
    covered_through = 0
    outside_positions: list[int] = []
    outside_text: list[str] = []
    for character, (start, end) in zip(reading_text, alignment):
        if start > covered_through:
            raise _fail("candidate_invalid_alignment")
        covered_through = max(covered_through, end)
        if _containing_span(start, end, spans) is None:
            if end != start + 1:
                raise _fail("candidate_invalid_alignment")
            outside_positions.append(start)
            outside_text.append(character)
    if covered_through != len(vmp_text):
        raise _fail("candidate_invalid_alignment")
    expected_positions: list[int] = []
    cursor = 0
    for span in spans:
        expected_positions.extend(range(cursor, span["start"]))
        cursor = span["end"]
    expected_positions.extend(range(cursor, len(vmp_text)))
    if outside_positions != expected_positions:
        raise _fail("candidate_invalid_alignment")
    if outside_text != [vmp_text[position] for position in expected_positions]:
        raise _fail("candidate_invalid_alignment")


def _validate_artifact_spans(
    value: object,
    *,
    vmp_length: int,
) -> tuple[dict[str, Any], ...]:
    if type(value) is not list or len(value) > MAX_REWRITE_SPANS:
        raise _fail("candidate_path_artifact_invalid_spans")
    spans: list[dict[str, Any]] = []
    previous_end = 0
    for index, span in enumerate(value):
        if not exact_keys(span, _SPAN_FIELDS):
            raise _fail("candidate_path_artifact_invalid_spans")
        assert isinstance(span, dict)
        start = span["start"]
        end = span["end"]
        source_text = span["source_text"]
        if (
            not _is_int(span["span_index"])
            or span["span_index"] != index
            or not _is_int(start)
            or not _is_int(end)
            or not 0 <= start < end <= vmp_length
            or start < previous_end
            or not isinstance(source_text, str)
            or len(source_text) != end - start
        ):
            raise _fail("candidate_path_artifact_invalid_spans")
        try:
            canonical_json_bytes(source_text)
        except CanonicalError as error:
            raise _fail("candidate_path_artifact_invalid_spans") from error
        spans.append(dict(span))
        previous_end = end
    return tuple(spans)


def _validate_lineage(value: object) -> dict[str, Any]:
    if not exact_keys(value, ("lineage_version", "contributors")):
        raise _fail("candidate_path_artifact_invalid_lineage")
    assert isinstance(value, dict)
    contributors = value["contributors"]
    if value["lineage_version"] != "1.0.0" or type(contributors) is not list or not contributors:
        raise _fail("candidate_path_artifact_invalid_lineage")
    canonical_contributors: list[dict[str, Any]] = []
    for contributor in contributors:
        if not isinstance(contributor, dict):
            raise _fail("candidate_path_artifact_invalid_lineage")
        mode = contributor.get("mode")
        if mode == "COMPOSED_SPAN":
            if not exact_keys(contributor, ("mode", "units")):
                raise _fail("candidate_path_artifact_invalid_lineage")
            units = contributor["units"]
            if type(units) is not list or not 1 <= len(units) <= MAX_REWRITE_SPANS:
                raise _fail("candidate_path_artifact_invalid_lineage")
            for index, unit in enumerate(units):
                if not exact_keys(unit, ("unit_index", "ranks")):
                    raise _fail("candidate_path_artifact_invalid_lineage")
                ranks = unit["ranks"]
                if (
                    not _is_int(unit["unit_index"])
                    or unit["unit_index"] != index
                    or type(ranks) is not list
                    or not 1 <= len(ranks) <= 8
                    or any(not _is_int(rank) or not 1 <= rank <= 8 for rank in ranks)
                    or ranks != sorted(set(ranks))
                ):
                    raise _fail("candidate_path_artifact_invalid_lineage")
        elif mode == "DIRECT_FULL_PATH":
            if not exact_keys(contributor, ("mode", "unit_index", "ranks")):
                raise _fail("candidate_path_artifact_invalid_lineage")
            ranks = contributor["ranks"]
            if (
                contributor["unit_index"] != 0
                or type(contributor["unit_index"]) is not int
                or type(ranks) is not list
                or not 1 <= len(ranks) <= 8
                or any(not _is_int(rank) or not 1 <= rank <= 8 for rank in ranks)
                or ranks != sorted(set(ranks))
            ):
                raise _fail("candidate_path_artifact_invalid_lineage")
        elif mode == "IDENTITY_BYPASS":
            if not exact_keys(contributor, ("mode",)):
                raise _fail("candidate_path_artifact_invalid_lineage")
        else:
            raise _fail("candidate_path_artifact_invalid_lineage")
        canonical_contributors.append(contributor)
    contributor_bytes = [canonical_json_bytes(item) for item in canonical_contributors]
    if contributor_bytes != sorted(contributor_bytes):
        raise _fail("candidate_path_artifact_invalid_lineage")
    return value


def validate_candidate_path_artifact(
    value: object,
    *,
    expected_vmp_sha256: str | None = None,
    expected_provider_manifest_sha256: str | None = None,
) -> None:
    if not exact_keys(value, CANDIDATE_PATH_ARTIFACT_FIELDS):
        raise _fail("candidate_path_artifact_schema_or_enum")
    assert isinstance(value, dict)
    if (
        value["artifact_version"] != "1.0.0"
        or not isinstance(value["path_id"], str)
        or _PATH_ID.fullmatch(value["path_id"]) is None
        or not is_sha256(value["path_sha256"])
        or not is_sha256(value["vmp_sha256"])
        or not is_nonboolean_int(value["vmp_length"], minimum=0, maximum=MAX_PATH_CODEPOINTS)
        or not is_sha256(value["provider_reading_manifest_sha256"])
    ):
        raise _fail("candidate_path_artifact_schema_or_enum")
    if expected_vmp_sha256 is not None and value["vmp_sha256"] != expected_vmp_sha256:
        raise _fail("candidate_path_artifact_context_mismatch")
    if (
        expected_provider_manifest_sha256 is not None
        and value["provider_reading_manifest_sha256"]
        != expected_provider_manifest_sha256
    ):
        raise _fail("candidate_path_artifact_context_mismatch")
    text = _validate_text_bound(value["text"], span=False)
    alignment = _decode_alignment(value["alignment"])
    _validate_monotonic_alignment(text, alignment, vmp_length=value["vmp_length"])
    covered_through = 0
    for start, end in alignment:
        if start > covered_through:
            raise _fail("candidate_path_artifact_invalid_alignment")
        covered_through = max(covered_through, end)
    if covered_through != value["vmp_length"]:
        raise _fail("candidate_path_artifact_invalid_alignment")
    _validate_lineage(value["lineage"])
    _validate_artifact_spans(
        value["effective_rewrite_spans"], vmp_length=value["vmp_length"]
    )
    try:
        score = f64_bits_to_float(value["composition_score_f64_bits"])
        numerator = f64_bits_to_float(value["q_numerator_f64_bits"])
        weight = f64_bits_to_float(value["q_f64_bits"])
    except CanonicalError as error:
        raise _fail("candidate_path_artifact_invalid_numeric") from error
    if not math.isfinite(score) or not 0.0 <= numerator <= 1.0 or not 0.0 <= weight <= 1.0:
        raise _fail("candidate_path_artifact_invalid_numeric")
    path_object = {"text": text, "alignment": _alignment_json(alignment)}
    if sha256(canonical_json_bytes(path_object)).hexdigest() != value["path_sha256"]:
        raise _fail("candidate_path_artifact_path_hash_mismatch")
    try:
        canonical_json_bytes(value, max_bytes=CANDIDATE_PATH_ARTIFACT_MAX_BYTES)
    except CanonicalError as error:
        raise _fail("candidate_path_artifact_too_large") from error


def build_candidate_path_artifact(
    path: InternalCandidatePath,
    *,
    vmp_sha256: str,
    provider_manifest_sha256: str,
    vmp_length: int,
) -> dict[str, Any]:
    value = {
        "artifact_version": "1.0.0",
        "path_id": path.path_id,
        "path_sha256": path.path_sha256,
        "vmp_sha256": vmp_sha256,
        "vmp_length": vmp_length,
        "provider_reading_manifest_sha256": provider_manifest_sha256,
        "text": path.text,
        "alignment": _alignment_json(path.alignment),
        "lineage": path.lineage,
        "composition_score_f64_bits": float_to_f64_bits(path.composition_score),
        "q_numerator_f64_bits": float_to_f64_bits(path.q_numerator),
        "q_f64_bits": float_to_f64_bits(path.q),
        "effective_rewrite_spans": [dict(span) for span in path.effective_rewrite_spans],
    }
    validate_candidate_path_artifact(
        value,
        expected_vmp_sha256=vmp_sha256,
        expected_provider_manifest_sha256=provider_manifest_sha256,
    )
    return value


def candidate_path_artifact_bytes(value: object) -> bytes:
    validate_candidate_path_artifact(value)
    try:
        return canonical_json_bytes(value, max_bytes=CANDIDATE_PATH_ARTIFACT_MAX_BYTES)
    except CanonicalError as error:
        raise _fail("candidate_path_artifact_too_large") from error


def candidate_path_artifact_sha256(value: object) -> str:
    return sha256(candidate_path_artifact_bytes(value)).hexdigest()


def parse_candidate_path_artifact(
    raw: bytes,
    *,
    expected_vmp_sha256: str | None = None,
    expected_provider_manifest_sha256: str | None = None,
) -> dict[str, Any]:
    if not isinstance(raw, bytes):
        raise _fail("candidate_path_artifact_invalid_input")
    if len(raw) > CANDIDATE_PATH_ARTIFACT_MAX_BYTES:
        raise _fail("candidate_path_artifact_too_large")
    try:
        value = strict_json_loads(raw, prefix="candidate_path_artifact")
    except CanonicalError as error:
        raise _fail(error.code) from error
    validate_candidate_path_artifact(
        value,
        expected_vmp_sha256=expected_vmp_sha256,
        expected_provider_manifest_sha256=expected_provider_manifest_sha256,
    )
    assert isinstance(value, dict)
    return value


def _provider_manifest_bytes(manifest: dict[str, Any]) -> bytes:
    try:
        return canonical_json_bytes(manifest, max_bytes=PROVIDER_MANIFEST_MAX_BYTES)
    except CanonicalError as error:
        raise _fail("candidate_invalid_provider_manifest") from error


def _canonical_provider_reading(
    reading: object,
    *,
    provider_mode: str,
    expected_start: int,
    expected_end: int,
    vmp_text: str,
    rewrite_spans: Sequence[dict[str, Any]],
    prior_ranks: set[int],
) -> dict[str, Any]:
    if not exact_keys(reading, _READING_FIELDS):
        raise _fail("candidate_invalid_provider_manifest")
    assert isinstance(reading, dict)
    rank = reading["provider_rank"]
    if not _is_int(rank) or not 1 <= rank <= 8 or rank in prior_ranks:
        raise _fail("candidate_invalid_provider_manifest")
    reading_text = _validate_text_bound(
        reading["reading_text"], span=provider_mode == "COMPOSED_SPAN"
    )
    alignment = _decode_alignment(reading["reading_alignment"])
    try:
        f64_bits_to_float(reading["raw_logit_f64_bits"])
    except CanonicalError as error:
        raise _fail("candidate_invalid_provider_manifest") from error
    if provider_mode == "COMPOSED_SPAN":
        _validate_span_alignment(
            reading_text,
            alignment,
            span_start=expected_start,
            span_end=expected_end,
            vmp_length=len(vmp_text),
        )
    else:
        _validate_direct_alignment(
            reading_text,
            alignment,
            vmp_text=vmp_text,
            spans=rewrite_spans,
        )
    return {
        "provider_rank": rank,
        "reading_text": reading_text,
        "reading_alignment": _alignment_json(alignment),
        "raw_logit_f64_bits": reading["raw_logit_f64_bits"],
    }


def build_provider_manifest(
    *,
    vmp_text: str,
    vmp_sha256: str,
    provider_config_id: str,
    provider_mode: str,
    normalizer_id: str,
    rewrite_spans: Sequence[dict[str, Any]],
    units: object,
) -> tuple[dict[str, Any], bytes, str, int]:
    """Validate and canonicalize one configured provider-reading manifest."""

    if (
        not is_sha256(vmp_sha256)
        or not isinstance(provider_config_id, str)
        or _PROVIDER_ID.fullmatch(provider_config_id) is None
        or provider_mode not in _CONFIGURED_MODES
        or not isinstance(normalizer_id, str)
        or _NORMALIZER_ID.fullmatch(normalizer_id) is None
    ):
        raise _fail("candidate_invalid_provider_manifest")
    if not 1 <= len(rewrite_spans) <= MAX_REWRITE_SPANS or type(units) is not list:
        raise _fail("candidate_invalid_provider_manifest")
    previous_end = 0
    for index, span in enumerate(rewrite_spans):
        if not exact_keys(span, _SPAN_FIELDS):
            raise _fail("candidate_invalid_provider_manifest")
        if (
            not _is_int(span["span_index"])
            or not _is_int(span["start"])
            or not _is_int(span["end"])
            or span["span_index"] != index
            or not 0 <= span["start"] < span["end"] <= len(vmp_text)
            or span["start"] < previous_end
            or span["source_text"] != vmp_text[span["start"] : span["end"]]
        ):
            raise _fail("candidate_invalid_provider_manifest")
        previous_end = span["end"]

    canonical_units: list[dict[str, Any]] = []
    provider_count = 0
    if provider_mode == "COMPOSED_SPAN":
        if len(units) != len(rewrite_spans):
            raise _fail("candidate_invalid_provider_manifest")
    elif len(units) != 1:
        raise _fail("candidate_invalid_provider_manifest")

    for unit_index, unit in enumerate(units):
        if not exact_keys(unit, _UNIT_FIELDS):
            raise _fail("candidate_invalid_provider_manifest", safe_count=provider_count)
        readings = unit["readings"]
        if type(readings) is not list or not 1 <= len(readings) <= MAX_READINGS_PER_UNIT:
            raise _fail("candidate_invalid_provider_manifest", safe_count=provider_count)
        if provider_mode == "COMPOSED_SPAN":
            span = rewrite_spans[unit_index]
            expected_kind = "SPAN"
            expected_start = span["start"]
            expected_end = span["end"]
            expected_source = span["source_text"]
        else:
            expected_kind = "FULL_PATH"
            expected_start = 0
            expected_end = len(vmp_text)
            expected_source = vmp_text
        if (
            not _is_int(unit["unit_index"])
            or unit["unit_index"] != unit_index
            or unit["unit_kind"] != expected_kind
            or not _is_int(unit["start"])
            or not _is_int(unit["end"])
            or unit["start"] != expected_start
            or unit["end"] != expected_end
            or unit["source_text"] != expected_source
        ):
            raise _fail("candidate_invalid_provider_manifest", safe_count=provider_count)

        canonical_readings: list[dict[str, Any]] = []
        ranks: set[int] = set()
        for reading in readings:
            try:
                canonical_reading = _canonical_provider_reading(
                    reading,
                    provider_mode=provider_mode,
                    expected_start=expected_start,
                    expected_end=expected_end,
                    vmp_text=vmp_text,
                    rewrite_spans=rewrite_spans,
                    prior_ranks=ranks,
                )
            except CandidateValidationError as error:
                error.safe_count = provider_count
                raise
            ranks.add(canonical_reading["provider_rank"])
            canonical_readings.append(canonical_reading)
            provider_count += 1
        canonical_units.append(
            {
                "unit_index": unit_index,
                "unit_kind": expected_kind,
                "start": expected_start,
                "end": expected_end,
                "source_text": expected_source,
                "readings": canonical_readings,
            }
        )

    manifest = {
        "manifest_version": "1.0.0",
        "vmp_sha256": vmp_sha256,
        "provider_config_id": provider_config_id,
        "provider_mode": provider_mode,
        "normalizer_id": normalizer_id,
        "rewrite_spans": [dict(span) for span in rewrite_spans],
        "units": canonical_units,
    }
    try:
        encoded = _provider_manifest_bytes(manifest)
    except CandidateValidationError as error:
        error.safe_count = provider_count
        raise
    return manifest, encoded, sha256(encoded).hexdigest(), provider_count


def build_identity_manifest(*, vmp_sha256: str) -> tuple[dict[str, Any], bytes, str]:
    if not is_sha256(vmp_sha256):
        raise _fail("candidate_invalid_provider_manifest")
    manifest = {
        "manifest_version": "1.0.0",
        "vmp_sha256": vmp_sha256,
        "provider_config_id": "provider_identity_bypass",
        "provider_mode": "IDENTITY_BYPASS",
        "normalizer_id": "normalizer_identity",
        "rewrite_spans": [],
        "units": [],
    }
    encoded = _provider_manifest_bytes(manifest)
    return manifest, encoded, sha256(encoded).hexdigest()


def _composed_contributor(units: Sequence[tuple[int, tuple[int, ...]]]) -> dict[str, Any]:
    return {
        "mode": "COMPOSED_SPAN",
        "units": [
            {"unit_index": unit_index, "ranks": list(ranks)}
            for unit_index, ranks in units
        ],
    }


def _direct_contributor(ranks: Sequence[int]) -> dict[str, Any]:
    return {"mode": "DIRECT_FULL_PATH", "unit_index": 0, "ranks": list(ranks)}


def _identity_contributor() -> dict[str, Any]:
    return {"mode": "IDENTITY_BYPASS"}


def _safe_logsumexp(values: Iterable[float]) -> float:
    try:
        result = ordered_logsumexp(list(values))
    except CanonicalError as error:
        code = "candidate_nonfinite" if "nonfinite" in error.code else "candidate_invalid_arithmetic"
        raise _fail(code) from error
    if not math.isfinite(result):
        raise _fail("candidate_nonfinite")
    return 0.0 if result == 0.0 else result


def _safe_sum(values: Iterable[float]) -> float:
    try:
        result = sequential_sum(values)
    except CanonicalError as error:
        code = "candidate_nonfinite" if "nonfinite" in error.code else "candidate_invalid_arithmetic"
        raise _fail(code) from error
    if not math.isfinite(result):
        raise _fail("candidate_nonfinite")
    return 0.0 if result == 0.0 else result


def _safe_subtract(left: float, right: float) -> float:
    result = left - right
    if not math.isfinite(result):
        raise _fail("candidate_nonfinite")
    return 0.0 if result == 0.0 else result


def _work_sort_key(value: _WorkCandidate) -> tuple[Any, ...]:
    return (
        -value.score,
        _utf8(value.text),
        _alignment_bytes(value.alignment),
        value.lineage_bytes,
    )


def _merge_work_candidates(values: Sequence[_WorkCandidate]) -> tuple[list[_WorkCandidate], int]:
    groups: dict[tuple[str, tuple[tuple[int, int], ...]], list[_WorkCandidate]] = {}
    for value in values:
        groups.setdefault((value.text, value.alignment), []).append(value)
    merged: list[_WorkCandidate] = []
    reduction = 0
    for group in groups.values():
        reduction += len(group) - 1
        contributions = tuple(
            contribution
            for candidate in group
            for contribution in candidate.contributions
        )
        candidate = _WorkCandidate(group[0].text, group[0].alignment, contributions)
        candidate.score
        merged.append(candidate)
    return merged, reduction


def _span_candidates(unit: dict[str, Any]) -> tuple[list[_SpanCandidate], int]:
    groups: dict[
        tuple[str, tuple[tuple[int, int], ...]],
        list[tuple[int, float]],
    ] = {}
    unit_index = unit["unit_index"]
    for reading in unit["readings"]:
        alignment = tuple(tuple(pair) for pair in reading["reading_alignment"])
        score = f64_bits_to_float(reading["raw_logit_f64_bits"])
        groups.setdefault((reading["reading_text"], alignment), []).append(
            (reading["provider_rank"], score)
        )
    raw_merged: list[_SpanCandidate] = []
    for (text, alignment), rank_scores in groups.items():
        ordered = sorted(
            rank_scores,
            key=lambda item: canonical_json_bytes(
                _composed_contributor(((unit_index, (item[0],)),))
            ),
        )
        raw_merged.append(
            _SpanCandidate(
                text=text,
                alignment=alignment,
                ranks=tuple(sorted(rank for rank, _ in rank_scores)),
                score=_safe_logsumexp([score for _, score in ordered]),
            )
        )
    ordered_merged = sorted(
        raw_merged,
        key=lambda value: canonical_json_bytes(
            _composed_contributor(((unit_index, value.ranks),))
        ),
    )
    denominator = _safe_logsumexp([value.score for value in ordered_merged])
    normalized = [
        _SpanCandidate(
            text=value.text,
            alignment=value.alignment,
            ranks=value.ranks,
            score=_safe_subtract(value.score, denominator),
        )
        for value in raw_merged
    ]
    return normalized, len(unit["readings"]) - len(normalized)


def _append_identity_segment(
    text: str,
    alignment: tuple[tuple[int, int], ...],
    *,
    vmp_text: str,
    start: int,
    end: int,
) -> tuple[str, tuple[tuple[int, int], ...]]:
    return text + vmp_text[start:end], alignment + _identity_alignment(start, end)


def _exact_composed(
    vmp_text: str,
    spans: Sequence[dict[str, Any]],
    candidates_by_span: Sequence[Sequence[_SpanCandidate]],
    work_counter: _CandidateWorkCounter,
) -> tuple[list[_WorkCandidate], int, int]:
    hypotheses: list[_WorkCandidate] = []
    for combination in product(*candidates_by_span):
        work_counter.consume(1)
        text = ""
        alignment: tuple[tuple[int, int], ...] = ()
        cursor = 0
        units: list[tuple[int, tuple[int, ...]]] = []
        scores: list[float] = []
        for span, candidate in zip(spans, combination):
            text, alignment = _append_identity_segment(
                text,
                alignment,
                vmp_text=vmp_text,
                start=cursor,
                end=span["start"],
            )
            text += candidate.text
            alignment += candidate.alignment
            cursor = span["end"]
            units.append((span["span_index"], candidate.ranks))
            scores.append(candidate.score)
        text, alignment = _append_identity_segment(
            text,
            alignment,
            vmp_text=vmp_text,
            start=cursor,
            end=len(vmp_text),
        )
        _validate_text_bound(text, span=False)
        work_counter.consume(len(text))
        score = _safe_sum(scores)
        hypotheses.append(
            _WorkCandidate(
                text,
                alignment,
                (_Contribution(_composed_contributor(units), score),),
            )
        )
    merged, full_reduction = _merge_work_candidates(hypotheses)
    return merged, 0, full_reduction


def _beam_chain(node: _BeamNode) -> list[_BeamNode]:
    chain: list[_BeamNode] = []
    current: _BeamNode | None = node
    while current is not None and current.parent is not None:
        chain.append(current)
        current = current.parent
    chain.reverse()
    return chain


def _compare_byte_chunks(
    left_chunks: Iterable[bytes], right_chunks: Iterable[bytes]
) -> int:
    left_iterator = iter(left_chunks)
    right_iterator = iter(right_chunks)
    left = b""
    right = b""
    left_offset = 0
    right_offset = 0
    left_done = False
    right_done = False
    while True:
        while left_offset == len(left) and not left_done:
            try:
                left = next(left_iterator)
                left_offset = 0
            except StopIteration:
                left_done = True
        while right_offset == len(right) and not right_done:
            try:
                right = next(right_iterator)
                right_offset = 0
            except StopIteration:
                right_done = True
        if left_done or right_done:
            if left_done and right_done:
                return 0
            return -1 if left_done else 1
        count = min(len(left) - left_offset, len(right) - right_offset)
        for index in range(count):
            left_byte = left[left_offset + index]
            right_byte = right[right_offset + index]
            if left_byte != right_byte:
                return -1 if left_byte < right_byte else 1
        left_offset += count
        right_offset += count


def _beam_text_chunks(
    node: _BeamNode,
    *,
    vmp_text: str,
    spans: Sequence[dict[str, Any]],
) -> tuple[bytes, ...]:
    chunks: list[bytes] = []
    cursor = 0
    for current in _beam_chain(node):
        span = spans[current.span_index]
        if cursor < span["start"]:
            chunks.append(_utf8(vmp_text[cursor : span["start"]]))
        assert current.span_candidate is not None
        chunks.append(_utf8(current.span_candidate.text))
        cursor = span["end"]
    return tuple(chunks)


def _beam_alignment_chunks(
    node: _BeamNode,
    *,
    spans: Sequence[dict[str, Any]],
) -> Iterable[bytes]:
    yield b"["
    first = True
    cursor = 0
    for current in _beam_chain(node):
        span = spans[current.span_index]
        for start, end in _identity_alignment(cursor, span["start"]):
            if not first:
                yield b","
            yield f"[{start},{end}]".encode("ascii")
            first = False
        assert current.span_candidate is not None
        for start, end in current.span_candidate.alignment:
            if not first:
                yield b","
            yield f"[{start},{end}]".encode("ascii")
            first = False
        cursor = span["end"]
    yield b"]"


def _beam_comparator(
    *,
    vmp_text: str,
    spans: Sequence[dict[str, Any]],
    work_counter: _CandidateWorkCounter,
):
    text_cache: dict[int, tuple[bytes, ...]] = {}

    def compare(left: _BeamNode, right: _BeamNode) -> int:
        work_counter.consume(1)
        left_score = left.score
        right_score = right.score
        if left_score != right_score:
            return -1 if left_score > right_score else 1
        left_identity = id(left)
        if left_identity not in text_cache:
            text_cache[left_identity] = _beam_text_chunks(
                left, vmp_text=vmp_text, spans=spans
            )
        right_identity = id(right)
        if right_identity not in text_cache:
            text_cache[right_identity] = _beam_text_chunks(
                right, vmp_text=vmp_text, spans=spans
            )
        left_text = text_cache[left_identity]
        right_text = text_cache[right_identity]
        text_order = _compare_byte_chunks(left_text, right_text)
        if text_order:
            return text_order
        alignment_order = _compare_byte_chunks(
            _beam_alignment_chunks(left, spans=spans),
            _beam_alignment_chunks(right, spans=spans),
        )
        if alignment_order:
            return alignment_order
        if left.lineage_bytes == right.lineage_bytes:
            return 0
        return -1 if left.lineage_bytes < right.lineage_bytes else 1

    return compare


def _deterministic_merge_sort(
    values: Sequence[_BeamNode], compare
) -> list[_BeamNode]:
    """Bottom-up stable merge sort with runtime-independent comparison order."""

    result = list(values)
    width = 1
    while width < len(result):
        merged: list[_BeamNode] = []
        for start in range(0, len(result), 2 * width):
            left = result[start : start + width]
            right = result[start + width : start + 2 * width]
            left_index = 0
            right_index = 0
            while left_index < len(left) and right_index < len(right):
                if compare(left[left_index], right[right_index]) <= 0:
                    merged.append(left[left_index])
                    left_index += 1
                else:
                    merged.append(right[right_index])
                    right_index += 1
            merged.extend(left[left_index:])
            merged.extend(right[right_index:])
        result = merged
        width *= 2
    return result


def _materialize_beam_node(
    node: _BeamNode,
    *,
    vmp_text: str,
    spans: Sequence[dict[str, Any]],
    work_counter: _CandidateWorkCounter,
) -> _WorkCandidate:
    text_parts: list[str] = []
    alignment: list[tuple[int, int]] = []
    cursor = 0
    for current in _beam_chain(node):
        span = spans[current.span_index]
        text_parts.append(vmp_text[cursor : span["start"]])
        alignment.extend(_identity_alignment(cursor, span["start"]))
        assert current.span_candidate is not None
        text_parts.append(current.span_candidate.text)
        alignment.extend(current.span_candidate.alignment)
        cursor = span["end"]
    text_parts.append(vmp_text[cursor:])
    alignment.extend(_identity_alignment(cursor, len(vmp_text)))
    text = "".join(text_parts)
    _validate_text_bound(text, span=False)
    work_counter.consume(len(text))
    return _WorkCandidate(text, tuple(alignment), node.contributions)


def _beam_composed(
    vmp_text: str,
    spans: Sequence[dict[str, Any]],
    candidates_by_span: Sequence[Sequence[_SpanCandidate]],
    work_counter: _CandidateWorkCounter,
) -> tuple[list[_WorkCandidate], int, int]:
    root = _BeamNode(
        parent=None,
        span_candidate=None,
        span_index=-1,
        contributions=(_Contribution(_composed_contributor(()), 0.0),),
    )
    partials = [root]
    partial_reduction = 0
    for span, span_candidates in zip(spans, candidates_by_span):
        grouped: dict[
            tuple[int, str, tuple[tuple[int, int], ...]], list[_BeamNode]
        ] = {}
        for partial in partials:
            for span_candidate in span_candidates:
                work_counter.consume(1)
                contributions: list[_Contribution] = []
                for prior in partial.contributions:
                    prior_units = tuple(
                        (value["unit_index"], tuple(value["ranks"]))
                        for value in prior.contributor["units"]
                    )
                    contributor = _composed_contributor(
                        prior_units + ((span["span_index"], span_candidate.ranks),)
                    )
                    contributions.append(
                        _Contribution(
                            contributor,
                            _safe_sum((prior.score, span_candidate.score)),
                        )
                    )
                node = _BeamNode(
                    parent=partial,
                    span_candidate=span_candidate,
                    span_index=span["span_index"],
                    contributions=tuple(contributions),
                )
                grouped.setdefault(
                    (id(partial), span_candidate.text, span_candidate.alignment), []
                ).append(node)
        merged: list[_BeamNode] = []
        for group in grouped.values():
            partial_reduction += len(group) - 1
            merged.append(
                _BeamNode(
                    parent=group[0].parent,
                    span_candidate=group[0].span_candidate,
                    span_index=group[0].span_index,
                    contributions=tuple(
                        contribution
                        for candidate in group
                        for contribution in candidate.contributions
                    ),
                )
            )
        if partial_reduction > 65_535:
            raise _fail("candidate_invalid_arithmetic")
        comparator = _beam_comparator(
            vmp_text=vmp_text,
            spans=spans,
            work_counter=work_counter,
        )
        partials = _deterministic_merge_sort(merged, comparator)[:BEAM_WIDTH]

    completed = [
        _materialize_beam_node(
            partial,
            vmp_text=vmp_text,
            spans=spans,
            work_counter=work_counter,
        )
        for partial in partials
    ]
    merged, full_reduction = _merge_work_candidates(completed)
    return merged, partial_reduction, full_reduction


def _composed_candidates(
    manifest: dict[str, Any],
    *,
    vmp_text: str,
    work_counter: _CandidateWorkCounter,
) -> tuple[list[_WorkCandidate], str, int, int, int]:
    candidates_by_span: list[list[_SpanCandidate]] = []
    span_reduction = 0
    product_bound = 1
    exact = True
    for unit in manifest["units"]:
        span_candidates, reduction = _span_candidates(unit)
        candidates_by_span.append(span_candidates)
        span_reduction += reduction
        if product_bound > BEAM_WIDTH // len(span_candidates):
            exact = False
        if exact:
            product_bound *= len(span_candidates)
    if exact:
        candidates, partial_reduction, full_reduction = _exact_composed(
            vmp_text, manifest["rewrite_spans"], candidates_by_span, work_counter
        )
        return candidates, "EXACT", span_reduction, partial_reduction, full_reduction
    candidates, partial_reduction, full_reduction = _beam_composed(
        vmp_text, manifest["rewrite_spans"], candidates_by_span, work_counter
    )
    return candidates, "BEAM", span_reduction, partial_reduction, full_reduction


def _direct_candidates(
    manifest: dict[str, Any], work_counter: _CandidateWorkCounter
) -> tuple[list[_WorkCandidate], int]:
    unit = manifest["units"][0]
    groups: dict[
        tuple[str, tuple[tuple[int, int], ...]],
        list[tuple[int, float]],
    ] = {}
    for reading in unit["readings"]:
        alignment = tuple(tuple(pair) for pair in reading["reading_alignment"])
        groups.setdefault((reading["reading_text"], alignment), []).append(
            (
                reading["provider_rank"],
                f64_bits_to_float(reading["raw_logit_f64_bits"]),
            )
        )
    raw_candidates: list[_WorkCandidate] = []
    for (text, alignment), rank_scores in groups.items():
        work_counter.consume(1 + len(text))
        ranks = tuple(sorted(rank for rank, _ in rank_scores))
        ordered = sorted(rank_scores, key=lambda value: canonical_json_bytes(_direct_contributor((value[0],))))
        score = _safe_logsumexp([value for _, value in ordered])
        raw_candidates.append(
            _WorkCandidate(
                text,
                alignment,
                (_Contribution(_direct_contributor(ranks), score),),
            )
        )
    ordered_candidates = sorted(raw_candidates, key=lambda value: value.lineage_bytes)
    denominator = _safe_logsumexp([value.score for value in ordered_candidates])
    normalized = [
        _WorkCandidate(
            value.text,
            value.alignment,
            tuple(
                _Contribution(
                    contribution.contributor,
                    _safe_subtract(contribution.score, denominator),
                )
                for contribution in value.contributions
            ),
        )
        for value in raw_candidates
    ]
    return normalized, len(unit["readings"]) - len(normalized)


def _make_paths_and_diagnostics(
    *,
    mode: str,
    search_mode: str,
    work_candidates: Sequence[_WorkCandidate],
    temperature: float,
    effective_spans: Sequence[dict[str, Any]],
    input_count: int,
    span_reduction: int,
    partial_reduction: int,
    full_reduction: int,
) -> tuple[dict[str, Any], tuple[InternalCandidatePath, ...]]:
    if not work_candidates or len(work_candidates) > BEAM_WIDTH:
        raise _fail("candidate_invalid_arithmetic")
    for reduction in (span_reduction, partial_reduction, full_reduction):
        if not 0 <= reduction <= 65_535:
            raise _fail("candidate_invalid_arithmetic")
    pre_k = sorted(work_candidates, key=_work_sort_key)
    returned = pre_k[:RETURNED_PATH_LIMIT]
    pre_lse_order = sorted(pre_k, key=lambda value: value.lineage_bytes)
    returned_lse_order = sorted(returned, key=lambda value: value.lineage_bytes)
    l_pre_k = _safe_logsumexp([value.score for value in pre_lse_order])
    l_returned = _safe_logsumexp([value.score for value in returned_lse_order])
    delta = _safe_subtract(l_returned, l_pre_k)
    if delta > 0.0:
        raise _fail("candidate_invalid_arithmetic")
    mass = math.exp(delta)
    if not math.isfinite(mass):
        raise _fail("candidate_nonfinite")

    lineage_order = sorted(range(len(returned)), key=lambda index: returned[index].lineage_bytes)
    try:
        numerators, q_normalizer, q_max, weights = ordered_softmax(
            [value.score for value in returned],
            temperature,
            accumulation_order=lineage_order,
        )
    except CanonicalError as error:
        code = "candidate_nonfinite" if "nonfinite" in error.code else "candidate_invalid_arithmetic"
        raise _fail(code) from error

    paths: list[InternalCandidatePath] = []
    spans = tuple(dict(span) for span in effective_spans)
    for index, (candidate, numerator, weight) in enumerate(
        zip(returned, numerators, weights), start=1
    ):
        path_object = {
            "text": candidate.text,
            "alignment": _alignment_json(candidate.alignment),
        }
        try:
            path_hash = sha256(canonical_json_bytes(path_object)).hexdigest()
        except CanonicalError as error:
            raise _fail("candidate_invalid_alignment") from error
        paths.append(
            InternalCandidatePath(
                path_id=f"candidate_path_{index:02d}",
                path_sha256=path_hash,
                text=candidate.text,
                alignment=candidate.alignment,
                lineage=candidate.lineage,
                composition_score=candidate.score,
                q_numerator=numerator,
                q=weight,
                effective_rewrite_spans=spans,
            )
        )

    total_reduction = span_reduction + partial_reduction + full_reduction
    if total_reduction > 65_535:
        raise _fail("candidate_invalid_arithmetic")
    diagnostics = {
        "mode": mode,
        "temperature_f64_bits": float_to_f64_bits(temperature),
        "search_mode": search_mode,
        "input_count": input_count,
        "span_merge_reduction_count": span_reduction,
        "partial_merge_reduction_count": partial_reduction,
        "full_merge_reduction_count": full_reduction,
        "total_merge_reduction_count": total_reduction,
        "postmerge_count": len(pre_k),
        "returned_count": len(paths),
        "preK_scope": "FINAL_BEAM" if search_mode == "BEAM" else "EXACT_FULL",
        "L_returned_f64_bits": float_to_f64_bits(l_returned),
        "L_preK_f64_bits": float_to_f64_bits(l_pre_k),
        "retained_preK_composition_mass_f64_bits": float_to_f64_bits(mass),
        "q_normalizer_f64_bits": float_to_f64_bits(q_normalizer),
        "q_max_f64_bits": float_to_f64_bits(q_max),
    }
    return diagnostics, tuple(paths)


def build_candidates_from_manifest(
    manifest: dict[str, Any],
    *,
    vmp_text: str,
    temperature: float,
    _work_counter: _CandidateWorkCounter | None = None,
) -> tuple[dict[str, Any], tuple[InternalCandidatePath, ...], int]:
    """Construct bounded candidates from an already accepted canonical manifest."""

    work_counter = _work_counter or _CandidateWorkCounter()
    mode = manifest["provider_mode"]
    if mode == "IDENTITY_BYPASS":
        _validate_text_bound(vmp_text, span=False)
        work_counter.consume(1 + len(vmp_text))
        alignment = _identity_alignment(0, len(vmp_text))
        candidate = _WorkCandidate(
            vmp_text,
            alignment,
            (_Contribution(_identity_contributor(), 0.0),),
        )
        diagnostics, paths = _make_paths_and_diagnostics(
            mode=mode,
            search_mode=mode,
            work_candidates=[candidate],
            temperature=temperature,
            effective_spans=(),
            input_count=1,
            span_reduction=0,
            partial_reduction=0,
            full_reduction=0,
        )
        return diagnostics, paths, 0
    if mode == "COMPOSED_SPAN":
        candidates, search_mode, span_reduction, partial_reduction, full_reduction = _composed_candidates(
            manifest, vmp_text=vmp_text, work_counter=work_counter
        )
    elif mode == "DIRECT_FULL_PATH":
        candidates, full_reduction = _direct_candidates(manifest, work_counter)
        search_mode = "DIRECT_FULL_PATH"
        span_reduction = 0
        partial_reduction = 0
    else:
        raise _fail("candidate_invalid_provider_manifest")
    diagnostics, paths = _make_paths_and_diagnostics(
        mode=mode,
        search_mode=search_mode,
        work_candidates=candidates,
        temperature=temperature,
        effective_spans=manifest["rewrite_spans"],
        input_count=sum(len(unit["readings"]) for unit in manifest["units"]),
        span_reduction=span_reduction,
        partial_reduction=partial_reduction,
        full_reduction=full_reduction,
    )
    normalizer_count = sum(len(unit["readings"]) for unit in manifest["units"])
    return diagnostics, paths, normalizer_count


def _execution(
    *,
    configured_mode: str,
    provider_config_id: str,
    provider_config_sha256: str,
    normalizer_id: str,
    normalizer_sha256: str,
    eligible_spans: Sequence[dict[str, Any]],
    invocation_attempted: bool,
    outcome: str,
    output_accepted: bool,
    bypass_reason: str,
    failure_code: str,
    provider_manifest_sha256: str | None,
) -> dict[str, Any]:
    return {
        "configured_mode": configured_mode,
        "provider_config_id": provider_config_id,
        "provider_config_sha256": provider_config_sha256,
        "normalizer_id": normalizer_id,
        "normalizer_sha256": normalizer_sha256,
        "eligible_spans": [dict(span) for span in eligible_spans],
        "invocation_attempted": invocation_attempted,
        "outcome": outcome,
        "output_accepted": output_accepted,
        "bypass_reason": bypass_reason,
        "failure_code": failure_code,
        "provider_manifest_sha256": provider_manifest_sha256,
    }


def _validate_execution_spans(value: object) -> None:
    if type(value) is not list or len(value) > MAX_REWRITE_SPANS:
        raise _fail("candidate_provider_execution_invalid")
    previous_end = 0
    for index, span in enumerate(value):
        if not exact_keys(span, _SPAN_FIELDS):
            raise _fail("candidate_provider_execution_invalid")
        assert isinstance(span, dict)
        start = span["start"]
        end = span["end"]
        if (
            not _is_int(span["span_index"])
            or span["span_index"] != index
            or not _is_int(start)
            or not _is_int(end)
            or not 0 <= start < end
            or start < previous_end
            or not isinstance(span["source_text"], str)
            or len(span["source_text"]) != end - start
        ):
            raise _fail("candidate_provider_execution_invalid")
        previous_end = end


def validate_provider_execution(value: object) -> None:
    if not exact_keys(value, _PROVIDER_EXECUTION_FIELDS):
        raise _fail("candidate_provider_execution_invalid")
    assert isinstance(value, dict)
    if (
        value["configured_mode"] not in _CONFIGURED_MODES
        or not isinstance(value["provider_config_id"], str)
        or _PROVIDER_ID.fullmatch(value["provider_config_id"]) is None
        or not is_sha256(value["provider_config_sha256"])
        or not isinstance(value["normalizer_id"], str)
        or _NORMALIZER_ID.fullmatch(value["normalizer_id"]) is None
        or not is_sha256(value["normalizer_sha256"])
        or type(value["invocation_attempted"]) is not bool
        or type(value["output_accepted"]) is not bool
    ):
        raise _fail("candidate_provider_execution_invalid")
    _validate_execution_spans(value["eligible_spans"])
    outcome = value["outcome"]
    simple = {
        "NOT_INVOKED": (False, False, "NONE", "PROVIDER_NOT_INVOKED", False, True),
        "ELIGIBILITY_INVALID": (False, False, "NONE", "ELIGIBILITY_INVALID", False, False),
        "NO_ELIGIBLE": (False, True, "NO_ELIGIBLE_ROMANIZED_SPAN", "NONE", True, False),
        "SUCCEEDED": (True, True, "NONE", "NONE", True, True),
        "PROVIDER_INVALID_OUTPUT": (True, False, "NONE", "PROVIDER_INVALID_OUTPUT", False, True),
        "NORMALIZER_INVALID_OUTPUT": (True, False, "NONE", "NORMALIZER_INVALID_OUTPUT", False, True),
    }
    spans = value["eligible_spans"]
    if outcome in simple:
        attempted, accepted, bypass, failure, has_hash, requires_spans = simple[outcome]
        if (
            value["invocation_attempted"] is not attempted
            or value["output_accepted"] is not accepted
            or value["bypass_reason"] != bypass
            or value["failure_code"] != failure
            or is_sha256(value["provider_manifest_sha256"]) is not has_hash
            or bool(spans) is not requires_spans
        ):
            raise _fail("candidate_provider_execution_invalid")
    elif outcome in {"UNAVAILABLE_FALLBACK", "TIMEOUT_FALLBACK"}:
        allowed = _UNAVAILABLE_CODES if outcome == "UNAVAILABLE_FALLBACK" else _TIMEOUT_CODES
        if (
            not spans
            or value["invocation_attempted"] is not True
            or value["output_accepted"] is not True
            or value["bypass_reason"] != "PROVIDER_FAILURE_RAW_FALLBACK"
            or value["failure_code"] not in allowed
            or not is_sha256(value["provider_manifest_sha256"])
        ):
            raise _fail("candidate_provider_execution_invalid")
    else:
        raise _fail("candidate_provider_execution_invalid")


def _provider_execution_bytes(value: object) -> bytes:
    validate_provider_execution(value)
    try:
        return canonical_json_bytes(value, max_bytes=PROVIDER_EXECUTION_MAX_BYTES)
    except CanonicalError as error:
        raise _fail("candidate_provider_execution_too_large") from error


def provider_execution_bytes(value: object) -> bytes:
    return _provider_execution_bytes(value)


def parse_provider_execution(raw: bytes) -> dict[str, Any]:
    if not isinstance(raw, bytes):
        raise _fail("candidate_provider_execution_invalid_input")
    if len(raw) > PROVIDER_EXECUTION_MAX_BYTES:
        raise _fail("candidate_provider_execution_too_large")
    try:
        value = strict_json_loads(raw, prefix="candidate_provider_execution")
    except CanonicalError as error:
        raise _fail(error.code) from error
    validate_provider_execution(value)
    assert isinstance(value, dict)
    return value


def validate_candidate_diagnostics(value: object) -> None:
    if not exact_keys(value, _CANDIDATE_DIAGNOSTIC_FIELDS):
        raise _fail("candidate_diagnostics_invalid")
    assert isinstance(value, dict)
    allowed_pairs = {
        ("COMPOSED_SPAN", "EXACT"),
        ("COMPOSED_SPAN", "BEAM"),
        ("DIRECT_FULL_PATH", "DIRECT_FULL_PATH"),
        ("IDENTITY_BYPASS", "IDENTITY_BYPASS"),
    }
    if (value["mode"], value["search_mode"]) not in allowed_pairs:
        raise _fail("candidate_diagnostics_invalid")
    try:
        temperature = f64_bits_to_float(value["temperature_f64_bits"])
        l_returned = f64_bits_to_float(value["L_returned_f64_bits"])
        l_pre_k = f64_bits_to_float(value["L_preK_f64_bits"])
        mass = f64_bits_to_float(value["retained_preK_composition_mass_f64_bits"])
        q_normalizer = f64_bits_to_float(value["q_normalizer_f64_bits"])
        f64_bits_to_float(value["q_max_f64_bits"])
    except CanonicalError as error:
        raise _fail("candidate_diagnostics_invalid_numeric") from error
    count_fields = (
        "input_count",
        "span_merge_reduction_count",
        "partial_merge_reduction_count",
        "full_merge_reduction_count",
        "total_merge_reduction_count",
        "postmerge_count",
        "returned_count",
    )
    if (
        temperature <= 0.0
        or not all(is_nonboolean_int(value[field], minimum=0, maximum=65_535) for field in count_fields)
        or not 1 <= value["input_count"] <= 512
        or not 1 <= value["postmerge_count"] <= 64
        or not 1 <= value["returned_count"] <= min(8, value["postmerge_count"])
        or value["total_merge_reduction_count"]
        != value["span_merge_reduction_count"]
        + value["partial_merge_reduction_count"]
        + value["full_merge_reduction_count"]
        or value["preK_scope"] not in {"EXACT_FULL", "FINAL_BEAM"}
        or (value["search_mode"] == "BEAM") is not (value["preK_scope"] == "FINAL_BEAM")
        or l_returned > l_pre_k
        or not 0.0 <= mass <= 1.0
        or q_normalizer <= 0.0
    ):
        raise _fail("candidate_diagnostics_invalid")


def _candidate_diagnostics_bytes(value: object) -> bytes:
    validate_candidate_diagnostics(value)
    try:
        return canonical_json_bytes(value, max_bytes=CANDIDATE_DIAGNOSTICS_MAX_BYTES)
    except CanonicalError as error:
        raise _fail("candidate_diagnostics_too_large") from error


def candidate_diagnostics_bytes(value: object) -> bytes:
    return _candidate_diagnostics_bytes(value)


def parse_candidate_diagnostics(raw: bytes) -> dict[str, Any]:
    if not isinstance(raw, bytes):
        raise _fail("candidate_diagnostics_invalid_input")
    if len(raw) > CANDIDATE_DIAGNOSTICS_MAX_BYTES:
        raise _fail("candidate_diagnostics_too_large")
    try:
        value = strict_json_loads(raw, prefix="candidate_diagnostics")
    except CanonicalError as error:
        raise _fail(error.code) from error
    validate_candidate_diagnostics(value)
    assert isinstance(value, dict)
    return value


def _parse_provider_manifest_for_replay(
    raw: bytes,
    *,
    vmp_text: str,
    vmp_sha256: str,
    visible_artifacts: object,
    execution: dict[str, Any],
) -> tuple[dict[str, Any], str]:
    if not isinstance(raw, bytes):
        raise _fail("candidate_provider_manifest_invalid_input")
    if len(raw) > PROVIDER_MANIFEST_MAX_BYTES:
        raise _fail("candidate_provider_manifest_too_large")
    try:
        value = strict_json_loads(raw, prefix="candidate_provider_manifest")
    except CanonicalError as error:
        raise _fail(error.code) from error
    if not isinstance(value, dict):
        raise _fail("candidate_provider_manifest_invalid")
    manifest_hash = sha256(raw).hexdigest()
    if manifest_hash != execution["provider_manifest_sha256"]:
        raise _fail("candidate_provider_manifest_hash_mismatch")
    if value.get("provider_mode") == "IDENTITY_BYPASS":
        expected, expected_raw, expected_hash = build_identity_manifest(
            vmp_sha256=vmp_sha256
        )
        if value != expected or raw != expected_raw or manifest_hash != expected_hash:
            raise _fail("candidate_provider_manifest_invalid")
        if execution["outcome"] not in {
            "NO_ELIGIBLE",
            "UNAVAILABLE_FALLBACK",
            "TIMEOUT_FALLBACK",
        }:
            raise _fail("candidate_provider_manifest_context_mismatch")
        return expected, expected_hash

    spans = validate_rewrite_spans(
        value.get("rewrite_spans"),
        vmp_text=vmp_text,
        visible_artifacts=visible_artifacts,
    )
    try:
        rebuilt, rebuilt_raw, rebuilt_hash, _ = build_provider_manifest(
            vmp_text=vmp_text,
            vmp_sha256=vmp_sha256,
            provider_config_id=value.get("provider_config_id"),
            provider_mode=value.get("provider_mode"),
            normalizer_id=value.get("normalizer_id"),
            rewrite_spans=spans,
            units=value.get("units"),
        )
    except CandidateValidationError as error:
        raise _fail("candidate_provider_manifest_invalid") from error
    if (
        rebuilt != value
        or rebuilt_raw != raw
        or rebuilt_hash != manifest_hash
        or execution["outcome"] != "SUCCEEDED"
        or execution["configured_mode"] != value["provider_mode"]
        or execution["provider_config_id"] != value["provider_config_id"]
        or execution["normalizer_id"] != value["normalizer_id"]
        or execution["eligible_spans"] != value["rewrite_spans"]
    ):
        raise _fail("candidate_provider_manifest_context_mismatch")
    return rebuilt, rebuilt_hash


def replay_candidate_run(
    *,
    vmp_text: str,
    vmp_sha256: str,
    visible_artifacts: object,
    provider_manifest_bytes: bytes,
    provider_execution_bytes: bytes,
    candidate_diagnostics_bytes: bytes,
    candidate_path_artifact_bytes: Sequence[bytes],
) -> CandidateReplayResult:
    """Recompute authoritative candidates from exact canonical persisted bytes."""

    if not isinstance(vmp_text, str) or not is_sha256(vmp_sha256):
        raise _fail("candidate_replay_invalid_vmp")
    execution = parse_provider_execution(provider_execution_bytes)
    if execution["eligible_spans"]:
        validated_spans = validate_rewrite_spans(
            execution["eligible_spans"],
            vmp_text=vmp_text,
            visible_artifacts=visible_artifacts,
        )
        if list(validated_spans) != execution["eligible_spans"]:
            raise _fail("candidate_replay_execution_mismatch")
    else:
        _artifact_ranges(visible_artifacts, len(vmp_text))
    manifest, manifest_hash = _parse_provider_manifest_for_replay(
        provider_manifest_bytes,
        vmp_text=vmp_text,
        vmp_sha256=vmp_sha256,
        visible_artifacts=visible_artifacts,
        execution=execution,
    )
    persisted_diagnostics = parse_candidate_diagnostics(candidate_diagnostics_bytes)
    temperature = f64_bits_to_float(persisted_diagnostics["temperature_f64_bits"])
    work_counter = _CandidateWorkCounter()
    recomputed_diagnostics, paths, _ = build_candidates_from_manifest(
        manifest,
        vmp_text=vmp_text,
        temperature=temperature,
        _work_counter=work_counter,
    )
    validate_candidate_diagnostics(recomputed_diagnostics)
    recomputed_diagnostic_bytes = canonical_json_bytes(
        recomputed_diagnostics, max_bytes=CANDIDATE_DIAGNOSTICS_MAX_BYTES
    )
    if candidate_diagnostics_bytes != recomputed_diagnostic_bytes:
        raise _fail("candidate_replay_diagnostics_mismatch")
    if type(candidate_path_artifact_bytes) not in {list, tuple} or len(
        candidate_path_artifact_bytes
    ) != len(paths):
        raise _fail("candidate_replay_path_count_mismatch")
    parsed_artifacts: list[dict[str, Any]] = []
    exact_artifact_bytes: list[bytes] = []
    hashes: list[str] = []
    for path, raw in zip(paths, candidate_path_artifact_bytes):
        parsed = parse_candidate_path_artifact(
            raw,
            expected_vmp_sha256=vmp_sha256,
            expected_provider_manifest_sha256=manifest_hash,
        )
        expected = build_candidate_path_artifact(
            path,
            vmp_sha256=vmp_sha256,
            provider_manifest_sha256=manifest_hash,
            vmp_length=len(vmp_text),
        )
        expected_raw = canonical_json_bytes(
            expected, max_bytes=CANDIDATE_PATH_ARTIFACT_MAX_BYTES
        )
        if parsed != expected or raw != expected_raw:
            raise _fail("candidate_replay_path_mismatch")
        parsed_artifacts.append(parsed)
        exact_artifact_bytes.append(raw)
        hashes.append(sha256(raw).hexdigest())
    return CandidateReplayResult(
        provider_execution=execution,
        provider_manifest=manifest,
        provider_manifest_sha256=manifest_hash,
        candidate_diagnostics=recomputed_diagnostics,
        internal_paths=paths,
        candidate_path_artifacts=tuple(parsed_artifacts),
        candidate_path_artifact_bytes=tuple(exact_artifact_bytes),
        candidate_path_artifact_sha256s=tuple(hashes),
        work_units=work_counter.used,
    )


def _empty_run(
    *,
    execution: dict[str, Any],
    status: str,
    failure_stage: str,
    invalid_code: str,
    configured_count: int,
    eligible_count: int,
    provider_count: int = 0,
) -> CandidateRun:
    return CandidateRun(
        provider_execution=execution,
        provider_manifest=None,
        provider_manifest_bytes=None,
        provider_manifest_sha256=None,
        candidate_diagnostics=None,
        internal_paths=(),
        execution_status=status,
        failure_stage=failure_stage,
        invalid_codes=(invalid_code,) if invalid_code else (),
        configured_span_entries_capped=configured_count,
        eligible_spans_capped=eligible_count,
        provider_count=provider_count,
        normalizer_count=0,
        candidate_count=0,
        alignment_count=0,
    )


def _validate_static_configuration(
    configured_mode: object,
    provider_config_id: object,
    provider_config_sha256: object,
    normalizer_id: object,
    normalizer_sha256: object,
    vmp_sha256: object,
) -> None:
    if (
        configured_mode not in _CONFIGURED_MODES
        or not isinstance(provider_config_id, str)
        or _PROVIDER_ID.fullmatch(provider_config_id) is None
        or not is_sha256(provider_config_sha256)
        or not isinstance(normalizer_id, str)
        or _NORMALIZER_ID.fullmatch(normalizer_id) is None
        or not is_sha256(normalizer_sha256)
        or not is_sha256(vmp_sha256)
    ):
        raise _fail("candidate_invalid_configuration")


def run_candidate_provider(
    *,
    vmp_text: str,
    vmp_sha256: str,
    visible_artifacts: object,
    configured_mode: str,
    provider_config_id: str,
    provider_config_sha256: str,
    normalizer_id: str,
    normalizer_sha256: str,
    selector_output: object,
    provider_units: object = None,
    dispatch_outcome: str = "SUCCEEDED",
    failure_code: str = "NONE",
    temperature: float = 1.0,
) -> CandidateRun:
    """Run the complete synthetic provider/candidate state machine.

    Static bindings and the VMP are assumed to have passed engine preflight;
    they are nevertheless checked to avoid constructing an unsafe record.
    """

    _validate_static_configuration(
        configured_mode,
        provider_config_id,
        provider_config_sha256,
        normalizer_id,
        normalizer_sha256,
        vmp_sha256,
    )
    if not isinstance(vmp_text, str):
        raise _fail("candidate_invalid_vmp")
    configured_count = min(len(selector_output), 65) if type(selector_output) is list else 0
    static_execution_bindings = {
        "configured_mode": configured_mode,
        "provider_config_id": provider_config_id,
        "provider_config_sha256": provider_config_sha256,
        "normalizer_id": normalizer_id,
        "normalizer_sha256": normalizer_sha256,
    }
    try:
        spans = validate_rewrite_spans(
            selector_output,
            vmp_text=vmp_text,
            visible_artifacts=visible_artifacts,
        )
    except CandidateValidationError:
        execution = _execution(
            **static_execution_bindings,
            eligible_spans=(),
            invocation_attempted=False,
            outcome="ELIGIBILITY_INVALID",
            output_accepted=False,
            bypass_reason="NONE",
            failure_code="ELIGIBILITY_INVALID",
            provider_manifest_sha256=None,
        )
        return _empty_run(
            execution=execution,
            status="INVALID",
            failure_stage="PROVIDER_EXECUTION",
            invalid_code="engine_invalid_eligibility",
            configured_count=configured_count,
            eligible_count=0,
        )

    if not spans:
        manifest, encoded, manifest_hash = build_identity_manifest(vmp_sha256=vmp_sha256)
        execution = _execution(
            **static_execution_bindings,
            eligible_spans=(),
            invocation_attempted=False,
            outcome="NO_ELIGIBLE",
            output_accepted=True,
            bypass_reason="NO_ELIGIBLE_ROMANIZED_SPAN",
            failure_code="NONE",
            provider_manifest_sha256=manifest_hash,
        )
        return _accepted_run(
            execution=execution,
            manifest=manifest,
            encoded=encoded,
            manifest_hash=manifest_hash,
            vmp_text=vmp_text,
            temperature=temperature,
            status="VALID",
            failure_stage="NONE",
            configured_count=configured_count,
            eligible_count=0,
            provider_count=0,
        )

    if dispatch_outcome not in _DISPATCH_OUTCOMES:
        raise _fail("candidate_invalid_dispatch_outcome")
    if dispatch_outcome == "NOT_INVOKED":
        if failure_code != "PROVIDER_NOT_INVOKED":
            raise _fail("candidate_invalid_dispatch_outcome")
        execution = _execution(
            **static_execution_bindings,
            eligible_spans=spans,
            invocation_attempted=False,
            outcome=dispatch_outcome,
            output_accepted=False,
            bypass_reason="NONE",
            failure_code=failure_code,
            provider_manifest_sha256=None,
        )
        return _empty_run(
            execution=execution,
            status="INVALID",
            failure_stage="PROVIDER_EXECUTION",
            invalid_code="engine_provider_not_invoked",
            configured_count=configured_count,
            eligible_count=len(spans),
        )
    if dispatch_outcome in {"PROVIDER_INVALID_OUTPUT", "NORMALIZER_INVALID_OUTPUT"}:
        if failure_code != dispatch_outcome:
            raise _fail("candidate_invalid_dispatch_outcome")
        execution = _execution(
            **static_execution_bindings,
            eligible_spans=spans,
            invocation_attempted=True,
            outcome=dispatch_outcome,
            output_accepted=False,
            bypass_reason="NONE",
            failure_code=failure_code,
            provider_manifest_sha256=None,
        )
        invalid = (
            "engine_provider_invalid_output"
            if dispatch_outcome == "PROVIDER_INVALID_OUTPUT"
            else "engine_normalizer_invalid_output"
        )
        return _empty_run(
            execution=execution,
            status="INVALID",
            failure_stage="PROVIDER_EXECUTION",
            invalid_code=invalid,
            configured_count=configured_count,
            eligible_count=len(spans),
        )
    if dispatch_outcome in {"UNAVAILABLE_FALLBACK", "TIMEOUT_FALLBACK"}:
        allowed = _UNAVAILABLE_CODES if dispatch_outcome == "UNAVAILABLE_FALLBACK" else _TIMEOUT_CODES
        if failure_code not in allowed:
            raise _fail("candidate_invalid_dispatch_outcome")
        manifest, encoded, manifest_hash = build_identity_manifest(vmp_sha256=vmp_sha256)
        execution = _execution(
            **static_execution_bindings,
            eligible_spans=spans,
            invocation_attempted=True,
            outcome=dispatch_outcome,
            output_accepted=True,
            bypass_reason="PROVIDER_FAILURE_RAW_FALLBACK",
            failure_code=failure_code,
            provider_manifest_sha256=manifest_hash,
        )
        return _accepted_run(
            execution=execution,
            manifest=manifest,
            encoded=encoded,
            manifest_hash=manifest_hash,
            vmp_text=vmp_text,
            temperature=temperature,
            status="DEGRADED_STOP_AFTER_IDENTITY",
            failure_stage="PROVIDER_EXECUTION",
            configured_count=configured_count,
            eligible_count=len(spans),
            provider_count=0,
        )

    if failure_code != "NONE":
        raise _fail("candidate_invalid_dispatch_outcome")
    try:
        manifest, encoded, manifest_hash, provider_count = build_provider_manifest(
            vmp_text=vmp_text,
            vmp_sha256=vmp_sha256,
            provider_config_id=provider_config_id,
            provider_mode=configured_mode,
            normalizer_id=normalizer_id,
            rewrite_spans=spans,
            units=provider_units,
        )
    except CandidateValidationError as error:
        execution = _execution(
            **static_execution_bindings,
            eligible_spans=spans,
            invocation_attempted=True,
            outcome="PROVIDER_INVALID_OUTPUT",
            output_accepted=False,
            bypass_reason="NONE",
            failure_code="PROVIDER_INVALID_OUTPUT",
            provider_manifest_sha256=None,
        )
        return _empty_run(
            execution=execution,
            status="INVALID",
            failure_stage="PROVIDER_EXECUTION",
            invalid_code="engine_provider_invalid_output",
            configured_count=configured_count,
            eligible_count=len(spans),
            provider_count=error.safe_count,
        )
    execution = _execution(
        **static_execution_bindings,
        eligible_spans=spans,
        invocation_attempted=True,
        outcome="SUCCEEDED",
        output_accepted=True,
        bypass_reason="NONE",
        failure_code="NONE",
        provider_manifest_sha256=manifest_hash,
    )
    return _accepted_run(
        execution=execution,
        manifest=manifest,
        encoded=encoded,
        manifest_hash=manifest_hash,
        vmp_text=vmp_text,
        temperature=temperature,
        status="VALID",
        failure_stage="NONE",
        configured_count=configured_count,
        eligible_count=len(spans),
        provider_count=provider_count,
    )


def _accepted_run(
    *,
    execution: dict[str, Any],
    manifest: dict[str, Any],
    encoded: bytes,
    manifest_hash: str,
    vmp_text: str,
    temperature: float,
    status: str,
    failure_stage: str,
    configured_count: int,
    eligible_count: int,
    provider_count: int,
) -> CandidateRun:
    work_counter = _CandidateWorkCounter()
    try:
        diagnostics, paths, normalizer_count = build_candidates_from_manifest(
            manifest,
            vmp_text=vmp_text,
            temperature=temperature,
            _work_counter=work_counter,
        )
    except CandidateValidationError as error:
        invalid = (
            "engine_candidate_nonfinite"
            if error.code == "candidate_nonfinite"
            else "engine_candidate_invalid_alignment"
            if error.code == "candidate_invalid_alignment"
            else "engine_candidate_invalid_arithmetic"
        )
        return CandidateRun(
            provider_execution=execution,
            provider_manifest=manifest,
            provider_manifest_bytes=encoded,
            provider_manifest_sha256=manifest_hash,
            candidate_diagnostics=None,
            internal_paths=(),
            execution_status="INVALID",
            failure_stage="CANDIDATE",
            invalid_codes=(invalid,),
            configured_span_entries_capped=configured_count,
            eligible_spans_capped=eligible_count,
            provider_count=provider_count,
            normalizer_count=0,
            candidate_count=0,
            alignment_count=0,
            vmp_sha256=manifest["vmp_sha256"],
            vmp_length=len(vmp_text),
            work_units=work_counter.used,
        )
    return CandidateRun(
        provider_execution=execution,
        provider_manifest=manifest,
        provider_manifest_bytes=encoded,
        provider_manifest_sha256=manifest_hash,
        candidate_diagnostics=diagnostics,
        internal_paths=paths,
        execution_status=status,
        failure_stage=failure_stage,
        invalid_codes=(),
        configured_span_entries_capped=configured_count,
        eligible_spans_capped=eligible_count,
        provider_count=provider_count,
        normalizer_count=normalizer_count,
        candidate_count=len(paths),
        alignment_count=sum(len(path.alignment) for path in paths),
        vmp_sha256=manifest["vmp_sha256"],
        vmp_length=len(vmp_text),
        work_units=work_counter.used,
    )


__all__ = [
    "BEAM_WIDTH",
    "CANDIDATE_PATH_ARTIFACT_FIELDS",
    "CANDIDATE_PATH_ARTIFACT_MAX_BYTES",
    "CANDIDATE_WORK_BUDGET",
    "CandidateReplayResult",
    "CandidateRun",
    "CandidateValidationError",
    "InternalCandidatePath",
    "RETURNED_PATH_LIMIT",
    "build_candidate_path_artifact",
    "build_candidates_from_manifest",
    "build_identity_manifest",
    "build_provider_manifest",
    "candidate_diagnostics_bytes",
    "candidate_path_artifact_bytes",
    "candidate_path_artifact_sha256",
    "parse_candidate_diagnostics",
    "parse_candidate_path_artifact",
    "parse_provider_execution",
    "provider_execution_bytes",
    "replay_candidate_run",
    "run_candidate_provider",
    "validate_candidate_diagnostics",
    "validate_candidate_path_artifact",
    "validate_provider_execution",
    "validate_rewrite_spans",
]
