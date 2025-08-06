# Using Existing Workspaces with fabric-cicd
# ==========================================
# Guide for deploying to existing workspaces in different capacities/regions

## 🎯 Existing Workspace Deployment Scenarios

### ✅ **Scenario 1: Migration to Existing Workspace**
# You have an existing workspace in the target region/capacity
# and want to deploy/update specific items

# Example: Move DEV items to existing PROD workspace
python fabric_deploy.py \
  --workspace-id "existing-prod-workspace-id" \
  --environment PROD \
  --items Notebook DataPipeline  # Deploy specific items only

### ✅ **Scenario 2: Cross-Region Disaster Recovery**
# Deploy to existing DR workspace in different region
# Maintains same functionality with regional configuration

python fabric_deploy.py \
  --source-workspace "primary-workspace-id" \
  --target-workspace "existing-dr-workspace-id" \
  --source-env PROD \
  --target-env PROD  # Same environment, different region

### ✅ **Scenario 3: Capacity Migration** 
# Move from one capacity to another (same or different region)
# Target workspace already exists on new capacity

python fabric_deploy.py \
  --workspace-id "existing-workspace-on-new-capacity" \
  --environment PROD

### ✅ **Scenario 4: Incremental Updates**
# Update specific items in existing workspace
# Perfect for ongoing development and maintenance

python fabric_deploy.py \
  --workspace-id "existing-workspace-id" \
  --environment DEV \
  --items Notebook  # Update only notebooks

## 🔧 Existing Workspace Considerations

### **Item Replacement Behavior**
# fabric-cicd behavior with existing items:
# ✅ Items with SAME NAME: Overwritten/Updated
# ✅ Items with DIFFERENT NAME: Left unchanged  
# ✅ New items: Created alongside existing items

### **Connection Handling in Existing Workspaces**
# When deploying to existing workspace:

# 1. REUSE EXISTING CONNECTIONS ✅
# If connections already exist, use their GUIDs in parameter.yml:

key_value_replace:
  - find_key: "$.properties.connection"
    replace_value:
      PROD: "existing-connection-guid-in-target-workspace"
    item_type: "DataPipeline"

# 2. CREATE NEW CONNECTIONS ⚠️
# If connections don't exist, create them manually first

# 3. UPDATE CONNECTION REFERENCES ✅  
# fabric-cicd updates all item references to use target workspace connections

### **Workspace Reference Updates**
# All workspace references automatically point to target workspace:

find_replace:
  - find_value: "source-workspace-id"
    replace_value:
      PROD: "$workspace.id"  # Target workspace ID (existing)

### **Cross-Item References in Existing Workspace**
# References between items work whether items existed before or are newly deployed:

find_replace:
  - find_value: "source-lakehouse-id"
    replace_value:
      PROD: "$items.Lakehouse.DataLake.id"  # Works for existing or new lakehouse

## 💡 Best Practices for Existing Workspaces

### **1. Pre-Deployment Assessment**
# Before deploying to existing workspace:

# Check existing items to avoid conflicts:
python validate_connections.py

# List current workspace contents (if accessible):
# - Use Fabric UI to review existing items
# - Note any items with same names as your deployment
# - Verify connection objects are available

### **2. Staged Deployment Strategy**
# Deploy incrementally to minimize risk:

# Phase 1: Infrastructure items (won't conflict with reports/notebooks)
python fabric_deploy.py \
  --workspace-id "existing-workspace" \
  --environment PROD \
  --items Lakehouse Warehouse Environment

# Phase 2: Processing items  
python fabric_deploy.py \
  --workspace-id "existing-workspace" \
  --environment PROD \
  --items Notebook DataPipeline Dataflow

# Phase 3: Analytics items
python fabric_deploy.py \
  --workspace-id "existing-workspace" \
  --environment PROD \
  --items SemanticModel Report Dashboard

### **3. Connection Reuse Strategy**
# Leverage existing connections when possible:

# Option A: Reuse existing connections
# 1. List connections in target workspace
# 2. Update parameter.yml with existing connection GUIDs
# 3. Deploy items - they'll use existing connections

# Option B: Create new connections
# 1. Create new connections with different names
# 2. Update parameter.yml with new connection GUIDs
# 3. Deploy items - they'll use new connections

### **4. Backup Strategy**
# Before deploying to existing workspace:
# ✅ Export existing items (if critical)
# ✅ Document current workspace state
# ✅ Test deployment in DEV environment first
# ✅ Use --dry-run to validate configuration

## 🔍 Existing Workspace Validation

### **Pre-Deployment Checklist**
# Before deploying to existing workspace:

# ✅ Confirm workspace ID and access permissions
az rest --uri "https://api.fabric.microsoft.com/v1/workspaces/existing-workspace-id"

# ✅ Verify capacity and region
# Check workspace properties in Fabric admin portal

# ✅ List existing connections (manually via Fabric UI)
# Note connection names and IDs for parameter.yml

# ✅ Review existing items for naming conflicts
# Items with same names will be overwritten

# ✅ Test with dry-run
python fabric_deploy.py \
  --workspace-id "existing-workspace-id" \
  --environment PROD \
  --dry-run

### **Post-Deployment Validation**
# After deploying to existing workspace:

# ✅ Verify deployed items work correctly
# Test notebooks, reports, pipelines

# ✅ Check existing items still function
# Ensure non-deployed items weren't affected

# ✅ Validate cross-references
# Confirm items reference correct targets

# ✅ Test data connectivity
# Verify connections to external systems work

## 📝 Example Configuration for Existing Workspace

### **parameter.yml for existing workspace deployment:**
```yaml
find_replace:
  # Update workspace references to existing target workspace
  - find_value: "dev-workspace-id"
    replace_value:
      PROD: "$workspace.id"  # Existing PROD workspace ID

  # Update item references (works for existing or new items)
  - find_value: "dev-lakehouse-id"  
    replace_value:
      PROD: "$items.Lakehouse.MainLakehouse.id"  # Existing or deployed lakehouse

key_value_replace:
  # Use existing connection in target workspace
  - find_key: "$.properties.connection"
    replace_value:
      PROD: "existing-sql-connection-guid"  # Connection already in workspace
    item_type: "DataPipeline"

spark_pool:
  # Use existing capacity pools
  - instance_pool_id: "dev-pool-id"
    replace_value:
      PROD:
        type: "Capacity"
        name: "ExistingProdPool"  # Pool already available in capacity
```

### **Deployment Command:**
```bash
# Deploy to existing workspace
python fabric_deploy.py \
  --workspace-id "existing-prod-workspace-guid" \
  --environment PROD

# Or incremental deployment
python fabric_deploy.py \
  --workspace-id "existing-workspace-guid" \
  --environment PROD \
  --items Notebook Report  # Update specific items only
```

## 🎯 Summary: Existing Workspace Support

fabric-cicd **fully supports existing workspaces** with these capabilities:

✅ **Deploy to any existing workspace** in any capacity/region  
✅ **Reuse existing connections** and infrastructure  
✅ **Update specific items** without affecting others  
✅ **Cross-region migration** to existing workspaces  
✅ **Incremental deployments** for ongoing updates  
✅ **Automatic reference updates** to target workspace context  
✅ **Capacity migration** between existing workspaces  

The key is proper configuration of parameter.yml with existing workspace connection GUIDs and ensuring your authentication has appropriate permissions to the target workspace.
