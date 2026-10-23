"""Romanization rules for Hindi (Devanagari), Tamil, and Telugu scripts.

Rules are split into the pieces needed to compose whole syllables:

* consonants: romanized unit -> alternative base characters with probabilities,
* vowels: romanized unit -> alternative (independent form, dependent matra) pairs,
* virama: the vowel-killer mark of the script,
* lexicon: whole-word renderings for sensitive terms (otp, password, ...).

For every romanized unit the alternative probabilities sum to 1.

Sources:
- Hindi: ITRANS, Harvard-Kyoto, modified Romanization (user-generated text)
- Tamil: Transliteration conventions in SMS/chat (no official standard)
- Telugu: Informal Romanization patterns
"""

from dataclasses import dataclass
from typing import Dict, Tuple


@dataclass(frozen=True)
class VowelForm:
    """One rendering of a romanized vowel unit.

    ``matra`` is the dependent sign used after a consonant; the empty string is
    the inherent vowel (no mark). ``p_medial`` and ``p_final`` are the
    probabilities of this form inside a word and at the end of a word.
    """

    independent: str
    matra: str
    p_medial: float = 1.0
    p_final: float = 1.0


@dataclass(frozen=True)
class LanguageRules:
    """All composition rules for a single script."""

    consonants: Dict[str, Tuple[Tuple[str, float], ...]]
    vowels: Dict[str, Tuple[VowelForm, ...]]
    virama: str
    lexicon: Dict[str, str]
    # Probability of a virama (vs. the inherent vowel) after a consonant that
    # is followed directly by another consonant, and at the end of a word.
    p_virama_before_consonant: float = 0.6
    p_virama_final: float = 0.4


def _c(*pairs: Tuple[str, float]) -> Tuple[Tuple[str, float], ...]:
    return tuple(pairs)


def _single(char: str) -> Tuple[Tuple[str, float], ...]:
    return ((char, 1.0),)


def _short_long(short: Tuple[str, str], long: Tuple[str, str]) -> Tuple[VowelForm, ...]:
    """Short/long pair; the long form is favoured at the end of a word."""
    return (
        VowelForm(short[0], short[1], p_medial=0.7, p_final=0.3),
        VowelForm(long[0], long[1], p_medial=0.3, p_final=0.7),
    )


def _even(first: Tuple[str, str], second: Tuple[str, str]) -> Tuple[VowelForm, ...]:
    return (
        VowelForm(first[0], first[1], 0.5, 0.5),
        VowelForm(second[0], second[1], 0.5, 0.5),
    )


def _one(independent: str, matra: str) -> Tuple[VowelForm, ...]:
    return (VowelForm(independent, matra),)


HINDI = LanguageRules(
    consonants={
        "k": _single("क"), "kh": _single("ख"), "q": _single("क"), "c": _single("क"),
        "g": _single("ग"), "gh": _single("घ"), "ng": _single("ङ"),
        "ch": _c(("च", 0.7), ("छ", 0.3)), "chh": _single("छ"),
        "j": _single("ज"), "jh": _single("झ"), "z": _single("ज"), "ny": _single("ञ"),
        "t": _c(("त", 0.6), ("ट", 0.4)), "th": _c(("थ", 0.6), ("ठ", 0.4)),
        "d": _c(("द", 0.6), ("ड", 0.4)), "dh": _c(("ध", 0.6), ("ढ", 0.4)),
        "tt": _single("ट"), "tth": _single("ठ"), "dd": _single("ड"), "ddh": _single("ढ"),
        "n": _single("न"), "nn": _single("ण"),
        "p": _single("प"), "ph": _single("फ"), "f": _single("फ"),
        "b": _single("ब"), "bh": _single("भ"), "m": _single("म"),
        "y": _single("य"), "r": _single("र"), "l": _single("ल"),
        "v": _single("व"), "w": _single("व"),
        "sh": _single("श"), "s": _single("स"), "h": _single("ह"),
    },
    vowels={
        "a": _one("अ", ""), "aa": _one("आ", "ा"),
        "i": _short_long(("इ", "ि"), ("ई", "ी")), "ii": _one("ई", "ी"), "ee": _one("ई", "ी"),
        "u": _short_long(("उ", "ु"), ("ऊ", "ू")), "uu": _one("ऊ", "ू"), "oo": _one("ऊ", "ू"),
        "e": _one("ए", "े"), "ai": _one("ऐ", "ै"),
        "o": _one("ओ", "ो"), "au": _one("औ", "ौ"),
    },
    virama="्",
    lexicon={
        "otp": "ओटीपी", "pwd": "पीडब्लू", "pass": "पास",
        "pin": "पिन", "cvv": "सीवीवी", "kyc": "केवाईसी",
    },
    p_virama_final=0.4,
)

