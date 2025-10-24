# Client Guide - Knowledge Base Assistant

Welcome to your AI-powered knowledge base chatbot! This guide will help you get started.

## What is This?

This is a RAG (Retrieval-Augmented Generation) system that:
- Lets you create an AI chatbot trained on YOUR documents
- Answers questions based on your company's knowledge base
- Provides accurate, source-cited responses
- Works with multiple document formats (PDF, Word, Text, Markdown)

## Quick Start (5 Minutes)

### 1. Initial Setup

Run the setup script:
```bash
./setup.sh
```

This will:
- Create a Python virtual environment
- Install all dependencies
- Create necessary folders

### 2. Configure API Key

Edit the `.env` file and add your DeepSeek API key:
```
DEEPSEEK_API_KEY=sk-your-api-key-here
```

Get your API key from: https://platform.deepseek.com

### 3. Add Your Documents

Place your documents in `data/client_content/`:
- Drag and drop PDF files
- Add Word documents (.docx)
- Include text files (.txt)
- Add Markdown files (.md)

### 4. Build the Knowledge Base

```bash
source venv/bin/activate
python3 scripts/build_index.py
```

This processes your documents and creates a searchable index (takes 1-5 minutes).

### 5. Start the Chatbot

**Web Interface** (Recommended):
```bash
streamlit run app.py
```
Then open http://localhost:8501 in your browser.

**Command Line Interface**:
```bash
python3 scripts/run_chatbot.py
```

## Using the Web Interface

### Chat Tab
- Ask questions about your documents
- Get instant answers with source citations
- View conversation history

### Admin Panel
- **Upload Documents**: Drag & drop new files
- **Build Index**: Process new documents
- **Configuration**: View current settings

## Adding More Content

### Option 1: Web Upload
1. Go to Admin Panel in the web interface
2. Select "Upload Documents"
3. Drag files or click to browse
4. Click "Save Files"
5. Go to "Build Index" tab and rebuild

### Option 2: Manual File Copy
1. Copy files to `data/client_content/`
2. Run: `python3 scripts/build_index.py`

### Option 3: Command Line Tool
```bash
python3 scripts/ingest_documents.py --source /path/to/your/files
```

## Supported Document Types

| Format | Extension | Notes |
|--------|-----------|-------|
| Plain Text | .txt | Best for structured content |
| PDF | .pdf | Automatically extracts text |
| Word | .docx | Tables and text supported |
| Markdown | .md | Formatted documentation |

## Tips for Best Results

### Document Preparation
✅ **Good**: Clear, well-organized content with headers
❌ **Avoid**: Scanned images (use OCR first), heavily formatted documents

### Writing Questions
✅ **Good**: "What are the pricing options for premium plans?"
❌ **Avoid**: "Tell me everything about everything"

### Content Organization
- Use clear section headers in your documents
- Break long documents into logical files
- Include contact information in a dedicated file
- Keep FAQs in a separate document

## Updating Content

When you add new documents or modify existing ones:

1. Add/update files in `data/client_content/`
2. Rebuild the index: `python3 scripts/build_index.py`
3. Restart the web app if it's running

Changes take effect after rebuilding the index.

## Troubleshooting

### "FAISS index not found"
**Solution**: Build the index first with `python3 scripts/build_index.py`

### "DEEPSEEK_API_KEY not found"
**Solution**: Add your API key to the `.env` file

### "No documents found"
**Solution**: Add documents to `data/client_content/` folder

### Web interface won't start
**Solution**: Make sure virtual environment is active:
```bash
source venv/bin/activate
streamlit run app.py
```

### Chatbot gives wrong answers
**Solutions**:
- Ensure your documents contain the information
- Check that documents were properly indexed
- Try rephrasing your question
- Verify document content is readable (not scanned images)

## Customization

Your system administrator can customize:
- Company branding and colors
- System prompt and behavior
- Retrieval parameters
- Supported languages

See `CUSTOMIZATION.md` for details.

## Support

For technical issues or questions, contact your system administrator.

---

**Need Help?**
- Check `README.md` for technical details
- See `CUSTOMIZATION.md` for configuration options
- Review example use cases in `data/examples/`
