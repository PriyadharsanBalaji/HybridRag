# 🤖 Hybrid RAG System

A production-ready Retrieval-Augmented Generation (RAG) system combining **Vector Search (ChromaDB)** and **Knowledge Graphs (NetworkX)** with **Google Gemini AI**.

## ✨ Features

- **Dual Retrieval System**: Vector similarity search + Knowledge graph traversal
- **Free Tier Optimized**: Uses Gemini Free API with intelligent rate limiting
- **Multi-Format Support**: PDF, DOCX, TXT, MD, CSV, XLSX, PPTX, HTML
- **Beautiful UI**: Modern Streamlit interface with visualizations
- **Entity Extraction**: Automatic entity and relationship extraction using spaCy
- **Production Ready**: Comprehensive logging, error handling, and metrics

## 🏗️ Architecture

User Query
↓
┌───────────────────────────────┐
│ Hybrid Retriever │
│ ┌─────────┐ ┌────────────┐ │
│ │ Vector │ │ Knowledge │ │
│ │ Search │ │ Graph │ │
│ │(Cosine) │ │ (NetworkX) │ │
│ └─────────┘ └────────────┘ │
└───────────────────────────────┘
↓
Context Fusion
↓
Gemini LLM (Free Tier)
↓
Response + Sources

text

## 📦 Installation

### Prerequisites

- Python 3.9+
- pip

### Setup

1. **Clone the repository**
```bash
git clone <your-repo>
cd hybrid-rag-system
Create virtual environment

bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
Install dependencies

bash
pip install -r requirements.txt
Download spaCy model

bash
python -m spacy download en_core_web_sm
Configure environment

bash
cp .env.example .env
Edit .env and add your Gemini API key:

bash
GOOGLE_API_KEY=your_gemini_api_key_here
Get your FREE API key from: https://makersuite.google.com/app/apikey

🚀 Usage
Start the application
bash
streamlit run app.py
The app will open in your browser at http://localhost:8501

Using the System
Upload Documents: Use the sidebar to upload PDF, DOCX, or other supported files

Process: Click "Process Files" to ingest documents

Ask Questions: Use the chat interface to query your documents

View Sources: Check sources and knowledge graph relationships

Monitor: View analytics and system metrics

📁 Project Structure
text
hybrid-rag-system/
├── app.py                      # Main Streamlit application
├── config.py                   # Configuration
├── requirements.txt
├── .env.example
├── src/                        # Core logic
│   ├── document_processor.py
│   ├── vector_store.py
│   ├── knowledge_graph.py
│   ├── hybrid_retriever.py
│   ├── rag_chain.py
│   ├── embeddings.py
│   ├── entity_extractor.py
│   └── llm_manager.py
├── utils/                      # Utilities
│   ├── logger.py
│   ├── helpers.py
│   ├── validators.py
│   ├── metrics.py
│   └── rate_limiter.py
├── database/                   # Database managers
│   ├── chroma_manager.py
│   └── graph_manager.py
└── ui/                         # UI components
    ├── components.py
    ├── styles.py
    └── visualizations.py
⚙️ Configuration
Key settings in .env:

GEMINI_MODEL: gemini-1.5-flash (FREE) or gemini-pro

MAX_REQUESTS_PER_MINUTE: 15 (free tier limit)

MAX_REQUESTS_PER_DAY: 1500 (free tier limit)

EMBEDDING_MODEL: all-MiniLM-L6-v2 (free)

MAX_CHUNK_SIZE: 1000 tokens

TOP_K_VECTOR_RESULTS: 5

ENABLE_KNOWLEDGE_GRAPH: true

🔧 Advanced Usage
Custom System Prompts
Modify the system prompt in src/rag_chain.py for different behaviors.

Adding New Document Types
Add loaders in src/document_processor.py.

Adjusting Retrieval
Tune TOP_K_VECTOR_RESULTS and TOP_K_GRAPH_RESULTS in config.

📊 Performance
Average query time: ~2-4 seconds

Retrieval: ~0.5-1 seconds

Generation: ~1.5-3 seconds (depends on Gemini API)

🐛 Troubleshooting
API Rate Limits
The system automatically handles Gemini free tier limits

Requests queue if limits are reached

Memory Issues
Reduce MAX_CHUNK_SIZE if processing large documents

Limit concurrent file uploads

spaCy Model Missing
bash
python -m spacy download en_core_web_sm
📝 License
MIT License

🤝 Contributing
Contributions welcome! Please open an issue or PR.

📧 Support
For issues, please open a GitHub issue.

Made with ❤️ using Streamlit, LangChain, ChromaDB, and Gemini AI

text

***

### **28. setup.sh**

```bash
#!/bin/bash

# Hybrid RAG System Setup Script

echo "🚀 Setting up Hybrid RAG System..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Download spaCy model
echo "🧠 Downloading spaCy model..."
python -m spacy download en_core_web_sm

# Create .env from template
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your GOOGLE_API_KEY"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data/uploads data/processed data/chroma_db logs

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your Gemini API key"
echo "2. Run: source venv/bin/activate"
echo "3. Run: streamlit run app.py"
echo ""
echo "🎉 Happy RAG-ing!"
🎯 INSTALLATION & USAGE
Quick Start
bash
# 1. Make setup script executable
chmod +x setup.sh

# 2. Run setup
./setup.sh

# 3. Edit .env and add your Gemini API key
nano .env

# 4. Run the app
streamlit run app.py
✨ FEATURES SUMMARY
✅ 100% Free - Gemini API, ChromaDB, NetworkX
✅ Rate Limiting - Automatic handling of API limits
✅ Hybrid Search - Vector + Knowledge Graph
✅ Beautiful UI - Modern, responsive Streamlit interface
✅ Production Ready - Logging, metrics, error handling
✅ Multi-Format - Supports 8+ document types
✅ Entity Extraction - Automatic with spaCy
✅ Graph Visualization - Interactive knowledge graph
✅ Source Attribution - Tracks all information sources
✅ Performance Metrics - Real-time analytics