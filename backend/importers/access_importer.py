"""
Access Database Importer — reads .mdb files and extracts engineering data.
Includes pickle caching for large databases (897MB+).
"""
import os
import pickle
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Tuple

from models.project import Project, Storey, StoreySourceData

CACHE_DIR = Path(__file__).parent.parent.parent / "data" / "cache"


def import_access_database(file_path: str) -> Tuple[Project, List[str]]:
    """
    Import engineering data from an Access .mdb file.
    Uses pickle caching for large files.
    Returns (project, list_of_warnings).
    """
    warnings = []

    try:
        from access_parser import AccessParser
    except ImportError:
        raise RuntimeError("access-parser package not installed. Run: pip install access-parser")

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Try loading from cache first
    raw_data = _load_from_cache(file_path)
    if raw_data is None:
        parser = AccessParser(file_path)
        raw_data = _parse_all_tables(parser, file_path, warnings)
        _save_to_cache(file_path, raw_data)

    # Create project
    project = Project(
        project_id=f"proj_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        project_name=Path(file_path).stem,
        database_file=file_path,
    )

    story_data = raw_data["story_data"]
    cmr_data = raw_data["cmr_data"]
    shears_data = raw_data["shears_data"]
    disp_data = raw_data["disp_data"]
    mass_data = raw_data["mass_data"]
    area_assign = raw_data.get("area_assign", {})
    drift_data = raw_data.get("drift_data", {})

    # Build storeys from all available data
    # Use CMR data as primary source (most complete), then add from others
    all_story_names = set()
    for d in [story_data, cmr_data, shears_data, disp_data, mass_data]:
        all_story_names.update(d.keys())

    # Normalize and sort storeys
    normalized = _normalize_story_names(list(all_story_names))

    # Create storey objects
    storeys = []
    for order, (norm_name, orig_names) in enumerate(normalized):
        # Try each original name to find data
        sd = StoreySourceData(
            source_name=orig_names[0] if orig_names else norm_name,
            source_table="Access Database",
            import_timestamp=datetime.now(),
        )

        # Populate from each source using any matching original name
        for orig in orig_names:
            # Story Data
            if orig in story_data and sd.elevation is None:
                sd.elevation = story_data[orig].get("Elevation")
                sd.height = story_data[orig].get("Height")
                sd.source_name = orig

            # Center Mass Rigidity
            if orig in cmr_data:
                cm = cmr_data[orig]
                sd.xcm = cm.get("XCM")
                sd.ycm = cm.get("YCM")
                sd.xcr = cm.get("XCR")
                sd.ycr = cm.get("YCR")
                if sd.mass is None:
                    sd.mass = cm.get("MassX")
                sd.source_name = orig

            # Story Shears
            if orig in shears_data:
                sh = shears_data[orig]
                sd.vx_ul1 = sh.get("UL1_VX")
                sd.vy_ul2 = sh.get("UL2_VY")
                sd.t_ul3 = sh.get("UL3_T")
                # EQX/EQY actual forces for stiffness
                sd.vx_eqx = sh.get("EQX_VX")
                sd.vy_eqy = sh.get("EQY_VY")

            # Displacements
            if orig in disp_data:
                dp = disp_data[orig]
                sd.ux_ul1 = dp.get("UL1_UX")
                sd.uy_ul1 = dp.get("UL1_UY")
                sd.rz_ul1 = dp.get("UL1_RZ")
                sd.ux_ul2 = dp.get("UL2_UX")
                sd.uy_ul2 = dp.get("UL2_UY")
                sd.rz_ul2 = dp.get("UL2_RZ")
                sd.ux_ul3 = dp.get("UL3_UX")
                sd.uy_ul3 = dp.get("UL3_UY")
                sd.rz_ul3 = dp.get("UL3_RZ")
                # EQX/EQY displacements for stiffness
                sd.ux_eqx = dp.get("EQX_UX")
                sd.uy_eqx = dp.get("EQX_UY")
                sd.ux_eqy = dp.get("EQY_UX")
                sd.uy_eqy = dp.get("EQY_UY")

            # Diaphragm Mass
            if orig in mass_data:
                md = mass_data[orig]
                if sd.mass is None:
                    sd.mass = md.get("MassX")
                sd.mmi = md.get("MMI")

            # Diaphragm Drifts (for stiffness calculation)
            if orig in drift_data.get("drift_x", {}):
                sd.drift_x_eqx = drift_data["drift_x"][orig]
            if orig in drift_data.get("drift_y", {}):
                sd.drift_y_eqy = drift_data["drift_y"][orig]

        # Skip ghost storeys (no elevation data and no mass data)
        if sd.elevation is None and sd.mass is None and sd.xcm is None:
            warnings.append(f"Skipping '{norm_name}' — no source data found")
            continue

        storey = Storey(
            storey_id=f"S{order+1:03d}",
            normalized_name=norm_name,
            building_id=project.project_id,
            order=order,
            source_data=sd,
        )
        storeys.append(storey)

    project.storeys = storeys

    # Compute ls_slab (radius of gyration from slab elements) for each storey
    for storey in storeys:
        orig = storey.source_data.source_name
        if orig in area_assign and storey.source_data.xcm is not None and storey.source_data.ycm is not None:
            storey.source_data.ls_slab = _compute_ls_from_slabs(
                area_assign[orig], storey.source_data.xcm, storey.source_data.ycm
            )
        # Also try normalized name
        if storey.source_data.ls_slab is None:
            for key in area_assign:
                if key.upper() == orig.upper() or key.upper() == storey.normalized_name.upper():
                    if storey.source_data.xcm is not None and storey.source_data.ycm is not None:
                        storey.source_data.ls_slab = _compute_ls_from_slabs(
                            area_assign[key], storey.source_data.xcm, storey.source_data.ycm
                        )
                    break

    return project, warnings


