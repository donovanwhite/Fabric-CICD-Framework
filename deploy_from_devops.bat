@echo off
REM =============================================================================
REM Azure DevOps Fabric Deployment Script
REM =============================================================================
REM This script simplifies deployment from Azure DevOps Git repositories
REM to Microsoft Fabric workspaces across different regions

echo.
echo ========================================
echo Azure DevOps Fabric Deployment
echo ========================================

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if required script exists
if not exist "fabric_deploy_devops.py" (
    echo ❌ fabric_deploy_devops.py not found
    echo Please ensure you're running this from the correct directory
    pause
    exit /b 1
)

REM =============================================================================
REM CONFIGURATION - EDIT THESE VALUES
REM =============================================================================

REM Your Azure DevOps repository URL
set "DEVOPS_REPO_URL=https://dev.azure.com/myorg/myproject/_git/fabric-repo"

REM Target workspace IDs for each environment
set "DEV_WORKSPACE_ID=11111111-1111-1111-1111-111111111111"
set "STAGING_WORKSPACE_ID=22222222-2222-2222-2222-222222222222"
set "PROD_WORKSPACE_ID=33333333-3333-3333-3333-333333333333"

REM Git branch configuration for each environment
set "DEV_BRANCH=develop"
set "STAGING_BRANCH=release/staging"
set "PROD_BRANCH=main"

echo.
echo Select deployment type:
echo 1. Parameterized Deployment (uses parameter.yml)
echo 2. Simple Deployment (keep original names)
echo 3. Exit
echo.
set /p DEPLOY_TYPE="Enter your choice (1-3): "

if "%DEPLOY_TYPE%"=="3" goto :end
if "%DEPLOY_TYPE%"=="1" goto :parameterized_menu
if "%DEPLOY_TYPE%"=="2" goto :simple_menu

echo ❌ Invalid choice. Please select 1, 2, or 3.
pause
goto :end

:parameterized_menu
echo.
echo === PARAMETERIZED DEPLOYMENT ===
echo This mode uses parameter.yml to replace environment-specific values
echo.
echo Please select deployment target:
echo.
echo 1. Deploy to DEV environment (from %DEV_BRANCH% branch)
echo 2. Deploy to STAGING environment (from %STAGING_BRANCH% branch)
echo 3. Deploy to PROD environment (from %PROD_BRANCH% branch)
echo 4. Dry run validation (DEV)
echo 5. Deploy specific items only
echo 6. Back to main menu
echo.
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto deploy_dev
if "%choice%"=="2" goto deploy_staging
if "%choice%"=="3" goto deploy_prod
if "%choice%"=="4" goto dry_run
if "%choice%"=="5" goto deploy_specific
if "%choice%"=="6" goto :eof
goto invalid_choice

:simple_menu
echo.
echo === SIMPLE DEPLOYMENT ===
echo This mode keeps original item names - no parameter.yml replacement
echo.
echo Please select deployment target:
echo.
echo 1. Deploy to DEV workspace (from %DEV_BRANCH% branch)
echo 2. Deploy to STAGING workspace (from %STAGING_BRANCH% branch)
echo 3. Deploy to PROD workspace (from %PROD_BRANCH% branch)
echo 4. Dry run validation (DEV workspace)
echo 5. Deploy specific items only (any workspace)
echo 6. Back to main menu
echo.
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto simple_deploy_dev
if "%choice%"=="2" goto simple_deploy_staging
if "%choice%"=="3" goto simple_deploy_prod
if "%choice%"=="4" goto simple_dry_run
if "%choice%"=="5" goto simple_deploy_specific
if "%choice%"=="6" goto :eof
goto invalid_choice

:deploy_dev
echo.
echo 🚀 Deploying to DEV environment...
echo    Repository: %DEVOPS_REPO_URL%
echo    Branch: %DEV_BRANCH%
echo    Workspace: %DEV_WORKSPACE_ID%
echo.
python fabric_deploy_devops.py --workspace-id "%DEV_WORKSPACE_ID%" --target-env DEV --repo-url "%DEVOPS_REPO_URL%" --branch %DEV_BRANCH%
goto deployment_complete

