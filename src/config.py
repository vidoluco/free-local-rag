"""
Configuration Module

Centralized configuration for RAG system paths, models, and parameters.
"""

from pathlib import Path
import os


class Config:
    """Central configuration for Essential RAG System."""

    # Project paths
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    INDICES_DIR = PROJECT_ROOT / "indices"
    DOCS_DIR = PROJECT_ROOT / "docs"

    # Data files
    CONTENT_FILE = DATA_DIR / "content.txt"

    # Index files
    FAISS_INDEX_FILE = INDICES_DIR / "faiss_index.index"
    CHUNKS_FILE = INDICES_DIR / "chunks.pkl"
    METADATA_FILE = INDICES_DIR / "metadata.json"

    # Embedding model
    EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"
    EMBEDDING_DIMENSION = 384

    # Chunking parameters
    CHUNK_SIZE = 500  # characters
    CHUNK_OVERLAP = 50  # characters

    # Retrieval parameters
    TOP_K = 3  # Number of chunks to retrieve
    BATCH_SIZE = 32  # Batch size for embedding generation

    # DeepSeek API
    DEEPSEEK_API_KEY_ENV = "DEEPSEEK_API_KEY"
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com/v1")
    DEEPSEEK_MODEL = "deepseek-chat"
    DEEPSEEK_TEMPERATURE = 0.3
    DEEPSEEK_MAX_TOKENS = 500

    # System prompt
    SYSTEM_PROMPT = """Sei l'assistente virtuale ufficiale di Viaggiare Bucarest, un tour operator italiano in Romania con oltre 30 anni di esperienza (dal 1991).

Il tuo ruolo:
- Fornire supporto promozionale e assistenza ai clienti in italiano
- Rispondere alle domande sui tour, prezzi, destinazioni e servizi
- Essere entusiasta, cordiale e professionale
- Utilizzare SOLO le informazioni fornite nel contesto
- Quando rilevante, includere i contatti: +40 774621133, +40 774621205, viaggiareabucarest@yahoo.com

Regole importanti:
- Rispondi SOLO basandoti sul contesto fornito
- Se l'informazione non è nel contesto, dillo chiaramente
- Mantieni un tono promozionale ma genuino
- Parla sempre in italiano
- Sii conciso ma completo"""

    @classmethod
    def ensure_dirs(cls):
        """Create necessary directories if they don't exist."""
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.INDICES_DIR.mkdir(parents=True, exist_ok=True)
        cls.DOCS_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_api_key(cls) -> str:
        """Get DeepSeek API key from environment."""
        api_key = os.getenv(cls.DEEPSEEK_API_KEY_ENV)
        if not api_key:
            raise ValueError(
                f"{cls.DEEPSEEK_API_KEY_ENV} not found in environment. "
                "Please set it in .env file."
            )
        return api_key
