#!/usr/bin/env python3
"""
test_swagger_connector.py
=========================
Testing script for Swagger/OpenAPI Connector.

Tests the Swagger connector integration including:
  - Swagger/OpenAPI spec parsing
  - Text document rendering
  - Index building integration

Run: python test_swagger_connector.py
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

MOCK_SWAGGER_SPEC = {
    "swagger": "2.0",
    "info": {
        "title": "Test API",
        "version": "1.0.0",
        "description": "A test API for validation"
    },
    "host": "api.example.com",
    "basePath": "/v1",
    "schemes": ["https"],
    "paths": {
        "/users": {
            "get": {
                "summary": "Get all users",
                "description": "Retrieve a list of all users",
                "operationId": "getUsers",
                "produces": ["application/json"],
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "schema": {
                            "type": "array",
                            "items": {"$ref": "#/definitions/User"}
                        }
                    }
                }
            },
            "post": {
                "summary": "Create a user",
                "description": "Create a new user",
                "operationId": "createUser",
                "consumes": ["application/json"],
                "parameters": [
                    {
                        "name": "body",
                        "in": "body",
                        "schema": {"$ref": "#/definitions/User"}
                    }
                ],
                "responses": {
                    "201": {"description": "User created"}
                }
            }
        },
        "/users/{id}": {
            "get": {
                "summary": "Get user by ID",
                "description": "Retrieve a specific user by ID",
                "operationId": "getUser",
                "parameters": [
                    {
                        "name": "id",
                        "in": "path",
                        "required": True,
                        "type": "string"
                    }
                ],
                "responses": {
                    "200": {"description": "User found"}
                }
            }
        }
    },
    "definitions": {
        "User": {
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "email": {"type": "string"}
            }
        }
    }
}


# ============================================================================
# SWAGGER CONNECTOR TESTS
# ============================================================================

def test_swagger_helpers():
    """Test 1: Swagger Helpers (extract_full_api_spec, render_api_to_text)"""
    print("\n" + "="*80)
    print("TEST 1: Swagger Helpers ")
    print("="*80)
    
    try:
        from ingestion.Swagger_connector.swagger_connector_helpers import (
            extract_full_api_spec,
            render_api_to_text
        )
        
        logger.info("Testing Swagger/OpenAPI parsing...")
        
        # Step 1: Extract API spec
        logger.info("Extracting API specification from mock...")
        api_info = extract_full_api_spec(MOCK_SWAGGER_SPEC)
        
        logger.info(f"Extracted API: {api_info.get('title')}")
        logger.info(f"  Version: {api_info.get('version')}")
        logger.info(f"  Description: {api_info.get('description')}")
        
        # Step 2: Extract paths
        paths = api_info.get('paths', [])
        logger.info(f"  Endpoints: {len(paths)}")
        
        if not paths:
            logger.warning(" No paths found in API spec")
            return False
        
        # Step 3: Render to text
        logger.info("Rendering API documentation to text...")
        docs = render_api_to_text(api_info)
        
        logger.info(f"Generated {len(docs)} text documents")
        
        if docs:
            logger.info(f"  Sample doc length: {len(docs[0])} characters")
            logger.info(f"  First 150 chars:\n{docs[0][:150]}...")
        
        return True
    
    except Exception as e:
        logger.error(f"✗ Test failed: {e}", exc_info=True)
        return False


def test_swagger_connector():
    """Test 2: Swagger Connector (extract_text_from_swagger_sources)"""
    print("\n" + "="*80)
    print("TEST 2: Swagger Connector ")
    print("="*80)
    
    try:
        from ingestion.Swagger_connector.swagger_connector import extract_text_from_swagger_sources
        
        logger.info("Testing complete Swagger connector...")
        
        # Mock the fetch_swagger function to avoid real API calls
        with patch('ingestion.Swagger_connector.swagger_connector.fetch_swagger') as mock_fetch:
            mock_fetch.return_value = MOCK_SWAGGER_SPEC
            
            logger.info("Extracting text from Swagger sources (mocked)...")
            docs = extract_text_from_swagger_sources()
            
            logger.info(f"Extracted {len(docs)} documents from Swagger sources")
            
            if not docs:
                logger.warning(" No documents extracted")
                return False
            
            # Check first document
            if docs:
                logger.info(f"  Sample doc length: {len(docs[0])} characters")
                logger.info(f"  First 150 chars:\n{docs[0][:150]}...")
        
        return True
    
    except Exception as e:
        logger.error(f"✗ Test failed: {e}", exc_info=True)
        return False


def test_swagger_index_builder():
    """Test 3: Swagger Integration with Index Builder"""
    print("\n" + "="*80)
    print("TEST 3: Swagger + Index Builder Integration ")
    print("="*80)
    
    try:
        from index_builder import IndexBuilder
        
        logger.info("Initializing IndexBuilder...")
        builder = IndexBuilder()
        
        # Mock the Swagger extraction to avoid real API calls
        with patch('index_builder.extract_text_from_swagger_sources') as mock_swagger:
            # Generate mock swagger documents
            mock_docs = [
                "# Test API v1.0.0\n\nDescription: A test API for validation\n\nGET /users - Get all users\nPOST /users - Create user\nGET /users/{id} - Get user by ID",
                "# User Definition\n\nProperties:\n- id: string\n- name: string\n- email: string\n\nUsed in: GET /users, POST /users, GET /users/{id}",
                "# API Authentication\n\nSchemes: https\nHost: api.example.com\nBase Path: /v1\n\nAll endpoints require authentication headers"
            ]
            mock_swagger.return_value = mock_docs
            
            logger.info("Building Swagger index (mocked)...")
            success = builder.build_swagger_index()
            
            logger.info(f"Index build {'successful' if success else 'failed'}")
            
            if success:
                logger.info(f"  Mock documents processed: {len(mock_docs)}")
                logger.info(f"  Documents transformed to chunks and embeddings")
                logger.info(f"  Stored in VectorStore collection: 'swagger'")
        
        return success
    
    except Exception as e:
        logger.error(f"✗ Test failed: {e}", exc_info=True)
        return False


def test_swagger_multiple_specs():
    """Test 4: Multiple Swagger Specs Processing"""
    print("\n" + "="*80)
    print("TEST 4: Multiple Swagger Specs ")
    print("="*80)
    
    try:
        from ingestion.Swagger_connector.swagger_connector_helpers import (
            extract_full_api_spec,
            render_api_to_text
        )
        
        logger.info("Testing multiple Swagger specifications...")
        
        # Create variations of swagger specs
        specs = {
            "Payment API": {
                **MOCK_SWAGGER_SPEC,
                "info": {
                    "title": "Payment API",
                    "version": "2.0.0",
                    "description": "Payment processing"
                },
                "paths": {
                    "/payments": {
                        "post": {
                            "summary": "Create payment",
                            "description": "Process a payment",
                            "responses": {"200": {"description": "Payment processed"}}
                        }
                    }
                }
            },
            "Auth API": {
                **MOCK_SWAGGER_SPEC,
                "info": {
                    "title": "Auth API",
                    "version": "1.5.0",
                    "description": "Authentication service"
                },
                "paths": {
                    "/auth/login": {
                        "post": {
                            "summary": "Login",
                            "description": "User login endpoint",
                            "responses": {"200": {"description": "Login successful"}}
                        }
                    },
                    "/auth/logout": {
                        "post": {
                            "summary": "Logout",
                            "description": "User logout endpoint",
                            "responses": {"200": {"description": "Logout successful"}}
                        }
                    }
                }
            }
        }
        
        total_docs = 0
        
        for api_name, spec in specs.items():
            logger.info(f"\nProcessing {api_name}...")
            
            # Extract and render
            api_info = extract_full_api_spec(spec)
            docs = render_api_to_text(api_info)
            
            logger.info(f"  {api_name}: {len(docs)} documents")
            total_docs += len(docs)
        
        logger.info(f"\nTotal documents from multiple specs: {total_docs}")
        
        return total_docs > 0
    
    except Exception as e:
        logger.error(f"✗ Test failed: {e}", exc_info=True)
        return False


# ============================================================================
# TEST RUNNER
# ============================================================================

def run_all_tests():
    """Run all Swagger connector tests in sequence"""
    print("\n" + "█" * 80)
    print("█" + " " * 78 + "█")
    print("█  SWAGGER CONNECTOR TEST SUITE " + " " * 45 + "█")
    print("█" + " " * 78 + "█")
    print("█" * 80)
    
    tests = [
        ("Swagger Helpers", test_swagger_helpers),
        ("Swagger Connector", test_swagger_connector),
        ("Swagger + Index Builder", test_swagger_index_builder),
        ("Multiple Swagger Specs", test_swagger_multiple_specs),
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
    print("TEST SUMMARY")
    print("="*80)
    
    for name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"{status}: {name}")
    
    total_passed = sum(1 for r in results.values() if r)
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    print("="*80 + "\n")
    
    return total_passed == total_tests


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
