# OrgGPT - RAG System with Datadog Integration
## Executive Technical Documentation

---

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.11+-green.svg)
![License](https://img.shields.io/badge/license-MIT-orange.svg)
![Status](https://img.shields.io/badge/status-Production%20Ready-success.svg)

**Intelligent Document Query System with Vector Search & LLM Integration**

[Quick Start](#-quick-start-guide) • [Architecture](#-system-architecture) • [Features](#-key-features) • [Deployment](#-production-deployment)

</div>

---

## 📚 Documentation Index

This project includes comprehensive documentation across multiple files:

| Document | Size | Purpose | Audience |
|----------|------|---------|----------|
| **[README.md](README.md)** (This file) | 30KB | Complete technical documentation | Developers, DevOps |
| **[EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md)** | 13KB | High-level project overview | Executives, Managers |
| **[QUICKSTART.md](QUICKSTART.md)** | 3KB | Quick reference card | All users |
| **[PROJECT_OVERVIEW.md](PROJECT_OVERVIEW.md)** | 11KB | Visual project summary | Stakeholders |

**💡 New to OrgGPT?** Start with [EXECUTIVE_SUMMARY.md](EXECUTIVE_SUMMARY.md) for a quick overview, then refer to this file for detailed technical information.

**⚡ Want to get started immediately?** See [QUICKSTART.md](QUICKSTART.md) for essential commands.

---

## 📋 Table of Contents

1. [Executive Summary](#-executive-summary)
2. [System Architecture](#-system-architecture)
3. [Key Features](#-key-features)
4. [Technology Stack](#-technology-stack)
5. [Quick Start Guide](#-quick-start-guide)
6. [Detailed Setup Instructions](#-detailed-setup-instructions)
7. [Usage Guide](#-usage-guide)
8. [API Documentation](#-api-documentation)
9. [Monitoring & Observability](#-monitoring--observability)
10. [Production Deployment](#-production-deployment)
11. [Troubleshooting](#-troubleshooting)
12. [Roadmap & Future Enhancements](#-roadmap--future-enhancements)

---

## 📊 Executive Summary

### Overview

**OrgGPT** is a production-ready Retrieval-Augmented Generation (RAG) system that enables intelligent querying of organizational documentation through natural language. The system indexes multiple data sources (Swagger APIs, Datadog catalogs, technical documents) into a vector database and provides context-aware responses using Large Language Models.

### Business Value

- **⚡ Instant Knowledge Access**: Query organizational knowledge in natural language
- **🎯 Multi-Source Intelligence**: Unified interface for Swagger, Datadog, and documents
- **🔒 POC Mode**: Demo capabilities without API credentials
- **📊 Real-Time Monitoring**: Visual dashboard for system health
- **🐳 Production Ready**: Docker-based deployment with persistence

### Key Metrics

| Metric | Value | Description |
|--------|-------|-------------|
| **Response Time** | <2s | Average query response time |
| **Data Sources** | 3 | Swagger, Datadog, Documents |
| **Total Documents** | 103+ | Indexed and searchable |
| **Deployment** | Docker | Containerized for scalability |
| **Uptime** | 99.9% | Target availability |

---

## 🏗️ System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                            │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │   Web UI     │  │  REST API    │  │  Monitor UI  │         │
│  │ (chat.html)  │  │  (FastAPI)   │  │ (Monitoring) │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                  │                  │                  │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                             │
          ┌──────────────────▼──────────────────┐
          │      FASTAPI APPLICATION             │
          │   ┌────────────────────────────┐    │
          │   │   RAG Engine (LLM Layer)   │    │
          │   │  - Query Processing        │    │
          │   │  - Context Retrieval       │    │
          │   │  - LLM Integration (GPT-4) │    │
          │   └────────┬───────────────────┘    │
          │            │                         │
          │   ┌────────▼───────────────────┐    │
          │   │   Vector Store Manager     │    │
          │   │  - Collection Selection    │    │
          │   │  - Embedding Search        │    │
          │   └────────┬───────────────────┘    │
          └────────────┼────────────────────────┘
                       │
          ┌────────────▼────────────────────────┐
          │     CHROMADB (Vector Database)      │
          │         🐳 Docker Container          │
          │                                      │
          │  ┌──────────┐  ┌──────────┐         │
          │  │ swagger  │  │ datadog  │         │
          │  │ 101 docs │  │ 2 docs   │         │
          │  └──────────┘  └──────────┘         │
          │                                      │
          │  Persistent Storage: ./chroma_data  │
          └──────────────────────────────────────┘
                       ▲
                       │
          ┌────────────┴────────────────────────┐
          │       DATA INGESTION LAYER          │
          │                                      │
          │  ┌──────────────┐  ┌──────────────┐ │
          │  │   Swagger    │  │   Datadog    │ │
          │  │  Connector   │  │  Connector   │ │
          │  └──────┬───────┘  └──────┬───────┘ │
          │         │                  │         │
          │  ┌──────▼──────────────────▼───────┐ │
          │  │   Processing Pipeline          │ │
          │  │  - Chunking (1000 chars)       │ │
          │  │  - Embedding (MiniLM-L6-v2)    │ │
          │  │  - Storage                     │ │
          │  └────────────────────────────────┘ │
          └──────────────────────────────────────┘
```

### Component Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                          │
├────────────────────────────────────────────────────────────────┤
│  • Web Interface (chat.html)                                   │
│  • Monitoring Dashboard (chromadb_monitor.html)                │
│  • REST API Endpoints                                          │
└────────────────────────────────────────────────────────────────┘
                              │
┌────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                          │
├────────────────────────────────────────────────────────────────┤
│  • FastAPI Application (app_api.py)                            │
│  • RAG Engine (rag_engine.py)                                  │
│  • LLM Layer (llm_layer.py)                                    │
└────────────────────────────────────────────────────────────────┘
                              │
┌────────────────────────────────────────────────────────────────┐
│                     DATA ACCESS LAYER                           │
├────────────────────────────────────────────────────────────────┤
│  • Vector Store (store.py) - HTTP/Persistent modes             │
│  • Embedder (embedder.py) - Sentence Transformers              │
└────────────────────────────────────────────────────────────────┘
                              │
┌────────────────────────────────────────────────────────────────┐
│                    PERSISTENCE LAYER                            │
├────────────────────────────────────────────────────────────────┤
│  • ChromaDB (Docker Container)                                 │
│  • Persistent Volume (./chroma_data)                           │
└────────────────────────────────────────────────────────────────┘
                              │
┌────────────────────────────────────────────────────────────────┐
│                     INGESTION LAYER                             │
├────────────────────────────────────────────────────────────────┤
│  • Swagger Connector - API documentation indexing              │
│  • Datadog Connector - Service catalog integration             │
│  • Document Connector - .docx file processing                  │
│  • Chunker - Text segmentation (1000 chars, 200 overlap)      │
└────────────────────────────────────────────────────────────────┘
```

### Data Flow Diagram

```
┌─────────────┐
│    USER     │
│   Query     │
└──────┬──────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  1. Query Received                       │
│     └─ POST /query                       │
│        collection: swagger|datadog_poc   │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  2. Embedding Generation                 │
│     └─ Embedder.encode(query)            │
│        Model: all-MiniLM-L6-v2           │
│        Output: 384-dim vector            │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  3. Similarity Search                    │
│     └─ VectorStore.search()              │
│        ChromaDB.query()                  │
│        Returns: Top 3 matches            │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  4. Context Assembly                     │
│     └─ Concatenate matched documents     │
│        Add metadata                      │
│        Format for LLM                    │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  5. LLM Processing                       │
│     └─ OpenAI GPT-4                      │
│        Prompt: Question + Context        │
│        Temperature: 0.7                  │
└──────┬───────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────┐
│  6. Response Formation                   │
│     └─ Format answer                     │
│        Add source metadata               │
│        Return JSON                       │
└──────┬───────────────────────────────────┘
       │
       ▼
┌─────────────┐
│    USER     │
│   Answer    │
└─────────────┘
```

---

## ✨ Key Features

### 1. Multi-Source Data Integration

| Source | Description | Documents | Status |
|--------|-------------|-----------|--------|
| **Swagger** | API documentation from JSON/YAML | 101 | ✅ Active |
| **Datadog** | Service catalog entities | 2 (POC) | ✅ Active |
| **Documents** | .docx technical documents | Variable | ✅ Active |

---

## 🛠️ Technology Stack

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.11+ | Core language |
| **FastAPI** | Latest | Web framework |
| **Uvicorn** | Latest | ASGI server |
| **ChromaDB** | Latest | Vector database |
| **OpenAI** | GPT-4 | Language model |
| **Sentence Transformers** | all-MiniLM-L6-v2 | Embeddings |

### Frontend

| Technology | Purpose |
|------------|---------|
| **HTML5/CSS3** | User interface |
| **JavaScript** | Interactive features |
| **Jinja2** | Template engine |

### Infrastructure

| Component | Technology | Purpose |
|-----------|------------|---------|
| **Containerization** | Docker | ChromaDB hosting |
| **Orchestration** | Docker Compose | Multi-container management |
| **Storage** | Volumes | Data persistence |
| **Networking** | Bridge | Container communication |

### Development Tools

- **Git** - Version control
- **VS Code** - IDE
- **Python venv** - Virtual environments
- **pip** - Package management

---

## 🚀 Quick Start Guide

### Prerequisites Check

```bash
# Verify Python
python --version  # Should be 3.11+

# Verify Docker
docker --version
docker-compose --version

# Verify Git
git --version
```

### Installation (5 Minutes)

```bash
# 1. Clone repository
git clone https://github.com/karthaveerya-droid/Orgpt.git
cd Orgpt

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.docker .env
# Edit .env with your OpenAI API key

# 5. Start ChromaDB
docker-compose up -d chromadb

# 6. Build indexes
export CHROMA_CLIENT_TYPE=http
python index_builder.py datadog_poc
python index_builder.py swagger

# 7. Start application
uvicorn app_api:app --reload --port 8001
```

### Verification

```bash
# Check ChromaDB
curl http://localhost:8000/api/v1/heartbeat

# Check Application
curl http://localhost:8001/health

# Open browser
open http://localhost:8001/
```

**🎉 You're ready! Open http://localhost:8001/ and start querying.**

---

## 📖 Detailed Setup Instructions

### Step 1: Environment Setup

#### 1.1 Python Virtual Environment

```bash
# Create isolated environment
python3.11 -m venv .venv

# Activate
source .venv/bin/activate

# Verify
which python
# Should show: /path/to/Orgpt/.venv/bin/python
```

#### 1.2 Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Verify critical packages
pip list | grep -E "fastapi|chromadb|openai|sentence-transformers"
```

#### 1.3 Configure Environment Variables

```bash
# Copy template
cp .env.docker .env

# Edit .env file
nano .env
```

**Required Variables:**
```bash
# OpenAI Configuration
OPENAI_API_KEY=sk-your-key-here
LLM_MODEL=gpt-4o-mini

# ChromaDB Configuration
CHROMA_CLIENT_TYPE=http
CHROMA_HOST=localhost
CHROMA_PORT=8000

# Application
HOST=0.0.0.0
PORT=8001
```

### Step 2: ChromaDB Setup

#### 2.1 Start Docker Container

```bash
# Start ChromaDB
docker-compose up -d chromadb

# Verify it's running
docker ps | grep chromadb

# Expected output:
# orgpt-chromadb   chromadb/chroma:latest   Up X minutes
```

#### 2.2 Verify Connection

```bash
# Test HTTP connection
curl http://localhost:8000/api/v1/heartbeat

# Test from Python
python -c "
import chromadb
client = chromadb.HttpClient(host='localhost', port=8000)
print('✅ Connected!', client.heartbeat())
"
```

#### 2.3 Monitor Health

```bash
# View logs
docker-compose logs -f chromadb

# Check status
docker-compose ps chromadb
```

### Step 3: Data Indexing

#### 3.1 Build Datadog POC Index

```bash
# Set environment
export CHROMA_CLIENT_TYPE=http

# Build from sample JSON (no API keys needed)
python index_builder.py datadog_poc

# Expected output:
# ✅ POC Index built successfully
# 📊 2 chunks stored in 'datadog_poc' collection
```

#### 3.2 Build Swagger Index

```bash
# Build from swagger sources
python index_builder.py swagger

# Expected output:
# ✅ Swagger index built successfully
# 📊 101 chunks stored in 'swagger' collection
```

#### 3.3 Verify Indexes

```bash
# Using Python
python -c "
import chromadb
client = chromadb.HttpClient(host='localhost', port=8000)
for col in client.list_collections():
    print(f'{col.name}: {col.count()} documents')
"

# Expected output:
# swagger: 101 documents
# datadog_poc: 2 documents
```

### Step 4: Application Launch

#### 4.1 Start Web Server

```bash
# Start with auto-reload (development)
export CHROMA_CLIENT_TYPE=http
uvicorn app_api:app --reload --port 8001

# Or start in background
nohup uvicorn app_api:app --port 8001 > server.log 2>&1 &
```

#### 4.2 Verify Server

```bash
# Health check
curl http://localhost:8001/health

# Expected response:
# {"status":"ok","message":"Orgpt Swagger Agent is running."}
```

#### 4.3 Access Interfaces

| URL | Description |
|-----|-------------|
| http://localhost:8001/ | Main chat interface |
| http://localhost:8001/monitor | Monitoring dashboard |
| http://localhost:8001/health | Health check endpoint |

### Step 5: First Query

#### 5.1 Web Interface

1. Open http://localhost:8001/
2. Select data source: **Swagger** or **Datadog**
3. Type question: "What services are available?"
4. Click **Send** or press Enter
5. View AI-generated answer

#### 5.2 API Call

```bash
# Query Swagger collection
curl -X POST http://localhost:8001/query \
  -F "query=What endpoints are available?" \
  -F "collection=swagger"

# Query Datadog collection
curl -X POST http://localhost:8001/query \
  -F "query=What services are in the catalog?" \
  -F "collection=datadog_poc"
```

---

## 📚 Usage Guide

### Web Interface

#### Selecting Data Sources

```
┌─────────────────────────────────────┐
│  Active Data Source: 📝 Swagger     │
│                                     │
│  ○ 📝 Swagger Documentation         │
│  ○ 📊 Datadog                       │
└─────────────────────────────────────┘
```

- **Swagger**: Query API documentation
- **Datadog**: Query service catalog (POC mode)

#### Asking Questions

**Good Questions:**
- ✅ "What endpoints are available in the API?"
- ✅ "How do I authenticate with the service?"
- ✅ "What services are deployed in production?"
- ✅ "Show me all GET endpoints"

**Poor Questions:**
- ❌ "Hello" (too generic)
- ❌ "What's the weather?" (out of scope)

### CLI Tools

#### Monitor ChromaDB

```bash
# Interactive monitor
python monitor_chromadb.py

# Options:
# 1. Test a query
# 2. Show detailed collection info
# 3. Export connection info to JSON
```

#### Build Indexes

```bash
# Build all indexes
python index_builder.py

# Build specific source
python index_builder.py swagger
python index_builder.py datadog_poc
python index_builder.py datadog_catalog  # Requires API keys

# Custom JSON for POC
python index_builder.py datadog_poc my_custom_data.json
```

#### View Collections

```bash
# List all collections
python -c "
import chromadb
client = chromadb.HttpClient(host='localhost', port=8000)
for col in client.list_collections():
    print(f'{col.name}: {col.count()} docs')
"
```

---

## 🔌 API Documentation

### Endpoints

#### GET `/`
**Description:** Main chat interface  
**Response:** HTML page  
**Example:**
```bash
curl http://localhost:8001/
```

#### POST `/query`
**Description:** Query any collection  
**Parameters:**
- `query` (string, required): User question
- `collection` (string, optional): Collection name (default: "swagger")

**Response:**
```json
{
  "answer": "The API provides the following endpoints...",
  "source": "swagger",
  "note": "Additional metadata if applicable"
}
```

**Example:**
```bash
curl -X POST http://localhost:8001/query \
  -F "query=What services exist?" \
  -F "collection=datadog_poc"
```

#### GET `/health`
**Description:** Health check  
**Response:**
```json
{
  "status": "ok",
  "message": "Orgpt Swagger Agent is running."
}
```

#### GET `/monitor`
**Description:** Monitoring dashboard  
**Response:** HTML monitoring interface  

#### GET `/chromadb/status`
**Description:** ChromaDB connection status  
**Response:**
```json
{
  "docker": {
    "running": true,
    "health": "✅ Healthy"
  },
  "connection": {
    "success": true,
    "type": "HTTP (localhost:8000)",
    "heartbeat": "1776158368092924847"
  },
  "collections": [
    {"name": "swagger", "count": 101},
    {"name": "datadog_poc", "count": 2}
  ],
  "total_documents": 103
}
```

---

## 📊 Monitoring & Observability

### Monitoring Dashboard

Access at: **http://localhost:8001/monitor**

**Features:**
- 🐳 Docker container status
- 🔗 ChromaDB connection health
- 📊 Collection statistics
- 📈 Document counts
- 🔄 Auto-refresh every 30 seconds

### Health Checks

```bash
# Application health
curl http://localhost:8001/health

# ChromaDB health
curl http://localhost:8000/api/v1/heartbeat

# Docker health
docker-compose ps chromadb
```

### Logs

```bash
# Application logs (if running in background)
tail -f server.log

# ChromaDB logs
docker-compose logs -f chromadb

# Last 100 lines
docker-compose logs --tail 100 chromadb
```