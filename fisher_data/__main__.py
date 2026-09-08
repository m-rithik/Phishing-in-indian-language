"""Command-line entry point for Fisher data tooling."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .validator import format_json, format_text, validate_files


class _SanitizedArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        del message
        self.print_usage(sys.stderr)
        self.exit(2, f"{self.prog}: error: invalid command-line arguments\n")


def _parser() -> argparse.ArgumentParser:
    parser = _SanitizedArgumentParser(prog="python3 -m fisher_data")
    subparsers = parser.add_subparsers(
        dest="command", required=True, parser_class=_SanitizedArgumentParser
    )
    validate = subparsers.add_parser(
        "validate", help="validate Fisher JSONL contract files"
    )
    validate.add_argument("--sources", required=True, type=Path)
    validate.add_argument("--items", required=True, type=Path)
    validate.add_argument("--annotations", required=True, type=Path)
    validate.add_argument("--registry-manifest", type=Path)
    validate.add_argument("--registry-references", type=Path)
    validate.add_argument(
        "--mode", required=True, choices=("draft", "pilot-final")
    )
    validate.add_argument(
        "--format", choices=("text", "json"), default="text", dest="output_format"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    report = validate_files(
        sources_path=args.sources,
        items_path=args.items,
        annotations_path=args.annotations,
        mode=args.mode,
        registry_manifest_path=args.registry_manifest,
        registry_references_path=args.registry_references,
    )
    if args.output_format == "json":
        print(format_json(report))
    else:
        print(format_text(report))
    return 0 if report.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
