# Fisher Phase-0 data contract v1.2

Status: executable dataset-snapshot contract for the 1,200-item ontology pilot.
Every record uses `schema_version: "1.2.0"`. Version 1.2 is a breaking pre-data
migration: it adds a bounded visible-artifact inventory and a canonical VMP hash
to every item, and binds explicit destination annotations to that inventory. It
retains the v1.1 separation of registry-derived relations from human annotation
gold. No backward compatibility is provided because no authentic corpus exists
under a superseded schema. This
validator checks stored mechanisms; it does not authorize data collection,
establish the truth of a registry approval or annotation, verify an external
human safety audit, train a
model, or establish deployment performance.

## Governance boundary

[`data/source_ledger.example.jsonl`](../data/source_ledger.example.jsonl) is the
pre-authorization governance record. It is intentionally blocked and is not an
input to this CLI. `sources.jsonl` is the strict dataset-snapshot projection,
linked to the governance ledger by stable `source_id`. The CLI does not validate
the full ledger or resolve approval, stewardship, storage, ethics, privacy,
license, release, or withdrawal work outside the projection.

## CLI, modes, and exit status

```console
python3 -m fisher_data validate \
  --sources PATH/sources.jsonl \
  --items PATH/items.jsonl \
  --annotations PATH/annotations.jsonl \
  [--registry-manifest PATH/registry_manifest.jsonl] \
  [--registry-references PATH/registry_references.jsonl] \
  --mode draft|pilot-final --format text|json
```

Exit status is 0 with no errors, 1 with validation errors, and 2 for invalid CLI
usage. Output defaults to text. Diagnostics and JSON keys are deterministic.
Messages are fixed strings; diagnostic metadata permits only generated line
numbers, contract-owned field paths, fixed dataset names, and validated safe IDs.
Untrusted JSON keys and record contents are never copied into diagnostics.

`draft` applies all schema, safety, cross-file, ancestry, partition,
registry-reference, and semantic rules. It reports the three pilot
allocation/cardinality checks as
warnings. A draft may omit both registry artifacts. If a registry-reference file
contains any records, a manifest must also be supplied and the reference
inventory must be complete for the supplied final annotations. An empty
reference file or a manifest alone is permitted for preflight. `pilot-final`
requires both files, at least one approved manifest snapshot, exact endpoint-pair
reference coverage, and applies all allocation, adjudication, coverage, and
reliability gates below.

`corpus-final` is deliberately not implemented in contract v1.2. The 6,000-item
corpus allocation therefore remains a hard pre-corpus governance/implementation
gate; passing either implemented mode is not corpus-final approval.

## JSONL, schema, safety, and operational bounds

Inputs are UTF-8 JSON Lines with exactly one object per nonblank physical line.
Blank lines, duplicate keys, non-finite numbers, malformed JSON, and non-object
records are errors. All fields documented for an object are required and unknown
fields are errors. JSON types are exact: a Boolean is not an integer. Every
source, item, annotation, registry-manifest, and registry-reference record
requires schema version `1.2.0`.

Every input path must resolve directly to a regular file. The validator rejects
directories, symbolic links, FIFOs, sockets, and devices before reading. It uses
a no-follow descriptor open, verifies the opened descriptor's device/inode and
regular-file type, then captures at most 512 MiB plus one raw byte from that
descriptor. Overflow is rejected before UTF-8 decoding or line parsing. The
accepted immutable byte string is decoded once; only then are CRLF, LF, and CR
interpreted with universal-newline physical-line semantics. Thus CRLF bytes and
discarded tails of overlong lines still count against the raw-byte limit.
Diagnostics never reproduce an input path.

