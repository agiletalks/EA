const fs = require('fs');
let raw = fs.readFileSync('slides_summary.json', 'utf8');
if (raw.charCodeAt(0) === 0xFEFF) raw = raw.slice(1);
const slides = JSON.parse(raw);

slides.forEach(s => {
  const ocr = s.ocrText.toUpperCase();
  const hasWatch = ocr.includes('WATCH');
  const hasListen = ocr.includes('LISTEN');
  const hasNote = !!s.notes;

  if (hasWatch || hasListen || hasNote) {
    const firstLine = s.ocrText.split('\n')[0];
    console.log(`Slide ${s.slideNumber}: ${firstLine} | Note: "${s.notes}" | Watch: ${hasWatch} | Listen: ${hasListen}`);
  }
});
