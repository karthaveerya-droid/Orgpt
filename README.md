# 🤖 ORGPT - Intelligent Organization API Documentation & Dependency Analysis System

> **Orgpt** is an intelligent system for API analysis and documentation based on **RAG (Retrieval-Augmented Generation)**. It enables querying APIs, understanding service dependencies, and generating architectural insights using LLMs.

## 📋 Project Description

### Overview
ORGPT combines **GitHub repository ingestion**, **code processing**, **vector search**, and **natural language generation** to build a smart assistant that understands the architecture of your systems.

### Current Use Cases
- ✅ Query API specifications (Swagger/OpenAPI)
- ✅ Search endpoint documentation
- ✅ Generate context-aware answers about APIs

### Future Use Cases
- 🎯 Direct analysis of GitHub repositories
- 🎯 Extract API information from source code
- 🎯 Map dependency graphs between services
- 🎯 Generate impact reports for code changes
- 🎯 Detect technical debt
- 🎯 Integrate with **LeanIX** for enterprise architecture
- 🎯 Real-time monitoring with **Datadog**

---

## 🏗️ System Architecture

### Main Components

```mermaid
graph TD
    A["📊 Data Sources<br/>(Swagger/GitHub Repos)"] --> B["🔍 Ingestion Layer"]
    B --> C["⚙️ Processing Layer"]
    C --> D["🗃️ Vector Store Layer"]
    D --> E["🔎 Retrieval Layer"]
    E --> F["🤖 LLM Layer"]
    F --> G["🌐 Application Layer"]
    
    B --> B1["Swagger Connector<br/>(TODAY)"]
    B --> B2["GitHub Connector<br/>(FUTURE)"]
    
    C --> C1["Chunker"]
    C1 --> C2["Embedder"]
    
    D --> D1["VectorStore<br/>(Pinecone/Weaviate)"]
    
    E --> E1["RAG Engine"]
    
    F --> F1["LLMHandler<br/>(OpenAI/Claude)"]
    
    G --> G1["app.py<br/>(Web UI)"]
    G --> G2["app_api.py<br/>(REST API)"]
    
    style A fill:#FFE5B4
    style B fill:#B4E5FF
    style C fill:#B4FFB4
    style D fill:#FFB4E5
    style E fill:#E5B4FF
    style F fill:#FFD700
    style G fill:#90EE90
```

---

## 🔄 Execution Flow - Query (User Query)

```mermaid
sequenceDiagram
    participant User as 👤 User
    participant App as 🌐 Application
    participant RAG as 🔎 RAG Engine
    participant VS as 🗃️ Vector Store
    participant LLM as 🤖 LLM Handler

    User->>App: 1️⃣ Submit query<br/>"How to create a user?"
    App->>RAG: 2️⃣ retrieve(query, top_k=3)
    RAG->>VS: 3️⃣ search(query_embedding)
    VS-->>RAG: 4️⃣ Top 3 relevant documents
    RAG-->>App: 5️⃣ Assembled context
    App->>LLM: 6️⃣ ask(query, context)
    LLM-->>App: 7️⃣ Generated answer
    App-->>User: 8️⃣ Present final response
    Note over User: "To create a user...<br/>POST /api/users with body..."
```

---

## 🏗️ Indexing Flow (Build Index)

```mermaid
graph TD
    A["📥 Ingestion<br/>extract_text_from_swagger"] --> B["🔄 Processing<br/>chunk_texts"]
    B --> C["🧠 Embedding<br/>embedder.embed"]
    C --> D["💾 Storage<br/>vs.add"]
    D --> E["✅ Index Ready"]
    
    A --> A1["1. Parse swagger.json"]
    B --> B1["2. Divide into chunks<br/>max_tokens: 512"]
    C --> C1["3. Generate vectors<br/>1536-dim embeddings"]
    D --> D1["4. Index in VectorStore<br/>with metadata"]
    
    style A fill:#FFB6C1
    style B fill:#87CEEB
    style C fill:#98FB98
    style D fill:#DDA0DD
    style E fill:#F0E68C
```

---

## 🚀 Future Roadmap - GitHub Repository Analysis

