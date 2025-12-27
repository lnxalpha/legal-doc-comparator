import streamlit as st
from legal_compare import compare_documents

def main():
    st.title("Legal Document Comparison Tool")
    st.markdown("""
    This app allows you to compare legal documents (PDF, DOCX, or images) to check for differences in content using semantic similarity.
    Upload two documents, and the system will compare their sentences for similarity.
    """)
    
    # Upload files
    uploaded_file_1 = st.file_uploader("Upload first document (PDF, DOCX, or image)", type=["pdf", "docx", "jpg", "jpeg", "png"])
    uploaded_file_2 = st.file_uploader("Upload second document (PDF, DOCX, or image)", type=["pdf", "docx", "jpg", "jpeg", "png"])
    
    if uploaded_file_1 and uploaded_file_2:
        st.write("Comparing documents...")
        result_html = compare_documents(uploaded_file_1, uploaded_file_2)
        st.markdown(result_html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
