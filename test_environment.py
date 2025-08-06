#!/usr/bin/env python3
"""
Test script to verify fabric-cicd environment setup
"""

def test_imports():
    """Test that all required packages can be imported"""
    try:
        import fabric_cicd
        print("✅ fabric-cicd imported successfully")
        
        from fabric_cicd import FabricWorkspace
        print("✅ FabricWorkspace imported successfully")
        
        from azure.identity import AzureCliCredential, DefaultAzureCredential
        print("✅ Azure identity imported successfully")
        
        import yaml
        print("✅ PyYAML imported successfully")
        
        import click
        print("✅ Click imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        return False

def test_python_version():
    """Test Python version compatibility"""
    import sys
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if (3, 9) <= version < (3, 13):
        print("✅ Python version is compatible with fabric-cicd")
        return True
    else:
        print("❌ Python version is NOT compatible with fabric-cicd")
        print("   Required: Python >=3.9 and <3.13")
        return False

def main():
    print("🧪 Testing Fabric CICD Environment Setup")
    print("=" * 50)
    
    # Test Python version
    python_ok = test_python_version()
    print()
    
    # Test imports
    imports_ok = test_imports()
    print()
    
    # Overall result
    if python_ok and imports_ok:
        print("🎉 Environment setup is SUCCESSFUL!")
        print("✅ Ready to use fabric-cicd for deployment")
        print()
        print("📋 Next steps:")
        print("   1. Configure parameter.yml with your workspace details")
        print("   2. Set up Azure CLI authentication: az login")
        print("   3. Test deployment with: python fabric_deploy_local.py --help")
        return 0
    else:
        print("❌ Environment setup has ISSUES")
        print("   Please review the errors above and fix them")
        return 1

if __name__ == "__main__":
    exit(main())
