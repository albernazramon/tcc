import argparse
import os
import subprocess
import time
import sys
from datetime import datetime

# Configurações
CONTAINER_NAME = "tpc-postgres"
DB_USER = "postgres"
DB_NAME = "tpc"
DOCKER_COMPOSE_FILE = "docker-compose.tpc.yml"
QUERY_TIMEOUT = 1200 # 20 minutos em segundos

def print_step(msg):
    print(f"\n[INFO] {datetime.now().strftime('%H:%M:%S')} - {msg}")

def run_command(cmd, capture=False):
    try:
        result = subprocess.run(cmd, capture_output=capture, text=True, check=True)
        return result
    except subprocess.CalledProcessError as e:
        print(f"[ERRO] Falha ao executar comando: {' '.join(cmd)}")
        if capture:
            print(f"[ERRO] Detalhes: {e.stderr}")
        return None

def ensure_database_ready():
    # Garante que o diretório de trabalho seja o do script para encontrar o docker-compose
    script_dir = os.path.dirname(os.path.abspath(__file__))
    run_command(["docker", "compose", "-f", os.path.join(script_dir, DOCKER_COMPOSE_FILE), "up", "-d"])
    
    ready = False
    for i in range(30):
        status = run_command(["docker", "inspect", "--format", "{{.State.Status}}", CONTAINER_NAME], capture=True)
        if status and status.stdout.strip() == "running":
            # Tenta ler o health status, mas não falha se não existir (ex: container sem healthcheck definido)
            health = run_command(["docker", "inspect", "--format", "{{if .State.Health}}{{.State.Health.Status}}{{else}}healthy{{end}}", CONTAINER_NAME], capture=True)
            if health and health.stdout.strip() == "healthy":
                ready = True
                break
        time.sleep(2)
    
    if not ready:
        print("[ERRO] O banco de dados não está pronto ou saudável. Execute setup_db.py primeiro!")
        sys.exit(1)

def clear_all_caches():
    """
    Limpa de forma agressiva todos os caches possíveis:
    1. OS CACHE (WSL2): Limpa o Page Cache do kernel Linux no WSL2.
    2. RESTART: Reinicia o container para limpar Shared Buffers da memória RAM.
    """
    print_step("Iniciando limpeza agressiva de cache...")

    # 1. Limpar Page Cache do WSL2 (O mais importante para Cold Start no Windows)
    # Isso limpa o cache de arquivos que o Windows/WSL2 mantém na RAM
    print("- Limpando Page Cache do WSL2 (Kernel)...")
    run_command(["wsl", "-u", "root", "sh", "-c", "echo 3 > /proc/sys/vm/drop_caches"])
    
    # 2. Restart do Container (Limpeza de RAM/Shared Buffers)
    print("- Reiniciando container para limpar Shared Buffers (RAM)...")
    run_command(["docker", "restart", CONTAINER_NAME])
    
    # Aguarda o postgres estar pronto novamente
    ready = False
    for _ in range(60):
        status = run_command(["docker", "inspect", "--format", "{{.State.Status}}", CONTAINER_NAME], capture=True)
        if status and status.stdout.strip() == "running":
            # Tenta ler o health status, mas não falha se não existir (ex: container sem healthcheck definido)
            health = run_command(["docker", "inspect", "--format", "{{if .State.Health}}{{.State.Health.Status}}{{else}}healthy{{end}}", CONTAINER_NAME], capture=True)
            if health and health.stdout.strip() == "healthy":
                ready = True
                break
        time.sleep(2)
    
    if not ready:
        print("[AVISO] O banco demorou a responder após o restart, aguardando mais 10s...")
        time.sleep(10)
    
    print("- Limpeza concluída com sucesso.")

