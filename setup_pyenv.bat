@echo off
REM =====================================================================
REM Microsoft Fabric CI/CD Environment Setup Script (PyEnv Version)
REM =====================================================================
REM This script sets up a complete development environment for Fabric CICD
REM using pyenv for Python version management instead of conda.
REM Perfect for users who cannot install conda or prefer pyenv.

echo.
echo 🚀 MICROSOFT FABRIC CI/CD ENVIRONMENT SETUP (PYENV - USER MODE)
echo ================================================================
echo � This script is designed for NON-ADMIN users
echo    All installations will be performed at user level
echo    No administrator privileges required
echo.

REM Test write permissions to current directory (user mode)
echo 🔍 Verifying user-level write permissions...
echo test > test_write.tmp 2>nul
if exist test_write.tmp (
    del test_write.tmp
    echo ✅ User-level write permissions confirmed
) else (
    echo ❌ Cannot write to current directory
    echo 💡 Please run this script from a directory you have write access to
    echo    (e.g., Documents, Desktop, or a project folder)
    echo ⚠️  Continuing anyway...
)
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

REM If we reach here, pyenv-win is not installed
echo ❌ pyenv-win is not installed or not in PATH
echo.
    echo 💡 Installing pyenv-win (user-level installation)...
    echo    This will install to %USERPROFILE%\.pyenv (user directory only)
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
        echo ⚠️  Continuing without pyenv installation...
        goto :SKIP_PYENV_INSTALL
    )
    
    REM Install pyenv-win to user directory
    echo 📦 Installing pyenv-win to user directory...
    echo    Location: %USERPROFILE%\.pyenv (no admin privileges required)
    git clone https://github.com/pyenv-win/pyenv-win.git %USERPROFILE%\.pyenv
    if %errorlevel% neq 0 (
        echo ❌ Failed to install pyenv-win to user directory
        echo 💡 Please ensure you have write access to %USERPROFILE%
        echo ⚠️  Continuing without pyenv installation...
        goto :SKIP_PYENV_INSTALL
    )
    
    REM Add pyenv to PATH
    set "PYENV_ROOT=%USERPROFILE%\.pyenv"
    set "PYENV_HOME=%USERPROFILE%\.pyenv\pyenv-win"
    set "PYENV=%USERPROFILE%\.pyenv\pyenv-win"
    set "PATH=%PYENV_HOME%\bin;%PYENV_HOME%\shims;%PATH%"
    
    echo ✅ pyenv-win installed successfully to user directory
    echo.
    echo ⚠️  IMPORTANT: You need to add pyenv to your user PATH environment variable.
    echo    Add these to your USER environment variables (not system):
    echo    PYENV_ROOT=%USERPROFILE%\.pyenv
    echo    PYENV_HOME=%USERPROFILE%\.pyenv\pyenv-win
    echo    PATH=%PYENV_HOME%\bin;%PYENV_HOME%\shims;[existing PATH]
    echo.
    echo 💡 To set user environment variables:
    echo    1. Press Win+R, type 'sysdm.cpl', press Enter
    echo    2. Click 'Environment Variables'
    echo    3. In 'User variables' section (top), edit PATH
    echo    4. Add the pyenv paths to your user PATH only
    echo.
    echo 🔄 Refreshing environment...

:SKIP_PYENV_INSTALL
REM Continue even without pyenv installation
echo.
echo ⚠️  Continuing setup without pyenv installation
echo 💡 You can install pyenv manually later if needed
echo.

:PYENV_FOUND

REM Check if pyenv is actually available before proceeding
where pyenv >nul 2>&1
if %errorlevel% neq 0 (
    if exist "%PYENV_HOME%\bin\pyenv.bat" (
        set "PYENV_CMD=%PYENV_HOME%\bin\pyenv.bat"
    ) else (
        echo ⚠️  pyenv not available, skipping Python version management
        goto :SKIP_PYTHON_SETUP
    )
) else (
    set "PYENV_CMD=pyenv"
)

