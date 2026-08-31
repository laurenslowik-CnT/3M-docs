#!/usr/bin/env python3
"""Upload all PDFs to Anthropic Files API and save their IDs to files.json."""

import json
import os
from pathlib import Path
import anthropic

FILES_JSON = Path(__file__).parent / "files.json"
PDF_DIR = Path(__file__).parent

client = anthropic.Anthropic()


def upload_all():
    registry = {}

    pdfs = sorted(PDF_DIR.glob("*.pdf"))
    if not pdfs:
        print("No PDFs found.")
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
    import sys
    if "--list" in sys.argv:
        list_uploaded()
    else:
        upload_all()
