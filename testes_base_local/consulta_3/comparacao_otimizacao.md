# Comparação de Resultados: Consulta 3

## Queries Analisadas

### Pré-Otimização: Subconsulta correlacionada pesada

**Problema:** A subconsulta é executada para cada linha da tabela `part`, o que é extremamente ineficiente para grandes volumes. Deveria ser um JOIN com agregação. Além disso, o comando com o EXPLAIN ficou executando por mais de 15 horas e não foi possível obter uma resposta.

```sql
SELECT
    p.p_name,
    (SELECT SUM(l.l_quantity)
     FROM public.lineitem l
     WHERE l.l_partkey = p.p_partkey) as total_qty
FROM
    public.part p
WHERE
    p.p_size > 10;
```

### Pós-Otimização: Alteração de subconsulta para JOIN

**Alterações:** A consulta foi alterada para remover a subconsulta que estava sendo realizada para somar cada campo de quantidade para cada linha de public.part, agora utilizando um JOIN, o que melhora a eficiência da consulta. Também foram criados índices.

```sql
SELECT
    p.p_name,
    SUM(l.l_quantity) AS total_qty
FROM
    public.part p
JOIN
    public.lineitem l ON p.p_partkey = l.l_partkey
WHERE
    p.p_size > 10
GROUP BY
    p.p_partkey, p.p_name;
```

---

## Comparação de Desempenho

A otimização foi drástica, considerando que antes da criação de índices e da alteração da consulta, não foi possível executar o cenário original mesmo com horas de execução.

| Métrica                    | Pré-Otimização | Pós-Otimização | Diferença / Impacto |
| :------------------------- | :------------- | :------------- | :------------------ |
| **Tempo de Execução**      | X              | 1,853.337 ms   | Excelente           |
| **Custo Inicial Estimado** | X              | 13,683,436.73  |                     |
| **Custo Total Estimado**   | X              | 13,689,480.38  |                     |
| **Linhas**                 | X              | 19,653         |                     |
| **Memória: Hit**           | X              | 12,158         |                     |
| **Memória: Read**          | X              | 75,792         |                     |
| **Memória: Dirtied**       | X              | -              | Sem memória suja    |
| **Memória: Written**       | X              | -              | Sem memória escrita |
| **Temp Read**              | X              | 21,760         |                     |
| **Temp Written**           | X              | 35,820         |                     |

### Resultados da Consulta (Registros)

- **Pré-Otimização:** [resultado_pre_otimizacao](.\resultado_pre_otimizacao.csv)
- **Pós-Otimização:** [resultado_pos_otimizacao](.\resultado_pos_otimizacao.csv)
  \_()
