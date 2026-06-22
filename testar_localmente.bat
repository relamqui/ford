@echo off
title WP CRM - Teste Local
echo ============================================
echo      WP CRM Server - Iniciando Localmente
echo ============================================
echo.
echo Forcando uso de SQLite local (ignora o Postgres do .env)
echo.

:: Forca o uso do SQLite local sobrepondo o .env
set DATABASE_URL=sqlite_local

:: Navegar para a pasta do script
cd /d "%~dp0"

:: Verificar se o Python esta instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao foi encontrado no PATH.
    echo Instale o Python em https://www.python.org/downloads/
    pause
    exit /b 1
)

:: Instalar todas as dependencias do requirements.txt
echo [1/2] Instalando dependencias...
pip install -r requirements.txt >nul
if %errorlevel% neq 0 (
    echo [AVISO] Houve um problema ao instalar dependencias.
    pause
    exit /b 1
)

echo.
echo [2/2] Iniciando servidor...
echo Acesse: http://localhost:3008 (A porta padrao e 3008)
echo Pressione Ctrl+C para encerrar.
echo.

python app.py
pause
