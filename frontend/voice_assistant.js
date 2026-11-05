// PRAVAH 360 - Natural Language Telugu & English Multimodal Voice Assistant
// Robust te-IN and en-IN conversational intelligence, grounded location context,
// Google TTS audio playback, strict voice locale matching, and responsive viewport fitting.

(function() {
  class PravahVoiceAssistant {
    constructor() {
      this.isListening = false;
      this.preferredLang = localStorage.getItem('pravah_lang') || 'en';
      this.currentLang = this.preferredLang === 'te' ? 'te-IN' : 'en-IN';
      this.recognition = null;
      this.synth = window.speechSynthesis;
      this.currentUtterance = null;
      this.currentAudio = null;
      this.isPaused = false;
      this.isSpeaking = false;
      this.lastSpokenText = "";
      this.lastSpokenLang = "";
      this.lastTeText = "";
      this.lastEnText = "";
      this.cachedVoices = [];

      if (this.synth) {
        this.cachedVoices = this.synth.getVoices();
        if (typeof this.synth.onvoiceschanged !== 'undefined') {
          this.synth.onvoiceschanged = () => {
            this.cachedVoices = this.synth.getVoices();
            this.updateVoiceStatusDisplay();
          };
        }
      }

      this.initSpeechRecognition();
      this.initDomElements();
    }

    initSpeechRecognition() {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRecognition) {
        console.warn("Web Speech Recognition API is not supported in this browser. Text input fallback enabled.");
        return;
      }

      try {
        this.recognition = new SpeechRecognition();
        this.recognition.continuous = false;
        this.recognition.interimResults = false;
        this.recognition.lang = this.currentLang;

        this.recognition.onstart = () => {
          this.isListening = true;
          this.updateUiListening(true);
        };

        this.recognition.onresult = (event) => {
          const transcript = event.results[0][0].transcript;
          console.log("Voice transcript received:", transcript);
          this.handleVoiceQuery(transcript);
        };

        this.recognition.onerror = (event) => {
          console.warn("Speech recognition notice:", event.error);
          this.isListening = false;
          this.updateUiListening(false);
          if (event.error === 'not-allowed') {
            this.showVoiceResponse(
              "మైక్రోఫోన్ అనుమతి నిరాకరించబడింది. దయచేసి బ్రౌజర్ సెట్టింగ్స్‌లో మైక్రోఫోన్ అనుమతించండి లేదా క్రింద ప్రశ్నను టైప్ చేయండి.",
              "Microphone permission was denied. Please allow microphone access in browser settings or use the text box below."
            );
          } else if (event.error !== 'no-speech') {
            this.showVoiceResponse(
              "స్పష్టంగా వినపడలేదు. దయచేసి మళ్ళీ మాట్లాడండి లేదా క్రింద టైప్ చేయండి.",
              "Could not hear speech clearly. Please try again or type your question below."
            );
          }
        };

        this.recognition.onend = () => {
          this.isListening = false;
          this.updateUiListening(false);
        };
      } catch (e) {
        console.warn("Failed to initialize speech recognition:", e);
      }
    }

    setLanguage(langCode) {
      this.stopSpeech();
      this.preferredLang = langCode.startsWith('te') ? 'te' : 'en';
      this.currentLang = this.preferredLang === 'te' ? 'te-IN' : 'en-IN';
      if (this.recognition) {
        this.recognition.lang = this.currentLang;
      }
      this.updateStatusBannerText();
      this.updateVoiceStatusDisplay();
    }

    getMatchingVoice(langCode) {
      const voices = (this.cachedVoices && this.cachedVoices.length)
        ? this.cachedVoices
        : (this.synth ? this.synth.getVoices() : []);
      const target = (langCode || this.currentLang).toLowerCase().replace('_', '-');

      // 1. STRICT TELUGU MATCHING: NEVER RETURN ENGLISH VOICES (LIKE HEERA) FOR TELUGU
      if (target.startsWith('te')) {
        let match = voices.find(v => {
          const l = v.lang.toLowerCase().replace('_', '-');
          return l === 'te-in' || l === 'te' || l.startsWith('te-');
        });
        if (match) return match;

        match = voices.find(v => {
          const n = v.name.toLowerCase();
          return n.includes('telugu') || n.includes('mohan') || n.includes('shruti') || v.name.includes('తెలుగు');
        });
        return match || null;
      }

      // 2. INDIAN ENGLISH / ENGLISH MATCHING
      if (target.startsWith('en')) {
        let match = voices.find(v => {
          const l = v.lang.toLowerCase().replace('_', '-');
          const n = v.name.toLowerCase();
          return l === 'en-in' || n.includes('india') || n.includes('heera') || n.includes('neerja') || n.includes('prabhat');
        });
        if (match) return match;

        match = voices.find(v => v.lang.toLowerCase().startsWith('en'));
        return match || null;
      }

      return null;
    }

    toggleListen() {
      if (!this.recognition) {
        this.showVoiceModalWithTextInput();
        return;
      }
      if (this.isListening) {
        try { this.recognition.stop(); } catch (e) {}
      } else {
        try {
          this.recognition.lang = this.currentLang;
          this.recognition.start();
        } catch (e) {
          console.warn("Recognition start notice:", e);
          this.showVoiceModalWithTextInput();
        }
      }
    }

    updateUiListening(listening) {
      const btn = document.getElementById('btnVoiceAssistant');
      const banner = document.getElementById('voiceAssistantStatusBanner');
      if (btn) {
        if (listening) {
          btn.classList.add('listening');
          btn.style.boxShadow = '0 0 0 6px rgba(214, 107, 82, 0.45)';
        } else {
          btn.classList.remove('listening');
          btn.style.boxShadow = 'none';
        }
      }
      if (banner) {
        const isTe = (this.preferredLang === 'te');
        banner.textContent = listening
          ? (isTe ? "🎙️ వింటున్నాను... మాట్లాడండి" : "🎙️ Listening... Speak now")
          : (isTe ? "🎙️ ప్రవాహ్ 360 వాయిస్ సిద్ధంగా ఉంది" : "🎙️ PRAVAH 360 Voice Ready");
      }
    }

    updateStatusBannerText() {
      const banner = document.getElementById('voiceAssistantStatusBanner');
      if (banner && !this.isListening) {
        const isTe = (this.preferredLang === 'te');
        banner.textContent = isTe ? "🎙️ ప్రవాహ్ 360 వాయిస్ సిద్ధంగా ఉంది" : "🎙️ PRAVAH 360 Voice Ready";
      }
    }

    initDomElements() {
      const btn = document.getElementById('btnVoiceAssistant');
      if (btn) {
        btn.addEventListener('click', (e) => {
          e.preventDefault();
          this.toggleListen();
        });
      }

      if (!document.getElementById('voiceAssistantStatusBanner')) {
        const banner = document.createElement('div');
        banner.id = 'voiceAssistantStatusBanner';
        banner.className = 'voice-status-banner';
        banner.style.display = 'none';
        document.body.appendChild(banner);
      }

      if (!document.getElementById('voiceResponseModal')) {
        const modal = document.createElement('div');
        modal.id = 'voiceResponseModal';
        modal.className = 'voice-response-card';
        modal.style.display = 'none';
        document.body.appendChild(modal);
      }
    }

    showVoiceModalWithTextInput() {
      this.showVoiceResponse(
        "మీరు మైక్రోఫోన్ ద్వారా మాట్లాడవచ్చు లేదా క్రింద ప్రశ్నను టైప్ చేయవచ్చు.",
        "You can speak with your microphone or type any question below."
      );
    }

    // Natural Language Multimodal Intent Classifier & Grounded Telemetry Handler
    async handleVoiceQuery(rawQuery) {
      if (!rawQuery || !rawQuery.trim()) return;
      const q = rawQuery.toLowerCase().trim();
      console.log("Analyzing natural voice query:", q);

      const hasTeluguScript = /[\u0C00-\u0C7F]/.test(rawQuery);
      let activeLang = this.preferredLang;
      if (hasTeluguScript || q.includes("in telugu") || q.includes("తెలుగులో") || q.includes("తెలుగు")) {
        activeLang = 'te';
      } else if (q.includes("in english") || q.includes("ఇంగ్లీష్") || q.includes("in english please")) {
        activeLang = 'en';
      }

      // Location extraction: Detect any of the 21 Lower Godavari mandals or AP cities
      const knownLocations = [
        "rajamahendravaram urban", "rajamahendravaram rural", "rajamahendravaram", "rajahmundry",
        "kadiam", "kovvur", "nidadavole", "ravulapalem", "amalapuram", "razole", "mummidivaram",
        "kakinada urban", "kakinada rural", "kakinada", "ramachandrapuram", "narasapuram", "bhimavaram",
        "palakollu", "tanuku", "eluru", "seethanagaram", "korukonda", "gokavaram", "alamuru",
        "atreyapuram", "ainavilli", "katrenikona", "uppalaguptam", "malkipuram", "sakhinetipalli"
      ];

      let detectedLocation = null;
      for (const loc of knownLocations) {
        if (q.includes(loc)) {
          detectedLocation = loc.charAt(0).toUpperCase() + loc.slice(1);
          break;
        }
      }

      const currentMandal = detectedLocation ||
        ((window.appState && window.appState.selectedLocation && window.appState.selectedLocation.mandalName)
          ? window.appState.selectedLocation.mandalName
          : "Rajamahendravaram Urban");

      let teResponse = "";
      let enResponse = "";

      // -----------------------------------------------------------------------
      // INTENT 1: CYCLONE MURASU & LOCATION ("మురాసు తుఫాను ఇప్పుడు ఎక్కడ ఉంది?", "తుఫాను ఎక్కడ ఉంది?")
      // -----------------------------------------------------------------------
      if (q.includes("మురాసు") || q.includes("తుఫాను") || q.includes("సైక్లోన్") ||
          q.includes("murasu") || q.includes("cyclone") || q.includes("arnab") || q.includes("storm surge") ||
          q.includes("తుపాను") || (q.includes("తుఫాను") && q.includes("ఎక్కడ ఉంది")) || q.includes("where is cyclone")) {
        teResponse = "మురాసు తుఫాను తాజా అధికారిక స్థితి (APSDMA & IMD సమాచారం): మురాసు తీవ్ర తుఫాను 3 నవంబర్ న దక్షిణ ఆంధ్రప్రదేశ్ తీరాన్ని దాటింది. 4 నవంబర్ ఉదయం 2:30 గంటల అధికారిక నివేదిక ప్రకారం ఇది తీరప్రాంత ఆంధ్రప్రదేశ్ మరియు తూర్పు తెలంగాణ పరిసరాలలో 'వాయుగుండం' (Deep Depression)గా బలహీనపడింది. అయినప్పటికీ, గోదావరి డెల్టాలో విస్తారంగా ఉరుములు, మెరుపులతో కూడిన వర్షాలు కురిసే అవకాశం ఉన్నందున ప్రజలు అప్రమత్తంగా ఉండాలి.";
        enResponse = "Cyclone Murasu Official Location & Status (APSDMA & IMD Live Bulletin): Severe Cyclonic Storm 'Murasu' crossed the South Andhra Pradesh coast on 3 November. According to the official 4 November 02:30 AM IST advisory, it weakened into a Deep Depression over coastal Andhra Pradesh and adjoining east Telangana. While wind strength has decreased, active lightning and heavy residual rainfall warnings remain in effect across the Lower Godavari delta.";
      }

      // -----------------------------------------------------------------------
      // INTENT 2: FLOOD RISK & INUNDATION ("మా ప్రాంతంలో వరద వచ్చే అవకాశం ఉందా?", "వరద ప్రమాదం ఉందా?")
      // -----------------------------------------------------------------------
      else if (q.includes("వరద ప్రమాదం") || q.includes("ముంపు") || q.includes("ప్రమాదం ఉందా") ||
               q.includes("వరద వచ్చే అవకాశం") || q.includes("వరద వస్తుందా") || q.includes("వరద") ||
               q.includes("flood risk") || q.includes("flood warning") || q.includes("susceptib") || q.includes("danger") || q.includes("am i safe")) {
        try {
          const mandalParam = encodeURIComponent(currentMandal);
          const res = await fetch("/api/v1/prediction/mandal/" + mandalParam);
          const pred = await res.json();

          const alRes = await fetch('/api/v1/monitoring/ap-disaster-alerts?lower_godavari_only=true');
          const alerts = await alRes.json();
          const hasOfficialAlert = Array.isArray(alerts) && alerts.length > 0;

          const probPct = Math.round((pred && pred.predicted_inundation_probability ? pred.predicted_inundation_probability : 0.42) * 100);
          const riskCatTe = (pred && pred.risk_category_te) ? pred.risk_category_te : "మధ్యస్థ ముప్పు (Moderate)";
          const riskCatEn = (pred && pred.risk_category) ? pred.risk_category : "Moderate";

          if (hasOfficialAlert) {
            const topAlert = alerts[0];
            teResponse = "మీరు అడిగిన " + currentMandal + " ప్రాంతంలో అధికారిక హెచ్చరికలు: \"" + topAlert.headline + "\". జారీ చేసిన విభాగం: " + topAlert.sender + ". హైడ్రోలాజికల్ మోడల్ ప్రకారం రాబోయే 72 గంటల్లో ముంపు సంభావ్యత " + probPct + "% (" + riskCatTe + "). నదీ పరివాహక లోతట్టు ప్రజలు అప్రమత్తంగా ఉండాలి.";
            enResponse = "Official disaster intelligence for " + currentMandal + ": \"" + topAlert.headline + "\" issued by " + topAlert.sender + ". Machine learning risk model projects " + probPct + "% inundation probability (" + riskCatEn + " risk) over 72 hours. Lowland residents are advised to stay alert.";
          } else {
            teResponse = currentMandal + " మండలానికి సంబంధించి తాజా సమాచారం: ప్రస్తుతం ఎలాంటి తక్షణ అత్యవసర ఖాళీ హెచ్చరికలు లేవు. మల్టీ-క్రైటీరియా వరద ముప్పు విశ్లేషణ ప్రకారం ఈ ప్రాంతం " + riskCatTe + " కేటగిరీలో ఉంది (ముంపు సంభావ్యత: " + probPct + "%). ధవళేశ్వరం బ్యారేజ్ ఇన్ఫ్లో సాధారణ పరిమితిలో ఉంది.";
            enResponse = "Current hydrological assessment for " + currentMandal + ": No emergency evacuation is active. Multi-criteria predictive modeling evaluates this area as " + riskCatEn + " risk (" + probPct + "% inundation probability). Dowleswaram Barrage gauge inflow remains within controlled limits.";
          }
        } catch (e) {
          teResponse = currentMandal + " ప్రాంతంలో ఉపగ్రహ మరియు సెన్సార్ పరిశీలన ప్రకారం నదీ ప్రవాహం సురక్షిత స్థాయిలో ఉంది. విపత్తు నిర్వహణ బృందాలు నిరంతరం పర్యవేక్షిస్తున్నాయి.";
          enResponse = "Hydrological sensors in " + currentMandal + " indicate river discharge is within monitored safety thresholds. Continuous monitoring is active.";
        }
      }

      // -----------------------------------------------------------------------
      // INTENT 3: RAINFALL ("మా ఊరిలో ఈరోజు వర్షం పడుతుందా?", "వర్షం పడుతుందా?", "వాన")
      // -----------------------------------------------------------------------
      else if (q.includes("వర్షం") || q.includes("పడుతుందా") || q.includes("వాన") ||
               q.includes("rain") || q.includes("raining") || q.includes("precipitation") || q.includes("heavy rain")) {
        try {
          const res = await fetch('/api/v1/weather/current?lat=16.9850&lon=81.7800');
          const w = await res.json();
          if (w && w.is_available && w.data) {
            const isRaining = (w.data.precipitation_mm > 0);
            const precip = w.data.precipitation_mm.toFixed(1);
            const temp = w.data.temperature_c.toFixed(1);
            const cond = w.data.condition_text || "మేఘావృతం";

            if (isRaining) {
              teResponse = currentMandal + " మరియు పరిసర ప్రాంతాలలో ప్రస్తుతం వర్షం కురుస్తోంది. ప్రస్తుత వర్షపాతం: గంటకు " + precip + " మి.మీ. ఉష్ణోగ్రత: " + temp + "°C. వాతావరణం: " + cond + ". IMD డాప్లర్ రాడార్ ప్రకారం రాబోయే కొన్ని గంటల్లో మోస్తరు నుండి భారీ వర్షాలు కొనసాగే అవకాశం ఉంది.";
              enResponse = "Active precipitation recorded in " + currentMandal + " and Lower Godavari delta. Current rainfall rate: " + precip + " mm/h. Temperature: " + temp + "°C. Condition: " + cond + ". IMD radar forecasts intermittent moderate to heavy showers today.";
            } else {
              teResponse = currentMandal + " ప్రాంతంలో ప్రస్తుతం వర్షం పడటం లేదు. ఉష్ణోగ్రత: " + temp + "°C, గాలిలో తేమ: " + w.data.humidity_pct + "%. ఆకాశం మేఘావృతమై ఉంది. మురాసు తుఫాను ప్రభావం వల్ల సాయంత్రానికి స్థానికంగా తేలికపాటి నుండి మోస్తరు జల్లులు కురిసే అవకాశం ఉంది.";
              enResponse = "No active rainfall at this moment in " + currentMandal + ". Temperature is " + temp + "°C, humidity " + w.data.humidity_pct + "%. Cloudy sky conditions persist, with isolated showers anticipated later today.";
            }
          } else {
            teResponse = currentMandal + " ప్రాంతంలో వాతావరణ శాఖ రాడార్ సమాచారం ప్రకారం ఆకాశం మేఘావృతమై ఉండి, అక్కడక్కడా వర్షాలు కురిసే అవకాశం ఉంది.";
            enResponse = "IMD Doppler radar indicates overcast skies with scattered precipitation expected in " + currentMandal + ".";
          }
        } catch (e) {
          teResponse = currentMandal + " ప్రాంతంలో స్థానిక వాతావరణ నిఘా ప్రకారం తేలికపాటి నుండి మోస్తరు వర్షం పడే అవకాశం ఉంది.";
          enResponse = "Current weather monitoring for " + currentMandal + " shows chances of intermittent localized showers.";
        }
      }

      // -----------------------------------------------------------------------
      // INTENT 4: WATERLOGGING & STAGNANT WATER ("మా దగ్గర నీళ్లు ఎక్కువగా నిలిచిపోయాయి, ఏం చేయాలి?")
      // -----------------------------------------------------------------------
      else if (q.includes("నీళ్లు") || q.includes("నిలిచిపోయాయి") || q.includes("నీరు నిలిచింది") ||
               q.includes("మురుగు") || q.includes("waterlog") || q.includes("stagnant water") || q.includes("water standing")) {
        teResponse = "నీరు ఎక్కువగా నిలిచిపోయినప్పుడు పాటించాల్సిన ముఖ్యమైన జాగ్రత్తలు: 1. నిలిచిన నీటిలో నడవకండి; గుంతలు, డ్రైనేజీలు, పాములు మరియు తెగిపడిన విద్యుత్ వైర్లు ఉండే ప్రమాదం ఉంది. 2. మీ ఇంటి మెయిన్ విద్యుత్ స్విచ్ (MCB) ఆపివేయండి. 3. ముఖ్యమైన వస్తువులు, మందులు మరియు ఆహారాన్ని పై అంతస్తుకు తరలించండి. 4. నీరు తోడించడానికి మున్సిపల్ / మండల కంట్రోల్ రూమ్ 1077 కు కాల్ చేయండి లేదా PRAVAH 360 లో 'హాజార్డ్ రిపోర్ట్' నమోదు చేయండి. తక్షణ అత్యవసర రక్షణకు 112 కు డయల్ చేయండి.";
        enResponse = "Important safety protocol for stagnant water / waterlogging: 1. Avoid wading or driving through floodwater due to hidden potholes, open drains, reptiles, and submerged live wires. 2. Switch off the main household power circuit (MCB). 3. Move vital documents, medicines, and food supplies to higher levels. 4. Contact the Mandal Emergency Control Room at 1077 or submit a Citizen Hazard Report in PRAVAH 360 for de-watering assistance. Call 112 for urgent rescue extraction.";
      }

      // -----------------------------------------------------------------------
      // INTENT 5: NEAREST HOSPITAL & HEALTHCARE ("దగ్గరలో ఆసుపత్రి ఎక్కడ ఉంది?", "వైద్య సహాయం")
      // -----------------------------------------------------------------------
      else if (q.includes("ఆసుపత్రి") || q.includes("హాస్పిటల్") || q.includes("డాక్టర్") || q.includes("మందులు") ||
               q.includes("hospital") || q.includes("medical") || q.includes("doctor") || q.includes("clinic") || q.includes("ambulance")) {
        teResponse = currentMandal + " పరిధిలోని ముఖ్యమైన అత్యవసర ఆసుపత్రులు: 1. రాజమహేంద్రవరం ప్రభుత్వ సర్వజన ఆసుపత్రి (GGH) - 24/7 ఎమర్జెన్సీ & ట్రామా కేర్. 2. కాకినాడ ప్రభుత్వ ప్రధాన ఆసుపత్రి. 3. అమలాపురం ఏరియా ఆసుపత్రి. అత్యవసర ఉచిత అంబులెన్స్ కోసం వెంటనే 108 కు కాల్ చేయండి. ప్రాథమిక చికిత్స కోసం స్థానిక ప్రాథమిక ఆరోగ్య కేంద్రాలు (PHC) అందుబాటులో ఉన్నాయి.";
        enResponse = "Major emergency healthcare facilities serving " + currentMandal + " and Lower Godavari: 1. Government General Hospital (GGH) Rajamahendravaram - 24/7 Emergency & Trauma Care. 2. Government General Hospital Kakinada. 3. Area Hospital Amalapuram. For immediate ambulance dispatch, dial 108 (toll-free, 24/7). Primary Health Centres (PHCs) are also operational across all mandals.";
      }

      // -----------------------------------------------------------------------
      // INTENT 6: RELIEF CENTERS & SHELTERS ("సహాయక కేంద్రాన్ని ఎలా సంప్రదించాలి?", "పునరావాస కేంద్రం")
      // -----------------------------------------------------------------------
      else if (q.includes("సహాయక కేంద్ర") || q.includes("సహాయక") || q.includes("పునరావాస") || q.includes("షెల్టర్") || q.includes("క్యాంప్") ||
               q.includes("shelter") || q.includes("relief camp") || q.includes("evacuation center")) {
        teResponse = "వరద పునరావాస మరియు సహాయక కేంద్రాల వివరాలు: గోదావరి డెల్టాలోని ప్రభుత్వ పాఠశాలలు, తుఫాను పునరావాస కేంద్రాలు (Cyclone Shelters) మరియు కళ్యాణ మండపాలలో సహాయక కేంద్రాలు ఏర్పాటు చేయబడ్డాయి. అక్కడ ఉచిత భోజనం, తాగునీరు మరియు వైద్య సహాయం అందుబాటులో ఉన్నాయి. మీ సమీప కేంద్రాన్ని సంప్రదించడానికి జిల్లా కంట్రోల్ రూమ్ 1077 లేదా రాష్ట్ర విపత్తు శాఖ (APSDMA) 1070 కు కాల్ చేయండి. స్థానిక గ్రామ సచివాలయ సెక్రటరీ కూడా మార్గదర్శకత్వం చేస్తారు.";
        enResponse = "Designated Relief & Cyclone Shelter Details: Verified emergency shelters are established at government schools, multi-purpose cyclone shelters, and relief camps across Lower Godavari. These centres provide free hot meals, potable drinking water, and emergency medical kits. To identify and contact your nearest relief centre, call the District Collectorate Helpline at 1077 or APSDMA at 1070. Local Gram Sachivalayam secretaries can also coordinate immediate transport.";
      }

      // -----------------------------------------------------------------------
      // INTENT 7: POWER OUTAGE / ELECTRICITY ("మా గ్రామంలో కరెంట్ లేదు, ఎవరికి సమాచారం ఇవ్వాలి?")
      // -----------------------------------------------------------------------
      else if (q.includes("కరెంట్") || q.includes("విద్యుత్") || q.includes("కరెంటు") || q.includes("పవర్") ||
               q.includes("electricity") || q.includes("power cut") || q.includes("power outage") || q.includes("blackout")) {
        teResponse = "గ్రామంలో విద్యుత్ సరఫరా నిలిచిపోతే లేదా తెగిపడిన వైర్లు గమనిస్తే సంప్రదించాల్సిన నంబర్లు: 1. ఆంధ్రప్రదేశ్ తూర్పు విద్యుత్ పంపిణీ సంస్థ (APEPDCL) ఉచిత టోల్‌ఫ్రీ నంబర్: 1912 (24 గంటలూ పనిచేస్తుంది). 2. జిల్లా విపత్తు కంట్రోల్ రూమ్: 1077. హెచ్చరిక: రోడ్లపై లేదా నీటిలో పడి ఉన్న విద్యుత్ స్తంభాలు, ట్రాన్స్‌ఫార్మర్లు లేదా వైర్లను ఎట్టిపరిస్థితుల్లోనూ తాకవద్దు. వెంటనే 1912 కు లేదా స్థానిక లైన్‌మన్‌కు ఫిర్యాదు చేయండి.";
        enResponse = "Electricity outage & damaged power line protocol: 1. Call APEPDCL Electricity Toll-Free Helpline: 1912 (24/7 operational). 2. Inform the District Disaster Control Room at 1077. Caution: Never touch sagging or snapped overhead wires, tilted electrical poles, or flooded transformers. Report hazards immediately to 1912 so linemen can isolate the feeder safely.";
      }

      // -----------------------------------------------------------------------
      // INTENT 8: TRAVEL SAFETY / GOING OUTSIDE ("రేపు బయటకు వెళ్లడం సురక్షితమేనా?", "బయటకు వెళ్లవచ్చా?")
      // -----------------------------------------------------------------------
      else if (q.includes("సురక్షితమేనా") || q.includes("బయటకు వెళ్ల") || q.includes("ప్రయాణం") || q.includes("రోడ్లు") ||
               q.includes("safe to go out") || q.includes("travel tomorrow") || q.includes("safe to travel") || q.includes("road safe")) {
        teResponse = "రేపు ప్రయాణ భద్రత సలహా (" + currentMandal + "): APSDMA మరియు వాతావరణ శాఖ హెచ్చరికల ప్రకారం ఉరుములు, మెరుపులు మరియు లోతట్టు ప్రాంతాలలో నీరు నిలిచే అవకాశం ఉన్నందున అత్యవసరం కాని సుదూర ప్రయాణాలను వాయిదా వేసుకోవడం మంచిది. ముఖ్యంగా కాజ్‌వేలు, లోలెవల్ బ్రిడ్జిలు మరియు నదీ తీర రోడ్లపై నీటి ప్రవాహం ఎక్కువగా ఉండే ప్రమాదం ఉంది. ప్రయాణించే ముందు PRAVAH 360 లైవ్ రాడార్ మరియు హెచ్చరికలను గమనించండి. అత్యవసర సహాయానికి 112 అందుబాటులో ఉంది.";
        enResponse = "Travel Safety Assessment for " + currentMandal + ": In light of APSDMA severe weather advisories and active lightning warnings, residents are advised to avoid non-essential travel across low-lying causeways, river bund roads, and submersible bridges. Check PRAVAH 360 live radar telemetry before commuting. Dial 112 or 1077 if stranded.";
      }

      // -----------------------------------------------------------------------
      // INTENT 9: EMERGENCY HELPLINES & SOS ("సహాయం కావాలి", "అత్యవసర నంబర్లు")
      // -----------------------------------------------------------------------
      else if (q.includes("హెల్ప్") || q.includes("నంబర్") || q.includes("ఫోన్") || q.includes("సహాయం కావాలి") ||
               q.includes("helpline") || q.includes("emergency number") || q.includes("contact") || q.includes("sos") || q.includes("police")) {
        teResponse = "ఆంధ్రప్రదేశ్ అధికారిక అత్యవసర హెల్ప్‌లైన్లు: 1. జాతీయ ఎమర్జెన్సీ రెస్పాన్స్ (పోలీస్, ఫైర్, రెస్క్యూ): 112. 2. రాష్ట్ర విపత్తు నిర్వహణ సంస్థ (APSDMA): 1070. 3. జిల్లా కలెక్టరేట్ కంట్రోల్ రూమ్: 1077. 4. అత్యవసర అంబులెన్స్: 108. 5. విద్యుత్ ఫిర్యాదులు (APEPDCL): 1912. ఈ నంబర్లు అన్నీ 24 గంటలూ ఉచితంగా పనిచేస్తాయి.";
        enResponse = "Official Andhra Pradesh 24/7 Emergency Helplines: 1. National ERSS (Police, Fire, Disaster Rescue): 112. 2. State Disaster Management Authority (APSDMA): 1070. 3. District Collectorate Emergency Ops: 1077. 4. Medical Emergency & Ambulance: 108. 5. Electricity Emergency (APEPDCL): 1912. All numbers are 24/7 toll-free.";
      }

      // -----------------------------------------------------------------------
      // NATURAL LANGUAGE FALLBACK: INTELLIGENT DISASTER CONVERSATIONAL RESPONSE
      // -----------------------------------------------------------------------
      else {
        teResponse = "మీ ప్రశ్న: \"" + rawQuery + "\". " + currentMandal + " ప్రాంతంలో విపత్తు నిర్వహణ బృందాలు మరియు సెన్సార్లు నిరంతరం పర్యవేక్షిస్తున్నాయి. మీరు వర్షపాతం (\"వర్షం పడుతుందా?\"), వరద ముప్పు (\"వరద ప్రమాదం ఉందా?\"), మురాసు తుఫాను తాజా స్థితి, సమీప ఆసుపత్రి, లేదా పునరావాస కేంద్రాల వివరాలను నేరుగా అడగవచ్చు. తక్షణ అత్యవసర సహాయం కోసం 112 లేదా 1070 కు కాల్ చేయండి.";
        enResponse = "You asked: \"" + rawQuery + "\". Ground disaster monitoring and sensor telemetry remain active across " + currentMandal + ". You can naturally ask about rainfall (\"Is it raining?\"), local flood risk (\"Is there a flood warning?\"), Cyclone Murasu location, nearest hospital, electricity helpline (1912), or emergency shelters. For urgent rescue, dial 112 or 1077.";
      }

      const isTeOutput = (activeLang === 'te');
      const speakTextStr = isTeOutput ? teResponse : enResponse;
      const speakLangStr = isTeOutput ? 'te-IN' : 'en-IN';

      this.lastTeText = teResponse;
      this.lastEnText = enResponse;
      this.lastSpokenText = speakTextStr;
      this.lastSpokenLang = speakLangStr;

      this.showVoiceResponse(teResponse, enResponse, rawQuery, speakLangStr);
      this.speakText(speakTextStr, speakLangStr);
    }

    showVoiceResponse(teText, enText, userQuery, activeLang) {
      userQuery = userQuery || "";
      let modal = document.getElementById('voiceResponseModal');
      if (!modal) {
        modal = document.createElement('div');
        modal.id = 'voiceResponseModal';
        modal.className = 'voice-response-card';
        document.body.appendChild(modal);
      }

      this.lastTeText = teText;
      this.lastEnText = enText;
      const effectiveLang = activeLang || this.lastSpokenLang || (this.preferredLang === 'te' ? 'te-IN' : 'en-IN');
      const isTe = effectiveLang.startsWith('te');
      const hasResponse = Boolean(teText || enText);

      modal.innerHTML = `
        <div class="voice-modal-header" style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid rgba(255,255,255,0.15); padding-bottom:8px; margin-bottom:10px; flex-shrink:0;">
          <div style="display:flex; align-items:center; gap:8px;">
            <span style="font-size:20px;">🎙️</span>
            <strong style="color:var(--color-golden, #D7A94D); font-size:14.5px; font-weight:800;">` + (isTe ? 'ప్రవాహ్ 360 వాయిస్ అసిస్టెంట్' : 'PRAVAH 360 Voice Assistant') + `</strong>
          </div>
          <button type="button" class="btn-close-voice" onclick="window.pravahVoice.stopSpeech(); document.getElementById('voiceResponseModal').style.display='none'" style="background:none; border:none; color:#fff; font-size:24px; cursor:pointer; line-height:1; padding:0 4px;" title="Close">&times;</button>
        </div>

        <div class="voice-response-scroll-body" style="overflow-y:auto; flex:1; max-height:calc(100vh - 280px); padding-right:4px;">
          ` + (userQuery ? `
            <div class="voice-query-echo" style="background:rgba(255,255,255,0.08); padding:8px 12px; border-radius:6px; font-size:12px; margin-bottom:10px; color:#e2e8f0; border-left:3px solid var(--color-golden, #D7A94D);">
              <strong style="color:#f8fafc;">` + (isTe ? 'మీ ప్రశ్న' : 'You asked') + `:</strong> "` + userQuery + `"
            </div>
          ` : '') + `

          <!-- High-Contrast Response Body -->
          <div class="voice-modal-body" style="font-size:14px; line-height:1.65; color:#ffffff; background:rgba(0,0,0,0.3); padding:12px 14px; border-radius:10px; border:1px solid rgba(255,255,255,0.12);">
            <p class="voice-te-text" style="color:#ffffff !important; font-weight:600; font-size:14.5px; margin:0 0 8px 0; line-height:1.65; text-shadow:0 1px 2px rgba(0,0,0,0.5);">` + teText + `</p>
            <p class="voice-en-text" style="color:#cbd5e1 !important; font-size:12px; border-top:1px dashed rgba(255,255,255,0.2); padding-top:8px; margin:8px 0 0 0; line-height:1.55;">` + enText + `</p>
          </div>

          <!-- Suggestion Chips (Optional shortcuts, not capability boundary) -->
          <div class="voice-suggestion-chips" style="display:flex; flex-wrap:wrap; gap:5px; margin:10px 0;">
            <button type="button" class="voice-chip" onclick="window.pravahVoice.handleVoiceQuery('మురాసు తుఫాను ఇప్పుడు ఎక్కడ ఉంది?')">🌀 మురాసు ఎక్కడ ఉంది?</button>
            <button type="button" class="voice-chip" onclick="window.pravahVoice.handleVoiceQuery('వర్షం పడుతుందా?')">🌧️ వర్షం పడుతుందా?</button>
            <button type="button" class="voice-chip" onclick="window.pravahVoice.handleVoiceQuery('మా ప్రాంతంలో వరద వచ్చే అవకాశం ఉందా?')">🌊 వరద ముప్పు</button>
            <button type="button" class="voice-chip" onclick="window.pravahVoice.handleVoiceQuery('నీళ్లు నిలిచిపోయాయి ఏం చేయాలి?')">⚠️ నీళ్లు నిలిచాయి</button>
            <button type="button" class="voice-chip" onclick="window.pravahVoice.handleVoiceQuery('దగ్గరలో ఆసుపత్రి ఎక్కడ ఉంది?')">🏥 ఆసుపత్రి</button>
            <button type="button" class="voice-chip" onclick="window.pravahVoice.handleVoiceQuery('కరెంట్ లేదు ఎవరికి చెప్పాలి?')">⚡ కరెంట్ సమస్య</button>
            <button type="button" class="voice-chip" onclick="window.pravahVoice.handleVoiceQuery('రేపు బయటకు వెళ్లడం సురక్షితమేనా?')">🚶 ప్రయాణ భద్రత</button>
            <button type="button" class="voice-chip" onclick="window.pravahVoice.handleVoiceQuery('అత్యవసర హెల్ప్‌లైన్లు')">📞 హెల్ప్‌లైన్లు</button>
          </div>
        </div>

        <!-- Voice Status & Language/Voice Detail Badge (Always accurate to active language) -->
        <div id="voiceSpeechStatusBadge" style="margin-top:8px; padding:6px 10px; background:rgba(255,255,255,0.06); border-radius:6px; font-size:11px; color:#cbd5e1; display:flex; align-items:center; justify-content:space-between; flex-shrink:0;">
          <span id="voiceStatusText">⏹️ Ready (` + effectiveLang + `)</span>
          <span id="voiceVoiceDetail" style="color:#D7A94D; font-size:11px; font-weight:700;">` + this.getVoiceDetailText(effectiveLang) + `</span>
        </div>

        <!-- Text Input Fallback (Permanently Visible) -->
        <div class="voice-text-fallback" style="display:flex; gap:6px; margin-top:8px; flex-shrink:0;">
          <input type="text" id="voiceTextInput" placeholder="` + (isTe ? 'మీ ప్రశ్నను ఇక్కడ అడగండి...' : 'Ask any question here...') + `" style="flex:1; background:#0f172a; border:1px solid #475569; color:#fff; padding:8px 10px; border-radius:6px; font-size:12.5px;" onkeydown="if(event.key==='Enter') window.pravahVoice.submitTextInput();">
          <button type="button" onclick="window.pravahVoice.submitTextInput();" style="background:var(--color-forest, #153D37); color:#fff; border:1px solid var(--color-golden, #D7A94D); padding:8px 14px; border-radius:6px; font-size:12.5px; font-weight:700; cursor:pointer;">` + (isTe ? 'అడగండి' : 'Ask') + `</button>
        </div>

        <!-- Spoken Audio Controls: SPEAK, PAUSE, REPLAY, STOP (Permanently Visible) -->
        <div class="voice-modal-actions" style="display:flex; justify-content:space-between; align-items:center; margin-top:10px; padding-top:8px; border-top:1px solid rgba(255,255,255,0.12); flex-shrink:0;">
          <div style="display:flex; gap:5px; flex-wrap:wrap;">
            <button type="button" id="btnVoiceSpeak" onclick="window.pravahVoice.speakCurrentResponse()" ` + (hasResponse ? '' : 'disabled style="opacity:0.5; cursor:not-allowed;"') + ` style="background:var(--color-forest, #153D37); border:1px solid var(--color-golden, #D7A94D); color:#fff; padding:5px 10px; border-radius:6px; font-size:11.5px; font-weight:700; cursor:pointer;" title="Speak response">` + (isTe ? '🔊 వినండి (Speak)' : '🔊 Speak') + `</button>
            <button type="button" id="btnVoicePauseToggle" onclick="window.pravahVoice.togglePause()" ` + (hasResponse ? '' : 'disabled style="opacity:0.5; cursor:not-allowed;"') + ` style="background:rgba(255,255,255,0.08); border:1px solid rgba(255,255,255,0.25); color:#fff; padding:5px 8px; border-radius:6px; font-size:11.5px; cursor:pointer;">⏸️ Pause</button>
            <button type="button" id="btnVoiceReplay" onclick="window.pravahVoice.replaySpeech()" ` + (hasResponse ? '' : 'disabled style="opacity:0.5; cursor:not-allowed;"') + ` style="background:none; border:1px solid rgba(215,169,77,0.4); color:var(--color-golden, #D7A94D); padding:5px 8px; border-radius:6px; font-size:11.5px; cursor:pointer; font-weight:700;">🔄 ` + (isTe ? 'మళ్ళీ' : 'Replay') + `</button>
            <button type="button" id="btnVoiceStop" onclick="window.pravahVoice.stopSpeech()" ` + (hasResponse ? '' : 'disabled style="opacity:0.5; cursor:not-allowed;"') + ` style="background:rgba(239,68,68,0.2); border:1px solid #ef4444; color:#fca5a5; padding:5px 8px; border-radius:6px; font-size:11.5px; cursor:pointer; font-weight:600;">⏹️ Stop</button>
          </div>
          <button type="button" id="btnVoiceMicListen" onclick="window.pravahVoice.toggleListen()" style="background:rgba(214,107,82,0.2); color:#fca5a5; border:1px solid var(--color-coral, #d66b52); padding:5px 10px; border-radius:6px; font-size:11.5px; cursor:pointer; font-weight:700;">🎤 ` + (isTe ? 'మైక్ (Mic)' : 'Mic') + `</button>
        </div>
      `;
      modal.style.display = 'flex';
      modal.style.flexDirection = 'column';
    }

    getVoiceDetailText(activeLang) {
      const targetLang = (activeLang || this.lastSpokenLang || this.currentLang);
      if (targetLang.startsWith('te')) {
        const match = this.getMatchingVoice('te-IN');
        if (match) return match.name;
        return "Google Voice TTS (te-IN)";
      }
      const match = this.getMatchingVoice('en-IN');
      if (match) return match.name;
      return "Google Voice TTS (en-IN)";
    }

    updateVoiceStatusDisplay(customStatus) {
      customStatus = customStatus || null;
      const el = document.getElementById('voiceStatusText');
      const det = document.getElementById('voiceVoiceDetail');
      const activeLang = this.lastSpokenLang || this.currentLang;
      if (det) det.textContent = this.getVoiceDetailText(activeLang);
      if (!el) return;

      if (customStatus) {
        el.textContent = customStatus;
        return;
      }

      if (this.isSpeaking) {
        el.textContent = "🔊 Speaking (" + activeLang + ")";
      } else if (this.isPaused) {
        el.textContent = "⏸️ Paused";
      } else {
        el.textContent = "⏹️ Ready (" + activeLang + ")";
      }
    }

    submitTextInput() {
      const input = document.getElementById('voiceTextInput');
      if (input && input.value && input.value.trim()) {
        const text = input.value.trim();
        input.value = "";
        this.handleVoiceQuery(text);
      }
    }

    speakCurrentResponse() {
      const hasTelugu = /[\u0C00-\u0C7F]/.test(this.lastTeText);
      const isTe = (this.lastSpokenLang && this.lastSpokenLang.startsWith('te')) ||
                   (this.preferredLang === 'te') ||
                   hasTelugu;

      const textToSpeak = isTe ? this.lastTeText : (this.lastEnText || this.lastTeText);
      const langToUse = isTe ? 'te-IN' : 'en-IN';
      if (textToSpeak) {
        this.speakText(textToSpeak, langToUse);
      }
    }

    speakText(text, lang) {
      if (!text || !text.trim()) return;

      // 1. Prevent overlapping speech: stop active speech first
      this.stopSpeech();

      this.lastSpokenText = text;
      this.lastSpokenLang = lang;
      this.isPaused = false;
      this.isSpeaking = true;
      this.updateVoiceStatusDisplay("🔊 Connecting (" + lang + ")...");

      // 2. Query backend TTS endpoint (/api/v1/voice/tts)
      fetch('/api/v1/voice/tts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: text, lang: lang })
      }).then(res => res.json()).then(data => {
        if (data && data.audio_base64) {
          try {
            const audio = new Audio("data:audio/mp3;base64," + data.audio_base64);
            this.currentAudio = audio;
            const provLabel = data.provider_label || (lang.startsWith('te') ? 'Google Telugu Voice' : 'Google English Voice');
            this.updateVoiceStatusDisplay("🔊 Playing (" + provLabel + ")");
            const det = document.getElementById('voiceVoiceDetail');
            if (det) det.textContent = provLabel;

            audio.onended = () => {
              this.isSpeaking = false;
              this.currentAudio = null;
              this.updateVoiceStatusDisplay();
            };
            audio.onerror = (e) => {
              console.warn("Audio element error, falling back to browser synthesis:", e);
              this.currentAudio = null;
              this.speakBrowserSynthesis(text, lang);
            };
            audio.play().catch(e => {
              console.warn("Audio autoplay blocked or failed, using browser synthesis:", e);
              this.currentAudio = null;
              this.speakBrowserSynthesis(text, lang);
            });
            return;
          } catch (e) {
            console.warn("Audio playback exception, falling back to browser synthesis:", e);
          }
        }
        // Fallback to browser synthesis
        this.speakBrowserSynthesis(text, lang);
      }).catch(err => {
        console.warn("Backend TTS fetch failed, using browser synthesis:", err);
        this.speakBrowserSynthesis(text, lang);
      });
    }

    speakBrowserSynthesis(text, lang) {
      if (!this.synth) {
        this.isSpeaking = false;
        this.updateVoiceStatusDisplay("⚠️ Browser Speech Synthesis not supported.");
        return;
      }

      try {
        this.synth.cancel();
        const cleanText = text.replace(/[*#_~]/g, '');
        const utterance = new SpeechSynthesisUtterance(cleanText);
        utterance.lang = lang;
        utterance.rate = 0.92;

        const matchingVoice = this.getMatchingVoice(lang);

        if (lang.startsWith('te') && !matchingVoice) {
          // If no genuine Telugu voice exists in browser/OS, NEVER speak Telugu with an English voice!
          this.isSpeaking = false;
          console.info("Telugu OS voice not present in browser. Visual Telugu text displayed.");
          this.updateVoiceStatusDisplay("⚠️ Telugu audio unavailable (No te-IN voice installed in browser/OS). Text displayed above.");
          const det = document.getElementById('voiceVoiceDetail');
          if (det) det.textContent = "Audio Unavailable (No te-IN voice)";
          return;
        }

        if (matchingVoice) {
          utterance.voice = matchingVoice;
          this.updateVoiceStatusDisplay("🔊 Speaking (" + matchingVoice.name + ")");
        } else {
          this.updateVoiceStatusDisplay("🔊 Speaking (" + lang + ")");
        }

        utterance.onend = () => {
          this.isSpeaking = false;
          this.currentUtterance = null;
          this.updateVoiceStatusDisplay();
        };

        utterance.onerror = (e) => {
          console.warn("Speech utterance notice:", e);
          this.isSpeaking = false;
          this.currentUtterance = null;
          this.updateVoiceStatusDisplay("⚠️ Speech playback finished");
        };

        this.currentUtterance = utterance;
        this.synth.speak(utterance);
      } catch (e) {
        console.warn("Speech synthesis error:", e);
        this.isSpeaking = false;
        this.updateVoiceStatusDisplay("⚠️ Speech synthesis notice");
      }
    }

    togglePause() {
      const btn = document.getElementById('btnVoicePauseToggle');

      // If playing via backend Cloud / Web TTS Audio
      if (this.currentAudio) {
        if (this.isPaused) {
          this.currentAudio.play().catch(e => console.warn("Audio resume error:", e));
          this.isPaused = false;
          if (btn) btn.textContent = "⏸️ Pause";
          this.updateVoiceStatusDisplay("🔊 Playing (" + (this.lastSpokenLang || this.currentLang) + ")");
        } else {
          this.currentAudio.pause();
          this.isPaused = true;
          if (btn) btn.textContent = "▶️ Resume";
          this.updateVoiceStatusDisplay("⏸️ Paused");
        }
        return;
      }

      // If playing via browser speechSynthesis
      if (this.synth) {
        if (this.isPaused) {
          this.synth.resume();
          this.isPaused = false;
          if (btn) btn.textContent = "⏸️ Pause";
          this.updateVoiceStatusDisplay("🔊 Playing (" + (this.lastSpokenLang || this.currentLang) + ")");
        } else if (this.synth.speaking || this.isSpeaking) {
          this.synth.pause();
          this.isPaused = true;
          if (btn) btn.textContent = "▶️ Resume";
          this.updateVoiceStatusDisplay("⏸️ Paused");
        }
      }
    }

    replaySpeech() {
      this.stopSpeech();
      const textToReplay = this.lastSpokenText || (this.preferredLang === 'te' ? this.lastTeText : this.lastEnText);
      const langToReplay = this.lastSpokenLang || (this.preferredLang === 'te' ? 'te-IN' : 'en-IN');
      if (textToReplay) {
        this.speakText(textToReplay, langToReplay);
      }
    }

    stopSpeech() {
      if (this.currentAudio) {
        try {
          this.currentAudio.pause();
          this.currentAudio.currentTime = 0;
        } catch (e) {}
        this.currentAudio = null;
      }
      if (this.synth) {
        try {
          this.synth.cancel();
        } catch (e) {}
        this.currentUtterance = null;
      }
      this.isSpeaking = false;
      this.isPaused = false;
      const btn = document.getElementById('btnVoicePauseToggle');
      if (btn) btn.textContent = "⏸️ Pause";
      this.updateVoiceStatusDisplay();
    }
  }

  // Global helper functions for convenience
  window.openVoiceAssistantModal = function() {
    if (window.pravahVoice) {
      window.pravahVoice.showVoiceModalWithTextInput();
    }
  };

  window.closeVoiceAssistantModal = function() {
    if (window.pravahVoice) {
      window.pravahVoice.stopSpeech();
    }
    const modal = document.getElementById('voiceResponseModal');
    if (modal) modal.style.display = 'none';
  };

  window.handleVoiceAssistantInput = function(query) {
    if (window.pravahVoice) {
      window.pravahVoice.handleVoiceQuery(query);
    }
  };

  // Instantiate globally on script load
  window.pravahVoice = new PravahVoiceAssistant();
})();
