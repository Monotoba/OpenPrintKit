from __future__ import annotations
from pathlib import Path
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QMessageBox,
)
from ..core.install import plan_install, perform_install


class InstallWizard(QDialog):
    def __init__(self, parent=None, last_dirs: dict | None = None):
        super().__init__(parent)
        self.setWindowTitle("Install to Orca Presets")
        self._last_dirs = last_dirs or {}
        self._ops = []
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        # Source and destination
        self._src = QLineEdit(); btn_src = QPushButton("…"); btn_src.clicked.connect(lambda: self._pick_dir(self._src, "install_src"))
        self._dst = QLineEdit(); btn_dst = QPushButton("…"); btn_dst.clicked.connect(lambda: self._pick_dir(self._dst, "install_dst"))
        for label, edit, btn in (("Source (profiles)", self._src, btn_src), ("Destination (Orca presets)", self._dst, btn_dst)):
            row = QHBoxLayout(); row.addWidget(QLabel(label)); row.addWidget(edit); row.addWidget(btn); lay.addLayout(row)

        # Actions
        row2 = QHBoxLayout()
        btn_dry = QPushButton("Dry Run"); btn_dry.clicked.connect(self._dry_run); row2.addWidget(btn_dry)
        btn_install = QPushButton("Install…"); btn_install.clicked.connect(self._install); row2.addWidget(btn_install)
        lay.addLayout(row2)

        # Plan table
        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["Status", "Category", "Name", "Destination"]) 
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        lay.addWidget(self._table)

    def _pick_dir(self, edit: QLineEdit, key: str):
        start = self._last_dirs.get(key, "")
        d = QFileDialog.getExistingDirectory(self, "Select Directory", start)
        if d:
            self._last_dirs[key] = d
            edit.setText(d)

    def _dry_run(self):
        src = self._src.text().strip(); dst = self._dst.text().strip()
        if not src or not dst:
            QMessageBox.warning(self, "Install", "Please select both source and destination directories.")
            return
        self._ops = plan_install(Path(src), Path(dst))
        self._populate(self._ops)
        if not self._ops:
            QMessageBox.information(self, "Install", "No files found to install.")

    def _populate(self, ops):
        self._table.setRowCount(0)
        for r, op in enumerate(ops):
            self._table.insertRow(r)
            for c, text in enumerate((op.status.upper(), op.category, op.name, str(op.dest))):
                self._table.setItem(r, c, QTableWidgetItem(text))

    def _install(self):
        if not self._ops:
            QMessageBox.warning(self, "Install", "Run Dry Run first to compute the plan.")
            return
        # Choose backup zip path
        backup, _ = QFileDialog.getSaveFileName(self, "Backup overwritten files as…", "backup_orca_presets.zip", "Zip (*.zip)")
        if not backup:
            # allow install without backup
            res = perform_install(self._ops, backup_zip=None)
        else:
            res = perform_install(self._ops, backup_zip=Path(backup))
        QMessageBox.information(self, "Install", f"Install complete. Written: {res['written']}, Skipped: {res['skipped']}")

