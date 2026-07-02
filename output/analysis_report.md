# Tree Inventory GIS Analysis & Conservation Report
**Mandaue City, Cebu, Philippines**

## Executive Summary
This report details the methodology, findings, and conservation implications of a comprehensive spatial analysis conducted on a 9,327-record tree inventory across 27 barangays. The primary objective is to provide a scientifically rigorous and visually professional decision-support tool for Local Government Unit (LGU) environmental planning and biodiversity conservation.

---

## 1. Analysis 1: Tree Distribution Map
**Purpose:** Map the spatial distribution of trees classified by their conservation status.
**Software:** Python 3 (GeoPandas, Matplotlib)
**Methodology:**
- Points were projected to EPSG:32651 (WGS 84 / UTM Zone 51N).
- Trees were categorized into four statuses: Endemic, Indigenous, Introduced, and Unknown.
- A colorblind-friendly palette was applied (Endemic: Dark Red, Indigenous: Dark Green, Introduced: Orange, Unknown: Gray).

**Key Findings:**
- **Indigenous** species dominate the inventory (6,502 records).
- **Introduced** species account for 1,637 records.
- **Endemic** species, which are of highest conservation concern, comprise 932 records.

**Limitations:**
- 2 records lacked coordinates entirely. These were excluded from the spatial point mapping but included in barangay-level aggregations.

**Recommended Conservation Actions:**
- Focus preservation efforts on the 932 endemic trees.
- Avoid planting introduced species in areas where endemic species are currently concentrated.

---

## 2. Analysis 2: Species Richness Map
**Purpose:** Identify barangays with the highest diversity of tree species.
**Software:** Python 3 (GeoPandas, mapclassify, Matplotlib)
**Methodology:**
- Counted the number of unique species names recorded within each barangay.
- Classified the richness counts into 5 categories using Natural Breaks (Jenks) optimization.

**Key Findings:**
- Top species-rich barangays: **Jagobiao** (45 species), **Subangdaku** (45 species), **Guizo** (44 species).
- Lowest richness barangays: **Bakilid** (14 species), **Cambaro** (20 species), **Basak** (21 species).
- Overall richness range: 14 – 45 species per barangay (Mean: 33.9).

**Recommended Conservation Actions:**
- Jagobiao and Subangdaku should be protected as urban biodiversity hubs.
- Barangays with very low richness (e.g., Bakilid) should be prioritized for tree planting programs targeting diverse native species.

---

## 3. Analysis 3: Native Tree Hotspot Analysis
**Purpose:** Identify statistically significant clusters of native (Endemic + Indigenous) trees.
**Software:** Python 3 (GeoPandas, libpysal, esda, Matplotlib)
**Methodology:**
- Filtered dataset to Native trees (7,433 records with valid coordinates).
- Generated a 150m x 150m fishnet grid over the study area.
- Calculated the Getis-Ord Gi* statistic using a Queen contiguity weights matrix.

**Key Findings:**
- A small percentage of grid cells showed statistically significant clustering.
- High + Very High Hotspot cells represent dense contiguous patches of native trees.

**Interpretation:**
Positive z-scores with p-values < 0.05 indicate spatial clustering of native trees that is unlikely to be random. These hotspots represent the most ecologically intact or intensely restored patches in the city.

**Recommended Conservation Actions:**
- Declare "Very High Hotspots" as strict protected zones.
- Establish ecological corridors connecting Moderate and High Hotspots.

---

## 4. Analysis 4: Tree Conservation & Management Priority
**Purpose:** Provide a composite priority score to guide LGU funding and management decisions.
**Software:** Python 3 (GeoPandas, mapclassify, Matplotlib)
**Methodology:**
A composite Conservation Priority Score (0-10 scale) was calculated per barangay:
- **Distribution Status Score (50%):** Weighted sum (Endemic=5, Indigenous=3, Introduced=1, Unknown=0).
- **Species Richness Score (30%):** Count of unique species.
- **Large Tree Score (20%):** Count of mature trees (DBH > 50 cm).

**Justification:**
The scoring weights reflect an ecological hierarchy where geographic restriction (Endemism) is prioritized highest due to global extinction risks, followed by regional ecological baseline contribution (Indigeneity) and community-level parameters (Species Richness), while heavily discounting non-native elements.

**Key Findings:**
- **Top Priority Barangays:** Subangdaku (Score: 10.0), Umapad (7.18), Jagobiao (6.13), Guizo (5.85).
- Subangdaku achieved the maximum score due to having the highest status weight sum, the highest richness (tied with Jagobiao), and the most large trees (48).

**Recommended Conservation Actions:**
- Subangdaku requires immediate attention to protect its mature trees and endemic species.
- Low priority barangays should be the focus of urban greening initiatives to improve their baseline ecological scores.

---
*Report generated automatically as part of the GIS Analysis Pipeline.*
