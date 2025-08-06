@echo off
REM =============================================================================
REM Activate Fabric CICD Conda Environment
REM =============================================================================
REM This script activates the fabric-cicd conda environment for development

echo.
echo 🚀 Activating Fabric CICD Environment...
echo.

REM Activate the conda environment
call "C:\ProgramData\Anaconda3\Scripts\activate.bat" fabric-cicd

REM Show environment info
echo ✅ Environment activated!
echo 📋 Environment: fabric-cicd
echo 🐍 Python version:
python --version
echo.

REM Test fabric-cicd availability
echo 🧪 Testing fabric-cicd installation...
python test_environment.py

echo.
echo 🎯 You're now ready to use Fabric CICD!
echo.
echo 📚 Available scripts:
echo    python fabric_deploy_local.py --help    # Deploy from local repository
echo    python fabric_deploy_devops.py --help   # Deploy from Azure DevOps
echo    deploy_from_devops.bat                   # Interactive DevOps deployment
echo.
echo 💡 To deactivate: conda deactivate
echo.

REM Keep the command prompt open in the activated environment
cmd /k
