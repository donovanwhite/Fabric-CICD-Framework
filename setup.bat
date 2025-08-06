@echo off
REM Microsoft Fabric CICD Setup Script
REM ===================================
REM This script sets up the fabric-cicd environment for cross-region migration

echo.
echo ========================================
echo  Microsoft Fabric CICD Setup
echo ========================================
echo.

@echo off
REM Microsoft Fabric CICD Setup Script
REM ===================================
REM This script sets up the fabric-cicd environment for cross-region migration

echo.
echo ========================================
echo  Microsoft Fabric CICD Setup
echo ========================================
echo.

REM Check Python version compatibility
echo 🔍 Checking Python version compatibility...
python -c "import sys; major, minor = sys.version_info[:2]; print(f'Python {major}.{minor} detected'); exit(0 if (major == 3 and 9 <= minor <= 12) else 1)" 2>nul
if errorlevel 1 (
    echo.
    echo ❌ ERROR: fabric-cicd requires Python 3.9 to 3.12
    echo    Your Python version is not compatible.
    echo.
    echo 💡 Solutions:
    echo    1. Install Python 3.12: https://www.python.org/downloads/
    echo    2. Use pyenv: pyenv install 3.12.7 ^&^& pyenv local 3.12.7
    echo    3. Use conda: conda create -n fabric-cicd python=3.12
    echo.
    pause
    exit /b 1
)

echo ✅ Python version is compatible

REM Check pip
pip --version >nul 2>&1
if errorlevel 1 (
    echo ❌ pip not found. Please install pip.
    pause
    exit /b 1
)

echo ✅ pip found

REM Install requirements
echo.
echo 📦 Installing fabric-cicd dependencies...
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ Failed to install dependencies.
    echo    Please check your internet connection and try again.
    pause
    exit /b 1
)

echo ✅ Dependencies installed successfully

REM Check Azure CLI
echo.
echo 🔍 Checking Azure CLI...
az --version >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Azure CLI not found.
    echo    Please install Azure CLI from: https://aka.ms/installazurecliwindows
    echo    Then run: az login
) else (
    echo ✅ Azure CLI found
    
    REM Check if logged in
    az account show >nul 2>&1
    if errorlevel 1 (
        echo ⚠️  Not logged in to Azure.
        echo    Please run: az login
    ) else (
        echo ✅ Azure CLI authenticated
        az account show --query "name" -o tsv
    )
)

REM Verify fabric-cicd installation
echo.
echo 🧪 Testing fabric-cicd installation...
python -c "from fabric_cicd import FabricWorkspace; print('✅ fabric-cicd imported successfully')" 2>nul
if errorlevel 1 (
    echo ❌ fabric-cicd import failed.
    echo    Please check the installation.
) else (
    echo ✅ fabric-cicd ready to use
)

REM Check repository structure
echo.
echo 📁 Checking repository structure...

if exist "parameter.yml" (
    echo ✅ parameter.yml found
) else (
    echo ⚠️  parameter.yml not found - template created
    echo    Please edit parameter.yml with your workspace and item IDs
)

REM Look for Fabric items
echo.
echo 🔍 Scanning for Fabric items...
set /a count=0
for /d %%i in (*.Notebook *.Report *.Dashboard *.SemanticModel *.Lakehouse *.Warehouse *.DataPipeline *.Dataflow *.Environment) do (
    echo    📁 %%i
    set /a count+=1
)

if %count% equ 0 (
    echo ⚠️  No Fabric items found in current directory
    echo    Expected folder structure: ItemName.ItemType\
    echo    Example: MyNotebook.Notebook\, SalesReport.Report\
) else (
    echo ✅ Found %count% Fabric item(s)
)

echo.
echo ========================================
echo  Setup Summary
echo ========================================
echo.
echo ✅ Python and pip installed
echo ✅ Dependencies installed
if exist "parameter.yml" (
    echo ✅ parameter.yml configured
) else (
    echo ⚠️  parameter.yml needs configuration
)
echo.
echo 🚀 Next Steps:
echo    1. Configure parameter.yml with your workspace IDs
echo    2. Create external connections in target workspace (SQL, Storage, etc.)
echo    3. Update connection GUIDs in parameter.yml  
echo    4. Ensure Azure CLI is authenticated: az login
echo    5. Test deployment: python fabric_deploy.py --help
echo    6. Run dry-run: python fabric_deploy.py --workspace-id "your-id" --environment DEV --dry-run
echo.
echo 🔗 Connection Handling:
echo    ✅ Fabric-to-Fabric references (automatic)
echo    ⚠️  External connections (manual setup required)
echo    ✅ Connection strings ^& endpoints (parameter replacement)
echo    📖 See connection_handling_guide.yml for details
echo.

pause
