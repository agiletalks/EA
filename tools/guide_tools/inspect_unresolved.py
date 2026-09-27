import json
import re

with open('scripts/audit_batch_0_30.json', 'r', encoding='utf-8') as f:
    d1 = json.load(f)
with open('scripts/audit_batch_30_186.json', 'r', encoding='utf-8') as f:
    d2 = json.load(f)

all_items = d1 + d2

unresolved = []
for i, it in enumerate(all_items):
    fname = it['file']
    f_str = it['footer_str']
    prac_m = re.search(r'([A-Z\s]+)[\-–—·•P\s]+PRACTITIONER\s*(\d+)', f_str, re.IGNORECASE)
    num_m = [int(n) for n in re.findall(r'\b(\d{1,3})\b', f_str) if 1 <= int(n) <= 135 and int(n) not in [2026]]
    if not prac_m and not num_m:
        unresolved.append((i, fname, it))

print(f"Total unresolved: {len(unresolved)}")
for i, fname, it in unresolved:
    print(f"[{i:03d}] {fname}:")
    print(f"   H: {it['header_str']}")
    print(f"   C: {it['center_str']}")
    print(f"   F: {it['footer_str']}")
