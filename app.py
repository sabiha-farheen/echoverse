import os
import streamlit as st
from dotenv import load_dotenv
from ibm_watson import TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
import requests

# Load environment variables
load_dotenv()

# IBM Watsonx Granite API (LLM for text rewriting)
WATSONX_API_KEY = os.getenv("WATSONX_API_KEY")
WATSONX_URL = os.getenv("WATSONX_URL")

# IBM Watson Text-to-Speech
WATSON_TTS_API_KEY = os.getenv("WATSON_TTS_API_KEY")
WATSON_TTS_URL = os.getenv("WATSON_TTS_URL")

# Initialize Watson TTS
tts_authenticator = IAMAuthenticator(WATSON_TTS_API_KEY)
tts = TextToSpeechV1(authenticator=tts_authenticator)
tts.set_service_url(WATSON_TTS_URL)

# Streamlit UI
st.title("EchoVerse 🎧")
st.write("AI-Powered Audiobook Creation Tool")

# Text input
user_text = st.text_area("Enter your text here:")

# Button
if st.button("Generate Audiobook"):
    if not user_text.strip():
        st.warning("⚠️ Please enter some text first.")
    else:
        # 🔹 Step 1: Call IBM Watsonx Granite API to rewrite text
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {WATSONX_API_KEY}"
        }
        payload = {
            "input": [{"role": "user", "content": user_text}],
            "parameters": {"decoding_method": "greedy"}
        }

        try:
            response = requests.post(WATSONX_URL, json=payload, headers=headers)
            response.raise_for_status()
            rewritten_text = response.json().get("output", user_text)  # fallback if API fails
        except Exception as e:
            st.error(f"Error calling Watsonx API: {e}")
            rewritten_text = user_text

        st.subheader("📖 Rewritten Text")
        st.write(rewritten_text)

        # 🔹 Step 2: Convert rewritten text to speech
        try:
            with open("output.mp3", "wb") as audio_file:
                audio_file.write(
                    tts.synthesize(
                        rewritten_text,
                        voice="en-US_AllisonV3Voice",
                        accept="audio/mp3"
                    ).get_result().content
                )

            st.audio("output.mp3", format="audio/mp3")
            st.download_button("⬇️ Download MP3", data=open("output.mp3", "rb"), file_name="audiobook.mp3")

        except Exception as e:
            st.error(f"Error with Watson TTS: {e}")
