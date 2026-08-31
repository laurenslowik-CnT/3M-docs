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
cp .env.local.example .env.local   # then add your API key
```

`.env.local`:
```
ANTHROPIC_API_KEY=sk-ant-...
```

## Usage

**1. Upload PDFs to Anthropic (one-time):**
```bash
python3 scripts/upload.py
```

**2. Ask questions:**
```bash
# interactive chat
python3 scripts/ask.py

# single question
python3 scripts/ask.py "What surfaces does VHB Max bond to?"
```

**3. Re-convert PDFs to markdown** (if source PDFs change):
```bash
python3 scripts/convert.py
```

## Scripts

| Script | Purpose |
|---|---|
| `scripts/upload.py` | Uploads all `docs/*.pdf` to Anthropic Files API, saves IDs to `files.json` |
| `scripts/ask.py` | Interactive or single-question chat against uploaded docs |
| `scripts/convert.py` | Converts `docs/*.pdf` → `docs/*.md` using OCR |
