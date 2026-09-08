"""Strict synthetic E0 semantic artifacts for Fisher.

The module deliberately keeps model scores and literal audit material outside
the learned feature rows.  It accepts already validated candidate paths,
constructs the canonical prediction audit, resolves the bounded actor by
destination Cartesian product against an in-memory offline fixture, and emits
the structural plan and exact E0 numeric tensor.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
import re
import unicodedata
from types import MappingProxyType
from typing import Any, Mapping, Sequence

from ._canonical import (
    CanonicalError,
    canonical_json_bytes,
    canonical_sha256,
    exact_keys,
    is_nonboolean_int,
    strict_json_loads,
)
from ._numeric import (
    f64_bits_to_float,
    float_to_f64_bits,
    sequential_mean,
    sequential_sum,
)


PREDICTION_AUDIT_VERSION = "1.0.0"
PAIR_PACKET_VERSION = "1.0.0"
FEATURE_VERSION = "1.0.0"
FEATURE_TENSOR_VERSION = "1.0.0"
E0_FEATURE_PLAN_ID = "E0_VMP_CATEGORY_MEAN_V1"

MAX_ENDPOINT_CANDIDATES = 512
MAX_ENDPOINT_CANDIDATES_PER_ROLE = 256
MAX_ENDPOINTS_PER_ROLE = 8
MAX_PAIRS = 64
MAX_EVIDENCE_IDS = 16
MAX_LOOKUP_CODEPOINTS = 20_000
MAX_LOOKUP_BYTES = 80_000
PREDICTION_AUDIT_MAX_BYTES = 4 * 1024 * 1024
PAIR_PACKET_MAX_BYTES = 16 * 1024 * 1024
FEATURE_TENSOR_MAX_BYTES = 2 * 1024 * 1024
FEATURE_PLAN_MAX_BYTES = 2 * 1024 * 1024
SYNTHETIC_REGISTRY_MAX_BYTES = 16 * 1024 * 1024
MAX_SYNTHETIC_REGISTRY_ENTRIES = 4_096
MAX_JSON_NESTING = 64
PAIR_CAPACITY = 64
PAIR_DIMENSION = 31

_HASH = re.compile(r"[0-9a-f]{64}\Z")
_SAFE_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z")
_REGISTRY_ID = re.compile(r"registry_[a-z0-9][a-z0-9_-]{0,62}\Z")
_RESOLVER_VERSION = re.compile(
    r"resolver_[0-9]{1,6}\.[0-9]{1,6}\.[0-9]{1,6}"
    r"(?:-[a-z0-9][a-z0-9.-]{0,31})?\Z"
)
_EVIDENCE_ID = re.compile(r"registry_evidence_[a-z0-9][a-z0-9_-]{0,45}\Z")

_ROLES = ("ACTOR", "DESTINATION")
_DESTINATION_KINDS = ("URL", "DOMAIN", "PHONE", "UPI", "BANK", "EMAIL", "APP", "OTHER")
_LOOKUP_STATUSES = ("ALIGNED", "UNALIGNED")
_STATES = ("MATCH", "MISMATCH", "UNKNOWN")
_COVERAGES = ("COMPLETE", "PARTIAL", "MISSING", "NOT_EVALUATED")
_SOURCES = ("REGISTRY", "ALIGNMENT_GUARD")

_PREDICTION_FIELDS = ("schema_version", "vmp_sha256", "path_predictions")
_PATH_PREDICTION_FIELDS = (
    "path_id",
    "path_sha256",
    "raw_endpoint_count",
    "actor_pre_cap_count",
    "destination_pre_cap_count",
    "actor_cap_hit",
    "destination_cap_hit",
    "endpoint_candidates",
    "selected_actor_candidate_indices",
    "selected_destination_candidate_indices",
)
_CANDIDATE_FIELDS = (
    "candidate_index",
    "role",
    "start",
    "end",
    "kind",
    "lookup_surface",
    "lookup_status",
    "score_f64_bits",
)
_ENDPOINT_FIELDS = ("role", "start", "end", "kind", "lookup_surface", "lookup_status")
_PACKET_FIELDS = (
    "packet_version",
    "vmp_sha256",
    "path_sha256",
    "registry_snapshot_id",
    "resolver_version",
    "no_explicit_pair",
    "registry_call_count",
    "pairs",
)
_PAIR_FIELDS = ("actor", "destination", "resolution")
_RESOLUTION_FIELDS = ("state", "registry_coverage", "resolution_source", "evidence_ids")
_PLAN_FIELDS = ("feature_version", "no_explicit_pair", "pairs")
_PLAN_ACTOR_FIELDS = ("start", "end", "lookup_status")
_PLAN_DESTINATION_FIELDS = ("start", "end", "kind", "lookup_status")
_PLAN_RESOLUTION_FIELDS = ("state", "registry_coverage", "resolution_source")
_TENSOR_FIELDS = (
    "schema_version",
    "plan_id",
    "vmp_sha256",
    "path_sha256",
    "semantic_feature_plan_sha256",
    "pair_capacity",
    "pair_dimension",
    "no_explicit_pair",
    "pair_mask",
    "vmp_hidden_grid_f64_bits",
    "pair_rows_f64_bits",
)
_REGISTRY_ARTIFACT_FIELDS = (
    "schema_version",
    "registry_snapshot_id",
    "resolver_version",
    "entries",
)
_REGISTRY_ENTRY_FIELDS = (
    "actor_lookup_surface",
    "destination_kind",
    "destination_lookup_surface",
    "state",
    "registry_coverage",
    "evidence_ids",
)


class SemanticValidationError(ValueError):
    """A semantic-stage failure carrying only a controlled safe code."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def _fail(code: str) -> SemanticValidationError:
    return SemanticValidationError(code)


def _utf8(value: str) -> bytes:
    return value.encode("utf-8")


def _get(value: object, name: str) -> Any:
    if isinstance(value, Mapping):
        if name not in value:
            raise _fail("semantic_invalid_path")
        return value[name]
    try:
        return getattr(value, name)
    except AttributeError as error:
        raise _fail("semantic_invalid_path") from error


def _valid_hash(value: object) -> bool:
    return isinstance(value, str) and _HASH.fullmatch(value) is not None


def _valid_safe_id(value: object) -> bool:
    return isinstance(value, str) and _SAFE_ID.fullmatch(value) is not None


def _require_canonical_size(value: object, maximum: int, code: str) -> bytes:
    try:
        return canonical_json_bytes(value, max_bytes=maximum)
    except CanonicalError as error:
        raise _fail(code) from error


def _reject_excessive_json_nesting(raw: bytes, code: str) -> None:
    """Bound recursive JSON exposure before invoking the shared parser."""

    depth = 0
    in_string = False
    escaped = False
    for byte in raw:
        if in_string:
            if escaped:
                escaped = False
            elif byte == 0x5C:
                escaped = True
            elif byte == 0x22:
                in_string = False
            continue
        if byte == 0x22:
            in_string = True
        elif byte in (0x5B, 0x7B):
            depth += 1
            if depth > MAX_JSON_NESTING:
                raise _fail(code)
        elif byte in (0x5D, 0x7D):
            depth = max(0, depth - 1)


def _validate_alignment(
    text: object, alignment: object, *, vmp_length: int
) -> tuple[str, tuple[tuple[int, int], ...]]:
    if not isinstance(text, str) or not isinstance(alignment, (list, tuple)):
        raise _fail("semantic_invalid_alignment")
    if len(text) != len(alignment):
        raise _fail("semantic_invalid_alignment")
    accepted: list[tuple[int, int]] = []
    previous_start = 0
    previous_end = 0
    for raw in alignment:
        if not isinstance(raw, (list, tuple)) or len(raw) != 2:
            raise _fail("semantic_invalid_alignment")
        start, end = raw
        if (
            not is_nonboolean_int(start, minimum=0)
            or not is_nonboolean_int(end, minimum=1)
            or not start < end <= vmp_length
            or (accepted and (start < previous_start or end < previous_end))
        ):
            raise _fail("semantic_invalid_alignment")
        accepted.append((start, end))
        previous_start, previous_end = start, end
    return text, tuple(accepted)


def _validate_rewrite_spans(
    spans: object, *, vmp_text: str
) -> tuple[tuple[int, int], ...]:
    if not isinstance(spans, (list, tuple)) or len(spans) > 64:
        raise _fail("semantic_invalid_rewrite_spans")
    accepted: list[tuple[int, int]] = []
    previous_end = 0
    for index, span in enumerate(spans):
        if not exact_keys(span, ("span_index", "start", "end", "source_text")):
            raise _fail("semantic_invalid_rewrite_spans")
        start, end = span["start"], span["end"]
        if (
            not is_nonboolean_int(span["span_index"])
            or span["span_index"] != index
            or not is_nonboolean_int(start, minimum=0)
            or not is_nonboolean_int(end, minimum=1)
            or not start < end <= len(vmp_text)
            or (accepted and start < previous_end)
            or span["source_text"] != vmp_text[start:end]
        ):
            raise _fail("semantic_invalid_rewrite_spans")
        accepted.append((start, end))
        previous_end = end
    return tuple(accepted)


