# Fisher Paper 1 Threat Model

> Status: **DRAFT — PRE-DATA, INTERNAL, AND NOT PRODUCTION PROTECTION**
>
> Version: `0.1-draft`
>
> Fisher is a research prototype for a controlled Paper 1 experiment. It is not
> a deployed anti-phishing service, does not make a safety guarantee, and must
> not be represented as protecting a person, device, account, or transaction.
> This document does not authorize authentic-data collection, protected-set
> access, model release, a public demo, or publication.

## 1. Evidence boundary and authority

This threat model uses the project evidence labels exactly:

- **OBSERVED:** directly established by the current repository or an executed
  check recorded by the project;
- **DERIVED:** a security conclusion that follows from observed design evidence;
- **ASSUMED:** a planning premise that has not been verified; and
- **UNKNOWN:** evidence is absent and a named check or decision is required.

**OBSERVED:** the repository is pre-data and pre-model. It contains strict
dataset and governance validators, a synthetic-only audit-selector rehearsal,
synthetic fixtures, and research specifications. It contains no Fisher corpus,
trained checkpoint, protected partition, model result, or demo. The current
execution boundary is recorded in [Execution Status](EXECUTION_STATUS.md).

**OBSERVED:** dataset, governance, and audit tooling exists and has synthetic
tests. Independent review identified governance policy/scanning/lineage defects
and an audit-selector scaling defect; both repaired revisions now have focused
independent passes. The governance projection still reports
`collection_ready=false` with 20 human gates unknown, and the synthetic selector
cannot certify a human audit. Its measured maximum-input memory cost is also
operationally material. A later dataset review reproduced two file-byte-bound
bypasses despite the then-passing tests; the pinned repair replay closed both
probes and passed 34/34 focused and 93/93 full tests as `E07`, preserving the
earlier `E06` failure. These boundaries are defined in the
[data contract](../DATA_CONTRACT.md),
[governance contract](../GOVERNANCE_CONTRACT.md), and
[audit-selector contract](../AUDIT_SELECTOR_CONTRACT.md).

**OBSERVED:** `E09` independently passed only the scoped schema-1.2 syntactic
VMP repair (42/42 focused and 101/101 full). `E10` independently passed the
original E08 specification repairs but found four new provider-identity,
endpoint/projection, boundedness, and metric-binding blockers. `E11`
independently passed those repairs but found five later provider-execution/run-
envelope, endpoint-numeric, E0-feature, evaluation-universe, and rewrite-
coordinate blockers. Its 101-test suite did not execute an engine. `P0` remains
blocked: `E12` found five remaining status-union, control-mask,
evaluation/gold-binding, system-provenance/five-seed, and candidate-numeric
blockers. `E13` then found three remaining preflight/run-union,
failure-accounting, and metric-input/counting groups. `E14` passes those repairs
and the other major contracts but finds three engine-descriptor/parser,
eligibility-accounting, and metric-universe/denominator/algebra groups. `E15`
passes those repairs and the previously reviewed surfaces but finds three strict
universe-input parser/count, structural-versus-semantic precedence, and
nonempty-denominator groups. The eighth local, universe-only docs repair requires
independent replay.

**DERIVED:** schema validity is necessary but not sufficient for safety,
authorization, annotation truth, registry truth, split independence, model
robustness, or publishability. A clean machine report cannot close a human-owned
gate.

**UNKNOWN:** the accountable institution, ethics authority, data controller,
data steward, security lead, incident contact, key custodian, native-language
reviewers, secure storage, retention policy, and protected-access custodian have
not been evidenced. Role names below therefore specify required ownership, not
named or authorized people.

## 2. Scope and non-goals

### 2.1 In scope

The threat model covers the Paper 1 lifecycle for:

- adult tester-donated authentic standalone messages;
- adult tester-authored simulations;
- public authentic auxiliary sources and their descendants;
- LLM-drafted, materially human-edited development/pilot material;
- restricted de-identification and equivalence-component preprocessing;
- JSONL ingestion, governance validation, annotation, and pilot-audit tooling;
- the frozen offline organization/artifact registry;
- governed transliteration resources and candidate posteriors;
- model development, factorial conditions, controls, calibration, thresholding,
  selective abstention, and the one-time protected evaluation;
- manifests, checkpoints, predictions, metrics, logs, and paper artifacts;
- a local offline research demo and the eventual publication/release process.

