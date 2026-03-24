# Comparação de Resultados: Consulta 5

## Queries Analisadas

### Pré-Otimização: Filtro LIKE com wildcard no início

**Problema:** O uso de `%` no início da string de busca impossibilita o uso de índices padrão, forçando a leitura de toda a tabela `supplier`.

```sql
SELECT
    s_name,
    s_address
FROM
    public.supplier
WHERE
    s_comment LIKE '%special packages%';
```

### Pós-Otimização: Criação de índice e instalação de extensão

**Alterações:** A consulta se manteve inalterada, porém além de criar índices, o modelo sugeriu a instalação da extensão pg_trgm, que permite a criação de melhores indexações de strings. Na consulta temos a utilização do padrão %pattern%

```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX trgm_supplier_s_comment_idx ON public.supplier USING GIN (s_comment gin_trgm_ops);
```

---

## Comparação de Desempenho

| Métrica                    | Pré-Otimização | Pós-Otimização | Diferença / Impacto |
| :------------------------- | :------------- | :------------- | :------------------ |
| **Tempo de Execução**      | 5.082 ms       | 1.233 ms       | Boa redução         |
| **Custo Inicial Estimado** | 0.00           | 129.74         | -                   |
| **Custo Total Estimado**   | 239.20         | 133.75         | -                   |
| **Linhas**                 | 1              | 1              | -                   |
| **Memória: Hit**           | -              | 204            | -                   |
| **Memória: Read**          | 208            | -              | -                   |
| **Memória: Dirtied**       | 205            | -              | -                   |
| **Memória: Written**       | -              | -              | -                   |
| **Temp Read**              | -              | -              | -                   |
| **Temp Written**           | -              | -              | -                   |

### Resultados da Consulta (Registros)

- **Pré-Otimização:** [resultado_pre_otimizacao](.\resultado_pre_otimizacao.csv)
- **Pós-Otimização:** [resultado_pos_otimizacao](.\resultado_pos_otimizacao.csv)
  \_(Resultados semelhantes)
