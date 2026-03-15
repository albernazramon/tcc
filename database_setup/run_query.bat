@echo off
setlocal

if "%~1"=="" (
    echo.
    echo Uso: %0 ^<arquivo_sql_ou_query_em_string^>
    echo Exemplo 1: %0 meuscript.sql
    echo Exemplo 2: %0 "SELECT count(*) FROM minha_tabela;"
    echo.
    exit /b 1
)

if exist "%~1" (
    echo.
    echo --- Executando arquivo SQL: %~1 ---
    docker exec -i tcc-postgres-retails psql -U postgres -d retails < "%~1"
) else (
    echo.
    echo --- Executando a instrucao SQL ---
    docker exec -t tcc-postgres-retails psql -U postgres -d retails -c "%~1"
)

echo.
echo --- Execucao finalizada ---
endlocal
