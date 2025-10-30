"""
Paco Verb Colorizer - Web Interface
Colors Spanish verb endings by grammatical person using Paco's Grammar methodology.
"""

import gradio as gr
from paco_colorizer import colorize_text

# Example texts for users to try
EXAMPLES = [
    ["Yo hablo español y tú hablas inglés."],
    ["Nosotros comemos mientras ellos estudian."],
    ["El canto es hermoso pero yo canto mejor."],
    ["María hablaba con Juan cuando llegué."],
    ["Mañana iré al mercado y compraré frutas."],
    ["Estoy estudiando mientras mi hermana está durmiendo."],
    ["He comido mucho pero todavía tengo hambre."],
]

def colorize_spanish_verbs(text):
    """
    Colorize Spanish verb endings by person.

    Colors:
    - yo (I) → red
    - tú (you, singular informal) → blue
    - él/ella/usted (he/she/you formal) → yellow
    - nosotros (we) → purple
    - ellos/ellas/ustedes (they/you plural) → green
    - shared endings (yo/él ambiguous like -aba, -ía) → orange
    """
    if not text.strip():
        return "<p style='color: gray;'>Enter some Spanish text above to see verb colorization.</p>"

    html_output = colorize_text(text)

    # Wrap in a nice container
    styled_output = f"""
    <div style="
        font-family: 'Georgia', serif;
        font-size: 18px;
        line-height: 1.8;
        padding: 20px;
        background: white;
        border-radius: 10px;
        border: 2px solid #e0e0e0;
    ">
        {html_output}
    </div>
    <div style="margin-top: 20px; padding: 15px; background: #f0f7ff; border-radius: 8px; border-left: 4px solid #2196F3;">
        <strong>🎨 Color Key:</strong><br>
        <span style="color: red;">●</span> <strong style="color: red;">yo</strong> (I) &nbsp;&nbsp;
        <span style="color: blue;">●</span> <strong style="color: blue;">tú</strong> (you) &nbsp;&nbsp;
        <span style="color: yellow; background: #333; padding: 2px 6px; border-radius: 3px;">●</span> <strong>él/ella/Ud.</strong> (he/she/you formal) &nbsp;&nbsp;
        <span style="color: purple;">●</span> <strong style="color: purple;">nosotros</strong> (we) &nbsp;&nbsp;
        <span style="color: green;">●</span> <strong style="color: green;">ellos/ellas/Uds.</strong> (they) &nbsp;&nbsp;
        <span style="color: orange;">●</span> <strong style="color: orange;">shared</strong> (yo/él ambiguous)
    </div>
    """

    return styled_output

# Create Gradio interface
with gr.Blocks(title="Paco Verb Colorizer - Spanish Grammar Tool") as demo:
    gr.Markdown("""
    # 🎨 Paco Verb Colorizer
    ### Automatic Spanish Verb Person Marking

    This tool automatically colors Spanish verb endings based on **Paco's Grammar** methodology.
    Only colors person markers in **finite main verbs** (not infinitives, participles, or gerunds).

    **Features:**
    - ✅ Distinguishes verbs from nouns (e.g., "el canto" won't be colored, but "yo canto" will)
    - ✅ Colors only the person-marking ending, not the whole word
    - ✅ Handles all major tenses: present, preterite, imperfect, future, conditional
    - ✅ Special handling for: *haber*, *estar*, *ir a + infinitive*
    """)

    with gr.Row():
        with gr.Column(scale=1):
            input_text = gr.Textbox(
                label="📝 Enter Spanish Text",
                placeholder="Type or paste Spanish text here...\nExample: Yo hablo español y tú hablas inglés.",
                lines=8,
                value="Yo hablo español mientras mi hermana estudia matemáticas."
            )

            colorize_btn = gr.Button("🎨 Colorize Verbs", variant="primary", size="lg")

            gr.Markdown("### 💡 Try These Examples:")
            gr.Examples(
                examples=EXAMPLES,
                inputs=[input_text],
                label=None
            )

        with gr.Column(scale=1):
            output_html = gr.HTML(
                label="Colorized Output",
                value="<p style='color: gray; padding: 20px;'>Click 'Colorize Verbs' to see results...</p>"
            )

    gr.Markdown("""
    ---
    ### 📚 How It Works

    **Verb Detection:**
    - Uses AI-powered POS tagging (spaCy) to accurately identify verbs
    - Filters out: nouns after articles ("el canto"), adverbs ("-mente"), infinitives, participles, gerunds

    **Person Markers Colored:**
    - **yo**: -o, -é, -aba, -ía (when unambiguous)
    - **tú**: -s (almost always)
    - **él/ella/Ud.**: -a, -e, -ó (thematic vowel)
    - **nosotros**: -mos
    - **ellos/ellas/Uds.**: -n
    - **shared**: -aba, -ía (could be yo OR él/ella)

    **Special Cases:**
    - *haber*: Colors the entire auxiliary (he, has, ha, hemos, han)
    - *estar*: est**oy**, est**ás**, est**á**
    - *ir*: v**oy**, v**as**, v**a**

    ---
    Created with ❤️ using Paco's Grammar methodology + AI-powered verb detection.
    """)

    # Connect button to function
    colorize_btn.click(
        fn=colorize_spanish_verbs,
        inputs=[input_text],
        outputs=[output_html]
    )

    # Also trigger on Enter key in textbox
    input_text.submit(
        fn=colorize_spanish_verbs,
        inputs=[input_text],
        outputs=[output_html]
    )

# Launch the app
if __name__ == "__main__":
    demo.launch()
