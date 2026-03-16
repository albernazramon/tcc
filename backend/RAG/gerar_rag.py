import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

# Carrega variáveis de ambiente do arquivo .env (caso exista localmente)
load_dotenv()

EMBEDDING_MODEL = "models/gemini-embedding-2-preview"
POSTGRE_DOC_PATH = "postgresql_doc.pdf"
DEST = "./chroma_db"

def create_vectors():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    pdf_path = os.path.join(current_dir, POSTGRE_DOC_PATH)
    persist_dir = os.path.join(current_dir, DEST)

    print(f"Iniciando processamento do RAG...");

    if not os.environ.get("GOOGLE_API_KEY"):
        print("AVISO: Defina a GOOGLE_API_KEY para gerar os embeddings!")
        return None

    if os.path.exists(persist_dir):
        print(f"Banco de vetores já existe em {persist_dir}. Carregando...")
        embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
        vectorstore = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
        return vectorstore

    if not os.path.exists(pdf_path):
        print(f"Erro: Arquivo PDF não encontrado em {pdf_path}")
        return None

    print(f"Carregando PDF: {pdf_path}")
    loader = PyPDFLoader(pdf_path)
    
    docs = []
    print("Iniciando leitura das páginas...")
    for i, doc in enumerate(loader.lazy_load()):
        docs.append(doc)
        if (i + 1) % 100 == 0:
            print(f"Carregadas {i + 1} páginas...")
            
    print(f"PDF carregado com sucesso. Total de páginas: {len(docs)}. Iniciando divisão de texto...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=600, 
        chunk_overlap=120,
        separators=["\n\n", "\n", " ", ""]
    )
    splits = text_splitter.split_documents(docs)
    
    print(f"Criados {len(splits)} fragmentos de texto. Gerando embeddings...")
    
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
    vectorstore = Chroma(embedding_function=embeddings, persist_directory=persist_dir)
    
    import time
    batch_size = 100
    for i in range(0, len(splits), batch_size):
        batch = splits[i:i+batch_size]
        print(f"Adicionando documentos {i} a {i+len(batch)} de {len(splits)} ao banco de vetores...")
        try:
            vectorstore.add_documents(batch)
            time.sleep(1) # Pausa para evitar rate limit da API
        except Exception as e:
            print(f"Erro no lote {i}. Aguardando 10 segundos para tentar novamente. Erro: {e}")
            time.sleep(10)
            vectorstore.add_documents(batch)
            
    print(f"RAG gerado com sucesso em {persist_dir}")
    return vectorstore

create_vectors()