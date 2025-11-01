from __future__ import annotations

QT_OK = True

try:
    from PySide6.QtWidgets import (
        QApplication,
        QDialog,
        QFormLayout,
        QHBoxLayout,
        QHeaderView,
        QLabel,
        QLineEdit,
        QPlainTextEdit,
        QPushButton,
        QComboBox,
        QFileDialog,
        QMessageBox,
        QTableWidget,
        QTableWidgetItem,
        QTextEdit,
        QTabWidget,
        QWidget,
        QVBoxLayout,
        QCheckBox,
        QSpinBox,
        QDoubleSpinBox,
        QGroupBox,
        QStyle,
    )
    from PySide6.QtGui import QIcon, QColor
    from PySide6.QtCore import QSettings
except Exception:
    QT_OK = False

    class _Sig:
        def connect(self, *a, **k):
            pass

    class _Stub:
        def __init__(self, *a, **k):
            pass

        def __call__(self, *a, **k):
            return self

        def __getattr__(self, name):
            if name in ("clicked", "triggered"):
                return _Sig()

            def _noop(*a, **k):
                return None

            return _noop

    # Widgets/layouts
    QApplication = _Stub  # type: ignore
    QDialog = _Stub  # type: ignore
    QFormLayout = _Stub  # type: ignore
    QHBoxLayout = _Stub  # type: ignore
    QHeaderView = _Stub  # type: ignore
    QLabel = _Stub  # type: ignore
    QLineEdit = _Stub  # type: ignore
    QPlainTextEdit = _Stub  # type: ignore
    QPushButton = _Stub  # type: ignore
    QComboBox = _Stub  # type: ignore
    QFileDialog = _Stub  # type: ignore
    QMessageBox = _Stub  # type: ignore
    QTableWidget = _Stub  # type: ignore
    QTableWidgetItem = _Stub  # type: ignore
    QTextEdit = _Stub  # type: ignore
    QTabWidget = _Stub  # type: ignore
    QWidget = _Stub  # type: ignore
    QVBoxLayout = _Stub  # type: ignore
    QCheckBox = _Stub  # type: ignore
    QSpinBox = _Stub  # type: ignore
    QDoubleSpinBox = _Stub  # type: ignore
    QGroupBox = _Stub  # type: ignore

    class QStyle:  # type: ignore
        class StandardPixmap:
            pass

    class QIcon:  # type: ignore
        pass

    class QColor:  # type: ignore
        def __init__(self, *a, **k):
            pass

    class QSettings:  # type: ignore
        def __init__(self, *a, **k):
            self._d = {}

        def value(self, k, default=None, type=None):  # noqa: A002 - match Qt signature
            return self._d.get(k, default)

        def setValue(self, k, v):
            self._d[k] = v

