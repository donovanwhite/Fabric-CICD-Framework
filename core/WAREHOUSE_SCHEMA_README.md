# Warehouse Schema Deployment

This directory contains the enhanced Fabric CI/CD framework with **Warehouse Schema Deployment** capabilities.

## 🚀 NEW CAPABILITY: Database Schema Deployment

The framework now supports deploying database schema objects (tables, views, stored procedures, etc.) to Fabric Warehouses, in addition to the existing Fabric item deployment.

### 🎯 Problem Solved

**Before**: fabric-cicd only deployed Fabric Warehouse *items* but not the database schema objects inside them.

**Now**: Complete end-to-end deployment of both Fabric items AND database schema objects.

## 📁 New Files

### Core Schema Deployment
- **`warehouse_schema_deploy.py`** - Core module for warehouse schema deployment
- **`enhanced_fabric_deploy.py`** - Enhanced deployment script with integrated schema support

### Dependencies
- Updated **`requirements.txt`** with SQL connectivity libraries (pyodbc, lxml)

## 🛠️ Prerequisites

### 1. Install Enhanced Dependencies
```bash
pip install -r ../envsetup/requirements.txt
```

### 2. SQL Server ODBC Driver
Download and install the Microsoft ODBC Driver 18 for SQL Server:
- **Windows**: https://go.microsoft.com/fwlink/?linkid=2187214
- **Linux**: https://docs.microsoft.com/en-us/sql/connect/odbc/linux-mac/installing-the-microsoft-odbc-driver-for-sql-server

### 3. Azure Authentication
Ensure you have access to the Fabric Warehouse with appropriate permissions:
- **Fabric Admin** or **Workspace Admin** role
- **SQL permissions** in the target warehouse (db_owner or equivalent)

## 🚀 Usage Examples

### Deploy Everything (Fabric Items + Schemas)
```bash
python enhanced_fabric_deploy.py \
    --workspace-id "your-workspace-id" \
    --repo-url "https://dev.azure.com/yourorg/YourProject/_git/YourRepo" \
    --deploy-schemas
```

### Deploy Only Schemas to Existing Warehouses
```bash
python enhanced_fabric_deploy.py \
    --workspace-id "your-workspace-id" \
    --local-path "./my-fabric-repo" \
    --deploy-schemas-only \
    --warehouse-name "my_warehouse"
```

### Dry Run with Schema Validation
```bash
python enhanced_fabric_deploy.py \
    --workspace-id "your-workspace-id" \
    --repo-url "https://dev.azure.com/yourorg/YourProject/_git/YourRepo" \
    --deploy-schemas \
    --dry-run
```

### Deploy from SQL Project Files
```python
from warehouse_schema_deploy import deploy_warehouse_schema_from_sqlproj

success = deploy_warehouse_schema_from_sqlproj(
    warehouse_name="my_warehouse",
    workspace_id="your-workspace-id", 
    sqlproj_path="./database/MyWarehouse.sqlproj"
)
```

## 📂 Supported Repository Structures

### Option 1: SQL Project Files
```
YourRepo/
├── fabric_items/
│   └── MyWarehouse.Warehouse/
└── database/
    ├── MyWarehouse.sqlproj
    ├── Tables/
    │   ├── Customer.sql
    │   └── Orders.sql
    ├── Views/
    │   └── CustomerOrders.sql
    └── StoredProcedures/
        └── GetCustomerData.sql
```

### Option 2: SQL Files in Directories
```
YourRepo/
├── MyWarehouse.Warehouse/
└── sql/
    ├── tables/
    │   ├── Customer.sql
    │   └── Orders.sql
    ├── views/
    │   └── CustomerOrders.sql
    └── procedures/
        └── GetCustomerData.sql
```

### Option 3: Mixed Structure
```
YourRepo/
├── warehouses/
│   └── MyWarehouse.Warehouse/
├── database/
│   └── schema.sql
└── migrations/
    ├── 001_create_tables.sql
    └── 002_create_views.sql
```

## 🎯 Supported Schema Objects

| Object Type | Supported | Notes |
|-------------|-----------|-------|
| **Tables** | ✅ | Including constraints, indexes |
| **Views** | ✅ | Standard and indexed views |
| **Stored Procedures** | ✅ | All parameter types |
| **Functions** | ✅ | Scalar and table-valued |
| **Schemas** | ✅ | Custom database schemas |
| **User-defined Types** | ✅ | Custom data types |
| **Synonyms** | ✅ | Object aliases |
| **Triggers** | ✅ | Table and view triggers |
| **Indexes** | ✅ | Clustered and non-clustered |

## 🔄 Deployment Workflow

