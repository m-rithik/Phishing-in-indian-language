from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
import ipaddress
from pathlib import Path
from pathlib import PurePosixPath
import posixpath
import re
import unicodedata
import xml.etree.ElementTree as ElementTree
from zipfile import BadZipFile, ZipFile

from openpyxl.utils.cell import range_boundaries
import pandas as pd


DEFAULT_SHEET = "Dravidian Dataset"
MAX_WORKBOOK_BYTES = 32 * 1024 * 1024
MAX_ROWS = 200_000
EXPECTED_COLUMNS = ("Message", "Type")
_SPREADSHEET_NS = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
_OFFICE_REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
_PACKAGE_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"


class DataValidationError(ValueError):
    """Raised when an input cannot be processed without weakening the contract."""


_URL_RE = re.compile(r"(?i)(?<!\w)(?:https?://|www\.)[^\s<>\[\]]+")
_EMAIL_RE = re.compile(
    r"(?i)(?<![\w@])[\w.!#$%&'*+/=?^_`{|}~\-]+@"
    r"(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,63}(?![\w@])"
)
_UPI_RE = re.compile(
    r"(?i)(?<![\w@])[a-z0-9][a-z0-9._-]{1,255}@"
    r"(?:upi|ybl|ibl|axl|okaxis|okhdfcbank|okicici|oksbi|paytm|apl|pingpay)(?![\w@])"
)
_IPV4_RE = re.compile(r"(?<![\w.])(?:\d{1,3}\.){3}\d{1,3}(?![\w.])")
_IPV6_CANDIDATE_RE = re.compile(r"(?<![\w:])[0-9a-fA-F:]{2,39}(?![\w:])")
_PHONE_CANDIDATE_RE = re.compile(r"(?<!\w)\+?\d[\d\s().-]{7,}\d(?!\w)")
_DOMAIN_CANDIDATE_RE = re.compile(
    r"(?i)(?<![\w@])[\w\u0080-\uffff-]+(?:\.[\w\u0080-\uffff-]+)+(?![\w@])"
)
_SPACED_HTTP_RE = re.compile(r"(?i)\bhttps?\s*:\s*/\s*/")
_SPACED_DOMAIN_RE = re.compile(r"(?i)\b[a-z0-9-]{2,}\s+\.\s+[a-z]{2,63}\b")
_UNDOTTED_HANDLE_RE = re.compile(
    r"(?i)(?<![\w@])[a-z0-9][a-z0-9._-]{1,255}@[a-z][a-z0-9_-]{1,63}(?![\w@.])"
)
_BROAD_PHONE_CANDIDATE_RE = re.compile(
    r"(?<!\w)\+?\d[\d\s()./\-\u200b\u200c\u200d\ufeff]{7,}\d(?!\w)"
)
_PLACEHOLDER_RE = re.compile(r"\[(?:URL|DOMAIN|EMAIL|PHONE|UPI|IPV4|IPV6)\]")
_DIGIT_RUN_RE = re.compile(r"\d+")


def _digest(value: str) -> str:
    return sha256(value.encode("utf-8")).hexdigest()


def workbook_sha256(path: Path) -> str:
    digest = sha256()
    try:
        with path.open("rb") as handle:
            while chunk := handle.read(1024 * 1024):
                digest.update(chunk)
    except OSError as exc:
        raise DataValidationError("workbook is not readable") from exc
    return digest.hexdigest()


def load_workbook_dataframe(
    workbook: str | Path,
    *,
    sheet: str = DEFAULT_SHEET,
) -> tuple[pd.DataFrame, str]:
    path = Path(workbook)
    if not isinstance(sheet, str) or not sheet or len(sheet) > 128:
        raise DataValidationError("sheet selection is invalid")
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise DataValidationError("workbook is not readable") from exc
    if not path.is_file() or path.suffix.casefold() != ".xlsx":
        raise DataValidationError("workbook format is invalid")
    if size <= 0 or size > MAX_WORKBOOK_BYTES:
        raise DataValidationError("workbook size is outside the accepted bound")

    digest = workbook_sha256(path)
    try:
        frame = pd.read_excel(
            path,
            sheet_name=sheet,
            dtype=object,
            engine="openpyxl",
            nrows=MAX_ROWS + 1,
        )
    except Exception as exc:
        raise DataValidationError("workbook contents are invalid") from exc
    if len(frame) > MAX_ROWS:
        raise DataValidationError("workbook row count exceeds the accepted bound")
    return frame, digest


