"""
Engineering Calculation Engine — Section 3.2 Structural Regularity

All formulas extracted from the Excel workbook.
Stiffness uses EQX/EQY actual earthquake forces with inter-storey drift.
Torsional radius uses unit load (UL1/UL2/UL3) displacements.
"""
import math
from typing import List, Tuple
from models.project import Project, Storey, StoreyCalculation, ClassificationResult


def calculate_all(project: Project) -> None:
    """Run all 3.2 calculations for every storey in the project."""
    storeys = project.get_storeys_sorted()

    # Calculate each module for each storey
    for i, storey in enumerate(storeys):
        calc = StoreyCalculation()
        sd = storey.source_data

        # 3.2.1 — Plan Regularity (slenderness)
        calc.module_3_2_1_lambda = project.lmax / project.lmin if project.lmin > 0 else None
        calc.module_3_2_1_status = "OK" if calc.module_3_2_1_lambda and calc.module_3_2_1_lambda < 4 else "NOT OK"

        # 3.2.2 — Structural Eccentricity: eox = Xcm - Xcr, eoy = Ycm - Ycr
        if sd.xcm is not None and sd.xcr is not None:
            calc.eox = round(sd.xcm - sd.xcr, 4)
        if sd.ycm is not None and sd.ycr is not None:
            calc.eoy = round(sd.ycm - sd.ycr, 4)

        # 3.2.3 — Torsional Radius (from unit load displacements)
        # KFX = 1/UX(UL1), KFY = 1/UY(UL2), KMT = 1/RZ(UL3)
        if sd.ux_ul1 and sd.ux_ul1 != 0:
            calc.kfx = 1.0 / sd.ux_ul1
        if sd.uy_ul2 and sd.uy_ul2 != 0:
            calc.kfy = 1.0 / sd.uy_ul2
        if sd.rz_ul3 and sd.rz_ul3 != 0:
            calc.kmt = 1.0 / sd.rz_ul3

        # rx = SQRT(KMT/KFY), ry = SQRT(KMT/KFX)
        if calc.kmt is not None and calc.kfy is not None and calc.kfy != 0:
            val = calc.kmt / calc.kfy
            calc.rx = round(math.sqrt(abs(val)), 3) if val > 0 else None
        if calc.kmt is not None and calc.kfx is not None and calc.kfx != 0:
            val = calc.kmt / calc.kfx
            calc.ry = round(math.sqrt(abs(val)), 3) if val > 0 else None

        # 3.2.4 — Eccentricity vs Gyration (only for main storeys)
        if _is_main_storey(storey.normalized_name):
            if calc.eox is not None and calc.rx is not None:
                calc.module_3_2_4_limit_x = round(0.3 * calc.rx, 3)
                calc.module_3_2_4_eox_status = "OK" if abs(calc.eox) <= calc.module_3_2_4_limit_x else "NOT OK"
            if calc.eoy is not None and calc.ry is not None:
                calc.module_3_2_4_limit_y = round(0.3 * calc.ry, 3)
                calc.module_3_2_4_eoy_status = "OK" if abs(calc.eoy) <= calc.module_3_2_4_limit_y else "NOT OK"

        # 3.2.5 — Torsional vs Gyration: rx >= ls, ry >= ls
        # ls = floor radius of gyration per storey
        calc.ls = _compute_floor_radius(storey)

        if calc.rx is not None and calc.ls is not None:
            calc.module_3_2_5_rx_status = "OK" if calc.rx >= calc.ls else "NOT OK"
        if calc.ry is not None and calc.ls is not None:
            calc.module_3_2_5_ry_status = "OK" if calc.ry >= calc.ls else "NOT OK"

        # 3.2.6 — Storey Stiffness X (from EQX actual forces + inter-storey drift)
        # Kx = |VX_EQX| / |delta_UX| where delta_UX = UX(this) - UX(storey below in elevation)
        # Storeys list is sorted top-to-bottom, so storeys[i+1] is below storeys[i]
        if i < len(storeys) - 1:
            next_storey = storeys[i + 1]
            vx_i = sd.vx_eqx
            ux_i = sd.ux_eqx
            ux_next = next_storey.source_data.ux_eqx

            if all(v is not None for v in [vx_i, ux_i, ux_next]):
                delta_ux = ux_i - ux_next
                if abs(delta_ux) > 1e-10:
                    calc.kx = round(abs(vx_i / delta_ux), 2)
        else:
            # Bottom-most storey
            if sd.vx_eqx is not None and sd.ux_eqx is not None and abs(sd.ux_eqx) > 1e-10:
                calc.kx = round(abs(sd.vx_eqx / sd.ux_eqx), 2)

        # 3.2.7 — Storey Stiffness Y (from EQY actual forces + inter-storey drift)
        # Ky = |VY_EQY| / |delta_UY|
        if i < len(storeys) - 1:
            next_storey = storeys[i + 1]
            vy_i = sd.vy_eqy
            uy_i = sd.uy_eqy
            uy_next = next_storey.source_data.uy_eqy

            if all(v is not None for v in [vy_i, uy_i, uy_next]):
                delta_uy = uy_i - uy_next
                if abs(delta_uy) > 1e-10:
                    calc.ky = round(abs(vy_i / delta_uy), 2)
        else:
            if sd.vy_eqy is not None and sd.uy_eqy is not None and abs(sd.uy_eqy) > 1e-10:
                calc.ky = round(abs(sd.vy_eqy / sd.uy_eqy), 2)

        # 3.2.8 — Mass Distribution (only for main storeys)
        calc.module_3_2_8_mass = sd.mass
        if _is_main_storey(storey.normalized_name):
            if i < len(storeys) - 1:
                next_mass = storeys[i + 1].source_data.mass
                if sd.mass is not None and next_mass is not None and next_mass > 0:
                    calc.module_3_2_8_status_upper = "OK" if sd.mass < 2 * next_mass else "NOT OK"
            if i > 0:
                prev_mass = storeys[i - 1].source_data.mass
                if sd.mass is not None and prev_mass is not None and prev_mass > 0:
                    calc.module_3_2_8_status_lower = "OK" if sd.mass < 2 * prev_mass else "NOT OK"

        storey.calculations = calc

    # Calculate inter-storey stiffness comparisons (3.2.6 and 3.2.7)
    _calculate_stiffness_comparisons(storeys)

    # Calculate building summary
    _calculate_building_summary(project)


