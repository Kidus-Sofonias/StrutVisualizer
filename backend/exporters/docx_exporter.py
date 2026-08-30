"""
DOCX Structural Design Report Generator

Adapted from the engineer's V41 report_generator.py.
Generates a professional Word document with:
- Cover page
- Table of Contents
- Sections 2.4 (Loading), 2.5 (Cover), 3.2-4.6
- Tables and engineering conclusions
"""
from pathlib import Path
from datetime import datetime
import math

try:
    from docx import Document
    from docx.shared import Inches, Pt, Cm, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
    from docx.enum.section import WD_ORIENT
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False


BLUE = "365F91"
LIGHT_BLUE = "D9E8F5"
GREEN = "1F7A3D"
RED = "B42318"
GRAY = "666666"


def _set_cell_shading(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = tcPr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tcPr.append(shd)
    shd.set(qn("w:fill"), fill)


def _set_run_font(run, name="Arial", size=9, bold=None, color=None):
    run.font.name = name
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"), name)
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"), name)
    run.font.size = Pt(size)
    if bold is not None:
        run.font.bold = bold
    if color:
        run.font.color.rgb = RGBColor.from_string(color)


def _style_document(doc):
    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Arial"
    normal.font.size = Pt(9.5)
    normal.paragraph_format.space_after = Pt(4)
    normal.paragraph_format.line_spacing = 1.05

    for name, size in [("Title", 24), ("Heading 1", 16), ("Heading 2", 13), ("Heading 3", 11)]:
        st = styles[name]
        st.font.name = "Arial"
        st.font.size = Pt(size)
        st.font.bold = True
        st.font.color.rgb = RGBColor.from_string(BLUE)
        st.paragraph_format.space_before = Pt(8)
        st.paragraph.format.space_after = Pt(5)


def _add_table(doc, headers, rows, col_widths=None):
    """Add a formatted table to the document."""
    table = doc.add_table(rows=1 + len(rows), cols=len(headers))
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Header row
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = ""
        p = cell.paragraphs[0]
        run = p.add_run(str(h))
        _set_run_font(run, size=8, bold=True, color="FFFFFF")
        _set_cell_shading(cell, BLUE)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Data rows
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            cell = table.rows[ri + 1].cells[ci]
            cell.text = ""
            p = cell.paragraphs[0]
            text = str(val) if val is not None else "—"
            run = p.add_run(text)
            _set_run_font(run, size=8)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if ri % 2 == 0:
                _set_cell_shading(cell, LIGHT_BLUE)

    return table


def _fmt(v, digits=3, dash="—"):
    if v is None:
        return dash
    try:
        return f"{float(v):.{digits}f}"
    except (ValueError, TypeError):
        return str(v)


def _status_text(s):
    return str(s or "—")


def _generate_cover_page(doc, project_name, sections):
    """Generate the report cover page."""
    for _ in range(4):
        doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("STRUCTURAL DESIGN REPORT")
    _set_run_font(run, size=28, bold=True, color=BLUE)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f"\n{project_name}")
    _set_run_font(run, size=18, bold=True)

    doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Seismic Analysis per Eurocode 8")
    _set_run_font(run, size=14, color=GRAY)

    doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(f"Generated: {datetime.now().strftime('%B %d, %Y')}")
    _set_run_font(run, size=11, color=GRAY)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run("Structural Engineering Analysis Platform")
    _set_run_font(run, size=11, color=GRAY)

    doc.add_page_break()


def _generate_loading_section(doc, loading_data):
    """Section 2.4 — Loading Schedule."""
    doc.add_heading("2.4 Loading Schedule", level=1)
    doc.add_paragraph(
        "Permanent, imposed and seismic actions are coordinated with Worksheet 2.4 "
        "and the imported ETABS model."
    )

    headers = ["Floor Group", "Occupancy", "Dead (kN/m²)", "Live (kN/m²)",
               "ψE", "Factored Live", "Seismic Total"]
    rows = []
    for item in loading_data.get("schedule", []):
        rows.append([
            item.get("floor_group", ""),
            item.get("occupancy", ""),
            _fmt(item.get("total_dead_knm2")),
            _fmt(item.get("live_knm2")),
            _fmt(item.get("psi_e"), 2),
            _fmt(item.get("factored_live_knm2")),
            _fmt(item.get("seismic_total_knm2")),
        ])
    _add_table(doc, headers, rows)
    doc.add_paragraph()


