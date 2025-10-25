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
        st.warning("⚠️ FAISS index not found. Please build the index first.")
        st.info("👉 Go to **Admin Panel** → **Build Index** to create the knowledge base from your documents.")
        return None
    except ValueError as e:
        st.error(f"Configuration error: {e}")
        st.info("Please check your environment variables and config.yaml settings.")
        return None


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

    # If chatbot failed to load, show helpful message
    if chatbot is None:
        st.error("💡 **Getting Started:**")
        st.write("1. Go to the **Admin Panel** (in sidebar)")
        st.write("2. Click **Build Index** tab")
        st.write("3. Click the 🔨 **Build Index** button")
        st.write("4. Wait for indexing to complete")
        st.write("5. Come back here to start chatting!")
        return

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
                # Get custom prompt from session state if set
                custom_prompt = st.session_state.get('custom_system_prompt')
                result = chatbot.chat(
                    prompt,
                    show_context=ui_config.get('show_retrieval_scores', False),
                    custom_system_prompt=custom_prompt
                )

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

    tab1, tab2, tab3, tab4 = st.tabs(["📄 Upload Documents", "🔨 Build Index", "🤖 AI Prompt", "⚙️ Configuration"])

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
            from datetime import datetime, timezone

            with open(Config.METADATA_FILE, 'r') as f:
                metadata = json.load(f)

            st.info(f"Current index: {metadata.get('total_chunks', 0)} chunks")
            st.write(f"**Model:** {metadata.get('model_name', 'Unknown')}")

            # Display timestamp if available
            if 'build_timestamp' in metadata:
                try:
                    build_time = datetime.fromisoformat(metadata['build_timestamp'])
                    now = datetime.now(timezone.utc)
                    time_diff = now - build_time

                    # Format human-readable time
                    if time_diff.days > 0:
                        time_ago = f"{time_diff.days} day{'s' if time_diff.days > 1 else ''} ago"
                    elif time_diff.seconds >= 3600:
                        hours = time_diff.seconds // 3600
                        time_ago = f"{hours} hour{'s' if hours > 1 else ''} ago"
                    elif time_diff.seconds >= 60:
                        minutes = time_diff.seconds // 60
                        time_ago = f"{minutes} minute{'s' if minutes > 1 else ''} ago"
                    else:
                        time_ago = "just now"

                    st.write(f"**Last indexed:** {time_ago}")
                    st.caption(f"({build_time.strftime('%Y-%m-%d %H:%M:%S UTC')})")
                except (ValueError, TypeError):
                    st.write(f"**Last indexed:** {metadata.get('build_timestamp', 'Unknown')}")
            else:
                st.write("**Last indexed:** Unknown (rebuild to add timestamp)")

        if st.button("🔨 Build Index"):
            with st.spinner("Building index... This may take a few minutes."):
                try:
                    indexer = LocalEmbeddingIndexer()
                    result = indexer.build()

                    st.success("✅ Index built successfully!")
                    st.write(f"Total chunks: {result['total_chunks']}")
                    st.write(f"Embedding dimension: {result['embedding_dimension']}")
                    st.info("♻️ Reloading app to use the new index...")

                    # Clear cache and reload app
                    st.cache_resource.clear()
                    st.rerun()

                except Exception as e:
                    st.error(f"❌ Error building index: {e}")

    with tab3:
        st.header("AI System Prompt")
        st.write("Customize the AI assistant's behavior by editing the system prompt.")

        # Get default prompt from config
        default_prompt = Config.SYSTEM_PROMPT

        # Initialize session state for custom prompt if not exists
        if 'custom_system_prompt' not in st.session_state:
            st.session_state['custom_system_prompt'] = None

        # Show current status
        if st.session_state.get('custom_system_prompt'):
            st.success("✅ Using custom prompt")
        else:
            st.info("ℹ️ Using default prompt from config.yaml")

        # Text area for editing prompt
        current_prompt = st.session_state.get('custom_system_prompt') or default_prompt
        edited_prompt = st.text_area(
            "System Prompt",
            value=current_prompt,
            height=300,
            help="This prompt defines how the AI assistant behaves and responds to queries."
        )

        col1, col2 = st.columns(2)

        with col1:
            if st.button("💾 Save Custom Prompt", use_container_width=True):
                if edited_prompt.strip():
                    st.session_state['custom_system_prompt'] = edited_prompt
                    st.success("✅ Custom prompt saved! It will be used for all new queries.")
                    st.rerun()
                else:
                    st.error("❌ Prompt cannot be empty")

        with col2:
            if st.button("🔄 Reset to Default", use_container_width=True):
                st.session_state['custom_system_prompt'] = None
                st.success("✅ Reset to default prompt from config.yaml")
                st.rerun()

        # Show preview of what's active
        with st.expander("📋 Preview Active Prompt"):
            active_prompt = st.session_state.get('custom_system_prompt') or default_prompt
            st.code(active_prompt, language=None)

    with tab4:
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
