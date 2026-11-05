const fs = require('fs');
const lines = fs.readFileSync('backend/app/api/endpoints.py', 'utf8').split('\n');
console.log(lines.slice(170, 195).map((l, i) => `${171+i}: ${l}`).join('\n'));
