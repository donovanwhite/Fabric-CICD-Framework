@echo off
REM =============================================================================
REM Microsoft Fabric CICD - Complete Environment Setup
REM =============================================================================
REM This script creates a conda environment, installs dependencies, and configures
REM Azure CLI for Microsoft Fabric CICD deployments.
REM
REM Requirements:
REM - Conda/Miniconda/Anaconda installed
REM - Internet connection for package downloads
REM - Administrator privileges (optional, for Azure CLI install)
REM
REM Usage: setup_fabric_cicd.bat [--skip-azure-cli] [--environment-name fabric-cicd]
REM =============================================================================

setlocal enabledelayedexpansion

REM Parse command line arguments
set "SKIP_AZURE_CLI=false"
set "ENV_NAME=fabric-cicd"
set "PYTHON_VERSION=3.12"

:parse_args
if "%~1"=="" goto :start_setup
if "%~1"=="--skip-azure-cli" (
    set "SKIP_AZURE_CLI=true"
    shift
    goto :parse_args
)
if "%~1"=="--environment-name" (
    set "ENV_NAME=%~2"
    shift
    shift
    goto :parse_args
)
if "%~1"=="--help" (
    goto :show_help
)
shift
goto :parse_args

:show_help
echo.
echo Microsoft Fabric CICD - Complete Environment Setup
echo ===================================================
echo.
echo Usage: %~nx0 [OPTIONS]
echo.
echo Options:
echo   --skip-azure-cli           Skip Azure CLI installation
echo   --environment-name NAME    Custom conda environment name (default: fabric-cicd)
echo   --help                     Show this help message
echo.
echo Examples:
echo   %~nx0                                      # Full setup with default environment
echo   %~nx0 --skip-azure-cli                    # Setup without Azure CLI
echo   %~nx0 --environment-name my-fabric-env    # Custom environment name
echo.
exit /b 0

:start_setup
echo.
echo ========================================
echo Microsoft Fabric CICD - Complete Setup
echo ========================================
echo.
echo 🎯 Environment: %ENV_NAME%
echo 🐍 Python: %PYTHON_VERSION%
echo 🌐 Azure CLI: %SKIP_AZURE_CLI:true=Skip%
echo.

REM =============================================================================
REM STEP 1: DETECT AND CONFIGURE CONDA
REM =============================================================================

echo.
echo 📋 STEP 1: Detecting Conda Installation
echo ========================================

REM Try to find conda in PATH first
echo 🔍 Checking for conda in PATH...
conda --version >nul 2>&1
if %errorlevel%==0 (
    echo ✅ Conda found in PATH
    set "CONDA_CMD=conda"
    goto :conda_ready
)

echo ❌ Conda not found in PATH, searching common locations...

REM Search common installation paths
set "CONDA_PATHS[0]=%USERPROFILE%\anaconda3"
set "CONDA_PATHS[1]=%USERPROFILE%\miniconda3"
set "CONDA_PATHS[2]=C:\ProgramData\Anaconda3"
set "CONDA_PATHS[3]=C:\ProgramData\Miniconda3"
set "CONDA_PATHS[4]=C:\tools\miniconda3"
set "CONDA_PATHS[5]=C:\Anaconda3"
set "CONDA_PATHS[6]=C:\Miniconda3"

set "CONDA_FOUND=false"
for /L %%i in (0,1,6) do (
    set "CONDA_PATH=!CONDA_PATHS[%%i]!"
    if exist "!CONDA_PATH!\Scripts\conda.exe" (
        echo ✅ Found conda at: !CONDA_PATH!
        set "CONDA_CMD=!CONDA_PATH!\Scripts\conda.exe"
        set "CONDA_ACTIVATE=!CONDA_PATH!\Scripts\activate.bat"
        set "CONDA_FOUND=true"
        goto :conda_ready
    )
)

if "%CONDA_FOUND%"=="false" (
    echo.
    echo ❌ ERROR: Conda not found!
    echo.
    echo 💡 Please install Conda/Miniconda/Anaconda:
    echo    • Miniconda: https://docs.conda.io/en/latest/miniconda.html
    echo    • Anaconda: https://www.anaconda.com/products/distribution
    echo.
    echo    After installation, restart this script.
    echo.
    pause
    exit /b 1
)

:conda_ready
echo ✅ Conda configuration complete
echo 🔧 Using: %CONDA_CMD%

REM =============================================================================
REM STEP 2: CREATE/UPDATE CONDA ENVIRONMENT
REM =============================================================================

echo.
echo 📋 STEP 2: Setting Up Conda Environment
echo ========================================