# ─── Cache helpers ───────────────────────────────────────────────────────────

def _cache_key(file_path: str) -> str:
    """Generate cache key from file content hash + modification time.
    
    Uses first 64KB of file content + mtime + size to avoid collisions
    when files with the same name but different content are uploaded.
    """
    mtime = os.path.getmtime(file_path)
    size = os.path.getsize(file_path)
    # Read first 64KB for content fingerprint (fast for large files)
    try:
        with open(file_path, 'rb') as f:
            content_head = f.read(65536)
        content_hash = hashlib.md5(content_head).hexdigest()
    except Exception:
        content_hash = 'nocontent'
    raw = f"{content_hash}_{mtime}_{size}"
    return hashlib.md5(raw.encode()).hexdigest()


def _load_from_cache(file_path: str) -> Optional[dict]:
    """Load parsed data from pickle cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = _cache_key(file_path)
    cache_file = CACHE_DIR / f"{key}.pkl"
    if cache_file.exists():
        try:
            with open(cache_file, "rb") as f:
                return pickle.load(f)
        except Exception:
            pass  # Corrupted cache, re-parse
    return None


def _save_to_cache(file_path: str, data: dict) -> None:
    """Save parsed data to pickle cache."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = _cache_key(file_path)
    cache_file = CACHE_DIR / f"{key}.pkl"
    try:
        with open(cache_file, "wb") as f:
            pickle.dump(data, f)
    except Exception:
        pass  # Cache write failed, not critical


# ─── Table parsers ───────────────────────────────────────────────────────────

def _parse_all_tables(parser, file_path: str, warnings: List[str]) -> dict:
    """Parse all needed tables from the Access database."""
    return {
        "story_data": _import_story_data(parser, warnings),
        "cmr_data": _import_center_mass_rigidity(parser, warnings),
        "shears_data": _import_story_shears(parser, warnings),
        "disp_data": _import_displacements(parser, warnings),
        "mass_data": _import_diaphragm_mass(parser, warnings),
        "area_assign": _import_area_assign(parser, warnings),
        "drift_data": _import_diaphragm_drifts(parser, warnings),
    }


