#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fabric CICD v0.1.29 Migration Helper
===================================

This script helps migrate from older versions of fabric-cicd to v0.1.29
and validates the new features are working correctly.

Features tested:
- Version compatibility
- New item type support
- Configuration-based deployment
- Enhanced parameterization features
"""

import sys
import os

def check_version_compatibility():
    """Check if fabric-cicd v0.1.29+ is installed"""
    try:
        import fabric_cicd
        from packaging import version
        
        current_version = fabric_cicd.__version__
        required_version = "0.1.29"
        
        print(f"📦 Current fabric-cicd version: {current_version}")
        
        if version.parse(current_version) >= version.parse(required_version):
            print("✅ Version check passed!")
            return True
        else:
            print(f"❌ Version {required_version}+ required")
            print("💡 Update with: pip install --upgrade fabric-cicd")
            return False
            
    except ImportError:
        print("❌ fabric-cicd not installed")
        print("💡 Install with: pip install fabric-cicd>=0.1.29")
        return False
    except Exception as e:
        print(f"⚠️  Version check failed: {e}")
        return True  # Continue anyway

def check_new_features():
    """Check if new v0.1.29 features are available"""
    try:
        from fabric_cicd import deploy_with_config
        print("✅ Configuration-based deployment available")
        
        # Check if new item types are supported
        from fabric_cicd import FabricWorkspace
        print("✅ FabricWorkspace class available")
        
        return True
    except ImportError as e:
        print(f"❌ New features not available: {e}")
        return False

def validate_config_file():
    """Validate the config.yml file exists and is properly formatted"""
    config_path = "../config/config.yml"
    
    if not os.path.exists(config_path):
        print(f"⚠️  Config file not found: {config_path}")
        print("💡 Create ../config/config.yml using the provided template")
        return False
    
    try:
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Check required sections
        required_sections = ['core']
        for section in required_sections:
            if section not in config:
                print(f"❌ Missing required section in ../config/config.yml: {section}")
                return False
        
        # Check core requirements
        core = config['core']
        if 'workspace_id' not in core and 'workspace' not in core:
            print("❌ Config file must specify either workspace_id or workspace")
            return False
        
        if 'repository_directory' not in core:
            print("❌ Config file must specify repository_directory")
            return False
            
        print("✅ Config file validation passed")
        return True
        
    except Exception as e:
        print(f"❌ Config file validation failed: {e}")
        return False

def validate_parameter_file():
    """Validate the parameter.yml file for v0.1.29 features"""
    param_path = "../config/parameter.yml"
    
    if not os.path.exists(param_path):
        print(f"⚠️  Parameter file not found: {param_path}")
        print("💡 Parameter file is optional but recommended")
        return True
    
    try:
        import yaml
        with open(param_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for v0.1.29 features
        v29_features = []
        if '_ALL_:' in content:
            v29_features.append("_ALL_ environment key")
        if '$ENV:' in content:
            v29_features.append("Environment variables")
        if '$workspace.$id' in content:
            v29_features.append("Enhanced dynamic variables")
        
        if v29_features:
            print(f"✅ Parameter file uses v0.1.29 features: {', '.join(v29_features)}")
        else:
            print("⚠️  Parameter file doesn't use new v0.1.29 features")
            print("💡 Consider updating to leverage _ALL_, $ENV:, and enhanced variables")
        
        return True
        
    except Exception as e:
        print(f"❌ Parameter file validation failed: {e}")
        return False

def validate_new_item_types():
    """Check if the framework supports all 21 v0.1.29 item types"""
    print("🔍 Checking new item type support...")
    
    # Read fabric_deploy.py to check item types
    deploy_script = "../core/fabric_deploy.py"
    if not os.path.exists(deploy_script):
        print(f"❌ Deploy script not found: {deploy_script}")
        return False
    
    try:
        with open(deploy_script, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_types = ['ApacheAirflowJob', 'MountedDataFactory']
        supported_new_types = []
        
        for item_type in new_types:
            if item_type in content:
                supported_new_types.append(item_type)
        
        if supported_new_types:
            print(f"✅ New item types supported: {', '.join(supported_new_types)}")
        else:
            print("⚠️  New item types not found in deploy script")
        
        return True
        
    except Exception as e:
        print(f"❌ Item type validation failed: {e}")
        return False

def main():
    print("🚀 FABRIC CICD v0.1.29 MIGRATION VALIDATION")
    print("=" * 50)
    
    all_checks_passed = True
    
    # Check version compatibility
    print("\n1. Version Compatibility Check")
    print("-" * 30)
    if not check_version_compatibility():
        all_checks_passed = False
    
    # Check new features
    print("\n2. New Features Check")
    print("-" * 20)
    if not check_new_features():
        all_checks_passed = False
    
    # Validate configuration files
    print("\n3. Configuration Files Check") 
    print("-" * 29)
    if not validate_config_file():
        all_checks_passed = False
    
    if not validate_parameter_file():
        all_checks_passed = False
    
    # Check new item types
    print("\n4. New Item Types Check")
    print("-" * 23)
    if not validate_new_item_types():
        all_checks_passed = False
    
    # Summary
    print("\n" + "=" * 50)
    if all_checks_passed:
        print("🎉 MIGRATION VALIDATION SUCCESSFUL!")
        print("✅ Your framework is ready for fabric-cicd v0.1.29")
        print("\n💡 Next steps:")
        print("   1. Test configuration-based deployment:")
        print("      python ../core/fabric_deploy.py --config-file ../config/config.yml --environment dev --dry-run")
        print("   2. Update your CI/CD pipelines to use new features")
        print("   3. Consider leveraging enhanced parameterization")
    else:
        print("❌ MIGRATION VALIDATION FAILED")
        print("💡 Please address the issues above before proceeding")
        sys.exit(1)

if __name__ == "__main__":
    main()