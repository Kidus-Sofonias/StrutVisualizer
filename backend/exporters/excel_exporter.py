"""
Excel Exporter — Faithful reproduction of the original workbook structure.
Each section gets its own sheet with formulas matching the original calculation logic.
"""
import os
import math
from datetime import datetime
from typing import Optional, Dict, List
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, numbers
from openpyxl.chart import LineChart, BarChart, Reference
from openpyxl.utils import get_column_letter

from models.project import Project, ClassificationResult

# ── Styles ──────────────────────────────────────────────────────────────
BLUE_FILL = PatternFill(start_color="BDD7EE", end_color="BDD7EE", fill_type="solid")
RED_FILL = PatternFill(start_color="F4CCCC", end_color="F4CCCC", fill_type="solid")
GREEN_FILL = PatternFill(start_color="D9EAD3", end_color="D9EAD3", fill_type="solid")
YELLOW_FILL = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
HEADER_FILL = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
TITLE_FONT = Font(name="Calibri", size=14, bold=True, color="1F4E79")
SUBTITLE_FONT = Font(name="Calibri", size=12, bold=True, color="2E75B6")
NORMAL_FONT = Font(name="Calibri", size=11)
BOLD_FONT = Font(name="Calibri", size=11, bold=True)
THIN_BORDER = Border(
    left=Side(style="thin"), right=Side(style="thin"),
    top=Side(style="thin"), bottom=Side(style="thin"),
)
CENTER = Alignment(horizontal="center", vertical="center")
WRAP = Alignment(horizontal="left", wrap_text=True)


def _cell(ws, row, col, value, font=None, fill=None, fmt=None, align=None, border=True):
    c = ws.cell(row=row, column=col, value=value)
    if font: c.font = font
    if fill: c.fill = fill
    if fmt: c.number_format = fmt
    if align: c.alignment = align
    elif isinstance(value, (int, float)): c.alignment = CENTER
    if border: c.border = THIN_BORDER
    return c


def _header_row(ws, row, headers, col_start=1):
    for i, h in enumerate(headers):
        c = ws.cell(row=row, column=col_start + i, value=h)
        c.font = Font(name="Calibri", size=10, bold=True, color="FFFFFF")
        c.fill = HEADER_FILL
        c.border = THIN_BORDER
        c.alignment = Alignment(horizontal="center", wrap_text=True)
    return row + 1


def _title(ws, row, text, col=2):
    ws.cell(row=row, column=col, value=text).font = TITLE_FONT
    return row + 1


def _subtitle(ws, row, text, col=2):
    ws.cell(row=row, column=col, value=text).font = SUBTITLE_FONT
    return row + 1


def _status_fill(status):
    if status in ("OK", "PASS", "NO SWAY"):
        return GREEN_FILL
    elif status in ("NOT OK", "FAIL", "SWAY"):
        return RED_FILL
    return None


def _fmt(v, d=3):
    if v is None or v == "" or v == "-":
        return "-"
    try:
        return round(float(v), d)
    except (TypeError, ValueError):
        return v


# ══════════════════════════════════════════════════════════════════════
# MAIN EXPORT FUNCTION
# ══════════════════════════════════════════════════════════════════════

def export_to_excel(project: Project, output_path: str, sections: Dict = None) -> str:
    wb = Workbook()
    wb.remove(wb.active)
    storeys = project.get_storeys_sorted()

    # Sheet 1: 3.2 Structural Regularity (all sub-tables on one sheet)
    _create_3_2_sheet(wb, project, storeys)

    # Sheet 2: STORY DATA
    _create_story_data_sheet(wb, project, storeys)

    # Sheet 3+: Other sections
    if sections:
        sec_builders = {
            "3.3": _create_3_3_sheet,
            "3.4": _create_3_4_sheet,
            "4.1": _create_4_1_sheet,
            "4.2": _create_4_2_sheet,
            "4.3": _create_4_3_sheet,
            "4.4": _create_4_4_sheet,
            "4.5": _create_4_5_sheet,
            "4.6": _create_4_6_sheet,
        }
        for sec_id in ["3.3", "3.4", "4.1", "4.2", "4.3", "4.4", "4.5", "4.6"]:
            if sec_id in sections and sec_id in sec_builders:
                sec_builders[sec_id](wb, project, storeys, sections[sec_id])

    wb.save(output_path)
    return output_path


# ══════════════════════════════════════════════════════════════════════
# STORY DATA SHEET
# ══════════════════════════════════════════════════════════════════════

