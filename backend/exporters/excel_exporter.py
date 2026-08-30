"""
Excel Exporter — Faithful reproduction of the original workbook structure.
Each section gets its own sheet with formulas matching the original calculation logic.

Charts:
1. Stiffness X axis (kN/m) — line chart
2. Stiffness Y axis (kN/m) — line chart
3. Elastic vs Design Displacement X — horizontal bar
4. Elastic vs Design Displacement Y — horizontal bar
"""
import os
import math
from datetime import datetime
from typing import Optional, Dict, List
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, numbers
from openpyxl.chart import LineChart, BarChart, Reference
from openpyxl.chart.series import SeriesLabel
from openpyxl.chart.label import DataLabelList
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

    # Sheet 1: Story Data
    _create_story_data_sheet(wb, project, storeys)

    # Sheet 2: 3.2 Structural Regularity (all 8 sub-tables + 4 charts)
    _create_3_2_sheet(wb, project, storeys)

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

    # Last sheet: Calculation Audit
    _create_audit_sheet(wb, project, sections)

    wb.save(output_path)
    return output_path


# ══════════════════════════════════════════════════════════════════════
# STORY DATA SHEET
# ══════════════════════════════════════════════════════════════════════

def _create_story_data_sheet(wb, project, storeys):
    ws = wb.create_sheet("Story Data")
    r = 1
    r = _title(ws, r, "Storey Data for Building")
    r += 1
    r = _header_row(ws, r, ["#", "Story", "Height (m)", "Elevation (m)", "Mass (t)",
                            "Xcm (m)", "Ycm (m)", "Xcr (m)", "Ycr (m)"], 1)
    for i, s in enumerate(storeys):
        sd = s.source_data
        _cell(ws, r, 1, i + 1)
        _cell(ws, r, 2, s.normalized_name)
        _cell(ws, r, 3, _fmt(sd.height, 2))
        _cell(ws, r, 4, _fmt(sd.elevation, 2))
        _cell(ws, r, 5, _fmt(sd.mass, 2))
        _cell(ws, r, 6, _fmt(sd.xcm, 3))
        _cell(ws, r, 7, _fmt(sd.ycm, 3))
        _cell(ws, r, 8, _fmt(sd.xcr, 3))
        _cell(ws, r, 9, _fmt(sd.ycr, 3))
        r += 1


