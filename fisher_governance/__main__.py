"""Command-line entry point for Fisher governance tooling."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from .validator import format_json, format_text, validate_ledger


class _SanitizedArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        del message
        self.print_usage(sys.stderr)
        self.exit(2, f"{self.prog}: error: invalid command-line arguments\n")


def _parser() -> argparse.ArgumentParser:
    parser = _SanitizedArgumentParser(prog="python3 -m fisher_governance")
    subparsers = parser.add_subparsers(
        dest="command", required=True, parser_class=_SanitizedArgumentParser
    )
    validate = subparsers.add_parser(
        "validate", help="validate a Fisher governance source ledger"
    )
    validate.add_argument("--ledger", required=True, type=Path)
    validate.add_argument(
        "--format", choices=("text", "json"), default="text", dest="output_format"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    report = validate_ledger(args.ledger)
    print(format_json(report) if args.output_format == "json" else format_text(report))
    return 0 if report.collection_ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
