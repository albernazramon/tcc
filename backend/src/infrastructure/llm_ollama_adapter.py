import ollama
from src.domain.interfaces import ILLMOptimizer

class OllamaLLMOptimizer(ILLMOptimizer):
    def __init__(self, model: str = "gemma3"):
        self.model = model

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
           - Forneça o código SQL reescrito para máxima performance.
           - Mantenha a semântica original dos dados.
           - Se necessário, sugira a criação de índices (comentados no código).

        3. EXPLICAÇÃO TÉCNICA E PLANO DE EXECUÇÃO ESTIMADO:
           - Explique as mudanças feitas.
           - Descreva como o PostgreSQL provavelmente processará a nova consulta comparada à antiga, explicando também o impacto previsto (ex: "Mudança de Seq Scan para Index Scan").
           - Forneça recomendações de manutenção (VACUUM, ANALYZE).

        ### REGRAS CRÍTICAS
        - Responda em PORTUGUÊS.
        - Seja extremamente técnico e preciso.
        - Se a consulta for ineficiente devido à estrutura (ex: falta de índices), forneça o comando `CREATE INDEX`.
        - Utilize o contexto do MANUAL sempre que possível para embasar sua decisão.
        """

        response = ollama.chat(
          model=self.model, 
          messages=[
            { 
              'role' : 'user',
              'content': prompt_template
            }
          ]
        )

        return response['message']['content'].strip()
