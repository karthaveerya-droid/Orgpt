"""
index_builder.py
================
Multi-source index builder for OrgGPT.

Supports:
  1. Swagger API documentation
  2. Project documents
  3. Datadog Catalog Entities (/api/v2/catalog/entity) ✨
  4. Datadog POC mode (JSON file, no API keys) 🎯

Usage:
    python index_builder.py                            # Build all indexes (default)
    python index_builder.py swagger                    # Build only Swagger
    python index_builder.py datadog_catalog            # Build Catalog Entities ✨
    python index_builder.py datadog_poc                # Build POC from JSON (no API keys) 🎯
    python index_builder.py datadog_poc custom.json    # Build POC from custom JSON file
"""

import os
import sys
import logging
from typing import List

# Ensure imports work when run from root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ingestion.Swagger_connector.swagger_connector import extract_text_from_swagger_sources
from ingestion.Document_connector.document_connector import extract_text_from_docs
from ingestion.Datadog_connector.datadog_connector import DatadogConnector

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
    """Multi-source index builder."""
    
    def __init__(self):
        """Initialize builder with reusable components."""
        self.embedder = Embedder()
        self.datadog_connector = None
        self.datadog_poc_connector = None
    
    def _get_datadog_connector(self) -> DatadogConnector:
        """Lazy load Datadog connector (only on demand)."""
        if self.datadog_connector is None:
            logger.info("Initializing Datadog connector...")
            self.datadog_connector = DatadogConnector()
        return self.datadog_connector
    
    def _get_datadog_poc_connector(self) -> DatadogConnector:
        """Lazy load Datadog POC connector (no API keys)."""
        if self.datadog_poc_connector is None:
            logger.info("Initializing Datadog POC connector (no API keys)...")
            self.datadog_poc_connector = DatadogConnector(poc_mode=True)
        return self.datadog_poc_connector
    
    def _create_and_store_index(
        self,
        documents: List[str],
        collection_name: str,
        id_prefix: str
    ) -> int:
        """
        Common logic for chunking, embedding, and storing documents.
        
        Args:
            documents: List of text documents
            collection_name: VectorStore collection name
            id_prefix: Prefix for document IDs
            
        Returns:
            Number of chunks stored
        """
        # Step 1: Chunk texts
        logger.info(f"Chunking {len(documents)} documents...")
        chunks = chunk_texts(documents)
        logger.info(f"✓ Chunked into {len(chunks)} segments")

        # Step 2: Create embeddings
        logger.info(f"Creating embeddings for {len(chunks)} chunks...")
        embeddings = self.embedder.embed(chunks)
        logger.info(f"✓ Created {len(embeddings)} embeddings")

        # Step 3: Store in VectorStore
        logger.info(f"Storing in VectorStore collection '{collection_name}'...")
        vs = VectorStore(collection_name)
        ids = [f"{id_prefix}_chunk_{i}" for i in range(len(chunks))]
        vs.add(ids=ids, texts=chunks, embeddings=embeddings)
        logger.info(f"✓ Stored {len(chunks)} chunks in collection '{collection_name}'\n")
        
        return len(chunks)

    def build_swagger_index(self) -> bool:
        """
        Build index from Swagger sources.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("\n" + "="*80)
        logger.info("📚 Building Swagger Index")
        logger.info("="*80 + "\n")

        try:
            # Step 1: Extract docs
            logger.info("Extracting Swagger documentation...")
            docs = extract_text_from_swagger_sources() + extract_text_from_docs()
            logger.info(f"✓ Extracted {len(docs)} documents")

            # Step 2-4: Chunk, embed, store
            chunks = self._create_and_store_index(
                documents=docs,
                collection_name="swagger",
                id_prefix="swagger"
            )
            
            logger.info(f"✅ Swagger index built successfully ({chunks} chunks)\n")
            return True
            
        except Exception as e:
            logger.error(f"❌ Swagger index failed: {e}\n")
            return False

    def build_datadog_catalog_index(self) -> bool:
        """
        Build index from new Datadog Catalog Entity API (/api/v2/catalog/entity).
        
        Uses CatalogEntityTransformer for rich markdown conversion.
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("\n" + "="*80)
        logger.info("📚 Building Datadog Catalog Entity Index ✨ (/api/v2/catalog/entity)")
        logger.info("="*80 + "\n")

        try:
            # Step 1: Extract catalog entities
            logger.info("Extracting Datadog Catalog entities...")
            connector = self._get_datadog_connector()
            entities = connector.extract_catalog_entities()
            
            if not entities:
                logger.warning("No catalog entities found")
                return False
                
            logger.info(f"✓ Extracted {len(entities)} catalog entities")

            # Step 2: Transform to documents
            logger.info("Transforming entities using CatalogEntityTransformer...")
            docs = connector.catalog_transformer.transform_entities_batch(entities)
            logger.info(f"✓ Transformed {len(docs)} entities to documents")

            # Step 3-5: Chunk, embed, store
            chunks = self._create_and_store_index(
                documents=docs,
                collection_name="datadog_catalog",
                id_prefix="datadog_catalog"
            )
            
            logger.info(f"✅ Datadog Catalog index built successfully ({chunks} chunks)\n")
            return True
            
        except Exception as e:
            logger.error(f"⚠️  Datadog Catalog index failed: {e}\n")
            return False

    def build_datadog_poc_index(self, json_file: str = "sample_get_entities_list.json") -> bool:
        """
        Build index from sample JSON file.
        
        This method demonstrates Datadog integration without requiring DD_API_KEY
        or DD_APP_KEY. Perfect for presentations and testing.
        
        Args:
            json_file: Path to JSON file containing Datadog entities
                      (default: sample_get_entities_list.json)
        
        Returns:
            True if successful, False otherwise
        """
        logger.info("\n" + "="*80)
        logger.info("📚 Building Datadog POC Index 🎯 (No API Keys Required)")
        logger.info(f"📂 Using JSON file: {json_file}")
        logger.info("="*80 + "\n")

        try:
            # Check if file exists
            if not os.path.exists(json_file):
                logger.error(f"❌ JSON file not found: {json_file}")
                logger.info("ℹ️  Place your sample JSON file in the project root directory")
                return False

            # Step 1: Load entities from JSON
            logger.info(f"Loading entities from JSON file: {json_file}")
            connector = self._get_datadog_poc_connector()
            entities = connector.extract_catalog_entities_from_json(json_file)
            
            if not entities:
                logger.warning("No entities found in JSON file")
                return False
                
            logger.info(f"✓ Loaded {len(entities)} entities from JSON")

            # Step 2: Convert entities to documents (already transformed by extract method)
            docs = entities  # Already transformed by extract_catalog_entities_from_json
            logger.info(f"✓ Using {len(docs)} transformed documents")

            # Step 3-5: Chunk, embed, store in separate POC collection
            chunks = self._create_and_store_index(
                documents=docs,
                collection_name="datadog_poc",
                id_prefix="datadog_poc"
            )
            
            logger.info(f"✅ Datadog POC index built successfully ({chunks} chunks)")
            logger.info(f"ℹ️  Collection: 'datadog_poc' (separate from production)")
            logger.info(f"ℹ️  Source: {json_file}\n")
            return True
            
        except Exception as e:
            logger.error(f"❌ Datadog POC index failed: {e}\n", exc_info=True)
            return False

    def build_all_indexes(self) -> bool:
        """
        Build all available indexes.
        
        Returns:
            True if at least one index succeeded
        """
        logger.info("\n" + "="*80)
        logger.info("🚀 BUILDING ALL INDEXES")
        logger.info("="*80)

        results = {}
        
        # Build Swagger
        results['swagger'] = self.build_swagger_index()
        
        # Build Datadog Catalog
        results['datadog_catalog'] = self.build_datadog_catalog_index()

        # Summary
        logger.info("="*80)
        logger.info("📊 INDEX BUILD SUMMARY")
        logger.info("="*80)
        
        for name, success in results.items():
            status = "✅" if success else "❌"
            logger.info(f"{status} {name}")
        
        total_success = sum(1 for v in results.values() if v)
        logger.info(f"\nTotal: {total_success}/{len(results)} indexes built successfully")
        logger.info("="*80 + "\n")
        
        return total_success > 0


def main():
    """CLI entry point."""
    import sys
    
    builder = IndexBuilder()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "swagger":
            success = builder.build_swagger_index()
        elif command == "datadog_catalog":
            success = builder.build_datadog_catalog_index()
        elif command == "datadog_poc":
            # Check if custom JSON file provided
            json_file = sys.argv[2] if len(sys.argv) > 2 else "sample_get_entities_list.json"
            success = builder.build_datadog_poc_index(json_file)
        elif command == "all":
            success = builder.build_all_indexes()
        else:
            logger.error(f"\n❌ Unknown command: {command}")
            logger.info("\nAvailable commands:")
            logger.info("  python index_builder.py swagger                    # Build Swagger index")
            logger.info("  python index_builder.py datadog_catalog            # Build Catalog Entities ✨")
            logger.info("  python index_builder.py datadog_poc                # Build POC (no API keys) 🎯")
            logger.info("  python index_builder.py datadog_poc custom.json    # Build POC from custom file")
            logger.info("  python index_builder.py all                        # Build all indexes (default)")
            logger.info("")
            return 1
    else:
        # Default: build all
        success = builder.build_all_indexes()
    
    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
