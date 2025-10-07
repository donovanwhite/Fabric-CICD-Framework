#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Warehouse Schema Deployment Validation Script
==============================================

This script validates that the warehouse schema deployment functionality 
is properly set up and working correctly.

Usage:
    python validate_schema_deployment.py --warehouse-name "your_warehouse" --workspace-id "your_workspace_id"
"""

import sys
import argparse
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    print("🔍 Checking dependencies...")
    
    # Check pyodbc
    try:
        import pyodbc
        print("✅ pyodbc available")
    except ImportError:
        print("❌ pyodbc not available - install with: pip install pyodbc")
        return False
    
    # Check azure-identity  
    try:
        from azure.identity import DefaultAzureCredential
        print("✅ azure-identity available")
    except ImportError:
        print("❌ azure-identity not available - install with: pip install azure-identity")
        return False
    
    # Check lxml
    try:
        import lxml
        print("✅ lxml available")
    except ImportError:
        print("❌ lxml not available - install with: pip install lxml")
        return False
    
    return True

def check_odbc_driver():
    """Check if ODBC driver for SQL Server is installed"""
    print("\n🔍 Checking ODBC drivers...")
    
    try:
        import pyodbc
        drivers = pyodbc.drivers()
        
        sql_drivers = [d for d in drivers if 'SQL Server' in d]
        if sql_drivers:
            print("✅ SQL Server ODBC drivers found:")
            for driver in sql_drivers:
                print(f"   📋 {driver}")
            return True
        else:
            print("❌ No SQL Server ODBC drivers found")
            print("   💡 Install Microsoft ODBC Driver 18 for SQL Server")
            return False
    
    except Exception as e:
        print(f"❌ Error checking ODBC drivers: {str(e)}")
        return False

def test_warehouse_connection(warehouse_name: str, workspace_id: str):
    """Test connection to a Fabric Warehouse"""
    print(f"\n🔍 Testing connection to Warehouse: {warehouse_name}")
    
    try:
        from warehouse_schema_deploy import WarehouseSchemaDeployer
        
        deployer = WarehouseSchemaDeployer(warehouse_name, workspace_id)
        
        if deployer.connect():
            print(f"✅ Successfully connected to Warehouse: {warehouse_name}")
            deployer.disconnect()
            return True
        else:
            print(f"❌ Failed to connect to Warehouse: {warehouse_name}")
            return False
    
    except ImportError:
        print("❌ warehouse_schema_deploy module not found")
        print("   💡 Ensure you're running from the core/ directory")
        return False
    except Exception as e:
        print(f"❌ Connection error: {str(e)}")
        return False

def create_sample_sql_files():
    """Create sample SQL files for testing"""
    print("\n🔍 Creating sample SQL files for testing...")
    
    sample_dir = Path("./sample_sql")
    sample_dir.mkdir(exist_ok=True)
    
    # Sample table
    table_sql = """
-- Sample table for warehouse schema deployment testing
CREATE TABLE [dbo].[TestTable] (
    [ID] INT IDENTITY(1,1) PRIMARY KEY,
    [Name] NVARCHAR(100) NOT NULL,
    [CreatedDate] DATETIME2 DEFAULT GETDATE(),
    [IsActive] BIT DEFAULT 1
);
"""
    
    # Sample view
    view_sql = """
-- Sample view for warehouse schema deployment testing  
CREATE VIEW [dbo].[TestView] AS
SELECT 
    ID,
    Name,
    CreatedDate,
    IsActive
FROM [dbo].[TestTable]
WHERE IsActive = 1;
"""
    
    # Sample stored procedure
    proc_sql = """
-- Sample stored procedure for warehouse schema deployment testing
CREATE PROCEDURE [dbo].[GetTestData]
    @IsActive BIT = 1
AS
BEGIN
    SET NOCOUNT ON;
    
    SELECT 
        ID,
        Name, 
        CreatedDate,
        IsActive
    FROM [dbo].[TestTable]
    WHERE IsActive = @IsActive
    ORDER BY CreatedDate DESC;
END;
"""
    
    # Write sample files
    (sample_dir / "01_create_table.sql").write_text(table_sql)
    (sample_dir / "02_create_view.sql").write_text(view_sql)
    (sample_dir / "03_create_procedure.sql").write_text(proc_sql)
    
    print(f"✅ Created sample SQL files in: {sample_dir}")
    print("   📄 01_create_table.sql")
    print("   📄 02_create_view.sql") 
    print("   📄 03_create_procedure.sql")
    
    return str(sample_dir)

def test_sql_parsing(sql_directory: str):
    """Test SQL file parsing functionality"""
    print(f"\n🔍 Testing SQL file parsing in: {sql_directory}")
    
    try:
        from warehouse_schema_deploy import WarehouseSchemaDeployer
        
        deployer = WarehouseSchemaDeployer("test_warehouse", "test_workspace")
        
        # Find SQL files
        sql_files = list(Path(sql_directory).glob("*.sql"))
        if not sql_files:
            print(f"❌ No SQL files found in: {sql_directory}")
            return False
        
        print(f"📁 Found {len(sql_files)} SQL files")
        
        # Parse each file
        total_objects = 0
        for sql_file in sql_files:
            objects = deployer.parse_sql_file(str(sql_file))
            print(f"   📄 {sql_file.name}: {len(objects)} objects")
            total_objects += len(objects)
        
        if total_objects > 0:
            print(f"✅ Successfully parsed {total_objects} schema objects")
            return True
        else:
            print("❌ No schema objects found in SQL files")
            return False
    
    except Exception as e:
        print(f"❌ SQL parsing error: {str(e)}")
        return False

def main():
    """Main validation function"""
    parser = argparse.ArgumentParser(description='Validate warehouse schema deployment setup')
    parser.add_argument('--warehouse-name', help='Fabric Warehouse name to test connection')
    parser.add_argument('--workspace-id', help='Fabric workspace ID')
    parser.add_argument('--skip-connection-test', action='store_true', 
                       help='Skip connection test (useful for CI/CD)')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("🧪 WAREHOUSE SCHEMA DEPLOYMENT VALIDATION")
    print("=" * 70)
    
    success = True
    
    # Check dependencies
    if not check_dependencies():
        success = False
    
    # Check ODBC driver
    if not check_odbc_driver():
        success = False
    
    # Test connection (if warehouse details provided)
    if args.warehouse_name and args.workspace_id and not args.skip_connection_test:
        if not test_warehouse_connection(args.warehouse_name, args.workspace_id):
            success = False
    elif not args.skip_connection_test:
        print("\n⚠️  Skipping connection test (no warehouse details provided)")
        print("   💡 Use --warehouse-name and --workspace-id to test connection")
    
    # Create and test sample SQL files
    sample_dir = create_sample_sql_files()
    if not test_sql_parsing(sample_dir):
        success = False
    
    # Final result
    print("\n" + "=" * 70)
    if success:
        print("🎉 VALIDATION COMPLETED SUCCESSFULLY!")
        print("✅ Warehouse schema deployment is ready to use")
    else:
        print("❌ VALIDATION FAILED!")
        print("🔧 Please address the issues above before using schema deployment")
    print("=" * 70)
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)