def execute_sql_file(file_path, scenario_num, query_name, is_pre_script=False):
    if not os.path.exists(file_path):
        print(f"[ERRO] Arquivo não encontrado: {file_path}")
        return False

    with open(file_path, "r", encoding="utf-8") as f:
        query_content = f.read().strip()

    if not query_content:
        print(f"[ERRO] Arquivo vazio: {file_path}")
        return False

    if is_pre_script:
        print_step(f"Executando script pré-consulta: {file_path}")
        cmd = ["docker", "exec", "-i", CONTAINER_NAME, "psql", "-U", DB_USER, "-d", DB_NAME]
        subprocess.run(cmd, input=query_content.encode("utf-8"), check=True)
        return True

    # Padrão de nomes
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_scenario_dir = os.path.join(base_dir, f"cenario_{scenario_num}")
    res_csv = os.path.join(target_scenario_dir, f"resultados_{query_name}.csv")
    res_txt = os.path.join(target_scenario_dir, f"resultados_{query_name}.txt")

    # Verifica se já existe
    if os.path.exists(res_csv) or os.path.exists(res_txt):
        print(f"[ERRO] Já existem resultados para '{query_name}' no cenario {scenario_num}. Abortando para não sobrescrever.")
        return False

    print_step(f"Executando consulta: {query_name} (Cenário {scenario_num})")

    # 0. Limpar cache (NATIVO E OBRIGATÓRIO)
    clear_all_caches()

    # 1. EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
    sql_statements = [s.strip() for s in query_content.split(';') if s.strip()]
    

    if len(sql_statements) > 1:

        main_query = next((s for s in sql_statements if s.lower().startswith('select')), sql_statements[0])
        pre_statements = "\n".join([s + ";" for s in sql_statements if s != main_query and sql_statements.index(s) < sql_statements.index(main_query)])
        post_statements = "\n".join([s + ";" for s in sql_statements if s != main_query and sql_statements.index(s) > sql_statements.index(main_query)])
        
        explain_query = f"{pre_statements}\nEXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) {main_query};\n{post_statements}"
    else:
        explain_query = f"EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) {query_content.rstrip(';')};"
    
    try:
        process = subprocess.Popen(
            ["docker", "exec", "-i", CONTAINER_NAME, "psql", "-U", DB_USER, "-d", DB_NAME],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        try:
            stdout, stderr = process.communicate(input=explain_query.encode("utf-8"), timeout=QUERY_TIMEOUT)
            
            if process.returncode == 0:
                with open(res_txt, "w", encoding="utf-8") as f:
                    f.write(stdout.decode("utf-8"))
                print(f"[SUCESSO] Explain salvo em {res_txt}")
            else:
                print(f"[ERRO] Falha na execução da query: {stderr.decode('utf-8')}")
                return False
                
        except subprocess.TimeoutExpired:
            process.kill()
            print(f"[AVISO] Tempo limite de 20 min excedido para {query_name}")
            with open(res_txt, "w", encoding="utf-8") as f:
                f.write(f"Tempo limite excedido. Não foi possível executar a consulta: {query_content}")
            return False

        # 2. Resultados em CSV
        print_step(f"Exportando resultados para CSV...")
        csv_cmd = f"\\pset format csv\n{query_content.rstrip(';')};"
        
        process_csv = subprocess.Popen(
            ["docker", "exec", "-i", CONTAINER_NAME, "psql", "-U", DB_USER, "-d", DB_NAME],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        try:
            stdout_csv, stderr_csv = process_csv.communicate(input=csv_cmd.encode("utf-8"), timeout=QUERY_TIMEOUT)
            if process_csv.returncode == 0:
                with open(res_csv, "w", encoding="utf-8") as f:
                    f.write(stdout_csv.decode("utf-8"))
                print(f"[SUCESSO] CSV salvo em {res_csv}")
            else:
                print(f"[ERRO] Falha ao gerar CSV: {stderr_csv.decode('utf-8')}")
        except subprocess.TimeoutExpired:
            process_csv.kill()
            print(f"[AVISO] Tempo limite de 20 min excedido ao gerar CSV")

    except Exception as e:
        print(f"[ERRO] Inesperado: {e}")
        return False

    return True

def main():
    parser = argparse.ArgumentParser(description="Execução de testes TPC")
    parser.add_argument("--cenario", type=int, required=True, help="Número do cenário (1-22)")
    parser.add_argument("--query", type=str, required=True, help="Nome do arquivo sql (sem o .sql)")
    parser.add_argument("--pre", type=str, help="Caminho para script SQL a ser executado antes da consulta (opcional)")

    args = parser.parse_args()

    ensure_database_ready()

    # Script prévio
    if args.pre:
        execute_sql_file(args.pre, args.cenario, "", is_pre_script=True)

    # Consulta principal
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sql_file = os.path.join(base_dir, f"cenario_{args.cenario}", f"{args.query}.sql")
    execute_sql_file(sql_file, args.cenario, args.query)

if __name__ == "__main__":
    main()
