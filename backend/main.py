"""
Structural Engineering Analysis Application — FastAPI Backend
"""
import os
import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict

# Ensure parent directory is on path for both `uvicorn main:app` and `python -m backend.main`
_backend_dir = Path(__file__).parent
_parent_dir = _backend_dir.parent
if str(_parent_dir) not in sys.path:
    sys.path.insert(0, str(_parent_dir))
if str(_backend_dir) not in sys.path:
    sys.path.insert(0, str(_backend_dir))

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Paths
ROOT = Path(__file__).parent.parent
FRONTEND = ROOT / "frontend"
DATA_DIR = ROOT / "data"
PROJECTS_DIR = DATA_DIR / "projects"
EXPORTS_DIR = DATA_DIR / "exports"
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
EXPORTS_DIR.mkdir(parents=True, exist_ok=True)

# App
app = FastAPI(title="Structural Engineering Analysis", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Static files
app.mount("/static", StaticFiles(directory=str(FRONTEND / "static")), name="static")
templates = Jinja2Templates(directory=str(FRONTEND))

# In-memory project store
projects_store: Dict[str, dict] = {}


# ─── Request Models ──────────────────────────────────────────────────────────

class ProjectConfig(BaseModel):
    project_name: str = ""
    client: str = ""
    designed_by: str = ""
    lmax: float = 33.5
    lmin: float = 22.5

class ExportRequest(BaseModel):
    project_id: str
    format: str = "excel"  # "excel" or "pdf"

class CompareRequest(BaseModel):
    project_ids: List[str]


# ─── Page Routes ─────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# ─── API Routes ──────────────────────────────────────────────────────────────

@app.get("/api/status")
async def get_status():
    return {
        "status": "running",
        "projects": len(projects_store),
        "project_ids": list(projects_store.keys()),
        "local_files": [f.name for f in PROJECTS_DIR.glob("*.mdb")] + [f.name for f in PROJECTS_DIR.glob("*.accdb")],
    }


@app.get("/api/version")
async def get_version():
    """Return application version info."""
    version_file = ROOT / "backend" / "VERSION"
    version = "1.0.0"
    build_date = ""
    git_hash = ""
    git_count = 0
    
    if version_file.exists():
        version = version_file.read_text().strip()
    
    try:
        import subprocess
        result = subprocess.run(
            ["git", "log", "-1", "--format=%H %ai"],
            capture_output=True, text=True, cwd=str(ROOT), timeout=5
        )
        if result.returncode == 0:
            parts = result.stdout.strip().split(" ", 1)
            git_hash = parts[0][:8] if parts else ""
            build_date = parts[1][:10] if len(parts) > 1 else ""
        
        result2 = subprocess.run(
            ["git", "rev-list", "--count", "HEAD"],
            capture_output=True, text=True, cwd=str(ROOT), timeout=5
        )
        if result2.returncode == 0:
            git_count = int(result2.stdout.strip())
    except Exception:
        pass
    
    return {
        "version": version,
        "build": git_count,
        "git_hash": git_hash,
        "build_date": build_date,
    }


@app.get("/api/system-stats")
async def get_system_stats():
    """Return current CPU, RAM, and disk usage for the import progress display."""
    import psutil
    try:
        cpu = psutil.cpu_percent(interval=0)
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage(str(ROOT))
        return {
            "cpu_percent": round(cpu, 1),
            "ram_percent": round(mem.percent, 1),
            "ram_used_mb": round(mem.used / 1024 / 1024),
            "ram_total_mb": round(mem.total / 1024 / 1024),
            "disk_percent": round(disk.percent, 1),
            "process_count": len(psutil.pids()),
        }
    except Exception as e:
        return {"error": str(e)}


class LoadLocalRequest(BaseModel):
    filename: str = "Bahru Model 1-3.mdb"

@app.post("/api/load-local")
async def load_local_database(req: LoadLocalRequest):
    """Load a database file that's already in data/projects/."""
    import traceback as tb
    filename = req.filename
    upload_path = PROJECTS_DIR / filename
    if not upload_path.exists():
        raise HTTPException(404, f"File not found: {filename}")
    
    # Import (uses cache)
    try:
        from importers.access_importer import import_access_database
        project, warnings = import_access_database(str(upload_path))
    except Exception as e:
        print(f"IMPORT ERROR: {tb.format_exc()}")
        raise HTTPException(500, f"Import failed: {str(e)}")
    
    # Calculate
    try:
        from calculations.engine import calculate_all
        calculate_all(project)
    except Exception as e:
        print(f"CALC ERROR: {tb.format_exc()}")
        raise HTTPException(500, f"Calculation failed: {str(e)}")
    
    # Import extended data
    try:
        from importers.extended_importer import import_extended_data
        ext_data = import_extended_data(str(upload_path))
    except Exception as e:
        ext_data = {}
        print(f"Extended import warning: {e}")
    
    # Store
    projects_store[project.project_id] = {
        "project": project,
        "file_path": str(upload_path),
        "warnings": warnings,
        "ext_data": ext_data,
    }
    
    return {
        "status": "success",
        "project_id": project.project_id,
        "project_name": project.project_name,
        "storeys_imported": len(project.storeys),
        "warnings": warnings,
        "storeys": [
            {
                "id": s.storey_id,
                "name": s.normalized_name,
                "source_name": s.source_data.source_name,
                "order": s.order,
                "elevation": s.source_data.elevation,
                "height": s.source_data.height,
                "xcm": s.source_data.xcm,
                "ycm": s.source_data.ycm,
                "xcr": s.source_data.xcr,
                "ycr": s.source_data.ycr,
                "mass": s.source_data.mass,
                "eox": s.calculations.eox,
                "eoy": s.calculations.eoy,
                "rx": s.calculations.rx,
                "ry": s.calculations.ry,
                "kx": s.calculations.kx,                "ky": s.calculations.ky,
                "ls": s.calculations.ls,
                "lmax": project.lmax,
                "lmin": project.lmin,
                "module_3_2_1_lambda": s.calculations.module_3_2_1_lambda,
                "module_3_2_1_status": s.calculations.module_3_2_1_status,
                "module_3_2_4_eox_status": s.calculations.module_3_2_4_eox_status,
                "module_3_2_4_eoy_status": s.calculations.module_3_2_4_eoy_status,
                "module_3_2_5_rx_status": s.calculations.module_3_2_5_rx_status,
                "module_3_2_5_ry_status": s.calculations.module_3_2_5_ry_status,
                "module_3_2_6_status": s.calculations.module_3_2_6_status,
                "module_3_2_7_status": s.calculations.module_3_2_7_status,
                "module_3_2_8_mass": s.calculations.module_3_2_8_mass,
                "module_3_2_8_status_upper": s.calculations.module_3_2_8_status_upper,
                "module_3_2_8_status_lower": s.calculations.module_3_2_8_status_lower,
                "classification": s.calculations.overall_classification.value,
                "failure_reasons": s.calculations.failure_reasons,
            }
            for s in project.get_storeys_sorted()
        ],
    }



@app.post("/api/upload")
async def upload_database(file: UploadFile = File(...)):
    """Upload an Access .mdb file and import data."""
    import traceback as tb
    
    suffix = Path(file.filename).suffix.lower()
    if suffix not in (".mdb", ".accdb"):
        raise HTTPException(400, f"Unsupported format: {suffix}. Use .mdb or .accdb")
    
    # Save file (streaming for large files)
    upload_path = PROJECTS_DIR / file.filename
    try:
        with open(upload_path, "wb") as f:
            while True:
                chunk = await file.read(1024 * 1024)  # 1MB chunks
                if not chunk:
                    break
                f.write(chunk)
    except Exception as e:
        raise HTTPException(500, f"File save failed: {str(e)}")
    
    # Import (uses cache if available)
    try:
        from importers.access_importer import import_access_database
        project, warnings = import_access_database(str(upload_path))
    except Exception as e:
        print(f"IMPORT ERROR: {tb.format_exc()}")
        raise HTTPException(500, f"Import failed: {str(e)}")
    
    # Calculate
    try:
        from calculations.engine import calculate_all
        calculate_all(project)
    except Exception as e:
        print(f"CALC ERROR: {tb.format_exc()}")
        raise HTTPException(500, f"Calculation failed: {str(e)}")
    
    # Import extended data
    try:
        from importers.extended_importer import import_extended_data
        ext_data = import_extended_data(str(upload_path))
    except Exception as e:
        ext_data = {}
        print(f"Extended import warning: {e}")
    
    # Store
    projects_store[project.project_id] = {
        "project": project,
        "file_path": str(upload_path),
        "warnings": warnings,
        "ext_data": ext_data,
    }
    
    return {
        "status": "success",
        "project_id": project.project_id,
        "project_name": project.project_name,
        "storeys_imported": len(project.storeys),
        "warnings": warnings,
        "storeys": [
            {
                "id": s.storey_id,
                "name": s.normalized_name,
                "source_name": s.source_data.source_name,
                "order": s.order,
                "elevation": s.source_data.elevation,
                "height": s.source_data.height,
                "xcm": s.source_data.xcm,
                "ycm": s.source_data.ycm,
                "xcr": s.source_data.xcr,
                "ycr": s.source_data.ycr,
                "mass": s.source_data.mass,
                "eox": s.calculations.eox,
                "eoy": s.calculations.eoy,
                "rx": s.calculations.rx,
                "ry": s.calculations.ry,
                "kx": s.calculations.kx,
                "ky": s.calculations.ky,
                "ls": s.calculations.ls,
                "lmax": project.lmax,
                "lmin": project.lmin,
                "module_3_2_1_lambda": s.calculations.module_3_2_1_lambda,
                "module_3_2_1_status": s.calculations.module_3_2_1_status,
                "module_3_2_4_eox_status": s.calculations.module_3_2_4_eox_status,
                "module_3_2_4_eoy_status": s.calculations.module_3_2_4_eoy_status,
                "module_3_2_5_rx_status": s.calculations.module_3_2_5_rx_status,
                "module_3_2_5_ry_status": s.calculations.module_3_2_5_ry_status,
                "module_3_2_6_status": s.calculations.module_3_2_6_status,
                "module_3_2_7_status": s.calculations.module_3_2_7_status,
                "module_3_2_8_mass": s.calculations.module_3_2_8_mass,
                "module_3_2_8_status_upper": s.calculations.module_3_2_8_status_upper,
                "module_3_2_8_status_lower": s.calculations.module_3_2_8_status_lower,
                "classification": s.calculations.overall_classification.value,
                "failure_reasons": s.calculations.failure_reasons,
            }
            for s in project.get_storeys_sorted()
        ],
    }


@app.get("/api/projects")
async def list_projects():
    """List all loaded projects, most recent first."""
    # Sort by project_id (contains timestamp) — most recent first
    sorted_projects = sorted(
        projects_store.items(),
        key=lambda item: item[0],
        reverse=True,
    )
    return {
        "projects": [
            {
                "id": pid,
                "name": data["project"].project_name,
                "storeys": len(data["project"].storeys),
                "client": data["project"].client,
                "created": pid.replace("proj_", ""),  # Extract timestamp
            }
            for pid, data in sorted_projects
        ]
    }


def _build_project_response(project):
    """Build full project response with all sections."""
    from calculations.engine_extended import (
        calculate_section_3_3, calculate_section_3_4, calculate_section_4_1,
        calculate_section_4_2, calculate_section_4_3, calculate_section_4_4,
        calculate_section_4_5, calculate_section_4_6,
    )
    ext_data = projects_store.get(project.project_id, {}).get("ext_data")
    
    sections = {}
    if ext_data:
        try:
            # 3.3 and 3.4 first
            sections["3.3"] = calculate_section_3_3(project, ext_data)
            sections["3.4"] = calculate_section_3_4(project, sections["3.3"])
            # 4.2 before 4.1 so modal data (T1x/T1y) is available for spectrum
            sections["4.2"] = calculate_section_4_2(ext_data)
            # Store 4.2 data in ext_data so 4.1 can access T1x/T1y
            ext_data["section_4_2"] = sections["4.2"]
            sections["4.1"] = calculate_section_4_1(project, sections["3.4"], ext_data)
            sections["4.3"] = calculate_section_4_3(project, ext_data)
            q_val = sections.get("3.4", {}).get("q", 2.76)
            sections["4.4"] = calculate_section_4_4(project, ext_data, q=q_val)
            sections["4.5"] = calculate_section_4_5(project, ext_data)
            sections["4.6"] = calculate_section_4_6(project, sections.get("4.1", {}), ext_data, q=q_val)
        except Exception as e:
            print(f"Section calc error: {e}")
    
    # Cache sections for export
    if project.project_id in projects_store:
        projects_store[project.project_id]["sections"] = sections
    
    return {
        "project_id": project.project_id,
        "project_name": project.project_name,
        "client": project.client,
        "designed_by": project.designed_by,
        "lmax": project.lmax,
        "lmin": project.lmin,
        "building_summary": project.building_summary,
        "total_weight_override": project.total_weight_override,
        "sections": sections,
        "storeys": [
            {
                "id": s.storey_id,
                "name": s.normalized_name,
                "source_name": s.source_data.source_name,
                "order": s.order,
                "elevation": s.source_data.elevation,
                "height": s.source_data.height,
                "xcm": s.source_data.xcm,
                "ycm": s.source_data.ycm,
                "xcr": s.source_data.xcr,
                "ycr": s.source_data.ycr,
                "mass": s.source_data.mass,
                "mmi": s.source_data.mmi,
                "ux_ul1": s.source_data.ux_ul1,
                "uy_ul2": s.source_data.uy_ul2,
                "rz_ul3": s.source_data.rz_ul3,
                "vx_ul1": s.source_data.vx_ul1,
                "vy_ul2": s.source_data.vy_ul2,
                "t_ul3": s.source_data.t_ul3,
                "vx_eqx": s.source_data.vx_eqx,
                "vy_eqy": s.source_data.vy_eqy,
                "ux_eqx": s.source_data.ux_eqx,
                "uy_eqx": s.source_data.uy_eqx,
                "ux_eqy": s.source_data.ux_eqy,
                "uy_eqy": s.source_data.uy_eqy,
                "eox": s.calculations.eox,
                "eoy": s.calculations.eoy,
                "kfx": s.calculations.kfx,
                "kfy": s.calculations.kfy,
                "kmt": s.calculations.kmt,
                "rx": s.calculations.rx,
                "ry": s.calculations.ry,
                "kx": s.calculations.kx,
                "ky": s.calculations.ky,
                "ls": s.calculations.ls,
                "lmax": project.lmax,
                "lmin": project.lmin,
                "module_3_2_1_lambda": s.calculations.module_3_2_1_lambda,
                "module_3_2_1_status": s.calculations.module_3_2_1_status,
                "module_3_2_4_eox_status": s.calculations.module_3_2_4_eox_status,
                "module_3_2_4_eoy_status": s.calculations.module_3_2_4_eoy_status,
                "module_3_2_5_rx_status": s.calculations.module_3_2_5_rx_status,
                "module_3_2_5_ry_status": s.calculations.module_3_2_5_ry_status,
                "module_3_2_6_status": s.calculations.module_3_2_6_status,
                "module_3_2_7_status": s.calculations.module_3_2_7_status,
                "module_3_2_8_mass": s.calculations.module_3_2_8_mass,
                "module_3_2_8_status_upper": s.calculations.module_3_2_8_status_upper,
                "module_3_2_8_status_lower": s.calculations.module_3_2_8_status_lower,
                "overall_classification": s.calculations.overall_classification.value,
                "failure_reasons": s.calculations.failure_reasons,
            }
            for s in project.get_storeys_sorted()
        ],
    }


@app.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    """Get detailed project data."""
    if project_id not in projects_store:
        raise HTTPException(404, "Project not found")
    
    project = projects_store[project_id]["project"]
    return _build_project_response(project)


@app.get("/api/projects/{project_id}/storeys/{storey_id}")
async def get_storey(project_id: str, storey_id: str):
    """Get detailed storey data."""
    if project_id not in projects_store:
        raise HTTPException(404, "Project not found")
    
    project = projects_store[project_id]["project"]
    for s in project.storeys:
        if s.storey_id == storey_id:
            return {
                "storey_id": s.storey_id,
                "name": s.normalized_name,
                "source_data": {
                    "xcm": s.source_data.xcm,
                    "ycm": s.source_data.ycm,
                    "xcr": s.source_data.xcr,
                    "ycr": s.source_data.ycr,
                    "ux_ul1": s.source_data.ux_ul1,
                    "uy_ul2": s.source_data.uy_ul2,
                    "rz_ul3": s.source_data.rz_ul3,
                    "vx_ul1": s.source_data.vx_ul1,
                    "vy_ul2": s.source_data.vy_ul2,
                    "mass": s.source_data.mass,
                },
                "calculations": {
                    "eox": s.calculations.eox,
                    "eoy": s.calculations.eoy,
                    "rx": s.calculations.rx,
                    "ry": s.calculations.ry,
                    "kx": s.calculations.kx,
                    "ky": s.calculations.ky,
                },
            }
    
    raise HTTPException(404, "Storey not found")


@app.post("/api/export")
async def export_report(req: ExportRequest):
    """Export project to Excel or PDF."""
    if req.project_id not in projects_store:
        raise HTTPException(404, "Project not found")
    
    project = projects_store[req.project_id]["project"]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Get sections data if available
    ext_store = projects_store.get(req.project_id, {})
    sections = ext_store.get("sections", {})
    
    try:
        if req.format == "excel":
            filename = f"report_{project.project_name}_{timestamp}.xlsx"
            output_path = EXPORTS_DIR / filename
            from exporters.excel_exporter import export_to_excel
            export_to_excel(project, str(output_path), sections=sections)
        elif req.format == "pdf":
            filename = f"report_{project.project_name}_{timestamp}.pdf"
            output_path = EXPORTS_DIR / filename
            from exporters.pdf_exporter import export_to_pdf
            export_to_pdf(project, str(output_path), sections=sections)
        else:
            raise HTTPException(400, f"Unknown format: {req.format}")
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(500, f"Export failed: {str(e)}")
    
    return FileResponse(
        path=str(output_path),
        filename=filename,
        media_type="application/octet-stream",
    )


@app.post("/api/compare")
async def compare_projects(req: CompareRequest):
    """Compare multiple projects side by side."""
    if len(req.project_ids) < 2:
        raise HTTPException(400, "Need at least 2 projects to compare")
    
    comparison = []
    for pid in req.project_ids:
        if pid not in projects_store:
            raise HTTPException(404, f"Project {pid} not found")
        
        project = projects_store[pid]["project"]
        storeys = project.get_storeys_sorted()
        
        comparison.append({
            "project_id": pid,
            "project_name": project.project_name,
            "storeys": [
                {
                    "name": s.normalized_name,
                    "eox": s.calculations.eox,
                    "eoy": s.calculations.eoy,
                    "rx": s.calculations.rx,
                    "ry": s.calculations.ry,
                    "kx": s.calculations.kx,
                    "ky": s.calculations.ky,
                    "classification": s.calculations.overall_classification.value,
                }
                for s in storeys
            ],
        })
    
    return {"comparison": comparison}


# ─── ETABS API Integration ──────────────────────────────────────────────────

class EtabsConnectRequest(BaseModel):
    model_path: str = ""
    launch_etabs: bool = False


@app.get("/api/etabs/status")
async def etabs_status():
    """Check if ETABS API is available on this machine."""
    from importers.etabs_api import check_etabs_available
    return check_etabs_available()


@app.post("/api/etabs/connect")
async def etabs_connect(req: EtabsConnectRequest):
    """Connect to ETABS and extract engineering data."""
    import traceback as tb
    from importers.etabs_api import connect_to_etabs
    from calculations.engine import calculate_all

    try:
        project, warnings = connect_to_etabs(
            model_path=req.model_path,
            launch_etabs=req.launch_etabs,
        )
    except Exception as e:
        print(f"ETABS connect error: {tb.format_exc()}")
        raise HTTPException(500, f"ETABS connection failed: {str(e)}")

    if project is None:
        raise HTTPException(500, f"ETABS connection failed: {warnings}")

    # Calculate
    try:
        calculate_all(project)
    except Exception as e:
        print(f"CALC ERROR: {tb.format_exc()}")
        raise HTTPException(500, f"Calculation failed: {str(e)}")

    # Import extended data (if available from ETABS)
    ext_data = {}
    try:
        from importers.extended_importer import import_extended_data
        if project.database_file and os.path.exists(project.database_file):
            ext_data = import_extended_data(project.database_file)
    except Exception:
        pass

    # Store
    projects_store[project.project_id] = {
        "project": project,
        "file_path": project.database_file,
        "warnings": warnings,
        "ext_data": ext_data,
    }

    return {
        "status": "success",
        "project_id": project.project_id,
        "project_name": project.project_name,
        "storeys_imported": len(project.storeys),
        "warnings": warnings,
    }


class WeightOverrideRequest(BaseModel):
    total_weight: Optional[float] = None  # kN, None = use calculated value


@app.post("/api/projects/{project_id}/weight-override")
async def set_weight_override(project_id: str, req: WeightOverrideRequest):
    """Set or clear the total building weight override for Section 4.1."""
    if project_id not in projects_store:
        raise HTTPException(404, "Project not found")
    project = projects_store[project_id]["project"]
    project.total_weight_override = req.total_weight
    # Recalculate sections with new weight
    ext_data = projects_store[project_id].get("ext_data")
    if ext_data:
        try:
            from calculations.engine_extended import (
                calculate_section_3_3, calculate_section_3_4, calculate_section_4_1,
                calculate_section_4_2, calculate_section_4_3, calculate_section_4_4,
                calculate_section_4_5, calculate_section_4_6,
            )
            sections = {}
            sections["3.3"] = calculate_section_3_3(project, ext_data)
            sections["3.4"] = calculate_section_3_4(project, sections["3.3"])
            sections["4.2"] = calculate_section_4_2(ext_data)
            ext_data["section_4_2"] = sections["4.2"]
            sections["4.1"] = calculate_section_4_1(project, sections["3.4"], ext_data)
            sections["4.3"] = calculate_section_4_3(project, ext_data)
            q_val = sections.get("3.4", {}).get("q", 2.76)
            sections["4.4"] = calculate_section_4_4(project, ext_data, q=q_val)
            sections["4.5"] = calculate_section_4_5(project, ext_data)
            sections["4.6"] = calculate_section_4_6(project, sections.get("4.1", {}), ext_data, q=q_val)
            projects_store[project_id]["sections"] = sections
        except Exception as e:
            print(f"Recalc error: {e}")
    w = project.total_weight_override
    calculated = None
    if ext_data:
        axial = ext_data.get("axial_loads", {})
        sesmassx = axial.get("SESMASSX", {})
        calculated = max(sesmassx.values()) if sesmassx else None
    return {
        "status": "success",
        "total_weight_override": w,
        "calculated_weight": calculated,
        "active_weight": w if w and w > 0 else calculated,
    }


@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: str):
    """Delete a project."""
    if project_id not in projects_store:
        raise HTTPException(404, "Project not found")
    
    del projects_store[project_id]
    return {"status": "deleted", "project_id": project_id}