# ══════════════════════════════════════════════════════════════════════
# 3.2 STRUCTURAL REGULARITY — All 8 tables + 4 charts
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
    r = _subtitle(ws, r, "Table 3.2.1: Regularity in Plan — Slenderness")
    r = _header_row(ws, r, ["#", "Story", "Lmax (m)", "Lmin (m)", "λ = Lmax/Lmin", "λ < 4", "Status"])
    t321_start = r
    for i, s in enumerate(storeys):
        _cell(ws, r, 1, i + 1)
        _cell(ws, r, 2, s.normalized_name)
        _cell(ws, r, 3, _fmt(project.lmax, 2))
        _cell(ws, r, 4, _fmt(project.lmin, 2))
        _cell(ws, r, 5, _fmt(lam, 4))
        _cell(ws, r, 6, "YES" if lam < 4 else "NO")
        _cell(ws, r, 7, s.calculations.module_3_2_1_status or "OK",
              fill=_status_fill(s.calculations.module_3_2_1_status or "OK"))
        r += 1
    t321_end = r - 1
    r += 1

    # ── 3.2.2 Structural Eccentricity ──
    r = _subtitle(ws, r, "Table 3.2.2: Structural Eccentricity of the Building")
    r = _header_row(ws, r, ["#", "Story", "Xcm (m)", "Ycm (m)", "Xcr (m)", "Ycr (m)", "eox (m)", "eoy (m)"])
    t322_start = r
    for i, s in enumerate(storeys):
        sd = s.source_data
        eox = sd.xcm - sd.xcr if sd.xcm is not None and sd.xcr is not None else None
        eoy = sd.ycm - sd.ycr if sd.ycm is not None and sd.ycr is not None else None
        _cell(ws, r, 1, i + 1)
        _cell(ws, r, 2, s.normalized_name)
        _cell(ws, r, 3, _fmt(sd.xcm))
        _cell(ws, r, 4, _fmt(sd.ycm))
        _cell(ws, r, 5, _fmt(sd.xcr))
        _cell(ws, r, 6, _fmt(sd.ycr))
        _cell(ws, r, 7, _fmt(eox))
        _cell(ws, r, 8, _fmt(eoy))
        r += 1
    t322_end = r - 1
    r += 1

    # ── 3.2.3 Torsional Radius ──
    r = _subtitle(ws, r, "Table 3.2.3: Torsional Radius of the Building")
    r = _header_row(ws, r, ["#", "Story", "UX(UL1)", "UY(UL2)", "RZ(UL3)",
                            "KFX (kN/m)", "KFY (kN/m)", "KMT (kN/m)", "rx (m)", "ry (m)"])
    t323_start = r
    for i, s in enumerate(storeys):
        c = s.calculations
        sd = s.source_data
        _cell(ws, r, 1, i + 1)
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
    t323_end = r - 1
    r += 1

    # ── 3.2.4 Eccentricity vs Gyration ──
    r = _subtitle(ws, r, "Table 3.2.4: Eccentricity and Radius of Gyration Comparison")
    r = _header_row(ws, r, ["#", "Story", "|eox| (m)", "rx (m)", "0.3·rx (m)", "Status X",
                            "|eoy| (m)", "ry (m)", "0.3·ry (m)", "Status Y"])
    for i, s in enumerate(storeys):
        c = s.calculations
        _cell(ws, r, 1, i + 1)
        _cell(ws, r, 2, s.normalized_name)
        _cell(ws, r, 3, _fmt(abs(c.eox) if c.eox else None))
        _cell(ws, r, 4, _fmt(c.rx))
        _cell(ws, r, 5, _fmt(c.module_3_2_4_limit_x))
        _cell(ws, r, 6, c.module_3_2_4_eox_status or "-",
              fill=_status_fill(c.module_3_2_4_eox_status))
        _cell(ws, r, 7, _fmt(abs(c.eoy) if c.eoy else None))
        _cell(ws, r, 8, _fmt(c.ry))
        _cell(ws, r, 9, _fmt(c.module_3_2_4_limit_y))
        _cell(ws, r, 10, c.module_3_2_4_eoy_status or "-",
              fill=_status_fill(c.module_3_2_4_eoy_status))
        r += 1
    r += 1

    # ── 3.2.5 Torsional Radius vs Floor Radius ──
    r = _subtitle(ws, r, "Table 3.2.5: Torsional Radius and Radius of Gyration Comparison")
    r = _header_row(ws, r, ["#", "Story", "rx (m)", "ls (m)", "rx ≥ ls", "Status",
                            "ry (m)", "ls (m)", "ry ≥ ls", "Status"])
    for i, s in enumerate(storeys):
        c = s.calculations
        _cell(ws, r, 1, i + 1)
        _cell(ws, r, 2, s.normalized_name)
        _cell(ws, r, 3, _fmt(c.rx))
        _cell(ws, r, 4, _fmt(c.ls))
        _cell(ws, r, 5, "YES" if (c.rx or 0) >= (c.ls or 0) else "NO")
        _cell(ws, r, 6, c.module_3_2_5_rx_status or "-",
              fill=_status_fill(c.module_3_2_5_rx_status))
        _cell(ws, r, 7, _fmt(c.ry))
        _cell(ws, r, 8, _fmt(c.ls))
        _cell(ws, r, 9, "YES" if (c.ry or 0) >= (c.ls or 0) else "NO")
        _cell(ws, r, 10, c.module_3_2_5_ry_status or "-",
              fill=_status_fill(c.module_3_2_5_ry_status))
        r += 1
    r += 1

    # ── 3.2.6 Stiffness X ──
    r = _subtitle(ws, r, "Table 3.2.6: Storey Stiffness along X Direction (EQX)")
    r = _header_row(ws, r, ["#", "Story", "Stiffness X (kN/m)", "Ki > 0.7·Ki+1", "Status"])
    t326_start = r
    for i, s in enumerate(storeys):
        c = s.calculations
        _cell(ws, r, 1, i + 1)
        _cell(ws, r, 2, s.normalized_name)
        _cell(ws, r, 3, _fmt(c.kx, 1))
        _cell(ws, r, 4, "YES" if c.module_3_2_6_status == "OK" else "NO")
        _cell(ws, r, 5, c.module_3_2_6_status or "-",
              fill=_status_fill(c.module_3_2_6_status))
        r += 1
    t326_end = r - 1
    r += 1

    # ── 3.2.7 Stiffness Y ──
    r = _subtitle(ws, r, "Table 3.2.7: Storey Stiffness along Y Direction (EQY)")
    r = _header_row(ws, r, ["#", "Story", "Stiffness Y (kN/m)", "Ki > 0.7·Ki+1", "Status"])
    t327_start = r
    for i, s in enumerate(storeys):
        c = s.calculations
        _cell(ws, r, 1, i + 1)
        _cell(ws, r, 2, s.normalized_name)
        _cell(ws, r, 3, _fmt(c.ky, 1))
        _cell(ws, r, 4, "YES" if c.module_3_2_7_status == "OK" else "NO")
        _cell(ws, r, 5, c.module_3_2_7_status or "-",
              fill=_status_fill(c.module_3_2_7_status))
        r += 1
    t327_end = r - 1
    r += 1

    # ── 3.2.8 Mass Distribution ──
    r = _subtitle(ws, r, "Table 3.2.8: Mass Distribution along Height")
    r = _header_row(ws, r, ["#", "Story", "Mass (t)", "Mi < 2·Mi+1", "Mi < 2·Mi-1",
                            "Status Upper", "Status Lower"])
    t328_start = r
    for i, s in enumerate(storeys):
        c = s.calculations
        _cell(ws, r, 1, i + 1)
        _cell(ws, r, 2, s.normalized_name)
        _cell(ws, r, 3, _fmt(c.module_3_2_8_mass, 4))
        su = c.module_3_2_8_status_upper or "-"
        sl = c.module_3_2_8_status_lower or "-"
        _cell(ws, r, 4, su, fill=_status_fill(su))
        _cell(ws, r, 5, sl, fill=_status_fill(sl))
        _cell(ws, r, 6, su, fill=_status_fill(su))
        _cell(ws, r, 7, sl, fill=_status_fill(sl))
        r += 1
    t328_end = r - 1
    r += 2

    # ── Building Summary ──
    r = _subtitle(ws, r, "Building Summary")
    if project.building_summary:
        for line in project.building_summary.split("\n"):
            _cell(ws, r, 2, line, border=False)
            r += 1
    r += 2

    # ══════════════════════════════════════════════════════════════════
    # CHARTS
    # ══════════════════════════════════════════════════════════════════
    chart_col = 12  # Charts start at column L
    chart_row = 1

    # ── Chart 1: Stiffness X (line chart) ──
    if t326_start <= t326_end:
        chart = LineChart()
        chart.title = "Stiffness X axis (kN/m)"
        chart.y_axis.title = "Stiffness (kN/m)"
        chart.x_axis.title = "Storey"
        chart.width = 22
        chart.height = 14
        chart.style = 10
        cats = Reference(ws, min_col=2, min_row=t326_start, max_row=t326_end)
        vals = Reference(ws, min_col=3, min_row=t326_start - 1, max_row=t326_end)
        chart.add_data(vals, titles_from_data=True)
        chart.set_categories(cats)
        s = chart.series[0]
        s.graphicalProperties.line.width = 25000
        ws.add_chart(chart, f"{get_column_letter(chart_col)}{chart_row}")

    # ── Chart 2: Stiffness Y (line chart) ──
    if t327_start <= t327_end:
        chart = LineChart()
        chart.title = "Stiffness Y axis (kN/m)"
        chart.y_axis.title = "Stiffness (kN/m)"
        chart.x_axis.title = "Storey"
        chart.width = 22
        chart.height = 14
        chart.style = 10
        cats = Reference(ws, min_col=2, min_row=t327_start, max_row=t327_end)
        vals = Reference(ws, min_col=3, min_row=t327_start - 1, max_row=t327_end)
        chart.add_data(vals, titles_from_data=True)
        chart.set_categories(cats)
        s = chart.series[0]
        s.graphicalProperties.line.width = 25000
        ws.add_chart(chart, f"{get_column_letter(chart_col)}{chart_row + 17}")

    # ── Chart 3 & 4: Displacement Comparison ──
    # Build displacement data table for charts (hidden area)
    disp_start_row = chart_row + 36
    _cell(ws, disp_start_row, chart_col, "Story", font=BOLD_FONT)
    _cell(ws, disp_start_row, chart_col + 1, "Elastic Disp X", font=BOLD_FONT)
    _cell(ws, disp_start_row, chart_col + 2, "Design Disp X", font=BOLD_FONT)
    _cell(ws, disp_start_row, chart_col + 3, "Elastic Disp Y", font=BOLD_FONT)
    _cell(ws, disp_start_row, chart_col + 4, "Design Disp Y", font=BOLD_FONT)

    for i, s in enumerate(storeys):
        row = disp_start_row + 1 + i
        sd = s.source_data
        _cell(ws, row, chart_col, s.normalized_name)
        _cell(ws, row, chart_col + 1, abs(sd.ux_eqx or 0))
        _cell(ws, row, chart_col + 2, abs(sd.ux_eqx or 0))
        _cell(ws, row, chart_col + 3, abs(sd.uy_eqy or 0))
        _cell(ws, row, chart_col + 4, abs(sd.uy_eqy or 0))

    disp_data_end = disp_start_row + len(storeys)

    # Chart 3: Displacement X — horizontal bar
    chart3 = BarChart()
    chart3.type = "bar"
    chart3.title = "Elastic vs Design Displacement — X Direction"
    chart3.x_axis.title = "Displacement (m)"
    chart3.width = 22
    chart3.height = 14
    chart3.style = 10
    cats3 = Reference(ws, min_col=chart_col, min_row=disp_start_row + 1, max_row=disp_data_end)
    vals_elastic_x = Reference(ws, min_col=chart_col + 1, min_row=disp_start_row, max_row=disp_data_end)
    vals_design_x = Reference(ws, min_col=chart_col + 2, min_row=disp_start_row, max_row=disp_data_end)
    chart3.add_data(vals_elastic_x, titles_from_data=True)
    chart3.add_data(vals_design_x, titles_from_data=True)
    chart3.set_categories(cats3)
    chart3.series[0].graphicalProperties.solidFill = "C00000"
    chart3.series[1].graphicalProperties.solidFill = "4472C4"
    chart3.grouping = "clustered"
    ws.add_chart(chart3, f"{get_column_letter(chart_col)}{disp_data_end + 2}")

    # Chart 4: Displacement Y — horizontal bar
    chart4 = BarChart()
    chart4.type = "bar"
    chart4.title = "Elastic vs Design Displacement — Y Direction"
    chart4.x_axis.title = "Displacement (m)"
    chart4.width = 22
    chart4.height = 14
    chart4.style = 10
    cats4 = Reference(ws, min_col=chart_col, min_row=disp_start_row + 1, max_row=disp_data_end)
    vals_elastic_y = Reference(ws, min_col=chart_col + 3, min_row=disp_start_row, max_row=disp_data_end)
    vals_design_y = Reference(ws, min_col=chart_col + 4, min_row=disp_start_row, max_row=disp_data_end)
    chart4.add_data(vals_elastic_y, titles_from_data=True)
    chart4.add_data(vals_design_y, titles_from_data=True)
    chart4.set_categories(cats4)
    chart4.series[0].graphicalProperties.solidFill = "C00000"
    chart4.series[1].graphicalProperties.solidFill = "4472C4"
    chart4.grouping = "clustered"
    ws.add_chart(chart4, f"{get_column_letter(chart_col)}{disp_data_end + 19}")


