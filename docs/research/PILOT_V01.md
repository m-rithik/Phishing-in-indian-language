# Fisher feasibility pilot schema v0.1.0

## Status and scope

This is a local-only data-readiness gate for the pre-preregistration 240-message feasibility
pilot. The later schema 1.2 / 1,200-item registry, structured-state G2, and research ontology
are out of scope. Passing this validator is not model evaluation, does not establish
phishing-detection performance, and does not authorize collection.

Collection remains **NOT AUTHORIZED** until the external accountable authorities approve the
zero-durable-raw intake design and transient environment, authorized access, raw retention of
zero, transformed-data retention and deletion, withdrawal handling, and the final consent
language and process. The validator verifies only machine-readable fields; it cannot verify
that consent was actually informed or that a consent reference maps to a valid record.
It also cannot prove identifier opacity, actual annotator blinding, reviewer qualification,
or the completeness of source, donor, campaign, or leakage-component grouping. Those remain
human governance and screening responsibilities.

The operational [Collection-to-Quarantine packet](PILOT_COLLECTION_PACKET.md) is
currently `BLOCKED` and defines the external SG1 decisions, separate state machines,
and synthetic acceptance evidence required before any real intake.

## Privacy boundary

- Original message bytes and raw-byte digests have durable retention of zero and must never
  enter files, logs, telemetry, caches, backups, Git, chat, issue trackers, command output, or
  research systems. The approved ephemeral text-only intake must transform safely before any
  write or reject with zero message persistence.
- Recruitment/eligibility/consent/refusal/withdrawal records and the mapping between consent
  references and people remain in a separate approved external vault with no message content.
- Message input remains unavailable until affirmative consent is valid for the exact activity
  and tier. The ephemeral intake accepts text only and rejects attachments.
- Only deidentified, defanged, model-visible text may enter `items.jsonl`.
- Consent references, source IDs, batch IDs, annotator IDs, item IDs, and leakage-component IDs
  must pass a bounded ASCII syntax check. Syntax does not prove opacity: generate random opaque
  IDs outside message content and never encode names, phone numbers, email addresses, or other
  personal data in an ID.
- A `privacy_review` value of `true` and an artifact-review status of `passed` are explicit human
  assertions. Automated scans are an additional fail-closed gate, not a substitute for review.
- Validator diagnostics contain only codes, record kind, line number, and field name. They do
  not echo paths, message text, identifiers, or field values.

Validator inputs must live in an approved, access-controlled external restricted mount or
service. Vault records, mappings, and restricted transformed pilot inputs must never be below
any repository checkout, even when a path is ignored. Pass absolute external paths to the
validator and never overwrite the tracked synthetic examples. The `data/raw/` ignore rule is
defense in depth, not an approved storage workflow or access control. Original message bytes
must never be stored there or in any other durable location. Maintain the intake-screening and
disposition history in an external append-only restricted ledger; do not put that ledger in Git
or chat.

The loader rejects symlinks and non-regular inputs and bounds bytes, physical LF-delimited
records, and line length before parsing. A filesystem path can still change between metadata
inspection and reading, so these checks do not eliminate the operating-system TOCTOU boundary.
Run validation only from an approved environment with access limited to authorized researchers,
using the absolute paths of the external restricted inputs.

## Input files

All inputs are bounded UTF-8 JSONL. LF is the only physical record delimiter; one terminal CR
is stripped from each record to support CRLF. A final newline does not create a blank record.
Blank physical records, invalid records, and valid records all count toward the per-file record
bound. JSON numbers, duplicate keys, non-finite constants, extra keys, and missing keys are
errors. Every row uses `schema_version` `0.1.0`.

`sources.jsonl` has exactly: `schema_version`, `source_id`, `provenance_class`,
`consent_status`, `consent_reference`, `collection_batch_id`,
`internal_research_permitted`, `release_tier`, and `source_status`. Accepted sources are active,
internal-only, consent-granted, internally permitted `tester_donated_authentic` or
`tester_authored_simulation` records.

