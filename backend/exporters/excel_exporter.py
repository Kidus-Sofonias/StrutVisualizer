"""
Excel Exporter — generates Excel workbook with all calculation results.
"""
import os
from datetime import datetime
from typing import Optional
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side

from ..models.project import Project, ClassificationResult


# Style constants
BLUE_FILL = PatternFill(start_color="BDD7EE", end_color="BDD7EE", fill_type="solid")
RED_FILL = PatternFill(start_color="F4CCCC", end_color="F4CCCC", fill_type="solid")
GREEN_FILL = PatternFill(start_color="D9EAD3", end_color="D9EAD3", fill_type="solid")
HEADER_FILL = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
HEADER_FONT = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
TITLE_FONT = Font(name="Calibri", size=14, bold=True, color="1F4E79")
NORMAL_FONT = Font(name="Calibri", size=11)
BOLD_FONT = Font(name="Calibri", size=11, bold=True)
THIN_BORDER = Border(
    left=Side(style="thin"),
    right=Side(style="thin"),
    top=Side(style="thin"),
    bottom=Side(style="thin"),
)


def export_to_excel(project: Project, output_path: str) -> str:
    """Export all calculation results to an Excel workbook."""
    wb = Workbook()
    
    # Remove default sheet
    wb.remove(wb.active)
    
    # Create sheets
    _create_project_info_sheet(wb, project)
    _create_3_2_1_sheet(wb, project)
    _create_3_2_2_sheet(wb, project)
    _create_3_2_3_sheet(wb, project)
    _create_3_2_4_sheet(wb, project)
    _create_3_2_5_sheet(wb, project)
    _create_3_2_6_sheet(wb, project)
    _create_3_2_7_sheet(wb, project)
    _create_3_2_8_sheet(wb, project)
    _create_summary_sheet(wb, project)
    
    # Save
    wb.save(output_path)
    return output_path


def _create_project_info_sheet(wb: Workbook, project: Project):
    """Create project information sheet."""
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


def _create_3_2_1_sheet(wb: Workbook, project: Project):
    """Create 3.2.1 Plan Regularity sheet."""
    ws = wb.create_sheet("3.2.1 Plan Regularity")
    ws["A1"] = "3.2.1 Regularity in Plan"
    ws["A1"].font = TITLE_FONT
    ws["A3"] = "Slenderness Check: λ = Lmax / Lmin < 4"
    ws["A4"] = f"Lmax: {project.lmax} m"
    ws["A5"] = f"Lmin: {project.lmin} m"
    ws["A6"] = f"λ = {project.lmax/project.lmin:.3f}"
    ws["A7"] = "Status: " + ("OK" if project.lmax/project.lmin < 4 else "NOT OK")
    
    # Table
    headers = ["Story", "Lmax (m)", "Lmin (m)", "λ", "Status"]
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=9, column=col, value=h)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.border = THIN_BORDER
    
    for row_idx, storey in enumerate(project.get_storeys_sorted(), 10):
        lam = project.lmax / project.lmin if project.lmin > 0 else 0
        ws.cell(row=row_idx, column=1, value=storey.normalized_name).border = THIN_BORDER
        ws.cell(row=row_idx, column=2, value=project.lmax).border = THIN_BORDER
        ws.cell(row=row_idx, column=3, value=project.lmin).border = THIN_BORDER
        ws.cell(row=row_idx, column=4, value=round(lam, 3)).border = THIN_BORDER
        status = "OK" if lam < 4 else "NOT OK"
        cell = ws.cell(row=row_idx, column=5, value=status)
        cell.border = THIN_BORDER
        cell.fill = GREEN_FILL if status == "OK" else RED_FILL


