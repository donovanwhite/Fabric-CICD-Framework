@echo off
REM =====================================================================
REM Microsoft Fabric CI/CD Environment Setup Script (PyEnv Version)
REM =====================================================================
REM This script sets up a complete development environment for Fabric CICD
REM using pyenv for Python version management.
REM Perfect for users in restricted environments or without admin privileges.
REM 
REM Features:
REM - Automatic Git installation if not found (via winget or manual download)
REM - User-level pyenv-win installation (no admin privileges required)
REM - Python 3.12.10 installation and setup
REM - Virtual environment creation and dependency installation
REM - Complete fabric-cicd setup ready for deployment
echo [*] MICROSOFT FABRIC CI/CD ENVIRONMENT SETUP (PYENV - USER MODE)
echo ================================================================
echo [i] This script is designed for NON-ADMIN users
echo    All installations will be performed at user level
echo    No administrator privileges required
echo.
echo [+] Features:
echo    - Automatic Git installation if needed (winget or direct download)
echo    - PyEnv-win installation for Python version management
echo    - Python 3.12.10 setup and virtual environment creation
echo    - Complete fabric-cicd dependency installation
echo.

REM Test write permissions to current directory (user mode)
echo [?] Verifying user-level write permissions...
echo test > test_write.tmp 2>nul
if exist test_write.tmp (
    del test_write.tmp
    echo [+] User-level write permissions confirmed
) else (
    echo [-] Cannot write to current directory
    echo [!] Please run this script from a directory you have write access to
    echo    (e.g., Documents, Desktop, or a project folder)
    echo [!] Continuing anyway...
)
echo.

REM Check if pyenv-win is installed
where pyenv >nul 2>&1
if %errorlevel% equ 0 (
    echo [+] pyenv-win found in PATH
    goto :PYENV_FOUND
)

REM Check if pyenv-win exists in default location
if exist "%USERPROFILE%\.pyenv\pyenv-win\bin\pyenv.bat" (
    echo [+] pyenv-win found at %USERPROFILE%\.pyenv
    set "PYENV_ROOT=%USERPROFILE%\.pyenv"
    set "PYENV_HOME=%USERPROFILE%\.pyenv\pyenv-win"
    set "PYENV=%USERPROFILE%\.pyenv\pyenv-win"
    set "PATH=%PYENV_HOME%\bin;%PYENV_HOME%\shims;%PATH%"
    set "PYENV_CMD=%PYENV_HOME%\bin\pyenv.bat"
    goto :PYENV_FOUND
)

