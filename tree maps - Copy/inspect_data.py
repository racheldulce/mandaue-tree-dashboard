import pandas as pd
import geopandas as gpd
import numpy as np

# Load Excel
df = pd.read_excel(r'c:\Users\LENOVO\Documents\tree maps - Copy\cleaned tree tagging.xlsx', sheet_name='coordinates')

print('=== EXCEL DATASET OVERVIEW ===')
print(f'Total rows: {len(df)}')
print(f'\nColumn dtypes:')
print(df.dtypes)
print(f'\nFirst 5 rows:')
print(df.head())
print(f'\nDistribution Status values:')
print(df['Distribution Status'].value_counts(dropna=False))
print(f'\nBarangay values:')
print(df['Barangay'].value_counts(dropna=False))
print(f'\nMissing values:')
print(df.isnull().sum())
lat_col = 'Waypoint Latitude'
lon_col = 'Waypoint Longitude'
print(f'\nLat range: {df[lat_col].min()} to {df[lat_col].max()}')
print(f'Lon range: {df[lon_col].min()} to {df[lon_col].max()}')
dbh_col = 'DBH (cm)'
ht_col = 'Height (ft)'
print(f'\nDBH (cm) stats:')
print(df[dbh_col].describe())
print(f'\nHeight (ft) stats:')
print(df[ht_col].describe())

# Duplicates
print(f'\nDuplicate rows: {df.duplicated().sum()}')
print(f'Duplicate GPS no: {df["GPS no."].duplicated().sum()}')

# Load GeoPackage
print('\n=== GEOPACKAGE OVERVIEW ===')
layers = gpd.list_layers(r'c:\Users\LENOVO\Documents\tree maps - Copy\shp_for_tree.gpkg')
print(f'Layers: {layers}')
for layer in layers['name']:
    gdf = gpd.read_file(r'c:\Users\LENOVO\Documents\tree maps - Copy\shp_for_tree.gpkg', layer=layer)
    print(f'\nLayer: {layer}')
    print(f'Shape: {gdf.shape}')
    print(f'CRS: {gdf.crs}')
    print(f'Geometry types: {gdf.geom_type.value_counts()}')
    print(f'Columns: {list(gdf.columns)}')
    print(f'First 5 rows:')
    print(gdf.head())
    print(f'Null geometries: {gdf.geometry.isnull().sum()}')
    print(f'Invalid geometries: {(~gdf.geometry.is_valid).sum()}')
    if 'Barangay' in gdf.columns or any('arang' in c.lower() for c in gdf.columns):
        bname_col = [c for c in gdf.columns if 'arang' in c.lower()][0] if any('arang' in c.lower() for c in gdf.columns) else 'Barangay'
        print(f'Barangay names in shapefile:')
        print(sorted(gdf[bname_col].tolist()))
