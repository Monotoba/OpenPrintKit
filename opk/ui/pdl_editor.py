from __future__ import annotations
from typing import Dict, Any, List, Tuple
from pathlib import Path
from PySide6.QtWidgets import (
    QWidget, QTabWidget, QFormLayout, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QDoubleSpinBox, QSpinBox, QComboBox, QCheckBox, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QTextEdit, QGroupBox
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
        self._init_filaments_tab()
        self._init_features_tab()
        self._init_machine_control_tab()
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

        # Bed shape polygon editor
        self.t_bedshape = QTableWidget(0, 2)
        self.t_bedshape.setHorizontalHeaderLabels(["X","Y"])
        self.t_bedshape.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        bs_btns = QHBoxLayout()
        bs_add = QPushButton("Add Point"); bs_add.clicked.connect(self._add_bed_point)
        bs_del = QPushButton("Remove Point"); bs_del.clicked.connect(self._del_bed_point)
        bs_rect = QPushButton("Make Rectangle from Width/Depth"); bs_rect.clicked.connect(self._bed_make_rect)
        bs_btns.addWidget(bs_add); bs_btns.addWidget(bs_del); bs_btns.addWidget(bs_rect); bs_btns.addStretch(1)

        # Limits group
        limits = QGroupBox("Limits")
        lim_form = QFormLayout(limits)
        self.l_print_speed = QDoubleSpinBox(); self.l_print_speed.setRange(1, 1000)
        self.l_travel_speed = QDoubleSpinBox(); self.l_travel_speed.setRange(1, 2000)
        self.l_accel = QDoubleSpinBox(); self.l_accel.setRange(1, 50000)
        self.l_jerk = QDoubleSpinBox(); self.l_jerk.setRange(0, 200)
        lim_form.addRow("Print Speed Max (mm/s)", self.l_print_speed)
        lim_form.addRow("Travel Speed Max (mm/s)", self.l_travel_speed)
        lim_form.addRow("Acceleration Max (mm/s²)", self.l_accel)
        lim_form.addRow("Jerk Max (mm/s)", self.l_jerk)

        form.addRow("PDL Version", self.f_pdl_version)
        form.addRow("ID", self.f_id)
        form.addRow("Name", self.f_name)
        form.addRow("Firmware", self.f_firmware)
        form.addRow("Kinematics", self.f_kinematics)
        form.addRow("Width (X)", self.f_width)
        form.addRow("Depth (Y)", self.f_depth)
        form.addRow("Z Height", self.f_z)
        form.addRow("Origin", self.f_origin)
        form.addRow(QLabel("Bed Shape (polygon)"))
        form.addRow(self.t_bedshape)
        form.addRow(bs_btns)
        form.addRow(limits)
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
        self.f_probe_active_low = QCheckBox()
        # Endstops group
        es = QGroupBox("Endstops Polarity (Active Low)")
        es_form = QFormLayout(es)
        self.es_x_min = QCheckBox(); self.es_x_max = QCheckBox()
        self.es_y_min = QCheckBox(); self.es_y_max = QCheckBox()
        self.es_z_min = QCheckBox(); self.es_z_max = QCheckBox()
        es_form.addRow("X Min", self.es_x_min)
        es_form.addRow("X Max", self.es_x_max)
        es_form.addRow("Y Min", self.es_y_min)
        es_form.addRow("Y Max", self.es_y_max)
        es_form.addRow("Z Min", self.es_z_min)
        es_form.addRow("Z Max", self.es_z_max)
        form.addRow("Auto Bed Leveling", self.f_abl)
        form.addRow("Probe Type", self.f_probe_type)
        form.addRow("Mesh Size (R)", self.f_mesh_r)
        form.addRow("Mesh Size (C)", self.f_mesh_c)
        form.addRow("Probe Active Low", self.f_probe_active_low)
        form.addRow(es)
        self.tabs.addTab(w, "Features")

    # ---------- Machine Control (M-codes helper) ----------
    def _init_machine_control_tab(self):
        w = QWidget(); form = QFormLayout(w)
        # PSU and Lights
        self.mc_psu_on_start = QCheckBox(); self.mc_psu_off_end = QCheckBox()
        self.mc_light_on_start = QCheckBox(); self.mc_light_off_end = QCheckBox()
        # RGB color at start
        row_rgb = QHBoxLayout();
        self.mc_rgb_r = QSpinBox(); self.mc_rgb_r.setRange(0,255); self.mc_rgb_r.setPrefix("R:")
        self.mc_rgb_g = QSpinBox(); self.mc_rgb_g.setRange(0,255); self.mc_rgb_g.setPrefix(" G:")
        self.mc_rgb_b = QSpinBox(); self.mc_rgb_b.setRange(0,255); self.mc_rgb_b.setPrefix(" B:")
        row_rgb.addWidget(self.mc_rgb_r); row_rgb.addWidget(self.mc_rgb_g); row_rgb.addWidget(self.mc_rgb_b)
        # Chamber temperature
        row_cht = QHBoxLayout();
        self.mc_chamber_temp = QDoubleSpinBox(); self.mc_chamber_temp.setRange(0,120); self.mc_chamber_temp.setSuffix(" °C")
        self.mc_chamber_wait = QCheckBox("Wait")
        row_cht.addWidget(self.mc_chamber_temp); row_cht.addWidget(self.mc_chamber_wait)
        # Mesh enable and Z offset
        self.mc_enable_mesh = QCheckBox()
        self.mc_z_offset = QDoubleSpinBox(); self.mc_z_offset.setRange(-5,5); self.mc_z_offset.setSingleStep(0.01); self.mc_z_offset.setPrefix("Z:")
        # Custom M-codes
        self.mc_start_custom = QTextEdit(); self.mc_start_custom.setPlaceholderText("; Custom M-codes at start\nM117 Starting…")
        self.mc_end_custom = QTextEdit(); self.mc_end_custom.setPlaceholderText("; Custom M-codes at end\nM117 Done")

        form.addRow("PSU ON at start (M80)", self.mc_psu_on_start)
        form.addRow("PSU OFF at end (M81)", self.mc_psu_off_end)
        form.addRow("Light ON at start (M355)", self.mc_light_on_start)
        form.addRow("Light OFF at end (M355)", self.mc_light_off_end)
        form.addRow("RGB at start (M150)", row_rgb)
        form.addRow("Chamber temp at start (M141/M191)", row_cht)
        form.addRow("Enable mesh at start (M420 S1)", self.mc_enable_mesh)
        form.addRow("Probe Z offset (M851)", self.mc_z_offset)
        form.addRow(QLabel("Custom start M-codes"), self.mc_start_custom)
        form.addRow(QLabel("Custom end M-codes"), self.mc_end_custom)
        self.tabs.addTab(w, "Machine Control")

    # ---------- Filaments ----------
    def _init_filaments_tab(self):
        w = QWidget(); v = QVBoxLayout(w)
        self.t_filaments = QTableWidget(0, 9)
        self.t_filaments.setHorizontalHeaderLabels([
            "Name","Type","Dia","Nozzle °C","Bed °C","Retract Len","Retract Spd","Fan %","Color"
        ])
        self.t_filaments.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        v.addWidget(self.t_filaments)
        row = QHBoxLayout()
        btn_add = QPushButton("Add"); btn_add.clicked.connect(self._add_filament)
        btn_del = QPushButton("Remove"); btn_del.clicked.connect(self._del_filament)
        row.addWidget(btn_add); row.addWidget(btn_del); row.addStretch(1)
        v.addLayout(row)
        self.tabs.addTab(w, "Filaments")

    def _add_filament(self):
        r = self.t_filaments.rowCount(); self.t_filaments.insertRow(r)
        defaults = ["PLA","PLA","1.75","205","60","0.8","40","100","#FFFFFF"]
        for c in range(9):
            item = QTableWidgetItem("")
            self.t_filaments.setItem(r, c, item)
        # Set some defaults
        self.t_filaments.item(r,0).setText(defaults[0])
        self.t_filaments.item(r,1).setText(defaults[1])
        self.t_filaments.item(r,2).setText(defaults[2])
        self.t_filaments.item(r,3).setText(defaults[3])
        self.t_filaments.item(r,4).setText(defaults[4])
        self.t_filaments.item(r,5).setText(defaults[5])
        self.t_filaments.item(r,6).setText(defaults[6])
        self.t_filaments.item(r,7).setText(defaults[7])
        self.t_filaments.item(r,8).setText(defaults[8])

    def _del_filament(self):
        rows = sorted({i.row() for i in self.t_filaments.selectedItems()}, reverse=True)
        for r in rows:
            self.t_filaments.removeRow(r)

    # ---------- G-code (Start/End) ----------
    def _init_gcode_tab(self):
        w = QWidget(); outer = QVBoxLayout(w)

        # Hook categories and fields (explicit hooks)
        self.g_edits: Dict[str, QTextEdit] = {}
        hook_tabs = QTabWidget()
        categories = {
            "Lifecycle": [
                "start","end","on_abort","pause","resume","power_loss_resume","auto_shutdown"
            ],
            "Layers": [
                "before_layer_change","layer_change","after_layer_change","top_layer_start","bottom_layer_start"
            ],
            "Tools & Filament": [
                "before_tool_change","tool_change","after_tool_change","filament_change"
            ],
            "Objects & Regions": [
                "before_object","after_object","before_region","after_region","support_interface_start","support_interface_end"
            ],
            "Motion": [
                "retraction","unretraction","travel_start","travel_end","bridge_start","bridge_end"
            ],
            "Temperature & Env": [
                "before_heating","after_heating","before_cooling"
            ],
            "Monitoring & Timelapse": [
                "on_progress_percent","on_layer_interval","on_time_interval","before_snapshot","after_snapshot"
            ],
        }
        for cat, fields in categories.items():
            pg = QWidget(); fl = QFormLayout(pg)
            for f in fields:
                ed = QTextEdit(); ed.setPlaceholderText("; one command per line")
                self.g_edits[f] = ed
                fl.addRow(f.replace('_',' ').title(), ed)
            hook_tabs.addTab(pg, cat)
        outer.addWidget(hook_tabs)

        # Macros table (name + script)
        outer.addWidget(QLabel("Macros (name → sequence)"))
        self.t_macros = QTableWidget(0, 2)
        self.t_macros.setHorizontalHeaderLabels(["Name","Script (one command per line)"])
        self.t_macros.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.t_macros.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        outer.addWidget(self.t_macros)
        rowm = QHBoxLayout();
        m_add = QPushButton("Add Macro"); m_add.clicked.connect(self._add_macro)
        m_del = QPushButton("Remove Macro"); m_del.clicked.connect(self._del_macro)
        rowm.addWidget(m_add); rowm.addWidget(m_del); rowm.addStretch(1)
        outer.addLayout(rowm)

        # Additional hooks (free-form gcode.hooks map)
        outer.addWidget(QLabel("Additional Hooks (gcode.hooks)"))
        self.t_hooks = QTableWidget(0, 2)
        self.t_hooks.setHorizontalHeaderLabels(["Hook Name","Script (one command per line)"])
        self.t_hooks.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.t_hooks.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        outer.addWidget(self.t_hooks)
        rowh = QHBoxLayout();
        h_add = QPushButton("Add Hook"); h_add.clicked.connect(self._add_hook)
        h_del = QPushButton("Remove Hook"); h_del.clicked.connect(self._del_hook)
        rowh.addWidget(h_add); rowh.addWidget(h_del); rowh.addStretch(1)
        outer.addLayout(rowh)

        self.tabs.addTab(w, "G-code")

    def _add_macro(self):
        r = self.t_macros.rowCount(); self.t_macros.insertRow(r)
        self.t_macros.setItem(r, 0, QTableWidgetItem("macro_name"))
        te = QTextEdit(); te.setPlaceholderText("G92 E0\nG1 E10 F300")
        self.t_macros.setCellWidget(r, 1, te)

    def _del_macro(self):
        rows = sorted({i.row() for i in self.t_macros.selectedItems()}, reverse=True)
        for r in rows:
            self.t_macros.removeRow(r)

    def _add_hook(self):
        r = self.t_hooks.rowCount(); self.t_hooks.insertRow(r)
        self.t_hooks.setItem(r, 0, QTableWidgetItem("monitor.progress_25"))
        te = QTextEdit(); te.setPlaceholderText("M117 25%")
        self.t_hooks.setCellWidget(r, 1, te)

    def _del_hook(self):
        rows = sorted({i.row() for i in self.t_hooks.selectedItems()}, reverse=True)
        for r in rows:
            self.t_hooks.removeRow(r)

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
        # Bed shape default rectangle
        self.t_bedshape.setRowCount(0)
        self._bed_make_rect()
        self.f_abl.setChecked(False)
        self.f_probe_type.setCurrentIndex(0)
        self.f_mesh_r.setValue(7); self.f_mesh_c.setValue(7)
        # Clear all explicit gcode hooks
        if hasattr(self, 'g_edits'):
            for ed in self.g_edits.values():
                ed.setPlainText("")
        # Clear macros and additional hooks tables
        if hasattr(self, 't_macros'):
            self.t_macros.setRowCount(0)
        if hasattr(self, 't_hooks'):
            self.t_hooks.setRowCount(0)
        # Machine control defaults
        if hasattr(self, 'mc_psu_on_start'):
            self.mc_psu_on_start.setChecked(False)
            self.mc_psu_off_end.setChecked(False)
            self.mc_light_on_start.setChecked(False)
            self.mc_light_off_end.setChecked(False)
            self.mc_rgb_r.setValue(0); self.mc_rgb_g.setValue(0); self.mc_rgb_b.setValue(0)
            self.mc_chamber_temp.setValue(0); self.mc_chamber_wait.setChecked(False)
            self.mc_enable_mesh.setChecked(False)
            self.mc_z_offset.setValue(0)
            self.mc_start_custom.setPlainText("")
            self.mc_end_custom.setPlainText("")

    def load_pdl(self, data: Dict[str, Any]) -> None:
        self._data = data
        g = data
        self.f_pdl_version.setText(str(g.get("pdl_version", "1.0")))
        self.f_id.setText(g.get("id", ""))
        self.f_name.setText(g.get("name", ""))
        fw = (g.get("firmware") or "marlin").lower(); self.f_firmware.setCurrentIndex(max(0, FIRMWARES.index(fw) if fw in FIRMWARES else 0))
        km = (g.get("kinematics") or "cartesian").lower(); self.f_kinematics.setCurrentIndex(max(0, KINEMATICS.index(km) if km in KINEMATICS else 0))
        geom = g.get("geometry") or {}
        bed = geom.get("bed_shape") or rect_to_bed_shape(220, 220)
        w, d = bed_shape_to_rect(bed)
        self.f_width.setValue(float(w)); self.f_depth.setValue(float(d))
        self.f_z.setValue(float(geom.get("z_height") or 250))
        self.f_origin.setText(geom.get("origin") or "front_left")
        # Populate bed shape table
        self.t_bedshape.setRowCount(0)
        for pt in bed:
            r = self.t_bedshape.rowCount(); self.t_bedshape.insertRow(r)
            self.t_bedshape.setItem(r, 0, QTableWidgetItem(str(pt[0])))
            self.t_bedshape.setItem(r, 1, QTableWidgetItem(str(pt[1])))

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
        self.f_probe_active_low.setChecked(bool(pr.get("active_low") or False))
        # Endstops
        es = g.get("endstops") or {}
        self.es_x_min.setChecked(bool(es.get("x_min_active_low") or False))
        self.es_x_max.setChecked(bool(es.get("x_max_active_low") or False))
        self.es_y_min.setChecked(bool(es.get("y_min_active_low") or False))
        self.es_y_max.setChecked(bool(es.get("y_max_active_low") or False))
        self.es_z_min.setChecked(bool(es.get("z_min_active_low") or False))
        self.es_z_max.setChecked(bool(es.get("z_max_active_low") or False))

        # G-code explicit hooks
        gc = g.get("gcode") or {}
        for key, ed in self.g_edits.items():
            ed.setPlainText("\n".join(gc.get(key) or []))
        # Macros
        self.t_macros.setRowCount(0)
        for name, seq in (gc.get("macros") or {}).items():
            r = self.t_macros.rowCount(); self.t_macros.insertRow(r)
            self.t_macros.setItem(r, 0, QTableWidgetItem(name))
            te = QTextEdit(); te.setPlainText("\n".join(seq or []))
            self.t_macros.setCellWidget(r, 1, te)
        # Additional hooks
        self.t_hooks.setRowCount(0)
        for name, seq in (gc.get("hooks") or {}).items():
            r = self.t_hooks.rowCount(); self.t_hooks.insertRow(r)
            self.t_hooks.setItem(r, 0, QTableWidgetItem(name))
            te = QTextEdit(); te.setPlainText("\n".join(seq or []))
            self.t_hooks.setCellWidget(r, 1, te)
        # Machine control: infer checkboxes from start/end
        start_seq = gc.get("start") or []
        end_seq = gc.get("end") or []
        def _has(prefix, seq):
            return any(str(s).strip().upper().startswith(prefix) for s in seq)
        self.mc_psu_on_start.setChecked(_has("M80", start_seq))
        self.mc_psu_off_end.setChecked(_has("M81", end_seq))
        self.mc_light_on_start.setChecked(_has("M355 S1", start_seq))
        self.mc_light_off_end.setChecked(_has("M355 S0", end_seq))
        # RGB M150 R,G,B
        import re
        m150 = next((s for s in start_seq if str(s).strip().upper().startswith("M150")), None)
        if m150:
            nums = {k:int(v) for k,v in re.findall(r"([RUB])\s*(\d+)", m150, flags=re.I)}
            self.mc_rgb_r.setValue(nums.get('R',0)); self.mc_rgb_g.setValue(nums.get('U',0)); self.mc_rgb_b.setValue(nums.get('B',0))
        # Chamber
        m141 = next((s for s in start_seq if str(s).strip().upper().startswith("M141")), None)
        if m141:
            m = re.search(r"S\s*(\d+)", m141, flags=re.I)
            if m:
                self.mc_chamber_temp.setValue(float(m.group(1)))
        self.mc_chamber_wait.setChecked(_has("M191", start_seq))
        # Mesh enable
        self.mc_enable_mesh.setChecked(any(s.strip().upper().startswith("M420 S1") for s in start_seq))
        # Z offset
        m851 = next((s for s in start_seq if str(s).strip().upper().startswith("M851")), None)
        if m851:
            m = re.search(r"Z\s*(-?\d+(?:\.\d+)?)", m851, flags=re.I)
            if m:
                try: self.mc_z_offset.setValue(float(m.group(1)))
                except Exception: pass

        # Limits
        lim = g.get("limits") or {}
        if isinstance(lim, dict):
            try: self.l_print_speed.setValue(float(lim.get("print_speed_max") or 0))
            except Exception: pass
            try: self.l_travel_speed.setValue(float(lim.get("travel_speed_max") or 0))
            except Exception: pass
            try: self.l_accel.setValue(float(lim.get("acceleration_max") or 0))
            except Exception: pass
            try: self.l_jerk.setValue(float(lim.get("jerk_max") or 0))
            except Exception: pass

        # Filaments/Materials
        self.t_filaments.setRowCount(0)
        for m in g.get("materials") or []:
            r = self.t_filaments.rowCount(); self.t_filaments.insertRow(r)
            vals = [
                str(m.get("name") or ""),
                str(m.get("filament_type") or ""),
                str(m.get("filament_diameter") or ""),
                str(m.get("nozzle_temperature") or ""),
                str(m.get("bed_temperature") or ""),
                str(m.get("retraction_length") or ""),
                str(m.get("retraction_speed") or ""),
                str(m.get("fan_speed") or ""),
                str(m.get("color_hex") or (m.get("color") or "")),
            ]
            for c, val in enumerate(vals):
                self.t_filaments.setItem(r, c, QTableWidgetItem(val))

    def dump_pdl(self) -> Dict[str, Any]:
        g: Dict[str, Any] = {}
        g["pdl_version"] = self.f_pdl_version.text().strip() or "1.0"
        g["id"] = self.f_id.text().strip()
        g["name"] = self.f_name.text().strip()
        g["firmware"] = self.f_firmware.currentText()
        g["kinematics"] = self.f_kinematics.currentText()
        # Bed shape: prefer explicit table points if present and >=3, else rectangle
        bed_pts = []
        for r in range(self.t_bedshape.rowCount()):
            try:
                x = float(self.t_bedshape.item(r,0).text()) if self.t_bedshape.item(r,0) else None
                y = float(self.t_bedshape.item(r,1).text()) if self.t_bedshape.item(r,1) else None
                if x is None or y is None:
                    continue
                bed_pts.append([x, y])
            except Exception:
                continue
        if len(bed_pts) < 3:
            bed_pts = rect_to_bed_shape(self.f_width.value(), self.f_depth.value())

        g["geometry"] = {
            "bed_shape": bed_pts,
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
        feat["probe"] = {"type": self.f_probe_type.currentText(), "mesh_size": [self.f_mesh_r.value(), self.f_mesh_c.value()], "active_low": self.f_probe_active_low.isChecked()}
        g["features"] = feat

        # G-code explicit hooks (stored as-is; generators will consume)
        gcode_out: Dict[str, Any] = {}
        for key, ed in self.g_edits.items():
            lines = [ln for ln in ed.toPlainText().splitlines() if ln.strip()]
            if lines:
                gcode_out[key] = lines
        # Macros
        macros: Dict[str, List[str]] = {}
        for r in range(self.t_macros.rowCount()):
            name = self.t_macros.item(r,0).text().strip() if self.t_macros.item(r,0) else ""
            te = self.t_macros.cellWidget(r,1)
            seq = [ln for ln in (te.toPlainText() if isinstance(te, QTextEdit) else "").splitlines() if ln.strip()]
            if name and seq:
                macros[name] = seq
        if macros:
            gcode_out["macros"] = macros
        # Additional hooks
        hooks_map: Dict[str, List[str]] = {}
        for r in range(self.t_hooks.rowCount()):
            name = self.t_hooks.item(r,0).text().strip() if self.t_hooks.item(r,0) else ""
            te = self.t_hooks.cellWidget(r,1)
            seq = [ln for ln in (te.toPlainText() if isinstance(te, QTextEdit) else "").splitlines() if ln.strip()]
            if name and seq:
                hooks_map[name] = seq
        if hooks_map:
            gcode_out["hooks"] = hooks_map
        if gcode_out:
            g["gcode"] = gcode_out
        # Store Machine Control as structured PDL; generators translate to hooks
        mc: Dict[str, Any] = {
            "psu_on_start": self.mc_psu_on_start.isChecked(),
            "psu_off_end": self.mc_psu_off_end.isChecked(),
            "light_on_start": self.mc_light_on_start.isChecked(),
            "light_off_end": self.mc_light_off_end.isChecked(),
            "rgb_start": {"r": self.mc_rgb_r.value(), "g": self.mc_rgb_g.value(), "b": self.mc_rgb_b.value()},
            "chamber": {"temp": self.mc_chamber_temp.value(), "wait": self.mc_chamber_wait.isChecked()},
            "enable_mesh_start": self.mc_enable_mesh.isChecked(),
            "z_offset": self.mc_z_offset.value(),
            "start_custom": [ln for ln in self.mc_start_custom.toPlainText().splitlines() if ln.strip()],
            "end_custom": [ln for ln in self.mc_end_custom.toPlainText().splitlines() if ln.strip()],
        }
        # Remove empty/defaults
        if not any((mc["psu_on_start"], mc["light_on_start"], mc["enable_mesh_start"], mc["z_offset"], mc["start_custom"])) and not any((mc["psu_off_end"], mc["light_off_end"], mc["end_custom"])) and not any((mc["rgb_start"][k] for k in ("r","g","b"))) and not mc["chamber"]["temp"]:
            pass
        else:
            g["machine_control"] = mc

        # Limits
        lim_out: Dict[str, Any] = {}
        if self.l_print_speed.value(): lim_out["print_speed_max"] = self.l_print_speed.value()
        if self.l_travel_speed.value(): lim_out["travel_speed_max"] = self.l_travel_speed.value()
        if self.l_accel.value(): lim_out["acceleration_max"] = self.l_accel.value()
        if self.l_jerk.value(): lim_out["jerk_max"] = self.l_jerk.value()
        if lim_out:
            g["limits"] = lim_out

        # Materials (Filaments)
        mats: List[Dict[str, Any]] = []
        for r in range(self.t_filaments.rowCount()):
            def _txt(c):
                it = self.t_filaments.item(r, c); return it.text().strip() if it else ""
            name = _txt(0); ftype = _txt(1)
            if not name and not ftype:
                continue
            entry: Dict[str, Any] = {
                "name": name,
                "filament_type": ftype or "Other",
            }
            # numeric optionals
            try: entry["filament_diameter"] = float(_txt(2) or 0)
            except Exception: pass
            try: entry["nozzle_temperature"] = float(_txt(3) or 0)
            except Exception: pass
            try: entry["bed_temperature"] = float(_txt(4) or 0)
            except Exception: pass
            try: entry["retraction_length"] = float(_txt(5) or 0)
            except Exception: pass
            try: entry["retraction_speed"] = float(_txt(6) or 0)
            except Exception: pass
            try: entry["fan_speed"] = float(_txt(7) or 0)
            except Exception: pass
            color = _txt(8)
            if color:
                if color.startswith('#') or len(color) == 6:
                    entry["color_hex"] = color
                else:
                    entry["color"] = color
            mats.append(entry)
        if mats:
            g["materials"] = mats
        # Endstops
        es_out: Dict[str, Any] = {
            "x_min_active_low": self.es_x_min.isChecked(),
            "x_max_active_low": self.es_x_max.isChecked(),
            "y_min_active_low": self.es_y_min.isChecked(),
            "y_max_active_low": self.es_y_max.isChecked(),
            "z_min_active_low": self.es_z_min.isChecked(),
            "z_max_active_low": self.es_z_max.isChecked(),
        }
        if any(es_out.values()):
            g["endstops"] = es_out
        return g

    # --- Helpers for Bed Shape editor
    def _add_bed_point(self):
        r = self.t_bedshape.rowCount(); self.t_bedshape.insertRow(r)
        self.t_bedshape.setItem(r, 0, QTableWidgetItem("0"))
        self.t_bedshape.setItem(r, 1, QTableWidgetItem("0"))

    def _del_bed_point(self):
        rows = sorted({i.row() for i in self.t_bedshape.selectedItems()}, reverse=True)
        for r in rows:
            self.t_bedshape.removeRow(r)

    def _bed_make_rect(self):
        w = self.f_width.value(); d = self.f_depth.value()
        pts = rect_to_bed_shape(w, d)
        self.t_bedshape.setRowCount(0)
        for x, y in pts:
            r = self.t_bedshape.rowCount(); self.t_bedshape.insertRow(r)
            self.t_bedshape.setItem(r, 0, QTableWidgetItem(str(x)))
            self.t_bedshape.setItem(r, 1, QTableWidgetItem(str(y)))