# ─── Engineering Report Sections (2.4, 2.5, 3.3 enhanced) ──────────────────

class BehaviorFactorRequest(BaseModel):
    building_type: str = "Multi-Storey Multi-Bay Frame"
    regularity: str = "Irregular"
    kw: float = 1.0

class SeismicParamsRequest(BaseModel):
    city: str = "Addis Ababa"
    spectrum_basis: str = "Envelope (Workbook)"
    ground_type: str = "B"
    importance_class: str = "II — Ordinary building"

class GeometricImperfectionRequest(BaseModel):
    member_count: float = 22.0


@app.get("/api/engineering-options")
async def get_engineering_options():
    """Return all configurable engineering parameters for the UI."""
    from calculations.engineering_reports import (
        get_seismic_options, get_geometric_imperfection_options,
        BEHAVIOR_Q0_TABLE,
    )
    return {
        "seismic": get_seismic_options(),
        "geometric": get_geometric_imperfection_options(),
        "behavior": {
            "building_types": list(BEHAVIOR_Q0_TABLE.keys()),
            "regularity_types": ["Regular", "Irregular in Plan", "Irregular in Elevation", "Irregular"],
            "q0_table": BEHAVIOR_Q0_TABLE,
        },
    }


@app.get("/api/loading-schedule")
async def get_loading_schedule():
    """Return the current loading schedule (Section 2.4)."""
    from calculations.engineering_reports import calculate_loading_schedule
    return calculate_loading_schedule()


