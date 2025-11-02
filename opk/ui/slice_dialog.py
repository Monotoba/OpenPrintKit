from __future__ import annotations
from pathlib import Path
from ._qt_compat import QDialog, QFormLayout, QLineEdit, QComboBox, QPushButton, QHBoxLayout, QFileDialog, QTextEdit, QSettings
import subprocess, shutil


class SliceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Slice via External CLI")
        self.s = QSettings("OpenPrintKit", "OPKStudio")
        self._build()
        self._load()

    def _build(self):
        f = QFormLayout(self)
        self.cb_slicer = QComboBox(); self.cb_slicer.addItems(["slic3r","prusaslicer","superslicer","curaengine"]) ; self.cb_slicer.setToolTip("External slicer (must be on PATH)")
        self.ed_model = QLineEdit(); self.ed_model.setPlaceholderText("Model (STL/3MF)")
        b_model = QPushButton("…"); b_model.clicked.connect(self._pick_model)
        r1 = QHBoxLayout(); r1.addWidget(self.ed_model); r1.addWidget(b_model)
        self.ed_profile = QLineEdit(); self.ed_profile.setPlaceholderText("Profile (INI for Slic3r family)")
        b_prof = QPushButton("…"); b_prof.clicked.connect(self._pick_profile)
        r2 = QHBoxLayout(); r2.addWidget(self.ed_profile); r2.addWidget(b_prof)
        self.ed_out = QLineEdit(); self.ed_out.setPlaceholderText("Output G-code path")
        b_out = QPushButton("…"); b_out.clicked.connect(self._pick_out)
        r3 = QHBoxLayout(); r3.addWidget(self.ed_out); r3.addWidget(b_out)
        self.ed_flags = QLineEdit(); self.ed_flags.setPlaceholderText("Extra flags (CuraEngine: include -j machine.json and -s settings)")
        self.out_view = QTextEdit(readOnly=True)
        # Buttons
        rowb = QHBoxLayout();
        b_run = QPushButton("Slice"); b_run.clicked.connect(self._run)
        b_close = QPushButton("Close"); b_close.clicked.connect(self.reject)
        rowb.addWidget(b_run); rowb.addWidget(b_close)

        f.addRow("Slicer", self.cb_slicer)
        f.addRow("Model", r1)
        f.addRow("Profile", r2)
        f.addRow("Output", r3)
        f.addRow("Flags", self.ed_flags)
        f.addRow(self.out_view)
        f.addRow(rowb)

    def _load(self):
        self.cb_slicer.setCurrentText(self.s.value("slice/slicer", "prusaslicer"))
        self.ed_model.setText(self.s.value("slice/model", ""))
        self.ed_profile.setText(self.s.value("slice/profile", ""))
        self.ed_out.setText(self.s.value("slice/out", ""))
        self.ed_flags.setText(self.s.value("slice/flags", ""))

    def _pick_model(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Pick model", "", "Models (*.stl *.3mf *.obj)")
        if fn: self.ed_model.setText(fn)

    def _pick_profile(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Pick profile (INI)", "", "INI (*.ini)")
        if fn: self.ed_profile.setText(fn)

    def _pick_out(self):
        fn, _ = QFileDialog.getSaveFileName(self, "Save G-code As", "", "G-code (*.gcode *.gco)")
        if fn: self.ed_out.setText(fn)

    def _run(self):
        slicer = self.cb_slicer.currentText()
        bin_name = 'CuraEngine' if slicer == 'curaengine' else slicer
        exe = shutil.which(bin_name)
        if not exe:
            self.out_view.append(f"[ERROR] slicer not found: {bin_name}")
            return
        model = Path(self.ed_model.text().strip())
        outp = Path(self.ed_out.text().strip())
        prof = Path(self.ed_profile.text().strip())
        flags = (self.ed_flags.text().strip() or '').split()
        if slicer in ('slic3r','prusaslicer','superslicer'):
            if not prof.exists():
                self.out_view.append("[ERROR] Profile INI is required for Slic3r family")
                return
            cmd = [exe, '--load', str(prof), '--export-gcode', '-o', str(outp), str(model)]
        else:
            cmd = [exe, 'slice', '-o', str(outp), '-l', str(model)] + flags
        try:
            self.out_view.append('[RUN] ' + ' '.join(cmd))
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.stdout: self.out_view.append(res.stdout)
            if res.stderr: self.out_view.append(res.stderr)
            self.out_view.append(f"[EXIT] code={res.returncode}")
            # persist selections
            self.s.setValue("slice/slicer", self.cb_slicer.currentText())
            self.s.setValue("slice/model", str(model))
            self.s.setValue("slice/profile", str(prof))
            self.s.setValue("slice/out", str(outp))
            self.s.setValue("slice/flags", self.ed_flags.text().strip())
        except Exception as e:
            self.out_view.append(f"[ERROR] {e}")
