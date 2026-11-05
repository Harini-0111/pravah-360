"""
Update frontend/app.js to integrate live monitoring, AP map, SACHET layer, resident help requests, and notifications.
"""
APP_JS_PATH = r"C:\major project\frontend\app.js"

with open(APP_JS_PATH, "r", encoding="utf-8") as f:
    js = f.read()

# 1. Update WORKSPACE_METADATA to include 'ap-monitor'
if "'ap-monitor':" not in js and '"ap-monitor":' not in js:
    meta_target = "operations: {\n      heading: 'Emergency Operations & Decision Support Simulator',\n      subheading: 'Multi-Role Tactical Coordination: Resident • Mandal • District • ERT Dispatch'\n    }"
    meta_repl = """operations: {
      heading: 'Emergency Operations & Decision Support Simulator',
      subheading: 'Multi-Role Tactical Coordination: Resident • Mandal • District • ERT Dispatch'
    },
    'ap-monitor': {
      heading: 'Andhra Pradesh Live Disaster Monitoring',
      subheading: 'NDMA SACHET • APSDMA Weather-Watch • IMD Cyclone & Rainfall • CWC Hydrological Stages'
    }"""
    if meta_target in js:
        js = js.replace(meta_target, meta_repl)
        print("Updated WORKSPACE_METADATA with ap-monitor.")
    else:
        # Fallback search
        js = js.replace("operations: {", "'ap-monitor': {\n      heading: 'Andhra Pradesh Live Disaster Monitoring',\n      subheading: 'NDMA SACHET • APSDMA Weather-Watch • IMD Cyclone & Rainfall • CWC Hydrological Stages'\n    },\n    operations: {")
        print("Fallback updated WORKSPACE_METADATA.")

# 2. Add maps.apMonitor
if "apMonitor: null" not in js:
    js = js.replace("maps = {\n    explorer: null,", "maps = {\n    explorer: null,\n    apMonitor: null,")
    print("Added apMonitor to maps cache.")

# 3. In switchWorkspace, handle ap-monitor map resize/init
if "workspaceId === 'ap-monitor'" not in js:
    switch_target = "if (workspaceId === 'explorer' && maps.explorer) {"
    switch_repl = """if (workspaceId === 'ap-monitor') {
      if (!maps.apMonitor) {
        setTimeout(initApMonitoringMap, 100);
      } else {
        setTimeout(() => maps.apMonitor.invalidateSize(), 200);
      }
    }
    if (workspaceId === 'explorer' && maps.explorer) {"""
    js = js.replace(switch_target, switch_repl)
    print("Added ap-monitor switch handling.")

# 4. In initExplorerLayers, add SACHET alerts layer
if "explorerLayers.sachetAlerts" not in js:
    sachet_code = """
    // 6. Real-Time NDMA SACHET Live Alerted Mandals Layer
    fetch('/api/v1/monitoring/ap-alerted-mandals-geojson')
      .then(res => res.json())
      .then(geojson => {
        explorerLayers.sachetAlerts = L.geoJSON(geojson, {
          style: (feature) => {
            const sev = feature.properties?.severity;
            const col = sev === 'Extreme' ? '#ef4444' : (sev === 'Severe' ? '#f59e0b' : '#38bdf8');
            return {
              color: col,
              weight: 2,
              fillColor: col,
              fillOpacity: 0.30
            };
          },
          onEachFeature: (feature, layer) => {
            const p = feature.properties || {};
            layer.bindPopup(`
              <div class="gis-popup">
                <h4>⚠️ ${p.events || 'Official Alert'} (${p.severity})</h4>
                <p><strong>Mandal:</strong> ${p.mandal} | <strong>District:</strong> ${p.district}</p>
                <p><strong>Source:</strong> ${p.senders || 'NDMA SACHET / APSDMA'}</p>
                <p><strong>Sent:</strong> ${p.last_sent || 'Recent'}</p>
              </div>
            `);
          }
        }).addTo(map);

        const chkSachet = document.getElementById('chkLyrLiveSachet');
        if (chkSachet) {
          chkSachet.addEventListener('change', (e) => {
            if (explorerLayers.sachetAlerts) {
              if (e.target.checked) explorerLayers.sachetAlerts.addTo(map);
              else map.removeLayer(explorerLayers.sachetAlerts);
            }
          });
        }
      })
      .catch(err => console.warn('Could not load SACHET GeoJSON in explorer:', err));
"""
    # Insert before the end of initExplorerLayers
    js = js.replace("return explorerLayers;\n  }", sachet_code + "\n    return explorerLayers;\n  }")
    print("Added sachetAlerts to initExplorerLayers.")

