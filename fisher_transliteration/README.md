# Fisher Transliteration: Multi-Candidate Generation for Indic Scripts

## Overview

`fisher_transliteration` generates whole-word Indic script interpretations from Romanized text, enabling **multi-candidate aggregation** for phishing detection across Hindi, Tamil, and Telugu.

**Key insight:** A user typing "otp" in a message might intend:
- English (romanized): `otp`
- Hindi (Devanagari): `ओटीपी`
- Tamil: `ஓடிபி`
- Telugu: `ఓటీపీ`

Rather than emitting single characters or fragmented tokens, this engine composes complete syllables (base consonants, dependent matras, inherent vowels, and viramas) and uses beam search to generate ranked, whole-word candidates with normalized probabilities.

---

## API

### `generate_candidates(text: str, config: Optional[CandidateConfig] = None) -> List[Candidate]`

Generates whole-word transliteration hypotheses from Romanized input.

**Args:**
- `text` (str): Romanized input word or phrase (e.g., "jaldi", "otp", "password")
- `config` (CandidateConfig, optional): Configuration specifying target language, max candidates, and whether to include original romanized text.

**Returns:** List of `Candidate` objects, sorted by confidence (descending), with confidences normalized to sum to 1.0.

**Example:**
```python
from fisher_transliteration import CandidateConfig, generate_candidates

config = CandidateConfig(language="hindi", max_candidates=5)
candidates = generate_candidates("jaldi", config)
for c in candidates:
    print(f"{c.script:10} {c.text:12} confidence={c.confidence:.3f}")

# Output:
# romanized  jaldi        confidence=0.240
# hindi      जल्दी        confidence=0.201
# hindi      जलदी        confidence=0.134
# hindi      जल्डी        confidence=0.134
# hindi      जलडी        confidence=0.089
```

### `CandidateConfig`

Configuration dataclass for candidate generation.

**Fields:**
- `language` (str, default="hindi"): Target Indic language (`"hindi"`, `"tamil"`, or `"telugu"`).
- `max_candidates` (int, default=8): Maximum number of top hypotheses to return.
- `min_confidence` (float, default=0.0): Minimum raw score threshold before ranking.
- `include_romanized` (bool, default=True): Whether to include the input romanized string as one candidate.

### `Candidate`

Immutable dataclass representing a single hypothesis.

**Fields:**
- `text` (str): Composed text in the target script (or original text if script is `"romanized"`).
- `script` (str): Hypothesis script (`"hindi"`, `"tamil"`, `"telugu"`, or `"romanized"`).
- `confidence` (float): Normalized probability (all candidates returned sum to 1.0 ± 1e-9).
- `source_rule` (str, optional): Origin indicator (`"transliteration"`, `"original"`, etc.).
- `ambiguous` (bool): Whether alternative interpretations branched during composition.

---

## Architecture & Syllable Composition

1. **Tokenization**: Greedy longest-match tokenization up to 8 characters to partition words into romanized consonant, vowel, and special units.
2. **Syllable Composition**:
   - Word-initial vowels map to independent vowel forms (e.g., `अ`, `இ`, `అ`).
   - Vowels following consonants attach as dependent vowel signs (**matras**, e.g., Hindi `ा`, Tamil `ா`, Telugu `ా`).
   - The vowel `a` following a consonant represents the inherent vowel (no matra attached).
   - Consonant clusters branch into explicit **virama** attachment (Hindi `्`, Tamil `்`, Telugu `్`) versus inherent vowels.
3. **Beam Search**: Evaluates candidate paths with a beam width of 16, pruning low-probability branches and scoring paths as products of transition probabilities.
4. **Lexicon Prioritization**: High-risk sensitive terms (e.g., `otp`, `password`, `cvv`, `kyc`) match whole-word lexicon entries with prior weights.
5. **Score Normalization**: Raw hypothesis scores are normalized so that returned candidate confidences sum exactly to 1.0, enabling direct use in probability-weighted aggregations.

---

## Testing

Run unit tests via `pytest`:
```bash
uv run pytest tests/test_transliteration.py -q
```
