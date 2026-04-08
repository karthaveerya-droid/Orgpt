"""
datadog_catalog_extractor.py
=============================

Provides access to:
  - Service catalog entities with relationships
  - Complex filters (owner, kind, name, ref)
  - Automatic pagination
  - Related entities (incidents, oncall, schemas)
  - Integration metadata (OpsGenie, PagerDuty, etc)


API Documentation: https://docs.datadoghq.com/api/latest/software-catalog/#get-a-list-of-entity-relations
"""

import logging
from typing import Dict, List, Any, Optional
from .datadog_client import DatadogAPIClient

logger = logging.getLogger(__name__)


class CatalogEntityExtractor:
    """
    Extracts service and application catalog entities from Datadog.
    
    This is more comprehensive than /api/v2/services because it includes:
    - Relaciones complejas (incidents, oncall, schemas, relatedEntities)
    - Metadata estructurada (owner, team, contacts, links)
    - Integración nativa (OpsGenie, PagerDuty)
    - Spec rico (lifecycle, tier, type, languages, dependencies)
    - Code locations y eventos asociados
    
    Example:
        extractor = CatalogEntityExtractor(client)
        services = extractor.extract_all_entities(kinds=["service"])
        payment_api = extractor.extract_entity_by_ref("service:payment-api")
        team_services = extractor.extract_entities_by_owner("platform-team")
    """
    
    API_ENDPOINT = "/api/v2/catalog/entity"
    DEFAULT_INCLUDES = "schema,oncall,relatedEntities"
    MAX_LIMIT = 100
    
    def __init__(self, client: DatadogAPIClient):
        """
        Initialize the catalog entity extractor.
        
        Args:
            client: DatadogAPIClient instance with valid credentials
        """
        self.client = client
        self.logger = logging.getLogger(__name__)
    
    def extract_all_entities(
        self,
        kinds: Optional[List[str]] = None,
        offset: int = 0,
        limit: int = 100,
        includes: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Extract catalog entities with optional filtering by kind.
        
        Args:
            kinds: Filter by entity kinds (e.g., ["service", "team", "application"])
            offset: Pagination offset (default: 0)
            limit: Items per page, max 100 (default: 100)
            includes: Comma-separated relationships to include
                     (schema, oncall, relatedEntities, incidents)
            
        Returns:
            List of entity dictionaries with attributes, relationships, metadata
            
        Raises:
            requests.HTTPError: On API errors
            
        Example:
            services = extractor.extract_all_entities(kinds=["service"])
            # Returns: [
            #   {
            #     "id": "...",
            #     "type": "service",
            #     "attributes": {...},
            #     "relationships": {...},
            #     "meta": {...}
            #   },
            #   ...
            # ]
        """
        if limit > self.MAX_LIMIT:
            logger.warning(f"Limit {limit} exceeds max {self.MAX_LIMIT}, using {self.MAX_LIMIT}")
            limit = self.MAX_LIMIT
        
        try:
            logger.info(f"Extracting catalog entities (offset={offset}, limit={limit})...")
            
            params = {
                "page[offset]": offset,
                "page[limit]": limit,
                "include": includes or self.DEFAULT_INCLUDES,
            }
            
            # Add kind filters if specified
            if kinds:
                for kind in kinds:
                    params[f"filter[kind]"] = kind
            
            response = self.client.get(self.API_ENDPOINT, params=params)
            
            entities = response.get("data", [])
            meta = response.get("meta", {})
            
            logger.info(
                f"✓ Extracted {len(entities)} entities "
                f"(total available: {meta.get('count', 'unknown')})"
            )
            
            return entities
            
        except Exception as e:
            logger.error(f"Error extracting catalog entities: {e}")
            return []
    
    def extract_entity_by_ref(
        self,
        ref: str,
        includes: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Extract a specific entity by reference.
        
        Args:
            ref: Entity reference in format "type:name"
                 Examples: "service:payment-api", "team:platform-team", "application:myapp"
            includes: Relationships to include
            
        Returns:
            Entity dictionary with all details, or None if not found
            
        Example:
            entity = extractor.extract_entity_by_ref("service:payment-api")
            # Returns: {
            #   "id": "...",
            #   "attributes": {
            #     "name": "payment-api",
            #     "displayName": "Payment API",
            #     "owner": "payment-team",
            #     ...
            #   },
            #   "relationships": {...}
            # }
        """
        try:
            logger.info(f"Extracting entity: {ref}")
            
            params = {
                "filter[ref]": ref,
                "include": includes or self.DEFAULT_INCLUDES,
            }
            
            response = self.client.get(self.API_ENDPOINT, params=params)
            
            entities = response.get("data", [])
            
            if not entities:
                logger.warning(f"Entity not found: {ref}")
                return None
            
            entity = entities[0]
            logger.info(
                f"✓ Found entity: {ref} "
                f"({entity.get('attributes', {}).get('displayName', 'Unknown')})"
            )
            
            return entity
            
        except Exception as e:
            logger.error(f"Error extracting entity {ref}: {e}")
            return None
    
    def extract_entity_by_id(
        self,
        entity_id: str,
        includes: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Extract a specific entity by internal ID.
        
        Args:
            entity_id: Internal entity ID
            includes: Relationships to include
            
        Returns:
            Entity dictionary or None
        """
        try:
            logger.info(f"Extracting entity by ID: {entity_id}")
            
            params = {
                "filter[id]": entity_id,
                "include": includes or self.DEFAULT_INCLUDES,
            }
            
            response = self.client.get(self.API_ENDPOINT, params=params)
            entities = response.get("data", [])
            
            if not entities:
                logger.warning(f"Entity not found by ID: {entity_id}")
                return None
            
            return entities[0]
            
        except Exception as e:
            logger.error(f"Error extracting entity by ID {entity_id}: {e}")
            return None
    
    def extract_entities_by_owner(
        self,
        owner: str,
        kinds: Optional[List[str]] = None,
        limit: int = 100,
        includes: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Extract all entities owned by a specific owner.
        
        Args:
            owner: Owner ID or name
            kinds: Optional filter by kinds
            limit: Items per page
            includes: Relationships to include
            
        Returns:
            List of entities owned by the specified owner
            
        Example:
            services = extractor.extract_entities_by_owner(
                "platform-team",
                kinds=["service"]
            )
        """
        try:
            logger.info(f"Extracting entities for owner: {owner}")
            
            params = {
                "filter[owner]": owner,
                "page[limit]": min(limit, self.MAX_LIMIT),
                "include": includes or self.DEFAULT_INCLUDES,
            }
            
            if kinds:
                for kind in kinds:
                    params[f"filter[kind]"] = kind
            
            response = self.client.get(self.API_ENDPOINT, params=params)
            entities = response.get("data", [])
            
            logger.info(f"✓ Found {len(entities)} entities for owner: {owner}")
            return entities
            
        except Exception as e:
            logger.error(f"Error extracting entities by owner {owner}: {e}")
            return []
    
    def extract_entities_by_name(
        self,
        name: str,
        kinds: Optional[List[str]] = None,
        includes: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Extract entities matching a name pattern.
        
        Args:
            name: Name to search for
            kinds: Optional filter by kinds
            includes: Relationships to include
            
        Returns:
            List of matching entities
        """
        try:
            logger.info(f"Extracting entities by name: {name}")
            
            params = {
                "filter[name]": name,
                "include": includes or self.DEFAULT_INCLUDES,
            }
            
            if kinds:
                for kind in kinds:
                    params[f"filter[kind]"] = kind
            
            response = self.client.get(self.API_ENDPOINT, params=params)
            entities = response.get("data", [])
            
            logger.info(f"✓ Found {len(entities)} entities matching: {name}")
            return entities
            
        except Exception as e:
            logger.error(f"Error extracting entities by name {name}: {e}")
            return []
    
    def extract_service_dependencies(
        self,
        service_ref: str,
        includes: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Extract entities that a service depends on (RelationTypeDependencyOf).
        
        Args:
            service_ref: Service reference (e.g., "service:payment-api")
            includes: Relationships to include
            
        Returns:
            List of dependencies
            
        Example:
            deps = extractor.extract_service_dependencies("service:payment-api")
            # Returns services that payment-api depends on
        """
        try:
            logger.info(f"Extracting dependencies for: {service_ref}")
            
            params = {
                "filter[relation][type]": "RelationTypeDependencyOf",
                "filter[ref]": service_ref,
                "include": includes or "relatedEntities",
            }
            
            response = self.client.get(self.API_ENDPOINT, params=params)
            entities = response.get("data", [])
            
            logger.info(f"✓ Found {len(entities)} dependencies for: {service_ref}")
            return entities
            
        except Exception as e:
            logger.error(f"Error extracting dependencies for {service_ref}: {e}")
            return []
    
    def extract_service_dependents(
        self,
        service_ref: str,
        includes: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Extract entities that depend on a given service (RelationTypeDependentOf).
        
        Args:
            service_ref: Service reference
            includes: Relationships to include
            
        Returns:
            List of dependent services
        """
        try:
            logger.info(f"Extracting dependents for: {service_ref}")
            
            params = {
                "filter[relation][type]": "RelationTypeDependentOf",
                "filter[ref]": service_ref,
                "include": includes or "relatedEntities",
            }
            
            response = self.client.get(self.API_ENDPOINT, params=params)
            entities = response.get("data", [])
            
            logger.info(f"✓ Found {len(entities)} dependents for: {service_ref}")
            return entities
            
        except Exception as e:
            logger.error(f"Error extracting dependents for {service_ref}: {e}")
            return []
    
    def extract_paginated_entities(
        self,
        kinds: Optional[List[str]] = None,
        limit: int = 100,
        max_pages: Optional[int] = None,
        includes: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Extract all entities with automatic pagination.
        
        Handles pagination automatically, fetching all pages until completion
        or max_pages is reached.
        
        Args:
            kinds: Filter by kinds
            limit: Items per page (max 100)
            max_pages: Stop after N pages (None = all pages)
            includes: Relationships to include
            
        Returns:
            All entities across all pages
            
        Example:
            all_services = extractor.extract_paginated_entities(
                kinds=["service"],
                limit=100,
                max_pages=None  # Get all
            )
        """
        all_entities = []
        offset = 0
        page_count = 0
        
        try:
            while True:
                if max_pages and page_count >= max_pages:
                    logger.info(f"Reached max_pages limit: {max_pages}")
                    break
                
                entities = self.extract_all_entities(
                    kinds=kinds,
                    offset=offset,
                    limit=limit,
                    includes=includes,
                )
                
                if not entities:
                    logger.info("No more entities to fetch")
                    break
                
                all_entities.extend(entities)
                offset += limit
                page_count += 1
                
                logger.debug(
                    f"Fetched {len(entities)} entities in page {page_count}, "
                    f"total so far: {len(all_entities)}"
                )
            
            logger.info(
                f"✓ Total entities extracted: {len(all_entities)} ({page_count} pages)"
            )
            return all_entities
            
        except Exception as e:
            logger.error(f"Error during paginated extraction: {e}")
            return all_entities  # Return partial results
    
    def extract_entities_by_tag(
        self,
        tag_key: str,
        tag_value: Optional[str] = None,
        kinds: Optional[List[str]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Extract entities matching a specific tag.
        
        Args:
            tag_key: Tag key (e.g., "team")
            tag_value: Tag value (e.g., "platform"), if None matches any value
            kinds: Optional filter by kinds
            
        Returns:
            List of matching entities
            
        Note: This is a post-filter since the API might not support tag filters
        """
        try:
            logger.info(f"Extracting entities with tag: {tag_key}={tag_value}")
            
            # Fetch entities (might need to fetch all and filter)
            all_entities = self.extract_paginated_entities(
                kinds=kinds,
                limit=100,
                max_pages=None,
            )
            
            # Filter by tag
            filtered = []
            for entity in all_entities:
                tags = entity.get("attributes", {}).get("tags", [])
                for tag in tags:
                    if tag_key in tag:
                        if tag_value is None or tag_value in tag:
                            filtered.append(entity)
                            break
            
            logger.info(f"✓ Found {len(filtered)} entities with tag: {tag_key}={tag_value}")
            return filtered
            
        except Exception as e:
            logger.error(f"Error extracting entities by tag: {e}")
            return []
    
    def get_entity_relationships(
        self,
        entity: Dict[str, Any],
        relationship_type: Optional[str] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract relationships from an entity.
        
        Args:
            entity: Entity dictionary (from extract_* methods)
            relationship_type: Specific relationship to extract
                              (incidents, oncall, schema, relatedEntities)
                              If None, returns all
            
        Returns:
            Dictionary mapping relationship types to their data
            
        Example:
            entity = extractor.extract_entity_by_ref("service:payment-api")
            rels = extractor.get_entity_relationships(entity)
            # Returns: {
            #   "incidents": [...],
            #   "oncall": [...],
            #   "relatedEntities": [...],
            #   "schema": {...}
            # }
        """
        try:
            relationships = entity.get("relationships", {})
            
            if relationship_type:
                return {
                    relationship_type: relationships.get(
                        relationship_type, {}
                    ).get("data", [])
                }
            
            result = {}
            for rel_type, rel_data in relationships.items():
                if isinstance(rel_data, dict) and "data" in rel_data:
                    result[rel_type] = rel_data["data"]
                else:
                    result[rel_type] = rel_data
            
            return result
            
        except Exception as e:
            logger.error(f"Error extracting relationships: {e}")
            return {}
    
    def get_entity_schema(
        self,
        entity: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """
        Extract schema details from an entity.
        
        Args:
            entity: Entity dictionary
            
        Returns:
            Schema dictionary with metadata, datadog config, integrations, spec
        """
        try:
            relationships = entity.get("relationships", {})
            schema_ref = relationships.get("schema", {}).get("data", {})
            
            if not schema_ref:
                return None
            
            schema_id = schema_ref.get("id")
            logger.debug(f"Entity has schema: {schema_id}")
            
            # Schema data would be in the 'included' section of the full response
            # This method is mainly for reference/documentation
            return schema_ref
            
        except Exception as e:
            logger.error(f"Error extracting schema: {e}")
            return None
