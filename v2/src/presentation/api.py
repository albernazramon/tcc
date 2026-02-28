from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import uvicorn
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))

from tcc.v2.src.domain.entities import QueryOptimizationRequest
from tcc.v2.src.application.optimize_query_use_case import OptimizeQueryUseCase
from tcc.v2.src.infrastructure.rag_chroma_adapter import ChromaVectorRetriever
from tcc.v2.src.infrastructure.llm_ollama_adapter import OllamaLLMOptimizer

app = FastAPI(
    title="SQL Optimizer API (DDD Version)",
    description="API para otimização de consultas SQL baseada em RAG e LLM com Arquitetura Hexagonal",
    version="2.0.0"
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "RAG", "chroma_db")

retriever = ChromaVectorRetriever(db_path=DB_PATH)
optimizer = OllamaLLMOptimizer()
use_case = OptimizeQueryUseCase(retriever=retriever, optimizer=optimizer)

class APIRequest(BaseModel):
    query: str = Field(..., description="A consulta SQL original a ser otimizada")
    schemas: str = Field(..., description="Os schemas das tabelas envolvidas")
    additional_info: Optional[str] = Field(None, description="Informações adicionais sobre o ambiente ou dados")

class APIResponse(BaseModel):
    original_query: str
    optimized_query: Optional[str] = None
    optimized_result: str

@app.post("/optimize", response_model=APIResponse)
async def optimize_query(request: APIRequest):
    try:
        domain_request = QueryOptimizationRequest(
            query=request.query,
            schemas=request.schemas,
            additional_info=request.additional_info
        )
        
        result = use_case.execute(domain_request)
        
        return APIResponse(
            original_query=result.original_query,
            optimized_query=result.optimized_query,
            optimized_result=result.optimization_explanation
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "SQL Optimizer API (DDD) is running. Access /docs for documentation."}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
