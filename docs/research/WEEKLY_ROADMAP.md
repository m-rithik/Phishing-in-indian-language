# Fisher 24-Week Research Roadmap

> Status: **DRAFT — BLOCKED FOR AUTHENTIC COLLECTION**; internal, embargoed, and gate-controlled. Week numbers are sequence labels, not calendar commitments. Dates, staffing, compute, ethics-review path, and source access are **UNKNOWN** until assigned.

## Operating rule

Work advances only when the current acceptance criteria are evidenced. A failed gate triggers repair, scope reduction, or the stated fallback route; it does not permit skipping ahead to `primary_test`. No commit, push, preprint, dataset release, public demo, or submission is implied by this roadmap.

**OBSERVED:** the repository is pre-data and pre-model. **ASSUMED:** native-language annotators and consenting adult testers can be recruited across all four strata. Validate that assumption before collection.

## Weekly execution plan

| Week | Work package | Concrete deliverables | Acceptance criteria / decision |
| ---: | --- | --- | --- |
| 1 | Scope and protocol freeze | Preregistration, blueprint, factorial-condition, transliteration-resource, registry, structured-state coverage, privacy-safe data, threat, source-ledger contracts, and full governance-ledger validator | Canonical partitions, four strata, all-token language denominator, visible-input labels, 2×2/controls, hypotheses, metrics, provenance, coverage quotas, and exclusions agree; dedicated governance-ledger validation and machine structure checks pass |
| 2 | Ethics, consent, safety, and provenance | Adult tester consent/withdrawal flow, human safety audit, de-identification/defanging procedure, artifact-safety rules, redistribution states | Named human reviewer approves internal collection; no validator is treated as ethics/safety approval; grouping uses privacy-safe equivalence keys |
| 3 | Registry, coverage, and annotation preflight | Minimal audited frozen offline registry; component-aware coverage manifest; operational language/primary/facet/span/visible-endpoint instructions; blinded registry-review workflow; tool rehearsal | Native reviewers audit all cells; each stratum has frozen facet and planned resolver-state quotas; blind annotators/final adjudicator see neither registry nor provenance; registry reviewer sees final endpoints but no label/provenance/protected outcome; schema/validator sync passes independent review |
| 4 | Annotator, registry-reviewer, and power-protocol freeze | Separate blind-annotation/adjudication and registry-reviewer training packets; qualification sets; coverage rehearsal; component-yield estimate; frozen simulation procedure | Two blind annotators plus a distinct final adjudicator and separate blinded registry reviewer are available; role-specific access tests pass; coverage tags are hidden/non-gold; prospective power rules freeze without a fabricated estimate |
| 5 | Pilot collection I | First safe, consented, tester/LLM-provenance-complete attempted batch across four strata/labels, released only from the hash-frozen candidate/component order | Registry and structured-state coverage gates passed before collection; no public-authentic or public-derived item enters the pilot; gold fields use model-visible text/artifact only; no source/author/prompt family crosses provisional components; pre-annotation machine and steward safety checks pass |
| 6 | Pilot collection II | Continue until 1,200 retained balanced binary/resolved-stratum items plus extra attempts excluded for unresolved primary and/or language stratum; component review | Retained target is exactly 300/stratum and 150/label; every excluded attempt has controlled matching reasons; replacements follow the same sampling rule with no cherry-picking |
| 7 | Independent pilot annotation | Two blind annotations for every retained or excluded attempted item | Primary/language/facet/span/evidence/visible-endpoint metrics use frozen definitions; registry/provenance/source intent remain hidden |
| 8 | Pilot adjudication, registry reference, and reliability | Third-party visible-input adjudication; separate blinded registry review; endpoint/span/evidence reliability; candidate ambiguity diagnostic; manifest freeze | Blind endpoint reliability and independent registry-reference audit pass their separate gates; no blind registry-state alpha/F1; excluded accounting and exact balance pass; audit universe freezes before seed generation |
| 9 | Pilot go/no-go | Frozen guide revision, registry/human-approval evidence, coverage/native-audit evidence, [canonical human audit](ANNOTATION_GUIDE.md#canonical-human-pilot-safety-and-provenance-audit), expansion decision | Main audit plus minimal-exposure supplements has zero findings: freeze initially missing annotator IDs, process in UTF-8 byte order, skip IDs covered by earlier supplements, otherwise take the lowest-HMAC-ranked unselected eligible bundle; no replacement; any finding triggers quarantine, repair, new freeze, full scan, and fresh witnessed audit |
| 10 | Full corpus expansion I | Audited collection to first expansion checkpoint | Every row has inherited consent/license/provenance/lineage; LLM ancestry is <=30% of `development`; public ancestry appears only in `development`/`external_test`; LLM ancestry is zero in all protected partitions |
| 11 | Full corpus expansion II | Balanced growth across language and label | Each stratum remains on track for 750 phishing/750 benign; dependence/component counts are reported alongside rows |
| 12 | Full corpus expansion III | Complete candidate 6,000-retained-record pool | 1,500 retained per stratum and 750 per label; public items remain `development`/`external_test`; protected items are tester-originated |
| 13 | Full annotation and adjudication | Double-annotation/adjudication for new records; final structured labels | Full-corpus quality meets the frozen annotation/safety requirements or deficient strata return to collection/annotation |
| 14 | Deduplication, components, and partition freeze | Exact/near-duplicate results; component manifest; canonical partition manifests; implemented and independently reviewed `corpus-final` validator | Exact totals: `development` 3,000, `probability_calibration` 400, `safety_threshold` 400 benign, `primary_test` 2,200; `corpus-final` validation passes; protected components singleton/monostratal; no public/LLM ancestry protected; each primary label×stratum cell >=50% authentic donation |
| 15 | `E1` classical and raw-encoder baselines | Rule, artifact LR, word LR, char LR, combined SVM, raw MuRIL/XLM-R/IndicBERT runs | Grouped 3-fold CV executes for seeds 11/23/37/53/71; configs, failures, predictions, and resource measurements are preserved |
| 16 | Governed transliteration/LID layer | Resource hashes/splits, LID candidates, composed/direct contextual providers, multi-span top-K, message-level `T_tr`, bypasses, coverage/NLL | Development-only lexicographic selection; group-disjoint message calibration/evaluation; licenses/checkpoints pinned; no protected tuning; frozen coverage gates pass or claim narrows |
| 17 | `E2` candidate and registry readiness | Freeze selected candidate engine; review/expand registry from independent official evidence if justified; validate blinded registry reference and deterministic resolver | Multi-span composition/calibration gates pass; registry versions remain hash bound, offline, human-audited, and independent of messages/protected outcomes |
| 18 | `E3` semantic factorial and causal controls | Reproducible `C00/C10/C01/C11`, endpoint/span heads, deterministic resolver, capacity/supervision controls, packet/mask traces | Conditions run on `development` only; only semantic cells resolve predicted endpoints; no learned registry-state loss; access and parameter accounting pass |
| 19 | `E4` ablations and robustness | Uniform weights, no raw/aux/registry/resolver, node removals, `UNKNOWN→MISMATCH`, entropy-only, encoder swaps; malformed/Unicode/shift tests | Every frozen ablation completes or is marked unrun; calibration optimizer/bounds/failure behavior, H4, power, and all pre-protected decisions freeze |
| 20 | Development analysis and system freeze | Whole-component bootstrap, empirical 5,000-dataset power update from grouped out-of-fold predictions, hyperparameter/registry/candidate/factorial freeze, five-seed system manifests | Empirical power under the frozen procedure is at least 80% or the preregistered fallback is taken; within every language `C11` recall is no more than 0.02 below `C01`; all protected components remain unopened |
| 21 | Per-system calibration and safety-threshold lock | Average five seed logits per returned path; fit own pooled scalar temperature to averaged path logits on `probability_calibration`; marginalize calibrated path risk; own float64 `nextafter` threshold on `safety_threshold` | Alert/entropy/disagreement/threshold share one calibrated object; no per-seed/language/shared-system calibration; optimizer and bit boundaries reproduce |
| 22 | `E5` `primary_test` evaluation | One execution on 2,200 tester-originated records; provenance-disaggregated and per-stratum outputs | No retuning; each label×stratum cell >=50% authentic donation; singleton/monostratal audit passes; raw outputs/manifests immutable; Holm analysis fixed |
| 23 | Statistics, failures, and route decision | Final bootstrap, multiplicity control, selective-risk curves, ablations, failure taxonomy, limitations, data statement | Choose method+benchmark only if both primary and mechanism/data gates pass; otherwise dataset/resource or null/mixed-result route |
| 24 | IP/publication gate, paper, and safe demo | Internal invention disclosure, professional review decision, manuscript, reproducibility package, 30–60 second offline demo | `FILE`, `DO NOT FILE`, or documented `DEFER`; disclosure occurs only when IP, research, data-rights, privacy, security, and venue-policy gates all authorize it |

## Phase and stage alignment

| Weeks | Research phases | Canonical outcome |
| --- | --- | --- |
| 1 | understand problem through algorithm contract | `P0` reconciled specification |
| 2–4 | authorization, registry, coverage, annotator preflight | `D0` collection preflight |
| 5–14 | pilot, corpus build, leakage control, split freeze | `D1` passed pilot and audited corpus |
| 14–15 | supported environment and synthetic engine harness | `E0`, then `E1` baseline engine |
| 16–17 | candidate and registry components | `E2` candidate engine |
| 18 | proposed method integration | `E3` semantic factorial engine |
| 19–20 | ablations, failures, power, and complete freeze | `E4` pre-protected package |
| 21–23 | calibration, threshold, protected evaluation, analysis | `E5` confirmatory package |
| 24 | paper, IP decision, and offline demo | separately gated disclosure/demo |

The demo is not an engine version and cannot influence scientific design or
expose the method before confirmatory and IP decisions.

## Mandatory stop/go routes

### Stop and repair

- consent, provenance, data-rights, or safety failure;
- missing/failing full governance-ledger validation before source acquisition;
- missing/failing `corpus-final` validation before full-corpus freeze or evaluation;
- missing, mutable, unaudited, or quota-deficient pre-pilot structured-state coverage manifest;
- any active link, credential, direct identifier, or undocumented source in audit;
- pilot agreement/completeness/adjudication failure;
- insufficient independent components or split leakage;
- any non-singleton or multistratal protected component;
- fewer than 300 independent benign `primary_test` components in a stratum for
  the possibility of an individual zero-error below-1% bound; note that 300
  cannot support a simultaneous four-stratum below-1% claim;
- any public ancestry outside `development`/`external_test`, or any LLM ancestry in a protected partition;
- any `primary_test` label×stratum cell below 50% tester-donated authentic for a field-like claim;
- candidate coverage below its gate;
- unpinned or unlicensed transliteration/LID resources, protected-set tuning, or registry live lookup;
- factorial feature-access, capacity, supervision, calibration, or threshold mismatch;
- structured span/endpoint or end-to-end resolver performance below its frozen
  development gate;
- development power below 80%; or
- protected-set access before model/analysis freeze.

### Method-plus-benchmark route

Requires both co-primary `R_safe` gains to have Holm-adjusted p-values below the
frozen familywise threshold and simultaneous lower bounds above zero, with point
gains at least 0.03; supporting mechanism/control evidence; honest low-FPR
intervals; complete ablations; protected independence/provenance gates; and—
within every stratum—own-threshold `C11` recall no more than 0.02 below `C01`.
This is a policy-level recall route, never a common-FPR dominance or
safety-superiority claim. An individual stratum below-1% upper-bound statement
requires exactly `0/300` false positives; the current design cannot support the
simultaneous all-four below-1% statement.

### Dataset/resource fallback

Use when the corpus, annotation, independence, ethics, and release gates pass but the method does not. Preserve null method results, structured annotation evidence, source limitations, and the locked low-FPR benchmark protocol.

If the corpus is valid but any primary authentic-donation cell misses 50%, use the controlled-benchmark/research-prototype route and explicitly prohibit field-like generalization, even when method statistics pass.

### Null/mixed-result route

If one co-primary hypothesis passes or mechanism evidence conflicts, report the mixed result without calling the complete coupling superior. A publication decision depends on the explanatory value of failure analyses, not on relabeling secondary metrics as primary.

## Weekly evidence packet

At every meaningful checkpoint, preserve:

- exact changed artifacts and decision owner;
- evidence labeled `OBSERVED`, `DERIVED`, `ASSUMED`, or `UNKNOWN`;
- alternatives considered and why they were not selected;
- exact checks run and their outputs;
- unrun checks and remaining risk;
- consent/source/license effects;
- component and partition impact;
- configuration, seed, dataset, and output hashes when applicable; and
- next gate and accountable owner.

The canonical Luna Markdown register must be updated for significant completed checkpoints. Git commits and publication remain separately approval-gated.

## Resource decisions still required

Before assigning calendar dates, observe and record:

- number and availability of qualified Hindi, Tamil, Telugu, and code-mix annotators;
- tester recruitment yield and consent/withdrawal administration;
- institutional ethics or review requirements;
- lawful auxiliary-source access and exact license/platform terms;
- independent-component yield after deduplication;
- available CPU/GPU, storage, and runtime budget;
- dependency licenses and supported Python/model versions;
- professional IP/name-clearance owner and turnaround; and
- candidate venue policy/deadline at the actual submission time.

Do not invent dates or compress the pilot, protected-set separation, or disclosure gate to fit a venue deadline.
