# Référence CLI OPK

Note : original anglais : `docs/cli-reference.md`.

## Table des matières
- Commandes
- Bases de données de bobines
- Substitutions avancées
- Astuces GUI

Commandes :
- `opk validate {chemins...}` — Valide les profils JSON via le schéma.
- `opk bundle --in SRC --out OUT.orca_printer` — Crée une archive Orca à partir de `printers/`, `filaments/`, `processes/`.
- `opk rules [--printer P] [--filament F] [--process S]` — Exécute les règles (erreurs/avertissements) avec résumé.
- `opk workspace init ROOT [--no-examples]` — Scaffolding d’un workspace standard.
- `opk install --src SRC --dest ORCA_PRESET_DIR [--backup BACKUP.zip] [--dry-run]` — Simulation et installation vers les presets d’Orca.
- `opk convert --from cura|prusa|superslicer|ideamaker --in IN --out OUTDIR` — Conversion vers profils OPK.
- `opk gcode-hooks --pdl PDL.yaml` — Liste les hooks disponibles après mappage firmware.
- `opk gcode-preview --pdl PDL.yaml --hook start --vars vars.json` — Rendu d’un hook avec variables.
- `opk gcode-validate --pdl PDL.yaml --vars vars.json` — Valide tous les hooks (placeholders non résolus).
- `opk pdl-validate --pdl PDL.yaml` — Valide schéma PDL + règles machine_control.
- `opk tag-preview --pdl PDL.yaml` — Affiche le bloc OpenPrintTag inséré au début.
- `opk gen-snippets --pdl PDL.yaml --out-dir OUT [--firmware FW]` — Génère fichiers `*_start.gcode` et `*_end.gcode`.
- `opk gen --pdl PDL.yaml --slicer orca|cura|prusa|ideamaker|bambu|superslicer|kisslicer --out OUTDIR [--bundle OUT]` — Génère des profils.
- `opk gui-screenshot --out OUTDIR [--targets ...]` — Capture des captures GUI hors‑écran.
- `opk slice --slicer slic3r|prusaslicer|superslicer|curaengine --model MODEL.stl --profile PROFILE.ini --out OUT.gcode [--flags "..."]` — Tranchage via CLI externe.
- `opk spool --source spoolman|tigertag|openspool|opentag3d --base-url URL --action create|read|update|delete|search [...]` — Opérations sur base de données de bobines.

### Bases de données de bobines
- Options communes : `--api-key`, `--id`, `--payload JSON`, `--query`, `--page`, `--page-size`, `--format items|normalized`, `--endpoints-file`, `--endpoints-json`.
- Politique de retry configurable via paramètres ou variables d’environnement (`OPK_NET_*`).

### Substitutions avancées
- `--bundle` — produit une archive (Orca : `.orca_printer`; autres : `.zip`).
- Accélérations (fusionnées dans `process_defaults.accelerations_mms2`) :
  - `--acc-perimeter N`, `--acc-infill N`, `--acc-external N`, `--acc-top N`, `--acc-bottom N`.

Voir aussi : `docs/overview.fr.md`, `docs/gcode-help.md`, `docs/firmware-mapping.md`.
