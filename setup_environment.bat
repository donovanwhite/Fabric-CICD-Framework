@echo off
REM =============================================================================
REM Fabric CICD Environment Setup Script
REM =============================================================================
REM This script creates a Python environment for Fabric CICD deployment
REM Supports both conda and venv depending on what's available

echo.
echo ========================================
echo Fabric CICD Environment Setup
echo ========================================
echo.

REM Check current Python version
echo 🔍 Checking current Python version...
python --version
echo.

REM Check for conda availability
echo 🔍 Checking for conda installation...
conda --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Conda not found in PATH
    goto check_for_conda_installation
) else (
    echo ✅ Conda found
    goto create_conda_env
)

:check_for_conda_installation
echo.
echo 🔍 Searching for conda in common installation paths...

REM Check common conda installation paths
if exist "%USERPROFILE%\anaconda3\Scripts\conda.exe" (
    echo ✅ Found Anaconda at %USERPROFILE%\anaconda3
    set "CONDA_PATH=%USERPROFILE%\anaconda3\Scripts\conda.exe"
    goto setup_conda_path
)

if exist "%USERPROFILE%\miniconda3\Scripts\conda.exe" (
    echo ✅ Found Miniconda at %USERPROFILE%\miniconda3
    set "CONDA_PATH=%USERPROFILE%\miniconda3\Scripts\conda.exe"
    goto setup_conda_path
)

if exist "C:\ProgramData\Anaconda3\Scripts\conda.exe" (
    echo ✅ Found Anaconda at C:\ProgramData\Anaconda3
    set "CONDA_PATH=C:\ProgramData\Anaconda3\Scripts\conda.exe"
    goto setup_conda_path
)

if exist "C:\ProgramData\Miniconda3\Scripts\conda.exe" (
    echo ✅ Found Miniconda at C:\ProgramData\Miniconda3
    set "CONDA_PATH=C:\ProgramData\Miniconda3\Scripts\conda.exe"
    goto setup_conda_path
)

echo ❌ Conda not found in common installation paths
goto offer_conda_install

:setup_conda_path
echo 🔧 Setting up conda path temporarily...
set "PATH=%PATH%;%CONDA_PATH%\.."
goto create_conda_env

:offer_conda_install
echo.
echo 💡 Conda is not installed. You have two options:
echo.
echo 1. Install Miniconda (Recommended for fabric-cicd)
echo    - Download from: https://docs.conda.io/en/latest/miniconda.html
echo    - Allows easy Python version management
echo.
echo 2. Use Python venv with current Python version
echo    - Current version: 
python --version
echo    - ⚠️  Warning: fabric-cicd requires Python >=3.9 and <3.13
echo    - Your current version may not be compatible
echo.
set /p choice="Choose option (1 for Miniconda install info, 2 for venv): "

if "%choice%"=="1" goto miniconda_install_info
if "%choice%"=="2" goto create_venv
goto offer_conda_install

:miniconda_install_info
echo.
echo 📥 To install Miniconda:
echo.
echo 1. Download Miniconda from: https://docs.conda.io/en/latest/miniconda.html
echo 2. Choose "Miniconda3 Windows 64-bit" installer
echo 3. Run the installer and follow the prompts
echo 4. Select "Add Miniconda3 to my PATH environment variable" during installation
echo 5. Restart your command prompt
echo 6. Run this script again
echo.
echo 🌐 Opening Miniconda download page...
start https://docs.conda.io/en/latest/miniconda.html
echo.
pause
exit /b 0

:create_conda_env
echo.
echo 🚀 Creating conda environment 'fabric-cicd' with Python 3.12...
echo.

REM Create conda environment with Python 3.12
"%CONDA_PATH%" create -n fabric-cicd python=3.12 -y

if errorlevel 1 (
    echo ❌ Failed to create conda environment
    pause
    exit /b 1
)

echo.
echo ✅ Conda environment created successfully!
echo.
echo 🔄 Activating environment and installing packages...

REM Activate environment and install packages
call "%CONDA_PATH%\..\activate.bat" fabric-cicd

