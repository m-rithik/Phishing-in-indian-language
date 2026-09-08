# Fisher synthetic E0 executable contract

> Status: synthetic interface implementation only. This package does not
> contain a trained model, authentic corpus, nonidentity production provider,
> real registry, or measured performance result. `G5` and `G6` remain blocked.

## Run the rehearsal

Python 3.11 or newer is the intended language boundary. The implementation uses
only the Python standard library and project-local Fisher modules.

```console
python3 -m fisher_engine rehearse \
  --fixture examples/engine/synthetic_e0.json \
  --format text
```

Use `--format json` for the canonical machine-readable report. Exit status `0`
means the complete synthetic rehearsal passed, `1` means a controlled input or
engine failure, and `2` means invalid command-line use. Failure output never
echoes a submitted path, malformed field, message, or external identifier.
Fixture paths are opened without symlink following, verified as regular files
with `fstat`, and read through a 4 MiB cap-plus-one boundary; directories,
FIFOs, devices, symlinks, and changing files fail closed. Top-level and
subcommand `--help` print help only and exit `0`.

## What the rehearsal proves

The fixture executes the eight frozen condition/control combinations:

- four base cells `C00`, `C10`, `C01`, and `C11`;
- matched `C00`/`C10` capacity controls; and
- matched `C01`/`C11` supervision controls.

Each run passes the path-free descriptor boundary, binds an exact source
closure and system manifest, constructs the same two-path synthetic provider
output with nonuniform path weights, performs candidate arithmetic, emits a five-seed audit, and validates a
canonical run envelope. Only base `C01` and `C11` construct prediction, pair,
registry, structural-feature, and numeric-feature artifacts. The harness then
executes two one-item synthetic metric runs against a complete frozen synthetic
universe. The expected match is a known-answer interface check, not an empirical
F1 result.

Artifact hashes bind compact UTF-8 JSON in declared field order, NFC strings,
finite binary64 values, positive zero, exact current source bytes, and the
recorded runtime/platform/math identity. Hashes therefore change when executable
source or the runtime binding changes. Repeated execution without either change
must be byte-identical.

All canonical JSON boundaries have an exact maximum container nesting of 64
objects/arrays, counting the root container as level one. Level 65, recursion
exhaustion, and allocation failure become controlled validation failures rather
than tracebacks. Stream readers clip even a hostile over-return to the exact
cap-plus-one prefix.

The source closure is collected by one process-global Python audit hook that is
inert without an active recorder. While active it records project-root `.py`
files observed through import, compile, exec, and open events; declared
entrypoints and collector bootstrap files are always reconciled. It does not
derive evidence from `sys.modules` process history.

An engine envelope is valid only with an opaque, recomputed PASS-preflight
context and the exact persisted provider, diagnostic, candidate-path, seed,
registry, prediction, pair, feature-plan, and tensor bytes required by its
status and mask. The public validator has no context-free acceptance path. It
replays candidate and semantic derivations, exact path weights and counts,
runtime/system bindings, and the eight-system matched-control bundle before
returning frozen active paths for evaluation.
Engine preflight itself requires that exact eight-manifest bundle; a structurally
valid single manifest without its matched factorial set fails system validation.

## Implementation map

- `fisher_engine._canonical` owns bounded reads, strict JSON event precedence,
  the 64-level nesting limit, canonical bytes, and SHA-256.
- `fisher_engine._numeric` owns binary64 bits, sequential arithmetic,
  log-sum-exp, and ordered softmax.
- `fisher_engine.preflight` owns descriptor parsing and PASS/FAIL receipts.
- `fisher_engine.candidate` owns provider manifests, alignment, exact/beam
  candidate construction, lineage, and candidate diagnostics.
- `fisher_engine.semantic` owns prediction audits, bounded endpoint selection,
  offline resolution, pair packets, structural plans, and E0 tensors.
- `fisher_engine.evaluation` owns universe/submission receipts, semantic closure,
  discrepancy accounting, and synthetic pair-metric arithmetic.
- `fisher_engine.artifacts` owns system, provider-execution, five-seed, and
  engine-envelope unions.
- `fisher_engine.source_closure` binds executed project source files.
- `fisher_engine.harness` integrates the complete synthetic E0 path.

The fixture and its non-hash acceptance projection are documented in
`examples/engine/README.md`.
