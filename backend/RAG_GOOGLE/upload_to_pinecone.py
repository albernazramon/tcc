import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

load_dotenv(dotenv_path="../.env")

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

def upload_rag_to_pinecone(pdf_path: str):
    if not os.path.exists(pdf_path):
        print(f"Erro: Arquivo PDF não encontrado em {pdf_path}")
        return

    print(f"Lendo PDF: {pdf_path}")
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        add_start_index=True
    )
    all_splits = text_splitter.split_documents(docs)
    print(f"PDF dividido em {len(all_splits)} trechos.")

    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=GOOGLE_API_KEY
    )
   
    pc = Pinecone(api_key=PINECONE_API_KEY)
    
    target_dimension = 3072
    
    if PINECONE_INDEX_NAME not in pc.list_indexes().names():
        print(f"Criando novo índice no Pinecone: {PINECONE_INDEX_NAME}")
        pc.create_index(
            name=PINECONE_INDEX_NAME,
            dimension=target_dimension,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
    else:
        index_info = pc.describe_index(PINECONE_INDEX_NAME)
        if index_info.dimension != target_dimension:
            print(f"AVISO: O índice '{PINECONE_INDEX_NAME}' tem dimensão {index_info.dimension}, mas o Google Gemini Embedding 001 gera {target_dimension}.")
            print(f"Por favor, delete o índice no painel do Pinecone e deixe o script criar um novo, ou crie manualmente com dimensão {target_dimension}.")

    print("Enviando vetores para o Pinecone (isso pode demorar alguns minutos)...")
    vectorstore = PineconeVectorStore.from_documents(
        documents=all_splits,
        embedding=embeddings,
        index_name=PINECONE_INDEX_NAME,
        pinecone_api_key=PINECONE_API_KEY
    )
    
    print("Upload concluído com sucesso!")

if __name__ == "__main__":
    pdf_path = os.path.join("..", "RAG", "postgresql_doc.pdf")
    upload_rag_to_pinecone(pdf_path)