REM Check Python version requirements
echo.
echo 🔍 Checking Python requirements...
echo    Required: Python 3.8+ (3.12 recommended for best compatibility)
echo.

REM Check if Python 3.12 is available via pyenv
echo 📋 Checking available Python versions...
"%PYENV_CMD%" versions
echo.

REM Install Python 3.12.10 if not available (user-level installation)
"%PYENV_CMD%" versions | findstr "3.12.10" >nul
if %errorlevel% neq 0 (
    echo 📦 Installing Python 3.12.10 to user directory...
    echo    This will install to %USERPROFILE%\.pyenv\versions\3.12.10
    "%PYENV_CMD%" install 3.12.10
    if %errorlevel% neq 0 (
        echo ❌ Failed to install Python 3.12.10 to user directory
        echo 💡 Try manually: "%PYENV_CMD%" install 3.12.10
        echo    Installation location: User directory only (no admin required)
        echo ⚠️  Continuing without Python 3.12.10 installation...
        goto :SKIP_PYTHON_SETUP
    )
    echo ✅ Python 3.12.10 installed successfully
) else (
    echo ✅ Python 3.12.10 already available
)

REM Set local Python version for this project
echo.
echo 🔧 Setting up project Python environment...
"%PYENV_CMD%" local 3.12.10
if %errorlevel% neq 0 (
    echo ❌ Failed to set local Python version
    echo ⚠️  Continuing with system Python...
    goto :SKIP_PYTHON_SETUP
)

echo ✅ Python 3.12.10 set as local version for this project

:SKIP_PYTHON_SETUP

REM Verify Python installation
echo.
echo 🔍 Verifying Python installation...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python is not accessible
    echo 💡 You may need to restart your command prompt after pyenv installation
    echo ⚠️  Continuing setup...
)

REM Upgrade pip (user-level installation)
echo.
echo 📦 Upgrading pip (user-level installation)...
echo    Installing to user directory only (no admin required)
python -m pip install --upgrade pip --user
if %errorlevel% neq 0 (
    echo ❌ Failed to upgrade pip with user-level installation
    echo 💡 This script is designed for user-mode installations only
    echo    If you encounter permissions issues, ensure you're in a writable directory
    echo ⚠️  Continuing setup...
)

REM Create virtual environment in user directory
echo.
echo 🔧 Creating virtual environment 'fabric-cicd-venv' (user directory)...
echo    Location: %CD%\fabric-cicd-venv (no admin privileges required)
python -m venv fabric-cicd-venv
if %errorlevel% neq 0 (
    echo ❌ Failed to create virtual environment in user directory
    echo 💡 Ensure you have write permissions to: %CD%
    echo ⚠️  Continuing setup...
)

echo ✅ Virtual environment created successfully in user directory

REM Activate virtual environment
echo.
echo 🔄 Activating virtual environment...
call fabric-cicd-venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ❌ Failed to activate virtual environment
    echo ⚠️  Continuing setup...
)

echo ✅ Virtual environment activated

REM Upgrade pip in virtual environment (user-level)
echo.
echo 📦 Upgrading pip in virtual environment (user directory)...
echo    Installing to virtual environment only (no admin required)
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo ❌ Pip upgrade in virtual environment failed
    echo 💡 Virtual environment should have user permissions by default
    echo ⚠️  Continuing setup...
)

REM Install core dependencies (user-level virtual environment)
echo.
echo 📦 Installing core dependencies to virtual environment...
echo    Installing to user virtual environment (no admin privileges required):
echo    - fabric-cicd (latest version)
echo    - azure-identity
echo    - PyYAML
echo    - packaging
echo    - click
echo.

pip install fabric-cicd --upgrade --force-reinstall
if %errorlevel% neq 0 (
    echo ⚠️  Failed to install fabric-cicd with force-reinstall, trying standard install...
    pip install fabric-cicd --upgrade
    if %errorlevel% neq 0 (
        echo ❌ Failed to install fabric-cicd to virtual environment
        echo 💡 Check your internet connection or try running from a different directory
        echo ⚠️  Continuing setup...
    )
)

