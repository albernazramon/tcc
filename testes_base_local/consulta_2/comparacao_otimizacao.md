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

### Pós-Otimização: Criação de índices

**Alterações:** O modelo manteve a consulta sintaticamente intacta, porém indicou a criação dos seguintes índices para tornar a função UPPER(c_name) sargeável.

```sql
CREATE INDEX idx_customer_c_name_upper ON public.customer (UPPER(c_name) varchar_pattern_ops);
```

---

## Comparação de Desempenho

| Métrica                    | Pré-Otimização | Pós-Otimização | Diferença / Impacto   |
| :------------------------- | :------------- | :------------- | :-------------------- |
| **Tempo de Execução**      | 89.930 ms      | 0.759 ms       | Redução drástica      |
| **Custo Inicial Estimado** | 0.00           | 24.11          | Aumento baixo         |
| **Custo Total Estimado**   | 4,066.40       | 1,858.73       | Redução impactante    |
| **Linhas**                 | 177            | 750            | Aumento significativo |
| **Memória: Hit**           | -              | 1              | -                     |
| **Memória: Read**          | 3,536          | 3              | Redução drástica      |
| **Memória: Dirtied**       | 3,518          | -              | Nenhuma memória suja  |
| **Memória: Written**       | -              | -              | -                     |
| **Temp Read**              | -              | -              | -                     |
| **Temp Written**           | -              | -              | -                     |

### Resultados da Consulta (Registros)

- **Pré-Otimização:** [resultado_pre_otimizacao](.\resultado_pre_otimizacao.csv)
- **Pós-Otimização:** [resultado_pos_otimizacao](.\resultado_pos_otimizacao.csv)
  \_(Os resultados apresentam os mesmos valores)
