from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DB_PATH = os.path.join(BASE_DIR, "RAG", "chroma_db")

retriever = ChromaVectorRetriever(db_path=DB_PATH)
optimizer = OllamaLLMOptimizer()
use_case = OptimizeQueryUseCase(retriever=retriever, optimizer=optimizer)

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
    logger.info("="*50)
    logger.info(f"Nova requisição de otimização recebida.")
    logger.info(f"Tamanho da Consulta Original: {len(request.query)} caracteres")
    logger.info(f"Tamanho do Schema: {len(request.schema)} caracteres")
    if request.additional_info:
        logger.info(f"Informações Adicionais Fornecidas: {len(request.additional_info)} caracteres")
        
    start_time = time.time()
    
    try:
        domain_request = QueryOptimizationRequest(
            query=request.query,
            schemas=request.schema,
            additional_info=request.additional_info
        )
        
        logger.info("Iniciando processamento do UseCase de Otimização...")
        result = use_case.execute(domain_request)
        
        end_time = time.time()
        execution_time = round(end_time - start_time, 2)
        logger.info(f"Otimização concluída com sucesso em {execution_time} segundos.")
        
        has_optimized_query = bool(result.optimized_query and result.optimized_query.strip())
        logger.info(f"Consulta otimizada gerada: {'Sim' if has_optimized_query else 'Não'}")
        
        return APIResponse(
            original_query=result.original_query,
            optimized_query=result.optimized_query,
            insights=result.optimization_explanation
        )
    except Exception as e:
        end_time = time.time()
        logger.error(f"Erro durante a otimização da consulta: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "SQL Optimizer API (DDD) is running. Access /docs for documentation."}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
