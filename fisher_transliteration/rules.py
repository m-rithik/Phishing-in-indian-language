"""Romanization rules for Hindi (Devanagari), Tamil, and Telugu scripts.

This module encodes common Romanization patterns used to write Indic scripts in Latin characters.
Each pattern is weighted by frequency to prioritize likely interpretations.

Sources:
- Hindi: ITRANS, Harvard-Kyoto, modified Romanization (user-generated text)
- Tamil: Transliteration conventions in SMS/chat (no official standard)
- Telugu: Informal Romanization patterns
"""

from dataclasses import dataclass
from typing import Dict, List, Tuple

@dataclass(frozen=True)
class RomanizationRule:
    """A single romanization pattern mapping."""
    romanized: str
    scripts: Dict[str, str]  # script -> character mapping
    weight: float = 1.0
    ambiguous: bool = False  # True if multiple interpretations are equally valid

# Hindi (Devanagari) romanization rules
# Ordered by likelihood in authentic text
HINDI_RULES: List[RomanizationRule] = [
    # Vowels (highest priority)
    RomanizationRule("a", {"devanagari": "अ"}, weight=2.0),
    RomanizationRule("aa", {"devanagari": "आ"}, weight=1.8),
    RomanizationRule("aaa", {"devanagari": "आ"}, weight=0.3, ambiguous=True),
    RomanizationRule("i", {"devanagari": "इ"}, weight=1.8),
    RomanizationRule("ii", {"devanagari": "ई"}, weight=1.8),
    RomanizationRule("u", {"devanagari": "उ"}, weight=1.8),
    RomanizationRule("uu", {"devanagari": "ऊ"}, weight=1.8),
    RomanizationRule("oo", {"devanagari": "ऊ"}, weight=0.5, ambiguous=True),
    RomanizationRule("e", {"devanagari": "ए"}, weight=1.5),
    RomanizationRule("ai", {"devanagari": "ऐ"}, weight=1.2),
    RomanizationRule("o", {"devanagari": "ओ"}, weight=1.5),
    RomanizationRule("au", {"devanagari": "औ"}, weight=1.2),

    # Common consonants
    RomanizationRule("k", {"devanagari": "क"}, weight=1.8),
    RomanizationRule("kh", {"devanagari": "ख"}, weight=1.5),
    RomanizationRule("g", {"devanagari": "ग"}, weight=1.8),
    RomanizationRule("gh", {"devanagari": "घ"}, weight=1.2),
    RomanizationRule("ng", {"devanagari": "ङ"}, weight=0.8),
    RomanizationRule("ch", {"devanagari": "छ"}, weight=1.8),
    RomanizationRule("chh", {"devanagari": "छ"}, weight=0.5, ambiguous=True),
    RomanizationRule("j", {"devanagari": "ज"}, weight=1.8),
    RomanizationRule("jh", {"devanagari": "झ"}, weight=1.2),
    RomanizationRule("ny", {"devanagari": "ञ"}, weight=1.0),
    RomanizationRule("t", {"devanagari": "त"}, weight=1.8),
    RomanizationRule("th", {"devanagari": "थ"}, weight=1.5),
    RomanizationRule("d", {"devanagari": "द"}, weight=1.8),
    RomanizationRule("dh", {"devanagari": "ध"}, weight=1.2),
    RomanizationRule("n", {"devanagari": "न"}, weight=1.8),
    RomanizationRule("p", {"devanagari": "प"}, weight=1.8),
    RomanizationRule("ph", {"devanagari": "फ"}, weight=1.5),
    RomanizationRule("b", {"devanagari": "ब"}, weight=1.8),
    RomanizationRule("bh", {"devanagari": "भ"}, weight=1.2),
    RomanizationRule("m", {"devanagari": "म"}, weight=1.8),
    RomanizationRule("y", {"devanagari": "य"}, weight=1.8),
    RomanizationRule("r", {"devanagari": "र"}, weight=1.8),
    RomanizationRule("l", {"devanagari": "ल"}, weight=1.8),
    RomanizationRule("v", {"devanagari": "व"}, weight=1.5),
    RomanizationRule("w", {"devanagari": "व"}, weight=1.0, ambiguous=True),
    RomanizationRule("sh", {"devanagari": "श"}, weight=1.5),
    RomanizationRule("s", {"devanagari": "स"}, weight=1.8),
    RomanizationRule("h", {"devanagari": "ह"}, weight=1.8),

    # Retroflex consonants (less common in casual text)
    RomanizationRule("tt", {"devanagari": "ट"}, weight=0.8),
    RomanizationRule("tth", {"devanagari": "ठ"}, weight=0.5),
    RomanizationRule("dd", {"devanagari": "ड"}, weight=0.8),
    RomanizationRule("ddh", {"devanagari": "ढ"}, weight=0.5),
    RomanizationRule("nn", {"devanagari": "ण"}, weight=0.5),

    # Sensitive term patterns (phishing detection context)
    RomanizationRule("otp", {"devanagari": "ओटीपी"}, weight=2.5),
    RomanizationRule("pwd", {"devanagari": "पीडब्लू"}, weight=0.8, ambiguous=True),
    RomanizationRule("pass", {"devanagari": "पास"}, weight=1.5),
    RomanizationRule("pin", {"devanagari": "पिन"}, weight=1.5),
    RomanizationRule("cvv", {"devanagari": "सीवीवी"}, weight=1.8),
    RomanizationRule("kyc", {"devanagari": "केवाईसी"}, weight=1.8),
]

