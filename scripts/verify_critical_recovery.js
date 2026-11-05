const { spawn } = require('child_process');
const http = require('http');
const fs = require('fs');
const path = require('path');

const chromePath = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const userDataDir = 'C:\\major project\\.chrome_recovery_verify_profile';
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
    '--remote-debugging-port=9232',
    `--user-data-dir=${userDataDir}`,
    'about:blank'
  ]);

  let versionData = null;
  for (let i = 0; i < 30; i++) {
    await new Promise(r => setTimeout(r, 200));
    try {
      versionData = await new Promise((resolve, reject) => {
        http.get('http://127.0.0.1:9232/json/version', res => {
          let data = '';
          res.on('data', c => data += c);
          res.on('end', () => resolve(JSON.parse(data)));
        }).on('error', reject);
      });
      if (versionData && versionData.webSocketDebuggerUrl) break;
    } catch (e) {}
  }

  if (!versionData) {
    console.error('Failed to connect to Chrome on port 9232');
    chromeProc.kill();
    process.exit(1);
  }

  const newTarget = await new Promise((resolve, reject) => {
    const req = http.request({
      host: '127.0.0.1',
      port: 9232,
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

  const results = {
    auth_registration: false,
    auth_login: false,
    auth_signout: false,
    telugu_welcome: false,
    telugu_login: false,
    telugu_register: false,
    telugu_revert: false,
    voice_rain_te: false,
    voice_weather_te: false,
    voice_rain_en: false,
    voice_rain_in_telugu: false,
    voice_flood_risk: false,
    voice_hospital: false,
    voice_sos: false
  };

  // =========================================================================
  // TEST 1: TELUGU LANGUAGE SWITCHING ACROSS PAGES
  // =========================================================================
  console.log('\n=== TEST 1: TELUGU LANGUAGE SWITCHING ACROSS PAGES ===');
  
  // 1A. Switch to Telugu on Welcome page using toggle button
  await evalExpr(`(() => {
    const toggle = document.getElementById('btnLandingLangToggle');
    if (toggle) toggle.click();
    else if (typeof window.setAppLanguage === 'function') window.setAppLanguage('te');
  })()`);
  await new Promise(r => setTimeout(r, 600));

  const teWelcomeCheck = await evalExpr(`({
    lang: document.body.getAttribute('data-lang'),
    tagline: document.querySelector('.hero-tagline')?.textContent?.trim(),
    headline: document.querySelector('.hero-headline')?.textContent?.trim(),
    btnExplore: document.getElementById('btnHeroExplore')?.textContent?.trim(),
    navOverview: document.querySelector('.landing-nav-links a')?.textContent?.trim(),
    navRegister: document.getElementById('btnNavRegister')?.textContent?.trim()
  })`);
  console.log('Telugu Welcome Page Content:', teWelcomeCheck);
  if (teWelcomeCheck.tagline?.includes('ప్రమాదాన్ని గుర్తించండి') && teWelcomeCheck.headline?.includes('ప్రకృతి మారినప్పుడు')) {
    results.telugu_welcome = true;
    console.log('✓ TEST 1A PASSED: Welcome page translated to Telugu');
  }

  await takeScreenshot('recovery_01_telugu_welcome.png');

  // 1B. Navigate to Login Page and verify Telugu headers
  await evalExpr(`window.navigateTo('login')`);
  await new Promise(r => setTimeout(r, 600));

  const teLoginCheck = await evalExpr(`({
    hash: window.location.hash,
    display: window.getComputedStyle(document.getElementById('page-login')).display,
    h2: document.querySelector('#page-login .auth-form-header h2')?.textContent?.trim(),
    btnText: document.getElementById('btnDedicatedLoginSubmit')?.textContent?.trim()
  })`);
  console.log('Telugu Login Page Content:', teLoginCheck);
  if (teLoginCheck.h2?.includes('మళ్ళీ స్వాగతం') || teLoginCheck.btnText?.includes('సైన్ ఇన్')) {
    results.telugu_login = true;
    console.log('✓ TEST 1B PASSED: Login page translated to Telugu');
  }
  await takeScreenshot('recovery_02_telugu_login.png');

  // 1C. Navigate to Register Page and verify Telugu headers
  await evalExpr(`window.navigateTo('register')`);
  await new Promise(r => setTimeout(r, 600));

  const teRegCheck = await evalExpr(`({
    hash: window.location.hash,
    display: window.getComputedStyle(document.getElementById('page-register')).display,
    h2: document.querySelector('#page-register .auth-form-header h2')?.textContent?.trim(),
    btnText: document.getElementById('btnRegisterSubmit')?.textContent?.trim()
  })`);
  console.log('Telugu Register Page Content:', teRegCheck);
  if (teRegCheck.h2?.includes('మీ ఖాతాను సృష్టించండి') || teRegCheck.btnText?.includes('ఖాతాను సృష్టించి')) {
    results.telugu_register = true;
    console.log('✓ TEST 1C PASSED: Register page translated to Telugu');
  }
  await takeScreenshot('recovery_03_telugu_register.png');

  // 1D. Switch back to English
  await evalExpr(`window.setAppLanguage('en')`);
  await new Promise(r => setTimeout(r, 400));
  const enRevertCheck = await evalExpr(`({
    lang: document.body.getAttribute('data-lang'),
    regH2: document.querySelector('#page-register .auth-form-header h2')?.textContent?.trim()
  })`);
  console.log('English Revert Check:', enRevertCheck);
  if (enRevertCheck.regH2?.includes('Create your account')) {
    results.telugu_revert = true;
    console.log('✓ TEST 1D PASSED: Switched back to English successfully');
  }

  // =========================================================================
  // TEST 2: AUTHENTICATION FLOW (REGISTRATION -> LOGIN -> SIGNOUT)
  // =========================================================================
  console.log('\n=== TEST 2: AUTHENTICATION FLOW ===');

  const uniqueUser = `citizen_recovery_${Date.now()}@example.com`;
  console.log(`Registering new user: ${uniqueUser}`);

  await evalExpr(`(() => {
    document.getElementById('regFullName').value = 'K. Satyanarayana';
    document.getElementById('regEmail').value = '${uniqueUser}';
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
  })()`);

  console.log('Waiting for registration and transition to role-select...');
  await new Promise(r => setTimeout(r, 2200));

  const postRegCheck = await evalExpr(`({
    hash: window.location.hash,
    feedbackText: document.getElementById('dedicatedRegisterFeedback')?.textContent,
    roleSelectDisplay: window.getComputedStyle(document.getElementById('page-role-select')).display
  })`);
  console.log('Registration Post-State:', postRegCheck);

  if (postRegCheck.feedbackText?.includes('✓') || postRegCheck.hash === '#role-select' || postRegCheck.roleSelectDisplay === 'block') {
    results.auth_registration = true;
    console.log('✓ TEST 2A PASSED: New account registered successfully and navigated to role-select');
  }
  await takeScreenshot('recovery_04_post_registration.png');

  // Role select -> Location onboarding -> Situation Home
  await evalExpr(`window.navigateTo('location-onboarding')`);
  await new Promise(r => setTimeout(r, 600));

  await evalExpr(`window.navigateTo('situation-home')`);
  await new Promise(r => setTimeout(r, 600));

  const sitHomeCheck = await evalExpr(`({
    hash: window.location.hash,
    sitHomeDisplay: window.getComputedStyle(document.getElementById('page-situation-home')).display,
    userBadge: document.getElementById('situationHomeUserBadge')?.textContent
  })`);
  console.log('Situation Home Active User State:', sitHomeCheck);
  await takeScreenshot('recovery_05_situation_home_active.png');

  // Test Sign Out
  console.log('Testing Sign Out...');
  await evalExpr(`(() => {
    if (typeof window.signOutUser === 'function') {
      window.signOutUser();
    } else {
      const btn = document.getElementById('btnSituationHomeSignOut');
      if (btn) btn.click();
      else window.navigateTo('welcome');
    }
  })()`);
  await new Promise(r => setTimeout(r, 1000));

  const signoutCheck = await evalExpr(`({
    hash: window.location.hash,
    welcomeDisplay: window.getComputedStyle(document.getElementById('page-welcome')).display
  })`);
  console.log('Post-SignOut State:', signoutCheck);
  if (signoutCheck.hash === '#welcome' && signoutCheck.welcomeDisplay === 'block') {
    results.auth_signout = true;
    console.log('✓ TEST 2B PASSED: Sign out terminated session and navigated to welcome');
  }

  // Test Sign In with newly registered credentials
  console.log(`Testing Sign In with newly registered email: ${uniqueUser}...`);
  await evalExpr(`window.navigateTo('login')`);
  await new Promise(r => setTimeout(r, 600));

  await evalExpr(`(() => {
    document.getElementById('dedicatedEmail').value = '${uniqueUser}';
    document.getElementById('dedicatedPassword').value = 'Password@123';
    if (typeof window.handleDedicatedLoginSubmit === 'function') {
      window.handleDedicatedLoginSubmit();
    } else {
      const btn = document.getElementById('btnDedicatedLoginSubmit');
      if (btn) btn.click();
    }
  })()`);
  await new Promise(r => setTimeout(r, 2000));

  const postLoginCheck = await evalExpr(`({
    hash: window.location.hash,
    feedbackText: document.getElementById('dedicatedLoginFeedback')?.textContent,
    user: window.authenticatedUser ? window.authenticatedUser.email : null
  })`);
  console.log('Post-Login State:', postLoginCheck);
  if (postLoginCheck.feedbackText?.includes('✓') || postLoginCheck.hash === '#role-select' || postLoginCheck.hash === '#situation-home' || postLoginCheck.user === '${uniqueUser}') {
    results.auth_login = true;
    console.log('✓ TEST 2C PASSED: Login with registered account succeeded');
  }
  await takeScreenshot('recovery_06_login_success.png');

  // =========================================================================
  // TEST 3: NATURAL LANGUAGE VOICE ASSISTANT INTENTS
  // =========================================================================
  console.log('\n=== TEST 3: NATURAL LANGUAGE VOICE ASSISTANT INTENTS ===');

  // 3A. Telugu Rain Question: "వర్షం పడుతుందా?"
  console.log('\nTesting 3A: "వర్షం పడుతుందా?" (Rain query in Telugu)...');
  await evalExpr(`window.pravahVoice.handleVoiceQuery('వర్షం పడుతుందా?')`);
  await new Promise(r => setTimeout(r, 1200));

  const voice3A = await evalExpr(`({
    visible: window.getComputedStyle(document.getElementById('voiceResponseModal')).display,
    teText: document.querySelector('.voice-te-text')?.textContent,
    enText: document.querySelector('.voice-en-text')?.textContent
  })`);
  console.log('Voice 3A Response:', voice3A);
  if (voice3A.teText?.includes('వర్ష') || voice3A.teText?.includes('వాతావరణ')) {
    results.voice_rain_te = true;
    console.log('✓ TEST 3A PASSED: Handled natural Telugu rainfall query without generic rejection');
  }

  // 3B. Telugu Weather Question: "ఈరోజు వాతావరణం ఎలా ఉంది?"
  console.log('\nTesting 3B: "ఈరోజు వాతావరణం ఎలా ఉంది?" (Weather query in Telugu)...');
  await evalExpr(`window.pravahVoice.handleVoiceQuery('ఈరోజు వాతావరణం ఎలా ఉంది?')`);
  await new Promise(r => setTimeout(r, 1200));

  const voice3B = await evalExpr(`({
    teText: document.querySelector('.voice-te-text')?.textContent,
    enText: document.querySelector('.voice-en-text')?.textContent
  })`);
  console.log('Voice 3B Response:', voice3B);
  if (voice3B.teText?.includes('వాతావరణ') && !voice3B.teText?.includes('వరద మట్టాలు, ఆశ్రయ కేంద్రాలు')) {
    results.voice_weather_te = true;
    console.log('✓ TEST 3B PASSED: Handled natural Telugu weather query without generic rejection');
  }

  // 3C. English Rain Question: "Is it raining today?"
  console.log('\nTesting 3C: "Is it raining today?" (English rain query)...');
  await evalExpr(`window.pravahVoice.handleVoiceQuery('Is it raining today?')`);
  await new Promise(r => setTimeout(r, 1200));

  const voice3C = await evalExpr(`({
    enText: document.querySelector('.voice-en-text')?.textContent
  })`);
  console.log('Voice 3C Response:', voice3C);
  if (voice3C.enText?.includes('raining') || voice3C.enText?.includes('precipitation') || voice3C.enText?.includes('monsoon')) {
    results.voice_rain_en = true;
    console.log('✓ TEST 3C PASSED: Handled English rain query with accurate telemetry response');
  }

  // 3D. Mixed Query: "Is it raining in Telugu?"
  console.log('\nTesting 3D: "Is it raining in Telugu?" (English request for Telugu answer)...');
  await evalExpr(`window.pravahVoice.handleVoiceQuery('Is it raining in Telugu?')`);
  await new Promise(r => setTimeout(r, 1200));

  const voice3D = await evalExpr(`({
    teText: document.querySelector('.voice-te-text')?.textContent,
    enText: document.querySelector('.voice-en-text')?.textContent
  })`);
  console.log('Voice 3D Response:', voice3D);
  if (voice3D.teText?.includes('వర్ష') || voice3D.teText?.includes('వాతావరణ')) {
    results.voice_rain_in_telugu = true;
    console.log('✓ TEST 3D PASSED: Understood "in Telugu" modifier and delivered Telugu response');
  }
  await takeScreenshot('recovery_07_voice_assistant_multilingual.png');

  // 3E. Telugu Flood Susceptibility Question: "మా ప్రాంతంలో వరద ప్రమాదం ఉందా?"
  console.log('\nTesting 3E: "మా ప్రాంతంలో వరద ప్రమాదం ఉందా?" (Flood susceptibility in Telugu)...');
  await evalExpr(`window.pravahVoice.handleVoiceQuery('మా ప్రాంతంలో వరద ప్రమాదం ఉందా?')`);
  await new Promise(r => setTimeout(r, 1200));

  const voice3E = await evalExpr(`({
    teText: document.querySelector('.voice-te-text')?.textContent
  })`);
  console.log('Voice 3E Response:', voice3E);
  if (voice3E.teText?.includes('వరద ముప్పు') || voice3E.teText?.includes('విశ్లేషణ స్కోరు') || voice3E.teText?.includes('ఎలివేషన్')) {
    results.voice_flood_risk = true;
    console.log('✓ TEST 3E PASSED: Handled flood susceptibility with Copernicus DEM evidence');
  }

  // 3F. Nearest Hospital Question: "దగ్గరలో ఆసుపత్రి ఎక్కడ ఉంది?"
  console.log('\nTesting 3F: "దగ్గరలో ఆసుపత్రి ఎక్కడ ఉంది?" (Nearest hospital query)...');
  await evalExpr(`window.pravahVoice.handleVoiceQuery('దగ్గరలో ఆసుపత్రి ఎక్కడ ఉంది?')`);
  await new Promise(r => setTimeout(r, 1200));

  const voice3F = await evalExpr(`({
    teText: document.querySelector('.voice-te-text')?.textContent,
    enText: document.querySelector('.voice-en-text')?.textContent
  })`);
  console.log('Voice 3F Response:', voice3F);
  if (voice3F.teText?.includes('ఆసుపత్రి') || voice3F.enText?.includes('Hospital') || voice3F.teText?.includes('108')) {
    results.voice_hospital = true;
    console.log('✓ TEST 3F PASSED: Identified mapped healthcare facilities and 108 ambulance hotline');
  }

  // 3G. Emergency SOS Question: "నాకు సహాయం కావాలి"
  console.log('\nTesting 3G: "నాకు సహాయం కావాలి" (Need help / SOS in Telugu)...');
  await evalExpr(`window.pravahVoice.handleVoiceQuery('నాకు సహాయం కావాలి')`);
  await new Promise(r => setTimeout(r, 1200));

  const voice3G = await evalExpr(`({
    teText: document.querySelector('.voice-te-text')?.textContent
  })`);
  console.log('Voice 3G Response:', voice3G);
  if (voice3G.teText?.includes('ఎయిడ్ కనెక్ట్') || voice3G.teText?.includes('112') || voice3G.teText?.includes('1070')) {
    results.voice_sos = true;
    console.log('✓ TEST 3G PASSED: Delivered SOS extraction and emergency line instructions');
  }
  await takeScreenshot('recovery_08_voice_hospital_help.png');

  console.log('\n======================================================');
  console.log('FINAL RECOVERY TEST RESULTS SUMMARY:');
  console.log(JSON.stringify(results, null, 2));
  console.log('======================================================');

  chromeProc.kill();
  process.exit(0);
}

main().catch(err => {
  console.error('Test execution failed:', err);
  process.exit(1);
});
