const fs = require('fs');
const APP_PATH = 'C:/major project/frontend/app.js';

let content = fs.readFileSync(APP_PATH, 'utf8');

// 1. Replace old SVG toggle for login pwd toggle (text → SVG)
const OLD_LOGIN_TOGGLE = `      btnTogglePwd.addEventListener('click', () => {\r\n        const isPwd = pwdInput.type === 'password';\r\n        pwdInput.type = isPwd ? 'text' : 'password';\r\n        btnTogglePwd.textContent = isPwd ? '🔒' : '👁️';\r\n      });`;
const NEW_LOGIN_TOGGLE = `      btnTogglePwd.addEventListener('click', () => {
        const isPwd = pwdInput.type === 'password';
        pwdInput.type = isPwd ? 'text' : 'password';
        const icon = document.getElementById('eyeIconLogin');
        if (icon) {
          if (isPwd) {
            icon.innerHTML = '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/><line x1="1" y1="1" x2="23" y2="23"/>';
          } else {
            icon.innerHTML = '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>';
          }
        }
        btnTogglePwd.setAttribute('aria-label', isPwd ? 'Hide password' : 'Show password');
      });`;
if (content.includes(OLD_LOGIN_TOGGLE)) {
  content = content.replace(OLD_LOGIN_TOGGLE, NEW_LOGIN_TOGGLE);
  console.log('✓ Login pwd toggle updated');
} else {
  console.log('⚠ Could not find old login toggle — skipping');
}

// 2. Replace old register toggle
const OLD_REG_TOGGLE = `      btnToggleReg.addEventListener('click', () => {\r\n        const isPwd = regPwdIn.type === 'password';\r\n        regPwdIn.type = isPwd ? 'text' : 'password';\r\n        btnToggleReg.textContent = isPwd ? '🔒' : '👁️';\r\n      });`;
const NEW_REG_TOGGLE = `      btnToggleReg.addEventListener('click', () => {
        const isPwd = regPwdIn.type === 'password';
        regPwdIn.type = isPwd ? 'text' : 'password';
        const svgEl = btnToggleReg.querySelector('svg');
        if (svgEl) {
          svgEl.innerHTML = isPwd
            ? '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94"/><path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19"/><line x1="1" y1="1" x2="23" y2="23"/>'
            : '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>';
        }
        btnToggleReg.setAttribute('aria-label', isPwd ? 'Hide password' : 'Show password');
      });`;
if (content.includes(OLD_REG_TOGGLE)) {
  content = content.replace(OLD_REG_TOGGLE, NEW_REG_TOGGLE);
  console.log('✓ Register pwd toggle updated');
} else {
  console.log('⚠ Could not find old register toggle — skipping');
}

// 3. Add password strength + confirm match listeners after eval pill section
const AFTER_EVAL_PILLS = `    // 3. Role Selection Cards`;
const PWD_STRENGTH_CODE = `    // Password strength meter
    const regPwdStrengthField = document.getElementById('regPassword');
    if (regPwdStrengthField) {
      regPwdStrengthField.addEventListener('input', () => {
        const val = regPwdStrengthField.value;
        const fill = document.getElementById('regPwdStrengthFill');
        const label = document.getElementById('regPwdStrengthLabel');
        if (!fill || !label) return;
        let strength = 0;
        if (val.length >= 8) strength++;
        if (/[A-Z]/.test(val)) strength++;
        if (/[0-9]/.test(val)) strength++;
        if (/[^A-Za-z0-9]/.test(val)) strength++;
        const widths = ['0%', '25%', '50%', '75%', '100%'];
        const colors = ['transparent', '#D66B52', '#D7A94D', '#4db6D7', '#4caf72'];
        const labels = ['', 'Weak', 'Fair', 'Good', 'Strong'];
        const labelColors = ['', '#D66B52', '#D7A94D', '#4db6D7', '#4caf72'];
        fill.style.width = widths[strength];
        fill.style.background = colors[strength];
        label.textContent = val.length > 0 ? labels[strength] : '';
        label.style.color = labelColors[strength];
      });
    }

    // Confirm password match hint
    const regConfirmField = document.getElementById('regConfirmPassword');
    if (regConfirmField && regPwdStrengthField) {
      const checkMatch = () => {
        const hint = document.getElementById('regPwdMatchHint');
        if (!hint) return;
        if (!regConfirmField.value) { hint.textContent = ''; return; }
        if (regConfirmField.value === regPwdStrengthField.value) {
          hint.textContent = '✓ Passwords match';
          hint.style.color = '#4caf72';
          regConfirmField.classList.remove('auth-input-error');
          regConfirmField.classList.add('auth-input-success');
        } else {
          hint.textContent = '✗ Passwords do not match';
          hint.style.color = '#D66B52';
          regConfirmField.classList.add('auth-input-error');
          regConfirmField.classList.remove('auth-input-success');
        }
      };
      regConfirmField.addEventListener('input', checkMatch);
      regPwdStrengthField.addEventListener('input', () => { if (regConfirmField.value) checkMatch(); });
    }

    // 3. Role Selection Cards`;

