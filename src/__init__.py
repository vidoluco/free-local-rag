"""
Essential RAG System

Tour operator chatbot with local embeddings and FAISS vector search.
"""

__version__ = "1.0.0"
__author__ = "Essential RAG Team"

from .config import Config
from .indexer import LocalEmbeddingIndexer
from .chatbot import TourChatbot

__all__ = ["Config", "LocalEmbeddingIndexer", "TourChatbot"]
