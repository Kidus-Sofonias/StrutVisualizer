"""
Engineering Report Modules — Sections 2.4, 2.5, and enhanced 3.3/3.4

Ported from the engineer's V41 application:
- Section 2.4: Loading Schedule (Worksheet 2.4)
- Section 2.5: Concrete Cover Check (Worksheet 2.5)
- Enhanced 3.3: Lateral Force Classification with UL1/UL2 directional analysis
- Enhanced 3.4: Behavior factor q with editable building type / regularity / kw
"""
import math
from typing import Dict, List, Optional


# ─── Section 2.4 — Loading Schedule ─────────────────────────────────────────

DEFAULT_LOADING_SCHEDULE = [
    {
        "key": "basement",
        "floor_group": "Basement Floors and Car Parkings",
        "occupancy": "Category F",
        "plaster_mm": 15.0,
        "plaster_knm2": 0.33,
        "screed_mm": 30.0,
        "screed_knm2": 0.75,
        "partition_knm2": 0.61,
        "finish_mm": 30.0,
        "finish_knm2": 0.81,
        "total_dead_knm2": 2.50,
        "live_category": "Category D1",
        "psi_e": 0.60,
        "live_knm2": 5.00,
        "factored_live_knm2": 3.00,
    },
    {
        "key": "ground",
        "floor_group": "Ground Floor / Shopping Floor",
        "occupancy": "Category D",
        "plaster_mm": 20.0,
        "plaster_knm2": 0.44,
        "screed_mm": 30.0,
        "screed_knm2": 0.75,
        "partition_knm2": 1.50,
        "finish_mm": 30.0,
        "finish_knm2": 0.81,
        "total_dead_knm2": 3.50,
        "live_category": "Category D1",
        "psi_e": 0.60,
        "live_knm2": 4.00,
        "factored_live_knm2": 2.40,
    },
    {
        "key": "apartment",
        "floor_group": "1st up to 14th and Terrace Floor / Apartment",
        "occupancy": "Category A",
        "plaster_mm": 20.0,
        "plaster_knm2": 0.44,
        "screed_mm": 30.0,
        "screed_knm2": 0.75,
        "partition_knm2": 2.80,
        "finish_mm": 30.0,
        "finish_knm2": 0.81,
        "total_dead_knm2": 4.80,
        "live_category": "Category A",
        "psi_e": 0.15,
        "live_knm2": 2.00,
        "factored_live_knm2": 0.30,
    },
    {
        "key": "utility",
        "floor_group": "Utility and Water Tanker Floor",
        "occupancy": "Category D",
        "plaster_mm": 21.0,
        "plaster_knm2": 0.441,
        "screed_mm": 30.0,
        "screed_knm2": 0.75,
        "partition_knm2": 1.00,
        "finish_mm": 30.0,
        "finish_knm2": 0.81,
        "total_dead_knm2": 3.001,
        "live_category": "Category D1",
        "psi_e": 0.80,
        "live_knm2": 5.00,
        "factored_live_knm2": 4.00,
    },
]


def get_loading_schedule(overrides: Optional[Dict] = None) -> List[Dict]:
    """Return the loading schedule with optional user overrides."""
    schedule = [dict(row) for row in DEFAULT_LOADING_SCHEDULE]
    if overrides:
        for item in schedule:
            k = item["key"]
            if k in overrides:
                item.update(overrides[k])
        # Recalculate derived fields
        for item in schedule:
            item["total_dead_knm2"] = sum(
                float(item.get(x) or 0)
                for x in ("plaster_knm2", "screed_knm2", "partition_knm2", "finish_knm2")
            )
            item["factored_live_knm2"] = float(item.get("live_knm2") or 0) * float(item.get("psi_e") or 0)
    return schedule


