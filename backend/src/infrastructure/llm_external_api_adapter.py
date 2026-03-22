from langchain_google_genai import ChatGoogleGenerativeAI
from src.domain.interfaces import ILLMOptimizer

class ExternalLLMOptimizer(ILLMOptimizer):
    def __init__(self, api_key: str, model_name: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model_name = model_name
        self.llm = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=api_key,
            temperature=0.2
        )

    def generate_optimization(self, query: str, schemas: str, context: str, additional_info: str) -> str:
        prompt_template = f"""
        ### PAPEL
        Você é um especialista em banco de dados PostgreSQL.
        Sua tarefa é transformar consultas lentas em consultas de alta performance.

        ### ENTRADAS
        1. CONSULTA ORIGINAL:
        {query}
        
        2. SCHEMAS DAS TABELAS:
        {schemas}

        3. CONTEXTO DO MANUAL (RAG):
        {context}

        4. INFORMAÇÕES ADICIONAIS:
        {additional_info}

        ### TAREFA
        Analise a consulta e forneça uma resposta estruturada em três partes:

        1. ANÁLISE DE PROBLEMAS:
           - Identifique por que a consulta original é lenta.
           - Cite conceitos como SARGability, tipos de Joins, ou custo de ordenação se aplicável.
           - Use as informações do MANUAL fornecidas para validar sua análise.

        2. CONSULTA OTIMIZADA:
           - Forneça APENAS o código SQL reescrito para máxima performance dentro do bloco de código.
           - NÃO inclua comentários de sugestão de índices dentro do bloco SQL.
           - Mantenha a semântica original dos dados.
           - Se houver necessidade de índices, mencione-os APENAS na seção 3 (EXPLICAÇÃO TÉCNICA).

        3. EXPLICAÇÃO TÉCNICA E PLANO DE EXECUÇÃO ESTIMADO:
           - Explique as mudanças feitas.
           - Descreva como o PostgreSQL provavelmente processará a nova consulta comparada à antiga, explicando também o impacto previsto (ex: "Mudança de Seq Scan para Index Scan").
           - Forneça recomendações de manutenção (VACUUM, ANALYZE).

        ### REGRAS CRÍTICAS
        - Responda em PORTUGUÊS. Todas as citações, referências e explicações baseadas no MANUAL (RAG) que estiverem em outros idiomas DEVEM ser traduzidas para o Português do Brasil de forma clara e técnica.
        - Seja extremamente técnico e preciso.
        - Se a consulta for ineficiente devido à estrutura (ex: falta de índices), forneça o comando `CREATE INDEX`.
        - Utilize o contexto do MANUAL sempre que possível para embasar sua decisão.
        """

        response = self.llm.invoke(prompt_template)
        return response.content.strip()