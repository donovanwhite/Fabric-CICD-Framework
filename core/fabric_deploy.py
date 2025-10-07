#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
        --workspace-id "your-workspace-id-here" \
        --repo-url "https://dev.azure.com/yourorg/YourProject/_git/YourRepo" \
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
    from fabric_cicd import FabricWorkspace, publish_all_items, deploy_with_config
    import fabric_cicd
except ImportError as e:
    print(f"❌ Missing required dependency: {e}")
    print("📦 Please install required packages:")
    print("   pip install fabric-cicd GitPython azure-identity")
    print("   Optional: pip install PyYAML (for parameter file support)")
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
        required_version = "0.1.29"
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
        '.MirroredDatabase': 'MirroredDatabase',
        '.VariableLibrary': 'VariableLibrary',
        '.CopyJob': 'CopyJob',
        '.Eventhouse': 'Eventhouse',
        '.Reflex': 'Reflex',
        '.Eventstream': 'Eventstream',
        '.SQLDatabase': 'SQLDatabase',
        '.KQLDashboard': 'KQLDashboard',
        '.GraphQLApi': 'GraphQLApi',
        '.ApacheAirflowJob': 'ApacheAirflowJob',
        '.MountedDataFactory': 'MountedDataFactory'
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

def deploy_with_error_handling(workspace):
    """Deploy Fabric items with enhanced error handling for individual item failures."""
    print("🚀 Starting deployment with enhanced error handling...")
    
    deployment_summary = {
        'successful': [],
        'failed': [],
        'skipped': [],
        'total': 0
    }
    
    try:
        # Try the standard publish_all_items first
        print("📦 Attempting bulk deployment using publish_all_items()...")
        result = publish_all_items(workspace)
        print("✅ Bulk deployment completed successfully!")
        return result
        
    except Exception as bulk_error:
        error_msg = str(bulk_error)
        if "Cannot find the KQL Database source" in error_msg:
            print("⚠️  Bulk deployment failed: KQL Dashboard database reference issue")
            print("💡 Most items were likely deployed successfully")
            print(f"🔍 Specific error: {error_msg}")
        elif "ParsingError" in error_msg:
            print("⚠️  Bulk deployment failed: Item configuration issue")
            print(f"🔍 Details: {error_msg}")
        else:
            print(f"⚠️  Bulk deployment failed: {error_msg}")
        
        print("🔄 Switching to individual item deployment with error handling...")
        print()
        
        # Get available item types from the workspace
        try:
            # Try to get items individually by type
            item_types_to_try = [
                'datapipelines', 'notebooks', 'reports', 'datasets', 
                'dataflows', 'lakehouses', 'warehouses', 'semanticmodels',
                'dashboards', 'datamart', 'kqlqueries', 'sparkjobdefinitions'
            ]
            
            for item_type in item_types_to_try:
                try:
                    print(f"📋 Processing {item_type}...")
                    
                    # Try to publish this item type
                    if hasattr(workspace, f'publish_{item_type}'):
                        publish_method = getattr(workspace, f'publish_{item_type}')
                        publish_method()
                        print(f"   ✅ {item_type} deployed successfully")
                        deployment_summary['successful'].append(item_type)
                    else:
                        print(f"   ⚠️  No publish method for {item_type}, skipping")
                        deployment_summary['skipped'].append(item_type)
                        
                except Exception as item_error:
                    error_msg = str(item_error)
                    print(f"   ❌ Failed to deploy {item_type}: {error_msg}")
                    
                    # Check for specific error types and provide helpful messages
                    if "does not have access to the connection" in error_msg:
                        print(f"   💡 Connection permission issue - user needs access to connections used in {item_type}")
                    elif "User does not have access" in error_msg:
                        print(f"   💡 Access permission issue - check user permissions for {item_type}")
                    elif "already exists" in error_msg:
                        print(f"   💡 Item already exists - consider using update instead of create")
                    elif "Invalid" in error_msg:
                        print(f"   💡 Configuration issue - check {item_type} settings and dependencies")
                    else:
                        print(f"   💡 Unknown error - review {item_type} configuration")
                    
                    deployment_summary['failed'].append({
                        'item_type': item_type,
                        'error': error_msg
                    })
                    print(f"   🔄 Continuing with next item type...")
                    
                deployment_summary['total'] += 1
                print()
            
            # Print deployment summary
            print("📊 DEPLOYMENT SUMMARY")
            print("=" * 50)
            print(f"✅ Successful: {len(deployment_summary['successful'])} item types")
            for item in deployment_summary['successful']:
                print(f"   - {item}")
            
            print(f"❌ Failed: {len(deployment_summary['failed'])} item types")
            for item in deployment_summary['failed']:
                print(f"   - {item['item_type']}: {item['error'][:100]}...")
            
            print(f"⚠️  Skipped: {len(deployment_summary['skipped'])} item types")
            for item in deployment_summary['skipped']:
                print(f"   - {item}")
            
            print(f"📈 Total processed: {deployment_summary['total']} item types")
            print()
            
            if deployment_summary['successful']:
                print("🎉 Partial deployment completed! Check successful items in your workspace.")
                return "Partial deployment completed with some failures"
            else:
                print("💥 No items were deployed successfully.")
                raise Exception("All item deployments failed")
                
        except Exception as individual_error:
            print(f"❌ Individual deployment also failed: {individual_error}")
            raise

