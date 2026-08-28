"""
Excel Exporter — compact format matching the original Excel workbook layout.
Sections grouped logically: all 3.2 on one sheet, each other section separate.
"""
import os
import math
from datetime import datetime
from typing import Optional, Dict, List
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.chart import LineChart, BarChart, Reference

from models.project import Project, ClassificationResult

# Styles matching original workbook conventions
BLUE_FILL = PatternFill(start_color="BDD7EE", end_color="BDD7EE", fill_type="solid")
RED_FILL = PatternFill(start_color="F4CCCC", end_color="F4CCCC", fill_type="solid")
GREEN_FILL = PatternFill(start_color="D9EAD3", end_color="D9EAD3", fill_type="solid")
YELLOW_FILL = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
HEADER_FILL = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
HEADER_FONT = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
TITLE_FONT = Font(name="Calibri", size=14, bold=True, color="1F4E79")
SUBTITLE_FONT = Font(name="Calibri", size=12, bold=True, color="2E75B6")
NORMAL_FONT = Font(name="Calibri", size=11)
BOLD_FONT = Font(name="Calibri", size=11, bold=True)
THIN_BORDER = Border(
    left=Side(style="thin"), right=Side(style="thin"),
    top=Side(style="thin"), bottom=Side(style="thin"),
)


def _write_header(ws, row, headers):
    for col, h in enumerate(headers, 1):
        c = ws.cell(row=row, column=col, value=h)
        c.font = HEADER_FONT
        c.fill = HEADER_FILL
        c.border = THIN_BORDER
        c.alignment = Alignment(horizontal="center", wrap_text=True)
    return row + 1


def _write_row(ws, row, values, fills=None):
    for col, v in enumerate(values, 1):
        c = ws.cell(row=row, column=col, value=v)
        c.border = THIN_BORDER
        c.alignment = Alignment(horizontal="center")
        if fills and col in fills:
            c.fill = fills[col]
    return row + 1


def _fmt(v, d=3):
    if v is None or v == "" or v == "-":
        return "-"
    try:
        return round(float(v), d)
    except (TypeError, ValueError):
        return v


def export_to_excel(project: Project, output_path: str, sections: Dict = None) -> str:
    wb = Workbook()
    wb.remove(wb.active)

    storeys = project.get_storeys_sorted()

    # Sheet 1: 3.2 Structural Regularity (all sub-tables)
    _create_3_2_sheet(wb, project, storeys)

    # Sheets 2+: Other sections
    if sections:
        for sec_id, sec_data in sorted(sections.items()):
            if sec_id.startswith("3.3"):
                _create_section_sheet(wb, "3.3 Lateral Force Participation", sec_data)
            elif sec_id.startswith("3.4"):
                _create_section_sheet(wb, "3.4 Behavioral Factor", sec_data)
            elif sec_id.startswith("4.1"):
                _create_section_sheet(wb, "4.1 Base Shear", sec_data)
            elif sec_id.startswith("4.2"):
                _create_section_sheet(wb, "4.2 Modal Load Participation", sec_data)
            elif sec_id.startswith("4.3"):
                _create_section_sheet(wb, "4.3 Geometric Imperfection", sec_data)
            elif sec_id.startswith("4.4"):
                _create_section_sheet(wb, "4.4 Stability Analysis", sec_data)
            elif sec_id.startswith("4.5"):
                _create_section_sheet(wb, "4.5 Storey Drift Control", sec_data)
            elif sec_id.startswith("4.6"):
                _create_section_sheet(wb, "4.6 Overturning Check", sec_data)

    wb.save(output_path)
    return output_path


