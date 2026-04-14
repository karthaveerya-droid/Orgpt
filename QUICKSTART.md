# 🚀 OrgGPT - Quick Reference Card

## ⚡ 30-Second Setup

```bash
# 1. Activate environment
source .venv/bin/activate

# 2. Start ChromaDB
docker-compose up -d chromadb

# 3. Configure environment
export CHROMA_CLIENT_TYPE=http

# 4. Start application
uvicorn app_api:app --reload --port 8001
```

**Open:** http://localhost:8001/

---

## 📋 Essential Commands

### Start Services

```bash
# Start ChromaDB
docker-compose up -d chromadb

# Start application
uvicorn app_api:app --reload --port 8001

# Start in background
nohup uvicorn app_api:app --port 8001 > server.log 2>&1 &
```

### Build Indexes

```bash
# POC mode (no API keys)
python index_builder.py datadog_poc

# Swagger documentation
python index_builder.py swagger

# All sources
python index_builder.py
```

### Monitor System

```bash
# Web monitoring
open http://localhost:8001/monitor

# CLI monitoring
python monitor_chromadb.py

# Docker status
docker-compose ps

# View logs
docker-compose logs -f chromadb
```

### Stop Services

```bash
# Stop application
pkill -f "uvicorn app_api"

# Stop ChromaDB
docker-compose stop chromadb

# Stop everything
docker-compose down
```

---

## 🔗 Important URLs

| URL | Description |
|-----|-------------|
| http://localhost:8001/ | Main interface |
| http://localhost:8001/monitor | System monitor |
| http://localhost:8001/health | Health check |
| http://localhost:8000 | ChromaDB server |

---

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| Connection refused | `docker-compose up -d chromadb` |
| No results | `python index_builder.py datadog_poc` |
| 500 error | Check `tail -f server.log` |
| Slow queries | Restart: `docker-compose restart chromadb` |

---

## 📊 System Status Check

```bash
# Quick health check
curl http://localhost:8001/health && \
curl http://localhost:8000/api/v1/heartbeat && \
echo "✅ All systems operational"
```

---

## 💡 Example Queries

**Swagger:**
- "What endpoints are available?"
- "How do I authenticate?"
- "Show me all POST endpoints"

**Datadog:**
- "What services are in the catalog?"
- "List all deployed services"

---

## 📁 Project Structure

```
Orgpt/
├── app_api.py              # Main application
├── index_builder.py        # Data indexing
├── docker-compose.yml      # ChromaDB setup
├── requirements.txt        # Dependencies
├── .env                    # Configuration
├── templates/              # Web interfaces
├── vector_store/           # DB layer
├── retrieval/              # RAG engine
├── ingestion/              # Data connectors
└── processing/             # NLP pipeline
```

---

## 🎯 Key Features

✅ Multi-source indexing (Swagger, Datadog, Docs)  
✅ POC mode (no API keys needed)  
✅ Real-time monitoring dashboard  
✅ Docker-based ChromaDB  
✅ GPT-4 powered responses  
✅ Persistent data storage  

---
