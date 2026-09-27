import os
import re
import json

guide_dir = r"c:\Antigravity\EA\practitioner guide"

with open('scripts/audit_batch_0_30.json', 'r', encoding='utf-8') as f:
    d1 = json.load(f)
with open('scripts/audit_batch_30_186.json', 'r', encoding='utf-8') as f:
    d2 = json.load(f)

all_items = d1 + d2

def clean_mod_name(mod):
    mod = re.sub(r'EMOTIONALAGILITY[O\s]*PRACTITIONER[\s]*GUIDE', '', mod, flags=re.IGNORECASE)
    mod = re.sub(r'[^a-zA-Z]', '', mod)
    if 'STARTHERE' in mod: return 'StartHere'
    if 'OPENING' in mod: return 'OpeningTheQuestion'
    if 'HOOKED' in mod: return 'Hooked'
    if 'SHOWINGUP' in mod: return 'ShowingUp'
    if 'STEPPINGOUT' in mod: return 'SteppingOut'
    if 'WALKINGYOURWHY' in mod: return 'WalkingYourWhy'
    if 'MOVINGON' in mod: return 'MovingOn'
    if 'LIVING' in mod: return 'LivingIntoTheQuestion'
    if 'APPENDIX' in mod: return 'Appendix'
    return mod

mapping = []

# Explicit overrides for verified special/edge cases:
overrides = {
    0: 'PG_Cover',
    1: 'PG_Page_001_Intro',
    2: 'PG_Page_003_Intro',
    3: 'PG_Page_004_BelongsTo',
    4: 'PG_Page_005_Contents',
    5: 'PG_Page_006_Sawubona',
    6: 'PG_Page_007_About',
    15: 'PG_Divider_OpeningTheQuestion',
    23: 'PG_Divider_Hooked',
    24: 'PG_Page_012_Hooked_Intro',
    49: 'PG_Divider_ShowingUp',
    50: 'PG_Page_028_ShowingUp_Intro',
    56: 'PG_P_ShowingUp_06',
    81: 'PG_Divider_SteppingOut',
    82: 'PG_Page_050_SteppingOut_Intro',
    83: 'PG_P_SteppingOut_01_retake1',
    84: 'PG_P_SteppingOut_02_retake1',
    85: 'PG_P_SteppingOut_01_retake2',
    86: 'PG_P_SteppingOut_02_retake2',
    92: 'PG_P_SteppingOut_08',
    98: 'PG_Page_055_SteppingOut',
    112: 'PG_Divider_WalkingYourWhy',
    113: 'PG_Page_070_WalkingYourWhy_Intro',
    133: 'PG_Page_079_WalkingYourWhy',
    142: 'PG_Page_088_WalkingYourWhy',
    144: 'PG_Page_090_WalkingYourWhy',
    148: 'PG_Divider_MovingOn',
    149: 'PG_Page_094_MovingOn_Intro',
    177: 'PG_Divider_LivingIntoTheQuestion',
}

for i, it in enumerate(all_items):
    fname = it['file']
    f_str = it['footer_str']
    h_str = it['header_str']
    c_str = it['center_str']
    
    if i in overrides:
        mapping.append((fname, overrides[i]))
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

    # Check page numbers
    num_m = [int(n) for n in re.findall(r'\b(\d{1,3})\b', f_str) if 1 <= int(n) <= 135 and int(n) not in [2026]]
    if num_m:
        pnum = num_m[-1]
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

    mapping.append((fname, f"PG_UNKNOWN_{i:03d}"))

# Format new filename with original IMG number appended for traceability
final_renames = []
for orig, tag in mapping:
    new_name = f"{tag}_{orig}"
    final_renames.append((orig, new_name))

print("Total files to rename:", len(final_renames))
unknowns = [x for x in final_renames if "UNKNOWN" in x[1]]
print("Any unknowns left?", len(unknowns))

with open("scripts/verified_guide_renames.json", "w", encoding="utf-8") as f:
    json.dump(final_renames, f, ensure_ascii=False, indent=2)
print("Saved mapping to scripts/verified_guide_renames.json")
