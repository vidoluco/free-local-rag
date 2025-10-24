#!/usr/bin/env python3
"""
Build FAISS Index CLI

Creates FAISS vector index from tour content using local embeddings.

Usage:
    python3 scripts/build_index.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.indexer import LocalEmbeddingIndexer


def main():
    """Build FAISS index using LocalEmbeddingIndexer."""
    try:
        indexer = LocalEmbeddingIndexer()
        result = indexer.build()

        print("\n🎉 Ready for chatbot!")
        print("Run: python3 scripts/run_chatbot.py")

    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        print("Please ensure data/content.txt exists.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
