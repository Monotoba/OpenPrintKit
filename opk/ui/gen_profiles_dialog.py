from __future__ import annotations
import json
from pathlib import Path
from ._qt_compat import (
    QDialog, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QComboBox, QFileDialog, QMessageBox, QCheckBox, QTextEdit, QVBoxLayout, QLabel, QSettings
)
from ..core.project import find_project_file, load_project_config, merge_policies


class GenerateProfilesDialog(QDialog):
    def __init__(self, parent=None, pdl_data: dict | None = None):
        super().__init__(parent)
        self.setWindowTitle("Generate Slicer Profiles")
        self._pdl_data = pdl_data or None
        self.s = QSettings("OpenPrintKit", "OPKStudio")
        self._build()
        self._load_defaults()

    def _build(self):
        f = QFormLayout(self)
        self.ed_pdl = QLineEdit(); self.ed_pdl.setPlaceholderText("Select PDL (YAML/JSON)")
        b_pdl = QPushButton("…"); b_pdl.clicked.connect(self._pick_pdl)
        row_pdl = QHBoxLayout(); row_pdl.addWidget(self.ed_pdl); row_pdl.addWidget(b_pdl)
        self.cb_slicer = QComboBox(); self.cb_slicer.addItems(["orca","cura","prusa","ideamaker","bambu"]) 
        self.ed_out = QLineEdit(); self.ed_out.setPlaceholderText("Output directory")
        b_out = QPushButton("…"); b_out.clicked.connect(self._pick_out)
        row_out = QHBoxLayout(); row_out.addWidget(self.ed_out); row_out.addWidget(b_out)
        self.ck_bundle = QCheckBox("Bundle (Orca/Cura/Prusa/ideaMaker)")
        self.ed_bundle = QLineEdit(); self.ed_bundle.setPlaceholderText("OUT.orca_printer")
        # Toggle bundle path enablement and placeholder per slicer
        def _update_bundle_enabled():
            slicer = self.cb_slicer.currentText()
            bundlable = slicer in ("orca","cura","prusa","ideamaker")
            self.ck_bundle.setEnabled(bundlable)
            self.ed_bundle.setEnabled(bundlable and self.ck_bundle.isChecked())
            self.ed_bundle.setPlaceholderText("OUT.orca_printer" if slicer == 'orca' else "OUT.zip")
        self.ck_bundle.toggled.connect(lambda *_: _update_bundle_enabled())
        self.cb_slicer.currentIndexChanged.connect(lambda *_: _update_bundle_enabled())
        if self._pdl_data is None:
            f.addRow("PDL file", row_pdl)
        else:
            # Using in-memory PDL from editor
            self.ed_pdl.setText("[In-Editor]"); self.ed_pdl.setEnabled(False); b_pdl.setEnabled(False)
        f.addRow("Slicer", self.cb_slicer)
        f.addRow("Output dir", row_out)
        f.addRow(self.ck_bundle)
        f.addRow("Bundle output", self.ed_bundle)
        # Buttons
        btns = QHBoxLayout();
        prev = QPushButton("Preview…"); prev.clicked.connect(self._preview)
        go = QPushButton("Generate"); go.clicked.connect(self._gen)
        btns.addWidget(prev)
        cancel = QPushButton("Close"); cancel.clicked.connect(self.reject)
        btns.addWidget(go); btns.addWidget(cancel)
        f.addRow(btns)

    def _load_defaults(self):
        # Default slicer and remembered fields
        try:
            self.cb_slicer.setCurrentText(self.s.value("app/default_slicer", "orca"))
        except Exception:
            pass
        self.ed_out.setText(self.s.value("gen_profiles/out_dir", self.s.value("app/out_dir", "")))
        self.ed_bundle.setText(self.s.value("gen_profiles/bundle_path", ""))
        self.ck_bundle.setChecked(self.s.value("gen_profiles/bundle_enabled", True, type=bool))
        if self._pdl_data is None:
            self.ed_pdl.setText(self.s.value("gen_profiles/pdl_path", ""))
        # Sync enablement state
        try:
            self.cb_slicer.currentIndexChanged.emit(self.cb_slicer.currentIndex())  # type: ignore[attr-defined]
        except Exception:
            pass

    def _pick_pdl(self):
        fn, _ = QFileDialog.getOpenFileName(self, "Select PDL (YAML/JSON)", "", "PDL (*.yaml *.yml *.json)")
        if fn: self.ed_pdl.setText(fn)

    def _pick_out(self):
        d = QFileDialog.getExistingDirectory(self, "Select Output Directory", self.ed_out.text() or "")
        if d: self.ed_out.setText(d)

    def _gen(self):
        out_dir = Path(self.ed_out.text().strip() or ".")
        # Source PDL: prefer in-memory provided by editor
        data = None
        if isinstance(self._pdl_data, dict):
            data = dict(self._pdl_data)
        else:
            pdl_path = Path(self.ed_pdl.text().strip())
            if not pdl_path.exists():
                QMessageBox.warning(self, "Generate", "Please select a valid PDL file (YAML/JSON).")
                return
            try:
                text = pdl_path.read_text(encoding="utf-8")
                data = json.loads(text) if pdl_path.suffix.lower()==".json" else __import__("yaml").safe_load(text)
            except Exception as e:
                QMessageBox.critical(self, "Generate", f"Failed to read PDL at {pdl_path.name}:\n{e}")
                return
        try:
            src_dir = Path(".") if isinstance(self._pdl_data, dict) else pdl_path.parent
            proj = find_project_file(src_dir)
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
                if self.ck_bundle.isChecked():
                    from ..core.bundle import build_bundle
                    bundle_text = self.ed_bundle.text().strip()
                    if not bundle_text:
                        base = (Path(self.ed_pdl.text()).stem if not isinstance(self._pdl_data, dict) else (data.get('name') or 'opk')).replace(' ', '_')
                        bundle_text = str((out_dir / f"{base}.orca_printer"))
                        self.ed_bundle.setText(bundle_text)
                    bundle_path = Path(bundle_text)
                    if not bundle_path.suffix:
                        bundle_path = bundle_path.with_suffix('.orca_printer')
                    bundle_path.parent.mkdir(parents=True, exist_ok=True)
                    build_bundle(out_dir, bundle_path)
                    self._show_bundle_summary(bundle_path)
            elif slicer == 'cura':
                from ..plugins.slicers.cura import generate_cura
                out = generate_cura(data or {}, out_dir)
                if self.ck_bundle.isChecked():
                    from ..core.bundle import build_profile_bundle
                    bundle_text = self.ed_bundle.text().strip()
                    if not bundle_text:
                        base = (Path(self.ed_pdl.text()).stem if not isinstance(self._pdl_data, dict) else (data.get('name') or 'opk')).replace(' ', '_')
                        bundle_text = str((out_dir / f"{base}_cura.zip"))
                        self.ed_bundle.setText(bundle_text)
                    bundle_path = Path(bundle_text)
                    if not bundle_path.suffix:
                        bundle_path = bundle_path.with_suffix('.zip')
                    bundle_path.parent.mkdir(parents=True, exist_ok=True)
                    build_profile_bundle(out, bundle_path, 'cura')
                    self._show_bundle_summary(bundle_path)
            elif slicer == 'prusa':
                from ..plugins.slicers.prusa import generate_prusa
                out = generate_prusa(data or {}, out_dir)
                if self.ck_bundle.isChecked():
                    from ..core.bundle import build_profile_bundle
                    bundle_text = self.ed_bundle.text().strip()
                    if not bundle_text:
                        base = (Path(self.ed_pdl.text()).stem if not isinstance(self._pdl_data, dict) else (data.get('name') or 'opk')).replace(' ', '_')
                        bundle_text = str((out_dir / f"{base}_prusa.zip"))
                        self.ed_bundle.setText(bundle_text)
                    bundle_path = Path(bundle_text)
                    if not bundle_path.suffix:
                        bundle_path = bundle_path.with_suffix('.zip')
                    bundle_path.parent.mkdir(parents=True, exist_ok=True)
                    build_profile_bundle(out, bundle_path, 'prusa')
                    self._show_bundle_summary(bundle_path)
            elif slicer == 'ideamaker':
                from ..plugins.slicers.ideamaker import generate_ideamaker
                out = generate_ideamaker(data or {}, out_dir)
                if self.ck_bundle.isChecked():
                    from ..core.bundle import build_profile_bundle
                    bundle_text = self.ed_bundle.text().strip()
                    if not bundle_text:
                        base = (Path(self.ed_pdl.text()).stem if not isinstance(self._pdl_data, dict) else (data.get('name') or 'opk')).replace(' ', '_')
                        bundle_text = str((out_dir / f"{base}_ideamaker.zip"))
                        self.ed_bundle.setText(bundle_text)
                    bundle_path = Path(bundle_text)
                    if not bundle_path.suffix:
                        bundle_path = bundle_path.with_suffix('.zip')
                    bundle_path.parent.mkdir(parents=True, exist_ok=True)
                    build_profile_bundle(out, bundle_path, 'ideamaker')
                    self._show_bundle_summary(bundle_path)
            elif slicer == 'bambu':
                from ..plugins.slicers.bambu import generate_bambu
                out = generate_bambu(data or {}, out_dir)
            else:
                out = {}
        except Exception as e:
            QMessageBox.critical(self, "Generate", f"Failed to generate profiles for '{slicer}':\n{e}")
            return
        # Persist last-used state
        try:
            self.s.setValue("gen_profiles/out_dir", str(out_dir))
            self.s.setValue("gen_profiles/bundle_enabled", self.ck_bundle.isChecked())
            if self.ed_bundle.text().strip():
                self.s.setValue("gen_profiles/bundle_path", self.ed_bundle.text().strip())
            if self._pdl_data is None:
                self.s.setValue("gen_profiles/pdl_path", self.ed_pdl.text().strip())
        except Exception:
            pass
        QMessageBox.information(self, "Generate", f"Wrote {len(out)} file(s) to:\n{out_dir}")
        self.accept()

    def _show_bundle_summary(self, path: Path) -> None:
        # Open bundle and show manifest, with option to open folder
        info = []
        try:
            import zipfile, json
            with zipfile.ZipFile(path, 'r') as zf:
                if 'manifest.json' in zf.namelist():
                    manifest = json.loads(zf.read('manifest.json').decode('utf-8'))
                    if manifest.get('slicer'):
                        info.append(f"slicer: {manifest.get('slicer')}")
                    if 'files' in manifest:
                        info.append(f"files: {', '.join(manifest['files'])}")
                    if 'printer_count' in manifest:
                        info.append(f"printers: {manifest['printer_count']} filaments: {manifest['filament_count']} processes: {manifest['process_count']}")
        except Exception:
            pass
        msg = f"Bundle written:\n{path}\n\n" + ("\n".join(info) if info else "")
        box = QMessageBox(self)
        box.setWindowTitle("Bundle Summary")
        box.setText(msg)
        open_btn = box.addButton("Open Folder", QMessageBox.ButtonRole.ActionRole)
        box.addButton("Close", QMessageBox.ButtonRole.RejectRole)
        box.exec()
        if box.clickedButton() == open_btn:
            try:
                # Try to open folder in OS file manager
                from PySide6.QtGui import QDesktopServices
                from PySide6.QtCore import QUrl
                QDesktopServices.openUrl(QUrl.fromLocalFile(str(path.parent)))
            except Exception:
                pass

    def _preview(self):
        # Generate to a temporary directory and show the generated file(s)
        import tempfile
        out_dir = Path(self.ed_out.text().strip() or ".")
        # Source PDL same logic as _gen
        data = None
        if isinstance(self._pdl_data, dict):
            data = dict(self._pdl_data)
        else:
            pdl_path = Path(self.ed_pdl.text().strip())
            if not pdl_path.exists():
                QMessageBox.warning(self, "Preview", "Please select a valid PDL file.")
                return
            try:
                text = pdl_path.read_text(encoding="utf-8")
                data = json.loads(text) if pdl_path.suffix.lower()==".json" else __import__("yaml").safe_load(text)
            except Exception as e:
                QMessageBox.critical(self, "Preview", f"Failed to read PDL:\n{e}")
                return
        try:
            src_dir = Path(".")
            proj = find_project_file(src_dir)
            if proj:
                data = merge_policies(data or {}, load_project_config(proj))
        except Exception:
            pass
        slicer = self.cb_slicer.currentText()
        try:
            with tempfile.TemporaryDirectory() as td:
                tdp = Path(td)
                if slicer == 'orca':
                    from ..plugins.slicers.orca import generate_orca
                    out = generate_orca(data or {}, tdp)
                elif slicer == 'cura':
                    from ..plugins.slicers.cura import generate_cura
                    out = generate_cura(data or {}, tdp)
                elif slicer == 'prusa':
                    from ..plugins.slicers.prusa import generate_prusa
                    out = generate_prusa(data or {}, tdp)
                elif slicer == 'ideamaker':
                    from ..plugins.slicers.ideamaker import generate_ideamaker
                    out = generate_ideamaker(data or {}, tdp)
                elif slicer == 'bambu':
                    from ..plugins.slicers.bambu import generate_bambu
                    out = generate_bambu(data or {}, tdp)
                else:
                    out = {}
                items = [(k, Path(p)) for k, p in out.items() if Path(p).exists()]
                if not items:
                    QMessageBox.information(self, "Preview", "No files generated.")
                    return
        except Exception as e:
            QMessageBox.critical(self, "Preview", f"Failed to generate preview:\n{e}")
            return
        # Show text in a simple viewer with file selector
        class _Preview(QDialog):
            def __init__(self, parent, files: list[tuple[str, Path]]):
                super().__init__(parent)
                self.setWindowTitle("Generated Profile Preview")
                lay = QVBoxLayout(self)
                self.sel = QComboBox(); self.meta = QLabel(); self.view = QTextEdit(readOnly=True)
                lay.addWidget(QLabel("Select file:")); lay.addWidget(self.sel); lay.addWidget(self.meta); lay.addWidget(self.view)
                for k, p in files:
                    self.sel.addItem(f"{k}: {p.name}", str(p))
                self.sel.currentIndexChanged.connect(self._load)
                self._load()

            def _load(self):
                try:
                    p = Path(self.sel.currentData() or "")
                    if p.exists():
                        try:
                            sz = p.stat().st_size
                            mtime = p.stat().st_mtime
                            import datetime
                            ts = datetime.datetime.fromtimestamp(mtime)
                            self.meta.setText(f"{p.name} — {sz} bytes — modified {ts:%Y-%m-%d %H:%M:%S}")
                        except Exception:
                            self.meta.setText(p.name)
                        self.view.setPlainText(p.read_text(encoding='utf-8'))
                except Exception:
                    pass

        _Preview(self, items).exec()
