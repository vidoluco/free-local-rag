# Examples Directory

This directory contains example implementations and use cases for the RAG system.

## Available Examples

### tour_operator/
Complete example of a tour operator knowledge base (Italian language).
- Original use case from viaggiarebucarest.com
- Demonstrates Italian language support
- Shows section-based content organization
- Includes reviews, pricing, contact information

## Using Examples

To test with an example:

1. Copy example config:
   ```bash
   # For tour operator example
   cp data/examples/tour_operator/config.yaml config.yaml
   ```

2. Build index with example data:
   ```bash
   python3 scripts/build_index.py --content data/examples/tour_operator/content.txt
   ```

3. Test the chatbot:
   ```bash
   python3 scripts/run_chatbot.py
   ```

## Creating New Examples

To add a new example use case:

1. Create a new directory: `data/examples/your_use_case/`
2. Add your content files
3. Include a README.md explaining the use case
4. Optionally include a custom config.yaml
5. Document any special setup requirements

Examples help demonstrate the system's flexibility across different domains and languages!
