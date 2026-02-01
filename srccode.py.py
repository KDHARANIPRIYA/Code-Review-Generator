import streamlit as st
import os
from fpdf import FPDF
from io import BytesIO
import tempfile
from langchain_community.llms import Ollama
from langchain.prompts import PromptTemplate
from datetime import datetime

# Initialize Ollama with Llama 3
llm = Ollama(model="llama3", base_url="http://localhost:11434")

# Streamlit app title and description
st.title("📝 Code Overview Generator")
st.markdown("""
Welcome to **CodeDoc Generator**! Upload a Python file and provide a prompt to generate a detailed document 
describing the code's inputs, outputs, and design. Powered by Llama 3 via Ollama.
""")

# File uploader for Python code
uploaded_file = st.file_uploader("Upload a Python file", type=["py"])

# User prompt input
prompt = st.text_area(
    "Enter your prompt (e.g., 'Generate a detailed document describing the inputs, outputs, and design of this code.')",
    value="Generate a detailed document describing the inputs, outputs, and design of the provided Python code."
)

# Function to read file content
def read_file_content(file):
    return file.read().decode("utf-8")

# Function to generate document using LLM
def generate_document(code, user_prompt):
    template = """
    You are an expert code analyst. Below is a Python code snippet and a user prompt. Follow the prompt to generate a detailed response in Markdown format.

    **User Prompt**: {prompt}
    
    **Python Code**:
    ```python
    {code}
    ```

    Ensure the response is well-structured, clear, and in Markdown format. Focus on describing the inputs, outputs, and design of the code as requested.
    """
    prompt_template = PromptTemplate(template=template, input_variables=["prompt", "code"])
    formatted_prompt = prompt_template.format(prompt=user_prompt, code=code)
    
    # Call LLM to generate response
    response = llm(formatted_prompt)
    return response

# Main logic
if uploaded_file is not None and prompt:
    # Read uploaded file
    code_content = read_file_content(uploaded_file)
    
    # Display uploaded code
    st.subheader("Uploaded Python Code")
    st.code(code_content, language="python")
    
    # Generate document
    with st.spinner("Generating document..."):
        document = generate_document(code_content, prompt)
    
    # Display generated document
    st.subheader("Generated Document")
    st.markdown(document)
    
    # Provide download button for the document
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"code_document_{timestamp}.pdf"
    
    # Convert the Markdown document to PDF using FPDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    # Add document content line by line
    for line in document.split('\n'):
        pdf.multi_cell(0, 10, line)

    # Create a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        pdf.output(tmp_file.name)
        tmp_file_path = tmp_file.name

    # Read back the file as binary
    with open(tmp_file_path, "rb") as f:
        pdf_data = f.read()

    # Download button for actual PDF
    st.download_button(
        label="Download as PDF",
        data=pdf_data,
        file_name=file_name,
        mime="application/pdf"
    )

else:
    st.info("Please upload a Python file and enter a prompt to generate the document.")