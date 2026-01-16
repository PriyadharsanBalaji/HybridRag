# 🚀 Hybrid RAG System

A production-ready Retrieval-Augmented Generation (RAG) system combining **Vector Search (ChromaDB)** and **Knowledge Graph reasoning (NetworkX)** powered by **Google Gemini AI** — fully optimized for the **free tier**.

---

## ✨ Features

- **Hybrid Retrieval**
  - Vector similarity search
  - Knowledge graph traversal
- **Free Tier Optimized**
  - Gemini Free API + intelligent rate limiting
- **Multi-Format Parsing**
  - PDF, DOCX, TXT, MD, CSV, XLSX, PPTX, HTML
- **Modern UI**
  - Streamlit interface with visualizations
- **Entity Extraction**
  - spaCy-based entity + relationship extraction
- **Production Ready**
  - Logging, error handling, metrics, attribution

---

## 🏗️ Architecture Overview

```
User Query
   │
   ▼
┌──────────────────────────────────┐
│         Hybrid Retriever         │
│ ┌────────────┐  ┌──────────────┐ │
│ │  Vector    │  │ Knowledge    │ │
│ │  Search    │  │  Graph       │ │
│ │ (Cosine)   │  │ (NetworkX)   │ │
│ └────────────┘  └──────────────┘ │
└──────────────────────────────────┘
   │
   ▼
Context Fusion
   │
   ▼
Gemini LLM (Free Tier)
   │
   ▼
Response + Sources
```

---

## 📦 Installation

### Prerequisites
- Python **3.9+**
- pip

---

### 1. Clone the repository

```bash
git clone <your-repo>
cd hybrid-rag-system
```

### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Download spaCy model

```bash
python -m spacy download en_core_web_sm
```

### 5. Configure `.env`

```bash
cp .env.example .env
```

Edit `.env` and set:

```
GOOGLE_API_KEY=your_gemini_api_key_here
```

Free key → https://makersuite.google.com/app/apikey

---

## 🚀 Running the Application

```bash
streamlit run app.py
```

App opens at:

> http://localhost:8501

---

## 🧩 Workflow

1. Upload documents
2. Click **Process Files**
3. Ask questions
4. View sources + graph relations
5. Monitor metrics

---

## 📁 Project Structure

```
hybrid-rag-system/
├── app.py
├── config.py
├── requirements.txt
├── .env.example
├── src/
│   ├── document_processor.py
│   ├── vector_store.py
│   ├── knowledge_graph.py
│   ├── hybrid_retriever.py
│   ├── rag_chain.py
│   ├── embeddings.py
│   ├── entity_extractor.py
│   └── llm_manager.py
├── utils/
│   ├── logger.py
│   ├── helpers.py
│   ├── validators.py
│   ├── metrics.py
│   └── rate_limiter.py
├── database/
│   ├── chroma_manager.py
│   └── graph_manager.py
└── ui/
    ├── components.py
    ├── styles.py
    └── visualizations.py
```

---

## ⚙️ Configuration

Key `.env` variables:

| Variable | Description |
|---|---|
| `GOOGLE_API_KEY` | Gemini Free API key |
| `GEMINI_MODEL` | `gemini-1.5-flash` (default) |
| `MAX_REQUESTS_PER_MINUTE` | Free tier rate limit |
| `MAX_REQUESTS_PER_DAY` | Free tier daily quota |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` |
| `MAX_CHUNK_SIZE` | Chunk token size |
| `TOP_K_VECTOR_RESULTS` | Vector retrieval count |
| `ENABLE_KNOWLEDGE_GRAPH` | Toggle graph retrieval |

---

## 📊 Performance

- Retrieval: **0.5 – 1s**
- Generation: **1.5 – 3s**
- End-to-end: **2 – 4s**

---

## 🧠 Entity & Graph Extraction

- Extracts entities using **spaCy**
- Builds directed graph with relationships
- Visualizes via Streamlit

---

## 🐛 Troubleshooting

| Issue | Fix |
|---|---|
| Rate limits | Auto handled via queue |
| Memory issues | Reduce `MAX_CHUNK_SIZE` |
| spaCy missing | `python -m spacy download en_core_web_sm` |

---

## 🎯 Setup Script

Make executable:

```bash
chmod +x setup.sh
```

Run:

```bash
./setup.sh
```

---

## 📝 License

MIT License

---

## 🤝 Contributing

PRs and issues welcome!

---

## 📧 Support

Open a GitHub issue.

Made with ❤️ using Streamlit, LangChain, ChromaDB, NetworkX, and Gemini AI.
