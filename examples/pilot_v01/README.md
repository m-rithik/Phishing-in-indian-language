# Fisher pilot v0.1.0 synthetic rehearsal

These records are entirely synthetic, reserved examples. They are not authentic phishing
messages, tester research data, or evidence of model performance. They exercise the draft
validator only and intentionally produce readiness warnings because the fixture is not the
240-item feasibility pilot.

Run from the repository root:

```bash
python -m fisher_pilot validate \
  --sources examples/pilot_v01/sources.jsonl \
  --items examples/pilot_v01/items.jsonl \
  --annotations examples/pilot_v01/annotations.jsonl \
  --mode draft --format text
```

Expected process result: `VALID` with readiness warnings. No model is trained or evaluated.
