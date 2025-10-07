#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive Fabric Deployment Script
====================================

Interactive wrapper for manual deployments from VS Code.
This script provides a user-friendly interface for deploying Fabric items
by prompting for all required parameters.

Features:
✅ Interactive prompts for all deployment parameters
✅ Compatibility checking (Python version, fabric-cicd version)
✅ Connection validation
✅ Repository analysis before deployment
✅ Support for both Git repositories and local paths
✅ Environment detection and activation verification
✅ Clear progress indicators and error handling

Usage:
    python manual/interactive_deploy.py

Requirements:
    - Python 3.8+ with activated virtual environment
    - fabric-cicd >=0.1.29
    - Required dependencies (GitPython, azure-identity, etc.)
"""

import os
import sys
import subprocess
from pathlib import Path

# Add the core directory to Python path for imports
current_dir = Path(__file__).parent.absolute()
core_dir = current_dir.parent / "core"
sys.path.insert(0, str(core_dir))

def print_banner():
    """Print welcome banner"""
    print("=" * 70)
    print("🚀 Microsoft Fabric Interactive Deployment")
    print("=" * 70)
    print("📋 This tool will guide you through deploying Fabric items")
    print("🔧 Manual deployment from VS Code with interactive prompts")
    print("=" * 70)
    print()

def check_environment():
    """Check if we're in the correct environment and all dependencies are available"""
    print("🔍 Checking environment and dependencies...")
    print()
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python version incompatible")
        print(f"   Current: {sys.version.split()[0]}")
        print("   Required: Python 3.8 or higher")
        print()
        print("💡 Please run from the envsetup directory:")
        print("   cd envsetup")
        print("   .\\activate_fabric_env_pyenv.bat")
        return False
    
    print(f"✅ Python version: {sys.version.split()[0]}")
    
    # Check required dependencies
    required_packages = [
        ('fabric_cicd', 'fabric-cicd'),
        ('git', 'GitPython'),
        ('azure.identity', 'azure-identity'),
        ('yaml', 'PyYAML')
    ]
    
    missing_packages = []
    for import_name, package_name in required_packages:
        try:
            __import__(import_name)
            print(f"✅ {package_name}: Available")
        except ImportError:
            print(f"❌ {package_name}: Missing")
            missing_packages.append(package_name)
    
    if missing_packages:
        print()
        print("❌ Missing required dependencies!")
        print("💡 Missing packages:", ', '.join(missing_packages))
        print()
        print("🔧 The launcher will attempt to install these automatically...")
        return False
    
    # Check fabric-cicd version
    try:
        import fabric_cicd  # type: ignore
        from packaging import version
        
        current_version = fabric_cicd.__version__
        required_version = "0.1.29"
        
        if version.parse(current_version) >= version.parse(required_version):
            print(f"✅ fabric-cicd version: {current_version}")
        else:
            print(f"⚠️  fabric-cicd version: {current_version} (recommend upgrading to {required_version}+)")
            
    except Exception as e:
        print(f"⚠️  Could not verify fabric-cicd version: {e}")
    
    print()
    print("✅ Environment check completed!")
    print()
    return True

def get_user_input(prompt, default=None, required=True):
    """Get user input with optional default value"""
    if default:
        full_prompt = f"{prompt} [{default}]: "
    else:
        full_prompt = f"{prompt}: "
    
    while True:
        user_input = input(full_prompt).strip()
        
        if user_input:
            return user_input
        elif default:
            return default
        elif not required:
            return None
        else:
            print("❌ This field is required. Please provide a value.")

def get_yes_no(prompt, default=True):
    """Get yes/no input from user"""
    default_text = "Y/n" if default else "y/N"
    response = input(f"{prompt} [{default_text}]: ").strip().lower()
    
    if not response:
        return default
    return response.startswith('y')

def validate_workspace_id(workspace_id):
    """Validate workspace ID format (should be a GUID)"""
    import re
    guid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(guid_pattern, workspace_id.lower()))

