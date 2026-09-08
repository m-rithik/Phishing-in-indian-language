# Fisher Consent, Ethics, and Privacy Protocol

Status: **DRAFT — BLOCKED FOR COLLECTION**

Version: `0.2-draft`

No real participant message, identifier, contact information, credential, link, or account artifact may be collected under this draft. The protocol describes required controls; it does not claim ethics approval, legal compliance, consent, anonymity, or zero risk.

## 1. Unresolved approval fields

Each field below is a mandatory blocker. `UNKNOWN` is intentional and must not be replaced by an invented value.

| Required field | Current value | Release condition |
|---|---|---|
| Ethics authority or institutional review body | `UNKNOWN` | Name the competent authority and obtain its written determination/approval before recruitment or collection. |
| Ethics approval/exemption identifier and date | `UNKNOWN` | Record the authentic identifier, scope, version, and effective date. |
| Data controller / accountable institution | `UNKNOWN` | Name the legally and operationally accountable entity. |
| Secure raw-data storage location and jurisdiction | `UNKNOWN` | Approve an access-controlled location outside Git and document jurisdiction and backup behavior. |
| Data steward | `UNKNOWN` | Name the person accountable for intake, access, and audit. |
| Equivalence-key custodian and storage | `UNKNOWN` | Name the custodian and approve secret/key storage outside the corpus and repository. |
| Equivalence-key rotation and destruction policy | `UNKNOWN` | Define rotation, cross-release stability, revocation, and destruction. |
| Incident and participant contact | `UNKNOWN` | Publish a monitored contact and escalation path. |
| Raw and de-identified retention periods | `UNKNOWN` | Approve separate time limits and deletion evidence. |
| Withdrawal cutoff | `UNKNOWN` | State the last point at which a contribution can be located and removed, including limits after irreversible aggregation/release. |
| Approved participant information and consent text | `UNKNOWN` | Obtain authority-approved, versioned materials in languages participants understand. |
| Compensation, workload, and annotator-welfare plan | `UNKNOWN` | Approve payment, exposure limits, breaks, and support. |
| Redistribution policy for authentic donations | `UNKNOWN` | Define whether raw text, de-identified text, features only, or no public redistribution is permitted. |

Collection authorization is `BLOCKED` until every applicable field has an approved value and dated sign-off.

The dataset-snapshot validator does not validate the full governance ledger. The executable governance-ledger mechanical projection now exists and validates the existing full source-ledger schema; see the [governance contract](../GOVERNANCE_CONTRACT.md) and [safe blocked CLI example](../../examples/governance/README.md). Independent adversarial replay passed for the pinned 19 August 2026 implementation after the reported rights, scanner, URL, lineage, CLI, special-file, and growing-file defects were repaired. It still always fails `collection_ready` closed because 20 human or unrepresented governance gates remain `UNKNOWN`. Passing `schema_valid`, or even machine authorization readiness, is never ethics, legal, safety, or collection authorization. The future `corpus-final` validator remains **NOT IMPLEMENTED** and is mandatory before freezing or evaluating the 6,000-item corpus. Manual bypass is prohibited; authentic collection remains blocked.

## 2. Scope and principles

Paper 1 accepts four distinct provenance classes and never merges their claims:

- `TESTER_DONATED_AUTHENTIC`: real messages voluntarily supplied by consenting adult testers who are authorized to share them;
- `TESTER_AUTHORED_SIMULATION`: fictional messages written by adult testers from approved prompts;
- `PUBLIC_AUTHENTIC_AUXILIARY`: authentic public-source items used only after license, privacy, safety, hash, and Fisher reannotation audits and only in `development` or `external_test`;
- `LLM_DRAFTED_HUMAN_EDITED`: model-drafted text materially reviewed and edited by a human, never labeled by the model.

