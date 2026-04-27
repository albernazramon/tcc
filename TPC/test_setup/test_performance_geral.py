import subprocess
import os
import sys
from datetime import datetime

# Configurações de caminhos baseados na localização deste script (tcc/TPC/test_setup/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # tcc/TPC
GENERAL_SCRIPT = os.path.join(BASE_DIR, "script_otimizacao_geral.sql")
TEST_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "run_tpc_test.py")

CONTAINER_NAME = "tpc-postgres"
DB_USER = "postgres"
DB_NAME = "tpc"
SCENARIOS = [1, 5, 10, 15, 20]

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def run_command(cmd, input_data=None):
    try:
        if input_data:
            return subprocess.run(cmd, input=input_data.encode("utf-8"), check=True, capture_output=True)
        else:
            return subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        log(f"ERRO ao executar: {' '.join(cmd)}")
        if e.stderr:
            print(e.stderr.decode("utf-8"))
        return None

def main():
    log("--- Iniciando Teste de Performance com Script Geral ---")

    # 1. Executar o script geral
    if not os.path.exists(GENERAL_SCRIPT):
        log(f"ERRO: Script geral não encontrado em {GENERAL_SCRIPT}")
        # DEBUG: mostrar onde estamos procurando
        log(f"CWD: {os.getcwd()}")
        log(f"Procurando em: {os.path.abspath(GENERAL_SCRIPT)}")
        return

    log(f"Aplicando script de otimização geral no banco '{DB_NAME}'...")
    with open(GENERAL_SCRIPT, "r", encoding="utf-8") as f:
        sql_content = f.read()
    
    # Executa via psql no container
    res = run_command(["docker", "exec", "-i", CONTAINER_NAME, "psql", "-U", DB_USER, "-d", DB_NAME], input_data=sql_content)
    
    if res:
        log("Script geral aplicado com sucesso.")
    else:
        log("Falha ao aplicar script geral. Verifique se o banco e o container estão ativos.")
        return

    # 2. Executar run_tpc_test para os cenários selecionados
    log(f"Iniciando testes para os cenários: {SCENARIOS}")
    
    for scenario in SCENARIOS:
        log(f">>> Testando Cenário {scenario}...")
        
        test_cmd = [
            sys.executable, TEST_SCRIPT, 
            "--cenario", str(scenario), 
            "--query", "consulta_otimizada"
        ]
        
        try:
            # Executar diretamente para ver o output no terminal
            subprocess.run(test_cmd, check=True)
            log(f"Cenário {scenario} concluído.")
        except subprocess.CalledProcessError:
            log(f"ERRO: Falha ao executar teste para o cenário {scenario}.")

    log("--- Processo de teste finalizado ---")

if __name__ == "__main__":
    main()
