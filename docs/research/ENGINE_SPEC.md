# Fisher Engine Specification

> Status: **P0 METHOD CONTRACT — IMPLEMENTATION AND INDEPENDENT REVIEW PENDING**.
> Internal, embargoed, and pre-data. This document specifies the research engine;
> it does not report a corpus, trained model, performance result, or collection
> authorization.

## 1. Evidence and lifecycle boundary

- **OBSERVED:** no Fisher model, candidate resource, registry snapshot, or
  authentic corpus is currently frozen.
- **DERIVED:** the interfaces and equations below remove an information-flow
  circularity in the earlier design, but their benefit remains an empirical
  question.
- **ASSUMED:** a bounded candidate generator and an independently governed
  offline registry can be built with adequate language and entity coverage.
- **UNKNOWN:** exact checkpoints, dependencies, optimizer bounds, compute,
  latency, candidate coverage, registry coverage, and model performance.

The canonical lifecycle is:

| Stage | Acceptance meaning |
| --- | --- |
| `P0` | reconciled protocol and specification package |
| `D0` | collection authorization plus registry, coverage, and annotator preflight |
| `D1` | passed pilot plus audited 6,000-record corpus and `corpus-final` evidence |
| `E0` | pinned supported environment plus synthetic engine harness |
| `E1` | baseline engine |
| `E2` | candidate engine |
| `E3` | semantic factorial engine |
| `E4` | pre-protected, development-only engine, ablations, power analysis, and freeze |
| `E5` | confirmatory calibration, safety-threshold, and protected-evaluation package |

The demo is separately gated after scientific, privacy, security, rights, and IP
review; it is not an engine stage. Passing a stage never implies a later stage.

## 2. Information domains

### 2.1 Visible Message Packet

