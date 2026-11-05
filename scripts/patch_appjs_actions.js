const fs = require('fs');

const path = 'frontend/app.js';
let content = fs.readFileSync(path, 'utf8');

const target = '  initMultiPageEntryControllers();';
const addition = `  initMultiPageEntryControllers();

  // URL query parameter action handlers (for automation & test captures)
  const urlParams = new URLSearchParams(window.location.search);
  const langParam = urlParams.get('lang');
  if (langParam && typeof window.setAppLanguage === 'function') {
    setTimeout(() => { window.setAppLanguage(langParam); }, 300);
  }
  const actionParam = urlParams.get('action');
  if (actionParam === 'telugu') {
    setTimeout(() => {
      if (typeof window.setAppLanguage === 'function') window.setAppLanguage('te');
    }, 300);
  } else if (actionParam === 'hazards') {
    setTimeout(() => {
      if (typeof window.setAppLanguage === 'function') window.setAppLanguage('te');
      const sec = document.getElementById('community-hazards');
      if (sec) sec.scrollIntoView({ behavior: 'instant', block: 'start' });
    }, 500);
  } else if (actionParam === 'voice') {
    setTimeout(() => {
      if (typeof window.setAppLanguage === 'function') window.setAppLanguage('te');
      if (window.pravahVoice && typeof window.pravahVoice.handleVoiceQuery === 'function') {
        window.pravahVoice.handleVoiceQuery('వరద హెచ్చరికలు ఉన్నాయా?');
      }
    }, 500);
  }`;

if (content.includes(target) && !content.includes('actionParam === \'telugu\'')) {
  content = content.replace(target, addition);
  fs.writeFileSync(path, content, 'utf8');
  console.log('SUCCESS: app.js updated with deep link actions');
} else {
  console.log('Already updated or target not found');
}
