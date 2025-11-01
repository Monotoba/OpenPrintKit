from __future__ import annotations
import sys
import json
from pathlib import Path
# Qt imports with headless-safe fallback stubs to allow import on CI
try:  # pragma: no cover - exercised indirectly in CI
    from PySide6.QtWidgets import (
        QApplication,
        QMainWindow,
        QWidget,
        QVBoxLayout,
        QPlainTextEdit,
        QFileDialog,
        QMessageBox,
    )
    from PySide6.QtGui import QIcon, QAction
    from PySide6.QtWidgets import QStyle
    from PySide6.QtCore import QSettings
except Exception:  # ImportError or plugin issues — provide minimal stubs for import-only tests
    class QApplication:  # type: ignore
        def __init__(self, *a, **k): ...
        def screens(self): return []
        def platformName(self): return "headless"
        def exec(self): return 0

    class QMainWindow: ...  # type: ignore
    class QWidget: ...  # type: ignore
    class QVBoxLayout:  # type: ignore
        def __init__(self, *a, **k): ...
        def addWidget(self, *a, **k): ...

    class QPlainTextEdit:  # type: ignore
        def __init__(self, *a, **k): ...
        def setPlaceholderText(self, *a, **k): ...
        def appendPlainText(self, *a, **k): ...

    class QFileDialog:  # type: ignore
        @staticmethod
        def getOpenFileNames(*a, **k): return ([], None)
        @staticmethod
        def getSaveFileName(*a, **k): return ("", None)
        @staticmethod
        def getExistingDirectory(*a, **k): return ""

    class QMessageBox:  # type: ignore
        class StandardButton:
            Yes = 1; No = 0
        @staticmethod
        def information(*a, **k): ...
        @staticmethod
        def warning(*a, **k): ...
        @staticmethod
        def critical(*a, **k): ...
        @staticmethod
        def question(*a, **k): return QMessageBox.StandardButton.No

    class QIcon: ...  # type: ignore
    class QAction:  # type: ignore
        def __init__(self, *a, **k): ...
        class _Sig:  # simple signal stub
            def connect(self, *a, **k): ...
        @property
        def triggered(self): return QAction._Sig()

    class QStyle:  # type: ignore
        class StandardPixmap: ...

    class QSettings:  # type: ignore
        def __init__(self, *a, **k): self._d = {}
        def value(self, k, default=None): return self._d.get(k, default)
        def setValue(self, k, v): self._d[k] = v