### Phase 1: GitHub Connector (Next 4 weeks)
```mermaid
graph LR
    A["GitHub API"] --> B["Repository Cloner"]
    B --> C["Code Parser<br/>(AST)"]
    C --> D["API Extractor<br/>(REST/gRPC)"]
    D --> E["Dependency Graph<br/>Builder"]
    E --> F["Vector Store"]
    
    style A fill:#FFE5B4
    style B fill:#B4E5FF
    style C fill:#B4FFB4
    style D fill:#FFB4E5
    style E fill:#E5B4FF
    style F fill:#F0E68C
```

**Tasks:**
- [ ] Implement GitHub API client with OAuth authentication
- [ ] Clone/analyze repositories
- [ ] Parse code (Python/TypeScript/Java)
- [ ] Extract API decorators (FastAPI, Flask, Express)
- [ ] Map imports and dependencies

### Phase 2: Dependency Graph Analysis
```mermaid
graph TD
    A["Service A<br/>GET /users"] --> B["Service B<br/>GET /auth"]
    B --> C["Service C<br/>Database"]
    A --> D["Service D<br/>Cache"]
    D --> C
    
    style A fill:#FFB6C1
    style B fill:#87CEEB
    style C fill:#98FB98
    style D fill:#DDA0DD
```

**Features:**
- Service dependency graph
- Change impact analysis
- Cycle detection
- Criticality analysis

### Phase 3: LeanIX Integration
```mermaid
graph LR
    OG["ORGPT<br/>GitHub Analysis"] -->|Sync| LX["LeanIX<br/>Enterprise Architecture"]
    LX -->|Query| LX1["Applications"]
    LX -->|Query| LX2["Interfaces"]
    LX -->|Query| LX3["Relations"]
    
    style OG fill:#F0E68C
    style LX fill:#E8F4F8
```

### Phase 4: Datadog Integration
```mermaid
graph LR
    OG["ORGPT<br/>Analysis"] -->|Metrics| DD["Datadog<br/>Monitoring"]
    DD -->|Track| DD1["Query Performance"]
    DD -->|Track| DD2["API Usage"]
    DD -->|Track| DD3["System Health"]
    
    style OG fill:#F0E68C
    style DD fill:#FFB6C1
```

---

## 📁 Project Structure

```
orgpt/
├── README.md                    # This file
├── requirements.txt             # Python dependencies
├── main.py                      # Main entry point
├── index_builder.py             # Index building script
├── app.py                       # Web interface (Streamlit)
├── app_api.py                   # REST API (FastAPI)
├── app_local.py                 # Local execution
│
├── ingestion/                   # 📥 Ingestion Layer
│   ├── __init__.py
│   ├── swagger_connector.py     # Parse Swagger/OpenAPI (TODAY)
│   └── github_connector.py      # Analyze GitHub (FUTURE)
│
├── processing/                  # ⚙️ Processing Layer
│   ├── __init__.py
│   ├── chunker.py               # Split text into chunks
│   └── embedder.py              # Generate vector embeddings
│
├── vector_store/                # 🗃️ Storage Layer
│   ├── __init__.py
│   └── store.py                 # Abstract VectorStore interface
│
├── retrieval/                   # 🔎 Retrieval Layer
│   ├── __init__.py
│   └── rag_engine.py            # RAG (Retrieval-Augmented Generation)
│
├── llm/                         # 🤖 LLM Layer
│   ├── __init__.py
│   └── llm_layer.py             # LLM model interface
│
├── integrations/                # 🔗 External Integrations (FUTURE)
│   ├── leanix_connector.py      # LeanIX connection
│   └── datadog_client.py        # Datadog telemetry
│
├── data/                        # 📊 Data
│   ├── sample_swagger.json      # Sample Swagger
│   └── indices/                 # Vector indices
│
└── templates/                   # 🎨 Web templates
    ├── index.html
    └── styles.css
```

---

## ⚡ Installation and Configuration

### Prerequisites
- Python 3.8+
- OpenAI API Key (or local model)
- Vector Store (Pinecone, Weaviate, or local FAISS)

### Setup

```bash
# 1. Clone repository
git clone https://github.com/karthaveerya-droid/Orgpt.git
cd Orgpt

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cat > .env << EOF
# OpenAI
OPENAI_API_KEY=your-api-key

# Vector Store (select one)
VECTOR_STORE_TYPE=pinecone  # or: weaviate, faiss
PINECONE_API_KEY=your-key
PINECONE_INDEX_NAME=orgpt

# GitHub (FUTURE)
GITHUB_TOKEN=your-token

# LeanIX (FUTURE)
LEANIX_API_KEY=your-key
LEANIX_WORKSPACE_ID=your-workspace

# Datadog (FUTURE)
DATADOG_API_KEY=your-key
DATADOG_APP_KEY=your-app-key
EOF
```

