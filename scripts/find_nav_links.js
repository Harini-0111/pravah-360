const fs = require('fs');
const html = fs.readFileSync('frontend/index.html', 'utf8');

// Find all buttons or links with 'sign' or 'login' or 'reg' in id or class
const lines = html.split('\n');
lines.forEach((l, i) => {
  if (l.includes('navigateTo(') || l.includes('btnLanding') || l.includes('btnNav') || l.includes('btnHero') || l.includes('href="#login"') || l.includes('href="#register"')) {
    console.log(`${i+1}: ${l.trim()}`);
  }
});
