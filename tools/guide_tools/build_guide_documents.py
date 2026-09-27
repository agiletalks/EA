import json
import os
import re

json_path = "scripts/extracted_practitioner_guide.json"
with open(json_path, "r", encoding="utf-8") as f:
    items = json.load(f)

print(f"Total extracted pages loaded: {len(items)}")

# Categorize pages by section
sections = [
    {
        "id": "00_Front_Matter",
        "title": "Front Matter (Cover, Introduction, Contents & About)",
        "match": lambda fn: any(k in fn for k in ["PG_Cover", "PG_Page_001_Intro", "PG_Page_003_Intro", "PG_Page_004_BelongsTo", "PG_Page_005_Contents", "PG_Page_006_Sawubona", "PG_Page_007_About"]),
        "pages": []
    },
    {
        "id": "01_Start_Here",
        "title": "Start Here (Practitioner Guide P1 ~ P8)",
        "match": lambda fn: "StartHere" in fn,
        "pages": []
    },
    {
        "id": "02_Opening_the_Question",
        "title": "Opening the Question (Arriving)",
        "match": lambda fn: "OpeningTheQuestion" in fn or "Opening" in fn,
        "pages": []
    },
    {
        "id": "03_Hooked",
        "title": "Hooked (When the story writes us)",
        "match": lambda fn: "Hooked" in fn,
        "pages": []
    },
    {
        "id": "04_Showing_Up",
        "title": "Showing Up (Meeting the moment)",
        "match": lambda fn: "ShowingUp" in fn,
        "pages": []
    },
    {
        "id": "05_Stepping_Out",
        "title": "Stepping Out (Widening the frame)",
        "match": lambda fn: "SteppingOut" in fn,
        "pages": []
    },
    {
        "id": "06_Walking_Your_Why",
        "title": "Walking Your Why (Living with everyday courage)",
        "match": lambda fn: "WalkingYourWhy" in fn,
        "pages": []
    },
    {
        "id": "07_Moving_On",
        "title": "Moving On (Creating meaningful, long-term change)",
        "match": lambda fn: "MovingOn" in fn,
        "pages": []
    },
    {
        "id": "08_Living_Into_the_Question",
        "title": "Living Into the Question (Closing reflections and recognitions)",
        "match": lambda fn: "LivingIntoTheQuestion" in fn or "Living" in fn,
        "pages": []
    },
    {
        "id": "09_Appendix",
        "title": "Appendix (Integration Maps & Reference Tools)",
        "match": lambda fn: "Appendix" in fn,
        "pages": []
    }
]

# Assign pages to sections
for it in items:
    fn = it["file"]
    assigned = False
    for sec in sections:
        if sec["match"](fn):
            sec["pages"].append(it)
            assigned = True
            break
    if not assigned:
        print(f"Warning: unassigned file {fn}")

# Create output docs directory
docs_dir = r"c:\Antigravity\EA\practitioner_guide\docs"
os.makedirs(docs_dir, exist_ok=True)

# Generate master markdown
master_md = ["# Emotional Agility® Practitioner Guide (教師手冊完整檔案庫)\n"]
master_md.append("> 本手冊彙整《Emotional Agility》實踐者教師指引與學員手冊內容，逐頁萃取文字，作為課程細節規劃、引導語（Do/Say）、控場心法（Hold / Listen for / Bridge）、應變機制（Watch & Adjust）之依據。\n")
master_md.append("## 目錄 (Table of Contents)\n")

for sec in sections:
    sec_id = sec["id"]
    sec_title = sec["title"]
    page_count = len(sec["pages"])
    master_md.append(f"- [{sec_title}](#{sec_id.lower().replace('_', '-')}) ({page_count} 頁)")

master_md.append("\n---\n")

for sec in sections:
    sec_id = sec["id"]
    sec_title = sec["title"]
    sec_md = [f"# {sec_title}\n"]
    master_md.append(f"\n<a id=\"{sec_id.lower().replace('_', '-')}\"></a>\n# {sec_title}\n")
    
    for it in sec["pages"]:
        fn = it["file"]
        # Format human-friendly subtitle
        sub = fn.replace("PG_", "").replace(".JPG", "")
        
        page_block = []
        page_block.append(f"## 📄 {sub}\n")
        page_block.append(f"*檔案來源: `practitioner_guide/photos/{fn}`*\n")
        page_block.append(it["markdown"])
        page_block.append("\n---\n")
        
        sec_md.extend(page_block)
        master_md.extend(page_block)
        
    sec_file_path = os.path.join(docs_dir, f"{sec_id}.md")
    with open(sec_file_path, "w", encoding="utf-8") as sf:
        sf.write("\n".join(sec_md))
    print(f"Generated: {sec_file_path} ({len(sec['pages'])} pages)")

master_file_path = os.path.join(docs_dir, "PRACTITIONER_GUIDE_COMPLETE.md")
with open(master_file_path, "w", encoding="utf-8") as mf:
    mf.write("\n".join(master_md))
print(f"Master guide generated: {master_file_path}")
