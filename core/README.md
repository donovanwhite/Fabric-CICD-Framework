# Core Deployment Logic

This folder contains the core deployment scripts and utilities for the Fabric CI/CD Framework.

## Files

- **`fabric_deploy.py`** - Main deployment script with traditional and configuration-based approaches
- **`supported_item_types.py`** - Definitive reference for officially supported Fabric item types
- **`warehouse_schema_deploy_sqlpackage.py`** - Warehouse schema deployment engine using SqlPackage.exe

## fabric_deploy.py

The main deployment script supports two deployment approaches:

### Traditional Parameter-based Deployment
```python
python fabric_deploy.py
```

### Configuration-based Deployment (v0.1.29)
```python
python fabric_deploy.py --config-file ../config/config.yml
```

## Key Features

- **Dual deployment modes**: Traditional parameters and new configuration-based approach
- **Warehouse schema deployment**: Automated SQL schema deployment using SqlPackage.exe
- **Enhanced error handling**: Comprehensive logging and validation
- **Environment flexibility**: Support for multiple environments and authentication methods
- **Item type validation**: Ensures only supported item types are deployed

## Supported Item Types (21 total)

See `supported_item_types.py` for the complete list of officially supported item types in fabric-cicd v0.1.29.

## Dependencies

- fabric-cicd >= 0.1.29
- azure-identity
- GitPython
- PyYAML
- requests (for Fabric API calls)
- pyodbc (for SQL Server connections)
- SqlPackage.exe (for warehouse schema deployment)

## Usage Examples

Run from the core directory or adjust paths accordingly:
```bash
# Traditional deployment
python fabric_deploy.py

# Configuration-based deployment
python fabric_deploy.py --config-file ../config/config.yml

# Environment-specific deployment
python fabric_deploy.py --environment prod
```