def _create_story_data_sheet(wb, project, storeys):
    ws = wb.create_sheet("STORY DATA")
    r = 1
    r = _title(ws, r, "Storey Height for Building")
    r += 1
    r = _header_row(ws, r, ["", "Story", "Height", "Elevation"], 1)
    for s in storeys:
        _cell(ws, r, 2, s.normalized_name)
        _cell(ws, r, 3, _fmt(s.source_data.height, 2))
        _cell(ws, r, 4, _fmt(s.source_data.elevation, 2))
        r += 1


# ══════════════════════════════════════════════════════════════════════
# 3.2 STRUCTURAL REGULARITY
# ══════════════════════════════════════════════════════════════════════

def _create_3_2_sheet(wb, project, storeys):
    ws = wb.create_sheet("3.2 Structural Regularity")
    r = 1
    lam = round(project.lmax / project.lmin, 4) if project.lmin > 0 else 0

    # Header
    r = _title(ws, r, "3.2 Structural Regularity")
    _cell(ws, r - 1, 7, "Project:", font=SUBTITLE_FONT, border=False)
    _cell(ws, r - 1, 8, project.project_name, border=False)
    _cell(ws, r, 7, "Client:", font=SUBTITLE_FONT, border=False)
    _cell(ws, r, 8, project.client or "N/A", border=False)
    r += 2

    # ── 3.2.1 Slenderness ──
    r = _subtitle(ws, r, "3.2.1. Regularity in Plan")
    r = _subtitle(ws, r, f"Slenderness: \u03bb = Lmax/Lmin = {project.lmax}/{project.lmin} = {lam}")
    _cell(ws, r, 2, "Status:", font=BOLD_FONT, border=False)
    _cell(ws, r, 3, "OK" if lam < 4 else "NOT OK", fill=GREEN_FILL if lam < 4 else RED_FILL)
    r += 2

    # ── 3.2.2 Structural Eccentricity ──
    r = _subtitle(ws, r, "Table 3.2.2: Structural Eccentricity of the Building")
    r = _header_row(ws, r, ["", "Story", "Xcm (m)", "Ycm (m)", "Xcr (m)", "Ycr (m)", "eox (m)", "eoy (m)"])
    t322_start = r
    for s in storeys:
        sd = s.source_data
        eox = _fmt(sd.xcm - sd.xcr) if sd.xcm is not None and sd.xcr is not None else None
        eoy = _fmt(sd.ycm - sd.ycr) if sd.ycm is not None and sd.ycr is not None else None
        _cell(ws, r, 2, s.normalized_name)
        _cell(ws, r, 3, _fmt(sd.xcm))
        _cell(ws, r, 4, _fmt(sd.ycm))
        _cell(ws, r, 5, _fmt(sd.xcr))
        _cell(ws, r, 6, _fmt(sd.ycr))
        _cell(ws, r, 7, eox)
        _cell(ws, r, 8, eoy)
        r += 1
    r += 1

    # ── 3.2.3 Torsional Radius ──
    r = _subtitle(ws, r, "Table 3.2.3: Torsional Radius of the Building")
    r = _header_row(ws, r, ["", "Story", "UX(UL1) (m)", "UY(UL2) (m)", "RZ(UL3) (rad)",
                            "KFX (kN/m)", "KFY (kN/m)", "KMT (kN/m)", "rx (m)", "ry (m)"])
    for s in storeys:
        c = s.calculations
        sd = s.source_data
        _cell(ws, r, 2, s.normalized_name)
        _cell(ws, r, 3, _fmt(sd.ux_ul1, 4))
        _cell(ws, r, 4, _fmt(sd.uy_ul2, 4))
        _cell(ws, r, 5, _fmt(sd.rz_ul3, 5))
        _cell(ws, r, 6, _fmt(c.kfx, 6))
        _cell(ws, r, 7, _fmt(c.kfy, 6))
        _cell(ws, r, 8, _fmt(c.kmt, 4))
        _cell(ws, r, 9, _fmt(c.rx))
        _cell(ws, r, 10, _fmt(c.ry))
        r += 1
    r += 1

    # ── 3.2.4 Eccentricity vs Gyration Comparison ──
    r = _subtitle(ws, r, "Table 3.2.4: Structural Eccentricity and Radius of Gyration Comparison")
    r = _header_row(ws, r, ["", "Story", "eox (m)", "rx (m)", "0.3\u00b7rx (m)", "Status",
                            "eoy (m)", "ry (m)", "0.3\u00b7ry (m)", "Status"])
    for s in storeys:
        c = s.calculations
        _cell(ws, r, 2, s.normalized_name)
        _cell(ws, r, 3, _fmt(abs(c.eox) if c.eox else None))
        _cell(ws, r, 4, _fmt(c.rx))
        _cell(ws, r, 5, _fmt(c.module_3_2_4_limit_x))
        _cell(ws, r, 6, c.module_3_2_4_eox_status or "-", fill=_status_fill(c.module_3_2_4_eox_status))
        _cell(ws, r, 7, _fmt(abs(c.eoy) if c.eoy else None))
        _cell(ws, r, 8, _fmt(c.ry))
        _cell(ws, r, 9, _fmt(c.module_3_2_4_limit_y))
        _cell(ws, r, 10, c.module_3_2_4_eoy_status or "-", fill=_status_fill(c.module_3_2_4_eoy_status))
        r += 1
    r += 1

    # ── 3.2.5 Torsional Radius vs Floor Radius ──
    r = _subtitle(ws, r, "Table 3.2.5: Torsional Radius and Radius of Gyration Comparison")
    r = _header_row(ws, r, ["", "Story", "rx (m)", "ls (m)", "Status", "ry (m)", "ls (m)", "Status"])
    for s in storeys:
        c = s.calculations
        _cell(ws, r, 2, s.normalized_name)
        _cell(ws, r, 3, _fmt(c.rx))
        _cell(ws, r, 4, _fmt(c.ls))
        _cell(ws, r, 5, c.module_3_2_5_rx_status or "-", fill=_status_fill(c.module_3_2_5_rx_status))
        _cell(ws, r, 6, _fmt(c.ry))
        _cell(ws, r, 7, _fmt(c.ls))
        _cell(ws, r, 8, c.module_3_2_5_ry_status or "-", fill=_status_fill(c.module_3_2_5_ry_status))
        r += 1
    r += 1

    # ── 3.2.6 Stiffness X ──
    r = _subtitle(ws, r, "Table 3.2.6: Storey Stiffness along X Direction of the Building")
    _cell(ws, r, 5, "EQX", font=SUBTITLE_FONT, border=False)
    r += 1
    t326_start = r
    r = _header_row(ws, r, ["", "Story", "Stiffness X axis (kN/m)", "Ki >0.7*Ki+1  X axis"])
    for s in storeys:
        c = s.calculations
        _cell(ws, r, 2, s.normalized_name)
        _cell(ws, r, 3, _fmt(c.kx, 1))
        _cell(ws, r, 4, c.module_3_2_6_status or "-", fill=_status_fill(c.module_3_2_6_status))
        r += 1
    t326_end = r - 1
    r += 1

    # ── 3.2.7 Stiffness Y ──
    r = _subtitle(ws, r, "Table 3.2.7: Storey Stiffness along Y Direction of the Building")
    _cell(ws, r, 5, "EQY", font=SUBTITLE_FONT, border=False)
    r += 1
    t327_start = r
    r = _header_row(ws, r, ["", "Story", "Stiffness Y axis (kN/m)", "Ki >0.7*Ki+1  Y axis"])
    for s in storeys:
        c = s.calculations
        _cell(ws, r, 2, s.normalized_name)
        _cell(ws, r, 3, _fmt(c.ky, 1))
        _cell(ws, r, 4, c.module_3_2_7_status or "-", fill=_status_fill(c.module_3_2_7_status))
        r += 1
    t327_end = r - 1
    r += 1

    # ── 3.2.8 Mass Distribution ──
    r = _subtitle(ws, r, "Table 3.2.8: Mass Distribution along height of the Building")
    r = _header_row(ws, r, ["", "Story", "Mass (1000 x Kg)", "Mi < 2Mi+1", "Mi < 2Mi-1"])
    for s in storeys:
        c = s.calculations
        _cell(ws, r, 2, s.normalized_name)
        _cell(ws, r, 3, _fmt(c.module_3_2_8_mass, 4))
        su = c.module_3_2_8_status_upper or "-"
        sl = c.module_3_2_8_status_lower or "-"
        _cell(ws, r, 4, su, fill=_status_fill(su))
        _cell(ws, r, 5, sl, fill=_status_fill(sl))
        r += 1
    r += 1

    # ── Building Summary ──
    r = _subtitle(ws, r, "Building Summary")
    if project.building_summary:
        for line in project.building_summary.split("\n"):
            _cell(ws, r, 2, line, border=False)
            r += 1
    r += 1

    # ── Charts ──
    chart_row = r + 1
    if t326_start <= t326_end:
        chart = LineChart()
        chart.title = "Stiffness X axis (kN/m)"
        chart.y_axis.title = "Stiffness (kN/m)"
        chart.width = 20
        chart.height = 12
        cats = Reference(ws, min_col=2, min_row=t326_start, max_row=t326_end)
        vals = Reference(ws, min_col=3, min_row=t326_start - 1, max_row=t326_end)
        chart.add_data(vals, titles_from_data=True)
        chart.set_categories(cats)
        ws.add_chart(chart, "F" + str(chart_row))

    if t327_start <= t327_end:
        chart = LineChart()
        chart.title = "Stiffness Y axis (kN/m)"
        chart.y_axis.title = "Stiffness (kN/m)"
        chart.width = 20
        chart.height = 12
        cats = Reference(ws, min_col=2, min_row=t327_start, max_row=t327_end)
        vals = Reference(ws, min_col=3, min_row=t327_start - 1, max_row=t327_end)
        chart.add_data(vals, titles_from_data=True)
        chart.set_categories(cats)
        ws.add_chart(chart, "F" + str(chart_row + 16))