def calculate_loading_schedule(schedule: Optional[List[Dict]] = None) -> Dict:
    """Section 2.4 — Complete loading schedule calculation."""
    if schedule is None:
        schedule = get_loading_schedule()

    results = []
    for item in schedule:
        dead = item.get("total_dead_knm2", 0)
        live = item.get("live_knm2", 0)
        psi_e = item.get("psi_e", 0)
        factored_live = item.get("factored_live_knm2", 0)

        # Seismic combination: 1.0*G + 1.0*ψE*Q (for seismic mass)
        seismic_dead = dead * 1.0
        seismic_live = live * psi_e
        seismic_total = seismic_dead + seismic_live

        results.append({
            **item,
            "seismic_dead_knm2": round(seismic_dead, 4),
            "seismic_live_knm2": round(seismic_live, 4),
            "seismic_total_knm2": round(seismic_total, 4),
        })

    return {
        "schedule": results,
        "code_reference": "ES EN 1991-1-1:2015 / ES EN 1998-1:2015",
        "description": (
            "Permanent, imposed and seismic actions coordinated with Worksheet 2.4. "
            "Total dead load = sum of plaster + screed + partition + finish. "
            "Factored live load = live load × ψE. "
            "Seismic mass combination: 1.0G + 1.0·ψE·Q."
        ),
    }


# ─── Section 2.5 — Concrete Cover Check ────────────────────────────────────

DEFAULT_COVER_CONFIG = {
    "rebar_arrangement": "Separated",
    "aggregate_size": "Less than 32mm",
    "structural_class": "S5",
    "super_exposure": "XC1",
    "sub_exposure": "XC2",
    "cmin_dur_super": 20.0,
    "cmin_dur_sub": 30.0,
    "cdev": 10.0,
    "super_slab": 25.0,
    "super_beam": 30.0,
    "super_column": 30.0,
    "super_shear_wall": 30.0,
    "sub_slab": 25.0,
    "sub_beam": 30.0,
    "sub_column": 40.0,
    "sub_shear_wall": 40.0,
    "foundation": 50.0,
}

# Bond requirements per Eurocode 2, Table 4.4N
BOND_TABLE = {
    "Less than 32mm": {
        "Slab": 12.0, "Beam": 20.0, "Column": 20.0,
        "Shear Wall": 20.0, "Foundation": 20.0,
    },
    "32mm or more": {
        "Slab": 17.0, "Beam": 25.0, "Column": 25.0,
        "Shear Wall": 25.0, "Foundation": 25.0,
    },
}

# Exposure class to minimum durability cover (Cmin,dur)
EXPOSURE_CMIN = {
    "XC1": 15.0, "XC2": 20.0, "XC3": 25.0, "XC4": 30.0,
    "XD1": 35.0, "XD2": 40.0, "XD3": 45.0,
    "XS1": 35.0, "XS2": 40.0, "XS3": 45.0,
    "XF1": 30.0, "XF2": 35.0, "XF3": 40.0, "XF4": 45.0,
    "XA1": 35.0, "XA2": 40.0, "XA3": 45.0,
}


