#!/usr/bin/env python3
"""
Microsoft Fabric CI/CD Setup Script
=============================================================

This script sets up CI/CD for Microsoft Fabric using the fabric-cicd library.
Based on extensive testing and troubleshooting, this uses the SIMPLE approach that actually works.

SUCCESSFUL APPROACH:
✅ Uses basic publish_all_items() function from fabric-cicd documentation
✅ Lets fabric-cicd handle subdirectory structures natively (Migration/, Warehouse/, etc.)
✅ Avoids complex parameter.yml configurations that cause validation errors
✅ Specifies item types based on actual repository analysis
✅ Successfully tested with 8 Fabric items across subdirectories

KEY LEARNINGS FROM TESTING:
1. Complex parameter.yml files cause validation errors ("Invalid parameter name 'find_key'")
2. fabric-cicd natively supports workspace subfolders - don't flatten the structure
3. Simple publish_all_items(workspace) is more reliable than advanced configurations in some scenarios
4. Authentication with DefaultAzureCredential works perfectly
5. Item type specification is crucial: ["Notebook", "Lakehouse", "Warehouse"]

SUPPORTED REPOSITORY STRUCTURE:
/<repository-root>
    /<workspace-subfolder>/          # e.g., Migration/
        /<item-name>.<item-type>     # e.g., nb_analysis.Notebook
        /<item-name>.<item-type>     # e.g., data_lake.Lakehouse
    /<workspace-subfolder>/          # e.g., Warehouse/
        /<item-name>.<item-type>     # e.g., analytics_wh.Warehouse
    /README.md                       # Optional files (ignored by fabric-cicd)

TESTED WITH:
- Repository: Azure DevOps with 8 items in subdirectories
- Items: 6 Notebooks + 1 Lakehouse (Migration/) + 1 Warehouse (Warehouse/)
- Authentication: DefaultAzureCredential as admin user
- Result: ✅ ALL ITEMS DEPLOYED SUCCESSFULLY

Usage:
    python fabric_deploy.py --workspace-id <workspace-id> --repo-url <repo-url>
    
Example:
    python fabric_deploy.py \
        --workspace-id "eb2f7de1-b2d5-4852-a744-735106d8dfe8" \
        --repo-url "https://dev.azure.com/contoso/Project/_git/repo" \
        --branch main
"""

import os
import sys
import tempfile
import shutil
import argparse
from pathlib import Path

# Check dependencies
try:
    from git import Repo
    from azure.identity import DefaultAzureCredential
    from fabric_cicd import FabricWorkspace, publish_all_items
    import fabric_cicd
except ImportError as e:
    print(f"❌ Missing required dependency: {e}")
    print("📦 Please install required packages:")
    print("   pip install fabric-cicd GitPython azure-identity")
    sys.exit(1)

def check_version_compatibility():
    """Check Python and fabric-cicd version compatibility"""
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python version incompatible")
        print(f"   Current: {sys.version.split()[0]}")
        print("   Required: Python 3.8 or higher")
        print("💡 Please upgrade Python or use a compatible environment")
        sys.exit(1)
    
    # Check fabric-cicd version
    try:
        from packaging import version
        required_version = "0.1.24"
        current_version = fabric_cicd.__version__
        
        if version.parse(current_version) < version.parse(required_version):
            print("❌ fabric-cicd version incompatible")
            print(f"   Current: {current_version}")
            print(f"   Required: {required_version} or higher")
            print("💡 Please upgrade: pip install --upgrade fabric-cicd")
            sys.exit(1)
            
        print(f"✅ Version check passed - fabric-cicd {current_version}")
        
    except ImportError:
        print("⚠️  Warning: Cannot verify fabric-cicd version (packaging module not available)")
        print("💡 Consider installing: pip install packaging")
        
    except Exception as e:
        print(f"⚠️  Warning: Version check failed: {e}")
        print("💡 Continuing with deployment attempt...")

def analyze_repository(repo_path):
    """
    Analyze repository to discover Fabric item types
    This helps determine the item_type_in_scope parameter
    """
    print("🔍 Analyzing repository structure...")
    
    fabric_extensions = {
        '.Notebook': 'Notebook',
        '.Lakehouse': 'Lakehouse', 
        '.Warehouse': 'Warehouse',
        '.SemanticModel': 'SemanticModel',
        '.Report': 'Report',
        '.DataPipeline': 'DataPipeline',
        '.Environment': 'Environment',
        '.Dataflow': 'Dataflow',
        '.KQLDatabase': 'KQLDatabase',
        '.KQLQueryset': 'KQLQueryset',
        '.MLModel': 'MLModel',
        '.MLExperiment': 'MLExperiment'
    }
    
    found_types = set()
    total_items = 0
    
    # Walk through repository
    for root, dirs, files in os.walk(repo_path):
        # Skip .git directories
        dirs[:] = [d for d in dirs if not d.startswith('.git')]
        
        for item in dirs + files:
            for ext, item_type in fabric_extensions.items():
                if item.endswith(ext):
                    found_types.add(item_type)
                    total_items += 1
                    rel_path = os.path.relpath(os.path.join(root, item), repo_path)
                    print(f"   📄 Found {item_type}: {rel_path}")
    
    print(f"📊 Analysis complete:")
    print(f"   Total Fabric items: {total_items}")
    print(f"   Item types found: {list(found_types)}")
    
    return list(found_types), total_items

