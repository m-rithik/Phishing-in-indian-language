# Fisher Synthetic Audit-Selector Rehearsal Contract

Status: **SYNTHETIC REHEARSAL ONLY — NOT HUMAN-AUDIT EVIDENCE**

Report/manifest version: `1.1.0`

Input-row version: `1.0.0`

Algorithm version: `fisher-audit-rehearsal-1.1.0`

## 1. Purpose and authority

`fisher_audit` is a deterministic, standard-library Python 3.11+ rehearsal of
the selection arithmetic frozen in the
[canonical human pilot safety and provenance
audit](research/ANNOTATION_GUIDE.md#canonical-human-pilot-safety-and-provenance-audit).
It exercises cell construction, the 10% ceiling, Hamilton allocation, seeded
HMAC ranking, and annotator-coverage supplements using explicit synthetic
metadata.

**OBSERVED:** the Annotation Guide is authoritative for the real human audit.
This contract does not amend it. **DERIVED:** a selector does not need message
text or governance evidence; it needs only the final cell states, item and
annotator identifiers, and a hash that binds each already frozen bundle.

The tool always reports `SYNTHETIC_REHEARSAL_ONLY` and `release_blocked: true`.
It cannot certify:

- execution of a human audit;
- a witnessed operating-system CSPRNG draw;
- completeness or pre-draw freeze of input manifests and hashes;
- completeness of the declared attempted-item universe;
- ethics, consent, provenance, registry, coverage, privacy, or governance approval;
- absence of any prohibited finding; or
- authorization to collect, release, train on, or evaluate authentic data.

It accepts no message text, source content, contact field, audit result, human
identity, timestamp, witness claim, or authentic-execution mode. Unknown fields
are rejected. This deliberately prevents the rehearsal file from becoming a
shadow corpus or a false audit certificate.

## 2. Command

From the repository root:

```console
python3 -m fisher_audit rehearse \
  --attempts examples/audit/attempts.synthetic.jsonl \
  --seed-hex 000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f \
  --scope SYNTHETIC_REHEARSAL_ONLY \
  --format text
```

`--format json` emits one canonical compact JSON object. The tool never creates
a seed. `--seed-hex` must be exactly 64 lowercase hexadecimal characters, which
decode to exactly 32 bytes. The explicit scope must be exactly
`SYNTHETIC_REHEARSAL_ONLY`; another value is rejected without being echoed.

Exit status is `0` only when the synthetic metadata is structurally valid and a
selection is produced, `1` for a validation/refusal result, and `2` for malformed
command syntax. Exit `0` is not a release, human-audit, or governance pass.

## 3. Synthetic attempted-item JSONL

The UTF-8 file contains exactly one JSON object per simulated retained `pilot`
or simulated adjudicated `excluded` attempt. Blank lines, a BOM, malformed UTF-8,
duplicate JSON keys, duplicate item IDs, and duplicate synthetic bundle hashes
are errors. The path must resolve directly to a regular file: directories,
symbolic links, FIFOs, sockets, and device nodes are rejected before content is
read. The operational bounds are 128 MiB, 32 KiB per line, and 100,000 records.

Every row has exactly these fields:

| Field | Requirement |
| --- | --- |
| `schema_version` | exactly `1.0.0` |
| `scope` | exactly `SYNTHETIC_REHEARSAL_ONLY` |
| `item_id` | full ASCII match `item_[a-z0-9][a-z0-9_-]{0,62}` |
| `simulated_partition` | `pilot` or `excluded` |
| `simulated_final_language_state` | one of the five canonical final language states |
| `simulated_final_primary_state` | `benign`, `phishing`, or `uncertain` |
| `simulated_provenance_class` | one of the four canonical provenance enum values |
| `blind_annotator_ids` | exactly two distinct ASCII annotator IDs, in ascending UTF-8 byte order |
| `final_annotator_id` | one ASCII annotator ID distinct from both blind annotators |
| `synthetic_bundle_sha256` | exactly 64 lowercase hexadecimal characters |

An annotator ID fully matches
`annotator_[a-z0-9][a-z0-9_-]{0,62}`. A simulated `pilot` row has a known study
language and binary primary state. A simulated `excluded` row has an uncertain
language and/or primary state. The word `authentic` inside a simulated provenance
enum exercises the frozen cell vocabulary; it does not assert that the synthetic
record is authentic.

`synthetic_bundle_sha256` is supplied rehearsal metadata that represents the hash
of an external, entirely invented bundle. The tool validates its encoding and
uniqueness but cannot recompute it because bundle content is intentionally absent.
It therefore cannot establish completeness, truth, or freeze timing.

## 4. Frozen selection arithmetic

The input file is the declared synthetic attempted universe. The tool sorts item
IDs by ascending UTF-8 bytes for canonicalization. It builds every nonempty cell
using the ASCII key:

```text
language_state|primary_state|provenance_class
```

For `N_attempted`, the prescribed main size is integer-exact
`ceil(0.10 * N_attempted) = (N_attempted + 9) // 10`. If
`N_attempted >= 1200` and the number of nonempty cells `H <= 60`, each cell first
receives one item. For the remaining `R = n - H` positions and remaining cell
capacities `C_h = N_h - 1`, allocation uses exact integer division of
`R * C_h / sum(C_h)`. Floors are assigned first; leftover positions follow
descending integer remainder, with ascending UTF-8 bytes of `cell_key` breaking
ties. Floating-point arithmetic is not used.

If `N_attempted < 1200` or `H > 60`, the entire declared universe is selected,
`fallback_entire_universe` and `revised_sampling_rule_required` are true, and the
result remains blocked. This is the exact protocol fallback, not an alternative
sampling rule.

Within a cell, ranking is the raw digest:

```text
HMAC-SHA256(
  key = the supplied 32 seed bytes,
  message = UTF8(cell_key + NUL + item_id)
)
```

The lowest digest wins. An identical-digest tie is broken by ascending UTF-8
bytes of `item_id`. Sampling is without replacement and every nonempty cell is
represented in the main sample.

## 5. Annotator supplements

After the main sample is fixed, the tool forms the ascending UTF-8 list of all
annotators absent from main-sample bundles. It processes that list in order. If
an earlier supplemental bundle also contains a later annotator, that later
annotator is already covered and no redundant bundle is added. Otherwise, the
tool adds the not-yet-selected item annotated by that annotator with the lowest
protocol HMAC digest and item-ID tie break. “Not-yet-selected” means absent from
both the frozen main sample and all supplements selected earlier in that same
ordered pass. The initially missing list is computed once and never recomputed,
reordered, or shortened. Each output supplement records its triggering annotator
and every annotator that bundle newly covered at the instant it was selected.

This is the frozen minimal-exposure interpretation: the initially missing list
does not change, but an entry triggers a selection only if that annotator is
still absent from the growing main-plus-supplement set. If no not-yet-selected
candidate exists for a still-absent annotator, selection fails closed with the
controlled `supplement_candidate_unavailable` diagnostic.

The report preserves `initially_missing_annotator_ids`, one ordered
`supplement_processing` record per initially missing annotator, and the complete
`final_covered_annotator_ids` and `final_uncovered_annotator_ids` sets. Processing
status is exactly `selected_supplement` or `skipped_already_covered`. A selected
status binds its item ID; a skipped status binds null. This makes the joint-
coverage decision explicit and replayable.

Supplements are disjoint from the main sample and from one another. They never
reduce, replace, or count toward main `n`.

The implementation constructs one HMAC-ranked candidate list for each annotator
from the validated universe, then advances past item IDs already selected. Each
attempt contributes exactly three annotator memberships. This preserves the
rule above without scanning the full universe once per missing annotator; it has
an `O(N log N)` upper bound for index construction and sorting under the fixed
three-annotator row schema, plus linear pointer advancement over memberships.

## 6. Deterministic evidence hashes

The JSON report contains:

- `input_file_sha256`: SHA-256 of the exact input bytes;
- `canonical_universe_sha256`: SHA-256 of canonical compact JSON for all validated
  rows sorted by item ID;
- `main_manifest_sha256`: SHA-256 of a `main_sample` envelope containing the
  ordered main-selection array;
- `supplement_manifest_sha256`: SHA-256 of an `annotator_supplements` envelope
  containing the ordered supplement array; and
- `selection_manifest_sha256`: SHA-256 of the algorithm version, scope, seed,
  canonical-universe hash, allocations, fallback state, main sample, and
  supplements plus their ordered processing trace and annotator-coverage sets.

Every main or supplement selection entry contains
`scope: SYNTHETIC_REHEARSAL_ONLY` and `release_blocked: true`. Each independently
hashed main/supplement envelope binds those same fields together with
`schema_version: 1.1.0`, algorithm version, manifest kind, and entries. The
selection-manifest core likewise binds report schema version, scope, and
`release_blocked: true`. Version `1.1.0` intentionally changes the three manifest
hashes from `1.0.0`; item selection and ordered supplement-processing semantics
do not change.

Canonical JSON uses sorted object keys, UTF-8, no insignificant whitespace, no
ASCII escaping requirement for Unicode, and no NaN. These hashes make identical
synthetic runs byte-comparable. They do not prove that a real manifest was frozen
before a witnessed seed draw.

## 7. Diagnostics and safety boundary

Diagnostics contain only a controlled severity, code, optional line number, and
controlled field name. They never include input values, JSON fragments, paths,
message text, or invalid command values. Successfully validated safe ASCII item
and annotator IDs appear in selection manifests because the manifest must identify
the selected synthetic bundles.

The example in `examples/audit/` contains no messages, persons, organizations,
routes, accounts, credentials, or contact information. Its 12 records deliberately
exercise the protocol's `<1200` full-universe fallback. It is not pilot evidence.
The rehearsal also does not enforce the complete dataset contract's balance,
ancestry, partition-eligibility, or provenance-share gates; those must pass in
`fisher_data` and the named human workflows before a real audit could begin.