echo 🔍 Checking if environment '%ENV_NAME%' exists...
"%CONDA_CMD%" env list | findstr /C:"%ENV_NAME%" >nul 2>&1
if %errorlevel%==0 (
    echo ⚠️  Environment '%ENV_NAME%' already exists
    echo.
    choice /C YN /M "Do you want to remove and recreate it? (Y/N)"
    if errorlevel 2 (
        echo 📦 Using existing environment
        goto :activate_environment
    )
    echo 🗑️  Removing existing environment...
    "%CONDA_CMD%" env remove -n %ENV_NAME% -y
    if errorlevel 1 (
        echo ❌ Failed to remove existing environment
        pause
        exit /b 1
    )
)

echo 🔨 Creating conda environment '%ENV_NAME%' with Python %PYTHON_VERSION%...
"%CONDA_CMD%" create -n %ENV_NAME% python=%PYTHON_VERSION% -y
if errorlevel 1 (
    echo ❌ Failed to create conda environment
    echo.
    echo 💡 Try manually:
    echo    conda create -n %ENV_NAME% python=%PYTHON_VERSION% -y
    pause
    exit /b 1
)

echo ✅ Conda environment created successfully

:activate_environment
echo 🔌 Activating environment '%ENV_NAME%'...

REM Activate the environment using the appropriate method
if defined CONDA_ACTIVATE (
    call "%CONDA_ACTIVATE%" %ENV_NAME%
) else (
    call conda activate %ENV_NAME%
)

if errorlevel 1 (
    echo ❌ Failed to activate environment
    pause
    exit /b 1
)

echo ✅ Environment activated successfully

REM =============================================================================
REM STEP 3: INSTALL PYTHON DEPENDENCIES
REM =============================================================================

echo.
echo 📋 STEP 3: Installing Python Dependencies
echo ========================================

echo 🔍 Checking for requirements.txt...
if not exist "requirements.txt" (
    echo ❌ requirements.txt not found
    echo 📝 Creating requirements.txt with essential packages...
    
    echo # Fabric CICD Requirements> requirements.txt
    echo # ========================>> requirements.txt
    echo # Core fabric-cicd library for Microsoft Fabric deployments>> requirements.txt
    echo fabric-cicd^>=0.1.23>> requirements.txt
    echo.>> requirements.txt
    echo # Azure authentication>> requirements.txt
    echo azure-identity^>=1.15.0>> requirements.txt
    echo.>> requirements.txt
    echo # YAML parsing for parameter.yml>> requirements.txt
    echo PyYAML^>=6.0>> requirements.txt
    echo.>> requirements.txt
    echo # Optional: Enhanced command line interface>> requirements.txt
    echo click^>=8.0.0>> requirements.txt
    echo.>> requirements.txt
    echo # Optional: Configuration management>> requirements.txt
    echo python-dotenv^>=1.0.0>> requirements.txt
    
    echo ✅ requirements.txt created
)

echo 📦 Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo ⚠️  Pip upgrade failed, continuing with current version
)

echo 📦 Installing requirements from requirements.txt...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install some packages
    echo.
    echo 💡 Try manually:
    echo    conda activate %ENV_NAME%
    echo    pip install -r requirements.txt
    echo.
    pause
    exit /b 1
)

echo ✅ Python dependencies installed successfully

REM =============================================================================
REM STEP 4: AZURE CLI SETUP (OPTIONAL)
REM =============================================================================

if "%SKIP_AZURE_CLI%"=="true" (
    echo.
    echo 📋 STEP 4: Azure CLI Setup - SKIPPED
    echo ===================================
    echo ⏭️  Azure CLI installation skipped per --skip-azure-cli flag
    goto :validation
)

echo.
echo 📋 STEP 4: Azure CLI Setup
echo ===========================

echo 🔍 Checking for Azure CLI...
az --version >nul 2>&1
if %errorlevel%==0 (
    echo ✅ Azure CLI is already installed
    goto :azure_login
)

echo ❌ Azure CLI not found
echo.
choice /C YN /M "Do you want to install Azure CLI? (Y/N)"
if errorlevel 2 (
    echo ⏭️  Skipping Azure CLI installation
    goto :validation
)

echo.
echo 📥 Downloading and installing Azure CLI...
echo 💡 This will open the Azure CLI installer in your browser
echo    Please follow the installation instructions and restart this script when done.
echo.

REM Download and run Azure CLI installer
powershell -Command "& {Start-Process 'https://aka.ms/installazurecliwindows'}"

echo.
echo ⏸️  Waiting for Azure CLI installation...
echo    Please install Azure CLI and press any key to continue
echo    Or press Ctrl+C to exit and restart this script later
pause

