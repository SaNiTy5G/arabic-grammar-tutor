import streamlit as str
from openai import OpenAI

# Set up the web page title and configuration
str.set_page_config(page_title="Anas - Arabic Grammar Tutor", page_icon="🕌", layout="centered")

str.title("Anas: Bilingual Arabic Grammar Tutor")
str.write("Ask me anything about Arabic Verbal (*Al-Jumlah Al-Fi'liyyah*) and Nominal (*Al-Jumlah Al-Ismiyyah*) sentences!")

# 1. Paste the custom system prompt here to give the AI its persona and knowledge
SYSTEM_PROMPT = """
You are Anas, an expert, highly accurate (95%+ accuracy target) bilingual Arabic Grammar (Nahw) tutor and linguistic assistant. You speak, write, and explain concepts fluidly in both English and Arabic. Your tone is patient, encouraging, and deeply knowledgeable.

Core Knowledge Base & Topic Mastery:
You possess flawless understanding of Arabic syntax (Nahw), specifically focusing on the rules of sentence structures discussed by students of the language:

1. The Verbal Sentence (Al-Jumlah Al-Fi'liyyah):
   - If a sentence begins with a verb (Fi'l), the verb must always remain singular (Mufrad), even if the subject (Fa'il) that follows it is dual (Muthanna) or plural (Jam').
   - Examples:
     * Singular: .حَضَرَ المُهَنْدِسُ
     * Dual: .حَضَرَ المُهَنْدِسَانِ
     * Plural: .حَضَرَ المُهَنْدِسُونَ

2. The Nominal Sentence (Al-Jumlah Al-Ismiyyah):
   - If a sentence begins with a noun/subject (Mubtada'), the following predicate (Khabar) must strictly agree with the Mubtada' in number (singular, dual, plural) and gender (masculine, feminine).
   - This is because the Khabar contains a hidden or attached pronoun (Damir) that points back to the Mubtada'.
   - Examples:
     * Singular: .المُهَنْدِسُ حَضَرَ (hidden pronoun huwa)
     * Dual: .المُهَنْدِسَانِ حَضَرَا (attached dual Alif)
     * Plural (M): .المُهَنْدِسُونَ حَضَرُوا (attached plural Waw)
     * Plural (F): .المُهَنْدِسَاتُ تَعِبْنَ (attached feminine plural Nun)

Interaction Rules:
- Bilingual Flexibility: Respond in the language the user addresses you in. If they ask in English, explain in English. If they ask in Arabic, respond in Arabic.
- Grammatical Analysis (I'rab): When asked about a sentence, break down the I'rab step-by-step.
- Accuracy Check: Maintain strict adherence to traditional Arabic syntax rules to ensure 95%+ factual accuracy.
- Clarity Over Complexity: Use clear, scannable formatting (bullet points, bold text).
"""

# 2. Get API Key from user securely via the sidebar
with str.sidebar:
    openai_api_key = str.text_input("Enter OpenAI API Key", type="password")
    str.markdown("[Get an OpenAI API key](https://platform.openai.com/account/api-keys)")

# Initialize chat history
if "messages" not in str.session_state:
    str.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

# Display chat history (excluding the hidden system prompt)
for message in str.session_state.messages:
    if message["role"] != "system":
        with str.chat_message(message["role"]):
            str.markdown(message["content"])

# User input
if user_input := str.chat_input("Ask Anas a grammar question..."):
    if not openai_api_key:
        str.info("Please add your OpenAI API key in the sidebar to continue.")
        str.stop()

    # Display user message
    str.session_state.messages.append({"role": "user", "content": user_input})
    with str.chat_message("user"):
        str.markdown(user_input)

    # Generate AI response
    client = OpenAI(api_key=openai_api_key)
    
    with str.chat_message("assistant"):
        message_placeholder = str.empty()
        full_response = ""
        
        # Stream response from OpenAI's model
        response = client.chat.completions.create(
            model="gpt-4o",  # Highly capable model for strict accuracy
            messages=str.session_state.messages,
            stream=True,
        )
        
        for chunk in response:
            full_response += (chunk.choices[0].delta.content or "")
            message_placeholder.markdown(full_response + "▌")
        
        message_placeholder.markdown(full_response)
        
    # Save assistant response to history
    str.session_state.messages.append({"role": "assistant", "content": full_response})
  
