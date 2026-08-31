#!/usr/bin/env python3
"""Ask questions about 3M VHB Tape Max docs.

Provider selection (automatic):
  ANTHROPIC_API_KEY set  →  Anthropic claude-opus-4-8
  No API key             →  Ollama at localhost:11434 (local, no key needed)
                            Default model: llama3.2  (override: OLLAMA_MODEL=mistral)

Doc source:
  default   →  Anthropic Files API  (requires: python3 scripts/upload.py)
  --local   →  reads docs/*.md directly (no upload needed)

Usage:
  python3 scripts/ask.py                           # interactive
  python3 scripts/ask.py --local                   # interactive, local markdown
  python3 scripts/ask.py "What is the flash point?"
  python3 scripts/ask.py --local "What is the flash point?"
"""

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent

# ── Load .env.local ───────────────────────────────────────────────────────────

_env = ROOT / ".env.local"
if _env.exists():
    for line in _env.read_text().splitlines():
        if "=" in line and not line.startswith("#"):
            k, _, v = line.partition("=")
            os.environ.setdefault(k.strip(), v.strip())

# ── Provider detection ────────────────────────────────────────────────────────

FILES_JSON = ROOT / "files.json"
DOCS_DIR = ROOT / "docs"

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "").strip()
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.2")
OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434/v1")

USE_ANTHROPIC = bool(ANTHROPIC_KEY)

SYSTEM = (
    "You are a product expert on 3M VHB Tape Max and related products. "
    "Answer questions using only the provided documents. "
    "If the answer isn't in the documents, say so."
)


def provider_label() -> str:
    if USE_ANTHROPIC:
        return "Anthropic (claude-opus-4-8)"
    return f"Ollama ({OLLAMA_MODEL} @ {OLLAMA_BASE_URL})"


# ── LLM call abstraction ──────────────────────────────────────────────────────

def call_llm(messages: list, system: str | list) -> str:
    """Send messages to whichever provider is active. Returns response text."""
    if USE_ANTHROPIC:
        return _call_anthropic(messages, system)
    return _call_ollama(messages, system)


def _call_anthropic(messages: list, system) -> str:
    import anthropic
    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=2048,
        system=system,
        messages=messages,
    )
    return response.content[0].text


def _call_ollama(messages: list, system) -> str:
    try:
        from openai import OpenAI
    except ImportError:
        print("openai package not installed. Run: pip install openai")
        sys.exit(1)

    # Flatten Anthropic-style system (list of blocks or plain string) to a string
    if isinstance(system, list):
        sys_text = " ".join(b["text"] for b in system if b.get("type") == "text")
    else:
        sys_text = system

    client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")

    openai_messages = [{"role": "system", "content": sys_text}]
    for m in messages:
        content = m["content"]
        # Flatten Anthropic content blocks to plain text for Ollama
        if isinstance(content, list):
            text_parts = []
            for block in content:
                if isinstance(block, dict):
                    if block.get("type") == "text":
                        text_parts.append(block["text"])
                    elif block.get("type") == "document":
                        # File API docs are already in context via system prompt in --local mode
                        pass
                else:
                    text_parts.append(str(block))
            content = "\n".join(text_parts)
        openai_messages.append({"role": m["role"], "content": content})

    try:
        response = client.chat.completions.create(
            model=OLLAMA_MODEL,
            messages=openai_messages,
        )
        return response.choices[0].message.content
    except Exception as e:
        if "connection" in str(e).lower():
            print(
                "\nCould not connect to Ollama. To install and start it:\n"
                "  brew install ollama\n"
                "  ollama serve &\n"
                f"  ollama pull {OLLAMA_MODEL}\n"
            )
            sys.exit(1)
        raise


# ── Local mode (markdown files) ──────────────────────────────────────────────

def load_markdown_context() -> str | list:
    parts = []
    for md in sorted(DOCS_DIR.glob("*.md")):
        parts.append(f"## {md.stem}\n\n{md.read_text()}")
    if not parts:
        print(f"No markdown files found in {DOCS_DIR}. Run: python3 scripts/convert.py")
        sys.exit(1)
    full_text = f"{SYSTEM}\n\n{'---'.join(parts)}"
    if USE_ANTHROPIC:
        # Use prompt caching for repeated queries
        return [{"type": "text", "text": full_text, "cache_control": {"type": "ephemeral"}}]
    return full_text


def ask_local(question: str) -> str:
    system = load_markdown_context()
    return call_llm([{"role": "user", "content": question}], system)


def chat_local():
    system = load_markdown_context()
    doc_count = len(list(DOCS_DIR.glob("*.md")))
    print(f"[{provider_label()}] {doc_count} docs loaded (local mode). Type 'quit' to exit.\n")

    history = []
    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question or question.lower() in ("quit", "exit"):
            break

        history.append({"role": "user", "content": question})
        answer = call_llm(history, system)
        history.append({"role": "assistant", "content": answer})
        print(f"\nClaude: {answer}\n")


# ── Files API mode (Anthropic only) ──────────────────────────────────────────

def load_registry() -> dict[str, str]:
    if not FILES_JSON.exists():
        print("No files.json found. Run: python3 scripts/upload.py  (or use --local)")
        sys.exit(1)
    return json.loads(FILES_JSON.read_text())


def build_files_content(question: str, registry: dict[str, str]) -> list:
    content = [{"type": "text", "text": question}]
    for name, file_id in registry.items():
        content.append({
            "type": "document",
            "source": {"type": "file", "file_id": file_id},
            "title": name.replace(".pdf", ""),
        })
    return content


def ask_files(question: str) -> str:
    import anthropic
    registry = load_registry()
    client = anthropic.Anthropic()
    response = client.beta.messages.create(
        model="claude-opus-4-8",
        max_tokens=2048,
        system=SYSTEM,
        messages=[{"role": "user", "content": build_files_content(question, registry)}],
        betas=["files-api-2025-04-14"],
    )
    return response.content[0].text


def chat_files():
    import anthropic
    registry = load_registry()
    client = anthropic.Anthropic()
    print(f"[{provider_label()}] {len(registry)} docs loaded (Files API). Type 'quit' to exit.\n")

    history = []
    while True:
        try:
            question = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question or question.lower() in ("quit", "exit"):
            break

        user_content = build_files_content(question, registry) if not history else question
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


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    args = sys.argv[1:]
    local = "--local" in args
    question_parts = [a for a in args if a != "--local"]

    # Files API mode requires Anthropic; fall back to --local if using Ollama
    if not local and not USE_ANTHROPIC:
        print(f"No ANTHROPIC_API_KEY found — switching to --local mode with {provider_label()}.\n")
        local = True

    if local:
        if question_parts:
            print(ask_local(" ".join(question_parts)))
        else:
            chat_local()
    else:
        if question_parts:
            print(ask_files(" ".join(question_parts)))
        else:
            chat_files()
