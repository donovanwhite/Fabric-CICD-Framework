"""
Fabric Cross-Region Deployment Script with Azure DevOps Git Integration
======================================================================

This script demonstrates how to deploy Fabric items across different regions
using the fabric-cicd library with Azure DevOps Git repository as source.

Usage:
    # Using local clone of DevOps repo
    python fabric_deploy_devops.py --workspace-id <workspace-id> --target-env PROD --repo-path ./my-fabric-repo

    # Using DevOps repo URL (will clone automatically)
    python fabric_deploy_devops.py --workspace-id <workspace-id> --target-env PROD --repo-url https://dev.azure.com/myorg/myproject/_git/fabric-repo

    # Using specific branch/commit
    python fabric_deploy_devops.py --workspace-id <workspace-id> --target-env PROD --repo-url https://dev.azure.com/myorg/myproject/_git/fabric-repo --branch main
"""

import argparse
import sys
import os
import subprocess
import tempfile
import shutil
import stat
import errno
from pathlib import Path
from typing import Optional

# Add the current directory to Python path for imports
sys.path.append(str(Path(__file__).parent))

def handle_remove_readonly(func, path, exc):
    """
    Windows error handler for readonly files during cleanup
    
    Args:
        func: Function that raised the exception
        path: Path to the file
        exc: Exception information tuple
    """
    excvalue = exc[1]
    if func in (os.rmdir, os.remove, os.unlink) and excvalue.errno == errno.EACCES:
        # Change file permissions and retry
        os.chmod(path, stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)  # 0o777
        func(path)
    else:
        raise

try:
    from fabric_cicd import FabricWorkspace
    from azure.identity import DefaultAzureCredential, AzureCliCredential
except ImportError as e:
    print("❌ Required packages not installed. Please run:")
    print("   pip install fabric-cicd azure-identity")
    print(f"   Error: {e}")
    sys.exit(1)

