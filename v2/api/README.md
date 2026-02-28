# API de Otimização de Consultas SQL

Esta API permite otimizar consultas SQL, sugerindo melhorias com base no esquema do banco de dados e informações adicionais.

## Testando a API com o Swagger

**Swagger UI** (OpenAPI) disponível em:  
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Exemplo de payload para o endpoint `/optimize`:

```json
{
  "query": "SELECT * FROM orders WHERE o_orderstatus = 'O' AND o_orderdate > '2024-01-01';",
  "schemas": "CREATE TABLE orders ( o_orderkey INTEGER PRIMARY KEY, o_custkey INTEGER, o_orderstatus CHAR(1), o_totalprice DECIMAL, o_orderdate DATE );",
  "additional_info": "A tabela 'orders' possui 10 milhões de registros e não possui índices além da chave primária."
}
```
