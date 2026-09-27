const fs = require('fs');

let raw = fs.readFileSync('slides_summary.json', 'utf8');
if (raw.charCodeAt(0) === 0xFEFF) {
  raw = raw.slice(1);
}
const slides = JSON.parse(raw);

function cleanText(t) {
  if (!t) return '';
  return t
    .replace(/[0©O]2026 SUSAN DAVID[^\n]*/gi, '')
    .replace(/PERCY POFENG HSU[^\n]*/gi, '')
    .replace(/EAC-C04-0061/gi, '')
    .replace(/EMOTIONAL\s*AGILITY[®@]*/gi, '')
    .trim();
}

let md = '# Complete Slide Outline (180 Slides)\n\n';

slides.forEach(s => {
  const c = cleanText(s.ocrText);
  const lines = c.split('\n').map(l => l.trim()).filter(Boolean);
  const title = lines[0] || '(Visual/Diagram)';
  const body = lines.slice(1).join(' ');
  md += `### Slide ${s.slideNumber}: ${title}\n`;
  if (body) {
    md += `- **Content**: ${body.substring(0, 160)}${body.length > 160 ? '...' : ''}\n`;
  }
  if (s.notes) {
    md += `- **Notes/Video**: ${s.notes}\n`;
  }
  md += '\n';
});

fs.writeFileSync('curriculum_outline.md', md, 'utf8');
console.log('Saved curriculum_outline.md');
