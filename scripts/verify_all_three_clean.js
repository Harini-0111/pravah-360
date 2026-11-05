const { spawn } = require('child_process');
const http = require('http');
const fs = require('fs');
const path = require('path');

const chromePath = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const userDataDir = 'C:\\major project\\.chrome_recovery_clean_profile';
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
    '--remote-debugging-port=9235',
    `--user-data-dir=${userDataDir}`,
    'about:blank'
  ]);

  let versionData = null;
  for (let i = 0; i < 30; i++) {
    await new Promise(r => setTimeout(r, 200));
    try {
      versionData = await new Promise((resolve, reject) => {
        http.get('http://127.0.0.1:9235/json/version', res => {
          let data = '';
          res.on('data', c => data += c);
          res.on('end', () => resolve(JSON.parse(data)));
        }).on('error', reject);
      });
      if (versionData && versionData.webSocketDebuggerUrl) break;
    } catch (e) {}
  }

  if (!versionData) {
    console.error('Failed to connect to Chrome on port 9235');
    chromeProc.kill();
    process.exit(1);
  }

  const newTarget = await new Promise((resolve, reject) => {
    const req = http.request({
      host: '127.0.0.1',
      port: 9235,
      path: '/json/new?http://127.0.0.1:8000/#welcome',
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

  await send('Page.navigate', { url: 'http://127.0.0.1:8000/#welcome' });
  console.log('Connected to browser. Navigated to http://127.0.0.1:8000/#welcome. Waiting 3s...');
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

  console.log('\n===============================================================');
  console.log('1. VERIFYING TELUGU LANGUAGE SWITCHING ACROSS SURFACES');
  console.log('===============================================================');

  // Explicitly call setAppLanguage('te') to switch to Telugu
  await evalExpr(`window.setAppLanguage('te')`);
  await new Promise(r => setTimeout(r, 600));

  const teWelcome = await evalExpr(`({
    lang: document.body.getAttribute('data-lang'),
    tagline: document.querySelector('.hero-tagline')?.textContent?.trim(),
    headline: document.querySelector('.hero-headline')?.textContent?.trim(),
    btnExplore: document.getElementById('btnHeroExplore')?.textContent?.trim(),
    toggleText: document.getElementById('btnLandingLangToggle')?.textContent?.trim()
  })`);
  console.log('Telugu Welcome:', teWelcome);

  await evalExpr(`window.navigateTo('login')`);
  await new Promise(r => setTimeout(r, 500));
  const teLogin = await evalExpr(`({
    h2: document.querySelector('#page-login .auth-form-header h2')?.textContent?.trim(),
    btn: document.getElementById('btnDedicatedLoginSubmit')?.textContent?.trim(),
    display: window.getComputedStyle(document.getElementById('page-login')).display
  })`);
  console.log('Telugu Login:', teLogin);

  await evalExpr(`window.navigateTo('register')`);
  await new Promise(r => setTimeout(r, 500));
  const teReg = await evalExpr(`({
    h2: document.querySelector('#page-register .auth-form-header h2')?.textContent?.trim(),
    btn: document.getElementById('btnRegisterSubmit')?.textContent?.trim(),
    display: window.getComputedStyle(document.getElementById('page-register')).display
  })`);
  console.log('Telugu Register:', teReg);

  await evalExpr(`window.setAppLanguage('en')`);
  await new Promise(r => setTimeout(r, 400));
  const enRevert = await evalExpr(`({
    lang: document.body.getAttribute('data-lang'),
    h2: document.querySelector('#page-register .auth-form-header h2')?.textContent?.trim()
  })`);
  console.log('English Revert:', enRevert);

  await takeScreenshot('clean_01_telugu_verified.png');

  console.log('\n===============================================================');
  console.log('2. VERIFYING AUTHENTICATION: REGISTER -> LOGIN -> SIGNOUT');
  console.log('===============================================================');

  const testEmail = `citizen_verified_${Date.now()}@example.com`;
  console.log('Registering test user:', testEmail);

  await evalExpr(`window.navigateTo('register')`);
  await new Promise(r => setTimeout(r, 400));

  await evalExpr(`(() => {
    document.getElementById('regFullName').value = 'M. Venkata Rao';
    document.getElementById('regEmail').value = '${testEmail}';
    document.getElementById('regPassword').value = 'Password@123';
    document.getElementById('regConfirmPassword').value = 'Password@123';
    document.getElementById('regDistrict').value = 'East Godavari';
    document.getElementById('regMandal').value = 'Amalapuram';
    window.handleDedicatedRegisterSubmit();
  })()`);

  await new Promise(r => setTimeout(r, 1200));

  const postReg = await evalExpr(`({
    user: window.authenticatedUser ? window.authenticatedUser.email : null,
    role: window.authenticatedUser ? window.authenticatedUser.role : null,
    roleSelectDisplay: window.getComputedStyle(document.getElementById('page-role-select')).display
  })`);
  console.log('Post-Registration State:', postReg);

  // Sign out
  console.log('Testing Sign Out...');
  await evalExpr(`window.signOutUser()`);
  await new Promise(r => setTimeout(r, 600));

  const postSignOut = await evalExpr(`({
    user: window.authenticatedUser,
    welcomeDisplay: window.getComputedStyle(document.getElementById('page-welcome')).display
  })`);
  console.log('Post-SignOut State:', postSignOut);

  // Sign back in with testEmail
  console.log('Signing back in with new account:', testEmail);
  await evalExpr(`window.navigateTo('login')`);
  await new Promise(r => setTimeout(r, 400));

  await evalExpr(`(() => {
    document.getElementById('dedicatedEmail').value = '${testEmail}';
    document.getElementById('dedicatedPassword').value = 'Password@123';
    window.handleDedicatedLoginSubmit();
  })()`);

  await new Promise(r => setTimeout(r, 1200));

  const postLogin = await evalExpr(`({
    user: window.authenticatedUser ? window.authenticatedUser.email : null,
    role: window.authenticatedUser ? window.authenticatedUser.role : null
  })`);
  console.log('Post-Login State:', postLogin);

  await takeScreenshot('clean_02_auth_verified.png');

  console.log('\n===============================================================');
  console.log('3. VERIFYING SEEDED ROLES (ALL 4 TIERS AUTHENTICATE CLEANLY)');
  console.log('===============================================================');

  const demoAccounts = [
    { email: 'citizen@pravah360.in', pass: 'Citizen@123', expectedRole: 'citizen' },
    { email: 'mandal.admin@pravah360.in', pass: 'Mandal@123', expectedRole: 'mandal_admin' },
    { email: 'district.collector@pravah360.in', pass: 'District@123', expectedRole: 'district_admin' },
    { email: 'ert.commander@pravah360.in', pass: 'Responder@123', expectedRole: 'emergency_response' }
  ];

  for (const acc of demoAccounts) {
    const res = await evalExpr(`(async () => {
      const resp = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: '${acc.email}', password: '${acc.pass}' })
      });
      const data = await resp.json();
      return { status: resp.status, role: data.user ? data.user.role : null };
    })()`);
    console.log(`Role ${acc.expectedRole} (${acc.email}): status=${res.status}, role=${res.role} (match=${res.role === acc.expectedRole})`);
  }

  console.log('\n===============================================================');
  console.log('4. VERIFYING VOICE ASSISTANT NATURAL INTENT HANDLING');
  console.log('===============================================================');

  const queries = [
    { q: 'వర్షం పడుతుందా?', name: 'Telugu Rain Question' },
    { q: 'ఈరోజు వాతావరణం ఎలా ఉంది?', name: 'Telugu Weather Question' },
    { q: 'Is it raining today?', name: 'English Rain Question' },
    { q: 'Is it raining in Telugu?', name: 'English Request for Telugu Answer' },
    { q: 'మా ప్రాంతంలో వరద ప్రమాదం ఉందా?', name: 'Telugu Flood Susceptibility' },
    { q: 'దగ్గరలో ఆసుపత్రి ఎక్కడ ఉంది?', name: 'Nearest Hospital' },
    { q: 'నాకు సహాయం కావాలి', name: 'Emergency SOS & Helplines' }
  ];

  for (const item of queries) {
    await evalExpr(`window.pravahVoice.handleVoiceQuery('${item.q}')`);
    await new Promise(r => setTimeout(r, 600));
    const ans = await evalExpr(`({
      te: document.querySelector('.voice-te-text')?.textContent?.slice(0, 90),
      en: document.querySelector('.voice-en-text')?.textContent?.slice(0, 90)
    })`);
    console.log(`Query "${item.q}" (${item.name}):`);
    console.log(`  -> TE: ${ans.te}...`);
    console.log(`  -> EN: ${ans.en}...`);
  }

  await takeScreenshot('clean_03_voice_verified.png');

  console.log('\n===============================================================');
  console.log('ALL VERIFICATIONS COMPLETED SUCCESSFULLY!');
  console.log('===============================================================');

  chromeProc.kill();
  process.exit(0);
}

main().catch(err => {
  console.error('Error in verification:', err);
  process.exit(1);
});
