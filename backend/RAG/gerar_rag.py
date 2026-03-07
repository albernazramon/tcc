import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

EMBEDDING_MODEL = "nomic-embed-text"
POSTGRE_DOC_PATH = "postgresql_doc.pdf"
DEST = "./chroma_db"

def create_vectors():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(current_dir, POSTGRE_DOC_PATH)
    persist_dir = os.path.join(current_dir, DEST)

    print(f"Iniciando processamento do RAG...");

    if os.path.exists(persist_dir):
        print(f"Banco de vetores já existe em {persist_dir}. Carregando...")
        embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
        vectorstore = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
        return vectorstore

    if not os.path.exists(pdf_path):
        print(f"Erro: Arquivo PDF não encontrado em {pdf_path}")
        return None

    print(f"Carregando PDF: {pdf_path}")
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600, 
        chunk_overlap=120,
        separators=["\n\n", "\n", " ", ""]
    )
    splits = text_splitter.split_documents(docs)
    
    print(f"Criados {len(splits)} fragmentos de texto. Gerando embeddings...")
    
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    vectorstore = Chroma.from_documents(
        documents=splits, 
        embedding=embeddings, 
        persist_directory=persist_dir
    )
    
    print(f"RAG gerado com sucesso em {persist_dir}")
    return vectorstore

create_vectors()