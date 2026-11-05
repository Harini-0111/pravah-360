const fs = require('fs');

// 1. Fix script load order in index.html
let html = fs.readFileSync('frontend/index.html', 'utf8');

// Remove translations.js and voice_assistant.js from bottom
html = html.replace('  <!-- Multilingual Telugu Engine & Voice Assistance -->\n  <script src="/static/translations.js"></script>\n  <script src="/static/voice_assistant.js"></script>\n', '');
html = html.replace('<script src="/static/translations.js"></script>\n<script src="/static/voice_assistant.js"></script>\n', '');

// Insert them right before app.js
const appScriptTag = '<script src="/static/app.js?v=20261103_scroll_reg"></script>';
const scriptsBeforeApp = `  <!-- Multilingual Telugu Engine & Voice Assistance -->\n  <script src="/static/translations.js"></script>\n  <script src="/static/voice_assistant.js"></script>\n  ${appScriptTag}`;

if (html.includes(appScriptTag) && !html.includes('src="/static/translations.js"></script>\n  <!-- Multilingual')) {
  html = html.replace(appScriptTag, scriptsBeforeApp);
  fs.writeFileSync('frontend/index.html', html, 'utf8');
  console.log('SUCCESS: script tags reordered in index.html');
} else {
  console.log('index.html script order check:', html.includes('translations.js'));
}

// 2. Fix app.js: replace the stale btnLandingLangToggle listener
let js = fs.readFileSync('frontend/app.js', 'utf8');

const staleBlock = `    // Landing Telugu Toggle
    const btnLang = document.getElementById('btnLandingLangToggle');
    if (btnLang) {
      btnLang.addEventListener('click', () => {
        const h = document.querySelector('.hero-headline');
        const t = document.querySelector('.hero-tagline');
        const s = document.querySelector('.hero-supporting-statement');
        if (btnLang.textContent.includes('తెలుగు')) {
          btnLang.textContent = 'English';
          if (h) h.textContent = 'ప్రకృతి మారినప్పుడు, సిద్ధంగా ఉండండి.';
          if (t) t.textContent = 'ప్రమాదాన్ని గుర్తించండి. సంసిద్ధంగా ఉండండి.';
          if (s) s.textContent = 'విపత్తులను అర్థం చేసుకోండి. సమాజాలను రక్షించండి. సహాయాన్ని అనుసంధానించండి.';
        } else {
          btnLang.textContent = 'తెలుగు';
          if (h) h.textContent = 'When nature changes, be prepared.';
          if (t) t.textContent = 'See the risk. Stay prepared.';
          if (s) s.textContent = 'Understand disasters. Protect communities. Connect people to help across the Lower Godavari Basin.';
        }
      });
    }`;

const cleanBlock = `    // Global Language Toggle on Welcome Page
    const btnLang = document.getElementById('btnLandingLangToggle');
    if (btnLang) {
      btnLang.addEventListener('click', () => {
        if (typeof window.toggleGlobalLanguage === 'function') {
          window.toggleGlobalLanguage();
        }
      });
    }`;

if (js.includes(staleBlock)) {
  js = js.replace(staleBlock, cleanBlock);
  console.log('SUCCESS: Stale btnLandingLangToggle listener replaced in app.js');
}

// Clean up registration redirect timing
js = js.replace(
  `            setTimeout(() => {
              const successOverlay = document.getElementById('regSuccessOverlay');
            if (successOverlay) { successOverlay.style.display = 'flex'; }
            setTimeout(() => { navigateTo('role-select'); }, 1500);
            }, 600);`,
  `            setTimeout(() => {
              const successOverlay = document.getElementById('regSuccessOverlay');
              if (successOverlay) { successOverlay.style.display = 'flex'; }
              setTimeout(() => { navigateTo('role-select'); }, 600);
            }, 300);`
);

fs.writeFileSync('frontend/app.js', js, 'utf8');
console.log('SUCCESS: app.js updated');

// 3. Update voice_assistant.js rain fallback wording
let voice = fs.readFileSync('frontend/voice_assistant.js', 'utf8');
voice = voice.replace(
  `teResponse = \`ప్రత్యక్ష వాతావరణ సెన్సార్ సమాచారం ప్రస్తుతం బ్యాకప్ మోడ్‌లో ఉంది. వాతావరణ శాఖ (IMD) సూచనల ప్రకారం తూర్పు గోదావరి మరియు కోనసీమ ప్రాంతాల్లో సాధారణ వర్షాకాల పరిస్థితులు కొనసాగుతున్నాయి.\`;`,
  `teResponse = \`ప్రస్తుత వర్షపాతం మరియు వాతావరణ సమాచారం: ప్రత్యక్ష సెన్సార్లు బ్యాకప్ మోడ్‌లో ఉన్నాయి. వాతావరణ శాఖ (IMD) సూచనల ప్రకారం గోదావరి డెల్టాలో తేలికపాటి వర్షం లేదా చిరుజల్లులు కురిసే అవకాశం ఉంది.\`;`
);
fs.writeFileSync('frontend/voice_assistant.js', voice, 'utf8');
console.log('SUCCESS: voice_assistant.js updated');
