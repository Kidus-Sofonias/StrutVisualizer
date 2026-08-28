"""
Excel Exporter — generates Excel workbook with all calculation results.
Includes sections 3.2 (storey-level) and 3.3–4.6 (building-level / extended).
"""
import os
from datetime import datetime
from typing import Optional, Dict
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

from models.project import Project, ClassificationResult


# Style constants
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


def _write_header_row(ws, row, headers, fill=HEADER_FILL):
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=row, column=col, value=h)
        cell.font = HEADER_FONT
        cell.fill = fill
        cell.border = THIN_BORDER
        cell.alignment = Alignment(horizontal="center", wrap_text=True)
    return row + 1


def _write_data_row(ws, row, values, status_col=None, status_val=None):
    for col, v in enumerate(values, 1):
        cell = ws.cell(row=row, column=col, value=v)
        cell.border = THIN_BORDER
        cell.alignment = Alignment(horizontal="center")
        if col == status_col:
            if status_val == "OK" or status_val == "PASS" or status_val == "NO SWAY":
                cell.fill = GREEN_FILL
            elif status_val in ("NOT OK", "FAIL", "SWAY"):
                cell.fill = RED_FILL
            else:
                cell.fill = YELLOW_FILL
    return row + 1


def export_to_excel(project: Project, output_path: str, sections: Dict = None) -> str:
    """Export all calculation results to an Excel workbook."""
    wb = Workbook()
    wb.remove(wb.active)

    # All 3.2 tables on one worksheet, then each 3.3–4.6 on separate sheets
    _create_project_info_sheet(wb, project)
    _create_3_2_combined_sheet(wb, project)

    # Section 3.3–4.6 sheets
    if sections:
        if "3.3" in sections:
            _create_3_3_sheet(wb, sections["3.3"])
        if "3.4" in sections:
            _create_3_4_sheet(wb, sections["3.4"])
        if "4.1" in sections:
            _create_4_1_sheet(wb, sections["4.1"])
        if "4.2" in sections:
            _create_4_2_sheet(wb, sections["4.2"])
        if "4.3" in sections:
            _create_4_3_sheet(wb, sections["4.3"])
        if "4.4" in sections:
            _create_4_4_sheet(wb, sections["4.4"])
        if "4.5" in sections:
            _create_4_5_sheet(wb, sections["4.5"])
        if "4.6" in sections:
            _create_4_6_sheet(wb, sections["4.6"])

    _create_summary_sheet(wb, project, sections)
    wb.save(output_path)
    return output_path


