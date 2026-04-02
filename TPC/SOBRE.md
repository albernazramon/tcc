## TPC-H

TPC-H é uma ferramenta de benchmarking que cria um banco de dados e consultas complexas para avaliação de performance.
Estou utilizando para gerar o banco e as consultas para testes da ferramenta do TCC.

### Executando o TPC

No site do TPC é possível fazer um breve cadastro que disponibiliza um zip contendo a ferramenta.
Para executar foram necessários alguns ajustes, como:

- Instalação do chocolatey
- Instalação do make
- Cópia de um arquivo makefile do TCP, alterando alguns parâmetros como banco de dados desejados, compiladores e etc
- Alteração no script original para remover caracteres especiais, para poder restaurar os dados no postgres

Ao executar o makefile (comando make), são gerados dois arquivos:

- dbgen: Executável que gera um banco de dados de acordo com o tamanho desejado (parâmetro s recebe um número que representa os GBs resultantes)
- qgen: Gera as consultas com base no banco de dados

### Banco de dados

Para geração de um banco de dados Postgres, foram executadas algumas etapas:

- Criado um banco de dados no PGadmin vazio.
- Criação das tabelas com o script disponibilizado na pasta do TPC (dss.dll).
- Geração de um banco de dados SQL server com 20Gb de dados utilizando o comando (dbgen.exe -s 20).
  - O TPC não fornece banco de dados postgreSQL nativamente.
  - O dbgen gera as tabelas e os dados, sendo que os dados de cada tabela ficam disponíveis em arquivos isolados. Ex.: region.tbl
- Cópia dos dados gerados nos arquivos .tbl para as tabelas no postgreSQL com o comando COPY.
- Geração de um backup para reutilização com Docker no projeto.

#### Importante

- As tabelas são geradas sem FK's ou outros objetos, contendo apenas os dados e schema, o que facilita não só a conversão para postgreSQL, como os testes de performance.

- Devido ao tamanho das tabelas, os conteúdos e backup estão não estão versionados nesse projeto.

- Para os testes ficou inviável ficar recriando o banco de dados com Docker, visto que o banco possui mais de 20Gb de dados. Então para otimizar a execução dos testes sem perder a premissa de não utilizar cache nos testes das consultas, foi utilizada a extensão pg_drop_caches.

### Geração das consultas

As consultas foram geradas com o arquivo qgen.exe disponibilizado pelo TPC.

## As consultas estão disponível em: [queries](./queries)

### Comando de cópia das tabelas

```sql
COPY customer FROM 'H:\TCC\TPC-H V3.0.1\dbgen\customer.tbl' WITH (FORMAT csv, DELIMITER '|');
COPY lineitem FROM 'H:\TCC\TPC-H V3.0.1\dbgen\lineitem.tbl' WITH (FORMAT csv, DELIMITER '|');
COPY nation FROM 'H:\TCC\TPC-H V3.0.1\dbgen\nation.tbl' WITH (FORMAT csv, DELIMITER '|');
COPY orders FROM 'H:\TCC\TPC-H V3.0.1\dbgen\orders.tbl' WITH (FORMAT csv, DELIMITER '|');
COPY part FROM 'H:\TCC\TPC-H V3.0.1\dbgen\part.tbl' WITH (FORMAT csv, DELIMITER '|');
COPY partsupp FROM 'H:\TCC\TPC-H V3.0.1\dbgen\partsupp.tbl' WITH (FORMAT csv, DELIMITER '|');
COPY region FROM 'H:\TCC\TPC-H V3.0.1\dbgen\region.tbl' WITH (FORMAT csv, DELIMITER '|');
COPY supplier FROM 'H:\TCC\TPC-H V3.0.1\dbgen\supplier.tbl' WITH (FORMAT csv, DELIMITER '|');
```
