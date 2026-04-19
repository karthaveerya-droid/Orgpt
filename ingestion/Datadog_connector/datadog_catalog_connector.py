"""
datadog_catalog_connector.py
============================
Datadog Catalog Entity connector implementing DataSourceConnector interface.

This connector extracts service catalog data from Datadog and transforms
it into RAG-ready documents following the Strategy Pattern.

SOLID Principles:
- SRP: Only responsible for Datadog Catalog extraction
- OCP: Can be extended without modification
- LSP: Can substitute any DataSourceConnector
- ISP: Implements minimal required interface
- DIP: Depends on DataSourceConnector abstraction
"""

import sys
import os
import logging
from typing import List, Dict, Any, Optional

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ingestion.base_connector import DataSourceConnector
from ingestion.Datadog_connector.datadog_connector import DatadogConnector

logger = logging.getLogger(__name__)


class DatadogCatalogConnector(DataSourceConnector):
    """
    Datadog Service Catalog connector.
    
    Extracts service catalog entities from Datadog API or JSON files
    and transforms them into RAG-ready markdown documents.
    
    Modes:
    - API mode: Connects to Datadog API (requires DD_API_KEY, DD_APP_KEY)
    - POC mode: Loads from JSON file (no API keys needed)
    
    Usage:
        # API mode
        connector = DatadogCatalogConnector()
        docs = connector.extract_documents()
        
        # POC mode
        connector = DatadogCatalogConnector(
            poc_mode=True,
            json_file="sample_get_entities_list.json"
        )
        docs = connector.extract_documents()
    """
    
    def __init__(
        self,
        poc_mode: bool = False,
        json_file: Optional[str] = None,
        kinds: Optional[List[str]] = None,
        max_pages: Optional[int] = None
    ):
        """
        Initialize Datadog Catalog connector.
        
        Args:
            poc_mode: If True, use JSON file instead of API
            json_file: Path to JSON file (for POC mode)
            kinds: List of entity kinds to extract (e.g., ['service'])
            max_pages: Maximum pages to fetch from API
        """
        self.poc_mode = poc_mode
        self.json_file = json_file or "sample_get_entities_list.json"
        self.kinds = kinds
        self.max_pages = max_pages
        
        # Initialize internal Datadog connector
        self._connector = DatadogConnector(poc_mode=poc_mode)
        
        self._stats = {
            "entity_count": 0,
            "document_count": 0,
            "mode": "poc" if poc_mode else "api",
        }
    
    def extract_documents(self) -> List[str]:
        """
        Extract and transform Datadog catalog entities to documents.
        
        Returns:
            List of markdown-formatted text documents
        """
        try:
            # Extract entities
            if self.poc_mode:
                logger.info(f"Extracting catalog entities from JSON: {self.json_file}")
                entities = self._connector.extract_catalog_entities_from_json(self.json_file)
            else:
                logger.info("Extracting catalog entities from Datadog API...")
                entities = self._connector.extract_catalog_entities(
                    kinds=self.kinds,
                    max_pages=self.max_pages
                )
            
            if not entities:
                logger.warning("No catalog entities extracted")
                return []
            
            self._stats["entity_count"] = len(entities)
            logger.info(f"✓ Extracted {len(entities)} catalog entities")
            
            # Transform to documents
            # Note: In POC mode, extract_catalog_entities_from_json already returns transformed docs
            if self.poc_mode:
                docs = entities  # Already transformed
            else:
                logger.info("Transforming entities to documents...")
                docs = self._connector.catalog_transformer.transform_entities_batch(entities)
            
            self._stats["document_count"] = len(docs)
            logger.info(f"✓ Transformed to {len(docs)} documents")
            
            return docs
            
        except Exception as e:
            logger.error(f"Failed to extract Datadog catalog entities: {e}", exc_info=True)
            raise
    
    def get_source_name(self) -> str:
        """Get source identifier."""
        return "datadog_catalog"
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get connector metadata."""
        base = super().get_metadata()
        base.update({
            "mode": self._stats["mode"],
            "entity_count": self._stats["entity_count"],
            "kinds": self.kinds if self.kinds else "all",
        })
        if self.poc_mode:
            base["json_file"] = self.json_file
        return base
    
    def get_stats(self) -> Dict[str, Any]:
        """Get extraction statistics."""
        return {
            **super().get_stats(),
            **self._stats,
        }
