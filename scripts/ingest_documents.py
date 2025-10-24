#!/usr/bin/env python3
"""
Document Ingestion CLI

Batch process documents from various formats and prepare for RAG indexing.
Supports: TXT, PDF, DOCX, Markdown, web scraping.

Usage:
    python3 scripts/ingest_documents.py --source data/client_content
    python3 scripts/ingest_documents.py --scrape-web
    python3 scripts/ingest_documents.py --source examples/tour_operator
"""

import sys
import argparse
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.loaders import DocumentLoader, WebScraper, ContentAggregator
from src.config import Config


def ingest_from_directory(source_dir: str, output_file: str = None):
    """
    Ingest all documents from a directory.

    Args:
        source_dir: Directory containing documents
        output_file: Optional output path for aggregated content
    """
    print("=" * 70)
    print("DOCUMENT INGESTION - Directory Mode")
    print("=" * 70)

    source_path = Path(source_dir)

    if not source_path.exists():
        print(f"\n❌ Error: Directory not found: {source_dir}")
        print(f"Please create it and add your documents.")
        sys.exit(1)

    print(f"\nSource directory: {source_path}")
    print("\nSupported formats: TXT, PDF, DOCX, Markdown")
    print("\nLoading documents...\n")

    # Load all documents
    documents = DocumentLoader.load_directory(source_path)

    if not documents:
        print("\n⚠️  No supported documents found in directory.")
        print("Please add .txt, .pdf, .docx, or .md files.")
        sys.exit(0)

    print(f"\n✅ Loaded {len(documents)} documents")

    # Show summary
    print("\nDocument Summary:")
    for doc in documents:
        content_len = len(doc['content'])
        print(f"  - {doc['filename']} ({doc['format']}): {content_len:,} characters")

    # Aggregate content
    print("\nAggregating content...")
    aggregated = ContentAggregator.aggregate_documents(documents)

    # Determine output path
    if not output_file:
        output_file = str(Config.DATA_DIR / "aggregated_content.txt")

    # Save
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(aggregated)

    print(f"\n✅ Aggregated content saved: {output_path}")
    print(f"   Total characters: {len(aggregated):,}")
    print("\n" + "=" * 70)
    print("Next step: Build index")
    print("Run: python3 scripts/build_index.py")
    print("=" * 70)


def ingest_from_web():
    """Scrape content from URLs specified in config.yaml."""
    print("=" * 70)
    print("DOCUMENT INGESTION - Web Scraping Mode")
    print("=" * 70)

    config = Config.load_config()
    web_config = config.get('data', {}).get('web_scraping', {})

    if not web_config.get('enabled', False):
        print("\n⚠️  Web scraping is disabled in config.yaml")
        print("To enable, set data.web_scraping.enabled: true")
        sys.exit(0)

    urls = web_config.get('urls', [])

    if not urls:
        print("\n⚠️  No URLs specified in config.yaml")
        print("Add URLs to data.web_scraping.urls list")
        sys.exit(0)

    print(f"\nFound {len(urls)} URLs to scrape:\n")
    for url in urls:
        print(f"  - {url}")

    print("\nStarting web scraping...\n")

    # Scrape URLs
    documents = WebScraper.scrape_from_config(config)

    if not documents:
        print("\n❌ No content scraped successfully")
        sys.exit(1)

    print(f"\n✅ Scraped {len(documents)} pages")

    # Show summary
    print("\nScraped Content Summary:")
    for doc in documents:
        content_len = len(doc['content'])
        print(f"  - {doc['title']}: {content_len:,} characters")

    # Save aggregated content
    output_file = str(Config.DATA_DIR / "scraped_content.txt")
    ContentAggregator.save_aggregated_content(documents, output_file)

    print("\n" + "=" * 70)
    print("Next step: Build index")
    print("Run: python3 scripts/build_index.py")
    print("=" * 70)


def ingest_single_file(file_path: str, output_file: str = None):
    """
    Ingest a single document file.

    Args:
        file_path: Path to document file
        output_file: Optional output path
    """
    print("=" * 70)
    print("DOCUMENT INGESTION - Single File Mode")
    print("=" * 70)

    print(f"\nLoading file: {file_path}")

    try:
        doc = DocumentLoader.load_document(file_path)
        print(f"✓ Loaded: {doc['filename']} ({doc['format']})")
        print(f"  Content length: {len(doc['content']):,} characters")

        # Save
        if not output_file:
            output_file = str(Config.DATA_DIR / f"processed_{doc['filename']}.txt")

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(doc['content'])

        print(f"\n✅ Saved to: {output_path}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Ingest documents for RAG system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Ingest all docs from client_content directory
  python3 scripts/ingest_documents.py --source data/client_content

  # Scrape web pages from config.yaml
  python3 scripts/ingest_documents.py --scrape-web

  # Process single file
  python3 scripts/ingest_documents.py --file document.pdf --output data/content.txt
        """
    )

    parser.add_argument(
        '--source', '-s',
        help='Directory containing documents to ingest'
    )

    parser.add_argument(
        '--file', '-f',
        help='Single file to ingest'
    )

    parser.add_argument(
        '--output', '-o',
        help='Output file path for aggregated content'
    )

    parser.add_argument(
        '--scrape-web', '-w',
        action='store_true',
        help='Scrape web pages from config.yaml'
    )

    args = parser.parse_args()

    # Ensure directories exist
    Config.ensure_dirs()

    # Route to appropriate function
    if args.scrape_web:
        ingest_from_web()
    elif args.file:
        ingest_single_file(args.file, args.output)
    elif args.source:
        ingest_from_directory(args.source, args.output)
    else:
        # Default: use client_content directory
        default_source = Config.CLIENT_CONTENT_DIR
        print(f"No source specified. Using default: {default_source}")
        print("(Use --help for more options)\n")
        ingest_from_directory(str(default_source), args.output)


if __name__ == "__main__":
    main()
