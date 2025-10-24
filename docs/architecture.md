# Essential RAG System - Architecture Documentation

## Overview

Production-ready Retrieval Augmented Generation (RAG) system for an Italian tour operator chatbot, featuring local embeddings and FAISS vector search.

## System Architecture

### High-Level Design

```
┌─────────────────────────────────────────────────────────────┐
│                    INDEXING PHASE (Offline)                  │
└─────────────────────────────────────────────────────────────┘

data/content.txt (33KB Italian text)
    ↓
LocalEmbeddingIndexer (src/indexer.py)
    ↓
├─ Semantic Chunking (by section markers, 500 chars, 50 overlap)
├─ Local Embedding (sentence-transformers, no API)
└─ FAISS Index Creation (IndexFlatL2, 75 vectors × 384 dim)
    ↓
indices/
├─ faiss_index.index (FAISS binary)
├─ chunks.pkl (document chunks)
└─ metadata.json (index stats)


┌─────────────────────────────────────────────────────────────┐
│                    QUERY PHASE (Runtime)                     │
└─────────────────────────────────────────────────────────────┘

User Query (Italian)
    ↓
TourChatbot (src/chatbot.py)
    ↓
1. Embed Query Locally (sentence-transformers)
    ↓
2. FAISS Search (top-3 chunks by L2 distance)
    ↓
3. Context Formatting (section headers + text)
    ↓
4. DeepSeek API Call (chat completion with context)
    ↓
Italian Response + Sources
```

## Component Details

### 1. Configuration Layer (`src/config.py`)

**Centralized configuration for all system parameters.**

Key Constants:
- **Paths**: `DATA_DIR`, `INDICES_DIR`, `CONTENT_FILE`
- **Models**: `EMBEDDING_MODEL` (multilingual-MiniLM-L12-v2)
- **Chunking**: `CHUNK_SIZE=500`, `CHUNK_OVERLAP=50`
- **Retrieval**: `TOP_K=3`
- **LLM**: `DEEPSEEK_MODEL`, `TEMPERATURE=0.3`
- **Prompts**: `SYSTEM_PROMPT` (promotional assistant persona)

Design Decisions:
- All magic numbers centralized
- Environment-based API key loading
- Path resolution relative to project root
- Immutable class-based config

### 2. Indexer (`src/indexer.py`)

**Handles offline index building with local embeddings.**

Class: `LocalEmbeddingIndexer`

Methods:
- `load_content()`: Read raw text from `data/content.txt`
- `chunk_by_sections()`: Split by `=== PAGINA:` markers with overlap
- `generate_embeddings()`: Batch encode with sentence-transformers
- `create_faiss_index()`: Build `IndexFlatL2` from embeddings
- `save_index()`: Persist index, chunks, metadata to `indices/`
- `build()`: Complete pipeline

Key Features:
- **No API calls**: Fully local embedding generation
- **Progress tracking**: tqdm integration for transparency
- **Metadata tracking**: Stores model info, chunk stats, sections
- **Idempotent**: Can rebuild index without side effects

Chunking Strategy:
```python
# Split by sections
sections = content.split('=== PAGINA:')

# Sub-chunk long sections with overlap
if len(section_content) > CHUNK_SIZE:
    start = 0
    while start < len(section_content):
        end = start + CHUNK_SIZE
        chunk = section_content[start:end]
        # Next chunk starts CHUNK_SIZE - CHUNK_OVERLAP chars ahead
        start += CHUNK_SIZE - CHUNK_OVERLAP
```

### 3. Chatbot (`src/chatbot.py`)

**Handles runtime query processing and LLM interaction.**

Class: `TourChatbot`

Methods:
- `load_index()`: Load FAISS + chunks from `indices/`
- `embed_query()`: Encode user query locally
- `retrieve()`: FAISS search → top-K chunks with scores
- `format_context()`: Prepare context for LLM
- `chat()`: Full RAG pipeline (retrieve + generate)
- `run_interactive()`: CLI interface

