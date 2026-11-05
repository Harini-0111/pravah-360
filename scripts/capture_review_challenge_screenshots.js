const { spawn } = require('child_process');
const http = require('http');
const fs = require('fs');
const path = require('path');

const chromePath = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const userDataDir = 'C:\\major project\\.chrome_challenge_verify_profile';
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
    '--remote-debugging-port=9229',
    `--user-data-dir=${userDataDir}`,
    'about:blank'
  ]);

  let versionData = null;
  for (let i = 0; i < 30; i++) {
    await new Promise(r => setTimeout(r, 200));
    try {
      versionData = await new Promise((resolve, reject) => {
        http.get('http://127.0.0.1:9229/json/version', res => {
          let data = '';
          res.on('data', c => data += c);
          res.on('end', () => resolve(JSON.parse(data)));
        }).on('error', reject);
      });
      if (versionData && versionData.webSocketDebuggerUrl) break;
    } catch (e) {}
  }

  if (!versionData) {
    console.error('Failed to connect to Chrome on port 9229');
    chromeProc.kill();
    process.exit(1);
  }

  const newTarget = await new Promise((resolve, reject) => {
    const req = http.request({
      host: '127.0.0.1',
      port: 9229,
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

  await send('Page.navigate', { url: 'http://127.0.0.1:8000/#welcome' });
  console.log('Navigated to #welcome. Waiting 3s for page load...');
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

  // 1. Verify Welcome Landing & Switch to Telugu
  console.log('\n--- 1. Switching to Telugu Mode ---');
  const teluguSwitchRes = await evalExpr(`(() => {
    if (typeof window.setAppLanguage === 'function') {
      window.setAppLanguage('te');
      return { success: true, lang: document.body.getAttribute('data-lang') };
    }
    return { success: false };
  })()`);
  console.log('Telugu Switch Result:', teluguSwitchRes);
  await new Promise(r => setTimeout(r, 600));

  const teluguTexts = await evalExpr(`({
    tagline: document.querySelector('.hero-tagline')?.textContent?.trim(),
    lead: document.querySelector('.hero-lead')?.textContent?.trim(),
    exploreBtn: document.getElementById('heroExploreBtn')?.textContent?.trim(),
    authBtn: document.getElementById('heroAuthBtn')?.textContent?.trim()
  })`);
  console.log('Telugu Rendered Elements:', teluguTexts);
  await takeScreenshot('page1_telugu_switched.png');

  // 2. Scroll to Community Ground Hazard Reporting Section
  console.log('\n--- 2. Inspecting Community Hazard Section ---');
  await evalExpr(`(() => {
    const sec = document.getElementById('community-hazards');
    if (sec) {
      sec.scrollIntoView({ behavior: 'instant', block: 'start' });
    }
  })()`);
  await new Promise(r => setTimeout(r, 800));

  const hazardCheck = await evalExpr(`({
    sectionExists: !!document.getElementById('community-hazards'),
    formExists: !!document.getElementById('hazardReportForm'),
    mandalSelect: !!document.getElementById('hazardMandal'),
    typeSelect: !!document.getElementById('hazardType'),
    feedCardsCount: document.querySelectorAll('.hazard-card').length
  })`);
  console.log('Hazard Portal Check:', hazardCheck);
  await takeScreenshot('community_hazard_section.png');

  // 3. Trigger Voice Assistant with Telugu flood warning query
  console.log('\n--- 3. Testing Voice Assistant Activation ---');
  await evalExpr(`(() => {
    // Scroll back to top right / comfortable view
    window.scrollTo({ top: 400, behavior: 'instant' });
    if (window.voiceAssistant) {
      window.voiceAssistant.handleVoiceQuery('వరద హెచ్చరికలు ఉన్నాయా?');
    }
  })()`);
  await new Promise(r => setTimeout(r, 1200));

  const voiceModalCheck = await evalExpr(`({
    dialogVisible: !!document.getElementById('voiceAssistantDialog'),
    queryText: document.getElementById('voiceQueryText')?.textContent,
    responseText: document.getElementById('voiceResponseContent')?.textContent
  })`);
  console.log('Voice Assistant Modal Check:', voiceModalCheck);
  await takeScreenshot('voice_assistant_active.png');

  console.log('\nAll verification screenshots captured successfully!');
  chromeProc.kill();
  process.exit(0);
}

main().catch(err => {
  console.error('Error during execution:', err);
  process.exit(1);
});
