# DevOps CI/CD Configurations

This folder contains CI/CD pipeline configurations and DevOps-related files for the Fabric-CICD Framework.

## Files

- **`azure-pipelines.yml`** - Azure DevOps pipeline configuration for automated deployment with warehouse schema support

## Azure Pipeline Features

The pipeline configuration includes:

- **Multi-environment support**: Separate stages for dev, test, and production
- **Warehouse schema deployment**: Full support for Microsoft Fabric warehouse schema deployment using .NET SDK and SqlPackage.exe
- **Service principal authentication**: Secure authentication using Azure service connections
- **Artifact management**: Proper handling of deployment artifacts and DACPAC files
- **Environment-specific parameters**: Dynamic parameter loading based on target environment
- **Pull request validation**: Comprehensive validation including warehouse schema changes
- **Error handling and reporting**: Comprehensive logging and failure notifications

## Usage

1. **Import pipeline**: Import `azure-pipelines.yml` into your Azure DevOps project
2. **Configure service connections**: Set up Azure service principal connections
3. **Set pipeline variables**: Configure environment-specific variables in Azure DevOps
4. **Configure branch policies**: Set up branch protection and approval gates
5. **Run pipeline**: Trigger deployments manually or through branch policies

## Pipeline Structure

```yaml
# Typical pipeline flow:
1. Checkout code
2. Setup Python environment
3. Install dependencies (Python packages, .NET SDK, SqlPackage.exe)
4. Validate configuration and warehouse schemas
5. Deploy Fabric items and warehouse schemas to target environment
6. Run post-deployment tests
7. Generate deployment report
```

### Warehouse Schema Pipeline Steps

The pipeline includes specialized steps for warehouse schema deployment:

1. **Install .NET SDK**: Downloads and installs the latest .NET SDK
2. **Install SqlPackage.exe**: Installs Microsoft SqlPackage as a global .NET tool
3. **Build DACPAC**: Uses `dotnet build` to compile warehouse schema projects
4. **Deploy Schemas**: Uses SqlPackage.exe to deploy DACPAC files to Fabric warehouses
5. **Validate Deployment**: Confirms successful schema deployment

## Environment Variables

Configure these variables in Azure DevOps pipeline settings:

### Authentication Variables
- `FABRIC_TENANT_ID` - Azure tenant ID for authentication
- `FABRIC_CLIENT_ID` - Service principal client ID
- `FABRIC_CLIENT_SECRET` - Service principal client secret

### Environment Configuration
- `FABRIC_WORKSPACE_ID` - Target Fabric workspace ID
- `REPO_URL` - Repository URL for source control
- Environment-specific workspace IDs and settings

### Warehouse Schema Variables (Optional)
- `WAREHOUSE_CONNECTION_STRING` - Override connection string for warehouse deployment
- `SQLPACKAGE_TIMEOUT` - Timeout for SqlPackage.exe operations (default: 300 seconds)

## Deployment Commands

The pipeline supports both traditional configuration-based deployment and direct command-line deployment:

### Configuration-Based Deployment
```bash
python core/fabric_deploy.py --config path/to/config.yml --include-warehouse-schemas
```

### Direct Command-Line Deployment
```bash
python core/fabric_deploy.py \
  --workspace-id "your-workspace-id" \
  --repo-url "https://github.com/your-org/your-repo" \
  --branch "main" \
  --include-warehouse-schemas
```

### Warehouse Schema Only Deployment
```bash
python core/warehouse_schema_deploy_sqlpackage.py \
  --workspace-id "your-workspace-id" \
  --project-path "path/to/warehouse/project"
```

## Required Azure Agent Capabilities

For warehouse schema deployment, ensure your build agents have:
- Ubuntu-based agents (recommended)
- Internet access for downloading .NET SDK and SqlPackage.exe
- Sufficient disk space for .NET tooling and DACPAC files

## Security Considerations

- Use Azure Key Vault for sensitive values
- Implement proper RBAC for pipeline access
- Enable audit logging for deployment activities
- Use service connections instead of direct credentials
- Warehouse deployments use Active Directory Interactive authentication for enhanced security
- Consider using managed identity for production deployments

## Troubleshooting

### Common Issues
- **SqlPackage.exe not found**: Ensure .NET SDK installation step completed successfully
- **Warehouse connection failures**: Verify Active Directory authentication and workspace permissions
- **DACPAC build failures**: Check .sqlproj file structure and MSBuild compatibility
- **Timeout errors**: Increase `SQLPACKAGE_TIMEOUT` variable for large schema deployments

### Debug Mode
Enable verbose logging by adding `--debug` flag to deployment commands in the pipeline.
