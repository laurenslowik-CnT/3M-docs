#!/usr/bin/env python3
"""Ask questions about 3M VHB Tape Max docs via Anthropic Files API."""

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

SYSTEM = (
    "You are a product expert on 3M VHB Tape Max and related products. "
    "Answer questions using only the provided documents. "
    "If the answer isn't in the documents, say so."
)

client = anthropic.Anthropic()


def load_registry() -> dict[str, str]:
    if not FILES_JSON.exists():
        print("No files.json found. Run: python3 scripts/upload.py")
        sys.exit(1)
    return json.loads(FILES_JSON.read_text())


def build_content(question: str, registry: dict[str, str]) -> list:
    content = [{"type": "text", "text": question}]
    for name, file_id in registry.items():
        content.append({
            "type": "document",
            "source": {"type": "file", "file_id": file_id},
            "title": name.replace(".pdf", ""),
        })
    return content


def ask(question: str) -> str:
    registry = load_registry()
    response = client.beta.messages.create(
        model="claude-opus-4-8",
        max_tokens=2048,
        system=SYSTEM,
        messages=[{
            "role": "user",
            "content": build_content(question, registry),
        }],
        betas=["files-api-2025-04-14"],
    )
    return response.content[0].text


def chat():
    registry = load_registry()
    print(f"Loaded {len(registry)} documents. Type 'quit' to exit.\n")

    history = []

    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not question or question.lower() in ("quit", "exit"):
            break

        # Attach docs only on the first turn; subsequent turns are plain chat
        if not history:
            user_content = build_content(question, registry)
        else:
            user_content = question

        history.append({"role": "user", "content": user_content})

        response = client.beta.messages.create(
            model="claude-opus-4-8",
            max_tokens=2048,
            system=SYSTEM,
            messages=history,
            betas=["files-api-2025-04-14"],
        )

        answer = response.content[0].text
        history.append({"role": "assistant", "content": answer})
        print(f"\nClaude: {answer}\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Single question mode: python3 scripts/ask.py "What is the flash point?"
        print(ask(" ".join(sys.argv[1:])))
    else:
        # Interactive chat mode
        chat()