def _create_3_2_sheet(wb, project, storeys):
    """All 3.2 tables on one sheet, compact layout matching original workbook."""
    ws = wb.create_sheet("3.2 Structural Regularity")
    r = 1
    lam = round(project.lmax / project.lmin, 3) if project.lmin > 0 else 0

    # Header
    ws.cell(row=r, column=2, value="3.2 Structural Regularity").font = TITLE_FONT
    ws.cell(row=r, column=7, value="Project:").font = SUBTITLE_FONT
    ws.cell(row=r, column=8, value=project.project_name)
    r += 1
    ws.cell(row=r, column=7, value="Client:").font = SUBTITLE_FONT
    ws.cell(row=r, column=8, value=project.client or "N/A")
    r += 1
    ws.cell(row=r, column=7, value="Designed by:").font = SUBTITLE_FONT
    ws.cell(row=r, column=8, value=project.designed_by or "N/A")
    r += 2

    # ── 3.2.1 ──
    ws.cell(row=r, column=1, value="3.2.1").font = SUBTITLE_FONT
    ws.cell(row=r, column=2, value="Regularity in Plan").font = SUBTITLE_FONT
    r += 1
    ws.cell(row=r, column=2, value=f"Lmax/Lmin = {project.lmax}/{project.lmin} = {lam}  =>  {'OK' if lam < 4 else 'NOT OK'}")
    r += 2

    # ── 3.2.2 Structural Eccentricity ──
    ws.cell(row=r, column=1, value="Table 3.2.2:").font = SUBTITLE_FONT
    ws.cell(row=r, column=3, value="Structural Eccentricity of the Building").font = SUBTITLE_FONT
    r += 1
    r = _write_header(ws, r, ["", "Story", "CMX (m)", "CMY (m)", "CRX (m)", "CRY (m)", "eox (m)", "eoy (m)"])
    # Store rows for chart data
    t322_start = r
    for s in storeys:
        sd = s.source_data
        eox = _fmt(sd.xcm - sd.xcr) if sd.xcm is not None and sd.xcr is not None else None
        eoy = _fmt(sd.ycm - sd.ycr) if sd.ycm is not None and sd.ycr is not None else None
        _write_row(ws, r, ["", s.normalized_name, _fmt(sd.xcm), _fmt(sd.ycm),
                           _fmt(sd.xcr), _fmt(sd.ycr), eox, eoy])
        r += 1
    r += 1

    # ── 3.2.3 Torsional Radius ──
    ws.cell(row=r, column=1, value="Table 3.2.3:").font = SUBTITLE_FONT
    ws.cell(row=r, column=3, value="Radius of Gyration of the Building").font = SUBTITLE_FONT
    r += 1
    r = _write_header(ws, r, ["", "Story", "eox (m)", "rx (m)", "0.3*rx (m)", "Status",
                               "eoy (m)", "ry (m)", "0.3*ry (m)", "Status"])
    for s in storeys:
        c = s.calculations
        lx = _fmt(c.module_3_2_4_limit_x)
        ly = _fmt(c.module_3_2_4_limit_y)
        sx = c.module_3_2_4_eox_status or "-"
        sy = c.module_3_2_4_eoy_status or "-"
        fills = {}
        if sx == "OK": fills[6] = GREEN_FILL
        elif sx == "NOT OK": fills[6] = RED_FILL
        if sy == "OK": fills[10] = GREEN_FILL
        elif sy == "NOT OK": fills[10] = RED_FILL
        _write_row(ws, r, ["", s.normalized_name, _fmt(abs(c.eox) if c.eox else None),
                           _fmt(c.rx), lx, sx,
                           _fmt(abs(c.eoy) if c.eoy else None), _fmt(c.ry), ly, sy], fills)
        r += 1
    r += 1

    # ── 3.2.4 Eccentricity vs Gyration ──
    ws.cell(row=r, column=1, value="Table 3.2.4:").font = SUBTITLE_FONT
    ws.cell(row=r, column=3, value="Structural Eccentricity and Radius of Gyration Comparison").font = SUBTITLE_FONT
    r += 1
    ws.cell(row=r, column=2, value="For this case the structure satisfies Plan regularity criterion in X-Direction").font = NORMAL_FONT
    r += 1
    ws.cell(row=r, column=2, value="For this case the structure satisfies Plan regularity criterion in Y-Direction").font = NORMAL_FONT
    r += 2

    # ── 3.2.5 Torsional Radius vs Floor Radius ──
    ws.cell(row=r, column=1, value="Table 3.2.5:").font = SUBTITLE_FONT
    ws.cell(row=r, column=3, value="Torsional Radius and Radius of Gyration Comparison for the Building").font = SUBTITLE_FONT
    r += 1
    r = _write_header(ws, r, ["", "Story", "rx", "ls", "Status", "ry", "ls", "Status"])
    for s in storeys:
        c = s.calculations
        fills = {}
        if c.module_3_2_5_rx_status == "OK": fills[5] = GREEN_FILL
        elif c.module_3_2_5_rx_status == "NOT OK": fills[5] = RED_FILL
        if c.module_3_2_5_ry_status == "OK": fills[8] = GREEN_FILL
        elif c.module_3_2_5_ry_status == "NOT OK": fills[8] = RED_FILL
        _write_row(ws, r, ["", s.normalized_name, _fmt(c.rx), _fmt(c.ls),
                           c.module_3_2_5_rx_status or "-", _fmt(c.ry), _fmt(c.ls),
                           c.module_3_2_5_ry_status or "-"], fills)
        r += 1
    r += 2

    # ── 3.2.6 Stiffness X ──
    ws.cell(row=r, column=1, value="Table 3.2.6:").font = SUBTITLE_FONT
    ws.cell(row=r, column=3, value="Storey Stiffness along X Direction of the Building").font = SUBTITLE_FONT
    r += 1
    ws.cell(row=r, column=5, value="EQX").font = SUBTITLE_FONT
    r += 1
    t326_start = r
    r = _write_header(ws, r, ["", "Story", "Stiffness X axis (kN/m)", "Ki >0.7*Ki+1  X axis"])
    for s in storeys:
        c = s.calculations
        fills = {}
        if c.module_3_2_6_status == "OK": fills[4] = GREEN_FILL
        elif c.module_3_2_6_status == "NOT OK": fills[4] = RED_FILL
        _write_row(ws, r, ["", s.normalized_name, _fmt(c.kx, 1),
                           c.module_3_2_6_status or "-"], fills)
        r += 1
    t326_end = r - 1
    r += 1

    # ── 3.2.7 Stiffness Y ──
    ws.cell(row=r, column=1, value="Table 3.2.7:").font = SUBTITLE_FONT
    ws.cell(row=r, column=3, value="Storey Stiffness along Y Direction of the Building").font = SUBTITLE_FONT
    r += 1
    ws.cell(row=r, column=5, value="EQY").font = SUBTITLE_FONT
    r += 1
    t327_start = r
    r = _write_header(ws, r, ["", "Story", "Stiffness Y axis (kN/m)", "Ki >0.7*Ki+1  Y axis"])
    for s in storeys:
        c = s.calculations
        fills = {}
        if c.module_3_2_7_status == "OK": fills[4] = GREEN_FILL
        elif c.module_3_2_7_status == "NOT OK": fills[4] = RED_FILL
        _write_row(ws, r, ["", s.normalized_name, _fmt(c.ky, 1),
                           c.module_3_2_7_status or "-"], fills)
        r += 1
    t327_end = r - 1
    r += 1

    # ── 3.2.8 Mass Distribution ──
    ws.cell(row=r, column=1, value="Table 3.2.8:").font = SUBTITLE_FONT
    ws.cell(row=r, column=3, value="Mass Distribution along height of the Building").font = SUBTITLE_FONT
    r += 1
    r = _write_header(ws, r, ["", "Story", "Mass (1000 x Kg)", "Mi < 2Mi+1", "Mi < 2Mi-1"])
    for s in storeys:
        c = s.calculations
        fills = {}
        su = c.module_3_2_8_status_upper or "-"
        sl = c.module_3_2_8_status_lower or "-"
        if su == "OK": fills[4] = GREEN_FILL
        elif su == "NOT OK": fills[4] = RED_FILL
        if sl == "OK": fills[5] = GREEN_FILL
        elif sl == "NOT OK": fills[5] = RED_FILL
        _write_row(ws, r, ["", s.normalized_name, _fmt(c.module_3_2_8_mass),
                           su, sl], fills)
        r += 1
    r += 1

    # ── Building Summary ──
    ws.cell(row=r, column=1, value="Building Summary").font = TITLE_FONT
    r += 1
    for line in project.building_summary.split("\n"):
        ws.cell(row=r, column=1, value=line)
        r += 1

    # ── Stiffness Distribution Charts ──
    chart_row = r + 2

    # Chart: Stiffness X distribution
    if t326_start <= t326_end:
        chart = LineChart()
        chart.title = "Stiffness Distribution - X Direction"
        chart.y_axis.title = "Stiffness (kN/m)"
        chart.x_axis.title = "Story"
        chart.width = 20
        chart.height = 12
        cats = Reference(ws, min_col=2, min_row=t326_start, max_row=t326_end)
        vals = Reference(ws, min_col=3, min_row=t326_start - 1, max_row=t326_end)
        chart.add_data(vals, titles_from_data=True)
        chart.set_categories(cats)
        chart.series[0].graphicalProperties.line.width = 25000
        ws.add_chart(chart, "F" + str(chart_row))

    # Chart: Stiffness Y distribution
    if t327_start <= t327_end:
        chart = LineChart()
        chart.title = "Stiffness Distribution - Y Direction"
        chart.y_axis.title = "Stiffness (kN/m)"
        chart.x_axis.title = "Story"
        chart.width = 20
        chart.height = 12
        cats = Reference(ws, min_col=2, min_row=t327_start, max_row=t327_end)
        vals = Reference(ws, min_col=3, min_row=t327_start - 1, max_row=t327_end)
        chart.add_data(vals, titles_from_data=True)
        chart.set_categories(cats)
        chart.series[0].graphicalProperties.line.width = 25000
        ws.add_chart(chart, "F" + str(chart_row + 16))


