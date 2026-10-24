# SMSDHL Dravidian Workbook Audit

## Evidence boundary

This document records a local, read-only audit of the user-supplied workbook
`Spam Message Collection (1).xlsx`. The workbook remains outside the repository.
Its SHA-256 is
`24ca099ac1ffabc0b02fd491f57d577c56afb932bc81c5964a40e32eab9a023b`.

The workbook appears consistent with the linked IEEE DataPort Dravidian
spam/ham collection, but the file alone does not prove provenance or the terms
accepted at download. The DataPort record is
<https://ieee-dataport.org/documents/spam-sms-dravidian-languages>. Preserve the
download-time license and terms before any redistribution or publication.

## Intended use

**Decision:** use this workbook only for duplicate-controlled, in-corpus
**spam-versus-ham development experiments**.

It is not phishing-labelled data. It cannot establish phishing performance,
transliteration novelty, a campaign/source-disjoint result, per-language
performance, a low-false-positive safety claim, or deployment readiness.
Consented tester messages annotated with Fisher's phishing ontology remain the
future primary evidence.

## Observed workbook structure

| Property | Observed value |
| --- | ---: |
| Sheets | 1 (`Dravidian Dataset`) |
| Columns | `Message`, `Type` |
| Loaded data rows | 7,718 |
| Nonempty messages | 7,715 |
| `Ham` labels | 6,322 |
| `Spam` labels | 1,394 |
| Malformed `Spa,` labels | 1 |
| Blank labels | 1 |
| Formula cells | 0 |

The median message length is 76 Unicode code points and 10 whitespace tokens.
The 95th percentiles are 191 code points and 28 whitespace tokens; the maximums
are 515 and 80.

## Duplicate and label audit

The duplicate key is Unicode NFKC normalization, removal of Unicode `Cf` format
controls, case folding, and whitespace collapse. Removing format controls from
the grouping key prevents invisible variants from crossing folds; the model
text itself is not stripped or overwritten.

The conservative policy builds the label set for every nonempty normalized
group before accepting binary labels. A group containing an unknown label or
both binary labels is contaminated. This prevents the malformed `Spa,` row from
silently legitimizing its matching `Spam` duplicate.

| Controlled disposition | Rows/groups |
| --- | ---: |
| Extra normalized duplicate rows in the raw audit | 1,231 |
| Contaminated/conflicting normalized groups | 28 |
| Binary rows quarantined from those groups | 57 |
| Same-label duplicate rows removed | 1,201 |
| Post-defang residual-candidate rows quarantined | 23 |
| Unique controlled rows after quarantine and deduplication | 6,433 |
| Controlled ham rows | 5,328 |
| Controlled spam rows | 1,105 |

Random row splitting is prohibited because repeated messages would cross folds
and inflate results. The development pipeline additionally groups number- and
route-normalized templates so simple campaign-like variants remain in one fold.
Because the workbook has no sender, author, campaign, or source identifier, this
is template-grouped development evaluation—not campaign-disjoint evaluation.

## Mechanical script audit

The following categories are computed from Unicode Letter/Mark code points.
They are script descriptions, not language labels. In particular, Latin text
can be English, Romanized Indic, code-mixed, or another language.

| Dominant script category | Displays after in-memory defanging | Controlled rows |
| --- | ---: | ---: |
| Latin | 2,141 | 1,194 |
| Malayalam | 1,911 | 1,819 |
| Kannada | 1,304 | 1,152 |
| Tamil | 1,135 | 1,102 |
| Telugu | 1,013 | 966 |
| Mixed | 210 | 199 |
| No letters | 1 | 1 |

## Safety and privacy boundary

The workbook contains live-route and personal-data-like strings. The primary
pipeline scanner counted 368 URL, 591 domain, 12 email, and 435 phone
occurrences before defanging. Counts overlap and are scanner-specific indicators,
not verified personal-data totals. An independent post-defang scan found 23
disjoint residual-candidate rows: nine spaced-HTTP, nine spaced-domain, three
undotted-handle, and two broader-phone candidates. All 23 are quarantined.

The workbook also has 29 Excel hyperlink cells; 14 stored targets differ from
their displayed text. The pipeline ingests only displayed cell values and
records only the hyperlink-cell count. It does not ingest or persist hyperlink
targets.

The pipeline therefore enforces these boundaries:

1. keep the source workbook outside Git;
2. avoid printing raw rows or live artifacts;
3. replace detected routes with typed placeholders only in the in-memory model
   view;
4. quarantine any row that still contains a detected live artifact;
5. persist only aggregate audits, run manifests, and metrics; and
6. never export message text to CSV or a spreadsheet.

## Frozen first experiment

The first experiment contains only:

- character TF-IDF (3–5 grams) with class-balanced logistic regression; and
- word TF-IDF (1–2 grams) plus character TF-IDF (3–5 grams) with a
  class-balanced linear SVM.

Evaluation is deterministic, template-grouped, stratified out-of-fold
development evaluation. It reports confusion matrices, spam
precision/recall/F1, macro F1, balanced accuracy, descriptive average precision,
fold support, group counts, and mechanical per-script results. Do not label any
fold as a protected or primary test set.

