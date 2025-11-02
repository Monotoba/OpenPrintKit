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

    def _build_ui(self):
        lay = QVBoxLayout(self)

        # File picker
        row = QHBoxLayout()
        self._file_label = QLabel("No PDL loaded")
        btn_open = QPushButton("Open PDL…")
        btn_open.clicked.connect(self._open_pdl)
        row.addWidget(self._file_label, 1)
        row.addWidget(btn_open)
        lay.addLayout(row)

        # Hook selector
        row2 = QHBoxLayout()
        row2.addWidget(QLabel("Hook:"))
        self._hook = QComboBox()
        row2.addWidget(self._hook, 1)
        lay.addLayout(row2)

        # Vars editor
        lay.addWidget(QLabel("Variables (JSON):"))
        self._vars = QTextEdit()
        self._vars.setPlaceholderText('{"nozzle":205, "bed":60, "layer":1, "tool":0}')
        try:
            self._vars.setText(self.s.value("gcode_preview/vars_json", '{"nozzle":205, "bed":60, "layer":1, "tool":0}'))
        except Exception:
            self._vars.setText('{"nozzle":205, "bed":60, "layer":1, "tool":0}')
        self._vars.setTabChangesFocus(True)
        lay.addWidget(self._vars)

        # Render button
        btn_render = QPushButton("Render")
        btn_render.clicked.connect(self._render)
        lay.addWidget(btn_render)

        # Preview
        lay.addWidget(QLabel("Preview:"))
        self._preview = QTextEdit(readOnly=True)
        lay.addWidget(self._preview, 1)

    def _open_pdl(self):
        start = self.s.value("gcode_preview/pdl_path", "")
        fn, _ = QFileDialog.getOpenFileName(self, "Open PDL (YAML/JSON)", start or "", "PDL (*.yaml *.yml *.json)")
        if not fn:
            return
        p = Path(fn)
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
        try:
            vars_obj = json.loads(self._vars.toPlainText() or "{}")
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