# ══════════════════════════════════════════════════════════════════════
# 3.3 LATERAL FORCE PARTICIPATION
# ══════════════════════════════════════════════════════════════════════

def _create_3_3_sheet(wb, project, storeys, data):
    ws = wb.create_sheet("3.3 Lateral Force")
    r = 1
    r = _title(ws, r, "3.3 Building Classification")
    r += 1

    bc = data.get("building_classification", "N/A")
    _cell(ws, r, 2, "Building Classification:", font=BOLD_FONT, border=False)
    _cell(ws, r, 4, bc, font=BOLD_FONT)
    r += 2

    # X-Direction
    xd = data.get("x_direction", {})
    r = _subtitle(ws, r, "Along X-Direction (UL1)")
    r = _header_row(ws, r, ["#", "Story", "Lateral (kN)", "Column (kN)", "Wall (kN)",
                            "Column %", "Wall %"])
    for i, s in enumerate(xd.get("storeys", [])):
        _cell(ws, r, 1, i + 1)
        _cell(ws, r, 2, s.get("name", ""))
        _cell(ws, r, 3, _fmt(s.get("lateral"), 0))
        _cell(ws, r, 4, _fmt(s.get("column_force"), 2))
        _cell(ws, r, 5, _fmt(s.get("wall_force"), 2))
        _cell(ws, r, 6, _fmt(s.get("column_pct", 0) * 100, 1))
        _cell(ws, r, 7, _fmt(s.get("wall_pct", 0) * 100, 1))
        r += 1
    r += 1

    col_pct = xd.get("column_pct", 0)
    wall_pct = xd.get("wall_pct", 0)
    _cell(ws, r, 2, "Ground FL Column %:", font=BOLD_FONT, border=False)
    _cell(ws, r, 4, _fmt(col_pct * 100, 1) if col_pct else "-", border=False)
    _cell(ws, r, 5, "%", border=False)
    r += 1
    _cell(ws, r, 2, "Ground FL Wall %:", font=BOLD_FONT, border=False)
    _cell(ws, r, 4, _fmt(wall_pct * 100, 1) if wall_pct else "-", border=False)
    _cell(ws, r, 5, "%", border=False)
    r += 2

    # Y-Direction
    yd = data.get("y_direction", {})
    r = _subtitle(ws, r, "Along Y-Direction (UL2)")
    r = _header_row(ws, r, ["#", "Story", "Lateral (kN)", "Column (kN)", "Wall (kN)",
                            "Column %", "Wall %"])
    for i, s in enumerate(yd.get("storeys", [])):
        _cell(ws, r, 1, i + 1)
        _cell(ws, r, 2, s.get("name", ""))
        _cell(ws, r, 3, _fmt(s.get("lateral"), 0))
        _cell(ws, r, 4, _fmt(s.get("column_force"), 2))
        _cell(ws, r, 5, _fmt(s.get("wall_force"), 2))
        _cell(ws, r, 6, _fmt(s.get("column_pct", 0) * 100, 1))
        _cell(ws, r, 7, _fmt(s.get("wall_pct", 0) * 100, 1))
        r += 1

    r += 2
    _cell(ws, r, 2, f"The structure is categorized as: {bc}", font=BOLD_FONT, border=False)


