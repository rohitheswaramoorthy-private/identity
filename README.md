# IdentityAI



---


- **Finalized Brand Identity**: Streamlined biometric squircle logo replacing generic shield symbols.
- **Strict 4-Card Landing Experience**: Focuses exclusively on the 4 primary brand identity pillars: **Name**, **Logo**, **Website**, and **Description**.
- **Multi-Provider AI Intelligence (No Demo Mode)**:
  - **Ollama** (100% Local on your Mac/PC via `http://localhost:11434`, zero cloud transfer)
  - **OpenAI** (Official API: `gpt-4o-mini`, `gpt-4o`, `o3-mini`, etc.)
  - **Google Gemini** (Official API: `gemini-2.0-flash`, `gemini-1.5-flash`, etc.)
  - **Anthropic Claude** (Official API: `claude-3-5-sonnet`, `claude-3-5-haiku`, etc.)
- **Custom AI Model Support**:
  - Enter any custom model identifier (e.g. `llama3.3`, `deepseek-r1`, `mistral-large`, `qwen2.5-coder`).
  - Supported directly across all provider adapters.
- **Localhost Scanning with User Consent**:
  - Requires explicit user permission before probing `localhost:11434` for a local Ollama server.
  - Automatically discovers installed models and provides a one-click connection option.
- **Custom Source Monitoring**:
  - Add custom monitoring channels, internal IP registries, or community links dynamically.
  - Toggle channels on or off with instant state persistence.
- **Separation of Search & AI Reasoning**: Real retrieval engine across Web, Apple App Store, Social, and Custom registries separate from the language model.
- **Traceable Provenance**: Every finding contains a status badge (`Verified`, `Possible match`, `Needs review`), source link, date, and defensible confidence metric. Official brand domains are guaranteed verified.
- **Patents & Copyrights Registry**: Integrated intellectual property view for trademarks and patents.
- **Zero-Trust Ephemeral Security**: Provider API keys are held strictly in server memory for the active session. Keys are **never** logged, **never** saved to disk, and **never** exposed in frontend JavaScript.

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

### 3. Start IdentityAI
```bash
./venv/bin/uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
```

Open your browser to: **[http://localhost:8000](http://localhost:8000)**

---

## Using Local Ollama
To run completely offline without cloud API keys:
1. Start Ollama on your machine:
   ```bash
   ollama serve
   ```
2. Open **Settings** in the IdentityAI top bar.
3. Click **"Allow & Scan Localhost"** to grant permission to detect your local Ollama server and installed models.
4. Click **"Connect to Local Ollama"** or type in your desired model name.

---

## Running the Automated Test Suite
```bash
PYTHONPATH=. ./venv/bin/pytest -v
```
All 11 tests execute in ~0.2s covering provider routing, localhost permission checks, custom sources, and session security.
