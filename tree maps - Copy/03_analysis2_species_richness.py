"""
==============================================================================
03_analysis2_species_richness.py
ANALYSIS 2 — SPECIES RICHNESS POINT MAP (Publication Quality)
==============================================================================
Purpose:
    Display tree points colored by the species richness of their host barangay.

Methodology:
    Species Richness = count of distinct 'Species name' values per barangay
    (calculated using all records).
    The richness class is then joined to individual valid tree points.

Classification: Natural Breaks (Jenks) or Quantiles into 5 classes:
    Very Low / Low / Moderate / High / Very High

CRS     : EPSG:32651 (WGS84/UTM Zone 51N)
Output  : PNG 600 dpi, TIFF 600 dpi, SVG, PDF (vector)
Software: Python 3.x, GeoPandas, Matplotlib, mapclassify
==============================================================================
"""

import os
import pandas as pd
import geopandas as gpd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import matplotlib.colors as mcolors
import matplotlib.patheffects as pe
import mapclassify
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────────────────────────────────────
BASE_DIR  = r'c:\Users\LENOVO\Documents\tree maps - Copy'
CSV_ALL   = os.path.join(BASE_DIR, 'outputs', 'data', 'tree_all_records.csv')
GPKG      = os.path.join(BASE_DIR, 'outputs', 'data', 'tree_inventory_cleaned.gpkg')
OUT_DIR   = os.path.join(BASE_DIR, 'outputs', 'maps', 'analysis2_richness')
os.makedirs(OUT_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1: LOAD DATA
# ─────────────────────────────────────────────────────────────────────────────
print("[1/5] Loading data...")
df_all   = pd.read_csv(CSV_ALL)
gdf_pts  = gpd.read_file(GPKG, layer='tree_points')
gdf_brgy = gpd.read_file(GPKG, layer='barangay_boundaries')

print(f"  All records: {len(df_all):,}")
print(f"  Valid Tree Points: {len(gdf_pts):,}")
print(f"  Barangays: {len(gdf_brgy)}")

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2: CALCULATE SPECIES RICHNESS PER BARANGAY
# ─────────────────────────────────────────────────────────────────────────────
print("\n[2/5] Calculating species richness per barangay...")

# Normalize species names (strip whitespace, title case)
df_all['Species name'] = df_all['Species name'].str.strip().str.title()

# Calculate richness: unique species per barangay (all records, not just valid GPS)
richness = (
    df_all.groupby('Barangay')['Species name']
    .nunique()
    .reset_index()
    .rename(columns={'Species name': 'species_richness', 'Barangay': 'ADM4_EN'})
)

# ─────────────────────────────────────────────────────────────────────────────
# STEP 3: CLASSIFY INTO 5 CATEGORIES
# ─────────────────────────────────────────────────────────────────────────────
print("\n[3/5] Classifying species richness into 5 categories...")

# Classify barangays first
values = richness['species_richness'].values
classifier = mapclassify.NaturalBreaks(values, k=5)
bins = classifier.bins
richness['richness_class'] = classifier.yb  # 0–4 class indices

CLASS_LABELS = {
    0: 'Very Low',
    1: 'Low',
    2: 'Moderate',
    3: 'High',
    4: 'Very High',
}

# Bin ranges for legend
bin_ranges = []
prev = values.min()
for b in bins:
    bin_ranges.append(f'{int(prev)}–{int(b)} species')
    prev = b + 1

# Join richness class to points
# gdf_pts has 'Barangay' which should map to 'ADM4_EN'
gdf_pts = gdf_pts.merge(richness[['ADM4_EN', 'species_richness', 'richness_class']], 
                        left_on='Barangay', right_on='ADM4_EN', how='left')

# Drop points with no richness class (shouldn't happen)
gdf_pts = gdf_pts.dropna(subset=['richness_class'])
gdf_pts['richness_class'] = gdf_pts['richness_class'].astype(int)

# ─────────────────────────────────────────────────────────────────────────────
# COLOR PALETTE — Sequential Green for Points
# ─────────────────────────────────────────────────────────────────────────────
GREEN_PALETTE = {
    0: '#A1D99B',   # Very Low  — light green
    1: '#74C476',   # Low       
    2: '#41AB5D',   # Moderate  
    3: '#238B45',   # High      
    4: '#005A32',   # Very High — dark forest green
}

gdf_pts['color'] = gdf_pts['richness_class'].map(GREEN_PALETTE)

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
    arrow_ax.fill([0, -0.45, 0, 0.45], [-1.0, -0.8, -0.4, -0.8], color='#FFFFFF',
                  ec='#222222', lw=0.8, zorder=3)
    arrow_ax.text(0, 1.05, 'N', ha='center', va='bottom', fontsize=8,
                  fontweight='bold', color='#222222')

def add_scale_bar(ax, gdf_brgy, length_km=1, pad_frac=0.04):
    xmin_b, ymin_b, xmax_b, ymax_b = gdf_brgy.total_bounds
    bar_x  = xmin_b + (xmax_b - xmin_b) * pad_frac
    bar_y  = ymin_b + (ymax_b - ymin_b) * pad_frac
    length = length_km * 1000
    segs   = 4; seg_len = length / segs; bar_h  = length * 0.025
    for i in range(segs):
        color = '#222222' if i % 2 == 0 else '#FFFFFF'
        ax.fill_between([bar_x + i * seg_len, bar_x + (i + 1) * seg_len],
                        [bar_y - bar_h, bar_y - bar_h], [bar_y, bar_y],
                        color=color, ec='#222222', lw=0.6, zorder=7)
    ax.text(bar_x,            bar_y - bar_h * 1.5, '0', ha='center', va='top', fontsize=6.5, color='#333333', zorder=8)
    ax.text(bar_x + length/2, bar_y - bar_h * 1.5, f'{length_km // 2} km', ha='center', va='top', fontsize=6.5, color='#333333', zorder=8)
    ax.text(bar_x + length,   bar_y - bar_h * 1.5, f'{length_km} km', ha='center', va='top', fontsize=6.5, color='#333333', zorder=8)

def label_barangays(ax, gdf_brgy, fontsize=6.0):
    offsets = {'Centro (Pob.)': (200, -300), 'Looc': (100, -200), 'Maguikay': (-200, 200), 'Cambaro': (0, 200), 'Bakilid': (0, -200)}
    for _, row in gdf_brgy.iterrows():
        cx, cy = row.geometry.centroid.x, row.geometry.centroid.y
        name = row['ADM4_EN']
        dx, dy = offsets.get(name, (0, 0))
        txt = ax.text(cx + dx, cy + dy, name, ha='center', va='center',
                      fontsize=fontsize, color='#111111', fontweight='semibold', zorder=10)
        txt.set_path_effects([pe.withStroke(linewidth=2.2, foreground='white')])

def save_map(fig, out_dir, name):
    for fmt, dpi in [('png', 600), ('tif', 600), ('svg', None), ('pdf', None)]:
        fpath = os.path.join(out_dir, f'{name}.{fmt}')
        if dpi:
            fig.savefig(fpath, dpi=dpi, bbox_inches='tight', facecolor='white', edgecolor='none')
        else:
            fig.savefig(fpath, bbox_inches='tight', facecolor='white', edgecolor='none')
        print(f"  Saved: {fpath}")

# ─────────────────────────────────────────────────────────────────────────────
# FIGURE FACTORY
# ─────────────────────────────────────────────────────────────────────────────
def build_richness_map(figsize=(14, 12), label_size=6.0, title_size=14,
                        legend_fontsize=9, footer_size=6.5, markerscale=1.0,
                        variant='standard'):

    xmin, ymin, xmax, ymax = gdf_brgy.total_bounds
    pad_x = (xmax - xmin) * 0.04
    pad_y = (ymax - ymin) * 0.04

    fig, ax = plt.subplots(figsize=figsize, facecolor='white')
    ax.set_facecolor('white')

    # ── Barangay layer (Hollow) ──────────────────────────────────────────────
    gdf_brgy.plot(ax=ax, facecolor='#F9F9F9', edgecolor='#666666', linewidth=0.8, zorder=1)

    # ── Tree points by richness class ────────────────────────────────────────
    # Plot from lowest to highest class so higher richness points are on top
    for cls in range(5):
        sub = gdf_pts[gdf_pts['richness_class'] == cls]
        if len(sub) == 0: continue
        sub.plot(
            ax=ax, color=GREEN_PALETTE[cls],
            markersize=12 * markerscale, marker='o', alpha=0.8,
            zorder=2 + cls  # higher class = higher zorder
        )

    # ── Grid ─────────────────────────────────────────────────────────────────
    ax.grid(True, linestyle='--', linewidth=0.35, color='#AAAAAA', alpha=0.55, zorder=0)
    ax.tick_params(axis='both', labelsize=6.5, color='#555555', labelcolor='#555555')
    ax.set_xlim(xmin - pad_x, xmax + pad_x)
    ax.set_ylim(ymin - pad_y, ymax + pad_y)

    # ── Labels ───────────────────────────────────────────────────────────────
    label_barangays(ax, gdf_brgy, fontsize=label_size)

    # ── Legend ───────────────────────────────────────────────────────────────
    legend_elements = []
    for cls in range(4, -1, -1):
        lbl  = CLASS_LABELS[cls]
        rang = bin_ranges[cls]
        n_pts = len(gdf_pts[gdf_pts['richness_class'] == cls])
        legend_elements.append(
            Line2D([0], [0], marker='o', color='w', markerfacecolor=GREEN_PALETTE[cls],
                   markersize=8 * markerscale,
                   label=f'{lbl} [{rang}] (n={n_pts:,} pts)')
        )

    legend = ax.legend(
        handles=legend_elements, title='Host Barangay Species Richness',
        title_fontsize=legend_fontsize + 0.5, fontsize=legend_fontsize,
        loc='upper left', bbox_to_anchor=(1.02, 1), frameon=True, framealpha=0.95,
        edgecolor='#CCCCCC', facecolor='white'
    )
    legend.get_title().set_fontweight('bold')

    # ── North Arrow & Scale ───────────────────────────────────────────────────
    add_north_arrow(ax)
    add_scale_bar(ax, gdf_brgy, length_km=1)

    # ── Axes labels ──────────────────────────────────────────────────────────
    ax.set_xlabel('Easting (m) — WGS 84 / UTM Zone 51N', fontsize=7, color='#444444')
    ax.set_ylabel('Northing (m) — WGS 84 / UTM Zone 51N', fontsize=7, color='#444444')

    # ── Title ────────────────────────────────────────────────────────────────
    ax.set_title(
        'Tree Points by Barangay Species Richness\nMandaue City, Cebu, Philippines',
        fontsize=title_size, fontweight='bold', color='#111111', pad=12, loc='left'
    )
    ax.text(0.0, 1.01,
            f'Total unique species: {df_all["Species name"].nunique()}  |  '
            f'Valid mapped trees: {len(gdf_pts):,}  |  '
            f'Classification: Natural Breaks (Jenks), k=5  |  EPSG:32651',
            transform=ax.transAxes, fontsize=7, color='#555555', va='bottom')

    # ── Footer ───────────────────────────────────────────────────────────────
    footer = (
        'Projection: WGS 84 / UTM Zone 51N (EPSG:32651)  |  '
        'Data Sources: Tree Inventory Survey 2024; Barangay Boundaries — LGU Mandaue City  |  '
        'Analysis: Python 3 / GeoPandas / mapclassify  |  '
        'Figure 2. Point-Based Species Richness Map'
    )
    fig.text(0.01, 0.005, footer, fontsize=footer_size - 0.5, color='#666666', style='italic')

    plt.tight_layout(rect=[0, 0.02, 1, 1])
    return fig, ax

# ─────────────────────────────────────────────────────────────────────────────
# STEP 4: BUILD & SAVE MAPS
# ─────────────────────────────────────────────────────────────────────────────
print("\n[4/5] Generating Standard Publication Map...")
fig_std, _ = build_richness_map(figsize=(14, 12), label_size=6.0, variant='standard')
save_map(fig_std, OUT_DIR, 'analysis2_species_richness_map')
plt.close(fig_std)

print("\nGenerating Poster (A1) Version...")
fig_poster, _ = build_richness_map(
    figsize=(23.4, 20.0), label_size=9.0, title_size=22,
    legend_fontsize=13, footer_size=9, markerscale=1.8, variant='poster'
)
poster_dir = os.path.join(BASE_DIR, 'outputs', 'maps', 'poster')
save_map(fig_poster, poster_dir, 'A1_analysis2_species_richness_map')
plt.close(fig_poster)

print("\nGenerating LGU Version...")
fig_lgu, ax_lgu = build_richness_map(
    figsize=(16, 14), label_size=8.5, title_size=17,
    legend_fontsize=11, footer_size=8, markerscale=1.4, variant='lgu'
)
ax_lgu.text(0.01, 0.01,
    'For Official LGU Use — Environmental Management Plan Attachment',
    transform=ax_lgu.transAxes, fontsize=8, color='#880000', fontweight='bold', style='italic',
    bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFF9E6', edgecolor='#CC8800', linewidth=0.8))
lgu_dir = os.path.join(BASE_DIR, 'outputs', 'maps', 'lgu')
save_map(fig_lgu, lgu_dir, 'LGU_analysis2_species_richness_map')
plt.close(fig_lgu)

print("\n--- Analysis 2 Complete ---")
print(f"Outputs saved to: {OUT_DIR}")