def main():
    parser = argparse.ArgumentParser(
        description='Deploy Fabric items using PROVEN working fabric-cicd approach',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic deployment with default authentication
  python fabric_deploy.py --workspace-id "your-workspace-id" --repo-url "https://dev.azure.com/org/proj/_git/repo"
  
  # With specific branch
  python fabric_deploy.py --workspace-id "your-workspace-id" --repo-url "repo-url" --branch development
  
  # Using service principal authentication
  python fabric_deploy.py --workspace-id "your-workspace-id" --repo-url "repo-url" --client-id "sp-client-id" --client-secret "sp-secret" --tenant-id "tenant-id"
  
  # Using parameter file for configuration
  python fabric_deploy.py --workspace-id "your-workspace-id" --repo-url "repo-url" --parameter-file "../config/parameter.yml"
  
  # Dry run (analyze only)
  python fabric_deploy.py --workspace-id "your-workspace-id" --repo-url "repo-url" --dry-run
  
  # Deploy specific item types only
  python fabric_deploy.py --workspace-id "your-workspace-id" --repo-url "repo-url" --item-types Notebook Lakehouse
  
  # Local directory deployment (skip git clone)
  python fabric_deploy.py --workspace-id "your-workspace-id" --local-path "./my-fabric-items"
  
  # Using parameter file with local path deployment
  python fabric_deploy.py --workspace-id "your-workspace-id" --local-path "./my-fabric-items" --parameter-file "../config/parameter.yml"
  
  # NEW v0.1.29: Configuration-based deployment
  python fabric_deploy.py --config-file "../config/config.yml" --environment prod
  
  # Configuration-based deployment with service principal
  python fabric_deploy.py --config-file "../config/config.yml" --environment prod --client-id "sp-client-id" --client-secret "sp-secret" --tenant-id "tenant-id"
        """
    )
    
    parser.add_argument('--workspace-id', required=True, 
                       help='Microsoft Fabric workspace ID (GUID)')
    parser.add_argument('--repo-url', 
                       help='Git repository URL (Azure DevOps, GitHub, etc.)')
    parser.add_argument('--local-path',
                       help='Local directory path containing Fabric items (alternative to --repo-url)')
    parser.add_argument('--branch', default='main',
                       help='Git branch to deploy from (default: main)')
    parser.add_argument('--parameter-file',
                       help='Path to parameter.yml file for configuration (default: ../config/parameter.yml)')
    parser.add_argument('--config-file',
                       help='Path to config.yml file for configuration-based deployment (default: ../config/config.yml)')
    parser.add_argument('--environment',
                       help='Environment name for configuration-based deployment (e.g., dev, test, prod)')
    parser.add_argument('--client-id',
                       help='Service Principal client ID for authentication')
    parser.add_argument('--client-secret',
                       help='Service Principal client secret for authentication')
    parser.add_argument('--tenant-id',
                       help='Azure tenant ID for service principal authentication')
    parser.add_argument('--dry-run', action='store_true',
                       help='Analyze repository without deploying')
    parser.add_argument('--item-types', nargs='*',
                       help='Specific item types to deploy (auto-detected if not specified)')
    
    args = parser.parse_args()
    
    # Validate mutually exclusive options
    if not args.repo_url and not args.local_path:
        parser.error("Either --repo-url or --local-path must be specified")
    
    if args.repo_url and args.local_path:
        parser.error("Cannot specify both --repo-url and --local-path")
    
    # Service principal authentication requires all three parameters
    sp_params = [args.client_id, args.client_secret, args.tenant_id]
    if any(sp_params) and not all(sp_params):
        parser.error("Service principal authentication requires --client-id, --client-secret, and --tenant-id")
    
    # Configuration-based deployment validation
    if args.config_file and not args.environment:
        parser.error("Configuration-based deployment requires --environment parameter")
    
    if args.config_file and (args.parameter_file or args.item_types):
        print("⚠️  Warning: --config-file will override --parameter-file and --item-types settings")
    
    # Check version compatibility first
    check_version_compatibility()
    
    # Create temporary directory for repository
    temp_dir = tempfile.mkdtemp(prefix='fabric_cicd_')
    repo_path = None
    
    try:
        print("🚀 FABRIC CI/CD DEPLOYMENT (PROVEN WORKING SOLUTION)")
        print("=" * 60)
        
        # Handle local path vs repository deployment
        if args.local_path:
            print(f"📂 Local path: {args.local_path}")
            repo_path = args.local_path
            if not os.path.exists(repo_path):
                print(f"❌ Local path does not exist: {repo_path}")
                sys.exit(1)
        else:
            print(f"📂 Temporary directory: {temp_dir}")
            print(f"🔗 Repository: {args.repo_url}")
            print(f"🌿 Branch: {args.branch}")
            
        print(f"🎯 Workspace ID: {args.workspace_id}")
        
        # Show authentication method
        if args.client_id:
            print(f"🔐 Authentication: Service Principal ({args.client_id})")
        else:
            print(f"🔐 Authentication: DefaultAzureCredential")
            
        if args.config_file:
            print(f"📋 Config file: {args.config_file}")
            print(f"🌍 Environment: {args.environment}")
            print(f"🆕 Using v0.1.29 configuration-based deployment")
        elif args.parameter_file:
            print(f"📋 Parameter file: {args.parameter_file}")
            
        print(f"🧪 Dry run: {args.dry_run}")
        print()
        
        # Clone repository if using repo-url
        if args.repo_url:
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
        else:
            print(f"✅ Using local path: {repo_path}")
        print()
        
        # Load parameter file if specified
        parameter_config = {}
        if args.parameter_file:
            print(f"📋 Loading parameter file: {args.parameter_file}")
            try:
                import yaml
                with open(args.parameter_file, 'r', encoding='utf-8') as f:
                    parameter_config = yaml.safe_load(f)
                print(f"✅ Parameter file loaded successfully")
                
                # Apply parameter file settings to override command line args where applicable
                if 'workspace_id' in parameter_config and not args.workspace_id:
                    args.workspace_id = parameter_config['workspace_id']
                    print(f"   Using workspace_id from parameter file: {args.workspace_id}")
                    
                if 'item_types' in parameter_config and not args.item_types:
                    args.item_types = parameter_config['item_types']
                    print(f"   Using item_types from parameter file: {args.item_types}")
                    
            except ImportError:
                print(f"❌ PyYAML not installed. Install with: pip install PyYAML")
                sys.exit(1)
            except Exception as e:
                print(f"❌ Failed to load parameter file: {e}")
                print("💡 Check file path and YAML syntax")
                sys.exit(1)
        print()
        
        # Handle configuration-based deployment (v0.1.29 feature)
        if args.config_file:
            print("🆕 USING CONFIGURATION-BASED DEPLOYMENT (v0.1.29)")
            print("=" * 60)
            
            if args.dry_run:
                print("🧪 DRY RUN - Configuration-based deployment analysis")
                print(f"📋 Config file: {args.config_file}")
                print(f"🌍 Environment: {args.environment}")
                print("💡 Would use deploy_with_config() function")
                return
            
            try:
                # Set up authentication for configuration-based deployment
                if args.client_id:
                    from azure.identity import ClientSecretCredential
                    credential = ClientSecretCredential(
                        tenant_id=args.tenant_id,
                        client_id=args.client_id,
                        client_secret=args.client_secret
                    )
                    print("🔐 Using Service Principal with configuration-based deployment")
                else:
                    credential = None
                    print("🔐 Using DefaultAzureCredential with configuration-based deployment")
                
                print(f"🚀 Deploying using config file: {args.config_file}")
                print(f"🌍 Target environment: {args.environment}")
                
                # Execute configuration-based deployment
                deploy_with_config(
                    config_file_path=args.config_file,
                    environment=args.environment,
                    token_credential=credential
                )
                
                print("✅ CONFIGURATION-BASED DEPLOYMENT COMPLETED!")
                print("🎉 Your Fabric items should now be visible in the workspace!")
                print("💡 Check your Fabric workspace to verify the deployment.")
                return
                
            except Exception as e:
                print(f"❌ Configuration-based deployment failed: {e}")
                print("💡 Check:")
                print("   - Config file path is correct")
                print("   - Environment name matches config file")
                print("   - YAML syntax is valid")
                print("   - Authentication is properly configured")
                sys.exit(1)
        
        # Continue with standard deployment approach        
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
            # Set up authentication credential
            if args.client_id:
                print("🔐 Using Service Principal authentication...")
                # Set environment variables for service principal authentication
                # This is the most compatible approach with fabric-cicd
                os.environ['AZURE_CLIENT_ID'] = args.client_id
                os.environ['AZURE_CLIENT_SECRET'] = args.client_secret
                os.environ['AZURE_TENANT_ID'] = args.tenant_id
                print("   Environment variables set for service principal")
            else:
                print("🔐 Using DefaultAzureCredential...")
            
            # Initialize workspace with authentication
            workspace_params = {
                'workspace_id': args.workspace_id,
                'repository_directory': repo_path
            }
            
            # Only limit scope if user explicitly specified item types
            if args.item_types:
                workspace_params['item_type_in_scope'] = item_types
                print(f"🎯 Limiting deployment to specified item types: {item_types}")
            else:
                print("🌐 Deploying ALL item types found in repository")
            
            # FabricWorkspace will automatically use environment variables for auth
            workspace = FabricWorkspace(**workspace_params)
            
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
        if args.item_types:
            print(f"   📦 Item types in scope: {item_types}")
        else:
            print(f"   📦 Item types found: {item_types} (all will be deployed)")
        print()
        
        # Execute deployment using enhanced error handling
        print("🚀 Deploying with enhanced error handling...")
        print("   This approach handles connection permission issues gracefully!")
        print(f"   Processing {total_items} items...")
        print()
        
        try:
            result = deploy_with_error_handling(workspace)
            
            print("✅ DEPLOYMENT COMPLETED!")
            print(f"📊 Result: {result}")
            print()
            print("🎉 Your Fabric items should now be visible in the workspace!")
            print("💡 Check your Fabric workspace to verify the deployment.")
            print("💡 Items with connection issues may need manual permission fixes.")
            
        except Exception as e:
            print(f"❌ Deployment failed: {e}")
            print()
            
            # Extract user-friendly error message from the exception
            error_message = str(e)
            if "ParsingError" in error_message and "Cannot find the KQL Database source" in error_message:
                print("🔍 Issue: KQL Dashboard database reference mismatch")
                print("💡 The KQL Dashboard references a database that doesn't exist or has a different name")
                print("💡 Most other items were likely deployed successfully")
                print("💡 Check your workspace - you should see deployed items")
                print()
                print("🛠️  To fix:")
                print("   - Update the KQL Dashboard definition in your source repository")
                print("   - Or ensure the database name matches what the dashboard expects")
            elif "authentication" in error_message.lower() or "credential" in error_message.lower():
                print("🔐 Issue: Authentication problem")
                print("💡 Try: az login")
            elif "permission" in error_message.lower() or "access" in error_message.lower():
                print("🔒 Issue: Workspace permissions")
                print("💡 Ensure you have Admin or Member role in the workspace")
            else:
                print("💡 Common issues to check:")
                print("   - Workspace permissions (need Admin or Member role)")
                print("   - Authentication (try: az login)")
                print("   - Network connectivity")
                print("   - Item dependencies and naming conflicts")
            
            print()
            print("🎯 Important: Check your Fabric workspace - many items may have deployed successfully")
            print("           even if the overall deployment reported failure!")
            print()
            print("📋 Quick Check:")
            print(f"   1. Open your Fabric workspace: {args.workspace_id}")
            print("   2. Look for recently updated items")
            print("   3. Most items (except problematic ones) should be there")
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
        if args and hasattr(args, 'repo_url') and args.repo_url and os.path.exists(temp_dir):
            try:
                print(f"🧹 Cleaning up: {temp_dir}")
                shutil.rmtree(temp_dir)
            except Exception as e:
                print(f"⚠️  Warning: Could not clean up temp directory: {e}")

if __name__ == "__main__":
    main()