def _create_project_info_sheet(wb, project):
    ws = wb.create_sheet("Project Info")
    ws["A1"] = "Structural Engineering Analysis"
    ws["A1"].font = TITLE_FONT
    ws["A3"] = "Project:"
    ws["B3"] = project.project_name
    ws["A4"] = "Client:"
    ws["B4"] = project.client
    ws["A5"] = "Designed by:"
    ws["B5"] = project.designed_by
    ws["A6"] = "Generated:"
    ws["B6"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ws["A8"] = "Building Summary"
    ws["A8"].font = TITLE_FONT
    ws["A9"] = project.building_summary


# ─── Section 3.2 sheets ─────────────────────────────────────────────────

def _create_3_2_combined_sheet(wb, project):
    """All 3.2 tables (3.2.1–3.2.8) on one worksheet."""
    ws = wb.create_sheet("3.2 Structural Regularity")
    storeys = project.get_storeys_sorted()
    lam = project.lmax / project.lmin if project.lmin > 0 else 0
    r = 1

    # ── 3.2.1 Plan Regularity ──
    ws.cell(row=r, column=1, value="3.2.1 Regularity in Plan").font = TITLE_FONT
    r += 1
    ws.cell(row=r, column=1, value=f"λ = Lmax/Lmin = {project.lmax}/{project.lmin} = {lam:.3f}  →  {'OK' if lam < 4 else 'NOT OK'}")
    r += 2

    # ── 3.2.2 Structural Eccentricity ──
    ws.cell(row=r, column=1, value="3.2.2 Structural Eccentricity").font = TITLE_FONT
    r += 1
    ws.cell(row=r, column=1, value="eox = Xcm − Xcr,  eoy = Ycm − Ycr").font = SUBTITLE_FONT
    r += 1
    r = _write_header_row(ws, r, ["Story", "Xcm (m)", "Ycm (m)", "Xcr (m)", "Ycr (m)", "eox (m)", "eoy (m)"])
    for s in storeys:
        sd, c = s.source_data, s.calculations
        _write_data_row(ws, r, [s.normalized_name, sd.xcm, sd.ycm, sd.xcr, sd.ycr, c.eox, c.eoy])
        r += 1
    r += 1

    # ── 3.2.3 Torsional Radius ──
    ws.cell(row=r, column=1, value="3.2.3 Torsional Radius").font = TITLE_FONT
    r += 1
    ws.cell(row=r, column=1, value="rx = √(KMT/KFY),  ry = √(KMT/KFX)").font = SUBTITLE_FONT
    r += 1
    r = _write_header_row(ws, r, ["Story", "UX(UL1)", "UY(UL2)", "RZ(UL3)", "KFX", "KFY", "KMT", "rx (m)", "ry (m)"])
    for s in storeys:
        sd, c = s.source_data, s.calculations
        _write_data_row(ws, r, [s.normalized_name, sd.ux_ul1, sd.uy_ul2, sd.rz_ul3, c.kfx, c.kfy, c.kmt, c.rx, c.ry])
        r += 1
    r += 1

    # ── 3.2.4 Eccentricity vs Gyration ──
    ws.cell(row=r, column=1, value="3.2.4 Eccentricity vs Gyration").font = TITLE_FONT
    r += 1
    ws.cell(row=r, column=1, value="|eox| ≤ 0.3·rx,  |eoy| ≤ 0.3·ry").font = SUBTITLE_FONT
    r += 1
    r = _write_header_row(ws, r, ["Story", "eox", "rx", "0.3·rx", "Status X", "eoy", "ry", "0.3·ry", "Status Y"])
    for s in storeys:
        c = s.calculations
        _write_data_row(ws, r, [s.normalized_name, c.eox, c.rx, c.module_3_2_4_limit_x, c.module_3_2_4_eox_status,
                                c.eoy, c.ry, c.module_3_2_4_limit_y, c.module_3_2_4_eoy_status], status_col=5, status_val=c.module_3_2_4_eox_status)
        cell_y = ws.cell(row=r, column=9)
        if c.module_3_2_4_eoy_status == "OK": cell_y.fill = GREEN_FILL
        elif c.module_3_2_4_eoy_status == "NOT OK": cell_y.fill = RED_FILL
        r += 1
    r += 1

    # ── 3.2.5 Torsional vs Floor Radius ──
    ws.cell(row=r, column=1, value="3.2.5 Torsional Radius vs Floor Radius").font = TITLE_FONT
    r += 1
    ws.cell(row=r, column=1, value="rx ≥ ls,  ry ≥ ls").font = SUBTITLE_FONT
    r += 1
    r = _write_header_row(ws, r, ["Story", "rx", "ls", "Status X", "ry", "ls", "Status Y"])
    for s in storeys:
        c = s.calculations
        _write_data_row(ws, r, [s.normalized_name, c.rx, c.ls, c.module_3_2_5_rx_status,
                                c.ry, c.ls, c.module_3_2_5_ry_status], status_col=4, status_val=c.module_3_2_5_rx_status)
        cell_y = ws.cell(row=r, column=7)
        if c.module_3_2_5_ry_status == "OK": cell_y.fill = GREEN_FILL
        elif c.module_3_2_5_ry_status == "NOT OK": cell_y.fill = RED_FILL
        r += 1
    r += 1

    # ── 3.2.6 Storey Stiffness X ──
    ws.cell(row=r, column=1, value="3.2.6 Storey Stiffness X").font = TITLE_FONT
    r += 1
    ws.cell(row=r, column=1, value="Kx = VX(EQX) / ΔUX,  Criterion: Ki > 0.7·Ki+1").font = SUBTITLE_FONT
    r += 1
    r = _write_header_row(ws, r, ["Story", "Kx (kN/m)", "VX (EQX)", "ΔUX (EQX)", "Status"])
    for s in storeys:
        sd, c = s.source_data, s.calculations
        _write_data_row(ws, r, [s.normalized_name, c.kx, sd.vx_eqx, sd.ux_eqx, c.module_3_2_6_status], status_col=5, status_val=c.module_3_2_6_status)
        r += 1
    r += 1

    # ── 3.2.7 Storey Stiffness Y ──
    ws.cell(row=r, column=1, value="3.2.7 Storey Stiffness Y").font = TITLE_FONT
    r += 1
    ws.cell(row=r, column=1, value="Ky = VY(EQY) / ΔUY,  Criterion: Ki > 0.7·Ki+1").font = SUBTITLE_FONT
    r += 1
    r = _write_header_row(ws, r, ["Story", "Ky (kN/m)", "VY (EQY)", "ΔUY (EQY)", "Status"])
    for s in storeys:
        sd, c = s.source_data, s.calculations
        _write_data_row(ws, r, [s.normalized_name, c.ky, sd.vy_eqy, sd.uy_eqy, c.module_3_2_7_status], status_col=5, status_val=c.module_3_2_7_status)
        r += 1
    r += 1

    # ── 3.2.8 Mass Distribution ──
    ws.cell(row=r, column=1, value="3.2.8 Mass Distribution").font = TITLE_FONT
    r += 1
    ws.cell(row=r, column=1, value="Mi < 2·Mi+1,  Mi < 2·Mi−1").font = SUBTITLE_FONT
    r += 1
    r = _write_header_row(ws, r, ["Story", "Mass (x10^3 kg)", "Mi < 2*Mi+1", "Mi < 2*Mi-1"])
    for s in storeys:
        c = s.calculations
        _write_data_row(ws, r, [s.normalized_name, c.module_3_2_8_mass, c.module_3_2_8_status_upper, c.module_3_2_8_status_lower], status_col=3, status_val=c.module_3_2_8_status_upper)
        cell = ws.cell(row=r, column=4)
        if c.module_3_2_8_status_lower == "OK": cell.fill = GREEN_FILL
        elif c.module_3_2_8_status_lower == "NOT OK": cell.fill = RED_FILL
        r += 1
    r += 1

    # ── Building Summary ──
    ws.cell(row=r, column=1, value="Building Summary").font = TITLE_FONT
    r += 1
    for line in project.building_summary.split("\n"):
        ws.cell(row=r, column=1, value=line)
        r += 1


# ─── Section 3.3–4.6 sheets ─────────────────────────────────────────────

def _create_3_3_sheet(wb, data):
    ws = wb.create_sheet("3.3 Classification")
    ws["A1"] = "3.3 Building Classification (Lateral Force Participation)"
    ws["A1"].font = TITLE_FONT
    ws["A3"] = "Building Classification:"
    ws["B3"] = data.get("building_classification", "")
    ws["B3"].font = BOLD_FONT
    ws["A4"] = data.get("description", "")

    # X-direction
    ws["A6"] = "X-Direction (UL1)"
    ws["A6"].font = SUBTITLE_FONT
    r = 7
    r = _write_header_row(ws, r, ["Story", "Lateral (kN)", "Column Force", "Wall Force", "Col %", "Wall %"])
    for s in data.get("x_direction", {}).get("storeys", []):
        _write_data_row(ws, r, [s["name"], s["lateral"], s["column_force"], s["wall_force"],
                                 f'{s["column_pct"]*100:.1f}%', f'{s["wall_pct"]*100:.1f}%'])
        r += 1

    # Y-direction
    r += 1
    ws.cell(row=r, column=1, value="Y-Direction (UL2)").font = SUBTITLE_FONT
    r += 1
    r = _write_header_row(ws, r, ["Story", "Lateral (kN)", "Column Force", "Wall Force", "Col %", "Wall %"])
    for s in data.get("y_direction", {}).get("storeys", []):
        _write_data_row(ws, r, [s["name"], s["lateral"], s["column_force"], s["wall_force"],
                                 f'{s["column_pct"]*100:.1f}%', f'{s["wall_pct"]*100:.1f}%'])
        r += 1


def _create_3_4_sheet(wb, data):
    ws = wb.create_sheet("3.4 Behavioral Factor")
    ws["A1"] = "3.4 Behavioral Factor (q)"
    ws["A1"].font = TITLE_FONT
    labels = [
        ("Building Type", data.get("building_type", "")),
        ("Plan Regularity", data.get("regularity_plan", "")),
        ("Elevation Regularity", data.get("regularity_elevation", "")),
        ("q₀", data.get("qo", "")),
        ("kw", data.get("kw", "")),
        ("αu/α₁", data.get("alpha_ratio", "")),
        ("q (Design)", data.get("q", "")),
        ("Formula", data.get("description", "")),
    ]
    for i, (label, val) in enumerate(labels, 3):
        ws.cell(row=i, column=1, value=label).font = BOLD_FONT
        ws.cell(row=i, column=2, value=val)


def _create_4_1_sheet(wb, data):
    ws = wb.create_sheet("4.1 Base Shear")
    ws["A1"] = "4.1 Base Shear Calculation"
    ws["A1"].font = TITLE_FONT
    params = [
        ("ag", f'{data.get("ag", "")} g'),
        ("Ground Type", data.get("ground_type", "")),
        ("S", data.get("S", "")),
        ("TB", f'{data.get("TB", "")} s'),
        ("TC", f'{data.get("TC", "")} s'),
        ("TD", f'{data.get("TD", "")} s'),
        ("T₁x", f'{data.get("T1x", "")} s'),
        ("T₁y", f'{data.get("T1y", "")} s'),
        ("q", data.get("q", "")),
        ("β (Lower Bound)", data.get("beta", "")),
        ("Total Weight", f'{data.get("total_weight_kN", 0):.0f} kN'),
        ("Sd(T)x", f'{data.get("Sd_x", 0):.4f}g = {data.get("Sd_x_pct", 0):.1f}% x ag'),
        ("Sd(T)y", f'{data.get("Sd_y", 0):.4f}g = {data.get("Sd_y_pct", 0):.1f}% x ag'),
        ("Fb (X)", f'{data.get("Fb_x", 0):.0f} kN'),
        ("Fb (Y)", f'{data.get("Fb_y", 0):.0f} kN'),
    ]
    for i, (label, val) in enumerate(params, 3):
        ws.cell(row=i, column=1, value=label).font = BOLD_FONT
        ws.cell(row=i, column=2, value=val)


def _create_4_2_sheet(wb, data):
    ws = wb.create_sheet("4.2 Modal Participation")
    ws["A1"] = "4.2 Modal Load Participation"
    ws["A1"].font = TITLE_FONT
    ws["A3"] = f'T₁x = {data.get("T1x", "")} s, T₁y = {data.get("T1y", "")} s'
    r = 5
    r = _write_header_row(ws, r, ["Mode", "Period (s)", "UX (%)", "UY (%)", "Sum UX", "Sum UY", "RX (%)", "RY (%)"])
    for m in data.get("modes", []):
        _write_data_row(ws, r, [m["mode"], f'{m["period"]:.4f}', f'{m["ux"]:.4f}', f'{m["uy"]:.4f}',
                                 f'{m["sum_ux"]:.4f}', f'{m["sum_uy"]:.4f}', f'{m["rx"]:.4f}', f'{m["ry"]:.4f}'])
        r += 1


def _create_4_3_sheet(wb, data):
    ws = wb.create_sheet("4.3 Imperfections")
    ws["A1"] = "4.3 Geometric Imperfections"
    ws["A1"].font = TITLE_FONT
    ws["A3"] = f'theta_i = {data.get("theta0", "")} * {data.get("alpha_h", "")} * {data.get("alpha_m", "")} = {data.get("theta_i", "")}'
    r = 5
    r = _write_header_row(ws, r, ["Story", "Ptot (kN)", "Height (m)", "θi", "Hi (kN)"])
    for s in data.get("storeys", []):
        _write_data_row(ws, r, [s["name"], s["ptot"], s["height"], s["theta_i"], s["hi"]])
        r += 1


def _create_4_4_sheet(wb, data):
    ws = wb.create_sheet("4.4 Stability")
    ws["A1"] = "4.4 Stability Analysis (P-Delta)"
    ws["A1"].font = TITLE_FONT
    ws["A3"] = f'Max θx = {data.get("max_theta_x", 0):.4f} ({data.get("max_classification_x", "")})'
    ws["A4"] = f'Max θy = {data.get("max_theta_y", 0):.4f} ({data.get("max_classification_y", "")})'
    r = 6
    r = _write_header_row(ws, r, ["Story", "Load Case", "Dir", "Ptot (kN)", "Hu (kN)", "Δu (m)", "Height (m)", "θ", "Status"])
    for s in data.get("storeys", []):
        _write_data_row(ws, r, [s["name"], s["load_case"], s["direction"], s["ptot"], s["hu"],
                                 s["delta_u"], s["height"], s["theta"], s["classification"]],
                        status_col=9, status_val=s["classification"])
        r += 1


def _create_4_5_sheet(wb, data):
    ws = wb.create_sheet("4.5 Drift Control")
    ws["A1"] = "4.5 Storey Drift Control (Damage Limitation)"
    ws["A1"].font = TITLE_FONT
    ws["A3"] = f'ν = {data.get("nu", "")}, Limit = {data.get("limit", "")}'
    ws["A4"] = f'Max X ratio = {data.get("max_ratio_x", 0):.6f} ({data.get("max_status_x", "")})'
    ws["A5"] = f'Max Y ratio = {data.get("max_ratio_y", 0):.6f} ({data.get("max_status_y", "")})'
    r = 7
    r = _write_header_row(ws, r, ["Story", "Load Case", "Dir", "Height (m)", "dr (m)", "ν·dr/h", "Limit", "Status"])
    for s in data.get("storeys", []):
        _write_data_row(ws, r, [s["name"], s["load_case"], s["direction"], s["height"],
                                 s["dr"], s["nu_dr_h"], s["limit"], s["status"]],
                        status_col=8, status_val=s["status"])
        r += 1


def _create_4_6_sheet(wb, data):
    ws = wb.create_sheet("4.6 Overturning")
    ws["A1"] = "4.6 Overturning Check"
    ws["A1"].font = TITLE_FONT
    ws["A3"] = f'Total Weight: {data.get("total_weight_kN", 0):.0f} kN'
    ws["A4"] = f'Required Safety Factor: {data.get("required_sf", 1.5)}'

    for direction, label in [("x_direction", "X-Direction"), ("y_direction", "Y-Direction")]:
        d = data.get(direction, {})
        r = ws.max_row + 2
        ws.cell(row=r, column=1, value=label).font = SUBTITLE_FONT
        r += 1
        ws.cell(row=r, column=1, value=f'OT Moment: {d.get("total_ot_moment", 0):.0f} kN·m')
        ws.cell(row=r, column=3, value=f'Resisting: {d.get("resisting_moment", 0):.0f} kN·m')
        ws.cell(row=r, column=5, value=f'SF: {d.get("safety_factor", 0):.2f}')
        ws.cell(row=r, column=6, value="PASS" if d.get("passes") else "FAIL")
        r += 1
        r = _write_header_row(ws, r, ["Story", "Elevation (m)", "Shear (kN)", "OT Moment (kN·m)"])
        for s in d.get("storeys", []):
            _write_data_row(ws, r, [s["name"], s["elevation"], s["shear"], s["ot_moment"]])
            r += 1


# ─── Summary sheet ───────────────────────────────────────────────────────

def _create_summary_sheet(wb, project, sections=None):
    ws = wb.create_sheet("Summary")
    ws["A1"] = "Building Structural Regularity Summary"
    ws["A1"].font = TITLE_FONT

    row = 3
    for line in project.building_summary.split("\n"):
        ws.cell(row=row, column=1, value=line)
        row += 1

    # Add section-level summaries
    if sections:
        row += 1
        ws.cell(row=row, column=1, value="Section Results").font = SUBTITLE_FONT
        row += 1
        summary_items = []
        if "3.3" in sections:
            summary_items.append(("3.3 Classification", sections["3.3"].get("building_classification", "")))
        if "3.4" in sections:
            summary_items.append(("3.4 q-factor", sections["3.4"].get("q", "")))
        if "4.1" in sections:
            summary_items.append(("4.1 Fb (X)", f'{sections["4.1"].get("Fb_x", 0):.0f} kN'))
            summary_items.append(("4.1 Fb (Y)", f'{sections["4.1"].get("Fb_y", 0):.0f} kN'))
        if "4.4" in sections:
            summary_items.append(("4.4 Max θx", f'{sections["4.4"].get("max_theta_x", 0):.4f} ({sections["4.4"].get("max_classification_x", "")})'))
            summary_items.append(("4.4 Max θy", f'{sections["4.4"].get("max_theta_y", 0):.4f} ({sections["4.4"].get("max_classification_y", "")})'))
        if "4.5" in sections:
            summary_items.append(("4.5 Max Drift X", f'{sections["4.5"].get("max_ratio_x", 0):.6f} ({sections["4.5"].get("max_status_x", "")})'))
            summary_items.append(("4.5 Max Drift Y", f'{sections["4.5"].get("max_ratio_y", 0):.6f} ({sections["4.5"].get("max_status_y", "")})'))
        if "4.6" in sections:
            summary_items.append(("4.6 SF (X)", f'{sections["4.6"].get("x_direction", {}).get("safety_factor", 0):.2f}'))
            summary_items.append(("4.6 SF (Y)", f'{sections["4.6"].get("y_direction", {}).get("safety_factor", 0):.2f}'))
        for label, val in summary_items:
            ws.cell(row=row, column=1, value=label).font = BOLD_FONT
            ws.cell(row=row, column=2, value=val)
            row += 1

    # Storey details table
    row += 2
    ws.cell(row=row, column=1, value="Storey Details").font = SUBTITLE_FONT
    row += 1
    headers = ["Story", "eox", "eoy", "rx", "ry", "Kx", "Ky", "Classification"]
    r = _write_header_row(ws, row, headers)
    for storey in project.get_storeys_sorted():
        c = storey.calculations
        _write_data_row(ws, r, [storey.normalized_name, c.eox, c.eoy, c.rx, c.ry, c.kx, c.ky,
                                 c.overall_classification.value])
        r += 1
