"""
==============================================================================
04_analysis3_hotspot.py
ANALYSIS 3 — NATIVE TREE HOTSPOT POINT MAP (Getis-Ord Gi*)
==============================================================================
Purpose:
    Identify statistically significant spatial clusters (hotspots) of
    endemic and indigenous trees and visualize them as individual points.

Workflow:
    1. Filter tree points to Endemic + Indigenous only (native species)
    2. Create fishnet grid (150 m x 150 m) over study area
    3. Count native trees per grid cell (spatial join)
    4. Run Getis-Ord Gi* using spatial weights matrix
    5. Join Gi* classification back to the individual native tree points
    6. Map points colored by their hotspot class

CRS     : EPSG:32651 (WGS84/UTM Zone 51N)
Output  : PNG 600 dpi, TIFF 600 dpi, SVG, PDF (vector)
Software: Python 3.x, GeoPandas, esda, libpysal, Matplotlib
==============================================================================
"""

import os
import numpy as np
import pandas as pd
import geopandas as gpd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import matplotlib.patheffects as pe
from shapely.geometry import box
import libpysal
from esda.getisord import G_Local
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────────────────────────────────────
BASE_DIR = r'c:\Users\LENOVO\Documents\tree maps - Copy'
GPKG     = os.path.join(BASE_DIR, 'outputs', 'data', 'tree_inventory_cleaned.gpkg')
OUT_DIR  = os.path.join(BASE_DIR, 'outputs', 'maps', 'analysis3_hotspot')
os.makedirs(OUT_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1: LOAD AND FILTER NATIVE TREES
# ─────────────────────────────────────────────────────────────────────────────
print("[1/7] Loading data and filtering native trees...")
gdf_pts  = gpd.read_file(GPKG, layer='tree_points')
gdf_brgy = gpd.read_file(GPKG, layer='barangay_boundaries')

native_mask = gdf_pts['Distribution Status'].isin(['Endemic', 'Indigenous'])
gdf_native  = gdf_pts[native_mask].copy()

print(f"  Total tree points: {len(gdf_pts):,}")
print(f"  Native trees (Endemic + Indigenous): {len(gdf_native):,}")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2: CREATE FISHNET GRID
# ─────────────────────────────────────────────────────────────────────────────
print("\n[2/7] Creating fishnet grid (150m x 150m)...")

CELL_SIZE = 150

xmin, ymin, xmax, ymax = gdf_brgy.total_bounds
cols = np.arange(xmin - CELL_SIZE, xmax + CELL_SIZE, CELL_SIZE)
rows = np.arange(ymin - CELL_SIZE, ymax + CELL_SIZE, CELL_SIZE)

grid_cells = []
for x in cols:
    for y in rows:
        grid_cells.append(box(x, y, x + CELL_SIZE, y + CELL_SIZE))

gdf_grid = gpd.GeoDataFrame({'geometry': grid_cells}, crs='EPSG:32651')
study_area = gdf_brgy.unary_union
gdf_grid   = gdf_grid[gdf_grid.geometry.intersects(study_area)].copy().reset_index(drop=True)
gdf_grid['cell_id'] = range(len(gdf_grid))

# ─────────────────────────────────────────────────────────────────────────────
# STEP 3: COUNT NATIVE TREES PER CELL
# ─────────────────────────────────────────────────────────────────────────────
print("\n[3/7] Counting native trees per grid cell...")

joined = gpd.sjoin(gdf_native, gdf_grid[['cell_id', 'geometry']], how='left', predicate='within')
count_per_cell = joined.groupby('cell_id').size().reset_index(name='native_count')

gdf_grid = gdf_grid.merge(count_per_cell, on='cell_id', how='left')
gdf_grid['native_count'] = gdf_grid['native_count'].fillna(0).astype(int)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 4: BUILD SPATIAL WEIGHTS MATRIX & RUN Gi*
# ─────────────────────────────────────────────────────────────────────────────
print("\n[4/7] Building spatial weights & Running Gi*...")

w = libpysal.weights.Queen.from_dataframe(gdf_grid, silence_warnings=True)
w.transform = 'R'

y = gdf_grid['native_count'].values.astype(float)
gi_star = G_Local(y, w, transform='R', star=True, permutations=999)

gdf_grid['gi_z']  = gi_star.Zs
gdf_grid['gi_p']  = gi_star.p_sim

# ─────────────────────────────────────────────────────────────────────────────
# STEP 5: CLASSIFY RESULTS
# ─────────────────────────────────────────────────────────────────────────────
print("\n[5/7] Classifying Gi* results...")

def classify_gi(row):
    z = row['gi_z']
    p = row['gi_p']
    if z > 2.576 and p < 0.01:   return 'Very High Hotspot'
    elif z > 1.96 and p < 0.05:  return 'High Hotspot'
    elif z > 1.645 and p < 0.10: return 'Moderate Hotspot'
    elif z < -2.576 and p < 0.01:return 'Very Low Coldspot'
    elif z < -1.96 and p < 0.05: return 'Coldspot'
    else:                        return 'Not Significant'

gdf_grid['hotspot_class'] = gdf_grid.apply(classify_gi, axis=1)

# Join class back to native points
gdf_native = gpd.sjoin(gdf_native, gdf_grid[['cell_id', 'hotspot_class', 'geometry']], how='left', predicate='within')
gdf_native['hotspot_class'] = gdf_native['hotspot_class'].fillna('Not Significant')

# Save grid to GeoPackage just in case
grid_out = os.path.join(BASE_DIR, 'outputs', 'data', 'tree_inventory_cleaned.gpkg')
gdf_grid.to_file(grid_out, layer='hotspot_grid', driver='GPKG')

# ─────────────────────────────────────────────────────────────────────────────
# COLOR PALETTE
# ─────────────────────────────────────────────────────────────────────────────
HOTSPOT_COLORS = {
    'Very High Hotspot': '#800000',    # Dark red
    'High Hotspot'     : '#E63333',    # Red
    'Moderate Hotspot' : '#FF9900',    # Orange
    'Not Significant'  : '#EEEEEE',    # Light gray
    'Coldspot'         : '#3366CC',    # Blue
    'Very Low Coldspot': '#003399',    # Dark blue
}

CLASS_ORDER = [
    'Very High Hotspot', 'High Hotspot', 'Moderate Hotspot',
    'Not Significant', 'Coldspot', 'Very Low Coldspot'
]

# ─────────────────────────────────────────────────────────────────────────────
# UTILITY FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
def add_north_arrow(ax, x=0.96, y=0.15, size=0.055):
    ax_x = ax.get_position().x0 + ax.get_position().width  * x
    ax_y = ax.get_position().y0 + ax.get_position().height * y
    fig  = ax.get_figure()
    arrow_ax = fig.add_axes([ax_x - 0.028, ax_y - 0.025, size, size * 1.4], anchor='C')
    arrow_ax.set_xlim(-1, 1); arrow_ax.set_ylim(-1.2, 1.2); arrow_ax.axis('off')
    arrow_ax.fill([0, -0.45, 0, 0.45], [1.0, -0.8, -0.4, -0.8], color='#222222', zorder=3)
    arrow_ax.fill([0, -0.45, 0, 0.45], [-1.0, -0.8, -0.4, -0.8], color='#FFFFFF', ec='#222222', lw=0.8, zorder=3)
    arrow_ax.text(0, 1.05, 'N', ha='center', va='bottom', fontsize=8, fontweight='bold', color='#222222')

def add_scale_bar(ax, gdf_brgy, length_km=1, pad_frac=0.04):
    xmin_b, ymin_b, xmax_b, ymax_b = gdf_brgy.total_bounds
    bar_x = xmin_b + (xmax_b - xmin_b) * pad_frac
    bar_y = ymin_b + (ymax_b - ymin_b) * pad_frac
    length = length_km * 1000
    bar_h  = length * 0.025
    for i in range(4):
        color = '#222222' if i % 2 == 0 else '#FFFFFF'
        ax.fill_between([bar_x + i * (length/4), bar_x + (i + 1) * (length/4)],
                        [bar_y - bar_h, bar_y - bar_h], [bar_y, bar_y],
                        color=color, ec='#222222', lw=0.6, zorder=7)
    ax.text(bar_x,            bar_y - bar_h * 1.5, '0', ha='center', va='top', fontsize=6.5, color='#333333', zorder=8)
    ax.text(bar_x + length/2, bar_y - bar_h * 1.5, f'{length_km//2} km', ha='center', va='top', fontsize=6.5, color='#333333', zorder=8)
    ax.text(bar_x + length,   bar_y - bar_h * 1.5, f'{length_km} km', ha='center', va='top', fontsize=6.5, color='#333333', zorder=8)

def label_barangays(ax, gdf_brgy, fontsize=6.0):
    offsets = {'Centro (Pob.)': (200, -300), 'Looc': (100, -200), 'Maguikay': (-200, 200), 'Cambaro': (0, 200), 'Bakilid': (0, -200)}
    for _, row in gdf_brgy.iterrows():
        cx, cy = row.geometry.centroid.x, row.geometry.centroid.y
        name   = row['ADM4_EN']
        dx, dy = offsets.get(name, (0, 0))
        txt = ax.text(cx + dx, cy + dy, name, ha='center', va='center',
                      fontsize=fontsize, color='#111111', fontweight='semibold', zorder=10)
        txt.set_path_effects([pe.withStroke(linewidth=2.5, foreground='white')])

def save_map(fig, out_dir, name):
    for fmt, dpi in [('png', 600), ('tif', 600), ('svg', None), ('pdf', None)]:
        fpath = os.path.join(out_dir, f'{name}.{fmt}')
        kw = dict(bbox_inches='tight', facecolor='white', edgecolor='none')
        if dpi: kw['dpi'] = dpi
        fig.savefig(fpath, **kw)
        print(f"  Saved: {fpath}")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 7: BUILD MAP
# ─────────────────────────────────────────────────────────────────────────────
def build_hotspot_map(figsize=(14, 12), label_size=6.0, title_size=14,
                       legend_fontsize=9, footer_size=6.5, markerscale=1.0, variant='standard'):

    xmin, ymin, xmax, ymax = gdf_brgy.total_bounds
    pad_x = (xmax - xmin) * 0.04
    pad_y = (ymax - ymin) * 0.04

    fig, ax = plt.subplots(figsize=figsize, facecolor='white')
    ax.set_facecolor('white')

    # ── Barangay boundaries on bottom ─────────────────────────────────────────
    gdf_brgy.plot(ax=ax, facecolor='#F9F9F9', edgecolor='#666666', linewidth=0.8, zorder=1)

    # ── Plot points by hotspot class ──────────────────────────────────────────
    # Plot non-significant first, then colder to hotter so hotspots are on top
    plot_order = ['Not Significant', 'Very Low Coldspot', 'Coldspot', 
                  'Moderate Hotspot', 'High Hotspot', 'Very High Hotspot']
    
    for cls in plot_order:
        sub = gdf_native[gdf_native['hotspot_class'] == cls]
        if len(sub) == 0: continue
        
        # Increase size for more significant points
        base_size = 8 if cls == 'Not Significant' else 14
        if 'Very High' in cls: base_size = 22
        elif 'High' in cls: base_size = 18
        
        # Add edge color for significant points
        edge = 'none' if cls == 'Not Significant' else '#222222'
        lw = 0 if cls == 'Not Significant' else 0.5
        
        sub.plot(
            ax=ax, color=HOTSPOT_COLORS[cls], edgecolor=edge, linewidth=lw,
            markersize=base_size * markerscale, marker='o', alpha=0.85,
            zorder=plot_order.index(cls) + 2
        )

    # ── Grid ─────────────────────────────────────────────────────────────────
    ax.grid(True, linestyle='--', linewidth=0.35, color='#AAAAAA', alpha=0.45, zorder=0)
    ax.tick_params(axis='both', labelsize=6.5, color='#555555', labelcolor='#555555')
    ax.set_xlim(xmin - pad_x, xmax + pad_x)
    ax.set_ylim(ymin - pad_y, ymax + pad_y)

    # ── Labels ───────────────────────────────────────────────────────────────
    label_barangays(ax, gdf_brgy, fontsize=label_size)

    # ── Legend ───────────────────────────────────────────────────────────────
    legend_elements = []
    z_labels = {
        'Very High Hotspot': 'z > 2.58, p < 0.01 (Significant clustering of HIGH values)',
        'High Hotspot'     : 'z > 1.96, p < 0.05 (High concentration)',
        'Moderate Hotspot' : 'z > 1.65, p < 0.10 (Moderate concentration)',
        'Not Significant'  : '|z| ≤ 1.65 (Random / not significant)',
        'Coldspot'         : 'z < -1.96, p < 0.05 (Low concentration)',
        'Very Low Coldspot': 'z < -2.58, p < 0.01 (Significant clustering of LOW values)',
    }
    
    for cls in CLASS_ORDER:
        n_pts = len(gdf_native[gdf_native['hotspot_class'] == cls])
        legend_elements.append(
            Line2D([0], [0], marker='o', color='w', markerfacecolor=HOTSPOT_COLORS[cls],
                   markeredgecolor='#222222' if cls != 'Not Significant' else 'none',
                   markersize=8 * markerscale,
                   label=f'{cls}')
        )

    legend = ax.legend(
        handles=legend_elements, title='Getis-Ord Gi* Classification (Points)',
        title_fontsize=legend_fontsize + 0.5, fontsize=legend_fontsize - 0.5,
        loc='upper left', bbox_to_anchor=(1.02, 1), frameon=True, framealpha=0.95,
        edgecolor='#CCCCCC', facecolor='white', handlelength=1.5
    )
    legend.get_title().set_fontweight('bold')

    # ── North Arrow & Scale ───────────────────────────────────────────────────
    add_north_arrow(ax)
    add_scale_bar(ax, gdf_brgy, length_km=1)

    # ── Axes ─────────────────────────────────────────────────────────────────
    ax.set_xlabel('Easting (m) — WGS 84 / UTM Zone 51N', fontsize=7, color='#444444')
    ax.set_ylabel('Northing (m) — WGS 84 / UTM Zone 51N', fontsize=7, color='#444444')
    ax.ticklabel_format(style='plain')

    # ── Title ────────────────────────────────────────────────────────────────
    ax.set_title(
        'Native Tree Hotspot Point Map (Getis-Ord Gi*)\nMandaue City, Cebu, Philippines',
        fontsize=title_size, fontweight='bold', color='#111111', pad=12, loc='left'
    )
    n_native = len(gdf_native)
    # Subtitle removed per request

    # ── Footer ───────────────────────────────────────────────────────────────
    # Footer removed per request

    plt.tight_layout(rect=[0, 0.02, 1, 1])
    return fig, ax


print("\n[6/6] Building and saving maps...")

fig_std, _ = build_hotspot_map(figsize=(14, 12), label_size=6.0, variant='standard')
save_map(fig_std, OUT_DIR, 'analysis3_native_tree_hotspot')
plt.close(fig_std)

print("\nPoster (A1) Version...")
fig_poster, _ = build_hotspot_map(
    figsize=(23.4, 20.0), label_size=9.0, title_size=22,
    legend_fontsize=12, footer_size=9, markerscale=1.8, variant='poster'
)
save_map(fig_poster, os.path.join(BASE_DIR, 'outputs', 'maps', 'poster'), 'A1_analysis3_native_tree_hotspot')
plt.close(fig_poster)

print("\nLGU Version...")
fig_lgu, ax_lgu = build_hotspot_map(
    figsize=(16, 14), label_size=8.5, title_size=17,
    legend_fontsize=10, footer_size=8, markerscale=1.4, variant='lgu'
)
ax_lgu.text(0.01, 0.01, 'For Official LGU Use — Environmental Management Plan Attachment',
    transform=ax_lgu.transAxes, fontsize=8, color='#880000', fontweight='bold', style='italic',
    bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFF9E6', edgecolor='#CC8800', linewidth=0.8))
save_map(fig_lgu, os.path.join(BASE_DIR, 'outputs', 'maps', 'lgu'), 'LGU_analysis3_native_tree_hotspot')
plt.close(fig_lgu)

print("\n--- Analysis 3 Complete ---")
print(f"Outputs saved to: {OUT_DIR}")
