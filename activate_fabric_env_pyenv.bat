@echo off
REM Quick activation script for Fabric CICD environment (PyEnv)
echo 🔄 Activating Fabric CICD environment (PyEnv)...

REM Set pyenv environment
set "PYENV_ROOT=%USERPROFILE%\.pyenv"
set "PYENV_HOME=%USERPROFILE%\.pyenv\pyenv-win"
set "PATH=%PYENV_HOME%\bin;%PYENV_HOME%\shims;%PATH%"

REM Activate virtual environment
call fabric-cicd-venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ Failed to activate virtual environment 'fabric-cicd-venv'
    echo 💡 Run setup_pyenv.bat first to create the environment
    pause
    exit /b 1
)

echo ✅ Environment activated: fabric-cicd-venv (PyEnv)
echo.

REM Run compatibility check
echo 🔍 Running compatibility check...
if exist "check_compatibility.py" (
    python check_compatibility.py
) else (
    echo ⚠️  check_compatibility.py not found
)
echo.

echo 💡 You can now run: python fabric_deploy.py --help
echo.

REM Stay in the activated environment
cmd /k
