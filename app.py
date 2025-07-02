# app.py
import streamlit as st
import io
import base64
from core.pdf_processor import process_pdf_in_memory
from core.redaction_config import PII_PATTERNS

# --- Page Configuration ---
st.set_page_config(
    page_title="PDF Redaction Application",
    page_icon="📄",
    layout="wide"
)

# --- Session State Initialization ---
if 'redacted_file' not in st.session_state:
    st.session_state.redacted_file = None
if 'original_file' not in st.session_state:
    st.session_state.original_file = None
if 'file_name' not in st.session_state:
    st.session_state.file_name = None

# --- Helper function for Base64 encoding ---
def get_pdf_display_str(pdf_bytes: bytes) -> str:
    """Converts PDF bytes to a Base64 encoded string for display in an iframe."""
    return base64.b64encode(pdf_bytes).decode('utf-8')

# --- UI Layout ---
st.title("PDF Redaction Application")
st.markdown("""
This application demonstrates a secure, in-memory PDF redaction pipeline. 
Upload a single PDF or multiple files for bulk processing.
""")

# --- Sidebar for Controls ---
with st.sidebar:
    st.header("⚙️ Redaction Controls")
    
    uploaded_files = st.file_uploader(
        "Upload PDF Files",
        type="pdf",
        accept_multiple_files=True,
        help="You can upload one or more files for bulk processing."
    )

    st.subheader("1. Select Redaction Types")
    redaction_options = {key: st.checkbox(f"Redact {key}", value=True) for key in PII_PATTERNS.keys()}
    redaction_options["IMAGES"] = st.checkbox("Redact All Images/Logos", value=False)
    
    st.subheader("2. Page Range (Optional)")
    page_range_enabled = st.checkbox("Process a specific page range")
    page_range = (0, 0)
    if page_range_enabled:
        col1, col2 = st.columns(2)
        with col1:
            start_page = st.number_input("Start Page", min_value=1, value=1, step=1)
        with col2:
            end_page = st.number_input("End Page", min_value=1, value=1, step=1)
        page_range = (start_page, end_page) if start_page <= end_page else None
    else:
        page_range = None

    # Custom Text Input ---
    st.subheader("3. Custom Text Redaction")
    custom_text_to_redact = st.text_area(
        "Enter specific words or phrases to redact (one per line).",
        height=150,
        help="Example: Project Phoenix, a specific client name, etc. The search is case-sensitive."
    )

    process_button = st.button("Process Files", type="primary", use_container_width=True)

# --- Main Content Area ---
if process_button and uploaded_files:
    # --- Parse custom text from the text area ---
    custom_texts_list = [text.strip() for text in custom_text_to_redact.split('\n') if text.strip()]

    # --- Bulk Processing Dashboard ---
    if len(uploaded_files) > 1:
        st.header("Bulk Processing Dashboard")
        progress_bar = st.progress(0)
        results = []

        for i, uploaded_file in enumerate(uploaded_files):
            try:
                original_bytes = uploaded_file.getvalue()
                with st.spinner(f"Processing {uploaded_file.name}..."):
                    # --- PASS CUSTOM TEXT TO PROCESSOR ---
                    redacted_bytes = process_pdf_in_memory(
                        original_bytes, 
                        redaction_options, 
                        page_range, 
                        custom_texts=custom_texts_list
                    )
                
                download_data = get_pdf_display_str(redacted_bytes)
                results.append({
                    "File Name": uploaded_file.name,
                    "Status": "✅ Success",
                    "Download": f"data:application/pdf;base64,{download_data}",
                })

            except Exception as e:
                results.append({"File Name": uploaded_file.name, "Status": f"❌ Error: {e}", "Download": "N/A"})
            
            progress_bar.progress((i + 1) / len(uploaded_files))
        
        st.dataframe([{"File Name": r["File Name"], "Status": r["Status"]} for r in results], use_container_width=True)
        st.success("Bulk processing complete!")

    # --- Single File Processing View ---
    else:
        uploaded_file = uploaded_files[0]
        st.session_state.file_name = uploaded_file.name
        
        with st.spinner(f"Processing {st.session_state.file_name}... Please wait."):
            try:
                original_bytes = uploaded_file.getvalue()
                st.session_state.original_file = original_bytes
                
                # --- PASS CUSTOM TEXT TO PROCESSOR ---
                redacted_bytes = process_pdf_in_memory(
                    original_bytes, 
                    redaction_options, 
                    page_range, 
                    custom_texts=custom_texts_list
                )
                st.session_state.redacted_file = redacted_bytes
                st.success("Redaction Complete!")
            except Exception as e:
                st.error(f"An error occurred: {e}")
                st.session_state.redacted_file = None
                st.session_state.original_file = None

# --- Display Area for Single File Preview ---
if st.session_state.redacted_file and st.session_state.original_file:
    st.header("📄 Document Preview")
    
    st.download_button(
        label=f"⬇️ Download Redacted {st.session_state.file_name}",
        data=st.session_state.redacted_file,
        file_name=f"redacted_{st.session_state.file_name}",
        mime="application/pdf",
        use_container_width=True
    )

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Original Document")
        base64_pdf_orig = get_pdf_display_str(st.session_state.original_file)
        st.markdown(f'<iframe src="data:application/pdf;base64,{base64_pdf_orig}" width="100%" height="800px"></iframe>', unsafe_allow_html=True)

    with col2:
        st.subheader("Redacted Document")
        base64_pdf_redacted = get_pdf_display_str(st.session_state.redacted_file)
        st.markdown(f'<iframe src="data:application/pdf;base64,{base64_pdf_redacted}" width="100%" height="800px"></iframe>', unsafe_allow_html=True)
else:
    st.info("Upload a file and click 'Process Files' to see the results.")