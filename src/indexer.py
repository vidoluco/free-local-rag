"""
FAISS Indexer with Local Embeddings

Handles document chunking, embedding generation, and FAISS index creation.
"""

import json
import pickle
from typing import List, Dict
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

from .config import Config


class LocalEmbeddingIndexer:
    """Build FAISS index using local sentence-transformers embeddings."""

    def __init__(
        self,
        model_name: str = None,
        chunk_size: int = None,
        chunk_overlap: int = None
    ):
        """
        Initialize indexer with local embedding model.

        Args:
            model_name: Sentence-transformers model (defaults to Config.EMBEDDING_MODEL)
            chunk_size: Max characters per chunk (defaults to Config.CHUNK_SIZE)
            chunk_overlap: Overlap between chunks (defaults to Config.CHUNK_OVERLAP)
        """
        self.model_name = model_name or Config.EMBEDDING_MODEL
        self.chunk_size = chunk_size or Config.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or Config.CHUNK_OVERLAP

        print(f"Loading local embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        print(f"✓ Model loaded (embedding dimension: {self.embedding_dim})")

    def load_content(self, content_path: str = None) -> str:
        """
        Load content from file or directory.

        Supports single file or directory with multiple documents.
        For directories, loads all supported formats and aggregates.
        """
        from pathlib import Path
        from .loaders import DocumentLoader, ContentAggregator

        # Use provided path or get from config
        if content_path:
            path = Path(content_path)
        else:
            path = Config.get_content_path()

        # If it's a file, load directly
        if path.is_file():
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()

        # If it's a directory, load all documents and aggregate
        elif path.is_dir():
            print(f"Loading documents from directory: {path}")
            documents = DocumentLoader.load_directory(path)

            if not documents:
                raise FileNotFoundError(
                    f"No supported documents found in {path}. "
                    "Please add .txt, .pdf, .docx, or .md files."
                )

            print(f"Loaded {len(documents)} documents")
            content = ContentAggregator.aggregate_documents(documents)
            return content

        else:
            raise FileNotFoundError(f"Path not found: {path}")

    def chunk_by_sections(self, content: str) -> List[Dict[str, str]]:
        """
        Split content by page sections with metadata.

        Returns:
            List of dicts with 'text', 'source', 'section' keys
        """
        chunks = []
        sections = content.split('=== PAGINA:')

        for section in sections:
            if not section.strip():
                continue

            lines = section.strip().split('\n', 1)
            section_name = lines[0].strip().replace('===', '').strip()
            section_content = lines[1].strip() if len(lines) > 1 else ""

            if not section_content:
                continue

            # Split long sections into smaller chunks with overlap
            if len(section_content) <= self.chunk_size:
                chunks.append({
                    'text': section_content,
                    'source': 'content.txt',
                    'section': section_name
                })
            else:
                # Split with overlap
                start = 0
                part_num = 1
                while start < len(section_content):
                    end = start + self.chunk_size
                    chunk_text = section_content[start:end]

                    chunks.append({
                        'text': chunk_text,
                        'source': 'content.txt',
                        'section': f"{section_name} (part {part_num})"
                    })

                    start += self.chunk_size - self.chunk_overlap
                    part_num += 1

        return chunks

    def generate_embeddings(
        self,
        texts: List[str],
        batch_size: int = None
    ) -> np.ndarray:
        """
        Generate embeddings locally using sentence-transformers.

        Args:
            texts: List of text chunks
            batch_size: Batch size for encoding (defaults to Config.BATCH_SIZE)

        Returns:
            Numpy array of embeddings (N x embedding_dim)
        """
        batch_size = batch_size or Config.BATCH_SIZE
        print(f"Generating embeddings for {len(texts)} chunks...")
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        return embeddings.astype(np.float32)

    def create_faiss_index(self, embeddings: np.ndarray) -> faiss.Index:
        """Create FAISS L2 index from embeddings."""
        print(f"Creating FAISS index...")
        index = faiss.IndexFlatL2(self.embedding_dim)
        index.add(embeddings)
        print(f"✓ FAISS index created with {index.ntotal} vectors")
        return index

    def save_index(
        self,
        index: faiss.Index,
        chunks: List[Dict],
        embeddings: np.ndarray
    ):
        """Save FAISS index, chunks, and metadata to indices/ directory."""
        Config.ensure_dirs()

        # Save FAISS index
        faiss.write_index(index, str(Config.FAISS_INDEX_FILE))
        print(f"✓ FAISS index saved: {Config.FAISS_INDEX_FILE}")

        # Save chunks
        with open(Config.CHUNKS_FILE, 'wb') as f:
            pickle.dump(chunks, f)
        print(f"✓ Chunks saved: {Config.CHUNKS_FILE}")

        # Save metadata
        metadata = {
            'total_chunks': len(chunks),
            'embedding_dimension': int(self.embedding_dim),
            'model_name': self.model_name,
            'chunk_size': self.chunk_size,
            'chunk_overlap': self.chunk_overlap,
            'sections': list(set([c['section'] for c in chunks]))
        }

        with open(Config.METADATA_FILE, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
        print(f"✓ Metadata saved: {Config.METADATA_FILE}")

    def build(self, content_path: str = None) -> Dict:
        """
        Complete indexing pipeline.

        Args:
            content_path: Path to content.txt file (defaults to Config.CONTENT_FILE)

        Returns:
            Dict with statistics and file paths
        """
        print("=" * 60)
        print("Building FAISS Index with Local Embeddings")
        print("=" * 60)

        # Load content
        print(f"\n1. Loading content...")
        content = self.load_content(content_path)
        print(f"✓ Loaded {len(content)} characters")

        # Chunk content
        print("\n2. Chunking content by sections...")
        chunks = self.chunk_by_sections(content)
        print(f"✓ Created {len(chunks)} chunks")

        # Generate embeddings
        print("\n3. Generating embeddings locally...")
        texts = [c['text'] for c in chunks]
        embeddings = self.generate_embeddings(texts)
        print(f"✓ Generated embeddings: {embeddings.shape}")

        # Create FAISS index
        print("\n4. Creating FAISS index...")
        index = self.create_faiss_index(embeddings)

        # Save everything
        print("\n5. Saving index and metadata...")
        self.save_index(index, chunks, embeddings)

        print("\n" + "=" * 60)
        print("✅ Index Build Complete!")
        print("=" * 60)
        print(f"Total chunks: {len(chunks)}")
        print(f"Embedding dimension: {self.embedding_dim}")
        print(f"Index size: {index.ntotal} vectors")

        return {
            'total_chunks': len(chunks),
            'embedding_dimension': int(self.embedding_dim),
            'index_size': index.ntotal
        }
