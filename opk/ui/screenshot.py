from __future__ import annotations
from pathlib import Path
from typing import Iterable, List
import os


def _ensure_offscreen() -> None:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")


def _app():
    from PySide6.QtWidgets import QApplication
    _ensure_offscreen()
    return QApplication.instance() or QApplication([])


def _grab_widget(widget, out_path: Path, size=(1000, 700)) -> None:
    from PySide6.QtCore import QSize
    from PySide6.QtGui import QPixmap
    try:
        # Some widgets need an explicit size to render predictably
        if hasattr(widget, 'resize'):
            widget.resize(QSize(size[0], size[1]))
        widget.show()
        widget.raise_()  # type: ignore[attr-defined]
    except Exception:
        pass
    # Pump events and grab
    app = _app(); app.processEvents()
    try:
        pix: QPixmap = widget.grab()  # type: ignore
    except Exception:
        # Fallback render
        pix = QPixmap(size[0], size[1])
        pix.fill()
        try:
            widget.render(pix)  # type: ignore
        except Exception:
            pass
    out_path.parent.mkdir(parents=True, exist_ok=True)
    pix.save(str(out_path))


def capture(targets: Iterable[str], out_dir: Path) -> List[Path]:
    """Capture screenshots of key UI components.

    targets: sequence including any of 'main','rules','profiles','snippets','settings','preferences'
    out_dir: destination directory
    """
    app = _app()
    written: List[Path] = []
    try:
        if 'main' in targets:
            from .main_window import MainWindow
            mw = MainWindow(); _grab_widget(mw, out_dir / 'main_window.png')
            written.append(out_dir / 'main_window.png')
        if 'rules' in targets:
            from .rules_dialog import RulesDialog
            dlg = RulesDialog(None, last_dirs={}); _grab_widget(dlg, out_dir / 'rules_dialog.png', size=(900, 600))
            written.append(out_dir / 'rules_dialog.png')
        if 'profiles' in targets:
            from .gen_profiles_dialog import GenerateProfilesDialog
            dlg = GenerateProfilesDialog(None, pdl_data={}); _grab_widget(dlg, out_dir / 'generate_profiles.png', size=(800, 520))
            written.append(out_dir / 'generate_profiles.png')
        if 'snippets' in targets:
            from .gen_snippets_dialog import GenerateSnippetsDialog
            dlg = GenerateSnippetsDialog(None); _grab_widget(dlg, out_dir / 'generate_snippets.png', size=(720, 320))
            written.append(out_dir / 'generate_snippets.png')
        if 'settings' in targets:
            from .app_settings_dialog import AppSettingsDialog
            dlg = AppSettingsDialog(None); _grab_widget(dlg, out_dir / 'app_settings.png', size=(760, 520))
            written.append(out_dir / 'app_settings.png')
        if 'preferences' in targets:
            from .preferences_dialog import PreferencesDialog
            dlg = PreferencesDialog(None, orca_preset_dir=""); _grab_widget(dlg, out_dir / 'preferences.png', size=(560, 260))
            written.append(out_dir / 'preferences.png')
    finally:
        try:
            app.processEvents()
        except Exception:
            pass
    return written

