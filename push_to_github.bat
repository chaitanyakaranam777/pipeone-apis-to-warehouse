@echo off
echo ===================================================
echo 🚀 PipeOne — Push to GitHub Helper
echo ===================================================
echo.

:: Check if git is installed
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo ❌ Git is not installed or not in your PATH.
    echo Please install Git from https://git-scm.com/ and try again.
    pause
    exit /b
)

:: Initialize git repository if not already initialized
if not exist .git (
    echo 📂 Initializing Git repository...
    git init
) else (
    echo 📂 Git repository already initialized.
)

:: Add files
echo 📝 Adding files to staging area...
git add .

:: Commit files
echo 💾 Committing files...
git commit -m "feat: initial commit - PipeOne data pipeline"

:: Get GitHub URL from user
echo.
echo Please create a new empty repository on GitHub (do not initialize with README or license).
set /p REPO_URL="🔗 Enter your GitHub Repository URL (e.g., https://github.com/username/repo.git): "

if "%REPO_URL%"=="" (
    echo ❌ No URL entered. Exiting...
    pause
    exit /b
)

:: Set remote origin
git remote remove origin >nul 2>nul
git remote add origin %REPO_URL%

:: Rename branch to main
git branch -M main

:: Push to main
echo.
echo 📤 Pushing to GitHub...
git push -u origin main

echo.
echo ===================================================
echo 🎉 Done! If there were no errors, your project is on GitHub.
echo ===================================================
pause
