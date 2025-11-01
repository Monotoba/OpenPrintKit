from __future__ import annotations
import json
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QComboBox, QFileDialog, QMessageBox, QCheckBox
)
from ..core.project import find_project_file, load_project_config, merge_policies


class GenerateProfilesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generate Slicer Profiles")
        self._build()

    def _build(self):
        f = QFormLayout(self)
        self.ed_pdl = QLineEdit(); self.ed_pdl.setPlaceholderText("Select PDL (YAML/JSON)")
        b_pdl = QPushButton("…"); b_pdl.clicked.connect(self._pick_pdl)
        row_pdl = QHBoxLayout(); row_pdl.addWidget(self.ed_pdl); row_pdl.addWidget(b_pdl)
        self.cb_slicer = QComboBox(); self.cb_slicer.addItems(["orca","cura","prusa","ideamaker","bambu"]) 
        self.ed_out = QLineEdit(); self.ed_out.setPlaceholderText("Output directory")
        b_out = QPushButton("…"); b_out.clicked.connect(self._pick_out)
        row_out = QHBoxLayout(); row_out.addWidget(self.ed_out); row_out.addWidget(b_out)
        self.ck_bundle = QCheckBox("Bundle (Orca)")
        self.ed_bundle = QLineEdit(); self.ed_bundle.setPlaceholderText("OUT.orca_printer")
        f.addRow("PDL file", row_pdl)
        f.addRow("Slicer", self.cb_slicer)
        f.addRow("Output dir", row_out)
        f.addRow(self.ck_bundle)
        f.addRow("Bundle output", self.ed_bundle)
        # Buttons
        btns = QHBoxLayout();
        go = QPushButton("Generate"); go.clicked.connect(self._gen)
        cancel = QPushButton("Close"); cancel.clicked.connect(self.reject)
        btns.addWidget(go); btns.addWidget(cancel)
        f.addRow(btns)

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
            QMessageBox.warning(self, "Generate", "Please select a valid PDL file.")
            return
        try:
            text = pdl_path.read_text(encoding="utf-8")
            data = json.loads(text) if pdl_path.suffix.lower()==".json" else __import__("yaml").safe_load(text)
        except Exception as e:
            QMessageBox.critical(self, "Generate", f"Failed to read PDL:\n{e}")
            return
        try:
            proj = find_project_file(pdl_path.parent)
            if proj:
                data = merge_policies(data or {}, load_project_config(proj))
        except Exception:
            pass
        slicer = self.cb_slicer.currentText()
        try:
            out_dir.mkdir(parents=True, exist_ok=True)
            if slicer == 'orca':
                from ..plugins.slicers.orca import generate_orca
                out = generate_orca(data or {}, out_dir)
                if self.ck_bundle.isChecked() and self.ed_bundle.text().strip():
                    from ..core.bundle import build_bundle
                    build_bundle(out_dir, Path(self.ed_bundle.text().strip()))
            elif slicer == 'cura':
                from ..plugins.slicers.cura import generate_cura
                out = generate_cura(data or {}, out_dir)
            elif slicer == 'prusa':
                from ..plugins.slicers.prusa import generate_prusa
                out = generate_prusa(data or {}, out_dir)
            elif slicer == 'ideamaker':
                from ..plugins.slicers.ideamaker import generate_ideamaker
                out = generate_ideamaker(data or {}, out_dir)
            elif slicer == 'bambu':
                from ..plugins.slicers.bambu import generate_bambu
                out = generate_bambu(data or {}, out_dir)
            else:
                out = {}
        except Exception as e:
            QMessageBox.critical(self, "Generate", f"Failed to generate profiles:\n{e}")
            return
        QMessageBox.information(self, "Generate", f"Wrote {len(out)} file(s) to {out_dir}")
        self.accept()

