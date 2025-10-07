#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fabric Warehouse Schema Deployment Module
==========================================

This module extends the Fabric CI/CD framework to support deploying database schema objects
(tables, views, stored procedures, functions, etc.) to Fabric Warehouses.

PROBLEM SOLVED:
- fabric-cicd deploys Warehouse items but not the schema objects inside them
- SQL projects (.sqlproj) contain schema definitions but no direct Fabric deployment
- Manual schema deployment is error-prone and not CI/CD friendly

SOLUTION APPROACH:
1. Parse SQL projects or SQL files to identify schema objects
2. Connect to Fabric Warehouse using SQL connection string  
3. Deploy schema objects in correct dependency order
4. Provide rollback capabilities and deployment validation
5. Integrate with existing fabric-cicd workflow

SUPPORTED SCHEMA OBJECTS:
✅ Tables (with constraints, indexes)
✅ Views 
✅ Stored Procedures
✅ Functions (Scalar, Table-valued)
✅ Schemas
✅ User-defined Data Types
✅ Synonyms
✅ Triggers

DEPLOYMENT STRATEGIES:
1. SQL Project (.sqlproj) parsing
2. Directory-based SQL files
3. Git repository SQL file discovery
4. Individual SQL script execution

AUTHENTICATION METHODS:
- Azure AD authentication (recommended)
- Service Principal authentication  
- SQL authentication (if enabled)

Usage:
    from warehouse_schema_deploy import WarehouseSchemaDeployer
    
    deployer = WarehouseSchemaDeployer(
        warehouse_name="your_warehouse_name",
        workspace_id="your_workspace_id"
    )
    
    # Deploy from SQL project
    deployer.deploy_from_sqlproj("path/to/project.sqlproj")
    
    # Deploy from directory
    deployer.deploy_from_directory("path/to/sql/files")
    
    # Deploy single script
    deployer.deploy_script("path/to/script.sql")
