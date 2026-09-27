import os
import re
import json
import time
from PIL import Image, ImageOps
from rapidocr_onnxruntime import RapidOCR

ocr = RapidOCR()
guide_dir = r"c:\Antigravity\EA\practitioner guide"

def get_text_from_region(img, box):
    cropped = img.crop(box)
    cw, ch = cropped.size
    # optimize scale
    scale = min(1.0, 1000.0 / max(cw, ch))
    if scale < 1.0:
        cropped = cropped.resize((int(cw * scale), int(ch * scale)))
    temp_p = f"temp_crop_{int(time.time()*1000)%100000}_{os.getpid()}.jpg"
    cropped.save(temp_p)
    res, _ = ocr(temp_p)
    if os.path.exists(temp_p):
        os.remove(temp_p)
    if not res:
        return []
    return [item[1] for item in res]

def analyze_image(filename):
    p = os.path.join(guide_dir, filename)
    raw_img = Image.open(p)
    img = ImageOps.exif_transpose(raw_img)
    w, h = img.size

    # 1. Footer (bottom 15%)
    footer_texts = get_text_from_region(img, (0, int(h * 0.85), w, h))
    footer_str = " ".join(footer_texts)

    # 2. Header (top 15%)
    header_texts = []
    # If footer doesn't clearly give page number or practitioner, check header
    if not re.search(r'(PRACTITIONER|\b\d+\b)', footer_str, re.IGNORECASE):
        header_texts = get_text_from_region(img, (0, 0, w, int(h * 0.15)))
    header_str = " ".join(header_texts)
    
    # 3. Center if needed
    center_texts = []
    if len(footer_texts) == 0 and len(header_texts) == 0:
        center_texts = get_text_from_region(img, (int(w*0.1), int(h*0.3), int(w*0.9), int(h*0.7)))
    center_str = " ".join(center_texts)
    
    return {
        "file": filename,
        "width": w,
        "height": h,
        "header": header_texts,
        "footer": footer_texts,
        "center": center_texts,
        "header_str": header_str,
        "footer_str": footer_str,
        "center_str": center_str
    }

if __name__ == "__main__":
    import sys
    start_idx = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    end_idx = int(sys.argv[2]) if len(sys.argv) > 2 else 186
    
    all_files = sorted(os.listdir(guide_dir))
    book_files = [f for f in all_files if f.startswith("IMG_") and f.endswith(".JPG") and int(f[4:8]) >= 5555]
    
    target_files = book_files[start_idx:end_idx]
    print(f"Auditing files {start_idx} to {end_idx} (total {len(target_files)})...")
    
    results = []
    for i, fname in enumerate(target_files):
        t0 = time.time()
        info = analyze_image(fname)
        dt = time.time() - t0
        print(f"[{start_idx + i:03d}] {fname} ({dt:.2f}s): F='{info['footer_str']}' | H='{info['header_str'][:30]}' | C='{info['center_str'][:30]}'")
        results.append(info)
        
    out_file = f"scripts/audit_batch_{start_idx}_{end_idx}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"Saved to {out_file}")