def _generate_cover_section(doc, cover_data):
    """Section 2.5 — Concrete Cover Check."""
    doc.add_heading("2.5 Concrete Cover Check", level=1)
    doc.add_paragraph(
        f"Aggregate size: {cover_data.get('aggregate_size', 'N/A')}, "
        f"Structural class: {cover_data.get('structural_class', 'N/A')}. "
        f"{cover_data.get('description', '')}"
    )

    headers = ["Group", "Member", "Cmin,bond", "Cmin,dur", "Cmin",
               "Cdev", "Cnom", "Selected", "Status"]
    rows = []
    for item in cover_data.get("rows", []):
        rows.append([
            item.get("group", ""),
            item.get("member", ""),
            _fmt(item.get("cmin_bond"), 0),
            _fmt(item.get("cmin_dur"), 0),
            _fmt(item.get("cmin"), 0),
            _fmt(item.get("cdev"), 0),
            _fmt(item.get("cnom_calculated"), 0),
            _fmt(item.get("selected_cover"), 0),
            item.get("status", ""),
        ])
    _add_table(doc, headers, rows)
    doc.add_paragraph()


def _generate_3_4_section(doc, behavior_data):
    """Section 3.4 — Behavioral Factor."""
    doc.add_heading("3.4 Behavioral Factor (q)", level=1)
    doc.add_paragraph(behavior_data.get("description", ""))

    doc.add_paragraph(
        f"Building type: {behavior_data.get('building_type', 'N/A')}\n"
        f"Ductility class: {behavior_data.get('ductility_class', 'DCM')}\n"
        f"q₀ = {behavior_data.get('q0', 'N/A')}, "
        f"kw = {behavior_data.get('kw', 'N/A')}, "
        f"q = {behavior_data.get('q', 'N/A')}"
    )
    doc.add_paragraph()


def _generate_4_1_section(doc, s41):
    """Section 4.1 — Base Shear."""
    doc.add_heading("4.1 Base Shear", level=1)
    doc.add_paragraph(s41.get("description_x", ""))

    doc.add_paragraph(
        f"Ground type: {s41.get('ground_type', 'B')}, "
        f"ag = {s41.get('ag', 0.1)}g, "
        f"β = {s41.get('beta', 0.2)}, "
        f"q = {s41.get('q', 'N/A')}\n"
        f"Total weight W = {s41.get('total_weight_kN', 0):.2f} kN\n"
        f"T1x = {s41.get('T1x', 0):.4f} s, T1y = {s41.get('T1y', 0):.4f} s\n"
        f"Fb_x = {s41.get('Fb_x', 0):.2f} kN, Fb_y = {s41.get('Fb_y', 0):.2f} kN\n"
        f"Lower bound X = {s41.get('lower_bound_x', 0):.2f} kN\n"
        f"Lower bound Y = {s41.get('lower_bound_y', 0):.2f} kN"
    )
    doc.add_paragraph()


def _generate_4_2_section(doc, s42):
    """Section 4.2 — Modal Participation."""
    doc.add_heading("4.2 Modal Participation", level=1)
    doc.add_paragraph(s42.get("description", ""))

    modes = s42.get("modes", [])
    if modes:
        headers = ["Mode", "Period (s)", "UX (%)", "UY (%)", "ΣUX (%)", "ΣUY (%)"]
        rows = []
        for m in modes[:15]:  # Show first 15 modes
            rows.append([
                m.get("mode", ""),
                _fmt(m.get("period"), 4),
                _fmt(m.get("ux"), 4),
                _fmt(m.get("uy"), 4),
                _fmt(m.get("sum_ux"), 2),
                _fmt(m.get("sum_uy"), 2),
            ])
        # Add final summary row
        if len(modes) > 15:
            last = modes[-1]
            rows.append(["...", "", "", "", "", ""])
            rows.append([
                f"Mode {last.get('mode', 50)}",
                _fmt(last.get("period"), 4),
                _fmt(last.get("ux"), 4),
                _fmt(last.get("uy"), 4),
                _fmt(last.get("sum_ux"), 2),
                _fmt(last.get("sum_uy"), 2),
            ])
        _add_table(doc, headers, rows)
    doc.add_paragraph()


