@echo off
cd /d "%~dp0"
echo Setting up Git repository...

:: 1. Initialize Git
git init
if %errorlevel% neq 0 (
    echo Error: Git is not installed or not in PATH.
    pause
    exit /b
)

:: 2. Stage all files
git add .

:: 3. Commit
git commit -m "Initial setup: Competitor Monitor System"

:: 4. Rename branch to main
git branch -M main

echo.
echo ========================================================
echo [Success] Local repository initialized!
echo.
echo Now, you need to link this to GitHub.
echo 1. Go to your GitHub repository page.
echo 2. Copy the URL (e.g., https://github.com/YourName/repo.git)
echo 3. Run the following command in the terminal:
echo.
echo    git remote add origin [PASTE_YOUR_URL_HERE]
echo    git push -u origin main
echo ========================================================
cmd /k