def calculate_concrete_cover(config: Optional[Dict] = None) -> Dict:
    """Section 2.5 — Concrete cover check per Eurocode 2, clause 4.4.

    Cmin = max(Cmin,bond, Cmin,dur, 10mm)
    Cnom = Cmin + Cdev (construction allowance)
    """
    cfg = {**DEFAULT_COVER_CONFIG, **(config or {})}
    agg = cfg["aggregate_size"]
    bond_table = BOND_TABLE.get(agg, BOND_TABLE["Less than 32mm"])
    dur_super = cfg["cmin_dur_super"]
    dur_sub = cfg["cmin_dur_sub"]
    cdev = cfg["cdev"]

    selections = [
        ("Super-Structure", "Slab", dur_super, "super_slab"),
        ("Super-Structure", "Beam", dur_super, "super_beam"),
        ("Super-Structure", "Column", dur_super, "super_column"),
        ("Super-Structure", "Shear Wall", dur_super, "super_shear_wall"),
        ("Sub-Structure", "Slab", dur_sub, "sub_slab"),
        ("Sub-Structure", "Beam", dur_sub, "sub_beam"),
        ("Sub-Structure", "Column", dur_sub, "sub_column"),
        ("Sub-Structure", "Shear Wall", dur_sub, "sub_shear_wall"),
        ("Sub-Structure", "Foundation", dur_sub, "foundation"),
    ]

    rows = []
    for group, member, dur, key in selections:
        cmin_bond = bond_table[member]
        cmin_dur = EXPOSURE_CMIN.get(cfg.get(f"{group.lower().replace('-', '_')}_exposure" if group == "Sub-Structure" else "super_exposure", "XC1"), dur)
        # Use the provided Cmin,dur directly (already accounts for structural class)
        cmin = max(cmin_bond, dur, 10.0)
        cnom = cmin + cdev
        selected_cover = cfg.get(key)
        status = "OK" if selected_cover is not None and selected_cover >= cnom else "REVISE"

        rows.append({
            "group": group,
            "member": member,
            "cmin_bond": cmin_bond,
            "cmin_dur": dur,
            "cmin": cmin,
            "cdev": cdev,
            "cnom_calculated": cnom,
            "selected_cover": selected_cover,
            "status": status,
        })

    return {
        "config": cfg,
        "rows": rows,
        "aggregate_size": agg,
        "structural_class": cfg["structural_class"],
        "code_reference": "ES EN 1992-1-1:2015, clause 4.4",
        "description": (
            f"Concrete cover check for aggregate size {agg}, "
            f"structural class {cfg['structural_class']}, "
            f"super-structure exposure {cfg['super_exposure']}, "
            f"sub-structure exposure {cfg['sub_exposure']}. "
            f"Cmin = max(Cmin,bond, Cmin,dur, 10mm); "
            f"Cnom = Cmin + Cdev ({cdev}mm)."
        ),
    }


# ─── Enhanced Section 3.3 — Building Classification ─────────────────────────

# Behavior factor q0 table per Eurocode 8, Table 3.2
BEHAVIOR_Q0_TABLE = {
    "One Storey Frame": {
        "Regular": 3.30, "Irregular in Plan": 3.15,
        "Irregular in Elevation": 2.64, "Irregular": 2.52,
    },
    "Multi-Storey One Bay Frame": {
        "Regular": 3.60, "Irregular in Plan": 3.30,
        "Irregular in Elevation": 2.88, "Irregular": 2.64,
    },
    "Multi-Storey Multi-Bay Frame": {
        "Regular": 3.90, "Irregular in Plan": 3.45,
        "Irregular in Elevation": 3.12, "Irregular": 2.76,
    },
    "Wall Equivalent Dual System": {
        "Regular": 3.60, "Irregular in Plan": 3.30,
        "Irregular in Elevation": 2.88, "Irregular": 2.64,
    },
    "Coupled Wall System": {
        "Regular": 3.60, "Irregular in Plan": 3.30,
        "Irregular in Elevation": 2.88, "Irregular": 2.64,
    },
    "Uncoupled Wall System": {
        "Regular": 3.00, "Irregular in Plan": 3.00,
        "Irregular in Elevation": 2.40, "Irregular": 2.40,
    },
}


def calculate_behavior_factor(
    section_3_3: Dict,
    building_type: str = "Multi-Storey Multi-Bay Frame",
    regularity: str = "Irregular",
    kw: float = 1.0,
) -> Dict:
    """Section 3.4 — Behavioral factor q with editable parameters.

    q = q0 × kw
    """
    kw = max(0.5, min(1.0, kw))
    q0 = BEHAVIOR_Q0_TABLE.get(building_type, {}).get(regularity)
    q = q0 * kw if q0 is not None else None

    classification = section_3_3.get("building_classification", "")
    cx = section_3_3.get("x_direction", {}).get("column_pct", 0)
    wx = section_3_3.get("x_direction", {}).get("wall_pct", 0)
    cy = section_3_3.get("y_direction", {}).get("column_pct", 0)
    wy = section_3_3.get("y_direction", {}).get("wall_pct", 0)

    return {
        "building_type": building_type,
        "regularity": regularity,
        "ductility_class": "DCM",
        "q0": q0,
        "kw": kw,
        "q": q,
        "classification_ul1": classification,
        "classification_ul2": classification,
        "column_pct_x": round(cx * 100, 1),
        "wall_pct_x": round(wx * 100, 1),
        "column_pct_y": round(cy * 100, 1),
        "wall_pct_y": round(wy * 100, 1),
        "code_reference": "ES EN 1998-1-1:2015, cl. 5.2.2.2",
        "q0_table": BEHAVIOR_Q0_TABLE,
        "building_types": list(BEHAVIOR_Q0_TABLE.keys()),
        "regularity_types": ["Regular", "Irregular in Plan", "Irregular in Elevation", "Irregular"],
        "description": f"q = {q0} × {kw} = {q:.2f}" if q else "Select building type and regularity",
    }