Before hashing or schema use, decoded keys and values are scanned for escaped
surrogate code points, bidirectional formatting controls U+061C, U+200E–U+200F,
U+202A–U+202E, and U+2066–U+2069, and C0 controls U+0000 through U+001F other
than TAB, LF, and CR. They produce fixed diagnostics and reject the record.
Every decoded string value is also scanned for high-confidence live routes:
HTTP/HTTPS/FTP and `www` routes, email, bare domains, valid bare IPv4 addresses,
syntactically valid bare IPv6 addresses, 10-to-15-digit phone forms, and bounded
ASCII UPI/contact-style handles, plus secret-like OTP, PIN, password, passcode,
credential, and recovery-code assignments. The handle grammar is one to 256
ASCII letters, digits, dot, underscore, or hyphen before `@` (starting with an
alphanumeric), followed by one to 64 ASCII letters, digits, underscore, or
hyphen (starting with a letter), with no dotted suffix. It is deliberately a
syntactic contact-route guard and does not assert that a handle is an active UPI
VPA. One or more periods immediately after the handle are treated as sentence
punctuation only when the period run is not followed by an ASCII alphanumeric,
underscore, or hyphen; consequently a dotted email/domain suffix is not matched
as a shorter handle prefix. For IPv6 parsing, terminal ASCII periods in the
bounded candidate are likewise ignored as sentence punctuation, while internal
dots remain available for IPv4-mapped IPv6 syntax. Unicode dot equivalents
U+2024, U+3002, U+FE52, U+FF0E, and U+FF61 are
mapped to ASCII full stop only in a temporary safety-scan copy; immutable stored
text, offsets, and hashes are unchanged. Unicode/IDN email or domain labels are
also covered. Reserved `.example`, `.invalid`, and `.test` hosts and defanged
`[.]` forms are allowed by the global route scanner. This conservative guard is
not proof that content is safe, non-sensitive, non-routable, or non-executable.

Operational denial-of-service bounds are part of v1.2:

| Bound | Limit |
| --- | ---: |
| bytes per input file | 512 MiB |
| decoded characters per physical line | 1,000,000 |
| source records | 10,000 |
| item records | 10,000 |
| annotation records | 40,000 |
| registry-manifest records | 10,000 |
| registry-reference records | 100,000 |
| object/list nesting depth | 32 |
| members in any object or list | 10,000 |
| item `text` Unicode code points | 10,000 |
| visible artifacts per item | 64 |
| rationale Unicode code points | 500 |

These are ingestion-safety bounds, not statistical sampling rules. Dates are real
canonical `YYYY-MM-DD`; SHA-256 values are exactly 64 lowercase hexadecimal
characters. IDs are full-string ASCII matches:

| Field | Full form |
| --- | --- |
| `source_id` | `src_[a-z0-9][a-z0-9_-]{0,62}` |
| `item_id` | `item_[a-z0-9][a-z0-9_-]{0,62}` |
| `leakage_component_id` | `component_[a-z0-9][a-z0-9_-]{0,62}` |
| `annotation_id` | `annotation_[a-z0-9][a-z0-9_-]{0,62}` |
| `annotator_id` | `annotator_[a-z0-9][a-z0-9_-]{0,62}` |
| `registry_snapshot_id` | `registry_[a-z0-9][a-z0-9_-]{0,62}` |
| `registry_reference_id` | `registry_reference_[a-z0-9][a-z0-9_-]{0,44}` |
| `registry_reviewer_id` | the shared person namespace `annotator_[a-z0-9][a-z0-9_-]{0,62}` |
| `registry_evidence_id` | `registry_evidence_[a-z0-9][a-z0-9_-]{0,45}` |
| `resolver_version` | `resolver_MAJOR.MINOR.PATCH`, each numeric part 1–6 digits, with the manifest version's optional lowercase prerelease syntax |

## Partitions and sources

The exact partitions are `pilot`, `unassigned`, `development`,
`probability_calibration`, `safety_threshold`, `primary_test`, `external_test`,
and `excluded`. The protected partitions are `probability_calibration`,
`safety_threshold`, and `primary_test`. There are no `train` or `dev` aliases.

Each `sources.jsonl` record contains exactly `schema_version`, `source_id`,
`artifact_sha256`, `provenance`, `rights`, `consent`, `privacy`, and
`eligible_partitions`. The last is a nonempty unique list of canonical partitions.

`provenance` contains exactly `provenance_class`, nonempty `origin_name`, nonempty
`collected_by`, and `collected_date`. Classes are
`tester_donated_authentic`, `tester_authored_simulation`, `public_authentic`, and
`llm_drafted_human_edited`. `rights` contains `basis` (`consent`, `contract`,
`license`, or `public_domain`), nonempty `license_id`, and Boolean
`research_use_permitted`. `consent` contains `status` (`granted`,
`not_applicable`, or `withdrawn`), nonempty `scope`, and nonempty
`withdrawal_process`. `privacy` contains Boolean `contains_personal_data`,
`deidentified`, and `reviewed`.

