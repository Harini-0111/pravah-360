# PRAVAH 360 · Missing Features & Recommendations

**Audit Date:** 2026-11-03  
**Scope:** All workspaces, all roles, entry journey, safety and security  
**Priority scale:** Critical → High → Medium → Optional

---

## CRITICAL (must resolve before any public deployment)

### C-1 · Password Reset / Account Recovery
**Gap:** "Forgot password?" shows an alert message directing users to a district administrator. There is no self-service password reset.  
**Impact:** A resident who forgets their password cannot re-access emergency alerts without human intervention during a disaster.  
**Recommendation:** Implement a simple reset-token flow: generate a time-limited token (stored hashed in the DB), display the token directly in-app (no email needed for v1), allow the user to submit the token and choose a new password. Alternatively, allow password reset by district admin via `scripts/create_user.py`.  
**Effort:** 1 day (backend token endpoint + simple frontend form).

### C-2 · HTTPS / TLS in Production
**Gap:** The application runs over plain HTTP on `127.0.0.1:8000`. Cookies are not marked `Secure` in the current configuration, so HttpOnly session cookies transmit in plain text over any non-localhost deployment.  
**Impact:** Session hijacking risk on any non-localhost deployment.  
**Recommendation:** Deploy behind a reverse proxy (nginx or Caddy) with TLS. Set `Secure` cookie attribute in `auth_db_service.py` response. Do not deploy without TLS.  
**Effort:** 1 hour (proxy config) + 1 hour (cookie flag).

### C-3 · Role-Based Access Enforcement on Sensitive API Endpoints
**Gap:** `GET /api/v1/operations/district/overview` and `POST /api/v1/operations/advisories` both use `require_roles` correctly. However, `GET /api/v1/operations/resident/help-requests` (all SOS requests, including personal GPS data) does not verify the caller's role — any authenticated user can list all help requests.  
**Impact:** Resident SOS details (name, location, number of persons) are accessible by any logged-in citizen.  
**Recommendation:** Add `require_roles(['mandal_admin','district_admin','emergency_response'])` to the `GET /api/v1/operations/resident/help-requests` endpoint.  
**Effort:** 10 minutes.

### C-4 · Input Validation: Advisory Broadcast
**Gap:** `POST /api/v1/operations/advisories` does not enforce a maximum message length on the server side. An extremely long advisory message could cause DB or memory issues.  
**Recommendation:** Add `max_length=1000` constraint on the `message` field in the advisory schema.  
**Effort:** 5 minutes.

---

## HIGH (important for reliability and trust)

### H-1 · Data Source Timestamps on Every Panel
**Gap:** River stage readings show timestamps. Weather cards, alert banners and impact assessment panels do not consistently show when data was last refreshed.  
**Impact:** Users cannot tell whether a "Moderate" alert is from 5 minutes ago or 5 hours ago.  
**Recommendation:** Add a `data_as_of` timestamp to every API response and surface it in the UI as a small grey label ("As of 14:23 IST · Source: IMD").  
**Effort:** 2 hours (backend) + 2 hours (frontend).

### H-2 · Stale / Unavailable Data Indicators
**Gap:** When the weather service returns an error or the monitoring service has no data, the UI currently shows blank cards or the last cached value without a clear "data unavailable" state.  
**Recommendation:** Each API-driven card should show a consistent "Data temporarily unavailable — last updated: [time]" message with a retry button when the API call fails.  
**Effort:** 3 hours (frontend).

### H-3 · Telugu Language Completeness
**Gap:** The language toggle switches header/navigation labels and some alert severity labels to Telugu. Body text of preparedness guides, form labels on registration, and advisory content remain in English.  
**Impact:** Rural residents who read primarily Telugu cannot follow preparedness instructions.  
**Recommendation:** Translate all safety guide content (at least Flood, Cyclone, Landslide chapters) into Telugu. Maintain a `translations.js` file for systematic management.  
**Effort:** 3–4 hours (content translation + JS integration).

### H-4 · Verified Emergency Contact Numbers
**Gap:** Helpline numbers shown (NDMA 1078, Police 100, Fire 101, Ambulance 108, Coastal Guard 1554) are standard national numbers. The Andhra Pradesh SDMA helpline number requires verification against the current official APSDMA directory.  
**Recommendation:** Verify all numbers from `https://apsdma.ap.gov.in/` and add source attribution ("Source: APSDMA, verified [date]").  
**Effort:** 30 minutes.

