"""
==============================================================================
02_analysis1_distribution_map.py
ANALYSIS 1 — TREE DISTRIBUTION MAP (Publication Quality)
==============================================================================
Purpose:
    Display all inventoried trees classified by Distribution Status
    (Endemic, Indigenous, Introduced, Unknown) overlaid on barangay boundaries.

Classification:
    Endemic     — globally/nationally restricted range
    Indigenous  — native to the region, not globally restricted
    Introduced  — non-native / exotic
    Unknown     — undetermined status

Color palette: Colorblind-friendly (verified against CVD simulations)
    Endemic     #8B0000  (Dark Red)
    Indigenous  #1A5C1A  (Dark Green)
    Introduced  #E07B00  (Orange)
    Unknown     #808080  (Gray)

CRS     : EPSG:32651 (WGS84/UTM Zone 51N)
Output  : PNG 600 dpi, TIFF 600 dpi, SVG, PDF (vector)
Software: Python 3.x, GeoPandas, Matplotlib
==============================================================================
"""

import os
import geopandas as gpd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as ticker
from matplotlib.lines import Line2D
import matplotlib.patheffects as pe
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# ─────────────────────────────────────────────────────────────────────────────
# PATHS & SETTINGS
# ─────────────────────────────────────────────────────────────────────────────
BASE_DIR  = r'c:\Users\LENOVO\Documents\tree maps - Copy'
GPKG      = os.path.join(BASE_DIR, 'outputs', 'data', 'tree_inventory_cleaned.gpkg')
OUT_DIR   = os.path.join(BASE_DIR, 'outputs', 'maps', 'analysis1_distribution')
os.makedirs(OUT_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# COLOR PALETTE (colorblind-friendly, publication-quality)
# ─────────────────────────────────────────────────────────────────────────────
STATUS_COLORS = {
    'Endemic'   : '#8B0000',   # Dark Red
    'Indigenous': '#1A5C1A',   # Dark Green
    'Introduced': '#E07B00',   # Orange
    'Unknown'   : '#808080',   # Gray
}
STATUS_ORDER = ['Endemic', 'Indigenous', 'Introduced', 'Unknown']
STATUS_SIZES = {
    'Endemic'   : 18,
    'Indigenous': 12,
    'Introduced': 10,
    'Unknown'   : 8,
}
STATUS_MARKERS = {
    'Endemic'   : 'D',   # diamond — highest conservation value
    'Indigenous': 'o',   # circle
    'Introduced': '^',   # triangle
    'Unknown'   : 's',   # square
}
STATUS_ZORDER = {
    'Endemic'   : 6,
    'Indigenous': 5,
    'Introduced': 4,
    'Unknown'   : 3,
}

# ─────────────────────────────────────────────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────────────────────────────────────────────
print("[1/4] Loading data...")
gdf_pts  = gpd.read_file(GPKG, layer='tree_points')
gdf_brgy = gpd.read_file(GPKG, layer='barangay_boundaries')

print(f"  Tree points: {len(gdf_pts):,}")
print(f"  Barangays  : {len(gdf_brgy)}")
print(f"  CRS: {gdf_pts.crs}")

# Get study area bounds with padding
xmin, ymin, xmax, ymax = gdf_brgy.total_bounds
pad_x = (xmax - xmin) * 0.04
pad_y = (ymax - ymin) * 0.04
XLIM = (xmin - pad_x, xmax + pad_x)
YLIM = (ymin - pad_y, ymax + pad_y)

# ─────────────────────────────────────────────────────────────────────────────
# UTILITY FUNCTIONS
# ─────────────────────────────────────────────────────────────────────────────
def add_north_arrow(ax, x=0.96, y=0.15, size=0.055):
    """Add a professional north arrow."""
    ax_x = ax.get_position().x0 + ax.get_position().width  * x
    ax_y = ax.get_position().y0 + ax.get_position().height * y
    fig  = ax.get_figure()
    arrow_ax = fig.add_axes([ax_x - 0.028, ax_y - 0.025, size, size * 1.4], anchor='C')
    arrow_ax.set_xlim(-1, 1)
    arrow_ax.set_ylim(-1.2, 1.2)
    arrow_ax.axis('off')
    # North triangle (dark)
    arrow_ax.fill([0, -0.45, 0, 0.45], [1.0, -0.8, -0.4, -0.8], color='#222222', zorder=3)
    # South triangle (light)
    arrow_ax.fill([0, -0.45, 0, 0.45], [-1.0, -0.8, -0.4, -0.8], color='#FFFFFF',
                  ec='#222222', lw=0.8, zorder=3)
    arrow_ax.text(0, 1.05, 'N', ha='center', va='bottom', fontsize=8,
                  fontweight='bold', color='#222222')


def add_scale_bar(ax, gdf_brgy, length_km=1, pad_frac=0.04):
    """Add a metric scale bar."""
    xmin_b, ymin_b, xmax_b, ymax_b = gdf_brgy.total_bounds
    bar_x  = xmin_b + (xmax_b - xmin_b) * pad_frac
    bar_y  = ymin_b + (ymax_b - ymin_b) * pad_frac
    length = length_km * 1000  # metres (UTM)

    # Draw scale bar segments (alternating black/white)
    segs = 4
    seg_len = length / segs
    for i in range(segs):
        color = '#222222' if i % 2 == 0 else '#FFFFFF'
        ax.fill_between(
            [bar_x + i * seg_len, bar_x + (i + 1) * seg_len],
            [bar_y - length * 0.025, bar_y - length * 0.025],
            [bar_y, bar_y],
            color=color, ec='#222222', lw=0.6, zorder=7, transform=ax.transData
        )
    bar_h = length * 0.025
    # Labels
    ax.text(bar_x, bar_y - bar_h * 1.5, '0', ha='center', va='top',
            fontsize=6.5, color='#333333', zorder=8)
    ax.text(bar_x + length / 2, bar_y - bar_h * 1.5, f'{length_km // 2} km',
            ha='center', va='top', fontsize=6.5, color='#333333', zorder=8)
    ax.text(bar_x + length, bar_y - bar_h * 1.5, f'{length_km} km',
            ha='center', va='top', fontsize=6.5, color='#333333', zorder=8)


def add_grid(ax):
    """Add a subtle coordinate grid."""
    ax.grid(True, linestyle='--', linewidth=0.35, color='#AAAAAA', alpha=0.55, zorder=0)
    ax.tick_params(axis='both', labelsize=6.5, color='#555555', labelcolor='#555555')


def label_barangays(ax, gdf_brgy, fontsize=6.0):
    """Label barangays with smart centroid placement and white halo."""
    # Manual offsets for crowded barangays (in metres)
    offsets = {
        'Centro (Pob.)': (200, -300),
        'Looc'         : (100, -200),
        'Maguikay'     : (-200, 200),
        'Cambaro'      : (0, 200),
        'Bakilid'      : (0, -200),
    }
    for _, row in gdf_brgy.iterrows():
        cx  = row.geometry.centroid.x
        cy  = row.geometry.centroid.y
        name = row['ADM4_EN']
        dx, dy = offsets.get(name, (0, 0))
        txt = ax.text(
            cx + dx, cy + dy, name,
            ha='center', va='center',
            fontsize=fontsize,
            color='#111111',
            fontweight='semibold',
            zorder=10,
        )
        txt.set_path_effects([
            pe.withStroke(linewidth=2.2, foreground='white'),
        ])


def save_map(fig, out_dir, name):
    """Save map in all required formats."""
    for fmt, dpi in [('png', 600), ('tif', 600), ('svg', None), ('pdf', None)]:
        fpath = os.path.join(out_dir, f'{name}.{fmt}')
        if dpi:
            fig.savefig(fpath, dpi=dpi, bbox_inches='tight',
                        facecolor='white', edgecolor='none')
        else:
            fig.savefig(fpath, bbox_inches='tight',
                        facecolor='white', edgecolor='none')
        print(f"  Saved: {fpath}")


# ─────────────────────────────────────────────────────────────────────────────
# FIGURE FACTORY — builds map for both standard and poster/LGU variants
# ─────────────────────────────────────────────────────────────────────────────
def build_distribution_map(figsize=(14, 12), label_size=6.0,
                            title_size=14, subtitle_size=9,
                            legend_fontsize=9, markerscale=1.0,
                            footer_size=6.5, variant='standard'):
    print(f"\n[2/4] Building {variant} distribution map...")

    fig, ax = plt.subplots(figsize=figsize, facecolor='white')
    ax.set_facecolor('white')

    # ── Barangay layer ──────────────────────────────────────────────────────
    gdf_brgy.plot(
        ax=ax,
        facecolor='#F5F5F0',
        edgecolor='#555555',
        linewidth=0.8,
        zorder=1,
    )

    # ── Tree points by status ───────────────────────────────────────────────
    status_counts = gdf_pts['Distribution Status'].value_counts()
    for status in STATUS_ORDER:
        sub = gdf_pts[gdf_pts['Distribution Status'] == status]
        if len(sub) == 0:
            continue
        sub.plot(
            ax=ax,
            color=STATUS_COLORS[status],
            markersize=STATUS_SIZES[status] * markerscale,
            marker=STATUS_MARKERS[status],
            alpha=0.75,
            zorder=STATUS_ZORDER[status],
            label=f'{status}',
        )

    # ── Cartographic elements ────────────────────────────────────────────────
    ax.set_xlim(XLIM)
    ax.set_ylim(YLIM)
    add_grid(ax)
    label_barangays(ax, gdf_brgy, fontsize=label_size)

    # ── Legend ───────────────────────────────────────────────────────────────
    legend_elements = [
        Line2D([0], [0], marker=STATUS_MARKERS[s], color='w',
               markerfacecolor=STATUS_COLORS[s],
               markersize=7 * markerscale,
               label=f'{s}')
        for s in STATUS_ORDER
    ]
    legend = ax.legend(
        handles=legend_elements,
        title='Distribution Status',
        title_fontsize=legend_fontsize + 0.5,
        fontsize=legend_fontsize,
        loc='upper left',
        bbox_to_anchor=(1.02, 1),
        frameon=True,
        framealpha=0.95,
        edgecolor='#CCCCCC',
        facecolor='white',
    )
    legend.get_title().set_fontweight('bold')

    # ── North Arrow & Scale Bar ──────────────────────────────────────────────
    add_north_arrow(ax)
    add_scale_bar(ax, gdf_brgy, length_km=1)

    # ── Axes labels ──────────────────────────────────────────────────────────
    ax.set_xlabel('Easting (m) — WGS 84 / UTM Zone 51N', fontsize=7, color='#444444')
    ax.set_ylabel('Northing (m) — WGS 84 / UTM Zone 51N', fontsize=7, color='#444444')
    ax.ticklabel_format(style='plain')

    # ── Title block ──────────────────────────────────────────────────────────
    total_pts = len(gdf_pts)
    ax.set_title(
        'Tree Distribution Map by Conservation Status\nMandaue City, Cebu, Philippines',
        fontsize=title_size,
        fontweight='bold',
        color='#111111',
        pad=12,
        loc='left',
    )

    # ── Subtitle / total count ───────────────────────────────────────────────
    # Subtitle removed per request

    # ── Footer ───────────────────────────────────────────────────────────────
    # Footer removed per request

    plt.tight_layout(rect=[0, 0.02, 1, 1])
    return fig, ax


# ─────────────────────────────────────────────────────────────────────────────
# BUILD & SAVE — STANDARD VERSION
# ─────────────────────────────────────────────────────────────────────────────
print("[3/4] Generating Standard Publication Map...")
fig_std, _ = build_distribution_map(figsize=(14, 12), label_size=6.0,
                                     variant='standard')
save_map(fig_std, OUT_DIR, 'analysis1_distribution_map')
plt.close(fig_std)

# ─────────────────────────────────────────────────────────────────────────────
# BUILD & SAVE — POSTER VERSION (A1 @ 150 dpi ~ 3508×4961 px)
# ─────────────────────────────────────────────────────────────────────────────
print("\n[4/4] Generating Poster (A1) Version...")
# A1 = 594mm × 841mm; at 150dpi ≈ 23.4 × 33.1 inches
fig_poster, _ = build_distribution_map(
    figsize=(23.4, 20.0),
    label_size=9.0,
    title_size=22,
    subtitle_size=14,
    legend_fontsize=13,
    markerscale=1.8,
    footer_size=9,
    variant='poster'
)
poster_dir = os.path.join(BASE_DIR, 'outputs', 'maps', 'poster')
save_map(fig_poster, poster_dir, 'A1_analysis1_distribution_map')
plt.close(fig_poster)

# ─────────────────────────────────────────────────────────────────────────────
# LGU VERSION — larger labels, simplified legend
# ─────────────────────────────────────────────────────────────────────────────
print("\nGenerating LGU Planning Version...")
fig_lgu, ax_lgu = build_distribution_map(
    figsize=(16, 14),
    label_size=8.5,
    title_size=17,
    subtitle_size=11,
    legend_fontsize=11,
    markerscale=1.4,
    footer_size=8,
    variant='lgu'
)
# Add LGU-specific annotation
ax_lgu.text(0.01, 0.01,
    'For Official LGU Use — Environmental Management Plan Attachment',
    transform=ax_lgu.transAxes, fontsize=8,
    color='#880000', fontweight='bold', style='italic',
    bbox=dict(boxstyle='round,pad=0.3', facecolor='#FFF9E6',
              edgecolor='#CC8800', linewidth=0.8))
lgu_dir = os.path.join(BASE_DIR, 'outputs', 'maps', 'lgu')
save_map(fig_lgu, lgu_dir, 'LGU_analysis1_distribution_map')
plt.close(fig_lgu)

print("\n--- Analysis 1 Complete ---")
print(f"Outputs saved to: {OUT_DIR}")
