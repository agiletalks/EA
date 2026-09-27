import os
import sys
from faster_whisper import WhisperModel

print("Loading Whisper model (tiny.en or base.en)...")
model = WhisperModel("base", device="cpu", compute_type="int8")

video_path = r"c:\Antigravity\EA\media\Slide-016_VID-004_Daily-Life-is-Full-of-Hooks.mp4"
print(f"Transcribing {video_path}...")
segments, info = model.transcribe(video_path, beam_size=5)

print(f"Detected language '{info.language}' with probability {info.language_probability:.2f}")

for segment in segments:
    print(f"[{segment.start:.2f}s -> {segment.end:.2f}s] {segment.text}")
