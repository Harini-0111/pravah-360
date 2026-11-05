# PRAVAH 360 · Security & Deployment Audit

**Audit Date:** 2026-11-03  
**Application:** PRAVAH 360 v2.0 — Geospatial Disaster Intelligence & Emergency Decision Support  
**Backend:** FastAPI / Python · SQLite · Uvicorn  
**Frontend:** Vanilla HTML/CSS/JavaScript · Leaflet · Globe.GL

---

## 1. Authentication Security

| Check | Status | Finding |
|:---|:---|:---|
| Password hashing algorithm | ✅ PASS | PBKDF2-HMAC-SHA256 with unique random salt per user. Iteration count adequate. |
| Password storage | ✅ PASS | Hashed values only stored. No plaintext passwords in database or logs. |
| Session token entropy | ✅ PASS | `secrets.token_urlsafe(32)` — cryptographically secure, 256-bit equivalent. |
| Session cookie attributes | ⚠️ WARN | `httponly=True, samesite='lax'` — correct. **`secure=False`** — must be changed to `True` before any non-localhost deployment with HTTPS. |
| Session expiry | ✅ PASS | `max_age=86400` (24 hours). Sessions cleared on logout. |
| Rate limiting on login | ✅ PASS | IP-based rate limiter on `POST /auth/login`. Lockout after repeated failures. |
| Rate limiting on registration | ⚠️ WARN | No rate limit on `POST /auth/register`. Recommendation: add IP-based limit (5/hour). |
| Seeded demo credentials | ⚠️ INFO | Four evaluator accounts seeded in `scripts/seed_users.py`. Passwords meet complexity requirements. NOT hardcoded in source — stored via `create_user.py` script. |
| Default passwords shipped | ✅ PASS | No default passwords in production code. `create_user.py` prompts interactively. |
| Forgot password | ⚠️ WARN | Shows alert only. No automated reset workflow. See MISSING_FEATURES C-1. |

---

## 2. Role-Based Access Control

| Check | Status | Finding |
|:---|:---|:---|
| Role enforcement on advisory broadcast | ✅ PASS | `require_roles(['mandal_admin','district_admin','emergency_response'])` |
| Role enforcement on district overview | ✅ PASS | `require_roles(['district_admin','emergency_response'])` |
| Role enforcement on resource status update | ✅ PASS | `require_roles(['mandal_admin','district_admin','emergency_response'])` |
| Role enforcement on help-requests list | ✅ FIXED | Previously unenforced. Now `require_roles(['mandal_admin','district_admin','emergency_response'])` — **fixed in this session (C-3)** |
| Citizen accessing admin routes | ✅ PASS | 403 returned for out-of-role access |
| Unauthenticated access to sensitive routes | ✅ PASS | 401 returned correctly |
| Role enforcement on audit log | ✅ PASS | `GET /auth/audit-log` protected |

---

## 3. Input Validation

| Check | Status | Finding |
|:---|:---|:---|
| SQL injection (SQLite) | ✅ PASS | All queries use parameterised statements |
| HTML injection in advisory messages | ✅ PASS | `html.escape()` applied to advisory content before storage |
| Advisory message length | ✅ FIXED | `max_length=2000` added to `AdvisoryCreate.message` — **fixed in this session (C-4)** |
| Email format validation | ✅ PASS | Pydantic `EmailStr` type used |
| Password minimum length | ✅ PASS | Enforced server-side (8 chars minimum) and client-side |
| Coordinate bounds validation | ✅ PASS | Latitude/longitude checked against study area bounds |

---

## 4. Secrets & Credentials

| Check | Status | Finding |
|:---|:---|:---|
| `.env` in `.gitignore` | ✅ PASS | `.env` is gitignored |
| API keys in frontend JS | ✅ PASS | No API keys found in `app.js`, `index.html`, or CSS |
| Credentials in source code | ✅ PASS | No hardcoded credentials found |
| `.env.example` provided | ✅ PASS | `.env.example` present with placeholder values |
| CDSE/NASA credentials | ⚠️ WARN | Real credentials exist in `.env` for satellite data. In production, use environment variable injection rather than file-based secrets. |
| Session secret rotation | ⚠️ INFO | Session tokens are per-user UUID. No application-level signing secret needed. |

