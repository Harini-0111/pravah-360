"""
Pydantic Schemas for Google Weather API & Location Intelligence.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class WeatherCondition(BaseModel):
    description: str = Field(..., description="Human-readable condition text")
    icon_uri: Optional[str] = Field(None, description="Official icon URI if provided")
    icon_code: Optional[str] = Field(None, description="Standardized condition code e.g. CLEAR, RAIN, THUNDERSTORM")

class CurrentConditions(BaseModel):
    temperature_c: Optional[float] = Field(None, description="Air temperature in Celsius")
    feels_like_c: Optional[float] = Field(None, description="Apparent feels-like temperature in Celsius")
    relative_humidity_pct: Optional[int] = Field(None, description="Relative humidity percentage (0-100)")
    wind_speed_kmh: Optional[float] = Field(None, description="Wind speed in km/h")
    wind_direction_deg: Optional[int] = Field(None, description="Wind direction in degrees (0-360)")
    wind_direction_cardinal: Optional[str] = Field(None, description="Cardinal wind direction e.g. N, SW, ENE")
    precipitation_mm: Optional[float] = Field(None, description="Precipitation quantity in mm")
    precipitation_probability_pct: Optional[int] = Field(None, description="Probability of precipitation (0-100)")
    condition: WeatherCondition = Field(..., description="Current weather condition")
    update_time_utc: Optional[str] = Field(None, description="Observation time in ISO 8601 UTC")
    update_time_local: Optional[str] = Field(None, description="Formatted local observation time (IST)")

class HourlyForecastItem(BaseModel):
    time_utc: str
    time_local: str
    temperature_c: float
    feels_like_c: Optional[float] = None
    precipitation_probability_pct: int = 0
    precipitation_mm: float = 0.0
    condition: WeatherCondition

class DailyForecastItem(BaseModel):
    date: str
    max_temperature_c: float
    min_temperature_c: float
    precipitation_probability_pct: int = 0
    precipitation_mm: float = 0.0
    condition: WeatherCondition

class WeatherAlertItem(BaseModel):
    id: str
    headline: str
    severity: str = Field(..., description="Severity level: EXTREME, SEVERE, MODERATE, MINOR, UNKNOWN")
    urgency: str = Field(..., description="Urgency: IMMEDIATE, EXPECTED, FUTURE, PAST, UNKNOWN")
    certainty: Optional[str] = None
    event: str
    description: str
    effective_time: str
    expire_time: str
    source_agency: str

class UnifiedWeatherResponse(BaseModel):
    is_available: bool = Field(..., description="True if weather data was retrieved or verified")
    api_status: str = Field(..., description="OK, API_KEY_NOT_CONFIGURED, API_ERROR, RATE_LIMITED, etc.")
    message: Optional[str] = None
    location: Dict[str, Any] = Field(..., description="Geographic location details")
    flood_model_supported: bool = Field(..., description="Whether exploratory flood susceptibility model covers this location")
    flood_model_note: str = Field(..., description="Explanation of flood susceptibility assessment coverage")
    current: Optional[CurrentConditions] = None
    hourly_forecast: List[HourlyForecastItem] = []
    daily_forecast: List[DailyForecastItem] = []
    alerts: List[WeatherAlertItem] = []
    alerts_status: str = Field(..., description="ACTIVE_OFFICIAL_ALERTS, NO_ACTIVE_ALERTS_REPORTED, COVERAGE_UNAVAILABLE, API_KEY_NOT_CONFIGURED, API_ERROR, UNSUPPORTED_LOCATION")
    alerts_source_info: str = Field(..., description="Description of alert issuing authority or coverage in provider feed")
    cached: bool = False
    cache_expiry_utc: Optional[str] = None

class LocationSearchResult(BaseModel):
    name: str
    formatted_name: str
    latitude: float
    longitude: float
    admin_level: str
    district: Optional[str] = None
    mandal: Optional[str] = None
    state: str = "Andhra Pradesh"
    country: str = "India"
    within_study_area: bool = False
