# Machine-Control M-Codes Reference

This reference groups common M-codes by function and notes typical support in popular firmwares (Marlin, RepRapFirmware/RRF, Klipper via macros, and general CNC).

Note: Klipper implements most functions through macros and [output_pin]; equivalent behavior is generally achievable.

## Power & System Control

- M80 — Turn PSU ON (ATX) — Marlin, RRF
- M81 — Turn PSU OFF (ATX) — Marlin, RRF
- M999 — Restart/reset firmware — Marlin, RRF
- M108 — Cancel wait (override heat wait) — Marlin
- M112 — Emergency stop — Marlin, RRF, Klipper
- M0/M1 — Program stop/optional stop — Marlin, RRF, CNC
- M18/M84 — Disable steppers — Marlin, RRF

## Lighting, IO, and Peripherals

- M42 Pnn Snnn — Set output pin value — Marlin, RRF
- M43 — Report/test pin state — Marlin
- M355 S0/S1 — Case light off/on — Marlin
- M150 — RGB LED color — Marlin
- M380/M381 — Solenoid/relay open/close — Marlin, RRF
- M710/M711 — Auxiliary device on/off — Marlin (CNC mode)

## Cooling Fans and Auxiliary Outputs

- M106 Snnn Pn — Set fan speed — Marlin, RRF
- M107 — Fan off — Marlin, RRF
- M141 — Set chamber temperature — Marlin, RRF
- M191 — Wait for chamber temperature — Marlin, RRF
- M42 (raw pin control) — Can drive fans/outputs — Marlin, RRF

## Filament / Extruder & Servo Control

- M280 Pn Snnn — Servo to angle — Marlin
- M282 Pn — Detach servo — Marlin
- M300 Snnn Pnnn — Beep/buzzer — Marlin
- M600 — Filament change — Marlin, RRF
- M701/M702 — Load/unload filament — RRF, Marlin variants
- M125 — Pause and park — Marlin, RRF

## Probe, Endstop & Sensors

- M119 — Report endstop status — Marlin, RRF
- M420 S1 — Enable mesh bed leveling — Marlin
- M851 Zn.nn — Set Z-probe offset — Marlin
- M401/M402 — Deploy/retract probe — Marlin
- M48 — Probe repeatability test — Marlin

## Communications & Networking

- M115 — Report firmware version — All
- M117 — Display LCD message — Marlin
- M118 — Host message — Marlin, RRF
- M999 — Restart after stop — Marlin, RRF
- M21/M22 — Mount/unmount SD card — Marlin, RRF
- M928 — Start SD log — Marlin
- M29 — Stop SD log — Marlin

## Camera and External Triggering

- M240 — Trigger camera — Marlin, RRF
- M42 S255 — Alternate trigger via pin — Marlin, RRF
- M118 — Host message to trigger capture — Marlin, RRF, Klipper
- Custom macros (e.g., TIMELAPSE_TAKE_FRAME) — Host-side/Klipper

## Heater & Safety Control

- M140/M190 — Set bed temp (no-wait/wait) — All
- M104/M109 — Set extruder temp (no-wait/wait) — All
- M141/M191 — Set/wait chamber temp — Marlin, RRF
- M144 — Idle bed — Marlin
- M303 — PID autotune — Marlin, RRF
- M108 — Cancel wait — Marlin

## Diagnostics & Maintenance

- M122 — Firmware diagnostic dump — Marlin, RRF
- M503 — Print current settings — Marlin, RRF
- M500/M501/M502 — Save/load/reset EEPROM — Marlin, RRF
- M105 — Report temperatures — All
- M42/M43 — GPIO diagnostics — Marlin

## Firmware Notes

- Marlin: Broad M-code set; pins, LEDs, relays, camera triggers.
- Klipper: Use [output_pin] and [gcode_macro] to emulate most functions.
- RepRapFirmware (Duet): Structured device creation (e.g., M950), lights (M150), case light (M355).
- Smoothieware: Subset similar to Marlin.

## Summary by Category

- Power: M80, M81, M18, M84 — PSU/steppers
- Lighting: M150, M355, M42 — LEDs/lights
- Fans: M106, M107 — Cooling
- Camera: M240, M42 — Trigger/relay
- Servo/Probe: M280, M401, M402 — Deploy/move
- Messages: M117, M118 — LCD/host
- Diagnostics: M122, M503, M500 — Diagnostics/store
- Safety: M112, M999 — Stop/reset