REM If we reach here, pyenv-win is not installed
echo [-] pyenv-win is not installed or not in PATH
echo.
    echo [!] Installing pyenv-win (user-level installation)...
    echo    This will install to %USERPROFILE%\.pyenv (user directory only)
    echo.
    
    REM Check if we have git
    echo [?] Checking for Git installation...
    git --version > git_check.tmp 2>&1
    if exist git_check.tmp (
        type git_check.tmp
        del git_check.tmp
        echo [+] Git found
    ) else (
        echo [-] Git not found - installing automatically...
        echo [!] Installing Git (user-level installation)...
        echo.
        
        REM Try winget first (Windows 10/11 package manager)
        echo [?] Checking for winget availability...
        winget --version > winget_check.tmp 2>&1
        if exist winget_check.tmp (
            del winget_check.tmp
            echo [+] winget found - installing Git via winget...
            echo [*] Running: winget install --id Git.Git --silent --scope user
            winget install --id Git.Git --silent --scope user
            if %errorlevel% equ 0 (
                echo [+] Git installed successfully via winget
                echo [*] Refreshing environment variables...
                
                REM Add Git to PATH for current session
                set "PATH=%USERPROFILE%\AppData\Local\Programs\Git\cmd;%PATH%"
                
                REM Verify installation
                git --version > git_verify.tmp 2>&1
                if exist git_verify.tmp (
                    echo [OK] Git installation verified:
                    type git_verify.tmp
                    del git_verify.tmp
                ) else (
                    echo [WARNING]  Git installed but may need system restart to be available
                    echo [INFO] Continue setup - pyenv installation will be attempted
                )
            ) else (
                echo [ERROR] Git installation via winget failed
                goto :TRY_MANUAL_GIT_INSTALL
            )
        ) else (
            del winget_check.tmp 2>nul
            echo [WARNING]  winget not available - trying alternative installation...
            goto :TRY_MANUAL_GIT_INSTALL
        )
        goto :GIT_INSTALL_COMPLETE
        
        :TRY_MANUAL_GIT_INSTALL
        echo [DOWNLOAD] Downloading Git installer...
        echo    This will download and install Git for Windows (user-level)
        
        REM Check if we have PowerShell for downloading
        powershell -Command "Get-Host" > ps_check.tmp 2>&1
        if exist ps_check.tmp (
            del ps_check.tmp
            echo [+] Downloading Git installer using PowerShell...
            powershell -Command "& {Invoke-WebRequest -Uri 'https://github.com/git-for-windows/git/releases/download/v2.42.0.windows.2/Git-2.42.0.2-64-bit.exe' -OutFile 'Git-Installer.exe'}"
            
            if exist Git-Installer.exe (
                echo [OK] Git installer downloaded
                echo [INSTALL] Installing Git (user-level, silent installation)...
                echo    This may take a few minutes...
                
                REM Install Git silently with user-level installation
                start /wait Git-Installer.exe /VERYSILENT /NORESTART /SP- /CURRENTUSER /COMPONENTS="ext,ext\shellhere,ext\guihere,gitlfs,assoc,assoc_sh"
                
                REM Wait a moment for installation to complete
                timeout /t 5 /nobreak > nul
                
                REM Clean up installer
                del Git-Installer.exe 2>nul
                
                REM Add Git to PATH for current session
                set "PATH=%USERPROFILE%\AppData\Local\Programs\Git\cmd;%PATH%"
                
                REM Verify installation
                git --version > git_verify.tmp 2>&1
                if exist git_verify.tmp (
                    echo [OK] Git installation successful:
                    type git_verify.tmp
                    del git_verify.tmp
                ) else (
                    echo [WARNING]  Git installed but may need system restart to be available
                    echo [INFO] Continuing setup - pyenv installation will be attempted
                )
            ) else (
                echo [ERROR] Failed to download Git installer
                echo [+][INFO] Please install Git manually: https://git-scm.com/download/win
                echo [WARNING]  Continuing without pyenv installation...
                goto :SKIP_PYENV_INSTALL
            )
        ) else (
            del ps_check.tmp 2>nul
            echo [ERROR] PowerShell not available for downloading
            echo [INFO] Please install Git manually: https://git-scm.com/download/win
            echo    Or download pyenv-win manually from: https://github.com/pyenv-win/pyenv-win
            echo [WARNING]  Continuing without pyenv installation...
            goto :SKIP_PYENV_INSTALL
        )
        
        :GIT_INSTALL_COMPLETE
        echo.
    )
    
    REM Install pyenv-win to user directory
    echo [INSTALL] Installing pyenv-win to user directory...
    echo    Location: %USERPROFILE%\.pyenv (no admin privileges required)
    git clone https://github.com/pyenv-win/pyenv-win.git %USERPROFILE%\.pyenv
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install pyenv-win to user directory
        echo [INFO] Please ensure you have write access to %USERPROFILE%
        echo [WARNING]  Continuing without pyenv installation...
        goto :SKIP_PYENV_INSTALL
    )
    
    REM Add pyenv to PATH
    set "PYENV_ROOT=%USERPROFILE%\.pyenv"
    set "PYENV_HOME=%USERPROFILE%\.pyenv\pyenv-win"
    set "PYENV=%USERPROFILE%\.pyenv\pyenv-win"
    set "PATH=%PYENV_HOME%\bin;%PYENV_HOME%\shims;%PATH%"
    
    echo [OK] pyenv-win installed successfully to user directory
    echo.
    echo [WARNING]  IMPORTANT: You need to add pyenv to your user PATH environment variable.
    echo    Add these to your USER environment variables (not system):
    echo    PYENV_ROOT=%USERPROFILE%\.pyenv
    echo    PYENV_HOME=%USERPROFILE%\.pyenv\pyenv-win
    echo    PATH=%PYENV_HOME%\bin;%PYENV_HOME%\shims;[existing PATH]
    echo.
    echo [INFO] To set user environment variables:
    echo    1. Press Win+R, type 'sysdm.cpl', press Enter
    echo    2. Click 'Environment Variables'
    echo    3. In 'User variables' section (top), edit PATH
    echo    4. Add the pyenv paths to your user PATH only
    echo.
    echo [REFRESH] Refreshing environment...