def main():
    parser = argparse.ArgumentParser(
        description='Deploy Fabric items using PROVEN working fabric-cicd approach',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic deployment
  python fabric_deploy.py --workspace-id "your-workspace-id" --repo-url "https://dev.azure.com/org/proj/_git/repo"
  
  # With specific branch
  python fabric_deploy.py --workspace-id "your-workspace-id" --repo-url "repo-url" --branch development
  
  # Dry run (analyze only)
  python fabric_deploy.py --workspace-id "your-workspace-id" --repo-url "repo-url" --dry-run
        """
    )
    
    parser.add_argument('--workspace-id', required=True, 
                       help='Microsoft Fabric workspace ID (GUID)')
    parser.add_argument('--repo-url', required=True,
                       help='Git repository URL (Azure DevOps, GitHub, etc.)')
    parser.add_argument('--branch', default='main',
                       help='Git branch to deploy from (default: main)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Analyze repository without deploying')
    parser.add_argument('--item-types', nargs='*',
                       help='Specific item types to deploy (auto-detected if not specified)')
    
    args = parser.parse_args()
    
    # Check version compatibility first
    check_version_compatibility()
    
    # Create temporary directory for repository
    temp_dir = tempfile.mkdtemp(prefix='fabric_cicd_')
    repo_path = None
    
    try:
        print("🚀 FABRIC CI/CD DEPLOYMENT (PROVEN WORKING SOLUTION)")
        print("=" * 60)
        print(f"📂 Temporary directory: {temp_dir}")
        print(f"🔗 Repository: {args.repo_url}")
        print(f"🌿 Branch: {args.branch}")
        print(f"🎯 Workspace ID: {args.workspace_id}")
        print(f"🧪 Dry run: {args.dry_run}")
        print()
        
        # Clone repository
        print("📥 Cloning repository...")
        try:
            repo = Repo.clone_from(args.repo_url, temp_dir)
        except Exception as e:
            print(f"❌ Failed to clone repository: {e}")
            print("💡 Check:")
            print("   - Repository URL is correct")
            print("   - You have access to the repository")
            print("   - Azure CLI authentication (az login)")
            sys.exit(1)
        
        # Checkout specific branch
        if args.branch != 'main':
            print(f"🔀 Switching to branch: {args.branch}")
            try:
                repo.git.checkout(args.branch)
            except Exception as e:
                print(f"❌ Failed to checkout branch {args.branch}: {e}")
                print("💡 Available branches:")
                for branch in repo.heads:
                    print(f"   - {branch.name}")
                sys.exit(1)
        
        repo_path = temp_dir
        print(f"✅ Repository ready at: {repo_path}")
        print()
        
        # Analyze repository structure
        item_types, total_items = analyze_repository(repo_path)
        
        if total_items == 0:
            print("⚠️  No Fabric items found in repository!")
            print("💡 Expected structure:")
            print("   /<folder>/")
            print("      /<item-name>.Notebook")
            print("      /<item-name>.Lakehouse")
            print("      /<item-name>.Warehouse")
            print("   etc.")
            return
        
        # Use user-specified item types or auto-detected ones
        if args.item_types:
            item_types = args.item_types
            print(f"🎯 Using specified item types: {item_types}")
        else:
            print(f"🔍 Auto-detected item types: {item_types}")
        print()
        
        if args.dry_run:
            print("🧪 DRY RUN - Analysis complete, no deployment performed")
            print(f"📊 Would deploy {total_items} items of types: {item_types}")
            return
        
        # Initialize FabricWorkspace using the PROVEN WORKING pattern
        print("🔧 Initializing FabricWorkspace...")
        print("   Using SIMPLE approach that actually works!")
        
        try:
            workspace = FabricWorkspace(
                workspace_id=args.workspace_id,
                repository_directory=repo_path,
                item_type_in_scope=item_types
            )
        except Exception as e:
            print(f"❌ Failed to initialize FabricWorkspace: {e}")
            print("💡 Check:")
            print("   - Workspace ID is correct")
            print("   - You have access to the workspace")
            print("   - DefaultAzureCredential is configured (az login)")
            sys.exit(1)
        
        print(f"✅ FabricWorkspace initialized successfully")
        print(f"   📁 Repository directory: {repo_path}")
        print(f"   🎯 Workspace ID: {args.workspace_id}")
        print(f"   📦 Item types in scope: {item_types}")
        print()
        
        # Execute deployment using PROVEN WORKING approach
        print("🚀 Deploying using publish_all_items()...")
        print("   This is the SIMPLE approach that actually works!")
        print(f"   Deploying {total_items} items...")
        print()
        
        try:
            result = publish_all_items(workspace)
            
            print("✅ DEPLOYMENT COMPLETED SUCCESSFULLY!")
            print(f"📊 Result: {result}")
            print()
            print("🎉 Your Fabric items should now be visible in the workspace!")
            print("💡 Check your Fabric workspace to verify the deployment.")
            
        except Exception as e:
            print(f"❌ Deployment failed: {e}")
            print("📋 Full error details:")
            import traceback
            traceback.print_exc()
            print()
            print("💡 Common issues:")
            print("   - Workspace permissions (need Admin or Member role)")
            print("   - Authentication expired (try az login)")
            print("   - Network connectivity issues")
            sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n⏹️  Deployment cancelled by user")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
    finally:
        # Clean up temporary directory
        if repo_path and os.path.exists(temp_dir):
            try:
                print(f"🧹 Cleaning up: {temp_dir}")
                shutil.rmtree(temp_dir)
            except Exception as e:
                print(f"⚠️  Warning: Could not clean up temp directory: {e}")

if __name__ == "__main__":
    main()
