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

def get_person_color(person: Optional[str], number: Optional[str], tense: Optional[str], mood: Optional[str]) -> str:
    """
    Get color based on grammatical person, number, tense, and mood from spaCy.
    Handles ambiguous forms:
    - Imperfect 1st/3rd singular: -aba, -ía (ambiguous)
    - Conditional 1st/3rd singular: -ría (ambiguous)
    - Subjunctive 3rd person (can be ambiguous)
    """
    if not person or not number:
        return COLORS["shared"]

    # Check for ambiguous imperfect (yo/él hablaba)
    if tense == "Imp" and person in ("1", "3") and number == "Sing":
        return COLORS["shared"]

    # Check for ambiguous conditional (yo/él hablaría)
    if mood == "Cnd" and person in ("1", "3") and number == "Sing":
        return COLORS["shared"]

    # Check for subjunctive - mark 1st/3rd person as shared
    if mood == "Sub" and person in ("1", "3") and number == "Sing":
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

def get_ending_to_color(word: str, person: Optional[str], number: Optional[str],
                        tense: Optional[str], mood: Optional[str]) -> tuple:
    """
    Determine which part of the word to color based on person/number/tense/mood.
    Returns (start_index, color)
    """
    low = word.lower()

    # Get the color based on morphology (handles ambiguity)
    color = get_person_color(person, number, tense, mood)

    # Special handling for haber (color whole auxiliary)
    if low in HABER:
        return (0, color)

    # Special handling for estar
    if low in ESTAR:
        if low == "estoy":
            idx = low.rfind("oy")
            return (idx, COLORS["1"])
        if low.endswith(("ás", "á", "amos", "áis", "án")):
            # Color the accent + ending
            for ending in ["ás", "á", "amos", "áis", "án"]:
                if low.endswith(ending):
                    return (len(low) - len(ending), color)

    # Special handling for ir
    if low in IR:
        if low == "voy":
            idx = low.rfind("oy")
            return (idx, COLORS["1"])
        if low.endswith(("as", "a", "amos", "áis", "an")):
            for ending in ["amos", "áis", "as", "an", "a"]:
                if low.endswith(ending):
                    return (len(low) - len(ending), color)

    # Future endings (not ambiguous between 1st/3rd)
    future = ["é", "ás", "á", "emos", "éis", "án"]
    for ending in sorted(future, key=len, reverse=True):
        if low.endswith(ending) and tense == "Fut":
            return (len(low) - len(ending), color)

    # Conditional endings (ambiguous between 1st/3rd singular)
    conditional = ["ía", "ías", "íamos", "íais", "ían"]
    for ending in sorted(conditional, key=len, reverse=True):
        if low.endswith(ending) and mood == "Cnd":
            return (len(low) - len(ending), color)

    # Imperfect endings (ambiguous between 1st/3rd singular for -aba/-ía)
    imperfect = ["ábamos", "ábais", "aban", "abas", "aba", "íamos", "íais", "ían", "ías", "ía"]
    for ending in sorted(imperfect, key=len, reverse=True):
        if low.endswith(ending) and tense == "Imp":
            return (len(low) - len(ending), color)

    # Preterite endings
    preterite = ["aste", "iste", "aron", "ieron", "amos", "imos"]
    for ending in sorted(preterite, key=len, reverse=True):
        if low.endswith(ending):
            return (len(low) - len(ending), color)

    # Single-letter preterite endings
    if low.endswith("é"):
        return (len(low) - 1, color)
    if low.endswith("ó"):
        return (len(low) - 1, color)

    # Present tense endings
    present = ["amos", "áis", "emos", "éis", "imos", "ís", "an", "en", "as", "es", "is", "a", "e"]
    for ending in sorted(present, key=len, reverse=True):
        if low.endswith(ending):
            return (len(low) - len(ending), color)

    # Fallback: first person singular -o
    if low.endswith("o"):
        return (len(low) - 1, color)

    # No recognized ending - color last character
    return (len(low) - 1, color)

def colorize_text(text: str) -> str:
    """
    Colorize Spanish verb endings using AI-powered morphological analysis.
    Uses spaCy to:
    - Identify finite verbs (not infinitives, gerunds, participles)
    - Extract person, number, tense, and mood for accurate coloring
    - Handle irregular verbs like tendrá, clitics like levantarse
    - Mark ambiguous forms (imperfect 1st/3rd, conditional 1st/3rd, subjunctive) as orange
    """
    doc = nlp(text)

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
            tense = token.morph.get("Tense")
            mood = token.morph.get("Mood")

            person_val = person[0] if person else None
            number_val = number[0] if number else None
            tense_val = tense[0] if tense else None
            mood_val = mood[0] if mood else None

            # Get the part to color
            start_idx, color = get_ending_to_color(token.text, person_val, number_val, tense_val, mood_val)

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
