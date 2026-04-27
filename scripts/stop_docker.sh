#!/bin/bash
# Script to stop ChromaDB Docker container

echo "🛑 Stopping ChromaDB Docker container..."

# Stop ChromaDB
docker-compose stop chromadb

echo "✅ ChromaDB stopped"
echo ""
echo "💡 To start again: ./scripts/start_docker.sh"
echo "🗑️  To remove completely: docker-compose down"
echo "⚠️  To remove with data: docker-compose down -v"
