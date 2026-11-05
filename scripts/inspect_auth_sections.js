const fs = require('fs');
const lines = fs.readFileSync('frontend/app.js', 'utf8').split('\n');

console.log('=== 3360 - 3440 ===');
console.log(lines.slice(3360, 3440).map((l, i) => `${3361+i}: ${l}`).join('\n'));

console.log('\n=== 3820 - 3980 ===');
console.log(lines.slice(3820, 3980).map((l, i) => `${3821+i}: ${l}`).join('\n'));
