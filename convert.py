#!/usr/bin/env python3
"""Convert PDFs in this directory to markdown using pymupdf4llm."""

import os
import re
import pymupdf4llm

PDF_DIR = os.path.dirname(os.path.abspath(__file__))


def clean_markdown(text):
    # Remove image OCR noise blocks
    text = re.sub(r"<!-- Start of picture text -->.*?<!-- End of picture text -->", "", text, flags=re.DOTALL)
    # Remove standalone page-number/footer lines like "1/2", "Page 1 of 13"
    text = re.sub(r"^\s*\d+/\d+\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"^\s*Page\s+\d+\s+of\s+\d+\s*$", "", text, flags=re.MULTILINE)
    # Collapse runs of 3+ blank lines down to 2
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip() + "\n"


for filename in sorted(os.listdir(PDF_DIR)):
    if not filename.endswith(".pdf"):
        continue
    pdf_path = os.path.join(PDF_DIR, filename)
    md_filename = os.path.splitext(filename)[0] + ".md"
    md_path = os.path.join(PDF_DIR, md_filename)

    print(f"Converting: {filename} → {md_filename}")
    try:
        md_text = pymupdf4llm.to_markdown(pdf_path)
        md_text = clean_markdown(md_text)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(md_text)
        print(f"  Done ({len(md_text)} chars)")
    except Exception as e:
        print(f"  Error: {e}")
