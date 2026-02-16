from langchain_chroma import Chroma
from langchain_community.embeddings import OllamaEmbeddings

EMBEDDING_MODEL = "nomic-embed-text"
DB_PATH = "./chroma_db"

def validate_db():
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)

    try:
        vector_db = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
    except Exception as e:
        print(f"ERRO ao ler o banco de dados. Detalhes: {e}")
        return

    qty_chunks = vector_db._collection.count()
    
    if qty_chunks == 0:
        print("ALERTA: Banco de dados encontrado, porém VAZIO (0 chunks).")
        return

    test_word = "The first variant of this command listed in the synopsis can change many of the role attributes that can" 
    print(f"🔎 Pesquisando por: '{test_word}'...")
    
    results = vector_db.similarity_search(test_word, k=2)

    if not results:
        print("FALHA: A busca não retornou nada.")
    else:
        print("Termo encontrado:\n")
        first_result = results[0]
        
        print(f">>> Página {first_result.metadata.get('page', '?')}")
        print(f">>> Conteúdo (primeiros 300 caracteres):")
        print(f"\"{first_result.page_content[:300]}...\"")        

if __name__ == "__main__":
    validate_db()