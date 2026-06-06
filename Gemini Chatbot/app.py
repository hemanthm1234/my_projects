import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain.docstore.document import Document
from dotenv import load_dotenv
import google.generativeai as genai
import numpy as np
import json
import os
import faiss
import atexit
import shutil
import re
from weasyprint import HTML
import io
import markdown  # pip install markdown

load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
llm_model = os.getenv("LLM_model")

genai.configure(api_key=api_key)

TEMP_DIR = "faiss_index"
EMBEDDINGS_PATH = os.path.join(TEMP_DIR, "embeddings.npy")
DOCS_PATH = os.path.join(TEMP_DIR, "docs.json")

# Clean up on exit
def cleanup():
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)

atexit.register(cleanup)  # Will run on app exit

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        reader = PdfReader(pdf)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text
    return text

def get_text_chunks(text):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, length_function=len)
    return splitter.split_text(text)

def get_vectorstore(text_chunks):
    os.makedirs(TEMP_DIR, exist_ok=True)
    embeddings_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    docs = [Document(page_content=chunk, metadata={}) for chunk in text_chunks]

    # Save documents as JSON
    with open(DOCS_PATH, "w") as f:
        json.dump([{"text": doc.page_content, "metadata": doc.metadata} for doc in docs], f)

    # Compute embeddings
    vectors = embeddings_model.embed_documents([doc.page_content for doc in docs])
    np.save(EMBEDDINGS_PATH, np.array(vectors, dtype=np.float32))

def load_vectorstore():
    # Load docs
    with open(DOCS_PATH, "r") as f:
        docs_data = json.load(f)
    docs = [Document(page_content=d["text"], metadata=d["metadata"]) for d in docs_data]

    # Load embeddings
    vectors = np.load(EMBEDDINGS_PATH).astype("float32")

    # Build FAISS index
    index = faiss.IndexFlatL2(vectors.shape[1])
    index.add(vectors)

    return docs, index

def get_conversation_chain():
    prompt = PromptTemplate(
        template="""
        Answer the question as detailed as possible from the provided context.
        Make sure to provide all the details.
        If the answer is not available in the context, just say "Answer is not in the given context."
        Don't provide wrong answers.
        Add Emogis in your answer.

        Context: \n{context}\n
        Question: \n{question}\n
        Answer:
        """,
        input_variables=["context", "question"]
    )
    # Initialize the model for the Gemini free tier
    model = ChatGoogleGenerativeAI(model=llm_model, temperature=0.3)

    return load_qa_chain(model, chain_type="stuff", prompt=prompt)

def user_input(user_question):
    docs, index = load_vectorstore()
    embeddings_model = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    query_vector = np.array([embeddings_model.embed_query(user_question)], dtype="float32")

    _, indices = index.search(query_vector, k=5)
    matched_docs = [docs[i] for i in indices[0]]

    chain = get_conversation_chain()
    response = chain(
        {"input_documents": matched_docs, "question": user_question},
        return_only_outputs=True
    )

    return response["output_text"].strip()  # ✅ Just return the clean answer

# Initialize session state variables
if "is_indexed" not in st.session_state:
    st.session_state.is_indexed = False
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

import io
import re
from fpdf import FPDF

# Utility function to remove emojis
def remove_emojis(text):
    emoji_pattern = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F680-\U0001F6FF"  # transport & map symbols
        "\U0001F1E0-\U0001F1FF"  # flags
        "\U00002700-\U000027BF"  # Dingbats
        "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        "]+",
        flags=re.UNICODE,
    )
    return emoji_pattern.sub(r'', text)

def generate_chat_pdf(chat_history):
    html_content = """
    <html>
    <head>
        <style>
            @page { size: A4 landscape; margin: 1.7cm; }

            body {
                font-family: Arial, sans-serif;
                background-color: #ffffff;
                color: #111;
                margin: 0;
                padding: 0;
            }

            .main {
                padding: 30px;
            }

            h1 {
                text-align: center;
                margin-bottom: 30px;
                font-size: 28px;
                color: #D9751E;
            }

            .chat-entry {
                page-break-inside: avoid;
                margin-bottom: 20px;
            }

            .question {
                font-weight: bold;
                color: #2563eb;
                margin-bottom: 8px;
            }

            .answer {
                margin-left: 50px;
                padding: 10px;
                background: #f8f9fa;
                border-radius: 6px;
                border: 1px solid #ddd;
            }

            .question p, .answer p {
                display: inline;
                margin: 0;
            }

            .divider {
                border-top-width: 1px;
                border-top-style: solid;
                border-top-color: #4F4F4F;
                margin: 15px 0;
            }

            pre, code {
                font-family: "Courier New", monospace;
                background: #f0f0f0;
                padding: 2px 4px;
                border-radius: 4px;
            }

            pre {
                padding: 10px;
                overflow-x: auto;
            }
        </style>
    </head>
    <body>
        <div class="main">
            <h1>✨ Gemini Chatbot Conversation (❓➟✨➟📚➟📝 ) </h1>
    """

    for idx, (q, a) in enumerate(chat_history, 1):
        q_html = markdown.markdown(q)
        a_html = markdown.markdown(a)

        html_content += f"""
        <div class="chat-entry">
            <div class="question">🧑‍💻 &nbsp; {q_html}</div>
            <div class="answer">✨ &nbsp; {a_html}</div>
            <div class="divider"></div>
        </div>
        """

    html_content += """
        </div>
    </body>
    </html>
    """

    pdf_bytes = HTML(string=html_content).write_pdf()
    return io.BytesIO(pdf_bytes)

def main():
    st.set_page_config(page_title="📚 Gemini PDF Chatbot", page_icon="✨")
    st.header("Chat with Multiple PDFs using Gemini ✨")

    # ─── Sidebar ─────────────────────────────────────
    with st.sidebar:
        st.subheader("📂 Upload your PDFs")
        uploaded_pdfs = st.file_uploader("Choose PDF files", accept_multiple_files=True)

        if st.button("⏬ Submit and Process"):
            if uploaded_pdfs:
                with st.spinner("Processing..."):
                    raw_text = get_pdf_text(uploaded_pdfs)
                    chunks = get_text_chunks(raw_text)
                    get_vectorstore(chunks)
                    st.session_state.is_indexed = True
                    st.session_state.chat_history = []
                    st.success("✅ Documents processed and indexed!")
            else:
                st.warning("Please upload at least one PDF.")

    # ─── Chat Interface ─────────────────────────────
    if st.session_state.is_indexed:
        st.subheader("Ask questions about your PDFs (❓➟✨➟📚➟📝)")

        # Show history
        for q, a in st.session_state.chat_history:
            with st.chat_message("user", avatar="🧑‍💻"):
                st.markdown(q)
            with st.chat_message("assistant", avatar="✨"):
                st.markdown(a)

        # Input pinned at bottom
        question = st.chat_input("Ask a question...")
        if question:
            with st.chat_message("user", avatar="🧑‍💻"):
                st.markdown(question)

            answer = user_input(question)
            with st.chat_message("assistant", avatar="✨"):
                st.markdown(answer)

            st.session_state.chat_history.append((question, answer))

    else:
        st.info("⬅️ Upload documents to start chatting...")
    
    with st.sidebar:
        # 👇 Add the download button here
        if st.session_state.chat_history:
            pdf_bytes = generate_chat_pdf(st.session_state.chat_history)
            st.download_button(
                label="Download PDF 📥",
                data=pdf_bytes,
                file_name="chat_history.pdf",
                mime="application/pdf",
            )

if __name__ == "__main__":
    main()