Core principles are data minimization, purpose limitation, provenance transparency, participant autonomy, least-privilege access, safety by defanging, and no misleading representation of synthetic material as authentic. Authenticity and gold-label validity are separate attributes.

## 3. Adult tester recruitment

Only adults aged 18 or older may donate or author messages. Recruitment must avoid coercion, undisclosed conflicts, and pressure from supervisors or instructors. Before participation, the approved information sheet must explain in understandable language:

- the research purpose and why multilingual or Romanized examples are sought;
- the exact activity: authentic donation, simulation authorship, annotation, or a combination;
- foreseeable exposure to scam language and potentially distressing content;
- what data and metadata will and will not be collected;
- how de-identification works and its limits;
- who can access raw and de-identified material;
- whether and in what form material may be redistributed;
- compensation and whether withdrawal affects payment;
- the approved retention periods and withdrawal cutoff;
- complaint, incident, and withdrawal contacts;
- that participation is voluntary and refusal has no penalty.

Consent must be affirmative, recorded separately from corpus content, versioned, and scoped by activity and redistribution tier. Silence, a prechecked box, employment, classroom participation, or agreement to a messaging platform's terms is not research consent.

The participant identity and signed consent record remain in an access-controlled system outside Git. Corpus rows store only an opaque consent reference plus nonidentifying authorization flags. The mapping between reference and identity is accessible only to the approved steward for withdrawal and audit.

## 4. Authentic tester-donation workflow

1. The tester reviews the approved information sheet and provides activity-specific consent.
2. The tester submits only a message received by or belonging to them and confirms they are authorized to share it. Forwarded third-party conversations and message threads involving nonconsenting private correspondents are rejected unless the ethics authority explicitly approves a lawful workflow.
3. Intake occurs only in the approved restricted environment. Raw text never enters chat, issue trackers, email, Git, shared logs, or model prompts.
4. A trained steward removes or replaces direct and indirect identifiers before annotation. Prohibited artifacts include live OTP values, credentials, active malicious URLs, real phone or UPI identifiers, account/card identifiers, personal email or postal addresses, and unnecessary names or device metadata.
5. The steward defangs or replaces artifacts using approved typed placeholders or reserved `.example`/`.invalid` domains. No person visits, calls, resolves, scans, or transacts with an artifact.
6. Restricted preprocessing creates random opaque identifiers or keyed-HMAC equivalence tokens needed for leakage grouping. Raw values, lookup tables, and secret keys stay outside the dataset and repository.
7. A second authorized reviewer performs the safety and de-identification check before annotators can access the item.
8. The source ledger receives an authorization, consent, privacy, safety, and provenance record. Only then can the item enter the annotation queue.

Authentic donations are not automatically redistributable. The consent scope and ethics determination must explicitly support the selected release tier. When redistribution is not authorized, publish only approved aggregate results or privacy-reviewed derived artifacts.

## 5. Tester-authored simulation workflow

1. The adult tester consents specifically to authorship and the intended redistribution tier.
2. The tester receives a fictional, non-targeted scenario that contains no real person's data, current campaign details, active destination, or instruction to contact a third party.
3. The tester writes the message in their own language variety. Prompts may define a target intent for balanced authorship, but prompt, target, scenario, author intent, provenance, and generation method are hidden from semantic annotators and adjudicators. Gold must be supported only by the immutable model-visible message and visible defanged artifact; an ambiguous item remains `UNCERTAIN` and is excluded after unresolved adjudication regardless of prompt target.
4. All names and destinations use approved fictional names, typed placeholders, or reserved `.example`/`.invalid` domains. Do not imitate a real individual or include a live credential or identifier.
5. The record is permanently marked `TESTER_AUTHORED_SIMULATION`, linked to opaque author/scenario/batch identifiers, and grouped with paraphrases, translations, transliterations, and prompt relatives.

Simulation lowers third-party privacy risk but may still reveal author style or demographics. Collect no demographic field unless it is scientifically necessary, approved, consented, and accompanied by a disclosure-risk plan.