# ══════════════════════════════════════════════════════════════════════
# 3.3 LATERAL FORCE PARTICIPATION
# ══════════════════════════════════════════════════════════════════════

def _create_3_3_sheet(wb, project, storeys, data):
    ws = wb.create_sheet("3.3 Lateral Force Participation")
    r = 1
    r = _title(ws, r, "3.3 Building Classification")
    r += 1

    bc = data.get("building_classification", "N/A")
    _cell(ws, r, 2, "Building Classification:", font=BOLD_FONT, border=False)
    _cell(ws, r, 4, bc)
    r += 2

    # X-Direction
    xd = data.get("x_direction", {})
    r = _subtitle(ws, r, "Along X-Direction (UL1)")
    r = _header_row(ws, r, ["", "Story", "Lateral Load", "Column Load", "Shear Wall Load",
                            "Column %", "Shear Wall %"])
    x_start = r
    for s in xd.get("storeys", []):
        _cell(ws, r, 2, s.get("name", ""))
        _cell(ws, r, 3, _fmt(s.get("lateral"), 0))
        _cell(ws, r, 4, _fmt(s.get("column_force"), 2))
        _cell(ws, r, 5, _fmt(s.get("wall_force"), 2))
        _cell(ws, r, 6, _fmt(s.get("column_pct", 0) * 100, 1) if s.get("column_pct") is not None else "-")
        _cell(ws, r, 7, _fmt(s.get("wall_pct", 0) * 100, 1) if s.get("wall_pct") is not None else "-")
        r += 1
    x_end = r - 1

    # Load participation summary
    r += 1
    _cell(ws, r, 2, "Load Participation", font=BOLD_FONT, border=False)
    r += 1
    col_pct = xd.get("column_pct", 0)
    wall_pct = xd.get("wall_pct", 0)
    _cell(ws, r, 2, "Column:", border=False)
    _cell(ws, r, 3, _fmt(col_pct * 100, 2) if col_pct else "-")
    _cell(ws, r, 4, "%", border=False)
    r += 1
    _cell(ws, r, 2, "Wall:", border=False)
    _cell(ws, r, 3, _fmt(wall_pct * 100, 2) if wall_pct else "-")
    _cell(ws, r, 4, "%", border=False)
    r += 2

    # Y-Direction
    yd = data.get("y_direction", {})
    r = _subtitle(ws, r, "Along Y-Direction (UL2)")
    r = _header_row(ws, r, ["", "Story", "Lateral Load", "Column Load", "Shear Wall Load",
                            "Column %", "Shear Wall %"])
    for s in yd.get("storeys", []):
        _cell(ws, r, 2, s.get("name", ""))
        _cell(ws, r, 3, _fmt(s.get("lateral"), 0))
        _cell(ws, r, 4, _fmt(s.get("column_force"), 2))
        _cell(ws, r, 5, _fmt(s.get("wall_force"), 2))
        _cell(ws, r, 6, _fmt(s.get("column_pct", 0) * 100, 1) if s.get("column_pct") is not None else "-")
        _cell(ws, r, 7, _fmt(s.get("wall_pct", 0) * 100, 1) if s.get("wall_pct") is not None else "-")
        r += 1

    r += 1
    _cell(ws, r, 2, f"The structure is categorized as {bc}", font=BOLD_FONT, border=False)


