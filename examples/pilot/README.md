# Synthetic pilot-contract example

Every record here is invented and reserved for documentation. It contains no real
message, person, organization, account, destination, route, or contact detail.
Every annotation independently covers the complete machine lexical-token
inventory. The four-item draft is intentionally not the final 1,200-item pilot.

Validate it from the repository root:

```console
python3 -m fisher_data validate \
  --sources examples/pilot/sources.jsonl \
  --items examples/pilot/items.jsonl \
  --annotations examples/pilot/annotations.jsonl \
  --registry-manifest examples/pilot/registry_manifest.jsonl \
  --registry-references examples/pilot/registry_references.jsonl \
  --mode draft --format text
```

The expected outcome is `VALID` with three intentional draft-completeness warnings:
`pilot_item_count`, `pilot_stratum_balance`, and `pilot_label_balance`. All records
use schema version `1.2.0`; this four-item example is not a pilot-final dataset.
Each item uses exact `[DOMAIN]` text plus one matching non-gold
`TYPED_PLACEHOLDER` inventory entry and a canonical `vmp_sha256`. Blind and
final annotations contain only visible-message human gold; their explicit
destination spans are bound to, but do not copy or create, the item inventory. The four
separate registry-reference rows are non-gold `UNKNOWN` results with missing
coverage, created by the distinct synthetic registry reviewer after the named
final annotations. Their approved manifest is illustrative metadata, not proof
that a real registry, approval, reviewer, or blinding process exists.
