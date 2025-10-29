---
title: Paco Verb Colorizer
emoji: 🎨
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: mit
---

# 🎨 Paco Verb Colorizer

An automatic Spanish verb person-marking tool based on **Paco's Grammar** methodology.

## What It Does

This tool automatically colors Spanish verb endings by grammatical person:

- 🔴 **yo** (I) - red
- 🔵 **tú** (you, singular) - blue
- 🟡 **él/ella/Ud.** (he/she/you formal) - yellow
- 🟣 **nosotros** (we) - purple
- 🟢 **ellos/ellas/Uds.** (they) - green
- 🟠 **shared** (ambiguous yo/él) - orange

## Features

✅ **Smart Verb Detection**: Uses linguistic gates to distinguish verbs from nouns
- "el canto" (the song) → NOT colored
- "yo canto" (I sing) → colored

✅ **Character-Level Coloring**: Colors only the person marker, not the whole word
- habl**o** (I speak)
- est**oy** (I am)
- h**e** comido (I have eaten)

✅ **All Major Tenses**: Present, preterite, imperfect, future, conditional

✅ **Special Cases**: Handles *haber*, *estar*, *ir a + infinitive*

## How It Works

### Phase 1: Verb Detection Gate
Filters out non-verbs using:
- Articles/determiners ("el", "la", "mi", "tu")
- Adverbs (words ending in "-mente")
- Context clues (subject pronouns, negations)

### Phase 2: Person Identification
Colors the specific person-marking ending:
- **yo**: -o, -é, -aba/-ía (shared)
- **tú**: -s (distinctive marker)
- **él/ella**: thematic vowel -a, -e
- **nosotros**: -mos
- **ellos/ellas**: -n

### Special Handling
- **haber**: h + **e**/as/a (never colors the 'h')
- **estar**: est + **oy**/ás/á (for progressive)
- **ir**: v + **oy**/as/a (for *ir a* constructions)

## Examples

**Input:**
```
Yo hablo español mientras mi hermana estudia matemáticas.
```

**Output:**
- Yo habl**o** (red)
- español
- mientras
- mi
- hermana
- estudi**a** (yellow)
- matemáticas

**Why "estudia" but not "hermana"?**
"hermana" follows the determiner "mi", so it's identified as a noun, not a verb!

## Use Cases

- 📚 **Language Learning**: Visual aid for understanding Spanish verb conjugation
- ✏️ **Grammar Teaching**: Demonstrate person-marking patterns
- 📝 **Text Analysis**: Quick identification of verb persons in Spanish texts

## Technical Details

- **Framework**: Gradio web interface
- **Language**: Python 3
- **Method**: Rule-based linguistic analysis (no ML/NLP libraries needed)
- **Based On**: Paco's Grammar methodology for Spanish verb person marking

## License

MIT License - See LICENSE file for details

## Credits

Developed for Spanish language learners and teachers.
Based on Paco's Grammar approach to teaching Spanish verb conjugation.
