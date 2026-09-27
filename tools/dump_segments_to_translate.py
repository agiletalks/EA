import os
import glob
import json

transcripts_dir = r"c:\Antigravity\EA\curriculum_data\transcripts"
out_file = r"c:\Antigravity\EA\curriculum_data\segments_to_translate.json"

short_videos = [
    "Slide-055_SOCVID-169_You-Are-the-Sky",
    "Slide-058_AUD-002_A-Meditation-for-Self-Compassion",
    "Slide-060_SOCVID-090_3-Steps-to-Show-Yourself-Compassion",
    "Slide-061_SOCVID-281_The-Secret-to-Self-Compassion",
    "Slide-064_SOCVID-109_How-to-Support-Others-During-Challenging-Times",
    "Slide-071_SOCVID_Quick-Tips-for-Bottlers-and-Brooders",
    "Slide-075_SOCVID-251_Learning-How-to-See-in-the-Dark",
    "Slide-080_SOCVID-086_Naming-What-You-Feel",
    "Slide-114_SOCVID-153_What-the-Func",
    "Slide-126_SOCVID-264_Values-in-Conflict",
    "Slide-140_SOCVID-122_Moving-in-Direction-of-Values",
    "Slide-154_SOCVID_How-to-Have-a-Difficult-Conversation",
    "Slide-169_SOCVID-170A_The-Four-Cs"
]

all_items = {}
total_segs = 0

for sv in short_videos:
    jp = os.path.join(transcripts_dir, f"{sv}.json")
    if not os.path.exists(jp):
        print(f"Missing {jp}")
        continue
    with open(jp, "r", encoding="utf-8") as f:
        data = json.load(f)
    segs = data.get("segments", [])
    all_items[sv] = [s["text"].strip() for s in segs]
    total_segs += len(segs)

with open(out_file, "w", encoding="utf-8") as f:
    json.dump(all_items, f, ensure_ascii=False, indent=2)

print(f"Dumped {len(all_items)} videos with {total_segs} segments to {out_file}")
