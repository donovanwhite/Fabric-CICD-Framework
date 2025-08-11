@echo off
REM =====================================================================
REM Microsoft Fabric CI/CD Environment Setup Script (CONDA - ADMIN REQUIRED)
REM =====================================================================
REM This script sets up a complete development environment for Fabric CICD
REM including conda environment, dependencies, and VS Code configuration.
REM 
REM ⚠️  ADMIN PRIVILEGES REQUIRED ⚠️
REM This script requires administrator privileges to:
REM - Install conda/miniconda system-wide
REM - Configure system PATH variables
REM - Install dependencies at system level
REM 
REM For NON-ADMIN users, please use setup_pyenv.bat instead

echo.
echo 🚀 MICROSOFT FABRIC CI/CD ENVIRONMENT SETUP (CONDA - ADMIN MODE)
echo =================================================================
echo ⚠️  ADMIN PRIVILEGES REQUIRED
echo    This script installs conda system-wide and requires administrator access
echo    For non-admin users, please use setup_pyenv.bat instead
echo.

REM Check for administrator privileges
echo 🔐 Checking for administrator privileges...
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ ADMIN PRIVILEGES REQUIRED
    echo.
    echo This script requires administrator privileges to:
    echo - Install conda/miniconda system-wide
    echo - Configure system PATH variables  
    echo - Install dependencies at system level
    echo.
    echo 💡 SOLUTIONS:
    echo    1. Right-click this script and select "Run as administrator"
    echo    2. Use setup_pyenv.bat for user-level installation (no admin required)
    echo.
    pause
    exit /b 1
)
echo ✅ Administrator privileges confirmed
echo.

REM Check if conda is available
where conda >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Conda found in PATH
    set "CONDA_CMD=conda"
    goto :CONDA_FOUND
)

REM If not in PATH, check common installation locations
echo 🔍 Conda not in PATH, checking common installation locations...

if exist "C:\ProgramData\Anaconda3\Scripts\conda.exe" (
    echo ✅ Found Anaconda at C:\ProgramData\Anaconda3
    set "CONDA_CMD=C:\ProgramData\Anaconda3\Scripts\conda.exe"
    set "PATH=C:\ProgramData\Anaconda3\Scripts;C:\ProgramData\Anaconda3\condabin;%PATH%"
    goto :CONDA_FOUND
)

if exist "C:\ProgramData\Miniconda3\Scripts\conda.exe" (
    echo ✅ Found Miniconda at C:\ProgramData\Miniconda3
    set "CONDA_CMD=C:\ProgramData\Miniconda3\Scripts\conda.exe"
    set "PATH=C:\ProgramData\Miniconda3\Scripts;C:\ProgramData\Miniconda3\condabin;%PATH%"
    goto :CONDA_FOUND
)

if exist "%USERPROFILE%\anaconda3\Scripts\conda.exe" (
    echo ✅ Found Anaconda at %USERPROFILE%\anaconda3
    set "CONDA_CMD=%USERPROFILE%\anaconda3\Scripts\conda.exe"
    set "PATH=%USERPROFILE%\anaconda3\Scripts;%USERPROFILE%\anaconda3\condabin;%PATH%"
    goto :CONDA_FOUND
)

if exist "%USERPROFILE%\Anaconda3\Scripts\conda.exe" (
    echo ✅ Found Anaconda at %USERPROFILE%\Anaconda3
    set "CONDA_CMD=%USERPROFILE%\Anaconda3\Scripts\conda.exe"
    set "PATH=%USERPROFILE%\Anaconda3\Scripts;%USERPROFILE%\Anaconda3\condabin;%PATH%"
    goto :CONDA_FOUND
)

if exist "%USERPROFILE%\miniconda3\Scripts\conda.exe" (
    echo ✅ Found Miniconda at %USERPROFILE%\miniconda3
    set "CONDA_CMD=%USERPROFILE%\miniconda3\Scripts\conda.exe"
    set "PATH=%USERPROFILE%\miniconda3\Scripts;%USERPROFILE%\miniconda3\condabin;%PATH%"
    goto :CONDA_FOUND
)

echo ❌ Conda not found in PATH or common locations
echo 💡 Please install Anaconda or Miniconda first:
echo    https://docs.anaconda.com/miniconda/
echo 💡 Or add conda to your PATH environment variable
pause
exit /b 1

:CONDA_FOUND
echo ✅ Using conda at: %CONDA_CMD%
"%CONDA_CMD%" --version

REM Check if Python 3.12 is available
echo.
echo 🔍 Checking Python availability...
"%CONDA_CMD%" search python=3.12* -c conda-forge >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Python 3.12 not available from conda-forge, will use default Python
    set PYTHON_VERSION=3.11
) else (
    set PYTHON_VERSION=3.12
)

echo ✅ Will use Python %PYTHON_VERSION%

