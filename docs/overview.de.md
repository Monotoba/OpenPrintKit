# OpenPrintKit Überblick

Hinweis: englisches Original: `docs/overview.md`.

Diese Seite fasst Konzepte und UI zusammen:

- PDL (Printer Description Language) ist die maßgebliche Quelle.
- Tabs: Bauraum, Extruder, Multimaterial, Filamente, Funktionen, Maschinensteuerung, Peripherie, G‑code, Logs.
- G‑code‑Hooks, Makros und Hook‑Mapping steuern, wo Kommandos eingefügt werden.
- `machine_control` beschreibt Absicht auf hoher Ebene; Generatoren übersetzen pro Firmware.
- Werkzeuge: G‑code‑Vorschau, Variablenprüfung, M‑Code‑Referenz.
  - Snippets generieren: Start/End‑G‑code für Firmware erzeugen.
  - Profile generieren: Profile für Orca, Cura, Prusa, ideaMaker, Bambu (mit Vorschau vor dem Schreiben).
- Einstellungen: Standard‑Slicer/Firmware, Ausgabepfad, Variablen‑JSON, Firmware‑Richtlinien.

Siehe auch: `docs/firmware-mapping.md`, `docs/mcode-reference.md`, `docs/cli-reference.md`.

Schnellzugriff:
- Benutzerhandbuch: `docs/user-manual.de.md`
- GUI‑Screenshots: `docs/images/`

## Wichtige Einstellungen
- Standard‑Slicer/Firmware — für Generatoren und UI.
- Ausgabeverzeichnis — vorgeschlagener Pfad für generierte Dateien.
- Variablen‑JSON — Standardwerte für die G‑code‑Vorschau.
- Variablen‑Vorlagen — optionales Datei mit benannten Vorlagen.
- Netzwerk‑Retry — Limit/Backoff/Jitter für Integrationen.
- Zuletzt benutzt — Maximalzahl gemerkter PDL/Vars‑Einträge.

## PDL → Slicer Mapping (Auszüge)
- process_defaults.layer_height_mm → Schichthöhe
- process_defaults.first_layer_mm → erste Schicht
- process_defaults.speeds_mms.{perimeter,infill,travel} → Geschwindigkeiten
- process_defaults.extrusion_multiplier → Extrusionsfaktor/Flow
- process_defaults.cooling.{min_layer_time_s,fan_*} → Kühlung/Lüfter
- limits.acceleration_max → Beschleunigung (Druck/Reise)
- limits.jerk_max → Jerk (Cura)
- process_defaults.accelerations_mms2.{...} → Bereichs‑Beschleunigungen

## OpenPrintTag
Metadaten im Start‑G‑code (`;BEGIN:OPENPRINTTAG` mit JSON).

## Firmware‑Tipps
- RRF: M929 für SD‑Logging; benannte Pins möglich.
- Klipper: M240 ↔ `M118 TIMELAPSE_TAKE_FRAME` standardmäßig.
- GRBL: Absaugung = M8 (an) / M9 (aus).
- LinuxCNC: Absaugung = M7 (an) / M9 (aus).