@app.get("/api/concrete-cover")
async def get_concrete_cover():
    """Return the concrete cover check (Section 2.5)."""
    from calculations.engineering_reports import calculate_concrete_cover
    return calculate_concrete_cover()


@app.get("/api/load-patterns")
async def get_load_patterns():
    """Return the ETABS load patterns (Section 2.4.2)."""
    from calculations.engineering_reports import calculate_load_patterns
    return calculate_load_patterns()


@app.get("/api/load-combinations")
async def get_load_combinations():
    """Return the ETABS load combinations (Section 2.4.3)."""
    from calculations.engineering_reports import calculate_load_combinations
    return calculate_load_combinations()


@app.post("/api/behavior-factor")
async def update_behavior_factor(req: BehaviorFactorRequest):
    """Update the behavior factor q (Section 3.4) and recalculate."""
    if not projects_store:
        raise HTTPException(400, "No project loaded")
    pid = list(projects_store.keys())[-1]
    project = projects_store[pid]["project"]
    ext_data = projects_store[pid].get("ext_data", {})

    from calculations.engineering_reports import calculate_behavior_factor
    from calculations.engine_extended import (
        calculate_section_3_3, calculate_section_3_4, calculate_section_4_1,
        calculate_section_4_2, calculate_section_4_3, calculate_section_4_4,
        calculate_section_4_5, calculate_section_4_6,
    )

    sections = {}
    sections["3.3"] = calculate_section_3_3(project, ext_data)
    sections["3.4"] = calculate_behavior_factor(
        sections["3.3"],
        building_type=req.building_type,
        regularity=req.regularity,
        kw=req.kw,
    )
    sections["4.2"] = calculate_section_4_2(ext_data)
    ext_data["section_4_2"] = sections["4.2"]
    sections["4.1"] = calculate_section_4_1(project, sections["3.4"], ext_data)
    sections["4.3"] = calculate_section_4_3(project, ext_data)
    q_val = sections.get("3.4", {}).get("q", 2.76)
    sections["4.4"] = calculate_section_4_4(project, ext_data, q=q_val)
    sections["4.5"] = calculate_section_4_5(project, ext_data)
    sections["4.6"] = calculate_section_4_6(project, sections.get("4.1", {}), ext_data, q=q_val)

    projects_store[pid]["sections"] = sections

    return {
        "status": "success",
        "q": sections["3.4"].get("q"),
        "building_type": req.building_type,
        "regularity": req.regularity,
        "kw": req.kw,
    }


