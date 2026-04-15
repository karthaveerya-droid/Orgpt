#!/usr/bin/env python3
"""
ChromaDB Connection Monitor
Shows real-time status of ChromaDB collections and connections
"""
import chromadb
import os
from datetime import datetime
import json

def print_separator(char="=", length=80):
    print(char * length)

def print_header(text):
    print_separator()
    print(f"  {text}")
    print_separator()

def get_chroma_info():
    """Get comprehensive ChromaDB information"""
    
    # Try HTTP Client (Docker)
    print_header("DOCKER CHROMADB CONNECTION")
    
    try:
        host = os.getenv("CHROMA_HOST", "localhost")
        port = int(os.getenv("CHROMA_PORT", "8000"))
        
        print(f"📡 Connecting to: {host}:{port}")
        client = chromadb.HttpClient(host=host, port=port)
        
        # Test connection with heartbeat
        heartbeat = client.heartbeat()
        print(f"Connection: SUCCESS")
        print(f"💓 Heartbeat: {heartbeat}")
        
        # Get collections
        collections = client.list_collections()
        print(f"\nCollections: {len(collections)} found\n")
        
        total_docs = 0
        for i, col in enumerate(collections, 1):
            count = col.count()
            total_docs += count
            
            print(f"{i}. Collection: '{col.name}'")
            print(f"   └─ Documents: {count:,}")
            
            # Get sample metadata if available
            if count > 0:
                sample = col.peek(limit=1)
                if sample and sample.get('metadatas') and sample['metadatas']:
                    print(f"   └─ Sample metadata: {sample['metadatas'][0]}")
            print()
        
        print_separator("-")
        print(f"Total Documents Across All Collections: {total_docs:,}")
        print_separator("-")
        
        return True, client, collections
        
    except Exception as e:
        print(f"Connection: FAILED")
        print(f"   Error: {e}\n")
        
        # Try local persistent client
        print_header("💾 LOCAL CHROMADB CONNECTION")
        
        try:
            db_path = "./chroma_db"
            print(f"Connecting to: {db_path}")
            
            client = chromadb.PersistentClient(path=db_path)
            collections = client.list_collections()
            
            print(f"Connection: SUCCESS")
            print(f"\nCollections: {len(collections)} found\n")
            
            total_docs = 0
            for i, col in enumerate(collections, 1):
                count = col.count()
                total_docs += count
                print(f"{i}. Collection: '{col.name}'")
                print(f"   └─ Documents: {count:,}\n")
            
            print_separator("-")
            print(f"Total Documents: {total_docs:,}")
            print_separator("-")
            
            return True, client, collections
            
        except Exception as e2:
            print(f"Connection: FAILED")
            print(f"   Error: {e2}\n")
            return False, None, None

def query_collection(client, collection_name, query_text):
    """Test query on a collection"""
    print_header(f"QUERY TEST: {collection_name}")
    
    try:
        collection = client.get_collection(collection_name)
        
        # Simple search with the query text
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        query_embedding = model.encode(query_text).tolist()
        
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=3
        )
        
        print(f"Query: '{query_text}'")
        print(f"\nResults: {len(results['ids'][0])} documents found\n")
        
        for i, (doc_id, doc, distance) in enumerate(zip(
            results['ids'][0],
            results['documents'][0],
            results['distances'][0]
        ), 1):
            print(f"{i}. ID: {doc_id}")
            print(f"   Distance: {distance:.4f}")
            print(f"   Text: {doc[:200]}...")
            print()
        
        return True
        
    except Exception as e:
        print(f"Query failed: {e}")
        return False

def check_docker_status():
    """Check if Docker container is running"""
    print_header("DOCKER STATUS")
    
    import subprocess
    
    try:
        # Check if Docker is running
        result = subprocess.run(
            ["docker", "ps", "--filter", "name=orgpt-chromadb", "--format", "{{.Status}}"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0 and result.stdout.strip():
            status = result.stdout.strip()
            print(f"Container: orgpt-chromadb")
            print(f"Status: {status}")
            
            # Check if healthy
            if "healthy" in status.lower():
                print(f"Health: HEALTHY")
            elif "unhealthy" in status.lower():
                print(f"Health: UNHEALTHY (but may still work)")
            else:
                print(f"Health: STARTING")
            
            return True
        else:
            print("Container 'orgpt-chromadb' is not running")
            print("\nStart it with: docker-compose up -d chromadb")
            return False
            
    except FileNotFoundError:
        print("Docker is not installed or not in PATH")
        return False
    except Exception as e:
        print(f"Error checking Docker: {e}")
        return False

def main():
    """Main monitoring function"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "CHROMADB CONNECTION MONITOR" + " " * 31 + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    
    # Show timestamp
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"⏰ Timestamp: {now}\n")
    
    # Check Docker status first
    docker_running = check_docker_status()
    print()
    
    # Get ChromaDB info
    success, client, collections = get_chroma_info()
    
    if not success:
        print("\n" + "=" * 80)
        print("Could not connect to ChromaDB")
        print("=" * 80)
        print("\nTroubleshooting:")
        print("   1. Start Docker ChromaDB: docker-compose up -d chromadb")
        print("   2. Set environment: export CHROMA_CLIENT_TYPE=http")
        print("   3. Check logs: docker-compose logs chromadb")
        return
    
    # Interactive mode
    print("\n" + "=" * 80)
    print("Connection successful! What would you like to do?")
    print("=" * 80)
    print("\nOptions:")
    print("  1. Test a query")
    print("  2. Show detailed collection info")
    print("  3. Export connection info to JSON")
    print("  q. Quit")
    
    choice = input("\nYour choice: ").strip()
    
    if choice == "1":
        print("\nAvailable collections:")
        for i, col in enumerate(collections, 1):
            print(f"  {i}. {col.name}")
        
        col_num = input("\nSelect collection number: ").strip()
        query = input("Enter your query: ").strip()
        
        try:
            col_idx = int(col_num) - 1
            col_name = collections[col_idx].name
            query_collection(client, col_name, query)
        except (ValueError, IndexError):
            print("Invalid collection number")
    
    elif choice == "2":
        for col in collections:
            print_header(f"Collection: {col.name}")
            data = col.get(limit=5, include=["metadatas", "documents"])
            print(f"Total documents: {col.count()}")
            print(f"\nSample data (first 5):")
            for i, (doc_id, metadata) in enumerate(zip(data['ids'], data['metadatas']), 1):
                print(f"\n{i}. ID: {doc_id}")
                print(f"   Metadata: {metadata}")
    
    elif choice == "3":
        output = {
            "timestamp": now,
            "docker_running": docker_running,
            "connection_type": "http" if docker_running else "persistent",
            "collections": []
        }
        
        for col in collections:
            output["collections"].append({
                "name": col.name,
                "count": col.count()
            })
        
        filename = "chromadb_status.json"
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\nStatus exported to: {filename}")
    
    print("\n" + "=" * 80)
    print("Done!")
    print("=" * 80 + "\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
