from __future__ import annotations
from pathlib import Path
from ._qt_compat import (
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
    QApplication,
    QStyle,
    QColor,
    QIcon,
    QComboBox,
)
from ..core.io import load_json
from ..core.rules import validate_printer, validate_filament, validate_process, summarize


class RulesDialog(QDialog):
    def __init__(self, parent=None, last_dirs: dict | None = None):
        super().__init__(parent)
        self.setWindowTitle("Run Rules")
        self._last_dirs = last_dirs or {}
        self._build_ui()

    def _build_ui(self):
        lay = QVBoxLayout(self)
        # File selectors
        self._printer = QLineEdit(); btn_pr = QPushButton("…"); btn_pr.clicked.connect(lambda: self._pick(self._printer))
        self._filament = QLineEdit(); btn_fi = QPushButton("…"); btn_fi.clicked.connect(lambda: self._pick(self._filament))
        self._process = QLineEdit(); btn_ps = QPushButton("…"); btn_ps.clicked.connect(lambda: self._pick(self._process))
        for label, edit, btn in (("Printer", self._printer, btn_pr), ("Filament", self._filament, btn_fi), ("Process", self._process, btn_ps)):
            row = QHBoxLayout(); row.addWidget(QLabel(label)); row.addWidget(edit); row.addWidget(btn); lay.addLayout(row)

        # Controls row (Run + Path filter)
        controls = QHBoxLayout()
        btn_run = QPushButton("Run"); btn_run.clicked.connect(self._run); controls.addWidget(btn_run)
        controls.addStretch(1)
        # Path-only filter
        controls.addWidget(QLabel("Path:"))
        self._path_filter = QComboBox(); self._path_filter.addItems(["ALL"])  # populated after Run
        try:
            self._path_filter.currentIndexChanged.connect(lambda *_: self._render_rows())
        except Exception:
            pass
        controls.addWidget(self._path_filter)
        # Text filter
        controls.addWidget(QLabel("Filter:"))
        self._text_filter = QLineEdit(); self._text_filter.setPlaceholderText("path or message contains…")
        try:
            self._text_filter.textChanged.connect(lambda *_: self._render_rows())
        except Exception:
            pass
        controls.addWidget(self._text_filter)
        lay.addLayout(controls)

        # Results table
        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(["Level", "Target", "Path", "Message"])
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        lay.addWidget(self._table)

    def _pick(self, edit: QLineEdit):
        start = self._last_dirs.get("rules", "")
        fn, _ = QFileDialog.getOpenFileName(self, "Pick JSON", start, "JSON (*.json)")
        if fn:
            self._last_dirs["rules"] = str(Path(fn).parent)
            edit.setText(fn)

    def _run(self):
        pr = self._printer.text().strip()
        fi = self._filament.text().strip()
        ps = self._process.text().strip()
        prd = load_json(pr) if pr else {}
        fid = load_json(fi) if fi else {}
        psd = load_json(ps) if ps else {}
        ip = validate_printer(prd) if prd else []
        ifi = validate_filament(fid) if fid else []
        ips = validate_process(psd, prd if prd else None) if psd else []
        rows = []
        for target, issues in (("printer", ip), ("filament", ifi), ("process", ips)):
            for i in issues:
                rows.append((i.level, target, i.path, i.message))
        self._rows = rows
        # Populate path filter options dynamically (unique path prefixes)
        try:
            # Extract simple prefixes (before first dot or '[')
            def _prefix(p: str) -> str:
                if not p:
                    return ''
                cut = len(p)
                for ch in ('.', '['):
                    idx = p.find(ch)
                    if idx != -1:
                        cut = min(cut, idx)
                return p[:cut] if cut > 0 else p
            opts = sorted({ _prefix(path) for _, _, path, _ in rows if path })
            items = ["ALL"] + [o for o in opts if o]
            self._path_filter.blockSignals(True)
            self._path_filter.clear(); self._path_filter.addItems(items)
            self._path_filter.blockSignals(False)
        except Exception:
            pass
        self._render_rows()

    def _populate(self, rows):
        self._table.setRowCount(0)
        style = QApplication.style()
        for r, (level, target, path, msg) in enumerate(rows):
            self._table.insertRow(r)
            for c, text in enumerate((level.upper(), target, path, msg)):
                item = QTableWidgetItem(text)
                if c == 0:
                    if level == "error":
                        item.setForeground(QColor("red"))
                        item.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxCritical))
                    elif level == "warn":
                        item.setForeground(QColor("darkorange"))
                        item.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning))
                    else:
                        item.setForeground(QColor("gray"))
                        item.setIcon(style.standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation))
                self._table.setItem(r, c, item)

    def _render_rows(self):
        rows = getattr(self, '_rows', [])
        try:
            prefix = (self._path_filter.currentText() or 'ALL').strip()
        except Exception:
            prefix = 'ALL'
        try:
            q = (self._text_filter.text() or '').strip().lower()
        except Exception:
            q = ''
        if prefix and prefix != 'ALL':
            rows = [(lvl, tgt, path, msg) for (lvl, tgt, path, msg) in rows if (path or '').startswith(prefix)]
        if q:
            rows = [(lvl, tgt, path, msg) for (lvl, tgt, path, msg) in rows if (q in (path or '').lower()) or (q in (msg or '').lower())]
        self._populate(rows)
