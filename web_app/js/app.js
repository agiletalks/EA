// Emotional Agility Interactive Learning Platform
// EAC-C04-0061 Percy Pofeng Hsu

(function() {
  const slides = window.EA_SLIDES_DATA || [];
  let currentIndex = 1; // 1-based index (1 to 180)
  let isStageMode = false;
  let isAnnotating = false;
  let currentColor = '#ef4444'; // Red pen by default
  let currentStrokeWidth = 3;
  let isDrawing = false;
  let lastX = 0;
  let lastY = 0;

  // DOM Elements
  const slideWrapper = document.getElementById('slideWrapper');
  const slideImage = document.getElementById('slideImage');
  const slideNumText = document.getElementById('slideNumText');
  const totalSlidesText = document.getElementById('totalSlidesText');
  const progressBar = document.getElementById('progressBar');
  const moduleBadge = document.getElementById('moduleBadge');
  const moduleName = document.getElementById('moduleName');
  
  const btnPrev = document.getElementById('btnPrev');
  const btnNext = document.getElementById('btnNext');
  const btnStageMode = document.getElementById('btnStageMode');
  const btnFullscreen = document.getElementById('btnFullscreen');
  const btnMediaHeader = document.getElementById('btnMediaHeader');
  const btnThumbnails = document.getElementById('btnThumbnails');
  const btnToggleSidebar = document.getElementById('btnToggleSidebar');
  const btnToggleWhiteboard = document.getElementById('btnToggleWhiteboard');
  
  const whiteboardToolbar = document.getElementById('whiteboardToolbar');
  const annotationCanvas = document.getElementById('annotationCanvas');
  const ctx = annotationCanvas.getContext('2d');
  
  const companionSidebar = document.getElementById('companionSidebar');
  const tabBtns = document.querySelectorAll('.tab-btn');
  const tabContents = document.querySelectorAll('.tab-content');
  
  const pqContainer = document.getElementById('pqContainer');
  const noteTextarea = document.getElementById('noteTextarea');
  const noteStatus = document.getElementById('noteStatus');
  const btnExportNotes = document.getElementById('btnExportNotes');
  const btnClearNote = document.getElementById('btnClearNote');
  
  const stickyGrid = document.getElementById('stickyGrid');
  const btnAddSticky = document.getElementById('btnAddSticky');
  const stickyColorSelect = document.getElementById('stickyColorSelect');
  
  const guideSlideTitle = document.getElementById('guideSlideTitle');
  const guideModule = document.getElementById('guideModule');
  const guideMediaInfo = document.getElementById('guideMediaInfo');
  const guideNotesText = document.getElementById('guideNotesText');
  
  // Media Modal & Subtitles
  const mediaModal = document.getElementById('mediaModal');
  const modalTitle = document.getElementById('modalTitle');
  const modalBadge = document.getElementById('modalBadge');
  const localVideoPlayer = document.getElementById('localVideoPlayer');
  const modalClose = document.getElementById('modalClose');
  const btnSubZh = document.getElementById('btnSubZh');
  const btnSubEn = document.getElementById('btnSubEn');
  const btnSubOff = document.getElementById('btnSubOff');
  
  let currentSubtitleMode = localStorage.getItem('ea_sub_mode') || 'zh'; // 'zh' | 'en' | 'off'
  
  // Thumbnails Drawer
  const drawerOverlay = document.getElementById('drawerOverlay');
  const thumbnailDrawer = document.getElementById('thumbnailDrawer');
  const drawerScroll = document.getElementById('drawerScroll');
  const btnCloseDrawer = document.getElementById('btnCloseDrawer');

  // Layer 2: Auth Gate Elements
  const authGateModal = document.getElementById('authGateModal');
  const authForm = document.getElementById('authForm');
  const authUser = document.getElementById('authUser');
  const authPass = document.getElementById('authPass');
  const authError = document.getElementById('authError');
  const btnLockScreen = document.getElementById('btnLockScreen');

  // Initialize
  totalSlidesText.textContent = slides.length;
  buildThumbnails();
  loadSlide(1);
  setupAnnotationCanvas();
  loadStickies();
  checkAuthStatus();

  // Resize canvas when window changes
  window.addEventListener('resize', resizeCanvas);

  function resizeCanvas() {
    const rect = slideImage.getBoundingClientRect();
    annotationCanvas.width = rect.width;
    annotationCanvas.height = rect.height;
  }

  // Slide Loading
  function loadSlide(index) {
    if (index < 1) index = 1;
    if (index > slides.length) index = slides.length;
    currentIndex = index;

    const s = slides[index - 1];

    // Image & basic counters
    slideImage.src = s.image;
    slideNumText.textContent = index;
    const pct = ((index / slides.length) * 100).toFixed(1);
    progressBar.style.width = `${pct}%`;

    // Module badge
    moduleBadge.style.borderColor = s.module.color;
    moduleName.textContent = `${s.module.code} · ${s.module.name} (${s.module.nameEn})`;

    // Video Indicator & Clickable Slide Setup
    if (s.hasMedia && s.media) {
      btnMediaHeader.style.display = 'inline-flex';
      slideWrapper.classList.add('has-media');
      slideImage.title = `🎬 點擊講義照片播放：${s.media.title} (${s.media.duration || ''}) · 快速鍵 M`;
    } else {
      btnMediaHeader.style.display = 'none';
      slideWrapper.classList.remove('has-media');
      slideImage.title = '';
    }

    // Powerful Questions
    updateQuestions(s);

    // Notes
    loadNoteForSlide(index);

    // Guide Tab
    updateGuide(s);

    // Clear annotation canvas when changing slides (or keep if desired)
    clearCanvas();

    // Update thumbnail selection
    updateThumbnailSelection();
  }

  function updateQuestions(s) {
    pqContainer.innerHTML = '';
    if (s.questions && s.questions.length > 0) {
      s.questions.forEach(q => {
        const card = document.createElement('div');
        card.className = 'pq-card';
        card.innerHTML = `
          <div class="pq-title">💡 Powerful Question · 深度提問</div>
          <div class="pq-text">${escapeHtml(q)}</div>
        `;
        pqContainer.appendChild(card);
      });
    } else {
      const card = document.createElement('div');
      card.className = 'pq-card';
      card.style.background = 'rgba(255,255,255,0.03)';
      card.style.borderColor = 'rgba(255,255,255,0.08)';
      card.innerHTML = `
        <div class="pq-title" style="color: var(--text-muted)">💭 課堂反思重點</div>
        <div class="pq-text" style="font-size: 13px; font-weight: normal; color: var(--text-muted)">
          ${s.bodySummary || '紀錄您在這一頁的洞見、體會與行動想法。'}
        </div>
      `;
      pqContainer.appendChild(card);
    }
  }

  function updateGuide(s) {
    guideSlideTitle.textContent = `Slide ${s.index}: ${s.title}`;
    guideModule.textContent = `${s.module.name} (${s.module.code})`;
    if (s.hasMedia && s.media) {
      guideMediaInfo.innerHTML = `🎬 <b>關聯影音：</b> ${s.media.title} [${s.media.code}]<br>時長：${s.media.duration || 'N/A'} · 本地高畫質：${s.media.resolution}`;
    } else {
      guideMediaInfo.textContent = '本頁為概念講授與提問討論，無特定外連影音。';
    }
    guideNotesText.textContent = s.notes || '依據原廠教材標準節奏進行。邀請學員停留於當下感受，避免過早尋求標準解答。';
  }

  // Notes persistence per slide
  function loadNoteForSlide(slideNum) {
    const key = `ea_note_slide_${slideNum}`;
    const saved = localStorage.getItem(key) || '';
    noteTextarea.value = saved;
    noteStatus.textContent = saved ? '已自動儲存' : '未有筆記';
  }

  noteTextarea.addEventListener('input', () => {
    const key = `ea_note_slide_${currentIndex}`;
    localStorage.setItem(key, noteTextarea.value);
    noteStatus.textContent = '已自動儲存';
  });

  btnClearNote.addEventListener('click', () => {
    if (confirm('確定要清空本頁筆記嗎？')) {
      const key = `ea_note_slide_${currentIndex}`;
      localStorage.removeItem(key);
      noteTextarea.value = '';
      noteStatus.textContent = '已清空';
    }
  });

  btnExportNotes.addEventListener('click', exportAllNotes);

  function exportAllNotes() {
    let md = `# Emotional Agility® 工作坊學員課堂筆記\n\n`;
    md += `> 講師：Percy Pofeng Hsu (EAC-C04-0061)\n`;
    md += `> 記錄時間：${new Date().toLocaleString()}\n\n---\n\n`;

    let hasAnyNotes = false;
    for (let i = 1; i <= slides.length; i++) {
      const key = `ea_note_slide_${i}`;
      const note = localStorage.getItem(key);
      if (note && note.trim()) {
        hasAnyNotes = true;
        const s = slides[i - 1];
        md += `### [Slide ${i}] ${s.title} (${s.module.name})\n`;
        if (s.questions && s.questions.length > 0) {
          md += `**提問**：${s.questions.join(' / ')}\n\n`;
        }
        md += `**我的筆記**：\n${note}\n\n---\n\n`;
      }
    }

    if (!hasAnyNotes) {
      alert('您尚未在任何投影片中記錄筆記！請在右側筆記區輸入內容後再匯出。');
      return;
    }

    const blob = new Blob([md], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Emotional-Agility-Notes_${new Date().toISOString().slice(0,10)}.md`;
    a.click();
    URL.revokeObjectURL(url);
  }

  // Video Modal & Subtitles Implementation (Clean Single Native Track Display)
  function openMediaModal() {
    const s = slides[currentIndex - 1];
    if (!s.hasMedia || !s.media) return;

    modalTitle.textContent = `${s.media.title}`;
    modalBadge.textContent = `${s.media.code} · ${s.media.resolution || '1080P'}`;

    // Remove any previous track elements to prevent ghost/duplicate cues
    while (localVideoPlayer.firstChild) {
      localVideoPlayer.removeChild(localVideoPlayer.firstChild);
    }

    const baseName = s.media.filename.replace(/\.mp4$/i, '');
    const zhPath = `media/${baseName}.zh.vtt`;
    const enPath = `media/${baseName}.en.vtt`;

    // Create fresh track elements
    const trackZh = document.createElement('track');
    trackZh.kind = 'subtitles';
    trackZh.srclang = 'zh';
    trackZh.label = '繁體中文';
    trackZh.src = zhPath;

    const trackEn = document.createElement('track');
    trackEn.kind = 'subtitles';
    trackEn.srclang = 'en';
    trackEn.label = 'English';
    trackEn.src = enPath;

    localVideoPlayer.appendChild(trackZh);
    localVideoPlayer.appendChild(trackEn);

    localVideoPlayer.src = s.media.local_path;
    mediaModal.classList.add('active');

    // Apply subtitle mode once video is ready
    const applyMode = () => {
      setSubtitleMode(currentSubtitleMode);
      localVideoPlayer.removeEventListener('loadeddata', applyMode);
    };
    localVideoPlayer.addEventListener('loadeddata', applyMode);
    setSubtitleMode(currentSubtitleMode);

    localVideoPlayer.play().catch(e => console.log('Autoplay prevented:', e));
  }

  function closeMediaModal() {
    localVideoPlayer.pause();
    localVideoPlayer.src = '';
    while (localVideoPlayer.firstChild) {
      localVideoPlayer.removeChild(localVideoPlayer.firstChild);
    }
    mediaModal.classList.remove('active');
  }

  function setSubtitleMode(mode) {
    currentSubtitleMode = mode;
    localStorage.setItem('ea_sub_mode', mode);

    btnSubZh.classList.toggle('active', mode === 'zh');
    btnSubEn.classList.toggle('active', mode === 'en');
    btnSubOff.classList.toggle('active', mode === 'off');

    // Switch native HTML5 textTracks cleanly (only one active at a time)
    if (localVideoPlayer.textTracks) {
      for (let i = 0; i < localVideoPlayer.textTracks.length; i++) {
        const t = localVideoPlayer.textTracks[i];
        const lang = (t.language || '').toLowerCase();
        const lbl = (t.label || '').toLowerCase();

        if (mode === 'zh' && (lang === 'zh' || lang === 'zh-tw' || lbl.includes('中文') || lbl.includes('繁體'))) {
          t.mode = 'showing';
        } else if (mode === 'en' && (lang === 'en' || lbl.includes('english'))) {
          t.mode = 'showing';
        } else {
          t.mode = 'disabled';
        }
      }
    }
  }

  function cycleSubtitleMode() {
    if (currentSubtitleMode === 'zh') setSubtitleMode('en');
    else if (currentSubtitleMode === 'en') setSubtitleMode('off');
    else setSubtitleMode('zh');
  }

  btnSubZh.addEventListener('click', () => setSubtitleMode('zh'));
  btnSubEn.addEventListener('click', () => setSubtitleMode('en'));
  btnSubOff.addEventListener('click', () => setSubtitleMode('off'));

  // Trigger video directly by clicking on the slide photo
  slideWrapper.addEventListener('click', () => {
    if (isAnnotating) return; // Don't trigger if drawing on whiteboard
    const s = slides[currentIndex - 1];
    if (s && s.hasMedia && s.media) {
      openMediaModal();
    }
  });

  btnMediaHeader.addEventListener('click', openMediaModal);
  modalClose.addEventListener('click', closeMediaModal);
  mediaModal.addEventListener('click', (e) => {
    if (e.target === mediaModal) closeMediaModal();
  });

  // Navigation
  btnPrev.addEventListener('click', () => loadSlide(currentIndex - 1));
  btnNext.addEventListener('click', () => loadSlide(currentIndex + 1));

  // Keyboard Shortcuts
  window.addEventListener('keydown', (e) => {
    // If typing in textarea, don't trigger slide shortcuts
    if (document.activeElement === noteTextarea || document.activeElement.tagName === 'INPUT') {
      return;
    }

    // Modal Active Special Shortcuts
    if (mediaModal.classList.contains('active')) {
      if (e.key === 'c' || e.key === 'C') {
        e.preventDefault();
        cycleSubtitleMode();
        return;
      }
      if (e.key === ' ') {
        e.preventDefault();
        if (localVideoPlayer.paused) localVideoPlayer.play();
        else localVideoPlayer.pause();
        return;
      }
      if (e.key === 'Escape') {
        e.preventDefault();
        closeMediaModal();
        return;
      }
    }

    switch(e.key) {
      case 'ArrowRight':
      case ' ':
      case 'PageDown':
        e.preventDefault();
        loadSlide(currentIndex + 1);
        break;
      case 'ArrowLeft':
      case 'Backspace':
      case 'PageUp':
        e.preventDefault();
        loadSlide(currentIndex - 1);
        break;
      case 'f':
      case 'F':
        toggleFullscreen();
        break;
      case 'm':
      case 'M':
        if (slides[currentIndex - 1].hasMedia) {
          if (mediaModal.classList.contains('active')) closeMediaModal();
          else openMediaModal();
        }
        break;
      case 'b':
      case 'B':
        toggleWhiteboard();
        break;
      case 'l':
      case 'L':
        lockScreen();
        break;
      case 'Escape':
        if (mediaModal.classList.contains('active')) closeMediaModal();
        if (thumbnailDrawer.classList.contains('active')) closeThumbnails();
        break;
    }
  });

  // Fullscreen
  btnFullscreen.addEventListener('click', toggleFullscreen);
  function toggleFullscreen() {
    if (!document.fullscreenElement) {
      document.documentElement.requestFullscreen().catch(err => alert(err.message));
    } else {
      document.exitFullscreen();
    }
  }

  // Stage Mode (Clean view for screen sharing)
  btnStageMode.addEventListener('click', () => {
    isStageMode = !isStageMode;
    document.body.classList.toggle('stage-mode', isStageMode);
    btnStageMode.classList.toggle('btn-primary', isStageMode);
    btnStageMode.title = isStageMode ? '退出投影大螢幕模式' : '切換為投影大螢幕模式';
  });

  // Sidebar Tabs
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      tabBtns.forEach(b => b.classList.remove('active'));
      tabContents.forEach(c => c.classList.remove('active'));
      btn.classList.add('active');
      const target = document.getElementById(btn.dataset.tab);
      if (target) target.classList.add('active');
    });
  });

  btnToggleSidebar.addEventListener('click', () => {
    companionSidebar.classList.toggle('collapsed');
  });

  // Whiteboard / Annotation
  btnToggleWhiteboard.addEventListener('click', toggleWhiteboard);
  function toggleWhiteboard() {
    isAnnotating = !isAnnotating;
    annotationCanvas.classList.toggle('active', isAnnotating);
    whiteboardToolbar.style.display = isAnnotating ? 'flex' : 'none';
    btnToggleWhiteboard.classList.toggle('btn-primary', isAnnotating);
    if (isAnnotating) resizeCanvas();
  }

  function setupAnnotationCanvas() {
    annotationCanvas.addEventListener('mousedown', (e) => {
      if (!isAnnotating) return;
      isDrawing = true;
      const rect = annotationCanvas.getBoundingClientRect();
      lastX = e.clientX - rect.left;
      lastY = e.clientY - rect.top;
    });

    annotationCanvas.addEventListener('mousemove', (e) => {
      if (!isDrawing || !isAnnotating) return;
      const rect = annotationCanvas.getBoundingClientRect();
      const currentX = e.clientX - rect.left;
      const currentY = e.clientY - rect.top;

      ctx.beginPath();
      ctx.moveTo(lastX, lastY);
      ctx.lineTo(currentX, currentY);
      ctx.strokeStyle = currentColor;
      ctx.lineWidth = currentStrokeWidth;
      ctx.lineCap = 'round';
      ctx.lineJoin = 'round';
      ctx.stroke();

      lastX = currentX;
      lastY = currentY;
    });

    window.addEventListener('mouseup', () => { isDrawing = false; });
  }

  function clearCanvas() {
    ctx.clearRect(0, 0, annotationCanvas.width, annotationCanvas.height);
  }

  document.getElementById('wbClear').addEventListener('click', clearCanvas);
  
  document.querySelectorAll('.color-dot').forEach(dot => {
    dot.addEventListener('click', (e) => {
      currentColor = e.target.dataset.color;
      document.querySelectorAll('.color-dot').forEach(d => d.style.transform = 'scale(1)');
      e.target.style.transform = 'scale(1.3)';
    });
  });

  document.getElementById('wbHighlighter').addEventListener('click', (e) => {
    currentColor = 'rgba(250, 204, 21, 0.4)'; // semi-transparent yellow
    currentStrokeWidth = 18;
  });

  document.getElementById('wbPen').addEventListener('click', () => {
    currentColor = '#ef4444';
    currentStrokeWidth = 3;
  });

  // Sticky Wall
  function loadStickies() {
    const saved = localStorage.getItem('ea_stickies');
    if (saved) {
      try {
        const list = JSON.parse(saved);
        stickyGrid.innerHTML = '';
        list.forEach(item => addStickyDom(item.text, item.color, false));
      } catch(e) {}
    }
  }

  function saveStickies() {
    const cards = stickyGrid.querySelectorAll('.sticky-card');
    const list = [];
    cards.forEach(c => {
      const text = c.querySelector('.sticky-text').innerText;
      let color = 'yellow';
      if (c.classList.contains('color-blue')) color = 'blue';
      if (c.classList.contains('color-green')) color = 'green';
      if (c.classList.contains('color-pink')) color = 'pink';
      list.push({ text, color });
    });
    localStorage.setItem('ea_stickies', JSON.stringify(list));
  }

  btnAddSticky.addEventListener('click', () => {
    const text = prompt('請輸入便箋內容（例如：我的洞見、發現的情緒鉤子、核心價值觀）：');
    if (text && text.trim()) {
      addStickyDom(text.trim(), stickyColorSelect.value, true);
    }
  });

  function addStickyDom(text, color, doSave) {
    const card = document.createElement('div');
    card.className = `sticky-card color-${color}`;
    card.innerHTML = `
      <button class="sticky-del" title="刪除便箋">×</button>
      <div class="sticky-text" contenteditable="true">${escapeHtml(text)}</div>
    `;

    card.querySelector('.sticky-del').addEventListener('click', () => {
      card.remove();
      saveStickies();
    });

    card.querySelector('.sticky-text').addEventListener('blur', saveStickies);

    stickyGrid.prepend(card);
    if (doSave) saveStickies();
  }

  // Thumbnails Drawer
  function buildThumbnails() {
    drawerScroll.innerHTML = '';
    slides.forEach((s) => {
      const item = document.createElement('div');
      item.className = 'thumb-item';
      item.dataset.slide = s.index;
      item.innerHTML = `
        <img src="${s.image}" alt="Slide ${s.index}" loading="lazy">
        <div class="thumb-num">${s.index}</div>
      `;
      item.addEventListener('click', () => {
        loadSlide(s.index);
        closeThumbnails();
      });
      drawerScroll.appendChild(item);
    });
  }

  function updateThumbnailSelection() {
    const items = drawerScroll.querySelectorAll('.thumb-item');
    items.forEach(it => {
      if (parseInt(it.dataset.slide) === currentIndex) {
        it.classList.add('current');
        it.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' });
      } else {
        it.classList.remove('current');
      }
    });
  }

  function openThumbnails() {
    drawerOverlay.classList.add('active');
    thumbnailDrawer.classList.add('active');
    updateThumbnailSelection();
  }

  function closeThumbnails() {
    drawerOverlay.classList.remove('active');
    thumbnailDrawer.classList.remove('active');
  }

  btnThumbnails.addEventListener('click', openThumbnails);
  btnCloseDrawer.addEventListener('click', closeThumbnails);
  drawerOverlay.addEventListener('click', closeThumbnails);

  // Layer 2: Auth Gatekeeper Logic
  function checkAuthStatus() {
    const isAuthed = sessionStorage.getItem('ea_auth_authenticated') === 'true';
    if (!isAuthed) {
      if (authGateModal) {
        authGateModal.classList.add('active');
        authGateModal.style.display = 'flex';
        setTimeout(() => authUser && authUser.focus(), 150);
      }
    } else {
      if (authGateModal) {
        authGateModal.classList.remove('active');
        authGateModal.style.display = 'none';
      }
    }
  }

  function lockScreen() {
    sessionStorage.removeItem('ea_auth_authenticated');
    if (mediaModal && mediaModal.classList.contains('active')) {
      closeMediaModal();
    }
    if (thumbnailDrawer && thumbnailDrawer.classList.contains('active')) {
      closeThumbnails();
    }
    if (authError) authError.style.display = 'none';
    if (authPass) authPass.value = '';
    if (authGateModal) {
      authGateModal.classList.add('active');
      authGateModal.style.display = 'flex';
      setTimeout(() => authUser && authUser.focus(), 150);
    }
  }

  if (authForm) {
    authForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const user = authUser ? authUser.value.trim() : '';
      const pass = authPass ? authPass.value : '';

      if (user === 'aigility-2026' && pass === '24721942@Ai') {
        sessionStorage.setItem('ea_auth_authenticated', 'true');
        if (authError) authError.style.display = 'none';
        if (authGateModal) {
          authGateModal.classList.remove('active');
          authGateModal.style.display = 'none';
        }
      } else {
        if (authError) authError.style.display = 'block';
        if (authPass) {
          authPass.value = '';
          authPass.focus();
        }
      }
    });
  }

  if (btnLockScreen) {
    btnLockScreen.addEventListener('click', lockScreen);
  }

  // Helper
  function escapeHtml(str) {
    return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  }

})();