def get_deployment_parameters():
    """Collect all deployment parameters from user"""
    print("📋 Deployment Configuration")
    print("-" * 30)
    
    # Workspace ID
    while True:
        workspace_id = get_user_input("🎯 Enter Fabric Workspace ID (GUID)")
        if validate_workspace_id(workspace_id):
            break
        print("❌ Invalid workspace ID format. Please enter a valid GUID.")
        print("💡 Example: 12345678-1234-1234-1234-123456789abc")
        print()
    
    print(f"✅ Workspace ID: {workspace_id}")
    print()
    
    # Repository or local path
    use_git = get_yes_no("📁 Deploy from Git repository? (No = use local path)", True)
    
    if use_git:
        # Git repository details
        print("📦 Git Repository Configuration")
        print("-" * 30)
        
        repo_url = get_user_input("🔗 Repository URL", 
                                "https://dev.azure.com/yourorg/YourProject/_git/YourRepo")
        
        branch = get_user_input("🌿 Branch name", "development")
        
        print(f"✅ Repository: {repo_url}")
        print(f"✅ Branch: {branch}")
        print()
        
        local_path = None
    else:
        # Local path
        local_path = get_user_input("📂 Local path containing Fabric items")
        if local_path and not os.path.exists(local_path):
            print(f"⚠️  Warning: Path '{local_path}' does not exist")
        
        repo_url = None
        branch = None
    
    # Advanced options
    print("⚙️  Advanced Options (press Enter to skip)")
    print("-" * 30)
    
    # Ask if user wants to deploy all items or specific types
    deploy_all = get_yes_no("📦 Deploy ALL item types found in repository?", True)
    
    item_types = None
    if not deploy_all:
        item_types_input = get_user_input("📋 Specific item types (comma-separated, e.g., Notebook,Lakehouse)", 
                                        required=True)
        if item_types_input:
            item_types = [t.strip() for t in item_types_input.split(',')]
            print(f"✅ Will deploy only: {', '.join(item_types)}")
    else:
        print("✅ Will deploy ALL item types found in repository")
    
    dry_run = get_yes_no("🔍 Dry run? (analyze without deploying)", False)
    
    # Authentication options
    use_service_principal = get_yes_no("🔐 Use Service Principal authentication? (No = use current user)", False)
    
    client_id = client_secret = tenant_id = None
    if use_service_principal:
        print("🔐 Service Principal Configuration")
        print("-" * 30)
        client_id = get_user_input("Client ID")
        client_secret = get_user_input("Client Secret")
        tenant_id = get_user_input("Tenant ID")
    
    return {
        'workspace_id': workspace_id,
        'repo_url': repo_url,
        'local_path': local_path,
        'branch': branch,
        'item_types': item_types,
        'dry_run': dry_run,
        'client_id': client_id,
        'client_secret': client_secret,
        'tenant_id': tenant_id
    }

def build_command(params):
    """Build the deployment command from parameters"""
    cmd = [sys.executable, str(core_dir / "fabric_deploy.py")]
    
    # Required parameters
    cmd.extend(['--workspace-id', params['workspace_id']])
    
    # Repository or local path
    if params['repo_url']:
        cmd.extend(['--repo-url', params['repo_url']])
        if params['branch']:
            cmd.extend(['--branch', params['branch']])
    else:
        cmd.extend(['--local-path', params['local_path']])
    
    # Optional parameters
    if params['item_types']:
        cmd.extend(['--item-types'] + params['item_types'])
    
    if params['dry_run']:
        cmd.append('--dry-run')
    
    # Service Principal authentication
    if params['client_id']:
        cmd.extend(['--client-id', params['client_id']])
        cmd.extend(['--client-secret', params['client_secret']])
        cmd.extend(['--tenant-id', params['tenant_id']])
    
    return cmd

def preview_deployment(params):
    """Show deployment preview to user"""
    print("🎯 Deployment Preview")
    print("=" * 50)
    print(f"📍 Target Workspace: {params['workspace_id']}")
    
    if params['repo_url']:
        print(f"📦 Repository: {params['repo_url']}")
        print(f"🌿 Branch: {params['branch']}")
    else:
        print(f"📂 Local Path: {params['local_path']}")
    
    if params['item_types']:
        print(f"📋 Item Types: {', '.join(params['item_types'])} (specific types only)")
    else:
        print("📋 Item Types: ALL types found in repository")
    
    print(f"🔍 Mode: {'Dry Run (Analysis Only)' if params['dry_run'] else 'Full Deployment'}")
    print(f"🔐 Authentication: {'Service Principal' if params['client_id'] else 'Current User'}")
    print("=" * 50)
    print()

def run_deployment(cmd):
    """Execute the deployment command"""
    print("🚀 Starting Deployment...")
    print("=" * 50)
    print(f"📝 Command: {' '.join(cmd[:3])} [parameters...]")
    print()
    
    try:
        # Run the deployment
        result = subprocess.run(cmd, capture_output=False, text=True)
        
        if result.returncode == 0:
            print()
            print("✅ Deployment completed successfully!")
        else:
            print()
            print(f"❌ Deployment failed with exit code: {result.returncode}")
            return False
            
    except KeyboardInterrupt:
        print("\n⏹️  Deployment cancelled by user")
        return False
    except Exception as e:
        print(f"\n❌ Error running deployment: {e}")
        return False
    
    return True

def main():
    """Main interactive deployment function"""
    try:
        print_banner()
        
        # Environment check
        if not check_environment():
            print("❌ Environment check failed - missing dependencies detected.")
            sys.exit(1)
        
        # Get deployment parameters
        params = get_deployment_parameters()
        
        # Preview deployment
        preview_deployment(params)
        
        # Confirm deployment
        if not get_yes_no("🚀 Proceed with deployment?", True):
            print("⏹️  Deployment cancelled by user")
            sys.exit(0)
        
        # Build and run command
        cmd = build_command(params)
        success = run_deployment(cmd)
        
        if success:
            print()
            print("🎉 Interactive deployment completed!")
            print("💡 Check your Fabric workspace to verify the deployment.")
        else:
            print()
            print("❌ Deployment encountered issues. Please check the output above.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()