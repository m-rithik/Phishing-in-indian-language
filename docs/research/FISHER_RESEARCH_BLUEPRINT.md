# Fisher Research Blueprint

> Status: internal and embargoed. Version: pre-data research design. The blueprint distinguishes planned work from measured evidence; it contains no claim that Fisher currently works.

## Evidence legend

- **OBSERVED:** directly supported by inspected repository state or a cited primary source.
- **DERIVED:** a design conclusion that follows from observed evidence; it still requires empirical testing.
- **ASSUMED:** a planning premise not yet verified.
- **UNKNOWN:** a question requiring a named future check.

**OBSERVED:** Fisher currently has no collected corpus, executable research
engine, trained checkpoint, or measured metric. `E11` independently passed the
second semantic repair but failed five later provider-execution/run-envelope,
endpoint-numeric, E0-feature, evaluation-universe, and rewrite-coordinate
requirements. `E12` then found five remaining status-union, causal-control,
evaluation/gold-binding, system-provenance/five-seed, and candidate-numeric
blockers. `E13` then found three remaining preflight/run-union,
failure-accounting, and metric-input/counting groups. `E14` passes those repairs
and the other major contracts but finds three engine-descriptor/parser,
eligibility-accounting, and metric-universe/denominator/algebra groups. `E15`
passes those repairs and the previously reviewed surfaces but finds three strict
universe-input parser/count, structural-versus-semantic precedence, and
nonempty-denominator groups; the eighth local, universe-only docs repair awaits
replay. **DERIVED:** every
performance, compute, user-impact, and patent-potential statement below is
prospective.

## Complete 30-output blueprint

### 1. Final project title

*Fisher: Uncertainty-Marginalized Transliteration and Semantic Consistency for Low-False-Positive Multilingual Indic Phishing Detection*

Fisher remains the project name. **UNKNOWN:** commercial/trademark and publication-name clearance because existing cybersecurity uses have been observed; the descriptive subtitle reduces ambiguity but does not provide clearance.

### 2. One-line idea

Fisher preserves a bounded calibrated distribution over Romanized Indic
interpretations, predicts visible semantic endpoints on each path, resolves
actor–destination compatibility with a frozen offline registry, marginalizes
calibrated path risk, and abstains when entropy and path disagreement are high.

### 3. Problem statement

Indian phishing messages often combine native scripts, English, nonstandard Romanization, urgency, impersonation, sensitive requests, and deceptive destination artifacts. Word-trigger systems can miss newly worded attacks and can falsely flag legitimate urgent messages. One-best transliteration can erase a meaning needed to connect the claimed organization with the requested action or destination.

Paper 1 asks for reliable standalone-message classification across mutually exclusive Hindi-dominant, Tamil-dominant, Telugu-dominant, and English–Indic code-mixed strata at a deliberately low false-positive operating point. It does not claim to solve all Indian languages, conversations, calls, images, or deployment.

### 4. Research gap

**OBSERVED from cited work:** transliteration lattices and N-best uncertainty predate Fisher; context-aware South Asian transliteration, Indic encoders, typed phishing structures, scam semantic primitives, calibration, and selective prediction also exist.

**DERIVED gap:** the testable opening is not any single component. It is whether
bounded calibrated Romanization uncertainty can be retained through predicted
endpoint extraction, deterministic offline consistency resolution, and
calibrated path-risk marginalization to improve campaign- and author-disjoint
low-FPR recall. **UNKNOWN:** whether exhaustive prior-art review or experiments
will uphold that gap.

### 5. Existing work