def count_external_hyperlink_cells(workbook: str | Path, *, sheet: str) -> int:
    """Count selected-sheet external hyperlink cells without loading or retaining targets."""
    path = Path(workbook)
    try:
        with ZipFile(path) as archive:
            workbook_root = ElementTree.parse(archive.open("xl/workbook.xml")).getroot()
            selected_relationship_id: str | None = None
            for sheet_element in workbook_root.iter(f"{{{_SPREADSHEET_NS}}}sheet"):
                if sheet_element.attrib.get("name") == sheet:
                    selected_relationship_id = sheet_element.attrib.get(
                        f"{{{_OFFICE_REL_NS}}}id"
                    )
                    break
            if selected_relationship_id is None:
                raise DataValidationError("selected sheet metadata is invalid")

            workbook_relationships = ElementTree.parse(
                archive.open("xl/_rels/workbook.xml.rels")
            ).getroot()
            sheet_target: str | None = None
            for relationship in workbook_relationships.iter(
                f"{{{_PACKAGE_REL_NS}}}Relationship"
            ):
                if relationship.attrib.get("Id") == selected_relationship_id:
                    sheet_target = relationship.attrib.get("Target")
                    break
            if sheet_target is None:
                raise DataValidationError("selected sheet metadata is invalid")

            if sheet_target.startswith("/"):
                sheet_part = sheet_target.lstrip("/")
            else:
                sheet_part = posixpath.normpath(posixpath.join("xl", sheet_target))
            if sheet_part.startswith("../") or not sheet_part.startswith("xl/"):
                raise DataValidationError("selected sheet metadata is invalid")

            part_path = PurePosixPath(sheet_part)
            relationships_part = str(
                part_path.parent / "_rels" / f"{part_path.name}.rels"
            )
            if relationships_part not in archive.namelist():
                return 0
            sheet_relationships = ElementTree.parse(archive.open(relationships_part)).getroot()
            external_hyperlink_ids = {
                relationship.attrib["Id"]
                for relationship in sheet_relationships.iter(
                    f"{{{_PACKAGE_REL_NS}}}Relationship"
                )
                if relationship.attrib.get("TargetMode") == "External"
                and relationship.attrib.get("Type", "").endswith("/hyperlink")
                and "Id" in relationship.attrib
            }
            if not external_hyperlink_ids:
                return 0

            cell_count = 0
            with archive.open(sheet_part) as sheet_stream:
                for _, element in ElementTree.iterparse(sheet_stream, events=("end",)):
                    if element.tag != f"{{{_SPREADSHEET_NS}}}hyperlink":
                        element.clear()
                        continue
                    if element.attrib.get(f"{{{_OFFICE_REL_NS}}}id") in external_hyperlink_ids:
                        reference = element.attrib.get("ref", "")
                        try:
                            minimum_column, minimum_row, maximum_column, maximum_row = (
                                range_boundaries(reference)
                            )
                        except ValueError as exc:
                            raise DataValidationError("hyperlink metadata is invalid") from exc
                        cell_count += (maximum_column - minimum_column + 1) * (
                            maximum_row - minimum_row + 1
                        )
                    element.clear()
            return cell_count
    except (BadZipFile, KeyError, OSError, ElementTree.ParseError) as exc:
        raise DataValidationError("workbook metadata is invalid") from exc


def normalize_duplicate_key(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text)
    without_format_controls = "".join(
        character for character in normalized if unicodedata.category(character) != "Cf"
    )
    return " ".join(without_format_controls.casefold().split())


def _replace_valid_ipv4(match: re.Match[str]) -> str:
    try:
        ipaddress.IPv4Address(match.group(0))
    except ipaddress.AddressValueError:
        return match.group(0)
    return "[IPV4]"