# ─── Seismic Parameters (Section 4.1 helpers) ──────────────────────────────

SPECTRUM_GROUND_PARAMETERS = {
    "Type 1": {
        "A": {"S": 1.00, "TB": 0.05, "TC": 0.25, "TD": 1.20},
        "B": {"S": 1.35, "TB": 0.05, "TC": 0.25, "TD": 1.20},
        "C": {"S": 1.50, "TB": 0.10, "TC": 0.25, "TD": 1.20},
        "D": {"S": 1.80, "TB": 0.10, "TC": 0.30, "TD": 1.20},
        "E": {"S": 1.60, "TB": 0.05, "TC": 0.25, "TD": 1.20},
    },
    "Type 2": {
        "A": {"S": 1.00, "TB": 0.15, "TC": 0.40, "TD": 2.00},
        "B": {"S": 1.20, "TB": 0.15, "TC": 0.50, "TD": 2.00},
        "C": {"S": 1.15, "TB": 0.20, "TC": 0.60, "TD": 2.00},
        "D": {"S": 1.35, "TB": 0.20, "TC": 0.80, "TD": 2.00},
        "E": {"S": 1.40, "TB": 0.15, "TC": 0.50, "TD": 2.00},
    },
}

ETHIOPIA_SEISMIC_CITIES = [
    {"city": "Addis Ababa", "zone": 3, "agr": 0.10},
    {"city": "Adama", "zone": 4, "agr": 0.15},
    {"city": "Arba Minch", "zone": 3, "agr": 0.10},
    {"city": "Bishoftu", "zone": 4, "agr": 0.15},
    {"city": "Dessie", "zone": 3, "agr": 0.10},
    {"city": "Dire Dawa", "zone": 3, "agr": 0.10},
    {"city": "Hawassa", "zone": 4, "agr": 0.15},
    {"city": "Jigjiga", "zone": 3, "agr": 0.10},
    {"city": "Mekele", "zone": 4, "agr": 0.15},
    {"city": "Semera", "zone": 5, "agr": 0.20},
    {"city": "Assaita", "zone": 5, "agr": 0.20},
    {"city": "Ankober", "zone": 5, "agr": 0.20},
]


def get_seismic_options() -> Dict:
    """Return all seismic parameter options for the UI."""
    return {
        "cities": ETHIOPIA_SEISMIC_CITIES,
        "spectrum_bases": ["Envelope (Workbook)", "Type 1", "Type 2"],
        "ground_types": ["A", "B", "C", "D", "E"],
        "importance_classes": ["I", "II — Ordinary building", "III", "IV"],
        "ground_parameters": SPECTRUM_GROUND_PARAMETERS,
        "behavior_q0_table": BEHAVIOR_Q0_TABLE,
    }


def get_geometric_imperfection_options() -> Dict:
    """Return geometric imperfection parameter options."""
    return {
        "theta0": 1.0 / 200.0,
        "default_member_count": 22,
        "definitions": [
            {"parameter": "Basic inclination θ0", "discussion": "θ0 = 1/200 = 0.005"},
            {"parameter": "Number of vertical members m", "discussion": "Default m = 22. Editable per project."},
            {"parameter": "Height reduction factor αh", "discussion": "αh = 2/√l, limited to 2/3 ≤ αh ≤ 1."},
            {"parameter": "Member reduction factor αm", "discussion": "αm = √[0.5 × (1 + 1/m)]."},
            {"parameter": "Inclination θi", "discussion": "θi = θ0 × αh × αm."},
        ],
    }
