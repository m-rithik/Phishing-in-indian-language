"""Tests for whole-word transliteration candidate generation."""

import math

import pytest

from fisher_transliteration.candidates import (
    Candidate,
    CandidateConfig,
    generate_candidates,
)


def _texts(candidates, limit=None):
    return [c.text for c in candidates[:limit]]


def test_jaldi_hindi_top5_contains_whole_word():
    candidates = generate_candidates("jaldi", CandidateConfig(language="hindi"))
    assert "जल्दी" in _texts(candidates, 5)


def test_otp_hindi_top_non_romanized_is_lexicon_word():
    candidates = generate_candidates("otp", CandidateConfig(language="hindi"))
    top = next(c for c in candidates if c.script != "romanized")
    assert top.text == "ओटीपी"


@pytest.mark.parametrize("language", ["hindi", "tamil", "telugu"])
@pytest.mark.parametrize("word", ["jaldi", "otp", "turant", "ventane"])
def test_every_candidate_is_a_whole_word(language, word):
    candidates = generate_candidates(word, CandidateConfig(language=language))
    assert candidates
    assert all(len(c.text) > 1 for c in candidates)


@pytest.mark.parametrize("language", ["hindi", "tamil", "telugu"])
@pytest.mark.parametrize("word", ["jaldi", "otp", "send otp now"])
def test_confidences_sum_to_one(language, word):
    candidates = generate_candidates(word, CandidateConfig(language=language))
    assert math.isclose(sum(c.confidence for c in candidates), 1.0, abs_tol=1e-9)


def test_password_tamil_whole_word():
    candidates = generate_candidates("password", CandidateConfig(language="tamil"))
    assert "கடவுச்சொல்" in _texts(candidates)


def test_only_requested_script_plus_romanized():
    candidates = generate_candidates("jaldi", CandidateConfig(language="tamil"))
    assert {c.script for c in candidates} <= {"tamil", "romanized"}


def test_romanized_can_be_excluded():
    config = CandidateConfig(language="hindi", include_romanized=False)
    candidates = generate_candidates("otp", config)
    assert candidates and all(c.script == "hindi" for c in candidates)


def test_max_candidates_respected_and_sorted():
    candidates = generate_candidates("jaldi", CandidateConfig(max_candidates=3))
    assert len(candidates) <= 3
    confidences = [c.confidence for c in candidates]
    assert confidences == sorted(confidences, reverse=True)


def test_case_insensitive_and_deterministic():
    assert generate_candidates("OTP") == generate_candidates("otp")
    assert generate_candidates("jaldi") == generate_candidates("jaldi")


def test_empty_and_invalid_input():
    assert generate_candidates("") == []
    assert generate_candidates("   ") == []
    assert generate_candidates(None) == []


def test_unknown_language_is_rejected():
    with pytest.raises(ValueError):
        generate_candidates("otp", CandidateConfig(language="klingon"))


def test_candidate_is_frozen_dataclass():
    candidate = Candidate("x", "hindi", 1.0)
    with pytest.raises(Exception):
        candidate.text = "y"
