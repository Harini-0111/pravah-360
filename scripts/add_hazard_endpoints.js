const fs = require('fs');
const path = 'C:/major project/backend/app/api/endpoints.py';
let code = fs.readFileSync(path, 'utf8');

// 1. Add Community Hazard Service imports near top
const importAnchor = "from backend.app.services.notification_service import NotificationDeliveryService";
const newImports = `from backend.app.services.notification_service import NotificationDeliveryService
from backend.app.services.community_hazard_service import CommunityHazardService
from backend.app.schemas.community import HazardReportCreate, HazardReportRecord, HazardReportStatusUpdate
from fastapi.responses import FileResponse`;

if (!code.includes("CommunityHazardService")) {
  code = code.replace(importAnchor, newImports);
  console.log("✓ Added CommunityHazardService imports");
}

// 2. Add hazard_service instantiation near other services
const initAnchor = "notification_service = NotificationDeliveryService()";
const newInit = `notification_service = NotificationDeliveryService()
hazard_service = CommunityHazardService()`;

if (!code.includes("hazard_service = CommunityHazardService()")) {
  code = code.replace(initAnchor, newInit);
  console.log("✓ Added hazard_service instance");
}

// 3. Add Hazard Endpoints at the bottom
const hazardEndpoints = `
# ==============================================================================
# COMMUNITY HAZARD REPORTING & GROUND OBSERVER WORKFLOW
# ==============================================================================

@router.post("/community/hazards/report", response_model=HazardReportRecord)
def submit_community_hazard(report: HazardReportCreate):
    """
    Submits a verified citizen ground observation or hazard photo report.
    Presents status: SUBMITTED -> UNDER_REVIEW -> VERIFIED / REJECTED -> RESOLVED.
    """
    return hazard_service.submit_report(report)

@router.get("/community/hazards", response_model=List[HazardReportRecord])
def list_community_hazards(mandal: Optional[str] = None, status: Optional[str] = None):
    """
    Returns public hazard feed with citizen PII redacted.
    """
    return hazard_service.list_reports(mandal=mandal, status=status)

@router.patch("/community/hazards/{report_id}/status", response_model=HazardReportRecord)
def update_hazard_status(
    report_id: str,
    update: HazardReportStatusUpdate,
    current_user: Dict[str, Any] = Depends(require_roles(["mandal_admin", "district_admin", "emergency_response"]))
):
    """
    Allows authorized administrators to verify, reject, or resolve hazard reports.
    """
    updated = hazard_service.update_report_status(report_id, update)
    if not updated:
        raise HTTPException(status_code=404, detail="Hazard report not found")
    return updated

@router.get("/community/hazards/{report_id}/photo")
def get_hazard_photo(report_id: str):
    """Returns the photo file uploaded with the hazard report."""
    photo_path = hazard_service.get_photo_path(report_id)
    if not photo_path or not os.path.exists(photo_path):
        raise HTTPException(status_code=404, detail="Photo not found")
    return FileResponse(photo_path, media_type="image/jpeg")
`;

if (!code.includes("/community/hazards/report")) {
  code = code + hazardEndpoints;
  console.log("✓ Added community hazard endpoints");
}

fs.writeFileSync(path, code, 'utf8');
console.log("Endpoints file updated successfully.");