# 5. Append AP Monitoring Map initialization, Live Health Daemon Polling, Resident SOS, and Notification functions
new_functions = """
  // =========================================================================
  // 9. ANDHRA PRADESH STATEWIDE LIVE DISASTER MONITORING CONTROLLER
  // =========================================================================
  let apAlertsData = [];
  let apDistrictsLayer = null;
  let apSachetLayer = null;
  let apStationsLayer = null;
  let apStudyAreaLayer = null;

  function initApMonitoringMap() {
    const container = document.getElementById('ap-monitoring-map');
    if (!container || maps.apMonitor) return;

    const map = L.map('ap-monitoring-map', {
      center: [16.20, 80.50],
      zoom: 7,
      zoomControl: true,
      minZoom: 6,
      maxZoom: 14
    });
    maps.apMonitor = map;

    // Dark Basemap
    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
      attribution: 'Esri, HERE, Garmin, © OpenStreetMap',
      maxZoom: 16
    }).addTo(map);

    // 1. Load AP Districts Outline
    fetch('/api/v1/monitoring/ap-districts-geojson')
      .then(res => res.json())
      .then(geojson => {
        apDistrictsLayer = L.geoJSON(geojson, {
          style: {
            color: '#64748b',
            weight: 1.5,
            fillColor: 'transparent',
            fillOpacity: 0
          },
          onEachFeature: (f, layer) => {
            const name = f.properties?.district || f.properties?.NAME_2 || 'District';
            layer.bindTooltip(name, { sticky: true, className: 'gis-tooltip' });
          }
        }).addTo(map);
      })
      .catch(e => console.warn('AP districts load error:', e));

    // 2. Load Lower Godavari Study Area Outline
    fetch('/static/data/lower_godavari_study_area.geojson')
      .then(res => res.json())
      .then(geojson => {
        apStudyAreaLayer = L.geoJSON(geojson, {
          style: {
            color: '#06b6d4',
            weight: 2.5,
            dashArray: '5, 5',
            fillColor: '#06b6d4',
            fillOpacity: 0.08
          }
        }).addTo(map);
      })
      .catch(e => console.warn('Study area load error in AP map:', e));

    // 3. Load NDMA SACHET Live Alerted Mandals
    fetch('/api/v1/monitoring/ap-alerted-mandals-geojson')
      .then(res => res.json())
      .then(geojson => {
        apSachetLayer = L.geoJSON(geojson, {
          style: (f) => {
            const sev = f.properties?.severity;
            const col = sev === 'Extreme' ? '#ef4444' : (sev === 'Severe' ? '#f59e0b' : '#38bdf8');
            return {
              color: col,
              weight: 1.8,
              fillColor: col,
              fillOpacity: 0.40
            };
          },
          onEachFeature: (f, layer) => {
            const p = f.properties || {};
            layer.bindPopup(`
              <div class="gis-popup">
                <h4>⚠️ ${p.events || 'Official Alert'} (${p.severity})</h4>
                <p><strong>Mandal:</strong> ${p.mandal} | <strong>District:</strong> ${p.district}</p>
                <p><strong>Authority:</strong> ${p.senders || 'NDMA SACHET / APSDMA'}</p>
                <p><strong>Valid Until:</strong> ${p.expires || 'Active'}</p>
              </div>
            `);
          }
        }).addTo(map);
      })
      .catch(e => console.warn('SACHET mandals load error:', e));

    // 4. Load CWC River Gauge Stations
    loadRiverGauges(map);

    // 5. Load Official Disaster Bulletins List
    loadOfficialAlerts();

    // Map Controls
    const btnFitAp = document.getElementById('btnFitApExtent');
    if (btnFitAp) {
      btnFitAp.addEventListener('click', () => {
        map.setView([16.20, 80.50], 7);
      });
    }

    const btnFocusLg = document.getElementById('btnFocusLowerGodavari');
    if (btnFocusLg) {
      btnFocusLg.addEventListener('click', () => {
        map.setView([16.942, 81.776], 9);
      });
    }

    const btnRefresh = document.getElementById('btnRefreshLiveFeeds');
    if (btnRefresh) {
      btnRefresh.addEventListener('click', () => {
        btnRefresh.textContent = '⏳ Ingesting...';
        fetch('/api/v1/monitoring/refresh', { method: 'POST' })
          .then(res => res.json())
          .then(data => {
            btnRefresh.textContent = '✓ Updated';
            setTimeout(() => { btnRefresh.textContent = '⚡ Ingest Now'; }, 2000);
            loadRiverGauges(map);
            loadOfficialAlerts();
            pollLiveMonitoringHealth();
          })
          .catch(() => { btnRefresh.textContent = '⚡ Ingest Now'; });
      });
    }

    const btnRefreshGauges = document.getElementById('btnRefreshRiverGauges');
    if (btnRefreshGauges) {
      btnRefreshGauges.addEventListener('click', () => loadRiverGauges(map));
    }
  }

  function loadRiverGauges(map) {
    fetch('/api/v1/monitoring/river-stages')
      .then(res => res.json())
      .then(stations => {
        const listContainer = document.getElementById('riverGaugeStationsList');
        if (listContainer) {
          listContainer.innerHTML = stations.map(s => `
            <div class="gauge-station-item">
              <div class="station-info-left">
                <strong>${s.station_name}</strong>
                <span>${s.river_name} • Elev ${s.elevation_m}m</span>
              </div>
              <div class="station-levels-right">
                <span class="level-value">${s.current_water_level_m}m</span>
                <div><span class="level-tag ${s.status.toLowerCase()}">${s.status.replace('_', ' ')}</span></div>
              </div>
            </div>
          `).join('');
        }

        // Add markers to map if map provided
        if (map) {
          if (apStationsLayer) map.removeLayer(apStationsLayer);
          const markers = stations.map(s => {
            const isAlert = s.status !== 'NORMAL';
            const iconHtml = `<div style="background:${isAlert ? '#f59e0b' : '#38bdf8'}; width:14px; height:14px; border-radius:50%; border:2px solid #fff; box-shadow:0 0 6px ${isAlert ? '#f59e0b' : '#38bdf8'};"></div>`;
            const icon = L.divIcon({ html: iconHtml, className: 'cwc-gauge-icon', iconSize: [14, 14] });
            const m = L.marker([s.lat, s.lon], { icon });
            m.bindPopup(`
              <div class="gis-popup">
                <h4>🌊 ${s.station_name}</h4>
                <p><strong>River:</strong> ${s.river_name}</p>
                <p><strong>Current Level:</strong> ${s.current_water_level_m} m</p>
                <p><strong>Warning Stage:</strong> ${s.warning_stage_m} m</p>
                <p><strong>Danger Stage:</strong> ${s.danger_stage_m} m</p>
                <p><strong>Status:</strong> <span class="level-tag ${s.status.toLowerCase()}">${s.status}</span></p>
              </div>
            `);
            return m;
          });
          apStationsLayer = L.layerGroup(markers).addTo(map);
        }
      })
      .catch(e => console.warn('Could not load river stages:', e));
  }

  function loadOfficialAlerts() {
    fetch('/api/v1/monitoring/ap-disaster-alerts')
      .then(res => res.json())
      .then(alerts => {
        apAlertsData = alerts;
        const feedCount = document.getElementById('apAlertsFeedCount');
        if (feedCount) feedCount.textContent = `${alerts.length} Active Bulletins`;

        renderOfficialAlerts('all');

        // Setup filter chips
        document.querySelectorAll('.severity-filter-chips .chip-sev').forEach(chip => {
          chip.addEventListener('click', (e) => {
            document.querySelectorAll('.severity-filter-chips .chip-sev').forEach(c => c.classList.remove('active'));
            chip.classList.add('active');
            renderOfficialAlerts(chip.getAttribute('data-sev'));
          });
        });
      })
      .catch(e => console.warn('Could not load official alerts:', e));
  }

  function renderOfficialAlerts(sevFilter) {
    const container = document.getElementById('officialDisasterAlertsFeed');
    if (!container) return;

    const filtered = (sevFilter === 'all')
      ? apAlertsData
      : apAlertsData.filter(a => a.severity.toLowerCase() === sevFilter.toLowerCase());

    if (filtered.length === 0) {
      container.innerHTML = '<div style="color:var(--text-muted); font-size:12px; padding:10px;">No alerts matching filter.</div>';
      return;
    }

    container.innerHTML = filtered.map(a => {
      const sLower = a.severity.toLowerCase();
      const lgBadge = a.intersects_lower_godavari ? '<span class="count-pill" style="background:rgba(6,182,212,0.2); color:#06b6d4;">Lower Godavari</span>' : '';
      return `
        <div class="alert-item-card ${sLower}">
          <div class="alert-card-top">
            <h5>${a.headline}</h5>
            <span class="alert-badge ${sLower}">${a.severity.toUpperCase()}</span>
          </div>
          <p class="alert-item-desc">${a.description || a.instructions || 'Standard precautionary protocol.'}</p>
          <div class="alert-item-meta">
            <span>Mandals: ${a.mandals_affected_count} ${lgBadge}</span>
            <span>Source: ${a.source_agency}</span>
          </div>
        </div>
      `;
    }).join('');
  }

  // Live Monitoring Daemon Health Polling
  function pollLiveMonitoringHealth() {
    fetch('/api/v1/monitoring/health')
      .then(res => res.json())
      .then(data => {
        const badge = document.getElementById('liveMonitoringBadge');
        const text = document.getElementById('liveMonitoringStatusText');
        if (badge && text) {
          const liveCount = Object.values(data.sources || {}).filter(s => s.status === 'LIVE' || s.status === 'AVAILABLE').length;
          text.textContent = `SYSTEM ACTIVE: ${liveCount} FEEDS LIVE`;
          badge.title = `Continuous Monitoring Daemon: ${data.daemon_status} | Health: ${data.overall_health} | Checks: ${data.total_checks_performed}`;
        }
      })
      .catch(e => console.warn('Health poll error:', e));
  }

  // Initialize Polling
  pollLiveMonitoringHealth();
  setInterval(pollLiveMonitoringHealth, 30000);

  // =========================================================================
  // 10. RESIDENT EMERGENCY SOS & NOTIFICATIONS CONTROLLER
  // =========================================================================
  function initResidentSosAndNotifications() {
    // 1. Resident Help Request Form
    const helpForm = document.getElementById('formResidentHelpRequest');
    if (helpForm) {
      helpForm.addEventListener('submit', (e) => {
        e.preventDefault();
        const payload = {
          resident_name: document.getElementById('helpResidentName').value.trim(),
          contact_phone: document.getElementById('helpContactPhone').value.trim(),
          mandal: document.getElementById('helpMandal').value,
          specific_location: document.getElementById('helpSpecificLocation').value.trim(),
          required_assistance: document.getElementById('helpRequiredAssistance').value,
          number_of_persons: parseInt(document.getElementById('helpFamilyCount').value, 10) || 1,
          urgency: 'CRITICAL'
        };

        const fb = document.getElementById('helpSubmissionFeedback');
        const btn = document.getElementById('btnSubmitHelpRequest');
        if (btn) btn.disabled = true;

        fetch('/api/v1/operations/resident/help-request', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        })
          .then(res => res.json())
          .then(data => {
            if (btn) btn.disabled = false;
            if (fb) {
              fb.style.display = 'block';
              fb.style.background = 'rgba(16, 185, 129, 0.2)';
              fb.style.color = '#10b981';
              fb.style.border = '1px solid #10b981';
              fb.innerHTML = `✓ Emergency Assistance Request Logged: <strong>${data.request_id}</strong> for ${data.mandal}. Transmitted to Mandal Incident Command.`;
            }
            helpForm.reset();
            loadIncomingHelpRequests();
          })
          .catch(err => {
            if (btn) btn.disabled = false;
            if (fb) {
              fb.style.display = 'block';
              fb.style.background = 'rgba(239, 68, 68, 0.2)';
              fb.style.color = '#ef4444';
              fb.innerHTML = 'Error logging emergency assistance request. Please try again.';
            }
          });
      });
    }

    // 2. Incoming Help Requests Loader
    function loadIncomingHelpRequests() {
      fetch('/api/v1/operations/resident/help-requests')
        .then(res => res.json())
        .then(requests => {
          const tbody = document.getElementById('residentHelpRequestsTbody');
          const countPill = document.getElementById('residentRequestsCount');
          if (countPill) countPill.textContent = `${requests.length} Active`;
          if (!tbody) return;

          if (requests.length === 0) {
            tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; color:var(--text-muted);">No pending resident assistance requests.</td></tr>';
            return;
          }

          tbody.innerHTML = requests.map(r => `
            <tr>
              <td><strong>${r.request_id}</strong></td>
              <td>${r.resident_name}</td>
              <td>${r.contact_phone}</td>
              <td>${r.mandal}</td>
              <td><span class="count-pill" style="background:rgba(239,68,68,0.15); color:#ef4444;">${r.required_assistance}</span></td>
              <td>${r.number_of_persons}</td>
              <td><span class="badge-status requested">${r.status}</span></td>
              <td>
                <button class="btn-sm btn-action-primary" onclick="alert('Request ${r.request_id} acknowledged and assigned to ERT dispatch unit.')">Dispatch ERT</button>
              </td>
            </tr>
          `).join('');
        })
        .catch(e => console.warn('Could not load incoming help requests:', e));
    }

    // 3. Notification Test Dispatch
    const btnTestNotif = document.getElementById('btnTriggerTestNotification');
    if (btnTestNotif) {
      btnTestNotif.addEventListener('click', () => {
        const statusSpan = document.getElementById('notifDispatchStatusText');
        if (statusSpan) statusSpan.textContent = 'Dispatching test broadcast...';

        fetch('/api/v1/notifications/test-delivery', { method: 'POST' })
          .then(res => res.json())
          .then(rec => {
            if (statusSpan) {
              statusSpan.textContent = `✓ Dispatched ${rec.dispatch_id} via ${rec.provider_name} (${rec.delivery_status})`;
            }
            loadNotificationHistory();
          })
          .catch(e => {
            if (statusSpan) statusSpan.textContent = 'Notification dispatch failed.';
          });
      });
    }

    // 4. Notification History Loader
    function loadNotificationHistory() {
      fetch('/api/v1/notifications/history')
        .then(res => res.json())
        .then(logs => {
          const tbody = document.getElementById('notificationDeliveryLogTbody');
          if (!tbody) return;

          if (logs.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:var(--text-muted);">No notification delivery logs found.</td></tr>';
            return;
          }

          tbody.innerHTML = logs.map(l => `
            <tr>
              <td><strong>${l.dispatch_id}</strong></td>
              <td>${l.recipient_id}</td>
              <td><span class="count-pill">${l.channel}</span></td>
              <td><span class="badge-status ${l.delivery_status.toLowerCase()}">${l.delivery_status}</span></td>
              <td>${l.provider_name}</td>
              <td>${new Date(l.dispatched_at).toLocaleTimeString()}</td>
            </tr>
          `).join('');
        })
        .catch(e => console.warn('Could not load notification logs:', e));
    }

    loadIncomingHelpRequests();
    loadNotificationHistory();
  }

  // Initialize SOS & Notifications
  initResidentSosAndNotifications();
"""

# Append new functions before the closing of DOMContentLoaded listener
if "initApMonitoringMap" not in js:
    # Find last closing
    idx = js.rfind("});")
    if idx != -1:
        js = js[:idx] + "\n" + new_functions + "\n});"
        print("Successfully integrated initApMonitoringMap and SOS controller into app.js!")
    else:
        js += "\n" + new_functions

with open(APP_JS_PATH, "w", encoding="utf-8") as f:
    f.write(js)

print("frontend/app.js updated successfully!")
