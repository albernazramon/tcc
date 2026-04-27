import os
import re

def consolidate_scripts():
    base_dir = "tcc/TPC"
    output_file = os.path.join(base_dir, "script_otimizacao_geral.sql")
    
    # Encontrar todas as pastas de cenário
    scenarios = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and d.startswith("cenario_")]
    
    # Ordenar numericamente os cenários
    scenarios.sort(key=lambda x: int(x.split("_")[1]))
    
    with open(output_file, "w", encoding="utf-8") as outfile:
        outfile.write("-- SCRIPT DE OTIMIZACAO GERAL --\n\n")
        
        for scenario in scenarios:
            script_path = os.path.join(base_dir, scenario, "script_otimizacao.sql")
            
            if os.path.exists(script_path):
                outfile.write(f"-- {scenario.replace('_', ' ').capitalize()} --\n")
                
                with open(script_path, "r", encoding="utf-8") as infile:
                    content = infile.read()
                    
                    # Remover comentários de linha (-- ...)
                    content = re.sub(r'--.*', '', content)
                    
                    # Remover comentários de bloco (/* ... */)
                    content = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
                    
                    # Limpar linhas vazias excessivas
                    lines = [line.strip() for line in content.splitlines() if line.strip()]
                    
                    if lines:
                        outfile.write("\n".join(lines))
                        outfile.write("\n\n")
                    else:
                        outfile.write("-- (Sem scripts de otimização neste cenário)\n\n")
            else:
                # Opcional: registrar que o arquivo não existe
                pass

    print(f"Arquivo gerado com sucesso em: {output_file}")

if __name__ == "__main__":
    consolidate_scripts()
