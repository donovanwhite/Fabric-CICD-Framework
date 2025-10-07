# Documentation

This folder contains comprehensive documentation for the Fabric CI/CD Framework.

## Documents

- **`README.md`** - Main documentation and getting started guide
- **`COMPLETE_GUIDE.md`** - Comprehensive guide with troubleshooting and advanced features

## Getting Started

### Quick Overview

This framework provides a proven approach for deploying Microsoft Fabric items using fabric-cicd v0.1.29:

- **21 supported item types** - Complete coverage of Fabric resources
- **Configuration-based deployment** - New v0.1.29 feature for streamlined operations
- **Enhanced parameterization** - Environment-specific values and advanced substitution
- **Modular architecture** - Organized codebase for maintainability
- **CI/CD integration** - Ready-to-use Azure DevOps pipelines

### Framework Highlights

1. **Use Simple `publish_all_items()` Function**
   - Follow the basic fabric-cicd documentation pattern
   - Avoid complex parameter.yml configurations that cause validation errors
   
2. **NEW: Configuration-Based Deployment (v0.1.29)**
   - Use `deploy_with_config()` for advanced scenarios
   - Centralized configuration with environment-specific settings
   
3. **Let fabric-cicd Handle Subdirectories Natively**
   - Don't flatten repository structures
   - fabric-cicd supports workspace subfolders out of the box
   
4. **Support All 21 Item Types (v0.1.29)**
   - Auto-detect or manually specify item types
   - Includes new ApacheAirflowJob and MountedDataFactory types

5. **Enhanced Parameterization Features**
   - Use `_ALL_` environment key for universal values
   - Environment variable replacement with `$ENV:` prefix
   - Advanced dynamic replacement variables

6. **Use DefaultAzureCredential**
   - Reliable authentication method
   - Works with Azure CLI (`az login`)

## 📁 SUPPORTED REPOSITORY STRUCTURE

```
/<repository-root>
    /<workspace-subfolder>/          # e.g., Migration/
        /<item-name>.<item-type>     # e.g., nb_analysis.Notebook
        /<item-name>.<item-type>     # e.g., data_lake.Lakehouse
    /<workspace-subfolder>/          # e.g., Warehouse/
        /<item-name>.<item-type>     # e.g., analytics_wh.Warehouse
    /README.md                       # Optional files (ignored)
```

## 🛠️ QUICK START

### 1. Environment Setup

#### PyEnv + Virtual Environment (✅ NO ADMIN REQUIRED - USER MODE)
```batch
REM Windows: Run the automated pyenv setup script (no admin privileges needed)
setup_pyenv.bat
```
**✅ USER-LEVEL INSTALLATION** - Perfect for non-admin users or restricted environments
This script will:
- ✅ Install Git if needed (winget or manual download)
- ✅ Install pyenv-win if not available (user-level)
- ✅ Install Python 3.12.10 via pyenv (user-level)
- ✅ Create a virtual environment 'fabric-cicd-venv'
- ✅ Install all dependencies from envsetup/requirements.txt
- ✅ Configure VS Code settings for the environment
- ✅ Verify Python and fabric-cicd version compatibility

### 2. Manual Installation (Alternative)
```bash
pip install fabric-cicd GitPython azure-identity
```

### 3. Authenticate
```bash
az login
```

### 4. Quick Environment Activation

#### For PyEnv Environment:
```batch
REM Activate pyenv virtual environment and run compatibility check
activate_fabric_env_pyenv.bat
```

### 5. Configure Parameters (Optional)
For cross-environment deployments with parameterization:
- See `../config/parameter.yml` for comprehensive examples with real-world values
- Copy and customize patterns that match your infrastructure
- Supports all 19 fabric-cicd v0.1.24 item types

### 6. Deploy
```bash
python fabric_deploy.py \
    --workspace-id "your-workspace-id" \
    --repo-url "https://dev.azure.com/org/project/_git/repo"
```

### 7. Verify
Check your Fabric workspace - all items should be deployed with folder structure preserved!

## 🔧 ENVIRONMENT SETUP GUIDE

### Python Environment Management

This project uses **PyEnv + Virtual Environment** for Python environment management. This approach is:

**Perfect for:**
- ✅ Non-admin users or restricted corporate environments
- ✅ Users who DON'T have administrator privileges
- ✅ Environments where traditional package managers are not allowed
- ✅ Lightweight Python version management needs

**Features:**
- 🪶 Lightweight Python version management
- 🔓 Works in restricted environments  
- 👤 NO administrator privileges required
- 🎛️ Fine-grained Python version control
- 📦 Standard Python tooling (pip, venv)
- 🏢 Perfect for corporate environments
- 📁 All installations in user directories

**Requirements:**
- 📋 Git (auto-installed by setup script if needed)
- � ~50MB disk space for Python installation
- 🔑 User-level write permissions to current directory

#### 🆘 Troubleshooting

**PyEnv Issues:**
- Ensure Git is available (script will install if needed)
- Check user-level write permissions to %USERPROFILE%\.pyenv
- Restart command prompt after pyenv installation
- Run `pyenv versions` to verify Python installation

