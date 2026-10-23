"""Transliteration candidate generation for Indic scripts (Hindi, Tamil, Telugu)."""

from .candidates import generate_candidates, CandidateConfig
from .rules import load_romanization_rules

__version__ = "0.1.0"
__all__ = ["generate_candidates", "CandidateConfig", "load_romanization_rules"]
