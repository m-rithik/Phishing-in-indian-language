# Fisher

Fisher v0.6 is a local message and link checking toolkit: a Chrome/Edge
extension, a shared analysis engine, and a command-line companion. Paste a
message, inspect a link without opening it, or explicitly analyze selected page
text. Results explain the detected patterns and suggest what to do next.

## Try it

1. Open `chrome://extensions` or `edge://extensions`, enable **Developer mode**,
   and **Load unpacked** from the `browser_extension` folder.
2. Open Fisher. Choose **Message** or **Link check**, paste an input, and analyze.
   You can also select page text and use the explicit selection button.
3. Use the same engine from a terminal (Node.js 22+):

   ```console
   node fisher.mjs analyze --format json < /path/to/message.txt
   node fisher.mjs analyze --mode url < /path/to/link.txt
   node fisher.mjs batch --format json < /path/to/messages-one-per-line.txt
   ```

The extension runs offline with no account, server, telemetry, or message
history. Link inspection examines syntax only; it does not visit the address
or check its reputation. These are transparent pattern checks with known blind
spots, not measured phishing predictions. A result without a match does not
establish safety.

For more room, choose **Open a roomy workspace** in the popup. The expanded view
adds side-by-side input and findings, follows your system's light/dark appearance,
and includes synthetic Hindi, Tamil, Telugu, and everyday-message examples.
**Save report** downloads generic findings as JSON without your submitted text or
link addresses. Each workspace starts with an empty draft; page selection stays
in the toolbar popup.

**Bulk check** accepts pasted inputs or a local UTF-8 `.txt` file, one message or
link per line. Review up to 100 inputs, filter by result, inspect individual line
findings, cancel an active run, and download a report excluding source text.
Link checks also inspect immediate destinations embedded in common navigation
query fields, reporting structural cues without opening or following any URL.

See the [extension and local-tool guide](browser_extension/README.md) for
keyboard shortcuts, limits, installation, and testing.