**PyEnv User-Mode Issues:**
- Ensure Git is installed and accessible (no admin required)
- Check if pyenv-win is in USER PATH (not system PATH)
- All installations go to user directories (%USERPROFILE%\.pyenv)
- Virtual environment created in current directory
- Restart command prompt after pyenv installation
- Run `pyenv versions` to verify installation

**Both Failing:**
- Use manual installation: `pip install fabric-cicd azure-identity PyYAML`
- Ensure Python 3.8+ is installed
- Check your corporate firewall/proxy settings

## �️ ENHANCED ERROR HANDLING & DEPLOYMENT FEATURES

### 🔄 Smart Error Recovery
The deployment script now includes enhanced error handling that automatically recovers from common deployment issues:

- **Connection Permission Errors**: When bulk deployment fails due to connection access issues, the script automatically switches to individual item deployment
- **Item-by-Item Processing**: Continues deploying other items even if some fail due to permissions
- **Detailed Error Reporting**: Provides specific guidance for "User does not have access to the connection" errors
- **Deployment Summary**: Shows comprehensive success/failure breakdown by item type

### 📊 Example Error Handling Output
```
❌ Error during bulk deployment: User does not have access to the connection 'connection_name'
🔄 Switching to individual item deployment...
✅ Notebook 'data_analysis.Notebook' deployed successfully
❌ Lakehouse 'raw_data.Lakehouse' failed: Connection permission required
✅ Warehouse 'analytics_dw.Warehouse' deployed successfully

📊 DEPLOYMENT SUMMARY:
   ✅ Notebooks: 3/4 successful
   ❌ Lakehouses: 0/2 successful (connection permissions required)
   ✅ Warehouses: 1/1 successful
```

### 🛠️ Connection Permission Issues
If you encounter connection permission errors:
1. **Contact your Fabric administrator** to grant access to required connections
2. **Check workspace permissions** - ensure you have Contributor or Admin role
3. **Verify connection exists** in the target workspace
4. **Review item dependencies** - some items may require specific data connections

## �📋 WHAT'S INCLUDED

```
🚀 CORE DEPLOYMENT SCRIPTS
└── fabric_deploy.py              # Comprehensive deployment script with all features

🔧 ENVIRONMENT SETUP
├── setup_pyenv.bat               # Automated pyenv + virtual environment setup
├── activate_fabric_env_pyenv.bat # Quick pyenv environment activation
└── requirements.txt              # Python dependencies (moved to envsetup/)

🛠️  UTILITIES
├── check_python.py              # Environment verification  
└── validate_connections.py      # Connection validation

📋 CONFIGURATION
├── parameter.yml                # Basic parameter file
├── parameter.yml               # Parameter configuration with examples
├── config.yml                   # NEW: v0.1.29 configuration-based deployment
└── azure-pipelines.yml          # Azure DevOps pipeline

🧪 TESTING
└── test_hybrid_deployment.bat   # Test script

📚 DOCUMENTATION
├── README.md                    # Main documentation
├── COMPLETE_GUIDE.md            # Comprehensive guide
└── SOLUTION_SUMMARY.md          # Solution overview
```

## 🔍 TESTING METHODOLOGY

Our solution was developed through extensive testing:

1. **Repository Analysis** - 8 Fabric items in subdirectories discovered
2. **Authentication Testing** - DefaultAzureCredential validation  
3. **Deployment Approaches** - Multiple strategies tested
4. **Error Resolution** - Parameter validation issues solved
5. **Success Verification** - All 8 items deployed successfully

## 💡 KEY LEARNINGS FROM TESTING

### ❌ What Doesn't Work
- Complex parameter.yml files (cause validation errors)
- Flattening repository structures (breaks folder organization)
- Using advanced fabric-cicd configurations (unnecessary complexity)
- REST API hybrid approaches (library is sufficient)

### ✅ What Works
- Simple `publish_all_items(workspace)` function
- Native subdirectory support in fabric-cicd
- Auto-detection of item types from repository
- DefaultAzureCredential authentication
- Minimal configuration approach

## 🎯 USAGE EXAMPLES

### Basic Deployment
```bash
python fabric_deploy.py \
    --workspace-id "eb2f7de1-b2d5-4852-a744-735106d8dfe8" \
    --repo-url "https://dev.azure.com/contoso/FabricProject/_git/analytics"
```

### With Parameterization
```bash
python fabric_deploy.py \
    --workspace-id "your-workspace-id" \
    --repo-url "your-repo-url" \
    --environment PROD
```

### NEW: Configuration-Based Deployment (v0.1.29)
```bash
# Use centralized config file for advanced deployment scenarios
python fabric_deploy.py \
    --config-file "config.yml" \
    --environment prod
```

### Specific Branch
```bash
python fabric_deploy.py \
    --workspace-id "your-workspace-id" \
    --repo-url "your-repo-url" \
    --branch development
```

### Dry Run (Analysis Only)
```bash
python fabric_deploy.py \
    --workspace-id "your-workspace-id" \
    --repo-url "your-repo-url" \
    --dry-run
```

