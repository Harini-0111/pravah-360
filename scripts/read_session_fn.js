const fs = require('fs');
const lines = fs.readFileSync('frontend/app.js', 'utf8').split('\n');
console.log(lines.slice(3600, 3750).map((l, i) => `${3601+i}: ${l}`).join('\n'));
