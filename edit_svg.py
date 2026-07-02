import xml.etree.ElementTree as ET
import re

svg_files = [
    r"c:\Users\LENOVO\Documents\2 maps\analysis1_distribution\analysis1_distribution_map.svg",
    r"c:\Users\LENOVO\Documents\2 maps\analysis4_priority\analysis4_conservation_priority_map.svg",
    r"c:\Users\LENOVO\Documents\2 maps\analysis3_hotspot\analysis3_native_tree_hotspot.svg"
]

for svg_file in svg_files:
    print(f"\n--- {svg_file} ---")
    try:
        tree = ET.parse(svg_file)
        root = tree.getroot()
        # Find all text elements. Need to handle SVG namespace.
        ns = {'svg': 'http://www.w3.org/2000/svg'}
        for text_elem in root.findall('.//svg:text', ns):
            # Text can be in the text element itself or in child tspan elements
            texts = []
            if text_elem.text and text_elem.text.strip():
                texts.append(text_elem.text.strip())
            for tspan in text_elem.findall('.//svg:tspan', ns):
                if tspan.text and tspan.text.strip():
                    texts.append(tspan.text.strip())
            if texts:
                print(repr(" ".join(texts)))
    except Exception as e:
        print("Error:", e)
