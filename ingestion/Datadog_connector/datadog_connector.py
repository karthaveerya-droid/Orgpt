"""
datadog_connector.py
====================
Main orchestrator for Datadog Catalog Entity integration into OrgGPT.

This module coordinates:
  1. Datadog API client initialization
  2. Data extraction from Catalog Entity API
  3. Transformation to RAG-ready documents
  4. Vector store ingestion

Architecture:
  - Client: Handles HTTP communication
  - Extractors: Fetch data from Datadog APIs
  - Transformers: Convert to text format
  - Connector: Orchestrates the flow

Data Sources:
  - /api/v2/catalog/entity ✨ (CatalogEntityExtractor + CatalogEntityTransformer)
  - /api/v1/slo ✨ (SLOExtractor + SLOTransformer)
"""

import os
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from .datadog_client import DatadogAPIClient, DatadogClientConfig

# ✨ CATALOG ENTITY IMPORTS
try:
    from .datadog_catalog_extractor import CatalogEntityExtractor
    from .datadog_catalog_transformers import CatalogEntityTransformer
    CATALOG_ENTITIES_AVAILABLE = True
except ImportError:
    CATALOG_ENTITIES_AVAILABLE = False
    logger_temp = logging.getLogger(__name__)
    logger_temp.warning("CatalogEntityExtractor or CatalogEntityTransformer not found. Catalog Entity extraction disabled.")

# ✨ SLO IMPORTS
try:
    from .datadog_slo_extractor import SLOExtractor
    from .datadog_slo_transformer import SLOTransformer
    SLO_AVAILABLE = True