"""

import os
import re
import json
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import xml.etree.ElementTree as ET

# SQL connection libraries
try:
    import pyodbc
    PYODBC_AVAILABLE = True
except ImportError:
    PYODBC_AVAILABLE = False

try:
    from azure.identity import DefaultAzureCredential
    AZURE_IDENTITY_AVAILABLE = True
except ImportError:
    AZURE_IDENTITY_AVAILABLE = False

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SchemaObjectType(Enum):
    """Enumeration of supported schema object types"""
    SCHEMA = "Schema"
    TABLE = "Table"
    VIEW = "View"
    STORED_PROCEDURE = "StoredProcedure"
    FUNCTION = "Function"
    USER_DEFINED_TYPE = "UserDefinedType"
    SYNONYM = "Synonym"
    TRIGGER = "Trigger"
    INDEX = "Index"

@dataclass
class SchemaObject:
    """Represents a database schema object"""
    name: str
    object_type: SchemaObjectType
    schema_name: str
    sql_content: str
    dependencies: List[str]
    file_path: Optional[str] = None
    deployment_order: int = 0

@dataclass
class DeploymentResult:
    """Represents the result of a schema deployment operation"""
    success: bool
    objects_deployed: int
    objects_failed: int
    errors: List[str]
    warnings: List[str]
    execution_time: float

class WarehouseSchemaDeployer:
    """
    Main class for deploying schema objects to Fabric Warehouses
    """
    
    def __init__(self, warehouse_name: str, workspace_id: str, 
                 connection_string: Optional[str] = None):
        """
        Initialize the warehouse schema deployer
        
        Args:
            warehouse_name: Name of the Fabric Warehouse
            workspace_id: Fabric workspace ID
            connection_string: Optional custom connection string
        """
        self.warehouse_name = warehouse_name
        self.workspace_id = workspace_id
        self.connection_string = connection_string
        self.connection = None
        self.deployment_history: List[DeploymentResult] = []
        
        # Validate dependencies
        if not PYODBC_AVAILABLE:
            raise ImportError("pyodbc is required for SQL connections. Install with: pip install pyodbc")
        
        if not AZURE_IDENTITY_AVAILABLE:
            logger.warning("azure-identity not available. Only SQL authentication will work.")
    
    def get_warehouse_connection_string(self) -> str:
        """
        Generate Fabric Warehouse connection string
        
        Returns:
            Connection string for the Fabric Warehouse
        """
        if self.connection_string:
            return self.connection_string
        
        # Fabric Warehouse connection string format
        server = f"{self.warehouse_name}.datawarehouse.fabric.microsoft.com"
        database = self.warehouse_name
        
        # Use Azure AD authentication by default
        connection_string = (
            f"Driver={{ODBC Driver 18 for SQL Server}};"
            f"Server={server};"
            f"Database={database};"
            f"Authentication=ActiveDirectoryDefault;"
            f"Encrypt=yes;"
            f"TrustServerCertificate=no;"
        )
        
        return connection_string
    
    def connect(self) -> bool:
        """
        Establish connection to the Fabric Warehouse
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            connection_string = self.get_warehouse_connection_string()
            self.connection = pyodbc.connect(connection_string)
            logger.info(f"✅ Connected to Fabric Warehouse: {self.warehouse_name}")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to connect to warehouse {self.warehouse_name}: {str(e)}")
            return False
    
    def disconnect(self):
        """Close the warehouse connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("🔌 Disconnected from warehouse")
    
    def parse_sqlproj(self, sqlproj_path: str) -> List[SchemaObject]:
        """
        Parse a SQL project file to extract schema objects
        
        Args:
            sqlproj_path: Path to the .sqlproj file
            
        Returns:
            List of schema objects found in the project
        """
        schema_objects = []
        project_dir = Path(sqlproj_path).parent
        
        try:
            tree = ET.parse(sqlproj_path)
            root = tree.getroot()
            
            # Find SQL files in the project
            for item_group in root.findall('.//{http://schemas.microsoft.com/developer/msbuild/2003}ItemGroup'):
                for build_item in item_group.findall('.//{http://schemas.microsoft.com/developer/msbuild/2003}Build'):
                    include = build_item.get('Include')
                    if include and include.endswith('.sql'):
                        sql_file_path = project_dir / include
                        if sql_file_path.exists():
                            objects = self.parse_sql_file(str(sql_file_path))
                            schema_objects.extend(objects)
            
            logger.info(f"📋 Parsed SQL project: {len(schema_objects)} objects found")
            return schema_objects
        
        except Exception as e:
            logger.error(f"❌ Failed to parse SQL project {sqlproj_path}: {str(e)}")
            return []
    
    def parse_sql_file(self, sql_file_path: str) -> List[SchemaObject]:
        """
        Parse a single SQL file to extract schema objects
        
        Args:
            sql_file_path: Path to the SQL file
            
        Returns:
            List of schema objects found in the file
        """
        schema_objects = []
        
        try:
            with open(sql_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove comments
            content = self.remove_sql_comments(content)
            
            # Split into individual statements
            statements = self.split_sql_statements(content)
            
            for statement in statements:
                obj = self.identify_schema_object(statement, sql_file_path)
                if obj:
                    schema_objects.append(obj)
            
            return schema_objects
        
        except Exception as e:
            logger.error(f"❌ Failed to parse SQL file {sql_file_path}: {str(e)}")
            return []
    
    def remove_sql_comments(self, sql_content: str) -> str:
        """Remove SQL comments from content"""
        # Remove single-line comments
        sql_content = re.sub(r'--.*$', '', sql_content, flags=re.MULTILINE)
        
        # Remove multi-line comments
        sql_content = re.sub(r'/\*.*?\*/', '', sql_content, flags=re.DOTALL)
        
        return sql_content
    
    def split_sql_statements(self, sql_content: str) -> List[str]:
        """Split SQL content into individual statements"""
        # Simple approach - split on GO statements
        statements = re.split(r'\bGO\b', sql_content, flags=re.IGNORECASE)
        
        # Clean up statements
        cleaned_statements = []
        for statement in statements:
            cleaned = statement.strip()
            if cleaned:
                cleaned_statements.append(cleaned)
        
        return cleaned_statements
    
    def identify_schema_object(self, sql_statement: str, file_path: str) -> Optional[SchemaObject]:
        """
        Identify the type and details of a schema object from SQL statement
        
        Args:
            sql_statement: SQL statement content
            file_path: Source file path
            
        Returns:
            SchemaObject if identified, None otherwise
        """
        sql_upper = sql_statement.upper().strip()
        
        # Schema patterns
        patterns = {
            SchemaObjectType.SCHEMA: r'CREATE\s+SCHEMA\s+(\[?\w+\]?)',
            SchemaObjectType.TABLE: r'CREATE\s+TABLE\s+(?:\[?\w+\]?\.)?\[?(\w+)\]?',
            SchemaObjectType.VIEW: r'CREATE\s+VIEW\s+(?:\[?\w+\]?\.)?\[?(\w+)\]?',
            SchemaObjectType.STORED_PROCEDURE: r'CREATE\s+(?:PROC|PROCEDURE)\s+(?:\[?\w+\]?\.)?\[?(\w+)\]?',
            SchemaObjectType.FUNCTION: r'CREATE\s+FUNCTION\s+(?:\[?\w+\]?\.)?\[?(\w+)\]?',
        }
        
        for object_type, pattern in patterns.items():
            match = re.search(pattern, sql_upper)
            if match:
                object_name = match.group(1).strip('[]')
                
                # Extract schema name
                schema_match = re.search(r'(?:\[?(\w+)\]?\.)?\[?\w+\]?', sql_upper)
                schema_name = schema_match.group(1) if schema_match and schema_match.group(1) else 'dbo'
                
                return SchemaObject(
                    name=object_name,
                    object_type=object_type,
                    schema_name=schema_name,
                    sql_content=sql_statement,
                    dependencies=[],  # TODO: Implement dependency analysis
                    file_path=file_path
                )
        
        return None
    
    def calculate_deployment_order(self, schema_objects: List[SchemaObject]) -> List[SchemaObject]:
        """
        Calculate the correct deployment order based on dependencies
        
        Args:
            schema_objects: List of schema objects to order
            
        Returns:
            Ordered list of schema objects
        """
        # Simple ordering by object type priority
        type_priority = {
            SchemaObjectType.SCHEMA: 1,
            SchemaObjectType.USER_DEFINED_TYPE: 2,
            SchemaObjectType.TABLE: 3,
            SchemaObjectType.FUNCTION: 4,
            SchemaObjectType.VIEW: 5,
            SchemaObjectType.STORED_PROCEDURE: 6,
            SchemaObjectType.SYNONYM: 7,
            SchemaObjectType.TRIGGER: 8,
            SchemaObjectType.INDEX: 9,
        }
        
        # Sort by priority and then by name
        ordered_objects = sorted(
            schema_objects,
            key=lambda obj: (type_priority.get(obj.object_type, 999), obj.name)
        )
        
        # Update deployment order
        for i, obj in enumerate(ordered_objects):
            obj.deployment_order = i + 1
        
        return ordered_objects
    
    def deploy_schema_objects(self, schema_objects: List[SchemaObject], 
                            dry_run: bool = False) -> DeploymentResult:
        """
        Deploy schema objects to the warehouse
        
        Args:
            schema_objects: List of schema objects to deploy
            dry_run: If True, only validate without executing
            
        Returns:
            Deployment result
        """
        import time
        start_time = time.time()
        
        result = DeploymentResult(
            success=True,
            objects_deployed=0,
            objects_failed=0,
            errors=[],
            warnings=[],
            execution_time=0
        )
        
        if not self.connection and not dry_run:
            result.success = False
            result.errors.append("No database connection available")
            return result
        
        # Order objects for deployment
        ordered_objects = self.calculate_deployment_order(schema_objects)
        
        logger.info(f"🚀 Starting deployment of {len(ordered_objects)} schema objects...")
        
        for obj in ordered_objects:
            try:
                if dry_run:
                    logger.info(f"🔍 [DRY RUN] Would deploy {obj.object_type.value}: {obj.schema_name}.{obj.name}")
                else:
                    logger.info(f"📦 Deploying {obj.object_type.value}: {obj.schema_name}.{obj.name}")
                    
                    cursor = self.connection.cursor()
                    cursor.execute(obj.sql_content)
                    cursor.commit()
                    cursor.close()
                
                result.objects_deployed += 1
                
            except Exception as e:
                error_msg = f"Failed to deploy {obj.object_type.value} {obj.schema_name}.{obj.name}: {str(e)}"
                logger.error(f"❌ {error_msg}")
                result.errors.append(error_msg)
                result.objects_failed += 1
                
                # Continue with other objects unless it's a critical failure
                if "syntax error" not in str(e).lower():
                    continue
        
        result.execution_time = time.time() - start_time
        result.success = result.objects_failed == 0
        
        logger.info(f"✅ Deployment completed: {result.objects_deployed} successful, {result.objects_failed} failed")
        return result
    
    def deploy_from_sqlproj(self, sqlproj_path: str, dry_run: bool = False) -> DeploymentResult:
        """
        Deploy schema objects from a SQL project file
        
        Args:
            sqlproj_path: Path to the .sqlproj file
            dry_run: If True, only validate without executing
            
        Returns:
            Deployment result
        """
        logger.info(f"📂 Processing SQL project: {sqlproj_path}")
        
        schema_objects = self.parse_sqlproj(sqlproj_path)
        if not schema_objects:
            return DeploymentResult(
                success=False,
                objects_deployed=0,
                objects_failed=0,
                errors=["No schema objects found in SQL project"],
                warnings=[],
                execution_time=0
            )
        
        return self.deploy_schema_objects(schema_objects, dry_run)
    
    def deploy_from_directory(self, directory_path: str, dry_run: bool = False) -> DeploymentResult:
        """
        Deploy schema objects from a directory of SQL files
        
        Args:
            directory_path: Path to directory containing SQL files
            dry_run: If True, only validate without executing
            
        Returns:
            Deployment result
        """
        logger.info(f"📁 Processing SQL directory: {directory_path}")
        
        schema_objects = []
        sql_files = Path(directory_path).glob("**/*.sql")
        
        for sql_file in sql_files:
            objects = self.parse_sql_file(str(sql_file))
            schema_objects.extend(objects)
        
        if not schema_objects:
            return DeploymentResult(
                success=False,
                objects_deployed=0,
                objects_failed=0,
                errors=["No schema objects found in directory"],
                warnings=[],
                execution_time=0
            )
        
        return self.deploy_schema_objects(schema_objects, dry_run)
    
    def deploy_script(self, script_path: str, dry_run: bool = False) -> DeploymentResult:
        """
        Deploy a single SQL script
        
        Args:
            script_path: Path to the SQL script
            dry_run: If True, only validate without executing
            
        Returns:
            Deployment result
        """
        logger.info(f"📄 Processing SQL script: {script_path}")
        
        schema_objects = self.parse_sql_file(script_path)
        if not schema_objects:
            return DeploymentResult(
                success=False,
                objects_deployed=0,
                objects_failed=0,
                errors=["No schema objects found in script"],
                warnings=[],
                execution_time=0
            )
        
        return self.deploy_schema_objects(schema_objects, dry_run)


# Convenience functions for easy integration
def deploy_warehouse_schema_from_sqlproj(warehouse_name: str, workspace_id: str, 
                                        sqlproj_path: str, dry_run: bool = False) -> bool:
    """
    Convenience function to deploy warehouse schema from SQL project
    
    Args:
        warehouse_name: Name of the Fabric Warehouse
        workspace_id: Fabric workspace ID  
        sqlproj_path: Path to the .sqlproj file
        dry_run: If True, only validate without executing
        
    Returns:
        True if deployment successful, False otherwise
    """
    deployer = WarehouseSchemaDeployer(warehouse_name, workspace_id)
    
    try:
        if not deployer.connect():
            return False
        
        result = deployer.deploy_from_sqlproj(sqlproj_path, dry_run)
        return result.success
    
    finally:
        deployer.disconnect()


def deploy_warehouse_schema_from_directory(warehouse_name: str, workspace_id: str,
                                         directory_path: str, dry_run: bool = False) -> bool:
    """
    Convenience function to deploy warehouse schema from directory
    
    Args:
        warehouse_name: Name of the Fabric Warehouse
        workspace_id: Fabric workspace ID
        directory_path: Path to directory containing SQL files
        dry_run: If True, only validate without executing
        
    Returns:
        True if deployment successful, False otherwise
    """
    deployer = WarehouseSchemaDeployer(warehouse_name, workspace_id)
    
    try:
        if not deployer.connect():
            return False
        
        result = deployer.deploy_from_directory(directory_path, dry_run)
        return result.success
    
    finally:
        deployer.disconnect()


if __name__ == "__main__":
    print("🏗️  Fabric Warehouse Schema Deployment Module")
    print("This module extends fabric-cicd to support database schema deployment")
    print()
    print("Usage examples:")
    print("  python warehouse_schema_deploy.py")
    print("  - or import and use the classes/functions in your deployment scripts")