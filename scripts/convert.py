#!/usr/bin/env python3
"""Convert PDFs in docs/ to markdown using pymupdf4llm."""

import os
import re
from pathlib import Path

import pymupdf4llm

ROOT = Path(__file__).parent.parent
PDF_DIR = ROOT / "docs"


def clean_markdown(text):
    text = re.sub(r"<!-- Start of picture text -->.*?<!-- End of picture text -->", "", text, flags=re.DOTALL)
    text = re.sub(r"^\s*\d+/\d+\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*Page\s+\d+\s+of\s+\d+\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


for pdf_path in sorted(PDF_DIR.glob("*.pdf")):
    md_path = pdf_path.with_suffix(".md")
    print(f"Converting: {pdf_path.name} → {md_path.name}")
    try:
        md_text = pymupdf4llm.to_markdown(str(pdf_path))
        md_text = clean_markdown(md_text)
        md_path.write_text(md_text, encoding="utf-8")
        print(f"  Done ({len(md_text)} chars)")
    except Exception as e:
        print(f"  Error: {e}")
