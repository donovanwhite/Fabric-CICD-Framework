@echo off
REM =====================================================================
REM Microsoft Fabric CI/CD Environment Setup Script (PyEnv Version)
REM =====================================================================
REM This script sets up a complete development environment for Fabric CICD
REM using pyenv for Python version management instead of conda.
REM Perfect for users who cannot install conda or prefer pyenv.

echo.
echo 🚀 MICROSOFT FABRIC CI/CD ENVIRONMENT SETUP (PYENV)
echo ===================================================
echo 💡 This script works without admin permissions
echo    Python packages will be installed at user level if needed
echo.

REM Check if pyenv-win is installed
where pyenv >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ pyenv-win found in PATH
    goto :PYENV_FOUND
)

REM Check if pyenv-win exists in default location
if exist "%USERPROFILE%\.pyenv\pyenv-win\bin\pyenv.bat" (
    echo ✅ pyenv-win found at %USERPROFILE%\.pyenv
    set "PYENV_ROOT=%USERPROFILE%\.pyenv"
    set "PYENV_HOME=%USERPROFILE%\.pyenv\pyenv-win"
    set "PYENV=%USERPROFILE%\.pyenv\pyenv-win"
    set "PATH=%PYENV_HOME%\bin;%PYENV_HOME%\shims;%PATH%"
    goto :PYENV_FOUND
)
if %errorlevel% neq 0 (
    echo ❌ pyenv-win is not installed or not in PATH
    echo.
    echo 💡 Installing pyenv-win...
    echo.
    
    REM Check if we have git
    echo 🔍 Checking for Git installation...
    git --version > git_check.tmp 2>&1
    if exist git_check.tmp (
        type git_check.tmp
        del git_check.tmp
        echo ✅ Git found
    ) else (
        echo ❌ Git is required to install pyenv-win
        echo 💡 Please install Git first: https://git-scm.com/download/win
        echo    Or download pyenv-win manually from: https://github.com/pyenv-win/pyenv-win
        pause
        exit /b 1
    )
    
    REM Install pyenv-win
    echo 📦 Cloning pyenv-win repository...
    git clone https://github.com/pyenv-win/pyenv-win.git %USERPROFILE%\.pyenv
    if %errorlevel% neq 0 (
        echo ❌ Failed to clone pyenv-win repository
        pause
        exit /b 1
    )
    
    REM Add pyenv to PATH
    set "PYENV_ROOT=%USERPROFILE%\.pyenv"
    set "PYENV_HOME=%USERPROFILE%\.pyenv\pyenv-win"
    set "PYENV=%USERPROFILE%\.pyenv\pyenv-win"
    set "PATH=%PYENV_HOME%\bin;%PYENV_HOME%\shims;%PATH%"
    
    echo ✅ pyenv-win installed successfully
    echo.
    echo ⚠️  IMPORTANT: You need to add pyenv to your PATH permanently.
    echo    Add these to your system environment variables:
    echo    PYENV_ROOT=%USERPROFILE%\.pyenv
    echo    PYENV_HOME=%USERPROFILE%\.pyenv\pyenv-win
    echo    PATH=%PYENV_HOME%\bin;%PYENV_HOME%\shims;[existing PATH]
    echo.
    echo 🔄 Refreshing environment...
    
) else (
    echo ✅ pyenv-win found
    set "PYENV_ROOT=%USERPROFILE%\.pyenv"
    set "PYENV_HOME=%USERPROFILE%\.pyenv\pyenv-win"
)

:PYENV_FOUND

REM Check Python version requirements
echo.
echo 🔍 Checking Python requirements...
echo    Required: Python 3.8+ (3.12 recommended for best compatibility)
echo.

REM Check if Python 3.12 is available via pyenv
echo 📋 Checking available Python versions...
pyenv versions
echo.

REM Install Python 3.12.10 if not available
pyenv versions | findstr "3.12.10" >nul
if %errorlevel% neq 0 (
    echo 📦 Installing Python 3.12.10...
    pyenv install 3.12.10
    if %errorlevel% neq 0 (
        echo ❌ Failed to install Python 3.12.10
        echo 💡 Try manually: pyenv install 3.12.10
        pause
        exit /b 1
    )
    echo ✅ Python 3.12.10 installed successfully
) else (
    echo ✅ Python 3.12.10 already available
)

REM Set local Python version for this project
echo.
echo 🔧 Setting up project Python environment...
pyenv local 3.12.10
if %errorlevel% neq 0 (
    echo ❌ Failed to set local Python version
    pause
    exit /b 1
)

echo ✅ Python 3.12.10 set as local version for this project

REM Verify Python installation
echo.
echo 🔍 Verifying Python installation...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python is not accessible
    echo 💡 You may need to restart your command prompt after pyenv installation
    pause
    exit /b 1
)

REM Upgrade pip
echo.
echo 📦 Upgrading pip...
python -m pip install --upgrade pip --user
if %errorlevel% neq 0 (
    echo ⚠️  Pip upgrade failed, trying without --user flag...
    python -m pip install --upgrade pip
    if %errorlevel% neq 0 (
        echo ⚠️  Pip upgrade failed, continuing with existing version...
    )
)

REM Create virtual environment
echo.
echo 🔧 Creating virtual environment 'fabric-cicd-venv'...
python -m venv fabric-cicd-venv
if %errorlevel% neq 0 (
    echo ❌ Failed to create virtual environment
    pause
    exit /b 1
)

echo ✅ Virtual environment created successfully

REM Activate virtual environment
echo.
echo 🔄 Activating virtual environment...
call fabric-cicd-venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ Failed to activate virtual environment
    pause
    exit /b 1
)