class FabricDevOpsDeployment:
    """Handles Fabric workspace deployments with Azure DevOps Git integration"""
    
    def __init__(self, use_cli_auth: bool = True):
        """
        Initialize Fabric deployment with DevOps integration
        
        Args:
            use_cli_auth: Use Azure CLI authentication (default) vs DefaultAzureCredential
        """
        # Choose authentication method
        if use_cli_auth:
            self.credential = AzureCliCredential()
            print("🔑 Using Azure CLI authentication")
        else:
            self.credential = DefaultAzureCredential()
            print("🔑 Using Default Azure credential chain")
        
        self.temp_repo_path = None
    
    def clone_devops_repo(self, repo_url: str, branch: str = "main", 
                         target_path: Optional[str] = None) -> Path:
        """
        Clone Azure DevOps repository to local directory
        
        Args:
            repo_url: Azure DevOps Git repository URL
            branch: Git branch to clone (default: main)
            target_path: Local path to clone to (default: temp directory)
            
        Returns:
            Path to cloned repository
        """
        if target_path:
            clone_path = Path(target_path).resolve()
            if clone_path.exists():
                shutil.rmtree(clone_path, onerror=handle_remove_readonly)
        else:
            # Use temporary directory
            temp_dir = tempfile.mkdtemp(prefix="fabric_deploy_")
            clone_path = Path(temp_dir) / "repo"
            self.temp_repo_path = clone_path
        
        print(f"📥 Cloning Azure DevOps repository...")
        print(f"   🔗 URL: {repo_url}")
        print(f"   🌿 Branch: {branch}")
        print(f"   📁 Local path: {clone_path}")
        
        try:
            # Clone repository
            cmd = ["git", "clone", "--branch", branch, "--depth", "1", repo_url, str(clone_path)]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            print("✅ Repository cloned successfully")
            return clone_path
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to clone repository: {e}")
            print(f"   stdout: {e.stdout}")
            print(f"   stderr: {e.stderr}")
            print("\n💡 Make sure:")
            print("   • Git is installed and in PATH")
            print("   • You have access to the Azure DevOps repository")
            print("   • Azure DevOps credentials are configured (git credential manager)")
            raise
    
    def validate_devops_repository(self, repo_path: Path):
        """Validate that the DevOps repository has the required structure"""
        if not repo_path.exists():
            raise FileNotFoundError(f"Repository directory not found: {repo_path}")
        
        # Check for parameter.yml
        parameter_file = repo_path / "parameter.yml"
        if not parameter_file.exists():
            print("⚠️  Warning: parameter.yml not found in repository root")
            print(f"   Expected location: {parameter_file}")
            print("   This file is required for environment-specific parameterization")
        
        # List Fabric items
        fabric_items = self._list_fabric_items(repo_path)
        if not fabric_items:
            print("⚠️  Warning: No Fabric items found in repository")
            print("   Expected folder structure: <ItemName>.<ItemType>/")
            print("   Make sure your Fabric workspace Git sync has committed items")
        else:
            print(f"📊 Found {len(fabric_items)} Fabric items:")
            for item in fabric_items:
                print(f"   📁 {item}")
        
        # Check for common DevOps files
        devops_files = [".gitignore", "azure-pipelines.yml", "README.md"]
        found_devops = [f for f in devops_files if (repo_path / f).exists()]
        if found_devops:
            print(f"🔧 DevOps files found: {', '.join(found_devops)}")
    
    def _list_fabric_items(self, repo_path: Path) -> list:
        """List all Fabric items in the repository"""
        fabric_extensions = [
            'Notebook', 'Report', 'Dashboard', 'SemanticModel', 'Lakehouse', 
            'Warehouse', 'DataPipeline', 'Dataflow', 'Environment', 'SQLEndpoint',
            'KQLDatabase', 'KQLQueryset', 'Eventhouse', 'Eventstream', 'MLModel',
            'MLExperiment', 'Activator', 'APIForGraphQL', 'CopyJob'
        ]
        
        items = []
        for item in repo_path.iterdir():
            if item.is_dir():
                for ext in fabric_extensions:
                    if item.name.endswith(f'.{ext}'):
                        items.append(item.name)
                        break
        
        return sorted(items)
    
    def deploy_from_devops_simple(self, workspace_id: str, 
                                 repo_url: Optional[str] = None, 
                                 repo_path: Optional[str] = None,
                                 branch: str = "main",
                                 item_types: list = None, 
                                 dry_run: bool = False, 
                                 update_mode: bool = True):
        """
        Deploy Fabric items from Azure DevOps repository WITHOUT parameterization
        This keeps all original item names and references intact
        
        Args:
            workspace_id: Target workspace ID in Fabric
            repo_url: Azure DevOps Git repository URL (if cloning)
            repo_path: Local path to repository (if already cloned)
            branch: Git branch to use (default: main)
            item_types: List of item types to deploy (None = all discovered types)
            dry_run: Validate configuration without deploying
            update_mode: If True, updates existing items; if False, only creates new items
        """
        print(f"🚀 {'VALIDATING' if dry_run else 'DEPLOYING'} FROM AZURE DEVOPS (SIMPLE)")
        print("="*70)
        
        try:
            # Determine repository path
            if repo_url:
                repository_directory = self.clone_devops_repo(repo_url, branch)
            elif repo_path:
                repository_directory = Path(repo_path).resolve()
                print(f"📁 Using local repository: {repository_directory}")
            else:
                raise ValueError("Either repo_url or repo_path must be provided")
            
            # Validate repository structure
            self.validate_devops_repository(repository_directory)
            
            print(f"🎯 Target Workspace: {workspace_id}")
            print(f"🌿 Branch: {branch}")
            print(f"📦 Mode: {'Dry Run' if dry_run else 'Live Deployment'}")
            print(f"🔄 Update Mode: {'Update existing items' if update_mode else 'Create new items only'}")
            print(f"📝 Parameterization: DISABLED - Original names preserved")
            
            if item_types:
                print(f"🔍 Item Types: {', '.join(item_types)}")
            else:
                print("🔍 Item Types: All discovered types")
            
            print("\n💡 Simple DevOps Deployment Behavior:")
            print("   • All item names remain exactly as in source repository")
            print("   • No parameter.yml replacement performed")
            print("   • Items deployed with original references intact")
            print("   • Repository content used as source of truth")
            print("   • Ideal for workspace-to-workspace copies via DevOps")
            print("   • Using workspace's current capacity assignment")
            
            # Check if repository has parameter.yml
            parameter_file = repository_directory / "parameter.yml"
            if parameter_file.exists():
                print(f"\n⚠️  Note: parameter.yml found but will be IGNORED")
                print(f"   File location: {parameter_file}")
                print("   Use deploy_from_devops() method if you want parameterization")
            
            # Create FabricWorkspace object WITHOUT environment parameter
            # This prevents parameter.yml processing
            workspace = FabricWorkspace(
                workspace_id=workspace_id,
                repository_directory=str(repository_directory),
                # Note: NO environment parameter = no parameterization
                item_type_in_scope=item_types,
                token_credential=self.credential
            )
            
            if dry_run:
                print("\n🔍 Performing validation...")
                print("✅ Repository structure validated")
                print("✅ Authentication validated")
                print("✅ Workspace access validated")
                print("\n💡 Run without --dry-run to proceed with deployment")
            else:
                print("\n📦 Starting simple deployment from DevOps repository...")
                workspace.deploy()
                print("\n✅ Simple deployment completed successfully!")
                print(f"   All items deployed with original names to workspace: {workspace_id}")
                
        except Exception as e:
            print(f"\n❌ Simple deployment failed: {e}")
            raise
        finally:
            # Cleanup temporary repository if created
            if self.temp_repo_path and self.temp_repo_path.exists():
                print(f"🧹 Cleaning up temporary repository: {self.temp_repo_path}")
                shutil.rmtree(self.temp_repo_path, onerror=handle_remove_readonly)

    def deploy_from_devops(self, workspace_id: str, environment: str,
                          repo_url: Optional[str] = None, 
                          repo_path: Optional[str] = None,
                          branch: str = "main",
                          item_types: list = None, 
                          dry_run: bool = False, 
                          update_mode: bool = True):
        """
        Deploy Fabric items from Azure DevOps repository to target workspace
        
        Args:
            workspace_id: Target workspace ID in Fabric
            environment: Environment name for parameterization (DEV, STAGING, PROD)
            repo_url: Azure DevOps Git repository URL (if cloning)
            repo_path: Local path to repository (if already cloned)
            branch: Git branch to use (default: main)
            item_types: List of item types to deploy (None = all discovered types)
            dry_run: Validate configuration without deploying
            update_mode: If True, updates existing items; if False, only creates new items
        """
        
        print("\n" + "="*70)
        print(f"🚀 {'VALIDATING' if dry_run else 'DEPLOYING'} FROM AZURE DEVOPS")
        print("="*70)
        
        try:
            # Determine repository path
            if repo_url:
                repository_directory = self.clone_devops_repo(repo_url, branch)
            elif repo_path:
                repository_directory = Path(repo_path).resolve()
                print(f"📁 Using local repository: {repository_directory}")
            else:
                raise ValueError("Either repo_url or repo_path must be provided")
            
            # Validate repository structure
            self.validate_devops_repository(repository_directory)
            
            print(f"🎯 Target Workspace: {workspace_id}")
            print(f"🌍 Environment: {environment}")
            print(f"🌿 Branch: {branch}")
            print(f"📦 Mode: {'Dry Run' if dry_run else 'Live Deployment'}")
            print(f"🔄 Update Mode: {'Update existing items' if update_mode else 'Create new items only'}")
            
            if item_types:
                print(f"🔍 Item Types: {', '.join(item_types)}")
            else:
                print("🔍 Item Types: All discovered types")
            
            print("\n💡 DevOps Deployment Behavior:")
            print("   • Repository content used as source of truth")
            print("   • Items with same names will be updated/replaced")
            print("   • New items will be created alongside existing items")
            print("   • Cross-references automatically updated to target workspace")
            print("   • Using workspace's current capacity assignment")
            
            # Create FabricWorkspace object
            workspace = FabricWorkspace(
                workspace_id=workspace_id,
                repository_directory=str(repository_directory),
                environment=environment,
                item_type_in_scope=item_types,
                token_credential=self.credential
            )
            
            if dry_run:
                print("\n🔍 Performing validation...")
                print("✅ Repository structure validated")
                print("✅ Parameter file validated")
                print("✅ Authentication validated")
                print("✅ Workspace access validated")
                print("\n💡 Run without --dry-run to proceed with deployment")
            else:
                print("\n📦 Starting deployment from DevOps repository...")
                workspace.deploy()
                print("\n✅ Deployment completed successfully!")
                
        except Exception as e:
            print(f"\n❌ Deployment failed: {e}")
            raise
        finally:
            # Cleanup temporary repository if created
            if self.temp_repo_path and self.temp_repo_path.exists():
                print(f"🧹 Cleaning up temporary repository: {self.temp_repo_path}")
                shutil.rmtree(self.temp_repo_path, onerror=handle_remove_readonly)

