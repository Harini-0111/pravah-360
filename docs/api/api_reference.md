# PRAVAH 360: REST API Specification & Endpoint Reference

**Base URL:** `http://127.0.0.1:8000/api/v1`
**Interactive Swagger UI:** `http://127.0.0.1:8000/docs`
**OpenAPI Specification:** `http://127.0.0.1:8000/openapi.json`

---

## 1. Geographic Identification & Spatial Lookups

### `GET /api/v1/geographic/identify`
Resolves geographic coordinates (latitude, longitude) to the enclosing administrative mandal and district via spatial indexing (STRtree / R-tree).

- **Parameters:**
  - `lat` (float, required): Latitude in decimal degrees (e.g., `16.5724`).
  - `lon` (float, required): Longitude in decimal degrees (e.g., `81.9961`).
- **Response `200 OK`:**
  ```json
  {
    "status": "success",
    "mandal_name": "Amalapuram",
    "district_name": "Dr. B.R. Ambedkar Konaseema",
    "fsi_score": 3.82,
    "fsi_category": "High",
    "population": 142850,
    "critical_facilities": 84,
    "primary_driver": "Low elevation & high drainage density"
  }
  ```

### `GET /api/v1/geographic/mandals`
Returns the GeoJSON FeatureCollection of all 21 study mandals with baseline demographic and susceptibility attributes.

---

## 2. Flood Susceptibility & Risk Assessment

### `GET /api/v1/flood-risk/basin-assessment`
Retrieves basin-wide flood susceptibility statistics, AHP criteria weightings, and cumulative population exposure metrics.

- **Response `200 OK`:**
  ```json
  {
    "study_area": "Lower Godavari Basin, AP",
    "total_mandals": 21,
    "baseline_population": 9126353,
    "elevated_exposure_population": 8252724,
    "critical_facilities_total": 1542,
    "ahp_weights": {
      "elevation": 0.3125,
      "slope": 0.3125,
      "distance_to_river": 0.1875,
      "land_cover": 0.0938,
      "drainage_density": 0.0938
    },
    "consistency_ratio": 0.0001
  }
  ```

### `GET /api/v1/flood-risk/mandal/{mandal_name}`
Returns granular risk profile, individual factor ratings, critical facilities count, and Telugu risk drivers for a specific mandal.

---

## 3. Alerts & Disaster Monitoring

### `GET /api/v1/alerts/feed`
Returns current official emergency warnings aggregated from APSDMA SACHET and IMD, complete with source freshness metadata.

- **Response `200 OK`:**
  ```json
  {
    "status": "success",
    "timestamp": "2026-11-09T14:30:00Z",
    "freshness_status": "FRESH (< 5 min)",
    "active_alerts_count": 3,
    "alerts": [
      {
        "alert_id": "APSDMA-2026-081",
        "severity": "Warning",
        "title": "Stage 2 Flood Warning - Godavari Mainstem",
        "source": "APSDMA / CWC",
        "source_timestamp": "2026-11-09T14:15:00Z",
        "affected_mandals": ["Polavaram", "Devipatnam", "Rajahmundry Rural"]
      }
    ]
  }
  ```

### `GET /api/v1/notifications/continuous-feed`
Provides a real-time event stream for the frontend sliding notification drawer.

### `POST /api/v1/notifications/acknowledge`
Records operator or resident acknowledgment of an active emergency broadcast.

---

## 4. Emergency Operations & Resource Allocation

### `POST /api/v1/operations/allocate`
Calculates optimal resource distribution across mandals using the Resource Allocation Priority Index (RAPI) and Hare-Niemeyer integer apportionment.

- **Request Body:**
  ```json
  {
    "available_boats": 50,
    "available_medical_kits": 100,
    "available_ration_packets": 200000
  }
  ```
- **Response `200 OK`:**
  ```json
  {
    "status": "success",
    "allocations": [
      {
        "mandal_name": "P.Gannavaram",
        "rapi_score": 0.884,
        "boats_allocated": 6,
        "medical_kits_allocated": 12,
        "ration_packets_allocated": 24500,
        "is_lanka_guaranteed": true
      }
    ]
  }
  ```

### `GET /api/v1/emergency/helplines`
Returns verified emergency response helpline numbers, SDRF control rooms, and district disaster management contacts.

---

## 5. Model Validation & Transparency

### `GET /api/v1/prediction/validation-report`
Returns the transparent evaluation metrics of the susceptibility classifier when benchmarked against the July 2022 flood candidate ground truth.

- **Response `200 OK`:**
  ```json
  {
    "evaluation_event": "Godavari July 2022 (Track 129)",
    "accuracy": 0.896,
    "brier_score": 0.088,
    "expected_calibration_error": 0.034,
    "contingency_matrix": {
      "true_positives": 18,
      "false_positives": 2,
      "false_negatives": 3,
      "true_negatives": 25
    }
  }
  ```

---

## 6. Voice Assistant & Accessibility

### `POST /api/v1/voice/tts`
Synthesizes Telugu (`te-IN`) or English (`en-IN`) speech audio payloads for emergency advisories.

- **Request Body:**
  ```json
  {
    "text": "గోదావరి నదికి వరద ప్రమాదం ఉంది. సహాయ కేంద్రాలకు తరలించండి.",
    "lang": "te-IN"
  }
  ```
- **Response `200 OK`:**
  ```json
  {
    "status": "success",
    "lang": "te-IN",
    "audio_type": "web_speech_or_encoded",
    "spoken_text": "..."
  }
  ```