def _validate_path_semantics(
    *,
    vmp_text: str,
    path_text: object,
    path_alignment: object,
    effective_rewrite_spans: object,
) -> tuple[str, tuple[tuple[int, int], ...]]:
    """Defensively replay the candidate path's source-coordinate invariants."""

    text, alignment = _validate_alignment(
        path_text,
        path_alignment,
        vmp_length=len(vmp_text),
    )
    spans = _validate_rewrite_spans(effective_rewrite_spans, vmp_text=vmp_text)
    outside_positions: list[int] = []
    covered_by_span: list[set[int]] = [set() for _ in spans]
    for character, (start, end) in zip(text, alignment):
        containing = [
            index
            for index, (span_start, span_end) in enumerate(spans)
            if span_start <= start and end <= span_end
        ]
        intersects = any(
            start < span_end and span_start < end
            for span_start, span_end in spans
        )
        if containing:
            if len(containing) != 1:
                raise _fail("semantic_invalid_alignment")
            covered_by_span[containing[0]].update(range(start, end))
        elif intersects:
            raise _fail("semantic_invalid_alignment")
        elif end != start + 1 or character != vmp_text[start]:
            raise _fail("semantic_invalid_alignment")
        else:
            outside_positions.append(start)
    rewritten_positions = {
        position
        for span_start, span_end in spans
        for position in range(span_start, span_end)
    }
    expected_outside = [
        position for position in range(len(vmp_text)) if position not in rewritten_positions
    ]
    if outside_positions != expected_outside:
        raise _fail("semantic_invalid_alignment")
    for covered, (span_start, span_end) in zip(covered_by_span, spans):
        if covered != set(range(span_start, span_end)):
            raise _fail("semantic_invalid_alignment")
    return text, alignment


def render_lookup_surface(
    *,
    vmp_text: str,
    path_text: str,
    path_alignment: Sequence[Sequence[int]],
    effective_rewrite_spans: Sequence[Mapping[str, Any]],
    start: int,
    end: int,
) -> tuple[str, str]:
    """Render one VMP-coordinate endpoint, rejecting rewrite cut-through."""

    if (
        not isinstance(vmp_text, str)
        or not is_nonboolean_int(start, minimum=0)
        or not is_nonboolean_int(end, minimum=1)
        or not start < end <= len(vmp_text)
    ):
        raise _fail("semantic_invalid_endpoint")
    validated_text, alignment = _validate_alignment(
        path_text, path_alignment, vmp_length=len(vmp_text)
    )
    spans = _validate_rewrite_spans(effective_rewrite_spans, vmp_text=vmp_text)
    for span_start, span_end in spans:
        intersects = start < span_end and span_start < end
        enclosed = start <= span_start and span_end <= end
        if intersects and not enclosed:
            return "", "UNALIGNED"
    surface = "".join(
        character
        for character, (source_start, source_end) in zip(validated_text, alignment)
        if start <= source_start and source_end <= end
    )
    if len(surface) > MAX_LOOKUP_CODEPOINTS or len(_utf8(surface)) > MAX_LOOKUP_BYTES:
        raise _fail("semantic_lookup_surface_too_large")
    return surface, "ALIGNED"


def _validate_endpoint(endpoint: object, *, vmp_length: int, candidate: bool) -> None:
    fields = _CANDIDATE_FIELDS if candidate else _ENDPOINT_FIELDS
    if not exact_keys(endpoint, fields):
        raise _fail("semantic_invalid_endpoint")
    role = endpoint["role"]
    kind = endpoint["kind"]
    start, end = endpoint["start"], endpoint["end"]
    surface = endpoint["lookup_surface"]
    status = endpoint["lookup_status"]
    if (
        role not in _ROLES
        or (role == "ACTOR" and kind != "NONE")
        or (role == "DESTINATION" and kind not in _DESTINATION_KINDS)
        or not is_nonboolean_int(start, minimum=0)
        or not is_nonboolean_int(end, minimum=1)
        or not start < end <= vmp_length
        or status not in _LOOKUP_STATUSES
        or not isinstance(surface, str)
        or len(surface) > MAX_LOOKUP_CODEPOINTS
        or len(_utf8(surface)) > MAX_LOOKUP_BYTES
        or (status == "UNALIGNED" and surface != "")
    ):
        raise _fail("semantic_invalid_endpoint")
    if candidate:
        if not is_nonboolean_int(endpoint["candidate_index"], minimum=0):
            raise _fail("semantic_invalid_prediction_audit")
        try:
            f64_bits_to_float(endpoint["score_f64_bits"])
        except CanonicalError as error:
            raise _fail("semantic_prediction_nonfinite") from error


def _endpoint_identity(candidate: Mapping[str, Any]) -> tuple[Any, ...]:
    return tuple(candidate[field] for field in _ENDPOINT_FIELDS)


def _packet_key(candidate: Mapping[str, Any]) -> tuple[Any, ...]:
    if candidate["role"] == "ACTOR":
        return (
            candidate["start"],
            candidate["end"],
            _utf8(candidate["lookup_surface"]),
        )
    return (
        candidate["start"],
        candidate["end"],
        _utf8(candidate["kind"]),
        _utf8(candidate["lookup_surface"]),
    )


def _selection(candidate_rows: Sequence[Mapping[str, Any]], role: str) -> tuple[int, list[int]]:
    winners: dict[tuple[Any, ...], Mapping[str, Any]] = {}
    for candidate in candidate_rows:
        if candidate["role"] != role:
            continue
        identity = _endpoint_identity(candidate)
        existing = winners.get(identity)
        if existing is None:
            winners[identity] = candidate
            continue
        score = f64_bits_to_float(candidate["score_f64_bits"])
        old_score = f64_bits_to_float(existing["score_f64_bits"])
        if score > old_score or (
            score == old_score
            and candidate["candidate_index"] < existing["candidate_index"]
        ):
            winners[identity] = candidate
    pre_cap_count = len(winners)
    score_selected = sorted(
        winners.values(),
        key=lambda row: (
            -f64_bits_to_float(row["score_f64_bits"]),
            row["start"],
            row["end"],
            _utf8(row["kind"]),
            _utf8(row["lookup_status"]),
            _utf8(row["lookup_surface"]),
        ),
    )[:MAX_ENDPOINTS_PER_ROLE]
    packet_order = sorted(score_selected, key=_packet_key)
    return pre_cap_count, [row["candidate_index"] for row in packet_order]


def _candidate_input_fields(candidate: object) -> tuple[str, ...]:
    if not isinstance(candidate, Mapping):
        raise _fail("semantic_invalid_endpoint")
    return tuple(candidate)