:deploy_staging
echo.
echo 🚀 Deploying to STAGING environment...
echo    Repository: %DEVOPS_REPO_URL%
echo    Branch: %STAGING_BRANCH%
echo    Workspace: %STAGING_WORKSPACE_ID%
echo.
python fabric_deploy_devops.py --workspace-id "%STAGING_WORKSPACE_ID%" --target-env STAGING --repo-url "%DEVOPS_REPO_URL%" --branch %STAGING_BRANCH%
goto deployment_complete

:deploy_prod
echo.
echo 🚀 Deploying to PROD environment...
echo    Repository: %DEVOPS_REPO_URL%
echo    Branch: %PROD_BRANCH%
echo    Workspace: %PROD_WORKSPACE_ID%
echo.
set /p confirm="⚠️  This will deploy to PRODUCTION. Are you sure? (y/N): "
if /i not "%confirm%"=="y" (
    echo Deployment cancelled.
    goto menu
)
python fabric_deploy_devops.py --workspace-id "%PROD_WORKSPACE_ID%" --target-env PROD --repo-url "%DEVOPS_REPO_URL%" --branch %PROD_BRANCH%
goto deployment_complete

:dry_run
echo.
echo 🔍 Performing dry run validation (DEV)...
echo    Repository: %DEVOPS_REPO_URL%
echo    Branch: %DEV_BRANCH%
echo    Workspace: %DEV_WORKSPACE_ID%
echo.
python fabric_deploy_devops.py --workspace-id "%DEV_WORKSPACE_ID%" --target-env DEV --repo-url "%DEVOPS_REPO_URL%" --branch %DEV_BRANCH% --dry-run
goto deployment_complete

:deploy_specific
echo.
echo Available item types: Notebook, Report, Dashboard, SemanticModel, Lakehouse, Warehouse, DataPipeline, Dataflow
echo.
set /p items="Enter item types to deploy (space-separated): "
set /p env="Enter target environment (DEV/STAGING/PROD): "
echo.

if /i "%env%"=="DEV" (
    set "workspace_id=%DEV_WORKSPACE_ID%"
    set "branch=%DEV_BRANCH%"
) else if /i "%env%"=="STAGING" (
    set "workspace_id=%STAGING_WORKSPACE_ID%"
    set "branch=%STAGING_BRANCH%"
) else if /i "%env%"=="PROD" (
    set "workspace_id=%PROD_WORKSPACE_ID%"
    set "branch=%PROD_BRANCH%"
) else (
    echo ❌ Invalid environment. Please use DEV, STAGING, or PROD
    goto menu
)

echo 🚀 Deploying specific items to %env%...
echo    Items: %items%
echo    Repository: %DEVOPS_REPO_URL%
echo    Branch: %branch%
echo    Workspace: %workspace_id%
echo.
python fabric_deploy_devops.py --workspace-id "%workspace_id%" --target-env %env% --repo-url "%DEVOPS_REPO_URL%" --branch %branch% --items %items%
goto deployment_complete

:deployment_complete
echo.
if errorlevel 1 (
    echo ❌ Deployment failed. Please check the error messages above.
) else (
    echo ✅ Deployment completed successfully!
)
echo.
set /p continue="Press Enter to return to menu or 'q' to quit: "
if /i "%continue%"=="q" goto exit
if "%DEPLOY_TYPE%"=="1" goto parameterized_menu
if "%DEPLOY_TYPE%"=="2" goto simple_menu
goto :eof

REM =============================================================================
REM SIMPLE DEPLOYMENT FUNCTIONS (NO PARAMETERIZATION)
REM =============================================================================

:simple_deploy_dev
echo.
echo 🚀 Simple Deployment to DEV workspace (keeping original names)
echo =====================================================================
echo Branch: %DEV_BRANCH%
echo Workspace: %DEV_WORKSPACE_ID%
echo Parameterization: DISABLED
echo.
python fabric_deploy_devops.py --workspace-id "%DEV_WORKSPACE_ID%" --simple --repo-url "%DEVOPS_REPO_URL%" --branch "%DEV_BRANCH%"
goto deployment_complete

:simple_deploy_staging
echo.
echo 🚀 Simple Deployment to STAGING workspace (keeping original names)
echo =====================================================================
echo Branch: %STAGING_BRANCH%
echo Workspace: %STAGING_WORKSPACE_ID%
echo Parameterization: DISABLED
echo.
python fabric_deploy_devops.py --workspace-id "%STAGING_WORKSPACE_ID%" --simple --repo-url "%DEVOPS_REPO_URL%" --branch "%STAGING_BRANCH%"
goto deployment_complete

