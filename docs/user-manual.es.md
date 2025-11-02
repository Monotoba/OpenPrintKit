# Manual de Usuario de OpenPrintKit

Este documento resume cómo instalar, usar y solucionar problemas con OpenPrintKit (OPK). Para referencias completas, consulte la versión en inglés (`docs/user-manual.md`).

## Introducción

OPK permite definir una vez (PDL) y generar perfiles para varios slicers (Orca, Cura, Prusa/SuperSlicer, Bambu, etc.), con validaciones y reglas de buenas prácticas.

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Conceptos clave

- Perfiles: `printer`, `filament`, `process` (JSON).
- PDL: modelo JSON/YAML; los generadores crean perfiles de slicer.
- Reglas: advertencias/errores independientes del esquema.
- Paquetes: `.orca_printer` (Orca) o `.zip` para otros.

## CLI (tareas comunes)

- Validar perfiles:
  ```bash
  opk validate path/a/*.json
  ```
- Reglas entre perfiles:
  ```bash
  opk rules --printer P.json --filament F.json --process S.json
  ```
- Generar desde PDL:
  ```bash
  opk gen --pdl mi_printer.yaml --slicer orca --out ./out [--bundle perf.orca_printer]
  ```
- Convertir desde otros formatos:
  ```bash
  opk convert --from cura --in CURA_DIR --out OUTDIR
  ```
- Instalar en presets de Orca (con copia de seguridad):
  ```bash
  opk install --src ./perfiles --dest ~/.../OrcaSlicer/.../presets --backup backup.zip
  ```

## Herramientas de G‑code

- Listar hooks: `opk gcode-hooks --pdl archivo.yaml`
- Previsualizar un hook: `opk gcode-preview --pdl archivo.yaml --hook start --vars vars.json`
- Validar variables: `opk gcode-validate --pdl archivo.yaml --vars vars.json`

## Bases de bobinas (Spool)

Operaciones básicas contra Spoolman/TigerTag/OpenSpool:
```bash
opk spool --source spoolman --base-url http://host --action search --query PLA --format items
opk spool --source tigertag --base-url https://api --action read --id 123 --format normalized
```
Paginación y overrides de endpoints: `--page`, `--page-size`, `--endpoints-json`, `--endpoints-file`.
Reintentos configurables: `OPK_NET_RETRY_LIMIT` (por defecto 5), backoff/jitter (`OPK_NET_RETRY_BACKOFF`, `OPK_NET_RETRY_JITTER`).

## Interfaz gráfica (OPK Studio)

Ejecutar: `opk-gui`

Pestañas: Área de impresión, Extrusores, Multi‑Material, Filamentos, Funciones, Control de Máquina, Periféricos, G‑code, OpenPrintTag, Problemas.

- Botón “Check…” en varias pestañas para ejecutar reglas y resaltar problemas.
- Filtros en pestaña Problemas (nivel y texto).
- Iconos de ayuda en campos (colocar el puntero para ver consejos).

## Consejos por firmware (resumen)

- Marlin: `M928`/`M29` para logging; RGB con `M150`; `M42` usa pines numéricos.
- RRF: `M929` para logging; pines con nombre (`out1`); fans `M106/M107 P`.
- Klipper: `M240` → `M118 TIMELAPSE_TAKE_FRAME`; fans vía macros.
- GRBL/LinuxCNC: extractor como coolant `M7/M8/M9`; fans no estándar.

## Solución de problemas

- Error de esquema: `opk validate` y revisar mensaje.
- Muchas advertencias: abrir GUI y usar “Check…”.
- Ruta de presets Orca: varía por SO y versión (usar `--dry-run`).
- Slicers externos: binarios en `PATH`.
- Red (spool): ajustar reintentos/backoff/jitter en Preferencias o variables de entorno.