Research use must be permitted; privacy review must be complete; personal data
must be deidentified; withdrawn sources are rejected; and tester sources require
granted consent. An LLM source cannot declare a protected partition. A
`public_authentic` source must declare a nonempty subset of only `development`
and `external_test`. Public-authentic items and every descendant are likewise
allowed only in those two partitions—not `pilot`, `unassigned`, `excluded`, or a
protected partition.

## Items, exclusions, ancestry, and leakage

Each `items.jsonl` record contains exactly:

`schema_version`, `item_id`, `source_id`, `text`, `content_sha256`, `vmp_sha256`,
`language`, `language_stratum`, `partition`, `exclusion_reasons`,
`visible_artifacts`, `privacy`, `generation`, `leakage_component_id`, and
`lineage`.

`content_sha256` is recomputed as `SHA-256(UTF-8(text))` without trimming,
normalization, or newline conversion. `vmp_sha256` is recomputed from the exact
UTF-8 bytes of canonical JSON for the object
`{"text": item.text, "visible_artifacts": item.visible_artifacts}`. Canonical
serialization recursively sorts object keys, uses compact separators `,` and
`:`, emits Unicode without ASCII escaping, and prohibits non-finite numbers;
array order is preserved. Known language/stratum pairs are
`hi`/`hindi`, `ta`/`tamil`, `te`/`telugu`, and
`mixed`/`english_indic_code_mixed`. `unknown`/`uncertain` is allowed only on an
`excluded` item. A retained pilot item must use one of the four study strata.

`exclusion_reasons` is a sorted unique controlled list. It is empty for every
non-excluded row and nonempty for every excluded row. Its vocabulary is:

- `unresolved_primary_label`
- `unresolved_language_stratum`
- `governance_ineligible`
- `safety_ineligible`
- `privacy_ineligible`
- `out_of_scope`
- `duplicate_or_leakage`

Pilot-final permits only the first two reasons, and they must exactly correspond
to the final annotation's uncertain primary-label and/or language-stratum
decision. Every excluded pilot attempt remains in the unresolved numerator and
attempted-item denominator; malformed records cannot hide a reduction.

`privacy` contains Boolean `synthetic`, `pii_reviewed`, and `contains_pii`; review
must be complete and `contains_pii` false. `generation` contains `method`
(`human`, `llm`, `template`, or `augmentation`) and nonempty `model_id`. Direct
LLM generation requires an ID other than `none`; other methods require `none`.
Direct LLM generation and source provenance must agree.

`lineage` contains unique `parent_item_ids` and operation `original`,
`translation`, `transliteration`, `paraphrase`, `counterfactual`, or
`augmentation`. Originals have no parents; derived items have at least one
existing parent. Self-links and directed cycles are errors. The validator builds
parent-to-child adjacency once and propagates direct public/LLM seeds to all
descendants in O(V+E) time.

An item is LLM-assisted when its source or generation is LLM-based or any
ancestor is LLM-assisted. LLM ancestry is forbidden in protected partitions,
must be no more than 30% of `development`, and independently no more than 30% of
retained `pilot`. Empty shares report `null`.

`leakage_component_id` is one externally precomputed final connected-component
ID. Parent and child must share it. A component cannot cross two non-excluded
partitions. A component touching a protected partition must contain exactly one
item globally, including excluded relatives, so protected FPR observations are
component-independent and monostratal. The CLI does not reconstruct omitted
campaign, author, template, artifact, or near-duplicate edges.

Exact text duplicates are rejected. Canonical duplicates are rejected after
Unicode NFKC, case folding, Unicode-whitespace splitting, and joining with one
ASCII space. This does not detect semantic paraphrases.

### Visible non-gold artifact inventory and VMP

`visible_artifacts` is a required array of zero through 64 records. Together
with immutable item `text`, it reconstructs the Visible Message Packet (VMP)
available as non-gold model input. It contains only visible safe
representations and their offsets. It contains no annotation, label, donor
intent, source provenance, scenario or campaign metadata, registry state,
registry coverage, registry evidence, or protected outcome.

