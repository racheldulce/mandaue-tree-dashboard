import pandas as pd
import json
import numpy as np

# Load dataset
df = pd.read_csv(r"c:\Users\LENOVO\Documents\2 maps\dataset\tree_all_records.csv")

# Clean numerical columns
def safe_numeric(col):
    return pd.to_numeric(col, errors='coerce').fillna(0)

if 'DBH_clean' in df.columns:
    df['dbh'] = safe_numeric(df['DBH_clean'])
elif 'dbh' in df.columns:
    df['dbh'] = safe_numeric(df['dbh'])
else:
    df['dbh'] = 0

if 'Height_clean_ft' in df.columns:
    df['height'] = safe_numeric(df['Height_clean_ft'])
elif 'height' in df.columns:
    df['height'] = safe_numeric(df['height'])
else:
    df['height'] = 0

if 'Latitude' in df.columns:
    df['lat'] = safe_numeric(df['Latitude'])
if 'Longitude' in df.columns:
    df['lon'] = safe_numeric(df['Longitude'])

# Standardize columns
brgy_col = [col for col in df.columns if 'brgy' in col.lower() or 'barangay' in col.lower()][0]
species_col = 'Species name' if 'Species name' in df.columns else [col for col in df.columns if 'species' in col.lower()][0]
status_col = 'Distribution Status' if 'Distribution Status' in df.columns else [col for col in df.columns if 'status' in col.lower()][0]
gps_col = 'GPS no.' if 'GPS no.' in df.columns else 'tree_id'

df[brgy_col] = df[brgy_col].fillna('Unknown')
df[species_col] = df[species_col].fillna('Unidentified')
df[status_col] = df[status_col].fillna('Unknown')

# 1. Generate DATA.brgyStats
# {barangay, tree_count, avg_dbh, avg_height, species_count}
brgyStats = []
for brgy, group in df.groupby(brgy_col):
    valid_dbh = group[group['dbh'] > 0]['dbh']
    valid_ht = group[group['height'] > 0]['height']
    brgyStats.append({
        "barangay": brgy,
        "tree_count": int(len(group)),
        "avg_dbh": float(valid_dbh.mean()) if not valid_dbh.empty else 0.0,
        "avg_height": float(valid_ht.mean()) if not valid_ht.empty else 0.0,
        "species_count": int(group[species_col].nunique())
    })
brgyStats = sorted(brgyStats, key=lambda x: x['tree_count'], reverse=True)

# 2. Generate DATA.statusByBrgy
# {barangay, Indigenous, Introduced, Endemic, Unknown}
statusByBrgy = []
status_counts = df.groupby([brgy_col, status_col]).size().unstack(fill_value=0)
for brgy in status_counts.index:
    row = {"barangay": brgy}
    for stat in ['Indigenous', 'Introduced', 'Endemic', 'Unknown']:
        row[stat] = int(status_counts.loc[brgy, stat]) if stat in status_counts.columns else 0
    statusByBrgy.append(row)

# 3. Generate DATA.topSpecies
top_sp = df[species_col].value_counts().head(15)
topSpecies = [[sp, int(count)] for sp, count in top_sp.items()]

# 4. Generate DATA.geoTrees
# {gps_no, brgy, dbh, height, species, status, lat, lon, cluster, intensity}
geoTrees = []
for idx, row in df.iterrows():
    geoTrees.append({
        "gps_no": str(row[gps_col]),
        "brgy": str(row[brgy_col]),
        "dbh": float(row['dbh']),
        "height": float(row['height']),
        "species": str(row[species_col]),
        "status": str(row[status_col]),
        "lat": float(row['lat']) if 'lat' in df.columns else 0.0,
        "lon": float(row['lon']) if 'lon' in df.columns else 0.0,
        "cluster": -1,
        "intensity": "Noise"
    })

# Write to data.js
data_obj = {
    "brgyStats": brgyStats,
    "statusByBrgy": statusByBrgy,
    "topSpecies": topSpecies,
    "geoTrees": geoTrees
}
with open(r"c:\Users\LENOVO\Documents\2 maps\data.js", "w", encoding="utf-8") as f:
    f.write("const DATA = " + json.dumps(data_obj) + ";\n")

print("Generated data.js successfully!")

# Print stats for LGU report
print("\n--- BARANGAY TREE COUNTS (Top 10) ---")
for i, b in enumerate(brgyStats[:10]):
    print(f"| {i+1} | {b['barangay']} | {b['tree_count']:,} | {b['avg_dbh']:.2f} | {b['avg_height']:.2f} | {b['species_count']} |")

print("\n--- TOP 15 SPECIES BY COUNT ---")
for i, sp in enumerate(topSpecies):
    # Find its status
    stat = df[df[species_col] == sp[0]][status_col].mode()
    stat_val = stat.iloc[0] if not stat.empty else "Unknown"
    print(f"| {i+1} | {sp[0]} | {sp[1]:,} | {stat_val} |")

print("\n--- ENDEMIC TREES PER BARANGAY (Top 5) ---")
endemic_sort = sorted(statusByBrgy, key=lambda x: x['Endemic'], reverse=True)
for i, b in enumerate(endemic_sort[:5]):
    print(f"| {b['barangay']} | {b['Endemic']} |")

print("\n--- HIGHEST INTRODUCED SPECIES CONCENTRATIONS (Top 5) ---")
intro_sort = []
for b in statusByBrgy:
    total = b['Indigenous'] + b['Introduced'] + b['Endemic'] + b['Unknown']
    if total > 0:
        intro_sort.append((b['barangay'], b['Introduced'], b['Introduced']/total*100))
intro_sort = sorted(intro_sort, key=lambda x: x[1], reverse=True)
for i, b in enumerate(intro_sort[:5]):
    print(f"| {b[0]} | {b[1]} | {b[2]:.1f}% |")

print("\n--- TOTALS ---")
print(f"Total Trees: {len(df)}")
print(f"Unknown Trees: {len(df[df[species_col].str.lower().str.contains('unknown|unidentified', na=False)])}")
