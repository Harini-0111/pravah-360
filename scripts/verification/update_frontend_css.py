"""
Append styling for AP Live Monitoring workspace and components to frontend/styles.css
"""
STYLES_PATH = r"C:\major project\frontend\styles.css"

with open(STYLES_PATH, "r", encoding="utf-8") as f:
    css = f.read()

live_css = """
/* ==========================================================================
   LIVE DISASTER MONITORING & AP STATEWIDE GIS WORKSPACE STYLES (PHASE 5.2.1)
   ========================================================================== */

/* Live Monitoring Header Pill */
.live-monitoring-pill {
  display: flex;
  align-items: center;
  gap: 8px;
  background: rgba(13, 148, 136, 0.15);
  border: 1px solid rgba(20, 184, 166, 0.4);
  border-radius: 16px;
  padding: 4px 12px;
  font-size: 11px;
  font-weight: 600;
  color: #2dd4bf;
  letter-spacing: 0.5px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.live-monitoring-pill:hover {
  background: rgba(13, 148, 136, 0.25);
  border-color: #2dd4bf;
}

.pulsing-dot-teal {
  width: 8px;
  height: 8px;
  background-color: #14b8a6;
  border-radius: 50%;
  box-shadow: 0 0 0 0 rgba(20, 184, 166, 0.7);
  animation: pulse-teal 1.8s infinite;
}

@keyframes pulse-teal {
  0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(20, 184, 166, 0.7); }
  70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(20, 184, 166, 0); }
  100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(20, 184, 166, 0); }
}

.nav-pill.live-pill {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.4);
}

/* AP Monitor Layout */
.ap-monitor-layout {
  display: grid;
  grid-template-columns: 420px 1fr;
  width: 100%;
  height: calc(100vh - 60px);
  overflow: hidden;
}

.ap-alerts-sidebar {
  background: var(--bg-surface);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow-y: auto;
  padding: 18px 20px;
  gap: 16px;
}

.ap-alerts-sidebar .sidebar-header h3 {
  font-size: 17px;
  font-weight: 700;
  color: var(--text-main);
  margin-top: 6px;
}

.ap-alerts-sidebar .sidebar-subtext {
  font-size: 11.5px;
  color: var(--text-secondary);
  margin-top: 2px;
}

.header-tag-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.live-pulse-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 10px;
  font-weight: 700;
  color: #2dd4bf;
  text-transform: uppercase;
}

.feed-count-tag {
  background: rgba(56, 189, 248, 0.15);
  color: #38bdf8;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
  font-weight: 600;
}

/* Sources Health Ribbon */
.sources-health-strip {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
  background: var(--bg-card);
  padding: 10px;
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.health-source-chip {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 10.5px;
  color: var(--text-secondary);
}

.health-source-chip.live .chip-status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #10b981;
}

.health-source-chip.notice .chip-status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: #f59e0b;
}

.health-source-chip strong {
  color: var(--text-main);
}

/* Hydrological Gauge Card */
.gauge-monitoring-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 14px;
}

.gauge-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.gauge-card-header h4 {
  font-size: 13px;
  font-weight: 600;
  color: #38bdf8;
  flex: 1;
  margin-left: 8px;
}

.gauge-stations-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.gauge-station-item {
  background: var(--bg-surface);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 8px 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.station-info-left strong {
  font-size: 12px;
  display: block;
  color: var(--text-main);
}

.station-info-left span {
  font-size: 10.5px;
  color: var(--text-secondary);
}

.station-levels-right {
  text-align: right;
}

.station-levels-right .level-value {
  font-size: 13px;
  font-weight: 700;
  font-family: var(--font-mono);
}

.level-tag {
  display: inline-block;
  padding: 2px 6px;
  border-radius: 8px;
  font-size: 9.5px;
  font-weight: 700;
  text-transform: uppercase;
}

.level-tag.normal { background: rgba(16, 185, 129, 0.15); color: #10b981; }
.level-tag.alert_stage { background: rgba(245, 158, 11, 0.2); color: #f59e0b; }
.level-tag.warning_stage { background: rgba(249, 115, 22, 0.2); color: #f97316; }
.level-tag.danger_stage { background: rgba(239, 68, 68, 0.2); color: #ef4444; }

/* Alerts Stream Container */
.alerts-stream-container {
  display: flex;
  flex-direction: column;
  flex: 1;
  gap: 10px;
}

.stream-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 11px;
  color: var(--text-secondary);
}

.severity-filter-chips {
  display: flex;
  gap: 4px;
}

.chip-sev {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 10.5px;
  cursor: pointer;
}

.chip-sev.active {
  background: var(--accent-blue);
  color: #070d18;
  font-weight: 700;
  border-color: var(--accent-blue);
}

.official-alerts-feed {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 400px;
  overflow-y: auto;
}

.alert-item-card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 12px;
  transition: border-color 0.2s ease;
}

.alert-item-card.extreme { border-left: 4px solid #ef4444; }
.alert-item-card.severe { border-left: 4px solid #f59e0b; }
.alert-item-card.moderate { border-left: 4px solid #38bdf8; }

.alert-item-card:hover {
  border-color: #38bdf8;
}

.alert-card-top {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 6px;
}

.alert-card-top h5 {
  font-size: 12.5px;
  font-weight: 600;
  color: var(--text-main);
  flex: 1;
}

.alert-badge {
  padding: 2px 6px;
  border-radius: 8px;
  font-size: 10px;
  font-weight: 700;
}

.alert-badge.extreme { background: rgba(239, 68, 68, 0.2); color: #ef4444; }
.alert-badge.severe { background: rgba(245, 158, 11, 0.2); color: #f59e0b; }
.alert-badge.moderate { background: rgba(56, 189, 248, 0.2); color: #38bdf8; }

.alert-item-desc {
  font-size: 11px;
  color: var(--text-secondary);
  margin-bottom: 6px;
  line-height: 1.4;
}

.alert-item-meta {
  display: flex;
  justify-content: space-between;
  font-size: 10px;
  color: var(--text-muted);
}

/* AP Map Container */
.ap-map-container {
  position: relative;
  width: 100%;
  height: 100%;
}

.ap-map-floating-bar {
  position: absolute;
  top: 16px;
  right: 16px;
  z-index: 1000;
  display: flex;
  gap: 8px;
}

.ap-map-legend {
  position: absolute;
  bottom: 24px;
  left: 20px;
  z-index: 1000;
  background: rgba(12, 20, 36, 0.92);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 10px 14px;
  font-size: 11px;
  box-shadow: 0 4px 16px rgba(0,0,0,0.4);
}

.ap-map-legend .legend-header {
  font-weight: 700;
  color: #38bdf8;
  margin-bottom: 6px;
}

.layer-badge.live-badge {
  background: rgba(245, 158, 11, 0.2);
  color: #f59e0b;
  border: 1px solid rgba(245, 158, 11, 0.4);
}
"""

if '.live-monitoring-pill' not in css:
    with open(STYLES_PATH, "a", encoding="utf-8") as f:
        f.write("\n" + live_css)
    print("styles.css updated with live monitoring styles!")
else:
    print("Live monitoring styles already present.")
