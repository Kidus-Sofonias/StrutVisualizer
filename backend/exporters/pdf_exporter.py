"""
PDF Exporter — generates professional engineering report with all sections.
"""
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak

from models.project import Project, ClassificationResult


HEADER_BG = colors.HexColor('#1F4E79')
LIGHT_BG = colors.HexColor('#F0F0F0')
PASS_BG = colors.HexColor('#D9EAD3')
FAIL_BG = colors.HexColor('#F4CCCC')


def _make_table(data, col_widths=None, pass_fail_cols=None):
    """Create a styled table."""
    t = Table(data, colWidths=col_widths)
    style = [
        ('BACKGROUND', (0, 0), (-1, 0), HEADER_BG),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
    ]
    # Color PASS/FAIL cells
    if pass_fail_cols:
        for row_i in range(1, len(data)):
            for col_i in pass_fail_cols:
                if col_i < len(data[row_i]):
                    val = str(data[row_i][col_i])
                    if val in ('OK', 'PASS', 'NO SWAY'):
                        style.append(('BACKGROUND', (col_i, row_i), (col_i, row_i), PASS_BG))
                    elif val in ('NOT OK', 'FAIL', 'SWAY'):
                        style.append(('BACKGROUND', (col_i, row_i), (col_i, row_i), FAIL_BG))
    t.setStyle(TableStyle(style))
    return t


