"""Pinned binary64 helpers for Fisher's synthetic E0 arithmetic audit."""

from __future__ import annotations

import math
import re
import struct
from typing import Iterable, Sequence

from ._canonical import CanonicalError


_F64_BITS = re.compile(r"[0-9a-f]{16}\Z")
POSITIVE_ZERO_BITS = "0000000000000000"
NEGATIVE_ZERO_BITS = "8000000000000000"


def canonicalize_zero(value: float) -> float:
    return 0.0 if value == 0.0 else value


def _finite_float(value: object, code: str = "numeric_nonfinite") -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise CanonicalError("numeric_invalid_type")
    result = float(value)
    if not math.isfinite(result):
        raise CanonicalError(code)
    return canonicalize_zero(result)


def float_to_f64_bits(value: object) -> str:
    """Return canonical big-endian binary64 bits, mapping -0.0 to +0.0."""

    finite = _finite_float(value)
    return struct.pack(">d", finite).hex()


def f64_bits_to_float(bits: object, *, reject_negative_zero: bool = True) -> float:
    if not isinstance(bits, str) or _F64_BITS.fullmatch(bits) is None:
        raise CanonicalError("numeric_invalid_f64_bits")
    if reject_negative_zero and bits == NEGATIVE_ZERO_BITS:
        raise CanonicalError("numeric_negative_zero")
    value = struct.unpack(">d", bytes.fromhex(bits))[0]
    if not math.isfinite(value):
        raise CanonicalError("numeric_nonfinite")
    return canonicalize_zero(value)


def binary64_add(left: object, right: object) -> float:
    result = _finite_float(_finite_float(left) + _finite_float(right))
    return canonicalize_zero(result)


def binary64_divide(numerator: object, denominator: object) -> float:
    top = _finite_float(numerator)
    bottom = _finite_float(denominator)
    if bottom == 0.0:
        raise CanonicalError("numeric_zero_denominator")
    return _finite_float(top / bottom)


def sequential_sum(values: Iterable[object]) -> float:
    total = 0.0
    for value in values:
        total = binary64_add(total, value)
    return canonicalize_zero(total)


def sequential_mean(values: Sequence[object] | Iterable[object]) -> float:
    materialized = list(values)
    if not materialized:
        raise CanonicalError("numeric_empty_mean")
    return binary64_divide(sequential_sum(materialized), float(len(materialized)))


def ordered_logsumexp(values: Sequence[object] | Iterable[object]) -> float:
    ordered = [_finite_float(value) for value in values]
    if not ordered:
        raise CanonicalError("numeric_empty_logsumexp")
    maximum = max(ordered)
    total = 0.0
    for value in ordered:
        shifted = _finite_float(value - maximum)
        total = binary64_add(total, _finite_float(math.exp(shifted)))
    return _finite_float(maximum + math.log(total))


def ordered_softmax(
    scores: Sequence[object],
    temperature: object,
    *,
    accumulation_order: Sequence[int] | None = None,
) -> tuple[list[float], float, float, list[float]]:
    """Compute display-order numerators/weights with a separate sum order."""

    if not scores:
        raise CanonicalError("numeric_empty_softmax")
    temp = _finite_float(temperature)
    if temp <= 0.0:
        raise CanonicalError("numeric_invalid_temperature")
    scaled = [binary64_divide(score, temp) for score in scores]
    maximum = max(scaled)
    numerators = [_finite_float(math.exp(_finite_float(value - maximum))) for value in scaled]
    if accumulation_order is None:
        order = list(range(len(numerators)))
    else:
        order = list(accumulation_order)
        if sorted(order) != list(range(len(numerators))):
            raise CanonicalError("numeric_invalid_accumulation_order")
    denominator = sequential_sum(numerators[index] for index in order)
    if denominator <= 0.0:
        raise CanonicalError("numeric_invalid_softmax_denominator")
    weights = [binary64_divide(value, denominator) for value in numerators]
    return numerators, denominator, canonicalize_zero(maximum), weights


__all__ = [
    "NEGATIVE_ZERO_BITS",
    "POSITIVE_ZERO_BITS",
    "binary64_add",
    "binary64_divide",
    "canonicalize_zero",
    "f64_bits_to_float",
    "float_to_f64_bits",
    "ordered_logsumexp",
    "ordered_softmax",
    "sequential_mean",
    "sequential_sum",
]