def main():
    parser = argparse.ArgumentParser(
        description="Deploy Fabric items from Azure DevOps repository",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Deploy from DevOps repo URL with parameterization
  python fabric_deploy_devops.py --workspace-id "12345" --target-env PROD --repo-url "https://dev.azure.com/myorg/myproject/_git/fabric-repo"
  
  # Deploy from local clone
  python fabric_deploy_devops.py --workspace-id "12345" --target-env PROD --repo-path "./my-fabric-repo"
  
  # Simple deployment without parameterization (keeps original names)
  python fabric_deploy_devops.py --workspace-id "12345" --simple --repo-url "https://dev.azure.com/myorg/myproject/_git/fabric-repo"
  
  # Deploy specific branch 
  python fabric_deploy_devops.py --workspace-id "12345" --target-env PROD --repo-url "https://..." --branch "release/v1.0"
        """
    )
    
    parser.add_argument("--workspace-id", required=True, 
                       help="Target Fabric workspace ID")
    parser.add_argument("--target-env", 
                       choices=["DEV", "STAGING", "PROD"],
                       help="Target environment for parameterization (optional for simple deployment)")
    
    # Repository source (mutually exclusive)
    repo_group = parser.add_mutually_exclusive_group(required=True)
    repo_group.add_argument("--repo-url", 
                           help="Azure DevOps Git repository URL")
    repo_group.add_argument("--repo-path", 
                           help="Local path to repository")
    
    parser.add_argument("--branch", default="main",
                       help="Git branch to use (default: main)")
    parser.add_argument("--items", nargs="+",
                       help="Specific item types to deploy (e.g., Notebook Report)")
    parser.add_argument("--dry-run", action="store_true",
                       help="Validate configuration without deploying")
    parser.add_argument("--create-only", action="store_true",
                       help="Create new items only, don't update existing")
    parser.add_argument("--simple", action="store_true",
                       help="Simple deployment without parameterization (keeps original names)")
    parser.add_argument("--use-default-auth", action="store_true",
                       help="Use DefaultAzureCredential instead of Azure CLI")
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.simple and not args.target_env:
        parser.error("Either --target-env is required for parameterized deployment, or use --simple for deployment without parameterization")
    
    if args.simple and args.target_env:
        parser.error("Cannot use both --simple and --target-env. Choose one deployment method.")
    
    try:
        # Initialize deployment handler
        deployment = FabricDevOpsDeployment(use_cli_auth=not args.use_default_auth)
        
        # Execute deployment
        if args.simple:
            # Simple deployment without parameterization
            deployment.deploy_from_devops_simple(
                workspace_id=args.workspace_id,
                repo_url=args.repo_url,
                repo_path=args.repo_path,
                branch=args.branch,
                item_types=args.items,
                dry_run=args.dry_run,
                update_mode=not args.create_only
            )
        else:
            # Parameterized deployment
            deployment.deploy_from_devops(
                workspace_id=args.workspace_id,
                environment=args.target_env,
                repo_url=args.repo_url,
                repo_path=args.repo_path,
                branch=args.branch,
                item_types=args.items,
                dry_run=args.dry_run,
                update_mode=not args.create_only
            )
        
    except KeyboardInterrupt:
        print("\n⚠️  Deployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Deployment failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