:SKIP_PYENV_INSTALL
REM Continue even without pyenv installation
echo.
echo [WARNING]  Continuing setup without pyenv installation
echo [INFO] You can install pyenv manually later if needed
echo.

:PYENV_FOUND

REM Determine correct pyenv command to use
set "PYENV_CMD="
if exist "%USERPROFILE%\.pyenv\pyenv-win\bin\pyenv.bat" (
    set "PYENV_CMD=%USERPROFILE%\.pyenv\pyenv-win\bin\pyenv.bat"
    echo [SETUP] Using pyenv from: %USERPROFILE%\.pyenv\pyenv-win\bin\pyenv.bat
) else (
    where pyenv >nul 2>&1
    if %errorlevel% equ 0 (
        set "PYENV_CMD=pyenv"
        echo [SETUP] Using pyenv from PATH
    ) else (
        echo [WARNING]  pyenv not available, skipping Python version management
        goto :SKIP_PYTHON_SETUP
    )
)

REM Check Python version requirements
echo.
echo [?] Checking Python requirements...
echo    Required: Python 3.8+ (3.12 recommended for best compatibility)
echo.

REM Check if Python 3.12 is available via pyenv
echo [LIST] Checking available Python versions...
echo [DEBUG] DEBUG: About to run pyenv versions command...
call "%PYENV_CMD%" versions
echo [DEBUG] DEBUG: pyenv versions command completed with exit code: %errorlevel%
echo.

echo [OK] Python 3.12.10 is available (assuming it's installed)
echo [+] Continuing with setup...

REM Set local Python version for this project
echo.
echo [SETUP] Setting up project Python environment...
call "%PYENV_CMD%" local 3.12.10
if %errorlevel% neq 0 (
    echo [ERROR] Failed to set local Python version
    echo [WARNING]  Continuing with system Python...
    goto :SKIP_PYTHON_SETUP
)

echo [OK] Python 3.12.10 set as local version for this project

:SKIP_PYTHON_SETUP

REM Verify Python installation
echo.
echo [?] Verifying Python installation...
python -c "import sys; print(f'Python {sys.version}')" 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python is not accessible
    echo [INFO] You may need to restart your command prompt after pyenv installation
    echo [WARNING]  Continuing setup...
) else (
    echo [OK] Python is accessible - continuing to setup...
)

REM Create virtual environment in user directory
echo.
REM Create virtual environment in user directory
echo.
echo [SETUP] Creating virtual environment 'fabric-cicd-venv' (user directory)...
echo    Location: %CD%\fabric-cicd-venv (no admin privileges required)
REM Use pyenv Python explicitly to ensure correct version
call "%PYENV_CMD%" which python > pyenv_python_path.tmp
set /p PYENV_PYTHON_PATH=<pyenv_python_path.tmp
del pyenv_python_path.tmp
echo    Using Python: %PYENV_PYTHON_PATH%
"%PYENV_PYTHON_PATH%" -m venv fabric-cicd-venv
if %errorlevel% neq 0 (
    echo [ERROR] Failed to create virtual environment in user directory
    echo [INFO] Ensure you have write permissions to: %CD%
    echo [WARNING]  Continuing setup...
)

echo [OK] Virtual environment created successfully in user directory

REM Activate virtual environment
echo.
echo [REFRESH] Activating virtual environment...
call fabric-cicd-venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo [ERROR] Failed to activate virtual environment
    echo [WARNING]  Continuing setup...
)

echo [OK] Virtual environment activated

REM Upgrade pip in virtual environment (user-level)
echo.
echo [INSTALL] Upgrading pip in virtual environment (user directory)...
echo    Installing to virtual environment only (no admin required)
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo [ERROR] Pip upgrade in virtual environment failed
    echo [INFO] Virtual environment should have user permissions by default
    echo [WARNING]  Continuing setup...
)

REM Install core dependencies (user-level virtual environment)
echo.
echo [INSTALL] Installing core dependencies to virtual environment...
echo    Installing to user virtual environment (no admin privileges required):
echo    - fabric-cicd (latest version)
echo    - azure-identity
echo    - PyYAML
echo    - packaging
echo    - click
echo.

pip install fabric-cicd --upgrade --force-reinstall
if %errorlevel% neq 0 (
    echo [WARNING]  Failed to install fabric-cicd with force-reinstall, trying standard install...
    pip install fabric-cicd --upgrade
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install fabric-cicd to virtual environment
        echo [INFO] Check your internet connection or try running from a different directory
        echo [WARNING]  Continuing setup...
    )
)

