# Complete Fabric CI/CD Guide

This comprehensive guide covers all aspects of using the fabric-cicd library for Microsoft Fabric workspaces.

## 📁 Repository Structure

```
Fabric/cicd/migrate/
├── fabric_cicd_setup.py           # Core Python wrapper class
├── fabric_deploy.py               # CLI deployment tool
├── validate_connections.py        # Connection analysis tool
├── parameter.yml                  # Configuration template
├── migration_examples.py          # Usage examples
├── existing_workspace_guide.md    # Existing workspace deployment guide
├── requirements.txt               # Python dependencies
├── setup.bat                      # Windows setup script
├── check_python.py               # Python version compatibility checker
├── PYTHON_VERSION_FIX.md          # Python 3.13 compatibility solutions
├── README.md                      # Basic overview
├── FABRIC_MIGRATION_GUIDE.md      # Migration scenarios
└── COMPLETE_GUIDE.md              # This comprehensive guide
```

## 🚀 Quick Start

### 1. Python Version Requirements
**⚠️ IMPORTANT:** The `fabric-cicd` library requires Python **3.9 to 3.12** (not 3.13+)

```cmd
# Check your Python version
python --version

# If you have Python 3.13+, you have these options:
```

**Option A: Use Python 3.12 with pyenv (Recommended)**
```cmd
# Install pyenv for Windows (if not already installed)
# https://github.com/pyenv-win/pyenv-win

# Install and use Python 3.12
pyenv install 3.12.7
pyenv local 3.12.7
python --version  # Should show Python 3.12.7
```

**Option B: Use Conda Environment**
```cmd
# Create conda environment with Python 3.12
conda create -n fabric-cicd python=3.12
conda activate fabric-cicd
python --version  # Should show Python 3.12.x
```

**Option C: Use Python 3.12 Virtual Environment**
```cmd
# If you have Python 3.12 installed separately
py -3.12 -m venv fabric-env
fabric-env\Scripts\activate
python --version  # Should show Python 3.12.x
```

### 2. Installation
```cmd
# Clone repository and navigate to migration folder
cd c:\source\repos\Fabric\cicd\migrate

# Install dependencies (requires Python 3.9-3.12)
pip install -r requirements.txt

# Or run automated setup
setup.bat
```

### 3. Authentication
```cmd
# Azure CLI authentication (recommended)
az login

# Set subscription if needed
az account set --subscription "your-subscription-id"
```

### 4. Basic Deployment
```cmd
# Deploy to existing workspace (most common scenario)
python fabric_deploy.py --workspace-id "your-workspace-guid" --environment PROD

# Dry run validation first
python fabric_deploy.py --workspace-id "your-workspace-guid" --environment DEV --dry-run
```

## 🎯 Deployment Scenarios

### Scenario 1: Deploy to Existing Workspace
**Most common use case** - Deploy to an existing workspace in a different capacity/region:

```cmd
# Update existing items and create new ones
python fabric_deploy.py --workspace-id "existing-workspace-guid" --environment PROD

# Only create new items, don't update existing
python fabric_deploy.py --workspace-id "existing-workspace-guid" --environment PROD --no-update-mode
```

**Behavior:**
- ✅ Items with same names → Updated/replaced
- ✅ Items with different names → Remain unchanged
- ✅ New items → Created alongside existing items
- ✅ Cross-references → Automatically updated to target workspace

### Scenario 2: Cross-Region Migration
Deploy from one region to another with full parameterization:

```cmd
python fabric_deploy.py \
  --source-workspace "source-workspace-guid" \
  --target-workspace "target-workspace-guid" \
  --source-env DEV \
  --target-env PROD
```

### Scenario 3: Specific Item Types
Deploy only certain types of items:

```cmd
python fabric_deploy.py \
  --workspace-id "workspace-guid" \
  --environment PROD \
  --items Notebook Report Lakehouse
```

## 🔧 Configuration

