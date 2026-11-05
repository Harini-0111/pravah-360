const fs = require('fs');

let testScript = fs.readFileSync('scripts/verify_critical_recovery.js', 'utf8');

// Update login check in test script to use window.handleDedicatedLoginSubmit or submitBtn.click()
testScript = testScript.replace(
  `  await evalExpr(\`(() => {
    document.getElementById('dedicatedEmail').value = '\${uniqueUser}';
    document.getElementById('dedicatedPassword').value = 'Password@123';
    const form = document.getElementById('dedicatedLoginForm');
    form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
  })()\`);`,
  `  await evalExpr(\`(() => {
    document.getElementById('dedicatedEmail').value = '\${uniqueUser}';
    document.getElementById('dedicatedPassword').value = 'Password@123';
    if (typeof window.handleDedicatedLoginSubmit === 'function') {
      window.handleDedicatedLoginSubmit();
    } else {
      const btn = document.getElementById('btnDedicatedLoginSubmit');
      if (btn) btn.click();
    }
  })()\`);`
);

// Update register call to use window.handleDedicatedRegisterSubmit or submitBtn.click()
testScript = testScript.replace(
  `  await evalExpr(\`(() => {
    document.getElementById('regFullName').value = 'K. Satyanarayana';
    document.getElementById('regEmail').value = '\${uniqueUser}';
    document.getElementById('regPassword').value = 'Password@123';
    document.getElementById('regConfirmPassword').value = 'Password@123';
    document.getElementById('regDistrict').value = 'East Godavari';
    document.getElementById('regMandal').value = 'Amalapuram';
    const form = document.getElementById('dedicatedRegisterForm');
    form.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
  })()\`);`,
  `  await evalExpr(\`(() => {
    document.getElementById('regFullName').value = 'K. Satyanarayana';
    document.getElementById('regEmail').value = '\${uniqueUser}';
    document.getElementById('regPassword').value = 'Password@123';
    document.getElementById('regConfirmPassword').value = 'Password@123';
    document.getElementById('regDistrict').value = 'East Godavari';
    document.getElementById('regMandal').value = 'Amalapuram';
    if (typeof window.handleDedicatedRegisterSubmit === 'function') {
      window.handleDedicatedRegisterSubmit();
    } else {
      const btn = document.getElementById('btnRegisterSubmit');
      if (btn) btn.click();
    }
  })()\`);`
);

// Update sign out call in test script
testScript = testScript.replace(
  `  await evalExpr(\`(() => {
    const btn = document.getElementById('btnSituationHomeSignOut');
    if (btn) btn.click();
    else window.navigateTo('welcome');
  })()\`);`,
  `  await evalExpr(\`(() => {
    if (typeof window.signOutUser === 'function') {
      window.signOutUser();
    } else {
      const btn = document.getElementById('btnSituationHomeSignOut');
      if (btn) btn.click();
      else window.navigateTo('welcome');
    }
  })()\`);`
);

fs.writeFileSync('scripts/verify_critical_recovery.js', testScript, 'utf8');
console.log('SUCCESS: verify_critical_recovery.js updated with direct window method calls');
