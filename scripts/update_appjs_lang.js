const fs = require('fs');

const path = 'frontend/app.js';
let content = fs.readFileSync(path, 'utf8');

const updatedSetAppLang = `  window.currentAppLang = localStorage.getItem('pravah_lang') || 'en';

  window.toggleGlobalLanguage = function() {
    const targetLang = window.currentAppLang === 'en' ? 'te' : 'en';
    window.setAppLanguage(targetLang);
  };

  window.setAppLanguage = function(lang) {
    if (!window.PRAVAH_TRANSLATIONS || !window.PRAVAH_TRANSLATIONS[lang]) return;
    window.currentAppLang = lang;
    try { localStorage.setItem('pravah_lang', lang); } catch (e) {}
    document.body.setAttribute('data-lang', lang);
    const dict = window.PRAVAH_TRANSLATIONS[lang];

    // 1. Update voice assistant language
    if (window.pravahVoice && typeof window.pravahVoice.setLanguage === 'function') {
      window.pravahVoice.setLanguage(lang);
    }

    // 2. Update language toggle buttons across surfaces
    document.querySelectorAll('#btnLandingLangToggle, .btn-lang-toggle, .lang-switch-btn').forEach(btn => {
      btn.textContent = dict.langToggle;
    });

    // 3. Apply all data-i18n attributes
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (dict[key]) {
        if (el.tagName === 'INPUT' && (el.type === 'button' || el.type === 'submit')) {
          el.value = dict[key];
        } else {
          el.textContent = dict[key];
        }
      }
    });

    // 4. Apply all data-i18n-placeholder attributes
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
      const key = el.getAttribute('data-i18n-placeholder');
      if (dict[key]) {
        el.placeholder = dict[key];
      }
    });

    // 5. Landing nav links
    const navLinks = document.querySelectorAll('.landing-nav-links a');
    if (navLinks.length >= 4) {
      navLinks[0].textContent = dict.navOverview;
      navLinks[1].textContent = dict.navAwareness;
      navLinks[2].textContent = dict.navRoles;
      navLinks[3].textContent = dict.navHelplines;
    }

    // 6. Hero section elements
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

    // 7. Awareness cards in Section 02
    const awarenessCards = document.querySelectorAll('.awareness-card');
    if (awarenessCards.length >= 5) {
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

      if (awarenessCards[4].querySelector('h3')) awarenessCards[4].querySelector('h3').textContent = dict.card5Title;
      if (awarenessCards[4].querySelector('p')) awarenessCards[4].querySelector('p').textContent = dict.card5Desc;
      if (awarenessCards[4].querySelector('.awareness-card-link')) awarenessCards[4].querySelector('.awareness-card-link').textContent = dict.card5Link;
    }

    // 8. Role Persona Cards
    const personaCards = document.querySelectorAll('.platform-persona-card');
    if (personaCards.length >= 2) {
      if (personaCards[0].querySelector('h3')) personaCards[0].querySelector('h3').textContent = dict.roleResidentTitle;
      if (personaCards[0].querySelector('p')) personaCards[0].querySelector('p').textContent = dict.roleResidentDesc;
      if (personaCards[0].querySelector('.btn-persona-cta')) personaCards[0].querySelector('.btn-persona-cta').textContent = dict.roleResidentBtn;

      if (personaCards[1].querySelector('h3')) personaCards[1].querySelector('h3').textContent = dict.roleResponseTitle;
      if (personaCards[1].querySelector('p')) personaCards[1].querySelector('p').textContent = dict.roleResponseDesc;
      if (personaCards[1].querySelector('.btn-persona-cta')) personaCards[1].querySelector('.btn-persona-cta').textContent = dict.roleResponseBtn;
    }

    // 9. Auth forms headers & buttons
    const signH2 = document.querySelector('#page-login .auth-form-header h2');
    const signP = document.querySelector('#page-login .auth-form-header p');
    if (signH2) signH2.textContent = dict.signInTitle;
    if (signP) signP.textContent = dict.signInDesc;

    const regH2 = document.querySelector('#page-register .auth-form-header h2');
    const regP = document.querySelector('#page-register .auth-form-header p');
    if (regH2) regH2.textContent = dict.registerTitle;
    if (regP) regP.textContent = dict.registerDesc;

    const btnLogSub = document.getElementById('btnDedicatedLoginSubmit');
    if (btnLogSub) btnLogSub.textContent = dict.btnSignInSubmit;

    const btnRegSub = document.getElementById('btnRegisterSubmit');
    if (btnRegSub) btnRegSub.textContent = dict.btnRegisterSubmit;

    // 10. Role Selection & Onboarding
    const roleH2 = document.querySelector('#page-role-select h2');
    const roleSub = document.querySelector('#page-role-select p');
    if (roleH2) roleH2.textContent = dict.roleSelectTitle;
    if (roleSub) roleSub.textContent = dict.roleSelectSub;

    const onbH2 = document.querySelector('#page-location-onboarding h2');
    const onbSub = document.querySelector('#page-location-onboarding p');
    const btnSaveOnb = document.getElementById('btnSaveLocationOnboarding');
    const btnDetLoc = document.getElementById('btnDetectLocation');
    if (onbH2) onbH2.textContent = dict.onboardingTitle;
    if (onbSub) onbSub.textContent = dict.onboardingSub;
    if (btnSaveOnb) btnSaveOnb.textContent = dict.btnSaveOnboarding;
    if (btnDetLoc) btnDetLoc.textContent = dict.btnDetectLocation;

    // 11. Situation Awareness Home
    const sitH2 = document.querySelector('#page-situation-home .entry-header-title');
    const sitSub = document.querySelector('#page-situation-home .entry-header-sub');
    if (sitH2) sitH2.textContent = dict.sitHomeTitle;
    if (sitSub) sitSub.textContent = dict.sitHomeSub;

    // 12. Helplines Intro
    const hlIntroH4 = document.querySelector('.helpline-intro h4');
    const hlIntroP = document.querySelector('.helpline-intro p');
    if (hlIntroH4) hlIntroH4.textContent = dict.helplineTitle;
    if (hlIntroP) hlIntroP.textContent = dict.helplineSub;

    console.log("App language switched to:", lang);
  };`;

// Replace lines from `window.currentAppLang = 'en';` to `console.log("App language switched to:", lang);\n  };`
const startIdx = content.indexOf("window.currentAppLang = 'en';");
const endTarget = 'console.log("App language switched to:", lang);\n  };';
const endIdx = content.indexOf(endTarget);

if (startIdx !== -1 && endIdx !== -1) {
  content = content.slice(0, startIdx) + updatedSetAppLang + content.slice(endIdx + endTarget.length);
  fs.writeFileSync(path, content, 'utf8');
  console.log('SUCCESS: app.js setAppLanguage completely updated');
} else {
  console.error('Could not find start/end targets in app.js');
}
