# Comparação de Resultados: Consulta 2

## Queries Analisadas

### Pré-Otimização: Uso de funções em colunas no WHERE (SARGability)

**Problema:** O uso de `UPPER()` na coluna `c_name` impede o uso de índices B-tree padrão, resultando em um Full Table Scan na tabela `customer`.

```sql
SELECT
    c_name,
    c_acctbal
FROM
    public.customer
WHERE
    UPPER(c_name) LIKE 'CUSTOMER#000000001%';
```

### Pós-Otimização: TODO

**Alterações:** TODO

```sql

```

---

## Comparação de Desempenho

| Métrica                    | Pré-Otimização | Pós-Otimização | Diferença / Impacto |
| :------------------------- | :------------- | :------------- | :------------------ |
| **Tempo de Execução**      | 89.930 ms      |                |                     |
| **Custo Inicial Estimado** | 0.00           |                |                     |
| **Custo Total Estimado**   | 4066.40        |                |                     |
| **Memória: Hit**           | -              |                |                     |
| **Memória: Read**          | 3536           |                |                     |
| **Memória: Dirtied**       | 3518           |                |                     |
| **Memória: Written**       | -              |                |                     |
| **Temp Read**              | -              |                |                     |
| **Temp Written**           | -              |                |                     |

### Resultados da Consulta (Registros)

- **Pré-Otimização:** [resultado_pre_otimizacao](.\resultado_pre_otimizacao.csv)
- **Pós-Otimização:** [resultado_pos_otimizacao](.\resultado_pos_otimizacao.csv)
  _(Os resultados apresentam a mesma quantidade de linhas, porém os dados não estão ordenados da mesma forma que no resultado da consulta original, devido à mudança de plano de execução com o `UNION ALL`.)_
