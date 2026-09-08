"""Synthetic-only rehearsal for Fisher's frozen human-audit selector."""

from .selector import (
    ALGORITHM_VERSION,
    SCOPE,
    Attempt,
    Diagnostic,
    RehearsalReport,
    allocate_hamilton,
    format_json,
    format_text,
    hmac_rank_digest,
    rehearse_file,
)

__all__ = [
    "ALGORITHM_VERSION",
    "SCOPE",
    "Attempt",
    "Diagnostic",
    "RehearsalReport",
    "allocate_hamilton",
    "format_json",
    "format_text",
    "hmac_rank_digest",
    "rehearse_file",
]
