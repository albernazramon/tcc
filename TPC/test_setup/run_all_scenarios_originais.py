import subprocess
import time
import sys
import os
from datetime import datetime

def print_step(msg):
    print(f"\n{'='*60}")
    print(f"[BATCH] {datetime.now().strftime('%H:%M:%S')} - {msg}")
    print(f"{'='*60}")

def run_all_scenarios():
    start_time_all = time.time()
    
    # 1. Executar o setup_db.py
    print_step("Iniciando Setup do Banco de Dados (Restore e VACUUM)...")
    try:
        subprocess.run(["python", "setup_db.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"[ERRO CRÍTICO] Falha no setup_db.py: {e}")
        sys.exit(1)
    
    # 2. Executar o run_tpc_test em loop para os 22 cenários
    for i in range(1, 23):
        print_step(f"EXECUTANDO CENÁRIO {i} de 22")
        
        # O script run_tpc_test.py já cuida de:
        # - Limpar Page Cache do WSL2 (Cold Start)
        # - Reiniciar o container (Limpar Shared Buffers)
        # - Executar a query original
        # - Salvar os resultados em .txt e .csv
        cmd = [
            "python", "run_tpc_test.py",
            "--cenario", str(i),
            "--query", "consulta_original"
        ]
        
        try:
            # check=False para não interromper o batch se uma query falhar (timeout ou erro de sintaxe)
            result = subprocess.run(cmd, check=False)
            if result.returncode != 0:
                print(f"[AVISO] O cenário {i} retornou erro. Continuando para o próximo...")
        except Exception as e:
            print(f"[ERRO] Falha ao tentar executar o cenário {i}: {e}")

    # Finalização
    print_step("Bateria de testes concluída. Desligando container...")
    subprocess.run(["docker", "compose", "-f", "docker-compose.tpc.yml", "down"])
    
    end_time_all = time.time()
    duration = (end_time_all - start_time_all) / 60
    print_step(f"PROCESSO COMPLETO FINALIZADO EM {duration:.2f} MINUTOS")

if __name__ == "__main__":
    print("Iniciando execução automática de todos os 22 cenários TPC...")
    
    try:
        run_all_scenarios()
    except KeyboardInterrupt:
        print("\n[STOP] Execução interrompida pelo usuário.")
        sys.exit(0)