1. **Deploy Fabric Items** - Creates Warehouse items in Fabric
2. **Wait for Readiness** - Ensures Warehouse is available for connections  
3. **Parse Schema Objects** - Analyzes SQL projects/files
4. **Calculate Dependencies** - Orders objects for deployment
5. **Deploy Schema Objects** - Executes SQL against Warehouse
6. **Validate Deployment** - Confirms successful deployment

## 🔧 Configuration Options

### Connection String Customization
```python
from warehouse_schema_deploy import WarehouseSchemaDeployer

# Custom connection string
deployer = WarehouseSchemaDeployer(
    warehouse_name="my_warehouse",
    workspace_id="workspace_id",
    connection_string="Driver={ODBC Driver 18 for SQL Server};Server=custom.server;..."
)
```

### Authentication Methods
- **Azure AD Default** (recommended) - Uses current user credentials
- **Service Principal** - For CI/CD pipelines
- **SQL Authentication** - If enabled on warehouse

## 🚨 Error Handling

### Common Issues and Solutions

**Connection Failed**
```
❌ Failed to connect to warehouse my_warehouse: [Error details]
```
- Verify warehouse name and workspace ID
- Check Azure AD authentication
- Ensure ODBC driver is installed

**SQL Syntax Errors**
```
❌ Failed to deploy Table Customer: Incorrect syntax near 'CONSTRAINT'
```
- Review SQL syntax for Fabric Warehouse compatibility
- Check for unsupported SQL Server features

**Dependency Issues**
```
❌ Failed to deploy View CustomerOrders: Invalid object name 'Customer'
```
- Ensure dependent objects are deployed first
- Check object names and schema references

## 🔍 Debugging and Logging

### Enable Detailed Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Your deployment code here
```

### Dry Run for Validation
```bash
python enhanced_fabric_deploy.py --dry-run --deploy-schemas
```

### Connection Testing
```python
from warehouse_schema_deploy import WarehouseSchemaDeployer

deployer = WarehouseSchemaDeployer("warehouse_name", "workspace_id")
if deployer.connect():
    print("✅ Connection successful!")
    deployer.disconnect()
else:
    print("❌ Connection failed!")
```

## 🔄 CI/CD Integration

### Azure DevOps Pipeline
```yaml
- script: |
    python core/enhanced_fabric_deploy.py \
      --workspace-id "$(FABRIC_WORKSPACE_ID)" \
      --repo-url "$(Build.Repository.Uri)" \
      --branch "$(Build.SourceBranchName)" \
      --deploy-schemas
  displayName: 'Deploy Fabric Items and Warehouse Schemas'
  env:
    AZURE_CLIENT_ID: $(AZURE_CLIENT_ID)
    AZURE_CLIENT_SECRET: $(AZURE_CLIENT_SECRET) 
    AZURE_TENANT_ID: $(AZURE_TENANT_ID)
```

### GitHub Actions
```yaml
- name: Deploy Fabric and Schemas
  run: |
    python core/enhanced_fabric_deploy.py \
      --workspace-id "${{ secrets.FABRIC_WORKSPACE_ID }}" \
      --repo-url "${{ github.repositoryUrl }}" \
      --deploy-schemas
  env:
    AZURE_CLIENT_ID: ${{ secrets.AZURE_CLIENT_ID }}
    AZURE_CLIENT_SECRET: ${{ secrets.AZURE_CLIENT_SECRET }}
    AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
```

## 📊 Best Practices

### 1. Schema Object Organization
- Use consistent naming conventions
- Group related objects in directories
- Include dependency documentation

### 2. SQL Code Quality
- Write Fabric Warehouse compatible SQL
- Use parameterized queries
- Include proper error handling

### 3. Deployment Strategy
- Always test with `--dry-run` first
- Deploy to dev/test before production
- Maintain rollback scripts

### 4. Security
- Use Azure AD authentication when possible
- Avoid hard-coded connection strings
- Implement least privilege access

## 🆘 Support and Troubleshooting

### Check System Requirements
```bash
python core/warehouse_schema_deploy.py
```

### Validate Dependencies
```bash
python -c "import pyodbc; print('✅ pyodbc available')"
python -c "import lxml; print('✅ lxml available')"
```

### Test Connectivity
```bash
python enhanced_fabric_deploy.py --workspace-id "your-id" --local-path "." --deploy-schemas-only --warehouse-name "your-warehouse" --dry-run
```

---

## 🎉 Benefits

✅ **Complete CI/CD Solution** - Deploy both Fabric items AND database schemas  
✅ **Automated Workflow** - No manual schema deployment steps  
✅ **Dependency Management** - Correct deployment order automatically calculated  
✅ **Error Resilience** - Comprehensive error handling and rollback capabilities  
✅ **Multi-format Support** - Works with SQL projects, directories, and individual files  
✅ **Production Ready** - Tested and validated deployment process  

Your Fabric CI/CD framework is now **enterprise-ready** with complete database lifecycle management! 🚀