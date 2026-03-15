#!/bin/bash
set -e

if [ -f "/tmp/banco_postgres_original.sql" ]; then
    ls -lh /tmp/banco_postgres_original.sql

    pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --no-owner --no-privileges -1 /tmp/banco_postgres_original.sql || {
        echo "[ERRO] Ocorreu uma falha no pg_restore!"
        exit 1
    }
    
    echo "RESTAURACAO CONCLUIDA COM SUCESSO!"
else
    echo "[ERRO] O ARQUIVO DE BACKUP NAO FOI MAPEADO CORRETAMENTE PELO DOCKER!"
    exit 1
fi
