const fs = require('fs');
const HTML_PATH = 'C:/major project/frontend/index.html';
let content = fs.readFileSync(HTML_PATH, 'utf8');

// 1. Add rescue_boat_evacuation.jpg to operations workspace header
const OPS_HEADER_TARGET = '<div class="ops-header-bar">';
const OPS_PHOTO_INSERT = `<div class="workspace-photo-banner" style="position:relative;height:180px;overflow:hidden;border-radius:12px;margin-bottom:16px;">
            <img src="/static/assets/images/emergency-response/rescue_boat_evacuation.jpg" alt="Rescue team evacuating residents from flooded neighbourhood" style="width:100%;height:100%;object-fit:cover;object-position:center 40%;">
            <div style="position:absolute;inset:0;background:linear-gradient(90deg,rgba(10,20,40,0.75) 0%,rgba(10,20,40,0.3) 60%,transparent 100%);display:flex;align-items:center;padding:24px;">
              <div style="color:#fff;">
                <div style="font-size:11px;font-weight:700;letter-spacing:0.1em;color:rgba(255,255,255,0.65);margin-bottom:4px;text-transform:uppercase;">Emergency Response</div>
                <div style="font-size:18px;font-weight:800;">Coordinated Rescue &amp; Resource Dispatch</div>
              </div>
            </div>
          </div>
          <div class="ops-header-bar">`;

if (content.includes(OPS_HEADER_TARGET)) {
  // Only replace first occurrence inside workspace-operations
  const wsIdx = content.indexOf('workspace-operations');
  const opsInWs = content.indexOf(OPS_HEADER_TARGET, wsIdx);
  if (opsInWs !== -1) {
    content = content.slice(0, opsInWs) + OPS_PHOTO_INSERT + content.slice(opsInWs + OPS_HEADER_TARGET.length);
    console.log('✓ Rescue boat photo added to operations workspace');
  }
} else {
  console.log('⚠ ops-header-bar not found');
}

// 2. Add ocean waves photo to global earth workspace
const GLOBE_CANVAS_TARGET = '<div id="globe-container" class="globe-canvas"></div>';
const GLOBE_PHOTO_INSERT = `<div class="workspace-photo-banner" style="position:absolute;top:0;left:0;right:0;height:140px;overflow:hidden;pointer-events:none;z-index:0;opacity:0.22;">
              <img src="/static/assets/images/awareness/bay_aerial_ocean_waves.jpg" alt="" aria-hidden="true" style="width:100%;height:100%;object-fit:cover;object-position:center 30%;">
            </div>
            <div id="globe-container" class="globe-canvas"></div>`;
if (content.includes(GLOBE_CANVAS_TARGET)) {
  content = content.replace(GLOBE_CANVAS_TARGET, GLOBE_PHOTO_INSERT);
  console.log('✓ Ocean waves atmospheric overlay added to global earth workspace');
} else {
  console.log('⚠ globe-container not found');
}

// 3. Add monsoon shelter B&W photo to help/preparedness workspace
const HELP_HEADER_TARGET = '<div class="help-header-card"';
const HELP_PHOTO_INSERT = `<div class="workspace-photo-banner" style="position:relative;height:160px;overflow:hidden;border-radius:12px;margin-bottom:16px;">
            <img src="/static/assets/images/communities/monsoon_shelter_community.jpg" alt="Displaced families sheltering under makeshift cover during monsoon rains" style="width:100%;height:100%;object-fit:cover;object-position:center 30%;filter:grayscale(0.3) contrast(1.1);">
            <div style="position:absolute;inset:0;background:linear-gradient(90deg,rgba(20,40,30,0.80) 0%,rgba(20,40,30,0.3) 70%,transparent 100%);display:flex;align-items:center;padding:24px;">
              <div style="color:#fff;max-width:400px;">
                <div style="font-size:11px;font-weight:700;letter-spacing:0.1em;color:rgba(255,255,255,0.6);margin-bottom:4px;text-transform:uppercase;">Safety &amp; Preparedness</div>
                <div style="font-size:16px;font-weight:800;line-height:1.35;">When disasters strike, knowledge and preparation protect lives.</div>
              </div>
            </div>
          </div>
          <div class="help-header-card"`;

const helpWsIdx = content.indexOf('workspace-help');
if (helpWsIdx !== -1) {
  const helpHeaderIdx = content.indexOf(HELP_HEADER_TARGET, helpWsIdx);
  if (helpHeaderIdx !== -1) {
    content = content.slice(0, helpHeaderIdx) + HELP_PHOTO_INSERT + content.slice(helpHeaderIdx + '<div class="help-header-card"'.length);
    console.log('✓ Monsoon shelter photo added to help workspace');
  } else {
    console.log('⚠ help-header-card not found inside workspace-help');
  }
} else {
  console.log('⚠ workspace-help not found');
}

fs.writeFileSync(HTML_PATH, content, 'utf8');
console.log('\nNew photo integrations complete.');
