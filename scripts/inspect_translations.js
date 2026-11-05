const fs = require('fs');
const tr = fs.readFileSync('frontend/translations.js', 'utf8');
console.log('Translations file length:', tr.length);
console.log('Keys in PRAVAH_TRANSLATIONS:');
const vm = require('vm');
const sandbox = { window: {} };
vm.createContext(sandbox);
vm.runInContext(tr, sandbox);
if (sandbox.window.PRAVAH_TRANSLATIONS) {
  console.log('Languages:', Object.keys(sandbox.window.PRAVAH_TRANSLATIONS));
  console.log('English keys count:', Object.keys(sandbox.window.PRAVAH_TRANSLATIONS.en || {}).length);
  console.log('Telugu keys count:', Object.keys(sandbox.window.PRAVAH_TRANSLATIONS.te || {}).length);
  console.log('Sample keys:', Object.keys(sandbox.window.PRAVAH_TRANSLATIONS.en || {}).slice(0, 30));
} else {
  console.log('PRAVAH_TRANSLATIONS not found on window!');
}
