import json
import os
import re

json_path = "practitioner_guide/practitioner_guide_data.json"
with open(json_path, "r", encoding="utf-8") as f:
    items = json.load(f)

# Sort items strictly by original photo order IMG_xxxx!
items = sorted(items, key=lambda x: int(re.search(r'IMG_(\d+)', x['file']).group(1)))
print(f"Total items in sequence: {len(items)}")

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

def clean_ocr_text(text):
    # Remove weird OCR artifacts and fix spacing where obvious
    text = re.sub(r'', '', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def escape_html(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

known_headings_lower = [
    'start here', 'how to use this guide', 'two books, one page number',
    'the markers', 'the workbook is not the work', 'the room map',
    'the clock', 'the journey', 'the shape', 'design notes', 'prepare',
    'hold the reveal', 'for the room you have', 'in your back pocket',
    'what this module teaches', 'the order you run', 'the time choices',
    'the content choices', 'guardrails', 'your scope', 'remote and hybrid',
    'the language you\'ll carry', 'order, time, and content', 'rituals',
    'participant resources', 'contents', 'appendix', 'integration map'
]

def format_page_into_reading_html(raw_lines):
    # Step 1: Filter out running header and footer noise
    cleaned_lines = []
    for raw in raw_lines:
        line = clean_ocr_text(raw)
        if not line:
            continue
        # Drop repeated footer branding lines
        if re.search(r'EMOTIONAL\s*AGILITY.*PRACTITIONER.*GUIDE', line, re.IGNORECASE) or \
           re.search(r'@?\s*2026\s*SUSAN\s*DAVID', line, re.IGNORECASE) or \
           re.search(r'VERSION\s*2\.0', line, re.IGNORECASE):
            continue
        # Drop standalone footer page markers like "START HERE · PRACTITIONER 4"
        if re.search(r'^[A-Z\s]+[·\-\–•P\s]+PRACTITIONER\s*\d+$', line, re.IGNORECASE):
            continue
        cleaned_lines.append(line)
        
    if not cleaned_lines:
        return '<p class="empty-state">*[本頁無文字內容或為純圖表，請點擊「原書對照」查看原版高解析度手冊]*</p>'

    # Step 2: Intelligent semantic paragraph assembly
    blocks = []
    curr_paragraph = []

    def flush_paragraph():
        if curr_paragraph:
            full_text = " ".join(curr_paragraph).strip()
            if full_text:
                blocks.append(('p', full_text))
            curr_paragraph.clear()

    for line in cleaned_lines:
        clean_lower = re.sub(r'[^a-z0-9\s]', '', line.lower()).strip()
        
        # 1. Section Title
        if clean_lower in known_headings_lower or (len(line) < 36 and not line.endswith(('.', ',', ';', ':', '-')) and line[0].isupper() and len(curr_paragraph) > 0):
            flush_paragraph()
            blocks.append(('h3', line))
            continue
            
        # 2. Key Facilitator Callout Markers
        marker_match = re.match(r'^(Do\s*/\s*Say|Hold|Listen\s+for|Bridge|Watch\s*&\s*Adjust|Carry|Save\s+for\s+later)\s*:\s*(.*)', line, re.IGNORECASE)
        if marker_match:
            flush_paragraph()
            m_type = marker_match.group(1).strip()
            m_body = marker_match.group(2).strip()
            blocks.append(('marker', m_type, m_body))
            continue
            
        # 3. Spoken dialogue in quotation marks
        if (line.startswith('“') or line.startswith('"')) and (line.endswith('”') or line.endswith('"') or len(line) < 120):
            flush_paragraph()
            blocks.append(('quote', line))
            continue

        # Check if line continues previous sentence or starts new
        curr_paragraph.append(line)

    flush_paragraph()

    # Step 3: Render to clean HTML
    html_output = []
    for b in blocks:
        b_type = b[0]
        
        if b_type == 'h3':
            html_output.append(f'<h3 class="article-heading">{escape_html(b[1])}</h3>')
        elif b_type == 'quote':
            html_output.append(f'<blockquote class="article-quote">{escape_html(b[1])}</blockquote>')
        elif b_type == 'marker':
            m_type = b[1].lower()
            tag_name = b[1]
            body_text = escape_html(b[2])
            
            card_class = "callout-generic"
            icon = "📌"
            if "say" in m_type:
                card_class = "callout-dosay"
                icon = "🗣️"
                tag_name = "DO / SAY"
            elif "hold" in m_type:
                card_class = "callout-hold"
                icon = "🛑"
                tag_name = "HOLD (刻意留白)"
            elif "listen" in m_type:
                card_class = "callout-listen"
                icon = "👂"
                tag_name = "LISTEN FOR (傾聽訊號)"
            elif "bridge" in m_type:
                card_class = "callout-bridge"
                icon = "🌉"
                tag_name = "BRIDGE (轉場金句)"
            elif "adjust" in m_type or "watch" in m_type:
                card_class = "callout-adjust"
                icon = "⚡"
                tag_name = "WATCH & ADJUST (應變處置)"
            elif "carry" in m_type:
                card_class = "callout-carry"
                icon = "🔥"
                tag_name = "CARRY (貫穿概念)"
            elif "save" in m_type:
                card_class = "callout-save"
                icon = "📦"
                tag_name = "SAVE FOR LATER (後置儲備)"
                
            html_output.append(f'''<div class="article-callout {card_class}">
  <div class="callout-header"><span class="callout-icon">{icon}</span> <span class="callout-title">{tag_name}</span></div>
  <div class="callout-content">{body_text}</div>
</div>''')
        else: # paragraph
            p_text = escape_html(b[1])
            # Highlight key facilitation concepts
            for kw in ["Stance language:", "Going meta:", "Mood-task matching:", "Right-sizing:", "Spaciousness:", "Circle:", "The Vault:", "The Room Map:", "The Clock:", "The Journey:", "The Shape:"]:
                if kw.lower() in p_text.lower():
                    pattern = re.compile(re.escape(kw), re.IGNORECASE)
                    p_text = pattern.sub(f'<strong class="concept-keyword">{kw}</strong>', p_text)
            html_output.append(f'<p class="article-paragraph">{p_text}</p>')

    return "\n".join(html_output)

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
    page_type = "學員手冊"
    page_label = fn.replace("PG_", "").replace(".JPG", "")
    
    if "Cover" in fn:
        page_type = "封面"
        page_label = "封面 Cover"
    elif "Divider" in fn:
        page_type = "單元首頁"
        page_label = "單元首頁 Divider"
    elif "_P_" in fn:
        page_type = "導師指引"
        m_p = re.search(r'_P_([A-Za-z]+)_(\d+)', fn)
        if m_p:
            page_label = f"Practitioner {int(m_p.group(2))}"
    elif "_Page_" in fn:
        page_type = "學員手冊"
        m_num = re.search(r'_Page_(\d+)', fn)
        if m_num:
            page_label = f"Page {int(m_num.group(1))}"
    elif "Intro" in fn:
        page_type = "引言"
        
    html_content = format_page_into_reading_html(it.get("raw_lines", []))
    
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

out_js = "web_app/js/guide_data.js"
with open(out_js, "w", encoding="utf-8") as f:
    f.write("window.PRACTITIONER_GUIDE_MODULES = " + json.dumps(modules_meta, default=str, ensure_ascii=False, indent=2) + ";\n\n")
    f.write("window.PRACTITIONER_GUIDE_PAGES = " + json.dumps(enriched_pages, ensure_ascii=False, indent=2) + ";\n")

print(f"Generated clean reading dataset in {out_js} with {len(enriched_pages)} pages in natural book sequence!")
