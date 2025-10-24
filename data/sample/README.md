# Sample Data Directory

This directory contains sample/demo data for testing the RAG system.

## Purpose

Use this folder to:
- Test the system before adding real client data
- Demonstrate capabilities to clients
- Verify configuration changes
- Debug retrieval quality

## Quick Start

1. Add some sample documents here (any supported format: txt, pdf, docx, md)
2. Update `config.yaml` to point to this directory:
   ```yaml
   data:
     input_folder: "data/sample"
   ```
3. Build the index:
   ```bash
   python3 scripts/build_index.py
   ```
4. Test queries:
   ```bash
   python3 scripts/run_chatbot.py
   ```

## Example Sample Data

Create a file `data/sample/demo_content.txt`:

```
=== DOCUMENT: Company Overview ===

We are a leading provider of innovative solutions in our industry.
Founded in 2020, we serve clients worldwide with dedication to excellence.

Contact us:
Email: demo@example.com
Phone: +1-555-0123

=== DOCUMENT: Services ===

Our Services:
- Consulting: Expert advice tailored to your needs
- Implementation: Full-service deployment and integration
- Support: 24/7 customer support with dedicated teams

Pricing: Contact us for a custom quote based on your requirements.

=== DOCUMENT: FAQ ===

Q: What are your business hours?
A: We operate Monday-Friday, 9 AM - 6 PM EST.

Q: Do you offer international services?
A: Yes, we serve clients globally with localized support.
```

Then build and test!
