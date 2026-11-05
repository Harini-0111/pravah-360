const fs = require('fs');
const html = fs.readFileSync('frontend/index.html', 'utf8');
const lines = html.split('\n');
lines.forEach((l, i) => {
  if (l.includes('btnLandingLangToggle')) {
    console.log(`${i+1}: ${l}`);
  }
});
