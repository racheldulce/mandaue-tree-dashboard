"""
==============================================================================
08_create_qgis_project.py
PHASE 6 — QGIS PROJECT & STYLING (QML) GENERATION
==============================================================================
Purpose:
    Generates QGIS style files (.qml) for all analytical layers and creates a
    basic QGIS project file (.qgs) that loads these layers with the styles applied.
    Due to the lack of PyQGIS in the standard environment, this uses XML generation.
"""

import os

BASE_DIR = r'c:\Users\LENOVO\Documents\tree maps - Copy'
GPKG     = os.path.join(BASE_DIR, 'outputs', 'data', 'tree_inventory_cleaned.gpkg')
QGIS_DIR = os.path.join(BASE_DIR, 'outputs', 'qgis')
STYLES_DIR = os.path.join(QGIS_DIR, 'styles')
os.makedirs(STYLES_DIR, exist_ok=True)

# ─────────────────────────────────────────────────────────────────────────────
# 1. GENERATE QML STYLES
# ─────────────────────────────────────────────────────────────────────────────

def write_qml(filename, content):
    path = os.path.join(STYLES_DIR, filename)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

# Analysis 1: Distribution Status (Categorized)
qml_distribution = """<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.28.0-Firenze" styleCategories="Symbology">
  <renderer-v2 type="categorizedSymbol" attr="Distribution Status" symbollevels="0">
    <categories>
      <category symbol="0" value="Endemic" label="Endemic"/>
      <category symbol="1" value="Indigenous" label="Indigenous"/>
      <category symbol="2" value="Introduced" label="Introduced"/>
      <category symbol="3" value="Unknown" label="Unknown"/>
    </categories>
    <symbols>
      <symbol type="marker" name="0"><layer class="SimpleMarker"><prop k="color" v="139,0,0,255"/><prop k="name" v="diamond"/><prop k="size" v="3"/></layer></symbol>
      <symbol type="marker" name="1"><layer class="SimpleMarker"><prop k="color" v="26,92,26,255"/><prop k="name" v="circle"/><prop k="size" v="2.5"/></layer></symbol>
      <symbol type="marker" name="2"><layer class="SimpleMarker"><prop k="color" v="224,123,0,255"/><prop k="name" v="triangle"/><prop k="size" v="2"/></layer></symbol>
      <symbol type="marker" name="3"><layer class="SimpleMarker"><prop k="color" v="128,128,128,255"/><prop k="name" v="square"/><prop k="size" v="1.5"/></layer></symbol>
    </symbols>
  </renderer-v2>
</qgis>"""
write_qml('analysis1_distribution.qml', qml_distribution)

# Analysis 4: Priority (Graduated/Categorized)
qml_priority = """<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis version="3.28.0-Firenze" styleCategories="Symbology|Labeling">
  <renderer-v2 type="categorizedSymbol" attr="priority_class">
    <categories>
      <category symbol="0" value="0" label="Very Low Priority"/>
      <category symbol="1" value="1" label="Low Priority"/>
      <category symbol="2" value="2" label="Moderate Priority"/>
      <category symbol="3" value="3" label="High Priority"/>
      <category symbol="4" value="4" label="Very High Priority"/>
    </categories>
    <symbols>
      <symbol type="fill" name="0"><layer class="SimpleFill"><prop k="color" v="217,240,211,255"/><prop k="outline_color" v="51,51,51,255"/></layer></symbol>
      <symbol type="fill" name="1"><layer class="SimpleFill"><prop k="color" v="144,201,135,255"/><prop k="outline_color" v="51,51,51,255"/></layer></symbol>
      <symbol type="fill" name="2"><layer class="SimpleFill"><prop k="color" v="255,221,119,255"/><prop k="outline_color" v="51,51,51,255"/></layer></symbol>
      <symbol type="fill" name="3"><layer class="SimpleFill"><prop k="color" v="224,123,0,255"/><prop k="outline_color" v="51,51,51,255"/></layer></symbol>
      <symbol type="fill" name="4"><layer class="SimpleFill"><prop k="color" v="139,0,0,255"/><prop k="outline_color" v="51,51,51,255"/></layer></symbol>
    </symbols>
  </renderer-v2>
  <labeling type="simple">
    <settings calloutType="simple">
      <text-style fontWordSpacing="0" fontSize="8" fontLetterSpacing="0" fontItalic="0" textColor="0,0,0,255" fontWeight="50" fontFamily="Arial"/>
      <text-buffer bufferSizeUnits="MM" bufferSize="1" bufferDraw="1" bufferColor="255,255,255,255"/>
      <text-mask maskSize="0" maskSizeUnits="MM" maskEnabled="0"/>
      <placement placement="1" placementFlags="10" dist="0"/>
    </settings>
  </labeling>
</qgis>"""
write_qml('analysis4_priority.qml', qml_priority)

# Create a simple QGS file pointing to the GeoPackage
qgs_content = f"""<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis projectname="Tree Inventory Analysis" version="3.28.0-Firenze">
  <projectlayers>
    <maplayer type="vector" geometry="Point" hasScaleBasedVisibilityFlag="0">
      <id>tree_points_id</id>
      <datasource>{GPKG}|layername=tree_points</datasource>
      <layername>Analysis 1: Tree Distribution</layername>
      <provider encoding="UTF-8">ogr</provider>
    </maplayer>
    <maplayer type="vector" geometry="Polygon" hasScaleBasedVisibilityFlag="0">
      <id>priority_id</id>
      <datasource>{GPKG}|layername=conservation_priority</datasource>
      <layername>Analysis 4: Conservation Priority</layername>
      <provider encoding="UTF-8">ogr</provider>
    </maplayer>
    <maplayer type="vector" geometry="Polygon" hasScaleBasedVisibilityFlag="0">
      <id>hotspot_id</id>
      <datasource>{GPKG}|layername=hotspot_grid</datasource>
      <layername>Analysis 3: Native Hotspot Grid</layername>
      <provider encoding="UTF-8">ogr</provider>
    </maplayer>
    <maplayer type="vector" geometry="Polygon" hasScaleBasedVisibilityFlag="0">
      <id>barangay_id</id>
      <datasource>{GPKG}|layername=barangay_boundaries</datasource>
      <layername>Barangay Boundaries</layername>
      <provider encoding="UTF-8">ogr</provider>
    </maplayer>
  </projectlayers>
  <layer-tree-group name="" expanded="1" checked="Qt::Checked">
    <customproperties>
      <Option/>
    </customproperties>
    <layer-tree-group name="Analyses" expanded="1" checked="Qt::Checked">
      <layer-tree-layer name="Analysis 1: Tree Distribution" id="tree_points_id" expanded="1" checked="Qt::Checked"/>
      <layer-tree-layer name="Analysis 3: Native Hotspot Grid" id="hotspot_id" expanded="1" checked="Qt::Checked"/>
      <layer-tree-layer name="Analysis 4: Conservation Priority" id="priority_id" expanded="1" checked="Qt::Checked"/>
    </layer-tree-group>
    <layer-tree-group name="Base Layers" expanded="1" checked="Qt::Checked">
      <layer-tree-layer name="Barangay Boundaries" id="barangay_id" expanded="1" checked="Qt::Checked"/>
    </layer-tree-group>
  </layer-tree-group>
</qgis>"""
with open(os.path.join(QGIS_DIR, 'tree_analysis.qgs'), 'w', encoding='utf-8') as f:
    f.write(qgs_content)

print(f"Generated QGIS Project (.qgs) and QML styles in {QGIS_DIR}")