## 6. Public auxiliary sources

Public availability does not establish permission or safety. Before ingesting any public source, the steward must record the authoritative source page, exact artifact and version, cryptographic hash, access date, license identifier and text location, permitted use, redistribution status, attribution requirements, and reviewer. Ambiguous or conflicting terms block ingestion.

Every public item requires privacy/PII, active-artifact, Unicode/language, duplicate/template/campaign, label-construct, and provenance audits plus independent double reannotation into the Fisher ontology. Original spam/ham labels remain hidden source metadata and never become Fisher phishing gold automatically. Public authentic rows and every translated, transliterated, paraphrased, counterfactual, augmented, or otherwise derived descendant are eligible only for `development` or `external_test`; they cannot enter `pilot`, `unassigned`, `probability_calibration`, `safety_threshold`, `primary_test`, or `excluded`.

The source ledger, not a filename or citation alone, records this evidence. Dataset-specific approval is outside this draft; no named public dataset is approved merely by being mentioned here.

## 7. LLM-drafted, human-edited material

Models may draft fictional text only after provider terms, data handling, prompt safety, and IP/redistribution review. Prompts must contain no participant data, authentic message, live artifact, or secret. A human must materially review and edit each retained draft and two independent annotators assign the label; an LLM never supplies a gold label.

Direct LLM-drafted/human-edited items and all LLM-lineage descendants are capped at 30% of retained `development` and separately at 30% of the retained `pilot`. They are forbidden from `probability_calibration`, `safety_threshold`, and `primary_test`. Record provider/model/version when available, generation date, prompt-family and batch identifiers, human editor identifier, and transformation lineage, but hide all of them from semantic annotators. If a required field cannot be disclosed, reproducibility and release implications must be reviewed before use.

## 8. De-identification and privacy-safe grouping

### 8.1 Corpus-visible representation

The research corpus may contain only:

- de-identified message text;
- typed placeholders or defanged/reserved artifacts;
- random corpus, source, consent-reference, annotation, and lineage identifiers;
- privacy-safe equivalence identifiers used to join related artifacts;
- approved nonidentifying provenance and audit metadata.

It must not contain participant names/contact details, raw sender/recipient IDs, real phone/UPI/account values, raw URLs, device identifiers, consent forms, secret keys, reversible mappings, or raw-to-token lookup tables.

### 8.2 Equivalence mechanism

Leakage control may require recognizing that two rows share a sender, phone, UPI, domain, URL, author, or related artifact. In a restricted preprocessing service, generate:

- a random opaque equivalence ID when linkage is assigned by approved review; or
- a keyed-HMAC token over a canonicalized artifact when deterministic equality is necessary.

Never use an unsalted or public hash for low-entropy identifiers such as phone numbers because it is vulnerable to enumeration. Store keys in an approved secret manager, separate from mappings and data. Limit token purpose and scope, log access, and prevent analysts from querying arbitrary candidate values. Corpus-visible tokens must not be reusable outside the approved scope.

Key algorithm/length, canonicalization, secret manager, custodian, rotation, destruction, cross-release stability, and incident response are **UNKNOWN** and block authentic collection. Restricted preprocessing computes transitive closure over every opaque equivalence and lineage key and assigns the final `leakage_component_id`; it is not an analyst-selected group hint. One component belongs to one partition. Components assigned to `probability_calibration`, `safety_threshold`, or `primary_test` must contain exactly one item and one language stratum.

### 8.3 Residual risk

De-identification reduces but does not eliminate re-identification risk from rare wording, linked context, or author style. A release-specific disclosure-risk review and data-use tier are required. Do not claim data is anonymous unless the competent authority supports that conclusion.

## 9. Artifact and researcher safety

