import os
import glob
import json
import time
from deep_translator import MyMemoryTranslator

media_dir = r"c:\Antigravity\EA\media"
transcripts_dir = r"c:\Antigravity\EA\curriculum_data\transcripts"

translator = MyMemoryTranslator(source='en-US', target='zh-TW')

def format_vtt_time(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"

# Official terminology fine-tuning
TERMINOLOGY = {
    "情緒敏捷性": "情緒敏捷",
    "掛鉤": "被鉤住",
    "被掛住": "被鉤住",
    "鉤起": "鉤住",
    "瓶裝者": "壓抑者",
    "沉思者": "沉溺者",
    "自我同情": "自我慈悲",
    "自我憐憫": "自我慈悲",
    "靈活性": "敏捷力",
    "走你的原因": "依循價值",
    "展示": "開放接納",
    "走出去": "跨越而出",
    "繼續前進": "勇往直前",
}

def refine_translation(text):
    for k, v in TERMINOLOGY.items():
        text = text.replace(k, v)
    return text

json_files = sorted(glob.glob(os.path.join(transcripts_dir, "*.json")))
print(f"Found {len(json_files)} transcripts.")

for jf in json_files:
    base_name = os.path.splitext(os.path.basename(jf))[0]
    zh_vtt_path = os.path.join(media_dir, f"{base_name}.zh.vtt")
    
    if os.path.exists(zh_vtt_path):
        print(f"Already exists: {base_name}.zh.vtt")
        continue

    print(f"\nTranslating: {base_name}...")
    
    if "Slide-016" in base_name:
        with open(zh_vtt_path, "w", encoding="utf-8") as f:
            f.write("WEBVTT\n\n1\n00:00:00.000 --> 00:00:37.000\n[環境音效：混亂忙碌的都市生活聲響與訊息鈴聲]\n")
        print("Written Slide-016 ambient subtitle.")
        continue

    try:
        with open(jf, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        segments = data.get("segments", [])
        vtt_lines = ["WEBVTT\n"]
        
        for i, s in enumerate(segments):
            text_en = s["text"].strip()
            if not text_en:
                continue
                
            try:
                trans = translator.translate(text_en)
                trans = refine_translation(trans)
            except Exception as te:
                print(f"Translation error on seg {i+1}: {te}")
                trans = text_en
                
            start_str = format_vtt_time(s["start"])
            end_str = format_vtt_time(s["end"])
            vtt_lines.append(f"\n{i+1}\n{start_str} --> {end_str}\n{trans}\n")
            
            # Gentle delay to prevent rate limit
            time.sleep(0.15)
            
        with open(zh_vtt_path, "w", encoding="utf-8") as f:
            f.writelines(vtt_lines)
            
        print(f"Successfully generated {base_name}.zh.vtt ({len(segments)} segments)")
    except Exception as e:
        print(f"Error processing {base_name}: {e}")

print("\nChinese subtitle generation finished!")
