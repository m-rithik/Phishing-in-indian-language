# Fisher Factorial Condition Specification

> Status: **P0 METHOD CONTRACT — IMPLEMENTATION AND REVIEW PENDING**. Internal,
> embargoed, and pre-data. This file freezes what `C00`, `C10`, `C01`, and
> `C11` may see, learn, and use before any protected result.

## 1. Common task and packet boundary

Every condition receives the same `VisibleMessagePacket` (`VMP`): exactly
schema-`1.2.0` `item.text` plus the non-gold, pre-annotation
`item.visible_artifacts` inventory, bound by required `item.vmp_sha256`.
Annotations consume but never construct, repair, or infer this packet. Artifact
grammar, Unicode-code-point range binding, exact destination-span binding, and
canonical bytes are frozen in
[ENGINE_SPEC.md](ENGINE_SPEC.md#21-visible-message-packet) and the
[data contract](../DATA_CONTRACT.md#visible-non-gold-artifact-inventory-and-vmp).
The grammar proves syntactic representation safety only, not authenticity,
semantic type, collection authority, or release authority. The VMP excludes
provenance, source label, donor intent, scenario, prompt, campaign, grouping
identifiers, registry data, annotations, and labels.

Only semantic conditions may construct a `SemanticEvidencePacket` (`SEP`): the
complete bounded Cartesian audit packet produced from model-predicted visible
actor and destination endpoint sets and the frozen offline registry. It binds
the separate `VMP` by `vmp_sha256` and does not embed VMP text. The exact packet contract is in
[ENGINE_SPEC.md](ENGINE_SPEC.md#2-information-domains).

Human gold includes primary label, subtype, language, facets, spans, supporting
evidence, and visible endpoints. A registry-derived relation state is not blind
human gold. Blind annotators and the final adjudicator receive no registry or
provenance. A separate blinded registry reviewer creates a versioned reference
from final visible endpoints without primary label, provenance, or protected
outcomes. The reference contains only `MATCH|MISMATCH|UNKNOWN` rows for explicit
pairs; no pair means zero rows and implicit runtime `N/A`.

**OBSERVED:** the independent data-repair replay recorded as `E07` in
[EXECUTION_STATUS.md](EXECUTION_STATUS.md#10-executable-evidence-checkpoints)
passes historical schema `1.1.0` mechanical checks, including the two earlier
byte-bound exploits. `E09` independently passes the scoped schema-1.2 syntactic
VMP repair. `E10` passes the original E08 repairs but independently fails four
new semantic-contract blockers. `E11` passes that live repair but independently
fails five further provider/run-envelope, endpoint-numeric, E0-feature,
evaluation-universe, and coordinate-predicate requirements. `E12` then finds
five remaining status-union, causal-control, evaluation-binding,
system-provenance/five-seed, and candidate-numeric blockers. **P0 BLOCKER:**
`E13` then fails three remaining preflight/run-union, failure-accounting, and
metric-input/counting groups. `E14` passes those repairs and the other major
contracts but finds three engine-descriptor/parser, eligibility-accounting, and
metric-universe/denominator/algebra blocker groups. `E15` passes those repairs
and the previously reviewed surfaces but finds three remaining strict universe-
input parser/count, structural-versus-semantic precedence, and nonempty-
denominator blocker groups. Fresh independent replay of this eighth local,
universe-only docs repair must complete
before `P0` can pass.

## 2. Frozen factors

| Condition | Transliteration handling | Semantic consistency |
| --- | --- | --- |
| `C00` | rank-one path from the frozen provider/configuration | absent |
| `C10` | calibrated weighted paths | absent |
| `C01` | the same rank-one path as `C00` | present |
| `C11` | calibrated weighted paths | present |

One frozen candidate provider/configuration, candidate construction, maximum
`K = 8`, complete `VMP` alignment, ordering, normalizer, `T_tr`, explicit
bypass/degraded state, tokenizer, and sequence limit are shared by all four
cells. `C00`/`C01` activate the same returned rank-one path; `C10`/`C11`
activate all returned paths and retain their calibrated weights. This makes
transliteration marginalization, rather than provider access, the first factor.
A separately named raw-text system is exploratory and is never a factorial
cell.
The complete mechanical alignment/transducer predicates, immutable bounded
`provider_rank`, contributor lineage and operand order, pinned binary64 LSE,
log-domain retained mass, and manifest binding are normative in
[ENGINE_SPEC.md](ENGINE_SPEC.md#3-candidate-construction).
Exactly one `COMPOSED_SPAN` or `DIRECT_FULL_PATH` configuration is active per
message run; direct and composed candidates never share a
`q` distribution. `IDENTITY_BYPASS` is an output-artifact mode. Provider
manifest, execution-envelope, unit/reading, f64-bit, lineage,
span/path/byte, and 4-MiB manifest bounds are normative in that section. Its
hash includes the ordered `rewrite_spans`: composed and direct modes require
1..64 successful spans; bypass outputs have none. Every configured/effective
coordinate is a non-Boolean integer satisfying the exact VMP range/slice/order/
nonoverlap/non-artifact predicate. Provider failure retains attempted spans in
`provider_execution`, produces an identity path with no effective spans, and is
`DEGRADED_STOP_AFTER_IDENTITY`; it invalidates confirmatory and protected metrics. Direct full-path readings preserve
every non-rewrite code point and visible-artifact slice exactly.

## 3. Common encoder and information access

All cells use the same encoder family/checkpoint, raw branch, candidate format,
artifact representation, pooling, risk-head width, dropout, optimizer family,
batch construction, update budget, early-stopping evidence, tuning budget, and
seed schedule. Encoder swaps are named ablations, not changes to the 2×2.

| Information or module | `C00` | `C10` | `C01` | `C11` |
| --- | --- | --- | --- | --- |
| `VMP` | yes | yes | yes | yes |
| active paths | returned rank 1 | all returned paths | the same returned rank 1 | all returned paths |
| provider execution | same frozen provider/configuration | same frozen provider/configuration | same frozen provider/configuration | same frozen provider/configuration |
| node/endpoint/span heads | inaccessible | inaccessible | rank 1 only | active per path |
| endpoint / audit packet / resolver | inaccessible | inaccessible | rank 1 only | every returned path |
| `SemanticFeaturePlan` / projected tokens | inaccessible | inaccessible | rank 1 only | every returned path |
| phishing-risk head | active | active per path | active with rank-1 projected tokens | active with per-path projected tokens |
| risk marginalization | none | `q` weighted | none | `q` weighted |
| pair-state prevalence diagnostic | none | none | rank-1 `pi` | `P_pair` |

Inaccessible means no feature, missingness bit, zero placeholder, prediction,
gradient, label, cache, or lookup crosses into the condition.

## 4. Endpoint packet, diagnostic, and loss contract

For semantic path `k`, predict deduplicated `VMP` endpoint sets `A_k` and `D_k`,
each capped at eight by the frozen score/tie rule in the engine specification.
The cap is an engineering bound, not empirical evidence. Endpoint identity is
the exact `(role,start,end,kind,lookup_surface,lookup_status)` audit tuple and
excludes score. Actors are `ACTOR/NONE`; destinations are
`DESTINATION/<schema-1.2 kind>`; status is `ALIGNED|UNALIGNED`. Ranges use
non-Boolean integer coordinates and are nonempty/in-bounds. Aligned surfaces equal bounded deterministic renderer output
and unaligned surfaces are empty. Retain the highest score, apply the cap using
the finite score and frozen ties, then reorder by the score-independent endpoint
keys. Scores remain only in the canonical prediction audit as finite big-endian
binary64 bits; exact equal-score ties retain the lowest emission index. Candidate offsets and
back-projection are prohibited.

The canonical packet is every Cartesian pair:

`E_k = {(a,d,Resolve_R(a,d)) : a in A_k, d in D_k}`.

It is a compatibility inventory, not an actor-to-destination link. Empty product
means no resolver calls, no rows, and implicit `N/A`. Candidate text substitutes
only fully enclosed candidate spans into an endpoint lookup surface. A
cut-through endpoint has `lookup_status=UNALIGNED` and every affected pair is
short-circuited before registry with `UNKNOWN`, `NOT_EVALUATED`,
`ALIGNMENT_GUARD`, empty evidence IDs, and zero registry calls.
That zero applies to each affected pair; other aligned pairs in the same packet
may still call the registry.

For compatibility state `s`, let `pi_k(s)` be the equal-weight prevalence of
`s` across nonempty `E_k`, or `1[s=N/A]` when `E_k` is empty, and define

`P_pair(s|x) = sum_k q_k pi_k(s)`.

This is diagnostic only. Full `E_k` is the bounded canonical audit packet, not
a risk-head input. It includes exact endpoint audit objects,
`registry_call_count`, at most 64 pairs, at most 16 bounded safe evidence IDs per
pair, exact resolution coherence, and a 16-MiB packet limit.

Risk consumes only the canonical `SemanticFeaturePlan` projection: endpoint
ranges/statuses, destination kind, and resolution state/coverage/source in the
same score-independent order. Coordinates are indexing instructions. E0 uses
only `E0_VMP_CATEGORY_MEAN_V1`: a pinned-Unicode five-category binary64 VMP grid,
sequential binary64 endpoint means, fixed 31-dimensional category order, a
64-row mask/padded tensor, and canonical bit-string audit/hash.
Literal surfaces, IDs, hashes, evidence, scores, provider ranks, candidate
weights, and score order are excluded. `q` enters only after per-path risk.
This is synthetic interface evidence only. The real subword/candidate-to-VMP
adapter and later plan/version are **UNKNOWN** and must be frozen before `E3`.

The resolver is frozen, offline, and deterministic. Registry-state prediction
is not a learned head and has no auxiliary loss: training a head to reproduce a
registry value that is also supplied to the risk path was rejected as circular.

Let `L_cls,k`, `L_endpoint,k`, and `L_span,k` be path-level binary phishing,
visible-endpoint, and visible-span losses. All gold ranges are `VMP` ranges.

- `C00` and `C01` use the same returned rank-one path: `L = L_cls,1` for `C00`, and
  `L = L_cls,1 + lambda_endpoint L_endpoint,1 + lambda_span L_span,1` for
  `C01`.
- `C10` uses `L = sum_k q_k L_cls,k`.
- `C11` uses `L = sum_k q_k (L_cls,k + lambda_endpoint L_endpoint,k +
  lambda_span L_span,k)`.

Freeze lambdas through grouped cross-validation on `development`. Candidate
generation and `q` are external and frozen. The registry is read-only and gets
no gradient. Missing annotations are masked, never interpreted as negatives.

## 5. Capacity and supervision controls

The only allowed `system_variant` values are
`BASE|CAPACITY_CONTROL|SUPERVISION_CONTROL`. The exact eight allowed
condition/variant combinations are the four `BASE` cells; a
`CAPACITY_CONTROL` at `C00`, matched by immutable system-artifact identity to
the `C01 BASE`; a `CAPACITY_CONTROL` at `C10`, similarly matched to the `C11
BASE`; and `SUPERVISION_CONTROL` variants at `C01` and `C11`, each matched to
its same-condition `BASE`. No other combination is valid.

Capacity controls replace the matched semantic modules with active
primary-label-only adapters whose trainable parameter counts match the named
semantic base. They receive no semantic label, prediction, endpoint, packet,
plan, projected token, resolver call, registry state, or missingness and are
optimized only by `L_cls`. The ordinary trained capacity adapter belongs to a
later engine checkpoint; `E0` verifies only manifest and artifact-mask
coherence.

Supervision controls preserve the corresponding rank-1 or `sum_k q_k`
endpoint/span losses and encoder gradients during training. At risk-visible
inference they are prohibited from constructing, calling, or exposing
endpoints, pair packets, registry lookups, feature plans/tensors, compatibility
states, and their missingness. A parameter-matched primary adapter produces
risk. The normative eight-row artifact mask, safe `system_id` grammar, and
exact matched-system binding are in
[ENGINE_SPEC.md](ENGINE_SPEC.md#32-canonical-system-artifact-manifest-and-engine-run-envelope).

A semantic-mechanism claim requires evidence beyond the no-semantic core,
capacity, and supervision controls. Otherwise route the explanation to capacity,
auxiliary supervision, or unresolved mechanism.

## 6. Parameter and compute accounting

For each condition/control preserve trainable and active parameter counts,
forward paths, candidate count, optimizer updates, tokens/examples, tuning
trials, early-stopping rule, seeds, measured peak memory/time/latency/throughput,
and candidate/registry hashes. Do not infer compute matching from model names.

Canary tests must prove registry and semantic outputs/missingness are absent from
no-semantic and masked-risk paths. Any active-parameter or budget mismatch is a
protocol deviation before protected scoring.

## 7. Five-seed calibrated path ensemble

For each trainable system use seeds `11, 23, 37, 53, 71`; do not select the best
seed. The canonical `FiveSeedLogitArtifact` binds those seeds, active-path
order, per-seed finite binary64 logits, sequential binary64 means, and the
system artifact. `E0` uses it only for known-answer arithmetic; real model
aggregation begins at `E3`/`E4`. A deterministic rule baseline emits a frozen
finite logit-scale score and uses five identical slots only for downstream
arithmetic. A linear SVM uses its margin as the preregistered logit-scale score.

For system `m`, seed `j`, and returned path `k`, average path logits:

`bar_ell_mk = (1/5) sum_j ell_mjk`.

Fit one positive scalar temperature `T_m` for the fixed system, pooled across
languages, using only `probability_calibration`, by minimizing binary NLL of the
marginalized `p_m` below. Define:

`rho_mk = sigmoid(bar_ell_mk / T_m)`,

`p_m(x) = sum_k w_mk rho_mk`,

`v_m(x) = 4 sum_k w_mk (rho_mk - p_m(x))^2`, and

`u_m(x) = 0.5 H(p_m(x)) / log(2) + 0.5 v_m(x)`.

where `w_m1=1` for a rank-one `C00`/`C01` system and `w_mk=q_k` for an
all-path `C10`/`C11` system. Here
`H(p) = -p log(p) - (1-p)log(1-p)` is binary entropy and
`0 log(0)=0` by continuity.

Top-1 systems have `v_m = 0`. Alert, entropy, threshold, disagreement, and
selective cutoffs use this same calibrated object. Temperatures are never fitted
per seed or language and never shared across systems. A common logit delta was
rejected as nonidentified; calibrated entropy with raw-logit disagreement was
rejected as scale-incoherent. Entropy-only is an ablation.

The deterministic optimizer, positive bounds, tolerance, dtype, tie behavior,
and nonfinite/convergence failure policy are **UNKNOWN** and must be frozen and
independently tested before `E4`.

## 8. System-specific safety threshold

For system `m`, score every benign `safety_threshold` record with `p_m`. In
float64 define:

`theta_m = nextafter(max_x p_m(x), +infinity)`.

Alert iff `p_m(x) >= theta_m`; equality alerts. NaN, missing paths, nonfinite
values, or irreproducible bit patterns invalidate the run. Store the maximum
record ID, score bits, dtype, threshold bits, calibration hash, and system hash.
Never share or adjust a threshold after `primary_test` access.

H1/H2 compare recall under each system's independently locked policy. They are
not common-FPR comparisons and cannot support safety superiority.

## 9. Selective cutoffs

For target coverage `c in {0.80, 0.90}` and `N` valid
`probability_calibration` records, sort by `(u_m, UTF-8 record_id bytes)` and
accept exactly the first `ceil(cN)`. Store the boundary pair and apply the same
comparison unchanged to `primary_test`.

Selective analysis cannot remove or complete-case-filter a primary record.
Entropy-only is supporting ablation evidence; H5 compares `C11` with `C01` and
`C10`.

## 10. Reliability and resolver evaluation

Report blind endpoint/span reliability under the annotation contract. Pair
metrics bind the exact canonical `registry_reference_bundle`, frozen nonempty
evaluation-universe manifest, and one canonical engine envelope per universe
entry through the exact metric-run manifest. The universe's strict structural
parser emits `MetricUniverseInputReceipt`; only its `PASS` permits submission
preflight, and only both structural passes permit semantic closure validation.
Malformed raw metric submissions produce only `MetricInputReceipt`; either
preflight `FAIL` creates no metric-run manifest or metric. A structurally valid
but semantically invalid universe, including an empty one, takes the exact
universe-error metric-run short-circuit without opening envelopes or treating
its entries as an evaluation set. For a bounded structural submission against a
semantically valid universe, duplicate/extra/order and exclusive envelope
outcome counts follow the engine's fixed precedence. Any missing/extra/reordered/
degraded/invalid envelope, snapshot/resolver/artifact/VMP/gold/path mismatch,
nonfinite output, or declared-denominator mutation makes the run `INVALID`, emits no pair
metrics, and never deletes an item. Report `N_all`, `N_gold_empty`, and
`N_gold_nonempty`; the metric union separately records exact universe and
declared-denominator error counts. Micro path-weighted TP/FP/FN aggregate across every item,
using weight one for `C01` rank one and `q_k` for `C11`;
gold-empty nonempty predictions contribute FP and both-empty contributes zero.
Pair precision, recall, and F1 are canonical `+0.0` when their own denominator
is zero; this is not a declared-denominator error. A `VALID` run has
`1<=N_all<=10000`, so `pair_emptiness_accuracy` always has a positive
denominator. Report aggregate pair F1, `pair_emptiness_accuracy` on `N_all`, and fixed-
denominator conditional empty/nonempty recalls. `C11` reports q-weighted and
rank-1; `C01` rank-1; `C00`/`C10` `N/A`. These are not blind relation IAA and no
registry-state loss is permitted.

## 11. Freeze and exit gate

The candidate model, registry, resolver, semantic schema, endpoint/span losses,
all condition implementations, calibration contract, and analysis code freeze
before any protected access. A protected-derived edit makes a later run
exploratory.

Exit requires reviewed manifests for four cells and four controls; packet-access,
feature, gradient, registry-call, parameter, update, candidate, ensemble,
calibration, threshold, and tie tests; unopened protected partitions; and an
independent information-flow/causal-control review. Passing prose alone is not
implementation evidence.

The canonical `EngineInputDescriptor` references separately supplied system-
manifest and VMP/item bytes by hash, never by filesystem path. Its bounded
one-code parser emits an `EnginePreflightReceipt` `PASS` or `FAIL`; only `PASS`
permits a run envelope.
After preflight, the canonical `SystemArtifactManifest` and schema-`1.1.0` engine envelope bind
the exact executed-source closure, system/control identity, runtime, VMP,
provider cause/configuration/attempted spans, output manifest, binary64
candidate diagnostics and `q` terms, ordered/active paths, five-seed and
prediction audits, SEP/feature hashes, direct registry artifact/resolver
identity, and the discriminated
`VALID|DEGRADED_STOP_AFTER_IDENTITY|INVALID` state. Invalid runs retain only
fully validated upstream artifacts under the exact primary-stage table;
an invalid configured eligibility-selector result uses the distinct
`ELIGIBILITY_INVALID` provider outcome, retains no unsafe span, and stops before
dispatch;
degraded identity fallbacks stop before prediction and
are excluded from confirmatory/protected metrics. E0 additionally binds the
fixed feature-tensor audit; pair metrics bind the complete frozen evaluation
universe, canonical gold inventories, both metric input receipts, and discriminated
metric-run manifest.
No informal candidate trace or second run-manifest hash is valid. The primary
cap is fixed at eight. A development-only mechanism
sensitivity at caps `{2,4,8}` is reported after primary configuration freeze;
it is not model selection and cannot change the protected cap.
