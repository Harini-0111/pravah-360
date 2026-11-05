const fs = require('fs');
const appPath = 'C:/major project/frontend/app.js';
let app = fs.readFileSync(appPath, 'utf8');

const helperFunctions = `
  // =========================================================================
  // COMMUNITY GROUND HAZARD SUBMISSION CONTROLLER
  // =========================================================================
  window.handleHazardReportSubmit = async function(e) {
    e.preventDefault();
    const btn = document.getElementById('btnSubmitHazardReport');
    const fb = document.getElementById('hazardSubmitFeedback');
    const mandal = document.getElementById('hazardMandal').value;
    const category = document.getElementById('hazardCategory').value;
    const description = document.getElementById('hazardDescription').value;
    const reporterName = document.getElementById('hazardReporterName').value || 'Local Resident';
    const photoInput = document.getElementById('hazardPhotoFile');

    if (btn) {
      btn.classList.add('loading');
      btn.disabled = true;
    }

    let photoData = null;
    if (photoInput && photoInput.files && photoInput.files[0]) {
      const file = photoInput.files[0];
      photoData = await new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = (re) => resolve(re.target.result);
        reader.readAsDataURL(file);
      });
    }

    const payload = {
      mandal: mandal,
      district: 'East Godavari',
      category: category,
      description: description,
      reporter_name: reporterName,
      location_description: 'Reported via PRAVAH 360 Citizen Web Portal',
      photo_data: photoData
    };

    try {
      const res = await fetch('/api/v1/community/hazards/report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (btn) {
        btn.classList.remove('loading');
        btn.disabled = false;
      }
      if (fb) {
        fb.style.display = 'block';
        fb.style.color = '#059669';
        fb.innerHTML = '✓ నివేదిక సమర్పించబడింది! ఐడీ: <strong>' + data.report_id + '</strong> (Status: SUBMITTED &rarr; Under Review)';
      }
      // Reset form
      document.getElementById('hazardDescription').value = '';
      if (photoInput) photoInput.value = '';
      // Refresh feed
      loadCommunityHazardsFeed();
    } catch (err) {
      console.error('Hazard submission error:', err);
      if (btn) {
        btn.classList.remove('loading');
        btn.disabled = false;
      }
      if (fb) {
        fb.style.display = 'block';
        fb.style.color = '#dc2626';
        fb.textContent = 'సమర్పణ విఫలమైంది. దయచేసి మళ్ళీ ప్రయత్నించండి.';
      }
    }
  };

  async function loadCommunityHazardsFeed() {
    const listEl = document.getElementById('communityHazardsList');
    if (!listEl) return;
    try {
      const res = await fetch('/api/v1/community/hazards');
      const reports = await res.json();
      if (!reports || reports.length === 0) return;
      listEl.innerHTML = reports.slice(0, 5).map(r => {
        const statusColors = {
          SUBMITTED: '#64748b',
          UNDER_REVIEW: '#d97706',
          VERIFIED: '#059669',
          RESOLVED: '#0284c7',
          REJECTED: '#dc2626'
        };
        const stColor = statusColors[r.status] || '#64748b';
        return \`
          <div style="padding:10px 12px; background:var(--color-mist); border-radius:8px; font-size:12.5px; border-left:3px solid \${stColor};">
            <div style="display:flex; justify-content:space-between; font-weight:700; color:var(--color-forest);">
              <span>\${r.category.replace(/_/g, ' ')}</span>
              <span style="color:\${stColor}; font-weight:800;">● \${r.status}</span>
            </div>
            <div style="color:var(--text-muted-dark); font-size:11.5px; margin-top:2px;">\${r.mandal} • \${r.description}</div>
            <div style="font-size:10.5px; color:#64748b; margin-top:4px;">Reporter: \${r.reporter_name_redacted} • \${r.created_at}</div>
          </div>
        \`;
      }).join('');
    } catch (e) {
      console.warn('Could not load hazards feed:', e);
    }
  }

  // =========================================================================
  // UNIVERSAL TELUGU / ENGLISH TRANSLATION CONTROLLER
  // =========================================================================
  window.currentAppLang = 'en';

  window.toggleGlobalLanguage = function() {
    const targetLang = window.currentAppLang === 'en' ? 'te' : 'en';
    window.setAppLanguage(targetLang);
  };

  window.setAppLanguage = function(lang) {
    if (!window.PRAVAH_TRANSLATIONS || !window.PRAVAH_TRANSLATIONS[lang]) return;
    window.currentAppLang = lang;
    const dict = window.PRAVAH_TRANSLATIONS[lang];

    // Update voice assistant language
    if (window.pravahVoice) {
      window.pravahVoice.setLanguage(lang);
    }

    // Update buttons
    const btnLandingToggle = document.getElementById('btnLandingLangToggle');
    if (btnLandingToggle) {
      btnLandingToggle.textContent = dict.langToggle;
    }

    // Apply data-i18n attributes
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (dict[key]) {
        el.textContent = dict[key];
      }
    });

    // Landing nav links
    const navLinks = document.querySelectorAll('.landing-nav-links a');
    if (navLinks.length >= 4) {
      navLinks[0].textContent = dict.navOverview;
      navLinks[1].textContent = dict.navAwareness;
      navLinks[2].textContent = dict.navRoles;
      navLinks[3].textContent = dict.navHelplines;
    }

    // Hero section
    const hHeadline = document.querySelector('.hero-headline');
    const hTagline = document.querySelector('.hero-tagline');
    const hStmt = document.querySelector('.hero-supporting-statement');
    const btnExp = document.getElementById('btnHeroExplore');
    const btnReg = document.getElementById('btnHeroRegister');
    const btnSign = document.getElementById('btnHeroSignIn');
    if (hHeadline) hHeadline.textContent = dict.heroHeadline;
    if (hTagline) hTagline.textContent = dict.heroTagline;
    if (hStmt) hStmt.textContent = dict.heroStatement;
    if (btnExp) btnExp.textContent = dict.btnExplore;
    if (btnReg) btnReg.textContent = dict.btnCreateAccount;
    if (btnSign) btnSign.textContent = dict.btnSignIn;

    // Card titles in Section 02
    const awarenessCards = document.querySelectorAll('.awareness-card');
    if (awarenessCards.length >= 4) {
      if (awarenessCards[0].querySelector('h3')) awarenessCards[0].querySelector('h3').textContent = dict.card1Title;
      if (awarenessCards[0].querySelector('p')) awarenessCards[0].querySelector('p').textContent = dict.card1Desc;
      if (awarenessCards[0].querySelector('.awareness-card-link')) awarenessCards[0].querySelector('.awareness-card-link').textContent = dict.card1Link;

      if (awarenessCards[1].querySelector('h3')) awarenessCards[1].querySelector('h3').textContent = dict.card2Title;
      if (awarenessCards[1].querySelector('p')) awarenessCards[1].querySelector('p').textContent = dict.card2Desc;
      if (awarenessCards[1].querySelector('.awareness-card-link')) awarenessCards[1].querySelector('.awareness-card-link').textContent = dict.card2Link;

      if (awarenessCards[2].querySelector('h3')) awarenessCards[2].querySelector('h3').textContent = dict.card3Title;
      if (awarenessCards[2].querySelector('p')) awarenessCards[2].querySelector('p').textContent = dict.card3Desc;
      if (awarenessCards[2].querySelector('.awareness-card-link')) awarenessCards[2].querySelector('.awareness-card-link').textContent = dict.card3Link;

      if (awarenessCards[3].querySelector('h3')) awarenessCards[3].querySelector('h3').textContent = dict.card4Title;
      if (awarenessCards[3].querySelector('p')) awarenessCards[3].querySelector('p').textContent = dict.card4Desc;
      if (awarenessCards[3].querySelector('.awareness-card-link')) awarenessCards[3].querySelector('.awareness-card-link').textContent = dict.card4Link;
    }

    // Role Persona Cards
    const personaCards = document.querySelectorAll('.platform-persona-card');
    if (personaCards.length >= 2) {
      if (personaCards[0].querySelector('h3')) personaCards[0].querySelector('h3').textContent = dict.roleResidentTitle;
      if (personaCards[0].querySelector('p')) personaCards[0].querySelector('p').textContent = dict.roleResidentDesc;
      if (personaCards[0].querySelector('.btn-persona-cta')) personaCards[0].querySelector('.btn-persona-cta').textContent = dict.roleResidentBtn;

      if (personaCards[1].querySelector('h3')) personaCards[1].querySelector('h3').textContent = dict.roleResponseTitle;
      if (personaCards[1].querySelector('p')) personaCards[1].querySelector('p').textContent = dict.roleResponseDesc;
      if (personaCards[1].querySelector('.btn-persona-cta')) personaCards[1].querySelector('.btn-persona-cta').textContent = dict.roleResponseBtn;
    }

    // Auth forms
    const signInTitleEl = document.querySelector('#loginFormCard .auth-form-header h2');
    const signInDescEl = document.querySelector('#loginFormCard .auth-form-header p');
    if (signInTitleEl) signInTitleEl.textContent = dict.signInTitle;
    if (signInDescEl) signInDescEl.textContent = dict.signInDesc;

    const regTitleEl = document.querySelector('#registerFormCard .auth-form-header h2');
    const regDescEl = document.querySelector('#registerFormCard .auth-form-header p');
    if (regTitleEl) regTitleEl.textContent = dict.registerTitle;
    if (regDescEl) regDescEl.textContent = dict.registerDesc;

    // Helplines intro
    const hlIntroH4 = document.querySelector('.helpline-intro h4');
    const hlIntroP = document.querySelector('.helpline-intro p');
    if (hlIntroH4) hlIntroH4.textContent = dict.helplineTitle;
    if (hlIntroP) hlIntroP.textContent = dict.helplineSub;

    console.log("App language switched to:", lang);
  };
`;

// Insert the helpers before DOMContentLoaded closes
const anchor = "document.addEventListener('DOMContentLoaded', () => {";
if (app.includes(anchor)) {
  // Replace btnLandingLangToggle listener with toggleGlobalLanguage
  const oldLangListener = `    const btnLang = document.getElementById('btnLandingLangToggle');
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

  const newLangListener = `    const btnLang = document.getElementById('btnLandingLangToggle');
    if (btnLang) {
      btnLang.addEventListener('click', () => {
        window.toggleGlobalLanguage();
      });
    }
    loadCommunityHazardsFeed();`;

  if (app.includes(oldLangListener)) {
    app = app.replace(oldLangListener, newLangListener);
    console.log("✓ Replaced old landing lang listener with window.toggleGlobalLanguage()");
  }

  // Prepend helper functions right before DOMContentLoaded
  app = helperFunctions + '\n' + app;
  console.log("✓ Injected community hazard & language helpers to app.js");
}

fs.writeFileSync(appPath, app, 'utf8');
console.log("app.js updated successfully.");
