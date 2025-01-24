import streamlit as st
import fitz  # PyMuPDF
import re
import io

st.title("extractPGs")

# App description
st.markdown(""" This app allows you to:
1. Upload a PDF file
2. Search for text using either simple text or regular expressions
3. Choose case-sensitive or insensitive search
4. Extract all pages containing matches
5. Handle large PDFs efficiently 
""")

# Sidebar inputs
with st.sidebar:
    uploaded_file = st.file_uploader("Upload PDF", type="pdf")
    search_string = st.text_input("Search string")
    case_sensitive = st.checkbox("Case sensitive")
    use_regex = st.checkbox("Use regular expressions")
    process_btn = st.button("Process PDF")

def process_pdf():
    if not uploaded_file or not search_string:
        st.error("Please upload a PDF file and enter a search string")
        return

    try:
        # Open PDF from memory
        pdf_stream = io.BytesIO(uploaded_file.read())
        doc = fitz.open(stream=pdf_stream, filetype="pdf")
    except Exception as e:
        st.error(f"Error opening PDF: {e}")
        return

    # Prepare search parameters
    flags = re.IGNORECASE if not case_sensitive else 0
    if use_regex:
        try:
            pattern = re.compile(search_string, flags=flags)
        except re.error as e:
            st.error(f"Invalid regular expression: {e}")
            return

    # Search through pages
    matching_pages = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()
        
        # Update progress
        progress = (page_num + 1) / len(doc)
        progress_bar.progress(progress)
        status_text.text(f"Processing page {page_num+1} of {len(doc)}...")

        # Perform search
        if use_regex:
            if pattern.search(text):
                matching_pages.append(page_num)
        else:
            if case_sensitive:
                if search_string in text:
                    matching_pages.append(page_num)
            else:
                if search_string.lower() in text.lower():
                    matching_pages.append(page_num)

    progress_bar.empty()
    status_text.empty()

    if not matching_pages:
        st.warning("No matching pages found")
        return

    # Create new PDF with matching pages
    try:
        output_pdf = fitz.open()
        for page_num in matching_pages:
            output_pdf.insert_pdf(doc, from_page=page_num, to_page=page_num)
        
        # Save to bytes buffer
        pdf_bytes = output_pdf.write()
        output_pdf.close()
        doc.close()
    except Exception as e:
        st.error(f"Error creating output PDF: {e}")
        return

    # Show results and download button
    st.success(f"Found {len(matching_pages)} matching pages")
    st.download_button(
        label="Download Extracted Pages",
        data=pdf_bytes,
        file_name="extracted_pages.pdf",
        mime="application/pdf"
    )

if process_btn:
    process_pdf()