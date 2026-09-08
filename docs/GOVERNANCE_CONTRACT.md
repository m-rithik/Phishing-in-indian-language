# Fisher governance-ledger contract v1.0

Status: executable **mechanical projection**; human collection authorization remains blocked.

This contract implements the strict source-record projection already specified by
[`SOURCE_LEDGER.md`](research/SOURCE_LEDGER.md). It does not replace the consent,
ethics, privacy, registry, annotation, or dataset-snapshot protocols. In
particular, a machine-valid `AUTHORIZED` record is only a structurally coherent
claim that the referenced gates were completed. The validator cannot establish
that those claims are true or that collection is lawful, ethical, safe, or
approved.

## CLI and exit status

```console
python3 -m fisher_governance validate \
  --ledger PATH/source_ledger.jsonl \
  --format text|json
```

The output separates four concepts:

- `schema_valid`: strict JSONL, schema, safety, graph, and cross-field checks
  have no mechanical error;
- `machine_authorization_ready`: the number of `AUTHORIZED`/`INGESTED` source
  records satisfying all representable source-level gates;
- `not_machine_verifiable`: fixed, explicit human or unrepresented gates whose
  state remains `UNKNOWN`; and
- `collection_ready`: always `false` in this projection because the frozen
  ledger has no authenticated human-governance package input.

Exit status is `0` only when `collection_ready` is true, `1` for a mechanically
invalid or still-blocked ledger, and `2` for invalid CLI usage. Consequently,
v1.0 fails closed with exit `1` even when an `AUTHORIZED` record is mechanically
coherent. Programs that need structural diagnostics must read `schema_valid`
rather than interpreting exit `1` as a schema error. Invalid argument handling
uses fixed usage/error text and never copies the rejected argument value into
stderr.

The current fictional record can be checked with:

```console
python3 -m fisher_governance validate \
  --ledger data/source_ledger.example.jsonl \
  --format text
```

Its intended result is `schema_valid=true`, `collection_ready=false`, lifecycle
`BLOCKED`, and exit status `1`.

## Strict JSONL and operational limits

The input must resolve to a regular file. Directories, FIFOs, devices, and
symlinks resolving to a non-regular target are rejected before content is read;
the opened file descriptor is checked again to close the pathname race. Reads
remain bounded even if a regular file grows after either metadata check: binary
chunks are counted cumulatively, no more than `MAX_FILE_BYTES + 1` bytes are
read, and an overflow rejects the whole input before UTF-8 decoding or JSON
parsing. Only the captured byte sequence is then decoded and parsed. The content
is UTF-8 JSON Lines with exactly one object on every nonblank physical line.
Duplicate keys at any nesting level, non-finite JSON numbers, blank lines,
malformed JSON, non-object records, escaped surrogate code points,
bidirectional formatting controls, and C0 controls other than TAB/LF/CR are
errors. All documented keys are required and unknown keys are errors. JSON types
are exact, so a Boolean is not an integer.

| Bound | Limit |
| --- | ---: |
| File bytes | 512 MiB |
| Decoded characters per physical line | 1,000,000 |
| Source records | 10,000 |
| Object/list nesting depth | 32 |
| Members in an object/list | 10,000 |
| Count fields | 0 through 10,000,000 or `null` |
| Normal prose | 500 code points unless stated otherwise |
| Description/rationale/basis | 2,000 code points |

`schema_version` is exactly `1.0.0`. A `source_id` fully matches
`src_[a-z0-9][a-z0-9_-]{0,62}`. Parent references use the same syntax. Other
opaque policy/family/batch/model identifiers are ASCII and fully match
`[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}`. These operational identifier constraints
prevent raw prose, contact routes, or reversible values from being smuggled into
opaque fields; they do not prove that an identifier is nonidentifying.

SHA-256 values contain exactly 64 lowercase hexadecimal characters. Artifact
hash algorithm and value are either both `null` or exactly `SHA-256` plus its
digest. Dates are real canonical `YYYY-MM-DD` values. Timestamps are timezone-
aware RFC 3339 values and `updated_at` cannot precede `created_at`.

## Artifact safety and official evidence references

