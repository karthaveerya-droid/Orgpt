"""
main.py
=======

Usage:
    python main.py                    # Build unified index and query
    python main.py --poc              # Use POC mode (no API keys)
    python main.py --query "..."      # Query only (skip build)
"""

from index_builder import IndexBuilder
from ingestion.Swagger_connector.swagger_connector import SwaggerConnector
from ingestion.Datadog_connector import DatadogCatalogConnector, DatadogSLOConnector
from retrieval.rag_engine import RAGEngine
from llm.llm_layer import LLMHandler
import sys


def build_unified_index(poc_mode: bool = True):
    """
    Build unified index with all data sources.
    
    Args:
        poc_mode: Use POC mode (JSON files) if True, API mode if False
    """
    print("\n" + "="*80)
    print(" Building Unified Knowledge Base")
    print("="*80 + "\n")
    
    builder = IndexBuilder("unified_knowledge")
    
    # Register all connectors
    builder.register_connector(SwaggerConnector())
    builder.register_connector(DatadogCatalogConnector(poc_mode=poc_mode))
    builder.register_connector(DatadogSLOConnector(poc_mode=poc_mode))
    
    # Build unified index
    success = builder.build_unified_index()
    
    if success:
        print("\n Unified knowledge base ready!")
    else:
        print("\n Failed to build knowledge base")
        return False
    
    return True


def query_orgpt(query: str, collection: str = "unified_knowledge"):
    """
    Query the unified knowledge base.
    
    Args:
        query: User query
        collection: Collection name (default: unified "unified_knowledge")
    """
    print(f"\n Query: {query}")
    print(f" Searching collection: {collection}\n")
    
    # Retrieve relevant context
    rag = RAGEngine(collection_name=collection)
    retrieved = rag.retrieve(query, top_k=5)
    context = "\n".join(retrieved["documents"][0])
    
    print(f" Retrieved {len(retrieved['documents'][0])} relevant chunks")
    
    # Generate answer with LLM
    llm = LLMHandler()
    answer = llm.ask(query, context)
    
    print("\n" + "="*80)
    print(" Answer:")
    print("="*80)
    print(answer)
    print("="*80 + "\n")
    
    return answer


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="OrgGPT Unified Knowledge Base")
    parser.add_argument("--poc", action="store_true", help="Use POC mode (JSON files, no API keys)")
    parser.add_argument("--query", type=str, help="Query string (skip build)")
    parser.add_argument("--collection", type=str, default="orgpt_knowledge", help="Collection name")
    
    args = parser.parse_args()
    
    # Build index if not query-only mode
    if not args.query:
        success = build_unified_index(poc_mode=args.poc)
        if not success:
            sys.exit(1)
    
    # Example queries
    if args.query:
        query_orgpt(args.query, collection=args.collection)
    else:
        # Demo queries
        print("\n" + "="*80)
        print(" Demo Queries")
        print("="*80)
        
        queries = [
            "What APIs are available for user management?",
            "Tell me about our service catalog",
            "What are the SLO targets for critical services?"
        ]
        
        for q in queries:
            query_orgpt(q, collection=args.collection)
            print("\n")

