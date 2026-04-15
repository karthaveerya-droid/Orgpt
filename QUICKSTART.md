# 🚀 OrgGPT - Quick Reference Card

## ⚡ 10-Second Setup (WITHOUT Docker)

```bash
# 1. Activate environment
source .venv/bin/activate

# 2. Start application (uses local ChromaDB automatically)
uvicorn app_api:app --reload --port 8001
```

**Open:** http://localhost:8001/

---

## 🐳 30-Second Setup (WITH Docker)

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

**Local Mode (No Docker):**
```bash
# Start application (ChromaDB runs embedded)
uvicorn app_api:app --reload --port 8001

# Start in background
nohup uvicorn app_api:app --port 8001 > server.log 2>&1 &
```

**Docker Mode:**
```bash
# Start ChromaDB container
docker-compose up -d chromadb

# Configure Docker mode
export CHROMA_CLIENT_TYPE=http

# Start application
uvicorn app_api:app --reload --port 8001
```

### Build Indexes

```bash
# Datadog Catalog POC (no API keys)
python index_builder.py datadog_poc

# Datadog SLO POC (no API keys)
python index_builder.py datadog_slo_poc

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
| "Could not connect to Chroma server" | Using Docker? Run `docker-compose up -d chromadb`. Using local? Unset `CHROMA_CLIENT_TYPE` or set to `persistent` |
| No results | `python index_builder.py datadog_catalog_poc` or `python index_builder.py datadog_slo_poc` |
| 500 error | Check `tail -f server.log` |
| Slow queries (Docker) | Restart: `docker-compose restart chromadb` |
| Slow queries (Local) | Delete `chroma_db/` and rebuild with POC command |
| Datadog API errors | Check API/APP keys in `.env` or use POC mode (`datadog_catalog_poc` / `datadog_slo_poc`) |

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

**Datadog Catalog:**
- "What services are in the catalog?"
- "List all deployed services"

**Datadog SLO:**
- "What SLOs do we have?"
- "Show me scheduled maintenance windows"
- "What are the availability targets?"

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
✅ **Works with or without Docker** (local ChromaDB embedded)  
✅ GPT-4 powered responses  
✅ Persistent data storage  

---

## 🔧 Configuration Modes

### Local Mode (Default - No Docker Required)
```bash
# In .env file:
CHROMA_CLIENT_TYPE=persistent

# Or just don't set it - defaults to persistent
```
- ✅ Faster startup
- ✅ No Docker installation needed
- ✅ Data stored in `./chroma_db/`
- ✅ Perfect for development

### Docker Mode (Production)
```bash
# In .env file:
CHROMA_CLIENT_TYPE=http
CHROMA_HOST=localhost
CHROMA_PORT=8000
```
- ✅ Better for production
- ✅ Easier to scale
- ✅ Data stored in `./chroma_data/`
- ✅ Isolated from application

---
