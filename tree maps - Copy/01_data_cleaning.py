"""
==============================================================================
01_data_cleaning.py
TREE INVENTORY GIS ANALYSIS — PHASE 0: DATA CLEANING & PREPARATION
==============================================================================
Purpose:
    Load, audit, clean, and export the tree inventory dataset and barangay
    boundary layer into a unified GeoPackage ready for all spatial analyses.

Author  : GIS Analysis Pipeline
CRS     : Input EPSG:4326 → Output EPSG:32651 (WGS84/UTM Zone 51N)
Software: Python 3.x, GeoPandas, Pandas, Shapely
==============================================================================
"""

import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import Point
import os
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────────────────────────────────────
BASE_DIR   = r'c:\Users\LENOVO\Documents\tree maps - Copy'
CSV_PATH = os.path.join(BASE_DIR, 'trees - main.csv')
GPKG_IN    = os.path.join(BASE_DIR, 'shp_for_tree.gpkg')
GPKG_OUT   = os.path.join(BASE_DIR, 'outputs', 'data', 'tree_inventory_cleaned.gpkg')

# Target CRS: WGS 84 / UTM Zone 51N — appropriate for Mandaue City, Cebu
TARGET_CRS = 'EPSG:32651'

print("=" * 70)
print("PHASE 0 — DATA CLEANING & PREPARATION")
print("=" * 70)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1: LOAD RAW EXCEL DATA
# ─────────────────────────────────────────────────────────────────────────────
print("\n[1/8] Loading raw dataset...")
df_raw = pd.read_csv(CSV_PATH)
print(f"  Raw records loaded: {len(df_raw):,}")

# Drop rows with empty Species name, DBH, or Height
initial_len = len(df_raw)
df_raw = df_raw.dropna(subset=['Species name', 'DBH(cm)', 'Height (ft)'])
print(f"  Dropped {initial_len - len(df_raw)} records with empty Species name, DBH, or Height.")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2: STANDARDIZE DISTRIBUTION STATUS
# ─────────────────────────────────────────────────────────────────────────────
print("\n[2/8] Standardizing Distribution Status values...")

STATUS_MAP = {
    'Indigenous'  : 'Indigenous',
    'Introduced'  : 'Introduced',
    'Endemic'     : 'Endemic',
    'Intrroduced' : 'Introduced',    # typo
    'Intoduced'   : 'Introduced',    # typo
    'EndemiC'     : 'Endemic',       # case error
    'Unidentified': 'Unknown',       # reclassify
}

df_raw['Distribution Status'] = df_raw['Distribution Status'].map(STATUS_MAP)
# NaN (251 records) → Unknown
df_raw['Distribution Status'] = df_raw['Distribution Status'].fillna('Unknown')

status_counts = df_raw['Distribution Status'].value_counts()
print(f"  Standardized counts:\n{status_counts.to_string()}")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 3: STANDARDIZE BARANGAY NAMES (match shapefile ADM4_EN)
# ─────────────────────────────────────────────────────────────────────────────
print("\n[3/8] Standardizing Barangay names to match shapefile...")

BRGY_MAP = {
    'Canbancalan': 'Cabancalan',
    'Ibabao'     : 'Ibabao-Estancia',
    'Centro'     : 'Centro (Pob.)',
    'Pagsabunga' : 'Pagsabungan',
}
df_raw['Barangay'] = df_raw['Barangay'].replace(BRGY_MAP)
print(f"  Corrections applied: {BRGY_MAP}")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 4: FLAG COORDINATE ISSUES
# ─────────────────────────────────────────────────────────────────────────────
print("\n[4/8] Flagging coordinate issues...")

# Align coordinates that were placed in the wrong column due to duplicate GPS numbers
shifted_mask = df_raw['Latitude'] > 90.0
n_shifted = shifted_mask.sum()
if n_shifted > 0:
    print(f"  Aligning coordinates for {n_shifted} records where latitude was in longitude column...")
    df_raw.loc[shifted_mask, 'Latitude'] = df_raw.loc[shifted_mask, 'Longitude']
    df_raw.loc[shifted_mask, 'Longitude'] = np.nan

df_raw['coord_flag'] = 'valid'

# Flag 1: Null coordinates
null_mask = df_raw['Latitude'].isna() | df_raw['Longitude'].isna()
df_raw.loc[null_mask, 'coord_flag'] = 'null_coords'

# Flag 2: Corrupted latitude (GPS no. stored instead of lat)
# Valid lat for Mandaue/Cebu: 10.0 – 11.0
# Valid lon: 123.5 – 124.5
lat_invalid = (df_raw['Latitude'].notna() &
               ~df_raw['Latitude'].between(10.0, 11.0))
