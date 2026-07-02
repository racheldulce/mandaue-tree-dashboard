import pandas as pd
import geopandas as gpd
import numpy as np

df = pd.read_excel(r'c:\Users\LENOVO\Documents\tree maps - Copy\cleaned tree tagging.xlsx', sheet_name='coordinates')
gdf = gpd.read_file(r'c:\Users\LENOVO\Documents\tree maps - Copy\shp_for_tree.gpkg', layer='shp_for_tree')

print('=== BARANGAY NAME COMPARISON ===')
shp_brgys = sorted(gdf['ADM4_EN'].unique())
xls_brgys = sorted(df['Barangay'].unique())
print(f'Shapefile barangays ({len(shp_brgys)}): {shp_brgys}')
print(f'Excel barangays ({len(xls_brgys)}): {xls_brgys}')
print(f'\nIn Excel but NOT in Shapefile:')
print(set(xls_brgys) - set(shp_brgys))
print(f'\nIn Shapefile but NOT in Excel:')
print(set(shp_brgys) - set(xls_brgys))

print('\n=== COORDINATE OUTLIER ANALYSIS ===')
# Expected bounds for Mandaue/Cebu area
# Lat ~ 10.3 to 10.42, Lon ~ 123.88 to 123.98
lat_ok = df['Waypoint Latitude'].between(10.0, 11.0)
lon_ok = df['Waypoint Longitude'].between(123.5, 124.5)
print(f'Rows with lat NOT in [10, 11]: {(~lat_ok & df["Waypoint Latitude"].notna()).sum()}')
print(f'Rows with lon NOT in [123.5, 124.5]: {(~lon_ok & df["Waypoint Longitude"].notna()).sum()}')

# Show outlier lats
outlier_lat = df[df['Waypoint Latitude'].notna() & ~lat_ok][['Barangay', 'GPS no.', 'Waypoint Latitude', 'Waypoint Longitude']]
print(f'\nOutlier latitudes:\n{outlier_lat}')

print('\n=== DBH OUTLIER ANALYSIS ===')
dbh_col = 'DBH (cm)'
print(f'DBH > 300 cm: {(df[dbh_col] > 300).sum()} records')
print(df[df[dbh_col] > 300][['Barangay', 'GPS no.', 'Species name', dbh_col]])

print('\n=== HEIGHT OUTLIER ANALYSIS ===')
ht_col = 'Height (ft)'
print(f'Height > 300 ft: {(df[ht_col] > 300).sum()} records')
print(df[df[ht_col] > 300][['Barangay', 'GPS no.', 'Species name', ht_col]])

print('\n=== DISTRIBUTION STATUS STANDARDIZATION ===')
print('Typos found:')
print(df['Distribution Status'].value_counts(dropna=False))
