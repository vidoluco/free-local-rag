"""
Configuration Module

Centralized configuration for RAG system paths, models, and parameters.
Loads from config.yaml for client-specific customization.
"""

from pathlib import Path
import os
import yaml
from typing import Dict, Any


class Config:
    """Central configuration for Essential RAG System."""

    # Project paths
    PROJECT_ROOT = Path(__file__).parent.parent
    CONFIG_FILE = PROJECT_ROOT / "config.yaml"
    DATA_DIR = PROJECT_ROOT / "data"
    INDICES_DIR = PROJECT_ROOT / "indices"
    DOCS_DIR = PROJECT_ROOT / "docs"

    # Default data paths
    CLIENT_CONTENT_DIR = DATA_DIR / "client_content"
    SAMPLE_DATA_DIR = DATA_DIR / "sample"
    EXAMPLES_DIR = DATA_DIR / "examples"

    # Backward compatibility
    CONTENT_FILE = DATA_DIR / "content.txt"

    # Index files
    FAISS_INDEX_FILE = INDICES_DIR / "faiss_index.index"
    CHUNKS_FILE = INDICES_DIR / "chunks.pkl"
    METADATA_FILE = INDICES_DIR / "metadata.json"

    # Configuration cache
    _config_data: Dict[str, Any] = None

    @classmethod
    def load_config(cls) -> Dict[str, Any]:
        """Load configuration from config.yaml file."""
        if cls._config_data is None:
            if cls.CONFIG_FILE.exists():
                with open(cls.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    cls._config_data = yaml.safe_load(f)
            else:
                # Return default configuration if file doesn't exist
                cls._config_data = cls._get_default_config()
        return cls._config_data

    @classmethod
    def _get_default_config(cls) -> Dict[str, Any]:
        """Return default configuration when config.yaml doesn't exist."""
        return {
            'company': {
                'name': 'Your Company',
                'contact': {'email': 'contact@example.com'}
            },
            'language': {'primary': 'en', 'assistant_name': 'AI Assistant'},
            'system_prompt': {
                'role': 'professional assistant',
                'instructions': 'You are a helpful AI assistant.'
            },
            'rag': {
                'chunk_size': 500,
                'chunk_overlap': 50,
                'top_k': 3,
                'batch_size': 32
            },
            'embedding': {
                'model': 'paraphrase-multilingual-MiniLM-L12-v2',
                'dimension': 384
            },
            'llm': {
                'provider': 'perplexity',
                'model': 'sonar',
                'temperature': 0.3,
                'max_tokens': 500,
                'api_base': 'https://api.perplexity.ai'
            },
            'ui': {
                'title': 'Knowledge Base Assistant',
                'page_icon': '🤖',
                'show_sources': True
            },
            'data': {
                'input_folder': 'data/client_content',
                'supported_formats': ['txt', 'pdf', 'docx', 'md']
            }
        }

    @classmethod
    def get(cls, key_path: str, default=None):
        """
        Get configuration value using dot notation.

        Example: Config.get('company.name') or Config.get('rag.chunk_size')
        """
        config = cls.load_config()
        keys = key_path.split('.')
        value = config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    # Embedding model properties
    @classmethod
    @property
    def EMBEDDING_MODEL(cls) -> str:
        return cls.get('embedding.model', 'paraphrase-multilingual-MiniLM-L12-v2')

    @classmethod
    @property
    def EMBEDDING_DIMENSION(cls) -> int:
        return cls.get('embedding.dimension', 384)

    # Chunking parameters
    @classmethod
    @property
    def CHUNK_SIZE(cls) -> int:
        return cls.get('rag.chunk_size', 500)

    @classmethod
    @property
    def CHUNK_OVERLAP(cls) -> int:
        return cls.get('rag.chunk_overlap', 50)

    # Retrieval parameters
    @classmethod
    @property
    def TOP_K(cls) -> int:
        return cls.get('rag.top_k', 3)

    @classmethod
    @property
    def BATCH_SIZE(cls) -> int:
        return cls.get('rag.batch_size', 32)

    # Perplexity API
    PERPLEXITY_API_KEY_ENV = "PERPLEXITY_API_KEY"

    @classmethod
    @property
    def PERPLEXITY_BASE_URL(cls) -> str:
        # Try Streamlit secrets first (for Streamlit Cloud)
        try:
            import streamlit as st
            if "PERPLEXITY_API_BASE" in st.secrets:
                return st.secrets["PERPLEXITY_API_BASE"]
        except (ImportError, FileNotFoundError):
            pass

        # Fall back to environment variable
        env_url = os.getenv("PERPLEXITY_API_BASE")
        if env_url:
            return env_url

        return cls.get('llm.api_base', 'https://api.perplexity.ai')

    @classmethod
    @property
    def PERPLEXITY_MODEL(cls) -> str:
        return cls.get('llm.model', 'sonar')

    @classmethod
    @property
    def PERPLEXITY_TEMPERATURE(cls) -> float:
        return cls.get('llm.temperature', 0.3)

    @classmethod
    @property
    def PERPLEXITY_MAX_TOKENS(cls) -> int:
        return cls.get('llm.max_tokens', 500)

    # System prompt - now dynamic
    @classmethod
    @property
    def SYSTEM_PROMPT(cls) -> str:
        """Generate system prompt from config.yaml template."""
        config = cls.load_config()
        company_name = config.get('company', {}).get('name', 'Your Company')
        language = config.get('language', {}).get('primary', 'en')
        role = config.get('system_prompt', {}).get('role', 'professional assistant')
        instructions = config.get('system_prompt', {}).get('instructions', '')

        # Format the template
        prompt = instructions.format(
            company_name=company_name,
            language=language,
            role=role
        )

        return prompt

    @classmethod
    def get_company_info(cls) -> Dict[str, Any]:
        """Get company information from config."""
        return cls.get('company', {})

    @classmethod
    def get_ui_config(cls) -> Dict[str, Any]:
        """Get UI configuration."""
        return cls.get('ui', {})

    @classmethod
    def get_data_config(cls) -> Dict[str, Any]:
        """Get data source configuration."""
        return cls.get('data', {})

    @classmethod
    def ensure_dirs(cls):
        """Create necessary directories if they don't exist."""
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.INDICES_DIR.mkdir(parents=True, exist_ok=True)
        cls.DOCS_DIR.mkdir(parents=True, exist_ok=True)
        cls.CLIENT_CONTENT_DIR.mkdir(parents=True, exist_ok=True)
        cls.SAMPLE_DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.EXAMPLES_DIR.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_api_key(cls) -> str:
        """
        Get Perplexity API key from Streamlit secrets or environment.

        Checks in order:
        1. Streamlit secrets (st.secrets) - for Streamlit Cloud deployment
        2. Environment variables (os.getenv) - for local development
        """
        # Try Streamlit secrets first (for Streamlit Cloud)
        try:
            import streamlit as st
            if "PERPLEXITY_API_KEY" in st.secrets:
                return st.secrets["PERPLEXITY_API_KEY"]
        except (ImportError, FileNotFoundError):
            # Streamlit not available or secrets not configured
            pass

        # Fall back to environment variable (for local development)
        api_key = os.getenv(cls.PERPLEXITY_API_KEY_ENV)
        if not api_key:
            raise ValueError(
                f"{cls.PERPLEXITY_API_KEY_ENV} not found in Streamlit secrets or environment. "
                "Please set it in Streamlit Cloud Settings → Secrets or in .env file."
            )
        return api_key

    @classmethod
    def get_content_path(cls) -> Path:
        """Get the primary content path for indexing."""
        # Check config for custom input folder
        input_folder = cls.get('data.input_folder', 'data/client_content')
        content_dir = cls.PROJECT_ROOT / input_folder

        # Backward compatibility: check for old content.txt
        if cls.CONTENT_FILE.exists():
            return cls.CONTENT_FILE

        # Otherwise return the content directory
        return content_dir
