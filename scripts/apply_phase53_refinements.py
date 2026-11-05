import re
import sys

def main():
    # 1. Update frontend/index.html
    with open('frontend/index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    # Add topo basemap radio if missing
    topo_snippet = """                  <label class="basemap-radio-label">
                    <input type="radio" name="basemapRadio" value="osm">
                    <span>OpenStreetMap</span>
                  </label>
                  <label class="basemap-radio-label">
                    <input type="radio" name="basemapRadio" value="topo">
                    <span>Topographic (Esri)</span>
                  </label>"""
    if 'value="topo"' not in html:
        html = re.sub(
            r'<label class="basemap-radio-label">\s*<input type="radio" name="basemapRadio" value="osm">\s*<span>OpenStreetMap</span>\s*</label>',
            topo_snippet,
            html
        )

    # Susceptibility opacity default to 55
    html = html.replace('id="rngSusceptibilityOpacity" min="10" max="90" value="45"', 'id="rngSusceptibilityOpacity" min="10" max="90" value="55"')

    # Fit Basin Extent button
    if 'id="btnFitBasinExtent"' not in html:
        html = html.replace(
            '<div id="explorer-map" class="gis-map"></div>',
            """<div id="explorer-map" class="gis-map"></div>

              <!-- Floating Map Tools -->
              <div class="gis-floating-toolbar">
                <button class="btn-gis-tool" id="btnFitBasinExtent" title="Fit Lower Godavari Basin Extent">🎯 Fit Basin</button>
              </div>"""
        )

    # Symbology Legend colors
    old_legend_pattern = r'<div class="legend-content" id="gisLegendContent">.*?</div>\s*</div>'
    new_legend = """<div class="legend-content" id="gisLegendContent">
                  <div class="legend-subheading">AHP Susceptibility</div>
                  <div class="legend-row"><span class="swatch" style="background:#ef4444;"></span> Very High (&ge; 0.72)</div>
                  <div class="legend-row"><span class="swatch" style="background:#f97316;"></span> High (0.58 – 0.72)</div>
                  <div class="legend-row"><span class="swatch" style="background:#eab308;"></span> Moderate (0.44 – 0.58)</div>
                  <div class="legend-row"><span class="swatch" style="background:#10b981;"></span> Low (&lt; 0.44)</div>
                  <div class="legend-subheading" style="margin-top:6px;">Sentinel-1 SAR (16 July 2022)</div>
                  <div class="legend-row"><span class="swatch" style="background:#00f0ff;"></span> Potential Flood Inundation</div>
                  <div class="legend-row"><span class="swatch" style="background:#2563eb;"></span> Permanent Water Reference</div>
                  <div class="legend-row"><span class="swatch" style="background:#a855f7;"></span> Saturated Wet Soil / Paddy</div>
                  <div class="legend-subheading" style="margin-top:6px;">Hydrology &amp; Admin</div>
                  <div class="legend-row"><span class="swatch" style="background:#00b4d8;"></span> River Network Reaches</div>
                  <div class="legend-row"><span class="swatch" style="background:#38bdf8;"></span> Mandal Boundaries</div>
                </div>
              </div>"""
    html = re.sub(old_legend_pattern, new_legend, html, flags=re.DOTALL)

    # 3D Globe Action buttons & quick flight pills
    if 'id="btnToggleGlobeTexture"' not in html:
        old_globe_actions = """              <div class="globe-action-buttons">
                <button class="btn-globe" id="btnToggleGlobeRotation" title="Toggle Auto-Rotation">
                  ⏸ Pause Rotation
                </button>
                <button class="btn-globe" id="btnResetGlobeView" title="Reset Global View">
                  🌍 Global Reset
                </button>
              </div>"""
        new_globe_actions = """              <div class="globe-action-buttons">
                <button class="btn-globe" id="btnToggleGlobeRotation" title="Toggle Auto-Rotation">
                  ⏸ Pause Rotation
                </button>
                <button class="btn-globe" id="btnResetGlobeView" title="Reset Global View">
                  🌍 Global Reset
                </button>
                <button class="btn-globe" id="btnToggleGlobeTexture" title="Switch Day/Night High-Res Texture">
                  ☀️ Day Texture
                </button>
              </div>
              <div class="globe-quick-pills" style="display:flex; gap:6px; margin-top:8px;">
                <span style="font-size:11px; color:#94a3b8; align-self:center;">Jump:</span>
                <button class="btn-globe-pill" data-country="India">🇮🇳 India</button>
                <button class="btn-globe-pill" data-country="United States of America">🇺🇸 USA</button>
                <button class="btn-globe-pill" data-country="Japan">🇯🇵 Japan</button>
                <button class="btn-globe-pill" data-country="Brazil">🇧🇷 Brazil</button>
              </div>"""
        html = html.replace(old_globe_actions, new_globe_actions)

    with open('frontend/index.html', 'w', encoding='utf-8') as f:
        f.write(html)
    print("Updated frontend/index.html")

    # 2. Update frontend/app.js
    with open('frontend/app.js', 'r', encoding='utf-8') as f:
        app_js = f.read()

    # loadMandalsLayer: ensure fallback and opacity 0.55 default
    app_js = app_js.replace(
        "const cat = record ? record.susceptibility_category : 'Moderate';",
        "const cat = record ? (record.risk_level || record.susceptibility_category) : 'Moderate';"
    )
    app_js = app_js.replace(
        "const opacityVal = parseInt(document.getElementById('rngSusceptibilityOpacity')?.value || 45) / 100;",
        "const opacityVal = parseInt(document.getElementById('rngSusceptibilityOpacity')?.value || 55) / 100;"
    )

    with open('frontend/app.js', 'w', encoding='utf-8') as f:
        f.write(app_js)
    print("Updated frontend/app.js")

    # 3. Update frontend/styles.css
    with open('frontend/styles.css', 'r', encoding='utf-8') as f:
        css = f.read()

    if '.gis-floating-toolbar' not in css:
        floating_toolbar_css = """
/* Floating GIS Map Tools */
.gis-floating-toolbar {
  position: absolute;
  top: 14px;
  right: 14px;
  z-index: 999;
  display: flex;
  gap: 8px;
}

.btn-gis-tool {
  background: rgba(15, 23, 42, 0.88);
  backdrop-filter: blur(8px);
  border: 1px solid rgba(56, 189, 248, 0.35);
  color: #e2e8f0;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.45);
  transition: all 0.2s ease;
  display: inline-flex;
  align-items: center;
  gap: 6px;
}

.btn-gis-tool:hover {
  background: rgba(0, 240, 255, 0.18);
  border-color: #00f0ff;
  color: #00f0ff;
  box-shadow: 0 0 10px rgba(0, 240, 255, 0.3);
  transform: translateY(-1px);
}
"""
        css += floating_toolbar_css
        with open('frontend/styles.css', 'w', encoding='utf-8') as f:
            f.write(css)
        print("Updated frontend/styles.css")

if __name__ == '__main__':
    main()
