from __future__ import annotations
from pathlib import Path
from PySide6.QtWidgets import QDialog, QVBoxLayout, QTextEdit, QMessageBox


CONTENT_FALLBACK = """
Machine-Control M-Codes Reference

Power: M80, M81, M18/M84, M112, M999
Lighting/IO: M42, M43, M355, M150, M380/M381, M710/M711
Fans/Chamber: M106, M107, M141, M191
Filament/Servo: M280, M282, M300, M600, M701/M702, M125
Probe/Endstops: M119, M420, M851, M401/M402, M48
Comm: M115, M117, M118, M21/M22, M928/M29
Camera: M240, M42, M118
Heaters/Safety: M140/M190, M104/M109, M141/M191, M144, M303, M108
Diagnostics: M122, M503, M500/M501/M502, M105

Refer to the repository docs (docs/mcode-reference.md) for details.
""".strip()


class McodeReferenceDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("M-code Reference")
        lay = QVBoxLayout(self)
        self.view = QTextEdit(readOnly=True)
        lay.addWidget(self.view)
        self._load_content()

    def _load_content(self):
        # Try repo docs path
        candidates = [
            Path(__file__).resolve().parents[2] / "docs" / "mcode-reference.md",
            Path(__file__).resolve().parents[3] / "docs" / "mcode-reference.md",
        ]
        for p in candidates:
            try:
                if p.exists():
                    self.view.setPlainText(p.read_text(encoding="utf-8"))
                    return
            except Exception:
                pass
        self.view.setPlainText(CONTENT_FALLBACK)

