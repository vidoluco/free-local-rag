# Essential RAG System - Production Template

White-label RAG (Retrieval-Augmented Generation) system ready for client demos and deployments. Build custom AI chatbots trained on any knowledge base in minutes.

## 🎯 What This Is

A production-ready, configurable RAG chatbot system that:
- **Works out of the box** - 5-minute setup with `./setup.sh`
- **Supports multiple formats** - PDF, DOCX, TXT, Markdown, web scraping
- **Fully customizable** - Company branding, prompts, behavior via config.yaml
- **Web & CLI interfaces** - Streamlit UI + command-line chatbot
- **Multi-language ready** - Tested with English, Italian, and other languages
- **Zero vendor lock-in** - Uses local embeddings + cost-effective Perplexity API

## 🚀 Quick Start

### 1. Setup (One Command)
```bash
git clone <repository>
cd essential-rag-system
./setup.sh
```

### 2. Configure
```bash
# Add your API key
nano .env
# PERPLEXITY_API_KEY=pplx-your-key-here

# Customize for your client
nano config.yaml
```

### 3. Add Content
```bash
# Copy client documents to data/client_content/
cp /path/to/docs/* data/client_content/

# Or ingest from various sources
python3 scripts/ingest_documents.py --source /path/to/files
```

### 4. Build & Run
```bash
source venv/bin/activate

# Build the knowledge base index
python3 scripts/build_index.py

# Launch web interface
streamlit run app.py

# Or run CLI chatbot
python3 scripts/run_chatbot.py
```

## 📁 Project Structure

```
essential-rag-system/
├── app.py                      # Streamlit web interface
├── setup.sh                    # One-command setup script
├── config.yaml                 # Client configuration (customize here!)
├── .env                        # API credentials
├── src/
│   ├── config.py              # Configuration loader
│   ├── indexer.py             # FAISS index builder
│   ├── chatbot.py             # RAG chatbot engine
│   └── loaders.py             # Multi-format document loaders
├── scripts/
│   ├── build_index.py         # Build FAISS index
│   ├── run_chatbot.py         # CLI chatbot
│   ├── ingest_documents.py    # Batch document ingestion
│   └── test_retrieval.py      # Test retrieval quality
├── data/
│   ├── client_content/        # Client documents go here
│   ├── sample/                # Sample/demo data
│   └── examples/              # Example implementations
├── docs/
│   ├── CLIENT_GUIDE.md        # End-user documentation
│   └── CUSTOMIZATION.md       # Deployment & config guide
└── indices/                    # Generated FAISS index (gitignored)
```

## 🎨 Key Features

### Multi-Format Document Support
- **PDF** - Automatic text extraction
- **DOCX** - Word documents with tables
- **TXT** - Plain text with section markers
- **Markdown** - Formatted documentation
- **Web Scraping** - Direct URL content extraction

### Flexible Configuration
Everything customizable via `config.yaml`:
- Company information & branding
- System prompt & chatbot personality
- Language settings (multilingual support)
- RAG parameters (chunk size, top-k retrieval)
- LLM settings (temperature, max tokens)
- UI customization (title, colors, welcome message)

### Two User Interfaces

**Web UI (Streamlit)**:
- Modern chat interface
- Admin panel for document management
- File upload & index building
- Source citation display
- Mobile-friendly

**CLI Interface**:
- Interactive terminal chatbot
- Perfect for testing & debugging
- No browser required

### Production Ready
- Local embedding generation (no API costs)
- Fast FAISS vector search (<1ms)
- Only LLM calls use API (cost-effective)
- Modular, maintainable codebase
- Comprehensive error handling
- Documented for easy handoff

## 🔧 Customization

### For New Client Deployment

1. **Edit `config.yaml`**:
```yaml
company:
  name: "Client Company Name"
  description: "Brief description"
  contact:
    email: "contact@client.com"
    phone: "+1-555-0123"

language:
  primary: "en"  # or "it", "es", "fr", etc.

system_prompt:
  role: "professional assistant"
  instructions: |
    You are an AI assistant for {company_name}...
```

2. **Customize System Behavior**:
```yaml
rag:
  chunk_size: 500
  top_k: 3

llm:
  temperature: 0.3
  max_tokens: 500

ui:
  title: "Client Knowledge Base"
  page_icon: "🤖"
```

3. **See CUSTOMIZATION.md** for complete guide

## 💡 Usage Examples

### Document Ingestion

