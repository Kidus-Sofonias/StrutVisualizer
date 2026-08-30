"""
PDF Exporter — clean, compact professional engineering report.
Uses reportlab for PDF generation.
"""
import os
from datetime import datetime
from typing import Dict, Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
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
    sub_style = ParagraphStyle("Sub", parent=styles["Heading2"], fontSize=12, spaceAfter=4,
                               textColor=colors.HexColor("#1F4E79"))
    note_style = ParagraphStyle("Note", parent=styles["Normal"], fontSize=8, textColor=colors.grey,
                                spaceAfter=2)
    body_style = ParagraphStyle("Body", parent=styles["Normal"], fontSize=8, leading=11, spaceAfter=4)
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
    _add_engineering_text_pdf(story, styles, "3.2")

    # 3.2.1 Slenderness
    story.append(Paragraph("Table 3.2.1: Slenderness", sub_style))
    story.append(Paragraph(f"λ = Lmax/Lmin = {project.lmax}/{project.lmin} = "
                           f"{round(project.lmax/project.lmin, 4)}", note_style))
    lam = round(project.lmax / project.lmin, 4)
    data = [["Story", "Lmax", "Lmin", "λ", "Status"]]
    for s in storeys:
        data.append([s.normalized_name, f"{project.lmax}", f"{project.lmin}",
                     str(lam), "OK" if lam < 4 else "NOT OK"])
    t = Table(data, repeatRows=1)
    t.setStyle(_table_style(status_cols=[5]))
    story.append(t)
    story.append(Spacer(1, 10))

    # 3.2.2 Eccentricity
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
    story.append(Spacer(1, 10))

    # 3.2.4 Eccentricity vs Gyration
    story.append(Paragraph("Table 3.2.4: Eccentricity vs Gyration", sub_style))
    story.append(Paragraph("|eox| <= 0.3*rx,  |eoy| <= 0.3*ry", note_style))
    data = [["Story", "|eox|", "rx", "0.3*rx", "X", "|eoy|", "ry", "0.3*ry", "Y"]]
    for s in storeys:
        c = s.calculations
        data.append([s.normalized_name,
                     _fmt(abs(c.eox) if c.eox else None),
                     _fmt(c.rx), _fmt(c.module_3_2_4_limit_x),
                     c.module_3_2_4_eox_status or "-",
                     _fmt(abs(c.eoy) if c.eoy else None),
                     _fmt(c.ry), _fmt(c.module_3_2_4_limit_y),
                     c.module_3_2_4_eoy_status or "-"])
    t = Table(data, repeatRows=1)
    t.setStyle(_table_style(status_cols=[5, 9]))
    story.append(t)
    story.append(Spacer(1, 10))

    # 3.2.5 Torsional Radius vs Floor Radius
    story.append(Paragraph("Table 3.2.5: Torsional Radius vs Floor Radius", sub_style))
    story.append(Paragraph("rx >= ls,  ry >= ls", note_style))
    data = [["Story", "rx", "ls", "Status", "ry", "ls", "Status"]]
    for s in storeys:
        c = s.calculations
        data.append([s.normalized_name, _fmt(c.rx), _fmt(c.ls),
                     c.module_3_2_5_rx_status or "-",
                     _fmt(c.ry), _fmt(c.ls),
                     c.module_3_2_5_ry_status or "-"])
    t = Table(data, repeatRows=1)
    t.setStyle(_table_style(status_cols=[4, 7]))
    story.append(t)
    story.append(Spacer(1, 10))

    # 3.2.6/3.2.7 Stiffness
    story.append(Paragraph("Table 3.2.6: Storey Stiffness X (EQX)", sub_style))
    data = [["Story", "Kx (kN/m)", "Ki > 0.7*Ki+1"]]
    for s in storeys:
        c = s.calculations
        data.append([s.normalized_name, _fmt(c.kx, 1), c.module_3_2_6_status or "-"])
    t = Table(data, repeatRows=1)
    t.setStyle(_table_style(status_cols=[3]))
    story.append(t)
    story.append(Spacer(1, 8))

    story.append(Paragraph("Table 3.2.7: Storey Stiffness Y (EQY)", sub_style))
    data = [["Story", "Ky (kN/m)", "Ki > 0.7*Ki+1"]]
    for s in storeys:
        c = s.calculations
        data.append([s.normalized_name, _fmt(c.ky, 1), c.module_3_2_7_status or "-"])
    t = Table(data, repeatRows=1)
    t.setStyle(_table_style(status_cols=[3]))
    story.append(t)
    story.append(Spacer(1, 8))

    # 3.2.8 Mass Distribution
    story.append(Paragraph("Table 3.2.8: Mass Distribution", sub_style))
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
            _add_engineering_text_pdf(story, styles, sec_id)
            _add_section_to_pdf(story, styles, sec_data, sec_id)
            story.append(PageBreak())

    doc.build(story)
    return output_path


