#!/usr/bin/env python3
"""
Migrate data from local PersistentClient to Docker HttpClient
"""
import chromadb
import os
from pathlib import Path

def migrate_to_docker():
    """Migrate all collections from local to Docker ChromaDB"""
    
    # Connect to local persistent ChromaDB
    local_db_path = Path(__file__).parent / "chroma_db"
    
    if not local_db_path.exists():
        print("No local ChromaDB found at:", local_db_path)
        print("   Nothing to migrate.")
        return
    
    print(f"Connecting to local ChromaDB at: {local_db_path}")
    local_client = chromadb.PersistentClient(path=str(local_db_path))
    
    # Connect to Docker HTTP ChromaDB
    print("Connecting to Docker ChromaDB at: localhost:8000")
    docker_client = chromadb.HttpClient(host="localhost", port=8000)
    
    # Get all collections from local
    local_collections = local_client.list_collections()
    
    if not local_collections:
        print(" No collections found in local ChromaDB")
        return
    
    print(f"\nFound {len(local_collections)} collection(s) to migrate:\n")
    
    # Migrate each collection
    for collection in local_collections:
        collection_name = collection.name
        print(f"Migrating collection: '{collection_name}'")
        
        try:
            # Get all data from local collection
            data = collection.get(
                include=["documents", "embeddings", "metadatas"]
            )
            
            num_docs = len(data['ids'])
            print(f"   📥 Retrieved {num_docs} documents")
            
            if num_docs == 0:
                print(f"    Collection '{collection_name}' is empty, skipping")
                continue
            
            # Create or get collection in Docker
            docker_collection = docker_client.get_or_create_collection(collection_name)
            
            # Check if already has data
            existing_count = docker_collection.count()
            if existing_count > 0:
                print(f"    Docker collection already has {existing_count} documents")
                response = input(f"   Do you want to overwrite? (y/N): ").lower()
                if response != 'y':
                    print(f"   ⏭️  Skipping '{collection_name}'")
                    continue
                
                # Delete and recreate collection
                docker_client.delete_collection(collection_name)
                docker_collection = docker_client.create_collection(collection_name)
            
            # Insert data into Docker collection
            docker_collection.add(
                ids=data['ids'],
                documents=data['documents'],
                embeddings=data['embeddings'],
                metadatas=data['metadatas']
            )
            
            # Verify
            new_count = docker_collection.count()
            print(f"   Successfully migrated {new_count} documents")
            
        except Exception as e:
            print(f"   Error migrating '{collection_name}': {e}")
            continue
    
    print("\n" + "="*60)
    print("Migration Summary:")
    print("="*60)
    
    docker_collections = docker_client.list_collections()
    for col in docker_collections:
        count = col.count()
        print(f"   {col.name}: {count} documents")
    
    print("\nMigration complete!")
    print("\nNext steps:")
    print("   1. Configure app to use Docker:")
    print("      export CHROMA_CLIENT_TYPE=http")
    print("   2. Start your application:")
    print("      uvicorn app_api:app --reload --port 8001")
    print("   3. Test in browser: http://localhost:8001/")


if __name__ == "__main__":
    print("=" * 60)
    print("ChromaDB Migration: Local → Docker")
    print("=" * 60)
    print()
    
    try:
        migrate_to_docker()
    except KeyboardInterrupt:
        print("\n\n Migration cancelled by user")
    except Exception as e:
        print(f"\nMigration failed: {e}")
        import traceback
        traceback.print_exc()
