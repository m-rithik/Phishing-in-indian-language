"""Command-line entry point for the synthetic Fisher audit rehearsal."""

from __future__ import annotations

import argparse
from pathlib import Path

from .selector import SCOPE, format_json, format_text, invalid_usage_report, rehearse_file


class _SanitizedArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        del message
        raise ValueError("invalid command-line arguments")


def _parser() -> argparse.ArgumentParser:
    parser = _SanitizedArgumentParser(prog="python3 -m fisher_audit")
    subparsers = parser.add_subparsers(dest="command", required=True)
    rehearse = subparsers.add_parser(
        "rehearse",
        help="rehearse the canonical selector with synthetic metadata only",
    )
    rehearse.add_argument("--attempts", required=True, type=Path)
    rehearse.add_argument("--seed-hex", required=True)
    rehearse.add_argument("--scope", required=True)
    rehearse.add_argument(
        "--format", choices=("text", "json"), default="text", dest="output_format"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    try:
        args = _parser().parse_args(argv)
    except ValueError:
        print(format_text(invalid_usage_report()))
        return 2
    except SystemExit as error:
        return error.code if isinstance(error.code, int) else 2

    if args.scope != SCOPE:
        report = invalid_usage_report(code="non_synthetic_scope")
    else:
        report = rehearse_file(args.attempts, args.seed_hex)

    if args.output_format == "json":
        print(format_json(report))
    else:
        print(format_text(report))
    return 0 if report.structurally_valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