Each entry contains exactly `kind`, `kind_reason`, `representation`, `start`,
`end`, and `text`. `kind` is exactly `URL`, `DOMAIN`, `PHONE`, `UPI`, `BANK`,
`EMAIL`, `APP`, or `OTHER`. `kind_reason` is 1–500 Unicode code points exactly
when `kind` is `OTHER`; it is the empty string for every controlled kind.
`representation` is exactly `TYPED_PLACEHOLDER`, `RESERVED`, or `DEFANGED`.
Representation grammar is frozen and case-sensitive except for the expressly
case-insensitive reserved-host grammar:

- `TYPED_PLACEHOLDER` is exactly `[URL]`, `[DOMAIN]`, `[PHONE]`, `[UPI]`,
  `[BANK]`, `[EMAIL]`, or `[APP]` for the matching controlled kind, and exactly
  `[ARTIFACT]` for `OTHER`.
- `RESERVED` must be the complete artifact surface, ASCII case-insensitively
  matching an optional `http://`, `https://`, or `www.` prefix, one or more
  conservative DNS labels, a final `.example` or `.invalid`, and an optional
  slash path containing only ASCII URL-path punctuation accepted by the
  validator. Ports, query strings, fragments, surrounding prose, `.test`, and
  `example.com`, `example.net`, or `example.org` are not accepted by this
  representation grammar. This intentionally narrow subset fails closed.
- `DEFANGED` must contain at least one exact case-sensitive marker: `[.]`,
  `(.)`, `[at]`, `[redacted]`, `hxxp:`, `hxxps:`, or `XXXX`.

Every representation must also pass the global live-route and secret-like-value
scanners. Offsets are exact integers, not Booleans. They are nonempty,
zero-based, half-open Unicode code-point ranges into immutable item `text`, and
stored artifact `text` equals the exact slice. Entries are unique, pairwise
nonoverlapping, and sorted by `(start, end, UTF-8(kind),
UTF-8(representation), UTF-8(text))`; duplicate and nested spans are therefore
invalid. Unknown entry fields are errors. The global surrogate, C0,
bidirectional-control, live-route, and secret-like-value scanners cover every
entry before schema use.

This inventory records visible input; it is not human annotation gold and does
not declare that an annotation span or final endpoint is correct. The validator
checks structure, offsets, the closed grammar, hashes, and conservative safety
syntax. It does not evaluate extractor recall or precision, prove real-world
safety or true defanging, prove that a placeholder preserves the original
artifact type, or authorize storage or release. Candidate rewrite spans in the
later engine must not overlap visible-artifact spans; that engine rule is not
implemented or claimed by this data validator.

Only `TYPED_PLACEHOLDER` mechanically binds `kind` to one exact surface token.
For `RESERVED` and `DEFANGED`, the validator checks the representation grammar
and global scanners but treats `kind` as human-audited metadata; it does not infer
the surface class or prove that the declared kind is true. Thus a representation
can be structurally valid while its declared non-gold kind remains wrong. That
known proof boundary must be resolved by the human data audit before real-data
use; schema validity is not extractor-quality or authenticity evidence.

## Annotation record

Each annotation contains exactly:

`schema_version`, `annotation_id`, `item_id`, `annotator_id`, `kind`,
`independent`, `primary_label`, `subtype`, `subtype_other_reason`,
`language_stratum`, `resolution_method`, `confidence`, `ambiguity_tags`,
`token_language_spans`, `code_mix_pair`, `facets`, `spans`,
`evidence_span_indices`, `romanization_ambiguities`, and `created_date`.

These records are human visible-message gold only. Blind annotators receive the
VMP—immutable message text plus the item's visible safe artifact inventory and
offsets—but the inventory is not copied into annotation records. They do not
receive source provenance, donor intent, primary labels, scenario or campaign
metadata, protected outcomes, a registry, registry coverage, registry evidence,
or registry-reference labels. The final adjudicator resolves only the same human
visible-message fields and has the same exclusions. Registry-derived fields are
unknown fields here and therefore fail validation.

`kind` is `blind` or `final`. Blind records are independent and use resolution
`not_applicable`; final records are not independent. Primary labels are `benign`,
`phishing`, and workflow state `uncertain`. Benign subtypes are `personal`,
`transactional`, `promotional`, `informational`, and `other`; other primary
labels use subtype `not_applicable`. `subtype_other_reason` is 1–500 Unicode code
points exactly for benign subtype `other`, and otherwise the empty string.
Confidence is `high`, `medium`, or `low`. Ambiguity tags are `language`,
`intent`, `actor`, `action`, `destination`, `romanization`, `missing_context`,
and `other`.