REM Set environment name
set ENV_NAME=fabric-cicd

echo.
echo 📦 Setting up conda environment: %ENV_NAME%
echo    Python version: %PYTHON_VERSION%
echo.

REM Check if environment already exists
"%CONDA_CMD%" info --envs | findstr "%ENV_NAME%" >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️  Environment '%ENV_NAME%' already exists
    echo.
    set /p "RECREATE=Do you want to recreate it? This will delete the existing environment (y/N): "
    if /i "!RECREATE!"=="y" (
        echo 🗑️  Removing existing environment...
        "%CONDA_CMD%" env remove -n %ENV_NAME% -y
        if %errorlevel% neq 0 (
            echo ❌ Failed to remove existing environment
            pause
            exit /b 1
        )
    ) else (
        echo ⏭️  Skipping environment creation, will update existing environment
        goto :ACTIVATE_ENV
    )
)

echo 🔨 Creating conda environment...
"%CONDA_CMD%" create -n %ENV_NAME% python=%PYTHON_VERSION% -y
if %errorlevel% neq 0 (
    echo ❌ Failed to create conda environment
    pause
    exit /b 1
)

echo ✅ Conda environment created successfully

:ACTIVATE_ENV
echo.
echo 🔄 Activating environment...

REM Initialize conda for this session if needed
echo 🔧 Initializing conda for current session...
call "%CONDA_CMD%" init cmd.exe --no-user >nul 2>&1

REM Set up conda activation in current session
for /f "tokens=*" %%i in ('"%CONDA_CMD%" info --base') do set CONDA_BASE=%%i
if exist "%CONDA_BASE%\Scripts\activate.bat" (
    call "%CONDA_BASE%\Scripts\activate.bat" %ENV_NAME%
) else (
    REM Alternative activation method
    call "%CONDA_CMD%" activate %ENV_NAME%
)

if %errorlevel% neq 0 (
    echo ❌ Failed to activate conda environment
    echo 💡 Manual activation required. Please run:
    echo    conda activate %ENV_NAME%
    echo    OR
    echo    Open an Anaconda Prompt and run this script again
    pause
    exit /b 1
)

echo ✅ Environment activated: %ENV_NAME%

REM Upgrade pip to latest version
echo.
echo 📦 Upgrading pip...
python -m pip install --upgrade pip
if %errorlevel% neq 0 (
    echo ⚠️  Pip upgrade failed, continuing with current version
)

REM Install requirements
echo.
echo 📥 Installing Python dependencies...
if not exist "requirements.txt" (
    echo ❌ requirements.txt not found in current directory
    echo 💡 Make sure you're running this script from the Fabric CICD directory
    pause
    exit /b 1
)

echo 📋 Installing from requirements.txt...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ❌ Failed to install requirements
    echo 💡 Check the error messages above
    pause
    exit /b 1
)

echo ✅ Dependencies installed successfully

REM Verify Python version compatibility
echo.
echo 🔍 Verifying Python version compatibility...
python -c "import sys; major, minor = sys.version_info[:2]; exit(0 if (major == 3 and minor >= 8) else 1)"
if %errorlevel% neq 0 (
    echo ❌ Python version incompatible
    echo 💡 Fabric CICD requires Python 3.8 or higher
    python --version
    pause
    exit /b 1
)

python -c "import sys; print(f'✅ Python version compatible: {sys.version.split()[0]}')"

REM Install/upgrade fabric-cicd to latest version
echo.
echo � Installing latest fabric-cicd version...
pip install --upgrade fabric-cicd
if %errorlevel% neq 0 (
    echo ❌ Failed to install fabric-cicd
    echo 💡 Check the error messages above
    pause
    exit /b 1
)

REM Verify fabric-cicd installation
echo.
echo 🔍 Verifying fabric-cicd installation...
python -c "import fabric_cicd; print(f'✅ fabric-cicd installed successfully')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ fabric-cicd import failed
    echo 💡 Check the installation error messages above
    pause
    exit /b 1
)

echo ✅ fabric-cicd is ready for use

REM Verify installation
echo.
echo 🔍 Verifying installation...
echo.
echo 📊 Python version:
python --version

echo.
echo 📦 Installed packages:
pip list | findstr /i "fabric-cicd azure-identity pyyaml gitpython"

echo.
echo 🧪 Testing Azure authentication...
python -c "from azure.identity import DefaultAzureCredential; print('✅ Azure identity available')" 2>nul
if %errorlevel% neq 0 (
    echo ❌ Azure identity import failed
    echo 💡 Check the installation error messages above
    pause
    exit /b 1
)

REM Create VS Code workspace settings
echo.
echo 🔧 Configuring VS Code settings...
if not exist ".vscode" mkdir .vscode

