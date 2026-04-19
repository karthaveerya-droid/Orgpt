# 🚀 OrgGPT - Quick Start Guide

> **Unified Knowledge Base**: All data sources (Swagger + Datadog Catalog + Datadog SLOs) in one place!

---

## ⚡️ First-Time Setup (5 Minutes)

### 1. Configure Environment

```bash
# Copy the environment template
cp .env.template .env

# Edit .env and add your API keys
nano .env  # or use your preferred editor
```

**Required values in `.env`:**
```bash
OPENAI_API_KEY=your_actual_api_key_here
LLM_MODEL=llama-3.3-70b-versatile  # or gpt-4o, gpt-4o-mini, etc.
```

**Optional (for live Datadog data):**
```bash
DD_API_KEY=your_datadog_api_key
DD_APP_KEY=your_datadog_app_key
```

### 2. Build Unified Index

```bash
# Activate environment
source .venv/bin/activate

# Build unified knowledge base (POC mode - no API keys needed)
python3 index_builder.py
```

**Expected output:**
```
✓ IndexBuilder initialized (collection: 'unified_knowledge')
✓ Registered connector: swagger
✓ Registered connector: datadog_catalog
✓ Registered connector: datadog_slo
...
✅ Unified index 'unified_knowledge' built successfully
```

### 3. Start Application

```bash
# Start server
uvicorn app_api:app --reload --port 8001
```

### 4. Open Browser

**Go to:** http://localhost:8001/

You're ready to ask questions! 🎉

---

## ⚡ Quick Start (Without Docker)

```bash
# 1. Activate environment
source .venv/bin/activate

# 2. Build index (first time only)
python3 index_builder.py

# 3. Start application
uvicorn app_api:app --reload --port 8001
```

**Open:** http://localhost:8001/

✅ **No Docker needed!** Uses local ChromaDB automatically.

---

## 🐳 With Docker (Production)

```bash
# 1. Activate environment
source .venv/bin/activate

# 2. Start ChromaDB
docker-compose up -d chromadb

# 3. Configure Docker mode
export CHROMA_CLIENT_TYPE=http

# 4. Build index (first time only)
python3 index_builder.py

# 5. Start application
uvicorn app_api:app --reload --port 8001
```

**Open:** http://localhost:8001/

---

## 📋 Essential Commands

### Build Unified Index

```bash
# Build unified knowledge base (default - POC mode, no API keys needed)
python3 index_builder.py

# Build with API mode (requires Datadog API keys)
python3 index_builder.py unified

# Build with POC mode (explicit)
python3 index_builder.py unified --poc
```

**What gets indexed:**
- ✅ Swagger API documentation
- ✅ Datadog Catalog entities
- ✅ Datadog SLO data
- ✅ All in ONE collection: `unified_knowledge`

### Start Application

**Development Mode:**
```bash
# Start with auto-reload
uvicorn app_api:app --reload --port 8001
```

**Production Mode:**
```bash
# Start in background
nohup uvicorn app_api:app --host 0.0.0.0 --port 8001 > server.log 2>&1 &
```

**With Docker:**
```bash
# 1. Start ChromaDB
docker-compose up -d chromadb

# 2. Set Docker mode
export CHROMA_CLIENT_TYPE=http

# 3. Start app
uvicorn app_api:app --reload --port 8001
```

### Monitor & Verify

```bash
# Open monitoring dashboard
open http://localhost:8001/monitor

# Check health
curl http://localhost:8001/health

# Verify collection
python3 -c "
from vector_store.store import VectorStore
vs = VectorStore('unified_knowledge')
print(f'✅ Collection has {vs.collection.count()} documents')
"

# View Docker logs (if using Docker)
docker-compose logs -f chromadb
```

### Stop Services

```bash
# Stop application (Ctrl+C in terminal, or)
pkill -f "uvicorn app_api"

# Stop ChromaDB (if using Docker)
docker-compose stop chromadb

# Stop everything (Docker)
docker-compose down
```

---

## 🔗 Important URLs

| URL | Description |
|-----|-------------|
| http://localhost:8001/ | **Main Chat Interface** - Ask questions here! |
| http://localhost:8001/monitor | System Monitor - View DB status |
| http://localhost:8001/health | Health Check API |
| http://localhost:8000 | ChromaDB Server (if using Docker) |

