"""
index_builder.py
================
Unified index builder for OrgGPT using Strategy Pattern.

Supported Data Sources:
  1. Swagger API documentation
  2. Datadog Catalog Entities (/api/v2/catalog/entity)
  3. Datadog SLOs (/api/v1/slo)
  4. POC mode for demos (JSON files, no API keys)

Usage:
    # Build unified index with all sources (POC mode)
    python index_builder.py
    
    # Build unified index with API mode
    python index_builder.py unified
    
    # Build unified index with POC mode
    python index_builder.py unified --poc
"""

import os
import sys
import logging
from typing import List, Dict, Any, Optional

# Ensure imports work when run from root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ingestion.base_connector import DataSourceConnector
from ingestion.Swagger_connector.swagger_connector import SwaggerConnector, extract_text_from_swagger_sources
from ingestion.Datadog_connector import DatadogCatalogConnector, DatadogSLOConnector
from ingestion.Document_connector.document_connector import extract_text_from_docs

from processing.chunker import chunk_texts
from processing.embedder import Embedder
from vector_store.store import VectorStore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class IndexBuilder:
    """
    Unified index builder using Strategy Pattern.
    
    Features:
    - Single collection for all data sources
    - Source metadata tracking
    
    Example:
        builder = IndexBuilder("unified_knowledge")
        builder.register_connector(SwaggerConnector())
        builder.register_connector(DatadogCatalogConnector(poc_mode=True))
        builder.build_unified_index()
    """
    
    def __init__(self, collection_name: str = "unified_knowledge"):
        """
        Initialize unified index builder.
        
        Args:
            collection_name: Name of unified collection (default: "unified_knowledge")
        """
        self.collection_name = collection_name
        self.embedder = Embedder()
        self.connectors: List[DataSourceConnector] = []
        
        logger.info(f"✓ IndexBuilder initialized (collection: '{collection_name}')")
    
    def register_connector(self, connector: DataSourceConnector) -> 'IndexBuilder':
        """
        Register a data source connector.
        
        Args:
            connector: DataSourceConnector instance
            
        Returns:
            Self for chaining
        """
        source_name = connector.get_source_name()
        self.connectors.append(connector)
        logger.info(f"✓ Registered connector: {source_name}")
        return self
    
    def build_unified_index(self) -> bool:
        """
        Build unified index from all registered connectors.
        
        Returns:
            True if at least one source succeeded
        """
        if not self.connectors:
            logger.warning("  No connectors registered")
            return False
        
        logger.info("\n" + "="*80)
        logger.info(f" BUILDING UNIFIED INDEX: '{self.collection_name}'")
        logger.info("="*80 + "\n")
        
        all_documents = []
        source_stats = {}
        successful_sources = 0
        
        # Extract from all sources
        for connector in self.connectors:
            source_name = connector.get_source_name()
            
            logger.info(f"\n{'─'*80}")
            logger.info(f" Extracting from: {source_name}")
            logger.info(f"{'─'*80}")
            
            try:
                # Extract documents
                docs = connector.extract_documents()
                
                if not docs:
                    logger.warning(f" No documents from {source_name}")
                    source_stats[source_name] = {"success": False, "doc_count": 0}
                    continue
                
                # Add source metadata to each document
                metadata = connector.get_metadata()
                logger.info(f"✓ Extracted {len(docs)} documents from {source_name}")
                logger.info(f"  Metadata: {metadata}")
                
                all_documents.extend(docs)
                source_stats[source_name] = {
                    "success": True,
                    "doc_count": len(docs),
                    "metadata": metadata
                }
                successful_sources += 1
                
            except Exception as e:
                logger.error(f" Failed to extract from {source_name}: {e}", exc_info=True)
                source_stats[source_name] = {"success": False, "error": str(e)}
        
        # Check if we have any documents
        if not all_documents:
            logger.error("\n No documents extracted from any source")
            return False
        
        logger.info(f"\n{'='*80}")
        logger.info(f" Total: {len(all_documents)} documents from {successful_sources} sources")
        logger.info(f"{'='*80}\n")
        
        # Store in unified collection
        success = self._store_documents(
            documents=all_documents,
            collection_name=self.collection_name,
            source_stats=source_stats
        )
        
        # Print summary
        self._print_summary(source_stats, success)
        
        return success
    
    def _store_documents(
        self,
        documents: List[str],
        collection_name: str,
        source_stats: Dict[str, Any]
    ) -> bool:
        """
        Chunk, embed, and store documents in vector store.
        
        Args:
            documents: List of text documents
            collection_name: Collection name
            source_stats: Statistics per source
            
        Returns:
            True if successful
        """
        try:
            # Step 1: Chunk texts
            logger.info(f" Chunking {len(documents)} documents...")
            chunks = chunk_texts(documents)
            logger.info(f" Created {len(chunks)} chunks")

            # Step 2: Create embeddings
            logger.info(f" Creating embeddings for {len(chunks)} chunks...")
            embeddings = self.embedder.embed(chunks)
            logger.info(f" Created {len(embeddings)} embeddings")

            # Step 3: Store in VectorStore
            logger.info(f" Storing in collection '{collection_name}'...")
            vs = VectorStore(collection_name, reset=True)  # Reset to ensure clean rebuild
            ids = [f"unified_chunk_{i}" for i in range(len(chunks))]
            
            # Add metadata for source tracking (could be enhanced later)
            vs.add(ids=ids, texts=chunks, embeddings=embeddings)
            
            logger.info(f" Stored {len(chunks)} chunks in '{collection_name}'\n")
            
            return True
            
        except Exception as e:
            logger.error(f" Failed to store documents: {e}", exc_info=True)
            return False
    
    def _print_summary(self, source_stats: Dict[str, Any], overall_success: bool):
        """Print build summary."""
        logger.info("\n" + "="*80)
        logger.info(" BUILD SUMMARY")
        logger.info("="*80)
        
        for source_name, stats in source_stats.items():
            if stats.get("success"):
                doc_count = stats.get("doc_count", 0)
                logger.info(f" {source_name}: {doc_count} documents")
            else:
                error = stats.get("error", "Unknown error")
                logger.info(f" {source_name}: {error}")
        
        success_count = sum(1 for s in source_stats.values() if s.get("success"))
        total_count = len(source_stats)
        
        logger.info(f"\n Total: {success_count}/{total_count} sources successful")
        
        if overall_success:
            logger.info(f" Unified index '{self.collection_name}' built successfully")
        else:
            logger.info(" Index build failed")
        
        logger.info("="*80 + "\n")


