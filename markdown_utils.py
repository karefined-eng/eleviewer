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


MATH_GREEK = {
    r"\alpha": "α", r"\beta": "β", r"\gamma": "γ", r"\delta": "δ", r"\epsilon": "ε",
    r"\zeta": "ζ", r"\eta": "η", r"\theta": "θ", r"\iota": "ι", r"\kappa": "κ",
    r"\lambda": "λ", r"\mu": "μ", r"\nu": "ν", r"\xi": "ξ", r"\pi": "π",
    r"\rho": "ρ", r"\sigma": "σ", r"\tau": "τ", r"\upsilon": "υ", r"\phi": "φ",
    r"\chi": "χ", r"\psi": "ψ", r"\omega": "ω",
    r"\Gamma": "Γ", r"\Delta": "Δ", r"\Theta": "Θ", r"\Lambda": "Λ", r"\Xi": "Ξ",
    r"\Pi": "Π", r"\Sigma": "Σ", r"\Phi": "Φ", r"\Psi": "Ψ", r"\Omega": "Ω",
}

MATH_SYMBOLS = {
    r"\infty": "∞", r"\sum": "∑", r"\int": "∫", r"\sqrt": "√", r"\pm": "±",
    r"\mp": "∓", r"\le": "≤", r"\ge": "≥", r"\neq": "≠", r"\approx": "≈",
    r"\equiv": "≡", r"\times": "×", r"\div": "÷", r"\cdot": "·",
    r"\rightarrow": "→", r"\leftarrow": "←", r"\Rightarrow": "⇒", r"\Leftarrow": "⇐",
    r"\partial": "∂", r"\nabla": "∇", r"\in": "∈", r"\forall": "∀", r"\exists": "∃"
}


def convert_latex_expr(expr):
    for k, v in MATH_GREEK.items():
        expr = expr.replace(k, v)
    for k, v in MATH_SYMBOLS.items():
        expr = expr.replace(k, v)
    expr = re.sub(r"\\frac\{([^}]+)\}\{([^}]+)\}", r"(\1 / \2)", expr)
    expr = re.sub(r"\^\{([^}]+)\}", r"<sup>\1</sup>", expr)
    expr = re.sub(r"\^([0-9a-zA-Z+-]+)", r"<sup>\1</sup>", expr)
    expr = re.sub(r"_\{([^}]+)\}", r"<sub>\1</sub>", expr)
    expr = re.sub(r"_([0-9a-zA-Z+-]+)", r"<sub>\1</sub>", expr)
    return expr


def preprocess_markdown(text):
    if not text:
        return ""
    
    # 1. Strikethrough ~~text~~ -> <del>text</del>
    text = re.sub(r"~~([^~]+)~~", r"<del>\1</del>", text)
    
    # 2. Task lists: - [ ] -> ☐, - [x] -> ☑
    text = re.sub(r"^(\s*)[-*+]\s+\[\s*\]\s+(.+)$", r"\1- <span style='color:#8b949e; font-weight:bold;'>☐</span> \2", text, flags=re.MULTILINE)
    text = re.sub(r"^(\s*)[-*+]\s+\[[xX]\]\s+(.+)$", r"\1- <span style='color:#58a6ff; font-weight:bold;'>☑</span> <del style='opacity:0.7;'>\2</del>", text, flags=re.MULTILINE)

    # 3. Block Math $$ ... $$
    def _block_math(match):
        raw = match.group(1).strip()
        conv = convert_latex_expr(raw)
        return f'<div style="text-align:center; margin:12px 0; padding:10px; background:rgba(110,118,129,0.1); border-radius:6px; font-family:\'Cambria Math\',\'Times New Roman\',serif; font-size:1.15em;">{conv}</div>'
    text = re.sub(r"\$\$(.+?)\$\$", _block_math, text, flags=re.DOTALL)

    # 4. Inline Math $ ... $
    def _inline_math(match):
        raw = match.group(1).strip()
        conv = convert_latex_expr(raw)
        return f'<span style="font-family:\'Cambria Math\',\'Times New Roman\',serif; font-style:italic; background:rgba(110,118,129,0.12); padding:1px 5px; border-radius:3px;">{conv}</span>'
    text = re.sub(r"(?<!\$)\$([^\$\n]+?)\$(?!\$)", _inline_math, text)

    return text

