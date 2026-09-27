const fs = require('fs');

const html = fs.readFileSync('C:\\Users\\agile\\.gemini\\antigravity\\brain\\aa9e3116-a3d1-45f6-aed9-1ec3c71279ef\\.system_generated\\steps\\270\\content.md', 'utf8');
const marker = '"transcript":"';
const start = html.indexOf(marker);
if (start !== -1) {
  const jsonStart = start + marker.length;
  const end = html.indexOf('","author"', jsonStart);
  let raw = html.substring(jsonStart, end);
  raw = JSON.parse(`"${raw}"`);
  fs.writeFileSync('c:\\Antigravity\\EA\\curriculum_data\\ted_transcript_zh.txt', raw, 'utf8');
  console.log('Saved TED zh transcript! Length:', raw.length);
} else {
  console.log('Marker not found');
}
