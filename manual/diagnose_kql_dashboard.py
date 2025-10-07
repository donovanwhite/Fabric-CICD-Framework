#!/usr/bin/env python3
"""
KQL Dashboard Database Reference Diagnostic Tool
===============================================

This tool examines the KQL Dashboard files to identify what database names they're referencing
and helps debug deployment issues.
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the core directory to Python path for imports
current_dir = Path(__file__).parent.absolute()
core_dir = current_dir.parent / "core"
sys.path.insert(0, str(core_dir))

def clone_and_analyze_repo():
    """Clone the repository and analyze KQL Dashboard files"""
    try:
        from git import Repo
        import json
        
        # Repository details
        repo_url = "https://dev.azure.com/contosodwft/SASSA%20Fabric%20Data%20Plaftorm/_git/SASSA%20Fabric%20Data%20Plaftorm"
        branch = "development"
        
        print("🔍 KQL Dashboard Database Reference Diagnostic")
        print("=" * 60)
        print(f"📦 Repository: {repo_url}")
        print(f"🌿 Branch: {branch}")
        print()
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp(prefix="kql_diagnostic_")
        print(f"📂 Temporary directory: {temp_dir}")
        
        try:
            # Clone repository
            print("📥 Cloning repository...")
            repo = Repo.clone_from(repo_url, temp_dir)
            repo.git.checkout(branch)
            print("✅ Repository cloned successfully")
            print()
            
            # Find KQL Dashboard files (check multiple patterns)
            dashboard_files = []
            all_files = []
            
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    full_path = os.path.join(root, file)
                    all_files.append(full_path)
                    
                    # Check for various KQL Dashboard patterns
                    if (file.endswith('.KQLDashboard') or 
                        'dashboard' in file.lower() or
                        file.endswith('.kqldashboard')):
                        dashboard_files.append(full_path)
            
            # Debug: show all files in dashboards folder
            print("🔍 All files in repository:")
            dashboard_folder_files = [f for f in all_files if 'dashboard' in f.lower()]
            if dashboard_folder_files:
                for f in dashboard_folder_files[:10]:  # Show first 10
                    rel_path = os.path.relpath(f, temp_dir)
                    print(f"   📄 {rel_path}")
            else:
                print("   📄 No files with 'dashboard' in name found")
            print()
            
            if not dashboard_files:
                print("⚠️  No KQL Dashboard files found")
                return
            
            print(f"📋 Found {len(dashboard_files)} KQL Dashboard file(s):")
            for dashboard in dashboard_files:
                rel_path = os.path.relpath(dashboard, temp_dir)
                print(f"   📄 {rel_path}")
            print()
            
            # Analyze each dashboard
            for dashboard_path in dashboard_files:
                analyze_dashboard_file(dashboard_path, temp_dir)
                
            # Find available databases
            print("🔍 Available KQL Databases in repository:")
            database_files = []
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    if file.endswith('.KQLDatabase'):
                        database_files.append(os.path.join(root, file))
            
            if database_files:
                for db_path in database_files:
                    rel_path = os.path.relpath(db_path, temp_dir)
                    db_name = os.path.splitext(os.path.basename(db_path))[0]
                    print(f"   📊 {rel_path} → Database name: {db_name}")
            else:
                print("   ⚠️  No KQL Database files found")
                
        finally:
            # Clean up
            try:
                shutil.rmtree(temp_dir)
                print(f"\n🧹 Cleaned up: {temp_dir}")
            except Exception as e:
                print(f"\n⚠️  Warning: Could not clean up {temp_dir}: {e}")
                
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return

def analyze_dashboard_file(dashboard_path, repo_root):
    """Analyze a KQL Dashboard file for database references"""
    try:
        rel_path = os.path.relpath(dashboard_path, repo_root)
        print(f"🔍 Analyzing: {rel_path}")
        print("-" * 40)
        
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Look for common database reference patterns
        database_references = []
        
        # Pattern 1: Direct database name references
        import re
        patterns = [
            r'"database":\s*"([^"]+)"',
            r'"databaseName":\s*"([^"]+)"',
            r'"cluster":\s*"[^"]*\.([^"\.]+)\.kusto',
            r'\.database\(\s*[\'"]([^\'"]+)[\'"]\s*\)',
            r'eh_sassa_grants?[_\-]?(?:dev|prod|test)?',
            r'dev[_\-]?eh[_\-]?sassa[_\-]?grant',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                if match and match not in database_references:
                    database_references.append(match)
        
        # Also search for any occurrence of "eh" and "sassa" together
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            line_lower = line.lower()
            if ('eh' in line_lower and 'sassa' in line_lower) or 'database' in line_lower:
                if any(keyword in line_lower for keyword in ['eh_sassa', 'sassa_grant', 'dev-eh', 'database']):
                    print(f"   Line {i}: {line.strip()}")
        
        if database_references:
            print("\n📊 Database references found:")
            for ref in database_references:
                print(f"   🎯 {ref}")
        else:
            print("   ⚠️  No obvious database references found")
            
        print()
        
    except Exception as e:
        print(f"   ❌ Error analyzing file: {e}")
        print()

if __name__ == "__main__":
    clone_and_analyze_repo()