import os
import re

def clean_sql(sql):
    # Remover public. para normalizar
    sql = sql.replace("public.", "")
    # Remover espaços extras e quebras de linha dentro do comando
    sql = re.sub(r'\s+', ' ', sql).strip()
    # Remover ponto e vírgula final para comparação
    if sql.endswith(';'):
        sql = sql[:-1]
    return sql

def get_target_object(sql):
    """
    Tenta extrair o que está sendo criado e onde.
    Ex: CREATE INDEX IF NOT EXISTS name ON table (cols) -> ('table', '(cols)')
    Ex: CREATE EXTENSION IF NOT EXISTS name -> ('EXTENSION', 'name')
    """
    sql_upper = sql.upper()
    
    if "CREATE EXTENSION" in sql_upper:
        match = re.search(r"CREATE EXTENSION IF NOT EXISTS (\w+)", sql, re.IGNORECASE)
        if match:
            return ("EXTENSION", match.group(1).lower())
        
    if "CREATE INDEX" in sql_upper:
        # Padrão: CREATE INDEX [IF NOT EXISTS] [name] ON [table] [USING method] (cols) [INCLUDE...] [WHERE...]
        # Vamos focar na tabela e nas colunas/condições, ignorando o nome do índice.
        match = re.search(r"ON\s+(\w+)\s+(.*)", sql, re.IGNORECASE)
        if match:
            table = match.group(1).lower()
            definition = match.group(2).lower().strip()
            return (table, definition)
            
    return None

def deduplicate_script():
    input_file = "tcc/TPC/script_otimizacao_geral.sql"
    output_file = "tcc/TPC/script_otimizacao_geral.sql" # Sobrescrever
    
    if not os.path.exists(input_file):
        print("Arquivo não encontrado.")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        lines = f.readlines()

    new_lines = []
    seen_targets = set()
    current_scenario = ""
    
    # Buffer para o comando SQL atual (pode ocupar várias linhas)
    sql_buffer = []
    
    def flush_buffer():
        nonlocal sql_buffer, current_scenario
        if not sql_buffer:
            return
        
        full_sql = "".join(sql_buffer).strip()
        cleaned = clean_sql(full_sql)
        target = get_target_object(cleaned)
        
        if target:
            if target not in seen_targets:
                seen_targets.add(target)
                if current_scenario:
                    new_lines.append(f"\n{current_scenario}")
                    current_scenario = ""
                new_lines.append(full_sql + ("\n" if full_sql.endswith(";") else ";\n"))
            else:
                # Duplicado encontrado
                # print(f"Removendo duplicata: {target}")
                pass
        else:
            # Não é um comando de criação reconhecido, manter se não for vazio
            if full_sql:
                if current_scenario:
                    new_lines.append(f"\n{current_scenario}")
                    current_scenario = ""
                new_lines.append(full_sql + "\n")
        
        sql_buffer = []

    for line in lines:
        stripped = line.strip()
        
        if stripped.startswith("--"):
            # Se for um cabeçalho de cenário, guardar para imprimir apenas se houver comando novo
            if "Cenario" in stripped:
                flush_buffer()
                current_scenario = line
            else:
                # Comentários gerais (como o do topo) manter
                flush_buffer()
                new_lines.append(line)
            continue
            
        if not stripped:
            flush_buffer()
            continue
            
        sql_buffer.append(line)
        if stripped.endswith(";"):
            flush_buffer()

    flush_buffer()

    with open(output_file, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    print(f"Deduplicação concluída. Arquivo atualizado: {output_file}")

if __name__ == "__main__":
    deduplicate_script()
