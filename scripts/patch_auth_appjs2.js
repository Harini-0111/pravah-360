const fs = require('fs');
const APP_PATH = 'C:/major project/frontend/app.js';

let content = fs.readFileSync(APP_PATH, 'utf8');

// Fix pwd toggles - search for the actual content patterns
// Login toggle
const loginToggleStart = content.indexOf("btnTogglePwd.addEventListener('click', () =>");
if (loginToggleStart !== -1) {
  // Find the end of this event listener block
  const blockEnd = content.indexOf('});', loginToggleStart) + 3;
  const oldBlock = content.slice(loginToggleStart, blockEnd);
  console.log('Old login toggle block found, length:', oldBlock.length);
  const newBlock = `btnTogglePwd.addEventListener('click', () => {
        const isPwd = pwdInput.type === 'password';
        pwdInput.type = isPwd ? 'text' : 'password';
        const icon = document.getElementById('eyeIconLogin');
        if (icon) {
          if (isPwd) {
            icon.innerHTML = '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/>';
          } else {
            icon.innerHTML = '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>';
          }
        }
        btnTogglePwd.setAttribute('aria-label', isPwd ? 'Hide password' : 'Show password');
      });`;
  content = content.slice(0, loginToggleStart) + newBlock + content.slice(blockEnd);
  console.log('✓ Login pwd toggle updated');
} else {
  console.log('⚠ Login toggle listener not found');
}

// Register toggle
const regToggleStart = content.indexOf("btnToggleReg.addEventListener('click', () =>");
if (regToggleStart !== -1) {
  const blockEnd = content.indexOf('});', regToggleStart) + 3;
  const oldBlock = content.slice(regToggleStart, blockEnd);
  console.log('Old register toggle block found, length:', oldBlock.length);
  const newBlock = `btnToggleReg.addEventListener('click', () => {
        const isPwd = regPwdIn.type === 'password';
        regPwdIn.type = isPwd ? 'text' : 'password';
        const svgEl = btnToggleReg.querySelector('svg');
        if (svgEl) {
          svgEl.innerHTML = isPwd
            ? '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/>'
            : '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>';
        }
        btnToggleReg.setAttribute('aria-label', isPwd ? 'Hide password' : 'Show password');
      });`;
  content = content.slice(0, regToggleStart) + newBlock + content.slice(blockEnd);
  console.log('✓ Register pwd toggle updated');
} else {
  console.log('⚠ Register toggle listener not found');
}

// Also wire the loading state reset after successful login
const LOGIN_SUCCESS_PATTERN = "navigateTo('role-select');";
// Ensure loading resets on any response from login form
const RESET_ON_LOGIN_ERROR = "setAuthBtnLoading('btnDedicatedLoginSubmit', false);";
// Find login form submission and add reset after try/catch
const loginFormIdx = content.indexOf("loginForm.addEventListener('submit'");
if (loginFormIdx !== -1) {
  // Find the catch block for login
  const loginCatchIdx = content.indexOf("} catch (err) {", loginFormIdx);
  const loginCatchEnd = content.indexOf("}", loginCatchIdx + 1);
  if (loginCatchIdx !== -1) {
    const insertPos = loginCatchIdx + "} catch (err) {\n".length;
    // Check if already added
    if (!content.slice(loginCatchIdx, loginCatchIdx + 100).includes('setAuthBtnLoading')) {
      content = content.slice(0, insertPos) + `        setAuthBtnLoading('btnDedicatedLoginSubmit', false);\n` + content.slice(insertPos);
      console.log('✓ Login error reset added');
    }
  }
}

// Same for register form
const regFormIdx = content.indexOf("regForm.addEventListener('submit'");
if (regFormIdx !== -1) {
  const regCatchIdx = content.indexOf("} catch (err) {", regFormIdx);
  if (regCatchIdx !== -1) {
    const insertPos2 = regCatchIdx + "} catch (err) {\n".length;
    if (!content.slice(regCatchIdx, regCatchIdx + 100).includes('setAuthBtnLoading')) {
      content = content.slice(0, insertPos2) + `        setAuthBtnLoading('btnRegisterSubmit', false);\n` + content.slice(insertPos2);
      console.log('✓ Register error reset added');
    }
  }
}

// Also show success overlay on successful registration before redirect
const REG_SUCCESS_NAVIGATE = "navigateTo('role-select');";
// Find it in the register submit context
const regSubmitIdx = content.indexOf("regForm.addEventListener('submit'");
if (regSubmitIdx !== -1) {
  const regSuccessNavigate = content.indexOf(REG_SUCCESS_NAVIGATE, regSubmitIdx);
  if (regSuccessNavigate !== -1 && !content.slice(regSuccessNavigate - 200, regSuccessNavigate).includes('regSuccessOverlay')) {
    const before = content.slice(0, regSuccessNavigate);
    const after = content.slice(regSuccessNavigate + REG_SUCCESS_NAVIGATE.length);
    const overlay = `const successOverlay = document.getElementById('regSuccessOverlay');
            if (successOverlay) { successOverlay.style.display = 'flex'; }
            setTimeout(() => { navigateTo('role-select'); }, 1500);`;
    content = before + overlay + after;
    console.log('✓ Register success overlay wired');
  }
}

fs.writeFileSync(APP_PATH, content, 'utf8');
console.log('\napp.js patch 2 complete.');
