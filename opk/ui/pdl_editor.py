from __future__ import annotations
from typing import Dict, Any, List, Tuple
from pathlib import Path
from ._qt_compat import (
    QWidget, QTabWidget, QFormLayout, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QDoubleSpinBox, QSpinBox, QComboBox, QCheckBox, QPushButton, QTableWidget,
    QTableWidgetItem, QHeaderView, QTextEdit, QGroupBox, QStyle
)
from ..core.gcode import EXPLICIT_HOOK_KEYS
from ..core.gcode import EXPLICIT_HOOK_KEYS


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
        self._init_peripherals_tab()
        self._init_openprinttag_tab()
        self._init_gcode_tab()
        self._init_issues_tab()

        self.set_defaults()

    # --- Issues tab (rules validation) ---
    def _init_issues_tab(self):
        w = QWidget(); v = QVBoxLayout(w)
        controls = QHBoxLayout()
        btn_refresh = QPushButton("Refresh"); btn_refresh.setToolTip("Validate current PDL against rules"); btn_refresh.clicked.connect(self._refresh_issues)
        btn_copy = QPushButton("Copy"); btn_copy.setToolTip("Copy issues to clipboard"); btn_copy.clicked.connect(self._copy_issues)
        controls.addWidget(btn_refresh); controls.addWidget(btn_copy)
        controls.addStretch(1)
        # Level filter
        controls.addWidget(QLabel("Level:"))
        from ._qt_compat import QComboBox as _QComboBox
        self.cb_issue_level = _QComboBox(); self.cb_issue_level.addItems(["ALL","ERROR+WARN","ERROR","WARN","INFO"])  # type: ignore
        try:
            self.cb_issue_level.currentIndexChanged.connect(lambda *_: self._render_issues())  # type: ignore[attr-defined]
        except Exception:
            pass
        controls.addWidget(self.cb_issue_level)
        # Text filter
        controls.addWidget(QLabel("Filter:"))
        self.ed_issue_filter = QLineEdit(); self.ed_issue_filter.setPlaceholderText("path or message contains…")
        try:
            self.ed_issue_filter.textChanged.connect(lambda *_: self._render_issues())  # type: ignore[attr-defined]
        except Exception:
            pass
        controls.addWidget(self.ed_issue_filter)
        v.addLayout(controls)
        self.t_issues = QTableWidget(0, 3)
        self.t_issues.setHorizontalHeaderLabels(["Level","Path","Message"])
        self.t_issues.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        v.addWidget(self.t_issues)
        idx = self.tabs.addTab(w, "Issues"); self.tabs.setTabToolTip(idx, "Rule-based validation results")
        self.issues_tab_index = idx

    def _refresh_issues(self):
        try:
            from ..core.rules import validate_pdl, summarize
            pdl = self.dump_pdl()
            issues = validate_pdl(pdl or {})
            # Cache then render with filter
            self._issues_cache = [(i.level, i.path, i.message) for i in issues]
            self._render_issues()
            # Update inline hints from issues
            self._update_inline_hints(issues)
            s = summarize(issues)
            try:
                if hasattr(self.parent(), 'update_issue_status'):
                    self.parent().update_issue_status(s.get('error',0), s.get('warn',0), s.get('info',0))
            except Exception:
                pass
        except Exception:
            pass

    def _render_issues(self):
        rows = getattr(self, '_issues_cache', [])
        try:
            target = (self.cb_issue_level.currentText() or 'ALL').upper()
        except Exception:
            target = 'ALL'
        try:
            q = (self.ed_issue_filter.text() or '').strip().lower()
        except Exception:
            q = ''
        def _keep(level: str) -> bool:
            l = (level or '').lower()
            if target == 'ALL':
                return True
            if target == 'ERROR+WARN':
                return l in ('error','warn')
            if target in ('ERROR','WARN','INFO'):
                return l == target.lower()
            return True
        self.t_issues.setRowCount(0)
        for lvl, path, msg in rows:
            if not _keep(lvl):
                continue
            if q and (q not in (path or '').lower()) and (q not in (msg or '').lower()):
                continue
            r = self.t_issues.rowCount(); self.t_issues.insertRow(r)
            self.t_issues.setItem(r, 0, QTableWidgetItem((lvl or '').upper()))
            self.t_issues.setItem(r, 1, QTableWidgetItem(path or ''))
            self.t_issues.setItem(r, 2, QTableWidgetItem(msg or ''))

    # --- Inline hints ---
    def _icon_for_level(self, level: str):
        try:
            st = self.style()
            if (level or '').lower() == 'error':
                return st.standardIcon(QStyle.StandardPixmap.SP_MessageBoxCritical)
            if (level or '').lower() == 'warn':
                return st.standardIcon(QStyle.StandardPixmap.SP_MessageBoxWarning)
            return st.standardIcon(QStyle.StandardPixmap.SP_MessageBoxInformation)
        except Exception:
            return None

    def _apply_hint(self, label: QLabel, level: str | None, message: str | None):
        try:
            if not label:
                return
            if not level and not message:
                label.setVisible(False)
                label.setToolTip("")
                return
            icon = self._icon_for_level(level or 'info')
            if icon:
                pm = icon.pixmap(16, 16)
                label.setPixmap(pm)
                label.setText("")
            else:
                label.setText("!")
            label.setToolTip(message or "")
            label.setVisible(True)
        except Exception:
            pass

    def _update_inline_hints(self, issues: list):
        # Reset
        for lab in [getattr(self, 'hint_fans_off', None), getattr(self, 'hint_exhaust_off', None), getattr(self, 'hint_sd_file', None), getattr(self, 'hint_camera_cmd', None), getattr(self, 'hint_exhaust_pin', None)]:
            try:
                if lab: lab.setVisible(False)
            except Exception:
                pass
        # Apply based on issues
        for i in issues:
            p = (getattr(i, 'path', '') or '')
            lvl = getattr(i, 'level', 'info')
            msg = getattr(i, 'message', '')
            if 'machine_control.fans.off_at_end' in p and getattr(self, 'hint_fans_off', None):
                self._apply_hint(self.hint_fans_off, lvl, msg)
            if 'machine_control.exhaust.off_at_end' in p and getattr(self, 'hint_exhaust_off', None):
                self._apply_hint(self.hint_exhaust_off, lvl, msg)
            if 'machine_control.sd_logging.filename' in p and getattr(self, 'hint_sd_file', None):
                self._apply_hint(self.hint_sd_file, lvl, msg)
            if p.startswith('machine_control.camera') and getattr(self, 'hint_camera_cmd', None):
                self._apply_hint(self.hint_camera_cmd, lvl, msg)
            if 'machine_control.exhaust.pin' in p and getattr(self, 'hint_exhaust_pin', None):
                self._apply_hint(self.hint_exhaust_pin, lvl, msg)

    def _run_firmware_checks(self, focus_prefix: str | List[str] = "machine_control") -> None:
        try:
            # Populate issues
            self._refresh_issues()
            # Switch to Issues tab and focus first relevant row
            idx = getattr(self, 'issues_tab_index', None)
            if isinstance(idx, int):
                self.tabs.setCurrentIndex(idx)
            # Select the first row with matching path prefix
            prefixes: List[str]
            if isinstance(focus_prefix, (list, tuple, set)):
                prefixes = [str(p) for p in focus_prefix]
            else:
                prefixes = [str(focus_prefix)]
            for r in range(self.t_issues.rowCount()):
                it = self.t_issues.item(r, 1)
                txt = (it.text() or '') if it else ''
                if any(txt.startswith(p) for p in prefixes):
                    self.t_issues.selectRow(r)
                    self.t_issues.scrollToItem(self.t_issues.item(r, 0))
                    break
        except Exception:
            pass

    def _copy_issues(self):
        try:
            from PySide6.QtWidgets import QApplication
            rows = []
            for r in range(self.t_issues.rowCount()):
                level = self.t_issues.item(r,0).text() if self.t_issues.item(r,0) else ''
                path = self.t_issues.item(r,1).text() if self.t_issues.item(r,1) else ''
                msg = self.t_issues.item(r,2).text() if self.t_issues.item(r,2) else ''
                rows.append(f"{level}\t{path}\t{msg}")
            QApplication.clipboard().setText("\n".join(rows))
        except Exception:
            pass

    # --- Helpers: Docs openers and resets ---
    def _open_doc(self, rel: str, title: str) -> None:
        try:
            from .mcode_reference_dialog import McodeReferenceDialog as _DocDlg
            dlg = _DocDlg(self)
            p = Path(__file__).resolve().parents[2] / rel
            if p.exists():
                dlg.view.setPlainText(p.read_text(encoding="utf-8"))
            dlg.setWindowTitle(title)
            dlg.resize(800, 600)
            dlg.exec()
        except Exception:
            pass

    def _reset_build_area_defaults(self) -> None:
        self.f_pdl_version.setText("1.0")
        self.f_origin.setText("front_left")
        # regenerate bed polygon from width/depth
        try:
            w = float(self.f_width.value() or 200); d = float(self.f_depth.value() or 200)
        except Exception:
            w, d = 200.0, 200.0
        shape = rect_to_bed_shape(w, d)
        self.t_bedshape.setRowCount(0)
        for x, y in shape:
            r = self.t_bedshape.rowCount(); self.t_bedshape.insertRow(r)
            self.t_bedshape.setItem(r, 0, QTableWidgetItem(f"{x}"))
            self.t_bedshape.setItem(r, 1, QTableWidgetItem(f"{y}"))
        # reset limits
        self.l_print_speed.setValue(0); self.l_travel_speed.setValue(0); self.l_accel.setValue(0); self.l_jerk.setValue(0)

    def _reset_machine_control_defaults(self) -> None:
        self.mc_psu_on_start.setChecked(False)
        self.mc_psu_off_end.setChecked(False)
        self.mc_enable_mesh.setChecked(False)
        self.mc_z_offset.setValue(0.0)
        self.mc_start_custom.clear(); self.mc_end_custom.clear()

    def _reset_peripherals_defaults(self) -> None:
        # Lights/RGB
        self.pr_light_on_start.setChecked(False); self.pr_light_off_end.setChecked(False)
        self.pr_rgb_r.setValue(0); self.pr_rgb_g.setValue(0); self.pr_rgb_b.setValue(0)
        # Chamber
        self.pr_chamber_temp.setValue(0); self.pr_chamber_wait.setChecked(False)
        # Camera
        self.pr_camera_before.setChecked(False); self.pr_camera_after.setChecked(False); self.pr_camera_cmd.setText("M240")
        # Fans
        self.pr_fan_part.setValue(0); self.pr_fan_aux_idx.setValue(0); self.pr_fan_aux.setValue(0)
        # Exhaust
        self.pr_exhaust_enable.setChecked(False); self.pr_exhaust_speed.setValue(0); self.pr_exhaust_pin.setValue(0); self.pr_exhaust_fan.setValue(0); self.pr_exhaust_off.setChecked(False)

    # ---------- Build Area ----------
    def _init_build_area_tab(self):
        w = QWidget(); form = QFormLayout(w)
        # Actions row
        row_actions = QHBoxLayout()
        btn_reset = QPushButton("Restore Defaults"); btn_reset.setToolTip("Reset common fields to sensible defaults")
        btn_help = QPushButton("Help…"); btn_help.setToolTip("Open overview documentation")
        btn_check = QPushButton("Check…"); btn_check.setToolTip("Run rules and open Issues tab")
        btn_reset.clicked.connect(self._reset_build_area_defaults)
        btn_help.clicked.connect(lambda: self._open_doc("docs/overview.md", "Overview"))
        btn_check.clicked.connect(lambda: self._run_firmware_checks(["process_defaults","limits"]))
        row_actions.addWidget(btn_reset); row_actions.addWidget(btn_help); row_actions.addWidget(btn_check); row_actions.addStretch(1)
        self.f_pdl_version = QLineEdit("1.0"); self.f_pdl_version.setToolTip("PDL schema version")
        self.f_id = QLineEdit()
        self.f_id.setToolTip("Unique printer identifier")
        self.f_name = QLineEdit(); self.f_name.setToolTip("Human-readable name")
        self.f_firmware = QComboBox(); self.f_firmware.addItems(FIRMWARES); self.f_firmware.setToolTip("Target firmware (affects mapping)")
        self.f_firmware.currentIndexChanged.connect(self._update_firmware_tips)
        self.f_kinematics = QComboBox(); self.f_kinematics.addItems(KINEMATICS); self.f_kinematics.setToolTip("Motion system type")
        self.f_width = QDoubleSpinBox(); self.f_width.setRange(10, 1000); self.f_width.setDecimals(1); self.f_width.setToolTip("Bed width (X)")
        self.f_depth = QDoubleSpinBox(); self.f_depth.setRange(10, 1000); self.f_depth.setDecimals(1); self.f_depth.setToolTip("Bed depth (Y)")
        self.f_z = QDoubleSpinBox(); self.f_z.setRange(10, 1000); self.f_z.setDecimals(1); self.f_z.setToolTip("Z height")
        self.f_origin = QLineEdit("front_left"); self.f_origin.setToolTip("Coordinate origin description")

        # Bed shape polygon editor
        self.t_bedshape = QTableWidget(0, 2)
        self.t_bedshape.setHorizontalHeaderLabels(["X","Y"])
        self.t_bedshape.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        bs_btns = QHBoxLayout()
        bs_add = QPushButton("Add Point"); bs_add.setToolTip("Add a new vertex to bed shape"); bs_add.clicked.connect(self._add_bed_point)
        bs_del = QPushButton("Remove Point"); bs_del.setToolTip("Remove selected vertices"); bs_del.clicked.connect(self._del_bed_point)
        bs_rect = QPushButton("Make Rectangle from Width/Depth"); bs_rect.setToolTip("Fill polygon from width/depth"); bs_rect.clicked.connect(self._bed_make_rect)
        bs_btns.addWidget(bs_add); bs_btns.addWidget(bs_del); bs_btns.addWidget(bs_rect); bs_btns.addStretch(1)

        # Limits group
        limits = QGroupBox("Limits")
        lim_form = QFormLayout(limits)
        self.l_print_speed = QDoubleSpinBox(); self.l_print_speed.setRange(1, 1000); self.l_print_speed.setToolTip("Max print speed")
        self.l_travel_speed = QDoubleSpinBox(); self.l_travel_speed.setRange(1, 2000); self.l_travel_speed.setToolTip("Max travel speed")
        self.l_accel = QDoubleSpinBox(); self.l_accel.setRange(1, 50000); self.l_accel.setToolTip("Global max acceleration")
        self.l_jerk = QDoubleSpinBox(); self.l_jerk.setRange(0, 200); self.l_jerk.setToolTip("Jerk (Cura)")
        lim_form.addRow("Print Speed Max (mm/s)", self.l_print_speed)
        lim_form.addRow("Travel Speed Max (mm/s)", self.l_travel_speed)
        lim_form.addRow("Acceleration Max (mm/s²)", self.l_accel)
        lim_form.addRow("Jerk Max (mm/s)", self.l_jerk)

        form.addRow(row_actions)
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
        idx = self.tabs.addTab(w, "Build Area"); self.tabs.setTabToolTip(idx, "Bed, geometry, and limits")

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
        idx = self.tabs.addTab(w, "Extruders"); self.tabs.setTabToolTip(idx, "Extruder/nozzle/toolhead configuration")

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
        idx = self.tabs.addTab(w, "Multi-Material"); self.tabs.setTabToolTip(idx, "Spool banks/carousels (AMS/MMU)")

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
        row_actions = QHBoxLayout()
        btn_reset = QPushButton("Restore Defaults"); btn_reset.setToolTip("Reset feature fields to defaults")
        btn_help = QPushButton("Help…"); btn_help.setToolTip("Open firmware mapping documentation")
        btn_check = QPushButton("Check…"); btn_check.setToolTip("Run rules and open Issues tab")
        btn_reset.clicked.connect(lambda: None)
        btn_help.clicked.connect(lambda: self._open_doc("docs/firmware-mapping.md", "Firmware Mapping"))
        btn_check.clicked.connect(lambda: self._run_firmware_checks(["machine_control","process_defaults"]))
        form.addRow(row_actions)
        self.f_abl = QCheckBox(); self.f_abl.setToolTip("Enable/disable ABL feature")
        self.f_probe_type = QComboBox(); self.f_probe_type.addItems(PROBE_TYPES)
        self.f_mesh_r = QSpinBox(); self.f_mesh_r.setRange(1, 20)
        self.f_mesh_c = QSpinBox(); self.f_mesh_c.setRange(1, 20)
        self.f_probe_active_low = QCheckBox()
        # Endstops group
        es = QGroupBox("Endstops Polarity (Checked = Active Low)")
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
        idx = self.tabs.addTab(w, "Features"); self.tabs.setTabToolTip(idx, "ABL, probe, endstops")

    # ---------- Machine Control (M-codes helper) ----------
    def _init_machine_control_tab(self):
        w = QWidget(); form = QFormLayout(w)
        row_actions = QHBoxLayout();
        btn_reset = QPushButton("Restore Defaults"); btn_reset.setToolTip("Clear machine control to defaults")
        btn_help = QPushButton("Help…"); btn_help.setToolTip("Open M-code reference")
        btn_check = QPushButton("Check…"); btn_check.setToolTip("Run firmware-specific checks and open Issues tab")
        btn_reset.clicked.connect(self._reset_machine_control_defaults)
        btn_help.clicked.connect(lambda: self._open_doc("docs/mcode-reference.md", "M-code Reference"))
        btn_check.clicked.connect(lambda: self._run_firmware_checks("machine_control"))
        row_actions.addWidget(btn_reset); row_actions.addWidget(btn_help); row_actions.addWidget(btn_check); row_actions.addStretch(1)
        # PSU controls (standard)
        self.mc_psu_on_start = QCheckBox(); self.mc_psu_on_start.setToolTip("Insert M80 into start")
        self.mc_psu_off_end = QCheckBox(); self.mc_psu_off_end.setToolTip("Insert M81 into end")
        # Mesh enable and Z offset
        self.mc_enable_mesh = QCheckBox(); self.mc_enable_mesh.setToolTip("Enable bed mesh at start (M420 S1)")
        self.mc_z_offset = QDoubleSpinBox(); self.mc_z_offset.setRange(-5,5); self.mc_z_offset.setSingleStep(0.01); self.mc_z_offset.setPrefix("Z:")
        # Custom M-codes
        self.mc_start_custom = QTextEdit(); self.mc_start_custom.setPlaceholderText("; Custom M-codes at start\nM117 Starting…")
        self.mc_end_custom = QTextEdit(); self.mc_end_custom.setPlaceholderText("; Custom M-codes at end\nM117 Done")

        form.addRow(row_actions)
        form.addRow("PSU ON at start (M80)", self.mc_psu_on_start)
        form.addRow("PSU OFF at end (M81)", self.mc_psu_off_end)
        form.addRow("Enable mesh at start (M420 S1)", self.mc_enable_mesh)
        form.addRow("Probe Z offset (M851)", self.mc_z_offset)
        form.addRow(QLabel("Custom start M-codes"), self.mc_start_custom)
        form.addRow(QLabel("Custom end M-codes"), self.mc_end_custom)
        idx = self.tabs.addTab(w, "Machine Control"); self.tabs.setTabToolTip(idx, "Lifecycle M-codes and custom sequences")

    # ---------- Peripherals (Lights, Camera, Fans, SD) ----------
    def _init_peripherals_tab(self):
        w = QWidget(); form = QFormLayout(w)
        row_actions = QHBoxLayout()
        btn_reset = QPushButton("Restore Defaults"); btn_reset.setToolTip("Clear peripherals to defaults")
        btn_help = QPushButton("Help…"); btn_help.setToolTip("Open firmware mapping documentation")
        btn_check = QPushButton("Check…"); btn_check.setToolTip("Run firmware-specific checks and open Issues tab")
        btn_reset.clicked.connect(self._reset_peripherals_defaults)
        btn_help.clicked.connect(lambda: self._open_doc("docs/firmware-mapping.md", "Firmware Mapping"))
        btn_check.clicked.connect(lambda: self._run_firmware_checks("machine_control"))
        row_actions.addWidget(btn_reset); row_actions.addWidget(btn_help); row_actions.addWidget(btn_check); row_actions.addStretch(1)
        form.addRow(row_actions)
        self.lb_fw_tip = QLabel(""); self.lb_fw_tip.setWordWrap(True)
        form.addRow(self.lb_fw_tip)
        # Lights
        self.pr_light_on_start = QCheckBox(); self.pr_light_on_start.setToolTip("M355 S1 at start")
        self.pr_light_off_end = QCheckBox(); self.pr_light_off_end.setToolTip("M355 S0 at end")
        row_rgb = QHBoxLayout();
        self.pr_rgb_r = QSpinBox(); self.pr_rgb_r.setRange(0,255); self.pr_rgb_r.setPrefix("R:"); self.pr_rgb_r.setToolTip("RGB red component (0-255)")
        self.pr_rgb_g = QSpinBox(); self.pr_rgb_g.setRange(0,255); self.pr_rgb_g.setPrefix(" G:"); self.pr_rgb_g.setToolTip("RGB green component (0-255)")
        self.pr_rgb_b = QSpinBox(); self.pr_rgb_b.setRange(0,255); self.pr_rgb_b.setPrefix(" B:"); self.pr_rgb_b.setToolTip("RGB blue component (0-255)")
        row_rgb.addWidget(self.pr_rgb_r); row_rgb.addWidget(self.pr_rgb_g); row_rgb.addWidget(self.pr_rgb_b)
        # Chamber
        row_cht = QHBoxLayout();
        self.pr_chamber_temp = QDoubleSpinBox(); self.pr_chamber_temp.setRange(0,120); self.pr_chamber_temp.setSuffix(" °C"); self.pr_chamber_temp.setToolTip("Chamber temperature target")
        self.pr_chamber_wait = QCheckBox("Wait"); self.pr_chamber_wait.setToolTip("Wait for chamber to reach target (M191)")
        row_cht.addWidget(self.pr_chamber_temp); row_cht.addWidget(self.pr_chamber_wait)
        # Camera
        self.pr_camera_before = QCheckBox("Trigger before snapshot"); self.pr_camera_before.setToolTip("Adds camera command to before_snapshot hook")
        self.pr_camera_after = QCheckBox("Trigger after snapshot"); self.pr_camera_after.setToolTip("Adds camera command to after_snapshot hook")
        self.pr_camera_cmd = QLineEdit("M240"); self.pr_camera_cmd.setToolTip("Snapshot command (e.g., M240 or macro)")
        self.hint_camera_cmd = QLabel("")
        # Fans
        row_part = QHBoxLayout();
        self.pr_fan_part = QSpinBox(); self.pr_fan_part.setRange(0,100); self.pr_fan_part.setSuffix(" %"); self.pr_fan_part.setToolTip("Part cooling fan at start")
        row_part.addWidget(QLabel("Part fan:")); row_part.addWidget(self.pr_fan_part)
        row_aux = QHBoxLayout();
        self.pr_fan_aux_idx = QSpinBox(); self.pr_fan_aux_idx.setRange(0,9); self.pr_fan_aux_idx.setToolTip("Aux fan index (P)")
        self.pr_fan_aux = QSpinBox(); self.pr_fan_aux.setRange(0,100); self.pr_fan_aux.setSuffix(" %"); self.pr_fan_aux.setToolTip("Aux fan speed at start")
        row_aux.addWidget(QLabel("Aux fan P:")); row_aux.addWidget(self.pr_fan_aux_idx); row_aux.addWidget(self.pr_fan_aux)
        self.pr_fans_off_end = QCheckBox("Fans off at end"); self.pr_fans_off_end.setToolTip("Insert M107 at end")
        self.hint_fans_off = QLabel("")
        # SD logging
        row_sd = QHBoxLayout();
        self.pr_sd_enable = QCheckBox("Enable at start")
        self.pr_sd_file = QLineEdit("opk_log.gco")
        self.pr_sd_stop = QCheckBox("Stop at end")
        self.hint_sd_file = QLabel("")
        row_sd.addWidget(self.pr_sd_enable); row_sd.addWidget(self.pr_sd_file); row_sd.addWidget(self.pr_sd_stop); row_sd.addWidget(self.hint_sd_file)

        form.addRow("Light ON at start (M355)", self.pr_light_on_start)
        form.addRow("Light OFF at end (M355)", self.pr_light_off_end)
        form.addRow("RGB at start (M150)", row_rgb)
        form.addRow("Chamber temp at start (M141/M191)", row_cht)
        _camrow = QHBoxLayout(); _camrow.addWidget(self.pr_camera_cmd); _camrow.addWidget(self.hint_camera_cmd); _camrow.addStretch(1)
        _camroww = QWidget(); _camroww.setLayout(_camrow)
        form.addRow(QLabel("Camera command"), _camroww)
        form.addRow(self.pr_camera_before)
        form.addRow(self.pr_camera_after)
        form.addRow(row_part)
        form.addRow(row_aux)
        row_fans_off = QHBoxLayout(); row_fans_off.addWidget(self.pr_fans_off_end); row_fans_off.addWidget(self.hint_fans_off); row_fans_off.addStretch(1)
        form.addRow(row_fans_off)
        form.addRow("SD logging (M928/M29)", row_sd)

        # Exhaust controls
        ex_row1 = QHBoxLayout();
        self.pr_exhaust_enable = QCheckBox("Enable at start"); self.pr_exhaust_enable.setToolTip("Enable exhaust at start via M42 or M106")
        self.pr_exhaust_speed = QSpinBox(); self.pr_exhaust_speed.setRange(0,100); self.pr_exhaust_speed.setSuffix(" %"); self.pr_exhaust_speed.setToolTip("Exhaust speed percent")
        ex_row1.addWidget(self.pr_exhaust_enable); ex_row1.addWidget(self.pr_exhaust_speed)
        ex_row2 = QHBoxLayout();
        self.pr_exhaust_pin = QSpinBox(); self.pr_exhaust_pin.setRange(0,999); self.pr_exhaust_pin.setPrefix("Pin P:"); self.pr_exhaust_pin.setToolTip("GPIO pin (M42 P) or use policy for named pins")
        self.pr_exhaust_fan = QSpinBox(); self.pr_exhaust_fan.setRange(0,9); self.pr_exhaust_fan.setPrefix(" Fan P:"); self.pr_exhaust_fan.setToolTip("Fan index (M106/M107 P)")
        self.pr_exhaust_off = QCheckBox("Off at end"); self.pr_exhaust_off.setToolTip("Turn exhaust off at end")
        self.hint_exhaust_off = QLabel(""); self.hint_exhaust_pin = QLabel("")
        ex_row2.addWidget(self.pr_exhaust_pin); ex_row2.addWidget(self.pr_exhaust_fan); ex_row2.addWidget(self.pr_exhaust_off); ex_row2.addWidget(self.hint_exhaust_off); ex_row2.addWidget(self.hint_exhaust_pin)
        form.addRow(QLabel("Exhaust (choose Pin or Fan)"))
        form.addRow(ex_row1)
        form.addRow(ex_row2)

        # Aux Outputs (M42)
        form.addRow(QLabel("Auxiliary Outputs (M42)"))
        self.t_aux = QTableWidget(0, 4)
        self.t_aux.setHorizontalHeaderLabels(["Label","Pin P","Start S","End S"])
        self.t_aux.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        form.addRow(self.t_aux)
        rowax = QHBoxLayout();
        ax_add = QPushButton("Add Aux"); ax_add.clicked.connect(self._add_aux)
        ax_del = QPushButton("Remove Aux"); ax_del.clicked.connect(self._del_aux)
        rowax.addWidget(ax_add); rowax.addWidget(ax_del); rowax.addStretch(1)
        form.addRow(rowax)

        # Custom Peripherals (hooked M-codes)
        form.addRow(QLabel("Custom Peripherals (hooked M-codes)"))
        self.t_cper = QTableWidget(0, 3)
        self.t_cper.setHorizontalHeaderLabels(["Label","Hook","Script (one command per line)"])
        self.t_cper.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        self.t_cper.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.t_cper.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        form.addRow(self.t_cper)
        rowcp = QHBoxLayout();
        cp_add = QPushButton("Add Peripheral"); cp_add.clicked.connect(self._add_cper)
        cp_del = QPushButton("Remove Peripheral"); cp_del.clicked.connect(self._del_cper)
        rowcp.addWidget(cp_add); rowcp.addWidget(cp_del); rowcp.addStretch(1)
        form.addRow(rowcp)
        idx = self.tabs.addTab(w, "Peripherals"); self.tabs.setTabToolTip(idx, "Lights, camera, fans, SD logging, exhaust")
        self._update_firmware_tips()

    # ---------- OpenPrintTag ----------
    def _init_openprinttag_tab(self):
        w = QWidget(); form = QFormLayout(w)
        self.opt_id = QLineEdit(); self.opt_id.setToolTip("OpenPrintTag ID")
        self.opt_version = QLineEdit(); self.opt_version.setToolTip("OpenPrintTag version")
        self.opt_url = QLineEdit(); self.opt_url.setToolTip("URL for documentation or support")
        self.opt_manu = QLineEdit(); self.opt_manu.setToolTip("Manufacturer")
        self.opt_model = QLineEdit(); self.opt_model.setToolTip("Model")
        self.opt_serial = QLineEdit(); self.opt_serial.setToolTip("Serial number")
        self.opt_notes = QTextEdit(); self.opt_notes.setToolTip("Notes")
        form.addRow("ID", self.opt_id)
        form.addRow("Version", self.opt_version)
        form.addRow("URL", self.opt_url)
        form.addRow("Manufacturer", self.opt_manu)
        form.addRow("Model", self.opt_model)
        form.addRow("Serial", self.opt_serial)
        form.addRow(QLabel("Notes"), self.opt_notes)
        # Custom data key/values
        self.t_opt_data = QTableWidget(0, 2)
        self.t_opt_data.setHorizontalHeaderLabels(["Key","Value"])
        self.t_opt_data.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        form.addRow(QLabel("Custom Data"))
        form.addRow(self.t_opt_data)
        row = QHBoxLayout();
        add = QPushButton("Add Data"); add.clicked.connect(self._opt_add)
        rem = QPushButton("Remove Data"); rem.clicked.connect(self._opt_del)
        row.addWidget(add); row.addWidget(rem); row.addStretch(1)
        form.addRow(row)
        # NFC and DB buttons
        row2 = QHBoxLayout();
        b_read = QPushButton("Read NFC"); b_read.clicked.connect(self._opt_nfc_read)
        b_write = QPushButton("Write NFC"); b_write.clicked.connect(self._opt_nfc_write)
        b_save = QPushButton("Save to DB"); b_save.clicked.connect(self._opt_db_save)
        b_load = QPushButton("Load from DB"); b_load.clicked.connect(self._opt_db_load)
        b_search = QPushButton("Search Online"); b_search.clicked.connect(self._opt_remote_search)
        b_sync = QPushButton("Sync Online"); b_sync.clicked.connect(self._opt_remote_sync)
        for b in (b_read, b_write, b_save, b_load, b_search, b_sync): row2.addWidget(b)
        form.addRow(row2)
        idx = self.tabs.addTab(w, "OpenPrintTag"); self.tabs.setTabToolTip(idx, "Embed metadata tag in start G-code")

    # ---------- Filaments ----------
    def _init_filaments_tab(self):
        w = QWidget(); v = QVBoxLayout(w)
        self.t_filaments = QTableWidget(0, 9)
        self.t_filaments.setHorizontalHeaderLabels([
            "Name","Type","Dia","Nozzle °C","Bed °C","Retract Len","Retract Spd","Fan %","Color"
        ])
        self.t_filaments.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.t_filaments.setToolTip("Materials table: name/type/diameter/temperatures/retraction/fan/color")
        v.addWidget(self.t_filaments)
        row = QHBoxLayout()
        btn_add = QPushButton("Add"); btn_add.setToolTip("Add a filament preset"); btn_add.clicked.connect(self._add_filament)
        btn_del = QPushButton("Remove"); btn_del.setToolTip("Remove selected presets"); btn_del.clicked.connect(self._del_filament)
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
        # Actions row
        row = QHBoxLayout()
        btn_check = QPushButton("Check…"); btn_check.setToolTip("Run rules and focus G-code issues")
        btn_check.clicked.connect(lambda: self._run_firmware_checks("gcode"))
        btn_help = QPushButton("Help…"); btn_help.setToolTip("Open G-code Help")
        btn_help.clicked.connect(lambda: self._open_doc("docs/gcode-help.md", "G-code Help"))
        row.addWidget(btn_check); row.addWidget(btn_help); row.addStretch(1)
        outer.addLayout(row)

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

        idx = self.tabs.addTab(w, "G-code"); self.tabs.setTabToolTip(idx, "Hooks and macros")

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
            self.mc_enable_mesh.setChecked(False)
            self.mc_z_offset.setValue(0)
            self.mc_start_custom.setPlainText("")
            self.mc_end_custom.setPlainText("")
        if hasattr(self, 'pr_light_on_start'):
            self.pr_light_on_start.setChecked(False)
            self.pr_light_off_end.setChecked(False)
            self.pr_rgb_r.setValue(0); self.pr_rgb_g.setValue(0); self.pr_rgb_b.setValue(0)
            self.pr_chamber_temp.setValue(0); self.pr_chamber_wait.setChecked(False)
            self.pr_camera_before.setChecked(False); self.pr_camera_after.setChecked(False)
            self.pr_camera_cmd.setText("M240")
            self.pr_fan_part.setValue(0); self.pr_fan_aux_idx.setValue(0); self.pr_fan_aux.setValue(0)
            self.pr_fans_off_end.setChecked(False)
            self.pr_sd_enable.setChecked(False); self.pr_sd_file.setText("opk_log.gco"); self.pr_sd_stop.setChecked(False)
            # Exhaust defaults
            self.pr_exhaust_enable.setChecked(False); self.pr_exhaust_speed.setValue(0)
            self.pr_exhaust_pin.setValue(0); self.pr_exhaust_fan.setValue(0); self.pr_exhaust_off.setChecked(False)
            # Aux outputs: initialize three rows
            if hasattr(self, 't_aux'):
                self.t_aux.setRowCount(0)
                for i in range(1,4):
                    self._add_aux(default_label=f"Aux{i}")
            # Custom peripherals: empty
            if hasattr(self, 't_cper'):
                self.t_cper.setRowCount(0)

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
        # OpenPrintTag
        opt = g.get("open_print_tag") or {}
        self.opt_id.setText(str(opt.get("id") or ""))
        self.opt_version.setText(str(opt.get("version") or ""))
        self.opt_url.setText(str(opt.get("url") or ""))
        self.opt_manu.setText(str(opt.get("manufacturer") or ""))
        self.opt_model.setText(str(opt.get("model") or ""))
        self.opt_serial.setText(str(opt.get("serial") or ""))
        self.opt_notes.setPlainText(str(opt.get("notes") or ""))
        self.t_opt_data.setRowCount(0)
        for k, v in (opt.get("data") or {}).items():
            r = self.t_opt_data.rowCount(); self.t_opt_data.insertRow(r)
            self.t_opt_data.setItem(r, 0, QTableWidgetItem(str(k)))
            self.t_opt_data.setItem(r, 1, QTableWidgetItem(str(v)))
        # Machine control: infer checkboxes from start/end and structured mc
        mc = (g.get("machine_control") or {})
        start_seq = gc.get("start") or []
        end_seq = gc.get("end") or []
        def _has(prefix, seq):
            return any(str(s).strip().upper().startswith(prefix) for s in seq)
        self.mc_psu_on_start.setChecked(bool(mc.get("psu_on_start") or _has("M80", start_seq)))
        self.mc_psu_off_end.setChecked(bool(mc.get("psu_off_end") or _has("M81", end_seq)))
        # Peripherals - lights
        self.pr_light_on_start.setChecked(bool(mc.get("light_on_start") or _has("M355 S1", start_seq)))
        self.pr_light_off_end.setChecked(bool(mc.get("light_off_end") or _has("M355 S0", end_seq)))
        # RGB M150 R,G,B
        import re
        m150 = next((s for s in start_seq if str(s).strip().upper().startswith("M150")), None)
        if m150:
            nums = {k:int(v) for k,v in re.findall(r"([RUB])\s*(\d+)", m150, flags=re.I)}
            self.pr_rgb_r.setValue(nums.get('R',0)); self.pr_rgb_g.setValue(nums.get('U',0)); self.pr_rgb_b.setValue(nums.get('B',0))
        elif isinstance(mc.get("rgb_start"), dict):
            self.pr_rgb_r.setValue(int(mc["rgb_start"].get('r') or 0))
            self.pr_rgb_g.setValue(int(mc["rgb_start"].get('g') or 0))
            self.pr_rgb_b.setValue(int(mc["rgb_start"].get('b') or 0))
        # Chamber
        m141 = next((s for s in start_seq if str(s).strip().upper().startswith("M141")), None)
        if m141:
            m = re.search(r"S\s*(\d+)", m141, flags=re.I)
            if m:
                self.pr_chamber_temp.setValue(float(m.group(1)))
        elif isinstance(mc.get("chamber"), dict) and mc["chamber"].get("temp"):
            self.pr_chamber_temp.setValue(float(mc["chamber"]["temp"]))
        self.pr_chamber_wait.setChecked(bool(mc.get("chamber", {}).get("wait") or _has("M191", start_seq)))
        # Mesh enable
        self.mc_enable_mesh.setChecked(any(s.strip().upper().startswith("M420 S1") for s in start_seq))
        # Z offset
        m851 = next((s for s in start_seq if str(s).strip().upper().startswith("M851")), None)
        if m851:
            m = re.search(r"Z\s*(-?\d+(?:\.\d+)?)", m851, flags=re.I)
            if m:
                try: self.mc_z_offset.setValue(float(m.group(1)))
                except Exception: pass
        elif isinstance(mc.get("z_offset"), (int, float)):
            self.mc_z_offset.setValue(float(mc["z_offset"]))
        # Camera
        cam = mc.get("camera") or {}
        self.pr_camera_cmd.setText(str(cam.get("command") or self.pr_camera_cmd.text()))
        self.pr_camera_before.setChecked(bool(cam.get("use_before_snapshot") or bool(g.get("before_snapshot"))))
        self.pr_camera_after.setChecked(bool(cam.get("use_after_snapshot") or bool(g.get("after_snapshot"))))
        # Fans
        fans = mc.get("fans") or {}
        try: self.pr_fan_part.setValue(int(fans.get("part_start_percent") or 0))
        except Exception: pass
        try: self.pr_fan_aux_idx.setValue(int(fans.get("aux_index") or 0))
        except Exception: pass
        try: self.pr_fan_aux.setValue(int(fans.get("aux_start_percent") or 0))
        except Exception: pass
        self.pr_fans_off_end.setChecked(bool(fans.get("off_at_end") or _has("M107", end_seq)))
        # SD logging
        sdl = mc.get("sd_logging") or {}
        self.pr_sd_enable.setChecked(bool(sdl.get("enable_start") or any(str(s).strip().upper().startswith("M928") for s in start_seq)))
        if sdl.get("filename"): self.pr_sd_file.setText(str(sdl.get("filename")))
        self.pr_sd_stop.setChecked(bool(sdl.get("stop_at_end") or _has("M29", end_seq)))
        # Exhaust
        ex = mc.get("exhaust") or {}
        self.pr_exhaust_enable.setChecked(bool(ex.get("enable_start") or False))
        try: self.pr_exhaust_speed.setValue(int(ex.get("speed_percent") or 0))
        except Exception: pass
        try: self.pr_exhaust_pin.setValue(int(ex.get("pin") or 0))
        except Exception: pass
        try: self.pr_exhaust_fan.setValue(int(ex.get("fan_index") or 0))
        except Exception: pass
        self.pr_exhaust_off.setChecked(bool(ex.get("off_at_end") or False))
        # Aux outputs
        if hasattr(self, 't_aux'):
            self.t_aux.setRowCount(0)
            for ao in (mc.get("aux_outputs") or []):
                r = self.t_aux.rowCount(); self.t_aux.insertRow(r)
                self.t_aux.setItem(r, 0, QTableWidgetItem(str(ao.get("label") or "Aux")))
                self.t_aux.setItem(r, 1, QTableWidgetItem(str(ao.get("pin") or "")))
                self.t_aux.setItem(r, 2, QTableWidgetItem(str(ao.get("start_value") or "")))
                self.t_aux.setItem(r, 3, QTableWidgetItem(str(ao.get("end_value") or "")))
        # Custom Peripherals
        if hasattr(self, 't_cper'):
            self.t_cper.setRowCount(0)
        # Build dynamic hook options from explicit hooks + existing gcode keys
        hook_options = set(EXPLICIT_HOOK_KEYS)
        hook_options.update(gc.keys())
        hook_options.update((gc.get("hooks") or {}).keys())
        for cp in (mc.get("custom_peripherals") or []):
            r = self.t_cper.rowCount(); self.t_cper.insertRow(r)
            self.t_cper.setItem(r, 0, QTableWidgetItem(str(cp.get("label") or "")))
            hook_combo = QComboBox(); hook_combo.setEditable(True)
            hook_combo.addItems(sorted(hook_options))
            hook_combo.setCurrentText(str(cp.get("hook") or "start"))
            self.t_cper.setCellWidget(r, 1, hook_combo)
            te = QTextEdit(); te.setPlainText("\n".join(cp.get("sequence") or []))
            self.t_cper.setCellWidget(r, 2, te)

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
            "enable_mesh_start": self.mc_enable_mesh.isChecked(),
            "z_offset": self.mc_z_offset.value(),
            "start_custom": [ln for ln in self.mc_start_custom.toPlainText().splitlines() if ln.strip()],
            "end_custom": [ln for ln in self.mc_end_custom.toPlainText().splitlines() if ln.strip()],
        }
        # Peripherals structured
        mc["light_on_start"] = self.pr_light_on_start.isChecked()
        mc["light_off_end"] = self.pr_light_off_end.isChecked()
        mc["rgb_start"] = {"r": self.pr_rgb_r.value(), "g": self.pr_rgb_g.value(), "b": self.pr_rgb_b.value()}
        mc["chamber"] = {"temp": self.pr_chamber_temp.value(), "wait": self.pr_chamber_wait.isChecked()}
        mc["camera"] = {"use_before_snapshot": self.pr_camera_before.isChecked(), "use_after_snapshot": self.pr_camera_after.isChecked(), "command": self.pr_camera_cmd.text().strip()}
        mc["fans"] = {"part_start_percent": self.pr_fan_part.value(), "aux_index": self.pr_fan_aux_idx.value(), "aux_start_percent": self.pr_fan_aux.value(), "off_at_end": self.pr_fans_off_end.isChecked()}
        mc["sd_logging"] = {"enable_start": self.pr_sd_enable.isChecked(), "filename": self.pr_sd_file.text().strip(), "stop_at_end": self.pr_sd_stop.isChecked()}
        mc["exhaust"] = {"enable_start": self.pr_exhaust_enable.isChecked(), "speed_percent": self.pr_exhaust_speed.value(), "off_at_end": self.pr_exhaust_off.isChecked(), "pin": self.pr_exhaust_pin.value(), "fan_index": self.pr_exhaust_fan.value()}
        # Auxiliary outputs
        aux = []
        for r in range(self.t_aux.rowCount()):
            label = self.t_aux.item(r,0).text().strip() if self.t_aux.item(r,0) else ""
            pin = self.t_aux.item(r,1).text().strip() if self.t_aux.item(r,1) else ""
            sv = self.t_aux.item(r,2).text().strip() if self.t_aux.item(r,2) else ""
            ev = self.t_aux.item(r,3).text().strip() if self.t_aux.item(r,3) else ""
            if not pin:
                continue
            try:
                entry = {"label": label or "Aux", "pin": int(pin)}
                if sv != "": entry["start_value"] = int(sv)
                if ev != "": entry["end_value"] = int(ev)
                aux.append(entry)
            except Exception:
                continue
        if aux:
            mc["aux_outputs"] = aux
        # Remove empty/defaults
        if not any((mc["psu_on_start"], mc["light_on_start"], mc["enable_mesh_start"], mc["z_offset"], mc["start_custom"])) and not any((mc["psu_off_end"], mc["light_off_end"], mc["end_custom"])) and not any((mc["rgb_start"][k] for k in ("r","g","b"))) and not mc["chamber"]["temp"] and not mc.get("camera",{}).get("use_before_snapshot") and not mc.get("camera",{}).get("use_after_snapshot") and not any((mc.get("fans",{}).get("part_start_percent"), mc.get("fans",{}).get("aux_start_percent"), mc.get("fans",{}).get("off_at_end"))) and not mc.get("sd_logging",{}).get("enable_start"):
            pass
        else:
            g["machine_control"] = mc
        # OpenPrintTag serialization
        opt: Dict[str, Any] = {}
        if self.opt_id.text().strip(): opt["id"] = self.opt_id.text().strip()
        if self.opt_version.text().strip(): opt["version"] = self.opt_version.text().strip()
        if self.opt_url.text().strip(): opt["url"] = self.opt_url.text().strip()
        if self.opt_manu.text().strip(): opt["manufacturer"] = self.opt_manu.text().strip()
        if self.opt_model.text().strip(): opt["model"] = self.opt_model.text().strip()
        if self.opt_serial.text().strip(): opt["serial"] = self.opt_serial.text().strip()
        if self.opt_notes.toPlainText().strip(): opt["notes"] = self.opt_notes.toPlainText().strip()
        data_map: Dict[str, Any] = {}
        for r in range(self.t_opt_data.rowCount()):
            k = self.t_opt_data.item(r,0).text().strip() if self.t_opt_data.item(r,0) else ""
            v = self.t_opt_data.item(r,1).text().strip() if self.t_opt_data.item(r,1) else ""
            if k:
                data_map[k] = v
        if data_map:
            opt["data"] = data_map
        if opt:
            g["open_print_tag"] = opt
        # Limits

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

    def _opt_add(self):
        r = self.t_opt_data.rowCount(); self.t_opt_data.insertRow(r)
        self.t_opt_data.setItem(r, 0, QTableWidgetItem("key"))
        self.t_opt_data.setItem(r, 1, QTableWidgetItem("value"))

    def _opt_del(self):
        rows = sorted({i.row() for i in self.t_opt_data.selectedItems()}, reverse=True)
        for r in rows:
            self.t_opt_data.removeRow(r)

    # --- OpenPrintTag NFC/DB/Remote ---
    def _collect_opt(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        if self.opt_id.text().strip(): data['id'] = self.opt_id.text().strip()
        if self.opt_version.text().strip(): data['version'] = self.opt_version.text().strip()
        if self.opt_url.text().strip(): data['url'] = self.opt_url.text().strip()
        if self.opt_manu.text().strip(): data['manufacturer'] = self.opt_manu.text().strip()
        if self.opt_model.text().strip(): data['model'] = self.opt_model.text().strip()
        if self.opt_serial.text().strip(): data['serial'] = self.opt_serial.text().strip()
        if self.opt_notes.toPlainText().strip(): data['notes'] = self.opt_notes.toPlainText().strip()
        dmap = {}
        for r in range(self.t_opt_data.rowCount()):
            k = self.t_opt_data.item(r,0).text().strip() if self.t_opt_data.item(r,0) else ""
            v = self.t_opt_data.item(r,1).text().strip() if self.t_opt_data.item(r,1) else ""
            if k: dmap[k] = v
        if dmap:
            data['data'] = dmap
        return data

    def _apply_opt(self, data: Dict[str, Any]):
        self.opt_id.setText(str(data.get('id') or ''))
        self.opt_version.setText(str(data.get('version') or ''))
        self.opt_url.setText(str(data.get('url') or ''))
        self.opt_manu.setText(str(data.get('manufacturer') or ''))
        self.opt_model.setText(str(data.get('model') or ''))
        self.opt_serial.setText(str(data.get('serial') or ''))
        self.opt_notes.setPlainText(str(data.get('notes') or ''))
        self.t_opt_data.setRowCount(0)
        for k, v in (data.get('data') or {}).items():
            r = self.t_opt_data.rowCount(); self.t_opt_data.insertRow(r)
            self.t_opt_data.setItem(r, 0, QTableWidgetItem(str(k)))
            self.t_opt_data.setItem(r, 1, QTableWidgetItem(str(v)))

    def _opt_nfc_read(self):
        from ..integrations import nfc as nfc_mod
        from PySide6.QtWidgets import QMessageBox
        if not nfc_mod.nfc_available():
            QMessageBox.warning(self, "NFC", "nfcpy not installed or NFC device unavailable.")
            return
        try:
            payload = nfc_mod.read_tag()
        except Exception as e:
            QMessageBox.critical(self, "NFC", f"Failed to read tag:\n{e}")
            return
        if payload:
            self._apply_opt(payload)
            QMessageBox.information(self, "NFC", "Loaded data from NFC tag.")
        else:
            QMessageBox.information(self, "NFC", "No OpenPrintTag payload found.")

    def _opt_nfc_write(self):
        from ..integrations import nfc as nfc_mod
        from PySide6.QtWidgets import QMessageBox
        if not nfc_mod.nfc_available():
            QMessageBox.warning(self, "NFC", "nfcpy not installed or NFC device unavailable.")
            return
        try:
            nfc_mod.write_tag(self._collect_opt())
        except Exception as e:
            QMessageBox.critical(self, "NFC", f"Failed to write tag:\n{e}")
            return
        QMessageBox.information(self, "NFC", "Wrote OpenPrintTag payload to NFC tag.")

    def _opt_db_save(self):
        from ..integrations import db
        from PySide6.QtWidgets import QMessageBox
        from PySide6.QtCore import QSettings
        s = QSettings("OpenPrintKit", "OPKStudio")
        db_path = Path(s.value("app/opt_db_path", str(Path.home() / ".opk" / "openprinttag.sqlite")))
        try:
            con = db.connect(db_path)
            db.save_tag(con, self._collect_opt())
            con.close()
        except Exception as e:
            QMessageBox.critical(self, "Database", f"Failed to save tag to DB:\n{e}")
            return
        QMessageBox.information(self, "Database", f"Saved to {db_path}")

    def _opt_db_load(self):
        from ..integrations import db
        from PySide6.QtWidgets import QMessageBox, QInputDialog
        from PySide6.QtCore import QSettings
        s = QSettings("OpenPrintKit", "OPKStudio")
        db_path = Path(s.value("app/opt_db_path", str(Path.home() / ".opk" / "openprinttag.sqlite")))
        tag_id, ok = QInputDialog.getText(self, "Load from DB", "Tag ID:")
        if not ok or not tag_id: return
        try:
            con = db.connect(db_path)
            tag = db.load_tag(con, tag_id)
            con.close()
        except Exception as e:
            QMessageBox.critical(self, "Database", f"Failed to load tag from DB:\n{e}")
            return
        if tag:
            self._apply_opt(tag)
        else:
            QMessageBox.information(self, "Database", "No record found.")

    def _opt_remote_search(self):
        from ..integrations import spool_sources as sources
        from PySide6.QtWidgets import QInputDialog, QMessageBox
        q, ok = QInputDialog.getText(self, "Search Online", "Query:")
        if not ok or not q: return
        # try each source (stubbed)
        results_total = 0
        for src in sources.list_sources():
            items = sources.search_remote(src, q)
            results_total += len(items)
        QMessageBox.information(self, "Online Search", f"Found {results_total} matches across sources (stubs).")

    def _opt_remote_sync(self):
        from ..integrations import spool_sources as sources
        from PySide6.QtWidgets import QMessageBox
        # attempt sync (stub)
        ok_any = False
        for src in sources.list_sources():
            ok_any = sources.sync_remote(src, self._collect_opt()) or ok_any
        if ok_any:
            QMessageBox.information(self, "Online Sync", "Sync completed (stub).")
        else:
            QMessageBox.information(self, "Online Sync", "No remote sync performed (stubs only).")

    # --- Firmware-specific tips ---
    def _update_firmware_tips(self):
        fw = (self.f_firmware.currentText() or "").lower()
        tip = ""
        if fw in ("rrf","reprap","reprapfirmware","duet"):
            tip = (
                "RRF tips:\n"
                "- SD logging via M929 P\"filename\" S1 (stop: M929 S0).\n"
                "- Prefer named pins (e.g., out1) over numeric pins.\n"
                "- Fans use M106/M107 with P index; add 'Fans off at end' to emit M107.\n"
                "- RGB uses M150 R/G/B values."
            )
            self.pr_sd_enable.setToolTip("Start SD logging (RRF uses M929)")
            self.pr_sd_file.setToolTip("RRF: M929 P\"filename\" S1")
            self.pr_exhaust_pin.setToolTip("RRF: you can use named pins (e.g., out1) as string")
            self.pr_camera_cmd.setToolTip("RRF: use M240 if configured, or M42 with named pin")
        elif fw == "klipper":
            tip = (
                "Klipper tips:\n"
                "- Camera M240 maps to 'M118 TIMELAPSE_TAKE_FRAME' by policy.\n"
                "- M106/M107 are typically macros; ensure printer.cfg defines fans.\n"
                "- Consider using SET_FAN_SPEED FAN=name SPEED=s for fine control."
            )
            self.pr_camera_cmd.setToolTip("Klipper: override default with your macro command")
        elif fw == "grbl":
            tip = (
                "GRBL tips:\n"
                "- Exhaust uses coolant: M8 on / M9 off (M7 optional).\n"
                "- Fan commands are not standard; consider coolant or custom peripherals."
            )
        elif fw == "linuxcnc":
            tip = (
                "LinuxCNC tips:\n"
                "- Exhaust uses coolant: M7/M8 on / M9 off.\n"
                "- Fan commands are not standard; prefer HAL-driven peripherals."
            )
        elif fw == "bambu":
            tip = (
                "Bambu tips:\n"
                "- G-code is limited; keep start/end minimal.\n"
                "- Prefer built-in macros and studio-side settings."
            )
        elif fw in ("smoothie", "smoothieware"):
            tip = (
                "Smoothieware tips:\n"
                "- Fans use M106/M107; ensure fan modules are enabled in config.txt.\n"
                "- RGB via M150 may require LED module support."
            )
        elif fw == "repetier":
            tip = (
                "Repetier tips:\n"
                "- Fans use M106/M107; verify P index.\n"
                "- RGB (M150) support depends on build; use macros if unavailable."
            )
        else:
            tip = (
                "Marlin tips:\n"
                "- SD logging: M928 start / M29 stop.\n"
                "- RGB via M150 requires LED/NeoPixel support.\n"
                "- Use numeric pins for M42; for fans use M106/M107."
            )
        if hasattr(self, 'lb_fw_tip'):
            self.lb_fw_tip.setText(tip)

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

    # --- Aux and Custom Peripherals helpers
    def _add_aux(self, default_label: str | None = None):
        r = self.t_aux.rowCount(); self.t_aux.insertRow(r)
        self.t_aux.setItem(r, 0, QTableWidgetItem(default_label or f"Aux{r+1}"))
        self.t_aux.setItem(r, 1, QTableWidgetItem(""))
        self.t_aux.setItem(r, 2, QTableWidgetItem(""))
        self.t_aux.setItem(r, 3, QTableWidgetItem(""))

    def _del_aux(self):
        rows = sorted({i.row() for i in self.t_aux.selectedItems()}, reverse=True)
        for r in rows:
            self.t_aux.removeRow(r)

    def _add_cper(self):
        r = self.t_cper.rowCount(); self.t_cper.insertRow(r)
        self.t_cper.setItem(r, 0, QTableWidgetItem("Peripheral"))
        hook_combo = QComboBox(); hook_combo.setEditable(True)
        for h in self._current_hook_options():
            hook_combo.addItem(h)
        hook_combo.setCurrentText("start")
        self.t_cper.setCellWidget(r, 1, hook_combo)
        te = QTextEdit(); te.setPlaceholderText("M42 Pnn Snnn\n; or other M-code(s)")
        self.t_cper.setCellWidget(r, 2, te)

    def _del_cper(self):
        rows = sorted({i.row() for i in self.t_cper.selectedItems()}, reverse=True)
        for r in rows:
            self.t_cper.removeRow(r)

    def _current_hook_options(self) -> List[str]:
        opts = set(EXPLICIT_HOOK_KEYS)
        # include any existing hooks in g_edits (explicit)
        opts.update(self.g_edits.keys())
        # include any free-form hooks table entries
        try:
            for r in range(self.t_hooks.rowCount()):
                it = self.t_hooks.item(r, 0)
                if it and it.text().strip():
                    opts.add(it.text().strip())
        except Exception:
            pass
        return sorted(opts)