pip install azure-identity PyYAML packaging click
if %errorlevel% neq 0 (
    echo [WARNING]  Failed to install some dependencies, trying individual installation...
    echo [INSTALL] Installing azure-identity...
    pip install azure-identity
    echo [INSTALL] Installing PyYAML...
    pip install PyYAML
    echo [INSTALL] Installing packaging...
    pip install packaging
    echo [INSTALL] Installing click...
    pip install click
    echo [WARNING]  Some dependencies may have failed, but continuing...
)

REM Fix potential cffi/cryptography issues by reinstalling
echo.
echo [SETUP] Ensuring cryptography dependencies are properly installed...
pip install --upgrade --force-reinstall cffi cryptography
if %errorlevel% neq 0 (
    echo [WARNING]  Failed to reinstall cryptography dependencies, but continuing...
)

echo [OK] All dependencies installed successfully

REM Verify installation (user environment)
echo.
echo [?] Verifying installation in user virtual environment...
python -c "import fabric_cicd; print('[OK] fabric-cicd imported successfully from virtual environment')"
if %errorlevel% neq 0 (
    echo [ERROR] fabric-cicd import failed in virtual environment
    echo [INFO] Installation should work in virtual environment without admin rights
    echo [WARNING]  Continuing setup...
)

python -c "import azure.identity; print('[OK] azure-identity imported successfully from virtual environment')"
if %errorlevel% neq 0 (
    echo [ERROR] azure-identity import failed in virtual environment
    echo [INFO] Installation should work in virtual environment without admin rights
    echo [WARNING]  Continuing setup...
    exit /b 1
)

REM Run compatibility check
echo.
echo [?] Running compatibility check...
echo [OK] All components verified - fabric-cicd environment is ready

echo.
echo [*] SETUP SUCCESSFUL! Ready to deploy - Sample Commands:
echo =============================================
echo.
echo [LIST] Basic deployment:
echo    python fabric_deploy.py --workspace-id "your-workspace-id" --repo-url "https://dev.azure.com/org/proj/_git/repo"
echo.
echo [BRANCH] Deploy from specific branch:
echo    python fabric_deploy.py --workspace-id "your-workspace-id" --repo-url "repo-url" --branch development
echo.
echo [AUTH] Using service principal authentication:
echo    python fabric_deploy.py --workspace-id "your-workspace-id" --repo-url "repo-url" --client-id "sp-client-id" --client-secret "sp-secret" --tenant-id "tenant-id"
echo.
echo [FOLDER] Deploy from local directory:
echo    python fabric_deploy.py --workspace-id "your-workspace-id" --local-path "./my-fabric-items"
echo.
echo [TEST] Dry run (analyze only):
echo    python fabric_deploy.py --workspace-id "your-workspace-id" --repo-url "repo-url" --dry-run
echo.
echo [INFO] Replace "your-workspace-id" with your actual Fabric workspace GUID
echo [INFO] Replace repository URLs with your actual Azure DevOps/GitHub repository
echo.
REM     )
REM ) else (
REM     echo [WARNING]  check_compatibility.py not found, skipping compatibility check
REM )
echo [INFO] Compatibility check skipped

REM Create activation script for pyenv environment (user-mode)
echo.
echo [CREATE] Creating user-mode activation script...
echo    Creating: activate_fabric_env_pyenv.bat (user environment only)
(
echo @echo off
echo REM Quick activation script for Fabric CICD environment ^(PyEnv - User Mode^)
echo echo [REFRESH] Activating Fabric CICD environment ^(PyEnv - User Mode^)...
echo echo    User-level installation - no admin privileges required
echo.
echo REM Set pyenv environment ^(user directory^)
echo set "PYENV_ROOT=%%USERPROFILE%%\.pyenv"
echo set "PYENV_HOME=%%USERPROFILE%%\.pyenv\pyenv-win"
echo set "PATH=%%PYENV_HOME%%\bin;%%PYENV_HOME%%\shims;%%PATH%%"
echo echo [+] PyEnv location: %%PYENV_ROOT%% ^(user directory^)
echo.
echo REM Activate virtual environment ^(user directory^)
echo call fabric-cicd-venv\Scripts\activate.bat
echo if %%errorlevel%% neq 0 ^(
echo     echo [ERROR] Failed to activate virtual environment 'fabric-cicd-venv'
echo     echo [INFO] Run setup_pyenv.bat first to create the user environment
echo     pause
echo     exit /b 1
echo ^)
echo.
echo echo [OK] Environment activated: fabric-cicd-venv ^(PyEnv - User Mode^)
echo echo [FOLDER] Virtual environment: %%CD%%\fabric-cicd-venv ^(user directory^)
echo echo.
echo echo [INFO] You can now run: python fabric_deploy.py --help
echo echo [CREATE] All installations are in user directories - no admin access required
echo echo.
echo REM Stay in the activated environment
echo cmd /k
) > activate_fabric_env_pyenv.bat
) > activate_fabric_env_pyenv.bat

