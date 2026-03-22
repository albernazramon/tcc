import re
from typing import Optional
from src.domain.entities import QueryOptimizationRequest, QueryOptimizationResult
from src.domain.interfaces import IVectorRetriever, ILLMOptimizer

class OptimizeQueryUseCase:
    def __init__(self, retriever: IVectorRetriever, optimizer: ILLMOptimizer):
        self.retriever = retriever
        self.optimizer = optimizer

    def _extract_sql_query(self, markdown_text: str) -> Optional[str]:
        pattern_section = r"(?:2\.|#)\s*(?:CONSULTA OTIMIZADA|OPTIMIZED QUERY).*?```sql\n(.*?)\n```"
        match = re.search(pattern_section, markdown_text, re.DOTALL | re.IGNORECASE)
        
        if match:
            return match.group(1).strip()
        
        pattern_fallback = r"```sql\n(.*?)\n```"
        matches = re.findall(pattern_fallback, markdown_text, re.DOTALL | re.IGNORECASE)
        if matches:
            return matches[-1].strip()
            
        return None

    def execute(self, request: QueryOptimizationRequest) -> QueryOptimizationResult:
        context, references = self.retriever.retrieve_context(request.query)
        
        llm_response = self.optimizer.generate_optimization(
            query=request.query,
            schemas=request.schemas,
            context=context,
            additional_info=request.additional_info or ""
        )
        
        extracted_query = self._extract_sql_query(llm_response)
        
        return QueryOptimizationResult(
            original_query=request.query,
            optimized_query=extracted_query,
            optimization_explanation=llm_response,
            manual_references=references
        )
