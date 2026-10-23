"""Transliteration candidate generation for ambiguous Romanized Indic text.

This module generates multiple plausible Indic interpretations from Romanized input,
enabling multi-candidate aggregation for more robust phishing detection.

Key concept: A user typing "OTP" in a chat may intend:
  - English "OTP" (one-time password)
  - Hindi ओटीपी
  - Tamil ஓடிபி
  - Telugu ఓటీపీ

This module explores all candidates and weights them by frequency.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
import re
from .rules import load_romanization_rules, RomanizationRule

@dataclass(frozen=True)
class Candidate:
    """A single transliteration hypothesis."""
    text: str
    script: str  # "hindi", "tamil", "telugu", or "romanized"
    confidence: float
    source_rule: Optional[str] = None
    ambiguous: bool = False

@dataclass(frozen=True)
class CandidateConfig:
    """Configuration for candidate generation."""
    max_candidates: int = 8
    min_confidence: float = 0.3
    include_romanized: bool = True
    scripts: List[str] = ("hindi", "tamil", "telugu")

class CandidateGenerator:
    """Generates transliteration candidates from Romanized Indic text."""

    def __init__(self, config: Optional[CandidateConfig] = None):
        self.config = config or CandidateConfig()
        self.rules = load_romanization_rules()
        self._build_rule_index()

    def _build_rule_index(self) -> None:
        """Build indices for fast rule matching."""
        self.rule_index = {}  # romanized -> List[RomanizationRule]
        for script, rules in self.rules.items():
            for rule in rules:
                if rule.romanized not in self.rule_index:
                    self.rule_index[rule.romanized] = []
                self.rule_index[rule.romanized].append(rule)

    def generate(self, text: str) -> List[Candidate]:
        """Generate transliteration candidates from Romanized text.

        Strategy:
        1. Tokenize input into possible romanization units
        2. For each unit, find matching rules
        3. Combine rules to form candidate interpretations
        4. Score and rank by confidence
        5. Return top-k candidates

        Args:
            text: Romanized input (e.g., "otp", "OTP", "send otp")

        Returns:
            List of Candidate objects, sorted by confidence (descending)
        """
        if not text or not isinstance(text, str):
            return []

        # Normalize: lowercase, collapse whitespace
        normalized = text.lower().strip()
        if not normalized:
            return []

        # Always include the original romanized version
        candidates = []
        if self.config.include_romanized:
            candidates.append(
                Candidate(
                    text=normalized,
                    script="romanized",
                    confidence=1.0,
                    source_rule="original",
                )
            )

        # Generate script-specific candidates
        for script in self.config.scripts:
            script_candidates = self._generate_for_script(normalized, script)
            candidates.extend(script_candidates)

        # Sort by confidence, then by ambiguity (unambiguous first)
        candidates.sort(
            key=lambda c: (-c.confidence, c.ambiguous, c.text)
        )

        # Deduplicate and truncate
        seen = set()
        result = []
        for candidate in candidates:
            key = (candidate.text, candidate.script)
            if key not in seen and len(result) < self.config.max_candidates:
                if candidate.confidence >= self.config.min_confidence:
                    seen.add(key)
                    result.append(candidate)

        return result

    def _generate_for_script(self, text: str, script: str) -> List[Candidate]:
        """Generate candidates for a specific script."""
        candidates = []

        # Greedy longest-match tokenization
        tokens = self._tokenize(text)
        if not tokens:
            return candidates

        # Map tokens to rules
        script_rules = self.rules.get(script, [])
        if not script_rules:
            return candidates

        rule_map = {r.romanized: r for r in script_rules}

        # Single-token candidates (most common: "otp" -> "ओटीपी")
        for token in tokens:
            rule = rule_map.get(token)
            if rule and script in rule.scripts:
                candidate_text = rule.scripts[script]
                candidates.append(
                    Candidate(
                        text=candidate_text,
                        script=script,
                        confidence=rule.weight,
                        source_rule=token,
                        ambiguous=rule.ambiguous,
                    )
                )

        # Multi-token candidates (less common: "p a s s" -> "पास")
        multi_token = self._try_multitoken(tokens, rule_map, script)
        candidates.extend(multi_token)

        return candidates

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize input into romanization units.

        Tries common romanization boundaries:
        - Consonant-vowel pairs: "ch", "sh", "th", "kh", "gh", "ph", "bh"
        - Vowels: "a", "aa", "i", "ii", "u", "uu", "e", "o", etc.
        - Consonants: "k", "g", "c", "j", etc.
        - Special: "otp", "cvv", "password"
        """
        if not text:
            return []

        tokens = []
        i = 0
        # Greedy longest match
        while i < len(text):
            matched = False

            # Try 4-character patterns first (e.g., "pass")
            for length in [4, 3, 2, 1]:
                if i + length <= len(text):
                    candidate = text[i : i + length]
                    if candidate in self.rule_index:
                        tokens.append(candidate)
                        i += length
                        matched = True
                        break

            if not matched:
                # If no rule matches, consume one character and continue
                tokens.append(text[i])
                i += 1

        return tokens

    def _try_multitoken(
        self, tokens: List[str], rule_map: Dict[str, RomanizationRule], script: str
    ) -> List[Candidate]:
        """Generate candidates from multi-token combinations."""
        candidates = []

        # Only try if we have 2-4 tokens and they're short
        if len(tokens) < 2 or len(tokens) > 4 or len("".join(tokens)) > 12:
            return candidates

        # Try all contiguous substrings
        for start in range(len(tokens)):
            for end in range(start + 2, min(start + 4, len(tokens) + 1)):
                joined = "".join(tokens[start:end])
                rule = rule_map.get(joined)

                if rule and script in rule.scripts:
                    candidate_text = rule.scripts[script]
                    candidates.append(
                        Candidate(
                            text=candidate_text,
                            script=script,
                            confidence=rule.weight * 0.7,  # Discount multi-token
                            source_rule=f"multi:{joined}",
                            ambiguous=rule.ambiguous,
                        )
                    )

        return candidates


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