def _generate_4_3_section(doc, s43):
    """Section 4.3 — Geometric Imperfection."""
    doc.add_heading("4.3 Geometric Imperfection", level=1)
    doc.add_paragraph(s43.get("description", ""))

    headers = ["Story", "Ptot (kN)", "θ₀", "L(h)", "αh", "αm", "θi", "Hi (kN)"]
    rows = []
    for s in s43.get("storeys", []):
        rows.append([
            s.get("name", ""),
            _fmt(s.get("ptot"), 0),
            _fmt(s.get("theta0"), 4),
            _fmt(s.get("height"), 2),
            _fmt(s.get("alpha_h"), 3),
            _fmt(s.get("alpha_m"), 6),
            _fmt(s.get("theta_i"), 6),
            _fmt(s.get("hi"), 2),
        ])
    _add_table(doc, headers, rows)
    doc.add_paragraph()


def _generate_4_4_section(doc, s44):
    """Section 4.4 — Stability Analysis."""
    doc.add_heading("4.4 Stability Analysis (P-Delta)", level=1)
    doc.add_paragraph(
        f"Max θx = {s44.get('max_theta_x', 0):.6f} — {s44.get('max_classification_x', '')}\n"
        f"Max θy = {s44.get('max_theta_y', 0):.6f} — {s44.get('max_classification_y', '')}"
    )

    headers = ["Story", "Load Case", "Dir", "Ptot", "Hu", "Δu", "h", "θ", "Status"]
    rows = []
    for s in s44.get("storeys", []):
        rows.append([
            s.get("name", ""),
            s.get("load_case", ""),
            s.get("direction", ""),
            _fmt(s.get("ptot"), 0),
            _fmt(s.get("hu"), 0),
            _fmt(s.get("delta_u"), 6),
            _fmt(s.get("height"), 2),
            _fmt(s.get("theta"), 6),
            s.get("classification", ""),
        ])
    _add_table(doc, headers, rows)
    doc.add_paragraph()


def _generate_4_5_section(doc, s45):
    """Section 4.5 — Storey Drift Control."""
    doc.add_heading("4.5 Storey Drift Control", level=1)
    doc.add_paragraph(
        f"ν = {s45.get('nu', 0.5)}, Limit = {s45.get('limit', 0.005)}\n"
        f"Max X ratio = {s45.get('max_ratio_x', 0):.6f} — {s45.get('max_status_x', '')}\n"
        f"Max Y ratio = {s45.get('max_ratio_y', 0):.6f} — {s45.get('max_status_y', '')}"
    )

    headers = ["Story", "Load Case", "dr X", "dr Y", "ν·dr/h (X)", "ν·dr/h (Y)", "Status"]
    rows = []
    for s in s45.get("storeys", []):
        rows.append([
            s.get("name", ""),
            s.get("load_case", ""),
            _fmt(s.get("dr_x"), 6),
            _fmt(s.get("dr_y"), 6),
            _fmt(s.get("nu_dr_h_x"), 6),
            _fmt(s.get("nu_dr_h_y"), 6),
            f"X:{s.get('status_x', '')} Y:{s.get('status_y', '')}",
        ])
    _add_table(doc, headers, rows)
    doc.add_paragraph()


def _generate_4_6_section(doc, s46):
    """Section 4.6 — Overturning Check."""
    doc.add_heading("4.6 Overturning Check", level=1)

    x_dir = s46.get("x_direction", {})
    y_dir = s46.get("y_direction", {})

    doc.add_paragraph(
        f"Total weight: {s46.get('total_weight_kN', 0):.2f} kN\n"
        f"X: OT Moment = {x_dir.get('total_ot_moment', 0):.2f} kN·m, "
        f"SF = {x_dir.get('safety_factor', 0):.3f} — {'PASS' if x_dir.get('passes') else 'FAIL'}\n"
        f"Y: OT Moment = {y_dir.get('total_ot_moment', 0):.2f} kN·m, "
        f"SF = {y_dir.get('safety_factor', 0):.3f} — {'PASS' if y_dir.get('passes') else 'FAIL'}"
    )
    doc.add_paragraph()