All decoded keys and string values are scanned without echoing the matching
value. Separators such as underscore do not create a bypass. The scanner rejects
HTTP/HTTPS/FTP/`www` routes, `mailto`, email, bare domains including Unicode-dot
variants, valid bare IPv4 addresses, 10–15-digit phone forms, and high-confidence
credential/OTP/PIN/password assignments.
Reserved `.example`, `.invalid`, and `.test` hosts and defanged `[.]` forms are
allowed for synthetic evidence.

Two exact fields are narrowly allowlisted because the frozen source protocol
requires authoritative evidence locators:

- `origin.landing_page`;
- `license.text_url`.

When non-null, each uses the deliberately conservative stable locator syntax:
lowercase `https://`, an ASCII DNS hostname with valid 1–63-character labels,
optional standard port `443`, and an optional ASCII path containing only the
unescaped characters `[A-Za-z0-9._~/-]`. User information, numeric IP hosts,
invalid DNS labels, nonstandard ports, queries, fragments, backslashes, percent
escapes, path dot-segments, non-ASCII characters, invalid punycode A-labels, and
bidirectional controls are rejected. Secret, phone, and IP scanning also applies
inside these fields before URL validation.
The validator never opens, fetches, resolves, or echoes a locator. Syntax cannot
prove that a page is official, complete, safe, preserved, or adequate license
evidence; those remain human gates.

## Source record

Every source object contains exactly these top-level keys:

`schema_version`, `source_id`, `source_name`, `description`,
`provenance_class`, `authenticity`, `lifecycle_status`, `blockers`, `origin`,
`artifact_hash`, `expected_record_count`, `audited_record_count`,
`language_scope`, `content_scope`, `authorization`, `consent`, `ethics`,
`license`, `release_tier`, `privacy_review`, `safety_review`, `quality_audits`,
`lineage`, `equivalence_policy`, `partition_eligibility`, `llm_fraction_scope`,
`steward`, `created_at`, `updated_at`, and `decision_notes`.

The four provenance classes and their required authenticity values are:

| `provenance_class` | `authenticity` |
| --- | --- |
| `TESTER_DONATED_AUTHENTIC` | `AUTHENTIC` |
| `TESTER_AUTHORED_SIMULATION` | `SIMULATED` |
| `PUBLIC_AUTHENTIC_AUXILIARY` | `AUTHENTIC` |
| `LLM_DRAFTED_HUMAN_EDITED` | `LLM_ASSISTED` |

Lifecycle is one of `PROPOSED`, `BLOCKED`, `AUTHORIZED`, `INGESTED`,
`REJECTED`, `WITHDRAWN`. `blockers` is a unique list of bounded nonempty
strings. An active (`AUTHORIZED`/`INGESTED`) source has no blocker and at least
one partition eligibility. Every other lifecycle has no projected partition and
retains a blocker or terminal reason. Rejection must agree with rejected
authorization; tester withdrawal must agree with withdrawn consent.

`language_scope` is a nonempty unique subset of `HINDI_DOMINANT`,
`TAMIL_DOMINANT`, `TELUGU_DOMINANT`, and `EN_INDIC_CODE_MIXED`. `content_scope`
is a nonempty unique subset of `MESSAGE_TEXT`, `URL`, `DOMAIN`, `PHONE`, `UPI`,
`BANK`, `EMAIL`, `APP`, and `OTHER`, and Paper 1 requires `MESSAGE_TEXT`.

### Nested objects

Every nested object has an exact key set:

- `origin`: `publisher_or_creator`, `landing_page`, `artifact_version`,
  `accessed_at`;
- `artifact_hash`: `algorithm`, `value`;
- `authorization`: `status`, `reviewer`, `reviewed_at`, `basis`;
- `consent`: `required`, `status`, `document_version`,
  `consent_reference_policy`;
- `ethics`: `status`, `authority`, `identifier`, `effective_date`;
- `license`: `status`, `name_or_spdx`, `text_url`, `version`, `reviewer`,
  `reviewed_at`, `research_use`, `modification`, `redistribution`,
  `commercial_use`, `attribution_text`, `conflict_notes`;
