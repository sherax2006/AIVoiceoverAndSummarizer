 

import streamlit as st
import fitz  # PyMuPDF
from gtts import gTTS
import os
from transformers import pipeline
import torch
import nest_asyncio
nest_asyncio.apply()

st.set_page_config(page_title=" AI Voiceover and Summarizer Generator in Education", layout="wide")

# -------------------- Style --------------------
st.markdown(
    """
    <style>
    .title-container {
        background-color: #004d99;
        padding: 25px 40px;
        border-radius: 10px;
        color: #f0f0f0;
        font-size: 2.4rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 40px;
        box-shadow: 0 4px 8px rgba(0, 77, 153, 0.3);
    }
    div.stButton > button {
        background-color: #004d99;
        color: #ffffff;
        font-weight: 600;
        padding: 10px 24px;
        border-radius: 8px;
        border: none;
        box-shadow: 0 3px 7px rgba(0, 77, 153, 0.5);
        transition: background-color 0.3s ease;
        margin-bottom: 30px;
    }
    div.stButton > button:hover {
        background-color: #003366;
        cursor: pointer;
    }
    .stFileUploader > label {
        font-weight: 600;
        color: #004d99;
    }
    .stSuccess {
        color: #006600 !important;
        font-weight: 600 !important;
    }
    .stError {
        color: #cc0000 !important;
        font-weight: 600 !important;
    }
    </style>
    """, unsafe_allow_html=True
)

st.markdown('<div class="title-container"> AI Voiceover and Summarizer in Education</div>', unsafe_allow_html=True)

# -------------------- Summarizer --------------------
@st.cache_resource
def load_summarizer():
    return pipeline("summarization", model="philschmid/bart-large-cnn-samsum")


summarizer = load_summarizer()

# -------------------- Upload PDF --------------------
uploaded_file = st.file_uploader("📄 Upload Your Lecture PDF", type=["pdf"])

if uploaded_file:
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    st.success(f"✅ Extracted {len(doc)} slides.")

    for idx, page in enumerate(doc):
        zoom = 2
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        img_bytes = pix.tobytes("png")
        st.image(img_bytes, caption=f"Original Slide {idx + 1}", use_container_width=True)
 
        slide_text = page.get_text()
 
        if st.button(f"🎧 Generate Voiceover for Slide {idx + 1}", key=f"btn_{idx}"):
            try:
                tts = gTTS(text=slide_text, lang='en', slow=False)
                audio_filename = f"slide_{idx+1}_voiceover.mp3"
                tts.save(audio_filename)
                with open(audio_filename, "rb") as audio_file:
                    st.audio(audio_file.read(), format="audio/mp3")
                st.success(f"✅ Voiceover for Slide {idx + 1} generated!")
            except Exception as e:
                st.error(f"❌ Error generating voiceover: {e}")
 
        if st.button(f"📄 Summarize Slide {idx + 1}", key=f"summary_btn_{idx}"):
            try:
                if len(slide_text.strip()) < 30:
                    raise ValueError("Text too short for summarization.")
                summary_output = summarizer(slide_text,  min_length=30, do_sample=False)
                summary = summary_output[0]['summary_text']
            except Exception:
                summary = "❗ Unable to generate a meaningful summary. The content may be too short or unstructured."

            st.info(f"📌 Summary for Slide {idx + 1}:\n\n{summary}")

            if summary and "Unable" not in summary:
                if st.button(f"🎧 Generate Voiceover for Summary of Slide {idx + 1}", key=f"summary_audio_btn_{idx}"):
                    try:
                        tts_summary = gTTS(text=summary, lang='en', slow=False)
                        summary_audio_filename = f"slide_{idx+1}_summary.mp3"
                        tts_summary.save(summary_audio_filename)
                        with open(summary_audio_filename, "rb") as audio_file:
                            st.audio(audio_file.read(), format="audio/mp3")
                        st.success(f"✅ Voiceover for Summary of Slide {idx + 1} generated!")
                    except Exception as e:
                        st.error(f"❌ Error generating summary voiceover: {e}")