df_raw.loc[lat_invalid, 'coord_flag'] = 'corrupted_lat'

# Flag 3: Corrupted longitude (out of bounds)
lon_invalid = (df_raw['Longitude'].notna() &
               ~df_raw['Longitude'].between(123.5, 124.5))
df_raw.loc[lon_invalid, 'coord_flag'] = 'corrupted_lon'


flag_counts = df_raw['coord_flag'].value_counts()
print(f"  Coordinate flag summary:\n{flag_counts.to_string()}")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 5: FLAG DBH AND HEIGHT OUTLIERS
# ─────────────────────────────────────────────────────────────────────────────
print("\n[5/8] Flagging DBH and Height outliers...")

DBH_MAX_VALID = 500.0   # cm — biological maximum for exceptional trees
HEIGHT_MAX_VALID = 250.0  # ft — biological maximum

df_raw['dbh_flag']    = 'valid'
df_raw['height_flag'] = 'valid'

dbh_col = 'DBH(cm)'
ht_col  = 'Height (ft)'

df_raw[dbh_col] = pd.to_numeric(df_raw[dbh_col], errors='coerce')
df_raw[ht_col] = pd.to_numeric(df_raw[ht_col], errors='coerce')

df_raw.loc[df_raw[dbh_col] > DBH_MAX_VALID, 'dbh_flag']       = 'outlier'
df_raw.loc[df_raw[ht_col]  > HEIGHT_MAX_VALID, 'height_flag'] = 'outlier'

n_dbh_outliers = (df_raw['dbh_flag'] == 'outlier').sum()
n_ht_outliers  = (df_raw['height_flag'] == 'outlier').sum()
print(f"  DBH outliers (> {DBH_MAX_VALID} cm): {n_dbh_outliers}")
print(f"  Height outliers (> {HEIGHT_MAX_VALID} ft): {n_ht_outliers}")

# Clean DBH for analysis (set outliers to NaN)
df_raw['DBH_clean'] = df_raw[dbh_col].where(df_raw['dbh_flag'] == 'valid', np.nan)
df_raw['Height_clean_ft'] = df_raw[ht_col].where(df_raw['height_flag'] == 'valid', np.nan)
# Convert height to meters for reporting
df_raw['Height_clean_m'] = df_raw['Height_clean_ft'] * 0.3048

# ─────────────────────────────────────────────────────────────────────────────
# STEP 6: CREATE VALID POINT GEODATAFRAME
# ─────────────────────────────────────────────────────────────────────────────
print("\n[6/8] Creating valid point layer...")

# Only include rows with valid coordinates
valid_mask = df_raw['coord_flag'] == 'valid'
df_points = df_raw[valid_mask].copy()
df_points = df_points.reset_index(drop=True)
df_points['tree_id'] = df_points.index + 1

# Create geometry
geometry = [Point(lon, lat) for lon, lat in
            zip(df_points['Longitude'], df_points['Latitude'])]
gdf_points = gpd.GeoDataFrame(df_points, geometry=geometry, crs='EPSG:4326')

# Reproject to UTM Zone 51N
gdf_points = gdf_points.to_crs(TARGET_CRS)

print(f"  Valid point records: {len(gdf_points):,}")
print(f"  Excluded (null): {null_mask.sum():,}")
print(f"  Excluded (corrupted): {lat_invalid.sum():,}")
print(f"  CRS: {gdf_points.crs}")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 7: LOAD AND REPROJECT BARANGAY BOUNDARIES
# ─────────────────────────────────────────────────────────────────────────────
print("\n[7/8] Loading and reprojecting barangay boundaries...")

gdf_brgy = gpd.read_file(GPKG_IN, layer='shp_for_tree')
gdf_brgy = gdf_brgy.to_crs(TARGET_CRS)

# Fix geometry if needed
gdf_brgy['geometry'] = gdf_brgy['geometry'].buffer(0)

# Compute centroids for labeling
gdf_brgy['centroid_x'] = gdf_brgy.geometry.centroid.x
gdf_brgy['centroid_y'] = gdf_brgy.geometry.centroid.y

print(f"  Barangay count: {len(gdf_brgy)}")
print(f"  CRS: {gdf_brgy.crs}")
print(f"  Barangay names: {sorted(gdf_brgy['ADM4_EN'].tolist())}")