def _import_story_data(parser, warnings: List[str]) -> Dict:
    """Import Story Data table."""
    data = {}
    try:
        table = parser.parse_table("Story Data")
        if not table:
            warnings.append("Story Data table not found or empty")
            return data

        stories = table.get("Story", [])
        heights = table.get("Height", [])
        elevations = table.get("Elevation", [])

        for i in range(len(stories)):
            name = stories[i] if i < len(stories) else None
            height = heights[i] if i < len(heights) else None
            if name and height and height > 0:  # Skip storeys with height=0
                data[name] = {
                    "Height": height,
                    "Elevation": elevations[i] if i < len(elevations) else None,
                }
    except Exception as e:
        warnings.append(f"Error reading Story Data: {e}")

    return data


def _import_center_mass_rigidity(parser, warnings: List[str]) -> Dict:
    """Import Center Mass Rigidity table."""
    data = {}
    try:
        table = parser.parse_table("Center Mass Rigidity")
        if not table:
            warnings.append("Center Mass Rigidity table not found or empty")
            return data

        stories = table.get("Story", [])
        xcm = table.get("XCM", [])
        ycm = table.get("YCM", [])
        xcr = table.get("XCR", [])
        ycr = table.get("YCR", [])
        massx = table.get("MassX", [])

        for i in range(len(stories)):
            name = stories[i] if i < len(stories) else None
            if name:
                data[name] = {
                    "XCM": xcm[i] if i < len(xcm) else None,
                    "YCM": ycm[i] if i < len(ycm) else None,
                    "XCR": xcr[i] if i < len(xcr) else None,
                    "YCR": ycr[i] if i < len(ycr) else None,
                    "MassX": massx[i] if i < len(massx) else None,
                }
    except Exception as e:
        warnings.append(f"Error reading Center Mass Rigidity: {e}")

    return data


def _import_story_shears(parser, warnings: List[str]) -> Dict:
    """Import Story Shears — extract UL1, UL2, UL3, EQX, EQY data."""
    data = {}
    try:
        table = parser.parse_table("Story Shears")
        if not table:
            warnings.append("Story Shears table not found or empty")
            return data

        stories = table.get("Story", [])
        loads = table.get("Load", [])
        locs = table.get("Loc", [])
        vx = table.get("VX", [])
        vy = table.get("VY", [])
        t = table.get("T", [])

        target_loads = {"UL1", "UL2", "UL3", "EQX", "EQY"}

        for i in range(len(stories)):
            story = stories[i] if i < len(stories) else None
            load = loads[i] if i < len(loads) else None
            loc = locs[i] if i < len(locs) else None

            if not story or not load or load not in target_loads:
                continue
            # Only take Bottom values for shear
            if loc != "Bottom":
                continue

            if story not in data:
                data[story] = {}

            if load == "UL1":
                data[story]["UL1_VX"] = vx[i] if i < len(vx) else None
            elif load == "UL2":
                data[story]["UL2_VY"] = vy[i] if i < len(vy) else None
            elif load == "UL3":
                data[story]["UL3_T"] = t[i] if i < len(t) else None
            elif load == "EQX":
                data[story]["EQX_VX"] = vx[i] if i < len(vx) else None
            elif load == "EQY":
                data[story]["EQY_VY"] = vy[i] if i < len(vy) else None
    except Exception as e:
        warnings.append(f"Error reading Story Shears: {e}")

    return data


def _import_displacements(parser, warnings: List[str]) -> Dict:
    """Import displacement data for UL1, UL2, UL3 load cases."""
    data = {}

    for table_name in ["Diaphragm CM Displacements", "Point Displacements"]:
        try:
            table = parser.parse_table(table_name)
            if not table:
                continue

            stories = table.get("Story", [])
            loads = table.get("Load", [])
            ux = table.get("UX", [])
            uy = table.get("UY", [])
            rz = table.get("RZ", [])

            target_loads = {"UL1", "UL2", "UL3", "EQX", "EQY"}

            for i in range(len(stories)):
                story = stories[i] if i < len(stories) else None
                load = loads[i] if i < len(loads) else None

                if not story or not load or load not in target_loads:
                    continue

                if story not in data:
                    data[story] = {}

                data[story][f"{load}_UX"] = ux[i] if i < len(ux) else None
                data[story][f"{load}_UY"] = uy[i] if i < len(uy) else None
                data[story][f"{load}_RZ"] = rz[i] if i < len(rz) else None

            if data:
                break  # Use first successful table
        except Exception as e:
            warnings.append(f"Error reading {table_name}: {e}")

    if not data:
        warnings.append("No displacement data found for UL1/UL2/UL3")

    return data