if (content.includes(AFTER_EVAL_PILLS)) {
  content = content.replace(AFTER_EVAL_PILLS, PWD_STRENGTH_CODE);
  console.log('✓ Password strength and confirm match listeners added');
} else {
  console.log('⚠ Could not find "3. Role Selection Cards" — skipping pwd strength injection');
}

// 4. Make login submit button show loading state and handle new pill class
const OLD_EVAL_PILLS = `    // Evaluator Quick-Fill Helper Pills
    document.querySelectorAll('.btn-test-pill').forEach(pill => {`;
const NEW_EVAL_PILLS = `    // Evaluator Quick-Fill Helper Pills — supports both old .btn-test-pill and new .auth-eval-pill
    document.querySelectorAll('.btn-test-pill, .auth-eval-pill').forEach(pill => {`;
if (content.includes(OLD_EVAL_PILLS)) {
  content = content.replace(OLD_EVAL_PILLS, NEW_EVAL_PILLS);
  console.log('✓ Eval pill selector updated');
}

// 5. Add loading state on login submit btn
const OLD_LOGIN_SUBMIT_FIND = `id="btnDedicatedLoginSubmit"`;
// We patch the existing login form submit handler to toggle loading class
const OLD_LOGIN_HANDLER = `  const loginForm = document.getElementById('dedicatedLoginForm');`;
if (content.includes(OLD_LOGIN_HANDLER)) {
  const LOGIN_HANDLER_PATCH = `  // --- Auth Submit Button Loading State Helpers ---
  function setAuthBtnLoading(btnId, loading) {
    const btn = document.getElementById(btnId);
    if (!btn) return;
    if (loading) { btn.classList.add('loading'); btn.disabled = true; }
    else { btn.classList.remove('loading'); btn.disabled = false; }
  }

  const loginForm = document.getElementById('dedicatedLoginForm');`;
  content = content.replace(OLD_LOGIN_HANDLER, LOGIN_HANDLER_PATCH);
  console.log('✓ Auth btn loading state helper added');
}

// 6. Apply loading state on login form submission
const OLD_LOGIN_SUBMIT = `  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();`;
const NEW_LOGIN_SUBMIT = `  loginForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    setAuthBtnLoading('btnDedicatedLoginSubmit', true);`;
if (content.includes(OLD_LOGIN_SUBMIT)) {
  content = content.replace(OLD_LOGIN_SUBMIT, NEW_LOGIN_SUBMIT);
  // Also find where we clear feedback after login and reset btn loading
  console.log('✓ Login submit loading state applied');
}

// 7. Apply loading state on register form
const OLD_REG_SUBMIT = `  regForm.addEventListener('submit', async (e) => {
    e.preventDefault();`;
const NEW_REG_SUBMIT = `  regForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    setAuthBtnLoading('btnRegisterSubmit', true);`;
if (content.includes(OLD_REG_SUBMIT)) {
  content = content.replace(OLD_REG_SUBMIT, NEW_REG_SUBMIT);
  console.log('✓ Register submit loading state applied');
}

fs.writeFileSync(APP_PATH, content, 'utf8');
console.log('\napp.js auth UI patches complete.');
