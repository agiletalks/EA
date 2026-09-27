import json
import re

with open('scripts/audit_batch_0_30.json', 'r', encoding='utf-8') as f:
    d1 = json.load(f)
with open('scripts/audit_batch_30_186.json', 'r', encoding='utf-8') as f:
    d2 = json.load(f)

all_items = d1 + d2
print(f"Total audited items: {len(all_items)}")

missing_identification = []

for i, it in enumerate(all_items):
    fname = it['file']
    f_str = it['footer_str']
    h_str = it['header_str']
    c_str = it['center_str']
    
    # 1. Check Practitioner marker
    prac_m = re.search(r'([A-Z\s]+)[\-–—·•P\s]+PRACTITIONER\s*(\d+)', f_str, re.IGNORECASE)
    if prac_m:
        mod = prac_m.group(1).strip()
        # Clean module name
        for prefix in ['EMOTIONALAGILITYOPRACTITIONERGUIDE', 'EMOTIONALAGILITYPRACTITIONERGUIDE', 'EMOTIONALAGILITYPRACTITIONER GUIDE']:
            mod = mod.replace(prefix, '').strip()
        num = int(prac_m.group(2))
        print(f"[{i:03d}] {fname} -> PRACTITIONER: {mod} P{num:02d}")
        continue
        
    # 2. Check numeric page
    # find all numbers in footer
    num_m = [int(n) for n in re.findall(r'\b(\d{1,3})\b', f_str) if 1 <= int(n) <= 135 and int(n) not in [2026]]
    if num_m:
        print(f"[{i:03d}] {fname} -> PAGE: {num_m[-1]:03d} (from '{f_str[:50]}')")
        continue

    # 3. Check center or header
    print(f"[{i:03d}] {fname} -> UNRESOLVED: F='{f_str[:40]}' | H='{h_str[:40]}' | C='{c_str[:40]}'")
    missing_identification.append((i, fname, it))

print(f"\nTotal unresolved: {len(missing_identification)}")
