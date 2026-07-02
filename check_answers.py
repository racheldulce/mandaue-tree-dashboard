import pandas as pd
import numpy as np

df = pd.read_csv(r"c:\Users\LENOVO\Documents\2 maps\dataset\tree_all_records.csv")

print(f"Columns: {df.columns.tolist()}")

brgy_col = [col for col in df.columns if 'brgy' in col.lower() or 'barangay' in col.lower()]
if brgy_col:
    bc = brgy_col[0]
else:
    bc = 'Location' # Fallback

lat_col = [col for col in df.columns if 'lat' in col.lower()]
lon_col = [col for col in df.columns if 'lon' in col.lower() or 'lng' in col.lower()]

print("\n--- Overall ---")
print(f"Total records: {len(df)}")
if brgy_col:
    print(f"Total barangays: {df[bc].nunique()}")

if lat_col and lon_col:
    lat = lat_col[0]
    lon = lon_col[0]
    missing_coords = df[lat].isna().sum() + df[lon].isna().sum()
    missing_points = df[[lat, lon]].isna().any(axis=1).sum()
    print(f"Missing coordinates (points without valid lat/lon): {missing_points}")

print("\n--- Analysis 1 ---")
status_col = [col for col in df.columns if 'status' in col.lower() or 'distribution' in col.lower()]
if status_col:
    sc = status_col[0]
    print(df[sc].value_counts())
else:
    print("Could not find status column. Columns:", df.columns)

print("\n--- Analysis 2 ---")
species_col = [col for col in df.columns if ('species' in col.lower() or 'name' in col.lower()) and 'brgy' not in col.lower() and 'sci' not in col.lower() and 'local' not in col.lower()]
if species_col:
    spc = species_col[0]
    if brgy_col:
        richness = df.groupby(bc)[spc].nunique()
        print("Top 3 richness:")
        print(richness.nlargest(3))
        print("Bottom 3 richness:")
        print(richness.nsmallest(3))
        print(f"Range: {richness.min()} - {richness.max()} (Mean: {richness.mean():.1f})")
else:
    print("Could not find species column. Columns:", df.columns)
    
print("\n--- Analysis 3 ---")
if status_col and lat_col and lon_col:
    sc = status_col[0]
    native_df = df[df[sc].isin(['Endemic', 'Indigenous'])]
    native_with_coords = native_df.dropna(subset=[lat, lon])
    print(f"Native trees with valid coords: {len(native_with_coords)}")
    
print("\n--- Analysis 4 ---")
if status_col and species_col and brgy_col:
    sc = status_col[0]
    spc = species_col[0]
    dbh_col = [col for col in df.columns if 'dbh' in col.lower()]
    
    if dbh_col:
        dbh_c = dbh_col[0]
        
        status_map = {'Endemic': 5, 'Indigenous': 3, 'Introduced': 1, 'Unknown': 0}
        df['status_weight'] = df[sc].map(status_map).fillna(0)
        dist_score_raw = df.groupby(bc)['status_weight'].sum()
        
        richness = df.groupby(bc)[spc].nunique()
        
        df[dbh_c] = pd.to_numeric(df[dbh_c], errors='coerce')
        large_trees = df[df[dbh_c] > 50].groupby(bc).size()
        
        scores = pd.DataFrame({'dist_raw': dist_score_raw, 'richness': richness, 'large_trees': large_trees}).fillna(0)
        
        def min_max_scale(series):
            if series.max() == series.min():
                return pd.Series(0, index=series.index)
            return (series - series.min()) / (series.max() - series.min())
            
        scores['dist_scaled'] = min_max_scale(scores['dist_raw'])
        scores['richness_scaled'] = min_max_scale(scores['richness'])
        scores['large_scaled'] = min_max_scale(scores['large_trees'])
        
        scores['final_score'] = (scores['dist_scaled'] * 50 + scores['richness_scaled'] * 30 + scores['large_scaled'] * 20) / 10
        
        print("\nTop 5 Priority Barangays (Scaled 0-10):")
        print(scores['final_score'].nlargest(5))
        
        if 'Subangdaku' in scores.index:
            print(f"\nSubangdaku large trees: {scores.loc['Subangdaku', 'large_trees']}")
            print(f"Subangdaku richness: {scores.loc['Subangdaku', 'richness']}")
            print(f"Subangdaku dist raw score: {scores.loc['Subangdaku', 'dist_raw']}")
        if 'Jagobiao' in scores.index:
            print(f"Jagobiao richness: {scores.loc['Jagobiao', 'richness']}")