- `privacy_review`: `status`, `deidentification`, `pii_scan`,
  `residual_risk_review`, `raw_storage_approval`, `reviewer`, `reviewed_at`;
- `safety_review`: `status`, `active_artifact_scan`, `defanging`,
  `credential_otp_scan`, `prohibited_identifier_scan`, `reviewer`,
  `reviewed_at`;
- `quality_audits`: `unicode_encoding`, `language_script`, `source_label`,
  `duplicate_near_duplicate`, `template_campaign`,
  `fisher_independent_reannotation`;
- `lineage`: `source_family_id`, `collection_batch_id`,
  `scenario_or_prompt_family_id`, `model_id`, `generation_batch_id`,
  `author_or_donor_batch_id`, `parent_source_ids`, `has_public_ancestor`,
  `has_llm_ancestor`;
- `equivalence_policy`: `required`, `opaque_token_policy_version`,
  `final_component_assignment_required`, `component_policy_version`,
  `key_custodian`, `key_rotation_policy`, `raw_values_or_keys_in_ledger`;
- `partition_eligibility`: the eight canonical Boolean partitions plus
  `rationale`.

The authorization vocabulary is `BLOCKED`, `APPROVED`, `REJECTED`; consent is
`NOT_STARTED`, `APPROVED`, `NOT_APPLICABLE`, `WITHDRAWN`; ethics is `UNKNOWN`,
`PENDING`, `APPROVED`, `EXEMPT`, `REJECTED`; license is `UNKNOWN`, `PENDING`,
`VERIFIED`, `INCOMPATIBLE`, `NOT_APPLICABLE`; and audit values are
`NOT_STARTED`, `PENDING`, `PASSED`, `FAILED`, `NOT_APPLICABLE`.

A completed decision requires its named reviewer and date where the schema has
those fields. An `APPROVED` consent requires non-null opaque document and
reference-policy versions. A completed ethics decision requires authority,
identifier, and effective date. A `VERIFIED` license requires identity, HTTPS
text locator, version, reviewer/date, and all four permission flags.
`NOT_APPLICABLE` license status requires a nonempty consent/contract basis and,
for an active source, reviewer/date.

Every decision note begins with exactly `OBSERVED:`, `DERIVED:`, `ASSUMED:`, or
`UNKNOWN:` followed by a nonempty statement. Contents remain bounded and cannot
contain a live route or secret-like value.

## Active-source authorization checks

An `AUTHORIZED` or `INGESTED` record is mechanically authorization-ready only
when all representable gates agree:

- authorization is `APPROVED`; ethics is `APPROVED` or `EXEMPT`;
- tester consent is required and `APPROVED`;
- license is `VERIFIED` or justified `NOT_APPLICABLE`, and release tier is known;
- every active source governed by `VERIFIED` license evidence has affirmative
  `research_use` permission;
- artifact version, acquisition time, and SHA-256 are present;
- privacy and safety reviews are `PASSED`, with every subcheck `PASSED` or
  `NOT_APPLICABLE`, reviewer, and timestamp;
- every quality audit is `PASSED` or `NOT_APPLICABLE`;
- steward, required equivalence-policy references, source-family, and
  collection-batch references are present;
- donation has a donor-batch reference; simulation also has scenario and author
  references; LLM-assisted material has prompt family, model, generation batch,
  and human-editor batch references;
- a public source has an HTTPS landing-page reference, `VERIFIED` license, and
  passed Fisher independent-reannotation audit; and
- `PUBLIC_TEXT`, `DEIDENTIFIED_TEXT`, and `DERIVED_ONLY` require affirmative
  redistribution under a verified license; `DEIDENTIFIED_TEXT` and
  `DERIVED_ONLY` additionally require affirmative modification. `PUBLIC_TEXT`
  alone does not assert that the source text was modified.

These checks validate reference completeness and consistency, not the truth of
the evidence.

## Lineage and partition policy