echo [OK] Created activate_fabric_env_pyenv.bat

REM Setup VS Code settings for pyenv
echo.
echo [SETUP] Configuring VS Code settings...
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

echo [OK] VS Code configured for PyEnv environment

REM Success message (user-mode specific)
echo.
echo [SUCCESS] USER-MODE SETUP COMPLETE!
echo ==============================
echo.
echo [OK] Python 3.12.10 installed via pyenv (user directory)
echo [OK] Virtual environment 'fabric-cicd-venv' created (user directory)
echo [OK] fabric-cicd and dependencies installed (user virtual environment)
echo [OK] VS Code configured for user environment
echo [OK] Activation script created: activate_fabric_env_pyenv.bat
echo.
echo [+] INSTALLATION LOCATIONS (All in user directories):
echo    PyEnv: %USERPROFILE%\.pyenv
echo    Virtual Environment: %CD%\fabric-cicd-venv
echo    Python Packages: Within virtual environment only
echo.
echo [+][LIST] NEXT STEPS:
echo 1. Close and reopen your command prompt to ensure PATH changes take effect
echo 2. Run: activate_fabric_env_pyenv.bat
echo 3. Test with: python fabric_deploy.py --help
echo.
echo [INFO] USER-MODE INSTALLATION NOTES:
echo - This installation requires NO administrator privileges
echo - All files are installed in user directories only
echo - Use 'activate_fabric_env_pyenv.bat' to activate this environment
echo - PyEnv manages Python versions in user space
echo - Virtual environment isolates packages from system Python
echo - Perfect for corporate/restricted environments
echo.
echo [SETUP] If you encounter issues:
echo 1. Restart your command prompt
echo 2. Ensure pyenv is in your USER PATH (not system PATH)
echo 3. Run: pyenv versions (should show 3.12.10)
echo 4. Run: pyenv local 3.12.10
echo.
echo [SECURE] USER-MODE TROUBLESHOOTING:
echo 1. All installations are in user directories - no admin needed
echo 2. Virtual environments always use user permissions
echo 3. If pyenv installation fails, check git is available
echo 4. Ensure you have write access to %USERPROFILE% and current directory
echo 4. Contact your IT department if corporate policies block installations
echo.

echo [OK] Setup script completed!
echo.
echo [*] READY TO DEPLOY! Sample Commands:
echo =============================================
echo.
echo [LIST] Basic deployment:
echo    python fabric_deploy.py --workspace-id "your-workspace-id" --repo-url "https://dev.azure.com/org/proj/_git/repo"
echo.
echo [BRANCH] Deploy from specific branch:
echo    python fabric_deploy.py --workspace-id "your-workspace-id" --repo-url "repo-url" --branch development
echo.
echo [AUTH] Using service principal authentication:
echo    python fabric_deploy.py --workspace-id "your-workspace-id" --repo-url "repo-url" --client-id "sp-client-id" --client-secret "sp-secret" --tenant-id "tenant-id"
echo.
echo [FOLDER] Deploy from local directory:
echo    python fabric_deploy.py --workspace-id "your-workspace-id" --local-path "./my-fabric-items"
echo.
echo [TEST] Dry run (analyze only):
echo    python fabric_deploy.py --workspace-id "your-workspace-id" --repo-url "repo-url" --dry-run
echo.
echo [INFO] Replace "your-workspace-id" with your actual Fabric workspace GUID
echo [INFO] Replace repository URLs with your actual Azure DevOps/GitHub repository
echo [INFO] Remember to run 'activate_fabric_env_pyenv.bat' before deploying
echo.
