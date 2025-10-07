# Environment Setup Scripts

This folder contains scripts for setting up the Python environment and dependencies.

## Files

- **`setup_pyenv.bat`** - Sets up pyenv and installs required Python version
- **`activate_fabric_env_pyenv.bat`** - Activates the fabric environment

## Python Environment Requirements

- **Python Version**: 3.9-3.12 (recommended: 3.11)
- **Package Manager**: pip
- **Virtual Environment**: pyenv or venv recommended

## Additional Requirements for Warehouse Schema Deployment

- **SqlPackage.exe**: Microsoft's database deployment tool (installed automatically via .NET global tool)
- **Microsoft ODBC Driver for SQL Server**: Required for connection testing
  - Windows: Usually pre-installed or available via Windows Update
  - Manual install: Download from Microsoft (ODBC Driver 17 or 18 for SQL Server)
- **.NET SDK**: Required for SqlPackage.exe installation and SQL project builds

## Setup Process

### 1. Initial Setup
```bash
# Run the setup script
setup_pyenv.bat
```

This script will:
- Install pyenv if not present
- Install Python 3.11 (if not already installed)
- Create a virtual environment for the fabric project
- Install required dependencies from requirements.txt

### 2. Environment Activation
```bash
# Activate the environment
activate_fabric_env_pyenv.bat
```

This script activates the virtual environment for fabric deployments.

## Manual Setup (Alternative)

If the batch scripts don't work in your environment:

```bash
# Create virtual environment
python -m venv fabric_env

# Activate environment (Windows)
fabric_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Troubleshooting

### Common Issues

1. **Python version not supported**: Ensure you have Python 3.9-3.12 installed
2. **Permission errors**: Run scripts as administrator if needed
3. **Path issues**: Ensure Python and pip are in your system PATH
4. **Network restrictions**: Configure proxy settings if behind corporate firewall

### Verification

After setup, verify your environment:
```bash
python --version  # Should show 3.9-3.12
pip list          # Should show fabric-cicd >= 0.1.29
```

## Environment Variables

The scripts may set these environment variables:
- `PYTHONPATH` - Python module search path
- `FABRIC_ENV` - Current environment identifier
- Various Azure authentication variables