def _replace_valid_ipv6(match: re.Match[str]) -> str:
    candidate = match.group(0)
    if candidate.count(":") < 2:
        return candidate
    try:
        ipaddress.IPv6Address(candidate)
    except ipaddress.AddressValueError:
        return candidate
    return "[IPV6]"


def _replace_valid_phone(match: re.Match[str]) -> str:
    candidate = match.group(0)
    digit_count = sum(character.isdigit() for character in candidate)
    return "[PHONE]" if 10 <= digit_count <= 15 else candidate


def _valid_domain(candidate: str) -> bool:
    if len(candidate) > 253:
        return False
    labels = candidate.split(".")
    if len(labels) < 2 or not (2 <= len(labels[-1]) <= 63):
        return False
    for label in labels:
        if not label or len(label) > 63 or label[0] == "-" or label[-1] == "-":
            return False
        if any(
            character != "-" and unicodedata.category(character)[0] not in {"L", "M", "N"}
            for character in label
        ):
            return False
    return any(unicodedata.category(character).startswith("L") for character in labels[-1])


def _replace_valid_domain(match: re.Match[str]) -> str:
    candidate = match.group(0)
    return "[DOMAIN]" if _valid_domain(candidate) else candidate


def _defang_with_counts(text: str) -> tuple[str, dict[str, int]]:
    counts = {
        "url": 0,
        "email": 0,
        "upi": 0,
        "phone": 0,
        "ipv4": 0,
        "ipv6": 0,
        "domain": 0,
    }

    def validated_replacer(kind: str, replacer):
        def replace(match: re.Match[str]) -> str:
            replacement = replacer(match)
            if replacement != match.group(0):
                counts[kind] += 1
            return replacement

        return replace

    value = unicodedata.normalize("NFKC", text).translate(
        {ord("。"): ".", ord("．"): ".", ord("｡"): "."}
    )
    value, counts["url"] = _URL_RE.subn("[URL]", value)
    value, counts["email"] = _EMAIL_RE.subn("[EMAIL]", value)
    value = _IPV6_CANDIDATE_RE.sub(validated_replacer("ipv6", _replace_valid_ipv6), value)
    value = _IPV4_RE.sub(validated_replacer("ipv4", _replace_valid_ipv4), value)
    value, counts["upi"] = _UPI_RE.subn("[UPI]", value)
    value = _PHONE_CANDIDATE_RE.sub(validated_replacer("phone", _replace_valid_phone), value)
    value = _DOMAIN_CANDIDATE_RE.sub(validated_replacer("domain", _replace_valid_domain), value)
    return value, counts


def scan_live_artifacts(text: str) -> dict[str, int]:
    """Count recognized raw artifacts without retaining their values."""
    _, counts = _defang_with_counts(text)
    return counts


def defang_text(text: str) -> str:
    """Replace recognized live contact/network artifacts with typed placeholders."""
    value, _ = _defang_with_counts(text)
    return value


def has_residual_live_artifact(text: str) -> bool:
    return defang_text(text) != text


def scan_residual_candidates(text: str) -> dict[str, int]:
    """Flag bounded residual categories for one row after primary defanging."""
    has_broad_phone = any(
        10 <= sum(character.isdecimal() for character in match.group(0)) <= 15
        for match in _BROAD_PHONE_CANDIDATE_RE.finditer(text)
    )
    return {
        "spaced_http": int(_SPACED_HTTP_RE.search(text) is not None),
        "spaced_domain": int(_SPACED_DOMAIN_RE.search(text) is not None),
        "undotted_handle": int(_UNDOTTED_HANDLE_RE.search(text) is not None),
        "broad_phone": int(has_broad_phone),
    }


def _script_for_character(character: str) -> str | None:
    codepoint = ord(character)
    if 0x0B80 <= codepoint <= 0x0BFF:
        return "tamil"
    if 0x0C00 <= codepoint <= 0x0C7F:
        return "telugu"
    if 0x0C80 <= codepoint <= 0x0CFF:
        return "kannada"
    if 0x0D00 <= codepoint <= 0x0D7F:
        return "malayalam"
    if "LATIN" in unicodedata.name(character, ""):
        return "latin"
    return None


