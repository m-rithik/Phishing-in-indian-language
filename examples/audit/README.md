# Synthetic audit-selector example

This directory contains only invented metadata for deterministic tool rehearsal.
There are no messages, people, organizations, routes, accounts, credentials, or
contact fields. The provenance values are simulated enum labels, not authenticity
claims.

Run:

```console
python3 -m fisher_audit rehearse \
  --attempts examples/audit/attempts.synthetic.jsonl \
  --seed-hex 000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f \
  --scope SYNTHETIC_REHEARSAL_ONLY \
  --format text
```

The expected status is `STRUCTURALLY_VALID`, with all 12 records selected under
`fallback_entire_universe: true`. The canonical protocol requires at least 1,200
attempts for 10% sampling, so this compact example deliberately rehearses the
full-universe fallback and reports that a revised real sampling rule would be
required. Regardless of exit status, the output remains
`SYNTHETIC_REHEARSAL_ONLY` and `release_blocked: true`.

Input rows use schema `1.0.0`. Output manifests use schema `1.1.0`; their hashed
envelopes and every selected entry bind the synthetic-only scope and blocked
release state.
