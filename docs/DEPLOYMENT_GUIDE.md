# PRAVAH 360 · Deployment Guide

**Version:** 2.0 — Phase 3 Final  
**Application:** Geospatial Disaster Intelligence & Emergency Decision Support  
**Stack:** Python 3.14 / FastAPI / SQLite / Vanilla JS + Leaflet + Globe.GL

---

## Prerequisites

| Requirement | Minimum | Recommended |
|:---|:---|:---|
| Python | 3.11 | 3.12+ |
| RAM | 2 GB | 4 GB |
| Disk | 5 GB | 10 GB (includes raster datasets) |
| OS | Windows 10 / Ubuntu 20.04 | Ubuntu 22.04 LTS |
| Network | Local only | HTTPS behind nginx (production) |

---

## Quick Start (Local Development)

```bash
# 1. Clone / extract the project
cd C:\major project       # Windows
# cd /home/user/pravah360 # Linux

# 2. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate    # Windows
# source .venv/bin/activate  # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up environment variables
cp .env.example .env
# Edit .env with your credentials (see Environment Variables section)

# 5. Seed privileged accounts (one-time setup)
python scripts/create_user.py
# Enter email, password, full name, role, district when prompted

# 6. Start the development server
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload

# 7. Open the application
# Navigate to: http://127.0.0.1:8000
```

---

## Environment Variables

Create a `.env` file from `.env.example`. Required variables:

```env
# Google Earth Engine (for satellite analysis)
EARTHENGINE_PROJECT=your-gee-project-id

# Copernicus Data Space (for Sentinel-1 SAR data)
CDSE_USERNAME=your-cdse-email@domain.com
CDSE_PASSWORD=your-cdse-password
CDSE_CLIENT_ID=your-client-id
CDSE_CLIENT_SECRET=your-client-secret

# NASA Earthdata (for GPM IMERG rainfall)
NASA_EARTHDATA_USERNAME=your-username
NASA_EARTHDATA_PASSWORD=your-password

# Study area bounds (do not change for Lower Godavari deployment)
STUDY_AREA_MIN_LON=81.0
STUDY_AREA_MAX_LON=82.8
STUDY_AREA_MIN_LAT=16.3
STUDY_AREA_MAX_LAT=17.9
```

> [!CAUTION]
> Never commit `.env` to version control. It is gitignored by default. For production, inject these as OS environment variables or use a secrets manager (AWS Secrets Manager, GCP Secret Manager, etc.).

---

## Account Management

### Create Privileged Accounts

```bash
# Interactive account creation script
python scripts/create_user.py
```

Prompts for: email, password (min 8 chars), full name, role, district.  
Roles: `citizen`, `mandal_admin`, `district_admin`, `emergency_response`

### Evaluator Demo Accounts (seeded)

| Role | Email | Default Password |
|:---|:---|:---|
| Resident | `citizen@pravah360.in` | Set via `create_user.py` |
| Mandal Admin | `mandal.admin@pravah360.in` | Set via `create_user.py` |
| District Admin | `district.collector@pravah360.in` | Set via `create_user.py` |
| ERT | `ert.commander@pravah360.in` | Set via `create_user.py` |

> [!IMPORTANT]
> Passwords are NOT in source code. Run `scripts/create_user.py` on first deployment to create these accounts with your chosen passwords. The evaluator pills on the login page fill the credentials you set.

---

## Database

- **Engine:** SQLite
- **File location:** `data/users.db`
- **Schema managed by:** `backend/app/services/auth_db_service.py` (auto-creates on startup)
- **Backup:** Copy `data/users.db` to a safe location before updates

```bash
# Manual backup
cp data/users.db backups/users_$(date +%Y%m%d).db
```

---

## Production Deployment (Linux + nginx + TLS)

### 1. Configure nginx

```nginx
server {
    listen 443 ssl;
    server_name pravah360.yourdomain.com;

    ssl_certificate     /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 2. Enable Secure Cookie (REQUIRED for HTTPS)

Edit `backend/app/api/endpoints.py` — find all `set_cookie` calls and change:

```python
# Change this line in every set_cookie call:
secure=False    # development
# To:
secure=True     # production (HTTPS only)
```

### 3. Restrict CORS

Edit `backend/app/main.py`:

```python
# Change:
allow_origins=["*"]
# To:
allow_origins=["https://pravah360.yourdomain.com"]
```

### 4. Start with systemd

```ini
[Unit]
Description=PRAVAH 360 FastAPI Application
After=network.target

[Service]
User=pravah
WorkingDirectory=/opt/pravah360
EnvironmentFile=/opt/pravah360/.env
ExecStart=/opt/pravah360/.venv/bin/uvicorn backend.app.main:app \
          --host 127.0.0.1 --port 8000 --workers 2 --access-log
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable pravah360
sudo systemctl start pravah360
```

---

## Health Checks

```bash
# Application health
curl http://127.0.0.1:8000/api/v1/monitoring/health

# Expected response:
# {"status": "healthy", "services": {...}, "alerts_loaded": 12, ...}
```

---

## Fallback: Classic UI

The original dashboard UI remains accessible at:
```
http://127.0.0.1:8000/?ui=classic
```
This serves `frontend/index_classic.html` as a fallback during evaluation.

---

## Pre-Deployment Security Checklist

- [ ] `secure=True` on all session cookies
- [ ] CORS restricted to production domain
- [ ] `.env` file not in repository
- [ ] No seeded plaintext passwords in source code
- [ ] TLS certificate valid and configured
- [ ] Rate limiting active on login (built-in) and registration (recommendation)
- [ ] Database backup scheduled
- [ ] Health endpoint accessible
- [ ] All tests passing: `python -m pytest tests/`

---

## File Structure Reference

```
major project/
├── backend/
│   └── app/
│       ├── api/endpoints.py        # All 58 API routes
│       ├── main.py                 # FastAPI app, CORS, static files
│       ├── services/               # Business logic services
│       └── schemas/                # Pydantic models
├── frontend/
│   ├── index.html                  # Main application (all pages)
│   ├── index_classic.html          # Fallback dashboard UI
│   ├── app.js                      # Frontend controller (3,892 lines)
│   ├── styles.css                  # Dashboard styles
│   ├── entry_journey.css           # Entry/auth page styles
│   └── assets/images/              # All photographs + brand SVGs
├── data/
│   ├── users.db                    # SQLite auth + session database
│   └── *.geojson                   # Precomputed geographic data
├── tests/                          # 78 backend unit tests
├── scripts/
│   ├── create_user.py              # Privileged account creation
│   └── seed_users.py               # Evaluator account seeder
├── docs/
│   ├── FINAL_FEATURE_AUDIT.md
│   ├── IMAGE_ASSET_USAGE_REPORT.md
│   ├── MISSING_FEATURES_AND_RECOMMENDATIONS.md
│   ├── SECURITY_AND_DEPLOYMENT_AUDIT.md
│   ├── FINAL_TEST_REPORT.md
│   └── DEPLOYMENT_GUIDE.md         # ← this file
├── .env                            # Local secrets (gitignored)
├── .env.example                    # Template for .env
└── .gitignore                      # Excludes .env, rasters, venv
```
