# Resultados e Discussões

Neste capítulo, são apresentados os resultados obtidos a partir dos experimentos realizados com a geração e otimização de consultas SQL utilizando Modelos de Linguagem de Grande Escala (LLMs), especificamente o modelo Gemma 3. Os testes foram estruturados para avaliar não apenas a capacidade do modelo em traduzir linguagem natural para SQL, mas também a eficácia de diferentes abordagens de otimização: Prompt simples e Recuperação Aumentada por Geração (RAG).

## Geração de Consultas em Linguagem Natural

As consultas foram geradas a partir de perguntas de diferentes níveis de complexidade, variando de agregações simples a junções (joins) complexas envolvendo múltiplas tabelas do esquema TPC-H. O arquivo `tcc/v1/geracao_de_consultas/CONSULTAS_GERADAS.md` documenta as seis consultas principais utilizadas como base para este estudo.

A Tabela 1 resume o desempenho e a precisão das consultas em três cenários: Original (sem otimização específica), Otimização via Prompt Simples e Otimização via RAG.

**Tabela 1: Comparativo de Desempenho e Alucinações**

| Cenário | Objetivo                   | Original (ms) | Otimiz. Prompt (ms) | Otimiz. RAG (ms) | Alucinação? (Original/Prompt/RAG) |
| :------ | :------------------------- | :------------ | :------------------ | :--------------- | :-------------------------------- |
| **Q1**  | Clientes por país          | 220           | 281                 | 229              | Não / Não / Sim (FK inexistente)  |
| **Q2**  | Top 5 clientes p/ valor    | 662           | 5061                | 680              | Sim / Não / Sim (Coluna inexist.) |
| **Q3**  | shipmode mais repetido     | 903           | 485                 | 395              | Não / Não / Não                   |
| **Q4**  | Clientes por país (LIMIT)  | 95            | 106                 | 182              | Sim / Não / Não                   |
| **Q5**  | Peças por região (HAVING)  | 276           | 50                  | N/A              | Não / Não / Não                   |
| **Q6**  | % Desconto (JOIN complexo) | 1195          | Erro                | 5876             | Sim / Erro / Sim (Campos extras)  |

## Análise do Desempenho e Otimizações

Os resultados demonstram que a intervenção da LLM na otimização de consultas apresenta um comportamento misto, dependendo da complexidade da tarefa e da estratégia adotada.

### O Papel dos Índices

A criação de índices sugerida pela LLM foi o fator de maior impacto positivo. Nas consultas **Q3** (ganho de ~55%) e **Q5** (redução de 276ms para 50ms), a recomendação correta de índices em colunas de filtro e agrupamento (`l_shipmode`, por exemplo) permitiu que o otimizador do PostgreSQL reduzisse drasticamente o custo de I/O.

No entanto, observou-se um risco significativo na indução de planos de execução subótimos. Na consulta **Q2**, o uso de índices sugeridos pelo Prompt simples levou o PostgreSQL a optar por um _Nested Loop Join_ em vez do _Hash Join_ original, resultando em uma degradação de performance de quase 8 vezes (de 662ms para 5061ms). Isso evidencia que a LLM, ao sugerir índices, pode "cegar" o otimizador para estratégias de varredura paralela mais eficientes em grandes volumes de dados.

### Alucinações e Validade do SQL

Um desafio persistente encontrado foi a ocorrência de "alucinações" — termos técnicos ou estruturas SQL que não existem no esquema ou no dialeto alvo (PostgreSQL).

- O **Prompt simples** falhou criticamente na **Q6**, gerando erro de sintaxe ao tentar usar a função `ROUND` com tipos de dados incompatíveis.
- O **RAG**, embora mais robusto na estrutura geral, alucinou chaves estrangeiras (FK) inexistentes na **Q1** e colunas na **Q2**, demonstrando que mesmo com o contexto do esquema injetado, o modelo ainda pode inferir relações baseadas em seu treinamento geral.

## Discussão sobre RAG vs Prompt Simples

A abordagem RAG mostrou-se superior na manutenção da estabilidade do plano de execução em consultas complexas, evitando as degradações extremas vistas no Prompt simples (como na Q2). No entanto, o RAG foi menos agressivo na sugestão de modificações estruturais de banco de dados (índices), o que resultou em ganhos menores em cenários onde um índice era a solução óbvia (Q5).

Conclui-se que, para resultados e discussões no âmbito deste TCC, a utilização de LLMs para otimização de consultas SQL é uma ferramenta poderosa para identificação de gargalos óbvios e sugestão de índices, mas exige uma validação humana rigorosa (Human-in-the-loop) para corrigir erros de sintaxe e evitar regressões de performance causadas por planos de execução ineficientes.
