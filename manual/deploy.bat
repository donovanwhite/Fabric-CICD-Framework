@echo off
echo.
echo ========================================
echo   Fabric Interactive Deployment
echo ========================================
echo   - Fabric workspace item deployment
echo   - Warehouse schema deployment (SQL Project)
echo   - SqlPackage.exe integration
echo ========================================
echo.

if not exist "interactive_deploy.py" (
    echo Error: Must run from manual directory
    echo Usage: cd manual and run deploy.bat
    pause
    exit /b 1
)

if exist "..\envsetup\fabric-cicd-venv\Scripts\activate.bat" (
    echo Activating environment...
    call "..\envsetup\fabric-cicd-venv\Scripts\activate.bat"
    echo Environment activated
    echo.
    echo Launching interactive deployment...
    python interactive_deploy.py
) else (
    echo Virtual environment not found
    echo Please run: cd ..\envsetup and then setup_pyenv.bat
    pause
)

echo.
echo Deployment session completed
pause
