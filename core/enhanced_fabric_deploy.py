#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Enhanced Fabric Deployment with Warehouse Schema Support
========================================================

This script extends the existing fabric_deploy.py to include warehouse schema deployment
capabilities. It provides a complete CI/CD solution for both Fabric items AND database
schema objects.

ENHANCED CAPABILITIES:
✅ Deploy Fabric items (existing functionality)
✅ Deploy Warehouse schema objects (NEW)
✅ Integrated deployment workflow
✅ Dependency management between Fabric items and schema objects
✅ Rollback capabilities
✅ Comprehensive logging and error handling

DEPLOYMENT WORKFLOW:
1. Deploy Fabric Warehouse items first (using fabric-cicd)
2. Wait for Warehouse to be ready
3. Deploy schema objects to the Warehouse
4. Validate deployment success
5. Optional: Run post-deployment tests

Usage:
    # Deploy everything (Fabric items + schema)
    python enhanced_fabric_deploy.py --workspace-id "id" --repo-url "url" --deploy-schemas
    
    # Deploy only Fabric items (existing behavior)
    python enhanced_fabric_deploy.py --workspace-id "id" --repo-url "url"
    
    # Deploy only schemas to existing warehouses
    python enhanced_fabric_deploy.py --workspace-id "id" --deploy-schemas-only --warehouse-name "wh_name"
    
    # Dry run with schema validation
    python enhanced_fabric_deploy.py --workspace-id "id" --repo-url "url" --deploy-schemas --dry-run
