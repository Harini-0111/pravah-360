import re
from pathlib import Path

app_js_path = Path('frontend/app.js')
with open(app_js_path, 'r', encoding='utf-8') as f:
    code = f.read()

# 1. Update createBasemaps to include Esri Reference layer with Dark Base, and Topo
old_create_basemaps = """  function createBasemaps() {
    // Esri World Dark Gray Canvas (Default - Clean, unwatermarked dark GIS canvas)
    const esriDark = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
      attribution: 'Tiles &copy; Esri &mdash; Esri, DeLorme, NAVTEQ',
      maxZoom: 16
    });

    // Esri World Imagery (High-res satellite)
    const esriSat = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
      attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
      maxZoom: 18
    });

    // OpenStreetMap Standard
    const osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      maxZoom: 19
    });

    return { esriDark, esriSat, osm };
  }"""

new_create_basemaps = """  function createBasemaps() {
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
  }"""

if old_create_basemaps in code:
    code = code.replace(old_create_basemaps, new_create_basemaps)
    print("Replaced createBasemaps")
else:
    print("WARNING: old_create_basemaps not found exactly")

# 2. Update initOverviewMap to be a true Geographic Hero area
old_init_overview = """  function initOverviewMap() {
    const container = document.getElementById('overview-map');
    if (!container || maps.overview) return;

    maps.overview = L.map('overview-map', {
      center: STUDY_AREA_CENTER,
      zoom: 8,
      zoomControl: false,
      attributionControl: false,
      preferCanvas: true
    });

    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Canvas/World_Dark_Gray_Base/MapServer/tile/{z}/{y}/{x}', {
      maxZoom: 14
    }).addTo(maps.overview);

    // Add Study Area Outline
    fetch('/static/data/lower_godavari_study_area.geojson')
      .then(res => res.json())
      .then(geojson => {
        L.geoJSON(geojson, {
          style: {
            color: '#38bdf8',
            weight: 2,
            fillColor: '#38bdf8',
            fillOpacity: 0.1
          }
        }).addTo(maps.overview);
      })
      .catch(() => {});

    // Add Mandals choropleth to Overview Map
    if (appState.mandalsData && appState.basinAssessment) {
      const lookup = {};
      appState.basinAssessment.mandal_assessments.forEach(m => {
        lookup[m.mandal_name.toLowerCase()] = m;
      });
      L.geoJSON(appState.mandalsData, {
        style: (feat) => {
          const n = (feat.properties?.NAME_3 || '').toLowerCase();
          const rec = lookup[n];
          return {
            color: '#ffffff',
            weight: 0.5,
            fillColor: getCategoryColor(rec ? rec.susceptibility_category : 'Moderate'),
            fillOpacity: 0.5
          };
        }
      }).addTo(maps.overview);
    }
  }"""

new_init_overview = """  function initOverviewMap() {
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
  }"""

if old_init_overview in code:
    code = code.replace(old_init_overview, new_init_overview)
    print("Replaced initOverviewMap")
else:
    print("WARNING: old_init_overview not found exactly")

# 3. Update initGlobalEarth to use local high-res textures
old_init_globe = """        // Initialize Globe.gl
        globeInstance = Globe()(container)
          .globeImageUrl('//unpkg.com/three-globe/example/img/earth-night.jpg')
          .bumpImageUrl('//unpkg.com/three-globe/example/img/earth-topology.png')
          .backgroundImageUrl('//unpkg.com/three-globe/example/img/night-sky.png')
          .polygonsData(appState.worldCountries)
          .polygonAltitude(0.01)
          .polygonCapColor(() => 'rgba(2, 132, 199, 0.25)')
          .polygonSideColor(() => 'rgba(2, 132, 199, 0.15)')
          .polygonStrokeColor(() => '#38bdf8')
          .polygonLabel(({ properties: d }) => `
            <div style="background:rgba(12,20,36,0.9); border:1px solid #38bdf8; padding:6px 10px; border-radius:5px; color:#fff; font-family:sans-serif; font-size:12px;">
              <strong>${d.name || d.NAME || d.ADMIN || 'Country'}</strong><br>
              <span style="font-size:10px; color:#94a3b8;">${d.continent || d.CONTINENT || 'Global Landmass'}</span>
            </div>
          `)
          .onPolygonHover(hoverD => {
            globeInstance
              .polygonAltitude(d => d === hoverD ? 0.05 : 0.01)
              .polygonCapColor(d => d === hoverD ? 'rgba(56, 189, 248, 0.6)' : 'rgba(2, 132, 199, 0.25)');
          })
          .onPolygonClick(({ properties: d }) => {
            selectGlobeCountry(d);
          });

        // Set Initial Camera Position (Looking towards India/Asia)
        globeInstance.pointOfView({ lat: 20, lng: 80, altitude: 2.2 }, 1500);

        // Auto-Rotation Setup
        globeInstance.controls().autoRotate = true;
        globeInstance.controls().autoRotateSpeed = 0.6;
        window.globeInstance = globeInstance;

        wireGlobeControls();"""

new_init_globe = """        // Initialize Globe.gl with high-res local textures & glowing atmosphere
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

        wireGlobeControls();"""

if old_init_globe in code:
    code = code.replace(old_init_globe, new_init_globe)
    print("Replaced initGlobalEarth")
else:
    print("WARNING: old_init_globe not found exactly")

# 4. Update wireGlobeControls to handle day/night toggle and quick country fly pills
old_wire_globe = """    // 4. Country Search & Autocomplete
    const searchInput = document.getElementById('globeCountrySearchInput');"""

new_wire_globe = """    // Day / Night Texture Toggle Button
    let isDayTexture = true;
    const btnTex = document.getElementById('btnToggleGlobeTexture');
    if (btnTex) {
      btnTex.addEventListener('click', () => {
        if (!globeInstance) return;
        isDayTexture = !isDayTexture;
        globeInstance.globeImageUrl(isDayTexture ? '/static/textures/earth-blue-marble.jpg' : '/static/textures/earth-night.jpg');
        btnTex.textContent = isDayTexture ? '☀️ Day Texture' : '🌙 Night Texture';
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
    const searchInput = document.getElementById('globeCountrySearchInput');"""

if old_wire_globe in code:
    code = code.replace(old_wire_globe, new_wire_globe)
    print("Replaced wireGlobeControls")
else:
    print("WARNING: old_wire_globe not found exactly")

with open(app_js_path, 'w', encoding='utf-8') as f:
    f.write(code)

print("Updated app.js successfully.")
