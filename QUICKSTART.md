# 🚀 OrgGPT - Quick Reference Card

## ⚡️ First-Time Setup

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

---

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
