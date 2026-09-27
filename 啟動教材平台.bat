@echo off
chcp 65001 >nul
echo =========================================================
echo    Emotional Agility® 官方工作坊互動教學平台
echo    講師：Percy Pofeng Hsu (EAC-C04-0061)
echo =========================================================
echo.
echo 正在啟動本機離線伺服器...
start "" "http://127.0.0.1:3000"
node server.js
pause