The ZIP packager was removed in October 2026. Load the `browser_extension`
folder unpacked. The
[11 October 2026 verification record](docs/research/EXECUTION_STATUS.md#current-local-product-snapshot--11-october-2026)
describes the earlier v0.5.0 package.

## Research context

Fisher is a text-only NLP research project for phishing detection in Hindi,
Tamil, Telugu, and English–Indic code-mixed messages. Its immediate proposed
contribution is uncertainty-aware transliteration: preserve multiple plausible
interpretations of Romanized Indic text and aggregate their phishing
predictions instead of committing to one normalization. Structured endpoint
reasoning is a later hypothesis, not part of the current build.

> Current status: the auxiliary spam/ham baseline and nested development model
> selection, local Fisher pilot v0.1.0 readiness validator, and an explicit-action
> browser-extension prototype are implemented and reproducible. No authentic
> Fisher phishing corpus has been collected, and no phishing performance result
> has been measured. The workbook experiments are pipeline checks; the nested
> run did not create a deployable model, and the extension still uses transparent
> rules rather than a trained Fisher phishing model.

The immediate research question is deliberately narrower: **among messages that
contain Romanized Indic text, does aggregating predictions over multiple
transliteration candidates outperform using only the top candidate on a
campaign/source-disjoint test set?**

## Current research priority

1. Resolve storage, consent, withdrawal, retention, and reviewer ownership, then
   obtain a safely defanged, consented **240-message feasibility pilot**: four
   language strata × two labels × 30 messages.
2. Validate provenance, Romanized-Indic coverage, annotation agreement,
   duplicates, component concentration, and campaign/source groups with the
   pilot v0.1.0 tool. This pilot is for data readiness, not paper metrics.
3. Run two lexical baselines first: character TF-IDF logistic regression and a
   word+character TF-IDF linear SVM.
4. Compare top-1 transliteration with multi-candidate aggregation using the same
   classifier. Add one multilingual encoder only after the data and local ML
   environment are ready.
5. Expand toward a preliminary paper corpus only if the pilot contains enough
   authentic transliteration ambiguity and the simple comparison shows a
   reproducible signal.

Public spam/ham datasets may be used only for development or external analysis
after license, privacy, duplication, and leakage checks. Their labels must not be
treated as phishing ground truth without Fisher-specific reannotation.

Voice, conversations, the offline registry, the full semantic factorial, patent claims, a 1% false-positive claim,
and the 6,000-message confirmatory design are deferred from the immediate path.

## Browser extension and shared engine

`browser_extension/` is a Manifest V3 Chrome/Edge prototype. It requests only
`activeTab` and `scripting`, declares no host permissions, content scripts or
background worker, and reads page text only when the user selects it and presses
**Selection mode**. The popup checks pasted messages, links, and explicitly
selected text with the shared engine. There is no network, telemetry, or storage
API. Its four popup results are **High-risk patterns found**, **Worth a closer
look**, **No clear pattern match**, and **Could not analyze**. No-match is
explicitly not a safety result.

The v0.6 shared engine performs bounded structural link inspection for embedded
credentials, IP addresses, internationalized hosts, unusual ports, defanged
spelling, and other review cues. It does not decide whether a domain is genuine.
The CLI emits generic reports or aggregate batch counts, without echoing input
text, hosts, or URL parameters. Its English and constructed Indic-language
rules have not been validated for accuracy or language coverage.

## Fisher pilot readiness validator

The new `fisher_pilot` package validates three restricted JSONL inputs: sources,
deidentified and defanged items, and blind/adjudication annotations. Draft mode
supports small structural rehearsals. Ready mode enforces the fixed 240-item
allocation, known-language and label agreement, source/consent/batch containment,
duplicate and template controls, component diversity and concentration, and a
deterministic whole-component three-fold allocation dry run.

Run the tracked synthetic rehearsal with:

```console
uv run python -m fisher_pilot validate \
  --sources examples/pilot_v01/sources.jsonl \
  --items examples/pilot_v01/items.jsonl \
  --annotations examples/pilot_v01/annotations.jsonl \
  --mode draft --format text
```

The example is invented and intentionally incomplete; it should be `VALID` with
readiness warnings. Never replace it with tester data. Real inputs require an
approved restricted store and remain unauthorized until the project resolves
the named governance decisions. See the [pilot v0.1.0 contract](docs/research/PILOT_V01.md).

## Working auxiliary baseline

The user-supplied Dravidian spam/ham workbook has now been processed through a
small, real NLP pipeline. It validates the mechanics we need next: bounded XLSX
ingestion, conservative label handling, duplicate and template grouping,
in-memory route defanging, grouped cross-validation, and aggregate-only result
artifacts.

The controlled projection contains 6,433 unique development messages: 5,328 ham
and 1,105 spam. Twenty-eight contaminated label groups, 1,201 same-label
duplicates, and 23 residual contact/route candidates are excluded. The workbook
itself remains outside Git.

Set up and run the pipeline with:

```console
uv sync
uv run python -m fisher_baselines audit \
  --workbook "/path/to/Spam Message Collection (1).xlsx" \
  --output outputs/smsdhl_dravidian/audit.json
uv run python -m fisher_baselines evaluate \
  --workbook "/path/to/Spam Message Collection (1).xlsx" \
  --output-dir outputs/smsdhl_dravidian/run_seed_1729 \
  --seed 1729 --folds 3
mkdir -p outputs/smsdhl_dravidian
uv run python -m fisher_baselines nested-evaluate \
  --workbook "/path/to/Spam Message Collection (1).xlsx" \
  --output outputs/smsdhl_dravidian/nested_seed_1729.json \
  --seed 1729 --outer-folds 3 --inner-folds 3
```

The evaluation directory must be absent or empty. It receives only three
aggregate JSON files: `audit.json`, `run_manifest.json`, and `metrics.json`. No
message text, row-level predictions, source path, or hyperlink target is
persisted. The nested command requires its safe output parent to exist and its
output filename to be unoccupied. It publishes one aggregate JSON file and no
model, vocabulary, predictions, source path, or sheet name.

Measured three-fold, template-grouped out-of-fold results at each classifier's
default decision threshold are:

| Model | Spam precision | Spam recall | Spam F1 | Macro F1 | FP | FN |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Character TF-IDF + logistic regression | 0.9209 | 0.8950 | 0.9078 | 0.9445 | 85 | 116 |
| Word + character TF-IDF + linear SVM | 0.9568 | 0.8824 | 0.9181 | 0.9509 | 44 | 130 |

The auxiliary v0.2 nested run used three outer and three inner
template-group-disjoint folds to select among eight fixed candidates. It chose
character linear SVM with `C=1` in outer folds 0 and 1 and word+character linear
SVM with `C=1` in fold 2. The resulting mean spam F1 was `0.923204619`, compared
with `0.918090119` for the frozen word+character `C=1` comparator. The
`0.005114500` improvement was below the predeclared `0.01` acceptance threshold,
so the acceptance decision was **false**. This is promising but inconclusive
auxiliary spam/ham development evidence, not a selected production model.

The v0.3 held-out comparison (`holdout-evaluate`) scores a group-disjoint
20% test partition once, after development-only Platt calibration, 1% ham-FPR
threshold selection, and model selection. The selected calibrated word+character
linear SVM reached spam F1 0.9358 (recall 0.9231, ham FPR 0.0103). Character LR
reached 0.9104. The shipped rule engine reached 0.1266 (recall 0.0679) on this
spam/ham data, which it was not designed to detect. NFKC + format-control
normalization was needed: without it, inserting zero-width joiners dropped the
lexical model's recall to zero. See the
[workbook audit](docs/research/SMSDHL_DATASET_AUDIT.md#held-out-comparison-v03-rules-versus-calibrated-lexical-models).

```console
uv run python -m fisher_baselines holdout-evaluate \
  --workbook "/path/to/Spam Message Collection (1).xlsx" \
  --output outputs/smsdhl_dravidian/holdout_seed_1729.json --seed 1729
```

These are development-only spam/ham measurements on one corpus. The split has
zero detected outer or inner template-group crossings, but the workbook lacks
campaign, sender, source, and reliable language metadata. All classifiers used
their default decision thresholds; no threshold tuning or calibration was
performed. The results therefore do not support phishing, per-language,
campaign-disjoint, calibrated-risk, low-FPR, or deployment claims. See the
[workbook audit](docs/research/SMSDHL_DATASET_AUDIT.md) for the exact evidence
boundary.

## Project layout

- `fisher_baselines/data.py` performs bounded workbook ingestion, conservative
  cleaning, in-memory defanging, duplicate control, and template grouping.
- `fisher_baselines/evaluation.py` runs the two grouped out-of-fold baselines and
  writes aggregate-only artifacts.
- `fisher_baselines/selection.py` runs the fixed nested grouped candidate
  selection and safely publishes one aggregate-only JSON artifact.
- `fisher_baselines/holdout.py` compares the shipped rule engine with calibrated
  lexical models on a held-out grouped partition, including robustness,
  bootstrap, slice, and cost measurements.
- `fisher_baselines/cli.py` exposes the `audit`, `evaluate`, `nested-evaluate`,
  and `holdout-evaluate` commands.
- `fisher_pilot/validator.py` validates the local 240-message feasibility-pilot
  contract and emits aggregate-only readiness reports.
- `fisher_pilot/cli.py` exposes the `draft` and `ready` validation modes.
- `browser_extension/` contains the explicit-action paste/selected-text browser
  interface, shared message/link analysis, and dependency-free unit tests.
- `fisher.mjs` runs that same engine on stdin; batch mode returns counts only,
  and batch-detail returns per-line JSON. Both batch and batch-detail exit 1 if
  any line cannot be analyzed.
- `tests/test_baseline_pipeline.py` covers schema, privacy, Unicode grouping,
  residual routes, leakage, deterministic folds, output safety, and CLI errors.
- `tests/test_baseline_selection.py` covers nested split isolation, candidate
  selection, deterministic aggregate-only output, and safe publication errors.
- `tests/test_pilot_validator.py` covers consent/provenance fields, annotation
  resolution, Unicode and credential safety, source/component containment,
  readiness arithmetic, agreement gates, and grouped allocation.
- [Workbook audit](docs/research/SMSDHL_DATASET_AUDIT.md) records the measured
  evidence and its limits.
- [Pilot v0.1.0 contract](docs/research/PILOT_V01.md) records the exact local
  schema, readiness gates, privacy boundary, and unverified human controls.
- [Change and decision log](docs/CHANGE_DECISION_LOG.md) records significant
  decisions, alternatives, verification, risks, and future commit references.

## Development

Python 3.11 or newer and [uv](https://docs.astral.sh/uv/) run the research
tools. Node.js 22+ runs the companion CLI and unit tests. Browser
testing uses development-only Playwright and axe dependencies:

```console
uv sync
npm ci
uv run python -m unittest discover -v -s tests -p 'test_*.py'
npm test
npx playwright install chromium
npm run test:browser
```

`uv build` produces two deliberately different artifacts. The source archive
contains the current Python packages, browser-extension and Node sources,
tests, examples, and linked Markdown documentation needed to inspect
and reproduce the repository product. The wheel installs only
`fisher_baselines` and `fisher_pilot`; it does not install the extension, Node
CLI, or synthetic research-engine packages.

The source workbook, virtual environment, raw/processed data, model artifacts,
and generated outputs are ignored by Git.

## Evaluation

The rule detector and an experimental transliteration step can be measured on
your own labelled messages. No real evaluation data ships with the repository:
`eval/messages.template.jsonl` holds 8 illustrative **synthetic** lines. Copy
it to `eval/messages.jsonl` and replace it with your data (target: 30 scam and
30 benign messages per language). The format and the rules for honest
`source` labels are in [`eval/README.md`](eval/README.md); `eval/load.py`
validates the file and rejects duplicate ids and duplicate text.

```console
cp eval/messages.template.jsonl eval/messages.jsonl   # then edit
npm run eval:rules
uv run python scripts/translit_experiment.py
```

- `npm run eval:rules` runs the shared engine on every message and reports
  TP, FP, TN, FN, precision, recall, F1 and the false-positive rate on benign
  messages, overall, per language and per script, for two settings (positive =
  high or review; positive = high only). It writes
  `eval/results/rules_metrics.json` and `eval/results/rules_errors.jsonl`
  (every false positive and false negative with its reasons).
- `scripts/translit_experiment.py` uses only `romanized` items. It compares the
  raw text (A), the text plus its top-1 transliteration (B), and the text plus
  5 transliteration variants aggregated by "any positive" (C-max) or by summed
  variant weight >= 0.5 (C-weighted). It writes
  `eval/results/translit_metrics.json` (per condition and language, plus exact
  McNemar tests for A vs B, B vs C-max and B vs C-weighted) and
  `eval/results/translit_examples.jsonl` (up to 20 items where the conditions
  disagree). The detector runs through `node fisher.mjs batch-detail`, which
  prints one JSON result per input line (batch checks are limited to 500 lines
  per call, so larger sets are sent in chunks).

The full Python test suite is designed for Linux/WSL; filesystem tests requiring POSIX features (such as `os.mkfifo` and deterministic archive packaging) are skipped on Windows.

### Evaluation limitations

- The detector is rule-based (keyword and pattern signals), not a trained model.
- The transliteration experiment uses an **oracle language ID**: each item's
  `language` field picks the target script. A real system must detect the
  language first, so those results are optimistic.
- Evaluation data is small or synthetic, so metrics (and p-values) describe
  that data only. This project makes **no claim of real-world accuracy**.
## Research boundary and next iteration

The implemented baseline and pilot validator establish a reproducible technical
starting point. The next scientifically meaningful milestone is an authorized,
provenance-recorded, human-reviewed Fisher dataset containing real phishing and
benign messages with source or campaign groups. Only after the pilot passes and
contains sufficient Romanized-Indic evidence should the project compare top-1
versus multi-candidate transliteration using the same classifier and a
component-disjoint split.

Before that collection, the project still needs confirmed source terms,
consent/storage ownership, deidentification rules, and a documented withdrawal
process. Do not visit message links, publish raw messages, or reinterpret this
workbook's spam labels as phishing labels.

The [Collection-to-Quarantine packet](docs/research/PILOT_COLLECTION_PACKET.md)
is the operational SG1 boundary and remains `BLOCKED`; it does not permit real
recruitment, submission, or storage without authentic dated external sign-off.

Commits, pushes, preprints, public demos, and releases require the approvals
recorded in the project governance policy.

## License and visibility

No reuse license has been selected. This first iteration is intended for the
owner's private GitHub repository; keep it private until the owner chooses
license terms and completes the recorded publication and IP review.
