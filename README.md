#  AI Voiceover & Summarizer for Educational PDFs

A powerful and user-friendly **Streamlit** application that enhances educational content by converting lecture PDFs into **audio voiceovers** and **summarized text** using **Hugging Face Transformers** and **Google Text-to-Speech (gTTS)**.  
Perfect for students, educators, and e-learning platforms to improve accessibility and comprehension.

---

##  Demo UI:

(https://github.com/user-attachments/assets/9109092e-acf7-4e1e-aab0-02e5a3057f23)
(https://github.com/user-attachments/assets/305ad48e-6162-44c3-a12d-38b914d7622a)
(https://github.com/user-attachments/assets/6840460e-3ade-4aaf-9cb0-921ba6bfb384)


---

## 🚀 Features

✅ Upload educational PDFs (lecture notes, presentations)  
🎧 Generate natural-sounding **voiceovers** for each slide  
📄 Create concise **summaries** using state-of-the-art NLP  
🔊 Voiceover for **summarized text** as well  
🖼️ Slide-by-slide image rendering of PDF content  
🎯 Ideal for auditory learners and rapid content review

---

## 📂 How It Works

1. Upload a PDF containing your lecture or notes.
2. The app displays each slide with options to:
   - 🔊 Generate voiceover of full text
   - 🧠 Summarize the content
   - 🎧 Listen to the voiceover of the summary
3. Audio is generated on-the-fly and played within the app.

---

##  Tech Stack

| Tool            | Description                                |
|-----------------|--------------------------------------------|
| **Streamlit**   | UI/UX framework for web application        |
| **PyMuPDF**     | PDF text and image extraction              |
| **gTTS**        | Google Text-to-Speech for audio synthesis  |
| **Transformers**| Pretrained BART model for summarization    |
| **Python**      | Core backend logic                         |

---

## 🛠️ Installation

```bash
# Clone the repository
git clone https://github.com/your-username/ai-voiceover-summarizer.git
cd ai-voiceover-summarizer

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the application
streamlit run app.py

```

## Example Use Case:
  A student uploads a PDF of biology lecture slides.
  The app reads each slide aloud, summarizes it, and provides an audio version of the summary — enabling effective multitasking and improved retention during study sessions.

---
## Future Improvements:
  Multilingual voiceover support
  
  Export all audio files as ZIP
  
  Full document summary generator
  
  Save history and summaries