@app.post("/api/seismic-parameters")
async def update_seismic_parameters(req: SeismicParamsRequest):
    """Update seismic parameters (Section 4.1) and recalculate."""
    if not projects_store:
        raise HTTPException(400, "No project loaded")
    pid = list(projects_store.keys())[-1]
    project = projects_store[pid]["project"]
    ext_data = projects_store[pid].get("ext_data", {})

    from calculations.engine_extended import (
        calculate_section_3_3, calculate_section_3_4, calculate_section_4_1,
        calculate_section_4_2, calculate_section_4_3, calculate_section_4_4,
        calculate_section_4_5, calculate_section_4_6,
    )

    sections = {}
    sections["3.3"] = calculate_section_3_3(project, ext_data)
    sections["3.4"] = calculate_section_3_4(project, sections["3.3"])
    sections["4.2"] = calculate_section_4_2(ext_data)
    ext_data["section_4_2"] = sections["4.2"]
    # Store seismic selection for 4.1
    ext_data["seismic_selection"] = {
        "city": req.city,
        "spectrum_basis": req.spectrum_basis,
        "ground_type": req.ground_type,
        "importance_class": req.importance_class,
    }
    sections["4.1"] = calculate_section_4_1(project, sections["3.4"], ext_data)
    sections["4.3"] = calculate_section_4_3(project, ext_data)
    q_val = sections.get("3.4", {}).get("q", 2.76)
    sections["4.4"] = calculate_section_4_4(project, ext_data, q=q_val)
    sections["4.5"] = calculate_section_4_5(project, ext_data)
    sections["4.6"] = calculate_section_4_6(project, sections.get("4.1", {}), ext_data, q=q_val)

    projects_store[pid]["sections"] = sections

    return {
        "status": "success",
        "city": req.city,
        "ground_type": req.ground_type,
        "weight_kN": sections["4.1"].get("total_weight_kN"),
        "Fb_x": sections["4.1"].get("Fb_x"),
        "Fb_y": sections["4.1"].get("Fb_y"),
    }