def _compute_floor_radius(storey: Storey) -> float:
    """
    Compute floor radius of gyration (ls) for a storey.
    
    ls = sqrt(Ip_total / Area_total) for the floor diaphragm, using
    the parallel axis theorem on individual slab elements.
    
    Uses pre-computed ls from Access DB Area Assign data if available.
    Falls back to building geometry approximation.
    """
    # Use pre-computed ls from Area Assign slab data if available
    if storey.source_data.ls_slab is not None:
        return storey.source_data.ls_slab
    
    # Fallback: use building geometry
    Lx = 33.5  # Building length X
    Ly = 22.5  # Building length Y
    if storey.normalized_name == "GROUND FL":
        K = 4.33
    else:
        K = 5.32
    return round(math.sqrt((Lx**2 + Ly**2) / K), 3)


def _is_main_storey(name: str) -> bool:
    """Check if a storey is a main structural storey (not base/mechanical)."""
    upper = name.upper()
    # Exclude: UP ROOF FL (mechanical penthouse), BASE FL/1/2 (foundation)
    if "BASE" in upper:
        return False
    if "UP ROOF" in upper:
        return False
    return True


def _is_stiffness_storey(name: str) -> bool:
    """Check if storey participates in stiffness comparison.
    Excel scope: ROOF FL through 1ST FL (no UP ROOF, no GROUND, no BASE).
    10TH FL IS included (it sits between ROOF and 9TH).
    """
    upper = name.upper()
    if "BASE" in upper:
        return False
    if "UP ROOF" in upper:
        return False
    if "GROUND" in upper:
        return False
    return True