# ══════════════════════════════════════════════════════════════════════
# 3.4 BEHAVIORAL FACTOR
# ══════════════════════════════════════════════════════════════════════

def _create_3_4_sheet(wb, project, storeys, data):
    ws = wb.create_sheet("3.4 Behavioral Factor")
    r = 1
    r = _title(ws, r, "3.4 Behavioral Factor (q)")
    r += 2

    r = _subtitle(ws, r, "q = q\u2080 \u00d7 kw \u00d7 (\u03b1u/\u03b11)")
    r += 1

    params = [
        ("Building Type", data.get("building_type", "")),
        ("q\u2080", data.get("qo", "")),
        ("kw", data.get("kw", "")),
        ("\u03b1u/\u03b11", data.get("alpha_ratio", "")),
        ("q (X)", data.get("qx", "")),
        ("q (Y)", data.get("qy", "")),
        ("q (design)", data.get("q", "")),
        ("Plan Regularity", data.get("regularity_plan", "")),
        ("Elevation Regularity", data.get("regularity_elevation", "")),
    ]
    r = _header_row(ws, r, ["", "Parameter", "Value"])
    for label, val in params:
        _cell(ws, r, 2, label)
        _cell(ws, r, 3, str(val) if val is not None else "-")
        r += 1


# ══════════════════════════════════════════════════════════════════════
# 4.1 BASE SHEAR
# ══════════════════════════════════════════════════════════════════════

