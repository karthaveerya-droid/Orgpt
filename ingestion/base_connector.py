"""
base_connector.py
=================
Abstract base class for all data source connectors.

This module implements the Strategy Pattern and Template Method Pattern
to provide a consistent interface for all data sources.

SOLID Principles Applied:
- Single Responsibility: Each connector handles only its data source
- Open/Closed: Open for extension (new connectors), closed for modification
- Liskov Substitution: All connectors are interchangeable
- Interface Segregation: Minimal, focused interface
- Dependency Inversion: Depend on abstraction, not concrete implementations

Design Patterns:
- Strategy Pattern: Each connector is a strategy for data extraction
- Template Method: Defines skeleton of extraction algorithm

Usage:
    class MyConnector(DataSourceConnector):
        def extract_documents(self) -> List[str]:
            # Extract logic here
            return documents
        
        def get_source_name(self) -> str:
            return "my_source"
    
    # Use with IndexBuilder
    builder = IndexBuilder()
    builder.register_connector(MyConnector())
    builder.build_unified_index()
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class DataSourceConnector(ABC):
    """
    Abstract base class for all data source connectors.
    
    This interface defines the contract that all data source connectors
    must implement.
    
    Responsibilities:
    - Extract documents from a specific data source
    - Provide source identification
    - Validate extracted data
    - Provide metadata about the source
    
    Examples of implementations:
    - SwaggerConnector: Extracts API documentation
    - DatadogCatalogConnector: Extracts service catalog
    - DatadogSLOConnector: Extracts SLO definitions
    - DocumentConnector: Extracts project documents
    """
    
    @abstractmethod
    def extract_documents(self) -> List[str]:
        """
        Extract and transform documents from this data source.
        
        This is the main method that each connector must implement.
        It should:
        1. Connect to the data source
        2. Extract raw data
        3. Transform to text format suitable for RAG
        4. Return list of text documents
        
        Returns:
            List of text documents ready for chunking and embedding
            
        Raises:
            Exception: If extraction fails
            
        Example:
            >>> connector = SwaggerConnector()
            >>> docs = connector.extract_documents()
            >>> len(docs)
            42
        """
        pass
    
    @abstractmethod
    def get_source_name(self) -> str:
        """
        Get the unique identifier for this data source.
        
        This name is used for:
        - Metadata tagging
        - Filtering results by source
        - Logging and debugging
        
        Returns:
            Unique source identifier (lowercase, no spaces)
            
        Example:
            >>> connector = SwaggerConnector()
            >>> connector.get_source_name()
            'swagger'
        """
        pass
    
    def get_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about this data source.
        
        Metadata is attached to each document chunk and can be used for:
        - Filtering search results
        - Displaying source information to users
        - Analytics and monitoring
        
        Default implementation provides basic metadata.
        Subclasses can override to add source-specific metadata.
        
        Returns:
            Dictionary with source metadata
            
        Example:
            >>> connector = SwaggerConnector()
            >>> connector.get_metadata()
            {'source': 'swagger', 'connector_version': '1.0'}
        """
        return {
            "source": self.get_source_name(),
            "connector_version": "1.0",
            "connector_type": self.__class__.__name__,
        }
    
    def validate_documents(self, documents: List[str]) -> bool:
        """
        Validate extracted documents.
        
        Performs basic validation to ensure documents are suitable
        for indexing. Can be overridden for source-specific validation.
        
        Default checks:
        - Documents list is not empty
        - All items are strings
        - Strings are not empty
        
        Args:
            documents: List of extracted documents
            
        Returns:
            True if valid, False otherwise
            
        Example:
            >>> connector = SwaggerConnector()
            >>> docs = connector.extract_documents()
            >>> connector.validate_documents(docs)
            True
        """
        if not documents:
            logger.warning(f"{self.get_source_name()}: No documents extracted")
            return False
        
        if not isinstance(documents, list):
            logger.error(f"{self.get_source_name()}: Documents must be a list")
            return False
        
        if not all(isinstance(doc, str) for doc in documents):
            logger.error(f"{self.get_source_name()}: All documents must be strings")
            return False
        
        if not all(doc.strip() for doc in documents):
            logger.warning(f"{self.get_source_name()}: Some documents are empty")
            return False
        
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the extraction.
        
        Can be overridden to provide connector-specific stats.
        
        Returns:
            Dictionary with statistics
        """
        return {
            "source": self.get_source_name(),
            "status": "ready",
        }
    
    def __repr__(self) -> str:
        """String representation of the connector."""
        return f"{self.__class__.__name__}(source='{self.get_source_name()}')"
    
    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"DataSourceConnector: {self.get_source_name()}"
