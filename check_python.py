#!/usr/bin/env python3
"""
Python Version Checker for fabric-cicd
======================================
This script checks if your Python version is compatible with fabric-cicd
"""

import sys

def check_python_version():
    """Check if Python version is compatible with fabric-cicd"""
    major, minor = sys.version_info[:2]
    current_version = f"{major}.{minor}"
    
    print("=" * 50)
    print("Python Version Compatibility Check")
    print("=" * 50)
    print(f"Current Python version: {sys.version}")
    print(f"Version: {current_version}")
    
    # fabric-cicd requires Python >=3.9 and <3.13
    if major == 3 and 9 <= minor <= 12:
        print("✅ COMPATIBLE: Your Python version works with fabric-cicd")
        return True
    else:
        print("❌ INCOMPATIBLE: fabric-cicd requires Python 3.9-3.12")
        print("\n💡 Solutions:")
        
        if major == 3 and minor >= 13:
            print("   Your Python is too new (3.13+)")
            print("   1. Install Python 3.12: https://www.python.org/downloads/")
            print("   2. Use pyenv: pyenv install 3.12.7 && pyenv local 3.12.7")
            print("   3. Use conda: conda create -n fabric-cicd python=3.12")
        elif major == 3 and minor < 9:
            print("   Your Python is too old (<3.9)")
            print("   1. Update Python: https://www.python.org/downloads/")
            print("   2. Use pyenv: pyenv install 3.12.7 && pyenv local 3.12.7")
            print("   3. Use conda: conda create -n fabric-cicd python=3.12")
        else:
            print("   You're not using Python 3")
            print("   1. Install Python 3.12: https://www.python.org/downloads/")
        
        print("\n📚 Documentation:")
        print("   - pyenv: https://github.com/pyenv/pyenv")
        print("   - conda: https://docs.conda.io/projects/conda/")
        
        return False

if __name__ == "__main__":
    is_compatible = check_python_version()
    
    if is_compatible:
        print("\n🚀 Next steps:")
        print("   1. Run: pip install -r requirements.txt")
        print("   2. Or run: setup.bat")
        print("   3. Configure parameter.yml")
        print("   4. Test: python fabric_deploy_local.py --help")
    else:
        print("\n⚠️  Please fix Python version before proceeding")
    
    print("=" * 50)
    sys.exit(0 if is_compatible else 1)
