"""
PRAVAH 360 - Official Emergency Helplines Directory
Maintains verified official disaster management and emergency contact numbers for Andhra Pradesh
and national emergency response. All numbers are sourced from official government portals
(MHA ERSS, APSDMA, AP WRD, District Collectorates).
"""

from typing import List, Dict, Any
from datetime import datetime

OFFICIAL_EMERGENCY_HELPLINES = [
    {
        "id": "nh-112",
        "service_name_en": "National Emergency Response Support System (ERSS)",
        "service_name_te": "జాతీయ అత్యవసర స్పందన వ్యవస్థ (ERSS)",
        "number": "112",
        "category": "ALL_EMERGENCIES",
        "hours": "24/7 Toll-Free",
        "authority": "Ministry of Home Affairs, Govt. of India",
        "jurisdiction": "All India & Andhra Pradesh",
        "description_en": "Single emergency number for police, fire, ambulance and disaster rescue dispatch.",
        "description_te": "పోలీస్, అగ్నిమాపక, అంబులెన్స్ మరియు విపత్తు సహాయం కోసం ఒకే జాతీయ అత్యవసర నంబరు.",
        "verified_date": "2026-11-04",
        "source_url": "https://www.mha.gov.in/emergency-response-support-system-erss"
    },
    {
        "id": "sdma-1070",
        "service_name_en": "AP-SDMA State Disaster Emergency Operation Centre",
        "service_name_te": "ఆంధ్రప్రదేశ్ విపత్తు నిర్వహణ సంస్థ (AP-SDMA) కంట్రోల్ రూమ్",
        "number": "1070",
        "category": "DISASTER_STATE",
        "hours": "24/7 Toll-Free",
        "authority": "Andhra Pradesh State Disaster Management Authority",
        "jurisdiction": "Andhra Pradesh State",
        "description_en": "State-level 24/7 disaster control room for cyclone, flood alerts and evacuation assistance.",
        "description_te": "తుఫానులు, వరద హెచ్చరికలు మరియు పునరావాస సహాయం కోసం రాష్ట్ర స్థాయి కంట్రోల్ రూమ్.",
        "verified_date": "2026-11-04",
        "source_url": "https://apsdma.ap.gov.in"
    },
    {
        "id": "deoc-1077",
        "service_name_en": "District Emergency Operations Centre (Collectorate)",
        "service_name_te": "జిల్లా కలెక్టరేట్ విపత్తు కంట్రోల్ రూమ్",
        "number": "1077",
        "category": "DISASTER_DISTRICT",
        "hours": "24/7 Toll-Free",
        "authority": "District Collector & Magistrate, East Godavari / Konaseema",
        "jurisdiction": "Lower Godavari Basin (District Level)",
        "description_en": "District collectorate control room for local mandal flood relief, boat dispatch and shelter info.",
        "description_te": "మండల స్థాయి వరద సహాయం, బోట్ల సమన్వయం మరియు పునరావాస కేంద్రాల కోసం జిల్లా కంట్రోల్ రూమ్.",
        "verified_date": "2026-11-04",
        "source_url": "https://eastgodavari.ap.gov.in"
    },
    {
        "id": "med-108",
        "service_name_en": "Emergency Medical & Ambulance Service",
        "service_name_te": "అత్యవసర వైద్య & అంబులెన్స్ సేవలు",
        "number": "108",
        "category": "MEDICAL",
        "hours": "24/7 Toll-Free",
        "authority": "Department of Health & Family Welfare, Govt. of Andhra Pradesh",
        "jurisdiction": "Andhra Pradesh State",
        "description_en": "Immediate medical evacuation, flood casualty triage, and life-support ambulance dispatch.",
        "description_te": "వరద బాధితుల వైద్య అత్యవసర సేవలు మరియు తక్షణ అంబులెన్స్ సహాయం.",
        "verified_date": "2026-11-04",
        "source_url": "https://health.ap.gov.in"
    },
    {
        "id": "fire-101",
        "service_name_en": "Fire, Water Rescue & Embankment Emergency",
        "service_name_te": "అగ్నిమాపక & జల రక్షణ సేవలు",
        "number": "101",
        "category": "RESCUE",
        "hours": "24/7 Toll-Free",
        "authority": "AP State Disaster Response and Fire Services Department",
        "jurisdiction": "Andhra Pradesh State",
        "description_en": "Water rescue, boat deployment for stranded families, and embankment hazard safety.",
        "description_te": "వరదల్లో చిక్కుకున్న ప్రజల రక్షణ మరియు రెస్క్యూ బోట్ కార్యకలాపాలు.",
        "verified_date": "2026-11-04",
        "source_url": "https://fireservices.ap.gov.in"
    },
    {
        "id": "tele-104",
        "service_name_en": "Health Advice & Epidemic Helpline",
        "service_name_te": "ఆరోగ్య సలహా & అంటువ్యాధుల నివారణ హెల్ప్‌లైన్",
        "number": "104",
        "category": "HEALTH_ADVICE",
        "hours": "24/7 Toll-Free",
        "authority": "Department of Health, Govt. of Andhra Pradesh",
        "jurisdiction": "Andhra Pradesh State",
        "description_en": "Tele-consultation for water-borne illnesses, safe drinking water chlorine dosing advice.",
        "description_te": "కలుషిత నీటి వ్యాధుల నివారణ మరియు సురక్షిత తాగునీటి సలహాల కోసం వైద్యుల హెల్ప్‌లైన్.",
        "verified_date": "2026-11-04",
        "source_url": "https://health.ap.gov.in"
    }
]

def get_official_helplines() -> List[Dict[str, Any]]:
    return OFFICIAL_EMERGENCY_HELPLINES
