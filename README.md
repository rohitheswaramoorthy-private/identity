# Brand Protection AI 🛡️

An ultra-minimalist, iOS-inspired glassmorphism web platform for detecting brand impersonation, deceptive lookalikes, unauthorized apps, and scam campaigns.

---

## Highlights

- **Ultra-Minimalist iOS Glassmorphism UI**: Built with soft translucent surfaces (`backdrop-filter: blur(28px)`), rounded corners, charcoal typography, and fluid section transitions without visual clutter.
- **Strict 4-Card Landing Experience**: Focuses exclusively on the 4 primary brand identity pillars: **Name**, **Logo**, **Website**, and **Description**.
- **Multi-Provider AI Intelligence**:
  - **OpenAI** (Official API: `gpt-4o-mini`, `gpt-4o`)
  - **Google Gemini** (Official API: `gemini-2.0-flash`, `gemini-1.5-flash`)
  - **Anthropic Claude** (Official API: `claude-3-5-sonnet`, `claude-3-5-haiku`)
  - **Ollama** (100% Local on your Mac via `http://localhost:11434`, zero cloud transfer)
  - **Simulated Demo Engine** (Instant zero-credential evaluation)
- **Separation of Search & AI Reasoning**: Real retrieval engine across Web, Apple App Store, and Social registries separate from the language model.
- **Traceable Provenance**: Every finding contains a status badge (`Verified`, `Possible match`, `Needs review`), source link, date, and defensible confidence metric. Official brand domains are guaranteed verified and never misclassified.
- **Patents & Copyrights Registry**: Integrated intellectual property view for trademarks and patents.
- **Zero-Trust Ephemeral Security**: Provider API keys are held strictly in server memory for the active session. Keys are **never** logged, **never** saved to disk, **never** exposed in frontend JavaScript, and **never** forwarded across providers.

---

## Getting Started (macOS)

### 1. Prerequisites
- Python 3.10+ (macOS native or Homebrew)

### 2. Setup Environment
```bash
cd /Users/rohithes/identity

# Activate the virtual environment
source venv/bin/activate

# Optional: review placeholder environment settings
cp .env.example .env
```

### 3. Start Brand Protection AI
```bash
./venv/bin/uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Open your browser to: **[http://localhost:8000](http://localhost:8000)**

---

## Using Local Ollama
To run completely offline without cloud API keys:
1. Start Ollama on your Mac:
   ```bash
   ollama serve
   ```
2. Pull your preferred model (e.g. `llama3.2`):
   ```bash
   ollama pull llama3.2
   ```
3. Open **Settings** in the top bar of the web app, select **Ollama**, and click **Connect & Test**.

---

## Running the Automated Test Suite
```bash
PYTHONPATH=. ./venv/bin/pytest -v
```
All 10 tests execute in < 0.2s covering provider routing, session security, candidate deduplication, and input validation.
