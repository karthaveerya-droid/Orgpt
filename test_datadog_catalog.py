#!/usr/bin/env python3
"""
test_datadog_catalog.py
=======================
Testing script for Datadog Catalog Entity POC.

Tests the new Catalog Entity API integration (/api/v2/catalog/entity) ✨

Run: python test_datadog_catalog.py
"""

import os
import sys
import logging
from typing import Optional
from unittest.mock import patch, MagicMock

# Ensure imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv

# Load environment
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# MOCK DATA & FIXTURES
# ============================================================================

MOCK_ENTITIES = [
    {
        "id": "service:payment-api",
        "type": "service",
        "attributes": {
            "name": "payment-api",
            "displayName": "Payment API",
            "kind": "service",
            "description": "Handles payment processing",
            "owner": "platform-team",
            "namespace": "production",
            "tags": ["critical", "payment"],
        },
        "meta": {
            "createdAt": "2024-01-01T00:00:00Z",
            "modifiedAt": "2024-02-01T00:00:00Z",
        },
        "relationships": {}
    },
    {
        "id": "service:auth-service",
        "type": "service",
        "attributes": {
            "name": "auth-service",
            "displayName": "Authentication Service",
            "kind": "service",
            "description": "Handles user authentication",
            "owner": "security-team",
            "namespace": "production",
            "tags": ["critical", "auth"],
        },
        "meta": {
            "createdAt": "2024-01-02T00:00:00Z",
            "modifiedAt": "2024-02-02T00:00:00Z",
        },
        "relationships": {}
    },
    {
        "id": "service:api-gateway",
        "type": "service",
        "attributes": {
            "name": "api-gateway",
            "displayName": "API Gateway",
            "kind": "service",
            "description": "Main API entry point",
            "owner": "platform-team",
            "namespace": "production",
            "tags": ["critical", "gateway"],
        },
        "meta": {
            "createdAt": "2024-01-03T00:00:00Z",
            "modifiedAt": "2024-02-03T00:00:00Z",
        },
        "relationships": {}
    },
]


def test_datadog_client():
    """Test 1: Basic Datadog API client connectivity (with mock)"""
    print("\n" + "="*80)
    print("TEST 1: Datadog API Client")
    print("="*80)
    
    try:
        from ingestion.Datadog_connector.datadog_client import (
            DatadogClientConfig,
            DatadogAPIClient
        )
        
        logger.info("✓ Imports successful")
        
        # Create mock config with dummy credentials
        with patch('ingestion.Datadog_connector.datadog_client.os.getenv') as mock_getenv:
            def getenv_side_effect(key, default=None):
                env_vars = {
                    "DD_API_KEY": "test_api_key_123",
                    "DD_APP_KEY": "test_app_key_456",
                    "DD_SITE": "datadoghq.eu"
                }
                return env_vars.get(key, default)
            
            mock_getenv.side_effect = getenv_side_effect
            
            # Create config
            config = DatadogClientConfig()
            logger.info(f"✓ Config created (site: {config.site})")
            
            # Create client
            client = DatadogAPIClient(config)
            logger.info("✓ Client initialized")
            
            # Mock the API response
            with patch.object(client, 'get') as mock_get:
                mock_get.return_value = {
                    "meta": {
                        "page": {"current": 1, "limit": 1}
                    },
                    "data": MOCK_ENTITIES[:1]
                }
                
                logger.info("Testing API connectivity to /api/v2/catalog/entity (mocked)...")
                response = client.get("/api/v2/catalog/entity", params={"page[limit]": 1})
                logger.info(f"✓ API call successful. Got {len(response.get('data', []))} entities")
        
        return True
    
    except Exception as e:
        logger.error(f"✗ Test failed: {e}", exc_info=True)
        return False