---

## 🚀 Usage

### 1. Build Index (Indexing)

```bash
python index_builder.py --source swagger --path sample_swagger.json
```

**Expected output:**
```
[INFO] Extracting Swagger documentation...
[INFO] Splitting into chunks (512 tokens max)...
[INFO] Generating 45 embeddings...
[INFO] Indexing in VectorStore...
✅ Swagger data indexed successfully!
```

### 2. Query Data (Query)

```bash
python main.py
# Input: "How to create a user?"
# Response: "To create a user, make a POST request to..."
```

### 3. Web Interface (Streamlit)

```bash
streamlit run app.py
```

Access: `http://localhost:8501`

### 4. REST API (FastAPI)

```bash
uvicorn app_api:app --reload
```

Access: `http://localhost:8000/docs`

---

## 📊 REST API Endpoints (Future)

### Query Endpoint
```http
POST /api/query
Content-Type: application/json

{
  "question": "How to authenticate users?",
  "top_k": 3,
  "context_window": 2000
}

Response:
{
  "answer": "To authenticate users...",
  "sources": ["endpoint_id_1", "endpoint_id_2"],
  "confidence": 0.95,
  "processing_time_ms": 234
}
```

### Index Status
```http
GET /api/index/status

Response:
{
  "indexed_documents": 450,
  "total_embeddings": 1200,
  "last_update": "2024-03-20T15:30:00Z",
  "vector_store": "pinecone",
  "status": "healthy"
}
```

### GitHub Analysis (FUTURE)
```http
POST /api/github/analyze
Content-Type: application/json

{
  "repo": "your-org/your-repo",
  "branch": "main",
  "extract_apis": true,
  "generate_dependency_graph": true
}

Response:
{
  "services": [
    {
      "name": "UserService",
      "endpoints": 12,
      "dependencies": ["AuthService", "DatabaseLayer"]
    }
  ],
  "dependency_graph": {...},
  "analysis_id": "analysis_123"
}
```

---

## 🔧 Component Details

### 1. Ingestion Layer (Data Extraction)

#### Swagger Connector (Current)
```python
from ingestion.swagger_connector import extract_text_from_swagger_sources

docs = extract_text_from_swagger_sources("sample_swagger.json")
# Returns: ["GET /users - Retrieves list of users...", ...]
```

#### GitHub Connector (Future)
```python
from ingestion.github_connector import extract_apis_from_github

apis = extract_apis_from_github(
    repo="org/repo",
    patterns=["@app.route", "@router.get", "@app.post"],
    languages=["python", "typescript", "java"]
)
# Returns: [APIInfo, APIInfo, ...]
```

### 2. Processing Layer (Data Processing)

```python
from processing.chunker import chunk_texts
from processing.embedder import Embedder

# Chunking
chunks = chunk_texts(
    texts=docs,
    chunk_size=512,
    overlap=50
)

# Embedding
embedder = Embedder(model="text-embedding-3-large")
embeddings = embedder.embed(chunks)
```

### 3. Vector Store Layer (Storage)

```python
from vector_store.store import VectorStore

vs = VectorStore("pinecone", index_name="orgpt")

# Add documents
vs.add(
    ids=["doc_1", "doc_2"],
    texts=chunks,
    embeddings=embeddings,
    metadata={"source": "swagger", "version": "1.0"}
)

# Search
results = vs.search(
    query_embedding=query_vec,
    top_k=3,
    filters={"source": "swagger"}
)
```

### 4. Retrieval Layer (Context Retrieval)

```python
from retrieval.rag_engine import RAGEngine

rag = RAGEngine(vector_store=vs)

retrieved = rag.retrieve(
    query="How to create a user?",
    top_k=3
)
# Returns: {"documents": [...], "scores": [...], "metadata": [...]}
```

### 5. LLM Layer (Response Generation)

```python
from llm.llm_layer import LLMHandler

llm = LLMHandler(model="gpt-4")

answer = llm.ask(
    query="How to create a user?",
    context="GET /users returns...\nPOST /users creates...",
    temperature=0.3
)
# Returns: "To create a user, make a POST to /users with..."
```