REM Check again after installation
az --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Azure CLI still not found
    echo 💡 Please restart your command prompt and run this script again
    pause
    exit /b 1
)

:azure_login
echo ✅ Azure CLI is available
echo.
echo 🔐 Azure Authentication Setup
echo.
choice /C YN /M "Do you want to authenticate with Azure now? (Y/N)"
if errorlevel 2 (
    echo ⏭️  Skipping Azure authentication
    echo 💡 Remember to run 'az login' before using Fabric CICD
    goto :validation
)

echo 🔐 Starting Azure login process...
az login
if errorlevel 1 (
    echo ❌ Azure login failed
    echo 💡 You can authenticate later with: az login
) else (
    echo ✅ Azure authentication successful
)

REM =============================================================================
REM STEP 5: VALIDATION AND TESTING
REM =============================================================================

:validation
echo.
echo 📋 STEP 5: Environment Validation
echo ==================================

echo 🧪 Testing fabric-cicd import...
python -c "import fabric_cicd; print(f'✅ fabric-cicd version: {fabric_cicd.__version__}')" 2>nul
if errorlevel 1 (
    echo ❌ fabric-cicd import failed
    echo 💡 Try: pip install --upgrade fabric-cicd
) else (
    echo ✅ fabric-cicd import successful
)

echo 🧪 Testing Azure identity...
python -c "from azure.identity import DefaultAzureCredential; print('✅ Azure identity available')" 2>nul
if errorlevel 1 (
    echo ❌ Azure identity import failed
    echo 💡 Try: pip install --upgrade azure-identity
) else (
    echo ✅ Azure identity available
)

echo 🧪 Testing YAML support...
python -c "import yaml; print('✅ YAML support available')" 2>nul
if errorlevel 1 (
    echo ❌ YAML import failed
    echo 💡 Try: pip install --upgrade PyYAML
) else (
    echo ✅ YAML support available
)

REM =============================================================================
REM STEP 6: CREATE ACTIVATION HELPER
REM =============================================================================

echo.
echo 📋 STEP 6: Creating Environment Activation Helper
echo =================================================

echo 📝 Creating activate_fabric_env.bat...

echo @echo off> activate_fabric_env.bat
echo REM =============================================================================>> activate_fabric_env.bat
echo REM Activate Fabric CICD Environment - %ENV_NAME%>> activate_fabric_env.bat
echo REM =============================================================================>> activate_fabric_env.bat
echo.>> activate_fabric_env.bat
echo echo 🚀 Activating Fabric CICD environment: %ENV_NAME%...>> activate_fabric_env.bat

if defined CONDA_ACTIVATE (
    echo call "%CONDA_ACTIVATE%" %ENV_NAME%>> activate_fabric_env.bat
) else (
    echo call conda activate %ENV_NAME%>> activate_fabric_env.bat
)

echo if errorlevel 1 ^(>> activate_fabric_env.bat
echo     echo ❌ Failed to activate environment>> activate_fabric_env.bat
echo     pause>> activate_fabric_env.bat
echo     exit /b 1>> activate_fabric_env.bat
echo ^)>> activate_fabric_env.bat
echo.>> activate_fabric_env.bat
echo echo ✅ Environment activated successfully!>> activate_fabric_env.bat
echo echo 💡 You can now run Fabric CICD commands>> activate_fabric_env.bat
echo echo.>> activate_fabric_env.bat

echo ✅ Helper script created: activate_fabric_env.bat

REM =============================================================================
REM COMPLETION SUMMARY
REM =============================================================================

echo.
echo ========================================
echo 🎉 Setup Complete!
echo ========================================
echo.
echo ✅ Conda environment '%ENV_NAME%' is ready
echo ✅ Python dependencies installed
if "%SKIP_AZURE_CLI%"=="false" (
    echo ✅ Azure CLI configured
)
echo ✅ Environment activation helper created
echo.
echo 🚀 Next Steps:
echo ===============
echo.
echo 1. Activate your environment:
echo    ^> activate_fabric_env.bat
echo.
echo 2. Configure your deployment parameters:
echo    ^> notepad parameter.yml
echo.
echo 3. Run migration examples:
echo    ^> python migration_examples.py --help
echo.
echo 4. Deploy your Fabric items:
echo    ^> python fabric_deploy_local.py --workspace-id "YOUR_ID" --target-env PROD
echo.
echo 💡 Useful Commands:
echo ==================
echo   • Activate environment:    activate_fabric_env.bat
echo   • List environments:       conda env list
echo   • Update packages:         pip install --upgrade fabric-cicd
echo   • Azure login:             az login
echo   • View examples:           python migration_examples.py --help
echo.

echo Press any key to exit...
pause >nul

exit /b 0
