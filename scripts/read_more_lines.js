const fs = require('fs');
const lines = fs.readFileSync('frontend/app.js', 'utf8').split('\n');
console.log(lines.slice(3770, 3845).map((l, i) => `${3771+i}: ${l}`).join('\n'));
