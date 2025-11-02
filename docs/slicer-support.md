# Slicer Support Matrix

This page summarizes import/export coverage and mapping depth per slicer.

- OrcaSlicer — Export (profiles + .orca_printer bundle); no import
- Cura — Import (JSON defs → OPK); Export (CFG)
- PrusaSlicer — Import (INI → OPK); Export (INI)
- SuperSlicer — Import (INI → OPK); Export (INI)
- ideaMaker — Import (CFG → OPK); Export (CFG)
- Bambu Studio — Export (INI‑style minimal)
- KISSlicer — Import (INI → OPK best‑effort); Export (INI best‑effort)
- CuraEngine — Slice via CLI (pass‑through flags)
- Slic3r/PrusaSlicer/SuperSlicer — Slice via CLI (load INI and export G‑code)

Mapping highlights (export)
- Geometry: bed shape (rect), Z height
- Extruder/material: nozzle_diameter, filament_diameter, temps (where available)
- Process defaults: layer heights; speeds (perimeter/infill/travel); external_perimeter/top/bottom (where supported)
- Cooling: min layer time; fan min/max/always on
- Acceleration/jerk: global and per‑section where supported
- G‑code: start/end hooks (rendered from PDL + machine_control)

Limitations
- Proprietary or binary formats (FlashPrint, QidiPrint, Craftware, Pathio, MatterControl, Kiri:Moto) are not supported directly; use snippet packs and documentation guidance instead.
- CuraEngine requires machine JSON and per‑setting flags; OPK `slice` passes flags through verbatim.

