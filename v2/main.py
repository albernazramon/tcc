import ollama
import re
import os
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

EMBEDDING_MODEL = "nomic-embed-text"
LLM_MODEL = "gemma3"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "RAG/chroma_db")

def analyze_query_patterns(query):
    query_upper = query.upper()
    search_terms = []
    
    patterns = {
        r'\bJOIN\b': ["JOIN optimization query planning", "Nested Loop vs Hash Join", "Join order performance"],
        r'\(SELECT': ["Subquery vs JOIN optimization", "Correlated subquery performance"],
        r'GROUP BY': ["GROUP BY aggregation index", "HashAggregate vs GroupAggregate"],
        r'ORDER BY': ["ORDER BY sorting index performance", "Incremental sort"],
        r'DISTINCT': ["DISTINCT performance optimization", "Unique index"],
        r'LIKE': ["LIKE pattern matching index", "GIN index trgm", "Full text search"],
        r'UNION\b': ["UNION vs UNION ALL performance"],
        r'WHERE': ["WHERE clause indexing", "Index Scan vs Seq Scan"],
        r'UPPER\(|LOWER\(': ["Function based index", "SARGability SQL"],
        r'OR': ["OR clause index performance", "Bitmap Index Scan"]
    }
    
    for pattern, terms in patterns.items():
        if re.search(pattern, query_upper):
            search_terms.extend(terms)
    
    if not search_terms:
        search_terms.append("PostgreSQL query optimization execution plan")
    
    return list(set(search_terms))

def retrieve_rag_context(query, k=2):
    try:
        if not os.path.exists(DB_PATH):
            return "Aviso: Banco de dados RAG não inicializado."

        search_terms = analyze_query_patterns(query)
        embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
        vectorstore = Chroma(persist_directory=DB_PATH, embedding_function=embeddings)
        
        all_results = []
        seen_content = set()
        
        for term in search_terms:
            results = vectorstore.similarity_search(term, k=k)
            for doc in results:
                content_hash = doc.page_content[:100]
                if content_hash not in seen_content:
                    all_results.append(doc)
                    seen_content.add(content_hash)
        
        if not all_results:
            return "Nenhum contexto relevante encontrado no RAG."
        
        context = "### CONTEXTO DO MANUAL POSTGRESQL\n"
        for i, doc in enumerate(all_results):
            page = doc.metadata.get('page', '?')
            context += f"\n--- Trecho {i+1} (Manual pág. {page}) ---\n{doc.page_content.strip()}\n"
        
        return context
    
    except Exception as e:
        print(f"Erro ao acessar RAG: {e}")
        return "Erro ao recuperar contexto do RAG."

def optimize_sql_and_generate_insights(query, schemas, additional_info):
    rag_context = retrieve_rag_context(query, k=3)
    
    prompt_template = f"""
    ### PAPEL
    Você é um especialista em banco de dados PostgreSQL.
    Sua tarefa é transformar consultas lentas em consultas de alta performance.

    ### ENTRADAS
    1. CONSULTA ORIGINAL:
    {query}
    
    2. SCHEMAS DAS TABELAS:
    {schemas}

    3. CONTEXTO DO MANUAL (RAG):
    {rag_context}

    4. INFORMAÇÕES ADICIONAIS:
    {additional_info}

    ### TAREFA
    Analise a consulta e forneça uma resposta estruturada em três partes:

    1. ANÁLISE DE PROBLEMAS:
       - Identifique por que a consulta original é lenta.
       - Cite conceitos como SARGability, tipos de Joins, ou custo de ordenação se aplicável.
       - Use as informações do MANUAL fornecidas para validar sua análise.

    2. CONSULTA OTIMIZADA:
       - Forneça o código SQL reescrito para máxima performance.
       - Mantenha a semântica original dos dados.
       - Se necessário, sugira a criação de índices (comentados no código).

    3. EXPLICAÇÃO TÉCNICA E PLANO DE EXECUÇÃO ESTIMADO:
       - Explique as mudanças feitas.
       - Descreva como o PostgreSQL provavelmente processará a nova consulta comparada à antiga, explicando também o impacto previsto (ex: "Mudança de Seq Scan para Index Scan").
       - Forneça recomendações de manutenção (VACUUM, ANALYZE).

    ### REGRAS CRÍTICAS
    - Responda em PORTUGUÊS.
    - Seja extremamente técnico e preciso.
    - Se a consulta for ineficiente devido à estrutura (ex: falta de índices), forneça o comando `CREATE INDEX`.
    - Utilize o contexto do MANUAL sempre que possível para embasar sua decisão.
    """

    response = ollama.chat(
      model=LLM_MODEL, 
      messages=[
        { 
          'role' : 'user',
          'content': prompt_template
        }
      ]
    )

    return response['message']['content'].strip()

# Testes #
query = """

"""

schemas = """

"""

additional_info = """

"""


result = optimize_sql_and_generate_insights(query, schemas, additional_info)
print(result)