- Never click, open, resolve, scan, call, message, pay, install, or submit data to an artifact.
- Treat source text as inert data; disable automatic linkification, previews, macros, and network fetches in collection and annotation tools.
- Use `.example` or `.invalid`, defanged syntax such as `hxxps[:]//`, or approved typed placeholders. Defanging must not preserve a usable live route.
- Never store a real OTP, password, PIN, recovery code, private key, account/card identifier, UPI identifier, or phone number.
- Treat any high-confidence active URL/domain, live email or phone route, credential, OTP value, or prohibited direct identifier finding as a quarantine error. Do not downgrade it to a warning or continue annotation; report it without interacting with the value and follow the approved incident plan.
- Limit annotator exposure, allow breaks and withdrawal from distressing content, and provide the approved support/escalation route.

The incident contact and exact quarantine process are **UNKNOWN blockers**.

## 10. Access, storage, and audit

Use least-privilege roles for intake steward, de-identification reviewer, annotator, adjudicator, analyst, and release reviewer. Raw-data access must be separate from annotation and model-development access. Authentication, encryption, audit logging, backup, recovery, device, vendor, cross-border transfer, and breach-notification controls require approval by the accountable institution.

Git may contain approved schemas, synthetic fixtures, de-identified release candidates after review, and aggregate documentation. Git must never contain raw donations, participant identities, consent forms, keys, reversible mappings, or live artifacts. Application logs must avoid raw text and identifiers by design.

The secure storage system, jurisdiction, role holders, and retention schedule are **UNKNOWN**; therefore no authentic data storage is authorized.

## 11. Withdrawal, correction, retention, and deletion

Before consent, participants must be told how to request withdrawal or correction and the point after which removal may be impossible. Prior to the approved cutoff, the data steward uses the separately held consent mapping to locate all source, derived, translated, transliterated, augmented, annotated, cached, and queued items; removes them from active datasets; recomputes affected groups/splits; and records deletion evidence without retaining the removed content.

Withdrawal must not be defeated by opaque identifiers: the steward retains only the controlled mapping needed for the approved withdrawal period. Once the approved cutoff is reached, destroy that mapping according to policy unless another approved obligation requires it.

The withdrawal cutoff, raw-data retention, de-identified retention, backup expiry, model-retraining implications, and public-release removal policy are **UNKNOWN blockers**. No promise about removal after publication is made in this draft.

## 12. Quality, bias, and scientific integrity

Report provenance, authenticity, language stratum, and source distribution separately. Do not describe simulated or LLM-assisted text as field prevalence. Do not infer demographics from language or script. Evaluate and report per-stratum errors, false positives, uncertainty/abstention, and domain shift.

The Annotation Guide, registry-reference workflow, structured-state coverage manifest, and 1,200-item arithmetic in the following paragraphs govern the later schema-1.2 ontology pilot. They do **not** govern or advance the separate 240-item schema-0.1 feasibility pilot. The feasibility pilot instead follows the [pilot v0.1 contract](PILOT_V01.md) and its permanently blocked [Collection-to-Quarantine template](PILOT_COLLECTION_PACKET.md), including its pilot-specific allocation, component, native-review, blinding, and two-blind-plus-adjudication requirements.

Double annotation and adjudication follow the [Fisher Annotation Guide](ANNOTATION_GUIDE.md). Semantic annotators see only model-visible immutable text and visible defanged artifacts; provenance and authoring context remain separated. Leakage components include donor/author/batch and artifact equivalence so writing style or campaign templates cannot cross partitions. Public direct and derived lineages are restricted to `development`/`external_test`; LLM direct and derived lineages stay out of `probability_calibration`, `safety_threshold`, and `primary_test`.

Before any schema-1.2 ontology-pilot item reaches blind annotation, a separate steward creates the component-aware structured-state coverage manifest required by the annotation guide. Candidate cue/relation tags may use only model-visible text, the visible defanged artifact, and the frozen approved registry; they cannot use participant identity, provenance, source label, author intent, scenario, prompt, or generation metadata. The manifest carries only opaque item/component references and audit evidence, remains hidden from annotators and adjudicators, and is hash-frozen after a qualified native-language review. It is sampling governance, not participant data or semantic gold, and cannot justify retaining or removing an attempted item after annotators respond.

