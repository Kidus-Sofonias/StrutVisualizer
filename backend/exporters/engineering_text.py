"""
Engineering text extracted from the original Excel workbook.
Used by Excel and PDF exporters to include engineering background,
formulas, and criteria in exported reports.
"""

ENGINEERING_TEXT = {
    "3.2": {
        "background": (
            "Structural regularity is a fundamental concept in seismic design according to "
            "Eurocode 8 (ES EN 1998-1-1:2015). A regular structure behaves predictably during "
            "an earthquake, with well-distributed inelastic deformations and no dangerous "
            "concentration of damage.\n\n"
            "The assessment evaluates both plan regularity and elevation regularity through "
            "quantitative checks on the structural geometry, mass distribution, stiffness "
            "distribution, and torsional response of the building."
        ),
        "criteria": (
            "3.2.1 Regularity in Plan:\n"
            "- Building shall be approximately symmetrical in plan\n"
            "- In-plan stiffness of floors shall be sufficiently large\n"
            "- Slenderness (Lmax/Lmin) shall not exceed 4\n\n"
            "3.2.2 Structural Eccentricity: eox = Xcm - Xcr, eoy = Ycm - Ycr\n\n"
            "3.2.3 Torsional Radius: rx = sqrt(KMT/KFY), ry = sqrt(KMT/KFX)\n\n"
            "3.2.4 Eccentricity vs Gyration: |eox| <= 0.3*rx, |eoy| <= 0.3*ry\n\n"
            "3.2.5 Torsional Radius vs Floor Radius: rx >= ls, ry >= ls\n\n"
            "3.2.6/3.2.7 Storey Stiffness: Ki > 0.7*Ki+1\n\n"
            "3.2.8 Mass Distribution: Mi < 2*Mi+1, Mi < 2*Mi-1"
        ),
    },
    "3.3": {
        "background": (
            "During seismic action, a building behaves based on the type of lateral force "
            "resisting system attached to it. Based on the mechanism through which the structure "
            "responds during seismic action, it is classified into various categories:\n\n"
            "- Frame System: More than 65% of base shear resisted by frame action\n"
            "- Wall System: More than 65% of base shear captured by primary shear wall\n"
            "- Dual System: Both frame and wall contribute to lateral resistance\n"
            "  - Frame Equivalent: More than 50% by frame action\n"
            "  - Wall Equivalent: More than 50% by wall action\n"
            "- Torsionally Flexible: Radius of gyration exceeds torsional radius\n"
            "- Inverted Pendulum: At least 50% mass in upper third of height"
        ),
    },
    "3.4": {
        "background": (
            "To avoid explicit inelastic structural analysis in design, the capacity of the "
            "structure to dissipate energy, through mainly ductile behaviour of its elements "
            "and/or other mechanisms, is taken into account through the behavior factor q.\n\n"
            "q = Fel / Fy\n\n"
            "Where:\n"
            "- Fel is the peak force in an SDOF system responding elastically\n"
            "- Fy is the yield load of the system\n\n"
            "For vertical seismic action, q up to 1.5 should generally be adopted."
        ),
        "formula": "q = qo * kw * (au/a1)",
        "criteria": (
            "qo: basic behavior factor, dependent on structural system type and regularity\n"
            "kw: factor reflecting prevailing failure mode in wall systems\n"
            "au/a1: multiplication factor (1.0 for regular, varies for irregular)\n\n"
            "ES EN 1998-1-1:2015, cl.5.2.2.2(1)"
        ),
    },
    "4.1": {
        "background": (
            "Eurocode 8 recommends highly idealized spectra, which follow the physical "
            "constraints and the characteristic features of actual spectra and are intended "
            "to represent average characteristics of ground motion on specific soil types.\n\n"
            "Reference return period:\n"
            "- No Collapse: 10% probability in 50 years (475-year return)\n"
            "- Damage Limitation: 10% probability in 10 years\n\n"
            "Building located in Addis Ababa, Seismic Zone 3.\n"
            "Importance class: II (Ordinary building)"
        ),
        "formula": (
            "Sd(T) = ag * S * (2/3 + T/TB * (2.5/q - 2/3))  for 0 <= T <= TB\n"
            "Sd(T) = ag * S * 2.5/q  for TB <= T <= TC\n"
            "Sd(T) = ag * S * 2.5/q * (TC/T)  for TC <= T <= TD\n"
            "Fb = Sd(T1) * W * lambda / q"
        ),
    },
    "4.2": {
        "background": (
            "The first mode of vibration or fundamental period of a building is the longest "
            "natural period of vibration. ETABS performs eigenvalue analysis to determine "
            "natural frequencies and mode shapes.\n\n"
            "Mass participation ratio indicates how much of the total building mass is "
            "activated in each mode. A minimum of 90% cumulative mass participation is "
            "typically required in each horizontal direction."
        ),
    },
    "4.3": {
        "background": (
            "The unfavorable effects of possible deviation in the geometry of the structure "
            "and the position of load shall be taken into account according to "
            "ES EN 1992.1.1:2015 Article 5.2.\n\n"
            "Imperfections shall be taken into account in ultimate limit states in persistent "
            "and accidental design situations.\n\n"
            "Imperfections may be represented by inclination: theta_i = theta_0 * alpha_h * alpha_m"
        ),
        "formula": "theta_i = theta_0 * alpha_h * alpha_m\nHi = Ptot * theta_i",
    },
    "4.4": {
        "background": (
            "Deflections in structural members induce secondary moments (P-Delta effects). "
            "Seismic design requires taking into account second-order effects whenever they "
            "exceed 10% of first-order effects.\n\n"
            "For values between 2% and 10%, second-order effects may be accounted for by "
            "multiplying first-order effects by 1/(1-theta)."
        ),
        "formula": "theta = sum(Pu * Delta_u) / (Hu * hs)",
        "criteria": (
            "- theta < 0.1: NO SWAY (second-order effects can be ignored or amplified)\n"
            "- theta >= 0.1: SWAY (second-order analysis required)\n"
            "- theta >= 0.3: Structure not adequate (redesign required)"
        ),
    },
    "4.5": {
        "background": (
            "Damage Limitation is related to the reduction of economic losses in frequent "
            "earthquakes, both structural and non-structural.\n\n"
            "Limits for non-structural elements:\n"
            "- Brittle material attached to structure: dr/h <= 0.005\n"
            "- Ductile non-structural elements: dr/h <= 0.0075\n"
            "- Non-structural fixed to not interfere: dr/h <= 0.010"
        ),
        "formula": "nu * dr / h <= limit",
        "criteria": (
            "Reduction factor nu (ES EN 1998-1-1):\n"
            "- Importance Class II: nu = 0.5"
        ),
    },
    "4.6": {
        "background": (
            "Building overturning occurs when the moment caused by lateral seismic forces "
            "exceeds the stabilizing moment provided by self-weight.\n\n"
            "The safety factor is the ratio of resisting (stabilizing) moment to overturning "
            "moment. A minimum safety factor of 1.5 is required."
        ),
        "formula": (
            "M_ot = sum(Vi * hi)\n"
            "M_resist = W * d\n"
            "SF = M_resist / M_ot >= 1.5"
        ),
        "criteria": (
            "Where:\n"
            "- Vi = story shear force at storey i\n"
            "- hi = elevation of storey i\n"
            "- W = total building weight at ground floor level\n"
            "- d = distance from building center to edge (X or Y direction)\n"
            "- SF >= 1.5 is required for safety"
        ),
    },
}
