@echo off
REM Fabric CICD Repository Maintenance Script
REM =========================================
REM This script helps maintain a clean repository state

echo.
echo 🧹 FABRIC CICD REPOSITORY MAINTENANCE
echo ====================================
echo.

echo 📋 Current Git Status:
git status --short

echo.
echo 🔍 Checking for debug files that should be ignored...
dir /b *debug* *test* *working* *temp* *backup* 2>nul
if errorlevel 1 (
    echo ✅ No debug files found
) else (
    echo ⚠️  Debug files detected - consider adding to .gitignore
)

echo.
echo 📊 Repository Summary:
echo Files in repository: 
dir /b *.py *.md *.yml *.bat | find /c /v ""

echo.
echo 🔄 Recommended maintenance commands:
echo    git pull          - Update from remote
echo    git status        - Check working directory
echo    git add .         - Stage all changes  
echo    git commit -m ""  - Commit with message
echo    git push          - Push to remote
echo.

pause