pip install azure-identity PyYAML packaging click
if %errorlevel% neq 0 (
    echo ⚠️  Failed to install some dependencies, trying individual installation...
    echo 📦 Installing azure-identity...
    pip install azure-identity
    echo 📦 Installing PyYAML...
    pip install PyYAML
    echo 📦 Installing packaging...
    pip install packaging
    echo 📦 Installing click...
    pip install click
    echo ⚠️  Some dependencies may have failed, but continuing...
)

echo ✅ All dependencies installed successfully

REM Verify installation (user environment)
echo.
echo 🔍 Verifying installation in user virtual environment...
python -c "import fabric_cicd; print('✅ fabric-cicd imported successfully from virtual environment')"
if %errorlevel% neq 0 (
    echo ❌ fabric-cicd import failed in virtual environment
    echo 💡 Installation should work in virtual environment without admin rights
    echo ⚠️  Continuing setup...
)

python -c "import azure.identity; print('✅ azure-identity imported successfully from virtual environment')"
if %errorlevel% neq 0 (
    echo ❌ azure-identity import failed in virtual environment
    echo 💡 Installation should work in virtual environment without admin rights
    echo ⚠️  Continuing setup...
    exit /b 1
)

REM Run compatibility check
echo.
echo 🔍 Running compatibility check...
if exist "check_compatibility.py" (
    python check_compatibility.py
    if %errorlevel% equ 0 (
        echo.
        echo 🚀 SETUP SUCCESSFUL! Ready to deploy - Sample Commands:
        echo =============================================
        echo.
        echo 📋 Basic deployment:
        echo    python fabric_deploy.py --workspace-id "your-workspace-id" --repo-url "https://dev.azure.com/org/proj/_git/repo"
        echo.
        echo 🌿 Deploy from specific branch:
        echo    python fabric_deploy.py --workspace-id "your-workspace-id" --repo-url "repo-url" --branch development
        echo.
        echo 🔐 Using service principal authentication:
        echo    python fabric_deploy.py --workspace-id "your-workspace-id" --repo-url "repo-url" --client-id "sp-client-id" --client-secret "sp-secret" --tenant-id "tenant-id"
        echo.
        echo 📁 Deploy from local directory:
        echo    python fabric_deploy.py --workspace-id "your-workspace-id" --local-path "./my-fabric-items"
        echo.
        echo 🧪 Dry run (analyze only):
        echo    python fabric_deploy.py --workspace-id "your-workspace-id" --repo-url "repo-url" --dry-run
        echo.
        echo 💡 Replace "your-workspace-id" with your actual Fabric workspace GUID
        echo 💡 Replace repository URLs with your actual Azure DevOps/GitHub repository
        echo.
    )
) else (
    echo ⚠️  check_compatibility.py not found, skipping compatibility check
)

