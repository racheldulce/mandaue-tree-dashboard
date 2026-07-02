import re

filepath = r"c:\Users\LENOVO\Documents\2 maps\output\LGU_Tree_Analysis_Report.md"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

# Replace KPIs
content = content.replace("9,342 trees", "9,327 trees")
content = content.replace("9.98% of total", "10.0% of total")

# Replace Status Breakdown
content = content.replace("| Indigenous | 6,513 | 69.7% |", "| Indigenous | 6,502 | 69.7% |")
content = content.replace("| Introduced | 1,631 | 17.5% |", "| Introduced | 1,637 | 17.6% |")
content = content.replace("| Endemic | 932 | 9.98% |", "| Endemic | 932 | 10.0% |")
content = content.replace("| Unknown | 266 | 2.8% |", "| Unknown | 256 | 2.7% |")

# Replace B. PATTERNS AND TRENDS updates
content = content.replace("24.7% of all", "24.6% of all")
content = content.replace("1,505 trees = 16.1% of all trees.", "1,481 trees = 15.9% of all trees.")

# Replace Top 15 Species Table
old_top_15 = """| 1 | Mahogany | 1,505 | Indigenous |
| 2 | Tugas (Vitex parviflora) | 843 | ENDEMIC |
| 3 | Talisay | 832 | Indigenous |
| 4 | Narra | 753 | Indigenous |
| 5 | Dakit | 526 | Indigenous |
| 6 | Nem Tree | 466 | Introduced |
| 7 | Indian Tree | 457 | Introduced |
| 8 | Fire Tree | 301 | Indigenous |
| 9 | Awom | 260 | Indigenous |
| 10 | Unidentified | 260 | Unknown |
| 11 | Rubber Tree | 238 | Indigenous |
| 12 | Mangga | 230 | Indigenous |
| 13 | Indian (variant) | 206 | Introduced |
| 14 | Nangka | 201 | Indigenous |
| 15 | Mansinitas | 188 | Indigenous |"""

new_top_15 = """| 1 | Mahogany | 1,481 | Indigenous |
| 2 | Tugas (Vitex parviflora) | 840 | ENDEMIC |
| 3 | Talisay | 819 | Indigenous |
| 4 | Narra | 745 | Indigenous |
| 5 | Dakit | 515 | Indigenous |
| 6 | Indian tree | 444 | Introduced |
| 7 | Nem tree | 435 | Introduced |
| 8 | Fire tree | 301 | Indigenous |
| 9 | Unidentified | 260 | Unknown |
| 10 | Awom | 255 | Indigenous |
| 11 | Rubber tree | 236 | Indigenous |
| 12 | Mangga | 223 | Indigenous |
| 13 | Indian | 203 | Introduced |
| 14 | Mansinitas | 185 | Indigenous |
| 15 | Nangka | 184 | Indigenous |"""

content = content.replace(old_top_15, new_top_15)

# Replace Introduced Species Table
old_intro = """| Casuntingan | 223 | 55.8% |
| Guizo | 143 | 26.9% |
| Pakna-an | 102 | 24.7% |
| Maguikay | 87 | 25.4% |
| Canduman | 80 | 26.1% |"""

new_intro = """| Casuntingan | 223 | 55.8% |
| Subangdaku | 178 | 15.3% |
| Guizo | 141 | 27.3% |
| Pakna-an | 102 | 24.7% |
| Maguikay | 87 | 25.4% |"""

content = content.replace(old_intro, new_intro)

with open(filepath, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated LGU_Tree_Analysis_Report.md")