:simple_deploy_prod
echo.
echo 🚀 Simple Deployment to PROD workspace (keeping original names)
echo =====================================================================
echo Branch: %PROD_BRANCH%
echo Workspace: %PROD_WORKSPACE_ID%
echo Parameterization: DISABLED
echo.
echo ⚠️  WARNING: You are deploying to PRODUCTION workspace!
echo This will deploy items with their original names from the repository.
set /p confirm="Are you sure? Type 'YES' to continue: "
if /i not "%confirm%"=="YES" (
    echo Deployment cancelled.
    goto simple_menu
)
python fabric_deploy_devops.py --workspace-id "%PROD_WORKSPACE_ID%" --simple --repo-url "%DEVOPS_REPO_URL%" --branch "%PROD_BRANCH%"
goto deployment_complete

:simple_dry_run
echo.
echo 🔍 Simple Deployment Validation (DEV workspace - DRY RUN)
echo =====================================================================
echo Branch: %DEV_BRANCH%
echo Workspace: %DEV_WORKSPACE_ID%
echo Mode: VALIDATION ONLY (no actual deployment)
echo Parameterization: DISABLED
echo.
python fabric_deploy_devops.py --workspace-id "%DEV_WORKSPACE_ID%" --simple --repo-url "%DEVOPS_REPO_URL%" --branch "%DEV_BRANCH%" --dry-run
goto deployment_complete

:simple_deploy_specific
echo.
echo 📦 Simple Deployment - Specific Items Only
echo =====================================================================
echo.
echo Which workspace?
echo 1. DEV (%DEV_WORKSPACE_ID%)
echo 2. STAGING (%STAGING_WORKSPACE_ID%)
echo 3. PROD (%PROD_WORKSPACE_ID%)
echo.
set /p ws_choice="Enter workspace choice (1-3): "

if "%ws_choice%"=="1" (
    set "TARGET_WORKSPACE=%DEV_WORKSPACE_ID%"
    set "TARGET_BRANCH=%DEV_BRANCH%"
    set "TARGET_NAME=DEV"
)
if "%ws_choice%"=="2" (
    set "TARGET_WORKSPACE=%STAGING_WORKSPACE_ID%"
    set "TARGET_BRANCH=%STAGING_BRANCH%"
    set "TARGET_NAME=STAGING"
)
if "%ws_choice%"=="3" (
    set "TARGET_WORKSPACE=%PROD_WORKSPACE_ID%"
    set "TARGET_BRANCH=%PROD_BRANCH%"
    set "TARGET_NAME=PROD"
)

if not defined TARGET_WORKSPACE (
    echo ❌ Invalid workspace choice
    goto simple_deploy_specific
)

echo.
echo Common item types:
echo - Notebook DataPipeline (Data Engineering)
echo - Lakehouse Warehouse (Data Storage)
echo - Report Dashboard SemanticModel (Analytics)
echo - Environment (Spark Configuration)
echo.
set /p items="Enter item types (space-separated, e.g., Notebook Report): "

echo.
echo 🚀 Simple Deployment to %TARGET_NAME% workspace (specific items)
echo Workspace: %TARGET_WORKSPACE%
echo Items: %items%
echo Parameterization: DISABLED
echo.
python fabric_deploy_devops.py --workspace-id "%TARGET_WORKSPACE%" --simple --repo-url "%DEVOPS_REPO_URL%" --branch "%TARGET_BRANCH%" --items %items%
goto deployment_complete

:invalid_choice
echo.
echo ❌ Invalid choice. Please enter 1-7.
pause
goto parameterized_menu

:exit
echo.
echo Thank you for using Azure DevOps Fabric Deployment!
echo.
pause

:end
exit /b 0

REM =============================================================================
REM TROUBLESHOOTING TIPS
REM =============================================================================
REM 
REM If deployment fails:
REM 1. Verify Azure CLI is logged in: az login
REM 2. Check repository URL and access permissions
REM 3. Ensure workspace IDs are correct
REM 4. Verify parameter.yml exists in repository root
REM 5. Check Git credentials are configured for DevOps
REM 
REM For Git credential issues:
REM - Install Git Credential Manager
REM - Run: git config --global credential.helper manager-core
REM - Authenticate once: git clone [your-repo-url]
REM