# Verify all Excel barangays match shapefile
excel_brgys = set(df_raw['Barangay'].unique())
shp_brgys   = set(gdf_brgy['ADM4_EN'].unique())
unmatched   = excel_brgys - shp_brgys
if unmatched:
    print(f"  WARNING: Excel barangays not in shapefile: {unmatched}")
else:
    print(f"  [OK] All Excel barangay names match shapefile.")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 8: SPATIAL JOIN — VERIFY BARANGAY ATTRIBUTION ON POINTS
# ─────────────────────────────────────────────────────────────────────────────
print("\n[8/8] Spatial join to verify point-barangay attribution...")

gdf_joined = gpd.sjoin(
    gdf_points[['tree_id', 'Barangay', 'Species name', 'DBH_clean',
                 'Height_clean_m', 'Distribution Status', 'coord_flag',
                 'dbh_flag', 'height_flag', 'geometry']],
    gdf_brgy[['ADM4_EN', 'geometry']],
    how='left', predicate='within'
)

# Where spatial join found a match, use spatial barangay; else keep Excel value
gdf_joined['Barangay_spatial'] = gdf_joined['ADM4_EN'].fillna(gdf_joined['Barangay'])
mismatch = (gdf_joined['Barangay'] != gdf_joined['Barangay_spatial']).sum()
print(f"  Points with barangay mismatch (Excel vs. spatial): {mismatch}")

# Filter out points that do not fall within any barangay boundary (where ADM4_EN is NaN)
outside_mask = gdf_joined['ADM4_EN'].isna()
outside_count = outside_mask.sum()
print(f"  Removing {outside_count} points that fall outside all barangay boundaries (border of Tawason and Canduman)...")
gdf_points = gdf_points[~outside_mask].reset_index(drop=True)
gdf_points['tree_id'] = gdf_points.index + 1


# Build the full "all records" table for barangay-level aggregations
df_all = df_raw.copy()
df_all['tree_id'] = df_all.index + 1

# ─────────────────────────────────────────────────────────────────────────────
# EXPORT TO GEOPACKAGE
# ─────────────────────────────────────────────────────────────────────────────
print("\nExporting to GeoPackage...")

# Layer 1: Valid GPS points only
cols_pts = ['tree_id', 'Barangay', 'GPS no.', 'Species name',
            'DBH_clean', 'Height_clean_ft', 'Height_clean_m',
            'Distribution Status', 'coord_flag', 'dbh_flag',
            'height_flag', 'Waypoint Latitude', 'Waypoint Longitude',
            'geometry']
cols_pts_exist = [c for c in cols_pts if c in gdf_points.columns]
gdf_points[cols_pts_exist].to_file(GPKG_OUT, layer='tree_points', driver='GPKG')
print(f"  [OK] Layer 'tree_points' written: {len(gdf_points):,} features")

# Layer 2: Barangay boundaries
gdf_brgy.to_file(GPKG_OUT, layer='barangay_boundaries', driver='GPKG')
print(f"  [OK] Layer 'barangay_boundaries' written: {len(gdf_brgy)} features")

# Layer 3: All records (no geometry) saved as CSV for aggregation
df_all_export = df_all[['tree_id', 'Barangay', 'GPS no.', 'Species name',
                          'DBH_clean', 'Height_clean_ft', 'Height_clean_m',
                          'Distribution Status', 'coord_flag', 'dbh_flag',
                          'height_flag', 'Latitude', 'Longitude']].copy()
csv_out = os.path.join(BASE_DIR, 'outputs', 'data', 'tree_all_records.csv')
df_all_export.to_csv(csv_out, index=False)
print(f"  [OK] All-records CSV written: {len(df_all_export):,} records -> {csv_out}")

# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY REPORT
# ─────────────────────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("CLEANING SUMMARY REPORT")
print("=" * 70)
print(f"  Total raw records           : {len(df_raw):,}")
print(f"  Valid GPS point records     : {len(gdf_points):,}")
print(f"  Excluded (null coords)      : {null_mask.sum():,}")
print(f"  Excluded (corrupted lat)    : {lat_invalid.sum():,}")
print(f"  Distribution Status fixed   : 267 (typos + NaN)")
print(f"  Barangay names corrected    : 4")
print(f"  DBH outliers flagged        : {n_dbh_outliers}")
print(f"  Height outliers flagged     : {n_ht_outliers}")
print(f"\n  Distribution Status (cleaned):")
print(df_raw['Distribution Status'].value_counts().to_string())
print(f"\n  Output GeoPackage: {GPKG_OUT}")
print(f"  Output CRS: {TARGET_CRS}")
print("\n[OK] Phase 0 complete — ready for spatial analyses.\n")