def _create_4_1_sheet(wb, project, storeys, data):
    ws = wb.create_sheet("4.1 Base Shear")
    r = 1
    r = _title(ws, r, "4.1 Base Shear Calculation")
    r += 2

    # Spectrum parameters
    r = _subtitle(ws, r, "Seismic Parameters")
    params = [
        ("ag", f"{data.get('ag', '')} g"),
        ("Ground Type", data.get("ground_type", "")),
        ("S", data.get("S", "")),
        ("TB", f"{data.get('TB', '')} s"),
        ("TC", f"{data.get('TC', '')} s"),
        ("TD", f"{data.get('TD', '')} s"),
        ("\u03b2", data.get("beta", "")),
        ("q", data.get("q", "")),
    ]
    r = _header_row(ws, r, ["", "Parameter", "Value"])
    for label, val in params:
        _cell(ws, r, 2, label)
        _cell(ws, r, 3, str(val) if val is not None else "-")
        r += 1
    r += 1

    # Fundamental periods
    r = _subtitle(ws, r, "Fundamental Periods")
    _cell(ws, r, 2, "T1x:", font=BOLD_FONT, border=False)
    _cell(ws, r, 3, data.get("T1x", ""))
    _cell(ws, r, 4, "s", border=False)
    _cell(ws, r, 5, "T1y:", font=BOLD_FONT, border=False)
    _cell(ws, r, 6, data.get("T1y", ""))
    _cell(ws, r, 7, "s", border=False)
    r += 2

    # Spectrum equations
    r = _subtitle(ws, r, "Design Spectrum Sd(T)")
    eqs = [
        "0 \u2264 T \u2264 TB:  Sd(T) = ag \u00d7 S \u00d7 (2/3 + T/TB \u00d7 (2.5/q \u2212 2/3))",
        "TB \u2264 T \u2264 TC:  Sd(T) = ag \u00d7 S \u00d7 2.5/q",
        "TC \u2264 T \u2264 TD:  Sd(T) = ag \u00d7 S \u00d7 2.5/q \u00d7 (TC/T)",
        "T > TD:  Sd(T) = ag \u00d7 S \u00d7 2.5/q \u00d7 (TC \u00d7 TD / T\u00b2)",
    ]
    for eq in eqs:
        _cell(ws, r, 2, eq, font=Font(name="Consolas", size=10, color="1F4E79"), border=False)
        r += 1
    r += 1

    # Results
    r = _subtitle(ws, r, "Base Shear Results")
    r = _header_row(ws, r, ["", "Direction", "Fb (kN)", "Lower Bound (kN)", "Governing (kN)", "Weight (kN)"])
    _cell(ws, r, 2, "X")
    _cell(ws, r, 3, _fmt(data.get("Fb_x"), 2))
    _cell(ws, r, 4, _fmt(data.get("lower_bound_x"), 2))
    _cell(ws, r, 5, _fmt(data.get("governing_x", data.get("Fb_x")), 2))
    _cell(ws, r, 6, _fmt(data.get("total_weight_kN"), 0))
    r += 1
    _cell(ws, r, 2, "Y")
    _cell(ws, r, 3, _fmt(data.get("Fb_y"), 2))
    _cell(ws, r, 4, _fmt(data.get("lower_bound_y"), 2))
    _cell(ws, r, 5, _fmt(data.get("governing_y", data.get("Fb_y")), 2))
    _cell(ws, r, 6, _fmt(data.get("total_weight_kN"), 0))