# ══════════════════════════════════════════════════════════════════════
# 3.4 BEHAVIORAL FACTOR
# ══════════════════════════════════════════════════════════════════════

def _create_3_4_sheet(wb, project, storeys, data):
    ws = wb.create_sheet("3.4 Behavioral Factor")
    r = 1
    r = _title(ws, r, "3.4 Behavioral Factor (q)")
    r += 2
    r = _subtitle(ws, r, "q = q₀ × kw × (αu/α1)")
    r += 1

    r = _header_row(ws, r, ["#", "Parameter", "Value"])
    params = [
        ("Building Type", data.get("building_type", "")),
        ("q₀", data.get("qo", "")),
        ("kw", data.get("kw", "")),
        ("αu/α1", data.get("alpha_ratio", "")),
        ("q (X)", data.get("qx", "")),
        ("q (Y)", data.get("qy", "")),
        ("q (design)", data.get("q", "")),
        ("Plan Regularity", data.get("regularity_plan", "")),
        ("Elevation Regularity", data.get("regularity_elevation", "")),
    ]
    for i, (label, val) in enumerate(params):
        _cell(ws, r, 1, i + 1)
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

    r = _subtitle(ws, r, "Seismic Parameters")
    r = _header_row(ws, r, ["#", "Parameter", "Value"])
    params = [
        ("Peak Ground Acceleration (ag)", f"{data.get('ag', '')} g"),
        ("Ground Type", data.get("ground_type", "")),
        ("Spectrum Type", data.get("spectrum_type", "")),
        ("Soil Factor (S)", data.get("S", "")),
        ("TB", f"{data.get('TB', '')} s"),
        ("TC", f"{data.get('TC', '')} s"),
        ("TD", f"{data.get('TD', '')} s"),
        ("Damping (β)", data.get("beta", "")),
        ("Behavior Factor (q)", data.get("q", "")),
    ]
    for i, (label, val) in enumerate(params):
        _cell(ws, r, 1, i + 1)
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

    # Design spectrum
    r = _subtitle(ws, r, "Design Spectrum Sd(T)")
    eqs = [
        "0 ≤ T ≤ TB:  Sd(T) = ag × S × (2/3 + T/TB × (2.5/q − 2/3))",
        "TB ≤ T ≤ TC:  Sd(T) = ag × S × 2.5/q",
        "TC ≤ T ≤ TD:  Sd(T) = ag × S × 2.5/q × (TC/T)",
        "T > TD:  Sd(T) = ag × S × 2.5/q × (TC × TD / T²)",
    ]
    for eq in eqs:
        _cell(ws, r, 2, eq, font=Font(name="Consolas", size=10, color="1F4E79"), border=False)
        r += 1
    r += 1

    # Results
    r = _subtitle(ws, r, "Base Shear Results")
    r = _header_row(ws, r, ["#", "Direction", "Sd(T) (% ag)", "Fb (kN)", "Lower Bound (kN)", "Weight (kN)", "Modal %"])
    _cell(ws, r, 1, 1)
    _cell(ws, r, 2, "X")
    _cell(ws, r, 3, _fmt(data.get("Sd_x_pct"), 2))
    _cell(ws, r, 4, _fmt(data.get("Fb_x"), 2))
    _cell(ws, r, 5, _fmt(data.get("lower_bound_x"), 2))
    _cell(ws, r, 6, _fmt(data.get("total_weight_kN"), 0))
    _cell(ws, r, 7, _fmt(data.get("modal_ratio_x", 0) * 100, 1))
    r += 1
    _cell(ws, r, 1, 2)
    _cell(ws, r, 2, "Y")
    _cell(ws, r, 3, _fmt(data.get("Sd_y_pct"), 2))
    _cell(ws, r, 4, _fmt(data.get("Fb_y"), 2))
    _cell(ws, r, 5, _fmt(data.get("lower_bound_y"), 2))
    _cell(ws, r, 6, _fmt(data.get("total_weight_kN"), 0))
    _cell(ws, r, 7, _fmt(data.get("modal_ratio_y", 0) * 100, 1))


