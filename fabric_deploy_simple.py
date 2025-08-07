#!/usr/bin/env python3
"""
Simple Fabric Deployment Script using fabric-cicd library
Following the basic usage pattern from documentation:
https://github.com/microsoft/fabric-cicd

This uses the simple publish_all_items() function as recommended.
"""

import os
import sys
import tempfile
import shutil
import argparse
from pathlib import Path
from git import Repo
from azure.identity import DefaultAzureCredential
from fabric_cicd import FabricWorkspace, publish_all_items

def main():
    parser = argparse.ArgumentParser(description='Deploy Fabric items using fabric-cicd library (simple approach)')
    parser.add_argument('--workspace-id', required=True, help='Fabric workspace ID')
    parser.add_argument('--repo-url', required=True, help='Azure DevOps repository URL')
    parser.add_argument('--branch', default='main', help='Git branch to deploy from')
    parser.add_argument('--use-default-auth', action='store_true', help='Use DefaultAzureCredential')
    
    args = parser.parse_args()
    
    # Create temporary directory for repository
    temp_dir = tempfile.mkdtemp(prefix='fabric_simple_')
    repo_path = None
    
    try:
        print("🚀 SIMPLE FABRIC DEPLOYMENT")
        print("=" * 50)
        print(f"📂 Temporary directory: {temp_dir}")
        print(f"🔗 Repository: {args.repo_url}")
        print(f"🌿 Branch: {args.branch}")
        print(f"🎯 Workspace ID: {args.workspace_id}")
        print()
        
        # Clone repository
        print("📥 Cloning repository...")
        repo = Repo.clone_from(args.repo_url, temp_dir)
        
        # Checkout specific branch
        if args.branch != 'main':
            print(f"🔀 Switching to branch: {args.branch}")
            repo.git.checkout(args.branch)
        
        repo_path = temp_dir
        print(f"✅ Repository ready at: {repo_path}")
        print()
        
        # List contents to verify
        print("📁 Repository contents:")
        for item in os.listdir(repo_path):
            item_path = os.path.join(repo_path, item)
            if os.path.isdir(item_path):
                print(f"   📂 {item}/")
                # List items in subdirectory
                for subitem in os.listdir(item_path):
                    print(f"      📄 {subitem}")
            else:
                print(f"   📄 {item}")
        print()
        
        # Initialize FabricWorkspace using the documented pattern
        print("🔧 Initializing FabricWorkspace...")
        
        # Specify item types that are in our repository
        item_types = ["Notebook", "Lakehouse", "Warehouse"]
        
        workspace = FabricWorkspace(
            workspace_id=args.workspace_id,
            repository_directory=repo_path,
            item_type_in_scope=item_types
        )
        
        print(f"✅ FabricWorkspace initialized")
        print(f"   📁 Repository directory: {repo_path}")
        print(f"   🎯 Workspace ID: {args.workspace_id}")
        print(f"   📦 Item types in scope: {item_types}")
        print()
        
        # Use the simple publish_all_items function as documented
        print("🚀 Publishing all items using publish_all_items()...")
        print("   This will deploy:")
        print("   • Migration/ folder with 7 items (6 notebooks + 1 lakehouse)")
        print("   • Warehouse/ folder with 1 warehouse")
        print()
        
        # Execute the deployment
        result = publish_all_items(workspace)
        
        print("✅ Deployment completed!")
        print(f"📊 Result: {result}")
        
    except Exception as e:
        print(f"❌ Error during deployment: {str(e)}")
        import traceback
        print("📋 Full traceback:")
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
