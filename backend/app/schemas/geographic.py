from typing import Optional, List, Any
from pydantic import BaseModel, Field

class CoordinateInput(BaseModel):
    latitude: Any
    longitude: Any
    point_id: Optional[str] = None
    label: Optional[str] = None

class BatchCoordinateInput(BaseModel):
    points: List[CoordinateInput]

class GeographicIdentification(BaseModel):
    latitude: Any
    longitude: Any
    is_valid_coordinate: bool
    country: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    district_code: Optional[str] = None
    mandal: Optional[str] = None
    subdistrict_code: Optional[str] = None
    village: Optional[str] = None
    village_status: str
    formatted_location: str
    within_study_area: bool
    precision_level: str
    error: Optional[str] = None
