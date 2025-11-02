# Guide Utilisateur OpenPrintKit (Brouillon)

Ceci est un point de départ en français. Voir `docs/user-manual.md` (anglais) pour la référence complète.

## Introduction

OpenPrintKit (OPK) permet de définir un PDL puis de générer des profils pour plusieurs slicers (Orca, Cura, Prusa/SuperSlicer, Bambu…), avec validations et règles.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Tâches fréquentes

- Valider: `opk validate ...`
- Règles: `opk rules --printer P --filament F --process S`
- Générer: `opk gen --pdl fichier.yaml --slicer orca --out outdir`
- Packager: `opk bundle --in src --out profil.orca_printer`
- Installer (Orca): `opk install --src src --dest chemin/presets`

## Interface graphique

Lancer: `opk-gui` — onglets pour zone d’impression, extrudeurs, matériaux, contrôle machine, périphériques, G‑code, etc.

---

Contributions bienvenues pour compléter/traduire ce guide.