REM Install packages
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Failed to install packages
    pause
    exit /b 1
)

echo.
echo ✅ All packages installed successfully!
goto show_usage_conda

:create_venv
echo.
echo 🚀 Creating Python virtual environment...
echo.

REM Check Python version compatibility
python -c "import sys; exit(0 if (3, 9) <= sys.version_info < (3, 13) else 1)" >nul 2>&1
if errorlevel 1 (
    echo ❌ Current Python version is not compatible with fabric-cicd
    echo    Required: Python >=3.9 and <3.13
    echo    Current: 
    python --version
    echo.
    echo 💡 Please install a compatible Python version or use conda
    pause
    exit /b 1
)

REM Create virtual environment
python -m venv fabric-cicd-venv

if errorlevel 1 (
    echo ❌ Failed to create virtual environment
    pause
    exit /b 1
)

echo ✅ Virtual environment created successfully!
echo.
echo 🔄 Activating environment and installing packages...

REM Activate virtual environment
call fabric-cicd-venv\Scripts\activate.bat

REM Install packages
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Failed to install packages
    pause
    exit /b 1
)

echo.
echo ✅ All packages installed successfully!
goto show_usage_venv

:show_usage_conda
echo.
echo ========================================
echo 🎉 Environment Setup Complete!
echo ========================================
echo.
echo 📋 Environment Details:
echo    Type: Conda Environment
echo    Name: fabric-cicd
echo    Python Version: 3.12
echo.
echo 🚀 To use this environment:
echo.
echo    # Activate the environment
echo    conda activate fabric-cicd
echo.
echo    # Verify installation
echo    python -c "from fabric_cicd import FabricWorkspace; print('✅ fabric-cicd ready!')"
echo.
echo    # Run local deployment
echo    python fabric_deploy_local.py --help
echo.
echo    # Run DevOps deployment
echo    python fabric_deploy_devops.py --help
echo.
echo 💡 The environment is already activated in this session!
goto test_installation

:show_usage_venv
echo.
echo ========================================
echo 🎉 Environment Setup Complete!
echo ========================================
echo.
echo 📋 Environment Details:
echo    Type: Python Virtual Environment
echo    Location: fabric-cicd-venv\
echo    Python Version: 
python --version
echo.
echo 🚀 To use this environment:
echo.
echo    # Activate the environment
echo    fabric-cicd-venv\Scripts\activate.bat
echo.
echo    # Verify installation
echo    python -c "from fabric_cicd import FabricWorkspace; print('✅ fabric-cicd ready!')"
echo.
echo    # Run local deployment
echo    python fabric_deploy_local.py --help
echo.
echo    # Run DevOps deployment
echo    python fabric_deploy_devops.py --help
echo.
echo 💡 The environment is already activated in this session!
goto test_installation

:test_installation
echo.
echo 🧪 Testing installation...
python -c "from fabric_cicd import FabricWorkspace; print('✅ fabric-cicd library imported successfully!')" 2>nul
if errorlevel 1 (
    echo ❌ fabric-cicd library test failed
    echo    This might be due to network issues or package conflicts
    echo    Try running: pip install --upgrade fabric-cicd
) else (
    echo ✅ fabric-cicd library test passed!
)

echo.
echo 🧪 Testing Azure authentication...
python -c "from azure.identity import AzureCliCredential; print('✅ Azure identity library ready!')" 2>nul
if errorlevel 1 (
    echo ❌ Azure identity library test failed
    echo    Try running: pip install --upgrade azure-identity
) else (
    echo ✅ Azure identity library test passed!
)

echo.
echo 📋 Next Steps:
echo    1. Configure your parameter.yml file
echo    2. Set up Azure CLI authentication: az login
echo    3. Configure DevOps repository settings in devops_config.yml
echo    4. Test deployment with --dry-run flag
echo.
pause
exit /b 0

REM =============================================================================
REM Error Handling
REM =============================================================================

:error
echo ❌ An error occurred during setup
pause
exit /b 1
