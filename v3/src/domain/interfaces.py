from abc import ABC, abstractmethod

class IVectorRetriever(ABC):
    @abstractmethod
    def retrieve_context(self, query: str) -> str:
        pass

class ILLMOptimizer(ABC):
    @abstractmethod
    def generate_optimization(self, query: str, schemas: str, context: str, additional_info: str) -> str:
        pass
