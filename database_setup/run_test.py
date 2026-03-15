import sys
import os
import subprocess
import time
from datetime import datetime

CONTAINER_NAME = "tcc-postgres-retails"
DB_USER = "postgres"
DB_NAME = "retails"

def print_step(msg):
    print(f"\n---> {msg}")

def restart_database():
    print_step("Reiniciando o banco de dados para garantir ambiente limpo...")
    
    subprocess.run(["docker", "compose", "down", "-v"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    subprocess.run(["docker", "compose", "up", "-d"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def wait_for_database():
    print_step("Aguardando inicialização do PostgreSQL...")
    
    time.sleep(5)
    
    max_retries = 10
    for i in range(max_retries):
        try:
            log_result = subprocess.run(
                ["docker", "logs", "--tail", "20", CONTAINER_NAME],
                capture_output=True, text=True, errors="ignore"
            )
          
            if "database system is ready to accept connections" in log_result.stdout or "database system is ready to accept connections" in log_result.stderr:
                if "PostgreSQL init process complete" in log_result.stdout or "PostgreSQL init process complete" in log_result.stderr:
                    print("[SUCESSO] Banco de dados pronto para uso!")
                    return True
            
            print(f"... restauração em andamento (tentativa {i+1}/{max_retries})...")
                
        except Exception as e:
            print(f"ERRO: {e}")
            
        time.sleep(5)
        
    print("[ERRO] A restauração do banco demorou demais!")
    return False

def run_query_and_collect(query_text, results_dir):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_filename = os.path.join(results_dir, f"resultado_{timestamp}")
    metrics_file = f"{base_filename}.txt"
    csv_file = f"{base_filename}.csv"

    clean_query = query_text.strip()
    if clean_query.endswith(';'):
        clean_query = clean_query[:-1]

    # 1. Coletando métricas (EXPLAIN ANALYZE BUFFERS)
    print_step(f"Executando EXPLAIN ANALYZE BUFFERS para coletar métricas de performance...")
    explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) {clean_query};"
    
    with open(metrics_file, "w", encoding="utf-8") as f:
        subprocess.run(
            ["docker", "exec", "-i", CONTAINER_NAME, "psql", "-U", DB_USER, "-d", DB_NAME],
            input=explain_query.encode("utf-8"),
            stdout=f,
            stderr=subprocess.STDOUT
        )
        
    # 2. Coletar resultados reais em CSV
    print_step(f"Executando query e exportando registros em formato CSV...")
    csv_query = f"\\pset format csv\n{clean_query};"
    
    with open(csv_file, "w", encoding="utf-8") as f:
        subprocess.run(
            ["docker", "exec", "-i", CONTAINER_NAME, "psql", "-U", DB_USER, "-d", DB_NAME],
            input=csv_query.encode("utf-8"),
            stdout=f,
            stderr=subprocess.STDOUT
        )
    
    print("SUCESSO!")
    print(f"  Metricas salvas em: {metrics_file}")
    print(f"  Resultados salvos em: {csv_file}")
    
def main():
    if len(sys.argv) < 2:
        print("Uso: python run_test.py <query_ou_arquivo.sql>")
        print("Exemplo 1: python run_test.py \"SELECT * FROM minha_tabela;\"")
        print("Exemplo 2: python run_test.py meu_script.sql")
        sys.exit(1)
        
    arg = sys.argv[1]
    
    # Verifica se eh um arquivo sql
    if os.path.isfile(arg):
        with open(arg, "r", encoding="utf-8") as file:
            query_text = file.read()
    else:
        query_text = arg
        
    results_dir = "resultados"
    if not os.path.exists(results_dir):
        os.makedirs(results_dir)
        
    restart_database()
    
    if wait_for_database():
        run_query_and_collect(query_text, results_dir)

if __name__ == "__main__":
    main()
