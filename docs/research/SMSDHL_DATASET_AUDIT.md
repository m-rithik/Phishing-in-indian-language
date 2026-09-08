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

## Remaining unknowns

- download-time license and usage terms;
- collection consent and source independence;
- the semantic boundary between promotional spam, fraud, and phishing;
- true language labels for Latin and mixed-script messages;
- campaign, sender, author, annotator, and temporal metadata; and
- whether any measured baseline result transfers to tester-authentic Fisher
  phishing data.
