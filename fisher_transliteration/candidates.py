"""Transliteration candidate generation for ambiguous Romanized Indic text.

This module generates whole-word Indic interpretations from Romanized input,
enabling multi-candidate aggregation for more robust phishing detection.

Key concept: A user typing "OTP" in a chat may intend:
  - English "OTP" (one-time password)
  - Hindi ओटीपी
  - Tamil ஓடிபி
  - Telugu ఓటీపీ

Each word is tokenized by greedy longest match into romanized units, composed
into syllables (consonant + matra, virama for clusters, independent vowels at
word start), and the ambiguous choices are explored with a beam search. Path
scores are products of rule probabilities; the returned confidences are
normalized to sum to 1 so they can be aggregated as probabilities.
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from .rules import LanguageRules, load_romanization_rules

BEAM_WIDTH = 16
MAX_TOKEN_LENGTH = 8  # long enough for "password"
LEXICON_WEIGHT = 2.0  # whole-word sensitive terms outrank composed spellings
ROMANIZED_PRIOR = 0.3  # prior mass kept for the untouched romanized text

_WORD_RE = re.compile(r"([a-z]+)")
# Hindi (Devanagari), Tamil and Telugu blocks: input containing any of these
# characters is already (partly) in native script.
_NATIVE_RE = re.compile("[\u0900-\u097f\u0b80-\u0bff\u0c00-\u0c7f]")
# Stop-consonant units that make a preceding n or m render as an anusvara.
_ANUSVARA_NASALS = frozenset({"n", "m"})
_ANUSVARA_STOPS = frozenset({"t", "d", "k", "g", "p", "b", "j", "c"})


@dataclass(frozen=True)
class Candidate:
    """A single transliteration hypothesis."""
    text: str
    script: str  # "hindi", "tamil", "telugu", "romanized", or "native"
    confidence: float
    source_rule: Optional[str] = None
    ambiguous: bool = False


@dataclass(frozen=True)
class CandidateConfig:
    """Configuration for candidate generation.

    ``min_confidence`` filters candidates by raw (pre-normalization) score.
    """
    max_candidates: int = 8
    min_confidence: float = 0.0
    include_romanized: bool = True
    language: str = "hindi"  # "hindi" | "tamil" | "telugu"


# A search state: (text so far, probability, pending consonant, branched)
_State = Tuple[str, float, bool, bool]


class CandidateGenerator:
    """Generates transliteration candidates from Romanized Indic text."""

    def __init__(self, config: Optional[CandidateConfig] = None):
        self.config = config or CandidateConfig()
        all_rules = load_romanization_rules()
        if self.config.language not in all_rules:
            raise ValueError(
                f"Unsupported language {self.config.language!r}; "
                f"expected one of {sorted(all_rules)}"
            )
        self.rules: LanguageRules = all_rules[self.config.language]

    def generate(self, text: str) -> List[Candidate]:
        """Generate whole-word candidates, sorted by confidence (descending).

        Args:
            text: Romanized input (e.g., "otp", "jaldi", "send otp")

        Returns:
            Candidates whose confidences sum to 1.0 (empty list for empty input).
        """
        if not text or not isinstance(text, str):
            return []

        normalized = text.lower().strip()
        if not normalized:
            return []

        scored: List[Candidate] = []
        # Input that already contains native-script characters is not romanized.
        original_script = "native" if _NATIVE_RE.search(normalized) else "romanized"
        if self.config.include_romanized:
            scored.append(
                Candidate(normalized, original_script, ROMANIZED_PRIOR, "original")
            )

        language = self.config.language
        for composed_text, score, source, ambiguous in self._transliterate(normalized):
            if self.config.include_romanized and composed_text == normalized:
                continue  # nothing was transliterated; the original already covers it
            if language == "hindi" and composed_text.endswith(self.rules.virama):
                continue
            scored.append(Candidate(composed_text, language, score, source, ambiguous))

        scored = [c for c in scored if c.confidence >= self.config.min_confidence]
        scored.sort(key=lambda c: (-c.confidence, c.ambiguous, c.text))

        seen = set()
        top: List[Candidate] = []
        for candidate in scored:
            key = (candidate.text, candidate.script)
            if key in seen:
                continue
            seen.add(key)
            top.append(candidate)
            if len(top) >= self.config.max_candidates:
                break

        total = sum(c.confidence for c in top)
        if total <= 0:
            return []
        return [
            Candidate(c.text, c.script, c.confidence / total, c.source_rule, c.ambiguous)
            for c in top
        ]

    def _transliterate(self, text: str) -> List[Tuple[str, float, str, bool]]:
        """Return (text, score, source_rule, ambiguous) for the whole input."""
        # Sequence of (text, score, ambiguous) hypotheses, built word by word.
        sequence: List[Tuple[str, float, bool]] = [("", 1.0, False)]
        for piece in _WORD_RE.split(text):
            if piece == "":
                continue
            if _WORD_RE.fullmatch(piece):
                words = self._transliterate_word(piece)
            else:
                words = [(piece, 1.0, False, "literal")]
            sequence = self._extend(sequence, words)

        return [(t, p, "transliteration", a) for t, p, a in sequence]

    @staticmethod
    def _extend(
        sequence: List[Tuple[str, float, bool]],
        words: List[Tuple[str, float, bool, str]],
    ) -> List[Tuple[str, float, bool]]:
        combined = [
            (prefix + word_text, prefix_p * word_p, prefix_amb or word_amb)
            for prefix, prefix_p, prefix_amb in sequence
            for word_text, word_p, word_amb, _ in words
        ]
        combined.sort(key=lambda item: (-item[1], item[0]))
        return combined[:BEAM_WIDTH]

    def _transliterate_word(self, word: str) -> List[Tuple[str, float, bool, str]]:
        """Return (text, score, ambiguous, source) hypotheses for one word."""
        results: Dict[str, Tuple[float, bool, str]] = {}

        lexical = self.rules.lexicon.get(word)
        if lexical is not None:
            results[lexical] = (LEXICON_WEIGHT, False, "lexicon")

        for text, score, ambiguous in self._compose(self._tokenize(word)):
            if text in results:
                prior, prior_amb, source = results[text]
                results[text] = (prior + score, prior_amb, source)
            else:
                results[text] = (score, ambiguous, "composed")

        ranked = sorted(results.items(), key=lambda item: (-item[1][0], item[0]))
        return [(t, s, a, src) for t, (s, a, src) in ranked[:BEAM_WIDTH]]

    def _tokenize(self, word: str) -> List[str]:
        """Greedy longest-match tokenization into romanized units."""
        units = set(self.rules.consonants) | set(self.rules.vowels)
        tokens: List[str] = []
        i = 0
        while i < len(word):
            for length in range(min(MAX_TOKEN_LENGTH, len(word) - i), 0, -1):
                piece = word[i : i + length]
                if piece in units:
                    tokens.append(piece)
                    i += length
                    break
            else:
                tokens.append(word[i])  # unknown letter passes through unchanged
                i += 1
        return tokens

    def _compose(self, tokens: List[str]) -> List[Tuple[str, float, bool]]:
        """Beam-search syllable composition over the romanized units."""
        rules = self.rules
        states: List[_State] = [("", 1.0, False, False)]
        last = len(tokens) - 1

        for index, token in enumerate(tokens):
            is_final = index == last
            next_states: List[_State] = []
            for text, prob, pending, branched in states:
                if token in rules.consonants:
                    base_text, base_branched = text, branched
                    base_prob = prob
                    if (
                        rules.anusvara
                        and not pending
                        and text
                        and token in _ANUSVARA_NASALS
                        and index < last
                        and tokens[index + 1] in _ANUSVARA_STOPS
                    ):
                        # n/m after a vowel and before a stop: extra branch that
                        # writes the nasal mark instead of the nasal consonant.
                        next_states.append(
                            (text + rules.anusvara, prob * rules.p_anusvara, False, True)
                        )
                        base_prob = prob * (1.0 - rules.p_anusvara)
                        base_branched = True
                    if pending:
                        # consonant directly after consonant: virama or inherent
                        for mark, p in (
                            (rules.virama, rules.p_virama_before_consonant),
                            ("", 1.0 - rules.p_virama_before_consonant),
                        ):
                            for char, cp in rules.consonants[token]:
                                next_states.append(
                                    (base_text + mark + char, base_prob * p * cp, True, True)
                                )
                    else:
                        for char, cp in rules.consonants[token]:
                            next_states.append(
                                (base_text + char, base_prob * cp, True,
                                 base_branched or cp < 1.0)
                            )
                elif token in rules.vowels:
                    for form in rules.vowels[token]:
                        p = form.p_final if is_final else form.p_medial
                        if p <= 0.0:
                            continue
                        mark = form.matra if pending else form.independent
                        alt = branched or len(rules.vowels[token]) > 1
                        next_states.append((text + mark, prob * p, False, alt))
                else:
                    # unknown character: resolve a pending consonant, pass through
                    next_states.append((text + token, prob, False, branched))
            next_states.sort(key=lambda s: (-s[1], s[0]))
            states = next_states[:BEAM_WIDTH]

        finished: List[Tuple[str, float, bool]] = []
        for text, prob, pending, branched in states:
            if pending:
                # word-final consonant: virama or inherent vowel
                finished.append((text + rules.virama, prob * rules.p_virama_final, True))
                finished.append((text, prob * (1.0 - rules.p_virama_final), True))
            else:
                finished.append((text, prob, branched))
        finished.sort(key=lambda item: (-item[1], item[0]))
        return finished[:BEAM_WIDTH]


def generate_candidates(
    text: str, config: Optional[CandidateConfig] = None
) -> List[Candidate]:
    """Convenience function to generate candidates without instantiating generator.

    Args:
        text: Romanized input
        config: Optional CandidateConfig

    Returns:
        List of Candidate objects
    """
    gen = CandidateGenerator(config)
    return gen.generate(text)
