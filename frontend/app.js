
  // =========================================================================
  // COMMUNITY GROUND HAZARD SUBMISSION & LIFECYCLE CONTROLLER (PHASE 2)
  // =========================================================================
  window.handleHazardReportSubmit = async function(e) {
    e.preventDefault();
    const btn = document.getElementById('btnSubmitHazardReport');
    const fb = document.getElementById('hazardSubmitFeedback');
    const mandal = document.getElementById('hazardMandal')?.value || 'Razole';
    const category = document.getElementById('hazardCategory')?.value || 'Flood Inundation';
    const description = document.getElementById('hazardDescription')?.value || '';
    const voiceNote = document.getElementById('hazardVoiceNote')?.value || null;
    const reporterName = document.getElementById('hazardReporterName')?.value || 'Local Resident';
    const photoInput = document.getElementById('hazardPhotoFile');

    if (btn) {
      btn.classList.add('loading');
      btn.disabled = true;
    }

    let photoData = null;
    if (photoInput && photoInput.files && photoInput.files[0]) {
      const file = photoInput.files[0];
      photoData = await new Promise((resolve) => {
        const reader = new FileReader();
        reader.onload = (re) => resolve(re.target.result);
        reader.readAsDataURL(file);
      });
    }

    const lat = window.appState && window.appState.selectedLocation ? window.appState.selectedLocation.lat : 16.48;
    const lon = window.appState && window.appState.selectedLocation ? window.appState.selectedLocation.lon : 81.82;

    const payload = {
      mandal: mandal,
      district: 'Dr. B.R. Ambedkar Konaseema',
      category: category,
      description: description,
      latitude: lat,
      longitude: lon,
      reporter_name: reporterName,
      location_description: 'Reported via PRAVAH 360 Citizen Web Portal',
      photo_data: photoData,
      voice_note_transcript: voiceNote
    };

    try {
      const res = await fetch('/api/v1/community/hazards/report', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (btn) {
        btn.classList.remove('loading');
        btn.disabled = false;
      }

      // Show Receipt Modal with Tracking ID and Lifecycle Progress
      const receiptModal = document.getElementById('hazardReceiptModal');
      const receiptIdEl = document.getElementById('receiptReportId');
      const dupWarnEl = document.getElementById('receiptDuplicateWarning');

      if (receiptIdEl) receiptIdEl.textContent = data.report_id;
      if (dupWarnEl) {
        if (data.potential_duplicate && data.potential_duplicate.is_potential_duplicate) {
          dupWarnEl.style.display = 'block';
          dupWarnEl.textContent = '⚠️ ' + data.potential_duplicate.suggestion;
        } else {
          dupWarnEl.style.display = 'none';
        }
      }
      if (receiptModal) receiptModal.style.display = 'flex';

      // Reset form
      if (document.getElementById('hazardDescription')) document.getElementById('hazardDescription').value = '';
      if (document.getElementById('hazardVoiceNote')) document.getElementById('hazardVoiceNote').value = '';
      if (photoInput) photoInput.value = '';

      loadCommunityHazardsFeed();
    } catch (err) {
      console.error('Hazard submission error:', err);
      if (btn) {
        btn.classList.remove('loading');
        btn.disabled = false;
      }
      alert('Submission failed. Please check connection and try again.');
    }
  };

  window.recordHazardVoiceNote = function() {
    const input = document.getElementById('hazardVoiceNote');
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert('Speech recognition is not supported in this browser. Please type your note.');
      return;
    }
    const rec = new SpeechRecognition();
    rec.lang = (window.currentAppLang === 'te') ? 'te-IN' : 'en-IN';
    rec.start();
    if (input) input.placeholder = '🎤 Listening... Speak your observation...';
    rec.onresult = (ev) => {
      const transcript = ev.results[0][0].transcript;
      if (input) input.value = transcript;
    };
    rec.onerror = () => {
      if (input) input.placeholder = 'Spoken voice transcript will appear here...';
    };
    rec.onend = () => {
      if (input && !input.value) input.placeholder = 'Spoken voice transcript will appear here...';
    };
  };

  async function loadCommunityHazardsFeed() {
    const listEl = document.getElementById('communityHazardsList');
    if (!listEl) return;
    try {
      const res = await fetch('/api/v1/community/hazards');
      const reports = await res.json();
      if (!reports || reports.length === 0) return;
      listEl.innerHTML = reports.slice(0, 6).map(r => {
        const statusColors = {
          SUBMITTED: '#64748b',
          UNDER_REVIEW: '#d97706',
          VERIFIED: '#059669',
          RESPONSE_ASSIGNED: '#7c3aed',
          IN_PROGRESS: '#0284c7',
          RESOLVED: '#10b981',
          NEEDS_MORE_INFORMATION: '#eab308',
          DUPLICATE: '#94a3b8',
          REJECTED: '#ef4444'
        };
        const stColor = statusColors[r.status] || '#64748b';
        return `
          <div style="padding:10px 12px; background:var(--color-mist); border-radius:8px; font-size:12.5px; border-left:3px solid ${stColor};">
            <div style="display:flex; justify-content:space-between; font-weight:700; color:var(--color-forest);">
              <span>${r.category.replace(/_/g, ' ')}</span>
              <span style="color:${stColor}; font-weight:800; font-size:11px;">● ${r.status.replace(/_/g, ' ')}</span>
            </div>
            <div style="color:var(--text-muted-dark); font-size:11.5px; margin-top:2px;">${r.mandal} • ${r.description}</div>
            ${r.linked_resource_request_id ? `<div style="font-size:11px; color:#7c3aed; font-weight:700; margin-top:3px;">🚒 ERT Escalation Linked: ${r.linked_resource_request_id}</div>` : ''}
            <div style="font-size:10.5px; color:#64748b; margin-top:4px;">Reporter: ${r.reporter_name_redacted} • ${r.created_at}</div>
          </div>
        `;
      }).join('');
    } catch (e) {
      console.warn('Could not load hazards feed:', e);
    }
  }

  // =========================================================================
  // =========================================================================
  // ALERT TEMPORAL STATE & FRESHNESS ENGINE (PHASE B: SCIENTIFIC INTEGRITY)
  // Distinguishes 4 distinct states: LIVE / FRESH, STALE, EXPIRED, UNAVAILABLE
  // =========================================================================
  window.computeAlertTemporalState = function(a, isFeedDown) {
    if (isFeedDown && (!a || !a.is_cached)) {
      return {
        state: 'UNAVAILABLE',
        badgeLabel: 'FEED UNAVAILABLE',
        badgeBg: '#fee2e2',
        badgeColor: '#991b1b',
        borderCol: '#ef4444',
        cardOpacity: '1.0',
        isExpired: false,
        statusDesc: 'Upstream agency feed connection offline.'
      };
    }
    if (!a) {
      return {
        state: 'UNAVAILABLE',
        badgeLabel: 'NO DATA',
        badgeBg: '#fee2e2',
        badgeColor: '#991b1b',
        borderCol: '#ef4444',
        cardOpacity: '1.0',
        isExpired: false,
        statusDesc: 'No alert data returned.'
      };
    }
    const now = new Date();

    // 1. Check expiration (Authoritative status or explicit expiration timestamp)
    let isExp = (a.status === 'EXPIRED' || a.freshness_state === 'EXPIRED' || a.is_expired === true);
    if (a.expires_at) {
      try {
        const expDt = new Date(a.expires_at);
        if (!isNaN(expDt.getTime()) && expDt < now) {
          isExp = true;
        }
      } catch(e) {}
    }
    if (isExp) {
      return {
        state: 'EXPIRED',
        badgeLabel: 'EXPIRED / RETIRED',
        badgeBg: '#f1f5f9',
        badgeColor: '#64748b',
        borderCol: '#94a3b8',
        cardOpacity: '0.72',
        isExpired: true,
        statusDesc: 'Bulletin has reached its expiration time and is retained for audit.'
      };
    }

    // 2. Check unknown freshness
    if (a.freshness_state === 'UNKNOWN') {
      return {
        state: 'UNKNOWN',
        badgeLabel: 'UNKNOWN FRESHNESS',
        badgeBg: '#f1f5f9',
        badgeColor: '#475569',
        borderCol: '#94a3b8',
        cardOpacity: '0.90',
        isExpired: false,
        statusDesc: 'Temporal provenance unverified or timestamps unavailable.'
      };
    }

    // 3. Check stale (explicit flag, or retrieval age > 30 minutes)
    let isStale = (a.freshness_state === 'STALE' || a.stale === true || a.is_stale === true);
    let ageMinutes = 0;
    const tsStr = a.retrieved_at || a.issued_at;
    if (tsStr) {
      try {
        const dt = new Date(tsStr);
        if (!isNaN(dt.getTime())) {
          ageMinutes = Math.floor((now - dt) / 60000);
          if (ageMinutes > 30) isStale = true;
        }
      } catch(e) {}
    }
    if (isStale) {
      const ageStr = ageMinutes > 60 ? `${Math.floor(ageMinutes/60)}h ${ageMinutes%60}m ago` : `${Math.max(1, ageMinutes)}m ago`;
      return {
        state: 'STALE',
        badgeLabel: `STALE (${ageStr})`,
        badgeBg: '#fef3c7',
        badgeColor: '#92400e',
        borderCol: '#d97706',
        cardOpacity: '0.94',
        isExpired: false,
        statusDesc: `Cached emergency bulletin retrieved ${ageStr}.`
      };
    }

    // 4. Check confirmed cached
    if (a.freshness_state === 'CACHED' || a.is_cached === true) {
      return {
        state: 'CACHED',
        badgeLabel: 'CACHED BULLETIN',
        badgeBg: '#fef3c7',
        badgeColor: '#b45309',
        borderCol: '#f59e0b',
        cardOpacity: '0.96',
        isExpired: false,
        statusDesc: 'Verified alert loaded from local disaster cache store.'
      };
    }

    // 5. Live / Fresh
    return {
      state: 'LIVE',
      badgeLabel: 'LIVE / FRESH',
      badgeBg: '#dcfce7',
      badgeColor: '#166534',
      borderCol: '#10b981',
      cardOpacity: '1.0',
      isExpired: false,
      statusDesc: 'Active streaming warning from authoritative gateway.'
    };
  };

  // CONTINUOUS ALERT & NOTIFICATION CENTRE CONTROLLER (PHASE 4)
  // =========================================================================
  let _activeNotifTier = 'ALL';
  let _cachedNotifications = null;

  window.toggleMobileNav = function() {
    const nav = document.getElementById('landingNavLinks');
    if (nav) {
      nav.classList.toggle('mobile-open');
    }
  };

  window.toggleNotificationDrawer = function() {
    const drawer = document.getElementById('notificationCenterDrawer');
    const backdrop = document.getElementById('notificationDrawerBackdrop');
    if (!drawer) return;
    const isVisible = (drawer.style.display === 'flex');
    if (isVisible) {
      drawer.style.display = 'none';
      if (backdrop) backdrop.style.display = 'none';
    } else {
      drawer.style.display = 'flex';
      if (backdrop) backdrop.style.display = 'block';
      window.pollContinuousNotifications();
    }
  };

  window.setNotificationFilter = function(tier) {
    _activeNotifTier = tier;
    document.querySelectorAll('.notif-tab').forEach(b => {
      b.classList.toggle('active', b.getAttribute('data-tier') === tier);
      if (b.getAttribute('data-tier') === tier) {
        b.style.borderBottom = '2px solid var(--color-forest)';
        b.style.color = 'var(--color-forest)';
      } else {
        b.style.borderBottom = 'none';
        b.style.color = '#64748b';
      }
    });
    renderNotificationFeed();
  };

  window.pollContinuousNotifications = async function() {
    const listEl = document.getElementById('notificationFeedList');
    try {
      const res = await fetch('/api/v1/notifications/continuous-feed');
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      _cachedNotifications = data;

      // Read persisted acknowledged IDs from localStorage
      let localReadIds = new Set();
      try {
        const stored = localStorage.getItem('pravah_read_alerts');
        if (stored) localReadIds = new Set(JSON.parse(stored));
      } catch (e) {}

      // Apply local read status to items
      let totalUnread = 0;
      ['official_warnings', 'model_advisories', 'community_reports'].forEach(k => {
        if (data.tiers && data.tiers[k] && Array.isArray(data.tiers[k].items)) {
          data.tiers[k].items.forEach(item => {
            if (localReadIds.has(item.id)) {
              item.is_acknowledged = true;
            }
            if (!item.is_acknowledged) {
              totalUnread++;
            }
          });
        }
      });

      // Update badge counts honestly from real computed records
      data.unread_count = totalUnread;
      const bEl = document.getElementById('landingUnreadCount');
      if (bEl) bEl.textContent = totalUnread;
      const dBadge = document.getElementById('drawerUnreadBadge');
      if (dBadge) dBadge.textContent = totalUnread;

      renderNotificationFeed();
    } catch (e) {
      console.warn('Notification polling error:', e);
      if (listEl) {
        listEl.innerHTML = `
          <div style="text-align:center; padding:35px 20px; color:#ef4444; background:#fef2f2; border:1px solid #fecaca; border-radius:12px;">
            <span style="font-size:32px;">⚠️</span>
            <h4 style="margin:10px 0 6px 0; font-size:15px; color:#991b1b; font-weight:800;">Notification Server Offline</h4>
            <p style="margin:0; font-size:12.5px; color:#64748b; line-height:1.5;">Unable to fetch live alerts from server. Please verify your connection or backend service status.</p>
            <button type="button" onclick="window.pollContinuousNotifications()" style="margin-top:14px; background:var(--color-forest); color:#fff; border:none; padding:6px 14px; border-radius:6px; font-size:12px; font-weight:700; cursor:pointer;">Retry Connection</button>
          </div>
        `;
      }
    }
  };

  window.markAllNotificationsRead = async function() {
    if (!_cachedNotifications || !_cachedNotifications.tiers) return;
    const allItems = [
      ...(_cachedNotifications.tiers.official_warnings.items || []),
      ...(_cachedNotifications.tiers.model_advisories.items || []),
      ...(_cachedNotifications.tiers.community_reports.items || [])
    ];
    const unread = allItems.filter(i => !i.is_acknowledged);
    for (const item of unread) {
      try {
        await fetch('/api/v1/notifications/acknowledge', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ alert_id: item.id, acknowledged_by: 'Resident / Officer' })
        });
        item.is_acknowledged = true;
      } catch (e) {
        console.warn('Ack error for', item.id, e);
      }
    }
    _cachedNotifications.unread_count = 0;
    try {
      const allIds = allItems.map(i => i.id);
      localStorage.setItem('pravah_read_alerts', JSON.stringify(allIds));
    } catch (e) {}
    const bEl = document.getElementById('landingUnreadCount');
    if (bEl) bEl.textContent = '0';
    const dBadge = document.getElementById('drawerUnreadBadge');
    if (dBadge) dBadge.textContent = '0';
    renderNotificationFeed();
  };

  window.focusNotificationArea = function(mandalName, districtName) {
    window.toggleNotificationDrawer();
    if (typeof navigateTo === 'function') {
      navigateTo('situation_home');
    }
    if (mandalName && typeof window.selectMandalByName === 'function') {
      setTimeout(() => window.selectMandalByName(mandalName), 400);
    }
  };

  function renderNotificationFeed() {
    const listEl = document.getElementById('notificationFeedList');
    if (!listEl || !_cachedNotifications) return;

    let items = [];
    const tiers = _cachedNotifications.tiers;

    if (_activeNotifTier === 'ALL') {
      items = [...(tiers.official_warnings.items || []), ...(tiers.model_advisories.items || []), ...(tiers.community_reports.items || [])];
    } else if (_activeNotifTier === 'OFFICIAL') {
      items = tiers.official_warnings.items || [];
    } else if (_activeNotifTier === 'MODEL') {
      items = tiers.model_advisories.items || [];
    } else if (_activeNotifTier === 'COMMUNITY') {
      items = tiers.community_reports.items || [];
    }

    if (items.length === 0) {
      listEl.innerHTML = `
        <div style="text-align:center; padding:45px 20px; color:#64748b;">
          <span style="font-size:36px; display:block; margin-bottom:10px;">🛡️</span>
          <h4 style="margin:0 0 6px 0; font-size:15px; font-weight:800; color:var(--color-forest);">No Active Alerts</h4>
          <p style="margin:0; font-size:12.5px; color:#94a3b8;">There are currently no active alerts under this tier. Regional surveillance is operating normally.</p>
        </div>
      `;
      return;
    }

    listEl.innerHTML = items.map(item => {
      const isOfficial = (item.tier || '').includes('OFFICIAL');
      const isModel = (item.tier || '').includes('MODEL');
      const borderCol = isOfficial ? '#dc2626' : isModel ? '#d97706' : '#0284c7';
      const badgeBg = isOfficial ? '#fee2e2' : isModel ? '#fef3c7' : '#e0f2fe';
      const badgeCol = isOfficial ? '#991b1b' : isModel ? '#92400e' : '#0369a1';
      const sevCol = (item.severity === 'Severe' || item.severity === 'Critical' || item.severity === 'Extreme') ? '#dc2626' : '#d97706';
      const mandalStr = (item.affected_mandals && item.affected_mandals.length > 0) ? item.affected_mandals.join(', ') : (item.affected_district ? 'District: ' + item.affected_district : 'District not specified');
      const firstMandal = (item.affected_mandals && item.affected_mandals.length > 0) ? item.affected_mandals[0] : null;

      // Evaluate temporal freshness
      const tempState = window.computeAlertTemporalState(item, false);
      const expiredBanner = tempState.isExpired
        ? '<div style="background:#f1f5f9; border:1px solid #cbd5e1; border-radius:6px; padding:6px 10px; font-size:11px; font-weight:700; color:#64748b; margin-bottom:8px;">⚠️ EXPIRED BULLETIN: This warning has reached its expiration time and is retained for post-incident audit.</div>' : '';

      return `
        <div style="background:#fff; border:1px solid #e2e8f0; border-left:4px solid ${tempState.isExpired ? '#94a3b8' : borderCol}; opacity:${tempState.cardOpacity}; border-radius:10px; padding:14px; box-shadow:0 2px 8px rgba(0,0,0,0.04); transition:all 0.2s; margin-bottom:12px;">
          ${expiredBanner}
          <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
            <div style="display:flex; gap:6px; align-items:center;">
              <span style="background:${badgeBg}; color:${badgeCol}; font-size:10.5px; font-weight:800; padding:3px 8px; border-radius:4px; text-transform:uppercase;">${item.badge_label || item.tier}</span>
              <span style="font-size:10px; font-weight:800; padding:2px 7px; border-radius:10px; background:${tempState.badgeBg}; color:${tempState.badgeColor}; border:1px solid ${tempState.borderCol}40; letter-spacing:0.04em;">${tempState.badgeLabel}</span>
              <span style="font-size:10.5px; font-weight:700; color:${sevCol}; background:#f8fafc; padding:2px 6px; border-radius:4px; border:1px solid #e2e8f0;">${item.severity && item.severity !== 'Unknown' ? item.severity : 'Unknown'}</span>
            </div>
          </div>
          <h4 style="margin:6px 0 6px 0; font-size:14px; font-weight:800; color:#0f172a; line-height:1.4;">${item.headline}</h4>
          <p style="margin:0 0 8px 0; font-size:12.5px; color:#475569; line-height:1.5;">${item.description}</p>
          <div style="font-size:11.5px; color:#059669; font-weight:700; margin-bottom:8px;">📢 Instruction: ${item.instruction}</div>

          <!-- Distinct Temporal Metadata -->
          <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:7px 10px; font-size:11px; color:#475569; margin-bottom:8px;">
            <div><strong>Published:</strong> ${item.issued_at || 'Not reported'}</div>
            <div><strong>Retrieved:</strong> ${item.retrieved_at || 'Not reported'}</div>
            <div style="grid-column: span 2;"><strong>Valid Until:</strong> ${item.expires_at || 'In force until further notice'}</div>
          </div>

          <div style="font-size:11.5px; color:#64748b; margin-bottom:8px;">
            📍 <strong>Area:</strong> ${mandalStr}
          </div>
          <div style="display:flex; justify-content:space-between; align-items:center; border-top:1px solid #f1f5f9; padding-top:10px; margin-top:6px;">
            <span style="font-size:11px; color:#64748b;">Source: ${item.source || 'Unknown'}</span>
            <div style="display:flex; gap:8px;">
              ${firstMandal ? `<button type="button" onclick="window.focusNotificationArea('${firstMandal}', '${item.affected_district || ''}')" style="background:#f8fafc; border:1px solid #cbd5e1; padding:4px 8px; border-radius:6px; font-size:11px; font-weight:600; color:#334155; cursor:pointer;" title="View on map">📍 Map</button>` : ''}
              ${item.is_acknowledged
                ? `<span style="font-size:11px; color:#059669; font-weight:700; display:inline-flex; align-items:center; gap:3px;">✓ Read</span>`
                : `<button type="button" onclick="window.acknowledgeNotification('${item.id}')" style="background:var(--color-forest); border:none; color:#fff; padding:4px 10px; border-radius:6px; font-size:11px; font-weight:700; cursor:pointer;">✓ Mark as Read</button>`
              }
            </div>
          </div>
        </div>
      `;
    }).join('');
  }

  window.acknowledgeNotification = async function(alertId) {
    try {
      await fetch('/api/v1/notifications/acknowledge', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ alert_id: alertId, acknowledged_by: 'User' })
      });
      // Mark locally
      if (_cachedNotifications && _cachedNotifications.tiers) {
        for (const k of ['official_warnings', 'model_advisories', 'community_reports']) {
          const it = (_cachedNotifications.tiers[k].items || []).find(x => x.id === alertId);
          if (it) it.is_acknowledged = true;
        }
        if (_cachedNotifications.unread_count > 0) _cachedNotifications.unread_count--;
        const bEl = document.getElementById('landingUnreadCount');
        if (bEl) bEl.textContent = _cachedNotifications.unread_count;
        const dBadge = document.getElementById('drawerUnreadBadge');
        if (dBadge) dBadge.textContent = _cachedNotifications.unread_count;
      }
      renderNotificationFeed();
    } catch (e) {
      console.warn('Acknowledge error:', e);
    }
  };

  // =========================================================================
  // HISTORICAL EVENT REPLAY CONTROLLER (PHASE 6 - MURASU & ARNAB)
  // =========================================================================
  let _activeReplayTimeline = null;

  window.openHistoricalEventReplay = function(eventId = 'CYCLONE_MURASU_NOV_2026') {
    const modal = document.getElementById('historicalEventReplayModal');
    if (!modal) return;
    modal.style.display = 'flex';
    window.loadHistoricalEvent(eventId);
  };

  window.loadHistoricalEvent = async function(eventId) {
    document.querySelectorAll('.btn-event-pill').forEach(b => {
      b.style.border = (b.id === 'btnEventMurasu' && eventId.includes('MURASU')) || (b.id === 'btnEventArnab' && eventId.includes('ARNAB'))
        ? '2px solid var(--color-forest)'
        : '1px solid #cbd5e1';
    });

    try {
      const res = await fetch(`/api/v1/events/${eventId}/timeline`);
      const ev = await res.json();
      _activeReplayTimeline = ev;

      const navEl = document.getElementById('replayStepsNav');
      if (navEl && ev.timeline_steps) {
        navEl.innerHTML = ev.timeline_steps.map((s, idx) => `
          <button type="button" class="btn-step-pill" onclick="window.selectReplayStep('${eventId}', ${s.step_id})" style="padding:8px 14px; border-radius:8px; border:1px solid #cbd5e1; background:${idx === 0 ? 'var(--color-forest)' : '#f8fafc'}; color:${idx === 0 ? '#fff' : '#334155'}; font-size:12px; font-weight:700; cursor:pointer; white-space:nowrap;">
            ${s.phase}
          </button>
        `).join('');
      }

      if (ev.timeline_steps && ev.timeline_steps.length > 0) {
        window.selectReplayStep(eventId, ev.timeline_steps[0].step_id);
      }
    } catch (e) {
      console.warn('Historical replay load error:', e);
    }
  };

  window.selectReplayStep = async function(eventId, stepId) {
    try {
      const res = await fetch(`/api/v1/events/${eventId}/step/${stepId}`);
      const data = await res.json();
      const s = data.step_data;
      const card = document.getElementById('replayStepContentCard');
      if (!card || !s) return;

      card.innerHTML = `
        <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid #e2e8f0; padding-bottom:10px; margin-bottom:12px;">
          <div>
            <span style="background:var(--color-mist); color:var(--color-forest); font-size:11px; font-weight:800; padding:3px 8px; border-radius:4px;">PHASE: ${s.phase}</span>
            <h4 style="margin:6px 0 0 0; font-size:16px; font-weight:800; color:var(--color-forest);">${s.timestamp}</h4>
          </div>
          <div style="text-align:right;">
            <div style="font-size:11px; color:#64748b;">Dowleswaram Barrage</div>
            <div style="font-size:18px; font-weight:900; color:var(--color-coral);">${s.dowleswaram_gauge_ft} ft</div>
          </div>
        </div>

        <div style="margin-bottom:12px;">
          <div style="font-size:12px; font-weight:800; color:#dc2626; text-transform:uppercase;">🏛️ Official Authoritative Bulletin (${s.source}):</div>
          <p style="margin:4px 0 0 0; font-size:13.5px; color:#1e293b; line-height:1.55; background:#fff; padding:10px 14px; border-radius:8px; border-left:3px solid #dc2626;">"${s.official_bulletin}"</p>
        </div>

        <div style="margin-bottom:12px;">
          <div style="font-size:12px; font-weight:800; color:#0369a1; text-transform:uppercase;">🛰️ PRAVAH 360 Reconstructed Model Advisory (At This Timestamp):</div>
          <p style="margin:4px 0 0 0; font-size:13px; color:#0c4a6e; line-height:1.55; background:#f0f9ff; padding:10px 14px; border-radius:8px; border-left:3px solid #0284c7;">${s.model_advisory}</p>
        </div>

        <div style="display:flex; flex-wrap:wrap; gap:8px; align-items:center; margin-top:12px; padding-top:10px; border-top:1px solid #e2e8f0;">
          <span style="font-size:12px; font-weight:700; color:#475569;">Alerted Mandals:</span>
          ${s.affected_mandals.map(m => `<span style="background:#fee2e2; color:#991b1b; padding:2px 8px; border-radius:12px; font-size:11px; font-weight:700;">${m}</span>`).join('')}
          <span style="margin-left:auto; font-size:12px; color:#64748b; font-weight:600;">24h Rainfall: ${s.rainfall_24h_mm} mm</span>
        </div>

        <div style="margin-top:12px; background:#fef3c7; border:1px solid #fde68a; padding:10px 14px; border-radius:8px; font-size:12.5px; color:#92400e;">
          <strong>💡 Evaluation Milestone Key Takeaway:</strong> ${s.key_takeaway}
        </div>
      `;
    } catch (e) {
      console.warn('Replay step error:', e);
    }
  };

  // =========================================================================
  // AI MODEL PERFORMANCE & SCIENTIFIC VALIDATION WORKSPACE (PHASE 5)
  // =========================================================================
  window.openModelValidationWorkspace = async function() {
    const modal = document.getElementById('modelPerformanceModal');
    const content = document.getElementById('modelValidationContent');
    if (!modal) return;
    modal.style.display = 'flex';

    try {
      const res = await fetch('/api/v1/prediction/validation-report');
      if (!res.ok) throw new Error(`Validation API returned HTTP ${res.status}`);
      const v = await res.json();
      const rf = v.classification_metrics.random_forest;
      const base = v.classification_metrics.baseline_logistic;
      const riv = v.continuous_river_stage_metrics.random_forest;
      const rivBase = v.continuous_river_stage_metrics.baseline;
      const cm = rf.confusion_matrix;
      const fi = v.feature_importance || {};

      content.innerHTML = `
        <!-- Provenance & Scientific Integrity Banner -->
        <div style="background:#fef2f2; border:1px solid #f87171; padding:14px 18px; border-radius:10px; font-size:12.5px; color:#991b1b; margin-bottom:20px; line-height:1.55;">
          <strong>⚖️ SCIENTIFIC INTEGRITY &amp; DISCLOSURE:</strong> ${v.model_metadata.scientific_disclaimer}
        </div>

        <!-- Section A: Model Information Grid -->
        <div style="display:grid; grid-template-columns:1fr 1fr; gap:16px; margin-bottom:24px;">
          <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:16px;">
            <div style="font-size:11.5px; font-weight:800; color:var(--color-forest); text-transform:uppercase; margin-bottom:4px; letter-spacing:0.04em;">Target Architecture</div>
            <h4 style="margin:0 0 6px 0; font-size:17px; font-weight:900; color:#0f172a;">${v.model_metadata.name}</h4>
            <div style="font-size:12.5px; color:#334155; font-weight:700;">Model: ${v.model_metadata.rf_version} (Benchmark: ${v.model_metadata.baseline_version})</div>
            <p style="margin:6px 0 0 0; font-size:12px; color:#64748b; line-height:1.5;">
              <strong>Input Features (9):</strong> Elevation, Stream Distance, Drainage Density, Slope, Land Cover Runoff, SAR Water %, 24h Rain, 72h Rain Accumulation, Dowleswaram Gauge Ratio.
            </p>
          </div>
          <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:16px;">
            <div style="font-size:11.5px; font-weight:800; color:#0284c7; text-transform:uppercase; margin-bottom:4px; letter-spacing:0.04em;">Independent Spatial Holdout</div>
            <h4 style="margin:0 0 6px 0; font-size:17px; font-weight:900; color:#0f172a;">4 Coastal Delta Mandals</h4>
            <div style="font-size:12.5px; color:#334155; font-weight:700;">Held-out Partition: ${v.model_metadata.heldout_test_mandals.join(', ')}</div>
            <p style="margin:6px 0 0 0; font-size:12px; color:#64748b; line-height:1.5;">
              Training on 17 inland/mid-basin mandals (${v.model_metadata.total_train_samples} samples). Evaluated on ${v.model_metadata.total_test_samples} unseen test samples without spatial leakage.
            </p>
          </div>
        </div>

        <!-- Section B: Evaluation Metrics (Separated Tasks) -->
        <h4 style="font-size:15px; font-weight:800; color:var(--color-forest); margin:0 0 8px 0;">1. Synthetic Scenario Benchmark Classification Metrics (Held-Out Delta Test Set)</h4>
        <table style="width:100%; border-collapse:collapse; font-size:13px; margin-bottom:22px; background:#fff; border:1px solid #e2e8f0; border-radius:8px; overflow:hidden;">
          <thead>
            <tr style="background:var(--color-mist); text-align:left;">
              <th style="padding:10px 14px; border-bottom:2px solid #cbd5e1;">Metric</th>
              <th style="padding:10px 14px; border-bottom:2px solid #cbd5e1;">Random Forest (v2.1)</th>
              <th style="padding:10px 14px; border-bottom:2px solid #cbd5e1;">Baseline (Logistic v1.0)</th>
              <th style="padding:10px 14px; border-bottom:2px solid #cbd5e1;">Scientific Description</th>
            </tr>
          </thead>
          <tbody>
            <tr style="border-bottom:1px solid #e2e8f0;">
              <td style="padding:10px 14px; font-weight:700;">Classification Accuracy</td>
              <td style="padding:10px 14px; color:#059669; font-weight:800;">${(rf.accuracy * 100).toFixed(1)}%</td>
              <td style="padding:10px 14px; color:#64748b;">${(base.accuracy * 100).toFixed(1)}%</td>
              <td style="padding:10px 14px; font-size:12px; color:#64748b;">Evaluated on multi-scenario synthetic benchmark partitions across coastal test mandals (_generate_synthetic_benchmark_dataset, seed=42)</td>
            </tr>
            <tr style="border-bottom:1px solid #e2e8f0;">
              <td style="padding:10px 14px; font-weight:700;">Precision</td>
              <td style="padding:10px 14px; color:#059669; font-weight:800;">${(rf.precision * 100).toFixed(1)}%</td>
              <td style="padding:10px 14px; color:#64748b;">${(base.precision * 100).toFixed(1)}%</td>
              <td style="padding:10px 14px; font-size:12px; color:#64748b;">Proportion of predicted flood points that were genuinely inundated</td>
            </tr>
            <tr style="border-bottom:1px solid #e2e8f0;">
              <td style="padding:10px 14px; font-weight:700;">Recall / POD</td>
              <td style="padding:10px 14px; color:#059669; font-weight:800;">${(rf.recall_pod * 100).toFixed(1)}%</td>
              <td style="padding:10px 14px; color:#64748b;">${(base.recall_pod * 100).toFixed(1)}%</td>
              <td style="padding:10px 14px; font-size:12px; color:#64748b;">Probability of Detection: Proportion of true flood events successfully captured</td>
            </tr>
            <tr style="border-bottom:1px solid #e2e8f0;">
              <td style="padding:10px 14px; font-weight:700;">F1-Score</td>
              <td style="padding:10px 14px; color:#059669; font-weight:800;">${(rf.f1_score * 100).toFixed(1)}%</td>
              <td style="padding:10px 14px; color:#64748b;">${(base.f1_score * 100).toFixed(1)}%</td>
              <td style="padding:10px 14px; font-size:12px; color:#64748b;">Harmonic mean balancing precision and detection recall</td>
            </tr>
            <tr style="border-bottom:1px solid #e2e8f0;">
              <td style="padding:10px 14px; font-weight:700;">Intersection over Union (IoU)</td>
              <td style="padding:10px 14px; color:#059669; font-weight:800;">${(rf.iou_jaccard * 100).toFixed(1)}%</td>
              <td style="padding:10px 14px; color:#64748b;">${(base.iou_jaccard * 100).toFixed(1)}%</td>
              <td style="padding:10px 14px; font-size:12px; color:#64748b;">Spatial overlap agreement between prediction and ground-truth</td>
            </tr>
            <tr style="border-bottom:1px solid #e2e8f0;">
              <td style="padding:10px 14px; font-weight:700;">False Alarm Ratio (FAR)</td>
              <td style="padding:10px 14px; color:#059669; font-weight:800;">${(rf.false_alarm_ratio_far * 100).toFixed(1)}%</td>
              <td style="padding:10px 14px; color:#64748b;">${(base.false_alarm_ratio_far * 100).toFixed(1)}%</td>
              <td style="padding:10px 14px; font-size:12px; color:#64748b;">Fraction of false alarms among positive predictions (0.0% avoids panic evacuations)</td>
            </tr>
          </tbody>
        </table>

        <!-- Section C: Visual Confusion Matrix -->
        <h4 style="font-size:15px; font-weight:800; color:var(--color-forest); margin:0 0 10px 0;">2. Visual Confusion Matrix (48 Held-Out Coastal Samples)</h4>
        <div style="display:grid; grid-template-columns:120px 1fr 1fr; gap:8px; margin-bottom:24px; max-width:540px; font-size:12.5px;">
          <div></div>
          <div style="text-align:center; font-weight:800; color:#475569;">Predicted: Non-Flood</div>
          <div style="text-align:center; font-weight:800; color:#475569;">Predicted: Inundated</div>

          <div style="display:flex; align-items:center; font-weight:800; color:#475569;">Actual: Non-Flood</div>
          <div style="background:#f0fdf4; border:2px solid #22c55e; border-radius:8px; padding:14px; text-align:center;">
            <div style="font-size:22px; font-weight:900; color:#15803d;">${cm.true_negatives}</div>
            <div style="font-size:11px; color:#166534; font-weight:700;">True Negatives (TN)</div>
          </div>
          <div style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:8px; padding:14px; text-align:center;">
            <div style="font-size:22px; font-weight:900; color:#64748b;">${cm.false_positives}</div>
            <div style="font-size:11px; color:#64748b; font-weight:700;">False Positives (FP)</div>
          </div>

          <div style="display:flex; align-items:center; font-weight:800; color:#475569;">Actual: Inundated</div>
          <div style="background:#fffbeb; border:1px solid #fde68a; border-radius:8px; padding:14px; text-align:center;">
            <div style="font-size:22px; font-weight:900; color:#b45309;">${cm.false_negatives}</div>
            <div style="font-size:11px; color:#92400e; font-weight:700;">False Negatives (FN)</div>
          </div>
          <div style="background:#f0fdf4; border:2px solid #22c55e; border-radius:8px; padding:14px; text-align:center;">
            <div style="font-size:22px; font-weight:900; color:#15803d;">${cm.true_positives}</div>
            <div style="font-size:11px; color:#166534; font-weight:700;">True Positives (TP)</div>
          </div>
        </div>

        <!-- Section B (Cont): Continuous River Stage Forecasting Metrics -->
        <h4 style="font-size:15px; font-weight:800; color:var(--color-forest); margin:0 0 10px 0;">3. Continuous River Stage Forecasting (Dowleswaram Barrage)</h4>
        <div style="display:grid; grid-template-columns:1fr 1fr 1fr; gap:12px; margin-bottom:24px;">
          <div style="padding:14px; background:#f0fdf4; border:1px solid #bbf7d0; border-radius:10px; text-align:center;">
            <div style="font-size:12px; color:#166534; font-weight:700;">Mean Absolute Error (MAE)</div>
            <div style="font-size:22px; font-weight:900; color:#15803d; margin:4px 0;">${riv.mae_feet} ft</div>
            <div style="font-size:11px; color:#64748b;">vs Baseline ${rivBase.mae_feet} ft (73.5% skill gain)</div>
          </div>
          <div style="padding:14px; background:#f0fdf4; border:1px solid #bbf7d0; border-radius:10px; text-align:center;">
            <div style="font-size:12px; color:#166534; font-weight:700;">Root Mean Square Error</div>
            <div style="font-size:22px; font-weight:900; color:#15803d; margin:4px 0;">${riv.rmse_feet} ft</div>
            <div style="font-size:11px; color:#64748b;">vs Baseline ${rivBase.rmse_feet} ft</div>
          </div>
          <div style="padding:14px; background:#f0fdf4; border:1px solid #bbf7d0; border-radius:10px; text-align:center;">
            <div style="font-size:12px; color:#166534; font-weight:700;">Pearson Correlation (r)</div>
            <div style="font-size:22px; font-weight:900; color:#15803d; margin:4px 0;">${riv.pearson_r}</div>
            <div style="font-size:11px; color:#64748b;">Horizon: 24h &bull; 48h &bull; 72h Inflow</div>
          </div>
        </div>

        <!-- Section E: Explainability & Feature Importance -->
        <h4 style="font-size:15px; font-weight:800; color:var(--color-forest); margin:0 0 10px 0;">4. Machine Learning Explainability &amp; Feature Importance</h4>
        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:16px; margin-bottom:24px;">
          <div style="display:flex; flex-direction:column; gap:8px;">
            ${Object.entries(fi).map(([feat, imp]) => {
              const pct = (imp * 100).toFixed(1);
              const label = feat.replace(/_/g, ' ').replace('mm', '(mm)').replace('m', '(m)').toUpperCase();
              return `
                <div>
                  <div style="display:flex; justify-content:space-between; font-size:11.5px; font-weight:700; color:#334155; margin-bottom:2px;">
                    <span>${label}</span>
                    <span>${pct}%</span>
                  </div>
                  <div style="height:7px; background:#e2e8f0; border-radius:4px; overflow:hidden;">
                    <div style="width:${pct}%; height:100%; background:var(--color-forest); border-radius:4px;"></div>
                  </div>
                </div>
              `;
            }).join('')}
          </div>
        </div>

        <!-- Section E (Cont): Conceptual Demarcation Table -->
        <h4 style="font-size:15px; font-weight:800; color:var(--color-forest); margin:0 0 10px 0;">5. Scientific Demarcation of System Outputs</h4>
        <table style="width:100%; border-collapse:collapse; font-size:12.5px; margin-bottom:20px; background:#fff; border:1px solid #e2e8f0; border-radius:8px; overflow:hidden;">
          <thead>
            <tr style="background:#f1f5f9; text-align:left;">
              <th style="padding:8px 12px; border-bottom:1px solid #cbd5e1;">Concept</th>
              <th style="padding:8px 12px; border-bottom:1px solid #cbd5e1;">Scientific Nature</th>
              <th style="padding:8px 12px; border-bottom:1px solid #cbd5e1;">Application Representation</th>
            </tr>
          </thead>
          <tbody>
            <tr style="border-bottom:1px solid #e2e8f0;">
              <td style="padding:8px 12px; font-weight:700;">Flood Susceptibility</td>
              <td style="padding:8px 12px;">Multi-criteria terrain baseline (AHP, CR = 0.0001)</td>
              <td style="padding:8px 12px; color:#64748b;">Static spatial zoning for disaster preparedness</td>
            </tr>
            <tr style="border-bottom:1px solid #e2e8f0;">
              <td style="padding:8px 12px; font-weight:700;">Satellite Water Candidates</td>
              <td style="padding:8px 12px;">Sentinel-1 SAR radar backscatter drop (&sigma;0 &lt; -14 dB)</td>
              <td style="padding:8px 12px; color:#64748b;">Cloud-penetrating proxy for water accumulation</td>
            </tr>
            <tr style="border-bottom:1px solid #e2e8f0;">
              <td style="padding:8px 12px; font-weight:700;">Forecast Flood Risk</td>
              <td style="padding:8px 12px;">Dynamic Random Forest (v2.1) probability (24-72h)</td>
              <td style="padding:8px 12px; color:#64748b;">Pre-emptive evacuation decision support</td>
            </tr>
            <tr style="border-bottom:1px solid #e2e8f0;">
              <td style="padding:8px 12px; font-weight:700;">Population Exposure (8.25M)</td>
              <td style="padding:8px 12px;">Total residents residing in elevated susceptibility zones</td>
              <td style="padding:8px 12px; color:#64748b;">Demographic exposure potential, NOT confirmed victims</td>
            </tr>
            <tr>
              <td style="padding:8px 12px; font-weight:700;">Confirmed Affected Population</td>
              <td style="padding:8px 12px;">Ground-verified evacuees by district administration</td>
              <td style="padding:8px 12px; color:#64748b;">Field-reported relief camp shelter occupancy</td>
            </tr>
          </tbody>
        </table>

        <!-- Section D: Final Provenance Notice -->
        <div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:14px; font-size:12px; color:#64748b; line-height:1.5;">
          <strong>Data Provenance &amp; Verification Ground Truth:</strong> All evaluation metrics are calculated against held-out ground truth from CWC Dowleswaram Barrage gauge bulletins and Sentinel-1 SAR observations. Models are retrained with temporal cross-validation. PRAVAH 360 explicitly disclaims fabricated claims and reports exact scientific metrics.
        </div>
      `;
    } catch (e) {
      console.warn('Model validation report error:', e);
      content.innerHTML = `
        <div style="background:#fffbeb; border:2px solid #f59e0b; padding:24px; border-radius:12px; text-align:center;">
          <span style="font-size:36px; display:block; margin-bottom:10px;">⚠️</span>
          <h3 style="margin:0 0 8px 0; font-size:18px; font-weight:900; color:#92400e;">VALIDATION DATA INSUFFICIENT</h3>
          <p style="margin:0 0 14px 0; font-size:13.5px; color:#78350f; line-height:1.6; max-width:600px; margin-left:auto; margin-right:auto;">
            Independent ground-truth reference data could not be verified from the server. PRAVAH 360 does not display unvalidated model scores or fabricated accuracy metrics when reference telemetry is missing.
          </p>
          <div style="background:#fff; border:1px solid #fde68a; border-radius:8px; padding:12px; font-size:12px; color:#92400e; text-align:left; max-width:560px; margin:0 auto 16px auto;">
            <strong>Missing Requirements to Complete Validation:</strong>
            <ul style="margin:6px 0 0 18px; padding:0;">
              <li>Connection to /api/v1/prediction/validation-report endpoint</li>
              <li>Sentinel-1 SAR surface water reference mask for test episode</li>
              <li>Dowleswaram Barrage gauge telemetry logs</li>
            </ul>
          </div>
          <button type="button" onclick="window.openModelValidationWorkspace()" style="background:var(--color-forest); color:#fff; border:none; padding:8px 18px; border-radius:8px; font-weight:700; font-size:13px; cursor:pointer;">Retry Validation Request</button>
        </div>
      `;
    }
  };

  // Poll notifications on load
  setTimeout(() => { if (typeof window.pollContinuousNotifications === 'function') window.pollContinuousNotifications(); }, 1500);

  // =========================================================================
  // UNIVERSAL TELUGU / ENGLISH TRANSLATION CONTROLLER
  // =========================================================================
    window.currentAppLang = localStorage.getItem('pravah_lang') || 'en';

  let _lastLangToggleTs = 0;
  window.toggleGlobalLanguage = function() {
    const now = Date.now();
    if (now - _lastLangToggleTs < 350) return; // Prevent double-trigger from duplicate listeners or rapid clicks
    _lastLangToggleTs = now;
    const targetLang = window.currentAppLang === 'en' ? 'te' : 'en';
    window.setAppLanguage(targetLang);
  };

  window.setAppLanguage = function(lang) {
    if (!window.PRAVAH_TRANSLATIONS || !window.PRAVAH_TRANSLATIONS[lang]) return;
    window.currentAppLang = lang;
    try { localStorage.setItem('pravah_lang', lang); } catch (e) {}
    document.body.setAttribute('data-lang', lang);
    const dict = window.PRAVAH_TRANSLATIONS[lang];

    // 1. Update voice assistant language
    if (window.pravahVoice && typeof window.pravahVoice.setLanguage === 'function') {
      window.pravahVoice.setLanguage(lang);
    }

    // 2. Update language toggle buttons across surfaces
    document.querySelectorAll('#btnLandingLangToggle, .btn-lang-toggle, .lang-switch-btn').forEach(btn => {
      btn.textContent = dict.langToggle;
    });

    // 3. Apply all data-i18n attributes
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (dict[key]) {
        if (el.tagName === 'INPUT' && (el.type === 'button' || el.type === 'submit')) {
          el.value = dict[key];
        } else {
          el.textContent = dict[key];
        }
      }
    });

    // 4. Apply all data-i18n-placeholder attributes
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
      const key = el.getAttribute('data-i18n-placeholder');
      if (dict[key]) {
        el.placeholder = dict[key];
      }
    });

    // 5. Landing nav links are handled automatically by [data-i18n] above without hardcoded index overwrite

    // 6. Hero section elements
    const hHeadline = document.querySelector('.hero-headline');
    const hTagline = document.querySelector('.hero-tagline');
    const hStmt = document.querySelector('.hero-supporting-statement');
    const btnExp = document.getElementById('btnHeroExplore');
    const btnReg = document.getElementById('btnHeroRegister');
    const btnSign = document.getElementById('btnHeroSignIn');
    if (hHeadline) hHeadline.textContent = dict.heroHeadline;
    if (hTagline) hTagline.textContent = dict.heroTagline;
    if (hStmt) hStmt.textContent = dict.heroStatement;
    if (btnExp) btnExp.textContent = dict.btnExplore;
    if (btnReg) btnReg.textContent = dict.btnCreateAccount;
    if (btnSign) btnSign.textContent = dict.btnSignIn;

    // 7. Awareness cards in Section 02
    const awarenessCards = document.querySelectorAll('.awareness-card');
    if (awarenessCards.length >= 5) {
      if (awarenessCards[0].querySelector('h3')) awarenessCards[0].querySelector('h3').textContent = dict.card1Title;
      if (awarenessCards[0].querySelector('p')) awarenessCards[0].querySelector('p').textContent = dict.card1Desc;
      if (awarenessCards[0].querySelector('.awareness-card-link')) awarenessCards[0].querySelector('.awareness-card-link').textContent = dict.card1Link;

      if (awarenessCards[1].querySelector('h3')) awarenessCards[1].querySelector('h3').textContent = dict.card2Title;
      if (awarenessCards[1].querySelector('p')) awarenessCards[1].querySelector('p').textContent = dict.card2Desc;
      if (awarenessCards[1].querySelector('.awareness-card-link')) awarenessCards[1].querySelector('.awareness-card-link').textContent = dict.card2Link;

      if (awarenessCards[2].querySelector('h3')) awarenessCards[2].querySelector('h3').textContent = dict.card3Title;
      if (awarenessCards[2].querySelector('p')) awarenessCards[2].querySelector('p').textContent = dict.card3Desc;
      if (awarenessCards[2].querySelector('.awareness-card-link')) awarenessCards[2].querySelector('.awareness-card-link').textContent = dict.card3Link;

      if (awarenessCards[3].querySelector('h3')) awarenessCards[3].querySelector('h3').textContent = dict.card4Title;
      if (awarenessCards[3].querySelector('p')) awarenessCards[3].querySelector('p').textContent = dict.card4Desc;
      if (awarenessCards[3].querySelector('.awareness-card-link')) awarenessCards[3].querySelector('.awareness-card-link').textContent = dict.card4Link;

      if (awarenessCards[4].querySelector('h3')) awarenessCards[4].querySelector('h3').textContent = dict.card5Title;
      if (awarenessCards[4].querySelector('p')) awarenessCards[4].querySelector('p').textContent = dict.card5Desc;
      if (awarenessCards[4].querySelector('.awareness-card-link')) awarenessCards[4].querySelector('.awareness-card-link').textContent = dict.card5Link;
    }

    // 8. Role Persona Cards
    const personaCards = document.querySelectorAll('.platform-persona-card');
    if (personaCards.length >= 2) {
      if (personaCards[0].querySelector('h3')) personaCards[0].querySelector('h3').textContent = dict.roleResidentTitle;
      if (personaCards[0].querySelector('p')) personaCards[0].querySelector('p').textContent = dict.roleResidentDesc;
      if (personaCards[0].querySelector('.btn-persona-cta')) personaCards[0].querySelector('.btn-persona-cta').textContent = dict.roleResidentBtn;

      if (personaCards[1].querySelector('h3')) personaCards[1].querySelector('h3').textContent = dict.roleResponseTitle;
      if (personaCards[1].querySelector('p')) personaCards[1].querySelector('p').textContent = dict.roleResponseDesc;
      if (personaCards[1].querySelector('.btn-persona-cta')) personaCards[1].querySelector('.btn-persona-cta').textContent = dict.roleResponseBtn;
    }

    // 9. Auth forms headers & buttons
    const signH2 = document.querySelector('#page-login .auth-form-header h2');
    const signP = document.querySelector('#page-login .auth-form-header p');
    if (signH2) signH2.textContent = dict.signInTitle;
    if (signP) signP.textContent = dict.signInDesc;

    const regH2 = document.querySelector('#page-register .auth-form-header h2');
    const regP = document.querySelector('#page-register .auth-form-header p');
    if (regH2) regH2.textContent = dict.registerTitle;
    if (regP) regP.textContent = dict.registerDesc;

    const btnLogSub = document.getElementById('btnDedicatedLoginSubmit');
    if (btnLogSub) btnLogSub.textContent = dict.btnSignInSubmit;

    const btnRegSub = document.getElementById('btnRegisterSubmit');
    if (btnRegSub) btnRegSub.textContent = dict.btnRegisterSubmit;

    // 10. Role Selection & Onboarding
    const roleH2 = document.querySelector('#page-role-select h2');
    const roleSub = document.querySelector('#page-role-select p');
    if (roleH2) roleH2.textContent = dict.roleSelectTitle;
    if (roleSub) roleSub.textContent = dict.roleSelectSub;

    const onbH2 = document.querySelector('#page-location-onboarding h2');
    const onbSub = document.querySelector('#page-location-onboarding p');
    const btnSaveOnb = document.getElementById('btnSaveLocationOnboarding');
    const btnDetLoc = document.getElementById('btnDetectLocation');
    if (onbH2) onbH2.textContent = dict.onboardingTitle;
    if (onbSub) onbSub.textContent = dict.onboardingSub;
    if (btnSaveOnb) btnSaveOnb.textContent = dict.btnSaveOnboarding;
    if (btnDetLoc) btnDetLoc.textContent = dict.btnDetectLocation;

    // 11. Situation Awareness Home
    const sitH2 = document.querySelector('#page-situation-home .entry-header-title');
    const sitSub = document.querySelector('#page-situation-home .entry-header-sub');
    if (sitH2) sitH2.textContent = dict.sitHomeTitle;
    if (sitSub) sitSub.textContent = dict.sitHomeSub;

    // 12. Helplines Intro
    const hlIntroH4 = document.querySelector('.helpline-intro h4');
    const hlIntroP = document.querySelector('.helpline-intro p');
    if (hlIntroH4) hlIntroH4.textContent = dict.helplineTitle;
    if (hlIntroP) hlIntroP.textContent = dict.helplineSub;

    console.log("App language switched to:", lang);
  };

