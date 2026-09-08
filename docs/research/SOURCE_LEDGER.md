# Fisher Source and License Ledger

Status: **DRAFT — BLOCKED FOR COLLECTION**

Version: `0.2-draft`

The source ledger is the machine-readable authorization and provenance register for every source considered by Fisher. A citation or downloadable file is not sufficient authorization. One JSON object per line is stored as JSONL. The single record in [`data/source_ledger.example.jsonl`](../../data/source_ledger.example.jsonl) is a fictional schema example, not collected data and not approval to collect.

The ledger must align with the [machine data contract](../DATA_CONTRACT.md). No source may be ingested until the executable mechanical projection passes and the ethics/privacy package and designated human reviewers authorize the same ledger version. The current global status is blocked because the named approvals and operational fields in [Consent, Ethics, and Privacy](CONSENT_ETHICS_PRIVACY.md) are `UNKNOWN`.

This document and `data/source_ledger.example.jsonl` define the full pre-authorization governance ledger. The dataset snapshot at `examples/pilot/sources.jsonl`, when created, is a strict ingestion projection containing only contract-approved source fields and linking back by `source_id`. Its dataset validator does not validate or replace this full governance ledger. A source must pass both the governance authorization process and the separate dataset-snapshot contract before any row is eligible for ingestion.

**OBSERVED:** executable checkpoint `E09` independently passed only the scoped
schema-`1.2.0` syntactic VMP repair. Later `E10` passed the original semantic
repair but failed four new engine-specification boundaries. `E11` then passed
that second repair but failed five later provider-execution/run-envelope,
endpoint-numeric, E0-feature, evaluation-universe, and coordinate-predicate
boundaries. None of these checkpoints authorizes a source, proves artifact
authenticity, or changes this ledger's separate schema version. `E12` finds five
additional engine status-union, control-mask, evaluation-binding,
system-provenance/five-seed, and candidate-numeric blockers. `E13` passes those
fifth-repair surfaces but finds three preflight/run-union and metric-input/
counting blocker groups. `E14` passes those repairs and the other major contracts
but finds three engine-descriptor/parser, eligibility-accounting, and metric-
universe/denominator/algebra groups. `E15` passes those repairs and the
previously reviewed surfaces but finds three remaining strict universe-input
parser/count, structural-versus-semantic precedence, and nonempty-denominator
groups. `P0` and collection remain blocked pending fresh independent replay of
the eighth local, universe-only docs repair and every named human
gate.

The executable governance-ledger mechanical projection now exists and validates the existing full source-ledger schema; see the [governance contract](../GOVERNANCE_CONTRACT.md) and [safe blocked CLI example](../../examples/governance/README.md). Independent adversarial replay passed for the pinned 19 August 2026 implementation after the reported rights, scanner, URL, lineage, CLI, special-file, and growing-file defects were repaired. It still always fails `collection_ready` closed because 20 human or unrepresented governance gates remain `UNKNOWN`. A passing `schema_valid` result, or even machine authorization readiness, is never ethics, legal, safety, or collection authorization. No source is authorized until both mechanical validation and the named human-governance reviews pass. The future `corpus-final` validator is a separate mandatory gate before the 6,000-item corpus is frozen or evaluated and remains unimplemented.

The governance display classes project to exact dataset-contract values as follows: `TESTER_DONATED_AUTHENTIC` → `tester_donated_authentic`; `TESTER_AUTHORED_SIMULATION` → `tester_authored_simulation`; `PUBLIC_AUTHENTIC_AUXILIARY` → `public_authentic`; and `LLM_DRAFTED_HUMAN_EDITED` → `llm_drafted_human_edited`. This full governance ledger uses its own schema version `1.0.0`; the separate [machine data contract](../DATA_CONTRACT.md) is authoritative for current dataset-snapshot schema `1.2.0`. The shared `source_id` projection must satisfy both contracts, and a mismatch blocks use until the governance ledger and dataset projection are reconciled together. Mapping public authentic data to `public_authentic` never grants eligibility outside `development`/`external_test`.

## 1. Provenance classes

Every source has exactly one `provenance_class`:

