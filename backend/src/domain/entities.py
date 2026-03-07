from dataclasses import dataclass
from typing import Optional

@dataclass
class QueryOptimizationRequest:
    query: str
    schemas: str
    additional_info: Optional[str] = None

@dataclass
class QueryOptimizationResult:
    original_query: str
    optimized_query: Optional[str]
    optimization_explanation: str
