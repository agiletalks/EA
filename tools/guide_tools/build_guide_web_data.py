import json
import os
import re

json_path = "practitioner_guide/practitioner_guide_data.json"
with open(json_path, "r", encoding="utf-8") as f:
    items = json.load(f)

modules_meta = [
    {
        "id": "00_Front_Matter",
        "name": "Front Matter (封面與引言)",
        "icon": "📑",
        "filter": lambda fn: any(k in fn for k in ["PG_Cover", "PG_Page_001_Intro", "PG_Page_003_Intro", "PG_Page_004_BelongsTo", "PG_Page_005_Contents", "PG_Page_006_Sawubona", "PG_Page_007_About"])
    },
    {
        "id": "01_Start_Here",
        "name": "Start Here (導師導引)",
        "icon": "🚀",
        "filter": lambda fn: "StartHere" in fn
    },
    {
        "id": "02_Opening_the_Question",
        "name": "Opening the Question (啟程與破冰)",
        "icon": "🌱",
        "filter": lambda fn: "OpeningTheQuestion" in fn or "Opening" in fn
    },
    {
        "id": "03_Hooked",
        "name": "Hooked (被情緒鉤住)",
        "icon": "🪝",
        "filter": lambda fn: "Hooked" in fn
    },
    {
        "id": "04_Showing_Up",
        "name": "Showing Up (勇敢現身)",
        "icon": "☀️",
        "filter": lambda fn: "ShowingUp" in fn
    },
    {
        "id": "05_Stepping_Out",
        "name": "Stepping Out (抽離跨出)",
        "icon": "🔭",
        "filter": lambda fn: "SteppingOut" in fn
    },
    {
        "id": "06_Walking_Your_Why",
        "name": "Walking Your Why (踐行價值)",
        "icon": "🧭",
        "filter": lambda fn: "WalkingYourWhy" in fn
    },
    {
        "id": "07_Moving_On",
        "name": "Moving On (昂首前行)",
        "icon": "⛰️",
        "filter": lambda fn: "MovingOn" in fn
    },
    {
        "id": "08_Living_Into_the_Question",
        "name": "Living Into the Question (反思與實踐)",
        "icon": "💫",
        "filter": lambda fn: "LivingIntoTheQuestion" in fn or "Living" in fn
    },
    {
        "id": "09_Appendix",
        "name": "Appendix (附錄整合工具)",
        "icon": "📊",
        "filter": lambda fn: "Appendix" in fn
    }
]

