"""Markdown to/from simple plain text for non-technical editing."""

import re


def markdown_to_simple(text):
    """Strip markdown syntax to readable plain text."""
    if not text:
        return ""
    lines = text.splitlines()
    out = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            out.append("")
            continue
        # headings
        stripped = re.sub(r"^#{1,6}\s+", "", stripped)
        # bold/italic
        stripped = re.sub(r"\*\*(.+?)\*\*", r"\1", stripped)
        stripped = re.sub(r"\*(.+?)\*", r"\1", stripped)
        stripped = re.sub(r"__(.+?)__", r"\1", stripped)
        stripped = re.sub(r"_(.+?)_", r"\1", stripped)
        # list markers
        stripped = re.sub(r"^[-*+]\s+", "", stripped)
        stripped = re.sub(r"^\d+\.\s+", "", stripped)
        # links [text](url) -> text
        stripped = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", stripped)
        # inline code
        stripped = re.sub(r"`([^`]+)`", r"\1", stripped)
        out.append(stripped)
    return "\n".join(out).strip()


def simple_to_markdown(text):
    """Convert plain text paragraphs back to minimal markdown."""
    if not text:
        return ""
    paragraphs = re.split(r"\n\s*\n", text.strip())
    return "\n\n".join(p.strip() for p in paragraphs if p.strip())