- `TESTER_DONATED_AUTHENTIC`: real messages donated by consenting adults after authorization, safety processing, and de-identification;
- `TESTER_AUTHORED_SIMULATION`: fictional messages written by consenting adults from approved safe scenarios;
- `PUBLIC_AUTHENTIC_AUXILIARY`: public authentic material with verified rights and audits, restricted with all descendants to `development` or `external_test` only;
- `LLM_DRAFTED_HUMAN_EDITED`: model-drafted, materially human-edited synthetic text; the model never creates a gold label.

These classes are never collapsed into a generic `synthetic` or `real` flag. Authenticity, legal authorization, redistribution, and Fisher label quality are distinct fields.

Provenance, original source labels, authoring scenario, prompt target, author intent, and generation method are governance metadata. They are hidden from semantic annotators and adjudicators and cannot justify the primary label, facets, spans, or evidence. Gold is derived only from the schema-1.2 VMP—exactly `item.text` plus non-gold pre-annotation `item.visible_artifacts`, bound by `item.vmp_sha256`; annotations never construct it. Unresolved visible intent remains `UNCERTAIN` and `excluded`.

## 2. Required JSONL structure

All keys listed here are required. Use JSON `null` only where this schema permits `UNKNOWN`; add a corresponding blocker or note. Empty strings are invalid substitutes for unknown values.

### 2.1 Identity and status

| Key | Type / allowed values | Meaning |
|---|---|---|
| `schema_version` | string | Governance-ledger schema version, currently `1.0.0`; it is distinct from current dataset-snapshot schema `1.2.0`. |
| `source_id` | string | Random, nonidentifying, stable source identifier. |
| `source_name` | string | Human-readable name; must not expose a participant. |
| `description` | string | Scope and origin without raw message text or identifiers. |
| `provenance_class` | enum | One of the four classes in Section 1. |
| `authenticity` | `AUTHENTIC`, `SIMULATED`, `LLM_ASSISTED` | What kind of evidence the source represents. |
| `lifecycle_status` | `PROPOSED`, `BLOCKED`, `AUTHORIZED`, `INGESTED`, `REJECTED`, `WITHDRAWN` | Current source state. `AUTHORIZED` requires all gates. |
| `blockers` | array of strings | Unresolved approvals or checks; empty only when authorization is supported. |

### 2.2 Origin, access, and integrity

| Key | Type / allowed values | Meaning |
|---|---|---|
| `origin` | object | `publisher_or_creator`, authoritative `landing_page`, exact `artifact_version`, and `accessed_at`. Participant identity is never included. |
| `artifact_hash` | object | `algorithm` and `value` for the exact acquired artifact, or both `null` before an artifact exists. Never hash a participant identifier here. |
| `expected_record_count` | integer or `null` | Preregistered/claimed count before audit. |
| `audited_record_count` | integer or `null` | Count measured from the exact hashed artifact after audit. |
| `language_scope` | array | Expected Fisher strata or language pairs; observed distribution is recorded by later audit, not guessed here. |
| `content_scope` | array | `MESSAGE_TEXT` and/or approved textual destination-artifact types. |

### 2.3 Authorization, consent, and ethics

| Key | Type / allowed values | Meaning |
|---|---|---|
| `authorization` | object | `status` (`BLOCKED`, `APPROVED`, `REJECTED`), named `reviewer` or `null`, `reviewed_at` or `null`, and `basis`. |
| `consent` | object | `required` boolean, `status` (`NOT_STARTED`, `APPROVED`, `NOT_APPLICABLE`, `WITHDRAWN`), opaque `document_version`, and opaque `consent_reference_policy`. Never store a signed form or identity. |
| `ethics` | object | `status` (`UNKNOWN`, `PENDING`, `APPROVED`, `EXEMPT`, `REJECTED`), authority, identifier, and effective date. Unknown values are `null` and block collection. |

For a public source, `consent.required` may be false, but ethics/privacy and license review still apply. For tester sources, consent is mandatory. An ethics exemption must be an authentic written determination, not a project self-assessment.

### 2.4 License and redistribution

