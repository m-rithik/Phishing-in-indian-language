# Fisher 240-item pilot: Collection-to-Quarantine packet

Status: **BLOCKED**

This tracked packet is an immutable `BLOCKED`/`UNKNOWN` template and the
operational stop/go boundary for the 240-item feasibility pilot. It permits no
recruitment, submission, or collection until the approved external system
contains authentic decisions and accountable dated sign-off bound to the exact
approved policy hashes. Durable original/raw message storage is prohibited in
every state. Do not fill this file with real decisions, names, dates,
signatures, references, hashes, storage paths, contact routes, or signed
evidence. The filled and signed instance exists only in the approved external
system. Any later Git projection requires separate privacy and release review,
must be content-free, and remains nonauthoritative.

Repository text, a validator result, a changed placeholder, or an owner
assertion cannot change this template's status or authorize collection.

This packet complements the [pilot v0.1.0 contract](PILOT_V01.md),
[Consent, Ethics, and Privacy protocol](CONSENT_ETHICS_PRIVACY.md),
[governance contract](../GOVERNANCE_CONTRACT.md), and
[threat model](THREAT_MODEL.md). When they differ, the stricter stop condition
applies.

## 1. Three separate state machines

These state machines are independent and must never be collapsed into one
family/batch progression. Only the filled, signed external instance can advance
the intake control plane or a family disposition. This tracked template never
advances any state.

### A. Intake control plane

The control plane applies only to one exact batch, collection window, and
protocol version.

| State | Effect |
|---|---|
| `BLOCKED` | Current state. Synthetic design, synthetic tests, and external approval preparation only; no real recruitment, message submission, collection, or raw persistence. |
| `APPROVED` | The external SG1 decision `COLLECTION_TO_QUARANTINE_APPROVED` has satisfied section 7 for the exact scope. Approved recruitment and consent-vault activity may begin. After valid consent, text may enter the ephemeral pre-persistence intake boundary; only approved de-identified/defanged text may be written to restricted quarantine. This does not approve later processing, annotation, aggregate readiness, or release. |
| `SUSPENDED` | Global kill state. It overrides `APPROVED` and makes recruitment, message submission, and persistence unavailable across the scoped intake. Refusal, withdrawal, incident response, and deletion duties continue in the external systems. |

Approval expiry or revocation, a systemic incident, integrity failure, or
policy/evidence mismatch sets `SUSPENDED` under the approved external process.
Neither family disposition nor pilot readiness can override it.

### B. Per-family disposition

Each submitted family has its own authoritative disposition. There is no batch
promotion state and one family's disposition cannot advance another family.

| State | Effect |
|---|---|
| `QUARANTINED` | Only approved de-identified/defanged text is durably isolated for two-person restricted review. Original message bytes were not persisted. No later processing or annotation is permitted. |
| `PREPROCESSING_APPROVED` | The family-specific quarantine review and section 7 checks permit restricted source reconciliation, component closure, and pilot-item preparation using only the approved transformed text. |
| `ANNOTATION_APPROVED` | The approved de-identified/defanged family may enter separated blind annotation after the pilot-specific requirements in section 7 pass. |
| `REJECTED` | Terminal and tombstoned. No processing, annotation, restoration, reingestion, or later promotion. |
| `WITHDRAWN` | Terminal and tombstoned across descendants, queues, caches, exports, and restoration paths. It never becomes `QUARANTINED`, `PREPROCESSING_APPROVED`, or `ANNOTATION_APPROVED` again. |

A systemic incident changes the intake control plane to `SUSPENDED`; it does not
rewrite terminal family dispositions. Active affected families remain isolated
or are rejected under the approved external incident process.

### C. Aggregate batch readiness

Aggregate readiness has only `NOT_READY` and `PILOT_READY`. It is derived only
from the 240-item v0.1 validator: `PILOT_READY` means the ready-mode gates and
component-fold dry run passed. It is never collection authority, a family
disposition, model evaluation, phishing-performance evidence, corpus-expansion
authority, or release authority.

## 2. Accountable roles

SG1 requires qualified holders only for these roles: research lead;
ethics/privacy authority; data controller; intake/data steward; independent
de-identification/privacy reviewers; key custodian; and security/incident lead.
No principal may perform more than one of these functions for the same family:
submission or intake, de-identification, independent review, or promotion. No
role-combination waiver may bypass this family-level separation.