def _create_3_2_2_sheet(wb: Workbook, project: Project):
    """Create 3.2.2 Structural Eccentricity sheet."""
    ws = wb.create_sheet("3.2.2 Eccentricity")
    ws["A1"] = "Table 3.2.2: Structural Eccentricity of the Building"
    ws["A1"].font = TITLE_FONT
    ws["A3"] = "Formula: eox = Xcm - Xcr, eoy = Ycm - Ycr"
    
    headers = ["Story", "Xcm (m)", "Ycm (m)", "Xcr (m)", "Ycr (m)", "eox (m)", "eoy (m)"]
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=5, column=col, value=h)
        cell.font = HEADER_FONT
        cell.fill = BLUE_FILL
        cell.border = THIN_BORDER
    
    for row_idx, storey in enumerate(project.get_storeys_sorted(), 6):
        sd = storey.source_data
        c = storey.calculations
        ws.cell(row=row_idx, column=1, value=storey.normalized_name).border = THIN_BORDER
        ws.cell(row=row_idx, column=2, value=sd.xcm).border = THIN_BORDER
        ws.cell(row=row_idx, column=3, value=sd.ycm).border = THIN_BORDER
        ws.cell(row=row_idx, column=4, value=sd.xcr).border = THIN_BORDER
        ws.cell(row=row_idx, column=5, value=sd.ycr).border = THIN_BORDER
        ws.cell(row=row_idx, column=6, value=c.eox).border = THIN_BORDER
        ws.cell(row=row_idx, column=7, value=c.eoy).border = THIN_BORDER


def _create_3_2_3_sheet(wb: Workbook, project: Project):
    """Create 3.2.3 Torsional Radius sheet."""
    ws = wb.create_sheet("3.2.3 Torsional Radius")
    ws["A1"] = "Table 3.2.3: Torsional Radius of the Building"
    ws["A1"].font = TITLE_FONT
    ws["A3"] = "Formulas: KFX=1/UX, KFY=1/UY, KMT=1/RZ"
    ws["A4"] = "rx = SQRT(KMT/KFY), ry = SQRT(KMT/KFX)"
    
    headers = ["Story", "UX(UL1)", "UY(UL2)", "RZ(UL3)", "KFX", "KFY", "KMT", "rx (m)", "ry (m)"]
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=6, column=col, value=h)
        cell.font = HEADER_FONT
        cell.fill = BLUE_FILL
        cell.border = THIN_BORDER
    
    for row_idx, storey in enumerate(project.get_storeys_sorted(), 7):
        sd = storey.source_data
        c = storey.calculations
        ws.cell(row=row_idx, column=1, value=storey.normalized_name).border = THIN_BORDER
        ws.cell(row=row_idx, column=2, value=sd.ux_ul1).border = THIN_BORDER
        ws.cell(row=row_idx, column=3, value=sd.uy_ul2).border = THIN_BORDER
        ws.cell(row=row_idx, column=4, value=sd.rz_ul3).border = THIN_BORDER
        ws.cell(row=row_idx, column=5, value=c.kfx).border = THIN_BORDER
        ws.cell(row=row_idx, column=6, value=c.kfy).border = THIN_BORDER
        ws.cell(row=row_idx, column=7, value=c.kmt).border = THIN_BORDER
        ws.cell(row=row_idx, column=8, value=c.rx).border = THIN_BORDER
        ws.cell(row=row_idx, column=9, value=c.ry).border = THIN_BORDER


def _create_3_2_4_sheet(wb: Workbook, project: Project):
    """Create 3.2.4 Eccentricity vs Gyration sheet."""
    ws = wb.create_sheet("3.2.4 Ecc vs Gyration")
    ws["A1"] = "Table 3.2.4: Structural Eccentricity and Radius of Gyration"
    ws["A1"].font = TITLE_FONT
    ws["A3"] = "Criterion: |eox| <= 0.3*rx, |eoy| <= 0.3*ry"
    
    headers = ["Story", "eox (m)", "rx (m)", "0.3*rx", "Status X", "eoy (m)", "ry (m)", "0.3*ry", "Status Y"]
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=5, column=col, value=h)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.border = THIN_BORDER
    
    for row_idx, storey in enumerate(project.get_storeys_sorted(), 6):
        c = storey.calculations
        ws.cell(row=row_idx, column=1, value=storey.normalized_name).border = THIN_BORDER
        ws.cell(row=row_idx, column=2, value=c.eox).border = THIN_BORDER
        ws.cell(row=row_idx, column=3, value=c.rx).border = THIN_BORDER
        ws.cell(row=row_idx, column=4, value=c.module_3_2_4_limit_x).border = THIN_BORDER
        cell = ws.cell(row=row_idx, column=5, value=c.module_3_2_4_eox_status)
        cell.border = THIN_BORDER
        cell.fill = GREEN_FILL if c.module_3_2_4_eox_status == "OK" else RED_FILL
        ws.cell(row=row_idx, column=6, value=c.eoy).border = THIN_BORDER
        ws.cell(row=row_idx, column=7, value=c.ry).border = THIN_BORDER
        ws.cell(row=row_idx, column=8, value=c.module_3_2_4_limit_y).border = THIN_BORDER
        cell = ws.cell(row=row_idx, column=9, value=c.module_3_2_4_eoy_status)
        cell.border = THIN_BORDER
        cell.fill = GREEN_FILL if c.module_3_2_4_eoy_status == "OK" else RED_FILL


