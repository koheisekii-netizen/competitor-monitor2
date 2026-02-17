@echo off
cd /d "%~dp0"
echo Connecting to GitHub repository...

:: Remote already exists? Remove it first to be safe
git remote remove origin 2>nul

:: Add the correct remote URL
git remote add origin https://github.com/koheisekii-netizen/competitor-monitor2.git

echo.
echo Pushing code to main branch...
echo (If a browser window opens, please sign in to GitHub)
echo.

git branch -M main
git push -u origin main

echo.
pause