@app.post("/api/geometric-imperfection")
async def update_geometric_imperfection(req: GeometricImperfectionRequest):
    """Update geometric imperfection member count (Section 4.3) and recalculate."""
    if not projects_store:
        raise HTTPException(400, "No project loaded")
    pid = list(projects_store.keys())[-1]
    project = projects_store[pid]["project"]
    ext_data = projects_store[pid].get("ext_data", {})

    from calculations.engine_extended import (
        calculate_section_3_3, calculate_section_3_4, calculate_section_4_1,
        calculate_section_4_2, calculate_section_4_3, calculate_section_4_4,
        calculate_section_4_5, calculate_section_4_6,
    )

    sections = {}
    sections["3.3"] = calculate_section_3_3(project, ext_data)
    sections["3.4"] = calculate_section_3_4(project, sections["3.3"])
    sections["4.2"] = calculate_section_4_2(ext_data)
    ext_data["section_4_2"] = sections["4.2"]
    sections["4.1"] = calculate_section_4_1(project, sections["3.4"], ext_data)
    sections["4.3"] = calculate_section_4_3(project, ext_data)
    q_val = sections.get("3.4", {}).get("q", 2.76)
    sections["4.4"] = calculate_section_4_4(project, ext_data, q=q_val)
    sections["4.5"] = calculate_section_4_5(project, ext_data)
    sections["4.6"] = calculate_section_4_6(project, sections.get("4.1", {}), ext_data, q=q_val)

    projects_store[pid]["sections"] = sections

    return {
        "status": "success",
        "member_count": req.member_count,
        "theta_i": sections["4.3"].get("theta_i"),
    }


