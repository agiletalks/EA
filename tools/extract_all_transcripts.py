import os
import glob
import json
from faster_whisper import WhisperModel

media_dir = r"c:\Antigravity\EA\media"
out_dir = r"c:\Antigravity\EA\curriculum_data\transcripts"
os.makedirs(out_dir, exist_ok=True)

def format_vtt_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"

model = WhisperModel("base", device="cpu", compute_type="int8")

videos = sorted(glob.glob(os.path.join(media_dir, "*.mp4")))
print(f"Found {len(videos)} videos.")

for v in videos:
    base_name = os.path.splitext(os.path.basename(v))[0]
    json_path = os.path.join(out_dir, f"{base_name}.json")
    vtt_en_path = os.path.join(media_dir, f"{base_name}.en.vtt")
    
    if os.path.exists(json_path) and os.path.exists(vtt_en_path):
        print(f"Already done: {base_name}")
        continue
    
    print(f"\nProcessing: {base_name}...")
    
    # Handle ambient sound video
    if "Slide-016" in base_name:
        segments_data = [
            {"start": 0.0, "end": 37.0, "text": "[Ambient sounds: bustling city sounds, notifications, rush hour]"}
        ]
        with open(vtt_en_path, "w", encoding="utf-8") as f:
            f.write("WEBVTT\n\n00:00:00.000 --> 00:00:37.000\n[Ambient sounds: bustling city sounds, notifications, rush hour]\n")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({"language": "en", "segments": segments_data}, f, ensure_ascii=False, indent=2)
        print("Generated ambient subtitle for Slide 16.")
        continue

    try:
        segments, info = model.transcribe(v, beam_size=5, language="en")
        segments_data = []
        vtt_lines = ["WEBVTT\n"]
        
        for i, s in enumerate(segments):
            text = s.text.strip()
            if not text:
                continue
            segments_data.append({
                "id": i + 1,
                "start": round(s.start, 3),
                "end": round(s.end, 3),
                "text": text
            })
            start_str = format_vtt_time(s.start)
            end_str = format_vtt_time(s.end)
            vtt_lines.append(f"\n{i+1}\n{start_str} --> {end_str}\n{text}\n")
            
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({"language": info.language, "segments": segments_data}, f, ensure_ascii=False, indent=2)
            
        with open(vtt_en_path, "w", encoding="utf-8") as f:
            f.writelines(vtt_lines)
            
        print(f"Saved {len(segments_data)} segments to {base_name}.en.vtt and JSON.")
    except Exception as e:
        print(f"Error processing {base_name}: {e}")

print("\nAll English transcriptions completed!")
