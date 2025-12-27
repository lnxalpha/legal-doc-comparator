# 🧾 Legal Document Comparator

This is a Streamlit app to compare scanned legal documents using OCR and semantic similarity models.

## Features

- Upload scanned legal documents (PDF or image)
- Extract text using OCR (Tesseract)
- Compare against reference documents
- Highlight differences using sentence similarity
- View results in an HTML-based side-by-side report

## Tech Stack

- Python
- Tesseract OCR via `pytesseract`
- Sentence Transformers (for semantic similarity)
- Streamlit (web interface)

## Setup

```bash
git clone https://github.com/YOUR_USERNAME/legal-doc-comparator.git
cd legal-doc-comparator
pip install -r requirements.txt
streamlit run app.py
