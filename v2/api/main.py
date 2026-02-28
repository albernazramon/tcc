from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import uvicorn
import re
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from tcc.v2.llm.optimizer import optimize_sql_and_generate_insights

app = FastAPI(
    title="SQL Optimizer API",
    description="API para otimização de consultas SQL baseada em RAG e LLM",
    version="1.0.0"
)

class OptimizeRequest(BaseModel):
    query: str = Field(..., description="A consulta SQL original a ser otimizada")
    schemas: str = Field(..., description="Os schemas das tabelas envolvidas")
    additional_info: Optional[str] = Field(None, description="Informações adicionais sobre o ambiente ou dados")

class OptimizeResponse(BaseModel):
    original_query: str
    optimized_query: Optional[str] = None
    optimized_result: str

def extract_sql_query(markdown_text: str) -> Optional[str]:
    pattern = r"```sql\n(.*?)\n```"
    match = re.search(pattern, markdown_text, re.DOTALL | re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None

@app.post("/optimize", response_model=OptimizeResponse)
async def optimize_query(request: OptimizeRequest):
    try:
        result = optimize_sql_and_generate_insights(
            request.query, 
            request.schemas, 
            request.additional_info or ""
        )
        
        extracted_query = extract_sql_query(result)
        
        return OptimizeResponse(
            original_query=request.query,
            optimized_query=extracted_query,
            optimized_result=result
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "SQL Optimizer API is running. Access /docs for documentation."}

uvicorn.run(app, host="127.0.0.1", port=8000)
