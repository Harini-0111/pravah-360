const fs = require('fs');
const js = fs.readFileSync('frontend/app.js', 'utf8');

const lines = js.split('\n');
lines.forEach((l, i) => {
  if (l.includes('checkInitialSession') || l.includes('function navigateTo')) {
    console.log(`${i+1}: ${l}`);
  }
});
