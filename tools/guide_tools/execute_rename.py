import os
import shutil
import json

guide_dir = r"c:\Antigravity\EA\practitioner guide"
unrelated_dir = os.path.join(guide_dir, "_unrelated_media")
os.makedirs(unrelated_dir, exist_ok=True)

# 1. Move non-book files
unrelated_files = [
    "IMG_5546.PNG", "IMG_5547.PNG", "IMG_5548.PNG", "IMG_5549.PNG", "IMG_5550.PNG",
    "IMG_5551.JPG", "IMG_5552.JPG", "IMG_5553.MOV", "IMG_5554.MOV"
]

for f in unrelated_files:
    src = os.path.join(guide_dir, f)
    if os.path.exists(src):
        dst = os.path.join(unrelated_dir, f)
        shutil.move(src, dst)
        print(f"Moved unrelated file: {f} -> _unrelated_media/")

# 2. Rename book files
with open("scripts/verified_guide_renames.json", "r", encoding="utf-8") as f:
    renames = json.load(f)

success_count = 0
for orig, new_name in renames:
    src = os.path.join(guide_dir, orig)
    dst = os.path.join(guide_dir, new_name)
    if os.path.exists(src):
        os.rename(src, dst)
        success_count += 1
    else:
        print(f"Warning: source file not found: {orig}")

print(f"Successfully renamed {success_count} / {len(renames)} book files!")
