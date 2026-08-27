"""
PDF Exporter — generates professional engineering report.
"""
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

from ..models.project import Project, ClassificationResult


def export_to_pdf(project: Project, output_path: str) -> str:
    """Export engineering report to PDF."""
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                           topMargin=20*mm, bottomMargin=20*mm,
                           leftMargin=15*mm, rightMargin=15*mm)
    
    styles = getSampleStyleSheet()
    story = []
    
    # Title
    title_style = ParagraphStyle('CustomTitle', parent=styles['Title'],
                                  fontSize=18, spaceAfter=20)
    story.append(Paragraph("Structural Engineering Analysis Report", title_style))
    story.append(Spacer(1, 10))
    
    # Project info
    story.append(Paragraph(f"<b>Project:</b> {project.project_name}", styles['Normal']))
    story.append(Paragraph(f"<b>Client:</b> {project.client}", styles['Normal']))
    story.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
    story.append(Spacer(1, 20))
    
    # Building Summary
    story.append(Paragraph("Building Summary", styles['Heading2']))
    for line in project.building_summary.split("\n"):
        if line.strip():
            story.append(Paragraph(line, styles['Normal']))
    story.append(Spacer(1, 20))
    
    # 3.2.2 — Structural Eccentricity
    story.append(Paragraph("3.2.2 Structural Eccentricity", styles['Heading2']))
    story.append(Paragraph("Formula: eox = Xcm - Xcr, eoy = Ycm - Ycr", styles['Normal']))
    story.append(Spacer(1, 10))
    
    data = [["Story", "Xcm", "Ycm", "Xcr", "Ycr", "eox", "eoy"]]
    for storey in project.get_storeys_sorted():
        sd = storey.source_data
        c = storey.calculations
        data.append([
            storey.normalized_name,
            f"{sd.xcm:.3f}" if sd.xcm else "-",
            f"{sd.ycm:.3f}" if sd.ycm else "-",
            f"{sd.xcr:.3f}" if sd.xcr else "-",
            f"{sd.ycr:.3f}" if sd.ycr else "-",
            f"{c.eox:.3f}" if c.eox else "-",
            f"{c.eoy:.3f}" if c.eoy else "-",
        ])
    
    t = Table(data, colWidths=[80, 55, 55, 55, 55, 55, 55])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F4E79')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0F0F0')]),
    ]))
    story.append(t)
    story.append(Spacer(1, 20))
    
    # 3.2.3 — Torsional Radius
    story.append(Paragraph("3.2.3 Torsional Radius", styles['Heading2']))
    story.append(Paragraph("rx = SQRT(KMT/KFY), ry = SQRT(KMT/KFX)", styles['Normal']))
    story.append(Spacer(1, 10))
    
    data = [["Story", "KFX", "KFY", "KMT", "rx", "ry"]]
    for storey in project.get_storeys_sorted():
        c = storey.calculations
        data.append([
            storey.normalized_name,
            f"{c.kfx:.6f}" if c.kfx else "-",
            f"{c.kfy:.6f}" if c.kfy else "-",
            f"{c.kmt:.4f}" if c.kmt else "-",
            f"{c.rx:.3f}" if c.rx else "-",
            f"{c.ry:.3f}" if c.ry else "-",
        ])
    
    t = Table(data, colWidths=[80, 70, 70, 70, 60, 60])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F4E79')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0F0F0')]),
    ]))
    story.append(t)
    story.append(Spacer(1, 20))
    
    # 3.2.6 — Stiffness X
    story.append(Paragraph("3.2.6 Storey Stiffness X Direction", styles['Heading2']))
    story.append(Paragraph("Criterion: Ki > 0.7 * Ki+1", styles['Normal']))
    story.append(Spacer(1, 10))
    
    data = [["Story", "Kx (kN/m)", "Status"]]
    for storey in project.get_storeys_sorted():
        c = storey.calculations
        data.append([
            storey.normalized_name,
            f"{c.kx:.2f}" if c.kx else "-",
            c.module_3_2_6_status or "-",
        ])
    
    t = Table(data, colWidths=[100, 100, 80])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F4E79')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0F0F0')]),
    ]))
    story.append(t)
    story.append(Spacer(1, 20))
    
    # 3.2.7 — Stiffness Y
    story.append(Paragraph("3.2.7 Storey Stiffness Y Direction", styles['Heading2']))
    story.append(Paragraph("Criterion: Ki > 0.7 * Ki+1", styles['Normal']))
    story.append(Spacer(1, 10))
    
    data = [["Story", "Ky (kN/m)", "Status"]]
    for storey in project.get_storeys_sorted():
        c = storey.calculations
        data.append([
            storey.normalized_name,
            f"{c.ky:.2f}" if c.ky else "-",
            c.module_3_2_7_status or "-",
        ])
    
    t = Table(data, colWidths=[100, 100, 80])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F4E79')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0F0F0')]),
    ]))
    story.append(t)
    story.append(Spacer(1, 20))
    
    # 3.2.8 — Mass Distribution
    story.append(Paragraph("3.2.8 Mass Distribution", styles['Heading2']))
    story.append(Paragraph("Criterion: Mi < 2*Mi+1, Mi < 2*Mi-1", styles['Normal']))
    story.append(Spacer(1, 10))
    
    data = [["Story", "Mass (1000 kg)", "Mi < 2*Mi+1", "Mi < 2*Mi-1"]]
    for storey in project.get_storeys_sorted():
        c = storey.calculations
        data.append([
            storey.normalized_name,
            f"{c.module_3_2_8_mass:.1f}" if c.module_3_2_8_mass else "-",
            c.module_3_2_8_status_upper or "-",
            c.module_3_2_8_status_lower or "-",
        ])
    
    t = Table(data, colWidths=[90, 90, 80, 80])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1F4E79')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F0F0F0')]),
    ]))
    story.append(t)
    
    doc.build(story)
    return output_path