An annotation lead and qualified native-language reviewers become required only
for the later per-family `ANNOTATION_APPROVED` transition. Model-development,
protected-set, statistical, IP/rights, registry, structured-state,
transliteration-resource, and release roles are outside this pilot's SG1 and are
governed when their later activity is proposed.

Names, signatures, signed forms, contact routes, credentials, secret keys, real
dates, evidence references, hashes, storage paths, decisions, and evidence
documents remain only in the approved external system. This Git template never
records a filled sign-off.

## 3. SG1 unresolved decisions and sign-off register

All 13 fields are mandatory blockers. The repository placeholders are permanent
and must not be replaced. Only the filled, signed external instance may supply
the authentic dated decisions and set the scoped intake control plane to
`APPROVED` through its `COLLECTION_TO_QUARANTINE_APPROVED` decision.

| # | Required decision field | Accountable SG1 role(s) | Repository state | Repository date | Repository evidence ref | Repository evidence/policy hash |
|---:|---|---|---|---|---|---|
| 1 | Ethics authority or institutional review body | Ethics/privacy authority | `EXTERNAL ONLY — UNKNOWN` | `EXTERNAL ONLY — UNKNOWN` | `EXTERNAL ONLY — UNKNOWN` | `EXTERNAL ONLY — UNKNOWN` |
| 2 | Ethics approval/exemption identifier and date | Ethics/privacy authority | `EXTERNAL ONLY — UNKNOWN` | `EXTERNAL ONLY — UNKNOWN` | `EXTERNAL ONLY — UNKNOWN` | `EXTERNAL ONLY — UNKNOWN` |
| 3 | Data controller / accountable institution | Data controller; research lead | `EXTERNAL ONLY — UNKNOWN` | `EXTERNAL ONLY — UNKNOWN` | `EXTERNAL ONLY — UNKNOWN` | `EXTERNAL ONLY — UNKNOWN` |
| 4 | Secure raw-data storage location and jurisdiction | Data controller; security/incident lead | `EXTERNAL ONLY — UNKNOWN` | `EXTERNAL ONLY — UNKNOWN` | `EXTERNAL ONLY — UNKNOWN` | `EXTERNAL ONLY — UNKNOWN` |
| 5 | Data steward | Data controller; intake/data steward | `EXTERNAL ONLY — UNKNOWN` | `EXTERNAL ONLY — UNKNOWN` | `EXTERNAL ONLY — UNKNOWN` | `EXTERNAL ONLY — UNKNOWN` |
| 6 | Equivalence-key custodian and storage | Key custodian; security/incident lead | `EXTERNAL ONLY — UNKNOWN` | `EXTERNAL ONLY — UNKNOWN` | `EXTERNAL ONLY — UNKNOWN` | `EXTERNAL ONLY — UNKNOWN` |
| 7 | Equivalence-key rotation and destruction policy | Key custodian; security/incident lead | `EXTERNAL ONLY — UNKNOWN` | `EXTERNAL ONLY — UNKNOWN` | `EXTERNAL ONLY — UNKNOWN` | `EXTERNAL ONLY — UNKNOWN` |
| 8 | Incident and participant contact | Security/incident lead; intake/data steward | `EXTERNAL ONLY — UNKNOWN` | `EXTERNAL ONLY — UNKNOWN` | `EXTERNAL ONLY — UNKNOWN` | `EXTERNAL ONLY — UNKNOWN` |
| 9 | Raw and de-identified retention periods | Data controller; intake/data steward | `EXTERNAL ONLY — UNKNOWN` | `EXTERNAL ONLY — UNKNOWN` | `EXTERNAL ONLY — UNKNOWN` | `EXTERNAL ONLY — UNKNOWN` |
| 10 | Withdrawal cutoff | Ethics/privacy authority; intake/data steward | `EXTERNAL ONLY — UNKNOWN` | `EXTERNAL ONLY — UNKNOWN` | `EXTERNAL ONLY — UNKNOWN` | `EXTERNAL ONLY — UNKNOWN` |
| 11 | Approved participant information and consent text | Ethics/privacy authority; research lead | `EXTERNAL ONLY — UNKNOWN` | `EXTERNAL ONLY — UNKNOWN` | `EXTERNAL ONLY — UNKNOWN` | `EXTERNAL ONLY — UNKNOWN` |
| 12 | Compensation, workload, and annotator-welfare plan | Ethics/privacy authority; research lead | `EXTERNAL ONLY — UNKNOWN` | `EXTERNAL ONLY — UNKNOWN` | `EXTERNAL ONLY — UNKNOWN` | `EXTERNAL ONLY — UNKNOWN` |
| 13 | Redistribution policy for authentic donations | Data controller; research lead | `EXTERNAL ONLY — UNKNOWN` | `EXTERNAL ONLY — UNKNOWN` | `EXTERNAL ONLY — UNKNOWN` | `EXTERNAL ONLY — UNKNOWN` |

