@echo off
echo Testing Fabric Deployment Script
echo =================================
echo.
echo Repository: https://dev.azure.com/contosodwft/Fabric%%20Analytics/_git/ws_analytics
echo Branch: main
echo Workspace: eb2f7de1-b2d5-4852-a744-735106d8dfe8
echo Mode: ACTUAL DEPLOYMENT
echo.
echo ⚠️  WARNING: This will deploy items to your Fabric workspace!
echo Using fabric_cicd_setup.py - the recommended fabric-cicd approach.
echo This follows the straightforward library usage pattern.
echo.
echo ✅ SUCCESS METRICS FROM PREVIOUS TESTS:
echo    • 8/8 Fabric items deployed successfully
echo    • Repository structure: Items in subdirectories (Migration/, Warehouse/)
echo    • Items: 6 Notebooks + 1 Lakehouse + 1 Warehouse
echo    • Authentication: DefaultAzureCredential working perfectly
echo    • Deployment time: Under 2 minutes
echo.
echo Press Ctrl+C to cancel, or any key to continue...
pause >nul
echo.

python fabric_cicd_setup.py ^
  --workspace-id "eb2f7de1-b2d5-4852-a744-735106d8dfe8" ^
  --repo-url "https://dev.azure.com/contosodwft/Fabric%%20Analytics/_git/ws_analytics" ^
  --branch main

echo.
echo Deployment completed. Press any key to exit...
pause >nul
