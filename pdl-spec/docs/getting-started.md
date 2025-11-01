# Getting Started Authoring a PDL

This short guide walks you from a blank file to a validated PDL.

1) Create `my_printer.yaml` from the minimal template:

```yaml
pdl_version: 1.0.0
id: vendor.model
name: Vendor Model
firmware: marlin
kinematics: cartesian
geometry:
  bed_shape: [[0,0],[220,0],[220,220],[0,220]]
  z_height: 250
```

2) Validate against the schema:

```bash
python -m jsonschema -i my_printer.yaml pdl-spec/docs/schema/pdl.schema.json
```

3) Explore examples:

- Minimal: examples/minimal.yaml
- Full: examples/full_lk5pro.yaml

For the complete specification, see PDL_SPEC.md.
