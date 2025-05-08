import streamlit as st
from legal_compare import compare_documents

st.set_page_config(page_title="Legal Document Comparator", layout="wide")

st.title("📄 Legal Document Comparator")
st.markdown("Upload two scanned legal documents for OCR, semantic comparison, and similarity analysis.")

uploaded_file1 = st.file_uploader("Upload Reference Document", type=["png", "jpg", "jpeg", "pdf"], key="ref")
uploaded_file2 = st.file_uploader("Upload Target Document", type=["png", "jpg", "jpeg", "pdf"], key="target")

if uploaded_file1 and uploaded_file2:
    with st.spinner("Processing..."):
        result_html = compare_documents(uploaded_file1, uploaded_file2)
        st.markdown(result_html, unsafe_allow_html=True)