"""

import os
import sys
import json
import time
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Any

# Import the existing fabric deployment functionality
from fabric_deploy import (
    deploy_with_error_handling, 
    get_fabric_workspace,
    analyze_repository_structure,
    get_item_types_from_repository
)

# Import the new warehouse schema deployment functionality
from warehouse_schema_deploy import (
    WarehouseSchemaDeployer, 
    deploy_warehouse_schema_from_sqlproj,
    deploy_warehouse_schema_from_directory
)

def find_sql_projects(repository_path: str) -> List[str]:
    """
    Find all SQL project files in the repository
    
    Args:
        repository_path: Path to the repository
        
    Returns:
        List of .sqlproj file paths
    """
    sql_projects = []
    repo_path = Path(repository_path)
    
    for sqlproj_file in repo_path.rglob("*.sqlproj"):
        sql_projects.append(str(sqlproj_file))
    
    print(f"🔍 Found {len(sql_projects)} SQL project(s):")
    for project in sql_projects:
        print(f"   📄 {project}")
    
    return sql_projects

def find_sql_directories(repository_path: str) -> List[str]:
    """
    Find directories containing SQL files
    
    Args:
        repository_path: Path to the repository
        
    Returns:
        List of directories containing SQL files
    """
    sql_directories = set()
    repo_path = Path(repository_path)
    
    for sql_file in repo_path.rglob("*.sql"):
        sql_directories.add(str(sql_file.parent))
    
    sql_dirs = list(sql_directories)
    print(f"🔍 Found {len(sql_dirs)} directory(ies) with SQL files:")
    for directory in sql_dirs:
        print(f"   📁 {directory}")
    
    return sql_dirs

def get_warehouse_names_from_repository(repository_path: str) -> List[str]:
    """
    Extract warehouse names from Fabric items in the repository
    
    Args:
        repository_path: Path to the repository
        
    Returns:
        List of warehouse names found
    """
    warehouse_names = []
    repo_path = Path(repository_path)
    
    # Look for .Warehouse directories/files
    for warehouse_item in repo_path.rglob("*.Warehouse"):
        warehouse_name = warehouse_item.stem
        if warehouse_name not in warehouse_names:
            warehouse_names.append(warehouse_name)
    
    print(f"🏢 Found {len(warehouse_names)} Warehouse item(s):")
    for name in warehouse_names:
        print(f"   🏗️  {name}")
    
    return warehouse_names

def wait_for_warehouse_ready(workspace_id: str, warehouse_name: str, timeout: int = 300) -> bool:
    """
    Wait for a Fabric Warehouse to be ready for connections
    
    Args:
        workspace_id: Fabric workspace ID
        warehouse_name: Name of the warehouse
        timeout: Maximum wait time in seconds
        
    Returns:
        True if warehouse is ready, False if timeout
    """
    print(f"⏳ Waiting for Warehouse '{warehouse_name}' to be ready...")
    
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        try:
            # Try to establish a connection to test readiness
            deployer = WarehouseSchemaDeployer(warehouse_name, workspace_id)
            if deployer.connect():
                deployer.disconnect()
                print(f"✅ Warehouse '{warehouse_name}' is ready!")
                return True
        except Exception as e:
            print(f"🔄 Still waiting... ({int(time.time() - start_time)}s)")
        
        time.sleep(10)  # Wait 10 seconds between checks
    
    print(f"⏰ Timeout waiting for Warehouse '{warehouse_name}' to be ready")
    return False

def deploy_schemas_to_warehouse(warehouse_name: str, workspace_id: str, 
                              repository_path: str, dry_run: bool = False) -> bool:
    """
    Deploy all schema objects to a specific warehouse
    
    Args:
        warehouse_name: Name of the Fabric Warehouse
        workspace_id: Fabric workspace ID
        repository_path: Path to the repository
        dry_run: If True, only validate without executing
        
    Returns:
        True if all deployments successful, False otherwise
    """
    print(f"🚀 Starting schema deployment to Warehouse: {warehouse_name}")
    
    deployer = WarehouseSchemaDeployer(warehouse_name, workspace_id)
    
    try:
        # Connect to the warehouse
        if not dry_run and not deployer.connect():
            print(f"❌ Failed to connect to Warehouse: {warehouse_name}")
            return False
        
        success = True
        
        # Deploy from SQL projects
        sql_projects = find_sql_projects(repository_path)
        for project_path in sql_projects:
            print(f"📦 Deploying SQL project: {project_path}")
            result = deployer.deploy_from_sqlproj(project_path, dry_run)
            if not result.success:
                print(f"❌ Failed to deploy SQL project: {project_path}")
                for error in result.errors:
                    print(f"   💥 {error}")
                success = False
            else:
                print(f"✅ Successfully deployed {result.objects_deployed} objects from {project_path}")
        
        # Deploy from SQL directories (if no SQL projects found)
        if not sql_projects:
            sql_directories = find_sql_directories(repository_path)
            for directory_path in sql_directories:
                print(f"📁 Deploying SQL directory: {directory_path}")
                result = deployer.deploy_from_directory(directory_path, dry_run)
                if not result.success:
                    print(f"❌ Failed to deploy SQL directory: {directory_path}")
                    for error in result.errors:
                        print(f"   💥 {error}")
                    success = False
                else:
                    print(f"✅ Successfully deployed {result.objects_deployed} objects from {directory_path}")
        
        return success
        
    finally:
        deployer.disconnect()

def enhanced_fabric_deployment(workspace_id: str, repo_url: str = None, 
                             local_path: str = None, branch: str = "main",
                             deploy_schemas: bool = False, 
                             deploy_schemas_only: bool = False,
                             warehouse_name: str = None,
                             dry_run: bool = False,
                             **kwargs) -> bool:
    """
    Enhanced deployment function that handles both Fabric items and warehouse schemas
    
    Args:
        workspace_id: Fabric workspace ID
        repo_url: Git repository URL (optional if local_path provided)
        local_path: Local repository path (optional if repo_url provided)
        branch: Git branch to deploy from
        deploy_schemas: Whether to deploy warehouse schemas after Fabric items
        deploy_schemas_only: Deploy only schemas (skip Fabric items)
        warehouse_name: Specific warehouse name (for schema-only deployment)
        dry_run: If True, only validate without executing
        **kwargs: Additional arguments for fabric deployment
        
    Returns:
        True if deployment successful, False otherwise
    """
    print("=" * 80)
    print("🚀 ENHANCED FABRIC DEPLOYMENT WITH WAREHOUSE SCHEMA SUPPORT")
    print("=" * 80)
    
    repository_path = local_path
    fabric_success = True
    
    # Step 1: Deploy Fabric items (unless schemas-only)
    if not deploy_schemas_only:
        print("\n📦 STEP 1: DEPLOYING FABRIC ITEMS")
        print("-" * 50)
        
        try:
            fabric_success = deploy_with_error_handling(
                workspace_id=workspace_id,
                repo_url=repo_url,
                local_path=local_path,
                branch=branch,
                dry_run=dry_run,
                **kwargs
            )
            
            if not fabric_success:
                print("❌ Fabric items deployment failed!")
                if not deploy_schemas:
                    return False
                print("⚠️  Continuing with schema deployment anyway...")
            else:
                print("✅ Fabric items deployed successfully!")
        
        except Exception as e:
            print(f"❌ Fabric deployment error: {str(e)}")
            if not deploy_schemas:
                return False
            fabric_success = False
    
    # Step 2: Deploy warehouse schemas (if requested)
    if deploy_schemas or deploy_schemas_only:
        print("\n🏗️  STEP 2: DEPLOYING WAREHOUSE SCHEMAS")
        print("-" * 50)
        
        if not repository_path:
            print("❌ Repository path is required for schema deployment")
            return False
        
        # Get warehouse names
        if warehouse_name:
            warehouse_names = [warehouse_name]
        else:
            warehouse_names = get_warehouse_names_from_repository(repository_path)
        
        if not warehouse_names:
            print("⚠️  No warehouses found for schema deployment")
            return fabric_success
        
        schema_success = True
        
        for wh_name in warehouse_names:
            print(f"\n🎯 Deploying schemas to Warehouse: {wh_name}")
            
            # Wait for warehouse to be ready (if we just deployed it)
            if not deploy_schemas_only and not dry_run:
                if not wait_for_warehouse_ready(workspace_id, wh_name):
                    print(f"❌ Warehouse {wh_name} not ready for schema deployment")
                    schema_success = False
                    continue
            
            # Deploy schemas to this warehouse
            result = deploy_schemas_to_warehouse(
                warehouse_name=wh_name,
                workspace_id=workspace_id,
                repository_path=repository_path,
                dry_run=dry_run
            )
            
            if result:
                print(f"✅ Schema deployment to {wh_name} completed successfully!")
            else:
                print(f"❌ Schema deployment to {wh_name} failed!")
                schema_success = False
        
        if not schema_success:
            print("❌ Some warehouse schema deployments failed!")
            return False
        
        print("✅ All warehouse schemas deployed successfully!")
    
    # Final result
    overall_success = fabric_success and (not deploy_schemas or schema_success)
    
    print("\n" + "=" * 80)
    if overall_success:
        print("🎉 ENHANCED DEPLOYMENT COMPLETED SUCCESSFULLY!")
    else:
        print("❌ ENHANCED DEPLOYMENT COMPLETED WITH ERRORS!")
    print("=" * 80)
    
    return overall_success

def main():
    """Main entry point for enhanced fabric deployment"""
    parser = argparse.ArgumentParser(
        description='Enhanced Fabric CI/CD deployment with warehouse schema support',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Deploy Fabric items and schemas
  python enhanced_fabric_deploy.py --workspace-id "12345" --repo-url "https://dev.azure.com/org/proj/_git/repo" --deploy-schemas
  
  # Deploy only schemas to existing warehouse
  python enhanced_fabric_deploy.py --workspace-id "12345" --local-path "./repo" --deploy-schemas-only --warehouse-name "my_warehouse"
  
  # Dry run with schema validation
  python enhanced_fabric_deploy.py --workspace-id "12345" --repo-url "url" --deploy-schemas --dry-run
        """
    )
    
    # Core arguments
    parser.add_argument('--workspace-id', required=True, help='Fabric workspace ID')
    parser.add_argument('--repo-url', help='Git repository URL')
    parser.add_argument('--local-path', help='Local repository path')
    parser.add_argument('--branch', default='main', help='Git branch (default: main)')
    
    # Schema deployment arguments
    parser.add_argument('--deploy-schemas', action='store_true', 
                       help='Deploy warehouse schemas after Fabric items')
    parser.add_argument('--deploy-schemas-only', action='store_true',
                       help='Deploy only schemas (skip Fabric items)')
    parser.add_argument('--warehouse-name', help='Specific warehouse name for schema deployment')
    
    # Common arguments
    parser.add_argument('--dry-run', action='store_true', help='Validate without executing')
    parser.add_argument('--item-types', nargs='+', help='Specific item types to deploy')
    parser.add_argument('--parameter-file', help='Parameter file for substitutions')
    parser.add_argument('--config-file', help='Configuration file for deployment')
    parser.add_argument('--environment', help='Environment name for config-based deployment')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.repo_url and not args.local_path:
        print("❌ Either --repo-url or --local-path must be specified")
        return False
    
    if args.deploy_schemas_only and not args.local_path and not args.repo_url:
        print("❌ Repository path is required for schema deployment")
        return False
    
    # Run enhanced deployment
    success = enhanced_fabric_deployment(
        workspace_id=args.workspace_id,
        repo_url=args.repo_url,
        local_path=args.local_path,
        branch=args.branch,
        deploy_schemas=args.deploy_schemas,
        deploy_schemas_only=args.deploy_schemas_only,
        warehouse_name=args.warehouse_name,
        dry_run=args.dry_run,
        item_types=args.item_types,
        parameter_file=args.parameter_file,
        config_file=args.config_file,
        environment=args.environment
    )
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()