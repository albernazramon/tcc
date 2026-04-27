import os
import subprocess
import time
import shutil
from datetime import datetime

CONTAINER_NAME = "tpc-postgres"
DOCKER_COMPOSE_FILE = "docker-compose.tpc.yml"
PG_DATA_DIR = r"H:\tpc_pgdata"
BACKUP_PATH = "/tmp/tpc.backup"

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def run(cmd, shell=False, ignore_errors=False):
    try:
        return subprocess.run(cmd, shell=shell, check=not ignore_errors, capture_output=True, text=True)
    except subprocess.CalledProcessError:
        return None

def main():
    log("--- Iniciando Reorganização do Ambiente de Testes ---")

    # 1. Parar e remover o container
    log("Parando e removendo containers (docker-compose down)...")
    run(["docker", "compose", "-f", DOCKER_COMPOSE_FILE, "down", "-v"], ignore_errors=True)
    run(["docker", "rm", "-f", CONTAINER_NAME], ignore_errors=True)

    # 2. Deletar a pasta do volume
    if os.path.exists(PG_DATA_DIR):
        log(f"Deletando pasta do volume: {PG_DATA_DIR}...")
        time.sleep(1) # Pequena pausa para o SO liberar handles
        try:
            shutil.rmtree(PG_DATA_DIR)
        except:
            run(f'rmdir /s /q "{PG_DATA_DIR}"', shell=True, ignore_errors=True)
    
    # 3. Iniciar um novo container
    log("Iniciando novo container...")
    run(["docker", "compose", "-f", DOCKER_COMPOSE_FILE, "up", "-d"])

    # Aguardar o Postgres estar pronto
    log("Aguardando Postgres inicializar...")
    ready = False
    for _ in range(30):
        check = run(["docker", "exec", CONTAINER_NAME, "pg_isready", "-U", "postgres"])
        if check and check.returncode == 0:
            # Teste adicional de query
            test_query = run(["docker", "exec", CONTAINER_NAME, "psql", "-U", "postgres", "-c", "SELECT 1;"])
            if test_query and test_query.returncode == 0:
                ready = True
                break
        time.sleep(2)

    if not ready:
        log("ERRO: Postgres não ficou pronto a tempo.")
        return

    # 4. Restauração do backup
    log("Criando banco 'tpc' e iniciando restauração (pg_restore)...")
    run(["docker", "exec", CONTAINER_NAME, "psql", "-U", "postgres", "-c", "CREATE DATABASE tpc;"], ignore_errors=True)
    
    restore = run([
        "docker", "exec", "-u", "postgres", CONTAINER_NAME,
        "pg_restore", "-U", "postgres", "-d", "tpc", BACKUP_PATH
    ], ignore_errors=True)

    # Verificação simples
    check_db = run(["docker", "exec", CONTAINER_NAME, "psql", "-U", "postgres", "-d", "tpc", "-t", "-c", "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';"])
    
    if check_db and check_db.stdout.strip().isdigit() and int(check_db.stdout.strip()) > 0:
        log("SUCESSO: Ambiente reiniciado e backup restaurado com êxito!")
    else:
        log("AVISO: Processo concluído, mas a verificação do banco falhou ou retornou 0 tabelas.")

if __name__ == "__main__":
    main()