---

## 🐛 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| **"Could not connect to Chroma server"** | Using Docker? Run `docker-compose up -d chromadb`. Using local? Unset `CHROMA_CLIENT_TYPE` |
| **No results / empty collection** | Run `python3 index_builder.py` to build the unified index |
| **"Collection not found"** | Build index first: `python3 index_builder.py` |
| **500 error** | Check logs: `tail -f server.log` or check terminal output |
| **Slow queries (Docker)** | Restart: `docker-compose restart chromadb` |
| **Slow queries (Local)** | Delete `chroma_db/` folder and rebuild: `python3 index_builder.py` |
| **Datadog API errors** | Check API/APP keys in `.env` or use POC mode (default) |
| **"LLM_MODEL must be set"** | Add `LLM_MODEL=llama-3.3-70b-versatile` to `.env` file |

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

**Try asking these questions in the web interface:**

**About APIs:**
- "What endpoints are available?"
- "How do I authenticate to the API?"
- "Show me all POST endpoints"
- "What's the rate limiting policy?"

**About Services:**
- "What services are in the catalog?"
- "List all deployed services"
- "What microservices do we have?"

**About SLOs:**
- "What SLOs do we have?"
- "Show me scheduled maintenance windows"
- "What are the availability targets?"
- "What's our uptime SLO?"

**General:**
- "What's in this knowledge base?"
- "Tell me about the architecture"
- "What documentation is available?"

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

✅ **Unified Knowledge Base** - One collection for all data sources  
✅ **Multi-source** - Swagger + Datadog Catalog + Datadog SLOs  
✅ **POC mode** - Demo without API keys  
✅ **No Docker required** - Works with local ChromaDB  
✅ **LLM powered** - GPT-4 or Llama models  
✅ **Real-time monitoring** - Web dashboard included  
✅ **Persistent storage** - Data saved locally or in Docker  
✅ **Simple API** - One endpoint for all queries  

---

## 🔧 Configuration Modes

### Local Mode (Default - Recommended for Development)
```bash
# In .env file (or just don't set these):
CHROMA_CLIENT_TYPE=persistent
CHROMA_PATH=./chroma_db
```

**Benefits:**
- ✅ Faster startup
- ✅ No Docker required
- ✅ Data stored in `./chroma_db/`
- ✅ Perfect for development

### Docker Mode (Recommended for Production)
```bash
# 1. Start ChromaDB container
docker-compose up -d chromadb

# 2. Set in .env file:
CHROMA_CLIENT_TYPE=http
CHROMA_HOST=localhost
CHROMA_PORT=8000
```

**Benefits:**
- ✅ Better for production
- ✅ Easier to scale
- ✅ Data stored in `./chroma_data/`
- ✅ Isolated from application
- ✅ Can be shared across multiple apps

---

## 🔧 Environment Configuration

### Available LLM Models

**Groq Models (Fast, Free Tier Available)**
- `llama-3.3-70b-versatile` - Latest Llama model
- `llama-3.1-70b-versatile` - Stable Llama model
- `mixtral-8x7b-32768` - Large context window

**OpenAI Models (Paid)**
- `gpt-4o` - Latest GPT-4 Omni
- `gpt-4o-mini` - Cost-effective GPT-4
- `gpt-4-turbo` - High performance
- `gpt-3.5-turbo` - Budget option

### Switching Models

Just change the `LLM_MODEL` value in your `.env` file and restart:

```bash
# Switch to GPT-4 Omni
LLM_MODEL=gpt-4o

# Switch to Llama 3.3
LLM_MODEL=llama-3.3-70b-versatile

# Switch to budget option
LLM_MODEL=gpt-4o-mini
```

### Environment Variables Reference

**ChromaDB:**
- `CHROMA_CLIENT_TYPE`: `persistent` (local) or `http` (Docker)
- `CHROMA_PATH`: Path for local DB (default: `./chroma_db`)
- `CHROMA_HOST`: Host for HTTP mode (default: `localhost`)
- `CHROMA_PORT`: Port for HTTP mode (default: `8000`)

