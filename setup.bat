@echo off
REM =====================================================================
REM Microsoft Fabric CI/CD Environment Setup Script
REM =====================================================================
REM This script sets up a complete development environment for Fabric CICD
REM including conda environment, dependencies, and VS Code configuration.

echo.
echo 🚀 MICROSOFT FABRIC CI/CD ENVIRONMENT SETUP
echo ============================================
echo.

REM Check if conda is available
where conda >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Conda not found in PATH
    echo 💡 Please install Anaconda or Miniconda first:
    echo    https://docs.anaconda.com/miniconda/
    pause
    exit /b 1
)

echo ✅ Conda found in PATH
conda --version

REM Check if Python 3.12 is available
echo.
echo 🔍 Checking Python availability...
conda search python=3.12* -c conda-forge >nul 2>&1
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
conda info --envs | findstr "%ENV_NAME%" >nul 2>&1
if %errorlevel% equ 0 (
    echo ⚠️  Environment '%ENV_NAME%' already exists
    echo.
    set /p "RECREATE=Do you want to recreate it? This will delete the existing environment (y/N): "
    if /i "!RECREATE!"=="y" (
        echo 🗑️  Removing existing environment...
        conda env remove -n %ENV_NAME% -y
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
conda create -n %ENV_NAME% python=%PYTHON_VERSION% -y
if %errorlevel% neq 0 (
    echo ❌ Failed to create conda environment
    pause
    exit /b 1
)

echo ✅ Conda environment created successfully

:ACTIVATE_ENV
echo.
echo 🔄 Activating environment...
call conda activate %ENV_NAME%
if %errorlevel% neq 0 (
    echo ❌ Failed to activate conda environment
    echo 💡 Try running: conda activate %ENV_NAME%
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

REM Verify fabric-cicd version
echo.
echo 🔍 Verifying fabric-cicd version...
python -c "import fabric_cicd; from packaging import version; required = '0.1.24'; current = fabric_cicd.__version__; exit(0 if version.parse(current) >= version.parse(required) else 1)" 2>nul
if %errorlevel% neq 0 (
    echo ❌ fabric-cicd version incompatible or not installed properly
    echo 💡 This framework requires fabric-cicd version 0.1.24 or higher
    echo 🔧 Installing/upgrading to latest fabric-cicd...
    pip install --upgrade fabric-cicd
    if %errorlevel% neq 0 (
        echo ❌ Failed to upgrade fabric-cicd
        pause
        exit /b 1
    )
    REM Verify again after upgrade
    python -c "import fabric_cicd; from packaging import version; required = '0.1.24'; current = fabric_cicd.__version__; exit(0 if version.parse(current) >= version.parse(required) else 1)" 2>nul
    if %errorlevel% neq 0 (
        echo ❌ fabric-cicd version still incompatible after upgrade
        python -c "import fabric_cicd; print(f'Current version: {fabric_cicd.__version__}')" 2>nul
        echo 💡 Required version: 0.1.24 or higher
        pause
        exit /b 1
    )
)

python -c "import fabric_cicd; print(f'✅ fabric-cicd version compatible: {fabric_cicd.__version__}')"

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
echo     "python.pythonPath": "conda run -n %ENV_NAME% python",
echo     "python.terminal.activateEnvironment": true,
echo     "python.terminal.activateEnvInCurrentTerminal": true,
echo     "python.condaPath": "conda",
echo     "python.defaultInterpreterPath": "conda run -n %ENV_NAME% python",
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
echo             "args": ["/k", "conda activate %ENV_NAME%"],
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
echo call conda activate %ENV_NAME%
echo echo ✅ Environment activated: %ENV_NAME%
echo echo 💡 You can now run: python fabric_deploy.py --help
echo echo.
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
