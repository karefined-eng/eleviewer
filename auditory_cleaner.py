import re

def clean_for_speech(text: str) -> str:
    """
    Cleans text of auditory clutter before sending it to the TTS engine.
    Strips Markdown formatting, URLs, and common PDF headers/footers.
    """
    if not text:
        return ""
        
    # 1. Markdown Links [text](url) -> text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
    
    # 2. Remove bare URLs entirely
    text = re.sub(r'https?://[^\s)\]]+|www\.[^\s)\]]+', '', text)
    
    # 3. Task list markers "- [ ]" or "- [x]"
    text = re.sub(r'^[-*+]\s+\[[ xX]\]\s+', '', text, flags=re.MULTILINE)
    
    # 4. List markers and Headings
    text = re.sub(r'^[-*+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)
    
    # 5. Bold, italic, code block markers
    text = re.sub(r'[*_`]', '', text)
    
    # 6. PDF Clutter: Standalone page numbers (e.g., just digits on a line)
    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
    
    # 7. PDF Clutter: "Page X" or "Page X of Y" on its own line
    text = re.sub(r'^\s*Page\s+\d+(\s+of\s+\d+)?\s*$', '', text, flags=re.IGNORECASE | re.MULTILINE)
    
    # 8. LaTeX / Math basic expansion (\alpha -> alpha)
    # This prevents the TTS from reading "backslash alpha"
    text = re.sub(r'\\([a-zA-Z]+)', r'\1', text)
    
    # Cleanup extra multiple newlines or spaces created by deletions
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()
