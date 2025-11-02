from __future__ import annotations
import json
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView, QComboBox
)
from PySide6.QtCore import QSettings
import yaml
from ..core.gcode import list_hooks, render_sequence


class GcodeValidateDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Validate Hook Variables")
        self._gcode = {}
        self._pdl_path: Path | None = None
        self._vars = {}
        self.s = QSettings("OpenPrintKit", "OPKStudio")
        self._build_ui()
        self._restore_state()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        row = QHBoxLayout()
        self._pdl_label = QLabel("No PDL loaded")
        btn_pdl = QPushButton("Open PDL…"); btn_pdl.setShortcut("Ctrl+O"); btn_pdl.clicked.connect(self._open_pdl)
        row.addWidget(self._pdl_label, 1)
        row.addWidget(QLabel("Recent:"))
        self._recent_pdls = QComboBox(); self._recent_pdls.setEditable(False)
        try:
            self._recent_pdls.activated.connect(self._choose_recent_pdl)
        except Exception:
            pass
        row.addWidget(self._recent_pdls)
        row.addWidget(btn_pdl)
        lay.addLayout(row)

        row2 = QHBoxLayout()
        self._vars_label = QLabel("No vars.json loaded")
        btn_vars = QPushButton("Open Vars…"); btn_vars.setShortcut("Ctrl+L"); btn_vars.clicked.connect(self._open_vars)
        row2.addWidget(self._vars_label, 1)
        row2.addWidget(QLabel("Recent:"))
        self._recent_vars = QComboBox(); self._recent_vars.setEditable(False)
        try:
            self._recent_vars.activated.connect(self._choose_recent_vars)
        except Exception:
            pass
        row2.addWidget(self._recent_vars)
        row2.addWidget(btn_vars)
        btn_tpl = QPushButton("Template…"); btn_tpl.setToolTip("Create vars JSON from template"); btn_tpl.setShortcut("Ctrl+T")
        btn_tpl.clicked.connect(self._create_vars_from_template)
        row2.addWidget(btn_tpl)
        lay.addLayout(row2)

        btn_run = QPushButton("Validate"); btn_run.setShortcut("Ctrl+V"); btn_run.clicked.connect(self._validate)
        lay.addWidget(btn_run)

        self._table = QTableWidget(0, 2)
        self._table.setHorizontalHeaderLabels(["Hook", "Missing Variables"])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        lay.addWidget(self._table)

    # --- State persistence ---
    def _restore_state(self):
        # Restore window geometry
        try:
            geo = self.s.value("gcode_validate/geometry", None)
            if geo:
                self.restoreGeometry(geo)
        except Exception:
            pass
        # Restore last PDL and vars if available
        try:
            last_p = self.s.value("gcode_validate/pdl_path", "")
            if last_p:
                p = Path(str(last_p))
                if p.exists():
                    self._load_pdl_from_path(p)
        except Exception:
            pass
        try:
            last_v = self.s.value("gcode_validate/vars_path", "")
            if last_v:
                vp = Path(str(last_v))
                if vp.exists():
                    self._load_vars_from_path(vp)
        except Exception:
            pass
        # Populate recents
        try:
            self._refresh_recents()
        except Exception:
            pass

    def closeEvent(self, e):  # noqa: N802 - Qt API
        try:
            self.s.setValue("gcode_validate/geometry", self.saveGeometry())
        except Exception:
            pass
        return super().closeEvent(e)

    def _open_pdl(self):
        start = self.s.value("gcode_validate/pdl_path", "")
        fn, _ = QFileDialog.getOpenFileName(self, "Open PDL (YAML/JSON)", start or "", "PDL (*.yaml *.yml *.json)")
        if not fn: return
        p = Path(fn)
        self._load_pdl_from_path(p)

    def _load_pdl_from_path(self, p: Path):
        text = p.read_text(encoding="utf-8")
        data = json.loads(text) if p.suffix.lower() == ".json" else yaml.safe_load(text)
        self._gcode = (data or {}).get("gcode") or {}
        self._pdl_path = p
        self._pdl_label.setText(str(p))
        try:
            self.s.setValue("gcode_validate/pdl_path", str(p))
        except Exception:
            pass
        try:
            self._push_recent("gcode_validate/recent_pdls", str(p))
            self._refresh_recents()
        except Exception:
            pass

    def _open_vars(self):
        start = self.s.value("gcode_validate/vars_path", "")
        fn, _ = QFileDialog.getOpenFileName(self, "Open Variables JSON", start or "", "JSON (*.json)")
        if not fn: return
        p = Path(fn)
        self._load_vars_from_path(p)

    def _load_vars_from_path(self, p: Path):
        self._vars = json.loads(p.read_text(encoding="utf-8"))
        self._vars_label.setText(str(p))
        try:
            self.s.setValue("gcode_validate/vars_path", str(p))
        except Exception:
            pass
        try:
            self._push_recent("gcode_validate/recent_vars", str(p))
            self._refresh_recents()
        except Exception:
            pass

    def _validate(self):
        hooks = list_hooks(self._gcode)
        self._table.setRowCount(0)
        for h in hooks:
            seq = self._gcode.get(h) if h in self._gcode else (self._gcode.get("hooks", {}) or {}).get(h)
            if not isinstance(seq, list):
                continue
            _, missing = render_sequence(seq, self._vars or {})
            if missing:
                r = self._table.rowCount(); self._table.insertRow(r)
                self._table.setItem(r, 0, QTableWidgetItem(h))
                self._table.setItem(r, 1, QTableWidgetItem(", ".join(sorted(missing))))

    # --- Recents helpers ---
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

    def _refresh_recents(self):
        # PDLs
        items = self._get_recent("gcode_validate/recent_pdls")
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
        # Vars
        vitems = self._get_recent("gcode_validate/recent_vars")
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
            self._load_vars_from_path(p)

    def _create_vars_from_template(self):
        try:
            from PySide6.QtWidgets import QInputDialog
        except Exception:
            return
        templates = self._load_templates()
        names = list(templates.keys())
        name, ok = QInputDialog.getItem(self, "Variables Template", "Template:", names, 0, False)
        if not ok or not name:
            return
        from PySide6.QtWidgets import QFileDialog
        import json as _json
        start = self.s.value("gcode_validate/vars_path", "")
        fn, _ = QFileDialog.getSaveFileName(self, "Save Template Vars As…", start or "vars.json", "JSON (*.json)")
        if not fn:
            return
        p = Path(fn)
        try:
            p.write_text(_json.dumps(templates[name], indent=2), encoding="utf-8")
            self._load_vars_from_path(p)
        except Exception:
            pass

    def _load_templates(self) -> dict:
        templates = {
            "Basic (nozzle/bed/layer/tool)": {"nozzle": 205, "bed": 60, "layer": 1, "tool": 0},
            "Monitoring (progress/time)": {"progress": 25, "elapsed_s": 0},
            "Environment (chamber/fan)": {"chamber": 40, "fan": 100},
        }
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