# ══════════════════════════════════════════════════════════════════════
# 4.2 MODAL LOAD PARTICIPATION
# ══════════════════════════════════════════════════════════════════════

def _create_4_2_sheet(wb, project, storeys, data):
    ws = wb.create_sheet("4.2 Modal Participation")
    r = 1
    r = _title(ws, r, "4.2 Modal Load Participation")
    r += 1

    _cell(ws, r, 2, "T1x:", font=BOLD_FONT, border=False)
    _cell(ws, r, 3, _fmt(data.get("T1x"), 6))
    _cell(ws, r, 4, "s", border=False)
    _cell(ws, r, 5, "T1y:", font=BOLD_FONT, border=False)
    _cell(ws, r, 6, _fmt(data.get("T1y"), 6))
    _cell(ws, r, 7, "s", border=False)
    r += 1
    _cell(ws, r, 2, "Total modes analyzed:", font=BOLD_FONT, border=False)
    _cell(ws, r, 3, data.get("total_modes", 50))
    r += 2

    modes = data.get("modes", [])
    if modes:
        r = _header_row(ws, r, ["#", "Mode", "Period (s)", "UX (%)", "UY (%)",
                                "ΣUX (%)", "ΣUY (%)", "RX (%)", "RY (%)", "RZ (%)"])
        for i, m in enumerate(modes[:50]):
            _cell(ws, r, 1, i + 1)
            _cell(ws, r, 2, m.get("mode", ""))
            _cell(ws, r, 3, _fmt(m.get("period"), 6))
            _cell(ws, r, 4, _fmt(m.get("ux"), 4))
            _cell(ws, r, 5, _fmt(m.get("uy"), 4))
            _cell(ws, r, 6, _fmt(m.get("sum_ux"), 2))
            _cell(ws, r, 7, _fmt(m.get("sum_uy"), 2))
            _cell(ws, r, 8, _fmt(m.get("rx"), 4))
            _cell(ws, r, 9, _fmt(m.get("ry"), 4))
            _cell(ws, r, 10, _fmt(m.get("rz"), 4))
            r += 1

        # Summary row
        r += 1
        _cell(ws, r, 2, "Final Cumulative UX:", font=BOLD_FONT, border=False)
        _cell(ws, r, 3, _fmt(data.get("mass_x"), 2))
        _cell(ws, r, 4, "%", border=False)
        r += 1
        _cell(ws, r, 2, "Final Cumulative UY:", font=BOLD_FONT, border=False)
        _cell(ws, r, 3, _fmt(data.get("mass_y"), 2))
        _cell(ws, r, 4, "%", border=False)