from ..core.io import load_json
from ..core import schema as S
from ..core.bundle import build_bundle
from .preferences_dialog import PreferencesDialog
from .app_settings_dialog import AppSettingsDialog
from .pdl_editor import PDLForm


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
        # Central: tabbed editor + logs
        self.editor = PDLForm(self)
        self.log_view = QPlainTextEdit(readOnly=True)
        self.log_view.setPlaceholderText("Logs will appear here…")
        container = QTabWidgetWrap(self.editor, self.log_view)
        self.setCentralWidget(container)
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
        act_open_pdl = QAction("Open PDL…", self); act_open_pdl.triggered.connect(self._open_pdl)
        act_save_pdl = QAction("Save PDL As…", self); act_save_pdl.triggered.connect(self._save_pdl)

        for a in (act_open_pdl, act_save_pdl, act_validate, act_rules, act_bundle, act_ws_init, act_install):
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
        act_gen_snip = QAction("Generate Snippets…", self); act_gen_snip.triggered.connect(self._gen_snippets)
        act_gen_prof = QAction("Generate Profiles…", self); act_gen_prof.triggered.connect(self._gen_profiles)
        tools_menu.addAction(act_gcode_prev)
        tools_menu.addAction(act_gcode_validate)
        tools_menu.addAction(act_gen_snip)
        tools_menu.addAction(act_gen_prof)

        help_menu = mb.addMenu("Help")
        act_overview = QAction("Overview…", self); act_overview.triggered.connect(self._help_overview)
        help_menu.addAction(act_overview)
        act_gcode = QAction("G-code Help…", self); act_gcode.triggered.connect(self._help_gcode)
        help_menu.addAction(act_gcode)
        act_fwmap = QAction("Firmware Mapping…", self); act_fwmap.triggered.connect(self._help_fwmap)
        help_menu.addAction(act_fwmap)
        act_quick = QAction("Quickstart…", self); act_quick.triggered.connect(self._help_quickstart)
        help_menu.addAction(act_quick)
        act_cli = QAction("CLI Reference…", self); act_cli.triggered.connect(self._help_cli_reference)
        help_menu.addAction(act_cli)
        act_mref = QAction("M-code Reference…", self); act_mref.triggered.connect(self._mcode_ref)
        help_menu.addAction(act_mref)
        act_about = QAction("About", self); act_about.triggered.connect(self._about)
        help_menu.addAction(act_about)

        # Preferences under File menu
        file_menu.addSeparator()
        act_prefs = QAction("Preferences…", self); act_prefs.triggered.connect(self._preferences)
        file_menu.addAction(act_prefs)
        act_settings = QAction("Settings…", self); act_settings.triggered.connect(self._settings)
        file_menu.addAction(act_settings)

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
        from .rules_dialog import RulesDialog
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
        from .install_wizard import InstallWizard
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

    def _open_pdl(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Open PDL (YAML/JSON)", "", "PDL (*.yaml *.yml *.json)")
        if not fn:
            return
        import json, yaml
        p = Path(fn)
        data = json.loads(p.read_text(encoding="utf-8")) if p.suffix.lower()==".json" else yaml.safe_load(p.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            QMessageBox.warning(self, "Open PDL", "Invalid PDL file")
            return
        self.editor.load_pdl(data)
        self.log(f"[PDL] Loaded {fn}")

    def _save_pdl(self):
        fn, _ = QFileDialog.getSaveFileName(self, "Save PDL As", "", "YAML (*.yaml *.yml);;JSON (*.json)")
        if not fn:
            return
        import json, yaml
        obj = self.editor.dump_pdl()
        try:
            from ..core import schema as S
            S.validate("pdl", obj)
        except Exception as e:
            if QMessageBox.question(self, "PDL Validation", f"Validation failed:\n{e}\n\nSave anyway?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No) != QMessageBox.StandardButton.Yes:
                return
        p = Path(fn)
        if p.suffix.lower() == ".json":
            p.write_text(json.dumps(obj, indent=2), encoding="utf-8")
        else:
            p.write_text(yaml.safe_dump(obj, sort_keys=False), encoding="utf-8")
        self.log(f"[PDL] Saved {fn}")

    def _gcode_preview(self):
        from .gcode_preview_dialog import GcodePreviewDialog
        dlg = GcodePreviewDialog(self)
        dlg.resize(700, 600)
        dlg.exec()

    def _gcode_validate(self):
        from .gcode_validate_dialog import GcodeValidateDialog
        dlg = GcodeValidateDialog(self)
        dlg.resize(700, 500)
        dlg.exec()

    def _gen_snippets(self):
        from .gen_snippets_dialog import GenerateSnippetsDialog
        dlg = GenerateSnippetsDialog(self)
        dlg.resize(650, 200)
        dlg.exec()

    def _gen_profiles(self):
        from .gen_profiles_dialog import GenerateProfilesDialog
        dlg = GenerateProfilesDialog(self)
        dlg.resize(650, 240)
        dlg.exec()

    def _mcode_ref(self):
        from .mcode_reference_dialog import McodeReferenceDialog
        dlg = McodeReferenceDialog(self)
        dlg.resize(800, 600)
        dlg.exec()

    def _settings(self):
        dlg = AppSettingsDialog(self)
        dlg.resize(600, 400)
        dlg.exec()

    def _help_overview(self):
        from .mcode_reference_dialog import McodeReferenceDialog as _DocDlg
        dlg = _DocDlg(self)
        # reuse viewer to show docs/overview.md
        try:
            from pathlib import Path
            p = Path(__file__).resolve().parents[2] / "docs" / "overview.md"
            if p.exists():
                dlg.view.setPlainText(p.read_text(encoding="utf-8"))
            dlg.setWindowTitle("OPK Overview")
        except Exception:
            pass
        dlg.resize(800, 600)
        dlg.exec()

    def _help_gcode(self):
        from .mcode_reference_dialog import McodeReferenceDialog as _DocDlg
        dlg = _DocDlg(self)
        try:
            from pathlib import Path
            p = Path(__file__).resolve().parents[2] / "docs" / "gcode-help.md"
            if p.exists():
                dlg.view.setPlainText(p.read_text(encoding="utf-8"))
            dlg.setWindowTitle("G-code Help")
        except Exception:
            pass
        dlg.resize(800, 600)
        dlg.exec()

    def _help_fwmap(self):
        from .mcode_reference_dialog import McodeReferenceDialog as _DocDlg
        dlg = _DocDlg(self)
        try:
            from pathlib import Path
            p = Path(__file__).resolve().parents[2] / "docs" / "firmware-mapping.md"
            if p.exists():
                dlg.view.setPlainText(p.read_text(encoding="utf-8"))
            dlg.setWindowTitle("Firmware Mapping")
        except Exception:
            pass
        dlg.resize(800, 600)
        dlg.exec()

    def _help_quickstart(self):
        from .mcode_reference_dialog import McodeReferenceDialog as _DocDlg
        dlg = _DocDlg(self)
        try:
            from pathlib import Path
            p = Path(__file__).resolve().parents[2] / "docs" / "quickstart.md"
            if p.exists():
                dlg.view.setPlainText(p.read_text(encoding="utf-8"))
            dlg.setWindowTitle("Quickstart")
        except Exception:
            pass
        dlg.resize(800, 600)
        dlg.exec()

    def _help_cli_reference(self):
        from .mcode_reference_dialog import McodeReferenceDialog as _DocDlg
        dlg = _DocDlg(self)
        try:
            from pathlib import Path
            p = Path(__file__).resolve().parents[2] / "docs" / "cli-reference.md"
            if p.exists():
                dlg.view.setPlainText(p.read_text(encoding="utf-8"))
            dlg.setWindowTitle("CLI Reference")
        except Exception:
            pass
        dlg.resize(800, 600)
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
    import os
    try:
        app = QApplication(sys.argv)
    except Exception as e:
        print(f"[FATAL] Failed to start QApplication: {e}", file=sys.stderr)
        sys.exit(2)

    if os.environ.get("OPK_DEBUG"):
        try:
            print(f"[DEBUG] Qt platform={app.platformName()} screens={len(app.screens())}")
        except Exception as e:
            print(f"[DEBUG] Unable to query platform/screens: {e}")

    if not app.screens():
        print("[FATAL] No available screens/display. Check X11/Wayland or set QT_QPA_PLATFORM.", file=sys.stderr)
        sys.exit(3)

    m = MainWindow(); m.resize(800, 480); m.show()
    ret = app.exec()
    # Save window state
    m.settings.setValue("window/geometry", m.saveGeometry())
    m.settings.setValue("window/state", m.saveState())
    sys.exit(ret)


class QTabWidgetWrap(QWidget):
    def __init__(self, editor: QWidget, logs: QPlainTextEdit):
        super().__init__()
        from ._qt_compat import QTabWidget
        tabs = QTabWidget()
        tabs.addTab(editor, "PDL Editor")
        tabs.addTab(logs, "Logs")
        lay = QVBoxLayout(self)
        lay.addWidget(tabs)
