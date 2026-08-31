# 3M VHB Tape Max — Product Docs

Product documentation for 3M VHB Tape Max, with a RAG demo powered by the Anthropic Files API.

## Documents

| File | Description |
|---|---|
| `docs/3m-vhb-tape-max-brochure-4p-enduser-letter-format-en.pdf` | End-user product brochure |
| `docs/Technical Data Sheet.pdf` | Technical specifications |
| `docs/Safety Data Sheet.pdf` | Safety information |
| `docs/Regulatory Data Sheet.pdf` | Regulatory compliance data |

Markdown versions of each PDF live alongside them in `docs/`.

## Setup

```bash
pip install -r requirements.txt
cp .env.local.example .env.local
```

### Option A — Anthropic (full quality)

Add your API key to `.env.local`:
```
ANTHROPIC_API_KEY=sk-ant-...
```

Then upload PDFs once:
```bash
python3 scripts/upload.py
python3 scripts/ask.py
```

### Option B — Ollama (local, no API key needed)

```bash
brew install ollama
ollama serve &
ollama pull llama3.2
python3 scripts/ask.py --local   # auto-detects no API key, uses Ollama
```

The script auto-selects the provider: Anthropic if `ANTHROPIC_API_KEY` is set, Ollama otherwise.

## Usage

```bash
# Interactive chat
python3 scripts/ask.py

# Single question
python3 scripts/ask.py "What surfaces does VHB Max bond to?"

# Force local markdown mode (skips Files API)
python3 scripts/ask.py --local
python3 scripts/ask.py --local "What is the flash point?"

# Use a different Ollama model
OLLAMA_MODEL=mistral python3 scripts/ask.py --local
```

**Re-convert PDFs to markdown** (if source PDFs change):
```bash
python3 scripts/convert.py
```

## Scripts

| Script | Purpose |
|---|---|
| `scripts/upload.py` | Uploads all `docs/*.pdf` to Anthropic Files API, saves IDs to `files.json` |
| `scripts/ask.py` | Interactive or single-question chat against uploaded docs |
| `scripts/convert.py` | Converts `docs/*.pdf` → `docs/*.md` using OCR |
