"""Tests for whole-word transliteration candidate generation."""

import dataclasses
import math

import pytest

from fisher_transliteration.candidates import (
    Candidate,
    CandidateConfig,
    CandidateGenerator,
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


def _composed_only(word, language, max_candidates=20):
    """Candidates produced by the composition rules alone (lexicon disabled)."""
    generator = CandidateGenerator(CandidateConfig(language=language, max_candidates=max_candidates))
    generator.rules = dataclasses.replace(generator.rules, lexicon={})
    return generator.generate(word)


@pytest.mark.parametrize(
    ("word", "language", "expected"),
    [
        ("udane", "tamil", "உடனே"),
        ("ventane", "telugu", "వెంటనే"),
        ("pampandi", "telugu", "పంపండి"),
        ("password", "hindi", "पासवर्ड"),
    ],
)
def test_scam_vocabulary_in_default_candidates(word, language, expected):
    candidates = generate_candidates(word, CandidateConfig(language=language))
    assert expected in _texts(candidates)


@pytest.mark.parametrize(
    ("word", "language", "expected"),
    [
        ("udane", "tamil", "உடனே"),
        ("ventane", "telugu", "వెంటనే"),
        ("pampandi", "telugu", "పంపండి"),
    ],
)
def test_composition_rules_alone_reach_the_correct_spelling(word, language, expected):
    assert expected in _texts(_composed_only(word, language))


@pytest.mark.parametrize("language", ["hindi", "tamil", "telugu"])
@pytest.mark.parametrize(
    "word",
    ["udane", "anuppunga", "pampandi", "ventane", "turant", "jaldi", "bhejo", "password", "otp", "pin", "kyc"],
)
def test_scam_lexicon_has_every_word_and_confidences_sum_to_one(language, word):
    rules = CandidateGenerator(CandidateConfig(language=language)).rules
    assert word in rules.lexicon
    candidates = generate_candidates(word, CandidateConfig(language=language))
    assert rules.lexicon[word] in _texts(candidates)
    assert math.isclose(sum(c.confidence for c in candidates), 1.0, abs_tol=1e-9)


@pytest.mark.parametrize(
    ("language", "dental", "retroflex"),
    [("tamil", "த", "ட"), ("telugu", "త", "ట")],
)
def test_t_has_dental_and_retroflex_alternatives(language, dental, retroflex):
    candidates = _composed_only("ata", language)
    by_text = {c.text: c.confidence for c in candidates}
    dental_text = next(t for t in by_text if t.endswith(dental))
    retroflex_text = next(t for t in by_text if t.endswith(retroflex))
    assert math.isclose(by_text[dental_text], by_text[retroflex_text], rel_tol=1e-9)


def test_d_has_retroflex_alternative_in_telugu_and_tamil():
    assert any("డ" in t for t in _texts(_composed_only("ada", "telugu")))
    assert any("ட" in t for t in _texts(_composed_only("ada", "tamil")))


@pytest.mark.parametrize(
    ("word", "language", "expected"),
    [
        ("canta", "hindi", "कंत"),
        ("kampa", "hindi", "कंप"),
        ("kanta", "telugu", "కంత"),
        ("kampa", "telugu", "కంప"),
        ("anga", "tamil", "அங்க"),
    ],
)
def test_nasal_before_a_stop_can_render_as_the_nasal_mark(word, language, expected):
    assert any(expected in t for t in _texts(_composed_only(word, language)))


def test_nasal_mark_is_an_extra_branch_not_a_replacement():
    texts = _texts(_composed_only("kanta", "telugu"))
    assert any("ం" in t for t in texts)
    assert any("న" in t for t in texts)


def test_nasal_mark_needs_a_preceding_vowel_and_a_following_stop():
    assert not any("ం" in t for t in _texts(_composed_only("kana", "telugu")))
    assert not any("ं" in t for t in _texts(_composed_only("nta", "hindi")))


@pytest.mark.parametrize("language", ["hindi", "tamil", "telugu"])
def test_native_script_input_is_labelled_native_not_romanized(language):
    candidates = generate_candidates("ओटीपी भेजें", CandidateConfig(language=language))
    assert candidates
    assert {c.script for c in candidates} == {"native"}
    assert math.isclose(sum(c.confidence for c in candidates), 1.0, abs_tol=1e-9)


def test_mixed_native_and_latin_input_keeps_native_label_on_original():
    candidates = generate_candidates("ओटीपी send", CandidateConfig(language="hindi"))
    original = next(c for c in candidates if c.source_rule == "original")
    assert original.script == "native"
    assert not any(c.script == "romanized" for c in candidates)