def _import_diaphragm_mass(parser, warnings: List[str]) -> Dict:
    """Import Diaphragm Mass Data table."""
    data = {}
    try:
        table = parser.parse_table("Diaphragm Mass Data")
        if not table:
            return data

        stories = table.get("Story", [])
        massx = table.get("MassX", [])
        mmi = table.get("MMI", [])

        for i in range(len(stories)):
            name = stories[i] if i < len(stories) else None
            if name:
                data[name] = {
                    "MassX": massx[i] if i < len(massx) else None,
                    "MMI": mmi[i] if i < len(mmi) else None,
                }
    except Exception as e:
        warnings.append(f"Error reading Diaphragm Mass Data: {e}")

    return data


def _import_area_assign(parser, warnings: List[str]) -> Dict:
    """Import Area Assign table for computing per-storey ls."""
    data = {}
    try:
        table = parser.parse_table("Area Assign")
        if not table:
            warnings.append("Area Assign table not found")
            return data

        stories = table.get("Story", [])
        section_types = table.get("SectionType", [])
        obj_areas = table.get("ObjectArea", [])
        polar_inertias = table.get("PolarInertia", [])
        centroid_xs = table.get("CentroidX", [])
        centroid_ys = table.get("CentroidY", [])

        for i in range(len(stories)):
            name = stories[i] if i < len(stories) else None
            stype = section_types[i] if i < len(section_types) else ""
            if not name or stype != "Slab":
                continue

            area = obj_areas[i] if i < len(obj_areas) else None
            pi_val = polar_inertias[i] if i < len(polar_inertias) else None
            cx = centroid_xs[i] if i < len(centroid_xs) else None
            cy = centroid_ys[i] if i < len(centroid_ys) else None

            if name not in data:
                data[name] = {"slab_cx": [], "slab_cy": [], "slab_area": [], "slab_pi": []}

            if area and area > 0 and pi_val is not None:
                data[name]["slab_cx"].append(cx if cx is not None else 0)
                data[name]["slab_cy"].append(cy if cy is not None else 0)
                data[name]["slab_area"].append(area)
                data[name]["slab_pi"].append(pi_val)
    except Exception as e:
        warnings.append(f"Error reading Area Assign: {e}")
    return data


def _compute_ls_from_slabs(slabs_data: dict, xcm: float, ycm: float):
    """Compute floor radius of gyration using parallel axis theorem."""
    import math
    if not slabs_data:
        return None
    if xcm is None or ycm is None:
        return None
    areas = slabs_data.get("slab_area", [])
    if not areas:
        return None
    total_ip = 0.0
    total_area = 0.0
    for j in range(len(areas)):
        a = areas[j]
        pi_val = slabs_data["slab_pi"][j] if j < len(slabs_data.get("slab_pi", [])) else 0
        cx = slabs_data["slab_cx"][j] if j < len(slabs_data.get("slab_cx", [])) else 0
        cy = slabs_data["slab_cy"][j] if j < len(slabs_data.get("slab_cy", [])) else 0
        dist_sq = (cx - xcm) ** 2 + (cy - ycm) ** 2
        total_ip += pi_val + a * dist_sq
        total_area += a
    if total_area > 0:
        return round(math.sqrt(total_ip / total_area), 3)
    return None


