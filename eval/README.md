# Evaluation Dataset Format

Each evaluation dataset file (`.jsonl`) contains one JSON object per line with the following schema:

```json
{
  "id": "hi-001",
  "text": "...",
  "label": "scam" | "benign",
  "language": "english" | "hindi" | "tamil" | "telugu",
  "script": "native" | "romanized" | "latin_english",
  "source": "synthetic" | "public:<dataset name>" | "consented"
}
```

### Constraints & Validation Rules
- **Fields**: Must contain exactly `id`, `text`, `label`, `language`, `script`, and `source`. Missing or unknown fields are rejected.
- **Labels**: Allowed values are `"scam"` or `"benign"`.
- **Languages**: Allowed values are `"english"`, `"hindi"`, `"tamil"`, or `"telugu"`.
- **Scripts**: Allowed values are `"native"`, `"romanized"`, or `"latin_english"`.
  - `script == "latin_english"` is required if and only if `language == "english"`.
- **Sources**: Allowed values are `"synthetic"`, `"consented"`, or strings beginning with `"public:"` (e.g., `"public:SMSDHL"`).
  - Any model-generated or synthetic text must always be labelled `"synthetic"`.
- **Integrity**: Duplicate IDs and duplicate texts (compared after lowercasing and collapsing whitespace) are rejected. Empty files are rejected.
