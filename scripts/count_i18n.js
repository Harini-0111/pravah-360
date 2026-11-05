const fs = require('fs');
const html = fs.readFileSync('frontend/index.html', 'utf8');

const matches = html.match(/data-i18n="[^"]*"/g) || [];
console.log('Total data-i18n elements in index.html:', matches.length);
console.log('Unique data-i18n keys:', Array.from(new Set(matches)).join(', '));
