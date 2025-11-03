# Mappage firmware (résumé)

Cette page est une traduction abrégée. Pour tous les détails, voir la version originale (anglais) : `docs/firmware-mapping.md`.

- Marlin
  - Journal SD : `M928` (début) / `M29` (fin)
  - RGB via `M150` (support LED requis)
  - Sorties personnalisées : `M42 P<broche> S<val>`
- RepRapFirmware (RRF)
  - Journal SD : `M929 P"fichier" S1` (arrêt : `M929 S0`)
  - Broches nommées (`out1`, etc.), ventilateurs `M106/M107 P`
- Klipper
  - `M240` ↔ `M118 TIMELAPSE_TAKE_FRAME` par politique
  - Utiliser macros pour ventilateurs/LEDs si nécessaire
- GRBL / LinuxCNC
  - Extraction (coolant) : `M7/M8` (on) / `M9` (off)

Voir l’original pour conseils par périphérique (lumières, caméra, ventilateurs, extraction) et politiques exactes.
