const fs = require('fs');

const html = fs.readFileSync('frontend/index.html', 'utf8');
const js = fs.readFileSync('frontend/app.js', 'utf8');

console.log('--- HTML CHECK ---');
console.log('page-login exists:', html.includes('id="page-login"'));
console.log('page-register exists:', html.includes('id="page-register"'));
console.log('loginForm in html:', html.includes('id="loginForm"'));
console.log('loginFormCard in html:', html.includes('id="loginFormCard"'));
console.log('dedicatedLoginForm in html:', html.includes('id="dedicatedLoginForm"'));
console.log('dedicatedRegForm in html:', html.includes('id="dedicatedRegForm"'));
console.log('registerForm in html:', html.includes('id="registerForm"'));
console.log('regForm in html:', html.includes('id="regForm"'));

// Find all form tags in html
const forms = html.match(/<form[^>]*>/gi) || [];
console.log('All form tags in HTML:\n', forms.join('\n'));

// Find input IDs related to login / register
const inputs = html.match(/<input[^>]*id="[^"]*"[^>]*>/gi) || [];
console.log('\nRelevant input tags in HTML:');
inputs.forEach(inp => {
  if (inp.includes('Email') || inp.includes('Password') || inp.includes('email') || inp.includes('password') || inp.includes('Name') || inp.includes('role')) {
    console.log(inp);
  }
});

// Check buttons
const buttons = html.match(/<button[^>]*id="[^"]*"[^>]*>/gi) || [];
console.log('\nRelevant buttons in HTML:');
buttons.forEach(btn => {
  if (btn.includes('Login') || btn.includes('Reg') || btn.includes('Submit') || btn.includes('Auth') || btn.includes('Sign')) {
    console.log(btn);
  }
});