| Key | Type / allowed values | Meaning |
|---|---|---|
| `license` | object | `status` (`UNKNOWN`, `PENDING`, `VERIFIED`, `INCOMPATIBLE`, `NOT_APPLICABLE`), SPDX/name, exact text URL, version, reviewer, review date, permitted research use, modification, redistribution, commercial-use flags, attribution text, and conflict notes. |
| `release_tier` | `NO_RELEASE`, `AGGREGATES_ONLY`, `DERIVED_ONLY`, `DEIDENTIFIED_TEXT`, `PUBLIC_TEXT`, `UNKNOWN` | Maximum approved release form. |

`NOT_APPLICABLE` license status is allowed only when consent/contract supplies the relevant authorization and a reviewer explains the basis. `UNKNOWN` release tier blocks redistribution.

### 2.5 Privacy, safety, and quality audits

| Key | Type / allowed values | Meaning |
|---|---|---|
| `privacy_review` | object | Status plus de-identification, PII scan, residual-risk review, raw-storage approval, reviewer, and date. |
| `safety_review` | object | Status plus active-artifact scan, defanging, credential/OTP scan, prohibited-identifier scan, reviewer, and date. |
| `quality_audits` | object | Status of Unicode/encoding, language/script, source-label, duplicate/near-duplicate, template/campaign, and Fisher independent-reannotation audits. |

Each audit status is `NOT_STARTED`, `PENDING`, `PASSED`, `FAILED`, or `NOT_APPLICABLE`. A source cannot be `AUTHORIZED` if an applicable audit is incomplete or failed.

A high-confidence active URL/domain, live email or phone route, credential/OTP, or prohibited identifier finding is a quarantine failure, not a warning. Human review remains mandatory because automated detectors cannot establish that a source is safe merely by finding nothing.

The language/script audit must account for every maximal Unicode Letter/Mark token. Destination, brand, acronym, and name tokens may receive contextual language `other`, but no token may be omitted from the language denominator. This prevents source-specific or reviewer-specific denominator manipulation.

### 2.6 Lineage, grouping, and partition eligibility

| Key | Type / allowed values | Meaning |
|---|---|---|
| `lineage` | object | Opaque source-family, collection-batch, scenario/prompt-family, model/generation-batch, author/donor-batch, parent-source references, and booleans `has_public_ancestor` and `has_llm_ancestor`. Ancestry is transitive, not only immediate. |
| `equivalence_policy` | object | Whether restricted linkage is required, the approved opaque-token policy/version, and final-component-assignment policy/version; never includes raw artifacts, mappings, or keys. |
| `partition_eligibility` | object | Booleans for `pilot`, `unassigned`, `development`, `probability_calibration`, `safety_threshold`, `primary_test`, `external_test`, and `excluded`, plus rationale. After full authorization, only approved true values project into snapshot `eligible_partitions`; a blocked record projects nothing. |
| `llm_fraction_scope` | string | `COUNTS_TOWARD_DEVELOPMENT_AND_PILOT_CAPS` for direct or derived LLM lineage; otherwise `NOT_APPLICABLE`. |

The projection uses the same eight canonical partitions. Restricted preprocessing computes transitive closure over every approved opaque equivalence and lineage key, then assigns final item `leakage_component_id`. All related rows remain in one component and partition. Components in `probability_calibration`, `safety_threshold`, and `primary_test` must be singleton and one-stratum.

Public-authentic sources and any source/item with public ancestry may set only `development` and/or `external_test` true; every other partition is false. Direct or derived LLM lineage sets `probability_calibration`, `safety_threshold`, and `primary_test` false and counts toward both independent caps: at most 30% of retained `development` and at most 30% of retained `pilot`. The primary test permits only tester-donated authentic and tester-authored simulation provenance, with results reported separately; donation-versus-simulation composition is also reported for probability calibration and safety threshold. The paper gate requires authentic donations to constitute at least 50% of each primary-test label × stratum cell: at least 125/250 phishing and 150/300 benign items per stratum. This gate routes claims and does not itself authorize collection.

### 2.7 Accountability

| Key | Type / allowed values | Meaning |
|---|---|---|
| `steward` | string or `null` | Approved accountable role/person; `null` blocks authorization. |
| `created_at` | RFC 3339 string | Ledger-record creation time. |
| `updated_at` | RFC 3339 string | Last substantive update time. |
| `decision_notes` | array of strings | Evidence-labeled decisions and limitations; no raw content. |