# ══════════════════════════════════════════════════════════════════════
# 4.3 GEOMETRIC IMPERFECTION
# ══════════════════════════════════════════════════════════════════════

def _create_4_3_sheet(wb, project, storeys, data):
    ws = wb.create_sheet("4.3 Geometric Imperfection")
    r = 1
    r = _title(ws, r, "4.3 Geometric Imperfections")
    r += 2
    r = _subtitle(ws, r, "θi = θ₀ × αh × αm")
    r += 1

    r = _header_row(ws, r, ["#", "Parameter", "Value"])
    params = [
        ("θ₀", data.get("theta0", 0.005)),
        ("αh", data.get("alpha_h", 1.0)),
        ("αm", data.get("alpha_m", 0.723)),
        ("θi", data.get("theta_i", "")),
    ]
    for i, (label, val) in enumerate(params):
        _cell(ws, r, 1, i + 1)
        _cell(ws, r, 2, label)
        _cell(ws, r, 3, _fmt(val, 6) if isinstance(val, (int, float)) else str(val))
        r += 1
    r += 1

    r = _subtitle(ws, r, "Imperfection Forces")
    r = _header_row(ws, r, ["#", "Story", "Ptot (kN)", "θ₀", "L(h) (m)",
                            "αh", "αm", "θi", "Hi (kN)"])
    for i, s in enumerate(data.get("storeys", [])):
        _cell(ws, r, 1, i + 1)
        _cell(ws, r, 2, s.get("name", ""))
        _cell(ws, r, 3, _fmt(s.get("ptot"), 2))
        _cell(ws, r, 4, s.get("theta0", 0.005))
        _cell(ws, r, 5, _fmt(s.get("l_h") or s.get("height"), 2))
        _cell(ws, r, 6, s.get("alpha_h", 1.0))
        _cell(ws, r, 7, _fmt(s.get("alpha_m"), 6))
        _cell(ws, r, 8, _fmt(s.get("theta_i"), 6))
        _cell(ws, r, 9, _fmt(s.get("hi"), 2), fill=BLUE_FILL)
        r += 1


# ══════════════════════════════════════════════════════════════════════
# 4.4 STABILITY ANALYSIS (P-DELTA)
# ══════════════════════════════════════════════════════════════════════

def _create_4_4_sheet(wb, project, storeys, data):
    ws = wb.create_sheet("4.4 Stability Analysis")
    r = 1
    r = _title(ws, r, "4.4 Stability Analysis (P-Delta)")
    r += 2

    r = _subtitle(ws, r, "Maximum Values")
    _cell(ws, r, 2, "Max θx:", font=BOLD_FONT, border=False)
    _cell(ws, r, 3, _fmt(data.get("max_theta_x"), 8))
    _cell(ws, r, 5, "Max θy:", font=BOLD_FONT, border=False)
    _cell(ws, r, 6, _fmt(data.get("max_theta_y"), 8))
    r += 1
    _cell(ws, r, 2, "X Classification:", font=BOLD_FONT, border=False)
    _cell(ws, r, 3, data.get("max_classification_x", ""),
          fill=_status_fill(data.get("max_classification_x")))
    _cell(ws, r, 5, "Y Classification:", font=BOLD_FONT, border=False)
    _cell(ws, r, 6, data.get("max_classification_y", ""),
          fill=_status_fill(data.get("max_classification_y")))
    r += 2

    r = _subtitle(ws, r, "θ = ΣPu × Δu / (Hu × hs)")
    r += 1

    r = _header_row(ws, r, ["#", "Storey", "Load Case", "Ptot (kN)", "Height (m)",
                            "Hu (kN)", "Δu (m)", "θ", "Classification"])
    for i, s in enumerate(data.get("storeys", [])):
        _cell(ws, r, 1, i + 1)
        _cell(ws, r, 2, s.get("name", ""))
        _cell(ws, r, 3, s.get("load_case", ""))
        _cell(ws, r, 4, _fmt(s.get("ptot"), 2))
        _cell(ws, r, 5, _fmt(s.get("height"), 2))
        _cell(ws, r, 6, _fmt(s.get("hu"), 2))
        _cell(ws, r, 7, _fmt(s.get("delta_u"), 6))
        _cell(ws, r, 8, _fmt(s.get("theta"), 6))
        _cell(ws, r, 9, s.get("classification", ""),
              fill=_status_fill(s.get("classification")))
        r += 1


# ══════════════════════════════════════════════════════════════════════
# 4.5 STOREY DRIFT CONTROL
# ══════════════════════════════════════════════════════════════════════

