"""
datadog_slo_connector.py
=======================
Datadog SLO connector implementing DataSourceConnector interface.

This connector extracts Service Level Objectives from Datadog and transforms
them into RAG-ready documents following the Strategy Pattern.

SOLID Principles:
- SRP: Only responsible for Datadog SLO extraction
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


class DatadogSLOConnector(DataSourceConnector):
    """
    Datadog Service Level Objectives (SLO) connector.
    
    Extracts SLO definitions from Datadog API or JSON files
    and transforms them into RAG-ready markdown documents.
    
    Modes:
    - API mode: Connects to Datadog API (requires DD_API_KEY, DD_APP_KEY)
    - POC mode: Loads from JSON file (no API keys needed)
    
    Usage:
        # API mode
        connector = DatadogSLOConnector()
        docs = connector.extract_documents()
        
        # POC mode
        connector = DatadogSLOConnector(
            poc_mode=True,
            json_file="sample_get_slo_list.json"
        )
        docs = connector.extract_documents()
    """
    
    def __init__(
        self,
        poc_mode: bool = False,
        json_file: Optional[str] = None,
        include_corrections: bool = False
    ):
        """
        Initialize Datadog SLO connector.
        
        Args:
            poc_mode: If True, use JSON file instead of API
            json_file: Path to JSON file (for POC mode)
            include_corrections: If True, also extract SLO corrections (API mode only)
        """
        self.poc_mode = poc_mode
        self.json_file = json_file or "sample_get_slo_list.json"
        self.include_corrections = include_corrections
        
        # Initialize internal Datadog connector
        self._connector = DatadogConnector(poc_mode=poc_mode)
        
        self._stats = {
            "slo_count": 0,
            "correction_count": 0,
            "document_count": 0,
            "mode": "poc" if poc_mode else "api",
        }
    
    def extract_documents(self) -> List[str]:
        """
        Extract and transform Datadog SLOs to documents.
        
        Returns:
            List of markdown-formatted text documents
        """
        try:
            all_docs = []
            
            # Extract SLOs
            if self.poc_mode:
                logger.info(f"Extracting SLOs from JSON: {self.json_file}")
                slos = self._connector.extract_slos_from_json(self.json_file)
            else:
                logger.info("Extracting SLOs from Datadog API...")
                slos = self._connector.extract_slos()
            
            if not slos:
                logger.warning("No SLOs extracted")
                return []
            
            self._stats["slo_count"] = len(slos)
            logger.info(f"✓ Extracted {len(slos)} SLOs")
            
            # Transform to documents
            # Auto-detect if these are corrections or regular SLOs
            logger.info("Transforming SLOs to documents...")
            if slos and slos[0].get("type") == "correction":
                logger.info("Detected SLO corrections (type='correction')")
                docs = self._connector.slo_transformer.transform_corrections_batch(slos)
            else:
                logger.info("Detected regular SLOs")
                docs = self._connector.slo_transformer.transform_slos_batch(slos)
            
            all_docs.extend(docs)
            logger.info(f"✓ Transformed to {len(docs)} documents")
            
            # Optionally extract corrections (API mode only)
            if self.include_corrections and not self.poc_mode:
                try:
                    logger.info("Extracting SLO corrections...")
                    corrections = self._connector.extract_slo_corrections()
                    if corrections:
                        correction_docs = self._connector.slo_transformer.transform_corrections_batch(corrections)
                        all_docs.extend(correction_docs)
                        self._stats["correction_count"] = len(corrections)
                        logger.info(f"✓ Extracted {len(corrections)} SLO corrections")
                except Exception as e:
                    logger.warning(f"Could not extract SLO corrections: {e}")
            
            self._stats["document_count"] = len(all_docs)
            return all_docs
            
        except Exception as e:
            logger.error(f"Failed to extract Datadog SLOs: {e}", exc_info=True)
            raise
    
    def get_source_name(self) -> str:
        """Get source identifier."""
        return "datadog_slo"
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get connector metadata."""
        base = super().get_metadata()
        base.update({
            "mode": self._stats["mode"],
            "slo_count": self._stats["slo_count"],
            "correction_count": self._stats["correction_count"],
            "include_corrections": self.include_corrections,
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