## 3. Cross-field authorization rules

A validator must reject `AUTHORIZED` or `INGESTED` when any of these conditions holds:

- an applicable consent, ethics, authorization, license/contract, privacy, safety, or quality gate is not approved/passed;
- the artifact exists but its cryptographic hash or exact version is absent;
- reviewer and review date are absent for a completed review;
- tester data lacks approved consent or contains participant identity in the ledger;
- public-authentic or public-derived lineage is eligible for any partition other than development or external test;
- direct or derived LLM lineage is eligible for probability calibration, safety threshold, or primary test, or is not counted toward both the 30% development cap and 30% retained-pilot cap;
- a primary-test source is not tester-donated authentic or tester-authored simulation;
- an LLM is represented as the gold-label source;
- raw artifact, participant identity, secret, key, or reversible mapping appears in the ledger;
- `release_tier` exceeds verified consent/license/contract permissions;
- `blockers` is nonempty;
- global protocol blockers remain unresolved.

Authorization does not guarantee row-level acceptance. Every item must still pass the aligned message contract, annotation guide, de-identification, grouping, and partition checks.

## 4. Source-specific requirements

### 4.1 Tester-donated authentic

Require adult consent for donation and exact release tier, separate opaque consent references, approved raw storage, two-person de-identification/safety review, and withdrawal linkage held outside the corpus. Never place identity or raw sender/destination values in the ledger.

### 4.2 Tester-authored simulation

Require adult authorship consent, approved fictional scenarios, safe reserved artifacts, opaque author/scenario/batch lineage, and permanent simulation marking. Tester-authored simulation may be primary-test eligible after all gates, but it must be reported separately from authentic donation and its hidden scenario may never justify gold; the example remains blocked and grants no authorization.

### 4.3 Public authentic auxiliary

Require authoritative license evidence, exact artifact/version/hash, privacy and safety audits, original-label preservation as hidden metadata, independent Fisher reannotation from model-visible content only, and connected-component grouping. It and all derived descendants are eligible only for development or external test.

### 4.4 LLM-drafted, human-edited

Require provider/model/version or an explained reproducibility limitation, generation and prompt-family lineage, human editor, material-edit confirmation, and independent human labels based only on model-visible content. It and all derived descendants count toward the separate 30% retained-development and 30% retained-pilot caps and have no probability-calibration, safety-threshold, or primary-test eligibility.

## 5. Review workflow

1. Create a `PROPOSED` ledger record without acquiring content.
2. Review authority, consent/contract, ethics, license/terms, privacy, and safety requirements.
3. If authorized to acquire, record exact artifact/version/hash inside the restricted workflow.
4. Run and record all required audits; do not overwrite failures.
5. Resolve blockers and obtain named, dated reviews.
6. Mark `AUTHORIZED` only when the dedicated full governance-ledger validator and human review both pass.
7. Ingest into quarantine, validate rows, de-identify, and compute final leakage components.
8. Before blind release, freeze and natively audit the separate component-aware structured-state coverage manifest using only model-visible content and the approved frozen registry. Coverage tags are non-gold, hidden from semantic annotators/adjudicators, and are not stored as source authorization facts in this ledger.
9. Independently annotate every released attempt under the frozen candidate/reserve order; do not remove an attempted item for disagreement or an incorrect candidate tag.
10. Update counts and status without deleting history; withdrawal or rejection preserves a reason but no prohibited content.

All substantive corrections are append-traceable. A later record version must say what changed, why, who approved it, and when.

## 6. Example limitations

The example JSONL record is intentionally `BLOCKED` and describes one fictional tester-authored simulation source using a reserved `.example` domain. It contains no real participant, message, consent, license, source artifact, or approval. Its null ethics, stewardship, storage, retention, withdrawal, and equivalence-key fields demonstrate blockers; they are not defaults to use in collection.

Validation of syntax alone does not authorize the record. Collection remains **BLOCKED** until the protocol, contract, validator, and named reviewers approve it.
