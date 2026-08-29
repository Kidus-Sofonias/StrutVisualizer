"""
Extended importer — parses additional Access tables needed for sections 3.3–4.6.
Uses pickle caching for large tables.
"""
import os
import pickle
import hashlib
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple

CACHE_DIR = Path(__file__).parent.parent.parent / "data" / "cache"


def import_extended_data(file_path: str) -> Dict:
    """Import all extended tables needed for 3.3–4.6."""
    cache_key = _cache_key(file_path) + "_extended"
    cache_file = CACHE_DIR / f"{cache_key}.pkl"

    if cache_file.exists():
        try:
            with open(cache_file, "rb") as f:
                return pickle.load(f)
        except Exception:
            pass

    from access_parser import AccessParser
    parser = AccessParser(file_path)

    data = {}

    # 1. Column Forces — aggregate V2/V3 per storey for EQX, EQY, UL1, UL2
    data["column_forces"] = _parse_column_forces(parser)

    # 2. Pier Forces (shear walls) — aggregate V2/V3 per storey
    data["pier_forces"] = _parse_pier_forces(parser)

    # 3. Displacement for CORSX1/CORSY1 load cases (for 4.4 stability)
    data["cors_displacements"] = _parse_cors_displacements(parser)

    # 4. Displacement for CORSX1DL/CORSY1DL load cases (for 4.5 drift)
    data["cors_dl_displacements"] = _parse_cors_dl_displacements(parser)

    # 5. Storey shears for CORSX1/CORSY1 (for 4.4 lateral forces)
    data["cors_shears"] = _parse_cors_shears(parser)

    # 6. Axial loads from SESMASSX/SESMASSY (for 4.3/4.4)
    data["axial_loads"] = _parse_axial_loads(parser)

    # 7. Total storey shears for EQX/EQY (for 4.6 overturning)
    data["eqx_shears"] = _parse_eqx_shears(parser)

    # Convert defaultdicts to regular dicts for pickling
    for key in data:
        if isinstance(data[key], dict):
            data[key] = {k: dict(v) if isinstance(v, defaultdict) else v for k, v in data[key].items()}

    # Save cache
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    try:
        with open(cache_file, "wb") as f:
            pickle.dump(data, f)
    except Exception as e:
        print(f"Extended cache save failed: {e}")

    return data


def _parse_column_forces(parser) -> Dict:
    """Aggregate Column Forces V2/V3 per storey for key load cases.
    
    Column Forces table has multiple Loc entries per column member
    (integration points along height: 0.0, 0.6, 1.2, ...). 
    We must only take ONE location per member to avoid double-counting.
    Use Loc=0 (bottom) for the base shear.
    """
    try:
        table = parser.parse_table("Column Forces")
        if not table:
            return {}
    except Exception:
        return {}

    stories = table.get("Story", [])
    loads = table.get("Load", [])
    locs = table.get("Loc", [])
    v2 = table.get("V2", [])
    v3 = table.get("V3", [])
    members = table.get("ColumnSection", table.get("FrameSection", []))

    target_loads = {"UL1", "UL2", "EQX", "EQY", "RSEQX", "RSEQY"}
    # Only use Loc=0 (bottom of element) to get base shear
    result = {}

    for i in range(len(stories)):
        load = loads[i] if i < len(loads) else None
        if load not in target_loads:
            continue
        
        loc = locs[i] if i < len(locs) else 0
        # Filter: only take Loc == 0 (bottom)
        if loc != 0:
            continue
        
        story = stories[i] if i < len(stories) else None
        if not story:
            continue

        if load not in result:
            result[load] = defaultdict(lambda: {"V2": 0.0, "V3": 0.0})
        result[load][story]["V2"] += v2[i] if i < len(v2) else 0
        result[load][story]["V3"] += v3[i] if i < len(v3) else 0

    return dict(result)


def _parse_pier_forces(parser) -> Dict:
    """Aggregate Pier Forces V2/V3 per storey for key load cases."""
    try:
        table = parser.parse_table("Pier Forces")
        if not table:
            return {}
    except Exception:
        return {}

    stories = table.get("Story", [])
    loads = table.get("Load", [])
    locs = table.get("Loc", [])
    v2 = table.get("V2", [])
    v3 = table.get("V3", [])

    target_loads = {"UL1", "UL2", "EQX", "EQY"}
    result = {}

    for i in range(len(stories)):
        load = loads[i] if i < len(loads) else None
        if load not in target_loads:
            continue
        loc = locs[i] if i < len(locs) else None
        if loc != "Bottom":
            continue

        story = stories[i] if i < len(stories) else None
        if not story:
            continue

        if load not in result:
            result[load] = defaultdict(lambda: {"V2": 0.0, "V3": 0.0})
        result[load][story]["V2"] += v2[i] if i < len(v2) else 0
        result[load][story]["V3"] += v3[i] if i < len(v3) else 0

    return dict(result)


def _parse_cors_displacements(parser) -> Dict:
    """Parse CORSX1/CORSY1 MAX/MIN displacements for stability analysis."""
    try:
        table = parser.parse_table("Diaphragm CM Displacements")
        if not table:
            return {}
    except Exception:
        return {}

    stories = table.get("Story", [])
    loads = table.get("Load", [])
    ux = table.get("UX", [])
    uy = table.get("UY", [])

    target_loads = {"CORSX1 MAX", "CORSX1 MIN", "CORSY1 MAX", "CORSY1 MIN"}
    result = {}

    for i in range(len(stories)):
        load = loads[i] if i < len(loads) else None
        if load not in target_loads:
            continue

        story = stories[i] if i < len(stories) else None
        if not story:
            continue

        if load not in result:
            result[load] = {}
        result[load][story] = {
            "UX": ux[i] if i < len(ux) else 0,
            "UY": uy[i] if i < len(uy) else 0,
        }

    return result


