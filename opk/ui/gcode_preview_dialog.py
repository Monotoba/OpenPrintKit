from __future__ import annotations
import json
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QTextEdit, QFileDialog
)
from PySide6.QtCore import Qt, QSettings
import yaml
from ..core.gcode import list_hooks, render_sequence, find_placeholders


class GcodePreviewDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("G-code Preview")
        self._pdl_path: Path | None = None
        self._gcode: dict = {}
        self.s = QSettings("OpenPrintKit", "OPKStudio")
        self._build_ui()
        self._restore_state()

    def _build_ui(self):
        lay = QVBoxLayout(self)

        # File picker
        row = QHBoxLayout()
        self._file_label = QLabel("No PDL loaded")
        btn_open = QPushButton("Open PDL…"); btn_open.setShortcut("Ctrl+O")
        btn_open.clicked.connect(self._open_pdl)
        # Recent PDLs
        row.addWidget(self._file_label, 1)
        row.addWidget(QLabel("Recent:"))
        self._recent_pdls = QComboBox(); self._recent_pdls.setEditable(False)
        try:
            self._recent_pdls.activated.connect(self._choose_recent_pdl)
        except Exception:
            pass
        row.addWidget(self._recent_pdls)
        clr_p = QPushButton("Clear"); clr_p.setToolTip("Clear recent PDLs"); clr_p.clicked.connect(lambda: self._clear_recents("gcode_preview/recent_pdls"))
        row.addWidget(clr_p)
        row.addWidget(btn_open)
        lay.addLayout(row)

        # Hook selector
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Hook:"))
        self._hook = QComboBox()
        try:
            # Persist selection changes
            self._hook.currentTextChanged.connect(lambda t: self._persist_hook(t))
        except Exception:
            pass
        row2.addWidget(self._hook, 1)
        lay.addLayout(row2)

        # Vars editor
        lay.addWidget(QLabel("Variables (JSON):"))
        # Vars controls (Load/Save)
        vr = QHBoxLayout()
        self._btn_load_vars = QPushButton("Load Vars…"); self._btn_load_vars.setShortcut("Ctrl+L"); self._btn_load_vars.clicked.connect(self._load_vars_file)
        self._btn_save_vars = QPushButton("Save Vars As…"); self._btn_save_vars.setShortcut("Ctrl+S"); self._btn_save_vars.clicked.connect(self._save_vars_file)
        self._btn_tpl_vars = QPushButton("Insert Template…"); self._btn_tpl_vars.setShortcut("Ctrl+T"); self._btn_tpl_vars.clicked.connect(self._insert_vars_template)
        vr.addWidget(self._btn_load_vars); vr.addWidget(self._btn_save_vars); vr.addWidget(self._btn_tpl_vars)
        # Recent vars
        vr.addWidget(QLabel("Recent:"))
        self._recent_vars = QComboBox(); self._recent_vars.setEditable(False)
        try:
            self._recent_vars.activated.connect(self._choose_recent_vars)
        except Exception:
            pass
        vr.addWidget(self._recent_vars)
        clr_v = QPushButton("Clear"); clr_v.setToolTip("Clear recent Vars"); clr_v.clicked.connect(lambda: self._clear_recents("gcode_preview/recent_vars"))
        vr.addWidget(clr_v)
        vr.addStretch(1)
        lay.addLayout(vr)
        self._vars = QTextEdit()
        self._vars.setPlaceholderText('{"nozzle":205, "bed":60, "layer":1, "tool":0}')
        try:
            self._vars.setText(self.s.value("gcode_preview/vars_json", '{"nozzle":205, "bed":60, "layer":1, "tool":0}'))
        except Exception:
            self._vars.setText('{"nozzle":205, "bed":60, "layer":1, "tool":0}')
        self._vars.setTabChangesFocus(True)
        lay.addWidget(self._vars)

        # Render button
        btn_render = QPushButton("Render"); btn_render.setShortcut("Ctrl+R")
        btn_render.clicked.connect(self._render)
        lay.addWidget(btn_render)

        # Preview
        lay.addWidget(QLabel("Preview:"))
        self._preview = QTextEdit(readOnly=True)
        lay.addWidget(self._preview, 1)

    # --- State persistence ---
    def _restore_state(self):
        try:
            # Restore window geometry
            geo = self.s.value("gcode_preview/geometry", None)
            if geo:
                self.restoreGeometry(geo)
        except Exception:
            pass
        # Attempt to restore last PDL
        try:
            last_p = self.s.value("gcode_preview/pdl_path", "")
            if last_p:
                p = Path(str(last_p))
                if p.exists():
                    self._load_pdl_from_path(p)
        except Exception:
            pass
        # Populate recents
        try:
            self._refresh_recents_combo()
        except Exception:
            pass

    def _persist_hook(self, hook: str):
        try:
            if hook:
                self.s.setValue("gcode_preview/hook", hook)
        except Exception:
            pass

    def closeEvent(self, e):  # noqa: N802 - Qt API
        try:
            self.s.setValue("gcode_preview/geometry", self.saveGeometry())
        except Exception:
            pass
        return super().closeEvent(e)

    def _open_pdl(self):
        start = self.s.value("gcode_preview/pdl_path", "")
        fn, _ = QFileDialog.getOpenFileName(self, "Open PDL (YAML/JSON)", start or "", "PDL (*.yaml *.yml *.json)")
        if not fn:
            return
        p = Path(fn)
        self._load_pdl_from_path(p)

    def _load_pdl_from_path(self, p: Path):
        text = p.read_text(encoding="utf-8")
        data = json.loads(text) if p.suffix.lower() == ".json" else yaml.safe_load(text)
        # inject policies from Settings if present
        try:
            from PySide6.QtCore import QSettings
            s = QSettings("OpenPrintKit", "OPKStudio")
            pol = {
                'klipper': {'camera_map': bool(s.value('policy/klipper/camera_map', True, type=bool))},
                'rrf': {'prefer_named_pins': bool(s.value('policy/rrf/prefer_named_pins', True, type=bool))},
                'grbl': {'exhaust_mode': s.value('policy/grbl/exhaust_mode', 'M8')},
            }
            data = dict(data or {})
            data['policies'] = pol
        except Exception:
            pass
        self._gcode = (data or {}).get("gcode") or {}
        hooks = list_hooks(self._gcode)
        self._hook.clear()
        self._hook.addItems(hooks)
        try:
            last_hook = self.s.value("gcode_preview/hook", "")
            if last_hook and last_hook in hooks:
                self._hook.setCurrentText(last_hook)
        except Exception:
            pass
        self._pdl_path = p
        self._file_label.setText(str(p))
        try:
            self.s.setValue("gcode_preview/pdl_path", str(p))
        except Exception:
            pass
        # update recents
        try:
            self._push_recent("gcode_preview/recent_pdls", str(p))
            self._refresh_recents_combo()
        except Exception:
            pass

    def _render(self):
        hook = self._hook.currentText()
        if not hook:
            self._preview.setPlainText("No hook selected")
            return
        seq = None
        if hook in self._gcode:
            seq = self._gcode.get(hook)
        elif isinstance(self._gcode.get("hooks"), dict) and hook in self._gcode.get("hooks"):
            seq = self._gcode["hooks"][hook]
        if not isinstance(seq, list):
            self._preview.setPlainText("Hook not found or not a sequence")
            return
        # Validate variables JSON and provide feedback
        text = self._vars.toPlainText() or "{}"
        try:
            vars_obj = json.loads(text)
            if not isinstance(vars_obj, dict):
                raise ValueError("Variables JSON must be an object (name → value)")
        except Exception as e:
            self._preview.setPlainText(f"Invalid variables JSON: {e}")
            return
        # Persist vars and hook
        try:
            self.s.setValue("gcode_preview/vars_json", self._vars.toPlainText())
            if hook:
                self.s.setValue("gcode_preview/hook", hook)
        except Exception:
            pass
        rendered, missing = render_sequence(seq, vars_obj)
        out = "\n".join(rendered)
        if missing:
            out += f"\n\n# Unresolved placeholders: {', '.join(sorted(missing))}"
        # show also what placeholders are present
        present = find_placeholders(seq)
        if present:
            out += f"\n# Placeholders present: {', '.join(sorted(present))}"
        self._preview.setPlainText(out)

    # --- File helpers ---
    def _get_recent(self, key: str) -> list:
        import json as _json
        try:
            raw = self.s.value(key, "[]")
            if isinstance(raw, str):
                return list(_json.loads(raw) or [])
            if isinstance(raw, list):
                return raw
        except Exception:
            pass
        return []

    def _recents_max(self) -> int:
        try:
            n = int(self.s.value("ui/recents_max", 10))
            return max(1, min(n, 50))
        except Exception:
            return 10

    def _set_recent(self, key: str, items: list) -> None:
        import json as _json
        try:
            self.s.setValue(key, _json.dumps(items[: self._recents_max()]))
        except Exception:
            pass

    def _push_recent(self, key: str, path: str) -> None:
        items = [i for i in self._get_recent(key) if i != path]
        items.insert(0, path)
        self._set_recent(key, items)

    def _refresh_recents_combo(self):
        items = [i for i in self._get_recent("gcode_preview/recent_pdls") if Path(i).exists()]
        # persist filtered list
        self._set_recent("gcode_preview/recent_pdls", items)
        try:
            self._recent_pdls.blockSignals(True)
        except Exception:
            pass
        self._recent_pdls.clear()
        for it in items:
            self._recent_pdls.addItem(it)
        try:
            self._recent_pdls.blockSignals(False)
        except Exception:
            pass
        # Vars recents
        vitems = [i for i in self._get_recent("gcode_preview/recent_vars") if Path(i).exists()]
        self._set_recent("gcode_preview/recent_vars", vitems)
        try:
            self._recent_vars.blockSignals(True)
        except Exception:
            pass
        self._recent_vars.clear()
        for it in vitems:
            self._recent_vars.addItem(it)
        try:
            self._recent_vars.blockSignals(False)
        except Exception:
            pass

    def _choose_recent_pdl(self):
        try:
            text = self._recent_pdls.currentText().strip()
        except Exception:
            text = ""
        if not text:
            return
        p = Path(text)
        if p.exists():
            self._load_pdl_from_path(p)

    def _choose_recent_vars(self):
        try:
            text = self._recent_vars.currentText().strip()
        except Exception:
            text = ""
        if not text:
            return
        p = Path(text)
        if p.exists():
            try:
                self._vars.setPlainText(p.read_text(encoding="utf-8"))
                self.s.setValue("gcode_preview/vars_path", str(p))
            except Exception:
                pass

    def _load_vars_file(self):
        start = self.s.value("gcode_preview/vars_path", "")
        fn, _ = QFileDialog.getOpenFileName(self, "Open Variables JSON", start or "", "JSON (*.json)")
        if not fn:
            return
        p = Path(fn)
        try:
            self._vars.setPlainText(Path(p).read_text(encoding="utf-8"))
            self.s.setValue("gcode_preview/vars_path", str(p))
            self._push_recent("gcode_preview/recent_vars", str(p))
        except Exception:
            pass

    def _save_vars_file(self):
        start = self.s.value("gcode_preview/vars_path", "")
        fn, _ = QFileDialog.getSaveFileName(self, "Save Variables JSON As…", start or "vars.json", "JSON (*.json)")
        if not fn:
            return
        p = Path(fn)
        try:
            p.write_text(self._vars.toPlainText(), encoding="utf-8")
            self.s.setValue("gcode_preview/vars_path", str(p))
            self._push_recent("gcode_preview/recent_vars", str(p))
        except Exception:
            pass

    def _clear_recents(self, key: str):
        self._set_recent(key, [])
        self._refresh_recents_combo()

    def _insert_vars_template(self):
        try:
            from PySide6.QtWidgets import QInputDialog
        except Exception:
            return
        templates = self._load_templates()
        names = list(templates.keys())
        name, ok = QInputDialog.getItem(self, "Insert Variables Template", "Template:", names, 0, False)
        if not ok or not name:
            return
        import json as _json
        self._vars.setPlainText(_json.dumps(templates[name], indent=2))
        try:
            self.s.setValue("gcode_preview/vars_json", self._vars.toPlainText())
        except Exception:
            pass

    def _load_templates(self) -> dict:
        # Built-in defaults
        templates = {
            "Basic (nozzle/bed/layer/tool)": {"nozzle": 205, "bed": 60, "layer": 1, "tool": 0},
            "Monitoring (progress/time)": {"progress": 25, "elapsed_s": 0},
            "Environment (chamber/fan)": {"chamber": 40, "fan": 100},
        }
        # Merge from Settings JSON if available
        try:
            path = str(self.s.value("gcode/templates_path", "") or "").strip()
            if path:
                p = Path(path)
                if p.exists():
                    import json as _json
                    data = _json.loads(p.read_text(encoding="utf-8")) or {}
                    if isinstance(data, dict):
                        templates.update({str(k): v for k, v in data.items() if isinstance(v, dict)})
        except Exception:
            pass
        return templates