def _generate_engineering_conclusion(doc, sections):
    """Generate the engineering conclusion from actual calculation results."""
    doc.add_heading("Engineering Conclusion", level=1)

    conclusions = []

    # 3.2 regularity
    s33 = sections.get("3.3", {})
    classification = s33.get("building_classification", "N/A")
    conclusions.append(f"The building structural system is classified as: {classification}.")

    # 3.4 q-factor
    s34 = sections.get("3.4", {})
    q = s34.get("q")
    if q:
        conclusions.append(f"The design behavior factor q = {q:.2f}.")

    # 4.1 base shear
    s41 = sections.get("4.1", {})
    if s41.get("Fb_x"):
        conclusions.append(
            f"The seismic base shear is Fb_x = {s41['Fb_x']:.2f} kN (X) and "
            f"Fb_y = {s41.get('Fb_y', 0):.2f} kN (Y)."
        )

    # 4.2 modal
    s42 = sections.get("4.2", {})
    if s42.get("meets_90_pct_x") and s42.get("meets_90_pct_y"):
        conclusions.append(
            f"Modal participation meets the 90% threshold in both directions "
            f"(UX={s42.get('mass_x', 0):.1f}%, UY={s42.get('mass_y', 0):.1f}%)."
        )

    # 4.4 stability
    s44 = sections.get("4.4", {})
    if s44.get("max_classification_x") == "SWAY" or s44.get("max_classification_y") == "SWAY":
        conclusions.append(
            f"The building is P-delta sensitive (SWAY) with max θx = {s44.get('max_theta_x', 0):.4f}, "
            f"max θy = {s44.get('max_theta_y', 0):.4f}. Second-order analysis is required."
        )
    else:
        conclusions.append(
            f"The building is not P-delta sensitive (NO SWAY). "
            f"Max θx = {s44.get('max_theta_x', 0):.4f}, max θy = {s44.get('max_theta_y', 0):.4f}."
        )

    # 4.5 drift
    s45 = sections.get("4.5", {})
    if s45.get("max_status_x") == "OK" and s45.get("max_status_y") == "OK":
        conclusions.append(
            f"Storey drift is within limits "
            f"(max X = {s45.get('max_ratio_x', 0):.6f}, max Y = {s45.get('max_ratio_y', 0):.6f})."
        )
    else:
        conclusions.append(
            f"Storey drift exceeds limits in one or more directions. "
            f"Max X = {s45.get('max_ratio_x', 0):.6f}, max Y = {s45.get('max_ratio_y', 0):.6f}."
        )

    # 4.6 overturning
    s46 = sections.get("4.6", {})
    x_sf = s46.get("x_direction", {}).get("safety_factor", 0)
    y_sf = s46.get("y_direction", {}).get("safety_factor", 0)
    if x_sf and y_sf:
        ok = x_sf > 1.5 and y_sf > 1.5
        conclusions.append(
            f"Overturning safety factor: X = {x_sf:.3f}, Y = {y_sf:.3f} — "
            f"{'satisfactory (>1.5)' if ok else 'NOT SATISFACTORY'}"
        )

    for line in conclusions:
        p = doc.add_paragraph(line)
        p.paragraph_format.space_after = Pt(4)


def generate_docx_report(project, sections, ext_data, output_path):
    """Generate the complete DOCX structural design report."""
    if not HAS_DOCX:
        raise RuntimeError("python-docx is required. Install with: pip install python-docx")

    doc = Document()
    _style_document(doc)

    # Cover page
    _generate_cover_page(doc, project.project_name, sections)

    # Section 2.4 — Loading Schedule
    from calculations.engineering_reports import calculate_loading_schedule
    loading_data = calculate_loading_schedule()
    _generate_loading_section(doc, loading_data)

    # Section 2.5 — Concrete Cover
    from calculations.engineering_reports import calculate_concrete_cover
    cover_data = calculate_concrete_cover()
    _generate_cover_section(doc, cover_data)

    # Section 3.4 — Behavioral Factor
    s34 = sections.get("3.4", {})
    if s34:
        _generate_3_4_section(doc, s34)

    # Section 4.1 — Base Shear
    s41 = sections.get("4.1", {})
    if s41:
        _generate_4_1_section(doc, s41)

    # Section 4.2 — Modal Participation
    s42 = sections.get("4.2", {})
    if s42:
        _generate_4_2_section(doc, s42)

    # Section 4.3 — Geometric Imperfection
    s43 = sections.get("4.3", {})
    if s43:
        _generate_4_3_section(doc, s43)

    # Section 4.4 — Stability
    s44 = sections.get("4.4", {})
    if s44:
        _generate_4_4_section(doc, s44)

    # Section 4.5 — Drift
    s45 = sections.get("4.5", {})
    if s45:
        _generate_4_5_section(doc, s45)

    # Section 4.6 — Overturning
    s46 = sections.get("4.6", {})
    if s46:
        _generate_4_6_section(doc, s46)

    # Engineering Conclusion
    _generate_engineering_conclusion(doc, sections)

    # Save
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    doc.save(str(output_path))
    return str(output_path)