# Tamil romanization rules
TAMIL_RULES: List[RomanizationRule] = [
    # Vowels
    RomanizationRule("a", {"tamil": "அ"}, weight=2.0),
    RomanizationRule("aa", {"tamil": "ஆ"}, weight=1.8),
    RomanizationRule("i", {"tamil": "இ"}, weight=1.8),
    RomanizationRule("ii", {"tamil": "ஈ"}, weight=1.8),
    RomanizationRule("u", {"tamil": "உ"}, weight=1.8),
    RomanizationRule("uu", {"tamil": "ஊ"}, weight=1.8),
    RomanizationRule("e", {"tamil": "எ"}, weight=1.5),
    RomanizationRule("ee", {"tamil": "ஏ"}, weight=1.5),
    RomanizationRule("ai", {"tamil": "ஐ"}, weight=1.2),
    RomanizationRule("o", {"tamil": "ஒ"}, weight=1.5),
    RomanizationRule("oo", {"tamil": "ஓ"}, weight=1.5),
    RomanizationRule("ou", {"tamil": "ஔ"}, weight=1.2),

    # Consonants
    RomanizationRule("k", {"tamil": "க"}, weight=1.8),
    RomanizationRule("kh", {"tamil": "க"}, weight=0.5, ambiguous=True),
    RomanizationRule("g", {"tamil": "க"}, weight=1.0, ambiguous=True),
    RomanizationRule("c", {"tamil": "ச"}, weight=1.8),
    RomanizationRule("ch", {"tamil": "ச"}, weight=0.5, ambiguous=True),
    RomanizationRule("j", {"tamil": "ஜ"}, weight=1.5),
    RomanizationRule("jh", {"tamil": "ஜ"}, weight=0.3, ambiguous=True),
    RomanizationRule("t", {"tamil": "த"}, weight=1.8),
    RomanizationRule("th", {"tamil": "த"}, weight=0.5, ambiguous=True),
    RomanizationRule("d", {"tamil": "த"}, weight=1.0, ambiguous=True),
    RomanizationRule("n", {"tamil": "ன"}, weight=1.8),
    RomanizationRule("p", {"tamil": "ப"}, weight=1.8),
    RomanizationRule("ph", {"tamil": "ப"}, weight=0.5, ambiguous=True),
    RomanizationRule("b", {"tamil": "ப"}, weight=1.0, ambiguous=True),
    RomanizationRule("m", {"tamil": "ம"}, weight=1.8),
    RomanizationRule("y", {"tamil": "ய"}, weight=1.8),
    RomanizationRule("r", {"tamil": "ர"}, weight=1.8),
    RomanizationRule("l", {"tamil": "ல"}, weight=1.8),
    RomanizationRule("ll", {"tamil": "ள"}, weight=1.5),
    RomanizationRule("v", {"tamil": "வ"}, weight=1.5),
    RomanizationRule("w", {"tamil": "வ"}, weight=1.0, ambiguous=True),
    RomanizationRule("sh", {"tamil": "ஷ"}, weight=1.3),
    RomanizationRule("s", {"tamil": "ச"}, weight=1.8),
    RomanizationRule("h", {"tamil": "ஹ"}, weight=1.8),

    # Sensitive terms
    RomanizationRule("otp", {"tamil": "ஓடிபி"}, weight=2.5),
    RomanizationRule("password", {"tamil": "கடவுச்சொல்"}, weight=2.0),
    RomanizationRule("pin", {"tamil": "பின்"}, weight=1.5),
    RomanizationRule("cvv", {"tamil": "சிவிவி"}, weight=1.8),
    RomanizationRule("kyc", {"tamil": "கேவைசி"}, weight=1.8),
]

