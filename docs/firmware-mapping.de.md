# Firmware-Mapping (Kurzüberblick)

Diese Seite ist eine verkürzte Übersetzung. Alle Details: englisches Original `docs/firmware-mapping.md`.

- Marlin
  - SD-Logging: `M928` (Start) / `M29` (Ende)
  - RGB via `M150`
  - Custom Pins: `M42 P<pin> S<val>`
- RepRapFirmware (RRF)
  - SD-Logging: `M929 P"datei" S1` (Stop: `M929 S0`)
  - Benannte Pins (`out1`, …), Lüfter `M106/M107 P`
- Klipper
  - `M240` ↔ `M118 TIMELAPSE_TAKE_FRAME` per Policy
  - Lüfter/LEDs oft als Makros
- GRBL / LinuxCNC
  - Absaugung (Kühlmittel): `M7/M8` an / `M9` aus

Siehe Original für gerätespezifische Hinweise (Licht, Kamera, Lüfter, Absaugung) und genaue Richtlinien.
