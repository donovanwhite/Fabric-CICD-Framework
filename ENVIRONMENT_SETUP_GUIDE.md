# Environment Setup Options Guide

## Choose Your Python Environment Manager

This project supports two Python environment management approaches to accommodate different user needs and system constraints.

## 🐍 Option 1: Conda Environment (Recommended)

**Use when:**
- ✅ You have Anaconda or Miniconda installed
- ✅ You prefer comprehensive package management
- ✅ You work with data science or scientific computing
- ✅ You want the most reliable cross-platform experience

**Setup:**
```batch
setup.bat
activate_fabric_env.bat
```

**Pros:**
- 🔧 Complete package management (Python + system libraries)
- 🚀 Faster setup and dependency resolution
- 📦 Better handling of complex dependencies
- 🔄 Easy environment switching
- 💪 Robust and mature ecosystem

**Cons:**
- 📁 Requires Anaconda/Miniconda installation (~400MB+)
- 🚫 May not be allowed in some corporate environments
- 💾 Uses more disk space

## 🎯 Option 2: PyEnv + Virtual Environment

**Use when:**
- ✅ You cannot install Anaconda/Miniconda
- ✅ You're in a restricted corporate environment
- ✅ You prefer lightweight Python version management
- ✅ You want more control over Python versions

**Setup:**
```batch
setup_pyenv.bat
activate_fabric_env_pyenv.bat
```

**Pros:**
- 🪶 Lightweight Python version management
- 🔓 Works in restricted environments
- 🎛️ Fine-grained Python version control
- 📦 Standard Python tooling (pip, venv)
- 🏢 Corporate-friendly

**Cons:**
- ⏱️ Longer initial setup time
- 🔧 More manual configuration required
- 📋 Requires Git for pyenv-win installation
- 🐛 Potentially more troubleshooting needed

## 📊 Quick Comparison

| Feature | Conda | PyEnv + venv |
|---------|-------|--------------|
| Installation Size | Large (~400MB+) | Small (~50MB) |
| Setup Complexity | Simple | Moderate |
| Corporate Friendly | Sometimes | Usually |
| Package Management | Excellent | Good |
| Python Version Control | Good | Excellent |
| Dependency Resolution | Excellent | Good |

## 🚀 Recommendation

1. **First choice**: Try `setup.bat` (conda approach)
2. **If conda fails or not allowed**: Use `setup_pyenv.bat` (pyenv approach)
3. **If both fail**: Manual pip installation

## 🔄 Switching Between Approaches

You can have both environments set up simultaneously:
- Conda environment: `activate_fabric_env.bat`
- PyEnv environment: `activate_fabric_env_pyenv.bat`

## 🆘 Troubleshooting

### Conda Issues
- Ensure Anaconda/Miniconda is properly installed
- Check PATH environment variables
- Run `conda info` to verify installation

### PyEnv Issues  
- Ensure Git is installed and accessible
- Check if pyenv-win is in PATH
- Restart command prompt after pyenv installation
- Run `pyenv versions` to verify installation

### Both Failing
- Use manual installation: `pip install fabric-cicd azure-identity PyYAML`
- Ensure Python 3.8+ is installed
- Check your corporate firewall/proxy settings