# Telugu romanization rules
TELUGU_RULES: List[RomanizationRule] = [
    # Vowels
    RomanizationRule("a", {"telugu": "అ"}, weight=2.0),
    RomanizationRule("aa", {"telugu": "ఆ"}, weight=1.8),
    RomanizationRule("i", {"telugu": "ఇ"}, weight=1.8),
    RomanizationRule("ii", {"telugu": "ఈ"}, weight=1.8),
    RomanizationRule("u", {"telugu": "ఉ"}, weight=1.8),
    RomanizationRule("uu", {"telugu": "ఊ"}, weight=1.8),
    RomanizationRule("e", {"telugu": "ఎ"}, weight=1.5),
    RomanizationRule("ee", {"telugu": "ఏ"}, weight=1.5),
    RomanizationRule("ai", {"telugu": "ఐ"}, weight=1.2),
    RomanizationRule("o", {"telugu": "ఒ"}, weight=1.5),
    RomanizationRule("oo", {"telugu": "ఓ"}, weight=1.5),
    RomanizationRule("ou", {"telugu": "ఔ"}, weight=1.2),

    # Consonants
    RomanizationRule("k", {"telugu": "క"}, weight=1.8),
    RomanizationRule("kh", {"telugu": "ఖ"}, weight=1.2),
    RomanizationRule("g", {"telugu": "గ"}, weight=1.8),
    RomanizationRule("gh", {"telugu": "ఘ"}, weight=0.8),
    RomanizationRule("ng", {"telugu": "ఙ"}, weight=0.5),
    RomanizationRule("c", {"telugu": "చ"}, weight=1.8),
    RomanizationRule("ch", {"telugu": "చ"}, weight=0.5, ambiguous=True),
    RomanizationRule("j", {"telugu": "జ"}, weight=1.8),
    RomanizationRule("jh", {"telugu": "ఝ"}, weight=0.8),
    RomanizationRule("ny", {"telugu": "ఞ"}, weight=0.5),
    RomanizationRule("t", {"telugu": "త"}, weight=1.8),
    RomanizationRule("th", {"telugu": "థ"}, weight=1.2),
    RomanizationRule("d", {"telugu": "ద"}, weight=1.8),
    RomanizationRule("dh", {"telugu": "ధ"}, weight=1.0),
    RomanizationRule("n", {"telugu": "న"}, weight=1.8),
    RomanizationRule("p", {"telugu": "ప"}, weight=1.8),
    RomanizationRule("ph", {"telugu": "ఫ"}, weight=1.2),
    RomanizationRule("b", {"telugu": "బ"}, weight=1.8),
    RomanizationRule("bh", {"telugu": "భ"}, weight=1.0),
    RomanizationRule("m", {"telugu": "ము"}, weight=1.8),
    RomanizationRule("y", {"telugu": "య"}, weight=1.8),
    RomanizationRule("r", {"telugu": "ర"}, weight=1.8),
    RomanizationRule("l", {"telugu": "ల"}, weight=1.8),
    RomanizationRule("v", {"telugu": "వ"}, weight=1.5),
    RomanizationRule("w", {"telugu": "వ"}, weight=1.0, ambiguous=True),
    RomanizationRule("sh", {"telugu": "శ"}, weight=1.3),
    RomanizationRule("s", {"telugu": "స"}, weight=1.8),
    RomanizationRule("h", {"telugu": "హ"}, weight=1.8),

    # Sensitive terms
    RomanizationRule("otp", {"telugu": "ఓటీపీ"}, weight=2.5),
    RomanizationRule("password", {"telugu": "పాస్‌వర్డ్"}, weight=2.0),
    RomanizationRule("pin", {"telugu": "పిన్"}, weight=1.5),
    RomanizationRule("cvv", {"telugu": "సీవీవీ"}, weight=1.8),
    RomanizationRule("kyc", {"telugu": "కేవైసీ"}, weight=1.8),
]

def load_romanization_rules() -> Dict[str, List[RomanizationRule]]:
    """Load all romanization rules by language."""
    return {
        "hindi": HINDI_RULES,
        "tamil": TAMIL_RULES,
        "telugu": TELUGU_RULES,
    }