`VisibleMessagePacket` (`VMP`) is the only common message input. Under current
dataset-snapshot schema `1.2.0`, it is exactly the ordered pair of the immutable
`item.text` string and the non-gold, pre-annotation `item.visible_artifacts`
array. The required `item.vmp_sha256` binds the canonical JSON object
`{"text":item.text,"visible_artifacts":item.visible_artifacts}` under the byte
rules in
[DATA_CONTRACT.md](../DATA_CONTRACT.md#visible-non-gold-artifact-inventory-and-vmp).
Those bytes use recursively sorted object keys, compact separators,
`ensure_ascii=false`, no nonfinite numbers, preserved array order, and UTF-8.
Annotations consume this packet; they never construct, repair, or infer it.

Each visible-artifact entry has exactly `kind`, `kind_reason`,
`representation`, `start`, `end`, and `text`. Its half-open integer range is in
Unicode-code-point coordinates and `text` must equal the exact `item.text`
slice. `kind_reason` is 1–500 Unicode code points exactly for `OTHER` and empty
otherwise. Entries are unique, pairwise nonoverlapping, and sorted by
`(start,end,UTF-8(kind),UTF-8(representation),UTF-8(text))`. The
allowed kinds are `URL|DOMAIN|PHONE|UPI|BANK|EMAIL|APP|OTHER`; representations
are `TYPED_PLACEHOLDER|RESERVED|DEFANGED`. Typed placeholders are exactly
`[URL]`, `[DOMAIN]`, `[PHONE]`, `[UPI]`, `[BANK]`, `[EMAIL]`, `[APP]`, or
`[ARTIFACT]` for the corresponding kind. `RESERVED` accepts only the contract's
conservative optional-scheme/optional-`www` DNS grammar ending in `.example` or
`.invalid`, with its bounded path grammar and no port, query, fragment, or
surrounding prose. `DEFANGED` requires at least one exact contract marker:
`[.]`, `(.)`, `[at]`, `[redacted]`, `hxxp:`, `hxxps:`, or `XXXX`. Every
representation also passes the contract's global live-route and secret
scanners. These rules establish syntactic representation safety only; they do
not establish real-world authenticity, correct semantic type, collection
authority, or release authority. Only `TYPED_PLACEHOLDER` mechanically binds
kind to surface; `RESERVED` and `DEFANGED` kinds remain human-audited metadata.
A gold `destination_artifact` span must bind
exactly on `(start,end,text)` to one pre-existing inventory entry and its
qualifier must equal that entry's kind; there is no converse requirement.

It excludes provenance, source label, donor intent, simulation scenario, prompt,
campaign, grouping/component identifiers, registry data, annotations, and gold
labels. Non-span bytes are never rewritten during candidate construction.

### 2.2 Semantic Evidence Packet

`SemanticEvidencePacket` (`SEP`) is the bounded canonical pair audit packet
defined in Section 4 and bound to, but not embedding, the separate `VMP` through
`vmp_sha256`. The packet is produced only from model-predicted visible actor and
destination endpoint sets and the frozen offline resolver. Each pair contains
its deterministic compatibility state, coverage/completeness flags, and bounded
evidence identifiers; snapshot and resolver bindings are packet-level fields.
It never contains provenance, source labels, gold endpoints, the primary label,
or protected outcomes.

Human gold covers the primary label, subtype, language, facets, spans,
supporting evidence, and visible actor/destination endpoints. Registry-derived
`MATCH`, `MISMATCH`, or `UNKNOWN` is not blind human gold. Blind
annotators and the final adjudicator receive only the `VMP`. A separate blinded
registry reviewer resolves final visible endpoints against the frozen registry
without seeing the primary label, provenance, or protected outcomes. The result
is a separately versioned audited registry-reference artifact with only
`MATCH|MISMATCH|UNKNOWN` rows for explicit pairs. No explicit pair means zero
rows and implicit runtime resolver state `N/A`.

**OBSERVED:** independent repair replay now passes the historical schema `1.1.0`
dataset validator, including the two byte-bound probes recorded as `E07` in
[EXECUTION_STATUS.md](EXECUTION_STATUS.md#10-executable-evidence-checkpoints).
That scoped pass separates blind visible endpoints from three-state
registry-reference rows and rejects the retired annotation relation field.
**OBSERVED:** `E08` failed independent semantic review on five exact blockers;
`E09` independently passed the scoped schema-1.2 syntactic VMP repair; and
`E10` independently passed the original E08 repairs but failed four new
provider, endpoint/feature, boundedness, and metric-binding blockers. `E11`
then independently passed those live repairs but failed five further execution-
envelope, endpoint-numeric, E0-feature, evaluation-universe, and rewrite-
coordinate requirements. `E12` independently failed the fourth repair on five
later invalid-state, control-representation, universe/gold-binding, system-
provenance/five-seed, and candidate-diagnostic/q-arithmetic blockers. `E13`
then failed the fifth repair on three remaining preflight/run-union,
failure-accounting, and metric-input/counting groups. `E14` independently passed
all E13 repairs and the previously reviewed major contracts but found three new
engine-descriptor/parser, eligibility-outcome/accounting, and metric-universe/
denominator/algebra blocker groups. `E15` independently passed those E14 repairs
and the previously reviewed surfaces but found three remaining universe-input-
parser/count, structural-versus-semantic precedence, and nonempty-denominator
blocker groups. **P0 blocker:** this eighth local, universe-only semantic repair
requires fresh independent replay;
neither scoped data passes nor 101
non-engine tests completes the gate.

## 3. Candidate construction

The 2x2 factorial freezes one candidate provider/configuration and applies it to
all four cells. Each message run configures exactly one `COMPOSED_SPAN` or
`DIRECT_FULL_PATH` provider. Those modes remain separate named
configurations/runs/ablations and never pool readings or logits in one `q`.
`C00` and `C01` activate exactly the same returned rank-one path; `C10` and
`C11` activate every returned path with `q`. `IDENTITY_BYPASS` is a canonical
candidate-output artifact, not a configured provider. Raw identity occurs only
under `NO_ELIGIBLE_ROMANIZED_SPAN` or a controlled degraded provider/normalizer
fallback. A raw-text system is a separately named exploratory baseline and is
never a factorial cell. This restores the intended estimand: H1 changes path
activation while semantic consistency stays present, and H2 changes semantic
consistency while all-path activation stays fixed.

A successful composed/direct execution has `1 <= I <= 64` configured eligible
Romanized rewrite spans `i = 0..I-1`. For every configured or effective span,
`span_index`, `start`, and `end` are non-Boolean integers; indices are contiguous
from zero; `0 <= start < end <= len(VMP.text)`; `source_text` equals the exact
VMP slice; and spans are sorted, nonoverlapping, and visible-artifact-disjoint.
More than 64 spans is invalid, never truncated. A provider-failure execution
retains its attempted nonempty configured eligible spans in the execution
envelope while its identity output has no effective rewrite spans. A
no-eligible execution has no configured or effective spans. “Unicode code
point” means the scalar-value indexing used by the schema-1.2 Python validator;
UTF-8 bytes and UTF-16 code units are never offset units.

Every non-`INVALID` factorial run emits one provider-reading manifest as its
canonical candidate-output artifact. Its top-level JSON fields,
in exact order, are
`manifest_version,vmp_sha256,provider_config_id,provider_mode,normalizer_id,rewrite_spans,units`.
`manifest_version` is `"1.0.0"`; `provider_config_id` fully matches
`provider_[a-z0-9][a-z0-9_-]{0,62}`; `normalizer_id` fully matches
`normalizer_[a-z0-9][a-z0-9_-]{0,62}`; and `provider_mode` is exactly
`COMPOSED_SPAN|DIRECT_FULL_PATH|IDENTITY_BYPASS`.

Each `rewrite_spans` object has the exact configured/effective span predicate
above. Successful `COMPOSED_SPAN` and `DIRECT_FULL_PATH` manifests require
between one and 64 such spans. A canonical `IDENTITY_BYPASS` manifest requires
`rewrite_spans=[]` and represents only the effective identity output.

Each `units` object has exact ordered fields
`unit_index,unit_kind,start,end,source_text,readings`. `unit_index` values are
non-Boolean integers contiguous from zero. `COMPOSED_SPAN` has exactly one
`unit_kind=SPAN` unit corresponding one-to-one to each ordered `rewrite_spans`
object with the same index, range, and source text. `DIRECT_FULL_PATH` has exactly one
`unit_kind=FULL_PATH` unit with index zero, range `[0,len(VMP.text))`, and exact
full VMP text. `IDENTITY_BYPASS` has `units=[]` and fixed IDs
`provider_identity_bypass` and `normalizer_identity`.

Every reading object has exact ordered fields
`provider_rank,reading_text,reading_alignment,raw_logit_f64_bits`.
`provider_rank` is a non-Boolean integer in `1..8`, unique within its unit; the
unambiguous raw-reading identity is `(unit_index,provider_rank)`, so ranks may
reset across units. `raw_logit_f64_bits` is exactly 16 lowercase hexadecimal
characters encoding the big-endian IEEE-754 binary64 bits of a finite value;
negative zero is invalid and must be canonicalized to positive-zero bits before
serialization. Reading alignment is the canonical VMP-interval array below.

A span `reading_text` is at most 512 Unicode code points and 2,048 UTF-8 bytes.
Every direct reading and every normalized composed/full result is at most 20,000
Unicode code points and 80,000 UTF-8 bytes. The complete canonical provider
manifest is at most 4 MiB. Exceeding any span, path, count, or byte bound rejects
the message run; truncation is prohibited.

The manifest uses the declared field order recursively, compact UTF-8 JSON,
`ensure_ascii=false`, no whitespace, no terminal LF, no nonfinite number, and no
extra field.
SHA-256 of those exact bytes is `provider_reading_manifest_sha256`; the same
digest is carried as `provider_execution.provider_manifest_sha256` in the
engine run envelope.

Every candidate string carries an alignment with exactly one nonempty
contiguous half-open `VMP` interval `[start,end]` per output Unicode code point.
Mechanically, `0 <= start < end <= len(VMP.text)` for every entry, and both the
start sequence and end sequence are nondecreasing; equal and overlapping
intervals are allowed. An unchanged noncandidate code point `j` has identity
interval `[j,j+1]`. Every interval emitted for a rewrite lies wholly inside its
single source rewrite span, and the union of the emitted intervals covers every
source code point in that span. This is the complete monotonicity predicate.

The frozen candidate-only normalizer is an alignment-aware transducer
`(candidate_text,candidate_alignment) ->
(normalized_text,normalized_alignment)`. It may change text only within the
source rewrite span and must return one alignment entry per normalized output
code point satisfying the same bounds, nonempty, nondecreasing-start,
nondecreasing-end, within-one-span, and complete-source-coverage predicates.
Reject a reading if an input or output length differs from its alignment length;
an offset is a Boolean/non-integer/out of bounds; an interval is empty; either
monotonicity sequence decreases; an interval crosses or escapes its rewrite
span; any source code point is uncovered; the normalizer changes a noncandidate
code point; or a rewrite touches a visible artifact. `E0` permits only the
identity transducer; it does not test linguistic normalization.

The canonical alignment encoding is an ordered JSON array of
`[vmp_start,vmp_end]` base-10 integer pairs, one pair per normalized output code
point, encoded as UTF-8 with compact separators, no whitespace, no Boolean
offsets, and no leading zero or plus sign. Candidate identity is `(normalized
text, alignment)`; text-only identity was rejected because two readings can
render the same text while supporting different `VMP` evidence.

Lineage is an exact canonical JSON object. A composed contributor is
`{"mode":"COMPOSED_SPAN","units":[{"unit_index":i,"ranks":[...]},...]}`
with units in ascending index and ranks ascending and unique. A direct
contributor is
`{"mode":"DIRECT_FULL_PATH","unit_index":0,"ranks":[...]}` with ascending
unique ranks. A bypass contributor is `{"mode":"IDENTITY_BYPASS"}`. A
duplicate-merged full path stores
`{"lineage_version":"1.0.0","contributors":[...]}`, with contributor objects
sorted by their canonical UTF-8 bytes. The same compact, declared-order,
`ensure_ascii=false`, no-whitespace/no-extra-field JSON rules apply.

Every LSE operand is attached to one individual contributor and processed in
ascending contributor-byte order. Beam and final tie keys append the complete
lineage bytes after text and alignment bytes. A composed contributor may retain
per-unit rank sets compactly; no merge, lineage record, or audit expands their
exponential raw cross-product. Lineage is immutable and manifest-bound.

All `logsumexp` operations use finite IEEE-754 binary64 inputs, the stable
max-shift form, and sequential operations in canonical operand order: choose
`m=max(x)`, start `total=+0.0`, update
`total=binary64(total + exp(binary64(x-m)))` for each ordered operand, and return
`binary64(m + log(total))`. Canonicalize negative zero to positive zero before
ordering, hashing, comparison, or serialization. Bit-for-bit replay is claimed
only inside the pinned runtime/container, including its architecture and math
library; no universal cross-platform bit identity is claimed.

For `COMPOSED_SPAN`:

1. Apply the frozen candidate-only normalizer and merge duplicate span
   candidates with identical `(normalized text, alignment)` using the canonical
   contributor order and binary64 `logsumexp` above.
2. Normalize each span's merged logits:

   `a_ir = ell_ir - logsumexp_t(ell_it)`.

3. For a full-message hypothesis `h = (r_1, ..., r_I)`, preserve every non-span
   `VMP` byte and accumulate binary64 additions sequentially in the already
   frozen ascending source-span order:

   `s(h) = sum_i a_i,r_i`.

4. Merge full-message candidates only when both normalized text and complete
   alignment are identical, using canonical contributor order and binary64
   `logsumexp`.
5. Compare the overflow-safe product of post-span-merge candidate counts with
   64. If it is at most 64, enumerate exactly. Otherwise run a deterministic
   width-64 beam. A partial-candidate key is its emitted normalized prefix plus
   its encoded alignment. After every expansion, merge exact keys with
   canonical binary64 `logsumexp`, then prune by descending score, normalized
   UTF-8 text bytes, encoded-alignment bytes, and full-contributor identity.
6. Return at most `K = 8` candidates, sorted by descending score, normalized
   UTF-8 text bytes, encoded-alignment bytes, and full-contributor identity. Do
   not pad.

For `DIRECT_FULL_PATH`, apply the same alignment-aware normalizer and bounds to
the single full-path unit's at most eight readings, merge identical `(normalized
text,alignment)` outputs by canonical contributor order, normalize their
logits, and return at most eight under the same final ordering. It never enters
the composed exact/beam product. The full-path unit is an input envelope, not
permission to rewrite all of VMP: each reading preserves every code point
outside the manifest-bound `rewrite_spans` and every visible-artifact slice
exactly, and changes text/alignment only inside one of those spans under the same
within-span and complete-source-coverage rules. Any violation rejects the run.
For `IDENTITY_BYPASS`, return only the fixed
identity path and lineage.

For the returned bounded list,

`q_k = softmax(s(z_k) / T_tr)`.

The exact division, max-shift exponentiation, lineage-byte accumulation order,
runtime-bound exp backend, numerator/denominator persistence, and display-order
separation are frozen in Section 3.2. Resulting weights remain associated with
the returned display order.

`q` is described only as a calibrated distribution over the returned bounded
list, not as the posterior over every possible transliteration. Scores,
normalization, merge arithmetic, and ordering use float64; nonfinite values are
rejected, and signed zero is canonicalized to positive zero before comparison
or serialization. Every record logs exact-versus-beam mode, input and
post-merge counts, the exact span/partial/full/total merge reductions, returned
count, and `retained_preK_composition_mass_f64_bits`. Compute retained mass only
in the log domain. Let
`L_returned=LSE({s(h):h is returned})`, let
`L_preK=LSE({s(h):h is in the applicable duplicate-merged pre-K set})`, define
`Delta=L_returned-L_preK`, and persist `mass=exp(Delta)` using the bound math
backend. Each set's LSE operands are processed in ascending full-contributor-
lineage bytes. Both sets must be
nonempty and all operands, LSE values, `Delta`, and `mass` must be finite;
`Delta>0` is invalid and must not be clamped. Persist both LSEs and the mass as
the exact big-endian binary64 bit strings in `candidate_diagnostics` after
signed-zero canonicalization. `T_tr` affects only `q`, never these untempered
scores. `preK_scope=EXACT_FULL` means the complete exact/direct/identity,
duplicate-merged set. `preK_scope=FINAL_BEAM` means only the final width-bounded,
duplicate-merged pre-`K` beam and never total-lattice posterior mass. Direct
`sum(exp(s))` ratios were rejected because valid long paths can underflow to
`0/0`.

Candidate-generator configuration is selected using only
`transliteration_development`, lexicographically by:

1. highest minimum language `coverage@8`;
2. highest macro `coverage@8`;
3. highest macro `coverage@1`; then
4. ascending configuration-ID UTF-8 bytes.

Fit `T_tr` only after configuration selection, using group-disjoint,
message-level transliteration calibration data. Word-pair data may train or
screen a generator, but cannot establish multi-span calibration. Report the
selected frozen configuration once on `transliteration_evaluation`. Direct and
composed configurations may compete as separate development runs/ablations;
neither is presumed superior and their candidates are never pooled. An enabled candidate configuration
that returns no path is invalid except for exactly these frozen bypass modes:

- `NO_ELIGIBLE_ROMANIZED_SPAN`: one unchanged, identity-aligned raw path with
  `s=0` and `q=1`; and
- `PROVIDER_FAILURE_RAW_FALLBACK`: one unchanged, identity-aligned raw path with
  `s=0` and `q=1`, permitted as degraded only for provider/normalizer
  unavailability or timeout before accepted output and only when the identity
  fallback validates.

Provider failure remains in the engine accounting record but invalidates every
confirmatory/protected metric run and is never candidate-coverage success. An
empty enabled candidate set is invalid. The `E0` identity normalizer exists
only for synthetic interface tests and supplies no linguistic-normalization
evidence.

### 3.1 Canonical provider execution

The provider-reading manifest above is a candidate-output artifact; it does not
by itself explain why an identity output occurred. Every run that reaches
provider configuration contains one exact `provider_execution` object with
ordered fields
`configured_mode,provider_config_id,provider_config_sha256,normalizer_id,normalizer_sha256,eligible_spans,invocation_attempted,outcome,output_accepted,bypass_reason,failure_code,provider_manifest_sha256`.
`configured_mode` is `COMPOSED_SPAN|DIRECT_FULL_PATH`; every factorial cell
uses the same frozen mode, provider configuration hash, normalizer hash, and
candidate configuration recorded by its `SystemArtifactManifest`. Provider and
normalizer IDs obey the manifest grammars above; their SHA-256 values are 64
lowercase hexadecimal characters and are never null in an `EngineRunEnvelope`.
`eligible_spans` uses exact ordered
`span_index,start,end,source_text` objects and the coordinate predicate above.
`invocation_attempted` and `output_accepted` are JSON Booleans. `outcome` is
exactly
`NOT_INVOKED|ELIGIBILITY_INVALID|NO_ELIGIBLE|SUCCEEDED|UNAVAILABLE_FALLBACK|TIMEOUT_FALLBACK|PROVIDER_INVALID_OUTPUT|NORMALIZER_INVALID_OUTPUT`.
`bypass_reason` is
`NONE|NO_ELIGIBLE_ROMANIZED_SPAN|PROVIDER_FAILURE_RAW_FALLBACK`.
`failure_code` is
`NONE|ELIGIBILITY_INVALID|PROVIDER_NOT_INVOKED|PROVIDER_UNAVAILABLE|PROVIDER_TIMEOUT|NORMALIZER_UNAVAILABLE|NORMALIZER_TIMEOUT|PROVIDER_INVALID_OUTPUT|NORMALIZER_INVALID_OUTPUT`.
`provider_manifest_sha256` is the SHA-256 of the accepted canonical
provider-reading manifest. It is nonnull if and only if `output_accepted=true`;
otherwise both are respectively null and false. Acceptance may cover the
configured provider output or the canonical identity output; malformed raw
provider/normalizer material is never hashed into this field.

The outcome table is exact:

| Outcome | Eligible spans / invocation | Bypass / failure | Accepted manifest | Required engine result |
| --- | --- | --- | --- | --- |
| `NOT_INVOKED` | 1..64 / false | `NONE` / `PROVIDER_NOT_INVOKED` | false / null | `INVALID` at `PROVIDER_EXECUTION` |
| `ELIGIBILITY_INVALID` | empty / false | `NONE` / `ELIGIBILITY_INVALID` | false / null | `INVALID` at `PROVIDER_EXECUTION`; sole code `engine_invalid_eligibility` |
| `NO_ELIGIBLE` | empty / false | `NO_ELIGIBLE_ROMANIZED_SPAN` / `NONE` | true / canonical identity hash | may continue |
| `SUCCEEDED` | 1..64 / true | `NONE` / `NONE` | true / canonical configured-output hash | may continue |
| `UNAVAILABLE_FALLBACK` | attempted 1..64 / true | `PROVIDER_FAILURE_RAW_FALLBACK` / `PROVIDER_UNAVAILABLE` or `NORMALIZER_UNAVAILABLE` | true / canonical identity hash | `DEGRADED_STOP_AFTER_IDENTITY` |
| `TIMEOUT_FALLBACK` | attempted 1..64 / true | `PROVIDER_FAILURE_RAW_FALLBACK` / `PROVIDER_TIMEOUT` or `NORMALIZER_TIMEOUT` | true / canonical identity hash | `DEGRADED_STOP_AFTER_IDENTITY` |
| `PROVIDER_INVALID_OUTPUT` | attempted 1..64 / true | `NONE` / `PROVIDER_INVALID_OUTPUT` | false / null | `INVALID` at `PROVIDER_EXECUTION` |
| `NORMALIZER_INVALID_OUTPUT` | attempted 1..64 / true | `NONE` / `NORMALIZER_INVALID_OUTPUT` | false / null | `INVALID` at `PROVIDER_EXECUTION` |

`ELIGIBILITY_INVALID` is selected before dispatch when the configured selector
output is not an array; contains more than 64 entries; or any member has a
Boolean/noninteger/out-of-range/empty range, wrong exact slice, overlap,
artifact contact, or noncanonical order. It retains `eligible_spans=[]`, never
serializes an unsafe selector member, and sets `invocation_attempted=false`,
`output_accepted=false`, and `provider_manifest_sha256=null`. The configured
provider/normalizer IDs and hashes remain present. Its
`configured_span_entries_capped` follows the array-length rule below,
`eligible_spans_capped=0`, and every later safe-unit count is zero. Static
registry fields still follow the system mask; execution is `INVALID` with
`failure_stage=PROVIDER_EXECUTION` and
`invalid_codes=["engine_invalid_eligibility"]`. `NOT_INVOKED` is the
fail-closed outcome when the preflight-valid static configuration exists but
dispatch cannot begin and no accepted identity fallback exists. Invalid
provider/normalizer output is structurally rejected before candidate acceptance
and can never be downgraded. These three invalid output outcomes plus
`ELIGIBILITY_INVALID` are failure records, not “valid provider combinations.” The sole
degraded policy applies only when no nonidentity candidate output was accepted
and the exact raw identity manifest/path independently passes every VMP,
alignment, bound, numeric, manifest, and hash predicate.

An invalid rewrite, alignment, arithmetic, or bound discovered after an
accepted canonical provider manifest is a `CANDIDATE` failure and retains that
accepted manifest under the stage table; it is never relabeled
`ELIGIBILITY_INVALID`.

Both bypass outputs have `effective_rewrite_spans=[]`; a degraded execution
retains attempted spans only in `provider_execution`. Identical identity-output
manifest hashes are valid because the enclosing envelope binds cause,
configuration, attempted spans, invocation, and status. A valid no-eligible
identity remains eligible for metrics; a degraded fallback invalidates every
confirmatory or protected metric run. `E0` tests accounting only and makes no
provider-robustness claim.

### 3.2 Canonical system artifact manifest and engine run envelope

Engine input, preflight, and per-item execution are separate artifact domains.
The normative `EngineInputDescriptor` schema `1.0.0` has exact top-level field
order
`schema_version,run_id,condition,system_id,system_variant,system_artifact_manifest_sha256,item_id,vmp_sha256`.
`run_id`, system ID, condition, variant, item ID, and SHA-256 values use their
existing safe grammars and enums. There are no other fields. The descriptor
references a separately supplied `SystemArtifactManifest` byte artifact and
separately supplied validated schema-1.2 item/VMP bytes by SHA-256. The engine
interface receives those bytes independently and verifies both hashes; no
filesystem path, URI, mutable object handle, or lookup location is semantically
bound.

Descriptor bytes are compact canonical UTF-8 JSON with recursively declared
field order, `ensure_ascii=false`, no BOM, CR, insignificant whitespace, extra
field, nonfinite number, or terminal LF, and NFC in every string. The exact cap
is 1,048,576 bytes. A valid `SystemArtifactManifest` and validated VMP/item are
mandatory preconditions for `EngineRunEnvelope`; preflight always emits one
receipt, and only a `PASS` receipt permits an envelope.

The raw parser reads at most 1,048,577 bytes and applies this total one-code
precedence:

1. `preflight_descriptor_too_large`;
2. `preflight_descriptor_bom`;
3. `preflight_descriptor_invalid_utf8`;
4. `preflight_descriptor_duplicate_key`;
5. `preflight_descriptor_nonfinite`;
6. `preflight_descriptor_invalid_json`;
7. `preflight_descriptor_non_nfc`;
8. `preflight_descriptor_noncanonical_bytes`;
9. `preflight_descriptor_schema_or_enum`;
10. `preflight_missing_referenced_artifact`;
11. `preflight_artifact_hash_mismatch`;
12. `preflight_invalid_system_manifest`; and
13. `preflight_invalid_vmp`.

After strict UTF-8 decoding, a deterministic JSON token scanner uses duplicate-
key and nonfinite hooks. It stops at the first unrecoverable syntax event. Among
events safely observed before that stop, duplicate key wins over nonfinite,
which wins over other JSON syntax, irrespective of byte offset. It performs no
error recovery beyond the first syntax event. `NON_NFC` checks every decoded
string. `NONCANONICAL_BYTES` then reserializes the parsed value under the exact
descriptor rules and requires byte equality. `SCHEMA_OR_ENUM` checks exact
fields, types, grammars, and enums. Artifact
existence for both references is checked before either hash; both hashes are
checked before either artifact is validated; the system manifest is validated
before the VMP/item. This freezes all joint-failure precedence.
“Missing” means the corresponding separately supplied byte-artifact input is
absent; preflight performs no filesystem or URI discovery.

`EnginePreflightReceipt` schema `1.0.0` has exact top-level field order
`schema_version,preflight_id,submitted_descriptor_sha256,submitted_prefix_sha256,prefix_bytes_hashed,observed_bytes,run_id,condition,system_id,system_variant,system_artifact_manifest_sha256,item_id,vmp_sha256,decoded_descriptor_count,validated_system_manifest_count,validated_vmp_count,failure_stage,invalid_codes,status`.
`preflight_id` matches
`engine_preflight_[a-z0-9][a-z0-9_-]{0,55}`. If EOF is observed within the cap,
`submitted_descriptor_sha256` hashes the complete raw descriptor,
`submitted_prefix_sha256=null`, `prefix_bytes_hashed=0`, and `observed_bytes` is
the exact non-Boolean length in `0..1048576`. If the cap is exceeded, the full
hash is null, the prefix hash covers exactly the first 1,048,577 bytes,
`prefix_bytes_hashed=1048577`, and `observed_bytes="GE_1048577"`. The reader
never consumes another byte.

The three counts are non-Boolean integers in `{0,1}`.
`decoded_descriptor_count=1` only after canonical bytes plus exact descriptor
schema/enums pass; it is zero for codes 1–9. The system-manifest count becomes
one only after its supplied bytes, hash, complete source closure, environment,
descriptor-to-manifest system/condition/variant identity, and static
bindings pass. The VMP count becomes one only
after the system count is one and the supplied item/VMP bytes, schema, and hash
pass. Because existence and hashes precede validation, counts remain zero for
codes 10–11; code 12 has both validation counts zero; code 13 has system count
one and VMP count zero.

The receipt is an exact union. `PASS` has all seven descriptor reference fields
nonnull and equal to the validated descriptor, all counts one,
`failure_stage=NONE`, and `invalid_codes=[]`. `FAIL` sets all seven reference
fields to null, uses `failure_stage=SOURCE_OR_CONFIG` for codes 1–12 or `VMP`
for code 13, and has `invalid_codes` equal to the one-element array containing
the first applicable code above. It never contains an exhaustive list. No raw
text, path, unsafe identifier, provider output, malformed field, or external
identifier is retained. `FAIL` emits no `EngineRunEnvelope`.

The receipt uses recursively declared field order, compact UTF-8 JSON,
`ensure_ascii=false`, NFC strings, no BOM, CR, whitespace, terminal LF, extra
field, or nonfinite number, and at most 64 KiB. Its exact-byte SHA-256 is
`engine_preflight_receipt_sha256`.

Every engine run envelope binds one already valid `SystemArtifactManifest`
schema `1.0.0`. Its exact
top-level field order is
`schema_version,system_id,condition,system_variant,executed_source_closure,registry_binding,provider_binding,model_binding,resource_binding,environment_binding,analysis_binding`.
`system_id` matches `system_[a-z0-9][a-z0-9_-]{0,62}`; `condition` is
`C00|C10|C01|C11`; and `system_variant` is
`BASE|CAPACITY_CONTROL|SUPERVISION_CONTROL`. Only these eight combinations are
valid:

| Condition | Allowed variant | Active paths | Inference semantic artifacts |
| --- | --- | --- | --- |
| `C00` | `BASE` | returned rank one | prohibited |
| `C10` | `BASE` | all returned paths | prohibited |
| `C01` | `BASE` | returned rank one | required |
| `C11` | `BASE` | all returned paths | required |
| `C00` | `CAPACITY_CONTROL` | returned rank one | prohibited; matched to base `C01` |
| `C10` | `CAPACITY_CONTROL` | all returned paths | prohibited; matched to base `C11` |
| `C01` | `SUPERVISION_CONTROL` | returned rank one | prohibited at inference; matched to base `C01` |
| `C11` | `SUPERVISION_CONTROL` | all returned paths | prohibited at inference; matched to base `C11` |

The exact artifact mask permits prediction audit, SEP, and feature plan/tensor
only for `BASE/C01` and `BASE/C11`, and requires them there only for a `VALID`
run. Every other allowed combination stores `prediction_audit_sha256=null`,
empty SEP/feature arrays, and `feature_plan_id=null`. Direct registry identity
is a static system binding rather than a downstream semantic output: its three
envelope fields are nonnull for `BASE/C01` and `BASE/C11` and null for every
other mask under every execution status. Supervision controls
may use endpoint/span labels and losses during training, but no endpoint output,
SEP, resolver call, registry value, feature plan/tensor, or semantic missingness
is constructed or exposed at inference. Capacity controls use an ordinary
trainable capacity adapter only at a later model checkpoint. `E0` validates
manifest/mask arithmetic and does not claim a trained control.

`executed_source_closure` has exact ordered fields
`closure_version,collection_method,declared_entrypoints,files,closure_sha256`.
The first two values are `"1.0.0"` and
`INSTRUMENTED_IMPORT_AND_EXECUTED_FILE_ACCESS_V1`. `declared_entrypoints` is a
sorted unique array of 1..64 safe repository-relative POSIX paths. `files` is a
sorted unique array of 1..4,096 exact `path,sha256` objects and must equal every
project source file loaded, imported, or opened as executable code for that path
by the pinned import hook, executed-file-access hook, and declared-entrypoint
audit. The closure collector, bootstrap, and entrypoints are themselves in the
list. Inability to observe dynamic execution or reconcile a declared entrypoint
is invalid; an arbitrary hand-selected subset is never accepted.
`closure_sha256` hashes the exact canonical ordered object
`closure_version,collection_method,declared_entrypoints,files` without the hash
field. This is replay evidence for the bound runtime, not proof that every
platform exposes execution identically.

A safe source path has one or more slash-separated components; each component
starts with ASCII alphanumeric or underscore and then contains only ASCII
alphanumeric, underscore, hyphen, or dot. Absolute paths, empty or `.`/`..`
components, backslashes, control characters, and leading/trailing slash are
invalid. Every SHA-256 is 64 lowercase hexadecimal characters over exact bytes.

`registry_binding` has exact ordered fields
`registry_snapshot_id,registry_artifact_sha256,resolver_version,resolver_source_manifest_sha256`.
All are nonnull and obey the registry/data grammars only for semantic base
systems; all are null under every other artifact mask. The direct registry
artifact hash must equal the registry manifest's declared artifact hash and the
engine-envelope value.

`provider_binding` has exact ordered fields
`provider_config_id,provider_config_sha256,normalizer_id,normalizer_sha256,candidate_configuration_sha256,provider_source_manifest_sha256`.
All six are nonnull for every factorial system, obey the provider/normalizer ID
grammars, and bind the one frozen candidate configuration shared by the four
base cells and their matched controls.

`model_binding` is null only for an E0 base-system manifest. Otherwise it has
exact ordered fields
`binding_stage,model_id,checkpoint_sha256,model_config_sha256,matched_system_id,matched_system_artifact_manifest_sha256,capacity_adapter_sha256,auxiliary_supervision`.
`binding_stage` is `E0|E3|E4`; IDs use the safe system-ID suffix grammar and
hashes are lowercase SHA-256 or null. At `E0`, implementation hashes may be null
and the object exists only when needed to bind a control's matched system. At
`E3|E4`, model/checkpoint/config hashes are nonnull. Base systems have null
matched/capacity fields and `auxiliary_supervision=false`. A capacity control
binds the exact matched semantic-base system ID and artifact-manifest hash,
requires a nonnull capacity-adapter hash at `E3|E4`, and uses false. A
supervision control binds its same-condition semantic base, has no capacity
adapter, and uses true. Matching provider/config, encoder family, risk-head
shape, and training budget is separately audited; an ID alone is not evidence.

`resource_binding` is always an object with exact ordered fields
`binding_stage,resource_manifest_sha256,synthetic_fixture_manifest_sha256`.
E0 requires stage `E0`, null real-resource hash, and a nonnull synthetic fixture
hash. E3/E4 require the corresponding stage, nonnull real-resource hash, and
null synthetic-fixture hash. `environment_binding` has exact ordered fields
`runtime_tag,python_implementation,python_version,unicode_version,platform_tag,architecture,math_backend_id,math_backend_sha256,float_contract,container_image_digest`.
Every identity string fully matches `[A-Za-z0-9][A-Za-z0-9._-]{0,127}`;
version strings use two
through four unsigned dot-separated integer components; the float contract is
`IEEE754_BINARY64_RNE`. The math-backend hash is nonnull. E0 may use a null OCI
digest; E3/E4 require `sha256:` followed by 64 lowercase hexadecimal characters.
`analysis_binding` has exact ordered fields
`analysis_source_manifest_sha256,analysis_config_sha256`, both nonnull.
E0 still requires exact engine/analysis closure, runtime/platform/math backend,
synthetic provider/resource fixtures, and a synthetic registry fixture wherever
the semantic artifact mask permits registry use; it does not require future
model, checkpoint, real-resource, or container hashes.

The manifest uses recursively declared field order, compact UTF-8 JSON,
`ensure_ascii=false`, no whitespace, no terminal LF, no extra field, and no
nonfinite value; it is at most 4 MiB. SHA-256 of exact bytes is
`system_artifact_manifest_sha256`. Actual future artifact values remain
**UNKNOWN** until produced and audited.

The engine run envelope schema version is `1.1.0`. Its exact top-level order is
`schema_version,run_id,condition,system_id,system_variant,system_artifact_manifest_sha256,runtime,vmp,provider_execution,failure_stage,failure_counts,candidate_diagnostics,candidate_paths,active_path_ids,five_seed_logit_artifact_sha256,prediction_audit_sha256,sep_packet_hashes,feature_plan_id,feature_tensor_hashes,registry_snapshot_id,registry_artifact_sha256,resolver_version,execution_status,invalid_codes`.
`run_id` matches `engine_run_[a-z0-9][a-z0-9_-]{0,62}`. Condition, system ID,
variant, runtime, bindings, and artifact mask exactly equal the referenced
system manifest. Run ID, condition, system identity/variant, system-manifest
hash, item ID, and VMP hash exactly equal the preceding `PASS` receipt.
`system_artifact_manifest_sha256`, `runtime`, and `vmp` are
valid and nonnull in every envelope. `provider_execution` is also always the
exact object in Section 3.1; `NOT_INVOKED` represents failure before a call.
`runtime` has exact ordered fields
`runtime_tag,python_implementation,python_version,unicode_version,platform_tag,architecture,math_backend_id,math_backend_sha256,float_contract` and equals
the corresponding environment-binding values. `vmp` has exact ordered fields
`item_id,vmp_sha256` and obeys schema-1.2 rules.

`failure_stage` is
`NONE|PROVIDER_EXECUTION|CANDIDATE|PREDICTION|SEP|FEATURE|BINDING|ENVELOPE`.
The primary failure is the earliest observed stage in the exact pipeline order
`PROVIDER_EXECUTION < CANDIDATE < PREDICTION < SEP < FEATURE < BINDING < ENVELOPE`.
Execution aborts before every later stage. Source/configuration and VMP failures
are preflight failures and are not envelope stages.
`failure_counts` has exact ordered fields
`total,configured_span_entries_capped,eligible_spans_capped,provider,normalizer,candidate,alignment,prediction,sep,feature,binding,envelope`.
`configured_span_entries_capped` is a non-Boolean integer in `0..65`: zero when
the selector result is not an array, otherwise `min(array_length,65)` regardless
of member validity. `eligible_spans_capped` is a non-Boolean integer in `0..64`
equal to the number of configured spans accepted as one complete valid set; it
is zero for `ELIGIBILITY_INVALID` and `NO_ELIGIBLE`. Every other category value
is a non-Boolean integer in `0..65534` or the exact saturation sentinel
`GE_65535`. Such a category is the exact number of completely decoded and
validated safe units available at completion or abort when below 65,535,
otherwise the sentinel. The offending unit does not count; every unexecuted
later-stage field is zero. `total` is the same capped/sentinel result over the
stored first two counts plus the uncapped sum of the remaining nine validated-
unit counts. These are safe-progress counts, not defect counts, and never retain
unsafe rows, text, surfaces, external IDs, or diagnostic payloads.

The field-to-unit mapping is exact: the first two span fields follow the selector
rules above; `provider` counts validated provider-reading
objects; `normalizer` counts validated normalized-reading outputs; `candidate`
counts validated complete candidate-path objects; `alignment` counts validated
`[vmp_start,vmp_end]` pairs across those paths; `prediction` counts validated
endpoint-candidate objects; `sep` counts validated canonical pair objects;
`feature` counts validated real feature rows; `binding` counts successful
equalities in this fixed order—system-manifest hash, condition, system ID,
variant, VMP hash, active-path list, five-seed hash, then each active path hash,
registry snapshot, registry artifact hash, resolver version, each SEP path/hash,
and each feature path/hash; and `envelope` counts validated top-level fields in
declared envelope order. A null/not-applicable binding contributes no unit.

Whenever retained by the status/stage table below, `candidate_diagnostics` has exact ordered fields
`mode,temperature_f64_bits,search_mode,input_count,span_merge_reduction_count,partial_merge_reduction_count,full_merge_reduction_count,total_merge_reduction_count,postmerge_count,returned_count,preK_scope,L_returned_f64_bits,L_preK_f64_bits,retained_preK_composition_mass_f64_bits,q_normalizer_f64_bits,q_max_f64_bits`.
`mode` is `COMPOSED_SPAN|DIRECT_FULL_PATH|IDENTITY_BYPASS`; `search_mode` is
`EXACT|BEAM|DIRECT_FULL_PATH|IDENTITY_BYPASS`; valid mode/search pairs are the
obvious composed exact/beam, direct/direct, and identity/identity pairs.
`preK_scope` is `EXACT_FULL|FINAL_BEAM`; only composed beam uses `FINAL_BEAM`.
All counts are exact non-Boolean integers. `input_count` is the total raw
provider-reading count across all composed units, the direct unit's raw reading
count, or one for identity. `postmerge_count` is the number of complete
duplicate-merged candidates in the applicable `preK` set. Input is `1..512`, postmerge is
`1..64`, returned is `1..8` and no greater than postmerge, and every merge-
reduction count is `0..65535` or the run is invalid rather than saturated.

For every duplicate merge group `g`, its reduction is `|g|-1`. The span count
is the sum across post-normalization duplicate groups within source spans; the
partial count is the sum across duplicate partial-prefix groups after every
beam expansion; the full count is the sum across duplicate complete-message
groups, including direct-mode groups; and total is their exact sum. Exact
composed mode has partial count zero; direct mode has span/partial zero; identity
has all four zero with input/postmerge/returned equal to one.

All `*_f64_bits` fields are exactly 16 lowercase big-endian IEEE-754 binary64
bits for finite values; negative zero is invalid and is canonicalized to
positive zero. Temperature is positive. Retained mass remains exactly
`exp(LSE(returned)-LSE(preK))`; both LSEs use untempered composition scores.
`EXACT_FULL` binds the complete exact/direct/identity duplicate-merged pre-K set;
`FINAL_BEAM` binds only the final width-bounded merged beam. Empty, nonfinite,
or positive-delta results are invalid and never clamped.

For every returned score `s_k`, compute
`t_k=binary64(s_k/T_tr)`, choose the finite numeric maximum `m`, compute
`n_k=binary64(exp(binary64(t_k-m)))` using the runtime-bound exp backend, then
sum `n_k` sequentially from binary64 `+0.0` in ascending canonical full-
contributor-lineage bytes. The result is `q_normalizer`; compute
`q_k=binary64(n_k/q_normalizer)`. Candidate display order never changes this
accumulation order. Persist the denominator and the max-shift value `m` in diagnostics
as `q_normalizer_f64_bits` and `q_max_f64_bits`; persist each numerator and q in
its path. Bitwise replay is promised only under the bound E0 runtime/platform/
math backend; E3/E4 additionally require the container binding. No universal
cross-platform bit claim is made.

`candidate_paths` contains 1..8 objects in final display order with exact fields
`path_id,path_sha256,lineage,composition_score_f64_bits,q_numerator_f64_bits,q_f64_bits,effective_rewrite_spans`.
Path IDs/hashes, lineage, scores, q values, and spans obey the existing contracts.
`active_path_ids` is exactly the first returned path for `C00|C01` and exactly
all returned paths in their display order for `C10|C11`. A bypass has one
identity path, so both rules select that same path.

`five_seed_logit_artifact_sha256` and `prediction_audit_sha256` are null or
lowercase SHA-256 values. SEP and feature arrays contain exact ordered
`path_id,sha256` objects in active-path order. `feature_plan_id` is null or
`E0_VMP_CATEGORY_MEAN_V1`. In every envelope, including `INVALID` and degraded,
the three direct registry fields are all nonnull and exactly equal the system
manifest for `BASE/C01|C11`, and all null under every other artifact mask.
When SEP packets are retained, their registry identities must also equal them.
`execution_status` is
`VALID|DEGRADED_STOP_AFTER_IDENTITY|INVALID`. `invalid_codes` is a sorted
unique array from the closed safe set
`engine_invalid_eligibility|engine_provider_not_invoked|engine_provider_invalid_output|engine_normalizer_invalid_output|engine_candidate_invalid_arithmetic|engine_candidate_nonfinite|engine_candidate_invalid_alignment|engine_prediction_invalid_audit|engine_prediction_nonfinite|engine_sep_invalid_packet|engine_feature_invalid_tensor|engine_feature_nonfinite|engine_binding_invalid_system|engine_binding_invalid_environment|engine_binding_invalid_registry|engine_binding_invalid_condition_mask|engine_binding_invalid_path|engine_envelope_invalid_payload`.
For `INVALID`, it contains only codes whose prefix maps to the primary stage:
`engine_invalid_eligibility` and `engine_provider_*`/`engine_normalizer_*` to `PROVIDER_EXECUTION`,
`engine_candidate_*` to `CANDIDATE`, `engine_prediction_*` to `PREDICTION`,
`engine_sep_*` to `SEP`, `engine_feature_*` to `FEATURE`, `engine_binding_*` to
`BINDING`, and `engine_envelope_*` to `ENVELOPE`.

The status union is exact:

- `VALID`: `failure_stage=NONE`; every failure count equals its fully completed
  safe-unit total under the rules above; `invalid_codes=[]`;
  provider execution, diagnostics, 1..8 paths, exact active paths, and the
  five-seed artifact are nonnull/complete; and the prediction/SEP/feature/
  registry fields exactly follow the artifact-mask table.
- `DEGRADED_STOP_AFTER_IDENTITY`: `failure_stage=PROVIDER_EXECUTION`;
  `invalid_codes=[]`; outcome is exactly `UNAVAILABLE_FALLBACK` or
  `TIMEOUT_FALLBACK`; the accepted canonical identity manifest, identity
  diagnostics, one identity path, and its active ID are complete. Processing
  stops there: `five_seed_logit_artifact_sha256=null`,
  `prediction_audit_sha256=null`, SEP/feature arrays are empty, and
  `feature_plan_id=null`, including for semantic base systems. The direct
  registry fields still follow the static system mask. Failure counts contain
  only safe units actually validated through the identity fallback; all
  unexecuted downstream fields are zero. Every confirmatory/protected metric
  manifest rejects this envelope.
- `INVALID`: `failure_stage` is non-`NONE`; `invalid_codes` is nonempty and
  primary-stage-coherent. The system-artifact hash, runtime, VMP, and direct
  registry fields always remain valid and nonnull/null exactly as their static
  mask requires. The exact retention table below applies; no malformed,
  partially decoded, or invented artifact is serialized.

| Primary failure stage | Provider execution | Candidate diagnostics / paths / active IDs | Five-seed / prediction audit | SEP hashes | Feature plan / tensor hashes |
| --- | --- | --- | --- | --- | --- |
| `PROVIDER_EXECUTION` | exact `ELIGIBILITY_INVALID`, `NOT_INVOKED`, `PROVIDER_INVALID_OUTPUT`, or `NORMALIZER_INVALID_OUTPUT`; output false/hash null | null / empty / empty | null / null | empty | null / empty |
| `CANDIDATE` | accepted `SUCCEEDED` or `NO_ELIGIBLE`; manifest hash retained | null / empty / empty | null / null | empty | null / empty |
| `PREDICTION` | accepted object retained | fully validated objects retained | null / null | empty | null / empty |
| `SEP` | accepted object retained | fully validated objects retained | validated five-seed retained; prediction audit retained when the mask permits | empty | null / empty |
| `FEATURE` | accepted object retained | fully validated objects retained | validated five-seed/prediction bindings retained by mask | fully validated SEP hashes retained | null / empty |
| `BINDING` | accepted object retained | fully validated objects retained | fully validated objects retained by mask | fully validated hashes retained by mask | fully validated plan/tensor hashes retained by mask |
| `ENVELOPE` | accepted object retained | fully validated objects retained | fully validated objects retained by mask | fully validated hashes retained by mask | fully validated plan/tensor hashes retained by mask |

An `ENVELOPE` primary failure means assembly of the intended valid payload
failed; that payload is discarded and the safe canonical `INVALID` union above
is emitted. If even this fail-closed envelope cannot satisfy its own canonical
serialization, size, and hash contract, no engine envelope or result is
claimed.

The envelope uses canonical declared-order compact UTF-8 JSON with
`ensure_ascii=false`, no whitespace, no terminal LF, no extra field, no
nonfinite number, and at most 1 MiB. SHA-256 of exact bytes is
`engine_run_envelope_sha256`; no informal candidate trace or second run hash is
accepted.

### 3.3 Canonical five-seed logit artifact

`FiveSeedLogitArtifact` schema `1.0.0` is used only for deterministic arithmetic
known-answer tests in E0 and real system aggregation in E3/E4. Its exact
top-level order is
`schema_version,system_artifact_manifest_sha256,vmp_sha256,active_path_ids,seeds,seed_logits_f64_bits,mean_logits_f64_bits`.
`active_path_ids` exactly equals the envelope order and `seeds` is exactly
`[11,23,37,53,71]`. `seed_logits_f64_bits` is an outer array of five rows in
that seed order, each with one 16-character finite binary64 bit string per active
path; `mean_logits_f64_bits` has one such value per active path. Missing,
additional, nonfinite, or negative-zero values invalidate the artifact and run.

For each path, begin with binary64 `+0.0`, add the five decoded logits
sequentially in the exact seed order with binary64 rounding after each addition,
then divide in binary64 by binary64 `5.0`; canonicalize negative zero. Canonical
declared-order compact UTF-8 JSON uses `ensure_ascii=false`, no whitespace,
no terminal LF, no extra field, and no nonfinite value and is at most 1 MiB. SHA-256 of
exact bytes is `five_seed_logit_artifact_sha256`. E0 uses synthetic finite
known-answer logits only; it claims no trained model or checkpoint. The scalar-
temperature optimizer remains **UNKNOWN** and must freeze before E4.

## 4. Factorial engine and canonical pair packets

For candidate path `k`, semantic conditions predict bounded, deduplicated sets
of visible actor endpoints `A_k` and visible destination endpoints `D_k`. Every
endpoint is represented only in half-open `VMP` code-point coordinates; a head
must predict those coordinates directly and may never emit a candidate offset
for later back-projection. Each role has an engineering cap of eight endpoints.
This is a resource bound, not an observed coverage or performance result.

The endpoint audit object has exact ordered fields
`role,start,end,kind,lookup_surface,lookup_status`. Actor endpoints use
`role=ACTOR,kind=NONE`; destination endpoints use `role=DESTINATION` and one
schema-1.2 controlled kind `URL|DOMAIN|PHONE|UPI|BANK|EMAIL|APP|OTHER`.
`start,end` are non-Boolean integers with
`0 <= start < end <= len(VMP.text)`. `lookup_status` is `ALIGNED|UNALIGNED`.
For `ALIGNED`, `lookup_surface` is exactly the frozen deterministic candidate
renderer output and is bounded by 20,000 Unicode code points and 80,000 UTF-8
bytes. For `UNALIGNED`, it is exactly the empty string.

A finite score exists only in a separate prediction-audit record and never in
the pair packet or learned view. Deduplication identity excludes score and is
the complete endpoint audit tuple; retain the highest-scored duplicate. Select
at most eight per role by descending finite score, then start/end, kind UTF-8,
lookup-status UTF-8, and lookup-surface UTF-8. Log pre-cap count and cap hit.
After the cap, reorder endpoints and pairs independently of score: actors by
`(start,end,UTF-8(lookup_surface))`, then destinations by
`(start,end,UTF-8(kind),UTF-8(lookup_surface))`. Score-derived order is never
visible to the packet or risk head.

### 4.1 Canonical prediction audit

The prediction audit schema version is `1.0.0`. Its exact top-level field order
is `schema_version,vmp_sha256,path_predictions`. Path predictions occur in
active-path order and have exact ordered fields
`path_id,path_sha256,raw_endpoint_count,actor_pre_cap_count,destination_pre_cap_count,actor_cap_hit,destination_cap_hit,endpoint_candidates,selected_actor_candidate_indices,selected_destination_candidate_indices`.
The VMP/path IDs and hashes equal the engine envelope and candidate paths.

Each endpoint candidate has exact ordered fields
`candidate_index,role,start,end,kind,lookup_surface,lookup_status,score_f64_bits`.
`candidate_index` is a non-Boolean integer contiguous from zero in model-emission
order. Each path has at most 512 candidates total and at most 256 for either
role. All existing endpoint role/kind/range/surface/status predicates and bounds
apply. `score_f64_bits` is exactly 16 lowercase hexadecimal characters encoding
a finite big-endian IEEE-754 binary64 score; negative zero is invalid and must
be canonicalized to positive zero. Selection decodes and compares this binary64
value, independent of host/model source dtype.

`raw_endpoint_count` equals the candidate-array length. Deduplicate by the exact
endpoint identity above; the highest binary64 score wins and an exact equal-score
tie keeps the lowest candidate index. Actor/destination pre-cap counts are the
post-dedup counts for those roles; each is a non-Boolean integer in `0..256`.
The corresponding cap-hit Boolean is true if and only if its pre-cap count is
greater than eight. Each selected-index array contains at most eight unique
indices, references only the retained deduplication winners, and is ordered by
the existing score-independent post-cap actor or destination packet key—not by
score. Every SEP packet endpoint must equal its referenced selected audit
endpoint exactly.

The audit uses recursively declared field order, compact UTF-8 JSON,
`ensure_ascii=false`, no whitespace, no terminal LF, no extra field, or nonfinite
number, and has at most 4 MiB. SHA-256 of exact bytes is
`prediction_audit_sha256`. This makes scores such as `1.00000004` and
`1.00000003` reproducibly distinct binary64 values even if an upstream
binary32 representation would have tied them.

For a candidate path, lookup-surface construction substitutes candidate text
only for candidate spans fully enclosed by the predicted `VMP` endpoint. If an
endpoint cuts through a candidate span, set `lookup_status=UNALIGNED`; every
affected pair short-circuits before registry access with `state=UNKNOWN`,
`registry_coverage=NOT_EVALUATED`,
`resolution_source=ALIGNMENT_GUARD`, `evidence_ids=[]`, and
zero resolver calls for that pair; it is not `MISMATCH` or `N/A`. A mixed packet
may still call the registry for other aligned pairs. `NOT_EVALUATED` is an
engine-only coverage value and never appears in a schema registry-reference
row. Gold endpoint and span losses remain in `VMP` coordinates.
Candidate-offset prediction followed by back-projection was rejected because
ambiguous alignment can silently change the evidence target.

Define the canonical pair packet as the complete Cartesian product

`E_k = {(a,d,Resolve_R(a,d)) : a in A_k, d in D_k}`.

Pairs are ordered by the score-independent post-cap actor key and then the
score-independent destination key above. Thus a path has at most 64 pairs. This is a
compatibility inventory, not a predicted or human-annotated actor-to-destination
link. If either endpoint set is empty, the product is empty: make no resolver
calls, emit no rows, and use only the implicit runtime state `N/A`.

For `s in {MATCH,MISMATCH,UNKNOWN,N/A}`, define equal-weight state prevalence

`pi_k(s) = |E_k|^-1 sum_{e in E_k} 1[state(e)=s]` when `E_k` is nonempty,

and `pi_k(s) = 1[s=N/A]` when `E_k` is empty. Then

`P_pair(s | x) = sum_k q_k pi_k(s)`.

`P_pair` is a diagnostic prevalence summary only. The complete canonical `E_k`
is an audit record; it never enters the learned risk head. Collapsing the audit
to one resolved pair was rejected, while exposing the full audit packet was
also rejected because literal surfaces and identifiers permit shortcut
features. Risk consumes only the deterministic `SemanticFeaturePlan` projection
defined below.

The canonical pair audit packet has exact top-level field order
`packet_version,vmp_sha256,path_sha256,registry_snapshot_id,resolver_version,no_explicit_pair,registry_call_count,pairs`.
The first five values are strings, `no_explicit_pair` is Boolean,
`registry_call_count` is a non-Boolean nonnegative integer, and `pairs` is an
array. Each pair has ordered fields `actor,destination,resolution`. Actor and
destination contain the six exact endpoint audit fields
`role,start,end,kind,lookup_surface,lookup_status`; resolution has ordered fields
`state,registry_coverage,resolution_source,evidence_ids`.

`packet_version="1.0.0"`; hashes are 64 lowercase hexadecimal characters;
state is `MATCH|MISMATCH|UNKNOWN`; coverage is
`COMPLETE|PARTIAL|MISSING|NOT_EVALUATED`; source is
`REGISTRY|ALIGNMENT_GUARD`. Every evidence ID fully matches
`registry_evidence_[a-z0-9][a-z0-9_-]{0,45}`, is unique, is sorted by UTF-8
bytes, and each pair has at most 16. `MATCH` and `MISMATCH` require
`COMPLETE+REGISTRY` and at least one evidence ID. A registry-derived `UNKNOWN`
requires `PARTIAL|MISSING+REGISTRY`. An alignment-derived `UNKNOWN` requires
`NOT_EVALUATED+ALIGNMENT_GUARD`, empty evidence IDs, and no registry call. No
other combination is valid. Schema coverage maps exactly
`complete -> COMPLETE`, `partial -> PARTIAL`, `missing -> MISSING`.

`registry_call_count` equals the number of `REGISTRY`-source pairs in that
packet. Empty product requires `pairs=[]`, `no_explicit_pair=true`, and count
zero; a nonempty product requires false. A run's total call count is the exact
sum of its path packet counts. Each packet has at most 64 pairs and at most 16
MiB canonical bytes; overflow rejects the run.

Encode packet objects recursively in declared field order as compact UTF-8 JSON
with `ensure_ascii=false`, no whitespace, nonfinite value, or extra field.
Every integer is a non-Boolean base-10 JSON integer with no leading zero or plus
sign.
SHA-256 of exact bytes is `pair_packet_sha256`. `path_sha256` binds the separate
canonical ordered `text,alignment` object under the same JSON rules.
`vmp_sha256`, registry snapshot, and resolver are frozen manifest bindings.
Endpoint scores exist only in the separate prediction audit.

The normative learned projection is `SemanticFeaturePlan`, with exact top-level
field order `feature_version,no_explicit_pair,pairs` and
`feature_version="1.0.0"`. Each pair has ordered fields
`actor,destination,resolution`; actor contains `start,end,lookup_status`;
destination contains `start,end,kind,lookup_status`; and resolution contains
`state,registry_coverage,resolution_source`. Pair order is the same
score-independent packet order. Canonical bytes follow the packet JSON rules
and their SHA-256 is `semantic_feature_plan_sha256`.

Plan coordinates are indexing instructions, never direct numeric risk features.
An explicit pair mask is required. Empty product yields zero real pair rows plus
the `no_explicit_pair` bit. No literal lookup surface, identifier, hash,
evidence ID, resolver/snapshot string, endpoint score, provider rank, candidate
weight, or score-derived order enters the per-path risk head. `q` is used only
after per-path risk computation for marginalization.

### 4.2 Exact E0 numeric feature audit

The only plan ID supported by `EngineRunEnvelope` schema `1.1.0` is the
synthetic-interface plan `E0_VMP_CATEGORY_MEAN_V1`. It does not claim
transformer or linguistic features. Its VMP hidden grid has dimension five and
one finite binary64 vector per VMP Unicode code point. Using the envelope's
pinned Unicode runtime, classify each code point in this precedence order:
`LETTER` when `unicodedata.category` begins `L`; `MARK` when it begins `M`;
`DECIMAL_DIGIT` when it is exactly `Nd`; `WHITESPACE` when none of the prior
rules holds and pinned `str.isspace` is true; otherwise `OTHER`. The basis order
is `LETTER,MARK,DECIMAL_DIGIT,WHITESPACE,OTHER`, with exactly one binary64
`1.0` and four positive binary64 zeroes.

For each endpoint and each of the five dimensions, start at binary64 `+0.0`, add
values sequentially in increasing VMP position with a binary64-rounded addition,
then divide in binary64 by binary64 `(end-start)`. A nonfinite result is invalid;
negative zero is canonicalized to positive zero. Each real pair row concatenates
in this exact order: actor mean `[5]`; destination mean `[5]`; destination-kind
one-hot `URL,DOMAIN,PHONE,UPI,BANK,EMAIL,APP,OTHER`; actor-lookup one-hot
`ALIGNED,UNALIGNED`; destination-lookup in the same order; state one-hot
`MATCH,MISMATCH,UNKNOWN`; coverage one-hot
`COMPLETE,PARTIAL,MISSING,NOT_EVALUATED`; and source one-hot
`REGISTRY,ALIGNMENT_GUARD`. The resulting pair dimension is 31.

The E0 feature-tensor audit schema version is `1.0.0` and its exact top-level
field order is
`schema_version,plan_id,vmp_sha256,path_sha256,semantic_feature_plan_sha256,pair_capacity,pair_dimension,no_explicit_pair,pair_mask,vmp_hidden_grid_f64_bits,pair_rows_f64_bits`.
`plan_id` is the E0 ID above; hashes bind the exact VMP, path, and structural
plan; `pair_capacity` and `pair_dimension` are non-Boolean integers fixed at 64
and 31. `pair_mask` is exactly 64 JSON Booleans: true for canonical real packet
rows first, then false. `no_explicit_pair` is true if and only if there are zero
real rows. Pair rows are exactly 64 rows, zero-padded with positive binary64
zero after the real rows.

The grid and pair-row fields are single row-major concatenations of 16-character
lowercase big-endian finite IEEE-754 binary64 bit strings; negative zero is
invalid. Their exact string lengths are `80*len(VMP.text)` and `16*64*31`
characters. No audit-only surface, ID, hash, evidence, score, rank, candidate
weight, or score order contributes a row value. Canonical serialization uses
recursively declared field order, compact UTF-8 JSON, `ensure_ascii=false`, no
whitespace, no terminal LF, no extra field or nonfinite number, and at most 2 MiB.
SHA-256 of exact bytes is `semantic_feature_tensor_sha256`.

The exact subword/candidate-hidden-to-VMP-grid adapter and its later plan/version
remain **UNKNOWN**, unimplemented, and must be frozen and tested before `E3`.
It cannot claim coverage from the E0 category-grid test. E0 tests only the exact
projection, mean arithmetic, masks, bytes, hashes, and exclusion canaries above.

There is no learned loss whose target is a registry state already supplied to
the risk path. That design was rejected as circular. Endpoint/span supervision
is retained. Semantic conditions consume only the feature plan and projected
tokens, never the audit packet itself.

| Information or module | `C00` | `C10` | `C01` | `C11` |
| --- | --- | --- | --- | --- |
| `VMP` | yes | yes | yes | yes |
| frozen provider/candidate list | same provider/list | same provider/list | same provider/list | same provider/list |
| active paths | returned rank one | all returned paths | returned rank one | all returned paths |
| provider execution | required | required | required | required |
| endpoint/span heads | no | no | rank 1 only | active per path |
| endpoint / audit packet / resolver | none | none | rank 1 only | every returned path |
| `SemanticFeaturePlan` / projected tokens | none | none | rank 1 only | every returned path |
| risk marginalization | none | `q` weighted | none | `q` weighted |
| pair-state diagnostic | none | none | rank-1 `pi` | `P_pair` |

This table describes the four `BASE` systems under `VALID`; the status union
governs degraded/invalid availability. `C00`/`C10` and capacity controls
construct no endpoints, packet, plan, or resolver call. Supervision controls may
train endpoint/span losses, but at inference may not construct, call, or expose
endpoint predictions, packet, plan, projected token, registry state, or
missingness. Feature, gradient, packet, plan, and call-count canaries verify
these exclusions.

Every metric run binds one canonical `registry_reference_bundle` audit manifest
with exact ordered fields
`schema_version,registry_snapshot_id,resolver_version,registry_manifest_sha256,registry_references_sha256`.
This bundle schema version is frozen as `"1.0.0"`; the snapshot ID and resolver
obey their registry contracts; both hashes are 64 lowercase hexadecimal
characters over the exact registry-manifest and registry-reference artifact
bytes. Canonical compact declared-order UTF-8 JSON under the no-extra-field
rules is hashed as `registry_reference_bundle_sha256`. A metric run fails if
its inference snapshot, resolver, registry-manifest hash, or reference-artifact
hash differs, including for zero-pair items.

### 4.3 Canonical evaluation universe and pair-metric run

The evaluation-universe schema version is `1.0.0` and its exact top-level order
is
`schema_version,universe_id,partition,dataset_artifact_hashes,registry_reference_bundle_sha256,entries`.
`universe_id` matches
`evaluation_universe_[a-z0-9][a-z0-9_-]{0,55}`. `partition` is exactly one of
the named Fisher evaluation partitions `development|primary_test|external_test`.
The dataset-hash object has exact ordered fields
`items_jsonl_sha256,annotations_jsonl_sha256,registry_manifest_jsonl_sha256,registry_references_jsonl_sha256`,
each a 64-character lowercase SHA-256 of the exact artifact bytes. The registry-
reference-bundle hash must bind the same registry artifacts.

There are at most 10,000 `entries`, unique and sorted by `item_id` UTF-8 bytes.
Each has exact ordered fields
`item_id,partition,vmp_sha256,final_annotation_id,gold_inventory_size_bytes,gold_inventory_sha256,gold_pair_count,gold_empty`.
IDs/hashes obey their data-contract grammars. `gold_pair_count` is a non-Boolean
nonnegative integer, `gold_inventory_size_bytes` is a non-Boolean integer in
`1..2097152`, `gold_empty` is true if and only if pair count is zero, and every
entry partition exactly equals the universe partition.

`gold_inventory_sha256` hashes a separate canonical object with exact top-level
field order
`inventory_version,item_id,vmp_sha256,final_annotation_id,actors,destinations,registry_references`,
where version is `"1.0.0"` and the identity/hash values exactly equal the entry.
Actor objects have exact
ordered fields `span_index,start,end,text`; destination objects have exact
ordered fields `span_index,start,end,text,kind`; registry-reference objects have
exact ordered fields
`registry_reference_id,actor_span_index,destination_span_index,label,registry_coverage,registry_evidence_ids,registry_snapshot_id,resolver_version`.
Endpoint objects reproduce the final annotation's explicit endpoint indices,
ranges, exact VMP slices, and destination kind; they are sorted by ascending
non-Boolean span index. Reference objects reproduce every Cartesian reference
and are sorted by actor index, destination index, then reference-ID UTF-8 bytes.
Their label/coverage/evidence/snapshot/resolver values obey the data and registry
contracts. `gold_pair_count` equals the reference-array length, and the arrays
must be complete and mutually coherent.

Gold inventory bytes use recursively declared field order, compact UTF-8 JSON,
`ensure_ascii=false`, no whitespace, no terminal LF, no extra field, and no
nonfinite value. They are at most 2 MiB; their exact byte length equals
`gold_inventory_size_bytes` and their SHA-256 equals the entry hash.

Universe construction is closure, not sampling. From the four exact dataset
artifacts, derive the complete UTF-8 item-ID-sorted set of every item whose
partition equals the named universe partition and which is retained, has exactly
one valid final annotation with binary label and one known study stratum, has a
valid matching VMP hash, and has a complete final actor/destination inventory
plus the exact complete Cartesian registry-reference inventory bound to the
named reference bundle. `entries` must equal this derived set byte-for-byte.
Omission, extra entry, duplicate, reorder, partition mismatch, or more than
10,000 derived items invalidates the universe. The derived set must contain
between one and 10,000 entries; a zero-entry closure is semantically invalid.
No post-inference selection or deletion is permitted.

The universe manifest is frozen before inference. It uses recursively declared
field order, compact UTF-8 JSON, `ensure_ascii=false`, no whitespace, no terminal
LF, no extra field or nonfinite number, and at most 32 MiB. SHA-256 of exact
bytes is `evaluation_universe_sha256`.

Raw evaluation-universe parsing and semantic closure validation are separate.
Every submitted universe first produces a `MetricUniverseInputReceipt` schema
`1.0.0` with exact top-level order
`schema_version,receipt_id,evaluation_universe_sha256,submitted_prefix_sha256,prefix_bytes_hashed,observed_bytes,decoded_entry_count,validated_entry_count,invalid_codes,status`.
`receipt_id` matches
`metric_universe_input_[a-z0-9][a-z0-9_-]{0,50}`. Its reader consumes at most
33,554,433 raw bytes: the 32-MiB cap plus one, and never reads another byte.
When the cap is exceeded, `evaluation_universe_sha256=null`, the prefix hash
covers exactly the first 33,554,433 bytes,
`prefix_bytes_hashed=33554433`, and
`observed_bytes="GE_33554433"`. For a bounded input,
`submitted_prefix_sha256=null`, `prefix_bytes_hashed=0`, and `observed_bytes`
is the exact non-Boolean byte length in `0..33554432`.
`evaluation_universe_sha256` is the SHA-256 of the complete supplied bytes if
and only if those bounded bytes pass the canonical-byte check; it is null for
every earlier failure. It is therefore available for a later schema or entry-
bound failure without claiming semantic validity.

The reader uses the same deterministic strict JSON scanner and parser semantics
as `EngineInputDescriptor`, not a library's default duplicate/nonfinite
behavior. Its exact one-code precedence is:

1. `metric_universe_too_large`;
2. `metric_universe_bom`;
3. `metric_universe_invalid_utf8`;
4. `metric_universe_duplicate_key`;
5. `metric_universe_nonfinite`;
6. `metric_universe_invalid_json_syntax`;
7. `metric_universe_non_nfc`;
8. `metric_universe_noncanonical_bytes`;
9. `metric_universe_schema_or_enum`; and
10. `metric_universe_too_many_entries`.

After strict UTF-8 decoding, lexical scanning is left-to-right and stops at the
first unrecoverable JSON syntax event. Among duplicate-key or nonfinite events
fully observed before that stop, duplicate key outranks nonfinite and both
outrank syntax according to the list above, irrespective of byte offset; no
recovery occurs after the syntax event. Only a successful full parse proceeds
to all-string NFC checking and then exact canonical reserialization/byte
equality. Only canonical bytes proceed to exact top-level, field, type, grammar,
enum, and entry-object validation; the entry limit is checked last. Thus an
invalid entry object plus an oversized array is
`metric_universe_schema_or_enum`, while an otherwise structurally valid array
of more than 10,000 entries is `metric_universe_too_many_entries`.

`decoded_entry_count` is a non-Boolean integer in `0..10001`. It is zero for
codes 1--8, for a non-object top level, for a missing or non-array `entries`,
or for any failure before a complete parsed top-level object with an `entries`
array exists. Once that whole canonical object and array exist, it is exactly
`min(len(entries),10001)`, including schema-invalid entry objects and non-object
array elements. There is no
prefix or partial-entry count. `validated_entry_count` is a non-Boolean integer
in `0..10000`; it equals `len(entries)` only when every entry individually
passes the exact structural field/type/grammar checks and `len(entries)<=10000`,
and is zero otherwise.

The receipt state table is exact:

| First applicable result | Universe hash / prefix hash | Decoded / validated entries | Status and continuation |
| --- | --- | --- | --- |
| `metric_universe_too_large` | null / SHA-256 of exactly the first 33,554,433 bytes | `0 / 0` | `FAIL`; no metric run |
| any of codes 2--8 | null / null | `0 / 0` | `FAIL`; no metric run |
| `metric_universe_schema_or_enum` before a complete top-level object plus `entries` array | SHA-256 of complete canonical supplied bytes / null | `0 / 0` | `FAIL`; no metric run |
| `metric_universe_schema_or_enum` with that complete array | SHA-256 of complete canonical supplied bytes / null | `min(len(entries),10001) / len(entries)` only when every entry is structurally valid and `len(entries)<=10000`, otherwise the validated count is `0` | `FAIL`; no metric run |
| `metric_universe_too_many_entries` | SHA-256 of complete canonical supplied bytes / null | `10001 / 0` | `FAIL`; no metric run |
| structural success, including `entries=[]` | SHA-256 of complete canonical supplied bytes / null | `len(entries) / len(entries)` | `PASS`; continue to submission preflight |

Every bounded row in this table has `prefix_bytes_hashed=0` and exact
`observed_bytes`; the too-large row alone has
`prefix_bytes_hashed=33554433` and `observed_bytes="GE_33554433"`.

The receipt is an exact union. `PASS` has a nonnull computed universe hash,
`invalid_codes=[]`, and means only that the complete universe is bounded,
canonical, and structurally schema-valid; zero entries may pass this structural
boundary. `FAIL` has `invalid_codes` equal to the one-element array containing
the first applicable code above. A failure before canonical-byte equality has
a null universe hash; a schema/enum or too-many-entries failure retains the
computed canonical-byte hash. `FAIL` emits no `MetricRunManifest` or metric
value. The receipt uses declared-order compact UTF-8 JSON,
`ensure_ascii=false`, NFC strings, no BOM, CR, whitespace, terminal LF, extra
field, or nonfinite number, is at most 64 KiB, and hashes as
`metric_universe_input_receipt_sha256`. It contains no raw bytes, item ID, text,
surface, or malformed identifier.

Metric-input preflight is separate from `MetricRunManifest`. After a universe
receipt passes, parse a submitted-inference descriptor against that receipt's
computed evaluation-universe hash
and consume at most 33,554,433 raw bytes: the 32-MiB cap plus one. A malformed,
oversized, non-UTF-8, noncanonical, or over-row-bound descriptor emits only a
`MetricInputReceipt` schema `1.0.0`; no metric-run manifest or metric value
exists.

The receipt's exact top-level order is
`schema_version,receipt_id,evaluation_universe_sha256,submitted_prefix_sha256,prefix_bytes_hashed,observed_bytes,decoded_row_count,validated_row_count,failure_stage,invalid_codes,status`.
`receipt_id` matches `metric_input_[a-z0-9][a-z0-9_-]{0,59}`. The prefix hash
covers exactly the consumed bytes and `prefix_bytes_hashed` is their non-Boolean
length in `0..33554433`. `observed_bytes` is the exact complete length in
`0..33554432` when EOF was observed or `GE_33554433` otherwise. Row counts are
non-Boolean integers in `0..20000` or sentinel `GE_20001`; a decoded row is one
complete entry object, while a validated row additionally passes exact
`item_id,envelope_sha256` grammar. The offending row never counts as validated.

`failure_stage` is `BYTES|UTF8|JSON|CANONICAL|ROW_BOUND|BINDING`, selecting the earliest
failure in that order. `invalid_codes` is a sorted unique nonempty array from
`metric_input_oversized|metric_input_invalid_utf8|metric_input_invalid_json|metric_input_invalid_shape|metric_input_noncanonical|metric_input_too_many_rows|metric_input_universe_hash_mismatch`,
containing codes from that stage only. The code-to-stage map is respectively
`metric_input_oversized` to `BYTES`, `metric_input_invalid_utf8` to `UTF8`,
`metric_input_invalid_json|metric_input_invalid_shape` to `JSON`,
`metric_input_noncanonical` to `CANONICAL`, and
`metric_input_too_many_rows` to `ROW_BOUND`, and
`metric_input_universe_hash_mismatch` to `BINDING`; `status=FAILED`. The
binding code applies when the structurally valid submission's declared
evaluation-universe hash differs from the hash computed from the supplied
canonical universe bytes. The receipt contains no
raw bytes, item ID, envelope ID, text, surface, or canonical full-descriptor
hash. It uses declared-order compact UTF-8 JSON, `ensure_ascii=false`, no
whitespace or terminal LF, no extra/nonfinite field, and at most 64 KiB; its
exact-byte hash is `metric_input_receipt_sha256`.

Only a structurally valid bounded submission becomes the canonical
submitted-inference manifest schema `1.0.0` with exact top-level order
`schema_version,evaluation_universe_sha256,system_artifact_manifest_sha256,entries`.
Each entry has exact ordered fields `item_id,envelope_sha256`; the array retains
submitted order and may contain duplicates so failure evidence is not rewritten.
It has at most 20,000 entries and 32 MiB under the universe's canonical JSON
rules. Its exact-byte hash is `submitted_inference_manifest_sha256`.

The metric boundary order is exact: first the universe structural receipt;
second, only after its `PASS`, the submitted-inference structural receipt and
hash binding; third, only after both structural boundaries pass, semantic
universe closure, partition, complete-entry, gold-inventory, and reference-
bundle validation. A universe structural `FAIL` wins and emits no metric run. If
the universe receipt passes but submission preflight fails, that submission
receipt wins and emits no metric run, even when the universe would later fail
semantic closure. The engine does not inspect semantic universe validity before
the submission boundary completes.

The pair-metric-run schema version is `1.1.0` with exact top-level order
`schema_version,metric_run_id,condition,system_id,system_variant,system_artifact_manifest_sha256,evaluation_universe_sha256,registry_reference_bundle_sha256,submitted_inference_manifest_sha256,inference_envelopes,N_all,N_gold_empty,N_gold_nonempty,universe_error_count,denominator_error_count,submitted_count,missing_count,extra_count,duplicate_count,reordered_count,degraded_count,invalid_count,mismatch_count,status,invalid_codes`.
`metric_run_id` matches `metric_run_[a-z0-9][a-z0-9_-]{0,62}`. Pair metrics are
valid only for `BASE/C01` or `BASE/C11`; every control and `C00|C10` reports
`N/A`. System identity and artifact hash equal every submitted envelope.
`N_all`, `N_gold_empty`, and `N_gold_nonempty` are non-Boolean integers in
`0..10000`. When `universe_error_count=0`, a semantically valid bound universe
has `1<=N_all<=10000`; the three expected values are derived from it, the first
equals its entry count, and the latter two sum to it. When
`universe_error_count=1`, all three are canonical zero and
`denominator_error_count=0`; no metric is computed.

`universe_error_count` is a non-Boolean integer in `{0,1}`. It is one only in
the semantic-universe short-circuit defined below. Once a semantically valid
bound universe exists, it is zero throughout the ordinary row algorithm. A
submission-declared universe hash that differs from the hash computed from the
supplied canonical bytes is instead
`metric_input_universe_hash_mismatch` at submission preflight and produces no
metric run; it is not a second universe-error route.
`denominator_error_count` is a non-Boolean integer in `0..3`: when
`universe_error_count=0`, it counts how many of the three declared fields
`N_all,N_gold_empty,N_gold_nonempty` differ from the values derived from that
valid bound universe; when `universe_error_count=1`, it is zero because no valid
bound universe exists from which to derive a comparison. These top-level counts
are disjoint from per-row envelope outcomes.

Each remaining diagnostic count is either a non-Boolean integer in `0..20000`
or the exact saturation sentinel `GE_20001`; no unsafe row, item text, surface,
or raw ID is embedded. Metric status is `VALID|INVALID`. `invalid_codes` is a sorted unique
array from the closed set
`metric_invalid_universe|metric_missing|metric_extra|metric_duplicate|metric_reordered|metric_degraded|metric_invalid_envelope|metric_binding_mismatch|metric_invalid_denominator`.

If both structural boundaries pass but the universe is not exactly the complete
nonempty semantic closure specified above, emit the sole semantic-universe
short-circuit `MetricRunManifest INVALID`: retain its computed supplied
`evaluation_universe_sha256` and the canonical
`submitted_inference_manifest_sha256`; set `universe_error_count=1`,
`N_all=N_gold_empty=N_gold_nonempty=0`, `denominator_error_count=0`, and
`submitted_count=|S|`; set
`missing_count=extra_count=duplicate_count=reordered_count=degraded_count=invalid_count=mismatch_count=0`;
set `inference_envelopes=[]`, `status=INVALID`, and
`invalid_codes=["metric_invalid_universe"]`; and emit no metric values. No
submitted envelope is opened. The engine never treats invalid universe entries
as `E`, repairs closure, compares submission rows, or deletes an item. A
canonical universe with `entries=[]` is the required known-answer case: its
structural receipt is `PASS`, submission preflight still runs, and after that
passes this exact semantic-invalid short-circuit applies.

Only when the universe is semantically valid, let `E` be its unique item IDs in
their frozen order and `S` the submitted rows in left-to-right order. Classify
each row exactly once by this precedence: if its `item_id` occurred earlier in
`S`, classify it `DUPLICATE`; otherwise record the ID as seen and classify it
`EXTRA` when it is not in `E`, or `UNIQUE_EXPECTED` otherwise. Thus
`duplicate_count` counts every `DUPLICATE` occurrence, `extra_count` counts the
first occurrence of each out-of-universe ID, and `U` is the `UNIQUE_EXPECTED`
rows in submitted order. Duplicate and extra rows are never opened or inspected
for envelope status or bindings. `submitted_count=|S|`.

Set `missing_count=|E|-|IDs(U)|`. Restrict `E` to the IDs present in `U`, retain
its universe order, and set `reordered_count` to the number of positional
mismatches between that restricted list and `U`; the lists have the same
length. For each row in `U`, classify one exclusive envelope outcome: missing,
unreadable, noncanonical, or `execution_status=INVALID` contributes one to
`invalid_count`; else `DEGRADED_STOP_AFTER_IDENTITY` contributes one to
`degraded_count`; else any required item/VMP/system/universe/registry/resolver/
envelope binding mismatch contributes one to `mismatch_count`; otherwise it is
a matched valid row. Counts are occurrence counts under the cap/sentinel rule.

The metric status union is exact:

- `VALID`: `inference_envelopes` has exact ordered `item_id,envelope_sha256`
  objects and equals the complete universe one-for-one and in the same order;
  it also equals the submitted manifest entries. Submitted count equals `N_all`;
  both top-level error counts and every discrepancy count are zero; every envelope is `VALID`, has the
  expected VMP/system/condition/variant/path/registry/artifact bindings,
  `1<=N_all<=10000`, and
  supplies all required finite objects; and `invalid_codes=[]`.
- `INVALID`: `inference_envelopes=[]`; the submitted-manifest hash remains
  present; bounded diagnostic counts summarize universe, denominator,
  submitted, missing, extra,
  duplicate, reordered, degraded, invalid, and binding-mismatch observations;
  at least one count across
  `universe_error_count,denominator_error_count,missing_count,extra_count,duplicate_count,reordered_count,degraded_count,invalid_count,mismatch_count`
  is nonzero, `invalid_codes`
  identifies those failed classes, and no pair
  metric is emitted. An invalid row is never forced to satisfy valid-list
  equality and no item is deleted.

`metric_invalid_universe` is present if and only if
the semantic-universe short-circuit sets `universe_error_count=1`;
`metric_invalid_denominator` is present if and only if
`denominator_error_count>0`. Any nonzero missing, extra, duplicate, reordered,
degraded, invalid, or mismatch count requires `status=INVALID` and its
corresponding controlled invalid code; zero counts prohibit those codes. For
the fixed example `E=[a,b]` and
`S=[b,a,a,c,c]`, the exact counts are `duplicate_count=2` (second `a`, second
`c`), `extra_count=1` (first `c`), `missing_count=0`, and
`reordered_count=2`, with `universe_error_count=0` and
`denominator_error_count=0` when the universe and all three declarations bind;
only the unique expected rows `b,a` may contribute to the
three exclusive envelope-outcome counts.

Any missing, extra, duplicate, reordered, degraded, or invalid envelope; VMP,
gold, universe, system, reference-bundle, registry artifact, snapshot, resolver,
candidate, path, prediction, packet, plan, tensor, or nonfinite mismatch; or
declared-denominator mutation makes the entire run `INVALID`. The manifest uses the
universe's canonical JSON rules, is at most 32 MiB, and hashes as
`metric_run_manifest_sha256`.

Only a `VALID` pair-metric manifest may enter the following calculations; its
`N_all` is therefore positive.
Report its fixed `N_all`, `N_gold_empty`, and `N_gold_nonempty`.

For falsification, compare exact tuples `(actor VMP start,end,destination VMP
start,end,state)`. Let `w_ik=1` for the sole active `C01` rank-one path and
`w_ik=q_ik` for `C11`. Across all `N_all`, accumulate micro
`TP=sum_i,k w_ik |E_ik intersect G_i|`,
`FP=sum_i,k w_ik |E_ik minus G_i|`, and
`FN=sum_i,k w_ik |G_i minus E_ik|`. Define
`precision_pair=TP/(TP+FP)`, `recall_pair=TP/(TP+FN)`, and
`F1_pair=2TP/(2TP+FP+FN)`. Each value is canonical binary64 `+0.0` whenever its
own denominator is zero; therefore `TP=FP=FN=0` yields
`precision_pair=recall_pair=F1_pair=+0.0`. This rule is identical for q-weighted
and rank-1 forms and never triggers `metric_invalid_denominator`, which is
reserved only for a declared `N_all|N_gold_empty|N_gold_nonempty` mismatch. A nonempty prediction on gold-empty contributes FP;
both-empty contributes zero counts but remains in `N_all`.

Report `pair_emptiness_accuracy=(1/N_all) sum_i,k w_ik
1[empty(E_ik)=empty(G_i)]`, gold-empty recall
`sum_{i:G_i empty,k}w_ik 1[E_ik empty]/N_gold_empty`, and gold-nonempty recall
`sum_{i:G_i nonempty,k}w_ik 1[E_ik nonempty]/N_gold_nonempty`, with conditional
metrics only when their fixed named denominator is nonzero. `C11` reports both
q-weighted and rank-1 forms; `C01` reports rank 1; `C00`/`C10` report `N/A`.
The pair-emptiness denominator is always positive on a `VALID` run because a
semantically valid evaluation universe has at least one entry.
These include endpoint and resolver failures but are not blind relation IAA.
Blind reliability remains endpoint/span reliability and no learned
registry-state loss is permitted.

## 5. Five-seed calibrated path ensemble

For system `m`, seed `j in {11,23,37,53,71}`, and active path `k`, let
`ell_mjk` be the path risk logit. The canonical five-seed artifact in Section
3.3 fixes source order, finite bits, and arithmetic. Average before calibration:

`bar_ell_mk = binary64((binary64 sequential sum in seed order)/5.0)`.

Fit one positive scalar `T_m` per fixed system, pooled across languages, using
only `probability_calibration` and minimizing binary NLL of the marginalized
`p_m` defined below. Let `w_mk=1` for the sole active rank-one path in
`C00|C01`, and `w_mk=q_k` for every active path in `C10|C11`. Define:

`rho_mk = sigmoid(bar_ell_mk / T_m)`,

`p_m(x) = sum_{k active} w_mk rho_mk`,

`v_m(x) = 4 sum_{k active} w_mk (rho_mk - p_m(x))^2`, and

`u_m(x) = 0.5 H(p_m(x)) / log(2) + 0.5 v_m(x)`,

where `H(p) = -p log(p) - (1-p)log(1-p)` is binary entropy and
`0 log(0) = 0` by continuity.

For the rank-one `C00` and `C01` systems, `v_m = 0`. The alert score, entropy, safety threshold,
selective cutoff, and path-disagreement term all use this same calibrated
object. A common logit delta was rejected as nonidentified. Combining calibrated
entropy with raw-logit disagreement was rejected as scale-incoherent.
Entropy-only remains an ablation.

**UNKNOWN / pre-`E4` requirement:** freeze and independently test the exact
scalar-temperature optimizer, positive bounds, convergence tolerance, tie
behavior, dtype, and invalid/nonfinite failure behavior. Until that contract is
evidenced, system calibration is not executable evidence.

## 6. Threshold and FPR claim boundary

Each system owns its temperature and its benign-only `safety_threshold`
threshold. H1 and H2 compare recall at those independently locked operating
policies. They do not estimate common-FPR dominance and cannot support a safety
superiority claim.

For a stratum with `n` independent benign records and zero false positives, the
one-sided exact 95% Clopper-Pearson upper bound is:

`U_95(n, 0) = 1 - 0.05^(1/n)`.

**DERIVED arithmetic:** `n = 300` gives `0.9936%`, so the `C11` absolute gate may
use an individual stratum-specific “below 1%” statement only when that stratum
has exactly `0/300` observed false positives. For a simultaneous four-stratum
Bonferroni statement, use `1 - (0.05/4)^(1/n)`: `n = 300` gives `1.4501%`, and
at least `437` independent zero-error benign records per stratum are required
for a simultaneous below-1% bound. Likewise, `598` zero-error records support an
individual below-0.5% bound and `875` per stratum support the simultaneous
four-stratum below-0.5% bound. These are sample-size calculations, not Fisher
results.

No arbitrary underpowered FPR noninferiority test is permitted. If comparative
FPR becomes essential, design a new untouched benign evaluation set, justify a
clinically or operationally meaningful margin externally, and freeze a paired
power design before any access.

## 7. Failure contracts and verification

- Empty enabled candidate sets, padding, nonfinite values, signed-zero drift,
  invalid/incomplete alignment, overlapping rewrite spans, a rewrite overlapping
  a visible artifact, altered non-span bytes, duplicate `(normalized text,
  alignment)` outputs after final merge, more than 64 spans, more than eight
  returned paths, a length/byte/manifest overflow, invalid provider ID/mode/unit/
  rank/logit bits, empty composed/direct or nonempty bypass `rewrite_spans`,
  direct-mode nonrewrite/artifact mutation, mixed provider configurations, or
  noncanonical lineage invalidates candidate construction. All four factorial
  cells bind the same frozen provider/configuration; `C00`/`C01` activate rank
  one and `C10`/`C11` all returned paths. The two bypass reasons use the
  canonical `IDENTITY_BYPASS` output manifest and are the only valid identity-
  output cases.
- A malformed configured selector or Boolean/out-of-range configured span is
  `ELIGIBILITY_INVALID` at `PROVIDER_EXECUTION` with no retained unsafe span. A
  Boolean/out-of-range effective span after provider acceptance, an execution-
  manifest inconsistency, a bypass whose effective spans are nonempty, or any
  malformed/nonfinite/alignment-breaking provider or normalizer output makes the
  run `INVALID`. Only a pre-acceptance unavailable/timeout failure with a fully
  validated identity fallback is `DEGRADED_STOP_AFTER_IDENTITY`; it stops before
  prediction and invalidates protected/confirmatory metrics.
- For an aligned explicit predicted pair, registry absence, conflict,
  incompleteness, or staleness returns `UNKNOWN`, never inferred `MISMATCH`. An
  unaligned pair takes the frozen pre-registry `ALIGNMENT_GUARD` short-circuit.
  An empty Cartesian product makes no calls and has runtime state `N/A`; it
  produces zero registry-reference rows and `N/A` is never a reference-row
  label.
- A network lookup, protected-derived registry entry, gold-endpoint resolver
  input during inference, or registry access in `C00`/`C10` invalidates the run.
- Descriptor/source-closure/system-artifact/environment/VMP failure emits only
  the one-code `EnginePreflightReceipt` `FAIL`, never an envelope; `PASS` binds
  the exact descriptor and validated references. After those preconditions pass,
  an envelope/logit/audit/tensor byte, hash, field-order, enum, status-union,
  count, condition/variant, path-order, artifact-mask, or active-path
  inconsistency; packet/plan overflow; evidence-ID/call-count violation;
  reference-bundle mismatch; a nonfinite grid/token/path value; calibration
  failure; or missing required path makes the envelope `INVALID` at the earliest
  primary stage under the retention table.
  It is never silently dropped or removed from metric `N_all`.
- After engine preflight, the canonical engine envelope is the sole run-level binding for source,
  system identity/variant/artifact/source closure, runtime/math backend, VMP,
  provider cause/configuration/spans, candidate numeric diagnostics, path
  lineage/scores/numerators/weights, active paths, five-seed artifact, prediction
  audit, SEP/feature hashes, direct registry artifact/resolver binding, status,
  and invalid codes. `EnginePreflightReceipt` records the exclusive engine
  descriptor preflight result; `MetricUniverseInputReceipt` records the exact
  structural result for every raw universe input; `MetricInputReceipt` records
  an invalid raw inference submission; `MetricRunManifest` exists only after
  both metric structural boundaries pass, and its universe-error short-circuit
  precedes row comparison. No separate informal run manifest or candidate-trace
  hash is accepted.
- `E0` must provide known-answer tests for float64 `logsumexp`, overflow-safe
  exact/beam selection, provider output/execution manifests, both bypass causes,
  complete executed-source closure, exact engine input descriptor/parser and
  PASS/FAIL preflight receipt, eligibility-invalid outcome/counts, system artifact/
  run-envelope canonical bytes and hashes, all eight masks, all three run-status
  variants, exact failure precedence/count units/stage retention, compact lineage without
  cross-product expansion, merge keys, coordinate/alignment predicates, signed
  zero, byte ties, staged merge reductions, binary64 q numerators/normalizer/
  maximum and retained mass, prediction-audit emission/
  dedup/cap/order, lookup cut-through, packet bytes/size/call counts/evidence
  rules, exact category-grid means and fixed feature tensor, complete gold bytes,
  closure-derived nonempty universe, strict universe-parser code precedence and
  receipt counts/hash states, empty-universe semantic-invalid known answer,
  universe/submission/semantic precedence, submitted-inference/metric status
  union, expanded universe/denominator counts, fixed duplicate/extra/
  order/outcome example, zero-denominator pair algebra, complete-universe pair
  metrics, `P_pair`, five-seed artifact/averaging, calibration
  ownership, `v`, rank-one `v=0`, and information masks.
  These are interface tests, not model evidence.

The preregistered primary system fixes the per-role endpoint cap at eight. A
bounded development-only mechanism sensitivity runs caps `{2,4,8}` after the
primary configuration is frozen; it is not model selection and cannot change
the protected cap.

The authoritative related contracts are the
[preregistration](PAPER_1_PREREGISTRATION.md),
[factorial specification](FACTORIAL_CONDITION_SPEC.md),
[transliteration protocol](TRANSLITERATION_RESOURCE_PROTOCOL.md), and
[registry protocol](REGISTRY_PROTOCOL.md).
