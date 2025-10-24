# Customization Guide

Guide for configuring the RAG system for new client deployments.

## Client Onboarding Checklist

- [ ] Clone/copy template to new directory
- [ ] Run `./setup.sh` to initialize environment
- [ ] Configure `config.yaml` with client details
- [ ] Set up `.env` with API credentials
- [ ] Collect and organize client documents
- [ ] Build initial index
- [ ] Test with sample queries
- [ ] Deploy (local or cloud)

## Configuration File (config.yaml)

The `config.yaml` file is the central customization point. All client-specific settings go here.

### Company Information

```yaml
company:
  name: "Acme Corporation"
  description: "Leading provider of innovative solutions"
  website: "https://acme.com"
  contact:
    email: "support@acme.com"
    phone: "+1-800-555-0123"
    additional_phone: "+1-800-555-0124"
```

### Language Settings

```yaml
language:
  primary: "en"  # en, it, es, fr, de, pt, nl, etc.
  assistant_name: "Acme Assistant"
```

**Supported Languages:**
- English (en) - Default
- Italian (it) - Fully tested
- Spanish (es), French (fr), German (de) - Supported by embedding model
- Others supported by sentence-transformers multilingual models

### System Prompt Customization

This controls the chatbot's behavior and personality:

```yaml
system_prompt:
  role: "professional assistant"  # Options: professional, friendly, technical, sales, support
  instructions: |
    You are an AI assistant for {company_name}.

    Your role:
    - Provide helpful information based on the company's knowledge base
    - Answer questions clearly and accurately
    - Be {role} and courteous
    - Use ONLY information from the provided context
    - If information is not in the context, say so clearly

    Important rules:
    - Only answer based on the provided context
    - Do not make up information
    - Always respond in {language}
    - Cite sources when providing answers
```

**Template Variables:**
- `{company_name}` - Replaced with company.name
- `{language}` - Replaced with language.primary
- `{role}` - Replaced with system_prompt.role

**Role Examples:**

**Professional Assistant:**
```
- Be professional and courteous
- Focus on accuracy and clarity
- Maintain formal tone
```

**Sales Assistant:**
```
- Be enthusiastic about products/services
- Highlight benefits and value propositions
- Guide users toward conversion
- Use persuasive but honest language
```

**Technical Support:**
```
- Focus on troubleshooting and solutions
- Provide step-by-step instructions
- Ask clarifying questions when needed
- Use technical terminology appropriately
```

### RAG Parameters

Fine-tune retrieval and generation:

```yaml
rag:
  chunk_size: 500  # Characters per chunk (300-800 recommended)
  chunk_overlap: 50  # Overlap between chunks (10-20% of chunk_size)
  top_k: 3  # Number of chunks to retrieve (3-5 recommended)
  batch_size: 32  # Embedding batch size (leave at 32)
```

**Tuning Guide:**

| Document Type | chunk_size | top_k | Notes |
|--------------|------------|-------|-------|
| Short FAQs | 300 | 5 | Small chunks, more results |
| Technical docs | 700 | 3 | Larger context per chunk |
| Product catalogs | 500 | 4 | Balanced approach |
| Legal documents | 800 | 3 | Preserve context |

### LLM Configuration

```yaml
llm:
  provider: "deepseek"
  model: "deepseek-chat"
  temperature: 0.3  # 0.0-1.0 (lower = more focused)
  max_tokens: 500  # Response length limit
  api_base: "https://api.deepseek.com/v1"
```

**Temperature Guide:**
- `0.0-0.2`: Factual, deterministic (legal, medical)
- `0.3-0.5`: Balanced (most use cases)
- `0.6-0.8`: Creative, varied (marketing, content)

### Web UI Customization

```yaml
ui:
  title: "Acme Knowledge Base"
  page_icon: "🚀"  # Any emoji or URL to favicon
  theme: "light"  # light or dark
  show_sources: true  # Show document sources
  show_retrieval_scores: false  # Debug mode
  welcome_message: |
    Welcome to {company_name} Knowledge Base!

    Ask me anything about our products, services, or company information.
```

### Data Sources

```yaml
data:
  input_folder: "data/client_content"
  supported_formats:
    - "txt"
    - "pdf"
    - "docx"
    - "md"
  web_scraping:
    enabled: false  # Set to true to enable
    urls:
      - "https://example.com/faq"
      - "https://example.com/about"
    selector: "article.main-content"  # Optional CSS selector
```

## Environment Variables (.env)

