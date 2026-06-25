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

**Live demo:** [ai-support-chatbot.mrabrahammacias.workers.dev](https://ai-support-chatbot.mrabrahammacias.workers.dev)
**HF Space:** [huggingface.co/spaces/MrMustSeeUs/ai-support-chatbot](https://huggingface.co/spaces/MrMustSeeUs/ai-support-chatbot)

A production-grade customer support chatbot powered by the Claude API. Answers customer questions 24/7 using a business-provided knowledge base, maintains full conversation history for natural follow-up questions, and falls back gracefully when a question is outside its scope. Deployed globally via Cloudflare Workers with automated CI/CD through GitHub Actions.

---

## Features

- **Always-on** — hosted on Hugging Face Spaces, no cold starts or sleep timeouts
- **Knowledge base driven** — business owners update a plain-text file, no code changes required
- **Conversation memory** — full session history sent on every turn for natural follow-ups
- **Injection-resistant** — input validation layer blocks prompt injection attempts before they reach the API
- **Graceful fallback** — out-of-scope questions return a consistent, professional response
- **Edge-deployed** — Cloudflare Worker proxy serves the app globally with HTTPS enforced by default
- **Automated deployments** — every push to main triggers validate → deploy via GitHub Actions

---

## Tech Stack

| Layer | Technology |
|---|---|
| AI Model | Claude API (`claude-sonnet-4-6`) |
| UI | Gradio 4.44.1 |
| Backend | Python 3.12 |
| Edge Proxy | Cloudflare Workers |
| App Hosting | Hugging Face Spaces |
| CI/CD | GitHub Actions |
| Secrets Management | Cloudflare Environment Variables + HF Repository Secrets |

---

## Architecture

```
User → Cloudflare Workers (HTTPS, global edge, permanent URL)
     → Hugging Face Spaces (Python + Gradio, always-on)
     → Claude API (claude-sonnet-4-6)
     → Response returned through the same chain
```

Conversation history is maintained in-memory per session. On each turn, the full history plus the system prompt (which embeds the knowledge base) is sent to the Claude API, giving it complete context for follow-up questions.

The Cloudflare Worker acts as a reverse proxy — decoupling the public-facing URL from the hosting platform. If the backend ever moves, only one line in `worker.js` changes.

---

## Project Structure

```
ai-support-chatbot/
├── src/
│   ├── __init__.py        # Marks src/ as a Python package
│   ├── security.py        # Input validation and injection detection
│   ├── knowledge_base.py  # Loads and caches the business FAQ at startup
│   ├── chatbot.py         # Claude API engine + conversation history management
│   └── app.py             # Gradio UI + application entry point
├── knowledge_base.txt     # Business FAQ — the only file non-developers need to touch
├── worker.js              # Cloudflare Worker reverse proxy
├── wrangler.toml          # Cloudflare Workers deployment config
├── requirements.txt       # Pinned Python dependencies
├── .env                   # Local secrets — never committed (see .gitignore)
└── .github/workflows/
    └── deploy.yml         # CI/CD: validate → deploy to HF + Cloudflare on push
```

---

## Security

- API key stored in platform secrets — never in code or committed files
- `.env` listed in `.gitignore` — cannot be accidentally committed
- All user input validated and sanitized before reaching the Claude API
- 500-character input cap prevents token abuse and runaway costs
- Regex-based injection detection blocks 9 known prompt injection patterns
- Knowledge base loaded once at startup — no repeated disk reads per request
- `show_error=False` in production — stack traces never exposed to end users
- HTTPS enforced by default on both Cloudflare Workers and Hugging Face Spaces

---

## Local Setup

```bash
# 1. Clone the repo
git clone https://github.com/MrMustSeeUs/ai-support-chatbot.git
cd ai-support-chatbot

# 2. Install dependencies (Python 3.12 required)
pip install -r requirements.txt

# 3. Create your .env file
# Add the following to a new file named .env:
# ANTHROPIC_API_KEY=your-key-from-console.anthropic.com
# BUSINESS_NAME=Your Business Name
# PORT=7860

# 4. Customize the knowledge base
# Edit knowledge_base.txt with your business information — no code changes needed

# 5. Run the app
py -3.12 -m src.app

# Open http://127.0.0.1:7860
```

---

## Customizing the Knowledge Base

Open `knowledge_base.txt` and replace the content with your own business information. The format is plain English — no special syntax required. Suggested sections:

- Business name and description
- Services or products with details
- Pricing structure
- Process or how-to-work-with-us
- Contact information
- Frequently asked questions
- What you don't offer (prevents the bot from speculating)

No code changes needed. Commit and push — GitHub Actions redeploys automatically.

---

## Deployment

### Required GitHub Secrets

Set these under **Settings → Secrets and variables → Actions**:

| Secret | Where to get it |
|---|---|
| `CF_API_TOKEN` | Cloudflare → My Profile → API Tokens → Edit Cloudflare Workers template |
| `CF_ACCOUNT_ID` | Cloudflare dashboard → right sidebar |
| `HF_TOKEN` | huggingface.co → Settings → Access Tokens → Write token |
| `HF_USERNAME` | Your Hugging Face username |

### Set the API key in Hugging Face Spaces

Space → Settings → Repository secrets → add `ANTHROPIC_API_KEY`

### Deploy

```bash
git add .
git commit -m "your message"
git push origin main
# GitHub Actions runs: Validate → Deploy to HF Spaces + Cloudflare Workers
```

---

## CI/CD Pipeline

```
push to main
    │
    ▼
Validate (Python 3.12)
    ├── Install minimal dependencies
    ├── Verify all imports resolve
    └── Run security smoke tests
         │
         ├──────────────────────┐
         ▼                      ▼
Deploy to HF Spaces    Deploy to Cloudflare Workers
(git push to Space)    (wrangler-action)
```

Both deploy jobs run in parallel after Validate passes. If Validate fails, neither deployment runs.

---

*Part of the AI Engineering Portfolio — Project 2 of 6*
*Built by Abraham Macias · [teocallidevs.tech](https://teocallidevs.tech) · [GitHub](https://github.com/MrMustSeeUs)*
