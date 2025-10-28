# Contributing to PDL

1. Validate your PDL with the JSON Schema (`docs/schema/pdl.schema.json`).
2. Include a minimal and a full example for each printer addition.
3. Keep units explicit; prefer SI units.
4. Follow SemVer for `pdl_version`.

## Validation (CLI)
```bash
python -m jsonschema -i docs/examples/full_lk5pro.yaml docs/schema/pdl.schema.json
