import streamlit as str
import hashlib
from openai import OpenAI

# Page setup optimized for an immersive mobile voice experience
str.set_page_config(page_title="Anas - Live Voice Tutor", page_icon="🗣️", layout="centered")

str.title("🗣️ Live Arabic Voice Conversation")
str.write("Talk to Anas cleanly. Once you finish recording, he will answer you back out loud automatically!")

# Core system instructions for the Arabic Grammar Persona
SYSTEM_PROMPT = """
You are Anas, an expert, highly accurate (95%+ accuracy target) bilingual Arabic Grammar (Nahw) tutor and linguistic assistant. You speak, write, and explain concepts fluidly in both English and Arabic. Your tone is patient, encouraging, and deeply knowledgeable.

Core Knowledge Base:
1. The Verbal Sentence (Al-Jumlah Al-Fi'liyyah):
   - Verb must always remain singular (Mufrad), even if the subject (Fa'il) is dual or plural.
   - Examples: .حَضَرَ المُهَنْدِسُ / .حَضَرَ المُهَنْدِسَانِ / .حَضَرَ المُهَنْدِسُونَ

2. The Nominal Sentence (Al-Jumlah Al-Ismiyyah):
   - The predicate (Khabar) must strictly agree with the starting noun (Mubtada') in number and gender.
   - Examples: .المُهَنْدِسُ حَضَرَ / .المُهَنْدِسَانِ حَضَرَا / .المُهَنْدِسُونَ حَضَرُوا

Interaction Rules:
- You are speaking in a live voice conversation. Keep your spoken explanations brief, engaging, and clear to hear.
- Respond in the same language the user speaks to you. 
"""

# Secure sidebar for your API Key
with str.sidebar:
    openai_api_key = str.text_input("Enter OpenAI API Key", type="password")
    str.markdown("[Get an OpenAI API key](https://platform.openai.com/account/api-keys)")

# Initialize state arrays to hold conversation history
if "messages" not in str.session_state:
    str.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
if "audio_responses" not in str.session_state:
    str.session_state.audio_responses = {}

# Display older chat logs (Autoplay is set to FALSE here so past history stays quiet)
for idx, message in enumerate(str.session_state.messages):
    if message["role"] != "system":
        with str.chat_message(message["role"]):
            str.markdown(message["content"])
            if message["role"] == "assistant" and idx in str.session_state.audio_responses:
                str.audio(str.session_state.audio_responses[idx], format="audio/mp3", autoplay=False)

str.markdown("---")

# Mobile microphone recording element
audio_value = str.audio_input("Tap the mic to speak to your teacher 🎙️")

if audio_value:
    if not openai_api_key:
        str.info("Please add your OpenAI API key in the sidebar to begin your lesson.")
        str.stop()

    # Create a unique hash of the audio to prevent infinite processing loops
    audio_bytes = audio_value.getvalue()
    audio_hash = hashlib.md5(audio_bytes).hexdigest()

    if "last_processed_hash" not in str.session_state or str.session_state.last_processed_hash != audio_hash:
        str.session_state.last_processed_hash = audio_hash
        
        client = OpenAI(api_key=openai_api_key)
        
        # 1. Convert your voice note into text (Whisper API)
        with str.spinner("Listening to you..."):
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=("audio.wav", audio_bytes)
            )
            user_text = transcript.text

        str.session_state.messages.append({"role": "user", "content": user_text})
        
        # 2. Generate text response from the Arabic tutor logic (GPT-4o)
        with str.chat_message("assistant"):
            text_placeholder = str.empty()
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=str.session_state.messages
            )
            full_response_text = response.choices[0].message.content
            text_placeholder.markdown(full_response_text)
            
            # 3. Convert the text reply to an immediate audio stream (TTS API)
            with str.spinner("Anas is replying..."):
                tts_response = client.audio.speech.create(
                    model="tts-1",
                    voice="alloy", 
                    input=full_response_text
                )
                assistant_audio_bytes = tts_response.content
                
                # CRITICAL CHANGE: Autoplay is set to TRUE only for the active live response
                str.audio(assistant_audio_bytes, format="audio/mp3", autoplay=True)

        # Save indices to keep the session state clean
        str.session_state.messages.append({"role": "assistant", "content": full_response_text})
        new_idx = len(str.session_state.messages) - 1
        str.session_state.audio_responses[new_idx] = assistant_audio_bytes
        
        # Refresh UI layout cleanly
        str.rerun()
      
