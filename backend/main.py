"""
Structural Engineering Analysis Application — FastAPI Backend
"""
import os
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict

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
    }


@app.post("/api/upload")
async def upload_database(file: UploadFile = File(...)):
    """Upload an Access .mdb file and import data."""
    suffix = Path(file.filename).suffix.lower()
    if suffix not in (".mdb", ".accdb"):
        raise HTTPException(400, f"Unsupported format: {suffix}. Use .mdb or .accdb")
    
    # Save file
    upload_path = PROJECTS_DIR / file.filename
    with open(upload_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Import
    try:
        from .importers.access_importer import import_access_database
        project, warnings = import_access_database(str(upload_path))
    except Exception as e:
        raise HTTPException(500, f"Import failed: {str(e)}")
    
    # Calculate
    try:
        from .calculations.engine import calculate_all
        calculate_all(project)
    except Exception as e:
        raise HTTPException(500, f"Calculation failed: {str(e)}")
    
    # Store
    projects_store[project.project_id] = {
        "project": project,
        "file_path": str(upload_path),
        "warnings": warnings,
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
                "classification": s.calculations.overall_classification.value,
            }
            for s in project.get_storeys_sorted()
        ],
    }


@app.get("/api/projects")
async def list_projects():
    """List all loaded projects."""
    return {
        "projects": [
            {
                "id": pid,
                "name": data["project"].project_name,
                "storeys": len(data["project"].storeys),
                "client": data["project"].client,
            }
            for pid, data in projects_store.items()
        ]
    }


@app.get("/api/projects/{project_id}")
async def get_project(project_id: str):
    """Get detailed project data."""
    if project_id not in projects_store:
        raise HTTPException(404, "Project not found")
    
    project = projects_store[project_id]["project"]
    return {
        "project_id": project.project_id,
        "project_name": project.project_name,
        "client": project.client,
        "designed_by": project.designed_by,
        "lmax": project.lmax,
        "lmin": project.lmin,
        "building_summary": project.building_summary,
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
    
    if req.format == "excel":
        filename = f"report_{project.project_name}_{timestamp}.xlsx"
        output_path = EXPORTS_DIR / filename
        from .exporters.excel_exporter import export_to_excel
        export_to_excel(project, str(output_path))
    elif req.format == "pdf":
        filename = f"report_{project.project_name}_{timestamp}.pdf"
        output_path = EXPORTS_DIR / filename
        from .exporters.pdf_exporter import export_to_pdf
        export_to_pdf(project, str(output_path))
    else:
        raise HTTPException(400, f"Unknown format: {req.format}")
    
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


@app.delete("/api/projects/{project_id}")
async def delete_project(project_id: str):
    """Delete a project."""
    if project_id not in projects_store:
        raise HTTPException(404, "Project not found")
    
    del projects_store[project_id]
    return {"status": "deleted", "project_id": project_id}


# ─── Run ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
