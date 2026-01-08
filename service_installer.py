
# -*- coding: utf-8 -*-
import win32serviceutil
import win32service
import win32event
import servicemanager
import sys
import os
import json

# Tenta importar as funcoes da logica
try:
    from backup_monitor import main_task, setup_logging, CHECK_INTERVAL_SECONDS
except ImportError:
    pass

BASE_DIR = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, 'frozen', False) else __file__))
CONFIG_FILE = os.path.join(BASE_DIR, "monitor_config.json")

def prompt_for_config():
    """Solicita o caminho da pasta de backup no momento da instalacao"""
    print(f"\n--- Instalacao do Monitor de Backup ---")
    backup_dir = input("Digite o caminho da pasta de backup: ").strip().replace('"', '')
    if os.path.isdir(backup_dir):
        with open(CONFIG_FILE, 'w') as f:
            json.dump({"BACKUP_DIR": backup_dir}, f, indent=4)
        print("Configuracao salva com sucesso!")
        return True
    else:
        print("ERRO: O caminho informado nao e uma pasta valida.")
        return False

class BackupMonitorService(win32serviceutil.ServiceFramework):
    _svc_name_ = "PythonBackupMonitor"
    _svc_display_name_ = "Servico de Monitoramento de Backup"
    _svc_description_ = "Verifica backups locais e reporta ao painel central."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_running = True

    def SvcStop(self):
        self.is_running = False
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        setup_logging()
        while self.is_running:
            try:
                main_task()
            except:
                pass
            # Aguarda o intervalo ou sinal de parada
            if win32event.WaitForSingleObject(self.hWaitStop, CHECK_INTERVAL_SECONDS * 1000) == win32event.WAIT_OBJECT_0:
                break

if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1].lower() == 'install':
        if not prompt_for_config():
            sys.exit(1)
            
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(BackupMonitorService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        win32serviceutil.HandleCommandLine(BackupMonitorService)
