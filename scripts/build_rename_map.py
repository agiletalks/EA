import json
import re

with open('scripts/audit_batch_0_30.json', 'r', encoding='utf-8') as f:
    d1 = json.load(f)
with open('scripts/audit_batch_30_186.json', 'r', encoding='utf-8') as f:
    d2 = json.load(f)

all_items = d1 + d2

def clean_mod_name(mod):
    mod = re.sub(r'EMOTIONALAGILITY[O\s]*PRACTITIONER[\s]*GUIDE', '', mod, flags=re.IGNORECASE)
    mod = re.sub(r'[^a-zA-Z]', '', mod)
    if 'STARTHERE' in mod: return 'StartHere'
    if 'OPENING' in mod: return 'Opening'
    if 'HOOKED' in mod: return 'Hooked'
    if 'SHOWINGUP' in mod: return 'ShowingUp'
    if 'STEPPINGOUT' in mod: return 'SteppingOut'
    if 'WALKINGYOURWHY' in mod: return 'WalkingYourWhy'
    if 'MOVINGON' in mod: return 'MovingOn'
    if 'LIVING' in mod: return 'LivingIntoTheQuestion'
    if 'APPENDIX' in mod: return 'Appendix'
    return mod

mapping = []

for i, it in enumerate(all_items):
    fname = it['file']
    f_str = it['footer_str']
    h_str = it['header_str']
    c_str = it['center_str']
    
    # Check special cases by index
    # 0: Cover
    if i == 0:
        mapping.append((fname, 'PG_Cover'))
        continue
    if i == 1:
        mapping.append((fname, 'PG_Page_001_Intro'))
        continue
    if i == 2:
        mapping.append((fname, 'PG_Page_003_Intro'))
        continue
    if i == 3:
        mapping.append((fname, 'PG_Page_004_BelongsTo'))
        continue
    if i == 4:
        mapping.append((fname, 'PG_Page_005_Contents'))
        continue
    if i == 5:
        mapping.append((fname, 'PG_Page_006_Sawubona'))
        continue
    if i == 6:
        mapping.append((fname, 'PG_Page_007_About'))
        continue
        
    # Check practitioner
    prac_m = re.search(r'([A-Z\s]+)[\-–—·•P\s]+PRACTITIONER\s*(\d+)', f_str, re.IGNORECASE)
    if prac_m:
        raw_mod = prac_m.group(1).strip()
        mod = clean_mod_name(raw_mod)
        pnum = int(prac_m.group(2))
        tag = f"PG_P_{mod}_{pnum:02d}"
        mapping.append((fname, tag))
        continue
        
    # Check module dividers / intros
    if 'Question' in c_str and 'Arriving' in c_str:
        mapping.append((fname, 'PG_Divider_OpeningTheQuestion'))
        continue
    if 'When the story writes us' in c_str:
        mapping.append((fname, 'PG_Divider_Hooked'))
        continue
    if 'This is the cinema inside our heads' in f_str:
        mapping.append((fname, 'PG_Page_012_Hooked_Intro'))
        continue
    if 'Showing Up' in c_str or 'Showing Up' in h_str:
        mapping.append((fname, 'PG_Divider_ShowingUp'))
        continue
    if 'This is showing up' in f_str:
        mapping.append((fname, 'PG_Page_028_ShowingUp_Intro'))
        continue
    if 'Widening the frame' in c_str:
        mapping.append((fname, 'PG_Divider_SteppingOut'))
        continue
    if 'This is stepping out' in c_str:
        mapping.append((fname, 'PG_Page_050_SteppingOut_Intro'))
        continue
    if 'Living with everyday' in c_str:
        mapping.append((fname, 'PG_Divider_WalkingYourWhy'))
        continue
    if 'This is walking your why' in c_str:
        mapping.append((fname, 'PG_Page_070_WalkingYourWhy_Intro'))
        continue
    if 'Creating meaningful, long-term' in c_str:
        mapping.append((fname, 'PG_Divider_MovingOn'))
        continue
    if 'If you\'ve ever sailed' in c_str or 'If you\'ve ever sailed' in h_str or i == 149:
        mapping.append((fname, 'PG_Page_094_MovingOn_Intro'))
        continue
    if 'Closing reflections and recognitions' in c_str or 'Closing reflections' in c_str:
        mapping.append((fname, 'PG_Divider_LivingIntoTheQuestion'))
        continue
        
    # Check page numbers
    num_m = [int(n) for n in re.findall(r'\b(\d{1,3})\b', f_str) if 1 <= int(n) <= 135 and int(n) not in [2026]]
    if num_m:
        pnum = num_m[-1]
        # Find which module it belongs to based on page range
        # TOC:
        # Opening: 8-11
        # Hooked: 12-27
        # Showing Up: 28-49
        # Stepping Out: 50-69
        # Walking Your Why: 70-93
        # Moving On: 94-115
        # Living Into the Question: 116-120
        # Appendix: 121-129
        mod_name = 'Other'
        if 8 <= pnum <= 11: mod_name = 'Opening'
        elif 12 <= pnum <= 27: mod_name = 'Hooked'
        elif 28 <= pnum <= 49: mod_name = 'ShowingUp'
        elif 50 <= pnum <= 69: mod_name = 'SteppingOut'
        elif 70 <= pnum <= 93: mod_name = 'WalkingYourWhy'
        elif 94 <= pnum <= 115: mod_name = 'MovingOn'
        elif 116 <= pnum <= 120: mod_name = 'LivingIntoTheQuestion'
        elif 121 <= pnum <= 135: mod_name = 'Appendix'
        
        mapping.append((fname, f"PG_Page_{pnum:03d}_{mod_name}"))
        continue

    # Fallback
    mapping.append((fname, f"PG_UNKNOWN_{i:03d}"))

# Check duplicate tags
tag_counts = {}
for fname, tag in mapping:
    tag_counts[tag] = tag_counts.get(tag, 0) + 1

final_mapping = []
seen = {}
for fname, tag in mapping:
    if tag_counts[tag] > 1:
        seen[tag] = seen.get(tag, 0) + 1
        final_tag = f"{tag}_v{seen[tag]}_{fname}"
    else:
        final_tag = f"{tag}_{fname}"
    final_mapping.append((fname, final_tag))

for i, (orig, new_name) in enumerate(final_mapping):
    print(f"[{i:03d}] {orig} -> {new_name}")
