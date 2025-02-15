import streamlit as st
import os
from PIL import Image
import io
import pdf2image
import base64
import fitz
import google.generativeai as genai

# Configure Gemini AI
genai.configure(api_key="AIzaSyCqq5SZhuK3YtvnH1joGUSmdTtqep7qK10")  # Replace with your API key

# Custom CSS to inject into the Streamlit app
custom_css = """
<style>
    .stButton > button {
        width: 100%;
        background-color: #4CAF50;
        color: white;
        padding: 10px 24px;
        border-radius: 8px;
        border: none;
        transition: background-color 0.3s;
    }
    .stButton > button:hover {
        background-color: #45a049;
    }
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .feature-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
</style>
"""

def get_gemini_response(input, pdf_content, prompt):
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content([input, pdf_content, prompt])
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"

def input_pdf_setup(uploaded_file):
    try:
        document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        text_parts = []
        
        # Extract text and metadata
        for page in document:
            text_parts.append(page.get_text())
            
        pdf_text_content = " ".join(text_parts)
        metadata = {
            "pages": len(document),
            "title": document.metadata.get("title", "Resume"),
            "author": document.metadata.get("author", 'author'),
        }
        return pdf_text_content, metadata
    except Exception as e:
        raise Exception(f"Error processing PDF: {str(e)}")

def main():
    st.set_page_config(
        page_title="Resume Analyzer",
        page_icon="📊",
        layout="wide"
    )
    
    # Inject custom CSS
    st.markdown(custom_css, unsafe_allow_html=True)
    
    # Main header
    st.markdown("""
        <div class="main-header">
            <h1>Resume Analyzer</h1>
            <p>Your Advanced Resume Analysis Tool</p>
        </div>
    """, unsafe_allow_html=True)

    # Create two columns for layout
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 📝 Job Description")
        input_text = st.text_area(
            "Enter the job description here:",
            height=150,
            key="input"
        )

    with col2:
        st.markdown("### 📄 Resume Upload")
        uploaded_file = st.file_uploader(
            "Upload your Resume (PDF)",
            type=["pdf"],
            help="Please upload a PDF file only"
        )

    # Display PDF metadata if file is uploaded
    if uploaded_file is not None:
        try:
            pdf_content, metadata = input_pdf_setup(uploaded_file)
            st.success("✅ PDF Uploaded Successfully!")
            
            # Display metadata in an expander
            with st.expander("📊 Document Information"):
                st.write(f"Pages: {metadata['pages']}")
                st.write(f"Title: {metadata['title']}")
                st.write(f"Author: {metadata['author']}")
        except Exception as e:
            st.error(f"Error: {str(e)}")
            return

        # Analysis Options in tabs
        st.markdown("### 🔍 Analysis Options")
        tabs = st.tabs([
            "Resume Review",
            "Skills Analysis",
            "Keyword Analysis",
            "Match Score",
            "Custom Query"
        ])

        # Define prompts
        prompts = {
            "review": """As an experienced Technical Human Resource Manager, provide a detailed evaluation of the resume against the job description. Focus on:
                        1. Overall alignment with the role
                        2. Key strengths and qualifications
                        3. Potential areas of concern
                        4. Professional presentation and formatting""",
            
            "skills": """As a Technical HR Manager specializing in data science, provide:
                        1. Detailed skills assessment
                        2. Specific recommendations for skill enhancement
                        3. Industry-relevant certifications to consider
                        4. Learning resources and development paths""",
            
            "keywords": """As an ATS expert, analyze:
                        1. Missing critical keywords
                        2. Keyword optimization suggestions
                        3. Industry-standard terminology
                        4. ATS-friendly formatting recommendations""",
            
            "match": """Provide a detailed match analysis:
                        1. Overall match percentage
                        2. Key matching criteria
                        3. Missing essential requirements
                        4. Recommendations for improving match score"""
        }

        # Tab 1: Resume Review
        with tabs[0]:
            if st.button("Analyze Resume", key="review"):
                with st.spinner("Analyzing resume..."):
                    response = get_gemini_response(prompts["review"], pdf_content, input_text)
                    st.markdown("### 📋 Analysis Results")
                    st.write(response)

        # Tab 2: Skills Analysis
        with tabs[1]:
            if st.button("Analyze Skills", key="skills"):
                with st.spinner("Analyzing skills..."):
                    response = get_gemini_response(prompts["skills"], pdf_content, input_text)
                    st.markdown("### 🎯 Skills Assessment")
                    st.write(response)

        # Tab 3: Keyword Analysis
        with tabs[2]:
            if st.button("Analyze Keywords", key="keywords"):
                with st.spinner("Analyzing keywords..."):
                    response = get_gemini_response(prompts["keywords"], pdf_content, input_text)
                    st.markdown("### 🔑 Keyword Analysis")
                    st.write(response)

        # Tab 4: Match Score
        with tabs[3]:
            if st.button("Calculate Match", key="match"):
                with st.spinner("Calculating match score..."):
                    response = get_gemini_response(prompts["match"], pdf_content, input_text)
                    st.markdown("### 📊 Match Analysis")
                    st.write(response)

        # Tab 5: Custom Query
        with tabs[4]:
            custom_query = st.text_area("Enter your custom query:", height=100)
            if st.button("Submit Query", key="custom"):
                if custom_query.strip():
                    with st.spinner("Processing query..."):
                        response = get_gemini_response(custom_query, pdf_content, input_text)
                        st.markdown("### 💡 Query Results")
                        st.write(response)
                else:
                    st.warning("Please enter a query first.")

    else:
        st.info("👆 Please upload a PDF resume to begin the analysis.")

    # Footer
    st.markdown("""
        ---
        <div style='text-align: center; color: #666;'>
            <p>JobFit Analyzer Pro - Making resume analysis smarter and more efficient</p>
        </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()