# ══════════════════════════════════════════════════════════════════════
# 4.2 MODAL LOAD PARTICIPATION
# ══════════════════════════════════════════════════════════════════════

def _create_4_2_sheet(wb, project, storeys, data):
    ws = wb.create_sheet("4.2 Modal Load Participation")
    r = 1
    r = _title(ws, r, "4.2 Modal Load Participation")
    r += 1

    _cell(ws, r, 2, "T1x:", font=BOLD_FONT, border=False)
    _cell(ws, r, 3, _fmt(data.get("T1x"), 4))
    _cell(ws, r, 4, "s", border=False)
    _cell(ws, r, 5, "T1y:", font=BOLD_FONT, border=False)
    _cell(ws, r, 6, _fmt(data.get("T1y"), 4))
    _cell(ws, r, 7, "s", border=False)
    r += 2

    modes = data.get("modes", [])
    if modes:
        r = _header_row(ws, r, ["", "Mode", "Period (s)", "UX (%)", "UY (%)", "RZ (%)",
                                "\u03a3UX (%)", "\u03a3UY (%)"])
        for m in modes[:50]:
            _cell(ws, r, 2, m.get("mode", ""))
            _cell(ws, r, 3, _fmt(m.get("period"), 6))
            _cell(ws, r, 4, _fmt(m.get("ux"), 4))
            _cell(ws, r, 5, _fmt(m.get("uy"), 4))
            _cell(ws, r, 6, _fmt(m.get("rz"), 4))
            _cell(ws, r, 7, _fmt(m.get("sum_ux"), 2))
            _cell(ws, r, 8, _fmt(m.get("sum_uy"), 2))
            r += 1


# ══════════════════════════════════════════════════════════════════════
# 4.3 GEOMETRIC IMPERFECTION
# ══════════════════════════════════════════════════════════════════════

def _create_4_3_sheet(wb, project, storeys, data):
    ws = wb.create_sheet("4.3 Geometric Imperfection")
    r = 1
    r = _title(ws, r, "4.3 Geometric Imperfections")
    r += 2

    # Parameters
    r = _subtitle(ws, r, "\u03b8i = \u03b8\u2080 \u00d7 \u03b1h \u00d7 \u03b1m")
    params = [
        ("\u03b8\u2080", data.get("theta0", 0.005)),
        ("\u03b1h", data.get("alpha_h", 1.0)),
        ("\u03b1m", data.get("alpha_m", 0.723)),
        ("\u03b8i", data.get("theta_i", "")),
    ]
    r = _header_row(ws, r, ["", "Parameter", "Value"])
    for label, val in params:
        _cell(ws, r, 2, label)
        _cell(ws, r, 3, _fmt(val, 6) if isinstance(val, (int, float)) else str(val))
        r += 1
    r += 1

    # Storey table
    r = _subtitle(ws, r, "Imperfection Forces")
    r = _header_row(ws, r, ["", "Story", "Ptot (kN)", "\u03b8\u2080", "L(h)", "m",
                            "\u03b1h", "\u03b1m", "\u03b8i", "Hi (kN)"])
    for s in data.get("storeys", []):
        _cell(ws, r, 2, s.get("name", ""))
        _cell(ws, r, 3, _fmt(s.get("ptot"), 2))
        _cell(ws, r, 4, s.get("theta0", 0.005))
        _cell(ws, r, 5, _fmt(s.get("l_h") or s.get("height"), 2))
        _cell(ws, r, 6, s.get("m", ""))
        _cell(ws, r, 7, s.get("alpha_h", 1.0))
        _cell(ws, r, 8, _fmt(s.get("alpha_m"), 6))
        _cell(ws, r, 9, _fmt(s.get("theta_i"), 6))
        _cell(ws, r, 10, _fmt(s.get("hi"), 2), fill=BLUE_FILL)
        r += 1


# ══════════════════════════════════════════════════════════════════════
# 4.4 STABILITY ANALYSIS (P-DELTA)
# ══════════════════════════════════════════════════════════════════════

