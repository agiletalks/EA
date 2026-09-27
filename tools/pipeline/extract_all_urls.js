const fs = require('fs');
let raw = fs.readFileSync('curriculum_data/slides_summary.json', 'utf8');
if (raw.charCodeAt(0) === 0xFEFF) raw = raw.slice(1);
const slides = JSON.parse(raw);

const urlRegex = /(https?:\/\/[^\s]+)/gi;

const allUrls = [];

slides.forEach(s => {
  const ocrMatches = s.ocrText.match(urlRegex) || [];
  const noteMatches = (s.notes || '').match(urlRegex) || [];
  
  const combined = Array.from(new Set([...ocrMatches, ...noteMatches]));
  if (combined.length > 0) {
    allUrls.push({
      slide: s.slideNumber,
      urls: combined,
      title: s.ocrText.split('\n')[0]
    });
  }
});

console.log(`Found ${allUrls.length} slides containing URLs:`);
allUrls.forEach(u => {
  console.log(`Slide ${u.slide} [${u.title}]: ${u.urls.join(', ')}`);
});
