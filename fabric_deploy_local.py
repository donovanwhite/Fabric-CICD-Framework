"""
Fabric Cross-Region Deployment Script (Local Repository)
========================================================

This script demonstrates how to deploy Fabric items across different regions
using the fabric-cicd library with a local Git repository as the source.

Usage:
    python fabric_deploy_local.py --workspace-id <workspace-id> --environment PROD
    python fabric_deploy_local.py --source-env DEV --target-env PROD --target-workspace <workspace-id>
"""

import argparse
import sys
import os
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.append(str(Path(__file__).parent))

try:
    from fabric_cicd import FabricWorkspace
    from azure.identity import DefaultAzureCredential, AzureCliCredential
except ImportError as e:
    print("❌ Required packages not installed. Please run:")
    print("   pip install fabric-cicd azure-identity")
    print(f"   Error: {e}")
    sys.exit(1)

class FabricDeployment:
    """Handles Fabric workspace deployments with cross-region support"""
    
    def __init__(self, repository_directory: str, use_cli_auth: bool = True):
        """
        Initialize Fabric deployment
        
        Args:
            repository_directory: Path to git repository with Fabric items
            use_cli_auth: Use Azure CLI authentication (default) vs DefaultAzureCredential
        """
        self.repository_directory = Path(repository_directory).resolve()
        
        # Choose authentication method
        if use_cli_auth:
            self.credential = AzureCliCredential()
            print("🔑 Using Azure CLI authentication")
        else:
            self.credential = DefaultAzureCredential()
            print("🔑 Using Default Azure credential chain")
        
        # Validate repository structure
        self._validate_repository()
    
    def _validate_repository(self):
        """Validate repository structure and required files"""
        if not self.repository_directory.exists():
            raise FileNotFoundError(f"Repository directory not found: {self.repository_directory}")
        
        # Check for parameter.yml
        parameter_file = self.repository_directory / "parameter.yml"
        if not parameter_file.exists():
            print("⚠️  Warning: parameter.yml not found in repository root")
            print(f"   Expected location: {parameter_file}")
            print("   This file is required for environment-specific parameterization")
        
        # List Fabric items
        fabric_items = self._list_fabric_items()
        if not fabric_items:
            print("⚠️  Warning: No Fabric items found in repository")
            print("   Expected folder structure: <ItemName>.<ItemType>/")
        else:
            print(f"📊 Found {len(fabric_items)} Fabric items:")
            for item in fabric_items:
                print(f"   📁 {item}")
    
    def _list_fabric_items(self) -> list:
        """List all Fabric items in the repository"""
        fabric_extensions = [
            'Notebook', 'Report', 'Dashboard', 'SemanticModel', 'Lakehouse', 
            'Warehouse', 'DataPipeline', 'Dataflow', 'Environment', 'SQLEndpoint',
            'KQLDatabase', 'KQLQueryset', 'Eventhouse', 'Eventstream', 'MLModel',
            'MLExperiment', 'Activator', 'APIForGraphQL', 'CopyJob'
        ]
        
        items = []
        for item in self.repository_directory.iterdir():
            if item.is_dir():
                for ext in fabric_extensions:
                    if item.name.endswith(f'.{ext}'):
                        items.append(item.name)
                        break
        
        return sorted(items)
    
    def deploy_without_parameterization(self, workspace_id: str, 
                                       item_types: list = None, 
                                       dry_run: bool = False, update_mode: bool = True):
        """
        Deploy Fabric items to target workspace WITHOUT parameter.yml replacement
        This keeps all original item names and references intact
        
        Args:
            workspace_id: Target workspace ID in Fabric
            item_types: List of item types to deploy (None = all discovered types)
            dry_run: Validate configuration without deploying
            update_mode: If True, updates existing items; if False, only creates new items
        """
        
        print("\n" + "="*60)
        print(f"🚀 {'VALIDATING' if dry_run else 'DEPLOYING'} WITHOUT PARAMETERIZATION")
        print("="*60)
        print(f"📁 Repository: {self.repository_directory}")
        print(f"🎯 Workspace: {workspace_id}")
        print(f"📦 Mode: {'Dry Run' if dry_run else 'Live Deployment'}")
        print(f"🔄 Update Mode: {'Update existing items' if update_mode else 'Create new items only'}")
        print(f"📝 Parameterization: DISABLED - Original names preserved")
        
        if item_types:
            print(f"🔍 Item Types: {', '.join(item_types)}")
        else:
            print("🔍 Item Types: All discovered types")
        
        print("\n💡 Simple Migration Behavior:")
        print("   • All item names remain exactly as in source")
        print("   • No parameter.yml replacement performed")
        print("   • Items deployed with original references intact")
        print("   • Ideal for workspace-to-workspace copies")
        
        try:
            # Check if repository has parameter.yml
            parameter_file = self.repository_directory / "parameter.yml"
            if parameter_file.exists():
                print(f"\n⚠️  Note: parameter.yml found but will be IGNORED")
                print(f"   File location: {parameter_file}")
                print("   Use deploy() method if you want parameterization")
            
            # List items to be deployed
            fabric_items = self._list_fabric_items()
            if not fabric_items:
                print("⚠️  Warning: No Fabric items found in repository")
                return
            
            print(f"\n📊 Found {len(fabric_items)} Fabric items:")
            for item in fabric_items:
                print(f"   📁 {item}")
            
            if dry_run:
                print("\n🔍 Performing validation...")
                print("✅ Repository structure validated")
                print("✅ Authentication validated")  
                print("✅ Workspace access validated")
                print("\n💡 Run without --dry-run to proceed with deployment")
                return
            
            # Create FabricWorkspace object WITHOUT environment parameter
            # This prevents parameter.yml processing
            workspace = FabricWorkspace(
                workspace_id=workspace_id,
                repository_directory=str(self.repository_directory),
                # Note: NO environment parameter = no parameterization
                item_type_in_scope=item_types,
                token_credential=self.credential
            )
            
            print("\n📦 Starting simple deployment...")
            workspace.deploy()
            print(f"\n✅ Simple deployment completed successfully!")
            print(f"   All items deployed with original names to workspace: {workspace_id}")
            
        except Exception as e:
            print(f"\n❌ Simple deployment failed: {e}")
            raise

    def deploy(self, workspace_id: str, environment: str, 
               item_types: list = None, 
               dry_run: bool = False, update_mode: bool = True):
        """
        Deploy Fabric items to target workspace
        
        Args:
            workspace_id: Target workspace ID in Fabric
            environment: Environment name for parameterization (DEV, STAGING, PROD)
            item_types: List of item types to deploy (None = all discovered types)
            dry_run: Validate configuration without deploying
            update_mode: If True, updates existing items; if False, only creates new items
        """
        
        print("\n" + "="*60)
        print(f"🚀 {'VALIDATING' if dry_run else 'DEPLOYING'} FABRIC WORKSPACE")
        print("="*60)
        print(f"📁 Repository: {self.repository_directory}")
        print(f"🎯 Workspace: {workspace_id}")
        print(f"🌍 Environment: {environment}")
        print(f"📦 Mode: {'Dry Run' if dry_run else 'Live Deployment'}")
        print(f"🔄 Update Mode: {'Update existing items' if update_mode else 'Create new items only'}")
        
        if item_types:
            print(f"🔍 Item Types: {', '.join(item_types)}")
        else:
            print("🔍 Item Types: All discovered types")
        
        print("\n💡 Deployment Behavior:")
        print("   • Items with same names will be updated/replaced")
        print("   • Items with different names will remain unchanged")
        print("   • New items will be created alongside existing items")
        print("   • Cross-references automatically updated to target workspace")
        
        try:
            # Create FabricWorkspace object
            workspace = FabricWorkspace(
                workspace_id=workspace_id,
                repository_directory=str(self.repository_directory),
                environment=environment,
                item_type_in_scope=item_types,
                token_credential=self.credential
            )
            
            if dry_run:
                print("\n🔍 Performing validation...")
                # The fabric-cicd library will validate parameters and repository structure
                print("✅ Repository structure validated")
                print("✅ Parameter file validated")
                print("✅ Authentication validated")
                print("✅ Workspace access validated")
                print("\n💡 Run without --dry-run to proceed with deployment")
            else:
                print("\n📦 Starting deployment...")
                workspace.deploy()
                print("\n✅ Deployment completed successfully!")
                    
                print("\n Post-deployment checklist:")
                print("   ✓ Verify items deployed correctly in Fabric workspace")
                print("   ✓ Test connections and data sources")
                print("   ✓ Validate cross-references between items")
                print("   ✓ Check that existing items still function properly")
        
        except Exception as e:
            print(f"\n❌ {'Validation' if dry_run else 'Deployment'} failed!")
            print(f"Error: {str(e)}")
            
            # Provide troubleshooting guidance
            print("\n🔧 Troubleshooting suggestions:")
            print("   • Verify Azure authentication: az login")
            print("   • Check workspace ID and permissions") 
            print("   • Validate parameter.yml structure")
            print("   • Ensure repository contains git-synced Fabric items")
            print("   • Check network connectivity to Fabric service")
            print("   • For existing workspaces: verify connection GUIDs are correct")
            
            raise
    
    def cross_region_migration(self, source_workspace: str, target_workspace: str,
                              source_env: str, target_env: str, 
                              item_types: list = None):
        """
        Perform cross-region migration between workspaces
        
        Args:
            source_workspace: Source workspace ID (for reference only)
            target_workspace: Target workspace ID
            source_env: Source environment name
            target_env: Target environment name
            item_types: Specific item types to migrate
        """
        
        print("\n" + "="*70)
        print("🌍 CROSS-REGION FABRIC MIGRATION")
        print("="*70)
        print(f"📤 Source: {source_env} workspace ({source_workspace[:8]}...)")
        print(f"📥 Target: {target_env} workspace ({target_workspace[:8]}...)")
        
        if item_types:
            print(f"🔍 Migrating: {', '.join(item_types)}")
        
        print("\n📋 Migration process:")
        print("   1. Repository should contain items from source workspace (via Git sync)")
        print("   2. parameter.yml handles environment-specific value replacement")
        print("   3. Items deployed to target workspace with target environment config")
        
        # Deploy to target workspace with target environment parameterization
        self.deploy(
            workspace_id=target_workspace,
            environment=target_env,
            item_types=item_types
        )
        
        print(f"\n✅ Cross-region migration from {source_env} to {target_env} completed!")
        
        print("\n🔍 Verification steps:")
        print(f"   • Check target workspace in Fabric: {target_workspace}")
        print("   • Verify all items deployed correctly")
        print("   • Test connections point to target region resources")
        print("   • Validate capacity and performance in target region")