| Area | Established evidence | Fisher boundary |
| --- | --- | --- |
| Transliteration lattices | [Durrani et al.](https://aclanthology.org/W12-4410/) and [neural lattice LMs](https://arxiv.org/abs/1803.05071) preserve alternatives | N-best/lattice processing is not novel |
| Romanized South Asian text | [Context-aware transliteration](https://direct.mit.edu/coli/article/50/2/475/119145/), [large-scale Indic transliteration evaluation](https://aclanthology.org/2021.eacl-main.303/), and [Aksharantar](https://aclanthology.org/2023.findings-emnlp.4/) | Candidate generation, transliteration data, and broad evaluation are enabling prior work |
| Indic representation and LID | [MuRIL](https://arxiv.org/abs/2103.10730), [IndicBERT v2](https://aclanthology.org/2023.acl-long.693/), [IndicLID](https://arxiv.org/abs/2305.15814), [informally Romanized LID](https://aclanthology.org/2025.emnlp-main.117/), and [XLM-R](https://arxiv.org/abs/1911.02116) | Encoders and LID are evaluated candidates, not contributions; checkpoint/API/license status remains **UNKNOWN** until pinned |
| Phishing/scam semantics | [PhishSigma++](https://arxiv.org/abs/2605.11619), [semantic scam primitives](https://aclanthology.org/2026.findings-acl.1025/), [ScriptMind](https://aclanthology.org/2026.eacl-industry.2/), [SmishTank](https://arxiv.org/abs/2402.18430), [MOZ-Smishing](https://aclanthology.org/2025.africanlp-1.23/), [KorSmishing Explainer](https://aclanthology.org/2024.emnlp-industry.47/), and a [2026 systematic-review preprint](https://arxiv.org/abs/2604.11429) | Multilingual datasets and explanatory systems already exist; Fisher is not the first multilingual smishing system |
| Calibration/selectivity | [Temperature scaling](https://proceedings.mlr.press/v70/guo17a.html) and [selective classification](https://arxiv.org/abs/1705.08500) | Calibration and abstention are established; the proposed coupling is under test |
| Public product behavior | [Google's India safety charter](https://blog.google/intl/en-in/company-news/googles-safety-charter-for-indias-ai-led-transformation/) describes Google Messages scam-text protection; [Microsoft Defender documentation](https://learn.microsoft.com/en-us/defender-office-365/anti-phishing-policies-about) describes user/domain impersonation protection | Their internal model architectures and Indic-language behavior are **UNKNOWN**; do not claim “first deployable detector” |

Scientific novelty remains non-exhaustively reviewed. Patent pressure is tracked in the dedicated gate; neither this table nor the gate is a legal opinion.

### 6. Novelty

#### Candidate directions considered

| Candidate | Research value | Feasibility now | Decision |
| --- | --- | --- | --- |
| Generic multilingual transformer | Low; common baseline | High | Baseline only |
| One-best Romanized normalization | Low; loses uncertainty | High | Factorial comparator |
| Generic N-best/lattice transliteration | Established | Medium | Component only |
| Typed actor/action/destination graph | Crowded | Medium | Component and comparator |
| Bounded path uncertainty plus predicted-endpoint registry resolution and calibrated risk marginalization | Potentially distinctive coupling | Medium | Selected core hypothesis |
| Entropy plus path-disagreement abstention | Incremental alone; meaningful in the coupling | Medium | Selected mechanism |
| Conversation-risk memory | Valuable but crowded and data-intensive | Low for Paper 1 | Defer |
| Voice/ASR phishing detection | Confounded by unavailable authentic consented audio and ASR error | Low | Defer |
| Federated/on-device deployment | Requires product/device/energy evidence | Low | Defer |
| Dataset/resource contribution | Defensible if provenance and independence gates pass | Medium | Parallel paper fallback |

**DERIVED proposed novelty:** calibrated candidate `q_k` values are not
collapsed before reasoning. A shared encoder predicts path-level visible
endpoint sets and risk; a frozen resolver supplies a complete bounded Cartesian
compatibility packet from predicted endpoints. Fisher marginalizes calibrated
risk over `q`, while q-weighted pair-state prevalence is diagnostic only;
selective risk uses predictive entropy plus calibrated between-path disagreement.

No “first,” “patentable,” “state of the art,” or deployment claim is authorized before the corresponding gate.

### 7. Research questions

- **RQ1:** Does uncertainty marginalization improve locked low-FPR recall over top-1 transliteration when semantic consistency is held present?
- **RQ2:** Does semantic consistency improve locked low-FPR recall when uncertainty marginalization is held present?
- **RQ3:** Is any gain explained by an interaction between uncertainty and semantic consistency rather than added parameters or training exposure?
- **RQ4:** Are gains concentrated in messages with genuine Romanization ambiguity, without unacceptable negative transfer across language strata?
- **RQ5:** Does `C11` reduce selective risk relative to both the top-1 semantic condition `C01` and the weighted-path condition without semantics `C10`?
- **RQ6:** Can the new corpus support an independently useful, provenance-safe benchmark even if the proposed mechanism is null?

### 8. Hypotheses

- **H1, co-primary:** `Delta1 = R_safe(C11) - R_safe(C01)`, testing `H0: Delta1 <= 0` versus `Delta1 > 0`.
- **H2, co-primary:** `Delta2 = R_safe(C11) - R_safe(C10)`, testing `H0: Delta2 <= 0` versus `Delta2 > 0`.
- **H3, secondary:** with `S(C) = -NLL(C)`, `[S(C11) - S(C01)] - [S(C10) - S(C00)] > 0`.
- **H4, secondary:** define `Delta_uncertainty(slice) = S_slice(C11) - S_slice(C01)` with `S = -NLL`; test `Delta_ambiguous > Delta_nonambiguous` using the frozen paired `development`/`primary_test` analysis. Fix the ambiguity-slice rule before observing any model result.
- **H5a, secondary:** `Delta5a = AURC(C01) - AURC(C11) > 0`.
- **H5b, secondary:** `Delta5b = AURC(C10) - AURC(C11) > 0`.

For each system, `R_safe` is the unweighted mean of four alert-level recalls, each computed on the 250 phishing singleton components in that stratum at that system's own frozen threshold. Co-primary success requires both unrounded effects to be at least 0.03, both Holm-adjusted one-sided p-values to be at most 0.05, and both joint familywise simultaneous lower bounds to exceed zero. These are hypotheses and decision rules, not results; the complete estimand and inferential contract is in [PAPER_1_PREREGISTRATION.md](PAPER_1_PREREGISTRATION.md#10-statistical-analysis).

### 9. Proposed contributions

1. **Method contribution, conditional:** bounded transliteration uncertainty,
   predicted-endpoint registry resolution, calibrated path-risk marginalization,
   and disagreement-aware selective prediction.
2. **Dataset contribution, conditional:** a 6,000-message, four-stratum,
   group-disjoint corpus with primary, semantic-facet, span/endpoint, provenance,
   lineage, and separately audited registry-reference artifacts.
3. **Evaluation contribution:** a preregistered low-FPR protocol separating system-specific ensemble calibration, benign-only system thresholds, tester-only `primary_test`, dependency-aware resampling, and multilingual negative-transfer analysis.
4. **Failure-analysis contribution:** attribution of errors to candidate
   coverage/calibration, endpoint extraction, registry missingness, deterministic
   resolution, calibrated path risk, and selective policy.

Each contribution is withdrawn or narrowed if its acceptance gate fails.

### 10. Complete architecture

```text
VisibleMessagePacket (schema-1.2 item.text + pre-annotation visible_artifacts + vmp_sha256)
  -> machine schema validation + separate human safety/ethics audit
  -> evaluated language/script/code-mix routing
  -> calibrated Romanization candidate generator {z_k, q_k}
  -> shared raw/path encoder
  -> per-path node, span, and bounded visible endpoint-set prediction in VMP coordinates
  -> canonical actor-set x destination-set resolver packet (audit only)
  -> score-independent SemanticFeaturePlan -> VMP-grid pooled semantic tokens
  -> per-path phishing-risk logits
  -> five-seed per-path logit average
  -> that system's scalar calibration per averaged path
  -> q-weighted calibrated risk + diagnostic pair-state prevalence
  -> that system's nextafter low-FPR threshold + entropy/disagreement abstention
  -> binary decision, structured evidence, uncertainty state
```

| Module | Input | Output | Training/evidence | Fallback |
| --- | --- | --- | --- | --- |
| Validation and human audit | raw record | machine-valid record plus independent human review state | machine schema/invariant tests; named ethics/safety reviewers | reject/quarantine invalid or unreviewed input |
| Language/script routing | visible text | mutually exclusive stratum and token/script signals | compare IndicLID and informally Romanized LID candidate under pinned artifacts | unknown/route-to-review |
| Candidate generation | Romanized spans or full VMP | aligned `z_1..z_K`, calibrated `q_1..q_K`, bypass/degraded status | one frozen `COMPOSED_SPAN` or `DIRECT_FULL_PATH` provider/configuration for all four cells; rank one active in `C00`/`C01`, all paths active in `C10`/`C11`; candidate-output and exact system/run manifests; governed resources and group-disjoint message-level calibration/evaluation | valid no-eligible identity; controlled pre-output failure identity is degraded/excluded; invalid output rejects |
| Shared encoder | raw and candidate paths | contextual representations | development only | raw-text baseline |
| Structured heads | representations | nodes, spans, capped deduplicated visible endpoint sets in `VMP` coordinates | Fisher blind visible-input annotations | absent endpoint set |
| Offline resolver | canonical predicted actor×destination pairs | bounded, hashed audit packet | frozen official-source registry; no live lookup | pair `UNKNOWN`; empty product is implicit `N/A` |
| Semantic projection | audit packet | score-independent plan, pair mask, and bounded pooled tokens | exact E0 pinned-Unicode category grid and binary64 31-dimensional tensor audit; future candidate/subword adapter and plan version frozen before `E3` | invalidate unavailable/nonfinite grid or tensor |
| Risk marginalizer | projected per-path features, then `q_k` only after path risk | message probability | learned path logits on `development`; calibration only on its partition | top-1 comparator |
| Calibration/decision | mean five-seed logits, entropy, disagreement | alert/benign/abstain | each ensemble owns its temperature, threshold, and cutoffs | invalidate unreproducible run |
| Explanation record | structured evidence | bounded evidence display | no generative explanation needed | show uncertainty/review reason |

There is no database, cloud API, frontend, or feedback-learning loop in the research MVP. A local batch interface is sufficient to test the hypothesis and limits data exposure.

### 11. Algorithms

The exact algorithm is in [ENGINE_SPEC.md](ENGINE_SPEC.md). VMP is exactly
schema-`1.2.0` `item.text` plus non-gold pre-annotation
`item.visible_artifacts`, bound by required `item.vmp_sha256`; annotations never
construct it. The artifact grammar and exact Unicode-code-point
destination-span binding prove syntactic representation safety only, not
authenticity or authority. Each input and normalized output code point has one
nonempty contiguous `VMP` interval; starts and ends are each nondecreasing,
equal/overlap is allowed, rewrite intervals stay within one
non-artifact-overlapping span, and their union covers its source. The normalizer
is an alignment-aware transducer and `E0` supports identity only. Merge identity
is `(normalized text, alignment)`. Each provider reading has a unique immutable
rank in `1..8`; merges preserve manifest-bound contributor lineage. Use the
frozen contributor operand order and sequential stable binary64 max-shift LSE,
an overflow-safe post-merge product, exact enumeration at at most 64, or a
width-64 beam keyed by emitted prefix plus alignment and merged after every
expansion. Return at most eight without padding, ordered by score, UTF-8 text,
encoded alignment, and lineage. Reject nonfinite values and canonicalize signed
zero. Construct `q` with the runtime-bound binary64 divide/max-shift/exp
operations, sequential numerator sum in ascending contributor-lineage bytes,
and division; persist each numerator/weight plus the maximum/normalizer.

`q` is calibrated only over the returned bounded list. Fit `T_tr` after a
lexicographically frozen generator selection using group-disjoint message-level
transliteration calibration; word pairs cannot establish multi-span calibration.
Each merge stage records `sum_g(|g|-1)` and their exact total. Retained mass is
`exp(LSE(returned)-LSE(preK))`, persisted only as
`retained_preK_composition_mass_f64_bits` with both LSEs;
empty/nonfinite/positive-delta cases are invalid and never clamped. Exact `preK`
is the complete enumerated merged set with `preK_scope=EXACT_FULL`; beam `preK`
is only its final bounded beam and never total-lattice mass. `T_tr` affects only
`q`. Bit replay is claimed only in the pinned runtime/container. The only
bypasses are
`NO_ELIGIBLE_ROMANIZED_SPAN` and `PROVIDER_FAILURE_RAW_FALLBACK`, each one
identity-aligned raw path with `s=0,q=1`; provider/normalizer unavailability or
timeout before accepted output may be degraded only if that fallback validates.
Malformed/nonfinite/alignment-invalid output is invalid. A degraded fallback is
never coverage success and invalidates protected/confirmatory metrics. An empty
enabled set is invalid, and the `E0` identity normalizer is synthetic-only.

Exactly one frozen provider configuration is active in every factorial message
run. `C00`/`C01` activate its returned rank-one path; `C10`/`C11` activate all
returned paths. Composed-span and
direct-full-path providers are separate runs/ablations and never pool readings
or logits in one `q`; `IDENTITY_BYPASS` is a candidate-output artifact, not a
configured provider. Their canonical provider-reading manifest, raw identity
`(unit_index,provider_rank)`, mode-specific compact contributor lineage,
16-character finite binary64 score bits, exact ID grammar, 64-span/eight-reading
bounds, 4-MiB manifest bound, and 512-code-point/2,048-byte span and
20,000-code-point/80,000-byte full-path bounds are frozen in the engine spec.
Successful composed and direct modes bind 1..64 ordered artifact-disjoint
rewrite spans. Every span index/start/end is a non-Boolean integer with
contiguous indices, `0 <= start < end <= len(VMP.text)`, exact slice, and sorted
nonoverlap; bypass output has none. A controlled pre-output failure preserves
attempted spans only in the exact `provider_execution` object. A direct reading preserves every non-rewrite code point
and visible-artifact slice and may change text/alignment only within those bound
spans.
Overflow rejects rather than truncates; contributor-byte order determines LSE
operands and no exponential raw cross-product is materialized.

Each execution begins from a path-free canonical `EngineInputDescriptor` that
hash-references separately supplied system-manifest and VMP/item bytes. Its
bounded total-precedence parser emits a one-code `PASS`/`FAIL`
`EnginePreflightReceipt`, and only `PASS` permits execution. Each execution binds a canonical `SystemArtifactManifest` containing the
complete instrumented executed-source closure plus registry, provider, model,
resource, environment, and analysis bindings. Its
schema-`1.1.0` run envelope is a strict
`VALID|DEGRADED_STOP_AFTER_IDENTITY|INVALID` union, applies the earliest-stage
retention/count table, and directly binds the registry
artifact hash. The exact eight base/capacity/supervision combinations and their
artifact masks prevent unrepresentable controls. A canonical
`FiveSeedLogitArtifact` fixes seeds `[11,23,37,53,71]`, active-path order,
finite binary64 logits, sequential mean, and system-artifact identity. `E0`
tests manifests, masks, and arithmetic only; it claims no trained model.

An invalid eligibility-selector result before dispatch uses
`ELIGIBILITY_INVALID`, retains no unsafe span or output hash, records bounded
configured-entry and zero accepted-span counts, and stops at
`PROVIDER_EXECUTION`. Invalid rewrite/alignment after an accepted provider
manifest remains `CANDIDATE` and retains the manifest.

For path `k`, predict deduplicated `VMP` endpoint sets `A_k,D_k`, each capped at
eight by score then frozen range/kind/status/surface ties, and log pre-cap counts
and hits. Each audit endpoint is exactly
`role,start,end,kind,lookup_surface,lookup_status`; actor kind is `NONE`,
destination kind is schema-controlled, and status is `ALIGNED|UNALIGNED`.
Endpoint identity excludes score. After cap, pairs are reordered by range,
kind, and surface UTF-8 bytes so score rank cannot leak. Candidate
offsets/back-projection are prohibited. Define the canonical compatibility inventory

`E_k={(a,d,Resolve_R(a,d)):a in A_k,d in D_k}`.

An empty product makes no calls/rows and has implicit `N/A`. Fully enclosed
candidate spans substitute into lookup surfaces; cut-through is `UNALIGNED` and
the affected pair short-circuits before registry with `UNKNOWN`, engine-only
`NOT_EVALUATED`, `ALIGNMENT_GUARD`, empty evidence IDs, and zero calls. Let
`pi_k(s)` be equal-weight state prevalence
over nonempty `E_k`, or the `N/A` indicator when empty, and
`P_pair(s|x)=sum_k q_k pi_k(s)`. This is diagnostic. The fixed-order compact
UTF-8 packet is an audit record, includes bounded safe evidence IDs and exact
`registry_call_count`, has at most 64 pairs/16 MiB, and is bound by
`vmp_sha256`, text/alignment `path_sha256`, and `pair_packet_sha256`. Endpoint
scores remain only in a separately canonical prediction audit as finite
big-endian binary64 bits, with exact emission indices, dedup/tie/cap selection,
bytes, and SHA-256.

Risk consumes only the deterministic canonical `SemanticFeaturePlan`, never the
audit packet. The plan retains endpoint ranges/status, destination kind, and
resolution state/coverage/source in score-independent order; coordinates are
indexing instructions rather than numeric features. `E0` freezes
`E0_VMP_CATEGORY_MEAN_V1`: a pinned-Unicode five-category binary64 VMP grid,
sequential range means, fixed 31-dimensional pair rows, and a 64-row Boolean
mask/zero-padded tensor with canonical bit strings and hash. Literal lookup
surfaces, IDs, hashes, evidence, scores, ranks, `q`, and score order are excluded.
This tests deterministic projection only. The future candidate/subword-to-VMP
adapter and feature-plan version remain **UNKNOWN** and must be frozen and
tested before `E3`.

For system `m`, average five seed path logits, fit its one temperature on
`probability_calibration`, and define:

`rho_mk = sigmoid(bar_ell_mk/T_m)`,

`p_m = sum_k w_mk rho_mk`,

`v_m = 4 sum_k w_mk(rho_mk-p_m)^2`,

`u_m = 0.5 H(p_m)/log(2) + 0.5v_m`, where
`H(p)=-p log(p)-(1-p)log(1-p)` and `0 log(0)=0`; `w_1=1` for
rank-one `C00`/`C01` and `w_k=q_k` for all-path `C10`/`C11`.

The exact `SystemArtifactManifest` and schema-1.1 run envelope bind the complete
executed-source closure, system/control identity, runtime/float/math-backend
contract, VMP, provider execution/cause/configuration/spans, candidate
diagnostics, path IDs/hashes/lineage/binary64 scores and weights/effective spans,
active paths, canonical five-seed/prediction audits, SEP/E0 tensor hashes,
direct registry artifact/resolver identity, and discriminated status. Exact
evaluation-universe/gold and metric-run unions separately bind the complete
denominator and valid or bounded-invalid submissions. The strict universe
receipt comes first, submission preflight against its computed hash second, and
semantic closure validation third. Either structural failure emits only its
receipt; a semantic-universe failure emits the exact no-envelope invalid metric
run. Bounded submissions against a valid universe use the frozen left-to-right
duplicate/extra/order and exclusive envelope-outcome counts. Bit replay is limited to
the pinned runtime/math backend or later bound container.

Top-1 has `v_m=0`. Alert, entropy, threshold, and disagreement use this same
calibrated object. A common delta was rejected as nonidentified and raw-logit
disagreement with calibrated entropy as incoherent. Exact optimizer
bounds/failure behavior remain an **UNKNOWN pre-`E4` freeze requirement**.

### 12. Models

| Component | Central choice | Comparators | Selection reason/status |
| --- | --- | --- | --- |
| Shared multilingual encoder | MuRIL | XLM-R base, IndicBERT v2 | **DERIVED:** MuRIL is aligned with transliterated Indic text; superiority is **UNKNOWN** |
| Language/script routing | no automatic winner | IndicLID and an informally Romanized LID candidate | Evaluate on Fisher-visible strata; checkpoint, API, and license are **UNKNOWN** until pinned |
| Candidate generation | bounded calibrated candidates, maximum 8 | top-1, flat top-K, uniform weights | Directly tests uncertainty claim |
| Structured prediction | compact span/node/endpoint-set heads plus deterministic Cartesian registry packets | node graph without consistency; adapted typed-relation comparator | Avoids circular registry-state supervision, invented pair links, and a general inference LLM |
| Classical detection | linear models over artifacts/TF-IDF | rule, LR, linear SVM | Strong low-cost baselines |
| Calibration | one pooled scalar temperature per fixed five-seed system ensemble | uncalibrated diagnostic | No per-seed, per-language, or shared-system calibration |
| Abstention | entropy plus path disagreement | entropy only | Tests the proposed selective mechanism |

Encoder swaps must be compute-matched and results disaggregated. LLMs are not inference components in Paper 1.

### 13. Dataset strategy

1. Freeze consent/ethics/privacy, visible-input annotation, source-license/provenance, registry, factorial, and paired-transliteration contracts.
2. Retain an exactly balanced 1,200-message pilot with two independent blind records plus one required third-distinct-annotator final record per attempt: 300 per stratum, 150 per label; unresolved attempted items are extra and the unresolved denominator is retained plus unresolved.
3. Before blind release, freeze hidden non-gold structured-state sampling
   targets: per stratum at least 30 candidate visible-explicit and 30
   no-visible-explicit items per facet, plus 30 planned candidates per resolver
   state. The [canonical human audit](ANNOTATION_GUIDE.md#canonical-human-pilot-safety-and-provenance-audit)
   freezes initially missing annotator IDs after its main sample, processes them
   in UTF-8 byte order, skips IDs already covered by earlier supplements, and
   otherwise selects the lowest-HMAC-ranked unselected eligible bundle. No
   replacement is allowed. These are coverage rules, not power or reliability
   claims.
4. Expand to 6,000 unique group-disjoint messages: 1,500 per stratum, 750 per label.
5. Preserve inherited provenance for tester donation, tester-authored simulation, public authentic sources, and LLM-drafted/human-edited records.
6. Cap LLM ancestry at 30% of `development`; prohibit public/LLM ancestry from `probability_calibration`, `safety_threshold`, and `primary_test`.
7. Make `primary_test` tester-originated only and require at least 50% tester-donated authentic in every label×stratum cell; report donation versus simulation separately.
8. Require singleton, monostratal components throughout all three protected partitions; no per-stratum below-1% claim without 300 independent benign `primary_test` components.
9. Retain original public labels separately from visible-input Fisher gold and use public items only in `development` or `external_test`.

Candidate auxiliary sources require row-level audit and ledger approval. [SMSDHL's author page](https://sites.google.com/cse.nits.ac.in/ramanujamge/publications/datasets-offered) describes Dravidian-language spam data, but spam is not phishing and the raw workbook remains unaudited in this project. Aksharantar and related resources are transliteration auxiliaries, not phishing gold data.

Exact canonical totals are `development` 3,000, `probability_calibration` 400, `safety_threshold` 400 benign, and `primary_test` 2,200. Additional valid states are `pilot`, `unassigned`, `external_test`, and `excluded`; `train/dev/test/external` aliases are invalid. Connected-component grouping prevents source/template/campaign/author/translation/prompt families from crossing partitions.

### 14. Technology stack

**ASSUMED implementation plan, subject to repository/dependency review:** Python; PyTorch; Hugging Face Transformers/Datasets; scikit-learn for classical baselines; a transliteration candidate adapter; JSONL/Parquet research records; configuration-driven runs; and local artifact tracking with immutable hashes. A lightweight batch CLI and static local demo are sufficient.

No vector database, graph database, external LLM API, mobile framework, cloud service, or microservice architecture is justified for Paper 1. Actual versions, GPU requirements, storage, and dependency licenses are **UNKNOWN** until the implementation environment is frozen.

### 15. Implementation phases

| Stage | Deliverable | Acceptance |
| --- | --- | --- |
| `P0` | reconciled protocol/specification package | documents, schema, validator, and independent review agree |
| `D0` | collection authorization plus registry/coverage/annotator preflight | every human and machine preflight gate passes |
| `D1` | passed pilot plus audited 6,000-record corpus and `corpus-final` | corpus/partition evidence passes |
| `E0` | pinned environment plus synthetic engine harness | known-answer packet/math/mask tests pass |
| `E1` | baseline engine | 13 comparators and evaluation harness reproduce on allowed data |
| `E2` | candidate engine | selection, composition, calibration, bypass, and coverage gates pass |
| `E3` | semantic factorial engine | four cells and controls run on `development` with access audits |
| `E4` | development-only ablations, power, robustness, and freeze | every pre-protected decision and manifest is locked |
| `E5` | confirmatory calibration/safety/protected package | one authorized protected sequence completes immutably |

The offline research demo is separately gated and is not an engine stage.

### 16. Experiments

1. Ontology reliability pilot and candidate-coverage diagnostic.
2. Grouped 3-fold development CV across seeds `11, 23, 37, 53, 71`.
3. Core 2×2 factorial experiment plus capacity- and supervision-matched controls under frozen resources.
4. Thirteen planned baselines/component comparators plus mandatory `C01` and proposed `C11`.
5. Candidate calibration/coverage, visible endpoint, audited reference, and
   q-weighted exact labelled pair-set/pair-emptiness experiments.
6. Per-system five-seed logit ensemble, per-system pooled scalar calibration, then per-system benign-only `nextafter` threshold lock.
7. One `primary_test` evaluation of primary and secondary metrics.
8. Locked-system paired bootstrap contrasts, per-language negative transfer, selective risk, and frozen failure slices.
9. Pre-protected-access power sensitivity plus a development-only grouped-OOF empirical update that reconstructs exact calibration, safety-threshold, and primary counts.
10. External public-source diagnostic reported separately if licensing and audit gates pass.

### 17. Baselines

The 13 are: suspicious-pattern rules; artifact logistic regression; word TF-IDF LR; character TF-IDF LR; combined word/character TF-IDF linear SVM; raw MuRIL; raw XLM-R base; raw IndicBERT v2; `C00`; flat top-K augmentation; `C10`; node graph without consistency; adapted typed relation. `C01` is additionally mandatory for the factorial contrast; `C11` is the proposed system. Four required capacity/supervision controls are causal checks, not added to or hidden inside the 13-baseline count.

### 18. Evaluation metrics

Primary: mean four-stratum recall at each system's own locked `safety_threshold` operating point (`R_safe`), with exactly 250 phishing singleton components per stratum; the two co-primary alert-level effects; actual FPR; and the prespecified FPR intervals on tester-only `primary_test`.

Secondary: normalized pAUROC at `FPR <= 0.01`, AUPRC, macro-F1/precision/recall,
specificity, confusion matrices, NLL, Brier, 15-bin ECE, AURC, risk at 90%/80%
coverage, per-slice metrics, evidence-span/endpoint metrics, q-weighted exact
labelled pair-set F1 over actor/destination `VMP` ranges and state, separately
reported `pair_emptiness_accuracy`, candidate coverage, and candidate NLL.
Freeze a separate canonical schema-`1.0.0` `registry_reference_bundle` that
binds registry snapshot, resolver, registry-manifest hash, and reference-artifact
hash. Before inference, freeze the canonical evaluation-universe `1.0.0`
manifest/hash as the complete, not sampled, nonempty UTF-8-sorted closure of one
to 10,000 eligible records in the named partition. It binds exact dataset/bundle
hashes and each partition/VMP/final annotation plus canonical versioned gold-
inventory byte size/hash; omission, extra, duplicate, or reorder invalidates
it. For `C01`/`C11`, a `VALID` metric-run `1.1.0` manifest binds exactly one
valid engine envelope per universe item in order. An `INVALID` run emits no
metrics and binds the submitted-inference manifest hash plus bounded discrepancy
counts, including disjoint universe and declared-denominator error counts, under
the exact row/outcome precedence. The deterministic strict universe receipt
precedes submission preflight, and both structural passes precede semantic
closure. Either preflight failure emits only its receipt. A structurally valid
but semantically invalid universe, including an empty one, emits the exact
universe-error invalid metric run, opens no envelope, and emits no metric.
Candidate/alignment/packet/path/nonfinite failures; any artifact/VMP/
gold/bundle/snapshot/resolver mismatch; or declared-denominator mutation invalidates the
whole run and never shrinks `N_all`. Report `N_all`, `N_gold_empty`, and
`N_gold_nonempty`. Micro path-weighted pair TP/FP/FN use weight one for `C01`
rank one and `q_k` for `C11`, and aggregate
over all `N_all`: a nonempty prediction on gold-empty contributes FP and
both-empty contributes zero counts. Pair precision, recall, and F1 are canonical
`+0.0` when their own denominator is zero; this natural case is not a declared-
denominator error. `C01` reports rank-1 metrics; `C11` reports
rank-1 and q-weighted path-marginal metrics plus conditional gold-empty and
gold-nonempty recalls when their fixed denominators are nonzero; `C00`/`C10`
report `N/A`. Report `pair_emptiness_accuracy` on all `N_all` and efficiency
only in a frozen environment. Every valid metric run has
`1<=N_all<=10000`, so pair-emptiness accuracy has a positive denominator.

For each language, report exact FPR intervals on 300 benign singleton
components. **DERIVED:** `0/300` gives an individual one-sided 95% upper bound
of `0.9936%`; only that `C11` outcome supports the phrase “individual
stratum-specific upper bound below 1%.” The simultaneous Bonferroni upper bound
at `0/300` is `1.4501%`; at least 437 independent zero-error benign records per
stratum are needed for all four below 1%. For below 0.5%, the corresponding
counts are 598 individual and 875 per stratum simultaneous. These are arithmetic
design facts, not observed results.

H1/H2 are policy-level own-threshold recall contrasts, never common-FPR
dominance or safety-superiority tests. Do not add an arbitrary underpowered FPR
noninferiority test. Comparative FPR would require a new untouched benign set,
an externally justified margin, and a paired power design frozen before access.

Statistics: the confirmatory 10,000-replicate paired bootstrap uses the same within-language sampled phishing IDs for all systems/effects and conditions on realized locked models, temperatures, and thresholds. It uses centered one-sided p-values, Holm-adjusted p-values, and joint max-error simultaneous lower bounds; any missing/nonfinite primary value invalidates the family, and abstention cannot remove primary records. The secondary Holm family is exactly H3/H4/H5a/H5b, all positive-direction; H4's exact slice/resampling remains a pre-access blocker. Broad exploration uses Benjamini–Hochberg FDR. The full formulas and tie/invalidity rules are in [PAPER_1_PREREGISTRATION.md](PAPER_1_PREREGISTRATION.md#10-statistical-analysis).

Prospective power has an assumption-labeled finite eight-cell paired-outcome sensitivity manifest followed by a development-only grouped-OOF update. The empirical gate uses 5,000 outer datasets, exact planned calibration/safety/primary counts, 10,000 inner paired resamples, and requires the exact one-sided 95% Monte Carlo lower bound on complete co-primary success to be at least 0.80; invalid fits count as failures and deterministic `PCG64DXSM` streams are manifested. A true effect of 0.03 is a boundary sensitivity case, not an automatically 80%-powered alternative. No Fisher power value is measured yet.

### 19. Ablation studies

Core 2×2; uniform candidate weights; `K = 1/2/4/8`; development-only endpoint
caps `{2,4,8}` with the primary/protected cap fixed at eight and no model
selection; no raw representation; no
auxiliary endpoint/span losses; no registry; `UNKNOWN → MISMATCH` analysis only;
no deterministic resolver input to risk; remove pressure/action/asset nodes;
entropy-only abstention; and encoder swaps.

### 20. Failure testing

Test unseen spellings, poor candidate ranking, wrong language stratum, code-mixing boundary errors, missing registry evidence, benign urgency, benign destination mismatch, promotional spam, no/obfuscated destination, Unicode and homoglyph attacks, punctuation/whitespace variants, emoji, empty/malformed/very long input, truncation, unseen templates/campaigns/authors, source shift, and abstention errors. Analyze each stage rather than attributing every miss to the classifier.

### 21. Privacy and security considerations

- consenting adults only for tester collection;
- no live OTPs, credentials, active malicious links, phone numbers, UPI IDs, or account IDs;
- `.invalid`/`.example` and defanged artifacts;
- privacy-safe equivalence keys for leakage grouping;
- immutable provenance, consent/withdrawal state, source license, and transformation lineage;
- restricted authentic raw data and separate redistribution authorization;
- poisoning, prompt-family contamination, duplicate leakage, registry tampering, Unicode evasion, and malicious-link activation tests;
- no automatic continual learning from demo users; and
- structured, bounded evidence rather than an LLM-generated justification.

Security testing cannot establish production safety; Paper 1 remains a research prototype.

### 22. Patent potential

**UNKNOWN / needs deeper professional search:** a narrowly framed bounded
candidate, predicted-endpoint resolver-state, calibrated path-risk
marginalization, and path-instability mechanism may warrant internal invention
review. Generic transliteration, graphs, source/domain comparison, scoring,
alerts, calibration, or conversations have substantial prior art. This is not a
patentability or freedom-to-operate conclusion.

No patentability, freedom-to-operate, ownership, or infringement conclusion is made. Public disclosure waits for professional counsel and a filing/no-filing decision.

### 23. Research-paper potential

The strongest route is a method-plus-benchmark paper if both co-primary hypotheses, mechanism checks, low-FPR evaluation, and data-quality gates pass. A dataset/resource paper is the honest fallback when corpus gates pass but method gains do not. A negative-result paper may be defensible if it rigorously shows where uncertainty propagation fails, but venue fit is **UNKNOWN**.

Suggested paper structure: problem and low-FPR motivation; prior-art boundary; research questions; corpus and ethics; method; preregistered experimental design; results; ablations; failure/selective-risk analysis; limitations; reproducibility; conclusion. No results section is populated before measurement.

### 24. Possible publication venues

Candidate venue families—chosen only after results and scope are known—include ACL-family Findings or workshops, ACM TALLIP, LREC-COLING/resource tracks, ICON, and FIRE. **UNKNOWN:** the best fit, current deadlines, page limits, artifact policies, anonymization requirements, and whether measured contribution clears each bar. Venue selection must not force premature disclosure or a rushed experiment.

### 25. Demo design

Use a local, offline, 30–60 second research comparison rather than a generic dashboard. A safe defanged message shows:

1. raw script/code-mix spans;
2. top candidate interpretations and calibrated weights;
3. actor/action/asset/destination nodes and per-pair compatibility states;
4. per-path risks and their marginalized result;
5. entropy and path disagreement;
6. alert/benign/abstain decision at the frozen threshold; and
7. side-by-side `C00/C10/C01/C11` behavior.

The demo must label examples as synthetic research fixtures and must not imply production protection.

### 26. Risks and limitations

- Four strata do not represent all Indian languages or dialects.
- Tester and simulation distributions may not match live attacks.
- Public spam labels do not equal phishing labels.
- 6,000 messages may contain far fewer than 6,000 independent components.
- The >=50% authentic-donation gate may be infeasible in one or more `primary_test` cells, forcing a controlled-benchmark claim.
- Registry missingness can make semantic consistency indeterminate.
- Candidate coverage/calibration may be inadequate for highly informal Romanization.
- Structured annotation is costly and may fail per-language agreement gates.
- A low empirical FPR on 300 benign singleton `primary_test` components per stratum has wide finite-sample uncertainty.
- Pooled-binomial FPR inference is invalid without a common-rate assumption across fixed language strata; only the stratified and per-language analyses support the main report.
- The power simulation's eight-cell feasibility solver, empirical grouped-OOF generator, and H4 slice/resampling rule remain **UNKNOWN** until frozen before protected access.
- Shared multilingual training may cause language-specific negative transfer.
- LLM-assisted `development` text may introduce style artifacts despite exclusion from all protected partitions.
- Name clearance, prior-art completeness, patent potential, compute, latency, and reproducibility are unresolved.

### 27. Future improvements

Only after Paper 1: Bengali/Marathi expansion through fresh independent gates; conversation progression and risk memory; warning-message HCI/user study; voice/ASR with consented audio and ASR-conditioned evaluation; QR/image/browser evidence; efficient/on-device inference; privacy-preserving or federated adaptation; active learning under adjudicator control; and longitudinal campaign shift. Each is a separate hypothesis, dataset, and ethics burden—not automatic scope.

### 28. Exact MVP

The research MVP is a passed `P0`, `D0`, and `D1` plus a frozen `E3` factorial
prototype:

- validated machine data/provenance contracts, explicit human safety/ethics audit, and synthetic fixtures;
- exactly 1,200 retained balanced double-annotated pilot items meeting every gate, with extra unresolved attempts reported;
- connected-component split tooling;
- governed transliteration-resource and offline-registry artifacts;
- one classical text baseline, complete `C00/C10/C01/C11`, and required capacity/supervision controls on `development` only;
- candidate coverage/calibration, span/endpoint, registry-reference/resolver,
  `R_safe`, FPR-bound, and AURC evaluation code; and
- reproducible configuration and manifests.

It is not a mobile app, production detector, public dataset, voice system, conversation model, or patent claim.

### 29. Exact final system

The Paper-1 final system is a validated, text-first research package containing the gated 6,000-message corpus; source/consent/provenance records; canonical group-disjoint partitions; singleton monostratal protected components; governed transliteration and registry artifacts; all baselines, 2×2 conditions, and causal controls; per-system five-seed ensembles, temperatures, thresholds, abstention, and structured evidence; one immutable tester-only `primary_test` evaluation; provenance-disaggregated statistical, ablation, failure, and efficiency reports; reproducibility artifacts; and a safe offline research demo.

Voice, conversations, vision, live messaging integration, autonomous updating, and deployment are future systems and cannot be described as completed Fisher functionality.

### 30. Week-by-week execution roadmap

The exact 24-week, gate-controlled roadmap is maintained in [WEEKLY_ROADMAP.md](WEEKLY_ROADMAP.md). Calendar dates remain unassigned until team availability, native-language coverage, ethics review path, compute, and source access are observed.

## Mapping of the required 20 phases

| Required phase | Blueprint evidence | Exit condition |
| --- | --- | --- |
| 1. Understand problem | Outputs 2–4; scoped population and failure costs | problem, assumptions, exclusions frozen |
| 2. Prior art | Output 5 and primary references | non-exhaustive matrix reviewed; no unsupported novelty claim |
| 3. Strongest novelty | Output 6, ten candidate directions | selected coupling survives feasibility/prior-art gate |
| 4. Research contribution | Outputs 7–9 | RQs, hypotheses, conditional contributions frozen |
| 5. Architecture | Output 10 plus factorial/registry protocols | module I/O, hidden-context exclusion, offline evidence, and fallback reviewed |
| 6. Model selection | Output 12 | central model and matched comparators frozen |
| 7. Dataset strategy | Output 13 plus transliteration protocol | canonical partitions, provenance/cell composition, independent protected components, and balanced 1,200 pilot pass |
| 8. Algorithm design | Output 11 plus factorial condition spec | equations, heads/losses, controls, per-system calibration/threshold, and tie behavior frozen before `primary_test` |
| 9. Build MVP | Output 28 | exact MVP acceptance complete |
| 10. Iterations | Output 15 | `P0`, `D0`, `D1`, and `E0–E5` gates pass in dependency order |
| 11. Baselines | Output 17 | all 13, `C01`, `C11`, and four causal controls reproducibly run without changing the baseline count |
| 12. Experiments | Outputs 16 and 18 | preregistered metrics/statistics complete |
| 13. Ablations | Output 19 | frozen ablation matrix complete |
| 14. Failure analysis | Outputs 20 and 26 | categorized per-stage failures reported |
| 15. Explainability/uncertainty | Outputs 10, 11, 18, 25 | calibrated selectivity and bounded evidence evaluated |
| 16. Privacy/security/ethics | Output 21 | machine invariants and separate named human ethics, safety, consent, provenance, and registry reviews pass |
| 17. Patent analysis | Output 22 and IP gate | professional filing/no-filing decision before disclosure |
| 18. Paper strategy | Outputs 23–24 | route chosen from measured gates |
| 19. Demo | Output 25 | safe offline comparison communicates method in 60 seconds |
| 20. Final critical review | risks, gates, exact final system | five-lens rejection audit closes or blocks release |

## Final critical-review checklist

Before declaring completion, conduct five independent lenses:

- **Research reviewer:** novelty survives baselines; hypotheses and multiplicity were not changed after `primary_test` access.
- **Patent examiner:** generic components are excluded; claim chart and disclosure chronology are professionally reviewed.
- **ML engineer:** no component leakage; protected components are singleton/monostratal; every system owns its five-seed calibration/threshold; runs reproduce.
- **Product/security engineer:** no unsafe artifact activation, unsupported real-time claim, or misleading confidence display.
- **Professor/project examiner:** contribution is measurable, simpler alternatives are strong, failures are visible, and the exact MVP/final boundaries are respected.

Any unresolved high-impact objection becomes a reported limitation or release blocker, not presentation polish.
