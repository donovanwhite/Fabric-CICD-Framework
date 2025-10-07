@echo off
REM Quick activation script for Fabric CICD environment (PyEnv - User Mode)
echo [REFRESH] Activating Fabric CICD environment (PyEnv - User Mode)...
echo    User-level installation - no admin privileges required

REM Set pyenv environment (user directory)
set "PYENV_ROOT=%USERPROFILE%\.pyenv"
set "PYENV_HOME=%USERPROFILE%\.pyenv\pyenv-win"
set "PATH=%PYENV_HOME%\bin;%PYENV_HOME%\shims;%PATH%"
echo [+] PyEnv location: %PYENV_ROOT% (user directory)

REM Activate virtual environment (user directory)
call ..\fabric-cicd-venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment 'fabric-cicd-venv'
    echo [INFO] Run setup_pyenv.bat first to create the user environment
    pause
    exit /b 1
)

echo [OK] Environment activated: fabric-cicd-venv (PyEnv - User Mode)
echo [FOLDER] Virtual environment: %CD%\..\fabric-cicd-venv (user directory)
echo.
echo [INFO] You can now run: python ../core/fabric_deploy.py --help
echo [CREATE] All installations are in user directories - no admin access required
echo.
REM Stay in the activated environment
cmd /k
