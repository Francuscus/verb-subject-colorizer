# Paco Verb Colorizer - AI-Enhanced Version
# Usage: python paco_colorizer.py < input.txt > output.html
# Or import colorize_text(text) to get HTML with colored verb endings.

import re, html, sys
from typing import List, Dict
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
    "yo": "red",
    "tu": "blue",
    "el": "yellow",
    "nos": "purple",
    "ellos": "green",
    "shared": "orange",
}

ESTAR = ["estoy","estas","estás","esta","está","estamos","estan","están"]
IR = ["voy","vas","va","vamos","van"]
HABER = ["he","has","ha","hemos","han"]

def tokenize(text: str):
    return re.findall(r"\w+|[^\w\s]", text, flags=re.UNICODE)

def is_verb_token(tokens: List[str], i: int, pos_tags: Dict[str, str]) -> bool:
    """
    Use spaCy POS tagging to accurately identify finite verbs.
    Excludes: infinitives, participles, gerunds, nouns, adverbs.
    """
    tok = tokens[i]
    low = tok.lower()

    # Special cases (auxiliary verbs) - always color
    if low in ESTAR or low in IR or low in HABER:
        return True

    # Check if it's alphanumeric
    if not re.fullmatch(r"[^\W\d_]+", low, flags=re.UNICODE):
        return False

    # Get POS tag from spaCy
    pos = pos_tags.get(low, "")

    # Only color if spaCy identifies it as a VERB or AUX (auxiliary)
    if pos not in ("VERB", "AUX"):
        return False

    # Exclude infinitives (-ar, -er, -ir endings without conjugation)
    if low.endswith(("ar", "er", "ir")) and len(low) > 2:
        # Check if it's a true infinitive or a conjugated form
        # True infinitives: hablar, comer, vivir
        # Conjugated: llegar → llegué (not infinitive)
        if not any(low.endswith(ending) for ending in [
            "é", "ás", "á", "emos", "éis", "án",  # future
            "ía", "ías", "íamos", "íais", "ían"   # conditional
        ]):
            return False

    # Exclude participles (-ado, -ido) - these don't carry person marking
    if low.endswith(("ado", "ido", "ído")) and len(low) > 3:
        return False

    # Exclude gerunds (-ando, -iendo)
    if low.endswith(("ando", "iendo", "yendo")) and len(low) > 4:
        return False

    return True

