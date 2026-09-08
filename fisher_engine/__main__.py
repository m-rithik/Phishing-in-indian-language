"""Safe command-line entry point for the Fisher synthetic E0 rehearsal."""

from __future__ import annotations

import argparse
import errno
import os
from pathlib import Path
import stat


_FIXTURE_MAX_BYTES = 4 * 1024 * 1024


class _FixtureInputError(ValueError):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


class _SanitizedArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        del message
        raise ValueError("invalid command-line arguments")


def _parser() -> argparse.ArgumentParser:
    parser = _SanitizedArgumentParser(prog="python3 -m fisher_engine")
    subparsers = parser.add_subparsers(
        dest="command", required=True, parser_class=_SanitizedArgumentParser
    )
    rehearse = subparsers.add_parser(
        "rehearse", help="run the reserved synthetic E0 interface rehearsal"
    )
    rehearse.add_argument("--fixture", required=True, type=Path)
    rehearse.add_argument(
        "--format", choices=("text", "json"), default="text", dest="output_format"
    )
    return parser


def _failure(code: str, output_format: str) -> None:
    safe_code = code if code.startswith("engine_") else "engine_internal_failure"
    if output_format == "json":
        value = {
            "report_version": "1.0.0",
            "scope": "SYNTHETIC_E0_ONLY",
            "invalid_codes": [safe_code],
            "status": "FAIL",
        }
        from ._canonical import canonical_json_bytes

        print(canonical_json_bytes(value).decode("utf-8"))
    else:
        print(f"Fisher synthetic E0: FAIL\ncode: {safe_code}")


def _read_regular_file(path: Path, cap: int) -> bytes:
    flags = os.O_RDONLY
    for name in ("O_CLOEXEC", "O_NOFOLLOW", "O_NONBLOCK"):
        flags |= getattr(os, name, 0)
    try:
        descriptor = os.open(path, flags)
    except OSError as error:
        code = "engine_internal_failure" if error.errno == errno.ENOENT else "engine_fixture_invalid_input"
        raise _FixtureInputError(code) from error
    except (MemoryError, RecursionError) as error:
        raise _FixtureInputError("engine_fixture_invalid_input") from error
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode):
            raise _FixtureInputError("engine_fixture_invalid_input")
        if before.st_size > cap:
            raise _FixtureInputError("engine_fixture_too_large")
        chunks: list[bytes] = []
        remaining = cap + 1
        while remaining:
            chunk = os.read(descriptor, min(remaining, 64 * 1024))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        data = b"".join(chunks)
        after = os.fstat(descriptor)
        if (
            (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns)
            != (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns)
            or len(data) != before.st_size
        ):
            raise _FixtureInputError("engine_fixture_invalid_input")
        if len(data) > cap:
            raise _FixtureInputError("engine_fixture_too_large")
        return data
    except (OSError, MemoryError, RecursionError) as error:
        raise _FixtureInputError("engine_fixture_invalid_input") from error
    finally:
        os.close(descriptor)


def main(argv: list[str] | None = None) -> int:
    try:
        args = _parser().parse_args(argv)
    except SystemExit as error:
        if error.code == 0:
            return 0
        print("Fisher synthetic E0: INVALID_USAGE")
        return 2
    except ValueError:
        print("Fisher synthetic E0: INVALID_USAGE")
        return 2

    try:
        raw = _read_regular_file(args.fixture, _FIXTURE_MAX_BYTES)
    except _FixtureInputError as error:
        _failure(error.code, args.output_format)
        return 1
    try:
        from . import harness as harness_module
    except (ImportError, OSError, ValueError, TypeError, KeyError):
        _failure("engine_internal_failure", args.output_format)
        return 1
    try:
        result = harness_module.run_synthetic_e0_bytes(
            raw, project_root=Path(__file__).resolve().parents[1]
        )
    except harness_module.HarnessError as error:
        _failure(error.code, args.output_format)
        return 1
    except (OSError, ValueError, TypeError, KeyError):
        _failure("engine_internal_failure", args.output_format)
        return 1
    print(
        harness_module.format_report_json(result)
        if args.output_format == "json"
        else harness_module.format_report_text(result)
    )
    return 0 if result.valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
