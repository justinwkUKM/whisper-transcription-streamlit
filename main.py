import streamlit as st
import openai
import os
import math
import tempfile
import wave
import json
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

    # Password input
    password = st.text_input("Enter Password to Enable Transcription", type="password")

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

        # Custom instructions for transcription
        custom_instructions = st.text_input(
            "Add any custom instructions for the transcription (optional):",
            ""
        )

        # Start transcription button (enabled only if password is correct)
        if password == "ANGSANA":
            if st.button("Start Transcription 📝"):
                # Show a message while processing
                with st.spinner("Transcribing audio, please wait... 🧠"):
                    try:
                        # Delete any existing chunk files from previous runs
                        for file in os.listdir():
                            if file.startswith("temp_chunk_") and file.endswith(".wav"):
                                os.remove(file)

                        # Save the uploaded mp3 file temporarily
                        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_mp3_file:
                            temp_mp3_file.write(uploaded_file.read())
                            temp_mp3_path = temp_mp3_file.name

                        # Convert mp3 to wav using ffmpeg (via os.system)
                        temp_wav_path = temp_mp3_path.replace(".mp3", ".wav")
                        os.system(f"ffmpeg -i {temp_mp3_path} {temp_wav_path}")

                        # Read the wav file and determine the duration
                        with wave.open(temp_wav_path, "rb") as wav_file:
                            frame_rate = wav_file.getframerate()
                            n_frames = wav_file.getnframes()
                            duration_seconds = n_frames / frame_rate
                            duration_minutes = duration_seconds / 60

                        # Split audio if longer than 1 minute
                        if duration_minutes > 1:
                            num_chunks = math.ceil(duration_minutes)
                            chunk_length_seconds = 60  # 1 minute chunks
                            transcripts = []

                            for i in range(num_chunks):
                                start_time = i * chunk_length_seconds
                                end_time = min((i + 1) * chunk_length_seconds, duration_seconds)

                                # Extract the chunk using ffmpeg
                                temp_chunk_path = f"temp_chunk_{i}.wav"
                                os.system(f"ffmpeg -i {temp_wav_path} -ss {start_time} -to {end_time} -c copy {temp_chunk_path}")

                                # Transcribe the chunk
                                with open(temp_chunk_path, "rb") as chunk_file:
                                    prompt = f"Transcribe the audio. The file mainly consists of {language_name}. {custom_instructions}" if custom_instructions else f"Transcribe the audio. The file mainly consists of {language_name}."
                                    chunk_transcript = client.audio.transcriptions.create(
                                        model="whisper-1",
                                        file=chunk_file,
                                        prompt=prompt
                                    )
                                    transcripts.append(chunk_transcript.text)

                                    # Append each chunk transcription to the JSON file
                                    try:
                                        with open("transcriptions.json", "r") as json_file:
                                            transcript_data = json.load(json_file)
                                    except FileNotFoundError:
                                        transcript_data = {}

                                    # Add or update the chunk transcription in the JSON file
                                    if uploaded_file.name not in transcript_data:
                                        transcript_data[uploaded_file.name] = ""
                                    transcript_data[uploaded_file.name] += f"{chunk_transcript.text}\n"

                                    # Save the updated JSON file
                                    with open("transcriptions.json", "w") as json_file:
                                        json.dump(transcript_data, json_file, indent=4)

                            # Combine all chunk transcripts
                            final_transcript = "\n".join(transcripts)
                        else:
                            # If the audio is less than 1 minute, transcribe directly
                            with open(temp_wav_path, "rb") as wav_file:
                                prompt = f"Transcribe the audio. The file mainly consists of {language_name}. {custom_instructions}" if custom_instructions else f"Transcribe the audio. The file mainly consists of {language_name}."
                                final_transcript = client.audio.transcriptions.create(
                                    model="whisper-1",
                                    file=wav_file,
                                    prompt=prompt
                                ).text

                            # Save transcription to a local JSON file
                            try:
                                with open("transcriptions.json", "r") as json_file:
                                    transcript_data = json.load(json_file)
                            except FileNotFoundError:
                                transcript_data = {}

                            transcript_data[uploaded_file.name] = final_transcript
                            with open("transcriptions.json", "w") as json_file:
                                json.dump(transcript_data, json_file, indent=4)

                        # Display the transcription
                        st.subheader("Transcription Result 📍:")
                        st.text_area("Transcription", final_transcript, height=200)
                        
                        # Download option for the transcription
                        st.download_button(
                            label="Download Transcription as TXT",
                            data=final_transcript,
                            file_name="transcription.txt",
                            mime="text/plain"
                        )
                    except Exception as e:
                        st.error(f"An error occurred during transcription: {str(e)}")
        else:
            st.warning("Please enter the correct password to enable transcription.")

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
# ffmpeg (install separately, e.g., via apt, brew, or download from ffmpeg.org)