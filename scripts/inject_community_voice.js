const fs = require('fs');
const htmlPath = 'C:/major project/frontend/index.html';
let html = fs.readFileSync(htmlPath, 'utf8');

// 1. Add Telugu font & voice styles in head
const fontHook = '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">';
const teluguFont = `<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&family=Noto+Sans+Telugu:wght@400;500;600;700&display=swap" rel="stylesheet">`;
if (html.includes(fontHook)) {
  html = html.replace(fontHook, teluguFont);
  console.log("✓ Added Noto Sans Telugu web font");
}

// 2. Add community hazard reporting section into page-welcome right before quick helplines
const helplinesAnchor = '<!-- Quick Helplines Strip -->';
const communityHazardSection = `
    <!-- Section: Community Ground Hazard Reporting (Citizen Verification) -->
    <section class="landing-hazard-section" id="community-hazard-reporting">
      <div class="section-editorial-header">
        <h2 data-i18n="hazardReportTitle">Report Local Flood Hazard or Road Block</h2>
        <p data-i18n="hazardReportDesc">Empowering rural citizens: upload photos of rising water, submerged culverts, or damaged embankments directly to Mandal disaster officers.</p>
      </div>

      <div class="hazard-reporting-container">
        <div class="hazard-form-card">
          <form id="communityHazardReportForm" onsubmit="handleHazardReportSubmit(event)">
            <div class="hazard-form-grid">
              <div class="auth-field-group">
                <label class="auth-label" for="hazardMandal">Mandal Location</label>
                <div class="auth-input-wrap auth-select-wrap">
                  <select id="hazardMandal" class="auth-input auth-select" required>
                    <option value="Rajamahendravaram Urban" selected>Rajamahendravaram Urban</option>
                    <option value="Rajamahendravaram Rural">Rajamahendravaram Rural</option>
                    <option value="Kovvur">Kovvur</option>
                    <option value="Kadiam">Kadiam</option>
                    <option value="Nidadavole">Nidadavole</option>
                    <option value="Razole">Razole</option>
                    <option value="Amalapuram">Amalapuram</option>
                    <option value="Mummidivaram">Mummidivaram</option>
                    <option value="Seethanagaram">Seethanagaram</option>
                    <option value="Gokavaram">Gokavaram</option>
                  </select>
                </div>
              </div>

              <div class="auth-field-group">
                <label class="auth-label" for="hazardCategory">Hazard Type</label>
                <div class="auth-input-wrap auth-select-wrap">
                  <select id="hazardCategory" class="auth-input auth-select" required>
                    <option value="RISING_WATER" selected>🌊 Rapidly Rising River Level</option>
                    <option value="ROAD_FLOODING">🚗 Submerged Roadway / Culvert</option>
                    <option value="EMBANKMENT_BREACH">⚠️ Canal / Bund Seepage or Breach</option>
                    <option value="DAMAGED_INFRASTRUCTURE">🏚️ Damaged Bridge or Electric Pole</option>
                    <option value="BLOCKED_ACCESS">🚫 Blocked Evacuation Path</option>
                  </select>
                </div>
              </div>

              <div class="auth-field-group auth-col-full">
                <label class="auth-label" for="hazardDescription">Observer Description</label>
                <div class="auth-input-wrap">
                  <textarea id="hazardDescription" class="auth-input" rows="2" style="padding-left:14px; resize:vertical;" placeholder="Describe water depth, landmarks (e.g. Near Razole bridge, 2 feet water overtopping)..." required></textarea>
                </div>
              </div>

              <div class="auth-field-group">
                <label class="auth-label" for="hazardPhotoFile">Attach Photo (Optional)</label>
                <div class="auth-input-wrap">
                  <input type="file" id="hazardPhotoFile" class="auth-input" accept="image/*" style="padding:8px 12px; font-size:12px;">
                </div>
              </div>

              <div class="auth-field-group">
                <label class="auth-label" for="hazardReporterName">Citizen Name (Redacted for Privacy)</label>
                <div class="auth-input-wrap">
                  <input type="text" id="hazardReporterName" class="auth-input" placeholder="e.g. Ramesh Varma" value="Local Resident">
                </div>
              </div>
            </div>

            <div style="display:flex; justify-content:space-between; align-items:center; margin-top:14px;">
              <button type="submit" class="auth-submit-btn" id="btnSubmitHazardReport" style="width:auto; padding:12px 28px;">
                <span class="auth-btn-text" data-i18n="btnSubmitHazard">Submit Hazard Report &rarr;</span>
                <span class="auth-btn-spinner" aria-hidden="true"></span>
              </button>
              <div id="hazardSubmitFeedback" style="display:none; font-size:13px; font-weight:600;"></div>
            </div>
          </form>
        </div>

        <!-- Recent Verified Community Hazard Observations -->
        <div class="hazard-feed-card">
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
            <h4 style="margin:0; font-size:15px; font-weight:800; color:var(--color-forest);">Ground Observations Feed</h4>
            <span class="badge-pill alert" style="background:#e0f2fe; color:#0369a1; font-size:11px; font-weight:700;">Status: Submitted &rarr; Verified</span>
          </div>
          <div id="communityHazardsList" style="display:flex; flex-direction:column; gap:8px; max-height:280px; overflow-y:auto;">
            <div style="padding:10px 12px; background:var(--color-mist); border-radius:8px; font-size:12.5px;">
              <div style="display:flex; justify-content:space-between; font-weight:700; color:var(--color-forest);">
                <span>🌊 High Water Near Embankment</span>
                <span style="color:#059669;">● Verified</span>
              </div>
              <div style="color:var(--text-muted-dark); font-size:11.5px; margin-top:2px;">Kovvur • Water reached yellow warning marker on western bund.</div>
              <div style="font-size:10.5px; color:#64748b; margin-top:4px;">Reported by: R*** V*** • 25 mins ago</div>
            </div>
            <div style="padding:10px 12px; background:var(--color-mist); border-radius:8px; font-size:12.5px;">
              <div style="display:flex; justify-content:space-between; font-weight:700; color:var(--color-forest);">
                <span>🚗 Road Inundation (1.5 ft)</span>
                <span style="color:#d97706;">● Under Review</span>
              </div>
              <div style="color:var(--text-muted-dark); font-size:11.5px; margin-top:2px;">Razole • Rural bypass road overtopped by agricultural drain.</div>
              <div style="font-size:10.5px; color:#64748b; margin-top:4px;">Reported by: K*** S*** • 1 hour ago</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Floating Telugu Voice Assistant Trigger Button -->
    <div class="floating-voice-widget" id="floatingVoiceWidget">
      <button type="button" class="btn-floating-voice" id="btnVoiceAssistant" onclick="window.pravahVoice && window.pravahVoice.toggleListen()" title="Speak in Telugu or English (వాయిస్ ద్వారా అడగండి)">
        <span class="voice-icon">🎤</span>
        <span class="voice-pulse-ring"></span>
      </button>
      <div class="voice-status-banner" id="voiceAssistantStatusBanner" style="display:none;"></div>
    </div>
`;

if (!html.includes('id="community-hazard-reporting"')) {
  html = html.replace(helplinesAnchor, communityHazardSection + '\n    ' + helplinesAnchor);
  console.log("✓ Added Community Hazard Reporting & Voice Assistant Widget to Page 1");
}

// 3. Add script tags before </body> for translations and voice assistant
const bodyEnd = '</body>';
const scriptsToAdd = `
  <!-- Multilingual Telugu Engine & Voice Assistance -->
  <script src="/static/translations.js"></script>
  <script src="/static/voice_assistant.js"></script>
</body>`;
if (!html.includes('translations.js')) {
  html = html.replace(bodyEnd, scriptsToAdd);
  console.log("✓ Injected translations.js and voice_assistant.js script tags");
}

fs.writeFileSync(htmlPath, html, 'utf8');
console.log("HTML successfully updated with Community & Voice features.");
