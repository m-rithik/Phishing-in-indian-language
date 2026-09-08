# Fisher Offline Registry Protocol

> Status: **P0 CONTRACT — REGISTRY BUILD AND SEMANTIC REVIEW BLOCKED**. Internal,
> embargoed, pre-data protocol. The registry is a versioned research input, not
> blind human gold, an authoritative public fraud list, or a live reputation
> service.

## 1. Purpose and evidence boundary

The registry supplies bounded evidence about Cartesian pairs from
model-predicted visible claimed-actor and destination endpoint sets. It must
distinguish positive compatibility evidence from missing evidence. It cannot
infer malicious intent, use a
message's source provenance as a label, turn an unlisted artifact into
`MISMATCH`, or define a blind human annotation target.

**OBSERVED:** no Fisher registry or frozen registry manifest has been built or
audited. **UNKNOWN:** achievable organization coverage, official-source
completeness, named reviewers, maintenance cost, and measured contribution.
Therefore registry-reference construction and every semantic-condition run are
blocked.

The shared `VisibleMessagePacket` (`VMP`) is exactly schema-`1.2.0` `item.text`
plus the non-gold, pre-annotation `item.visible_artifacts` inventory, bound by
required `item.vmp_sha256`; annotations never construct it. Artifact grammar
and exact Unicode-code-point destination-span binding are normative in the
[data contract](../DATA_CONTRACT.md#visible-non-gold-artifact-inventory-and-vmp).
That grammar proves syntactic representation safety only, not authenticity,
semantic type, collection authority, or release authority. The
`SemanticEvidencePacket` (`SEP`) is the complete bounded canonical pair audit
packet resolved from predicted endpoints and bound to the separate `VMP` by
`vmp_sha256`; it does not embed VMP text. Full definitions are in
[ENGINE_SPEC.md](ENGINE_SPEC.md#2-information-domains).

## 2. Allowed sources

Registry evidence must come from frozen copies of official organization-controlled or government/regulator-controlled sources. Examples include an organization's official domain page, regulator directory, or published official contact/security notice. Search-result snippets, crowd reports, domain reputation vendors, model-generated claims, public comments, and the phishing/benign label are not registry evidence.

Every evidence item records its authoritative URL, retrieval timestamp, response/file SHA-256, content/media type, cited excerpt location, source authority type, reviewer, and review decision. Preserve the fetched evidence under access and copyright controls; a URL alone is not reproducible evidence.

## 3. Mandatory pre-pilot manifest and identifier namespace

Before a steward may finalize planned relation-coverage cells or a registry
reviewer may construct registry references, the project must create a minimal,
audited, frozen offline registry artifact and a manifest binding it to an
identifier. This is a `D0` preflight prerequisite, not a later engine feature.

`registry_snapshot_id` belongs to the reserved Fisher namespace and must fully match `registry_[a-z0-9][a-z0-9_-]{0,62}`. An identifier is unique and immutable; it is never recycled for changed content.

The machine-binding manifest supplied through optional CLI argument `--registry-manifest` contains exactly:

- `schema_version: "1.2.0"`;
- `registry_snapshot_id`;
- registry `artifact_sha256` as exactly 64 lowercase hexadecimal characters;
- semantic `version` in `MAJOR.MINOR.PATCH` form with an optional lowercase prerelease suffix;
- canonical `snapshot_date` in `YYYY-MM-DD`; and
- `approval_state`, one of `approved`, `pending`, or `blocked`.

The broader human audit package is separate from this strict machine object. It binds to the same snapshot ID/hash and records source-manifest, entry-set, normalization, and evidence-bundle hashes; scope and jurisdictions; normalization rules; source-authority/completeness decisions; reviewer-role and decision references; offline/no-network evidence; supersession; and release/retention classification. Separating the strict manifest from the audit package prevents unknown machine fields while preserving the evidence needed for human approval.

For supplied dataset registry-reference rows, the dataset CLI validates manifest
field and hash syntax, binds each referenced snapshot ID to exactly one supplied
manifest row, and enforces approval-state coherence. It also validates
evidence-ID syntax and inventory rules. `MATCH` and `MISMATCH` require
`approval_state: "approved"`. Until the manifest exists, only synthetic tool
rehearsal may exercise resolver states; real pilot release remains blocked by
the separate preflight coverage design.

The dataset CLI does **not** open the registry artifact to establish that its
bytes match `artifact_sha256`, and it does not establish that referenced
evidence artifacts exist. Actual artifact-to-hash binding, registry truth and
completeness, and evidence existence and adequacy require separate external and
human checks. Engine/run-manifest binding likewise needs its own executable
check; the dataset CLI does not validate engine manifests. All applicable
machine bindings and named human approvals must pass before `MATCH`/`MISMATCH`
can enter an engine input, metric, or research claim.

The annotation guide's pre-annotation structured-state coverage manifest is a
separate external governance artifact, not `registry_manifest.jsonl` and not an
input accepted by the current dataset CLI. A steward may assign a planned
relation-coverage tag only from the `VMP` plus this exact frozen registry. The
coverage manifest binds the registry hash, remains hidden from blind annotators
and the final adjudicator, and freezes before real pilot release. Its planned
tag never becomes semantic gold or a registry reference.

**OBSERVED:** the independent repair replay recorded as `E07` in
[EXECUTION_STATUS.md](EXECUTION_STATUS.md#10-executable-evidence-checkpoints)
passes historical schema `1.1.0` mechanical validation. `E09` independently
passes current schema-1.2 syntactic VMP validation. `E10` passes the original
E08 repairs but independently fails the later provider/endpoint-feature/bounds/
metric contract. `E11` passes those second-repair requirements but fails the
later provider-execution/run-envelope, endpoint-numeric, E0-feature,
evaluation-universe, and coordinate-predicate contract. `E12` then finds five
remaining status-union, causal-control, evaluation/gold-binding,
system-provenance/five-seed, and candidate-numeric blockers. `E13` then fails
three remaining preflight/run-union, failure-accounting, and metric-input/
counting groups. `E14` passes those repairs and the other major contracts but
finds three engine-descriptor/parser, eligibility-accounting, and metric-
universe/denominator/algebra blocker groups. `E15` passes those repairs and the
previously reviewed surfaces but finds three remaining strict universe-input
parser/count, structural-versus-semantic precedence, and nonempty-denominator
blocker groups. **P0 blocker:** this eighth local, universe-only docs repair requires
independent replay.
Neither scoped data pass validates artifact hash contents, registry truth,
evidence existence, or human workflow.

## 4. Versioned registry schema

Each registry release has `registry_version` matching the strict manifest's semantic `version`, creation timestamp, schema version, source-manifest hash, entry-set hash, normalization hash, reviewer set, and freeze state. Each entry contains:

| Field | Requirement |
| --- | --- |
| `entity_id` | stable internal identifier |
| `canonical_name` | reviewed official name |
| `aliases` | source-supported names and abbreviations with evidence IDs |
| `jurisdiction` | explicit scope |
| `artifact_type` | for example web domain or official short code |
| `artifact_pattern` | normalized exact or constrained pattern; no unsafe active URL |
| `valid_from`, `valid_to` | evidence-supported validity or `UNKNOWN` |
| `evidence_ids` | one or more authoritative frozen evidence records |
| `coverage_scope` | what the evidence affirmatively covers |
| `completeness_state` | `COMPLETE_FOR_SCOPE` or `INCOMPLETE` |
| `review_status` | `APPROVED`, `CONDITIONAL`, `RETIRED`, or `EXCLUDED` |

Aliases and artifacts cannot be added from protected-set labels or model errors. Defang stored examples; canonical comparison values may be encrypted or access-restricted where necessary.

## 5. Coverage and completeness

Registry coverage is not the fraction of messages receiving a non-`UNKNOWN` answer. Report separately:

1. **entity coverage:** fraction of eligible model-visible claimed entities mapped to an approved `entity_id`;
2. **artifact-type coverage:** fraction of eligible visible artifacts whose type is supported for that entity;
3. **complete-for-scope coverage:** fraction for which authoritative evidence explicitly defines the relevant allowed/incompatible scope; and
4. **relation resolvability:** fraction assigned `MATCH` or `MISMATCH` under the rules below.

Denominators, eligible cases, unsupported artifact types, and `UNKNOWN` cases must be reported overall and by stratum/provenance. `COMPLETE_FOR_SCOPE` requires a reviewer to identify authoritative evidence that is sufficiently exhaustive for the exact entity, jurisdiction, artifact type, and study freeze date. Mere absence from an official webpage is `INCOMPLETE`.

## 6. Frozen resolver rules

Apply the rules independently to every explicit actor/destination endpoint pair
supplied to the resolver. During inference, form the complete Cartesian product
of model-predicted endpoint sets for each candidate path. During reference
construction, form the complete Cartesian product of final visible actor and
destination endpoints created without registry access. The inventory does not
assert that a human or model linked one actor to one destination:

- `MATCH`: approved registry evidence affirmatively links the claimed entity to the visible artifact within the recorded scope and validity.
- `MISMATCH`: an entity and artifact are both visible, the entity is resolved, and complete-for-scope authoritative evidence establishes incompatibility for that artifact type/scope.
- `UNKNOWN`: evidence is missing, ambiguous, stale, incomplete, unsupported, conflicting, or insufficient for either `MATCH` or `MISMATCH`.
- `UNKNOWN`: a candidate lookup surface is unaligned because its endpoint cuts
  through a rewritten span. This short-circuits before registry with
  engine-only `registry_coverage=NOT_EVALUATED`,
  `resolution_source=ALIGNMENT_GUARD`, `evidence_ids=[]`, and zero resolver calls
  for that pair; a mixed packet may still contain calls for aligned pairs.
  `NOT_EVALUATED` is never a schema reference-row value.
- runtime `N/A`: either endpoint set is empty, so the Cartesian product is empty.
  Make no lookup calls and create zero registry-reference rows; `N/A` is never a
  registry-reference row label.

For aligned pairs, schema-reference coverage values map into SEP exactly as
`complete -> COMPLETE`, `partial -> PARTIAL`, and `missing -> MISSING`.
`NOT_EVALUATED` exists only in the engine short-circuit and never in a reference
row.

Engine audit evidence IDs fully match
`registry_evidence_[a-z0-9][a-z0-9_-]{0,45}`, are unique/sorted, and number at
most 16 per pair. `MATCH`/`MISMATCH` require `COMPLETE+REGISTRY` and nonempty
evidence; registry `UNKNOWN` requires `PARTIAL|MISSING+REGISTRY`; alignment
`UNKNOWN` requires `NOT_EVALUATED+ALIGNMENT_GUARD`, empty evidence, and no call.
The packet call count equals its `REGISTRY`-source pair count; run total is the
sum across paths. Empty product has count zero.

`UNKNOWN` can never be coerced to `MISMATCH` in the primary system. The frozen `UNKNOWN → MISMATCH` run is analysis-only and must be labeled unsafe-shortcut evidence.

## 7. Offline inference and reference contract

Package the approved registry as a read-only, content-hashed local artifact. No
live DNS, WHOIS, search, browsing, reputation API, redirect following, or
network lookup is permitted during reference construction or any model run.
Normalize only with the frozen version. A lookup returns the relation state,
evidence availability flags, `registry_version`, and coverage/completeness
state; it does not return source intent, provenance, gold endpoints, or the
primary label.

Safe evidence IDs and snapshot/version identifiers are retained only for
audit, explanation, and manifest binding. The complete bounded packet is an
audit record, never learned input. Its endpoint objects, score-independent
order, call count, resolution coherence, evidence cap/grammar, 64-pair cap, and
16-MiB byte cap are frozen in the engine specification.

The canonical `EngineInputDescriptor` refers to separately supplied system-
manifest and VMP/item bytes by hash, not a filesystem path. Its bounded total-
precedence parser emits a `PASS` or `FAIL` `EnginePreflightReceipt`; only `PASS`
permits the canonical
`SystemArtifactManifest` and schema-`1.1.0` engine run envelope
bind the complete executed-source closure, system/control identity,
runtime/environment/math backend, VMP, provider execution and bypass cause,
active paths, five-seed and prediction audits, SEP/feature hashes, direct
`registry_artifact_sha256`, registry snapshot/resolver, and the discriminated
status. All four factorial cells use the same frozen provider/configuration;
`C00`/`C01` activate its rank-one path and `C10`/`C11` activate all paths. A
no-eligible run is a valid identity output. Provider/normalizer unavailability
or timeout before any nonidentity output may be
`DEGRADED_STOP_AFTER_IDENTITY` only when the exact identity manifest/path
validates; processing then stops before prediction. Malformed/nonfinite/
alignment-invalid output is `INVALID`. Degraded runs invalidate every protected
or confirmatory metric run.
An invalid configured eligibility-selector result uses
`ELIGIBILITY_INVALID`, retains no unsafe span, makes no provider call, and emits
no candidate or semantic artifact; a later rewrite/alignment failure after an
accepted provider manifest remains `CANDIDATE`.
Identical identity-output hashes do not erase the distinct cause because the
envelope binds it. Exact objects, bytes, hashes, source-closure evidence, and
condition/status coherence are normative in
[ENGINE_SPEC.md](ENGINE_SPEC.md#31-canonical-provider-execution) and
[ENGINE_SPEC.md](ENGINE_SPEC.md#32-canonical-system-artifact-manifest-and-engine-run-envelope).

The exact SEP packet field inventory/order, compact UTF-8 JSON bytes,
`vmp_sha256`, path text/alignment-bound `path_sha256`, pair ordering, and
`pair_packet_sha256` are frozen in
[ENGINE_SPEC.md](ENGINE_SPEC.md#4-factorial-engine-and-canonical-pair-packets).
Endpoint scores remain only in the canonical prediction audit as finite
big-endian binary64 bit strings, with exact emission indices, dedup/tie/cap
selection, declared-order compact bytes, and SHA-256. Learned risk receives only
the canonical `SemanticFeaturePlan`. For `E0`, the exact
`E0_VMP_CATEGORY_MEAN_V1` audit constructs a pinned-Unicode five-category
binary64 VMP grid, sequential range means, and fixed 31-dimensional one-hot
pair rows with a 64-row Boolean mask/zero padding and canonical bit strings.
Literal lookup surfaces, evidence/registry/resolver IDs, hashes, scores,
provider ranks, candidate weights, and score order are absent. `q` is applied
only after per-path risk. The future candidate/subword-to-VMP adapter and its
feature-plan version are unimplemented and must freeze before `E3`; the E0
audit proves only deterministic projection and masks.

A registry reviewer works after final visible-endpoint adjudication, without
access to the primary label, provenance, donor intent, scenario, source label,
or protected outcomes. The reviewer resolves the canonical Cartesian product of
final endpoint sets and produces a separate versioned audited artifact whose row
labels are exactly `MATCH`, `MISMATCH`, or `UNKNOWN`. An empty product means no
calls, zero rows, and implicit runtime `N/A`. Blind annotators and the final
adjudicator never see the registry or annotate pair links.

At inference, path `k` yields bounded endpoint sets `A_k`, `D_k` and canonical
packet

`E_k = {(a,d,Resolve_R(a,d)) : a in A_k, d in D_k}`.

Each role is capped at eight by the frozen deduplication/score/tie rule, so the
packet has at most 64 pairs. Define `pi_k(s)` as equal-weight state prevalence
over nonempty `E_k`, or `1[s=N/A]` for an empty packet, and

`P_pair(s|x) = sum_k q_k pi_k(s)`.

This is diagnostic only; `E_k` is never a learned risk input.
`C00` and `C10`, capacity controls, and masked risk paths receive neither
endpoint predictions, pair packets, feature plans/tokens, registry values, nor
missingness indicators. Supervision controls retain endpoint/span losses but
may not construct/call/expose endpoint prediction, packet, plan, token, resolver,
semantic state, or missingness to risk.

Blind reliability is measured only for visible endpoints/spans. Metrics bind a
canonical schema-`1.0.0` `registry_reference_bundle` carrying snapshot,
resolver, registry-manifest hash, and reference-artifact hash. Before inference,
the evaluation-universe `1.0.0` manifest is the complete, not sampled, nonempty
UTF-8 item-ID-sorted closure of eligible records in the named partition, with
one to 10,000 entries. It binds exact dataset hashes, bundle hash,
partition, VMP/final annotation, and canonical versioned gold-inventory byte
size/hash; omission, extra, duplicate, or reorder invalidates it. Its hash fixes
`N_all`, `N_gold_empty`, and `N_gold_nonempty`. A `VALID` metric-run `1.1.0`
manifest for `C01`/`C11` binds exactly one valid engine envelope per universe
item in order. Its `INVALID` branch emits no metrics and instead binds the
submitted-inference manifest hash and exact precedence-based bounded discrepancy
counts plus disjoint universe and declared-denominator error counts. A strict
`MetricUniverseInputReceipt` structural boundary precedes submission preflight,
and both precede universe semantic closure. Either structural failure produces
only its receipt. A structurally valid but semantically invalid universe,
including an empty one, produces the exact universe-error invalid metric-run,
opens no envelope, and emits no metric. Natural zero denominators in pair precision,
recall, or F1 produce canonical `+0.0`, not a declared-denominator error. Any artifact,
VMP, gold, bundle, snapshot, or resolver mismatch; nonfinite/path failure; or
declared-denominator mutation invalidates the whole run and never shrinks the universe.
Micro path-weighted pair TP/FP/FN use weight one for `C01` rank one and `q_k`
for `C11`; gold-empty false positives are included and both-empty adds zero
counts. Report pair F1, all-item emptiness accuracy, and conditional recalls.
Every valid metric run has positive `N_all`, so all-item emptiness accuracy has
a positive denominator.
`C11` reports q-weighted/rank-1, `C01` rank-1, and `C00`/`C10` `N/A`. Do not
report blind registry-state alpha/F1 or train a registry-state loss.

## 8. Freeze and leakage policy

Build, review, and freeze the initial minimal registry from approved authoritative
evidence independent of every Fisher message before the coverage manifest and
blind release. It must not be derived from pilot messages, labels, scenarios,
errors, or source metadata. A later expansion may use only independently
approved authoritative evidence selected during `development`, must receive a
new version and audit, and must freeze before protected access. Record the exact
artifact hash in the registry manifest and each canonical engine run envelope;
bind each applicable registry-reference to that manifest through
`registry_snapshot_id`.

After freeze:

- protected messages, labels, errors, provenance, or artifacts cannot add aliases or entries;
- official-source changes are logged but do not alter the confirmatory version;
- a material update creates a new registry version and an explicitly exploratory evaluation;
- entries derived from a Fisher message or its descendant are prohibited; and
- an expired or contradicted source moves the evidence to review for future versions, never a silent edit.

## 9. Safety, privacy, and release

Do not store active malicious links, credentials, personal phone/UPI/account identifiers, or unneeded personal data. Registry evidence can contain copyrighted or sensitive operational material even when publicly visible; release rights require separate human review. Demonstrations use `.invalid`, `.example`, or safely defanged representations.

## 10. Verification ownership

The dataset CLI validates manifest field and hash syntax, snapshot-ID binding to
the supplied manifest, approval-state coherence, and evidence-ID syntax and
inventory. It does not verify the registry artifact's bytes against the declared
hash, inspect engine/run manifests, or establish that evidence artifacts exist.
Actual artifact-to-hash binding, registry truth and completeness, evidence
existence and adequacy, source authority, whether `MATCH`/`MISMATCH` is
justified, and lawful retention/release require separate external or named human
checks. Reviewer identities and authority remain **UNKNOWN**.

## 11. Exit gates

**`D0` pilot-preflight gate:** before any real pilot item is released, the
minimal registry, namespace, manifest binding, hashes, human
authority/completeness approval, offline/no-network check, blinded registry
reviewer workflow, schema/validator sync, and separately hash-frozen
component-aware coverage manifest must pass. The coverage manifest contains the
annotation guide's planned relation-state minima and receives qualified native
review; it is not gold.

**Confirmatory-use gate:** the registry is eligible only when source and entry
hashes are frozen; every state is evidence-linked; completeness is reviewed;
coverage denominators are computed; offline/no-network, predicted-endpoint-only,
canonical Cartesian packet, literal-ID nonexposure, packet-access, and
condition-mask tests pass; and independent audit finds no protected-derived
entry, circular target, or unsafe artifact.

The full governance-ledger validator and the future `corpus-final` validator remain separate mandatory gates. Neither is implemented merely by validating a registry manifest.
