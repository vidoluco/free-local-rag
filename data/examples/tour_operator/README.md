# Data Directory

This directory contains the source content for the RAG system.

## Files

### `content.txt`
Manually curated Italian content from viaggiarebucarest.com

**Content Structure:**
- Organized by page sections using `=== PAGINA: [Section Name] ===` markers
- Each section contains tour descriptions, pricing, contact information, or reviews
- Total size: ~33KB
- Language: Italian
- Topics: Romanian tours, Bucharest, Dracula Castle, Bear Sanctuary, etc.

**Sections Include:**
- Home / Index
- Tour descriptions (Parlamento, Dracula, Bucovina, etc.)
- Pricing information
- Customer reviews (Feedback / Recensioni)
- Contact information (Contatti)

## Data Flow

```
content.txt
    ↓
Chunked by sections (src/indexer.py)
    ↓
75 semantic chunks (500 chars each, 50 char overlap)
    ↓
Embedded locally (sentence-transformers)
    ↓
Stored in indices/faiss_index.index
```

## Updating Content

1. Edit `content.txt` directly
2. Maintain section marker format: `=== PAGINA: [Name] ===`
3. Rebuild index: `python3 scripts/build_index.py`

## Content Characteristics

- **Promotional**: Emphasizes 30+ years experience, Italian-run tours
- **Informational**: Detailed tour programs, durations, pricing
- **Contact-focused**: Multiple phone numbers and email prominently featured
- **Review-rich**: Customer testimonials in Italian
- **SEO keywords**: Tour operator Romania, Dracula Castle, Bucarest, etc.

## Data Quality

✅ Clean, structured text
✅ No HTML or markup
✅ Consistent formatting
✅ Native Italian language
✅ Domain-specific vocabulary
