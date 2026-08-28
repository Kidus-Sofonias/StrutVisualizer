/**
 * Engineering text extracted from the Excel workbook.
 * Each section contains: title, subtitle, background, criteria, formula, notes.
 */

export const engineeringText = {
  '3.2': {
    title: '3.2 — Structural Regularity',
    subtitle: 'Structural Regularity Assessment per Eurocode 8',
    background: `Structural regularity is a fundamental concept in seismic design according to Eurocode 8 (ES EN 1998-1-1:2015). A regular structure behaves predictably during an earthquake, with well-distributed inelastic deformations and no dangerous concentration of damage. Irregular structures may experience unexpected force concentrations, excessive torsional response, or premature failure of specific storeys.

The assessment evaluates both plan regularity and elevation regularity through a series of quantitative checks on the structural geometry, mass distribution, stiffness distribution, and torsional response of the building.`,
    subsections: {
      '3.2.1': {
        title: 'Regularity in Plan',
        criteria: `For the building to be categorized as being regular in plan, it shall satisfy all the conditions listed below:

1. With respect to the lateral stiffness and mass distribution, the building structure shall be approximately symmetrical in plan with respect to the two orthogonal directions. The building satisfies condition 1 requirement due to a lack of any L, C, H, I, and X shape. It is almost symmetrical in both orthogonal directions.

2. The in-plan stiffness of the floors shall be sufficiently large in comparison with the lateral stiffness of the vertical structural elements, so that the deformation of the floor shall have a small effect on the distribution of seismic forces among the vertical elements. The horizontal displacement of the floor due to seismic action does not exceed anywhere by more than 10% of the corresponding absolute horizontal displacement that would result from a rigid diaphragm. Slab thickness is greater than 70mm. The minimum reinforcement requirement of Eurocode 2 is applied for both orthogonal directions. Therefore the structure satisfies condition 2 plan regularity criterion.

3. The slenderness (λ = Lmax/Lmin) of the building in plan shall not be higher than 4, where Lmax and Lmin are respectively the larger and smaller in-plan dimensions of the building.`,
      },
      '3.2.2': {
        title: 'Structural Eccentricity',
        formula: 'eox = Xcm − Xcr\neoy = Ycm − Ycr',
        criteria: `Structural eccentricity shall be less than 30% of the torsional radius of the building. The eccentricity represents the offset between the center of mass (where inertial forces act) and the center of rigidity (where the structure's resistance is concentrated). Large eccentricities cause additional torsional response during earthquakes.`,
      },
      '3.2.3': {
        title: 'Torsional Radius',
        formula: 'KFX = 1/UX(UL1)\nKFY = 1/UY(UL2)\nKMT = 1/RZ(UL3)\nrx = √(KMT/KFY)\nry = √(KMT/KFX)',
        criteria: `The torsional stiffness is derived from unit load (UL1, UL2, UL3) displacement results. KFX and KFY represent translational stiffness in X and Y directions respectively, while KMT represents torsional stiffness. The torsional radii rx and ry are then compared against the floor radius of gyration (ls) to check torsional regularity.`,
      },
      '3.2.4': {
        title: 'Eccentricity vs Gyration Comparison',
        formula: '|eox| ≤ 0.3 × rx\n|eoy| ≤ 0.3 × ry',
        criteria: `For this case the structure satisfies Plan regularity criterion in X-Direction and Y-Direction. The structural eccentricity must remain within 30% of the torsional radius in each direction.`,
      },
      '3.2.5': {
        title: 'Torsional Radius vs Floor Radius',
        formula: 'rx ≥ ls\nry ≥ ls',
        criteria: `Torsional radius should be greater than or equal to the radius of gyration of each floor system. If this condition is not met, the structure is torsionally irregular. Based on analysis data from Table 3.2.4, it can be concluded that the building is irregular in Plan for the Building classification.`,
      },
      '3.2.6': {
        title: 'Storey Stiffness — X Direction',
        formula: 'Ki > 0.7 × Ki+1',
        criteria: `Criteria for regularity in Elevation: Both the lateral stiffness and the mass of the individual storeys shall remain constant or reduce gradually, without abrupt changes, from the base to the top of a particular building. Each storey's X-direction stiffness must exceed 70% of the storey below it.`,
      },
      '3.2.7': {
        title: 'Storey Stiffness — Y Direction',
        formula: 'Ki > 0.7 × Ki+1',
        criteria: `Same criterion as 3.2.6 but evaluated independently in the Y direction. Do not simply duplicate X-direction values — the Y-direction stiffness has its own distribution based on the arrangement of shear walls and columns in that direction.`,
      },
      '3.2.8': {
        title: 'Mass Distribution Along Height',
        formula: 'Mi < 2 × Mi+1\nMi < 2 × Mi-1',
        criteria: `The mass of each storey should not exceed twice the mass of the storey above or below it. Abrupt mass changes create dangerous force concentrations during seismic response. Based on analysis data from Tables 3.2.6, 3.2.7, 3.2.8, it can be concluded about the building's regularity in elevation.`,
      },
    },
    charts: {
      displacement_x: 'Elastic spectrum deflection versus Design spectrum deflection shape — Along X-Direction',
      displacement_y: 'Elastic spectrum deflection versus Design spectrum deflection shape — Along Y-Direction',
      chart_note: 'Based on analysis data, the Elastic Analysis will be taken for Analysis for Damage Limitation and Stability Analysis.',
    },
  },

  '3.3': {
    title: '3.3 — Building System Classification',
    subtitle: 'Lateral Force Participation Ratio',
    background: `During seismic action, a building behaves based on the type of lateral force resisting system attached to it. Based on the mechanism through which the structure responds during seismic action, it is classified into various categories:

• Frame System: If more than 65% of the total base shear force is resisted by a frame action of primary seismic columns and beams, the structure is classified under frame system.

• Wall System: For a structure where more than 65% of the total base shear force is captured by a primary shear wall. It is further classified as coupled and uncoupled wall based on the arrangement of shear walls.

• Dual System: In this case both primary seismic frame and wall contribute to the resistance of seismic lateral force. It is classified into two based on the amount of force captured by primary seismic frame and wall:
  – Frame Equivalent Dual System: More than 50% of lateral force captured by frame action
  – Wall Equivalent Dual System: More than 50% of lateral force captured by wall action

• Torsionally Flexible System: A building whose radius of gyration of the floor mass exceeds the torsional radius in one or both of the two main directions of the building in plan.

• Inverted Pendulum System: A system with at least 50% of the total mass in the upper third of the height, or with energy dissipation at the base of a single element.`,
    criteria: `Stiffness Contribution and Lateral Force Attraction are evaluated for each storey using column forces and pier (shear wall) forces from ETABS analysis under unit load cases UL1 (X-direction) and UL2 (Y-direction).`,
  },

  '3.4': {
    title: '3.4 — Behavioral Factor (q)',
    subtitle: 'Seismic Behavior Reduction Factor',
    background: `To avoid explicit inelastic structural analysis in design, the capacity of the structure to dissipate energy, through mainly ductile behaviour of its elements and/or other mechanisms, is taken into account through the behavior factor q.

The behavior factor q is defined as: q = Fel / Fy

Where:
• Fel is the peak force that would be developed in an SDOF system if it responded to the earthquake elastically
• Fy is the yield load of the system

For the vertical component of the seismic action, a behavior factor q up to 1.5 should generally be adopted for all materials and structural systems. The adoption of values for q greater than 1.5 in the vertical direction should be justified through an appropriate analysis.`,
    formula: 'q = qo × kw × (αu/α1)',
    criteria: `qo is the basic value of the behavior factor, dependent on the type of the structural system and on its regularity in elevation.

kw is the factor reflecting the prevailing failure mode in structural systems with walls.

When the multiplication factor αu/α1 has not been evaluated through an explicit calculation, for buildings which are regular or irregular in plan, approximate values of αu/α1 may be used. For regular buildings: αu/α1 = 1.0. For irregular buildings: αu/α1 varies by system type.

ES EN 1998-1-1:2015, cl.5.2.2.2(1))`,
  },

  '4.1': {
    title: '4.1 — Base Shear Calculation',
    subtitle: 'Seismic Base Shear Force',
    background: `Eurocode 8 recommends highly idealized spectra, which follow the physical constraints and the characteristic features of actual spectra and are intended to represent average characteristics of ground motion on specific soil types.

The reference return period for the seismic action:
• No Collapse Requirement: 10% Probability of exceedance in 50 years (475-year return period)
• Damage Limitation Requirement: 10% Probability of exceedance in 10 years

Ground type based on Shear wave or SPT values.
Important class of building: Ordinary building with importance class II.

The predominant surface wave magnitude of earthquakes that contribute to the seismic hazard. The building is located in Addis Ababa, which is categorized under Seismic Zone 3.`,
    formula: `Sd(T) = ag × S × (2/3 + T/TB × (2.5/q − 2/3))  for 0 ≤ T ≤ TB
Sd(T) = ag × S × 2.5/q  for TB ≤ T ≤ TC
Sd(T) = ag × S × 2.5/q × (TC/T)  for TC ≤ T ≤ TD
Sd(T) = ag × S × 2.5/q × (TC × TD / T²)  for T > TD`,
    criteria: `Check which equation to use for X Direction Sd(T) and Y Direction Sd(T) based on the fundamental periods T1x and T1y.

Base Shear Force: Fb = Sd(T1) × W × λ / q

Where:
• Sd(T1) = design spectral acceleration at fundamental period
• W = total building weight
• λ = correction factor for modal mass participation
• q = behavior factor`,
  },

  '4.2': {
    title: '4.2 — Modal Participation',
    subtitle: 'Fundamental Periods & Mass Participation',
    background: `The first mode of vibration or fundamental period of a building is the longest natural period of vibration. For seismic design, it is essential to determine this period and verify that sufficient modal mass is captured in the analysis.

ETABS performs eigenvalue analysis to determine the natural frequencies and mode shapes of the structure. The mass participation ratio indicates how much of the total building mass is activated in each mode. A minimum of 90% cumulative mass participation is typically required in each horizontal direction.`,
  },

  '4.3': {
    title: '4.3 — Geometric Imperfections',
    subtitle: 'P-Delta Imperfection Forces',
    background: `The unfavorable effects of possible deviation in the geometry of the structure and the position of load shall be taken into account in the analysis of members and structures according to ES EN 1992.1.1:2015 Article 5.2.

Imperfections shall be taken into account in ultimate limit states in persistent and accidental design situations. Imperfections need not be considered for serviceability limit states.

Imperfections may be represented by inclination θi given by:
θi = θ0 × αh × αm

Where:
• θ0 = basic reference inclination (0.005 for frames)
• αh = height reduction factor
• αm = number of columns reduction factor`,
    formula: 'θi = θ0 × αh × αm\nHi = Ptot × θi',
    criteria: `The transversal force Hi due to geometric imperfection will be calculated for each storey as the product of the total vertical load at that storey (Ptot) and the imperfection ratio (θi).`,
  },

  '4.4': {
    title: '4.4 — Stability Analysis (P-Delta)',
    subtitle: 'Inter-Story Drift Sensitivity Coefficient',
    background: `The deflections in the members of the structure induce secondary moments due to the fact that the ends of the member may no longer be vertical in the deflected position. These secondary effects for members subjected to compression are referred to as P-Δ (global) or P-δ (local) effects.

Seismic design requires taking into account second order (P-Δ) effects in building whenever in the vertical members of any story they exceed 10% of the total first order ones. For values between 2% and 10%, second order effects may be accounted for by multiplying the effects of the analysis for first order effects by the factor 1/(1-θ).`,
    formula: 'θ = ΣPu × Δu / (Hu × hs)',
    criteria: `Where:
• ΣPu = sum of all vertical loads at the storey
• Δu = design inter-storey displacement
• Hu = total lateral force at the storey
• hs = storey height

Classification:
• θ < 0.1 → NO SWAY (second order effects can be ignored or amplified)
• θ ≥ 0.1 → SWAY (second order analysis required)
• θ ≥ 0.3 → Structure is not adequate (redesign required)`,
  },

  '4.5': {
    title: '4.5 — Damage Limitation (Drift Control)',
    subtitle: 'Inter-Storey Drift Limit Check',
    background: `Damage Limitation is related to the reduction of economic losses in frequent earthquakes, both in what concerns structural and non-structural damages. Under such events, the structure should not sustain significant damage.

Damage Limitation for various Non-Structural elements:
• For non-structural elements of brittle material attached to the structure: dr/h ≤ 0.005
• For buildings having ductile non-structural elements: dr/h ≤ 0.0075
• For buildings having non-structural elements fixed in a way so as not to interfere with structural deformation: dr/h ≤ 0.010

Where:
• dr = inter-storey drift
• h = storey height
• ν = reduction factor (dependent on importance class and return period)`,
    formula: 'ν × dr / h ≤ limit',
    criteria: `Reduction factor ν of limitation to inter-storey drift (ES EN 1998-1-1):
• Importance Class II: ν = 0.5

The check compares the reduced inter-storey drift ratio (ν × dr/h) against the limit for each storey under each load case.`,
  },

  '4.6': {
    title: '4.6 — Overturning Check',
    subtitle: 'Safety Factor Against Overturning',
    background: `Building overturning occurs when the moment caused by lateral seismic forces exceeds the stabilizing moment provided by the building's self-weight. The safety factor is defined as the ratio of the resisting (stabilizing) moment to the overturning moment.

The overturning moment is calculated as the sum of (Story Shear × Elevation) for each storey level. The resisting moment is the product of the total building weight at ground floor level and the distance from the building center of mass to the edge.`,
    formula: 'M_ot = Σ(Vi × hi)\nM_resist = W × d\nSF = M_resist / M_ot ≥ 1.5',
    criteria: `Where:
• Vi = story shear force at storey i
• hi = elevation of storey i
• W = total building weight at ground floor level
• d = distance from building center to the edge (X or Y direction)
• SF ≥ 1.5 is required for safety

The check is performed independently for both X and Y directions.`,
  },
}

export default engineeringText