def _create_4_5_sheet(wb, project, storeys, data):
    ws = wb.create_sheet("4.5 Storey Drift Control")
    r = 1
    r = _title(ws, r, "4.5 Damage Limitation")
    r += 2

    _cell(ws, r, 2, "ν (reduction factor):", font=BOLD_FONT, border=False)
    _cell(ws, r, 4, data.get("nu", 0.5))
    _cell(ws, r, 5, "Limit:", font=BOLD_FONT, border=False)
    _cell(ws, r, 6, data.get("limit", 0.005))
    r += 1
    _cell(ws, r, 2, "Max ν·dr/h (X):", font=BOLD_FONT, border=False)
    _cell(ws, r, 3, _fmt(data.get("max_ratio_x"), 6))
    _cell(ws, r, 5, "Max ν·dr/h (Y):", font=BOLD_FONT, border=False)
    _cell(ws, r, 6, _fmt(data.get("max_ratio_y"), 6))
    r += 2

    r = _header_row(ws, r, ["#", "Story", "Load Case", "dr X", "dr Y",
                            "ν·dr/h (X)", "ν·dr/h (Y)", "Limit", "X Status", "Y Status"])
    for i, s in enumerate(data.get("storeys", [])):
        _cell(ws, r, 1, i + 1)
        _cell(ws, r, 2, s.get("name", ""))
        _cell(ws, r, 3, s.get("load_case", ""))
        _cell(ws, r, 4, _fmt(s.get("dr_x"), 6))
        _cell(ws, r, 5, _fmt(s.get("dr_y"), 6))
        _cell(ws, r, 6, _fmt(s.get("nu_dr_h_x"), 6))
        _cell(ws, r, 7, _fmt(s.get("nu_dr_h_y"), 6))
        _cell(ws, r, 8, s.get("limit", 0.005))
        _cell(ws, r, 9, s.get("status_x", ""),
              fill=_status_fill(s.get("status_x")))
        _cell(ws, r, 10, s.get("status_y", ""),
              fill=_status_fill(s.get("status_y")))
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
    _cell(ws, r, 3, f"Building Center Distance: {data.get('ground_xcm', '')} m",
          font=SUBTITLE_FONT, border=False)
    r += 1
    r = _header_row(ws, r, ["#", "Story", "Elevation (m)", "Story Height (m)",
                            "Vi × hi (kN·m)", "ΣMOT (kN·m)"])
    total_ot = 0
    for i, s in enumerate(xd.get("storeys", [])):
        _cell(ws, r, 1, i + 1)
        _cell(ws, r, 2, s.get("name", ""))
        _cell(ws, r, 3, _fmt(s.get("elevation"), 2))
        _cell(ws, r, 4, _fmt(s.get("height"), 2))
        _cell(ws, r, 5, _fmt(s.get("shear"), 2))
        total_ot += s.get("ot_moment", 0)
        _cell(ws, r, 6, _fmt(total_ot, 2), fill=YELLOW_FILL)
        r += 1

    r += 1
    _cell(ws, r, 4, "Total OT Moment:", font=BOLD_FONT, border=False)
    _cell(ws, r, 6, _fmt(xd.get("total_ot_moment"), 2))
    r += 1
    _cell(ws, r, 4, "Resisting Moment:", font=BOLD_FONT, border=False)
    _cell(ws, r, 6, _fmt(xd.get("resisting_moment"), 2))
    r += 1
    _cell(ws, r, 4, "Safety Factor:", font=BOLD_FONT, border=False)
    _cell(ws, r, 5, _fmt(xd.get("safety_factor"), 4))
    sf_x = xd.get("safety_factor", 0)
    _cell(ws, r, 6, "≥ 1.5", border=False)
    _cell(ws, r, 7, "PASS" if sf_x >= 1.5 else "FAIL",
          fill=GREEN_FILL if sf_x >= 1.5 else RED_FILL)
    r += 2

    # Y-Direction
    yd = data.get("y_direction", {})
    r = _subtitle(ws, r, "Along Y-Direction")
    _cell(ws, r, 3, f"Building Center Distance: {data.get('ground_ycm', '')} m",
          font=SUBTITLE_FONT, border=False)
    r += 1
    r = _header_row(ws, r, ["#", "Story", "Elevation (m)", "Story Height (m)",
                            "Vi × hi (kN·m)", "ΣMOT (kN·m)"])
    total_ot = 0
    for i, s in enumerate(yd.get("storeys", [])):
        _cell(ws, r, 1, i + 1)
        _cell(ws, r, 2, s.get("name", ""))
        _cell(ws, r, 3, _fmt(s.get("elevation"), 2))
        _cell(ws, r, 4, _fmt(s.get("height"), 2))
        _cell(ws, r, 5, _fmt(s.get("shear"), 2))
        total_ot += s.get("ot_moment", 0)
        _cell(ws, r, 6, _fmt(total_ot, 2), fill=YELLOW_FILL)
        r += 1

    r += 1
    _cell(ws, r, 4, "Total OT Moment:", font=BOLD_FONT, border=False)
    _cell(ws, r, 6, _fmt(yd.get("total_ot_moment"), 2))
    r += 1
    _cell(ws, r, 4, "Resisting Moment:", font=BOLD_FONT, border=False)
    _cell(ws, r, 6, _fmt(yd.get("resisting_moment"), 2))
    r += 1
    _cell(ws, r, 4, "Safety Factor:", font=BOLD_FONT, border=False)
    _cell(ws, r, 5, _fmt(yd.get("safety_factor"), 4))
    sf_y = yd.get("safety_factor", 0)
    _cell(ws, r, 6, "≥ 1.5", border=False)
    _cell(ws, r, 7, "PASS" if sf_y >= 1.5 else "FAIL",
          fill=GREEN_FILL if sf_y >= 1.5 else RED_FILL)