The external package must also state attestation authority, decision scope,
policy version, effective and expiry/review dates, revocation method, and the
exact batch/protocol it covers. Those semantics are not yet frozen, so SG1
remains blocked. The authority must explicitly approve the zero-durable-raw
design, its transient execution environment, and raw retention of zero; the
raw-storage and retention decisions must not be silently marked not applicable.

## 4. Data zones and promotion boundary

| Zone | Permitted contents and roles | Prohibited flow |
|---|---|---|
| External recruitment/consent vault | Before any message submission, the approved external system may hold only the minimum contact and eligibility data, participant notice/version, consent or refusal state, withdrawal mapping, and approved operational evidence. Access, retention, deletion, and pre-consent opt-out are separately controlled. | No message text, attachment, message metadata, corpus ID, Git/chat/ticket copy, research access, or inferred consent. |
| Ephemeral pre-persistence intake boundary | After valid activity/tier consent, a memory/stream-only process accepts text only, performs fail-closed de-identification, defanging, Unicode/privacy/credential safety scanning, and assigns a random immutable version ID. | No attachments; no durable original bytes, raw digest, temporary file, log, telemetry, cache, crash/core dump, swap/pagefile capture, backup, preview, linkification, network resolution, external LLM call, or equality-query interface. |
| Restricted quarantine | Only approved de-identified/defanged text, a random immutable version ID, minimum source/component metadata, and content-free findings needed for two-person independent review. | No original text, raw-byte digest, identity/consent data, key, reversible mapping, analyst/annotator access, or promotion after disagreement. |
| Restricted pilot preprocessing | After `PREPROCESSING_APPROVED` and AC-10 pass, authorized source reconciliation, component closure, opaque ID assignment, optional approved scoped keyed-HMAC binding, and v0.1 item preparation using only the approved transformed text. | No original bytes, key/mapping export, analyst-selected grouping, arbitrary equality query, or family merging after review. |
| Research | Immutable approved de-identified/defanged model-visible text, approved placeholders, opaque IDs, blind annotations, aggregate reports, and SHA-256 only of the approved transformed bytes. | No original text or raw digest, identity/consent mapping, key, reversible lookup, active route, hidden provenance/intent, or public text release. |

The ephemeral boundary terminally rejects a candidate with zero message
persistence if it detects any live route, OTP, password, PIN, account/card/UPI
value, phone number, direct identifier, attachment, or transformation it cannot
prove safe. A sanitized, content-free rejection disposition may be recorded
externally; the candidate message and raw digest may not be recorded anywhere.

Raw-byte SHA-256 values and other raw digests are content-derived and must never
be called content-free. Under this zero-durable-raw design they never leave the
ephemeral boundary or become durable. Intake cross-zone binding uses only a
random immutable version ID. A purpose-scoped keyed HMAC may be introduced in
restricted preprocessing only after AC-10 passes, with its key and interface
outside research access. No binding may equal the raw SHA-256 or expose
candidate-dictionary/equality probing. The research zone may hash only the
approved de-identified/defanged bytes required by v0.1.

If any downstream synthetic defense canary or later false negative reveals a
prohibited artifact, annotation stops and the affected family becomes terminal
`REJECTED` and tombstoned. A systemic failure also sets the intake control plane
to `SUSPENDED`.

## 5. Participant information, consent, and source authority

