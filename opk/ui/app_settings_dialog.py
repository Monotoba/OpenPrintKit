from __future__ import annotations
from PySide6.QtWidgets import (
    QDialog, QFormLayout, QLineEdit, QComboBox, QCheckBox, QPushButton, QHBoxLayout, QFileDialog
)
from PySide6.QtCore import QSettings


class AppSettingsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Application Settings")
        self.s = QSettings("OpenPrintKit", "OPKStudio")
        self._build()
        self._load()

    def _build(self):
        f = QFormLayout(self)
        self.cb_slicer = QComboBox(); self.cb_slicer.addItems(["orca","cura","prusa","bambu","custom"])
        self.cb_slicer.setToolTip("Default slicer for generation")
        self.cb_firmware = QComboBox(); self.cb_firmware.addItems(["marlin","rrf","klipper","grbl","linuxcnc","smoothie","repetier","bambu"]) 
        self.cb_firmware.setToolTip("Default firmware for mapping")
        self.ed_outdir = QLineEdit(); self.ed_outdir.setPlaceholderText("e.g., ./dist/snippets"); self.ed_outdir.setToolTip("Default output directory for generated files")
        b_od = QPushButton("…"); b_od.clicked.connect(self._pick_outdir)
        row_od = QHBoxLayout(); row_od.addWidget(self.ed_outdir); row_od.addWidget(b_od)
        self.ed_vars = QLineEdit(); self.ed_vars.setPlaceholderText("pdl-spec/examples/vars.sample.json"); self.ed_vars.setToolTip("Default variables JSON for G-code preview")
        b_v = QPushButton("…"); b_v.clicked.connect(self._pick_vars)
        row_v = QHBoxLayout(); row_v.addWidget(self.ed_vars); row_v.addWidget(b_v)
        # Policy toggles
        self.ck_klip_cam = QCheckBox("Map M240 to M118 TIMELAPSE_TAKE_FRAME (Klipper)")
        self.ck_rrf_named = QCheckBox("Prefer named pins (RRF)")
        self.cb_grbl_exh = QComboBox(); self.cb_grbl_exh.addItems(["M8 (flood)", "M7 (mist)"]) ; self.cb_grbl_exh.setToolTip("Exhaust mapping for GRBL/LinuxCNC")
        # Layout
        f.addRow("Default slicer", self.cb_slicer)
        f.addRow("Default firmware", self.cb_firmware)
        f.addRow("Output directory", row_od)
        f.addRow("Variables JSON", row_v)
        f.addRow(self.ck_klip_cam)
        f.addRow(self.ck_rrf_named)
        f.addRow("GRBL/LinuxCNC exhaust", self.cb_grbl_exh)
        # Buttons
        btns = QHBoxLayout(); ok = QPushButton("Save"); ok.clicked.connect(self.accept); cancel = QPushButton("Cancel"); cancel.clicked.connect(self.reject)
        btns.addWidget(ok); btns.addWidget(cancel)
        f.addRow(btns)

    def _pick_outdir(self):
        from PySide6.QtWidgets import QFileDialog
        d = QFileDialog.getExistingDirectory(self, "Select Output Directory", self.ed_outdir.text() or "")
        if d:
            self.ed_outdir.setText(d)

    def _pick_vars(self):
        from PySide6.QtWidgets import QFileDialog
        fn, _ = QFileDialog.getOpenFileName(self, "Select Variables JSON", self.ed_vars.text() or "", "JSON (*.json)")
        if fn:
            self.ed_vars.setText(fn)

    def _load(self):
        self.cb_slicer.setCurrentText(self.s.value("app/default_slicer", "orca"))
        self.cb_firmware.setCurrentText(self.s.value("app/default_firmware", "marlin"))
        self.ed_outdir.setText(self.s.value("app/out_dir", ""))
        self.ed_vars.setText(self.s.value("app/vars_path", ""))
        self.ck_klip_cam.setChecked(self.s.value("policy/klipper/camera_map", True, type=bool))
        self.ck_rrf_named.setChecked(self.s.value("policy/rrf/prefer_named_pins", True, type=bool))
        self.cb_grbl_exh.setCurrentIndex(0 if self.s.value("policy/grbl/exhaust_mode","M8") == "M8" else 1)

    def accept(self):
        self.s.setValue("app/default_slicer", self.cb_slicer.currentText())
        self.s.setValue("app/default_firmware", self.cb_firmware.currentText())
        self.s.setValue("app/out_dir", self.ed_outdir.text().strip())
        self.s.setValue("app/vars_path", self.ed_vars.text().strip())
        self.s.setValue("policy/klipper/camera_map", self.ck_klip_cam.isChecked())
        self.s.setValue("policy/rrf/prefer_named_pins", self.ck_rrf_named.isChecked())
        self.s.setValue("policy/grbl/exhaust_mode", "M8" if self.cb_grbl_exh.currentIndex()==0 else "M7")
        super().accept()

