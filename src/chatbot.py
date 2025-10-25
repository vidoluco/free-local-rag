"""
RAG Chatbot with Local Embeddings + Perplexity Sonar LLM

Handles query embedding, FAISS retrieval, and chat completion.
"""

import json
import pickle
from typing import List, Dict, Tuple
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from dotenv import load_dotenv

from .config import Config


class RAGChatbot:
    """RAG chatbot with configurable knowledge base and system prompt."""

    def __init__(
        self,
        model_name: str = None,
        top_k: int = None
    ):
        """
        Initialize chatbot with FAISS index and Perplexity API.

        Args:
            model_name: Sentence-transformers model (defaults to Config.EMBEDDING_MODEL)
            top_k: Number of chunks to retrieve (defaults to Config.TOP_K)
        """
        self.model_name = model_name or Config.EMBEDDING_MODEL
        self.top_k = top_k or Config.TOP_K

        # Load environment variables
        load_dotenv()

        # Initialize Perplexity client
        self.api_key = Config.get_api_key()
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=Config.PERPLEXITY_BASE_URL
        )

        # Load local embedding model
        print(f"Loading local embedding model: {self.model_name}")
        self.embedding_model = SentenceTransformer(self.model_name)
        print(f"✓ Embedding model loaded")

        # Load FAISS index
        print("Loading FAISS index...")
        self.load_index()
        print(f"✓ Index loaded with {self.index.ntotal} vectors\n")

    def load_index(self):
        """Load FAISS index, chunks, and metadata from indices/ directory."""
        if not Config.FAISS_INDEX_FILE.exists():
            raise FileNotFoundError(
                f"FAISS index not found at {Config.FAISS_INDEX_FILE}. "
                "Run build_index.py first."
            )

        # Load FAISS index
        self.index = faiss.read_index(str(Config.FAISS_INDEX_FILE))

        # Load chunks
        with open(Config.CHUNKS_FILE, 'rb') as f:
            self.chunks = pickle.load(f)

        # Load metadata
        with open(Config.METADATA_FILE, 'r', encoding='utf-8') as f:
            self.metadata = json.load(f)

    def embed_query(self, query: str) -> np.ndarray:
        """Generate embedding for query using local model."""
        embedding = self.embedding_model.encode(query, convert_to_numpy=True)
        return embedding.astype(np.float32)

    def retrieve(self, query: str) -> List[Dict]:
        """
        Retrieve top-k relevant chunks for query.

        Args:
            query: User's question

        Returns:
            List of dicts with 'text', 'section', 'score', 'distance'
        """
        # Generate query embedding locally
        query_embedding = self.embed_query(query)

        # Search FAISS index
        distances, indices = self.index.search(
            query_embedding.reshape(1, -1),
            self.top_k
        )

        # Format results
        results = []
        for idx, (distance, chunk_idx) in enumerate(zip(distances[0], indices[0])):
            if chunk_idx == -1:  # No more results
                continue

            chunk = self.chunks[chunk_idx]
            # Convert L2 distance to similarity score
            similarity = 1 / (1 + distance)

            results.append({
                'text': chunk['text'],
                'section': chunk['section'],
                'source': chunk['source'],
                'score': float(similarity),
                'distance': float(distance),
                'rank': idx + 1
            })

        return results

    def format_context(self, results: List[Dict]) -> Tuple[str, List[str]]:
        """
        Format retrieved chunks into context for LLM.

        Args:
            results: Retrieved chunks

        Returns:
            Tuple of (formatted_context, list_of_sources)
        """
        if not results:
            return "No relevant content found.", []

        context_parts = []
        sources = []

        for result in results:
            section = result['section']
            text = result['text']

            # Add source reference
            if section not in sources:
                sources.append(section)

            # Format context entry
            context_parts.append(f"[Section: {section}]\n{text}\n")

        formatted_context = "\n---\n".join(context_parts)
        return formatted_context, sources

    def chat(self, query: str, show_context: bool = False, custom_system_prompt: str = None) -> Dict:
        """
        Process user query through RAG pipeline.

        Args:
            query: User's question in Italian
            show_context: Whether to return retrieved context (for debugging)
            custom_system_prompt: Optional custom system prompt to override Config.SYSTEM_PROMPT

        Returns:
            Dict with 'answer', 'sources', optionally 'context' and 'retrieved_chunks'
        """
        # Retrieve relevant chunks
        retrieved = self.retrieve(query)

        # Format context
        context, sources = self.format_context(retrieved)

        # Create user message with context
        user_message = f"""Context from knowledge base:
{context}

User question: {query}

Provide a complete answer based on the provided context."""

        # Use custom prompt if provided, otherwise use config
        system_prompt = custom_system_prompt if custom_system_prompt is not None else Config.SYSTEM_PROMPT

        # Call Perplexity API
        try:
            response = self.client.chat.completions.create(
                model=Config.PERPLEXITY_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=Config.PERPLEXITY_TEMPERATURE,
                max_tokens=Config.PERPLEXITY_MAX_TOKENS
            )

            answer = response.choices[0].message.content

            result = {
                'answer': answer,
                'sources': sources,
                'query': query
            }

            if show_context:
                result['context'] = context
                result['retrieved_chunks'] = retrieved

            return result

        except Exception as e:
            return {
                'answer': f"Error communicating with service: {str(e)}",
                'sources': [],
                'query': query,
                'error': str(e)
            }

    def run_interactive(self):
        """Run interactive CLI chatbot."""
        company_info = Config.get_company_info()
        company_name = company_info.get('name', 'Knowledge Base')
        description = company_info.get('description', '')

        print("=" * 70)
        print(f"{company_name} - AI Assistant")
        print("=" * 70)
        if description:
            print(description)
        print("\nAsk questions about our knowledge base...")
        print("\nCommands: 'exit' to quit, 'help' for examples\n")

        while True:
            try:
                # Get user input
                query = input("\n💬 Tu: ").strip()

                if not query:
                    continue

                if query.lower() in ['exit', 'quit']:
                    print("\n👋 Thank you! Goodbye!")
                    break

                if query.lower() == 'help':
                    print("\n📋 Example questions:")
                    print("  - What services do you offer?")
                    print("  - How can I contact you?")
                    print("  - Tell me about your products")
                    print("  - What are your pricing options?")
                    continue

                # Process query
                print("\n🤖 Assistente: ", end="", flush=True)
                result = self.chat(query)

                # Display answer
                print(result['answer'])

                # Display sources
                if result['sources']:
                    print(f"\n📚 Sources: {', '.join(result['sources'][:3])}")

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")


# Backward compatibility alias
TourChatbot = RAGChatbot
