"""
==============================================================================
05_analysis4_conservation_priority.py
ANALYSIS 4 — TREE CONSERVATION PRIORITY POINT MAP
==============================================================================
Purpose:
    Plot individual tree points colored by their host barangay's Conservation Priority Score.

Methodology:
    The composite score integrates three dimensions per barangay:
    1. DISTRIBUTION STATUS SCORE (50%)
    2. SPECIES RICHNESS SCORE (30%)
    3. LARGE TREE SCORE (20%)
    Priority class (0-4) is joined to individual points for visualization.

CRS     : EPSG:32651 (WGS84/UTM Zone 51N)
Output  : PNG 600 dpi, TIFF 600 dpi, SVG, PDF (vector)
Software: Python 3.x, GeoPandas, Matplotlib, mapclassify
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
import mapclassify
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────────────────────────────────────
BASE_DIR = r'c:\Users\LENOVO\Documents\tree maps - Copy'
CSV_ALL  = os.path.join(BASE_DIR, 'outputs', 'data', 'tree_all_records.csv')
GPKG     = os.path.join(BASE_DIR, 'outputs', 'data', 'tree_inventory_cleaned.gpkg')
OUT_DIR  = os.path.join(BASE_DIR, 'outputs', 'maps', 'analysis4_priority')
os.makedirs(OUT_DIR, exist_ok=True)

STATUS_WEIGHTS = {'Endemic': 5, 'Indigenous': 3, 'Introduced': 1, 'Unknown': 0}

# ─────────────────────────────────────────────────────────────────────────────
# STEP 1: LOAD DATA & COMPUTE SCORES
# ─────────────────────────────────────────────────────────────────────────────
print("[1/3] Loading data & computing priority scores...")
df_all   = pd.read_csv(CSV_ALL)
gdf_pts  = gpd.read_file(GPKG, layer='tree_points')
gdf_brgy = gpd.read_file(GPKG, layer='barangay_boundaries')

df_all['Species name'] = df_all['Species name'].str.strip().str.title()
df_all['status_weight'] = df_all['Distribution Status'].map(STATUS_WEIGHTS).fillna(0)

# Status Score
status_score = df_all.groupby('Barangay')['status_weight'].sum().reset_index()
status_score.columns = ['ADM4_EN', 'status_score_raw']

# Richness Score
richness_score = df_all.groupby('Barangay')['Species name'].nunique().reset_index()
richness_score.columns = ['ADM4_EN', 'richness_raw']

# Large Tree Score
df_valid_dbh = df_all[df_all['dbh_flag'] == 'valid'].copy()
large_trees = df_valid_dbh[df_valid_dbh['DBH_clean'] > 50].groupby('Barangay').size().reset_index()
large_trees.columns = ['ADM4_EN', 'large_tree_count']

# Merge to a df
df_score = pd.DataFrame({'ADM4_EN': gdf_brgy['ADM4_EN']})
df_score = df_score.merge(status_score,  on='ADM4_EN', how='left')
df_score = df_score.merge(richness_score, on='ADM4_EN', how='left')
df_score = df_score.merge(large_trees,    on='ADM4_EN', how='left')

df_score['status_score_raw'] = df_score['status_score_raw'].fillna(0)
df_score['richness_raw']     = df_score['richness_raw'].fillna(0).astype(int)
df_score['large_tree_count'] = df_score['large_tree_count'].fillna(0).astype(int)

def normalize(series, new_min=0, new_max=10):
    s_min, s_max = series.min(), series.max()
    if s_max == s_min: return series * 0 + 5
    return (series - s_min) / (s_max - s_min) * (new_max - new_min) + new_min

df_score['status_norm']      = normalize(df_score['status_score_raw'])
df_score['richness_norm']    = normalize(df_score['richness_raw'])
df_score['large_tree_norm']  = normalize(df_score['large_tree_count'])

df_score['priority_score'] = (0.50 * df_score['status_norm'] + 
                              0.30 * df_score['richness_norm'] + 
                              0.20 * df_score['large_tree_norm'])

scores = df_score['priority_score'].values
classifier = mapclassify.NaturalBreaks(scores, k=5)
bins = classifier.bins
df_score['priority_class'] = classifier.yb

PRIORITY_LABELS = {0: 'Very Low Priority', 1: 'Low Priority', 2: 'Moderate Priority', 3: 'High Priority', 4: 'Very High Priority'}

bin_ranges = []
prev = scores.min()
for b in bins:
    bin_ranges.append(f'{prev:.2f}–{b:.2f}')
    prev = b

# ─────────────────────────────────────────────────────────────────────────────
# STEP 2: JOIN TO POINTS
# ─────────────────────────────────────────────────────────────────────────────
print("\n[2/3] Joining classes to tree points...")

# Join to tree points
gdf_pts = gdf_pts.merge(df_score[['ADM4_EN', 'priority_class', 'priority_score']], 
                        left_on='Barangay', right_on='ADM4_EN', how='left')
gdf_pts = gdf_pts.dropna(subset=['priority_class'])
gdf_pts['priority_class'] = gdf_pts['priority_class'].astype(int)

PRIORITY_COLORS = {
    0: '#D9F0D3',   # Very Low
    1: '#90C987',   # Low
    2: '#FFDD77',   # Moderate
    3: '#E07B00',   # High
    4: '#8B0000',   # Very High
}

gdf_pts['color'] = gdf_pts['priority_class'].map(PRIORITY_COLORS)

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
# STEP 3: BUILD MAP
# ─────────────────────────────────────────────────────────────────────────────
def build_priority_map(figsize=(14, 12), label_size=6.0, title_size=14,
                        legend_fontsize=9, footer_size=6.5, markerscale=1.0, variant='standard'):

    xmin, ymin, xmax, ymax = gdf_brgy.total_bounds
    pad_x = (xmax - xmin) * 0.04
    pad_y = (ymax - ymin) * 0.04

    fig, ax = plt.subplots(figsize=figsize, facecolor='white')
    ax.set_facecolor('white')

    # ── Barangay boundaries ──────────────────────────────────────────────────
    gdf_brgy.plot(ax=ax, facecolor='#F9F9F9', edgecolor='#666666', linewidth=0.8, zorder=1)

    # ── Plot points by priority class ────────────────────────────────────────
    for cls in range(5):
        sub = gdf_pts[gdf_pts['priority_class'] == cls]
        if len(sub) == 0: continue
        
        # Larger points for higher priority
        size = 8 + (cls * 2)
        edge = '#222222' if cls >= 3 else 'none'
        lw = 0.5 if cls >= 3 else 0
        
        sub.plot(ax=ax, color=PRIORITY_COLORS[cls], edgecolor=edge, linewidth=lw,
                 markersize=size * markerscale, marker='o', alpha=0.85, zorder=2 + cls)

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
        lbl  = PRIORITY_LABELS[cls]
        rang = bin_ranges[cls]
        n_pts = len(gdf_pts[gdf_pts['priority_class'] == cls])
        edge = '#222222' if cls >= 3 else 'none'
        legend_elements.append(
            Line2D([0], [0], marker='o', color='w', markerfacecolor=PRIORITY_COLORS[cls],
                   markeredgecolor=edge, markersize=8 * markerscale,
                   label=f'{lbl} [score: {rang}] (n={n_pts:,} pts)')
        )

    score_components = [
        mpatches.Patch(facecolor='none', edgecolor='none', label=''),
        mpatches.Patch(facecolor='none', edgecolor='none', label='Score Components (weights):'),
        mpatches.Patch(facecolor='none', edgecolor='none', label='  Status (50%): Endemic=5, Indig=3, Intro=1, Unk=0'),
        mpatches.Patch(facecolor='none', edgecolor='none', label='  Richness (30%): unique spp per barangay'),
        mpatches.Patch(facecolor='none', edgecolor='none', label='  Large Tree (20%): DBH > 50 cm count'),
    ]

    legend = ax.legend(
        handles=legend_elements + score_components, title='Conservation Priority Class (Points)',
        title_fontsize=legend_fontsize + 0.5, fontsize=legend_fontsize - 0.5,
        loc='upper left', bbox_to_anchor=(1.02, 1), frameon=True, framealpha=0.95, edgecolor='#CCCCCC', facecolor='white'
    )
    legend.get_title().set_fontweight('bold')

    # ── North Arrow & Scale ───────────────────────────────────────────────────
    add_north_arrow(ax)
    add_scale_bar(ax, gdf_brgy, length_km=1)

    # ── Axes ─────────────────────────────────────────────────────────────────
    ax.set_xlabel('Easting (m) — WGS 84 / UTM Zone 51N', fontsize=7, color='#444444')
    ax.set_ylabel('Northing (m) — WGS 84 / UTM Zone 51N', fontsize=7, color='#444444')

    # ── Title ────────────────────────────────────────────────────────────────
    ax.set_title(
        'Tree Points by Conservation Priority\nMandaue City, Cebu, Philippines',
        fontsize=title_size, fontweight='bold', color='#111111', pad=12, loc='left'
    )
    ax.text(0.0, 1.01,
            f'Valid mapped trees: {len(gdf_pts):,}  |  '
            f'Composite score: 50% Status + 30% Richness + 20% Large Tree  |  EPSG:32651',
            transform=ax.transAxes, fontsize=7, color='#555555', va='bottom')

    # ── Footer ───────────────────────────────────────────────────────────────
    footer = (
        'Projection: WGS 84 / UTM Zone 51N (EPSG:32651)  |  '
        'Data Sources: Tree Inventory Survey 2024; Barangay Boundaries — LGU Mandaue City  |  '
        'Analysis: Python 3 / GeoPandas / mapclassify  |  '
        'Figure 4. Point-Based Conservation Priority Map'
    )
    fig.text(0.01, 0.005, footer, fontsize=footer_size - 0.5, color='#666666', style='italic')

    plt.tight_layout(rect=[0, 0.02, 1, 1])
    return fig, ax


print("\n[3/3] Generating maps...")
fig_std, _ = build_priority_map(figsize=(14, 12), label_size=6.0, variant='standard')
save_map(fig_std, OUT_DIR, 'analysis4_conservation_priority_map')
plt.close(fig_std)

print("\nPoster (A1) Version...")
fig_poster, _ = build_priority_map(
    figsize=(23.4, 20.0), label_size=9.0, title_size=22,
    legend_fontsize=12, footer_size=9, markerscale=1.8, variant='poster'
)
save_map(fig_poster, os.path.join(BASE_DIR, 'outputs', 'maps', 'poster'), 'A1_analysis4_conservation_priority_map')
plt.close(fig_poster)

print("\nLGU Version...")
fig_lgu, ax_lgu = build_priority_map(
    figsize=(16, 14), label_size=8.5, title_size=17,
    legend_fontsize=10, footer_size=8, markerscale=1.4, variant='lgu'
)
ax_lgu.text(0.01, 0.01, 'For Official LGU Use — Environmental Management Plan Attachment',
    transform=ax_lgu.transAxes, fontsize=8, color='#880000', fontweight='bold', style='italic',
    bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFF9E6', edgecolor='#CC8800', linewidth=0.8))
save_map(fig_lgu, os.path.join(BASE_DIR, 'outputs', 'maps', 'lgu'), 'LGU_analysis4_conservation_priority_map')
plt.close(fig_lgu)

print("\n--- Analysis 4 Complete ---")
print(f"Outputs saved to: {OUT_DIR}")
