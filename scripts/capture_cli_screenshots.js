const { execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');
const os = require('os');

const chromePath = 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const screenshotsDir = path.resolve(__dirname, '..', 'docs', 'screenshots');
if (!fs.existsSync(screenshotsDir)) fs.mkdirSync(screenshotsDir, { recursive: true });

const targets = [
  {
    name: 'page1_telugu_switched.png',
    url: 'http://127.0.0.1:8000/?action=telugu#welcome'
  },
  {
    name: 'community_hazard_section.png',
    url: 'http://127.0.0.1:8000/?action=hazards#welcome'
  },
  {
    name: 'voice_assistant_active.png',
    url: 'http://127.0.0.1:8000/?action=voice#welcome'
  }
];

targets.forEach(t => {
  const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), 'chrome_ss_'));
  const outFile = path.join(screenshotsDir, t.name);
  console.log(`Capturing ${t.name} from ${t.url}...`);
  try {
    execFileSync(chromePath, [
      '--headless=new',
      `--user-data-dir=${tmpDir}`,
      '--disable-gpu',
      '--no-sandbox',
      '--run-all-compositor-stages-before-draw',
      '--hide-scrollbars',
      '--window-size=1440,900',
      '--virtual-time-budget=6000',
      `--screenshot=${outFile}`,
      t.url
    ], { timeout: 20000 });
    
    if (fs.existsSync(outFile)) {
      const stats = fs.statSync(outFile);
      console.log(`✓ Created ${t.name} (${stats.size} bytes)`);
    } else {
      console.error(`✗ File not created: ${t.name}`);
    }
  } catch (err) {
    console.error(`Error capturing ${t.name}:`, err.message);
  } finally {
    try { fs.rmSync(tmpDir, { recursive: true, force: true }); } catch (e) {}
  }
});
