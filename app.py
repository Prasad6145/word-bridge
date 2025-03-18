
import gradio as gr
import speech_recognition as sr
from deep_translator import GoogleTranslator
from gtts import gTTS
import os
from pydub import AudioSegment

# Initialize the recognizer
recognizer = sr.Recognizer()

# Function to perform translation
def translate_text(text, src_lang, target_lang):
    try:
        translation = GoogleTranslator(source=src_lang, target=target_lang).translate(text)
        return translation
    except Exception as e:
        return str(e)

# Function to provide text-to-speech for the translation
def text_to_speech(translation, lang):
    try:
        tts = gTTS(translation, lang=lang)
        audio_path = "output.mp3"
        tts.save(audio_path)
        return audio_path if os.path.exists(audio_path) else "Audio generation failed"
    except Exception as e:
        return str(e)

# Function to count words and characters in the source text
def count_words_and_chars(text):
    word_count = len(text.split())
    char_count = len(text)
    return f"Words: {word_count}, Characters: {char_count}"

# Function to clear text fields
def clear_text_fields():
    return "", "", "", ""

# Function to save translation to a text file
def save_translation(text, translation):
    with open("saved_translations.txt", "a") as f:
        f.write(f"Original: {text}\nTranslated: {translation}\n\n")
    return "Translation saved!"

# Function for speech recognition (live voice input to text)
def recognize_speech(audio):
    try:
        audio_segment = AudioSegment.from_file(audio)
        audio_segment.export("temp.wav", format="wav")

        with sr.AudioFile("temp.wav") as source:
            audio_data = recognizer.record(source)  # read the entire audio file
            text = recognizer.recognize_google(audio_data)
            return text
    except sr.UnknownValueError:
        return "Could not understand audio."
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {e}"

# List of languages
languages = [
    ('English', 'en'),
    ('Spanish', 'es'),
    ('French', 'fr'),
    ('German', 'de'),
    ('Italian', 'it'),
    ('Portuguese', 'pt'),
    ('Russian', 'ru'),
    ('Chinese (Simplified)', 'zh-CN'),
    ('Chinese (Traditional)', 'zh-TW'),
    ('Japanese', 'ja'),
    ('Korean', 'ko'),
    ('Hindi', 'hi'),
    ('Telugu', 'te'),
    ('Tamil', 'ta'),
    ('Arabic', 'ar')
]

# Define Gradio interface with merged components and custom title style
css = """
    body {
        background-color: white;  /* Set background color to white */
        color: black;  /* Set text color to black */
        margin: 0;
        padding: 0;
        height: 100vh;
        display: flex;
        justify-content: center;
        align-items: center;
    }
    .gradio-container {
        background-color: white;  /* Container background color */
        padding: 20px;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 10px;
        overflow-y: auto;  /* Enable vertical scrolling */
        max-height: 100vh;
        width: 100%;
        box-sizing: border-box;
    }
    .textbox-group, .button-row {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 10px;
        width: 100%;
    }
    #translate-btn {
        background-color: #4CAF50; /* Green */
        color: white; /* White text */
    }
    #tts-btn {
        background-color: #2196F3; /* Blue */
        color: white; /* White text */
    }
    #clear-btn {
        background-color: #f44336; /* Red */
        color: white; /* White text */
    }
    #save-btn {
        background-color: #FF9800; /* Orange */
        color: white; /* White text */
    }
    #upload-audio-btn {
        background-color: #9C27B0; /* Purple */
        color: white; /* White text */
    }
    #translate-btn, #tts-btn, #clear-btn, #save-btn, #upload-audio-btn {
        width: 100%; /* Stretch buttons to full width */
        margin: 5px 0;
        border: none; /* Remove border */
        padding: 10px; /* Add padding */
        border-radius: 5px; /* Rounded corners */
        cursor: pointer; /* Pointer cursor */
        font-size: 16px; /* Font size */
    }
    h1 {
        text-align: center;  /* Center the title */
        font-family: 'Algerian', sans-serif;  /* Change the font style */
        font-weight: bold;  /* Make the font bold */
        font-size: 32px;  /* Increase font size */
        color: black;  /* Set title color to dark purple */
    }
    #label {
        color: black;  /* Set label text color to black */
        font-size: 16px;  /* Set label font size */
        font-weight: bold;
    }
"""

with gr.Blocks(css=css) as demo:
    gr.Markdown("<h1>Word Bridge</h1>")

    # Grouping all components in a single column for unified layout
    with gr.Column(elem_classes="textbox-group"):
        # Input fields
        src_text = gr.Textbox(label="Text / Upload Audio",
                              placeholder="Type text or upload audio below...",
                              lines=4,
                              interactive=True,
                              elem_id="src-text-area")

        src_lang = gr.Dropdown(choices=[(name, code) for name, code in languages], value='en', label="Source Language")
        target_lang = gr.Dropdown(choices=[(name, code) for name, code in languages], value='fr', label="Target Language")

        # Outputs
        translation_output = gr.Textbox(label="Translated Text", interactive=False, lines=4, elem_id="translation-output")
        audio_output = gr.Audio(label="Listen to Translation")
        word_char_count = gr.Textbox(label="Word and Character Count", interactive=False, elem_id="word-char-count")
        status_message = gr.Textbox(label="Status", interactive=False, elem_id="status-message")

    # Buttons all merged into a single column
    with gr.Column(elem_classes="button-row"):
        translate_btn = gr.Button("Translate", elem_id="translate-btn", variant="primary")
        tts_btn = gr.Button("Listen to Translation", elem_id="tts-btn", variant="secondary")
        clear_btn = gr.Button("Clear", elem_id="clear-btn", variant="secondary")
        save_btn = gr.Button("Save Translation", elem_id="save-btn", variant="secondary")
        upload_audio_btn = gr.Button("Upload Audio", elem_id="upload-audio-btn", variant="secondary")

    # When the translate button is clicked
    translate_btn.click(translate_text, [src_text, src_lang, target_lang], translation_output)

    # Count words and characters after translation
    src_text.change(count_words_and_chars, src_text, word_char_count)

    # When the text-to-speech button is clicked
    tts_btn.click(text_to_speech, [translation_output, target_lang], audio_output)

    # When the clear button is clicked
    clear_btn.click(clear_text_fields, [], [src_text, translation_output, word_char_count, status_message])

    # When the save button is clicked
    save_btn.click(save_translation, [src_text, translation_output], status_message)

    # Upload audio button to start voice recognition
    upload_audio_btn.click(recognize_speech, inputs=gr.Audio(type='filepath'), outputs=src_text)

# Launch the app
demo.launch()
