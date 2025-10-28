from __future__ import annotations
from PySide6.QtWidgets import QApplication,QMainWindow,QWidget,QVBoxLayout,QLabel,QPushButton,QFileDialog,QMessageBox
import sys
from ..core.io import load_json
from ..core import schema as S

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OpenPrintKit")
        w=QWidget(); lay=QVBoxLayout(w)
        lay.addWidget(QLabel("Validate an OPK profile or bundle."))
        btn=QPushButton("Validate profile…"); btn.clicked.connect(self._validate); lay.addWidget(btn)
        self.setCentralWidget(w)

    def _validate(self):
        fn,_=QFileDialog.getOpenFileName(self,"Open JSON","","JSON (*.json)")
        if not fn: return
        try:
            obj = load_json(fn)
            S.validate(obj.get("type"), obj)
        except Exception as e:
            QMessageBox.critical(self,"Validation",f"Failed:\n{e}")
        else:
            QMessageBox.information(self,"Validation","Looks good!")

def main():
    app=QApplication(sys.argv)
    m=MainWindow(); m.resize(640,360); m.show()
    sys.exit(app.exec())
