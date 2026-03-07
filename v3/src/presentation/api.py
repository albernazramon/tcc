from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
import uvicorn
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))

from tcc.v3.src.domain.entities import QueryOptimizationRequest
from tcc.v3.src.application.optimize_query_use_case import OptimizeQueryUseCase
from tcc.v3.src.infrastructure.rag_chroma_adapter import ChromaVectorRetriever
from tcc.v3.src.infrastructure.llm_external_api_adapter import ExternalLLMOptimizer

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

class APIRequest(BaseModel):
    query: str = Field(..., description="A consulta SQL original a ser otimizada")
    schema: str = Field(..., alias="schema", description="Os schemas das tabelas envolvidas")
    additional_info: Optional[str] = Field(None, description="Informações adicionais sobre o ambiente ou dados")
    api_key: Optional[str] = Field(None, description="A chave da API externa (Google Gemini ou Llama-Groq) - Opcional se usar EnvVar")

class EvaluationResponse(BaseModel):
    is_valid: bool
    confidence_score: int = Field(..., ge=0, le=10)
    hallucination_issues: str

class APIResponse(BaseModel):
    original_query: str
    optimized_query: Optional[str] = None
    insights: str
    evaluation: Optional[EvaluationResponse] = None

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
        
    api_key = request.api_key or os.environ.get("GOOGLE_API_KEY")
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
        
        logger.info("Iniciando processamento do UseCase de Otimização (API Externa)...")
        result = use_case.execute(domain_request)
        
        end_time = time.time()
        execution_time = round(end_time - start_time, 2)
        logger.info(f"Otimização concluída com sucesso em {execution_time} segundos.")
        
        has_optimized_query = bool(result.optimized_query and result.optimized_query.strip())
        logger.info(f"Consulta otimizada gerada: {'Sim' if has_optimized_query else 'Não'}")

        evaluation = None
        if has_optimized_query:
            logger.info("Iniciando avaliação de qualidade e checagem de alucinações...")
            eval_start_time = time.time()
            try:
                from langchain_google_genai import ChatGoogleGenerativeAI
                eval_llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", google_api_key=api_key, temperature=0.1)
                
                eval_prompt = f"""Você é um analista de banco de dados e auditor de segurança focado em PostgreSQL.
Sua tarefa é avaliar uma consulta SQL otimizada com base APENAS no Schema Fornecido.
Verifique rigorosamente se a consulta otimizada faz referência a alguma tabela ou coluna que NÃO ESTEJA explicitamente definida no Schema.

Schema Fornecido:
{request.schema}

Consulta Original:
{request.query}

Consulta Otimizada:
{result.optimized_query}

Responda ESTRITAMENTE no seguinte formato JSON, sem mais nenhum texto adicional ou marcação markdown (Apenas o texto JSON puro):
{{
  "is_valid": true ou false,
  "confidence_score": numero de 0 a 10,
  "hallucination_issues": "Descreva em português quais tabelas/colunas inventadas foram utilizadas, ou 'Nenhuma alucinação detectada'"
}}
"""
                eval_response = eval_llm.invoke(eval_prompt)
                
                import json
                json_str = eval_response.content.strip()
                if json_str.startswith("```json"):
                    json_str = json_str[7:]
                elif json_str.startswith("```"):
                    json_str = json_str[3:]
                if json_str.endswith("```"):
                    json_str = json_str[:-3]
                json_str = json_str.strip()
                
                try:
                    eval_data = json.loads(json_str)
                    evaluation = EvaluationResponse(**eval_data)
                    logger.info(f"Avaliação concluída em {round(time.time() - eval_start_time, 2)}s.")
                    logger.info(f"Nota: {evaluation.confidence_score}/10 | Válida: {evaluation.is_valid}")
                except Exception as parse_e:
                    logger.warning(f"Falha ao interpretar resposta do avaliador. Raw: {json_str[:100]}... Error: {str(parse_e)}")
            except Exception as eval_e:
                logger.warning(f"Erro na etapa de avaliação, ignorando... Error: {str(eval_e)}")
        
        return APIResponse(
            original_query=result.original_query,
            optimized_query=result.optimized_query,
            insights=result.optimization_explanation,
            evaluation=evaluation
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
