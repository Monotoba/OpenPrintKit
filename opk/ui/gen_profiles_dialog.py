from __future__ import annotations
import json
from pathlib import Path
from ._qt_compat import (
    QDialog, QFormLayout, QLineEdit, QPushButton, QHBoxLayout, QComboBox, QFileDialog, QMessageBox, QCheckBox, QTextEdit, QVBoxLayout, QLabel
)
from ..core.project import find_project_file, load_project_config, merge_policies


class GenerateProfilesDialog(QDialog):
    def __init__(self, parent=None, pdl_data: dict | None = None):
        super().__init__(parent)
        self.setWindowTitle("Generate Slicer Profiles")
        self._pdl_data = pdl_data or None
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
        self.ck_bundle = QCheckBox("Bundle (Orca/Cura/Prusa/ideaMaker)")
        self.ed_bundle = QLineEdit(); self.ed_bundle.setPlaceholderText("OUT.orca_printer")
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
                QMessageBox.warning(self, "Generate", "Please select a valid PDL file.")
                return
            try:
                text = pdl_path.read_text(encoding="utf-8")
                data = json.loads(text) if pdl_path.suffix.lower()==".json" else __import__("yaml").safe_load(text)
            except Exception as e:
                QMessageBox.critical(self, "Generate", f"Failed to read PDL:\n{e}")
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
                if self.ck_bundle.isChecked() and self.ed_bundle.text().strip():
                    from ..core.bundle import build_bundle
                    bundle_path = Path(self.ed_bundle.text().strip())
                    build_bundle(out_dir, bundle_path)
                    self._show_bundle_summary(bundle_path)
            elif slicer == 'cura':
                from ..plugins.slicers.cura import generate_cura
                out = generate_cura(data or {}, out_dir)
                if self.ck_bundle.isChecked() and self.ed_bundle.text().strip():
                    from ..core.bundle import build_profile_bundle
                    bundle_path = Path(self.ed_bundle.text().strip())
                    build_profile_bundle(out, bundle_path, 'cura')
                    self._show_bundle_summary(bundle_path)
            elif slicer == 'prusa':
                from ..plugins.slicers.prusa import generate_prusa
                out = generate_prusa(data or {}, out_dir)
                if self.ck_bundle.isChecked() and self.ed_bundle.text().strip():
                    from ..core.bundle import build_profile_bundle
                    bundle_path = Path(self.ed_bundle.text().strip())
                    build_profile_bundle(out, bundle_path, 'prusa')
                    self._show_bundle_summary(bundle_path)
            elif slicer == 'ideamaker':
                from ..plugins.slicers.ideamaker import generate_ideamaker
                out = generate_ideamaker(data or {}, out_dir)
                if self.ck_bundle.isChecked() and self.ed_bundle.text().strip():
                    from ..core.bundle import build_profile_bundle
                    bundle_path = Path(self.ed_bundle.text().strip())
                    build_profile_bundle(out, bundle_path, 'ideamaker')
                    self._show_bundle_summary(bundle_path)
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
                self.sel = QComboBox(); self.view = QTextEdit(readOnly=True)
                lay.addWidget(QLabel("Select file:")); lay.addWidget(self.sel); lay.addWidget(self.view)
                for k, p in files:
                    self.sel.addItem(f"{k}: {p.name}", str(p))
                self.sel.currentIndexChanged.connect(self._load)
                self._load()

            def _load(self):
                try:
                    p = Path(self.sel.currentData() or "")
                    if p.exists():
                        self.view.setPlainText(p.read_text(encoding='utf-8'))
                except Exception:
                    pass

        _Preview(self, items).exec()