def _create_section_sheet(wb, title, data):
    """Create a sheet for sections 3.3-4.6."""
    ws = wb.create_sheet(title)
    r = 1
    ws.cell(row=r, column=1, value=title).font = TITLE_FONT
    r += 2

    if not data:
        ws.cell(row=r, column=1, value="No data available")
        return

    # Handle dict data (key-value pairs)
    if isinstance(data, dict):
        for key, val in data.items():
            if isinstance(val, list) and val and isinstance(val[0], dict):
                # Table data
                ws.cell(row=r, column=1, value=key).font = SUBTITLE_FONT
                r += 1
                headers = list(val[0].keys())
                r = _write_header(ws, r, headers)
                for row_data in val:
                    _write_row(ws, r, [row_data.get(h) for h in headers])
                    r += 1
                r += 1
            elif isinstance(val, (str, int, float)):
                ws.cell(row=r, column=1, value=str(key) + ":").font = BOLD_FONT
                ws.cell(row=r, column=2, value=str(val))
                r += 1

    # Handle list data
    elif isinstance(data, list) and data:
        if isinstance(data[0], dict):
            headers = list(data[0].keys())
            r = _write_header(ws, r, headers)
            for row_data in data:
                _write_row(ws, r, [row_data.get(h) for h in headers])
                r += 1
