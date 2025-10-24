# Client Content Directory

Place your client's documents here for indexing.

## Supported Formats

- **TXT** (.txt) - Plain text files
- **PDF** (.pdf) - PDF documents
- **DOCX** (.docx) - Microsoft Word documents
- **Markdown** (.md) - Markdown files

## Usage

### Option 1: Manual Upload
1. Copy your files directly into this directory
2. Run the index builder:
   ```bash
   python3 scripts/build_index.py
   ```

### Option 2: Using Ingest Script
```bash
python3 scripts/ingest_documents.py --source data/client_content
```

### Option 3: Web Interface
1. Start the web app: `streamlit run app.py`
2. Navigate to Admin Panel
3. Use the file uploader

## Document Organization

You can organize files in subdirectories - the system will recursively load all supported files:

```
client_content/
├── general/
│   ├── about.md
│   └── services.pdf
├── products/
│   ├── product_catalog.docx
│   └── pricing.txt
└── faq.md
```

## Notes

- Files are aggregated into a single knowledge base
- Each document becomes a section in the index
- Large files are automatically chunked for better retrieval
- Changes require rebuilding the index
