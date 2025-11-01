from __future__ import annotations
import sys
import json
from pathlib import Path
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QPlainTextEdit,
    QFileDialog,
    QMessageBox,
    QAction,
)
from PySide6.QtGui import QIcon

from ..core.io import load_json
from ..core import schema as S
from ..core.bundle import build_bundle


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OpenPrintKit")
        self._init_ui()

    def _init_ui(self):
        w = QWidget(); lay = QVBoxLayout(w)
        self.log_view = QPlainTextEdit(readOnly=True)
        self.log_view.setPlaceholderText("Logs will appear here…")
        lay.addWidget(self.log_view)
        self.setCentralWidget(w)

        # Menus
        mb = self.menuBar()
        file_menu = mb.addMenu("File")

        act_validate = QAction("Validate…", self); act_validate.triggered.connect(self._validate)
        act_rules = QAction("Run Rules…", self); act_rules.triggered.connect(self._rules)
        act_bundle = QAction("Build Bundle…", self); act_bundle.triggered.connect(self._bundle)
        act_ws_init = QAction("Workspace Init…", self); act_ws_init.triggered.connect(self._workspace_init)
        act_exit = QAction("Exit", self); act_exit.triggered.connect(self.close)

        for a in (act_validate, act_rules, act_bundle, act_ws_init):
            file_menu.addAction(a)
        file_menu.addSeparator(); file_menu.addAction(act_exit)

        help_menu = mb.addMenu("Help")
        act_about = QAction("About", self); act_about.triggered.connect(self._about)
        help_menu.addAction(act_about)

    # Utilities
    def log(self, msg: str) -> None:
        self.log_view.appendPlainText(msg)

    # Actions
    def _validate(self):
        fns, _ = QFileDialog.getOpenFileNames(self, "Open JSON", "", "JSON (*.json)")
        if not fns:
            return
        ok = True
        for fn in fns:
            try:
                obj = load_json(fn)
                S.validate(obj.get("type"), obj)
            except Exception as e:
                ok = False
                self.log(f"[FAIL] {Path(fn).name}: {e}")
            else:
                self.log(f"[ OK ] {Path(fn).name}")
        if ok:
            QMessageBox.information(self, "Validation", "All files validated successfully.")
        else:
            QMessageBox.warning(self, "Validation", "Some files failed validation. See log.")

    def _rules(self):
        # Prompt for each file; user can cancel to skip any category
        pr, _ = QFileDialog.getOpenFileName(self, "Select Printer JSON (optional)", "", "JSON (*.json)")
        fi, _ = QFileDialog.getOpenFileName(self, "Select Filament JSON (optional)", "", "JSON (*.json)")
        ps, _ = QFileDialog.getOpenFileName(self, "Select Process JSON (optional)", "", "JSON (*.json)")
        from ..core.rules import validate_printer, validate_filament, validate_process, summarize
        prd = load_json(pr) if pr else {}
        fid = load_json(fi) if fi else {}
        psd = load_json(ps) if ps else {}
        ip = validate_printer(prd) if prd else []
        ifi = validate_filament(fid) if fid else []
        ips = validate_process(psd, prd if prd else None) if psd else []
        for label, issues in (("printer", ip), ("filament", ifi), ("process", ips)):
            for i in issues:
                self.log(f"[{i.level.upper():5}] {label}:{i.path} — {i.message}")
        s = summarize(ip, ifi, ips)
        self.log(f"[SUMMARY] errors={s['error']} warns={s['warn']} infos={s['info']} total={s['total']}")
        if s["error"]:
            QMessageBox.warning(self, "Rules", "Completed with errors. See log.")
        else:
            QMessageBox.information(self, "Rules", "No rule errors detected.")

    def _bundle(self):
        src = QFileDialog.getExistingDirectory(self, "Select Source Directory (with printers/ filaments/ processes/)")
        if not src:
            return
        out, _ = QFileDialog.getSaveFileName(self, "Save Bundle As", "", "OPK Bundle (*.orca_printer)")
        if not out:
            return
        outp = Path(out)
        if not outp.suffix:
            outp = outp.with_suffix(".orca_printer")
        try:
            build_bundle(Path(src), outp)
        except Exception as e:
            self.log(f"[BUNDLE] Failed: {e}")
            QMessageBox.critical(self, "Bundle", f"Failed to build bundle:\n{e}")
        else:
            self.log(f"[BUNDLE] Wrote {outp}")
            QMessageBox.information(self, "Bundle", f"Wrote: {outp}")

    def _workspace_init(self):
        root = QFileDialog.getExistingDirectory(self, "Select Workspace Directory (will be created if missing)")
        if not root:
            return
        from ..workspace.scaffold import init_workspace
        try:
            p = init_workspace(Path(root), with_examples=True)
        except Exception as e:
            self.log(f"[WS] Init failed: {e}")
            QMessageBox.critical(self, "Workspace", f"Init failed:\n{e}")
        else:
            self.log(f"[WS] Initialized at {p}")
            QMessageBox.information(self, "Workspace", f"Initialized at:\n{p}")

    def _about(self):
        QMessageBox.information(self, "About OpenPrintKit", "OpenPrintKit — Validate, bundle, and manage printer profiles.")


def main():
    app = QApplication(sys.argv)
    m = MainWindow(); m.resize(800, 480); m.show()
    sys.exit(app.exec())
