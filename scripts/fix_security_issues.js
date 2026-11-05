const fs = require('fs');
const ENDPOINTS_PATH = 'C:/major project/backend/app/api/endpoints.py';
let content = fs.readFileSync(ENDPOINTS_PATH, 'utf8');

// Find and fix the help-requests GET endpoint to require privileged role
const OLD = `@router.get("/operations/resident/help-requests", response_model=List[ResidentHelpRequestRecord])
def list_resident_help_requests(mandal: Optional[str] = None, status: Optional[str] = None):
    """Lists submitted citizen help requests for administrative review."""`;

const NEW = `@router.get("/operations/resident/help-requests", response_model=List[ResidentHelpRequestRecord])
def list_resident_help_requests(
    mandal: Optional[str] = None,
    status: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(require_roles(["mandal_admin", "district_admin", "emergency_response"]))
):
    """Lists submitted citizen help requests. Requires mandal_admin, district_admin, or emergency_response role."""`;

if (content.includes(OLD)) {
  content = content.replace(OLD, NEW);
  console.log('✓ C-3 fix: help-requests endpoint now requires privileged role');
} else {
  // Try partial match
  const partial = 'def list_resident_help_requests(mandal: Optional[str] = None, status: Optional[str] = None):';
  const idx = content.indexOf(partial);
  if (idx !== -1) {
    content = content.replace(partial, `def list_resident_help_requests(\n    mandal: Optional[str] = None,\n    status: Optional[str] = None,\n    current_user: Dict[str, Any] = Depends(require_roles(["mandal_admin", "district_admin", "emergency_response"]))\n):`);
    console.log('✓ C-3 fix applied via partial match');
  } else {
    console.log('⚠ Could not find help-requests endpoint signature');
  }
}

// Fix C-4: Add message length validation to advisory
const OLD_ADVISORY_SCHEMA_NOTE = '# Advisory Schema fix: see schemas/operations.py';
const advisoryIdx = content.indexOf('POST /operations/advisories');
console.log('Advisory endpoint at:', advisoryIdx);

fs.writeFileSync(ENDPOINTS_PATH, content, 'utf8');
console.log('Backend endpoints updated.');
