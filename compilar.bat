@echo off
title Compilador - BACKUP DOS CLIENTES
color 0b
cls

echo =======================================================
echo    ASSISTENTE DE COMPILACAO - BACKUP DOS CLIENTES
echo =======================================================
echo.

:: Passo 1: Verificar se os ficheiros Python existem
echo [1/4] Verificando ficheiros fonte...
if not exist "backup_monitor.py" (
    color 0c
    echo ERRO: O ficheiro 'backup_monitor.py' nao foi encontrado!
    echo Certifica-te de que ele esta na mesma pasta que este script.
    pause
    exit
)
if not exist "service_installer.py" (
    color 0c
    echo ERRO: O ficheiro 'service_installer.py' nao foi encontrado!
    pause
    exit
)
echo OK: Ficheiros fonte encontrados.
echo.

:: Passo 2: Instalar dependencias
echo [2/4] Instalando/Atualizando bibliotecas necessarias...
pip install --upgrade pip
pip install pyinstaller wmi requests pywin32
if %errorlevel% neq 0 (
    color 0c
    echo.
    echo ERRO: Falha ao instalar dependencias. Verifica a tua ligacao a internet.
    pause
    exit
)
echo.

:: Passo 3: Compilacao
echo [3/4] Gerando executavel (service_installer.exe)...
echo Isto pode demorar um pouco, por favor aguarda...
echo.

:: Remove pastas antigas se existirem para evitar conflitos
if exist "dist" rd /s /q "dist"
if exist "build" rd /s /q "build"

pyinstaller --onefile --noconsole --hidden-import=win32timezone service_installer.py

if %errorlevel% neq 0 (
    color 0c
    echo.
    echo ERRO: Falha na compilacao. Verifica as mensagens acima.
    pause
    exit
)

:: Passo 4: Conclusao
cls
color 0a
echo =======================================================
echo    COMPILACAO CONCLUIDA COM SUCESSO!
echo =======================================================
echo.
echo O teu instalador 'service_installer.exe' ja esta pronto.
echo Caminho: %~dp0dist\service_installer.exe
echo.
echo DICA: Leva este ficheiro para o cliente e executa-o como Administrador.
echo.
pause
