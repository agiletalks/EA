const fs = require('fs');

let raw = fs.readFileSync('slides_summary.json', 'utf8');
if (raw.charCodeAt(0) === 0xFEFF) {
  raw = raw.slice(1);
}
const slides = JSON.parse(raw);

console.log(`Loaded ${slides.length} slides.`);

function cleanText(t) {
  if (!t) return '';
  return t
    .replace(/[0©O]2026 SUSAN DAVID[^\n]*/gi, '')
    .replace(/PERCY POFENG HSU[^\n]*/gi, '')
    .replace(/EAC-C04-0061/gi, '')
    .replace(/EMOTIONAL\s*AGILITY[®@]*/gi, '')
    .trim();
}

const summary = [];

slides.forEach(s => {
  const cleaned = cleanText(s.ocrText);
  const lines = cleaned.split('\n').map(l => l.trim()).filter(Boolean);
  const headline = lines.slice(0, 3).join(' / ');
  summary.push({
    slide: s.slideNumber,
    headline,
    full: cleaned,
    notes: s.notes || ''
  });
});

fs.writeFileSync('slides_clean.json', JSON.stringify(summary, null, 2), 'utf8');

// Print outline
for (let i = 0; i < summary.length; i++) {
  const item = summary[i];
  if (item.headline) {
    console.log(`Slide ${item.slide}: ${item.headline.substring(0, 80)}${item.notes ? ' [NOTE: ' + item.notes.substring(0, 40) + ']' : ''}`);
  }
}
