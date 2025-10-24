# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Cover as a senior engineer the full loop from design (architect), build (engineer, builder), test (chaos reviewer, senior code reviewer), deploy (cloud architect) of SDLC.

## Project Overview

RAG chatbot system for Italian tour operator content (viaggiarebucarest.com) using DeepSeek API and FAISS indexing. Content is in Italian covering Romanian tours, destinations, and booking information.

## Architecture

**Phase 1: Data Preparation (COMPLETED)**
- Manual content curation from viaggiarebucarest.com
- Structured text file with tour programs, contact info, reviews
- High-quality Italian content ready for RAG

**Phase 2: RAG System (TO BE IMPLEMENTED)**
- Text chunking and embedding generation
- FAISS vector index creation
- DeepSeek API integration for chat completion
- Query → retrieval → generation pipeline

**Phase 3: Chatbot Interface (FUTURE)**
- CLI or web interface for user queries
- Context-aware responses using retrieved content

## Data Flow

```
data/content.txt (manual curated content)
  → [NEXT] text chunking → chunks
  → [NEXT] embedding generation → FAISS index
  → [NEXT] chatbot with DeepSeek API
```

## Key Commands

```bash
# Environment setup
pip3 install -r requirements.txt
cp .env.example .env  # Then add DEEPSEEK_API_KEY

# View manual content
cat data/content.txt

# Future: RAG system
# python3 build_index.py    # Create FAISS embeddings
# python3 chatbot.py         # Run chatbot interface
```

## Data Structure

- `data/content.txt`: Manually curated content from viaggiarebucarest.com with tour programs, reviews, contact info
- Content is organized by page sections with clear separators
- High-quality structured text ready for chunking and embedding

## Content Characteristics

- **Language**: Italian
- **Domain**: Tour operator services in Romania
- **Topics**: Bucharest tours, Dracula Castle, Bear Sanctuary, pricing, contact info
- **Key contacts**: +40 774621133, +40 774621205, viaggiareabucarest@yahoo.com
- **Content quality**: Includes customer reviews, tour descriptions, booking info

## Next Implementation Steps

1. **Text Chunking**: Split markdown content into semantic chunks (~500 tokens with overlap)
2. **Embeddings**: Generate embeddings using OpenAI-compatible API (DeepSeek supports text-embedding models)
3. **FAISS Index**: Build index with `faiss.IndexFlatL2` or `IndexIVFFlat` for larger datasets
4. **Retrieval**: Implement similarity search (top-k=3-5 chunks per query)
5. **Generation**: Use DeepSeek Chat API with system prompt + retrieved context
6. **Evaluation**: Test with Italian queries about tours, prices, locations

## Development Principles

- Senior engineer quality: clean, maintainable, production-ready code
- Minimal documentation: code should be self-explanatory
- Manual content curation for quality over quantity
- Focus on RAG system implementation with DeepSeek + FAISS
