# Fisher Annotation Guide

Status: **DRAFT — BLOCKED FOR COLLECTION**

Version: `0.2-draft`

This guide operationalizes the Paper 1 ontology for text messages and textual destination artifacts. It does not authorize collection. Collection remains blocked until the ethics authority and approval identifier, data controller, secure storage location, equivalence-key custodian and rotation policy, incident contact, retention period, withdrawal cutoff, and approved consent materials are recorded in [Consent, Ethics, and Privacy](CONSENT_ETHICS_PRIVACY.md). Native-language reviewers must approve the examples and lexical-token rules before the pilot.

The message-level record and validator are governed by the
[machine data contract](../DATA_CONTRACT.md). **OBSERVED:** historical schema `1.1.0`
separates visible endpoints from three-state registry-reference rows,
rejects the retired annotation-relation field, and has the independent `E07`
data-repair pass recorded in
[EXECUTION_STATUS.md](EXECUTION_STATUS.md#10-executable-evidence-checkpoints).
Current schema `1.2.0` adds the non-gold visible-artifact inventory and VMP hash
binding. `E08` then failed independent semantic review; `E09` independently
passes only the scoped schema-1.2 syntactic VMP repair. `E10` independently
passes the original E08 repair but finds four later semantic-contract blockers.
`E11` independently passes those second-repair requirements but finds five later
provider-execution/run-envelope, endpoint-numeric, E0-feature,
evaluation-universe, and rewrite-coordinate blockers. `E12` then finds five
remaining status-union, causal-control, evaluation/gold-binding,
system-provenance/five-seed, and candidate-numeric blockers. `E13` independently
passes those fifth-repair surfaces but finds three preflight/run-union and
metric-input/counting blocker groups. `E14` passes those repairs and the other
major contracts but finds three engine-descriptor/parser, eligibility-
accounting, and metric-universe/denominator/algebra groups. `E15` passes those
repairs and the previously reviewed surfaces but finds three remaining strict
universe-input parser/count, structural-versus-semantic precedence, and
nonempty-denominator groups. The eighth local, universe-only docs repair
requires fresh independent replay. Until that passes, `P0` and collection remain blocked.

## 1. Annotation objective and unit

The primary task is binary classification of one message as `PHISHING` or `BENIGN`. A message may include textual destination artifacts such as a URL, domain, phone number, UPI identifier, bank/account destination, email address, or app name. Voice, audio, QR images, browser screenshots, and conversation history are outside Paper 1.

One annotation unit is the `VisibleMessagePacket` (`VMP`): exactly
schema-`1.2.0` `item.text` plus the non-gold, pre-annotation
`item.visible_artifacts` inventory, bound by required `item.vmp_sha256`.
Annotations consume it and never construct, repair, or infer it. Semantic
annotators receive no provenance, authoring metadata, registry
state, or registry evidence. They label independently and must not inspect
another annotator's work, execute code in the message, visit a destination, call
a number, contact a sender, or search a live identifier. All artifacts must
already be defanged or replaced with approved typed placeholders.

Every pre-annotation artifact entry contains exactly `kind`, `kind_reason`,
`representation`, `start`, `end`, and `text`. Its non-Boolean integer range is
zero-based, half-open, and measured in Unicode code points; `text` is the exact
`item.text[start:end]` slice. `kind_reason` is 1–500 Unicode code points exactly
for `OTHER` and empty otherwise. Entries are unique, pairwise nonoverlapping, and
sorted by `(start,end,UTF-8(kind),UTF-8(representation),UTF-8(text))`. Kinds are
`URL|DOMAIN|PHONE|UPI|BANK|EMAIL|APP|OTHER` and
representations are `TYPED_PLACEHOLDER|RESERVED|DEFANGED`. Typed placeholders
are exactly `[URL]`, `[DOMAIN]`, `[PHONE]`, `[UPI]`, `[BANK]`, `[EMAIL]`,
`[APP]`, and `[ARTIFACT]` for their corresponding kinds. `RESERVED` permits
only the data contract's conservative optional-scheme/optional-`www` DNS form
ending `.example` or `.invalid`, with its bounded path grammar and no port,
query, fragment, or surrounding prose. `DEFANGED` requires an exact marker:
`[.]`, `(.)`, `[at]`, `[redacted]`, `hxxp:`, `hxxps:`, or `XXXX`. All forms
also pass the global live-route and secret scanners. This grammar proves
syntactic representation safety only; it does not prove authenticity, correct
semantic type, collection authority, or release authority. Only a typed
placeholder mechanically binds kind to surface; reserved and defanged kinds
remain human-audited metadata.

The primary label, subtype, facets, spans, evidence, and ambiguity decision must be justified only from that model-visible packet. Author intent, simulation scenario, prompt, source label, provenance class, generation method, donor/author identity, campaign assignment, and collection notes are hidden from annotators and adjudicators. Those fields may govern authorization, eligibility, grouping, stratification, or audit, but they cannot establish semantic gold. If the visible packet cannot support a binary decision, the annotation remains `UNCERTAIN` and the item is excluded after unresolved adjudication even when a hidden scenario intended a particular label.

### 1.1 Display terms and machine enums

This guide uses uppercase terms for human-visible decisions. The [machine data contract](../DATA_CONTRACT.md) is authoritative and uses this exact mapping:

| Guide term | Machine value |
|---|---|
| `HINDI_DOMINANT` | `hindi` |
| `TAMIL_DOMINANT` | `tamil` |
| `TELUGU_DOMINANT` | `telugu` |
| `EN_INDIC_CODE_MIXED` | `english_indic_code_mixed` |
| `BENIGN` | `benign` |
| `PHISHING` | `phishing` |
| annotation/adjudication `UNCERTAIN` | `uncertain` |
| per-annotation language stratum | `hindi`, `tamil`, `telugu`, `english_indic_code_mixed`, or workflow state `uncertain` |
| excluded item status | partition `excluded` |
| span roles | `claimed_actor`, `claim_or_problem`, `requested_action`, `sensitive_item_or_asset`, `destination_artifact`, `pressure_tactic`, `supporting_evidence` |
| registry-reference row labels (not blind annotation fields) | `MATCH`, `MISMATCH`, `UNKNOWN` |
| implicit resolver state when no explicit pair exists | `N/A` (zero reference rows) |

The current dataset snapshot carries `schema_version: "1.2.0"` and implements
this machine-representable P0 boundary locally. The canonical partition values remain
`pilot`, `unassigned`, `development`, `probability_calibration`,
`safety_threshold`, `primary_test`, `external_test`, and `excluded`. The machine
value `uncertain` supports workflow and adjudication; it is not a third paper
gold class. Machine implementation does not validate linguistic truth, registry
truth, reviewer blinding, or human authorization; independent review is pending.

## 2. Eligibility checks

Reject or quarantine the item before semantic annotation if any of these conditions holds:

- the text is empty, corrupted, or cannot be rendered as Unicode;
- a high-confidence detector finds an active URL/domain, live email or phone route, credential or OTP value, unredacted direct identifier, real account/UPI value, or other prohibited sensitive data;
- its provenance class, authorization, or source-ledger reference is missing;
- its language does not fit exactly one of the four strata below;
- it is a duplicate already assigned the same canonical item identifier;
- the text requires unavailable conversation, audio, image, or external account context to establish even an adjudicated primary label.

A high-confidence active-route or prohibited-identifier finding is a quarantine error, not a warning. It blocks annotation until an authorized steward safely removes or defangs the value and a second review passes. Conservative automation is incomplete, so human safety and privacy review remains mandatory even when no detector fires.

Every item stores a sorted, unique `exclusion_reasons` list drawn only from:

- `unresolved_primary_label`;
- `unresolved_language_stratum`;
- `governance_ineligible`;
- `safety_ineligible`;
- `privacy_ineligible`;
- `out_of_scope`;
- `duplicate_or_leakage`.

The list is empty for every non-`excluded` item and nonempty for every `excluded` item. A reason describes disposition and never substitutes for a semantic label or stratum. In `pilot-final`, excluded attempts may use only `unresolved_primary_label` and/or `unresolved_language_stratum`, exactly matching the final annotation's unresolved states. Governance, safety, privacy, scope, and duplicate failures are resolved or rejected before a row becomes a pilot attempt and are reported separately in the sampling flow.

## 3. Mutually exclusive language strata

### 3.1 Counting rule

The machine lexical-token inventory is complete: it contains exactly every maximal contiguous run of Unicode Letter or Mark code points in the immutable raw text, in order, with no omission, overlap, split, or merge. Digits, punctuation, whitespace, and emoji are not Letter/Mark runs. **Every** inventory token enters the language-percentage denominator. A destination, brand, conventional acronym, or named-identifier token that cannot be assigned confidently to `hi`, `ta`, `te`, or `en` from the visible context is labeled `other`; it is never dropped from the denominator. This deterministic all-token rule prevents a reviewer from changing a stratum by selectively excluding inconvenient tokens through an unauditable eligibility judgment.

Each independent and final annotation creates its own `token_language_spans` and computes proportions over every entry. Each entry contains exactly half-open `start`/`end`, exact raw substring `text`, `language` (`hi`, `ta`, `te`, `en`, or `other`), and observed `script` (`devanagari`, `tamil`, `telugu`, `latin`, or `other`). Its stored `text` must equal the immutable message substring at `[start, end)`. Entries are sorted, unique, nonoverlapping, nonempty, in bounds, and collectively equal the complete Letter/Mark-run inventory.

Script is observed form, while language is the contextual linguistic reading; neither is inferred from the other. For script validation, recognized DEVANAGARI, TAMIL, TELUGU, or LATIN Letter/Mark names contribute that script. Common/Inherited generic marks that contribute no recognized script inherit the token's sole recognized explicit script. A token with multiple recognized scripts, an unsupported Letter, or no recognized explicit script uses `other`. Machine validation can verify offsets, the complete Unicode Letter/Mark inventory, and this observed-script rule. It cannot determine contextual language, lexical borrowing, named-identifier status, or whether a Latin-script form is Hindi, Tamil, Telugu, English, or `other`. Those judgments require qualified native-language reviewers. Within each primary-label × language-stratum cell, the later corpus targets approximately one-third native-script-dominant, one-third Romanized-dominant, and one-third mixed-script items. A deviation greater than five percentage points must be registered before dataset lock and cannot be repaired by splitting related translation, transliteration, or paraphrase families.

### 3.2 Assignment order

Each blind annotator independently assigns top-level `language_stratum`; the third annotator supplies the final value. Apply these rules in order:

1. Evaluate code mix first. Assign `EN_INDIC_CODE_MIXED` only when English and **exactly one** core Indic language (Hindi, Tamil, or Telugu) each account for at least 20% of all lexical tokens, neither reaches 70%, and no second core Indic language is present. Record `code_mix_pair` as `en_hi`, `en_ta`, or `en_te`.
2. If code mix did not apply, assign `HINDI_DOMINANT`, `TAMIL_DOMINANT`, or `TELUGU_DOMINANT` when the corresponding core Indic language accounts for at least 70% of all lexical tokens.
3. Otherwise assign annotation `language_stratum: "uncertain"`, set the `language` ambiguity tag, and adjudicate.

Items with two core Indic languages and no language reaching dominance, no rule reaching a threshold, or unresolved stratum conflict remain `uncertain`. Text with no Letter/Mark token is ineligible before blind release because no language denominator exists. A final known annotation stratum must equal the item's final study stratum. Item `language_stratum: "uncertain"` (paired with item `language: "unknown"`) is permitted only in partition `excluded`, with `unresolved_language_stratum`. `uncertain` is a workflow state, not a fifth study stratum.

Every dominant-language or `uncertain` annotation uses `code_mix_pair: "none"`; a code-mixed annotation must use the matching `en_hi`, `en_ta`, or `en_te` value. Token spans, pair, annotation stratum, and final item stratum must agree where resolved.

Boundary examples (synthetic; native-speaker review is still required):

- `Aapka khaata aaj band hoga` is Hindi-dominant even when Romanized; script does not determine the stratum.
- `KYC turant update karo` is not automatically code-mixed merely because `KYC` resembles an English acronym. Assign every token a contextual language or `other`, count all four tokens, and apply the thresholds without exclusion.
- A message with English and Hindi each at 50% is `EN_INDIC_CODE_MIXED` with `code_mix_pair: "en_hi"` if both contribute content.
- A message with Hindi at 75% and English at 25% is `HINDI_DOMINANT`, because one language reaches 70%.
- A message with Hindi at 45%, Tamil at 30%, and English at 25% is outside the four-stratum scope because it contains more than one core Indic language.

## 4. Primary label

### 4.1 `PHISHING`

Label `PHISHING` when the message uses deceptive social engineering to induce an action intended to expose a credential, sensitive information, account access, money or another protected asset; install or open an unsafe resource; or route the recipient to a deceptive destination. An impersonated organization is strong evidence but is not mandatory. A destination artifact is also not mandatory: a request to reply with an OTP or password can be phishing.

The label must be supported only by the immutable schema-1.2 VMP. Scenario
intent, prompt target, source label, provenance, author identity, or generation
method cannot supply or break a tie. Suspicious words, urgency, spelling errors,
Romanization, unknown domains, or promotions are not sufficient on their own.

### 4.2 `BENIGN`

Label `BENIGN` when the message does not meet the phishing definition. For every benign item, assign exactly one subtype:

- `PERSONAL`: interpersonal, noncommercial communication;
- `TRANSACTIONAL`: a legitimate receipt, alert, status, appointment, or requested service message;
- `PROMOTIONAL`: marketing, advertising, or nonmalicious bulk promotion;
- `INFORMATIONAL`: public-interest, educational, organizational, or general information not tied to a transaction;
- `OTHER`: benign content that does not fit the other four; annotators must add a short reason.

Subtype is `N/A` for phishing items. Promotional spam remains benign and must not be relabeled as phishing merely because it is unsolicited.

Every annotation stores `subtype_other_reason`. It is a Unicode string of 1–500 code points exactly when the annotation is benign with subtype `other`; it must be the empty string for every other subtype or label. The reason must describe the visible content-based categorization and cannot contain provenance, scenario, prompt, source-label, or author-intent information.

### 4.3 Uncertainty and confidence

`UNCERTAIN` is allowed during independent annotation when evidence cannot support either binary label. It is not a gold class and must never be converted silently to benign. Annotators record a confidence level (`HIGH`, `MEDIUM`, or `LOW`) and one or more ambiguity tags, such as `LANGUAGE`, `INTENT`, `ACTOR`, `ACTION`, `DESTINATION`, `ROMANIZATION`, `MISSING_CONTEXT`, or `OTHER`.

A third qualified annotator, distinct from both blind annotators, creates a final record for **every** pilot attempt. Blind conflicts and any uncertain primary label or language stratum specifically require adjudication; agreement between blind records does not remove the universal final-record requirement. A retained final record requires both a binary `PHISHING`/`BENIGN` label and one of the four study strata. If primary intent remains unresolved, retain primary `UNCERTAIN`, resolution `UNRESOLVED`, partition `excluded`, and reason `unresolved_primary_label`. If language remains unresolved, retain annotation stratum `uncertain`, partition `excluded`, and reason `unresolved_language_stratum`. Both reasons are present when both decisions remain unresolved. `excluded` is an item status, never a primary label or fifth stratum.

## 5. Structured facets and evidence spans

All spans use zero-based, half-open Unicode code-point offsets `[start, end)` into the immutable raw text. Normalized text, byte offsets, grapheme-cluster positions, or rendered columns must not be substituted. Every span stores `start`, `end`, exact substring `text`, `facet`, `qualifier`, and `qualifier_reason`; `raw_text[start:end]` must equal stored `text`. `qualifier_reason` is a Unicode string of 1–500 code points exactly when `qualifier` is `OTHER`; otherwise it is the empty string. Discontinuous evidence is stored as separate spans. Overlapping spans are permitted only when they support different facet instances; identical duplicate spans are not.

The annotation's `facets` array contains exactly one record for each of the six semantic facets below. Each record stores `facet`, `state`, and `span_indices`. State is:

- `explicit`: one or more indexed spans state the facet in visible text;
- `not_explicit`: the facet is relevant but is not textually stated; `span_indices` is empty and hidden context cannot fill it;
- `not_applicable`: the facet does not apply; `span_indices` is empty.

For every explicit facet, use the smallest visible span that preserves its meaning. Do not invent missing entities or use provenance, scenario, prompt, source label, or author intent as an evidence source.

As a machine coherence rule, a `PHISHING` annotation cannot mark `requested_action` or `sensitive_item_or_asset` as `not_applicable`, and at least one of `requested_action`, `sensitive_item_or_asset`, `destination_artifact`, `claimed_actor`, or `claim_or_problem` must be `explicit`. This rule can reject an internally incoherent record; it cannot prove that the phishing judgment is true.

### 5.1 Facets

- `claimed_actor`: the person, role, service, or organization the sender claims or implies they represent. Record all materially distinct actors. Example spans include `bank officer` or a named service.
- `claim_or_problem`: the event, benefit, warning, status, or problem presented as true, such as account suspension or a prize.
- `requested_action`: what the recipient is asked or pressured to do, such as reply, click, call, pay, install, verify, or share.
- `sensitive_item_or_asset`: the credential, information, access, money, or protected asset sought or put at risk, such as OTP, password, PIN, identity document, card data, account control, or funds.
- `destination_artifact`: the textual target of an action. Its spans use qualifier `URL`, `DOMAIN`, `PHONE`, `UPI`, `BANK`, `EMAIL`, `APP`, or `OTHER`. Artifacts must be defanged, reserved, or typed placeholders before annotation.
- `pressure_tactic`: a persuasive or coercive tactic. Its spans use qualifier `URGENCY`, `THREAT`, `AUTHORITY`, `SCARCITY`, `REWARD`, `FEAR`, `TRUST`, `SOCIAL_PROOF`, or `OTHER`. Add a visible-evidence note for `OTHER`.

The six facet records exclude `supporting_evidence`. Instead, evidence is represented by separate spans whose facet is `supporting_evidence`, and the top-level `evidence_span_indices` references them. Every structured span is referenced exactly once by its matching facet record. At least one visible supporting-evidence span is required for every included binary annotation. Spans for `claimed_actor`, `claim_or_problem`, `requested_action`, and `sensitive_item_or_asset` always use qualifier `N/A`; destination and pressure spans use their controlled qualifiers above; supporting-evidence spans use `N/A`.

Use state `not_applicable` when a facet truly does not apply and `not_explicit` when it is relevant but no exact raw-text span states it. Missing annotation is never equivalent to either state.

Every `destination_artifact` annotation span must match exactly one existing
pre-annotation `visible_artifacts` entry on `(start,end,text)`, and its qualifier
must equal that entry's `kind`. Annotation cannot create or modify an inventory
entry. The converse is not required: an inventory entry need not become a gold
destination span unless the visible message supports that facet decision.

### 5.2 Visible actor and destination endpoints

Blind annotators and the final adjudicator annotate only visible actor and
destination spans/endpoints from the `VMP`. They do not receive a registry,
registry coverage, or a `MATCH`/`MISMATCH` state. An endpoint is absent when the
corresponding facet is not explicit; no hidden actor or destination may be
invented.

After final visible-endpoint adjudication, mechanically form the complete
Cartesian product of the final actor endpoint set and final destination endpoint
set. A separate blinded registry reviewer resolves every resulting pair against
the exact frozen offline registry. This is a compatibility inventory; neither
blind annotators nor the final adjudicator create an actor-to-destination link.
The reviewer receives the endpoint text/offsets and registry evidence
but no primary label, provenance, source label, donor intent, scenario, prompt,
campaign/group identifier, or protected outcome. Each applicable pair produces
one `MATCH`, `MISMATCH`, or `UNKNOWN` row in canonical actor-then-destination
endpoint-key order in a separately versioned audited registry-reference
artifact. If either endpoint set is empty, make no resolver calls, create zero
reference rows, and use only the implicit runtime state `N/A`; `N/A` is never a
reference-row label.

The rules are defined by the [Offline Registry Protocol](REGISTRY_PROTOCOL.md):
absence, incomplete evidence, conflict, or staleness is `UNKNOWN`, never
`MISMATCH`. Registry reviewers never visit a live destination. Actor–destination
consistency is only one evidence channel: phishing can use an apparently
compatible destination, and benign content can have an `UNKNOWN` relation.

Blind reliability therefore covers actor/destination endpoint and span
agreement. A derived Cartesian endpoint-inventory metric may compare endpoint
range products, but it is not pair-link or relation annotation. Engine
falsification uses q-weighted exact labelled pair-set F1 over actor/destination
`VMP` ranges and registry state against the separate reference. Every metric run
binds the exact canonical schema-`1.0.0` `registry_reference_bundle`; this is an
engine/evaluation manifest, not a dataset-row schema. Its registry snapshot,
resolver, registry-manifest hash, and reference-artifact hash must equal the
inference bindings even for a zero-pair item. Before inference, the exact
canonical evaluation-universe `1.0.0` manifest/hash binds the dataset artifact
hashes, bundle hash, and the complete, not sampled, nonempty UTF-8-sorted
eligible set from the named partition, with one to 10,000 entries. Each entry binds partition, VMP,
final annotation, and the exact byte size/hash of its versioned canonical gold
inventory; omission, extra, duplicate, or reorder invalidates the universe. A
separate discriminated metric-run `1.1.0` manifest has a `VALID` branch with
exactly one valid engine envelope per universe item in order and an `INVALID`
branch with no metrics, a submitted-inference manifest hash, and bounded
discrepancy counts, including disjoint universe and declared-denominator error
counts. It derives `N_all`, `N_gold_empty`, and `N_gold_nonempty`.
The deterministic strict universe receipt precedes submission preflight, and
both structural passes precede semantic closure. Either preflight failure
produces only its receipt. A structurally valid but semantically invalid
universe, including an empty one, produces the exact universe-error invalid
metric run, opens no envelope, and emits no metric. Malformed, oversized,
non-UTF-8, or noncanonical submitted descriptor bytes are
instead rejected before any metric-run manifest by the bounded canonical
`MetricInputReceipt` `1.0.0`; no metric values exist on that path. For a valid
bounded submitted list, the engine scans left to right and classifies each row
once as duplicate, first extra, or unique expected, then derives missing and
positional reorder counts. Only unique expected rows enter the exclusive
`INVALID`-envelope, then `DEGRADED_STOP_AFTER_IDENTITY`, then binding-mismatch
precedence. Any nonzero discrepancy count invalidates the run and emits no
metrics. A final endpoint/reference, inference path, packet,
alignment, resolver, artifact/hash, VMP/gold/bundle/snapshot/resolver, or finite-
output failure; or declared-denominator mutation invalidates the whole applicable run
and never silently removes an item.

Micro path-weighted TP/FP/FN aggregate over all `N_all`, using weight one for
`C01` rank one and `q_k` for `C11`: a nonempty prediction on
gold-empty contributes FP, while both-empty contributes zero counts. Report
`N_all`, `N_gold_empty`, `N_gold_nonempty`, pair F1, and
`pair_emptiness_accuracy` on all `N_all`. `C01` reports rank-1 values; `C11`
reports rank-1 and q-weighted path-marginal values plus fixed-denominator
gold-empty and gold-nonempty recalls when those denominators are nonzero;
`C00`/`C10` report `N/A`. Blind relation alpha/F1 is prohibited because blind
annotators never received that information.
Pair precision, recall, and F1 are canonical `+0.0` when their own denominator
is zero. That natural algebraic case is never a declared-denominator mismatch.
Every valid metric run has `1<=N_all<=10000`, so pair-emptiness accuracy has a
positive denominator.

## 6. Romanization ambiguity and acceptable forms

Add a `romanization_ambiguities` entry when a Roman-script surface span has two or more linguistically plausible intended readings, segmentations, native-script forms, or semantic interpretations relevant to a facet or label. The raw ambiguity span must align to observed Latin script and be assigned language `hi`, `ta`, or `te`. Each entry must contain at least two unique acceptable forms. For uniqueness only, canonicalize each candidate `form` by Unicode NFKC, case-fold it, split on all Unicode whitespace, and join the resulting fields with one ASCII space; the uniqueness key is `(canonicalized form, declared script)`. Gloss-only, case-only, compatibility-only, and whitespace-only variation does not create a second form. Every declared form script must match its form's observed Unicode script. This canonicalization never rewrites or normalizes the raw message, ambiguity span text, or offsets. A nonempty array and machine ambiguity tag `romanization` must occur together; both are absent when no ambiguity is recorded. Each entry stores:

- exact `start`, `end`, and substring `text` from the raw message;
- `language` (`hi`, `ta`, or `te`);
- `acceptable_forms`, each containing `form`, `script`, and a short `gloss`;
- `affected_decisions`, selected from `primary_label` and the six facet names.

Annotators do not assign candidate probabilities or select a single model path. Candidate weights are learned or calibrated later. An ordinary Romanized spelling variant is not an ambiguity when all reasonable readings preserve the same intended form, meaning, and annotated decision. Preserve its raw spelling, but create no separate snapshot field or `romanization_ambiguities` entry. Only decision-relevant ambiguity enters the machine snapshot.

The downstream candidate generator may select only sorted, nonoverlapping
Romanized rewrite spans that do not overlap any visible artifact range. Every
configured or effective `span_index`, `start`, and `end` is a non-Boolean
integer; indices are contiguous from zero; `0 <= start < end <= len(VMP.text)`;
source text is the exact slice; and the configured list is bounded by 64.
No-eligible bypass has none; a provider-failure run retains its attempted
nonempty configured spans only in its run envelope and emits no effective span.
Every
candidate path must retain complete `VMP` alignment; model endpoints and all
gold losses remain `VMP` ranges, never candidate offsets or back-projected
ranges. Complete alignment means one nonempty interval per normalized output
Unicode code point, separately nondecreasing starts and ends, within-one-span
rewrite intervals, and complete source-code-point coverage. Normalization must
transform text and alignment together under the exact rejection rules in the
engine specification. These are engine constraints, not additional annotator
judgments.

Acceptable-form sets and their adjudications must be frozen before any model result on those items is inspected. Adding a candidate because it improves a result is prohibited. If no defensible candidate set can be formed, use the `ROMANIZATION` ambiguity tag and send the item to adjudication or exclude it.

Illustrations:

- `jldi`, `jaldi`, and `jaldee` can be acceptable surface variants for an intended Hindi reading meaning “quickly”; they need not be separate semantic candidates when the meaning is unchanged.
- A short surface form with plausible readings in two languages is an ambiguity only when both readings survive message context; otherwise annotate the context-supported language and retain the observed spelling.
- Emoji or digit substitution, such as a digit inside a word, remains verbatim in raw text. Record the interpreted form only in the candidate annotation; never rewrite the source.

## 7. Hard cases

These are synthetic decision patterns, not collected data and not an exhaustive gold set.

| Case | Example | Required decision |
|---|---|---|
| Benign urgency and action | `Reminder: your clinic appointment is today; please arrive by 4 PM.` | `BENIGN/TRANSACTIONAL`; urgency and an action are insufficient for phishing. No destination endpoint is annotated, so no registry-reference row is created; runtime resolver state is `N/A`. |
| Phishing without a destination | `Bank officer bol raha hoon. Account bachane ke liye OTP abhi reply karo.` | `PHISHING`; actor, threat/urgency, reply action, and OTP asset are present. No destination endpoint is annotated, so no registry-reference row is created; runtime resolver state is `N/A`. No live OTP value appears. |
| Benign with an unknown destination | `Community class notes are available at portal.example; no login or payment is requested.` | `BENIGN/INFORMATIONAL` from visible text alone; annotate the visible destination. A separate registry reviewer may return `UNKNOWN`; hidden scenario intent is irrelevant. |
| Phishing with a plausible destination | `Security team: confirm your password at account-help.example.` | `PHISHING` because it solicits a password through deceptive social engineering even if a destination appears plausible; do not force `MISMATCH`. |
| Promotion | `Weekend sale: 20% off at shop.example.` | `BENIGN/PROMOTIONAL` unless additional evidence meets the phishing definition. Reward language alone is insufficient. |
| Low-pressure phishing | `Example Support: send your one-time login code to this chat when convenient so we can unlock your account.` | `PHISHING` from the visible credential request and claimed support role; urgency is not required. A less explicit request that needs scenario intent remains `UNCERTAIN`. |
| Obfuscation and emoji | `V3rify n0w 🔒 at access.example.` | Preserve raw text exactly; annotate interpreted action only as derived annotation. Obfuscation does not decide the label by itself. |
| Unresolved context | `Please update it here.` | Retain final annotation `UNCERTAIN` with resolution `UNRESOLVED`, set item status to `EXCLUDED`, and leave binary gold absent if no permitted context resolves actor, action, or intent. |
| Benign actor–destination match not provable | `Example College: the public course brochure is available at admissions.example; no sign-in is required.` | `BENIGN/INFORMATIONAL`; annotate both visible endpoints. The separate registry reviewer returns `UNKNOWN` unless approved evidence supports `MATCH`. |

Every translated or Romanized version is linked to its parent by lineage/equivalence identifiers and must remain in the same final leakage component and partition.

## 8. Pre-annotation structured-state coverage manifest

Before any real pilot item is released to blind annotators, a separate steward
must freeze a component-aware candidate coverage manifest. The steward may use
only the same immutable schema-1.2 VMP available to annotation plus the approved
frozen offline registry for a planned actor–destination state. The steward must
not use provenance class, source label, author intent, scenario, prompt, donor
identity, generation method, or another hidden field.

For each of the four language strata and its 300-retained-item target, the frozen candidate plan must include:

- for **each** of the six facets, at least 30 candidate items with a visible explicit cue and at least 30 candidate items without a visible explicit cue; and
- at least 30 candidate items for **each** planned actor–destination state: `MATCH`, `MISMATCH`, `UNKNOWN`, and `N/A`.

One candidate may satisfy several facet and relation-coverage quotas. These overlaps are allowed, but the coverage plan does not replace or relax the final requirement of 150 `BENIGN` and 150 `PHISHING` retained items per stratum. The counts are `30/300` design-coverage minima intended to expose endpoint and resolver states; they are not precision, power, prevalence, performance, independence, or reliability claims.

Candidate cue/state tags are sampling metadata, **not gold annotations**. They
remain hidden from blind annotators, the final adjudicator, and later outcome
analysis, and no tag may populate, override, break a tie in, or retrospectively
correct a primary label, facet, span, endpoint, evidence, language, or registry
reference. Planned relation-state coverage additionally requires the pre-pilot
registry's mechanical binding and separate human authority/completeness
approval.

The manifest must bind the exact candidate item references to their already computed final `leakage_component_id`, preserve the prespecified candidate and reserve order, report both item and distinct-component counts for every quota, and keep each connected component in one partition. It must bind the annotation-guide version and registry snapshot/hash used for steward review. Its exact representation, steward decision, quota table, native-review audit decision, and cryptographic hash are frozen before blind release. The current dataset-snapshot CLI has no coverage-manifest input and cannot validate the steward's linguistic or semantic judgments; this remains an external, human-audited pre-pilot gate.

At least one qualified native-language reviewer for the relevant stratum must audit token-language judgments and every coverage cell before release. A missing reviewer, failed quota, unbound component, mutable manifest, or missing hash blocks pilot collection. Once an item begins blind annotation, it remains an attempted item and cannot be removed because annotators disagree, a candidate tag was wrong, or a metric worsens. Replacements follow only the frozen reserve order and prespecified eligibility rules. Achieved reliability is computed from blind annotations under the frozen contract; any undefined gated metric still fails.

## 9. Annotation workflow

1. A data steward verifies source-ledger authorization, safety, de-identification, provenance, and eligibility outside the annotation interface.
2. Restricted preprocessing assigns a random corpus identifier, opaque lineage/equivalence keys, and the final `leakage_component_id`. Direct identifiers, secret keys, provenance, source labels, authoring intent, scenarios, prompts, and generation metadata never enter the semantic annotation interface.
3. Two qualified annotators independently and blindly see only the `VMP`. They
   assign stratum, primary label, benign subtype when applicable,
   confidence/ambiguity, facets, spans, supporting evidence, and visible
   actor/destination endpoints. A separate steward handles authorization and
   provenance eligibility.
4. Automated checks reject invalid enums, broken offsets, missing applicable facets, and prohibited artifacts. Automation does not create a gold label.
5. A third qualified annotator, distinct from both blind annotators, creates the
   final record for every attempt and resolves material semantic disagreements,
   still without registry or provenance. Original records remain immutable.
6. A separate blinded registry reviewer resolves the mechanically generated
   Cartesian product of final visible endpoint sets using the frozen registry
   and writes the separately versioned registry reference. No human pair link is
   annotated.
7. After final adjudication and manifest/hash freeze, an independent auditor
   executes the [canonical human pilot safety and provenance audit](#canonical-human-pilot-safety-and-provenance-audit),
   including required annotator-coverage supplements.
8. Only the adjudicated, versioned output plus its separately governed registry
   reference can enter a release candidate. Partition assignment uses complete
   leakage components, never individual rows.

Annotators must be adults and proficient in the assigned language/script varieties. Exact qualifications, training set, payment, workload limits, conflict-of-interest policy, and named adjudicators are **UNKNOWN** and must be approved before the pilot.

## 10. Leakage-safe grouping

Connected components must join any items related by exact or near duplicate; translation, transliteration, paraphrase, counterfactual, or augmentation lineage; scenario, template, or campaign; domain, URL, UPI, phone, sender, organization artifact, or other destination; tester, donor, author, or collection batch; public source family; or LLM prompt, model, and generation batch. Public-derived and LLM-derived descendants inherit their ancestry regardless of the immediate row's provenance or generation field.

Where grouping depends on sensitive artifacts, restricted preprocessing creates either random opaque equivalence identifiers or deterministic keyed-HMAC tokens. It computes transitive closure over **all** opaque equivalence and lineage keys, then writes `leakage_component_id` as the final component assignment. This field is not a donor-provided batch hint or a freely chosen row identifier. Raw artifacts, component inputs, secret keys, lookup tables, and reversible mappings are not stored in corpus rows, annotations, logs, Git, or released files. Key owner, storage, rotation, access, destruction, and cross-release stability are **UNKNOWN blockers** defined in the privacy package.

One final component is assigned to exactly one partition. Every item in `probability_calibration`, `safety_threshold`, or `primary_test` must be a singleton component containing one item and one language stratum. Any related family with more than one row is ineligible for these protected partitions; it cannot be split to manufacture independence.

## 11. Pilot design and pass/fail gates

The ontology pilot contains exactly 1,200 **retained** items in partition `pilot`: 300 per language stratum, with 150 final `BENIGN` and 150 final `PHISHING` items in each stratum. It tests the ontology and guide, not model performance. A pilot attempt begins only after a row passes the frozen pre-annotation eligibility/safety rules and is released to blind annotation. Every such attempted item receives two blind independent annotations and one final record from a third annotator. Pre-annotation rejects are reported separately in the sampling flow and cannot be relabeled as pilot attempts.

Any pilot attempt with unresolved final primary label and/or final language stratum moves to partition `excluded`. These are additional attempted rows outside the retained 1,200, remain auditable, and all count in the unresolved numerator and denominator. If `E` attempts are excluded after completing 1,200 retained rows, the gate is `E / (1,200 + E) <= 0.05`. All prospectively sampled items and exclusion reasons must be accounted for. Replacement is allowed only under prespecified eligibility rules; reviewers may not discard difficult, disagreeing, low-confidence, or inconvenient items merely to reach balance or agreement gates.

### Canonical human pilot safety and provenance audit

This subsection is the authoritative human audit protocol for the ontology pilot. Its universe is every retained `pilot` item plus every `excluded` attempted item after final adjudication. Let `N_attempted` be that universe size. An audit unit is the whole linked item/source/annotation bundle: exact item record, source record and applicable governance evidence, both blind annotations, and the final annotation.

The main audit size is `n = ceil(0.10 × N_attempted)`. Partition the universe into the nonempty cross-product cells of:

- final language state: `hindi`, `tamil`, `telugu`, `english_indic_code_mixed`, or `uncertain`;
- final primary state: `benign`, `phishing`, or `uncertain`; and
- source provenance class: `tester_donated_authentic`, `tester_authored_simulation`, `public_authentic`, or `llm_drafted_human_edited`.

Define a cell's ASCII `cell_key` as `language_state|primary_state|provenance_class`. Let `H` be the number of nonempty cells and `N_h` the capacity of cell `h`. Give every nonempty cell one main-sample item. For the remaining `R = n - H` slots, use Hamilton largest remainder on remaining capacities `C_h = N_h - 1`: compute quota `q_h = R × C_h / Σ_h C_h`, allocate `floor(q_h)`, then assign unfilled slots in descending fractional-remainder order. Break equal remainders by ascending UTF-8 byte order of `cell_key`. There are at most `5 × 3 × 4 = 60` nonempty cells and `N_attempted >= 1,200`, hence `n >= 120` and one-per-cell allocation is feasible. If either bound is violated, audit the entire attempted universe so every cell is covered and block release until a revised sampling rule is declared before another draw.

After the item manifest, source manifest, annotation manifest covering all three records per item, and their hashes are frozen, an independent auditor performs exactly one witnessed 32-byte operating-system CSPRNG draw. Redraw is prohibited. Record the 64-character lowercase hexadecimal seed, draw time, witness, and auditor identity in the audit evidence. Within each cell, rank items by the raw HMAC-SHA256 digest with the 32 seed bytes as key and `UTF8(cell_key + NUL + item_id)` as message. Select the required number of lowest digests; break an identical-digest tie by ascending UTF-8 byte order of `item_id`.

Every selected bundle includes all three annotation records. After the main
sample is fixed, freeze the complete list of annotator IDs absent from those
bundles. Process that initially missing list once in ascending UTF-8 byte order.
Before processing each ID, skip it if a supplement selected for an earlier ID
already covers it; otherwise add the lowest-HMAC-ranked eligible bundle that the
ID annotated and that is not already selected. There is no redraw or
replacement. This minimal-exposure supplement pass never reduces or replaces
the main `n`; record the initially missing list, skips, choices, and final
coverage separately.

The auditor checks each complete bundle for exactly these prohibited findings:

- active HTTP/HTTPS/FTP/`www` route or bare live domain, including IDN labels and Unicode-dot equivalents;
- live email or `mailto` route, valid IPv4 address, phone number, UPI identifier, or bank/account identifier;
- credential, password, PIN, OTP, or authentication code;
- unredacted direct identifier;
- executable or redirect instruction, or unsafe attachment reference; or
- missing or contradictory consent, rights, provenance, lineage, privacy, safety, registry binding, or structured-state coverage binding.

Representations that pass the schema-1.2 `RESERVED` grammar ending in
`.example` or `.invalid`, and approved schema-valid defanged/typed-placeholder
forms, are not active-route findings on grammar alone. `.test` is not accepted
by that `RESERVED` grammar. The allowed finding count is zero. Any prohibited
finding fails the audit: do not replace the sampled item; stop processing and
quarantine the affected leakage family; follow the approved incident process;
repair the upstream defect; freeze a new data/manifest version; then run a 100%
machine scan and a new audit with a fresh, independently witnessed seed before
release can be reconsidered.

Auditors must never visit, resolve, call, message, execute, redirect through, install, open, or otherwise interact with a route or attachment. This human audit does not replace machine validation, and a clean machine scan does not replace this human audit.

All gates below must pass under the same frozen guide version:

- binary primary label: Krippendorff's alpha at least `0.80` and raw agreement at least `90%`;
- binary blind-pair coverage: both blind labels are binary for at least `95%` of all retained-plus-excluded attempted items; `UNCERTAIN` is never coerced to a binary label;
- language stratum: report raw blind agreement across `hindi`, `tamil`, `telugu`, `english_indic_code_mixed`, and `uncertain`; nominal Krippendorff alpha uses all valid attempted-item blind pairs, must be at least `0.80`, and has no separate raw-agreement gate;
- every one of the six structured facet applicability states: Krippendorff alpha at least `0.67` overall;
- endpoint-aware `claimed_actor`, `requested_action`, and
  `destination_artifact` categories: alpha at least `0.60` within each resolved
  study stratum;
- each structured facet's spans, scored on union-explicit blind pairs: macro exact F1 at least `0.60` and character-overlap F1 at least `0.75`;
- supporting-evidence spans, scored separately: macro exact F1 at least `0.60` and character-overlap F1 at least `0.75`;
- mechanically derived Cartesian actor/destination endpoint inventory on
  applicable union products: exact F1 at least `0.60`; this is endpoint-range
  structure, not blind pair-link or registry-state agreement;
- annotation-bundle completeness: at least `95%` of all retained-plus-excluded
  attempted items have exactly two valid, distinct independent blind records
  and exactly one semantically valid final record with complete applicable
  facet, span/evidence, endpoint, and language structure; the final may be
  binary or a permitted unresolved `uncertain` record matching the excluded
  state;
- excluded unresolved attempts after adjudication: at most `5%` of all fully annotated pilot attempts, with every excluded attempt in the numerator and retained-plus-excluded attempts in the denominator;
- [canonical human pilot safety and provenance audit](#canonical-human-pilot-safety-and-provenance-audit): the frozen main sample and any annotator-coverage supplements are audited under the exact protocol above, with zero prohibited findings.

Agreement is calculated on the two independent pre-adjudication annotations.
The executable metric contract must preserve exact units, missing-state
handling, endpoint matching, union-explicit/applicable denominators, span and
Unicode-overlap formulas, completeness, and undefined-metric behavior; every
undefined gated metric fails. It must not reinstate blind registry-state
alpha/F1. The separate registry-reference audit and end-to-end labelled
pair-set metric cannot substitute for blind endpoint reliability.

If a gate fails, revise the guide, document the reason, and reannotate every affected gate row under the final guide version. Then run a fresh double-annotated confirmation wave with 300 retained binary-labeled items that does not reuse pilot items; any unresolved attempts are additional rows and use the same denominator rule. Do not scale to the 6,000-item corpus until the revised gate set passes. The later corpus target is 1,500 items per stratum (750 phishing and 750 benign), subject to the preregistered data and independence gates.

## 12. Provenance boundaries

Every item has exactly one source provenance class:

- `TESTER_DONATED_AUTHENTIC`: an adult tester voluntarily donates a real message they are authorized to share; it is de-identified and safety-processed before annotation.
- `TESTER_AUTHORED_SIMULATION`: an adult tester writes a fictional message from an approved scenario; it is never represented as authentic.
- `PUBLIC_AUTHENTIC_AUXILIARY`: an authentic public-source item with verified license, hash, privacy/safety audit, and independent Fisher reannotation; it and every descendant are eligible only for `development` or `external_test`, never the ontology pilot or another partition.
- `LLM_DRAFTED_HUMAN_EDITED`: a model drafts text that a human reviews and materially edits; the model never supplies the gold label.

Their exact dataset-contract source values are, respectively, `tester_donated_authentic`, `tester_authored_simulation`, `public_authentic`, and `llm_drafted_human_edited`. The shorter machine value `public_authentic` does not change the development/external-test-only restriction.

Direct LLM-drafted/human-edited items and every descendant of LLM lineage together may be no more than 30% of retained `development` and no more than 30% of the retained `pilot`. They have 0% allocation to `probability_calibration`, `safety_threshold`, and `primary_test`. Direct public-authentic items and every descendant of public lineage are restricted to `development` and `external_test` only.

The `primary_test` partition is tester-originated only. Both `tester_donated_authentic` and `tester_authored_simulation` are permitted after all other gates, but they remain separately reported in every primary result; simulation is never described as authentic field prevalence. Donation-versus-simulation composition is also reported for `probability_calibration` and `safety_threshold`. In each of the eight label × stratum primary-test cells, at least 50% of retained items must be authentic donations: at least 125 of each 250-item phishing cell and at least 150 of each 300-item benign cell. This is a Paper 1 claim-routing gate, not authorization to collect. If any cell misses it, route the result to a controlled-benchmark/research-prototype claim and prohibit field-like generalization.

No source label, provenance, scenario, or generation method is shown to semantic annotators or used to justify gold. Provenance is retained for eligibility, grouping, audit, and disaggregated reporting and cannot be inferred from filenames.

## 13. Pre-pilot blockers and sign-off

The guide becomes eligible for pilot use only when all of the following are recorded:

- approved consent/ethics/privacy package and all named blocker fields;
- approved source-ledger schema and one authorized ledger entry per source;
- aligned, executable data contract and validator;
- executable full governance-ledger validator passing every source authorization record; the dataset-snapshot CLI is not a substitute;
- approved native-language reviewers, annotator qualifications, training, and adjudication procedure;
- frozen primary-label examples and acceptable-form policy;
- minimal audited frozen offline registry manifest/namespace, mechanical
  snapshot binding, blinded registry-review workflow, and separate human
  authority/completeness approval;
- aligned schema/validator that stores blind visible endpoints separately from
  the versioned registry-reference artifact, with independent review;
- frozen component-aware structured-state coverage manifest meeting every per-stratum facet/relation quota, with qualified native-reviewer audit and recorded hash, before any pilot item is released;
- frozen metric implementation aligned with the machine contract;
- successful dry run using only synthetic reserved/defanged fixtures;
- reviewed `corpus-final` validator design recorded as a mandatory pre-corpus-freeze gate even though the current implementation does not yet provide it;
- dated sign-off by the research lead, ethics/privacy owner, data steward, and annotation lead.

Until then, the status remains **DRAFT — BLOCKED FOR COLLECTION**.
