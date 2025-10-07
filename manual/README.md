# Manual Deployment Scripts

This folder contains scripts for manual deployment operations.

## Files

- **`deploy.bat`** - Windows batch script for quick manual deployment

## Usage

### Manual Deployment
```batch
deploy.bat
```

This script provides a simple interface for manual deployment operations when you need to deploy outside of automated CI/CD processes.

For automated deployments, use the main deployment script:
```bash
cd ../core
python fabric_deploy.py --workspace-id "your-workspace-id" --repo-url "your-repo-url"
```

## Environment Setup

Before using manual deployment scripts, ensure your environment is set up:
```batch
cd ../envsetup
setup_pyenv.bat
## Prerequisites

Before using manual deployment:

1. **Set up the environment**:
   ```batch
   cd ../envsetup
   setup_pyenv.bat
   ```

2. **Activate the environment**:
   ```batch
   cd ../envsetup
   activate_fabric_env_pyenv.bat
   ```

3. **Configure your deployment**:
   - Update `../config/parameter.yml` with your workspace details
   - Or use the configuration-based approach with `../config/config.yml`

## Manual Deployment Process

1. **Basic deployment**:
   ```batch
   deploy.bat
   ```

2. **Advanced deployment from core**:
   ```batch
   cd ../core
   python fabric_deploy.py --workspace-id "your-workspace-id" --repo-url "your-repo-url"
   ```

3. **With warehouse schema deployment**:
   ```batch
   cd ../core
   python fabric_deploy.py --workspace-id "your-workspace-id" --repo-url "your-repo-url" --include-warehouse-schemas
   ```

## Features

- Simple batch script interface for quick deployments
- Integration with the core deployment engine
- Support for warehouse schema deployment
- Environment validation through setup scripts