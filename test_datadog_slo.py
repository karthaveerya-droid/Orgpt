#!/usr/bin/env python3
"""
test_datadog_slo.py
===================
Testing script for Datadog SLO Integration.

Tests the SLO API integration (/api/v1/slo) ✨

Run: python test_datadog_slo.py
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

MOCK_SLOS = [
    {
        "id": "slo-api-availability",
        "name": "API Availability",
        "description": "99.9% uptime for payment API",
        "type": "metric",
        "type_id": 0,
        "tags": ["env:prod", "team:platform", "service:payment"],
        "thresholds": [
            {
                "target": 99.9,
                "target_display": "99.9",
                "timeframe": "7d",
                "warning": 99.5
            },
            {
                "target": 99.95,
                "target_display": "99.95",
                "timeframe": "30d",
                "warning": 99.85
            }
        ],
        "monitor_ids": [123456, 789012],
        "monitor_tags": ["monitor:critical"],
        "created_at": 1640995200,
        "modified_at": 1641081600,
        "creator": {
            "name": "John Doe",
            "email": "john@example.com"
        }
    },
    {
        "id": "slo-auth-latency",
        "name": "Authentication Latency",
        "description": "95% of requests under 200ms",
        "type": "metric",
        "type_id": 0,
        "tags": ["env:prod", "team:security", "service:auth"],
        "thresholds": [
            {
                "target": 95.0,
                "target_display": "95.0",
                "timeframe": "7d",
                "warning": 90.0
            },
            {
                "target": 97.0,
                "target_display": "97.0",
                "timeframe": "30d",
                "warning": 93.0
            }
        ],
        "monitor_ids": [234567],
        "monitor_tags": ["monitor:performance"],
        "created_at": 1640995200,
        "modified_at": 1641081600,
        "creator": {
            "name": "Jane Smith",
            "email": "jane@example.com"
        }
    },
]

MOCK_CORRECTIONS = [
    {
        "id": "corr-maintenance-123",
        "type": "correction",
        "attributes": {
            "category": "Scheduled Maintenance",
            "description": "Database migration and optimization",
            "start": 1641081600,
            "end": 1641085200,
            "duration": 3600,
            "slo_id": "slo-api-availability",
            "timezone": "UTC",
            "rrule": "FREQ=WEEKLY;BYDAY=SU",
            "created_at": 1641000000,
            "modified_at": 1641002000,
            "creator": {
                "name": "DevOps Team",
                "email": "devops@example.com",
                "handle": "devops"
            },
            "modifier": {
                "name": "DevOps Team",
                "email": "devops@example.com",
                "handle": "devops"
            }
        }
    },
]


def test_slo_extractor():
    """Test 1: SLO Extractor"""
    print("\n" + "="*80)
    print("TEST 1: SLO Extractor ✨")
    print("="*80)
    
    try:
        from ingestion.Datadog_connector.datadog_client import DatadogClientConfig, DatadogAPIClient
        from ingestion.Datadog_connector.datadog_slo_extractor import SLOExtractor
        
        logger.info("✓ Imports successful")
        
        # Create mock client
        with patch('ingestion.Datadog_connector.datadog_client.os.getenv') as mock_getenv:
            def getenv_side_effect(key, default=None):
                env_vars = {
                    'DD_API_KEY': 'test_api_key_12345',
                    'DD_APP_KEY': 'test_app_key_67890',
                    'DD_SITE': 'datadoghq.eu'
                }
                return env_vars.get(key, default)
            
            mock_getenv.side_effect = getenv_side_effect
            
            config = DatadogClientConfig()
            client = DatadogAPIClient(config)
            
            logger.info("Testing SLOExtractor...")
            extractor = SLOExtractor(client)
            
            # Mock the API response
            with patch.object(client, 'get') as mock_get:
                mock_get.return_value = {"data": MOCK_SLOS}
                
                logger.info("Extracting SLOs...")
                slos = extractor.extract_all_slos(limit=100)
                
                logger.info(f"✓ Extracted {len(slos)} SLOs")
                
                if slos:
                    first_slo = slos[0]
                    logger.info(f"  Sample SLO ID: {first_slo.get('id')}")
                    logger.info(f"  Sample SLO name: {first_slo.get('name')}")
                    logger.info(f"  Sample SLO targets: {len(first_slo.get('thresholds', []))} thresholds")
            
            client.close()
        
        return True
    
    except Exception as e:
        logger.error(f"✗ Test failed: {e}", exc_info=True)
        return False


def test_slo_transformer():
    """Test 2: SLO Transformer"""
    print("\n" + "="*80)
    print("TEST 2: SLO Transformer ✨")
    print("="*80)
    
    try:
        from ingestion.Datadog_connector.datadog_slo_transformer import SLOTransformer
        
        logger.info("Testing SLOTransformer...")
        transformer = SLOTransformer()
        
        # Transform the first mock SLO
        sample_slo = MOCK_SLOS[0]
        
        logger.info("Transforming SLO to markdown...")
        doc = transformer.transform_slo(sample_slo)
        
        logger.info(f"✓ Transformation successful")
        logger.info(f"  Document length: {len(doc)} characters")
        logger.info(f"  First 300 chars:\n{doc[:300]}...")
        
        # Test batch transformation
        logger.info("\nTesting batch transformation...")
        docs = transformer.transform_slos_batch(MOCK_SLOS)
        logger.info(f"✓ Batch transformation successful: {len(docs)} documents")
        
        return True
    
    except Exception as e:
        logger.error(f"✗ Test failed: {e}", exc_info=True)
        return False


def test_correction_transformer():
    """Test 3: SLO Correction Transformer"""
    print("\n" + "="*80)
    print("TEST 3: SLO Correction Transformer ✨")
    print("="*80)
    
    try:
        from ingestion.Datadog_connector.datadog_slo_transformer import SLOTransformer
        
        logger.info("Testing SLO Correction Transformer...")
        transformer = SLOTransformer()
        
        # Transform the mock correction
        sample_correction = MOCK_CORRECTIONS[0]
        
        logger.info("Transforming correction to markdown...")
        doc = transformer.transform_slo_correction(sample_correction)
        
        logger.info(f"✓ Transformation successful")
        logger.info(f"  Document length: {len(doc)} characters")
        logger.info(f"  First 300 chars:\n{doc[:300]}...")
        
        # Test batch transformation
        logger.info("\nTesting batch transformation...")
        docs = transformer.transform_corrections_batch(MOCK_CORRECTIONS)
        logger.info(f"✓ Batch transformation successful: {len(docs)} documents")
        
        return True
    
    except Exception as e:
        logger.error(f"✗ Test failed: {e}", exc_info=True)
        return False


def test_slo_connector():
    """Test 4: DatadogConnector with SLO support"""
    print("\n" + "="*80)
    print("TEST 4: DatadogConnector (SLO Integration) ✨")
    print("="*80)
    
    try:
        from ingestion.Datadog_connector.datadog_connector import DatadogConnector
        
        logger.info("Testing POC mode (JSON file)...")
        connector = DatadogConnector(poc_mode=True)
        
        # Test JSON extraction
        json_file = "sample_get_slo_list.json"
        if os.path.exists(json_file):
            logger.info(f"Loading SLOs from {json_file}...")
            slos = connector.extract_slos_from_json(json_file)
            
            logger.info(f"✓ Loaded {len(slos)} SLOs from JSON")
            
            if slos:
                logger.info("Transforming SLOs to documents...")
                docs = connector.slo_transformer.transform_slos_batch(slos)
                logger.info(f"✓ Transformed to {len(docs)} documents")
                
                if docs:
                    logger.info(f"  First document preview:\n{docs[0][:200]}...")
        else:
            logger.warning(f"JSON file not found: {json_file}")
            logger.info("Testing with mock data instead...")
            
            # Mock the connector methods
            with patch.object(connector, 'extract_slos') as mock_extract:
                mock_extract.return_value = MOCK_SLOS
                
                logger.info("Extracting SLOs (mocked)...")
                slos = mock_extract()
                
                logger.info(f"✓ Extracted {len(slos)} SLOs")
                
                logger.info("Transforming SLOs to documents...")
                docs = connector.slo_transformer.transform_slos_batch(slos)
                logger.info(f"✓ Transformed to {len(docs)} documents")
        
        return True
    
    except Exception as e:
        logger.error(f"✗ Test failed: {e}", exc_info=True)
        return False


def test_vector_store_integration():
    """Test 5: Vector Store Integration with SLOs"""
    print("\n" + "="*80)
    print("TEST 5: Vector Store Integration (SLO) ✨")
    print("="*80)
    
    try:
        from ingestion.Datadog_connector.datadog_store_integration import DatadogVectorStoreIntegration
        from vector_store.store import VectorStore
        
        logger.info("Initializing VectorStore (datadog_slo_test collection)...")
        vs = VectorStore(collection_name="datadog_slo_test")
        
        logger.info("Initializing DatadogVectorStoreIntegration...")
        integration = DatadogVectorStoreIntegration(vs, cache_ttl_seconds=3600)
        
        # Mock the DatadogConnector
        with patch('ingestion.Datadog_connector.datadog_store_integration.DatadogConnector') as mock_connector_class:
            mock_connector = MagicMock()
            mock_connector_class.return_value = mock_connector
            
            # Setup mock to return test SLOs
            mock_connector.extract_slos_from_json.return_value = MOCK_SLOS
            
            # Mock the transformer
            mock_connector.slo_transformer.transform_slos_batch.return_value = [
                f"# SLO: {slo['name']}\n\n**ID**: {slo['id']}\n\n{slo['description']}"
                for slo in MOCK_SLOS
            ]
            
            logger.info("Ingesting SLO data (mocked)...")
            result = integration.ingest_slo_data(json_file_path="sample_get_slo_list.json")
            
            logger.info(f"✓ Ingestion result: {result['status']}")
            if result['status'] == 'success':
                logger.info(f"  SLO count: {result.get('slo_count', 0)}")
                logger.info(f"  Document count: {result.get('document_count', 0)}")
        
        return result['status'] == 'success'
    
    except Exception as e:
        logger.error(f"✗ Test failed: {e}", exc_info=True)
        return False


def test_index_builder():
    """Test 6: Index Builder with SLO support"""
    print("\n" + "="*80)
    print("TEST 6: Index Builder (SLO POC) ✨")
    print("="*80)
    
    try:
        from index_builder import IndexBuilder
        
        logger.info("Initializing IndexBuilder...")
        builder = IndexBuilder()
        
        # Check if sample JSON exists
        json_file = "sample_get_slo_list.json"
        if os.path.exists(json_file):
            logger.info(f"Building SLO POC index from {json_file}...")
            success = builder.build_datadog_slo_poc_index(json_file)
            
            logger.info(f"✓ Index build {'successful' if success else 'failed'}")
        else:
            logger.warning(f"JSON file not found: {json_file}")
            logger.info("Testing with mock data instead...")
            
            # Mock the connector
            with patch('index_builder.DatadogConnector') as mock_connector_class:
                mock_connector = MagicMock()
                mock_connector_class.return_value = mock_connector
                
                # Setup mock to return test SLOs
                mock_connector.extract_slos_from_json.return_value = MOCK_SLOS
                
                # Mock the transformer
                mock_connector.slo_transformer.transform_slos_batch.return_value = [
                    f"# SLO: {slo['name']}\n\nTarget: {slo['thresholds'][0]['target']}%\n\n{slo['description']}"
                    for slo in MOCK_SLOS
                ]
                
                logger.info("Building SLO POC index (mocked)...")
                success = builder.build_datadog_slo_poc_index(json_file)
                
                logger.info(f"✓ Index build {'successful' if success else 'failed'}")
        
        return success
    
    except Exception as e:
        logger.error(f"✗ Test failed: {e}", exc_info=True)
        return False


def run_all_tests():
    """Run all Datadog SLO tests in sequence"""
    print("\n" + "█" * 80)
    print("█" + " " * 78 + "█")
    print("█  DATADOG SLO INTEGRATION - TEST SUITE ✨" + " " * 36 + "█")
    print("█" + " " * 78 + "█")
    print("█" * 80)
    
    tests = [
        ("SLO Extractor", test_slo_extractor),
        ("SLO Transformer", test_slo_transformer),
        ("SLO Correction Transformer", test_correction_transformer),
        ("SLO Connector", test_slo_connector),
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
