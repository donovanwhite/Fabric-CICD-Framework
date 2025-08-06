"""
Cross-Region Migration Examples
==============================

This file contains practical examples for common cross-region migration scenarios
using the fabric-cicd library.

Run these examples after setting up your parameter.yml file with actual values.

Command Line Usage:
    python migration_examples.py --scenario 1 --workspace-id "WORKSPACE_ID" --target-env PROD
    python migration_examples.py --scenario 7 --workspace-id "WORKSPACE_ID" --simple --items "Notebook Report"
    python migration_examples.py --scenario 4 --workspace-id "WORKSPACE_ID" --target-env DEV --dry-run
"""

import os
import argparse
from pathlib import Path
from fabric_deploy_local import FabricDeployment

# =============================================================================
# COMMAND LINE ARGUMENT PARSING
# =============================================================================

def parse_arguments():
    """Parse command line arguments for migration examples"""
    parser = argparse.ArgumentParser(
        description='Microsoft Fabric Cross-Region Migration Examples',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run analytics migration to PROD
  python migration_examples.py --scenario 1 --workspace-id "33333333-3333-3333-3333-333333333333" --target-env PROD

  # Simple deployment with specific items
  python migration_examples.py --scenario 7 --workspace-id "11111111-1111-1111-1111-111111111111" --simple --items "Notebook Report"

  # Dry run validation
  python migration_examples.py --scenario 1 --workspace-id "11111111-1111-1111-1111-111111111111" --target-env DEV --dry-run

  # Deploy specific items with parameterization
  python migration_examples.py --scenario 5 --workspace-id "22222222-2222-2222-2222-222222222222" --target-env STAGING --items "Lakehouse Warehouse"

Available Item Types:
  Notebook, Report, Dashboard, SemanticModel, Lakehouse, Warehouse, 
  DataPipeline, Dataflow, Environment, Eventhouse, Eventstream, 
  KQLDatabase, KQLQueryset, MLModel, MLExperiment
        """
    )
    
    # Required arguments
    parser.add_argument('--scenario', type=int, choices=range(1, 9), required=True,
                       help='Migration scenario to run (1-8)')
    parser.add_argument('--workspace-id', type=str, required=True,
                       help='Target Fabric workspace ID (GUID format)')
    
    # Deployment mode - mutually exclusive
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--target-env', choices=['DEV', 'STAGING', 'PROD'],
                           help='Target environment for parameterized deployment')
    mode_group.add_argument('--simple', action='store_true',
                           help='Simple deployment (keep original names)')
    
    # Optional arguments
    parser.add_argument('--items', type=str, nargs='+',
                       help='Space-separated list of item types to deploy')
    parser.add_argument('--dry-run', action='store_true',
                       help='Validation only - no actual deployment')
    parser.add_argument('--repository-path', type=str, 
                       default=r"C:\source\repos\Fabric\cicd\migrate",
                       help='Path to repository containing Fabric items')
    
    return parser.parse_args()

# =============================================================================
# CONFIGURATION EXAMPLES  
# =============================================================================

# Example workspace configurations for different regions
WORKSPACE_CONFIGS = {
    'dev': {
        'workspace_id': '11111111-1111-1111-1111-111111111111',  # Replace with actual
        'environment': 'DEV',
        'region': 'East US'
    },
    'staging': {
        'workspace_id': '22222222-2222-2222-2222-222222222222',  # Replace with actual
        'environment': 'STAGING', 
        'region': 'Central US'
    },
    'prod': {
        'workspace_id': '33333333-3333-3333-3333-333333333333',  # Replace with actual
        'environment': 'PROD',
        'region': 'West Europe'
    }
}

# =============================================================================
# UPDATED SCENARIO FUNCTIONS WITH COMMAND LINE SUPPORT
# =============================================================================

def analytics_migration_example(args):
    """
    Migrate analytics workload: Lakehouse + Warehouse + Reports + Semantic Models
    From DEV (East US) to PROD (West Europe)
    """
    
    print("📊 Analytics Workload Migration Example")
    print("="*50)
    
    # Initialize deployment
    deployment = FabricDeployment(args.repository_path)
    
    # Analytics-specific item types (unless overridden by --items)
    analytics_items = args.items if args.items else [
        'Lakehouse',      # Data lake storage
        'Warehouse',      # SQL analytics
        'SemanticModel',  # Power BI datasets
        'Report',         # Power BI reports
        'Dashboard'       # Power BI dashboards
    ]
    
    print("🎯 Target: Analytics items migration")
    print(f"📦 Items: {', '.join(analytics_items)}")
    print(f"🏢 Workspace: {args.workspace_id}")
    print(f"🔧 Mode: {'Simple' if args.simple else f'Parameterized ({args.target_env})'}")
    print(f"🔍 Dry Run: {'Yes' if args.dry_run else 'No'}")
    
    # Execute deployment based on mode
    if args.simple:
        deployment.deploy_without_parameterization(
            workspace_id=args.workspace_id,
            item_types=analytics_items,
            dry_run=args.dry_run
        )
    else:
        deployment.deploy(
            workspace_id=args.workspace_id,
            environment=args.target_env,
            item_types=analytics_items,
            dry_run=args.dry_run
        )

# =============================================================================
# SCENARIO 2: DATA ENGINEERING PIPELINE MIGRATION  
# =============================================================================

def data_engineering_migration_example(args):
    """
    Migrate data engineering workload: Notebooks + Pipelines + Environments
    From STAGING (Central US) to PROD (West Europe)
    """
    
    print("🔧 Data Engineering Migration Example")
    print("="*50)
    
    deployment = FabricDeployment(args.repository_path)
    
    # Data engineering item types (unless overridden by --items)
    engineering_items = args.items if args.items else [
        'Notebook',       # Spark notebooks
        'DataPipeline',   # ETL pipelines
        'Environment',    # Spark environments  
        'Lakehouse'       # Target data storage
    ]
    
    print("🎯 Target: Data engineering pipeline")
    print(f"📦 Items: {', '.join(engineering_items)}")
    print(f"🏢 Workspace: {args.workspace_id}")
    print(f"🔧 Mode: {'Simple' if args.simple else f'Parameterized ({args.target_env})'}")
    
    # Execute deployment based on mode
    if args.simple:
        deployment.deploy_without_parameterization(
            workspace_id=args.workspace_id,
            item_types=engineering_items,
            dry_run=args.dry_run
        )
    else:
        deployment.deploy(
            workspace_id=args.workspace_id,
            environment=args.target_env,
            item_types=engineering_items,
            dry_run=args.dry_run
        )

# =============================================================================
# SCENARIO 3: REAL-TIME ANALYTICS MIGRATION
# =============================================================================

def realtime_analytics_migration_example():
    """
    Migrate real-time analytics: Eventhouses + Eventstreams + KQL
    From DEV to PROD across regions
    """
    
    print("⚡ Real-Time Analytics Migration Example")
    print("="*50)
    
    repository_path = r"C:\source\repos\Fabric\cicd\migrate"
    deployment = FabricDeployment(repository_path)
    
    # Real-time analytics items
    realtime_items = [
        'Eventhouse',     # Real-time database
        'Eventstream',    # Event streaming
        'KQLDatabase',    # KQL database
        'KQLQueryset'     # KQL queries
    ]
    
    print("🎯 Target: Real-time analytics DEV → PROD")
    print(f"📦 Items: {', '.join(realtime_items)}")
    
    deployment.cross_region_migration(
        source_workspace=WORKSPACE_CONFIGS['dev']['workspace_id'],
        target_workspace=WORKSPACE_CONFIGS['prod']['workspace_id'],
        source_env='DEV',
        target_env='PROD',
        item_types=realtime_items
    )

# =============================================================================
# SCENARIO 4: PHASED MIGRATION STRATEGY
# =============================================================================

def phased_migration_example():
    """
    Demonstrate phased migration approach:
    1. Infrastructure items first (Lakehouse, Warehouse, Environment)
    2. Processing items second (Notebooks, Pipelines)  
    3. Analytics items last (Reports, Dashboards)
    """
    
    print("📋 Phased Migration Strategy Example")
    print("="*50)
    
    repository_path = r"C:\source\repos\Fabric\cicd\migrate"
    deployment = FabricDeployment(repository_path)
    
    # Phase 1: Infrastructure
    phase1_items = ['Lakehouse', 'Warehouse', 'Environment']
    print(f"\n🏗️  Phase 1 - Infrastructure: {', '.join(phase1_items)}")
    deployment.deploy(
        workspace_id=WORKSPACE_CONFIGS['prod']['workspace_id'],
        environment='PROD',
        item_types=phase1_items
    )
    
    # Phase 2: Data Processing  
    phase2_items = ['Notebook', 'DataPipeline', 'Dataflow']
    print(f"\n⚙️  Phase 2 - Data Processing: {', '.join(phase2_items)}")
    deployment.deploy(
        workspace_id=WORKSPACE_CONFIGS['prod']['workspace_id'],
        environment='PROD',
        item_types=phase2_items
    )
    
    # Phase 3: Analytics & Reporting
    phase3_items = ['SemanticModel', 'Report', 'Dashboard']
    print(f"\n📊 Phase 3 - Analytics: {', '.join(phase3_items)}")
    deployment.deploy(
        workspace_id=WORKSPACE_CONFIGS['prod']['workspace_id'],
        environment='PROD',
        item_types=phase3_items
    )

# =============================================================================
# SCENARIO 5: DISASTER RECOVERY SETUP
# =============================================================================

def disaster_recovery_migration_example():
    """
    Set up disaster recovery by replicating PROD environment
    to secondary region with identical configuration
    """
    
    print("🚨 Disaster Recovery Setup Example")
    print("="*50)
    
    repository_path = r"C:\source\repos\Fabric\cicd\migrate"
    deployment = FabricDeployment(repository_path)
    
    # DR workspace configuration
    dr_workspace_id = '44444444-4444-4444-4444-444444444444'  # Replace with actual
    
    print("🎯 Target: Disaster Recovery environment setup")
    print(f"📍 Primary: {WORKSPACE_CONFIGS['prod']['region']}")
    print(f"📍 DR: Secondary region")
    
    # Deploy all items to DR environment using PROD configuration
    deployment.deploy(
        workspace_id=dr_workspace_id,
        environment='PROD',  # Use PROD config for DR
        item_types=None      # All item types
    )
    
    print("✅ Disaster recovery environment ready")
    print("💡 Test failover procedures and update connection strings as needed")

# =============================================================================
# SCENARIO 6: MULTI-REGION COMPLIANCE DEPLOYMENT
# =============================================================================

def compliance_migration_example():
    """
    Deploy to multiple regions for compliance requirements
    Each region may have specific configuration needs
    """
    
    print("🌍 Multi-Region Compliance Deployment")
    print("="*50)
    
    repository_path = r"C:\source\repos\Fabric\cicd\migrate"
    deployment = FabricDeployment(repository_path)
    
    # Compliance regions
    compliance_regions = {
        'eu': {
            'workspace_id': '55555555-5555-5555-5555-555555555555',
            'environment': 'PROD',
            'region': 'West Europe'
        },
        'us': {
            'workspace_id': '66666666-6666-6666-6666-666666666666', 
            'environment': 'PROD',
            'region': 'East US'
        },
        'asia': {
            'workspace_id': '77777777-7777-7777-7777-777777777777',
            'environment': 'PROD', 
            'region': 'Southeast Asia'
        }
    }
    
    # Items that need regional deployment
    compliance_items = ['Lakehouse', 'Warehouse', 'Report', 'SemanticModel']
    
    for region_name, config in compliance_regions.items():
        print(f"\n🌐 Deploying to {region_name.upper()} region ({config['region']})")
        
        deployment.deploy(
            workspace_id=config['workspace_id'],
            environment=config['environment'],
            item_types=compliance_items
        )
        
        print(f"✅ {region_name.upper()} region deployment completed")

# =============================================================================
# SCENARIO 7: SIMPLE MIGRATION (KEEP ORIGINAL NAMES)
# =============================================================================

def simple_migration_example():
    """
    Migrate items keeping their original names - no parameterization
    Useful when you want exact copies in different workspace/capacity
    """
    
    print("📋 Simple Migration (Keep Original Names)")
    print("="*50)
    
    repository_path = r"C:\source\repos\Fabric\cicd\migrate"
    deployment = FabricDeployment(repository_path)
    
    print("🎯 Target: Migrate items with original names intact")
    print("📝 No parameter.yml replacement - items keep source names")
    
    # Simple deployment without environment parameterization
    deployment.deploy_without_parameterization(
        workspace_id=WORKSPACE_CONFIGS['prod']['workspace_id'],
        item_types=['Lakehouse', 'Notebook', 'Report']  # Specify what to migrate
    )
    
    print("✅ Simple migration completed - all items keep original names")

# =============================================================================
# SCENARIO 8: DEVELOPMENT TO PRODUCTION PIPELINE
# =============================================================================

def dev_to_prod_pipeline_example():
    """
    Complete development lifecycle: DEV → STAGING → PROD
    Each environment in potentially different regions
    """
    
    print("🔄 Development Pipeline Migration")
    print("="*50)
    
    repository_path = r"C:\source\repos\Fabric\cicd\migrate"
    deployment = FabricDeployment(repository_path)
    
    # Pipeline stages
    pipeline_stages = [
        ('DEV', WORKSPACE_CONFIGS['dev']),
        ('STAGING', WORKSPACE_CONFIGS['staging']),
        ('PROD', WORKSPACE_CONFIGS['prod'])
    ]
    
    for stage_name, config in pipeline_stages:
        print(f"\n🚀 Deploying to {stage_name} environment")
        print(f"📍 Region: {config['region']}")
        print(f"💾 Capacity: {config['capacity']}")
        
        # Deploy with validation first
        deployment.deploy(
            workspace_id=config['workspace_id'],
            environment=config['environment'],
            dry_run=True  # Validate first
        )
        
        # Prompt for confirmation
        response = input(f"Deploy to {stage_name}? (y/N): ")
        if response.lower() == 'y':
            deployment.deploy(
                workspace_id=config['workspace_id'],
                environment=config['environment'],
                dry_run=False
            )
            print(f"✅ {stage_name} deployment completed")
        else:
            print(f"⏭️  Skipped {stage_name} deployment")

# =============================================================================
# MAIN EXECUTION
# =============================================================================

def main():
    """Run migration examples based on command line arguments or interactive selection"""
    
    # Check if command line arguments provided
    import sys
    if len(sys.argv) > 1:
        # Command line mode
        args = parse_arguments()
        run_scenario_with_args(args)
    else:
        # Interactive mode (legacy)
        run_interactive_mode()

def run_scenario_with_args(args):
    """Run specific scenario with command line arguments"""
    
    # Handle "all" item type option
    if args.items and len(args.items) == 1 and args.items[0].lower() == 'all':
        args.items = None  # None means all item types
    
    print("🚀 Fabric Cross-Region Migration Examples")
    print("="*60)
    print(f"📋 Scenario: {args.scenario}")
    print(f"🏢 Workspace: {args.workspace_id}")
    print(f"🔧 Mode: {'Simple' if args.simple else f'Parameterized ({args.target_env})'}")
    if args.items:
        print(f"📦 Items: {', '.join(args.items)}")
    else:
        print(f"📦 Items: All discovered item types")
    print(f"🔍 Dry Run: {'Yes' if args.dry_run else 'No'}")
    print("="*60)
    
    try:
        # Map scenarios to functions
        scenario_functions = {
            1: analytics_migration_example,
            2: data_engineering_migration_example,
            3: realtime_analytics_migration_example,
            4: phased_migration_example,
            5: disaster_recovery_migration_example,
            6: compliance_migration_example,
            7: simple_migration_example,
            8: dev_to_prod_pipeline_example,
        }
        
        if args.scenario in scenario_functions:
            scenario_functions[args.scenario](args)
            print("\n✅ Migration completed successfully!")
        else:
            print(f"❌ Invalid scenario: {args.scenario}")
            
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        print("\n🔧 Troubleshooting tips:")
        print("• Verify workspace ID is correct")
        print("• Check Azure authentication: az login")
        print("• Ensure parameter.yml is properly configured")
        print("• Validate repository structure and Fabric items")

def run_interactive_mode():
    """Run migration examples based on user selection (legacy mode)"""
    
    print("🚀 Fabric Cross-Region Migration Examples")
    print("="*60)
    print("Select a migration scenario:")
    print("1. Analytics Workload Migration")
    print("2. Data Engineering Pipeline Migration") 
    print("3. Real-Time Analytics Migration")
    print("4. Phased Migration Strategy")
    print("5. Disaster Recovery Setup")
    print("6. Multi-Region Compliance Deployment")
    print("7. Simple Migration (Keep Original Names)")
    print("8. Development Pipeline (DEV→STAGING→PROD)")
    print("0. Exit")
    print("\n💡 Tip: Use command line arguments for automation!")
    print("   Example: python migration_examples.py --scenario 1 --workspace-id 'WORKSPACE_ID' --target-env PROD")
    
    choice = input("\nEnter your choice (0-8): ")
    
    try:
        # Create a mock args object for interactive mode using WORKSPACE_CONFIGS
        class InteractiveArgs:
            def __init__(self):
                self.repository_path = r"C:\source\repos\Fabric\cicd\migrate"
                self.workspace_id = WORKSPACE_CONFIGS['prod']['workspace_id']
                self.target_env = 'PROD'
                self.simple = False
                self.items = None
                self.dry_run = False
        
        args = InteractiveArgs()
        
        if choice == '1':
            analytics_migration_example(args)
        elif choice == '2':
            data_engineering_migration_example(args)
        elif choice == '3':
            print("⚡ Real-Time Analytics Migration - Use command line mode for full control")
            print("Example: python migration_examples.py --scenario 3 --workspace-id 'ID' --target-env PROD")
        elif choice == '4':
            print("📋 Phased Migration Strategy - Use command line mode for full control")
            print("Example: python migration_examples.py --scenario 4 --workspace-id 'ID' --target-env PROD")
        elif choice == '5':
            print("🚨 Disaster Recovery Setup - Use command line mode for full control")
            print("Example: python migration_examples.py --scenario 5 --workspace-id 'ID' --target-env PROD")
        elif choice == '6':
            print("🌍 Multi-Region Compliance - Use command line mode for full control")
            print("Example: python migration_examples.py --scenario 6 --workspace-id 'ID' --target-env PROD")
        elif choice == '7':
            args.simple = True
            args.target_env = None
            print("📋 Simple Migration Example")
            analytics_migration_example(args)  # Use analytics as simple example
        elif choice == '8':
            print("🔄 Development Pipeline - Use command line mode for full control")
            print("Example: python migration_examples.py --scenario 8 --workspace-id 'ID' --target-env PROD")
        elif choice == '0':
            print("👋 Goodbye!")
            return
        else:
            print("❌ Invalid choice. Please select 0-8.")
            
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        print("\n🔧 Troubleshooting tips:")
        print("• Verify workspace IDs in WORKSPACE_CONFIGS")
        print("• Check Azure authentication: az login")
        print("• Ensure parameter.yml is properly configured")
        print("• Validate repository structure and Fabric items")

# =============================================================================
# REMAINING SCENARIO FUNCTIONS (SIMPLIFIED FOR COMMAND LINE)
# =============================================================================

def realtime_analytics_migration_example(args):
    """Real-time analytics migration with command line support"""
    print("⚡ Real-Time Analytics Migration Example")
    print("="*50)
    
    deployment = FabricDeployment(args.repository_path)
    
    realtime_items = args.items if args.items else [
        'Eventhouse', 'Eventstream', 'KQLDatabase', 'KQLQueryset'
    ]
    
    print(f"🎯 Target: Real-time analytics")
    print(f"📦 Items: {', '.join(realtime_items)}")
    
    if args.simple:
        deployment.deploy_without_parameterization(
            workspace_id=args.workspace_id,
            item_types=realtime_items,
            dry_run=args.dry_run
        )
    else:
        deployment.deploy(
            workspace_id=args.workspace_id,
            environment=args.target_env,
            item_types=realtime_items,
            dry_run=args.dry_run
        )

def phased_migration_example(args):
    """Phased migration with command line support"""
    print("📋 Phased Migration Strategy Example")
    print("="*50)
    
    deployment = FabricDeployment(args.repository_path)
    
    # Phase 1: Infrastructure
    phase1_items = ['Lakehouse', 'Warehouse', 'Environment']
    print(f"\n🏗️  Phase 1 - Infrastructure: {', '.join(phase1_items)}")
    
    if args.simple:
        deployment.deploy_without_parameterization(
            workspace_id=args.workspace_id,
            item_types=phase1_items,
            dry_run=args.dry_run
        )
    else:
        deployment.deploy(
            workspace_id=args.workspace_id,
            environment=args.target_env,
            item_types=phase1_items,
            dry_run=args.dry_run
        )

def disaster_recovery_migration_example(args):
    """Disaster recovery setup with command line support"""
    print("🚨 Disaster Recovery Setup Example")
    print("="*50)
    
    deployment = FabricDeployment(args.repository_path)
    
    print("🎯 Target: Disaster Recovery environment setup")
    print(f"🏢 Workspace: {args.workspace_id}")
    
    # Deploy all items to DR environment
    if args.simple:
        deployment.deploy_without_parameterization(
            workspace_id=args.workspace_id,
            item_types=args.items,  # None means all
            dry_run=args.dry_run
        )
    else:
        deployment.deploy(
            workspace_id=args.workspace_id,
            environment=args.target_env,
            item_types=args.items,  # None means all
            dry_run=args.dry_run
        )

def compliance_migration_example(args):
    """Multi-region compliance deployment with command line support"""
    print("🌍 Multi-Region Compliance Deployment")
    print("="*50)
    
    deployment = FabricDeployment(args.repository_path)
    
    compliance_items = args.items if args.items else ['Lakehouse', 'Warehouse', 'Report', 'SemanticModel']
    
    print(f"🌐 Deploying to workspace: {args.workspace_id}")
    print(f"📦 Items: {', '.join(compliance_items)}")
    
    if args.simple:
        deployment.deploy_without_parameterization(
            workspace_id=args.workspace_id,
            item_types=compliance_items,
            dry_run=args.dry_run
        )
    else:
        deployment.deploy(
            workspace_id=args.workspace_id,
            environment=args.target_env,
            item_types=compliance_items,
            dry_run=args.dry_run
        )

def simple_migration_example(args):
    """Simple migration keeping original names"""
    print("📋 Simple Migration (Keep Original Names)")
    print("="*50)
    
    deployment = FabricDeployment(args.repository_path)
    
    simple_items = args.items if args.items else ['Lakehouse', 'Notebook', 'Report']
    
    print("🎯 Target: Migrate items with original names intact")
    print("📝 No parameter.yml replacement - items keep source names")
    print(f"📦 Items: {', '.join(simple_items)}")
    
    deployment.deploy_without_parameterization(
        workspace_id=args.workspace_id,
        item_types=simple_items,
        dry_run=args.dry_run
    )

def dev_to_prod_pipeline_example(args):
    """Development pipeline example with command line support"""
    print("🔄 Development Pipeline Migration")
    print("="*50)
    
    deployment = FabricDeployment(args.repository_path)
    
    print(f"🚀 Deploying to {args.target_env if not args.simple else 'Simple'} environment")
    print(f"🏢 Workspace: {args.workspace_id}")
    
    if args.simple:
        deployment.deploy_without_parameterization(
            workspace_id=args.workspace_id,
            item_types=args.items,
            dry_run=args.dry_run
        )
    else:
        deployment.deploy(
            workspace_id=args.workspace_id,
            environment=args.target_env,
            item_types=args.items,
            dry_run=args.dry_run
        )

# =============================================================================
# INTERACTIVE MODE FUNCTIONS (LEGACY SUPPORT)  
# =============================================================================

def analytics_migration_example_interactive():
    """Interactive version of analytics migration for backward compatibility"""
    # Create a mock args object for interactive mode
    class InteractiveArgs:
        def __init__(self):
            self.repository_path = r"C:\source\repos\Fabric\cicd\migrate"
            self.workspace_id = WORKSPACE_CONFIGS['prod']['workspace_id']
            self.target_env = 'PROD'
            self.simple = False
            self.items = None
            self.dry_run = False
    
    args = InteractiveArgs()
    analytics_migration_example(args)

if __name__ == "__main__":
    main()