def script_category(text: str) -> str:
    """Return a mechanical dominant-script category; this is not language inference."""
    counts = {name: 0 for name in ("tamil", "telugu", "kannada", "malayalam", "latin")}
    without_placeholders = _PLACEHOLDER_RE.sub("", text)
    for character in without_placeholders:
        if unicodedata.category(character)[0] not in {"L", "M"}:
            continue
        script = _script_for_character(character)
        if script is not None:
            counts[script] += 1
    recognized_letters_and_marks = sum(counts.values())
    if recognized_letters_and_marks == 0:
        return "no_letters"
    dominant, count = max(counts.items(), key=lambda item: (item[1], item[0]))
    if count / recognized_letters_and_marks >= 0.70:
        return dominant
    return "mixed"


def template_group_id(model_text: str) -> str:
    normalized = normalize_duplicate_key(_DIGIT_RUN_RE.sub("[NUMBER]", model_text))
    return _digest(f"fisher-template-v1\0{normalized}")


def _trim_and_validate_headers(frame: pd.DataFrame) -> pd.DataFrame:
    trimmed = [column.strip() if isinstance(column, str) else None for column in frame.columns]
    if len(trimmed) != 2 or set(trimmed) != set(EXPECTED_COLUMNS) or None in trimmed:
        raise DataValidationError("workbook schema is invalid")
    if len(set(trimmed)) != len(trimmed):
        raise DataValidationError("workbook schema is invalid")
    renamed = frame.copy(deep=False)
    renamed.columns = trimmed
    return renamed.loc[:, list(EXPECTED_COLUMNS)]


def _label_state(value: object) -> str:
    if value is None or (not isinstance(value, str) and pd.isna(value)):
        return "blank"
    if not isinstance(value, str):
        return "unknown"
    stripped = value.strip()
    if not stripped:
        return "blank"
    folded = stripped.casefold()
    return folded if folded in {"ham", "spam"} else "unknown"


