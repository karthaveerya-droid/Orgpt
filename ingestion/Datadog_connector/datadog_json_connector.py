"""
datadog_json_connector.py
=========================
Connector for structured Datadog JSON files (sample_datadog.json).

Features:
- Parses structured Datadog JSON with services, monitors, incidents, etc.
- Creates semantic chunks per entity (1 service = 1 chunk, 1 incident = 1 chunk)
- Rich metadata for precise retrieval
- Human-readable formatted text for LLM context

Usage:
    connector = DatadogJSONConnector("sample_datadog.json")
    documents = connector.extract_documents()
"""

import json
import logging
import os
from typing import List, Dict, Any, Optional
from datetime import datetime

from ingestion.base_connector import DataSourceConnector

logger = logging.getLogger(__name__)


class DatadogJSONConnector(DataSourceConnector):
    """
    Extracts structured data from Datadog JSON files and creates semantic chunks.
    
    Each entity type (service, monitor, incident, team) becomes a separate document
    with rich metadata for precise retrieval.
    """
    
    def __init__(self, json_file: str):
        """
        Initialize Datadog JSON connector.
        
        Args:
            json_file: Path to Datadog JSON file (absolute or relative to project root)
        """
        # Handle both absolute and relative paths
        if not os.path.isabs(json_file):
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
            json_file = os.path.join(project_root, json_file)
        
        self.json_file = json_file
        self.data: Optional[Dict[str, Any]] = None
        
        logger.info(f"DatadogJSONConnector initialized with file: {json_file}")
    
    def get_source_name(self) -> str:
        """Return source name."""
        return "Datadog JSON File"
    
    def get_metadata(self) -> Dict[str, Any]:
        """Return connector metadata."""
        return {
            "source_type": "datadog_json",
            "file": os.path.basename(self.json_file),
            "version": "1.0"
        }
    
    def extract_documents(self) -> List[str]:
        """
        Extract and format all entities from Datadog JSON.
        
        Returns:
            List of formatted text documents (one per entity)
        """
        try:
            # Load JSON file
            with open(self.json_file, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            
            logger.info(f"✓ Loaded Datadog JSON from {self.json_file}")
            
            documents = []
            
            # Extract different entity types
            documents.extend(self._extract_services())
            documents.extend(self._extract_monitors())
            documents.extend(self._extract_incidents())
            documents.extend(self._extract_teams())
            documents.extend(self._extract_dependency_graph())
            
            logger.info(f"✓ Extracted {len(documents)} documents from Datadog JSON")
            
            return documents
            
        except FileNotFoundError:
            logger.error(f"✗ File not found: {self.json_file}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"✗ Invalid JSON in {self.json_file}: {e}")
            return []
        except Exception as e:
            logger.error(f"✗ Error extracting from Datadog JSON: {e}", exc_info=True)
            return []
    
    def _extract_services(self) -> List[str]:
        """Extract and format service entities."""
        services = self.data.get("services", [])
        documents = []
        
        for service in services:
            text = self._format_service(service)
            documents.append(text)
        
        logger.info(f"  ✓ Extracted {len(documents)} services")
        return documents
    
    def _format_service(self, service: Dict[str, Any]) -> str:
        """Format a service entity as human-readable text."""
        lines = []
        
        # Header
        lines.append(f"═══════════════════════════════════════════════════════════════")
        lines.append(f"SERVICE: {service['service_name']}")
        lines.append(f"═══════════════════════════════════════════════════════════════")
        lines.append("")
        
        # Basic info
        lines.append(f"Team: {service.get('team', 'N/A')}")
        lines.append(f"Owner: {service.get('owner', 'N/A')}")
        lines.append(f"Language: {service.get('language', 'N/A')} | Type: {service.get('type', 'N/A')} | Tier: {service.get('tier', 'N/A')}")
        lines.append(f"Repository: {service.get('repo', 'N/A')}")
        
        if service.get('docs'):
            lines.append(f"Documentation: {service['docs']}")
        
        lines.append("")
        
        # Dependencies
        if service.get('dependencies'):
            lines.append("DEPENDENCIES:")
            for dep in service['dependencies']:
                lines.append(f"  • {dep}")
            lines.append("")
        
        # Dependents
        if service.get('dependents'):
            lines.append("DEPENDENT SERVICES (who depends on this):")
            for dep in service['dependents']:
                lines.append(f"  • {dep}")
            lines.append("")
        
        # SLOs
        if service.get('slos'):
            lines.append("SERVICE LEVEL OBJECTIVES (SLOs):")
            for slo in service['slos']:
                status_emoji = "✅" if slo['status'] == "OK" else "⚠️" if slo['status'] == "WARNING" else "❌"
                lines.append(f"  {status_emoji} {slo['name']}")
                lines.append(f"     Target: {slo['target']}% | Current: {slo['current']}% | Status: {slo['status']}")
                lines.append(f"     Window: {slo['window']}")
            lines.append("")
        
        # Metrics
        if service.get('metrics'):
            metrics = service['metrics']
            lines.append("PERFORMANCE METRICS:")
            
            if 'request_rate' in metrics:
                rr = metrics['request_rate']
                lines.append(f"  • Request Rate: {rr['value']} {rr['unit']} (trend: {rr['trend']})")
            
            if 'error_rate' in metrics:
                er = metrics['error_rate']
                lines.append(f"  • Error Rate: {er['value']}{er['unit']} (trend: {er['trend']})")
            
            if all(k in metrics for k in ['p50_latency_ms', 'p95_latency_ms', 'p99_latency_ms']):
                lines.append(f"  • Latency: p50={metrics['p50_latency_ms']}ms, p95={metrics['p95_latency_ms']}ms, p99={metrics['p99_latency_ms']}ms")
            
            if 'apdex' in metrics:
                lines.append(f"  • Apdex Score: {metrics['apdex']}")
            
            # Custom metrics
            if 'custom' in metrics:
                lines.append("  • Custom Metrics:")
                for key, value in metrics['custom'].items():
                    lines.append(f"      - {key}: {value}")
            
            lines.append("")
        
        # Infrastructure
        if service.get('infrastructure'):
            infra = service['infrastructure']
            lines.append("INFRASTRUCTURE:")
            
            if 'hosts' in infra:
                lines.append(f"  • Hosts: {', '.join(infra['hosts'])}")
            
            lines.append(f"  • Containers: {infra.get('containers', 'N/A')}")
            lines.append(f"  • CPU Usage: {infra.get('avg_cpu_percent', 'N/A')}% avg")
            lines.append(f"  • Memory Usage: {infra.get('avg_memory_percent', 'N/A')}% avg")
            lines.append("")
        
        # Tags
        if service.get('tags'):
            lines.append(f"TAGS: {', '.join(service['tags'])}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _extract_monitors(self) -> List[str]:
        """Extract and format monitor entities."""
        monitors = self.data.get("monitors", [])
        documents = []
        
        for monitor in monitors:
            text = self._format_monitor(monitor)
            documents.append(text)
        
        logger.info(f"  ✓ Extracted {len(documents)} monitors")
        return documents
    
    def _format_monitor(self, monitor: Dict[str, Any]) -> str:
        """Format a monitor entity as human-readable text."""
        lines = []
        
        # Header
        status_emoji = "🔴" if monitor['status'] == "ALERT" else "⚠️" if monitor['status'] == "WARNING" else "🟢"
        lines.append(f"═══════════════════════════════════════════════════════════════")
        lines.append(f"{status_emoji} MONITOR: {monitor['name']}")
        lines.append(f"═══════════════════════════════════════════════════════════════")
        lines.append("")
        
        # Basic info
        lines.append(f"ID: {monitor['id']}")
        lines.append(f"Type: {monitor['type']}")
        lines.append(f"Status: {monitor['status']}")
        lines.append(f"Service: {monitor.get('service', 'N/A')}")
        lines.append(f"Team: {monitor.get('team', 'N/A')}")
        lines.append("")
        
        # Query
        lines.append("QUERY:")
        lines.append(f"  {monitor['query']}")
        lines.append("")
        
        # Thresholds
        if monitor.get('threshold'):
            threshold = monitor['threshold']
            lines.append("THRESHOLDS:")
            if 'critical' in threshold:
                lines.append(f"  • Critical: {threshold['critical']}")
            if 'warning' in threshold:
                lines.append(f"  • Warning: {threshold['warning']}")
            lines.append("")
        
        # Notifications
        if monitor.get('notify'):
            lines.append(f"NOTIFICATIONS: {', '.join(monitor['notify'])}")
            lines.append("")
        
        # Last triggered
        if monitor.get('last_triggered'):
            lines.append(f"Last Triggered: {monitor['last_triggered']}")
            if monitor.get('triggered_duration_minutes'):
                lines.append(f"Duration: {monitor['triggered_duration_minutes']} minutes")
            lines.append("")
        
        # Tags
        if monitor.get('tags'):
            lines.append(f"TAGS: {', '.join(monitor['tags'])}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _extract_incidents(self) -> List[str]:
        """Extract and format incident entities."""
        incidents = self.data.get("incidents", [])
        documents = []
        
        for incident in incidents:
            text = self._format_incident(incident)
            documents.append(text)
        
        logger.info(f"  ✓ Extracted {len(documents)} incidents")
        return documents
    
    def _format_incident(self, incident: Dict[str, Any]) -> str:
        """Format an incident entity as human-readable text."""
        lines = []
        
        # Header
        status_emoji = "🔴" if incident['status'] == "active" else "✅"
        lines.append(f"═══════════════════════════════════════════════════════════════")
        lines.append(f"{status_emoji} INCIDENT: {incident['title']}")
        lines.append(f"═══════════════════════════════════════════════════════════════")
        lines.append("")
        
        # Basic info
        lines.append(f"ID: {incident['id']}")
        lines.append(f"Status: {incident['status'].upper()}")
        lines.append(f"Severity: {incident['severity']}")
        lines.append(f"Team: {incident.get('team', 'N/A')}")
        lines.append(f"Commander: {incident.get('commander', 'N/A')}")
        lines.append("")
        
        # Services affected
        if incident.get('services_affected'):
            lines.append(f"SERVICES AFFECTED: {', '.join(incident['services_affected'])}")
            lines.append("")
        
        # Timeline
        lines.append(f"Started: {incident.get('started_at', 'N/A')}")
        if incident.get('resolved_at'):
            lines.append(f"Resolved: {incident['resolved_at']}")
        
        if incident.get('ttd_minutes'):
            lines.append(f"Time to Detect: {incident['ttd_minutes']} minutes")
        if incident.get('ttr_minutes'):
            lines.append(f"Time to Resolve: {incident['ttr_minutes']} minutes")
        
        lines.append("")
        
        # Customer impact
        if incident.get('customer_impact'):
            lines.append("CUSTOMER IMPACT:")
            lines.append(f"  {incident['customer_impact']}")
            lines.append("")
        
        # Root cause
        if incident.get('root_cause'):
            lines.append("ROOT CAUSE:")
            lines.append(f"  {incident['root_cause']}")
            lines.append("")
        
        # Timeline events
        if incident.get('timeline'):
            lines.append("TIMELINE:")
            for event in incident['timeline']:
                lines.append(f"  • {event['time']}: {event['event']}")
            lines.append("")
        
        # Postmortem
        if incident.get('postmortem_url'):
            lines.append(f"POSTMORTEM: {incident['postmortem_url']}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _extract_teams(self) -> List[str]:
        """Extract and format team entities."""
        teams = self.data.get("teams", [])
        documents = []
        
        for team in teams:
            text = self._format_team(team)
            documents.append(text)
        
        logger.info(f"  ✓ Extracted {len(documents)} teams")
        return documents
    
    def _format_team(self, team: Dict[str, Any]) -> str:
        """Format a team entity as human-readable text."""
        lines = []
        
        # Header
        lines.append(f"═══════════════════════════════════════════════════════════════")
        lines.append(f"TEAM: {team['display_name']}")
        lines.append(f"═══════════════════════════════════════════════════════════════")
        lines.append("")
        
        # Basic info
        lines.append(f"Name: {team['name']}")
        lines.append(f"Lead: {team.get('lead', 'N/A')}")
        lines.append(f"Members: {team.get('members', 'N/A')}")
        lines.append(f"Slack Channel: {team.get('slack_channel', 'N/A')}")
        lines.append(f"On-Call Schedule: {team.get('oncall_schedule', 'N/A')}")
        lines.append("")
        
        # Services owned
        if team.get('services_owned'):
            lines.append(f"SERVICES OWNED: {', '.join(team['services_owned'])}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _extract_dependency_graph(self) -> List[str]:
        """Extract and format dependency graph as a document."""
        dep_graph = self.data.get("dependency_graph", {})
        
        if not dep_graph:
            return []
        
        lines = []
        
        # Header
        lines.append(f"═══════════════════════════════════════════════════════════════")
        lines.append(f"SYSTEM DEPENDENCY GRAPH")
        lines.append(f"═══════════════════════════════════════════════════════════════")
        lines.append("")
        
        # Nodes
        if dep_graph.get('nodes'):
            lines.append(f"TOTAL NODES: {len(dep_graph['nodes'])}")
            lines.append("")
            lines.append("ALL SYSTEM COMPONENTS:")
            for node in dep_graph['nodes']:
                lines.append(f"  • {node}")
            lines.append("")
        
        # Edges (dependencies)
        if dep_graph.get('edges'):
            lines.append(f"TOTAL DEPENDENCIES: {len(dep_graph['edges'])}")
            lines.append("")
            lines.append("DEPENDENCY RELATIONSHIPS:")
            for edge in dep_graph['edges']:
                from_node = edge['from']
                to_node = edge['to']
                dep_type = edge.get('type', 'unknown')
                arrow = "──sync──>" if dep_type == "sync" else "~~async~~>" if dep_type == "async" else "────>"
                lines.append(f"  {from_node} {arrow} {to_node}")
            lines.append("")
        
        logger.info(f"  ✓ Extracted dependency graph")
        return ["\n".join(lines)]