```bash
# DeepSeek API Configuration
DEEPSEEK_API_KEY=sk-your-api-key-here
DEEPSEEK_API_BASE=https://api.deepseek.com/v1  # Optional override
```

**Security Notes:**
- Never commit `.env` to git
- Use different API keys per deployment
- Consider API usage limits and costs

## Advanced Customization

### Custom Embedding Model

To use a different embedding model:

1. Update `config.yaml`:
```yaml
embedding:
  model: "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
  dimension: 768  # Must match model's output dimension
```

2. Rebuild index:
```bash
python3 scripts/build_index.py
```

**Popular Models:**
- `paraphrase-multilingual-MiniLM-L12-v2`: Fast, good quality (384 dim) [DEFAULT]
- `paraphrase-multilingual-mpnet-base-v2`: Higher quality, slower (768 dim)
- `all-MiniLM-L6-v2`: English only, very fast (384 dim)

### Web Scraping Setup

To automatically scrape content from client website:

1. Enable in `config.yaml`:
```yaml
data:
  web_scraping:
    enabled: true
    urls:
      - "https://client.com/about"
      - "https://client.com/products"
      - "https://client.com/faq"
    selector: "main"  # Optional: CSS selector for content area
```

2. Run scraper:
```bash
python3 scripts/ingest_documents.py --scrape-web
```

3. Build index:
```bash
python3 scripts/build_index.py
```

### Multi-Language Support

For multilingual deployments:

1. Use multilingual embedding model (default is multilingual)
2. Set primary language in config.yaml
3. Adjust system prompt for target language
4. Organize documents by language in subdirectories

Example for Italian:
```yaml
language:
  primary: "it"
  assistant_name: "Assistente Virtuale"

system_prompt:
  instructions: |
    Sei l'assistente virtuale di {company_name}.

    Il tuo ruolo:
    - Fornire informazioni utili basate sulla knowledge base aziendale
    - Rispondere alle domande in modo chiaro e preciso
    - Essere professionale e cortese
    - Utilizzare SOLO le informazioni fornite nel contesto
```

## Deployment Scenarios

### Local Development
```bash
source venv/bin/activate
streamlit run app.py
```
Access at: http://localhost:8501

### Internal Server
```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```
Access at: http://server-ip:8501

### Cloud Deployment

**Docker** (coming soon):
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
CMD ["streamlit", "run", "app.py", "--server.address", "0.0.0.0"]
```

**Environment Variables for Production:**
- Set `deployment.debug: false` in config.yaml
- Use environment variables for sensitive data
- Configure proper firewall rules
- Set up HTTPS/SSL

## Testing & Quality Assurance

### Test Query Examples

Create `test_queries.txt` with domain-specific questions:

```
What are your business hours?
How can I contact support?
What products do you offer?
What is your return policy?
```

Test retrieval:
```bash
python3 scripts/test_retrieval.py
```

### Quality Checklist

- [ ] All client documents indexed successfully
- [ ] Test queries return accurate answers
- [ ] Sources are cited correctly
- [ ] Response tone matches brand
- [ ] Contact information is accurate
- [ ] Web interface loads without errors
- [ ] API key is configured correctly

## Client Handoff

Before handing off to client:

1. **Documentation**
   - Provide CLIENT_GUIDE.md
   - Create custom FAQ if needed
   - Document any special configurations

2. **Training**
   - Show how to add documents
   - Demonstrate rebuilding index
   - Explain how to test queries

3. **Access**
   - Provide login credentials (if applicable)
   - Share API key securely
   - Document access URLs

4. **Maintenance**
   - Schedule periodic content updates
   - Monitor API usage and costs
   - Plan for scaling if needed

## Troubleshooting

### Poor Answer Quality
1. Check document quality (readable, not scanned)
2. Increase `top_k` to retrieve more context
3. Adjust `chunk_size` for your content type
4. Review system prompt for clarity

### Slow Performance
1. Reduce `chunk_size` to create fewer chunks
2. Use faster embedding model
3. Consider caching strategies
4. Reduce `max_tokens` in LLM config

### Wrong Language Responses
1. Verify `language.primary` setting
2. Update system prompt with language-specific instructions
3. Check that documents are in expected language

## Support & Resources

- **GitHub Issues**: Report bugs or request features
- **Documentation**: Check README.md for technical details
- **Examples**: See `data/examples/` for reference implementations
- **Community**: [Add your support channel]

---

**Ready to deploy?** Follow the Client Onboarding Checklist at the top of this document.