def _create_3_2_5_sheet(wb: Workbook, project: Project):
    """Create 3.2.5 Torsional vs Gyration sheet."""
    ws = wb.create_sheet("3.2.5 Torsional vs Gyration")
    ws["A1"] = "Table 3.2.5: Torsional Radius and Radius of Gyration"
    ws["A1"].font = TITLE_FONT
    ws["A3"] = "Criterion: rx >= ls, ry >= ls"
    
    headers = ["Story", "rx (m)", "ls (m)", "Status X", "ry (m)", "ls (m)", "Status Y"]
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=5, column=col, value=h)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.border = THIN_BORDER
    
    for row_idx, storey in enumerate(project.get_storeys_sorted(), 6):
        c = storey.calculations
        ws.cell(row=row_idx, column=1, value=storey.normalized_name).border = THIN_BORDER
        ws.cell(row=row_idx, column=2, value=c.rx).border = THIN_BORDER
        ws.cell(row=row_idx, column=3, value=c.ls).border = THIN_BORDER
        cell = ws.cell(row=row_idx, column=4, value=c.module_3_2_5_rx_status)
        cell.border = THIN_BORDER
        cell.fill = GREEN_FILL if c.module_3_2_5_rx_status == "OK" else RED_FILL
        ws.cell(row=row_idx, column=5, value=c.ry).border = THIN_BORDER
        ws.cell(row=row_idx, column=6, value=c.ls).border = THIN_BORDER
        cell = ws.cell(row=row_idx, column=7, value=c.module_3_2_5_ry_status)
        cell.border = THIN_BORDER
        cell.fill = GREEN_FILL if c.module_3_2_5_ry_status == "OK" else RED_FILL


def _create_3_2_6_sheet(wb: Workbook, project: Project):
    """Create 3.2.6 Storey Stiffness X sheet."""
    ws = wb.create_sheet("3.2.6 Stiffness X")
    ws["A1"] = "Table 3.2.6: Storey Stiffness along X Direction"
    ws["A1"].font = TITLE_FONT
    ws["A3"] = "Criterion: Ki > 0.7 * Ki+1"
    
    headers = ["Story", "Kx (kN/m)", "Status"]
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=5, column=col, value=h)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.border = THIN_BORDER
    
    for row_idx, storey in enumerate(project.get_storeys_sorted(), 6):
        c = storey.calculations
        ws.cell(row=row_idx, column=1, value=storey.normalized_name).border = THIN_BORDER
        ws.cell(row=row_idx, column=2, value=c.kx).border = THIN_BORDER
        cell = ws.cell(row=row_idx, column=3, value=c.module_3_2_6_status)
        cell.border = THIN_BORDER
        if c.module_3_2_6_status == "OK":
            cell.fill = GREEN_FILL
        elif c.module_3_2_6_status == "NOT OK":
            cell.fill = RED_FILL


