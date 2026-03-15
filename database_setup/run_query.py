import sys
import os
import subprocess

CONTAINER_NAME = "tcc-postgres-retails"
DB_USER = "postgres"
DB_NAME = "retails"

def main():
    if len(sys.argv) < 2:
        print("\nUso: python run_query.py <arquivo_sql_ou_query_em_string>")
        print('Exemplo 1: python run_query.py meuscript.sql')
        print('Exemplo 2: python run_query.py "CREATE INDEX idx_1 ON tabela(coluna);" \n')
        sys.exit(1)
        
    query_arg = sys.argv[1]
    
    if os.path.isfile(query_arg):
        print(f"\n--- Executando arquivo SQL: {query_arg} ---")
        
        with open(query_arg, "r", encoding="utf-8") as file:
            query_text = file.read()
            
        subprocess.run(
            ["docker", "exec", "-i", CONTAINER_NAME, "psql", "-U", DB_USER, "-d", DB_NAME],
            input=query_text.encode("utf-8")
        )
    else:
        print("\n--- Executando a instrucao SQL ---")
        subprocess.run(
            ["docker", "exec", "-t", CONTAINER_NAME, "psql", "-U", DB_USER, "-d", DB_NAME, "-c", query_arg]
        )

    print("\n--- Execucao finalizada ---")

if __name__ == "__main__":
    main()
