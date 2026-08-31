#!/usr/bin/env python3
"""Upload all PDFs to Anthropic Files API and save their IDs to files.json."""

import json
import os
import sys
from pathlib import Path
import anthropic

ROOT = Path(__file__).parent.parent

# Load .env.local if present
_env = ROOT / ".env.local"
if _env.exists():
    for line in _env.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

FILES_JSON = ROOT / "files.json"
PDF_DIR = ROOT / "docs"

client = anthropic.Anthropic()


def upload_all():
    registry = {}

    pdfs = sorted(PDF_DIR.glob("*.pdf"))
    if not pdfs:
        print(f"No PDFs found in {PDF_DIR}")
        return

    for pdf in pdfs:
        print(f"Uploading: {pdf.name} ...", end=" ", flush=True)
        with open(pdf, "rb") as f:
            result = client.beta.files.upload(
                file=(pdf.name, f, "application/pdf"),
            )
        registry[pdf.name] = result.id
        print(f"→ {result.id}")

    FILES_JSON.write_text(json.dumps(registry, indent=2))
    print(f"\nSaved {len(registry)} file IDs to {FILES_JSON.name}")


def list_uploaded():
    if not FILES_JSON.exists():
        print("No files.json found — run upload first.")
        return
    registry = json.loads(FILES_JSON.read_text())
    for name, fid in registry.items():
        print(f"  {fid}  {name}")


if __name__ == "__main__":
    if "--list" in sys.argv:
        list_uploaded()
    else:
        upload_all()