```bash
# From directory
python3 scripts/ingest_documents.py --source data/client_content

# Single file
python3 scripts/ingest_documents.py --file document.pdf

# Web scraping (after configuring URLs in config.yaml)
python3 scripts/ingest_documents.py --scrape-web
```

### Building Index

```bash
# Build from default location (data/client_content)
python3 scripts/build_index.py

# Build from specific file/directory
python3 scripts/build_index.py --content data/sample/demo.txt
```

### Running the Chatbot

```bash
# Web interface (recommended)
streamlit run app.py

# CLI interactive mode
python3 scripts/run_chatbot.py

# CLI test mode
python3 scripts/run_chatbot.py --test
```

### As a Python Module

```python
from src.chatbot import RAGChatbot

# Initialize
bot = RAGChatbot()

# Ask questions
result = bot.chat("What are your business hours?")
print(result['answer'])
print(f"Sources: {result['sources']}")
```

## 🌍 Multi-Language Support

The system supports multiple languages out of the box:

- **English** (default)
- **Italian** (fully tested - see examples/tour_operator)
- **Spanish, French, German, Portuguese** (supported by embedding model)

Configure in `config.yaml`:
```yaml
language:
  primary: "it"  # for Italian

system_prompt:
  instructions: |
    Sei l'assistente virtuale di {company_name}...
```

## 📊 Technical Specifications

| Component | Technology | Notes |
|-----------|-----------|-------|
| **Embeddings** | sentence-transformers | Local, zero API cost |
| **Vector Store** | FAISS | Fast exact search |
| **LLM** | Perplexity Sonar | Cost-effective, OpenAI-compatible |
| **Web UI** | Streamlit | Modern, responsive |
| **Embedding Model** | paraphrase-multilingual-MiniLM-L12-v2 | 384 dimensions |
| **Default Chunk Size** | 500 chars | With 50 char overlap |
| **Default Top-K** | 3 | Configurable per deployment |

## 📚 Documentation

- **CLIENT_GUIDE.md** - End-user guide for clients
- **CUSTOMIZATION.md** - Deployment & configuration guide for you
- **data/examples/** - Example implementations (tour operator, etc.)
- **Code comments** - Inline documentation throughout

## 🎯 Use Cases

Perfect for:
- **Customer Support** - Answer FAQs from knowledge base
- **Sales Enablement** - Product information chatbot
- **Internal Knowledge** - Employee self-service portal
- **Documentation Assistant** - Technical documentation Q&A
- **Client Demos** - White-label solution for prospects

## ⚙️ Requirements

- Python 3.8+
- 2GB RAM minimum (4GB recommended)
- Perplexity API key (get from https://www.perplexity.ai/settings/api)
- ~500MB disk space for dependencies
- Linux, macOS, or Windows with bash

## 🔐 Security Notes

- Never commit `.env` to version control (already in .gitignore)
- Use unique API keys per deployment
- Sanitize client data before ingestion
- Review documents for sensitive information
- Consider API rate limits and costs

## 📈 Scaling Considerations

**Current Setup** (single machine):
- Handles 10-50 concurrent users
- <100MB document corpus
- <10K chunks in index

**For Larger Scale**:
- Use IndexIVFFlat for 100K+ chunks
- Deploy on cloud (AWS, GCP, Azure)
- Add Redis caching layer
- Load balance multiple instances
- Consider Pinecone/Weaviate for vector storage

## 🐛 Troubleshooting

See CLIENT_GUIDE.md for common issues and solutions.

For development/deployment issues:
- Check `indices/metadata.json` for index stats
- Use `scripts/test_retrieval.py` to debug retrieval
- Enable `show_retrieval_scores: true` in config.yaml for debugging
- Check logs in terminal where app is running

## 🤝 Contributing

This is a template system. Customize per client:
1. Fork/copy for each deployment
2. Never commit client data to git
3. Use examples/ folder for reference implementations
4. Update CLIENT_GUIDE.md with client-specific instructions

## 📝 License

Private/Commercial - Essential RAG System Template

## 🆘 Support

For technical issues or questions:
- Review documentation in `docs/`
- Check examples in `data/examples/`
- Contact system administrator

---

**Ready to deploy?**
1. Run `./setup.sh`
2. Configure `config.yaml`
3. Add documents to `data/client_content/`
4. Build index with `python3 scripts/build_index.py`
5. Launch with `streamlit run app.py`

**Total setup time: ~5 minutes** ⚡
