# Paco Verb Colorizer - AI-Enhanced with Morphological Analysis
# Usage: python paco_colorizer.py < input.txt > output.html
# Or import colorize_text(text) to get HTML with colored verb endings.

import re, html, sys
from typing import Optional
import spacy

# Load Spanish model (small, fast model)
try:
    nlp = spacy.load("es_core_news_sm")
except OSError:
    print("Downloading Spanish model...", file=sys.stderr)
    import subprocess
    subprocess.run([sys.executable, "-m", "spacy", "download", "es_core_news_sm"])
    nlp = spacy.load("es_core_news_sm")

COLORS = {
    "1": "red",      # yo / nosotros
    "2": "blue",     # tú / vosotros
    "3": "yellow",   # él/ella/Ud. / ellos/ellas/Uds.
    "shared": "orange",  # ambiguous
}

PERSON_COLORS = {
    ("1", "Sing"): "red",      # yo
    ("2", "Sing"): "blue",     # tú
    ("3", "Sing"): "yellow",   # él/ella/Ud.
    ("1", "Plur"): "purple",   # nosotros
    ("2", "Plur"): "blue",     # vosotros (keeping blue)
    ("3", "Plur"): "green",    # ellos/ellas/Uds.
}

ESTAR = ["estoy","estas","estás","esta","está","estamos","estáis","estan","están"]
IR = ["voy","vas","va","vamos","vais","van"]
HABER = ["he","has","ha","hemos","habéis","han"]

def get_person_color(person: Optional[str], number: Optional[str]) -> str:
    """Get color based on grammatical person and number from spaCy."""
    if not person or not number:
        return COLORS["shared"]
    
    key = (person, number)
    return PERSON_COLORS.get(key, COLORS["shared"])

def should_color_verb(token) -> bool:
    """
    Use spaCy's morphological analysis to determine if this is a finite verb.
    Returns True only for conjugated verbs that show person marking.
    """
    # Must be a verb or auxiliary
    if token.pos_ not in ("VERB", "AUX"):
        return False
    
    # Get verb form from morphology
    verb_form = token.morph.get("VerbForm")
    
    # Only color finite verbs (conjugated forms)
    # Skip: Inf (infinitives), Ger (gerunds), Part (participles)
    if not verb_form or verb_form[0] != "Fin":
        return False
    
    return True

def get_ending_to_color(word: str, person: Optional[str], number: Optional[str]) -> tuple:
    """
    Determine which part of the word to color based on person/number.
    Returns (start_index, color)
    """
    low = word.lower()
    
    # Special handling for haber (color whole auxiliary)
    if low in HABER:
        return (0, get_person_color(person, number))
    
    # Special handling for estar
    if low in ESTAR:
        if low == "estoy":
            idx = low.rfind("oy")
            return (idx, COLORS["1"])
        if low.endswith(("ás", "á", "amos", "áis", "án")):
            # Color the accent + ending
            for ending in ["ás", "á", "amos", "áis", "án"]:
                if low.endswith(ending):
                    return (len(low) - len(ending), get_person_color(person, number))
    
    # Special handling for ir
    if low in IR:
        if low == "voy":
            idx = low.rfind("oy")
            return (idx, COLORS["1"])
        if low.endswith(("as", "a", "amos", "áis", "an")):
            for ending in ["amos", "áis", "as", "an", "a"]:
                if low.endswith(ending):
                    return (len(low) - len(ending), get_person_color(person, number))
    
    # Future/Conditional - color the ending after infinitive
    future_cond = ["é", "ás", "á", "emos", "éis", "án", "ía", "ías", "íamos", "íais", "ían"]
    for ending in sorted(future_cond, key=len, reverse=True):
        if low.endswith(ending):
            return (len(low) - len(ending), get_person_color(person, number))
    
    # Imperfect endings
    imperfect = ["ábamos", "ábais", "aban", "abas", "aba", "íamos", "íais", "ían", "ías", "ía"]
    for ending in sorted(imperfect, key=len, reverse=True):
        if low.endswith(ending):
            # -aba and -ía without clear person markers are "shared"
            if ending in ["aba", "ía"] and not person:
                return (len(low) - len(ending), COLORS["shared"])
            return (len(low) - len(ending), get_person_color(person, number))
    
    # Preterite endings
    preterite = ["aste", "iste", "aron", "ieron", "amos", "imos"]
    for ending in sorted(preterite, key=len, reverse=True):
        if low.endswith(ending):
            return (len(low) - len(ending), get_person_color(person, number))
    
    # Single-letter preterite endings
    if low.endswith("é"):
        return (len(low) - 1, COLORS["1"])
    if low.endswith("ó"):
        return (len(low) - 1, get_person_color("3", "Sing"))
    
    # Present tense endings
    present = ["amos", "áis", "emos", "éis", "imos", "ís", "an", "en", "as", "es", "is", "a", "e"]
    for ending in sorted(present, key=len, reverse=True):
        if low.endswith(ending):
            return (len(low) - len(ending), get_person_color(person, number))
    
    # Fallback: first person singular -o
    if low.endswith("o"):
        return (len(low) - 1, COLORS["1"])
    
    # No recognized ending - color last character
    return (len(low) - 1, get_person_color(person, number))

def colorize_text(text: str) -> str:
    """
    Colorize Spanish verb endings using AI-powered morphological analysis.
    Uses spaCy to:
    - Identify finite verbs (not infinitives, gerunds, participles)
    - Extract person and number for accurate coloring
    - Handle irregular verbs like tendrá, clitics like levantarse
    """
    doc = nlp(text)
    
    # Build a map of word positions to spaCy tokens
    token_map = {}
    for token in doc:
        token_map[token.idx] = token
    
    result = []
    current_pos = 0
    
    for token in doc:
        # Add any text before this token (spaces, punctuation handled by spaCy)
        if token.idx > current_pos:
            result.append(html.escape(text[current_pos:token.idx]))
        
        # Check if we should color this token
        if should_color_verb(token):
            person = token.morph.get("Person")
            number = token.morph.get("Number")
            person_val = person[0] if person else None
            number_val = number[0] if number else None
            
            # Get the part to color
            start_idx, color = get_ending_to_color(token.text, person_val, number_val)
            
            # Build colored HTML
            before = html.escape(token.text[:start_idx])
            after = html.escape(token.text[start_idx:])
            result.append(f"{before}<span style='color:{color};'>{after}</span>")
        else:
            # Not a verb or not finite - just escape and add
            result.append(html.escape(token.text))
        
        current_pos = token.idx + len(token.text)
    
    # Add any remaining text
    if current_pos < len(text):
        result.append(html.escape(text[current_pos:]))
    
    return "".join(result)

if __name__ == "__main__":
    text = sys.stdin.read()
    html_out = colorize_text(text)
    sys.stdout.write(html_out)