def _create_3_2_7_sheet(wb: Workbook, project: Project):
    """Create 3.2.7 Storey Stiffness Y sheet."""
    ws = wb.create_sheet("3.2.7 Stiffness Y")
    ws["A1"] = "Table 3.2.7: Storey Stiffness along Y Direction"
    ws["A1"].font = TITLE_FONT
    ws["A3"] = "Criterion: Ki > 0.7 * Ki+1"
    
    headers = ["Story", "Ky (kN/m)", "Status"]
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=5, column=col, value=h)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.border = THIN_BORDER
    
    for row_idx, storey in enumerate(project.get_storeys_sorted(), 6):
        c = storey.calculations
        ws.cell(row=row_idx, column=1, value=storey.normalized_name).border = THIN_BORDER
        ws.cell(row=row_idx, column=2, value=c.ky).border = THIN_BORDER
        cell = ws.cell(row=row_idx, column=3, value=c.module_3_2_7_status)
        cell.border = THIN_BORDER
        if c.module_3_2_7_status == "OK":
            cell.fill = GREEN_FILL
        elif c.module_3_2_7_status == "NOT OK":
            cell.fill = RED_FILL


def _create_3_2_8_sheet(wb: Workbook, project: Project):
    """Create 3.2.8 Mass Distribution sheet."""
    ws = wb.create_sheet("3.2.8 Mass Distribution")
    ws["A1"] = "Table 3.2.8: Mass Distribution along Height"
    ws["A1"].font = TITLE_FONT
    ws["A3"] = "Criterion: Mi < 2*Mi+1, Mi < 2*Mi-1"
    
    headers = ["Story", "Mass (1000 kg)", "Mi < 2*Mi+1", "Mi < 2*Mi-1"]
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=5, column=col, value=h)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.border = THIN_BORDER
    
    for row_idx, storey in enumerate(project.get_storeys_sorted(), 6):
        c = storey.calculations
        ws.cell(row=row_idx, column=1, value=storey.normalized_name).border = THIN_BORDER
        ws.cell(row=row_idx, column=2, value=c.module_3_2_8_mass).border = THIN_BORDER
        cell = ws.cell(row=row_idx, column=3, value=c.module_3_2_8_status_upper)
        cell.border = THIN_BORDER
        if c.module_3_2_8_status_upper == "OK":
            cell.fill = GREEN_FILL
        elif c.module_3_2_8_status_upper == "NOT OK":
            cell.fill = RED_FILL
        cell = ws.cell(row=row_idx, column=4, value=c.module_3_2_8_status_lower)
        cell.border = THIN_BORDER
        if c.module_3_2_8_status_lower == "OK":
            cell.fill = GREEN_FILL
        elif c.module_3_2_8_status_lower == "NOT OK":
            cell.fill = RED_FILL


def _create_summary_sheet(wb: Workbook, project: Project):
    """Create building summary sheet."""
    ws = wb.create_sheet("Summary")
    ws["A1"] = "Building Structural Regularity Summary"
    ws["A1"].font = TITLE_FONT
    
    row = 3
    for line in project.building_summary.split("\n"):
        ws.cell(row=row, column=1, value=line)
        row += 1
    
    row += 2
    ws.cell(row=row, column=1, value="Storey Details").font = TITLE_FONT
    row += 1
    
    headers = ["Story", "eox", "eoy", "rx", "ry", "Kx", "Ky", "Classification"]
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=row, column=col, value=h)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.border = THIN_BORDER
    
    row += 1
    for storey in project.get_storeys_sorted():
        c = storey.calculations
        ws.cell(row=row, column=1, value=storey.normalized_name).border = THIN_BORDER
        ws.cell(row=row, column=2, value=c.eox).border = THIN_BORDER
        ws.cell(row=row, column=3, value=c.eoy).border = THIN_BORDER
        ws.cell(row=row, column=4, value=c.rx).border = THIN_BORDER
        ws.cell(row=row, column=5, value=c.ry).border = THIN_BORDER
        ws.cell(row=row, column=6, value=c.kx).border = THIN_BORDER
        ws.cell(row=row, column=7, value=c.ky).border = THIN_BORDER
        cell = ws.cell(row=row, column=8, value=c.overall_classification.value)
        cell.border = THIN_BORDER
        cell.fill = GREEN_FILL if c.overall_classification == ClassificationResult.PASS else RED_FILL
        row += 1