def _import_diaphragm_drifts(parser, warnings: List[str]) -> Dict:
    """Import Diaphragm Drifts table for stiffness calculation.
    
    Per the reference app / Excel formula:
      3.2.6: Kx = |Shear_EQX_VX| / |DriftX_EQX * Height|
      3.2.7: Ky = |Shear_EQY_VY| / |DriftY_next_row * Height|
    
    The Diaphragm Drifts table has per-storey, per-load-case drift values.
    For X direction: take the DriftX value for EQX load case.
    For Y direction: take the DriftY from the NEXT row after EQY match
    (matching the Excel's +1 row behavior).
    """
    data = {"drift_x": {}, "drift_y": {}, "all_rows": []}
    try:
        # Try both common table names
        table = parser.parse_table("Diaphragm Drifts")
        if not table:
            table = parser.parse_table("Diaphram Drift")
        if not table:
            # Try the Excel-style table name
            table = parser.parse_table("Diaphragm Drift")
        if not table:
            warnings.append("Diaphragm Drifts table not found")
            return data

        stories = table.get("Story", [])
        loads = table.get("Load", [])
        driftx = table.get("DriftX", [])
        drifty = table.get("DriftY", [])

        # Build ordered list of (story, load, driftx, drifty)
        rows = []
        for i in range(len(stories)):
            s = stories[i] if i < len(stories) else None
            lc = loads[i] if i < len(loads) else None
            dx = driftx[i] if i < len(driftx) else None
            dy = drifty[i] if i < len(drifty) else None
            if s and lc:
                rows.append((str(s).strip(), str(lc).strip().upper(), dx, dy))

        data["all_rows"] = rows

        # First-match behavior for drift_x (EQX): take first DriftX per story
        for s, lc, dx, dy in rows:
            if lc == "EQX" and s not in data["drift_x"]:
                data["drift_x"][s] = dx

        # For drift_y (EQY): use the NEXT row after first EQY match per story
        # This matches the Excel's +1 row behavior in process_327
        first_eqy_idx = {}
        for idx, (s, lc, dx, dy) in enumerate(rows):
            if lc == "EQY" and s not in first_eqy_idx:
                first_eqy_idx[s] = idx
        for s, idx in first_eqy_idx.items():
            next_idx = idx + 1
            if next_idx < len(rows):
                data["drift_y"][s] = rows[next_idx][3]  # DriftY from next row

    except Exception as e:
        warnings.append(f"Error reading Diaphragm Drifts: {e}")

    return data


# ─── Name normalization ─────────────────────────────────────────────────────

def _normalize_story_names(names: List[str]) -> List[Tuple[str, List[str]]]:
    """
    Normalize storey names and return sorted list.
    Returns: [(normalized_name, [original_names])]
    """
    import re

    mapping = {}

    for name in names:
        upper = name.strip().upper()

        # Roof patterns
        if re.match(r"^(UP\s*)?ROOF", upper):
            if "UP" in upper:
                norm = "UP ROOF FL"
            else:
                norm = "ROOF FL"
        # Ground
        elif "GROUND" in upper:
            norm = "GROUND FL"
        # Basement
        elif "BASE" in upper:
            num = re.search(r"(\d+)", upper)
            if num:
                norm = f"BASE {num.group(1)} FL"
            else:
                norm = "BASE FL"
        # Numbered floors
        else:
            num = re.search(r"(\d+)", upper)
            if num:
                n = int(num.group(1))
                suffix = "TH"
                if n == 1: suffix = "ST"
                elif n == 2: suffix = "ND"
                elif n == 3: suffix = "RD"
                norm = f"{n}{suffix} FL"
            else:
                norm = upper

        if norm not in mapping:
            mapping[norm] = []
        mapping[norm].append(name)

    # Sort by floor number (top to bottom)
    def sort_key(item):
        name = item[0]
        if "UP ROOF" in name:
            return 100
        if "ROOF" in name:
            return 99
        if "GROUND" in name:
            return 0
        if "BASE" in name:
            num = re.search(r"(\d+)", name)
            return -int(num.group(1)) if num else -1
        num = re.search(r"(\d+)", name)
        return int(num.group(1)) if num else 50

    sorted_items = sorted(mapping.items(), key=sort_key)
    return sorted_items
