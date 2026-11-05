const fs = require('fs');

const tr = `// PRAVAH 360 - Comprehensive Bilingual Translation System (English & Telugu)
// Covers all surfaces: Navigation, Welcome, Login, Register, Role Selection,
// Location Onboarding, Situation Home, Operations, Weather, Alerts, Hazards, and Voice.

window.PRAVAH_TRANSLATIONS = {
  en: {
    // Top Nav & Common
    "langToggle": "తెలుగు",
    "navOverview": "Overview",
    "navAwareness": "Awareness",
    "navRoles": "Personas",
    "navHelplines": "Helplines",
    "navRegister": "Register Free",
    "navSignIn": "Sign In →",
    "signOut": "Sign Out",
    "backToWelcome": "← Back to Welcome",
    "back": "Back",
    "search": "Search",
    "reset": "Reset",
    "commandCentre": "Enter Command Centre",
    "guidedTour": "Start Guided Tour",
    "emergencySos": "Emergency SOS",

    // Welcome Hero
    "heroTagline": "See the risk. Stay prepared.",
    "heroHeadline": "When nature changes, be prepared.",
    "heroStatement": "Understand disasters. Protect communities. Connect people to help across the Lower Godavari Basin.",
    "btnExplore": "Explore Platform ↓",
    "btnCreateAccount": "Register Free →",
    "btnSignIn": "Sign In",
    "liveMonitoring": "Live Satellite & Sensor Monitoring",
    "basinSubtitle": "Lower Godavari Basin & River Delta",
    "basinDesc": "Real-time flood vulnerability, satellite radar detection, and emergency coordination across 21 mandals.",

    // Section 02 Awareness
    "secAwarenessTitle": "Understand the Situation on the Ground",
    "secAwarenessDesc": "Live Earth observation, river stage telemetries, and community relief operations across the Godavari delta.",
    "activeSurveillance": "Active Environmental Surveillance",
    "cycloneBannerTitle": "Severe Weather & Flood Stage Alerts",
    "cycloneBannerSub": "Central Water Commission & IMD live telemetric monitoring active across all 21 mandals.",
    
    // Awareness Cards
    "card1Title": "River Flood Monitoring",
    "card1Desc": "Live CWC sensor levels at Dowleswaram Barrage and Bhadrachalam upstream station.",
    "card1Link": "View River Levels →",
    "card2Title": "Coastal Weather & Cyclones",
    "card2Desc": "Deep Bay of Bengal depressions and cyclonic storm surge forecasts from IMD radar feeds.",
    "card2Link": "View Weather Forecast →",
    "card3Title": "Heavy Monsoon Rainfall",
    "card3Desc": "High-resolution ERA5 & GPM precipitation accumulation overlays for river basin catchments.",
    "card3Link": "Explore Rainfall Analytics →",
    "card4Title": "Community Preparedness",
    "card4Desc": "Local high-elevation cyclone relief centers and emergency safe drinking water distribution.",
    "card4Link": "Explore Relief Shelters →",
    "card5Title": "Evacuation & Rescue Operations",
    "card5Desc": "NDRF and SDRF tactical motorboat deployment tracking and safe navigation corridors.",
    "card5Link": "Response Coordination →",

    // Personas Section
    "secPersonasTitle": "A Platform Engineered for Every Stakeholder",
    "secPersonasDesc": "Tailored interfaces for community residents, district administrators, and tactical disaster response teams.",
    "roleResidentTitle": "Residents & Rural Communities",
    "roleResidentDesc": "Access hyper-local flood risk warnings, locate high-ground shelters, request safe drinking water, and trigger emergency SOS.",
    "roleResidentBtn": "Get Started as Resident →",
    "roleResponseTitle": "Emergency Response Teams (NDRF/SDRF)",
    "roleResponseDesc": "Real-time submerged obstacle maps, high-clearance rescue boat navigation, and emergency extraction dispatch.",
    "roleResponseBtn": "Access Response Center →",
    "roleMandalTitle": "Mandal Administrator",
    "roleMandalDesc": "Local ward-level monitoring, resource dispatching, relief material inventory, and shelter coordination.",
    "roleMandalBtn": "Access Mandal Control →",
    "roleDistrictTitle": "District Collectorate",
    "roleDistrictDesc": "Basin-wide predictive models, demographic exposure analytics, inter-agency resource allocation, and evacuation orders.",
    "roleDistrictBtn": "Access District Operations →",

    // Authentication: Login
    "signInTitle": "Welcome back",
    "signInDesc": "Sign in to access your monitoring workspace and emergency operations.",
    "emailLabel": "Email Address",
    "passwordLabel": "Password",
    "rememberMe": "Remember me on this device",
    "forgotPassword": "Forgot password?",
    "btnSignInSubmit": "Sign In to Account →",
    "noAccountText": "Don't have an account?",
    "createAccountLink": "Create a free account →",
    "evaluatorPillLabel": "Quick-fill demo account:",

    // Authentication: Registration
    "registerTitle": "Create your account",
    "registerDesc": "Register as a resident to receive local disaster alerts and emergency assistance.",
    "fullNameLabel": "Full Name",
    "regEmailLabel": "Email Address",
    "regPasswordLabel": "Password (min 8 chars)",
    "confirmPasswordLabel": "Confirm Password",
    "districtLabel": "District",
    "mandalLabel": "Mandal",
    "btnRegisterSubmit": "Create Account & Proceed →",
    "haveAccountText": "Already have an account?",
    "signInLink": "Sign In →",

    // Role Selection
    "roleSelectTitle": "Choose Your Operational Role",
    "roleSelectSub": "Tailored workflows for residents, administrators, and emergency responders across the Godavari Basin.",

    // Location Onboarding
    "onboardingTitle": "Confirm Your Location",
    "onboardingSub": "Set your district and mandal to receive hyper-local flood alerts and nearest shelter mapping.",
    "btnDetectLocation": "Detect My Location",
    "btnSaveOnboarding": "Save Location & Enter Platform →",

    // Situation Awareness Home
    "sitHomeTitle": "Situation Awareness Home",
    "sitHomeSub": "Real-time operational overview for your selected sector",
    "btnLaunchExplorer": "Launch Web GIS Explorer",
    "btnLaunchAidConnect": "Open AidConnect Operations",
    "btnLaunchEvidence": "Scientific Methodology & AI",
    "btnLaunchHelp": "Emergency Preparedness",
    "summaryHeading": "Operational Overview & Intelligence",

    // Operations & SOS
    "opsTitle": "AidConnect Emergency Operations",
    "sosHeading": "Urgent Rescue Assistance (SOS)",
    "sosDesc": "If you are trapped by flood water or cut off, send an immediate distress alert.",
    "btnSendSos": "Request Emergency Extraction (SOS)",

    // Ground Hazard Reporting
    "hazardReportTitle": "Citizen Ground Hazard & Field Reporting",
    "hazardReportDesc": "Report waterlogged roads, breached embankments, or trapped citizens. Verified by district response teams.",
    "hazardMandalLabel": "Select Mandal",
    "hazardTypeLabel": "Hazard Type",
    "hazardLandmarkLabel": "Landmark / Local Name",
    "hazardDescLabel": "Detailed Description",
    "hazardPhotoLabel": "Field Photo (Optional)",
    "btnSubmitHazard": "Submit Field Hazard Report",
    "recentObservationsTitle": "Recent Verified Field Observations",

    // Helplines Section
    "helplineTitle": "Official Andhra Pradesh Emergency Helplines",
    "helplineSub": "Toll-free 24/7 disaster helplines and district emergency operation centers.",
    "helplineSdma": "AP State Disaster Management Authority",
    "helplineNational": "National Emergency Response Support",
    "helplineMedical": "Medical & Ambulance Emergency",
    "helplineDistrict": "District Collectorate Control Room",

    // Voice Assistant
    "voiceAssistantTitle": "PRAVAH 360 Voice Assistant",
    "voiceListeningPrompt": "Listening... Speak naturally in Telugu or English",
    "voiceInputPlaceholder": "Type your question here if microphone is unavailable...",
    "btnSendVoiceQuery": "Ask",
    "voicePromptRain": "వర్షం పడుతుందా? (Is it raining?)",
    "voicePromptWeather": "ఈరోజు వాతావరణం ఎలా ఉంది? (Today's Weather)",
    "voicePromptFlood": "మా ప్రాంతంలో వరద ప్రమాదం ఉందా? (Flood Risk)",
    "voicePromptHospital": "దగ్గరలో ఆసుపత్రి ఎక్కడ ఉంది? (Nearest Hospital)",
    "voicePromptShelter": "పునరావాస కేంద్రం ఎక్కడ ఉంది? (Shelter)",
    "voicePromptHelpline": "అత్యవసర నంబర్లు (Helplines)",
    "voicePromptHelp": "సహాయం కావాలి (Need Help / SOS)",
    "btnReplayVoice": "🔄 Replay Voice"
  },

  te: {
    // Top Nav & Common
    "langToggle": "English",
    "navOverview": "అవలోకనం",
    "navAwareness": "తాజా సమాచారం",
    "navRoles": "విభాగాల పాత్రలు",
    "navHelplines": "హెల్ప్‌లైన్లు",
    "navRegister": "నమోదు చేసుకోండి",
    "navSignIn": "సైన్ ఇన్ →",
    "signOut": "లాగ్ అవుట్",
    "backToWelcome": "← హోమ్ పేజీకి వెళ్ళండి",
    "back": "వెనుకకు",
    "search": "వెతకండి",
    "reset": "రీసెట్ చేయండి",
    "commandCentre": "కమాండ్ సెంటర్‌లోకి ప్రవేశించండి",
    "guidedTour": "గైడెడ్ టూర్ ప్రారంభించండి",
    "emergencySos": "అత్యవసర SOS",

    // Welcome Hero
    "heroTagline": "ప్రమాదాన్ని గుర్తించండి. సంసిద్ధంగా ఉండండి.",
    "heroHeadline": "ప్రకృతి మారినప్పుడు, సిద్ధంగా ఉండండి.",
    "heroStatement": "గోదావరి లోతట్టు ప్రాంతాలలో విపత్తులను ముందే అర్థం చేసుకోండి. సమాజాలను రక్షించండి. ప్రజలను తక్షణ సహాయంతో అనుసంధానించండి.",
    "btnExplore": "వివరాలు చూడండి ↓",
    "btnCreateAccount": "ఉచిత నమోదు →",
    "btnSignIn": "సైన్ ఇన్",
    "liveMonitoring": "ప్రత్యక్ష ఉపగ్రహ & సెన్సార్ పర్యవేక్షణ",
    "basinSubtitle": "దిగువ గోదావరి బేసిన్ మరియు డెల్టా ప్రాంతం",
    "basinDesc": "21 మండలాల్లోని వరద ముప్పు, రాడార్ పరిశీలనలు మరియు అత్యవసర సహాయ కార్యకలాపాలు.",

    // Section 02 Awareness
    "secAwarenessTitle": "క్షేత్రస్థాయి తాజా పరిస్థితులను తెలుసుకోండి",
    "secAwarenessDesc": "గోదావరి డెల్టా అంతటా ఉపగ్రహ నిఘా, నదీ నీటిమట్టాలు మరియు సామాజిక సహాయ చర్యలు.",
    "activeSurveillance": "క్రియాశీల పర్యావరణ నిఘా",
    "cycloneBannerTitle": "తీవ్ర వాతావరణం మరియు వరద మట్టాల హెచ్చరికలు",
    "cycloneBannerSub": "సెంట్రల్ వాటర్ కమిషన్ మరియు వాతావరణ శాఖ ద్వారా 21 మండలాల్లో నిరంతర పర్యవేక్షణ.",
    
    // Awareness Cards
    "card1Title": "నదీ నీటిమట్టాల పర్యవేక్షణ",
    "card1Desc": "ధవళేశ్వరం బ్యారేజ్ మరియు భద్రాచలం వద్ద సెంట్రల్ వాటర్ కమిషన్ (CWC) ద్వారా ప్రత్యక్ష నీటిమట్టాల పరిశీలన.",
    "card1Link": "నీటిమట్టాలు చూడండి →",
    "card2Title": "తీరప్రాంత తుఫానులు & వాతావరణం",
    "card2Desc": "బంగాళాఖాతంలో అల్పపీడనాలు మరియు తుఫానుల గమనాన్ని ఐఎండి రాడార్ ద్వారా పరిశీలించండి.",
    "card2Link": "వాతావరణ సూచనలు →",
    "card3Title": "భారీ వర్షపాతం హెచ్చరికలు",
    "card3Desc": "గోదావరి పరివాహక ప్రాంతాల్లో ఉపగ్రహ వర్షపాత సమాచారం మరియు ఆకస్మిక వరద ముప్పు అంచనాలు.",
    "card3Link": "వర్షపాత వివరాలు →",
    "card4Title": "సమాజ సంసిద్ధత & పునరావాసం",
    "card4Desc": "21 మండలాల్లోని ఎత్తైన తుఫాను పునరావాస కేంద్రాలు మరియు సురక్షిత తాగునీటి సరఫరా కేంద్రాలు.",
    "card4Link": "పునరావాస కేంద్రాలు →",
    "card5Title": "సహాయక & రెస్క్యూ కార్యకలాపాలు",
    "card5Desc": "ఎన్డీఆర్ఎఫ్ (NDRF), ఎస్డీఆర్ఎఫ్ రక్షణ బోట్ల సంచారం మరియు సురక్షిత తరలింపు మార్గాలు.",
    "card5Link": "రెస్క్యూ సమన్వయం →",

    // Personas Section
    "secPersonasTitle": "అందరికీ ఉపయోగపడే సమీకృత వేదిక",
    "secPersonasDesc": "గ్రామీణ ప్రజలు, మండల అధికారులు మరియు అత్యవసర రక్షణ బృందాలకు అనుగుణమైన ప్రత్యేక డాష్‌బోర్డులు.",
    "roleResidentTitle": "గ్రామీణ ప్రజలు / నివాసితులు",
    "roleResidentDesc": "మీ గ్రామంలోని వరద ప్రమాదం తెలుసుకోండి, సమీప పునరావాస కేంద్రాలు కనుగొనండి మరియు అత్యవసర SOS పంపండి.",
    "roleResidentBtn": "నివాసిగా ప్రారంభించండి →",
    "roleResponseTitle": "అత్యవసర రక్షణ దళాలు (NDRF/SDRF)",
    "roleResponseDesc": "వరదల్లో చిక్కుకున్న ప్రజల జీపీఎస్ లొకేషన్లు, సురక్షిత బోట్ రూట్లు మరియు అత్యవసర తరలింపు సేవలు.",
    "roleResponseBtn": "రక్షణ కేంద్రానికి వెళ్ళండి →",
    "roleMandalTitle": "మండల నిర్వాహకుడు",
    "roleMandalDesc": "గ్రామ స్థాయి పర్యవేక్షణ, సహాయక సామాగ్రి పంపిణీ మరియు పునరావాస కేంద్రాల సమన్వయం.",
    "roleMandalBtn": "మండల కంట్రోల్ రూమ్ →",
    "roleDistrictTitle": "జిల్లా కలెక్టరేట్",
    "roleDistrictDesc": "బేసిన్ స్థాయి వరద ముప్పు విశ్లేషణ, జనాభా లెక్కలు, వనరుల కేటాయింపు మరియు ముందస్తు హెచ్చరికలు.",
    "roleDistrictBtn": "జిల్లా కార్యకలాపాలు →",

    // Authentication: Login
    "signInTitle": "మళ్ళీ స్వాగతం",
    "signInDesc": "మీ పర్యవేక్షణ వర్క్‌స్పేస్ మరియు అత్యవసర కార్యకలాపాలను యాక్సెస్ చేయడానికి సైన్ ఇన్ చేయండి.",
    "emailLabel": "ఈమెయిల్ చిరునామా",
    "passwordLabel": "పాస్‌వర్డ్",
    "rememberMe": "ఈ పరికరంలో నన్ను గుర్తుంచుకో",
    "forgotPassword": "పాస్‌వర్డ్ మర్చిపోయారా?",
    "btnSignInSubmit": "ఖాతాలోకి సైన్ ఇన్ చేయండి →",
    "noAccountText": "ఖాతా లేదా?",
    "createAccountLink": "ఉచిత ఖాతాను సృష్టించండి →",
    "evaluatorPillLabel": "త్వరిత డెమో ఖాతాలు:",

    // Authentication: Registration
    "registerTitle": "మీ ఖాతాను సృష్టించండి",
    "registerDesc": "స్థానిక విపత్తు హెచ్చరికలు మరియు అత్యవసర సహాయం పొందడానికి నివాసిగా నమోదు చేసుకోండి.",
    "fullNameLabel": "పూర్తి పేరు",
    "regEmailLabel": "ఈమెయిల్ చిరునామా",
    "regPasswordLabel": "పాస్‌వర్డ్ (కనీసం 8 అక్షరాలు)",
    "confirmPasswordLabel": "పాస్‌వర్డ్‌ను నిర్ధారించండి",
    "districtLabel": "జిల్లా",
    "mandalLabel": "మండలం",
    "btnRegisterSubmit": "ఖాతాను సృష్టించి కొనసాగించండి →",
    "haveAccountText": "ఇప్పటికే ఖాతా ఉందా?",
    "signInLink": "సైన్ ఇన్ చేయండి →",

    // Role Selection
    "roleSelectTitle": "మీ నిర్వహణ పాత్రను ఎంచుకోండి",
    "roleSelectSub": "గోదావరి బేసిన్ అంతటా నివాసితులు, నిర్వాహకులు మరియు అత్యవసర సహాయకుల కోసం అనుకూలీకరించిన వర్క్‌ఫ్లోలు.",

    // Location Onboarding
    "onboardingTitle": "మీ స్థానాన్ని నిర్ధారించండి",
    "onboardingSub": "ఖచ్చితమైన వరద హెచ్చరికలు మరియు సమీప పునరావాస కేంద్రాల సమాచారం కోసం మీ జిల్లా మరియు మండలాన్ని ఎంచుకోండి.",
    "btnDetectLocation": "నా స్థానాన్ని గుర్తించు",
    "btnSaveOnboarding": "సేవ్ చేసి కొనసాగించండి →",

    // Situation Awareness Home
    "sitHomeTitle": "తాజా పరిస్థితుల సమీక్ష",
    "sitHomeSub": "మీరు ఎంచుకున్న ప్రాంతానికి సంబంధించిన సమగ్ర సమాచారం",
    "btnLaunchExplorer": "వెబ్ జీఐఎస్ మ్యాప్ ప్రారంభించండి",
    "btnLaunchAidConnect": "ఎయిడ్ కనెక్ట్ కార్యకలాపాలు",
    "btnLaunchEvidence": "శాస్త్రీయ పద్ధతులు & ఏఐ",
    "btnLaunchHelp": "అత్యవసర సంసిద్ధత",
    "summaryHeading": "నిర్వహణ అవలోకనం & సమాచారం",

    // Operations & SOS
    "opsTitle": "ఎయిడ్ కనెక్ట్ అత్యవసర కార్యకలాపాలు",
    "sosHeading": "తక్షణ రక్షణ సహాయం (SOS)",
    "sosDesc": "మీరు వరద నీటిలో చిక్కుకుంటే లేదా రోడ్డు తెగిపోతే, వెంటనే అత్యవసర హెచ్చరికను పంపండి.",
    "btnSendSos": "అత్యవసర రక్షణను అభ్యర్థించండి (SOS)",

    // Ground Hazard Reporting
    "hazardReportTitle": "క్షేత్రస్థాయి ప్రమాద & ముంపు నివేదిక",
    "hazardReportDesc": "ముంపునకు గురైన రహదారులు, తెగిపోయిన కట్టలు లేదా సహాయం అవసరమైన ప్రాంతాల ఫోటోలు పంపండి. రక్షణ దళాల ద్వారా ధృవీకరించబడుతుంది.",
    "hazardMandalLabel": "మండలం ఎంచుకోండి",
    "hazardTypeLabel": "ప్రమాద రకం",
    "hazardLandmarkLabel": "ముఖ్యమైన ప్రదేశం / స్థానిక పేరు",
    "hazardDescLabel": "పూర్తి వివరాలు",
    "hazardPhotoLabel": "క్షేత్రస్థాయి ఫోటో (ఐచ్ఛికం)",
    "btnSubmitHazard": "ప్రమాద నివేదికను సమర్పించండి",
    "recentObservationsTitle": "ఇటీవల ధృవీకరించబడిన క్షేత్ర నివేదికలు",

    // Helplines Section
    "helplineTitle": "ఆంధ్రప్రదేశ్ అత్యవసర అధికారిక హెల్ప్‌లైన్లు",
    "helplineSub": "24 గంటలూ అందుబాటులో ఉండే ఉచిత విపత్తు కంట్రోల్ రూమ్ నంబర్లు.",
    "helplineSdma": "ఆంధ్రప్రదేశ్ విపత్తు నిర్వహణ సంస్థ (AP SDMA)",
    "helplineNational": "జాతీయ అత్యవసర స్పందన విభాగం",
    "helplineMedical": "వైద్య మరియు అంబులెన్స్ సేవలు",
    "helplineDistrict": "జిల్లా కలెక్టరేట్ కంట్రోల్ రూమ్",

    // Voice Assistant
    "voiceAssistantTitle": "ప్రవాహ్ 360 వాయిస్ అసిస్టెంట్",
    "voiceListeningPrompt": "వింటున్నాము... తెలుగు లేదా ఆంగ్లంలో సహజంగా మాట్లాడండి",
    "voiceInputPlaceholder": "మైక్రోఫోన్ లేకపోతే మీ ప్రశ్నను ఇక్కడ టైప్ చేయండి...",
    "btnSendVoiceQuery": "అడగండి",
    "voicePromptRain": "వర్షం పడుతుందా? (Is it raining?)",
    "voicePromptWeather": "ఈరోజు వాతావరణం ఎలా ఉంది? (Today's Weather)",
    "voicePromptFlood": "మా ప్రాంతంలో వరద ప్రమాదం ఉందా? (Flood Risk)",
    "voicePromptHospital": "దగ్గరలో ఆసుపత్రి ఎక్కడ ఉంది? (Nearest Hospital)",
    "voicePromptShelter": "పునరావాస కేంద్రం ఎక్కడ ఉంది? (Shelter)",
    "voicePromptHelpline": "అత్యవసర నంబర్లు (Helplines)",
    "voicePromptHelp": "సహాయం కావాలి (Need Help / SOS)",
    "btnReplayVoice": "🔄 మళ్ళీ వినండి"
  }
};
`;

fs.writeFileSync('frontend/translations.js', tr, 'utf8');
console.log('SUCCESS: frontend/translations.js updated with complete bilingual dictionary');
