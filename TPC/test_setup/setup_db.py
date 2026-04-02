import os
import subprocess
import time
import shutil
from datetime import datetime

# Configurações
CONTAINER_NAME = "tpc-postgres"
TEST_SETUP_CONTAINER = "test-setup"
DOCKER_COMPOSE_FILE = "docker-compose.tpc.yml"
PG_DATA_DIR = r"H:\tpc_pgdata"
BACKUP_PATH = "/tmp/tpc.backup"

def print_step(msg):
    print(f"\n[INFO] {datetime.now().strftime('%H:%M:%S')} - {msg}")

def run_command(cmd, shell=False, capture=False, ignore_errors=False):
    try:
        return subprocess.run(cmd, shell=shell, check=not ignore_errors, capture_output=capture, text=True)
    except subprocess.CalledProcessError as e:
        if not ignore_errors:
            print(f"[AVISO] Comando falhou: {e}")
        return None

def main():
    # 1. Matar o container test-setup (se existir)
    print_step(f"Tentando parar e remover o container {TEST_SETUP_CONTAINER}...")
    run_command(["docker", "rm", "-f", TEST_SETUP_CONTAINER], ignore_errors=True)

    # 2. Parar o banco atual para liberar a pasta
    print_step("Parando containers do docker-compose...")
    run_command(["docker", "compose", "-f", DOCKER_COMPOSE_FILE, "down", "-v"], ignore_errors=True)

    # 3. Deletar a pasta H:\tpc_pgdata
    if os.path.exists(PG_DATA_DIR):
        print_step(f"Tentando deletar a pasta {PG_DATA_DIR}...")
        # Dá um tempinho extra pro windows soltar a pasta
        time.sleep(2)
        try:
            shutil.rmtree(PG_DATA_DIR)
            print(f"[SUCESSO] Pasta {PG_DATA_DIR} removida.")
        except Exception as e:
            print(f"[AVISO] rmtree falhou ({e}), tentando forçar via shell...")
            run_command(f'rmdir /s /q "{PG_DATA_DIR}"', shell=True, ignore_errors=True)
    else:
        print_step(f"Pasta {PG_DATA_DIR} não existe, pulando deleção.")

    # 4. Iniciar o container
    print_step("Iniciando o container via docker-compose...")
    run_command(["docker", "compose", "-f", DOCKER_COMPOSE_FILE, "up", "-d"])

    # 5. Aguardar o Postgres estar PRONTO
    print_step("Aguardando o Postgres estar 100% pronto...")
    time.sleep(5)
    
    ready = False
    for i in range(20):
        # Usamos o banco 'postgres' padrão para checar
        check = run_command(["docker", "exec", CONTAINER_NAME, "pg_isready", "-U", "postgres"], capture=True, ignore_errors=True)
        if check and "accepting connections" in check.stdout:
            # Postgres aceita conexões, mas pode estar inicializando bancos de dados internos ainda
            # Vamos testar um comando psql simples no banco 'postgres'
            test_psql = run_command(["docker", "exec", CONTAINER_NAME, "psql", "-U", "postgres", "-c", "SELECT 1;"], capture=True, ignore_errors=True)
            if test_psql:
                ready = True
                break
        time.sleep(3)
        print(f"... aguardando inicialização do Postgres ({i+1}/20) ...")

    if not ready:
        print("[ERRO] Postgres não subiu adequadamente.")
        return

    # 6. Preparar Banco TPC e Restaurar
    print_step("Criando banco 'tpc' e iniciando RESTAURAÇÃO...")
    
    # Mata conexões se houver e dropa o banco se já existir (segurança extra)
    run_command(["docker", "exec", "-u", "postgres", CONTAINER_NAME, "psql", "-U", "postgres", "-c", "DROP DATABASE IF EXISTS tpc;"], ignore_errors=True)
    run_command(["docker", "exec", "-u", "postgres", CONTAINER_NAME, "psql", "-U", "postgres", "-c", "CREATE DATABASE tpc;"])

    print_step("Executando pg_restore...")
    restore_cmd = [
        "docker", "exec", "-u", "postgres", CONTAINER_NAME,
        "pg_restore", "-U", "postgres", "-d", "tpc", BACKUP_PATH
    ]
    
    # pg_restore pode retornar avisos irrelevantes, não matamos o script por isso
    run_command(restore_cmd, ignore_errors=True)

    # 7. Otimização Pós-Restore (Evitar Hint Bits na 1ª consulta)
    print_step("Executando VACUUM ANALYZE para otimizar tabelas e estatísticas...")
    run_command([
        "docker", "exec", CONTAINER_NAME,
        "psql", "-U", "postgres", "-d", "tpc", "-c", "VACUUM ANALYZE;"
    ], ignore_errors=True)

    # 8. Verificação Final
    print_step("Verificando tabelas restauradas...")
    check_tables = run_command([
        "docker", "exec", CONTAINER_NAME, 
        "psql", "-U", "postgres", "-d", "tpc", "-t", "-c", 
        "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public';"
    ], capture=True, ignore_errors=True)
    
    if check_tables:
        try:
            count = int(check_tables.stdout.strip())
            if count > 0:
                print_step(f"SUCESSO! {count} tabelas encontradas no banco 'tpc'.")
            else:
                print("[ERRO] Nenhuma tabela encontrada após restauração.")
        except Exception as e:
            print(f"[ERRO] Falha ao ler contagem de tabelas: {e}")
    else:
        print("[ERRO] Não foi possível conectar ao banco 'tpc' para verificar restauração.")

if __name__ == "__main__":
    main()
