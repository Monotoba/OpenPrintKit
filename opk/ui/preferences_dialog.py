from __future__ import annotations
from ._qt_compat import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog, QSettings


class PreferencesDialog(QDialog):
    def __init__(self, parent=None, orca_preset_dir: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self._orca = QLineEdit(orca_preset_dir)
        self.s = QSettings("OpenPrintKit", "OPKStudio")
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        row = QHBoxLayout()
        row.addWidget(QLabel("Orca presets directory"))
        row.addWidget(self._orca)
        pick = QPushButton("…"); pick.clicked.connect(self._pick_orca)
        row.addWidget(pick)
        lay.addLayout(row)

        # Clear recent files (G-code preview/validate)
        row2 = QHBoxLayout()
        btn_clear = QPushButton("Clear Recent Files…")
        btn_clear.setToolTip("Clear recent PDL/Vars lists used by G-code tools")
        btn_clear.clicked.connect(self._clear_recents)
        row2.addWidget(btn_clear)
        row2.addStretch(1)
        lay.addLayout(row2)

        btns = QHBoxLayout()
        reset = QPushButton("Reset to Defaults"); reset.setToolTip("Reset fields to defaults (not saved until Save)"); reset.clicked.connect(self._reset_defaults)
        btns.addWidget(reset)
        btns.addStretch(1)
        ok = QPushButton("Save"); ok.clicked.connect(self.accept); btns.addWidget(ok)
        cancel = QPushButton("Cancel"); cancel.clicked.connect(self.reject); btns.addWidget(cancel)
        lay.addLayout(btns)

    def _pick_orca(self):
        from PySide6.QtWidgets import QFileDialog
        d = QFileDialog.getExistingDirectory(self, "Select Orca presets directory", self._orca.text())
        if d:
            self._orca.setText(d)

    def _clear_recents(self):
        # Known recents keys to clear
        keys = (
            "gcode_preview/recent_pdls",
            "gcode_preview/recent_vars",
            "gcode_validate/recent_pdls",
            "gcode_validate/recent_vars",
        )
        for k in keys:
            try:
                self.s.setValue(k, "[]")
            except Exception:
                pass

    def _reset_defaults(self):
        try:
            self._orca.setText("")
        except Exception:
            pass

    @property
    def orca_preset_dir(self) -> str:
        return self._orca.text().strip()