def prepare_dataframe(frame: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, object]]:
    """Validate, conservatively quarantine, deduplicate, and defang a source frame."""
    source = _trim_and_validate_headers(frame)
    dispositions = {
        "total_rows": int(len(source)),
        "valid_text_rows": 0,
        "candidate_binary_rows": 0,
        "quarantined_invalid_text_rows": 0,
        "quarantined_blank_label_rows": 0,
        "quarantined_unknown_label_rows": 0,
        "contaminated_duplicate_groups": 0,
        "quarantined_contaminated_binary_rows": 0,
        "deduplicated_binary_rows_removed": 0,
        "quarantined_residual_artifact_rows": 0,
        "retained_rows": 0,
    }
    raw_artifact_counts = {
        "url": 0,
        "email": 0,
        "upi": 0,
        "phone": 0,
        "ipv4": 0,
        "ipv6": 0,
        "domain": 0,
    }
    residual_candidate_counts = {
        "spaced_http": 0,
        "spaced_domain": 0,
        "undotted_handle": 0,
        "broad_phone": 0,
    }
    residual_candidate_rows = 0

    grouped_rows: dict[str, list[tuple[int, str, str]]] = defaultdict(list)
    group_states: dict[str, set[str]] = defaultdict(set)
    for row_position, (message, label_value) in enumerate(
        source[["Message", "Type"]].itertuples(index=False, name=None)
    ):
        if not isinstance(message, str) or not message.strip():
            dispositions["quarantined_invalid_text_rows"] += 1
            continue
        dispositions["valid_text_rows"] += 1
        for kind, count in scan_live_artifacts(message).items():
            raw_artifact_counts[kind] += count
        duplicate_key = normalize_duplicate_key(message)
        state = _label_state(label_value)
        group_states[duplicate_key].add(state if state in {"ham", "spam"} else "malformed")
        if state == "blank":
            dispositions["quarantined_blank_label_rows"] += 1
            continue
        if state == "unknown":
            dispositions["quarantined_unknown_label_rows"] += 1
            continue
        dispositions["candidate_binary_rows"] += 1
        grouped_rows[duplicate_key].append((row_position, message, state))

    retained: list[dict[str, str]] = []
    for duplicate_key in sorted(grouped_rows):
        rows = grouped_rows[duplicate_key]
        binary_labels = {row[2] for row in rows}
        states = group_states[duplicate_key]
        contaminated = len(binary_labels) > 1 or "malformed" in states
        if contaminated:
            dispositions["contaminated_duplicate_groups"] += 1
            dispositions["quarantined_contaminated_binary_rows"] += len(rows)
            continue

        representative = min(
            rows,
            key=lambda row: (unicodedata.normalize("NFKC", row[1]), row[1], row[0]),
        )
        dispositions["deduplicated_binary_rows_removed"] += len(rows) - 1
        _, message, label = representative
        model_text = defang_text(message)
        row_residual_counts = scan_residual_candidates(model_text)
        for kind, count in row_residual_counts.items():
            residual_candidate_counts[kind] += count
        has_residual_candidate = any(row_residual_counts.values())
        if has_residual_candidate:
            residual_candidate_rows += 1
        if has_residual_live_artifact(model_text) or has_residual_candidate:
            dispositions["quarantined_residual_artifact_rows"] += 1
            continue
        retained.append(
            {
                "record_id": _digest(f"fisher-record-v1\0{duplicate_key}"),
                "group_id": template_group_id(model_text),
                "label": label,
                "model_text": model_text,
                "script": script_category(model_text),
            }
        )

    retained.sort(key=lambda row: row["record_id"])
    dispositions["retained_rows"] = len(retained)
    classified = (
        dispositions["quarantined_invalid_text_rows"]
        + dispositions["quarantined_blank_label_rows"]
        + dispositions["quarantined_unknown_label_rows"]
        + dispositions["quarantined_contaminated_binary_rows"]
        + dispositions["deduplicated_binary_rows_removed"]
        + dispositions["quarantined_residual_artifact_rows"]
        + dispositions["retained_rows"]
    )
    if classified != dispositions["total_rows"]:
        raise RuntimeError("internal disposition accounting failure")

    prepared = pd.DataFrame.from_records(
        retained,
        columns=["record_id", "group_id", "label", "model_text", "script"],
    )
    audit: dict[str, object] = {
        "schema_version": "1.0.0",
        "task": "auxiliary_spam_ham",
        "label_policy": "case-insensitive exact Ham/Spam after surrounding-whitespace trimming",
        "duplicate_policy": (
            "NFKC + Unicode Cf removal + casefold + whitespace collapse; "
            "malformed/conflicting groups quarantined"
        ),
        "script_policy": "mechanical >=70% recognized Unicode Letter/Mark dominance; not language inference",
        "artifact_policy": (
            "typed placeholders for recognized live artifacts; independent bounded residual "
            "candidate scanner fails closed"
        ),
        "raw_pre_defang_artifact_counts": raw_artifact_counts,
        "post_defang_residual_candidate_counts": residual_candidate_counts,
        "post_defang_residual_candidate_rows": residual_candidate_rows,
        "dispositions": dispositions,
        "retained_label_counts": {
            label: int(count)
            for label, count in prepared["label"].value_counts().sort_index().items()
        },
        "retained_script_counts": {
            script: int(count)
            for script, count in prepared["script"].value_counts().sort_index().items()
        },
    }
    return prepared, audit


def audit_workbook(
    workbook: str | Path,
    *,
    sheet: str = DEFAULT_SHEET,
) -> tuple[pd.DataFrame, dict[str, object]]:
    frame, digest = load_workbook_dataframe(workbook, sheet=sheet)
    external_hyperlink_cells = count_external_hyperlink_cells(workbook, sheet=sheet)
    prepared, audit = prepare_dataframe(frame)
    audit["source"] = {
        "workbook_sha256": digest,
        "selected_sheet": sheet,
        "external_hyperlink_cells": external_hyperlink_cells,
        "external_hyperlink_targets_recorded": False,
        "source_path_recorded": False,
    }
    return prepared, audit
