import re
import os
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from tcc.v2.src.domain.interfaces import IVectorRetriever

class ChromaVectorRetriever(IVectorRetriever):
    def __init__(self, db_path: str, embedding_model: str = "nomic-embed-text", k: int = 3):
        self.db_path = db_path
        self.embedding_model = embedding_model
        self.k = k

    def _analyze_query_patterns(self, query: str) -> list[str]:
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

    def retrieve_context(self, query: str) -> str:
        try:
            if not os.path.exists(self.db_path):
                return f"Aviso: Banco de dados RAG não inicializado em {self.db_path}."

            search_terms = self._analyze_query_patterns(query)
            embeddings = OllamaEmbeddings(model=self.embedding_model)
            vectorstore = Chroma(persist_directory=self.db_path, embedding_function=embeddings)
            
            all_results = []
            seen_content = set()
            
            for term in search_terms:
                results = vectorstore.similarity_search(term, k=self.k)
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
