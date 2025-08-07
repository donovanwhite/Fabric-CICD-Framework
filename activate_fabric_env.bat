@echo off
REM Quick activation script for Fabric CICD environment
echo 🔄 Activating Fabric CICD environment...
call conda activate fabric-cicd
if %errorlevel% neq 0 (
    echo ❌ Failed to activate environment 'fabric-cicd'
    echo 💡 Run setup.bat first to create the environment
    pause
    exit /b 1
)

echo ✅ Environment activated: fabric-cicd
echo.

REM Run compatibility check
echo 🔍 Running compatibility check...
python check_compatibility.py
echo.

echo 💡 You can now run: python fabric_deploy.py --help
echo.

REM Stay in the activated environment
cmd /k