**LLM (Required):**
- `OPENAI_API_KEY`: Your API key for Groq/OpenAI
- `LLM_MODEL`: Model name (no default - must be set)

**Datadog (Optional):**
- `DD_API_KEY`: Datadog API key
- `DD_APP_KEY`: Datadog application key
- `DD_SITE`: Datadog site (default: `datadoghq.com`)
- `DATADOG_POC_ENABLED`: Enable POC mode (default: `true`)

**Application:**
- `HOST`: Server host (default: `0.0.0.0`)
- `PORT`: Server port (default: `8001`)
- `ENVIRONMENT`: `development`, `staging`, or `production`
- `DEBUG`: Enable debug mode (default: `true`)

### Example Configurations

**Local Development (No Docker):**
```bash
CHROMA_CLIENT_TYPE=persistent
CHROMA_PATH=./chroma_db
OPENAI_API_KEY=sk-proj-...
LLM_MODEL=llama-3.3-70b-versatile
```

**Docker Deployment:**
```bash
CHROMA_CLIENT_TYPE=http
CHROMA_HOST=localhost
CHROMA_PORT=8000
OPENAI_API_KEY=sk-proj-...
LLM_MODEL=gpt-4o-mini
```

**With Live Datadog Integration:**
```bash
OPENAI_API_KEY=sk-proj-...
LLM_MODEL=llama-3.3-70b-versatile
DD_API_KEY=your_dd_api_key
DD_APP_KEY=your_dd_app_key
DATADOG_POC_ENABLED=false
```

**POC/Demo Mode (No Datadog API Keys):**
```bash
OPENAI_API_KEY=sk-proj-...
LLM_MODEL=llama-3.3-70b-versatile
DATADOG_POC_ENABLED=true
# No DD_API_KEY or DD_APP_KEY needed!
```

### Common Issues

**Error: "LLM_MODEL must be set in environment variables"**
- **Solution**: Add `LLM_MODEL=your-model-name` to your `.env` file

**Error: "API key not found"**
- **Solution**: Add `OPENAI_API_KEY=your-api-key` to your `.env` file

**ChromaDB connection issues**
- **Solution**: Check `CHROMA_CLIENT_TYPE` matches your setup:
  - Use `persistent` for local development
  - Use `http` when running with Docker

### Security Note

⚠️ **Never commit your `.env` file to git!** It contains sensitive API keys and is already in `.gitignore`.

---

## 🚀 Complete Workflow

### First Time Setup:
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.template .env
nano .env  # Add your OPENAI_API_KEY and LLM_MODEL

# 3. Activate virtual environment
source .venv/bin/activate

# 4. Build unified index
python3 index_builder.py

# 5. Start application
uvicorn app_api:app --reload --port 8001

# 6. Open browser
open http://localhost:8001
```

### Daily Use:
```bash
# 1. Activate environment
source .venv/bin/activate

# 2. Start app (if index already built)
uvicorn app_api:app --reload --port 8001

# 3. Open browser
open http://localhost:8001
```

### Rebuild Index (when data changes):
```bash
# Stop the app (Ctrl+C)

# Rebuild index
python3 index_builder.py

# Restart app
uvicorn app_api:app --reload --port 8001
```

---

## 📊 What's in the Unified Collection?

When you run `python3 index_builder.py`, it creates a **single collection** called `unified_knowledge` containing:

| Data Source | Content | Document Count |
|-------------|---------|----------------|
| **Swagger** | API endpoints, parameters, responses | ~100+ |
| **Datadog Catalog** | Service entities, metadata | ~2 (POC) |
| **Datadog SLO** | SLO definitions, targets, corrections | Variable |

**Total:** All sources searchable from one interface! 🎯

---

## 🆘 Need Help?

**Common Commands:**
```bash
# Check if index exists
python3 -c "from vector_store.store import VectorStore; vs = VectorStore('unified_knowledge'); print(vs.collection.count())"

# View available commands
python3 index_builder.py --help

# Check health
curl http://localhost:8001/health

# View logs
tail -f server.log
```

**Still having issues?** Check the [README.md](README.md) for detailed troubleshooting.

---
