import re
import os
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from src.domain.interfaces import IVectorRetriever

class PineconeVectorRetriever(IVectorRetriever):
    def __init__(self, index_name: str, google_api_key: str, pinecone_api_key: str, k: int = 3):
        self.index_name = index_name
        self.k = k
        
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=google_api_key
        )
        
        self.vectorstore = PineconeVectorStore(
            index_name=self.index_name,
            embedding=self.embeddings,
            pinecone_api_key=pinecone_api_key
        )

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

    def retrieve_context(self, query: str) -> tuple[str, list[dict]]:
        try:
            search_terms = self._analyze_query_patterns(query)
            
            all_results = []
            seen_content = set()
            
            print(f"Buscando contexto no Pinecone para os termos: {search_terms}")
            
            for term in search_terms:
                results = self.vectorstore.similarity_search(term, k=self.k)
                for doc in results:
                    content_hash = doc.page_content[:100]
                    if content_hash not in seen_content:
                        all_results.append(doc)
                        seen_content.add(content_hash)
            
            print(f"RAG (Pinecone): {len(all_results)} trechos relevantes encontrados.")
            
            references = []
            if not all_results:
                return "Nenhum contexto relevante encontrado no RAG.", []
            
            context = "### CONTEXTO DO MANUAL POSTGRESQL\n"
            for i, doc in enumerate(all_results):
                page = doc.metadata.get('page', '?')
                context += f"\n--- Trecho {i+1} (Manual pág. {page}) ---\n{doc.page_content.strip()}\n"
                references.append({
                    "id": i + 1,
                    "page": page,
                    "content": doc.page_content.strip()
                })
            
            return context, references
        
        except Exception as e:
            print(f"Erro ao acessar RAG no Pinecone: {e}")
            raise ConnectionError(f"Erro ao recuperar contexto do RAG Cloud: {str(e)}")
