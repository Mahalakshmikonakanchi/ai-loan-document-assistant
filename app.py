import streamlit as st
import os
from dotenv import load_dotenv
from pypdf import PdfReader
import google.generativeai as genai

# Page setup
st.set_page_config(page_title="AI Loan Assistant", layout="wide")

# Load Gemini API key
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("models/gemini-2.5-flash")

st.markdown("""
# 🏦 AI Loan Document Assistant
Analyze borrower documents, identify risks, find missing documents, and generate underwriting-style summaries.
""")

st.markdown("### 📄 Upload Loan Document")
uploaded_file = st.file_uploader("", type="pdf")


def extract_text(pdf):
    reader = PdfReader(pdf)
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


if uploaded_file:
    text = extract_text(uploaded_file)

    if not text.strip():
        st.error("Could not extract text from this PDF. Please upload a text-based PDF.")
    else:
        st.success("✅ Document uploaded and processed successfully")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("### 💬 Ask a Question")
            question = st.text_input(
                "Example: What are the key risks in this loan file?"
            )

            if question:
                prompt = f"""
                You are an AI loan document assistant.

                Analyze the document carefully and answer the user's question.
                If the document does not contain enough information, clearly say what is missing.

                Document:
                {text[:6000]}

                Question:
                {question}
                """

                response = model.generate_content(prompt)

                st.markdown("### 🤖 Answer")
                st.write(response.text)

        with col2:
            st.markdown("### 📋 Quick Actions")

            if st.button("Generate Loan Summary"):
                summary_prompt = f"""
                You are an underwriting assistant.

                Summarize this loan document in a clear, professional format.

                Include:
                - Borrower information
                - Loan type and loan amount
                - Income details
                - Credit score
                - Debt-to-income ratio
                - Key risks
                - Missing documents
                - Overall review recommendation

                Document:
                {text[:6000]}
                """

                response = model.generate_content(summary_prompt)

                st.markdown("### 🧾 Loan Summary")
                st.write(response.text)

            if st.button("Extract Structured Data"):
                extract_prompt = f"""
                Extract structured loan data from this document.

                Return ONLY valid JSON with these fields:
                {{
                  "borrower_name": "",
                  "loan_type": "",
                  "loan_amount": "",
                  "annual_income": "",
                  "credit_score": "",
                  "debt_to_income_ratio": "",
                  "employment_status": "",
                  "provided_documents": [],
                  "missing_documents": [],
                  "risks": [],
                  "recommendation": ""
                }}

                Document:
                {text[:6000]}
                """

                response = model.generate_content(extract_prompt)

                st.markdown("### 📊 Structured Loan Data")
                st.code(response.text, language="json")

            if st.button("Identify Missing Documents"):
                missing_prompt = f"""
                Review this loan document and identify missing documents needed for underwriting.

                Return:
                - Missing document name
                - Why it is needed
                - Priority: High, Medium, or Low

                Document:
                {text[:6000]}
                """

                response = model.generate_content(missing_prompt)

                st.markdown("### 🚨 Missing Documents")
                st.write(response.text)

        st.markdown("---")
        st.markdown("### 📌 Document Preview")
        st.text_area("Extracted PDF Text", text[:3000], height=250)
else:
    st.info("Upload a loan PDF to begin.")