def _add_engineering_text_pdf(story, styles, section_key):
    """Add engineering background text to PDF."""
    try:
        from exporters.engineering_text import ENGINEERING_TEXT
    except ImportError:
        return

    et = ENGINEERING_TEXT.get(section_key)
    if not et:
        return

    body_style = ParagraphStyle("Body", parent=styles["Normal"], fontSize=8, leading=11, spaceAfter=4)
    formula_style = ParagraphStyle("Formula", parent=styles["Normal"], fontSize=8, fontName="Courier",
                                   leading=10, textColor=colors.HexColor("#1F4E79"),
                                   spaceBefore=4, spaceAfter=4, leftIndent=10)

    if et.get("background"):
        story.append(Paragraph("<b>Background:</b>", styles["Normal"]))
        for para in et["background"].split("\n"):
            if para.strip():
                story.append(Paragraph(para.strip(), body_style))
        story.append(Spacer(1, 4))

    if et.get("formula"):
        story.append(Paragraph("<b>Formula:</b>", styles["Normal"]))
        for line in et["formula"].split("\n"):
            if line.strip():
                story.append(Paragraph(line.strip(), formula_style))
        story.append(Spacer(1, 4))

    if et.get("criteria"):
        story.append(Paragraph("<b>Criteria:</b>", styles["Normal"]))
        for para in et["criteria"].split("\n"):
            if para.strip():
                story.append(Paragraph(para.strip(), body_style))
        story.append(Spacer(1, 6))


def _add_section_to_pdf(story, styles, data, sec_id=""):
    """Add section data to PDF story with proper formatting."""
    if not isinstance(data, dict):
        return

    # Section-specific table formatting
    if sec_id == "3.3":
        _add_3_3_pdf(story, styles, data)
    elif sec_id == "3.4":
        _add_3_4_pdf(story, styles, data)
    elif sec_id == "4.1":
        _add_4_1_pdf(story, styles, data)
    elif sec_id == "4.2":
        _add_4_2_pdf(story, styles, data)
    elif sec_id == "4.3":
        _add_4_3_pdf(story, styles, data)
    elif sec_id == "4.4":
        _add_4_4_pdf(story, styles, data)
    elif sec_id == "4.5":
        _add_4_5_pdf(story, styles, data)
    elif sec_id == "4.6":
        _add_4_6_pdf(story, styles, data)
    else:
        # Generic fallback
        _add_generic_pdf(story, styles, data)


def _add_3_3_pdf(story, styles, data):
    bc = data.get("building_classification", "N/A")
    story.append(Paragraph(f"<b>Building Classification:</b> {bc}", styles["Normal"]))
    story.append(Spacer(1, 6))

    for direction_key, label in [("x_direction", "X-Direction (UL1)"), ("y_direction", "Y-Direction (UL2)")]:
        dd = data.get(direction_key, {})
        story.append(Paragraph(f"<b>{label}</b>", styles["Normal"]))
        tdata = [["Story", "Lateral", "Column", "Wall", "Col%", "Wall%"]]
        for s in dd.get("storeys", []):
            tdata.append([s.get("name", ""), _fmt(s.get("lateral"), 0),
                         _fmt(s.get("column_force"), 0), _fmt(s.get("wall_force"), 0),
                         f"{s.get('column_pct', 0)*100:.1f}%", f"{s.get('wall_pct', 0)*100:.1f}%"])
        t = Table(tdata, repeatRows=1)
        t.setStyle(_table_style())
        story.append(t)
        story.append(Spacer(1, 8))