### Parameter.yml Template
The `parameter.yml` file supports multiple configuration patterns:

```yaml
# Environment-specific configurations
DEV:
  find_replace:
    # String replacement patterns
    "dev-storage-account": "prod-storage-account"
    "development": "production"
  
  key_value_replace:
    # JSON/YAML path-based replacement
    - path: "$.properties.connection.serverName"
      value: "prod-sql-server.database.windows.net"
    - path: "$.workspaceId" 
      value: "target-workspace-guid"
  
  spark_pool:
    # Spark environment configuration
    pool_name: "prod-spark-pool"
    min_nodes: 2
    max_nodes: 10

PROD:
  find_replace:
    "staging-resource": "production-resource"
    # Add more production-specific replacements
```

### Connection Handling
Connections require different handling strategies:

#### Fabric-to-Fabric References
```yaml
# Automatically handled by fabric-cicd
find_replace:
  "source-workspace-id": "target-workspace-id"
  "source-lakehouse-name": "target-lakehouse-name"
```

#### External Connections
```yaml
# Manual configuration required
key_value_replace:
  - path: "$.properties.connectionString"
    value: "Server=prod-server;Database=ProdDB;Integrated Security=true"
  - path: "$.properties.connectionId"
    value: "prod-connection-guid"
```

## 🔍 Connection Analysis

Use the connection validator to understand your dependencies:

```cmd
# Analyze all connections in repository
python validate_connections.py

# Generate detailed report
python validate_connections.py --output connections_report.json
```

**Output includes:**
- 🔗 Fabric-to-Fabric references (auto-handled)
- 🌐 External connections (manual setup needed)
- 📊 Connection complexity analysis
- 📝 Deployment recommendations

## 📋 Pre-Deployment Checklist

### For New Workspaces
- [ ] Target workspace created in Fabric
- [ ] Appropriate capacity assigned
- [ ] Workspace permissions configured
- [ ] External connections created (if needed)
- [ ] parameter.yml configured with target environment

### For Existing Workspaces
- [ ] Backup important existing items (if needed)
- [ ] Review connection GUIDs in existing workspace
- [ ] Update parameter.yml with existing connection IDs
- [ ] Test with --dry-run first
- [ ] Choose appropriate --update-mode setting

### Authentication & Permissions
- [ ] Azure CLI authentication completed (`az login`)
- [ ] Fabric workspace read/write permissions
- [ ] Azure subscription access for resources
- [ ] Service principal configured (if using automated pipelines)

## 🛠️ Advanced Usage

### CLI Reference
```cmd
# Complete command reference
python fabric_deploy.py --help

# Key parameters:
--workspace-id       # Target workspace GUID (required for basic deployment)
--environment        # Environment name for parameterization (DEV/STAGING/PROD)
--repository         # Path to git-synced Fabric repository (default: current dir)
--items             # Specific item types to deploy
--dry-run           # Validate without deploying
--update-mode       # Update existing items (default: true)
--no-update-mode    # Only create new items
--use-default-auth  # Use service principal instead of Azure CLI

# Cross-region migration:
--source-workspace   # Source workspace GUID
--target-workspace   # Target workspace GUID  
--source-env        # Source environment name
--target-env        # Target environment name
```

### Python API Usage
```python
from fabric_cicd_setup import FabricCICDMigration

# Initialize migration handler
migration = FabricCICDMigration("path/to/repository")

# Deploy to existing workspace
migration.deploy_to_workspace(
    workspace_id="target-workspace-guid",
    environment="PROD",
    update_existing=True
)

# Cross-region migration
migration.migrate_cross_region(
    source_workspace="source-guid",
    target_workspace="target-guid", 
    source_env="DEV",
    target_env="PROD"
)
```

## 🚨 Troubleshooting

### Common Issues