Recruitment starts only while the exact intake scope is `APPROVED`. Before
consent, the external vault may collect only minimum contact/eligibility data,
deliver the approved notice, and support refusal or opt-out; it accepts no
message bytes. Refusal and withdrawal are handled only in the external vault
under its approved retention/deletion process. A separate message-text input is
enabled only after affirmative consent is valid for the exact activity and tier.

The approved information sheet and affirmative activity-specific consent must,
in language the participant understands, explain:

- the research purpose and why multilingual/Romanized messages are sought;
- the exact activity: authentic donation, simulation authorship, annotation, or
  an approved combination;
- foreseeable scam-language or distressing-content exposure;
- what data/metadata are and are not collected, de-identification limits, and
  who can access each zone;
- the exact redistribution tier, compensation terms, retention periods,
  withdrawal cutoff, and complaint/incident/withdrawal process; and
- voluntariness, no penalty for refusal, and whether withdrawal affects payment.

Only adults aged 18 or older may participate. Consent must be affirmative,
versioned, separately recorded, and valid for the exact activity and release
tier; silence, prechecked boxes, employment/classroom participation, or platform
terms are insufficient. Authentic donors may submit only a standalone message
received by or belonging to them and must attest authority to share it.
Forwarded conversations, threads, attachments, or third-party material involving
nonconsenting private correspondents are rejected unless the external ethics
authority has approved a specific lawful workflow. Simulation prompts must be
fictional, non-targeted, and free of real-person data, live destinations, and
third-party contact instructions. Participant instructions require replacing
routes, numbers, account/credential values, and direct identifiers with approved
typed placeholders before submission. This is defense in depth: automated
intake remains fail closed and never trusts participant pre-redaction.

## 6. Required operational controls

- **Storage and access:** an externally approved transient intake environment
  with durable raw retention fixed at zero; approved jurisdiction and encryption
  for the vault and transformed-data zones; individual MFA accounts, least
  privilege, time-bounded grants, access logs, backup controls, revocation SLA,
  two-person break-glass, and task separation.
- **De-identification and safety:** text-only memory/stream intake; inert
  rendering; disabled previews, attachments, macros, scripts, linkification,
  network calls, and external LLM calls; fail-closed machine transformation and
  scanning before any durable write; then two independent reviews of only the
  transformed text. Any prohibited value or unsafe transformation causes
  terminal rejection with zero message persistence; reviewer disagreement keeps
  transformed text in restricted quarantine or rejects it.
- **Retention, withdrawal, and deletion:** externally approved raw retention of
  zero plus separate clocks for recruitment/consent, transformed text, mappings,
  logs, and backups; controlled withdrawal mapping; descendant/queue/cache/export
  closure; tombstones preventing reingestion; backup expiry/restoration tests;
  content-free deletion evidence; and no hold without separate approval.
- **Incident response:** approved secure notification path, stop/contain rules,
  lineage assessment, access/key revocation, authority/participant notification,
  repair, fresh scans, independent review, and externally witnessed synthetic
  drill before collection.
- **Reviewer welfare:** qualified language-matched adults, workload/exposure
  limits, breaks, opt-out without penalty, compensation, support, conflicts
  review, and escalation controlled outside the corpus.
- **Release:** no raw or consent material; no release inferred from pilot
  readiness; separate privacy, rights, ethics, security, IP, and release-owner
  approval for any aggregate, derived artifact, model, demonstration, or text.

Proposed compatibility mapping: pilot v0.1 `internal_only` maps to governance
`NO_RELEASE` for text. This proposal permits no public raw or de-identified text
and remains pending authentic external approval. It does not itself authorize
aggregate, feature, model, or paper release.

## 7. Synthetic security acceptance checks

Every check uses only synthetic, reserved, inert canaries. Current status is
`NOT RUN / FAIL`. A transition's listed checks must all be `PASS`, with zero
`UNRUN`, `FAIL`, or `INCONCLUSIVE` branches, and must be externally witnessed
and bound to the exact AC-suite, policy, and build hashes in the approved
external system. Partial, stale, mismatched, local-only, or machine-only
evidence fails the gate.

Governance `schema_valid=true` alone is insufficient. Before intake can become
`APPROVED`, exact-scope planned source records for the batch, window, and
protocol must be schema-valid and the filled, signed external SG1 instance must
issue `COLLECTION_TO_QUARANTINE_APPROVED`. At this pre-acquisition point the
artifact hash may be null and `machine_authorization_ready=true` cannot yet be
required because no approved transformed artifact exists. After transformed
text enters restricted quarantine, its source record must report
`machine_authorization_ready=true`, with no blocked, withdrawn, or invalid
ancestor, before that family can become `PREPROCESSING_APPROVED`.