def format_html(raw_lines):
    html_blocks = []
    
    for raw in raw_lines:
        line = raw.strip()
        if not line:
            continue
            
        # Check special sections
        if line.lower() in ["the room map", "the clock", "the journey", "the shape", "design notes", "prepare", "hold the reveal", "for the room you have", "in your back pocket", "how to use this guide", "what this module teaches"]:
            html_blocks.append(f'<h3 class="section-title">📌 {line}</h3>')
            continue
            
        # Do / Say
        if re.search(r'\b(do\s*/\s*say|say)\b', line, re.IGNORECASE) and ('"' in line or '“' in line or ':' in line):
            html_blocks.append(f'<div class="guide-card card-dosay"><div class="card-badge">🗣️ DO / SAY</div><div class="card-body">{escape_html(line)}</div></div>')
            continue
            
        # Hold
        if re.search(r'\bhold\b', line, re.IGNORECASE) and (':' in line or 'what' in line.lower()):
            html_blocks.append(f'<div class="guide-card card-hold"><div class="card-badge">🛑 HOLD (留白·不劇透)</div><div class="card-body">{escape_html(line)}</div></div>')
            continue
            
        # Listen for
        if re.search(r'\blisten\s+for\b', line, re.IGNORECASE):
            html_blocks.append(f'<div class="guide-card card-listen"><div class="card-badge">👂 LISTEN FOR (傾聽訊號)</div><div class="card-body">{escape_html(line)}</div></div>')
            continue
            
        # Bridge
        if re.search(r'\bbridge\b', line, re.IGNORECASE) and (':' in line or 'sentence' in line.lower()):
            html_blocks.append(f'<div class="guide-card card-bridge"><div class="card-badge">🌉 BRIDGE (轉場金句)</div><div class="card-body">{escape_html(line)}</div></div>')
            continue
            
        # Watch & Adjust
        if re.search(r'\bwatch\s*&\s*adjust\b', line, re.IGNORECASE):
            html_blocks.append(f'<div class="guide-card card-adjust"><div class="card-badge">⚡ WATCH & ADJUST (應變調整)</div><div class="card-body">{escape_html(line)}</div></div>')
            continue
            
        # Carry
        if re.search(r'\bcarry\b', line, re.IGNORECASE) and ':' in line:
            html_blocks.append(f'<div class="guide-card card-carry"><div class="card-badge">🔥 CARRY (貫穿概念)</div><div class="card-body">{escape_html(line)}</div></div>')
            continue
            
        # Save for later
        if re.search(r'\bsave\s+for\s+later\b', line, re.IGNORECASE):
            html_blocks.append(f'<div class="guide-card card-save"><div class="card-badge">📦 SAVE FOR LATER (後置儲備)</div><div class="card-body">{escape_html(line)}</div></div>')
            continue
            
        # Regular paragraph or quotes
        if line.startswith('“') or line.startswith('"'):
            html_blocks.append(f'<blockquote class="spoken-quote">{escape_html(line)}</blockquote>')
        else:
            html_blocks.append(f'<p class="guide-paragraph">{escape_html(line)}</p>')
            
    return "\n".join(html_blocks)

def escape_html(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

enriched_pages = []

for idx, it in enumerate(items):
    fn = it["file"]
    
    # Identify module
    curr_mod = modules_meta[0]
    for m in modules_meta:
        if m["filter"](fn):
            curr_mod = m
            break
            
    # Page type & label
    page_type = "Workbook"
    page_label = fn.replace("PG_", "").replace(".JPG", "")
    
    if "Cover" in fn:
        page_type = "Cover"
        page_label = "封面 Cover"
    elif "Divider" in fn:
        page_type = "Divider"
        page_label = "單元首頁 Divider"
    elif "_P_" in fn:
        page_type = "Practitioner"
        # e.g. PG_P_StartHere_01 -> Start Here · Practitioner 1
        m_p = re.search(r'_P_([A-Za-z]+)_(\d+)', fn)
        if m_p:
            page_label = f"Practitioner {int(m_p.group(2))}"
    elif "_Page_" in fn:
        page_type = "Workbook"
        m_num = re.search(r'_Page_(\d+)', fn)
        if m_num:
            page_label = f"Page {int(m_num.group(1))}"
    elif "Intro" in fn:
        page_type = "FrontMatter"
        
    html_content = format_html(it.get("raw_lines", []))
    
    enriched_pages.append({
        "index": idx,
        "file": fn,
        "moduleId": curr_mod["id"],
        "moduleName": curr_mod["name"],
        "moduleIcon": curr_mod["icon"],
        "pageType": page_type,
        "pageLabel": page_label,
        "photoUrl": f"/practitioner_guide/photos/{fn}",
        "lineCount": it.get("line_count", 0),
        "rawText": " ".join(it.get("raw_lines", [])),
        "htmlContent": html_content
    })

# Write to web_app/js/guide_data.js as window.PRACTITIONER_GUIDE_DATA
out_js = "web_app/js/guide_data.js"
with open(out_js, "w", encoding="utf-8") as f:
    f.write("window.PRACTITIONER_GUIDE_MODULES = " + json.dumps(modules_meta, default=str, ensure_ascii=False, indent=2) + ";\n\n")
    f.write("window.PRACTITIONER_GUIDE_PAGES = " + json.dumps(enriched_pages, ensure_ascii=False, indent=2) + ";\n")

print(f"Generated {out_js} with {len(enriched_pages)} structured pages!")