Key Features:
- **Same embedding model**: Consistency with indexer
- **Score conversion**: L2 distance → similarity score
- **Context windowing**: Top-K chunks formatted with section headers
- **Grounded generation**: System prompt enforces context-only responses
- **Error handling**: Graceful API failure handling

Retrieval Process:
```python
1. query_embedding = model.encode(query)        # Local, ~50ms
2. distances, indices = index.search(query_emb, k=3)  # FAISS, <1ms
3. scores = [1 / (1 + dist) for dist in distances]   # Distance → similarity
4. chunks = [chunks[idx] for idx in indices]          # Fetch chunks
5. context = format_chunks_with_sections(chunks)      # Format for LLM
6. response = deepseek_api.chat(context + query)      # API call
```

### 4. Scripts Layer (`scripts/`)

**Thin CLI wrappers for user interaction.**

Files:
- `build_index.py`: Import `LocalEmbeddingIndexer`, call `.build()`
- `run_chatbot.py`: Import `TourChatbot`, call `.run_interactive()` or test mode
- `test_retrieval.py`: Test FAISS search without LLM (for debugging)

Design:
- Minimal business logic (delegated to `src/`)
- Clear error messages
- Proper exit codes
- Import from `src` modules

## Data Flow Diagram

```
┌──────────────┐
│ content.txt  │  Raw Italian text (source of truth)
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│ Semantic Chunker │  Split by sections + overlap
└──────┬───────────┘
       │
       ▼
┌──────────────────────┐
│ 75 Text Chunks       │  ~500 chars each, metadata attached
└──────┬───────────────┘
       │
       ▼
┌──────────────────────────┐
│ sentence-transformers    │  paraphrase-multilingual-MiniLM-L12-v2
│ (LOCAL - no API)         │
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ 75 × 384 Embeddings      │  numpy.float32 array
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ FAISS IndexFlatL2        │  Exact L2 distance search
└──────┬───────────────────┘
       │
       ▼
┌──────────────────────────┐
│ Persisted to indices/    │
│ • faiss_index.index      │
│ • chunks.pkl             │
│ • metadata.json          │
└──────────────────────────┘

RUNTIME:

┌──────────────┐
│ User Query   │  "Quanto costa il tour del Parlamento?"
└──────┬───────┘
       │
       ▼
┌──────────────────┐
│ Embed Locally    │  Same model as indexing
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ FAISS Search     │  L2 distance, top-3
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Format Context   │  Section headers + text
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ DeepSeek API     │  Chat completion with context
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Italian Response │  Grounded in retrieved context
└──────────────────┘
```

## Technology Stack

| Layer | Technology | Justification |
|-------|-----------|---------------|
| **Embeddings** | sentence-transformers | Zero-cost, local, multilingual Italian support |
| **Vector Store** | FAISS (IndexFlatL2) | Fast exact search, suitable for <1M vectors |
| **LLM** | DeepSeek API | Cost-effective, OpenAI-compatible |
| **Language** | Python 3.8+ | Rich ML ecosystem |
| **CLI** | Native Python | Simple, no frameworks needed |
| **Config** | python-dotenv | Standard env var management |

## Key Design Decisions

### Why Local Embeddings?

**Decision**: Use sentence-transformers locally instead of API-based embeddings

**Rationale**:
- Zero marginal cost per query
- No API dependency for indexing
- Fast inference on CPU (~50ms per query)
- Multilingual model supports Italian well
- Consistent embeddings (same model for index + query)

**Trade-offs**:
- Lower quality than OpenAI `text-embedding-3-large`
- Acceptable for domain-specific content with 75 chunks

### Why FAISS IndexFlatL2?

**Decision**: Use exact L2 distance search (no approximation)

**Rationale**:
- 75 vectors = brute-force search is <1ms
- No need for approximate methods (IVF, HNSW) at this scale
- Simplicity: no index training required
- Accuracy: exact distances, no recall degradation

