import os
import glob
from faster_whisper import WhisperModel

media_dir = r"c:\Antigravity\EA\media"
videos = sorted(glob.glob(os.path.join(media_dir, "*.mp4")))

print(f"Total videos to scan: {len(videos)}")
model = WhisperModel("base", device="cpu", compute_type="int8")

results = []
for v in videos:
    name = os.path.basename(v)
    if "TED-Talk" in name and "Full" not in name and "Slide-045" not in name:
        # We can analyze TED segments together
        pass
    
    print(f"\n--- Checking: {name} ---")
    try:
        segments, info = model.transcribe(v, beam_size=3)
        segs = list(segments)
        text_len = sum(len(s.text.strip()) for s in segs)
        has_speech = len(segs) > 0 and text_len > 30 and info.language_probability > 0.4
        preview = " ".join([s.text.strip() for s in segs[:2]])[:100]
        print(f"Language: {info.language} (prob: {info.language_probability:.2f}), Segments: {len(segs)}, TextLen: {text_len}")
        print(f"Preview: {preview}")
        results.append({
            "name": name,
            "has_speech": has_speech,
            "lang": info.language,
            "prob": round(info.language_probability, 2),
            "segments_count": len(segs),
            "preview": preview
        })
    except Exception as e:
        print(f"Error checking {name}: {e}")
        results.append({
            "name": name,
            "has_speech": False,
            "error": str(e)
        })

import json
with open(r"c:\Antigravity\EA\curriculum_data\subtitle_audit.json", "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
print("\nScan completed and saved to curriculum_data/subtitle_audit.json")
