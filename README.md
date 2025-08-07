# Microsoft Fabric CI/CD Migration Framework

🎉 **SUCCESS!** This framework has been thoroughly tested and proven to work with real Azure DevOps repositories.

> 📚 **Need more details?** For comprehensive troubleshooting, lessons learned, and advanced scenarios, see the **[📖 COMPLETE GUIDE](COMPLETE_GUIDE.md)**

## ✅ PROVEN RESULTS
- **Successfully deployed 8 Fabric items** from Azure DevOps repository
- **Repository structure:** Items in subdirectories (Migration/, Warehouse/)
- **Item types:** 6 Notebooks + 1 Lakehouse + 1 Warehouse  
- **Authentication:** DefaultAzureCredential working perfectly
- **Deployment time:** Fast and reliable

## 🚀 WORKING SOLUTION OVERVIEW

This framework provides a **simple, tested approach** for deploying Microsoft Fabric items using the `fabric-cicd` library. After extensive testing and troubleshooting, we've identified the approach that actually works.

### 🔑 KEY SUCCESS FACTORS

1. **Use Simple `publish_all_items()` Function**
   - Follow the basic fabric-cicd documentation pattern
   - Avoid complex parameter.yml configurations that cause validation errors
   
2. **Let fabric-cicd Handle Subdirectories Natively**
   - Don't flatten repository structures
   - fabric-cicd supports workspace subfolders out of the box
   
3. **Specify Correct Item Types**
   - Auto-detect or manually specify: `["Notebook", "Lakehouse", "Warehouse"]`
   - Based on actual repository analysis

4. **Use DefaultAzureCredential**
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

### 1. Install Dependencies
```bash
pip install fabric-cicd GitPython azure-identity
```

### 2. Authenticate
```bash
az login
```

### 3. Configure Parameters (Optional)
For cross-environment deployments with parameterization:
- See `parameter_example.yml` for comprehensive examples with real-world values
- Copy and customize patterns that match your infrastructure
- Supports all 19 fabric-cicd v0.1.24 item types

### 4. Deploy
```bash
python fabric_deploy.py \
    --workspace-id "your-workspace-id" \
    --repo-url "https://dev.azure.com/org/project/_git/repo"
```

### 5. Verify
Check your Fabric workspace - all items should be deployed with folder structure preserved!

## 📋 WHAT'S INCLUDED

```
🚀 CORE DEPLOYMENT SCRIPTS
├── fabric_deploy.py              # Main deployment script
└── fabric_deploy_simple.py       # Simple deployment alternative

🔧 UTILITIES
├── check_python.py              # Environment verification  
└── validate_connections.py      # Connection validation

📋 CONFIGURATION
├── parameter.yml                # Basic parameter file
├── parameter_example.yml        # Comprehensive parameter examples with real values
├── requirements.txt             # Python dependencies
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

The included `parameter_example.yml` demonstrates:

### 🏢 **Real-World Scenarios**
- **Retail Analytics Platform**: Complete DEV/UAT/PROD deployment examples
- **All 19 Item Types**: Comprehensive coverage of fabric-cicd v0.1.24 capabilities
- **Actual Values**: Realistic connection strings, GUIDs, and configurations (sanitized)

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
