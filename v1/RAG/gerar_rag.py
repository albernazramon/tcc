import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

EMBEDDING_MODEL = "nomic-embed-text"
POSTGRE_DOC_PATH = "postgresql_doc.pdf"
DEST = "./chroma_db"

def create_vectors():
    if os.path.exists(DEST):        
        embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
        vectorstore = Chroma(persist_directory=DEST, embedding_function=embeddings)
        return vectorstore

    loader = PyPDFLoader(POSTGRE_DOC_PATH)
    docs = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200
    )
    splits = text_splitter.split_documents(docs)
    
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings, persist_directory=DEST)
    return vectorstore

create_vectors()