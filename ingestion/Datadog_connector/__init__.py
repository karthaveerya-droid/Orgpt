"""
Datadog Connector Module
========================
Integrates Datadog APM service catalog, dependency graphs, and ownership data
into OrgGPT's knowledge base.
"""

# New unified connectors (Strategy Pattern)
from .datadog_catalog_connector import DatadogCatalogConnector
from .datadog_slo_connector import DatadogSLOConnector
from .datadog_connector import DatadogConnector
from .datadog_connector import extract_datadog_data

# Internal components (for advanced usage)
from .datadog_catalog_extractor import CatalogEntityExtractor
from .datadog_catalog_transformers import CatalogEntityTransformer

__all__ = [
    # New unified connectors (recommended)
    "DatadogCatalogConnector",
    "DatadogSLOConnector",
    "DatadogConnector",
    "extract_datadog_data",
    # Internal components
    "CatalogEntityExtractor",
    "CatalogEntityTransformer",
]
