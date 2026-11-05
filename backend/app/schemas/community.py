"""
Community Hazard Report Schemas.
Supports citizen hazard reports with photos, GPS coordinates,
administrator triage workflow, duplicate detection, and ERT escalation.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class HazardReportCreate(BaseModel):
    mandal: str = Field(..., description="Mandal where hazard was observed")
    district: Optional[str] = Field(default="East Godavari", description="District name")
    category: str = Field(..., description="Hazard category: Flood Inundation, Waterlogging, Fallen Tree / Powerline, Damaged Road / Culvert, Strong Winds, Lightning Damage, Other Hazard")
    description: str = Field(..., max_length=1500, description="Observer notes and description")
    location_description: Optional[str] = Field(default=None, description="Landmark or reach description")
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    reporter_name: Optional[str] = Field(default="Anonymous Resident", description="Name of citizen")
    reporter_phone: Optional[str] = None
    photo_data: Optional[str] = Field(default=None, description="Base64 encoded photo or image data URL")
    voice_note_transcript: Optional[str] = Field(default=None, description="Telugu or English transcribed voice description")

class HazardReportStatusUpdate(BaseModel):
    status: str = Field(..., description="Target status: SUBMITTED, UNDER_REVIEW, VERIFIED, RESPONSE_ASSIGNED, IN_PROGRESS, RESOLVED, NEEDS_MORE_INFORMATION, DUPLICATE, REJECTED")
    reviewer_notes: Optional[str] = None
    reviewed_by: Optional[str] = "Mandal Administrator"

class HazardEscalateRequest(BaseModel):
    resource_type: str = Field(default="Rescue Motorboat", description="Resource type: Rescue Motorboat, Evacuation Ambulance, Road Clearance Crew, Sandbag Embankment Unit, Mobile Water Purification")
    priority: str = Field(default="HIGH", description="Priority level: URGENT, HIGH, MEDIUM, LOW")
    assigned_team: Optional[str] = Field(default="NDRF 10th Bn Team Delta / SDRF Unit 3", description="Tactical unit")
    dispatch_notes: Optional[str] = Field(default=None, description="Operational instructions for ERT crew")

class HazardReportRecord(BaseModel):
    report_id: str
    created_at: str
    updated_at: str
    status: str = "SUBMITTED"  # SUBMITTED -> UNDER_REVIEW -> VERIFIED -> RESPONSE_ASSIGNED -> IN_PROGRESS -> RESOLVED
    mandal: str
    district: str
    category: str
    description: str
    location_description: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    reporter_name_redacted: str
    has_photo: bool = False
    photo_url: Optional[str] = None
    voice_note_transcript: Optional[str] = None
    reviewer_notes: Optional[str] = None
    reviewed_by: Optional[str] = None
    linked_resource_request_id: Optional[str] = None
    potential_duplicate: Optional[Dict[str, Any]] = None
