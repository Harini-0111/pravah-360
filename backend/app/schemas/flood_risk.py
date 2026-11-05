from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from backend.app.schemas.geographic import GeographicIdentification

# --- Phase 2 Models (Preserved for compatibility) ---

class FloodMarker(BaseModel):
    id: str
    marker_id: Optional[str] = None
    name: Optional[str] = None
    latitude: float
    longitude: float
    risk_level: str  # Critical, High, Moderate, Low
    inundation_probability: float
    water_depth_est_m: Optional[float] = None
    water_depth_m: Optional[float] = None
    geographic_info: GeographicIdentification
    mandal: Optional[str] = None
    district: Optional[str] = None
    state: Optional[str] = None
    formatted_location: str
    timestamp: str
    susceptibility_score: Optional[float] = None
    water_depth_status: Optional[str] = "NOT_OBSERVED"
    observation_type: Optional[str] = "TERRAIN_SUSCEPTIBILITY_MONITORING"

class FloodAlert(BaseModel):
    alert_id: str
    severity: str  # RED_ALERT, ORANGE_ALERT, YELLOW_ALERT, ADVISORY
    risk_level: str  # Critical, High, Moderate
    title: str
    headline: Optional[str] = None
    mandal: str
    district: str
    state: str
    latitude: float
    longitude: float
    coordinates_str: str
    summary: str
    message: Optional[str] = None
    action_recommended: str
    human_readable_location: str
    issued_at: str
    alert_type: Optional[str] = "SUSCEPTIBILITY_ADVISORY"
    observation_status: Optional[str] = "SATELLITE_SAR_PENDING_EXPORT_VALIDATION"

class FloodImpactSummary(BaseModel):
    study_area: str
    total_monitored_points: int
    critical_risk_count: int
    critical_points_count: Optional[int] = None
    high_risk_count: int
    high_risk_points_count: Optional[int] = None
    moderate_risk_count: int
    districts_impacted: Optional[List[str]] = None
    mandals_affected: Any  # List[str] or Dict[str, int]
    district_summary: Dict[str, Dict[str, Any]]


# --- Phase 4 Explainable Flood Risk & Impact Assessment Models ---

class FactorBreakdown(BaseModel):
    elevation_m: float
    elevation_score: float
    slope_deg: float
    slope_score: float
    river_distance_km: float
    major_river_distance_km: Optional[float] = None
    river_proximity_score: float
    landcover_dominant: str
    landcover_score: float
    historical_hazard_score: float
    dem_coverage_pct: Optional[float] = 98.12

class MandalRiskAssessment(BaseModel):
    mandal_name: str
    district_name: str
    reorganized_district_2022: str
    area_sq_km: float
    susceptibility_score: float  # 0.0 to 1.0
    risk_level: str  # Low, Moderate, High, Very High
    baseline_population_2020: int
    potentially_exposed_population: int
    exposed_population_pct: float
    population_very_high_risk: Optional[int] = None
    population_high_risk: Optional[int] = None
    population_moderate_risk: Optional[int] = None
    population_low_risk: Optional[int] = None
    raw_population_very_high: Optional[float] = None
    raw_population_high: Optional[float] = None
    raw_population_moderate: Optional[float] = None
    raw_population_low: Optional[float] = None
    raw_baseline_population: Optional[float] = None
    healthcare_facilities_count: int
    educational_facilities_count: int
    emergency_shelters_count: int
    total_facilities_count: int
    facilities_very_high_risk: Optional[int] = None
    facilities_high_risk: Optional[int] = None
    factors: FactorBreakdown
    primary_risk_drivers: List[str]
    plain_english_explanation: str
    scientific_limitations: List[str]
    confidence_level: Optional[str] = "HIGH"
    dem_coverage_confidence: Optional[str] = "HIGH"
    overall_assessment_confidence: Optional[str] = "UNRATED (Exploratory Multi-Criteria Model)"

class DistrictRiskSummary(BaseModel):
    district_name: str
    total_mandals: int
    mandals_by_risk: Dict[str, int]
    total_baseline_population: int
    total_exposed_population: int
    total_facilities_exposed: int

class BasinRiskAssessmentSummary(BaseModel):
    study_area: str
    total_mandals: int
    risk_distribution: Dict[str, int]
    total_population: int
    total_potentially_exposed_population: int
    exposed_population_pct: Optional[float] = None
    population_exposure_by_risk: Dict[str, int]
    raw_population_exposure_by_risk: Optional[Dict[str, float]] = None
    raw_total_population: Optional[float] = None
    raw_total_exposed_population: Optional[float] = None
    rounding_discrepancy: Optional[int] = 0
    total_mapped_facilities: int
    facilities_by_risk: Dict[str, int]
    district_summaries: Dict[str, DistrictRiskSummary]
    mandals: List[MandalRiskAssessment]
    methodology: str
    factor_weights: Dict[str, float]
    classification_thresholds: Dict[str, str]
    data_sources: Dict[str, str]
    sar_inundation_status: str

class PointRiskEvaluationInput(BaseModel):
    latitude: float
    longitude: float
    weights: Optional[Dict[str, float]] = None

class PointRiskEvaluation(BaseModel):
    latitude: float
    longitude: float
    is_inside_study_area: bool
    mandal: Optional[str] = None
    district: Optional[str] = None
    susceptibility_score: Optional[float] = None
    risk_level: str
    elevation_m: Optional[float] = None
    slope_deg: Optional[float] = None
    river_distance_km: Optional[float] = None
    landcover_class: Optional[str] = None
    historical_hazard_score: Optional[float] = None
    explanation: str
    limitation_note: str
    confidence_level: Optional[str] = "HIGH"
    dem_coverage_confidence: Optional[str] = "HIGH"
    overall_assessment_confidence: Optional[str] = "UNRATED (Exploratory Multi-Criteria Model)"

class SensitivityScenario(BaseModel):
    scenario_name: str
    description: str
    weights: Dict[str, float]
    risk_distribution: Dict[str, int]
    mandals_shifted_count: int
    notable_shifts: List[str]

class SensitivityAnalysisResult(BaseModel):
    baseline_weights: Dict[str, float]
    scenarios: List[SensitivityScenario]
    conclusion: str
