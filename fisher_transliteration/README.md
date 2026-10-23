# Fisher Transliteration: Multi-Candidate Generation for Indic Scripts

## Overview

`fisher_transliteration` generates multiple plausible Indic script interpretations from Romanized input, enabling **multi-candidate aggregation** for more robust phishing detection across Hindi, Tamil, and Telugu.

**Key insight:** A user typing "otp" in a message might intend:
- English (romanized): `otp`
- Hindi (Devanagari): `ओटीपी`
- Tamil: `ஓடிபி`
- Telugu: `ఓటీపీ`

By generating all candidates and aggregating predictions over them, phishing classifiers can detect signals that might be missed by single-interpretation approaches.

## API

### `generate_candidates(text: str, config: Optional[CandidateConfig] = None) -> List[Candidate]`

Generate transliteration candidates from Romanized input.

**Args:**
- `text` (str): Romanized input (e.g., "otp", "password", "send otp")
- `config` (CandidateConfig, optional): Configuration (max_candidates, min_confidence, etc.)

**Returns:** List of `Candidate` objects, sorted by confidence (descending)

**Example:**
```python
from fisher_transliteration import generate_candidates

candidates = generate_candidates("otp")
for c in candidates:
    print(f"{c.script:12} {c.text:15} confidence={c.confidence:.2f}")

# Output:
# romanized    otp             confidence=1.00
# hindi        ओटीपी           confidence=2.50
# tamil        ஓடிபி           confidence=2.50
# telugu       ఓటీపీ           confidence=2.50
```

### `CandidateConfig`

Configuration dataclass for candidate generation.

**Fields:**
- `max_candidates` (int, default=8): Maximum candidates to return
- `min_confidence` (float, default=0.3): Minimum confidence threshold
- `include_romanized` (bool, default=True): Include original romanized version
- `scripts` (List[str], default=["hindi", "tamil", "telugu"]): Target scripts

**Example:**
```python
from fisher_transliteration import CandidateConfig, generate_candidates

config = CandidateConfig(max_candidates=3, scripts=["hindi", "tamil"])
candidates = generate_candidates("password", config)
```

### `Candidate`

Immutable dataclass representing a single transliteration hypothesis.

**Fields:**
- `text` (str): Transliterated text in target script
- `script` (str): Target script ("hindi", "tamil", "telugu", or "romanized")
- `confidence` (float): Likelihood weight (derived from romanization rule frequency)
- `source_rule` (str, optional): Name of the rule used (e.g., "otp", "multi:pass")
- `ambiguous` (bool): Whether multiple interpretations are equally valid

## Design

### Romanization Rules

Three language-specific rule sets encode common Romanization patterns:

#### Hindi (Devanagari)
- Covers vowels, consonants, retroflex consonants, and sensitive terms (OTP, password, CVV, KYC)
- Weights prioritize authentic text (e.g., "aa" → आ at weight 1.8, "aaa" → आ at weight 0.3)
- See `rules.py:HINDI_RULES`

#### Tamil
- Covers Tamil vowel system (11 independent vowels) and consonants
- Notes ambiguities (e.g., Tamil "க" maps from both "k" and "g")
- Sensitive term coverage: ஓடிபி, கடவுச்சொல், etc.
- See `rules.py:TAMIL_RULES`

#### Telugu
- Covers Telugu vowels (6 independent + 2 dependent), consonants, retroflex consonants
- Sensitive term coverage: ఓటీపీ, పాస్‌వర్డ్, etc.
- See `rules.py:TELUGU_RULES`

### Candidate Generation Strategy

1. **Tokenization**: Greedy longest-match to break input into romanization units (e.g., "otp" → ["otp"], "ch" → ["ch"], "password" → ["p", "a", "s", "s"] or ["pass"])
2. **Rule Matching**: For each token, find applicable rules in each script
3. **Combination**: Generate multi-token candidates (less frequent: "p a s s" → "पास")
4. **Scoring**: Each rule has a weight (frequency or sensitivity)
5. **Ranking**: Sort by confidence, deduplicate by (text, script), truncate to max_candidates

### Privacy & Safety

- **No input echo**: Candidates are transliterated interpretations, never the original romanized input verbatim
- **Bounded computation**: Max 8 candidates (configurable), preventing DoS
- **Deterministic**: Same input always produces same candidates (enables reproducible tests)

## Integration with Fisher Engine

### Current State (v0.5)
The v0.5 extension uses transparent rule-based detection on romanized input only.

### Future (v0.6+)
Planned integration with phishing classifier:

```python
# In detector.mjs (future):
import { generate_candidates } from "./transliteration.mjs";

function detectPhishingMultiCandidate(message: string) {
  const candidates = generate_candidates(extractRomanizedIndic(message));
  const predictions = candidates.map(c => classifyCandidate(c));
  return aggregate(predictions);  // vote, average confidence, etc.
}
```

## Testing

Run the test suite:
```bash
uv run python -m unittest tests.test_transliteration -v
```

Tests cover:
- Single and multi-token generation (20 tests, all passing)
- Phishing term recognition (OTP, CVV, KYC, password)
- Script-specific generation (Hindi, Tamil, Telugu)
- Confidence ordering and filtering
- Configuration behavior
- Determinism and privacy

## Limitations & Future Work

### Current Limitations
1. **Rule set is curated, not learned**: Romanization patterns are hand-coded from linguistic knowledge, not extracted from corpus
2. **English/Romanized only as input**: Non-Latin scripts must be Romanized first (not handled by this module)
3. **No context**: Rules are context-free; "ka" → क equally in "kaka" and "karma"
4. **Sensitive terms only**: Rules focus on phishing signals; general vocabulary is sparse

### Future Improvements
1. **Learn from corpus**: Extract romanization patterns from real user-generated Hindi/Tamil/Telugu SMS and chat
2. **Bidirectional transliteration**: Build Indic→Roman reversal as well (currently Roman→Indic only)
3. **Context-aware rules**: Weight rules by preceding/following tokens
4. **Multilingual encoder**: Replace rule-based generation with fine-tuned XLS-R or mBERT
5. **Ambiguity resolution**: Use classifier confidence to select top-1 candidate instead of all

## References

- **ITRANS** (Harvard-Kyoto, Velthuis): Standard Romanization for Hindi/Sanskrit
- **Fisher Transliteration Resource Protocol**: `docs/research/TRANSLITERATION_RESOURCE_PROTOCOL.md`
- **Pilot Validator**: `fisher_pilot/validator.py` (tracks `romanization_ambiguous` flag)

## License

No reuse license selected. Part of Fisher research project.