echo ✅ Virtual environment activated

REM Upgrade pip in virtual environment
echo.
echo 📦 Upgrading pip in virtual environment...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo ⚠️  Pip upgrade in virtual environment failed, continuing with existing version...
)

REM Install core dependencies
echo.
echo 📦 Installing core dependencies...
echo    - fabric-cicd (latest version)
echo    - azure-identity
echo    - PyYAML
echo    - packaging
echo    - click
echo.

pip install fabric-cicd --upgrade --force-reinstall
if %errorlevel% neq 0 (
    echo ❌ Failed to install fabric-cicd
    pause
    exit /b 1
)

pip install azure-identity PyYAML packaging click
if %errorlevel% neq 0 (
    echo ❌ Failed to install additional dependencies
    pause
    exit /b 1
)

echo ✅ All dependencies installed successfully

REM Verify installation
echo.
echo 🔍 Verifying installation...
python -c "import fabric_cicd; print('✅ fabric-cicd imported successfully')"
if %errorlevel% neq 0 (
    echo ❌ fabric-cicd import failed
    pause
    exit /b 1
)

python -c "import azure.identity; print('✅ azure-identity imported successfully')"
if %errorlevel% neq 0 (
    echo ❌ azure-identity import failed
    pause
    exit /b 1
)

REM Run compatibility check
echo.
echo 🔍 Running compatibility check...
if exist "check_compatibility.py" (
    python check_compatibility.py
) else (
    echo ⚠️  check_compatibility.py not found, skipping compatibility check
)

REM Create activation script for pyenv environment
echo.
echo 📝 Creating activation script...
(
echo @echo off
echo REM Quick activation script for Fabric CICD environment ^(PyEnv^)
echo echo 🔄 Activating Fabric CICD environment ^(PyEnv^)...
echo.
echo REM Set pyenv environment
echo set "PYENV_ROOT=%%USERPROFILE%%\.pyenv"
echo set "PYENV_HOME=%%USERPROFILE%%\.pyenv\pyenv-win"
echo set "PATH=%%PYENV_HOME%%\bin;%%PYENV_HOME%%\shims;%%PATH%%"
echo.
echo REM Activate virtual environment
echo call fabric-cicd-venv\Scripts\activate.bat
echo if %%errorlevel%% neq 0 ^(
echo     echo ❌ Failed to activate virtual environment 'fabric-cicd-venv'
echo     echo 💡 Run setup_pyenv.bat first to create the environment
echo     pause
echo     exit /b 1
echo ^)
echo.
echo echo ✅ Environment activated: fabric-cicd-venv ^(PyEnv^)
echo echo.
echo.
echo REM Run compatibility check
echo echo 🔍 Running compatibility check...
echo if exist "check_compatibility.py" ^(
echo     python check_compatibility.py
echo ^) else ^(
echo     echo ⚠️  check_compatibility.py not found
echo ^)
echo echo.
echo.
echo echo 💡 You can now run: python fabric_deploy.py --help
echo echo.
echo.
echo REM Stay in the activated environment
echo cmd /k
) > activate_fabric_env_pyenv.bat

echo ✅ Created activate_fabric_env_pyenv.bat

REM Setup VS Code settings for pyenv
echo.
echo 🔧 Configuring VS Code settings...
if not exist ".vscode" mkdir .vscode

REM Get the full path to the virtual environment Python
for /f "delims=" %%i in ('cd') do set "CURRENT_DIR=%%i"
set "VENV_PYTHON=%CURRENT_DIR%\fabric-cicd-venv\Scripts\python.exe"

(
echo {
echo     "python.defaultInterpreterPath": "%VENV_PYTHON:\=\\%",
echo     "python.terminal.activateEnvironment": true,
echo     "python.linting.enabled": true,
echo     "python.linting.pylintEnabled": false,
echo     "python.linting.flake8Enabled": true,
echo     "python.formatting.provider": "black",
echo     "python.analysis.autoImportCompletions": true,
echo     "python.analysis.typeCheckingMode": "basic",
echo     "files.associations": {
echo         "*.yml": "yaml",
echo         "*.yaml": "yaml"
echo     },
echo     "yaml.validate": true,
echo     "yaml.completion": true
echo }
) > .vscode\settings.json

echo ✅ VS Code configured for PyEnv environment

REM Success message
echo.
echo 🎉 SETUP COMPLETE!
echo ==================
echo.
echo ✅ Python 3.12.10 installed via pyenv
echo ✅ Virtual environment 'fabric-cicd-venv' created
echo ✅ fabric-cicd and dependencies installed
echo ✅ VS Code configured
echo ✅ Activation script created: activate_fabric_env_pyenv.bat
echo.
echo 📋 NEXT STEPS:
echo 1. Close and reopen your command prompt to ensure PATH changes take effect
echo 2. Run: activate_fabric_env_pyenv.bat
echo 3. Test with: python fabric_deploy.py --help
echo.
echo 💡 IMPORTANT NOTES:
echo - Use 'activate_fabric_env_pyenv.bat' to activate this environment
echo - This uses pyenv + virtual environment instead of conda
echo - Your Python version is managed by pyenv locally in this project
echo - Virtual environment is in the 'fabric-cicd-venv' folder
echo - Installation works without admin permissions (uses user-level installs)
echo.
echo 🔧 If you encounter issues:
echo 1. Restart your command prompt
echo 2. Ensure pyenv is in your PATH
echo 3. Run: pyenv versions (should show 3.12.10)
echo 4. Run: pyenv local 3.12.10
echo.

pause
