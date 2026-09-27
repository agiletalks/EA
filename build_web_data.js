const fs = require('fs');

let raw = fs.readFileSync('curriculum_data/slides_summary.json', 'utf8');
if (raw.charCodeAt(0) === 0xFEFF) raw = raw.slice(1);
const slides = JSON.parse(raw);

const mediaList = JSON.parse(fs.readFileSync('curriculum_data/media_inventory.json', 'utf8'));

// Build media lookup map by slide number
const mediaMap = {};
mediaList.forEach(m => {
  if (typeof m.slide === 'number') {
    mediaMap[m.slide] = m;
  }
});

function getModuleInfo(slideNum) {
  if (slideNum <= 10) {
    return { id: 0, code: 'MOD-0', name: '開場定錨', nameEn: 'Opening & Arriving', color: '#10b981' };
  } else if (slideNum <= 35) {
    return { id: 1, code: 'MOD-1', name: '被鉤住', nameEn: 'Hooked', color: '#f59e0b' };
  } else if (slideNum <= 81) {
    return { id: 2, code: 'MOD-2', name: '勇於面對', nameEn: 'Showing Up', color: '#06b6d4' };
  } else if (slideNum <= 105) {
    return { id: 3, code: 'MOD-3', name: '退後一步', nameEn: 'Stepping Out', color: '#8b5cf6' };
  } else if (slideNum <= 144) {
    return { id: 4, code: 'MOD-4', name: '依循價值', nameEn: 'Walking Your Why', color: '#ec4899' };
  } else if (slideNum <= 170) {
    return { id: 5, code: 'MOD-5', name: '向前邁進', nameEn: 'Moving On', color: '#3b82f6' };
  } else {
    return { id: 6, code: 'MOD-6', name: '實踐與收尾', nameEn: 'Living Into The Question', color: '#6366f1' };
  }
}

function cleanText(t) {
  if (!t) return '';
  return t
    .replace(/[0©O]2026 SUSAN DAVID[^\n]*/gi, '')
    .replace(/PERCY POFENG HSU[^\n]*/gi, '')
    .replace(/EAC-C04-0061/gi, '')
    .replace(/EMOTIONAL\s*AGILITY[®@]*/gi, '')
    .trim();
}

function extractQuestions(text) {
  const lines = text.split('\n').map(l => l.trim()).filter(Boolean);
  const qList = [];
  let isQ = false;
  let qBuf = [];

  for (let i = 0; i < lines.length; i++) {
    const l = lines[i];
    if (l.includes('Powerful Question') || l.includes('Question') || l.endsWith('?')) {
      isQ = true;
      if (l.endsWith('?') && !l.includes('Powerful Question')) {
        qList.push(l);
      }
    }
  }

  // Fallback checks
  const questionMatches = text.match(/([A-Z][^?\n]*\?)/g);
  if (questionMatches) {
    questionMatches.forEach(q => {
      const trimmed = q.trim();
      if (trimmed.length > 8 && !qList.includes(trimmed)) {
        qList.push(trimmed);
      }
    });
  }

  return qList;
}

const slideData = slides.map(s => {
  const mod = getModuleInfo(s.slideNumber);
  const cleaned = cleanText(s.ocrText);
  const lines = cleaned.split('\n').map(l => l.trim()).filter(Boolean);
  const title = lines[0] || `Slide ${s.slideNumber}`;
  const questions = extractQuestions(cleaned);
  const media = mediaMap[s.slideNumber] || null;

  return {
    index: s.slideNumber,
    image: `slides_extracted/slide_${String(s.slideNumber).padStart(3, '0')}.png`,
    module: mod,
    title: title,
    bodySummary: lines.slice(1).join(' ').substring(0, 300),
    questions: questions,
    hasMedia: !!media,
    media: media,
    notes: s.notes || ''
  };
});

const output = `// Auto-generated slide deck metadata for Emotional Agility Workshop
window.EA_SLIDES_DATA = ${JSON.stringify(slideData, null, 2)};
`;

fs.writeFileSync('web_app/js/slides_data.js', output, 'utf8');
console.log(`Generated web_app/js/slides_data.js with ${slideData.length} slides.`);
