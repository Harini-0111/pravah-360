const fs = require('fs');
const html = fs.readFileSync('frontend/index.html', 'utf8');
const lines = html.split('\n');
console.log(lines.slice(690, 725).map((l, i) => `${691+i}: ${l}`).join('\n'));