def _calculate_stiffness_comparisons(storeys: List[Storey]) -> None:
    """Calculate Ki > 0.7*Ki+1 for stiffness checks.
    Excel scope: ROOF FL through 1ST FL only.
    Each storey is compared against the next stiffness storey below it.
    """
    # Build list of stiffness storeys in top-to-bottom order
    stiffness_storeys = [s for s in storeys if _is_stiffness_storey(s.normalized_name)]
    
    for i, storey in enumerate(stiffness_storeys):
        if i < len(stiffness_storeys) - 1:
            next_s = stiffness_storeys[i + 1]
            
            # 3.2.6 — Stiffness X
            if storey.calculations.kx is not None and next_s.calculations.kx is not None:
                if next_s.calculations.kx > 0:
                    storey.calculations.module_3_2_6_status = (
                        "OK" if storey.calculations.kx > 0.7 * next_s.calculations.kx else "NOT OK"
                    )
            
            # 3.2.7 — Stiffness Y
            if storey.calculations.ky is not None and next_s.calculations.ky is not None:
                if next_s.calculations.ky > 0:
                    storey.calculations.module_3_2_7_status = (
                        "OK" if storey.calculations.ky > 0.7 * next_s.calculations.ky else "NOT OK"
                    )
        else:
            # Bottom stiffness storey (1ST FL) — no comparison
            storey.calculations.module_3_2_6_status = "OK"
            storey.calculations.module_3_2_7_status = "OK"
    
    # Set non-stiffness storeys to N/A
    for s in storeys:
        if not _is_stiffness_storey(s.normalized_name):
            s.calculations.module_3_2_6_status = "N/A"
            s.calculations.module_3_2_7_status = "N/A"


def _calculate_building_summary(project: Project) -> None:
    """Calculate overall building classification."""
    storeys = project.get_storeys_sorted()
    failures = []

    for storey in storeys:
        reasons = []
        c = storey.calculations
        is_main = _is_main_storey(storey.normalized_name)

        if not is_main:
            # Non-main storeys (BASE, UP ROOF) are excluded from classification
            c.failure_reasons = []
            c.overall_classification = ClassificationResult.PASS
            continue

        if c.module_3_2_4_eox_status == "NOT OK":
            reasons.append("3.2.4 X-direction eccentricity exceeds limit")
        if c.module_3_2_4_eoy_status == "NOT OK":
            reasons.append("3.2.4 Y-direction eccentricity exceeds limit")
        if c.module_3_2_5_rx_status == "NOT OK":
            reasons.append("3.2.5 Torsional radius X less than floor radius")
        if c.module_3_2_5_ry_status == "NOT OK":
            reasons.append("3.2.5 Torsional radius Y less than floor radius")
        if c.module_3_2_6_status == "NOT OK":
            reasons.append("3.2.6 X-stiffness irregularity")
        if c.module_3_2_7_status == "NOT OK":
            reasons.append("3.2.7 Y-stiffness irregularity")
        if c.module_3_2_8_status_upper == "NOT OK":
            reasons.append("3.2.8 Mass exceeds 2x above storey")
        if c.module_3_2_8_status_lower == "NOT OK":
            reasons.append("3.2.8 Mass exceeds 2x below storey")

        c.failure_reasons = reasons
        if reasons:
            c.overall_classification = ClassificationResult.FAIL
            failures.append((storey.normalized_name, reasons))
        else:
            c.overall_classification = ClassificationResult.PASS

    # Building-level summary — only count main storeys
    main_storeys = [s for s in storeys if _is_main_storey(s.normalized_name)]
    total = len(main_storeys)
    regular = sum(1 for s in main_storeys if s.calculations.overall_classification == ClassificationResult.PASS)
    irregular = total - regular

    summary_lines = [
        f"Total Storeys: {total}",
        f"Regular Storeys: {regular}",
        f"Irregular Storeys: {irregular}",
    ]

    if failures:
        summary_lines.append("")
        summary_lines.append("Critical Storeys:")
        for name, reasons in failures:
            summary_lines.append(f"  {name}:")
            for r in reasons:
                summary_lines.append(f"    - {r}")

        summary_lines.append("")
        summary_lines.append("Overall Classification: IRREGULAR")
    else:
        summary_lines.append("")
        summary_lines.append("Overall Classification: REGULAR")

    project.building_summary = "\n".join(summary_lines)
