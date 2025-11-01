# Firmware Mapping Guide

This guide explains how structured `machine_control` fields are translated into G-code hooks per firmware.

## Marlin (default)

- PSU: `M80` at start, `M81` at end.
- Lights: `M355 S1`/`M355 S0`; RGB with `M150 R/U/B`.
- Fans: `M106 S..` (part), `M106 P.. S..` (aux), `M107` at end.
- Chamber: `M141 S..` and optional `M191 S..`.
- SD logging: `M928 <file>`, end: `M29`.
- Camera: `M240` (or custom `camera.command`).
- Exhaust: `M42 P<pin> S..` or `M106 P.. S..`; off: `M42 .. S0` or `M107 P..`.
- Aux outputs: `M42 P<pin> S..` start/end values.
- Custom peripherals: sequences inserted into specified hooks.

## RepRapFirmware (RRF / Duet)

- SD logging mapped to `M929 P"<file>" S1` (start) and `M929 S0` (stop).
- Camera: `M240` if configured or use `camera.command`/`M42` on named pins (use `pin: "outName"`).
- Fans/exhaust: prefer `M106 Pn S..` and `M107 Pn`.
- Outputs: `M42 P"outName" S..` or numeric pin; consider M950 device creation in firmware config.
- Other codes pass through.

## Klipper

- Camera: `M240` mapped to `M118 TIMELAPSE_TAKE_FRAME` by default; override with `camera.command`.
- Fans/lights/exhaust: pass-through (or map to SET_* via custom macros if desired).

## GRBL

- Exhaust: `M8` (flood coolant) at start; `M9` at end.
- Other outputs: use Custom Peripherals (hooked M-codes) as needed.

## LinuxCNC

- Exhaust: `M7` (mist) at start; `M9` at end.
- Other outputs: `M62`/`M63` (digital output) via Custom Peripherals, or map LEDs/fans to your HAL setup.

## Smoothieware / Repetier

- Use Marlin-like mappings; adjust with Custom Peripherals when needed.

