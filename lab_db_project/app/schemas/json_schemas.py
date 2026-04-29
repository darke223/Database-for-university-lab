from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class SampleGeometry(BaseModel):
    diameter_mm: float = Field(..., gt=0)
    length_mm: float = Field(..., gt=0)
    additional_info: Optional[Dict[str, Any]] = None

class PhysicalProperties(BaseModel):
    density_kg_m3: float = Field(..., gt=0)
    elastic_modulus_gpa: Optional[float] = Field(None, gt=0)
    yield_strength_mpa: Optional[float] = Field(None, gt=0)
    material_grade: Optional[str] = None

class StrikerGeometry(BaseModel):
    diameter_mm: float = Field(..., gt=0)
    length_mm: float = Field(..., gt=0)
    mass_g: Optional[float] = Field(None, gt=0)

class MeasurementPoint(BaseModel):
    time_ms: float
    strain: float
    stress_mpa: float

class ResultMeasurements(BaseModel):
    temperature_c: Optional[float] = None
    strain_rate_s1: Optional[float] = None
    max_stress_mpa: Optional[float] = None
    data_points: Optional[List[MeasurementPoint]] = None
    raw_metadata: Optional[Dict[str, Any]] = None
