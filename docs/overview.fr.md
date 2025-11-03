# Aperçu d’OpenPrintKit

Note : version originale en anglais : `docs/overview.md`.

Cette page résume les concepts et l’interface d’OPK :

- PDL (Printer Description Language) = source de vérité.
- Onglets : Zone d’impression, Extrudeurs, Multi‑matériaux, Filaments, Fonctionnalités, Contrôle machine, Périphériques, G‑code, Journaux.
- Les hooks G‑code, macros et la carte des hooks déterminent où les commandes sont injectées.
- `machine_control` capture l’intention haut niveau ; les générateurs traduisent selon le firmware.
- Outils : Aperçu G‑code, Validation des variables, Référence M‑code.
  - Générer des extraits : crée des fichiers start/end G‑code prêts pour le firmware.
  - Générer des profils : produit des profils pour Orca, Cura, Prusa, ideaMaker, Bambu (avec Aperçu avant écriture).
- Paramètres : slicer/firmware par défaut, dossier de sortie, JSON de variables, politiques firmware.

Voir aussi : `docs/firmware-mapping.md`, `docs/mcode-reference.md`, `docs/cli-reference.md`.

Liens rapides :
- Manuel Utilisateur : `docs/user-manual.fr.md`
- Captures d’écran GUI : `docs/images/`

## Points clés de Paramètres
- Slicer/firmware par défaut — utilisé par les générateurs et l’UI.
- Dossier de sortie — chemin proposé pour les fichiers générés.
- Variables JSON — valeurs par défaut pour l’Aperçu G‑code.
- Modèles de variables — fichier optionnel de modèles nommés.
- Politique de reprise réseau — limites/recul/aléa pour les intégrations.
- Fichiers récents — nombre maximum mémorisé pour PDL/Vars.

## Cartographie PDL → Slicer (extraits)
- process_defaults.layer_height_mm → hauteur de couche
- process_defaults.first_layer_mm → première couche
- process_defaults.speeds_mms.{perimeter,infill,travel} → vitesses
- process_defaults.extrusion_multiplier → multiplicateur / débit matière
- process_defaults.cooling.{min_layer_time_s,fan_*} → refroidissement/ventilateurs
- limits.acceleration_max → accélération impression/déplacement
- limits.jerk_max → jerk (Cura)
- process_defaults.accelerations_mms2.{...} → accélération par section

## OpenPrintTag
Méta‑données injectées dans le start G‑code (bloc JSON `;BEGIN:OPENPRINTTAG`).

## Conseils spécifiques firmware
- RRF : M929 pour journal SD ; broches nommées prises en charge.
- Klipper : M240 ↔ `M118 TIMELAPSE_TAKE_FRAME` par défaut.
- GRBL : extraction = M8 (on) / M9 (off).
- LinuxCNC : extraction = M7 (on) / M9 (off).
