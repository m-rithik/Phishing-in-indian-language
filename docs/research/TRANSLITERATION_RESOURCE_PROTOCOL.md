# Fisher Transliteration Resource Protocol

> Status: internal, embargoed, pre-data protocol. This governs auxiliary paired transliteration resources and candidate posteriors; it does not authorize acquisition or redistribution of any resource.

## 1. Purpose and boundary

Fisher may use paired Romanized/native-script resources to generate and calibrate candidate interpretations. Those pairs are auxiliary linguistic evidence, not phishing examples. They cannot supply phishing labels, tune a Fisher protected partition, or be treated as a Fisher benchmark result.

**OBSERVED:** no paired resource has been ingested or audited in the repository.
`E11` independently passed the preceding provider-manifest/lineage/bounds repair
but failed the later provider-execution/run-envelope, endpoint-numeric,
E0-feature, evaluation-universe, and coordinate-predicate contract. **UNKNOWN:**
final resources, licenses, coverage, schema, quality, redistribution rights, and
whether the eighth local, universe-only repair after `E15`'s three strict
universe-input parser/count, structural-versus-semantic precedence, and
nonempty-denominator blocker groups will pass independent replay. `E15` passed
the E14 repair and all previously reviewed surfaces. The E13 repair and shared-provider factor, control masks,
evaluation/gold binding, provenance/five-seed, and candidate-numeric surfaces
passed that fifth replay. Every resource
remains blocked until the ledger, file audit, and P0 replay below pass.

## 2. Governed resource manifest

For every acquired resource version, preserve an immutable manifest containing:

| Field | Requirement |
| --- | --- |
| `resource_id` | stable project identifier |
| `title`, `creators`, `version` | exact source metadata |
| `source_uri` and DOI, if any | authoritative landing identifier |
| `acquired_at` | timestamp and lawful acquisition route |
| `license_expression` | observed license identifier or `UNKNOWN` |
| `license_text_sha256` | hash of the exact retained license/terms text |
| `platform_terms_sha256` | hash when platform terms separately constrain access |
| `raw_file_sha256` | hash of each immutable source file |
| `allowed_uses` | reviewed internal training/evaluation/redistribution states |
| `languages`, `scripts`, `romanization_scope` | observed coverage after audit |
| `transformations` | ordered derivation code/configuration and hashes |
| `reviewer`, `reviewed_at`, `decision` | `APPROVED_INTERNAL`, `APPROVED_RELEASE`, `CONDITIONAL`, or `EXCLUDED` |

Public accessibility is not a license. A machine-readable entry cannot replace human review of license text, platform obligations, privacy, or redistribution.

## 3. Separate transliteration partitions

Auxiliary resources use their own grouped partitions:

- `transliteration_development`: candidate-generator fitting and selection;
- `transliteration_temperature_calibration`: group-disjoint, message-level
  fitting of `T_tr` only; and
- `transliteration_evaluation`: frozen candidate coverage and candidate-NLL measurement.

Group exact/near duplicate Roman forms, native forms, lexical families,
inflectional variants, source rows, speakers/authors when available, message
templates, and generated descendants before partitioning. No group crosses
these partitions. Fisher's `probability_calibration`, `safety_threshold`, or
`primary_test` partition cannot fit, select, rerank, calibrate, or repair a
transliteration candidate model.

Word-pair resources may train a provider or measure isolated lexical coverage,
but they cannot establish calibration for the multi-span message distribution.
Every `T_tr` fitting record must be a message-level example with adjudicated
acceptable full-message interpretations and the same bounded composition path
used by Fisher inference.

## 4. Exact resource and candidate records

Each lexical paired-resource row used to train or screen a provider serializes:

| Field | Type and rule |
| --- | --- |
| `pair_id` | unique nonempty string |
| `resource_id`, `resource_version` | keys into the governed manifest |
| `source_row_key` | privacy-safe immutable source-row reference |
| `language` | frozen language code |
| `roman_text` | immutable observed Romanized string |
| `native_reference_forms` | nonempty list of observed reference strings |
| `acceptable_normalized_forms` | nonempty adjudicated set used only for acceptable-candidate membership |
| `normalization_version` | exact normalization configuration hash/version |
| `group_id` | dependency component identifier |
| `partition` | one of the three transliteration partitions |
| `candidates` | optional provider-diagnostic list of at most eight candidate objects |
| `generator_version` | code/model/configuration hash |
| `license_record_id` | governed manifest decision key |
| `provenance_lineage` | ordered source and transformation parent identifiers |

