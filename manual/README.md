# Manual Deployment and Utility Scripts

This folder contains scripts for manual operations, validation, and troubleshooting.

## Files

### Compatibility and Migration
- **`check_compatibility.py`** - Checks system compatibility with fabric-cicd requirements
- **`check_migration.py`** - Validates migration to v0.1.29 and checks for breaking changes
- **`check_python.py`** - Validates Python version and environment setup

### Connection and Validation
- **`validate_connections.py`** - Tests connectivity to Fabric workspaces and Azure services

## Usage

### System Compatibility Check
```bash
python check_compatibility.py
```
Validates:
- Python version compatibility (3.9-3.12)
- Required package availability
- System prerequisites

### Migration Validation
```bash
python check_v29_migration.py
```
Checks:
- Breaking changes in v0.1.29
- Deprecated parameter formats
- New feature compatibility
- Configuration file validity

### Python Environment Check
```bash
python check_python.py
```
Verifies:
- Python version and installation
- Virtual environment status
- Package dependencies

### Connection Validation
```bash
python validate_connections.py
```
Tests:
- Azure authentication
- Fabric workspace connectivity
- Service principal permissions
- Network connectivity

## Troubleshooting Guide

### Common Issues

1. **Authentication Failures**
   - Run `validate_connections.py` to diagnose
   - Check service principal permissions
   - Verify tenant ID and client credentials

2. **Version Compatibility**
   - Use `check_compatibility.py` for system validation
   - Update Python version if needed
   - Upgrade fabric-cicd package

3. **Migration Issues**
   - Run `check_migration.py` before upgrading
   - Review parameter file formats
   - Update deprecated configurations

4. **Network Issues**
   - Check proxy settings
   - Verify firewall rules
   - Test Azure service connectivity

## Manual Deployment Steps

1. **Pre-deployment validation**:
   ```bash
   python check_compatibility.py
   python validate_connections.py
   ```

2. **Configuration validation**:
   ```bash
   python check_migration.py
   ```

3. **Manual deployment**:
   ```bash
   cd ../core
   python fabric_deploy.py
   ```

## Best Practices

- Always run compatibility checks before deployment
- Validate connections in new environments
- Use migration checker when upgrading fabric-cicd versions
- Keep these scripts updated with environment changes