Governance `collection_ready=false` remains expected because the validator
cannot authenticate external approvals. The repository's safe blocked fixture
cannot satisfy intake approval because it lacks the exact scope and signed
external evidence. Both mechanical checks are necessary and never sufficient.

| Transition | Required acceptance evidence |
|---|---|
| Intake `BLOCKED` → `APPROVED` through external `COLLECTION_TO_QUARANTINE_APPROVED` | AC-00, AC-01, AC-02, AC-03, AC-04-I, AC-05, AC-06, AC-07, AC-09, AC-11, AC-12, and AC-13 all pass with zero unrun or inconclusive subcheck branches, together with schema-valid exact-scope planned source records, signed external SG1, and explicit approval of the zero-durable-raw design, transient environment, and zero raw retention. |
| Family `QUARANTINED` → `PREPROCESSING_APPROVED` | Every intake-transition check remains current and hash-matched; the transformed artifact's source record is `machine_authorization_ready=true` with no blocked, withdrawn, or invalid ancestor; and AC-04-P and AC-10 additionally pass with zero unrun or inconclusive subcheck branches. Intake remains random-version-ID-only until AC-10 passes. |
| Family `PREPROCESSING_APPROVED` → `ANNOTATION_APPROVED` | Every earlier check remains current and hash-matched; AC-08 additionally passes. The pilot-specific eight-cell/240-item allocation and component plan are approved and frozen; the v0.1 annotation schema/version in `PILOT_V01.md` is frozen; qualified native-language reviewers sign off; and blinding, access separation, and the welfare plan are verified. |
| Aggregate `NOT_READY` → `PILOT_READY` | Only the 240-item v0.1 ready-mode validator derives this state. It inherits no collection, family-disposition, or release authority. |

The schema-1.2 registry, structured-state G2, and 1,200-item ontology are later
work and are out of scope for every v0.1 family or readiness transition.

No `N/A` or deferral is permitted unless an external authority records a scoped,
dated rationale under its approved process. No `N/A`, deferral, or rationale may
remove a check listed as required for that transition.

