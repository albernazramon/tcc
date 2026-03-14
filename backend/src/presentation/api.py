from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import uvicorn
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))

from src.domain.entities import QueryOptimizationRequest
from src.application.optimize_query_use_case import OptimizeQueryUseCase
from src.infrastructure.rag_chroma_adapter import ChromaVectorRetriever
from src.infrastructure.llm_external_api_adapter import ExternalLLMOptimizer

app = FastAPI(
    title="SQL Optimizer API (DDD Version)",
    description="API para otimização de consultas SQL baseada em RAG e LLM com Arquitetura Hexagonal",
    version="2.0.0"
)

allowed_origins_str = os.environ.get("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000,*")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(",") if origin.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "RAG", "chroma_db")

retriever = ChromaVectorRetriever(db_path=DB_PATH)

class APIRequest(BaseModel):
    query: str = Field(..., description="A consulta SQL original a ser otimizada")
    schema: str = Field(..., alias="schema", description="Os schemas das tabelas envolvidas")
    additional_info: Optional[str] = Field(None, description="Informações adicionais sobre o ambiente ou dados")

class APIResponse(BaseModel):
    original_query: str
    optimized_query: Optional[str] = None
    insights: str

import logging
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("api_execution.log", encoding="utf-8")
    ]
)
logger = logging.getLogger("SQLOptimizerAPI")

@app.post("/optimize", response_model=APIResponse)
async def optimize_query(request: APIRequest):
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=400, detail="API Key do Google Gemini é necessária. Forneça no payload ou defina a variável de ambiente GOOGLE_API_KEY.")

    start_time = time.time()
    
    try:
        domain_request = QueryOptimizationRequest(
            query=request.query,
            schemas=request.schema,
            additional_info=request.additional_info
        )
        
        optimizer = ExternalLLMOptimizer(api_key=api_key)
        use_case = OptimizeQueryUseCase(retriever=retriever, optimizer=optimizer)
        
        result = use_case.execute(domain_request)
        
        end_time = time.time()
        execution_time = round(end_time - start_time, 2)
        has_optimized_query = bool(result.optimized_query and result.optimized_query.strip())

        return APIResponse(
            original_query=result.original_query,
            optimized_query=result.optimized_query,
            insights=result.optimization_explanation
        )
    except Exception as e:
        end_time = time.time()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "SQL Optimizer API (DDD) is running. Access /docs for documentation."}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
