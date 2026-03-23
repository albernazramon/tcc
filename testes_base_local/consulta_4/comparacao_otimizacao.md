# Comparação de Resultados: Consulta 4

## Queries Analisadas

### Pré-Otimização: Ordenação global de grande volume sem índice

**Problema:** Ordenar 4.4 milhões de registros por uma coluna não indexada causará um Sort em disco extremamente lento.

```sql
SELECT
    l_orderkey,
    l_partkey,
    l_shipdate
FROM
    public.lineitem
ORDER BY
    l_shipdate DESC
LIMIT 100;
```

### Pós-Otimização: Criação de índice

**Alterações:** A única alteração indicada é a criação de um índice, conforme indicado, sem nenhuma alteração sintática.

```sql
CREATE INDEX idx_lineitem_l_shipdate_desc ON public.lineitem (l_shipdate DESC);
```

---

## Comparação de Desempenho

| Métrica                    | Pré-Otimização | Pós-Otimização | Diferença / Impacto                   |
| :------------------------- | :------------- | :------------- | :------------------------------------ |
| **Tempo de Execução**      | 1387.505 ms    | 0.722 ms       | Redução considerável                  |
| **Custo Inicial Estimado** | 98714.98       | 0.43           | Redução drástica                      |
| **Custo Total Estimado**   | 98726.63       | 9.90           | Redução drástica                      |
| **Linhas**                 | 100            | 100            | -                                     |
| **Memória: Hit**           | 76             | 13             | Baixa necessidade de reaproveitamento |
| **Memória: Read**          | 84184          | 87             | Baixa leitura                         |
| **Memória: Dirtied**       | 84166          | -              | Sem necessidade de sujar a memória    |
| **Memória: Written**       | 66641          | -              | Sem necessidade de escrever           |
| **Temp Read**              | -              | -              | -                                     |
| **Temp Written**           | -              | -              | -                                     |

### Resultados da Consulta (Registros)

- **Pré-Otimização:** [resultado_pre_otimizacao](.\resultado_pre_otimizacao.csv)
- **Pós-Otimização:** [resultado_pos_otimizacao](.\resultado_pos_otimizacao.csv)
  \_(Os resultados divergem no conteúdo, porém a única ordenação da consulta é pelo campo l_shipdate, que estão todos repetidos, então isso não garante um resultado igual)
