@echo off
echo Instalando dependencias...
pip install pyinstaller wmi requests pywin32
echo.
echo Compilando service_installer.py...
pyinstaller --onefile --hidden-import=win32timezone service_installer.py
echo.
echo Pronto! O arquivo service_installer.exe esta na pasta 'dist'.
pause
