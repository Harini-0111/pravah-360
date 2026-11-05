const fs = require('fs');
const lines = fs.readFileSync('frontend/app.js', 'utf8').split('\n');
console.log(lines.slice(3830, 3900).map((l, i) => `${3831+i}: ${l}`).join('\n'));
