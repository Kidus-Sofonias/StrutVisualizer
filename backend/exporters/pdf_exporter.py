"""
PDF Exporter — clean, compact professional engineering report.
Uses reportlab for PDF generation.
"""
import os
from datetime import datetime
from typing import Dict, Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER

from models.project import Project, ClassificationResult


def _fmt(v, d=3):
    if v is None or v == "" or v == "-":
        return "-"
    try:
        return f"{float(v):.{d}f}"
    except (TypeError, ValueError):
        return str(v)


def _status_color(status):
    if status in ("OK", "PASS", "NO SWAY"):
        return colors.HexColor("#15803d")
    elif status in ("NOT OK", "FAIL", "SWAY"):
        return colors.HexColor("#b91c1c")
    return colors.HexColor("#a16207")


def export_to_pdf(project: Project, output_path: str, sections: Dict = None) -> str:
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=15*mm, bottomMargin=15*mm,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("Title2", parent=styles["Title"], fontSize=16, spaceAfter=6)
    sub_style = ParagraphStyle("Sub", parent=styles["Heading2"], fontSize=12, spaceAfter=4, textColor=colors.HexColor("#1F4E79"))
    note_style = ParagraphStyle("Note", parent=styles["Normal"], fontSize=8, textColor=colors.grey, spaceAfter=2)
    story = []

    # ── Title page ──
    story.append(Paragraph("Structural Engineering Analysis", title_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph(f"<b>Project:</b> {project.project_name}", styles["Normal"]))
    story.append(Paragraph(f"<b>Client:</b> {project.client or 'N/A'}", styles["Normal"]))
    story.append(Paragraph(f"<b>Designed by:</b> {project.designed_by or 'N/A'}", styles["Normal"]))
    story.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles["Normal"]))
    story.append(Spacer(1, 12))

    # Building summary
    story.append(Paragraph("Building Summary", sub_style))
    for line in project.building_summary.split("\n"):
        if line.strip():
            story.append(Paragraph(line.strip(), styles["Normal"]))
    story.append(PageBreak())

    storeys = project.get_storeys_sorted()

    # ── 3.2 Structural Regularity ──
    story.append(Paragraph("3.2 Structural Regularity", title_style))
    story.append(Spacer(1, 8))

    # 3.2.2 Table
    story.append(Paragraph("Table 3.2.2: Structural Eccentricity", sub_style))
    story.append(Paragraph("eox = Xcm - Xcr,  eoy = Ycm - Ycr", note_style))
    data = [["Story", "CMX", "CMY", "CRX", "CRY", "eox", "eoy"]]
    for s in storeys:
        sd = s.source_data
        eox = sd.xcm - sd.xcr if sd.xcm is not None and sd.xcr is not None else None
        eoy = sd.ycm - sd.ycr if sd.ycm is not None and sd.ycr is not None else None
        data.append([s.normalized_name, _fmt(sd.xcm), _fmt(sd.ycm),
                     _fmt(sd.xcr), _fmt(sd.ycr), _fmt(eox), _fmt(eoy)])
    t = Table(data, repeatRows=1)
    t.setStyle(_table_style())
    story.append(t)
    story.append(Spacer(1, 12))

    # 3.2.4 Table
    story.append(Paragraph("Table 3.2.4: Eccentricity vs Gyration", sub_style))
    story.append(Paragraph("|eox| <= 0.3*rx,  |eoy| <= 0.3*ry", note_style))
    data = [["Story", "eox", "rx", "0.3*rx", "X", "eoy", "ry", "0.3*ry", "Y"]]
    for s in storeys:
        c = s.calculations
        data.append([s.normalized_name, _fmt(abs(c.eox) if c.eox else None),
                     _fmt(c.rx), _fmt(c.module_3_2_4_limit_x), c.module_3_2_4_eox_status or "-",
                     _fmt(abs(c.eoy) if c.eoy else None), _fmt(c.ry),
                     _fmt(c.module_3_2_4_limit_y), c.module_3_2_4_eoy_status or "-"])
    t = Table(data, repeatRows=1)
    t.setStyle(_table_style(status_cols=[5, 9]))
    story.append(t)
    story.append(Spacer(1, 12))

    # 3.2.5 Table
    story.append(Paragraph("Table 3.2.5: Torsional Radius vs Floor Radius", sub_style))
    story.append(Paragraph("rx >= ls,  ry >= ls", note_style))
    data = [["Story", "rx", "ls", "Status", "ry", "ls", "Status"]]
    for s in storeys:
        c = s.calculations
        data.append([s.normalized_name, _fmt(c.rx), _fmt(c.ls),
                     c.module_3_2_5_rx_status or "-", _fmt(c.ry), _fmt(c.ls),
                     c.module_3_2_5_ry_status or "-"])
    t = Table(data, repeatRows=1)
    t.setStyle(_table_style(status_cols=[4, 7]))
    story.append(t)
    story.append(Spacer(1, 12))

    # 3.2.6 Table
    story.append(Paragraph("Table 3.2.6: Storey Stiffness X", sub_style))
    story.append(Paragraph("Kx = |VX(EQX)| / |DriftX * H|,  Ki >= 0.7*Ki+1", note_style))
    data = [["Story", "Kx (kN/m)", "Status"]]
    for s in storeys:
        c = s.calculations
        data.append([s.normalized_name, _fmt(c.kx, 1), c.module_3_2_6_status or "-"])
    t = Table(data, repeatRows=1)
    t.setStyle(_table_style(status_cols=[3]))
    story.append(t)
    story.append(Spacer(1, 12))

    # 3.2.7 Table
    story.append(Paragraph("Table 3.2.7: Storey Stiffness Y", sub_style))
    story.append(Paragraph("Ky = |VY(EQY)| / |DriftY * H|,  Ki >= 0.7*Ki+1", note_style))
    data = [["Story", "Ky (kN/m)", "Status"]]
    for s in storeys:
        c = s.calculations
        data.append([s.normalized_name, _fmt(c.ky, 1), c.module_3_2_7_status or "-"])
    t = Table(data, repeatRows=1)
    t.setStyle(_table_style(status_cols=[3]))
    story.append(t)
    story.append(Spacer(1, 12))

    # 3.2.8 Table
    story.append(Paragraph("Table 3.2.8: Mass Distribution", sub_style))
    story.append(Paragraph("Mi < 2Mi+1  and  Mi < 2Mi-1", note_style))
    data = [["Story", "Mass (t)", "< 2*Upper", "< 2*Lower"]]
    for s in storeys:
        c = s.calculations
        data.append([s.normalized_name, _fmt(c.module_3_2_8_mass),
                     c.module_3_2_8_status_upper or "-",
                     c.module_3_2_8_status_lower or "-"])
    t = Table(data, repeatRows=1)
    t.setStyle(_table_style(status_cols=[3, 4]))
    story.append(t)
    story.append(PageBreak())

    # ── Other sections ──
    if sections:
        for sec_id in ["3.3", "3.4", "4.1", "4.2", "4.3", "4.4", "4.5", "4.6"]:
            sec_data = sections.get(sec_id)
            if not sec_data:
                continue
            sec_titles = {
                "3.3": "3.3 Lateral Force Participation",
                "3.4": "3.4 Behavioral Factor",
                "4.1": "4.1 Base Shear",
                "4.2": "4.2 Modal Load Participation",
                "4.3": "4.3 Geometric Imperfection",
                "4.4": "4.4 Stability Analysis",
                "4.5": "4.5 Storey Drift Control",
                "4.6": "4.6 Overturning Check",
            }
            story.append(Paragraph(sec_titles.get(sec_id, sec_id), title_style))
            story.append(Spacer(1, 8))
            _add_section_to_pdf(story, styles, sec_data)
            story.append(PageBreak())

    doc.build(story)
    return output_path