except ImportError:
    SLO_AVAILABLE = False
    logger_temp = logging.getLogger(__name__)
    logger_temp.warning("SLOExtractor or SLOTransformer not found. SLO extraction disabled.")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatadogConnector:
    """
    Main connector for Datadog API integration.
    
    Supports:
    - Catalog Entity API (/api/v2/catalog/entity) ✨
    - SLO API (/api/v1/slo) ✨
    
    Follows Open/Closed Principle:
      - Closed for modification (stable core)
      - Open for extension (new extractors/transformers)
    
    Usage:
        # Catalog Entities
        connector = DatadogConnector()
        entities = connector.extract_catalog_entities()
        docs = connector.catalog_transformer.transform_entities_batch(entities)
        
        # SLOs
        slos = connector.extract_slos()
        slo_docs = connector.slo_transformer.transform_slos_batch(slos)
    """
    
    def __init__(self, config: Optional[DatadogClientConfig] = None, poc_mode: bool = False):
        """
        Initialize Datadog connector.
        
        Args:
            config: DatadogClientConfig instance. If None, creates default from env vars.
            poc_mode: If True, skip API client initialization (for JSON-only usage)
        """
        self.poc_mode = poc_mode
        
        if not poc_mode:
            self.config = config or DatadogClientConfig()
            self.client = DatadogAPIClient(self.config)
        else:
            # POC mode: no API client needed
            self.config = None
            self.client = None
            logger.info("🎯 POC mode enabled - API client skipped")
        
        # ✨ Initialize Catalog Entity extractor and transformer
        if CATALOG_ENTITIES_AVAILABLE:
            if not poc_mode:
                self.catalog_extractor = CatalogEntityExtractor(self.client)
            else:
                self.catalog_extractor = None  # Not needed for POC
            self.catalog_transformer = CatalogEntityTransformer()
            logger.info("✓ Catalog Entity transformer initialized")
        else:
            self.catalog_extractor = None
            self.catalog_transformer = None
            logger.warning("⚠️  Catalog Entity support disabled - modules not found")
        
        # ✨ Initialize SLO extractor and transformer
        if SLO_AVAILABLE:
            if not poc_mode:
                self.slo_extractor = SLOExtractor(self.client)
            else:
                self.slo_extractor = None  # Not needed for POC
            self.slo_transformer = SLOTransformer()
            logger.info("✓ SLO transformer initialized")
        else:
            self.slo_extractor = None
            self.slo_transformer = None
            logger.warning("⚠️  SLO support disabled - modules not found")
        
        # Cache for extracted data
        self._cache: Dict[str, Any] = {}
        self._last_sync: Optional[datetime] = None
    
    # ✨ NEW METHOD
    def extract_catalog_entities(
        self,
        kinds: Optional[List[str]] = None,
        limit: int = 100,
        max_pages: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract Catalog Entities from /api/v2/catalog/entity endpoint.
        
        Args:
            kinds: List of entity kinds to extract (e.g., ['service']). If None, gets all.
            limit: Items per page (max 100)
            max_pages: Maximum pages to fetch. If None, fetches all.
            
        Returns:
            List of catalog entity dictionaries
            
        Raises:
            RuntimeError: If Catalog Entity support is not available
            
        Example:
            entities = connector.extract_catalog_entities(kinds=['service'], max_pages=5)
            docs = connector.catalog_transformer.transform_entities_batch(entities)
        """
        if not CATALOG_ENTITIES_AVAILABLE:
            raise RuntimeError(
                "Catalog Entity extraction not available. "
                "Ensure datadog_catalog_extractor.py and datadog_catalog_transformers.py exist."
            )
        
        if not self.catalog_extractor:
            raise RuntimeError("Catalog Entity extractor not initialized")
        
        try:
            logger.info("🔄 Extracting Catalog Entities...")
            entities = self.catalog_extractor.extract_paginated_entities(
                kinds=kinds or ["service"],
                limit=limit,
                max_pages=max_pages
            )
            
            # Cache result
            self._cache["catalog_entities"] = entities
            self._last_sync = datetime.now()
            
            logger.info(f"✓ Successfully extracted {len(entities)} catalog entities")
            return entities
            
        except Exception as e:
            logger.error(f"✗ Error extracting catalog entities: {e}")
            raise
    
    # ✨ NEW METHODS FOR SLO
    def extract_slos(
        self,
        query: Optional[str] = None,
        tags_query: Optional[str] = None,
        limit: int = 100,
        max_pages: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        Extract Service Level Objectives (SLOs) from /api/v1/slo endpoint.
        
        Args:
            query: Filter by SLO name (e.g., "availability")
            tags_query: Filter by tags (e.g., "env:prod,team:platform")
            limit: Items per page (max 1000)
            max_pages: Maximum pages to fetch. If None, fetches all.
            
        Returns:
            List of SLO dictionaries
            
        Raises:
            RuntimeError: If SLO support is not available
            
        Example:
            slos = connector.extract_slos(tags_query="env:prod", max_pages=5)
            docs = connector.slo_transformer.transform_slos_batch(slos)
        """
        if not SLO_AVAILABLE:
            raise RuntimeError(
                "SLO extraction not available. "
                "Ensure datadog_slo_extractor.py and datadog_slo_transformer.py exist."
            )
        
        if not self.slo_extractor:
            raise RuntimeError("SLO extractor not initialized")
        
        try:
            logger.info("🔄 Extracting SLOs...")
            
            if max_pages:
                slos = []
                offset = 0
                for page in range(max_pages):
                    page_slos = self.slo_extractor.extract_all_slos(
                        offset=offset,
                        limit=limit,
                        query=query,
                        tags_query=tags_query,
                    )
                    
                    if not page_slos:
                        break
                    
                    slos.extend(page_slos)
                    
                    if len(page_slos) < limit:
                        break
                    
                    offset += limit
            else:
                slos = self.slo_extractor.extract_all_paginated(
                    query=query,
                    tags_query=tags_query,
                )
            
            # Cache result
            self._cache["slos"] = slos
            self._last_sync = datetime.now()
            
            logger.info(f"✓ Successfully extracted {len(slos)} SLOs")
            return slos
            
        except Exception as e:
            logger.error(f"✗ Error extracting SLOs: {e}")
            raise
    
    def extract_slo_corrections(
        self,
        slo_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """
        Extract SLO corrections (maintenance windows).
        
        Args:
            slo_id: Optional SLO ID to filter corrections
            limit: Items per page (max 1000)
            
        Returns:
            List of correction dictionaries
            
        Example:
            corrections = connector.extract_slo_corrections(slo_id="abc123")
            docs = connector.slo_transformer.transform_corrections_batch(corrections)
        """
        if not SLO_AVAILABLE:
            raise RuntimeError("SLO extraction not available")
        
        if not self.slo_extractor:
            raise RuntimeError("SLO extractor not initialized")
        
        try:
            logger.info(f"🔄 Extracting SLO corrections (slo_id={slo_id or 'all'})...")
            
            corrections = self.slo_extractor.extract_slo_corrections(
                slo_id=slo_id,
                limit=limit,
            )
            
            # Cache result
            cache_key = f"corrections_{slo_id or 'all'}"
            self._cache[cache_key] = corrections
            
            logger.info(f"✓ Successfully extracted {len(corrections)} corrections")
            return corrections
            
        except Exception as e:
            logger.error(f"✗ Error extracting SLO corrections: {e}")
            raise
    
    def extract_slos_from_json(self, json_file_path: str) -> List[Dict[str, Any]]:
        """
        Extract SLOs from a local JSON file (POC mode).
        
        This method allows loading SLOs from a sample JSON file without requiring
        API credentials. Useful for demonstrations and testing.
        
        Args:
            json_file_path: Path to JSON file containing Datadog SLOs
                           Expected format: {"data": [slo1, slo2, ...]}
        
        Returns:
            List of SLO dictionaries ready for transformation
        
        Example:
            >>> connector = DatadogConnector(poc_mode=True)
            >>> slos = connector.extract_slos_from_json("sample_get_slo_list.json")
            >>> docs = connector.slo_transformer.transform_slos_batch(slos)
        """
        if not SLO_AVAILABLE:
            raise RuntimeError(
                "SLO transformation not available. "
                "Ensure datadog_slo_transformer.py exists."
            )
        
        logger.info(f"📂 Loading Datadog SLOs from JSON file: {json_file_path}")
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract SLOs from the 'data' field (Datadog API format)
            slos = data.get('data', [])
            
            if not slos:
                logger.warning(f"No SLOs found in {json_file_path}")
                return []
            
            logger.info(f"✅ Loaded {len(slos)} SLOs from JSON file")
            
            # Cache result
            self._cache["slos_from_json"] = slos
            self._last_sync = datetime.now()
            
            return slos
            
        except FileNotFoundError:
            logger.error(f"❌ JSON file not found: {json_file_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON format in {json_file_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Error loading SLOs from JSON: {e}", exc_info=True)
            raise
    
    def get_cache(self) -> Dict[str, Any]:
        """Get the internal cache of extracted data."""
        return self._cache
    
    def get_last_sync_time(self) -> Optional[datetime]:
        """Get timestamp of last successful data extraction."""
        return self._last_sync
    
    def close(self):
        """Clean up resources."""
        self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def extract_catalog_entities_from_json(self, json_file_path: str) -> List[Dict[str, Any]]:
        """
        Extract catalog entities from a local JSON file (POC mode).
        
        This method allows loading entities from a sample JSON file without requiring
        API credentials. Useful for demonstrations and testing.
        
        Args:
            json_file_path: Path to JSON file containing Datadog entities
                           Expected format: {"data": [entity1, entity2, ...]}
        
        Returns:
            List of catalog entity dictionaries ready for transformation
        
        Example:
            >>> connector = DatadogConnector(config)
            >>> entities = connector.extract_catalog_entities_from_json("sample_get_entities_list.json")
        """
        logger.info(f"📂 Loading Datadog entities from JSON file: {json_file_path}")
        
        try:
            with open(json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract entities from the 'data' field (Datadog API format)
            entities = data.get('data', [])
            
            if not entities:
                logger.warning(f"No entities found in {json_file_path}")
                return []
            
            logger.info(f"✅ Loaded {len(entities)} entities from JSON file")
            
            # Transform entities using the same transformer as API data
            transformed_entities = []
            for entity in entities:
                try:
                    transformed = self.catalog_transformer.transform_entity(entity)
                    transformed_entities.append(transformed)
                except Exception as e:
                    logger.error(f"Error transforming entity: {e}")
                    continue
            
            logger.info(f"✅ Transformed {len(transformed_entities)} entities successfully")
            return transformed_entities
            
        except FileNotFoundError:
            logger.error(f"❌ JSON file not found: {json_file_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"❌ Invalid JSON format in {json_file_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ Error loading entities from JSON: {e}", exc_info=True)
            raise


# Convenience function for direct ingestion
def extract_datadog_data(
    api_key: Optional[str] = None,
    app_key: Optional[str] = None,
    kinds: Optional[List[str]] = None,
    max_pages: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """
    Extract Datadog Catalog Entities in a single call.
    
    This is a convenience wrapper around DatadogConnector for simpler usage.
    
    Args:
        api_key: Datadog API key (uses DD_API_KEY env var if not provided)
        app_key: Datadog Application key (uses DD_APP_KEY env var if not provided)
        kinds: List of entity kinds to extract (e.g., ['service', 'team'])
        max_pages: Maximum pages to fetch. If None, fetches all.
    
    Returns:
        List of catalog entity dictionaries ready for transformation to documents
    
    Example:
        >>> entities = extract_datadog_data()
        >>> # entities is now a list of Catalog Entity objects
    """
    config = DatadogClientConfig(api_key=api_key, app_key=app_key)
    
    with DatadogConnector(config) as connector:
        return connector.extract_catalog_entities(
            kinds=kinds or ["service"],
            max_pages=max_pages
        )


if __name__ == "__main__":
    # POC Testing
    try:
        entities = extract_datadog_data(kinds=["service"], max_pages=2)
        
        print("\n" + "=" * 80)
        print("Sample Extracted Catalog Entities:")
        print("=" * 80)
        print(f"Total entities: {len(entities)}")
        
        for i, entity in enumerate(entities[:3]):
            print(f"\n--- Entity {i+1} ---")
            print(json.dumps(entity, indent=2)[:500])
            print("...")
    
    except Exception as e:
        logger.error(f"POC test failed: {e}", exc_info=True)
