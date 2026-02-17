@echo off
cd /d "%~dp0"
echo Updating GitHub repository with latest changes...

:: Stage all changes
git add .

:: Commit
git commit -m "Fix: workflow and scraper improvements"

:: Push
git push

echo.
echo Done! Now go to GitHub Actions and run the workflow again.
pause