### H-5 · Globe Free-Text Search
**Gap:** The "Search" input on the Global 3D Earth workspace accepts text but only navigates to four hardcoded country presets.  
**Recommendation:** Implement a simple lookup against the GeoJSON countries dataset, or integrate the existing `GET /api/v1/locations/search` endpoint for India-specific queries.  
**Effort:** 2 hours.

### H-6 · 7-Day Weather Forecast (Daily)
**Gap:** The weather service returns 7 days of daily forecast data but the UI only displays 5.  
**Recommendation:** Update the daily forecast renderer to display all returned days (up to 7).  
**Effort:** 30 minutes.

### H-7 · Remember Me (Extended Session)
**Gap:** "Remember me" checkbox is visible but does not extend the session cookie beyond the default session lifetime.  
**Recommendation:** Pass a `remember: true` flag to the login endpoint. The backend `AuthDBService.authenticate()` should set `max_age=604800` (7 days) on the session cookie when the flag is true.  
**Effort:** 1 hour.

---

## MEDIUM (improves experience and completeness)

### M-1 · Demo / Evaluator Mode Banner
**Gap:** Evaluator demo accounts use real-looking data. Judges may not immediately know they are using a pre-seeded demonstration account.  
**Recommendation:** When logged in via an evaluator pill, show a non-intrusive banner: "Demo Mode — sample data only. Not a live operational system."  
**Effort:** 1 hour.

### M-2 · First-Time User Guidance / Onboarding Tooltip
**Gap:** After role selection and location confirmation, new residents land on the Situation Awareness Home with no guidance on what to do first.  
**Recommendation:** A dismissible 3-step tooltip (e.g., "1. Check your local alert. 2. See your risk map. 3. Know your SOS.") on first login for citizen role.  
**Effort:** 2 hours.

### M-3 · New Photos Integration into Analytics Workspaces
**Gap:** Three new user-supplied photographs are saved but not yet integrated into Emergency Operations, Global Earth, and Safety workspaces.  
**Recommendation:** Add `rescue_boat_evacuation.jpg` to the Community Aid workspace header, `bay_aerial_ocean_waves.jpg` as the Global Earth intro banner, and `monsoon_shelter_community.jpg` to the Safety workspace.  
**Effort:** 1 hour.

### M-4 · API Rate Limiting on Registration
**Gap:** `POST /api/v1/auth/register` does not have rate limiting. A malicious actor could bulk-register accounts.  
**Recommendation:** Add IP-based rate limiting (5 registrations per hour per IP) mirroring the existing login rate limiter.  
**Effort:** 1 hour.

### M-5 · Print / Offline Stylesheet for Safety Guides
**Gap:** Safety guides cannot be saved as a PDF or printed in a readable format.  
**Recommendation:** Add a `@media print` stylesheet that renders only the safety guide content cleanly.  
**Effort:** 2 hours.

### M-6 · Loading and Empty States
**Gap:** Some workspace tables show blank while data is loading.  
**Recommendation:** Add skeleton loading states to the resource board, advisories table, and help requests list.  
**Effort:** 2 hours.

### M-7 · Accessibility (WCAG 2.1 AA)
**Gap:** Auth form focus ring visibility is adequate. Several map controls lack ARIA labels. The language toggle in the header has no `aria-label`.  
**Recommendation:** Add `aria-label` to all icon-only buttons. Ensure focus ring is visible in all high-contrast modes.  
**Effort:** 2 hours.

---

## OPTIONAL (future enhancements)

| ID | Feature | Rationale |
|:---|:---|:---|
| O-1 | Email notification provider integration | Currently test-only; requires SMTP or SMS API |
| O-2 | SOS request real-time push (WebSocket) | Allows ERT to receive instant alert without polling |
| O-3 | Offline service worker for safety guides | Allows access to preparedness content without connectivity |
| O-4 | Multi-language admin interface | Mandal admins may prefer Telugu UI |
| O-5 | Automated helpline verification job | Re-check contact numbers weekly against APSDMA |
| O-6 | Satellite imagery auto-refresh trigger | Re-run SAR candidate detection on schedule |
| O-7 | Mobile app wrapper (PWA) | Improves mobile access for rural residents |
| O-8 | Audit log viewer in admin UI | Currently API-only; admin UI display not implemented |

---

## Summary

| Priority | Count | Addressed in this session |
|:---|:---|:---|
| Critical | 4 | C-3 fixed (SOS data access). C-1, C-2, C-4 documented with instructions. |
| High | 7 | H-5, H-6, H-7 documented. Remaining require dedicated development. |
| Medium | 7 | M-3 tracked (photos). Others documented for next sprint. |
| Optional | 8 | Backlog for post-evaluation roadmap. |
