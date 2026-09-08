# Fisher synthetic E0 fixture

`synthetic_e0.json` is a reserved, synthetic-only known-answer input. It
contains no authentic message, live destination, secret, or trained-model
output. The rehearsal executes all four base cells and four controls, constructs
semantic artifacts only for base `C01` and `C11`, and validates two one-item
synthetic metric runs.

The fixture has one Romanized Hindi source span with two reserved synthetic
Devanagari readings. Their unequal synthetic logits produce two returned paths
with nonuniform `q`: `C00`/`C01` cells retain rank one, while `C10`/`C11` cells
retain both paths. Each of the five seed rows contains the full two-column
returned-path matrix; the harness slices rank-one cells and retains both columns
for all-path cells. This is an Indic/code-mix interface fixture, not a claim of
linguistic coverage or detection quality.

Run it with:

```console
python3 -m fisher_engine rehearse \
  --fixture examples/engine/synthetic_e0.json \
  --format text
```

`expected_summary.json` freezes the non-hash acceptance projection. Artifact
hashes intentionally bind the current exact engine source closure and therefore
change when executable source changes. The rehearsal proves deterministic
interfaces and arithmetic only; it is not a model, corpus, robustness, or
performance result. `G5` and `G6` remain blocked.
