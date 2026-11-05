const fs = require('fs');
const lines = fs.readFileSync('frontend/app.js', 'utf8').split('\n');
console.log(lines.slice(4170, 4210).map((l, i) => `${4171+i}: ${l}`).join('\n'));