A binary final uses `adjudicated`. A final with uncertain primary label uses
`unresolved` and an excluded item. An annotation with uncertain language stratum
requires the `language` ambiguity tag. A known final language stratum must match
item `language_stratum` and `language`. Blind decisions remain independent and
may disagree with item/final metadata.

### Complete lexical-token inventory and language derivation

The machine lexical-token inventory is every maximal contiguous run of Unicode
General Category Letter (`L*`) or Mark (`M*`) code points in exact item text.
`token_language_spans` must cover that inventory exactly once, in order, with no
omission, extra span, split, overlap, or merge. Each entry contains exactly
`start`, `end`, `text`, `language`, and `script`.
Text equals the exact raw substring. Languages are `hi`, `ta`, `te`, `en`, and
`other`; scripts are `devanagari`, `tamil`, `telugu`, `latin`, and `other`.

Observed script is derived from Unicode names of every Letter/Mark code point.
Names containing DEVANAGARI, TAMIL, TELUGU, or LATIN contribute those scripts for
both Letters and Marks. A Common, Inherited, or otherwise unscripted Mark inherits
the sole recognized script found elsewhere in the same token. An unsupported
Letter, no recognized script, or multiple recognized scripts produces `other`.
Thus NFC and NFD Latin spellings remain Latin without normalizing stored text or
offsets. The declared script must equal the observed result.

Every machine lexical token enters the language-stratum denominator. Artifact,
brand, and identifier tokens are labeled contextually—often `other`—but cannot be
silently excluded. The ordered derivation is:

1. Code-mixed if English and exactly one of `hi`/`ta`/`te` are present, each is at
   least 20%, and neither is 70% or more. The pair is respectively `en_hi`,
   `en_ta`, or `en_te`.
2. Otherwise `hindi`, `tamil`, or `telugu` if its token share is at least 70%.
3. Otherwise `uncertain`, with `code_mix_pair: none`.

The stored annotation `language_stratum` and `code_mix_pair` must equal the
derived values. This ordering deliberately makes a 99:1 English/Indic row
uncertain, and a row with multiple positive core Indic languages cannot satisfy
the code-mix rule.

### Facets, spans, evidence, and phishing coherence

`facets` contains exactly one `facet`, `state`, `span_indices` record for each of
`claimed_actor`, `claim_or_problem`, `requested_action`,
`sensitive_item_or_asset`, `destination_artifact`, and `pressure_tactic`. State
is `explicit`, `not_explicit`, or `not_applicable`. Explicit facets have at least
one matching span; other states have none. Every structured span is referenced
exactly once.

Each `spans` entry contains exactly `start`, `end`, `text`, `facet`, `qualifier`,
and `qualifier_reason`. Facets are the six above plus `supporting_evidence`.
Destination qualifiers are `URL`, `DOMAIN`, `PHONE`, `UPI`, `BANK`, `EMAIL`,
`APP`, and `OTHER`; pressure qualifiers are `URGENCY`, `THREAT`, `AUTHORITY`,
`SCARCITY`, `REWARD`, `FEAR`, `TRUST`, `SOCIAL_PROOF`, and `OTHER`; other spans
use `N/A`. `qualifier_reason` is 1–500 Unicode code points exactly when qualifier
is `OTHER`, otherwise the empty string.

Offsets are zero-based, half-open Python string indices `[start,end)`, counting
Unicode code points in exact stored text—not bytes, grapheme clusters, normalized
text, or display columns. Stored span text equals `item.text[start:end]`. Spans
are sorted by start, end, facet, qualifier and unique; cross-facet overlap is
allowed. `evidence_span_indices` is sorted, unique, and references only
`supporting_evidence`; binary annotations require at least one.

Every explicit `destination_artifact` span must exactly match one item
`visible_artifacts` entry on `(start, end, text)`, and its annotation qualifier
must equal that entry's `kind`. There is no converse requirement: a visible
artifact need not become an explicit human destination span. Annotation records
cannot create or change the pre-annotation VMP inventory.

As a coherence check only, a phishing annotation requires `requested_action` and
`sensitive_item_or_asset` to be applicable (not `not_applicable`) and at least one
of requested action, sensitive item/asset, destination, claimed actor, or
claim/problem to be explicit. This does not establish that the label is true.

