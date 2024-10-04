import streamlit as st
import openai
import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")  # Replace "OPENAI_API_KEY" with the variable name in your .env file

client = OpenAI()

# List of top 100 languages (ISO 639-1 codes and language names)
LANGUAGES = [
    ("en", "English"), ("zh", "Chinese"), ("es", "Spanish"), ("hi", "Hindi"), ("ar", "Arabic"),
    ("bn", "Bengali"), ("pt", "Portuguese"), ("ru", "Russian"), ("ja", "Japanese"), ("pa", "Punjabi"),
    ("de", "German"), ("jv", "Javanese"), ("ko", "Korean"), ("fr", "French"), ("te", "Telugu"),
    ("mr", "Marathi"), ("tr", "Turkish"), ("ta", "Tamil"), ("vi", "Vietnamese"), ("ur", "Urdu"),
    ("it", "Italian"), ("fa", "Persian"), ("gu", "Gujarati"), ("kn", "Kannada"), ("pl", "Polish"),
    ("uk", "Ukrainian"), ("ml", "Malayalam"), ("or", "Odia"), ("my", "Burmese"), ("th", "Thai"),
    ("am", "Amharic"), ("az", "Azerbaijani"), ("be", "Belarusian"), ("bg", "Bulgarian"), ("cs", "Czech"),
    ("da", "Danish"), ("dv", "Dhivehi"), ("el", "Greek"), ("et", "Estonian"), ("eu", "Basque"),
    ("fi", "Finnish"), ("ga", "Irish"), ("ha", "Hausa"), ("he", "Hebrew"), ("hu", "Hungarian"),
    ("id", "Indonesian"), ("is", "Icelandic"), ("kk", "Kazakh"), ("km", "Khmer"), ("ky", "Kyrgyz"),
    ("la", "Latin"), ("lt", "Lithuanian"), ("lv", "Latvian"), ("mk", "Macedonian"), ("mn", "Mongolian"),
    ("ms", "Malay"), ("ne", "Nepali"), ("no", "Norwegian"), ("ps", "Pashto"), ("ro", "Romanian"),
    ("si", "Sinhala"), ("sk", "Slovak"), ("sl", "Slovenian"), ("so", "Somali"), ("sq", "Albanian"),
    ("sr", "Serbian"), ("sv", "Swedish"), ("sw", "Swahili"), ("ta", "Tamil"), ("tl", "Tagalog"),
    ("tn", "Tswana"), ("uz", "Uzbek"), ("xh", "Xhosa"), ("yo", "Yoruba"), ("zu", "Zulu")
]

# Define the Streamlit app
def main():
    # Page Layout
    st.set_page_config(page_title="MP3 Transcription App", page_icon="🎧", layout="centered")

    # Title and Description
    st.title("MP3 Transcription App 🎧")
    st.markdown(
        """
        ### Easily convert your MP3 audio files into text with the power of OpenAI's Whisper API.
        Just upload your MP3 file, select the language, and let us do the rest!
        📇 This app supports transcription in multiple languages and provides a seamless experience.
        """
    )

    # File uploader
    uploaded_file = st.file_uploader("Choose an MP3 file to transcribe", type=["mp3"], label_visibility="visible")

    if uploaded_file is not None:
        # Language selection dropdown with default as English
        language_code, language_name = st.selectbox(
            "Select the language for transcription",
            LANGUAGES,
            index=0,  # Default to English
            format_func=lambda x: x[1]
        )

        # Start transcription button
        if st.button("Start Transcription 📝"):
            # Show a message while processing
            with st.spinner("Transcribing audio, please wait... 🧠"):
                # Send the audio file to Whisper API
                uploaded_file.seek(0)  # Reset file pointer to the beginning
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=uploaded_file,
                    language=language_code
                )

                # Display the transcription
                st.subheader("Transcription Result 📍:")
                st.text_area("Transcription", transcript.text, height=200)
                
                # Download option for the transcription
                st.download_button(
                    label="Download Transcription as TXT",
                    data=transcript.text,
                    file_name="transcription.txt",
                    mime="text/plain"
                )

    # Footer
    st.markdown("""
    ---
    ##### 🌟 Developed with Streamlit & OpenAI Whisper 🌟
    📢 Feedback? Reach out to us!
    """)

# Run the app
if __name__ == "__main__":
    main()

# Required libraries:
# streamlit
# openai
# python-dotenv