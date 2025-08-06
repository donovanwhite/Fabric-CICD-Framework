# 🚀 Microsoft Fabric CICD Cross-Region Migration Solution

**A comprehensive, production-ready solution for automated deployment and cross-region migration of Microsoft Fabric workspaces using the fabric-cicd library.**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![Fabric CICD](https://img.shields.io/badge/fabric--cicd-v0.1.23-green)](https://pypi.org/project/fabric-cicd/)
[![Azure](https://img.shields.io/badge/Azure-Compatible-orange)](https://azure.microsoft.com)

## 📖 Table of Contents

- [🎯 Overview](#-overview)
- [✨ Features](#-features)
- [📋 Prerequisites](#-prerequisites)
- [⚡ Quick Start](#-quick-start)
- [🏗️ Architecture](#️-architecture)
- [🔧 Configuration](#-configuration)
- [🚀 Deployment Methods](#-deployment-methods)
- [💡 Usage Examples](#-usage-examples)
- [🌍 Cross-Region Migration](#-cross-region-migration)
- [🔐 Security & Best Practices](#-security--best-practices)
- [🔍 Troubleshooting](#-troubleshooting)
- [📚 Advanced Scenarios](#-advanced-scenarios)
- [🆘 Support](#-support)

---

## 🎯 Overview

This solution provides automated deployment and cross-region migration capabilities for Microsoft Fabric workspaces. Built on the official `fabric-cicd` library (v0.1.23), it enables DevOps teams to:

- **Deploy Fabric items** across environments (DEV → STAGING → PROD)
- **Migrate workspaces** between regions for disaster recovery
- **Parameterize configurations** for environment-specific values
- **Automate CI/CD pipelines** with both local and Azure DevOps Git integration
- **Maintain consistency** across multiple environments and regions

### 🎨 What Makes This Special

- **Dual Deployment Modes**: Parameterized (with environment-specific replacements) and Simple (keep original names)
- **Cross-Region Support**: Complete migration workflows between Azure regions
- **Interactive & Automated**: Both command-line automation and interactive menu-driven deployments
- **Comprehensive Examples**: 8 real-world migration scenarios with practical code samples
- **Production Ready**: Error handling, dry-run validation, and enterprise security considerations

---

## ✨ Features

### 🎯 **Deployment Capabilities**
- ✅ **Local Git Repository** deployment with `fabric_deploy_local.py`
- ✅ **Azure DevOps Git** deployment with `fabric_deploy_devops.py`
- ✅ **Parameterized deployments** using `parameter.yml` configuration
- ✅ **Simple deployments** keeping original item names
- ✅ **Selective item deployment** by type (Notebook, Report, Lakehouse, etc.)
- ✅ **Dry-run validation** before actual deployment
- ✅ **Cross-region migration** with environment promotion

### 🔧 **Automation & Integration**
- ✅ **Windows Batch Scripts** for interactive menu-driven deployment
- ✅ **Command-line interfaces** for CI/CD pipeline integration
- ✅ **Migration examples** with 8 real-world scenarios
- ✅ **Azure DevOps** compatible with service principal authentication
- ✅ **Environment variable** support for secrets management

### 📦 **Supported Fabric Items**
- 📓 **Notebooks** (Jupyter/Spark notebooks)
- 📊 **Reports** (Power BI reports)
- 📈 **Dashboards** (Power BI dashboards)  
- 🗄️ **Semantic Models** (Power BI datasets)
- 🏗️ **Lakehouses** (Data lake storage)
- 🏭 **Warehouses** (SQL analytics)
- 🔄 **Data Pipelines** (ETL workflows)
- 💧 **Dataflows** (Data transformation)
- ⚙️ **Environments** (Spark configurations)
- ⚡ **Eventhouses** (Real-time analytics)
- 🌊 **Event Streams** (Streaming data)
- 📝 **KQL Databases** (Kusto analytics)
- 🔍 **KQL Querysets** (Kusto queries)

---

## 📋 Prerequisites

### 1. 💻 **Software Requirements**
```bash
# Required software
Python 3.8+ (Recommended: 3.12.11 for fabric-cicd compatibility)
Git 2.30+
Azure CLI 2.50+

# Optional (for advanced scenarios)
Azure DevOps CLI extension
PowerShell 7+ (for enhanced script support)
```

### 2. 🏢 **Microsoft Fabric Requirements**
- Microsoft Fabric workspace(s) with items to migrate
- Git integration enabled on source workspace
- Target workspace(s) in different region/environment
- Appropriate permissions in both source and target workspaces
- Fabric Premium capacity (for advanced features)

### 3. 🔐 **Authentication & Permissions**
- Azure CLI authenticated: `az login`
- Fabric Workspace Admin or Contributor permissions
- Access to both source and target Fabric workspaces
- Service Principal (for production automation)

### 4. 📦 **Python Environment**
```bash
# Create conda environment (recommended)
conda create -n fabric-cicd python=3.12.11
conda activate fabric-cicd

# Install dependencies
pip install -r requirements.txt
```

---

## ⚡ Quick Start

### 📥 **Step 1: Installation**
```bash
# Clone the repository
git clone <your-repo-url>
cd fabric-cicd-solution

# Setup Python environment
conda create -n fabric-cicd python=3.12.11
conda activate fabric-cicd

# Install dependencies
pip install -r requirements.txt

# Verify installation
python check_python.py
```

### 📂 **Step 2: Repository Structure**
Your repository should follow this structure:
```
C:\source\repos\Fabric\cicd\migrate\fabric\
├── parameter.yml                    # Environment configuration (REQUIRED)
├── fabric_deploy_local.py           # Local deployment script
├── fabric_deploy_devops.py          # Azure DevOps deployment script
├── migration_examples.py            # Example scenarios
├── deploy_from_local.bat            # Interactive local deployment
├── deploy_from_devops.bat           # Interactive DevOps deployment
├── requirements.txt                 # Python dependencies
├── README.md                        # This documentation
│
├── MyNotebook.Notebook/             # Fabric items from Git sync
├── SalesReport.Report/              
├── DataWarehouse.Warehouse/         
├── ETLPipeline.DataPipeline/        
└── ProductionEnv.Environment/       
```

### ⚙️ **Step 3: Configure parameter.yml**
Edit `parameter.yml` with your actual workspace and item IDs:

```yaml
# Replace these placeholder values with real GUIDs
find_replace:
  - find_value: "SOURCE_WORKSPACE_ID_PLACEHOLDER"
    replace_value:
      DEV: "$workspace.id"
      STAGING: "$workspace.id"  
      PROD: "$workspace.id"
    item_type: ["Notebook", "DataPipeline"]

  - find_value: "SOURCE_LAKEHOUSE_ID_PLACEHOLDER"
    replace_value:
      DEV: "$items.Lakehouse.DevLakehouse.id"
      STAGING: "$items.Lakehouse.StagingLakehouse.id"
      PROD: "$items.Lakehouse.ProdLakehouse.id"
    item_type: ["Notebook", "Dataflow"]
```

### 🚀 **Step 4: Deploy**

#### **Option A: Interactive Deployment (Recommended for first-time users)**
```bash
# Local Git repository deployment
deploy_from_local.bat

# Azure DevOps repository deployment  
deploy_from_devops.bat
```

#### **Option B: Command Line Deployment**
```bash
# Dry run validation first
python fabric_deploy_local.py --workspace-id "your-workspace-id" --environment PROD --dry-run

# Actual deployment
python fabric_deploy_local.py --workspace-id "your-workspace-id" --environment PROD

# Deploy specific items only
python fabric_deploy_local.py --workspace-id "your-workspace-id" --environment PROD --items Notebook Report
```

---

## 🏗️ Architecture

### 🔄 **Deployment Flow**
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Source        │    │   Parameter      │    │   Target        │
│   Repository    │───▶│   Processing     │───▶│   Workspace     │
│   (Git)         │    │   (fabric-cicd)  │    │   (Fabric)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                        │
         ▼                        ▼                        ▼
   Git-synced items         Environment-specific      Deployed items
   (.Notebook/, .Report/)   value replacement        with correct config
```

### 🧩 **Component Architecture**

#### **Core Deployment Scripts**
- **`fabric_deploy_local.py`**: Deploys from local Git repositories
- **`fabric_deploy_devops.py`**: Deploys from Azure DevOps Git repositories  
- **`migration_examples.py`**: Provides 8 real-world migration scenarios

#### **Interactive Scripts**  
- **`deploy_from_local.bat`**: Menu-driven local deployment (7 options)
- **`deploy_from_devops.bat`**: Menu-driven DevOps deployment (6 options)

#### **Configuration Files**
- **`parameter.yml`**: Environment-specific parameter configuration
- **`requirements.txt`**: Python dependencies
- **`connection_handling_guide.yml`**: Connection management examples

---

## 🔧 Configuration

### 📝 **parameter.yml Structure**

The `parameter.yml` file has three main sections for different types of parameter replacement:

#### **1. find_replace** - Simple String Replacement
Perfect for replacing workspace IDs, connection strings, and simple values:

```yaml
find_replace:
  # Workspace ID replacement
  - find_value: "SOURCE_WORKSPACE_ID_PLACEHOLDER"
    replace_value:
      DEV: "$workspace.id"      # Dynamic: Uses target workspace ID
      STAGING: "$workspace.id"  
      PROD: "$workspace.id"
    item_type: ["Notebook", "DataPipeline", "Dataflow", "Report"]
    file_path: "**/notebook-content.py"

  # Connection string replacement
  - find_value: "SERVER_CONNECTION_STRING_PLACEHOLDER"
    replace_value:
      DEV: "dev-server.database.windows.net"
      STAGING: "staging-server.database.windows.net"
      PROD: "prod-server.database.windows.net"
    item_type: ["DataPipeline", "Dataflow"]
```

#### **2. key_value_replace** - JSON/YAML Key-Value Replacement
For structured configuration files using JSONPath expressions:

```yaml
key_value_replace:
  # Data pipeline connection configuration
  - find_key: "$.properties.activities[*].typeProperties.connectionString"
    replace_value:
      DEV: "Server=dev-sql.database.windows.net;Database=DevDB"
      STAGING: "Server=staging-sql.database.windows.net;Database=StagingDB"
      PROD: "Server=prod-sql.database.windows.net;Database=ProdDB"
    item_type: "DataPipeline"
    file_path: "**/queryMetadata.json"
```

#### **3. spark_pool** - Environment Spark Pool Configuration
For Environment items that reference custom Spark pools:

```yaml
spark_pool:
  # Production-grade pool configuration
  - instance_pool_id: "SOURCE_LARGE_POOL_ID_PLACEHOLDER"
    replace_value:
      DEV:
        type: "Workspace"     # Pool type: only Workspace pools supported
        name: "DevPool_Small" # Smaller pool for development
      STAGING:
        type: "Workspace"
        name: "StagingPool_Medium"
      PROD:
        type: "Workspace"  
        name: "ProdPool_Large"    # Large pool for production workloads
    item_name: ["ProductionEnvironment", "MLEnvironment"]
```

### 🎯 **Dynamic Variables**
fabric-cicd supports these dynamic replacement variables:

- **`$workspace.id`** - Target workspace ID
- **`$items.<ItemType>.<ItemName>.id`** - Deployed item ID
- **`$items.<ItemType>.<ItemName>.sqlendpoint`** - SQL endpoint (Lakehouse/Warehouse only)  
- **`$items.<ItemType>.<ItemName>.queryserviceuri`** - Query URI (Eventhouse only)

### 🌱 **Environment Variables** (Optional)
```yaml
find_replace:
  - find_value: "CONNECTION_STRING_PLACEHOLDER"
    replace_value:
      DEV: "$ENV:DEV_CONNECTION_STRING"
      PROD: "$ENV:PROD_CONNECTION_STRING"
```

---

## 🚀 Deployment Methods

### 📍 **Method 1: Local Git Repository Deployment**

Deploy directly from your local Git repository containing Fabric items.

#### **Interactive Mode:**
```bash
# Run the interactive menu
deploy_from_local.bat

# Menu options:
# 1. Deploy to DEV environment
# 2. Deploy to STAGING environment  
# 3. Deploy to PROD environment
# 4. Dry run validation
# 5. Deploy specific items only
# 6. Cross-region migration
# 7. Exit
```

#### **Command Line Mode:**
```bash
# Basic parameterized deployment
python fabric_deploy_local.py --workspace-id "workspace-id" --environment PROD

# Simple deployment (keep original names)
python fabric_deploy_local.py --workspace-id "workspace-id" --simple

# Deploy specific item types
python fabric_deploy_local.py --workspace-id "workspace-id" --environment PROD --items Notebook Report Dashboard

# Dry run validation
python fabric_deploy_local.py --workspace-id "workspace-id" --environment PROD --dry-run

# Cross-region migration
python fabric_deploy_local.py --source-workspace "source-id" --target-workspace "target-id" --source-env DEV --target-env PROD
```

### 🌐 **Method 2: Azure DevOps Git Repository Deployment**

Deploy from Azure DevOps Git repositories with automatic repository cloning.

#### **Interactive Mode:**
```bash
# Run the interactive menu  
deploy_from_devops.bat

# Choose deployment type:
# 1. Parameterized Deployment (uses parameter.yml)
# 2. Simple Deployment (keep original names)
# 3. Exit
```

#### **Command Line Mode:**
```bash
# Parameterized deployment from DevOps
python fabric_deploy_devops.py --workspace-id "workspace-id" --target-env PROD --repo-url "https://dev.azure.com/org/project/_git/repo" --branch main

# Simple deployment from DevOps
python fabric_deploy_devops.py --workspace-id "workspace-id" --simple --repo-url "https://dev.azure.com/org/project/_git/repo" --branch main

# Deploy specific items
python fabric_deploy_devops.py --workspace-id "workspace-id" --target-env PROD --repo-url "repo-url" --branch main --items Lakehouse Warehouse

# Dry run validation
python fabric_deploy_devops.py --workspace-id "workspace-id" --target-env DEV --repo-url "repo-url" --branch develop --dry-run
```

### 🎯 **Method 3: Migration Examples**

Use pre-built scenarios for common migration patterns.

#### **Command Line Mode:**
```bash
# Analytics workload migration
python migration_examples.py --scenario 1 --workspace-id "workspace-id" --target-env PROD

# Data engineering migration with specific items
python migration_examples.py --scenario 2 --workspace-id "workspace-id" --target-env STAGING --items Notebook DataPipeline Lakehouse

# Simple migration keeping original names
python migration_examples.py --scenario 7 --workspace-id "workspace-id" --simple --items Notebook Report

# Real-time analytics migration
python migration_examples.py --scenario 3 --workspace-id "workspace-id" --target-env PROD --items Eventhouse Eventstream

# Disaster recovery setup
python migration_examples.py --scenario 5 --workspace-id "dr-workspace-id" --target-env PROD

# Dry run validation
python migration_examples.py --scenario 1 --workspace-id "workspace-id" --target-env DEV --dry-run
```

#### **Interactive Mode:**
```bash
# Run interactive scenario selection
python migration_examples.py

# Available scenarios:
# 1. Analytics Workload Migration
# 2. Data Engineering Pipeline Migration  
# 3. Real-Time Analytics Migration
# 4. Phased Migration Strategy
# 5. Disaster Recovery Setup
# 6. Multi-Region Compliance Deployment
# 7. Simple Migration (Keep Original Names)
# 8. Development Pipeline (DEV→STAGING→PROD)
```

---

## 💡 Usage Examples

### 🎯 **Common Deployment Patterns**

#### **1. Standard Environment Promotion**
```bash
# Deploy to DEV for testing
python fabric_deploy_local.py --workspace-id "dev-workspace-id" --environment DEV --dry-run
python fabric_deploy_local.py --workspace-id "dev-workspace-id" --environment DEV

# Promote to STAGING  
python fabric_deploy_local.py --workspace-id "staging-workspace-id" --environment STAGING

# Deploy to PROD
python fabric_deploy_local.py --workspace-id "prod-workspace-id" --environment PROD
```

#### **2. Selective Item Deployment**
```bash
# Deploy only data engineering items
python fabric_deploy_local.py --workspace-id "workspace-id" --environment PROD --items Notebook DataPipeline Environment Lakehouse

# Deploy only analytics items
python fabric_deploy_local.py --workspace-id "workspace-id" --environment PROD --items Report Dashboard SemanticModel

# Deploy only storage items
python fabric_deploy_local.py --workspace-id "workspace-id" --environment PROD --items Lakehouse Warehouse
```

#### **3. Azure DevOps Integration**
```bash
# Deploy from feature branch
python fabric_deploy_devops.py --workspace-id "dev-workspace-id" --target-env DEV --repo-url "https://dev.azure.com/org/project/_git/repo" --branch feature/new-reports

# Deploy from release branch  
python fabric_deploy_devops.py --workspace-id "staging-workspace-id" --target-env STAGING --repo-url "https://dev.azure.com/org/project/_git/repo" --branch release/v1.2

# Deploy from main branch to production
python fabric_deploy_devops.py --workspace-id "prod-workspace-id" --target-env PROD --repo-url "https://dev.azure.com/org/project/_git/repo" --branch main
```

### 📊 **Real-World Scenarios**

#### **Scenario 1: Analytics Migration**
Migrate complete analytics workload including data lake, warehouse, and reports:
```bash
python migration_examples.py --scenario 1 --workspace-id "33333333-3333-3333-3333-333333333333" --target-env PROD --items Lakehouse Warehouse SemanticModel Report Dashboard
```

#### **Scenario 2: Data Engineering Pipeline**
Deploy data processing notebooks and pipelines:
```bash
python migration_examples.py --scenario 2 --workspace-id "22222222-2222-2222-2222-222222222222" --target-env STAGING --items Notebook DataPipeline Environment Lakehouse
```

#### **Scenario 3: Disaster Recovery**
Set up disaster recovery environment:
```bash
python migration_examples.py --scenario 5 --workspace-id "44444444-4444-4444-4444-444444444444" --target-env PROD
```

---

## 🌍 Cross-Region Migration

Cross-region migration enables you to move Fabric workspaces between Azure regions for disaster recovery, compliance, or performance optimization.

### 🎯 **Migration Process**

#### **1. Source Workspace Preparation**
```bash
# Ensure Git integration is enabled
# Commit all items to Git repository
# Export any manual configurations
```

#### **2. Target Region Setup** 
```bash
# Create target workspace in new region
# Configure appropriate capacity/SKU
# Set up networking and security
```

#### **3. Parameter Configuration**
Update `parameter.yml` for regional differences:
```yaml
find_replace:
  # Regional API endpoints
  - find_value: "https://api.source-region.example.com"
    replace_value:
      DEV: "https://api.dev-region.example.com"
      STAGING: "https://api.staging-region.example.com" 
      PROD: "https://api.prod-region.example.com"

  # Regional storage accounts
  - find_value: "sourcestorageaccount"
    replace_value:
      DEV: "devstorageaccount"
      STAGING: "stagingstorageaccount"
      PROD: "prodstorageaccount"
```

#### **4. Execute Migration**
```bash
# Cross-region migration using local deployment
python fabric_deploy_local.py \
  --source-workspace "source-workspace-id" \
  --target-workspace "target-workspace-id" \
  --source-env DEV \
  --target-env PROD

# Cross-region migration using examples
python migration_examples.py --scenario 1 --workspace-id "target-workspace-id" --target-env PROD
```

### 🗺️ **Regional Considerations**

#### **Network Connectivity**
- Update connection strings for regional endpoints
- Configure VPN/ExpressRoute for hybrid scenarios
- Test latency between regions

#### **Data Residency**
- Ensure compliance with data sovereignty requirements
- Update data processing locations
- Validate regulatory compliance

#### **Performance Optimization**
- Choose regions close to data sources
- Consider Azure region pairing for DR
- Test performance after migration

#### **Cost Optimization**
- Compare pricing between regions
- Optimize for reserved capacity
- Consider data transfer costs

---

## 🔐 Security & Best Practices

### 🔒 **Authentication & Authorization**

#### **Interactive Development**
```bash
# Use Azure CLI for development
az login
az account set --subscription "your-subscription-id"
```

#### **Production Automation**
```bash
# Use Service Principal for CI/CD
az login --service-principal --username "app-id" --password "password" --tenant "tenant-id"

# Environment variables for automation
export AZURE_CLIENT_ID="your-app-id"
export AZURE_CLIENT_SECRET="your-password"  
export AZURE_TENANT_ID="your-tenant-id"
```

#### **Managed Identity** (Recommended for Azure-hosted automation)
```python
from azure.identity import DefaultAzureCredential
credential = DefaultAzureCredential()
```

### 🛡️ **Access Control**

#### **Workspace Permissions**
- **Admin**: Full deployment and configuration access
- **Contributor**: Deploy items but not workspace settings
- **Viewer**: Read-only access for validation

#### **Repository Security**
- Separate repositories per environment  
- Branch protection rules for production
- Code review requirements
- Signed commits for critical changes

#### **Secrets Management**
```yaml
# Use environment variables for secrets
find_replace:
  - find_value: "DATABASE_PASSWORD_PLACEHOLDER"
    replace_value:
      DEV: "$ENV:DEV_DB_PASSWORD"
      PROD: "$ENV:PROD_DB_PASSWORD"
```

### 📋 **Deployment Best Practices**

#### **1. Environment Strategy**
```
Development → Testing → Staging → Production
     ↓           ↓        ↓          ↓
   Dev Region  Test Region  Staging  Prod Region
                                      ↓
                             DR Region (Disaster Recovery)
```

#### **2. Validation Pipeline**
```bash
# Always validate before deployment
python fabric_deploy_local.py --workspace-id "workspace-id" --environment PROD --dry-run

# Check for errors
if [ $? -eq 0 ]; then
  echo "Validation passed, proceeding with deployment"
  python fabric_deploy_local.py --workspace-id "workspace-id" --environment PROD
else
  echo "Validation failed, stopping deployment"
  exit 1
fi
```

#### **3. Backup Strategy**
```bash
# Export current workspace before deployment
az rest --method GET --uri "https://api.fabric.microsoft.com/v1/workspaces/workspace-id/items" > backup-$(date +%Y%m%d).json

# Version control parameter files
git add parameter.yml
git commit -m "Update parameters for PROD deployment $(date)"
git tag "deploy-prod-$(date +%Y%m%d-%H%M%S)"
```

#### **4. Monitoring & Validation**
```bash
# Post-deployment validation
python -c "
import requests
response = requests.get('https://api.fabric.microsoft.com/v1/workspaces/workspace-id/items')
if response.status_code == 200:
    print(f'✅ Workspace accessible, {len(response.json())} items found')
else:
    print(f'❌ Workspace validation failed: {response.status_code}')
"
```

---

## 🔍 Troubleshooting

### 🚨 **Common Issues & Solutions**

#### **Authentication Errors**
```bash
# Issue: Authentication failed
# Solution: Verify Azure CLI login
az account show
az login --scope https://analysis.windows.net/powerbi/api/.default

# Issue: Service principal authentication
# Solution: Check environment variables
echo $AZURE_CLIENT_ID
echo $AZURE_TENANT_ID
# Don't echo client secret for security
```

#### **Import/Dependency Errors**
```bash
# Issue: fabric-cicd not found
# Solution: Install/upgrade fabric-cicd
pip install --upgrade fabric-cicd azure-identity

# Issue: Python version compatibility
# Solution: Check Python version
python --version  # Should be 3.8+ (recommended 3.12.11)

# Issue: Missing dependencies
# Solution: Reinstall requirements
pip install -r requirements.txt --force-reinstall
```

#### **Configuration Errors**
```bash
# Issue: parameter.yml syntax error
# Solution: Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('parameter.yml')); print('✅ YAML is valid')"

# Issue: Missing placeholders
# Solution: Check for required placeholders  
grep -r "PLACEHOLDER" parameter.yml

# Issue: Invalid workspace ID
# Solution: Verify workspace ID format (GUID)
python -c "
import uuid
try:
    uuid.UUID('your-workspace-id')
    print('✅ Valid GUID format')
except ValueError:
    print('❌ Invalid GUID format')
"
```

#### **Repository Structure Issues**
```bash
# Issue: Items not found
# Solution: Verify repository structure
find . -name "*.Notebook" -o -name "*.Report" -o -name "*.Lakehouse"

# Issue: parameter.yml not found
# Solution: Ensure parameter.yml is in repository root
ls -la parameter.yml

# Issue: Git sync issues
# Solution: Check Git integration status in Fabric workspace
```

### 🔧 **Debug Mode**

#### **Enable Verbose Logging**
```bash
# Set debug environment variable
export FABRIC_CICD_DEBUG=true

# Run with debug output
python fabric_deploy_local.py --workspace-id "workspace-id" --environment DEV --dry-run --verbose
```

#### **Validate Configuration**
```bash
# Check configuration script
python validate_connections.py

# Verify environment setup
python check_python.py
```

#### **Test Network Connectivity**
```bash
# Test Fabric API connectivity
curl -H "Authorization: Bearer $(az account get-access-token --scope https://analysis.windows.net/powerbi/api/.default --query accessToken -o tsv)" \
     "https://api.fabric.microsoft.com/v1/workspaces"
```

### 📊 **Performance Optimization**

#### **Large Repository Handling**
```bash
# Deploy specific items only for faster deployment
python fabric_deploy_local.py --workspace-id "workspace-id" --environment PROD --items Notebook Report

# Use shallow Git clone for DevOps deployment
git clone --depth 1 --single-branch --branch main "repo-url"
```

#### **Parallel Deployment**
```bash
# Deploy different item types in parallel (advanced)
python fabric_deploy_local.py --workspace-id "workspace-id" --environment PROD --items Lakehouse Warehouse &
python fabric_deploy_local.py --workspace-id "workspace-id" --environment PROD --items Notebook DataPipeline &
wait  # Wait for all background jobs to complete
```

---

## 📚 Advanced Scenarios

### 🏢 **Enterprise CI/CD Pipeline Integration**

#### **Azure DevOps Pipeline** (azure-pipelines.yml)
```yaml
trigger:
  branches:
    include:
    - main
    - develop
    - release/*

pool:
  vmImage: 'ubuntu-latest'

variables:
  pythonVersion: '3.12'

stages:
- stage: Validate
  displayName: 'Validation Stage'
  jobs:
  - job: ValidateDeployment
    displayName: 'Validate Fabric Deployment'
    steps:
    - task: UsePythonVersion@0
      inputs:
        versionSpec: '$(pythonVersion)'
      displayName: 'Setup Python'
    
    - script: |
        pip install -r requirements.txt
      displayName: 'Install Dependencies'
    
    - task: AzureCLI@2
      displayName: 'Validate Deployment'
      inputs:
        azureSubscription: 'fabric-service-connection'
        scriptType: 'bash'
        scriptLocation: 'inlineScript'
        inlineScript: |
          python fabric_deploy_local.py --workspace-id $(DEV_WORKSPACE_ID) --environment DEV --dry-run

- stage: Deploy
  displayName: 'Deployment Stage'
  dependsOn: Validate
  condition: succeeded()
  jobs:
  - deployment: DeployToProduction
    displayName: 'Deploy to Production'
    environment: 'Production'
    strategy:
      runOnce:
        deploy:
          steps:
          - task: AzureCLI@2
            displayName: 'Deploy Fabric Items'
            inputs:
              azureSubscription: 'fabric-service-connection'
              scriptType: 'bash'
              scriptLocation: 'inlineScript'
              inlineScript: |
                python fabric_deploy_local.py --workspace-id $(PROD_WORKSPACE_ID) --environment PROD
```

#### **GitHub Actions** (.github/workflows/fabric-deploy.yml)
```yaml
name: Fabric CICD Deployment

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

env:
  PYTHON_VERSION: '3.12'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Azure Login
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}
    
    - name: Validate Deployment
      run: |
        python fabric_deploy_local.py --workspace-id ${{ secrets.DEV_WORKSPACE_ID }} --environment DEV --dry-run

  deploy:
    needs: validate
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    environment: production
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: ${{ env.PYTHON_VERSION }}
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Azure Login
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}
    
    - name: Deploy to Production
      run: |
        python fabric_deploy_local.py --workspace-id ${{ secrets.PROD_WORKSPACE_ID }} --environment PROD
```

### 🔄 **Multi-Environment Deployment Strategy**

#### **Environment Configuration Matrix**
```bash
# environments.json
{
  "environments": [
    {
      "name": "DEV",
      "workspace_id": "11111111-1111-1111-1111-111111111111",
      "region": "East US",
      "capacity": "A1",
      "branch": "develop"
    },
    {
      "name": "STAGING", 
      "workspace_id": "22222222-2222-2222-2222-222222222222",
      "region": "Central US",
      "capacity": "A2",
      "branch": "release/staging"
    },
    {
      "name": "PROD",
      "workspace_id": "33333333-3333-3333-3333-333333333333", 
      "region": "West Europe",
      "capacity": "A4",
      "branch": "main"
    }
  ]
}
```

#### **Automated Multi-Environment Deployment**
```bash
#!/bin/bash
# deploy-all-environments.sh

ENVIRONMENTS_FILE="environments.json"

# Read environments and deploy
jq -r '.environments[] | @base64' $ENVIRONMENTS_FILE | while read env; do
  ENV_DATA=$(echo $env | base64 --decode)
  ENV_NAME=$(echo $ENV_DATA | jq -r '.name')
  WORKSPACE_ID=$(echo $ENV_DATA | jq -r '.workspace_id')
  BRANCH=$(echo $ENV_DATA | jq -r '.branch')
  
  echo "🚀 Deploying to $ENV_NAME environment..."
  
  # Validation first
  python fabric_deploy_devops.py \
    --workspace-id "$WORKSPACE_ID" \
    --target-env "$ENV_NAME" \
    --repo-url "$REPO_URL" \
    --branch "$BRANCH" \
    --dry-run
  
  if [ $? -eq 0 ]; then
    echo "✅ Validation passed for $ENV_NAME"
    
    # Actual deployment
    python fabric_deploy_devops.py \
      --workspace-id "$WORKSPACE_ID" \
      --target-env "$ENV_NAME" \
      --repo-url "$REPO_URL" \
      --branch "$BRANCH"
    
    if [ $? -eq 0 ]; then
      echo "✅ $ENV_NAME deployment completed successfully"
    else
      echo "❌ $ENV_NAME deployment failed"
      exit 1
    fi
  else
    echo "❌ $ENV_NAME validation failed"
    exit 1
  fi
done
```

### 🌐 **Multi-Region Disaster Recovery**

#### **Disaster Recovery Configuration**
```yaml
# dr-config.yml
disaster_recovery:
  primary_region: "East US"
  dr_region: "West Europe"
  
  replication_strategy: "active_passive"
  
  primary_workspace: "33333333-3333-3333-3333-333333333333"
  dr_workspace: "44444444-4444-4444-4444-444444444444"
  
  critical_items:
    - "CustomerData.Lakehouse"
    - "SalesReports.Report"
    - "MainWarehouse.Warehouse"
  
  rpo_minutes: 60  # Recovery Point Objective
  rto_minutes: 240 # Recovery Time Objective
```

#### **DR Deployment Script**
```bash
#!/bin/bash
# disaster-recovery-setup.sh

echo "🚨 Setting up Disaster Recovery environment..."

# Deploy all items to DR region
python migration_examples.py \
  --scenario 5 \
  --workspace-id "44444444-4444-4444-4444-444444444444" \
  --target-env PROD

# Validate DR deployment
python fabric_deploy_local.py \
  --workspace-id "44444444-4444-4444-4444-444444444444" \
  --environment PROD \
  --dry-run

echo "✅ Disaster Recovery environment ready"
echo "💡 Test failover procedures and update connection strings as needed"
```

### 🔄 **Blue-Green Deployment Strategy**

#### **Blue-Green Configuration**
```bash
# Blue-green deployment with workspace switching
BLUE_WORKSPACE="55555555-5555-5555-5555-555555555555"
GREEN_WORKSPACE="66666666-6666-6666-6666-666666666666"
CURRENT_ACTIVE="blue"  # or "green"

# Deploy to inactive environment
if [ "$CURRENT_ACTIVE" = "blue" ]; then
  TARGET_WORKSPACE=$GREEN_WORKSPACE
  TARGET_ENV="green"
else
  TARGET_WORKSPACE=$BLUE_WORKSPACE
  TARGET_ENV="blue"
fi

echo "🚀 Deploying to $TARGET_ENV environment ($TARGET_WORKSPACE)..."

# Deploy to inactive environment
python fabric_deploy_local.py \
  --workspace-id "$TARGET_WORKSPACE" \
  --environment PROD

# Validation tests
echo "🔍 Running validation tests..."
python validate_deployment.py --workspace-id "$TARGET_WORKSPACE"

if [ $? -eq 0 ]; then
  echo "✅ Validation passed, ready to switch traffic"
  # Switch traffic (update connection strings, DNS, etc.)
  # This would involve updating your application configuration
else
  echo "❌ Validation failed, keeping current environment active"
  exit 1
fi
```

---

## 🆘 Support

### 📚 **Documentation Resources**
- **[fabric-cicd Library Documentation](https://microsoft.github.io/fabric-cicd/latest/)** - Official library documentation
- **[Microsoft Fabric Documentation](https://learn.microsoft.com/en-us/fabric/)** - Complete Fabric platform guide
- **[Git Integration Guide](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/git-get-started)** - Fabric Git integration setup
- **[Fabric REST API Reference](https://learn.microsoft.com/en-us/rest/api/fabric/)** - API documentation for custom integrations

### 🔧 **Troubleshooting Resources**
- **[Connection Handling Guide](connection_handling_guide.yml)** - Connection management examples
- **[Python Version Fix Guide](PYTHON_VERSION_FIX.md)** - Python compatibility solutions
- **[Complete Setup Guide](COMPLETE_GUIDE.md)** - Comprehensive setup instructions
- **[Migration Guide](FABRIC_MIGRATION_GUIDE.md)** - Step-by-step migration procedures

### 🤝 **Community & Support**
- **Issues**: Report bugs and issues in the repository issue tracker
- **Discussions**: Join community discussions for questions and best practices
- **Contributions**: Submit pull requests for improvements and new features
- **Enterprise Support**: Contact Microsoft Support for enterprise assistance

### 📋 **Quick Support Checklist**

When reporting issues, please include:

1. **Environment Information**
   ```bash
   python --version
   pip list | grep fabric-cicd
   az --version
   ```

2. **Error Messages**
   ```bash
   # Enable debug mode
   export FABRIC_CICD_DEBUG=true
   # Run command and capture full output
   ```

3. **Configuration Files**
   ```bash
   # Sanitized parameter.yml (remove sensitive data)
   # Repository structure: ls -la
   ```

4. **Reproduction Steps**
   - Exact commands used
   - Expected vs actual behavior
   - Any workarounds discovered

---

## 📝 Next Steps

### ✅ **Setup Checklist**

1. **✅ Environment Setup**
   ```bash
   # Install Python 3.12.11
   # Install Azure CLI
   # Create conda environment
   conda create -n fabric-cicd python=3.12.11
   conda activate fabric-cicd
   ```

2. **✅ Install Dependencies**
   ```bash
   pip install -r requirements.txt
   python check_python.py  # Verify installation
   ```

3. **✅ Configure Authentication**
   ```bash
   az login
   az account set --subscription "your-subscription-id"
   ```

4. **✅ Setup Repository Structure**
   ```bash
   # Ensure Fabric items are in correct format
   # Create parameter.yml with your configurations
   # Test with dry-run deployment
   ```

5. **✅ Validate Configuration**
   ```bash
   python fabric_deploy_local.py --workspace-id "test-workspace-id" --environment DEV --dry-run
   ```

6. **✅ Deploy & Test**
   ```bash
   # Deploy to development environment first
   python fabric_deploy_local.py --workspace-id "dev-workspace-id" --environment DEV
   
   # Verify deployment in Fabric workspace
   # Test connections and functionality
   ```

7. **✅ Production Deployment**
   ```bash
   # Deploy to production when ready
   python fabric_deploy_local.py --workspace-id "prod-workspace-id" --environment PROD
   
   # Document configuration for team use
   # Set up CI/CD pipelines for automation
   ```

### 🚀 **Advanced Features to Explore**

- **🔄 Cross-region migration** for disaster recovery
- **⚡ Real-time analytics** deployment with Eventhouses
- **🏭 Data engineering pipelines** with Notebooks and DataPipelines  
- **📊 Analytics workloads** with Reports and Dashboards
- **🌍 Multi-region compliance** deployments
- **🔄 Blue-green deployment** strategies
- **🏢 Enterprise CI/CD** pipeline integration

### 📈 **Scaling Your Solution**

1. **Team Collaboration**: Set up branch protection and code review processes
2. **Multi-Environment**: Expand to dev/test/staging/prod pipeline
3. **Automation**: Integrate with Azure DevOps or GitHub Actions
4. **Monitoring**: Add deployment validation and health checks
5. **Governance**: Implement security policies and compliance checks

**Happy deploying! 🚀**

---

*This solution is built with ❤️ for the Microsoft Fabric community. Star ⭐ this repository if you find it helpful!* 
   - Connection IDs, etc.

### Step 4: Run Deployment

#### Basic Deployment (Single Environment)
```bash
# Dry run first (validation only)
python fabric_deploy.py --workspace-id "your-target-workspace-id" --environment PROD --dry-run

# Actual deployment
python fabric_deploy.py --workspace-id "your-target-workspace-id" --environment PROD
```

#### Cross-Region Migration
```bash
# Migrate from DEV (East US) to PROD (West Europe)
python fabric_deploy.py \
  --source-workspace "dev-workspace-id" \
  --target-workspace "prod-workspace-id" \
  --source-env DEV \
  --target-env PROD
```

#### Deploy Specific Item Types Only
```bash
# Deploy only Notebooks and Reports
python fabric_deploy_local.py --workspace-id "workspace-id" --environment PROD --items Notebook Report
```

## 📂 Repository Structure Explained

### Required Files
- **parameter.yml**: Environment-specific configuration
- **Fabric Items**: Folders ending with `.ItemType` (e.g., `MyNotebook.Notebook/`)

### Fabric Item Types Supported
- `Notebook` - Jupyter/Spark notebooks
- `Report` - Power BI reports
- `Dashboard` - Power BI dashboards  
- `SemanticModel` - Power BI datasets/semantic models
- `Lakehouse` - Fabric lakehouses
- `Warehouse` - Fabric warehouses
- `DataPipeline` - Data integration pipelines
- `Dataflow` - Dataflow Gen2
- `Environment` - Spark environments
- `SQLEndpoint` - SQL analytics endpoints
- And more...

## 🔧 Configuration Details

### parameter.yml Structure
The parameter.yml file has three main sections:

#### 1. find_replace
For simple string replacement across all file types:
```yaml
find_replace:
  - find_value: "source-value"
    replace_value:
      DEV: "dev-value"
      PROD: "prod-value"
    item_type: "Notebook"
```

#### 2. key_value_replace  
For JSON/YAML files using JSONPath:
```yaml
key_value_replace:
  - find_key: "$.properties.connection"
    replace_value:
      DEV: "dev-connection-id"
      PROD: "prod-connection-id"
    item_type: "DataPipeline"
```

#### 3. spark_pool
For Environment spark pool configuration:
```yaml
spark_pool:
  - instance_pool_id: "source-pool-id"
    replace_value:
      DEV:
        type: "Capacity"
        name: "DevPool"
      PROD:
        type: "Capacity" 
        name: "ProdPool"
```

### Dynamic Variables
fabric-cicd supports dynamic replacement:
- `$workspace.id` - Target workspace ID
- `$items.Lakehouse.MyLakehouse.id` - Deployed item ID
- `$items.Lakehouse.MyLakehouse.sqlendpoint` - SQL endpoint

## 🌍 Cross-Region Migration Process

### 1. Source Workspace (Git-Synced)
- Enable Git integration in source workspace
- Commit items to Git repository
- Items appear as folders: `ItemName.ItemType/`

### 2. Parameter Configuration
- Configure environment-specific values in parameter.yml
- Account for regional differences:
  - Connection strings
  - Storage account names
  - API endpoints
  - Capacity pool configurations

### 3. Target Deployment
- Deploy items to target workspace in different region
- fabric-cicd applies environment-specific parameters
- Cross-references between items automatically updated

## 🔍 Troubleshooting

### Common Issues

#### Authentication Errors
```bash
# Verify Azure CLI login
az account show

# Check Fabric permissions
az rest --uri "https://api.fabric.microsoft.com/v1/workspaces/{workspace-id}"
```

#### Import Errors
```bash
# Install/upgrade fabric-cicd
pip install --upgrade fabric-cicd azure-identity

# Check Python version
python --version  # Should be 3.8+
```

#### Parameter File Issues
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('parameter.yml'))"

# Check for required placeholders
grep -r "PLACEHOLDER" parameter.yml
```

#### Repository Structure Issues
- Ensure folders end with `.ItemType` (e.g., `.Notebook`, `.Report`)
- Verify items were committed via Fabric Git sync
- Check parameter.yml is in repository root

### Debug Mode
```bash
# Enable verbose logging
export FABRIC_CICD_DEBUG=true
python fabric_deploy.py --workspace-id "workspace-id" --environment DEV --dry-run
```

## 📚 Advanced Scenarios

### Multiple Environment Deployment
```bash
# Deploy to multiple environments
for env in DEV STAGING PROD; do
  echo "Deploying to $env..."
  python fabric_deploy.py --workspace-id "${env}_WORKSPACE_ID" --environment $env
done
```

### Selective Item Migration
```bash
# Migrate only data items
python fabric_deploy.py --workspace-id "workspace-id" --environment PROD \
  --items Lakehouse Warehouse DataPipeline

# Migrate only reporting items  
python fabric_deploy.py --workspace-id "workspace-id" --environment PROD \
  --items Report Dashboard SemanticModel
```

### Pipeline Integration
```yaml
# Azure DevOps Pipeline example
- task: AzureCLI@2
  displayName: 'Deploy Fabric Items'
  inputs:
    azureSubscription: 'fabric-service-connection'
    scriptType: 'bash'
    scriptLocation: 'inlineScript'
    inlineScript: |
      python fabric_deploy.py \
        --workspace-id $(PROD_WORKSPACE_ID) \
        --environment PROD
```

## 🔐 Security Considerations

### Authentication
- Use service principals for production pipelines
- Avoid storing secrets in parameter.yml
- Use Azure Key Vault for sensitive configuration

### Access Control
- Limit workspace permissions to deployment accounts
- Use separate service principals per environment
- Implement approval gates for production deployments

### Data Protection
- Ensure parameter.yml doesn't contain sensitive data
- Use environment variables for secrets: `$ENV:SECRET_NAME`
- Implement proper Git repository access controls

## 📈 Best Practices

### 1. Repository Organization
- Keep one workspace per Git repository
- Use clear naming: `ProjectName.ItemType/`
- Maintain separate branches for environments

### 2. Parameter Management
- Use dynamic variables when possible: `$workspace.id`
- Group related configurations together
- Document all placeholder replacements

### 3. Deployment Strategy
- Always run dry-run first
- Deploy to DEV → STAGING → PROD
- Validate after each deployment

### 4. Cross-Region Considerations
- Account for regional endpoint differences
- Update connection strings for regional services
- Verify capacity and SKU availability per region
- Test latency and performance post-migration

## 🆘 Support Resources

- [fabric-cicd Documentation](https://microsoft.github.io/fabric-cicd/latest/)
- [Microsoft Fabric Documentation](https://learn.microsoft.com/en-us/fabric/)
- [Git Integration Guide](https://learn.microsoft.com/en-us/fabric/cicd/git-integration/git-get-started)
- [Fabric REST API Reference](https://learn.microsoft.com/en-us/rest/api/fabric/)

## 📝 Next Steps

1. ✅ Install dependencies: `pip install -r requirements.txt`
2. ✅ Configure parameter.yml with your workspace IDs
3. ✅ Run validation: `python fabric_deploy.py --dry-run`
4. ✅ Deploy to target environment
5. ✅ Verify deployment in Fabric workspace
6. ✅ Test connections and functionality
7. ✅ Document your configuration for team use
