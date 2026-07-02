# 🌳 LGU MULTI-DATA ANALYSIS REPORT
## Mandaue City Urban Tree Inventory — Spatio-Temporal Analysis
**Prepared by:** LGU Geospatial and Data Intelligence Analysis System  
**Jurisdiction:** Mandaue City, Cebu, Philippines  
**Coverage:** 27 Barangays  
**Data Source:** Urban Tree Inventory Dashboard (tree_dashboard.html + data.js)  
**Report Date:** June 30, 2026

---

## A. OBSERVATIONS
*(Pure Data Description — What is Directly Shown)*

### 📊 Key Performance Indicators

| Indicator | Value |
|---|---|
| Total Trees Tagged | 9,327 trees across 27 barangays |
| Unique Species Recorded | 67+ species |
| Endemic Trees | 932 trees (10.0% of total) |
| Average DBH | ~25 cm |

### Distribution Status Breakdown

| Status | Count | Percentage |
|---|---|---|
| Indigenous | 6,502 | 69.7% |
| Introduced | 1,637 | 17.6% |
| Endemic | 932 | 10.0% |
| Unknown | 256 | 2.7% |
| TOTAL | 9,342 | 100% |

### Barangay Tree Counts

| Rank | Barangay | Tree Count | Avg DBH (cm) | Avg Height (ft) | Species |
|---|---|---|---|---|---|
| 1 | Subangdaku | 1,162 | 21.64 | 13.86 | 44 |
| 2 | Umapad | 1,133 | 19.91 | 14.42 | 24 |
| 3 | Guizo | 531 | 27.28 | 23.89 | 44 |
| 4 | Casili | 513 | 21.74 | 19.34 | 42 |
| 5 | Centro | 492 | 26.13 | 17.98 | 39 |
| 6 | Pakna-an | 413 | 19.12 | 15.62 | 42 |
| 7 | Casuntingan | 400 | 21.91 | 17.00 | 33 |
| 8 | Labogon | 384 | 28.47 | 23.16 | 43 |
| 9 | Tawason | 379 | 23.62 | 18.92 | 39 |
| 10 | Mantuyong | 379 | 22.59 | 18.45 | 23 |
| 11 | Jagobiao | 375 | 31.06 | 23.26 | 41 |
| 12 | Maguikay | 343 | 24.92 | 18.32 | 39 |
| 13 | Looc | 348 | 25.45 | 20.36 | 37 |
| 14 | Ibabao | 336 | 27.71 | 21.75 | 26 |
| 15 | Canduman | 307 | 26.87 | 15.64 | 35 |
| 16 | Tipolo | 246 | 27.82 | 21.18 | 33 |
| 17 | Canbancalan | 231 | 27.76 | 19.20 | 39 |
| 18 | Cubacub | 210 | 29.17 | 25.32 | 31 |
| 19 | Tabok | 193 | 25.35 | 20.23 | 33 |
| 20 | Pagsabunga | 183 | 42.61 | 22.14 | 33 |
| 21 | Banilad | 165 | 23.60 | 18.44 | 37 |
| 22 | Alang-alang | 150 | 25.97 | 20.91 | 24 |
| 23 | Opao | 124 | 21.12 | 16.92 | 28 |
| 24 | Tingub | 118 | 28.89 | 22.64 | 33 |
| 25 | Basak | 106 | 29.44 | 24.08 | 21 |
| 26 | Bakilid | 63 | 24.35 | 21.84 | 14 |
| 27 | Cambaro | 58 | 29.09 | 20.64 | 20 |

### Top 15 Species by Count

| Rank | Species | Count | Status |
|---|---|---|---|
| 1 | Mahogany | 1,481 | Indigenous |
| 2 | Tugas (Vitex parviflora) | 840 | ENDEMIC |
| 3 | Talisay | 819 | Indigenous |
| 4 | Narra | 745 | Indigenous |
| 5 | Dakit | 515 | Indigenous |
| 6 | Indian tree | 444 | Introduced |
| 7 | Nem tree | 435 | Introduced |
| 8 | Fire tree | 301 | Indigenous |
| 9 | Unidentified | 260 | Unknown |
| 10 | Awom | 255 | Indigenous |
| 11 | Rubber tree | 236 | Indigenous |
| 12 | Mangga | 223 | Indigenous |
| 13 | Indian | 203 | Introduced |
| 14 | Mansinitas | 185 | Indigenous |
| 15 | Nangka | 184 | Indigenous |

### Endemic Trees per Barangay (Top)

