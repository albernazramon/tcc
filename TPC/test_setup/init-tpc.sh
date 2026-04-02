#!/bin/bash
set -e

echo "[INFO] INICIANDO RESTAURACAO DO BANCO TPC"

echo "[INFO] Restaurando tabelas e dados..."
pg_restore -U postgres -d tpc /tmp/tpc.backup || echo "[AVISO] pg_restore retornou alguns avisos, mas continuando..."

echo "[SUCESSO] RESTAURACAO TPC CONCLUIDA COM SUCESSO!"
