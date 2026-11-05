const fs = require('fs');
const c = fs.readFileSync('C:/major project/backend/app/api/endpoints.py', 'utf8');
const routes = [];
const lines = c.split('\n');
lines.forEach(line => {
  const m = line.match(/@router\.(get|post|put|delete|patch)\(['"]([^'"]+)['"]/i);
  if (m) routes.push(m[1].toUpperCase() + ' /api/v1' + m[2]);
});
console.log('Routes:', routes.length);
routes.forEach(r => console.log(' ', r));
