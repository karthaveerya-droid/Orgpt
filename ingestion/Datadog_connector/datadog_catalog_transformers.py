"""
datadog_catalog_transformers.py
================================
Transform Datadog Catalog Entity responses to RAG-optimized documents.

This module converts raw JSON from the Catalog Entity API into
Markdown-formatted documents optimized for:
  - SentenceTransformer embeddings
  - RAG queries
  - Natural language understanding
  - Knowledge graph integration
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class CatalogEntityTransformer:
    """Transform catalog entities to RAG-optimized markdown documents."""
    
    def __init__(self):
        pass
    
    def transform_entity(
        self,
        entity: Dict[str, Any],
        include_relationships: bool = True,
    ) -> str:
        """
        Transform a single catalog entity to markdown.
        
        Args:
            entity: Entity dictionary from API
            include_relationships: Whether to include relationship sections
            
        Returns:
            Markdown-formatted string optimized for RAG
        """
        try:
            attributes = entity.get("attributes", {})
            meta = entity.get("meta", {})
            relationships = entity.get("relationships", {})
            
            name = attributes.get("name", "Unknown")
            display_name = attributes.get("displayName", name)
            kind = attributes.get("kind", "unknown")
            description = attributes.get("description", "")
            owner = attributes.get("owner", "")
            namespace = attributes.get("namespace", "")
            tags = attributes.get("tags", [])
            
            # Build document
            sections = []
            
            # Header
            sections.append(f"# {display_name}")
            if kind:
                sections.append(f"**Type**: {kind}")
            
            # Basic info
            sections.append("")
            sections.append("## Service Details")
            sections.append(f"**Name**: {name}")
            if display_name != name:
                sections.append(f"**Display Name**: {display_name}")
            if namespace:
                sections.append(f"**Namespace**: {namespace}")
            if owner:
                sections.append(f"**Owner**: {owner}")
            if tags:
                sections.append(f"**Tags**: {', '.join(tags)}")
            
            # Description
            if description:
                sections.append("")
                sections.append("## Description")
                sections.append(description)
            
            # Metadata
            created_at = meta.get("createdAt", "")
            modified_at = meta.get("modifiedAt", "")
            if created_at or modified_at:
                sections.append("")
                sections.append("## Metadata")
                if created_at:
                    sections.append(f"**Created**: {created_at}")
                if modified_at:
                    sections.append(f"**Last Modified**: {modified_at}")
            
            # Relationships
            if include_relationships and relationships:
                sections.extend(
                    self._format_relationships(name, relationships)
                )
            
            return "\n".join(sections)
            
        except Exception as e:
            logger.error(f"Error transforming entity: {e}")
            return ""
    
    def _format_relationships(
        self,
        entity_name: str,
        relationships: Dict[str, Any]
    ) -> List[str]:
        """Format relationships section."""
        sections = []
        sections.append("")
        sections.append("## Relationships")
        
        if "incidents" in relationships:
            incidents = relationships.get("incidents", {}).get("data", [])
            sections.append(f"**Incidents**: {len(incidents)} related incidents")
            if incidents:
                for incident in incidents[:5]:  # Show first 5
                    sections.append(f"  - {incident.get('id', 'unknown')}")
                if len(incidents) > 5:
                    sections.append(f"  - ... and {len(incidents) - 5} more")
        
        if "oncall" in relationships:
            oncall = relationships.get("oncall", {}).get("data", [])
            sections.append(f"**Oncall**: {len(oncall)} schedules")
            if oncall:
                for schedule in oncall[:3]:
                    sections.append(f"  - {schedule.get('id', 'unknown')}")
        
        if "relatedEntities" in relationships:
            related = relationships.get("relatedEntities", {}).get("data", [])
            sections.append(f"**Related Services**: {len(related)} related")
            if related:
                for entity in related[:5]:
                    entity_id = entity.get('id', 'unknown')
                    sections.append(f"  - {entity_id}")
                if len(related) > 5:
                    sections.append(f"  - ... and {len(related) - 5} more")
        
        return sections
    
    def transform_entity_with_schema(
        self,
        entity: Dict[str, Any],
        schema_data: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Transform entity with detailed schema information.
        
        Args:
            entity: Entity from API
            schema_data: Schema from 'included' array (optional)
            
        Returns:
            Comprehensive markdown document
        """
        try:
            # Base entity transformation
            doc_lines = [self.transform_entity(entity, include_relationships=True)]
            
            # Add schema details if available
            if schema_data:
                doc_lines.append("")
                doc_lines.append("## Service Architecture")
                doc_lines.extend(
                    self._format_schema_details(schema_data)
                )
            
            return "\n".join(doc_lines)
            
        except Exception as e:
            logger.error(f"Error transforming entity with schema: {e}")
            return self.transform_entity(entity)
    
    def _format_schema_details(
        self,
        schema: Dict[str, Any]
    ) -> List[str]:
        """Format detailed schema information."""
        sections = []
        
        schema_obj = schema.get("attributes", {}).get("schema", {})
        metadata = schema_obj.get("metadata", {})
        datadog_config = schema_obj.get("datadog", {})
        integrations = schema_obj.get("integrations", {})
        spec = schema_obj.get("spec", {})
        
        # Ownership and Contacts
        sections.append("### Ownership")
        additional_owners = metadata.get("additionalOwners", [])
        if additional_owners:
            sections.append("**Additional Owners**:")
            for owner in additional_owners:
                owner_type = owner.get("type", "unknown")
                sections.append(f"  - {owner.get('name', 'Unknown')} ({owner_type})")
        
        contacts = metadata.get("contacts", [])
        if contacts:
            sections.append("**Contacts**:")
            for contact in contacts:
                contact_type = contact.get("type", "unknown")
                contact_name = contact.get("name", "")
                contact_value = contact.get("contact", "")
                sections.append(f"  - {contact_type}: {contact_name} ({contact_value})")
        
        # Documentation Links
        links = metadata.get("links", [])
        if links:
            sections.append("")
            sections.append("### Documentation")
            for link in links:
                link_name = link.get("name", "Link")
                link_url = link.get("url", "")
                sections.append(f"  - [{link_name}]({link_url})")
        
        # Code Locations
        if datadog_config:
            code_locations = datadog_config.get("codeLocations", [])
            if code_locations:
                sections.append("")
                sections.append("### Code Locations")
                for location in code_locations:
                    repo_url = location.get("repositoryURL", "")
                    paths = location.get("paths", [])
                    sections.append(f"  - Repository: {repo_url}")
                    if paths:
                        for path in paths:
                            sections.append(f"    - {path}")
            
            # Events
            events = datadog_config.get("events", [])
            if events:
                sections.append("")
                sections.append("### Events")
                for event in events:
                    event_name = event.get("name", "")
                    sections.append(f"  - {event_name}")
            
            # Logs
            logs = datadog_config.get("logs", [])
            if logs:
                sections.append("")
                sections.append("### Logs")
                for log in logs:
                    log_name = log.get("name", "")
                    sections.append(f"  - {log_name}")
            
            # Performance tags
            perf_data = datadog_config.get("performanceData", {})
            perf_tags = perf_data.get("tags", [])
            if perf_tags:
                sections.append("")
                sections.append("### Performance Tags")
                for tag in perf_tags:
                    sections.append(f"  - {tag}")
        
        # Integrations
        if integrations:
            sections.append("")
            sections.append("### Integrations")
            
            if "opsgenie" in integrations:
                opsgenie = integrations["opsgenie"]
                sections.append("**OpsGenie**:")
                if opsgenie.get("serviceURL"):
                    sections.append(f"  - URL: {opsgenie.get('serviceURL')}")
                if opsgenie.get("region"):
                    sections.append(f"  - Region: {opsgenie.get('region')}")
            
            if "pagerduty" in integrations:
                pagerduty = integrations["pagerduty"]
                sections.append("**PagerDuty**:")
                if pagerduty.get("serviceURL"):
                    sections.append(f"  - URL: {pagerduty.get('serviceURL')}")
        
        # Service Spec
        if spec:
            sections.append("")
            sections.append("### Service Specification")
            
            lifecycle = spec.get("lifecycle")
            if lifecycle:
                sections.append(f"**Lifecycle**: {lifecycle}")
            
            tier = spec.get("tier")
            if tier:
                sections.append(f"**Tier**: {tier}")
            
            service_type = spec.get("type")
            if service_type:
                sections.append(f"**Type**: {service_type}")
            
            languages = spec.get("languages", [])
            if languages:
                sections.append(f"**Languages**: {', '.join(languages)}")
            
            # Dependencies
            depends_on = spec.get("dependsOn", [])
            if depends_on:
                sections.append("")
                sections.append("**Depends On**:")
                for dep in depends_on:
                    sections.append(f"  - {dep}")
            
            component_of = spec.get("componentOf", [])
            if component_of:
                sections.append("")
                sections.append("**Component Of**:")
                for component in component_of:
                    sections.append(f"  - {component}")
        
        return sections
    
    def transform_entities_batch(
        self,
        entities: List[Dict[str, Any]],
        max_docs: Optional[int] = None,
    ) -> List[str]:
        """
        Transform multiple entities to individual documents.
        
        Args:
            entities: List of entities
            max_docs: Limit number of documents (None = all)
            
        Returns:
            List of markdown documents
        """
        docs = []
        
        for i, entity in enumerate(entities):
            if max_docs and i >= max_docs:
                break
            
            try:
                doc = self.transform_entity(entity)
                if doc:
                    docs.append(doc)
            except Exception as e:
                logger.error(f"Error transforming entity {i}: {e}")
        
        logger.info(f"✓ Transformed {len(docs)} entities to documents")
        return docs
    
    def transform_dependency_graph(
        self,
        service_name: str,
        depends_on: List[Dict[str, Any]],
        dependents: List[Dict[str, Any]],
    ) -> str:
        """
        Create a dependency graph document for a service.
        
        Args:
            service_name: Central service name
            depends_on: Services this one depends on
            dependents: Services that depend on this one
            
        Returns:
            Formatted dependency document
        """
        sections = []
        
        sections.append(f"# Dependency Graph: {service_name}")
        sections.append("")
        
        # Upstream dependencies
        sections.append("## Services This Depends On (Upstream)")
        if depends_on:
            for dep in depends_on:
                dep_name = dep.get("attributes", {}).get("name", "unknown")
                sections.append(f"- {dep_name}")
        else:
            sections.append("- None (This is a foundational service)")
        
        # Downstream dependents
        sections.append("")
        sections.append("## Services That Depend On This (Downstream)")
        if dependents:
            for dep in dependents:
                dep_name = dep.get("attributes", {}).get("name", "unknown")
                sections.append(f"- {dep_name}")
        else:
            sections.append("- None (No services depend on this)")
        
        # Summary
        sections.append("")
        sections.append("## Summary")
        sections.append(f"- **Total Dependencies**: {len(depends_on)}")
        sections.append(f"- **Total Dependents**: {len(dependents)}")
        sections.append(f"- **Total Related**: {len(depends_on) + len(dependents)}")
        
        return "\n".join(sections)
    
    def create_consolidated_catalog_doc(
        self,
        service_name: str,
        entity: Dict[str, Any],
        dependencies: Optional[List[Dict[str, Any]]] = None,
        dependents: Optional[List[Dict[str, Any]]] = None,
        schema_data: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create a comprehensive service profile document.
        
        Combines entity info, schema, and dependencies into one RAG document.
        
        Args:
            service_name: Service name
            entity: Main entity dict
            dependencies: Services this depends on
            dependents: Services depending on this
            schema_data: Schema details
            
        Returns:
            Consolidated markdown document
        """
        sections = []
        
        # Main entity with schema
        sections.append(self.transform_entity_with_schema(entity, schema_data))
        
        # Dependencies
        if dependencies or dependents:
            sections.append("")
            sections.append(self.transform_dependency_graph(
                service_name,
                dependencies or [],
                dependents or []
            ))
        
        return "\n".join(sections)
