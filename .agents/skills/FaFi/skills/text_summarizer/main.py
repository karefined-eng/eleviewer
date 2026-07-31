"""
Text Summarizer Skill
=====================
Fasst Texte auf eine gewünschte Länge zusammen.
"""

import os
from typing import Dict, Any


def execute(text: str, max_length: int = 150, style: str = "neutral") -> Dict[str, Any]:
    """
    Fasst einen Text zusammen.
    
    Args:
        text: Der zu kürzende Quelltext
        max_length: Maximale Länge in Wörtern
        style: Zusammenfassungsstil (neutral, formal, casual, bullet_points)
        
    Returns:
        Dictionary mit summary, original_length, summary_length
    """
    # Berechne Original-Länge
    words = text.split()
    original_length = len(words)
    
    # Wenn Text bereits kurz genug ist
    if original_length <= max_length:
        return {
            'summary': text,
            'original_length': original_length,
            'summary_length': original_length
        }
    
    # Versuche OpenAI API zu nutzen (falls verfügbar)
    try:
        from openai import OpenAI
        
        client = OpenAI()
        
        style_instructions = {
            'neutral': 'Fasse den Text neutral und sachlich zusammen.',
            'formal': 'Fasse den Text in einem formellen, akademischen Stil zusammen.',
            'casual': 'Fasse den Text in einem lockeren, verständlichen Stil zusammen.',
            'bullet_points': 'Fasse den Text als Aufzählung der wichtigsten Punkte zusammen.'
        }
        
        prompt = f"""
{style_instructions.get(style, style_instructions['neutral'])}

Maximale Länge: {max_length} Wörter.

Text:
{text}

Zusammenfassung:
"""
        
        response = client.responses.create(
            model="gpt-5",
            input=prompt
        )
        
        summary = response.output_text.strip()
        
    except Exception as e:
        # Fallback: Einfache extraktive Zusammenfassung
        summary = _simple_summarize(text, max_length)
    
    summary_length = len(summary.split())
    
    return {
        'summary': summary,
        'original_length': original_length,
        'summary_length': summary_length
    }


def _simple_summarize(text: str, max_length: int) -> str:
    """
    Einfache extraktive Zusammenfassung als Fallback.
    Wählt die wichtigsten Sätze basierend auf Wortfrequenz.
    """
    import re
    from collections import Counter
    
    # Teile in Sätze
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return text[:max_length * 5]  # Grobe Schätzung
    
    # Berechne Wortfrequenzen
    words = re.findall(r'\w+', text.lower())
    word_freq = Counter(words)
    
    # Entferne häufige Stoppwörter
    stopwords = {'der', 'die', 'das', 'ein', 'eine', 'und', 'oder', 'aber', 'ist', 
                 'sind', 'war', 'waren', 'wird', 'werden', 'hat', 'haben', 'the', 
                 'a', 'an', 'and', 'or', 'but', 'is', 'are', 'was', 'were'}
    for sw in stopwords:
        word_freq.pop(sw, None)
    
    # Bewerte Sätze
    sentence_scores = []
    for sentence in sentences:
        sentence_words = re.findall(r'\w+', sentence.lower())
        score = sum(word_freq.get(w, 0) for w in sentence_words)
        sentence_scores.append((sentence, score))
    
    # Sortiere nach Score
    sentence_scores.sort(key=lambda x: x[1], reverse=True)
    
    # Wähle Sätze bis max_length erreicht
    summary_sentences = []
    current_length = 0
    
    for sentence, score in sentence_scores:
        sentence_length = len(sentence.split())
        if current_length + sentence_length <= max_length:
            summary_sentences.append(sentence)
            current_length += sentence_length
        
        if current_length >= max_length * 0.8:
            break
    
    # Sortiere nach ursprünglicher Reihenfolge
    original_order = {s: i for i, s in enumerate(sentences)}
    summary_sentences.sort(key=lambda s: original_order.get(s, 999))
    
    return '. '.join(summary_sentences) + '.'


# Für direkten Aufruf
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        text = sys.argv[1]
        max_len = int(sys.argv[2]) if len(sys.argv) > 2 else 150
        
        result = execute(text, max_len)
        print(f"Original: {result['original_length']} Wörter")
        print(f"Zusammenfassung: {result['summary_length']} Wörter")
        print(f"\n{result['summary']}")
