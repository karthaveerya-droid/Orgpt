"""
swagger_connector.py
---------------------
Upgraded ingestion for Orgpt.
Fetches multiple Swagger/OpenAPI sources and returns a single list of flattened text docs.
Drop-in compatible with main.py expecting: docs = extract_text_from_swagger(...)
"""

import sys
import os
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ingestion.base_connector import DataSourceConnector
from ingestion.Swagger_connector.swagger_connector_helpers import (
    fetch_swagger,
    extract_full_api_spec,
    render_api_to_text,
)
import logging

logger = logging.getLogger(__name__)

class SwaggerConnector(DataSourceConnector):
    DEFAULT_SOURCES = {
        "Petstore": "https://petstore.swagger.io/v2/swagger.json",
        "Weather.gov": "https://api.weather.gov/openapi.json",
        "Swagger.io Generator": "https://generator.swagger.io/api/swagger.json",
    }
    
    def __init__(self, sources: Dict[str, str] = None):
        """
        Initialize Swagger connector.
        
        Args:
            sources: Dictionary of {name: url} for Swagger sources
                    If None, uses DEFAULT_SOURCES
        """
        self.sources = sources if sources is not None else self.DEFAULT_SOURCES
        self._stats = {
            "total_endpoints": 0,
            "successful_sources": 0,
            "failed_sources": 0,
        }
    
    def extract_documents(self) -> List[str]:
        """
        Extract documents from all Swagger sources.
        
        Returns:
            List of text documents (one per endpoint)
        """
        all_docs = []
        
        for name, url in self.sources.items():
            logger.info(f"Extracting from {name}: {url}")
            
            try:
                spec = fetch_swagger(url)
                api_info = extract_full_api_spec(spec)
                docs = render_api_to_text(api_info)
                all_docs.extend(docs)
                
                endpoint_count = len(api_info.get('paths', []))
                self._stats["total_endpoints"] += endpoint_count
                self._stats["successful_sources"] += 1
                
                logger.info(f"✓ Extracted {endpoint_count} endpoints from {api_info.get('title', name)}")
                
            except Exception as e:
                logger.error(f"✗ Failed to extract from {name}: {e}")
                self._stats["failed_sources"] += 1
        
        logger.info(f"Swagger extraction complete: {len(all_docs)} documents from {self._stats['successful_sources']} sources")
        return all_docs
    
    def get_source_name(self) -> str:
        """Get source identifier."""
        return "swagger"
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get connector metadata."""
        base = super().get_metadata()
        base.update({
            "source_count": len(self.sources),
            "source_urls": list(self.sources.values()),
            "total_endpoints": self._stats["total_endpoints"],
        })
        return base
    
    def get_stats(self) -> Dict[str, Any]:
        """Get extraction statistics."""
        return {
            **super().get_stats(),
            **self._stats,
            "source_count": len(self.sources),
        }

def extract_text_from_swagger_sources():
    """    
    Returns:
        List of text documents
    """
    connector = SwaggerConnector()
    return connector.extract_documents()


# ---------- CLI / Local Testing ----------

if __name__ == "__main__":
    docs = extract_text_from_swagger_sources()

    print("\n" + "="*80)
    print("Summary")
    print("="*80)
    print(f"Total text docs: {len(docs)}")
