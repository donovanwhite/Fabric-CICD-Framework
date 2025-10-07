# Official fabric-cicd v0.1.29 Supported Item Types
# ==================================================
# This file documents the OFFICIAL supported item types in fabric-cicd v0.1.29
# Source: https://microsoft.github.io/fabric-cicd/0.1.29/#supported-item-types
# 
# IMPORTANT: Only these 21 item types are officially supported.
# Other item types you may see referenced elsewhere are NOT supported.

# =============================================================================
# OFFICIALLY SUPPORTED ITEM TYPES (21 total)
# =============================================================================

SUPPORTED_ITEM_TYPES = [
    # Core workspace items
    'DataPipeline',           # Data integration pipelines
    'Environment',            # Spark environments and configurations  
    'Notebook',               # Jupyter/Synapse notebooks
    'Report',                 # Power BI reports
    'SemanticModel',          # Power BI semantic models (datasets)
    
    # Data storage items
    'Lakehouse',              # Delta Lake storage
    'Warehouse',              # SQL data warehouse
    'SQLDatabase',            # SQL databases
    'MirroredDatabase',       # Mirrored database connections
    
    # Data processing items  
    'Dataflow',               # Data transformation flows
    'CopyJob',                # Data copy operations
    'VariableLibrary',        # Shared variables and parameters
    
    # Real-time analytics items
    'Eventhouse',             # Real-time event processing
    'KQLDatabase',            # Kusto Query Language databases
    'KQLQueryset',            # KQL query collections
    'KQLDashboard',           # Real-time dashboards
    'Eventstream',            # Streaming data processing
    'Reflex',                 # Real-time activators/triggers
    
    # API and integration items
    'GraphQLApi',             # GraphQL API endpoints
    'ApacheAirflowJob',       # Apache Airflow workflows (NEW in v0.1.29)
    'MountedDataFactory',     # Mounted Azure Data Factory (NEW in v0.1.29)
]

# =============================================================================
# ITEM TYPES NOT SUPPORTED (Common misconceptions)
# =============================================================================

NOT_SUPPORTED_ITEM_TYPES = [
    'MLModel',                # ❌ Machine Learning models - NOT supported
    'MLExperiment',           # ❌ ML experiments - NOT supported  
    'SparkJobDefinition',     # ❌ Spark job definitions - NOT supported
    'Dashboard',              # ❌ Classic dashboards - use KQLDashboard instead
    'Dataset',                # ❌ Legacy term - use SemanticModel instead
]

# =============================================================================
# ITEM TYPE MAPPING FOR DISCOVERY
# =============================================================================
# File extensions to item type mapping for repository analysis

FABRIC_EXTENSIONS = {
    # Core items
    '.Notebook': 'Notebook',
    '.DataPipeline': 'DataPipeline', 
    '.Environment': 'Environment',
    '.Report': 'Report',
    '.SemanticModel': 'SemanticModel',
    
    # Storage items
    '.Lakehouse': 'Lakehouse',
    '.Warehouse': 'Warehouse', 
    '.SQLDatabase': 'SQLDatabase',
    '.MirroredDatabase': 'MirroredDatabase',
    
    # Processing items
    '.Dataflow': 'Dataflow',
    '.CopyJob': 'CopyJob',
    '.VariableLibrary': 'VariableLibrary',
    
    # Real-time items
    '.Eventhouse': 'Eventhouse',
    '.KQLDatabase': 'KQLDatabase',
    '.KQLQueryset': 'KQLQueryset', 
    '.KQLDashboard': 'KQLDashboard',
    '.Eventstream': 'Eventstream',
    '.Reflex': 'Reflex',
    
    # API items
    '.GraphQLApi': 'GraphQLApi',
    '.ApacheAirflowJob': 'ApacheAirflowJob',
    '.MountedDataFactory': 'MountedDataFactory',
}

# =============================================================================
# VALIDATION FUNCTION
# =============================================================================

def validate_item_type(item_type):
    """Validate if an item type is officially supported"""
    if item_type in SUPPORTED_ITEM_TYPES:
        return True, f"✅ {item_type} is officially supported"
    elif item_type in NOT_SUPPORTED_ITEM_TYPES:
        return False, f"❌ {item_type} is NOT supported in fabric-cicd v0.1.29"
    else:
        return False, f"❓ {item_type} is not recognized - check official documentation"

# =============================================================================
# USAGE EXAMPLES
# =============================================================================

if __name__ == "__main__":
    print("Official fabric-cicd v0.1.29 Supported Item Types")
    print("=" * 50)
    
    print(f"\n✅ SUPPORTED ({len(SUPPORTED_ITEM_TYPES)} total):")
    for item_type in SUPPORTED_ITEM_TYPES:
        print(f"   - {item_type}")
    
    print(f"\n❌ NOT SUPPORTED ({len(NOT_SUPPORTED_ITEM_TYPES)} total):")
    for item_type in NOT_SUPPORTED_ITEM_TYPES:
        print(f"   - {item_type}")
    
    print(f"\n📊 Total officially supported: {len(SUPPORTED_ITEM_TYPES)}")
    print("📚 Source: https://microsoft.github.io/fabric-cicd/0.1.29/#supported-item-types")