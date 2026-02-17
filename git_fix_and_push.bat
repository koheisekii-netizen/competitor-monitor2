@echo off
cd /d "%~dp0"
echo Fixing Git configuration...

:: 1. Set local git user (to avoid "Please tell me who you are" error)
:: You can change these if you want, but this is enough to make it work.
git config user.email "user@example.com"
git config user.name "Competitor Monitor User"

:: 2. Ensure everything is added
git add .

:: 3. Commit again (in case the first one failed)
git commit -m "Initial commit: Competitor Monitor System"

:: 4. Ensure branch is main
git branch -M main

:: 5. Add remote if missing (just in case)
git remote add origin https://github.com/koheisekii-netizen/competitor-monitor2.git 2>nul

echo.
echo Pushing to GitHub...
git push -u origin main

echo.
echo If you see "Branch 'main' set up to track remote branch 'main'", it succeeded!
pause
