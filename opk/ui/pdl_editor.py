from __future__ import annotations
from typing import Dict, Any, List, Tuple
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QTabWidget, QFormLayout, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QDoubleSpinBox, QSpinBox, QComboBox, QCheckBox, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QTextEdit
)


FIRMWARES = ["marlin","klipper","reprap","rrf","smoothie","bambu","crealityos","other"]
KINEMATICS = ["cartesian","corexy","corexz","delta","scara","polar"]
PROBE_TYPES = ["inductive","bltouch","crt","strain_gauge","nozzle_contact","manual","other"]
NOZZLE_TYPES = ["brass","hardened_steel","stainless","ruby","tungsten","other"]
DRIVE_TYPES = ["direct","bowden","other"]


def rect_to_bed_shape(width: float, depth: float) -> List[List[float]]:
    return [[0.0, 0.0], [width, 0.0], [width, depth], [0.0, depth]]


def bed_shape_to_rect(shape: List[List[float]]) -> Tuple[float, float]:
    if not shape or len(shape) < 2:
        return 0.0, 0.0
    xs = [p[0] for p in shape]
    ys = [p[1] for p in shape]
    return max(xs) - min(xs), max(ys) - min(ys)


class PDLForm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._data: Dict[str, Any] = {}
        self.tabs = QTabWidget(self)
        lay = QVBoxLayout(self); lay.addWidget(self.tabs)

        self._init_build_area_tab()
        self._init_extruders_tab()
        self._init_multimaterial_tab()
        self._init_features_tab()
        self._init_gcode_tab()

        self.set_defaults()

    # ---------- Build Area ----------
    def _init_build_area_tab(self):
        w = QWidget(); form = QFormLayout(w)
        self.f_pdl_version = QLineEdit("1.0")
        self.f_id = QLineEdit()
        self.f_name = QLineEdit()
        self.f_firmware = QComboBox(); self.f_firmware.addItems(FIRMWARES)
        self.f_kinematics = QComboBox(); self.f_kinematics.addItems(KINEMATICS)
        self.f_width = QDoubleSpinBox(); self.f_width.setRange(10, 1000); self.f_width.setDecimals(1)
        self.f_depth = QDoubleSpinBox(); self.f_depth.setRange(10, 1000); self.f_depth.setDecimals(1)
        self.f_z = QDoubleSpinBox(); self.f_z.setRange(10, 1000); self.f_z.setDecimals(1)
        self.f_origin = QLineEdit("front_left")

        form.addRow("PDL Version", self.f_pdl_version)
        form.addRow("ID", self.f_id)
        form.addRow("Name", self.f_name)
        form.addRow("Firmware", self.f_firmware)
        form.addRow("Kinematics", self.f_kinematics)
        form.addRow("Width (X)", self.f_width)
        form.addRow("Depth (Y)", self.f_depth)
        form.addRow("Z Height", self.f_z)
        form.addRow("Origin", self.f_origin)
        self.tabs.addTab(w, "Build Area")

    # ---------- Extruders ----------
    def _init_extruders_tab(self):
        w = QWidget(); v = QVBoxLayout(w)
        self.t_extruders = QTableWidget(0, 6)
        self.t_extruders.setHorizontalHeaderLabels(["ID","Nozzle ⌀","Nozzle Type","Drive","Max Temp","Mixing Ch."])
        self.t_extruders.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        v.addWidget(self.t_extruders)
        row = QHBoxLayout();
        btn_add = QPushButton("Add"); btn_add.clicked.connect(self._add_extruder)
        btn_del = QPushButton("Remove"); btn_del.clicked.connect(self._del_extruder)
        row.addWidget(btn_add); row.addWidget(btn_del); row.addStretch(1)
        v.addLayout(row)
        self.tabs.addTab(w, "Extruders")

    def _add_extruder(self):
        r = self.t_extruders.rowCount(); self.t_extruders.insertRow(r)
        for c in range(6):
            self.t_extruders.setItem(r, c, QTableWidgetItem(""))
        # sensible defaults
        self.t_extruders.item(r,1).setText("0.4")
        self.t_extruders.item(r,2).setText(NOZZLE_TYPES[0])
        self.t_extruders.item(r,3).setText(DRIVE_TYPES[0])
        self.t_extruders.item(r,4).setText("300")
        self.t_extruders.item(r,5).setText("1")

    def _del_extruder(self):
        rows = sorted({i.row() for i in self.t_extruders.selectedItems()}, reverse=True)
        for r in rows:
            self.t_extruders.removeRow(r)

    # ---------- Multi-Material ----------
    def _init_multimaterial_tab(self):
        w = QWidget(); v = QVBoxLayout(w)
        self.t_banks = QTableWidget(0, 2)
        self.t_banks.setHorizontalHeaderLabels(["Name","Capacity"])
        self.t_banks.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        v.addWidget(self.t_banks)
        row = QHBoxLayout(); btn_add = QPushButton("Add"); btn_add.clicked.connect(self._add_bank)
        btn_del = QPushButton("Remove"); btn_del.clicked.connect(self._del_bank)
        row.addWidget(btn_add); row.addWidget(btn_del); row.addStretch(1)
        v.addLayout(row)
        self.tabs.addTab(w, "Multi-Material")

    def _add_bank(self):
        r = self.t_banks.rowCount(); self.t_banks.insertRow(r)
        self.t_banks.setItem(r, 0, QTableWidgetItem("AMS-1"))
        self.t_banks.setItem(r, 1, QTableWidgetItem("4"))

    def _del_bank(self):
        rows = sorted({i.row() for i in self.t_banks.selectedItems()}, reverse=True)
        for r in rows:
            self.t_banks.removeRow(r)

    # ---------- Features ----------
    def _init_features_tab(self):
        w = QWidget(); form = QFormLayout(w)
        self.f_abl = QCheckBox()
        self.f_probe_type = QComboBox(); self.f_probe_type.addItems(PROBE_TYPES)
        self.f_mesh_r = QSpinBox(); self.f_mesh_r.setRange(1, 20)
        self.f_mesh_c = QSpinBox(); self.f_mesh_c.setRange(1, 20)
        form.addRow("Auto Bed Leveling", self.f_abl)
        form.addRow("Probe Type", self.f_probe_type)
        form.addRow("Mesh Size (R)", self.f_mesh_r)
        form.addRow("Mesh Size (C)", self.f_mesh_c)
        self.tabs.addTab(w, "Features")

    # ---------- G-code (Start/End) ----------
    def _init_gcode_tab(self):
        w = QWidget(); v = QVBoxLayout(w)
        v.addWidget(QLabel("Start G-code"))
        self.g_start = QTextEdit(); self.g_start.setPlaceholderText("M104 S{nozzle}\nM140 S{bed}\nG28")
        v.addWidget(self.g_start)
        v.addWidget(QLabel("End G-code"))
        self.g_end = QTextEdit(); self.g_end.setPlaceholderText("M104 S0\nM140 S0\nM84")
        v.addWidget(self.g_end)
        self.tabs.addTab(w, "G-code")

    # ---------- Data IO ----------
    def set_defaults(self):
        self.f_id.setText("")
        self.f_name.setText("")
        self.f_firmware.setCurrentIndex(0)
        self.f_kinematics.setCurrentIndex(0)
        self.f_width.setValue(220.0)
        self.f_depth.setValue(220.0)
        self.f_z.setValue(250.0)
        self.f_origin.setText("front_left")
        self.t_extruders.setRowCount(0)
        self._add_extruder()
        self.t_banks.setRowCount(0)
        self.f_abl.setChecked(False)
        self.f_probe_type.setCurrentIndex(0)
        self.f_mesh_r.setValue(7); self.f_mesh_c.setValue(7)
        self.g_start.setPlainText("")
        self.g_end.setPlainText("")

    def load_pdl(self, data: Dict[str, Any]) -> None:
        self._data = data
        g = data
        self.f_pdl_version.setText(str(g.get("pdl_version", "1.0")))
        self.f_id.setText(g.get("id", ""))
        self.f_name.setText(g.get("name", ""))
        fw = (g.get("firmware") or "marlin").lower(); self.f_firmware.setCurrentIndex(max(0, FIRMWARES.index(fw) if fw in FIRMWARES else 0))
        km = (g.get("kinematics") or "cartesian").lower(); self.f_kinematics.setCurrentIndex(max(0, KINEMATICS.index(km) if km in KINEMATICS else 0))
        geom = g.get("geometry") or {}
        w, d = bed_shape_to_rect(geom.get("bed_shape") or rect_to_bed_shape(220, 220))
        self.f_width.setValue(float(w)); self.f_depth.setValue(float(d))
        self.f_z.setValue(float(geom.get("z_height") or 250))
        self.f_origin.setText(geom.get("origin") or "front_left")

        # Extruders
        self.t_extruders.setRowCount(0)
        for ex in g.get("extruders") or []:
            r = self.t_extruders.rowCount(); self.t_extruders.insertRow(r)
            for c in range(6):
                self.t_extruders.setItem(r, c, QTableWidgetItem(""))
            self.t_extruders.item(r,0).setText(str(ex.get("id") or ""))
            self.t_extruders.item(r,1).setText(str(ex.get("nozzle_diameter") or ""))
            self.t_extruders.item(r,2).setText(str(ex.get("nozzle_type") or ""))
            self.t_extruders.item(r,3).setText(str(ex.get("drive") or ""))
            self.t_extruders.item(r,4).setText(str(ex.get("max_nozzle_temperature") or ""))
            self.t_extruders.item(r,5).setText(str(ex.get("mixing_channels") or "1"))

        # Multi-material
        self.t_banks.setRowCount(0)
        mm = g.get("multi_material") or {}
        for b in mm.get("spool_banks") or []:
            r = self.t_banks.rowCount(); self.t_banks.insertRow(r)
            self.t_banks.setItem(r, 0, QTableWidgetItem(str(b.get("name") or "")))
            self.t_banks.setItem(r, 1, QTableWidgetItem(str(b.get("capacity") or "")))

        # Features
        feat = g.get("features") or {}
        self.f_abl.setChecked(bool(feat.get("auto_bed_leveling") or False))
        pr = feat.get("probe") or {}
        pt = (pr.get("type") or PROBE_TYPES[0]).lower()
        self.f_probe_type.setCurrentIndex(max(0, PROBE_TYPES.index(pt) if pt in PROBE_TYPES else 0))
        mesh = pr.get("mesh_size") or [7,7]
        self.f_mesh_r.setValue(int(mesh[0] if len(mesh) > 0 else 7))
        self.f_mesh_c.setValue(int(mesh[1] if len(mesh) > 1 else 7))

        # G-code
        gc = g.get("gcode") or {}
        self.g_start.setPlainText("\n".join(gc.get("start") or []))
        self.g_end.setPlainText("\n".join(gc.get("end") or []))

    def dump_pdl(self) -> Dict[str, Any]:
        g: Dict[str, Any] = {}
        g["pdl_version"] = self.f_pdl_version.text().strip() or "1.0"
        g["id"] = self.f_id.text().strip()
        g["name"] = self.f_name.text().strip()
        g["firmware"] = self.f_firmware.currentText()
        g["kinematics"] = self.f_kinematics.currentText()
        g["geometry"] = {
            "bed_shape": rect_to_bed_shape(self.f_width.value(), self.f_depth.value()),
            "z_height": self.f_z.value(),
            "origin": self.f_origin.text().strip() or "front_left",
        }
        # Extruders
        exs = []
        for r in range(self.t_extruders.rowCount()):
            exs.append({
                "id": (self.t_extruders.item(r,0).text() if self.t_extruders.item(r,0) else "") or None,
                "nozzle_diameter": float(self.t_extruders.item(r,1).text() or 0.4),
                "nozzle_type": (self.t_extruders.item(r,2).text() or "brass"),
                "drive": (self.t_extruders.item(r,3).text() or "direct"),
                "max_nozzle_temperature": float(self.t_extruders.item(r,4).text() or 300),
                "mixing_channels": int(self.t_extruders.item(r,5).text() or 1),
            })
        g["extruders"] = exs

        # Multi-material
        banks = []
        for r in range(self.t_banks.rowCount()):
            banks.append({
                "name": self.t_banks.item(r,0).text() if self.t_banks.item(r,0) else "",
                "capacity": int(self.t_banks.item(r,1).text() or 1)
            })
        g["multi_material"] = {"spool_banks": banks} if banks else {}

        # Features
        feat: Dict[str, Any] = {"auto_bed_leveling": self.f_abl.isChecked()}
        feat["probe"] = {"type": self.f_probe_type.currentText(), "mesh_size": [self.f_mesh_r.value(), self.f_mesh_c.value()]}
        g["features"] = feat

        # G-code
        g["gcode"] = {
            "start": [ln for ln in self.g_start.toPlainText().splitlines() if ln.strip()],
            "end": [ln for ln in self.g_end.toPlainText().splitlines() if ln.strip()],
        }
        return g