def main():
    """CLI entry point."""
    import sys
    
    # Check for POC mode flag
    poc_mode = "--poc" in sys.argv
    if poc_mode:
        sys.argv.remove("--poc")
    
    # Check for JSON Datadog file flag
    json_datadog_file = None
    if "--json-datadog" in sys.argv:
        idx = sys.argv.index("--json-datadog")
        if idx + 1 < len(sys.argv):
            json_datadog_file = sys.argv[idx + 1]
            sys.argv.remove("--json-datadog")
            sys.argv.remove(json_datadog_file)
        else:
            logger.error("\n Error: --json-datadog requires a file path")
            return 1
    
    builder = IndexBuilder()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "unified" or command == "--unified":
            # Unified mode
            logger.info("Building UNIFIED index...")
            builder.register_connector(SwaggerConnector())
            
            if poc_mode:
                builder.register_connector(DatadogCatalogConnector(poc_mode=True))
                builder.register_connector(DatadogSLOConnector(poc_mode=True))
            else:
                builder.register_connector(DatadogCatalogConnector())
                builder.register_connector(DatadogSLOConnector())
            
            # Optional: Add JSON Datadog file connector
            if json_datadog_file:
                from ingestion.Datadog_connector import DatadogJSONConnector
                logger.info(f"  Adding Datadog JSON file: {json_datadog_file}")
                builder.register_connector(DatadogJSONConnector(json_datadog_file))
            
            success = builder.build_unified_index()
        else:
            logger.error(f"\n Unknown command: {command}")
            logger.info("\nAvailable commands:")
            logger.info("    python index_builder.py                                    # Build unified index (POC mode)")
            logger.info("    python index_builder.py unified                            # Build unified index (API mode)")
            logger.info("    python index_builder.py unified --poc                      # Build unified index (POC mode)")
            logger.info("    python index_builder.py unified --poc --json-datadog FILE  # Include structured JSON file")
            logger.info("")
            return 1
    else:
        # Default: build unified index with POC mode
        logger.info(" Building UNIFIED index (POC mode by default)...")
        builder.register_connector(SwaggerConnector())
        builder.register_connector(DatadogCatalogConnector(poc_mode=True))
        builder.register_connector(DatadogSLOConnector(poc_mode=True))
        
        # Optional: Add JSON Datadog file connector
        if json_datadog_file:
            from ingestion.Datadog_connector import DatadogJSONConnector
            logger.info(f"  Adding Datadog JSON file: {json_datadog_file}")
            builder.register_connector(DatadogJSONConnector(json_datadog_file))
        
        success = builder.build_unified_index()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
