---
title: AI Support Chatbot
emoji: 💬
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 4.44.1
app_file: src/app.py
pinned: false
python_version: "3.12"
---

# 24/7 AI Support Chatbot

A customer support chatbot powered by Claude that answers questions around the clock using a business-provided knowledge base. Maintains full conversation history so follow-up questions work naturally. Falls back gracefully when a question is outside the knowledge base.

**Live demo:** [ai-support-chatbot.[account].workers.dev](https://ai-support-chatbot.[account].workers.dev)

---

## What It Does

- Answers customer questions 24/7 with no human staffing required
- Loads a plain-text knowledge base (FAQ, policies, pricing) at startup
- Maintains conversation history across the full session
- Refuses to answer questions outside the knowledge base — no hallucination
- Blocks prompt injection attempts before they reach the API
- Business owners update the knowledge base by editing one text file — no code changes

---

## Tech Stack

| Layer | Technology |
|---|---|
| AI | Claude API (`claude-sonnet-4-6`) |
| UI | Gradio |
| Backend | Python 3.11 |
| Edge proxy | Cloudflare Workers |
| App hosting | Hugging Face Spaces |
| CI/CD | GitHub Actions |
| Secrets | Cloudflare environment variables / HF Secrets |

---

## Project Structure

```
ai-support-chatbot/
├── src/
│   ├── security.py        # Input validation and injection detection
│   ├── knowledge_base.py  # Loads and caches the business FAQ
│   ├── chatbot.py         # Claude API engine + conversation history
│   └── app.py             # Gradio UI + entry point
├── knowledge_base.txt     # Business FAQ — edit this to customize the bot
├── worker.js              # Cloudflare Worker proxy
├── wrangler.toml          # Cloudflare deployment config
├── requirements.txt       # Python dependencies
└── .github/workflows/
    └── deploy.yml         # CI/CD pipeline
```

---

## Local Setup

```bash
# 1. Clone the repo
git clone https://github.com/MrMustSeeUs/ai-support-chatbot.git
cd ai-support-chatbot

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add your API key to .env
cp .env .env.local
# Edit .env and replace "your-api-key-here" with your key from:
# https://console.anthropic.com/

# 5. Customize the knowledge base
# Edit knowledge_base.txt with your business information

# 6. Run the app
python src/app.py

# Visit http://localhost:7860
```

---

## Customizing the Knowledge Base

Open `knowledge_base.txt` and replace the sample content with your own:

- Business name and description
- Products and pricing
- Shipping and return policies
- Contact information
- Frequently asked questions

No code changes needed. Restart the app after editing.

---

## Deployment

### Required GitHub Secrets

Set these in your repo under **Settings → Secrets → Actions**:

| Secret | Where to get it |
|---|---|
| `CF_API_TOKEN` | Cloudflare dashboard → My Profile → API Tokens |
| `CF_ACCOUNT_ID` | Cloudflare dashboard → right sidebar |
| `HF_TOKEN` | huggingface.co → Settings → Access Tokens |
| `HF_USERNAME` | Your Hugging Face username |

### Deploy

```bash
git add .
git commit -m "your message"
git push origin main
# GitHub Actions handles the rest automatically
```

### Set the Anthropic API key in Hugging Face Spaces

In your Space → Settings → Repository secrets → add `ANTHROPIC_API_KEY`

---

## Security

- API key stored in platform secrets — never in code or config files
- `.env` is in `.gitignore` — never committed
- All input validated before reaching the Claude API
- 500-character input cap prevents token abuse
- Prompt injection detection blocks 8+ known attack patterns
- Knowledge base loaded once at startup — not re-read per request
- HTTPS enforced by default on both Cloudflare Workers and HF Spaces

---

## Architecture

```
User → Cloudflare Workers (proxy, HTTPS, global edge)
     → Hugging Face Spaces (Python + Gradio, always-on)
     → Claude API (claude-sonnet-4-6)
     → Response returned through the same chain
```

Conversation history is maintained in-memory per session. On each turn, the full history plus the system prompt (which includes the knowledge base) is sent to the Claude API, giving it complete context for follow-up questions.

---

*Part of the AI Engineering Portfolio — Project 2 of 6*
*Built by Abraham Macias*
