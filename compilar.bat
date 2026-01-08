
@echo off
echo ==============================================
echo    Compilando Servico de Monitoramento
echo ==============================================
echo.
echo Instalando dependencias necessarias...
pip install pyinstaller wmi requests pywin32
echo.
echo Gerando executavel service_installer.exe...
pyinstaller --onefile --hidden-import=win32timezone service_installer.py
echo.
echo Concluido! O arquivo esta na pasta 'dist'.
pause
