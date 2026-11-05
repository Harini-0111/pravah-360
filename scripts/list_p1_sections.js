const fs = require('fs');
const html = fs.readFileSync('C:/major project/frontend/index.html', 'utf8');
const p1 = html.slice(0, 15745);
const lines = p1.split('\n');
lines.forEach((l, i) => {
  if (l.includes('landing-') || l.includes('section-editorial') || l.includes('<section')) {
    console.log((i + 1) + ': ' + l.trim().slice(0, 80));
  }
});