All parent source IDs must resolve within the supplied ledger. Self-links,
duplicates, missing parents, and directed cycles are errors. A deterministic
iterative topological pass computes transitive public/LLM ancestry in `O(V+E)`
graph work, so a valid chain up to the record bound does not depend on Python's
recursion limit. Every record belonging to or downstream of a cycle fails
because its ancestry cannot be resolved. Missing-parent uncertainty propagates
to all descendants. For resolved sources, stored `has_public_ancestor` and
`has_llm_ancestor` flags must match. A direct source is not its own ancestor;
direct provenance is combined with computed ancestry for policy checks.

An active child is machine-authorization-ready only if every reachable parent is
also active and mechanically authorization-ready. A `PROPOSED`, `BLOCKED`,
`REJECTED`, `WITHDRAWN`, missing, cyclic, or mechanically invalid ancestor blocks
that child and every active descendant. The current schema defines no historical
detachment, retained-derivative, or withdrawn-ancestor exception. Such an
exception would require a separately versioned policy and schema rather than an
implicit bypass.

The only partitions are `pilot`, `unassigned`, `development`,
`probability_calibration`, `safety_threshold`, `primary_test`, `external_test`,
and `excluded`.

- Direct/derived public lineage may declare only `development` and/or
  `external_test`.
- Direct/derived LLM lineage cannot declare `probability_calibration`,
  `safety_threshold`, or `primary_test` and must use
  `COUNTS_TOWARD_DEVELOPMENT_AND_PILOT_CAPS`.
- All other lineage uses LLM scope `NOT_APPLICABLE`.
- `primary_test` requires tester-donated authentic or tester-authored simulation
  provenance and no public or LLM ancestry.

The validator cannot calculate the 30% development/pilot LLM caps from source
eligibility because the denominator is retained items, not sources. The dataset
validator remains authoritative for item-level transitive ancestry, partitions,
components, and the measured caps.

## Machine versus human readiness

The JSON report contains the following explicit `UNKNOWN` gates. This list makes
known evidence limits visible; it is not a claim that all possible human or legal
questions are exhaustively enumerated:

- ethics-authority truth;
- data controller/accountable institution;
- secure storage, jurisdiction, backup, and access controls;
- consent-material quality, language, voluntariness, and adult eligibility;
- retention, deletion, backup expiry, and deletion evidence;
- withdrawal cutoff, mapping, and operational removal controls;
- incident contact, secure channel, procedure, and synthetic drill;
- native-reviewer qualifications, coverage audit, and sign-off;
- annotator compensation, workload, welfare, and conflicts;
- equivalence-key secret management;
- license rights and official-source truth;
- privacy/safety review truth and two-person quality;
- append-only history and hash immutability across snapshots;
- the separate component-aware structured-state coverage manifest;
- real-world provenance and lineage completeness;
- whether an artifact hash actually binds the claimed artifact and version;
- measured source-count and acquisition-time truth;
- reviewer/steward identity, qualification, independence, and authority;
- whether opaque identifiers are truly nonidentifying and scope-limited; and
- material human editing of every retained LLM draft.

Some are `REFERENCE_ONLY`: the ledger can require a status or opaque reference
but cannot authenticate it. Others are `NOT_REPRESENTED`: the frozen record has
no structured field from which a machine could decide. Adding a new manifest or
turning prose blocker strings into approvals would create policy, so v1.0 does
neither. A later executable human-governance package requires a separately
frozen schema, authority roles, evidence-reference rules, signatures or
attestation model, lifecycle, and compatibility version.

## Compatibility and non-claims

- This validator consumes the full governance ledger. It does not consume or
  replace `sources.jsonl` from the Phase-0 dataset contract.
- Passing it does not validate items, annotations, registry contents, structured
  coverage, pilot arithmetic, human safety audit, corpus-final gates, or model
  results.
- Official evidence URLs are parsed only. No network operation occurs.
- A shape-valid LLM source remains `HUMAN_REVIEW_REQUIRED`; its prompt/model/
  editor-batch references do not prove material human editing.
- A single snapshot cannot prove historical immutability.
- Sanitized diagnostics contain only fixed messages, generated line numbers,
  contract-owned field paths, and source IDs that passed the safe syntax. They
  never quote an unknown key, source description, URL, blocker, reviewer, or
  other untrusted value.
- The safe fixture under `examples/governance/` is fictional and blocked. It is
  not evidence of approval and grants no permission to collect data.