`items.jsonl` has exactly: `schema_version`, `item_id`, `source_id`, `text`,
`content_sha256`, `language_stratum`, `final_label`, `label_resolution`,
`leakage_component_id`, `romanized_indic`, `romanization_ambiguous`, `artifact_review`,
`privacy_review`, and `partition`. `content_sha256` is the lowercase SHA-256 of the exact UTF-8
bytes of the approved de-identified/defanged `text`; it is never an original-message digest or
cross-zone equality token. The four strata are `hindi`, `tamil`, `telugu`, and
`english_indic_code_mixed`; final labels are `phishing` and `benign`; partition is `pilot`.
Artifact review is exactly an object with `status: passed` and representation `none`,
`typed_placeholders`, or `defanged`. The exact typed placeholders are `[URL]`, `[DOMAIN]`,
`[EMAIL]`, `[PHONE]`, `[UPI]`, `[IPV4]`, and `[IPV6]`. Representation `none` forbids these
tokens, `typed_placeholders` requires at least one, and `defanged` permits either state.
Automated safety scanning uses an NFKC view with every Unicode `Cf` format control and a frozen
set of additional default-ignorable code-point ranges removed,
but preserves the exact approved transformed text and hashes its exact UTF-8 bytes. The frozen
stdlib-only predicate covers `00AD`, `034F`, `061C`, `115F–1160`, `17B4–17B5`, `180B–180F`,
`200B–200F`, `202A–202E`, `2060–206F`, `3164`, `FE00–FE0F`, `FEFF`, `FFA0`,
`FFF0–FFF8`, `1BCA0–1BCA3`, `1D173–1D17A`, and `E0000–E0FFF`, including tags and
supplementary variation selectors. This conservative frozen list is not claimed to remain
exhaustive across future Unicode versions and must be reviewed when the Unicode runtime changes.
Bidi controls are independently rejected before removal. Disallowed
control characters, effectively invisible text, recognized live artifacts, bounded residual
candidates, and obvious credential or financial-identifier values also fail validation.

`romanized_indic` and `romanization_ambiguous` are human screening assertions, not inferred
language facts. Ambiguity can be true only for an item screened as Romanized Indic. A later
research decision must block any transliteration experiment when the applicable pilot has zero
Romanized Indic coverage; this schema does not invent a numerical sufficiency threshold.

`annotations.jsonl` has exactly: `schema_version`, `annotation_id`, `item_id`, `annotator_id`,
`kind`, `primary_label`, `language_stratum`, and `confidence`. Kinds are `blind` and
`adjudication`; blind annotation may use `uncertain`, while an adjudicated final outcome must be
binary and use one of the four known strata.

## Annotation and leakage rules

Every item has exactly two blind annotations by distinct annotators. If both the label and
stratum agree and are final values, adjudication is forbidden and the item records
`blind_agreement`. Otherwise exactly one distinct adjudicator supplies the final binary label
and known stratum, and the item records `adjudicated`.

Unicode NFKC normalization, removal of format controls, case-folding, and whitespace collapse
define normalized exact duplicates. Retained normalized exact duplicates are rejected and
cannot fill quotas. The audited template rule also normalizes digit runs, so route/number
variants under that rule must share a component. Every `source_id` must map to exactly one
component, and sources that repeat a consent reference or collection batch must collectively
map to exactly one component. These containment rules prevent a donor/source/batch group from
crossing the dry-run folds. All messages derived from the same source
event, campaign, template, or near-semantic duplicate family must also be assigned the same
leakage component by researchers before splitting. No arbitrary character-similarity threshold
is automated because no threshold has yet been validated for this pilot.

## Draft and ready modes

`draft` enforces schema, authorization fields, safety scans, hashes, references, annotation
workflow, and duplicate grouping. Readiness deficits are warnings, so a structurally valid
small rehearsal exits zero.

`ready` additionally requires:

- exactly 240 items;
- exactly 30 items in every label-by-language cell (2 labels × 4 strata);
- at least five distinct leakage components in every cell;
- no component containing more than 10 of the 30 items in any cell;
- blind label raw agreement of at least 0.90, where only matching binary labels count as an
  agreement and any `uncertain` rating remains in the denominator;
- blind language known raw agreement of at least 0.90, where only matching known strata count
  and matching or discordant `uncertain` ratings remain in the denominator;
- five-state nominal Krippendorff alpha of at least 0.80 for blind language strata, and nominal
  alpha of at least 0.80 for blind labels;
- defined gated metrics; and
- deterministic three-fold whole-component assignment balancing the complete eight-cell
  vector, with at least five components and all eight cells represented in every fold.

The fold assignment is a deterministic leakage and allocation dry run. It is not model
evaluation, a statistical-power calculation, or evidence that three folds are scientifically
adequate. Likewise, `ready` may contain entirely tester-authored simulations. A passing result
is never evidence that authentic phishing messages were collected or that Fisher detects them.

The report is aggregate-only: counts, source-level and item-level provenance classes,
cell/component counts, romanization counts, disagreement/uncertainty item and rating counts and
rates (a blind rating is uncertain when either its label or language stratum is `uncertain`),
agreement metrics, fold component/cell aggregates, and sanitized diagnostics. It
contains no model metrics, row text, identifiers, values, or input paths.