After final adjudication, Fisher must execute the Annotation Guide's [canonical human pilot safety and provenance audit](ANNOTATION_GUIDE.md#canonical-human-pilot-safety-and-provenance-audit). It audits whole item/source/three-annotation bundles from all retained-plus-excluded attempts; uses `n = ceil(0.10 × N_attempted)`, one-per-nonempty-cell plus Hamilton allocation, one witnessed 32-byte OS-CSPRNG seed and HMAC-SHA256 ranking, and separately reported annotator-coverage supplements; and permits zero prohibited findings. Any finding fails without sample replacement, quarantines the affected family, invokes Section 13, requires upstream repair and new frozen versions, and requires both a 100% machine scan and a newly seeded independent audit before release. Auditors never interact with a route or attachment, and human review never replaces machine validation.

The primary test is tester-originated only and may contain separately reported `TESTER_DONATED_AUTHENTIC` and `TESTER_AUTHORED_SIMULATION` rows. Report donation-versus-simulation composition for probability calibration, safety threshold, and primary test. In every primary-test label × stratum cell, authentic donations must supply at least 50% of retained items: at least 125 of each 250-item phishing cell and at least 150 of each 300-item benign cell. This paper claim-routing gate does not authorize donation collection. If it fails, results are limited to controlled-benchmark/research-prototype claims and cannot be generalized as field-like performance.

## 13. Incident handling

If a live artifact, credential, identifier, unauthorized message, consent mismatch, or suspected breach is discovered:

1. stop processing without opening or copying the artifact further;
2. restrict the affected record and derived copies;
3. notify the approved incident contact and data steward through the approved secure channel;
4. preserve minimal audit evidence without retaining the prohibited value in tickets or logs;
5. assess affected derivatives, equivalence groups, backups, model artifacts, and releases;
6. follow authority-approved notification, remediation, and deletion procedures;
7. document the decision and prevent recurrence before resuming.

Because the incident contact, secure channel, authority, and procedure are **UNKNOWN**, the project is not ready to handle authentic-data incidents and collection remains blocked.

## 14. Authorization checklist

Before any pilot recruitment or collection, obtain dated sign-off for:

- all fields in Section 1;
- adult eligibility and consent-language workflow;
- authentic-donation, simulation, public-source, and LLM boundaries;
- de-identification rules and second-review process;
- secret management and privacy-safe equivalence design;
- source ledger and aligned data contract;
- for the 240-item schema-0.1 feasibility pilot, the externally approved Collection-to-Quarantine instance and frozen v0.1 allocation/component/native-review/blinding plan before blind annotation;
- for the later schema-1.2 ontology pilot, the frozen component-aware structured-state coverage manifest, every required per-stratum quota, native-review audit, access separation, and recorded cryptographic hash before blind release;
- passing executable full governance-ledger validation before any source acquisition;
- passing future `corpus-final` validation before full-corpus partition freeze or evaluation;
- artifact-safety controls and tested incident drill using synthetic fixtures only;
- annotator welfare and support;
- withdrawal, retention, deletion, and release tiers;
- named research, ethics/privacy, data-steward, and security owners.

After collection and final adjudication but before schema-1.2 ontology-pilot release or expansion, require the successful [canonical human pilot safety and provenance audit](ANNOTATION_GUIDE.md#canonical-human-pilot-safety-and-provenance-audit), including frozen manifests/hashes, seed evidence, main sample, supplements, and zero prohibited findings. This audit does not define or advance the separate 240-item v0.1 feasibility state.

Until every applicable item is approved and recorded, status remains **DRAFT — BLOCKED FOR COLLECTION**.