def export_to_pdf(project: Project, output_path: str, sections=None) -> str:
    """Export engineering report to PDF with all sections."""
    doc = SimpleDocTemplate(output_path, pagesize=A4,
                           topMargin=20*mm, bottomMargin=20*mm,
                           leftMargin=15*mm, rightMargin=15*mm)
    styles = getSampleStyleSheet()
    story = []
    title_style = ParagraphStyle('CustomTitle', parent=styles['Title'], fontSize=18, spaceAfter=20)
    h2 = ParagraphStyle('H2', parent=styles['Heading2'], fontSize=14, spaceBefore=16, spaceAfter=8)
    h3 = ParagraphStyle('H3', parent=styles['Heading3'], fontSize=11, spaceBefore=12, spaceAfter=6)
    normal = styles['Normal']
    small = ParagraphStyle('Small', parent=normal, fontSize=8, spaceAfter=4)
    mono = ParagraphStyle('Mono', parent=normal, fontName='Courier', fontSize=9, textColor=colors.HexColor('#2E75B6'))

    storeys = project.get_storeys_sorted()

    # ── Title ──
    story.append(Paragraph("Structural Engineering Analysis Report", title_style))
    story.append(Paragraph(f"<b>Project:</b> {project.project_name}", normal))
    story.append(Paragraph(f"<b>Client:</b> {project.client}", normal))
    story.append(Paragraph(f"<b>Designed by:</b> {project.designed_by}", normal))
    story.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal))
    story.append(Spacer(1, 20))

    # ── Building Summary ──
    story.append(Paragraph("Building Summary", h2))
    for line in project.building_summary.split("\n"):
        if line.strip():
            story.append(Paragraph(line, normal))
    story.append(Spacer(1, 20))

    # ═══════════════════════════════════════════════════════════════
    # SECTION 3.2 — Structural Regularity (all tables on one page group)
    # ═══════════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(Paragraph("3.2 Structural Regularity", h2))
    story.append(Spacer(1, 10))

    # 3.2.1
    lam = project.lmax / project.lmin if project.lmin > 0 else 0
    story.append(Paragraph("3.2.1 Plan Regularity", h3))
    story.append(Paragraph(f"λ = Lmax/Lmin = {project.lmax}/{project.lmin} = {lam:.3f} → {'OK' if lam < 4 else 'NOT OK'}", mono))
    story.append(Spacer(1, 10))

    # 3.2.2
    story.append(Paragraph("3.2.2 Structural Eccentricity", h3))
    story.append(Paragraph("eox = Xcm − Xcr,  eoy = Ycm − Ycr", mono))
    data = [["Story", "Xcm", "Ycm", "Xcr", "Ycr", "eox", "eoy"]]
    for s in storeys:
        sd, c = s.source_data, s.calculations
        data.append([s.normalized_name,
                     f"{sd.xcm:.3f}" if sd.xcm else "-", f"{sd.ycm:.3f}" if sd.ycm else "-",
                     f"{sd.xcr:.3f}" if sd.xcr else "-", f"{sd.ycr:.3f}" if sd.ycr else "-",
                     f"{c.eox:.3f}" if c.eox else "-", f"{c.eoy:.3f}" if c.eoy else "-"])
    story.append(_make_table(data, [70, 50, 50, 50, 50, 50, 50]))
    story.append(Spacer(1, 12))

    # 3.2.3
    story.append(Paragraph("3.2.3 Torsional Radius", h3))
    story.append(Paragraph("rx = √(KMT/KFY),  ry = √(KMT/KFX)", mono))
    data = [["Story", "KFX", "KFY", "KMT", "rx (m)", "ry (m)"]]
    for s in storeys:
        c = s.calculations
        data.append([s.normalized_name,
                     f"{c.kfx:.6f}" if c.kfx else "-", f"{c.kfy:.6f}" if c.kfy else "-",
                     f"{c.kmt:.4f}" if c.kmt else "-",
                     f"{c.rx:.3f}" if c.rx else "-", f"{c.ry:.3f}" if c.ry else "-"])
    story.append(_make_table(data, [70, 70, 70, 70, 55, 55]))
    story.append(Spacer(1, 12))

    # 3.2.4
    story.append(Paragraph("3.2.4 Eccentricity vs Gyration", h3))
    story.append(Paragraph("|eox| ≤ 0.3·rx,  |eoy| ≤ 0.3·ry", mono))
    data = [["Story", "eox", "rx", "0.3·rx", "Status X", "eoy", "ry", "0.3·ry", "Status Y"]]
    for s in storeys:
        c = s.calculations
        data.append([s.normalized_name,
                     f"{c.eox:.3f}" if c.eox else "-", f"{c.rx:.3f}" if c.rx else "-",
                     f"{c.module_3_2_4_limit_x:.3f}" if c.module_3_2_4_limit_x else "-", c.module_3_2_4_eox_status or "-",
                     f"{c.eoy:.3f}" if c.eoy else "-", f"{c.ry:.3f}" if c.ry else "-",
                     f"{c.module_3_2_4_limit_y:.3f}" if c.module_3_2_4_limit_y else "-", c.module_3_2_4_eoy_status or "-"])
    story.append(_make_table(data, [65, 45, 45, 50, 55, 45, 45, 50, 55], pass_fail_cols=[4, 8]))
    story.append(Spacer(1, 12))

    # 3.2.5
    story.append(Paragraph("3.2.5 Torsional Radius vs Floor Radius", h3))
    story.append(Paragraph("rx ≥ ls,  ry ≥ ls", mono))
    data = [["Story", "rx", "ls", "Status X", "ry", "ls", "Status Y"]]
    for s in storeys:
        c = s.calculations
        data.append([s.normalized_name,
                     f"{c.rx:.3f}" if c.rx else "-", f"{c.ls:.3f}" if c.ls else "-", c.module_3_2_5_rx_status or "-",
                     f"{c.ry:.3f}" if c.ry else "-", f"{c.ls:.3f}" if c.ls else "-", c.module_3_2_5_ry_status or "-"])
    story.append(_make_table(data, [70, 55, 55, 65, 55, 55, 65], pass_fail_cols=[3, 6]))
    story.append(Spacer(1, 12))

    # 3.2.6
    story.append(Paragraph("3.2.6 Storey Stiffness X", h3))
    story.append(Paragraph("Kx = VX(EQX) / ΔUX,  Criterion: Ki > 0.7·Ki+1", mono))
    data = [["Story", "Kx (kN/m)", "VX (EQX)", "Status"]]
    for s in storeys:
        sd, c = s.source_data, s.calculations
        data.append([s.normalized_name, f"{c.kx:.0f}" if c.kx else "-",
                     f"{sd.vx_eqx:.1f}" if sd.vx_eqx else "-", c.module_3_2_6_status or "-"])
    story.append(_make_table(data, [80, 80, 80, 80], pass_fail_cols=[3]))
    story.append(Spacer(1, 12))

    # 3.2.7
    story.append(Paragraph("3.2.7 Storey Stiffness Y", h3))
    story.append(Paragraph("Ky = VY(EQY) / ΔUY,  Criterion: Ki > 0.7·Ki+1", mono))
    data = [["Story", "Ky (kN/m)", "VY (EQY)", "Status"]]
    for s in storeys:
        sd, c = s.source_data, s.calculations
        data.append([s.normalized_name, f"{c.ky:.0f}" if c.ky else "-",
                     f"{sd.vy_eqy:.1f}" if sd.vy_eqy else "-", c.module_3_2_7_status or "-"])
    story.append(_make_table(data, [80, 80, 80, 80], pass_fail_cols=[3]))
    story.append(Spacer(1, 12))

    # 3.2.8
    story.append(Paragraph("3.2.8 Mass Distribution", h3))
    story.append(Paragraph("Mi < 2·Mi+1,  Mi < 2·Mi−1", mono))
    data = [["Story", "Mass (x10^3 kg)", "Mi < 2*Mi+1", "Mi < 2*Mi-1"]]
    for s in storeys:
        c = s.calculations
        data.append([s.normalized_name, f"{c.module_3_2_8_mass:.1f}" if c.module_3_2_8_mass else "-",
                     c.module_3_2_8_status_upper or "-", c.module_3_2_8_status_lower or "-"])
    story.append(_make_table(data, [80, 90, 80, 80], pass_fail_cols=[2, 3]))

    # ═══════════════════════════════════════════════════════════════
    # SECTIONS 3.3–4.6 (only if sections data provided)
    # ═══════════════════════════════════════════════════════════════
    if sections:
        # 3.3
        if "3.3" in sections:
            s33 = sections["3.3"]
            story.append(PageBreak())
            story.append(Paragraph("3.3 Building Classification", h2))
            story.append(Paragraph(f"<b>Classification:</b> {s33.get('building_classification', '')}", normal))
            story.append(Paragraph(s33.get("description", ""), normal))
            story.append(Spacer(1, 10))

            story.append(Paragraph("X-Direction (UL1)", h3))
            data = [["Story", "Lateral (kN)", "Column", "Wall", "Col %", "Wall %"]]
            for s in s33.get("x_direction", {}).get("storeys", []):
                data.append([s["name"], f"{s['lateral']:.0f}", f"{s['column_force']:.0f}",
                             f"{s['wall_force']:.0f}", f"{s['column_pct']*100:.1f}%", f"{s['wall_pct']*100:.1f}%"])
            story.append(_make_table(data, [70, 75, 75, 75, 55, 55]))
            story.append(Spacer(1, 10))

            story.append(Paragraph("Y-Direction (UL2)", h3))
            data = [["Story", "Lateral (kN)", "Column", "Wall", "Col %", "Wall %"]]
            for s in s33.get("y_direction", {}).get("storeys", []):
                data.append([s["name"], f"{s['lateral']:.0f}", f"{s['column_force']:.0f}",
                             f"{s['wall_force']:.0f}", f"{s['column_pct']*100:.1f}%", f"{s['wall_pct']*100:.1f}%"])
            story.append(_make_table(data, [70, 75, 75, 75, 55, 55]))

        # 3.4
        if "3.4" in sections:
            s34 = sections["3.4"]
            story.append(PageBreak())
            story.append(Paragraph("3.4 Behavioral Factor (q)", h2))
            story.append(Paragraph(f"<b>q = {s34.get('q', '')}</b> ({s34.get('description', '')})", normal))
            story.append(Paragraph(f"Building Type: {s34.get('building_type', '')}", normal))
            story.append(Paragraph(f"Plan: {s34.get('regularity_plan', '')}, Elevation: {s34.get('regularity_elevation', '')}", normal))

        # 4.1
        if "4.1" in sections:
            s41 = sections["4.1"]
            story.append(PageBreak())
            story.append(Paragraph("4.1 Base Shear Calculation", h2))
            story.append(Paragraph(f"ag = {s41.get('ag', '')}g, Ground Type = {s41.get('ground_type', '')}, q = {s41.get('q', '')}", normal))
            sd_x = s41.get('Sd_x', 0)
            sd_y = s41.get('Sd_y', 0)
            story.append(Paragraph(f"Sd(T)x = {sd_x:.4f}g = {s41.get('Sd_x_pct', 0):.1f}% x ag, Fb = {s41.get('Fb_x', 0):.0f} kN", normal))
            story.append(Paragraph(f"Sd(T)y = {sd_y:.4f}g = {s41.get('Sd_y_pct', 0):.1f}% x ag, Fb = {s41.get('Fb_y', 0):.0f} kN", normal))
            story.append(Paragraph(f"Total Weight = {s41.get('total_weight_kN', 0):.0f} kN", normal))

        # 4.2
        if "4.2" in sections:
            s42 = sections["4.2"]
            story.append(PageBreak())
            story.append(Paragraph("4.2 Modal Participation", h2))
            story.append(Paragraph(f"T₁x = {s42.get('T1x', '')}s ({    s42.get('mass_x', '')}%), T1y = {s42.get('T1y', '')}s ({s42.get('mass_y', '')}%)", normal))
            story.append(Spacer(1, 10))
            data = [["Mode", "Period (s)", "UX (%)", "UY (%)", "Sum UX", "Sum UY"]]
            for m in s42.get("modes", [])[:10]:
                data.append([str(m["mode"]), f"{m['period']:.4f}", f"{m['ux']:.4f}", f"{m['uy']:.4f}",
                             f"{m['sum_ux']:.4f}", f"{m['sum_uy']:.4f}"])
            story.append(_make_table(data, [40, 70, 60, 60, 65, 65]))

        # 4.3
        if "4.3" in sections:
            s43 = sections["4.3"]
            story.append(PageBreak())
            story.append(Paragraph("4.3 Geometric Imperfections", h2))
            story.append(Paragraph(f"theta_i = {s43.get('theta0', '')} * {s43.get('alpha_h', '')} * {s43.get('alpha_m', '')} = {s43.get('theta_i', '')}", mono))
            story.append(Spacer(1, 10))
            data = [["Story", "Ptot (kN)", "Height (m)", "θi", "Hi (kN)"]]
            for s in s43.get("storeys", []):
                data.append([s["name"], f"{s['ptot']:.0f}", f"{s['height']:.2f}",
                             f"{s['theta_i']:.6f}", f"{s['hi']:.2f}"])
            story.append(_make_table(data, [80, 80, 70, 80, 70]))

        # 4.4
        if "4.4" in sections:
            s44 = sections["4.4"]
            story.append(PageBreak())
            story.append(Paragraph("4.4 Stability Analysis (P-Delta)", h2))
            story.append(Paragraph(f"Max θx = {s44.get('max_theta_x', 0):.4f} ({s44.get('max_classification_x', '')})", normal))
            story.append(Paragraph(f"Max θy = {s44.get('max_theta_y', 0):.4f} ({s44.get('max_classification_y', '')})", normal))

        # 4.5
        if "4.5" in sections:
            s45 = sections["4.5"]
            story.append(PageBreak())
            story.append(Paragraph("4.5 Storey Drift Control", h2))
            story.append(Paragraph(f"ν = {s45.get('nu', '')},  Limit = {s45.get('limit', '')}", normal))
            story.append(Paragraph(f"Max X: {s45.get('max_ratio_x', 0):.6f} ({s45.get('max_status_x', '')})", normal))
            story.append(Paragraph(f"Max Y: {s45.get('max_ratio_y', 0):.6f} ({s45.get('max_status_y', '')})", normal))

        # 4.6
        if "4.6" in sections:
            s46 = sections["4.6"]
            story.append(PageBreak())
            story.append(Paragraph("4.6 Overturning Check", h2))
            story.append(Paragraph(f"Weight = {s46.get('total_weight_kN', 0):.0f} kN, Required SF ≥ {s46.get('required_sf', 1.5)}", normal))
            xd = s46.get("x_direction", {})
            yd = s46.get("y_direction", {})
            story.append(Paragraph(f"X: OT = {xd.get('total_ot_moment', 0):.0f} kN·m, Resist = {xd.get('resisting_moment', 0):.0f} kN·m, SF = {xd.get('safety_factor', 0):.2f} → {'PASS' if xd.get('passes') else 'FAIL'}", normal))
            story.append(Paragraph(f"Y: OT = {yd.get('total_ot_moment', 0):.0f} kN·m, Resist = {yd.get('resisting_moment', 0):.0f} kN·m, SF = {yd.get('safety_factor', 0):.2f} → {'PASS' if yd.get('passes') else 'FAIL'}", normal))

    doc.build(story)
    return output_path
