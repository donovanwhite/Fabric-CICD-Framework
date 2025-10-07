"""
Connection Validation Script for Fabric CICD Migration
=====================================================

This script helps validate connections and references before and after migration.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Set
import yaml

class ConnectionValidator:
    """Validates connections and references in Fabric workspace migration"""
    
    def __init__(self, repository_path: str):
        self.repository_path = Path(repository_path)
        self.parameter_file = self.repository_path / "config" / "parameter.yml"
        self.connections_found = {}
        self.references_found = {}
        
    def analyze_repository(self) -> Dict:
        """Analyze repository for connections and references"""
        
        print("🔍 Analyzing Fabric items for connections and references...")
        
        analysis = {
            'fabric_items': self._find_fabric_items(),
            'external_connections': self._find_external_connections(),
            'internal_references': self._find_internal_references(),
            'parameter_mappings': self._analyze_parameter_file(),
            'missing_connections': []
        }
        
        return analysis
    
    def _find_fabric_items(self) -> List[Dict]:
        """Find all Fabric items in repository"""
        items = []
        
        fabric_extensions = [
            'Notebook', 'Report', 'Dashboard', 'SemanticModel', 'Lakehouse',
            'Warehouse', 'DataPipeline', 'Dataflow', 'Environment', 'SQLEndpoint'
        ]
        
        for item_dir in self.repository_path.iterdir():
            if item_dir.is_dir():
                for ext in fabric_extensions:
                    if item_dir.name.endswith(f'.{ext}'):
                        name = item_dir.name[:-len(f'.{ext}')]
                        items.append({
                            'name': name,
                            'type': ext,
                            'path': str(item_dir),
                            'connections': self._analyze_item_connections(item_dir, ext)
                        })
                        break
        
        return items
    
    def _analyze_item_connections(self, item_dir: Path, item_type: str) -> Dict:
        """Analyze connections within a specific Fabric item"""
        connections = {
            'external_connections': [],
            'fabric_references': [],
            'workspace_references': []
        }
        
        # Different item types have different connection patterns
        if item_type == 'Notebook':
            connections.update(self._analyze_notebook_connections(item_dir))
        elif item_type == 'DataPipeline':
            connections.update(self._analyze_pipeline_connections(item_dir))
        elif item_type == 'Dataflow':
            connections.update(self._analyze_dataflow_connections(item_dir))
        elif item_type == 'Report':
            connections.update(self._analyze_report_connections(item_dir))
        elif item_type == 'SemanticModel':
            connections.update(self._analyze_semantic_model_connections(item_dir))
        
        return connections
    
    def _analyze_notebook_connections(self, item_dir: Path) -> Dict:
        """Analyze Notebook connections and references"""
        connections = {'external_connections': [], 'fabric_references': [], 'workspace_references': []}
        
        notebook_content = item_dir / "notebook-content.py"
        if notebook_content.exists():
            content = notebook_content.read_text(encoding='utf-8')
            
            # Look for lakehouse references in META comments
            lakehouse_pattern = r'#\s*META\s+"default_lakehouse":\s*"([0-9a-fA-F-]+)"'
            for match in re.finditer(lakehouse_pattern, content):
                connections['fabric_references'].append({
                    'type': 'lakehouse',
                    'id': match.group(1),
                    'location': 'notebook metadata'
                })
            
            # Look for workspace references
            workspace_pattern = r'#\s*META\s+"default_lakehouse_workspace_id":\s*"([0-9a-fA-F-]+)"'
            for match in re.finditer(workspace_pattern, content):
                connections['workspace_references'].append({
                    'type': 'workspace',
                    'id': match.group(1),
                    'location': 'notebook metadata'
                })
            
            # Look for SQL connections in code
            sql_pattern = r'([\w-]+\.database\.windows\.net)'
            for match in re.finditer(sql_pattern, content):
                connections['external_connections'].append({
                    'type': 'sql_server',
                    'endpoint': match.group(1),
                    'location': 'notebook code'
                })
        
        return connections
    
    def _analyze_pipeline_connections(self, item_dir: Path) -> Dict:
        """Analyze Data Pipeline connections"""
        connections = {'external_connections': [], 'fabric_references': [], 'workspace_references': []}
        
        pipeline_content = item_dir / "pipeline-content.json"
        if pipeline_content.exists():
            try:
                with open(pipeline_content, 'r', encoding='utf-8') as f:
                    pipeline_data = json.load(f)
                
                # Look for external connections in activities
                activities = pipeline_data.get('properties', {}).get('activities', [])
                for activity in activities:
                    # Check source connections
                    source = activity.get('typeProperties', {}).get('source', {})
                    if 'datasetSettings' in source:
                        conn_ref = source['datasetSettings'].get('externalReferences', {}).get('connection')
                        if conn_ref:
                            connections['external_connections'].append({
                                'type': 'external_dataset',
                                'connection_id': conn_ref,
                                'activity': activity.get('name', 'unknown'),
                                'location': 'source'
                            })
                    
                    # Check sink connections
                    sink = activity.get('typeProperties', {}).get('sink', {})
                    if 'datasetSettings' in sink:
                        linked_service = sink['datasetSettings'].get('linkedService', {})
                        if 'properties' in linked_service:
                            props = linked_service['properties'].get('typeProperties', {})
                            if 'artifactId' in props:
                                connections['fabric_references'].append({
                                    'type': 'fabric_artifact',
                                    'artifact_id': props['artifactId'],
                                    'workspace_id': props.get('workspaceId'),
                                    'activity': activity.get('name', 'unknown'),
                                    'location': 'sink'
                                })
                            
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                print(f"⚠️  Could not parse pipeline content: {e}")
        
        return connections
    
    def _analyze_dataflow_connections(self, item_dir: Path) -> Dict:
        """Analyze Dataflow connections"""
        connections = {'external_connections': [], 'fabric_references': [], 'workspace_references': []}
        
        # Check queryMetadata.json for connections
        query_metadata = item_dir / "queryMetadata.json"
        if query_metadata.exists():
            try:
                with open(query_metadata, 'r', encoding='utf-8') as f:
                    metadata = json.load(f)
                
                conn_list = metadata.get('connections', [])
                for conn in conn_list:
                    connections['external_connections'].append({
                        'type': 'dataflow_connection',
                        'kind': conn.get('kind'),
                        'connection_id': conn.get('connectionId'),
                        'location': 'queryMetadata'
                    })
                    
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                print(f"⚠️  Could not parse dataflow metadata: {e}")
        
        # Check mashup.pq for workspace/item references
        mashup_file = item_dir / "mashup.pq"
        if mashup_file.exists():
            content = mashup_file.read_text(encoding='utf-8', errors='ignore')
            
            # Look for workspace references
            workspace_pattern = r'workspaceId\s*=\s*"([0-9a-fA-F-]+)"'
            for match in re.finditer(workspace_pattern, content):
                connections['workspace_references'].append({
                    'type': 'workspace',
                    'id': match.group(1),
                    'location': 'mashup.pq'
                })
            
            # Look for lakehouse references
            lakehouse_pattern = r'lakehouseId\s*=\s*"([0-9a-fA-F-]+)"'
            for match in re.finditer(lakehouse_pattern, content):
                connections['fabric_references'].append({
                    'type': 'lakehouse',
                    'id': match.group(1),
                    'location': 'mashup.pq'
                })
        
        return connections
    
    def _analyze_report_connections(self, item_dir: Path) -> Dict:
        """Analyze Report connections to datasets"""
        connections = {'external_connections': [], 'fabric_references': [], 'workspace_references': []}
        
        # Reports typically reference semantic models
        report_content = item_dir / "report.json"
        if report_content.exists():
            try:
                with open(report_content, 'r', encoding='utf-8') as f:
                    report_data = json.load(f)
                
                # Look for dataset references
                config = report_data.get('config', '{}')
                if isinstance(config, str):
                    config = json.loads(config)
                
                # Dataset references are often in the config
                if 'modelId' in config:
                    connections['fabric_references'].append({
                        'type': 'semantic_model',
                        'id': config['modelId'],
                        'location': 'report config'
                    })
                    
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                print(f"⚠️  Could not parse report content: {e}")
        
        return connections
    
    def _analyze_semantic_model_connections(self, item_dir: Path) -> Dict:
        """Analyze Semantic Model data source connections"""
        connections = {'external_connections': [], 'fabric_references': [], 'workspace_references': []}
        
        model_bim = item_dir / "model.bim"
        if model_bim.exists():
            try:
                with open(model_bim, 'r', encoding='utf-8') as f:
                    model_data = json.load(f)
                
                # Look for data sources
                data_sources = model_data.get('model', {}).get('dataSources', [])
                for ds in data_sources:
                    conn_str = ds.get('connectionString', '')
                    if 'database.windows.net' in conn_str:
                        connections['external_connections'].append({
                            'type': 'sql_database',
                            'connection_string': conn_str,
                            'name': ds.get('name'),
                            'location': 'model.bim'
                        })
                    elif 'lakehouse' in conn_str.lower():
                        connections['fabric_references'].append({
                            'type': 'lakehouse',
                            'connection_string': conn_str,
                            'name': ds.get('name'),
                            'location': 'model.bim'
                        })
                        
            except (json.JSONDecodeError, UnicodeDecodeError) as e:
                print(f"⚠️  Could not parse semantic model: {e}")
        
        return connections
    
    def _find_external_connections(self) -> List[Dict]:
        """Find all external connections that need manual setup"""
        external_connections = []
        
        for item in self._find_fabric_items():
            for conn in item['connections']['external_connections']:
                if conn not in external_connections:
                    external_connections.append(conn)
        
        return external_connections
    
    def _find_internal_references(self) -> List[Dict]:
        """Find all internal Fabric item references"""
        internal_references = []
        
        for item in self._find_fabric_items():
            for ref in item['connections']['fabric_references']:
                if ref not in internal_references:
                    internal_references.append(ref)
        
        return internal_references
    
    def _analyze_parameter_file(self) -> Dict:
        """Analyze ../config/parameter.yml for connection mappings"""
        if not self.parameter_file.exists():
            return {'error': '../config/parameter.yml not found'}
        
        try:
            with open(self.parameter_file, 'r', encoding='utf-8') as f:
                params = yaml.safe_load(f) or {}
            
            mappings = {
                'find_replace_count': len(params.get('find_replace', [])),
                'key_value_replace_count': len(params.get('key_value_replace', [])),
                'spark_pool_count': len(params.get('spark_pool', [])),
                'environments': set(),
                'connection_mappings': []
            }
            
            # Analyze find_replace for connection updates
            for item in params.get('find_replace', []):
                replace_vals = item.get('replace_value', {})
                mappings['environments'].update(replace_vals.keys())
                
                # Check if this looks like a connection mapping
                find_val = item.get('find_value', '')
                if any(term in find_val.lower() for term in ['connection', 'server', 'database', 'storage', 'endpoint']):
                    mappings['connection_mappings'].append({
                        'type': 'connection_string',
                        'find_value': find_val,
                        'environments': list(replace_vals.keys())
                    })
            
            # Analyze key_value_replace for connection GUIDs
            for item in params.get('key_value_replace', []):
                replace_vals = item.get('replace_value', {})
                mappings['environments'].update(replace_vals.keys())
                
                find_key = item.get('find_key', '')
                if 'connection' in find_key.lower():
                    mappings['connection_mappings'].append({
                        'type': 'connection_guid',
                        'find_key': find_key,
                        'environments': list(replace_vals.keys())
                    })
            
            mappings['environments'] = list(mappings['environments'])
            return mappings
            
        except Exception as e:
            return {'error': f'Failed to parse ../config/parameter.yml: {str(e)}'}
    
    def generate_report(self) -> str:
        """Generate a comprehensive connection analysis report"""
        analysis = self.analyze_repository()
        
        report = []
        report.append("🔍 FABRIC WORKSPACE CONNECTION ANALYSIS")
        report.append("=" * 60)
        report.append("")
        
        # Fabric Items Summary
        report.append(f"📊 FABRIC ITEMS FOUND: {len(analysis['fabric_items'])}")
        for item in analysis['fabric_items']:
            report.append(f"   📁 {item['name']} ({item['type']})")
            
            ext_conns = len(item['connections']['external_connections'])
            fab_refs = len(item['connections']['fabric_references'])
            ws_refs = len(item['connections']['workspace_references'])
            
            if ext_conns > 0:
                report.append(f"      🔗 External connections: {ext_conns}")
            if fab_refs > 0:
                report.append(f"      🏢 Fabric references: {fab_refs}")
            if ws_refs > 0:
                report.append(f"      🌐 Workspace references: {ws_refs}")
        
        report.append("")
        
        # External Connections (Need Manual Setup)
        report.append("🚨 EXTERNAL CONNECTIONS (Require Manual Setup)")
        report.append("-" * 50)
        
        if analysis['external_connections']:
            for conn in analysis['external_connections']:
                report.append(f"   ⚠️  {conn.get('type', 'Unknown')}")
                if 'endpoint' in conn:
                    report.append(f"      Endpoint: {conn['endpoint']}")
                if 'connection_id' in conn:
                    report.append(f"      Connection ID: {conn['connection_id']}")
                report.append(f"      Location: {conn.get('location', 'Unknown')}")
                report.append("")
        else:
            report.append("   ✅ No external connections found")
        
        report.append("")
        
        # Internal References (Automatically Handled)
        report.append("✅ INTERNAL REFERENCES (Automatically Handled)")
        report.append("-" * 50)
        
        if analysis['internal_references']:
            for ref in analysis['internal_references']:
                report.append(f"   🏢 {ref.get('type', 'Unknown')}")
                if 'id' in ref:
                    report.append(f"      ID: {ref['id']}")
                report.append(f"      Location: {ref.get('location', 'Unknown')}")
                report.append("")
        else:
            report.append("   ℹ️  No internal references found")
        
        report.append("")
        
        # Parameter File Analysis
        param_analysis = analysis['parameter_mappings']
        report.append("⚙️  PARAMETER CONFIGURATION")
        report.append("-" * 50)
        
        if 'error' in param_analysis:
            report.append(f"   ❌ {param_analysis['error']}")
        else:
            report.append(f"   📝 Find/Replace rules: {param_analysis['find_replace_count']}")
            report.append(f"   🔧 Key/Value rules: {param_analysis['key_value_replace_count']}")
            report.append(f"   ⚡ Spark pool rules: {param_analysis['spark_pool_count']}")
            report.append(f"   🌍 Environments: {', '.join(param_analysis['environments'])}")
            report.append("")
            
            if param_analysis['connection_mappings']:
                report.append("   🔗 Connection mappings found:")
                for mapping in param_analysis['connection_mappings']:
                    report.append(f"      • {mapping['type']}")
                    if 'find_value' in mapping:
                        report.append(f"        Find: {mapping['find_value']}")
                    if 'find_key' in mapping:
                        report.append(f"        Key: {mapping['find_key']}")
                    report.append(f"        Environments: {', '.join(mapping['environments'])}")
                    report.append("")
        
        report.append("")
        report.append("📋 DEPLOYMENT OPTIONS")
        report.append("-" * 30)
        report.append("🆕 NEW WORKSPACE:")
        report.append("   • fabric-cicd creates items in empty workspace")
        report.append("   • No conflicts with existing items")
        report.append("   • Clean deployment environment")
        report.append("")
        report.append("♻️  EXISTING WORKSPACE:")
        report.append("   • fabric-cicd updates/replaces existing items")
        report.append("   • Items with same name are overwritten")
        report.append("   • Preserves other items not in repository")
        report.append("   • Ideal for iterative deployments")
        report.append("")
        report.append("📋 RECOMMENDED ACTIONS")
        report.append("-" * 30)
        report.append("1. ✅ Choose target workspace (new or existing)")
        report.append("2. ✅ Create external connections manually in target workspace")
        report.append("3. ✅ Update connection GUIDs in ../config/parameter.yml")
        report.append("4. ✅ Verify fabric-to-fabric references use dynamic variables")
        report.append("5. ✅ Test connectivity after migration")
        report.append("6. ✅ Validate existing items won't conflict (if using existing workspace)")
        
        return "\n".join(report)

def main():
    """Main function to run connection analysis"""
    import sys
    
    if len(sys.argv) > 1:
        repo_path = sys.argv[1]
    else:
        repo_path = "."
    
    print(f"🔍 Analyzing connections in: {repo_path}")
    
    validator = ConnectionValidator(repo_path)
    report = validator.generate_report()
    
    print(report)
    
    # Save report to file
    report_file = Path(repo_path) / "connection_analysis_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📄 Report saved to: {report_file}")

if __name__ == "__main__":
    main()
