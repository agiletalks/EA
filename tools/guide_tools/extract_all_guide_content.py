import os
import re
import glob
import json
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from PIL import Image, ImageOps
from rapidocr_onnxruntime import RapidOCR

guide_dir = r"c:\Antigravity\EA\practitioner guide"

def process_single_image(file_path):
    filename = os.path.basename(file_path)
    ocr = RapidOCR()
    raw_img = Image.open(file_path)
    img = ImageOps.exif_transpose(raw_img)
    w, h = img.size
    
    # Scale for optimal speed & quality (max dimension ~1800)
    scale = min(1.0, 1800.0 / max(w, h))
    sw, sh = int(w * scale), int(h * scale)
    img_scaled = img.resize((sw, sh))
    
    temp_p = f"temp_ocr_{os.getpid()}_{int(time.time()*1000)%100000}.jpg"
    img_scaled.save(temp_p)
    res, _ = ocr(temp_p)
    if os.path.exists(temp_p):
        try: os.remove(temp_p)
        except: pass
        
    if not res:
        return {
            "file": filename,
            "lines": [],
            "markdown": "*[No text detected on this page]*"
        }
        
    # Scale coordinates back to original or normalized
    # res items: [box, text, score]
    # box is 4 points: [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
    boxes = []
    for item in res:
        box = item[0]
        text = item[1].strip()
        score = float(item[2])
        if not text:
            continue
        xs = [pt[0] for pt in box]
        ys = [pt[1] for pt in box]
        min_x, max_x = min(xs) / scale, max(xs) / scale
        min_y, max_y = min(ys) / scale, max(ys) / scale
        height = max_y - min_y
        boxes.append({
            "text": text,
            "score": score,
            "x": min_x,
            "y": min_y,
            "w": max_x - min_x,
            "h": height,
            "center_y": (min_y + max_y) / 2.0
        })
        
    # Sort boxes primarily by vertical position (Y)
    # Group boxes on the same line if their Y is within 0.5 * avg line height
    boxes.sort(key=lambda b: (b['y'], b['x']))
    
    lines = []
    if boxes:
        avg_h = sum(b['h'] for b in boxes) / len(boxes)
        y_thresh = max(18.0, avg_h * 0.6)
        
        current_line = [boxes[0]]
        for b in boxes[1:]:
            last_b = current_line[-1]
            if abs(b['center_y'] - last_b['center_y']) <= y_thresh:
                current_line.append(b)
            else:
                # Sort line items left to right
                current_line.sort(key=lambda x: x['x'])
                lines.append(current_line)
                current_line = [b]
        if current_line:
            current_line.sort(key=lambda x: x['x'])
            lines.append(current_line)

    # Format into markdown
    md_lines = []
    for line in lines:
        line_str = " ".join([b['text'] for b in line])
        # Format key facilitator labels
        for keyword in ["Do / Say:", "Do/Say:", "Hold:", "Listen for:", "Bridge:", "Watch & Adjust:", "Watch&Adjust:", "Carry:", "Save for later:", "In Your Back Pocket:"]:
            if keyword.lower() in line_str.lower():
                pattern = re.compile(re.escape(keyword), re.IGNORECASE)
                line_str = pattern.sub(f"**{keyword}**", line_str)
                
        for section_title in ["The Room Map", "The Clock", "The Journey", "The Shape", "Design Notes", "Prepare", "Hold the Reveal", "For the Room You Have", "How to Use This Guide"]:
            if line_str.strip().lower() == section_title.lower():
                line_str = f"### {section_title}"
                
        md_lines.append(line_str)
        
    markdown_text = "\n\n".join(md_lines)
    
    return {
        "file": filename,
        "line_count": len(lines),
        "markdown": markdown_text,
        "raw_lines": [" ".join([b['text'] for b in line]) for line in lines]
    }

def main():
    files = sorted(glob.glob(os.path.join(guide_dir, "PG_*.JPG")))
    print(f"Starting parallel full-page text extraction for {len(files)} pages...")
    t0 = time.time()
    
    results = {}
    with ProcessPoolExecutor(max_workers=6) as executor:
        future_to_file = {executor.submit(process_single_image, f): f for f in files}
        completed = 0
        for future in as_completed(future_to_file):
            completed += 1
            res = future.result()
            results[res['file']] = res
            if completed % 15 == 0 or completed == len(files):
                print(f"Extracted {completed}/{len(files)} pages ({time.time() - t0:.1f}s)...")
                
    # Sort results in alphabetical order of filename
    sorted_files = sorted(results.keys())
    
    # Save master JSON
    json_path = "scripts/extracted_practitioner_guide.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump([results[f] for f in sorted_files], f, ensure_ascii=False, indent=2)
    print(f"All {len(files)} pages extracted and saved to {json_path} in {time.time() - t0:.1f}s!")

if __name__ == "__main__":
    main()