# ══════════════════════════════════════════════════════════════════════
# CALCULATION AUDIT SHEET
# ══════════════════════════════════════════════════════════════════════

def _create_audit_sheet(wb, project, sections):
    ws = wb.create_sheet("Calculation Audit")
    r = 1
    r = _title(ws, r, "Calculation Audit — Cross-Check Against Original Workbook")
    r += 1
    _cell(ws, r, 2, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", border=False)
    r += 1
    _cell(ws, r, 2, "Original: Stability_Behaviour_Calculation_for BAHRU SARBET MODEL 1-3", border=False)
    r += 2

    r = _header_row(ws, r, ["#", "Section", "Parameter", "Our Value", "Excel Value",
                            "Diff %", "Status", "Notes"])

    excel_refs = {
        "3.3 Classification": ("Un-Coupled Wall System", None),
        "3.4 q": (2.76, None),
        "4.1 Fb_x (kN)": (2032.12, None),
        "4.1 Fb_y (kN)": (2032.12, None),
        "4.2 T1x (s)": (2.568473, None),
        "4.2 T1y (s)": (2.807803, None),
        "4.3 θi": (0.003615, None),
        "4.4 Max θx": (0.204728, None),
        "4.4 Max θy": (0.257708, None),
        "4.5 Max ratio_x": (0.003053, None),
        "4.5 Max ratio_y": (0.002592, None),
        "4.6 SF_X": (12.579, None),
        "4.6 SF_Y": (11.525, None),
    }

    audit_data = []
    if sections:
        # 3.3
        s33 = sections.get("3.3", {})
        audit_data.append(("3.3", "Classification", s33.get("building_classification", "-"),
                          "Un-Coupled Wall System"))
        # 3.4
        s34 = sections.get("3.4", {})
        audit_data.append(("3.4", "q", s34.get("q", "-"), 2.76))
        # 4.1
        s41 = sections.get("4.1", {})
        audit_data.append(("4.1", "Fb_x (kN)", s41.get("Fb_x", "-"), 2032.12))
        audit_data.append(("4.1", "Fb_y (kN)", s41.get("Fb_y", "-"), 2032.12))
        # 4.2
        s42 = sections.get("4.2", {})
        audit_data.append(("4.2", "T1x (s)", s42.get("T1x", "-"), 2.568473))
        audit_data.append(("4.2", "T1y (s)", s42.get("T1y", "-"), 2.807803))
        # 4.3
        s43 = sections.get("4.3", {})
        audit_data.append(("4.3", "θi", s43.get("theta_i", "-"), 0.003615))
        # 4.4
        s44 = sections.get("4.4", {})
        audit_data.append(("4.4", "Max θx", s44.get("max_theta_x", "-"), 0.204728))
        audit_data.append(("4.4", "Max θy", s44.get("max_theta_y", "-"), 0.257708))
        # 4.5
        s45 = sections.get("4.5", {})
        audit_data.append(("4.5", "Max ratio_x", s45.get("max_ratio_x", "-"), 0.003053))
        audit_data.append(("4.5", "Max ratio_y", s45.get("max_ratio_y", "-"), 0.002592))
        # 4.6
        s46 = sections.get("4.6", {})
        xd = s46.get("x_direction", {})
        yd = s46.get("y_direction", {})
        audit_data.append(("4.6", "SF_X", xd.get("safety_factor", "-"), 12.579))
        audit_data.append(("4.6", "SF_Y", yd.get("safety_factor", "-"), 11.525))

    for i, (sec, param, our_val, excel_val) in enumerate(audit_data):
        _cell(ws, r, 1, i + 1)
        _cell(ws, r, 2, sec)
        _cell(ws, r, 3, param)

        if isinstance(our_val, str):
            _cell(ws, r, 4, our_val)
            _cell(ws, r, 5, str(excel_val) if excel_val else "-")
            match = our_val.lower() == str(excel_val).lower() if excel_val else False
            _cell(ws, r, 6, "-")
            _cell(ws, r, 7, "MATCH" if match else "CHECK", fill=GREEN_FILL if match else YELLOW_FILL)
        elif our_val is not None and excel_val is not None and isinstance(our_val, (int, float)) and isinstance(excel_val, (int, float)):
            _cell(ws, r, 4, _fmt(our_val, 6))
            _cell(ws, r, 5, _fmt(excel_val, 6))
            diff_pct = abs(our_val - excel_val) / abs(excel_val) * 100 if excel_val != 0 else 0
            _cell(ws, r, 6, _fmt(diff_pct, 4))
            status = "OK" if diff_pct < 1.0 else "CHECK"
            _cell(ws, r, 7, status, fill=GREEN_FILL if status == "OK" else YELLOW_FILL)
        else:
            _cell(ws, r, 4, str(our_val) if our_val else "-")
            _cell(ws, r, 5, str(excel_val) if excel_val else "-")
            _cell(ws, r, 6, "-")
            _cell(ws, r, 7, "CHECK", fill=YELLOW_FILL)

        _cell(ws, r, 8, "")
        r += 1
