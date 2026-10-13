import streamlit as st
import io
from document_processor import DocumentProcessor
from citation_extractor import CitationExtractor
from summarizer import Summarizer

# Page Configuration
st.set_page_config(
    page_title="AI Legal Document Summarizer & Citation Extractor",
    page_icon="⚖️",
    layout="wide"
)

# Custom CSS for a premium look
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 5px;
        height: 3em;
        background-color: #007bff;
        color: white;
        font-weight: bold;
    }
    .stButton>button:hover {
        background-color: #0056b3;
        border: none;
    }
    .reportview-container .main .block-container {
        padding-top: 2rem;
    }
    .citation-card {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #ffffff;
        border-left: 5px solid #007bff;
        margin-bottom: 1rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize Session State
if "summary" not in st.session_state:
    st.session_state.summary = ""
if "citations" not in st.session_state:
    st.session_state.citations = {}
if "processed" not in st.session_state:
    st.session_state.processed = False

# Sidebar
with st.sidebar:
    st.title("⚙️ Configuration")
    st.info("Upload a legal document (PDF, DOCX, or TXT) to get started.")
    
    uploaded_file = st.file_uploader("Choose a file", type=['pdf', 'docx', 'txt'])
    
    summary_length = st.selectbox(
        "Summary Length",
        options=["short", "medium", "long"],
        index=1,
        help="Select the detail level of the AI summary."
    )
    
    st.divider()
    st.markdown("### About")
    st.markdown("""
    This tool uses AI models (BART) and pattern matching to help legal professionals quickly parse complex documents.
    """)

# Main UI
st.title("⚖️ AI Legal Document Summarizer & Citation Extractor")

if uploaded_file is not None:
    # Action Button
    if st.button("🚀 Process Document"):
        with st.spinner("Processing document..."):
            try:
                # 1. Document Extraction
                processor = DocumentProcessor()
                file_bytes = uploaded_file.read()
                raw_text = processor.extract_text(file_bytes, uploaded_file.name)
                clean_text = processor.clean_text(raw_text)
                
                if not clean_text:
                    st.error("Could not extract any text from the document.")
                else:
                    # 2. Citation Extraction
                    with st.status("Extracting citations...", expanded=False):
                        extractor = CitationExtractor()
                        st.session_state.citations = extractor.extract_all(clean_text)
                    
                    # 3. AI Summarization
                    with st.status("Generating AI summary (this may take a moment)...", expanded=True):
                        summarizer = Summarizer()
                        st.session_state.summary = summarizer.summarize(clean_text, length_mode=summary_length)
                    
                    st.session_state.processed = True
                    st.success("Processing complete!")
                    
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                st.exception(e)

# Results Display
if st.session_state.processed:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📝 AI-Generated Summary")
        if st.session_state.summary:
            st.write(st.session_state.summary)
        else:
            st.warning("No summary was generated.")
            
    with col2:
        st.subheader("📚 Extracted Citations")
        cits = st.session_state.citations
        
        # Display as expanders or lists
        if any(cits.values()):
            for category, items in cits.items():
                if items:
                    with st.expander(f"{category.capitalize()} ({len(items)})"):
                        for item in items:
                            st.markdown(f"- {item}")
        else:
            st.info("No legal citations found.")

    # Export Functionality
    st.divider()
    col_dl_1, col_dl_2 = st.columns([1, 5])
    
    # Prepare download package
    export_text = f"SUMMARY ({summary_length.upper()})\n"
    export_text += "="*20 + "\n"
    export_text += st.session_state.summary + "\n\n"
    export_text += "EXTRACTED CITATIONS\n"
    export_text += "="*20 + "\n"
    for cat, items in st.session_state.citations.items():
        if items:
            export_text += f"\n{cat.upper()}:\n"
            for item in items:
                export_text += f"- {item}\n"

    with col_dl_1:
        st.download_button(
            label="💾 Download Results",
            data=export_text,
            file_name=f"legal_analysis_{uploaded_file.name.split('.')[0]}.txt",
            mime="text/plain"
        )

else:
    if uploaded_file is None:
        st.info("Please upload a document to begin.")
    else:
        st.info("Click 'Process Document' to generate analysis.")
