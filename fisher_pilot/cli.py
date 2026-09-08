from __future__ import annotations

import argparse
from collections.abc import Sequence
import json
import sys

from fisher_pilot.validator import validate_files


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m fisher_pilot")
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate = subparsers.add_parser("validate", help="validate Fisher pilot JSONL")
    validate.add_argument("--sources", required=True)
    validate.add_argument("--items", required=True)
    validate.add_argument("--annotations", required=True)
    validate.add_argument("--mode", choices=("draft", "ready"), required=True)
    validate.add_argument("--format", choices=("text", "json"), required=True)
    return parser


def _text_report(report: dict[str, object]) -> str:
    counts = report["counts"]
    assert isinstance(counts, dict)
    lines = [
        f"{report['status']} Fisher pilot schema {report['schema_version']} ({report['mode']})",
        (
            f"counts sources={counts['sources']} items={counts['items']} "
            f"annotations={counts['annotations']} errors={counts['errors']} "
            f"warnings={counts['warnings']}"
        ),
    ]
    diagnostics = report["diagnostics"]
    assert isinstance(diagnostics, list)
    for diagnostic in diagnostics:
        assert isinstance(diagnostic, dict)
        location = diagnostic["record_kind"]
        if "line" in diagnostic:
            location += f":{diagnostic['line']}"
        if "field" in diagnostic:
            location += f":{diagnostic['field']}"
        lines.append(f"{diagnostic['severity']} {diagnostic['code']} {location}")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    arguments = parser.parse_args(argv)
    result = validate_files(
        arguments.sources,
        arguments.items,
        arguments.annotations,
        mode=arguments.mode,
    )
    if arguments.format == "json":
        print(json.dumps(result.report, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    else:
        print(_text_report(result.report))
    return 0 if result.valid else 1


if __name__ == "__main__":
    sys.exit(main())
