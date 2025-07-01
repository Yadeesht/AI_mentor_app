import streamlit as st
import os
from typing import Optional
from modules.file_handler import extract_text_from_file
from modules.retriever import create_faiss_index, search_faiss_index
from modules.voice_input import transcribe_audio
import openai
from modules.voice_reply import generate_and_play_audio
from modules.gemini_api import generate_gemini_response
from gtts import gTTS
from streamlit_mic_recorder import mic_recorder

if 'faiss_index' not in st.session_state:
    st.session_state.faiss_index = None
if 'processed_filename' not in st.session_state:
    st.session_state.processed_filename = None
if 'recording' not in st.session_state:
    st.session_state.recording = False
if 'transcribed_text' not in st.session_state:
    st.session_state.transcribed_text = None
if 'current_subject' not in st.session_state:
    st.session_state.current_subject = None
if 'audio' not in st.session_state:
    st.session_state.audio = None

# Sidebar for app info and subject selection/upload
st.sidebar.title("About")
st.sidebar.info("""
**Modular AI Mentor Platform**
- Upload subject files (.pdf or .txt)
- Ask questions via text or voice
- Get avatar-based explanations
""")

# Subject selection in sidebar
subject_options = ["Python","AI"]  # Expanded options
selected_subject = st.sidebar.selectbox(
    "Select Subject", 
    ["-- Select --"] + subject_options,
    key="subject_select"
)

if selected_subject != "-- Select --":
    st.session_state.current_subject = selected_subject
    # File upload section in sidebar
    uploaded_file = st.sidebar.file_uploader(
        f"Upload {selected_subject} Material", 
        type=["pdf", "txt"],
        key="file_uploader"
    )
    if uploaded_file:
        try:
            # Only process if file is new or changed
            if (st.session_state.processed_filename != uploaded_file.name or 
                st.session_state.current_subject != selected_subject):
                    # Create subject directory if needed
                    folder_path = f"data/{selected_subject}"
                    os.makedirs(folder_path, exist_ok=True)
                    # Save the file
                    file_path = os.path.join(folder_path, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    # Extract text and create index
                    text = extract_text_from_file(uploaded_file)
                    if not text:
                        st.error("Could not extract text from the file.")
                        st.stop()
                    faiss_index = create_faiss_index(text)
                    # Update session state
                    st.session_state.faiss_index = faiss_index
                    st.session_state.processed_filename = uploaded_file.name
                    st.session_state.current_subject = selected_subject
                    st.sidebar.info(f"Index contains {faiss_index.index.ntotal} chunks of information.")
        except Exception as e:
            st.sidebar.error(f"An error occurred: {str(e)}")
            st.stop()

# Main app styling
st.markdown("""
<style>
    .centered-title {
        text-align: center;
        margin-bottom: 1rem;
    }
    .instructions {
        font-size: 1rem;
        text-align: center;
        margin-bottom: 1.5rem;
    }
    .mic-button {
        height: 3rem !important;
        width: 3rem !important;
        font-size: 1.5rem !important;
    }

</style>
""", unsafe_allow_html=True)

# Main app interface (chat only)


# Query section with WhatsApp-style interface
if not st.session_state.get('faiss_index'):
    st.markdown('<div style="text-align:center; margin-top: 2rem; font-size: 1.2rem; color: #aaa;">Please upload your file first to start asking questions.</div>', unsafe_allow_html=True)

if st.session_state.get('faiss_index'):
    st.markdown('<h2 style="text-align:center; margin-bottom: 1.5rem;">What are you looking for?</h2>', unsafe_allow_html=True)
    if 'recording' not in st.session_state:
        st.session_state.recording = False
    if 'transcribed_text' in st.session_state and st.session_state.transcribed_text:
        st.session_state.text_query = st.session_state.transcribed_text
        st.session_state.transcribed_text = None
        st.rerun()
    st.markdown('<div class="input-container">', unsafe_allow_html=True)
    col1, col2 = st.columns([4, 1])
    with col1:
        query = st.text_input(
            "Type or use voice...", 
            key="text_query",
            label_visibility="collapsed"
        )
    with col2:
        audio = mic_recorder(
            start_prompt="🎤",
            stop_prompt="⏹️",
            just_once=True,
            format="wav",
            key="mic"
        )
    st.markdown('</div>', unsafe_allow_html=True)
    if audio and audio["bytes"]:
        transcribed_text, error = transcribe_audio(audio["bytes"])
        if error:
            st.error(error)
        else:
            st.session_state.transcribed_text = transcribed_text
            st.rerun()
    if query and query.strip():
        try:
                results = search_faiss_index(st.session_state.faiss_index, query, k=3)
                if results:
                    st.subheader("Mentor's Answer:")
                    context_chunks = [r.page_content for r in results]
                    tutor_response = generate_gemini_response(context_chunks, query,selected_subject)
                    if tutor_response.startswith("[Error]"):
                        st.error(tutor_response)
                        st.session_state.tutor_response = tutor_response
                        st.session_state.audio = None
                    else:
                        st.write(tutor_response)
                        st.session_state.tutor_response = tutor_response
                        st.spinner("Creating audio...")
                        audio_path = generate_and_play_audio(tutor_response,voice='en-IN-NeerjaNeural')
                        if audio_path:
                            st.audio(audio_path, format='audio/mp3')
                        else:
                            st.warning("Could not generate audio.")
                else:
                    tutor_response = generate_gemini_response([],query,selected_subject)
                    if tutor_response.startswith("[Error]"):
                        st.error(tutor_response)
                        st.session_state.tutor_response = tutor_response
                        st.session_state.audio = None
                    else:
                        st.write(tutor_response)
                        st.session_state.tutor_response = tutor_response
        except Exception as e:
            st.error(f"An error occurred during the search: {str(e)}")
st.markdown("</div>", unsafe_allow_html=True)





