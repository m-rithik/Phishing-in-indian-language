from __future__ import annotations

import argparse
from collections.abc import Sequence
import sys

from fisher_baselines.data import DEFAULT_SHEET, DataValidationError, audit_workbook
from fisher_baselines.evaluation import (
    EvaluationError,
    evaluate_workbook,
    write_evaluation_outputs,
    write_json_file,
)
from fisher_baselines.selection import nested_evaluate_workbook, write_selection_output


def _integer(value: str) -> int:
    try:
        return int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("invalid integer") from exc


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m fisher_baselines")
    subparsers = parser.add_subparsers(dest="command", required=True)

    audit = subparsers.add_parser("audit", help="audit an auxiliary spam/ham workbook")
    audit.add_argument("--workbook", required=True)
    audit.add_argument("--output", required=True)
    audit.add_argument("--sheet", default=DEFAULT_SHEET)

    evaluate = subparsers.add_parser("evaluate", help="run development-only grouped evaluation")
    evaluate.add_argument("--workbook", required=True)
    evaluate.add_argument("--output-dir", required=True)
    evaluate.add_argument("--sheet", default=DEFAULT_SHEET)
    evaluate.add_argument("--seed", type=_integer, default=1729)
    evaluate.add_argument("--folds", type=_integer, default=3)

    nested = subparsers.add_parser(
        "nested-evaluate", help="run development-only nested grouped model selection"
    )
    nested.add_argument("--workbook", required=True)
    nested.add_argument("--output", required=True)
    nested.add_argument("--sheet", default=DEFAULT_SHEET)
    nested.add_argument("--seed", type=_integer, default=1729)
    nested.add_argument("--outer-folds", type=_integer, default=3)
    nested.add_argument("--inner-folds", type=_integer, default=3)
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    arguments = parser.parse_args(argv)
    try:
        if arguments.command == "audit":
            _, report = audit_workbook(arguments.workbook, sheet=arguments.sheet)
            write_json_file(report, arguments.output)
            print("Audit completed.")
            return 0

        if arguments.command == "evaluate":
            result = evaluate_workbook(
                arguments.workbook,
                sheet=arguments.sheet,
                seed=arguments.seed,
                folds=arguments.folds,
            )
            write_evaluation_outputs(result, arguments.output_dir)
            print("Development evaluation completed.")
            return 0

        selection = nested_evaluate_workbook(
            arguments.workbook,
            sheet=arguments.sheet,
            seed=arguments.seed,
            outer_folds=arguments.outer_folds,
            inner_folds=arguments.inner_folds,
        )
        write_selection_output(selection, arguments.output)
        print("Development nested selection completed.")
        return 0
    except (DataValidationError, EvaluationError, OSError):
        parser.exit(2, "error: operation failed safely\n")


if __name__ == "__main__":
    sys.exit(main())
