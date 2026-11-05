# PRAVAH 360: TELUGU TRANSLATION & LOCALIZATION COMPLETENESS REPORT

**Document ID:** `DOC-P360-TELUGU-2026-V1`  
**Focus Area:** Vernacular Accessibility, Multi-lingual Architecture, Bidirectional Language Switching, Local Dialect Appropriateness for Andhra Pradesh Godavari Delta.  
**Audience:** Academic Evaluators, Civil Defense Officers, Field Volunteers, Gram Panchayat Representatives.

---

## 1. Executive Summary & Purpose

In disaster management, language barrier is a critical vulnerability. The Godavari river delta (Konaseema, East Godavari, and West Godavari districts) encompasses hundreds of river island (*lanka*) villages, coastal fishermen hamlets, and agricultural communities where English literacy is limited. An emergency warning system that operates solely in English fails at the point of greatest need.

PRAVAH 360 incorporates native, end-to-end **Telugu (తెలుగు) localization** alongside English. Unlike generic automated widget translations (e.g., Google Translate widgets that break layouts or mangle disaster terminology), PRAVAH 360 utilizes a curated, domain-specific terminology dictionary implemented in [`frontend/translations.js`](file:///c:/major%20project/frontend/translations.js).

---

## 2. Terminology Dictionary & Dialect Standardization

Disaster terminology requires precise distinction between *forecast*, *warning*, *evacuation*, and *relief*. Below is the standardized Telugu lexicon implemented in PRAVAH 360:

| English Term | Standard Telugu Translation | Transliteration | Contextual Application in PRAVAH 360 |
| :--- | :--- | :--- | :--- |
| **PRAVAH 360** | ప్రవాహ్ 360 | Pravah 360 | Core brand identity (*ప్రవాహం* - Flow / Current) |
| **See the risk. Stay prepared.** | ప్రమాదాన్ని గుర్తించండి. సిద్ధంగా ఉండండి. | Pramadanni gurtinchandi. Siddhange undandi. | Landing page hero slogan |
| **Situational Awareness** | తాజా పరిస్థితుల సమీక్ష | Taja paristhitula sameeksha | Real-time environmental and weather assessment |
| **Flood Warning / Inundation** | వరద హెచ్చరిక మరియు ముంపు | Varada hechharika mariyu mumpu | Riverine and backwater flood alerts |
| **Evacuation Center / Relief Camp** | పునరావాస కేంద్రం | Punaravasa kendram | Designated cyclone / flood shelter |
| **Safe Drinking Water** | సురక్షిత తాగునీరు | Surakshita taguneeru | Water tanker and purification point availability |
| **Emergency Helplines** | అత్యవసర హెల్ప్‌లైన్లు | Atyavasara helplines | 1070 (SDMA), 112, 108 medical response numbers |
| **Ground Hazard Report** | క్షేత్రస్థాయి ప్రమాద నివేదిక | Kshetrasthayi pramada nivedika | Citizen hazard observation and photo upload |
| **Water Level Monitoring** | నదీ నీటిమట్టాల పర్యవేక్షణ | Nadi neetimattala paryavekshana | CWC / Sir Arthur Cotton Barrage gauge readings |
| **Vulnerable Population** | ముంపునకు గురయ్యే ప్రజలు | Mumpunaku gurayye prajalu | WorldPop demographic exposure categorization |
| **Response Teams / NDRF** | సహాయక బృందాలు | Sahayaka brundalu | Disaster response and relief personnel |
| **Voice Assistant** | వాయిస్ అసిస్టెంట్ | Voice Assistant | Speech-driven interaction module |

---

## 3. UI Scope & Component Coverage Matrix

The Telugu localization engine covers every public-facing and community-accessible surface of the application:

| Surface Component | Key Translated Elements | Translation Key Namespace | Status |
| :--- | :--- | :--- | :--- |
| **Top Navigation Bar** | Welcome, Overview, GIS Explorer, Sign In / Profile, Language Toggle | `nav_*` | Fully Verified |
| **Hero Section** | Slogan, Sub-headline, Mission statement, Action CTA buttons | `hero_*` | Fully Verified |
| **Situation Awareness Cards** | River flood, Coastal storm, Extreme rainfall, Shelter operations, Evacuation boat | `card_*` | Fully Verified |
| **Role Selection Personas** | Resident/Citizen, District Administrator, Response Team | `role_*` | Fully Verified |
| **Ground Hazard Portal** | Form fields (Hazard type, Location, Landmark, Phone, Photo prompt), Submit CTA | `hazard_*` | Fully Verified |
| **Emergency Helplines Bar** | Andhra Pradesh SDMA, Disaster Control, Fire, Ambulance, Police labels | `helpline_*` | Fully Verified |
| **Voice Assistant Interface** | Voice status, Prompt hint, Response dialog, Speech synthesis output | `voice_*` | Fully Verified |
| **Authentication Headers** | Sign In, Register, Back to Welcome, Role indicator | `auth_*` | Fully Verified |

---

## 4. Typography & Font Rendering Architecture

Telugu script is an Indic abugida with complex conjunct characters (వత్తులు - *vattulu* and గుణింతాలు - *guninthalu*). Improper web font rendering leads to character clipping, missing vowel markers, or fallback to generic system fonts.

To guarantee crisp typographical fidelity across devices:
1. **Google Font Integration:** Loaded **Google Noto Sans Telugu** (`weights: 400, 500, 600, 700`) directly in [`frontend/index.html`](file:///c:/major%20project/frontend/index.html).
2. **CSS Font Cascade:** Configured in [`frontend/entry_journey.css`](file:///c:/major%20project/frontend/entry_journey.css):
   ```css
   body[data-lang="te"] {
     font-family: 'Noto Sans Telugu', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
     line-height: 1.65; /* Increased line-height prevents diacritic clipping */
   }
   ```
3. **Dynamic Font Sizing:** Telugu characters are visually denser than Latin characters. The layout utilizes fluid clamp sizing and flexible vertical rhythm so multi-syllable Telugu words fit buttons without overflow.

---

## 5. Bidirectional State Management

Language switching is instantaneous and does not trigger a full page reload or drop existing form state:
1. **User Action:** The user clicks the `🌐 EN / తె` button in the top header or selects language during onboarding.
2. **State Propagation:** `window.setAppLanguage('te')` is dispatched.
3. **DOM Traversal:** Elements tagged with `data-i18n="<key>"` or `data-i18n-placeholder="<key>"` are queried and mapped against `PRAVAH_TRANSLATIONS[lang]`.
4. **Speech Engine Synchronization:** The Web Speech API recognition and synthesis engine (`voice_assistant.js`) automatically rebinds its language code from `en-US` to `te-IN`, ensuring vocal input and synthesized audio output match the visual UI.
5. **Persistence:** The user's selection is stored in `localStorage.getItem('pravah_lang')` and restored on subsequent visits.

---

## 6. Evaluation Defense & Academic Justification

When evaluators inquire about the Telugu localization:
- **"Is this just a Google Translate overlay?"**  
  *No.* Google Translate plugins inject external iframes, suffer from network latency, break responsive layouts, and mistranslate technical hydrological concepts (e.g., translating "gauge discharge" into generic "measurement firing"). PRAVAH 360 uses a curated, hardcoded translation dictionary designed specifically for the Godavari disaster administration context.
- **"How does this support illiterate rural citizens?"**  
  For citizens who cannot read Telugu script, the Telugu Voice Assistant (`te-IN`) listens to spoken queries and provides audio responses in natural Telugu speech, bridging both textual and literacy divides.