### Romanization ambiguity

Each ambiguity contains exact `start`, `end`, `text`, `language`,
`acceptable_forms`, and `affected_decisions`. The raw source span must have
observed Latin script and language `hi`, `ta`, or `te`. At least two acceptable
forms are required; each has nonempty `form`, declared `script`, and nonempty
`gloss`. Declared form script must match observed Unicode script. Uniqueness uses
the contract's NFKC/casefold/whitespace-canonical `(form, script)`, so changing only a gloss cannot fabricate a
second candidate. Affected decisions are a sorted, unique, nonempty subset of
`primary_label` and the six facets. An ambiguity affecting an actor/destination
comparison is represented through `claimed_actor` and/or `destination_artifact`;
there is no human relation decision.
`romanization_ambiguities` and the `romanization` tag are present together.
Surface Romanized variants without a decision ambiguity stay in raw text and
token-language records; v1.2 has no separate `romanized_variant` field.

### Non-gold registry references and registry manifest

Registry comparison is deliberately separate from human gold. After final
visible actor and destination endpoints are frozen, a separate registry-review
role receives only those endpoints and the frozen offline registry. It does not
receive the primary label, source provenance, or protected outcomes. Each
`registry_references.jsonl` row contains exactly:

`schema_version`, `registry_reference_id`, `item_id`, `final_annotation_id`,
`registry_reviewer_id`, `registry_snapshot_id`, `actor_span_index`,
`destination_span_index`, `label`, `registry_coverage`,
`registry_evidence_ids`, `resolver_version`, `blinding_attestation`, and
`created_date`.

`label` is `MATCH`, `MISMATCH`, or `UNKNOWN`; there is no `N/A` record.
`registry_coverage` is `complete`, `partial`, or `missing`. The attestation is
the exact controlled string
`primary_label_provenance_and_protected_outcomes_hidden`. It is a recorded claim,
not machine proof. `registry_evidence_ids` is a sorted unique list of safe IDs in
the external registry-evidence namespace. These are not message
`supporting_evidence` spans, and numeric message-span evidence indices are
unknown fields in a registry reference.

The named annotation must be a final annotation for the same item. The registry
reviewer uses the shared `annotator_*` person namespace and must differ from both
blind annotators and the final annotator for that item. Actor and destination
indices must refer respectively to explicit `claimed_actor` and
`destination_artifact` spans in the named final annotation. Every Cartesian pair
of those explicit endpoints has exactly one reference, ordered by item ID, final
annotation ID, actor index, destination index, and reference ID. Duplicate,
missing, or extra pairs are errors. When there are no applicable pairs, the
coherent artifact has zero rows; no `N/A` row is invented.

`MATCH` and `MISMATCH` require `complete` coverage, one or more registry evidence
IDs, and a bound approved manifest snapshot. `UNKNOWN` requires `partial` or
`missing` coverage and may have zero or more evidence IDs. In pilot-final, every
reference—including `UNKNOWN`—must bind an approved manifest snapshot.

Each `registry_manifest.jsonl` record contains exactly `schema_version`, safe
`registry_snapshot_id`, `artifact_sha256`, semantic `version` in
`MAJOR.MINOR.PATCH` form with an optional lowercase prerelease suffix,
`snapshot_date`, and external `approval_state` (`approved`, `pending`, or
`blocked`). Every reference snapshot ID requires a supplied, declared manifest
record.

The CLI checks schemas, safe identifiers, manifest binding and recorded approval,
reviewer separation by ID, endpoint references, deterministic order, label/
coverage/evidence coherence, and endpoint-pair inventory relative to the supplied
final annotations. It cannot verify that blinding actually occurred, that a
reviewer was authorized, that registry contents or labels are true, that the
registry is complete in the real world, that cited evidence is adequate, or that
the external approval is authentic.

## Pilot-final arithmetic and exact workflow

Pilot-final permits only `pilot` plus extra unresolved `excluded` attempts. It
requires exactly 1,200 retained pilot items, exactly 300 final-known items in each
study stratum, and—using final decisions—exactly 150 benign and 150 phishing per
stratum. Excluded attempts are not part of the 1,200 or balance allocation.
Every attempted item requires exactly two valid independent blind annotations
from distinct annotators and exactly one semantically valid final annotation from
a third annotator distinct from both. Excluded reasons must exactly match final
uncertain primary and/or language decisions. The unresolved rate is:

