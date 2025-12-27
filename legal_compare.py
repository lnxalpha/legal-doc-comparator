import re
import io
import os
import pytesseract
from PIL import Image
from PyPDF2 import PdfReader
from pdf2image import convert_from_bytes
import docx
import nltk
from nltk.tokenize import sent_tokenize
from sentence_transformers import SentenceTransformer, util

import shutil
print("Tesseract:", shutil.which("tesseract"))
print("Poppler:", shutil.which("pdftoppm"))

# ---------- Initialization ----------
# Set NLTK data path first
nltk_data_path = os.path.join(os.getcwd(), "nltk_data")
os.makedirs(nltk_data_path, exist_ok=True)
nltk.data.path.insert(0, nltk_data_path)

# Download both punkt and punkt_tab for compatibility
for resource in ["punkt", "punkt_tab"]:
    try:
        nltk.data.find(f"tokenizers/{resource}")
    except LookupError:
        print(f"Downloading {resource}...")
        nltk.download(resource, download_dir=nltk_data_path)

# Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


# ---------- Helper Functions ----------
def extract_text_from_file(file):
    """Extract text from PDF, DOCX, or image files."""
    filename = file.name.lower()

    # ---------- PDF ----------
    if filename.endswith(".pdf"):
        file_bytes = file.read()
        pdf_stream = io.BytesIO(file_bytes)

        # 1️⃣ Try text-based extraction
        reader = PdfReader(pdf_stream)
        text = ""

        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"

        if text.strip():
            return text  # ✅ text-based PDF

        # 2️⃣ Fallback: scanned PDF → OCR
        images = convert_from_bytes(file_bytes)
        ocr_text = ""

        for img in images:
            ocr_text += pytesseract.image_to_string(img) + "\n"

        return ocr_text

    # ---------- DOCX ----------
    elif filename.endswith(".docx"):
        doc = docx.Document(file)
        return "\n".join(p.text for p in doc.paragraphs)

    # ---------- IMAGE ----------
    else:
        image = Image.open(file)
        return pytesseract.image_to_string(image)

def clean_and_tokenize(text):
    """Clean text and split into sentences."""
    text = re.sub(r"\s+", " ", text)
    return sent_tokenize(text)


# ---------- Core Comparison Function ----------
def compare_documents(file1, file2):
    """
    Compare two documents and return HTML of semantic similarity results.
    Supports PDF, DOCX, and images.
    """
    text1 = extract_text_from_file(file1)
    text2 = extract_text_from_file(file2)

    sents1 = clean_and_tokenize(text1)
    sents2 = clean_and_tokenize(text2)

    # Safety check: ensure documents have text
    if not sents1 or not sents2:
        return "<p><b>Error:</b> One or both documents contain no readable text.</p>"

    # Encode sentences
    emb1 = model.encode(sents1, convert_to_tensor=True)
    emb2 = model.encode(sents2, convert_to_tensor=True)

    # Compare sentences
    results = []
    for idx, sent2 in enumerate(sents2):
        sims = util.cos_sim(emb2[idx], emb1)[0]
        max_sim, best_idx = float(sims.max()), int(sims.argmax())
        ref_sent = sents1[best_idx]
        error_flag = max_sim < 0.85
        results.append((sent2, ref_sent, max_sim, error_flag))

    # Generate HTML table
    html = "<h3>Comparison Results</h3>"
    html += "<table border='1' style='width:100%; border-collapse:collapse'>"
    html += "<tr><th>Target Sentence</th><th>Best Match in Reference</th><th>Similarity</th></tr>"

    for target, ref, sim, err in results:
        row_style = " style='background-color:#fdd'" if err else ""
        html += f"<tr{row_style}><td>{target}</td><td>{ref}</td><td>{sim:.2f}</td></tr>"

    html += "</table>"
    return html


# ---------- Example Streamlit Usage ----------
if __name__ == "__main__":
    import streamlit as st

    st.title("Legal Document Comparator")

    uploaded_file_1 = st.file_uploader("Upload Reference Document", type=["pdf", "docx", "png", "jpg", "jpeg"])
    uploaded_file_2 = st.file_uploader("Upload Target Document", type=["pdf", "docx", "png", "jpg", "jpeg"])

    if uploaded_file_1 and uploaded_file_2:
        st.info("Processing, please wait...")
        result_html = compare_documents(uploaded_file_1, uploaded_file_2)
        st.markdown(result_html, unsafe_allow_html=True)