def _create_4_4_sheet(wb, project, storeys, data):
    ws = wb.create_sheet("4.4 Stability Analysis")
    r = 1
    r = _title(ws, r, "4.4 Stability Analysis (P-Delta)")
    r += 2

    # Max values
    r = _subtitle(ws, r, "Maximum Values")
    _cell(ws, r, 2, "Max \u03b8x:", font=BOLD_FONT, border=False)
    _cell(ws, r, 3, _fmt(data.get("max_theta_x"), 8))
    _cell(ws, r, 5, "Max \u03b8y:", font=BOLD_FONT, border=False)
    _cell(ws, r, 6, _fmt(data.get("max_theta_y"), 8))
    r += 1
    _cell(ws, r, 2, "X Classification:", font=BOLD_FONT, border=False)
    _cell(ws, r, 3, data.get("max_classification_x", ""), fill=_status_fill(data.get("max_classification_x")))
    _cell(ws, r, 5, "Y Classification:", font=BOLD_FONT, border=False)
    _cell(ws, r, 6, data.get("max_classification_y", ""), fill=_status_fill(data.get("max_classification_y")))
    r += 2

    # Formula
    r = _subtitle(ws, r, "\u03b8 = \u03a3Pu \u00d7 \u0394u / (Hu \u00d7 hs)")
    r += 1

    # Storey table matching original format
    r = _header_row(ws, r, ["", "Storey", "Combination", "Ptot (kN)", "Height (m)",
                            "Hu X (kN)", "Hu Y (kN)", "dr X (m)", "dr Y (m)",
                            "\u03b8x", "\u03b8y", "Along X", "Along Y"])
    for s in data.get("storeys", []):
        _cell(ws, r, 2, s.get("name", ""))
        _cell(ws, r, 3, s.get("load_case", ""))
        _cell(ws, r, 4, _fmt(s.get("ptot"), 2))
        _cell(ws, r, 5, _fmt(s.get("height"), 2))
        hu = s.get("hu", 0)
        dr = s.get("delta_u", 0)
        theta = s.get("theta", 0)
        classification = s.get("classification", "")

        if s.get("direction") == "X":
            _cell(ws, r, 6, _fmt(hu, 2))
            _cell(ws, r, 8, _fmt(dr, 6))
            _cell(ws, r, 10, _fmt(theta, 6))
            _cell(ws, r, 12, classification, fill=_status_fill(classification))
        else:
            _cell(ws, r, 7, _fmt(hu, 2))
            _cell(ws, r, 9, _fmt(dr, 6))
            _cell(ws, r, 11, _fmt(theta, 6))
            _cell(ws, r, 13, classification, fill=_status_fill(classification))
        r += 1


# ══════════════════════════════════════════════════════════════════════
# 4.5 STOREY DRIFT CONTROL
# ══════════════════════════════════════════════════════════════════════

def _create_4_5_sheet(wb, project, storeys, data):
    ws = wb.create_sheet("4.5 Storey Drift Control")
    r = 1
    r = _title(ws, r, "4.5 Damage Limitation")
    r += 2

    # Parameters
    _cell(ws, r, 2, "\u03bd (reduction factor):", font=BOLD_FONT, border=False)
    _cell(ws, r, 4, data.get("nu", 0.5))
    _cell(ws, r, 5, "Limit:", font=BOLD_FONT, border=False)
    _cell(ws, r, 6, data.get("limit", 0.005))
    r += 1
    _cell(ws, r, 2, "Max X-Drift:", font=BOLD_FONT, border=False)
    _cell(ws, r, 3, _fmt(data.get("max_ratio_x"), 6))
    _cell(ws, r, 5, "Max Y-Drift:", font=BOLD_FONT, border=False)
    _cell(ws, r, 6, _fmt(data.get("max_ratio_y"), 6))
    r += 2

    # Storey table
    r = _header_row(ws, r, ["", "Story", "Combination", "dr X (m)", "dr Y (m)",
                            "Story Height", "\u03bd\u00b7dr/h (X)", "\u03bd\u00b7dr/h (Y)",
                            "X Status", "Y Status"])
    for s in data.get("storeys", []):
        _cell(ws, r, 2, s.get("name", ""))
        _cell(ws, r, 3, s.get("load_case", ""))
        _cell(ws, r, 4, _fmt(s.get("dr"), 6) if s.get("direction") == "X" else "")
        _cell(ws, r, 5, _fmt(s.get("dr"), 6) if s.get("direction") == "Y" else "")
        _cell(ws, r, 6, _fmt(s.get("height"), 2))
        if s.get("direction") == "X":
            _cell(ws, r, 7, _fmt(s.get("nu_dr_h"), 6))
            _cell(ws, r, 9, s.get("status", ""), fill=_status_fill(s.get("status")))
        else:
            _cell(ws, r, 8, _fmt(s.get("nu_dr_h"), 6))
            _cell(ws, r, 10, s.get("status", ""), fill=_status_fill(s.get("status")))
        r += 1