| Barangay | Endemic Count |
|---|---|
| Subangdaku | 360 |
| Umapad | 270 |
| Casili | 71 |
| Tipolo | 39 |
| Mantuyong | 32 |
| Centro | 26 |
| All others | less than 20 |

### Highest Introduced Species Concentrations

| Barangay | Introduced Count | % of Local Total |
|---|---|---|
| Casuntingan | 223 | 55.8% |
| Subangdaku | 178 | 15.3% |
| Guizo | 141 | 27.3% |
| Pakna-an | 102 | 24.7% |
| Maguikay | 87 | 25.4% |

---

## B. PATTERNS AND TRENDS
*(What is Happening — Relationships, Clusters, Anomalies)*

1. EXTREME CONCENTRATION AT TWO BARANGAYS
   Subangdaku (1,162) and Umapad (1,133) together hold 24.6% of all 9,327 trees 
   despite being just 2 of 27 barangays. A significant spatial imbalance.

2. LOW-COVERAGE BARANGAYS
   Cambaro (58), Bakilid (63), Basak (106), and Tingub (118) are critically 
   underrepresented — fewer than 120 trees each, indicating either data gaps or 
   genuine urban canopy deficits.

3. ENDEMIC HOTSPOT DOMINANCE
   Subangdaku (360) and Umapad (270) hold 67.1% of all 932 endemic trees city-wide.
   These two barangays are ecological critical zones for endemic species survival.

4. CASUNTINGAN ANOMALY — INTRODUCED DOMINANCE
   The only barangay where introduced species (223) outnumber indigenous (168),
   at a 55.8% introduced ratio. An ecological imbalance and invasion risk hotspot.

5. PAGSABUNGA DBH OUTLIER
   Average DBH of 42.61 cm — nearly double the city average (~25 cm). Indicates 
   a pocket of very mature, old-growth-like trees or remnant forested land.

6. SUBANGDAKU — HIGH COUNT, SHORT HEIGHT
   Despite the most trees (1,162), Subangdaku has the lowest avg height (13.86 ft),
   suggesting mostly young or plantation-style plantings, not mature canopy.

7. HIGH INTRODUCED SPECIES IN URBAN CORE
   Guizo, Pakna-an, Canduman, Maguikay — all commercially active — show the highest
   introduced species concentrations (80-143), reflecting aesthetic over ecological planting.

8. 260 UNIDENTIFIED TREES
   "Unidentified" species is tied 9th most common. This is a data quality gap 
   affecting all conservation classification efforts.

9. SPECIES RICHNESS VS TREE COUNT DISCONNECT
   Guizo (531 trees, 44 species) matches Subangdaku (1,162 trees, 44 species) 
   in diversity — Guizo is more ecologically dense per unit area.

10. MAHOGANY DOMINANCE
    1,481 trees = 15.9% of all trees. Reflects past reforestation programs, 
    not natural diversity. May signal plantation dependency over ecological balance.

---

## C. LGU IMPLICATIONS
*(Meaning for Governance and Community Impact)*

ENVIRONMENTAL / ECOLOGICAL
- Subangdaku and Umapad are ecological lifelines. Urbanization there risks losing 
  67% of all endemic trees city-wide — a non-recoverable ecological loss.
- Casuntingan is at a tipping point: introduced species outcompeting native flora, 
  threatening local pollinators and long-term forest integrity.
- Pagsabunga's old trees (DBH >40cm) are irreplaceable carbon sinks and wildlife 
  habitat. Loss to development cannot be undone.

URBAN PLANNING AND GREEN INFRASTRUCTURE
- Cambaro, Bakilid, Basak, Tingub are critically underserved. Residents lack 
  shade, urban cooling, and air quality benefits from trees.
- Subangdaku's low tree height means dense stands provide minimal shade or 
  cooling benefits — a common issue with underpruned monoculture plantings.
- 2.8% Unknown species prevents accurate DENR compliance reporting for the city.

DISASTER RISK / CLIMATE RESILIENCE
- Urban heat island risk is highest in low-canopy barangays. 
  Cambaro, Bakilid, Basak, Tingub are most vulnerable to extreme heat.
- Introduced species (Mahogany, Indian Tree) have shallower root systems — 
  higher windthrow risk during typhoons, posing safety hazards.

HEALTH AND COMMUNITY WELL-BEING
- Low tree cover areas face greater dust, heat, noise pollution, 
  and reduced mental health benefits.
- Tugas (Vitex parviflora) provides nectar for native pollinators essential to 
  local food systems (fruit trees). Protecting it supports food security.

---

## D. RECOMMENDATIONS
*(Actionable LGU Actions)*

=== URGENT (Immediate Action Required) ===