---

## 🔗 Complete Flow Diagram

```mermaid
graph LR
    subgraph input["🔌 INPUT"]
        I1["Swagger Specs"]
        I2["GitHub Repos"]
        I3["User Queries"]
    end
    
    subgraph processing["⚙️ PROCESSING"]
        P1["Swagger Connector"]
        P2["GitHub Connector"]
        P3["Chunker"]
        P4["Embedder"]
    end
    
    subgraph storage["🗄️ STORAGE"]
        S1["Vector Store"]
        S2["Metadata DB"]
    end
    
    subgraph retrieval["🔍 RETRIEVAL"]
        R1["Query Embedding"]
        R2["Similarity Search"]
        R3["Context Assembly"]
    end
    
    subgraph generation["🤖 GENERATION"]
        G1["Prompt Builder"]
        G2["LLM Call"]
        G3["Response Format"]
    end
    
    subgraph output["📤 OUTPUT"]
        O1["Web Interface"]
        O2["REST API"]
    end
    
    I1 --> P1
    I2 --> P2
    P1 --> P3
    P2 --> P3
    P3 --> P4
    P4 --> S1
    P4 --> S2
    I3 --> R1
    R1 --> R2
    R2 --> S1
    R2 --> R3
    R3 --> G1
    G1 --> G2
    G2 --> G3
    G3 --> O1
    G3 --> O2
    
    style input fill:#FFE5B4
    style processing fill:#B4E5FF
    style storage fill:#FFB4E5
    style retrieval fill:#E5B4FF
    style generation fill:#FFD700
    style output fill:#90EE90
```

---

## 🔗 Future Integrations

### LeanIX Integration
Sync with enterprise architecture platform:

```mermaid
graph TB
    subgraph LEANIX["🏢 LeanIX Integration"]
        L1["🔐 OAuth 2.0<br/>Authentication"]
        L2["📲 API Client"]
        L3["🔄 Data Mapper"]
        L4["📊 Query Engine"]
        L5["🔗 Sync Manager"]
    end
    
    subgraph ORGPT["🤖 ORGPT Core"]
        O1["GitHub Analysis"]
        O2["Dependency Graph"]
        O3["API Catalog"]
    end
    
    L1 --> L2
    L2 --> L3
    L3 --> L4
    L4 --> L5
    
    O1 --> L3
    O2 --> L3
    O3 --> L4
    
    style LEANIX fill:#E8F4F8
    style ORGPT fill:#F0E68C
```

### Datadog Integration
Monitor system health and performance:

```mermaid
graph TB
    subgraph DATADOG["📈 Datadog Monitoring"]
        D1["📊 Metrics"]
        D2["📝 Events Log"]
        D3["🔗 Distributed Trace"]
        D4["📉 Dashboards"]
    end
    
    subgraph ORGPT["🤖 ORGPT Core"]
        O1["Query Processing"]
        O2["Retrieval Engine"]
        O3["LLM Generation"]
    end
    
    O1 --> D1
    O2 --> D2
    O3 --> D3
    O3 --> D4
    
    style DATADOG fill:#FFB6C1
    style ORGPT fill:#F0E68C
```

---

## 📊 Usage Examples

### Case 1: Analyze an API
```bash
$ python main.py
> Question: "What are all the endpoints for managing users?"

Response:
- GET /api/v1/users - Retrieves paginated user list
- GET /api/v1/users/{id} - Retrieves a specific user
- POST /api/v1/users - Creates a new user
- PUT /api/v1/users/{id} - Updates a user
- DELETE /api/v1/users/{id} - Deletes a user

Documentation found in: swagger_v1.0
```
---

## 🎯 Contributing

Contributions are welcome! For major changes:

1. Fork the project
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit with clear messages (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📝 License

This project is licensed under the MIT License. See `LICENSE` for details.

---

## 👥 Author

**Kartik Aveerya** - [@karthaveerya-droid](https://github.com/karthaveerya-droid)

---

## 🙏 Acknowledgments

- Inspired by modern RAG architectures
- Built on OpenAI, LangChain, and vector search tools
- Open source community

---

## 📞 Contact and Support

- 📧 Email: [your-email@example.com]
- 🐛 Issues: [GitHub Issues](https://github.com/karthaveerya-droid/Orgpt/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/karthaveerya-droid/Orgpt/discussions)

---