---

## 5. CORS Configuration

| Check | Status | Finding |
|:---|:---|:---|
| Current CORS setting | ⚠️ WARN | `allow_origins=["*"]` — permits any origin |
| `allow_credentials=True` | ⚠️ WARN | Combined with `allow_origins=["*"]`, this is a security misconfiguration for production. Browsers reject this combination for cookies, but it signals an incomplete hardening. |
| **Production recommendation** | Action required | Replace `["*"]` with explicit allowed origins: `["https://yourdomain.com"]` |

---

## 6. Error Leakage

| Check | Status | Finding |
|:---|:---|:---|
| Stack traces in API errors | ✅ PASS | FastAPI default: 500 errors return generic JSON, not tracebacks in production mode |
| Debug endpoints exposed | ✅ PASS | No debug or admin backdoor endpoints found |
| Password in error messages | ✅ PASS | Authentication errors are generic ("Invalid credentials") |
| Session ID in response body | ⚠️ INFO | Login response includes `session_id` in JSON body for JS to store. This is safe when used alongside HttpOnly cookie but is redundant — consider removing from response body |

---

## 7. Frontend Security

| Check | Status | Finding |
|:---|:---|:---|
| XSS via innerHTML | ⚠️ WARN | `app.js` uses `innerHTML` to render advisory messages and alert content. Mitigated by server-side HTML escaping, but `textContent` is safer where layout allows |
| CSP (Content Security Policy) | ❌ MISSING | No CSP header configured. Add CSP header in nginx/uvicorn to restrict script-src |
| External resources | ⚠️ INFO | Google Fonts loaded from CDN. Add to CSP allowlist |
| Password in localStorage | ✅ PASS | Session managed via HttpOnly cookie. No passwords or tokens in localStorage |
| Eval or unsafe JS patterns | ✅ PASS | No `eval()`, no `Function()` constructor |

---

## 8. Deployment Readiness Checklist

| Item | Status | Action Required |
|:---|:---|:---|
| Production startup command | ✅ Ready | `uvicorn backend.app.main:app --host 0.0.0.0 --port 8000` |
| Reverse proxy (nginx/Caddy) | ❌ Not configured | Required for TLS |
| TLS/HTTPS | ❌ Not configured | Required before any public deployment |
| Cookie `secure=True` | ❌ Missing | Set in endpoints.py before deploying with HTTPS |
| CORS origin restriction | ❌ Missing | Replace `["*"]` with production domain |
| Environment variable management | ⚠️ File-based | Move to OS environment variables or secrets manager |
| Database backups | ⚠️ Manual | `data/users.db` — add scheduled backup |
| Logging configuration | ✅ Pass | Uvicorn access logging active |
| Health check endpoint | ✅ Pass | `GET /api/v1/monitoring/health` returns service status |
| Static file serving | ✅ Pass | FastAPI StaticFiles mount serving `/static/` |
| README | ✅ Pass | Project README exists |
| `.gitignore` | ✅ Pass | Correctly excludes `.env`, rasters, venv |

---

## 9. Production Startup Commands

```bash
# 1. Install dependencies (first time only)
python -m pip install -r requirements.txt

# 2. Seed privileged accounts (first time only, prompts for passwords)
python scripts/create_user.py

# 3. Start the server (development)
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000

# 4. Start the server (production — behind reverse proxy)
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --workers 2 --access-log
```

> [!CAUTION]
> Do NOT use `--host 0.0.0.0` without a TLS-terminating reverse proxy in front. The session cookie is currently `secure=False` which must be changed to `secure=True` once HTTPS is available.

---

## 10. Security Verdict

**Overall:** The application is suitable for local demonstration and evaluation. It has real password hashing, proper session management, and role-based access control on the majority of sensitive endpoints.

**Before any public or external deployment:**
1. Add TLS via nginx/Caddy
2. Set `secure=True` on session cookie
3. Restrict CORS to the production domain
4. Add registration rate limiting
5. Remove or restrict the `session_id` from the login response body
6. Add a Content Security Policy header