def _parse_cors_dl_displacements(parser) -> Dict:
    """Parse CORSX1DL/CORSY1DL displacements for drift control."""
    try:
        table = parser.parse_table("Diaphragm CM Displacements")
        if not table:
            return {}
    except Exception:
        return {}

    stories = table.get("Story", [])
    loads = table.get("Load", [])
    ux = table.get("UX", [])
    uy = table.get("UY", [])

    target_loads = {"CORSX1DL MAX", "CORSX1DL MIN", "CORSY1DL MAX", "CORSY1DL MIN"}
    result = {}

    for i in range(len(stories)):
        load = loads[i] if i < len(loads) else None
        if load not in target_loads:
            continue

        story = stories[i] if i < len(stories) else None
        if not story:
            continue

        if load not in result:
            result[load] = {}
        result[load][story] = {
            "UX": ux[i] if i < len(ux) else 0,
            "UY": uy[i] if i < len(uy) else 0,
        }

    return result


def _parse_cors_shears(parser) -> Dict:
    """Parse Story Shears for CORSX1/CORSY1 load cases."""
    try:
        table = parser.parse_table("Story Shears")
        if not table:
            return {}
    except Exception:
        return {}

    stories = table.get("Story", [])
    loads = table.get("Load", [])
    locs = table.get("Loc", [])
    vx = table.get("VX", [])
    vy = table.get("VY", [])

    target_loads = {"CORSX1 MAX", "CORSX1 MIN", "CORSY1 MAX", "CORSY1 MIN"}
    result = {}

    for i in range(len(stories)):
        load = loads[i] if i < len(loads) else None
        if load not in target_loads:
            continue
        loc = locs[i] if i < len(locs) else None
        if loc != "Bottom":
            continue

        story = stories[i] if i < len(stories) else None
        if not story:
            continue

        if load not in result:
            result[load] = {}
        result[load][story] = {
            "VX": vx[i] if i < len(vx) else 0,
            "VY": vy[i] if i < len(vy) else 0,
        }

    return result


def _parse_axial_loads(parser) -> Dict:
    """Parse axial loads from SESMASSX/SESMASSY load cases.
    Includes BOTH Column Forces AND Pier Forces (shear walls).
    The Excel Ptot = sum of column P + pier P at each storey.
    """
    target_loads = {"SESMASSX", "SESMASSY"}
    result = {}

    # 1. Column Forces — sum P at Loc=0 (base of columns at each storey)
    try:
        table = parser.parse_table("Column Forces")
        if table:
            stories = table.get("Story", [])
            loads = table.get("Load", [])
            locs = table.get("Loc", [])
            p = table.get("P", [])
            for i in range(len(stories)):
                load = loads[i] if i < len(loads) else None
                if load not in target_loads:
                    continue
                loc = locs[i] if i < len(locs) else None
                if loc != 0:
                    continue
                story = stories[i] if i < len(stories) else None
                if not story:
                    continue
                if load not in result:
                    result[load] = defaultdict(float)
                result[load][story] += abs(p[i]) if i < len(p) and p[i] else 0
    except Exception:
        pass

    # 2. Pier Forces — sum P at Bottom (base of shear walls at each storey)
    try:
        table = parser.parse_table("Pier Forces")
        if table:
            stories = table.get("Story", [])
            loads = table.get("Load", [])
            locs = table.get("Loc", [])
            p = table.get("P", [])
            for i in range(len(stories)):
                load = loads[i] if i < len(loads) else None
                if load not in target_loads:
                    continue
                loc = locs[i] if i < len(locs) else None
                if loc != "Bottom":
                    continue
                story = stories[i] if i < len(stories) else None
                if not story:
                    continue
                if load not in result:
                    result[load] = defaultdict(float)
                result[load][story] += abs(p[i]) if i < len(p) and p[i] else 0
    except Exception:
        pass

    return dict(result)


def _parse_eqx_shears(parser) -> Dict:
    """Parse Story Shears for EQX/EQY load cases (for overturning)."""
    try:
        table = parser.parse_table("Story Shears")
        if not table:
            return {}
    except Exception:
        return {}

    stories = table.get("Story", [])
    loads = table.get("Load", [])
    locs = table.get("Loc", [])
    vx = table.get("VX", [])
    vy = table.get("VY", [])

    target_loads = {"EQX", "EQY"}
    result = {}

    for i in range(len(stories)):
        load = loads[i] if i < len(loads) else None
        if load not in target_loads:
            continue
        loc = locs[i] if i < len(locs) else None
        if loc != "Bottom":
            continue

        story = stories[i] if i < len(stories) else None
        if not story:
            continue

        if load not in result:
            result[load] = {}
        result[load][story] = {
            "VX": vx[i] if i < len(vx) else 0,
            "VY": vy[i] if i < len(vy) else 0,
        }

    return result


def _cache_key(file_path: str) -> str:
    """Generate cache key from file content hash + modification time."""
    mtime = os.path.getmtime(file_path)
    size = os.path.getsize(file_path)
    try:
        with open(file_path, 'rb') as f:
            content_head = f.read(65536)
        content_hash = hashlib.md5(content_head).hexdigest()
    except Exception:
        content_hash = 'nocontent'
    return hashlib.md5(f"{content_hash}_{mtime}_{size}".encode()).hexdigest()
