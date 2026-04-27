# Resumo dos Cenários de Teste e Otimizações

Esta tabela apresenta um comparativo entre as consultas originais e os resultados obtidos após sugestões de otimização (via Prompt simples e RAG), destacando o ganho de desempenho e os desafios técnicos.

| Cenário | Objetivo                   | Original (ms) | Otimiz. Prompt (ms) | Otimiz. RAG (ms) | Alucinação? (Original/Prompt/RAG) | Observações e Pontos de Atenção                                                                             |
| :------ | :------------------------- | :------------ | :------------------ | :--------------- | :-------------------------------- | :---------------------------------------------------------------------------------------------------------- |
| **Q1**  | Clientes por país          | 220           | 281                 | 229              | Não / Não / Sim (FK inexistente)  | LLM indicou que a consulta já era otimizada; foco em índices.                                               |
| **Q2**  | Top 5 clientes p/ valor    | 662           | 5061                | 680              | Sim / Não / Sim (Coluna inexist.) | **Atenção:** Prompt teve queda brusca de performance (Nested Loop vs Hash Join). RAG manteve similar.       |
| **Q3**  | shipmode mais repetido     | 903           | 485                 | 395              | Não / Não / Não                   | Melhoria significativa (~55%) com a criação de índice em `l_shipmode`.                                      |
| **Q4**  | Clientes por país (LIMIT)  | 95            | 106                 | 182              | Sim / Não / Não                   | Diferenças pequenas; variação normal de execução ou overhead de plano.                                      |
| **Q5**  | Peças por região (HAVING)  | 276           | 50                  | N/A\*            | Não / Não / Não                   | Otimização drástica no Prompt via índices. RAG não gerou script de índices.                                 |
| **Q6**  | % Desconto (JOIN complexo) | 1195          | Erro\*\*            | 5876             | Sim / Erro / Sim (Campos extras)  | **Crítico:** Prompt gerou SQL inválido. RAG executou, mas com tempo superior (volume de dados processados). |

\* _Consulta não alterada no RAG devido à falta de scripts de índices._
\*\* _Erro de sintaxe (função ROUND) na sugestão do Prompt._

## Análise de Otimização e Principais Diferenças

- **Impacto dos Índices:** A criação de índices sugerida pelas LLMs foi o fator determinante para melhorias (ex: Q3 e Q5). No entanto, em consultas de grande volume (Q2), uma escolha errada de plano pelo PostgreSQL (Nested Loop sugerido/induzido por índices vs Hash Join original) pode degradar severamente a performance.
- **Qualidade do SQL Gerado:**
  - O **Prompt simples** tendeu a errar em funções específicas do PostgreSQL (ex: `ROUND` com tipos incompatíveis na Q6).
  - O **RAG** mostrou-se mais robusto na estrutura da consulta, embora tenha falhado em gerar scripts de índices em alguns casos (Q5).
- **Consistência dos Dados:** Consultas complexas (Q6) exigiram ajustes manuais nos filtros, pois as LLMs desconhecem a distribuição real dos valores, gerando filtros que retornavam zero registros ou eram excessivamente lentos.
- **Desempenho I/O:** Consultas que tocam `lineitem` continuam sendo os maiores gargalos, dependendo fortemente de índices de cobertura e paralelismo.
