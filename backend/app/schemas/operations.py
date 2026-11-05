"""
Emergency Operations Simulator Schemas.
Supports role-based decision support for Residents, Mandal Administrators,
District Administrators, and Emergency Response Teams (ERT).
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class AdvisoryCreate(BaseModel):
    mandal: str = Field(..., description="Target mandal name")
    district: str = Field(..., description="Target district name")
    target_tiers: List[str] = Field(default=["Very High", "High"], description="Target susceptibility tiers")
    priority: str = Field(default="HIGH", description="Priority level: CRITICAL, HIGH, MODERATE, ROUTINE")
    headline: str = Field(..., max_length=200, description="Advisory headline (max 200 chars)")
    message: str = Field(..., max_length=2000, description="Plain-language safety instructions (max 2000 chars)")
    action_recommended: str = Field(..., description="Recommended tactical evacuation or protection actions")
    dispatched_by: str = Field(default="Mandal Disaster Management Cell", description="Issuing authority designation")

class AdvisoryRecord(BaseModel):
    advisory_id: str
    mandal: str
    district: str
    target_tiers: List[str]
    priority: str
    headline: str
    message: str
    action_recommended: str
    dispatched_by: str
    created_at: str
    status: str = "ACTIVE"  # ACTIVE, EXPIRED, CANCELLED
    stats: Dict[str, int] = Field(default_factory=lambda: {"queued": 0, "delivered_simulated": 0, "acknowledged_simulated": 0})

class AdvisoryAcknowledge(BaseModel):
    advisory_id: str
    mandal: Optional[str] = None
    district: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    resident_identifier: Optional[str] = "Resident-Anonymous"

class ResourceRequestCreate(BaseModel):
    mandal: str
    district: str
    category: str = Field(..., description="Resource category e.g. Rescue boats, Food and drinking water, Medical kits and first aid, Emergency medicines, Temporary shelters and essential supplies, Rescue personnel and transport support")
    quantity: int = Field(..., gt=0)
    unit: str = Field(default="units")
    priority: str = Field(default="HIGH", description="CRITICAL, HIGH, MODERATE")
    reason: str = Field(..., description="Operational justification / situation description")
    requester_role: str = Field(default="Mandal Incident Commander")

class ResourceRequestUpdate(BaseModel):
    status: str = Field(..., description="Target status: Requested, Approved, Dispatched, On Scene, Completed, Rejected, Cancelled")
    note: Optional[str] = None
    updated_by: str = Field(default="ERT Incident Dispatch")

class ResourceRequestRecord(BaseModel):
    request_id: str
    mandal: str
    district: str
    category: str
    quantity: int
    unit: str
    priority: str
    reason: str
    requester_role: str
    current_status: str = "Requested"
    created_at: str
    updated_at: str
    status_history: List[Dict[str, Any]] = Field(default_factory=list)

class NearestFacility(BaseModel):
    name: str
    facility_type: str
    distance_km: float
    host_risk_level: Optional[str] = None
    latitude: float
    longitude: float
    emergency_ready: bool = False

class ResidentViewResponse(BaseModel):
    location_name: str
    mandal: str
    district: str
    state: str
    latitude: float
    longitude: float
    within_study_area: bool
    susceptibility_score: float
    susceptibility_tier: str
    active_advisories: List[AdvisoryRecord]
    nearest_facilities: List[NearestFacility]
    advisory_count: int

class DistrictOverviewResponse(BaseModel):
    district: str
    total_mandals: int
    mandals: List[str]
    total_population: int
    exposed_population: int
    exposure_percentage: float
    highest_risk_tier: str
    active_advisories_count: int
    acknowledgment_rate_pct: float
    resource_requests_count: int
    pending_resources_count: int