def _make_candidate(
    raw: Mapping[str, Any],
    *,
    index: int,
    vmp_text: str,
    path_text: str,
    alignment: Sequence[Sequence[int]],
    spans: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    allowed = {
        ("role", "start", "end", "kind", "score_f64_bits"),
        ("candidate_index", "role", "start", "end", "kind", "score_f64_bits"),
        (
            "candidate_index", "role", "start", "end", "kind",
            "lookup_surface", "lookup_status", "score_f64_bits",
        ),
    }
    if _candidate_input_fields(raw) not in allowed:
        raise _fail("semantic_invalid_endpoint")
    if "candidate_index" in raw and raw["candidate_index"] != index:
        raise _fail("semantic_invalid_prediction_audit")
    start, end = raw["start"], raw["end"]
    surface, status = render_lookup_surface(
        vmp_text=vmp_text,
        path_text=path_text,
        path_alignment=alignment,
        effective_rewrite_spans=spans,
        start=start,
        end=end,
    )
    if "lookup_surface" in raw and (
        raw["lookup_surface"] != surface or raw["lookup_status"] != status
    ):
        raise _fail("semantic_invalid_lookup_render")
    candidate = {
        "candidate_index": index,
        "role": raw["role"],
        "start": start,
        "end": end,
        "kind": raw["kind"],
        "lookup_surface": surface,
        "lookup_status": status,
        "score_f64_bits": raw["score_f64_bits"],
    }
    _validate_endpoint(candidate, vmp_length=len(vmp_text), candidate=True)
    return candidate


def build_prediction_audit(
    *,
    vmp_text: str,
    vmp_sha256: str,
    active_paths: Sequence[object],
    emitted_candidates_by_path: Mapping[str, Sequence[Mapping[str, Any]]],
) -> tuple[dict[str, Any], str]:
    """Build and validate the canonical score-bearing prediction audit."""

    if not isinstance(vmp_text, str) or not _valid_hash(vmp_sha256):
        raise _fail("semantic_invalid_prediction_audit")
    path_predictions: list[dict[str, Any]] = []
    seen_paths: set[str] = set()
    for path in active_paths:
        path_id = _get(path, "path_id")
        path_sha256 = _get(path, "path_sha256")
        path_text = _get(path, "text")
        alignment = _get(path, "alignment")
        spans = _get(path, "effective_rewrite_spans")
        if (
            not _valid_safe_id(path_id)
            or path_id in seen_paths
            or not _valid_hash(path_sha256)
        ):
            raise _fail("semantic_invalid_path")
        seen_paths.add(path_id)
        _, validated_alignment = _validate_path_semantics(
            vmp_text=vmp_text,
            path_text=path_text,
            path_alignment=alignment,
            effective_rewrite_spans=spans,
        )
        expected_path_hash = canonical_sha256(
            {"text": path_text, "alignment": [list(value) for value in validated_alignment]}
        )
        if path_sha256 != expected_path_hash:
            raise _fail("semantic_invalid_path_hash")
        _validate_rewrite_spans(spans, vmp_text=vmp_text)
        if path_id not in emitted_candidates_by_path:
            raise _fail("semantic_missing_path_predictions")
        raw_candidates = emitted_candidates_by_path[path_id]
        if not isinstance(raw_candidates, (list, tuple)) or len(raw_candidates) > MAX_ENDPOINT_CANDIDATES:
            raise _fail("semantic_prediction_bound")
        candidates = [
            _make_candidate(
                raw,
                index=index,
                vmp_text=vmp_text,
                path_text=path_text,
                alignment=alignment,
                spans=spans,
            )
            for index, raw in enumerate(raw_candidates)
        ]
        role_counts = {
            role: sum(candidate["role"] == role for candidate in candidates)
            for role in _ROLES
        }
        if any(value > MAX_ENDPOINT_CANDIDATES_PER_ROLE for value in role_counts.values()):
            raise _fail("semantic_prediction_bound")
        actor_count, selected_actor = _selection(candidates, "ACTOR")
        destination_count, selected_destination = _selection(candidates, "DESTINATION")
        path_predictions.append(
            {
                "path_id": path_id,
                "path_sha256": path_sha256,
                "raw_endpoint_count": len(candidates),
                "actor_pre_cap_count": actor_count,
                "destination_pre_cap_count": destination_count,
                "actor_cap_hit": actor_count > MAX_ENDPOINTS_PER_ROLE,
                "destination_cap_hit": destination_count > MAX_ENDPOINTS_PER_ROLE,
                "endpoint_candidates": candidates,
                "selected_actor_candidate_indices": selected_actor,
                "selected_destination_candidate_indices": selected_destination,
            }
        )
    if set(emitted_candidates_by_path) != seen_paths:
        raise _fail("semantic_extra_path_predictions")
    audit = {
        "schema_version": PREDICTION_AUDIT_VERSION,
        "vmp_sha256": vmp_sha256,
        "path_predictions": path_predictions,
    }
    digest = validate_prediction_audit(
        audit,
        vmp_text=vmp_text,
        expected_paths=active_paths,
    )
    return audit, digest


def validate_prediction_audit(
    audit: object,
    *,
    vmp_text: str,
    expected_paths: Sequence[object] | None = None,
) -> str:
    if (
        not exact_keys(audit, _PREDICTION_FIELDS)
        or audit["schema_version"] != PREDICTION_AUDIT_VERSION
        or not _valid_hash(audit["vmp_sha256"])
        or not isinstance(audit["path_predictions"], list)
        or not 1 <= len(audit["path_predictions"]) <= 8
    ):
        raise _fail("semantic_invalid_prediction_audit")
    expected = list(expected_paths) if expected_paths is not None else None
    if expected is not None and len(expected) != len(audit["path_predictions"]):
        raise _fail("semantic_invalid_prediction_audit")
    seen_paths: set[str] = set()
    for path_index, prediction in enumerate(audit["path_predictions"]):
        if not exact_keys(prediction, _PATH_PREDICTION_FIELDS):
            raise _fail("semantic_invalid_prediction_audit")
        path_id, path_hash = prediction["path_id"], prediction["path_sha256"]
        if (
            not _valid_safe_id(path_id)
            or path_id in seen_paths
            or not _valid_hash(path_hash)
            or not isinstance(prediction["endpoint_candidates"], list)
            or len(prediction["endpoint_candidates"]) > MAX_ENDPOINT_CANDIDATES
            or not is_nonboolean_int(prediction["raw_endpoint_count"], minimum=0, maximum=MAX_ENDPOINT_CANDIDATES)
            or prediction["raw_endpoint_count"] != len(prediction["endpoint_candidates"])
        ):
            raise _fail("semantic_invalid_prediction_audit")
        seen_paths.add(path_id)
        if expected is not None:
            path = expected[path_index]
            if path_id != _get(path, "path_id") or path_hash != _get(path, "path_sha256"):
                raise _fail("semantic_invalid_prediction_audit")
            _validate_path_semantics(
                vmp_text=vmp_text,
                path_text=_get(path, "text"),
                path_alignment=_get(path, "alignment"),
                effective_rewrite_spans=_get(path, "effective_rewrite_spans"),
            )
        candidates = prediction["endpoint_candidates"]
        for index, candidate in enumerate(candidates):
            _validate_endpoint(candidate, vmp_length=len(vmp_text), candidate=True)
            if candidate["candidate_index"] != index:
                raise _fail("semantic_invalid_prediction_audit")
            if expected is not None:
                surface, status = render_lookup_surface(
                    vmp_text=vmp_text,
                    path_text=_get(expected[path_index], "text"),
                    path_alignment=_get(expected[path_index], "alignment"),
                    effective_rewrite_spans=_get(expected[path_index], "effective_rewrite_spans"),
                    start=candidate["start"],
                    end=candidate["end"],
                )
                if surface != candidate["lookup_surface"] or status != candidate["lookup_status"]:
                    raise _fail("semantic_invalid_lookup_render")
        role_counts = {
            role: sum(candidate["role"] == role for candidate in candidates)
            for role in _ROLES
        }
        if any(value > MAX_ENDPOINT_CANDIDATES_PER_ROLE for value in role_counts.values()):
            raise _fail("semantic_prediction_bound")
        actor_count, selected_actor = _selection(candidates, "ACTOR")
        destination_count, selected_destination = _selection(candidates, "DESTINATION")
        for field in (
            "selected_actor_candidate_indices",
            "selected_destination_candidate_indices",
        ):
            selected = prediction[field]
            if (
                not isinstance(selected, list)
                or len(selected) > MAX_ENDPOINTS_PER_ROLE
                or len(set(selected)) != len(selected)
                or any(
                    not is_nonboolean_int(value, minimum=0, maximum=max(0, len(candidates) - 1))
                    for value in selected
                )
            ):
                raise _fail("semantic_invalid_prediction_audit")
        count_fields = (
            ("actor_pre_cap_count", actor_count),
            ("destination_pre_cap_count", destination_count),
        )
        if any(
            not is_nonboolean_int(prediction[field], minimum=0, maximum=256)
            or prediction[field] != count
            for field, count in count_fields
        ):
            raise _fail("semantic_invalid_prediction_audit")
        if (
            type(prediction["actor_cap_hit"]) is not bool
            or type(prediction["destination_cap_hit"]) is not bool
            or prediction["actor_cap_hit"] != (actor_count > MAX_ENDPOINTS_PER_ROLE)
            or prediction["destination_cap_hit"] != (destination_count > MAX_ENDPOINTS_PER_ROLE)
            or prediction["selected_actor_candidate_indices"] != selected_actor
            or prediction["selected_destination_candidate_indices"] != selected_destination
        ):
            raise _fail("semantic_invalid_prediction_audit")
    _require_canonical_size(audit, PREDICTION_AUDIT_MAX_BYTES, "semantic_prediction_audit_too_large")
    return canonical_sha256(audit, max_bytes=PREDICTION_AUDIT_MAX_BYTES)


def parse_prediction_audit_structural(raw: bytes, *, vmp_text: str) -> dict[str, Any]:
    """Parse structure only; this does not bind candidate-path rendering."""

    if not isinstance(raw, bytes) or len(raw) > PREDICTION_AUDIT_MAX_BYTES:
        raise _fail("semantic_prediction_audit_too_large")
    _reject_excessive_json_nesting(raw, "semantic_prediction_audit_nesting_too_deep")
    try:
        value = strict_json_loads(raw, prefix="prediction_audit")
    except CanonicalError as error:
        raise _fail("semantic_invalid_prediction_audit") from error
    validate_prediction_audit(value, vmp_text=vmp_text)
    return value


def parse_prediction_audit(raw: bytes, *, vmp_text: str) -> dict[str, Any]:
    """Backward-compatible structural parser; not an authoritative replay."""

    return parse_prediction_audit_structural(raw, vmp_text=vmp_text)


def _selected_endpoints(prediction: Mapping[str, Any], role: str) -> list[dict[str, Any]]:
    field = (
        "selected_actor_candidate_indices"
        if role == "ACTOR"
        else "selected_destination_candidate_indices"
    )
    candidates = prediction["endpoint_candidates"]
    endpoints: list[dict[str, Any]] = []
    for index in prediction[field]:
        candidate = candidates[index]
        endpoints.append({name: candidate[name] for name in _ENDPOINT_FIELDS})
    return endpoints


@dataclass(frozen=True)
class OfflineRegistryResolver:
    """Frozen in-memory resolver used only by the synthetic E0 rehearsal."""

    registry_snapshot_id: str
    resolver_version: str
    records: Mapping[tuple[str, str, str], Mapping[str, Any]]

    def __post_init__(self) -> None:
        if (
            _REGISTRY_ID.fullmatch(self.registry_snapshot_id) is None
            or _RESOLVER_VERSION.fullmatch(self.resolver_version) is None
            or not isinstance(self.records, Mapping)
        ):
            raise _fail("semantic_invalid_registry_fixture")
        copied: dict[tuple[str, str, str], dict[str, Any]] = {}
        for key, raw_resolution in self.records.items():
            if (
                not isinstance(key, tuple)
                or len(key) != 3
                or not all(isinstance(value, str) for value in key)
                or key[1] not in _DESTINATION_KINDS
                or not isinstance(raw_resolution, Mapping)
                or not exact_keys(
                    raw_resolution,
                    ("state", "registry_coverage", "evidence_ids"),
                )
            ):
                raise _fail("semantic_invalid_registry_fixture")
            resolution = {
                "state": raw_resolution.get("state"),
                "registry_coverage": raw_resolution.get("registry_coverage"),
                "resolution_source": "REGISTRY",
                "evidence_ids": list(raw_resolution.get("evidence_ids", [])),
            }
            _validate_resolution(resolution)
            copied[key] = resolution
        object.__setattr__(self, "records", MappingProxyType(copied))

    def resolve(
        self, actor: Mapping[str, Any], destination: Mapping[str, Any]
    ) -> dict[str, Any]:
        key = (
            actor["lookup_surface"],
            destination["kind"],
            destination["lookup_surface"],
        )
        resolution = self.records.get(key)
        if resolution is None:
            return {
                "state": "UNKNOWN",
                "registry_coverage": "MISSING",
                "resolution_source": "REGISTRY",
                "evidence_ids": [],
            }
        return {
            "state": resolution["state"],
            "registry_coverage": resolution["registry_coverage"],
            "resolution_source": "REGISTRY",
            "evidence_ids": list(resolution["evidence_ids"]),
        }


def _validate_resolution(resolution: object) -> None:
    if not exact_keys(resolution, _RESOLUTION_FIELDS):
        raise _fail("semantic_invalid_resolution")
    state = resolution["state"]
    coverage = resolution["registry_coverage"]
    source = resolution["resolution_source"]
    evidence_ids = resolution["evidence_ids"]
    if (
        state not in _STATES
        or coverage not in _COVERAGES
        or source not in _SOURCES
        or not isinstance(evidence_ids, list)
        or len(evidence_ids) > MAX_EVIDENCE_IDS
        or evidence_ids != sorted(set(evidence_ids), key=_utf8)
        or any(not isinstance(value, str) or _EVIDENCE_ID.fullmatch(value) is None for value in evidence_ids)
    ):
        raise _fail("semantic_invalid_resolution")
    registry_known = (
        state in {"MATCH", "MISMATCH"}
        and coverage == "COMPLETE"
        and source == "REGISTRY"
        and bool(evidence_ids)
    )
    registry_unknown = (
        state == "UNKNOWN"
        and coverage in {"PARTIAL", "MISSING"}
        and source == "REGISTRY"
    )
    alignment_unknown = (
        state == "UNKNOWN"
        and coverage == "NOT_EVALUATED"
        and source == "ALIGNMENT_GUARD"
        and evidence_ids == []
    )
    if not (registry_known or registry_unknown or alignment_unknown):
        raise _fail("semantic_invalid_resolution")


@dataclass(frozen=True)
class FrozenRegistry:
    """Registry reconstructed exclusively from one canonical artifact."""

    registry_snapshot_id: str
    resolver_version: str
    artifact_sha256: str
    artifact_bytes: bytes
    _records: Mapping[tuple[str, str, str], Mapping[str, Any]]

    def resolve(
        self, actor: Mapping[str, Any], destination: Mapping[str, Any]
    ) -> dict[str, Any]:
        key = (
            actor["lookup_surface"],
            destination["kind"],
            destination["lookup_surface"],
        )
        resolution = self._records.get(key)
        if resolution is None:
            return {
                "state": "UNKNOWN",
                "registry_coverage": "MISSING",
                "resolution_source": "REGISTRY",
                "evidence_ids": [],
            }
        return {
            "state": resolution["state"],
            "registry_coverage": resolution["registry_coverage"],
            "resolution_source": "REGISTRY",
            "evidence_ids": list(resolution["evidence_ids"]),
        }


def _registry_entry_key(entry: Mapping[str, Any]) -> tuple[bytes, bytes, bytes]:
    return (
        _utf8(entry["actor_lookup_surface"]),
        _utf8(entry["destination_kind"]),
        _utf8(entry["destination_lookup_surface"]),
    )


def validate_synthetic_registry_artifact(artifact: object) -> str:
    """Validate the complete canonical synthetic E0 registry artifact."""

    if (
        not exact_keys(artifact, _REGISTRY_ARTIFACT_FIELDS)
        or artifact["schema_version"] != "1.0.0"
        or not isinstance(artifact["registry_snapshot_id"], str)
        or _REGISTRY_ID.fullmatch(artifact["registry_snapshot_id"]) is None
        or not isinstance(artifact["resolver_version"], str)
        or _RESOLVER_VERSION.fullmatch(artifact["resolver_version"]) is None
        or not isinstance(artifact["entries"], list)
        or len(artifact["entries"]) > MAX_SYNTHETIC_REGISTRY_ENTRIES
    ):
        raise _fail("semantic_invalid_registry_artifact")
    prior_key: tuple[bytes, bytes, bytes] | None = None
    for entry in artifact["entries"]:
        if not exact_keys(entry, _REGISTRY_ENTRY_FIELDS):
            raise _fail("semantic_invalid_registry_artifact")
        actor = entry["actor_lookup_surface"]
        destination = entry["destination_lookup_surface"]
        if (
            not isinstance(actor, str)
            or not actor
            or len(actor) > MAX_LOOKUP_CODEPOINTS
            or len(_utf8(actor)) > MAX_LOOKUP_BYTES
            or entry["destination_kind"] not in _DESTINATION_KINDS
            or not isinstance(destination, str)
            or not destination
            or len(destination) > MAX_LOOKUP_CODEPOINTS
            or len(_utf8(destination)) > MAX_LOOKUP_BYTES
        ):
            raise _fail("semantic_invalid_registry_artifact")
        resolution = {
            "state": entry["state"],
            "registry_coverage": entry["registry_coverage"],
            "resolution_source": "REGISTRY",
            "evidence_ids": entry["evidence_ids"],
        }
        _validate_resolution(resolution)
        key = _registry_entry_key(entry)
        if prior_key is not None and key <= prior_key:
            raise _fail("semantic_invalid_registry_artifact")
        prior_key = key
    _require_canonical_size(
        artifact,
        SYNTHETIC_REGISTRY_MAX_BYTES,
        "semantic_registry_artifact_too_large",
    )
    return canonical_sha256(artifact, max_bytes=SYNTHETIC_REGISTRY_MAX_BYTES)


def build_synthetic_registry_artifact(
    *,
    registry_snapshot_id: str,
    resolver_version: str,
    records: Mapping[tuple[str, str, str], Mapping[str, Any]],
) -> tuple[dict[str, Any], bytes, str]:
    """Build exact canonical bytes for an auditable synthetic registry."""

    if not isinstance(records, Mapping):
        raise _fail("semantic_invalid_registry_artifact")
    entries: list[dict[str, Any]] = []
    for key, resolution in records.items():
        if (
            not isinstance(key, tuple)
            or len(key) != 3
            or not all(isinstance(value, str) for value in key)
            or not exact_keys(
                resolution,
                ("state", "registry_coverage", "evidence_ids"),
            )
        ):
            raise _fail("semantic_invalid_registry_artifact")
        entries.append(
            {
                "actor_lookup_surface": key[0],
                "destination_kind": key[1],
                "destination_lookup_surface": key[2],
                "state": resolution["state"],
                "registry_coverage": resolution["registry_coverage"],
                "evidence_ids": list(resolution["evidence_ids"]),
            }
        )
    entries.sort(key=_registry_entry_key)
    artifact = {
        "schema_version": "1.0.0",
        "registry_snapshot_id": registry_snapshot_id,
        "resolver_version": resolver_version,
        "entries": entries,
    }
    digest = validate_synthetic_registry_artifact(artifact)
    raw = canonical_json_bytes(artifact, max_bytes=SYNTHETIC_REGISTRY_MAX_BYTES)
    return artifact, raw, digest


def parse_synthetic_registry_artifact(raw: bytes) -> dict[str, Any]:
    """Parse and completely validate a self-contained synthetic registry."""

    if not isinstance(raw, bytes) or len(raw) > SYNTHETIC_REGISTRY_MAX_BYTES:
        raise _fail("semantic_registry_artifact_too_large")
    _reject_excessive_json_nesting(raw, "semantic_registry_nesting_too_deep")
    try:
        artifact = strict_json_loads(raw, prefix="synthetic_registry")
    except CanonicalError as error:
        raise _fail("semantic_invalid_registry_artifact") from error
    validate_synthetic_registry_artifact(artifact)
    return artifact


def frozen_registry_from_artifact(
    raw: bytes, *, expected_sha256: str | None = None
) -> FrozenRegistry:
    """Reconstruct immutable resolver truth from canonical artifact bytes."""

    artifact = parse_synthetic_registry_artifact(raw)
    digest = canonical_sha256(artifact, max_bytes=SYNTHETIC_REGISTRY_MAX_BYTES)
    if expected_sha256 is not None and (
        not _valid_hash(expected_sha256) or digest != expected_sha256
    ):
        raise _fail("semantic_registry_artifact_hash_mismatch")
    records: dict[tuple[str, str, str], Mapping[str, Any]] = {}
    for entry in artifact["entries"]:
        key = (
            entry["actor_lookup_surface"],
            entry["destination_kind"],
            entry["destination_lookup_surface"],
        )
        records[key] = MappingProxyType(
            {
                "state": entry["state"],
                "registry_coverage": entry["registry_coverage"],
                "evidence_ids": tuple(entry["evidence_ids"]),
            }
        )
    return FrozenRegistry(
        registry_snapshot_id=artifact["registry_snapshot_id"],
        resolver_version=artifact["resolver_version"],
        artifact_sha256=digest,
        artifact_bytes=bytes(raw),
        _records=MappingProxyType(records),
    )


def build_pair_packet(
    *,
    vmp_sha256: str,
    vmp_length: int,
    path_prediction: Mapping[str, Any],
    resolver: OfflineRegistryResolver | FrozenRegistry,
) -> tuple[dict[str, Any], str]:
    """Resolve the exact selected-audit endpoint Cartesian product."""

    if not _valid_hash(vmp_sha256) or not is_nonboolean_int(vmp_length, minimum=0):
        raise _fail("semantic_invalid_packet")
    actors = _selected_endpoints(path_prediction, "ACTOR")
    destinations = _selected_endpoints(path_prediction, "DESTINATION")
    pairs: list[dict[str, Any]] = []
    registry_call_count = 0
    for actor, destination in product(actors, destinations):
        if actor["lookup_status"] == "UNALIGNED" or destination["lookup_status"] == "UNALIGNED":
            resolution = {
                "state": "UNKNOWN",
                "registry_coverage": "NOT_EVALUATED",
                "resolution_source": "ALIGNMENT_GUARD",
                "evidence_ids": [],
            }
        else:
            resolution = resolver.resolve(actor, destination)
            registry_call_count += 1
        pairs.append(
            {
                "actor": dict(actor),
                "destination": dict(destination),
                "resolution": resolution,
            }
        )
    packet = {
        "packet_version": PAIR_PACKET_VERSION,
        "vmp_sha256": vmp_sha256,
        "path_sha256": path_prediction["path_sha256"],
        "registry_snapshot_id": resolver.registry_snapshot_id,
        "resolver_version": resolver.resolver_version,
        "no_explicit_pair": not pairs,
        "registry_call_count": registry_call_count,
        "pairs": pairs,
    }
    digest = validate_pair_packet(
        packet,
        vmp_length=vmp_length,
        expected_path_prediction=path_prediction,
    )
    return packet, digest


def validate_pair_packet(
    packet: object,
    *,
    vmp_length: int | None = None,
    expected_path_prediction: Mapping[str, Any] | None = None,
) -> str:
    if (
        not exact_keys(packet, _PACKET_FIELDS)
        or packet["packet_version"] != PAIR_PACKET_VERSION
        or not _valid_hash(packet["vmp_sha256"])
        or not _valid_hash(packet["path_sha256"])
        or not isinstance(packet["registry_snapshot_id"], str)
        or _REGISTRY_ID.fullmatch(packet["registry_snapshot_id"]) is None
        or not isinstance(packet["resolver_version"], str)
        or _RESOLVER_VERSION.fullmatch(packet["resolver_version"]) is None
        or type(packet["no_explicit_pair"]) is not bool
        or not is_nonboolean_int(packet["registry_call_count"], minimum=0, maximum=MAX_PAIRS)
        or not isinstance(packet["pairs"], list)
        or len(packet["pairs"]) > MAX_PAIRS
    ):
        raise _fail("semantic_invalid_packet")
    if vmp_length is None:
        vmp_length = max(
            (
                endpoint["end"]
                for pair in packet["pairs"]
                if isinstance(pair, dict)
                for endpoint in (pair.get("actor", {}), pair.get("destination", {}))
                if isinstance(endpoint, dict) and is_nonboolean_int(endpoint.get("end"), minimum=1)
            ),
            default=0,
        )
    if not is_nonboolean_int(vmp_length, minimum=0):
        raise _fail("semantic_invalid_packet")
    registry_calls = 0
    actor_inventory: dict[tuple[Any, ...], dict[str, Any]] = {}
    destination_inventory: dict[tuple[Any, ...], dict[str, Any]] = {}
    for pair in packet["pairs"]:
        if not exact_keys(pair, _PAIR_FIELDS):
            raise _fail("semantic_invalid_packet")
        _validate_endpoint(pair["actor"], vmp_length=vmp_length, candidate=False)
        _validate_endpoint(pair["destination"], vmp_length=vmp_length, candidate=False)
        if pair["actor"]["role"] != "ACTOR" or pair["destination"]["role"] != "DESTINATION":
            raise _fail("semantic_invalid_packet")
        _validate_resolution(pair["resolution"])
        guarded = (
            pair["actor"]["lookup_status"] == "UNALIGNED"
            or pair["destination"]["lookup_status"] == "UNALIGNED"
        )
        if guarded != (pair["resolution"]["resolution_source"] == "ALIGNMENT_GUARD"):
            raise _fail("semantic_invalid_resolution")
        registry_calls += pair["resolution"]["resolution_source"] == "REGISTRY"
        actor_inventory[tuple(pair["actor"][field] for field in _ENDPOINT_FIELDS)] = pair["actor"]
        destination_inventory[
            tuple(pair["destination"][field] for field in _ENDPOINT_FIELDS)
        ] = pair["destination"]
    actors_in_order = sorted(actor_inventory.values(), key=_packet_key)
    destinations_in_order = sorted(destination_inventory.values(), key=_packet_key)
    if len(actors_in_order) > 8 or len(destinations_in_order) > 8:
        raise _fail("semantic_invalid_packet")
    expected_inventory = [
        (actor, destination)
        for actor, destination in product(actors_in_order, destinations_in_order)
    ]
    actual_inventory = [(pair["actor"], pair["destination"]) for pair in packet["pairs"]]
    if actual_inventory != expected_inventory:
        raise _fail("semantic_invalid_packet")
    if (
        packet["no_explicit_pair"] != (len(packet["pairs"]) == 0)
        or packet["registry_call_count"] != registry_calls
    ):
        raise _fail("semantic_invalid_packet")
    if expected_path_prediction is not None:
        if packet["path_sha256"] != expected_path_prediction["path_sha256"]:
            raise _fail("semantic_packet_prediction_mismatch")
        actors = _selected_endpoints(expected_path_prediction, "ACTOR")
        destinations = _selected_endpoints(expected_path_prediction, "DESTINATION")
        expected_pairs = [(actor, destination) for actor, destination in product(actors, destinations)]
        actual_pairs = [(pair["actor"], pair["destination"]) for pair in packet["pairs"]]
        if actual_pairs != expected_pairs:
            raise _fail("semantic_packet_prediction_mismatch")
    _require_canonical_size(packet, PAIR_PACKET_MAX_BYTES, "semantic_packet_too_large")
    return canonical_sha256(packet, max_bytes=PAIR_PACKET_MAX_BYTES)


def parse_pair_packet_structural(raw: bytes) -> dict[str, Any]:
    """Parse packet structure only; registry truth is not established."""

    if not isinstance(raw, bytes) or len(raw) > PAIR_PACKET_MAX_BYTES:
        raise _fail("semantic_packet_too_large")
    _reject_excessive_json_nesting(raw, "semantic_packet_nesting_too_deep")
    try:
        value = strict_json_loads(raw, prefix="pair_packet")
    except CanonicalError as error:
        raise _fail("semantic_invalid_packet") from error
    validate_pair_packet(value)
    return value


def parse_pair_packet(raw: bytes) -> dict[str, Any]:
    """Backward-compatible structural parser; not an authoritative replay."""

    return parse_pair_packet_structural(raw)


def build_semantic_feature_plan(packet: Mapping[str, Any]) -> tuple[dict[str, Any], str]:
    validate_pair_packet(packet)
    plan, _ = build_semantic_feature_plan_unchecked(packet)
    digest = validate_semantic_feature_plan(plan)
    return plan, digest


def validate_semantic_feature_plan(
    plan: object, *, expected_packet: Mapping[str, Any] | None = None
) -> str:
    if (
        not exact_keys(plan, _PLAN_FIELDS)
        or plan["feature_version"] != FEATURE_VERSION
        or type(plan["no_explicit_pair"]) is not bool
        or not isinstance(plan["pairs"], list)
        or len(plan["pairs"]) > MAX_PAIRS
        or plan["no_explicit_pair"] != (len(plan["pairs"]) == 0)
    ):
        raise _fail("semantic_invalid_feature_plan")
    for pair in plan["pairs"]:
        if (
            not exact_keys(pair, _PAIR_FIELDS)
            or not exact_keys(pair["actor"], _PLAN_ACTOR_FIELDS)
            or not exact_keys(pair["destination"], _PLAN_DESTINATION_FIELDS)
            or not exact_keys(pair["resolution"], _PLAN_RESOLUTION_FIELDS)
        ):
            raise _fail("semantic_invalid_feature_plan")
        actor, destination, resolution = pair["actor"], pair["destination"], pair["resolution"]
        if (
            not is_nonboolean_int(actor["start"], minimum=0)
            or not is_nonboolean_int(actor["end"], minimum=1)
            or not actor["start"] < actor["end"]
            or actor["lookup_status"] not in _LOOKUP_STATUSES
            or not is_nonboolean_int(destination["start"], minimum=0)
            or not is_nonboolean_int(destination["end"], minimum=1)
            or not destination["start"] < destination["end"]
            or destination["kind"] not in _DESTINATION_KINDS
            or destination["lookup_status"] not in _LOOKUP_STATUSES
            or resolution["state"] not in _STATES
            or resolution["registry_coverage"] not in _COVERAGES
            or resolution["resolution_source"] not in _SOURCES
        ):
            raise _fail("semantic_invalid_feature_plan")
        guarded = (
            actor["lookup_status"] == "UNALIGNED"
            or destination["lookup_status"] == "UNALIGNED"
        )
        registry_known = (
            not guarded
            and resolution["state"] in {"MATCH", "MISMATCH"}
            and resolution["registry_coverage"] == "COMPLETE"
            and resolution["resolution_source"] == "REGISTRY"
        )
        registry_unknown = (
            not guarded
            and resolution["state"] == "UNKNOWN"
            and resolution["registry_coverage"] in {"PARTIAL", "MISSING"}
            and resolution["resolution_source"] == "REGISTRY"
        )
        alignment_unknown = (
            guarded
            and resolution["state"] == "UNKNOWN"
            and resolution["registry_coverage"] == "NOT_EVALUATED"
            and resolution["resolution_source"] == "ALIGNMENT_GUARD"
        )
        if not (registry_known or registry_unknown or alignment_unknown):
            raise _fail("semantic_invalid_feature_plan")
    if expected_packet is not None:
        validate_pair_packet(expected_packet)
        expected, _ = build_semantic_feature_plan_unchecked(expected_packet)
        if plan != expected:
            raise _fail("semantic_feature_plan_packet_mismatch")
    return canonical_sha256(plan)


def parse_semantic_feature_plan_structural(raw: bytes) -> dict[str, Any]:
    """Parse plan structure only; audit, packet, and registry are not bound."""

    if not isinstance(raw, bytes) or len(raw) > FEATURE_PLAN_MAX_BYTES:
        raise _fail("semantic_feature_plan_too_large")
    _reject_excessive_json_nesting(raw, "semantic_feature_plan_nesting_too_deep")
    try:
        value = strict_json_loads(raw, prefix="semantic_feature_plan")
    except CanonicalError as error:
        raise _fail("semantic_invalid_feature_plan") from error
    validate_semantic_feature_plan(value)
    return value


def build_semantic_feature_plan_unchecked(
    packet: Mapping[str, Any],
) -> tuple[dict[str, Any], str]:
    """Internal projection used to avoid validation recursion."""

    pairs: list[dict[str, Any]] = []
    for pair in packet["pairs"]:
        pairs.append(
            {
                "actor": {field: pair["actor"][field] for field in _PLAN_ACTOR_FIELDS},
                "destination": {
                    field: pair["destination"][field] for field in _PLAN_DESTINATION_FIELDS
                },
                "resolution": {
                    field: pair["resolution"][field] for field in _PLAN_RESOLUTION_FIELDS
                },
            }
        )
    plan = {
        "feature_version": FEATURE_VERSION,
        "no_explicit_pair": not pairs,
        "pairs": pairs,
    }
    return plan, canonical_sha256(plan)


def _category_vector(character: str) -> tuple[float, float, float, float, float]:
    category = unicodedata.category(character)
    if category.startswith("L"):
        index = 0
    elif category.startswith("M"):
        index = 1
    elif category == "Nd":
        index = 2
    elif character.isspace():
        index = 3
    else:
        index = 4
    return tuple(1.0 if position == index else 0.0 for position in range(5))  # type: ignore[return-value]


def e0_vmp_category_grid(vmp_text: str) -> tuple[tuple[float, ...], ...]:
    if not isinstance(vmp_text, str):
        raise _fail("semantic_invalid_vmp")
    return tuple(_category_vector(character) for character in vmp_text)


def _endpoint_mean(
    grid: Sequence[Sequence[float]], start: int, end: int
) -> list[float]:
    return [sequential_mean([grid[index][dimension] for index in range(start, end)]) for dimension in range(5)]


def _one_hot(value: str, vocabulary: Sequence[str]) -> list[float]:
    if value not in vocabulary:
        raise _fail("semantic_invalid_feature_plan")
    return [1.0 if candidate == value else 0.0 for candidate in vocabulary]


def _feature_rows(vmp_text: str, plan: Mapping[str, Any]) -> tuple[str, str, list[bool]]:
    grid = e0_vmp_category_grid(vmp_text)
    grid_bits = "".join(float_to_f64_bits(value) for row in grid for value in row)
    rows: list[list[float]] = []
    for pair in plan["pairs"]:
        actor, destination, resolution = pair["actor"], pair["destination"], pair["resolution"]
        if actor["end"] > len(grid) or destination["end"] > len(grid):
            raise _fail("semantic_invalid_feature_plan")
        row = (
            _endpoint_mean(grid, actor["start"], actor["end"])
            + _endpoint_mean(grid, destination["start"], destination["end"])
            + _one_hot(destination["kind"], _DESTINATION_KINDS)
            + _one_hot(actor["lookup_status"], _LOOKUP_STATUSES)
            + _one_hot(destination["lookup_status"], _LOOKUP_STATUSES)
            + _one_hot(resolution["state"], _STATES)
            + _one_hot(resolution["registry_coverage"], _COVERAGES)
            + _one_hot(resolution["resolution_source"], _SOURCES)
        )
        if len(row) != PAIR_DIMENSION:
            raise AssertionError("E0 pair feature dimension drifted")
        rows.append(row)
    mask = [True] * len(rows) + [False] * (PAIR_CAPACITY - len(rows))
    rows.extend([[0.0] * PAIR_DIMENSION for _ in range(PAIR_CAPACITY - len(rows))])
    row_bits = "".join(float_to_f64_bits(value) for row in rows for value in row)
    return grid_bits, row_bits, mask


def build_e0_feature_tensor(
    *,
    vmp_text: str,
    vmp_sha256: str,
    path_sha256: str,
    semantic_feature_plan: Mapping[str, Any],
    semantic_feature_plan_sha256: str | None = None,
) -> tuple[dict[str, Any], str]:
    plan_hash = validate_semantic_feature_plan(semantic_feature_plan)
    if semantic_feature_plan_sha256 is not None and semantic_feature_plan_sha256 != plan_hash:
        raise _fail("semantic_feature_plan_hash_mismatch")
    if not _valid_hash(vmp_sha256) or not _valid_hash(path_sha256):
        raise _fail("semantic_invalid_feature_tensor")
    grid_bits, row_bits, mask = _feature_rows(vmp_text, semantic_feature_plan)
    tensor = {
        "schema_version": FEATURE_TENSOR_VERSION,
        "plan_id": E0_FEATURE_PLAN_ID,
        "vmp_sha256": vmp_sha256,
        "path_sha256": path_sha256,
        "semantic_feature_plan_sha256": plan_hash,
        "pair_capacity": PAIR_CAPACITY,
        "pair_dimension": PAIR_DIMENSION,
        "no_explicit_pair": semantic_feature_plan["no_explicit_pair"],
        "pair_mask": mask,
        "vmp_hidden_grid_f64_bits": grid_bits,
        "pair_rows_f64_bits": row_bits,
    }
    digest = validate_e0_feature_tensor(
        tensor, vmp_text=vmp_text, semantic_feature_plan=semantic_feature_plan
    )
    return tensor, digest


def validate_e0_feature_tensor(
    tensor: object,
    *,
    vmp_text: str,
    semantic_feature_plan: Mapping[str, Any],
) -> str:
    plan_hash = validate_semantic_feature_plan(semantic_feature_plan)
    if (
        not exact_keys(tensor, _TENSOR_FIELDS)
        or tensor["schema_version"] != FEATURE_TENSOR_VERSION
        or tensor["plan_id"] != E0_FEATURE_PLAN_ID
        or not _valid_hash(tensor["vmp_sha256"])
        or not _valid_hash(tensor["path_sha256"])
        or tensor["semantic_feature_plan_sha256"] != plan_hash
        or not is_nonboolean_int(tensor["pair_capacity"])
        or tensor["pair_capacity"] != PAIR_CAPACITY
        or not is_nonboolean_int(tensor["pair_dimension"])
        or tensor["pair_dimension"] != PAIR_DIMENSION
        or type(tensor["no_explicit_pair"]) is not bool
        or tensor["no_explicit_pair"] != semantic_feature_plan["no_explicit_pair"]
        or not isinstance(tensor["pair_mask"], list)
        or len(tensor["pair_mask"]) != PAIR_CAPACITY
        or any(type(value) is not bool for value in tensor["pair_mask"])
        or not isinstance(tensor["vmp_hidden_grid_f64_bits"], str)
        or not isinstance(tensor["pair_rows_f64_bits"], str)
        or len(tensor["vmp_hidden_grid_f64_bits"]) != 80 * len(vmp_text)
        or len(tensor["pair_rows_f64_bits"]) != 16 * PAIR_CAPACITY * PAIR_DIMENSION
    ):
        raise _fail("semantic_invalid_feature_tensor")
    expected_grid, expected_rows, expected_mask = _feature_rows(vmp_text, semantic_feature_plan)
    if (
        tensor["pair_mask"] != expected_mask
        or tensor["vmp_hidden_grid_f64_bits"] != expected_grid
        or tensor["pair_rows_f64_bits"] != expected_rows
    ):
        raise _fail("semantic_invalid_feature_tensor")
    _require_canonical_size(tensor, FEATURE_TENSOR_MAX_BYTES, "semantic_feature_tensor_too_large")
    return canonical_sha256(tensor, max_bytes=FEATURE_TENSOR_MAX_BYTES)


def parse_e0_feature_tensor_structural(
    raw: bytes, *, vmp_text: str, semantic_feature_plan: Mapping[str, Any]
) -> dict[str, Any]:
    """Parse tensor structure only; upstream audit/registry truth is not bound."""

    if not isinstance(raw, bytes) or len(raw) > FEATURE_TENSOR_MAX_BYTES:
        raise _fail("semantic_feature_tensor_too_large")
    _reject_excessive_json_nesting(raw, "semantic_feature_tensor_nesting_too_deep")
    try:
        value = strict_json_loads(raw, prefix="feature_tensor")
    except CanonicalError as error:
        raise _fail("semantic_invalid_feature_tensor") from error
    validate_e0_feature_tensor(
        value, vmp_text=vmp_text, semantic_feature_plan=semantic_feature_plan
    )
    return value


def parse_e0_feature_tensor(
    raw: bytes, *, vmp_text: str, semantic_feature_plan: Mapping[str, Any]
) -> dict[str, Any]:
    """Backward-compatible structural parser; not an authoritative replay."""

    return parse_e0_feature_tensor_structural(
        raw,
        vmp_text=vmp_text,
        semantic_feature_plan=semantic_feature_plan,
    )


def packet_state_prevalence(packet: Mapping[str, Any]) -> dict[str, float]:
    validate_pair_packet(packet)
    if not packet["pairs"]:
        return {"MATCH": 0.0, "MISMATCH": 0.0, "UNKNOWN": 0.0, "N/A": 1.0}
    denominator = float(len(packet["pairs"]))
    return {
        state: sequential_sum(
            1.0 for pair in packet["pairs"] if pair["resolution"]["state"] == state
        ) / denominator
        for state in ("MATCH", "MISMATCH", "UNKNOWN", "N/A")
    }


def marginalized_pair_prevalence(
    weighted_packets: Sequence[tuple[str, Mapping[str, Any]]]
) -> dict[str, float]:
    if not isinstance(weighted_packets, (list, tuple)) or not 1 <= len(weighted_packets) <= 8:
        raise _fail("semantic_empty_marginalization")
    decoded: list[tuple[float, dict[str, float]]] = []
    for q_bits, packet in weighted_packets:
        try:
            q = f64_bits_to_float(q_bits)
        except CanonicalError as error:
            raise _fail("semantic_invalid_q") from error
        if not 0.0 <= q <= 1.0:
            raise _fail("semantic_invalid_q")
        decoded.append((q, packet_state_prevalence(packet)))
    return {
        state: sequential_sum(q * prevalence[state] for q, prevalence in decoded)
        for state in ("MATCH", "MISMATCH", "UNKNOWN", "N/A")
    }


@dataclass(frozen=True)
class ReplayedSemanticPath:
    """Authoritative exact-byte result for one replayed candidate path."""

    path_id: str
    q_f64_bits: str
    pair_packet_bytes: bytes
    pair_packet_sha256: str
    semantic_feature_plan_bytes: bytes
    semantic_feature_plan_sha256: str
    feature_tensor_bytes: bytes
    feature_tensor_sha256: str
    registry_pair_tuples: tuple[tuple[int, int, int, int, str, str, str], ...]
    state_prevalence: tuple[tuple[str, float], ...]


@dataclass(frozen=True)
class SemanticReplayResult:
    """Frozen complete-chain replay; structural parses alone are not this result."""

    vmp_sha256: str
    prediction_audit_bytes: bytes
    prediction_audit_sha256: str
    registry_artifact_bytes: bytes
    registry_artifact_sha256: str
    registry_snapshot_id: str
    resolver_version: str
    paths: tuple[ReplayedSemanticPath, ...]
    pair_prevalence: tuple[tuple[str, float], ...]

    @property
    def P_pair(self) -> Mapping[str, float]:
        return MappingProxyType(dict(self.pair_prevalence))


def _authoritative_paths(
    *, active_paths: Sequence[object] | None, candidate_context: object | None
) -> tuple[object, ...]:
    if (active_paths is None) == (candidate_context is None):
        raise _fail("semantic_replay_candidate_context")
    if active_paths is not None:
        paths = active_paths
    else:
        paths = None
        for name in ("active_paths", "internal_paths", "paths"):
            candidate = getattr(candidate_context, name, None)
            if isinstance(candidate, (list, tuple)):
                paths = candidate
                break
        if paths is None:
            raise _fail("semantic_replay_candidate_context")
    if not isinstance(paths, (list, tuple)) or not 1 <= len(paths) <= 8:
        raise _fail("semantic_replay_candidate_context")
    return tuple(paths)


def _path_q_bits(path: object) -> str:
    if isinstance(path, Mapping) and "q_f64_bits" in path:
        bits = path["q_f64_bits"]
    elif hasattr(path, "record"):
        bits = path.record["q_f64_bits"]
    elif hasattr(path, "q"):
        bits = float_to_f64_bits(path.q)
    else:
        raise _fail("semantic_invalid_q")
    try:
        value = f64_bits_to_float(bits)
    except CanonicalError as error:
        raise _fail("semantic_invalid_q") from error
    if not 0.0 <= value <= 1.0:
        raise _fail("semantic_invalid_q")
    return bits


def _validate_path_map(
    value: object,
    path_ids: Sequence[str],
    *,
    code: str,
    require_bytes: bool,
) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or set(value) != set(path_ids):
        raise _fail(code)
    if require_bytes and any(not isinstance(item, bytes) for item in value.values()):
        raise _fail(code)
    return value


def _check_expected_hash(
    actual: str, expected: object, *, code: str
) -> None:
    if expected is not None and (not _valid_hash(expected) or actual != expected):
        raise _fail(code)


def replay_semantic_chain(
    *,
    vmp_text: str,
    vmp_sha256: str,
    prediction_audit_bytes: bytes,
    registry_artifact_bytes: bytes,
    pair_packet_bytes_by_path: Mapping[str, bytes],
    semantic_feature_plan_bytes_by_path: Mapping[str, bytes],
    feature_tensor_bytes_by_path: Mapping[str, bytes],
    active_paths: Sequence[object] | None = None,
    candidate_context: object | None = None,
    expected_prediction_audit_sha256: str | None = None,
    expected_registry_artifact_sha256: str | None = None,
    expected_pair_packet_sha256_by_path: Mapping[str, str] | None = None,
    expected_semantic_feature_plan_sha256_by_path: Mapping[str, str] | None = None,
    expected_feature_tensor_sha256_by_path: Mapping[str, str] | None = None,
) -> SemanticReplayResult:
    """Replay and bind the complete VMP -> candidate -> registry -> feature chain.

    Unlike the ``*_structural`` parsers, this function treats the candidate
    path context and canonical registry artifact as authoritative inputs and
    recomputes every derived semantic artifact before returning frozen bytes.
    """

    if not isinstance(vmp_text, str) or not _valid_hash(vmp_sha256):
        raise _fail("semantic_replay_vmp_mismatch")
    paths = _authoritative_paths(
        active_paths=active_paths,
        candidate_context=candidate_context,
    )
    path_ids = [_get(path, "path_id") for path in paths]
    if (
        len(set(path_ids)) != len(path_ids)
        or any(not _valid_safe_id(path_id) for path_id in path_ids)
    ):
        raise _fail("semantic_replay_candidate_context")
    packet_bytes = _validate_path_map(
        pair_packet_bytes_by_path,
        path_ids,
        code="semantic_replay_packet_set_mismatch",
        require_bytes=True,
    )
    plan_bytes = _validate_path_map(
        semantic_feature_plan_bytes_by_path,
        path_ids,
        code="semantic_replay_feature_plan_set_mismatch",
        require_bytes=True,
    )
    tensor_bytes = _validate_path_map(
        feature_tensor_bytes_by_path,
        path_ids,
        code="semantic_replay_feature_tensor_set_mismatch",
        require_bytes=True,
    )
    expected_packet_hashes = (
        None
        if expected_pair_packet_sha256_by_path is None
        else _validate_path_map(
            expected_pair_packet_sha256_by_path,
            path_ids,
            code="semantic_replay_packet_hash_mismatch",
            require_bytes=False,
        )
    )
    expected_plan_hashes = (
        None
        if expected_semantic_feature_plan_sha256_by_path is None
        else _validate_path_map(
            expected_semantic_feature_plan_sha256_by_path,
            path_ids,
            code="semantic_replay_feature_plan_hash_mismatch",
            require_bytes=False,
        )
    )
    expected_tensor_hashes = (
        None
        if expected_feature_tensor_sha256_by_path is None
        else _validate_path_map(
            expected_feature_tensor_sha256_by_path,
            path_ids,
            code="semantic_replay_feature_tensor_hash_mismatch",
            require_bytes=False,
        )
    )

    audit = parse_prediction_audit_structural(
        prediction_audit_bytes,
        vmp_text=vmp_text,
    )
    if audit["vmp_sha256"] != vmp_sha256:
        raise _fail("semantic_replay_vmp_mismatch")
    audit_hash = validate_prediction_audit(
        audit,
        vmp_text=vmp_text,
        expected_paths=paths,
    )
    _check_expected_hash(
        audit_hash,
        expected_prediction_audit_sha256,
        code="semantic_replay_prediction_audit_hash_mismatch",
    )
    registry = frozen_registry_from_artifact(
        registry_artifact_bytes,
        expected_sha256=expected_registry_artifact_sha256,
    )

    replayed_paths: list[ReplayedSemanticPath] = []
    weighted_packets: list[tuple[str, Mapping[str, Any]]] = []
    for path, prediction in zip(paths, audit["path_predictions"]):
        path_id = prediction["path_id"]
        supplied_packet = parse_pair_packet_structural(packet_bytes[path_id])
        supplied_packet_hash = canonical_sha256(
            supplied_packet,
            max_bytes=PAIR_PACKET_MAX_BYTES,
        )
        if expected_packet_hashes is not None:
            _check_expected_hash(
                supplied_packet_hash,
                expected_packet_hashes[path_id],
                code="semantic_replay_packet_hash_mismatch",
            )
        expected_packet, expected_packet_hash = build_pair_packet(
            vmp_sha256=vmp_sha256,
            vmp_length=len(vmp_text),
            path_prediction=prediction,
            resolver=registry,
        )
        if (
            supplied_packet != expected_packet
            or supplied_packet_hash != expected_packet_hash
            or packet_bytes[path_id] != canonical_json_bytes(expected_packet)
        ):
            raise _fail("semantic_replay_packet_mismatch")

        supplied_plan = parse_semantic_feature_plan_structural(plan_bytes[path_id])
        supplied_plan_hash = canonical_sha256(supplied_plan)
        if expected_plan_hashes is not None:
            _check_expected_hash(
                supplied_plan_hash,
                expected_plan_hashes[path_id],
                code="semantic_replay_feature_plan_hash_mismatch",
            )
        expected_plan, expected_plan_hash = build_semantic_feature_plan(expected_packet)
        if (
            supplied_plan != expected_plan
            or supplied_plan_hash != expected_plan_hash
            or plan_bytes[path_id] != canonical_json_bytes(expected_plan)
        ):
            raise _fail("semantic_replay_feature_plan_mismatch")

        supplied_tensor = parse_e0_feature_tensor_structural(
            tensor_bytes[path_id],
            vmp_text=vmp_text,
            semantic_feature_plan=expected_plan,
        )
        supplied_tensor_hash = canonical_sha256(
            supplied_tensor,
            max_bytes=FEATURE_TENSOR_MAX_BYTES,
        )
        if expected_tensor_hashes is not None:
            _check_expected_hash(
                supplied_tensor_hash,
                expected_tensor_hashes[path_id],
                code="semantic_replay_feature_tensor_hash_mismatch",
            )
        expected_tensor, expected_tensor_hash = build_e0_feature_tensor(
            vmp_text=vmp_text,
            vmp_sha256=vmp_sha256,
            path_sha256=prediction["path_sha256"],
            semantic_feature_plan=expected_plan,
            semantic_feature_plan_sha256=expected_plan_hash,
        )
        if (
            supplied_tensor != expected_tensor
            or supplied_tensor_hash != expected_tensor_hash
            or tensor_bytes[path_id] != canonical_json_bytes(expected_tensor)
        ):
            raise _fail("semantic_replay_feature_tensor_mismatch")

        q_bits = _path_q_bits(path)
        weighted_packets.append((q_bits, expected_packet))
        prevalence = packet_state_prevalence(expected_packet)
        pair_tuples = tuple(
            (
                pair["actor"]["start"],
                pair["actor"]["end"],
                pair["destination"]["start"],
                pair["destination"]["end"],
                pair["resolution"]["state"],
                pair["resolution"]["registry_coverage"],
                pair["resolution"]["resolution_source"],
            )
            for pair in expected_packet["pairs"]
        )
        replayed_paths.append(
            ReplayedSemanticPath(
                path_id=path_id,
                q_f64_bits=q_bits,
                pair_packet_bytes=bytes(packet_bytes[path_id]),
                pair_packet_sha256=expected_packet_hash,
                semantic_feature_plan_bytes=bytes(plan_bytes[path_id]),
                semantic_feature_plan_sha256=expected_plan_hash,
                feature_tensor_bytes=bytes(tensor_bytes[path_id]),
                feature_tensor_sha256=expected_tensor_hash,
                registry_pair_tuples=pair_tuples,
                state_prevalence=tuple(prevalence.items()),
            )
        )
    pair_prevalence = marginalized_pair_prevalence(weighted_packets)
    return SemanticReplayResult(
        vmp_sha256=vmp_sha256,
        prediction_audit_bytes=bytes(prediction_audit_bytes),
        prediction_audit_sha256=audit_hash,
        registry_artifact_bytes=bytes(registry_artifact_bytes),
        registry_artifact_sha256=registry.artifact_sha256,
        registry_snapshot_id=registry.registry_snapshot_id,
        resolver_version=registry.resolver_version,
        paths=tuple(replayed_paths),
        pair_prevalence=tuple(pair_prevalence.items()),
    )


def build_semantic_artifacts(
    *,
    vmp_text: str,
    vmp_sha256: str,
    active_paths: Sequence[object],
    emitted_candidates_by_path: Mapping[str, Sequence[Mapping[str, Any]]],
    registry_resolver: OfflineRegistryResolver,
) -> dict[str, Any]:
    """Build every synthetic semantic artifact for the active path list."""

    audit, audit_hash = build_prediction_audit(
        vmp_text=vmp_text,
        vmp_sha256=vmp_sha256,
        active_paths=active_paths,
        emitted_candidates_by_path=emitted_candidates_by_path,
    )
    path_artifacts: list[dict[str, Any]] = []
    weighted_packets: list[tuple[str, Mapping[str, Any]]] = []
    for path, prediction in zip(active_paths, audit["path_predictions"]):
        packet, packet_hash = build_pair_packet(
            vmp_sha256=vmp_sha256,
            vmp_length=len(vmp_text),
            path_prediction=prediction,
            resolver=registry_resolver,
        )
        plan, plan_hash = build_semantic_feature_plan(packet)
        tensor, tensor_hash = build_e0_feature_tensor(
            vmp_text=vmp_text,
            vmp_sha256=vmp_sha256,
            path_sha256=prediction["path_sha256"],
            semantic_feature_plan=plan,
            semantic_feature_plan_sha256=plan_hash,
        )
        if isinstance(path, Mapping) and "q_f64_bits" in path:
            q_bits = path["q_f64_bits"]
        elif hasattr(path, "record"):
            q_bits = path.record["q_f64_bits"]
        elif hasattr(path, "q"):
            q_bits = float_to_f64_bits(path.q)
        else:
            raise _fail("semantic_invalid_q")
        weighted_packets.append((q_bits, packet))
        path_artifacts.append(
            {
                "path_id": prediction["path_id"],
                "pair_packet": packet,
                "pair_packet_sha256": packet_hash,
                "semantic_feature_plan": plan,
                "semantic_feature_plan_sha256": plan_hash,
                "semantic_feature_tensor": tensor,
                "semantic_feature_tensor_sha256": tensor_hash,
                "state_prevalence": packet_state_prevalence(packet),
            }
        )
    return {
        "prediction_audit": audit,
        "prediction_audit_sha256": audit_hash,
        "paths": path_artifacts,
        "P_pair": marginalized_pair_prevalence(weighted_packets),
    }


__all__ = [
    "E0_FEATURE_PLAN_ID",
    "FEATURE_TENSOR_MAX_BYTES",
    "FrozenRegistry",
    "MAX_ENDPOINTS_PER_ROLE",
    "MAX_PAIRS",
    "OfflineRegistryResolver",
    "PAIR_CAPACITY",
    "PAIR_DIMENSION",
    "PAIR_PACKET_MAX_BYTES",
    "PREDICTION_AUDIT_MAX_BYTES",
    "SemanticValidationError",
    "SemanticReplayResult",
    "ReplayedSemanticPath",
    "build_e0_feature_tensor",
    "build_pair_packet",
    "build_prediction_audit",
    "build_synthetic_registry_artifact",
    "build_semantic_artifacts",
    "build_semantic_feature_plan",
    "e0_vmp_category_grid",
    "frozen_registry_from_artifact",
    "marginalized_pair_prevalence",
    "packet_state_prevalence",
    "parse_e0_feature_tensor",
    "parse_e0_feature_tensor_structural",
    "parse_pair_packet",
    "parse_pair_packet_structural",
    "parse_prediction_audit",
    "parse_prediction_audit_structural",
    "parse_semantic_feature_plan_structural",
    "parse_synthetic_registry_artifact",
    "render_lookup_surface",
    "replay_semantic_chain",
    "validate_e0_feature_tensor",
    "validate_pair_packet",
    "validate_prediction_audit",
    "validate_synthetic_registry_artifact",
    "validate_semantic_feature_plan",
]
