# Fisher governance validator example

`source_ledger.blocked.jsonl` is a single fictional, schema-only source record.
It contains no participant, real message, credential, contact route, collected
artifact, or approval. Its only domain-like literal uses the reserved `.example`
suffix.

Run:

```console
python3 -m fisher_governance validate \
  --ledger examples/governance/source_ledger.blocked.jsonl \
  --format text
```

Expected outcome: the record is mechanically well formed, but collection is
`BLOCKED` and the command exits `1`. This is the correct result; the fixture is
not an authorized data source. The report also lists explicit `UNKNOWN` human
gates, including evidence truth, reviewer authority, provenance/lineage truth,
hash binding, opaque-ID privacy, and LLM material-edit evidence. That list makes
known limits visible and is not asserted to exhaust every human or legal gate.
