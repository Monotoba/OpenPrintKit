from __future__ import annotations
import json
from pathlib import Path
from ._qt_compat import (
    QDialog, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QComboBox, QFileDialog, QMessageBox, QSettings
)
from ..core.gcode import generate_snippets


class GenerateSnippetsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generate Firmware-ready Snippets")
        self.s = QSettings("OpenPrintKit", "OPKStudio")
        self._build()
        self._load_defaults()

    def _build(self):
        f = QFormLayout(self)
        self.ed_pdl = QLineEdit(); self.ed_pdl.setPlaceholderText("Select PDL (YAML/JSON)")
        b_pdl = QPushButton("…"); b_pdl.clicked.connect(self._pick_pdl)
        row_pdl = QHBoxLayout(); row_pdl.addWidget(self.ed_pdl); row_pdl.addWidget(b_pdl)
        self.cb_fw = QComboBox(); self.cb_fw.addItems(["marlin","rrf","klipper","grbl","linuxcnc","smoothie","repetier","bambu"]) 
        self.ed_out = QLineEdit(); self.ed_out.setPlaceholderText("Output directory")
        b_out = QPushButton("…"); b_out.clicked.connect(self._pick_out)
        row_out = QHBoxLayout(); row_out.addWidget(self.ed_out); row_out.addWidget(b_out)
        f.addRow("PDL file", row_pdl)
        f.addRow("Firmware", self.cb_fw)
        f.addRow("Output dir", row_out)
        # Buttons
        btns = QHBoxLayout();
        go = QPushButton("Generate"); go.clicked.connect(self._gen)
        cancel = QPushButton("Close"); cancel.clicked.connect(self.reject)
        btns.addWidget(go); btns.addWidget(cancel)
        f.addRow(btns)

    def _load_defaults(self):
        self.cb_fw.setCurrentText(self.s.value("app/default_firmware", "marlin"))
        # Prefer dialog-specific out_dir if present, else app default
        self.ed_out.setText(self.s.value("gen_snippets/out_dir", self.s.value("app/out_dir", "")))
        self.ed_pdl.setText(self.s.value("gen_snippets/pdl_path", ""))

    def _pick_pdl(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Select PDL (YAML/JSON)", "", "PDL (*.yaml *.yml *.json)")
        if fn: self.ed_pdl.setText(fn)

    def _pick_out(self):
        d = QFileDialog.getExistingDirectory(self, "Select Output Directory", self.ed_out.text() or "")
        if d: self.ed_out.setText(d)

    def _gen(self):
        pdl_path = Path(self.ed_pdl.text().strip())
        out_dir = Path(self.ed_out.text().strip() or ".")
        if not pdl_path.exists():
            QMessageBox.warning(self, "Generate", "Please select a valid PDL file (YAML/JSON).")
            return
        try:
            text = pdl_path.read_text(encoding="utf-8")
            data = json.loads(text) if pdl_path.suffix.lower()==".json" else __import__("yaml").safe_load(text)
        except Exception as e:
            QMessageBox.critical(self, "Generate", f"Failed to read PDL at {pdl_path.name}:\n{e}")
            return
        fw = self.cb_fw.currentText() or None
        try:
            # inject policies from Settings
            pol = {
                'klipper': {'camera_map': bool(self.s.value('policy/klipper/camera_map', True, type=bool))},
                'rrf': {'prefer_named_pins': bool(self.s.value('policy/rrf/prefer_named_pins', True, type=bool))},
                'grbl': {'exhaust_mode': self.s.value('policy/grbl/exhaust_mode', 'M8')},
            }
            data = dict(data or {})
            data['policies'] = pol
            start, end = generate_snippets(data, firmware=fw)
        except Exception as e:
            QMessageBox.critical(self, "Generate", f"Failed to generate snippets:\n{e}")
            return
        try:
            out_dir.mkdir(parents=True, exist_ok=True)
            base = pdl_path.stem
            (out_dir / f"{base}_start.gcode").write_text("\n".join(start)+"\n", encoding="utf-8")
            (out_dir / f"{base}_end.gcode").write_text("\n".join(end)+"\n", encoding="utf-8")
        except Exception as e:
            QMessageBox.critical(self, "Generate", f"Failed to write snippets:\n{e}")
            return
        # Persist last-used inputs
        try:
            self.s.setValue("gen_snippets/pdl_path", str(pdl_path))
            self.s.setValue("gen_snippets/out_dir", str(out_dir))
            # Also refresh app default out_dir for convenience
            self.s.setValue("app/out_dir", str(out_dir))
        except Exception:
            pass
        QMessageBox.information(self, "Generate", f"Wrote:\n{out_dir}/{base}_start.gcode\n{out_dir}/{base}_end.gcode")
        self.accept()
