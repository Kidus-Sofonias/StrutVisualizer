"""
Data models for Structural Engineering Analysis Application.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum


class ClassificationResult(Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    NOT_DETERMINED = "not_determined"
    MISSING_DATA = "missing_data"


@dataclass
class StoreySourceData:
    """Raw imported data from Access/ETABS for a single storey."""
    source_name: str = ""
    source_table: str = ""
    elevation: Optional[float] = None
    height: Optional[float] = None
    mass: Optional[float] = None
    mmi: Optional[float] = None  # Mass Moment of Inertia
    ls_slab: Optional[float] = None  # Floor radius of gyration from slab elements
    xcm: Optional[float] = None
    ycm: Optional[float] = None
    xcr: Optional[float] = None
    ycr: Optional[float] = None
    # Unit load displacements
    ux_ul1: Optional[float] = None
    uy_ul1: Optional[float] = None
    rz_ul1: Optional[float] = None
    ux_ul2: Optional[float] = None
    uy_ul2: Optional[float] = None
    rz_ul2: Optional[float] = None
    ux_ul3: Optional[float] = None
    uy_ul3: Optional[float] = None
    rz_ul3: Optional[float] = None
    # Unit load shears
    vx_ul1: Optional[float] = None
    vy_ul2: Optional[float] = None
    t_ul3: Optional[float] = None
    # Actual earthquake forces (EQX/EQY) for stiffness
    vx_eqx: Optional[float] = None
    vy_eqy: Optional[float] = None
    # Actual earthquake displacements (EQX/EQY) for inter-storey drift
    ux_eqx: Optional[float] = None
    uy_eqx: Optional[float] = None
    ux_eqy: Optional[float] = None
    uy_eqy: Optional[float] = None
    # Diaphragm Drifts (from Diaphragm Drifts table)
    drift_x_eqx: Optional[float] = None  # DriftX for EQX load case
    drift_y_eqy: Optional[float] = None  # DriftY for EQY load case (next-row)
    import_timestamp: Optional[datetime] = None


@dataclass
class StoreyCalculation:
    """Calculated results for a single storey, for all modules."""
    module_3_2_1_status: str = ""
    module_3_2_1_lambda: Optional[float] = None
    
    eox: Optional[float] = None
    eoy: Optional[float] = None
    
    kfx: Optional[float] = None
    kfy: Optional[float] = None
    kmt: Optional[float] = None
    rx: Optional[float] = None
    ry: Optional[float] = None
    
    module_3_2_4_status_x: str = ""
    module_3_2_4_status_y: str = ""
    module_3_2_4_eox_status: str = ""
    module_3_2_4_eoy_status: str = ""
    module_3_2_4_limit_x: Optional[float] = None
    module_3_2_4_limit_y: Optional[float] = None
    
    ls: Optional[float] = None
    module_3_2_5_rx_status: str = ""
    module_3_2_5_ry_status: str = ""
    
    kx: Optional[float] = None
    ky: Optional[float] = None
    module_3_2_6_status: str = ""
    module_3_2_7_status: str = ""
    
    module_3_2_8_mass: Optional[float] = None
    module_3_2_8_status_upper: str = ""
    module_3_2_8_status_lower: str = ""
    
    overall_classification: ClassificationResult = ClassificationResult.NOT_DETERMINED
    failure_reasons: List[str] = field(default_factory=list)


@dataclass
class Storey:
    """A single storey — the fundamental unit of analysis."""
    storey_id: str
    normalized_name: str
    building_id: str
    order: int = 0
    source_data: StoreySourceData = field(default_factory=StoreySourceData)
    calculations: StoreyCalculation = field(default_factory=StoreyCalculation)

    @property
    def has_source_data(self) -> bool:
        sd = self.source_data
        return any(v is not None for v in [
            sd.xcm, sd.ycm, sd.xcr, sd.ycr,
            sd.ux_ul1, sd.uy_ul2, sd.rz_ul3,
            sd.vx_ul1, sd.vy_ul2, sd.t_ul3,
            sd.mass
        ])


@dataclass
class Project:
    """A structural engineering project."""
    project_id: str
    project_name: str
    client: str = ""
    designed_by: str = ""
    database_file: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    storeys: List[Storey] = field(default_factory=list)
    lmax: float = 33.5
    lmin: float = 22.5
    building_summary: str = ""
    total_weight_override: Optional[float] = None  # Manual override for W in kN (Section 4.1)
    
    def get_storey_by_name(self, name: str) -> Optional[Storey]:
        for s in self.storeys:
            if s.normalized_name.upper() == name.upper():
                return s
        return None
    
    def get_storeys_sorted(self) -> List[Storey]:
        return sorted(self.storeys, key=lambda s: s.order, reverse=True)