def _add_3_4_pdf(story, styles, data):
    tdata = [["Parameter", "Value"]]
    for k, v in [("Building Type", data.get("building_type")),
                 ("q₀", data.get("qo")),
                 ("kw", data.get("kw")),
                 ("αu/α1", data.get("alpha_ratio")),
                 ("q (design)", data.get("q")),
                 ("Plan Regularity", data.get("regularity_plan")),
                 ("Elevation Regularity", data.get("regularity_elevation"))]:
        tdata.append([k, str(v) if v is not None else "-"])
    t = Table(tdata, repeatRows=1)
    t.setStyle(_table_style())
    story.append(t)


def _add_4_1_pdf(story, styles, data):
    tdata = [["Parameter", "Value"]]
    for k, v in [("ag", f"{data.get('ag', '')} g"),
                 ("Ground Type", data.get("ground_type")),
                 ("S", data.get("S")),
                 ("TB", f"{data.get('TB', '')} s"),
                 ("TC", f"{data.get('TC', '')} s"),
                 ("TD", f"{data.get('TD', '')} s"),
                 ("β", data.get("beta")),
                 ("q", data.get("q")),
                 ("T1x", f"{data.get('T1x', '')} s"),
                 ("T1y", f"{data.get('T1y', '')} s"),
                 ("Weight", f"{data.get('total_weight_kN', 0):.0f} kN"),
                 ("Fb_x", f"{data.get('Fb_x', 0):.2f} kN"),
                 ("Fb_y", f"{data.get('Fb_y', 0):.2f} kN")]:
        tdata.append([k, str(v) if v is not None else "-"])
    t = Table(tdata, repeatRows=1)
    t.setStyle(_table_style())
    story.append(t)


def _add_4_2_pdf(story, styles, data):
    story.append(Paragraph(f"<b>T1x = {data.get('T1x', 0):.6f} s, T1y = {data.get('T1y', 0):.6f} s</b>",
                           styles["Normal"]))
    story.append(Spacer(1, 4))
    modes = data.get("modes", [])
    if modes:
        tdata = [["Mode", "Period", "UX%", "UY%", "ΣUX%", "ΣUY%"]]
        for m in modes[:10]:
            tdata.append([str(m.get("mode", "")), f"{m.get('period', 0):.4f}",
                         f"{m.get('ux', 0):.4f}", f"{m.get('uy', 0):.4f}",
                         f"{m.get('sum_ux', 0):.2f}", f"{m.get('sum_uy', 0):.2f}"])
        t = Table(tdata, repeatRows=1)
        t.setStyle(_table_style())
        story.append(t)
    story.append(Paragraph(f"<i>Total modes: {data.get('total_modes', 50)} (first 10 shown)</i>",
                           styles["Normal"]))


def _add_4_3_pdf(story, styles, data):
    story.append(Paragraph(f"<b>θi = {data.get('theta0', 0.005)} × {data.get('alpha_h', 1.0)} × "
                           f"{data.get('alpha_m', 0.723)} = {data.get('theta_i', 0)}</b>",
                           styles["Normal"]))
    story.append(Spacer(1, 4))
    tdata = [["Story", "Ptot (kN)", "θi", "Hi (kN)"]]
    for s in data.get("storeys", []):
        tdata.append([s.get("name", ""), _fmt(s.get("ptot"), 0),
                     _fmt(s.get("theta_i"), 6), _fmt(s.get("hi"), 2)])
    t = Table(tdata, repeatRows=1)
    t.setStyle(_table_style())
    story.append(t)


def _add_4_4_pdf(story, styles, data):
    story.append(Paragraph(f"<b>Max θx = {_fmt(data.get('max_theta_x'), 6)} "
                           f"({data.get('max_classification_x', '')})</b>", styles["Normal"]))
    story.append(Paragraph(f"<b>Max θy = {_fmt(data.get('max_theta_y'), 6)} "
                           f"({data.get('max_classification_y', '')})</b>", styles["Normal"]))
    story.append(Spacer(1, 4))
    tdata = [["Story", "Load", "Ptot", "Hu", "Δu", "θ", "Status"]]
    for s in data.get("storeys", [])[:30]:  # Limit to prevent huge PDFs
        tdata.append([s.get("name", ""), s.get("load_case", ""),
                     _fmt(s.get("ptot"), 0), _fmt(s.get("hu"), 0),
                     _fmt(s.get("delta_u"), 6), _fmt(s.get("theta"), 6),
                     s.get("classification", "")])
    t = Table(tdata, repeatRows=1)
    t.setStyle(_table_style(status_cols=[7]))
    story.append(t)