## Measured development run

The implemented seed-1729 run used three folds containing 2,144, 2,145, and
2,144 rows across 6,377 template groups. No template group crossed folds. The
single `ham|no_letters` row makes exact composite stratification impossible, so
the run manifest marks stratification as approximate.

| Model | Spam precision | Spam recall | Spam F1 | Macro F1 | TN | FP | FN | TP |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Character TF-IDF + logistic regression | 0.9209 | 0.8950 | 0.9078 | 0.9445 | 5,243 | 85 | 116 | 989 |
| Word + character TF-IDF + linear SVM | 0.9568 | 0.8824 | 0.9181 | 0.9509 | 5,284 | 44 | 130 | 975 |

Two same-seed runs produced byte-identical aggregate audit, manifest, and metric
files. Pooled out-of-fold average precision remains descriptive because scores
from separately fitted folds are not calibrated to one common scale; the output
also records mean per-fold average precision. No classifier is designated a
paper winner from this one development run.

## Auxiliary nested model selection v0.2

The next development experiment used nested `StratifiedGroupKFold` selection:
three outer folds estimate the selected policy, while three inner folds select a
configuration independently inside each outer-training partition. Template
groups remain intact. The controlled input has 6,433 rows and 6,377 template
groups; no group crossed an outer or inner fold, and no template group contained
both labels.

The fixed candidate set contains eight configurations:

| Feature/classifier family | Candidate `C` values |
| --- | --- |
| Character TF-IDF + class-balanced logistic regression | `0.5`, `1`, `2` |
| Character TF-IDF + class-balanced linear SVM | `0.5`, `1` |
| Word + character TF-IDF + class-balanced linear SVM | `0.5`, `1`, `2` |

Each candidate's TF-IDF features are fitted only on its current training
partition. Selection ranks mean inner-fold spam F1, then macro F1, then spam
precision, followed by a deterministic tie-break. The complete run performs 72
inner candidate fits, three selected outer refits, and six frozen-baseline outer
fits: 81 fits total. Classifiers use their default decision thresholds. There is
no threshold tuning and no score calibration.

Run it only after creating the intended safe output parent:

```console
mkdir -p outputs/smsdhl_dravidian
uv run python -m fisher_baselines nested-evaluate \
  --workbook "/path/to/Spam Message Collection (1).xlsx" \
  --output outputs/smsdhl_dravidian/nested_seed_1729.json \
  --seed 1729 --outer-folds 3 --inner-folds 3
```

The destination must not already exist. The command publishes one canonical,
aggregate JSON file. It does not persist a trained model, vocabulary, row-level
predictions, source path, or selected sheet name.

### Measured nested result

Inner selection chose character linear SVM with `C=1` for outer folds 0 and 1,
and word+character linear SVM with `C=1` for outer fold 2. Its outer-fold summary
and the frozen word+character linear SVM `C=1` comparator were:

| Policy | Spam precision | Spam recall | Spam F1 | Macro F1 | Balanced accuracy | Mean fold AP | TN | FP | FN | TP |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Nested selected policy | 0.963790836 | 0.885975119 | 0.923204619 | 0.954016326 | 0.939515336 | 0.964974856 | 5,291 | 37 | 126 | 979 |
| Frozen word+character SVM, `C=1` | 0.956858475 | 0.882351930 | 0.918090119 | 0.950945875 | 0.937046888 | 0.963414111 | 5,284 | 44 | 130 | 975 |

The selected policy improved mean spam F1 by `0.005114500`, improved mean macro
F1, and was not worse on spam F1 in any outer fold. The predeclared acceptance
rule nevertheless required at least `0.01` mean spam-F1 improvement over the
frozen comparator. Therefore the recorded acceptance decision is **false**.
This is promising but inconclusive auxiliary spam/ham development evidence.

Two measured executions produced byte-identical 14,052-byte JSON artifacts with
SHA-256
`cc821dee5e20b5b04926f6ebb708d2bfc67a8ba466ec7a3960743ed6282ca5ec`.
Their wall-clock runtimes were 70.65 and 71.58 seconds; maximum resident memory
was 398,360,576 and 417,742,848 bytes. These measurements describe this local
run only and are not performance guarantees.

No deployable model was created. In particular, this experiment does not alter
the browser extension, which remains a transparent rule-only prototype. The
earlier first-experiment measurements above remain the historical baseline,
rather than being replaced or reinterpreted as nested-test results.

## Held-out comparison v0.3: rules versus calibrated lexical models

This experiment answers a question the earlier runs left open: how does the
**shipped v0.5 rule engine** compare with trained lexical models, and how do
calibrated models behave at a low-false-alarm operating point on data that
played no role in fitting, calibration, threshold choice, or model selection?

Protocol (all decisions are fixed before the test partition is scored):

1. `StratifiedGroupKFold(5)` over label+script strata and template groups; fold
   0 (1,287 rows, 221 spam) is the held-out test partition and the other 5,146
   rows are development. Zero template groups cross the boundary.