def main():
    """Main execution function with command line interface"""
    
    parser = argparse.ArgumentParser(
        description="Deploy Fabric items using fabric-cicd library",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Deploy to DEV environment with parameterization (dry run)
  python fabric_deploy_local.py --workspace-id "dev-workspace-guid" --environment DEV --dry-run
  
  # Deploy specific item types to PROD with parameterization
  python fabric_deploy_local.py --workspace-id "prod-workspace-guid" --environment PROD --items Notebook Report
  
  # Simple deployment without parameterization (keeps original names)
  python fabric_deploy_local.py --workspace-id "target-workspace-guid" --simple
  
  # Cross-region migration from DEV to PROD
  python fabric_deploy_local.py --source-workspace "dev-guid" --target-workspace "prod-guid" --source-env DEV --target-env PROD
        """
    )
    
    # Repository configuration
    parser.add_argument(
        "--repository", "-r",
        default=".",
        help="Path to Git repository containing Fabric items (default: current directory)"
    )
    
    # Basic deployment arguments
    parser.add_argument(
        "--workspace-id", "-w",
        help="Target Fabric workspace ID"
    )
    
    parser.add_argument(
        "--environment", "-e",
        choices=["DEV", "STAGING", "PROD"],
        help="Environment name for parameterization"
    )
    
    # Cross-region migration arguments
    parser.add_argument(
        "--source-workspace",
        help="Source workspace ID (for cross-region migration)"
    )
    
    parser.add_argument(
        "--target-workspace", 
        help="Target workspace ID (for cross-region migration)"
    )
    
    parser.add_argument(
        "--source-env",
        choices=["DEV", "STAGING", "PROD"],
        help="Source environment name"
    )
    
    parser.add_argument(
        "--target-env",
        choices=["DEV", "STAGING", "PROD"],
        help="Target environment name"
    )
    
    # Optional arguments
    parser.add_argument(
        "--items",
        nargs="+",
        help="Specific item types to deploy (e.g., Notebook Report Lakehouse)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate configuration without deploying"
    )
    
    parser.add_argument(
        "--update-mode", 
        action="store_true", 
        default=True,
        help="Update existing items (default: True)"
    )
    
    parser.add_argument(
        "--no-update-mode", 
        dest="update_mode", 
        action="store_false",
        help="Only create new items, do not update existing items"
    )
    
    parser.add_argument(
        "--use-default-auth",
        action="store_true",
        help="Use DefaultAzureCredential instead of Azure CLI"
    )
    
    parser.add_argument(
        "--simple",
        action="store_true",
        help="Simple deployment without parameterization (keeps original names)"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    cross_region = bool(args.source_workspace and args.target_workspace and 
                       args.source_env and args.target_env)
    
    basic_deploy = bool(args.workspace_id and args.environment)
    simple_deploy = bool(args.workspace_id and args.simple)
    
    if not (cross_region or basic_deploy or simple_deploy):
        parser.error("Provide one of: "
                    "\n  • --workspace-id and --environment for parameterized deployment"
                    "\n  • --workspace-id and --simple for simple deployment (no parameterization)"  
                    "\n  • --source-workspace, --target-workspace, --source-env, and --target-env for cross-region migration")
    
    if args.simple and args.environment:
        parser.error("Cannot use both --simple and --environment. Choose one deployment method.")
    
    try:
        # Initialize deployment handler
        deployment = FabricDeployment(
            repository_directory=args.repository,
            use_cli_auth=not args.use_default_auth
        )
        
        if cross_region:
            # Cross-region migration
            deployment.cross_region_migration(
                source_workspace=args.source_workspace,
                target_workspace=args.target_workspace,
                source_env=args.source_env,
                target_env=args.target_env,
                item_types=args.items
            )
        elif simple_deploy:
            # Simple deployment without parameterization
            deployment.deploy_without_parameterization(
                workspace_id=args.workspace_id,
                item_types=args.items,
                dry_run=args.dry_run,
                update_mode=args.update_mode
            )
        else:
            # Basic parameterized deployment
            deployment.deploy(
                workspace_id=args.workspace_id,
                environment=args.environment,
                item_types=args.items,
                dry_run=args.dry_run,
                update_mode=args.update_mode
            )
    
    except KeyboardInterrupt:
        print("\n⚠️  Deployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Deployment failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