#### Python Version Compatibility
```
ERROR: Could not find a version that satisfies the requirement fabric-cicd
```
**Solution:**
- fabric-cicd requires Python 3.9-3.12 (not 3.13+)
- Check version: `python --version`
- Install Python 3.12: https://www.python.org/downloads/
- Use pyenv: `pyenv install 3.12.7 && pyenv local 3.12.7`
- Use conda: `conda create -n fabric-cicd python=3.12`

#### Authentication Errors
```
Error: Unable to authenticate to Azure
```
**Solution:**
- Run `az login` to authenticate
- Verify subscription access: `az account show`
- Check workspace permissions in Fabric portal

#### Workspace Not Found
```
Error: Workspace with ID 'xxx' not found
```
**Solution:**
- Verify workspace GUID is correct
- Ensure workspace is in the correct capacity/region
- Check workspace permissions

#### Parameter File Issues
```
Error: Parameter file validation failed
```
**Solution:**
- Validate YAML syntax in parameter.yml
- Ensure all required sections are present
- Check for typos in environment names

#### Connection Failures
```
Error: Connection 'xxx' not found in target workspace
```
**Solution:**
- Create connection in target workspace first
- Update parameter.yml with correct connection GUID
- Use connection validator to identify missing connections

### Validation Commands
```cmd
# Test Azure authentication
az account show

# Validate parameter file syntax
python -c "import yaml; yaml.safe_load(open('parameter.yml'))"

# Check repository structure
python validate_connections.py --validate-only

# Test workspace access
python fabric_deploy.py --workspace-id "your-workspace" --environment DEV --dry-run
```

## 📊 Best Practices

### 1. Environment Strategy
- **DEV**: Development with test data and connections
- **STAGING**: Production-like environment for testing
- **PROD**: Production with live data and connections

### 2. Connection Management
- Create connections in target workspace before deployment
- Use consistent naming conventions across environments
- Document connection dependencies

### 3. Deployment Process
- Always run with `--dry-run` first
- Test in staging environment before production
- Use version control for parameter.yml files
- Monitor deployment logs for errors

### 4. Existing Workspace Deployments
- Understand item replacement behavior
- Backup critical existing items if needed
- Use `--no-update-mode` for additive deployments
- Validate connections after deployment

## 📚 Additional Resources

- [Existing Workspace Guide](existing_workspace_guide.md) - Detailed existing workspace scenarios
- [Migration Examples](migration_examples.py) - Code examples for common patterns
- [Fabric Migration Guide](FABRIC_MIGRATION_GUIDE.md) - Step-by-step migration scenarios
- [Connection Validator](validate_connections.py) - Connection analysis tool
- [Microsoft Fabric Documentation](https://docs.microsoft.com/fabric/) - Official Fabric docs
- [fabric-cicd GitHub](https://github.com/microsoft/fabric-cicd) - Official library repository

## 🆕 What's New

### Latest Features
- ✅ **Existing Workspace Support** - Deploy to existing workspaces with flexible update modes
- ✅ **Connection Validation** - Automated analysis of connection dependencies
- ✅ **Enhanced CLI** - Comprehensive command-line interface with dry-run support
- ✅ **Cross-Region Migration** - Full parameterization for region-to-region deployment
- ✅ **Update Mode Control** - Choose between updating existing items or creating new ones

### Coming Soon
- 🔄 **Rollback Support** - Automated rollback for failed deployments
- 📊 **Deployment Analytics** - Performance metrics and deployment insights
- 🔐 **Enhanced Security** - Advanced authentication and permission validation
- 🌐 **Multi-Tenant Support** - Deploy across multiple tenants and subscriptions

---

💡 **Need Help?** Review the specific guides for your scenario:
- **New to fabric-cicd?** Start with [README.md](README.md)
- **Existing workspace deployment?** See [existing_workspace_guide.md](existing_workspace_guide.md)
- **Cross-region migration?** Check [FABRIC_MIGRATION_GUIDE.md](FABRIC_MIGRATION_GUIDE.md)
- **Connection issues?** Run `python validate_connections.py`
