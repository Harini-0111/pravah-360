const fs = require('fs');

const path = 'frontend/entry_journey.css';
let css = fs.readFileSync(path, 'utf8');

const target = `/* Voice Response Modal Card */
.voice-response-card {
  position: fixed;
  bottom: 96px;
  right: 24px;
  width: 380px;
  max-width: 90vw;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 20px 40px rgba(12, 36, 32, 0.25);
  border: 1.5px solid var(--color-forest);
  padding: 20px 22px;
  z-index: 1001;
  animation: authFadeSlideUp 0.3s ease;
}`;

const replacement = `/* Voice Response Modal Card */
.voice-response-card {
  position: fixed;
  bottom: 96px;
  right: 24px;
  width: 420px;
  max-width: 92vw;
  background: rgba(15, 23, 42, 0.96);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border-radius: 16px;
  box-shadow: 0 20px 45px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(215, 169, 77, 0.35);
  padding: 20px 22px;
  z-index: 1001;
  color: #f8fafc;
  animation: authFadeSlideUp 0.3s ease;
}

.voice-chip {
  background: rgba(255, 255, 255, 0.08);
  color: #e2e8f0;
  border: 1px solid rgba(255, 255, 255, 0.15);
  border-radius: 14px;
  padding: 4px 10px;
  font-size: 11.5px;
  font-family: 'Noto Sans Telugu', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.voice-chip:hover {
  background: #153D37;
  color: #ffffff;
  border-color: #D7A94D;
  transform: translateY(-1px);
}`;

if (css.includes(target)) {
  css = css.replace(target, replacement);
  fs.writeFileSync(path, css, 'utf8');
  console.log('SUCCESS: Voice modal styles updated in entry_journey.css');
} else {
  console.log('Target not found in entry_journey.css');
}
