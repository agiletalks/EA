# Emotional Agility® 官方工作坊互動教學平台

> **認證專用編號**: EAC-C04-0061  
> **認證講師**: Percy Pofeng Hsu (許伯豐)  
> **教材版本**: Official Workshop Slides V2 (180 頁全套完整教材)

---

## 🌟 核心特色

1. **原廠投影片 1:1 零失真呈現**
   - 完整載入 180 頁原廠教學投影片高清畫質（1920x1080）。
   - 保留原廠格式與內容，絕不竄改或刪減任何文字與版面。
2. **多媒體點擊即播**
   - 當前投影片若附帶影音素材，**直接點擊投影片上的影音封面或照片**即可觸發沉浸式劇院播放。
   - 原生支援離線高畫質播放與完整時間軸進度控制。
3. **無重疊高對比單軌字幕 (Bilingual Subtitles)**
   - 官方多媒體素材全數配備繁體中文與 English 雙語字幕。
   - 支援即時一鍵切換「繁體中文 / English / 關閉」（快捷鍵 `C`）。
   - 單軌獨立渲染，徹底避免多重文字覆蓋干擾。
4. **雙層資安防護 (Dual Authentication Shield)**
   - **第一層 (伺服器端 HTTP Basic Auth)**：Node.js 伺服器層即時阻擋非授權請求。
   - **第二層 (前端沉浸式鎖定遮罩 Gatekeeper)**：載入即鎖定，支援自適應全螢幕驗證與快捷鍵 `L` 一鍵安全鎖定。
   - **授權帳號**：`aigility-2026` / **授權密碼**：`24721942@Ai`
5. **專業教學輔助工具**
   - ✏️ **投影片即時筆記批註筆**（快捷鍵 `B`，支援紅筆、黃色螢光筆、橡皮擦與一鍵清除）。
   - 💡 **Powerful Questions (提問引導區)**：每頁自動同步原廠教練級引導反思問題。
   - 📝 **個人隨堂筆記區**：自動隨投影片即時儲存於本機，並支援一鍵匯出 Markdown 格式。
   - 📌 **互動便利貼牆 (Sticky Wall)**：支援彩色便利貼即時記錄課堂洞見與發現的情緒鉤子。
   - 📑 **180 頁縮圖快速跳轉抽屜**：隨時點擊縮圖目錄即時切換。
   - 📺 **投影大螢幕模式 (Stage Mode)**：隱藏側欄與所有控制按鈕，提供最純淨的投影分享體驗。

---

## 🚀 快速啟動

### 方式一：Node.js 本機伺服器
```bash
# 啟動伺服器
node server.js
```
開啟瀏覽器訪問：`http://localhost:3000`  
瀏覽器將跳出 HTTP Basic Auth 認證，輸入授權帳密：
- **帳號**：`aigility-2026`
- **密碼**：`24721942@Ai`

### 方式二：Windows 一鍵啟動腳本
雙擊根目錄下的 `啟動教學平台.bat`，系統將自動啟動本機伺服器並開啟瀏覽器。

---

## ⌨️ 常用快捷鍵

| 快捷鍵 | 功能說明 |
| :--- | :--- |
| `→` / `Space` / `PageDown` | 下一頁投影片 |
| `←` / `Backspace` / `PageUp` | 上一頁投影片 |
| `M` | 叫出 / 關閉當前頁面的影音教材 |
| `C` | 影音播放中循環切換中/英/無字幕 |
| `B` | 切換投影片畫筆批註工具列 |
| `F` | 全螢幕切換 |
| `L` | 一鍵安全鎖定畫面 (Lock Screen) |
| `Esc` | 關閉影音彈窗或縮圖目錄 |

---

## 📁 專案架構 (Project Structure)

```text
EA/
├── server.js                        # Node.js 伺服器 (HTTP Basic Auth 雙層認證 + 影音串流 + 靜態託管)
├── package.json                     # Node 專案配置清單
├── 啟動教材平台.bat                  # Windows 一鍵啟動腳本
├── README.md                        # 平台完整操作指引與架構說明
├── .gitignore                       # Git 忽略設定規則
│
├── web_app/                         # 教學平台前端單頁應用 (SPA)
│   ├── css/app.css                  # 深色專業介面與劇場模式樣式
│   ├── js/app.js                    # 核心控制邏輯、畫筆批註、雙層驗證、快捷鍵
│   ├── js/slides_data.js            # 180 頁投影片索引、影音綁定、引導問題
│   └── index.html                   # 教材互動主頁面
│
├── practitioner_guide/              # 導師手冊完整資料庫 (Practitioner Guide)
│   ├── docs/                        # 逐頁萃取之結構化 Markdown 文件 (課程規劃依據)
│   │   ├── 00_Front_Matter.md       # 封面、引言、目錄、Susan David 介紹
│   │   ├── 01_Start_Here.md         # 導引章節 (Practitioner P1~P8, Room Map 規範)
│   │   ├── 02_Opening_the_Question.md # 破冰引導 (Practitioner P1~P5 + 學員頁)
│   │   ├── 03_Hooked.md             # 被鉤住模組 (Practitioner P1~P10 + 學員頁)
│   │   ├── 04_Showing_Up.md         # 勇敢現身模組 (Practitioner P1~P10 + 學員頁)
│   │   ├── 05_Stepping_Out.md       # 抽離跨出模組 (Practitioner P1~P10 + 學員頁)
│   │   ├── 06_Walking_Your_Why.md   # 踐行價值模組 (Practitioner P1~P12 + 學員頁)
│   │   ├── 07_Moving_On.md          # 昂首前行模組 (Practitioner P1~P8 + 學員頁)
│   │   ├── 08_Living_Into_the_Question.md # 結語與反思
│   │   ├── 09_Appendix.md           # 附錄整合圖表
│   │   └── PRACTITIONER_GUIDE_COMPLETE.md # 全冊 186 頁單一完整檢索手冊
│   ├── photos/                      # 186 頁手冊高解析度原檔照片 (具備頁碼識別檔名)
│   └── practitioner_guide_data.json # 結構化 OCR JSON 資料庫
│
├── slides_extracted/                # 180 頁原廠高清投影片 (Slide 1 ~ 180, 1920x1080)
├── slide_previews/                  # 投影片縮圖目錄
├── media/                           # 官方多媒體素材、中英對照雙語 VTT 字幕
├── curriculum/                      # 課程大綱、課堂模組定義與教學規劃
├── raw_sources/                     # 原廠 PPTX / PPSX 原始檔案封存
└── tools/                           # 自動化工具庫
    ├── guide_tools/                 # 手冊頁碼辨識與全文萃取工具
    ├── subtitles/                   # 雙語字幕轉錄與時間軸校正工具
    ├── pipeline/                    # 投影片提取與分析腳本
    └── media_downloader/            # 影片下載與壓縮腳本
```

---
© 2026 Emotional Agility®. Authorized Facilitator Percy Pofeng Hsu. All rights reserved.