2. Each lexical model receives NFKC + Unicode `Cf` removal (the same folding as
   the duplicate key), produces grouped four-fold development out-of-fold scores,
   and fits a Platt sigmoid on them. The operating threshold is the lowest one
   whose development out-of-fold ham false-positive rate is at most 1%. The model
   is then refitted on all development rows.
3. The selected model is the one with the highest development out-of-fold spam
   recall at that threshold (then AP). The rule engine is untrained and is
   scored as positive when it returns `review` or `high`.
4. The test partition is scored once. Robustness perturbations, template-group
   paired bootstrap intervals (1,000 resamples), and per-slice metrics are
   computed on it. An unnormalized model is reported as an ablation and is
   excluded from selection.

```console
uv run python -m fisher_baselines holdout-evaluate \
  --workbook "/path/to/Spam Message Collection (1).xlsx" \
  --output outputs/smsdhl_dravidian/holdout_seed_1729.json --seed 1729
```

The output must not already exist and its parent must. It is one aggregate JSON
file; no text, prediction, model, or vocabulary is persisted.

### Measured held-out result (seed 1729)

Development selected `word_char_linear_svc`. The test results at each approach's
operating point were:

| Approach | Spam precision | Spam recall | Spam F1 | Ham FPR | AP | ROC AUC | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Rules v0.5 (`review` or `high`) | 0.9375 | 0.0679 | 0.1266 | 0.0009 | 0.2237 | 0.5335 | 1 | 206 |
| Char TF-IDF + LR, calibrated | 0.9507 | 0.8733 | 0.9104 | 0.0094 | 0.9585 | 0.9906 | 10 | 28 |
| Word+char TF-IDF + linear SVM, calibrated (selected) | 0.9488 | 0.9231 | 0.9358 | 0.0103 | 0.9642 | 0.9937 | 11 | 17 |

The rule engine returned `high` for no test message. The selected model's test
Brier score was 0.0175 and its 10-bin expected calibration error was 0.0076.
Paired template-group bootstrap 95% intervals for selected-minus-other were:
spam F1 +0.809 [0.743, 0.870] and recall +0.855 [0.807, 0.902] against the
rules, and spam F1 +0.025 [-0.001, 0.052] and recall +0.050 [0.018, 0.082]
against character LR. The F1 interval against LR includes zero.

Spam recall / ham FPR on the test partition under perturbation:

| Perturbation | Rules | Char LR | Selected SVM | SVM without normalization |
| --- | ---: | ---: | ---: | ---: |
| None | 0.068 / 0.0009 | 0.873 / 0.0094 | 0.923 / 0.0103 | 0.923 / 0.0094 |
| Uppercase | 0.068 / 0.0009 | 0.873 / 0.0094 | 0.923 / 0.0103 | 0.923 / 0.0094 |
| Latin→Cyrillic homoglyphs | 0.014 / 0.0009 | 0.855 / 0.0103 | 0.910 / 0.0084 | 0.910 / 0.0075 |
| Zero-width joiner between characters | 0.253 / 0.0281 | 0.873 / 0.0094 | 0.923 / 0.0103 | **0.000 / 0.0000** |
| Truncate to 64 code points | 0.014 / 0.0000 | 0.538 / 0.0084 | 0.665 / 0.0113 | 0.665 / 0.0113 |

Without normalization, zero-width-joiner insertion reduced the lexical model's
spam recall to zero. Normalization restored it, and the clean-test cost was one
additional false positive. This normalization decision was informed by the
test-partition perturbation, so the normalized row is not a fully blind estimate
of that design choice.

Selected-model slices: Telugu spam recall 0.833 (18 spam) and Latin-script ham
FPR 0.029 (175 ham) are the weakest script slices. Both of the 2 spam messages
of at most 40 code points were missed. Slices with fewer than about 50 spam
examples are too small for stable estimates.

Two same-seed runs produced identical outputs apart from timing fields (output
SHA-256 of one run:
`d6f7c9622fb3d9a34c7284401ff7bbf4f7d5a06f4b930cded6f5a3b29e511a91`).
Wall-clock time was 20–28 s and peak resident memory was 469–512 MB. The selected
model fitted in about 1.5 s, predicted about 0.14 ms per message, and pickled to
about 4.8 MB in memory. These describe one local machine.

### Interpretation boundary

**OBSERVED:** on this spam/ham corpus, the rule engine almost never fires. That
is consistent with its design for credential and phishing pressure cues rather
than promotional spam, so it is **not** evidence about its phishing recall.
**DERIVED:** a calibrated word+character model is the strongest supported
candidate for a future learned component, and its probability output supports
tiered warnings. **Not supported:** phishing performance, campaign-disjoint
generalization, per-language claims, or a deployment false-positive rate. The
1% ham-FPR operating point is a development design assumption, not a product
claim.

## Remaining unknowns

- download-time license and usage terms;
- collection consent and source independence;
- the semantic boundary between promotional spam, fraud, and phishing;
- true language labels for Latin and mixed-script messages;
- campaign, sender, author, annotator, and temporal metadata; and
- whether any measured baseline result transfers to tester-authentic Fisher
  phishing data.
