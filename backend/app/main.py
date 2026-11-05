"""
Main FastAPI Application.
AI-Based Flood Risk, Impact Assessment and Emergency Decision Support System.
"""
import os
import json
from typing import Optional
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse

from backend.app.api.endpoints import router as api_router

app = FastAPI(
    title="Geospatial Flood Intelligence & Decision Support System",
    description="Explainable Geospatial AI for Flood Risk and Impact Assessment with Human-Readable Geographic Place Names",
    version="2.0.0"
)

# Enable CORS for local dev and web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API endpoints
app.include_router(api_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_event():
    import asyncio
    import logging
    from backend.app.services.normalization_service import MonitoringDataNormalizationService
    from backend.app.api.endpoints import monitoring_service
    logger = logging.getLogger("uvicorn")
    try:
        mig_res = MonitoringDataNormalizationService.run_all_migrations()
        logger.info(f"Startup data normalization completed: Alerts={mig_res['alerts_migration']['valid_count']}, Gauges={mig_res['gauges_migration']['valid_count']}")
    except Exception as me:
        logger.warning(f"Startup data normalization notice: {me}")

    try:
        monitoring_service.execute_all_checks()
        asyncio.create_task(monitoring_service.start_daemon(interval_seconds=300))
    except Exception as e:
        logger.error(f"Startup monitoring daemon initialization error: {e}")

@app.on_event("shutdown")
def shutdown_event():
    from backend.app.api.endpoints import monitoring_service
    monitoring_service.stop_daemon()

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")
BOUNDARIES_GEOJSON = os.path.join(BASE_DIR, "data", "processed", "boundaries", "lower_godavari_mandals.geojson")

@app.get("/api/v1/health")
def health_check():
    return {
        "status": "healthy",
        "system": "Geospatial Flood Intelligence System",
        "study_area": "Lower Godavari Basin, Andhra Pradesh",
        "phase": "Phase 2 - Geographic Area Identification & Alerts"
    }

@app.get("/api/v1/boundaries/mandals-geojson")
def get_mandals_geojson():
    """Serves the processed GADM mandal boundaries for frontend map rendering."""
    if os.path.exists(BOUNDARIES_GEOJSON):
        with open(BOUNDARIES_GEOJSON, "r", encoding="utf-8") as f:
            return json.load(f)
    return JSONResponse(status_code=404, content={"error": "Boundary GeoJSON not found"})

# Serve frontend single-page application
if os.path.exists(FRONTEND_DIR):
    app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")

    @app.get("/")
    def serve_frontend_root(request: Request):
        try:
            ui = request.query_params.get("ui")
            no_cache_headers = {
                "Cache-Control": "no-cache, no-store, must-revalidate",
                "Pragma": "no-cache",
                "Expires": "0"
            }
            if ui == "classic":
                classic_file = os.path.join(FRONTEND_DIR, "index_classic.html")
                if os.path.exists(classic_file):
                    with open(classic_file, "r", encoding="utf-8") as f:
                        return HTMLResponse(content=f.read(), headers=no_cache_headers)
            index_file = os.path.join(FRONTEND_DIR, "index.html")
            if os.path.exists(index_file):
                with open(index_file, "r", encoding="utf-8") as f:
                    return HTMLResponse(content=f.read(), headers=no_cache_headers)
            return {"message": "Geospatial Flood Intelligence API active. Frontend index.html not yet built."}
        except Exception as e:
            import traceback
            traceback.print_exc()
            return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
