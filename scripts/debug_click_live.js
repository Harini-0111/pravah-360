const { spawn } = require('child_process');
const http = require('http');
const fs = require('fs');

const chromePath = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const userDataDir = 'C:\\major project\\.chrome_debug_click';

async function main() {
  if (fs.existsSync(userDataDir)) {
    try { fs.rmSync(userDataDir, { recursive: true, force: true }); } catch (e) {}
  }

  const chromeProc = spawn(chromePath, [
    '--headless=new',
    '--disable-gpu',
    '--remote-debugging-port=9238',
    `--user-data-dir=${userDataDir}`,
    'about:blank'
  ]);

  let versionData = null;
  for (let i = 0; i < 30; i++) {
    await new Promise(r => setTimeout(r, 200));
    try {
      versionData = await new Promise((resolve, reject) => {
        http.get('http://127.0.0.1:9238/json/version', res => {
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
      port: 9238,
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
    if (msg.method === 'Runtime.exceptionThrown') {
      consoleLogs.push({ type: 'EXCEPTION', text: msg.params.exceptionDetails.text + ' ' + (msg.params.exceptionDetails.exception?.description || '') });
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

  console.log('Console logs on load:', consoleLogs);

  // Check state before click
  const stateBefore = await send('Runtime.evaluate', {
    expression: `({
      hasToggleGlobalLanguage: typeof window.toggleGlobalLanguage,
      hasSetAppLanguage: typeof window.setAppLanguage,
      hasTranslations: !!window.PRAVAH_TRANSLATIONS,
      teTranslationsCount: window.PRAVAH_TRANSLATIONS ? Object.keys(window.PRAVAH_TRANSLATIONS.te || {}).length : 0,
      currentAppLang: window.currentAppLang,
      bodyDataLang: document.body.getAttribute('data-lang'),
      btnText: document.getElementById('btnLandingLangToggle')?.textContent,
      btnOnclick: document.getElementById('btnLandingLangToggle')?.getAttribute('onclick')
    })`,
    returnByValue: true
  });
  console.log('State BEFORE click:', stateBefore.result.value);

  // Simulate click on toggle
  console.log('\n--- Clicking #btnLandingLangToggle ---');
  const clickResult = await send('Runtime.evaluate', {
    expression: `(() => {
      const btn = document.getElementById('btnLandingLangToggle');
      if (!btn) return 'BUTTON_NOT_FOUND';
      btn.click();
      return 'CLICKED';
    })()`,
    returnByValue: true
  });
  console.log('Click dispatch result:', clickResult.result.value);
  await new Promise(r => setTimeout(r, 500));

  // Check state after click
  const stateAfter = await send('Runtime.evaluate', {
    expression: `({
      currentAppLang: window.currentAppLang,
      bodyDataLang: document.body.getAttribute('data-lang'),
      tagline: document.querySelector('.hero-tagline')?.textContent?.trim(),
      headline: document.querySelector('.hero-headline')?.textContent?.trim(),
      btnText: document.getElementById('btnLandingLangToggle')?.textContent,
      navOverview: document.querySelector('.landing-nav-links a')?.textContent?.trim()
    })`,
    returnByValue: true
  });
  console.log('State AFTER click:', stateAfter.result.value);
  console.log('Console logs after click:', consoleLogs);

  chromeProc.kill();
  process.exit(0);
}

main().catch(e => { console.error(e); process.exit(1); });
