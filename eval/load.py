"""Dataset loader and validator for Fisher evaluation messages."""

import json
from pathlib import Path
import re
from typing import Any, Dict, List, Union

REQUIRED_FIELDS = {"id", "text", "label", "language", "script", "source"}
ALLOWED_LABELS = {"scam", "benign"}
ALLOWED_LANGUAGES = {"english", "hindi", "tamil", "telugu"}
ALLOWED_SCRIPTS = {"native", "romanized", "latin_english"}


def _collapse_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().lower()


def load_messages(path: Union[str, Path]) -> List[Dict[str, Any]]:
    """Load and validate an evaluation .jsonl dataset file.

    Raises:
        ValueError: If validation fails for any reason, including missing/unknown
            fields, invalid values, duplicates, language-script mismatch, or empty file.
    """
    file_path = Path(path)
    if not file_path.is_file():
        raise ValueError(f"File not found: {file_path}")

    lines = file_path.read_text(encoding="utf-8").splitlines()
    non_empty_lines = [line.strip() for line in lines if line.strip()]
    if not non_empty_lines:
        raise ValueError(f"Evaluation file is empty: {file_path}")

    messages = []
    seen_ids = set()
    seen_texts = set()

    for line_idx, line in enumerate(non_empty_lines, start=1):
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON on line {line_idx}: {exc}") from exc

        if not isinstance(record, dict):
            raise ValueError(f"Record on line {line_idx} is not a JSON object")

        record_keys = set(record.keys())
        if record_keys != REQUIRED_FIELDS:
            missing = REQUIRED_FIELDS - record_keys
            unknown = record_keys - REQUIRED_FIELDS
            msg_parts = []
            if missing:
                msg_parts.append(f"missing fields {sorted(missing)}")
            if unknown:
                msg_parts.append(f"unknown fields {sorted(unknown)}")
            raise ValueError(f"Line {line_idx} has invalid schema: {', '.join(msg_parts)}")

        record_id = record["id"]
        if not isinstance(record_id, str) or not record_id.strip():
            raise ValueError(f"Line {line_idx} has invalid or empty id: {record_id!r}")
        if record_id in seen_ids:
            raise ValueError(f"Line {line_idx} contains duplicate id: {record_id!r}")
        seen_ids.add(record_id)

        text = record["text"]
        if not isinstance(text, str) or not text.strip():
            raise ValueError(f"Line {line_idx} has invalid or empty text")
        norm_text = _collapse_whitespace(text)
        if norm_text in seen_texts:
            raise ValueError(f"Line {line_idx} contains duplicate text: {text!r}")
        seen_texts.add(norm_text)

        label = record["label"]
        if label not in ALLOWED_LABELS:
            raise ValueError(f"Line {line_idx} has invalid label {label!r}; must be one of {sorted(ALLOWED_LABELS)}")

        language = record["language"]
        if language not in ALLOWED_LANGUAGES:
            raise ValueError(f"Line {line_idx} has invalid language {language!r}; must be one of {sorted(ALLOWED_LANGUAGES)}")

        script = record["script"]
        if script not in ALLOWED_SCRIPTS:
            raise ValueError(f"Line {line_idx} has invalid script {script!r}; must be one of {sorted(ALLOWED_SCRIPTS)}")

        # script == "latin_english" exactly when language == "english"
        if (script == "latin_english") != (language == "english"):
            raise ValueError(
                f"Line {line_idx} script/language mismatch: script={script!r} is only allowed "
                f"if and only if language='english', but got language={language!r}"
            )

        source = record["source"]
        if not isinstance(source, str):
            raise ValueError(f"Line {line_idx} source must be a string")
        is_valid_source = source in {"synthetic", "consented"} or source.startswith("public:")
        if not is_valid_source:
            raise ValueError(f"Line {line_idx} has invalid source {source!r}")

        messages.append(record)

    return messages
