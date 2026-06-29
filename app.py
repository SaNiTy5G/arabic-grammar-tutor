import streamlit as str
import hashlib
from openai import OpenAI

# 1. PASTE YOUR ACTUAL OPENAI API KEY BETWEEN THE QUOTES BELOW
# Example: MY_API_KEY = "sk-proj-..."
MY_API_KEY = "YOUR_ACTUAL_OPENAI_API_KEY_HERE"

# Page setup optimized for a premium mobile experience
str.set_page_config(page_title="Anas AI - Live Voice", page_icon="🗣️", layout="centered")

# Custom Premium CSS Design
str.markdown("""
    <style>
    .stApp {
        background-color: #0d1117;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    h1 {
        color: #ffffff !important;
        font-weight: 800 !important;
        letter-spacing: -0.5px;
        text-align: center;
        margin-bottom: 5px !important;
    }
    .subtext {
        color: #8b949e;
        text-align: center;
        font-size: 14px;
        margin-bottom: 30px;
    }
    .voice-card {
        background: linear-gradient(135deg, #161b22 0%, #21262d 100%);
        border: 1px solid #30363d;
        border-radius: 20px;
        padding: 25px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
        margin-bottom: 20px;
    }
    .custom-label {
        color: #58a6ff;
        font-weight: 600;
        font-size: 14px;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    div[data-testid="stAudioInput"] {
        background-color: #0d1117 !important;
        border: 1px solid #30363d !important;
        border-radius: 14px !important;
        padding: 10px !important;
    }
    /* This completely hides the sidebar navigation arrow on mobile */
    button[data-testid="collapsedControl"] {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

str.markdown("<h1>🗣️ Live Arabic Tutor</h1>", unsafe_allow_html=True)
str.markdown("<p class='subtext'>Talk to Anas fluently. Your voice note will process, and he will respond out loud automatically.</p>", unsafe_allow_html=True)

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

# Initialize state structures
if "messages" not in str.session_state:
    str.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]
if "audio_responses" not in str.session_state:
    str.session_state.audio_responses = {}

# Display previous messages
for idx, message in enumerate(str.session_state.messages):
    if message["role"] != "system":
        with str.chat_message(message["role"]):
            str.markdown(message["content"])
            if message["role"] == "assistant" and idx in str.session_state.audio_responses:
                str.audio(str.session_state.audio_responses[idx], format="audio/mp3", autoplay=False)

# Main Interface Card
str.markdown("<div class='voice-card'>", unsafe_allow_html=True)
str.markdown("<div class='custom-label'>🎙️ Tap to Speak to Your Teacher</div>", unsafe_allow_html=True)

audio_value = str.audio_input("Record Voice Note")

str.markdown("</div>", unsafe_allow_html=True)

# Processing logic execution
if audio_value:
    if MY_API_KEY == "YOUR_ACTUAL_OPENAI_API_KEY_HERE" or not MY_API_KEY:
        str.error("Please add your secret OpenAI API key to line 7 of the code on GitHub.")
        str.stop()

    audio_bytes = audio_value.getvalue()
    audio_hash = hashlib.md5(audio_bytes).hexdigest()

    if "last_processed_hash" not in str.session_state or str.session_state.last_processed_hash != audio_hash:
        str.session_state.last_processed_hash = audio_hash
        
        client = OpenAI(api_key=MY_API_KEY)
        
        with str.spinner("Listening..."):
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=("audio.wav", audio_bytes)
            )
            user_text = transcript.text

        str.session_state.messages.append({"role": "user", "content": user_text})
        
        with str.chat_message("assistant"):
            text_placeholder = str.empty()
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=str.session_state.messages
            )
            full_response_text = response.choices[0].message.content
            text_placeholder.markdown(full_response_text)
            
            with str.spinner("Anas is replying..."):
                tts_response = client.audio.speech.create(
                    model="tts-1",
                    voice="alloy", 
                    input=full_response_text
                )
                assistant_audio_bytes = tts_response.content
                str.audio(assistant_audio_bytes, format="audio/mp3", autoplay=True)

        str.session_state.messages.append({"role": "assistant", "content": full_response_text})
        new_idx = len(str.session_state.messages) - 1
        str.session_state.audio_responses[new_idx] = assistant_audio_bytes
        
        str.rerun()
