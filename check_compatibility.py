#!/usr/bin/env python3
"""
Fabric CICD Version Compatibility Checker
==========================================
This script checks if your environment meets the requirements for Fabric CICD deployment.
"""

import sys

def check_python_version():
    """Check if Python version is compatible"""
    print("🔍 Checking Python version...")
    
    version_info = sys.version_info
    version_str = f"{version_info.major}.{version_info.minor}.{version_info.micro}"
    
    print(f"   Current Python: {version_str}")
    
    if version_info < (3, 8):
        print("❌ Python version incompatible")
        print("   Required: Python 3.8 or higher")
        print("💡 Please upgrade Python or use a compatible environment")
        return False
    elif version_info >= (3, 13):
        print("⚠️  Python version may have compatibility issues")
        print("   fabric-cicd officially supports Python < 3.13")
        print("💡 Consider using Python 3.12 for best compatibility")
        return True
    else:
        print("✅ Python version compatible")
        return True

def check_fabric_cicd_version():
    """Check if fabric-cicd is installed and functional"""
    print("\n🔍 Checking fabric-cicd...")
    
    try:
        import fabric_cicd
        
        # Try different ways to get the version
        current_version = None
        
        # Method 1: Direct __version__ attribute
        if hasattr(fabric_cicd, '__version__'):
            current_version = fabric_cicd.__version__
        
        # Method 2: Using importlib.metadata (Python 3.8+)
        if not current_version:
            try:
                import importlib.metadata
                current_version = importlib.metadata.version('fabric-cicd')
            except Exception:
                pass
        
        # Method 3: Using pkg_resources (fallback)
        if not current_version:
            try:
                import pkg_resources
                current_version = pkg_resources.get_distribution('fabric-cicd').version
            except Exception:
                pass
        
        # Report status regardless of version - using latest version approach
        if current_version:
            print(f"✅ fabric-cicd version {current_version} installed")
        else:
            print("✅ fabric-cicd installed and importable (version not detectable)")
        
        print("   Using latest version approach - setup always installs newest version")
        return True
        
    except ImportError:
        print("❌ fabric-cicd not installed")
        print("💡 Install with: pip install fabric-cicd")
        return False

def check_dependencies():
    """Check if all required dependencies are available"""
    print("\n🔍 Checking dependencies...")
    
    dependencies = {
        'azure.identity': 'Azure authentication',
        'git': 'Git operations (GitPython)',
        'yaml': 'YAML processing (PyYAML)',
        'pathlib': 'Path handling (built-in)',
        'tempfile': 'Temporary files (built-in)',
        'argparse': 'Command line parsing (built-in)'
    }
    
    missing = []
    
    for module, description in dependencies.items():
        try:
            __import__(module)
            print(f"   ✅ {description}")
        except ImportError:
            print(f"   ❌ {description}")
            missing.append(module)
    
    if missing:
        print(f"\n💡 Install missing dependencies:")
        if 'azure.identity' in missing:
            print("   pip install azure-identity")
        if 'git' in missing:
            print("   pip install GitPython")
        if 'yaml' in missing:
            print("   pip install PyYAML")
        return False
    
    return True

def check_azure_auth():
    """Check if Azure authentication is configured"""
    print("\n🔍 Checking Azure authentication...")
    
    try:
        from azure.identity import DefaultAzureCredential
        # Try to get a credential (this doesn't actually authenticate)
        credential = DefaultAzureCredential()
        print("✅ Azure authentication libraries available")
        print("💡 Use 'az login' to authenticate before deployment")
        return True
    except ImportError:
        print("❌ Azure authentication libraries not available")
        print("💡 Install with: pip install azure-identity")
        return False
    except Exception as e:
        print(f"⚠️  Azure authentication setup issue: {e}")
        print("💡 This may be normal - authenticate with 'az login' before deployment")
        return True

def main():
    """Run all compatibility checks"""
    print("🔧 FABRIC CICD COMPATIBILITY CHECKER")
    print("=" * 40)
    
    checks = [
        check_python_version(),
        check_fabric_cicd_version(),
        check_dependencies(),
        check_azure_auth()
    ]
    
    print("\n📋 COMPATIBILITY SUMMARY")
    print("=" * 30)
    
    if all(checks):
        print("🎉 All checks passed! Your environment is ready for Fabric CICD.")
        print("\n🚀 Next steps:")
        print("   1. Authenticate: az login")
        print("   2. Test deployment: python fabric_deploy.py --help")
        print("   3. Run deployment: python fabric_deploy.py --workspace-id <id> --repo-url <url>")
    else:
        print("⚠️  Some compatibility issues found.")
        print("💡 Please address the issues above before running Fabric CICD.")
        print("\n🔧 Quick fixes:")
        print("   • Update Python: Use Python 3.8-3.12")
        print("   • Upgrade fabric-cicd: pip install --upgrade fabric-cicd")
        print("   • Install dependencies: pip install -r requirements.txt")
        
    print(f"\n📊 Check results: {sum(checks)}/{len(checks)} passed")
    
    return all(checks)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
