const { spawn } = require('child_process');
const http = require('http');
const fs = require('fs');
const path = require('path');

const chromePath = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const userDataDir = 'C:\\major project\\.chrome_verify_live';

async function main() {
  if (fs.existsSync(userDataDir)) {
    try { fs.rmSync(userDataDir, { recursive: true, force: true }); } catch (e) {}
  }

  const chromeProc = spawn(chromePath, [
    '--headless=new',
    '--disable-gpu',
    '--remote-debugging-port=9244',
    `--user-data-dir=${userDataDir}`,
    'about:blank'
  ]);

  let versionData = null;
  for (let i = 0; i < 30; i++) {
    await new Promise(r => setTimeout(r, 200));
    try {
      versionData = await new Promise((resolve, reject) => {
        http.get('http://127.0.0.1:9244/json/version', res => {
          let data = '';
          res.on('data', c => data += c);
          res.on('end', () => resolve(JSON.parse(data)));
        }).on('error', reject);
      });
      if (versionData && versionData.webSocketDebuggerUrl) break;
    } catch (e) {}
  }

  const newTarget = await new Promise((resolve, reject) => {
    const req = http.request({
      host: '127.0.0.1',
      port: 9244,
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

  const consoleLogs = [];
  ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    if (msg.method === 'Runtime.consoleAPICalled') {
      consoleLogs.push({ type: msg.params.type, text: msg.params.args.map(a => a.value || a.description).join(' ') });
    }
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

  await send('Page.navigate', { url: 'http://127.0.0.1:8000/#welcome' });
  await new Promise(r => setTimeout(r, 2000));

  console.log('--- TEST 1: Initial Welcome Page (English Default) ---');
  let state = (await send('Runtime.evaluate', {
    expression: `({
      currentLang: window.currentAppLang,
      btnText: document.getElementById('btnLandingLangToggle')?.textContent?.trim(),
      heroHeadline: document.querySelector('.hero-headline')?.textContent?.trim(),
      heroTagline: document.querySelector('.hero-tagline')?.textContent?.trim(),
      navOverview: document.querySelectorAll('.landing-nav-links a')[0]?.textContent?.trim()
    })`,
    returnByValue: true
  })).result.value;
  console.log('State before click:', state);

  // Take screenshot 1: Welcome in English
  let shot1 = await send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync('docs/screenshots/test_welcome_english.png', Buffer.from(shot1.data, 'base64'));

  console.log('--- TEST 2: Clicking Telugu Toggle Button ONCE ---');
  await send('Runtime.evaluate', {
    expression: `document.getElementById('btnLandingLangToggle').click();`
  });
  await new Promise(r => setTimeout(r, 600));

  let stateTe = (await send('Runtime.evaluate', {
    expression: `({
      currentLang: window.currentAppLang,
      btnText: document.getElementById('btnLandingLangToggle')?.textContent?.trim(),
      heroHeadline: document.querySelector('.hero-headline')?.textContent?.trim(),
      heroTagline: document.querySelector('.hero-tagline')?.textContent?.trim(),
      navOverview: document.querySelectorAll('.landing-nav-links a')[0]?.textContent?.trim()
    })`,
    returnByValue: true
  })).result.value;
  console.log('State after clicking Telugu toggle:', stateTe);

  // Take screenshot 2: Welcome in Telugu
  let shot2 = await send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync('docs/screenshots/test_welcome_telugu.png', Buffer.from(shot2.data, 'base64'));

  console.log('--- TEST 3: Clicking Toggle Button AGAIN (Back to English) ---');
  await send('Runtime.evaluate', {
    expression: `document.getElementById('btnLandingLangToggle').click();`
  });
  await new Promise(r => setTimeout(r, 600));

  let stateEnAgain = (await send('Runtime.evaluate', {
    expression: `({
      currentLang: window.currentAppLang,
      btnText: document.getElementById('btnLandingLangToggle')?.textContent?.trim(),
      heroHeadline: document.querySelector('.hero-headline')?.textContent?.trim(),
      heroTagline: document.querySelector('.hero-tagline')?.textContent?.trim(),
      navOverview: document.querySelectorAll('.landing-nav-links a')[0]?.textContent?.trim()
    })`,
    returnByValue: true
  })).result.value;
  console.log('State after clicking back to English:', stateEnAgain);

  console.log('--- TEST 4: Navigating to Dedicated Split-Screen Login ---');
  await send('Runtime.evaluate', { expression: `window.navigateTo('login');` });
  await new Promise(r => setTimeout(r, 600));

  let stateLogin = (await send('Runtime.evaluate', {
    expression: `({
      pageLoginDisplay: document.getElementById('page-login')?.style?.display,
      hasLeftPanel: !!document.querySelector('#page-login .auth-left-panel'),
      hasRightPanel: !!document.querySelector('#page-login .auth-right-panel'),
      hasTopNav: !!document.querySelector('#page-login .auth-top-nav-bar'),
      loginTitle: document.querySelector('#page-login .auth-form-header h2')?.textContent?.trim(),
      demoPillsCount: document.querySelectorAll('.auth-eval-pill').length
    })`,
    returnByValue: true
  })).result.value;
  console.log('Login page state:', stateLogin);

  let shot3 = await send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync('docs/screenshots/test_split_login.png', Buffer.from(shot3.data, 'base64'));

  console.log('--- TEST 5: Navigating to Dedicated Registration Page ---');
  await send('Runtime.evaluate', { expression: `window.navigateTo('register');` });
  await new Promise(r => setTimeout(r, 600));

  let stateRegister = (await send('Runtime.evaluate', {
    expression: `({
      pageRegDisplay: document.getElementById('page-register')?.style?.display,
      hasLeftPanel: !!document.querySelector('#page-register .auth-left-panel'),
      hasPwdStrength: !!document.getElementById('regPwdStrengthBar'),
      regTitle: document.querySelector('#page-register .auth-form-header h2')?.textContent?.trim(),
      districtsCount: document.querySelectorAll('#regDistrict option').length
    })`,
    returnByValue: true
  })).result.value;
  console.log('Register page state:', stateRegister);

  let shot4 = await send('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync('docs/screenshots/test_split_register.png', Buffer.from(shot4.data, 'base64'));

  console.log('All tests completed successfully!');
  try { ws.close(); } catch (e) {}
  try { chromeProc.kill(); } catch (e) {}
  process.exit(0);
}

main().catch(err => {
  console.error('Fatal test error:', err);
  process.exit(1);
});
