"""
Datadog Connector Module
========================
Integrates Datadog APM service catalog, dependency graphs, and ownership data
into OrgGPT's knowledge base.

Exports:
  - DatadogConnector: Main orchestrator
  - extract_datadog_data: Convenience function for direct ingestion
  - CatalogEntityExtractor: Advanced catalog entity extraction
  - CatalogEntityTransformer: Transform catalog entities to RAG documents
"""

from .datadog_connector import DatadogConnector
from .datadog_connector import extract_datadog_data
from .datadog_catalog_extractor import CatalogEntityExtractor
from .datadog_catalog_transformers import CatalogEntityTransformer

__all__ = [
    "DatadogConnector",
    "extract_datadog_data",
    "CatalogEntityExtractor",
    "CatalogEntityTransformer",
]
