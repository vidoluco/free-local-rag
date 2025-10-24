#!/usr/bin/env python3
"""
Streamlit Web Interface for RAG System

Production-ready web UI for knowledge base chatbot with admin features.

Usage:
    streamlit run app.py
"""

import streamlit as st
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import Config
from src.chatbot import RAGChatbot
from src.indexer import LocalEmbeddingIndexer
from src.loaders import DocumentLoader, ContentAggregator


# Page configuration
ui_config = Config.get_ui_config()
st.set_page_config(
    page_title=ui_config.get('title', 'Knowledge Base Assistant'),
    page_icon=ui_config.get('page_icon', '🤖'),
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_resource
def load_chatbot():
    """Load and cache the RAG chatbot."""
    try:
        return RAGChatbot()
    except FileNotFoundError:
        st.error("FAISS index not found. Please build the index first using scripts/build_index.py")
        st.stop()
    except ValueError as e:
        st.error(f"Configuration error: {e}")
        st.stop()


def chat_interface():
    """Main chat interface."""
    company_info = Config.get_company_info()
    company_name = company_info.get('name', 'Knowledge Base')

    st.title(f"{company_name} Assistant")

    # Show welcome message
    welcome_msg = ui_config.get('welcome_message', '').format(company_name=company_name)
    if welcome_msg:
        st.info(welcome_msg)

    # Load chatbot
    chatbot = load_chatbot()

    # Initialize chat history in session state
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            # Show sources if available
            if message.get("sources") and ui_config.get('show_sources', True):
                with st.expander("📚 Sources"):
                    st.write(", ".join(message["sources"]))

    # Chat input
    if prompt := st.chat_input("Ask me anything..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get chatbot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = chatbot.chat(prompt, show_context=ui_config.get('show_retrieval_scores', False))

                st.markdown(result['answer'])

                # Show sources
                if result.get('sources') and ui_config.get('show_sources', True):
                    with st.expander("📚 Sources"):
                        st.write(", ".join(result['sources']))

                # Debug: Show retrieval scores
                if ui_config.get('show_retrieval_scores', False) and result.get('retrieved_chunks'):
                    with st.expander("🔍 Debug: Retrieval Scores"):
                        for chunk in result['retrieved_chunks']:
                            st.write(f"**{chunk['section']}** - Score: {chunk['score']:.3f}")

        # Add assistant message to history
        st.session_state.messages.append({
            "role": "assistant",
            "content": result['answer'],
            "sources": result.get('sources', [])
        })


def admin_panel():
    """Admin panel for document management."""
    st.title("Admin Panel")

    tab1, tab2, tab3 = st.tabs(["📄 Upload Documents", "🔨 Build Index", "⚙️ Configuration"])

    with tab1:
        st.header("Upload Documents")
        st.write("Upload documents to add to the knowledge base.")

        uploaded_files = st.file_uploader(
            "Choose files",
            accept_multiple_files=True,
            type=['txt', 'pdf', 'docx', 'md']
        )

        if uploaded_files:
            st.success(f"Selected {len(uploaded_files)} file(s)")

            if st.button("Save Files"):
                Config.ensure_dirs()
                saved_count = 0

                for uploaded_file in uploaded_files:
                    # Save to client_content directory
                    save_path = Config.CLIENT_CONTENT_DIR / uploaded_file.name
                    with open(save_path, 'wb') as f:
                        f.write(uploaded_file.getbuffer())
                    saved_count += 1

                st.success(f"✅ Saved {saved_count} file(s) to {Config.CLIENT_CONTENT_DIR}")
                st.info("Next: Go to 'Build Index' tab to index the new documents")

    with tab2:
        st.header("Build FAISS Index")
        st.write("Build or rebuild the vector index from your documents.")

        # Show current index info
        if Config.METADATA_FILE.exists():
            import json
            with open(Config.METADATA_FILE, 'r') as f:
                metadata = json.load(f)

            st.info(f"Current index: {metadata.get('total_chunks', 0)} chunks")
            st.write(f"Model: {metadata.get('model_name', 'Unknown')}")
            st.write(f"Last updated: {Config.FAISS_INDEX_FILE.stat().st_mtime if Config.FAISS_INDEX_FILE.exists() else 'Never'}")

        if st.button("🔨 Build Index"):
            with st.spinner("Building index... This may take a few minutes."):
                try:
                    indexer = LocalEmbeddingIndexer()
                    result = indexer.build()

                    st.success("✅ Index built successfully!")
                    st.write(f"Total chunks: {result['total_chunks']}")
                    st.write(f"Embedding dimension: {result['embedding_dimension']}")
                    st.warning("Please restart the app to use the new index.")

                except Exception as e:
                    st.error(f"❌ Error building index: {e}")

    with tab3:
        st.header("Configuration")

        company_info = Config.get_company_info()

        st.subheader("Company Information")
        st.write(f"**Name:** {company_info.get('name', 'N/A')}")
        st.write(f"**Description:** {company_info.get('description', 'N/A')}")

        contact = company_info.get('contact', {})
        if contact:
            st.write(f"**Email:** {contact.get('email', 'N/A')}")
            st.write(f"**Phone:** {contact.get('phone', 'N/A')}")

        st.subheader("RAG Parameters")
        st.write(f"**Chunk Size:** {Config.CHUNK_SIZE}")
        st.write(f"**Top K:** {Config.TOP_K}")
        st.write(f"**Embedding Model:** {Config.EMBEDDING_MODEL}")

        st.info("To modify configuration, edit config.yaml and restart the app.")


def main():
    """Main application."""

    # Sidebar navigation
    with st.sidebar:
        st.title("Navigation")

        page = st.radio(
            "Go to",
            ["💬 Chat", "⚙️ Admin Panel"],
            label_visibility="collapsed"
        )

        st.divider()

        # Company info in sidebar
        company_info = Config.get_company_info()
        st.subheader(company_info.get('name', 'Knowledge Base'))

        description = company_info.get('description', '')
        if description:
            st.caption(description)

        contact = company_info.get('contact', {})
        if contact:
            st.divider()
            st.caption("**Contact Us**")
            if contact.get('email'):
                st.caption(f"📧 {contact['email']}")
            if contact.get('phone'):
                st.caption(f"📞 {contact['phone']}")

    # Route to selected page
    if page == "💬 Chat":
        chat_interface()
    else:
        admin_panel()


if __name__ == "__main__":
    main()
