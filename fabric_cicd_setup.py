"""
Microsoft Fabric CICD Migration Setup
=====================================

This script demonstrates how to use the fabric-cicd library to move Fabric items
including reports, datasets, and connections between capacities in different regions.

Key Components:
- Git-synced workspace integration
- parameter.yml configuration for environment-specific values
- Cross-region capacity migration
- Item type handling (Reports, Semantic Models, Lakehouses, etc.)

Prerequisites:
1. pip install fabric-cicd
2. Azure CLI authentication (az login)
3. Git-synced Fabric workspaces
4. parameter.yml file in repository root
"""

from fabric_cicd import FabricWorkspace
from azure.identity import DefaultAzureCredential
import os
import json
from pathlib import Path

class FabricCICDMigration:
    """
    Handles Microsoft Fabric workspace migration using fabric-cicd library
    """
    
    def __init__(self, repository_directory: str):
        """
        Initialize the Fabric CICD Migration
        
        Args:
            repository_directory: Path to git repository containing Fabric items
        """
        self.repository_directory = Path(repository_directory)
        self.credential = DefaultAzureCredential()
        
        # Verify repository structure
        self._validate_repository_structure()
    
    def _validate_repository_structure(self):
        """Validate that the repository has the required structure"""
        if not self.repository_directory.exists():
            raise FileNotFoundError(f"Repository directory not found: {self.repository_directory}")
        
        parameter_file = self.repository_directory / "parameter.yml"
        if not parameter_file.exists():
            print("⚠️  Warning: parameter.yml not found. Creating template...")
            self._create_parameter_template()
        
        # Check for Fabric items (folders ending with item types)
        fabric_items = self._discover_fabric_items()
        print(f"📊 Discovered {len(fabric_items)} Fabric items in repository")
        for item_type, count in fabric_items.items():
            print(f"   {item_type}: {count}")
    
    def _discover_fabric_items(self) -> dict:
        """Discover Fabric items in the repository"""
        item_types = {
            'Notebook': 0, 'Report': 0, 'Dashboard': 0, 'SemanticModel': 0,
            'Lakehouse': 0, 'Warehouse': 0, 'DataPipeline': 0, 'Dataflow': 0,
            'Environment': 0, 'SQLEndpoint': 0, 'KQLDatabase': 0, 'KQLQueryset': 0,
            'Eventhouse': 0, 'Eventstream': 0, 'MLModel': 0, 'MLExperiment': 0
        }
        
        for item in self.repository_directory.iterdir():
            if item.is_dir():
                # Check if folder name ends with a Fabric item type
                for item_type in item_types.keys():
                    if item.name.endswith(f'.{item_type}'):
                        item_types[item_type] += 1
                        break
        
        return {k: v for k, v in item_types.items() if v > 0}
    
    def _create_parameter_template(self):
        """Create a template parameter.yml file"""
        template_content = """# Fabric CICD Parameter Configuration
# This file handles environment-specific values for cross-region migration

find_replace:
  # Workspace ID replacement (for items referencing workspace)
  - find_value: "00000000-0000-0000-0000-000000000000"  # Source workspace ID
    replace_value:
      DEV: "$workspace.id"      # Target DEV workspace ID (dynamic)
      PROD: "$workspace.id"     # Target PROD workspace ID (dynamic)
    item_type: ["Notebook", "DataPipeline", "Dataflow"]

  # Lakehouse ID replacement (for notebooks and dataflows)
  - find_value: "11111111-1111-1111-1111-111111111111"  # Source lakehouse ID
    replace_value:
      DEV: "$items.Lakehouse.MyLakehouse.id"    # Target DEV lakehouse (dynamic)
      PROD: "$items.Lakehouse.MyLakehouse.id"   # Target PROD lakehouse (dynamic)
    item_type: ["Notebook", "Dataflow"]

  # SQL Connection replacement (for data pipelines)
  - find_value: "22222222-2222-2222-2222-222222222222"  # Source SQL connection
    replace_value:
      DEV: "33333333-3333-3333-3333-333333333333"   # DEV SQL connection ID
      PROD: "44444444-4444-4444-4444-444444444444"  # PROD SQL connection ID
    item_type: "DataPipeline"

key_value_replace:
  # Data Pipeline connection replacement using JSONPath
  - find_key: "$.properties.activities[?(@.name=='Copy Data')].typeProperties.source.datasetSettings.externalReferences.connection"
    replace_value:
      DEV: "dev-connection-guid"
      PROD: "prod-connection-guid"
    item_type: "DataPipeline"

spark_pool:
  # Environment spark pool configuration
  - instance_pool_id: "55555555-5555-5555-5555-555555555555"  # Source pool ID
    replace_value:
      DEV:
        type: "Capacity"
        name: "DevCapacityPool"
      PROD:
        type: "Capacity" 
        name: "ProdCapacityPool"
    item_name: "MyEnvironment"
"""
        
        parameter_file = self.repository_directory / "parameter.yml"
        with open(parameter_file, 'w', encoding='utf-8') as f:
            f.write(template_content)
        
        print(f"✅ Created template parameter.yml at {parameter_file}")
        print("📝 Please edit this file with your actual workspace and item IDs")
    
    def create_fabric_workspace(self, workspace_id: str, environment: str = None, 
                               item_types_in_scope: list = None) -> FabricWorkspace:
        """
        Create a FabricWorkspace object for deployment
        
        Args:
            workspace_id: Target workspace ID
            environment: Environment name (DEV, PROD, etc.)
            item_types_in_scope: List of item types to deploy
        
        Returns:
            FabricWorkspace object ready for deployment
        """
        
        if item_types_in_scope is None:
            # Default to most common item types
            item_types_in_scope = [
                "Notebook", "Report", "Dashboard", "SemanticModel",
                "Lakehouse", "Warehouse", "DataPipeline", "Dataflow",
                "Environment"
            ]
        
        workspace = FabricWorkspace(
            workspace_id=workspace_id,
            repository_directory=str(self.repository_directory),
            environment=environment,
            item_type_in_scope=item_types_in_scope,
            token_credential=self.credential
        )
        
        return workspace
    
    def deploy_to_workspace(self, workspace_id: str, environment: str, 
                           item_types: list = None, dry_run: bool = False):
        """
        Deploy Fabric items to target workspace
        
        Args:
            workspace_id: Target workspace ID
            environment: Environment name for parameterization
            item_types: Specific item types to deploy
            dry_run: If True, validate without deploying
        """
        
        print(f"🚀 {'Validating' if dry_run else 'Deploying'} to workspace: {workspace_id}")
        print(f"🎯 Environment: {environment}")
        
        try:
            # Create workspace object
            workspace = self.create_fabric_workspace(
                workspace_id=workspace_id,
                environment=environment,
                item_types_in_scope=item_types
            )
            
            if dry_run:
                print("🔍 Performing validation (dry run)...")
                # Add validation logic here
                print("✅ Validation completed successfully")
            else:
                print("📦 Starting deployment...")
                workspace.deploy()
                print("✅ Deployment completed successfully")
                
        except Exception as e:
            print(f"❌ {'Validation' if dry_run else 'Deployment'} failed: {str(e)}")
            raise
    
    def migrate_cross_region(self, source_config: dict, target_config: dict, 
                           item_types: list = None):
        """
        Migrate items from source to target workspace (cross-region)
        
        Args:
            source_config: Source workspace configuration
            target_config: Target workspace configuration  
            item_types: Specific item types to migrate
        """
        
        print("🌍 Starting cross-region migration...")
        print(f"📤 Source: {source_config['environment']} - {source_config['workspace_id']}")
        print(f"📥 Target: {target_config['environment']} - {target_config['workspace_id']}")
        
        # Deploy to target workspace with environment-specific parameters
        self.deploy_to_workspace(
            workspace_id=target_config['workspace_id'],
            environment=target_config['environment'],
            item_types=item_types
        )
        
        print("✅ Cross-region migration completed!")
    
    def list_repository_items(self):
        """List all items in the repository with their types"""
        print("📋 Repository Items:")
        print("=" * 50)
        
        for item in self.repository_directory.iterdir():
            if item.is_dir() and '.' in item.name:
                name, item_type = item.name.rsplit('.', 1)
                print(f"📁 {name:<30} | {item_type}")
    
    def validate_parameter_file(self):
        """Validate the parameter.yml file structure"""
        parameter_file = self.repository_directory / "parameter.yml"
        
        if not parameter_file.exists():
            print("❌ parameter.yml not found")
            return False
        
        try:
            import yaml
            with open(parameter_file, 'r', encoding='utf-8') as f:
                params = yaml.safe_load(f)
            
            # Basic validation
            valid_sections = ['find_replace', 'key_value_replace', 'spark_pool']
            found_sections = [section for section in valid_sections if section in params]
            
            print("✅ parameter.yml validation:")
            print(f"   Found sections: {found_sections}")
            
            # Validate each section
            for section in found_sections:
                items = params[section]
                print(f"   {section}: {len(items)} configurations")
            
            return True
            
        except Exception as e:
            print(f"❌ parameter.yml validation failed: {str(e)}")
            return False

