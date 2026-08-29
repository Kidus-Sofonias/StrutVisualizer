/**
 * Detailed engineering text extracted from the Excel workbook.
 * Each section contains: title, subtitle, background, criteria, formula, notes.
 * These are the actual engineering descriptions from the structural analysis.
 */

export const engineeringText = {
  '3.2': {
    title: '3.2 — Structural Regularity',
    subtitle: 'Structural Regularity Assessment per Eurocode 8',
    background: `Structural regularity is assessed according to Eurocode 8 (ES EN 1998-1-1:2015) to determine whether a building will behave in a predictable and ductile manner during seismic loading. A regular structure distributes inelastic deformations uniformly, avoiding dangerous concentrations of damage. Irregular structures may develop unexpected force concentrations, excessive torsional response, or premature failure of specific storeys.

The assessment evaluates both plan regularity and elevation regularity through a series of quantitative checks on the structural geometry, mass distribution, stiffness distribution, and torsional response of the building.

Regular buildings are permitted higher behavior factors (q), while irregular buildings may require reduction of the q-factor or additional analysis provisions. The results of this section directly affect Sections 3.3 (Building System Classification), 3.4 (Behavioral Factor), and all subsequent seismic calculations.`,
    subsections: {
      '3.2.1': {
        title: 'Regularity in Plan (Slenderness)',
        formula: 'λ = Lmax / Lmin < 4',
        criteria: `For the building to be categorized as being regular in plan, it shall satisfy all the conditions listed below:

1. With respect to the lateral stiffness and mass distribution, the building structure shall be approximately symmetrical in plan with respect to the two orthogonal directions. The building satisfies condition 1 requirement due to a lack of any L, C, H, I, and X shape. It is almost symmetrical in both orthogonal directions.

2. The in-plan stiffness of the floors shall be sufficiently large in comparison with the lateral stiffness of the vertical structural elements, so that the deformation of the floor shall have a small effect on the distribution of seismic forces among the vertical elements. The horizontal displacement of the floor due to seismic action does not exceed anywhere by more than 10% of the corresponding absolute horizontal displacement that would result from a rigid diaphragm. Slab thickness is greater than 70mm. The minimum reinforcement requirement of Eurocode 2 is applied for both orthogonal directions. Therefore the structure satisfies condition 2 plan regularity criterion.

3. The slenderness (λ = Lmax/Lmin) of the building in plan shall not be higher than 4, where Lmax and Lmin are respectively the larger and smaller in-plan dimensions of the building.`,
      },
      '3.2.2': {
        title: 'Structural Eccentricity',
        formula: 'eox = Xcm − Xcr\neoy = Ycm − Ycr',
        criteria: `Structural eccentricity is the distance between the center of mass (CM) and the center of rigidity (CR) of each storey. The center of mass is the point where the total mass of the storey is considered to act, and it determines where inertial forces are generated during an earthquake. The center of rigidity is the point through which the resultant of the storey's lateral stiffness acts.

When these two points do not coincide, the eccentricity causes additional torsional (twisting) response during seismic loading. The larger the eccentricity, the greater the torsional demands on the structural elements.

According to ES EN 1998-1-1, for a building to be considered regular in plan, the structural eccentricity in both X and Y directions must remain less than 30% of the torsional radius of the building in the respective direction.

The eccentricity values are computed storey-by-storey from the ETABS analysis results. The center of mass coordinates (Xcm, Ycm) and center of rigidity coordinates (Xcr, Ycr) are imported from the Access database (ETABS model data).`,
      },
      '3.2.3': {
        title: 'Torsional Radius',
        formula: 'KFX = 1/UX(UL1)\nKFY = 1/UY(UL2)\nKMT = 1/RZ(UL3)\nrx = √(KMT/KFY)\nry = √(KMT/KFX)',
        criteria: `The torsional stiffness and torsional radii are derived from the structural response under unit load cases (UL1, UL2, UL3) applied through ETABS.

UL1 = Unit load in X-direction (produces UX displacement)
UL2 = Unit load in Y-direction (produces UY displacement)
UL3 = Unit torsional moment (produces RZ rotation)

The translational stiffness in X is: KFX = 1/UX(UL1)
The translational stiffness in Y is: KFY = 1/UY(UL2)
The torsional stiffness is: KMT = 1/RZ(UL3)

The torsional radius in X is: rx = √(KMT/KFY)
The torsional radius in Y is: ry = √(KMT/KFX)

These radii represent the distance from the center of rigidity at which a lateral force would produce the same torsional response as the actual eccentric loading. A larger torsional radius means the structure is more resistant to torsional effects.

The torsional radii are then compared against the floor radius of gyration (ls) to determine torsional regularity (Section 3.2.5) and against the eccentricity to determine whether eccentricity limits are satisfied (Section 3.2.4).`,
      },
      '3.2.4': {
        title: 'Structural Eccentricity and Radius of Gyration Comparison for the Building',
        formula: '|eox| ≤ 0.3 × rx\n|eoy| ≤ 0.3 × ry',
        criteria: `This check verifies that the structural eccentricity in each direction does not exceed 30% of the torsional radius in that direction.

For X-direction: |eox| = |Xcm − Xcr| must be ≤ 0.3 × rx
For Y-direction: |eoy| = |Ycm − Ycr| must be ≤ 0.3 × ry

If this condition is satisfied in both directions, the building is considered regular in plan with respect to torsional eccentricity. This is per ES EN 1998-1-1, Annex E, Table E.1.

The check is performed independently for each storey. A single storey failure means the entire building is classified as irregular in plan for this criterion.

The limit of 0.3 is a Eurocode provision that ensures the eccentricity-induced torsional effects remain within acceptable bounds relative to the torsional stiffness of the structure.`,
      },
      '3.2.5': {
        title: 'Torsional Radius and Radius of Gyration Comparison for the Building',
        formula: 'rx ≥ ls\nry ≥ ls',
        criteria: `The torsional radius (rx, ry) must be greater than or equal to the radius of gyration of the floor system (ls) in each direction.

The radius of gyration ls is computed from the floor system geometry using the parallel axis theorem:

ls = √(Σ(Ipolar + Area × ((Cx − Xcm)² + (Cy − Ycm)²)) / Σ(Area))

Where:
- Ipolar = polar moment of inertia of each slab element about its own centroid
- Area = area of each slab element
- Cx, Cy = centroid coordinates of each slab element
- Xcm, Ycm = center of mass coordinates of the storey

This calculation uses the Area Assignments Summary table from the Access database, which contains the slab element properties (area, centroid, polar inertia) for each storey.

When rx < ls or ry < ls, the structure is torsionally flexible — meaning the floor mass has a larger radius than the torsional resistance can control. This leads to amplified torsional response during earthquakes.

If this condition fails in any storey in either direction, the building is classified as torsionally irregular per ES EN 1998-1-1.`,
      },
      '3.2.6': {
        title: 'Storey Stiffness along X Direction of the Building',
        formula: 'Ki = |VXi| / (|DriftXi| × Hi)\nKi > 0.7 × Ki+1',
        criteria: `Storey stiffness in the X direction is calculated as the ratio of the story shear force to the inter-storey drift multiplied by the storey height:

Kx = |Shear_EQX| / (|DriftX_EQX| × Height)

Where:
- Shear_EQX = story shear force under EQX load case (from Story Shears table in Access DB)
- DriftX_EQX = inter-storey drift in X under EQX load case (from Diaphragm Drifts table in Access DB)
- Height = storey height in meters

The Diaphragm Drifts table from the ETABS analysis provides the drift values directly. The drift represents the relative horizontal displacement between consecutive storeys.

For regularity in elevation, both the lateral stiffness and the mass of the individual storeys shall remain constant or reduce gradually, without abrupt changes, from the base to the top of the building (ES EN 1998-1-1, §4.3.3(2)).

The specific criterion is: Ki > 0.7 × Ki+1
Where Ki is the stiffness of storey i and Ki+1 is the stiffness of the storey above it.

If this condition is violated for any storey pair, the building is classified as irregular in elevation. This irregularity may require additional provisions or reduction of the behavior factor.

Storey order in this analysis: ROOF FL (top) → 1ST FL (bottom), excluding the highest top storey (UP ROOF FL) and BASE level.`,
      },
      '3.2.7': {
        title: 'Storey Stiffness along Y Direction of the Building',
        formula: 'Ki = |VYi| / (|DriftYi| × Hi)\nKi > 0.7 × Ki+1',
        criteria: `Same criterion as 3.2.6 but evaluated independently in the Y direction. The Y-direction stiffness has its own distribution based on the arrangement of shear walls and columns in that direction.

Kx = |Shear_EQY| / (|DriftY_EQY| × Height)

Where:
- Shear_EQY = story shear force under EQY load case
- DriftY_EQY = inter-storey drift in Y under EQY load case
- Height = storey height

Note: The Y-direction may use the NEXT ROW in the Diaphragm Drifts table after the EQY match, due to how ETABS organizes the drift data (DriftX and DriftY appear in separate rows for each load case).

The distribution of lateral stiffness in the Y direction may differ significantly from the X direction because the arrangement and sizes of shear walls and columns are not necessarily symmetric. Therefore, each storey must be independently checked.

A building may satisfy the X-direction stiffness criterion but fail the Y-direction criterion, or vice versa.`,
      },
      '3.2.8': {
        title: 'Mass Distribution along Height of the Building',
        formula: 'Mi < 2 × Mi+1\nMi < 2 × Mi-1',
        criteria: `The mass of each storey should not exceed twice the mass of the storey above (Mi+1) or twice the mass of the storey below (Mi-1).

This criterion ensures that mass distribution along the building height is relatively uniform, without abrupt changes that could create dangerous force concentrations during seismic response.

Mass values are imported from the ETABS Diaphragm Mass data in the Access database. The mass represents the total seismic mass at each storey level, including structural and non-structural contributions.

The check is performed for each storey pair:
1. Mi < 2 × Mi+1: Mass at current storey should not be more than double the storey above
2. Mi < 2 × Mi-1: Mass at current storey should not be more than double the storey below

Based on analysis data from Tables 3.2.6, 3.2.7, and 3.2.8, a conclusion can be drawn about the building's regularity in elevation. If all three criteria are satisfied, the building is regular in elevation.`,
      },
    },
    charts: {
      stiffness_note: 'The stiffness distribution charts show the storey stiffness along the height of the building. A smooth, gradually increasing curve from top to bottom indicates regular stiffness distribution. Sudden drops or spikes indicate irregularity.',
      displacement_x_title: 'Elastic spectrum deflection versus Design spectrum deflection — Along X-Direction',
      displacement_y_title: 'Elastic spectrum deflection versus Design spectrum deflection — Along Y-Direction',
      displacement_note: 'Based on analysis data, the Elastic Analysis will be taken for Analysis for Damage Limitation and Stability Analysis.',
    },
  },

  '3.3': {
    title: '3.3 — Building System Classification',
    subtitle: 'Lateral Force Participation Ratio',
    background: `During seismic action, a building responds based on the type of lateral force resisting system (LFRS) incorporated into it. The classification of the building system is essential because it determines the applicable behavior factor (q), the redundancy factor, and the design detailing requirements according to ES EN 1998-1-1.

The lateral force resisting system is classified by evaluating the proportion of total base shear resisted by different structural elements (columns, beams, shear walls) under the applicable unit load cases. ETABS provides the element-level forces under UL1 (X-direction unit load) and UL2 (Y-direction unit load), which are used to determine the participation of each element type.

The building system classification directly affects Section 3.4 (Behavioral Factor q), which in turn affects Section 4.1 (Base Shear) and all subsequent calculations. An incorrect classification propagates errors throughout the entire analysis.

Building System Types per ES EN 1998-1-1:

• Frame System: >65% of total base shear resisted by frame action (columns + beams)
• Wall System: >65% of total base shear resisted by shear walls
  – Uncoupled Wall: walls act independently
  – Coupled Wall: walls connected by coupling beams
• Dual System: Both frame and wall contribute significantly
  – Frame Equivalent Dual: >50% by frame
  – Wall Equivalent Dual: >50% by wall
• Torsionally Flexible System: floor radius of gyration exceeds torsional radius in one or both directions (from Section 3.2.5)
• Inverted Pendulum System: ≥50% of mass in upper third of height`,
    criteria: `The stiffness contribution and lateral force attraction are evaluated for each storey using column forces and pier (shear wall) forces from ETABS analysis under unit load cases UL1 (X-direction) and UL2 (Y-direction).

For each storey:
- Column lateral force = sum of all column shears in the direction of interest
- Wall lateral force = sum of all pier shears in the direction of interest
- Total lateral force = Column + Wall
- Column % = Column / Total × 100
- Wall % = Wall / Total × 100

The building classification is determined by the storey with the highest base shear contribution ratio.`,
  },

  '3.4': {
    title: '3.4 — Behavioral Factor (q)',
    subtitle: 'Seismic Behavior Reduction Factor',
    background: `To avoid the need for explicit inelastic structural analysis in design, Eurocode 8 accounts for the energy dissipation capacity of the structure through the behavior factor q. The behavior factor is defined as the ratio of the force that would develop in the structure if it remained elastic to the yield strength of the actual ductile structure:

q = Fel / Fy

Where:
• Fel = peak force that would develop in an SDOF system responding elastically to the design earthquake
• Fy = yield load of the system

A higher q-factor allows the engineer to design for lower forces, relying on the structure's ductile deformation capacity. However, higher q-values impose stricter detailing requirements to ensure the assumed ductility can be achieved.

The behavior factor depends on:
1. The structural system type (from Section 3.3)
2. Regularity in elevation (from Section 3.2)
3. The material (concrete, steel, etc.)
4. The ductility class (DCH, DCM, DCL)

For the vertical component of seismic action, q_v ≤ 1.5 should generally be adopted regardless of material or system type.

ES EN 1998-1-1:2015, Table 5.1 provides the basic q₀ values for different structural systems.`,
    formula: 'q = q₀ × kw × (αu/α1)',
    criteria: `q₀ = basic value of the behavior factor, dependent on:
  - Structural system type (frame, wall, dual, etc.)
  - Regularity in elevation (regular or irregular)
  - Ductility class

kw = factor reflecting the prevailing failure mode in structural systems with walls
  - kw = 1.0 for frame-equivalent systems
  - kw = 1.0 for wall-equivalent systems with predominantly flexural behavior
  - kw = 0.75 for wall-equivalent systems with predominantly shear behavior

αu/α1 = multiplication factor for overstrength
  - α1 = ratio of moment resistance at the base to the applied moment at the base
  - αu = ratio of total ultimate shear resistance to total applied shear at the storey level
  - When not evaluated through explicit calculation:
    • For regular buildings: αu/α1 = 1.0
    • For irregular buildings: varies by system type (Table 5.1 of EC8)

The final q-factor is the lesser of the X-direction and Y-direction values (or the value governing the most critical direction).

ES EN 1998-1-1:2015, cl.5.2.2.2(1))`,
  },

  '4.1': {
    title: '4.1 — Base Shear Calculation',
    subtitle: 'Seismic Base Shear Force (Fb)',
    background: `Eurocode 8 defines the design elastic response spectrum as a function of the natural vibration period T of the structure. The spectrum is highly idealized, following the physical constraints and characteristic features of actual response spectra, and represents average characteristics of ground motion on specific soil types.

The design spectral acceleration Sd(T) depends on:
• ag = peak ground acceleration on type A ground
• S = soil factor (depends on ground type)
• TB, TC, TD = corner periods of the spectrum
• q = behavior factor (from Section 3.4)

Reference return period for seismic action:
• No Collapse Requirement: 475-year return period (10% probability of exceedance in 50 years)
• Damage Limitation Requirement: varies by importance class

Ground type is determined from Shear wave velocity or SPT N-values from site investigation.
The building importance class is II (ordinary buildings).
The building is located in Addis Ababa, categorized under Seismic Zone 3.

The response spectrum has four branches:
1. Plateau region (TB ≤ T ≤ TC): Sd(T) = ag × S × 2.5/q
2. Constant velocity region (TC ≤ T ≤ TD): Sd(T) decreases as 1/T
3. Constant displacement region (T > TD): Sd(T) decreases as 1/T²
4. Initial branch (T < TB): Sd(T) increases linearly from 2/3 × ag × S`,
    formula: `Sd(T) = ag × S × (2/3 + T/TB × (2.5/q − 2/3))  for 0 ≤ T ≤ TB
Sd(T) = ag × S × 2.5/q  for TB ≤ T ≤ TC
Sd(T) = ag × S × 2.5/q × (TC/T)  for TC ≤ T ≤ TD
Sd(T) = ag × S × 2.5/q × (TC × TD / T²)  for T > TD`,
    criteria: `Step 1: Determine which branch of the spectrum applies for X Direction and Y Direction based on the fundamental periods T1x and T1y.

Step 2: Calculate Sd(T1x) and Sd(T1y) using the appropriate spectral equation.

Step 3: Calculate the Base Shear Force:
Fb = Sd(T1) × W × λ / q

Where:
• Sd(T1) = design spectral acceleration at fundamental period
• W = total building weight (sum of storey masses × g)
• λ = correction factor for modal mass participation
  – λ = 0.85 if ≥90% mass participation captured
  – λ = 1.0 otherwise
• q = behavior factor from Section 3.4

Step 4: Apply lower bound check:
The base shear shall not be less than: Fb,min = 0.1 × ag × W (or specific code provision)

The design base shear is the governing (larger) value between the spectral calculation and the lower bound.

Note: The X-direction and Y-direction base shears are calculated independently using their respective fundamental periods and modal participation ratios.`,
  },

  '4.2': {
    title: '4.2 — Modal Participation',
    subtitle: 'Fundamental Periods & Mass Participation',
    background: `Dynamic analysis of a structure involves determining its natural frequencies (or equivalently, natural periods) and mode shapes through eigenvalue analysis. Each mode of vibration represents a characteristic pattern of deformation that the structure adopts when freely vibrating.

ETABS performs eigenvalue analysis to determine the natural frequencies and mode shapes of the structure. The mass participation ratio indicates how much of the total building mass is activated (participates) in each mode.

The fundamental period (T1) is the longest natural period of vibration and typically corresponds to the mode with the highest mass participation. For seismic design, T1x and T1y are the fundamental periods in the X and Y directions respectively.

A minimum of 90% cumulative mass participation is typically required in each horizontal direction to ensure that the analysis captures sufficient dynamic response. ETABS typically analyzes 50 or more modes to achieve this requirement.

The fundamental periods directly affect:
• The design spectral acceleration (Section 4.1)
• The base shear force calculation
• The modal load distribution for response spectrum analysis

Higher modes with significant mass participation may also affect:
• Inter-storey drift patterns
• P-delta sensitivity
• Force distribution in non-regular structures

The mass participation data is imported from the ETABS modal analysis results stored in the Access database.`,
    criteria: `ETABS modal analysis results include for each mode:
- Mode number
- Natural period (T)
- Mass participation in X (UX), Y (UY), and rotation (RZ)
- Cumulative mass participation (ΣUX, ΣUY)

The fundamental period T1 is identified as the mode with the highest mass participation in each direction.

Key acceptance criteria:
- Cumulative mass participation ≥ 90% in each horizontal direction
- At least one mode with mass participation > 50% in each direction
- Period ratio T1y/T1x typically should be > 0.8 for regular structures (to avoid torsional coupling)`,
  },

  '4.3': {
    title: '4.3 — Geometric Imperfections',
    subtitle: 'P-Delta Imperfection Forces',
    background: `Geometric imperfections account for the unfavorable effects of possible deviations in the geometry of the structure and the position of loads. According to ES EN 1992.1.1:2015, Article 5.2, imperfections shall be taken into account in ultimate limit states in persistent and accidental design situations.

Imperfections need not be considered for serviceability limit states.

Imperfections may be represented by an inclination (notional slope) θi applied to the vertical load-bearing elements. This inclination produces equivalent horizontal forces that simulate the effect of geometric imperfections.

The basic reference inclination depends on the structural system:
• θ₀ = 0.005 for frames (beam-slab structures)
• θ₀ = 0.002 for braced structures

The inclination is modified by reduction factors:

αh = height reduction factor = 1/√(H) where H is the building height in meters (αh ≤ 1.0)
αm = number of columns reduction factor = 0.5 × (1 + 1/n) where n = number of columns at storey level (αm ≤ 1.0)

The imperfection ratio is: θi = θ₀ × αh × αm

The equivalent horizontal force at each storey is: Hi = Ptot × θi

Where Ptot is the total cumulative vertical load at that storey level (from top to that storey).

These forces are applied in both X and Y directions independently. The direction yielding the more critical result governs the design.`,
    formula: 'θi = θ₀ × αh × αm\nHi = Ptot × θi',
    criteria: `Where:
• θ₀ = basic reference inclination (0.005 for frames)
• αh = 1/√H ≤ 1.0 (H in meters)
• αm = 0.5 × (1 + 1/n) ≤ 1.0 (n = number of columns at storey)
• Ptot = total vertical load at storey i (sum of all masses from top to storey i)
• Hi = equivalent horizontal imperfection force at storey i

The transversal forces Hi are computed storey-by-storey and used in the stability analysis (Section 4.4) and overturning check (Section 4.6).

ES EN 1992.1.1:2015, Article 5.2`,
  },

  '4.4': {
    title: '4.4 — Stability Analysis (P-Delta)',
    subtitle: 'Inter-Story Drift Sensitivity Coefficient',
    background: `Second-order (P-Δ) effects arise when the deformations in the structure cause additional moments due to the vertical loads acting on the displaced geometry. These secondary effects can significantly amplify the forces and displacements, particularly in flexible or tall structures.

The inter-story drift sensitivity coefficient θ quantifies the severity of second-order effects:

θ = ΣPu × Δu / (Hu × hs)

Where:
• ΣPu = sum of all vertical loads at the storey level
• Δu = design inter-storey displacement under seismic loading
• Hu = total lateral force at the storey
• hs = storey height

The coefficient is computed for each storey under each load case (EQX, EQY, UL1, UL2, UL3) and each direction.

Classification per ES EN 1998-1-1:
• θ < 0.10 → NO SWAY: Second-order effects can be ignored (or accounted for by multiplying first-order effects by 1/(1-θ) for 0.02 < θ < 0.10)
• θ ≥ 0.10 → SWAY: Second-order analysis is required
• θ ≥ 0.30 → Structure is inadequate: Redesign is required

For most well-designed buildings, θ should be well below 0.10 in all load cases. Values approaching 0.10 indicate the structure is near the limit of first-order analysis applicability.

The maximum θ value across all storeys and load cases governs the overall classification.`,
    formula: 'θ = ΣPu × Δu / (Hu × hs)',
    criteria: `Where:
• ΣPu = cumulative vertical load at storey level (kN)
• Δu = design inter-storey displacement (m)
• Hu = total lateral force at storey (kN)
• hs = storey height (m)

Classification:
• θ < 0.10 → NO SWAY (second order effects negligible or amplifiable)
• 0.10 ≤ θ < 0.30 → SWAY (second order analysis required, multiply by 1/(1-θ))
• θ ≥ 0.30 → Structure not adequate (redesign required)

The check is performed for each load case in both X and Y directions. The governing (maximum) θ value determines the overall stability classification.

ES EN 1998-1-1:2015, §4.4.3.2`,
  },

  '4.5': {
    title: '4.5 — Storey Drift Control',
    subtitle: 'Damage Limitation Check',
    background: `Damage limitation is related to the reduction of economic losses during frequent earthquakes, addressing both structural and non-structural damage. Under such events, the structure should not sustain significant damage, and non-structural elements should remain functional.

The inter-storey drift limit check ensures that the relative displacement between consecutive storeys, when reduced by the importance factor ν, does not exceed the code-specified limit.

The inter-storey drift dr is defined as the difference in lateral displacement between consecutive storeys:
dr = Ui - Ui-1

Where Ui is the lateral displacement at storey i.

The drift ratio is: dr/h where h is the storey height.

The reduced drift ratio is: ν × dr/h

Different limits apply depending on the type of non-structural elements:
• Brittle non-structural elements attached to the structure: ν × dr/h ≤ 0.005
• Ductile non-structural elements: ν × dr/h ≤ 0.0075
• Non-structural elements not interfering with structural deformation: ν × dr/h ≤ 0.010

The reduction factor ν depends on the importance class and the return period:
• Importance Class II (ordinary buildings): ν = 0.5 for 475-year return period

The check is performed for each storey under each load case. The maximum drift ratio across all storeys and load cases determines the governing condition.`,
    formula: 'ν × dr / h ≤ limit',
    criteria: `Reduction factor ν (ES EN 1998-1-1, Table 4.3):
• Importance Class I: ν = 0.4
• Importance Class II: ν = 0.5
• Importance Class III: ν = 0.7
• Importance Class IV: ν = 1.0

Drift limits (ES EN 1998-1-1, §4.4.3.3):
• For buildings having non-structural elements of brittle material: dr/h ≤ 0.005
• For buildings having ductile non-structural elements: dr/h ≤ 0.0075
• For buildings with non-structural elements not interfering: dr/h ≤ 0.010

The limit used in this analysis corresponds to the applicable limit for the building type.

ES EN 1998-1-1:2015, §4.4.3.3`,
  },

  '4.6': {
    title: '4.6 — Overturning Check',
    subtitle: 'Safety Factor Against Overturning',
    background: `Building overturning occurs when the moment caused by lateral seismic forces exceeds the stabilizing (resisting) moment provided by the building's self-weight. The check ensures that the building has adequate resistance against rigid-body overturning about its base edges.

The overturning moment is calculated as the sum of (story shear × elevation) for each storey level above the ground:

M_ot = Σ(Vi × hi)

Where:
• Vi = story shear force at storey i
• hi = elevation of storey i above ground level

The resisting moment is the product of the total building weight at the ground floor level and the distance from the building center of mass to the edge (in the direction of overturning):

M_resist = W × d

Where:
• W = total building weight (sum of all storey weights)
• d = distance from center of mass to the nearest edge in the direction of interest

For X-direction overturning: d = min(Xcm, Lx - Xcm)
For Y-direction overturning: d = min(Ycm, Ly - Ycm)

Where Lx, Ly are the plan dimensions of the building.

The safety factor is: SF = M_resist / M_ot ≥ 1.5

The check is performed independently for both X and Y directions. The direction with the lower safety factor governs the overall check.

The story shears are imported from the Story Shears table in the Access database, and the center of mass coordinates come from the ETABS analysis results.`,
    formula: 'M_ot = Σ(Vi × hi)\nM_resist = W × d\nSF = M_resist / M_ot ≥ 1.5',
    criteria: `Where:
• Vi = story shear force at storey i (kN) — from Story Shears table
• hi = elevation of storey i above ground (m)
• W = total building weight at ground floor level (kN)
• d = lever arm = distance from CM to nearest edge in direction of check (m)

Required: SF ≥ 1.5 for both X and Y directions

The safety factor accounts for:
• Uncertainties in seismic hazard
• Modeling approximations
• Potential for torsional amplification
• Variations in mass distribution

ES EN 1998-1-1:2015, §4.4.3.4`,
  },
}

export default engineeringText