| ID | Acceptance check | Required passing outcome and evidence |
|---|---|---|
| `AC-00` | Authorization interlock | Removing or altering any approval keeps recruitment and message input unavailable before persistence. Evidence binds approvals to authorized identities, dates, exact policy hashes, the tested build, and the zero-durable-raw scope. |
| `AC-01` | Consent-before-data | Missing, expired, withdrawn, wrong-activity/tier, prechecked, non-adult, or unauthorized-third-party consent accepts zero message bytes and creates zero message or annotation records; only sanitized refusal evidence is retained in the external vault, with identity/evidence separate. |
| `AC-02` | Storage isolation | Synthetic probes show no durable original-message path or canary in temporary files, IPC spill, raw digests, crash/core dumps, swap/pagefile persistence, caches, logs, telemetry, or backups. Annotator, analyst, CI, Git, and release accounts cannot list/read vault data, transient input, mappings, transformed quarantine, backups, or keys; controls and denied access are witnessed. |
| `AC-03` | Access/separation | Shared, stale, self-approved, two-role, bulk, escalated, and revoked access is rejected. Evidence shows individual MFA accounts, least privilege, time bounds, no principal performing more than one same-family submission/intake, de-identification, independent-review, or promotion function, revocation SLA, and two-person break-glass; no waiver bypasses this separation. |
| `AC-04` | Intake and promotion safety | **AC-04-I:** route, OTP/password/PIN, account/card/UPI, phone, direct-identifier, attachment, Unicode, consent-mismatch, and unsafe-transformation canaries are terminally rejected with zero durable message or family text and zero annotator exposure. **AC-04-P:** reviewer disagreement keeps approved transformed text quarantined or rejects it; a downstream canary or later false negative stops annotation, terminally rejects/tombstones the family, and sets intake `SUSPENDED` when systemic; later processing requires two matching independent approvals, machine validation, and the random version binding. Both subchecks are mandatory at their matrix transitions. |
| `AC-05` | Withdrawal closure | A synthetic contribution is located across descendants, queues, caches, exports, and model references. Partial failure blocks completion/training/release; success withdraws, prevents reingestion, recomputes splits, records content-free evidence, and is idempotent. |
| `AC-06` | Retention deletion | Tests prove raw retention is zero and test-clock expiry covers recruitment/consent, transformed text, mapping, log, and backup tiers; restored backups reapply tombstones; silent snapshots do not survive; only separately approved holds pause deletion. |
| `AC-07` | Incident drill | Raw-in-log/Git, unauthorized-read, consent-mismatch, key-canary, and failed-deletion events halt intake, contain the family, alert owners securely within approved deadlines without prohibited ticket content, revoke access/keys, assess lineage, and require independent repair/rescan before resume. |
| `AC-08` | Reviewer exposure | Inert route/HTML/attachment canaries plus DOM/DNS/HTTP/process monitoring prove annotators see only immutable de-identified text/placeholders with zero navigation, network, script, attachment, or LLM calls; workload, breaks, opt-out, and support are enforced. |
| `AC-09` | Logging | A unique inert canary traverses success, error, exception, withdrawal, and incident paths with zero original, raw-digest, escaped, URL, or Base64 occurrence; logs are allowlisted, content-free, tamper-evident, and lifecycle-controlled. |
| `AC-10` | Equivalence secrets | Arbitrary equality/dictionary/mapping access is denied; no keys, originals, raw digests, or mappings enter corpus, logs, Git, or packages. For every synthetic candidate dictionary, no value outside the ephemeral boundary equals raw SHA-256 or supports equality probing. Synthetic rotation regenerates commitments/tokens/components, invalidates the old key, and records destruction. |
| `AC-11` | Git exclusion | A disposable-copy force-add/hook-bypass canary is rejected; transient intake and restricted hosts lack Git credentials/egress; staged and release scanners fail closed. In a disposable copy, changing tracked `Status: BLOCKED`, changing any of the 52 `EXTERNAL ONLY — UNKNOWN` cells, or inserting a real-looking decision, date, reference, or hash must make staged and release scanning fail. |
| `AC-12` | Package/CI exclusion | Wheel, sdist, container, and docs builds use a clean allowlisted source tree while the consent vault, transient intake, and restricted storage are unmounted and inaccessible. Inspection of every manifest and built archive confirms that exact allowlists and hash-pinned synthetic fixtures yield no restricted content, paths, caches, mappings, keys, raw digests, or restricted JSONL. |
| `AC-13` | Recovery integrity | Restoring every durable tier after withdrawal, expiry, revocation, rejection, or quarantine preserves tombstones and withdrawn/rejected/quarantined state; any resurrection or original-message artifact blocks service and collection. |

Tracked-template immutability is currently a policy-only negative control. Its
AC-11 branch remains `NOT RUN / FAIL` until a scanner implements it and the
result is externally witnessed. Scanner rejection can prove only that the
negative guard fired; it cannot create positive collection authorization.

For each AC, the approved external system must record `PASS`, `FAIL`,
`INCONCLUSIVE`, or `UNRUN`; witnessed date; accountable role; evidence
reference and hash; exact AC-suite, policy, and build hashes; branch coverage;
and residual risk. AC-04-I and AC-04-P are distinct nested evidence records and
outcomes under AC-04; neither may be marked `PASS` using the other's evidence.
Each transition requires exactly its listed outcomes to be `PASS`, current, and
hash-matched. A later-transition AC or subcheck may remain `UNRUN` without blocking
an earlier transition where it is not listed. Evidence must contain no canary
value, original data, route, credential, key, mapping, or participant
identifier. None of these filled values belongs in this Git template.

## 8. Explicit non-automation decision

Do not implement a new positive software authorization checker yet. Authority
identities, evidence/attestation verification, effective and expiry semantics,
revocation propagation, and supersession rules are not frozen. Until they are,
software may validate structure and remain blocked, but it cannot emit an
authoritative positive collection decision. Only the approved external
accountable process can advance the filled, signed external instance's intake
or family state, and it must preserve the evidence boundary above. Only the
v0.1 validator derives aggregate batch readiness. This tracked template never
advances intake, family, or batch state.