def color_token(tokens: List[str], i: int) -> str:
    tok = tokens[i]
    low = tok.lower()

    # Present perfect (haber): color only after silent 'h'
    if low in HABER:
        mapping = {
            "he": ("yo","e"),
            "has": ("tu","as"),
            "ha": ("el","a"),
            "hemos": ("nos","emos"),
            "han": ("ellos","an"),
        }
        who, part = mapping[low]
        idx = tok.lower().rfind(part)
        return html.escape(tok[:idx]) + f"<span style='color:{COLORS[who]};'>" + html.escape(tok[idx:]) + "</span>"

    # Progressive (estar + gerund): yo => only 'oy' in 'estoy'; others => person marker
    if low in ESTAR:
        if low == "estoy":
            idx = tok.lower().rfind("oy")
            return html.escape(tok[:idx]) + f"<span style='color:{COLORS['yo']};'>" + html.escape(tok[idx:]) + "</span>"
        if low.endswith("ás"):  # tú
            return html.escape(tok[:-1]) + f"<span style='color:{COLORS['tu']};'>" + html.escape(tok[-1:]) + "</span>"
        if low.endswith("á"):   # él/ella/Ud.
            return html.escape(tok[:-1]) + f"<span style='color:{COLORS['el']};'>" + html.escape(tok[-1:]) + "</span>"
        if low.endswith("amos"):
            return html.escape(tok[:-4]) + f"<span style='color:{COLORS['nos']};'>" + html.escape(tok[-4:]) + "</span>"
        if low.endswith("án"):
            return html.escape(tok[:-1]) + f"<span style='color:{COLORS['ellos']};'>" + html.escape(tok[-1:]) + "</span>"

    # Ir a + infinitive: yo => only 'oy' in 'voy'; others => person marker
    if low in IR:
        if low == "voy":
            idx = tok.lower().rfind("oy")
            return html.escape(tok[:idx]) + f"<span style='color:{COLORS['yo']};'>" + html.escape(tok[idx:]) + "</span>"
        if low.endswith("s"):   # vas
            return html.escape(tok[:-1]) + f"<span style='color:{COLORS['tu']};'>" + html.escape(tok[-1:]) + "</span>"
        if low.endswith("a"):   # va
            return html.escape(tok[:-1]) + f"<span style='color:{COLORS['el']};'>" + html.escape(tok[-1:]) + "</span>"
        if low.endswith("mos"):
            return html.escape(tok[:-3]) + f"<span style='color:{COLORS['nos']};'>" + html.escape(tok[-3:]) + "</span>"
        if low.endswith("n"):
            return html.escape(tok[:-1]) + f"<span style='color:{COLORS['ellos']};'>" + html.escape(tok[-1:]) + "</span>"

    # Future/Conditional endings (attach to infinitive)
    for end, who in [
        ("íamos","nos"),("remos","nos"),("ríamos","nos"),
        ("ían","ellos"),("rán","ellos"),
        ("ías","tu"),("rás","tu"),
        ("ía","shared"),("rá","el"),
        ("é","yo"),("á","el"),
    ]:
        if low.endswith(end):
            base = low[:-len(end)]
            if base.endswith(("ar","er","ir")):
                idx = len(tok) - len(end)
                color = COLORS["shared"] if who=="shared" else COLORS[who]
                return html.escape(tok[:idx]) + f"<span style='color:{color};'>" + html.escape(tok[idx:]) + "</span>"

    # Imperfect
    if low.endswith("ábamos"):
        return html.escape(tok[:-4]) + f"<span style='color:{COLORS['nos']};'>" + html.escape(tok[-4:]) + "</span>"
    if low.endswith("íamos"):
        return html.escape(tok[:-4]) + f"<span style='color:{COLORS['nos']};'>" + html.escape(tok[-4:]) + "</span>"
    if low.endswith("aban"):
        return html.escape(tok[:-2]) + f"<span style='color:{COLORS['ellos']};'>" + html.escape(tok[-2:]) + "</span>"
    if low.endswith("ían"):
        return html.escape(tok[:-2]) + f"<span style='color:{COLORS['ellos']};'>" + html.escape(tok[-2:]) + "</span>"
    if low.endswith("abas") or low.endswith("ías"):
        return html.escape(tok[:-2]) + f"<span style='color:{COLORS['tu']};'>" + html.escape(tok[-2:]) + "</span>"
    if low.endswith("aba") or low.endswith("ía"):
        idx = len(tok) - (3 if low.endswith("aba") else 2)
        return html.escape(tok[:idx]) + f"<span style='color:{COLORS['shared']};'>" + html.escape(tok[idx:]) + "</span>"

    # Preterite (regular)
    if low.endswith("é"):
        return html.escape(tok[:-1]) + f"<span style='color:{COLORS['yo']};'>" + html.escape(tok[-1:]) + "</span>"
    if low.endswith("aste") or low.endswith("iste"):
        return html.escape(tok[:-4]) + f"<span style='color:{COLORS['tu']};'>" + html.escape(tok[-4:]) + "</span>"
    if low.endswith("ó"):
        return html.escape(tok[:-1]) + f"<span style='color:{COLORS['el']};'>" + html.escape(tok[-1:]) + "</span>"
    if low.endswith("amos") or low.endswith("imos"):
        return html.escape(tok[:-4]) + f"<span style='color:{COLORS['nos']};'>" + html.escape(tok[-4:]) + "</span>"
    if low.endswith("aron") or low.endswith("ieron"):
        return html.escape(tok[:-3]) + f"<span style='color:{COLORS['ellos']};'>" + html.escape(tok[-3:]) + "</span>"

    # Present defaults
    for end, who in [
        ("amos","nos"),("emos","nos"),("imos","nos"),
        ("an","ellos"),("en","ellos"),
        ("as","tu"),("es","tu"),
        ("a","el"),("e","el"),
        ("o","yo"),
    ]:
        if low.endswith(end):
            if who == "tu":
                return html.escape(tok[:-1]) + f"<span style='color:{COLORS['tu']};'>" + html.escape(tok[-1:]) + "</span>"
            if who == "ellos":
                return html.escape(tok[:-1]) + f"<span style='color:{COLORS['ellos']};'>" + html.escape(tok[-1:]) + "</span>"
            if who == "nos":
                return html.escape(tok[:-3]) + f"<span style='color:{COLORS['nos']};'>" + html.escape(tok[-3:]) + "</span>"
            if who == "el":
                return html.escape(tok[:-1]) + f"<span style='color:{COLORS['el']};'>" + html.escape(tok[-1:]) + "</span>"
            if who == "yo":
                return html.escape(tok[:-1]) + f"<span style='color:{COLORS['yo']};'>" + html.escape(tok[-1:]) + "</span>"

    return html.escape(tok)

def colorize_text(text: str) -> str:
    """
    Colorize Spanish verb endings using AI-powered POS tagging.

    Uses spaCy to accurately identify verbs (not nouns, adverbs, etc.)
    and colors only the person-marking endings in finite verbs.
    """
    # Use spaCy to get POS tags for all words
    doc = nlp(text)
    pos_tags = {}
    for token in doc:
        pos_tags[token.text.lower()] = token.pos_

    tokens = tokenize(text)
    out = []
    for i, tok in enumerate(tokens):
        if re.fullmatch(r"\w+", tok, flags=re.UNICODE) and is_verb_token(tokens, i, pos_tags):
            out.append(color_token(tokens, i))
        else:
            out.append(html.escape(tok))

    rebuilt = []
    idx = 0
    j = 0
    for m in re.finditer(r"\w+|[^\w\s]", text, flags=re.UNICODE):
        start, end = m.span()
        rebuilt.append(html.escape(text[idx:start]))
        rebuilt.append(out[j])
        idx = end
        j += 1
    rebuilt.append(html.escape(text[idx:]))
    return "".join(rebuilt)

if __name__ == "__main__":
    text = sys.stdin.read()
    html_out = colorize_text(text)
    sys.stdout.write(html_out)
