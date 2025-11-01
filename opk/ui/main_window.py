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
from PySide6.QtWidgets import QStyle

from ..core.io import load_json
from ..core import schema as S
from ..core.bundle import build_bundle
from .rules_dialog import RulesDialog
from .install_wizard import InstallWizard
from .gcode_preview_dialog import GcodePreviewDialog
from .gcode_validate_dialog import GcodeValidateDialog
from PySide6.QtCore import QSettings
from .preferences_dialog import PreferencesDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OpenPrintKit")
        self.settings = QSettings("OpenPrintKit", "OPKStudio")
        self._init_ui()
        # Restore geometry/state
        if (geo := self.settings.value("window/geometry")):
            self.restoreGeometry(geo)
        if (state := self.settings.value("window/state")):
            self.restoreState(state)

    def _init_ui(self):
        w = QWidget(); lay = QVBoxLayout(w)
        self.log_view = QPlainTextEdit(readOnly=True)
        self.log_view.setPlaceholderText("Logs will appear here…")
        lay.addWidget(self.log_view)
        self.setCentralWidget(w)
        self.setAcceptDrops(True)
        self.statusBar().showMessage("Ready")

        # Menus
        mb = self.menuBar()
        file_menu = mb.addMenu("File")

        style = self.style()
        act_validate = QAction(style.standardIcon(QStyle.StandardPixmap.SP_DialogApplyButton), "Validate…", self); act_validate.triggered.connect(self._validate)
        act_rules = QAction(style.standardIcon(QStyle.StandardPixmap.SP_BrowserReload), "Run Rules…", self); act_rules.triggered.connect(self._rules)
        act_bundle = QAction(style.standardIcon(QStyle.StandardPixmap.SP_DirIcon), "Build Bundle…", self); act_bundle.triggered.connect(self._bundle)
        act_ws_init = QAction(style.standardIcon(QStyle.StandardPixmap.SP_FileDialogNewFolder), "Workspace Init…", self); act_ws_init.triggered.connect(self._workspace_init)
        act_install = QAction(style.standardIcon(QStyle.StandardPixmap.SP_ArrowDown), "Install to Orca…", self); act_install.triggered.connect(self._install)
        act_exit = QAction("Exit", self); act_exit.triggered.connect(self.close)

        for a in (act_validate, act_rules, act_bundle, act_ws_init, act_install):
            file_menu.addAction(a)
        file_menu.addSeparator(); file_menu.addAction(act_exit)

        # Toolbar
        tb = self.addToolBar("Main")
        tb.addAction(act_validate)
        tb.addAction(act_rules)
        tb.addAction(act_bundle)
        tb.addAction(act_ws_init)
        tb.addAction(act_install)

        tools_menu = mb.addMenu("Tools")
        act_gcode_prev = QAction("G-code Preview…", self); act_gcode_prev.triggered.connect(self._gcode_preview)
        act_gcode_validate = QAction("Validate Hook Variables…", self); act_gcode_validate.triggered.connect(self._gcode_validate)
        tools_menu.addAction(act_gcode_prev)
        tools_menu.addAction(act_gcode_validate)

        help_menu = mb.addMenu("Help")
        act_about = QAction("About", self); act_about.triggered.connect(self._about)
        help_menu.addAction(act_about)

        # Preferences under File menu
        file_menu.addSeparator()
        act_prefs = QAction("Preferences…", self); act_prefs.triggered.connect(self._preferences)
        file_menu.addAction(act_prefs)

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
        last_dirs = {
            "rules": self.settings.value("dirs/rules", "")
        }
        dlg = RulesDialog(self, last_dirs=last_dirs)
        dlg.exec()
        # persist directory
        self.settings.setValue("dirs/rules", last_dirs.get("rules", ""))

    def _bundle(self):
        start = self.settings.value("dirs/src", "")
        src = QFileDialog.getExistingDirectory(self, "Select Source Directory (with printers/ filaments/ processes/)", start)
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
            self.settings.setValue("dirs/src", src)

    def _workspace_init(self):
        start = self.settings.value("dirs/ws", "")
        root = QFileDialog.getExistingDirectory(self, "Select Workspace Directory (will be created if missing)", start)
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
            self.settings.setValue("dirs/ws", root)

    def _install(self):
        last_dirs = {
            "install_src": self.settings.value("dirs/install_src", ""),
            "install_dst": self.settings.value("dirs/install_dst", ""),
        }
        # default to stored Orca preset path if present
        if not last_dirs["install_dst"]:
            last_dirs["install_dst"] = self.settings.value("paths/orca_preset", "")
        dlg = InstallWizard(self, last_dirs=last_dirs)
        dlg.exec()
        self.settings.setValue("dirs/install_src", last_dirs.get("install_src", ""))
        self.settings.setValue("dirs/install_dst", last_dirs.get("install_dst", ""))
        if last_dirs.get("install_dst"):
            self.settings.setValue("paths/orca_preset", last_dirs.get("install_dst"))

    def _preferences(self):
        current = self.settings.value("paths/orca_preset", "")
        dlg = PreferencesDialog(self, orca_preset_dir=current)
        if dlg.exec():
            self.settings.setValue("paths/orca_preset", dlg.orca_preset_dir)
            self.log(f"[PREFS] Orca presets set to: {dlg.orca_preset_dir}")

    def _gcode_preview(self):
        dlg = GcodePreviewDialog(self)
        dlg.resize(700, 600)
        dlg.exec()

    def _gcode_validate(self):
        dlg = GcodeValidateDialog(self)
        dlg.resize(700, 500)
        dlg.exec()

    # Drag & drop validation
    def dragEnterEvent(self, e):
        if any(url.toLocalFile().endswith(".json") for url in e.mimeData().urls() or []):
            e.acceptProposedAction()
        else:
            e.ignore()

    def dropEvent(self, e):
        paths = [url.toLocalFile() for url in e.mimeData().urls() or [] if url.toLocalFile().endswith(".json")]
        if not paths:
            e.ignore(); return
        ok = True
        for fn in paths:
            try:
                obj = load_json(fn)
                S.validate(obj.get("type"), obj)
            except Exception as ex:
                ok = False
                self.log(f"[FAIL] {Path(fn).name}: {ex}")
            else:
                self.log(f"[ OK ] {Path(fn).name}")
        e.acceptProposedAction()
        if ok:
            self.statusBar().showMessage("Validation succeeded", 3000)
        else:
            self.statusBar().showMessage("Validation had failures", 3000)

    def _about(self):
        QMessageBox.information(self, "About OpenPrintKit", "OpenPrintKit — Validate, bundle, and manage printer profiles.")


def main():
    app = QApplication(sys.argv)
    m = MainWindow(); m.resize(800, 480); m.show()
    ret = app.exec()
    # Save window state
    m.settings.setValue("window/geometry", m.saveGeometry())
    m.settings.setValue("window/state", m.saveState())
    sys.exit(ret)
