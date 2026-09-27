const fs = require('fs');
let raw = fs.readFileSync('curriculum_data/slides_summary.json', 'utf8');
if (raw.charCodeAt(0) === 0xFEFF) raw = raw.slice(1);
const slides = JSON.parse(raw);

const targetSlides = [55, 60, 61, 114, 126, 140, 169];
targetSlides.forEach(num => {
  const s = slides[num - 1];
  console.log(`=== Slide ${num} ===\n${s.ocrText}\n-------------------`);
});