@app.post("/api/export-docx")
async def export_docx():
    """Export a DOCX structural design report."""
    if not projects_store:
        raise HTTPException(400, "No project loaded")
    pid = list(projects_store.keys())[-1]
    project = projects_store[pid]["project"]
    sections = projects_store[pid].get("sections", {})
    ext_data = projects_store[pid].get("ext_data", {})

    # Build project info dict for the DOCX generator
    project_info = {
        "project_name": getattr(project, 'project_name', 'Structural Project'),
        "client_name": getattr(project, 'client_name', ''),
        "location": getattr(project, 'location', 'Addis Ababa, Ethiopia'),
        "designed_by": getattr(project, 'designed_by', 'Sofonias B'),
        "description": getattr(project, 'description', ''),
    }

    # Build results dict mapping section keys for the DOCX generator
    # section_3_2 comes from the project storeys (engine.py calculate_all)
    storeys_sorted = project.get_storeys_sorted() if hasattr(project, 'get_storeys_sorted') else []
    section_3_2 = {
        "slenderness": {
            "Lmax": getattr(project, 'lmax', 0),
            "Lmin": getattr(project, 'lmin', 0),
            "slenderness_ratio": getattr(project, 'lmax', 0) / getattr(project, 'lmin', 1) if getattr(project, 'lmin', 0) > 0 else 0,
            "status": "OK",
        },
        "eccentricity": [
            {
                "name": s.normalized_name,
                "cmx": s.source_data.xcm if s.source_data else None,
                "cmy": s.source_data.ycm if s.source_data else None,
                "crx": s.source_data.xcr if s.source_data else None,
                "cry": s.source_data.ycr if s.source_data else None,
                "eox": s.calculations.eox if s.calculations else None,
                "eoy": s.calculations.eoy if s.calculations else None,
            } for s in storeys_sorted
        ],
        "torsional_radius": [
            {
                "name": s.normalized_name,
                "ul1_ux": s.source_data.ux_ul1 if s.source_data else None,
                "ul2_uy": s.source_data.uy_ul2 if s.source_data else None,
                "ul3_rz": s.source_data.rz_ul3 if s.source_data else None,
                "rx": s.calculations.rx if s.calculations else None,
                "ry": s.calculations.ry if s.calculations else None,
            } for s in storeys_sorted
        ],
        "eccentricity_comparison": [
            {
                "name": s.normalized_name,
                "eox": s.calculations.eox if s.calculations else None,
                "rx": s.calculations.rx if s.calculations else None,
                "threshold_x": round(0.3 * (s.calculations.rx or 0), 3) if s.calculations else None,
                "status_x": s.calculations.module_3_2_4_eox_status if s.calculations else "—",
                "eoy": s.calculations.eoy if s.calculations else None,
                "ry": s.calculations.ry if s.calculations else None,
                "threshold_y": round(0.3 * (s.calculations.ry or 0), 3) if s.calculations else None,
                "status_y": s.calculations.module_3_2_4_eoy_status if s.calculations else "—",
            } for s in storeys_sorted
        ],
        "floor_radius": [
            {
                "name": s.normalized_name,
                "rx": s.calculations.rx if s.calculations else None,
                "ls": s.calculations.ls if s.calculations else None,
                "status_x": s.calculations.module_3_2_5_rx_status if s.calculations else "—",
                "ry": s.calculations.ry if s.calculations else None,
                "status_y": s.calculations.module_3_2_5_ry_status if s.calculations else "—",
            } for s in storeys_sorted
        ],
        "stiffness_x": [
            {
                "name": s.normalized_name,
                "elevation": s.elevation if hasattr(s, 'elevation') else None,
                "stiffness_x": s.calculations.kx if s.calculations else None,
                "status": s.calculations.module_3_2_6_status if s.calculations else "—",
            } for s in storeys_sorted
        ],
        "stiffness_y": [
            {
                "name": s.normalized_name,
                "elevation": s.elevation if hasattr(s, 'elevation') else None,
                "stiffness_y": s.calculations.ky if s.calculations else None,
                "status": s.calculations.module_3_2_7_status if s.calculations else "—",
            } for s in storeys_sorted
        ],
        "mass_distribution": [
            {
                "name": s.normalized_name,
                "elevation": s.elevation if hasattr(s, 'elevation') else None,
                "mass": s.calculations.module_3_2_8_mass if s.calculations else None,
                "status_above": s.calculations.module_3_2_8_status_upper if s.calculations else "—",
                "status_below": s.calculations.module_3_2_8_status_lower if s.calculations else "—",
            } for s in storeys_sorted
        ],
        "displacement_x": [
            {"name": s.normalized_name, "design_disp": s.source_data.ux_eqx if s.source_data else None,
             "elastic_disp": s.source_data.ux_eqy if s.source_data else None}
            for s in storeys_sorted if s.source_data and (s.source_data.ux_eqx is not None or s.source_data.ux_eqy is not None)
        ],
        "displacement_y": [
            {"name": s.normalized_name, "design_disp": s.source_data.uy_eqx if s.source_data else None,
             "elastic_disp": s.source_data.uy_eqy if s.source_data else None}
            for s in storeys_sorted if s.source_data and (s.source_data.uy_eqx is not None or s.source_data.uy_eqy is not None)
        ],
    }

    results = {
        "section_3_2": section_3_2,
        "section_3_3": sections.get("3.3", {}),
        "section_3_4": sections.get("3.4", {}),
        "section_4_1": sections.get("4.1", {}),
        "section_4_2": sections.get("4.2", {}),
        "section_4_3": sections.get("4.3", {}),
        "section_4_4": sections.get("4.4", {}),
        "section_4_5": sections.get("4.5", {}),
        "section_4_6": sections.get("4.6", {}),
        "behavior": sections.get("3.4", {}),
    }

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{project.project_name}_Structural_Design_Report.docx"
    output_path = EXPORTS_DIR / filename

    try:
        from exporters.docx_exporter import generate_docx_report
        generate_docx_report(project_info, results, str(EXPORTS_DIR))
        # Find the actual generated file
        import glob
        docx_files = sorted(glob.glob(str(EXPORTS_DIR / "Structural_Design_Report_*.docx")), reverse=True)
        if docx_files:
            actual_path = docx_files[0]
            # Rename to the expected name
            import shutil
            shutil.move(actual_path, str(output_path))
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(500, f"DOCX export failed: {str(e)}")

    return FileResponse(
        path=str(output_path),
        filename=filename,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


# ─── Run ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
