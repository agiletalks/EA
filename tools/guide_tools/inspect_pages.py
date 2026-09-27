import json
import re

with open('practitioner_guide/practitioner_guide_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

data = sorted(data, key=lambda x: int(re.search(r'IMG_(\d+)', x['file']).group(1)))

for i in range(0, 48):
    it = data[i]
    fn = it['file']
    lc = it.get('line_count', 0)
    print(f"{i:3d}: {fn:40s} (lines: {lc})")
