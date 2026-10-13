# Ollama Local AI Setup

Install Ollama for your operating system, then download and run an AI model locally.

## macOS

**1. Install Ollama**

```bash
brew install --cask ollama
```

Open the Ollama app once after installation.

**2. Start the server (if not already running)**

```bash
ollama serve
```

## Windows

**1. Install Ollama**

In PowerShell:

```powershell
winget install Ollama.Ollama
```

Open Ollama after installation.

**2. Start the server (if not already running)**

```powershell
ollama serve
```

## Linux

**1. Install Ollama**

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**2. Start the server (if not already running)**

```bash
ollama serve
```

> On Linux systems with the Ollama service already running, you can skip this command.

## Download and Run a Model (All Operating Systems)

Open a new terminal or PowerShell window if `ollama serve` is running in the first one.

**3. Download an example model**

```bash
ollama pull llama3.2:1b
```

**4. Run the model locally**

```bash
ollama run llama3.2:1b
```

After the model downloads, you can run it offline.
