# Fisher Execution Status

> Authoritative purpose: report what the repository proves now. This is not a
> roadmap, a claim that the proposed method works, or authorization to collect,
> train, access protected data, disclose, commit, or publish.

## 1. Status and evidence contract

The status tokens in this file have narrow meanings:

| Status | Meaning |
| --- | --- |
| `COMPLETE_SPEC` | The requested design artifact is sufficiently specified for its current pre-execution role; it is not implemented or empirically validated unless a separate executable checkpoint says so. |
| `PARTIAL` | Some required specification or implementation evidence exists, but the requested phase/output is not complete. |
| `BLOCKED` | Work is prohibited or cannot validly proceed until a named dependency or approval gate passes. |
| `MISSING` | No repository artifact implements or executes the requested deliverable. A prose intention elsewhere does not change this status. |
| `IMPLEMENTED_UNREVIEWED` | Code or a machine artifact exists, but no successful independent review is recorded for the claimed scope. |
| `EXECUTED_PASS` | A named command was actually run successfully for the exact, narrow scope stated in an executable-evidence row. It never promotes a conceptual phase automatically. |
| `REVIEW_FAILED` | Independent review produced a reproducible material defect; a unit-test pass does not override it. |
| `REPAIRED_PENDING_REVIEW` | A repair exists locally, but the previously failing independent check has not yet been replayed successfully. |

Material statements use the project evidence labels:

- **OBSERVED:** directly verified from the current repository, commands, or local environment.
- **DERIVED:** follows from stated observed evidence.
- **ASSUMED:** plausible but not verified.
- **UNKNOWN:** requires a named check or decision.

### Current working priority

**DECIDED:** synthetic-engine work is paused. The immediate evidence-producing
path is a 240-message, provenance-recorded, safely defanged, human-reviewed
feasibility pilot: four language strata × two labels × 30 messages. Its purpose
is to measure collection yield, annotation clarity, duplicate/template leakage,
Romanized-Indic coverage, and source/campaign grouping. It is not a benchmark
and cannot support a low-false-positive or deployment claim.

If the pilot is viable, the first executable NLP comparison is limited to two
lexical baselines, top-1 transliteration, and multi-candidate transliteration
aggregation. The 6,000-record corpus, full semantic factorial, registry,
synthetic-engine hardening, voice, conversations, app/deployment work, and
patent claims are deferred. Public spam/ham data are development/external-only
until separately reannotated for Fisher's phishing ontology.

### Current truth boundary

**OBSERVED HISTORY THROUGH `E16`:** the repository contained research
specifications, JSONL validators, synthetic fixtures, and a synthetic
audit-selector rehearsal. Independent review
identified material governance-validator and audit-selector defects. Both
repairs now have focused independent passes. A later independent cross-contract
review of the dataset validator failed on two executable file-byte-bound
bypasses and two documentation contract errors; the earlier local test pass is
preserved in `E05`, and the failure is recorded separately in `E06`. The pinned
repair then passed independent replay as `E07`. The newly reconciled candidate
alignment and semantic endpoint/pair interfaces then failed independent review
on five specification blockers recorded in `E08`. The schema-1.2 syntactic VMP
repair then passed scoped independent review as `E09`, and the original five
E08 repairs passed semantic replay as part of `E10`; that same `E10` review
found four new provider-identity, endpoint/projection, resource-bound, and
metric-binding blockers. `E11` independently passed that second repair but
found five later provider-execution/run-envelope, endpoint-numeric, E0-feature,
evaluation-universe, and rewrite-coordinate blockers. `E12` then found five
remaining invalid-state, control-representation, universe/gold-binding,
system-provenance/five-seed, and candidate-diagnostic/`q` blockers. `E13`
independently passed those fifth-repair surfaces but found three remaining
preflight/run-union and metric-input/counting blocker groups. `E14`
independently passed all E13 repairs and the other major contracts but found
three new engine-descriptor/parser, eligibility-outcome/accounting, and metric-
universe/denominator/algebra blocker groups. `E15` independently passed those
E14 repairs and the previously reviewed surfaces but found three remaining
universe-input-parser/count, structural-versus-semantic precedence, and
nonempty-denominator blocker groups. `E16` independently passed that eighth
repair, the universe parser/precedence/semantic-invalid/nonempty contract, and
the prior `E08–E15` regression set. `P0/G0` therefore became `COMPLETE_SPEC`
under the design-only definition below. At that checkpoint, synthetic-engine
implementation and empirical execution were still open. The historical rows
remain evidence of their stated scopes only; none authorizes a human gate.

#### Historical product snapshot — 8 September 2026

**OBSERVED:** the current local source tree adds the v0.4 explicit-action
Chrome/Edge extension, its shared transparent-rule analyzer, and the root Node
CLI. It also contains the auxiliary spam/ham baseline and nested-selection run,
the Fisher pilot v0.1.0 readiness validator, and synthetic-engine implementation
packages. `LUNA-20260906-002` records 69/69 Node tests, 7/7 real-browser
scenarios, and 316/316 Python tests as passing for the verified v0.4 checkpoint.
Those are local implementation checks, not GitHub-hosted CI evidence.