def _add_4_5_pdf(story, styles, data):
    story.append(Paragraph(f"<b>ν = {data.get('nu', 0.5)}, Limit = {data.get('limit', 0.005)}</b>",
                           styles["Normal"]))
    story.append(Paragraph(f"<b>Max X: {_fmt(data.get('max_ratio_x'), 6)} "
                           f"({data.get('max_status_x', '')})</b>", styles["Normal"]))
    story.append(Paragraph(f"<b>Max Y: {_fmt(data.get('max_ratio_y'), 6)} "
                           f"({data.get('max_status_y', '')})</b>", styles["Normal"]))
    story.append(Spacer(1, 4))
    tdata = [["Story", "Load", "drX", "drY", "νdr/h(X)", "νdr/h(Y)", "X", "Y"]]
    for s in data.get("storeys", []):
        tdata.append([s.get("name", ""), s.get("load_case", ""),
                     _fmt(s.get("dr_x"), 6), _fmt(s.get("dr_y"), 6),
                     _fmt(s.get("nu_dr_h_x"), 6), _fmt(s.get("nu_dr_h_y"), 6),
                     s.get("status_x", ""), s.get("status_y", "")])
    t = Table(tdata, repeatRows=1)
    t.setStyle(_table_style(status_cols=[7, 8]))
    story.append(t)


def _add_4_6_pdf(story, styles, data):
    story.append(Paragraph(f"<b>Weight: {data.get('total_weight_kN', 0):.0f} kN</b>",
                           styles["Normal"]))
    story.append(Spacer(1, 4))

    for dir_key, label in [("x_direction", "X-Direction"), ("y_direction", "Y-Direction")]:
        dd = data.get(dir_key, {})
        sf = dd.get("safety_factor", 0)
        story.append(Paragraph(f"<b>{label}: SF = {sf:.2f} {'PASS' if sf >= 1.5 else 'FAIL'}</b>",
                              styles["Normal"]))
        tdata = [["Story", "Elevation", "Shear", "ΣMOT"]]
        total_ot = 0
        for s in dd.get("storeys", []):
            total_ot += s.get("ot_moment", 0)
            tdata.append([s.get("name", ""), _fmt(s.get("elevation"), 2),
                         _fmt(s.get("shear"), 0), _fmt(total_ot, 0)])
        t = Table(tdata, repeatRows=1)
        t.setStyle(_table_style())
        story.append(t)
        story.append(Spacer(1, 4))

    story.append(Paragraph(
        f"<b>OT Moment X: {data.get('x_direction', {}).get('total_ot_moment', 0):.0f} kN·m, "
        f"Resisting: {data.get('x_direction', {}).get('resisting_moment', 0):.0f} kN·m</b>",
        styles["Normal"]))
    story.append(Paragraph(
        f"<b>OT Moment Y: {data.get('y_direction', {}).get('total_ot_moment', 0):.0f} kN·m, "
        f"Resisting: {data.get('y_direction', {}).get('resisting_moment', 0):.0f} kN·m</b>",
        styles["Normal"]))


def _add_generic_pdf(story, styles, data):
    """Generic fallback for sections without specific formatting."""
    for key, val in data.items():
        if isinstance(val, list) and val and isinstance(val[0], dict):
            story.append(Paragraph(f"<b>{key}</b>", styles["Normal"]))
            headers = list(val[0].keys())
            tdata = [headers]
            for row in val:
                tdata.append([str(row.get(h, "-")) for h in headers])
            t = Table(tdata, repeatRows=1)
            t.setStyle(_table_style())
            story.append(t)
            story.append(Spacer(1, 6))
        elif isinstance(val, (str, int, float)):
            story.append(Paragraph(f"<b>{key}:</b> {val}", styles["Normal"]))


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
    return TableStyle(style_cmds)