**When to upgrade**: >10K vectors → consider IndexIVFFlat

### Why 500-char Chunks with 50-char Overlap?

**Decision**: Chunk size = 500 chars, overlap = 50 chars

**Rationale**:
- **Size**: Balances context (not too fragmented) vs. relevance (not too broad)
- **Overlap**: Prevents splitting mid-sentence at chunk boundaries
- **Token count**: ~125 tokens/chunk (4 chars/token) → fits LLM context easily
- **Retrieval**: 3 chunks × 500 chars = ~1500 chars context (manageable for LLM)

**Tested alternatives**:
- 300 chars: Too fragmented, lost context
- 1000 chars: Too broad, diluted relevance

### Why Top-K = 3?

**Decision**: Retrieve 3 chunks per query

**Rationale**:
- Provides sufficient context without noise
- ~1500 chars total context (well within DeepSeek limits)
- Empirically tested: K=1 too narrow, K=5 introduced irrelevant chunks
- Configurable in `Config.TOP_K`

### Why DeepSeek?

**Decision**: Use DeepSeek API instead of GPT-4 or Claude

**Rationale**:
- Cost-effective (~1/10th price of GPT-4)
- OpenAI-compatible API (easy integration)
- Free tier available for testing
- Sufficient quality for grounded Q&A tasks
- Can swap to OpenAI by changing `base_url`

## Security Considerations

1. **API Keys**: Stored in `.env` (gitignored)
2. **Input Validation**: User queries not sanitized (future: add length limits)
3. **Rate Limiting**: No current implementation (future: add for production)
4. **Prompt Injection**: System prompt enforces context grounding (partial mitigation)

## Performance Characteristics

| Operation | Latency | Notes |
|-----------|---------|-------|
| Index Building | ~10s | One-time, offline |
| Query Embedding | ~50ms | Local CPU |
| FAISS Search | <1ms | 75 vectors |
| Context Formatting | <1ms | String operations |
| DeepSeek API | 500-2000ms | Network + LLM inference |
| **Total Query Time** | **0.5-2s** | Acceptable for chatbot |

## Scalability Analysis

Current system scales well for:
- **Up to 1M vectors**: FAISS IndexFlatL2 handles efficiently
- **Up to 100 QPS**: Local embedding bottleneck at ~50ms
- **Data updates**: Rebuild index in seconds

Bottlenecks:
- **DeepSeek API**: Rate limits, network latency
- **Embedding model**: Single-threaded CPU inference

Future optimizations:
- GPU acceleration for embeddings (10x faster)
- Approximate FAISS index (IVF, HNSW) for >1M vectors
- Batch query processing
- Caching frequent queries

## Monitoring & Debugging

**Test Retrieval**:
```bash
python3 scripts/test_retrieval.py
```
Shows retrieved chunks without LLM (validates FAISS + embeddings)

**Inspect Index**:
```python
from src.config import Config
import json

with open(Config.METADATA_FILE) as f:
    print(json.load(f))
```

**Logs**:
- Progress bars during indexing (tqdm)
- Console output for CLI scripts
- Error tracebacks for debugging

## Future Enhancements

1. **Hybrid Search**: Combine semantic (FAISS) + keyword (BM25)
2. **Re-ranking**: Two-stage retrieval with cross-encoder
3. **Streaming**: Stream LLM responses for better UX
4. **Memory**: Add conversation history for multi-turn chat
5. **Analytics**: Track query patterns, chunk utilization
6. **UI**: Streamlit or Gradio web interface
7. **Tests**: Pytest suite for unit/integration tests

## References

- [FAISS Documentation](https://github.com/facebookresearch/faiss/wiki)
- [Sentence-Transformers](https://www.sbert.net/)
- [DeepSeek API](https://platform.deepseek.com/api-docs/)
- [RAG Best Practices](https://www.anthropic.com/index/contextual-retrieval)