TAMIL = LanguageRules(
    consonants={
        "k": _single("க"), "kh": _single("க"), "g": _single("க"), "gh": _single("க"),
        "q": _single("க"),
        "c": _single("ச"), "ch": _single("ச"), "s": _single("ச"),
        "j": _single("ஜ"), "jh": _single("ஜ"), "z": _single("ஜ"),
        "t": _single("த"), "th": _single("த"), "d": _single("த"), "dh": _single("த"),
        "n": _single("ன"), "p": _single("ப"), "ph": _single("ப"), "b": _single("ப"),
        "bh": _single("ப"), "f": _single("ஃப"), "m": _single("ம"),
        "y": _single("ய"), "r": _single("ர"), "l": _single("ல"), "ll": _single("ள"),
        "v": _single("வ"), "w": _single("வ"), "sh": _single("ஷ"), "h": _single("ஹ"),
    },
    vowels={
        "a": _one("அ", ""), "aa": _one("ஆ", "ா"),
        "i": _short_long(("இ", "ி"), ("ஈ", "ீ")), "ii": _one("ஈ", "ீ"),
        "u": _short_long(("உ", "ு"), ("ஊ", "ூ")), "uu": _one("ஊ", "ூ"),
        "e": _even(("எ", "ெ"), ("ஏ", "ே")), "ee": _one("ஏ", "ே"),
        "ai": _one("ஐ", "ை"),
        "o": _even(("ஒ", "ொ"), ("ஓ", "ோ")), "oo": _one("ஓ", "ோ"),
        "ou": _one("ஔ", "ௌ"), "au": _one("ஔ", "ௌ"),
    },
    virama="்",
    lexicon={
        "otp": "ஓடிபி", "password": "கடவுச்சொல்", "pin": "பின்",
        "cvv": "சிவிவி", "kyc": "கேவைசி",
    },
    p_virama_final=0.6,
)

TELUGU = LanguageRules(
    consonants={
        "k": _single("క"), "kh": _single("ఖ"), "q": _single("క"),
        "g": _single("గ"), "gh": _single("ఘ"), "ng": _single("ఙ"),
        "c": _single("చ"), "ch": _single("చ"),
        "j": _single("జ"), "jh": _single("ఝ"), "z": _single("జ"), "ny": _single("ఞ"),
        "t": _single("త"), "th": _single("థ"), "d": _single("ద"), "dh": _single("ధ"),
        "n": _single("న"), "p": _single("ప"), "ph": _single("ఫ"), "f": _single("ఫ"),
        "b": _single("బ"), "bh": _single("భ"), "m": _single("మ"),
        "y": _single("య"), "r": _single("ర"), "l": _single("ల"),
        "v": _single("వ"), "w": _single("వ"),
        "sh": _single("శ"), "s": _single("స"), "h": _single("హ"),
    },
    vowels={
        "a": _one("అ", ""), "aa": _one("ఆ", "ా"),
        "i": _short_long(("ఇ", "ి"), ("ఈ", "ీ")), "ii": _one("ఈ", "ీ"),
        "u": _short_long(("ఉ", "ు"), ("ఊ", "ూ")), "uu": _one("ఊ", "ూ"),
        "e": _even(("ఎ", "ె"), ("ఏ", "ే")), "ee": _one("ఏ", "ే"),
        "ai": _one("ఐ", "ై"),
        "o": _even(("ఒ", "ొ"), ("ఓ", "ో")), "oo": _one("ఓ", "ో"),
        "ou": _one("ఔ", "ౌ"), "au": _one("ఔ", "ౌ"),
    },
    virama="్",
    lexicon={
        "otp": "ఓటీపీ", "password": "పాస్‌వర్డ్", "pin": "పిన్",
        "cvv": "సీవీవీ", "kyc": "కేవైసీ",
    },
    p_virama_final=0.6,
)


def load_romanization_rules() -> Dict[str, LanguageRules]:
    """Load all romanization rules by language."""
    return {
        "hindi": HINDI,
        "tamil": TAMIL,
        "telugu": TELUGU,
    }