`all excluded attempts / (1,200 retained pilot items + all excluded attempts)`

It must be at most 5%. The denominator never shrinks for missing or malformed
annotations.

Pilot-final also requires an explicitly supplied registry-reference artifact and
registry manifest. Every applicable endpoint pair in every final annotation must
have exactly one reference bound to an approved snapshot. An explicitly supplied
empty reference file is valid when all final annotations have zero applicable
actor-by-destination pairs, provided an approved manifest is still supplied; the
report marks `zero_applicable_pairs: true`.

Completeness is the number of attempted items with exactly two valid, distinct,
independent blind records and one semantically valid third-annotator final record
divided by all retained-plus-excluded attempts. The final may be binary or
uncertain as permitted by its exclusion state. Completeness must be at least 95%.
This quality/reporting gate does not waive the exact record-cardinality, schema,
semantic, or annotator-distinctness errors above.

## Frozen blind-pair reliability

All metrics use valid distinct independent blind pairs before adjudication.
Undefined gated metrics fail pilot-final. Values are reported, not claimed as
empirical results by this specification.

| Metric | Frozen units / missing policy | Gate |
| --- | --- | ---: |
| binary-pair coverage | both blind primary labels binary / all attempted items | ≥ .95 |
| binary raw agreement | exact agreement over covered binary pairs | ≥ .90 |
| binary Cohen kappa | unweighted, same covered pairs; reported only | none |
| binary nominal Krippendorff alpha | same covered pairs | ≥ .80 |
| language raw agreement | exact five-state agreement over every valid attempted blind pair | none |
| language nominal Krippendorff alpha | four study strata plus `uncertain`, every valid attempted blind pair | ≥ .80 |
| facet applicability alpha | nominal alpha for each of six three-state facets over every valid attempted blind pair | ≥ .67 each |
| named per-stratum alpha | final-known stratum; endpoint-aware state+exact-range signatures for actor, action, and destination | ≥ .60 each |
| per-facet exact-span F1 | macro pairwise F1 for exact ranges where either blind is explicit; both absent omitted | ≥ .60 each |
| per-facet character-overlap F1 | macro pairwise F1 on covered character indices over the same union-explicit denominator | ≥ .75 each |
| endpoint-pair structure exact F1 | macro pairwise exact-set F1 on the Cartesian set `(actor_start,actor_end,destination_start,destination_end)` where either blind set is nonempty; both empty omitted | ≥ .60 |
| supporting-evidence exact F1 | macro pairwise exact-range F1 over covered binary pairs with union-nonempty evidence | ≥ .60 |
| supporting-evidence character-overlap F1 | macro pairwise character-index F1 on the same evidence denominator | ≥ .75 |
| attempted-item completeness | complete valid annotation bundles / all attempted items | ≥ .95 |

Nominal alpha uses observed pair disagreement and the pooled finite-sample
expected disagreement. A zero expected-disagreement denominator is undefined.
Macro span F1 is `2|A∩B|/(|A|+|B|)`; one empty side scores zero. The explicitly
frozen union denominator prevents mutually absent structured fields from
inflating agreement.

The report separately exposes a mechanically counted registry inventory:
applicable endpoint pairs, reference records, coverage counts (`complete`,
`partial`, `missing`), label counts (`match`, `mismatch`, `unknown`), and the
Boolean zero-pair state. Visible-message endpoint-pair structure F1 remains a
human reliability metric, but it contains no registry label. The report
intentionally exposes no relation-label human IAA, registry-relation F1, resolver
accuracy, or end-to-end model metric.

## Known limitations

The validator cannot prove consent authenticity, source truth, PII absence,
registry truth or real-world completeness, reviewer authority, actual blinding,
annotation correctness, provenance truth, completeness of the
external leakage graph, semantic deduplication, representativeness, fairness,
calibration, deployment safety, or execution of the preregistered external 10%
human safety audit. Those remain human/governance responsibilities.
Registry-reference report counts are inventories, not resolver accuracy,
precision, recall, or F1; those belong to model evaluation. Corpus-final
allocation and model-training or inference code are intentionally outside v1.2.
