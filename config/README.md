# Configuration Files

This folder contains all configuration files for the Fabric CI/CD Framework.

## Files

### Parameter Files
- **`parameter.yml`** - Main parameter configuration with environment-specific values
- **`parameter.yml`** - Main parameter file with v0.1.29 features and examples

### Configuration Files
- **`config.yml`** - Configuration-based deployment settings for v0.1.29

## Usage

1. **Configure parameters**: Edit `parameter.yml` with your environment-specific values
2. **Configure environments**: Update parameter files with your specific environment values
3. **Set up authentication**: Configure service principal or interactive authentication
4. **Configure deployment**: Modify `config.yml` for configuration-based deployment approach

## Environment Variables

The parameter files support environment-specific configurations using:
- `_ALL_` key for common settings across all environments
- `$ENV:VARIABLE_NAME` syntax for environment variable substitution
- Environment-specific sections (dev, test, prod, etc.)

## Security

- Never commit sensitive values like secrets or passwords
- Use Azure Key Vault references or environment variables for sensitive data
- Keep example files generic and remove any real credentials before committing