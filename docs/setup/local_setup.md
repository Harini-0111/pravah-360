# PRAVAH 360: Local Development & Setup Guide

This guide provides instructions for setting up, running, and testing **PRAVAH 360** on a local Windows development environment using Windows PowerShell.

---

## 1. Prerequisites

- **Operating System:** Windows 10/11, macOS, or Linux (commands below assume Windows PowerShell).
- **Python:** Python 3.10 to 3.14 (64-bit recommended).
- **Git:** Installed and available on system `PATH`.
- **Modern Web Browser:** Chrome, Edge, Firefox, or Safari with WebGL enabled.
- **Microphone & Speakers:** For testing browser-based Telugu Voice Assistant (`SpeechRecognition` & `SpeechSynthesis`).

---

## 2. Step-by-Step Installation

### Step 1: Clone the Repository
```powershell
git clone https://github.com/<your-username>/pravah-360.git
cd pravah-360
```

### Step 2: Create a Virtual Environment
```powershell
# Create virtual environment named .venv
python -m venv .venv

# Activate the virtual environment in PowerShell
.\.venv\Scripts\Activate.ps1
```
*(If script execution is disabled on Windows, run `Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` once in an elevated PowerShell).*

### Step 3: Install Required Dependencies
```powershell
# Upgrade pip
.\.venv\Scripts\python.exe -m pip install --upgrade pip

# Install project dependencies
.\.venv\Scripts\pip.exe install -r requirements.txt
```

### Step 4: Configure Environment Variables
Create a local `.env` configuration file from the template:
```powershell
Copy-Item .env.example .env
```
Open `.env` in your text editor and review configuration. All local operations and preprocessed datasets work with default placeholder values out of the box.

---

## 3. Starting the Application

Launch the FastAPI application server using Uvicorn:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
```

When startup succeeds, the terminal will display:
```text
INFO:     Started server process [PID]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

---

## 4. Accessing the Application

- **Web Application Single Page App:** Open your browser and navigate to:
  [`http://127.0.0.1:8000`](http://127.0.0.1:8000)
- **Interactive OpenAPI / Swagger Documentation:**
  [`http://127.0.0.1:8000/docs`](http://127.0.0.1:8000/docs)
- **ReDoc Interactive Documentation:**
  [`http://127.0.0.1:8000/redoc`](http://127.0.0.1:8000/redoc)

---

## 5. Running Automated Tests

The repository includes 9 automated test suites comprising 98 unit and integration test cases covering AHP consistency, geographic spatial indexing, alert freshness lifecycles, and emergency operations.

### Running Pure Unit Tests (Offline)
```powershell
.\.venv\Scripts\python.exe -m unittest tests/test_ahp_consistency_and_weights.py tests/test_flood_risk_assessment.py tests/test_geographic_identification.py tests/test_flood_data_validation.py tests/test_pravah_auth.py
```

### Running the Complete Test Suite (98 Tests)
To run the full suite (including live REST API endpoint verification):
1. In Terminal 1, ensure the server is active:
   ```powershell
   .\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --port 8000
   ```
2. In Terminal 2, run the test runner:
   ```powershell
   .\.venv\Scripts\python.exe -m unittest discover tests/
   ```
   **Expected Result:**
   ```text
   Ran 98 tests in ~20.1s
   OK
   ```

---

## 6. Obtaining and Processing External Geospatial Datasets Locally

Due to upstream redistribution licensing restrictions, third-party administrative boundary files (GADM) and regional river reach vectors (HydroRIVERS) are not packaged in the public GitHub repository. They must be downloaded separately and processed locally using the provided automation scripts:

### A. GADM Administrative Boundaries (v4.1)
- **Source:** [GADM Download Portal](https://gadm.org/download_country.html) (Select India; download Country Level 2 districts and Level 3 sub-districts/mandals).
- **Licensing:** Free for academic and non-commercial research; public redistribution prohibited.
- **Local Placement:** Place the raw files into `data/raw/boundaries/district/` and `data/raw/boundaries/mandal/`.
- **Processing Command:**
  ```powershell
  .\.venv\Scripts\python.exe scripts/download_boundaries.py
  ```
  This script filters and clips the 21 Lower Godavari study mandals across Dr. B.R. Ambedkar Konaseema, East Godavari, and West Godavari districts, outputting `data/processed/boundaries/lower_godavari_mandals.geojson` and associated bounding boxes.

### B. HydroRIVERS Basin Hydrographic Network (v10)
- **Source:** [HydroSHEDS / WWF HydroRIVERS](https://www.hydrosheds.org/products/hydrorivers) (Download the Asian Region river network archive `HydroRIVERS_v10_as_shp.zip`).
- **Licensing:** Free for scientific, educational, and non-commercial research.
- **Local Placement:** Place and extract the shapefile into `data/raw/rivers/HydroRIVERS_v10_as_shp/`.
- **Processing Command:**
  ```powershell
  .\.venv\Scripts\python.exe scripts/download_rivers.py
  ```
  This script clips the continental network to the Lower Godavari basin boundary and generates `data/processed/rivers/lower_godavari_hydrorivers.geojson` for the distance-to-river analysis factor.
