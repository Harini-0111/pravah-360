const fs = require('fs');

const path = 'frontend/app.js';
let content = fs.readFileSync(path, 'utf8');

// 1. Fix the duplicate const urlParams declaration at the end of app.js
content = content.replace(
  `  // URL query parameter action handlers (for automation & test captures)
  const urlParams = new URLSearchParams(window.location.search);
  const langParam = urlParams.get('lang');`,
  `  // URL query parameter action handlers (for automation & test captures)
  const deepLinkParams = new URLSearchParams(window.location.search);
  const langParam = deepLinkParams.get('lang');`
);
content = content.replace(
  `  const actionParam = urlParams.get('action');`,
  `  const actionParam = deepLinkParams.get('action');`
);

// 2. Fix setAuthBtnLoading at line 3422 if it's called out of scope
// Make setAuthBtnLoading globally available inside DOMContentLoaded
const helperDef = `  function setAuthBtnLoading(btnId, loading) {
    const btn = document.getElementById(btnId);
    if (!btn) return;
    if (loading) { btn.classList.add('loading'); btn.disabled = true; }
    else { btn.classList.remove('loading'); btn.disabled = false; }
  }`;

if (!content.includes('function setAuthBtnLoading(btnId, loading)')) {
  // Add it early in DOMContentLoaded
  content = content.replace(
    `document.addEventListener('DOMContentLoaded', () => {`,
    `document.addEventListener('DOMContentLoaded', () => {\n${helperDef}`
  );
}

// 3. Fix checkInitialSession to properly unwrap user object from /api/v1/auth/session
content = content.replace(
  `        if (data && data.user) {
          authenticatedUser = data.user;
          updateUserBadges();
        }`,
  `        const u = data.user || (data.user_id ? data : null);
        if (u) {
          authenticatedUser = u;
          updateUserBadges();
        }`
);

// 4. Fix btnLandingLangToggle listener in initMultiPageEntryControllers
const oldToggleBlock = `    // Landing Telugu Toggle
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

const newToggleBlock = `    // Global Language Toggle on Welcome Page
    const btnLang = document.getElementById('btnLandingLangToggle');
    if (btnLang) {
      btnLang.addEventListener('click', () => {
        if (typeof window.toggleGlobalLanguage === 'function') {
          window.toggleGlobalLanguage();
        }
      });
    }`;

if (content.includes(oldToggleBlock)) {
  content = content.replace(oldToggleBlock, newToggleBlock);
}

fs.writeFileSync(path, content, 'utf8');
console.log('SUCCESS: app.js core logic patched');