def _add_section_to_pdf(story, styles, data):
    """Add section data to PDF story."""
    if isinstance(data, dict):
        for key, val in data.items():
            if isinstance(val, list) and val and isinstance(val[0], dict):
                story.append(Paragraph(str(key), styles["Heading3"]))
                headers = list(val[0].keys())
                table_data = [headers]
                for row in val:
                    table_data.append([_fmt(row.get(h)) if isinstance(row.get(h), float) else str(row.get(h, "-")) for h in headers])
                t = Table(table_data, repeatRows=1)
                t.setStyle(_table_style())
                story.append(t)
                story.append(Spacer(1, 8))
            elif isinstance(val, (str, int, float)):
                story.append(Paragraph(f"<b>{key}:</b> {val}", styles["Normal"]))
    elif isinstance(data, list) and data and isinstance(data[0], dict):
        headers = list(data[0].keys())
        table_data = [headers]
        for row in data:
            table_data.append([_fmt(row.get(h)) if isinstance(row.get(h), float) else str(row.get(h, "-")) for h in headers])
        t = Table(table_data, repeatRows=1)
        t.setStyle(_table_style())
        story.append(t)


def _table_style(status_cols=None):
    """Generate a clean compact table style."""
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E79")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 7),
        ("FONTSIZE", (0, 0), (-1, 0), 7),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f8fafc")]),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
    ]
    if status_cols:
        for col_idx in status_cols:
            # Color status cells
            pass  # Would need per-cell coloring which reportlab handles differently
    return TableStyle(style_cmds)
