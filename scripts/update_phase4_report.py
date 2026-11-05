"""
Script to update sections 5, 6, 7 in PHASE_4_FLOOD_RISK_AND_IMPACT_ASSESSMENT_REPORT.md using line index
"""
from pathlib import Path

report_path = Path(r"C:\major project\PHASE_4_FLOOD_RISK_AND_IMPACT_ASSESSMENT_REPORT.md")
lines = report_path.read_text(encoding="utf-8").splitlines()

start_idx = None
end_idx = None

for i, line in enumerate(lines):
    if line.startswith("| :---: | :--- | :--- | :---:"):
        start_idx = i
        break

for i, line in enumerate(lines):
    if line.startswith("| **TOTAL ESSENTIAL FACILITIES**"):
        end_idx = i
        break

print(f"start_idx={start_idx}, end_idx={end_idx}")

new_lines_block = """| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | **Bhimavaram** | West Godavari | 200.7 | 3.7 | 1.4 | 1.2 | 8.4 | **0.881** | **Very High** | 561,705 | 557,748 | 99.3% | 110 |
| 2 | **Ramachandrapuram** | Dr. B.R. Ambedkar Konaseema | 291.5 | 8.7 | 1.5 | 1.3 | 6.8 | **0.847** | **Very High** | 717,462 | 708,245 | 98.7% | 94 |
| 3 | **Kakinada** | Kakinada | 239.3 | 5.2 | 1.3 | 1.3 | 12.1 | **0.844** | **Very High** | 1,009,871 | 998,420 | 98.9% | 159 |
| 4 | **Mummidivaram** | Dr. B.R. Ambedkar Konaseema | 185.1 | 4.3 | 2.4 | 1.5 | 0.8 | **0.842** | **Very High** | 284,861 | 284,861 | 100.0% | 10 |
| 5 | **Narsapur** | West Godavari | 269.4 | 4.7 | 2.5 | 1.3 | 0.4 | **0.827** | **Very High** | 645,992 | 643,514 | 99.6% | 69 |
| 6 | **Tanuku** | West Godavari | 261.2 | 8.6 | 1.8 | 1.4 | 7.2 | **0.825** | **Very High** | 591,307 | 583,212 | 98.6% | 102 |
| 7 | **Razole** | Dr. B.R. Ambedkar Konaseema | 227.1 | 6.7 | 3.1 | 1.3 | 0.6 | **0.824** | **Very High** | 363,222 | 363,222 | 100.0% | 23 |
| 8 | **Amalapuram** | Dr. B.R. Ambedkar Konaseema | 230.1 | 7.2 | 2.9 | 1.5 | 1.1 | **0.801** | **Very High** | 468,767 | 468,767 | 100.0% | 81 |
| 9 | **Kottapeta** | Dr. B.R. Ambedkar Konaseema | 179.3 | 10.0 | 1.7 | 1.4 | 0.5 | **0.799** | **Very High** | 358,034 | 357,980 | 100.0% | 27 |
| 10 | **Kovvur** | East Godavari | 385.2 | 40.6 | 1.8 | 1.5 | 0.2 | **0.793** | **Very High** | 471,416 | 451,120 | 95.7% | 43 |
| 11 | **Pithapuram** | Kakinada | 280.9 | 12.7 | 1.6 | 1.3 | 15.3 | **0.771** | **Very High** | 318,178 | 311,450 | 97.9% | 34 |
| 12 | **Rajahmundry** | East Godavari | 338.4 | 44.9 | 2.3 | 1.3 | 0.3 | **0.768** | **Very High** | 916,054 | 884,510 | 96.6% | 129 |
| 13 | **Tadepallegudem** | West Godavari | 337.8 | 26.3 | 1.6 | 1.4 | 14.2 | **0.706** | **High** | 425,720 | 404,210 | 94.9% | 102 |
| 14 | **Eluru** | Eluru | 396.9 | 27.0 | 1.5 | 1.2 | 18.5 | **0.676** | **High** | 678,823 | 641,120 | 94.4% | 185 |
| 15 | **Peddapuram** | Kakinada | 338.7 | 51.2 | 1.8 | 1.4 | 16.4 | **0.655** | **High** | 374,548 | 348,110 | 92.9% | 57 |
| 16 | **Polavaram** | Eluru | 857.8 | 199.8 | 8.0 | 1.3 | 0.2 | **0.559** | **Moderate** | 100,277 | 48,210 | 48.1% | 11 |
| 17 | **Tuni** | Kakinada | 407.9 | 57.0 | 6.2 | 1.2 | 22.8 | **0.536** | **Moderate** | 308,229 | 198,450 | 64.4% | 52 |
| 18 | **Prathipadu** | Kakinada | 454.4 | 161.9 | 8.9 | 1.3 | 19.1 | **0.463** | **Moderate** | 300,747 | 158,230 | 52.6% | 2 |
| 19 | **Chintalapudi** | Eluru | 722.5 | 110.5 | 2.5 | 1.6 | 24.1 | **0.395** | **Low** | 228,881 | 98,420 | 43.0% | 34 |
| 20 | **Addatigala** | Alluri Sitharama Raju | 1,208.5 | 397.4 | 13.8 | 1.6 | 18.2 | **0.301** | **Low** | 107,314 | 24,710 | 23.0% | 2 |
| 21 | **RampaChodavaram** | Alluri Sitharama Raju | 1,446.8 | 411.5 | 16.2 | 1.3 | 1.1 | **0.291** | **Low** | 99,325 | 12,320 | 12.4% | 1 |
| **TOTAL** | **21 Mandals** | **6 Districts** | **9,008.8** | **95.6** | **4.5** | **1.4** | **9.3** | **--** | **--** | **9,126,353** | **8,252,724** | **90.43%** | **1,467** |

---

## 6. District Exposure Summaries

Aggregated by 2022 reorganized district jurisdictions across the Lower Godavari delta:

```
+---------------------------------------------------------------------------------------------------------+
|                                    DISTRICT RISK & EXPOSURE AGGREGATION                                 |
+------------------------------+---------+--------------------+----------------+----------------+---------+
| District (2022 Reorganized)  | Mandals | Risk Distribution  | Baseline Pop   | Exposed Pop    | Mapped  |
|                              | Total   | (VH / H / M / L)   | (WorldPop 2020)| (VH + H Pixels)| Facils  |
+------------------------------+---------+--------------------+----------------+----------------+---------+
| Dr. B.R. Ambedkar Konaseema  | 5       | 5 / 0 / 0 / 0      | 2,192,346      | 2,183,074(99.6%)| 235    |
| West Godavari                | 4       | 3 / 1 / 0 / 0      | 2,224,724      | 2,188,684(98.4%)| 383    |
| East Godavari                | 2       | 2 / 0 / 0 / 0      | 1,387,470      | 1,335,630(96.3%)| 172    |
| Kakinada                     | 5       | 2 / 1 / 2 / 0      | 2,311,573      | 2,014,660(87.2%)| 304    |
| Eluru                        | 3       | 0 / 1 / 1 / 1      | 1,003,981      | 787,750 (78.5%)| 230     |
| Alluri Sitharama Raju        | 2       | 0 / 0 / 0 / 2      | 206,639        | 37,030 (17.9%) | 3       |
+------------------------------+---------+--------------------+----------------+----------------+---------+
| BASIN TOTAL                  | 21      | 12 / 3 / 3 / 3     | 9,126,353      | 8,252,724(90.4%)| 1,467   |
+------------------------------+---------+--------------------+----------------+----------------+---------+
```

### Highlights:
- **Dr. B.R. Ambedkar Konaseema District**: $100\%$ of evaluated mandals fall in the **Very High Risk** category, with $2.18\\text{M}$ residents ($99.58\\%$) occupying elevated flood-prone land. Konaseema is an alluvial island network bounded by the Gautami and Vasishta branches.
- **West Godavari District**: Comprises low-lying aquaculture depressions and coastal canals (Bhimavaram, Narsapur, Tanuku), representing $2.19\\text{M}$ exposed residents ($98.38\\%$).
- **Alluri Sitharama Raju District**: Dominated by high-elevation Papikonda forest hills ($>400\\text{m}$ elevation, $>13^\\circ$ slope), demonstrating low susceptibility to broadsheet inundation ($17.9\\%$ confined to canyon bottoms).

---

## 7. Infrastructure Exposure Breakdown

Using verified point locations from OpenStreetMap evaluated at exact coordinates $(x, y)$:

| Facility Type | Very High Risk Zones | High Risk Zones | Moderate Risk Zones | Low Risk Zones | Total Inside 21 Mandals |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Healthcare Facilities** (Hospitals, Clinics, PHCs) | **679** | **430** | **37** | **0** | **1,146** |
| **Educational Institutions** (Schools, Colleges) | **140** | **155** | **35** | **3** | **333** |
| **Emergency Cyclone / Flood Shelters** | **57** | **6** | **0** | **0** | **63** |
| **TOTAL ESSENTIAL FACILITIES** | **876** ($56.8\\%$) | **591** ($38.3\\%$) | **72** ($4.7\\%$) | **3** ($0.2\\%$) | **1,542** |""".splitlines()

if start_idx is not None and end_idx is not None:
    updated_lines = lines[:start_idx] + new_lines_block + lines[end_idx+1:]
    report_path.write_text("\n".join(updated_lines), encoding="utf-8")
    print("Report updated successfully via line replacement!")
else:
    print("Indices not found.")
