from __future__ import annotations
import json
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFileDialog, QTableWidget, QTableWidgetItem, QHeaderView
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

    def _build_ui(self):
        lay = QVBoxLayout(self)
        row = QHBoxLayout()
        self._pdl_label = QLabel("No PDL loaded")
        btn_pdl = QPushButton("Open PDL…"); btn_pdl.clicked.connect(self._open_pdl)
        row.addWidget(self._pdl_label, 1); row.addWidget(btn_pdl)
        lay.addLayout(row)

        row2 = QHBoxLayout()
        self._vars_label = QLabel("No vars.json loaded")
        btn_vars = QPushButton("Open Vars…"); btn_vars.clicked.connect(self._open_vars)
        row2.addWidget(self._vars_label, 1); row2.addWidget(btn_vars)
        lay.addLayout(row2)

        btn_run = QPushButton("Validate"); btn_run.clicked.connect(self._validate)
        lay.addWidget(btn_run)

        self._table = QTableWidget(0, 2)
        self._table.setHorizontalHeaderLabels(["Hook", "Missing Variables"])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        lay.addWidget(self._table)

    def _open_pdl(self):
        start = self.s.value("gcode_validate/pdl_path", "")
        fn, _ = QFileDialog.getOpenFileName(self, "Open PDL (YAML/JSON)", start or "", "PDL (*.yaml *.yml *.json)")
        if not fn: return
        p = Path(fn)
        text = p.read_text(encoding="utf-8")
        data = json.loads(text) if p.suffix.lower() == ".json" else yaml.safe_load(text)
        self._gcode = (data or {}).get("gcode") or {}
        self._pdl_path = p
        self._pdl_label.setText(str(p))
        try:
            self.s.setValue("gcode_validate/pdl_path", str(p))
        except Exception:
            pass

    def _open_vars(self):
        start = self.s.value("gcode_validate/vars_path", "")
        fn, _ = QFileDialog.getOpenFileName(self, "Open Variables JSON", start or "", "JSON (*.json)")
        if not fn: return
        p = Path(fn)
        self._vars = json.loads(p.read_text(encoding="utf-8"))
        self._vars_label.setText(str(p))
        try:
            self.s.setValue("gcode_validate/vars_path", str(p))
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
