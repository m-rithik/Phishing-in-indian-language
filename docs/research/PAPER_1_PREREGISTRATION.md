# Fisher Paper 1: Preregistration Protocol

> Status: internal, embargoed, and pre-data. This protocol is a design commitment, not a report of completed experiments. Public disclosure is blocked by the separate publication/IP gate.

## 1. Study identity

**Title:** *Fisher: Uncertainty-Marginalized Transliteration and Semantic Consistency for Low-False-Positive Multilingual Indic Phishing Detection*

**One-line study:** Test whether retaining calibrated uncertainty over Romanized Indic interpretations, reasoning about semantic consistency on every interpretation, and marginalizing risk improves phishing recall at a locked low false-positive operating point.

**Evidence status:**

- **OBSERVED:** The repository contains governance and research-design artifacts; it contains no collected Fisher corpus, trained model, benchmark result, or latency measurement at protocol freeze.
- **DERIVED:** All gains, agreement values, candidate coverage, compute costs, and deployment behavior are therefore unknown until the named checks run.
- **ASSUMED:** A student research team can recruit sufficient consenting adult testers and native-language annotators. This assumption is a collection gate, not a fact.
- **UNKNOWN:** Fisher commercial-name clearance, exhaustive scientific novelty, patentability, compute availability, data yield, and achievable performance.

## 2. Scope and estimands

Paper 1 is a standalone-message, NLP-first study. Each example contains message text and, when visible in that message, a defanged destination artifact such as a URL or domain. The four mutually exclusive evaluation strata are:

1. Hindi-dominant;
2. Tamil-dominant;
3. Telugu-dominant; and
4. English–Indic code-mixed.

The annotation guide must operationalize dominance and code-mixing before collection; a record cannot belong to more than one stratum. Conversation history, voice/ASR, images, QR codes, browser context, deployment claims, and warning-user studies are outside Paper 1.

