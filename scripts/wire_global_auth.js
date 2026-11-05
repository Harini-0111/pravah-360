const fs = require('fs');

let js = fs.readFileSync('frontend/app.js', 'utf8');

// 1. Remove lines 3846-3865 (the stale btnLandingLangToggle listener)
const staleToggleRegex = /\/\/ Landing Telugu Toggle[\s\S]*?btnLang\.addEventListener\('click'[\s\S]*?\}\);\s*\}/;
if (staleToggleRegex.test(js)) {
  js = js.replace(staleToggleRegex, `// Landing Global Language Toggle
    const btnLang = document.getElementById('btnLandingLangToggle');
    if (btnLang) {
      btnLang.addEventListener('click', () => {
        if (typeof window.toggleGlobalLanguage === 'function') {
          window.toggleGlobalLanguage();
        }
      });
    }`);
  console.log('SUCCESS: Stale btnLandingLangToggle replaced via regex');
} else {
  console.log('Notice: staleToggleRegex did not match directly');
}

// 2. Add global handlers on window for Login, Register, SignOut, and getAuthenticatedUser
const globalAuthHandlers = `
  // Globally Accessible Handlers for Form Submissions and Auth Actions
  window.handleDedicatedLoginSubmit = async function(e) {
    if (e && e.preventDefault) e.preventDefault();
    const email = document.getElementById('dedicatedEmail')?.value.trim();
    const password = document.getElementById('dedicatedPassword')?.value;
    const feedback = document.getElementById('dedicatedLoginFeedback');
    const submitBtn = document.getElementById('btnDedicatedLoginSubmit');

    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = 'Verifying credentials...';
    }
    if (feedback) feedback.style.display = 'none';

    try {
      const res = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      const data = await res.json();

      if (res.ok && data.status === 'authenticated') {
        authenticatedUser = data.user;
        window.authenticatedUser = data.user;
        if (feedback) {
          feedback.className = 'login-feedback success';
          feedback.style.display = 'block';
          feedback.textContent = '✓ Sign in successful! Redirecting...';
        }
        updateUserBadges();

        setTimeout(() => {
          if (authenticatedUser.role === 'citizen') {
            navigateTo('role-select');
          } else {
            navigateTo('situation-home');
          }
        }, 500);
      } else {
        if (feedback) {
          feedback.className = 'login-feedback error';
          feedback.style.display = 'block';
          feedback.textContent = data.detail || 'Invalid email or password.';
        }
      }
    } catch (err) {
      if (feedback) {
        feedback.className = 'login-feedback error';
        feedback.style.display = 'block';
        feedback.textContent = 'Connection error. Please try again.';
      }
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = (window.currentAppLang === 'te') ? 'ఖాతాలోకి సైన్ ఇన్ చేయండి →' : 'Sign In to Account →';
      }
    }
  };

  window.handleDedicatedRegisterSubmit = async function(e) {
    if (e && e.preventDefault) e.preventDefault();
    const full_name = document.getElementById('regFullName')?.value.trim();
    const email = document.getElementById('regEmail')?.value.trim();
    const password = document.getElementById('regPassword')?.value;
    const confirmPassword = document.getElementById('regConfirmPassword')?.value;
    const district = document.getElementById('regDistrict')?.value || 'East Godavari';
    const mandal = document.getElementById('regMandal')?.value || 'Rajamahendravaram Urban';
    const feedback = document.getElementById('dedicatedRegisterFeedback');
    const submitBtn = document.getElementById('btnRegisterSubmit');

    if (feedback) feedback.style.display = 'none';

    if (password !== confirmPassword) {
      if (feedback) {
        feedback.className = 'login-feedback error';
        feedback.style.display = 'block';
        feedback.textContent = 'Passwords do not match. Please re-enter.';
      }
      return;
    }

    if (password.length < 8) {
      if (feedback) {
        feedback.className = 'login-feedback error';
        feedback.style.display = 'block';
        feedback.textContent = 'Password must be at least 8 characters long.';
      }
      return;
    }

    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = 'Creating account...';
    }

    try {
      const res = await fetch('/api/v1/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ full_name, email, password, district, mandal })
      });
      const data = await res.json();

      if (res.ok && data.status === 'registered') {
        authenticatedUser = data.user;
        window.authenticatedUser = data.user;
        if (appState.selectedLocation) {
          appState.selectedLocation.mandalName = mandal;
          appState.selectedLocation.districtName = district;
          appState.selectedLocation.name = mandal;
        }
        if (feedback) {
          feedback.className = 'login-feedback success';
          feedback.style.display = 'block';
          feedback.textContent = '✓ Account created successfully! Redirecting...';
        }
        updateUserBadges();

        setTimeout(() => {
          navigateTo('role-select');
        }, 500);
      } else {
        if (feedback) {
          feedback.className = 'login-feedback error';
          feedback.style.display = 'block';
          feedback.textContent = data.detail || 'Registration failed. Please check inputs.';
        }
      }
    } catch (err) {
      if (feedback) {
        feedback.className = 'login-feedback error';
        feedback.style.display = 'block';
        feedback.textContent = 'Network error during registration. Please try again.';
      }
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = (window.currentAppLang === 'te') ? 'ఖాతాను సృష్టించి కొనసాగించండి →' : 'Create Account & Proceed →';
      }
    }
  };

  window.signOutUser = async function() {
    try {
      await fetch('/api/v1/auth/logout', { method: 'POST' });
    } catch (e) {}
    authenticatedUser = null;
    window.authenticatedUser = null;
    navigateTo('welcome');
  };
`;

// Insert the global handlers before initMultiPageEntryControllers
if (!js.includes('window.handleDedicatedLoginSubmit =')) {
  js = js.replace('function initMultiPageEntryControllers() {', `${globalAuthHandlers}\n  function initMultiPageEntryControllers() {`);
  console.log('SUCCESS: Global auth handlers added to app.js');
}

fs.writeFileSync('frontend/app.js', js, 'utf8');