1. DECLARE SUBANGDAKU AND UMAPAD AS PROTECTED URBAN GREEN ZONES
   - Pass a City Ordinance designating these two barangays as Urban Green Buffer Zones.
   - Require ECCs for any construction within 50m of endemic tree clusters.
   - Cost: Administrative/legislative — LOW cost, HIGH impact.

2. EMERGENCY SPECIES IDENTIFICATION DRIVE — 260 UNKNOWN TREES
   - Deploy Barangay tree tagging teams with DENR and local universities 
     (USC, UV Gullas) to identify all 260 "Unknown/Unidentified" trees.
   - Target: Update inventory database within 60 days.
   - Use updated data to refine city's DENR species compliance report.

3. CASUNTINGAN INTRODUCED SPECIES MANAGEMENT PLAN
   - Audit all 223 introduced trees in Casuntingan.
   - Phased replacement plan: replace dying/removed introduced trees 
     100% with indigenous/endemic species (Tugas, Narra, Talisay).

=== SHORT-TERM (Within 6 Months) ===

4. EMERGENCY GREENING PROGRAM FOR UNDERSERVED BARANGAYS
   - Allocate planting budget for Cambaro, Bakilid, Basak, Tingub.
   - Target: minimum 150 additional trees per barangay using fast-growing 
     indigenous species (Talisay, Narra, Fire Tree).
   - Coordinate with Barangay Captains for site selection.

5. PAGSABUNGA HERITAGE TREE DOCUMENTATION AND PROTECTION
   - Document all trees with DBH >= 40 cm as candidate Heritage Trees.
   - Apply for DENR Heritage Tree designation for qualified specimens.
   - Install protective signage and prohibit removal without LGU permit.

=== MEDIUM-TERM (6-18 Months) ===

6. DIVERSIFY MAHOGANY-DOMINANT AREAS WITH ENDEMIC SPECIES
   - Where Mahogany > 25% of local trees, introduce diversity-planting.
   - Target: Plant Tugas, Kulo, and other endemic species alongside Mahogany.
   - Partner with schools and barangay councils for community tree nurseries.

7. ESTABLISH CITY-WIDE URBAN TREE MONITORING SYSTEM
   - Upgrade dashboard with annual re-inventory protocols (every January).
   - Include growth tracking (DBH change over time), mortality tracking, 
     and introduced species spread monitoring.
   - Assign one Barangay Environmental Officer (BEO) per barangay for 
     quarterly tree condition reports.

---

## E. PRIORITY INSIGHTS
*(Top 3 Urgent Issues for Executive Briefing)*

===================================================================
PRIORITY 1 — ENDEMIC SPECIES CONCENTRATION RISK  [CRITICAL]
===================================================================
Subangdaku and Umapad hold 630 of 932 total endemic trees (67.1%).
If these two barangays face urban development pressure, road widening, 
or informal settlement expansion, the city risks losing the majority of 
its ecologically significant endemic species in a single event.

ACTION REQUIRED: Legal protection ordinance + DENR coordination within 30 days.

===================================================================
PRIORITY 2 — CASUNTINGAN ECOLOGICAL IMBALANCE  [HIGH]
===================================================================
Casuntingan is the ONLY barangay where introduced species outnumber 
native trees (55.8% introduced). This active imbalance will worsen over 
time without intervention, potentially spreading to adjacent barangays 
(Guizo, Alang-alang, Looc).

ACTION REQUIRED: Invasive species audit + phased replacement program within 90 days.

===================================================================
PRIORITY 3 — CRITICAL CANOPY GAPS IN 4 BARANGAYS  [HIGH]
===================================================================
Cambaro, Bakilid, Basak, and Tingub collectively have only 345 trees — 
fewer than a single top barangay holds alone. These areas face highest 
heat risk, lowest air quality, and weakest disaster resilience.

ACTION REQUIRED: Emergency greening budget in next supplemental budget cycle.

---

## DATA QUALITY NOTES (Limitations)

| Issue | Details | Recommended Action |
|---|---|---|
| 260 Unidentified trees | Cannot be classified for conservation policy | Immediate field re-survey |
| Mahogany as Indigenous | May be plantation-origin; needs verification | Species-level expert review |
| Low counts in 4 barangays | May reflect incomplete surveying | Verify survey coverage |
| No temporal comparison | Single-point-in-time only | Add annual re-inventory cycle |

---
*Generated from: Mandaue City Urban Tree Inventory Dashboard (data.js)*
*For: Executive Briefing | Disaster Risk Planning | DENR Compliance | Barangay Decision Making*
*Report Date: June 30, 2026*