echo Creating VS Code settings.json...
(
echo {
echo     "python.pythonPath": "%CONDA_CMD% run -n %ENV_NAME% python",
echo     "python.terminal.activateEnvironment": true,
echo     "python.terminal.activateEnvInCurrentTerminal": true,
echo     "python.condaPath": "%CONDA_CMD%",
echo     "python.defaultInterpreterPath": "%CONDA_CMD% run -n %ENV_NAME% python",
echo     "python.envFile": "${workspaceFolder}/.env",
echo     "files.associations": {
echo         "*.yml": "yaml",
echo         "*.yaml": "yaml"
echo     },
echo     "yaml.schemas": {
echo         "file:///schemas/parameter-schema.json": "parameter*.yml"
echo     },
echo     "terminal.integrated.defaultProfile.windows": "Command Prompt",
echo     "terminal.integrated.profiles.windows": {
echo         "Fabric CICD Environment": {
echo             "path": "cmd.exe",
echo             "args": ["/k", "\"%CONDA_CMD%\" activate %ENV_NAME%"],
echo             "icon": "terminal-cmd"
echo         }
echo     }
echo }
) > .vscode\settings.json

echo ✅ VS Code settings created

REM Create environment activation script
echo.
echo 📝 Creating activation script...
(
echo @echo off
echo REM Quick activation script for Fabric CICD environment
echo echo 🔄 Activating Fabric CICD environment...
echo.
echo REM Initialize conda if needed
echo call "%CONDA_CMD%" init cmd.exe --no-user ^>nul 2^>^&1
echo.
echo REM Activate environment
echo call "%CONDA_CMD%" activate %ENV_NAME%
echo if %%errorlevel%% neq 0 ^(
echo     echo ❌ Failed to activate environment 'fabric-cicd'
echo     echo 💡 Try opening an Anaconda Prompt and running:
echo     echo    conda activate %ENV_NAME%
echo     pause
echo     exit /b 1
echo ^)
echo echo ✅ Environment activated: %ENV_NAME%
echo echo 💡 You can now run: python fabric_deploy.py --help
echo echo.
echo cmd /k
) > activate_fabric_env.bat

echo ✅ Created activate_fabric_env.bat

REM Create .env template if it doesn't exist
if not exist ".env" (
    echo.
    echo 📝 Creating .env template...
    (
    echo # Fabric CICD Environment Variables
    echo # ================================
    echo.
    echo # Azure Authentication ^(if needed^)
    echo # AZURE_CLIENT_ID=your-client-id
    echo # AZURE_CLIENT_SECRET=your-client-secret  
    echo # AZURE_TENANT_ID=your-tenant-id
    echo.
    echo # Default Fabric Workspace
    echo # FABRIC_WORKSPACE_ID=your-default-workspace-id
    echo.
    echo # Repository Settings
    echo # REPO_URL=https://dev.azure.com/org/project/_git/repo
    echo # BRANCH_NAME=main
    ) > .env
    echo ✅ Created .env template
)

echo.
echo 🎉 SETUP COMPLETED SUCCESSFULLY!
echo ================================
echo.
echo 📋 What was configured:
echo    ✅ Conda environment: %ENV_NAME%
echo    ✅ Python %PYTHON_VERSION% with all dependencies
echo    ✅ fabric-cicd library installed and tested
echo    ✅ Azure authentication libraries
echo    ✅ VS Code workspace settings
echo    ✅ Environment activation script
echo.
echo 🚀 Next steps:
echo    1. Close and reopen VS Code to apply settings
echo    2. Use Ctrl+Shift+P ^> "Python: Select Interpreter" 
echo    3. Choose the Fabric CICD environment
echo    4. Test deployment: python fabric_deploy.py --help
echo.
echo 💡 Alternative: Use Anaconda Prompt
echo    • Open "Anaconda Prompt" from Start Menu
echo    • Navigate to: cd "%CD%"
echo    • Activate environment: conda activate %ENV_NAME%
echo    • Run deployment: python fabric_deploy.py --help
echo.
echo 💡 Quick commands:
echo    • Activate environment: activate_fabric_env.bat
echo    • Check compatibility: python check_compatibility.py
echo    • Test setup: python -c "import fabric_cicd; print('Ready!')"
echo    • Run deployment: python fabric_deploy.py --workspace-id ^<id^> --repo-url ^<url^>
echo.

REM Run final compatibility check
echo 🔧 Running final compatibility check...
python check_compatibility.py
if %errorlevel% neq 0 (
    echo.
    echo ⚠️  Compatibility check found some issues
    echo 💡 Review the messages above and fix any problems
    echo 🔄 You can re-run: python check_compatibility.py
    echo.
) else (
    echo.
    echo ✅ All compatibility checks passed!
    echo.
)

REM Keep the window open to show results
echo 🏁 Setup complete! Press any key to exit...
pause >nul
