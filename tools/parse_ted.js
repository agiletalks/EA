const fs = require('fs');

const html = fs.readFileSync('C:\\Users\\agile\\.gemini\\antigravity\\brain\\aa9e3116-a3d1-45f6-aed9-1ec3c71279ef\\.system_generated\\steps\\270\\content.md', 'utf8');
const marker = '<script id="__NEXT_DATA__" type="application/json">';
const start = html.indexOf(marker);
if (start !== -1) {
  const jsonStart = start + marker.length;
  const end = html.indexOf('</script>', jsonStart);
  const jsonStr = html.substring(jsonStart, end);
  const data = JSON.parse(jsonStr);
  fs.writeFileSync('ted_next_data.json', JSON.stringify(data, null, 2), 'utf8');
  console.log('Success! Found __NEXT_DATA__');
  
  // Inspect transcript or video info
  function findKeys(obj, prefix = '') {
    if (!obj || typeof obj !== 'object') return;
    for (const k of Object.keys(obj)) {
      if (k.toLowerCase().includes('transcript') || k.toLowerCase().includes('subtitle') || k.toLowerCase().includes('cue')) {
        console.log(`Found relevant key: ${prefix}.${k}`);
      }
      if (typeof obj[k] === 'object' && obj[k] !== null && prefix.split('.').length < 6) {
        findKeys(obj[k], `${prefix}.${k}`);
      }
    }
  }
  findKeys(data);
} else {
  console.log('Marker not found');
}