def test_catalog_extractor():
    """Test 2: Catalog Entity Extractor ✨"""
    print("\n" + "="*80)
    print("TEST 2: Catalog Entity Extractor ✨")
    print("="*80)
    
    try:
        from ingestion.Datadog_connector.datadog_client import DatadogClientConfig, DatadogAPIClient
        from ingestion.Datadog_connector.datadog_catalog_extractor import CatalogEntityExtractor
        
        config = DatadogClientConfig()
        client = DatadogAPIClient(config)
        
        # Test catalog entity extraction
        logger.info("Testing CatalogEntityExtractor...")
        extractor = CatalogEntityExtractor(client)
        
        logger.info("Extracting Catalog Entities (max 5 pages)...")
        entities = extractor.extract_paginated_entities(
            kinds=["service"],
            limit=100,
            max_pages=5
        )
        
        logger.info(f"✓ Extracted {len(entities)} catalog entities")
        
        if entities:
            first_entity = entities[0]
            logger.info(f"  Sample entity ID: {first_entity.get('id')}")
            logger.info(f"  Sample entity name: {first_entity.get('attributes', {}).get('name')}")
        
        client.close()
        return True
    
    except Exception as e:
        logger.error(f"✗ Test failed: {e}", exc_info=True)
        return False


def test_catalog_transformer():
    """Test 3: Catalog Entity Transformer ✨"""
    print("\n" + "="*80)
    print("TEST 3: Catalog Entity Transformer ✨")
    print("="*80)
    
    try:
        from ingestion.Datadog_connector.datadog_catalog_transformers import CatalogEntityTransformer
        
        logger.info("Testing CatalogEntityTransformer...")
        transformer = CatalogEntityTransformer()
        
        # Create a sample entity for testing
        sample_entity = {
            "id": "test-service",
            "type": "service",
            "attributes": {
                "name": "test-service",
                "displayName": "Test Service",
                "kind": "service",
                "description": "A sample service for testing",
                "owner": "platform-team",
                "namespace": "default",
                "tags": ["test", "demo"],
            },
            "meta": {
                "createdAt": "2024-01-01T00:00:00Z",
                "modifiedAt": "2024-01-02T00:00:00Z",
            },
            "relationships": {}
        }
        
        # Transform the entity
        logger.info("Transforming entity to markdown...")
        doc = transformer.transform_entity(sample_entity)
        
        logger.info(f"✓ Transformation successful")
        logger.info(f"  Document length: {len(doc)} characters")
        logger.info(f"  First 200 chars:\n{doc[:200]}...")
        
        return True
    
    except Exception as e:
        logger.error(f"✗ Test failed: {e}", exc_info=True)
        return False


def test_connector():
    """Test 4: Full DatadogConnector (Catalog Entity)"""
    print("\n" + "="*80)
    print("TEST 4: DatadogConnector (Catalog Entity Integration) ✨")
    print("="*80)
    
    try:
        from ingestion.Datadog_connector.datadog_connector import DatadogConnector
        
        logger.info("Initializing DatadogConnector...")
        connector = DatadogConnector()
        
        logger.info("Extracting Catalog Entities (POC: max 10)...")
        entities = connector.extract_catalog_entities(
            kinds=["service"],
            limit=50,
            max_pages=1
        )
        
        logger.info(f"✓ Extracted {len(entities)} entities")
        
        if entities:
            logger.info("Transforming entities to documents...")
            docs = connector.catalog_transformer.transform_entities_batch(entities)
            logger.info(f"✓ Transformed to {len(docs)} documents")
            
            if docs:
                logger.info(f"  Sample document length: {len(docs[0])} characters")
        
        return True
    
    except Exception as e:
        logger.error(f"✗ Test failed: {e}", exc_info=True)
        return False