### Specific Item Types
```bash
python fabric_deploy.py \
    --workspace-id "your-workspace-id" \
    --repo-url "your-repo-url" \
    --item-types Notebook Lakehouse
```

## 📊 PARAMETERIZATION EXAMPLES

The included `../config/parameter.yml` demonstrates:

### 🏢 **Real-World Scenarios**
- **Retail Analytics Platform**: Complete DEV/UAT/PROD deployment examples
- **All 21 Item Types**: Comprehensive coverage of fabric-cicd v0.1.29 capabilities
- **Actual Values**: Realistic connection strings, GUIDs, and configurations (sanitized)
- **NEW v0.1.29 Features**: `_ALL_` environment key, `$ENV:` variables, enhanced filters

### 🔧 **Three Configuration Types**
- **`find_replace`**: Simple string replacements across files
- **`key_value_replace`**: JSONPath-based updates for complex configurations  
- **`spark_pool`**: Environment-specific Spark pool management

### 🌍 **Cross-Environment Patterns**
- SQL Server: `server-env.database.windows.net`
- Storage: `accountnameenv.dfs.core.windows.net`
- Event Hub: `namespace-env.servicebus.windows.net`
- APIs: `api-env.company.com`

### 🔒 **Security Best Practices**
- Dynamic item references: `$items.Lakehouse.DataLake.id`
- Workspace variables: `$workspace.id`
- Key Vault integration patterns
- Managed identity considerations

## 🆕 NEW v0.1.29 FEATURES

### Configuration-Based Deployment
The framework now supports the new configuration-based deployment approach introduced in v0.1.29:

```bash
# Create a config.yml file (example provided)
python fabric_deploy.py --config-file config.yml --environment prod
```

**Benefits:**
- **Centralized Configuration**: All settings in one YAML file
- **Environment Management**: Easy environment-specific configurations
- **Advanced Features**: Access to latest fabric-cicd capabilities
- **Built-in Validation**: Configuration validation before deployment

### Enhanced Parameterization

**_ALL_ Environment Key:**
```yaml
find_replace:
  - find_value: "WORKSPACE_ID_PLACEHOLDER"
    replace_value:
      _ALL_: "$workspace.$id"  # Apply to all environments
```

**Environment Variables:**
```yaml
find_replace:
  - find_value: "CONNECTION_STRING_PLACEHOLDER"
    replace_value:
      DEV: "$ENV:dev_connection_string"
      PROD: "$ENV:prod_connection_string"
```

**Enhanced Dynamic Variables:**
- `$workspace.<name>` - Reference specific workspace by name
- `$workspace.<name>.$items.<type>.<name>.$id` - Cross-workspace item references
- Improved file filters with wildcard support

### New Item Types Support
Now supports all **21 item types** including:
- **ApacheAirflowJob** - Apache Airflow workflow definitions
- **MountedDataFactory** - Mounted Azure Data Factory resources
- All existing types with enhanced parameterization support

### Migration from Standard to Configuration-Based Deployment

**Current approach:**
```bash
python fabric_deploy.py --workspace-id "id" --repo-url "url" --parameter-file parameter.yml
```

**New v0.1.29 approach:**
```bash
python fabric_deploy.py --config-file config.yml --environment prod
```

The configuration file consolidates all settings and provides more powerful deployment control.

## 🔧 TROUBLESHOOTING

### Common Issues & Solutions

1. **"No module named 'git'"**
   ```bash
   pip install GitPython
   ```

2. **Authentication Errors**
   ```bash
   az login
   # Verify with: az account show
   ```

3. **No Items Found**
   - Check repository structure matches expected format
   - Ensure items have correct extensions (.Notebook, .Lakehouse, etc.)

4. **Permission Errors**  
   - Verify workspace Admin or Member role
   - Check workspace ID is correct

## 📊 TESTED CONFIGURATION

This solution was successfully tested with:
- **Repository:** Azure DevOps Git repository
- **Structure:** 8 items in subdirectories (Migration/, Warehouse/)
- **Items:** 6 Notebooks, 1 Lakehouse, 1 Warehouse
- **Authentication:** DefaultAzureCredential (admin user)
- **Result:** ✅ 100% SUCCESS - All items deployed with folder structure preserved

## 🆘 SUPPORT

If you encounter issues:

1. Run with `--dry-run` first to analyze your repository
2. Check the diagnostic output for item discovery
3. Verify authentication with `az account show`
4. Ensure your repository structure matches the expected format

**Need more help?** 👉 See the **[📖 COMPLETE GUIDE](COMPLETE_GUIDE.md)** for:
- Detailed troubleshooting steps
- Lessons learned from extensive testing
- Advanced scenarios and configurations
- Performance metrics and best practices

## 🎉 SUCCESS METRICS

- ✅ **8/8 items deployed successfully**
- ✅ **Folder structure preserved** (Migration/, Warehouse/)
- ✅ **Authentication working** (DefaultAzureCredential)
- ✅ **Fast deployment** (under 2 minutes)
- ✅ **No manual intervention required**

---

*This solution represents the culmination of extensive testing and troubleshooting to identify the approach that actually works with fabric-cicd library.*
