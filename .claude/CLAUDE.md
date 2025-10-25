# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Cover as a senior engineer the full loop from design (architect), build (engineer, builder), test (chaos reviewer, senior code reviewer), deploy (cloud architect) of SDLC.

## Project Overview

White-label RAG (Retrieval-Augmented Generation) chatbot system template ready for client demos and deployments. Supports multiple document formats, fully configurable via config.yaml, with Streamlit web UI and CLI interfaces.

## Architecture

**Current State: Production-Ready Template**
- Multi-format document loading (PDF, DOCX, TXT, Markdown, web scraping)
- FAISS vector index with local embeddings (sentence-transformers)
- Perplexity Sonar API for chat completion
- Streamlit web interface + CLI chatbot
- Configurable via config.yaml for client customization

## System Components

```
Documents (PDF/DOCX/TXT/MD)
  → src/loaders.py (DocumentLoader)
  → src/indexer.py (LocalEmbeddingIndexer)
  → FAISS index + chunks
  → src/chatbot.py (RAGChatbot)
  → Perplexity API
  → app.py (Streamlit UI) or CLI
```

## Key Commands

```bash
# Setup
./setup.sh                              # One-command setup
cp .env.example .env                    # Then add PERPLEXITY_API_KEY

# Build index
python3 scripts/build_index.py          # Build from data/client_content/

# Run interfaces
streamlit run app.py                    # Web UI (recommended)
python3 scripts/run_chatbot.py          # CLI chatbot

# Testing
python3 scripts/test_retrieval.py       # Test retrieval quality
```

## Project Structure

- **app.py**: Streamlit web interface (chat + admin panel)
- **config.yaml**: Client configuration (company info, prompts, RAG params)
- **src/config.py**: Configuration loader with YAML + env support
- **src/loaders.py**: Multi-format document loaders
- **src/indexer.py**: FAISS index builder with local embeddings
- **src/chatbot.py**: RAG chatbot with retrieval + generation
- **scripts/**: Build index, run chatbot, ingest documents, test retrieval
- **data/client_content/**: Client documents (gitignored)
- **data/sample/**: Demo/sample data
- **data/examples/**: Reference implementations (e.g., tour operator)
- **indices/**: Generated FAISS index (gitignored)

## Configuration System

All client-specific settings in `config.yaml`:
- **company**: Name, description, contact info, branding
- **language**: Primary language, assistant name
- **system_prompt**: Role, behavior instructions (supports template variables)
- **rag**: Chunk size, overlap, top-k retrieval, batch size
- **embedding**: Model name, dimension
- **llm**: Provider (perplexity), model (sonar), temperature, max_tokens
- **ui**: Title, icon, theme, welcome message
- **data**: Input folder, supported formats

Environment variables in `.env`:
- **PERPLEXITY_API_KEY**: API key (required)
- **PERPLEXITY_API_BASE**: API base URL (optional override)

## LLM Provider: Perplexity Sonar

- **API**: OpenAI-compatible chat completions API
- **Model**: "sonar" (configurable in config.yaml)
- **Base URL**: https://api.perplexity.ai
- **Key**: Set in .env or Streamlit secrets (for cloud deployment)

## Deployment Modes

**Local Development**:
- Use .env file for API key
- Run via `streamlit run app.py`

**Streamlit Cloud**:
- Set secrets in app settings (PERPLEXITY_API_KEY)
- Config checks st.secrets first, then os.getenv()
- Automatic deployment from git push

## Client Customization Workflow

1. **Configure**: Edit config.yaml with client info
2. **Documents**: Add to data/client_content/
3. **Build**: Run scripts/build_index.py
4. **Test**: Use Streamlit UI or CLI to verify
5. **Deploy**: Push to Streamlit Cloud or self-host

## Development Principles

- Production-ready code: clean, modular, maintainable
- Zero client data in git (data/client_content/ in .gitignore)
- Configuration over code (use config.yaml, not hardcoding)
- Multi-language support (use language-agnostic prompts)
- Local embeddings (cost-effective, no API for embeddings)
- Comprehensive error handling (graceful degradation)
- Documentation for handoff (CLIENT_GUIDE.md, CUSTOMIZATION.md)

## Example Use Case

Original system: Italian tour operator (viaggiarebucarest.com)
- See data/examples/tour_operator/ for reference implementation
- Demonstrates multi-language support (Italian)
- Shows real-world content structure

## Testing & Quality

- **scripts/test_retrieval.py**: Test retrieval quality
- **Admin panel**: Upload docs, rebuild index, customize prompt
- **UI config**: Enable show_retrieval_scores for debugging
- **Metadata**: Check indices/metadata.json for index stats

## Common Tasks

**Add new client**:
1. Copy config.yaml template
2. Edit company info, system prompt, language
3. Add client documents to data/client_content/
4. Build index
5. Test and deploy

**Update LLM provider**:
- Edit config.yaml llm section
- Update Config class properties (PERPLEXITY_* → NEW_PROVIDER_*)
- Update chatbot.py API client initialization

**Change embedding model**:
- Edit config.yaml embedding section
- Rebuild index (embeddings will be regenerated)

**Multi-language deployment**:
- Set language.primary in config.yaml
- Translate system_prompt.instructions
- Use multilingual embedding model (default supports 50+ languages)