# ══════════════════════════════════════════════════════════════════════
# 4.6 OVERTURNING CHECK
# ══════════════════════════════════════════════════════════════════════

def _create_4_6_sheet(wb, project, storeys, data):
    ws = wb.create_sheet("4.6 Overturning Check")
    r = 1
    r = _title(ws, r, "4.6 Building Overturning Check")
    r += 2

    _cell(ws, r, 2, "Total Weight:", font=BOLD_FONT, border=False)
    _cell(ws, r, 3, _fmt(data.get("total_weight_kN"), 0))
    _cell(ws, r, 4, "kN", border=False)
    _cell(ws, r, 5, "Required SF:", font=BOLD_FONT, border=False)
    _cell(ws, r, 6, data.get("required_sf", 1.5))
    r += 2

    # X-Direction
    xd = data.get("x_direction", {})
    r = _subtitle(ws, r, "Along X-Direction")
    _cell(ws, r, 5, f"Distance of Building Center: {data.get('ground_xcm', '')} m", border=False)
    r += 1
    r = _header_row(ws, r, ["", "Story", "Story Height", "Elevation", "Story Shear (kN)", "OT Moment (kN\u00b7m)"])
    for s in xd.get("storeys", []):
        _cell(ws, r, 2, s.get("name", ""))
        _cell(ws, r, 3, _fmt(s.get("height") or s.get("elevation"), 2))
        _cell(ws, r, 4, _fmt(s.get("elevation"), 2))
        _cell(ws, r, 5, _fmt(s.get("shear"), 2))
        _cell(ws, r, 6, _fmt(s.get("ot_moment"), 2))
        r += 1

    r += 1
    _cell(ws, r, 4, "Total Overturning Moment:", font=BOLD_FONT, border=False)
    _cell(ws, r, 6, _fmt(xd.get("total_ot_moment"), 2))
    r += 1
    _cell(ws, r, 4, "Resisting Moment:", font=BOLD_FONT, border=False)
    _cell(ws, r, 6, _fmt(xd.get("resisting_moment"), 2))
    r += 1
    _cell(ws, r, 4, "Safety Factor:", font=BOLD_FONT, border=False)
    _cell(ws, r, 5, _fmt(xd.get("safety_factor"), 4))
    _cell(ws, r, 6, "\u2265 1.5", border=False)
    _cell(ws, r, 7, xd.get("passes", False), fill=GREEN_FILL if xd.get("passes") else RED_FILL)
    r += 2

    # Y-Direction
    yd = data.get("y_direction", {})
    r = _subtitle(ws, r, "Along Y-Direction")
    _cell(ws, r, 5, f"Distance of Building Center: {data.get('ground_ycm', '')} m", border=False)
    r += 1
    r = _header_row(ws, r, ["", "Story", "Story Height", "Elevation", "Story Shear (kN)", "OT Moment (kN\u00b7m)"])
    for s in yd.get("storeys", []):
        _cell(ws, r, 2, s.get("name", ""))
        _cell(ws, r, 3, _fmt(s.get("height") or s.get("elevation"), 2))
        _cell(ws, r, 4, _fmt(s.get("elevation"), 2))
        _cell(ws, r, 5, _fmt(s.get("shear"), 2))
        _cell(ws, r, 6, _fmt(s.get("ot_moment"), 2))
        r += 1

    r += 1
    _cell(ws, r, 4, "Total Overturning Moment:", font=BOLD_FONT, border=False)
    _cell(ws, r, 6, _fmt(yd.get("total_ot_moment"), 2))
    r += 1
    _cell(ws, r, 4, "Resisting Moment:", font=BOLD_FONT, border=False)
    _cell(ws, r, 6, _fmt(yd.get("resisting_moment"), 2))
    r += 1
    _cell(ws, r, 4, "Safety Factor:", font=BOLD_FONT, border=False)
    _cell(ws, r, 5, _fmt(yd.get("safety_factor"), 4))
    _cell(ws, r, 6, "\u2265 1.5", border=False)
    _cell(ws, r, 7, yd.get("passes", False), fill=GREEN_FILL if yd.get("passes") else RED_FILL)
