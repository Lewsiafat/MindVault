# Gemini API Quick Reference

MindVault uses Google Gemini 2.0 Flash for all AI features. This is a quick reference for setup and usage.

## Getting an API Key

1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Sign in with a Google account
3. Click **Get API Key** → **Create API Key**
4. Copy the key and add it to your `.env` file:
   ```
   GEMINI_API_KEY=AIza...
   ```

## Free Tier Limits (as of 2025)

| Model | Requests/min | Requests/day | Tokens/min |
|-------|-------------|-------------|-----------|
| Gemini 2.0 Flash | 15 | 1,500 | 1,000,000 |
| Gemini 1.5 Pro | 2 | 50 | 32,000 |

For personal use with MindVault, the free tier is sufficient for most workflows.

## How MindVault Uses Gemini

MindVault uses the `google-genai` Python SDK:

```python
from google import genai as genai_sdk
client = genai_sdk.Client(api_key=GEMINI_API_KEY)
response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=prompt
)
```

### AI Calls Made by MindVault

| Feature | When Called | Cached? |
|---------|-------------|---------|
| Overview summary | On demand | 1h in-memory |
| Smart categories | On demand | File cache (persistent) |
| Document summary | Per document, on demand | 1h in-memory |
| Wiki ingestion | On demand per doc | Written to disk |
| Wiki synthesis | On demand | Written to disk |
| Lint check | On demand | No |
| Lint fix | On demand | No |

### Cost Estimate

For a knowledge base of ~50 documents:
- Initial categorization: ~10,000 tokens (~$0.001)
- Wiki ingestion (50 docs): ~100,000 tokens total (~$0.01)
- Daily usage (summaries, search): ~5,000 tokens/day (~$0.0005/day)

**Effective monthly cost: < $0.05** for typical personal use.

## Important Notes

- MindVault uses `gemini-2.0-flash` — do NOT use `gemini-2.0-flash-lite` (deprecated)
- Gemini sometimes returns JSON wrapped in markdown fences — MindVault handles this automatically
- If you hit rate limits, add a small delay between Wiki ingestion calls
