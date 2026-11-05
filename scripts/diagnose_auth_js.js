const fs = require('fs');
const js = fs.readFileSync('frontend/app.js', 'utf8');

console.log('--- JS AUTH LISTENERS ---');
console.log('dedicatedLoginForm listener:', js.includes('dedicatedLoginForm'));
console.log('dedicatedRegisterForm listener:', js.includes('dedicatedRegisterForm'));
console.log('btnDedicatedLoginSubmit listener:', js.includes('btnDedicatedLoginSubmit'));
console.log('btnRegisterSubmit listener:', js.includes('btnRegisterSubmit'));
console.log('loginForm listener:', js.includes('loginForm'));

// Let's print out lines around dedicatedLoginForm
const lines = js.split('\n');
lines.forEach((line, idx) => {
  if (line.includes('dedicatedLoginForm') || line.includes('dedicatedRegisterForm') || line.includes('btnDedicatedLoginSubmit') || line.includes('btnRegisterSubmit') || line.includes('/api/v1/auth/login') || line.includes('/api/v1/auth/register')) {
    console.log(`${idx+1}: ${line.trim()}`);
  }
});
