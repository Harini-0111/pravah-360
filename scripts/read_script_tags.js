const fs = require('fs');
const html = fs.readFileSync('frontend/index.html', 'utf8');
const lines = html.split('\n');
console.log(lines.slice(6215, 6235).map((l, i) => `${6216+i}: ${l}`).join('\n'));
console.log(lines.slice(6420, 6435).map((l, i) => `${6421+i}: ${l}`).join('\n'));
