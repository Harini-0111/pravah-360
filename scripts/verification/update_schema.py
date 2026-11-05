"""
Update ResidentHelpRequestCreate in backend/app/schemas/monitoring.py
"""
SCHEMA_PATH = r"C:\major project\backend\app\schemas\monitoring.py"

with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
    text = f.read()

target = '''class ResidentHelpRequestCreate(BaseModel):
    mandal: str
    district: str
    contact_name: Optional[str] = "Resident"
    contact_phone: Optional[str] = None
    location_description: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    urgency: str = Field(default="HIGH", description="CRITICAL, HIGH, MODERATE")
    assistance_type: str = Field(..., description="Evacuation, Medical, Food/Water, Shelter, Stranded Livestock")
    num_persons_affected: int = 1
    situation_notes: str'''

replacement = '''class ResidentHelpRequestCreate(BaseModel):
    mandal: str
    district: Optional[str] = "East Godavari"
    contact_name: Optional[str] = "Resident"
    contact_phone: Optional[str] = None
    location_description: str = "Unspecified river reach"
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    urgency: str = Field(default="HIGH", description="CRITICAL, HIGH, MODERATE")
    assistance_type: str = Field(default="Evacuation", description="Evacuation, Medical, Food/Water, Shelter, Stranded Livestock")
    num_persons_affected: int = 1
    situation_notes: Optional[str] = ""

    # Support friendly aliases from different client versions
    def __init__(self, **data):
        if "resident_name" in data and "contact_name" not in data:
            data["contact_name"] = data["resident_name"]
        if "specific_location" in data and "location_description" not in data:
            data["location_description"] = data["specific_location"]
        if "required_assistance" in data and "assistance_type" not in data:
            data["assistance_type"] = data["required_assistance"]
        if "number_of_persons" in data and "num_persons_affected" not in data:
            data["num_persons_affected"] = data["number_of_persons"]
        super().__init__(**data)'''

text = text.replace(target, replacement)
with open(SCHEMA_PATH, "w", encoding="utf-8") as f:
    f.write(text)

print("Updated ResidentHelpRequestCreate schema with optional defaults and client aliases!")
