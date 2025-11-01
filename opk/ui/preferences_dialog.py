from __future__ import annotations
from ._qt_compat import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QFileDialog


class PreferencesDialog(QDialog):
    def __init__(self, parent=None, orca_preset_dir: str = ""):
        super().__init__(parent)
        self.setWindowTitle("Preferences")
        self._orca = QLineEdit(orca_preset_dir)
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        row = QHBoxLayout()
        row.addWidget(QLabel("Orca presets directory"))
        row.addWidget(self._orca)
        pick = QPushButton("…"); pick.clicked.connect(self._pick_orca)
        row.addWidget(pick)
        lay.addLayout(row)

        btns = QHBoxLayout()
        ok = QPushButton("Save"); ok.clicked.connect(self.accept); btns.addWidget(ok)
        cancel = QPushButton("Cancel"); cancel.clicked.connect(self.reject); btns.addWidget(cancel)
        lay.addLayout(btns)

    def _pick_orca(self):
        from PySide6.QtWidgets import QFileDialog
        d = QFileDialog.getExistingDirectory(self, "Select Orca presets directory", self._orca.text())
        if d:
            self._orca.setText(d)

    @property
    def orca_preset_dir(self) -> str:
        return self._orca.text().strip()
