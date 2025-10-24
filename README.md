# Essential RAG System

Production-ready RAG chatbot for Italian tour operator using local embeddings and FAISS vector search.

## 🎯 Features

- **Local Embeddings**: Zero-cost embedding generation with sentence-transformers
- **FAISS Vector Search**: Fast semantic search over tour content
- **DeepSeek Integration**: Cost-effective LLM for chat completion
- **Italian Language**: Optimized for Italian queries and responses
- **Modular Design**: Clean separation between indexing and runtime

## 🏗️ Architecture

```
User Query (Italian)
    ↓
Local Embedding (sentence-transformers) ← No API cost
    ↓
FAISS Semantic Search ← <1ms
    ↓
Top-K Context Retrieval
    ↓
DeepSeek Chat Completion ← Only API call
    ↓
Grounded Italian Response
```

## 📁 Project Structure

```
essential-rag-system/
├── src/                      # Core Python modules
│   ├── config.py            # Centralized configuration
│   ├── indexer.py           # FAISS index builder
│   └── chatbot.py           # RAG chatbot engine
├── scripts/                  # CLI executables
│   ├── build_index.py       # Build FAISS index
│   ├── run_chatbot.py       # Run interactive chatbot
│   └── test_retrieval.py    # Test retrieval pipeline
├── data/                     # Source data
│   └── content.txt          # Italian tour content
├── indices/                  # Generated FAISS data (gitignored)
│   ├── faiss_index.index    # FAISS vector index
│   ├── chunks.pkl           # Document chunks
│   └── metadata.json        # Index metadata
├── docs/                     # Documentation
└── tests/                    # Unit tests (future)
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip3 install -r requirements.txt
```

### 2. Configure API Key

```bash
cp .env.example .env
# Edit .env and add your DEEPSEEK_API_KEY
```

### 3. Build FAISS Index

```bash
python3 scripts/build_index.py
```

This will:
- Load `data/content.txt` (Italian tour content)
- Chunk text by sections with overlap
- Generate embeddings locally (no API calls)
- Create FAISS index in `indices/`

### 4. Run Chatbot

**Interactive mode:**
```bash
python3 scripts/run_chatbot.py
```

**Test mode:**
```bash
python3 scripts/run_chatbot.py --test
```

**Test retrieval only (no LLM):**
```bash
python3 scripts/test_retrieval.py
```

## 📊 Technical Specifications

| Component | Technology | Notes |
|-----------|-----------|-------|
| **Embeddings** | sentence-transformers | `paraphrase-multilingual-MiniLM-L12-v2` |
| **Vector Store** | FAISS | `IndexFlatL2` (exact search) |
| **LLM** | DeepSeek API | OpenAI-compatible client |
| **Embedding Dim** | 384 | Optimized for Italian |
| **Chunk Size** | 500 chars | With 50 char overlap |
| **Top-K Retrieval** | 3 | Configurable in `src/config.py` |

## 💡 Usage Examples

### As a Module

```python
from src.chatbot import TourChatbot

# Initialize chatbot
bot = TourChatbot()

# Ask question
result = bot.chat("Quanto costa il tour del Parlamento?")
print(result['answer'])
print(result['sources'])
```

### As a CLI

```bash
$ python3 scripts/run_chatbot.py

💬 Tu: Quanto costa il tour del Parlamento?

🤖 Assistente: Il tour del Parlamento ha un prezzo a partire da
25 euro a persona. Per maggiori informazioni contattaci a
+40 774621133 o +40 774621205.

📚 Fonti: Tour del Parlamento, I nostri Tours
```

## 🔧 Configuration

All configuration is centralized in `src/config.py`:

```python
from src.config import Config

# Customize parameters
Config.TOP_K = 5              # Retrieve more chunks
Config.CHUNK_SIZE = 700       # Larger chunks
Config.DEEPSEEK_TEMPERATURE = 0.1  # More focused responses
```

## 📚 Data

- **Source**: viaggiarebucarest.com
- **Language**: Italian
- **Content**: Tour descriptions, pricing, reviews, contact info
- **Size**: ~33KB text, 75 semantic chunks

## 🧪 Testing

The system includes comprehensive testing:

1. **Retrieval Test**: Validates FAISS search without LLM
2. **Chatbot Test**: End-to-end with synthetic questions
3. **Interactive Test**: Manual testing via CLI

## 📖 Documentation

- `CLAUDE.md` - Development guidelines and architecture details
- `docs/architecture.md` - Detailed system architecture
- `data/README.md` - Data documentation

## 🛠️ Development

### Adding New Content

1. Update `data/content.txt`
2. Rebuild index: `python3 scripts/build_index.py`

### Modifying System Prompt

Edit `Config.SYSTEM_PROMPT` in `src/config.py`

### Changing Embedding Model

```python
# In src/config.py
Config.EMBEDDING_MODEL = "your-model-name"
```

Then rebuild index.

## ⚙️ Requirements

- Python 3.8+
- sentence-transformers 2.2.2+
- faiss-cpu 1.7.4+
- openai 1.12.0+
- numpy, python-dotenv, tqdm

## 📝 License

Private project for Essential RAG System

## 👥 Contact

For questions about Viaggiare Bucarest tours:
- Phone: +40 774621133, +40 774621205
- Email: viaggiareabucarest@yahoo.com