The semantic target is binary `phishing` versus `benign`. Nonmalicious
promotion is a benign subtype, not a third headline class. `uncertain` is a
workflow/abstention state, not semantic gold. Every condition receives only a
`VisibleMessagePacket` (`VMP`): exactly schema-`1.2.0` `item.text` plus the
non-gold, pre-annotation `item.visible_artifacts` inventory, bound by required
`item.vmp_sha256`. Annotations consume but never construct or infer it. The
artifact grammar and exact Unicode-code-point destination-span binding in the
[data contract](../DATA_CONTRACT.md#visible-non-gold-artifact-inventory-and-vmp)
establish syntactic representation safety only, not authenticity, semantic
type, collection authority, or release authority. Human gold covers primary
label, subtype,
language, facets, spans, supporting evidence, and visible actor/destination
endpoints. Provenance, source label, donor intent, scenario, prompt, campaign,
grouping identifiers, registry information, and hidden context never decide
gold.

For system `m` and language stratum `l`, let `P_l` be the 250 audited phishing singleton components in `primary_test`, and let `A_mi = 1[p_m(x_i) >= theta_m]`, where `theta_m` is that system's own frozen threshold. Define alert-level recall `R_l(m) = (1/250) * sum_{i in P_l} A_mi` and the unweighted four-stratum estimand `R_safe(m) = (1/4) * sum_l R_l(m)`. The co-primary effects are `Delta1 = R_safe(C11) - R_safe(C01)` and `Delta2 = R_safe(C11) - R_safe(C10)`. These estimands condition on each realized locked system, temperature, and threshold; they do not place all systems at a shared threshold.

Results must also report the observed benign false-positive rate and the prespecified intervals in Section 10. The primary population is protocol-eligible tester-originated standalone messages, not public-source data and not all Indian messaging traffic. Authentic tester donations and tester-authored simulations must be reported separately.

## 3. Proposed method and novelty boundary

Every factorial message run configures the same frozen provider/configuration:
exactly one `COMPOSED_SPAN` or `DIRECT_FULL_PATH` provider. `C00`/`C01`
activate its returned rank-one path; `C10`/`C11` activate all returned paths.
`IDENTITY_BYPASS` is a candidate-output artifact, not a configured provider.
Composed and direct are separate named configurations/runs/ablations and never
pool logits or paths inside one `q`. The canonical per-message provider-reading
manifest fixes exact IDs/modes/units/readings/f64 bits/bytes/hash and the ordered
`rewrite_spans`; successful composed and direct modes require 1..64 spans,
while an effective identity output has none.
Composed mode has one unit and at most eight readings per span; direct mode has
one full-path unit and at most eight
readings, and bypass has no units. A direct full-path reading preserves every
non-rewrite VMP code point and visible-artifact slice exactly and may change
text/alignment only within those manifest-bound spans. Span text is bounded at 512 code points/2,048
bytes, full paths at 20,000/80,000, and the manifest at 4 MiB; overflow rejects.

Each Romanized span cannot overlap a visible artifact. Every configured or
effective `span_index`, `start`, and `end` is a non-Boolean integer; indices are
contiguous from zero; `0 <= start < end <= len(VMP.text)`; source text is the
exact slice; and spans are sorted and nonoverlapping. Every input and
normalized output Unicode code point has exactly one
nonempty contiguous `VMP` interval: starts and ends are separately
nondecreasing, equal/overlap is allowed, every rewrite interval remains within
one source span, and the union covers every source code point. Noncandidate
code points use identity alignment. The normalizer is the frozen
alignment-aware transducer `(candidate_text,candidate_alignment) ->
(normalized_text,normalized_alignment)` and rejects every length, integer,
bounds, emptiness, monotonicity, span, coverage, nonspan-change, or
visible-artifact violation specified in
[ENGINE_SPEC.md](ENGINE_SPEC.md#3-candidate-construction). Candidate merge
identity is `(normalized text, alignment)`. `E0` uses only the identity
normalizer and proves no linguistic normalization.

Normalize span logits and compose full messages while preserving all non-span
`VMP` bytes. Use an overflow-safe product of post-span-merge counts to choose
exact enumeration at at most 64, otherwise a width-64 beam. Each beam expansion
merges exact `(emitted normalized prefix, alignment)` keys using manifest-bound
canonical compact contributor lineage without exponential cross-product
expansion, canonical operand order, and sequential stable binary64
max-shift `logsumexp`, then prunes by score, UTF-8 text, encoded alignment, and
contributor identity.
Each provider reading has raw identity `(unit_index,provider_rank)`; ranks are
unique `1..8` within a unit and may reset across units. Duplicate merges preserve
the exact mode-specific contributor JSON and canonical contributor-byte order;
every LSE uses that order. Bit replay is claimed only in the pinned
runtime/container, not universally across platforms.
Return at most `K = 8` under the same order without padding. Reject nonfinite
values and canonicalize signed zero to positive zero before comparisons or
serialization. Candidate weights use the runtime-bound binary64 construction:
divide scores by `T_tr`, max-shift, exponentiate, sequentially sum numerators in
ascending full-contributor-lineage bytes, then divide. Per-path numerator/
weight plus the maximum and normalizer are persisted as binary64 bits.
Retained mass is computed in the log domain as
`exp(LSE(returned)-LSE(preK))`, persisted only as
`retained_preK_composition_mass_f64_bits` with
`preK_scope=EXACT_FULL|FINAL_BEAM` and both LSE operands. Empty,
nonfinite, or positive-delta results are invalid and are never clamped. Exact
mode uses the complete enumerated merged set as `preK`;
beam mode uses only its final bounded merged pre-`K` set and must never imply
total-lattice posterior mass.
The exact algorithm and selection rule are frozen in
[ENGINE_SPEC.md](ENGINE_SPEC.md#3-candidate-construction).

Fit `T_tr` only after selecting the generator on
`transliteration_development`, using group-disjoint message-level
transliteration calibration. Word-pair data cannot establish multi-span
calibration. Phishing labels never update `q`.

The only valid bypasses are `NO_ELIGIBLE_ROMANIZED_SPAN` and
`PROVIDER_FAILURE_RAW_FALLBACK`, each an identity-aligned raw path with `s=0`
and `q=1`. The exact `provider_execution` object in the canonical engine run
envelope binds configured mode/IDs/hashes, eligible or attempted spans,
invocation, bypass reason, failure code, and provider-reading-manifest hash.
An invalid selector result before dispatch has the separate
`ELIGIBILITY_INVALID` outcome, empty retained eligible spans, bounded selector-
entry and zero accepted-span counts, no output hash/candidates/downstream
artifacts, and an `INVALID` provider-execution-stage envelope. An invalid
rewrite/alignment after an accepted provider manifest remains `CANDIDATE`.
No-eligible execution has no spans and is not degraded. Provider or normalizer
unavailability/timeout before accepting any output may retain its attempted
1..64 spans only in `provider_execution`, has no effective rewrite span, and is
`DEGRADED_STOP_AFTER_IDENTITY` only if the exact identity fallback validates;
processing stops before prediction. It is never coverage
success and invalidates confirmatory or protected metric runs; `E0` tests
accounting only. Malformed, nonfinite, alignment-invalid, provider-invalid, or
normalizer-invalid output is `INVALID`, not degraded. An empty enabled
candidate set outside these modes is invalid. The `E0` identity normalizer is
synthetic-only and proves no linguistic normalization.

A shared encoder predicts visible nodes, spans, bounded actor/destination
endpoint sets, and path-risk logits. Endpoints are deduplicated by
the exact `(role,start,end,kind,lookup_surface,lookup_status)` audit tuple,
retain the highest score, and are
capped at eight per role by descending score then frozen `VMP`
range/kind/status/lookup UTF-8 ties. After cap, packet order is independently
score-free. Actors use `ACTOR/NONE`; destinations use
`DESTINATION/<controlled kind>`; status is `ALIGNED|UNALIGNED`; aligned surfaces
equal bounded renderer output and unaligned surfaces are empty. Scores remain
only in the canonical prediction audit as finite big-endian binary64 bit
strings; negative zero is canonicalized to positive zero. Emission indices,
score association, highest-score deduplication, equal-score lowest-index
tie-breaks, pre-cap counts, cap hits, selected indices, exact compact bytes, and
SHA-256 are frozen in the engine contract. The cap is an
engineering bound, not a performance result. Endpoints are predicted only in
`VMP` coordinates; candidate-offset back-projection is prohibited.

For path `k`, let `A_k` and `D_k` be those endpoint sets. Only semantic
conditions construct the canonical Cartesian compatibility packet

`E_k = {(a,d,Resolve_R(a,d)) : a in A_k, d in D_k}`.

An empty product makes no calls or rows and has implicit `N/A`; it is not an
explicit reference label. Pair order follows actor then destination endpoint
keys. Lookup surfaces substitute fully enclosed candidate spans. A cut-through
endpoint is `UNALIGNED` and every affected pair is `UNKNOWN`.
It short-circuits before registry with engine-only `NOT_EVALUATED`,
`ALIGNMENT_GUARD`, empty evidence IDs, and zero registry calls.
That zero applies to each affected pair; other aligned pairs in the same packet
may still call the registry.

Let `pi_k(s)` be equal-weight state prevalence over nonempty `E_k`, or
`1[s=N/A]` when empty, and define

`P_pair(s|x) = sum_k q_k pi_k(s)`.

`P_pair` is diagnostic only; the complete pair packet is an audit record, not a
risk input. It includes exact endpoint audit fields, call count, bounded safe
evidence IDs, resolution coherence, and 16-MiB rejection bound under the fixed
field inventory/order and compact UTF-8 JSON bytes frozen in
[ENGINE_SPEC.md](ENGINE_SPEC.md#4-factorial-engine-and-canonical-pair-packets),
including required `vmp_sha256`, path text/alignment-bound `path_sha256`, and
the pair-packet hash.

Risk consumes only the exact `SemanticFeaturePlan` projection. Plan coordinates
are indexing instructions, never numeric risk features. For `E0` only,
`E0_VMP_CATEGORY_MEAN_V1` deterministically builds a five-dimensional binary64
VMP grid in the order `LETTER,MARK,DECIMAL_DIGIT,WHITESPACE,OTHER`, using the
pinned Unicode category followed by pinned `str.isspace`; it uses sequential
binary64 range means and the frozen one-hot category/status/state/coverage/source
order to produce 31-dimensional pair rows, a 64-row Boolean mask/zero-padded
tensor, exact bit strings, canonical bytes, and a hash. Literal surfaces, IDs,
hashes, evidence, scores, provider ranks, candidate weights, and score-derived
order never enter risk; `q` is used only after per-path risk. This is an exact
synthetic interface test, not a transformer-feature claim. A separate future
candidate/subword-to-VMP adapter and feature-plan version remain unimplemented
and must be frozen before `E3`.

Registry state is deterministic, not a learned relation target. A learned loss
that reproduces a registry state already supplied to the risk path was rejected
as circular; endpoint/span supervision remains.

For system `m`, average five seed path logits before calibration:

`bar_ell_mk = (1/5) sum_j ell_mjk`.

Fit one positive `T_m` per system using only `probability_calibration` by
minimizing binary NLL of the marginalized `p_m` below, then:

`rho_mk = sigmoid(bar_ell_mk/T_m)`,

`p_m(x) = sum_k w_mk rho_mk`,

`v_m(x) = 4 sum_k w_mk (rho_mk-p_m(x))^2`, and

`u_m(x) = 0.5 H(p_m(x))/log(2) + 0.5 v_m(x)`,

where `w_m1=1` for rank-one `C00`/`C01`, `w_mk=q_k` for all-path
`C10`/`C11`, `H(p) = -p log(p) - (1-p)log(1-p)`, and `0 log(0)=0`.

Top-1 has `v_m=0`. Alert, entropy, threshold, and disagreement use this same
calibrated object. Common-delta calibration was rejected as nonidentified;
raw-disagreement plus calibrated entropy was rejected as scale-incoherent.
Entropy-only remains an ablation. Exact optimizer bounds/failure behavior remain
an **UNKNOWN pre-`E4` freeze requirement**.

**DERIVED proposed contribution:** the narrow research claim is the coupling of
bounded calibrated candidate weights, predicted-endpoint structured reasoning,
deterministic offline relation resolution, calibrated risk marginalization, and
entropy-plus-path-disagreement abstention.

The following are established ingredients or comparators and must not be claimed as Fisher inventions: N-best or lattice transliteration, IndicXlit/Aksharantar, MuRIL, XLM-R, IndicBERT v2, IndicLID, typed graphs, generic brand/domain matching, multitask learning, calibration, selective prediction, or explanations. A generic `transliterate → graph → brand/domain comparison → score → alert` pipeline is incremental and subject to prior-art and patent pressure.

## 4. Research questions and hypotheses

### Primary research question

Does uncertainty-marginalized transliteration improve campaign- and author-disjoint phishing detection at a low false-positive operating point over one-best transliteration, and is that improvement specifically enabled by semantic consistency?

### Core factorial conditions

| Condition | Transliteration handling | Semantic consistency |
| --- | --- | --- |
| `C00` | returned rank-one path from the frozen provider/configuration | absent |
| `C10` | calibrated weighted paths | absent |
| `C01` | the same returned rank-one path as `C00` | present |
| `C11` | calibrated weighted paths | present; proposed full method |

All four cells use the same partitions, `VMP`, encoder, update budget, tuning
policy, seed schedule, and frozen candidate provider/configuration. `C00`/`C10`
construct no endpoint, audit packet, feature plan/token, or resolver call.
`C01` constructs returned-rank-1 audit/plan only;
`C11` constructs them for every returned path and uses q only after path risk.
`C01` applies
endpoint/span loss on rank 1; `C11` uses `sum_k q_k` path losses. Capacity
controls receive no semantics. Supervision controls preserve those auxiliary
losses but may not construct/call/expose endpoint predictions, packet, plan,
tokens, registry state, or missingness to risk. Full access and loss rules are frozen in
[FACTORIAL_CONDITION_SPEC.md](FACTORIAL_CONDITION_SPEC.md).

### Confirmatory hypotheses

- **H1 (co-primary):** `H0: Delta1 <= 0` versus `HA: Delta1 > 0`.
- **H2 (co-primary):** `H0: Delta2 <= 0` versus `HA: Delta2 > 0`.
- **H3 (secondary mechanism):** let `S(C) = -NLL(C)`; `[S(C11) - S(C01)] - [S(C10) - S(C00)] > 0`.
- **H4 (secondary mechanism):** define `Delta_uncertainty(slice) = S_slice(C11) - S_slice(C01)` with `S = -NLL`; test `Delta_ambiguous > Delta_nonambiguous` using the frozen paired `development`/`primary_test` analysis. Fix the ambiguity-slice rule before observing any model result.
- **H5a (secondary selectivity):** define the positive-direction effect `Delta5a = AURC(C01) - AURC(C11)` and test `Delta5a > 0`.
- **H5b (secondary selectivity):** define the positive-direction effect `Delta5b = AURC(C10) - AURC(C11)` and test `Delta5b > 0`.

The co-primary family succeeds only if, for both effects, the unrounded observed `Delta >= 0.03`, the Holm-adjusted one-sided `p <= 0.05`, and the corresponding joint familywise simultaneous one-sided lower bound is strictly greater than zero. Rounded table values never determine the decision. Failure to satisfy every gate for both H1 and H2 blocks a full-method superiority claim and does not authorize metric substitution after `primary_test` inspection.

## 5. Corpus design and provenance restrictions

### Main target

The main corpus target is 6,000 retained unique messages: 1,500 per stratum, with 750 phishing and 750 benign in each. Before expansion, the retained binary ontology pilot contains exactly 1,200 items: 300 per stratum and 150 per label per stratum.

Every attempted pilot item receives exactly two valid blind independent annotations from distinct annotators and exactly one semantically valid final record from a third distinct annotator. The final record is the deliberate conflict-resolution/adjudication record, is marked `independent: false`, and is required even when the two blind annotations agree. Items still unresolved after adjudication are assigned `excluded` and are extra attempted items, not part of the balanced 1,200 retained binary pilot. The unresolved rate is `unresolved / (1,200 retained + unresolved)` and must be at most 5%. Collect replacements under the same sampling rule; do not remove difficult but resolved items, change denominators, or cherry-pick replacements to improve agreement.

Tester-donated authentic, tester-authored simulation, public-source authentic, and LLM-drafted/human-edited ancestry remain distinct at row level and propagate to every descendant. The LLM cap is `development records with any LLM ancestor / 3,000 retained development records <= 0.30`; LLM ancestry is prohibited from `probability_calibration`, `safety_threshold`, and `primary_test`. Public-source items and descendants are allowed only in `development` or `external_test`. No LLM or public-source label supplies Fisher gold without visible-input human annotation.

`primary_test` is tester-originated only: tester-donated authentic or tester-authored simulation. In each of its eight label×stratum cells, at least 50% must be tester-donated authentic—at least 125 of each 250-item phishing cell and at least 150 of each 300-item benign cell. Report every primary metric separately by these two provenance groups. If any cell cannot meet this gate, the study routes to a controlled-benchmark/research-prototype claim and cannot make field-like generalization claims.

`probability_calibration` and `safety_threshold` must also have zero public and zero LLM ancestry; report their tester-donation/simulation composition by stratum and label where applicable.

### Canonical partition vocabulary

The only valid Fisher partition values are `pilot`, `unassigned`, `development`, `probability_calibration`, `safety_threshold`, `primary_test`, `external_test`, and `excluded`. `train`, `training`, `dev`, `validation`, `calibration`, `test`, and `locked_test` are not aliases in data records; other informal names are invalid too. `development` alone supports fitting, grouped cross-validation, hyperparameter selection, and early stopping.

### Exact main partitions

| Partition | Per stratum phishing | Per stratum benign | Per stratum total | Four-stratum total | Permitted use |
| --- | ---: | ---: | ---: | ---: | --- |
| `development` | 450 | 300 | 750 | 3,000 | fitting, grouped CV, tuning |
| `probability_calibration` | 50 | 50 | 100 | 400 | system-ensemble scalar temperature and selective cutoffs only |
| `safety_threshold` | 0 | 100 | 100 | 400 | system-ensemble low-FPR threshold only |
| `primary_test` | 250 | 300 | 550 | 2,200 | one final confirmatory evaluation |
| **Total** | **750** | **750** | **1,500** | **6,000** | |

The absence of phishing examples in `safety_threshold` is intentional. `probability_calibration`, `safety_threshold`, and `primary_test` cannot select an architecture, hyperparameter, feature, candidate, registry entry, checkpoint, or seed.

### Dependence and leakage controls

Create connected components across exact/near duplicates, translation/transliteration/paraphrase/counterfactual parents, scenario/template/campaign, safe-equivalence destination/sender identifiers, tester author, donation batch, source family, and LLM prompt family. A component cannot cross partitions or grouped-CV folds. Direct phone, UPI, account, sender, or live-domain identifiers must not be retained solely for grouping; use approved privacy-safe equivalence keys.

Every `probability_calibration`, `safety_threshold`, and `primary_test` component must contain exactly one retained message and exactly one language stratum. Audit component construction before protected access. These singleton, monostratal protected components are required for the planned per-message exact-binomial interpretation and language-stratified paired bootstrap. If `primary_test` cannot supply 300 independently grouped benign singleton components in every stratum, report the achieved sample and interval but make no per-stratum below-1% FPR claim.

Deduplication and component construction occur before model fitting. Fit tokenizers and feature transforms only within `development`; freeze the offline registry before protected access; use `probability_calibration` and `safety_threshold` only as specified below. `primary_test` remains inaccessible until pilot, provenance, independence, model, and analysis gates pass.

## 6. Annotation targets and pilot acceptance

Blind annotators and the final adjudicator annotate the primary label, benign
subtype, language stratum, facets, evidence spans, and visible actor/destination
endpoints from the `VMP` only. They receive neither registry nor provenance. A
separate blinded registry reviewer later resolves the canonical Cartesian
product of final visible actor and destination endpoint sets against the frozen
registry, without the primary label, provenance, or protected outcomes, and
writes a separately versioned registry-reference artifact. This is a
compatibility inventory, not a human actor-to-destination link. Registry-derived
state is not blind human gold. Reference rows are exactly
`MATCH|MISMATCH|UNKNOWN`; an empty product yields no calls, zero rows, and
implicit runtime `N/A`.

Before blind release, freeze a prospective structured-state coverage manifest.
In each stratum it targets at least 30 candidate visible-explicit and 30
no-visible-explicit items for each of six facets, plus at least 30 planned
candidates for each resolver state. Tags are hidden non-gold sampling metadata;
they cannot populate or correct endpoints, labels, or registry references. The
count of 30 is a coverage minimum, not power, precision, prevalence,
independence, performance, or reliability evidence.

**OBSERVED:** `E09` independently passes the scoped schema-1.2 syntactic VMP
repair. `E10` independently passes the original E08 repairs but fails four new
provider/lineage, endpoint/feature, boundedness, and metric-binding blockers.
`E11` independently passed those second-repair requirements but failed five
further provider-execution/run-envelope, endpoint-numeric, E0-feature,
evaluation-universe, and coordinate-predicate requirements; 101/101 tests did
not execute an engine. `E12` then failed five remaining status-union,
causal-control, evaluation/gold-binding, system-provenance/five-seed, and
candidate-diagnostic/`q` requirements. `E13` then failed three remaining
preflight/run-union, failure-accounting, and metric-input/counting groups. `E14`
passes those repairs and the other major contracts but finds three engine-
descriptor/parser, eligibility-accounting, and metric-universe/denominator/
algebra blocker groups. `E15` passes those repairs and the previously reviewed
surfaces but finds three remaining strict universe-input parser/count,
structural-versus-semantic precedence, and nonempty-denominator blocker groups.
**P0 blocker:** fresh independent replay of this eighth local, universe-only docs repair remains
required.
Subject to that review and every upstream gate,
the 1,200-message pilot passes only if every following condition holds; any
undefined gated metric fails:

- binary-pair coverage is at least 0.95;
- raw pre-adjudication binary agreement is at least 0.90;
- binary nominal Krippendorff alpha is at least 0.80;
- five-state language nominal Krippendorff alpha is at least 0.80;
- each of the six facet-applicability nominal alphas is at least 0.67;
- endpoint-aware actor, action, and destination alpha is at least 0.60 in every
  final-known language stratum for each named target;
- for each of all six facets, exact-span F1 is at least 0.60 and character-overlap F1 is at least 0.75 on the frozen union-explicit denominator;
- mechanically derived Cartesian endpoint-inventory exact F1 is at least 0.60;
  annotators never link actor/destination pairs or label registry state;
- supporting-evidence exact F1 is at least 0.60 and supporting-evidence character-overlap F1 is at least 0.75;
- attempted-item completeness is at least 0.95;
- unresolved adjudication, computed as `all excluded attempts / (1,200 retained pilot items + all excluded attempts)`, is at most 0.05;
- retained-pilot arithmetic is exactly 1,200 total, exactly 300 in each of four strata, and exactly 150 benign plus 150 phishing in each stratum; and
- the [canonical human pilot safety and provenance audit](ANNOTATION_GUIDE.md#canonical-human-pilot-safety-and-provenance-audit)
  takes exactly `ceil(0.10*N_attempted)` main bundles and records zero prohibited
  findings. Freeze the initially missing annotator IDs, process them once in
  UTF-8 byte order, skip an ID already covered by an earlier supplement, and
  otherwise choose its lowest-HMAC-ranked unselected eligible bundle. No
  supplement replaces the main sample.

If any gate fails, revise the ontology/guide and repeat an appropriately powered pilot round. Do not silently discard difficult examples to pass.

## 7. Training, calibration, and threshold protocol

`development` uses grouped, component-disjoint 3-fold cross-validation. For every fixed system ensemble—baseline, factorial condition, or required control—train seeds `11, 23, 37, 53, 71` under the frozen development procedure. Report seed/fold results and never select the best seed. Freeze hyperparameters and stopping rules before protected access.

Each run binds the exact `SystemArtifactManifest`, complete executed-source
closure, runtime/environment/math backend, system/control identity, and direct
registry/provider/model/resource/analysis bindings through the schema-`1.1.0`
engine envelope. Source/configuration or VMP failure before those bindings emits
only `EnginePreflightReceipt`. The envelope's
`VALID|DEGRADED_STOP_AFTER_IDENTITY|INVALID` union retains only fully validated
upstream artifacts under its exact stage table. The canonical `FiveSeedLogitArtifact` binds the fixed seed
order, active paths, finite binary64 logits, sequential binary64 mean, and
system-artifact hash. `E0` checks known-answer arithmetic only; real model
logits/checkpoints and the temperature optimizer remain **UNKNOWN** until their
named later gates.

For each fixed system `m`, average its five logits for each returned path,
calibrate those averaged path logits with the system's one pooled scalar
temperature on the shared 400-item `probability_calibration`, and marginalize
the calibrated path probabilities with `q`. Never fit per-seed, per-language,
or shared-system temperatures. Score the 400 benign `safety_threshold` items
with `p_m` and set that system's float64 threshold to
`nextafter(max p_m, +infinity)`. Equality alerts; NaN or a missing/nonfinite path
invalidates the run. Freeze dtype, bits, ties, and boundaries. Never adjust after
`primary_test` access.

### Pre-protected-access power protocol

Power assessment has two stages, neither of which uses a Fisher protected partition or supplies a measured Fisher result.

1. **Assumption-labeled sensitivity stage.** For each language, model the three paired Bernoulli alerts `(C11, C01, C10)` on a phishing singleton as one eight-cell multinomial outcome. A finite, versioned scenario manifest contains the explicit eight cell probabilities for each stratum. The required scenario list is the 12 combinations of comparator recall `r in {0.50, 0.70, 0.85}`, common true effect `delta in {0.03, 0.05}`, and pairwise discordance regime `{minimum-feasible, maximum-feasible}` applied to both `C11-C01` and `C11-C10`; each scenario sets both comparator marginal recalls to `r` and the `C11` marginal to `r11 = r + delta`. For either pair, discordance is `P(A_C11 != A_comparator)`, with extremes `d_min = delta` and `d_max = min(r11 + r, 2 - r11 - r)`. The manifest must record any additional constraint needed to identify a valid joint eight-cell distribution. The deterministic feasibility solver, its tolerance, and its tie-break are **UNKNOWN** and must be frozen and independently checked before this stage can run. Infeasible scenarios remain in the manifest with an explicit reason; they are not silently replaced. The `delta = 0.03` scenarios are boundary/sensitivity cases, not alternatives assumed to have 80% power.
2. **Development-only empirical update.** After system design is frozen but before any protected access, use grouped out-of-fold `development` score/component tuples to generate 5,000 outer synthetic datasets. Every outer dataset reproduces the planned per-stratum counts—50 phishing and 50 benign for probability calibration, 100 benign for threshold construction, and 250 phishing plus 300 benign for primary evaluation—and redoes each system's scalar calibration and own-threshold construction. It then applies the exact confirmatory decision below using 10,000 inner paired resamples. Sampling must preserve the fitted grouped-OOF dependence representation specified in the simulation manifest; the exact empirical generator remains **UNKNOWN** until frozen before the update.

The empirical gate passes only if the exact one-sided 95% Clopper–Pearson lower bound on the proportion of the 5,000 outer datasets that satisfy the complete co-primary decision is at least 0.80. An invalid/nonfinite calibration, threshold, score, resample family, or decision counts as a failed outer dataset; it is never deleted. Use deterministic NumPy `PCG64DXSM` streams with a versioned root seed, named child-stream derivation, library/runtime versions, code hash, scenario-manifest hash, and output hash. A failed gate triggers more independent components or a narrower claim, not post hoc relaxation. No power value is reported as measured until this procedure is implemented and run.

## 8. Comparators and compute matching

The 13 planned baselines/component comparators are:

1. deterministic suspicious-pattern rule system;
2. destination-artifact logistic regression;
3. word TF-IDF logistic regression;
4. character TF-IDF logistic regression;
5. combined word/character TF-IDF linear SVM;
6. raw-text MuRIL classifier;
7. raw-text XLM-R base classifier;
8. raw-text IndicBERT v2 classifier;
9. `C00` one-best, no semantic consistency;
10. flat top-K augmentation without candidate probabilities;
11. `C10` weighted paths without semantic consistency;
12. node graph without the consistency relation mechanism; and
13. adapted typed-relation baseline.

`C01` is additionally mandatory as the one-best semantic cell required for H1, and `C11` is the proposed system. Thus, the complete experimental matrix includes the 13 listed baselines/component comparators plus `C01` and `C11`; the same model may fill two roles only if this is stated without double-counting evidence.

The four required capacity/supervision controls in [FACTORIAL_CONDITION_SPEC.md](FACTORIAL_CONDITION_SPEC.md) do not change the 13-baseline count. The exact eight allowed condition/variant combinations use `system_variant=BASE|CAPACITY_CONTROL|SUPERVISION_CONTROL`: capacity controls at `C00`/`C10` are artifact-bound to the corresponding semantic `C01`/`C11` bases, while supervision controls at `C01`/`C11` preserve auxiliary supervision but prohibit endpoint, SEP, registry, or semantic tensors at risk-visible inference. `E0` validates manifests/masks only; the ordinary trained capacity adapter is later work. A semantics claim must survive these controls rather than attribute extra heads, labels, or parameters to consistency reasoning.

Classical models receive nested development-only tuning. Neural comparisons receive matched encoder size where applicable, data exposure, update budget, tuning trials, early-stopping information, and seed schedule. Record actual parameter count, peak memory, train time, and inference latency when measured; no compute value is assumed here.

## 9. Outcomes and reporting

### Primary reporting

- `R_safe`: unweighted mean of four stratum-specific phishing recalls at the locked threshold;
- each stratum's recall, precision, specificity, and confusion matrix;
- actual macro and per-stratum benign false-positive rates with the prespecified intervals, plus any pooled-binomial sensitivity labeled with its additional assumption; and
- both co-primary paired contrasts, raw and Holm-adjusted one-sided p-values, and joint familywise simultaneous one-sided lower bounds.

### Secondary reporting

- normalized partial AUROC for `FPR <= 0.01` and AUPRC;
- macro-F1, precision, recall, specificity, and full confusion matrices;
- NLL, Brier score, and 15-bin expected calibration error;
- area under the risk–coverage curve and risk at 90% and 80% coverage;
- per-stratum and preregistered slice results;
- evidence-span exact/overlap F1 and visible-endpoint metrics;
- q-weighted exact labelled pair-set F1 over actor/destination `VMP` ranges and
  state against the bundle-bound audited registry reference, plus
  separately reported `pair_emptiness_accuracy`;
- transliteration candidate coverage and candidate NLL; and
- measured parameter count, latency, memory, and throughput when the measurement environment is frozen.

Freeze the exact canonical `registry_reference_bundle` schema `1.0.0`. Before
inference, freeze the canonical evaluation-universe `1.0.0` manifest and its
hash. It is the complete, not sampled, nonempty UTF-8 item-ID-sorted closure of every
validated item in the named partition that is retained, binary final,
study-stratum-known, VMP-valid, and has complete final endpoint/reference
inventory; it has between one and 10,000 entries when semantically valid. Each entry binds partition, VMP,
final annotation, the exact byte size/hash of its canonical versioned gold
inventory, gold pair count, and emptiness. Omission, extra, duplicate, or
reorder invalidates the universe.

For `C01`/`C11`, the discriminated metric-run `1.1.0` manifest derives
`N_all`, `N_gold_empty`, and `N_gold_nonempty`. A `VALID` run binds exactly one
valid engine envelope per universe item in universe order. An `INVALID` run
emits no metrics and instead binds the submitted-inference manifest hash plus
bounded submitted/missing/extra/duplicate/reordered/degraded/invalid/mismatch
counts plus disjoint universe and declared-denominator error counts under the
frozen left-to-right and exclusive-envelope precedence; it
does not pretend the invalid submission satisfies valid equality. Malformed,
oversized, non-UTF-8, noncanonical, or row-oversized raw input emits only a
bounded `MetricInputReceipt`, with no metric-run manifest or metric value.
Universe bytes first pass the strict, deterministic one-code
`MetricUniverseInputReceipt`; submission preflight against its computed hash
comes second, and semantic closure validation comes third. Either structural
preflight failure emits only its receipt. A structurally valid but semantically
invalid universe, including `entries=[]`, emits the exact universe-error
`MetricRunManifest INVALID`, opens no envelope, uses no submitted row for
comparison, and emits no metric. A natural zero denominator in pair precision,
recall, or F1 produces canonical `+0.0`; it is not a declared-denominator error.
Any VMP/gold/bundle/snapshot/resolver mismatch, path/nonfinite failure, or
declared-denominator mutation invalidates the whole run and never shrinks the frozen
universe. The exact field inventories, canonical bytes, bounds, and hashes are
frozen in
[ENGINE_SPEC.md](ENGINE_SPEC.md#43-canonical-evaluation-universe-and-pair-metric-run).

For message `i`, let `G_i` be the exact reference tuple set and `E_ik` the
predicted tuple set for path `k`, with tuple
`(actor_start,actor_end,destination_start,destination_end,state)` in `VMP`
coordinates. Across every `N_all` item accumulate micro
`TP=sum_i,k w_ik |E_ik intersect G_i|`,
`FP=sum_i,k w_ik |E_ik minus G_i|`, and
`FN=sum_i,k w_ik |G_i minus E_ik|`, where `w_i1=1` for `C01` and
`w_ik=q_ik` for `C11`; report pair precision, recall, and
`F1_pair=2TP/(2TP+FP+FN)`. Each is canonical `+0.0` when its own denominator is
zero, identically for rank-1 and q-weighted forms. Gold-empty nonempty prediction contributes FP;
both-empty contributes zero counts. Separately
report `pair_emptiness_accuracy=(1/N_all) sum_i,k w_ik
1[empty(E_ik)=empty(G_i)]` and fixed-denominator conditional empty/nonempty
recalls. `C11` reports rank-1 and q-weighted; `C01` rank-1; `C00`/`C10` `N/A`.
Every `VALID` run has `1<=N_all<=10000`, so the pair-emptiness denominator is
positive.
Neither
statistic is blind relation IAA, and neither licenses a learned registry-state
loss.

Accuracy alone cannot support a claim. A confidence interval on FPR is mandatory; 300 independently grouped benign `primary_test` messages per stratum does not guarantee an FPR below 1%.

For zero false positives among `n` independent benign records, the one-sided
exact 95% upper bound is `1 - 0.05^(1/n)`. **DERIVED:** `n=300` gives
`0.9936%`. Therefore an individual stratum-specific below-1% statement is
available only for exactly `0/300` observed false positives. For simultaneous
four-stratum Bonferroni inference, `1-(0.05/4)^(1/n)` is `1.4501%` at `n=300`,
and at least `437` independent zero-error benign records per stratum are needed
for a simultaneous below-1% statement. For below `0.5%`, the corresponding
zero-error counts are `598` for an individual stratum and `875` per stratum for
all four simultaneously. These are arithmetic design properties, not Fisher
results.

## 10. Statistical analysis

### Confirmatory paired bootstrap

Condition on the realized locked models, five-seed ensemble logits, temperatures, and own-system thresholds; confirmatory resampling does not refit or reconstruct any of them. Draw 10,000 language-stratified paired bootstrap replicates. In each stratum, sort the 250 phishing IDs by UTF-8 bytes, sample integer positions with replacement, and use that identical sampled-ID vector for `C11`, `C01`, and `C10` and for both co-primary effects. Use NumPy `PCG64DXSM` with root seed `20260819` and named child stream `confirmatory-primary`; freeze the NumPy version and child-stream derivation in the analysis manifest. Selective abstention is analyzed separately and cannot remove, replace, or complete-case-filter any primary record.

For positive-direction effect `Delta_j`, let `Delta_j^(b)` be replicate `b`, let `Delta_hat_j` be the observed estimate, and define centered error `E_j^(b) = Delta_j^(b) - Delta_hat_j`. For `H0: Delta_j <= 0`, the centered one-sided p-value uses the right tail: `(1 + sum_b 1[E_j^(b) >= Delta_hat_j]) / 10001`. Order raw co-primary p-values ascending, breaking an exact tie by hypothesis ID (`H1` before `H2`), and compute Holm adjusted values as the monotone running maximum of `(2-k+1) * p_(k)`, capped at one. The sequential Holm rejection rule and adjusted values must agree.

Confidence bounds are not called Holm-adjusted intervals. Using the same `E_j^(b) = Delta_j^(b) - Delta_hat_j`, define `M^(b) = max(E_1^(b), E_2^(b))`. Sort the 10,000 finite `M^(b)` values ascending and set `q_0.95` to the 9,501st value (one-indexed), the `ceil(0.95 * (B + 1))` order statistic for `B = 10,000`; the simultaneous lower bounds are `L_j = Delta_hat_j - q_0.95`. Store the software/runtime versions and the sorted-order checksum in the analysis manifest. Any missing/nonfinite primary score, effect, or bootstrap value invalidates the entire co-primary family; complete-case deletion is prohibited.

### False-positive-rate inference

Within each language stratum, report the observed FPR among its 300 benign singleton `primary_test` components with a two-sided 95% Clopper–Pearson interval and a one-sided 95% Clopper–Pearson upper bound. Their binomial interpretation assumes independent, identically distributed Bernoulli errors within that stratum after the singleton audit. Report macro FPR as the unweighted mean of the four stratum estimates. Its 95% interval is a 10,000-replicate language-stratified percentile bootstrap: sort IDs by UTF-8 bytes, resample the same 300 benign IDs within each stratum, use the `fpr-macro` child stream of the frozen confirmatory generator, and take the 250th and 9,751st sorted replicate values (one-indexed conservative outer order statistics based on `B + 1`).

Also report a Bonferroni simultaneous collection of per-language two-sided Clopper–Pearson intervals at confidence `1 - alpha/4` and, separately, simultaneous one-sided upper bounds at confidence `1 - alpha/4`, with `alpha = 0.05`. Average the four lower endpoints and the four upper endpoints only as a conservative descriptive macro bound. Do not describe that averaged-endpoint bound as an exact interval for macro FPR. A pooled 1,200-record Clopper–Pearson interval is exact only under an additional common-i.i.d.-Bernoulli assumption that conflicts with allowing heterogeneous fixed strata; it may appear solely as an assumption-dependent sensitivity analysis and never replaces per-language evidence.

H1 and H2 are policy-level recall contrasts at independently locked system
thresholds. They never establish common-FPR dominance, overall safety
superiority, or a population-wide below-1% claim. The `C11` absolute gate may be
described as an **individual stratum-specific 95% upper FPR bound below 1%**
only for a stratum with `0/300` false positives. The current design cannot make a
familywise all-four-strata below-1% statement, because its zero-error
Bonferroni bound is `1.4501%` at 300 per stratum.

Do not add an arbitrary underpowered FPR noninferiority test. If comparative FPR
becomes essential, specify a new untouched benign evaluation set, an externally
justified operational margin, and a paired power design before any access. A
nominal pooled 1,200-record binomial analysis remains only an explicitly
assumption-dependent sensitivity and never replaces stratum evidence.

### Secondary and discovery families

The secondary Holm family is exactly `{H3, H4, H5a, H5b}`, with all four effects encoded so positive favors Fisher. H3 uses the positive `-NLL` interaction already defined; H5a/H5b use comparator AURC minus `C11` AURC. The exact H4 ambiguity-slice definition and the secondary-family resampling implementation are **UNKNOWN** and block confirmatory secondary testing until frozen before protected access. Missing/nonfinite values invalidate the applicable family rather than trigger complete-case deletion. Broad baseline and unregistered slice exploration remains discovery-only under Benjamini–Hochberg false-discovery-rate control. Do not make subgroup claims for a slice with fewer than 50 independent components.

## 11. Ablations and mechanism checks

Run the complete 2×2, followed by these frozen ablations:

- replace calibrated `q_k` with uniform candidate weights;
- candidate budgets `K in {1, 2, 4, 8}`;
- development-only endpoint caps `{2,4,8}` as sensitivity, with the primary and all
  protected runs fixed at eight; this is not model selection;
- remove the raw-message representation;
- remove auxiliary endpoint/span losses;
- remove registry evidence;
- force `UNKNOWN → MISMATCH` as analysis-only evidence of why that shortcut is unsafe;
- remove deterministic registry resolution from the semantic risk path;
- remove pressure, action, or asset nodes one at a time;
- replace entropy-plus-disagreement abstention with entropy-only abstention; and
- swap MuRIL with XLM-R base and IndicBERT v2 under matched settings.

Every run is initiated by the exact canonical `EngineInputDescriptor`, whose
hash references resolve against separately supplied system-manifest and VMP/item
bytes, never filesystem paths. Its total one-code raw parser emits a `PASS` or
`FAIL` `EnginePreflightReceipt`; only `PASS` permits the canonical
`SystemArtifactManifest` and schema-`1.1.0` engine run envelope. They bind complete executed-source closure,
system/control identity, runtime/float/math-backend contract, VMP, exact
`provider_execution`, candidate diagnostics and path lineage/scores/weights,
active paths, five-seed and prediction audits, SEP/E0 feature-tensor hashes,
direct registry artifact/resolver identity, and discriminated execution status.
The separate complete evaluation-universe/canonical-gold, universe/input receipts,
and metric-run union bind the denominator and valid or bounded-invalid
submissions. No informal run
or candidate trace substitutes for these
artifacts.
The endpoint-cap sensitivity cannot modify the frozen primary configuration or
protected cap.

Top-8 candidate coverage must reach at least 90% overall and 85% in each Hindi, Tamil, and Telugu stratum before the full uncertainty claim proceeds. The English–Indic stratum's coverage diagnostic must be reported, but its applicable transliteration subset must be defined before collection.

## 12. Failure and robustness analysis

Predefine error buckets: unseen Romanization, wrong candidate ranking, semantic extraction error, registry missingness, benign urgency, benign brand/domain mismatch, obfuscated destination, no destination, promotional spam, code-mixing boundary error, truncated/very long text, emoji/punctuation/Unicode corruption, adversarial homoglyph, template shift, and abstention failure.

Test empty and malformed inputs, long-message truncation, punctuation/whitespace variation, Unicode normalization, unknown tokens, code-switching, safe defanged artifacts, and unseen component families. Report failures by provenance and stratum. No adversarial or real-world robustness claim is allowed from synthetic perturbations alone.

## 13. Go/no-go and claim-routing rules

A method-and-benchmark paper route requires all of the following:

1. ethics, consent, privacy, and source-license gates completed;
2. the ontology pilot passes;
3. component-disjoint data and partition checks pass;
4. every protected component is singleton and monostratal, including at least 300 independent benign `primary_test` components per stratum for a per-stratum below-1% claim;
5. every `primary_test` label×stratum cell is at least 50% tester-donated authentic, with provenance-disaggregated reporting;
6. transliteration-resource and offline-registry protocols pass and top-8 candidate coverage passes;
7. the four factorial conditions and capacity/supervision controls pass information-flow and budget audits;
8. grouped-CV evidence-span overlap F1 is at least 0.75, visible-endpoint
   reliability passes, the registry reference passes independent audit, and the
   q-weighted labelled pair-set F1 plus `pair_emptiness_accuracy` reach their
   pre-`E4` frozen development gates;
9. both H1 and H2 pass their statistical and 0.03 practical-effect gates;
10. H3/H4 supply mechanism evidence consistent with the proposed claim;
11. low-FPR estimates and exact bounds follow the individual-versus-familywise
    claim boundary above, with no common-FPR or safety-superiority claim;
12. within every language stratum, `primary_test` phishing recall at each system's own locked threshold for `C11` is no more than 0.02 absolute below `C01`; and
13. the publication/IP gate authorizes disclosure.

If data quality passes but method gates fail, route to a dataset/resource paper with null results and error analysis. If pilot or independence gates fail, stop corpus expansion and repair the protocol. If only one co-primary hypothesis passes, report mixed evidence and do not call the full mechanism superior.

## 14. Deviations, reproducibility, and embargo

Record protocol changes before `primary_test` access, with reason, affected hypotheses, and whether the change is confirmatory or exploratory. Preserve configurations, seeds, component manifests, hashes, environment metadata, and per-example predictions under access control. Never overwrite the original text or provenance.

The machine validator verifies machine-representable gates such as vocabulary, schema, arithmetic, lineage, component separation, provenance exclusions, hashes, and configuration equality. It cannot approve ethics, consent quality, linguistic labels, official-source completeness, artifact safety, privacy, or lawful release. Those gates require named human review and documented audits.

No public preprint, repository publication, model release, dataset release, talk, poster, demo, abstract, or public benchmark submission occurs until the publication/IP gate is completed. This is a planning restriction, not legal advice.

## 15. Primary technical references

- Transliteration-lattice precedent: [Durrani et al.](https://aclanthology.org/W12-4410/)
- Neural lattice language modeling: [Su et al.](https://arxiv.org/abs/1803.05071)
- Context-aware Romanized South Asian transliteration: [Roark et al.](https://direct.mit.edu/coli/article/50/2/475/119145/)
- Large-scale Indic transliteration evaluation: [EACL 2021 study](https://aclanthology.org/2021.eacl-main.303/)
- Aksharantar: [Madhani et al.](https://aclanthology.org/2023.findings-emnlp.4/)
- MuRIL: [Khanuja et al.](https://arxiv.org/abs/2103.10730)
- IndicLID: [Madhani et al.](https://arxiv.org/abs/2305.15814)
- Informally Romanized language identification: [Benton et al.](https://aclanthology.org/2025.emnlp-main.117/)
- IndicBERT v2: [Doddapaneni et al.](https://aclanthology.org/2023.acl-long.693/)
- XLM-R: [Conneau et al.](https://arxiv.org/abs/1911.02116)
- Neural-network calibration: [Guo et al.](https://proceedings.mlr.press/v70/guo17a.html)
- Selective prediction: [Geifman and El-Yaniv](https://arxiv.org/abs/1705.08500)
- Recent multilingual phishing system: [PhishSigma++](https://arxiv.org/abs/2605.11619)
- Semantic scam primitives: [ACL Findings 2026 paper](https://aclanthology.org/2026.findings-acl.1025/)
- Script-aware phishing evidence: [ScriptMind](https://aclanthology.org/2026.eacl-industry.2/)
- Smishing dataset/system comparison: [SmishTank](https://arxiv.org/abs/2402.18430)
- Mobile-money smishing benchmark: [MOZ-Smishing](https://aclanthology.org/2025.africanlp-1.23/)
- Korean detection/explanation system: [KorSmishing Explainer](https://aclanthology.org/2024.emnlp-industry.47/)
- SMS phishing systematic review preprint: [2026 preprint](https://arxiv.org/abs/2604.11429)
