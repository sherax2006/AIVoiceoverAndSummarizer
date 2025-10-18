# # pip install gtts

# # pip install typer==0.3.2 click==7.1.2 gtts==2.2.3 spleeter==2.4.0

import os
# Streamlit watcher can crash with some torch modules; disable file watcher
os.environ.setdefault("STREAMLIT_SERVER_FILE_WATCHER_TYPE", "none")
# Avoid optional backends causing heavy imports/crashes
os.environ.setdefault("TRANSFORMERS_NO_TF", "1")
os.environ.setdefault("TRANSFORMERS_NO_FLAX", "1")

import streamlit as st
import fitz  # PyMuPDF
from gtts import gTTS
from io import BytesIO
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

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
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model_name = "facebook/bart-large-cnn"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
    model = model.to(device)

    def summarize(text: str, max_length: int = 150, min_length: int = 40) -> str:
        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=1024,
        )
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with torch.no_grad():
            summary_ids = model.generate(
                **inputs,
                max_length=max_length,
                min_length=min_length,
                do_sample=False,
                num_beams=4,
                early_stopping=True,
            )
        return tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    return summarize


summarize_fn = load_summarizer()

# -------------------- Upload PDF --------------------
uploaded_file = st.file_uploader("📄 Upload Your Lecture PDF", type=["pdf"])

if uploaded_file:
    doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
    st.success(f"✅ Extracted {len(doc)} slides.")

    zoom = st.sidebar.slider("Zoom", 1.0, 3.0, 2.0, 0.25)
    render_images = st.sidebar.checkbox("Render slide images", value=True)
    start_page = st.sidebar.number_input("Start page", min_value=1, max_value=len(doc), value=1, step=1)
    end_page = st.sidebar.number_input("End page", min_value=start_page, max_value=len(doc), value=len(doc), step=1)

    def chunk_text(text, max_chars=2000):
        t = text.strip()
        if len(t) <= max_chars:
            return [t]
        chunks = []
        start = 0
        while start < len(t):
            end = min(start + max_chars, len(t))
            cut = t[start:end]
            last_period = cut.rfind(".")
            if last_period != -1 and end != len(t):
                end = start + last_period + 1
            chunks.append(t[start:end].strip())
            start = end
        return [c for c in chunks if c]

    for local_idx, page in enumerate(doc[int(start_page)-1:int(end_page)]):
        idx = (int(start_page) - 1) + local_idx
        if render_images:
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            img_bytes = pix.tobytes("png")
            st.image(img_bytes, caption=f"Original Slide {idx + 1}", use_container_width=True)

        slide_text = page.get_text()

        if st.button(f"🎧 Generate Voiceover for Slide {idx + 1}", key=f"btn_{idx}"):
            try:
                cache_key = f"audio_{idx}"
                if cache_key in st.session_state:
                    st.audio(st.session_state[cache_key], format="audio/mp3")
                else:
                    with st.spinner("Generating voiceover..."):
                        tts = gTTS(text=slide_text, lang='en', slow=False)
                        buf = BytesIO()
                        tts.write_to_fp(buf)
                        audio_bytes = buf.getvalue()
                        st.session_state[cache_key] = audio_bytes
                        st.audio(audio_bytes, format="audio/mp3")
                st.success(f"✅ Voiceover for Slide {idx + 1} generated!")
            except Exception as e:
                st.error(f"❌ Error generating voiceover: {e}")

        if st.button(f"📄 Summarize Slide {idx + 1}", key=f"summary_btn_{idx}"):
            try:
                if len(slide_text.strip()) < 30:
                    raise ValueError("Text too short for summarization.")
                cache_key_sum = f"summary_{idx}"
                if cache_key_sum in st.session_state:
                    summary = st.session_state[cache_key_sum]
                else:
                    with st.spinner("Summarizing slide..."):
                        parts = chunk_text(slide_text)
                        partials = []
                        for p in parts:
                            out_text = summarize_fn(p, max_length=150, min_length=40)
                            partials.append(out_text)
                        combined = " ".join(partials)
                        if len(partials) > 1:
                            summary = summarize_fn(combined, max_length=180, min_length=60)
                        else:
                            summary = combined
                        st.session_state[cache_key_sum] = summary
            except Exception:
                summary = "❗ Unable to generate a meaningful summary. The content may be too short or unstructured."

            st.info(f"📌 Summary for Slide {idx + 1}:\n\n{summary}")

            if summary and "Unable" not in summary:
                if st.button(f"🎧 Generate Voiceover for Summary of Slide {idx + 1}", key=f"summary_audio_btn_{idx}"):
                    try:
                        cache_key_sa = f"summary_audio_{idx}"
                        if cache_key_sa in st.session_state:
                            st.audio(st.session_state[cache_key_sa], format="audio/mp3")
                        else:
                            with st.spinner("Generating summary voiceover..."):
                                tts_summary = gTTS(text=summary, lang='en', slow=False)
                                buf2 = BytesIO()
                                tts_summary.write_to_fp(buf2)
                                summary_audio_bytes = buf2.getvalue()
                                st.session_state[cache_key_sa] = summary_audio_bytes
                                st.audio(summary_audio_bytes, format="audio/mp3")
                        st.success(f"✅ Voiceover for Summary of Slide {idx + 1} generated!")
                    except Exception as e:
                        st.error(f"❌ Error generating summary voiceover: {e}")