The shared `VisibleMessagePacket` (`VMP`) is exactly schema-`1.2.0`
`item.text` plus the non-gold, pre-annotation `item.visible_artifacts`
inventory, bound by required `item.vmp_sha256`; annotations never construct or
infer it. Artifact grammar and exact Unicode-code-point destination-span binding
follow the [data contract](../DATA_CONTRACT.md#visible-non-gold-artifact-inventory-and-vmp)
and prove syntactic representation safety only, not authenticity, semantic
type, collection authority, or release authority. VMP excludes provenance,
source label, donor intent, scenario, prompt, campaign/grouping, registry,
annotations, and labels.
Only semantic conditions may create the canonical Cartesian audit packet by
applying the frozen offline resolver to predicted bounded visible endpoint sets.
That full packet is never a learned input; the risk head receives only the
deterministic `SemanticFeaturePlan`. `E0` instantiates its exact pinned-Unicode
five-category binary64 VMP grid and 31-dimensional, 64-row masked tensor audit;
a future candidate/subword-to-VMP adapter and feature-plan version must freeze
before `E3` and remain unimplemented. Paper 1 covers Hindi-dominant,
Telugu-dominant, and English–Indic code-mixed text. The exact scientific scope is
frozen in the [preregistration](PAPER_1_PREREGISTRATION.md).

### 2.2 Non-goals

- Production malware analysis, incident response, transactional fraud blocking,
  or a guarantee that an input is safe.
- Live URL, DNS, WHOIS, redirect, reputation, search, telephone, payment, or
  account lookup during annotation, training, evaluation, inference, or demo.
- Visiting, resolving, calling, messaging, executing, installing, opening, or
  transacting with any submitted artifact.
- Conversation, voice/ASR, image, QR, browser-context, attachment, or endpoint
  protection for Paper 1.
- Continual or online learning, automatic feedback ingestion, or a public
  arbitrary-input inference API.
- An inference-time LLM or LLM-generated explanation. Paper 1 uses bounded
  structured evidence; an LLM may only draft fictional source material under
  the separate governed provenance rules.
- Protection against a fully compromised operating system, secret manager, or
  authorized administrator. Those scenarios are retained as operational risks,
  not claimed as solved by research code.

Approved evidence or public-resource acquisition, if later authorized, occurs in
a separate quarantined acquisition workflow. It does not create a network lookup
path inside annotation, modeling, evaluation, or the offline demo.

## 3. Assets and harm model

| Asset ID | Asset or claim | Security property | Harm if compromised |
| --- | --- | --- | --- |
| `A01` | raw donation, participant identity, consent mapping, withdrawal mapping | confidentiality, purpose limitation, traceable deletion | re-identification, coercion, participant harm, invalid consent |
| `A02` | de-identified message, labels, spans, provenance, lineage | integrity, confidentiality, authenticity | privacy leakage, poisoned gold, invalid benchmark |
| `A03` | equivalence keys, raw-to-token mappings, secret-manager state | confidentiality, separation, revocability | enumeration of low-entropy identifiers, cross-release linkage |
| `A04` | source ledger, rights/ethics evidence, approval history | authenticity, integrity, non-repudiation | unauthorized acquisition or release, false compliance claim |
| `A05` | registry evidence, normalization, completeness decisions | integrity, freshness, independence | false `MATCH`/`MISMATCH`, circular target, biased model |
| `A06` | transliteration pairs, acceptable forms, generator, `T_tr` | provenance, integrity, partition isolation | candidate poisoning, hidden backdoor, false coverage claim |
| `A07` | components, partitions, manifests, protected-access state | integrity, confidentiality, one-way lifecycle | leakage, benchmark overfitting, invalid confirmatory inference |
| `A08` | code, dependencies, checkpoints, configs, seeds, run environment | provenance, integrity, reproducibility | code execution, tampered result, non-reproducible paper |
| `A09` | calibration logits, temperatures, thresholds, predictions, statistics | integrity, completeness, immutability | manipulated low-FPR result or unsupported superiority claim |
| `A10` | annotator and researcher safety, time, and welfare | safety, availability, exposure minimization | distress, unsafe interaction, denial of work |
| `A11` | Fisher research claim, paper, demo, and institutional reputation | scientific integrity, bounded communication | false assurance, unsafe use, retraction, rights or IP harm |

The harm model prioritizes: participant or researcher safety; privacy and data
rights; scientific validity; false-positive/false-negative harms and unequal
abstention; reproducibility and accountability; then service availability. A
scientifically invalid “safe” result is a security harm because it can induce
false protection claims.

## 4. Actors and adversary capabilities

| Actor | Legitimate role | Credible failure or adversarial capability |
| --- | --- | --- |
| tester/donor | donate or author an approved message | mistake, unauthorized third-party content, crafted Unicode, hidden identifier, repeated/template submission |
| source publisher/provider | provide a public or generated resource | replace files, obscure terms, retain prompts, introduce patterned or poisoned content |
| intake steward/reviewer | authorize, de-identify, defang, quarantine | human error, policy bypass, insider misuse, unsafe copying |
| annotator/adjudicator/auditor | assign or review semantic state | collusion, fatigue, provenance inference, registry misuse, selective exclusion |
| registry/resource reviewer | approve official evidence and linguistic resources | incomplete review, stale evidence, protected-derived update, conflict of interest |
| analyst/model developer | split, train, calibrate, evaluate | accidental leakage, benchmark gaming, threshold manipulation, unauthorized protected access |
| dependency/checkpoint publisher | distribute code or weights | malicious custom code, compromised package, mutable revision, serialized payload |
| local insider or compromised account | access one project role or workspace | copy restricted material, alter manifests/results, escalate through overbroad access |
| publication/demo consumer | inspect released artifacts | infer members, misuse model, treat prototype output as protection, redistribute restricted text |
| external phishing operator | attempt to evade or poison a future intake/demo | obfuscation, homoglyphs, prompt/template flooding, distribution shift |

**ASSUMED:** role separation and least privilege can be implemented before
collection. **UNKNOWN:** the actual identity, training, conflicts, device posture,
and authorization of every role. The design does not assume all insiders are
benign, nor does it assume machine detectors find every prohibited artifact.

## 5. Trust boundaries and data flow

```text
TB0 outside world
  adult tester / authorized public-resource acquisition / approved LLM drafting
        |
        v
TB1 restricted intake quarantine (raw, untrusted, no Git/chat/shared logs)
        |
        | two-person authorization + safety + de-identification review
        v
TB2 restricted preprocessing service
  raw-to-placeholder transformation + keyed equivalence/lineage closure
  secrets and reversible mappings stay here
        |
        | de-identified immutable packet + opaque IDs + manifest hashes only
        v
TB3 governed research data zone
  source projection -> strict JSONL validators -> annotation interface
  annotators see VMP only; registry reviewer later sees the Cartesian product of final endpoint sets only
        |
        | two blind records + distinct final record + frozen audit bundle
        v
TB4 component and partition boundary
  development | probability_calibration | safety_threshold | primary_test
       |                  protected partitions remain access-controlled
       v
TB5 offline model-build boundary
  pinned transliteration resource + frozen registry + code/dependencies
  -> baselines/factorial systems/controls -> locked five-seed artifacts
        |
        | separately authorized sequential access; immutable run manifest
        v
TB6 calibration, threshold, and one-time confirmatory boundary
  probability calibration -> benign safety threshold -> primary test once
        |
        v
TB7 release boundary
  bounded aggregate results -> offline synthetic/authorized demo -> paper/package
```

Independent side inputs cross controlled boundaries:

- official evidence crosses from a quarantined acquisition process into a
  content-hashed read-only registry; the model never performs a live lookup;
- paired transliteration resources cross only after license, hash, grouping, and
  partition audit and never contain Fisher protected text or labels;
- packages/checkpoints cross only through an allowlisted, pinned, offline build
  process; arbitrary custom model code is not trusted merely because a model hub
  hosts it.

The highest-risk transitions are `TB1 -> TB2` (unsafe raw content), `TB2 -> TB3`
(de-identification failure), `TB3 -> TB4` (component leakage), `TB5 -> TB6`
(protected-set contamination), and `TB6 -> TB7` (privacy, rights, and claim
overreach).

## 6. Risk-rating rubric

Ratings are ordinal review aids, not measured probabilities.

### 6.1 Severity

| Rating | Decision rule |
| --- | --- |
| `CRITICAL` | credible participant/credential harm, secret compromise, unauthorized raw-data release, arbitrary code execution, protected-test invalidation, or a false production-safety claim |
| `HIGH` | invalidates a primary scientific claim, materially exposes de-identified members, corrupts provenance/gold, or defeats a required stop gate |
| `MODERATE` | damages a secondary analysis, reproducibility, bounded availability, or a recoverable internal artifact without direct participant harm |
| `LOW` | localized inconvenience or cosmetic integrity loss with no effect on safety, privacy, or claims |

### 6.2 Likelihood under the planned prototype

| Rating | Decision rule |
| --- | --- |
| `EXPECTED` | ordinary workflow or data characteristics will exercise the condition without adversarial intent |
| `PLAUSIBLE` | a realistic mistake or motivated actor can reach the precondition with ordinary project access |
| `CONDITIONAL` | requires a future feature, uncommon access combination, or multiple failed controls |
| `REMOTE` | requires capabilities outside the stated system boundary, while not being impossible |

An untested prevention lowers no rating by itself. Residual risk is stated
qualitatively per threat. `UNKNOWN` evidence never receives a reassuring rating.

## 7. Threat register

Each entry distinguishes machine enforcement from human judgment. “Required”
means the control is a gate, not that it currently exists.

### TM-01 — Intake identity, consent, or authority spoofing

- **STRIDE / ML class:** spoofing, repudiation, provenance poisoning.
- **Surface and precondition:** a tester or steward can submit a message or
  consent/source reference before authenticated authority and ownership checks.
- **Inherent assessment:** `CRITICAL / PLAUSIBLE`.
- **Affected asset or claim:** `A01`, `A02`, `A04`; lawful/ethical collection and
  tester-originated primary-population claims.
- **Prevention:** require adult, activity-specific, versioned consent; reject
  third-party conversations without explicit authority; keep identity/consent
  outside the corpus; bind only an opaque consent reference; require two-person
  intake review and a named data steward.
- **Detection:** reconcile consent scope, source authorization, lifecycle,
  withdrawal state, and row provenance; sample complete source/item/annotation
  bundles in the canonical human audit.
- **Recovery:** stop intake; quarantine the source and descendants; verify
  authority through the approved channel; delete unauthorized derivatives and
  recompute components/splits; record the incident without copied raw content.
- **Owners:** machine—governance and dataset validators for representable
  consistency; human—ethics authority, data steward, consent reviewer.
- **Verification artifact:** authenticated consent/authority evidence, source
  ledger version, two-reviewer intake record, withdrawal/deletion evidence.
- **Residual risk:** a valid opaque reference cannot prove voluntariness,
  comprehension, age, or authority. These are current `UNKNOWN` blockers.

### TM-02 — Live artifact, credential, identifier, or unsafe attachment enters the project

- **STRIDE / ML class:** information disclosure, elevation of privilege,
  researcher-safety abuse.
- **Surface and precondition:** untrusted intake, source text, annotation, or
  evidence contains an active route, contact path, secret, identifier, redirect,
  or executable/attachment instruction.
- **Inherent assessment:** `CRITICAL / EXPECTED` for authentic phishing-like
  material.
- **Affected asset or claim:** `A01`, `A02`, `A10`; participant/researcher safety
  and the “inert text only” boundary.
- **Prevention:** authentic raw material stays in restricted intake; no artifact
  is opened or contacted; replace with approved typed placeholders or reserved
  domains; disable previews, linkification, macros, redirects, and network
  fetches; perform independent second review before annotation.
- **Detection:** strict route/contact scanners plus human safety review over the
  full bundle; scan Unicode-dot and IDN forms, bare routes, valid IPs, phone
  forms, credentials, OTPs, account/UPI identifiers, and unsafe attachment
  references without echoing a finding.
- **Recovery:** stop without interacting; quarantine the entire leakage family;
  restrict derivatives, caches, backups, and model artifacts; repair upstream;
  freeze a new version; run a 100% machine scan and newly seeded independent
  audit.
- **Owners:** machine—intake scanner and validators; human—safety reviewer,
  steward, incident lead.
- **Verification artifact:** sanitized scanner report, two-person defanging
  record, quarantine ticket containing no prohibited value, fresh manifest/hash
  and audit evidence.
- **Residual risk:** regex/IDN detectors are intentionally incomplete and human
  reviewers can miss context-dependent identifiers. Zero machine findings is
  not proof of safety.

### TM-03 — Unicode, homoglyph, defanging, or parser differential bypass

- **STRIDE / ML class:** tampering, evasion, input ambiguity.
- **Surface and precondition:** different components normalize, tokenize, render,
  hash, or scan the same Unicode bytes differently.
- **Inherent assessment:** `HIGH / PLAUSIBLE`.
- **Affected asset or claim:** `A02`, `A05`, `A06`, `A07`; safety scanning,
  offsets, language strata, duplicate detection, and adversarial robustness.
- **Prevention:** preserve immutable UTF-8 text; hash exact bytes; use code-point
  offsets; reject surrogates and prohibited controls; make normalization
  purpose-specific and versioned; never rewrite raw text; render untrusted text
  as inert plain text.
- **Detection:** differential tests across scanner, validator, tokenizer,
  registry normalizer, candidate generator, and demo; include NFC/NFD, NFKC
  compatibility, Unicode whitespace/dots, IDN labels, mixed scripts, bidi/control
  cases, emoji, combining marks, and truncation boundaries.
- **Recovery:** quarantine affected records; identify the first divergent
  transform; version the fix; recompute hashes, duplicates, components,
  annotations, and model artifacts affected by changed semantics.
- **Owners:** machine—validation/tool maintainers; human—native-language and
  security reviewers.
- **Verification artifact:** versioned normalization manifest, cross-component
  conformance corpus, raw-offset round-trip tests, render screenshots for the
  annotation/demo UI.
- **Residual risk:** visually confusable and novel-script behavior cannot be
  exhaustively enumerated; synthetic perturbations do not prove real-world
  robustness.

### TM-04 — Resource exhaustion or malicious JSONL structure

- **STRIDE / ML class:** denial of service, parser abuse.
- **Surface and precondition:** an untrusted file can exceed size, line, nesting,
  container, record, or text limits or exploit duplicate/nonfinite JSON values.
- **Inherent assessment:** `MODERATE / PLAUSIBLE`.
- **Affected asset or claim:** `A08`, `A10`; tool availability and deterministic
  validation.
- **Prevention:** enforce byte, line, record, depth, member, and text bounds
  before expensive semantic work; reject duplicate keys, nonobjects, nonfinite
  numbers, malformed UTF-8, blank lines, and unknown fields.
- **Detection:** resource-limit diagnostics, bounded-memory tests, time/memory
  profiling, and fuzzing in an isolated synthetic environment.
- **Recovery:** abort the file, preserve only sanitized diagnostics, quarantine
  it, and require a bounded regenerated artifact rather than partial ingestion.
- **Owners:** machine—tool maintainer; human—security reviewer for limit changes.
- **Verification artifact:** limit tests, profiler output, deterministic error
  report, exact input hash when safe to retain.
- **Residual risk:** current limits constrain data shape, not all algorithmic
  worst cases or host-level exhaustion; resource budgets remain environment
  dependent.

### TM-05 — De-identification failure or semantic re-identification

- **STRIDE / ML class:** information disclosure, membership/privacy leakage.
- **Surface and precondition:** direct identifiers, rare wording, linked context,
  style, or derivatives survive restricted preprocessing.
- **Inherent assessment:** `CRITICAL / PLAUSIBLE`.
- **Affected asset or claim:** `A01`, `A02`, `A11`; participant privacy and any
  redistribution claim.
- **Prevention:** minimize fields; separate raw and research zones; replace
  direct/indirect identifiers; use two-person review; avoid demographic
  inference; restrict release tier; never claim anonymity without authority.
- **Detection:** automated PII/contact scans plus contextual human review;
  disclosure-risk review over text, rare phrases, provenance combinations,
  checkpoints, embeddings, examples, and paper excerpts.
- **Recovery:** quarantine all descendants, cached datasets, checkpoints, and
  drafts; execute withdrawal/deletion policy; retrain or suppress affected
  artifacts where required; notify through the approved incident process.
- **Owners:** machine—PII/safety scanner; human—privacy reviewer, steward,
  controller, release reviewer.
- **Verification artifact:** de-identification checklist, second-review record,
  disclosure-risk decision, lineage deletion manifest, release-tier approval.
- **Residual risk:** de-identification cannot eliminate rare-language or
  author-style linkage. Secure storage, retention, and release policy are
  currently `UNKNOWN`, so authentic collection remains blocked.

### TM-06 — Equivalence-token enumeration, key compromise, or linkage misuse

- **STRIDE / ML class:** information disclosure, elevation of privilege,
  tampering.
- **Surface and precondition:** a low-entropy artifact is publicly hashed, the
  HMAC key/mapping leaks, or an analyst can submit arbitrary equality queries.
- **Inherent assessment:** `CRITICAL / CONDITIONAL`.
- **Affected asset or claim:** `A01`, `A03`, `A07`; privacy and dependency-safe
  grouping.
- **Prevention:** random opaque IDs where possible; keyed HMAC only inside
  restricted preprocessing; separate key, mapping, and corpus; purpose-scope
  tokens; prohibit arbitrary queries; rotate/destroy under approved policy;
  never put a key, raw value, mapping, or lookup table in Git, logs, corpus, or
  prompts.
- **Detection:** secret scanning, access audit, canary attempts to place key-like
  material in permitted outputs, and reconciliation of token issuance with
  approved jobs.
- **Recovery:** revoke/rotate the key, isolate affected releases, regenerate
  scoped tokens/components, assess cross-release linkage, delete compromised
  mappings, and document participant/release implications.
- **Owners:** machine—restricted service and secret scanner; human—key custodian,
  steward, security lead.
- **Verification artifact:** secret-manager policy/reference, key-access log,
  rotation/destruction evidence, token-scope test, repository/log secret scan.
- **Residual risk:** algorithm, canonicalization, custodian, rotation, and
  destruction are current `UNKNOWN` blockers; deterministic tokens retain
  equality leakage even when the key is secure.

### TM-07 — Public-source authorization, license, or provenance laundering

- **STRIDE / ML class:** spoofing, repudiation, data poisoning.
- **Surface and precondition:** public availability, a citation, or an inherited
  label is mistaken for rights, safety, authenticity, or Fisher gold.
- **Inherent assessment:** `HIGH / PLAUSIBLE`.
- **Affected asset or claim:** `A02`, `A04`, `A11`; lawful use, provenance, and
  benchmark validity.
- **Prevention:** propose before acquisition; bind exact version/hash, terms,
  authoritative landing evidence, reviewer, permitted use, modification and
  release tier; independently reannotate from visible input; keep public direct
  and derived lineages only in `development`/`external_test`.
- **Detection:** governance cross-field and transitive-lineage validation;
  compare artifact hash and license text hash; audit original labels as hidden
  metadata; inspect source/template/campaign duplication.
- **Recovery:** block or withdraw the source; propagate restriction to every
  descendant; remove it from runs/releases; recompute components and results;
  correct the paper/data statement without erasing history.
- **Owners:** machine—governance/dataset validators; human—license reviewer,
  privacy reviewer, steward.
- **Verification artifact:** immutable source-ledger record, exact artifact and
  terms hashes, human rights decision, independent reannotation record.
- **Residual risk:** a syntactically valid official locator or recorded reviewer
  cannot prove legal rights, officialness, or source-label construct validity.

### TM-08 — LLM prompt/template contamination or synthetic-label leakage

- **STRIDE / ML class:** data poisoning, label leakage, benchmark gaming.
- **Surface and precondition:** prompts expose target labels, authentic content,
  provider-retained data, live artifacts, or repeated generation style; LLM
  descendants enter protected partitions or the LLM supplies gold.
- **Inherent assessment:** `HIGH / PLAUSIBLE`.
- **Affected asset or claim:** `A01`, `A02`, `A07`; privacy, gold validity, and
  generalization.
- **Prevention:** prompts contain no authentic donation, identifier, live route,
  secret, or protected example; retain prompt/model/batch lineage outside the
  semantic view; require material human editing and independent human labels;
  cap inherited LLM ancestry at 30% of retained development and pilot; prohibit
  it from all protected partitions.
- **Detection:** transitive ancestry checks, prompt-family component grouping,
  style/template duplicate analysis, provenance-disaggregated errors, and
  provider/data-handling review.
- **Recovery:** quarantine the generation family and descendants; rebuild
  components; remove contaminated protected records; invalidate affected runs;
  regenerate only under a new approved prompt and manifest.
- **Owners:** machine—lineage/partition validators; human—prompt reviewer,
  steward, annotation lead, provider-terms reviewer.
- **Verification artifact:** prompt-family manifest/hash, provider decision,
  human-edit record, ancestry report, LLM-share report, partition audit.
- **Residual risk:** stylistic artifacts can survive human editing and make
  development easier than tester data. Provider training/retention behavior may
  remain unknown.

### TM-09 — Hidden provenance, scenario, source label, or grouping key leaks into gold/model input

- **STRIDE / ML class:** information disclosure, target leakage, benchmark
  contamination.
- **Surface and precondition:** filenames, UI fields, feature positions,
  missingness bits, logs, or joins expose hidden generation/intent/provenance
  context to annotators or model conditions.
- **Inherent assessment:** `HIGH / PLAUSIBLE`.
- **Affected asset or claim:** `A02`, `A07`, `A09`; visible-input gold and causal
  factorial claims.
- **Prevention:** create a strict model-visible packet; use opaque IDs; separate
  authorization metadata from annotation/model stores; reject filename-derived
  labels; mask unavailable features rather than passing informative zeros;
  expose registry only to specified semantic conditions.
- **Detection:** schema-to-tensor provenance tracing, blinded UI review, canary
  hidden fields, feature-access tests, mutual-information diagnostics used only
  as alarms, and code review of joins/loaders.
- **Recovery:** invalidate labels/runs created under the leak; rebuild the view;
  reannotate affected items; retrain every dependent model from clean data.
- **Owners:** machine—data/feature pipeline maintainer; human—annotation lead,
  independent information-flow reviewer.
- **Verification artifact:** field-level data-flow manifest, UI capture, feature
  trace, masking tests, independent sign-off.
- **Residual risk:** annotators may infer likely provenance from wording even
  when metadata is hidden; inference must be analyzed, not represented as fully
  preventable.

### TM-10 — Poisoning or backdoor through messages, templates, campaigns, or labels

- **STRIDE / ML class:** tampering, training-data poisoning, backdoor.
- **Surface and precondition:** one actor can contribute repeated or coordinated
  examples, correlated trigger patterns, malicious labels, or disproportionate
  source families.
- **Inherent assessment:** `HIGH / PLAUSIBLE`.
- **Affected asset or claim:** `A02`, `A07`, `A09`; learned behavior and
  population generalization.
- **Prevention:** source authorization; per-family opaque lineage; connected
  components across author/donor/batch/template/campaign/artifact and all
  descendants; independent labels and final adjudication; source/cell caps and
  provenance-stratified reporting; no automatic demo-to-training feedback.
- **Detection:** influence/outlier and trigger-cluster analysis on development;
  disagreement/failure slices by source and component; duplicate/template scans;
  label-audit sampling; component-level sensitivity analysis.
- **Recovery:** quarantine the whole family, not a convenient row; correct
  lineage; reannotate; retrain clean systems; classify earlier results as
  invalid or exploratory.
- **Owners:** machine—dedup/component and analysis tools; human—steward,
  annotation lead, ML security reviewer.
- **Verification artifact:** component graph/hash, source contribution table,
  disagreement report, poisoning review, clean-retrain comparison.
- **Residual risk:** component construction cannot reconstruct an omitted hidden
  relationship, and sophisticated triggers may be indistinguishable from
  genuine dialect or campaign variation.

### TM-11 — Duplicate, lineage, author, or campaign leakage across partitions

- **STRIDE / ML class:** tampering, information disclosure, evaluation leakage.
- **Surface and precondition:** related rows receive different or incomplete
  keys, near duplicates evade canonical matching, or an analyst assigns
  components row by row.
- **Inherent assessment:** `CRITICAL / PLAUSIBLE`.
- **Affected asset or claim:** `A07`, `A09`; grouped-CV and protected-test
  independence.
- **Prevention:** compute transitive closure in restricted preprocessing over all
  authorized equivalence/lineage keys before splitting; one component enters one
  partition; every protected component is globally singleton and monostratal;
  reject parent/child component mismatch and partition crossings.
- **Detection:** exact, canonical, near-duplicate, semantic similarity, template,
  author, campaign, artifact and ancestry audits; holdout canaries; component
  yield report before partition freeze.
- **Recovery:** close missing edges, recompute the entire component graph and all
  partitions, invalidate any model that saw a newly connected protected item,
  and narrow independence claims when singleton yield fails.
- **Owners:** machine—restricted component builder and dataset validator;
  human—privacy steward and independent leakage reviewer.
- **Verification artifact:** input-edge manifest held outside the corpus,
  transitive component hash, partition manifest, singleton/monostratal audit.
- **Residual risk:** exact/canonical checks do not prove semantic independence;
  privacy minimization makes some linkage signals unavailable.

### TM-12 — Annotation manipulation, collusion, fatigue, or selective adjudication

- **STRIDE / ML class:** tampering, repudiation, label poisoning.
- **Surface and precondition:** annotators see each other’s work, share hidden
  context, are unqualified/overloaded, or difficult items are excluded after
  disagreement.
- **Inherent assessment:** `HIGH / PLAUSIBLE`.
- **Affected asset or claim:** `A02`, `A10`; ontology reliability and gold truth.
- **Prevention:** qualified language-matched adults; two independent blind
  records; one distinct final annotator for every attempt; immutable blind
  records; hidden provenance/coverage tags; frozen reserve order; workload,
  welfare, conflict, and break policy.
- **Detection:** exact annotator-cardinality/distinctness checks, agreement and
  completeness gates, per-annotator drift/disagreement review, audit supplements
  covering annotators, and attempted-item accounting including unresolved rows.
- **Recovery:** preserve original records; suspend affected wave; investigate
  conflicts; revise guide prospectively; reannotate every affected gate row and
  run a fresh confirmation wave where required.
- **Owners:** machine—dataset/reliability validator; human—annotation lead,
  native reviewer, welfare owner, independent auditor.
- **Verification artifact:** training/qualification evidence, blind assignment
  log, immutable annotation manifests, reliability report, audit supplement list.
- **Residual risk:** agreement can be high under a shared misunderstanding and a
  machine cannot judge linguistic truth or reviewer qualification.

### TM-13 — Structured-state coverage or audit sampling is gamed

- **STRIDE / ML class:** tampering, benchmark gaming, repudiation.
- **Surface and precondition:** candidate tags use hidden intent, easy rows are
  retained, manifests change after annotation, a seed is redrawn, or failed
  sampled items are replaced.
- **Inherent assessment:** `HIGH / PLAUSIBLE`.
- **Affected asset or claim:** `A02`, `A07`, `A11`; identifiable reliability
  metrics and pilot safety evidence.
- **Prevention:** coverage uses only immutable model-visible content and the
  frozen approved registry; tags are hidden non-gold; bind components/reserve
  order/hash before blind release; freeze bundle manifests before exactly one
  witnessed 32-byte OS-CSPRNG seed; no redraw or sample replacement.
- **Detection:** quota reconciliation by item and distinct component; manifest
  hash checks; deterministic Hamilton/HMAC replay; annotator supplements;
  append-only audit record; zero-finding gate.
- **Recovery:** any prohibited finding or sampling deviation fails the audit;
  quarantine affected families; repair upstream; freeze a new version; run a
  100% machine scan and a fresh independently seeded audit.
- **Owners:** machine—audit selector and manifest verifier; human—coverage
  steward, native reviewer, independent auditor and witness.
- **Verification artifact:** coverage manifest/hash, native-review decision,
  frozen universe hashes, seed/witness record, selector outputs, complete audit
  findings register.
- **Residual risk:** the selector proves arithmetic only; it cannot prove that
  the universe was complete, frozen before the draw, or reviewed honestly.

### TM-14 — Registry poisoning, incompleteness, staleness, or circular target construction

- **STRIDE / ML class:** tampering, spoofing, target leakage, semantic poisoning.
- **Surface and precondition:** unofficial evidence, an incomplete official page,
  a protected error, or a Fisher message changes an alias/entry; absence is
  converted to `MISMATCH`; a singular pair silently replaces a Cartesian
  inventory; opaque registry IDs become learned shortcut features; gold
  endpoints or a learned registry-state target are fed to a risk path that
  already consumes registry state.
- **Inherent assessment:** `CRITICAL / PLAUSIBLE`.
- **Affected asset or claim:** `A05`, `A07`, `A09`; actor–destination mechanism
  and causal semantics claim.
- **Prevention:** accept only frozen organization/government-controlled evidence;
  bind evidence, content, entry, source, and normalization hashes; require
  explicit scope/completeness; preserve `UNKNOWN`; prohibit message-, label-,
  error-, and protected-derived entries; freeze before protected access; blind
  semantic annotators/adjudicator to registry; construct a separate reference by
  a reviewer blind to label/provenance/protected outcomes; mechanically form
  Cartesian endpoint pairs; resolve bounded predicted endpoint sets at inference;
  canonicalize and hash the exact audit-packet UTF-8 bytes; cap it at 64 pairs
  and 16 MiB; keep endpoint scores as canonical finite binary64 bit strings only
  in the separately hashed prediction audit; resolve equal-score selection by
  emission index; reorder after score-based cap so rank cannot leak; project the
  exact E0 five-category binary64 grid to a fixed 31-dimensional masked tensor;
  and keep literal surfaces/evidence/snapshot/version/hash IDs out of learned
  features;
  short-circuit unaligned pairs before registry with `UNKNOWN`, engine-only
  `NOT_EVALUATED`, `ALIGNMENT_GUARD`, empty evidence IDs, and zero calls;
  prohibit candidate-offset back-projection and learned registry-state loss.
- **Detection:** independent source-authority/completeness review; stale/expired
  evidence queue; snapshot/hash/access traces; canaries proving `C00`/`C10`,
  capacity controls, and masked risk paths receive no endpoint, packet, plan,
  projected token, registry value, or missingness; predicted-`VMP`-endpoint-only,
  Cartesian-packet, exact audit-to-feature projection/mask,
  literal-surface/ID/score/rank/`q` nonexposure, and no-learned-relation-loss
  audits.
- **Recovery:** retire evidence only in a new version; never silently mutate the
  confirmatory artifact; invalidate affected annotation/model runs; classify a
  later version as exploratory.
- **Owners:** machine—manifest binding and feature-access checks; human—registry
  authority/completeness reviewer and causal-design reviewer.
- **Verification artifact:** registry artifact/manifest/audit package, evidence
  hashes and excerpts, completeness decision, version-diff, target/feature flow
  test.
- **Residual risk:** official sources may be incomplete or change. The method
  boundary and historical schema `1.1.0` repair exist, and current schema
  `1.2.0` has the scoped `E09` syntactic pass. No registry or engine exists, and
  fresh review of the reconciled endpoint, packet, exact E0 feature audit,
  metric-universe binding, and condition contracts remains a `P0` blocker.

### TM-15 — Transliteration-resource poisoning, candidate suppression, or calibration leakage

- **STRIDE / ML class:** tampering, backdoor, evaluation leakage.
- **Surface and precondition:** paired data contain poisoned mappings, duplicate
  families cross transliteration partitions, acceptable forms change after
  failures, or phishing/protected labels update candidate weights.
- **Inherent assessment:** `HIGH / PLAUSIBLE`.
- **Affected asset or claim:** `A06`, `A09`; uncertainty-marginalization mechanism
  and candidate-coverage evidence.
- **Prevention:** exact resource/version/license/file hashes; group-disjoint
  transliteration development, message-level temperature calibration, and
  evaluation; at most eight candidates per span and eight returned message
  paths; complete per-code-point `VMP` alignment; no rewrite/artifact overlap;
  mechanically defined `(normalized text, alignment)` merge identity;
  alignment-aware normalization; overflow-safe exact/beam selection; exactly one
  frozen `COMPOSED_SPAN|DIRECT_FULL_PATH` provider/configuration shared by all
  four cells, rank one active for `C00`/`C01`, all returned paths active for
  `C10`/`C11`, and `IDENTITY_BYPASS` only as a
  candidate-output artifact; immutable `(unit_index,provider_rank)` identities;
  1..64 manifest-bound artifact-disjoint rewrite spans with non-Boolean,
  in-range coordinates for successful composed/direct output, no effective span
  for bypass, and attempted spans retained separately on provider failure;
  direct preservation of non-rewrite/artifact content; bounded
  manifests/readings/paths; compact contributor lineage; canonical
  binary64 LSE operand order; exact stage-reduction accounting; one scoped
  log-domain retained-mass field; exact runtime-bound `q` numerators,
  normalizer, maximum, and signed-zero rules; human
  acceptable-form adjudication; freeze generator, normalizer, `T_tr`, and the
  two explicit bypasses before phishing training; bind source/runtime,
  provider-execution cause/configuration/spans, candidate paths, complete
  executed-source/system-artifact identity, and downstream hashes in the
  schema-1.1 engine run envelope after the path-free canonical input descriptor
  and one-code `PASS` preflight receipt; fail invalid eligibility selection
  before provider dispatch without retaining unsafe spans; allow
  only `DEGRADED_STOP_AFTER_IDENTITY` for unavailable/timeout before accepted
  nonidentity output plus a validated identity fallback, with no prediction;
  reject
  malformed/nonfinite/alignment-invalid output as invalid; never count fallback
  as coverage success or admit it to confirmatory/protected metrics; never use
  protected labels/gradients for `q_k`.
- **Detection:** group-leakage and duplicate audits; candidate rank/logit/schema
  validation; acceptable-form correction history; per-language coverage/NLL;
  backdoor/trigger slices; gradient and data-access traces.
- **Recovery:** exclude or version the resource; rebuild candidates/calibration;
  invalidate downstream models and protected eligibility; narrow the uncertainty
  claim if coverage gates fail.
- **Owners:** machine—resource/candidate validator and training pipeline; human—
  license reviewer, native-language adjudicator, independent resource reviewer.
- **Verification artifact:** governed resource manifest, partition/group hash,
  provider-reading manifest, system-artifact manifest/schema-1.1 run envelope, candidate
  records, `T_tr` fit log, coverage/NLL report, no-protected-access trace.
- **Residual risk:** linguistic acceptability and resource bias are human
  judgments; no paired resource is currently ingested or audited.

### TM-16 — Malicious dependency, checkpoint, serialized object, or custom model code

- **STRIDE / ML class:** elevation of privilege, tampering, supply-chain attack.
- **Surface and precondition:** a mutable package/model revision or unsafe
  deserializer executes code during install, load, preprocessing, or inference.
- **Inherent assessment:** `CRITICAL / PLAUSIBLE` once model work begins.
- **Affected asset or claim:** `A01`, `A03`, `A08`, `A09`; host/repository
  integrity, secrets, data, and reproducibility.
- **Prevention:** allowlist sources and packages; pin exact versions/revisions and
  hashes; review licenses; build in an isolated least-privilege offline
  environment; prohibit remote custom-code execution; prefer non-executable
  weight formats; no secrets or raw data in build/training environments unless
  explicitly required and isolated.
- **Detection:** dependency lock/hash verification, signature/provenance checks
  where available, static review of custom code, malware scan, network-denial
  test, software-bill-of-materials diff, and clean-environment reproduction.
- **Recovery:** disconnect and preserve minimal forensic evidence; rotate exposed
  secrets; rebuild from a trusted base; revalidate artifacts/results; invalidate
  any run whose environment integrity is uncertain.
- **Owners:** machine—build/CI integrity checks; human—security and dependency
  reviewers.
- **Verification artifact:** lockfile/SBOM, package/model hashes, approved-source
  list, sandbox/network trace, clean-build attestation.
- **Residual risk:** no ML dependency environment or checkpoint is currently
  pinned, and upstream compromise cannot be eliminated by hashes chosen after
  acquisition.

### TM-17 — Training-time exfiltration through logs, caches, checkpoints, or model prompts

- **STRIDE / ML class:** information disclosure, membership leakage.
- **Surface and precondition:** data loaders, exception traces, experiment tools,
  model artifacts, or third-party services retain raw/de-identified examples,
  identifiers, keys, or predictions.
- **Inherent assessment:** `CRITICAL / CONDITIONAL`.
- **Affected asset or claim:** `A01`, `A02`, `A03`, `A08`.
- **Prevention:** local/offline training; sanitized diagnostics; no raw text in
  logs/run names; no external inference or experiment API; separate restricted
  preprocessing; minimize checkpoint metadata; scope caches; encrypt and
  access-control research artifacts; prohibit secrets and raw donations in Git.
- **Detection:** repository, log, cache, checkpoint-metadata, crash-dump, and
  outbound-network scans; canary identifiers that must never appear outside the
  restricted zone.
- **Recovery:** revoke access, quarantine artifacts, rotate secrets, purge
  approved caches/backups under policy, retrain if model leakage is material,
  and execute incident notification requirements.
- **Owners:** machine—logging/artifact and egress controls; human—security lead,
  steward, model-release reviewer.
- **Verification artifact:** egress-denial trace, secret/raw-text scan, artifact
  inventory, access log, deletion evidence.
- **Residual risk:** checkpoints can memorize rare text even without literal log
  leakage; the disclosure test and retention/retraining policy remain `UNKNOWN`.

### TM-18 — Factorial information-flow, supervision, or capacity contamination

- **STRIDE / ML class:** tampering, target leakage, causal benchmark gaming.
- **Surface and precondition:** no-semantic conditions receive registry/semantic
  endpoint/pair signals, masked fields leak missingness, controls have inactive
  parameters, path losses differ, or tuning/update budgets differ.
- **Inherent assessment:** `HIGH / PLAUSIBLE`.
- **Affected asset or claim:** `A08`, `A09`; H1/H2 and semantic-mechanism claims.
- **Prevention:** frozen field-level condition contract; identical visible input,
  encoder, candidate ordering, seeds, tuning and update budgets; exact active
  parameter matching; rank-1 `C01` versus q-weighted `C11` auxiliary losses;
  supervision-matched output blocking; registry and endpoint/pair packets
  inaccessible to no-semantic paths.
- **Detection:** feature-access and gradient traces, tensor canaries, parameter
  participation tests, update/token/trial accounting, registry-call audit, and
  independent causal-control review.
- **Recovery:** classify the run as a protocol deviation; repair the condition
  interface; retrain all affected cells/controls before protected access.
- **Owners:** machine—training/information-flow test owner; human—independent ML
  methods reviewer.
- **Verification artifact:** per-condition manifest, feature/gradient trace,
  parameter and compute table, registry access log, reviewer decision.
- **Residual risk:** equal parameter count does not guarantee equal effective
  capacity or optimization difficulty; mechanism interpretation remains
  conditional on the controls.

### TM-19 — Calibration, safety-threshold, or score-boundary manipulation

- **STRIDE / ML class:** tampering, benchmark gaming.
- **Surface and precondition:** systems share a temperature/threshold, calibrate
  a common delta rather than averaged path logits, combine calibrated entropy
  with raw-logit disagreement, use protected labels, drop nonfinite paths, alter
  dtype/ties, or adjust after primary results.
- **Inherent assessment:** `CRITICAL / PLAUSIBLE`.
- **Affected asset or claim:** `A07`, `A09`; locked low-FPR operating point and
  co-primary recall contrasts.
- **Prevention:** average five fixed logits for every path; fit one positive
  scalar temperature per system only on `probability_calibration`; compute
  calibrated path probabilities, `q`-weighted risk, entropy, and disagreement
  from the same object; derive each system’s float64 `nextafter` threshold only
  from benign `safety_threshold`;
  freeze exact bit patterns, IDs, comparison rule, and artifacts before primary
  access; any nonfinite score invalidates the run.
- **Detection:** recompute from immutable logits; cross-system ownership checks;
  bitwise threshold/tie tests; partition-access trace; manifest comparison before
  and after protected access.
- **Recovery:** invalidate the system/family; restore pre-access artifacts or
  rebuild prospectively; never repair a confirmatory threshold using primary
  outcomes.
- **Owners:** machine—calibration/evaluation pipeline; human—statistical lead and
  protected-access custodian.
- **Verification artifact:** logit hash, temperature fit record, maximum benign
  record ID/score bits, threshold bits, dtype/runtime manifest, access audit.
- **Residual risk:** a correctly locked threshold may still generalize poorly.
  H1/H2 remain own-policy recall comparisons, never common-FPR dominance or a
  safety-superiority claim; exact scalar-optimizer behavior is not yet frozen.

### TM-20 — Premature, repeated, or indirect protected-set access

- **STRIDE / ML class:** information disclosure, elevation of privilege,
  evaluation overfitting.
- **Surface and precondition:** a person, job, cache, dashboard, error log, or
  derived aggregate reveals protected text, labels, scores, or errors before
  freeze or permits repeated confirmatory attempts.
- **Inherent assessment:** `CRITICAL / PLAUSIBLE`.
- **Affected asset or claim:** `A07`, `A09`, `A11`; confirmatory validity.
- **Prevention:** physically/logically separate protected stores; least-privilege
  custodian; sequential authorization for probability calibration, threshold,
  and exactly one primary execution; immutable code/model/analysis hashes;
  outputs released only after run lock; no exploratory UI over protected data.
- **Detection:** append-only access/job logs, access canaries, artifact timestamps
  and hashes, one-run nonce/authorization record, review of caches and failed jobs.
- **Recovery:** presume contamination; block confirmatory claims; investigate
  exposure; use only an independently reserved replacement set if one was
  prospectively authorized, otherwise route results to exploratory status.
- **Owners:** machine—access-control/run orchestration; human—protected-set
  custodian, research lead, independent auditor.
- **Verification artifact:** access-control matrix, unopened-state attestation,
  authorized run manifest, complete access/job log, post-run seal.
- **Residual risk:** a person can remember information, and aggregate feedback
  can leak test behavior. No protected partitions currently exist, so controls
  remain required rather than verified.

### TM-21 — Selective-abstention abuse or unequal coverage

- **STRIDE / ML class:** denial of service, fairness harm, metric gaming.
- **Surface and precondition:** a system abstains disproportionately on a language,
  provenance group, authentic donations, or difficult attacks, or removes
  abstained records from primary recall/FPR denominators.
- **Inherent assessment:** `HIGH / PLAUSIBLE`.
- **Affected asset or claim:** `A09`, `A11`; usable coverage, subgroup safety,
  and H5/selectivity claims.
- **Prevention:** freeze `u(x)` and exact 80%/90% calibration cutoffs before
  primary access; keep selective analysis secondary; never delete, replace, or
  complete-case-filter a primary record; report coverage and risk by stratum and
  provenance; no automated “safe” label for an abstention.
- **Detection:** risk–coverage curves, AURC, coverage parity diagnostics, abstain
  confusion matrices, hard-slice review, and provenance/language disaggregation.
- **Recovery:** narrow the selectivity claim; revise only in a new exploratory
  version; route abstentions to human review in the demo without implying safety.
- **Owners:** machine—evaluation pipeline; human—methods, fairness, and HCI
  reviewers.
- **Verification artifact:** cutoff manifest, full-denominator primary table,
  subgroup coverage/risk report, abstention error analysis.
- **Residual risk:** equal coverage does not establish equal harm; four strata do
  not cover all Indian languages, dialects, or user populations.

### TM-22 — Metric, resampling, or result-manifest manipulation

- **STRIDE / ML class:** tampering, repudiation, benchmark gaming.
- **Surface and precondition:** IDs are sampled inconsistently across systems,
  failed runs are deleted, hypotheses/slices change, multiplicity or bootstrap
  tails are altered, or rounded values determine success.
- **Inherent assessment:** `HIGH / PLAUSIBLE`.
- **Affected asset or claim:** `A09`, `A11`; co-primary and secondary inference.
- **Prevention:** preregister estimands, signs, seeds, child streams, tie rules,
  order statistics, invalidity handling, multiplicity, and practical-effect
  gates; use identical paired IDs; preserve all failures; separate confirmatory
  and discovery analyses.
- **Detection:** independent formula/code review, synthetic null/known-answer
  tests, deterministic replay and checksums, raw-versus-table reconciliation,
  and deviation audit before protected access.
- **Recovery:** correct code before protected access; after access, preserve the
  original output and mark corrected analysis/deviation transparently; block the
  original confirmatory claim when the frozen rule was not followed.
- **Owners:** machine—statistics pipeline; human—statistical lead and independent
  reviewer.
- **Verification artifact:** analysis manifest/code hash, known-answer test
  report, raw predictions/effects, sorted-order checksum, deviation register.
- **Residual risk:** current H4 resampling, empirical power generator, and exact
  FPR claim-routing rule remain `UNKNOWN` and must freeze before protected use.

### TM-23 — Manifest, artifact, or history tampering and rollback

- **STRIDE / ML class:** tampering, repudiation.
- **Surface and precondition:** a mutable file is reused under an old identifier,
  a hash is omitted/recomputed after review, history is rewritten, or code/data
  and approval refer to different versions.
- **Inherent assessment:** `HIGH / PLAUSIBLE`.
- **Affected asset or claim:** `A04` through `A09`; reproducibility, approvals,
  and chain of custody.
- **Prevention:** immutable unique IDs; content hashes for data, evidence,
  registry, resources, configs, code, predictions, and outputs; append-traceable
  corrections; atomic run manifests; read-only frozen artifacts; independent
  approval bound to exact hashes.
- **Detection:** full dependency-graph verification, hash replay, duplicate-ID
  and supersession checks, timestamp/access review, and environment recreation.
- **Recovery:** quarantine the mismatched artifact; restore from a trusted frozen
  copy; create a new version and revision record; invalidate downstream evidence
  whose dependency hash cannot be proven.
- **Owners:** machine—artifact/manifest verifier; human—artifact custodian,
  research lead, release auditor.
- **Verification artifact:** signed or access-controlled manifest bundle,
  dependency hash graph, append-only correction record, reproduction report.
- **Residual risk:** hashes prove byte equality, not truth or pre-hash integrity;
  one repository snapshot cannot prove append-only history.

### TM-24 — Membership inference, extraction, or unsafe model release

- **STRIDE / ML class:** information disclosure, model privacy attack.
- **Surface and precondition:** checkpoints, logits, embeddings, per-example
  predictions, an unrestricted demo, or detailed examples are released.
- **Inherent assessment:** `CRITICAL / CONDITIONAL`.
- **Affected asset or claim:** `A01`, `A02`, `A08`, `A11`; participant privacy
  and IP.
- **Prevention:** no public inference endpoint; offline bounded demo with
  synthetic or release-authorized examples; default to aggregates; checkpoint
  and per-example output release requires separate privacy, rights, misuse, and
  IP review; suppress rare or identifying examples.
- **Detection:** membership/extraction red-team on development-only surrogates,
  nearest-neighbor memorization review, output-query budget review, and release
  inventory scan.
- **Recovery:** do not release or withdraw the affected artifact where possible;
  rotate access; notify under policy; publish a corrected data/model statement;
  retrain with an approved mitigation only as a new version.
- **Owners:** machine—release scanner and demo access control; human—privacy,
  security, IP, and release reviewers.
- **Verification artifact:** privacy attack report, release bill of materials,
  example-level disclosure audit, written release decision.
- **Residual risk:** empirical privacy attacks cannot prove absence of membership
  leakage. No checkpoint release is authorized by Paper 1 planning.

### TM-25 — Offline demo activates artifacts, leaks data, or misstates confidence

- **STRIDE / ML class:** information disclosure, elevation of privilege, unsafe
  HCI, repudiation.
- **Surface and precondition:** the demo accepts arbitrary input, renders active
  links/previews, makes a network call, invokes an LLM, exposes hidden metadata,
  or describes calibrated probability as guaranteed safety.
- **Inherent assessment:** `CRITICAL / CONDITIONAL`.
- **Affected asset or claim:** `A01`, `A02`, `A08`, `A10`, `A11`.
- **Prevention:** local offline static/batch demo; only synthetic or expressly
  release-authorized defanged fixtures; inert rendering; network denied; no
  inference LLM or generative explanation; bounded structured evidence; visible
  “research prototype—not protection” label; no automatic storage or feedback.
- **Detection:** egress trace, UI link/preview tests, fixture allowlist/hash,
  hidden-field inspection, accessibility and warning-comprehension review,
  artifact/secret scan of the built package.
- **Recovery:** disable the demo; quarantine captured input/build logs; remove
  unsafe fixture or dependency; rebuild and re-review before any showing.
- **Owners:** machine—demo build/runtime maintainer; human—security, privacy, HCI,
  and release reviewers.
- **Verification artifact:** offline/egress test, rendered UI review, fixture
  manifest, package scan, approved prototype disclaimer.
- **Residual risk:** observers may still overgeneralize a convincing demo; demo
  quality cannot substitute for measured protection.

### TM-26 — Publication, benchmark, or artifact release causes privacy, rights, IP, or safety harm

- **STRIDE / ML class:** information disclosure, repudiation, benchmark gaming.
- **Surface and precondition:** manuscript examples, tables, appendix, code,
  dataset, model, or preprint are disclosed before rights, privacy, IP, name,
  venue, and claim-routing gates pass.
- **Inherent assessment:** `CRITICAL / PLAUSIBLE`.
- **Affected asset or claim:** `A01`, `A02`, `A04`, `A08`, `A11`.
- **Prevention:** embargo by default; professional filing/no-filing/defer and
  name decisions; release-tier reconciliation; aggregate and provenance-
  disaggregated reporting; remove operational indicators; no “first,” “SOTA,”
  patentability, field-prevalence, below-1%, or production claim without its
  exact evidence gate.
- **Detection:** independent paper-to-manifest traceability review, privacy and
  rights scan, claim-evidence matrix, venue-policy check, secret/live-artifact
  scan, and reproduction from the frozen package.
- **Recovery:** stop disclosure; correct or retract unsupported material; notify
  affected parties/venue under approved policy; preserve the original record and
  explanation rather than silently replacing it.
- **Owners:** machine—release/claim scanner; human—research lead, privacy/data-
  rights reviewer, professional IP counsel, venue/release owner.
- **Verification artifact:** publication/IP gate decision, claim-evidence matrix,
  data/model card, release manifest, rights/privacy approvals, reproduction log.
- **Residual risk:** publication is effectively irreversible and can enable
  misuse or re-identification through combination with outside information.

### TM-27 — Insider privilege misuse or separation-of-duties collapse

- **STRIDE / ML class:** elevation of privilege, spoofing, repudiation,
  information disclosure.
- **Surface and precondition:** one account can intake raw data, approve it,
  manage equivalence secrets, annotate, access protected labels, alter results,
  and authorize release.
- **Inherent assessment:** `CRITICAL / PLAUSIBLE` without operational controls.
- **Affected asset or claim:** all assets, especially `A01`, `A03`, `A07`, `A09`.
- **Prevention:** least privilege; separate steward, de-identification reviewer,
  annotator, adjudicator, auditor, analyst, protected custodian, and release
  reviewer; two-person approvals for high-impact transitions; time-bounded
  access; no shared accounts.
- **Detection:** immutable role/access logs, periodic entitlement review,
  conflicting-role checks, unusual access/job alerts, and independent audit.
- **Recovery:** suspend access, preserve minimal logs, rotate keys, revalidate
  every artifact the role could modify, and repeat affected approvals/runs under
  independent control.
- **Owners:** machine—identity/access system; human—accountable institution,
  security lead, independent auditor.
- **Verification artifact:** role matrix, named assignments, access-review log,
  two-person approvals, incident exercise.
- **Residual risk:** all accountable role holders and the operational access
  system are currently `UNKNOWN`; research documentation alone cannot enforce
  separation.

## 8. Safe abuse cases and expected control outcomes

These cases describe defenses without supplying live indicators or executable
attack procedures.

| Abuse case | Expected safe outcome |
| --- | --- |
| a submitted string disguises a route with Unicode separators or an IDN label | reject/quarantine without echoing or resolving it; second human review remains mandatory |
| a researcher pastes a raw donation into Git, chat, a ticket, or a run name | treat as an incident, restrict copies, invoke deletion/notification policy, and scan derivatives |
| one tester submits many related paraphrases or simulations | join author/scenario/template family into one component; prevent protected use of a nonsingleton family |
| a public dataset’s filename and spam label imply permission and phishing gold | keep blocked until exact rights/audits pass; hide source label and independently annotate visible content |
| an LLM draft reflects a prompt’s target label or repeated template | hide prompt/intent, require human edit and independent labels, group the prompt family, prohibit protected ancestry |
| a registry item is missing or official evidence is incomplete | return `UNKNOWN`; never infer `MISMATCH` from absence |
| a model package requests custom code or an unpinned mutable revision | refuse it pending isolated review and immutable pinning; do not load it around restricted data |
| an analyst requests a second primary-test run after inspecting errors | deny confirmatory reuse; log the request and route any later run to exploratory status unless a prospectively reserved set exists |
| abstention removes most difficult examples in one stratum | retain every primary denominator; report stratum coverage/risk and block a broad selectivity claim |
| a demo user supplies arbitrary content or expects a safety decision | do not accept/store it; use allowlisted fixtures and display the prototype/non-protection boundary |

## 9. Security invariants

An invariant failure is a stop condition, not a warning to waive.

1. **`INV-01 Raw-zone isolation`:** no raw donation, participant identity,
   consent form, live artifact, reversible mapping, or secret/key enters Git,
   chat, issue trackers, shared logs, model prompts, annotation storage, or a
   release artifact.
2. **`INV-02 Inert artifacts`:** annotation, validation, modeling, auditing, and
   demo never visit, resolve, call, message, execute, redirect through, install,
   or open an artifact.
3. **`INV-03 Fail-closed safety`:** a high-confidence route, credential, OTP,
   identifier, unsafe attachment reference, or contradictory authorization
   causes quarantine; it is never downgraded to a warning.
4. **`INV-04 Restricted equivalence`:** only the restricted preprocessing zone
   sees raw equality inputs, keys, or mappings; corpus-visible IDs are opaque and
   purpose-scoped.
5. **`INV-05 Visible-input gold`:** VMP is exactly schema-1.2 `item.text` plus
   non-gold pre-annotation `item.visible_artifacts`, bound by `vmp_sha256` and
   never constructed from annotations. Semantic labels, spans, facets,
   supporting evidence, and actor/destination endpoints use only that immutable
   `VMP`.
   Registry state is a separate Cartesian compatibility reference, never blind
   human gold or a human pair link; provenance, prompt, scenario, source label,
   and author intent never decide gold.
6. **`INV-06 Immutable lineage`:** public and LLM ancestry propagates through
   every descendant; relationships cannot be erased by changing an immediate
   provenance field.
7. **`INV-07 Component confinement`:** no component crosses active partitions;
   each protected component is globally singleton and monostratal.
8. **`INV-08 Protected provenance`:** no public or LLM ancestry enters
   `probability_calibration`, `safety_threshold`, or `primary_test`; primary test
   is tester-originated and follows the authentic-donation cell gate.
9. **`INV-09 Offline evidence`:** registry, annotation, model, evaluation, and
   demo perform no network lookup. Registry inputs are frozen, hashed, read-only,
   and independent of protected outcomes.
10. **`INV-10 Unknown is not mismatch`:** absence, incomplete coverage, conflict,
    staleness, or an unaligned lookup cannot produce a confirmatory `MISMATCH`.
    Unaligned pairs take the zero-call `ALIGNMENT_GUARD` short-circuit; an empty
    Cartesian product makes no call/row and is implicit `N/A`.
11. **`INV-11 Frozen candidate posterior`:** phishing labels or protected data do
    not fit, select, rerank, or recalibrate transliteration candidates or `q_k`;
    complete mechanical `VMP` alignment and alignment-aware normalization,
    one frozen provider/configuration across the four factorial cells with
    rank-one versus all-path activation only, exact non-Boolean in-range
    rewrite coordinates, canonical provider-reading manifest/hash and enclosing
    provider-execution object,
    `(unit_index,provider_rank)` contributor lineage, bounded outputs,
    canonical binary64 LSE/order/merge reductions, single scoped log-domain
    retained mass, exact runtime-bound `q` arithmetic, merge identity, and
    explicit bypass/degraded/invalid status are frozen.
12. **`INV-12 No inference LLM`:** no LLM receives inference input, produces the
    phishing decision, or generates the displayed explanation.
13. **`INV-13 Condition isolation`:** `C00`/`C10` and capacity controls have no
    endpoint/pair, semantic, or registry input, missingness, prediction,
    gradient, or lookup; supervision-control risk paths receive no endpoint/pair
    output, audit packet, feature plan/token, or semantic output.
14. **`INV-14 Per-system lock`:** every trainable system uses all frozen seeds,
    owns its scalar calibration and benign-only threshold, preserves boundary
    bits, and receives no post-primary adjustment.
15. **`INV-15 One-way protected access`:** protected access follows the approved
    sequence and the primary evaluation executes once under immutable manifests.
16. **`INV-16 Complete primary denominators`:** the complete pre-frozen named
    canonical evaluation-universe manifest/hash equals the entire eligible
    nonempty named-partition closure of one to 10,000 items and binds each
    canonical gold inventory byte length/hash. A deterministic strict universe
    receipt precedes submission preflight; both structural passes precede
    semantic closure. Either preflight failure emits only its bounded receipt.
    A structurally valid but semantically invalid universe takes the exact
    universe-error short-circuit without opening an envelope. Otherwise the discriminated metric-run manifest binds one
    valid engine envelope per item in order or applies the frozen duplicate/
    extra/reorder/exclusive-outcome counts plus disjoint universe and declared-
    denominator error counts. Natural zero pair-metric denominators return
    canonical `+0.0`, not a denominator-binding error.
    `pair_emptiness_accuracy` has a positive denominator on every valid run.
    A missing, extra, reordered, degraded, nonfinite, abstained, malformed, or
    inconvenient record fails the applicable run and is never silently deleted.
    Registry-reference bundle and inference snapshot/resolver/artifact hashes
    must match even for zero-pair items.
17. **`INV-17 Traceable artifacts`:** every result resolves to exact code, data,
    registry, resource, model, config, seed, environment, and analysis hashes.
    The `SystemArtifactManifest` derives a complete executed-source closure and
    the canonical five-seed artifact binds active paths and binary64 means.
    Endpoint cap/tie/pre-cap/cap-hit, provider execution/manifest/ranks/lineage,
    alignment encoding/hash, source/runtime/float/math-backend contract, exact
    merge reductions, retained-mass/`q` binary64 bits, active paths, lookup status, canonical
    prediction-audit/packet/call-count/E0 feature-tensor hashes,
    engine-input/preflight, registry-reference-bundle/evaluation-universe,
    metric-universe/input-receipt/metric-run hashes, and bypass/degraded status are
    manifested. Endpoint scores remain in the exact
    separate prediction audit. Literal surfaces,
    identifiers, hashes, evidence, scores, ranks, `q`, and score order never
    enter learned semantic features.
18. **`INV-18 Bounded claim`:** every public claim maps to a passed gate; the
    prototype label remains visible and no release is inferred from a machine
    validator pass.

## 10. Required negative and adversarial tests

All tests use synthetic, reserved, or separately authorized inert fixtures. They
must not contain a live indicator or operational attack instruction.

| Test family | Required negative cases | Passing evidence |
| --- | --- | --- |
| strict ingestion | malformed UTF-8/JSON, duplicate keys, nonfinite values, blank/nonobject rows, unknown fields, Boolean-as-integer, depth/member/record/line/file limits | deterministic sanitized diagnostics; whole invalid record excluded |
| artifact safety | reserved versus active-route-shaped fixtures; Unicode-dot/IDN, email, IP, phone, credential/OTP, identifier and attachment-reference classes; keys as well as values | active shapes quarantine; reserved/approved defanged fixtures remain inert; no matched content echoed |
| Unicode/offsets | NFC/NFD, compatibility forms, combining marks, bidi/control, mixed scripts, emoji, Unicode whitespace, homoglyph and truncation boundaries | exact raw hash/substring/offset round trip; cross-tool decisions agree or fail closed |
| provenance and lineage | missing/duplicate/cyclic parents, false transitive flags, public/LLM descendant relabeling, source partition excess, withdrawn source | graph/partition validation rejects every policy bypass |
| components | exact/canonical/near duplicate, paraphrase/translation/template/author/artifact relatives, excluded relative attached to protected row | one transitive component; no active split crossing; protected family rejected unless globally singleton |
| annotation | hidden provenance/registry canary, nonblind pair, reused final annotator, missing final, selective exclusion, broken spans/evidence/endpoints, blind relation label, undefined reliability denominator | forbidden field remains inaccessible; exact cardinality and endpoint reliability gates fail closed |
| coverage/audit | under-quota cell, changed hash, post-freeze universe mutation, alternate seed/redraw, sample replacement, unavailable annotator supplement | deterministic replay detects deviation and release stays blocked |
| engine/metric envelopes | filesystem-bound or noncanonical engine descriptor, ambiguous duplicate/nonfinite/parser precedence, pre-system or pre-VMP failure forced into run envelope, invalid eligibility selector reaching provider dispatch, invalid provider outcome with accepted hash, later-stage loss of validated upstream objects, stale E0 envelope version, overlapping failure codes, malformed/oversized/non-UTF-8/duplicate/nonfinite/non-NFC/noncanonical universe or metric descriptor forced into a run manifest, partial universe-entry counting, semantic-invalid or empty universe used as `E`, wrong universe/submission/semantic precedence, duplicate/extra/reorder/status double counting, missing universe/denominator diagnostic, natural zero pair denominator mislabeled invalid | path-free bounded one-code engine preflight or strict one-code universe receipt and constructible schema-1.1 envelope selected exclusively; earliest stage, receipt counts/hashes, empty-universe short-circuit, and safe-unit counts reproduce; required expanded metric example and `+0.0` algebra are exact; no unsafe content or metric leaks |
| registry | unbound/stale snapshot, incomplete evidence, protected-derived alias, singular-pair collapse, wrong packet/plan fields/order/bytes, unsafe or excess evidence ID, packet overflow, call-count mismatch, missing/ambiguous prediction-audit binary64 score/index/tie, endpoint score or score-order leak, wrong E0 basis/mean/mask/tensor bytes, unaligned lookup reaching registry, `UNKNOWN -> MISMATCH`, literal-surface/ID/hash feature canary, learned registry-state loss, gold/candidate-offset endpoint inference, registry input to no-semantic/masked risk, inference/reference bundle mismatch including zero-pair, incomplete/oversized/unbound gold inventory, evaluation-universe omission/deletion/reordering, valid-versus-invalid metric-union confusion | reference/run rejected; version mutation becomes exploratory; only the exact projected plan/tokens reach risk; unaligned pair makes zero registry calls |
| transliteration | mixed provider configurations, provider/config mismatch across factorial cells, wrong rank-one/all-path activation, missing/ambiguous provider-execution or schema-1.1 engine envelope, incomplete executed-source/system binding, malformed/oversized provider manifest, invalid ID/mode/unit/rank/f64 bits, Boolean/out-of-range rewrite coordinate, lost attempted span on failure, invalid output mislabeled degraded, text-only duplicate merge, invalid/incomplete or nonmechanical alignment, normalization without transformed alignment, rewrite/artifact overlap, duplicate/mutable raw identity, wrong contributor/LSE operand order or stage-reduction count, exponential lineage expansion, cross-partition group, altered non-span code points, output/path/manifest overflow, overflowed exact/beam branch, wrong partial merge/prune order, signed-zero/nonfinite drift, direct-exp underflow, positive retained-mass delta, wrong `preK_scope`, stale dual mass field, wrong `q` numerator/normalizer/order, beam falsely reported as total-lattice mass, missing acceptable top-K, protected-driven reference addition, invalid/empty bypass, provider failure counted as coverage or admitted to protected metrics | composition, alignment, numeric, log-mass, schema, bound, envelope, or coverage gate fails; `q_k` and bypass cause reproduce from the bound source/runtime/math backend and exact run envelope only |
| supply chain | altered package/checkpoint hash, custom-code request, unsafe serializer, unexpected network attempt, dependency/version drift | load/build refused; egress denied; clean pinned rebuild reproduces |
| training information flow | hidden-field/registry tensor canaries, inactive capacity-match parameters, unmatched updates/trials, log/cache raw-text canary | no forbidden signal or raw text appears; active parameter/budget traces match |
| calibration/threshold | shared temperature, per-seed/per-language calibration, wrong partition, NaN, exact maximum/equality, dtype or bit-pattern change, post-lock mutation | per-system recomputation is bitwise consistent; prohibited variant invalidates run |
| protected access | unauthorized/pre-freeze job, failed job with partial output, repeated primary invocation, cached protected error view | job denied or family invalidated; append-only access record proves one authorized run |
| selectivity/statistics | abstention complete-case deletion, empty subgroup, sign/tail reversal, inconsistent paired IDs, failed-resample deletion, changed multiplicity | known-answer tests and deterministic replay match preregistration; invalid family fails |
| demo/release | arbitrary input, active rendering, preview/network request, inference-LLM call, hidden metadata, raw/log secret, unsupported safety claim | input refused, network denied, inert output, package/claim scan passes |

Passing these tests establishes only the named implementation property. It does
not establish ethics, linguistic validity, source truth, real-world robustness,
or production security.

## 11. Incident and quarantine flow

The following sequence applies to suspected live artifacts, prohibited data,
unauthorized collection, key exposure, source/label poisoning, partition
leakage, protected access, malicious dependency behavior, and release defects.

1. **Stop:** halt the current job or review without opening, resolving, copying,
   or echoing the suspect value.
2. **Contain:** restrict the record, source, leakage family, dependent manifests,
   caches, checkpoints, predictions, paper excerpts, and release copies.
3. **Notify:** use the approved secure channel to contact the named steward and
   incident lead. Do not put the prohibited value in a ticket, chat, or email.
4. **Preserve minimally:** retain only sanitized diagnostic codes, safe opaque
   identifiers, affected artifact hashes, times, roles, and access/job evidence
   necessary for review.
5. **Assess lineage:** trace raw, transformed, translated, transliterated,
   annotated, cached, trained, backed-up, demonstrated, and released descendants.
6. **Classify impact:** identify participant/privacy, secret/key, scientific,
   protected-set, rights, safety, and disclosure consequences. A protected leak
   or uncertain environment integrity invalidates confirmatory status by default.
7. **Remediate upstream:** remove the cause, rotate keys or revoke access where
   applicable, repair de-identification/component/configuration logic, and follow
   approved authority/participant notification and deletion rules.
8. **Refreeze:** issue new versioned data/code/manifests and preserve the prior
   decision plus a dated correction; do not silently overwrite evidence.
9. **Reverify:** run the complete affected machine suite, a 100% scan when pilot
   safety is implicated, and a fresh independently seeded human audit when the
   canonical pilot audit failed.
10. **Resume or route:** named human owners decide whether work may resume,
    claims must narrow, the run is exploratory, or release remains blocked.

**UNKNOWN / BLOCKER:** the real incident contact, secure channel, storage,
notification procedure, retention/deletion policy, and drill evidence are absent.
Therefore the repository is not ready to handle an authentic-data incident and
authentic collection remains prohibited.

## 12. Phase-specific security stop/go gates

| Gate | Work permitted after pass | Security/privacy evidence required | Automatic stop condition |
| --- | --- | --- | --- |
| `SG0` / `P0` specification coherence | synthetic-only tooling and reviewed design | independently verify schema-`1.2.0` VMP hash/artifact grammar, engine-preflight/run-envelope separation, exact provider outcomes and primary-stage retention/counting, Boolean-safe rewrite coordinates, mechanical alignment/transducer, compact lineage/LSE/log-mass, exact binary64 prediction audit, bounded endpoint sets, canonical audit-packet/feature-plan/E0 tensor bytes/hashes, Cartesian `E_k`, diagnostic `P_pair`, bundle-bound nonempty universe, strict universe/input receipts and precedence, semantic-invalid short-circuit, exact metric-run counting/denominators, forbidden-feature nonexposure, and canonical stage vocabulary; close findings; assign owners | circular gold/registry path, stale schema, nonreconstructible VMP, preflight/run ambiguity, provider/run ambiguity, overlapping failure counts, endpoint numeric ambiguity, singular-pair collapse, invalid-universe row use, denominator shrinkage, or contradictory contract |
| `SG1` collection authorization | approved tester recruitment/intake only | authenticated ethics/controller/steward decisions; consent; secure storage/access; retention/withdrawal; key custody; incident drill; rights and welfare plan | any `UNKNOWN` mandatory owner/control or machine-only “approval” |
| `SG2` pilot preflight | release authorized candidates to blind annotation | audited frozen minimal registry; structured coverage manifest; native review; safe annotation UI; exact hashes; source authorization | missing/mutable hash, quota/reviewer failure, live/network path |
| `SG3` pilot expansion | begin corpus expansion | exact 1,200 retained plus excluded accounting; two blind plus one distinct final; all reliability gates; zero-finding canonical human audit | undefined/failed metric, replaced audit item, unsafe/provenance finding |
| `SG4` corpus/partition freeze | build models on development | audited 6,000 corpus; `corpus-final` implementation; complete components; protected singleton/monostratal/provenance and authentic-donation gates | leakage, unresolved ancestry, non-singleton protected family, validator gap |
| `SG5` resource/build readiness | development-only baseline/component training | pinned licensed dependencies/checkpoints; SBOM; isolated offline environment; multi-span transliteration resource/generator/calibration/coverage; audited registry/resolver | mutable/untrusted code, failed coverage, live lookup, protected tuning |
| `SG6` factorial/model freeze | prepare protected-access package | VMP/audit-packet/feature-plan, predicted-endpoint resolver, VMP-grid adapter, feature/gradient/capacity/supervision audits; path-calibration optimizer contract; five-seed manifests; power/H4 frozen; threat tests pass | information-flow/budget mismatch or development evidence below gate |
| `SG7` protected access | calibration, threshold, then one primary run | unopened-state audit; named custodian; immutable models/code/analysis; per-system calibration/threshold tests; one-run authorization | prior exposure, hash drift, nonfinite output, repeated/unauthorized access |
| `SG8` claim routing | internal results and route decision | immutable outputs; complete primary/statistical/failure/selectivity analysis; provenance/FPR interpretation; incident review | missing record, post-hoc threshold/hypothesis, unsupported field claim |
| `SG9` disclosure/demo/release | only the specifically authorized artifact | professional IP/name decision; privacy/rights/security/venue approvals; membership/misuse review; offline demo and claim scan | live/raw/secret material, unresolved rights, unsupported claim, absent approval |

No downstream gate can compensate for a failed upstream gate. A synthetic pass
cannot promote an authentic-data phase, and a strong model result cannot cure a
privacy, rights, provenance, or protected-access violation.

## 13. Accepted, deferred, and prohibited risks

### 13.1 Accepted only for the current synthetic pre-data phase

- Validators are conservative but incomplete; synthetic fixtures may exercise
  machine behavior while remaining explicitly non-evidence for human safety.
- The local research process can tolerate bounded tool unavailability or
  resource-limit rejection because no safety-critical service exists.
- Hashes provide integrity binding but not truth, authority, or historical
  immutability. Human approval remains separate.
- The four-language design is knowingly incomplete. This is a scientific scope
  limitation, never an implicit “other language is safe” decision.

These acceptances do not apply to authentic collection, protected evaluation,
or release.

### 13.2 Deferred behind explicit future gates

- host hardening, secret-manager selection, backup/jurisdiction controls, and
  disaster recovery;
- finalized HMAC algorithm/canonicalization/rotation/destruction and privacy
  attack evaluation;
- dependency/checkpoint pinning, SBOM, safe serialization, and sandbox evidence;
- a full `corpus-final` validator and complete component reconstruction audit;
- membership inference/model extraction and any checkpoint-release decision;
- real-user warning comprehension, accessibility, and human-factors evaluation;
- conversation, voice/ASR, images/QR, browser evidence, federated/on-device,
  continual learning, and live operational integrations.

Deferral means “outside Paper 1 or blocked until separately specified,” not
“low risk.”

### 13.3 Never accepted for Paper 1

- raw donations, identifiers, live artifacts, secrets, keys, or reversible
  mappings in Git, shared logs, model prompts, annotation stores, or releases;
- interaction with a destination or attachment;
- inference-time network lookup or inference LLM;
- public/LLM ancestry in protected partitions;
- protected-set-driven registry/candidate/model/threshold repair;
- silent deletion of failed, abstained, unresolved, or inconvenient records;
- a production-protection, patentability, field-prevalence, or universal
  Indian-language claim from this prototype.

## 14. Required ownership and verification package

Before authentic collection, the project must name distinct accountable holders
for research lead, ethics/privacy authority, data controller, intake/data
steward, de-identification reviewer, key custodian, security/incident lead,
annotation lead, native-language reviewers, registry reviewer, transliteration
resource reviewer, protected-set custodian, statistical lead, IP/rights reviewer,
and release owner. A role may be combined only after a documented
separation-of-duties and conflict review; collection, approval, protected access,
and release must not collapse into one unaudited person.

The minimum security verification package for any phase contains:

- exact scope, data-flow, role/access, and threat-model versions;
- immutable source/data/component/registry/resource/code/model/config hashes;
- machine reports with sanitized diagnostics and exact commands;
- named human decisions for every non-machine-verifiable gate;
- negative-test and incident-drill results with unrun checks stated;
- access, quarantine, correction, withdrawal/deletion, and supersession records;
- residual-risk acceptance signed by the accountable phase owner; and
- a claim-evidence matrix limiting what the phase can support.

## 15. Traceability to authoritative project contracts

- Collection, de-identification, artifact safety, access, withdrawal, and human
  incident requirements: [Consent, Ethics, and Privacy](CONSENT_ETHICS_PRIVACY.md).
- Source classes, rights, lineage, and authorization: [Source Ledger](SOURCE_LEDGER.md)
  and [governance contract](../GOVERNANCE_CONTRACT.md).
- Strict JSONL, safety scanners, annotation structure, components, and pilot
  reliability: [data contract](../DATA_CONTRACT.md).
- Blind annotation, structured-state coverage, and canonical human audit:
  [Annotation Guide](ANNOTATION_GUIDE.md).
- Offline evidence, completeness, and `UNKNOWN` behavior:
  [Registry Protocol](REGISTRY_PROTOCOL.md).
- Candidate resources, calibration isolation, and bypasses:
  [Transliteration Resource Protocol](TRANSLITERATION_RESOURCE_PROTOCOL.md).
- Condition information flow, controls, per-system calibration, and threshold:
  [Factorial Condition Specification](FACTORIAL_CONDITION_SPEC.md).
- Protected access, inference, metrics, failure slices, and claim routing:
  [Paper 1 Preregistration](PAPER_1_PREREGISTRATION.md).
- Phase order and stop/go route: [Weekly Roadmap](WEEKLY_ROADMAP.md).

Implementation-level machine behavior is currently represented by the
[dataset validator](../../fisher_data/validator.py),
[governance validator](../../fisher_governance/validator.py), and
[synthetic audit selector](../../fisher_audit/selector.py). None of those files
can authorize a human-owned gate.

## 16. Review and change rule

Review this threat model before each of `SG1`, `SG4`, `SG5`, `SG7`, and `SG9`,
and after any incident, new data source, schema change, registry/resource update,
model/dependency change, new interface, protected-access deviation, or release
scope change. Add or revise threats prospectively and preserve the earlier
decision through the project’s append-traceable change process.

This document becomes eligible for an authentic-data phase only after named
security, privacy, data-stewardship, annotation, and research owners verify its
controls against the implemented system. Until then, Fisher remains a synthetic-
only, offline research specification—not production protection.