**OBSERVED:** no authentic Fisher corpus, trained Fisher model, model
checkpoint, proposed transliteration-method run, protected evaluation,
paper-result table, or gated research/model-comparison demo exists. The local
extension is an advisory product prototype, not that research demo. Synthetic
engine work remains paused; its implementation does not constitute a fitted
detector or empirical result. The four-item pilot fixture and twelve-item audit
fixture are invented structural examples, not research data or experimental
evidence. This agrees with the declared boundary in the
[README](../../README.md#research-context) and the
[blueprint evidence legend](FISHER_RESEARCH_BLUEPRINT.md#evidence-legend).

**DERIVED:** Fisher is an independently accepted, deterministic and falsifiable
pre-data `P0` research specification with implemented local validation and
synthetic-engine surfaces. It is not a trained phishing detector, benchmark,
paper result, patentable invention, or deployable phishing system.

#### Historical product snapshot — 11 September 2026

**OBSERVED:** the uncommitted local working tree advances the extension and
shared JavaScript engine to v0.5.0. The popup now keeps separate in-memory
message and link drafts, applies the correct 20,000- or 2,048-code-point limit,
shows inline input correction, labels message/link/selected-text results, puts
recommended action before technical detail, and provides an **Edit input**
return path. Selected page text uses a bounded DOM-text preflight followed by
the browser-rendered selection string; form-control-only values remain
excluded. Message link evidence and semantic masking now share one canonical,
single-pass bounded scan. It validates raw authorities, handles common ASCII,
Indic, CJK, wrapper, emoji, and defanged-link boundaries, masks every recognized
candidate even after the 32-address inspection budget, and prevents address
hosts, paths, user information, or email text from supplying message-pressure or
credential cues. Four local Fisher icon sizes are declared without adding
permissions, network access, or storage.

**OBSERVED:** `npm test` passed 113/113 checks; the installed-extension Chromium
suite passed 14/14 scenarios, including automated WCAG checks, selected-text
fidelity, absence of external requests, and 320-pixel layout; the packaging
module passed 26/26 checks; and the complete Python suite passed 318/318 tests.
`npm audit --audit-level=high` reported zero vulnerabilities. Independent final
security re-review found no reproducible in-scope P0 or P1 issue. A contrived
delimiter-free, near-20,000-character repeated-email token took about 0.51
seconds warm in that review; it stayed within the input bound and did not leak
text or change the risk result. The deterministic ignored archive
`outputs/browser_extension/fisher-scam-signal-prototype-v0.5.0.zip` contains 12
runtime members, is 105,300 bytes, passes ZIP integrity and source-byte equality
checking, and has SHA-256
`8e71e577b202e2379082ba276b58b3ff4ae843d19b11f66c8f6406772f369088`.
These are local implementation and packaging checks, not GitHub-hosted evidence
for v0.5.

**OBSERVED:** the product remains an explicit-action advisory checker. It has no
authentic Fisher corpus, trained Fisher phishing model, live reputation lookup,
or measured phishing accuracy. **DERIVED:** v0.5 is a more complete and
internally consistent local product iteration, but it does not change any
research, collection, model, deployment, publication, or safety gate below.

#### Current local product snapshot — 11 October 2026

**OBSERVED:** the local v0.5 extension and CLI include the expanded workspace,
separate message/link/bulk drafts, bounded text-file import, cancellable batch
analysis, filtered line findings, generic JSON exports, and bounded embedded
navigation-destination checks. The local product completion pass found no
reproducible blocking runtime defect in its reviewed scope. It preserves the
existing runtime code and refreshes the installation package and instructions.

**OBSERVED:** `npm test` passed 148/148 tests. `npm run test:browser` passed
22/22 installed-extension Chromium scenarios, covering selection, input limits,
batch import/cancellation, report privacy, narrow/dark layouts, and automated
accessibility. `uv run --python 3.11 python -m unittest discover -q -s tests
-p 'test_*.py'` passed 318/318 tests. Runtime syntax checks and `git diff --check`
passed. These are local checks, not hosted-CI results, accuracy measurements,
manual assistive-technology testing, or stock Chrome/Edge verification.

**OBSERVED:** the rebuilt deterministic archive is
`outputs/browser_extension/fisher-scam-signal-prototype-v0.5.0.zip`, with 12
runtime files, 153,663 bytes, and SHA-256
`3a3599724ef8861caf644453f4040c9377a12ff3d6087be53b42fd433c666040`.
The old ZIP differed from current source in `links.mjs`, `popup.html`,
`popup.js`, and `styles.css`; it is preserved under
`outputs/finish-baseline-20261011/`. The September package measurements above
describe that historical build, not the current download.

**OBSERVED:** independent package verification passed ZIP integrity, exact
runtime inventory, byte equality with all 12 source files, and an identical
second build from an isolated source copy. A disposable Chromium installation
extracted from the new ZIP passed message, embedded-destination, batch, and
individual/batch JSON-export smoke checks, with zero page errors or external
HTTP(S) requests. Both exports excluded the submitted synthetic canaries.
The focused packaging suite also passed 26/26 tests after the documentation
updates; these tests are included in the 318-test Python suite above.

**DERIVED:** the local advisory product is ready for owner installation within
the tested scope. **OBSERVED:** no authentic Fisher phishing dataset, trained
Fisher phishing model, transliteration comparison, measured phishing accuracy,
or completed research submission was produced by this pass. Research gates
below remain separate and unresolved. Source changes remain local and
uncommitted; no push, store submission, or public release was performed.

## 2. Historical Phase-0 environment observation

These observations predate the current product implementation and are preserved
as Phase-0 environment evidence. They are not a current dependency inventory,
target requirements, or performance claims.

| Property | Observed value | Consequence |
| --- | --- | --- |
| Machine architecture | ARM64 Mac (`arm64`), macOS 15.3.1 | Apple/ARM compatibility must be resolved for every pinned dependency. No CUDA assumption is valid. |
| Memory | 17,179,869,184 bytes (16 GiB) | Full-model training feasibility is **UNKNOWN**; memory must be measured with selected checkpoints and batch sizes. |
| Free workspace volume | approximately 55 GiB | Dataset, cache, checkpoint, and prediction retention need a storage budget before acquisition or training. |
| Python | CPython 3.14.6 at the active `python3` | The project says Python 3.11+; support by the proposed ML stack on 3.14.6 is **UNKNOWN**. |
| Present scientific package | NumPy 2.4.4 | Only the observed local NumPy installation is available from the proposed ML stack. |
| Absent Python packages | `torch`, `transformers`, `sklearn`, `datasets`, `tokenizers`, `sentencepiece`, `pandas`, `pyarrow`, `safetensors`, `accelerate` | Baselines, encoders, training, Parquet handling, and model serialization cannot execute in the current environment. |
| Large-file/runtime tooling | Git LFS absent; `nvidia-smi`/NVIDIA runtime absent | Large-artifact policy and compute environment are not frozen. This does not establish whether Apple acceleration could be used after installing a supported framework. |

The proposed stack remains a design in
[blueprint output 14](FISHER_RESEARCH_BLUEPRINT.md#14-technology-stack), not an
installed reproducible environment.

## 3. Git and publication boundary

**OBSERVED — pre-publication check on 8 September 2026:** local `HEAD` resolves
to `b23359ac89e072691018c3760c445910d93f110b`; the checked-out branch at that
observation was `master`; and the v0.4 product and supporting research changes
were still unpublished working-tree content. `origin` was configured as
`https://github.com/m-rithik/Phishing-in-indian-language.git`. This dated
observation does not prescribe the branch name or repository root used for a
later publication snapshot.

**DERIVED:** the local commit predates the unpublished v0.4 snapshot and does
not by itself prove that snapshot. Commit and push/publication remain separate
approval events governed by the
[project operating policy](../CHANGE_DECISION_LOG.md#operating-policy).

## 4. Dependency graph and critical path

```text
[P0 / G0 COMPLETE_SPEC — design-only independent semantic PASS E16]
  |-- ACCEPTED: deterministic/falsifiable synthetic-E0 specification
  |-- PRESERVED HISTORY: E06 and E08-E15 failures and their scoped repairs
  |-- SYNTHETIC ENGINE: local scaffolding exists; review unresolved; work paused
  |-- NEXT RESEARCH ACTION: prepare and audit the 240-message feasibility pilot
  `-- AUTHORIZATION/DATA PATH
                    |
                    v
[D0 / G1 collection authorization: ethics + consent + privacy + provenance]
                    |
                    v
[D0 / G2 registry + coverage + annotator/blinded-registry-review preflight]
                    |
                    v
[D1 / G3 1,200-retained ontology pilot + reliability + independent audit]
                    |
                    v
[D1 / G4 6,000-record corpus + components + corpus-final validation]
                    |
                    v
[E0-E2 / G5 environment + synthetic harness + baselines + candidate engine]
                    |
                    v
[E3-E4 / G6 semantic factorial + controls + development-only freeze]
                    |
                    v
[E5 / G7 per-system calibration + safety threshold + protected authorization]
                    |
                    v
[G8 one immutable primary_test run + statistics + claim routing]
                    |
                    v
[G9 professional IP decision + manuscript + safe demo + release authorization]
```

Prior-art, dependency/license, threat, and name-clearance work runs alongside the
critical path but can stop disclosure at `G9`. The gate ordering is required by
the [24-week roadmap](WEEKLY_ROADMAP.md#mandatory-stopgo-routes) and
[preregistration](PAPER_1_PREREGISTRATION.md#13-gono-go-and-claim-routing-rules).
Skipping an upstream gate invalidates downstream evidence.

The 240-item schema-0.1 feasibility pilot is a separate, pre-G2 data-readiness
branch. It uses label/language annotations and its own allocation, component,
native-review, and blinding plan. It does not use or satisfy the schema-1.2
registry/structured-state workflow and cannot advance `G2` or `G3`.

## 5. Named stop/go gates

| Gate ID | Gate | Current state | Exact evidence | Proof required to pass |
| --- | --- | --- | --- | --- |
| `G0` | `P0` specification-coherence gate | `COMPLETE_SPEC` | `E16` records an independent `P0 SEMANTIC PASS` for the deterministic/falsifiable synthetic-`E0` specification, including the eighth universe repair and prior `E08–E15` regressions. This is design acceptance only. | No further `P0` design proof is required for this frozen version. Implement and independently test the exact synthetic `E0` provider/system/descriptor/preflight/run/prediction/packet/plan/tensor/universe/metric-input/metric-run interfaces; implementation or empirical evidence is not part of `G0`. |
| `G1` | `D0` collection-authorization gate | `BLOCKED` | The repaired governance validator has a focused independent pass and still reports `collection_ready=false`. Twenty human/unrepresented gates remain `UNKNOWN`. | Named approvals, consent/withdrawal material, secure storage/access/retention, incident route, provenance authorization, and authenticated human evidence; a machine pass cannot supply them. |
| `G2` | `D0` registry and coverage gate | `BLOCKED` | No audited registry exists; the annotation guide requires a frozen coverage manifest, native review, and blinded registry-review workflow. | Immutable audited registry; complete coverage manifest; independent schema/validator review; qualified native review; annotator and separate registry-reviewer readiness. |
| `G3` | Pilot reliability, safety, and expansion gate | `BLOCKED` | Pilot arithmetic and reliability are specified in the [data contract](../DATA_CONTRACT.md#pilot-final-arithmetic-and-exact-workflow), but only synthetic fixtures exist. | Exactly 1,200 retained balanced items plus all excluded attempts; two blind plus one distinct final annotation per attempt; every metric gate; frozen bundles; independent human audit with zero prohibited findings. |
| `G4` | Corpus-final and independence gate | `BLOCKED` | The [roadmap Week 14 gate](WEEKLY_ROADMAP.md#weekly-execution-plan) requires 6,000 retained records and a `corpus-final` validator; neither exists. | Audited corpus; exact partitions; transitive components; protected singleton/monostratal checks; provenance composition; implemented and independently reviewed `corpus-final` validation. |
| `G5` | `E0–E2` resource/model-readiness gate | `BLOCKED` | Synthetic interface code exists locally, but its independent implementation review is unresolved; no trained baseline, candidate resource, model artifact, or supported ML environment exists. | A viable audited pilot; licensed resources; supported environment; lexical baselines; selected message-level candidate method and measured coverage. |
| `G6` | `E3–E4` factorial-development and freeze gate | `BLOCKED` | The factorial contract is prose only; scalar-calibration optimizer/bounds/failure behavior, feasibility solver, grouped-OOF generator, and H4 rule remain unresolved. | Executable VMP/audit-packet/feature-plan conditions and controls; predicted-endpoint resolver, VMP-grid adapter, and mask audits; grouped predictions; frozen calibration/power/H4 implementations; empirical gate or fallback. |
| `G7` | Protected-access gate | `BLOCKED` | The [threshold protocol](PAPER_1_PREREGISTRATION.md#7-training-calibration-and-threshold-protocol) forbids protected access before upstream freezes; no protected data exists. | Frozen five-seed systems, temperatures, thresholds, analysis code/manifests/hashes, passed independence/provenance audits, and explicit protected-access authorization. |
| `G8` | Method, benchmark, or fallback route gate | `BLOCKED` | No `primary_test` execution or result exists. FPR routing is now specified as own-policy recall plus absolute per-stratum bounds; it is not common-FPR dominance. | One immutable protected run; complete co-primary, mechanism, calibration, FPR, ablation, failure, and negative-transfer evidence; claim route chosen without changing hypotheses. |
| `G9` | IP, publication, demo, and release gate | `BLOCKED` | The [publication/IP checklist](PUBLICATION_IP_GATE.md#gate-checklist) has no professional decision or release evidence. | Professional filing/no-filing/defer decision; name clearance; manuscript and reproducibility audit; data/model/demo rights and safety approval; venue-policy check; explicit publication authorization. |

## 6. Contract reconciliation state

### `OPEN-REGISTRY-GOLD-001` — semantic specification accepted; implementation open

**DECIDED / DERIVED:** blind human gold is limited to the `VMP`: primary label,
subtype, language, facets, spans/evidence, and visible endpoints. Blind
annotators and the final adjudicator see no registry/provenance. A separate
reviewer, blind to the primary label/provenance/protected outcomes, resolves the
canonical Cartesian product of final endpoint sets against a frozen registry
and writes only `MATCH|MISMATCH|UNKNOWN` reference rows; an empty product makes
no calls/rows and has implicit runtime `N/A`. At inference only bounded predicted
`VMP` endpoint sets construct the per-path Cartesian audit packet; state
prevalence is diagnostic, and semantic risk consumes only the deterministic
`SemanticFeaturePlan` projection. `E0_VMP_CATEGORY_MEAN_V1` supplies the exact
pinned-Unicode five-category binary64 VMP grid and 31-dimensional masked tensor
audit; a future candidate/subword adapter and feature-plan version remain
unimplemented and must freeze before `E3`. No learned registry-state loss or
literal surface/registry-ID/hash/score/rank/`q` feature is allowed.

**OBSERVED HISTORY:** `E06` found two executable byte-bound bypasses and two
documentation contract errors after the earlier local pass. **OBSERVED REPAIR:**
the pinned data repair passed both exploit replays, 34/34 focused tests, and
93/93 full tests under independent `E07`. **OBSERVED LATER FAILURE:** `E08`
identified five semantic-contract blockers; its 93/93 test pass did not execute
an engine. `E09` then passed the scoped schema-1.2 syntactic VMP repair, while
`E10` passed the original five repairs and found four new semantic-contract
blockers despite 101/101 non-engine tests. `E11` passed that second repair and
found five later execution-envelope, endpoint-numeric, E0-feature,
evaluation-universe, and coordinate-predicate blockers despite 101/101
non-engine tests. `E13` then passed the shared-provider factor, exact masks,
complete universe/gold binding, system/five-seed provenance, and candidate
numeric surfaces, but found three remaining preflight/run-union and metric-input/
counting blocker groups despite 101/101 non-engine tests. `E14` passed all E13
repairs and the other major contracts but found three descriptor/parser,
eligibility-accounting, and metric-universe/denominator/algebra groups despite
101 passing non-engine test methods. `E15` passed all E14 repairs and the prior
reviewed surfaces but found three remaining universe-input-parser/count,
structural-versus-semantic precedence, and nonempty-denominator groups despite
101/101 non-engine tests. `E16` independently passed the eighth repair, the
universe parser/precedence/semantic-invalid/nonempty contract, and all named
prior `E08–E15` regressions. **OPEN:** engine implementation and later feature/
gradient/access tests.
`P0/G0` is `COMPLETE_SPEC` only; all implementation and empirical gates remain
unchanged.

### `OPEN-VERSION-001` — canonical taxonomy independently accepted; execution open

**DECIDED:** the canonical taxonomy is `P0`; `D0`; `D1`; `E0`; `E1`; `E2`; `E3`;
`E4`; `E5`, with meanings fixed in
[ENGINE_SPEC.md](ENGINE_SPEC.md#1-evidence-and-lifecycle-boundary). The demo is
separately gated. Ambiguous prior version labels are retired and cannot be used
for an acceptance claim.

**OBSERVED:** `E16` independently accepts the `P0` semantic specification.
No engine stage is complete merely because this taxonomy is accepted; `E0–E5`
still require their own executable evidence.

## 7. Active work packages

No calendar dates or people are assigned because staffing and authority evidence
is absent. `UNKNOWN` means the accountable owner has not been evidenced.

| Work package | State | Accountable owner | Deliverable and immediate exit proof | Depends on |
| --- | --- | --- | --- | --- |
| `WP-00-CONTRACT` | `COMPLETE_SPEC` | `UNKNOWN` | `E16` independently accepts the deterministic/falsifiable `P0` contract while preserving `E05–E15` history. Freeze this version; corrections require a new evidence row. | None |
| `WP-01-GOVERNANCE` | `BLOCKED` | `UNKNOWN` | Execute the authorization checklist with named authority, consent, storage, withdrawal, retention, incident, and source decisions. | `WP-00-CONTRACT` where relation handling affects consent/tooling |
| `WP-02-PREFLIGHT` | `BLOCKED` | `UNKNOWN` | Build the audited offline registry, structured-state coverage manifest, native-review evidence, annotator packet, and authenticated human-governance evidence package. The mechanical governance projection cannot supply these approvals. | `WP-00-CONTRACT`, `WP-01-GOVERNANCE` |
| `WP-03-VALIDATION` | `PARTIAL` | `UNKNOWN` | Preserve governance/audit and `E07` data-validator independent passes; implement later `corpus-final` without overstating human approval. | Frozen contracts |
| `WP-04-PILOT` | `BLOCKED` | `UNKNOWN` | Collect, annotate, adjudicate, validate, and independently audit the exact ontology pilot. | `WP-01-GOVERNANCE`, `WP-02-PREFLIGHT`, `WP-03-VALIDATION` |
| `WP-05-CORPUS` | `BLOCKED` | `UNKNOWN` | Build and freeze the audited 6,000-record component-disjoint corpus and protected partitions. | Passed `WP-04-PILOT` |
| `WP-06-MODELS` | `BLOCKED` | `UNKNOWN` | Synthetic harness work is paused. After the feasibility-pilot audit, install a supported minimal ML environment and run character TF-IDF logistic regression plus word+character TF-IDF linear SVM before implementing transliteration aggregation. | Viable audited pilot and authorized development data; no model claim can pass `G5` early |
| `WP-07-CONFIRMATORY` | `BLOCKED` | `UNKNOWN` | Freeze systems and analyses, lock calibration/thresholds, then execute protected evaluation exactly once. | Passed `WP-06-MODELS` and `G7` |
| `WP-08-DISCLOSURE` | `BLOCKED` | `UNKNOWN` | Choose evidence-supported paper route, complete professional IP/name decisions, manuscript, reproducibility package, and safe demo. | `WP-07-CONFIRMATORY`, `G9` |

## 8. Required 20-phase checkpoint table

Rows preserve the master brief's order. Each `Pxx` identifier is stable for
machine updates.

| ID | Required phase | Status | Exact local evidence | Concrete proof needed to advance |
| --- | --- | --- | --- | --- |
| `P01` | Deeply understand the problem | `PARTIAL` | Problem, scope, and gap are written in [outputs 2–4](FISHER_RESEARCH_BLUEPRINT.md#2-one-line-idea). | Empirical stakeholder/user evidence; explicit separation of user, research, and commercial opportunity; tested assumptions and failure costs. |
| `P02` | Prior art and research landscape | `PARTIAL` | [Prior-art search log](PRIOR_ART_SEARCH_LOG.md#3-search-sessions) records scientific/patent searches and its own search gaps. | Reproducible broader paper/patent/product/GitHub search, dated query/export evidence, claim-level comparison, and independent review. |
| `P03` | Find the strongest novelty | `PARTIAL` | Ten candidate directions and a selected coupling appear in [output 6](FISHER_RESEARCH_BLUEPRINT.md#6-novelty). | Evidence-backed scoring across novelty, feasibility, compute, data, time, measurable impact, demo value, and claim pressure; experimental falsification against simpler combinations. |
| `P04` | Define the research contribution | `COMPLETE_SPEC` | RQs, hypotheses, and conditional contributions are precise in [outputs 7–9](FISHER_RESEARCH_BLUEPRINT.md#7-research-questions) and [preregistration](PAPER_1_PREREGISTRATION.md#4-research-questions-and-hypotheses). | Execution remains separate: do not promote conditional contributions until their gates and experiments pass. |
| `P05` | Design the system architecture | `PARTIAL` | VMP, candidate, resolver audit packet, semantic feature projection, calibration, and condition access are specified in [ENGINE_SPEC.md](ENGINE_SPEC.md); current schema `1.2.0` implements the VMP artifact inventory/hash and endpoint/reference boundary locally. | Replay independent semantic review; implement engine interfaces/configuration, failure contracts, resource targets, and end-to-end synthetic tests. |
| `P06` | Model selection | `PARTIAL` | Candidate families and comparators are listed in [output 12](FISHER_RESEARCH_BLUEPRINT.md#12-models). | Pin exact checkpoints, APIs, licenses, versions, tokenizers, parameter budgets, hardware feasibility, and development-only selection procedure. |
| `P07` | Dataset strategy | `BLOCKED` | Dataset/provenance design is substantial in [output 13](FISHER_RESEARCH_BLUEPRINT.md#13-dataset-strategy), but collection authorization remains unresolved in the [ethics protocol](CONSENT_ETHICS_PRIVACY.md#14-authorization-checklist). | Pass `G1–G3`, then produce an audited real pilot; no synthetic fixture can satisfy this. |
| `P08` | Algorithm design | `PARTIAL` | Aligned multi-span composition, bounded endpoint sets, deterministic Cartesian pair resolution, calibrated path ensemble, uncertainty, thresholding, and FPR routing are specified in [ENGINE_SPEC.md](ENGINE_SPEC.md). | Implement; freeze scalar-calibration optimizer, power, and H4 rules; independently test math, invalidity, ties, masking, literal-ID nonexposure, and information flow. |
| `P09` | Build the MVP | `PARTIAL` | Strict dataset/governance validation and synthetic audit rehearsal exist, but the [exact MVP](FISHER_RESEARCH_BLUEPRINT.md#28-exact-mvp) additionally requires a passed pilot, governed resources, 2×2 prototype, controls, and evaluation code. | Meet every exact-MVP bullet with artifact hashes and end-to-end execution on authorized development data. |
| `P10` | Implementation in iterations | `PARTIAL` | Pre-data validation code exists; canonical `P0/D0/D1/E0–E5` stages are specified in [output 15](FISHER_RESEARCH_BLUEPRINT.md#15-implementation-phases). | Independently review taxonomy and execute each stage's acceptance checks; no engine stage has implementation evidence. |
| `P11` | Baselines | `MISSING` | The baseline list exists only as prose in [preregistration Section 8](PAPER_1_PREREGISTRATION.md#8-comparators-and-compute-matching); repository inventory contains no baseline implementation or run artifacts. | Implement all 13 comparators plus mandatory `C01`/`C11` roles and four causal controls; run matched grouped-CV experiments with frozen configs and predictions. |
| `P12` | Experiment design | `PARTIAL` | Outcomes/statistics are preregistered in [Sections 9–10](PAPER_1_PREREGISTRATION.md#9-outcomes-and-reporting). | Implement and independently validate evaluation/power/statistics code; freeze remaining rules; produce dry-run manifests, then authorized measured runs. |
| `P13` | Ablation studies | `MISSING` | The matrix is planned in [preregistration Section 11](PAPER_1_PREREGISTRATION.md#11-ablations-and-mechanism-checks), but no ablation code or run exists. | Implement every frozen ablation and execute it under matched development conditions before protected access. |
| `P14` | Failure analysis | `PARTIAL` | Failure buckets are specified in [preregistration Section 12](PAPER_1_PREREGISTRATION.md#12-failure-and-robustness-analysis); validator tests exercise schema/Unicode failures. | Execute model-, provenance-, stratum-, shift-, adversarial-, calibration-, and abstention-level analyses and retain per-stage error evidence. |
| `P15` | Explainability and uncertainty | `PARTIAL` | Structured evidence and uncertainty equations are designed in [outputs 10–11](FISHER_RESEARCH_BLUEPRINT.md#10-complete-architecture). | Implement bounded explanations, calibrated risk/coverage, path disagreement, abstention, faithfulness checks, and comparator evaluation. |
| `P16` | Privacy, security, and ethics | `BLOCKED` | A detailed [consent/ethics/privacy protocol](CONSENT_ETHICS_PRIVACY.md#14-authorization-checklist) and fail-closed [mechanical governance projection](../GOVERNANCE_CONTRACT.md#machine-versus-human-readiness) exist, but approval fields and accountable authorities remain unresolved. | Named approvals plus executed consent, de-identification, storage, access, retention, incident, artifact-safety, bias, and adversarial audits. |
| `P17` | Patent analysis | `BLOCKED` | A preliminary [publication/IP gate](PUBLICATION_IP_GATE.md#narrow-invention-candidate-for-professional-review) and patent-pressure map exist; they explicitly are not legal conclusions. | Professional novelty/FTO/ownership/name review, claim chart, disclosure chronology, and written `FILE`/`DO NOT FILE`/`DEFER` decision. |
| `P18` | Paper strategy | `PARTIAL` | Conditional routes, outline, and venue families exist in [outputs 23–24](FISHER_RESEARCH_BLUEPRINT.md#23-research-paper-potential). | Measured results, chosen honest route, current venue-policy/deadline check, manuscript, reproducibility statement, limitations, and internal review. |
| `P19` | Make the project demo impressive | `MISSING` | The local v0.4 advisory extension exists, but the research/model-comparison demo in [output 25](FISHER_RESEARCH_BLUEPRINT.md#25-demo-design) remains prose only. | Implement and safety-review an offline 30–60 second comparison using synthetic or release-authorized examples after scientific/IP gates. |
| `P20` | Final critical review | `PARTIAL` | A five-lens checklist exists in the [blueprint](FISHER_RESEARCH_BLUEPRINT.md#final-critical-review-checklist), and this completion audit exposes current gaps. | Repeat independent research, patent, ML, product/security, and examiner reviews on the actual frozen corpus, system, results, demo, and release package; close or explicitly block every objection. |

## 9. Required 30-output checkpoint table

Rows preserve the master brief's order. `COMPLETE_SPEC` never means implemented
or experimentally validated.

| ID | Required final output | Status | Exact local evidence | Concrete proof needed to advance |
| --- | --- | --- | --- | --- |
| `O01` | Final project title | `COMPLETE_SPEC` | [Blueprint output 1](FISHER_RESEARCH_BLUEPRINT.md#1-final-project-title). | Execution-independent; commercial/trademark/publication-name clearance remains a separate `G9` requirement. |
| `O02` | One-line idea | `COMPLETE_SPEC` | [Blueprint output 2](FISHER_RESEARCH_BLUEPRINT.md#2-one-line-idea). | Change only through a recorded research-scope decision. |
| `O03` | Problem statement | `COMPLETE_SPEC` | [Blueprint output 3](FISHER_RESEARCH_BLUEPRINT.md#3-problem-statement). | Empirical problem validation belongs to `P01`, not this prose deliverable. |
| `O04` | Research gap | `PARTIAL` | [Blueprint output 4](FISHER_RESEARCH_BLUEPRINT.md#4-research-gap) labels the gap as derived and non-exhaustive. | Complete reproducible scientific/product/patent search and independent claim-boundary review. |
| `O05` | Existing work | `PARTIAL` | [Blueprint output 5](FISHER_RESEARCH_BLUEPRINT.md#5-existing-work) and the [search log](PRIOR_ART_SEARCH_LOG.md#4-scientific-evidence-map). | Add systematic inclusion/exclusion, reproducible query/export evidence, products/GitHub implementations, and exact closest-method comparison. |
| `O06` | Novelty | `PARTIAL` | [Blueprint output 6](FISHER_RESEARCH_BLUEPRINT.md#6-novelty) defines a conditional coupling, not a proven novelty claim. | Prior-art closure plus factorial/mechanism experiments proving value beyond simpler alternatives. |
| `O07` | Research questions | `COMPLETE_SPEC` | [Blueprint output 7](FISHER_RESEARCH_BLUEPRINT.md#7-research-questions). | Preserve unchanged through protected evaluation or record a preregistered deviation. |
| `O08` | Hypotheses | `COMPLETE_SPEC` | [Blueprint output 8](FISHER_RESEARCH_BLUEPRINT.md#8-hypotheses) and exact decision rules in the [preregistration](PAPER_1_PREREGISTRATION.md#4-research-questions-and-hypotheses). | Resolve H4 before protected access; FPR routing is specified but unexecuted. |
| `O09` | Proposed contributions | `PARTIAL` | [Blueprint output 9](FISHER_RESEARCH_BLUEPRINT.md#9-proposed-contributions) explicitly makes method/dataset contributions conditional. | Pass the contribution-specific method, corpus, evaluation, and failure-analysis gates; withdraw or narrow failed claims. |
| `O10` | Complete architecture | `PARTIAL` | [Engine specification](ENGINE_SPEC.md), [blueprint output 10](FISHER_RESEARCH_BLUEPRINT.md#10-complete-architecture), and current local schema `1.2.0`. | Replay independent semantic review; implement engine interfaces, manifests, fallbacks, and end-to-end integration. |
| `O11` | Algorithms | `PARTIAL` | [Engine specification](ENGINE_SPEC.md) freezes candidate composition, resolver, calibrated path ensemble, selectivity, and FPR boundary. | Executable tested implementation, exact scalar optimizer contract, power/H4 implementation, and independent verification. |
| `O12` | Models | `PARTIAL` | [Blueprint output 12](FISHER_RESEARCH_BLUEPRINT.md#12-models). | Exact licensed artifacts, versions, selection results, capacity accounting, environment compatibility, and trained runs. |
| `O13` | Dataset strategy | `BLOCKED` | [Blueprint output 13](FISHER_RESEARCH_BLUEPRINT.md#13-dataset-strategy) is designed, while [collection authorization](CONSENT_ETHICS_PRIVACY.md#14-authorization-checklist) is unresolved. | Pass governance/registry/coverage gates and execute the real pilot before corpus expansion. |
| `O14` | Technology stack | `PARTIAL` | [Blueprint output 14](FISHER_RESEARCH_BLUEPRINT.md#14-technology-stack) is assumed; Section 2 above measures missing dependencies. | Freeze supported Python, lockfile/environment, dependency licenses, storage/compute budgets, model versions, and reproducible installation smoke test. |
| `O15` | Implementation phases | `COMPLETE_SPEC` | [Blueprint output 15](FISHER_RESEARCH_BLUEPRINT.md#15-implementation-phases) uses canonical `P0/D0/D1/E0–E5`. | Independent vocabulary review; then prove each stage separately. |
| `O16` | Experiments | `PARTIAL` | [Blueprint output 16](FISHER_RESEARCH_BLUEPRINT.md#16-experiments) and preregistered analysis exist as designs. | Implement, dry-run, independently verify, and then execute every gated experiment on authorized partitions. |
| `O17` | Baselines | `MISSING` | Only a list exists in [blueprint output 17](FISHER_RESEARCH_BLUEPRINT.md#17-baselines); no baseline code/config/prediction is present. | Implement and reproducibly execute the complete matched comparator suite. |
| `O18` | Evaluation metrics | `PARTIAL` | Metrics, path uncertainty, and individual/familywise FPR boundaries exist in [blueprint output 18](FISHER_RESEARCH_BLUEPRINT.md#18-evaluation-metrics). | Implement verified code, resolve H4, and compute only on allowed data. |
| `O19` | Ablation studies | `MISSING` | [Blueprint output 19](FISHER_RESEARCH_BLUEPRINT.md#19-ablation-studies) is a plan only. | Ablation implementations, frozen configs, completed runs, and component-attribution report. |
| `O20` | Failure testing | `PARTIAL` | [Blueprint output 20](FISHER_RESEARCH_BLUEPRINT.md#20-failure-testing) defines cases; current tests cover only validation behavior. | Execute the complete model/system failure suite, preserve cases and predictions, and report mitigations and residual risk. |
| `O21` | Privacy/security considerations | `BLOCKED` | Considerations are specified in [blueprint output 21](FISHER_RESEARCH_BLUEPRINT.md#21-privacy-and-security-considerations), and machine governance checks exist, but authenticated human/governance execution is absent. | Pass `G1`, safety/provenance audit, threat tests, access/storage controls, and release review. |
| `O22` | Patent potential | `BLOCKED` | [Blueprint output 22](FISHER_RESEARCH_BLUEPRINT.md#22-patent-potential) correctly says deeper professional search is needed. | Enablement evidence plus professional novelty/FTO/ownership/name decision before disclosure. |
| `O23` | Research-paper potential | `PARTIAL` | Conditional routes appear in [blueprint output 23](FISHER_RESEARCH_BLUEPRINT.md#23-research-paper-potential). | Corpus and experimental evidence sufficient to choose method, resource, mixed/null, or no-paper route. |
| `O24` | Possible publication venues | `PARTIAL` | Venue families are proposed in [blueprint output 24](FISHER_RESEARCH_BLUEPRINT.md#24-possible-publication-venues), with policies/deadlines unresolved. | After results, verify current scope fit, deadlines, page limits, artifact/anonymity/AI policies, and disclosure compatibility. |
| `O25` | Demo design | `MISSING` | [Blueprint output 25](FISHER_RESEARCH_BLUEPRINT.md#25-demo-design) is prose; the v0.4 advisory extension is not the required gated research/model-comparison demo. | Working offline artifact, safe examples, model-comparison trace, timing/user-comprehension check, and security/IP approval. |
| `O26` | Risks and limitations | `COMPLETE_SPEC` | [Blueprint output 26](FISHER_RESEARCH_BLUEPRINT.md#26-risks-and-limitations). | Update with observed failures and measured limits after every execution phase. |
| `O27` | Future improvements | `COMPLETE_SPEC` | [Blueprint output 27](FISHER_RESEARCH_BLUEPRINT.md#27-future-improvements). | Keep outside Paper 1 unless separately approved and preregistered. |
| `O28` | Exact MVP | `PARTIAL` | [Blueprint output 28](FISHER_RESEARCH_BLUEPRINT.md#28-exact-mvp) defines it; only part of its validation layer exists. | Passed real pilot, governed resources, split tooling, 2×2 plus controls, evaluation code, and complete reproducibility manifests. |
| `O29` | Exact final system | `MISSING` | [Blueprint output 29](FISHER_RESEARCH_BLUEPRINT.md#29-exact-final-system) defines the target; none of the corpus/model/evaluation/demo package exists. | Produce every listed final artifact and pass `G0–G9`; prose is not proof. |
| `O30` | Week-by-week execution roadmap | `COMPLETE_SPEC` | The [24-week roadmap](WEEKLY_ROADMAP.md#weekly-execution-plan) provides ordered work and stop/go routes. | Assign dates/resources only after staffing, authority, compute, and source evidence exists; keep status evidence in this file. |

## 10. Executable evidence checkpoints

These rows preserve executed passes and later independent failures. A historical
unit pass does not override a `REVIEW_FAILED` row, and none establishes a corpus,
annotation quality, model performance, human approval, or release readiness.

| ID | Status | Scope actually executed | Evidence and result | Does not prove |
| --- | --- | --- | --- | --- |
| `E01` | `EXECUTED_PASS` | Historical unit-suite execution before independent defect findings | `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v` executed 76 tests in 16.169 seconds: `OK`. | The suite missed later independently reproduced governance and audit defects; this row is not a current implementation-review pass and proves no human gate. |
| `E02` | `EXECUTED_PASS` | Four-item structural data dry run in `draft` mode | The [synthetic pilot fixture](../../examples/pilot/README.md) validated with 2 sources, 4 items, 12 annotations, 0 errors, and exactly 3 expected pilot-size/balance warnings using [fisher_data](../../fisher_data/validator.py). | A 1,200-item pilot, authentic data, linguistic quality, safety audit, or a passing `pilot-final` corpus. |
| `E03` | `EXECUTED_PASS` | Repaired synthetic audit-selector, focused independent review | The original independent timing exposed approximately quadratic supplement selection (`1,200≈0.131s`, `2,400≈0.449s`, `4,800≈1.696s`, `10,000≈7.212s`). Against selector `8abb47a2...`, entry point `3da5859...`, and contract `00520285...`, the independent reviewer passed 28/28 focused tests plus exact reference, HMAC, order, supplement, and safety replay. Measured adversarial unique-annotator cases were 10,000 in 0.302s/101 MiB and 100,000 in 3.494s/642 MiB; maximum-sized JSON was approximately 90.6 MB/737 MiB. The prior failure remains part of this evidence history. | Synthetic selector arithmetic and the measured implementation bounds only. It does not prove a complete/frozen real universe, witnessed seed, human review, zero prohibited findings, governance authorization, or release readiness; the maximum-input memory cost remains operationally material. |
| `E04` | `EXECUTED_PASS` | Repaired governance-ledger mechanical projection, focused independent review | The prior independent review reproduced rights-policy, scanner, lineage/cycle, host parsing, CLI-exposure, and post-`fstat` growth defects. Against validator `0aa6f638...`, tests `90c4cf...`, and contract `81fa76...`, the independent reviewer passed all 31 focused tests, the growth-race regression, and original adversarial spot probes; the blocked fixture remained `collection_ready=false`. The implementation owner had also passed the then-current 89-test full suite, but the independent reviewer did not rerun that full suite because concurrent data changes made it a different tree. | The failed findings remain recorded, and the focused repair is accepted. This does not prove full-tree stability after concurrent changes, any of 20 human gates, collection readiness, registry/coverage approval, or lawful/ethical authorization. |
| `E05` | `EXECUTED_PASS` | Local schema `1.1.0` endpoint/reference repair and integration validation | The stable focused suite passed 32/32 at validator `8e7260dc...` and data contract `812245bb...`. A local full-tree run of `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v` passed 91/91 in 22.435 seconds. The four-item draft CLI returned `VALID` with `registry_references=4`, `applicable_pairs=4`, `missing=4`, `unknown=4`, `zero_applicable_pairs=false`, no errors, and the expected three allocation warnings. Tests cover retired-field/blind-registry-input rejection, endpoint and endpoint-pair metrics without relation-label metrics, three-state reference binding/reviewer separation, Cartesian inventory, and explicit zero-pair support. | The subsequent independent review failed as recorded in `E06`; these local passes did not cover its bypasses. This does not prove linguistic/registry truth, pilot readiness, human blinding, authentic data, or collection authorization. |
| `E06` | `REVIEW_FAILED` | Independent cross-contract review of dataset validator `8e7260dc...`, tests `aaf3ad7d...`, data contract `812245bb...`, and research-document claims | Two reduced-limit probes reproduced executable file-byte-bound bypasses. First, post-open growth through oversized-line draining counted the first chunk but not drained remainder bytes: the final file was 103 raw bytes with `MAX_FILE_BYTES=20`, yet validation reported `line_length_limit` without `file_size_limit`. Second, universal-newline translation changed raw CRLF to LF before the old decoded-text re-encoding/count: the final file was 24 raw bytes with `MAX_FILE_BYTES=20`, yet no `file_size_limit` was reported. The review also found that `SOURCE_LEDGER.md` named stale dataset-snapshot schema `1.0.0` and that `REGISTRY_PROTOCOL.md` overstated what the dataset CLI proves about registry artifact hashes and evidence artifacts. The existing focused 32/32 and full 91/91 suites still passed, demonstrating missing regression coverage rather than absence of the defects. | No repair or replay pass is claimed. The probes are reduced-limit reproductions, not a measured real-input exploit rate. Documentation repair alone cannot close the executable findings, validate external artifact bytes or evidence, prove registry truth/completeness, or authorize collection. |
| `E07` | `EXECUTED_PASS` | Independent replay of the scoped dataset byte-bound and cross-contract repair | Against validator `4d1f849...`, tests `5b0a52c...`, and data contract `0fc29164...`, both exact `E06` exploit probes were replayed and closed. The focused suite passed 34/34 and the full suite passed 93/93. This new row preserves rather than erases the `E06` failure evidence. | This scoped pass does not review or implement the newly reconciled candidate-alignment, endpoint-set, Cartesian-packet, `P_pair`, feature-whitelist, condition-loss, or engine-manifest contracts. It does not prove linguistic/registry truth, human workflow, collection authorization, model performance, or release readiness. |
| `E08` | `REVIEW_FAILED` | Independent semantic-interface and cross-document specification review | At review, hashes were ENGINE_SPEC `873320bdcfc9cfc985d23d1064bb6c0dd22c1e114901bc32fc680541eba5491e`, FACTORIAL `431a86b6a5903041cd432a641e1040ca9366441c03367f8347558093fbd993a2`, PREREG `b1c65e0da7915d584bb0b8af433777e564cf36ac00daf871dd3524e8c0d09d06`, REGISTRY `e2344307b5983776863e1f9f4ec273ad51032863a131abb04a276a5ef8148f88`, TRANSLITERATION `52b70fb6f389af84ca5bbb96a465457d0169f24c514436fdd37d9a8684c27641`, THREAT `c7a3670139fabbca81a1169c9e9321ddbc73aef3bc2f0d2774ead82734b87e8f`, BLUEPRINT `8abaa6b8c011ce7a3da1b52d35170866fd0e9bb8cf78386ee88df1a2ea8e17d5`, ANNOTATION `689c41c86981acefaa0e2f996709a3a061d09d6c780061d637ca4a0a02b0c412`, EXECUTION_STATUS `9da2d2fc335dc0d971a8eabe2df2a30e7a33ac39d65ab3d71f724422ec957eac`, and historical schema-1.1 DATA_CONTRACT `0fc291644f6423d57eedf108713c72625b95554d81f4ba2ec235dbfb8dde448e`. Five blockers were independently observed: (1) persisted schema-1.1 item data could not reconstruct the specified VMP because it lacked a non-gold visible-artifact inventory and annotations were prohibited inference inputs; (2) alignment “monotone” had no machine predicate and normalization-induced alignment transformation was unspecified; (3) “fixed-order float64 logsumexp” did not freeze operand order—a NumPy permutation probe on the same six logits produced `8.456834966970222` and `8.456834966970224`; (4) a valid 2,000 equal-binary-span long beam with best score about `-1386.294` made a direct-exponent retained-mass ratio become `0/0`; and (5) pair-packet hashing lacked canonical bytes, field inventory/order, and numeric encoding. The reviewer also found that `zero_pair_correct` misnamed its all-message emptiness-agreement formula and that the unaligned resolver short-circuit was unspecified. `python3 -B -m unittest discover -s tests -v` passed 93/93 in 22.791 seconds but did not execute a `fisher_engine`. | The local docs-only schema-1.2/VMP, mechanical alignment/transducer, provider-lineage/LSE, log-domain retained-mass, canonical SEP, pair-emptiness, and unaligned-short-circuit repair is pending independent replay. No engine, empirical result, registry truth, human workflow, collection authorization, or `G0/P0` pass is claimed. |
| `E09` | `EXECUTED_PASS` | Independent replay of the scoped schema-1.2 syntactic VMP/data-contract repair before `E0` | Against validator `997cecbfccedb66bdff21c3995a1f3c6cbc6f13daff9b019c3daaf15da904c2f`, tests `e0e385284b2e730a7081fbd232d1f2bab763bdc63805d417fd8455a89ae2073f`, and DATA_CONTRACT `4c7e4d60714f4da3237bd9d9b9b9e2f017849b066501e02b090527c85c37c8d3`, the independent reviewer passed 42/42 focused and 101/101 full tests. The original bare IPv6, UPI, Unicode-dot, mapped/terminal-punctuation, bracket/port/full/zone cases were replayed under the repaired scanner. This is a pre-`E0` syntactic VMP pass and preserves `E06`/`E08` failures. | Artifact grammar proves syntactic representation safety only, not real-world authenticity, human-audited artifact kind, registry truth/completeness, collection authorization, nonidentity provider behavior, Python-3.11 support, an engine, model performance, or publication readiness. |
| `E10` | `REVIEW_FAILED` | Second independent semantic-interface review at the scoped `E09` data boundary | Verdict was `P0 SEMANTIC FAIL`; `G0` remained blocked. Pins were ENGINE `9e93a31c33b6fd13fbc9de32cd27ea0c2e873d6e246e021fe2ec4ff8db5d2cd4`, FACTORIAL `7748303757b1f4435da3e5d0b53c91e98df165b0f9dcc2723a59eb104756ee28`, PREREG `ac6e4d7f41380f22cfbc297359c51a191b68cf6254f60eefe1256ec6fd2f12c4`, REGISTRY `354fcf4e6b1e050cfdf8ccacfd9ae1ff7a7920eef69f3ef9f3225f75c2bc4388`, TRANSLITERATION `53116cea3cc1ef7aa4776fc0b700d7b6a7fcadbcb1881aa77cbcddc3e247cbec`, THREAT `ca47b04d69625ee6e6666e1b85902b2860591b41292b63b59724b32f346df62e`, BLUEPRINT `f02a8ad9509984d43b745fb70702f1953650e16e31079f39611dc3024ab90422`, ANNOTATION `d900b8ffccf2bdfb8b8dd8bc106105fda2aeedf248ec40690c36d67da4e7ab42`, EXECUTION_STATUS `d3b1ca81f028562318b2a0b04e96b02e89fa4bdfdeb8c49f9741322e7a09e94e`, SOURCE_LEDGER `45b71d884bb2e0f0cb9c5bf7037245d64bcb989b66fb577bd1c1816c6f1de2bf`, and DATA_CONTRACT `4c7e4d60714f4da3237bd9d9b9b9e2f017849b066501e02b090527c85c37c8d3`. The original five `E08` repairs passed. Four new blockers were observed: (1) provider identity/manifests lacked exact cross-unit/direct lineage, schema/bytes/order/ID/f64/hash identity—the concrete ambiguity allowed two separate rank-1 responses and a direct response without a comparable key; (2) endpoint vocabulary/bounds, score-independent packet order, and an exact audit-to-learned-feature projection/canary were incomplete; (3) evidence IDs, candidate output, and packet size lacked normative safe bounds; and (4) metric eligibility/failure handling plus exact inference/reference snapshot-resolver-artifact equality were undefined, permitting a registry-B `UNKNOWN` prediction to score against a registry-A `MATCH` reference. `python3 -B -m unittest discover -s tests -v` passed 101/101 in 29.586 seconds but had no engine coverage. Independent conceptual probes—not executable engine tests—confirmed operand-order-sensitive LSE (`-0x1.975cd27944a3dp-7` versus `-0x1.975cd279449bdp-7`), signed-zero canonicalization, a 2,000-span direct-exp underflow where log mass was `0x1.00000000002e7p-3`, overflow-safe exact `8x8=64` versus beam `8x8x2=128`, and a metric vector with TP `.6`, FP `.25`, FN `.4`, F1 `.6486486486486486`, q emptiness `.7833333333333333`, empty recall `.875`, nonempty recall `.6`, and rank-1 emptiness `1.0`; packet hashes were computed conceptually but no engine/call audit existed. | The second local docs-only provider-manifest/lineage/bounds, endpoint/audit-packet/feature-plan/grid, and bundle-bound complete-universe metric repair is pending fresh independent replay. No engine, real registry, nonidentity provider, Python-3.11 runtime, D0/D1 human workflow, collection authorization, model result, performance, or publication claim is established. |
| `E11` | `REVIEW_FAILED` | Third independent semantic-interface review at the scoped `E09` data boundary | Verdict was `P0 SEMANTIC FAIL`; `G0` remained blocked. Pins were ENGINE `c150c5784e9556bb8b0d12669598bdb6bd5e3a83c8e42d837a90d11eb21fc70e`, FACTORIAL `ce1700f9fa1abc0d0c3f26571c421a32e568a2ecd251c937630ad9b70f52cd4d`, PREREG `54e6d33874397ee15fdec72d4e685cd783b085bc15ec6290193ccd8df2a886ce`, REGISTRY `dc626f1dd3ed5e93aee2c868ecdf8a97d00d68c476446f7f28598d1f735a4264`, TRANSLITERATION `0630d531ccb85cf3795a7747c9cd28be025d6172882da9887ba6575876cd89bc`, THREAT `4dc317354ea801bfe4f83f7af1c4d11c8812af5a3bc3b983467c18c7416b830f`, BLUEPRINT `0b4d5d5bd1f9809367c7bc366d7690b1b9d24be6e042d06bfe7ddd73470e8e4b`, ANNOTATION `0ad5936f3962676fa27ad83758e6c3fbe55e543d19d8c0e66c910f8753c39a1c`, EXECUTION_STATUS `714f686b450eb7018a0d93021287c752c6274de79f631af78bc97d41db98f505`, SOURCE_LEDGER `ae961e648774691e419f8a2d2ea9edfe0cd0481667ee17976562f2a4d48ed941`, and DATA_CONTRACT `4c7e4d60714f4da3237bd9d9b9b9e2f017849b066501e02b090527c85c37c8d3`. The second-repair requirements passed. Five new blockers were observed: (1) both bypass causes serialized as the same `IDENTITY_BYPASS` output and lost attempted provider configuration/spans, while the broader run manifest had no exact schema/bytes/hash; the conceptual no-span and provider-failure manifest hash was identical at `bf5e49ce81eb38a6be8496f1ed4c6b0f57e51d5c4c780312a1087cc3768bed3d`; (2) endpoint selection lacked an exact prediction-audit score representation, association, order, serialization, and hash, so `1.00000004` versus `1.00000003` differs in binary64 but ties in binary32; (3) `SemanticFeaturePlan` projection lacked exact basis/order/dtype/grid/row encoding and mean arithmetic, while conceptual sequential binary64 `[1e16,1,-1e16]` produced `0` versus compensated `1/3`; (4) the evaluation universe lacked an exact manifest/item grammar/order/hash and metric binding, so conceptual post-hoc deletion `[a,b]` to `[a]` could pass; and (5) rewrite `start`/`end` lacked an explicit non-Boolean integer/range predicate, while Python Boolean `true` can act as index `1`. `python3 -B -m unittest discover -s tests -v` passed 101/101 in 29.666 seconds but did not execute an engine. Every cited counterexample was a conceptual probe, not an engine test. | The third local docs-only provider-execution/source/run-envelope, binary64 prediction-audit, exact E0 grid/tensor, canonical evaluation-universe/metric-run, and Boolean-safe rewrite-coordinate repair is pending fresh independent replay. No engine, real registry, nonidentity provider, Python-3.11 runtime, D0/D1 human workflow, collection authorization, model result, performance, or publication claim is established. |
| `E12` | `REVIEW_FAILED` | Fourth independent semantic-interface replay at the scoped `E09` data boundary | Verdict remained `P0 SEMANTIC FAIL`; `G0` remained blocked. Pins were ENGINE `1ae7b86fbf3dce7f2c93afc202794cfcb03f0d6dca9d02b7c7e9e11ed13499ae`, FACTORIAL `99d5d8e49176f4dfaec07ee737f1b07cdb96c9ec0da5063ef9cb2734b74ed313`, PREREG `67c3640de0e0d80a7ac943cdd2621295766fff80ecd842220ac2e6f3cec14efb`, REGISTRY `9699825e312cd17f93b85445700c167b0820c7cb5136e111a9b9bf586bad0866`, TRANSLITERATION `0d4ce4016ece538fa980ae52ed2d721c42e2332efd9b70b80faf7927480a4b60`, THREAT `971caa609b9714837a1219d0bd7c5b1e95c00cdce294607948fd9fb47a55ed80`, BLUEPRINT `a051f692171740730d1c6fd1034a35000a3106ce9f74cb554f443b8f2b2ddf71`, ANNOTATION `0e1cf0620168f039be39a35e601ae2e07cb40c44706276b85637fa21835c47b5`, EXECUTION_STATUS `7062794857cc0e132b6c56a2575b3d591a5e50c1edb8632da3cb36db7b69589f`, SOURCE_LEDGER `f94dcc8ea557bf7a67ba411837a4f904ab04d42fed583e7788ebf52ccdb89f3d`, and DATA_CONTRACT `4c7e4d60714f4da3237bd9d9b9b9e2f017849b066501e02b090527c85c37c8d3`. Five blockers were independently observed: (1) the run-envelope invalid state contradicted its own mandatory valid-artifact inventory and could force invented candidates or downstream objects after an early failure; (2) the causal controls were not representable as exact condition/variant/artifact masks while preserving prohibited endpoint/registry/semantic inference access; (3) the evaluation-universe closure and per-item canonical gold bytes/length/hash were incomplete, so exact denominator and gold reconstruction were not bound; (4) exact system provenance, complete executed-source closure, registry/provider/model/resource/environment/analysis bindings, and canonical five-seed logits/means were absent; and (5) candidate stage-reduction counts, one retained-mass vocabulary/scope, and exact runtime-bound binary64 `q` numerator/normalizer/accumulation operations were incomplete. `python3 -B -m unittest discover -s tests -v` passed 101/101 in 29.144 seconds but did not execute an engine. Any reviewer examples or arithmetic checks were conceptual probes only, not engine evidence. | The fifth local docs-only repair restores one shared provider factorial, discriminated engine/metric unions, exact eight-combination masks, complete universe/gold binding, canonical system/source/registry/five-seed provenance, and exact candidate/mass/`q` diagnostics. It is pending fresh independent replay. No engine, trained control, real registry, nonidentity provider, Python-3.11 runtime, D0/D1 human workflow, collection authorization, model result, performance, or publication claim is established. |
| `E13` | `REVIEW_FAILED` | Fifth independent semantic-interface replay at the scoped `E09` data boundary | Verdict remained `P0 SEMANTIC FAIL`; `G0` remained blocked. Pins were ENGINE `0beaf6e38b36b086e94cd2707aad2392afb502c1ae8f8d8df087fc61bdeaf217`, FACTORIAL `cfaf647ec7086e43d769e97920dcb604645e314dd8f347910d32d268c329d23b`, PREREG `099572752140dc01f721044166b6e83f9f31a189a48b5ea7c4f6a9ccf392c5d3`, REGISTRY `b838ba4f7cb12ef0e9fde5eda0a101889f7478e250fd4424009cd40083a07d62`, TRANSLITERATION `0f4a5f4314a38c094d20cb81a17feef2d9b4ed747a514a0e49462e4b902999b4`, THREAT `e43fb1b200112829a6a6af1acc6ac722f377054db5a5167e5783dc23867f90cb`, BLUEPRINT `eb914de7aa72f1f01493fd10a7e66d96e78c21a55a968f9006736e60a54d7a22`, ANNOTATION `8a33d3b8f78d98a3ba52380a6f9dfecf6abf8011fa41d97f726896953605288c`, EXECUTION_STATUS `6a66249b4220b059beaca02f2ca52bb08217acbe0102c90b9e72242ab969eee9`, SOURCE_LEDGER `7be24b53bdb33d0bd48bcb6c3c205677cfa4e94067ba495794986247865169b9`, and DATA_CONTRACT `4c7e4d60714f4da3237bd9d9b9b9e2f017849b066501e02b090527c85c37c8d3`. The shared-provider factorial, exact control masks, complete universe/gold binding, system/source/registry/five-seed provenance, and candidate diagnostics/`q` surfaces from the fifth repair passed; conceptual equality of the provider output quartet was not a blocker. Three blocker groups remained: (1) source/config or VMP failures before valid mandatory bindings had no separate preflight receipt, while the per-item run union still left provider outcome/hash nullability, invalid-stage retention and registry binding, failure precedence/count units, and two possible degraded continuations non-constructible; (2) malformed, oversized, non-UTF-8, or noncanonical metric submissions could not safely produce the then-required canonical full-submission hash and metric-run row; and (3) duplicate, extra, missing, reordered, degraded, invalid, and mismatch counts had no exclusive classification precedence, so examples such as expected `[a,b]` and submitted `[b,a,a,c,c]` were not uniquely determined. `python3 -B -m unittest discover -s tests -v` passed 101/101 in 30.105 seconds but did not execute an engine. All reviewer probes were conceptual, not engine tests. | The sixth local docs-only repair separates bounded engine and metric-input preflight receipts from their canonical run artifacts, makes provider outcomes and stage retention/counting exact, permits only degraded-stop-after-identity, and freezes exclusive submitted-list discrepancy counting. It is pending fresh independent replay. No engine, trained control, real registry, nonidentity provider, Python-3.11 runtime, D0/D1 human workflow, collection authorization, model result, performance, or publication claim is established. |
| `E14` | `REVIEW_FAILED` | Sixth independent semantic-interface replay at the scoped `E09` data boundary | Verdict remained `P0 SEMANTIC FAIL`; `G0` remained blocked. Pins were ENGINE `1a462b26d2b1b84590c95ca1e91ab0380f05fd7b5121cee743571afc7c867b9b`, FACTORIAL `1850c41e1b66204db46fe5d5104472b475a2d55d50b5a00ec2778bf71a92146f`, PREREG `8521fa83bb184f2185e2b5f3c86e8ce34789db1c0e001348835f0e7dcd6c23f4`, REGISTRY `4c9cd1af715ccee6c267ee320a2c054752c4a192cc1acd1f970ffca108d2a06a`, TRANSLITERATION `07d529e4b83c30f9d7cd7747bf85375d5083bdf7cc3a187d2fb79089ddc834c7`, THREAT `f8c830a3f01d04f17ce6ef441e6ac236a8ca7b5c5da7feb97a1c3fdac7e98196`, BLUEPRINT `4ee5105021d003215dc50850317b8d7eb5bda0e3324aafab594fafe21f4ec9ba`, ANNOTATION `2665425dd0ce58593e7793a650792ada09e568e34d92bbee11f30ed1dc70dee4`, EXECUTION_STATUS `2b92ba77f8bbbfb3edc431f523e8e5e2c1e782dd73316d97280d65baadc2329b`, SOURCE_LEDGER `c321ef50a6cadfd6d2fcd98730f183872ed07608c6aabc48c679d66d38e0da51`, and DATA_CONTRACT `4c7e4d60714f4da3237bd9d9b9b9e2f017849b066501e02b090527c85c37c8d3`. All E13 repairs and the previously reviewed shared-provider, mask, provenance, candidate, universe/gold, packet, feature, and metric-submission contracts passed. Three new blocker groups remained: (1) no normative path-free `EngineInputDescriptor`, exact raw-byte/parser/duplicate/nonfinite/canonical/schema/reference precedence, or constructible PASS receipt bound the supplied system/VMP artifacts; (2) invalid eligibility-selector outputs had no total provider outcome, safe retained shape, controlled code, or exact configured-versus-accepted span counts before dispatch; and (3) metric runs lacked disjoint universe/declared-denominator error counts, a safe malformed-universe input boundary, and canonical zero-denominator precision/recall/F1 algebra. The existing 101 test methods passed but did not execute an engine; reviewer descriptor/parser, eligibility, and metric checks were conceptual probes only. | The seventh local docs-only repair freezes the engine descriptor/parser/PASS–FAIL receipt, `ELIGIBILITY_INVALID` and bounded selector accounting, safe universe-input receipt, disjoint universe/denominator counts, and canonical `+0.0` pair algebra. It is pending fresh independent replay. No engine, trained control, real registry, nonidentity provider, Python-3.11 runtime, D0/D1 human workflow, collection authorization, model result, performance, or publication claim is established. |
| `E15` | `REVIEW_FAILED` | Seventh independent semantic-interface replay at the scoped `E09` data boundary | Verdict remained `P0 SEMANTIC FAIL`; `G0` remained blocked. Pins were ENGINE `bdbe7ccaa907d874ad40ffad66bc3888848e6fe5408c8c499877a9dd3e9f0b7d`, FACTORIAL `1e82661cc58db207cc2bf0e95a612e6fdbfad7983bac664ee625adeba180560e`, PREREG `d6543084b4b9abe2617da8890aa9bbccd952649731dd1bbe401ecde173d40cc8`, REGISTRY `4efd8f6f69887d642204c35746b7930d89eced7a4d889e3da1087de96107ea7d`, TRANSLITERATION `2ba805983de8863c66ec0528f8d3362fa48c48f955dea92febef6fd24223d4a6`, THREAT `131e310770bc678c6b43a328842a3811c24c55395c4efeacc702be84a4053dfc`, BLUEPRINT `ce801ef4d0d2da96feadb0b52cbe8a94a3107dabbaf17f76b30035310098caa7`, ANNOTATION `522202ede387d2c6e5704d6420bde866e5c4e77a9cff541c0b063b77768dd819`, EXECUTION_STATUS `aa7389dce3c109a88e634abd2f0b403ee0c2900e3e465b7fce780eab851eb4eb`, SOURCE_LEDGER `444e43ba3417632b9d1ea426cb668c1323499fc90cfab353147b492efa13db64`, and DATA_CONTRACT `4c7e4d60714f4da3237bd9d9b9b9e2f017849b066501e02b090527c85c37c8d3`. All E14 repairs and the prior reviewed engine-descriptor, eligibility, run-union, factorial, provenance, candidate, packet, feature, universe/gold, submission, metric-counting, and zero-pair-algebra surfaces passed. Three remaining blocker groups were independently observed: (1) `MetricUniverseInputReceipt` did not freeze the strict raw scanner/parser's distinct BOM, duplicate-key, nonfinite, syntax, NFC, canonical-byte, schema/enum, and entry-bound codes or their one-code precedence, leaving library-default behavior possible; (2) decoded-versus-validated entry counts, complete-hash versus over-cap prefix-hash states, and structural receipt `PASS` versus semantic closure were not machine exact; and (3) universe-structural, submission-preflight, and semantic-closure precedence was ambiguous, including whether an invalid or empty universe could enter row comparison, open envelopes, or leave `pair_emptiness_accuracy` with a zero valid-run denominator. `python3 -B -m unittest discover -s tests -v` passed 101/101 in 30.210 seconds but did not execute an engine. Link and anchor checks passed; scanner/count/precedence and empty-universe checks were conceptual probes only, not executable engine tests. | The eighth local, universe-only docs repair freezes the strict one-code universe scanner/parser and receipt count/hash union, exact universe-then-submission-then-semantic precedence, semantic-invalid no-envelope short-circuit, and one-to-10,000 valid-universe denominator. It is pending fresh independent replay. No engine, trained control, real registry, nonidentity provider, Python-3.11 runtime, D0/D1 human workflow, collection authorization, model result, performance, or publication claim is established. |
| `E16` | `EXECUTED_PASS` | Eighth independent P0 semantic-interface replay at the scoped `E09` data boundary | Verdict was `P0 SEMANTIC PASS`. Stable pins were ENGINE `a159c86fee69118349a0d7c25634ba6ac362e4a687bee9787b80dc4d405a02f4`, FACTORIAL `6629f99d12ec2eb87e02f085ae5ddee7723cb1288ff0761ead0d97b161b6316a`, PREREG `9c2b5e79858f1f17866aa06ea537deb42ed5c64b79dfb0e828017119d2c87008`, REGISTRY `1e4ecf750589450fb14614e963e8e4f090c34a415c915ef583a178a07cf4ad9b`, TRANSLITERATION `6a76b516df50b18a0c67f6975462efd75c5f9fabe7a64c0fca160eeb77d0895e`, THREAT `4283b39d1f08e71b053c3fc71d044186828a38da8c4fa1fc301da83e7f2494c2`, BLUEPRINT `df63128f94d5c021675ee74ae29da98b9fcbcc805b2c1fb895633b305422b46b`, ANNOTATION `b9724e0725616bdc1b437357ec026cdeb871de4d8bc6dbd8a55d9eaa1017c5eb`, EXECUTION_STATUS `7f2d7bae1a9837231edbe9a2d0a5c75e2654c1bd2555fabec3eb8326967c712e`, SOURCE_LEDGER `f3264e66de5441f1552a5c817cef4ae26585bf419f8d11000030e4448bc81875`, and DATA_CONTRACT `4c7e4d60714f4da3237bd9d9b9b9e2f017849b066501e02b090527c85c37c8d3`. The strict universe scanner/parser, exact receipt count/hash states, universe-then-submission-then-semantic precedence, semantic-invalid no-envelope branch, nonempty valid universe/denominator, and all named prior `E08–E15` regressions passed. Independent documentation verification covered 136 targets and 93 anchors. `python3 -B -m unittest discover -s tests -v` passed 101/101 in 30.206 seconds; this suite was explicitly non-engine. | This accepts only a deterministic and falsifiable synthetic-`E0` specification and promotes `P0/G0` to design-only `COMPLETE_SPEC`. It does not implement an engine, execute a provider/resolver/model, create a corpus or registry, authorize collection, validate human workflow, measure empirical performance, access protected data, or support publication/product claims. `G5`, `G6`, and every governance, data, implementation, model, and empirical gate remain unchanged. |

**DECIDED / DERIVED architecture adjudication after `E12`:** one frozen
provider/configuration now serves all four factorial cells; only rank-one versus
all-path activation and semantic absence/presence define the two factors. The
engine and metric manifests are discriminated status unions, and source/system/
five-seed provenance, control masks, complete universe/gold closure, and exact
candidate diagnostics are contractually bound. This is a local design repair,
not an independent pass or implementation claim.

**DECIDED / DERIVED architecture adjudication after `E13`:** failures before a
valid system manifest and validated VMP create only an
`EnginePreflightReceipt`; a per-item `EngineRunEnvelope` begins only after those
preconditions. Malformed or unbounded metric-submission bytes create only a
`MetricInputReceipt`; a `MetricRunManifest` begins only after structural and
canonical input validation. The run union has one controlled
`DEGRADED_STOP_AFTER_IDENTITY` branch, and valid bounded metric submissions use
one exclusive discrepancy-counting precedence. This is a local sixth design
repair pending independent replay, not an implementation or pass.

**DECIDED / DERIVED architecture adjudication after `E14`:** a path-free
canonical `EngineInputDescriptor` and total one-code parser precede the
PASS/FAIL receipt; only PASS permits an engine envelope. Invalid selector output
has its own pre-dispatch outcome and bounded safe counts. Metric runs distinguish
universe-binding from declared-denominator errors, malformed universe bytes stay
in a safe receipt domain, and natural zero pair-metric denominators yield
canonical `+0.0`. This seventh local repair is pending independent replay and is
not an implementation or pass.

**DECIDED / DERIVED architecture adjudication after `E15`:** universe input now
uses the same deterministic strict scanner discipline as engine input and emits
one exact structural receipt code. Universe structural validation precedes
submission preflight, which precedes semantic closure. A structurally valid but
semantically invalid universe has one no-envelope metric-run short-circuit; a
valid universe and `N_all` are nonempty. This eighth local repair is pending
independent replay and is not an implementation or pass.

**OBSERVED independent disposition at `E16`:** the eighth replay returned
`P0 SEMANTIC PASS`, including the prior regression surfaces. Under this file's
`COMPLETE_SPEC` definition, `P0/G0` is accepted only as a deterministic and
falsifiable synthetic-`E0` design. This disposition does not promote `E0`,
`G5`, `G6`, or any governance, data, model, implementation, empirical,
protected-access, or release gate.

## 11. Machine-update rules

1. Keep IDs `G0–G9`, `OPEN-*`, `WP-*`, `P01–P20`, `O01–O30`, and `E01+`
   stable; never reuse an ID for a different requirement.
2. Use only the status tokens defined in Section 1. Do not infer a phase
   promotion from a passing narrower checkpoint.
3. Change a status only when the “proof needed” cell is backed by a linked local
   artifact or exact command result. Label unavailable evidence `UNKNOWN`.
4. Preserve failed or superseded evidence through a dated revision in the Luna
   register; do not rewrite history or convert a planned metric into a result.
5. Add new executable evidence as a new `E##` row with command, scope, outcome,
   and explicit non-claims. Never overwrite a failed run.
6. Recompute the critical path after any gate changes. Downstream work remains
   blocked unless every required upstream gate is evidenced.
7. Before this handoff, validate that phase IDs are exactly `P01` through `P20`,
   output IDs exactly `O01` through `O30`, and evidence IDs exactly `E01`
   through `E16`, each in order; validate all local Markdown targets and anchors,
   UTF-8, LF-only line endings, final newline, and absence of trailing
   whitespace.

## 12. Next evidence-producing action

The next valid evidence-producing action is to prepare the 240-message
feasibility-pilot packet and resolve the minimum consent, storage,
deidentification, provenance, and source-authorization requirements needed to
use it. After collection, audit language/script distribution, Romanized-Indic
coverage, labels, duplicates, templates, and source/campaign components before
any split or model run. The two IEEE DataPort spam/ham datasets are candidate
development/external sources only after download-time terms are preserved,
privacy and leakage audits pass, and labels are independently mapped to Fisher's
ontology. `G5` and `G6` remain blocked; synthetic-engine work is paused and does
not authorize collection, training, protected access, or an empirical claim.