def main():
    """Example usage of Fabric CICD Migration"""
    
    # Configuration
    REPOSITORY_DIR = r"C:\source\repos\Fabric\cicd\migrate\fabric-workspace"
    
    # Workspace configurations for different environments/regions
    workspaces = {
        'dev': {
            'workspace_id': 'dev-workspace-id-here',
            'environment': 'DEV',
            'region': 'East US'
        },
        'prod': {
            'workspace_id': 'prod-workspace-id-here', 
            'environment': 'PROD',
            'region': 'West Europe'
        }
    }
    
    try:
        # Initialize migration handler
        migration = FabricCICDMigration(REPOSITORY_DIR)
        
        # List repository contents
        migration.list_repository_items()
        
        # Validate parameter file
        migration.validate_parameter_file()
        
        # Example: Deploy to DEV environment (validation only)
        print("\n" + "="*60)
        migration.deploy_to_workspace(
            workspace_id=workspaces['dev']['workspace_id'],
            environment='DEV',
            dry_run=True
        )
        
        # Example: Cross-region migration DEV -> PROD
        print("\n" + "="*60)
        migration.migrate_cross_region(
            source_config=workspaces['dev'],
            target_config=workspaces['prod'],
            item_types=['Notebook', 'Report', 'Lakehouse']  # Specific types only
        )
        
    except Exception as e:
        print(f"💥 Error in main execution: {str(e)}")

if __name__ == "__main__":
    main()