def test_vector_store_integration():
    """Test 5: Vector Store Integration (Catalog Entity) with mock"""
    print("\n" + "="*80)
    print("TEST 5: Vector Store Integration ✨")
    print("="*80)
    
    try:
        from ingestion.Datadog_connector.datadog_store_integration import DatadogVectorStoreIntegration
        from vector_store.store import VectorStore
        
        logger.info("Initializing VectorStore (datadog_catalog collection)...")
        vs = VectorStore(collection_name="datadog_catalog")
        
        logger.info("Initializing DatadogVectorStoreIntegration...")
        integration = DatadogVectorStoreIntegration(vs, cache_ttl_seconds=3600)
        
        # Mock the DatadogConnector to return our test data
        with patch('ingestion.Datadog_connector.datadog_store_integration.DatadogConnector') as mock_connector_class:
            mock_connector = MagicMock()
            mock_connector_class.return_value = mock_connector
            
            # Setup mock to return test entities
            mock_connector.extract_catalog_entities.return_value = MOCK_ENTITIES
            
            # Mock the transformer
            mock_connector.catalog_transformer.transform_entities_batch.return_value = [
                f"# {entity['attributes']['name']}\n\n{entity['attributes']['description']}"
                for entity in MOCK_ENTITIES
            ]
            
            logger.info("Ingesting Datadog Catalog data (mocked)...")
            result = integration.ingest_datadog_data()
            
            logger.info(f"✓ Ingestion result: {result['status']}")
            if result['status'] == 'success':
                logger.info(f"  Entities: {result.get('entity_count', 0)}")
                logger.info(f"  Documents: {result.get('document_count', 0)}")
        
        return result['status'] == 'success'
    
    except Exception as e:
        logger.error(f"✗ Test failed: {e}", exc_info=True)
        return False


def test_index_builder():
    """Test 6: Index Builder (Catalog Entity) with mock"""
    print("\n" + "="*80)
    print("TEST 6: Index Builder with Catalog Entity ✨")
    print("="*80)
    
    try:
        from index_builder import IndexBuilder
        
        logger.info("Initializing IndexBuilder...")
        builder = IndexBuilder()
        
        # Mock the DatadogConnector to return our test data
        with patch('index_builder.DatadogConnector') as mock_connector_class:
            mock_connector = MagicMock()
            mock_connector_class.return_value = mock_connector
            
            # Setup mock to return test entities
            mock_connector.extract_catalog_entities.return_value = MOCK_ENTITIES
            
            # Mock the transformer
            mock_connector.catalog_transformer.transform_entities_batch.return_value = [
                f"# {entity['attributes']['name']}\n\nOwner: {entity['attributes']['owner']}\n\n{entity['attributes']['description']}"
                for entity in MOCK_ENTITIES
            ]
            
            logger.info("Building Datadog Catalog index (mocked)...")
            success = builder.build_datadog_catalog_index()
            
            logger.info(f"✓ Index build {'successful' if success else 'failed'}")
        
        return success
    
    except Exception as e:
        logger.error(f"✗ Test failed: {e}", exc_info=True)
        return False


def run_all_tests():
    """Run all Datadog Catalog Entity tests in sequence"""
    print("\n" + "█" * 80)
    print("█" + " " * 78 + "█")
    print("█  DATADOG CATALOG ENTITY POC - TEST SUITE ✨" + " " * 32 + "█")
    print("█" + " " * 78 + "█")
    print("█" * 80)
    
    tests = [
        ("Datadog Client", test_datadog_client),
        ("Catalog Extractor", test_catalog_extractor),
        ("Catalog Transformer", test_catalog_transformer),
        ("Connector", test_connector),
        ("Vector Store Integration", test_vector_store_integration),
        ("Index Builder", test_index_builder),
    ]
    
    results = {}
    
    for name, test_func in tests:
        try:
            result = test_func()
            results[name] = result
        except Exception as e:
            logger.error(f"Unexpected error in {name}: {e}")
            results[name] = False
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    for name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    total_passed = sum(1 for r in results.values() if r)
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    print("="*80 + "\n")
    
    return total_passed == total_tests


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
