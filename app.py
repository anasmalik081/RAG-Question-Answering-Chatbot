import streamlit as st
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains import create_retrieval_chain
from langchain.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFDirectoryLoader

# Loading Environments
load_dotenv()

# Loading the GROQ Model
model = init_chat_model("gemma2-9b-it", model_provider="groq")

# Prompt Template
prompt = ChatPromptTemplate.from_template(
    """
    Answer the questions based on the provided context only.
    Please provide the most accurate response based on the question
    <context>
    {context}
    </context>

    Question: {input}
    """
)

def create_vector_embeddings():
    if "vectors" not in st.session_state:
        st.session_state.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        st.session_state.loader = PyPDFDirectoryLoader("research_papers")
        st.session_state.docs = st.session_state.loader.load()
        st.session_state.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        st.session_state.final_documents = st.session_state.text_splitter.split_documents(st.session_state.docs)
        st.session_state.vectors = FAISS.from_documents(st.session_state.final_documents, st.session_state.embeddings)

# Title
st.title("RAG Document Q&A with GROQ and Gemma")

# Question
user_input = st.text_input("Enter your query from the research paper")

if st.button("Document Embedding"):
    create_vector_embeddings()
    st.write("Vector Database is ready")

if user_input:
    document_chain = create_stuff_documents_chain(model, prompt)
    retriever = st.session_state.vectors.as_retriever()
    chain = create_retrieval_chain(retriever, document_chain)
    response = chain.invoke({"input": user_input})
    st.write(response["answer"])

    # With streamlit expander
    with st.expander("Document Similarity Search"):
        for idx, doc in enumerate(response["context"]):
            st.write(doc.page_content)
            st.write("---------------------------------------------")