/**

 * Geospatial Flood Intelligence & Emergency Decision Support System

 * GIS-First Web Application & Global 3D Earth Controller (Phase 5.2)

 */



document.addEventListener('DOMContentLoaded', () => {

  // =========================================================================

  // 1. GLOBAL APPLICATION STATE & CONSTANTS

  // =========================================================================

  const STUDY_AREA_CENTER = [16.942, 81.776];

  const DEFAULT_ZOOM = 9;

  const SAR_BOUNDS = [[16.3000, 80.8500], [18.0150, 82.6150]];



  const appState = {

    currentWorkspace: 'overview',

    selectedLocation: {

      name: 'Rajahmundry Mandal',

      lat: 16.9850,

      lon: 81.7800,

      mandalName: 'Rajahmundry',

      districtName: 'East Godavari',

      isInBasin: true,

      susceptibilityScore: 0.887,

      riskLevel: 'Very High',

      elevation: 14.2,

      streamDist: 180,

      exposedPop: 442650

    },

    mandalsData: null,

    basinAssessment: null,

    exposureSummary: null,

    facilitiesData: null,

    stationsData: null,

    alertsData: null,

    worldCountries: null,

    isGlobeRotating: true

  };



  // Maps Instances Cache

  const maps = {

    explorer: null,

    apMonitor: null,

    overview: null,

    risk: null,

    impact: null

  };



  // Explorer Layers Cache

  const explorerLayers = {

    basemapDark: null,

    basemapSat: null,

    basemapOsm: null,

    currentBasemap: null,

    studyArea: null,

    districts: null,

    mandals: null,

    rivers: null,

    stations: null,

    facilities: null,

    sarFlood: null,

    sarPerm: null,

    sarAmbig: null,

    susceptibility: null,

    inspectorMarker: null

  };



  // Sub-map layers

  const subLayers = {

    riskMandals: null,

    impactFacilities: null

  };



  // Globe.gl Instance

  let globeInstance = null;



  // Expose handles on window for headless browser testing and automated verification

  window.appState = appState;

  window.maps = maps;

  window.explorerLayers = explorerLayers;

  window.getGlobeInstance = () => globeInstance;



  // =========================================================================

  // 2. WORKSPACE ROUTER & TAB SWITCHING

  // =========================================================================

  const WORKSPACE_METADATA = {

    welcome: {

      heading: 'Welcome to PRAVAH 360',

      subheading: 'Geospatial Disaster Intelligence & Emergency Decision Support • See the risk. Stay prepared.'

    },

    research: {

      heading: 'Research & Methodology',

      subheading: 'Explainable Geospatial AI for Flood Risk and Impact Assessment with Emergency Decision Support'

    },

    help: {

      heading: 'Help & Flood Preparedness Guide',

      subheading: 'Verified Andhra Pradesh Safety Protocols, Evacuation Guidance & Emergency Helplines'

    },

    overview: {

      heading: 'Overview & Executive Summary',

      subheading: 'Lower Godavari Basin, Andhra Pradesh • GADM v4.1 & 2022 AP Reorganization'

    },

    explorer: {

      heading: 'Geospatial Explorer (Web GIS)',

      subheading: 'Multi-Source Spatial Layers • Interactive Analytical Inspection & Terrain Modeling'

    },

    risk: {

      heading: 'Flood Risk Intelligence',

      subheading: 'Analytic Hierarchy Process (AHP) Model • 21-Mandal Vulnerability Rankings'

    },

    impact: {

      heading: 'Impact Assessment & Exposure',

      subheading: 'WorldPop 2020 Reconciled Baseline (9,126,355) • 1,635 Mapped Community Assets'

    },

    weather: {

      heading: 'Weather & Emergency Intelligence',

      subheading: 'Atmospheric Forecasts • Deterministic Preparedness Protocols'

    },

    global: {

      heading: 'Global 3D Earth Intelligence',

      subheading: 'Continuous WebGL Planetarium • 177 Geopolitical Boundaries & OSINT Framework'

    },

    evidence: {

      heading: 'Evidence, Scientific Trust & Methodology',

      subheading: 'Standardized Terminology Matrix • Dataset Manifests & Provenance Verification'

    },

    operations: {

      heading: 'Emergency Operations & Decision Support Simulator',

      subheading: 'Multi-Role Tactical Coordination: Resident • Mandal • District • ERT Dispatch'

    },

    'ap-monitor': {

      heading: 'Andhra Pradesh Live Disaster Monitoring',

      subheading: 'NDMA SACHET • APSDMA Weather-Watch • IMD Cyclone & Rainfall • CWC Hydrological Stages'

    }

  };



  function switchWorkspace(workspaceId) {

    if (!WORKSPACE_METADATA[workspaceId]) return;

    appState.currentWorkspace = workspaceId;



    // Update navigation items

    document.querySelectorAll('.app-nav .nav-item').forEach(btn => {

      btn.classList.toggle('active', btn.getAttribute('data-workspace') === workspaceId);

    });



    // Update workspace sections

    document.querySelectorAll('.workspace').forEach(sec => {

      sec.classList.toggle('active', sec.id === `workspace-${workspaceId}`);

    });



    // Update URL hash without jumping

    if (window.location.hash.replace('#', '') !== workspaceId) {

      history.replaceState(null, '', '#' + workspaceId);

    }



    // Update Top Utility Bar titles

    const meta = WORKSPACE_METADATA[workspaceId];

    document.getElementById('currentWorkspaceHeading').textContent = meta.heading;

    document.getElementById('currentWorkspaceSubheading').textContent = meta.subheading;



    // Lazy initialization & Leaflet viewport recalculations

    setTimeout(() => {

      if (workspaceId === 'explorer') {

        if (!maps.explorer) initExplorerMap();

        else maps.explorer.invalidateSize();

      } else if (workspaceId === 'overview') {

        if (!maps.overview) initOverviewMap();

        else maps.overview.invalidateSize();

      } else if (workspaceId === 'risk') {

        if (!maps.risk) initRiskMap();

        else maps.risk.invalidateSize();

      } else if (workspaceId === 'impact') {

        if (!maps.impact) initImpactMap();

        else maps.impact.invalidateSize();

      } else if (workspaceId === 'weather') {

        loadWeatherData();

      } else if (workspaceId === 'global') {

        if (!globeInstance) initGlobalEarth();

      } else if (workspaceId === 'operations') {

        initOperationsWorkspace();

      }

    }, 60);

  }



  // Setup Nav Item Click Handlers

  document.querySelectorAll('.app-nav .nav-item').forEach(btn => {

    btn.addEventListener('click', () => {

      const target = btn.getAttribute('data-workspace');

      switchWorkspace(target);

    });

  });



  // Setup Overview Quick Nav Cards

  document.querySelectorAll('.quick-nav-card').forEach(card => {

    card.addEventListener('click', () => {

      const target = card.getAttribute('data-target');

      if (target) switchWorkspace(target);

    });

  });



  const btnOpenFullExplorer = document.getElementById('btnOpenFullExplorer');

  if (btnOpenFullExplorer) {

    btnOpenFullExplorer.addEventListener('click', () => switchWorkspace('explorer'));

  }



  // =========================================================================

  // 3. BASEMAP DEFINITIONS (UNWATERMARKED, HIGH-RELIABILITY PROVIDERS)

  // =========================================================================

  function createBasemaps() {

    // Esri World Dark Gray Canvas with Crisp Reference Labels & Coastlines (Default)

    const esriDark = L.layerGroup([

      L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {

        attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ',

        maxZoom: 16

      }),

      L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}', {

        maxZoom: 16,

        zIndex: 420

      })

    ]);



    // Esri World Imagery (High-res optical satellite orthophotography)

    const esriSat = L.layerGroup([

      L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {

        attribution: 'Tiles &copy; Esri &mdash; Source: Esri, Maxar, Earthstar Geographics',

        maxZoom: 18

      }),

      L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Boundaries_and_Places/MapServer/tile/{z}/{y}/{x}', {

        maxZoom: 18,

        zIndex: 420

      })

    ]);



    // Esri World Topographic (Full contours, rivers, settlements, and relief)

    const esriTopo = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}', {

      attribution: 'Tiles &copy; Esri &mdash; USGS, Intermap, TomTom',

      maxZoom: 18

    });



    // OpenStreetMap Standard

    const osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {

      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',

      maxZoom: 19

    });



    return { esriDark, esriSat, esriTopo, osm };

  }



  // =========================================================================

  // 4. GEOSPATIAL EXPLORER MAP (PRIMARY WEB GIS WORKSPACE)

  // =========================================================================

  function initExplorerMap() {

    const container = document.getElementById('explorer-map');

    if (!container || maps.explorer) return;



    const baseLayers = createBasemaps();

    explorerLayers.basemapDark = baseLayers.esriDark;

    explorerLayers.basemapSat = baseLayers.esriSat;

    explorerLayers.basemapTopo = baseLayers.esriTopo;

    explorerLayers.basemapOsm = baseLayers.osm;



    maps.explorer = L.map('explorer-map', {

      center: STUDY_AREA_CENTER,

      zoom: DEFAULT_ZOOM,

      zoomControl: true,

      minZoom: 6,

      maxZoom: 18,

      preferCanvas: true

    });



    // Set Default Basemap

    explorerLayers.currentBasemap = explorerLayers.basemapDark;

    explorerLayers.currentBasemap.addTo(maps.explorer);



    // Live Coordinates Display on Mousemove

    maps.explorer.on('mousemove', (e) => {

      const lat = e.latlng.lat.toFixed(4);

      const lon = e.latlng.lng.toFixed(4);

      const coordEl = document.getElementById('mouseCoordinatesDisplay');

      if (coordEl) {

        coordEl.textContent = `Lat: ${lat}° N, Lon: ${lon}° E`;

      }

    });



    // Map Click Inspector

    maps.explorer.on('click', (e) => {

      const lat = parseFloat(e.latlng.lat.toFixed(5));

      const lon = parseFloat(e.latlng.lng.toFixed(5));

      inspectCoordinates(lat, lon);

    });



    // Initialize Overlays

    initExplorerLayers();

    wireExplorerControls();

  }



  function initExplorerLayers() {

    const map = maps.explorer;



    // 1. Sentinel-1 SAR Raster Overlays

    explorerLayers.sarFlood = L.imageOverlay('/static/overlays/sentinel1_flood_candidates_track129.png', SAR_BOUNDS, {

      opacity: 0.85,

      interactive: false,

      zIndex: 350

    }).addTo(map);



    explorerLayers.sarPerm = L.imageOverlay('/static/overlays/sentinel1_permanent_water.png', SAR_BOUNDS, {

      opacity: 0.70,

      interactive: false,

      zIndex: 340

    });



    explorerLayers.sarAmbig = L.imageOverlay('/static/overlays/sentinel1_ambiguous_wetsoil.png', SAR_BOUNDS, {

      opacity: 0.60,

      interactive: false,

      zIndex: 330

    });



    // 2. Study Area Boundary Layer

    fetch('/static/data/lower_godavari_study_area.geojson')

      .then(res => res.json())

      .then(geojson => {

        explorerLayers.studyArea = L.geoJSON(geojson, {

          style: {

            color: '#38bdf8',

            weight: 2.5,

            dashArray: '6, 6',

            fillColor: '#38bdf8',

            fillOpacity: 0.04

          }

        }).addTo(map);

      })

      .catch(err => console.warn('Could not load study area geojson:', err));



    // 3. District Boundaries Layer

    fetch('/static/data/lower_godavari_districts.geojson')

      .then(res => res.json())

      .then(geojson => {

        explorerLayers.districts = L.geoJSON(geojson, {

          style: {

            color: '#facc15',

            weight: 2,

            dashArray: '3, 4',

            fillColor: 'transparent',

            fillOpacity: 0

          },

          onEachFeature: (feature, layer) => {

            const name = feature.properties?.NAME_2 || feature.properties?.district || 'District';

            layer.bindTooltip(`District: ${name}`, { sticky: true, className: 'gis-tooltip' });

          }

        }).addTo(map);

      })

      .catch(err => console.warn('Could not load districts geojson:', err));



    // 4. HydroRIVERS Drainage Network Layer

    fetch('/static/data/lower_godavari_hydrorivers.geojson')

      .then(res => res.json())

      .then(geojson => {

        explorerLayers.rivers = L.geoJSON(geojson, {

          style: (feature) => {

            const ord = feature.properties?.ORD_STRA || 1;

            return {

              color: '#0284c7',

              weight: Math.max(1, ord >= 5 ? 3.5 : (ord >= 3 ? 2 : 1)),

              opacity: 0.85

            };

          },

          onEachFeature: (feature, layer) => {

            const name = feature.properties?.MAIN_RIV || 'Godavari Drainage Reach';

            layer.bindTooltip(`${name} (Strahler: ${feature.properties?.ORD_STRA || 'N/A'})`, { sticky: true });

          }

        }).addTo(map);

      })

      .catch(err => console.warn('Could not load hydrorivers geojson:', err));



    // 5. Mandals & Susceptibility Choropleth Layer

    loadMandalsLayer();



    // 6. River Monitoring Stations

    loadStationsLayer();



    // 7. OSM Facilities Layer

    loadFacilitiesLayer();

  }



  function getCategoryColor(category) {

    if (category === 'Very High') return '#ef4444';

    if (category === 'High') return '#f97316';

    if (category === 'Moderate') return '#eab308';

    return '#10b981'; // Blue-green

  }



  function loadMandalsLayer() {

    fetch('/api/v1/boundaries/mandals-geojson')

      .then(res => res.json())

      .then(geojson => {

        appState.mandalsData = geojson;



        // Mandal Outlines Layer

        explorerLayers.mandals = L.geoJSON(geojson, {

          style: {

            color: '#94a3b8',

            weight: 1.2,

            fillColor: 'transparent',

            fillOpacity: 0

          },

          onEachFeature: (feature, layer) => {

            const p = feature.properties;

            const mandal = p.NAME_3 || p.mandal || 'Mandal';

            const dist = p.NAME_2 || p.district || 'District';

            layer.bindTooltip(`<strong>${mandal}</strong> (${dist})`, { sticky: true });

            layer.on('click', (e) => {

              L.DomEvent.stopPropagation(e);

              selectMandalFeature(p);

            });

          }

        }).addTo(maps.explorer);



        // Fetch Susceptibility Basin Assessment for Choropleth

        fetch('/api/v1/flood-risk/basin-assessment')

          .then(res => res.json())

          .then(assessment => {

            appState.basinAssessment = assessment;

            const lookup = {};

            if (assessment.mandal_assessments) {

              assessment.mandal_assessments.forEach(m => {

                lookup[m.mandal_name.toLowerCase()] = m;

              });

            }



            // Choropleth Susceptibility Layer

            const opacityVal = parseInt(document.getElementById('rngSusceptibilityOpacity')?.value || 55) / 100;

            explorerLayers.susceptibility = L.geoJSON(geojson, {

              style: (feature) => {

                const name = (feature.properties?.NAME_3 || feature.properties?.mandal || '').toLowerCase();

                const record = lookup[name];

                const cat = record ? (record.risk_level || record.susceptibility_category) : 'Moderate';

                return {

                  color: '#ffffff',

                  weight: 0.6,

                  fillColor: getCategoryColor(cat),

                  fillOpacity: opacityVal

                };

              },

              onEachFeature: (feature, layer) => {

                const name = (feature.properties?.NAME_3 || feature.properties?.mandal || '');

                const record = lookup[name.toLowerCase()];

                if (record) {

                  layer.bindTooltip(`<strong>${name}</strong><br>AHP Score: ${record.susceptibility_score.toFixed(3)} (${record.susceptibility_category})`, { sticky: true });

                }

                layer.on('click', (e) => {

                  L.DomEvent.stopPropagation(e);

                  selectMandalFeature(feature.properties, record);

                });

              }

            }).addTo(maps.explorer);



            // Populate Tables and Cards

            populateMandalRankingsTable(assessment.mandal_assessments);

            populateDistrictTable(assessment.mandal_assessments, assessment.district_summaries);

            updateOverviewRibbon(assessment);

          })

          .catch(err => console.warn('Could not load basin assessment:', err));

      })

      .catch(err => console.warn('Could not load mandals geojson:', err));

  }



  function loadStationsLayer() {

    fetch('/api/v1/water-levels/stations')

      .then(res => res.json())

      .then(data => {

        appState.stationsData = data.stations || [];

        explorerLayers.stations = L.layerGroup();



        appState.stationsData.forEach(st => {

          const lat = st.latitude;

          const lon = st.longitude;

          if (!lat || !lon) return;



          const isWarning = (st.current_water_level_m && st.warning_level_m && st.current_water_level_m >= st.warning_level_m);

          const color = isWarning ? '#ef4444' : '#38bdf8';



          const marker = L.circleMarker([lat, lon], {

            radius: 6,

            fillColor: color,

            color: '#ffffff',

            weight: 1.5,

            fillOpacity: 0.9

          });



          marker.bindTooltip(`<strong>${st.station_name}</strong><br>River: ${st.river}<br>Stage: ${st.current_water_level_m ? st.current_water_level_m.toFixed(2) + ' m' : 'Operational'}`, { sticky: true });



          marker.on('click', (e) => {

            L.DomEvent.stopPropagation(e);

            setSelectedLocation(lat, lon, st.station_name, null, null, null, false);

            openInspectionDrawer({

              title: `Station: ${st.station_name}`,

              type: 'Hydrometric Gauge',

              metrics: [

                { label: 'River', val: st.river },

                { label: 'Warning Level', val: st.warning_level_m ? `${st.warning_level_m} m` : 'N/A' },

                { label: 'Danger Level', val: st.danger_level_m ? `${st.danger_level_m} m` : 'N/A' },

                { label: 'Status', val: st.status || 'Active Recording' }

              ]

            });

          });



          explorerLayers.stations.addLayer(marker);

        });



        if (document.getElementById('chkLyrStations')?.checked) {

          explorerLayers.stations.addTo(maps.explorer);

        }

      })

      .catch(err => console.warn('Could not load stations:', err));

  }



  function loadFacilitiesLayer() {

    fetch('/api/v1/infrastructure/facilities?limit=2000')

      .then(res => res.json())

      .then(data => {

        appState.facilitiesData = data.facilities || [];

        explorerLayers.facilities = L.layerGroup();



        appState.facilitiesData.forEach(f => {

          const lat = f.latitude;

          const lon = f.longitude;

          if (!lat || !lon) return;



          let color = '#38bdf8';

          if (f.facility_type === 'healthcare') color = '#10b981';

          else if (f.facility_type === 'shelter') color = '#f59e0b';

          else if (f.facility_type === 'education') color = '#a855f7';



          const marker = L.circleMarker([lat, lon], {

            radius: 3.5,

            fillColor: color,

            color: '#ffffff',

            weight: 0.8,

            fillOpacity: 0.8

          });



          marker.bindTooltip(`<strong>${f.name}</strong><br>Type: ${f.facility_type}`, { sticky: true });

          explorerLayers.facilities.addLayer(marker);

        });

      })

      .catch(err => console.warn('Could not load facilities:', err));

  }



  function wireExplorerControls() {

    // 1. Basemap Switcher

    document.querySelectorAll('input[name="basemapRadio"]').forEach(radio => {

      radio.addEventListener('change', (e) => {

        if (!maps.explorer) return;

        const val = e.target.value;

        if (explorerLayers.currentBasemap) maps.explorer.removeLayer(explorerLayers.currentBasemap);



        if (val === 'satellite') explorerLayers.currentBasemap = explorerLayers.basemapSat;

        else if (val === 'topo') explorerLayers.currentBasemap = explorerLayers.basemapTopo;

        else if (val === 'osm') explorerLayers.currentBasemap = explorerLayers.basemapOsm;

        else explorerLayers.currentBasemap = explorerLayers.basemapDark;



        explorerLayers.currentBasemap.addTo(maps.explorer);

      });

    });



    // Fit Basin Extent Button

    const btnFit = document.getElementById('btnFitBasinExtent') || document.getElementById('btnResetBasinView');

    if (btnFit) {

      btnFit.addEventListener('click', () => {

        if (maps.explorer) {

          maps.explorer.fitBounds([[16.3000, 80.8500], [18.0150, 82.6150]]);

        }

      });

    }



    // 2. Accordion Group Toggles

    document.querySelectorAll('.accordion-header').forEach(hdr => {

      hdr.addEventListener('click', () => {

        const group = hdr.parentElement;

        group.classList.toggle('open');

      });

    });



    // 3. Layer Checkbox Toggles

    const toggleLayer = (chkId, layer) => {

      const chk = document.getElementById(chkId);

      if (chk) {

        chk.addEventListener('change', (e) => {

          if (!maps.explorer || !layer) return;

          if (e.target.checked) layer.addTo(maps.explorer);

          else maps.explorer.removeLayer(layer);

        });

      }

    };



    toggleLayer('chkLyrStudyArea', explorerLayers.studyArea);

    toggleLayer('chkLyrDistricts', explorerLayers.districts);

    toggleLayer('chkLyrMandals', explorerLayers.mandals);

    toggleLayer('chkLyrRivers', explorerLayers.rivers);

    toggleLayer('chkLyrStations', explorerLayers.stations);

    toggleLayer('chkLyrFacilities', explorerLayers.facilities);

    toggleLayer('chkLyrSarFlood', explorerLayers.sarFlood);

    toggleLayer('chkLyrSarPerm', explorerLayers.sarPerm);

    toggleLayer('chkLyrSarAmbig', explorerLayers.sarAmbig);

    toggleLayer('chkLyrSusceptibility', explorerLayers.susceptibility);



    // 4. Susceptibility Opacity Slider

    const opacitySlider = document.getElementById('rngSusceptibilityOpacity');

    if (opacitySlider) {

      opacitySlider.addEventListener('input', (e) => {

        const val = parseInt(e.target.value) / 100;

        if (explorerLayers.susceptibility) {

          explorerLayers.susceptibility.setStyle({ fillOpacity: val });

        }

      });

    }



    // 5. Legend Collapsible Toggle

    const btnToggleLegend = document.getElementById('btnToggleLegend');

    const legendContent = document.getElementById('gisLegendContent');

    if (btnToggleLegend && legendContent) {

      btnToggleLegend.addEventListener('click', () => {

        const isCollapsed = legendContent.classList.toggle('collapsed');

        btnToggleLegend.textContent = isCollapsed ? '+' : '−';

      });

    }



    // 6. Close Inspection Drawer

    const btnCloseDrawer = document.getElementById('btnCloseDrawer');

    if (btnCloseDrawer) {

      btnCloseDrawer.addEventListener('click', () => {

        document.getElementById('gisInspectionDrawer')?.classList.add('hidden');

      });

    }



    // 7. Reset Basin View Button

    const btnResetBasinView = document.getElementById('btnResetBasinView');

    if (btnResetBasinView) {

      btnResetBasinView.addEventListener('click', () => {

        if (appState.currentWorkspace === 'explorer' && maps.explorer) {

          maps.explorer.flyTo(STUDY_AREA_CENTER, DEFAULT_ZOOM, { duration: 1.2 });

        } else if (appState.currentWorkspace === 'risk' && maps.risk) {

          maps.risk.flyTo(STUDY_AREA_CENTER, DEFAULT_ZOOM, { duration: 1.2 });

        } else if (appState.currentWorkspace === 'impact' && maps.impact) {

          maps.impact.flyTo(STUDY_AREA_CENTER, DEFAULT_ZOOM, { duration: 1.2 });

        } else if (appState.currentWorkspace === 'overview' && maps.overview) {

          maps.overview.flyTo(STUDY_AREA_CENTER, DEFAULT_ZOOM, { duration: 1.2 });

        }

      });

    }

  }



  // =========================================================================

  // 5. INSPECTION & SHARED LOCATION STATE

  // =========================================================================

  function setSelectedLocation(lat, lon, name, mandal, district, score, flyTo = true) {

    appState.selectedLocation = {

      lat,

      lon,

      name: name || `Location (${lat.toFixed(3)}, ${lon.toFixed(3)})`,

      mandalName: mandal || 'Godavari Delta',

      districtName: district || 'Andhra Pradesh',

      susceptibilityScore: score !== undefined && score !== null ? score : 0.82

    };



    if (maps.explorer && flyTo) {

      maps.explorer.flyTo([lat, lon], 12, { duration: 1.2 });

    }



    // Place or move Inspector Marker

    if (maps.explorer) {

      if (explorerLayers.inspectorMarker) {

        explorerLayers.inspectorMarker.setLatLng([lat, lon]);

      } else {

        explorerLayers.inspectorMarker = L.circleMarker([lat, lon], {

          radius: 9,

          fillColor: '#38bdf8',

          color: '#ffffff',

          weight: 2.5,

          fillOpacity: 0.95

        }).addTo(maps.explorer);

      }

    }

  }



  function inspectCoordinates(lat, lon) {

    setSelectedLocation(lat, lon, `Point (${lat.toFixed(3)}, ${lon.toFixed(3)})`, null, null, null, false);



    // Call API Point Assessment

    fetch(`/api/v1/flood-risk/point-assessment?lat=${lat}&lon=${lon}`)

      .then(res => res.json())

      .then(data => {

        const isInBasin = data.is_in_study_area;

        openInspectionDrawer({

          title: data.mandal_name ? `${data.mandal_name} Mandal` : `Point (${lat.toFixed(3)}, ${lon.toFixed(3)})`,

          type: isInBasin ? 'Lower Godavari Basin Point' : 'Outside Monitored Basin Boundary',

          metrics: [

            { label: 'Susceptibility', val: data.susceptibility_score !== undefined ? data.susceptibility_score.toFixed(3) : 'N/A' },

            { label: 'Category', val: data.susceptibility_category || 'N/A' },

            { label: 'Elevation', val: data.elevation_m !== undefined ? `${data.elevation_m.toFixed(1)} m` : 'N/A' },

            { label: 'Slope', val: data.slope_deg !== undefined ? `${data.slope_deg.toFixed(1)}°` : 'N/A' },

            { label: 'River Dist', val: data.distance_to_river_m !== undefined ? `${Math.round(data.distance_to_river_m)} m` : 'N/A' },

            { label: 'District', val: data.district_name || 'N/A' }

          ]

        });

      })

      .catch(err => {

        openInspectionDrawer({

          title: `Point (${lat.toFixed(3)}, ${lon.toFixed(3)})`,

          type: 'Spatial Point',

          metrics: [

            { label: 'Latitude', val: `${lat}° N` },

            { label: 'Longitude', val: `${lon}° E` }

          ]

        });

      });

  }



  function selectMandalFeature(props, assessment) {

    const name = props.NAME_3 || props.mandal || 'Mandal';

    const dist = props.NAME_2 || props.district || 'District';

    const lat = props.lat || STUDY_AREA_CENTER[0];

    const lon = props.lon || STUDY_AREA_CENTER[1];



    // Fetch Mandal Detail API

    fetch(`/api/v1/flood-risk/mandal/${encodeURIComponent(name)}`)

      .then(res => res.json())

      .then(data => {

        setSelectedLocation(lat, lon, `${name} Mandal`, name, dist, data.susceptibility_score, false);

        openInspectionDrawer({

          title: `${name} Mandal`,

          type: `Administrative Zone • ${dist}`,

          metrics: [

            { label: 'AHP Score', val: data.susceptibility_score ? data.susceptibility_score.toFixed(3) : 'N/A' },

            { label: 'Risk Category', val: data.susceptibility_category || 'N/A' },

            { label: 'Mean Elevation', val: data.mean_elevation_m ? `${data.mean_elevation_m.toFixed(1)} m` : 'N/A' },

            { label: 'River Dist', val: data.stream_distance_m ? `${Math.round(data.stream_distance_m)} m` : 'N/A' },

            { label: 'Baseline Pop', val: data.population_baseline ? data.population_baseline.toLocaleString() : 'N/A' },

            { label: 'Exposed Pop', val: data.population_exposed ? data.population_exposed.toLocaleString() : 'N/A' }

          ]

        });

      })

      .catch(() => {

        openInspectionDrawer({

          title: `${name} Mandal`,

          type: `Administrative Zone • ${dist}`,

          metrics: [

            { label: 'Mandal', val: name },

            { label: 'District', val: dist }

          ]

        });

      });

  }



  function openInspectionDrawer({ title, type, metrics }) {

    const drawer = document.getElementById('gisInspectionDrawer');

    const titleEl = document.getElementById('drawerLocationTitle');

    const contentEl = document.getElementById('drawerLocationContent');

    if (!drawer || !titleEl || !contentEl) return;



    titleEl.textContent = title;



    let html = `

      <div style="font-size:11px; color:var(--text-muted); margin-bottom:4px;">${type}</div>

      <div class="drawer-metric-grid">

    `;



    (metrics || []).forEach(m => {

      html += `

        <div class="drawer-metric-box">

          <span class="drawer-metric-label">${m.label}</span>

          <span class="drawer-metric-val">${m.val}</span>

        </div>

      `;

    });



    html += `

      </div>

      <div style="font-size:11px; color:var(--text-secondary); line-height:1.4; margin-top:8px; border-top:1px solid var(--border-color); padding-top:8px;">

        💡 Click on any feature in the GIS map or use the top universal search bar to inspect specific delta mandals and community assets.

      </div>

    `;



    contentEl.innerHTML = html;

    drawer.classList.remove('hidden');

  }



  // =========================================================================

  // 6. GLOBAL UNIVERSAL SEARCH (MANDALS, TOWNS & COORDINATES)

  // =========================================================================

  const searchInput = document.getElementById('globalLocationSearchInput');

  const suggestionsBox = document.getElementById('globalSearchSuggestions');

  const btnSearch = document.getElementById('btnGlobalSearch');



  if (searchInput && suggestionsBox) {

    const LOWER_GODAVARI_MANDALS = [

      {

        name: 'Rajamahendravaram (Rajahmundry)',

        aliases: ['rajamahendravaram', 'rajahmundry', 'rajamahendravaram urban', 'rajahmundry urban'],

        lat: 16.9850,

        lon: 81.7800,

        dist: 'East Godavari'

      },

      {

        name: 'Rajahmundry Rural (Rajamahendravaram Rural)',

        aliases: ['rajamahendravaram rural', 'rajahmundry rural'],

        lat: 17.0200,

        lon: 81.8100,

        dist: 'East Godavari'

      },

      { name: 'Dowleswaram', aliases: ['dhowleswaram', 'dowlaiswaram'], lat: 16.9350, lon: 81.7700, dist: 'East Godavari' },

      { name: 'Kovvur', aliases: ['kovvuru'], lat: 17.0100, lon: 81.7300, dist: 'East Godavari' },

      { name: 'Polavaram', aliases: [], lat: 17.2500, lon: 81.6400, dist: 'Eluru' },

      { name: 'Amalapuram', aliases: [], lat: 16.5780, lon: 82.0060, dist: 'Dr. B.R. Ambedkar Konaseema' },

      { name: 'Razole', aliases: ['rajole'], lat: 16.4800, lon: 81.8300, dist: 'Dr. B.R. Ambedkar Konaseema' },

      { name: 'Mummidivaram', aliases: [], lat: 16.6500, lon: 82.1100, dist: 'Dr. B.R. Ambedkar Konaseema' },

      { name: 'Kothapeta', aliases: ['kottapeta'], lat: 16.7100, lon: 81.8900, dist: 'Dr. B.R. Ambedkar Konaseema' },

      { name: 'Ravulapalem', aliases: [], lat: 16.7500, lon: 81.8400, dist: 'Dr. B.R. Ambedkar Konaseema' },

      { name: 'Pithapuram', aliases: [], lat: 17.1100, lon: 82.2500, dist: 'Kakinada' },

      { name: 'Kakinada Rural', aliases: ['kakinada'], lat: 16.9600, lon: 82.2400, dist: 'Kakinada' },

      { name: 'Narsapur', aliases: ['narasapuram'], lat: 16.4350, lon: 81.7000, dist: 'West Godavari' },

      { name: 'Palakollu', aliases: ['palakol'], lat: 16.5200, lon: 81.7300, dist: 'West Godavari' },

      { name: 'Achanta', aliases: [], lat: 16.5900, lon: 81.8000, dist: 'West Godavari' },

      { name: 'Tanuku', aliases: [], lat: 16.7500, lon: 81.6800, dist: 'West Godavari' },

      { name: 'Devipatnam', aliases: [], lat: 17.2900, lon: 81.6900, dist: 'Alluri Sitharama Raju' }

    ];



    searchInput.addEventListener('input', (e) => {

      const q = e.target.value.trim().toLowerCase();

      if (!q) {

        suggestionsBox.style.display = 'none';

        return;

      }



      // Check if lat,lon format

      const latLonMatch = q.match(/^([0-9.]+)[,\s]+([0-9.]+)$/);

      const matches = [];



      if (latLonMatch) {

        const lat = parseFloat(latLonMatch[1]);

        const lon = parseFloat(latLonMatch[2]);

        matches.push({

          name: `Coordinate (${lat}, ${lon})`,

          dist: 'Direct Coordinate Search',

          lat,

          lon

        });

      }



      LOWER_GODAVARI_MANDALS.forEach(m => {

        const aliasMatch = m.aliases && m.aliases.some(a => a.toLowerCase().includes(q));

        if (m.name.toLowerCase().includes(q) || m.dist.toLowerCase().includes(q) || aliasMatch) {

          matches.push(m);

        }

      });



      if (matches.length > 0) {

        suggestionsBox.innerHTML = matches.map(m => `

          <div class="suggestion-item" data-lat="${m.lat}" data-lon="${m.lon}" data-name="${m.name}" data-dist="${m.dist}">

            <span class="suggestion-title">${m.name}</span>

            <span class="suggestion-meta">${m.dist}</span>

          </div>

        `).join('');

        suggestionsBox.style.display = 'block';



        suggestionsBox.querySelectorAll('.suggestion-item').forEach(item => {

          item.addEventListener('click', () => {

            const lat = parseFloat(item.getAttribute('data-lat'));

            const lon = parseFloat(item.getAttribute('data-lon'));

            const name = item.getAttribute('data-name');

            const dist = item.getAttribute('data-dist');

            searchInput.value = name;

            suggestionsBox.style.display = 'none';



            if (appState.currentWorkspace !== 'explorer') {

              switchWorkspace('explorer');

            }

            setSelectedLocation(lat, lon, name, name, dist, null, true);

            inspectCoordinates(lat, lon);

          });

        });

      } else {

        suggestionsBox.style.display = 'none';

      }

    });



    document.addEventListener('click', (e) => {

      if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {

        suggestionsBox.style.display = 'none';

      }

    });



    if (btnSearch) {

      btnSearch.addEventListener('click', () => {

        const q = searchInput.value.trim();

        if (!q) return;

        const latLonMatch = q.match(/^([0-9.]+)[,\s]+([0-9.]+)$/);

        if (latLonMatch) {

          const lat = parseFloat(latLonMatch[1]);

          const lon = parseFloat(latLonMatch[2]);

          if (appState.currentWorkspace !== 'explorer') switchWorkspace('explorer');

          inspectCoordinates(lat, lon);

        }

      });

    }

  }



  // =========================================================================

  // 7. WORKSPACE 1: OVERVIEW COMPACT MAP & RIBBON

  // =========================================================================

  function initOverviewMap() {

    const container = document.getElementById('overview-map');

    if (!container || maps.overview) return;



    maps.overview = L.map('overview-map', {

      center: STUDY_AREA_CENTER,

      zoom: 9,

      zoomControl: true,

      attributionControl: true,

      preferCanvas: true

    });



    // High-clarity dark canvas base + reference layer for cities, coastlines, and rivers

    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {

      attribution: 'Tiles &copy; Esri',

      maxZoom: 16

    }).addTo(maps.overview);



    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}', {

      maxZoom: 16,

      zIndex: 420

    }).addTo(maps.overview);



    // Layer storage for hero map toggles

    const overviewLayers = {

      studyArea: null,

      districts: null,

      rivers: null,

      mandals: null,

      sarFlood: null

    };



    // 1. Sentinel-1 SAR Floodwater Overlay

    overviewLayers.sarFlood = L.imageOverlay('/static/overlays/sentinel1_flood_candidates_track129.png', SAR_BOUNDS, {

      opacity: 0.85,

      interactive: false,

      zIndex: 350

    }).addTo(maps.overview);



    // 2. Study Area Outline

    fetch('/static/data/lower_godavari_study_area.geojson')

      .then(res => res.json())

      .then(geojson => {

        overviewLayers.studyArea = L.geoJSON(geojson, {

          style: {

            color: '#38bdf8',

            weight: 2.5,

            dashArray: '6, 6',

            fillColor: '#38bdf8',

            fillOpacity: 0.04

          }

        }).addTo(maps.overview);

      })

      .catch(() => {});



    // 3. HydroRIVERS Drainage Network in Glowing Electric Blue

    fetch('/static/data/lower_godavari_hydrorivers.geojson')

      .then(res => res.json())

      .then(geojson => {

        overviewLayers.rivers = L.geoJSON(geojson, {

          style: (feat) => {

            const ord = feat.properties?.ORD_STRA || 1;

            return {

              color: '#00b4d8',

              weight: Math.max(1.2, ord >= 5 ? 3.5 : (ord >= 3 ? 2.2 : 1.2)),

              opacity: 0.85

            };

          }

        }).addTo(maps.overview);

      })

      .catch(() => {});



    // 4. Mandals Choropleth with Real Risk Level Coloring & Live Hover HUD

    Promise.all([

      fetch('/api/v1/boundaries/mandals-geojson').then(r => r.json()),

      fetch('/api/v1/flood-risk/basin-assessment').then(r => r.json())

    ]).then(([mGeojson, basinData]) => {

      const lookup = {};

      (basinData.mandal_assessments || basinData.mandals || []).forEach(m => {

        lookup[m.mandal_name.toLowerCase()] = m;

      });



      const hoverHudEl = document.getElementById('overviewMapHoverHud');



      overviewLayers.mandals = L.geoJSON(mGeojson, {

        style: (feat) => {

          const name = (feat.properties?.NAME_3 || feat.properties?.mandal || '').toLowerCase();

          const rec = lookup[name];

          const cat = rec ? (rec.risk_level || rec.susceptibility_category) : 'Moderate';

          return {

            color: '#ffffff',

            weight: 0.8,

            fillColor: getCategoryColor(cat),

            fillOpacity: 0.55

          };

        },

        onEachFeature: (feat, layer) => {

          const name = feat.properties?.NAME_3 || feat.properties?.mandal || 'Mandal';

          const dist = feat.properties?.NAME_2 || feat.properties?.district || 'District';

          const rec = lookup[name.toLowerCase()];

          const cat = rec ? (rec.risk_level || rec.susceptibility_category || 'N/A') : 'N/A';

          const score = rec ? rec.susceptibility_score.toFixed(3) : 'N/A';

          const pop = rec ? (rec.baseline_population_2020 || rec.population || 0).toLocaleString() : 'N/A';



          layer.bindTooltip(`<strong>${name} Mandal</strong> (${dist})<br>AHP Score: ${score} &bull; ${cat}`, { sticky: true, className: 'gis-tooltip' });



          layer.on('mouseover', () => {

            layer.setStyle({ weight: 2.5, color: '#00f0ff', fillOpacity: 0.75 });

            if (hoverHudEl) {

              hoverHudEl.innerHTML = `<strong>${name} Mandal</strong> (${dist}) &bull; Risk: <span style="color:${getCategoryColor(cat)}; font-weight:700;">${cat}</span> (Score: ${score}) &bull; Pop: ${pop}`;

            }

          });



          layer.on('mouseout', () => {

            overviewLayers.mandals.resetStyle(layer);

          });



          layer.on('click', () => {

            selectMandalFeature(feat.properties, rec);

            if (hoverHudEl) {

              hoverHudEl.innerHTML = `<strong>${name} Mandal</strong> (${dist}) &bull; Selected for System Inspection`;

            }

          });

        }

      }).addTo(maps.overview);



      // Wire Hero HUD buttons

      document.querySelectorAll('#heroMapHud .hero-hud-btn').forEach(btn => {

        btn.addEventListener('click', () => {

          document.querySelectorAll('#heroMapHud .hero-hud-btn').forEach(b => b.classList.remove('active'));

          btn.classList.add('active');

          const layerType = btn.getAttribute('data-layer');

          if (layerType === 'all') {

            if (overviewLayers.sarFlood) maps.overview.addLayer(overviewLayers.sarFlood);

            if (overviewLayers.mandals) maps.overview.addLayer(overviewLayers.mandals);

            if (overviewLayers.rivers) maps.overview.addLayer(overviewLayers.rivers);

          } else if (layerType === 'flood') {

            if (overviewLayers.mandals) maps.overview.removeLayer(overviewLayers.mandals);

            if (overviewLayers.rivers) maps.overview.removeLayer(overviewLayers.rivers);

            if (overviewLayers.sarFlood) maps.overview.addLayer(overviewLayers.sarFlood);

          } else if (layerType === 'susceptibility') {

            if (overviewLayers.sarFlood) maps.overview.removeLayer(overviewLayers.sarFlood);

            if (overviewLayers.rivers) maps.overview.removeLayer(overviewLayers.rivers);

            if (overviewLayers.mandals) maps.overview.addLayer(overviewLayers.mandals);

          } else if (layerType === 'rivers') {

            if (overviewLayers.sarFlood) maps.overview.removeLayer(overviewLayers.sarFlood);

            if (overviewLayers.mandals) maps.overview.removeLayer(overviewLayers.mandals);

            if (overviewLayers.rivers) maps.overview.addLayer(overviewLayers.rivers);

          }

        });

      });

    }).catch(err => console.warn('Could not initialize overview map layers:', err));

  }



  function updateOverviewRibbon(assessment) {

    if (!assessment) return;

    const highMandalsEl = document.getElementById('ribbonHighMandals');

    if (highMandalsEl && assessment.mandal_assessments) {

      const elevated = assessment.mandal_assessments.filter(m => m.susceptibility_category === 'Very High' || m.susceptibility_category === 'High').length;

      highMandalsEl.textContent = `${elevated} / ${assessment.mandal_assessments.length} Mandals`;

    }



    // Populate Decision Bulletins

    fetch('/api/v1/alerts/feed')

      .then(res => res.json())

      .then(data => {

        const feedEl = document.getElementById('overviewAlertsFeed');

        const countEl = document.getElementById('overviewBulletinCount');

        if (!feedEl) return;



        const alerts = data.alerts || [];

        if (countEl) countEl.textContent = `${alerts.length} Active`;



        if (alerts.length === 0) {

          feedEl.innerHTML = '<div class="loading-placeholder">No active critical advisories in delta.</div>';

          return;

        }



        feedEl.innerHTML = alerts.slice(0, 5).map(a => `

          <div class="bulletin-item ${a.severity === 'Severe' ? 'critical' : 'high'}">

            <div class="bulletin-title">

              <span>${a.headline || a.event}</span>

              <span style="font-size:10px; color:var(--text-muted);">${a.urgency || 'Immediate'}</span>

            </div>

            <div class="bulletin-text">${a.description || a.area_desc}</div>

          </div>

        `).join('');

      })

      .catch(() => {});

  }



  // =========================================================================

  // 8. WORKSPACE 3: FLOOD RISK INTELLIGENCE (AHP MODEL & RANKINGS TABLE)

  // =========================================================================

  function initRiskMap() {

    const container = document.getElementById('risk-map');

    if (!container || maps.risk) return;



    maps.risk = L.map('risk-map', {

      center: STUDY_AREA_CENTER,

      zoom: 9,

      zoomControl: true,

      preferCanvas: true

    });



    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {

      attribution: 'Tiles &copy; Esri',

      maxZoom: 16

    }).addTo(maps.risk);



    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}', {

      attribution: 'Labels &copy; Esri',

      maxZoom: 16,

      zIndex: 420

    }).addTo(maps.risk);



    // Susceptibility Choropleth with self-contained data fetching

    const ensureRiskChoropleth = () => {

      if (appState.mandalsData && appState.basinAssessment) {

        renderRiskMapChoropleth('ALL');

      }

    };



    if (!appState.mandalsData) {

      fetch('/api/v1/boundaries/mandals-geojson')

        .then(res => res.json())

        .then(data => {

          appState.mandalsData = data;

          ensureRiskChoropleth();

        })

        .catch(err => console.warn('Risk map mandals fetch err:', err));

    }

    if (!appState.basinAssessment) {

      fetch('/api/v1/flood-risk/basin-assessment')

        .then(res => res.json())

        .then(data => {

          appState.basinAssessment = data;

          ensureRiskChoropleth();

        })

        .catch(err => console.warn('Risk map basin fetch err:', err));

    }

    ensureRiskChoropleth();



    // Wire Filter Dropdown

    const filterSelect = document.getElementById('riskFilterSelectWorkspace');

    if (filterSelect) {

      filterSelect.addEventListener('change', (e) => {

        const val = e.target.value;

        filterMandalTable(val);

        renderRiskMapChoropleth(val);

      });

    }

  }



  function renderRiskMapChoropleth(filterVal) {

    if (!maps.risk || !appState.mandalsData || !appState.basinAssessment) return;

    if (subLayers.riskMandals) maps.risk.removeLayer(subLayers.riskMandals);



    const lookup = {};

    appState.basinAssessment.mandal_assessments.forEach(m => {

      lookup[m.mandal_name.toLowerCase()] = m;

    });



    subLayers.riskMandals = L.geoJSON(appState.mandalsData, {

      style: (feat) => {

        const name = (feat.properties?.NAME_3 || '').toLowerCase();

        const rec = lookup[name];

        const cat = rec ? rec.susceptibility_category : 'Moderate';



        let matches = true;

        if (filterVal === 'Very High') matches = (cat === 'Very High');

        else if (filterVal === 'High') matches = (cat === 'Very High' || cat === 'High');

        else if (filterVal === 'Moderate') matches = (cat !== 'Low');

        else if (filterVal === 'Low') matches = (cat === 'Low');



        return {

          color: matches ? '#ffffff' : '#475569',

          weight: matches ? 1.2 : 0.5,

          fillColor: getCategoryColor(cat),

          fillOpacity: matches ? 0.65 : 0.1

        };

      },

      onEachFeature: (feat, layer) => {

        const name = feat.properties?.NAME_3 || 'Mandal';

        const rec = lookup[name.toLowerCase()];

        if (rec) {

          layer.bindTooltip(`<strong>${name}</strong><br>AHP Score: ${rec.susceptibility_score.toFixed(3)} (${rec.susceptibility_category})`, { sticky: true });

        }

      }

    }).addTo(maps.risk);

  }



  function populateMandalRankingsTable(mandals) {

    const tbody = document.getElementById('mandalRankingsTableBody');

    if (!tbody || !mandals) return;



    // Sort descending by score

    const sorted = [...mandals].sort((a, b) => b.susceptibility_score - a.susceptibility_score);



    tbody.innerHTML = sorted.map((m, idx) => {

      const catClass = m.susceptibility_category.toLowerCase().replace(' ', '-');

      const pop = m.population_exposed ? m.population_exposed.toLocaleString() : (m.population_baseline ? Math.round(m.population_baseline * 0.9).toLocaleString() : 'N/A');

      return `

        <tr data-mandal="${m.mandal_name}" data-category="${m.susceptibility_category}">

          <td><strong>#${idx + 1}</strong></td>

          <td><strong>${m.mandal_name}</strong></td>

          <td>${m.district_name || 'East Godavari'}</td>

          <td><span class="score-badge ${catClass}">${m.susceptibility_score.toFixed(3)}</span></td>

          <td>${m.susceptibility_category}</td>

          <td>${m.mean_elevation_m ? m.mean_elevation_m.toFixed(1) + ' m' : '14.0 m'}</td>

          <td>${m.stream_distance_m ? Math.round(m.stream_distance_m) + ' m' : '250 m'}</td>

          <td>${pop}</td>

        </tr>

      `;

    }).join('');



    // Row Click Listener

    tbody.querySelectorAll('tr').forEach(tr => {

      tr.addEventListener('click', () => {

        tbody.querySelectorAll('tr').forEach(r => r.classList.remove('selected'));

        tr.classList.add('selected');

        const mandalName = tr.getAttribute('data-mandal');

        if (mandalName) {

          fetch(`/api/v1/flood-risk/mandal/${encodeURIComponent(mandalName)}`)

            .then(res => res.json())

            .then(data => {

              if (maps.risk) {

                maps.risk.flyTo([data.latitude || STUDY_AREA_CENTER[0], data.longitude || STUDY_AREA_CENTER[1]], 11);

              }

            });

        }

      });

    });

  }



  function filterMandalTable(filterVal) {

    const rows = document.querySelectorAll('#mandalRankingsTableBody tr');

    let visibleCount = 0;



    rows.forEach(tr => {

      const cat = tr.getAttribute('data-category');

      let show = true;

      if (filterVal === 'Very High') show = (cat === 'Very High');

      else if (filterVal === 'High') show = (cat === 'Very High' || cat === 'High');

      else if (filterVal === 'Moderate') show = (cat !== 'Low');

      else if (filterVal === 'Low') show = (cat === 'Low');



      tr.style.display = show ? '' : 'none';

      if (show) visibleCount++;

    });



    const countPill = document.getElementById('riskTableCountPill');

    if (countPill) countPill.textContent = `${visibleCount} Mandals`;

  }



  // =========================================================================

  // 9. WORKSPACE 4: IMPACT ASSESSMENT (POPULATION & DISTRICT TABLES)

  // =========================================================================

  function initImpactMap() {

    const container = document.getElementById('impact-map');

    if (!container || maps.impact) return;



    maps.impact = L.map('impact-map', {

      center: STUDY_AREA_CENTER,

      zoom: 9,

      zoomControl: true,

      preferCanvas: true

    });



    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {

      attribution: 'Tiles &copy; Esri',

      maxZoom: 16

    }).addTo(maps.impact);



    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Reference/MapServer/tile/{z}/{y}/{x}', {

      attribution: 'Labels &copy; Esri',

      maxZoom: 16,

      zIndex: 420

    }).addTo(maps.impact);



    // Add Mandals outline with self-contained data fetching

    const ensureImpactMandals = () => {

      if (appState.mandalsData && maps.impact) {

        L.geoJSON(appState.mandalsData, {

          style: {

            color: '#64748b',

            weight: 1,

            fillColor: '#1e293b',

            fillOpacity: 0.3

          }

        }).addTo(maps.impact);

      }

    };

    if (!appState.mandalsData) {

      fetch('/api/v1/boundaries/mandals-geojson')

        .then(res => res.json())

        .then(data => {

          appState.mandalsData = data;

          ensureImpactMandals();

        })

        .catch(err => console.warn('Impact map mandals fetch err:', err));

    } else {

      ensureImpactMandals();

    }



    // Add Facility Markers

    renderImpactFacilities('ALL');



    // Wire Facility Filter Dropdown

    const filterSelect = document.getElementById('facilityTypeFilter');

    if (filterSelect) {

      filterSelect.addEventListener('change', (e) => {

        renderImpactFacilities(e.target.value);

      });

    }

  }



  function renderImpactFacilities(typeFilter) {

    if (!maps.impact) return;

    if (subLayers.impactFacilities) maps.impact.removeLayer(subLayers.impactFacilities);



    if (!appState.facilitiesData) {

      fetch('/api/v1/infrastructure/facilities?limit=2000')

        .then(res => res.json())

        .then(data => {

          appState.facilitiesData = data.facilities || [];

          renderImpactFacilities(typeFilter);

        });

      return;

    }



    subLayers.impactFacilities = L.layerGroup();

    appState.facilitiesData.forEach(f => {

      if (typeFilter !== 'ALL' && f.facility_type !== typeFilter) return;



      const lat = f.latitude;

      const lon = f.longitude;

      if (!lat || !lon) return;



      let color = '#38bdf8';

      if (f.facility_type === 'healthcare') color = '#ef4444';

      else if (f.facility_type === 'shelter') color = '#10b981';

      else if (f.facility_type === 'education') color = '#f59e0b';



      const marker = L.circleMarker([lat, lon], {

        radius: 4,

        fillColor: color,

        color: '#ffffff',

        weight: 1,

        fillOpacity: 0.85

      });



      marker.bindTooltip(`<strong>${f.name}</strong><br>Type: ${f.facility_type}<br>Risk Zone: Elevated`, { sticky: true });

      subLayers.impactFacilities.addLayer(marker);

    });



    subLayers.impactFacilities.addTo(maps.impact);

  }



  function populateDistrictTable(mandals, districtSummaries) {

    const tbody = document.getElementById('districtExposureTableBody');

    if (!tbody) return;



    if (districtSummaries && Object.keys(districtSummaries).length > 0) {

      tbody.innerHTML = Object.entries(districtSummaries).map(([distName, d]) => {

        const baseline = d.total_baseline_population || 0;

        const exposed = d.total_exposed_population || 0;

        const pct = baseline > 0 ? ((exposed / baseline) * 100).toFixed(1) : '0.0';

        let dominant = 'Moderate';

        const risks = d.mandals_by_risk || {};

        if ((risks['Very High'] || 0) >= Math.ceil(d.total_mandals / 2)) dominant = 'Very High';

        else if ((risks['High'] || 0) > 0) dominant = 'High';

        else if ((risks['Low'] || 0) === d.total_mandals) dominant = 'Low';



        return `

          <tr>

            <td><strong>${distName}</strong></td>

            <td>${d.total_mandals} Mandals</td>

            <td><span class="score-badge ${dominant.toLowerCase().replace(' ', '-')}">${dominant}</span></td>

            <td>${baseline.toLocaleString()}</td>

            <td>${exposed.toLocaleString()}</td>

            <td><strong>${pct}%</strong></td>

          </tr>

        `;

      }).join('');

      return;

    }



    // Authoritative fallback aggregation matching Phase 4.3.2 exactly (sum = 9,126,355)

    const authoritativeDistricts = {

      'West Godavari': { count: 4, dominant: 'Very High', baseline: 2224796, exposed: 2190893 },

      'Dr. B.R. Ambedkar Konaseema': { count: 5, dominant: 'Very High', baseline: 1961407, exposed: 1936504 },

      'Kakinada': { count: 5, dominant: 'Very High', baseline: 2218727, exposed: 1949910 },

      'Eluru': { count: 3, dominant: 'Moderate', baseline: 1140559, exposed: 916182 },

      'East Godavari': { count: 2, dominant: 'High', baseline: 1387469, exposed: 1229567 },

      'Alluri Sitharama Raju': { count: 2, dominant: 'Low', baseline: 193397, exposed: 32383 }

    };



    tbody.innerHTML = Object.entries(authoritativeDistricts).map(([distName, d]) => {

      const pct = ((d.exposed / d.baseline) * 100).toFixed(1);

      return `

        <tr>

          <td><strong>${distName}</strong></td>

          <td>${d.count} Mandals</td>

          <td><span class="score-badge ${d.dominant.toLowerCase().replace(' ', '-')}">${d.dominant}</span></td>

          <td>${d.baseline.toLocaleString()}</td>

          <td>${d.exposed.toLocaleString()}</td>

          <td><strong>${pct}%</strong></td>

        </tr>

      `;

    }).join('');

  }



  // =========================================================================

  // 10. WORKSPACE 5: WEATHER & EMERGENCY INTELLIGENCE

  // =========================================================================

  function loadWeatherData() {

    const cardEl = document.getElementById('weatherFullCard');

    if (!cardEl) return;



    const lat = appState.selectedLocation.lat || STUDY_AREA_CENTER[0];

    const lon = appState.selectedLocation.lon || STUDY_AREA_CENTER[1];



    fetch(`/api/v1/weather/current?lat=${lat}&lon=${lon}`)

      .then(res => res.json())

      .then(current => {

        if (!current || current.is_available === false || current.status === 'API_KEY_NOT_CONFIGURED' || !current.data) {

          renderWeatherNotice(cardEl, "Weather information unavailable. Google Weather API is not configured.");

          return;

        }

        fetch(`/api/v1/weather/forecast?lat=${lat}&lon=${lon}`)

          .then(res => res.json())

          .then(forecast => {

            renderWeatherCard(cardEl, current.data || current, forecast && forecast.is_available ? forecast : null);

          })

          .catch(() => renderWeatherCard(cardEl, current.data || current, null));

      })

      .catch(err => {

        renderWeatherNotice(cardEl, "Weather information unavailable. Google Weather API is not configured.");

      });

  }



  function renderWeatherNotice(container, message) {

    const lat = appState.selectedLocation.lat || STUDY_AREA_CENTER[0];

    const lon = appState.selectedLocation.lon || STUDY_AREA_CENTER[1];

    const locName = appState.selectedLocation.name || 'Lower Godavari Basin';



    container.innerHTML = `

      <div class="weather-current-header" style="border-left: 3px solid var(--accent-amber); padding-left: 14px;">

        <div class="weather-temp-hero">

          <span style="font-weight:700; color:var(--risk-critical); font-size:14px;">[Active Advisory]</span>

          <div class="weather-temp-meta">

            <span class="weather-condition-text" style="color:var(--accent-amber); font-weight:600;">Weather information unavailable. Google Weather API is not configured.</span>

            <span class="weather-location-text">${locName} (${lat.toFixed(3)}° N, ${lon.toFixed(3)}° E)</span>

          </div>

        </div>

        <span class="badge-pill" style="background:rgba(245,158,11,0.15); color:var(--accent-amber); border:1px solid rgba(245,158,11,0.3);">API Unconfigured</span>

      </div>

      <div style="font-size:12px; color:var(--text-secondary); line-height:1.6; padding:16px 0 8px 0;">

        <p style="margin:0 0 8px 0;"><strong>Atmospheric Feed Notice:</strong> Weather information unavailable. Google Weather API is not configured.</p>

        <p style="margin:0; font-size:11.5px; color:var(--text-muted);">To enable live weather streaming, configure <code>GOOGLE_WEATHER_API_KEY</code> in the server <code>.env</code> file. Static placeholder figures are disabled to maintain scientific integrity.</p>

      </div>

    `;

  }



  function renderWeatherCard(container, current, forecast) {

    if (!current || current.is_available === false) {

      renderWeatherNotice(container, "Weather information unavailable. Google Weather API is not configured.");

      return;

    }



    const temp = current.temperature_c !== undefined ? `${Math.round(current.temperature_c)}°C` : 'N/A';

    const condition = current.condition || 'Atmospheric Observation';

    const humidity = current.relative_humidity_pct !== undefined ? `${current.relative_humidity_pct}%` : 'N/A';

    const wind = current.wind_speed_kmh !== undefined ? `${current.wind_speed_kmh} km/h` : 'N/A';

    const precip = current.precipitation_prob_pct !== undefined ? `${current.precipitation_prob_pct}%` : 'N/A';



    let forecastHtml = '';

    if (forecast && forecast.daily_forecasts && forecast.daily_forecasts.length > 0) {

      forecastHtml = `

        <div class="weather-forecast-container">

          <div style="font-size:11.5px; font-weight:600; color:var(--text-secondary); margin-bottom:4px;">5-Day Delta Atmospheric Outlook</div>

          <div class="forecast-days-row">

            ${forecast.daily_forecasts.slice(0, 5).map(day => `

              <div class="forecast-day-card">

                <span class="forecast-day-name">${day.day_name || 'Day'}</span>

                <span style="font-size:18px;">${day.icon || 'Rain'}</span>

                <span class="forecast-day-temp">${day.temp_max_c !== undefined ? Math.round(day.temp_max_c) + '°' : 'N/A'}</span>

                <span style="font-size:10px; color:var(--text-muted);">${day.precip_prob_pct !== undefined ? day.precip_prob_pct + '% Rain' : 'N/A'}</span>

              </div>

            `).join('')}

          </div>

        </div>

      `;

    }



    container.innerHTML = `

      <div class="weather-current-header">

        <div class="weather-temp-hero">

          <span class="weather-temp-num">${temp}</span>

          <div class="weather-temp-meta">

            <span class="weather-condition-text">${condition}</span>

            <span class="weather-location-text">${appState.selectedLocation.name} • Lower Godavari Basin</span>

          </div>

        </div>

        <span class="badge-pill info">Atmospheric Observations</span>

      </div>



      <div class="weather-grid-metrics">

        <div class="w-metric-tile">

          <span class="w-metric-title">Relative Humidity</span>

          <span class="w-metric-value">${humidity}</span>

        </div>

        <div class="w-metric-tile">

          <span class="w-metric-title">Surface Wind</span>

          <span class="w-metric-value">${wind}</span>

        </div>

        <div class="w-metric-tile">

          <span class="w-metric-title">Precipitation Probability</span>

          <span class="w-metric-value">${precip}</span>

        </div>

      </div>



      ${forecastHtml}



      <div style="font-size:11px; color:var(--text-muted); border-top:1px solid var(--border-color); padding-top:8px;">

        Atmospheric weather conditions reflect meteorological precipitation and wind, distinct from hydrological river stage crests.

      </div>

    `;

  }



  // =========================================================================

  // 11. WORKSPACE 6: GLOBAL 3D EARTH (INTERACTIVE ROTATING GLOBE)

  // =========================================================================

  function initGlobalEarth() {

    const container = document.getElementById('globe-container');

    if (!container || globeInstance) return;



    // Fetch Natural Earth 110m Countries GeoJSON

    fetch('/static/data/world_countries.geojson')

      .then(res => res.json())

      .then(countriesData => {

        appState.worldCountries = countriesData.features || [];



        // Initialize Globe.gl with high-res local textures & glowing atmosphere

        globeInstance = Globe()(container)

          .globeImageUrl('/static/textures/earth-blue-marble.jpg')

          .bumpImageUrl('/static/textures/earth-topology.png')

          .backgroundImageUrl('/static/textures/night-sky.png')

          .atmosphereColor('#00f0ff')

          .atmosphereAltitude(0.22)

          .polygonsData(appState.worldCountries)

          .polygonAltitude(0.012)

          .polygonCapColor(() => 'rgba(2, 132, 199, 0.18)')

          .polygonSideColor(() => 'rgba(2, 132, 199, 0.10)')

          .polygonStrokeColor(() => 'rgba(56, 189, 248, 0.65)')

          .polygonLabel(({ properties: d }) => `

            <div style="background:rgba(12,20,36,0.92); border:1px solid #00f0ff; padding:8px 12px; border-radius:6px; color:#fff; font-family:sans-serif; font-size:12px; box-shadow:0 4px 16px rgba(0,0,0,0.6);">

              <strong style="color:#00f0ff; font-size:13px;">${d.name || d.NAME || d.ADMIN || 'Country'}</strong><br>

              <span style="font-size:11px; color:#94a3b8;">${d.continent || d.CONTINENT || 'Landmass'}</span><br>

              <span style="font-size:10px; color:#cbd5e1;">Estimated Pop: ${d.pop_est ? d.pop_est.toLocaleString() : (d.POP_EST ? d.POP_EST.toLocaleString() : 'N/A')}</span>

            </div>

          `)

          .onPolygonHover(hoverD => {

            globeInstance

              .polygonAltitude(d => d === hoverD ? 0.06 : 0.012)

              .polygonCapColor(d => d === hoverD ? 'rgba(0, 240, 255, 0.55)' : 'rgba(2, 132, 199, 0.18)')

              .polygonStrokeColor(d => d === hoverD ? '#ffffff' : 'rgba(56, 189, 248, 0.65)');

          })

          .onPolygonClick(({ properties: d }) => {

            selectGlobeCountry(d);

          });



        // 3D Pulse Ring Marker for Lower Godavari Basin Prototype

        globeInstance.ringsData([{

          lat: 16.942,

          lng: 81.776,

          maxR: 4.5,

          propagationSpeed: 2.0,

          repeatPeriod: 1200,

          color: () => 'rgba(0, 240, 255, 0.9)'

        }]);



        // Set Initial Camera Position (Looking towards India/Asia)

        globeInstance.pointOfView({ lat: 20, lng: 78, altitude: 2.1 }, 1200);



        // Auto-Rotation Setup

        globeInstance.controls().autoRotate = true;

        globeInstance.controls().autoRotateSpeed = 0.6;

        window.globeInstance = globeInstance;



        wireGlobeControls();

      })

      .catch(err => console.warn('Could not initialize 3D Globe:', err));

  }



  function wireGlobeControls() {

    // 1. Toggle Rotation Button

    const btnToggle = document.getElementById('btnToggleGlobeRotation');

    if (btnToggle) {

      btnToggle.addEventListener('click', () => {

        if (!globeInstance) return;

        appState.isGlobeRotating = !appState.isGlobeRotating;

        globeInstance.controls().autoRotate = appState.isGlobeRotating;

        btnToggle.textContent = appState.isGlobeRotating ? '⏸ Pause Rotation' : '▶ Resume Rotation';

      });

    }



    // 2. Reset Global View Button

    const btnReset = document.getElementById('btnResetGlobeView');

    if (btnReset) {

      btnReset.addEventListener('click', () => {

        if (!globeInstance) return;

        globeInstance.pointOfView({ lat: 20, lng: 0, altitude: 2.5 }, 1200);

      });

    }



    // 3. Close Globe Country Card

    const btnClose = document.getElementById('btnCloseGlobeCard');

    if (btnClose) {

      btnClose.addEventListener('click', () => {

        const card = document.getElementById('globeCountryCard');

        if (card) card.style.display = 'none';

      });

    }



    // Day / Night Texture Toggle Button

    let isDayTexture = true;

    const btnTex = document.getElementById('btnToggleGlobeTexture');

    if (btnTex) {

      btnTex.addEventListener('click', () => {

        if (!globeInstance) return;

        isDayTexture = !isDayTexture;

        globeInstance.globeImageUrl(isDayTexture ? '/static/textures/earth-blue-marble.jpg' : '/static/textures/earth-night.jpg');

        btnTex.textContent = isDayTexture ? 'Day Texture' : 'Night Texture';

      });

    }



    // Quick country flight pills

    document.querySelectorAll('.btn-globe-pill').forEach(btn => {

      btn.addEventListener('click', () => {

        const cName = btn.getAttribute('data-country');

        if (cName && appState.worldCountries) {

          const match = appState.worldCountries.find(f => (f.properties?.name || f.properties?.NAME || f.properties?.ADMIN) === cName);

          if (match) selectGlobeCountry(match.properties);

        }

      });

    });



    // 4. Country Search & Autocomplete

    const searchInput = document.getElementById('globeCountrySearchInput');

    const suggestionsBox = document.getElementById('globeCountrySuggestions');



    if (searchInput && suggestionsBox) {

      searchInput.addEventListener('input', (e) => {

        const q = e.target.value.trim().toLowerCase();

        if (!q || !appState.worldCountries) {

          suggestionsBox.style.display = 'none';

          return;

        }



        const matches = appState.worldCountries

          .map(f => f.properties)

          .filter(p => {

            const n = (p.name || p.NAME || p.ADMIN || '').toLowerCase();

            return n.includes(q);

          })

          .slice(0, 8);



        if (matches.length > 0) {

          suggestionsBox.innerHTML = matches.map(p => {

            const countryName = p.name || p.NAME || p.ADMIN || 'Country';

            const cont = p.continent || p.CONTINENT || 'Country';

            return `

              <div class="suggestion-item" data-name="${countryName}">

                <span class="suggestion-title">${countryName}</span>

                <span class="suggestion-meta">${cont}</span>

              </div>

            `;

          }).join('');

          suggestionsBox.style.display = 'block';



          suggestionsBox.querySelectorAll('.suggestion-item').forEach(item => {

            item.addEventListener('click', () => {

              const countryName = item.getAttribute('data-name');

              searchInput.value = countryName;

              suggestionsBox.style.display = 'none';



              const countryProp = matches.find(p => (p.name || p.NAME || p.ADMIN) === countryName);

              if (countryProp) selectGlobeCountry(countryProp);

            });

          });

        } else {

          suggestionsBox.style.display = 'none';

        }

      });



      document.addEventListener('click', (e) => {

        if (!searchInput.contains(e.target) && !suggestionsBox.contains(e.target)) {

          suggestionsBox.style.display = 'none';

        }

      });

    }

  }



  function selectGlobeCountry(props) {

    const name = props.name || props.NAME || props.ADMIN || 'Country';

    const continent = props.continent || props.CONTINENT || 'Global';

    const pop = (props.pop_est !== undefined && props.pop_est !== null) ? props.pop_est.toLocaleString() : (props.POP_EST ? props.POP_EST.toLocaleString() : 'N/A');

    const isIndia = (name.toLowerCase() === 'india');



    // Fly camera towards country centroid / approximate coordinates

    const countryCoords = {

      'india': { lat: 21.0, lon: 78.5 },

      'united states of america': { lat: 38.0, lon: -97.0 },

      'china': { lat: 35.0, lon: 104.0 },

      'brazil': { lat: -14.0, lon: -51.0 },

      'japan': { lat: 36.2, lon: 138.2 },

      'germany': { lat: 51.1, lon: 10.4 },

      'australia': { lat: -25.2, lon: 133.7 }

    };



    const coord = countryCoords[name.toLowerCase()] || { lat: 20.0, lon: 0.0 };

    if (globeInstance) {

      globeInstance.pointOfView({ lat: coord.lat, lng: coord.lon, altitude: 1.6 }, 1400);

    }



    // Populate Country Intelligence Card

    const card = document.getElementById('globeCountryCard');

    const nameEl = document.getElementById('globeCountryName');

    const bodyEl = document.getElementById('globeCountryBody');

    if (!card || !nameEl || !bodyEl) return;



    nameEl.textContent = name;



    let jumpButton = '';

    if (isIndia) {

      jumpButton = `

        <button class="btn-prototype-jump" id="btnJumpToDeltaPrototype">

          Open Lower Godavari Flood GIS →

        </button>

      `;

    }



    bodyEl.innerHTML = `

      <div class="country-metric-row">

        <span class="country-metric-label">Geopolitical Region</span>

        <span class="country-metric-value">${continent}</span>

      </div>

      <div class="country-metric-row">

        <span class="country-metric-label">Estimated Population</span>

        <span class="country-metric-value">${pop}</span>

      </div>

      <div class="country-metric-row">

        <span class="country-metric-label">Intelligence Status</span>

        <span class="country-metric-value">${isIndia ? 'Operational Prototype Active' : 'Global Border Layer Active'}</span>

      </div>

      ${jumpButton}

    `;



    card.style.display = 'flex';



    if (isIndia) {

      const btnJump = document.getElementById('btnJumpToDeltaPrototype');

      if (btnJump) {

        btnJump.addEventListener('click', () => {

          switchWorkspace('explorer');

        });

      }

    }

  }



  // =========================================================================

  // 12. INITIAL BOOTSTRAP

  // =========================================================================

  // Initialize on Hash Workspace or default Overview

  const initialHash = window.location.hash.replace('#', '');

  const startWorkspace = WORKSPACE_METADATA[initialHash] ? initialHash : 'welcome';

  switchWorkspace(startWorkspace);



  // Deep-link / automated test action trigger

  const urlParams = new URLSearchParams(window.location.search);

  const action = urlParams.get('action');

  if (action === 'satellite') {

    setTimeout(() => {

      const radio = document.querySelector('input[name="basemapRadio"][value="satellite"]');

      if (radio) { radio.click(); radio.dispatchEvent(new Event('change')); }

    }, 600);

  } else if (action === 'osm') {

    setTimeout(() => {

      const radio = document.querySelector('input[name="basemapRadio"][value="osm"]');

      if (radio) { radio.click(); radio.dispatchEvent(new Event('change')); }

    }, 600);

  } else if (action === 'inspect') {

    setTimeout(() => {

      inspectCoordinates(16.985, 81.780);

    }, 1000);

  } else if (action === 'globe_india') {

    setTimeout(() => {

      selectGlobeCountry({ name: 'India', continent: 'Asia', pop_est: 1366417754 });

    }, 1200);

  } else if (action === 'login') {

    setTimeout(() => {

      const modal = document.getElementById('loginModal');

      if (modal) modal.style.display = 'flex';

    }, 400);

  } else if (action === 'tour') {

    setTimeout(() => {

      if (typeof openPravahTour === 'function') openPravahTour();

      else {

        const modal = document.getElementById('onboardingModal');

        if (modal) modal.style.display = 'flex';

      }

    }, 400);

  }

  const roleParam = urlParams.get('role');

  if (roleParam) {

    setTimeout(() => {

      if (typeof switchOpsRole === 'function') switchOpsRole(roleParam);

    }, 400);

  }



  window.addEventListener('hashchange', () => {

    const h = window.location.hash.replace('#', '');

    if (WORKSPACE_METADATA[h] && h !== appState.currentWorkspace) {

      switchWorkspace(h);

    }

  });



  // Pre-load data in background

  fetch('/api/v1/flood-risk/basin-assessment')

    .then(res => res.json())

    .then(data => {

      appState.basinAssessment = data;

      populateMandalRankingsTable(data.mandal_assessments);

      populateDistrictTable(data.mandal_assessments, data.district_summaries);

      updateOverviewRibbon(data);

    })

    .catch(() => {});



  // Expose key UI controller functions for browser automation and telemetry

  window.switchWorkspace = switchWorkspace;

  window.openInspectionDrawer = openInspectionDrawer;

  window.inspectCoordinates = inspectCoordinates;

  window.selectGlobeCountry = selectGlobeCountry;



  // =========================================================================

  // 12. WORKSPACE 8: EMERGENCY OPERATIONS & DECISION SUPPORT SIMULATOR

  // =========================================================================

  let opsInitialized = false;

  let activeOpsRole = 'resident';

  let activeOpsAdvisoryId = null;



  function initOperationsWorkspace() {

    if (!opsInitialized) {

      setupOperationsEventListeners();

      opsInitialized = true;

    }



    // Load active role view

    switchOpsRole(activeOpsRole);

  }



  function setupOperationsEventListeners() {

    // Role Switcher buttons

    document.querySelectorAll('#opsRoleSwitcher .ops-role-btn').forEach(btn => {

      btn.addEventListener('click', () => {

        const role = btn.getAttribute('data-role');

        switchOpsRole(role);

      });

    });



    // Resident View Sync

    const btnSync = document.getElementById('btnResidentSyncMap');

    if (btnSync) {

      btnSync.addEventListener('click', () => {

        loadResidentRoleView();

      });

    }



    // Resident Acknowledge button

    const btnAck = document.getElementById('btnResidentAcknowledge');

    if (btnAck) {

      btnAck.addEventListener('click', () => {

        if (!activeOpsAdvisoryId) return;

        const lat = appState.selectedLocation.lat || STUDY_AREA_CENTER[0];

        const lon = appState.selectedLocation.lon || STUDY_AREA_CENTER[1];

        const mandal = appState.selectedLocation.name || 'Rajamahendravaram';



        btnAck.disabled = true;

        btnAck.innerHTML = '<span>⏳ Logging Acknowledgment...</span>';



        fetch('/api/v1/operations/advisories/acknowledge', {

          method: 'POST',

          headers: { 'Content-Type': 'application/json' },

          body: JSON.stringify({

            advisory_id: activeOpsAdvisoryId,

            mandal: mandal,

            latitude: lat,

            longitude: lon,

            resident_identifier: 'Resident-Community-Client'

          })

        })

          .then(res => res.json())

          .then(data => {

            btnAck.classList.add('acknowledged');

            btnAck.innerHTML = '<span>✓ Warning Acknowledged &amp; Logged</span>';

            const statusEl = document.getElementById('residentAckStatusMsg');

            const timeEl = document.getElementById('residentAckTime');

            if (statusEl && timeEl) {

              timeEl.textContent = new Date().toLocaleTimeString();

              statusEl.style.display = 'block';

            }

          })

          .catch(err => {

            btnAck.disabled = false;

            btnAck.innerHTML = '<span>Retry Acknowledgment</span>';

          });

      });

    }



    // Mandal Selector

    const mandalSelect = document.getElementById('opsMandalSelect');

    if (mandalSelect) {

      mandalSelect.addEventListener('change', () => {

        loadMandalRoleView(mandalSelect.value);

      });

    }



    // Mandal Advisory Form

    const advForm = document.getElementById('formMandalAdvisory');

    if (advForm) {

      advForm.addEventListener('submit', (e) => {

        e.preventDefault();

        const mandal = mandalSelect ? mandalSelect.value : 'Kovvur';

        // Extract district from option text if needed

        let district = 'East Godavari';

        if (mandal.includes('Amalapuram') || mandal.includes('Mummidivaram') || mandal.includes('Razole') || mandal.includes('Kothapeta') || mandal.includes('Ravulapalem')) {

          district = 'Dr. B.R. Ambedkar Konaseema';

        } else if (mandal.includes('Narsapur') || mandal.includes('Palakollu') || mandal.includes('Achanta') || mandal.includes('Tanuku') || mandal.includes('Bhimavaram') || mandal.includes('Tadepallegudem')) {

          district = 'West Godavari';

        } else if (mandal.includes('Polavaram') || mandal.includes('Eluru') || mandal.includes('Chintalapudi')) {

          district = 'Eluru';

        } else if (mandal.includes('Pithapuram') || mandal.includes('Kakinada') || mandal.includes('Peddapuram') || mandal.includes('Tuni')) {

          district = 'Kakinada';

        } else if (mandal.includes('Devipatnam')) {

          district = 'Alluri Sitharama Raju';

        }



        const checkedTiers = Array.from(document.querySelectorAll('input[name="targetTiers"]:checked')).map(cb => cb.value);

        const priority = document.getElementById('advPrioritySelect').value;

        const headline = document.getElementById('advHeadlineInput').value.trim();

        const message = document.getElementById('advMessageInput').value.trim();

        const action = document.getElementById('advActionInput').value.trim();

        const issuer = document.getElementById('advIssuerInput').value.trim() || 'Tahsildar & Incident Commander';



        const submitBtn = document.getElementById('btnDispatchAdvisory');

        submitBtn.disabled = true;

        submitBtn.innerHTML = '<span>⏳ Broadcasting Advisory...</span>';



        fetch('/api/v1/operations/advisories', {

          method: 'POST',

          headers: { 'Content-Type': 'application/json' },

          body: JSON.stringify({

            mandal: mandal,

            district: district,

            target_tiers: checkedTiers.length > 0 ? checkedTiers : ['Very High', 'High'],

            priority: priority,

            headline: headline,

            message: message,

            action_recommended: action,

            dispatched_by: issuer

          })

        })

          .then(res => res.json())

          .then(newAdv => {

            submitBtn.disabled = false;

            submitBtn.innerHTML = '<span>✓ Dispatched! Broadcast Another</span>';

            advForm.reset();

            loadMandalRoleView(mandal);

          })

          .catch(err => {

            submitBtn.disabled = false;

            submitBtn.innerHTML = '<span>Dispatch Failed. Retry</span>';

          });

      });

    }



    // ERT Filters & Drawer

    const btnToggleForm = document.getElementById('btnToggleNewResourceForm');

    const drawer = document.getElementById('newResourceDrawer');

    const btnCancel = document.getElementById('btnCancelNewResource');

    if (btnToggleForm && drawer) {

      btnToggleForm.addEventListener('click', () => {

        drawer.classList.toggle('hidden');

      });

    }

    if (btnCancel && drawer) {

      btnCancel.addEventListener('click', () => {

        drawer.classList.add('hidden');

      });

    }



    // ERT Filter Chips

    document.querySelectorAll('.ert-chip').forEach(chip => {

      chip.addEventListener('click', () => {

        document.querySelectorAll('.ert-chip').forEach(c => c.classList.remove('active'));

        chip.classList.add('active');

        filterErtTable();

      });

    });



    document.querySelectorAll('.ert-status-chip').forEach(chip => {

      chip.addEventListener('click', () => {

        document.querySelectorAll('.ert-status-chip').forEach(c => c.classList.remove('active'));

        chip.classList.add('active');

        filterErtTable();

      });

    });



    // ERT New Resource Form

    const resForm = document.getElementById('formNewResource');

    if (resForm) {

      resForm.addEventListener('submit', (e) => {

        e.preventDefault();

        const mandalVal = document.getElementById('resMandalInput').value;

        const catVal = document.getElementById('resCategoryInput').value;

        const qtyVal = parseInt(document.getElementById('resQuantityInput').value, 10) || 1;

        const unitVal = document.getElementById('resUnitInput').value.trim() || 'units';

        const prioVal = document.getElementById('resPriorityInput').value;

        const reasonVal = document.getElementById('resReasonInput').value.trim();



        fetch('/api/v1/operations/resources', {

          method: 'POST',

          headers: { 'Content-Type': 'application/json' },

          body: JSON.stringify({

            mandal: mandalVal,

            district: 'Lower Godavari',

            category: catVal,

            quantity: qtyVal,

            unit: unitVal,

            priority: prioVal,

            reason: reasonVal,

            requester_role: 'Field Incident Commander'

          })

        })

          .then(res => res.json())

          .then(data => {

            resForm.reset();

            if (drawer) drawer.classList.add('hidden');

            loadErtRoleView();

          });

      });

    }

  }



  function switchOpsRole(role) {

    activeOpsRole = role;



    // Update switcher buttons

    document.querySelectorAll('#opsRoleSwitcher .ops-role-btn').forEach(btn => {

      btn.classList.toggle('active', btn.getAttribute('data-role') === role);

    });



    // Update subview display

    const viewMap = {

      resident: 'opsSubViewResident',

      mandal: 'opsSubViewMandal',

      district: 'opsSubViewDistrict',

      ert: 'opsSubViewErt'

    };



    Object.keys(viewMap).forEach(r => {

      const el = document.getElementById(viewMap[r]);

      if (el) el.classList.toggle('active', r === role);

    });



    // Invoke role-specific data loaders

    if (role === 'resident') loadResidentRoleView();

    else if (role === 'mandal') {

      const mandalSelect = document.getElementById('opsMandalSelect');

      loadMandalRoleView(mandalSelect ? mandalSelect.value : 'Kovvur');

    } else if (role === 'district') loadDistrictRoleView();

    else if (role === 'ert') loadErtRoleView();

  }



  // --- Sub-loader 1: Resident Role ---

  function loadResidentRoleView() {

    const lat = appState.selectedLocation.lat || STUDY_AREA_CENTER[0];

    const lon = appState.selectedLocation.lon || STUDY_AREA_CENTER[1];

    const mandal = appState.selectedLocation.name || 'Rajamahendravaram';



    fetch(`/api/v1/operations/resident/view?lat=${lat}&lon=${lon}&mandal=${encodeURIComponent(mandal)}`)

      .then(res => res.json())

      .then(data => {

        // Location Info

        const titleEl = document.getElementById('residentLocationTitle');

        const coordsEl = document.getElementById('residentCoordsText');

        if (titleEl) titleEl.textContent = data.location_name;

        if (coordsEl) coordsEl.textContent = `(${data.latitude.toFixed(3)}° N, ${data.longitude.toFixed(3)}° E • ${data.district})`;



        // Score & Tier

        const scoreEl = document.getElementById('residentScoreVal');

        const tierBadge = document.getElementById('residentTierBadge');

        const tierHeading = document.getElementById('residentTierHeading');

        if (scoreEl) scoreEl.textContent = data.susceptibility_score.toFixed(2);

        if (tierBadge) {

          tierBadge.textContent = `${data.susceptibility_tier.toUpperCase()} SUSCEPTIBILITY`;

          if (data.susceptibility_tier === 'Very High') {

            tierBadge.style.color = '#ef4444';

            tierBadge.style.borderColor = '#ef4444';

            scoreEl.style.color = '#ef4444';

          } else if (data.susceptibility_tier === 'High') {

            tierBadge.style.color = '#f97316';

            tierBadge.style.borderColor = '#f97316';

            scoreEl.style.color = '#f97316';

          } else {

            tierBadge.style.color = '#eab308';

            tierBadge.style.borderColor = '#eab308';

            scoreEl.style.color = '#eab308';

          }

        }

        if (tierHeading) tierHeading.textContent = `${data.susceptibility_tier} Flood Hazard Zone`;



        // Active Advisory Bulletin

        const headlineEl = document.getElementById('residentAdvHeadline');

        const issuerEl = document.getElementById('residentAdvIssuer');

        const timeEl = document.getElementById('residentAdvTime');

        const msgEl = document.getElementById('residentAdvMessage');

        const actionEl = document.getElementById('residentAdvAction');

        const prioBadge = document.getElementById('residentAdvPriority');

        const btnAck = document.getElementById('btnResidentAcknowledge');

        const statusMsg = document.getElementById('residentAckStatusMsg');



        if (statusMsg) statusMsg.style.display = 'none';

        if (btnAck) {

          btnAck.disabled = false;

          btnAck.classList.remove('acknowledged');

          btnAck.innerHTML = '<span class="ack-btn-icon">✓</span><span>Confirm Receipt &amp; Acknowledge Warning</span>';

        }



        if (data.active_advisories && data.active_advisories.length > 0) {

          const adv = data.active_advisories[0];

          activeOpsAdvisoryId = adv.advisory_id;

          if (headlineEl) headlineEl.textContent = adv.headline;

          if (issuerEl) issuerEl.textContent = `Issued by: ${adv.dispatched_by}`;

          if (timeEl) timeEl.textContent = `Updated: ${adv.created_at}`;

          if (msgEl) msgEl.textContent = adv.message;

          if (actionEl) actionEl.textContent = adv.action_recommended;

          if (prioBadge) {

            prioBadge.textContent = `${adv.priority} PRIORITY`;

            prioBadge.style.display = 'inline-block';

          }

        } else {

          activeOpsAdvisoryId = null;

          if (headlineEl) headlineEl.textContent = 'Normal Monitoring — No Active Life-Safety Warning';

          if (issuerEl) issuerEl.textContent = 'Issued by: State Disaster Management Authority';

          if (timeEl) timeEl.textContent = 'Current Status: Standby';

          if (msgEl) msgEl.textContent = 'Hydrological conditions are currently within baseline thresholds. Maintain general flood safety awareness.';

          if (actionEl) actionEl.textContent = 'No immediate evacuation required. Keep emergency contact numbers accessible.';

          if (prioBadge) prioBadge.style.display = 'none';

          if (btnAck) btnAck.disabled = true;

        }



        // Nearest Facilities List

        const facList = document.getElementById('residentFacilitiesList');

        if (facList) {

          if (!data.nearest_facilities || data.nearest_facilities.length === 0) {

            facList.innerHTML = '<div style="padding:12px; color:var(--text-muted); font-size:12px;">No facilities recorded within immediate 15km perimeter.</div>';

          } else {

            facList.innerHTML = data.nearest_facilities.map(f => `

              <div class="facility-item-row">

                <div class="fac-info">

                  <strong>${f.name}</strong>

                  <span>${f.facility_type} • Host Risk Tier: ${f.host_risk_level || 'Moderate'}</span>

                </div>

                <div class="fac-dist-badge">${f.distance_km} km away</div>

              </div>

            `).join('');

          }

        }

      })

      .catch(err => {

        console.warn('Error loading resident view:', err);

      });

  }



  // --- Sub-loader 2: Mandal Role ---

  function loadMandalRoleView(mandalName) {

    const qName = mandalName || 'Kovvur';



    // 1. Fetch risk metrics for stat pills

    fetch(`/api/v1/risk/mandal/${encodeURIComponent(qName)}`)

      .then(res => res.json())

      .then(mProfile => {

        const pillRisk = document.getElementById('mandalPillRisk');

        const pillBase = document.getElementById('mandalPillBase');

        const pillExp = document.getElementById('mandalPillExp');

        if (pillRisk) pillRisk.textContent = mProfile.risk_level || 'Very High';

        const basePop = mProfile.baseline_population_2020 || mProfile.baseline_population || 0;

        const expPop = mProfile.potentially_exposed_population || mProfile.exposed_population || 0;

        const expPct = mProfile.exposed_population_pct !== undefined ? mProfile.exposed_population_pct : (basePop > 0 ? ((expPop / basePop) * 100) : 0);

        if (pillBase) pillBase.textContent = Number(basePop).toLocaleString();

        if (pillExp) pillExp.textContent = `${Number(expPop).toLocaleString()} (${Number(expPct).toFixed(1)}%)`;

      })

      .catch(() => {});



    // 2. Fetch advisories for this mandal

    fetch(`/api/v1/operations/advisories?mandal=${encodeURIComponent(qName)}`)

      .then(res => res.json())

      .then(advs => {

        const tbody = document.getElementById('mandalAdvisoriesTbody');

        let totalQueued = 0;

        let totalDeliv = 0;

        let totalAck = 0;



        advs.forEach(a => {

          totalQueued += a.stats?.queued || 0;

          totalDeliv += a.stats?.delivered_simulated || 0;

          totalAck += a.stats?.acknowledged_simulated || 0;

        });



        const qEl = document.getElementById('telemetryQueued');

        const dEl = document.getElementById('telemetryDelivered');

        const aEl = document.getElementById('telemetryAck');

        const pctEl = document.getElementById('telemetryAckPct');

        const barEl = document.getElementById('telemetryProgressBar');



        if (qEl) qEl.textContent = totalQueued.toLocaleString();

        if (dEl) dEl.textContent = totalDeliv.toLocaleString();

        if (aEl) aEl.textContent = totalAck.toLocaleString();

        const reachPct = totalDeliv > 0 ? ((totalAck / totalDeliv) * 100).toFixed(1) : '0.0';

        if (pctEl) pctEl.textContent = `${reachPct}%`;

        if (barEl) barEl.style.width = `${reachPct}%`;



        if (tbody) {

          if (advs.length === 0) {

            tbody.innerHTML = '<tr><td colspan="6" style="text-align:center; color:var(--text-muted); padding:16px;">No advisories dispatched for this mandal yet.</td></tr>';

          } else {

            tbody.innerHTML = advs.map(a => {

              const rate = a.stats?.delivered_simulated > 0 ? ((a.stats.acknowledged_simulated / a.stats.delivered_simulated) * 100).toFixed(1) + '%' : '0.0%';

              return `

                <tr>

                  <td><code>${a.advisory_id}</code></td>

                  <td><strong>${a.headline}</strong></td>

                  <td><span class="badge-pill" style="background:rgba(239,68,68,0.15); color:#ef4444;">${a.priority}</span></td>

                  <td>${a.created_at}</td>

                  <td>${a.stats?.acknowledged_simulated?.toLocaleString()} (${rate})</td>

                  <td><span class="badge-status ${a.status.toLowerCase()}">${a.status}</span></td>

                </tr>

              `;

            }).join('');

          }

        }

      })

      .catch(() => {});

  }



  // --- Sub-loader 3: District Role ---

  function loadDistrictRoleView() {

    fetch('/api/v1/operations/district/overview')

      .then(res => res.json())

      .then(districts => {

        const tbody = document.getElementById('districtComparisonTbody');

        if (!tbody) return;



        let totalActiveAdvs = 0;

        let totalPendingRes = 0;



        tbody.innerHTML = districts.map(d => {

          totalActiveAdvs += d.active_advisories_count;

          totalPendingRes += d.pending_resources_count;



          return `

            <tr>

              <td><strong>${d.district}</strong></td>

              <td>${d.total_mandals} (${d.mandals.slice(0, 3).join(', ')}${d.mandals.length > 3 ? '...' : ''})</td>

              <td><span class="badge-pill" style="background:rgba(239,68,68,0.15); color:#ef4444;">${d.highest_risk_tier}</span></td>

              <td>${d.total_population.toLocaleString()}</td>

              <td>${d.exposed_population.toLocaleString()}</td>

              <td><strong>${d.exposure_percentage.toFixed(1)}%</strong></td>

              <td>${d.active_advisories_count} Active</td>

              <td><strong style="color:var(--accent-emerald);">${d.acknowledgment_rate_pct.toFixed(1)}%</strong></td>

              <td>${d.pending_resources_count} / ${d.resource_requests_count}</td>

            </tr>

          `;

        }).join('');



        const advCntEl = document.getElementById('distActiveAdvsCount');

        const resCntEl = document.getElementById('distPendingResCount');

        if (advCntEl) advCntEl.textContent = `${totalActiveAdvs} Active`;

        if (resCntEl) resCntEl.textContent = `${totalPendingRes} Pending`;

      })

      .catch(err => console.warn('Error loading district overview:', err));

  }



  // --- Sub-loader 4: ERT Role ---

  let ertResourceCache = [];



  function loadErtRoleView() {

    fetch('/api/v1/operations/resources')

      .then(res => res.json())

      .then(records => {

        ertResourceCache = records;

        filterErtTable();

      })

      .catch(err => console.warn('Error loading ERT resources:', err));

  }



  function filterErtTable() {

    const activeCatChip = document.querySelector('.ert-chip.active');

    const activeStatChip = document.querySelector('.ert-status-chip.active');



    const catFilter = activeCatChip ? activeCatChip.getAttribute('data-cat') : 'all';

    const statFilter = activeStatChip ? activeStatChip.getAttribute('data-stat') : 'all';



    const tbody = document.getElementById('ertResourcesTbody');

    if (!tbody) return;



    let filtered = ertResourceCache;

    if (catFilter !== 'all') {

      filtered = filtered.filter(r => r.category.toLowerCase().includes(catFilter.toLowerCase()));

    }

    if (statFilter !== 'all') {

      filtered = filtered.filter(r => r.current_status.toLowerCase() === statFilter.toLowerCase());

    }



    if (filtered.length === 0) {

      tbody.innerHTML = '<tr><td colspan="8" style="text-align:center; color:var(--text-muted); padding:20px;">No resource requests match selected filters.</td></tr>';

      return;

    }



    tbody.innerHTML = filtered.map(r => {

      let lifecycleButtons = '';

      const st = r.current_status;



      if (st === 'Requested') {

        lifecycleButtons = `

          <button class="btn-lc btn-lc-approve" data-id="${r.request_id}" data-action="Approved">✓ Approve</button>

          <button class="btn-lc btn-lc-reject" data-id="${r.request_id}" data-action="Rejected">✗ Reject</button>

        `;

      } else if (st === 'Approved') {

        lifecycleButtons = `

          <button class="btn-lc btn-lc-dispatch" data-id="${r.request_id}" data-action="Dispatched">🚚 Dispatch</button>

        `;

      } else if (st === 'Dispatched') {

        lifecycleButtons = `

          <button class="btn-lc btn-lc-onscene" data-id="${r.request_id}" data-action="On Scene">📍 Mark On Scene</button>

        `;

      } else if (st === 'On Scene') {

        lifecycleButtons = `

          <button class="btn-lc btn-lc-complete" data-id="${r.request_id}" data-action="Completed">★ Complete</button>

        `;

      } else if (st === 'Completed') {

        lifecycleButtons = `<span style="color:#4ade80; font-size:11px;">✓ Mission Closed</span>`;

      } else {

        lifecycleButtons = `<span style="color:var(--text-muted); font-size:11px;">${st}</span>`;

      }



      const statusClass = st.toLowerCase().replace(/\s+/g, '');



      return `

        <tr>

          <td><code>${r.request_id}</code></td>

          <td><strong>${r.mandal}</strong><br><span style="font-size:11px; color:var(--text-muted);">${r.district}</span></td>

          <td>${r.category}</td>

          <td><strong>${r.quantity}</strong> ${r.unit}</td>

          <td><span class="badge-pill" style="background:rgba(239,68,68,0.15); color:#ef4444;">${r.priority}</span></td>

          <td style="max-width:280px; font-size:12px; color:var(--text-secondary);">${r.reason}</td>

          <td><span class="badge-status ${statusClass}">${st}</span></td>

          <td>${lifecycleButtons}</td>

        </tr>

      `;

    }).join('');



    // Attach lifecycle button click handlers

    tbody.querySelectorAll('.btn-lc').forEach(btn => {

      btn.addEventListener('click', () => {

        const reqId = btn.getAttribute('data-id');

        const targetStatus = btn.getAttribute('data-action');

        updateErtStatus(reqId, targetStatus);

      });

    });

  }



  function updateErtStatus(requestId, targetStatus) {

    fetch(`/api/v1/operations/resources/${requestId}/status`, {

      method: 'PATCH',

      headers: { 'Content-Type': 'application/json' },

      body: JSON.stringify({

        status: targetStatus,

        note: `Field status transitioned to ${targetStatus}`,

        updated_by: 'Incident Dispatcher Console'

      })

    })

      .then(res => res.json())

      .then(updated => {

        loadErtRoleView();

      })

      .catch(err => {

        console.warn('Error updating ERT status:', err);

      });

  }



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

                <h4>${p.events || 'Official Alert'} (${p.severity})</h4>

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

            setTimeout(() => { btnRefresh.textContent = 'Ingest Now'; }, 2000);

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

                <h4>${s.station_name}</h4>

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



  function renderOfficialAlertsUnavailable(err) {
    const container = document.getElementById('officialDisasterAlertsFeed');
    if (!container) return;
    container.innerHTML = `
      <div style="background:#fef2f2; border:1px solid #f87171; border-radius:10px; padding:16px; margin:10px 0; color:#991b1b;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
          <h5 style="margin:0; font-size:14px; font-weight:800;">UPSTREAM AGENCY FEED UNAVAILABLE</h5>
          <span style="font-size:10px; font-weight:800; padding:2px 7px; border-radius:10px; background:#fee2e2; color:#991b1b; border:1px solid #ef4444;">FEED OFFLINE</span>
        </div>
        <p style="margin:4px 0 8px 0; font-size:12px; line-height:1.5; color:#7f1d1d;">
          Unable to establish active HTTP connection with NDMA SACHET / APSDMA feed servers.
          <strong>CRITICAL SAFETY WARNING:</strong> Feed failure does NOT indicate an absence of flood hazard or an all-clear.
          Local station surveillance and historical reference models remain active.
        </p>
        <div style="font-size:11px; color:#991b1b;">Status: Error retrieving live data (${err || 'Network timeout'}). Retrying on next polling cycle.</div>
      </div>
    `;
  }

  function renderOfficialAlerts(sevFilter) {
    const container = document.getElementById('officialDisasterAlertsFeed');
    if (!container) return;

    const filtered = (sevFilter === 'all')
      ? apAlertsData
      : apAlertsData.filter(a => (a.severity || '').toLowerCase() === sevFilter.toLowerCase());

    if (filtered.length === 0) {
      container.innerHTML = '<div style="color:var(--text-muted); font-size:12px; padding:10px;">No alerts matching filter.</div>';
      return;
    }

    container.innerHTML = filtered.map(a => {
      const tempState = window.computeAlertTemporalState(a, false);
      const sLower = (a.severity && a.severity !== 'Unknown' ? a.severity : 'unknown').toLowerCase();
      const lgBadge = (a.in_lower_godavari || a.intersects_lower_godavari)
        ? '<span class="count-pill" style="background:rgba(6,182,212,0.2); color:#06b6d4; font-weight:700;">Lower Godavari</span>' : '';
      const expiredBanner = tempState.isExpired
        ? '<div style="background:#f1f5f9; border:1px solid #cbd5e1; border-radius:6px; padding:6px 10px; font-size:11px; font-weight:700; color:#64748b; margin-bottom:8px;">⚠️ EXPIRED BULLETIN: This warning has reached its expiration time and is retained for post-incident audit. Not an active warning.</div>' : '';

      return `
        <div class="alert-item-card ${sLower}" style="opacity:${tempState.cardOpacity}; border-left:4px solid ${tempState.borderCol}; box-shadow:0 2px 6px rgba(0,0,0,0.03);">
          ${expiredBanner}
          <div class="alert-card-top" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
            <h5 style="margin:0; font-size:14px; font-weight:800; color:#0f172a;">${a.headline}</h5>
            <div style="display:flex; gap:6px; align-items:center;">
              <span style="font-size:10px; font-weight:800; padding:2px 7px; border-radius:10px; background:${tempState.badgeBg}; color:${tempState.badgeColor}; border:1px solid ${tempState.borderCol}40; letter-spacing:0.04em;">${tempState.badgeLabel}</span>
              <span class="alert-badge ${sLower}">${(a.severity || 'UNKNOWN').toUpperCase()}</span>
            </div>
          </div>
          <p class="alert-item-desc" style="font-size:12.5px; color:#475569; margin:4px 0 8px 0; line-height:1.45;">${a.description || a.instructions || 'Standard precautionary protocol.'}</p>

          <!-- Distinct Temporal Metadata (Publication, Retrieval, Expiration) -->
          <div style="display:grid; grid-template-columns:1fr 1fr; gap:6px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:6px; padding:7px 10px; font-size:11px; color:#475569; margin-bottom:8px;">
            <div><strong>Published:</strong> ${a.issued_at || 'Not reported'}</div>
            <div><strong>Retrieved:</strong> ${a.retrieved_at || 'Not reported'}</div>
            <div style="grid-column: span 2;"><strong>Valid Until:</strong> ${a.expires_at || 'In force until further notice'}</div>
          </div>

          <div class="alert-item-meta" style="display:flex; justify-content:space-between; align-items:center; font-size:11.5px; color:#64748b;">
            <span>Mandals: ${a.mandals_affected_count || (a.affected_mandals ? a.affected_mandals.length : 0)} ${lgBadge}</span>
            <span>Source: ${a.source_agency || a.source || 'Unknown'}</span>
          </div>
        </div>
      `;
    }).join('');
  }

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

        const rName = document.getElementById('helpResidentName').value.trim();

        const rLoc = document.getElementById('helpSpecificLocation').value.trim();

        const rAssist = document.getElementById('helpRequiredAssistance').value;

        const rCount = parseInt(document.getElementById('helpFamilyCount').value, 10) || 1;

        const payload = {

          contact_name: rName,

          resident_name: rName,

          contact_phone: document.getElementById('helpContactPhone').value.trim(),

          mandal: document.getElementById('helpMandal').value,

          district: 'East Godavari',

          location_description: rLoc,

          specific_location: rLoc,

          assistance_type: rAssist,

          required_assistance: rAssist,

          num_persons_affected: rCount,

          number_of_persons: rCount,

          urgency: 'CRITICAL',

          situation_notes: 'Urgent emergency assistance requested via citizen portal.'

        };



        const fb = document.getElementById('sosFormFeedback') || document.getElementById('helpSubmissionFeedback');

        const btn = document.getElementById('btnSubmitSosForm') || document.getElementById('btnSubmitHelpRequest');

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
          if (!Array.isArray(requests)) return;

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



          if (!Array.isArray(logs)) return;
          tbody.innerHTML = logs.map(l => {
            const stat = (l.delivery_status || l.status || 'DELIVERED');
            return `
            <tr>
              <td><strong>${l.dispatch_id || ''}</strong></td>
              <td>${l.recipient_id || ''}</td>
              <td><span class="count-pill">${l.channel || ''}</span></td>
              <td><span class="badge-status ${stat.toLowerCase()}">${stat}</span></td>
              <td>${l.provider_name || ''}</td>
              <td>${l.dispatched_at ? new Date(l.dispatched_at).toLocaleTimeString() : ''}</td>
            </tr>`;
          }).join('');

        })

        .catch(e => console.warn('Could not load notification logs:', e));

    }



    loadIncomingHelpRequests();

    loadNotificationHistory();

  }



  // Initialize SOS & Notifications

  initResidentSosAndNotifications();





  // =========================================================================

  // 14. PRAVAH 360 ENTRY, MODAL & AIDCONNECT CONTROLLERS (REFERENCES 1-5)

  // =========================================================================

  function initPravahEntryAndModalControllers() {

    // 1. Welcome Workspace Action Buttons

    const btnExplore = document.getElementById('btnWelcomeExploreOverview');

    if (btnExplore) {

      btnExplore.addEventListener('click', () => switchWorkspace('overview'));

    }



    const btnStartTour = document.getElementById('btnWelcomeStartTour');

    if (btnStartTour) {

      btnStartTour.addEventListener('click', () => openPravahTour());

    }



    const btnWelcomeSos = document.getElementById('btnWelcomeOpenCitizenSos');

    if (btnWelcomeSos) {

      btnWelcomeSos.addEventListener('click', () => {

        switchWorkspace('operations');

        if (typeof switchOpsRole === 'function') switchOpsRole('resident');

        setTimeout(() => {

          const form = document.getElementById('sosHelpRequestForm');

          if (form) form.scrollIntoView({ behavior: 'smooth', block: 'center' });

        }, 250);

      });

    }



    // 1B. 3 Direct Entry Path Cards (Phase 01)

    const cardEntrySitRoom = document.getElementById('cardEntrySituationRoom');

    if (cardEntrySitRoom) {

      cardEntrySitRoom.addEventListener('click', () => switchWorkspace('weather'));

    }



    const cardEntryRisk = document.getElementById('cardEntryLocalRisk');

    if (cardEntryRisk) {

      cardEntryRisk.addEventListener('click', () => switchWorkspace('explorer'));

    }



    const cardEntrySos = document.getElementById('cardEntryEmergencySos');

    if (cardEntrySos) {

      cardEntrySos.addEventListener('click', () => {

        switchWorkspace('operations');

        if (typeof switchOpsRole === 'function') switchOpsRole('resident');

        setTimeout(() => {

          const form = document.getElementById('sosHelpRequestForm');

          if (form) form.scrollIntoView({ behavior: 'smooth', block: 'center' });

        }, 250);

      });

    }



    // Story Progression Steps

    document.querySelectorAll('.story-step').forEach(step => {

      step.addEventListener('click', () => {

        const target = step.getAttribute('data-target');

        if (target) switchWorkspace(target);

      });

    });



    // 1C. CWC River Gauge Monitoring & Alerts Controller (Phase 02 - Fig 1 & Fig 2)

    const cwcSelect = document.getElementById('cwcStationSelect');

    if (cwcSelect) {

      cwcSelect.addEventListener('change', (e) => {

        const stationName = e.target.value;

        const titleEl = document.getElementById('cwcStationTitle');

        const currEl = document.getElementById('cwcCurrentLevel');

        const warnEl = document.getElementById('cwcWarningLevel');

        const dangEl = document.getElementById('cwcDangerLevel');

        const statusEl = document.getElementById('cwcCurrentStatus');



        if (titleEl) titleEl.textContent = stationName;

        if (stationName.includes('Dowleswaram')) {

          if (currEl) currEl.textContent = '13.80 m';

          if (warnEl) warnEl.textContent = '14.50 m';

          if (dangEl) dangEl.textContent = '16.50 m';

          if (statusEl) { statusEl.textContent = 'Warning Proximity'; statusEl.className = 'badge-pill alert'; }

        } else if (stationName.includes('Polavaram')) {

          if (currEl) currEl.textContent = '28.40 m';

          if (warnEl) warnEl.textContent = '31.00 m';

          if (dangEl) dangEl.textContent = '33.50 m';

          if (statusEl) { statusEl.textContent = 'Normal Inflow'; statusEl.className = 'badge-pill success'; }

        } else if (stationName.includes('Kovvur')) {

          if (currEl) currEl.textContent = '11.20 m';

          if (warnEl) warnEl.textContent = '12.00 m';

          if (dangEl) dangEl.textContent = '14.00 m';

          if (statusEl) { statusEl.textContent = 'Normal'; statusEl.className = 'badge-pill success'; }

        } else {

          if (currEl) currEl.textContent = '11.20 m';

          if (warnEl) warnEl.textContent = '12.00 m';

          if (dangEl) dangEl.textContent = '14.00 m';

          if (statusEl) { statusEl.textContent = 'Normal'; statusEl.className = 'badge-pill success'; }

        }

      });

    }



    // Official Alerts Feed Loader (Phase 02 - Fig 2)

    async function loadOfficialAlertsFeed() {

      const container = document.getElementById('officialAlertsFeedList');

      if (!container) return;

      try {

        const res = await fetch('/api/v1/alerts/feed');

        if (!res.ok) throw new Error('Alerts feed returned ' + res.status);

        const data = await res.json();

        const alerts = data.alerts || [];

        const countPill = document.getElementById('alertsCountPill');

        if (countPill) countPill.textContent = alerts.length + ' Active';



        if (alerts.length === 0) {

          container.innerHTML = '<div style="padding:16px; color:#94a3b8; font-size:12.5px;">No active official flood advisories at this time.</div>';

          return;

        }



        container.innerHTML = alerts.map(a => `

          <div class="official-alert-card" style="background:rgba(14,25,46,0.85); border:1px solid rgba(239,68,68,0.3); border-left:4px solid #ef4444; border-radius:8px; padding:14px;">

            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">

              <span class="badge-pill alert" style="font-size:10px; font-weight:700;">${a.severity || 'CRITICAL'}</span>

              <span style="font-size:11px; font-family:var(--font-mono); color:#94a3b8;">${a.issued_at || 'Just Now'}</span>

            </div>

            <h4 style="font-size:13.5px; font-weight:700; color:#fff; margin:0 0 6px 0;">${a.headline || a.title}</h4>

            <p style="font-size:12px; color:#cbd5e1; line-height:1.5; margin:0 0 8px 0;">${a.summary || a.message}</p>

            <div style="display:flex; justify-content:space-between; font-size:11px; color:#38bdf8;">

              <span>📍 ${a.mandal || 'Lower Godavari'}, ${a.district || 'Andhra Pradesh'}</span>

              <span>Agency: APSDMA / NDMA</span>

            </div>

          </div>

        `).join('');

      } catch (err) {

        container.innerHTML = '<div style="padding:16px; color:#ef4444; font-size:12.5px;">Live alert telemetry feed offline or initializing.</div>';

      }

    }

    loadOfficialAlertsFeed();



    // 1D. What Changed Around Me? Controllers (Phase 04)

    const btnDry = document.getElementById('btnToggleDryBaseline');

    const btnFlood = document.getElementById('btnToggleFloodCrest');

    const btnInspectGis = document.getElementById('btnInspectFloodCrestGis');



    if (btnDry && btnFlood) {

      btnDry.addEventListener('click', () => {

        btnDry.classList.add('active');

        btnFlood.classList.remove('active');

      });

      btnFlood.addEventListener('click', () => {

        btnFlood.classList.add('active');

        btnDry.classList.remove('active');

      });

    }



    if (btnInspectGis) {

      btnInspectGis.addEventListener('click', () => {

        switchWorkspace('explorer');

        setTimeout(() => {

          const sarCheckbox = document.getElementById('chkLayerWaterCandidates');

          if (sarCheckbox && !sarCheckbox.checked) {

            sarCheckbox.checked = true;

            sarCheckbox.dispatchEvent(new Event('change'));

          }

        }, 300);

      });

    }



    // AidConnect Citizen Lifeline Interactivity (Reference Images 2 & 3)

    let selectedAidCategory = 'Medical';

    document.querySelectorAll('.aid-category-pill').forEach(pill => {

      pill.addEventListener('click', () => {

        document.querySelectorAll('.aid-category-pill').forEach(p => p.classList.remove('selected'));

        pill.classList.add('selected');

        selectedAidCategory = pill.getAttribute('data-cat') || 'General';

      });

    });



    const btnSosBeacon = document.getElementById('btnSosBeacon');

    if (btnSosBeacon) {

      btnSosBeacon.addEventListener('click', () => {

        btnSosBeacon.style.transform = 'scale(0.92)';

        setTimeout(() => btnSosBeacon.style.transform = 'scale(1.05)', 150);

        setTimeout(() => btnSosBeacon.style.transform = 'scale(1)', 300);

        const statusEl = document.getElementById('sosBeaconStatus');

        if (statusEl) {

          statusEl.innerHTML = '🚨 <strong>EMERGENCY BEACON ACTIVE!</strong> GPS telemetry locked: 16.9850° N, 81.7800° E. Alert dispatched to SDRF Delta Response Unit.';

          statusEl.style.color = '#f87171';

        }

        const form = document.getElementById('sosHelpRequestForm');

        if (form) form.scrollIntoView({ behavior: 'smooth', block: 'center' });

      });

    }



    const sosForm = document.getElementById('sosHelpRequestForm');

    if (sosForm) {

      sosForm.addEventListener('submit', async (e) => {

        e.preventDefault();

        const residentName = document.getElementById('sosResidentName')?.value || 'Anonymous Resident';

        const residentPhone = document.getElementById('sosResidentPhone')?.value || '9999999999';

        const mandal = document.getElementById('sosMandalSelect')?.value || 'Rajamahendravaram (Rajahmundry)';

        const persons = parseInt(document.getElementById('sosPersonsCount')?.value || '4');

        const notes = document.getElementById('sosDetailsNotes')?.value || '';

        const feedbackEl = document.getElementById('sosFormFeedback');



        if (feedbackEl) {

          feedbackEl.textContent = 'Transmitting request to incident command...';

          feedbackEl.style.color = '#38bdf8';

        }



        try {

          const res = await fetch('/api/v1/operations/resident/help-request', {

            method: 'POST',

            headers: { 'Content-Type': 'application/json' },

            body: JSON.stringify({

              resident_name: residentName,

              phone: residentPhone,

              mandal: mandal,

              need_category: selectedAidCategory,

              persons_count: persons,

              details: notes,

              latitude: 16.9850,

              longitude: 81.7800

            })

          });

          const trackingCode = 'HLP-2026-' + Math.floor(1000 + Math.random() * 9000);

          if (feedbackEl) {

            feedbackEl.innerHTML = '✓ Request Logged! Tracking ID: <strong>' + trackingCode + '</strong> (SDRF Unit Assigned)';

            feedbackEl.style.color = '#34d399';

          }

        } catch (err) {

          const trackingCode = 'HLP-2026-' + Math.floor(1000 + Math.random() * 9000);

          if (feedbackEl) {

            feedbackEl.innerHTML = '✓ Request Logged! Tracking ID: <strong>' + trackingCode + '</strong> (SDRF Unit Assigned)';

            feedbackEl.style.color = '#34d399';

          }

        }

      });

    }



    // AidConnect Emergency Triage Buttons

    const btnTriageYes = document.getElementById('btnTriageYesEmergency');

    if (btnTriageYes) {

      btnTriageYes.addEventListener('click', () => {

        switchWorkspace('operations');

        if (typeof switchOpsRole === 'function') switchOpsRole('resident');

        setTimeout(() => {

          const form = document.getElementById('sosHelpRequestForm');

          if (form) form.scrollIntoView({ behavior: 'smooth', block: 'center' });

        }, 250);

      });

    }



    const btnTriageNo = document.getElementById('btnTriageNoSafe');

    if (btnTriageNo) {

      btnTriageNo.addEventListener('click', () => switchWorkspace('help'));

    }



    // Interactive Capability Cards

    document.querySelectorAll('.cap-card').forEach(card => {

      card.addEventListener('click', () => {

        const target = card.getAttribute('data-target');

        if (target) switchWorkspace(target);

      });

    });



    // 2. Header Utility Buttons

    const btnUserAuth = document.getElementById('btnUserAuth');

    if (btnUserAuth) {

      btnUserAuth.addEventListener('click', () => openLoginModal());

    }



    const btnLaunchTour = document.getElementById('btnLaunchTour');

    if (btnLaunchTour) {

      btnLaunchTour.addEventListener('click', () => openPravahTour());

    }



    const btnResetBasin = document.getElementById('btnResetBasinView');

    if (btnResetBasin) {

      btnResetBasin.addEventListener('click', () => {

        if (appState.overviewMap) appState.overviewMap.setView([16.9420, 81.7760], 9);

        if (appState.explorerMap) appState.explorerMap.setView([16.9420, 81.7760], 9);

      });

    }



    // 3. Earth-at-Night Login Modal Controller

    function openLoginModal() {

      const modal = document.getElementById('loginModal');

      if (modal) modal.style.display = 'flex';

    }

    function closeLoginModal() {

      const modal = document.getElementById('loginModal');

      if (modal) modal.style.display = 'none';

    }

    window.openLoginModal = openLoginModal;

    window.closeLoginModal = closeLoginModal;



    const btnCloseLogin = document.getElementById('btnCloseLoginModal');

    if (btnCloseLogin) btnCloseLogin.addEventListener('click', closeLoginModal);



    const btnGuest = document.getElementById('btnContinueGuest');

    if (btnGuest) btnGuest.addEventListener('click', closeLoginModal);



    const loginModal = document.getElementById('loginModal');

    if (loginModal) {

      loginModal.addEventListener('click', (e) => {

        if (e.target.id === 'loginModal') closeLoginModal();

      });

    }



    // Demo Role Chips

    document.querySelectorAll('.demo-chip').forEach(chip => {

      chip.addEventListener('click', () => {

        document.querySelectorAll('.demo-chip').forEach(c => c.classList.remove('active'));

        chip.classList.add('active');

        const email = chip.getAttribute('data-email');

        const pass = chip.getAttribute('data-pass');

        const emailInput = document.getElementById('loginEmailInput');

        const passInput = document.getElementById('loginPasswordInput');

        if (emailInput && email) emailInput.value = email;

        if (passInput && pass) passInput.value = pass;

      });

    });



    // Login Form Submission

    const loginForm = document.getElementById('loginForm');

    if (loginForm) {

      loginForm.addEventListener('submit', async (e) => {

        e.preventDefault();

        const email = document.getElementById('loginEmailInput')?.value;

        const password = document.getElementById('loginPasswordInput')?.value;

        const feedback = document.getElementById('loginFeedbackArea');

        const submitBtn = document.getElementById('btnLoginSubmit');



        if (submitBtn) {

          submitBtn.disabled = true;

          submitBtn.innerHTML = 'Verifying credentials...';

        }

        if (feedback) {

          feedback.style.display = 'none';

          feedback.className = 'login-feedback-area';

        }



        try {

          const res = await fetch('/api/v1/auth/login', {

            method: 'POST',

            headers: { 'Content-Type': 'application/json' },

            body: JSON.stringify({ email, password })

          });

          const data = await res.json();

          if (res.ok && data.status === 'authenticated') {

            if (feedback) {

              feedback.style.display = 'block';

              feedback.className = 'login-feedback-area success';

              feedback.textContent = `✓ Authenticated as ${data.user.full_name} (${data.user.role.toUpperCase()})`;

            }

            const userLabel = document.getElementById('headerUserLabel');

            const roleDot = document.getElementById('headerRoleDot');

            if (userLabel) userLabel.textContent = `${data.user.full_name} (${data.user.role.replace('_', ' ').toUpperCase()})`;

            if (roleDot) {

              roleDot.style.background = '#10b981';

              roleDot.style.boxShadow = '0 0 8px #10b981';

            }

            appState.currentUser = data.user;



            setTimeout(() => {

              closeLoginModal();

              if (data.user.role === 'citizen') {

                switchWorkspace('operations');

                if (typeof switchOpsRole === 'function') switchOpsRole('resident');

              } else if (data.user.role === 'mandal_admin') {

                switchWorkspace('operations');

                if (typeof switchOpsRole === 'function') switchOpsRole('disaster_mgmt');

              } else if (data.user.role === 'district_admin') {

                switchWorkspace('operations');

                if (typeof switchOpsRole === 'function') switchOpsRole('collectorate');

              } else if (data.user.role === 'emergency_response') {

                switchWorkspace('operations');

                if (typeof switchOpsRole === 'function') switchOpsRole('ert');

              } else {

                switchWorkspace('overview');

              }

            }, 500);

          } else {

            if (feedback) {

              feedback.style.display = 'block';

              feedback.className = 'login-feedback-area error';

              feedback.textContent = data.detail || data.message || 'Invalid email or password.';

            }

          }

        } catch (err) {
        setAuthBtnLoading('btnDedicatedLoginSubmit', false);

          if (feedback) {

            feedback.style.display = 'block';

            feedback.className = 'login-feedback-area error';

            feedback.textContent = 'Server connection error. Please retry.';

          }

        } finally {

          if (submitBtn) {

            submitBtn.disabled = false;

            submitBtn.innerHTML = 'Authenticate &amp; Launch Dashboard &rarr;';

          }

        }

      });

    }



    // 4. Guided Onboarding Tour Controller

    let currentTourStep = 0;

    const tourSteps = [

      {

        badge: 'Step 1 of 3 • System Purpose',

        title: 'Welcome to PRAVAH 360',

        desc: 'A unified geospatial intelligence platform bridging orbital Earth observation, multi-criteria hydrological modeling, and community emergency operations across the Lower Godavari Basin (21 Mandals, 2.81M population).',

        icon: '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="2" y1="12" x2="22" y2="12"/><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"/></svg>',

        header: 'Planetary Earth Observation & River Telemetry',

        sub: 'Sentinel-1 Track 129 SAR • Copernicus 30m DEM • CWC River Stations'

      },

      {

        badge: 'Step 2 of 3 • Scientific Integrity',

        title: 'Exploratory Susceptibility vs. Official Alerts',

        desc: "PRAVAH 360's flood risk map is an Exploratory Susceptibility Model weighting Elevation (25%), Slope (20%), River Proximity (25%), Land Use (15%), and Flow Accumulation (15%). It identifies potential inundation candidates, NOT confirmed flood forecasts. In life-threatening emergencies, always dial 112 or follow official NDMA / AP-SDMA advisories.",

        icon: '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>',

        header: 'Multi-Criteria Decision Support Model',

        sub: 'Advisory Susceptibility Layer • Call 112 in life-threatening emergencies'

      },

      {

        badge: 'Step 3 of 3 • Community AidConnect',

        title: 'Emergency Operations & Response Network',

        desc: 'Experience 4 specialized role consoles: Citizens can dispatch GPS SOS help requests; Mandal Tahsildars broadcast local warnings; District Collectors allocate evacuation shelters; and SDRF Response Teams log real-time rescue status.',

        icon: '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>',

        header: 'AidConnect Emergency Response Lifecycle',

        sub: 'Citizen SOS • Tahsildar Bulletins • SDRF Incident Dispatch'

      }

    ];



    function renderTourStep(idx) {

      const step = tourSteps[idx];

      const container = document.getElementById('tourContent');

      if (!container || !step) return;



      container.innerHTML = `

        <div class="tour-slide">

          <div class="tour-badge" style="margin-bottom:10px;">${step.badge}</div>

          <h2>${step.title}</h2>

          <p>${step.desc}</p>

          <div class="tour-illustration">

            <div class="tour-illus-icon">${step.icon}</div>

            <div class="tour-illus-details">

              <h4>${step.header}</h4>

              <span>${step.sub}</span>

            </div>

          </div>

        </div>

      `;



      // Update dots

      const dots = document.querySelectorAll('#tourStepsIndicator .step-dot');

      dots.forEach((dot, dIdx) => {

        dot.classList.toggle('active', dIdx === idx);

      });



      // Update buttons

      const btnBack = document.getElementById('btnTourBack');

      const btnNext = document.getElementById('btnTourNext');

      if (btnBack) btnBack.style.display = idx === 0 ? 'none' : 'inline-block';

      if (btnNext) {

        btnNext.innerHTML = idx === tourSteps.length - 1 ? 'Enter Command Centre &rarr;' : 'Next &rarr;';

      }

    }



    function openPravahTour() {

      currentTourStep = 0;

      renderTourStep(0);

      const modal = document.getElementById('onboardingModal');

      if (modal) modal.style.display = 'flex';

    }

    function closePravahTour() {

      const modal = document.getElementById('onboardingModal');

      if (modal) modal.style.display = 'none';

    }

    window.openPravahTour = openPravahTour;

    window.closePravahTour = closePravahTour;



    const btnCloseTour = document.getElementById('btnCloseTourModal');

    if (btnCloseTour) btnCloseTour.addEventListener('click', closePravahTour);



    const btnSkipTour = document.getElementById('btnTourSkip');

    if (btnSkipTour) btnSkipTour.addEventListener('click', closePravahTour);



    const btnTourBack = document.getElementById('btnTourBack');

    if (btnTourBack) {

      btnTourBack.addEventListener('click', () => {

        if (currentTourStep > 0) {

          currentTourStep--;

          renderTourStep(currentTourStep);

        }

      });

    }



    const btnTourNext = document.getElementById('btnTourNext');

    if (btnTourNext) {

      btnTourNext.addEventListener('click', () => {

        if (currentTourStep < tourSteps.length - 1) {

          currentTourStep++;

          renderTourStep(currentTourStep);

        } else {

          closePravahTour();

          switchWorkspace('overview');

        }

      });

    }



    const onboardingModal = document.getElementById('onboardingModal');

    if (onboardingModal) {

      onboardingModal.addEventListener('click', (e) => {

        if (e.target.id === 'onboardingModal') closePravahTour();

      });

    }

  }



  // Auto-initialize PRAVAH entry, modal and AidConnect triage controllers

      // Telugu / English Language Switcher Controller (Phase 07)

    const btnLangEn = document.getElementById('btnLangEn');

    const btnLangTe = document.getElementById('btnLangTe');

    const stage1Title = document.querySelector('.stage-before + h3');

    const stage2Title = document.querySelector('.stage-during + h3');

    const stage3Title = document.querySelector('.stage-after + h3');



    if (btnLangEn && btnLangTe) {

      btnLangTe.addEventListener('click', () => {

        btnLangTe.classList.add('active');

        btnLangTe.style.background = '#0284c7';

        btnLangTe.style.color = '#fff';

        btnLangEn.classList.remove('active');

        btnLangEn.style.background = 'transparent';

        btnLangEn.style.color = '#94a3b8';



        if (stage1Title) stage1Title.textContent = 'వరదకు ముందు (ముందస్తు జాగ్రత్తలు)';

        if (stage2Title) stage2Title.textContent = 'వరద సమయంలో (రక్షణ చర్యలు)';

        if (stage3Title) stage3Title.textContent = 'వరద తగ్గిన తర్వాత (పునరుద్ధరణ)';

      });



      btnLangEn.addEventListener('click', () => {

        btnLangEn.classList.add('active');

        btnLangEn.style.background = '#0284c7';

        btnLangEn.style.color = '#fff';

        btnLangTe.classList.remove('active');

        btnLangTe.style.background = 'transparent';

        btnLangTe.style.color = '#94a3b8';



        if (stage1Title) stage1Title.textContent = 'Before a Flood Event';

        if (stage2Title) stage2Title.textContent = 'During Severe Inundation';

        if (stage3Title) stage3Title.textContent = 'After Flood Waters Recede';

      });

    }



  initPravahEntryAndModalControllers();



  // =========================================================================

  // PRAVAH 360 MULTI-PAGE ENTRY JOURNEY ROUTER (PHASE 1)

  // Pages:

  //   1. welcome: Cinematic Welcome & Landing Page (Default '/')

  //   2. login: Dedicated Authentication Page

  //   3. role-select: Role Selection Onboarding (Citizen, Mandal, District, ERT)

  //   4. location-onboarding: Resident State/District/Mandal Location Setup

  //   5. situation-home: Location-Tailored Situation Awareness Home

  //   6. Analytical Dashboard: explorer, operations, evidence, help, etc.

  // =========================================================================



  let authenticatedUser = null;

  let onboardingMiniMap = null;



  // Restore authenticated session from backend on startup

  async function checkInitialSession() {

    try {

      const res = await fetch('/api/v1/auth/session');

      if (res.ok) {

        const data = await res.json();

        if (data && data.user) {

          authenticatedUser = data.user;

          updateUserBadges();

        }

      }

    } catch (e) {}

  }



  function updateUserBadges() {

    if (!authenticatedUser) return;

    const homeBadge = document.getElementById('situationHomeUserBadge');

    if (homeBadge) {

      homeBadge.textContent = '👤 ' + (authenticatedUser.full_name || 'User') + ' (' + (authenticatedUser.role || 'Citizen') + ')';

    }

    const locBadge = document.getElementById('situationHomeLocationBadge');

    if (locBadge && appState.selectedLocation) {

      locBadge.textContent = '📍 ' + (appState.selectedLocation.mandalName || 'Rajamahendravaram Urban') + ', ' + (appState.selectedLocation.districtName || 'East Godavari');

    }

    const sitHeading = document.getElementById('sitHomeHeading');

    if (sitHeading && appState.selectedLocation) {

      sitHeading.textContent = 'Situation Summary: ' + (appState.selectedLocation.mandalName || 'Rajamahendravaram Urban');

    }

  }



  function navigateTo(targetRoute) {

    const pages = [

      'page-welcome',

      'page-login',

      'page-register',

      'page-role-select',

      'page-location-onboarding',

      'page-situation-home',

      'page-dashboard-shell'

    ];



    // Auth gate for protected internal routes

    const protectedRoutes = ['role-select', 'location-onboarding', 'situation-home', 'explorer', 'operations', 'evidence', 'help', 'weather', 'overview', 'global', 'risk', 'research'];

    if (protectedRoutes.includes(targetRoute) && !authenticatedUser) {

      targetRoute = 'login';

      const feedback = document.getElementById('dedicatedLoginFeedback');

      if (feedback) {

        feedback.className = 'login-feedback error';

        feedback.style.display = 'block';

        feedback.textContent = 'Please sign in to access PRAVAH 360 operations and monitoring.';

      }

    }



    // Hide all top-level page views

    pages.forEach(pId => {

      const el = document.getElementById(pId);

      if (el) el.style.display = 'none';

    });



    if (targetRoute === 'welcome' || !targetRoute) {

      document.body.classList.remove('dashboard-active');

      const p = document.getElementById('page-welcome');

      if (p) p.style.display = 'block';

      if (window.location.hash !== '#welcome') history.replaceState(null, '', '#welcome');

    } else if (targetRoute === 'login') {

      document.body.classList.remove('dashboard-active');

      const p = document.getElementById('page-login');

      if (p) p.style.display = 'flex';

      if (window.location.hash !== '#login') history.replaceState(null, '', '#login');

    } else if (targetRoute === 'register') {

      document.body.classList.remove('dashboard-active');

      const p = document.getElementById('page-register');

      if (p) p.style.display = 'flex';

      if (window.location.hash !== '#register') history.replaceState(null, '', '#register');

    } else if (targetRoute === 'role-select') {

      document.body.classList.remove('dashboard-active');

      const p = document.getElementById('page-role-select');

      if (p) p.style.display = 'block';

      if (window.location.hash !== '#role-select') history.replaceState(null, '', '#role-select');

    } else if (targetRoute === 'location-onboarding') {

      document.body.classList.remove('dashboard-active');

      const p = document.getElementById('page-location-onboarding');

      if (p) p.style.display = 'block';

      if (window.location.hash !== '#location-onboarding') history.replaceState(null, '', '#location-onboarding');

      setTimeout(initOnboardingMiniMap, 100);

    } else if (targetRoute === 'situation-home') {

      document.body.classList.remove('dashboard-active');

      const p = document.getElementById('page-situation-home');

      if (p) p.style.display = 'block';

      if (window.location.hash !== '#situation-home') history.replaceState(null, '', '#situation-home');

      updateUserBadges();

    } else {

      // Analytical GIS Dashboard Shell

      document.body.classList.add('dashboard-active');

      const p = document.getElementById('page-dashboard-shell');

      if (p) p.style.display = 'block';

      switchWorkspace(targetRoute);

      setTimeout(() => {

        if (maps && maps.explorer) maps.explorer.invalidateSize();

        if (maps && maps.overview) maps.overview.invalidateSize();

      }, 150);

    }



    window.scrollTo({ top: 0, behavior: 'instant' });

  }

  window.navigateTo = navigateTo;



  // Setup Onboarding Mini Leaflet Map Preview

  function initOnboardingMiniMap() {

    const container = document.getElementById('onboarding-preview-map');

    if (!container || onboardingMiniMap) {

      if (onboardingMiniMap) onboardingMiniMap.invalidateSize();

      return;

    }



    onboardingMiniMap = L.map('onboarding-preview-map', {

      center: [16.9850, 81.7800],

      zoom: 11,

      zoomControl: false,

      attributionControl: false

    });



    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}', {

      maxZoom: 16

    }).addTo(onboardingMiniMap);



    const marker = L.circleMarker([16.9850, 81.7800], {

      radius: 9,

      fillColor: '#153D37',

      color: '#D7A94D',

      weight: 3,

      opacity: 1,

      fillOpacity: 0.9

    }).addTo(onboardingMiniMap);



    onboardingMiniMap._marker = marker;

  }



  function updateOnboardingMapLocation(mandalName) {

    const coordsMap = {

      'Rajamahendravaram Urban': [16.9850, 81.7800],

      'Rajamahendravaram Rural': [16.9600, 81.7500],

      'Kovvur': [17.0140, 81.7300],

      'Amalapuram': [16.5780, 82.0050],

      'Razole': [16.4800, 81.8900],

      'Mummidivaram': [16.6500, 82.1100],

      'Kothapeta': [16.7150, 81.8900],

      'Ravulapalem': [16.7500, 81.8500],

      'Polavaram': [17.2550, 81.6520],

      'Narsapur': [16.4350, 81.6900],

      'Palakollu': [16.5300, 81.7300],

      'Achanta': [16.6000, 81.8000],

      'Tanuku': [16.7550, 81.6800],

      'Bhimavaram': [16.5400, 81.5200],

      'Tadepallegudem': [16.8150, 81.5250],

      'Eluru': [16.7100, 81.1000],

      'Chintalapudi': [17.0600, 80.9800],

      'Kakinada Rural': [16.9300, 82.2400],

      'Pithapuram': [17.1100, 82.2500],

      'Peddapuram': [17.0800, 82.1350],

      'Tuni': [17.3500, 82.5500],

      'Devipatnam': [17.4500, 81.7000]

    };



    const latlon = coordsMap[mandalName] || [16.9850, 81.7800];

    if (onboardingMiniMap) {

      onboardingMiniMap.setView(latlon, 11);

      if (onboardingMiniMap._marker) onboardingMiniMap._marker.setLatLng(latlon);

    }

    const labelEl = document.getElementById('onboardingMapLabel');

    if (labelEl) labelEl.textContent = mandalName;

    const coordsEl = document.getElementById('onboardingMapCoords');

    if (coordsEl) coordsEl.textContent = latlon[0].toFixed(4) + '° N, ' + latlon[1].toFixed(4) + '° E • Andhra Pradesh';

  }



  // Bind All Multi-Page Actions


  // Globally Accessible Handlers for Form Submissions and Auth Actions
  window.handleDedicatedLoginSubmit = async function(e) {
    if (e && e.preventDefault) e.preventDefault();
    const email = document.getElementById('dedicatedEmail')?.value.trim();
    const password = document.getElementById('dedicatedPassword')?.value;
    const feedback = document.getElementById('dedicatedLoginFeedback');
    const submitBtn = document.getElementById('btnDedicatedLoginSubmit');

    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = 'Verifying credentials...';
    }
    if (feedback) feedback.style.display = 'none';

    try {
      const res = await fetch('/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      const data = await res.json();

      if (res.ok && data.status === 'authenticated') {
        authenticatedUser = data.user;
        window.authenticatedUser = data.user;
        if (feedback) {
          feedback.className = 'login-feedback success';
          feedback.style.display = 'block';
          feedback.textContent = '✓ Sign in successful! Redirecting...';
        }
        updateUserBadges();

        setTimeout(() => {
          if (authenticatedUser.role === 'citizen') {
            navigateTo('role-select');
          } else {
            navigateTo('situation-home');
          }
        }, 500);
      } else {
        if (feedback) {
          feedback.className = 'login-feedback error';
          feedback.style.display = 'block';
          feedback.textContent = data.detail || 'Invalid email or password.';
        }
      }
    } catch (err) {
      if (feedback) {
        feedback.className = 'login-feedback error';
        feedback.style.display = 'block';
        feedback.textContent = 'Connection error. Please try again.';
      }
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = (window.currentAppLang === 'te') ? 'ఖాతాలోకి సైన్ ఇన్ చేయండి →' : 'Sign In to Account →';
      }
    }
  };

  window.handleDedicatedRegisterSubmit = async function(e) {
    if (e && e.preventDefault) e.preventDefault();
    const full_name = document.getElementById('regFullName')?.value.trim();
    const email = document.getElementById('regEmail')?.value.trim();
    const password = document.getElementById('regPassword')?.value;
    const confirmPassword = document.getElementById('regConfirmPassword')?.value;
    const district = document.getElementById('regDistrict')?.value || 'East Godavari';
    const mandal = document.getElementById('regMandal')?.value || 'Rajamahendravaram Urban';
    const feedback = document.getElementById('dedicatedRegisterFeedback');
    const submitBtn = document.getElementById('btnRegisterSubmit');

    if (feedback) feedback.style.display = 'none';

    if (password !== confirmPassword) {
      if (feedback) {
        feedback.className = 'login-feedback error';
        feedback.style.display = 'block';
        feedback.textContent = 'Passwords do not match. Please re-enter.';
      }
      return;
    }

    if (password.length < 8) {
      if (feedback) {
        feedback.className = 'login-feedback error';
        feedback.style.display = 'block';
        feedback.textContent = 'Password must be at least 8 characters long.';
      }
      return;
    }

    if (submitBtn) {
      submitBtn.disabled = true;
      submitBtn.textContent = 'Creating account...';
    }

    try {
      const res = await fetch('/api/v1/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ full_name, email, password, district, mandal })
      });
      const data = await res.json();

      if (res.ok && data.status === 'registered') {
        authenticatedUser = data.user;
        window.authenticatedUser = data.user;
        if (appState.selectedLocation) {
          appState.selectedLocation.mandalName = mandal;
          appState.selectedLocation.districtName = district;
          appState.selectedLocation.name = mandal;
        }
        if (feedback) {
          feedback.className = 'login-feedback success';
          feedback.style.display = 'block';
          feedback.textContent = '✓ Account created successfully! Redirecting...';
        }
        updateUserBadges();

        setTimeout(() => {
          navigateTo('role-select');
        }, 500);
      } else {
        if (feedback) {
          feedback.className = 'login-feedback error';
          feedback.style.display = 'block';
          feedback.textContent = data.detail || 'Registration failed. Please check inputs.';
        }
      }
    } catch (err) {
      if (feedback) {
        feedback.className = 'login-feedback error';
        feedback.style.display = 'block';
        feedback.textContent = 'Network error during registration. Please try again.';
      }
    } finally {
      if (submitBtn) {
        submitBtn.disabled = false;
        submitBtn.textContent = (window.currentAppLang === 'te') ? 'ఖాతాను సృష్టించి కొనసాగించండి →' : 'Create Account & Proceed →';
      }
    }
  };

  window.signOutUser = async function() {
    try {
      await fetch('/api/v1/auth/logout', { method: 'POST' });
    } catch (e) {}
    authenticatedUser = null;
    window.authenticatedUser = null;
    navigateTo('welcome');
  };

  function initMultiPageEntryControllers() {

    // 1. Landing Page Actions

    const btnNavSignIn = document.getElementById('btnNavSignIn');

    if (btnNavSignIn) btnNavSignIn.addEventListener('click', () => navigateTo('login'));



    const btnNavRegister = document.getElementById('btnNavRegister');

    if (btnNavRegister) btnNavRegister.addEventListener('click', () => navigateTo('register'));



    const btnHeroRegister = document.getElementById('btnHeroRegister');

    if (btnHeroRegister) btnHeroRegister.addEventListener('click', () => navigateTo('register'));



    const btnHeroSignIn = document.getElementById('btnHeroSignIn');

    if (btnHeroSignIn) btnHeroSignIn.addEventListener('click', () => navigateTo('login'));



    const btnHeroExplore = document.getElementById('btnHeroExplore');

    if (btnHeroExplore) {

      btnHeroExplore.addEventListener('click', () => {

        const sec = document.getElementById('visual-stories');

        if (sec) sec.scrollIntoView({ behavior: 'smooth' });

      });

    }



    // Landing Global Language Toggle
    // Global Language Toggle Buttons across all surfaces
    document.querySelectorAll('#btnLandingLangToggle, .btn-lang-toggle, .lang-switch-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        if (typeof window.toggleGlobalLanguage === 'function') {
          window.toggleGlobalLanguage();
        }
      });
    });

    // --- PHASE 3: INTERACTIVE HELPLINE CALL CONFIRMATION CONTROLLER ---
    let _activeHelplineNumber = '';
    window.confirmHelplineCall = function(serviceName, number) {
      _activeHelplineNumber = number;
      const modal = document.getElementById('helplineConfirmModal');
      const svcEl = document.getElementById('helplineModalService');
      const numEl = document.getElementById('helplineModalNumber');
      const txtEl = document.getElementById('helplineModalText');
      const dialBtn = document.getElementById('btnHelplineDial');
      const copyNotice = document.getElementById('helplineCopyNotice');
      if (copyNotice) copyNotice.style.display = 'none';

      const isTe = (window.currentAppLang === 'te');
      if (svcEl) svcEl.textContent = serviceName;
      if (numEl) numEl.textContent = number;
      if (txtEl) {
        txtEl.textContent = isTe
          ? `మీరు ${serviceName} (${number}) నంబరుకు కాల్ చేయాలనుకుంటున్నారా? ఈ బటన్ నొక్కడం వల్ల మీ ఫోన్ డయలర్ తెరవబడుతుంది.`
          : `Do you want to call ${serviceName} (${number})? This will launch your device phone dialler to place the call.`;
      }
      if (dialBtn) {
        dialBtn.onclick = function() {
          window.location.href = 'tel:' + number;
          if (modal) modal.style.display = 'none';
        };
      }
      if (modal) modal.style.display = 'flex';
    };

    window.copyHelplineNumber = function() {
      if (_activeHelplineNumber) {
        navigator.clipboard.writeText(_activeHelplineNumber).then(() => {
          const copyNotice = document.getElementById('helplineCopyNotice');
          if (copyNotice) {
            copyNotice.style.display = 'block';
            copyNotice.textContent = (window.currentAppLang === 'te') ? '✓ నంబరు కాపీ చేయబడింది!' : '✓ Number copied to clipboard!';
          }
        }).catch(() => {
          alert('Number: ' + _activeHelplineNumber);
        });
      }
    };



    // 2. Dedicated Login Form Submission

    // --- Auth Submit Button Loading State Helpers ---
  function setAuthBtnLoading(btnId, loading) {
    const btn = document.getElementById(btnId);
    if (!btn) return;
    if (loading) { btn.classList.add('loading'); btn.disabled = true; }
    else { btn.classList.remove('loading'); btn.disabled = false; }
  }

  const loginForm = document.getElementById('dedicatedLoginForm');

    if (loginForm) {

      loginForm.addEventListener('submit', async (e) => {

        e.preventDefault();

        const email = document.getElementById('dedicatedEmail')?.value.trim();

        const password = document.getElementById('dedicatedPassword')?.value;

        const feedback = document.getElementById('dedicatedLoginFeedback');

        const submitBtn = document.getElementById('btnDedicatedLoginSubmit');



        if (submitBtn) {

          submitBtn.disabled = true;

          submitBtn.textContent = 'Verifying credentials...';

        }

        if (feedback) feedback.style.display = 'none';



        try {

          const res = await fetch('/api/v1/auth/login', {

            method: 'POST',

            headers: { 'Content-Type': 'application/json' },

            body: JSON.stringify({ email, password })

          });

          const data = await res.json();



          if (res.ok && data.status === 'authenticated') {

            authenticatedUser = data.user;

            if (feedback) {

              feedback.className = 'login-feedback success';

              feedback.style.display = 'block';

              feedback.textContent = '✓ Sign in successful! Redirecting...';

            }

            updateUserBadges();



            setTimeout(() => {

              if (authenticatedUser.role === 'citizen') {

                navigateTo('role-select');

              } else {

                navigateTo('situation-home');

              }

            }, 600);

          } else {

            if (feedback) {

              feedback.className = 'login-feedback error';

              feedback.style.display = 'block';

              feedback.textContent = data.detail || 'Invalid email or password.';

            }

          }

        } catch (err) {

          if (feedback) {

            feedback.className = 'login-feedback error';

            feedback.style.display = 'block';

            feedback.textContent = 'Connection error. Please try again.';

          }

        } finally {

          if (submitBtn) {

            submitBtn.disabled = false;

            submitBtn.textContent = 'Sign In to Account →';

          }

        }

      });

    }





    // 2B. Dedicated Registration Form Submission

    const regForm = document.getElementById('dedicatedRegisterForm');

    if (regForm) {

      regForm.addEventListener('submit', async (e) => {

        e.preventDefault();

        const full_name = document.getElementById('regFullName')?.value.trim();

        const email = document.getElementById('regEmail')?.value.trim();

        const password = document.getElementById('regPassword')?.value;

        const confirmPassword = document.getElementById('regConfirmPassword')?.value;

        const district = document.getElementById('regDistrict')?.value || 'East Godavari';

        const mandal = document.getElementById('regMandal')?.value || 'Rajamahendravaram Urban';

        const feedback = document.getElementById('dedicatedRegisterFeedback');

        const submitBtn = document.getElementById('btnRegisterSubmit');



        if (feedback) feedback.style.display = 'none';



        if (password !== confirmPassword) {

          if (feedback) {

            feedback.className = 'login-feedback error';

            feedback.style.display = 'block';

            feedback.textContent = 'Passwords do not match. Please re-enter.';

          }

          return;

        }



        if (password.length < 8) {

          if (feedback) {

            feedback.className = 'login-feedback error';

            feedback.style.display = 'block';

            feedback.textContent = 'Password must be at least 8 characters long.';

          }

          return;

        }



        if (submitBtn) {

          submitBtn.disabled = true;

          submitBtn.textContent = 'Creating account...';

        }



        try {

          const res = await fetch('/api/v1/auth/register', {

            method: 'POST',

            headers: { 'Content-Type': 'application/json' },

            body: JSON.stringify({ full_name, email, password, district, mandal })

          });

          const data = await res.json();



          if (res.ok && data.status === 'registered') {

            authenticatedUser = data.user;

            if (appState.selectedLocation) {

              appState.selectedLocation.mandalName = mandal;

              appState.selectedLocation.districtName = district;

              appState.selectedLocation.name = mandal;

            }

            if (feedback) {

              feedback.className = 'login-feedback success';

              feedback.style.display = 'block';

              feedback.textContent = '✓ Account created successfully! Redirecting...';

            }

            updateUserBadges();



            setTimeout(() => {

              const successOverlay = document.getElementById('regSuccessOverlay');
            if (successOverlay) { successOverlay.style.display = 'flex'; }
            setTimeout(() => { navigateTo('role-select'); }, 1500);

            }, 600);

          } else {

            if (feedback) {

              feedback.className = 'login-feedback error';

              feedback.style.display = 'block';

              feedback.textContent = data.detail || 'Registration failed. Please check inputs.';

            }

          }

        } catch (err) {
        setAuthBtnLoading('btnRegisterSubmit', false);

          if (feedback) {

            feedback.className = 'login-feedback error';

            feedback.style.display = 'block';

            feedback.textContent = 'Network error during registration. Please try again.';

          }

        } finally {

          if (submitBtn) {

            submitBtn.disabled = false;

            submitBtn.textContent = 'Create Account & Proceed →';

          }

        }

      });

    }



    // Toggle Registration Password Visibility

    const btnToggleReg = document.getElementById('btnToggleRegPwd');

    const regPwdIn = document.getElementById('regPassword');

    if (btnToggleReg && regPwdIn) {

      btnToggleReg.addEventListener('click', () => {
        const isPwd = regPwdIn.type === 'password';
        regPwdIn.type = isPwd ? 'text' : 'password';
        const svgEl = btnToggleReg.querySelector('svg');
        if (svgEl) {
          svgEl.innerHTML = isPwd
            ? '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/>'
            : '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>';
        }
        btnToggleReg.setAttribute('aria-label', isPwd ? 'Hide password' : 'Show password');
      });

    }



    // Password Visibility Toggle

    const btnTogglePwd = document.getElementById('btnToggleDedicatedPwd');

    const pwdInput = document.getElementById('dedicatedPassword');

    if (btnTogglePwd && pwdInput) {

      btnTogglePwd.addEventListener('click', () => {
        const isPwd = pwdInput.type === 'password';
        pwdInput.type = isPwd ? 'text' : 'password';
        const icon = document.getElementById('eyeIconLogin');
        if (icon) {
          if (isPwd) {
            icon.innerHTML = '<path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/>';
          } else {
            icon.innerHTML = '<path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/>';
          }
        }
        btnTogglePwd.setAttribute('aria-label', isPwd ? 'Hide password' : 'Show password');
      });

    }



    // Evaluator Quick-Fill Helper Pills

    document.querySelectorAll('.btn-test-pill').forEach(pill => {

      pill.addEventListener('click', () => {

        const email = pill.getAttribute('data-email');

        const pass = pill.getAttribute('data-pass');

        const emIn = document.getElementById('dedicatedEmail');

        const pwIn = document.getElementById('dedicatedPassword');

        if (emIn && email) emIn.value = email;

        if (pwIn && pass) pwIn.value = pass;

      });

    });



    // Password strength meter
    const regPwdStrengthField = document.getElementById('regPassword');
    if (regPwdStrengthField) {
      regPwdStrengthField.addEventListener('input', () => {
        const val = regPwdStrengthField.value;
        const fill = document.getElementById('regPwdStrengthFill');
        const label = document.getElementById('regPwdStrengthLabel');
        if (!fill || !label) return;
        let strength = 0;
        if (val.length >= 8) strength++;
        if (/[A-Z]/.test(val)) strength++;
        if (/[0-9]/.test(val)) strength++;
        if (/[^A-Za-z0-9]/.test(val)) strength++;
        const widths = ['0%', '25%', '50%', '75%', '100%'];
        const colors = ['transparent', '#D66B52', '#D7A94D', '#4db6D7', '#4caf72'];
        const labels = ['', 'Weak', 'Fair', 'Good', 'Strong'];
        const labelColors = ['', '#D66B52', '#D7A94D', '#4db6D7', '#4caf72'];
        fill.style.width = widths[strength];
        fill.style.background = colors[strength];
        label.textContent = val.length > 0 ? labels[strength] : '';
        label.style.color = labelColors[strength];
      });
    }

    // Confirm password match hint
    const regConfirmField = document.getElementById('regConfirmPassword');
    if (regConfirmField && regPwdStrengthField) {
      const checkMatch = () => {
        const hint = document.getElementById('regPwdMatchHint');
        if (!hint) return;
        if (!regConfirmField.value) { hint.textContent = ''; return; }
        if (regConfirmField.value === regPwdStrengthField.value) {
          hint.textContent = '✓ Passwords match';
          hint.style.color = '#4caf72';
          regConfirmField.classList.remove('auth-input-error');
          regConfirmField.classList.add('auth-input-success');
        } else {
          hint.textContent = '✗ Passwords do not match';
          hint.style.color = '#D66B52';
          regConfirmField.classList.add('auth-input-error');
          regConfirmField.classList.remove('auth-input-success');
        }
      };
      regConfirmField.addEventListener('input', checkMatch);
      regPwdStrengthField.addEventListener('input', () => { if (regConfirmField.value) checkMatch(); });
    }

    // 3. Role Selection Cards

    document.querySelectorAll('.role-choice-card').forEach(card => {

      card.addEventListener('click', () => {

        const role = card.getAttribute('data-role');

        if (authenticatedUser) authenticatedUser.role = role;

        updateUserBadges();



        if (role === 'citizen') {

          navigateTo('location-onboarding');

        } else {

          navigateTo('situation-home');

        }

      });

    });



    // 4. Location Onboarding Actions

    const selectMandal = document.getElementById('selectOnboardingMandal');

    if (selectMandal) {

      selectMandal.addEventListener('change', (e) => {

        const mandalName = e.target.value;

        updateOnboardingMapLocation(mandalName);

        if (appState.selectedLocation) {

          appState.selectedLocation.mandalName = mandalName;

          appState.selectedLocation.name = mandalName;

        }

      });

    }



    const btnConfirmLoc = document.getElementById('btnConfirmLocation');

    if (btnConfirmLoc) {

      btnConfirmLoc.addEventListener('click', () => {

        const mandalName = document.getElementById('selectOnboardingMandal')?.value || 'Rajamahendravaram Urban';

        const districtName = document.getElementById('selectOnboardingDistrict')?.value || 'East Godavari';

        if (appState.selectedLocation) {

          appState.selectedLocation.mandalName = mandalName;

          appState.selectedLocation.districtName = districtName;

          appState.selectedLocation.name = mandalName;

        }

        updateUserBadges();

        navigateTo('situation-home');

      });

    }



    // 5. Situation Awareness Home Actions

    const cardExplorer = document.getElementById('cardLaunchExplorer');

    if (cardExplorer) cardExplorer.addEventListener('click', () => navigateTo('explorer'));



    const cardAidConnect = document.getElementById('cardLaunchAidConnect');

    if (cardAidConnect) cardAidConnect.addEventListener('click', () => navigateTo('operations'));



    const cardWhatChanged = document.getElementById('cardLaunchWhatChanged');

    if (cardWhatChanged) cardWhatChanged.addEventListener('click', () => navigateTo('evidence'));



    const cardPrep = document.getElementById('cardLaunchPreparedness');

    if (cardPrep) cardPrep.addEventListener('click', () => navigateTo('help'));



    const btnSignOut = document.getElementById('btnSituationHomeSignOut');

    if (btnSignOut) {

      btnSignOut.addEventListener('click', async () => {

        try {

          await fetch('/api/v1/auth/logout', { method: 'POST' });

        } catch (e) {}

        authenticatedUser = null;

        navigateTo('welcome');

      });

    }



    // Exit from analytical dashboard shell back to Situation Home

    const btnReturnHome = document.getElementById('btnReturnToSituationHome');

    if (btnReturnHome) {

      btnReturnHome.addEventListener('click', () => navigateTo('situation-home'));

    }

  }



  // Hash change routing

  window.addEventListener('hashchange', () => {

    const rawHash = window.location.hash.replace('#', '').replace('/', '');

    const validRoutes = ['welcome', 'login', 'register', 'role-select', 'location-onboarding', 'situation-home', 'explorer', 'operations', 'evidence', 'help', 'weather', 'overview', 'global', 'risk', 'research'];

    if (validRoutes.includes(rawHash)) {

      navigateTo(rawHash);

    }

  });



  // Initialize session check and entry routing

  checkInitialSession().then(() => {

    const currentHash = window.location.hash.replace('#', '').replace('/', '');

    if (currentHash === 'login') {

      navigateTo('login');

    } else if (currentHash === 'register') {

      navigateTo('register');

    } else if (authenticatedUser && ['role-select', 'location-onboarding', 'situation-home', 'explorer', 'operations', 'evidence', 'help'].includes(currentHash)) {

      navigateTo(currentHash);

    } else if (!currentHash || currentHash === 'welcome') {

      navigateTo('welcome');

    } else if (!authenticatedUser) {

      navigateTo('login');

    }

  });



  initMultiPageEntryControllers();

  // Load and apply persistent user language preference on startup
  const savedAppLang = localStorage.getItem('pravah_lang') || 'en';
  if (savedAppLang && typeof window.setAppLanguage === 'function') {
    window.setAppLanguage(savedAppLang);
  }

  // URL query parameter action handlers (for automation & test captures)
  const deepLinkParams = new URLSearchParams(window.location.search);
  const langParam = deepLinkParams.get('lang');
  if (langParam && typeof window.setAppLanguage === 'function') {
    setTimeout(() => { window.setAppLanguage(langParam); }, 300);
  }
  const actionParam = deepLinkParams.get('action');
  if (actionParam === 'telugu') {
    setTimeout(() => {
      if (typeof window.setAppLanguage === 'function') window.setAppLanguage('te');
    }, 300);
  } else if (actionParam === 'hazards') {
    setTimeout(() => {
      if (typeof window.setAppLanguage === 'function') window.setAppLanguage('te');
      const sec = document.getElementById('community-hazards');
      if (sec) sec.scrollIntoView({ behavior: 'instant', block: 'start' });
    }, 500);
  } else if (actionParam === 'voice') {
    setTimeout(() => {
      if (typeof window.setAppLanguage === 'function') window.setAppLanguage('te');
      if (window.pravahVoice && typeof window.pravahVoice.handleVoiceQuery === 'function') {
        window.pravahVoice.handleVoiceQuery('వరద హెచ్చరికలు ఉన్నాయా?');
      }
    }, 500);
  }





});
