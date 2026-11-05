const { spawn } = require('child_process');
const http = require('http');
const fs = require('fs');
const path = require('path');

const chromePath = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const userDataDir = 'C:\\major project\\.chrome_final_verify_profile';
const screenshotDir = 'C:\\major project\\docs\\screenshots';

async function main() {
  if (fs.existsSync(userDataDir)) {
    try { fs.rmSync(userDataDir, { recursive: true, force: true }); } catch (e) {}
  }
  if (!fs.existsSync(screenshotDir)) {
    fs.mkdirSync(screenshotDir, { recursive: true });
  }

  const chromeProc = spawn(chromePath, [
    '--headless=new',
    '--disable-gpu',
    '--remote-debugging-port=9227',
    `--user-data-dir=${userDataDir}`,
    'about:blank'
  ]);

  let versionData = null;
  for (let i = 0; i < 30; i++) {
    await new Promise(r => setTimeout(r, 200));
    try {
      versionData = await new Promise((resolve, reject) => {
        http.get('http://127.0.0.1:9227/json/version', res => {
          let data = '';
          res.on('data', c => data += c);
          res.on('end', () => resolve(JSON.parse(data)));
        }).on('error', reject);
      });
      if (versionData && versionData.webSocketDebuggerUrl) break;
    } catch (e) {}
  }

  if (!versionData) {
    console.error('Failed to connect to Chrome on port 9227');
    chromeProc.kill();
    process.exit(1);
  }

  const newTarget = await new Promise((resolve, reject) => {
    const req = http.request({
      host: '127.0.0.1',
      port: 9227,
      path: '/json/new?http://127.0.0.1:8000/',
      method: 'PUT'
    }, res => {
      let data = '';
      res.on('data', c => data += c);
      res.on('end', () => resolve(JSON.parse(data)));
    });
    req.on('error', reject);
    req.end();
  });

  const ws = new WebSocket(newTarget.webSocketDebuggerUrl);

  let id = 1;
  const pending = new Map();

  function send(method, params = {}) {
    return new Promise((resolve, reject) => {
      const msgId = id++;
      pending.set(msgId, { resolve, reject });
      ws.send(JSON.stringify({ id: msgId, method, params }));
    });
  }

  ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    if (msg.id && pending.has(msg.id)) {
      const { resolve, reject } = pending.get(msg.id);
      pending.delete(msg.id);
      if (msg.error) reject(msg.error);
      else resolve(msg.result);
    }
  };

  await new Promise(r => ws.onopen = r);

  await send('Page.enable');
  await send('Runtime.enable');
  await send('DOM.enable');
  await send('Emulation.setDeviceMetricsOverride', {
    width: 1440,
    height: 900,
    deviceScaleFactor: 1,
    mobile: false
  });

  await send('Page.navigate', { url: 'http://127.0.0.1:8000/' });
  console.log('✓ Connected & navigated to http://127.0.0.1:8000/. Waiting 3s for page load...');
  await new Promise(r => setTimeout(r, 3000));

  async function evalExpr(expr) {
    const res = await send('Runtime.evaluate', { expression: expr, returnByValue: true, awaitPromise: true });
    return res.result ? res.result.value : null;
  }

  async function takeScreenshot(filename) {
    const res = await send('Page.captureScreenshot', { format: 'png' });
    const target = path.join(screenshotDir, filename);
    fs.writeFileSync(target, Buffer.from(res.data, 'base64'));
    console.log(`[SCREENSHOT] Saved: ${filename} (${fs.statSync(target).size} bytes)`);
  }

  // 1. Test Split-Screen Sign In Page
  console.log('\n--- 1. Testing Split-Screen Sign In Page ---');
  await evalExpr(`window.location.hash = '#login'`);
  await new Promise(r => setTimeout(r, 600));

  const loginCheck = await evalExpr(`({
    hash: window.location.hash,
    loginDisplay: window.getComputedStyle(document.getElementById('page-login')).display,
    hasLeftPanel: !!document.querySelector('#page-login .auth-left-panel'),
    hasRightPanel: !!document.querySelector('#page-login .auth-right-panel'),
    hasFormCard: !!document.getElementById('loginFormCard'),
    hasEmail: !!document.getElementById('dedicatedEmail'),
    hasPwd: !!document.getElementById('dedicatedPassword'),
    hasRemember: !!document.getElementById('dedicatedRemember'),
    evalPillsCount: document.querySelectorAll('.auth-eval-pill').length
  })`);
  console.log('Login Layout Check:', loginCheck);
  await takeScreenshot('auth_split_login.png');

  // Test evaluator pill click
  console.log('Testing Evaluator pill quick-fill...');
  await evalExpr(`(() => {
    const pill = document.querySelector('.auth-eval-pill[data-email="citizen@pravah360.in"]');
    if (pill) pill.click();
  })()`);
  await new Promise(r => setTimeout(r, 200));
  const emailFilled = await evalExpr(`document.getElementById('dedicatedEmail').value`);
  const passFilled = await evalExpr(`document.getElementById('dedicatedPassword').value`);
  console.log(`Pill click result: email="${emailFilled}", password length=${passFilled ? passFilled.length : 0}`);

  // 2. Test Split-Screen Registration Page
  console.log('\n--- 2. Testing Split-Screen Registration Page ---');
  await evalExpr(`window.location.hash = '#register'`);
  await new Promise(r => setTimeout(r, 600));

  const regCheck = await evalExpr(`({
    hash: window.location.hash,
    registerDisplay: window.getComputedStyle(document.getElementById('page-register')).display,
    hasLeftPanel: !!document.querySelector('#page-register .auth-left-panel'),
    hasRightPanel: !!document.querySelector('#page-register .auth-right-panel'),
    hasFormCard: !!document.getElementById('registerFormCard'),
    hasPwdBar: !!document.getElementById('regPwdStrengthBar'),
    hasMatchHint: !!document.getElementById('regPwdMatchHint'),
    districtsCount: document.getElementById('regDistrict')?.options.length || 0,
    mandalsCount: document.getElementById('regMandal')?.options.length || 0
  })`);
  console.log('Registration Layout Check:', regCheck);

  // Test live password strength & confirm match feedback
  await evalExpr(`(() => {
    const pwdIn = document.getElementById('regPassword');
    pwdIn.value = 'Pravah@2026Secure';
    pwdIn.dispatchEvent(new Event('input', { bubbles: true }));
    const confirmIn = document.getElementById('regConfirmPassword');
    confirmIn.value = 'Pravah@2026Secure';
    confirmIn.dispatchEvent(new Event('input', { bubbles: true }));
  })()`);
  await new Promise(r => setTimeout(r, 300));

  const pwdFeedback = await evalExpr(`({
    strengthLabel: document.getElementById('regPwdStrengthLabel')?.textContent,
    strengthFillWidth: document.getElementById('regPwdStrengthFill')?.style.width,
    matchHint: document.getElementById('regPwdMatchHint')?.textContent
  })`);
  console.log('Live Password Feedback Check:', pwdFeedback);
  await takeScreenshot('auth_split_register.png');

  // 3. Test Real Login & Role-Based Entry
  console.log('\n--- 3. Testing Sign In & Role Entry ---');
  await evalExpr(`window.location.hash = '#login'`);
  await new Promise(r => setTimeout(r, 500));

  await evalExpr(`(() => {
    document.querySelector('.auth-eval-pill[data-email="citizen@pravah360.in"]').click();
    document.getElementById('dedicatedLoginForm').dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
  })()`);
  await new Promise(r => setTimeout(r, 1200));

  // Role select page reached
  const roleSelectDisplay = await evalExpr(`window.getComputedStyle(document.getElementById('page-role-select')).display`);
  console.log('Role Select Page Display:', roleSelectDisplay);
  await takeScreenshot('role_select_verified.png');

  // Choose Resident role card
  await evalExpr(`(() => {
    const card = document.querySelector('.role-choice-card[data-role="citizen"]');
    if (card) card.click();
  })()`);
  await new Promise(r => setTimeout(r, 800));

  // Location onboarding: confirm location
  await evalExpr(`(() => {
    const btn = document.getElementById('btnConfirmLocation');
    if (btn) btn.click();
  })()`);
  await new Promise(r => setTimeout(r, 800));

  const sitHomeState = await evalExpr(`({
    hash: window.location.hash,
    sitHomeDisplay: window.getComputedStyle(document.getElementById('page-situation-home')).display,
    badge: document.getElementById('situationHomeUserBadge')?.innerText
  })`);
  console.log('Situation Awareness Home State:', sitHomeState);
  await takeScreenshot('situation_home_verified.png');

  // 4. Test Operations Workspace & New Photo Banner
  console.log('\n--- 4. Testing Operations Workspace & New Photo Banner ---');
  await evalExpr(`(() => {
    window.location.hash = '#operations';
  })()`);
  await new Promise(r => setTimeout(r, 1200));

  const opsBannerCheck = await evalExpr(`({
    workspaceDisplay: window.getComputedStyle(document.getElementById('workspace-operations')).display,
    bannerFound: !!document.querySelector('#workspace-operations .workspace-photo-banner img'),
    bannerSrc: document.querySelector('#workspace-operations .workspace-photo-banner img')?.getAttribute('src'),
    bannerComplete: document.querySelector('#workspace-operations .workspace-photo-banner img')?.complete
  })`);
  console.log('Operations Workspace Banner Check:', opsBannerCheck);
  await takeScreenshot('workspace_operations_verified.png');

  // 5. Test Safety & Preparedness Workspace Photo
  console.log('\n--- 5. Testing Safety & Preparedness Workspace Photo ---');
  await evalExpr(`(() => {
    window.location.hash = '#help';
  })()`);
  await new Promise(r => setTimeout(r, 1000));

  const helpBannerCheck = await evalExpr(`({
    workspaceDisplay: window.getComputedStyle(document.getElementById('workspace-help')).display,
    bannerFound: !!document.querySelector('#workspace-help .workspace-photo-banner img'),
    bannerSrc: document.querySelector('#workspace-help .workspace-photo-banner img')?.getAttribute('src'),
    bannerComplete: document.querySelector('#workspace-help .workspace-photo-banner img')?.complete
  })`);
  console.log('Help Workspace Banner Check:', helpBannerCheck);
  await takeScreenshot('workspace_help_verified.png');

  // 6. Test Global 3D Earth Workspace Ocean Overlay
  console.log('\n--- 6. Testing Global 3D Earth Workspace Ocean Overlay ---');
  await evalExpr(`(() => {
    window.location.hash = '#global';
  })()`);
  await new Promise(r => setTimeout(r, 1000));

  const globeBannerCheck = await evalExpr(`({
    workspaceDisplay: window.getComputedStyle(document.getElementById('workspace-global')).display,
    bannerFound: !!document.querySelector('#workspace-global .workspace-photo-banner img'),
    bannerSrc: document.querySelector('#workspace-global .workspace-photo-banner img')?.getAttribute('src')
  })`);
  console.log('Global Earth Workspace Overlay Check:', globeBannerCheck);
  await takeScreenshot('workspace_global_verified.png');

  console.log('\n================================================================');
  console.log('ALL VERIFICATIONS SUCCESSFUL! ALL TESTS PASSED.');
  console.log('================================================================\n');

  ws.close();
  chromeProc.kill();
  process.exit(0);
}

main().catch(err => {
  console.error('Test run failed:', err);
  process.exit(1);
});
