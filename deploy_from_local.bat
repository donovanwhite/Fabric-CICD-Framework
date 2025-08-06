@echo off
REM =============================================================================
REM Local Repository Fabric Deployment Script
REM =============================================================================
REM This script simplifies deployment from local Git repositories
REM to Microsoft Fabric workspaces across different regions

echo.
echo ========================================
echo Local Repository Fabric Deployment
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Check if required script exists
if not exist "fabric_deploy_local.py" (
    echo ❌ fabric_deploy_local.py not found
    echo Please ensure you're running this from the correct directory
    pause
    exit /b 1
)

REM =============================================================================
REM CONFIGURATION - EDIT THESE VALUES
REM =============================================================================

REM Local repository path (current directory by default)
set "LOCAL_REPO_PATH=."

REM Target workspace IDs for each environment
set "DEV_WORKSPACE_ID=11111111-1111-1111-1111-111111111111"
set "STAGING_WORKSPACE_ID=22222222-2222-2222-2222-222222222222"
set "PROD_WORKSPACE_ID=33333333-3333-3333-3333-333333333333"

REM =============================================================================
REM DEPLOYMENT MENU
REM =============================================================================

:menu
echo.
echo Please select deployment target:
echo.
echo 1. Deploy to DEV environment
echo 2. Deploy to STAGING environment
echo 3. Deploy to PROD environment
echo 4. Dry run validation (DEV)
echo 5. Deploy specific items only
echo 6. Cross-region migration
echo 7. Exit
echo.
set /p choice="Enter your choice (1-7): "

if "%choice%"=="1" goto deploy_dev
if "%choice%"=="2" goto deploy_staging
if "%choice%"=="3" goto deploy_prod
if "%choice%"=="4" goto dry_run
if "%choice%"=="5" goto deploy_specific
if "%choice%"=="6" goto cross_region_migration
if "%choice%"=="7" goto exit
goto invalid_choice

:deploy_dev
echo.
echo 🚀 Deploying to DEV environment...
echo    Repository: %LOCAL_REPO_PATH%
echo    Workspace: %DEV_WORKSPACE_ID%
echo.
python fabric_deploy_local.py --repository "%LOCAL_REPO_PATH%" --workspace-id "%DEV_WORKSPACE_ID%" --environment DEV
goto deployment_complete

:deploy_staging
echo.
echo 🚀 Deploying to STAGING environment...
echo    Repository: %LOCAL_REPO_PATH%
echo    Workspace: %STAGING_WORKSPACE_ID%
echo.
python fabric_deploy_local.py --repository "%LOCAL_REPO_PATH%" --workspace-id "%STAGING_WORKSPACE_ID%" --environment STAGING
goto deployment_complete

:deploy_prod
echo.
echo 🚀 Deploying to PROD environment...
echo    Repository: %LOCAL_REPO_PATH%
echo    Workspace: %PROD_WORKSPACE_ID%
echo.
set /p confirm="⚠️  This will deploy to PRODUCTION. Are you sure? (y/N): "
if /i not "%confirm%"=="y" (
    echo Deployment cancelled.
    goto menu
)
python fabric_deploy_local.py --repository "%LOCAL_REPO_PATH%" --workspace-id "%PROD_WORKSPACE_ID%" --environment PROD
goto deployment_complete

:dry_run
echo.
echo 🔍 Performing dry run validation (DEV)...
echo    Repository: %LOCAL_REPO_PATH%
echo    Workspace: %DEV_WORKSPACE_ID%
echo.
python fabric_deploy_local.py --repository "%LOCAL_REPO_PATH%" --workspace-id "%DEV_WORKSPACE_ID%" --environment DEV --dry-run
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
) else if /i "%env%"=="STAGING" (
    set "workspace_id=%STAGING_WORKSPACE_ID%"
) else if /i "%env%"=="PROD" (
    set "workspace_id=%PROD_WORKSPACE_ID%"
) else (
    echo ❌ Invalid environment. Please use DEV, STAGING, or PROD
    goto menu
)

echo 🚀 Deploying specific items to %env%...
echo    Items: %items%
echo    Repository: %LOCAL_REPO_PATH%
echo    Workspace: %workspace_id%
echo.
python fabric_deploy_local.py --repository "%LOCAL_REPO_PATH%" --workspace-id "%workspace_id%" --environment %env% --items %items%
goto deployment_complete

:cross_region_migration
echo.
echo ========================================
echo 🌍 Cross-Region Migration Setup
echo ========================================
echo.
echo Available environments: DEV, STAGING, PROD
echo.
set /p source_env="Enter SOURCE environment: "
set /p target_env="Enter TARGET environment: "
echo.

REM Set source workspace
if /i "%source_env%"=="DEV" (
    set "source_workspace=%DEV_WORKSPACE_ID%"
) else if /i "%source_env%"=="STAGING" (
    set "source_workspace=%STAGING_WORKSPACE_ID%"
) else if /i "%source_env%"=="PROD" (
    set "source_workspace=%PROD_WORKSPACE_ID%"
) else (
    echo ❌ Invalid source environment
    goto menu
)

REM Set target workspace
if /i "%target_env%"=="DEV" (
    set "target_workspace=%DEV_WORKSPACE_ID%"
) else if /i "%target_env%"=="STAGING" (
    set "target_workspace=%STAGING_WORKSPACE_ID%"
) else if /i "%target_env%"=="PROD" (
    set "target_workspace=%PROD_WORKSPACE_ID%"
) else (
    echo ❌ Invalid target environment
    goto menu
)

echo.
echo 🚀 Cross-region migration: %source_env% → %target_env%
echo    Source Workspace: %source_workspace%
echo    Target Workspace: %target_workspace%
echo.
set /p confirm="Proceed with migration? (y/N): "
if /i not "%confirm%"=="y" (
    echo Migration cancelled.
    goto menu
)

python fabric_deploy_local.py --repository "%LOCAL_REPO_PATH%" --source-workspace "%source_workspace%" --target-workspace "%target_workspace%" --source-env %source_env% --target-env %target_env%
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
goto menu

:invalid_choice
echo.
echo ❌ Invalid choice. Please enter 1-7.
goto menu

:exit
echo.
echo Thank you for using Local Repository Fabric Deployment!
echo.
pause
exit /b 0

REM =============================================================================
REM TROUBLESHOOTING TIPS
REM =============================================================================
REM 
REM If deployment fails:
REM 1. Verify Azure CLI is logged in: az login
REM 2. Check workspace IDs are correct
REM 3. Verify parameter.yml exists in repository root
REM 4. Ensure Fabric items are present in local repository
REM 5. Check fabric-cicd environment is activated
REM 
REM For environment issues:
REM - Activate conda environment: conda activate fabric-cicd
REM - Or use: activate_fabric_env.bat
REM
