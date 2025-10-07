#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fabric Warehouse Schema Deployment Module

Deploys database schema objects to Fabric Warehouses using:
1. dotnet build to build SQL projects (.sqlproj) into DACPAC files
2. SqlPackage.exe to deploy DACPAC files to Fabric Warehouses

Requirements:
- SqlPackage.exe (installed via SQL Server Data Tools or dotnet tool)
- .NET SDK for building SQL projects
- SQL project (.sqlproj) files for warehouse schemas

Usage:
    deployer = WarehouseSchemaDeployer("warehouse_name", "workspace_id")
    result = deployer.deploy_from_sqlproj("path/to/project.sqlproj")
"""

import os
import sys
import subprocess
import shutil
import tempfile
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import json
import requests
from azure.identity import DefaultAzureCredential
try:
    import pyodbc
except ImportError:
    pyodbc = None

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class DeploymentResult:
    """Result of a schema deployment operation"""
    success: bool
    dacpac_path: Optional[str] = None
    objects_deployed: int = 0
    objects_failed: int = 0
    errors: Optional[List[str]] = None
    warnings: Optional[List[str]] = None
    execution_time: float = 0
    deployment_report: Optional[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []

class WarehouseSchemaDeployer:
    """
    Deploys warehouse schema objects using SqlPackage.exe
    """
    
    def __init__(self, warehouse_name: str, workspace_id: str, server_name: Optional[str] = None):
        """
        Initialize the warehouse schema deployer
        
        Args:
            warehouse_name: Name of the Fabric warehouse
            workspace_id: Fabric workspace ID
            server_name: Optional Fabric warehouse server name (if not provided, will be generated from workspace_id)
        """
        self.warehouse_name = warehouse_name
        self.workspace_id = workspace_id
        self.server_name = server_name
        self.sqlpackage_path = None
        self.connection_string = None
        
        # Find SqlPackage.exe
        self._find_sqlpackage()
        
    def _find_sqlpackage(self) -> None:
        """Find SqlPackage.exe on the system"""
        
        # Common installation paths for SqlPackage.exe
        possible_paths = [
            # SQL Server Data Tools (Visual Studio)
            r"C:\Program Files\Microsoft SQL Server\160\DAC\bin\SqlPackage.exe",
            r"C:\Program Files\Microsoft SQL Server\150\DAC\bin\SqlPackage.exe",
            r"C:\Program Files\Microsoft SQL Server\140\DAC\bin\SqlPackage.exe",
            
            # Azure Data Studio
            r"C:\Users\%USERNAME%\.azuredatastudio\extensions\microsoft.sql-database-projects-*\BuildDirectory\SqlPackage.exe",
            
            # Standalone SqlPackage
            r"C:\Program Files\Microsoft SQL Server\SqlPackage\SqlPackage.exe",
            
            # dotnet tool (global)
            "sqlpackage",  # If installed as dotnet tool
        ]
        
        # Check PATH first
        if shutil.which("sqlpackage"):
            self.sqlpackage_path = "sqlpackage"
            logger.info("Found SqlPackage in PATH")
            return
            
        # Check specific paths
        for path in possible_paths:
            expanded_path = os.path.expandvars(path)
            if "*" in expanded_path:
                # Handle wildcard paths (like Azure Data Studio extensions)
                import glob
                matches = glob.glob(expanded_path)
                if matches:
                    self.sqlpackage_path = matches[0]
                    logger.info(f"Found SqlPackage at: {self.sqlpackage_path}")
                    return
            elif os.path.exists(expanded_path):
                self.sqlpackage_path = expanded_path
                logger.info(f"Found SqlPackage at: {self.sqlpackage_path}")
                return
        
        # Not found
        logger.error("SqlPackage.exe not found! Please install:")
        logger.error("• SQL Server Data Tools (SSDT)")
        logger.error("• Azure Data Studio with SQL Database Projects extension")
        logger.error("• dotnet tool: dotnet tool install -g microsoft.sqlpackage")
        
        raise Exception("SqlPackage.exe not found. Please install SQL Server Data Tools or SqlPackage.")
    
    def _get_warehouse_id(self) -> Optional[str]:
        """Get warehouse ID from Fabric API"""
        try:
            # Get access token
            credential = DefaultAzureCredential()
            token = credential.get_token("https://api.fabric.microsoft.com/.default")
            
            # Call Fabric API to get warehouses
            url = f"https://api.fabric.microsoft.com/v1/workspaces/{self.workspace_id}/warehouses"
            headers = {
                "Authorization": f"Bearer {token.token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            warehouses = response.json().get("value", [])
            
            # Find warehouse by name
            for warehouse in warehouses:
                if warehouse.get("displayName") == self.warehouse_name:
                    return warehouse.get("id")
            
            logger.warning(f"Warehouse '{self.warehouse_name}' not found in workspace")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get warehouse ID: {e}")
            return None
    
    def _get_fabric_connection_string(self) -> Optional[str]:
        """Get connection string from Fabric API"""
        warehouse_id = self._get_warehouse_id()
        if not warehouse_id:
            return None
            
        try:
            # Get access token
            credential = DefaultAzureCredential()
            token = credential.get_token("https://api.fabric.microsoft.com/.default")
            
            # Call Fabric API to get connection string
            url = f"https://api.fabric.microsoft.com/v1/workspaces/{self.workspace_id}/warehouses/{warehouse_id}/connectionString"
            headers = {
                "Authorization": f"Bearer {token.token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            connection_data = response.json()
            server_endpoint = connection_data.get("connectionString")
            
            if server_endpoint:
                logger.info(f"Retrieved server endpoint from Fabric API: {server_endpoint}")
                
                # Build connection string with Active Directory Interactive authentication
                return (
                    f"Server={server_endpoint};"
                    f"Database={self.warehouse_name};"
                    f"Authentication=Active Directory Interactive;"
                    f"Encrypt=True;"
                    f"TrustServerCertificate=False;"
                )
            else:
                logger.warning("No connection string returned from API")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get connection string from API: {e}")
            return None
    
    def _get_connection_string(self) -> str:
        """Get connection string for Fabric warehouse"""
        
        # Try to get connection string from Fabric API first
        api_connection_string = self._get_fabric_connection_string()
        if api_connection_string:
            logger.info("Using connection string from Fabric API")
            return api_connection_string
        
        # Fallback to manual construction
        logger.warning("API connection string failed, falling back to manual construction")
        
        # Build server endpoint
        server = (self.server_name if self.server_name 
                 else f"{self.workspace_id}.datawarehouse.fabric.microsoft.com")
        
        if not self.server_name:
            logger.warning("Using workspace ID as server name - may not work for all warehouses")
        
        # Build connection string with Active Directory Interactive (proven to work)
        return (
            f"Server={server};"
            f"Database={self.warehouse_name};"
            f"Authentication=Active Directory Interactive;"
            f"Encrypt=True;"
            f"TrustServerCertificate=False;"
        )
    
    def test_connection(self) -> bool:
        """Test SQL connection with SELECT 1"""
        connection_string = self._get_connection_string()
        logger.info("Testing SQL connection...")
        
        # Parse connection string once
        conn_parts = dict(part.split('=', 1) for part in connection_string.split(';') if '=' in part)
        server = conn_parts.get('Server', '')
        database = conn_parts.get('Database', '')
        
        # Try pyodbc first (most reliable)
        if pyodbc:
            try:
                pyodbc_conn_str = (
                    f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                    f"SERVER={server};"
                    f"DATABASE={database};"
                    f"Authentication=ActiveDirectoryInteractive;"
                    f"Encrypt=yes;"
                    f"TrustServerCertificate=no;"
                )
                
                with pyodbc.connect(pyodbc_conn_str, timeout=30) as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1 as test_result")
                    result = cursor.fetchone()
                    
                    if result and result[0] == 1:
                        logger.info("SQL connection test successful")
                        return True
                        
            except Exception as e:
                logger.warning(f"pyodbc connection failed: {e}")
        else:
            logger.warning("pyodbc not available, trying sqlcmd")
        
        # Fallback to sqlcmd
        try:
            cmd = ['sqlcmd', '-S', server, '-d', database, '-G', '-Q', 'SELECT 1', '-l', '30']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                logger.info("sqlcmd connection test successful")
                return True
            else:
                logger.error(f"sqlcmd failed: {result.stderr}")
                
        except (FileNotFoundError, subprocess.TimeoutExpired, Exception) as e:
            logger.warning(f"sqlcmd test failed: {e}")
        
        logger.warning("No connection test method available")
        return False
    
    def build_dacpac(self, sqlproj_path: str, output_dir: Optional[str] = None) -> Tuple[bool, str, List[str]]:
        """
        Build a SQL project into a DACPAC file using SqlPackage.exe
        
        Args:
            sqlproj_path: Path to the .sqlproj file
            output_dir: Output directory for DACPAC (default: temp directory)
            
        Returns:
            Tuple of (success, dacpac_path, errors)
        """
        
        if not self.sqlpackage_path:
            return False, "", ["SqlPackage.exe not available"]
            
        # Prepare output directory
        if output_dir is None:
            output_dir = tempfile.mkdtemp(prefix="fabric_dacpac_")
        
        sqlproj_file = Path(sqlproj_path)
        dacpac_name = sqlproj_file.stem + ".dacpac"
        dacpac_path = Path(output_dir) / dacpac_name
        
        # Use dotnet build to build the SQL project into a DACPAC
        abs_sqlproj_file = sqlproj_file.resolve()
        abs_output_dir = Path(output_dir).resolve()
        
        # Use dotnet build for all SQL projects (modern approach)
        cmd = [
            "dotnet", "build",
            str(abs_sqlproj_file),
            "--configuration", "Release",
            "--output", str(abs_output_dir),
            "--verbosity", "minimal"
        ]
        
        logger.info(f"Building DACPAC: {sqlproj_file}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                timeout=60,
                cwd=sqlproj_file.parent
            )
            
            if result.returncode == 0:
                # Look for generated DACPAC file
                dacpac_candidates = [
                    Path(output_dir) / f"{sqlproj_file.stem}.dacpac",
                    Path(output_dir) / "bin" / "Release" / f"{sqlproj_file.stem}.dacpac",
                    Path(sqlproj_file.parent) / "bin" / "Release" / f"{sqlproj_file.stem}.dacpac"
                ]
                
                for dacpac_path in dacpac_candidates:
                    if dacpac_path.exists():
                        logger.info(f"DACPAC build successful: {dacpac_path}")
                        return True, str(dacpac_path), []
                
                logger.warning("DACPAC not found after build")
                return False, "", ["DACPAC file not found after build"]
                
            else:
                errors = [f"dotnet build failed (exit code: {result.returncode})", result.stderr]
                logger.error(f"DACPAC build failed: {errors[0]}")
                return False, "", errors
                
        except subprocess.TimeoutExpired:
            error_msg = "dotnet build timed out after 60 seconds"
            logger.error(error_msg)
            return False, "", [error_msg]
            
        except Exception as e:
            error_msg = f"Failed to execute dotnet build: {str(e)}"
            logger.error(error_msg)
            return False, "", [error_msg]
    
    def deploy_dacpac(self, source_path: str, dry_run: bool = False) -> DeploymentResult:
        """
        Deploy a DACPAC file or SQL project to the Fabric warehouse using SqlPackage.exe
        
        Args:
            source_path: Path to the DACPAC file or SQL project file
            dry_run: If True, generate deployment script without executing
            
        Returns:
            DeploymentResult with deployment details
        """
        
        if not self.sqlpackage_path:
            return DeploymentResult(
                success=False,
                errors=["SqlPackage.exe not available"]
            )
        
        # Get connection string
        connection_string = self._get_connection_string()
        
        # Determine source type
        source_path_obj = Path(source_path)
        is_sqlproj = source_path_obj.suffix.lower() == '.sqlproj'
        
        # Prepare command
        if dry_run:
            # Generate deployment script only
            script_path = source_path_obj.parent / f"{source_path_obj.stem}_deployment.sql"
            cmd = [
                self.sqlpackage_path,
                "/Action:Script",
                f"/SourceFile:{source_path}",
                f"/TargetConnectionString:{connection_string}",
                f"/OutputPath:{script_path}",
                "/p:IgnorePermissions=true",
                "/p:IgnoreRoleMembership=true"
            ]
            
            source_type = "SQL Project" if is_sqlproj else "DACPAC"
            logger.info(f"🔍 [DRY RUN] Generating deployment script...")
            logger.info(f"   📦 Source: {source_path} ({source_type})")
            logger.info(f"   📄 Script: {script_path}")
            
        else:
            # Deploy to database using connection string (most reliable for Fabric)
            cmd = [
                self.sqlpackage_path,
                "/Action:Publish",
                f"/SourceFile:{source_path}",
                f"/TargetConnectionString:{connection_string}",
                "/p:IgnorePermissions=true",
                "/p:IgnoreRoleMembership=true"
            ]
            
            source_type = "SQL Project" if is_sqlproj else "DACPAC"
            logger.info(f"Deploying {source_type} to warehouse: {self.warehouse_name}")
        
        try:
            # Execute SqlPackage deployment
            import time
            start_time = time.time()
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                timeout=120  # 2 minute timeout
            )
            
            execution_time = time.time() - start_time
            
            if result.returncode == 0:
                if dry_run:
                    logger.info("Deployment script generated successfully")
                    return DeploymentResult(
                        success=True,
                        dacpac_path=source_path,
                        execution_time=execution_time,
                        deployment_report=str(script_path)
                    )
                else:
                    objects_deployed = self._count_deployed_objects(result.stdout)
                    logger.info(f"DACPAC deployment successful: {objects_deployed} objects")
                    
                    return DeploymentResult(
                        success=True,
                        dacpac_path=source_path,
                        objects_deployed=objects_deployed,
                        execution_time=execution_time,
                        deployment_report=result.stdout
                    )
            else:
                errors = [f"SqlPackage failed (exit code: {result.returncode})", result.stderr]
                logger.error(f"DACPAC deployment failed: {errors[0]}")
                    
                return DeploymentResult(
                    success=False,
                    dacpac_path=source_path,
                    errors=errors,
                    execution_time=execution_time
                )
                
        except subprocess.TimeoutExpired:
            error_msg = "SqlPackage deployment timed out after 120 seconds"
            logger.error(error_msg)
            return DeploymentResult(success=False, dacpac_path=source_path, errors=[error_msg])
            
        except Exception as e:
            error_msg = f"Failed to execute SqlPackage: {str(e)}"
            logger.error(error_msg)
            return DeploymentResult(success=False, dacpac_path=source_path, errors=[error_msg])
    
    def _count_deployed_objects(self, output: str) -> int:
        """Parse SqlPackage output to count deployed objects"""
        
        # Basic parsing - SqlPackage typically reports operations
        # This is a simplified version, actual parsing would be more sophisticated
        lines = output.split('\n')
        count = 0
        
        for line in lines:
            if any(keyword in line.lower() for keyword in ['creating', 'altering', 'updating']):
                if any(obj_type in line.lower() for obj_type in ['table', 'view', 'procedure', 'function']):
                    count += 1
        
        return count
    
    def deploy_from_sqlproj(self, sqlproj_path: str, dry_run: bool = False) -> DeploymentResult:
        """
        Deploy schema objects from a SQL project file using SqlPackage.exe
        
        Args:
            sqlproj_path: Path to the .sqlproj file
            dry_run: If True, only generate deployment script without executing
            
        Returns:
            Deployment result
        """
        logger.info(f"Processing SQL project: {sqlproj_path}")
        
        # Step 1: Build DACPAC
        build_success, dacpac_path, build_errors = self.build_dacpac(sqlproj_path)
        
        if not build_success:
            return DeploymentResult(success=False, errors=build_errors)
        
        # Step 2: Deploy DACPAC
        deploy_result = self.deploy_dacpac(dacpac_path, dry_run)
        
        # Clean up temporary DACPAC if needed
        if dacpac_path and os.path.exists(dacpac_path):
            try:
                # Keep DACPAC for dry runs, clean up for actual deployments
                if not dry_run:
                    os.remove(dacpac_path)
                    # Also clean up temp directory if we created it
                    dacpac_dir = Path(dacpac_path).parent
                    if dacpac_dir.name.startswith("fabric_dacpac_"):
                        shutil.rmtree(dacpac_dir, ignore_errors=True)
            except Exception as e:
                logger.warning(f"⚠️  Could not clean up DACPAC file: {e}")
        
        return deploy_result

# For backward compatibility, keep the same interface
def has_sqlpackage_support() -> bool:
    """Check if SqlPackage.exe is available"""
    try:
        deployer = WarehouseSchemaDeployer("test", "test")
        return deployer.sqlpackage_path is not None
    except:
        return False