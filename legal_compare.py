import pytesseract
from PIL import Image
from PyPDF2 import PdfReader
import docx
import re
import nltk
from nltk.tokenize import sent_tokenize
from sentence_transformers import SentenceTransformer, util

nltk.download("punkt")

model = SentenceTransformer("all-MiniLM-L6-v2")

def extract_text_from_file(file):
    """Extract text from DOCX or PDF file."""
    if file.name.endswith(".pdf"):
        reader = PdfReader(file)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text
    elif file.name.endswith(".docx"):
        doc = docx.Document(file)
        text = ""
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    else:
        image = Image.open(file)
        return pytesseract.image_to_string(image)

def clean_and_tokenize(text):
    """Clean and tokenize text into sentences."""
    text = re.sub(r"\s+", " ", text)
    return sent_tokenize(text)

def compare_documents(file1, file2):
    """Compare two documents (PDF, DOCX, or image) and return the comparison results."""
    text1 = extract_text_from_file(file1)
    text2 = extract_text_from_file(file2)
    
    sents1 = clean_and_tokenize(text1)
    sents2 = clean_and_tokenize(text2)

    emb1 = model.encode(sents1, convert_to_tensor=True)
    emb2 = model.encode(sents2, convert_to_tensor=True)

    results = []
    for idx, sent2 in enumerate(sents2):
        sims = util.cos_sim(emb2[idx], emb1)[0]
        max_sim, best_idx = float(sims.max()), int(sims.argmax())
        ref_sent = sents1[best_idx]
        error_flag = max_sim < 0.85
        results.append((sent2, ref_sent, max_sim, error_flag))

    html = "<h3>Comparison Results</h3><table border='1' style='width:100%; border-collapse:collapse'>"
    html += "<tr><th>Target Sentence</th><th>Best Match in Reference</th><th>Similarity</th></tr>"
    for t, r, sim, err in results:
        row_style = " style='background-color:#fdd'" if err else ""
        html += f"<tr{row_style}><td>{t}</td><td>{r}</td><td>{sim:.2f}</td></tr>"
    html += "</table>"
    return html
