/**
 * Emotional Agility® Practitioner Guide Reader Application
 */

(function () {
  'use strict';

  const AUTH_KEY = 'ea_auth_authenticated';
  const VALID_USERS = ['aigility-2026', 'aigility'];
  const VALID_PASS = '24721942@Ai';

  let currentPageIndex = 0;
  let fontScale = 100;
  let photoZoom = 1.0;
  let isPhotoOpen = false;
  let isDarkTheme = false;
  let searchQuery = '';

  const pages = window.PRACTITIONER_GUIDE_PAGES || [];
  const modules = window.PRACTITIONER_GUIDE_MODULES || [];

  // DOM Elements
  const authModal = document.getElementById('authGateModal');
  const authUsername = document.getElementById('authUsername');
  const authPassword = document.getElementById('authPassword');
  const authErrorMsg = document.getElementById('authErrorMsg');

  const sidebarModuleList = document.getElementById('sidebarModuleList');
  const guideSearchInput = document.getElementById('guideSearchInput');
  const guideSearchClear = document.getElementById('guideSearchClear');

  const metaModuleBadge = document.getElementById('metaModuleBadge');
  const metaTypeBadge = document.getElementById('metaTypeBadge');
  const metaPageTitle = document.getElementById('metaPageTitle');
  const metaPageIndicator = document.getElementById('metaPageIndicator');
  const guideArticle = document.getElementById('guideArticle');

  const btnPrevPage = document.getElementById('btnPrevPage');
  const btnNextPage = document.getElementById('btnNextPage');
  const btnBottomPrev = document.getElementById('btnBottomPrev');
  const btnBottomNext = document.getElementById('btnBottomNext');
  const bottomPageIndicator = document.getElementById('bottomPageIndicator');

  const btnFontDec = document.getElementById('btnFontDec');
  const btnFontInc = document.getElementById('btnFontInc');
  const fontScaleDisplay = document.getElementById('fontScaleDisplay');

  const btnTogglePhoto = document.getElementById('btnTogglePhoto');
  const guidePhotoPanel = document.getElementById('guidePhotoPanel');
  const guidePhotoImg = document.getElementById('guidePhotoImg');
  const photoFilename = document.getElementById('photoFilename');
  const btnPhotoZoomIn = document.getElementById('btnPhotoZoomIn');
  const btnPhotoZoomOut = document.getElementById('btnPhotoZoomOut');
  const btnPhotoZoomReset = document.getElementById('btnPhotoZoomReset');
  const btnClosePhoto = document.getElementById('btnClosePhoto');

  const btnToggleTheme = document.getElementById('btnToggleTheme');
  const btnLock = document.getElementById('btnLock');

  // Initialize
  function init() {
    checkAuth();
    loadPreferences();
    renderSidebar();
    bindEvents();

    // Check URL parameters for page or module
    const urlParams = new URLSearchParams(window.location.search);
    const hash = window.location.hash;
    
    if (urlParams.get('page')) {
      const p = parseInt(urlParams.get('page'), 10);
      if (!isNaN(p) && p >= 0 && p < pages.length) {
        goToPage(p);
        return;
      }
    } else if (hash && hash.startsWith('#page=')) {
      const p = parseInt(hash.replace('#page=', ''), 10);
      if (!isNaN(p) && p >= 0 && p < pages.length) {
        goToPage(p);
        return;
      }
    }

    if (urlParams.get('module')) {
      const modQuery = urlParams.get('module').toLowerCase();
      const matchIdx = pages.findIndex(p => p.moduleId.toLowerCase().includes(modQuery) || p.moduleName.toLowerCase().includes(modQuery));
      if (matchIdx !== -1) {
        goToPage(matchIdx);
        return;
      }
    }

    goToPage(0);
  }

  // Auth Handling
  function checkAuth() {
    const isUnlocked = sessionStorage.getItem(AUTH_KEY) === 'true';
    if (isUnlocked) {
      authModal.style.display = 'none';
    } else {
      authModal.style.display = 'flex';
      setTimeout(() => authUsername.focus(), 100);
    }
  }

  function submitAuth() {
    const user = authUsername.value.trim().toLowerCase();
    const pass = authPassword.value.trim();

    if (VALID_USERS.includes(user) && pass === VALID_PASS) {
      sessionStorage.setItem(AUTH_KEY, 'true');
      authModal.style.display = 'none';
      authErrorMsg.textContent = '';
    } else {
      authErrorMsg.textContent = '帳號或密碼錯誤，請重新輸入。';
      authPassword.value = '';
      authPassword.focus();
    }
  }

  function lockScreen() {
    sessionStorage.removeItem(AUTH_KEY);
    authUsername.value = '';
    authPassword.value = '';
    authErrorMsg.textContent = '';
    authModal.style.display = 'flex';
    authUsername.focus();
  }

  // Preferences
  function loadPreferences() {
    const savedScale = localStorage.getItem('ea_guide_font_scale');
    if (savedScale) {
      fontScale = parseInt(savedScale, 10);
      applyFontScale();
    }

    const savedTheme = localStorage.getItem('ea_guide_theme');
    if (savedTheme === 'dark') {
      isDarkTheme = true;
      document.body.classList.add('theme-dark');
      btnToggleTheme.querySelector('.theme-icon').textContent = '☀️';
    } else {
      isDarkTheme = false;
      document.body.classList.remove('theme-dark');
      btnToggleTheme.querySelector('.theme-icon').textContent = '🌙';
    }

    const savedPhotoOpen = localStorage.getItem('ea_guide_photo_open');
    if (savedPhotoOpen === 'true') {
      openPhotoPanel();
    }
  }

  function applyFontScale() {
    guideArticle.style.fontSize = (fontScale / 100 * 19) + 'px';
    fontScaleDisplay.textContent = fontScale + '%';
    localStorage.setItem('ea_guide_font_scale', fontScale);
  }

  // Render Sidebar
  function renderSidebar() {
    sidebarModuleList.innerHTML = '';

    modules.forEach(mod => {
      const modPages = pages.filter(p => p.moduleId === mod.id);
      if (modPages.length === 0) return;

      const groupEl = document.createElement('div');
      groupEl.className = 'sidebar-module-group';
      groupEl.dataset.moduleId = mod.id;

      const headerEl = document.createElement('div');
      headerEl.className = 'module-header expanded';
      headerEl.innerHTML = `
        <span>${mod.icon || '📁'} ${mod.name}</span>
        <span class="badge">${modPages.length}</span>
      `;
      headerEl.addEventListener('click', () => {
        headerEl.classList.toggle('expanded');
      });

      const listEl = document.createElement('div');
      listEl.className = 'module-pages-list';

      modPages.forEach(p => {
        const itemEl = document.createElement('div');
        itemEl.className = 'sidebar-page-item';
        itemEl.dataset.pageIndex = p.index;
        itemEl.innerHTML = `
          <span class="sidebar-page-name">${p.pageLabel}</span>
          <span class="sidebar-page-type-tag">${p.pageType}</span>
        `;
        itemEl.addEventListener('click', () => {
          goToPage(p.index);
        });
        listEl.appendChild(itemEl);
      });

      groupEl.appendChild(headerEl);
      groupEl.appendChild(listEl);
      sidebarModuleList.appendChild(groupEl);
    });
  }

  // Page Navigation
  function goToPage(index) {
    if (index < 0 || index >= pages.length) return;
    currentPageIndex = index;
    const page = pages[index];

    // Meta bar
    metaModuleBadge.textContent = `${page.moduleIcon || '📖'} ${page.moduleName}`;
    metaTypeBadge.textContent = page.pageType;
    metaPageTitle.textContent = page.pageLabel;
    
    const indicatorText = `第 ${index + 1} / ${pages.length} 頁`;
    metaPageIndicator.textContent = indicatorText;
    bottomPageIndicator.textContent = indicatorText;

    // Render Article Content
    let contentHtml = page.htmlContent || '<p>無文字內容</p>';
    if (searchQuery) {
      contentHtml = highlightText(contentHtml, searchQuery);
    }
    guideArticle.innerHTML = contentHtml;
    const scrollEl = document.getElementById('articleScrollWrapper') || guideArticle;
    scrollEl.scrollTop = 0;

    // Render Photo Scan
    guidePhotoImg.src = page.photoUrl;
    photoFilename.textContent = page.file;
    resetPhotoZoom();

    // Arrows state
    btnPrevPage.disabled = (index === 0);
    btnNextPage.disabled = (index === pages.length - 1);
    btnBottomPrev.disabled = (index === 0);
    btnBottomNext.disabled = (index === pages.length - 1);

    // Update active state in sidebar
    document.querySelectorAll('.sidebar-page-item').forEach(el => {
      if (parseInt(el.dataset.pageIndex, 10) === index) {
        el.classList.add('active');
        // Ensure parent module is expanded
        const group = el.closest('.sidebar-module-group');
        if (group) {
          const hdr = group.querySelector('.module-header');
          if (hdr && !hdr.classList.contains('expanded')) {
            hdr.classList.add('expanded');
          }
        }
        el.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
      } else {
        el.classList.remove('active');
      }
    });

    // Update URL hash
    window.location.hash = `page=${index}`;
  }

  function highlightText(html, query) {
    if (!query) return html;
    try {
      const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
      return html.replace(regex, '<mark class="guide-highlight">$1</mark>');
    } catch (e) {
      return html;
    }
  }

  // Photo Split View Controls
  function openPhotoPanel() {
    isPhotoOpen = true;
    guidePhotoPanel.classList.add('open');
    btnTogglePhoto.classList.add('active');
    localStorage.setItem('ea_guide_photo_open', 'true');
  }

  function closePhotoPanel() {
    isPhotoOpen = false;
    guidePhotoPanel.classList.remove('open');
    btnTogglePhoto.classList.remove('active');
    localStorage.setItem('ea_guide_photo_open', 'false');
  }

  function togglePhotoPanel() {
    if (isPhotoOpen) closePhotoPanel();
    else openPhotoPanel();
  }

  function resetPhotoZoom() {
    photoZoom = 1.0;
    guidePhotoImg.style.transform = `scale(${photoZoom})`;
  }

  // Search
  function handleSearch(q) {
    searchQuery = q.trim();
    if (!searchQuery) {
      guideSearchClear.style.display = 'none';
      document.querySelectorAll('.sidebar-page-item').forEach(el => el.style.display = 'flex');
      document.querySelectorAll('.sidebar-module-group').forEach(el => el.style.display = 'block');
      goToPage(currentPageIndex);
      return;
    }

    guideSearchClear.style.display = 'block';
    const queryLower = searchQuery.toLowerCase();
    let firstMatchIdx = -1;

    pages.forEach((p, idx) => {
      const matches = p.rawText.toLowerCase().includes(queryLower) ||
                      p.pageLabel.toLowerCase().includes(queryLower) ||
                      p.moduleName.toLowerCase().includes(queryLower);
                      
      const itemEl = document.querySelector(`.sidebar-page-item[data-page-index="${idx}"]`);
      if (itemEl) {
        itemEl.style.display = matches ? 'flex' : 'none';
      }

      if (matches && firstMatchIdx === -1) {
        firstMatchIdx = idx;
      }
    });

    // Hide module groups if no children match
    document.querySelectorAll('.sidebar-module-group').forEach(grp => {
      const hasVisible = Array.from(grp.querySelectorAll('.sidebar-page-item')).some(it => it.style.display !== 'none');
      grp.style.display = hasVisible ? 'block' : 'none';
      if (hasVisible) {
        grp.querySelector('.module-header').classList.add('expanded');
      }
    });

    if (firstMatchIdx !== -1) {
      goToPage(firstMatchIdx);
    }
  }

  // Bind Events
  function bindEvents() {
    // Nav Buttons
    btnPrevPage.addEventListener('click', () => goToPage(currentPageIndex - 1));
    btnNextPage.addEventListener('click', () => goToPage(currentPageIndex + 1));
    btnBottomPrev.addEventListener('click', () => goToPage(currentPageIndex - 1));
    btnBottomNext.addEventListener('click', () => goToPage(currentPageIndex + 1));

    // Font Size
    btnFontInc.addEventListener('click', () => {
      if (fontScale < 160) {
        fontScale += 10;
        applyFontScale();
      }
    });
    btnFontDec.addEventListener('click', () => {
      if (fontScale > 80) {
        fontScale -= 10;
        applyFontScale();
      }
    });

    // Photo Controls
    btnTogglePhoto.addEventListener('click', togglePhotoPanel);
    btnClosePhoto.addEventListener('click', closePhotoPanel);

    btnPhotoZoomIn.addEventListener('click', () => {
      if (photoZoom < 2.5) {
        photoZoom += 0.25;
        guidePhotoImg.style.transform = `scale(${photoZoom})`;
      }
    });
    btnPhotoZoomOut.addEventListener('click', () => {
      if (photoZoom > 0.6) {
        photoZoom -= 0.25;
        guidePhotoImg.style.transform = `scale(${photoZoom})`;
      }
    });
    btnPhotoZoomReset.addEventListener('click', resetPhotoZoom);

    // Theme Toggle
    btnToggleTheme.addEventListener('click', () => {
      isDarkTheme = !isDarkTheme;
      if (isDarkTheme) {
        document.body.classList.add('theme-dark');
        btnToggleTheme.querySelector('.theme-icon').textContent = '☀️';
        localStorage.setItem('ea_guide_theme', 'dark');
      } else {
        document.body.classList.remove('theme-dark');
        btnToggleTheme.querySelector('.theme-icon').textContent = '🌙';
        localStorage.setItem('ea_guide_theme', 'light');
      }
    });

    // Lock
    btnLock.addEventListener('click', lockScreen);

    // Search input
    let searchDebounceTimer = null;
    guideSearchInput.addEventListener('input', (e) => {
      clearTimeout(searchDebounceTimer);
      searchDebounceTimer = setTimeout(() => {
        handleSearch(e.target.value);
      }, 250);
    });

    guideSearchClear.addEventListener('click', () => {
      guideSearchInput.value = '';
      handleSearch('');
      guideSearchInput.focus();
    });

    // Keyboard Shortcuts
    window.addEventListener('keydown', (e) => {
      // Don't trigger if typing in inputs
      if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
        if (e.key === 'Escape') {
          e.target.blur();
        }
        return;
      }

      if (e.key === 'ArrowLeft' || e.key === '[') {
        goToPage(currentPageIndex - 1);
      } else if (e.key === 'ArrowRight' || e.key === ']') {
        goToPage(currentPageIndex + 1);
      } else if (e.key.toLowerCase() === 'p') {
        togglePhotoPanel();
      } else if (e.key.toLowerCase() === 'l') {
        lockScreen();
      } else if (e.key === '/') {
        e.preventDefault();
        guideSearchInput.focus();
        guideSearchInput.select();
      }
    });
  }

  // Export to window
  window.GuideApp = {
    init,
    submitAuth,
    goToPage,
    lockScreen
  };

  document.addEventListener('DOMContentLoaded', init);
})();