Every raw lexical or span-candidate object contains `provider_rank`,
`candidate_text`,
`candidate_script`, finite `raw_logit`, `is_acceptable`, `generation_status`,
and its source alignment. In a message-run provider manifest, `provider_rank` is
a non-Boolean integer in `1..8`, unique within its unit; raw identity is
`(unit_index,provider_rank)` and ranks may reset across units. Scores serialize
only as finite, positive-zero-canonicalized, 16-character lowercase big-endian
binary64 hex. Each unit has at most eight readings.
Duplicate identity is `(normalized text, alignment)`, not text alone, and exact
duplicates are merged by exact mode-specific canonical-lineage binary64
`logsumexp` before assigning
separate `returned_rank`; remaining returned ranks are unique and contiguous
from 1. Ties use normalized UTF-8 text bytes, encoded-alignment bytes, and
contributor identity after the score.

`is_acceptable` is true only when the frozen normalizer maps the candidate into
`acceptable_normalized_forms`. Human adjudication, not a Fisher phishing label,
defines the acceptable set. Lexical rows do not fit or validate `T_tr`.

Every message-level selection/calibration/evaluation record additionally binds
the schema-`1.2.0` VMP, exactly `item.text` plus non-gold pre-annotation
`item.visible_artifacts`, through required `item.vmp_sha256`; annotations never
construct this packet. Its artifact grammar and exact Unicode-code-point
destination-span binding follow the
[data contract](../DATA_CONTRACT.md#visible-non-gold-artifact-inventory-and-vmp)
and prove syntactic representation safety only, not authenticity. It also
binds:

- for every factorial cell, the same frozen provider/configuration with exactly one configured mode
  `COMPOSED_SPAN|DIRECT_FULL_PATH`; `IDENTITY_BYPASS` is a candidate-output
  artifact, not a configured provider; direct and composed are separate
  configurations/runs and never pool candidates or logits in one `q`; `C00`/
  `C01` activate returned rank 1 and `C10`/`C11` activate all returned paths;
- the exact provider manifest fields/IDs/modes/units/readings/f64 bits and
  `provider_reading_manifest_sha256` frozen in the engine specification;
- the exact enclosing `provider_execution` object, which distinguishes success,
  no eligible span, and attempted provider failure and binds configuration,
  normalizer, eligible/attempted spans, invocation, bypass/failure state, and
  the candidate-output manifest hash;

- unique `message_pair_id`, resource/version, group, language, partition,
  immutable source text hash, and normalization/configuration hashes;
- a sorted nonoverlapping list of at most 64 Romanized spans with exact
  code-point offsets and at most eight candidate objects per span; every
  `span_index`, `start`, and `end` is a non-Boolean integer, indices are
  contiguous from zero, `0 <= start < end <= len(VMP.text)`, source text is the
  exact VMP slice, and spans cannot overlap visible artifacts;
- for every provider and normalized returned path, an ordered alignment JSON
  array of `[vmp_start,vmp_end]` integer pairs, exactly one nonempty contiguous
  `VMP` interval per output Unicode code point; starts and ends are each
  nondecreasing, equal/overlap is allowed, each rewrite interval stays within
  one source span, and the union covers every source code point;
- the nonempty adjudicated set of acceptable normalized full-message forms;
- exact-versus-beam mode, pre/post-merge counts, exact span/partial/full
  reductions and their sum, returned path list, returned scores/order,
  per-path `q` numerator/weight, `q` maximum/normalizer, and the single scoped
  retained-mass field; and
- license/provenance lineage and provider/composition version.

Span reading text is bounded by 512 code points/2,048 UTF-8 bytes; direct and
every normalized full path by 20,000/80,000; canonical provider manifest bytes
by 4 MiB. Overflow rejects rather than truncates. The manifest uses recursively
declared field order, compact UTF-8, `ensure_ascii=false`, no whitespace,
terminal LF, nonfinite value, or extra field. It is the candidate-output
artifact, not the complete run audit. The canonical `SystemArtifactManifest`
and schema-`1.1.0` engine run envelope, emitted only after valid system/VMP
preflight, bind the complete executed-source
closure, pinned runtime/float/math-backend contract, system/control identity, VMP,
`provider_execution`, candidate diagnostics, path IDs/hashes/lineage/binary64
scores and weights/effective spans, active paths, downstream hashes, registry
identity, status, and invalid codes under exact byte bounds and SHA-256. The
normative inventory appears in
[ENGINE_SPEC.md](ENGINE_SPEC.md#32-canonical-system-artifact-manifest-and-engine-run-envelope).

The manifest's exact top-level order is
`manifest_version,vmp_sha256,provider_config_id,provider_mode,normalizer_id,rewrite_spans,units`.
Every successful composed or direct manifest binds 1..64 ordered,
nonoverlapping, artifact-disjoint `rewrite_spans` objects with ordered
`span_index,start,end,source_text`; bypass alone uses an empty list. Composed
units correspond one-to-one to these spans. A direct full-path unit does not
authorize whole-message rewriting: every reading preserves every code point
outside the bound spans and every visible-artifact slice exactly, with changes
allowed only inside the corresponding span alignment. Zero eligible spans route
only through `NO_ELIGIBLE_ROMANIZED_SPAN` identity bypass. A provider-failure
execution retains its attempted 1..64 nonempty eligible spans in
`provider_execution`, while its identity-output manifest and effective path use
no rewrite spans.

The message record validates that non-span code points and their identity
alignments are preserved. The candidate-only normalizer is an alignment-aware
transducer `(candidate_text,candidate_alignment) ->
(normalized_text,normalized_alignment)` and rejects every length, integer,
bounds, emptiness, monotonicity, within-span, source-coverage, nonspan-change,
and visible-artifact violation frozen in the engine specification. `E0` permits
only the identity transducer. The record never embeds a Fisher phishing label
or protected-partition identifier.

## 5. Multi-span candidate construction and calibration

Romanized spans are sorted, nonoverlapping half-open `VMP` code-point ranges and
cannot overlap visible artifacts. For Romanized span `i`, merge only candidates
with identical `(normalized text, alignment)`. A raw contributor begins with its
`(unit_index,provider_rank)`. A composed contributor stores mode plus ordered
unit/rank-set objects; a direct contributor stores mode, unit zero, and ranks;
a bypass contributor stores mode only. A merged full path stores schema-1.0.0
contributors sorted by canonical UTF-8 bytes. These compact objects never
expand the exponential raw rank cross-product. Every LSE operand sequence is
sorted by individual contributor bytes. Use finite IEEE-754 binary64, stable max-shift LSE, and sequential
operations in that order; canonicalize negative zero to positive zero. Bit
replay is claimed only for the pinned runtime/container/architecture/math
library, not universally across platforms. Normalize the merged raw logits:

`a_ir = ell_ir - logsumexp_t(ell_it)`.

For full-message hypothesis `h = (r_1, ..., r_I)`, preserve every byte outside
the replaced `VMP` spans and score:

`s(h) = sum_i a_i,r_i`.

Merge full-message candidates only when normalized text and complete alignment
are identical. Use an overflow-safe comparison of the product of post-span-merge
candidate counts with 64. Enumerate exactly when it is at most 64. Otherwise use
a deterministic width-64 beam whose partial key is emitted normalized prefix
plus encoded alignment. After every expansion, merge exact partial keys with
the same canonical binary64 LSE, then prune by descending score, normalized
UTF-8 text bytes, encoded-alignment bytes, and contributor identity. Return at
most `K = 8` under the same order, with no padding.

For only that returned bounded list, construct `q` with the exact runtime-bound
binary64 operations: `t_k=binary64(s_k/T_tr)`; take `m=max_k t_k`; set
`n_k=binary64(exp(binary64(t_k-m)))` using the manifest-bound math backend;
sequentially sum `n_k` from positive zero in ascending full-contributor-lineage
bytes; and set `q_k=binary64(n_k/denominator)`. Persist
`q_max_f64_bits`, `q_normalizer_f64_bits`, and each path's
`q_numerator_f64_bits` and `q_f64_bits`. Display order never changes the
accumulation order.

`q` is a calibrated distribution over the returned bounded list, not a claim
about unenumerated interpretations. All score, merge, and ordering arithmetic is
binary64; reject nonfinite values and canonicalize signed zero to positive zero
before comparisons and serialization. At each merge stage, the reduction count
is `sum_g (|g|-1)` over its deterministic duplicate groups. Record separate
span, partial, and full reductions and their exact sum, plus exact/beam mode,
input/postmerge/returned counts, and retained pre-`K` composition mass.
Compute mass only in the log domain:
`Delta=LSE(returned scores)-LSE(preK scores)` and `mass=exp(Delta)`. Reject an
empty set, nonfinite operand/result, or `Delta>0`; never clamp. Persist both LSE
values and retained mass as exact 16-character lowercase big-endian binary64
bit strings in the canonical engine-run diagnostics after signed-zero
canonicalization. The only mass field is
`retained_preK_composition_mass_f64_bits`. For exact enumeration, `preK` is the
full enumerated, duplicate-merged set and `preK_scope=EXACT_FULL`. For beam
mode, `preK` is only the final width-bounded, duplicate-merged pre-`K` beam and
`preK_scope=FINAL_BEAM`; it is not total-lattice posterior mass. `T_tr` affects
only `q`. Direct
`sum(exp(s))` ratios are prohibited because valid long paths can underflow to
`0/0`.

Select one generator configuration using only
`transliteration_development`, lexicographically by highest minimum language
`coverage@8`, then highest macro `coverage@8`, then highest macro `coverage@1`,
then ascending configuration-ID UTF-8 bytes. Fit `T_tr` only after that choice.
A direct contextual message-level provider may compete only as a separate
named configuration/run/ablation; no provider is assumed to win and no direct
reading is pooled with composed paths. It must emit the same complete alignment
interface and obey its full-path manifest, merge, ordering, numeric, and bound
rules.

Fit the single positive scalar `T_tr` only on group-disjoint message-level
`transliteration_temperature_calibration` by minimizing:

`L_tr = -sum_i log(sum_{k in A_i} q_ik)`,

where `A_i` is the set of returned full-message candidate indices adjudicated
acceptable for message `i`. It may be empty when generation misses every
acceptable full-message interpretation. Freeze the provider selection,
composition algorithm, ordering, normalizer, and `T_tr` before phishing-model
training. Phishing labels and gradients cannot update or recalibrate `q_k`.

If no acceptable candidate appears in the generated top eight during temperature fitting, record zero acceptable mass and apply the preregistered finite numerical floor only inside the log calculation; never mark an unacceptable candidate acceptable. The floor value and numeric dtype must be frozen in configuration before evaluation.

## 6. Frozen evaluation and reporting

Top-K acceptable-form coverage is:

`coverage@K = count(A_i intersects returned ranks 1..K is nonempty) / count(eligible message records)`.

Report the selected configuration exactly once on
`transliteration_evaluation`, with `K in {1, 2, 4, 8}`, message-level candidate
NLL, number of groups, exact-versus-beam rates, retained-mass distribution, and
confidence intervals overall and by language. The Fisher uncertainty route
requires top-8 coverage of at least 90% overall and at least 85% in each Hindi,
Tamil, and Telugu evaluation subset. These are future gates, not measured
results.

Do not inflate coverage by adding references after inspecting model failures. Reference-set corrections require a versioned adjudication record and a clean rerun.

## 7. Bypass paths

Before dispatch, an eligibility selector result that is not an array, exceeds
64 entries, or contains any Boolean/noninteger/out-of-range/empty/overlapping/
artifact-touching/nonordered span uses the exact `ELIGIBILITY_INVALID` provider
outcome. It retains no span or output manifest, makes no provider call, records
only the bounded raw entry count and zero accepted spans, and is `INVALID` at
`PROVIDER_EXECUTION`. A rewrite or alignment defect discovered after a provider
manifest was accepted remains a `CANDIDATE` failure and retains that manifest.

Exactly two bypass modes are valid:

- `NO_ELIGIBLE_ROMANIZED_SPAN`: one unchanged, identity-aligned raw path with
  `s=0` and `q=1`; this includes messages for which no Romanization operation is
  eligible, including already-native content; and
- `PROVIDER_FAILURE_RAW_FALLBACK`: one unchanged, identity-aligned raw path with
  `s=0` and `q=1`, allowed only for provider/normalizer unavailability or timeout
  before any output is accepted and only when the identity fallback validates;
  attempted eligible spans/configuration remain in `provider_execution`, with a
  non-`NONE` failure code, no effective rewrite span, and
  `DEGRADED_STOP_AFTER_IDENTITY` status.

Processing stops before prediction. Candidate failure never deletes the raw representation and is retained for
accounting, but it invalidates every confirmatory or protected metric run and is
never counted as candidate-coverage success. No-eligible records are outside
the applicable paired-resource coverage denominator. Both identity outputs can
share their candidate-output manifest hash because the canonical engine run
envelope binds cause/configuration/spans/invocation. An empty enabled candidate
set and any malformed, nonfinite, alignment-breaking, provider-invalid, or
normalizer-invalid output is `INVALID`, never degraded. The `E0` identity normalizer is permitted only for synthetic
known-answer interface tests and proves no linguistic normalization capability.

## 8. English–Indic applicable subset

Before observing model results, the annotation guide must freeze an `english_indic_transliteration_applicable` rule. It is true only when the model-visible message contains at least one adjudicated Roman-script span intended as Hindi, Tamil, or Telugu lexical content for which a native-script candidate is meaningful. English words, organization names, URLs, alphanumeric identifiers, and conventional English borrowings alone do not qualify.

Report candidate coverage and H4 ambiguity analyses both on this applicable
subset and with its prevalence denominator. Non-applicable English–Indic records
use `NO_ELIGIBLE_ROMANIZED_SPAN` and cannot be counted as successful
transliteration coverage.

## 9. Routing candidates and prior-art boundary

[Large-scale Indic transliteration evaluation](https://aclanthology.org/2021.eacl-main.303/) and [Aksharantar](https://aclanthology.org/2023.findings-emnlp.4/) establish substantial transliteration resource/evaluation precedent. [IndicLID](https://arxiv.org/abs/2305.15814) is not the only routing candidate: [Benton et al. 2025](https://aclanthology.org/2025.emnlp-main.117/) specifically evaluate informally Romanized language identification.

Treat IndicLID and the informally Romanized LID approach as evaluated candidates/comparators on `development`, not automatic selections. Before use, pin the exact checkpoint, API, code revision, preprocessing, output-label mapping, and license; all are **UNKNOWN** until inspected. Routing evaluation must include native-script, Romanized, and English–Indic applicable/non-applicable subsets and report per-stratum confusion. Routing cannot use Fisher protected labels during inference or tune after protected access.

## 10. Leakage and release controls

- No Fisher `primary_test` text, artifact, gold span, label, provenance intent, or descendant can enter a paired resource.
- Do not mine protected Fisher partitions to expand acceptable forms or aliases.
- Resource-derived candidates inherit source/license lineage.
- A resource update after protected-set access creates a new
  resource/model version and an exploratory rerun; it cannot silently alter the
  confirmatory system.
- Release only source rows and derived candidates explicitly permitted by the recorded license, terms, consent, and privacy decision.

## 11. Verification ownership

The future engine validator may verify field types, the one shared configured
provider rule for every factorial condition, the exact provider-reading manifest,
provider-execution object, system-artifact manifest/run envelope, their canonical
bytes/hashes,
provider/normalizer ID grammar, unit/rank identity, finite binary64 bit strings,
positive-zero canonicalization, partition values, group separation, hashes,
span/path/manifest limits, visible-artifact nonoverlap, complete alignment
encoding and coverage,
`(normalized text, alignment)` duplicate merging, overflow-safe exact/beam
choice, mode-specific provider-rank/lineage binding, canonical LSE operand order,
partial-merge/prune keys, byte-order ties, log-domain retained mass and all three
exact binary64 bit strings, preserved non-span code points, explicit
bypass/degraded status, no padding,
acceptable-set nonemptiness, and lineage references. It cannot decide linguistic
acceptability, exact implementation rounding without executable evidence,
lawful use, privacy, consent, or redistribution. Those require documented human
review.

## 12. Exit gate

The transliteration component is frozen only when resource decisions and hashes
are complete; partitions are group-disjoint; configuration selection follows
the frozen lexicographic rule; multi-span message records validate; `T_tr` is
fitted only on message-level calibration; bypass, exact/beam, merge, tie, and
alignment/mass-accounting tests pass; provider failures remain degraded and out
of coverage success and protected/confirmatory metrics; the frozen evaluation
coverage gates pass; and an
independent reviewer confirms no Fisher protected-set tuning.
