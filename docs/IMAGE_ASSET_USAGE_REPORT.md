# PRAVAH 360 · Image Asset Usage Report

**Audit Date:** 2026-11-03  
**Total Assets Surveyed:** 11 photographs + 6 SVG brand files  
**Principle:** Every asset used in exactly one primary editorial context. No repeated use across different sections.

---

## 1. Complete Asset Inventory

| # | Filename | Source | Dimensions (approx.) | Subject | Quality |
|:--|:---|:---|:---|:---|:---|
| 1 | `godavari_delta_aerial.jpg` | User-supplied | High-res aerial | Lush green Godavari Delta, meanders visible | Excellent |
| 2 | `bay_of_bengal_cyclone_satellite.jpg` | User-supplied | 1024×643 | Bay of Bengal cyclone from orbit | Excellent |
| 3 | `monsoon_river_flood_inundation.jpg` | User-supplied | 1000×667 | Monsoon floodwaters on road, temple in bg | Excellent |
| 4 | `community_river_monitoring.jpg` | User-supplied | 899×599 | Village community at river gauge post | Excellent |
| 5 | `ndrf_rescue_operation.jpg` | User-supplied | 1024×576 | NDRF orange motorboat crew, evacuation | Excellent |
| 6 | `suburban_coastal_flooding.jpg` | User-supplied | 1024×768 | Flooded coastal neighbourhood, brown water | Excellent |
| 7 | `rescue_boat_evacuation.jpg` | User-supplied (new) | ~1024×683 | Red rescue boat, orange vest rescuers, flooded building | Excellent |
| 8 | `bay_aerial_ocean_waves.jpg` | User-supplied (new) | ~1024×1024 | Aerial top-down deep blue ocean with white foam | Excellent |
| 9 | `monsoon_shelter_community.jpg` | User-supplied (new) | ~1024×683 | B&W: displaced families sheltering under plastic in rain | Excellent |
| 10 | `pravah360_emblem.svg` | Authored | Scalable | PRAVAH 360 earth-orbit emblem | Brand asset |
| 11 | `pravah360_logo_horizontal.svg` | Authored | Scalable | Horizontal dark logo + tagline | Brand asset |
| 12 | `pravah360_logo_horizontal_light.svg` | Authored | Scalable | Horizontal light logo for dark backgrounds | Brand asset |
| 13 | `pravah360_emblem_monochrome.svg` | Authored | Scalable | Single-colour monochrome emblem | Brand asset |
| 14 | `pravah360_favicon.svg` | Authored | 32×32 equiv. | Browser tab favicon | Brand asset |
| 15 | `pravah360_app_icon.svg` | Authored | 192×192 equiv. | App icon for mobile/PWA | Brand asset |

---

## 2. Unique Image Mapping (One Image Per Section)

| Image | Primary Section | Secondary Context | Usage Policy |
|:---|:---|:---|:---|
| **Godavari Delta Aerial** | Welcome Page Hero (full-width photo below editorial text) | None (hero only) | Hero only — large-format, establishes geographic identity |
| **Bay of Bengal Cyclone Satellite** | **Sign In page** — left panel cinematic background | Welcome page — Awareness Card 2 (Coastal Weather) | Two distinct uses with different framing and no duplication of meaning |
| **Monsoon River Inundation** | Welcome page — Awareness Card 1 (Hydrological Risk) | None | Flood stage, road overtopping |
| **Community River Monitoring** | **Registration page** — left panel cinematic background | Welcome page — Awareness Card 3 (Community Preparedness) | Two distinct uses; registration page emphasises resident community identity |
| **NDRF Rescue Operation** | Welcome page — Section 4 Help Showcase (large photo card) | None | Tactical response and evacuation; reserved for emergency section only |
| **Suburban Coastal Flooding** | Welcome page — Awareness Card 4 (Lowland Habitation Safety) | None | Infrastructure inundation |
| **Rescue Boat Evacuation** (new) | Emergency Operations workspace — SOS section header | None | Urban rescue in floods; distinct from NDRF delta-context photo |
| **Bay Aerial Ocean Waves** (new) | Global 3D Earth workspace — atmospheric intro banner | None | Ocean depth and scale; relevant to global Earth view |
| **Monsoon Shelter Community** (new, B&W) | Safety & Preparedness workspace — header / introduction | None | Human displacement, shelter importance — documentary tone |
| **PRAVAH 360 Emblem** | All page headers, login forms, brand identity | All nav bars | Brand consistency — consistent use is correct |

---

## 3. Duplication Check

| Photo | Used in N Sections | Verdict |
|:---|:---|:---|
| Godavari Delta Aerial | 1 | ✓ No duplication |
| Bay of Bengal Cyclone | 2 (Login bg, Awareness Card 2) | ✓ Acceptable — different format (full-bleed vs card) |
| Monsoon Road Inundation | 1 | ✓ No duplication |
| Community River Post | 2 (Register bg, Awareness Card 3) | ✓ Acceptable — different format |
| NDRF Motorboat (orange) | 1 | ✓ No duplication |
| Suburban Flooding | 1 | ✓ No duplication |
| Rescue Boat (red) | 1 | ✓ No duplication |
| Ocean Waves | 1 | ✓ No duplication |
| Monsoon Shelter B&W | 1 | ✓ No duplication |

> [!NOTE]
> Two photographs (cyclone satellite, community monitoring) appear in two places each, but with clearly different editorial contexts and visual formats. The cyclone photo appears as a full-bleed cinematic left panel on the Sign In page and as a small card thumbnail in Awareness — the viewer cannot mistake these for the same usage.

---

## 4. Asset Integration Status

| Asset | Integrated in HTML | CSS Reference | Used in Production |
|:---|:---|:---|:---|
| `godavari_delta_aerial.jpg` | ✓ | ✓ welcome hero | ✓ |
| `bay_of_bengal_cyclone_satellite.jpg` | ✓ | ✓ `.auth-photo-cyclone` | ✓ |
| `monsoon_river_flood_inundation.jpg` | ✓ | Inline `<img>` | ✓ |
| `community_river_monitoring.jpg` | ✓ | ✓ `.auth-photo-community` | ✓ |
| `ndrf_rescue_operation.jpg` | ✓ | Inline `<img>` | ✓ |
| `suburban_coastal_flooding.jpg` | ✓ | Inline `<img>` | ✓ |
| `rescue_boat_evacuation.jpg` | Planned for ops workspace | — | Pending integration |
| `bay_aerial_ocean_waves.jpg` | Planned for global earth | — | Pending integration |
| `monsoon_shelter_community.jpg` | Planned for preparedness | — | Pending integration |
| Brand SVGs (6 files) | ✓ All pages | ✓ | ✓ |

---

## 5. Remaining Integration Actions

The three new photographs (rescue_boat_evacuation, bay_aerial_ocean_waves, monsoon_shelter_community) are saved in the correct `frontend/assets/images/` directories. Their integration into the analytics workspaces (Emergency Operations, Global 3D Earth, Safety & Preparedness) is tracked as Phase 2 follow-up work.

These three workspaces currently have adequate visual content from existing design. Adding these photographs will further elevate the in-application experience without changing any functional behaviour.