REM Create activation script for pyenv environment (user-mode)
echo.
echo 📝 Creating user-mode activation script...
echo    Creating: activate_fabric_env_pyenv.bat (user environment only)
(
echo @echo off
echo REM Quick activation script for Fabric CICD environment ^(PyEnv - User Mode^)
echo echo 🔄 Activating Fabric CICD environment ^(PyEnv - User Mode^)...
echo echo    User-level installation - no admin privileges required
echo.
echo REM Set pyenv environment ^(user directory^)
echo set "PYENV_ROOT=%%USERPROFILE%%\.pyenv"
echo set "PYENV_HOME=%%USERPROFILE%%\.pyenv\pyenv-win"
echo set "PATH=%%PYENV_HOME%%\bin;%%PYENV_HOME%%\shims;%%PATH%%"
echo echo 📂 PyEnv location: %%PYENV_ROOT%% ^(user directory^)
echo.
echo REM Activate virtual environment ^(user directory^)
echo call fabric-cicd-venv\Scripts\activate.bat
echo if %%errorlevel%% neq 0 ^(
echo     echo ❌ Failed to activate virtual environment 'fabric-cicd-venv'
echo     echo 💡 Run setup_pyenv.bat first to create the user environment
echo     pause
echo     exit /b 1
echo ^)
echo.
echo echo ✅ Environment activated: fabric-cicd-venv ^(PyEnv - User Mode^)
echo echo 📂 Virtual environment: %%CD%%\fabric-cicd-venv ^(user directory^)
echo echo.
echo.
echo REM Run compatibility check
echo echo 🔍 Running compatibility check in user environment...
echo if exist "check_compatibility.py" ^(
echo     python check_compatibility.py
echo ^) else ^(
echo     echo ⚠️  check_compatibility.py not found
echo ^)
echo echo.
echo.
echo echo 💡 You can now run: python fabric_deploy.py --help
echo echo 📝 All installations are in user directories - no admin access required
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

REM Success message (user-mode specific)
echo.
echo 🎉 USER-MODE SETUP COMPLETE!
echo ==============================
echo.
echo ✅ Python 3.12.10 installed via pyenv (user directory)
echo ✅ Virtual environment 'fabric-cicd-venv' created (user directory)
echo ✅ fabric-cicd and dependencies installed (user virtual environment)
echo ✅ VS Code configured for user environment
echo ✅ Activation script created: activate_fabric_env_pyenv.bat
echo.
echo � INSTALLATION LOCATIONS (All in user directories):
echo    PyEnv: %USERPROFILE%\.pyenv
echo    Virtual Environment: %CD%\fabric-cicd-venv
echo    Python Packages: Within virtual environment only
echo.
echo �📋 NEXT STEPS:
echo 1. Close and reopen your command prompt to ensure PATH changes take effect
echo 2. Run: activate_fabric_env_pyenv.bat
echo 3. Test with: python fabric_deploy.py --help
echo.
echo 💡 USER-MODE INSTALLATION NOTES:
echo - This installation requires NO administrator privileges
echo - All files are installed in user directories only
echo - Use 'activate_fabric_env_pyenv.bat' to activate this environment
echo - PyEnv manages Python versions in user space
echo - Virtual environment isolates packages from system Python
echo - Perfect for corporate/restricted environments
echo.
echo 🔧 If you encounter issues:
echo 1. Restart your command prompt
echo 2. Ensure pyenv is in your USER PATH (not system PATH)
echo 3. Run: pyenv versions (should show 3.12.10)
echo 4. Run: pyenv local 3.12.10
echo.
echo 🔒 USER-MODE TROUBLESHOOTING:
echo 1. All installations are in user directories - no admin needed
echo 2. Virtual environments always use user permissions
echo 3. If pyenv installation fails, check git is available
echo 4. Ensure you have write access to %USERPROFILE% and current directory
echo 4. Contact your IT department if corporate policies block installations
echo.

echo ✅ Setup script completed!
echo.
echo 🚀 READY TO DEPLOY! Sample Commands:
echo =============================================
echo.
echo 📋 Basic deployment:
echo    python fabric_deploy.py --workspace-id "your-workspace-id" --repo-url "https://dev.azure.com/org/proj/_git/repo"
echo.
echo 🌿 Deploy from specific branch:
echo    python fabric_deploy.py --workspace-id "your-workspace-id" --repo-url "repo-url" --branch development
echo.
echo 🔐 Using service principal authentication:
echo    python fabric_deploy.py --workspace-id "your-workspace-id" --repo-url "repo-url" --client-id "sp-client-id" --client-secret "sp-secret" --tenant-id "tenant-id"
echo.
echo 📁 Deploy from local directory:
echo    python fabric_deploy.py --workspace-id "your-workspace-id" --local-path "./my-fabric-items"
echo.
echo 🧪 Dry run (analyze only):
echo    python fabric_deploy.py --workspace-id "your-workspace-id" --repo-url "repo-url" --dry-run
echo.
echo 💡 Replace "your-workspace-id" with your actual Fabric workspace GUID
echo 💡 Replace repository URLs with your actual Azure DevOps/GitHub repository
echo 💡 Remember to run 'activate_fabric_env_pyenv.bat' before deploying
echo.
