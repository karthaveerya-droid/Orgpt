#!/bin/bash
# Script to start ChromaDB with Docker

echo "🐳 Starting ChromaDB Docker container..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose not found. Please install docker-compose."
    exit 1
fi

# Start ChromaDB
echo "📦 Starting ChromaDB service..."
docker-compose up -d chromadb

# Wait for ChromaDB to be ready
echo "⏳ Waiting for ChromaDB to be ready..."
max_attempts=30
attempt=0

while [ $attempt -lt $max_attempts ]; do
    if curl -s http://localhost:8000/api/v1/heartbeat > /dev/null 2>&1; then
        echo "✅ ChromaDB is ready!"
        break
    fi
    
    attempt=$((attempt + 1))
    echo "   Attempt $attempt/$max_attempts..."
    sleep 2
done

if [ $attempt -eq $max_attempts ]; then
    echo "❌ ChromaDB failed to start within expected time"
    echo "   Check logs with: docker-compose logs chromadb"
    exit 1
fi

# Show status
echo ""
echo "📊 ChromaDB Status:"
docker-compose ps chromadb

echo ""
echo "🔗 ChromaDB is available at: http://localhost:8000"
echo ""
echo "💡 Next steps:"
echo "   1. Configure environment: export CHROMA_CLIENT_TYPE=http"
echo "   2. Build indices: python index_builder.py datadog_poc"
echo "   3. Start app: uvicorn app_api:app --reload --port 8001"
echo ""
echo "📝 View logs: docker-compose logs -f chromadb"
echo "🛑 Stop: docker-compose stop chromadb"
