# G-code Hooks & Macros

OPK organizes G-code into lifecycle hooks:

- Lifecycle: start, end, pause, resume, on_abort, power_loss_resume, auto_shutdown
- Layers: before_layer_change, layer_change, after_layer_change, top_layer_start, bottom_layer_start
- Tools/Filament: before_tool_change, tool_change, after_tool_change, filament_change
- Objects/Regions: before_object, after_object, before_region, after_region, support_interface_start, support_interface_end
- Motion: retraction, unretraction, travel_start, travel_end, bridge_start, bridge_end
- Temperature/Env: before_heating, after_heating, before_cooling
- Monitoring/Timelapse: on_progress_percent, on_layer_interval, on_time_interval, before_snapshot, after_snapshot

Use `gcode.macros` for named sequences and `gcode.hooks` (map) for arbitrary hook names.
Placeholders such as `{nozzle}`, `{bed}`, `{layer}` are supported; dotted/array paths (e.g., `{printer.name}`, `{filament_diameter[0]}`) are recognized in preview/validator.

See `docs/mcode-reference.md` for common M-codes.

