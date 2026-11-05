"""
Provider-Based Emergency Notification Schemas.
Supports multi-channel alert delivery (Email, SMS, In-App),
administrator approval gating, recipient lists, safe test mode,
and provider response tracking.
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class NotificationRecipient(BaseModel):
    recipient_id: str
    name: str
    role: str  # Resident, Mandal Officer, District Collector, ERT Lead, Test Contact
    mandal: Optional[str] = None
    district: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    is_test_recipient: bool = True
    active: bool = True
    consent_recorded: bool = True

class NotificationDispatchCreate(BaseModel):
    channel: str = Field(..., description="EMAIL, SMS, or IN_APP")
    target_scope: str = Field(..., description="STUDY_MANDAL, ENTIRE_DISTRICT, STATE_WIDE, or TEST_RECIPIENTS_ONLY")
    target_mandal: Optional[str] = None
    target_district: Optional[str] = None
    severity: str = Field(default="HIGH", description="CRITICAL, HIGH, MODERATE, ROUTINE")
    subject: str
    message: str
    action_guidance: Optional[str] = None
    source_reference: str = Field(default="APSDMA / Lower Godavari EDSS")
    approved_by_admin: bool = Field(default=False, description="Requires admin approval to release")
    admin_approval_note: Optional[str] = None
    test_mode_only: bool = Field(default=True, description="When true, sends strictly to verified test contacts")

class NotificationDeliveryRecord(BaseModel):
    dispatch_id: str
    channel: str
    created_at: str
    updated_at: str
    status: str  # DRAFT, PENDING_APPROVAL, APPROVED, QUEUED, SENT_TO_PROVIDER, DELIVERED, FAILED, CANCELLED
    target_scope: str
    target_mandal: Optional[str]
    target_district: Optional[str]
    severity: str
    subject: str
    message: str
    source_reference: str
    test_mode: bool
    recipients_count: int
    recipients_summary: List[Dict[str, Any]]
    provider_name: str
    provider_response: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    delivered_at: Optional[str] = None
