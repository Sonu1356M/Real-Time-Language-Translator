import os
import time
import pygame
import streamlit as st
import tracemalloc
import asyncio
import speech_recognition as sr
from gtts import gTTS
from googletrans import LANGUAGES, Translator

# Start memory tracing
tracemalloc.start()

# Initialize translator and audio
translator = Translator()
pygame.mixer.init()

# Create language name -> code mapping
language_mapping = {name: code for code, name in LANGUAGES.items()}

def get_language_code(language_name):
    return language_mapping.get(language_name, language_name)

def translator_function(spoken_text, from_language, to_language):
    return translator.translate(spoken_text, src=from_language, dest=to_language)

def text_to_voice(text_data, to_language):
    tts = gTTS(text=text_data, lang=to_language, slow=False)
    tts.save("cache_file.mp3")
    audio = pygame.mixer.Sound("cache_file.mp3")
    audio.play()
    while pygame.mixer.get_busy():
        time.sleep(0.1)
    os.remove("cache_file.mp3")

# Async helper
def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    if loop.is_running():
        return coro  # Let Streamlit handle this if it's an async environment
    else:
        return loop.run_until_complete(coro)

# Streamlit UI
st.title("🔊 Real-Time Language Translator")

from_language_name = st.selectbox("Select Source Language:", list(LANGUAGES.values()))
to_language_name = st.selectbox("Select Target Language:", list(LANGUAGES.values()))

from_language = get_language_code(from_language_name)
to_language = get_language_code(to_language_name)

if st.button("🎙 Start Listening and Translate"):
    rec = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎧 Listening... Speak now!")
        rec.pause_threshold = 1
        try:
            audio = rec.listen(source, phrase_time_limit=5)
        except Exception as e:
            st.error(f"Microphone Error: {e}")
            st.stop()

    try:
        spoken_text = rec.recognize_google(audio, language=from_language)
        st.success(f"🗣️ You said: `{spoken_text}`")

        # Translate
        translated = translator_function(spoken_text, from_language, to_language)

        if asyncio.iscoroutine(translated):
            translated = run_async(translated)

        st.success(f"🌍 Translated: `{translated.text}`")

        # Speak
        st.info("🔊 Playing translation...")
        text_to_voice(translated.text, to_language)

    except Exception as e:
        st.error(f"❌ Error: {e}")
